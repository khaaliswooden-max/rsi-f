# domains/prompt_generator.py — Generate domain-specific prompts
import random
from typing import List, Dict
from domains.taxonomy import DomainID, DOMAINS

# Seed prompts per domain
SEED_PROMPTS: Dict[DomainID, Dict[str, List[str]]] = {
    
    DomainID.FED_SLED_PROCUREMENT: {
        "RFP_analysis": [
            "Analyze this RFP for a cloud migration contract. What are the key evaluation factors and how should we weight our response?",
            "The solicitation mentions 'best value' but doesn't specify weights. How should we interpret this?",
            "What are the protest risks in this sole-source justification?",
        ],
        "proposal_writing": [
            "Write a technical approach section for a cybersecurity assessment contract.",
            "How should we structure our past performance volume for a DoD contract?",
            "Draft an executive summary for a $50M IT modernization proposal.",
        ],
        "compliance_check": [
            "Review this subcontracting plan for FAR 52.219-9 compliance.",
            "Does our teaming arrangement create an OCI? How do we mitigate?",
            "What CMMC level is required for this CUI-handling contract?",
        ],
    },
    
    DomainID.BIOMEDICAL_GBCI: {
        "signal_processing": [
            "Design a filtering pipeline for EGG signals to extract gastric slow wave activity.",
            "How do I handle motion artifacts in wearable gut biosensor data?",
            "What's the optimal sampling rate for detecting gut-brain vagal signaling?",
        ],
        "microbiome_analysis": [
            "Design a study to correlate gut microbiome composition with anxiety symptoms.",
            "What are the confounders in microbiome-mood association studies?",
            "How should we handle the compositional nature of 16S data in our analysis?",
        ],
        "regulatory_pathway": [
            "What FDA classification would a gut motility monitoring patch fall under?",
            "Design a clinical validation study for a gut-brain biomarker device.",
            "What's the predicate device strategy for a novel intestinal biosensor?",
        ],
    },
    
    DomainID.INGESTIBLE_GBCI: {
        "capsule_design": [
            "What are the size constraints for an ingestible capsule to ensure safe GI transit?",
            "Design a biocompatible encapsulation strategy for an electronic capsule.",
            "How do we ensure the capsule passes naturally without retention?",
        ],
        "telemetry": [
            "Calculate the RF link budget for in-body to external receiver communication.",
            "What frequencies are approved for medical ingestible device telemetry?",
            "Design a low-power protocol for continuous gut parameter transmission.",
        ],
        "clinical_validation": [
            "Design a clinical study comparing our ingestible sensor to colonoscopy.",
            "What are the primary endpoints for an ingestible gut motility monitor trial?",
            "How do we handle capsule retention as an adverse event in our protocol?",
        ],
    },
    
    DomainID.LEGACY_REFACTORING: {
        "code_translation": [
            "Translate this COBOL PERFORM VARYING loop to Python.",
            "How do I handle COBOL REDEFINES clauses in a modern data model?",
            "Convert this CICS transaction to a REST API while preserving semantics.",
        ],
        "testing_strategy": [
            "Design characterization tests for a COBOL batch job with no documentation.",
            "How do we ensure decimal precision parity between COBOL COMP-3 and Python?",
            "Create a parallel run strategy to validate our migrated system.",
        ],
        "strangler_pattern": [
            "Design a strangler fig architecture for migrating a mainframe banking system.",
            "How do we route traffic between legacy and new systems during migration?",
            "What's the rollback strategy if the new component fails in production?",
        ],
    },
    
    DomainID.AUTONOMY_OS: {
        "agent_design": [
            "Design a tool permission system for an autonomous coding agent.",
            "How should multi-agent systems handle conflicting goals?",
            "What's the architecture for a self-improving agent with safety constraints?",
        ],
        "safety_constraints": [
            "Implement a human approval gate for high-impact autonomous actions.",
            "How do we ensure an agent can always be shut down?",
            "Design a monitoring system to detect agent capability jumps.",
        ],
        "capability_assessment": [
            "How do we measure if an autonomous agent is safe to deploy?",
            "What benchmarks should we use for tool-use safety evaluation?",
            "Design an eval suite for multi-agent coordination correctness.",
        ],
    },
    
    DomainID.QUANTUM_ARCHAEOLOGY: {
        "event_reconstruction": [
            "Reconstruct the logistics of Alexander's army crossing the Hindu Kush.",
            "What's the uncertainty range for the population of Rome in 100 CE?",
            "Synthesize archaeological and textual evidence for the Exodus route.",
        ],
        "source_analysis": [
            "How should we weight Herodotus vs archaeological evidence for Persian forces at Thermopylae?",
            "Design a provenance tracking system for historical source documents.",
            "What's the methodology for detecting interpolations in ancient manuscripts?",
        ],
        "uncertainty_modeling": [
            "Build a Bayesian model for dating the Thera eruption.",
            "How do we quantify uncertainty in historical population estimates?",
            "Design a confidence framework for AI-reconstructed historical events.",
        ],
    },
    
    DomainID.DEFENSE_WORLD_MODELS: {
        "scene_reconstruction": [
            "Design a pipeline for 3D reconstruction from drone imagery in contested environments.",
            "How do we handle GPS-denied localization for world model construction?",
            "What's the uncertainty quantification approach for terrain reconstruction?",
        ],
        "sensor_fusion": [
            "Fuse EO, IR, and SAR data for a unified 3D scene representation.",
            "How do we handle temporal misalignment in multi-sensor fusion?",
            "Design a confidence metric for fused intelligence products.",
        ],
        "tactical_planning": [
            "Generate terrain analysis for route planning with concealment optimization.",
            "How should the world model support line-of-sight calculations?",
            "Design an interface for human-AI collaborative mission planning.",
        ],
    },
    
    DomainID.HALAL_COMPLIANCE: {
        "ingredient_analysis": [
            "Analyze this ingredient list for halal compliance across GSO and JAKIM standards.",
            "How do we handle E471 (mono- and diglycerides) which may be plant or animal derived?",
            "What's the ruling on alcohol in vanilla extract under different madhabs?",
        ],
        "certification_mapping": [
            "Map our product certification to OIC/SMIIC mutual recognition requirements.",
            "What additional testing is required for UAE vs Malaysian halal certification?",
            "Design a system to track certification status across multiple jurisdictions.",
        ],
        "supply_chain": [
            "Design a blockchain-based provenance system for halal meat supply chain.",
            "How do we prevent cross-contamination in shared manufacturing facilities?",
            "What's the audit protocol for verifying halal slaughter compliance?",
        ],
    },
    
    DomainID.MOBILE_DATA_CENTER: {
        "architecture_design": [
            "Design a compute architecture for a 20kW mobile data center in a transit case.",
            "How do we handle storage redundancy in a single-node deployable unit?",
            "What's the network topology for a mesh of mobile data centers?",
        ],
        "power_systems": [
            "Calculate the power budget for a GPU-heavy edge AI workload in a PodX unit.",
            "Design a power management strategy for generator + battery hybrid operation.",
            "How do we handle graceful shutdown on power loss?",
        ],
        "ddil_operations": [
            "Design a data synchronization strategy for intermittent connectivity.",
            "How should applications degrade gracefully in bandwidth-limited scenarios?",
            "What's the PACE plan for a deployed mobile data center?",
        ],
    },
    
    DomainID.HUBZONE: {
        "eligibility_assessment": [
            "Does our company qualify for HUBZone if 30% of employees live in the zone but we're headquartered outside?",
            "How do we count remote employees for HUBZone residency calculation?",
            "What happens to our certification if the HUBZone map is redrawn?",
        ],
        "contracting_strategy": [
            "Identify HUBZone set-aside opportunities matching our IT capabilities.",
            "How do we compete effectively when a HUBZone contract is full and open?",
            "Design a teaming strategy that preserves our HUBZone status.",
        ],
        "compliance_maintenance": [
            "Create an annual recertification checklist for HUBZone compliance.",
            "How do we document employee residency for SBA audit?",
            "What triggers require us to notify SBA of material changes?",
        ],
    },
}


