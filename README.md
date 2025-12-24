# Zuup Domain-Specific Preference Collection

Collect human preference data for training domain-expert AI systems across 10 Zuup platforms.

## Domains

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

## Quick Start

### 1. Open in Cursor (or any IDE with terminal)

```bash
# Open this folder in Cursor
# File → Open Folder → select zuup-preferences
```

### 2. Setup Environment

```bash
# In Cursor terminal (Ctrl+` to open)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run Collection UI

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

### 4. Collect Preferences

1. Open http://127.0.0.1:7860 in browser
2. Enter your annotator ID
3. Select domain
4. Click "Load New Pair"
5. Compare responses A vs B
6. Rate dimensions + select winner
7. Submit

## Project Structure

```
zuup-preferences/
├── domains/
│   ├── taxonomy.py          # Domain definitions & rubrics
│   └── prompt_generator.py  # Seed prompts per domain
├── collection/
│   └── app.py               # Gradio collection UI
├── preference_data/         # Collected annotations (gitignore)
│   └── {domain}_preferences.jsonl
├── requirements.txt
└── README.md
```

## Data Format

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
  "record_hash": "a1b2c3d4..."
}
```

## Export for Training

```python
from collection.app import PreferenceStore

store = PreferenceStore()
df = store.export_for_training("procurement", format="dpo")
df.to_json("procurement_dpo.jsonl", orient="records", lines=True)
```

## Adding Real Response Generation

Edit `collection/app.py`, replace placeholder responses with Ollama calls:

```python
import httpx

def generate_response(prompt: str, temperature: float = 0.3) -> str:
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
```

## Target Collection Size

| Domain | Min Samples | Annotator Requirements |
|--------|-------------|------------------------|
| Procurement | 500 | Gov contracting exp |
| Legacy | 300 | COBOL/mainframe exp |
| Defense WM | 300 | GEOINT background |
| Biomedical | 400 | Biomed/neuro |
| Autonomy | 300 | AI safety familiarity |

## License

Internal Zuup Innovation Lab use.
