"""
Zuup Preference Collection UI
=============================
A beautiful Gradio interface for collecting human preference data
across all 10 Zuup domain platforms.
"""

import gradio as gr
import json
import hashlib
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import random

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_client import generate_response_pair
from domains.taxonomy import (
    get_domain,
    get_all_domains,
    get_domain_choices,
    get_category_choices,
    get_dimension_info,
    DOMAINS,
)
from domains.prompt_generator import get_random_prompt, generate_prompt_pair


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
    preference: str  # "A", "B", or "TIE"
    dimension_scores: Dict[str, int]
    timestamp: str
    record_hash: str
    difficulty: str = "medium"
    notes: str = ""


class PreferenceStore:
    """Manages preference data storage and retrieval."""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "preference_data"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, domain: str) -> Path:
        return self.data_dir / f"{domain}_preferences.jsonl"
    
    def _compute_hash(self, record: PreferenceRecord) -> str:
        """Compute a unique hash for record deduplication."""
        content = f"{record.domain}|{record.prompt}|{record.annotator_id}|{record.timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def save_record(self, record: PreferenceRecord) -> bool:
        """Save a preference record to the appropriate domain file."""
        try:
            record.record_hash = self._compute_hash(record)
            file_path = self._get_file_path(record.domain)
            
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
            
            return True
        except Exception as e:
            print(f"Error saving record: {e}")
            return False
    
    def load_records(self, domain: str) -> List[PreferenceRecord]:
        """Load all records for a domain."""
        file_path = self._get_file_path(domain)
        records = []
        
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        records.append(PreferenceRecord(**data))
        
        return records
    
    def get_stats(self) -> Dict[str, Dict]:
        """Get collection statistics by domain."""
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
    
    def export_for_training(self, domain: str, format: str = "dpo") -> List[Dict]:
        """Export data in training-ready format."""
        records = self.load_records(domain)
        
        if format == "dpo":
            # Direct Preference Optimization format
            exported = []
            for r in records:
                if r.preference == "A":
                    chosen, rejected = r.response_a, r.response_b
                elif r.preference == "B":
                    chosen, rejected = r.response_b, r.response_a
                else:
                    continue  # Skip ties for DPO
                
                exported.append({
                    "prompt": r.prompt,
                    "chosen": chosen,
                    "rejected": rejected,
                    "domain": r.domain,
                    "category": r.category,
                })
            return exported
        
        elif format == "rm":
            # Reward model format
            exported = []
            for r in records:
                if r.preference == "A":
                    chosen, rejected = r.response_a, r.response_b
                elif r.preference == "B":
                    chosen, rejected = r.response_b, r.response_a
                else:
                    continue
                
                exported.append({
                    "prompt": r.prompt,
                    "chosen": chosen,
                    "rejected": rejected,
                    "scores": r.dimension_scores,
                })
            return exported
        
        else:
            # Raw format
            return [asdict(r) for r in records]


# ═══════════════════════════════════════════════════════════════════════════════
# RESPONSE GENERATION (shared LLM client; fallback to placeholders if unavailable)
# ═══════════════════════════════════════════════════════════════════════════════

def generate_responses(prompt: str, domain: str) -> Tuple[str, str]:
    """Generate two responses for comparison via shared LLM client."""
    return generate_response_pair(prompt, domain_id=domain)


# ═══════════════════════════════════════════════════════════════════════════════
# GRADIO UI
# ═══════════════════════════════════════════════════════════════════════════════

# Initialize store
store = PreferenceStore()

# Custom CSS for beautiful styling
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Outfit:wght@300;400;500;600;700&display=swap');

