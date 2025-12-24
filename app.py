"""
Zuup Preference Collection - Hugging Face Spaces
=================================================
A beautiful interface for collecting human preference data.
"""

import gradio as gr
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
import random

# Import domain modules
from domains.taxonomy import (
    get_domain,
    get_all_domains,
    get_category_choices,
    DOMAINS,
)
from domains.prompt_generator import get_random_prompt


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STORAGE
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class PreferenceRecord:
    """A single preference annotation record."""
    domain: str
    category: str
    prompt: str
    response_a: str
    response_b: str
    annotator_id: str
    preference: str
    dimension_scores: Dict[str, int]
    timestamp: str
    record_hash: str
    difficulty: str = "medium"
    notes: str = ""


class PreferenceStore:
    """Manages preference data storage."""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent / "preference_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, domain: str) -> Path:
        return self.data_dir / f"{domain}_preferences.jsonl"
    
    def save_record(self, record: PreferenceRecord) -> bool:
        try:
            content = f"{record.domain}|{record.prompt}|{record.annotator_id}|{record.timestamp}"
            record.record_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            file_path = self._get_file_path(record.domain)
            
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
            return True
        except Exception as e:
            print(f"Error saving record: {e}")
            return False
    
    def load_records(self, domain: str) -> List[PreferenceRecord]:
        file_path = self._get_file_path(domain)
        records = []
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        records.append(PreferenceRecord(**json.loads(line)))
        return records
    
    def get_stats(self) -> Dict[str, Dict]:
        stats = {}
        for domain in DOMAINS:
            records = self.load_records(domain)
            annotators = set(r.annotator_id for r in records)
            pref_dist = {"A": 0, "B": 0, "TIE": 0}
            for r in records:
                pref_dist[r.preference] = pref_dist.get(r.preference, 0) + 1
            stats[domain] = {
                "total": len(records),
                "annotators": len(annotators),
                "preference_distribution": pref_dist,
                "target": DOMAINS[domain].min_samples
            }
        return stats


# Initialize store
store = PreferenceStore()


def generate_responses(prompt: str, domain: str) -> Tuple[str, str]:
    """Generate placeholder responses for comparison."""
    domain_info = get_domain(domain)
    domain_name = domain_info.name if domain_info else domain
    
    response_a = f"""**Response A**

Based on my analysis of your {domain_name} query:

1. **Primary Analysis**: The core issue involves understanding fundamental requirements.
2. **Key Considerations**: Regulatory factors, technical feasibility, resource implications.
3. **Recommended Approach**: A phased approach prioritizing risk mitigation.
4. **Next Steps**: Document current state, identify stakeholders, develop roadmap.

*[Placeholder response - integrate with LLM in production]*"""

    response_b = f"""**Response B**

Thank you for this {domain_name} question. Here's my analysis:

**Executive Summary**: This requires balancing immediate needs against long-term objectives.

**Technical Perspective**:
- Option 1: Conservative approach minimizing risk
- Option 2: Aggressive approach maximizing benefits  
- Option 3: Balanced trade-off approach

**Recommendations**:
1. Conduct thorough assessment
2. Engage stakeholders early
3. Establish success metrics
4. Implement iterative improvements

*[Placeholder response - integrate with LLM in production]*"""

    return response_a, response_b


# Custom CSS
CUSTOM_CSS = """
.main-header { text-align: center; padding: 1.5rem; margin-bottom: 1rem; }
.main-header h1 { font-size: 2rem; margin-bottom: 0.5rem; }
"""


