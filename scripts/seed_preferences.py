"""
Synthetic Seed Preference Generator
====================================
Generate synthetic preference pairs for cold-start bootstrapping.
Uses domain-specific prompt templates from taxonomy to create 
DPO-trainable preference data.

Priority Domains (target 500 each):
1. procurement - High data ease, high revenue signal
2. defense_wm - Medium data, high revenue, high readiness (Orb)
3. halal - Medium data, medium revenue

Usage:
    python scripts/seed_preferences.py --domain procurement --count 50
    python scripts/seed_preferences.py --all-priority --count 50
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path
from typing import Literal, Optional, List, Dict
from datetime import datetime

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.zuup_sdk import ZuupPreferenceClient, AsyncZuupPreferenceClient

# Load API key from environment
API_KEY = os.getenv("ZUUP_API_KEY", "")

# Try to import expanded seeds
try:
    from scripts.seed_preferences_expanded import EXPANDED_SEEDS
    HAS_EXPANDED = True
except ImportError:
    EXPANDED_SEEDS = {}
    HAS_EXPANDED = False

# ═══════════════════════════════════════════════════════════════════════════════
# DOMAIN-SPECIFIC SEED DATA
# ═══════════════════════════════════════════════════════════════════════════════

PRIORITY_DOMAINS = ["procurement", "defense_wm", "halal"]
SECONDARY_DOMAINS = ["legacy", "autonomy", "mobile_dc", "hubzone"]
EXPLORATORY_DOMAINS = ["biomedical", "ingestible", "quantum_arch"]

SEED_DATA: Dict[str, List[Dict]] = {
    # ─────────────────────────────────────────────────────────────────────────────
    # PROCUREMENT (Priority 1) - FAR/DFARS, RFP Analysis, Proposals
    # ─────────────────────────────────────────────────────────────────────────────
    "procurement": [
        {
            "category": "far_dfars",
            "prompt": "What FAR clauses apply to a firm-fixed-price IT services contract?",
            "response_a": """Key FAR clauses for FFP IT services:

**Mandatory Clauses:**
1. **FAR 52.212-4** – Contract Terms and Conditions (Commercial Products)
2. **FAR 52.212-5** – Contract Terms Required for Commercial Products
3. **FAR 52.217-8** – Option to Extend Services
4. **FAR 52.217-9** – Option to Extend the Term
5. **FAR 52.232-33** – Payment by Electronic Funds Transfer

**If DoD, add DFARS:**
- **DFARS 252.204-7012** – Safeguarding Covered Defense Information
- **DFARS 252.232-7003** – Electronic Submission of Payment Requests

**Compliance Checklist:**
- Verify CMMC level requirement (typically Level 1-2 for IT services)
- Confirm labor categories align with SCA wage determinations
- Ensure pricing is fully burdened (indirect rates applied)
- Include NAICS code verification (typically 541512 or 541519)""",
            "response_b": "You need FAR 52.212-4 and some DFARS clauses. Check the contract for details.",
            "preference": "A",
            "dimension_scores": {"accuracy": 5, "compliance": 5, "actionability": 5, "clarity": 5}
        },
        {
            "category": "rfp_analysis",
            "prompt": "How do I identify the most important evaluation factors in an RFP?",
            "response_a": """**Finding Evaluation Factors - Step by Step:**

1. **Section M Analysis** (Primary Source)
   - Look for explicit weights or relative importance statements
   - "Technical is significantly more important than price" = weight ~60/40
   - "Factors are approximately equal" = weight evenly

2. **Section L Correlation**
   - Cross-reference submission requirements with Section M
   - Page limits indicate importance (more pages = higher weight)
   - Detailed instructions signal evaluation focus

3. **Key Phrases to Flag:**
   - "Go/No-Go" or "Pass/Fail" = mandatory threshold
   - "Discriminator" = likely deciding factor
   - "Demonstrates understanding" = needs depth

4. **Red Flag Check:**
   - Misalignment between L and M often indicates amendment coming
   - Conflicting guidance = submit RFI for clarification

**Pro tip:** Build evaluation matrix mapping each M factor to L requirements.""",
            "response_b": "Read Section M of the RFP to find evaluation criteria. The factors are usually listed there.",
            "preference": "A",
            "dimension_scores": {"accuracy": 5, "compliance": 4, "actionability": 5, "clarity": 5}
        },
        {
            "category": "proposal_writing",
            "prompt": "Write an opening paragraph for a technical approach section responding to a DoD cybersecurity requirements.",
            "response_a": """[COMPANY NAME] brings mission-proven expertise to [AGENCY]'s cybersecurity requirements, combining CMMC Level 3 certified infrastructure with a staff maintaining active TS/SCI clearances and IAT Level III certifications. Our technical approach directly addresses the three core objectives outlined in the PWS: (1) zero-trust architecture implementation, (2) continuous monitoring and threat detection, and (3) incident response within 4-hour SLAs. 

