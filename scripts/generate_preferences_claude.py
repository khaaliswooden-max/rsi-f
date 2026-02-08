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
from datetime import datetime, timezone
import hashlib

# Add parent dir to path
_REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO_ROOT))
DEFAULT_OUTPUT_DIR = _REPO_ROOT / "preference_data"

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

    "biomedical": """You are an expert in gut-brain communication interface (GB-CI) research and biomedical systems:
- Biosensor design for enteric and vagal signaling
- Neural-enteric analysis and gut-brain axis
- Clinical protocols and IRB for GB-CI trials
- Biomedical data interpretation and biomarker tracking
- Symbion platform research applications

Generate realistic questions that biomedical or neuroscience researchers would ask.""",

    "ingestible": """You are an expert in ingestible devices and capsule endoscopy (Symbion HW):
- Capsule design, form factor, power, and in-body telemetry
- In-vivo sensing (pH, motility, gas) and calibration
- FDA/CE regulatory pathway (510(k), de novo, clinical evidence)
- Manufacturing, bioburden testing, and QC for ingestibles

Generate realistic questions that medical device or biomedical engineers would ask.""",

    "legacy": """You are an expert in legacy system modernization and COBOL/mainframe transformation (Relian):
- COBOL analysis, copybooks, business rules, dead code
- Migration strategy (rehost/refactor/replace), CICS, VSAM
- Code translation (COBOL to Java, JCL to orchestration, CICS to REST)
- Testing and validation for migration correctness

Generate realistic questions that mainframe developers or architects would ask.""",

    "autonomy": """You are an expert in autonomous agent systems and AI safety (Veyra):
- Agent architecture, goals, communication, memory
- Safety constraints, human override, resource limits
- Multi-agent coordination, negotiation, conflict resolution
- Verification, alignment, and behavioral monitoring

Generate realistic questions that AI safety researchers or autonomy engineers would ask.""",

    "quantum_arch": """You are an expert in quantum archaeology and historical reconstruction (QAWM):
- Temporal modeling, Bayesian chronology, event sequences
- Artifact analysis, provenance, trade routes
- Quantum algorithms (QAOA, VQE, sampling) for archaeology
- Data integration (stratigraphy, radiocarbon, textual evidence)

Generate realistic questions that archaeologists or quantum-computing practitioners would ask.""",

    "mobile_dc": """You are an expert in mobile data centers and tactical edge computing (PodX):
- Edge computing, workload placement, latency, resource-constrained ML
- DDIL (Denied, Degraded, Intermittent, Limited) operations and sync
- Tactical infrastructure, power budget, hardening, rapid deployment
- Security and COMSEC in disconnected environments

Generate realistic questions that edge or tactical IT engineers would ask.""",

    "hubzone": """You are an expert in HUBZone small business contracting (HZ Navigator):
- HUBZone certification, eligibility, employee residence, principal office
- Set-aside contracting, sole-source thresholds, price evaluation preference
- Ongoing compliance, recertification, employee count, redesignation
- Teaming, mentor-protégé, JV performance of work, affiliation

Generate realistic questions that SBA or small business contracting specialists would ask.""",
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


def preference_to_jsonl_record(pref: Dict, index: int) -> Dict:
    """Convert generated preference to JSONL record matching seed script schema."""
    record = {
        "domain": pref["domain"],
        "category": pref.get("category", "general"),
        "prompt": pref["prompt"],
        "response_a": pref["response_a"],
        "response_b": pref["response_b"],
        "preference": "A",
        "annotator_id": "claude_generator_v1",
        "dimension_scores": {"accuracy": 5, "completeness": 5, "clarity": 5, "relevance": 5},
        "metadata": {
            "source": "synthetic",
            "generator": "generate_preferences_claude",
            "batch_index": index,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }
    content = f"{record['prompt']}{record['response_a']}{record['response_b']}"
    record["record_hash"] = hashlib.sha256(content.encode()).hexdigest()[:12]
    return record


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
    output_file: str = None,
    output_dir: Optional[str] = None,
) -> List[Dict]:
    """Generate multiple preference pairs for a domain. Optionally append JSONL to output_dir."""
    
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
    
    # Save to single JSON file if requested (legacy)
    if output_file and generated:
        with open(output_file, 'w') as f:
            json.dump(generated, f, indent=2)
        print(f"\n  Saved {len(generated)} preferences to {output_file}")
    
    # Append JSONL to domain-specific file (same schema as seed scripts)
    if output_dir and generated:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        jsonl_path = out_path / f"{domain}_preferences.jsonl"
        existing_hashes = set()
        if jsonl_path.exists():
            with open(jsonl_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        rec = json.loads(line.strip())
                        if rec.get("record_hash"):
                            existing_hashes.add(rec["record_hash"])
                    except Exception:
                        pass
        appended = 0
        with open(jsonl_path, 'a', encoding='utf-8') as f:
            for idx, pref in enumerate(generated):
                record = preference_to_jsonl_record(pref, idx)
                if record["record_hash"] in existing_hashes:
                    continue
                f.write(json.dumps(record) + "\n")
                existing_hashes.add(record["record_hash"])
                appended += 1
        print(f"\n  Appended {appended} preferences to {jsonl_path}")
    
    print(f"\n  Summary: {len(generated)} generated, {submitted} submitted")
    return generated


def main():
    parser = argparse.ArgumentParser(description="Generate preferences using Claude")
    parser.add_argument("--domain", type=str, help="Single domain to generate for")
    parser.add_argument("--all-priority", action="store_true", help="Generate for priority domains (procurement, defense_wm, halal)")
    parser.add_argument("--all-domains", action="store_true", help="Generate for all domains in taxonomy")
    parser.add_argument("--count", type=int, default=10, help="Number of preferences per domain")
    parser.add_argument("--api-key", type=str, help="Zuup API key for submission")
    parser.add_argument("--no-submit", action="store_true", help="Generate only, don't submit")
    parser.add_argument("--output", type=str, help="Save combined generated preferences to a single JSON file")
    parser.add_argument("--output-dir", type=str, default=str(DEFAULT_OUTPUT_DIR), help="Directory for per-domain JSONL files (default: preference_data)")
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
    all_domain_ids = list(DOMAINS.keys())

    if args.domain:
        if args.domain not in all_domain_ids:
            print(f"[ERROR] Unknown domain: {args.domain}. Choose from: {all_domain_ids}")
            sys.exit(1)
        domains = [args.domain]
    elif args.all_domains:
        domains = all_domain_ids
        print(f"[INFO] Generating for all {len(domains)} domains: {domains}")
    elif args.all_priority:
        domains = priority_domains
    else:
        print("Specify --domain, --all-priority, or --all-domains")
        return

    # Generate (each domain batch writes its own JSONL when output_dir is set)
    all_generated = []
    for domain in domains:
        results = asyncio.run(generate_batch(
            domain=domain,
            count=args.count,
            api_key=api_key,
            submit=submit,
            output_file=None,
            output_dir=args.output_dir,
        ))
        all_generated.extend(results)

    # Save combined JSON if requested
    if args.output and all_generated:
        with open(args.output, 'w') as f:
            json.dump(all_generated, f, indent=2)
        print(f"\nSaved {len(all_generated)} total preferences to {args.output}")

    print(f"\n=== Complete ===")
    print(f"Total generated: {len(all_generated)}")


if __name__ == "__main__":
    main()