:root {
    --zuup-primary: #6366f1;
    --zuup-secondary: #8b5cf6;
    --zuup-accent: #f59e0b;
    --zuup-dark: #0f172a;
    --zuup-darker: #020617;
    --zuup-surface: #1e293b;
    --zuup-surface-light: #334155;
    --zuup-text: #f1f5f9;
    --zuup-text-muted: #94a3b8;
    --zuup-success: #10b981;
    --zuup-warning: #f59e0b;
    --zuup-error: #ef4444;
    --gradient-primary: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
    --gradient-dark: linear-gradient(180deg, #0f172a 0%, #020617 100%);
}

.gradio-container {
    background: var(--gradient-dark) !important;
    font-family: 'Outfit', sans-serif !important;
    min-height: 100vh;
}

.main-header {
    text-align: center;
    padding: 2rem 1rem;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
    border-radius: 1rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(99, 102, 241, 0.2);
}

.main-header h1 {
    font-family: 'Outfit', sans-serif !important;
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem !important;
}

.main-header p {
    color: var(--zuup-text-muted) !important;
    font-size: 1.1rem !important;
}

.domain-card {
    background: var(--zuup-surface) !important;
    border: 1px solid var(--zuup-surface-light) !important;
    border-radius: 0.75rem !important;
    padding: 1rem !important;
    transition: all 0.2s ease !important;
}

.domain-card:hover {
    border-color: var(--zuup-primary) !important;
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.15) !important;
}

.response-panel {
    background: var(--zuup-surface) !important;
    border: 2px solid var(--zuup-surface-light) !important;
    border-radius: 1rem !important;
    padding: 1.5rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.9rem !important;
    line-height: 1.6 !important;
    max-height: 500px !important;
    overflow-y: auto !important;
}

.response-panel-a {
    border-left: 4px solid #3b82f6 !important;
}

.response-panel-b {
    border-left: 4px solid #f59e0b !important;
}

.preference-btn {
    padding: 1rem 2rem !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    border-radius: 0.75rem !important;
    transition: all 0.2s ease !important;
    min-width: 150px !important;
}

.btn-a {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    border: none !important;
}

.btn-a:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4) !important;
}

.btn-b {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
    border: none !important;
}

.btn-b:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 20px rgba(245, 158, 11, 0.4) !important;
}

.btn-tie {
    background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%) !important;
    border: none !important;
}

.slider-label {
    color: var(--zuup-text) !important;
    font-weight: 500 !important;
}

.stat-card {
    background: var(--zuup-surface) !important;
    border-radius: 0.75rem !important;
    padding: 1rem !important;
    text-align: center !important;
}

.stat-number {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: var(--zuup-primary) !important;
}

.progress-bar {
    height: 8px !important;
    border-radius: 4px !important;
    background: var(--zuup-surface-light) !important;
    overflow: hidden !important;
}

.progress-fill {
    height: 100% !important;
    background: var(--gradient-primary) !important;
    border-radius: 4px !important;
    transition: width 0.3s ease !important;
}

.prompt-display {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%) !important;
    border: 1px solid rgba(99, 102, 241, 0.3) !important;
    border-radius: 1rem !important;
    padding: 1.5rem !important;
    font-size: 1rem !important;
    line-height: 1.7 !important;
}

.dimension-slider {
    margin: 0.75rem 0 !important;
}

.footer-info {
    text-align: center;
    padding: 1rem;
    color: var(--zuup-text-muted);
    font-size: 0.85rem;
    margin-top: 2rem;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--zuup-dark);
}