We have delivered identical capabilities under contracts with [SIMILAR AGENCY] (Contract FA8XXX-XX-X-XXXX, $XXM value), achieving 99.97% system availability and a 23% reduction in security incidents over the 3-year period of performance. The following sections detail our methodology, tools, and management approach aligned to each evaluation criterion specified in Section M.""",
            "response_b": "Our company has experience in cybersecurity. We have qualified staff and good tools. We will meet all the requirements in the RFP and deliver quality results on time and within budget.",
            "preference": "A",
            "dimension_scores": {"accuracy": 4, "compliance": 5, "actionability": 4, "clarity": 5}
        },
        {
            "category": "pricing_strategy",
            "prompt": "Should I use loaded labor rates or separate ODCs for a cost-plus-fixed-fee contract?",
            "response_a": """**For CPFF contracts, generally separate ODCs from labor.** Here's why:

**Recommend: Unbundled Approach**
- Direct labor rates (without fee)
- Indirect rates applied separately (fringe, overhead, G&A)
- Fee applied to appropriate base
- ODCs listed separately (typically fee-bearing, but confirm RFP)

**Why This Works:**
1. **Audit-friendly** – DCAA prefers visibility into rate composition
2. **Flexibility** – Can adjust ODC estimates without repricing labor
3. **Competitive** – Loaded rates appear higher even if cost-equivalent
4. **Compliant** – Matches FAR 16.306 structure expectations

**Exceptions to Consider:**
- Some agencies require "fully burdened" rates for comparison
- T&M CLINs often use composite/blended rates
- Check Section L for explicit rate structure requirements

