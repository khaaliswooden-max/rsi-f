"""
Zuup Domain Taxonomy & Evaluation Rubrics
==========================================
Defines domain-specific categories, rubrics, and scoring criteria
for preference collection across all 10 Zuup platforms.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class DimensionWeight(Enum):
    """Weight levels for scoring dimensions per domain."""
    CRITICAL = 3
    HIGH = 2
    STANDARD = 1


@dataclass
class ScoringDimension:
    """A dimension for evaluating response quality."""
    name: str
    description: str
    weight: DimensionWeight
    anchors: Dict[int, str]  # 1-5 scale anchors


@dataclass
class Category:
    """A sub-category within a domain."""
    id: str
    name: str
    description: str
    example_tasks: List[str]


@dataclass
class Domain:
    """Complete domain definition with metadata and rubrics."""
    id: str
    name: str
    platform: str
    description: str
    icon: str
    categories: List[Category]
    dimensions: List[ScoringDimension]
    annotator_requirements: str
    min_samples: int
    color: str  # For UI theming


# ═══════════════════════════════════════════════════════════════════════════════
# SCORING DIMENSIONS (Reusable across domains)
# ═══════════════════════════════════════════════════════════════════════════════

DIMENSION_ACCURACY = ScoringDimension(
    name="accuracy",
    description="Factual correctness and domain expertise demonstrated",
    weight=DimensionWeight.CRITICAL,
    anchors={
        1: "Contains major factual errors or misconceptions",
        2: "Some inaccuracies that could mislead",
        3: "Generally accurate with minor gaps",
        4: "Accurate with good domain knowledge",
        5: "Expertly accurate, demonstrates deep expertise"
    }
)

DIMENSION_SAFETY = ScoringDimension(
    name="safety",
    description="Avoids harmful, unethical, or dangerous content",
    weight=DimensionWeight.CRITICAL,
    anchors={
        1: "Contains dangerous or harmful guidance",
        2: "Potential safety concerns present",
        3: "Safe but lacks precautionary context",
        4: "Safe with appropriate caveats",
        5: "Exemplary safety awareness and guardrails"
    }
)

DIMENSION_ACTIONABILITY = ScoringDimension(
    name="actionability",
    description="Provides clear, implementable guidance",
    weight=DimensionWeight.HIGH,
    anchors={
        1: "Vague, no clear next steps",
        2: "Somewhat actionable but unclear",
        3: "Moderately actionable guidance",
        4: "Clear, specific action items",
        5: "Immediately actionable with concrete steps"
    }
)

DIMENSION_CLARITY = ScoringDimension(
    name="clarity",
    description="Well-structured, easy to understand response",
    weight=DimensionWeight.STANDARD,
    anchors={
        1: "Confusing, poorly organized",
        2: "Somewhat unclear structure",
        3: "Adequate clarity",
        4: "Well-organized and clear",
        5: "Exceptionally clear and well-structured"
    }
)

DIMENSION_COMPLIANCE = ScoringDimension(
    name="compliance",
    description="Adherence to regulatory/legal requirements",
    weight=DimensionWeight.CRITICAL,
    anchors={
        1: "Violates regulations/standards",
        2: "Compliance gaps present",
        3: "Basic compliance awareness",
        4: "Strong regulatory alignment",
        5: "Expert compliance with citations"
    }
)

DIMENSION_TECHNICAL_DEPTH = ScoringDimension(
    name="technical_depth",
    description="Appropriate level of technical detail",
    weight=DimensionWeight.HIGH,
    anchors={
        1: "Superficial, lacks technical substance",
        2: "Limited technical depth",
        3: "Adequate technical content",
        4: "Good technical depth",
        5: "Excellent technical depth and insight"
    }
)

DIMENSION_ETHICS = ScoringDimension(
    name="ethics",
    description="Ethical considerations and responsible AI",
    weight=DimensionWeight.CRITICAL,
    anchors={
        1: "Ignores ethical implications",
        2: "Minimal ethical awareness",
        3: "Basic ethical consideration",
        4: "Strong ethical framing",
        5: "Exemplary ethical reasoning"
    }
)


# ═══════════════════════════════════════════════════════════════════════════════
# DOMAIN DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

DOMAINS: Dict[str, Domain] = {}

# ─────────────────────────────────────────────────────────────────────────────
# 1. Fed/SLED Procurement (Aureon)
# ─────────────────────────────────────────────────────────────────────────────
DOMAINS["procurement"] = Domain(
    id="procurement",
    name="Fed/SLED Procurement",
    platform="Aureon",
    description="Government contracting expertise covering FAR/DFARS regulations, RFP analysis, proposal writing, and compliance",
    icon="📋",
    color="#1e3a5f",
    categories=[
        Category(
            id="rfp_analysis",
            name="RFP Analysis",
            description="Analyzing government solicitations and requirements",
            example_tasks=[
                "Extract key requirements from this RFP",
                "Identify evaluation criteria and weights",
                "Flag compliance risks in solicitation"
            ]
        ),
        Category(
            id="proposal_writing",
            name="Proposal Writing",
            description="Technical and management proposal development",
            example_tasks=[
                "Draft technical approach section",
                "Write past performance narrative",
                "Develop staffing plan justification"
            ]
        ),
        Category(
            id="far_dfars",
            name="FAR/DFARS Interpretation",
            description="Regulatory guidance and clause interpretation",
            example_tasks=[
                "Explain implications of this FAR clause",
                "DFARS compliance requirements for CUI",
                "Small business subcontracting plan requirements"
            ]
        ),
        Category(
            id="pricing_strategy",
            name="Pricing & Cost Strategy",
            description="Cost proposal development and pricing analysis",
            example_tasks=[
                "Labor category rate justification",
                "Cost realism analysis approach",
                "CPFF vs FFP tradeoff analysis"
            ]
        )
    ],
    dimensions=[DIMENSION_ACCURACY, DIMENSION_COMPLIANCE, DIMENSION_ACTIONABILITY, DIMENSION_CLARITY],
    annotator_requirements="Government contracting experience (CO, contracts specialist, or proposal manager)",
    min_samples=500
)

# ─────────────────────────────────────────────────────────────────────────────
# 2. Biomedical GB-CI (Symbion)
# ─────────────────────────────────────────────────────────────────────────────
DOMAINS["biomedical"] = Domain(
    id="biomedical",
    name="Biomedical GB-CI",
    platform="Symbion",
    description="Gut-brain communication interface research, biosensor development, and neural-enteric system analysis",
    icon="🧬",
    color="#2d5a3d",
    categories=[
        Category(
            id="biosensor_design",
            name="Biosensor Design",
            description="Design of gut-brain interface sensors",
            example_tasks=[
                "Specify biosensor requirements for enteric signaling",
                "Material biocompatibility analysis",
                "Signal processing architecture for vagal nerve"
            ]
        ),
        Category(
            id="neural_analysis",
            name="Neural-Enteric Analysis",
            description="Analysis of gut-brain axis communication",
            example_tasks=[
                "Interpret microbiome-brain signaling data",
                "Vagus nerve stimulation protocol design",
                "Enteric nervous system mapping"
            ]
        ),
        Category(
            id="clinical_protocols",
            name="Clinical Protocols",
            description="Clinical study design and protocols",
            example_tasks=[
                "Design IRB protocol for GB-CI trial",
                "Adverse event monitoring plan",
                "Patient selection criteria"
            ]
        ),
        Category(
            id="data_interpretation",
            name="Data Interpretation",
            description="Biomedical data analysis and interpretation",
            example_tasks=[
                "Statistical analysis of biosensor readings",
                "Correlate gut signals with cognitive metrics",
                "Longitudinal biomarker tracking"
            ]
        )
    ],
    dimensions=[DIMENSION_ACCURACY, DIMENSION_SAFETY, DIMENSION_TECHNICAL_DEPTH, DIMENSION_CLARITY],
    annotator_requirements="Biomedical or neuroscience background (PhD preferred)",
    min_samples=400
)

# ─────────────────────────────────────────────────────────────────────────────
# 3. Ingestible GB-CI (Symbion HW)
# ─────────────────────────────────────────────────────────────────────────────
DOMAINS["ingestible"] = Domain(
    id="ingestible",
    name="Ingestible GB-CI",
    platform="Symbion HW",
    description="Capsule endoscopy and in-vivo sensing devices, ingestible electronics design and safety",
    icon="💊",
    color="#4a3d5c",
    categories=[
        Category(
            id="capsule_design",
            name="Capsule Design",
            description="Ingestible device hardware design",
            example_tasks=[
                "Capsule form factor optimization",
                "Power management for 72hr transit",
                "Antenna design for in-body telemetry"
            ]
        ),
        Category(
            id="invivo_sensing",
            name="In-Vivo Sensing",
            description="Sensing modalities for GI tract",
            example_tasks=[
                "pH sensing array calibration",
                "Motility pattern detection algorithm",
                "Gas composition sensing approach"
            ]
        ),
        Category(
            id="regulatory_path",
            name="Regulatory Pathway",
            description="FDA/CE regulatory strategy",
            example_tasks=[
                "510(k) predicate device analysis",
                "De novo classification strategy",
                "Clinical evidence requirements"
            ]
        ),
        Category(
            id="manufacturing",
            name="Manufacturing & QC",
            description="Production and quality control",
            example_tasks=[
                "Bioburden testing protocol",
                "Encapsulation process validation",
                "Batch release testing requirements"
            ]
        )
    ],
    dimensions=[DIMENSION_SAFETY, DIMENSION_ACCURACY, DIMENSION_COMPLIANCE, DIMENSION_TECHNICAL_DEPTH],
    annotator_requirements="Medical device or biomedical engineering experience",
    min_samples=350
)

# ─────────────────────────────────────────────────────────────────────────────
# 4. Legacy Refactoring (Relian)
# ─────────────────────────────────────────────────────────────────────────────
DOMAINS["legacy"] = Domain(
    id="legacy",
    name="Legacy Refactoring",
    platform="Relian",
    description="COBOL modernization, mainframe migration, and legacy system transformation",
    icon="🔧",
    color="#5c4a3d",
    categories=[
        Category(
            id="cobol_analysis",
            name="COBOL Analysis",
            description="Understanding and documenting COBOL systems",
            example_tasks=[
                "Parse COBOL copybook structure",
                "Document business rules from code",
                "Identify dead code and dependencies"
            ]
        ),
        Category(
            id="migration_strategy",
            name="Migration Strategy",
            description="Planning legacy system migration",
            example_tasks=[
                "Recommend migration approach (rehost/refactor/replace)",
                "Risk assessment for CICS migration",
                "Data migration strategy for VSAM files"
            ]
        ),
        Category(
            id="code_translation",
            name="Code Translation",
            description="Converting legacy code to modern languages",
            example_tasks=[
                "Translate COBOL paragraph to Java",
                "Map JCL to modern orchestration",
                "Convert CICS screens to REST APIs"
            ]
        ),
        Category(
            id="testing_validation",
            name="Testing & Validation",
            description="Ensuring migration correctness",
            example_tasks=[
                "Design test cases for COBOL migration",
                "Output comparison strategy",
                "Performance baseline methodology"
            ]
        )
    ],
    dimensions=[DIMENSION_ACCURACY, DIMENSION_TECHNICAL_DEPTH, DIMENSION_ACTIONABILITY, DIMENSION_CLARITY],
    annotator_requirements="COBOL/mainframe experience (developer or architect)",
    min_samples=300
)

# ─────────────────────────────────────────────────────────────────────────────
# 5. Autonomy OS (Veyra)
# ─────────────────────────────────────────────────────────────────────────────
DOMAINS["autonomy"] = Domain(
    id="autonomy",
    name="Autonomy OS",
    platform="Veyra",
    description="Agent systems, AI safety, autonomous decision-making, and multi-agent coordination",
    icon="🤖",
    color="#3d4a5c",
    categories=[
        Category(
            id="agent_design",
            name="Agent Architecture",
            description="Designing autonomous agent systems",
            example_tasks=[
                "Design agent goal hierarchy",
                "Specify agent communication protocol",
                "Memory and state management approach"
            ]
        ),
        Category(
            id="safety_constraints",
            name="Safety Constraints",
            description="Ensuring safe autonomous behavior",
            example_tasks=[
                "Define safety invariants for agent",
                "Design human override mechanisms",
                "Specify resource usage limits"
            ]
        ),
        Category(
            id="multi_agent",
            name="Multi-Agent Coordination",
            description="Coordinating multiple agents",
            example_tasks=[
                "Design agent negotiation protocol",
                "Resource allocation among agents",
                "Conflict resolution mechanism"
            ]
        ),
        Category(
            id="verification",
            name="Verification & Alignment",
            description="Verifying agent behavior alignment",
            example_tasks=[
                "Define alignment test suite",
                "Behavioral monitoring approach",
                "Value learning methodology"
            ]
        )
    ],
    dimensions=[DIMENSION_SAFETY, DIMENSION_ETHICS, DIMENSION_ACCURACY, DIMENSION_TECHNICAL_DEPTH],
    annotator_requirements="AI safety familiarity (researcher or practitioner)",
    min_samples=300
)

# ─────────────────────────────────────────────────────────────────────────────
# 6. Quantum Archaeology (QAWM)
# ─────────────────────────────────────────────────────────────────────────────
DOMAINS["quantum_arch"] = Domain(
    id="quantum_arch",
    name="Quantum Archaeology",
    platform="QAWM",
    description="Historical reconstruction using quantum computing, archaeological data analysis, and temporal modeling",
    icon="🏛️",
    color="#5c3d4a",
    categories=[
        Category(
            id="temporal_modeling",
            name="Temporal Modeling",
            description="Modeling historical timelines and events",
            example_tasks=[
                "Bayesian chronology construction",
                "Event sequence probability analysis",
                "Temporal uncertainty quantification"
            ]
        ),
        Category(
            id="artifact_analysis",
            name="Artifact Analysis",
            description="Analyzing archaeological artifacts",
            example_tasks=[
                "Material composition inference",
                "Provenance network reconstruction",
                "Trade route probability mapping"
            ]
        ),
        Category(
            id="quantum_algorithms",
            name="Quantum Algorithms",
            description="Quantum computing for archaeology",
            example_tasks=[
                "Design QAOA for site optimization",
                "Quantum sampling for reconstruction",
                "VQE for molecular dating"
            ]
        ),
        Category(
            id="data_integration",
            name="Data Integration",
            description="Combining heterogeneous archaeological data",
            example_tasks=[
                "Fuse stratigraphy with radiocarbon",
                "Integrate textual and material evidence",
                "Cross-site correlation analysis"
            ]
        )
    ],
    dimensions=[DIMENSION_ACCURACY, DIMENSION_TECHNICAL_DEPTH, DIMENSION_CLARITY, DIMENSION_ACTIONABILITY],
    annotator_requirements="Archaeology or quantum computing background",
    min_samples=250
)

# ─────────────────────────────────────────────────────────────────────────────
# 7. Defense World Models (Orb)
# ─────────────────────────────────────────────────────────────────────────────
DOMAINS["defense_wm"] = Domain(
    id="defense_wm",
    name="Defense World Models",
    platform="Orb",
    description="3D scene understanding, ISR applications, and geospatial intelligence modeling",
    icon="🌐",
    color="#2d3a4a",
    categories=[
        Category(
            id="scene_reconstruction",
            name="3D Scene Reconstruction",
            description="Building world models from sensor data",
            example_tasks=[
                "Multi-sensor fusion architecture",
                "NeRF optimization for aerial imagery",
                "Point cloud registration approach"
            ]
        ),
        Category(
            id="isr_analysis",
            name="ISR Analysis",
            description="Intelligence, surveillance, reconnaissance",
            example_tasks=[
                "Change detection methodology",
                "Activity pattern analysis",
                "Object identification protocol"
            ]
        ),
        Category(
            id="geospatial",
            name="Geospatial Intelligence",
            description="Location-based intelligence analysis",
            example_tasks=[
                "Terrain analysis for mobility",
                "LOC/LOS computation",
                "Pattern-of-life modeling"
            ]
        ),
        Category(
            id="simulation",
            name="Simulation & Prediction",
            description="World model simulation capabilities",
            example_tasks=[
                "Scenario generation methodology",
                "Predictive modeling approach",
                "What-if analysis framework"
            ]
        )
    ],
    dimensions=[DIMENSION_ACCURACY, DIMENSION_SAFETY, DIMENSION_TECHNICAL_DEPTH, DIMENSION_CLARITY],
    annotator_requirements="GEOINT or ISR background (analyst or engineer)",
    min_samples=300
)

# ─────────────────────────────────────────────────────────────────────────────
# 8. Halal Compliance (Civium)
# ─────────────────────────────────────────────────────────────────────────────
DOMAINS["halal"] = Domain(
    id="halal",
    name="Halal Compliance",
    platform="Civium",
    description="Halal certification, supply chain traceability, and Islamic dietary law compliance",
    icon="☪️",
    color="#1a4a3d",
    categories=[
        Category(
            id="certification",
            name="Certification Process",
            description="Halal certification requirements and process",
            example_tasks=[
                "Certification body evaluation",
                "Audit preparation checklist",
                "Non-conformance remediation"
            ]
        ),
        Category(
            id="supply_chain",
            name="Supply Chain Traceability",
            description="Tracking halal compliance through supply chain",
            example_tasks=[
                "Ingredient verification protocol",
                "Cross-contamination prevention",
                "Supplier qualification process"
            ]
        ),
        Category(
            id="ingredient_analysis",
            name="Ingredient Analysis",
            description="Analyzing ingredients for halal status",
            example_tasks=[
                "E-number halal assessment",
                "Animal-derived ingredient alternatives",
                "Processing aid evaluation"
            ]
        ),
        Category(
            id="documentation",
            name="Documentation & Records",
            description="Maintaining compliance documentation",
            example_tasks=[
                "Halal control plan development",
                "Traceability record requirements",
                "Certificate authenticity verification"
            ]
        )
    ],
    dimensions=[DIMENSION_COMPLIANCE, DIMENSION_ACCURACY, DIMENSION_CLARITY, DIMENSION_ACTIONABILITY],
    annotator_requirements="Halal certification or Islamic dietary law expertise",
    min_samples=300
)

# ─────────────────────────────────────────────────────────────────────────────
# 9. Mobile Data Center (PodX)
# ─────────────────────────────────────────────────────────────────────────────
DOMAINS["mobile_dc"] = Domain(
    id="mobile_dc",
    name="Mobile Data Center",
    platform="PodX",
    description="Edge computing, DDIL (Denied, Degraded, Intermittent, Limited) environments, tactical infrastructure",
    icon="📦",
    color="#4a4a2d",
    categories=[
        Category(
            id="edge_compute",
            name="Edge Computing",
            description="Computing at the tactical edge",
            example_tasks=[
                "Workload placement optimization",
                "Latency-aware service mesh",
                "Resource-constrained ML inference"
            ]
        ),
        Category(
            id="ddil_ops",
            name="DDIL Operations",
            description="Operating in disconnected environments",
            example_tasks=[
                "Data sync strategy for intermittent connectivity",
                "Autonomous operation protocols",
                "Reconnection reconciliation"
            ]
        ),
        Category(
            id="tactical_infra",
            name="Tactical Infrastructure",
            description="Deployable infrastructure design",
            example_tasks=[
                "Power budget optimization",
                "Environmental hardening requirements",
                "Rapid deployment checklist"
            ]
        ),
        Category(
            id="security",
            name="Security & COMSEC",
            description="Security in tactical environments",
            example_tasks=[
                "Zero-trust edge architecture",
                "Key management for disconnected ops",
                "Tamper detection mechanisms"
            ]
        )
    ],
    dimensions=[DIMENSION_ACCURACY, DIMENSION_SAFETY, DIMENSION_TECHNICAL_DEPTH, DIMENSION_ACTIONABILITY],
    annotator_requirements="Edge computing or tactical IT experience",
    min_samples=300
)

# ─────────────────────────────────────────────────────────────────────────────
# 10. HUBZone (HZ Navigator)
# ─────────────────────────────────────────────────────────────────────────────
DOMAINS["hubzone"] = Domain(
    id="hubzone",
    name="HUBZone Contracting",
    platform="HZ Navigator",
    description="HUBZone small business contracting, certification, and compliance",
    icon="🏢",
    color="#3d2d4a",
    categories=[
        Category(
            id="certification",
            name="HUBZone Certification",
            description="HUBZone program certification process",
            example_tasks=[
                "Eligibility determination",
                "Employee residence verification",
                "Principal office requirements"
            ]
        ),
        Category(
            id="contracting",
            name="Set-Aside Contracting",
            description="HUBZone set-aside opportunities",
            example_tasks=[
                "Sole-source threshold analysis",
                "Price evaluation preference calculation",
                "Subcontracting limitations"
            ]
        ),
        Category(
            id="compliance",
            name="Ongoing Compliance",
            description="Maintaining HUBZone status",
            example_tasks=[
                "Recertification requirements",
                "Employee count maintenance",
                "Redesignation period rules"
            ]
        ),
        Category(
            id="teaming",
            name="Teaming & JVs",
            description="Partnership strategies for HUBZone firms",
            example_tasks=[
                "Mentor-protégé eligibility",
                "JV performance of work rules",
                "Affiliation analysis"
            ]
        )
    ],
    dimensions=[DIMENSION_COMPLIANCE, DIMENSION_ACCURACY, DIMENSION_ACTIONABILITY, DIMENSION_CLARITY],
    annotator_requirements="SBA programs or small business contracting experience",
    min_samples=250
)


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_domain(domain_id: str) -> Optional[Domain]:
    """Get domain by ID."""
    return DOMAINS.get(domain_id)


def get_all_domains() -> List[Domain]:
    """Get all domain definitions."""
    return list(DOMAINS.values())


def get_domain_choices() -> List[tuple]:
    """Get domain choices for UI dropdown."""
    return [(f"{d.icon} {d.name} ({d.platform})", d.id) for d in DOMAINS.values()]


def get_category_choices(domain_id: str) -> List[tuple]:
    """Get category choices for a domain."""
    domain = get_domain(domain_id)
    if not domain:
        return []
    return [(c.name, c.id) for c in domain.categories]


def get_dimension_info(domain_id: str) -> List[Dict]:
    """Get scoring dimensions for a domain with full info."""
    domain = get_domain(domain_id)
    if not domain:
        return []
    return [
        {
            "name": d.name,
            "description": d.description,
            "weight": d.weight.value,
            "anchors": d.anchors
        }
        for d in domain.dimensions
    ]