def create_ui():
    """Create the Gradio interface."""
    
    with gr.Blocks(
        title="Zuup Preference Collection",
        css=CUSTOM_CSS,
        theme=gr.themes.Soft()
    ) as demo:
        
        # State
        current_prompt = gr.State("")
        current_response_a = gr.State("")
        current_response_b = gr.State("")
        current_category = gr.State("")
        current_difficulty = gr.State("")
        
        # Header
        gr.HTML("""
            <div class="main-header">
                <h1>🎯 Zuup Preference Collection</h1>
                <p>Collecting expert human feedback to train domain-specific AI systems</p>
            </div>
        """)
        
        with gr.Tabs():
            # Annotation Tab
            with gr.TabItem("📝 Annotate"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### ⚙️ Configuration")
                        annotator_id = gr.Textbox(label="Annotator ID", placeholder="your-name")
                        domain_dropdown = gr.Dropdown(
                            label="Domain",
                            choices=[(f"{d.icon} {d.name}", d.id) for d in get_all_domains()],
                            value="procurement"
                        )
                        category_dropdown = gr.Dropdown(label="Category", choices=[])
                        load_btn = gr.Button("🔄 Load New Pair", variant="primary")
                        session_stats = gr.Markdown("*Load a pair to begin*")
                    
                    with gr.Column(scale=3):
                        gr.Markdown("### 📋 Prompt")
                        prompt_display = gr.Markdown("*Click 'Load New Pair' to begin*")
                        
                        gr.Markdown("### 🔍 Compare Responses")
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("#### 🅰️ Response A")
                                response_a_display = gr.Markdown("*Waiting...*")
                            with gr.Column():
                                gr.Markdown("#### 🅱️ Response B")
                                response_b_display = gr.Markdown("*Waiting...*")
                        
                        gr.Markdown("### 📏 Rate Quality (1-5)")
                        with gr.Row():
                            accuracy_slider = gr.Slider(1, 5, value=3, step=1, label="🎯 Accuracy")
                            safety_slider = gr.Slider(1, 5, value=3, step=1, label="🛡️ Safety")
                        with gr.Row():
                            actionability_slider = gr.Slider(1, 5, value=3, step=1, label="🚀 Actionability")
                            clarity_slider = gr.Slider(1, 5, value=3, step=1, label="✨ Clarity")
                        
                        notes_input = gr.Textbox(label="📝 Notes (Optional)", lines=2)
                        
                        gr.Markdown("### 🏆 Select Winner")
                        with gr.Row():
                            prefer_a_btn = gr.Button("🅰️ Prefer A", variant="primary")
                            prefer_tie_btn = gr.Button("🤝 Tie", variant="secondary")
                            prefer_b_btn = gr.Button("🅱️ Prefer B", variant="primary")
                        
                        submit_status = gr.Markdown("")
            
            # Progress Tab
            with gr.TabItem("📊 Progress"):
                gr.Markdown("### 📈 Collection Progress")
                refresh_btn = gr.Button("🔄 Refresh")
                stats_display = gr.HTML()
                
                def get_stats_html():
                    stats = store.get_stats()
                    html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">'
                    for domain_id, s in stats.items():
                        domain = get_domain(domain_id)
                        if not domain:
                            continue
                        progress = min(100, (s["total"] / s["target"]) * 100) if s["target"] > 0 else 0
                        html += f'''
                        <div style="background: #f0f0f0; padding: 1rem; border-radius: 8px;">
                            <strong>{domain.icon} {domain.name}</strong><br>
                            <span>{s["total"]} / {s["target"]} ({progress:.1f}%)</span><br>
                            <span>{s["annotators"]} annotators</span>
                        </div>'''
                    html += '</div>'
                    return html
                
                refresh_btn.click(get_stats_html, outputs=[stats_display])
                demo.load(get_stats_html, outputs=[stats_display])
            
            # Domains Tab
            with gr.TabItem("📚 Domains"):
                gr.Markdown("### 🗂️ Available Domains")
                domains_html = ""
                for d in get_all_domains():
                    cats = ", ".join([c.name for c in d.categories])
                    domains_html += f"**{d.icon} {d.name}** ({d.platform})\n\n"
                    domains_html += f"{d.description}\n\n"
                    domains_html += f"Categories: {cats}\n\n---\n\n"
                gr.Markdown(domains_html)
        
        # Event handlers
        def update_categories(domain_id):
            choices = get_category_choices(domain_id)
            return gr.Dropdown(choices=[("All", None)] + choices, value=None)
        
        domain_dropdown.change(update_categories, [domain_dropdown], [category_dropdown])
        
        def load_pair(domain_id, category_id, annotator):
            if not annotator:
                return ("*Enter your Annotator ID*", "*Enter ID*", "*Enter ID*", 
                        "", "", "", "", "*Enter your Annotator ID to begin*")
            
            prompt_obj = get_random_prompt(domain_id, category_id)
            response_a, response_b = generate_responses(prompt_obj.prompt, domain_id)
            
            records = store.load_records(domain_id)
            user_records = [r for r in records if r.annotator_id == annotator]
            stats = f"**Your Progress:** {len(user_records)} | **Domain Total:** {len(records)}/{DOMAINS[domain_id].min_samples}"
            
            return (prompt_obj.prompt, response_a, response_b,
                    prompt_obj.prompt, response_a, response_b,
                    prompt_obj.category, prompt_obj.difficulty, stats)
        
        load_btn.click(
            load_pair,
            [domain_dropdown, category_dropdown, annotator_id],
            [prompt_display, response_a_display, response_b_display,
             current_prompt, current_response_a, current_response_b,
             current_category, current_difficulty, session_stats]
        )
        
        def submit_pref(pref, domain_id, annotator, prompt, resp_a, resp_b, 
                        cat, diff, acc, safe, action, clarity, notes):
            if not annotator:
                return "❌ Please enter your Annotator ID"
            if not prompt or prompt.startswith("*"):
                return "❌ Please load a prompt pair first"
            
            record = PreferenceRecord(
                domain=domain_id,
                category=cat or "general",
                prompt=prompt,
                response_a=resp_a,
                response_b=resp_b,
                annotator_id=annotator,
                preference=pref,
                dimension_scores={"accuracy": acc, "safety": safe, 
                                  "actionability": action, "clarity": clarity},
                timestamp=datetime.now().isoformat(),
                record_hash="",
                difficulty=diff or "medium",
                notes=notes
            )
            
            if store.save_record(record):
                return f"✅ Saved! Preference '{pref}' recorded."
            return "❌ Failed to save. Try again."
        
        # Connect preference buttons
        prefer_a_btn.click(
            lambda *args: submit_pref("A", *args),
            [domain_dropdown, annotator_id, current_prompt, current_response_a, 
             current_response_b, current_category, current_difficulty,
             accuracy_slider, safety_slider, actionability_slider, clarity_slider, notes_input],
            [submit_status]
        )
        prefer_tie_btn.click(
            lambda *args: submit_pref("TIE", *args),
            [domain_dropdown, annotator_id, current_prompt, current_response_a,
             current_response_b, current_category, current_difficulty,
             accuracy_slider, safety_slider, actionability_slider, clarity_slider, notes_input],
            [submit_status]
        )
        prefer_b_btn.click(
            lambda *args: submit_pref("B", *args),
            [domain_dropdown, annotator_id, current_prompt, current_response_a,
             current_response_b, current_category, current_difficulty,
             accuracy_slider, safety_slider, actionability_slider, clarity_slider, notes_input],
            [submit_status]
        )
    
    return demo


# Create and launch
demo = create_ui()
demo.launch()