::-webkit-scrollbar-thumb {
    background: var(--zuup-surface-light);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--zuup-primary);
}
"""


def create_ui():
    """Create the main Gradio interface."""
    
    # State variables
    current_prompt = gr.State("")
    current_response_a = gr.State("")
    current_response_b = gr.State("")
    current_category = gr.State("")
    current_difficulty = gr.State("")
    
    with gr.Blocks(
        title="Zuup Preference Collection",
        css=CUSTOM_CSS,
        theme=gr.themes.Base(
            primary_hue="indigo",
            secondary_hue="purple",
            neutral_hue="slate",
            font=("Outfit", "sans-serif"),
            font_mono=("JetBrains Mono", "monospace"),
        ).set(
            body_background_fill="#0f172a",
            body_background_fill_dark="#020617",
            block_background_fill="#1e293b",
            block_background_fill_dark="#1e293b",
            block_border_color="#334155",
            block_label_text_color="#f1f5f9",
            block_title_text_color="#f1f5f9",
            input_background_fill="#0f172a",
            input_border_color="#334155",
            button_primary_background_fill="#6366f1",
            button_primary_background_fill_hover="#4f46e5",
        )
    ) as demo:
        
        # Header
        gr.HTML("""
            <div class="main-header">
                <h1>🎯 Zuup Preference Collection</h1>
                <p>Collecting expert human feedback to train domain-specific AI systems</p>
            </div>
        """)
        
        with gr.Tabs() as tabs:
            
            # ═══════════════════════════════════════════════════════════════
            # TAB 1: Annotation Interface
            # ═══════════════════════════════════════════════════════════════
            with gr.TabItem("📝 Annotate", id="annotate"):
                
                with gr.Row():
                    # Left sidebar - Configuration
                    with gr.Column(scale=1):
                        gr.Markdown("### ⚙️ Configuration")
                        
                        annotator_id = gr.Textbox(
                            label="Annotator ID",
                            placeholder="your-name",
                            info="Your unique identifier for tracking contributions"
                        )
                        
                        domain_dropdown = gr.Dropdown(
                            label="Domain",
                            choices=[(f"{d.icon} {d.name} ({d.platform})", d.id) for d in get_all_domains()],
                            value="procurement",
                            info="Select the domain to annotate"
                        )
                        
                        category_dropdown = gr.Dropdown(
                            label="Category (Optional)",
                            choices=[],
                            value=None,
                            info="Filter by specific category"
                        )
                        
                        load_btn = gr.Button(
                            "🔄 Load New Pair",
                            variant="primary",
                            size="lg"
                        )
                        
                        gr.Markdown("---")
                        gr.Markdown("### 📊 Session Stats")
                        session_stats = gr.Markdown("*Load a pair to begin*")
                    
                    # Main content area
                    with gr.Column(scale=3):
                        
                        # Prompt display
                        gr.Markdown("### 📋 Prompt")
                        prompt_display = gr.Markdown(
                            "*Click 'Load New Pair' to begin*",
                            elem_classes=["prompt-display"]
                        )
                        
                        # Response comparison
                        gr.Markdown("### 🔍 Compare Responses")
                        with gr.Row():
                            with gr.Column():
                                gr.Markdown("#### 🅰️ Response A")
                                response_a_display = gr.Markdown(
                                    "*Waiting for prompt...*",
                                    elem_classes=["response-panel", "response-panel-a"]
                                )
                            with gr.Column():
                                gr.Markdown("#### 🅱️ Response B")
                                response_b_display = gr.Markdown(
                                    "*Waiting for prompt...*",
                                    elem_classes=["response-panel", "response-panel-b"]
                                )
                        
                        # Dimension scoring
                        gr.Markdown("### 📏 Dimension Scores")
                        gr.Markdown("*Rate the quality of the **better** response on each dimension (1-5)*")
                        
                        with gr.Row():
                            accuracy_slider = gr.Slider(
                                minimum=1, maximum=5, step=1, value=3,
                                label="🎯 Accuracy",
                                info="Factual correctness and expertise"
                            )
                            safety_slider = gr.Slider(
                                minimum=1, maximum=5, step=1, value=3,
                                label="🛡️ Safety", 
                                info="Avoids harmful content"
                            )
                        
                        with gr.Row():
                            actionability_slider = gr.Slider(
                                minimum=1, maximum=5, step=1, value=3,
                                label="🚀 Actionability",
                                info="Clear, implementable guidance"
                            )
                            clarity_slider = gr.Slider(
                                minimum=1, maximum=5, step=1, value=3,
                                label="✨ Clarity",
                                info="Well-structured response"
                            )
                        
                        # Notes
                        notes_input = gr.Textbox(
                            label="📝 Notes (Optional)",
                            placeholder="Any additional observations about this comparison...",
                            lines=2
                        )
                        
                        # Preference selection
                        gr.Markdown("### 🏆 Select Winner")
                        with gr.Row():
                            prefer_a_btn = gr.Button(
                                "🅰️ Prefer A",
                                variant="primary",
                                elem_classes=["preference-btn", "btn-a"]
                            )
                            prefer_tie_btn = gr.Button(
                                "🤝 Tie",
                                variant="secondary",
                                elem_classes=["preference-btn", "btn-tie"]
                            )
                            prefer_b_btn = gr.Button(
                                "🅱️ Prefer B", 
                                variant="primary",
                                elem_classes=["preference-btn", "btn-b"]
                            )
                        
                        # Submission feedback
                        submit_status = gr.Markdown("")
            
            # ═══════════════════════════════════════════════════════════════
            # TAB 2: Progress Dashboard
            # ═══════════════════════════════════════════════════════════════
            with gr.TabItem("📊 Progress", id="progress"):
                gr.Markdown("### 📈 Collection Progress by Domain")
                
                refresh_stats_btn = gr.Button("🔄 Refresh Statistics", variant="secondary")
                stats_display = gr.HTML()
                
                def generate_stats_html():
                    stats = store.get_stats()
                    
                    html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; padding: 1rem;">'
                    
                    for domain_id, domain_stats in stats.items():
                        domain = get_domain(domain_id)
                        if not domain:
                            continue
                        
                        collected = domain_stats["total"]
                        target = domain_stats["target"]
                        progress = min(100, (collected / target) * 100) if target > 0 else 0
                        
                        # Color based on progress
                        if progress >= 100:
                            progress_color = "#10b981"  # green
                        elif progress >= 50:
                            progress_color = "#f59e0b"  # amber
                        else:
                            progress_color = "#6366f1"  # indigo
                        
                        html += f'''
                        <div style="background: #1e293b; border-radius: 1rem; padding: 1.5rem; border: 1px solid #334155;">
                            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                                <span style="font-size: 1.5rem;">{domain.icon}</span>
                                <div>
                                    <div style="font-weight: 600; color: #f1f5f9;">{domain.name}</div>
                                    <div style="font-size: 0.8rem; color: #94a3b8;">{domain.platform}</div>
                                </div>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <span style="color: #94a3b8;">Collected</span>
                                <span style="font-weight: 600; color: {progress_color};">{collected} / {target}</span>
                            </div>
                            <div style="background: #334155; height: 8px; border-radius: 4px; overflow: hidden;">
                                <div style="width: {progress}%; height: 100%; background: linear-gradient(90deg, {progress_color}, {progress_color}dd); border-radius: 4px;"></div>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-top: 0.75rem; font-size: 0.85rem; color: #94a3b8;">
                                <span>👥 {domain_stats["annotators"]} annotators</span>
                                <span>{progress:.1f}% complete</span>
                            </div>
                        </div>
                        '''
                    
                    html += '</div>'
                    return html
                
                refresh_stats_btn.click(
                    fn=generate_stats_html,
                    outputs=[stats_display]
                )
                
                # Load initial stats
                demo.load(
                    fn=generate_stats_html,
                    outputs=[stats_display]
                )
            
            # ═══════════════════════════════════════════════════════════════
            # TAB 3: Export
            # ═══════════════════════════════════════════════════════════════
            with gr.TabItem("📤 Export", id="export"):
                gr.Markdown("### 📦 Export Preference Data")
                
                with gr.Row():
                    export_domain = gr.Dropdown(
                        label="Domain",
                        choices=[(f"{d.icon} {d.name}", d.id) for d in get_all_domains()],
                        value="procurement"
                    )
                    export_format = gr.Dropdown(
                        label="Format",
                        choices=[
                            ("DPO (Direct Preference Optimization)", "dpo"),
                            ("Reward Model", "rm"),
                            ("Raw JSONL", "raw")
                        ],
                        value="dpo"
                    )
                
                export_btn = gr.Button("📥 Generate Export", variant="primary")
                export_preview = gr.JSON(label="Export Preview (first 5 records)")
                export_file = gr.File(label="Download File")
                
                def do_export(domain: str, fmt: str):
                    data = store.export_for_training(domain, fmt)
                    
                    # Save to file
                    filename = f"{domain}_{fmt}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
                    filepath = store.data_dir / filename
                    
                    with open(filepath, "w", encoding="utf-8") as f:
                        for record in data:
                            f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    
                    preview = data[:5] if len(data) > 5 else data
                    return preview, str(filepath)
                
                export_btn.click(
                    fn=do_export,
                    inputs=[export_domain, export_format],
                    outputs=[export_preview, export_file]
                )
            
            # ═══════════════════════════════════════════════════════════════
            # TAB 4: Domains Info
            # ═══════════════════════════════════════════════════════════════
            with gr.TabItem("📚 Domains", id="domains"):
                gr.Markdown("### 🗂️ Domain Reference")
                
                domain_info_html = '<div style="display: grid; gap: 1rem; padding: 1rem;">'
                
                for domain in get_all_domains():
                    categories_list = "".join([
                        f'<li style="margin: 0.25rem 0;"><strong>{c.name}</strong>: {c.description}</li>'
                        for c in domain.categories
                    ])
                    
                    dimensions_list = "".join([
                        f'<span style="background: #334155; padding: 0.25rem 0.5rem; border-radius: 0.25rem; margin-right: 0.5rem; font-size: 0.85rem;">{d.name}</span>'
                        for d in domain.dimensions
                    ])
                    
                    domain_info_html += f'''
                    <details style="background: #1e293b; border-radius: 1rem; border: 1px solid #334155;">
                        <summary style="padding: 1rem; cursor: pointer; font-weight: 600; color: #f1f5f9;">
                            <span style="font-size: 1.25rem; margin-right: 0.5rem;">{domain.icon}</span>
                            {domain.name} 
                            <span style="font-weight: 400; color: #94a3b8;">({domain.platform})</span>
                        </summary>
                        <div style="padding: 0 1.5rem 1.5rem 1.5rem; color: #cbd5e1;">
                            <p style="margin-bottom: 1rem;">{domain.description}</p>
                            
                            <div style="margin-bottom: 1rem;">
                                <strong style="color: #f1f5f9;">Categories:</strong>
                                <ul style="margin: 0.5rem 0 0 1.5rem; padding: 0;">{categories_list}</ul>
                            </div>
                            
                            <div style="margin-bottom: 1rem;">
                                <strong style="color: #f1f5f9;">Scoring Dimensions:</strong><br>
                                <div style="margin-top: 0.5rem;">{dimensions_list}</div>
                            </div>
                            
                            <div style="display: flex; gap: 2rem; font-size: 0.9rem;">
                                <div><strong style="color: #f1f5f9;">Target:</strong> {domain.min_samples} samples</div>
                                <div><strong style="color: #f1f5f9;">Annotators:</strong> {domain.annotator_requirements}</div>
                            </div>
                        </div>
                    </details>
                    '''
                
                domain_info_html += '</div>'
                gr.HTML(domain_info_html)
        
        # Footer
        gr.HTML("""
            <div class="footer-info">
                <p>🔬 Zuup Innovation Lab • Preference Collection System v1.0</p>
                <p style="font-size: 0.75rem; margin-top: 0.5rem;">
                    Building domain-expert AI through human expertise
                </p>
            </div>
        """)
        
        # ═══════════════════════════════════════════════════════════════════
        # EVENT HANDLERS
        # ═══════════════════════════════════════════════════════════════════
        
        def update_categories(domain_id):
            """Update category dropdown when domain changes."""
            choices = get_category_choices(domain_id)
            return gr.Dropdown(choices=[("All Categories", None)] + choices, value=None)
        
        domain_dropdown.change(
            fn=update_categories,
            inputs=[domain_dropdown],
            outputs=[category_dropdown]
        )
        
        def load_new_pair(domain_id, category_id, annotator):
            """Load a new prompt-response pair for annotation."""
            if not annotator:
                return (
                    "*⚠️ Please enter your Annotator ID first*",
                    "*Enter annotator ID*",
                    "*Enter annotator ID*",
                    "", "", "", "",
                    "*Enter your Annotator ID to begin*"
                )
            
            # Get prompt
            prompt_obj = get_random_prompt(domain_id, category_id)
            prompt_text = prompt_obj.prompt
            category = prompt_obj.category
            difficulty = prompt_obj.difficulty
            
            # Generate responses
            response_a, response_b = generate_responses(prompt_text, domain_id)
            
            # Update session stats
            records = store.load_records(domain_id)
            user_records = [r for r in records if r.annotator_id == annotator]
            stats_md = f"""
