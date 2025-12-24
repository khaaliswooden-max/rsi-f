---
title: Zuup Preference Collection
emoji: 🎯
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 5.9.1
app_file: app.py
pinned: false
license: mit
short_description: Expert preference collection for AI training
---

# 🎯 Zuup Preference Collection

A beautiful Gradio interface for collecting human preference data across 10 specialized domain platforms.

## Features

- **📝 Annotation Interface**: Compare AI responses and select preferences
- **📊 Progress Dashboard**: Track collection progress by domain
- **📤 Export Tools**: Export data in DPO, Reward Model, or Raw JSONL formats
- **📚 Domain Reference**: Complete documentation of all 10 domains

## Domains

| Domain | Platform | Description |
|--------|----------|-------------|
| 📋 Fed/SLED Procurement | Aureon | Government contracting expertise |
| 🧬 Biomedical GB-CI | Symbion | Gut-brain communication research |
| 💊 Ingestible GB-CI | Symbion HW | Capsule endoscopy devices |
| 🔧 Legacy Refactoring | Relian | COBOL modernization |
| 🤖 Autonomy OS | Veyra | Agent systems & AI safety |
| 🏛️ Quantum Archaeology | QAWM | Historical reconstruction |
| 🌐 Defense World Models | Orb | 3D scene understanding |
| ☪️ Halal Compliance | Civium | Islamic dietary certification |
| 📦 Mobile Data Center | PodX | Edge computing & DDIL |
| 🏢 HUBZone Contracting | Aureon | Small business programs |

## Usage

1. Enter your Annotator ID
2. Select a domain to annotate
3. Click "Load New Pair" to get a prompt with two responses
4. Rate the responses on quality dimensions
5. Select your preference (A, B, or Tie)
6. Repeat!

## Export Formats

- **DPO**: Direct Preference Optimization format for training
- **Reward Model**: Includes dimension scores for reward modeling
- **Raw JSONL**: Complete records with all metadata

---

Built by Zuup Innovation Lab 🔬
