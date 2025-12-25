"""
Claude-Powered Preference Generation
=====================================
Uses Claude API to generate high-quality synthetic preference pairs
for DPO training across Zuup domains.

Prerequisites:
    pip install anthropic
    export ANTHROPIC_API_KEY=your-key

Usage:
    python scripts/generate_preferences_claude.py --domain procurement --count 10
    python scripts/generate_preferences_claude.py --all-priority --count 20
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("[WARNING] anthropic not installed. Run: pip install anthropic")

from scripts.zuup_sdk import ZuupPreferenceClient
from domains.taxonomy import DOMAINS, get_domain

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ZUUP_API_KEY = os.getenv("ZUUP_API_KEY", "")
MODEL = "claude-sonnet-4-20250514"

# Domain-specific generation prompts
DOMAIN_PROMPTS = {
    "procurement": """You are an expert in U.S. federal government contracting with deep knowledge of:
- FAR (Federal Acquisition Regulation) and DFARS
- RFP analysis and proposal writing
- Contract types (FFP, CPFF, T&M, IDIQ)
- Small business programs (8(a), HUBZone, SDVOSB, WOSB)
- DCAA compliance and cost accounting
- Source selection and evaluation criteria

Generate realistic procurement questions that professionals would ask.""",

    "defense_wm": """You are an expert in defense-related world modeling and geospatial intelligence:
- 3D scene reconstruction (photogrammetry, NeRF, 3DGS)
- ISR (Intelligence, Surveillance, Reconnaissance) analysis
- Geospatial intelligence and terrain analysis
- Sensor fusion (EO, IR, SAR, LiDAR)
- Simulation and digital twins for defense
- Computer vision for defense applications

Generate realistic technical questions that defense analysts and engineers would ask.""",

    "halal": """You are an expert in halal food certification and compliance:
