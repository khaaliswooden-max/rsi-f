# domains/taxonomy.py — Domain definitions and quality criteria
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict


class DomainID(Enum):
    FED_SLED_PROCUREMENT = "procurement"
    BIOMEDICAL_GBCI = "gbci"
    LEGACY_REFACTORING = "legacy"
    AUTONOMY_OS = "autonomy"
    QUANTUM_ARCHAEOLOGY = "qawm"
    DEFENSE_WORLD_MODELS = "defense_wm"
    HALAL_COMPLIANCE = "halal"
    MOBILE_DATA_CENTER = "podx"
    HUBZONE = "hubzone"
    INGESTIBLE_GBCI = "ingestible"


@dataclass
class QualityDimension:
    name: str
    description: str
    weight: float  # 0.0-1.0, must sum to 1.0 across dimensions
    examples_good: List[str]
    examples_bad: List[str]


@dataclass
class DomainSpec:
    id: DomainID
    name: str
    description: str
    zuup_platform: str  # Which Zuup platform this maps to
    
    # Quality criteria
    dimensions: List[QualityDimension]
    
    # Safety & compliance
    safety_considerations: List[str]
    compliance_frameworks: List[str]
    
    # Annotation requirements
    required_expertise: List[str]
    min_annotator_agreement: float  # Krippendorff's alpha threshold
    
    # Prompt categories
    prompt_categories: List[str]
    
    # Domain-specific terminology
    key_terms: Dict[str, str] = field(default_factory=dict)


# === Domain Specifications ===