**Key:** If DCAA will audit, use accounting system structure. Don't create a rate methodology just for this proposal.""",
            "response_b": "Use loaded rates so it's simpler. Just multiply your base rate by your wrap rate.",
            "preference": "A",
            "dimension_scores": {"accuracy": 5, "compliance": 5, "actionability": 4, "clarity": 5}
        },
        {
            "category": "rfp_analysis",
            "prompt": "What does 'technically acceptable/lowest price' (TALP) mean and how should I approach it?",
            "response_a": """**TALP = Binary Technical Gate + Price Competition**

**What It Means:**
- Technical proposals rated Pass/Fail against minimum requirements
- ALL passing proposals compete on price alone
- Lowest-priced "Acceptable" wins (no best-value tradeoff)

**Strategic Implications:**
1. **Don't over-engineer** – Extra capability won't help, only costs more
2. **Map requirements exactly** – Use compliance matrix religiously
3. **Price to win** – This IS a price shootout
4. **Risk: Feature creep** – Resist urge to differentiate technically

**Proposal Approach:**
- Meet every "shall" requirement (document compliance)
- Minimize page count (less to review = less risk of "unacceptable")
- Focus effort on cost proposal accuracy
- Include ONLY mandatory certifications/clearances

**Warning Signs This May Change:**
- Very complex requirements often shift to best-value mid-procurement
- Ask in Q&A if "technical excellence" will be considered

**Bottom Line:** In TALP, the cheapest compliant solution wins. Period.""",
            "response_b": "TALP means they want the lowest price. Make sure your proposal meets the requirements and keep costs low.",
            "preference": "A",
            "dimension_scores": {"accuracy": 5, "compliance": 5, "actionability": 5, "clarity": 5}
        },
        {
            "category": "far_dfars",
            "prompt": "Explain the small business subcontracting plan requirements under FAR 19.702.",
            "response_a": """**FAR 19.702 Subcontracting Plan Requirements:**

**When Required:**
- Contracts > $750K ($1.5M for construction)
- Prime contractor is OTHER than small business
- Subcontracting opportunities exist

**Plan Must Include:**
1. **Goals** – Percentage targets for each socioeconomic category:
   - Small Business (SB)
   - Small Disadvantaged Business (SDB)
   - Women-Owned Small Business (WOSB)
   - HUBZone
   - Service-Disabled Veteran-Owned (SDVOSB)

2. **Dollar and percentage goals** for base period + options

3. **Description of efforts:**
   - How you'll identify SB sources
   - Outreach activities (matchmaking events, etc.)
   - Internal procedures for review

4. **Administrator designation** – Named individual responsible

5. **Reporting commitment** – ISR/SSR via eSRS

**Approval Process:**
- Contracting Officer reviews before award
- SBA may review if CO requests

**Non-compliance consequences:**
- Liquidated damages
- Negative past performance
- Potential termination

**Pro tip:** Even if you're small, understand this—primes need SB partners.""",
            "response_b": "Large businesses need to subcontract to small businesses. You need to set percentage goals and report on them.",
            "preference": "A",
            "dimension_scores": {"accuracy": 5, "compliance": 5, "actionability": 4, "clarity": 5}
        },
        {
            "category": "proposal_writing",
            "prompt": "How do I write a compelling Past Performance narrative?",
            "response_a": """**Past Performance Narrative Structure (PPQ Format):**

**Opening Hook (1-2 sentences):**
"Under Contract [Number] with [Agency], [Company] delivered [specific outcome] that directly mirrors the [Solicitation] requirements."

**Relevance Bridge (Paragraph 1):**
- Contract value, period of performance, contract type
- Technical scope similarities to current RFP
- Agency/mission alignment
- Team members who will transition

**Performance Story (Core – 2-3 paragraphs):**
Structure around evaluation criteria. For each:
- **Challenge faced** (complexity, constraints)
- **Actions taken** (specific methodology)
- **Results achieved** (QUANTIFY: %, $, time saved)

Example: *"Reduced system downtime from 99.5% to 99.97% availability, exceeding the SLA by 0.47% and saving the agency an estimated $2.3M in productivity costs."*

**Relevance Summary:**
- Direct mapping: "This experience demonstrates our proven capability in [Evaluation Factor X]"

**Pro Tips:**
- Match length to page limits per reference
- Include POC who will validate claims
- Use metrics the evaluator can verify
- Anticipate CPARS/PPIRS check—ensure alignment""",
            "response_b": "Write about your past work that's similar to this contract. Include the contract number, what you did, and how well you did it.",
            "preference": "A",
            "dimension_scores": {"accuracy": 4, "compliance": 4, "actionability": 5, "clarity": 5}
        },
    ],
    
    # ─────────────────────────────────────────────────────────────────────────────
    # DEFENSE WORLD MODELS (Priority 2) - 3D, ISR, Geospatial
    # ─────────────────────────────────────────────────────────────────────────────
    "defense_wm": [
        {
            "category": "scene_reconstruction",
            "prompt": "What's the best approach for multi-view 3D reconstruction from drone imagery?",
            "response_a": """**Multi-View 3D Reconstruction Pipeline for Drone Imagery:**

**1. Data Acquisition Best Practices:**
- Maintain 70-80% overlap (frontal) and 60-70% sidelap
- Capture at consistent altitude for uniform GSD
- Include oblique angles (45°) for facade detail
- GPS/IMU data critical for georeferencing

**2. Recommended Pipeline:**
```
Images → Feature Detection (SIFT/SuperPoint) 
       → Feature Matching (SuperGlue/LoFTR)
       → SfM (COLMAP/OpenMVG) → Sparse Point Cloud
       → MVS (OpenMVS/PMVS) → Dense Point Cloud
       → Meshing (Poisson/TSDF) → Textured Mesh
```

**3. Modern Alternatives (2024):**
- **3D Gaussian Splatting (3DGS):** Faster rendering, better novel views
- **NeRF variants (Instant-NGP, Nerfacto):** Good for complex scenes
- **Hybrid approaches:** SfM + neural refinement

**4. Quality Metrics:**
- Reprojection error < 1 pixel
- Point density > 100 pts/m² for urban
- Ground control points for absolute accuracy

**Key Decision:** If real-time rendering needed → 3DGS. If maximum geometric accuracy → traditional MVS + mesh.""",
            "response_b": "Use photogrammetry software like Pix4D or Agisoft. Upload your drone images and it will create a 3D model.",
            "preference": "A",
            "dimension_scores": {"accuracy": 5, "safety": 4, "technical_depth": 5, "clarity": 5}
        },
        {
            "category": "isr_analysis",
            "prompt": "How do I implement change detection between two satellite images?",
            "response_a": """**Change Detection Implementation Guide:**

**1. Preprocessing (Critical):**
```python
# Co-registration
aligned = cv2.warpPerspective(img2, H, img1.shape[:2])
# Radiometric normalization
normalized = histogram_matching(img2, reference=img1)
# Atmospheric correction if multi-temporal
```

**2. Methods by Use Case:**

**A. Pixel-Level (Fast, simple):**
- Image differencing: `diff = |img1 - img2|`
- Threshold: `changes = diff > μ + 2σ`
- Good for: Quick screening, homogeneous areas

**B. Object-Level (More robust):**
- Segment both images (SAM, watershed)
- Compare segment statistics
- Good for: Urban areas, structured changes

**C. Deep Learning (Best accuracy):**
```python
# Siamese networks or change detection transformers
model = ChangeFormer()  # or BIT, SNUNet
changes = model(img1, img2)
```

**3. Post-processing:**
- Morphological operations (remove noise)
- Minimum mapping unit filtering
- False positive reduction via texture analysis

**4. Validation:**
- Confusion matrix against ground truth
- Kappa coefficient > 0.8 for operational use
- Producer's/User's accuracy per change class

**Output:** Binary change mask + change magnitude map.""",
            "response_b": "Subtract one image from the other and look at the pixels that are different. You can use a threshold to find the changes.",
            "preference": "A",
            "dimension_scores": {"accuracy": 5, "safety": 4, "technical_depth": 5, "clarity": 5}
        },
        {
            "category": "geospatial",
            "prompt": "Explain line-of-sight (LOS) analysis for terrain and how to compute it.",
            "response_a": """**Line-of-Sight (LOS) Analysis:**

**Concept:** Determines visibility between observer and target considering terrain obstruction.

**Algorithm (Bresenham + DEM):**
```python
def compute_los(dem, observer, target, obs_height=2.0):
    \"\"\"
    dem: Digital Elevation Model (2D array)
    observer: (row, col) of observer position
    target: (row, col) of target position
    obs_height: Observer height above ground (meters)
    \"\"\"
    # Get cells along the line
    cells = bresenham_line(observer, target)
    
    obs_elev = dem[observer] + obs_height
    target_elev = dem[target]
    
    # Calculate required slope to target
    dist_to_target = euclidean_distance(observer, target)
    slope_to_target = (target_elev - obs_elev) / dist_to_target
    
    # Check each intermediate cell
    for cell in cells[1:-1]:
        cell_elev = dem[cell]
        dist = euclidean_distance(observer, cell)
        required_elev = obs_elev + slope_to_target * dist
        
        if cell_elev > required_elev:
            return False  # Obstructed
    
    return True  # Visible
```

**Viewshed Analysis (Multiple Targets):**
- Run LOS from observer to all cells in AOI
- Output: Binary raster (visible=1, hidden=0)
- Tools: GDAL, GRASS GIS `r.viewshed`, or custom GPU implementation

**Key Parameters:**
- Observer height (eye level ~1.7m, vehicle ~2.5m)
- Target height (affects visibility)
- Max range (computational limit)
- Earth curvature correction for long distances

**Applications:** Sensor placement, concealment analysis, communications planning.""",
            "response_b": "Line of sight checks if you can see from one point to another. Use GIS software to calculate it with your terrain data.",
            "preference": "A",
            "dimension_scores": {"accuracy": 5, "safety": 4, "technical_depth": 5, "clarity": 5}
        },
        {
            "category": "simulation",
            "prompt": "What's a good architecture for real-time world model updates in a defense simulation?",
            "response_a": """**Real-Time World Model Update Architecture:**

**Core Design Pattern: Event-Sourced Digital Twin**

```
┌─────────────────────────────────────────────────────────────┐
│                    Sensor Fusion Layer                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ EO/IR   │ │  SAR    │ │  AIS    │ │ SIGINT  │           │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘           │
│       └──────────┬┴───────────┴───────────┘                 │
│                  ▼                                           │
│         ┌───────────────┐                                   │
│         │ Track Fusion  │ (Multi-hypothesis tracker)        │
│         └───────┬───────┘                                   │
└─────────────────┼───────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   World State Manager                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Entity Store │  │ Terrain DB   │  │ Event Log    │       │
│  │ (Redis/Ignite)│  │ (PostGIS)    │  │ (Kafka)      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  Simulation Engine                           │
│  • Discrete event simulation (< 100ms tick)                 │
│  • Physics models for entity behavior                       │
│  • Predictive forward projection                            │
│  • What-if branching via snapshot/restore                   │
└─────────────────────────────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  Rendering/API Layer                         │
│  • CesiumJS/Unreal for 3D visualization                     │
│  • gRPC streams for downstream consumers                    │
│  • REST for async queries                                   │
└─────────────────────────────────────────────────────────────┘
```

**Key Requirements:**
1. **Sub-second latency:** Use in-memory state (Redis Cluster)
2. **Temporal queries:** "Show state at T-5min" via event replay
3. **Scalability:** Partition by geographic tile
4. **Determinism:** Same inputs → same outputs for replay

**Technologies:** Apache Kafka (events), Redis/Apache Ignite (state), PostGIS (terrain), gRPC (streaming).""",
            "response_b": "Use a database to store the world state and update it when new data comes in. Use WebSockets to push updates to the visualization.",
            "preference": "A",
            "dimension_scores": {"accuracy": 5, "safety": 5, "technical_depth": 5, "clarity": 4}
        },
        {
            "category": "scene_reconstruction",
            "prompt": "Compare 3D Gaussian Splatting vs NeRF for defense applications.",
            "response_a": """**3D Gaussian Splatting vs NeRF for Defense Use Cases:**

| Aspect | 3D Gaussian Splatting | NeRF |
|--------|----------------------|------|
| **Rendering Speed** | Real-time (100+ FPS) | Slow (seconds/frame) |
| **Training Time** | Minutes | Hours |
| **Novel Views** | Excellent | Excellent |
| **Explicit Geometry** | Yes (point cloud) | No (implicit) |
| **Memory** | Higher (stores Gaussians) | Lower (MLP weights) |
| **Editing** | Easy (manipulate Gaussians) | Difficult |

**Defense Application Recommendations:**

**Use 3DGS When:**
- Real-time visualization required (mission planning)
- Need to export geometry for CAD/BIM
- Interactive scene manipulation (what-if analysis)
- Hardware-constrained deployment (edge devices)
- Rapid iteration on new scenes

**Use NeRF When:**
- Maximum visual quality paramount
- Reflective/transparent surfaces (water, glass)
- Training time not critical
- Research/experimentation phase

**Hybrid Approach (Best of Both):**
1. Train NeRF for highest quality reconstruction
2. Convert to 3DGS for deployment (tools exist)
3. Use 3DGS for runtime rendering

**Operational Consideration:**
3DGS produces actual point data that can be exported—important for interoperability with GIS systems (convert to LAS/LAZ).""",
            "response_b": "NeRF creates better quality but is slower. Gaussian Splatting is faster. Choose based on whether you need speed or quality.",
            "preference": "A",
            "dimension_scores": {"accuracy": 5, "safety": 4, "technical_depth": 5, "clarity": 5}
        },
    ],
    
    # ─────────────────────────────────────────────────────────────────────────────
    # HALAL COMPLIANCE (Priority 3) - Certification, Supply Chain, Ingredients
    # ─────────────────────────────────────────────────────────────────────────────
    "halal": [
        {
            "category": "ingredient_analysis",
            "prompt": "Is E471 (mono- and diglycerides) halal?",
            "response_a": """**E471 (Mono- and Diglycerides) - Halal Status: DEPENDS ON SOURCE**

**What It Is:**
E471 is an emulsifier made from glycerol and fatty acids. Common in baked goods, margarine, ice cream.

**Halal Determination:**

| Source | Status | How to Verify |
|--------|--------|---------------|
| **Plant-derived** (soy, palm, sunflower) | ✅ Halal | Request COA specifying plant origin |
| **Animal-derived (halal slaughtered)** | ✅ Halal | Requires halal certificate for animal fat source |
| **Animal-derived (non-halal/pork)** | ❌ Haram | Most common in Western products |
| **Synthetic** | ✅ Halal | Rare, verify manufacturing process |

**Verification Steps:**
1. Request Material Safety Data Sheet (MSDS) or spec sheet
2. Check source declaration—"vegetable origin" is positive indicator
3. For animal-derived: require halal certificate from supplier's supplier
4. Cross-reference with certifying body's ingredient database

**Red Flags:**
- "May contain traces of animal products"
- No source declaration on spec sheet
- Supplier unwilling to provide documentation

**Certification Standards:**
- JAKIM (Malaysia): Requires plant source OR halal-certified animal
- MUI (Indonesia): Similar requirements
- IFANCA (US): Will certify plant-derived E471

**Recommendation:** When in doubt, specify plant-origin E471 in procurement specs.""",
            "response_b": "E471 can be halal or haram depending on where it comes from. Check with the manufacturer if it's from plants or animals.",
            "preference": "A",
            "dimension_scores": {"compliance": 5, "accuracy": 5, "clarity": 5, "actionability": 5}
        },
        {
            "category": "certification",
            "prompt": "What are the key steps in obtaining halal certification for a food manufacturing facility?",
            "response_a": """**Halal Certification Process for Food Manufacturing:**

**Phase 1: Preparation (4-8 weeks)**
1. **Gap Assessment**
   - Review all ingredients against halal standards
   - Identify equipment shared with non-halal products
   - Map supply chain for animal-derived inputs

2. **Documentation Prep**
   - Ingredient specifications with halal declarations
   - Supplier halal certificates (valid, recognized CB)
   - Process flow diagrams
   - Cleaning/sanitation SOPs

**Phase 2: Application (2-4 weeks)**
1. Submit application to chosen Certification Body (CB)
2. Required documents:
   - Company registration
   - Product list with formulations
   - Facility layout
   - HACCP plan
   - Supplier certificates

**Phase 3: Audit (1-2 days on-site)**
Auditor will verify:
- ✓ Ingredient storage segregation
- ✓ Production line dedication or validated cleaning
- ✓ No cross-contamination risks
- ✓ Traceability system
- ✓ Staff training records
- ✓ Halal supervisor appointment

**Phase 4: Certification (2-4 weeks)**
- Auditor report review by CB committee
- Non-conformance resolution if needed
- Certificate issuance (typically 1-2 year validity)

**Cost Estimate:**
- Application fee: $500-2,000
- Audit fee: $1,000-3,000/day
- Annual certification: $2,000-10,000 (varies by CB and scope)

**Recognized CBs:** IFANCA (US), ISWA (US), JAKIM (Malaysia), MUI (Indonesia), HFA (UK)""",
            "response_b": "Apply to a halal certification body, they will audit your facility, and if you pass you get certified. Keep your ingredients halal and avoid cross-contamination.",
            "preference": "A",
            "dimension_scores": {"compliance": 5, "accuracy": 5, "clarity": 5, "actionability": 5}
        },
        {
            "category": "supply_chain",
            "prompt": "How do I verify that my supplier's halal certificate is legitimate?",
            "response_a": """**Halal Certificate Verification Checklist:**

**1. Certificate Authenticity Check:**
```
□ Certificate number present and unique
□ Certifying body (CB) name and logo
□ CB accreditation number visible
□ Product/facility clearly identified
□ Validity dates (not expired)
□ Scope of certification specified
□ Authorized signature/stamp
□ Hologram or security feature (if applicable)
```

**2. Certifying Body Verification:**

| Recognition Level | How to Verify |
|-------------------|---------------|
| **JAKIM-recognized** | Check: halal.gov.my/content/directory |
| **MUI-recognized** | Check: halalmui.org |
| **ESMA (UAE)** | Check: esma.gov.ae |
| **GCC-recognized** | Check: GSO halal registry |

**3. Direct Verification Steps:**
1. **Contact CB directly** using website contact (not cert contact)
2. **Request verification letter** with reference to cert number
3. **Cross-reference** certificate details with CB database if public
4. **Check CB accreditation** with their accreditation body

**4. Red Flags:**
- ⚠️ CB has no web presence or verifiable address
- ⚠️ Certificate design doesn't match CB's official templates
- ⚠️ Cert covers extremely broad scope (everything halal)
- ⚠️ Supplier refuses to allow direct CB contact
- ⚠️ Price was suspiciously low for certification

**5. Ongoing Monitoring:**
- Set certificate expiry reminders
- Request updated certificates proactively
- Conduct periodic supplier audits

**Documentation to Maintain:**
- Copy of certificate
- Verification correspondence
- CB recognition evidence
- Supplier halal commitment letter""",
            "response_b": "Check if the certificate has the right dates and contact the certification body to confirm. Make sure the CB is recognized.",
            "preference": "A",
            "dimension_scores": {"compliance": 5, "accuracy": 5, "clarity": 5, "actionability": 5}
        },
        {
            "category": "certification",
            "prompt": "What are the differences between JAKIM, MUI, and IFANCA halal certifications?",
            "response_a": """**Comparison of Major Halal Certification Bodies:**

| Aspect | JAKIM (Malaysia) | MUI (Indonesia) | IFANCA (USA) |
|--------|------------------|-----------------|--------------|
| **Authority Type** | Government agency | Religious council | Non-profit |
| **Recognition** | Global gold standard | Largest Muslim market | North America primary |
| **Standards Base** | MS 1500:2019 | LPPOM MUI HAS | Follows OIC/SMIIC |
| **Strictness** | Very strict | Strict | Moderate-Strict |

**Key Differences:**

**JAKIM (Malaysia)**
- ✅ Most widely recognized globally
- ✅ Required for Malaysian import
- ❗ Strict on alcohol (0.01% limit for food)
- ❗ No stunning accepted for poultry
- 📋 Requires Malaysian-registered CB or JAKIM-recognized foreign CB

**MUI/LPPOM MUI (Indonesia)**
- ✅ Required for Indonesian market (mandatory since 2024)
- ✅ Largest halal consumer base access
- ❗ Specific audit methodology (HAS 23000)
- ❗ Product-by-product certification
- 📋 Annual on-site audit required

**IFANCA (USA)**
- ✅ Recognized in 40+ countries
- ✅ Familiar with US/Western manufacturing
- ❗ More flexible on stunning (with conditions)
- ❗ May not be accepted in Malaysia without equivalence
- 📋 Offers ingredient certification

**Mutual Recognition:**
- JAKIM maintains list of 84+ recognized foreign CBs
- MUI has separate recognition system
- Not all US CBs are recognized in SE Asia

**Recommendation by Target Market:**
- **Global/Malaysia:** JAKIM or JAKIM-recognized CB
- **Indonesia:** MUI mandatory + others for additional markets
- **North America primary:** IFANCA or ISNA
- **Multi-market:** Consider dual certification""",
            "response_b": "JAKIM is from Malaysia, MUI is from Indonesia, and IFANCA is from the USA. They all certify products as halal but have different requirements. Choose based on where you want to sell.",
            "preference": "A",
            "dimension_scores": {"compliance": 5, "accuracy": 5, "clarity": 5, "actionability": 4}
        },
        {
            "category": "supply_chain",
            "prompt": "How do I prevent cross-contamination with non-halal products in a shared facility?",
            "response_a": """**Cross-Contamination Prevention in Shared Facilities:**

**1. Physical Segregation (Preferred)**
```
Dedicated Lines:
├── Halal production area
│   ├── Dedicated equipment
│   ├── Separate storage
│   └── Controlled access
└── Non-halal production area
```

**2. Temporal Segregation (If Shared Equipment)**

**Required Protocol:**
1. **Scheduling:** Halal production FIRST after deep clean
2. **Cleaning validation:**
   - 3-step: Wash → Rinse → Sanitize
   - Visual inspection (no residue)
   - ATP swab testing (recommended)
   - Rinse water testing (for critical equipment)
3. **Documentation:**
   - Cleaning log with responsible person signature
   - Time/date stamps
   - Verification sign-off

**3. Storage Controls**
- Halal ingredients on upper shelves (prevent drip contamination)
- Physical barriers or separate rooms preferred
- Clear labeling: "HALAL ONLY" signage
- Pallet color coding system

**4. Personnel Procedures**
- Dedicated PPE for halal production
- Training on halal requirements (documented)
- Halal supervisor present during production
- Handwashing protocols between production types

**5. Documentation Requirements**
| Document | Frequency | Retention |
|----------|-----------|-----------|
| Cleaning logs | Per changeover | 3 years |
| Training records | Annual refresh | Duration + 3 years |
| Production schedule | Daily | 2 years |
| Segregation audit | Monthly | 3 years |

**6. Risk-Based Approach**
- **High risk:** Pork/alcohol → Maximum segregation
- **Medium risk:** Non-halal meat → Validated cleaning OK
- **Lower risk:** Vegetarian but non-certified → Standard cleaning

**Certification Body Expectations:**
Most CBs will accept temporal segregation with validated cleaning, but some (JAKIM) may require dedicated lines for certain product categories.""",
            "response_b": "Keep halal and non-halal products separate. Clean equipment thoroughly between production runs and train your staff on halal requirements.",
            "preference": "A",
            "dimension_scores": {"compliance": 5, "accuracy": 5, "clarity": 5, "actionability": 5}
        },
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# SUBMISSION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def submit_preference_sync(
    client: ZuupPreferenceClient,
    domain: str,
    category: str,
    prompt: str,
    response_a: str,
    response_b: str,
    preference: Literal["A", "B", "TIE"],
    dimension_scores: Dict[str, int] = None
) -> dict:
    """Submit a single preference using sync client."""
    result = client.log_preference(
        domain=domain,
        category=category,
        prompt=prompt,
        response_a=response_a,
        response_b=response_b,
        preference=preference,
        annotator_id="seed_script_v1",
        response_a_model="expert_synthetic",
        response_b_model="baseline_synthetic",
        dimension_scores=dimension_scores,
        notes="synthetic_seed_data"
    )
    return result


