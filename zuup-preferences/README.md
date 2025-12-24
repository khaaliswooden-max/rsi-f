---
title: Zuup Preference Collection
emoji: 🎯
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: "4.44.0"
app_file: app.py
pinned: false
license: mit
---

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

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

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
│   ├── __init__.py           # Domain module exports
│   ├── taxonomy.py           # Domain definitions & rubrics
│   └── prompt_generator.py   # Seed prompts per domain
├── collection/
│   ├── __init__.py           # Collection module exports
│   └── app.py                # Gradio collection UI
├── preference_data/          # Collected annotations (gitignored)
│   └── {domain}_preferences.jsonl
├── requirements.txt
├── .gitignore
└── README.md
```

## Data Format

Each annotation is stored as JSONL:

```json
{
  "domain": "procurement",
  "category": "rfp_analysis",
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

### Using Python

```python
from collection.app import PreferenceStore

store = PreferenceStore()
df = store.export_for_training("procurement", format="dpo")
df.to_json("procurement_dpo.jsonl", orient="records", lines=True)
```

### Using the UI

1. Navigate to the "📤 Export" tab
2. Select domain
3. Choose format (DPO or Raw)
4. Click "Export to JSONL"

### DPO Format Output

```json
{
  "prompt": "Analyze this RFP...",
  "chosen": "Response that was preferred...",
  "rejected": "Response that was not preferred...",
  "domain": "procurement",
  "category": "rfp_analysis"
}
```

## Adding Real Response Generation

Edit `collection/app.py`, replace the `generate_responses` function with Ollama calls:

```python
import httpx

def generate_response(prompt: str, temperature: float = 0.3) -> str:
    """Generate a response using Ollama."""
    response = httpx.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.1:8b",  # or your preferred model
            "prompt": prompt,
            "temperature": temperature,
            "stream": False
        },
        timeout=60.0
    )
    return response.json()["response"]

def generate_responses(
    prompt: str,
    domain_id: str,
    use_llm: bool = True
) -> Tuple[str, str]:
    """Generate two responses for comparison."""
    if use_llm:
        # Generate with different temperatures for variety
        response_a = generate_response(prompt, temperature=0.3)
        response_b = generate_response(prompt, temperature=0.7)
        return response_a, response_b
    else:
        # Fall back to placeholders
        return _placeholder_responses(prompt, domain_id)
```

### Start Ollama

```bash
# Install Ollama first: https://ollama.ai
ollama serve  # Start the server

# In another terminal
ollama pull llama3.1:8b  # Download model
```

## Command Line Options

```bash
python collection/app.py --help

# Create public share link (for remote annotators)
python collection/app.py --share

# Custom port
python collection/app.py --port 8080

# Custom data directory
python collection/app.py --data-dir /path/to/annotations
```

## Target Collection Size

| Domain | Min Samples | Annotator Requirements |
|--------|-------------|----------------------|
| Procurement | 500 | Gov contracting exp |
| Legacy Refactoring | 300 | COBOL/mainframe exp |
| Defense WM | 300 | GEOINT background |
| Biomedical GB-CI | 400 | Biomed/neuro |
| Autonomy OS | 300 | AI safety familiarity |
| All others | 300 | Domain expertise |

## Evaluation Dimensions

All domains use these core dimensions (with domain-specific weights):

| Dimension | Description |
|-----------|-------------|
| **Accuracy** | Factual correctness and technical precision |
| **Safety** | Avoids harmful, dangerous, or non-compliant recommendations |
| **Actionability** | Provides clear, executable next steps |
| **Clarity** | Clear, well-organized, appropriate for audience |

### Scoring Rubric (1-5)

| Score | General Meaning |
|-------|-----------------|
| 1 | Critical failures, unusable |
| 2 | Significant issues |
| 3 | Acceptable, room for improvement |
| 4 | Good with minor issues |
| 5 | Excellent, exemplary |

## Quality Guidelines for Annotators

### Before Starting
- Read the domain guide in the "📚 Domain Guide" tab
- Understand the evaluation rubric for your domain
- Use a consistent annotator ID across sessions

### During Annotation
- Read both responses completely before scoring
- Consider domain-specific requirements
- Use the full scoring range (1-5)
- Add notes for edge cases or unclear comparisons
- Take breaks to avoid fatigue

### When to Mark "Tie"
- Both responses are equally good (or equally bad)
- Trade-offs make a clear preference impossible
- **Don't** use tie when you're unsure—take more time to decide

## Troubleshooting

### Import Errors
```bash
# Make sure you're in the zuup-preferences directory
cd zuup-preferences

# Ensure virtual environment is activated
venv\Scripts\activate  # Windows
```

### Port Already in Use
```bash
python collection/app.py --port 7861
```

### Gradio Not Loading
```bash
# Update Gradio
pip install --upgrade gradio
```

## Development

### Running Tests

```bash
# Test taxonomy
python domains/taxonomy.py

# Test prompt generator
python domains/prompt_generator.py
```

### Adding a New Domain

1. Add domain definition to `domains/taxonomy.py`:
```python
DOMAINS["new_domain"] = Domain(
    id="new_domain",
    name="New Domain Name",
    platform=Platform.YOUR_PLATFORM,
    description="...",
    categories=[...],
    dimensions=[...],
    expertise_requirements="...",
    min_samples=300
)
```

2. Add prompt templates to `domains/prompt_generator.py`:
```python
PROMPT_TEMPLATES["new_domain"] = {
    "category_1": [
        "Prompt template 1...",
        "Prompt template 2...",
    ],
    # ... more categories
}
```

## License

Internal Zuup Innovation Lab use.

