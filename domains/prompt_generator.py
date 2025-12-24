"""
Zuup Domain-Specific Prompt Generator
=====================================
Generates seed prompts for each domain to bootstrap preference collection.
Each domain has realistic, challenging prompts that require expert evaluation.
"""

import random
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class SeedPrompt:
    """A seed prompt for preference collection."""
    domain: str
    category: str
    prompt: str
    difficulty: str  # easy, medium, hard
    context: str = ""  # Optional additional context


# ═══════════════════════════════════════════════════════════════════════════════
# SEED PROMPTS BY DOMAIN
# ═══════════════════════════════════════════════════════════════════════════════

SEED_PROMPTS: Dict[str, List[SeedPrompt]] = {
    
    # ─────────────────────────────────────────────────────────────────────────
    # PROCUREMENT (Aureon)
    # ─────────────────────────────────────────────────────────────────────────
    "procurement": [
        SeedPrompt(
            domain="procurement",
            category="rfp_analysis",
            prompt="Analyze this RFP section and identify the key evaluation factors:\n\n'The Government will evaluate proposals using a best value tradeoff process. Technical approach and past performance are significantly more important than cost. Within technical, the subfactors are: (1) Understanding of Requirements, (2) Management Approach, (3) Staffing Plan. Past performance will be evaluated on relevance and quality.'",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="procurement",
            category="rfp_analysis",
            prompt="This solicitation includes FAR 52.219-14 (Limitations on Subcontracting). We're a small business prime with 45% of work going to our large business subcontractor. What are our compliance risks?",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="procurement",
            category="proposal_writing",
            prompt="Draft a technical approach section for a cybersecurity assessment contract. The SOW requires vulnerability scanning, penetration testing, and security posture assessment for a federal agency network with 5,000 endpoints.",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="procurement",
            category="proposal_writing",
            prompt="Write a past performance narrative for a software development project. Key facts: 18-month agile development, delivered 3 weeks early, zero critical defects at deployment, $2.1M contract value, client was DoD.",
            difficulty="easy"
        ),
        SeedPrompt(
            domain="procurement",
            category="far_dfars",
            prompt="Explain the implications of DFARS 252.204-7012 (Safeguarding Covered Defense Information) for a cloud services contractor. What are the key compliance requirements?",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="procurement",
            category="far_dfars",
            prompt="A CO has included FAR 52.232-40 (Providing Accelerated Payments to Small Business Subcontractors) in our contract. What are our obligations as the prime contractor?",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="procurement",
            category="pricing_strategy",
            prompt="We're pricing a T&M contract. Our fully burdened labor rate for a Senior Engineer is $185/hr, but the IGCE seems to expect rates around $145/hr. What strategies can we use to remain competitive while maintaining profitability?",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="procurement",
            category="pricing_strategy",
            prompt="Compare the risk allocation between FFP, CPFF, and T&M contract types for a software modernization effort with uncertain scope.",
            difficulty="medium"
        ),
    ],
    
    # ─────────────────────────────────────────────────────────────────────────
    # BIOMEDICAL (Symbion)
    # ─────────────────────────────────────────────────────────────────────────
    "biomedical": [
        SeedPrompt(
            domain="biomedical",
            category="biosensor_design",
            prompt="Design a biosensor specification for detecting enteric serotonin levels in the gut lumen. Consider signal-to-noise ratio, biocompatibility, and real-time telemetry requirements.",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="biomedical",
            category="biosensor_design",
            prompt="What materials should we consider for a chronic implantable biosensor that will remain in the GI tract for 30 days? Address biocompatibility, biofouling, and structural integrity.",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="biomedical",
            category="neural_analysis",
            prompt="Interpret this finding: Our GB-CI device detected a 3x increase in vagal afferent signaling 30 minutes post-prandial, correlating with increased SCFA production measured by the metabolite sensor. What mechanisms might explain this?",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="biomedical",
            category="neural_analysis",
            prompt="Design a stimulation protocol for selective vagus nerve stimulation targeting the gut-brain axis without affecting cardiac function.",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="biomedical",
            category="clinical_protocols",
            prompt="Draft key inclusion/exclusion criteria for a Phase 1 clinical trial of our GB-CI biosensor in patients with treatment-resistant depression.",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="biomedical",
            category="clinical_protocols",
            prompt="What adverse events should be specifically monitored in a study of an ingestible gut-brain interface device? Develop a monitoring and reporting plan.",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="biomedical",
            category="data_interpretation",
            prompt="Our biosensor array is showing periodic oscillations in gut motility data with a period of approximately 90 minutes. What physiological phenomenon might this represent, and how should we analyze it?",
            difficulty="medium"
        ),
    ],
    
    # ─────────────────────────────────────────────────────────────────────────
    # INGESTIBLE (Symbion HW)
    # ─────────────────────────────────────────────────────────────────────────
    "ingestible": [
        SeedPrompt(
            domain="ingestible",
            category="capsule_design",
            prompt="Our ingestible capsule needs to operate for 72 hours on a 30mAh battery. The device includes pH sensor, temperature sensor, accelerometer, and BLE transmitter. Optimize the power budget and duty cycling strategy.",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="ingestible",
            category="capsule_design",
            prompt="Design an antenna configuration for an ingestible capsule that must transmit through tissue to an external receiver worn on the abdomen. Consider frequency selection, SAR limits, and path loss.",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="ingestible",
            category="invivo_sensing",
            prompt="Our capsule's pH sensor shows drift of 0.3 pH units over 48 hours in bench testing. What calibration and compensation strategies can we implement given we cannot recalibrate once ingested?",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="ingestible",
            category="invivo_sensing",
            prompt="Develop an algorithm to detect gastric emptying events from our ingestible capsule's accelerometer and pH sensor data.",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="ingestible",
            category="regulatory_path",
            prompt="Our ingestible capsule is Class II device similar to existing capsule endoscopy devices, but adds novel biosensing capabilities. Should we pursue 510(k) or De Novo? Analyze the regulatory strategy.",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="ingestible",
            category="regulatory_path",
            prompt="What clinical evidence will FDA likely require for our ingestible gut-brain interface device? Consider both safety and effectiveness endpoints.",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="ingestible",
            category="manufacturing",
            prompt="Develop a batch release testing protocol for our ingestible capsules. Include bioburden, seal integrity, electronic functionality, and battery capacity tests.",
            difficulty="medium"
        ),
    ],
    
    # ─────────────────────────────────────────────────────────────────────────
    # LEGACY (Relian)
    # ─────────────────────────────────────────────────────────────────────────
    "legacy": [
        SeedPrompt(
            domain="legacy",
            category="cobol_analysis",
            prompt="""Analyze this COBOL paragraph and document its business logic:

CALCULATE-INTEREST.
    IF ACCOUNT-TYPE = 'S'
        COMPUTE INTEREST-AMT = BALANCE * SAVINGS-RATE / 12
    ELSE IF ACCOUNT-TYPE = 'C'
        IF BALANCE < MINIMUM-BAL
            COMPUTE INTEREST-AMT = 0
            COMPUTE FEE-AMT = MONTHLY-FEE
        ELSE
            COMPUTE INTEREST-AMT = BALANCE * CHECK-RATE / 12
        END-IF
    END-IF.
    ADD INTEREST-AMT TO BALANCE.
    SUBTRACT FEE-AMT FROM BALANCE.""",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="legacy",
            category="cobol_analysis",
            prompt="This COBOL program has 50,000 lines and references 200 copybooks. How would you approach creating a dependency map and identifying dead code?",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="legacy",
            category="migration_strategy",
            prompt="We have a batch COBOL system running on z/OS that processes 2 million transactions nightly with a 4-hour batch window. Compare rehosting to Linux vs. refactoring to Java, considering risk, timeline, and cost.",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="legacy",
            category="migration_strategy",
            prompt="Our CICS transaction system has 500 BMS maps. What's the recommended approach for migrating these to a modern web interface?",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="legacy",
            category="code_translation",
            prompt="""Translate this COBOL data structure to a Java class:

01  CUSTOMER-RECORD.
    05  CUST-ID              PIC 9(10).
    05  CUST-NAME.
        10  FIRST-NAME       PIC X(25).
        10  LAST-NAME        PIC X(35).
    05  CUST-ADDRESS.
        10  STREET           PIC X(50).
        10  CITY             PIC X(30).
        10  STATE            PIC X(2).
        10  ZIP              PIC 9(5)V9(4).
    05  ACCOUNT-BAL          PIC S9(9)V99 COMP-3.""",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="legacy",
            category="testing_validation",
            prompt="Design a testing strategy to validate that our migrated Java application produces identical outputs to the original COBOL system for all business scenarios.",
            difficulty="hard"
        ),
    ],
    
    # ─────────────────────────────────────────────────────────────────────────
    # AUTONOMY (Veyra)
    # ─────────────────────────────────────────────────────────────────────────
    "autonomy": [
        SeedPrompt(
            domain="autonomy",
            category="agent_design",
            prompt="Design a goal hierarchy for an autonomous research agent that can browse the web, read papers, and synthesize findings. How do you balance exploration vs. exploitation?",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="autonomy",
            category="agent_design",
            prompt="Specify a memory architecture for a long-running agent that needs to maintain context across thousands of interactions while managing token limits.",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="autonomy",
            category="safety_constraints",
            prompt="Define safety invariants for an autonomous coding agent that can read/write files, execute code, and access the internet. What actions should require human approval?",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="autonomy",
            category="safety_constraints",
            prompt="Design a human override mechanism for an autonomous agent that can interrupt any action within 100ms but doesn't create constant interruption fatigue.",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="autonomy",
            category="multi_agent",
            prompt="Design a negotiation protocol for resource allocation among 10 autonomous agents with different objectives competing for limited compute and API rate limits.",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="autonomy",
            category="multi_agent",
            prompt="How should we handle conflicts when two agents have contradictory goals? Design a resolution mechanism that doesn't require human intervention for every conflict.",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="autonomy",
            category="verification",
            prompt="Design a test suite to verify that an autonomous agent remains aligned with its specified objectives over thousands of interactions.",
            difficulty="hard"
        ),
    ],
    
    # ─────────────────────────────────────────────────────────────────────────
    # QUANTUM ARCHAEOLOGY (QAWM)
    # ─────────────────────────────────────────────────────────────────────────
    "quantum_arch": [
        SeedPrompt(
            domain="quantum_arch",
            category="temporal_modeling",
            prompt="We have radiocarbon dates for 50 artifacts from a site, but they don't form a coherent chronology. Some dates seem inverted relative to stratigraphy. How should we build a Bayesian chronological model that accounts for these discrepancies?",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="quantum_arch",
            category="temporal_modeling",
            prompt="Quantify the uncertainty in a historical event date when we have: (1) a terminus post quem from a coin, (2) two conflicting textual references, and (3) dendrochronology from associated timbers.",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="quantum_arch",
            category="artifact_analysis",
            prompt="We've identified three possible quarry sources for obsidian artifacts. Design a probabilistic framework for source attribution given XRF elemental composition data.",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="quantum_arch",
            category="quantum_algorithms",
            prompt="How could we use QAOA to optimize the selection of excavation units given constraints on budget, access, and expected information gain?",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="quantum_arch",
            category="quantum_algorithms",
            prompt="Design a quantum sampling approach for generating plausible reconstructions of a partially preserved ancient text from fragmentary evidence.",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="quantum_arch",
            category="data_integration",
            prompt="Integrate these data sources for a Bronze Age site: (1) ceramic typology suggesting 1400-1200 BCE, (2) radiocarbon dates centering on 1550 BCE, (3) Egyptian imports dated to Thutmose III. Resolve the apparent contradictions.",
            difficulty="hard"
        ),
    ],
    
    # ─────────────────────────────────────────────────────────────────────────
    # DEFENSE WORLD MODELS (Orb)
    # ─────────────────────────────────────────────────────────────────────────
    "defense_wm": [
        SeedPrompt(
            domain="defense_wm",
            category="scene_reconstruction",
            prompt="Design a multi-sensor fusion architecture for building a 3D world model from: (1) satellite imagery at 0.5m resolution, (2) UAV video at 4K, (3) ground-level panoramic photos. Address registration, scale, and temporal alignment.",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="defense_wm",
            category="scene_reconstruction",
            prompt="We're using NeRF for 3D reconstruction from aerial imagery. The scene includes both static structures and moving vehicles. How should we modify the approach to handle dynamic elements?",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="defense_wm",
            category="isr_analysis",
            prompt="Design a change detection methodology for identifying new construction at a facility using bi-temporal satellite imagery. Consider shadow effects, seasonal variation, and false positive suppression.",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="defense_wm",
            category="isr_analysis",
            prompt="Develop an activity pattern analysis framework to characterize the operational tempo of a logistics hub from 30 days of overhead imagery.",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="defense_wm",
            category="geospatial",
            prompt="Given a DEM and vehicle specifications, compute optimal routes considering trafficability, cover/concealment, and fuel consumption. Output should support what-if analysis.",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="defense_wm",
            category="simulation",
            prompt="Design a scenario generation methodology for training ML models on rare events using our world model. How do we ensure diversity while maintaining physical plausibility?",
            difficulty="hard"
        ),
    ],
    
    # ─────────────────────────────────────────────────────────────────────────
    # HALAL (Civium)
    # ─────────────────────────────────────────────────────────────────────────
    "halal": [
        SeedPrompt(
            domain="halal",
            category="certification",
            prompt="Our food manufacturing facility also processes pork products on separate lines. What measures are required to obtain halal certification for our non-pork lines? Address equipment, timing, and cleaning protocols.",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="halal",
            category="certification",
            prompt="Compare the certification requirements of JAKIM (Malaysia), ESMA (UAE), and MUI (Indonesia). What are the key differences a multinational company should be aware of?",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="halal",
            category="supply_chain",
            prompt="Design a traceability system to verify halal status from slaughter to final product for a meat processing operation that sources from 50 suppliers.",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="halal",
            category="supply_chain",
            prompt="Our supplier has changed the source of a gelatin ingredient. Previously it was fish-derived, now it's bovine-derived but halal-certified. What verification steps are needed?",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="halal",
            category="ingredient_analysis",
            prompt="Evaluate these E-numbers for halal status: E120 (carmine), E441 (gelatin), E471 (mono/diglycerides), E904 (shellac). What additional information would you need for definitive determination?",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="halal",
            category="ingredient_analysis",
            prompt="A flavoring supplier provides 'natural vanilla flavor' with an ethanol carrier. Analyze the halal status and recommend alternatives if needed.",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="halal",
            category="documentation",
            prompt="Develop a halal control plan template for a snack food manufacturer. Include critical control points, monitoring procedures, and corrective actions.",
            difficulty="medium"
        ),
    ],
    
    # ─────────────────────────────────────────────────────────────────────────
    # MOBILE DATA CENTER (PodX)
    # ─────────────────────────────────────────────────────────────────────────
    "mobile_dc": [
        SeedPrompt(
            domain="mobile_dc",
            category="edge_compute",
            prompt="Design a workload placement algorithm for a mobile data center with 4 GPU nodes and 8 CPU nodes. Workloads include ML inference, database queries, and video transcoding with varying latency requirements.",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="mobile_dc",
            category="edge_compute",
            prompt="Our edge deployment runs a 7B parameter LLM. Optimize the inference pipeline for minimum latency given: 32GB GPU RAM, intermittent power, and 100ms target response time.",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="mobile_dc",
            category="ddil_ops",
            prompt="Design a data synchronization strategy for a mobile data center that has satellite connectivity for 4 hours/day at 2Mbps. Local data generation is approximately 50GB/day.",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="mobile_dc",
            category="ddil_ops",
            prompt="How should our edge system handle a 72-hour complete connectivity blackout? Address data persistence, autonomous operation, and eventual consistency.",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="mobile_dc",
            category="tactical_infra",
            prompt="Our mobile data center is deploying to a location with ambient temperature of 50°C. Design the thermal management approach given 50kW of compute load and no external power for HVAC.",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="mobile_dc",
            category="tactical_infra",
            prompt="Develop a rapid deployment checklist for a containerized data center. From truck arrival to operational status should be under 2 hours.",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="mobile_dc",
            category="security",
            prompt="Design a zero-trust architecture for an edge data center that may be physically accessed by adversaries. Include data-at-rest encryption, key management, and tamper response.",
            difficulty="hard"
        ),
    ],
    
    # ─────────────────────────────────────────────────────────────────────────
    # HUBZONE (Aureon)
    # ─────────────────────────────────────────────────────────────────────────
    "hubzone": [
        SeedPrompt(
            domain="hubzone",
            category="certification",
            prompt="Our company has 45 employees. 20 work at HQ in a HUBZone, 15 work remotely (10 in HUBZones), and 10 work at a client site in a non-HUBZone. Do we meet the 35% employee residence requirement?",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="hubzone",
            category="certification",
            prompt="We're a tech company where most employees work remotely. What documentation will SBA require to verify their residences are in HUBZones?",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="hubzone",
            category="contracting",
            prompt="We're a HUBZone small business competing on a set-aside contract valued at $3.5 million. Explain the limitations on subcontracting and how our teaming arrangement with a large business should be structured.",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="hubzone",
            category="contracting",
            prompt="Calculate the price evaluation preference for a HUBZone firm bidding $1,050,000 against a non-HUBZone firm bidding $1,000,000 on a full and open competition.",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="hubzone",
            category="compliance",
            prompt="Our principal office HUBZone has been redesignated as non-HUBZone. We have ongoing contracts with HUBZone set-asides. What are our obligations and options?",
            difficulty="hard"
        ),
        SeedPrompt(
            domain="hubzone",
            category="compliance",
            prompt="We're approaching our 3-year recertification. Two employees who lived in HUBZones have moved to non-HUBZone areas. How does this affect our certification status?",
            difficulty="medium"
        ),
        SeedPrompt(
            domain="hubzone",
            category="teaming",
            prompt="Analyze whether a joint venture between our HUBZone firm and a large business mentor would qualify for HUBZone set-asides. What are the key requirements?",
            difficulty="hard"
        ),
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# GENERATOR FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_random_prompt(domain_id: str, category_id: str = None) -> SeedPrompt:
    """Get a random prompt from a domain, optionally filtered by category."""
    prompts = SEED_PROMPTS.get(domain_id, [])
    if not prompts:
        # Return a generic prompt if domain not found
        return SeedPrompt(
            domain=domain_id,
            category="general",
            prompt=f"Provide expert guidance on a {domain_id} topic.",
            difficulty="medium"
        )
    
    if category_id:
        prompts = [p for p in prompts if p.category == category_id]
        if not prompts:
            prompts = SEED_PROMPTS[domain_id]
    
    return random.choice(prompts)


def get_all_prompts(domain_id: str) -> List[SeedPrompt]:
    """Get all prompts for a domain."""
    return SEED_PROMPTS.get(domain_id, [])


def get_prompts_by_difficulty(domain_id: str, difficulty: str) -> List[SeedPrompt]:
    """Get prompts filtered by difficulty level."""
    prompts = SEED_PROMPTS.get(domain_id, [])
    return [p for p in prompts if p.difficulty == difficulty]


def get_prompt_stats() -> Dict[str, Dict]:
    """Get statistics about available prompts."""
    stats = {}
    for domain_id, prompts in SEED_PROMPTS.items():
        categories = {}
        difficulties = {"easy": 0, "medium": 0, "hard": 0}
        
        for p in prompts:
            categories[p.category] = categories.get(p.category, 0) + 1
            difficulties[p.difficulty] = difficulties.get(p.difficulty, 0) + 1
        
        stats[domain_id] = {
            "total": len(prompts),
            "categories": categories,
            "difficulties": difficulties
        }
    
    return stats


def generate_prompt_pair(domain_id: str) -> Tuple[SeedPrompt, str, str]:
    """
    Generate a prompt with two placeholder responses for comparison.
    In production, replace placeholders with actual LLM responses.
    """
    prompt = get_random_prompt(domain_id)
    
    # Placeholder responses - replace with actual LLM calls
    response_a = f"[Response A - Generated response to: {prompt.prompt[:100]}...]"
    response_b = f"[Response B - Generated response to: {prompt.prompt[:100]}...]"
    
    return prompt, response_a, response_b

