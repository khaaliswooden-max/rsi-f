"""
Zuup Preference Collection - Hugging Face Spaces
=================================================
A beautiful interface for collecting human preference data.
With HF Dataset persistence and API endpoints for RSI/RSF.

ARCHITECTURE: FastAPI app with Gradio mounted as sub-app.
This ensures API routes are handled before Gradio catches them.
"""

import gradio as gr
import json
import hashlib
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import random

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Literal

# Import domain modules
from domains.taxonomy import (
    get_domain,
    get_all_domains,
    get_category_choices,
    DOMAINS,
)
from domains.prompt_generator import get_random_prompt

# HuggingFace Hub imports for persistence
try:
    from huggingface_hub import HfApi, CommitScheduler, hf_hub_download
    HF_HUB_AVAILABLE = True
except ImportError:
    HF_HUB_AVAILABLE = False
    print("⚠️ huggingface_hub not installed - persistence disabled")


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

HF_TOKEN = os.getenv("HF_TOKEN")
DATASET_REPO = os.getenv("DATASET_REPO", "zuup1/zuup-preferences")
API_KEYS = set(filter(None, os.getenv("API_KEYS", "").split(",")))
EXPORT_KEY = os.getenv("EXPORT_KEY", "")


# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
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
    response_a_model: str = "placeholder"
    response_b_model: str = "placeholder"


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STORAGE WITH HF DATASET PERSISTENCE
# ═══════════════════════════════════════════════════════════════════════════════

class PreferenceStore:
    """Manages preference data storage with HF Dataset sync."""
    
    def __init__(self):
        # Use /tmp for HF Spaces (persists across requests, syncs to dataset)
        self.data_dir = Path("/tmp/preference_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup HF Dataset sync
        self.scheduler = None
        self._setup_hf_sync()
    
    def _setup_hf_sync(self):
        """Setup automatic sync to HuggingFace Dataset."""
        if not HF_HUB_AVAILABLE:
            print("⚠️ huggingface_hub not available")
            return
            
        if not HF_TOKEN:
            print("⚠️ No HF_TOKEN - data will be lost on restart!")
            return
        
        try:
            self.scheduler = CommitScheduler(
                repo_id=DATASET_REPO,
                repo_type="dataset",
                folder_path=self.data_dir,
                path_in_repo="raw",
                every=2,  # Sync every 2 minutes
                token=HF_TOKEN,
            )
            print(f"✓ HF Dataset sync enabled: {DATASET_REPO}")
            self._pull_existing_data()
        except Exception as e:
            print(f"⚠️ HF sync disabled: {e}")
    
    def _pull_existing_data(self):
        """Pull existing data from HF Dataset on startup."""
        if not HF_TOKEN:
            return
        try:
            api = HfApi(token=HF_TOKEN)
            files = api.list_repo_files(DATASET_REPO, repo_type="dataset")
            for f in files:
                if f.startswith("raw/") and f.endswith(".jsonl"):
                    filename = f.replace("raw/", "")
                    local_path = self.data_dir / filename
                    if not local_path.exists():
                        try:
                            hf_hub_download(
                                repo_id=DATASET_REPO,
                                filename=f,
                                repo_type="dataset",
                                local_dir=self.data_dir.parent,
                                token=HF_TOKEN,
                            )
                            print(f"✓ Pulled {f}")
                        except Exception as e:
                            print(f"Could not pull {f}: {e}")
        except Exception as e:
            print(f"Could not pull existing data: {e}")
    
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
    
    def load_records(self, domain: str) -> List[dict]:
        file_path = self._get_file_path(domain)
        records = []
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            records.append(json.loads(line))
                        except:
                            pass
        return records
    
    def get_all_records(self) -> List[dict]:
        """Get all records across all domains."""
        all_records = []
        for jsonl in self.data_dir.glob("*_preferences.jsonl"):
            with open(jsonl) as f:
                for line in f:
                    if line.strip():
                        try:
                            all_records.append(json.loads(line))
                        except:
                            pass
        return all_records
    
    def export_dpo_format(self, min_confidence: float = 0.0) -> List[dict]:
        """Export in DPO training format."""
        records = self.get_all_records()
        dpo_data = []
        for r in records:
            pref = r.get("preference", "")
            if pref not in ["A", "B"]:
                continue  # Skip ties for DPO
            
            # Calculate confidence from dimension scores
            scores = r.get("dimension_scores", {})
            avg_score = sum(scores.values()) / len(scores) if scores else 3
            confidence = avg_score / 5.0
            
            if confidence < min_confidence:
                continue
            
            dpo_data.append({
                "prompt": r["prompt"],
                "chosen": r["response_a"] if pref == "A" else r["response_b"],
                "rejected": r["response_b"] if pref == "A" else r["response_a"],
                "domain": r["domain"],
                "category": r.get("category", ""),
                "dimension_scores": scores,
            })
        return dpo_data
    
    def get_stats(self) -> Dict[str, Dict]:
        stats = {}
        for domain_id in DOMAINS:
            records = self.load_records(domain_id)
            annotators = set(r.get("annotator_id", "") for r in records)
            pref_dist = {"A": 0, "B": 0, "TIE": 0}
            for r in records:
                p = r.get("preference", "")
                if p in pref_dist:
                    pref_dist[p] += 1
            stats[domain_id] = {
                "total": len(records),
                "annotators": len(annotators),
                "preference_distribution": pref_dist,
                "target": DOMAINS[domain_id].min_samples
            }
        return stats


# Initialize store
store = PreferenceStore()


# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI APP (Created FIRST, before Gradio)
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Zuup Preference Collection API",
    description="API for collecting human preferences for Zuup ecosystem RSI/RSF",
    version="1.0.0",
)