DOMAINS: Dict[DomainID, DomainSpec] = {
    
    DomainID.FED_SLED_PROCUREMENT: DomainSpec(
        id=DomainID.FED_SLED_PROCUREMENT,
        name="Federal/SLED Procurement",
        description="Government procurement, contracting, FAR/DFARS compliance, proposal writing, and acquisition strategy.",
        zuup_platform="Aureon",
        dimensions=[
            QualityDimension(
                name="regulatory_accuracy",
                description="Correct citation and interpretation of FAR/DFARS, CJIS, FedRAMP requirements",
                weight=0.30,
                examples_good=["Correctly cites FAR 15.306 for competitive range determination"],
                examples_bad=["Vague reference to 'federal regulations' without specifics"]
            ),
            QualityDimension(
                name="actionability",
                description="Provides concrete, implementable steps for procurement actions",
                weight=0.25,
                examples_good=["Step-by-step RFP response checklist with deadlines"],
                examples_bad=["Generic advice to 'review the solicitation carefully'"]
            ),
            QualityDimension(
                name="traceability",
                description="Maintains clear audit trail and decision rationale",
                weight=0.20,
                examples_good=["Documents evaluation criteria mapping to PWS requirements"],
                examples_bad=["Scores proposals without explaining methodology"]
            ),
            QualityDimension(
                name="risk_awareness",
                description="Identifies compliance risks, protest grounds, and mitigation strategies",
                weight=0.15,
                examples_good=["Flags OCI concerns with specific mitigation plan"],
                examples_bad=["Ignores potential bid protest vulnerabilities"]
            ),
            QualityDimension(
                name="clarity",
                description="Clear, professional communication suitable for government audiences",
                weight=0.10,
                examples_good=["Structured proposal section with clear headers"],
                examples_bad=["Jargon-heavy text without definitions"]
            ),
        ],
        safety_considerations=[
            "No disclosure of procurement-sensitive information",
            "No advice that could constitute bid-rigging",
            "No circumvention of competition requirements",
            "Protect source selection information"
        ],
        compliance_frameworks=["FAR", "DFARS", "CJIS", "FedRAMP", "CMMC", "Section 508"],
        required_expertise=["Government contracting experience", "FAR/DFARS familiarity"],
        min_annotator_agreement=0.7,
        prompt_categories=[
            "RFP_analysis", "proposal_writing", "pricing_strategy", 
            "compliance_check", "protest_risk", "teaming_agreements",
            "past_performance", "capability_statements", "CPARS_response"
        ],
        key_terms={
            "PWS": "Performance Work Statement",
            "LPTA": "Lowest Price Technically Acceptable",
            "OCI": "Organizational Conflict of Interest",
            "CPARS": "Contractor Performance Assessment Reporting System"
        }
    ),
    
    DomainID.BIOMEDICAL_GBCI: DomainSpec(
        id=DomainID.BIOMEDICAL_GBCI,
        name="Gut-Brain Computer Interface (External)",
        description="Biosensor systems, gut microbiome analysis, neural signal processing, and brain-gut axis research.",
        zuup_platform="Symbion",
        dimensions=[
            QualityDimension(
                name="scientific_accuracy",
                description="Correct understanding of gut-brain axis physiology, microbiome science",
                weight=0.30,
                examples_good=["Accurate description of vagal afferent signaling pathways"],
                examples_bad=["Conflates correlation with causation in microbiome studies"]
            ),
            QualityDimension(
                name="safety_primacy",
                description="Prioritizes patient/user safety, acknowledges limitations",
                weight=0.25,
                examples_good=["Recommends physician consultation before intervention"],
                examples_bad=["Suggests unvalidated treatments without disclaimers"]
            ),
            QualityDimension(
                name="technical_rigor",
                description="Correct signal processing, biosensor engineering principles",
                weight=0.20,
                examples_good=["Proper SNR calculations for biosensor specifications"],
                examples_bad=["Ignores noise floor in sensitivity claims"]
            ),
            QualityDimension(
                name="regulatory_awareness",
                description="Understands FDA pathways, IRB requirements, HIPAA constraints",
                weight=0.15,
                examples_good=["Identifies 510(k) predicate device strategy"],
                examples_bad=["Ignores medical device classification requirements"]
            ),
            QualityDimension(
                name="ethical_grounding",
                description="Addresses informed consent, data privacy, vulnerable populations",
                weight=0.10,
                examples_good=["Discusses consent protocols for cognitive research"],
                examples_bad=["No mention of data governance for health data"]
            ),
        ],
        safety_considerations=[
            "No medical advice without appropriate disclaimers",
            "No claims of FDA approval without evidence",
            "Acknowledge research vs clinical evidence distinction",
            "Protect PHI in all examples",
            "No promotion of unvalidated interventions"
        ],
        compliance_frameworks=["FDA 21 CFR", "HIPAA", "IRB/Common Rule", "GDPR (health data)", "ISO 13485"],
        required_expertise=["Biomedical engineering", "Neuroscience background", "Regulatory familiarity"],
        min_annotator_agreement=0.75,
        prompt_categories=[
            "signal_processing", "microbiome_analysis", "biosensor_design",
            "clinical_study_design", "regulatory_pathway", "data_architecture",
            "neural_decoding", "intervention_protocols"
        ],
        key_terms={
            "ENS": "Enteric Nervous System",
            "SCFAs": "Short-Chain Fatty Acids",
            "HRV": "Heart Rate Variability",
            "EGG": "Electrogastrography"
        }
    ),
    
    DomainID.INGESTIBLE_GBCI: DomainSpec(
        id=DomainID.INGESTIBLE_GBCI,
        name="Ingestible Gut-Brain Interface",
        description="Ingestible biosensors, capsule endoscopy, in-vivo diagnostics, and wireless telemetry.",
        zuup_platform="Symbion (Hardware)",
        dimensions=[
            QualityDimension(
                name="biocompatibility",
                description="Materials safety, degradation pathways, toxicity considerations",
                weight=0.25,
                examples_good=["Specifies USP Class VI materials for encapsulation"],
                examples_bad=["Ignores GI transit variability in design"]
            ),
            QualityDimension(
                name="engineering_feasibility",
                description="Realistic power budgets, form factors, telemetry constraints",
                weight=0.25,
                examples_good=["Calculates RF link budget for in-body transmission"],
                examples_bad=["Assumes unlimited battery life in capsule form"]
            ),
            QualityDimension(
                name="clinical_validity",
                description="Correlation with gold-standard diagnostics, clinical utility",
                weight=0.20,
                examples_good=["Validates against colonoscopy findings"],
                examples_bad=["Claims diagnostic accuracy without clinical trial data"]
            ),
            QualityDimension(
                name="regulatory_pathway",
                description="Clear FDA classification, predicate strategy, clinical evidence requirements",
                weight=0.20,
                examples_good=["Maps to PillCam as predicate for 510(k)"],
                examples_bad=["Ignores De Novo pathway for novel devices"]
            ),
            QualityDimension(
                name="safety_engineering",
                description="Failure modes, retention protocols, emergency procedures",
                weight=0.10,
                examples_good=["Defines capsule retention management protocol"],
                examples_bad=["No consideration of obstruction scenarios"]
            ),
        ],
        safety_considerations=[
            "Capsule retention/obstruction protocols mandatory",
            "Biocompatibility testing requirements",
            "Wireless emission limits (SAR)",
            "Contraindications for GI pathology",
            "No pediatric use without specific validation"
        ],
        compliance_frameworks=["FDA 21 CFR 876", "IEC 60601", "ISO 10993", "FCC Part 95"],
        required_expertise=["Medical device engineering", "GI physiology", "RF engineering"],
        min_annotator_agreement=0.8,
        prompt_categories=[
            "capsule_design", "power_systems", "telemetry", "biocompatibility",
            "clinical_validation", "manufacturing", "regulatory_submission"
        ],
        key_terms={
            "GITT": "GI Transit Time",
            "WCE": "Wireless Capsule Endoscopy",
            "MICS": "Medical Implant Communication Service"
        }
    ),
    
    DomainID.LEGACY_REFACTORING: DomainSpec(
        id=DomainID.LEGACY_REFACTORING,
        name="Legacy System Refactoring",
        description="COBOL migration, mainframe modernization, strangler pattern implementation, and technical debt reduction.",
        zuup_platform="Relian",
        dimensions=[
            QualityDimension(
                name="correctness_preservation",
                description="Maintains functional equivalence with legacy system",
                weight=0.30,
                examples_good=["Characterization tests verify behavior parity"],
                examples_bad=["Assumes modern code 'should work the same'"]
            ),
            QualityDimension(
                name="risk_mitigation",
                description="Incremental migration, rollback strategies, blast radius containment",
                weight=0.25,
                examples_good=["Implements strangler fig with feature flags"],
                examples_bad=["Big-bang migration with no fallback"]
            ),
            QualityDimension(
                name="technical_accuracy",
                description="Correct understanding of COBOL, JCL, VSAM, CICS, IMS",
                weight=0.20,
                examples_good=["Handles COBOL COMP-3 packed decimal correctly"],
                examples_bad=["Ignores EBCDIC encoding issues"]
            ),
            QualityDimension(
                name="business_continuity",
                description="Maintains operations during migration, handles batch windows",
                weight=0.15,
                examples_good=["Parallel run strategy with reconciliation"],
                examples_bad=["Requires production downtime for cutover"]
            ),
            QualityDimension(
                name="documentation",
                description="Captures tribal knowledge, maps business rules",
                weight=0.10,
                examples_good=["Documents undocumented COPYBOOK business logic"],
                examples_bad=["Assumes self-documenting code"]
            ),
        ],
        safety_considerations=[
            "Production data protection during migration",
            "Audit trail continuity across systems",
            "Compliance evidence preservation",
            "No loss of business logic"
        ],
        compliance_frameworks=["SOX", "PCI-DSS", "GLBA", "HIPAA (if healthcare)"],
        required_expertise=["COBOL experience", "Mainframe operations", "Modern architecture"],
        min_annotator_agreement=0.7,
        prompt_categories=[
            "code_translation", "data_migration", "testing_strategy",
            "strangler_pattern", "batch_modernization", "API_wrapping",
            "performance_parity", "knowledge_capture"
        ],
        key_terms={
            "COPYBOOK": "COBOL data structure definition",
            "JCL": "Job Control Language",
            "VSAM": "Virtual Storage Access Method",
            "CICS": "Customer Information Control System"
        }
    ),
    
    DomainID.AUTONOMY_OS: DomainSpec(
        id=DomainID.AUTONOMY_OS,
        name="Autonomy OS / Post-ASI LLM",
        description="Autonomous agent systems, tool use safety, multi-agent coordination, and post-superintelligence architectures.",
        zuup_platform="Veyra",
        dimensions=[
            QualityDimension(
                name="safety_alignment",
                description="Proper constraints, human oversight, corrigibility",
                weight=0.30,
                examples_good=["Implements approval gates for high-impact actions"],
                examples_bad=["Autonomous execution without human checkpoints"]
            ),
            QualityDimension(
                name="capability_grounding",
                description="Realistic assessment of current vs speculative capabilities",
                weight=0.25,
                examples_good=["Clearly labels TRL for each capability claim"],
                examples_bad=["Conflates research concepts with production readiness"]
            ),
            QualityDimension(
                name="tool_safety",
                description="Proper sandboxing, permission models, rollback mechanisms",
                weight=0.20,
                examples_good=["Defines tool permission matrix with escalation"],
                examples_bad=["Gives agents unrestricted filesystem access"]
            ),
            QualityDimension(
                name="coordination_correctness",
                description="Multi-agent consensus, conflict resolution, resource management",
                weight=0.15,
                examples_good=["Implements Byzantine fault tolerance for agent voting"],
                examples_bad=["Assumes agents always agree"]
            ),
            QualityDimension(
                name="interpretability",
                description="Explainable decisions, audit trails, reasoning transparency",
                weight=0.10,
                examples_good=["Logs full reasoning chain for each action"],
                examples_bad=["Black-box decision making"]
            ),
        ],
        safety_considerations=[
            "Human-in-the-loop for consequential decisions",
            "Containment strategies for capability overhang",
            "No self-modification without approval",
            "Shutdown/rollback always available",
            "Distinguish speculation from engineering"
        ],
        compliance_frameworks=["NIST AI RMF", "EU AI Act (high-risk)", "DoD AI Ethics"],
        required_expertise=["AI safety research", "Distributed systems", "Agent architectures"],
        min_annotator_agreement=0.75,
        prompt_categories=[
            "agent_design", "tool_permissions", "multi_agent_coord",
            "safety_constraints", "capability_assessment", "deployment_strategy",
            "failure_modes", "alignment_verification"
        ],
        key_terms={
            "HITL": "Human-in-the-Loop",
            "TRL": "Technology Readiness Level",
            "Corrigibility": "Ability to be corrected/shut down"
        }
    ),
    
    DomainID.QUANTUM_ARCHAEOLOGY: DomainSpec(
        id=DomainID.QUANTUM_ARCHAEOLOGY,
        name="Quantum Archaeological World Models",
        description="Historical event reconstruction, evidence synthesis, uncertainty quantification, and temporal reasoning.",
        zuup_platform="QAWM / QAL",
        dimensions=[
            QualityDimension(
                name="evidential_rigor",
                description="Proper source citation, evidence weighting, provenance tracking",
                weight=0.30,
                examples_good=["Weights primary sources over secondary interpretations"],
                examples_bad=["Treats Wikipedia as primary evidence"]
            ),
            QualityDimension(
                name="uncertainty_quantification",
                description="Explicit confidence intervals, alternative hypotheses",
                weight=0.25,
                examples_good=["Reports reconstruction with 95% CI and alternatives"],
                examples_bad=["Presents single interpretation as fact"]
            ),
            QualityDimension(
                name="temporal_reasoning",
                description="Correct handling of chronology, causation, anachronism detection",
                weight=0.20,
                examples_good=["Flags anachronistic elements in source material"],
                examples_bad=["Ignores temporal inconsistencies"]
            ),
            QualityDimension(
                name="methodological_transparency",
                description="Clear description of reconstruction methodology",
                weight=0.15,
                examples_good=["Documents Bayesian update process for beliefs"],
                examples_bad=["Presents conclusions without methodology"]
            ),
            QualityDimension(
                name="simulation_validity",
                description="Realistic constraints on reconstructions, physics/economics grounding",
                weight=0.10,
                examples_good=["Validates against known logistical constraints"],
                examples_bad=["Ignores material/resource limitations of era"]
            ),
        ],
        safety_considerations=[
            "No falsification of historical record",
            "Acknowledge political sensitivities",
            "Distinguish reconstruction from fabrication",
            "Respect cultural heritage considerations"
        ],
        compliance_frameworks=["Academic integrity standards", "NAGPRA (if indigenous)", "UNESCO heritage"],
        required_expertise=["Historical methodology", "Bayesian reasoning", "Domain history"],
        min_annotator_agreement=0.65,
        prompt_categories=[
            "event_reconstruction", "source_analysis", "timeline_synthesis",
            "counterfactual_analysis", "evidence_weighting", "visualization",
            "uncertainty_modeling", "cross_reference"
        ],
        key_terms={
            "Provenance": "Chain of custody/origin of evidence",
            "Terminus post quem": "Earliest possible date",
            "Terminus ante quem": "Latest possible date"
        }
    ),
    
    DomainID.DEFENSE_WORLD_MODELS: DomainSpec(
        id=DomainID.DEFENSE_WORLD_MODELS,
        name="Defense World Models",
        description="3D scene understanding, spatial intelligence, ISR applications, and tactical decision support.",
        zuup_platform="Orb",
        dimensions=[
            QualityDimension(
                name="spatial_accuracy",
                description="Correct 3D reconstruction, geospatial reasoning, coordinate systems",
                weight=0.25,
                examples_good=["Proper MGRS/UTM coordinate handling"],
                examples_bad=["Ignores datum/projection errors"]
            ),
            QualityDimension(
                name="operational_relevance",
                description="Actionable intelligence, mission-aligned outputs",
                weight=0.25,
                examples_good=["Identifies tactically significant terrain features"],
                examples_bad=["Generic scene description without operational context"]
            ),
            QualityDimension(
                name="uncertainty_communication",
                description="Confidence levels, sensor limitations, fusion caveats",
                weight=0.20,
                examples_good=["Reports reconstruction confidence per region"],
                examples_bad=["Presents all outputs as equally reliable"]
            ),
            QualityDimension(
                name="security_awareness",
                description="OPSEC considerations, classification handling, need-to-know",
                weight=0.20,
                examples_good=["Redacts sensitive locations in examples"],
                examples_bad=["Uses real operational data in training"]
            ),
            QualityDimension(
                name="interoperability",
                description="Standards compliance, data exchange formats",
                weight=0.10,
                examples_good=["Outputs in NGA-compliant formats"],
                examples_bad=["Proprietary formats without conversion"]
            ),
        ],
        safety_considerations=[
            "No real classified/operational data",
            "OPSEC in all examples",
            "Dual-use awareness",
            "No targeting recommendations without HITL",
            "Export control (ITAR/EAR) awareness"
        ],
        compliance_frameworks=["NIST 800-171", "CMMC", "ITAR", "NGA standards", "NATO STANAG"],
        required_expertise=["Geospatial intelligence", "3D computer vision", "Defense domain"],
        min_annotator_agreement=0.75,
        prompt_categories=[
            "scene_reconstruction", "change_detection", "terrain_analysis",
            "sensor_fusion", "tactical_planning", "visualization",
            "data_standards", "pipeline_design"
        ],
        key_terms={
            "MGRS": "Military Grid Reference System",
            "ISR": "Intelligence, Surveillance, Reconnaissance",
            "GEOINT": "Geospatial Intelligence"
        }
    ),
    
    DomainID.HALAL_COMPLIANCE: DomainSpec(
        id=DomainID.HALAL_COMPLIANCE,
        name="Global Halal Compliance",
        description="Halal certification, supply chain provenance, standards harmonization, and attestation systems.",
        zuup_platform="Civium (Halal)",
        dimensions=[
            QualityDimension(
                name="jurisprudential_accuracy",
                description="Correct understanding of fiqh positions, school differences",
                weight=0.25,
                examples_good=["Acknowledges Hanafi vs Shafi'i differences on seafood"],
                examples_bad=["Presents single madhab view as universal"]
            ),
            QualityDimension(
                name="standards_mapping",
                description="Correct mapping across GSO, JAKIM, MUI, ESMA standards",
                weight=0.25,
                examples_good=["Maps ingredient to multiple standard requirements"],
                examples_bad=["Assumes single global standard"]
            ),
            QualityDimension(
                name="supply_chain_rigor",
                description="Provenance tracking, contamination prevention, audit trails",
                weight=0.20,
                examples_good=["Full chain of custody from slaughter to retail"],
                examples_bad=["Relies on final product testing only"]
            ),
            QualityDimension(
                name="dispute_handling",
                description="Clear escalation paths, scholarly consultation protocols",
                weight=0.15,
                examples_good=["Defined process for disputed ingredients"],
                examples_bad=["Binary halal/haram without nuance"]
            ),
            QualityDimension(
                name="cultural_sensitivity",
                description="Respectful treatment of religious requirements",
                weight=0.15,
                examples_good=["Frames compliance as religious obligation support"],
                examples_bad=["Treats halal as mere market requirement"]
            ),
        ],
        safety_considerations=[
            "Respect religious sensitivities",
            "No misrepresentation of certification status",
            "Acknowledge legitimate scholarly differences",
            "Protect proprietary formulations"
        ],
        compliance_frameworks=["GSO 2055", "MS 1500", "UAE.S 2055", "OIC/SMIIC"],
        required_expertise=["Islamic jurisprudence familiarity", "Food science", "Supply chain"],
        min_annotator_agreement=0.7,
        prompt_categories=[
            "ingredient_analysis", "certification_mapping", "supply_chain",
            "audit_protocols", "dispute_resolution", "standards_harmonization",
            "cross_contamination", "documentation"
        ],
        key_terms={
            "Dhabiha": "Islamic slaughter method",
            "Mashbooh": "Doubtful/questionable",
            "Istihalah": "Complete transformation (purification)"
        }
    ),
    
    DomainID.MOBILE_DATA_CENTER: DomainSpec(
        id=DomainID.MOBILE_DATA_CENTER,
        name="Mobile Distributed Data Centers",
        description="Edge computing in DDIL environments, tactical networking, and resilient infrastructure.",
        zuup_platform="PodX",
        dimensions=[
            QualityDimension(
                name="operational_resilience",
                description="Offline-first, degraded mode operation, recovery procedures",
                weight=0.25,
                examples_good=["Defines graceful degradation for each connectivity state"],
                examples_bad=["Assumes persistent connectivity"]
            ),
            QualityDimension(
                name="environmental_hardening",
                description="Thermal, shock, vibration, EMI considerations",
                weight=0.25,
                examples_good=["Specifies MIL-STD-810 compliance for shock/vibe"],
                examples_bad=["Commercial hardware without hardening"]
            ),
            QualityDimension(
                name="logistics_feasibility",
                description="Power budgets, form factors, transportability constraints",
                weight=0.20,
                examples_good=["Calculates total power budget with thermal headroom"],
                examples_bad=["Ignores generator fuel logistics"]
            ),
            QualityDimension(
                name="security_architecture",
                description="Zero-trust, data-at-rest encryption, physical security",
                weight=0.20,
                examples_good=["HSM-backed key management with tamper response"],
                examples_bad=["Software-only encryption with key in memory"]
            ),
            QualityDimension(
                name="interoperability",
                description="Coalition partner integration, standards compliance",
                weight=0.10,
                examples_good=["Implements NATO FMN standards for data sharing"],
                examples_bad=["Proprietary protocols without gateways"]
            ),
        ],
        safety_considerations=[
            "Personnel safety in field conditions",
            "Data destruction procedures",
            "Physical security protocols",
            "EMI/EMC compliance"
        ],
        compliance_frameworks=["MIL-STD-810", "MIL-STD-461", "NIST 800-171", "NATO STANAG"],
        required_expertise=["Edge computing", "Military logistics", "Tactical networking"],
        min_annotator_agreement=0.7,
        prompt_categories=[
            "architecture_design", "power_systems", "thermal_management",
            "networking", "security", "logistics", "deployment_procedures",
            "recovery_operations"
        ],
        key_terms={
            "DDIL": "Denied, Degraded, Intermittent, Limited (bandwidth)",
            "PACE": "Primary, Alternate, Contingency, Emergency (comms)",
            "FMN": "Federated Mission Networking"
        }
    ),
    
    DomainID.HUBZONE: DomainSpec(
        id=DomainID.HUBZONE,
        name="HUBZone Ecosystem",
        description="HUBZone certification, small business contracting, economic development in underserved areas.",
        zuup_platform="Aureon (HUBZone)",
        dimensions=[
            QualityDimension(
                name="regulatory_accuracy",
                description="Correct HUBZone eligibility rules, SBA requirements",
                weight=0.30,
                examples_good=["Correctly calculates 35% employee residency requirement"],
                examples_bad=["Misapplies principal office location rules"]
            ),
            QualityDimension(
                name="strategic_guidance",
                description="Actionable advice for certification and contracting",
                weight=0.25,
                examples_good=["Maps HUBZone set-aside opportunities to capabilities"],
                examples_bad=["Generic small business advice"]
            ),
            QualityDimension(
                name="compliance_maintenance",
                description="Ongoing compliance, recertification, audit preparation",
                weight=0.20,
                examples_good=["Defines annual recertification checklist"],
                examples_bad=["Assumes one-time certification"]
            ),
            QualityDimension(
                name="economic_development",
                description="Understanding of HUBZone program economic objectives",
                weight=0.15,
                examples_good=["Connects certification to community impact"],
                examples_bad=["Treats purely as contracting advantage"]
            ),
            QualityDimension(
                name="documentation",
                description="Proper evidence collection, record-keeping",
                weight=0.10,
                examples_good=["Specifies required residence documentation"],
                examples_bad=["Vague reference to 'proof of residence'"]
            ),
        ],
        safety_considerations=[
            "No advice on fraudulent certification",
            "Accurate representation of eligibility",
            "Privacy of employee information"
        ],
        compliance_frameworks=["13 CFR Part 126", "SBA HUBZone Program", "FAR 19.13"],
        required_expertise=["Small business contracting", "SBA programs", "Government procurement"],
        min_annotator_agreement=0.7,
        prompt_categories=[
            "eligibility_assessment", "certification_process", "contracting_strategy",
            "compliance_maintenance", "teaming", "subcontracting",
            "map_analysis", "documentation"
        ],
        key_terms={
            "HUBZone": "Historically Underutilized Business Zone",
            "Set-aside": "Contract reserved for specific small business category",
            "Principal office": "Location where greatest number of employees work"
        }
    ),
}


def get_domain(domain_id: DomainID) -> DomainSpec:
    return DOMAINS[domain_id]


def get_all_domains() -> List[DomainSpec]:
    return list(DOMAINS.values())


def get_quality_rubric(domain_id: DomainID) -> str:
    """Generate human-readable quality rubric for annotators."""
    domain = DOMAINS[domain_id]
    rubric = f"# Quality Rubric: {domain.name}\n\n"
    rubric += f"{domain.description}\n\n"
    rubric += "## Scoring Dimensions\n\n"
    
    for dim in domain.dimensions:
        rubric += f"### {dim.name.replace('_', ' ').title()} (Weight: {dim.weight:.0%})\n"
        rubric += f"{dim.description}\n\n"
        rubric += f"**Good example:** {dim.examples_good[0]}\n\n"
        rubric += f"**Bad example:** {dim.examples_bad[0]}\n\n"
    
    rubric += "## Safety Considerations\n"
    for safety in domain.safety_considerations:
        rubric += f"- {safety}\n"
    
    return rubric