class DomainPromptGenerator:
    """Generate prompts for a specific domain."""
    
    def __init__(self, domain_id: DomainID):
        self.domain = DOMAINS[domain_id]
        self.seed_prompts = SEED_PROMPTS.get(domain_id, {})
    
    def get_random_prompt(self, category: str = None) -> dict:
        """Get a random prompt, optionally from a specific category."""
        if category and category in self.seed_prompts:
            prompts = self.seed_prompts[category]
        else:
            # Flatten all categories
            prompts = [p for cat_prompts in self.seed_prompts.values() for p in cat_prompts]
        
        if not prompts:
            return {"error": "No prompts available for this domain"}
        
        prompt = random.choice(prompts)
        return {
            "domain": self.domain.id.value,
            "category": category or "mixed",
            "prompt": prompt,
            "quality_dimensions": [d.name for d in self.domain.dimensions],
            "key_terms": self.domain.key_terms
        }
    
    def get_all_prompts(self) -> List[dict]:
        """Get all seed prompts for this domain."""
        results = []
        for category, prompts in self.seed_prompts.items():
            for prompt in prompts:
                results.append({
                    "domain": self.domain.id.value,
                    "category": category,
                    "prompt": prompt
                })
        return results
    
    def evolve_prompt(self, base_prompt: str, evolution_type: str = "complexity") -> str:
        """
        Evolve a prompt using Evol-Instruct methodology.
        Evolution types: complexity, specificity, constraint, multi_step
        """
        evolutions = {
            "complexity": f"Make this task more complex by adding regulatory constraints:\n\n{base_prompt}",
            "specificity": f"Make this more specific with concrete numbers and requirements:\n\n{base_prompt}",
            "constraint": f"Add a difficult constraint that requires creative problem-solving:\n\n{base_prompt}",
            "multi_step": f"Expand this into a multi-step problem requiring planning:\n\n{base_prompt}",
        }
        return evolutions.get(evolution_type, base_prompt)


def generate_response_pair(prompt: str, generator_model, temperature_high: float = 0.9) -> tuple:
    """
    Generate two responses for pairwise comparison.
    Uses temperature variation to create natural quality differences.
    """
    # High-quality response (low temperature, more tokens)
    response_a = generator_model.generate(
        prompt, 
        temperature=0.3, 
        max_tokens=1024
    )
    
    # Potentially lower-quality response (high temperature)
    response_b = generator_model.generate(
        prompt, 
        temperature=temperature_high, 
        max_tokens=512
    )
    
    # Randomize order to avoid position bias
    if random.random() > 0.5:
        return response_a, response_b, "A"
    else:
        return response_b, response_a, "B"