async def submit_preference_async(
    client: AsyncZuupPreferenceClient,
    domain: str,
    category: str,
    prompt: str,
    response_a: str,
    response_b: str,
    preference: Literal["A", "B", "TIE"],
    dimension_scores: Dict[str, int] = None
) -> dict:
    """Submit a single preference using async client."""
    result = await client.log_preference(
        domain=domain,
        prompt=prompt,
        response_a=response_a,
        response_b=response_b,
        preference=preference,
        annotator_id="seed_script_v1",
        response_a_model="expert_synthetic",
        response_b_model="baseline_synthetic",
        dimension_scores=dimension_scores,
        notes="synthetic_seed_data",
        category=category
    )
    return result


def submit_domain_seeds_sync(
    domain: str, 
    count: int = None,
    verbose: bool = True,
    api_key: str = None,
    seed_data: Dict = None
) -> List[dict]:
    """Submit seed data for a single domain (synchronous)."""
    data_source = seed_data or SEED_DATA
    if domain not in data_source:
        print(f"[ERROR] No seed data for domain: {domain}")
        return []
    
    client = ZuupPreferenceClient(api_key=api_key or API_KEY)
    seeds = data_source[domain]
    
    if count:
        seeds = seeds[:count]
    
    results = []
    for i, seed in enumerate(seeds, 1):
        result = submit_preference_sync(
            client=client,
            domain=domain,
            category=seed["category"],
            prompt=seed["prompt"],
            response_a=seed["response_a"],
            response_b=seed["response_b"],
            preference=seed["preference"],
            dimension_scores=seed.get("dimension_scores")
        )
        results.append(result)
        
        if verbose:
            status = "[OK]" if result.success else "[FAIL]"
            print(f"  [{i}/{len(seeds)}] {status} {seed['category']}: {seed['prompt'][:50]}...")
    
    return results