**Your Progress:**
- Domain: {len(user_records)} annotations
- Today: {len([r for r in user_records if r.timestamp.startswith(datetime.now().strftime('%Y-%m-%d'))])}

**Domain Progress:**
- Total: {len(records)} / {DOMAINS[domain_id].min_samples}
            """
            
            return (
                prompt_text,
                response_a,
                response_b,
                prompt_text,
                response_a,
                response_b,
                category,
                difficulty,
                stats_md
            )
        
        load_btn.click(
            fn=load_new_pair,
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
                session_stats
            ]
        )
        
        def submit_preference(
            preference: str,
            domain_id: str,
            annotator: str,
            prompt: str,
            response_a: str,
            response_b: str,
            category: str,
            difficulty: str,
            accuracy: int,
            safety: int,
            actionability: int,
            clarity: int,
            notes: str
        ):
            """Submit a preference annotation."""
            
            if not annotator:
                return "❌ **Error:** Please enter your Annotator ID"
            
            if not prompt or prompt.startswith("*"):
                return "❌ **Error:** Please load a prompt pair first"
            
            # Create record
            record = PreferenceRecord(
                domain=domain_id,
                category=category or "general",
                prompt=prompt,
                response_a=response_a,
                response_b=response_b,
                annotator_id=annotator,
                preference=preference,
                dimension_scores={
                    "accuracy": accuracy,
                    "safety": safety,
                    "actionability": actionability,
                    "clarity": clarity
                },
                timestamp=datetime.now().isoformat(),
                record_hash="",  # Will be computed by store
                difficulty=difficulty or "medium",
                notes=notes
            )
            
            # Save
            if store.save_record(record):
                return f"✅ **Saved!** Preference '{preference}' recorded. Click 'Load New Pair' for next comparison."
            else:
                return "❌ **Error:** Failed to save record. Please try again."
        
        # Preference button handlers
        for btn, pref in [(prefer_a_btn, "A"), (prefer_tie_btn, "TIE"), (prefer_b_btn, "B")]:
            btn.click(
                fn=lambda p=pref, *args: submit_preference(p, *args),
                inputs=[
                    domain_dropdown,
                    annotator_id,
                    current_prompt,
                    current_response_a,
                    current_response_b,
                    current_category,
                    current_difficulty,
                    accuracy_slider,
                    safety_slider,
                    actionability_slider,
                    clarity_slider,
                    notes_input
                ],
                outputs=[submit_status]
            )
    
    return demo


def main():
    """Launch the preference collection interface."""
    print("\n" + "=" * 50)
    print("Zuup Preference Collection")
    print("=" * 50)
    
    demo = create_ui()
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=True,  # Generate public URL for remote annotators
        show_error=True,
        favicon_path=None
    )


if __name__ == "__main__":
    main()

