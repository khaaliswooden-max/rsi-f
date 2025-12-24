"""
Zuup Preference Collection UI

Gradio-based interface for collecting human preference annotations
across 10 Zuup domain-specific AI platforms.
"""

import json
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict

import gradio as gr
import pandas as pd

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from domains.taxonomy import DOMAINS, get_domain, get_domain_choices, get_category_choices
from domains.prompt_generator import PromptGenerator, generate_sample_pair


# ============================================================================
# PREFERENCE DATA STORE
# ============================================================================

@dataclass
class PreferenceRecord:
    """A single preference annotation record."""
    domain: str
    category: str
    prompt: str
    response_a: str
    response_b: str
    annotator_id: str
    preference: str  # "A", "B", or "tie"
    dimension_scores: Dict[str, int]
    timestamp: str
    record_hash: str
    difficulty: Optional[str] = None
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PreferenceStore:
    """
    Manages preference data storage and retrieval.
    
    Stores annotations as JSONL files, one per domain.
    """
    
    def __init__(self, data_dir: str = "preference_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    def _get_file_path(self, domain: str) -> Path:
        return self.data_dir / f"{domain}_preferences.jsonl"
        
    def save_annotation(self, record: PreferenceRecord) -> str:
        """Save an annotation to the appropriate domain file."""
        file_path = self._get_file_path(record.domain)
        
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict()) + "\n")
            
        return record.record_hash
        
    def load_domain_annotations(self, domain: str) -> List[PreferenceRecord]:
        """Load all annotations for a domain."""
        file_path = self._get_file_path(domain)
        
        if not file_path.exists():
            return []
            
        records = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    records.append(PreferenceRecord(**data))
                    
        return records
        
    def get_domain_stats(self, domain: str) -> Dict[str, Any]:
        """Get statistics for a domain's annotations."""
        records = self.load_domain_annotations(domain)
        
        if not records:
            return {
                "total": 0,
                "annotators": 0,
                "preference_distribution": {"A": 0, "B": 0, "tie": 0}
            }
            
        annotators = set(r.annotator_id for r in records)
        pref_dist = {"A": 0, "B": 0, "tie": 0}
        for r in records:
            if r.preference in pref_dist:
                pref_dist[r.preference] += 1
                
        return {
            "total": len(records),
            "annotators": len(annotators),
            "preference_distribution": pref_dist
        }
        
    def export_for_training(
        self,
        domain: str,
        format: str = "dpo"
    ) -> pd.DataFrame:
        """
        Export annotations in training-ready format.
        
        Args:
            domain: Domain to export
            format: Export format - "dpo" for Direct Preference Optimization
            
        Returns:
            DataFrame ready for training
        """
        records = self.load_domain_annotations(domain)
        
        if not records:
            return pd.DataFrame()
            
        if format == "dpo":
            # DPO format: prompt, chosen, rejected
            data = []
            for r in records:
                if r.preference == "A":
                    data.append({
                        "prompt": r.prompt,
                        "chosen": r.response_a,
                        "rejected": r.response_b,
                        "domain": r.domain,
                        "category": r.category
                    })
                elif r.preference == "B":
                    data.append({
                        "prompt": r.prompt,
                        "chosen": r.response_b,
                        "rejected": r.response_a,
                        "domain": r.domain,
                        "category": r.category
                    })
                # Skip ties for DPO
                    
            return pd.DataFrame(data)
        else:
            # Raw format
            return pd.DataFrame([r.to_dict() for r in records])
            
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics across all domains."""
        stats = {}
        for domain_id in DOMAINS.keys():
            stats[domain_id] = self.get_domain_stats(domain_id)
        return stats


# ============================================================================
# RESPONSE GENERATION (Placeholder - Replace with Ollama/LLM calls)
# ============================================================================

def generate_responses(
    prompt: str,
    domain_id: str,
    use_llm: bool = False
) -> Tuple[str, str]:
    """
    Generate two responses for comparison.
    
    In production, replace this with actual LLM calls.
    """
    if use_llm:
        # Placeholder for Ollama integration
        # See README for httpx-based implementation
        pass
        
    domain = get_domain(domain_id)
    domain_name = domain.name if domain else domain_id
    
    # Generate distinct placeholder responses
    response_a = f"""**Response A** (Conservative/Precise)