- Islamic dietary laws (fiqh al-at'ima)
- Halal certification bodies (JAKIM, MUI, IFANCA, ISWA)
- Ingredient analysis (E-numbers, animal derivatives, alcohol)
- Supply chain traceability and verification
- Cross-contamination prevention
- Audit and documentation requirements

Generate realistic questions that halal compliance officers would ask.""",
}

GENERATION_TEMPLATE = """Generate a preference pair for training an AI assistant on {domain} topics.

REQUIREMENTS:
1. Create a realistic question that a professional would ask
2. Generate TWO responses:
   - Response A: Expert-quality, detailed, accurate, actionable
   - Response B: Generic, shallow, missing key details or slightly incorrect
3. Response A should CLEARLY be better than Response B
4. Include specific domain terminology and real-world applicability

CATEGORY: {category}
CATEGORY DESCRIPTION: {category_desc}

OUTPUT FORMAT (JSON):
{{
    "prompt": "The professional's question",
    "response_a": "The expert, comprehensive response",
    "response_b": "The mediocre, generic response",
    "category": "{category}",
    "reasoning": "Brief explanation of why A is better"
}}

Generate ONE preference pair now:"""


def get_category_for_domain(domain_id: str) -> tuple:
    """Get a random category from domain."""
    import random
    domain = get_domain(domain_id)
    if not domain:
        return "general", "General domain questions"
    cat = random.choice(domain.categories)
    return cat.id, cat.description


async def generate_preference_claude(
    client: anthropic.Anthropic,
    domain: str,
    category: str = None,
) -> Optional[Dict]:
    """Generate a single preference pair using Claude."""
    
    if category is None:
        category, cat_desc = get_category_for_domain(domain)
    else:
        domain_obj = get_domain(domain)
        cat_desc = next(
            (c.description for c in domain_obj.categories if c.id == category),
            "General questions"
        ) if domain_obj else "General questions"
    
    system_prompt = DOMAIN_PROMPTS.get(domain, f"You are an expert in {domain}.")
    user_prompt = GENERATION_TEMPLATE.format(
        domain=domain,
        category=category,
        category_desc=cat_desc
    )
    
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        # Extract JSON from response
        content = response.content[0].text
        
        # Find JSON in response
        start = content.find('{')
        end = content.rfind('}') + 1
        if start == -1 or end == 0:
            print(f"  [ERROR] No JSON found in response")
            return None
        
        json_str = content[start:end]
        data = json.loads(json_str)
        
        # Validate required fields
        required = ["prompt", "response_a", "response_b"]
        if not all(k in data for k in required):
            print(f"  [ERROR] Missing required fields")
            return None
        
        data["category"] = category
        data["domain"] = domain
        return data
        
    except json.JSONDecodeError as e:
        print(f"  [ERROR] JSON parse error: {e}")
        return None
    except Exception as e:
        print(f"  [ERROR] API error: {e}")
        return None


def submit_to_zuup(preference: Dict, api_key: str) -> bool:
    """Submit generated preference to Zuup API."""
    client = ZuupPreferenceClient(api_key=api_key)
    
    result = client.log_preference(
        domain=preference["domain"],
        category=preference.get("category", "general"),
        prompt=preference["prompt"],
        response_a=preference["response_a"],
        response_b=preference["response_b"],
        preference="A",  # A is always better in our generation
        annotator_id="claude_generator_v1",
        response_a_model="claude_expert",
        response_b_model="claude_baseline",
        notes=f"Generated: {datetime.now().isoformat()}"
    )
    
    return result.success


async def generate_batch(
    domain: str,
    count: int,
    api_key: str,
    submit: bool = True,
    output_file: str = None
) -> List[Dict]:
    """Generate multiple preference pairs for a domain."""
    
    if not HAS_ANTHROPIC or not ANTHROPIC_API_KEY:
        print("[ERROR] Anthropic API not configured")
        print("  Set ANTHROPIC_API_KEY environment variable")
        return []
    
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    generated = []
    submitted = 0
    
    print(f"\n=== Generating {count} preferences for {domain.upper()} ===")
    
    for i in range(count):
        print(f"  [{i+1}/{count}] Generating...", end=" ")
        
        pref = await generate_preference_claude(client, domain)
        
        if pref:
            generated.append(pref)
            print(f"[OK] {pref['prompt'][:40]}...")
            
            if submit and api_key:
                if submit_to_zuup(pref, api_key):
                    submitted += 1
                    print(f"           -> Submitted to Zuup")
                else:
                    print(f"           -> Submit failed")
        else:
            print("[FAILED]")
        
        # Rate limiting
        await asyncio.sleep(1)
    
    # Save to file if requested
    if output_file and generated:
        with open(output_file, 'w') as f:
            json.dump(generated, f, indent=2)
        print(f"\n  Saved {len(generated)} preferences to {output_file}")
    
    print(f"\n  Summary: {len(generated)} generated, {submitted} submitted")
    return generated


def main():
    parser = argparse.ArgumentParser(description="Generate preferences using Claude")
    parser.add_argument("--domain", type=str, help="Single domain to generate for")
    parser.add_argument("--all-priority", action="store_true", help="Generate for all priority domains")
    parser.add_argument("--count", type=int, default=10, help="Number of preferences per domain")
    parser.add_argument("--api-key", type=str, help="Zuup API key for submission")
    parser.add_argument("--no-submit", action="store_true", help="Generate only, don't submit")
    parser.add_argument("--output", type=str, help="Save generated preferences to JSON file")
    
    args = parser.parse_args()
    
    if not HAS_ANTHROPIC:
        print("[ERROR] anthropic package not installed")
        print("  Run: pip install anthropic")
        sys.exit(1)
    
    if not ANTHROPIC_API_KEY:
        print("[ERROR] ANTHROPIC_API_KEY not set")
        print("  Set environment variable or pass directly")
        sys.exit(1)
    
    api_key = args.api_key or ZUUP_API_KEY
    submit = not args.no_submit and bool(api_key)
    
    if not submit:
        print("[INFO] Running in generate-only mode (no submission)")
    
    # Determine domains
    priority_domains = ["procurement", "defense_wm", "halal"]
    
    if args.domain:
        domains = [args.domain]
    elif args.all_priority:
        domains = priority_domains
    else:
        print("Specify --domain or --all-priority")
        return
    
    # Generate
    all_generated = []
    for domain in domains:
        results = asyncio.run(generate_batch(
            domain=domain,
            count=args.count,
            api_key=api_key,
            submit=submit,
            output_file=None  # Save all at end
        ))
        all_generated.extend(results)
    
    # Save combined output
    if args.output and all_generated:
        with open(args.output, 'w') as f:
            json.dump(all_generated, f, indent=2)
        print(f"\nSaved {len(all_generated)} total preferences to {args.output}")
    
    print(f"\n=== Complete ===")
    print(f"Total generated: {len(all_generated)}")


if __name__ == "__main__":
    main()

