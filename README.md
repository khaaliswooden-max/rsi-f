# 🎯 Zuup Preference Collection

> Collect human preference data for training domain-expert AI systems across 10 Zuup platforms.

![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)
![Gradio](https://img.shields.io/badge/UI-Gradio-orange.svg)
![License](https://img.shields.io/badge/license-Internal-red.svg)

## 📋 Domains

| Domain | Platform | Description |
|--------|----------|-------------|
| Fed/SLED Procurement | Aureon | Government contracting, FAR/DFARS |
| Biomedical GB-CI | Symbion | Gut-brain interface, biosensors |
| Ingestible GB-CI | Symbion HW | Capsule endoscopy, in-vivo |
| Legacy Refactoring | Relian | COBOL migration, mainframe |
| Autonomy OS | Veyra | Agent systems, AI safety |
| Quantum Archaeology | QAWM | Historical reconstruction |
| Defense World Models | Orb | 3D scene, ISR applications |
| Halal Compliance | Civium | Certification, supply chain |
| Mobile Data Center | PodX | Edge computing, DDIL |
| HUBZone | Aureon | Small business contracting |

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Collection UI

```bash
python collection/app.py
```

Output:
```
🎯 Zuup Preference Collection
==================================================
Local URL:  http://127.0.0.1:7860
Share URL:  https://xxxxx.gradio.live  ← Share with annotators
```

### 3. Collect Preferences

1. Open http://127.0.0.1:7860 in browser
2. Enter your annotator ID
3. Select domain
4. Click "Load New Pair"
5. Compare responses A vs B
6. Rate dimensions + select winner
7. Submit

## 📁 Project Structure

```
zuup-preferences/
├── domains/
│   ├── __init__.py
│   ├── taxonomy.py          # Domain definitions & rubrics
│   └── prompt_generator.py  # Seed prompts per domain
├── collection/
│   ├── __init__.py
│   └── app.py               # Gradio collection UI
├── preference_data/         # Collected annotations (gitignored)
│   └── {domain}_preferences.jsonl
├── requirements.txt
└── README.md
```

## 📊 Data Format

Each annotation is stored as JSONL:

```json
{
  "domain": "procurement",
  "category": "RFP_analysis",
  "prompt": "Analyze this RFP...",
  "response_a": "...",
  "response_b": "...",
  "annotator_id": "khaalis",
  "preference": "A",
  "dimension_scores": {
    "accuracy": 4,
    "safety": 5,
    "actionability": 4,
    "clarity": 3
  },
  "timestamp": "2024-12-24T...",
  "record_hash": "a1b2c3d4...",
  "difficulty": "medium",
  "notes": ""
}
```

## 📤 Export for Training

### Using Python

```python
from collection.app import PreferenceStore

store = PreferenceStore()

# Export as DPO format
dpo_data = store.export_for_training("procurement", format="dpo")

# Export as Reward Model format
rm_data = store.export_for_training("procurement", format="rm")

# Export raw
raw_data = store.export_for_training("procurement", format="raw")

# Save to file
import json
with open("procurement_dpo.jsonl", "w") as f:
    for record in dpo_data:
        f.write(json.dumps(record) + "\n")
```

### Using UI

1. Go to the "📤 Export" tab
2. Select domain and format
3. Click "Generate Export"
4. Download the file

### Export Formats

**DPO (Direct Preference Optimization):**
```json
{
  "prompt": "...",
  "chosen": "...",
  "rejected": "...",
  "domain": "procurement",
  "category": "rfp_analysis"
}
```

**Reward Model:**
```json
{
  "prompt": "...",
  "chosen": "...",
  "rejected": "...",
  "scores": {"accuracy": 4, "safety": 5, ...}
}
```

## 🔧 Adding Real Response Generation

Edit `collection/app.py`, replace the `generate_responses` function:

```python
import httpx

def generate_response(prompt: str, temperature: float = 0.3) -> str:
    """Generate response using Ollama."""
    response = httpx.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.1:8b",
            "prompt": prompt,
            "temperature": temperature,
            "stream": False
        },
        timeout=60.0
    )
    return response.json()["response"]

def generate_responses(prompt: str, domain: str) -> tuple[str, str]:
    """Generate two different responses for comparison."""
    response_a = generate_response(prompt, temperature=0.3)
    response_b = generate_response(prompt, temperature=0.7)
    return response_a, response_b
```

Or use OpenAI-compatible API:

```python
import httpx

def generate_response(prompt: str, model: str = "gpt-4") -> str:
    """Generate response using OpenAI API."""
    response = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        },
        timeout=60.0
    )
    return response.json()["choices"][0]["message"]["content"]
```

## 🎯 Target Collection Size

| Domain | Min Samples | Annotator Requirements |
|--------|-------------|----------------------|
| Procurement | 500 | Gov contracting exp |
| Legacy | 300 | COBOL/mainframe exp |
| Defense WM | 300 | GEOINT background |
| Biomedical | 400 | Biomed/neuro |
| Autonomy | 300 | AI safety familiarity |
| Ingestible | 350 | Medical device exp |
| Quantum Arch | 250 | Archaeology/QC |
| Halal | 300 | Certification exp |
| Mobile DC | 300 | Edge computing exp |
| HUBZone | 250 | SBA programs exp |

## 📏 Evaluation Dimensions

All responses are scored on 4 primary dimensions (1-5 scale):

1. **🎯 Accuracy** - Factual correctness and domain expertise
2. **🛡️ Safety** - Avoids harmful, unethical, or dangerous content  
3. **🚀 Actionability** - Provides clear, implementable guidance
4. **✨ Clarity** - Well-structured, easy to understand

Domain-specific dimensions (e.g., Compliance, Technical Depth, Ethics) are defined in `domains/taxonomy.py`.

## 🔐 Data Privacy

- Preference data is stored locally in `preference_data/`
- This directory is gitignored by default
- Do not commit annotator PII
- For production, implement proper authentication

## 🛠️ Development

### Adding a New Domain

1. Add domain definition to `domains/taxonomy.py`:

```python
DOMAINS["new_domain"] = Domain(
    id="new_domain",
    name="New Domain Name",
    platform="Platform",
    description="Description...",
    icon="🆕",
    color="#hexcolor",
    categories=[...],
    dimensions=[...],
    annotator_requirements="...",
    min_samples=300
)
```

2. Add seed prompts to `domains/prompt_generator.py`:

```python
SEED_PROMPTS["new_domain"] = [
    SeedPrompt(
        domain="new_domain",
        category="category_id",
        prompt="Your expert prompt here...",
        difficulty="medium"
    ),
    # ...more prompts
]
```

### Running Tests

```bash
# Test domain definitions
python -c "from domains import get_all_domains; print([d.name for d in get_all_domains()])"

# Test prompt generation
python -c "from domains import get_random_prompt; print(get_random_prompt('procurement'))"
```

## 📜 License

Internal Zuup Innovation Lab use only.

---

<div align="center">
  <strong>🔬 Zuup Innovation Lab</strong><br>
  <em>Building domain-expert AI through human expertise</em>
</div>

