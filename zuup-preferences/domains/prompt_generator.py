"""
Prompt Generator for Zuup Preference Collection

Generates domain-specific seed prompts for preference data collection.
Prompts are designed to elicit expert-level responses that can be meaningfully compared.
"""

import random
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from .taxonomy import Domain, Category, get_domain, DOMAINS


@dataclass
class GeneratedPrompt:
    """A generated prompt with metadata."""
    domain_id: str
    category_id: str
    prompt: str
    difficulty: str  # "basic", "intermediate", "advanced"
    context: Optional[str] = None


# ============================================================================
# SEED PROMPT TEMPLATES BY DOMAIN
# ============================================================================

PROMPT_TEMPLATES: Dict[str, Dict[str, List[str]]] = {
    
    # -------------------------------------------------------------------------
    # PROCUREMENT
    # -------------------------------------------------------------------------
    "procurement": {
        "rfp_analysis": [
            "Analyze the following RFP excerpt and identify the key evaluation factors, their relative weights, and any compliance requirements that could be disqualifying:\n\n{context}",
            "Review this Statement of Work (SOW) and identify ambiguous requirements that should be clarified through questions during the Q&A period:\n\n{context}",
            "Compare Section L (Instructions) and Section M (Evaluation Criteria) of this RFP to identify any inconsistencies or areas where we should focus our proposal strategy:\n\n{context}",
            "What are the key discriminators we should emphasize in our proposal based on this RFP's evaluation criteria?",
            "Identify the mandatory (go/no-go) requirements vs. desirable features in this solicitation.",
        ],
        "proposal_writing": [
            "Draft a technical approach section for a cloud migration project that emphasizes security, minimal downtime, and phased implementation.",
            "Write a past performance narrative for a cybersecurity contract that demonstrates relevant experience with FedRAMP-authorized environments.",
            "Create a management approach section that addresses key personnel, quality control, and risk management for a software development contract.",
            "Draft an executive summary for a proposal responding to an AI/ML analytics platform RFP for a defense agency.",
            "Write a transition plan section for taking over an incumbent contract with 30 days for knowledge transfer.",
        ],
        "far_dfars": [
            "Explain the implications of FAR 52.219-14 (Limitations on Subcontracting) for a small business prime contractor and how to ensure compliance.",
            "What are the notification and consent requirements under DFARS 252.204-7012 for cyber incidents affecting Covered Defense Information?",
            "Interpret the organizational conflict of interest requirements under FAR 9.5 and explain mitigation strategies for a contractor that provides both advisory and implementation services.",
            "Explain the cost allowability requirements for independent research and development (IR&D) under FAR 31.205-18.",
            "How do the Truth in Negotiations Act (TINA) requirements apply to modifications of contracts originally awarded on a sole-source basis?",
        ],
        "pricing_strategy": [
            "Develop a pricing strategy for a Time & Materials task order where the government has indicated best value is the priority, not LPTA.",
            "How should we structure our cost proposal for a cost-plus-fixed-fee R&D contract to ensure compliance while remaining competitive?",
            "Calculate and justify indirect cost rates for a proposal to an agency that typically challenges wrap rates above 150%.",
            "Design a pricing approach for a fixed-price contract with uncertain scope, balancing competitive pricing with risk mitigation.",
            "How should we price options years on a 5-year IDIQ contract given expected labor cost escalation?",
        ],
        "contract_admin": [
            "Draft a Request for Equitable Adjustment (REA) for government-caused delays that extended performance by 3 months.",
            "How should we respond to a Contracting Officer's cure notice alleging delivery delays when the delays were caused by government-furnished equipment issues?",
            "Prepare a strategy for responding to negative CPARS ratings that we believe are factually inaccurate.",
            "What are the requirements and process for novating a contract during a corporate acquisition?",
            "How should we handle a contract modification that the government claims is within scope but we believe constitutes a cardinal change?",
        ],
    },
    
    # -------------------------------------------------------------------------
    # BIOMEDICAL GB-CI
    # -------------------------------------------------------------------------
    "biomedical_gbci": {
        "biosensor_design": [
            "Design a multi-analyte biosensor panel for detecting gut-brain axis biomarkers associated with major depressive disorder.",
            "Propose a continuous monitoring approach for measuring vagal nerve activity using non-invasive wearable sensors.",
            "Compare piezoelectric and optical sensing modalities for detecting gut motility patterns, considering sensitivity, power requirements, and form factor.",
            "Design a biosensor system for real-time monitoring of intestinal permeability markers (e.g., zonulin, LPS).",
            "What biomarkers should a gut-brain interface monitor to detect early signs of neuroinflammation?",
        ],
        "microbiome_analysis": [
            "Interpret 16S rRNA sequencing results showing elevated Proteobacteria and reduced Bacteroidetes in a patient cohort with treatment-resistant depression.",
            "Design a longitudinal metagenomic study to investigate the relationship between gut microbiome composition and cognitive decline in early Alzheimer's disease.",
            "Analyze the mechanisms by which short-chain fatty acid (SCFA) production by gut bacteria influences blood-brain barrier permeability.",
            "How should we control for dietary confounders in a microbiome-anxiety association study?",
            "Design a bioinformatics pipeline for identifying microbial metabolites that cross the blood-brain barrier from shotgun metagenomic data.",
        ],
        "neural_pathways": [
            "Describe the vagal afferent signaling cascade from gut chemoreceptors to the nucleus tractus solitarius and its implications for satiety interventions.",
            "Map the enteric nervous system modulation targets that could be leveraged for treating functional gastrointestinal disorders with neural components.",
            "Analyze how inflammatory cytokines produced by gut dysbiosis affect blood-brain barrier permeability and neuroinflammation.",
            "Explain the role of the gut-brain axis in the pathophysiology of Parkinson's disease, including alpha-synuclein propagation.",
            "How do enteroendocrine cells communicate with vagal afferents, and what are the key signaling molecules involved?",
        ],
        "clinical_protocol": [
            "Design a Phase 2 randomized controlled trial to evaluate a psychobiotic intervention for generalized anxiety disorder, including primary and secondary endpoints.",
            "Develop a comprehensive outcome measure framework for evaluating gut-brain interventions in irritable bowel syndrome with comorbid anxiety.",
            "Create a safety monitoring plan for a first-in-human trial of an implantable gut biosensor with wireless data transmission.",
            "Design inclusion/exclusion criteria for a microbiome transplant trial targeting autism spectrum disorder GI symptoms.",
            "What biomarkers should we collect in a gut-brain intervention trial to enable mechanistic analysis?",
        ],
    },
    
    # -------------------------------------------------------------------------
    # INGESTIBLE GB-CI
    # -------------------------------------------------------------------------
    "ingestible_gbci": {
        "capsule_design": [
            "Specify the power budget and energy harvesting options for an ingestible capsule designed for 72-hour transit through the entire GI tract.",
            "Design an antenna system for reliable in-body RF communication from an ingestible capsule to an external receiver, considering tissue absorption.",
            "Evaluate coating materials for targeted drug release in the ileum, considering pH sensitivity, enzymatic degradation, and manufacturing feasibility.",
            "Design the mechanical housing for an ingestible capsule that must withstand gastric acid, peristaltic forces, and contain sensitive electronics.",
            "How should we approach thermal management for an ingestible capsule with active sensing that generates 50mW of heat?",
        ],
        "in_vivo_sensing": [
            "Design an algorithm for mapping pH gradients along the GI tract using an ingestible capsule with a single pH sensor.",
            "Specify image sensor requirements for a capsule endoscope optimized for low-light conditions in the small bowel.",
            "Develop a temperature calibration approach for in-vivo sensing accuracy, accounting for body temperature variations.",
            "Design a position estimation system for an ingestible capsule using a combination of RF signal strength and IMU data.",
            "How should we approach real-time data compression for video capsule endoscopy given power and bandwidth constraints?",
        ],
        "regulatory_pathway": [
            "Determine the appropriate FDA regulatory pathway (510(k), De Novo, or PMA) for a smart pill that combines diagnostics with targeted drug delivery.",
            "Draft a biocompatibility testing protocol per ISO 10993 for an ingestible capsule with novel polymer coating.",
            "Prepare a clinical evidence strategy for a De Novo request for an AI-enhanced capsule endoscopy system.",
            "What special controls should we expect for an ingestible biosensor classified as a Class II device?",
            "How should we approach pediatric labeling requirements for an ingestible diagnostic device?",
        ],
        "manufacturing": [
            "Design a sterilization validation protocol for an ingestible capsule containing temperature-sensitive electronics.",
            "Specify incoming inspection criteria for MEMS sensors used in ingestible diagnostic devices.",
            "Create a batch release testing protocol that ensures 100% reliability for an ingestible therapeutic device.",
            "How should we approach process validation for a novel micro-assembly process used in capsule manufacturing?",
            "Design a packaging system that maintains sterility and enables visual inspection of ingestible capsules.",
        ],
    },
    
    # -------------------------------------------------------------------------
    # LEGACY REFACTORING
    # -------------------------------------------------------------------------
    "legacy_refactoring": {
        "cobol_analysis": [
            "Analyze and document the data structures defined in this COBOL copybook, including packed decimal fields and level-88 conditions:\n\n{context}",
            "Identify dead code and unreachable paragraphs in this COBOL program's PROCEDURE DIVISION:\n\n{context}",
            "Map the CICS transaction flow and BMS map dependencies for this online banking module.",
            "Document the business rules encoded in this COBOL program's conditional logic for a modernization team.",
            "Analyze the file I/O patterns in this batch COBOL program and identify potential modernization blockers.",
        ],
        "migration_strategy": [
            "Compare rehost, replatform, and refactor approaches for migrating an IMS DB/DC application to AWS, considering risk, cost, and timeline.",
            "Design a phased migration strategy for a 24/7 banking system that cannot tolerate more than 15 minutes of downtime per month.",
            "Evaluate Micro Focus Enterprise Server vs. AWS Mainframe Modernization for a COBOL application with heavy CICS usage.",
            "How should we approach migrating a system with extensive JCL job scheduling dependencies to a cloud-native orchestration platform?",
            "Design a strangler fig pattern implementation for incrementally migrating a monolithic COBOL application to microservices.",
        ],
        "data_transformation": [
            "Design an approach to convert EBCDIC data with packed decimal (COMP-3) and binary (COMP) fields to a modern cloud database.",
            "How should we migrate VSAM KSDS files to PostgreSQL while maintaining key-sequenced access patterns?",
            "Design a strategy for handling generation data groups (GDGs) when migrating batch processes to cloud storage.",
            "Create a data validation framework to ensure functional equivalence between mainframe and migrated data.",
            "How should we handle COBOL REDEFINES clauses when generating target database schemas?",
        ],
        "testing_validation": [
            "Design a regression test strategy for validating a migrated batch processing system against the original mainframe implementation.",
            "Create a data validation framework for comparing outputs between legacy and modernized systems at scale.",
            "Develop a performance baseline comparison approach to ensure the modernized system meets or exceeds mainframe performance.",
            "How should we approach testing a migrated CICS application's transaction response times against the original?",
            "Design an approach for generating representative test data from production mainframe data while ensuring privacy compliance.",
        ],
    },
    
    # -------------------------------------------------------------------------
    # AUTONOMY OS
    # -------------------------------------------------------------------------
    "autonomy_os": {
        "agent_architecture": [
            "Design a multi-agent hierarchy for automating literature review and synthesis tasks, with appropriate capability boundaries and coordination patterns.",
            "Implement a tool-use authorization flow that allows agents to use approved tools while preventing unauthorized capability acquisition.",
            "Create an inter-agent communication protocol that enables collaboration while preventing privilege escalation between agents.",
            "Design an agent architecture for automated code review that balances thoroughness with safety constraints.",
            "How should we structure memory and context sharing between agents in a long-running research automation system?",
        ],
        "safety_mechanisms": [
            "Design a capability boundary enforcement system that prevents agents from acquiring tools or permissions beyond their assigned scope.",
            "Implement constitutional AI constraints for an agent that assists with content moderation, ensuring it cannot be jailbroken through adversarial prompts.",
            "Create a comprehensive audit logging system for agent actions that enables post-hoc analysis of decision-making processes.",
            "Design a monitoring system that detects potential goal drift or capability seeking behavior in autonomous agents.",
            "How should we implement output filtering to prevent an agent from exfiltrating sensitive information while maintaining utility?",
        ],
        "human_oversight": [
            "Design an approval workflow for high-stakes actions that balances safety with operational efficiency for an autonomous customer service agent.",
            "Implement graceful degradation patterns for an agent system when it encounters tasks outside its competence boundary.",
            "Create escalation criteria that determine when an agent should defer to human judgment versus proceed autonomously.",
            "Design a human-in-the-loop interface for supervising a fleet of agents processing sensitive documents.",
            "How should we handle situations where human oversight is unavailable but the agent needs to make time-sensitive decisions?",
        ],
        "evaluation": [
            "Design a benchmark suite for evaluating an agent's ability to decompose complex tasks into appropriate subtasks.",
            "Create a red-team evaluation protocol for testing an agent's resistance to prompt injection and jailbreaking attempts.",
            "Develop metrics for measuring goal stability across extended context lengths and multi-turn interactions.",
            "Design an evaluation framework for assessing an agent's calibration—its ability to know what it doesn't know.",
            "How should we evaluate an agent's ability to request appropriate human oversight in ambiguous situations?",
        ],
    },
    
    # -------------------------------------------------------------------------
    # QUANTUM ARCHAEOLOGY
    # -------------------------------------------------------------------------
    "quantum_archaeology": {
        "evidence_analysis": [
            "Cross-reference pottery shard decoration patterns across 12 archaeological sites to identify trade network connections in Bronze Age Anatolia.",
            "Reconstruct ancient trade routes from coin distribution data, accounting for hoarding patterns and modern collection biases.",
            "Date this structure using multi-proxy calibration from dendrochronology, radiocarbon, and archaeomagnetism, handling conflicting results.",
            "Analyze this fragmentary cuneiform tablet to identify the text genre and likely archive of origin.",
            "How should we handle provenance uncertainty when integrating looted artifacts into a regional database analysis?",
        ],
        "reconstruction": [
            "Simulate population dynamics for a Bronze Age collapse scenario using settlement survey data and paleoclimate proxies.",
            "Model the climate impact on Late Classic Maya agricultural systems using settlement pattern, soil chemistry, and paleobotanical data.",
            "Reconstruct battle sequences from archaeological evidence at a Roman siege site, integrating projectile distributions and destruction layers.",
            "Create a probabilistic model for the spread of metallurgical knowledge across Eurasia in the 3rd millennium BCE.",
            "How should we model the demographic impact of the Antonine Plague from epigraphic and archaeological evidence?",
        ],
        "pattern_recognition": [
            "Detect cultural transmission patterns in ceramic decoration styles across a 500-year stratigraphic sequence.",
            "Identify anomalous events in this stratigraphic profile that might indicate natural disasters or rapid social changes.",
            "Cluster handwriting samples from Dead Sea Scroll fragments for authorship attribution, handling fragmentary evidence.",
            "Identify potential astronomical alignments in monument orientations, controlling for false positives from multiple testing.",
            "How should we distinguish deliberate patterning from random variation in prehistoric cave art color distributions?",
        ],
        "computational_methods": [
            "Design an MCMC sampler for radiocarbon calibration that properly handles multiple samples with stratigraphic ordering constraints.",
            "Implement a graph-based artifact similarity network for identifying production centers from ceramic chemistry data.",
            "Apply combinatorial optimization to predict undiscovered site locations based on known site distributions and environmental variables.",
            "Design a Bayesian approach to combining radiocarbon dates from the same context with varying precision.",
            "How should we handle sparse data when applying machine learning to archaeological predictive modeling?",
        ],
    },
    
    # -------------------------------------------------------------------------
    # DEFENSE WORLD MODELS
    # -------------------------------------------------------------------------
    "defense_wm": {
        "scene_understanding": [
            "Identify and classify structures of interest in this LiDAR point cloud, distinguishing military installations from civilian infrastructure.",
            "Design a fusion approach for combining SAR and EO imagery to detect building changes in an urban environment with frequent cloud cover.",
            "Detect terrain changes between these two collection dates that might indicate concealment activities or tunnel construction.",
            "How should we approach automated detection of camouflaged vehicles in multi-spectral imagery?",
            "Design a change detection algorithm that distinguishes hostile activity from normal construction in a denied area.",
        ],
        "pattern_of_life": [
            "Identify anomalous vehicle movement patterns in this week of wide-area motion imagery that might indicate preparation for hostile action.",
            "Establish a baseline activity model for this compound to enable detection of significant deviations.",
            "Correlate SIGINT collection times with observed movements to assess attribution confidence for a vehicle of interest.",
            "Design a pattern-of-life analysis approach that accounts for weekly, seasonal, and cultural event variations.",
            "How should we distinguish hostile reconnaissance from normal civilian activity in pattern-of-life analysis?",
        ],
        "sensor_fusion": [
            "Design a multi-sensor fusion architecture for a UAV swarm conducting persistent surveillance, optimizing for coverage and redundancy.",
            "Develop an approach for resolving conflicting target classifications from EO, SAR, and GMTI sensors.",
            "Create a dynamic collection priority algorithm that allocates sensor resources based on information gaps and target value.",
            "How should we handle time synchronization and georeferencing errors when fusing data from multiple platforms?",
            "Design a degraded-mode fusion approach when SATCOM bandwidth limits force data triage from remote sensors.",
        ],
        "decision_support": [
            "Generate ingress route options with risk assessments considering enemy air defense, terrain masking, and time on target requirements.",
            "Identify optimal observation positions for a reconnaissance team balancing concealment, sight lines, and extraction routes.",
            "Predict adversary response to a planned friendly action based on historical pattern-of-life and doctrine analysis.",
            "Design a decision support interface that presents ISR-derived options without overwhelming the tactical commander.",
            "How should we communicate confidence levels and intelligence gaps in automated targeting recommendations?",
        ],
    },
    
    # -------------------------------------------------------------------------
    # HALAL COMPLIANCE
    # -------------------------------------------------------------------------
    "halal_compliance": {
        "ingredient_analysis": [
            "Assess the halal status of gelatin in this pharmaceutical product and recommend compliant alternatives that maintain product stability.",
            "Evaluate these E-number food additives for halal status, considering different scholarly opinions on synthetic vs. natural sources.",
            "Analyze the alcohol content in vanilla extract used in this baked goods formulation and determine compliance with major certification body standards.",
            "How should we assess the halal status of enzymes derived from genetically modified organisms?",
            "Evaluate the halal compliance of this whey protein product, considering the rennet source and processing conditions.",
        ],
        "supply_chain": [
            "Design a comprehensive supplier audit checklist for meat products that addresses slaughter, processing, and transportation requirements.",
            "Trace this questionable ingredient to its original source to verify certification claims, handling gaps in documentation.",
            "Verify logistics separation requirements for halal shipments sharing transport with non-halal goods.",
            "How should we approach halal verification for ingredients sourced from markets with limited certification infrastructure?",
            "Design a traceability system that provides immutable halal provenance records from farm to consumer.",
        ],
        "certification": [
            "Compare JAKIM (Malaysia), IFANCA (USA), and MUI (Indonesia) certification requirements for a food manufacturer seeking multi-market access.",
            "Prepare the documentation package for MUI certification of a beverage product, addressing their specific requirements for imported ingredients.",
            "Map halal certification reciprocity and recognition agreements across Southeast Asian, Middle Eastern, and European markets.",
            "How should we handle certification renewal when our slaughterhouse partner's certification has lapsed?",
            "Design a certification management system that tracks expiration, renewal requirements, and audit schedules across multiple bodies.",
        ],
        "process_compliance": [
            "Design a production line layout that ensures effective separation between halal and non-halal product manufacturing in a shared facility.",
            "Create a cleaning validation protocol for equipment shared between halal and non-halal production that meets certification requirements.",
            "Develop halal control points for integration into an existing HACCP food safety management system.",
            "How should we handle an accidental cross-contamination incident during production?",
            "Design training materials for production staff on halal compliance requirements, considering diverse religious literacy levels.",
        ],
    },
    
    # -------------------------------------------------------------------------
    # MOBILE DATA CENTER
    # -------------------------------------------------------------------------
    "mobile_datacenter": {
        "infrastructure_design": [
            "Specify the cooling system design for a containerized data center delivering 50kW compute power in 40°C ambient desert conditions.",
            "Design the power distribution architecture for a mobile data center with generator primary power and battery backup for seamless failover.",
            "Create a 20U rack layout optimized for transport vibration tolerance while maximizing compute density for edge AI workloads.",
            "How should we approach EMI shielding for a mobile data center deployed near sensitive communications equipment?",
            "Design the physical security architecture for a containerized data center deployed in a semi-permissive environment.",
        ],
        "edge_computing": [
            "Design a K3s (lightweight Kubernetes) cluster architecture for a disconnected deployment that must operate autonomously for 30 days.",
            "Implement a store-and-forward data synchronization architecture for a distributed edge system with intermittent satellite connectivity.",
            "Optimize ML inference workloads for a power-constrained edge deployment limited to 2kW total compute budget.",
            "How should we handle container orchestration failover when the primary control plane node fails in an isolated environment?",
            "Design a data lifecycle management strategy for edge nodes with limited storage that must retain critical data for eventual sync.",
        ],
        "resilient_networking": [
            "Design a mesh network architecture with SATCOM backup that provides continuous connectivity for 6 distributed edge nodes.",
            "Implement a delay-tolerant networking protocol for a system that may experience multi-hour connectivity blackouts.",
            "Create a bandwidth-aware data prioritization scheme that ensures critical operational data flows over constrained satellite links.",
            "How should we approach network security for a mobile data center connecting to varying network infrastructures in different locations?",
            "Design a dynamic routing architecture that automatically fails over between terrestrial, satellite, and mesh connectivity options.",
        ],
        "operations": [
            "Create a comprehensive pre-deployment checklist for a mobile data center pod being shipped to a remote austere location.",
            "Design a monitoring and alerting strategy for a mobile data center with bandwidth-constrained uplink to the NOC.",
            "Develop a field troubleshooting guide for operators who are not IT specialists to resolve common issues.",
            "How should we approach remote system updates when connectivity windows are unpredictable and brief?",
            "Create a disaster recovery procedure for a mobile data center experiencing partial hardware failure in an isolated location.",
        ],
    },
    
    # -------------------------------------------------------------------------
    # HUBZONE
    # -------------------------------------------------------------------------
    "hubzone": {
        "certification": [
            "Evaluate whether this company's principal office location meets HUBZone eligibility requirements, considering the recent census tract redesignation.",
            "Calculate the 35% employee residency requirement for HUBZone certification, handling employees who work remotely from various locations.",
            "Document the ownership and control structure for a company with complex equity arrangements seeking HUBZone certification.",
            "How should we handle a situation where an employee's move outside a HUBZone affects our compliance percentage?",
            "Analyze the impact of a proposed office relocation on our HUBZone certification eligibility.",
        ],
        "opportunity_identification": [
            "Identify HUBZone set-aside opportunities in NAICS 541512 (Computer Systems Design) for Q1 forecasted procurements.",
            "Evaluate whether the price evaluation preference (10% for HUBZone) would make us competitive on this full and open competition.",
            "Analyze the competitive landscape for this HUBZone set-aside, identifying likely competitors and their strengths.",
            "How should we evaluate whether to pursue a HUBZone set-aside vs. a full and open opportunity where we can claim the preference?",
            "Identify task order opportunities on MAC vehicles where our HUBZone status provides a competitive advantage.",
        ],
        "compliance_maintenance": [
            "Prepare documentation for our upcoming HUBZone recertification, addressing changes in our employee composition since initial certification.",
            "How should we handle an employee's relocation outside the HUBZone while maintaining certification compliance?",
            "Address the impact of a census tract redesignation that removes our principal office from HUBZone eligibility.",
            "Design a compliance monitoring system that tracks employee residency and alerts when we approach the 35% threshold.",
            "Create a protocol for annual recertification that minimizes disruption while ensuring complete and accurate submissions.",
        ],
        "joint_ventures": [
            "Evaluate the HUBZone population requirements for a joint venture between our HUBZone firm and a large business mentor.",
            "Structure a mentor-protégé joint venture that maintains HUBZone status for set-aside eligibility.",
            "Ensure our proposed JV operating agreement meets HUBZone control requirements for the HUBZone partner.",
            "How should we handle work distribution in a HUBZone JV to meet limitations on subcontracting requirements?",
            "Analyze whether an 8(a) JV with a HUBZone partner can claim both set-aside preferences on applicable contracts.",
        ],
    },
}