# Pydantic models for API
class PreferenceInput(BaseModel):
    domain: str
    category: str = "general"
    prompt: str
    response_a: str
    response_b: str
    preference: Literal["A", "B", "TIE"]
    annotator_id: str = "api"
    dimension_scores: dict = Field(default_factory=lambda: {
        "accuracy": 3, "safety": 3, "actionability": 3, "clarity": 3
    })
    difficulty: str = "medium"
    notes: str = ""
    response_a_model: str = ""
    response_b_model: str = ""


class ExportRequest(BaseModel):
    format: Literal["jsonl", "dpo"] = "dpo"
    min_confidence: float = 0.0
    limit: int = 10000
    domain: Optional[str] = None


# ═══════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS (Registered BEFORE Gradio mount)
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "hf_sync_enabled": store.scheduler is not None,
        "dataset_repo": DATASET_REPO if store.scheduler else None,
    }


@app.get("/api/stats")
async def api_stats():
    """Get collection statistics."""
    stats = store.get_stats()
    total = sum(s["total"] for s in stats.values())
    return {
        "total_preferences": total,
        "by_domain": stats,
    }


@app.post("/api/preferences")
async def api_submit_preference(
    pref: PreferenceInput,
    x_api_key: str = Header(default=None),
):
    """Submit a preference via API."""
    # Validate API key if configured
    if API_KEYS and x_api_key not in API_KEYS:
        raise HTTPException(401, "Invalid API key")
    
    # Validate domain
    if pref.domain not in DOMAINS:
        raise HTTPException(400, f"Invalid domain. Must be one of: {list(DOMAINS.keys())}")
    
    record = PreferenceRecord(
        domain=pref.domain,
        category=pref.category,
        prompt=pref.prompt,
        response_a=pref.response_a,
        response_b=pref.response_b,
        annotator_id=pref.annotator_id,
        preference=pref.preference,
        dimension_scores=pref.dimension_scores,
        timestamp=datetime.now().isoformat(),
        record_hash="",
        difficulty=pref.difficulty,
        notes=pref.notes,
        response_a_model=pref.response_a_model,
        response_b_model=pref.response_b_model,
    )
    
    if store.save_record(record):
        return {"status": "saved", "hash": record.record_hash}
    raise HTTPException(500, "Failed to save preference")


@app.post("/api/export")
async def api_export(
    req: ExportRequest,
    x_api_key: str = Header(...),
):
    """Export preferences for training. Requires premium API key."""
    if x_api_key != EXPORT_KEY:
        raise HTTPException(403, "Export requires premium API key")
    
    if req.format == "dpo":
        data = store.export_dpo_format(req.min_confidence)
    else:
        data = store.get_all_records()
    
    if req.domain:
        data = [d for d in data if d.get("domain") == req.domain]
    
    data = data[:req.limit]
    
    return {
        "count": len(data),
        "format": req.format,
        "data": data,
    }


@app.get("/api/domains")
async def api_domains():
    """List available domains."""
    return {
        "domains": [
            {
                "id": d.id,
                "name": d.name,
                "icon": d.icon,
                "platform": d.platform,
                "description": d.description,
                "categories": [{"id": c.id, "name": c.name} for c in d.categories],
            }
            for d in get_all_domains()
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════════
# RESPONSE GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════════════
# GRADIO UI
# ═══════════════════════════════════════════════════════════════════════════════

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
            
            # API Info Tab
            with gr.TabItem("🔌 API"):
                gr.Markdown("""
### 🔌 API Endpoints

This Space provides REST API endpoints for programmatic access:

#### Health Check
```
GET /api/health
```

#### Get Statistics
```
GET /api/stats
```

#### Submit Preference
```
POST /api/preferences
Content-Type: application/json
X-API-Key: your-api-key (optional)

{
    "domain": "procurement",
    "category": "general",
    "prompt": "Your prompt here",
    "response_a": "Response A text",
    "response_b": "Response B text",
    "preference": "A",
    "annotator_id": "api-user",
    "dimension_scores": {"accuracy": 4, "safety": 5, "actionability": 3, "clarity": 4}
}
```

#### Export Data (Premium)
```
POST /api/export
Content-Type: application/json
X-API-Key: your-export-key

{
    "format": "dpo",
    "min_confidence": 0.6,
    "limit": 1000
}
```

#### List Domains
```
GET /api/domains
```

---
**Note**: Data syncs to HuggingFace Dataset every 2 minutes.
                """)
        
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
            user_records = [r for r in records if r.get("annotator_id") == annotator]
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


# ═══════════════════════════════════════════════════════════════════════════════
# MOUNT GRADIO ON FASTAPI (AFTER API routes are defined)
# ═══════════════════════════════════════════════════════════════════════════════

# Create Gradio demo
demo = create_ui()

# Mount Gradio app onto FastAPI at root path
# This MUST come after all API route definitions
app = gr.mount_gradio_app(app, demo, path="/")


# ═══════════════════════════════════════════════════════════════════════════════
# LAUNCH
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