async def submit_domain_seeds_async(
    domain: str,
    count: int = None,
    verbose: bool = True,
    api_key: str = None,
    seed_data: Dict = None
) -> List[dict]:
    """Submit seed data for a single domain (async for speed)."""
    data_source = seed_data or SEED_DATA
    if domain not in data_source:
        print(f"[ERROR] No seed data for domain: {domain}")
        return []
    
    client = AsyncZuupPreferenceClient(api_key=api_key or API_KEY)
    seeds = data_source[domain]
    
    if count:
        seeds = seeds[:count]
    
    tasks = []
    for seed in seeds:
        task = submit_preference_async(
            client=client,
            domain=domain,
            category=seed["category"],
            prompt=seed["prompt"],
            response_a=seed["response_a"],
            response_b=seed["response_b"],
            preference=seed["preference"],
            dimension_scores=seed.get("dimension_scores")
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    if verbose:
        success = sum(1 for r in results if hasattr(r, 'success') and r.success)
        print(f"  -> {success}/{len(results)} submitted successfully")
    
    return results


def run_smoke_check(api_key: str = None) -> bool:
    """Verify API connectivity."""
    print("[SMOKE CHECK] Running smoke check...")
    client = ZuupPreferenceClient(api_key=api_key or API_KEY)
    
    try:
        # Health check
        health = client.health()
        print(f"  [OK] Health: {health}")
        
        # Stats check
        stats = client.stats()
        print(f"  [OK] Stats: {stats}")
        
        # Domains check
        domains = client.domains()
        print(f"  [OK] Domains: {list(domains.keys()) if isinstance(domains, dict) else domains}")
        
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic seed preferences")
    parser.add_argument("--domain", type=str, help="Single domain to seed")
    parser.add_argument("--all-priority", action="store_true", help="Seed all priority domains")
    parser.add_argument("--all", action="store_true", help="Seed all domains with data")
    parser.add_argument("--count", type=int, help="Limit seeds per domain")
    parser.add_argument("--smoke-check", action="store_true", help="Just verify API connectivity")
    parser.add_argument("--async-mode", action="store_true", help="Use async for faster submission")
    parser.add_argument("--list-seeds", action="store_true", help="List available seed data")
    parser.add_argument("--api-key", type=str, help="API key for authentication (or set ZUUP_API_KEY env var)")
    parser.add_argument("--include-expanded", action="store_true", help="Include expanded seed data (~30 more per domain)")
    
    args = parser.parse_args()
    
    # Merge expanded seeds if requested
    active_seeds = dict(SEED_DATA)
    if args.include_expanded and HAS_EXPANDED:
        for domain, expanded in EXPANDED_SEEDS.items():
            if domain in active_seeds:
                active_seeds[domain] = active_seeds[domain] + expanded
            else:
                active_seeds[domain] = expanded
        print("[INFO] Including expanded seed data")
    
    # List available seeds
    if args.list_seeds:
        print("=== Available Seed Data ===")
        for domain, seeds in active_seeds.items():
            priority = "[PRIORITY]" if domain in PRIORITY_DOMAINS else ""
            expanded_count = len(EXPANDED_SEEDS.get(domain, [])) if HAS_EXPANDED else 0
            base_count = len(SEED_DATA.get(domain, []))
            if args.include_expanded and expanded_count > 0:
                print(f"  {domain}: {len(seeds)} seeds ({base_count} base + {expanded_count} expanded) {priority}")
            else:
                print(f"  {domain}: {len(seeds)} seeds {priority}")
        if HAS_EXPANDED and not args.include_expanded:
            print("\n  [TIP] Use --include-expanded for +{} more seeds".format(
                sum(len(s) for s in EXPANDED_SEEDS.values())))
        return
    
    # Get API key
    api_key = args.api_key or API_KEY
    
    # Smoke check only
    if args.smoke_check:
        success = run_smoke_check(api_key)
        sys.exit(0 if success else 1)
    
    # Determine domains to process
    if args.domain:
        domains = [args.domain]
    elif args.all_priority:
        domains = PRIORITY_DOMAINS
    elif args.all:
        domains = list(SEED_DATA.keys())
    else:
        print("Specify --domain, --all-priority, --all, or --smoke-check")
        print("Use --list-seeds to see available seed data")
        return
    
    # Submit seeds
    print(f"[SEEDING] Seeding {len(domains)} domain(s)...")
    print(f"   API: https://zuup1-zuup-preference-collection.hf.space")
    print()
    
    total_success = 0
    total_failed = 0
    
    for domain in domains:
        print(f"=== {domain.upper()} ===")
        
        if args.async_mode:
            results = asyncio.run(submit_domain_seeds_async(domain, args.count, api_key=api_key, seed_data=active_seeds))
        else:
            results = submit_domain_seeds_sync(domain, args.count, api_key=api_key, seed_data=active_seeds)
        
        success = sum(1 for r in results if hasattr(r, 'success') and r.success)
        failed = len(results) - success
        total_success += success
        total_failed += failed
        print()
    
    # Summary
    print("=" * 50)
    print(f"[SUCCESS] Total submitted: {total_success}")
    if total_failed > 0:
        print(f"[FAILED] Total failed: {total_failed}")
    
    # Next steps
    print()
    print("=== Next Steps ===")
    print("   1. Verify submissions: Check API stats")
    print("   2. Generate more seeds with Claude/local LLMs")
    print("   3. Target: 500 preferences per priority domain")


if __name__ == "__main__":
    main()