class PromptGenerator:
    """Generates prompts for preference data collection."""
    
    def __init__(self, domain_id: Optional[str] = None):
        """
        Initialize the generator.
        
        Args:
            domain_id: Optional domain to restrict generation to
        """
        self.domain_id = domain_id
        
    def generate(
        self,
        domain_id: Optional[str] = None,
        category_id: Optional[str] = None,
        context: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> GeneratedPrompt:
        """
        Generate a random prompt.
        
        Args:
            domain_id: Domain to generate from (uses self.domain_id if None)
            category_id: Specific category (random if None)
            context: Optional context to inject into template
            difficulty: Optional difficulty filter
            
        Returns:
            GeneratedPrompt with the generated prompt
        """
        domain_id = domain_id or self.domain_id
        if not domain_id:
            domain_id = random.choice(list(DOMAINS.keys()))
            
        domain = get_domain(domain_id)
        if not domain:
            raise ValueError(f"Unknown domain: {domain_id}")
            
        templates = PROMPT_TEMPLATES.get(domain_id, {})
        if not templates:
            raise ValueError(f"No templates for domain: {domain_id}")
            
        # Select category
        if category_id:
            if category_id not in templates:
                raise ValueError(f"Unknown category: {category_id}")
            category_templates = templates[category_id]
        else:
            category_id = random.choice(list(templates.keys()))
            category_templates = templates[category_id]
            
        # Select and format prompt
        prompt_template = random.choice(category_templates)
        
        # Handle context placeholder
        if "{context}" in prompt_template:
            if context:
                prompt = prompt_template.format(context=context)
            else:
                # Use placeholder note if no context provided
                prompt = prompt_template.replace(
                    "{context}",
                    "[Insert relevant document/data excerpt here]"
                )
        else:
            prompt = prompt_template
            
        # Estimate difficulty based on prompt characteristics
        if not difficulty:
            difficulty = self._estimate_difficulty(prompt)
            
        return GeneratedPrompt(
            domain_id=domain_id,
            category_id=category_id,
            prompt=prompt,
            difficulty=difficulty,
            context=context
        )
        
    def generate_batch(
        self,
        domain_id: str,
        n: int = 10,
        category_id: Optional[str] = None
    ) -> List[GeneratedPrompt]:
        """
        Generate a batch of prompts.
        
        Args:
            domain_id: Domain to generate from
            n: Number of prompts to generate
            category_id: Optional category filter
            
        Returns:
            List of GeneratedPrompt objects
        """
        prompts = []
        for _ in range(n):
            try:
                prompts.append(self.generate(domain_id, category_id))
            except Exception:
                continue
        return prompts
        
    def _estimate_difficulty(self, prompt: str) -> str:
        """Estimate prompt difficulty based on characteristics."""
        indicators = {
            "advanced": ["design", "implement", "evaluate", "compare", "analyze", "complex"],
            "intermediate": ["explain", "describe", "create", "develop", "how should"],
            "basic": ["what", "identify", "list", "summarize", "define"]
        }
        
        prompt_lower = prompt.lower()
        
        for difficulty, keywords in indicators.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    return difficulty
                    
        return "intermediate"
        
    def get_available_categories(self, domain_id: str) -> List[str]:
        """Get available categories for a domain."""
        return list(PROMPT_TEMPLATES.get(domain_id, {}).keys())
        
    def get_all_prompts(self, domain_id: str) -> Dict[str, List[str]]:
        """Get all prompts for a domain organized by category."""
        return PROMPT_TEMPLATES.get(domain_id, {})


def generate_sample_pair(
    domain_id: str,
    category_id: Optional[str] = None
) -> Tuple[GeneratedPrompt, str, str]:
    """
    Generate a prompt with placeholder response pair.
    
    This is used for UI testing. In production, responses would come from
    actual LLM inference with different temperatures/prompts.
    
    Args:
        domain_id: Domain to generate from
        category_id: Optional category filter
        
    Returns:
        Tuple of (prompt, response_a, response_b)
    """
    generator = PromptGenerator()
    prompt = generator.generate(domain_id, category_id)
    
    # Placeholder responses - in production these would come from Ollama/etc
    response_a = f"[Response A - Generated with temperature=0.3]\n\nThis is a placeholder response for:\n{prompt.prompt[:100]}..."
    response_b = f"[Response B - Generated with temperature=0.7]\n\nThis is an alternative placeholder response for:\n{prompt.prompt[:100]}..."
    
    return prompt, response_a, response_b


if __name__ == "__main__":
    # Demo prompt generation
    generator = PromptGenerator()
    
    print("=" * 60)
    print("ZUUP PROMPT GENERATOR DEMO")
    print("=" * 60)
    
    for domain_id in list(DOMAINS.keys())[:3]:
        print(f"\n{domain_id.upper()}")
        print("-" * 40)
        
        for i in range(2):
            prompt = generator.generate(domain_id)
            print(f"\n[{prompt.category_id}] ({prompt.difficulty})")
            print(f"  {prompt.prompt[:150]}...")

