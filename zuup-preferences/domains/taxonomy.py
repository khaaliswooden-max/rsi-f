"""
Zuup Domain Taxonomy & Evaluation Rubrics

Defines 10 specialized domains with their categories, evaluation dimensions, 
and scoring rubrics for preference data collection.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class Platform(Enum):
    """Zuup platform identifiers."""
    AUREON = "aureon"
    SYMBION = "symbion"
    SYMBION_HW = "symbion_hw"
    RELIAN = "relian"
    VEYRA = "veyra"
    QAWM = "qawm"
    ORB = "orb"
    CIVIUM = "civium"
    PODX = "podx"


@dataclass
class EvaluationDimension:
    """A scoring dimension for response evaluation."""
    name: str
    description: str
    rubric: Dict[int, str]  # Score -> description
    weight: float = 1.0


@dataclass
class Category:
    """A task category within a domain."""
    id: str
    name: str
    description: str
    example_tasks: List[str] = field(default_factory=list)


@dataclass
class Domain:
    """Complete domain definition with evaluation rubrics."""
    id: str
    name: str
    platform: Platform
    description: str
    categories: List[Category]
    dimensions: List[EvaluationDimension]
    expertise_requirements: str
    min_samples: int = 300
    
    def get_dimension_names(self) -> List[str]:
        return [d.name for d in self.dimensions]


# ============================================================================
# EVALUATION DIMENSIONS (Shared across domains with domain-specific weights)
# ============================================================================

ACCURACY = EvaluationDimension(
    name="accuracy",
    description="Factual correctness and technical precision",
    rubric={
        1: "Contains critical errors or fabrications",
        2: "Multiple inaccuracies that affect usefulness", 
        3: "Generally accurate with minor errors",
        4: "Accurate with only trivial issues",
        5: "Completely accurate and precise"
    }
)

SAFETY = EvaluationDimension(
    name="safety",
    description="Avoids harmful, dangerous, or non-compliant recommendations",
    rubric={
        1: "Dangerous or illegal recommendations",
        2: "Potentially harmful without warnings",
        3: "Safe but lacks important caveats",
        4: "Safe with appropriate warnings",
        5: "Exemplary safety awareness throughout"
    }
)

ACTIONABILITY = EvaluationDimension(
    name="actionability",
    description="Provides clear, executable next steps",
    rubric={
        1: "No actionable guidance",
        2: "Vague suggestions only",
        3: "Some actionable items but incomplete",
        4: "Clear actions with most details",
        5: "Fully actionable with complete details"
    }
)

CLARITY = EvaluationDimension(
    name="clarity",
    description="Clear, well-organized, appropriate for audience",
    rubric={
        1: "Incoherent or incomprehensible",
        2: "Confusing structure or jargon",
        3: "Understandable but could be clearer",
        4: "Clear and well-organized",
        5: "Exceptionally clear and accessible"
    }
)

DOMAIN_EXPERTISE = EvaluationDimension(
    name="domain_expertise",
    description="Demonstrates specialized knowledge of the field",
    rubric={
        1: "No domain knowledge evident",
        2: "Surface-level understanding only",
        3: "Adequate domain knowledge",
        4: "Strong domain expertise",
        5: "Expert-level mastery demonstrated"
    }
)

COMPLIANCE = EvaluationDimension(
    name="compliance",
    description="Adheres to relevant regulations and standards",
    rubric={
        1: "Violates regulations",
        2: "Ignores compliance requirements",
        3: "Mentions compliance but incomplete",
        4: "Good compliance awareness",
        5: "Comprehensive compliance coverage"
    }
)


# ============================================================================
# DOMAIN DEFINITIONS
# ============================================================================

DOMAINS: Dict[str, Domain] = {}

# ---------------------------------------------------------------------------
# 1. FED/SLED PROCUREMENT (Aureon)
# ---------------------------------------------------------------------------
DOMAINS["procurement"] = Domain(
    id="procurement",
    name="Fed/SLED Procurement",
    platform=Platform.AUREON,
    description="Government contracting expertise covering FAR/DFARS regulations, RFP analysis, proposal writing, and compliance requirements for federal, state, local, and education procurement.",
    categories=[
        Category(
            id="rfp_analysis",
            name="RFP Analysis",
            description="Analyze government RFPs to identify requirements, evaluation criteria, and compliance needs",
            example_tasks=[
                "Extract key requirements from this DoD RFP",
                "Identify compliance gaps in our proposal draft",
                "Summarize evaluation factors for this GSA opportunity"
            ]
        ),
        Category(
            id="proposal_writing",
            name="Proposal Writing",
            description="Draft and review government proposal sections",
            example_tasks=[
                "Write a technical approach section for cloud migration",
                "Draft past performance narrative for SEWP contract",
                "Create management approach for staffing augmentation"
            ]
        ),
        Category(
            id="far_dfars",
            name="FAR/DFARS Interpretation",
            description="Interpret and apply Federal Acquisition Regulations",
            example_tasks=[
                "Explain FAR 15.306 competitive range determination",
                "What DFARS clauses apply to CUI handling?",
                "Interpret organizational conflict of interest requirements"
            ]
        ),
        Category(
            id="pricing_strategy",
            name="Pricing Strategy",
            description="Develop competitive and compliant pricing strategies",
            example_tasks=[
                "Structure a T&M price proposal",
                "Calculate wrap rates for cost-plus contract",
                "Justify price reasonableness for sole source"
            ]
        ),
        Category(
            id="contract_admin",
            name="Contract Administration",
            description="Manage contract modifications, deliverables, and compliance",
            example_tasks=[
                "Draft REA for scope creep",
                "Prepare CPARS response strategy",
                "Process contract modification request"
            ]
        )
    ],
    dimensions=[ACCURACY, COMPLIANCE, ACTIONABILITY, CLARITY, DOMAIN_EXPERTISE],
    expertise_requirements="Government contracting experience: CO, CS, capture manager, or proposal manager background",
    min_samples=500
)

# ---------------------------------------------------------------------------
# 2. BIOMEDICAL GB-CI (Symbion)
# ---------------------------------------------------------------------------
DOMAINS["biomedical_gbci"] = Domain(
    id="biomedical_gbci",
    name="Biomedical GB-CI",
    platform=Platform.SYMBION,
    description="Gut-brain interface research covering biosensor technology, microbiome analysis, neural signaling pathways, and clinical trial design for GI-neurological interventions.",
    categories=[
        Category(
            id="biosensor_design",
            name="Biosensor Design",
            description="Design and optimize gut-brain interface biosensors",
            example_tasks=[
                "Propose biomarker panel for vagal nerve activity",
                "Design continuous glucose-cortisol correlation sensor",
                "Evaluate piezoelectric vs. optical sensing for gut motility"
            ]
        ),
        Category(
            id="microbiome_analysis",
            name="Microbiome Analysis",
            description="Analyze gut microbiome data and its neural correlates",
            example_tasks=[
                "Interpret 16S rRNA sequencing for depression biomarkers",
                "Design metagenomic study for anxiety-microbiome link",
                "Analyze SCFA production pathways for cognitive function"
            ]
        ),
        Category(
            id="neural_pathways",
            name="Neural Pathway Mapping",
            description="Map and analyze gut-brain neural signaling",
            example_tasks=[
                "Describe vagus nerve signaling cascade for satiety",
                "Analyze enteric nervous system modulation targets",
                "Map inflammatory cytokine effects on BBB permeability"
            ]
        ),
        Category(
            id="clinical_protocol",
            name="Clinical Protocol Design",
            description="Design clinical trials for GB-CI interventions",
            example_tasks=[
                "Design Phase 2 trial for probiotic cognitive intervention",
                "Develop outcome measures for gut-brain anxiety treatment",
                "Create safety monitoring plan for implantable gut sensor"
            ]
        )
    ],
    dimensions=[ACCURACY, SAFETY, DOMAIN_EXPERTISE, CLARITY, ACTIONABILITY],
    expertise_requirements="Biomedical/neuroscience background, familiarity with GI physiology and neural systems",
    min_samples=400
)

# ---------------------------------------------------------------------------
# 3. INGESTIBLE GB-CI (Symbion HW)
# ---------------------------------------------------------------------------
DOMAINS["ingestible_gbci"] = Domain(
    id="ingestible_gbci",
    name="Ingestible GB-CI",
    platform=Platform.SYMBION_HW,
    description="Capsule endoscopy and ingestible device engineering covering in-vivo sensing, power management, biocompatible materials, and FDA regulatory pathways.",
    categories=[
        Category(
            id="capsule_design",
            name="Capsule Engineering",
            description="Design ingestible sensing and therapeutic devices",
            example_tasks=[
                "Specify power budget for 72-hour GI transit capsule",
                "Design antenna for in-body RF communication",
                "Evaluate coating materials for targeted drug release"
            ]
        ),
        Category(
            id="in_vivo_sensing",
            name="In-Vivo Sensing",
            description="Develop sensing systems for GI tract environment",
            example_tasks=[
                "Design pH gradient mapping algorithm for capsule",
                "Specify image sensor for low-light bowel imaging",
                "Develop temperature calibration for in-vivo accuracy"
            ]
        ),
        Category(
            id="regulatory_pathway",
            name="FDA Regulatory Pathway",
            description="Navigate FDA approval for ingestible devices",
            example_tasks=[
                "Determine 510(k) vs. PMA pathway for smart pill",
                "Draft biocompatibility testing protocol per ISO 10993",
                "Prepare clinical evidence strategy for De Novo request"
            ]
        ),
        Category(
            id="manufacturing",
            name="Manufacturing & QC",
            description="Establish manufacturing and quality control processes",
            example_tasks=[
                "Design sterilization validation for ingestible capsule",
                "Specify incoming inspection criteria for sensors",
                "Create batch release testing protocol"
            ]
        )
    ],
    dimensions=[SAFETY, ACCURACY, COMPLIANCE, DOMAIN_EXPERTISE, ACTIONABILITY],
    expertise_requirements="Medical device engineering, familiarity with FDA regulations and biomedical materials",
    min_samples=300
)

# ---------------------------------------------------------------------------
# 4. LEGACY REFACTORING (Relian)
# ---------------------------------------------------------------------------
DOMAINS["legacy_refactoring"] = Domain(
    id="legacy_refactoring",
    name="Legacy Refactoring",
    platform=Platform.RELIAN,
    description="COBOL and mainframe modernization covering code analysis, migration strategies, data transformation, and hybrid cloud integration.",
    categories=[
        Category(
            id="cobol_analysis",
            name="COBOL Code Analysis",
            description="Analyze and document legacy COBOL applications",
            example_tasks=[
                "Document COBOL copybook data structures",
                "Identify dead code in batch processing module",
                "Map CICS transaction flow dependencies"
            ]
        ),
        Category(
            id="migration_strategy",
            name="Migration Strategy",
            description="Plan and execute mainframe migration projects",
            example_tasks=[
                "Compare rehost vs. refactor approach for IMS DB",
                "Design phased migration for 24/7 banking system",
                "Evaluate Microfocus vs. AWS mainframe options"
            ]
        ),
        Category(
            id="data_transformation",
            name="Data Transformation",
            description="Transform legacy data formats and structures",
            example_tasks=[
                "Convert EBCDIC packed decimal to modern format",
                "Design VSAM to PostgreSQL migration approach",
                "Handle generation data group in cloud storage"
            ]
        ),
        Category(
            id="testing_validation",
            name="Testing & Validation",
            description="Ensure functional equivalence after modernization",
            example_tasks=[
                "Design regression test strategy for batch jobs",
                "Create data validation framework for migration",
                "Develop performance baseline comparison approach"
            ]
        )
    ],
    dimensions=[ACCURACY, ACTIONABILITY, DOMAIN_EXPERTISE, CLARITY, SAFETY],
    expertise_requirements="COBOL/mainframe experience, understanding of legacy architectures and modernization patterns",
    min_samples=300
)

# ---------------------------------------------------------------------------
# 5. AUTONOMY OS (Veyra)
# ---------------------------------------------------------------------------
DOMAINS["autonomy_os"] = Domain(
    id="autonomy_os",
    name="Autonomy OS",
    platform=Platform.VEYRA,
    description="AI agent systems covering multi-agent orchestration, safety mechanisms, capability boundaries, and human oversight integration.",
    categories=[
        Category(
            id="agent_architecture",
            name="Agent Architecture",
            description="Design multi-agent systems and coordination patterns",
            example_tasks=[
                "Design agent hierarchy for research automation",
                "Implement tool-use authorization flow",
                "Create inter-agent communication protocol"
            ]
        ),
        Category(
            id="safety_mechanisms",
            name="Safety Mechanisms",
            description="Implement AI safety constraints and monitoring",
            example_tasks=[
                "Design capability boundary enforcement system",
                "Implement constitutional AI constraints",
                "Create audit logging for agent actions"
            ]
        ),
        Category(
            id="human_oversight",
            name="Human Oversight",
            description="Integrate human-in-the-loop controls",
            example_tasks=[
                "Design approval workflow for high-stakes actions",
                "Implement graceful degradation when uncertain",
                "Create escalation criteria for agent decisions"
            ]
        ),
        Category(
            id="evaluation",
            name="Agent Evaluation",
            description="Evaluate agent capabilities and alignment",
            example_tasks=[
                "Design benchmark for task decomposition ability",
                "Create red-team evaluation protocol",
                "Measure goal stability across context lengths"
            ]
        )
    ],
    dimensions=[SAFETY, ACCURACY, DOMAIN_EXPERTISE, ACTIONABILITY, CLARITY],
    expertise_requirements="AI/ML background, familiarity with AI safety concepts and agent systems",
    min_samples=300
)

# ---------------------------------------------------------------------------
# 6. QUANTUM ARCHAEOLOGY (QAWM)
# ---------------------------------------------------------------------------
DOMAINS["quantum_archaeology"] = Domain(
    id="quantum_archaeology",
    name="Quantum Archaeology",
    platform=Platform.QAWM,
    description="Historical reconstruction using computational methods, quantum-inspired optimization, pattern recognition in fragmentary evidence, and probabilistic modeling of past events.",
    categories=[
        Category(
            id="evidence_analysis",
            name="Evidence Analysis",
            description="Analyze and correlate fragmentary historical evidence",
            example_tasks=[
                "Cross-reference pottery shard patterns across sites",
                "Reconstruct trade routes from coin distribution",
                "Date structure using multi-proxy calibration"
            ]
        ),
        Category(
            id="reconstruction",
            name="Historical Reconstruction",
            description="Model past events and conditions probabilistically",
            example_tasks=[
                "Simulate population dynamics from settlement data",
                "Model climate impact on agricultural collapse",
                "Reconstruct battle sequences from archaeological finds"
            ]
        ),
        Category(
            id="pattern_recognition",
            name="Pattern Recognition",
            description="Identify patterns in historical and archaeological data",
            example_tasks=[
                "Detect cultural transmission patterns in artifacts",
                "Identify anomalous events in stratigraphic sequence",
                "Cluster writing samples for authorship attribution"
            ]
        ),
        Category(
            id="computational_methods",
            name="Computational Methods",
            description="Apply advanced algorithms to archaeological problems",
            example_tasks=[
                "Design MCMC sampler for radiocarbon calibration",
                "Implement graph-based artifact similarity network",
                "Apply optimization to site location prediction"
            ]
        )
    ],
    dimensions=[ACCURACY, DOMAIN_EXPERTISE, CLARITY, ACTIONABILITY, SAFETY],
    expertise_requirements="Archaeology/history background, computational methods familiarity",
    min_samples=300
)

# ---------------------------------------------------------------------------
# 7. DEFENSE WORLD MODELS (Orb)
# ---------------------------------------------------------------------------
DOMAINS["defense_wm"] = Domain(
    id="defense_wm",
    name="Defense World Models",
    platform=Platform.ORB,
    description="3D scene understanding for ISR applications covering geospatial analysis, multi-sensor fusion, pattern-of-life analysis, and tactical decision support.",
    categories=[
        Category(
            id="scene_understanding",
            name="3D Scene Understanding",
            description="Analyze and interpret 3D geospatial scenes",
            example_tasks=[
                "Identify structures of interest in LiDAR point cloud",
                "Fuse SAR and EO imagery for building detection",
                "Detect terrain changes between collection dates"
            ]
        ),
        Category(
            id="pattern_of_life",
            name="Pattern-of-Life Analysis",
            description="Analyze activity patterns from persistent surveillance",
            example_tasks=[
                "Identify anomalous vehicle movement patterns",
                "Establish baseline activity for compound",
                "Correlate SIGINT with observed movements"
            ]
        ),
        Category(
            id="sensor_fusion",
            name="Multi-Sensor Fusion",
            description="Integrate data from multiple collection platforms",
            example_tasks=[
                "Design fusion architecture for UAV swarm",
                "Resolve conflicting sensor observations",
                "Prioritize collection based on information gaps"
            ]
        ),
        Category(
            id="decision_support",
            name="Tactical Decision Support",
            description="Provide actionable intelligence for operations",
            example_tasks=[
                "Generate ingress route options with risk assessment",
                "Identify optimal observation positions",
                "Predict adversary response to friendly action"
            ]
        )
    ],
    dimensions=[ACCURACY, SAFETY, DOMAIN_EXPERTISE, ACTIONABILITY, CLARITY],
    expertise_requirements="GEOINT/ISR background, familiarity with defense applications and operational security",
    min_samples=300
)

# ---------------------------------------------------------------------------
# 8. HALAL COMPLIANCE (Civium)
# ---------------------------------------------------------------------------
DOMAINS["halal_compliance"] = Domain(
    id="halal_compliance",
    name="Halal Compliance",
    platform=Platform.CIVIUM,
    description="Halal certification and supply chain verification covering ingredient analysis, slaughter standards, cross-contamination prevention, and global certification body requirements.",
    categories=[
        Category(
            id="ingredient_analysis",
            name="Ingredient Analysis",
            description="Evaluate ingredient halal status and alternatives",
            example_tasks=[
                "Assess gelatin source and halal alternatives",
                "Evaluate E-number additives for halal status",
                "Analyze alcohol content in vanilla extract"
            ]
        ),
        Category(
            id="supply_chain",
            name="Supply Chain Verification",
            description="Verify and audit halal supply chains",
            example_tasks=[
                "Design supplier audit checklist for meat products",
                "Trace ingredient origin to certified source",
                "Verify logistics separation for halal shipments"
            ]
        ),
        Category(
            id="certification",
            name="Certification Management",
            description="Navigate halal certification processes globally",
            example_tasks=[
                "Compare JAKIM vs. IFANCA certification requirements",
                "Prepare documentation for MUI certification",
                "Map certification reciprocity across markets"
            ]
        ),
        Category(
            id="process_compliance",
            name="Process Compliance",
            description="Ensure manufacturing processes meet halal standards",
            example_tasks=[
                "Design production line for halal/non-halal separation",
                "Create cleaning validation for equipment sharing",
                "Develop halal control points for HACCP integration"
            ]
        )
    ],
    dimensions=[COMPLIANCE, ACCURACY, DOMAIN_EXPERTISE, ACTIONABILITY, CLARITY],
    expertise_requirements="Halal certification experience, understanding of Islamic jurisprudence (fiqh) on food",
    min_samples=300
)

# ---------------------------------------------------------------------------
# 9. MOBILE DATA CENTER (PodX)
# ---------------------------------------------------------------------------
DOMAINS["mobile_datacenter"] = Domain(
    id="mobile_datacenter",
    name="Mobile Data Center",
    platform=Platform.PODX,
    description="Edge computing for DDIL (Denied, Degraded, Intermittent, Limited) environments covering containerized infrastructure, power management, and resilient networking.",
    categories=[
        Category(
            id="infrastructure_design",
            name="Infrastructure Design",
            description="Design containerized data center solutions",
            example_tasks=[
                "Specify cooling for 50kW compute in 40C ambient",
                "Design power distribution for generator + battery",
                "Layout 20U rack for transport vibration tolerance"
            ]
        ),
        Category(
            id="edge_computing",
            name="Edge Computing Architecture",
            description="Architect compute for disconnected operations",
            example_tasks=[
                "Design K3s cluster for DDIL deployment",
                "Implement store-and-forward sync architecture",
                "Optimize ML inference for power-constrained edge"
            ]
        ),
        Category(
            id="resilient_networking",
            name="Resilient Networking",
            description="Build networks for degraded connectivity",
            example_tasks=[
                "Design mesh network with SATCOM backup",
                "Implement delay-tolerant networking protocol",
                "Create bandwidth-aware data prioritization"
            ]
        ),
        Category(
            id="operations",
            name="Field Operations",
            description="Support deployment and operations in austere conditions",
            example_tasks=[
                "Create pre-deployment checklist for pod",
                "Design monitoring for bandwidth-constrained uplink",
                "Develop troubleshooting guide for field operators"
            ]
        )
    ],
    dimensions=[ACCURACY, ACTIONABILITY, DOMAIN_EXPERTISE, SAFETY, CLARITY],
    expertise_requirements="Data center/infrastructure experience, understanding of edge computing and military/austere operations",
    min_samples=300
)

# ---------------------------------------------------------------------------
# 10. HUBZONE (Aureon)
# ---------------------------------------------------------------------------
DOMAINS["hubzone"] = Domain(
    id="hubzone",
    name="HUBZone Contracting",
    platform=Platform.AUREON,
    description="HUBZone small business contracting covering certification requirements, set-aside opportunities, compliance maintenance, and joint venture structures.",
    categories=[
        Category(
            id="certification",
            name="HUBZone Certification",
            description="Navigate HUBZone certification requirements",
            example_tasks=[
                "Evaluate principal office location eligibility",
                "Calculate 35% employee residency requirement",
                "Document ownership and control for certification"
            ]
        ),
        Category(
            id="opportunity_identification",
            name="Opportunity Identification",
            description="Find and qualify HUBZone set-aside opportunities",
            example_tasks=[
                "Identify HUBZone set-asides in target NAICS codes",
                "Evaluate price evaluation preference applicability",
                "Analyze competitive landscape for HUBZone set-aside"
            ]
        ),
        Category(
            id="compliance_maintenance",
            name="Compliance Maintenance",
            description="Maintain HUBZone certification and compliance",
            example_tasks=[
                "Prepare recertification documentation",
                "Handle employee move outside HUBZone",
                "Address map redesignation impact on certification"
            ]
        ),
        Category(
            id="joint_ventures",
            name="Joint Venture Structures",
            description="Structure HUBZone-compliant joint ventures and mentorships",
            example_tasks=[
                "Evaluate HUBZone JV population requirements",
                "Structure mentor-protégé for HUBZone firm",
                "Ensure JV meets HUBZone control requirements"
            ]
        )
    ],
    dimensions=[COMPLIANCE, ACCURACY, ACTIONABILITY, DOMAIN_EXPERTISE, CLARITY],
    expertise_requirements="Small business contracting experience, SBA regulations familiarity",
    min_samples=300
)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_domain(domain_id: str) -> Optional[Domain]:
    """Retrieve a domain by its ID."""
    return DOMAINS.get(domain_id)


def get_all_domains() -> List[Domain]:
    """Get all registered domains."""
    return list(DOMAINS.values())


def get_domain_choices() -> List[tuple]:
    """Get domain choices for UI dropdowns."""
    return [(d.name, d.id) for d in DOMAINS.values()]


def get_category_choices(domain_id: str) -> List[tuple]:
    """Get category choices for a specific domain."""
    domain = get_domain(domain_id)
    if not domain:
        return []
    return [(c.name, c.id) for c in domain.categories]


if __name__ == "__main__":
    # Quick domain overview
    print("=" * 60)
    print("ZUUP DOMAIN TAXONOMY")
    print("=" * 60)
    
    for domain_id, domain in DOMAINS.items():
        print(f"\n{domain.name} ({domain.platform.value})")
        print(f"  Categories: {len(domain.categories)}")
        print(f"  Dimensions: {', '.join(domain.get_dimension_names())}")
        print(f"  Min Samples: {domain.min_samples}")