Based on my analysis of your query regarding {domain_name}:

**Key Points:**
1. This response takes a more conservative, methodical approach
2. Emphasis on established best practices and standards
3. Careful consideration of risks and compliance

**Recommendation:**
Following standard protocols would suggest a phased approach, ensuring each step is validated before proceeding.

**Caveats:**
- Specific circumstances may require adjustment
- Consult with domain experts for final decisions

This is a **placeholder response** for preference collection. In production, this would be generated by an LLM with temperature=0.3 for more deterministic output."""

    response_b = f"""**Response B** (Creative/Exploratory)

Interesting question about {domain_name}! Here's my take:

**Fresh Perspective:**
This response explores alternative approaches that might not be immediately obvious. Sometimes unconventional solutions yield the best results.

**Key Insights:**
• Consider emerging trends and technologies
• Think about edge cases others might miss  
• Balance innovation with practical constraints

**Action Items:**
1. Start with a pilot/proof-of-concept
2. Gather feedback and iterate quickly
3. Scale what works, abandon what doesn't

**Note:** While this approach is more exploratory, it's grounded in proven principles adapted to your specific context.

This is a **placeholder response** for preference collection. In production, this would be generated by an LLM with temperature=0.7 for more creative output."""

    return response_a, response_b


def compute_hash(
    prompt: str,
    response_a: str,
    response_b: str,
    annotator_id: str
) -> str:
    """Compute a unique hash for this annotation."""
    content = f"{prompt}|{response_a}|{response_b}|{annotator_id}|{datetime.now().isoformat()}"
    return hashlib.sha256(content.encode()).hexdigest()[:12]


# ============================================================================
# GRADIO UI
# ============================================================================

def create_collection_ui(store: PreferenceStore) -> gr.Blocks:
    """Create the Gradio collection interface."""
    
    generator = PromptGenerator()
    
    # Custom CSS for a polished look
    custom_css = """
    .gradio-container {
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
    .domain-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .response-box {
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        min-height: 300px;
    }
    .dimension-score {
        padding: 10px;
        background: #f5f5f5;
        border-radius: 5px;
        margin: 5px 0;
    }
    .stats-box {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #2d5a87;
    }
    """
    
    with gr.Blocks(
        title="Zuup Preference Collection",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="slate",
        ),
        css=custom_css
    ) as app:
        
        # Header
        gr.Markdown("""
        # 🎯 Zuup Preference Collection
        
        Collect human preference data for training domain-expert AI systems.
        """)
        
        # Session state
        current_prompt = gr.State("")
        current_response_a = gr.State("")
        current_response_b = gr.State("")
        current_category = gr.State("")
        current_difficulty = gr.State("")
        
        with gr.Tabs():
            # ----------------------------------------------------------------
            # TAB 1: Collection Interface
            # ----------------------------------------------------------------
            with gr.TabItem("📝 Collect Preferences"):
                
                with gr.Row():
                    # Left column: Setup
                    with gr.Column(scale=1):
                        gr.Markdown("### Annotator Setup")
                        
                        annotator_id = gr.Textbox(
                            label="Your Annotator ID",
                            placeholder="e.g., khaalis",
                            info="Unique identifier for tracking your contributions"
                        )
                        
                        domain_dropdown = gr.Dropdown(
                            label="Select Domain",
                            choices=[(d.name, d.id) for d in DOMAINS.values()],
                            value=list(DOMAINS.keys())[0] if DOMAINS else None,
                            info="Choose the domain you have expertise in"
                        )
                        
                        category_dropdown = gr.Dropdown(
                            label="Category (Optional)",
                            choices=[],
                            value=None,
                            info="Filter to specific task category"
                        )
                        
                        load_btn = gr.Button(
                            "🔄 Load New Pair",
                            variant="primary",
                            size="lg"
                        )
                        
                        # Domain info display
                        domain_info = gr.Markdown("")
                        
                    # Right column: Stats
                    with gr.Column(scale=1):
                        gr.Markdown("### Session Stats")
                        stats_display = gr.Markdown("*Select a domain to see stats*")
                        
                # Prompt display
                gr.Markdown("---")
                gr.Markdown("### Prompt")
                prompt_display = gr.Markdown("*Click 'Load New Pair' to start*")
                
                # Response comparison
                gr.Markdown("### Compare Responses")
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### Response A")
                        response_a_display = gr.Markdown("")
                        
                    with gr.Column():
                        gr.Markdown("#### Response B")
                        response_b_display = gr.Markdown("")
                
                # Evaluation section
                gr.Markdown("---")
                gr.Markdown("### Your Evaluation")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        # Dimension scores
                        gr.Markdown("**Rate each dimension (1-5):**")
                        
                        with gr.Row():
                            accuracy_score = gr.Slider(
                                label="Accuracy",
                                minimum=1, maximum=5, step=1, value=3,
                                info="Factual correctness and technical precision"
                            )
                            safety_score = gr.Slider(
                                label="Safety",
                                minimum=1, maximum=5, step=1, value=3,
                                info="Avoids harmful recommendations"
                            )
                            
                        with gr.Row():
                            actionability_score = gr.Slider(
                                label="Actionability",
                                minimum=1, maximum=5, step=1, value=3,
                                info="Clear, executable next steps"
                            )
                            clarity_score = gr.Slider(
                                label="Clarity",
                                minimum=1, maximum=5, step=1, value=3,
                                info="Well-organized and clear"
                            )
                            
                    with gr.Column(scale=1):
                        # Preference selection
                        gr.Markdown("**Which response is better overall?**")
                        preference_radio = gr.Radio(
                            choices=[
                                ("A is better", "A"),
                                ("B is better", "B"),
                                ("Tie (equally good/bad)", "tie")
                            ],
                            value=None,
                            label="Overall Preference"
                        )
                        
                        notes_input = gr.Textbox(
                            label="Notes (Optional)",
                            placeholder="Any additional observations...",
                            lines=3
                        )
                        
                # Submit button
                submit_btn = gr.Button(
                    "✅ Submit Annotation",
                    variant="primary",
                    size="lg"
                )
                
                submission_status = gr.Markdown("")
                
            # ----------------------------------------------------------------
            # TAB 2: Stats Dashboard  
            # ----------------------------------------------------------------
            with gr.TabItem("📊 Statistics"):
                gr.Markdown("### Collection Progress")
                
                refresh_stats_btn = gr.Button("🔄 Refresh Stats")
                
                overall_stats_display = gr.Markdown("")
                
                with gr.Row():
                    domain_stats_table = gr.DataFrame(
                        label="Annotations by Domain",
                        headers=["Domain", "Total", "Annotators", "A Pref", "B Pref", "Ties"],
                        interactive=False
                    )
                    
            # ----------------------------------------------------------------
            # TAB 3: Export
            # ----------------------------------------------------------------
            with gr.TabItem("📤 Export"):
                gr.Markdown("### Export Training Data")
                
                export_domain = gr.Dropdown(
                    label="Domain to Export",
                    choices=[(d.name, d.id) for d in DOMAINS.values()],
                    value=list(DOMAINS.keys())[0] if DOMAINS else None
                )
                
                export_format = gr.Radio(
                    choices=[
                        ("DPO Format (chosen/rejected)", "dpo"),
                        ("Raw Format (all fields)", "raw")
                    ],
                    value="dpo",
                    label="Export Format"
                )
                
                export_btn = gr.Button("📥 Export to JSONL", variant="primary")
                export_status = gr.Markdown("")
                export_preview = gr.DataFrame(label="Preview (first 5 rows)")
                
            # ----------------------------------------------------------------
            # TAB 4: Domain Reference
            # ----------------------------------------------------------------
            with gr.TabItem("📚 Domain Guide"):
                gr.Markdown("### Domain Evaluation Rubrics")
                
                domain_guide_select = gr.Dropdown(
                    label="Select Domain",
                    choices=[(d.name, d.id) for d in DOMAINS.values()],
                    value=list(DOMAINS.keys())[0] if DOMAINS else None
                )
                
                domain_guide_content = gr.Markdown("")
                
        # ====================================================================
        # EVENT HANDLERS
        # ====================================================================
        
        def update_categories(domain_id):
            """Update category dropdown when domain changes."""
            if not domain_id:
                return gr.update(choices=[], value=None)
            categories = get_category_choices(domain_id)
            return gr.update(
                choices=[("All Categories", None)] + categories,
                value=None
            )
            
        def update_domain_info(domain_id):
            """Update domain info display."""
            domain = get_domain(domain_id)
            if not domain:
                return ""
                
            return f"""
**Platform:** {domain.platform.value}  
**Min Samples:** {domain.min_samples}  
**Expertise Required:** {domain.expertise_requirements}
"""
            
        def update_stats_display(domain_id):
            """Update stats display for selected domain."""
            stats = store.get_domain_stats(domain_id)
            domain = get_domain(domain_id)
            min_samples = domain.min_samples if domain else 300
            progress = (stats["total"] / min_samples) * 100
            
            return f"""
<div class="stats-box">
<strong>Domain Progress:</strong> {stats['total']} / {min_samples} ({progress:.1f}%)

**Unique Annotators:** {stats['annotators']}

**Preference Distribution:**
- A preferred: {stats['preference_distribution']['A']}
- B preferred: {stats['preference_distribution']['B']}
- Ties: {stats['preference_distribution']['tie']}
</div>
"""
            
        def load_new_pair(domain_id, category_id, annotator_id):
            """Load a new prompt-response pair."""
            if not annotator_id:
                return (
                    "⚠️ *Please enter your Annotator ID first*",
                    "", "", "", "", "",
                    "Please enter your annotator ID above to start."
                )
                
            try:
                # Generate prompt
                prompt_obj = generator.generate(domain_id, category_id if category_id else None)
                
                # Generate responses
                response_a, response_b = generate_responses(prompt_obj.prompt, domain_id)
                
                prompt_md = f"""
**Category:** {prompt_obj.category_id} | **Difficulty:** {prompt_obj.difficulty}

---

{prompt_obj.prompt}
"""
                
                return (
                    prompt_md,
                    response_a,
                    response_b,
                    prompt_obj.prompt,
                    response_a,
                    response_b,
                    prompt_obj.category_id,
                    prompt_obj.difficulty,
                    ""
                )
            except Exception as e:
                return (
                    f"⚠️ *Error loading pair: {e}*",
                    "", "", "", "", "", "", "", ""
                )
                
        def submit_annotation(
            annotator_id, domain_id,
            prompt, response_a, response_b, category, difficulty,
            preference, accuracy, safety, actionability, clarity, notes
        ):
            """Submit the annotation."""
            if not annotator_id:
                return "❌ Please enter your Annotator ID"
            if not preference:
                return "❌ Please select a preference (A, B, or Tie)"
            if not prompt:
                return "❌ Please load a prompt-response pair first"
                
            # Create record
            record = PreferenceRecord(
                domain=domain_id,
                category=category or "unknown",
                prompt=prompt,
                response_a=response_a,
                response_b=response_b,
                annotator_id=annotator_id,
                preference=preference,
                dimension_scores={
                    "accuracy": int(accuracy),
                    "safety": int(safety),
                    "actionability": int(actionability),
                    "clarity": int(clarity)
                },
                timestamp=datetime.now().isoformat(),
                record_hash=compute_hash(prompt, response_a, response_b, annotator_id),
                difficulty=difficulty,
                notes=notes if notes else None
            )
            
            # Save
            record_hash = store.save_annotation(record)
            
            return f"✅ Annotation saved! (Hash: `{record_hash}`)\n\n*Click 'Load New Pair' for the next comparison.*"
            
        def get_all_domain_stats():
            """Get stats for all domains as DataFrame."""
            all_stats = store.get_all_stats()
            
            data = []
            for domain_id, stats in all_stats.items():
                domain = get_domain(domain_id)
                data.append([
                    domain.name if domain else domain_id,
                    stats["total"],
                    stats["annotators"],
                    stats["preference_distribution"]["A"],
                    stats["preference_distribution"]["B"],
                    stats["preference_distribution"]["tie"]
                ])
                
            return pd.DataFrame(
                data,
                columns=["Domain", "Total", "Annotators", "A Pref", "B Pref", "Ties"]
            )
            
        def export_data(domain_id, format_type):
            """Export annotations for training."""
            df = store.export_for_training(domain_id, format_type)
            
            if df.empty:
                return "⚠️ No annotations found for this domain.", pd.DataFrame()
                
            # Save to file
            output_path = store.data_dir / f"{domain_id}_{format_type}.jsonl"
            df.to_json(output_path, orient="records", lines=True)
            
            return f"✅ Exported {len(df)} records to `{output_path}`", df.head(5)
            
        def get_domain_guide(domain_id):
            """Generate domain guide content."""
            domain = get_domain(domain_id)
            if not domain:
                return "*Domain not found*"
                
            content = f"""
## {domain.name}

**Platform:** {domain.platform.value}  
**Description:** {domain.description}

### Categories

"""
            for cat in domain.categories:
                content += f"**{cat.name}** (`{cat.id}`)\n"
                content += f": {cat.description}\n\n"
                
            content += "\n### Evaluation Dimensions\n\n"
            
            for dim in domain.dimensions:
                content += f"#### {dim.name.title()}\n"
                content += f"{dim.description}\n\n"
                content += "| Score | Meaning |\n|-------|--------|\n"
                for score, desc in sorted(dim.rubric.items()):
                    content += f"| {score} | {desc} |\n"
                content += "\n"
                
            content += f"\n### Annotator Requirements\n\n{domain.expertise_requirements}\n"
            content += f"\n**Target Collection Size:** {domain.min_samples} samples\n"
            
            return content
            
        # Wire up events
        domain_dropdown.change(
            update_categories,
            inputs=[domain_dropdown],
            outputs=[category_dropdown]
        )
        
        domain_dropdown.change(
            update_domain_info,
            inputs=[domain_dropdown],
            outputs=[domain_info]
        )
        
        domain_dropdown.change(
            update_stats_display,
            inputs=[domain_dropdown],
            outputs=[stats_display]
        )
        
        load_btn.click(
            load_new_pair,
            inputs=[domain_dropdown, category_dropdown, annotator_id],
            outputs=[
                prompt_display,
                response_a_display,
                response_b_display,
                current_prompt,
                current_response_a,
                current_response_b,
                current_category,
                current_difficulty,
                submission_status
            ]
        )
        
        submit_btn.click(
            submit_annotation,
            inputs=[
                annotator_id, domain_dropdown,
                current_prompt, current_response_a, current_response_b,
                current_category, current_difficulty,
                preference_radio,
                accuracy_score, safety_score, actionability_score, clarity_score,
                notes_input
            ],
            outputs=[submission_status]
        )
        
        refresh_stats_btn.click(
            get_all_domain_stats,
            inputs=[],
            outputs=[domain_stats_table]
        )
        
        export_btn.click(
            export_data,
            inputs=[export_domain, export_format],
            outputs=[export_status, export_preview]
        )
        
        domain_guide_select.change(
            get_domain_guide,
            inputs=[domain_guide_select],
            outputs=[domain_guide_content]
        )
        
        # Initialize on load
        app.load(
            lambda: get_all_domain_stats(),
            inputs=[],
            outputs=[domain_stats_table]
        )
        
    return app


def run_collection_ui(
    share: bool = False,
    port: int = 7860,
    data_dir: str = "preference_data"
):
    """
    Launch the preference collection UI.
    
    Args:
        share: Whether to create a public Gradio share link
        port: Local port to run on
        data_dir: Directory for storing preference data
    """
    print("\n" + "=" * 50)
    print("Zuup Preference Collection")
    print("=" * 50)
    
    store = PreferenceStore(data_dir)
    app = create_collection_ui(store)
    
    app.launch(
        share=share,
        server_port=port,
        show_error=True
    )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Zuup Preference Collection UI")
    parser.add_argument("--share", action="store_true", help="Create public share link")
    parser.add_argument("--port", type=int, default=7860, help="Port to run on")
    parser.add_argument("--data-dir", type=str, default="preference_data", help="Data directory")
    
    args = parser.parse_args()
    
    run_collection_ui(
        share=args.share,
        port=args.port,
        data_dir=args.data_dir
    )

