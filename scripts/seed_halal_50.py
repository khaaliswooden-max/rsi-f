# File: scripts/seed_halal_50.py
"""
50 synthetic halal (Civium) preferences for DPO cold-start.
Run: python scripts/seed_halal_50.py
"""

import httpx
import asyncio
import os
from datetime import datetime

API_BASE = "https://zuup1-zuup-preference-collection.hf.space"
API_KEY = os.getenv("ZUUP_API_KEY", "zuup-seed-key")

HALAL_PREFERENCES = [
    # ============ CERTIFICATION (13 items) ============
    {
        "category": "certification",
        "prompt": "What are the major halal certification bodies and how do they differ?",
        "chosen": """**Major global halal certification bodies:**

| Organization | Country | Recognition | Scope |
|--------------|---------|-------------|-------|
| JAKIM | Malaysia | Gold standard, widely accepted | Comprehensive |
| MUI-LPPOM | Indonesia | Largest Muslim population | Food, cosmetics, pharma |
| IFANCA | USA | North American leader | Food, supplements |
| ISNA | Canada/USA | Broad recognition | Food products |
| HFA | UK | European market | Meat, food products |
| ESMA | UAE | Gulf region standard | Broad scope |
| SMIIC | OIC members | International standard (OIC/SMIIC) | Harmonization |

**Key differences:**

**1. Standards framework:**
- JAKIM: MS 1500:2019 (Malaysian Standard)
- MUI: HAS 23000 system
- Gulf: GSO 2055-1 (GCC Standardization Org)
- OIC: OIC/SMIIC 1:2019 (harmonized)

**2. Slaughter requirements:**
| Aspect | Stricter Bodies | More Flexible |
|--------|-----------------|---------------|
| Stunning | Prohibited (some HFA) | Permitted pre-slaughter (some) |
| Mechanical slaughter | Manual only | Mechanical with conditions |
| Tasmiyyah | Each animal | Continuous recitation |

**3. Alcohol tolerance:**
- Zero tolerance: JAKIM, MUI (0.0%)
- Technical trace: Some bodies allow <0.5% in non-beverage

**4. Cross-contamination:**
- JAKIM: Sertu (ritual cleansing) required for pork contact
- Others: Thorough cleaning may suffice

**Selection criteria:** Choose certifier recognized in your target export markets. Malaysian/Indonesian markets require JAKIM/MUI recognition.""",
        "rejected": "There are many halal certification bodies like JAKIM, MUI, and IFANCA. They have different standards for different countries."
    },
    {
        "category": "certification",
        "prompt": "What is the halal certification process for a food manufacturing facility?",
        "chosen": """**Halal certification process (typical 3-6 month timeline):**

**Phase 1: Pre-Application (2-4 weeks)**

1. **Gap assessment**
   - Review all ingredients against halal requirements
   - Identify non-halal or mashbooh (doubtful) items
   - Assess production line contamination risks
   - Evaluate supplier halal status

2. **Documentation preparation**
   - Ingredient list with supplier certificates
   - Production flowcharts
   - Cleaning procedures (SOPs)
   - HACCP/food safety documentation

**Phase 2: Application (1-2 weeks)**

Required documents:
- Application form
- Company registration
- Product specifications
- Ingredient declarations (all components)
- Supplier halal certificates
- Manufacturing process flow
- Plant layout diagram
- Cleaning/sanitation SOPs
- Quality management system docs

**Phase 3: Document Review (2-4 weeks)**
- Certifier reviews all submissions
- Queries on unclear ingredients
- Request for additional documentation
- Preliminary approval to proceed

**Phase 4: Facility Audit (1-2 days)**

| Audit Area | Key Checks |
|------------|------------|
| Receiving | Ingredient verification, storage segregation |
| Storage | Halal/non-halal separation, labeling |
| Production | Line dedication or cleaning validation |
| Equipment | Shared equipment protocols |
| Personnel | Training, awareness |
| Documentation | Traceability, records |

**Phase 5: Corrective Actions (if needed, 2-4 weeks)**
- Address non-conformances
- Submit evidence of corrections
- Re-audit if major findings

**Phase 6: Certification Decision (1-2 weeks)**
- Committee review
- Certificate issuance
- Validity: Typically 1-2 years

**Ongoing requirements:**
- Annual surveillance audits
- Ingredient change notifications
- Renewal application before expiry""",
        "rejected": "Apply to a certification body, submit your documents, get audited, and receive your certificate if you pass."
    },
    {
        "category": "certification",
        "prompt": "What is the difference between halal and halal-certified?",
        "chosen": """**Halal vs. Halal-Certified distinction:**

**Halal:**
- Intrinsic religious status
- Means "permissible" in Islamic law
- Determined by Shariah principles
- Does not require third-party verification
- Examples: Fresh fruits, vegetables, water, most grains

**Halal-Certified:**
- Third-party verified halal status
- Documented compliance with standards
- Audited production process
- Traceable supply chain
- Certificate issued by recognized body

**Why certification matters for processed foods:**

| Factor | Uncertified | Certified |
|--------|-------------|-----------|
| Ingredient verification | Unknown | Verified halal |
| Cross-contamination | Unknown risk | Controlled |
| Processing aids | May be non-halal | Verified |
| Supply chain | Untraced | Documented |
| Market access | Limited | Export-ready |
| Consumer trust | Variable | High |

**When certification is essential:**

1. **Processed foods** - Hidden ingredients, processing aids
2. **Meat products** - Slaughter method verification
3. **Export markets** - Regulatory requirement
4. **Retail/foodservice** - Consumer expectation
5. **Ingredients** - B2B supply chain requirement

**When certification may be unnecessary:**

1. **Whole natural foods** - Unprocessed fruits, vegetables
2. **Water** - Plain, unflavored
3. **Salt, sugar** - Pure, unprocessed forms
4. **Personal consumption** - Individual religious judgment

**Key insight:** "Halal" is a religious determination; "halal-certified" is a commercial verification system that provides assurance and market access.

**Mashbooh (doubtful) category:**
Items without clear halal/haram status require investigation or certification to resolve doubt.""",
        "rejected": "Halal means permissible in Islam. Halal-certified means a certification body has verified it meets halal standards."
    },
    {
        "category": "certification",
        "prompt": "How do I get halal certification recognized in multiple countries?",
        "chosen": """**Multi-country halal certification strategy:**

**Approach 1: Mutual Recognition Agreements (MRAs)**

Many certification bodies have bilateral recognition:

JAKIM (Malaysia) recognizes:
- MUI-LPPOM (Indonesia)
- MUIS (Singapore)
- CICOT (Thailand)
- IFANCA (USA)
- ISNA (Canada)
- Selected others (70+ bodies)

**Check recognition status:**
- JAKIM: halal.gov.my (official recognized list)
- MUI: halalmui.org
- UAE ESMA: Listed approved bodies

**Approach 2: Multiple Certifications**

For maximum market access, obtain certifications from:

| Target Market | Recommended Certifier |
|---------------|----------------------|
| Malaysia | JAKIM or JAKIM-recognized |
| Indonesia | MUI-LPPOM |
| Gulf/MENA | ESMA, GSO-compliant body |
| Singapore | MUIS |
| USA/Canada | IFANCA, ISNA |
| Europe | HFA, recognized EU bodies |
| Global (OIC) | SMIIC-accredited body |

**Approach 3: SMIIC Accreditation**

OIC/SMIIC standards provide harmonized framework:

- **OIC/SMIIC 1:2019** - General requirements
- **OIC/SMIIC 2** - Conformity assessment bodies
- Bodies accredited to SMIIC standards gain broader recognition

**Practical implementation:**
Decision framework:
1. Identify primary target market -> select primary certifier
2. Check if primary covers other markets via recognition
3. Identify gaps requiring additional certification
4. Coordinate audit schedules to reduce costs

**Cost optimization:**
- Use one certifier with broad recognition where possible
- Coordinate audit schedules to reduce travel costs
- Leverage existing food safety audits (GFSI) for efficiency""",
        "rejected": "Get certification from a body recognized in multiple countries, or get separate certifications for each market you want to enter."
    },
    {
        "category": "certification",
        "prompt": "What are the common reasons for halal certification rejection or suspension?",
        "chosen": """**Halal certification rejection/suspension causes:**

**Category 1: Ingredient Issues (Most Common)**

| Issue | Example | Severity |
|-------|---------|----------|
| Non-halal ingredient | Pork gelatin, lard | Critical - Rejection |
| Unverified ingredient | Missing halal certificate | Major |
| Alcohol content | >0.5% or any in some schemes | Critical |
| Doubtful E-numbers | E120 (carmine), E441 (gelatin) | Major |
| Undeclared processing aids | Pork-derived enzymes | Critical |

**Category 2: Cross-Contamination**

| Issue | Description | Resolution |
|-------|-------------|------------|
| Shared equipment | Same line for halal/non-halal | Dedicated or validated cleaning |
| Storage mixing | Non-halal stored with halal | Physical segregation |
| Transport contamination | Shared vehicles | Dedicated or cleaning protocol |
| Utensil sharing | Same tools for both | Color-coded, dedicated sets |

**Category 3: Slaughter Non-Conformance (Meat)**

- Non-Muslim slaughterman
- Missing Tasmiyyah (invocation)
- Improper stunning (prohibited types)
- Incomplete bleeding
- Animal welfare violations

**Category 4: Documentation Failures**

Common gaps:
- Expired supplier certificates
- Incomplete traceability records
- Missing batch records
- Undocumented ingredient changes
- Inadequate cleaning logs
- No training records

**Category 5: Systemic Issues**

| Issue | Impact |
|-------|--------|
| No Halal Assurance System | Cannot demonstrate control |
| Inadequate training | Staff unaware of requirements |
| No internal audit | Issues undetected |
| Management commitment lacking | Resources insufficient |

**Suspension triggers:**
1. Failed surveillance audit
2. Consumer complaint (verified)
3. Undeclared product/ingredient change
4. Use of certificate on non-certified products
5. Misrepresentation of halal status

**Reinstatement process:**
1. Root cause analysis
2. Corrective action implementation
3. Evidence submission
4. Re-audit (usually required)
5. Committee review
6. Certificate reinstatement

**Prevention:** Implement robust Halal Assurance System (HAS) with internal audits, change control, and continuous monitoring.""",
        "rejected": "Certifications get rejected for using non-halal ingredients, cross-contamination, or documentation problems. Fix the issues and reapply."
    },
    {
        "category": "certification",
        "prompt": "What is a Halal Assurance System (HAS) and what are its components?",
        "chosen": """**Halal Assurance System (HAS) = Management system ensuring consistent halal compliance**

Based on MUI HAS 23000 and similar frameworks.

**Core components:**

**1. Halal Policy**
- Top management commitment statement
- Scope of halal commitment
- Communication to all stakeholders
- Signed and dated

**2. Halal Management Team**

| Role | Responsibility |
|------|----------------|
| Halal Committee Chair | Overall accountability |
| Halal Coordinator | Day-to-day management |
| Production Rep | Manufacturing compliance |
| Purchasing Rep | Ingredient/supplier control |
| QA Rep | Testing, verification |
| Internal Auditor | Compliance checking |

**3. Training and Education**
- All employees: Halal awareness (annual)
- Production staff: Handling procedures
- Purchasing: Supplier verification
- QA: Testing, documentation
- Internal auditors: Audit techniques
- Management: System oversight

**4. Materials (Ingredient Control)**
- Approved ingredient list
- Supplier halal certificates
- Certificate validity tracking
- New ingredient approval process
- Specification management

**5. Products**
- Product registration with certifier
- Formulation control
- Label compliance
- Product change management

**6. Production Facilities**

| Element | Requirement |
|---------|-------------|
| Layout | Segregation where needed |
| Equipment | Dedicated or cleaning protocol |
| Storage | Halal/non-halal separation |
| Utilities | No contamination risk |

**7. Written Procedures (SOPs)**
Critical procedures:
- Ingredient receiving and verification
- Production line setup/changeover
- Cleaning and sanitation
- Non-conformance handling
- Traceability and recall

**8. Traceability**
- Forward trace: Ingredient to Batch to Product to Customer
- Backward trace: Customer complaint to Product to Batch to Ingredients

**9. Handling of Non-Conforming Products**
- Identification and segregation
- Investigation and root cause
- Disposition decision
- Corrective action
- Preventive measures

**10. Internal Audit**
- Minimum annual frequency
- Trained internal auditors
- Checklist-based verification
- Findings and corrective actions
- Management review

**11. Management Review**
- Regular review meetings (minimum annual)
- Review of audit results, complaints, changes
- Resource allocation
- Improvement decisions

**Integration with food safety:**
HAS integrates with HACCP, ISO 22000, FSSC 22000—many controls overlap, reducing duplication.""",
        "rejected": "HAS is a management system for halal compliance with components like policies, training, procedures, and audits."
    },
    {
        "category": "certification",
        "prompt": "How does halal certification differ for cosmetics versus food products?",
        "chosen": """**Halal cosmetics vs. food certification comparison:**

**Fundamental difference:**
- Food: Ingested (internal consumption)
- Cosmetics: Applied externally (but may enter body through skin, lips, etc.)

**Scope of halal requirements:**

| Aspect | Food | Cosmetics |
|--------|------|-----------|
| Ingredient source | Critical | Critical |
| Processing | Must be halal | Must be halal |
| Cross-contamination | Strict control | Strict control |
| Alcohol | Generally prohibited | Debated (see below) |
| Animal testing | Not typically addressed | May be included |
| Najs (impure) contact | Prohibited | Prohibited |

**Cosmetics-specific considerations:**

**1. Alcohol in cosmetics:**

| Position | Ruling | Bodies |
|----------|--------|--------|
| Prohibited all | No alcohol whatsoever | Some stricter bodies |
| Synthetic permitted | Synthetic alcohol OK, grape/date prohibited | Many bodies |
| Functional permitted | Ethanol as solvent OK if evaporates | Some bodies |
| Case-by-case | Depends on source and function | Varies |

**2. Common problematic cosmetic ingredients:**

| Ingredient | Source Concern | Halal Alternative |
|------------|----------------|-------------------|
| Collagen | Often porcine | Marine, plant-based |
| Glycerin | May be animal fat | Vegetable glycerin |
| Stearic acid | Animal fat | Plant-derived |
| Keratin | May be animal | Plant, synthetic |
| Carmine (CI 75470) | Insect-derived | Synthetic colorants |
| Lanolin | Sheep (halal if from halal slaughter) | Plant alternatives |
| Placenta extracts | Animal source | Prohibited |

**3. Additional cosmetics requirements:**
- MS 2200:2008 (Malaysia) - Islamic consumer goods
- HAS 23201 (MUI) - Cosmetics
- GSO 2055-2 (Gulf) - Cosmetics & personal care
- OIC/SMIIC 4 - Cosmetics

**4. Certification process differences:**

| Step | Food | Cosmetics |
|------|------|-----------|
| Ingredient review | Food additives focus | Wider raw material scope |
| Facility audit | Food safety integration | May include GMP cosmetics |
| Testing | May include alcohol testing | Ingredient verification focus |
| Labeling | Nutrition + halal | Ingredient list + halal |

**5. Toyyib (wholesome) considerations:**
Cosmetics standards increasingly incorporate:
- No harmful ingredients
- No carcinogens
- Environmental responsibility
- Cruelty-free (no animal testing)

**Market insight:** Halal cosmetics is fastest-growing segment. Muslim consumers increasingly seek halal-certified personal care products.""",
        "rejected": "Cosmetics certification focuses on ingredients like collagen and glycerin sources. Alcohol rules vary between certification bodies."
    },
    {
        "category": "certification",
        "prompt": "What is the role of the Internal Halal Committee and who should be on it?",
        "chosen": """**Internal Halal Committee (IHC) structure and function:**

**Purpose:** Governing body responsible for implementing and maintaining halal compliance within the organization.

**Minimum composition:**

| Role | Qualifications | Responsibilities |
|------|----------------|------------------|
| **Chairperson** | Senior management, halal trained | Overall accountability, resources |
| **Halal Executive/Coordinator** | Full-time, halal certified | Day-to-day implementation |
| **Production Representative** | Process knowledge | Manufacturing compliance |
| **QA/QC Representative** | Quality background | Testing, verification |
| **Purchasing Representative** | Procurement authority | Supplier management |
| **R&D Representative** | Formulation knowledge | New product development |
| **Warehouse/Logistics** | Operations knowledge | Storage, distribution |

**For larger organizations, add:**
- Internal Halal Auditor (trained, may be separate from committee)
- Shariah Advisor (for complex rulings)
- HR Representative (training coordination)

**IHC meeting requirements:**
- Frequency: Minimum quarterly
- Agenda items: Review of halal status, non-conformance review, audit findings, supplier certificate status, new product approvals, training status, customer complaints
- Documentation: Meeting minutes (signed), attendance record, action items with deadlines

**Key responsibilities matrix:**

| Activity | Responsible | Accountable | Consulted | Informed |
|----------|-------------|-------------|-----------|----------|
| Ingredient approval | QA | Halal Exec | R&D, Purchasing | Production |
| Supplier approval | Purchasing | Halal Exec | QA | Finance |
| Production monitoring | Production | Halal Exec | QA | Chair |
| Internal audit | Auditor | Chair | All | Management |
| Non-conformance | QA | Halal Exec | Production | Chair |
| Training | HR | Halal Exec | All | Management |

**Halal Executive qualifications:**

1. **Training:** Certified halal executive course (JAKIM, MUI, or equivalent)
2. **Knowledge:** Understanding of Islamic dietary laws
3. **Experience:** Food industry background preferred
4. **Authority:** Empowered to stop production if needed
5. **Independence:** Can report directly to top management

**Muslim requirement:**
- Most schemes require Halal Executive to be Muslim
- Committee should have Muslim representation
- Non-Muslim members permitted in supporting roles

**Performance indicators:**

| KPI | Target |
|-----|--------|
| Audit non-conformances | Zero critical |
| Supplier certificate validity | 100% current |
| Training completion | 100% of required staff |
| Corrective action closure | Within 30 days |
| Internal audit completion | Per schedule |""",
        "rejected": "The Internal Halal Committee includes representatives from management, production, QA, and purchasing. They meet regularly to oversee halal compliance."
    },
    {
        "category": "certification",
        "prompt": "How do I handle a halal certification for contract manufacturing?",
        "chosen": """**Contract manufacturing halal certification approaches:**

**Scenario types:**

| Scenario | Certification Holder | Complexity |
|----------|---------------------|------------|
| Brand owner uses certified co-packer | Co-packer | Low |
| Brand owner uses non-certified co-packer | Brand owner | High |
| Co-packer offers halal service | Co-packer | Medium |
| Shared certification | Both parties | Complex |

**Approach 1: Co-packer holds certification**
- Brand Owner provides formulation to Co-Packer (Certified)
- Co-Packer manufactures under their certificate
- Brand Owner uses co-packer's halal logo

**Requirements:**
- Verify co-packer's certificate is valid
- Confirm product is within their scope
- Contractual halal requirements
- Right to audit

**Approach 2: Brand owner holds certification**
- Brand Owner submits co-packer facility as manufacturing site
- Co-packer facility audited as extension of brand owner's scope
- Brand owner responsible for compliance
- Co-packer implements brand owner's HAS
- Contract includes halal obligations

**Contractual requirements:**

Ingredient control:
- Only approved halal ingredients
- Certificates provided to brand owner
- Prior written approval for changes

Production control:
- Dedicated or validated changeover
- Batch records maintained
- Physical separation from non-halal

Audit rights:
- Annual minimum + for-cause
- 48 hours notice or unannounced
- Full access to halal-related areas

Non-conformance:
- Immediate notification upon discovery
- Product quarantine required
- Joint root cause analysis

Liability:
- Indemnification for losses
- Recall cost sharing arrangement
- Product liability coverage

**Due diligence checklist:**

| Item | Verification |
|------|--------------|
| Halal certificate | Valid, scope covers product type |
| Certification body | Recognized by target markets |
| Facility audit | Personal visit or third-party |
| Ingredient control | Approved supplier list |
| Segregation | Physical or temporal separation |
| Traceability | Batch tracking capability |
| Staff training | Halal awareness program |
| Previous issues | History of non-conformances |

**Risk mitigation:** Conduct initial and periodic audits. Include halal KPIs in supplier scorecard.""",
        "rejected": "Either the co-packer has certification and you use their logo, or you include their facility in your certification scope and audit them."
    },
    {
        "category": "certification",
        "prompt": "What are the key differences between Malaysian (JAKIM) and Indonesian (MUI) halal standards?",
        "chosen": """**JAKIM vs. MUI halal standards comparison:**

**Overview:**

| Aspect | JAKIM (Malaysia) | MUI-LPPOM (Indonesia) |
|--------|------------------|----------------------|
| Standard | MS 1500:2019 | HAS 23000 |
| Authority | Government (JAKIM) | Semi-government (MUI + BPJPH) |
| Mandatory | Yes (for domestic) | Yes (Law 33/2014) |
| Validity | 2 years | 4 years (new law) |

**Ingredient requirements:**

| Issue | JAKIM | MUI |
|-------|-------|-----|
| Alcohol | Zero tolerance | Khamr (intoxicating) prohibited; synthetic case-by-case |
| Stunning | Prohibited (generally) | Permitted with conditions |
| Mechanical slaughter | Manual preferred | Permitted with conditions |
| Gelatin | Must be halal-certified | Must be halal-certified |
| Enzymes | Case-by-case, halal source required | Detailed in positive list |

**Alcohol specifics:**

**JAKIM position:**
- Any alcohol in final product: Not halal
- Alcohol as processing aid: Must be removed
- Natural fermentation: Must be controlled <0.5%

**MUI position:**
- Khamr (wine, beer, liquor): Absolutely prohibited
- Industrial alcohol (synthetic): May be permitted as processing aid
- Ethanol from non-khamr: Case-by-case evaluation
- Final product: Should not contain intoxicating amount

**Facility requirements:**

| Requirement | JAKIM | MUI |
|-------------|-------|-----|
| Sertu (ritual cleansing) | Required if pork/dog contact | Recommended, not always required |
| Dedicated facility | Preferred, not mandatory | Risk-based approach |
| Muslim workers | Required for slaughter | Required for slaughter |
| Halal committee | Mandatory | Mandatory (Internal Halal Team) |

**Documentation differences:**

JAKIM requires: MyeHalal online system submission, company profile, product details + formulations, HACCP certificate (if applicable), halal certificates (ingredients), manufacturing process flow

MUI requires: CEROL online system, HAS manual, internal auditor appointment, training records, detailed ingredient matrix, SOP for halal critical points

**Audit approach:**

| Aspect | JAKIM | MUI |
|--------|-------|-----|
| Frequency | Annual minimum | Based on risk category |
| Duration | 1-2 days typical | 1-3 days |
| Focus | Documentation + facility | HAS implementation |
| Unannounced | Yes, possible | Yes, possible |

**Mutual recognition:**
- JAKIM recognizes MUI (with conditions)
- MUI recognizes JAKIM
- Products certified by one may need verification for the other

**Practical implication:**
If targeting both markets, align to stricter requirement (usually JAKIM on alcohol, MUI on HAS documentation). Consider dual certification for sensitive products.""",
        "rejected": "JAKIM is stricter on alcohol with zero tolerance. MUI has more detailed HAS requirements. Both recognize each other's certification."
    },
    {
        "category": "certification",
        "prompt": "How do I certify a restaurant or food service operation as halal?",
        "chosen": """**Halal foodservice certification process:**

**Key differences from manufacturing:**

| Aspect | Manufacturing | Foodservice |
|--------|--------------|-------------|
| Control | Closed system | Open, customer-facing |
| Ingredients | Bulk, verified | Multiple suppliers, frequent changes |
| Staff | Trained, supervised | High turnover |
| Menu | Fixed products | Dynamic, seasonal |
| Cross-contamination | Engineered controls | Procedural controls |

**Certification requirements:**

**1. Premises requirements:**
- Halal-only kitchen: Preferred
- Shared kitchen: Strict segregation required (separate cooking equipment, utensils, storage, preparation surfaces, documented cleaning)
- Storage: Physical separation of halal/non-halal

**2. Ingredient control:**

| Category | Requirement |
|----------|-------------|
| Meat | Halal-certified slaughter, certificate on file |
| Poultry | Halal-certified, verified supplier |
| Seafood | Generally permissible (no certification needed) |
| Processed ingredients | Halal certificate required |
| Cooking oils | Halal-certified if animal-based |
| Sauces/condiments | Verify halal status, certificates |

**3. Staff requirements:**
- Muslim supervisor on each shift (some schemes)
- All staff trained on halal handling
- Training records maintained
- Refresher training annually

**4. Menu management:**
- New items require Halal committee approval
- Ingredient verification and supplier certs before launch
- Only pre-approved substitutions allowed
- Specials require same verification as regular items

**5. Operational procedures:**

| Procedure | Key Points |
|-----------|------------|
| Receiving | Check halal certificates, reject non-compliant |
| Storage | Labeled, segregated, FIFO |
| Preparation | Dedicated or cleaned equipment |
| Cooking | No cross-contamination |
| Serving | Halal-only serving utensils |
| Cleaning | Documented protocols |

**6. Documentation:**
Required records:
- Supplier list with halal certificates
- Delivery receipts with halal verification
- Staff training records
- Daily halal checklist (signed)
- Cleaning logs
- Non-conformance records
- Customer complaint log

**Audit frequency:**
- Initial: Comprehensive facility audit
- Surveillance: Typically 2-4 times per year
- Unannounced: Possible at any time

**Special considerations:**

| Issue | Solution |
|-------|----------|
| Alcohol in cooking | Prohibited (wine, mirin, etc.) |
| Shared fryers | Dedicated for halal, or separate oil |
| Buffet cross-contact | Separate serving utensils, barriers |
| Catering off-site | Same standards apply |
| Food delivery | Segregated from non-halal |

**Cost factors:**
- Annual certification fee
- Ingredient premium (halal meat typically 10-20% higher)
- Staff training
- Possible kitchen modifications
- Audit fees""",
        "rejected": "Restaurant certification requires halal ingredients, trained staff, no cross-contamination, and regular audits. The kitchen should be dedicated or have strict segregation."
    },
    {
        "category": "certification",
        "prompt": "What is the process for halal certification of pharmaceutical products?",
        "chosen": """**Halal pharmaceutical certification framework:**

**Regulatory context:**
Pharmaceuticals occupy unique position—necessity (dharura) may permit otherwise prohibited ingredients if no halal alternative exists.

**Key standards:**

| Standard | Scope |
|----------|-------|
| MS 2424:2012 | Halal pharmaceuticals (Malaysia) |
| HAS 23002 | Drugs (MUI Indonesia) |
| GSO 2055-3 | Pharmaceuticals (Gulf) |
| OIC/SMIIC 6 | Pharmaceuticals (OIC) |

**Ingredient classification:**

Halal (clearly permissible):
- Plant-derived
- Synthetic chemicals
- Halal animal-derived (certified)

Haram (prohibited):
- Porcine-derived (gelatin, insulin historically)
- Alcohol (as active ingredient)
- Non-halal animal derivatives

Mashbooh (doubtful - investigate):
- Unclear animal source
- Fermentation products
- Processing aids

**Common pharmaceutical concerns:**

| Ingredient | Issue | Halal Alternative |
|------------|-------|-------------------|
| Gelatin capsules | Often porcine | Bovine (halal), HPMC (vegetable) |
| Magnesium stearate | Animal source | Vegetable grade |
| Glycerin | Animal fat | Vegetable glycerin |
| Stearic acid | Animal source | Plant-derived |
| Lactose | Animal rennet | Microbial/vegetable rennet |
| Alcohol (excipient) | Intoxicant | Non-alcoholic solvents |

**Certification process:**

**Phase 1: Product evaluation**
1. Active ingredient halal status
2. Excipient halal verification
3. Capsule shell material
4. Coating materials
5. Processing aids

**Phase 2: Manufacturing assessment**
- GMP compliance (prerequisite)
- Ingredient segregation
- Equipment dedication or cleaning validation
- Cross-contamination controls
- Traceability systems
- Documentation

**Phase 3: Shariah compliance review**
- Review by religious authority
- Necessity (dharura) evaluation if no alternative
- Conditions for permissibility

**Phase 4: Certification decision**

| Outcome | Condition |
|---------|-----------|
| Full halal certification | All ingredients halal, proper manufacturing |
| Conditional certification | Minor issues with corrective action plan |
| Dharura allowance | No halal alternative, life-saving necessity |
| Rejection | Non-halal ingredients with available alternatives |

**Dharura (necessity) principle:**
- Condition: Life-threatening or serious health risk
- Alternative: No halal alternative available
- Quantity: Minimum necessary amount
- Duration: Until halal alternative available
- Documentation: Shariah committee ruling

**Example:** Porcine insulin was permitted under dharura before recombinant human insulin became available.

**Labeling requirements:**
- Halal logo (if certified)
- Certification body name
- Certificate number
- "Halal" statement
- (If dharura): "For medical necessity"

**Market trends:**
- Growing demand for halal-certified OTC medicines
- Halal vitamins and supplements expanding
- Vaccine halal status increasingly scrutinized
- Biopharmaceuticals requiring new guidance""",
        "rejected": "Pharmaceutical halal certification checks ingredients like gelatin and excipients. The dharura principle may allow prohibited ingredients if medically necessary with no alternative."
    },
    {
        "category": "certification",
        "prompt": "How do I maintain halal certification during facility renovation or equipment changes?",
        "chosen": """**Halal certification maintenance during changes:**

**Notification requirements:**

| Change Type | Notification | Timeline |
|-------------|--------------|----------|
| New equipment (same process) | Inform certifier | Before use |
| New production line | Prior approval | 30+ days advance |
| Facility layout change | Prior approval | Before construction |
| New product | Application required | Per certifier process |
| Ingredient change | Prior approval | Before implementation |
| Supplier change | Prior approval | Before first order |

**Equipment change protocol:**

Step 1 - Assessment:
- Will equipment contact halal products?
- Was equipment previously used for non-halal?
- Is equipment shared with non-halal production?
- Does change affect production flow?

Step 2 - Notification:
- Documents: Equipment specification, previous use history, installation location, cleaning/commissioning plan
- Submit to certification body

Step 3 - Commissioning:
- New equipment: Standard cleaning sufficient
- Used equipment: Sertu or equivalent if pork/dog contact
- Shared equipment: Validated cleaning procedure

Step 4 - Verification:
- Internal audit before production
- Documentation maintained
- Certifier audit may be required

**Facility renovation scenarios:**

**Scenario 1: Layout change (no scope change)**
- T-30 days: Notify certifier with plans
- T-14 days: Certifier review/approval
- T-0: Construction begins
- Construction period: No production in affected area
- Completion: Internal verification
- Post-completion: Certifier audit (if required)
- Resume production: After clearance

**Scenario 2: Expansion (scope change)**
1. Submit expansion application
2. New layout, equipment list, process flow
3. Certifier evaluates halal compliance
4. Implement per approved plans
5. Internal audit of new areas
6. Certifier inspection
7. Certificate amendment

**Scenario 3: Temporary relocation during renovation**
- Notify certifier immediately
- Temporary facility must meet same standards
- May require interim audit
- Traceability must be maintained
- Certificate may need amendment

**Critical controls during changes:**

| Risk | Control |
|------|---------|
| Construction contamination | Physical barriers, HEPA, pressure differential |
| Contractor hygiene | Training, supervision, restricted access |
| Equipment commissioning | Cleaning validation before use |
| Documentation gaps | Maintain all records during transition |
| Product integrity | Hold and test first batches |

**Sertu requirement (JAKIM and similar):**

If equipment had contact with pork or dog:
1. Wash with water mixed with soil (clay) once
2. Rinse with clean water six times
3. Document each step
4. Halal committee verification
5. Records maintained""",
        "rejected": "Notify your certification body before making changes. Get approval for major changes, clean new equipment properly, and document everything."
    },

    # ============ SUPPLY CHAIN (12 items) ============
    {
        "category": "supply_chain",
        "prompt": "How do I implement halal traceability in my supply chain?",
        "chosen": """**Halal supply chain traceability implementation:**

**Traceability requirements:**
Full chain: Raw Material -> Supplier -> Transport -> Receiving -> Storage -> Production -> Packaging -> Warehouse -> Distribution -> Customer

**Key traceability elements:**

| Element | Data Captured |
|---------|---------------|
| Ingredient | Supplier, certificate, batch, expiry |
| Supplier | Halal cert number, validity, scope |
| Transport | Vehicle ID, previous cargo, cleaning |
| Receiving | Date, inspector, verification status |
| Storage | Location, segregation status |
| Production | Batch, line, operators, date/time |
| Packaging | Lot code, packaging materials |
| Distribution | Shipment ID, destination, carrier |

**Implementation framework:**

Key system functions:
1. Register ingredient with halal verification
2. Verify halal status against supplier certificates
3. Create production batch with ingredient traceability
4. Forward trace: ingredient to finished products
5. Backward trace: finished product to ingredients

**Technology options:**

| Technology | Pros | Cons |
|------------|------|------|
| Barcode/QR | Low cost, widely adopted | Manual scanning |
| RFID | Automated, batch tracking | Higher cost |
| Blockchain | Immutable, transparent | Complexity, cost |
| ERP integration | Centralized, efficient | Vendor dependency |
| Hybrid | Best of multiple | Integration complexity |

**Recall simulation (test traceability):**
- Trigger: Simulated halal non-conformance
- Time limit: 4 hours (typical target)
- Forward trace: Identify all affected products
- Backward trace: Identify ingredient source
- Documentation: Gather all relevant records
- Mock recall: Communication to customers
- Review: Identify gaps, improve system

**Supplier integration:**

| Level | Data Sharing |
|-------|--------------|
| Basic | Certificates only |
| Standard | Certificates + batch data |
| Advanced | Real-time inventory + batch |
| Integrated | Full visibility, shared systems |""",
        "rejected": "Track ingredients from supplier to finished product using batch numbers and lot codes. Keep records of halal certificates and verify at each step."
    },
    {
        "category": "supply_chain",
        "prompt": "How do I verify supplier halal compliance?",
        "chosen": """**Supplier halal verification program:**

**Tier-based approach:**

| Tier | Risk Level | Verification Depth |
|------|------------|-------------------|
| Tier 1 | High (animal-derived, critical) | Full audit + certificate |
| Tier 2 | Medium (processed, potential risk) | Certificate + questionnaire |
| Tier 3 | Low (natural, unprocessed) | Certificate or declaration |

**Verification process:**

**Step 1: Initial qualification**

Documentation required:
- Valid halal certificate
- Certificate scope (products covered)
- Certification body recognition status
- Product specifications
- MSDS/SDS if applicable
- Manufacturing location

Questionnaire topics:
- Is facility halal-dedicated?
- What is cross-contamination control?
- List all ingredients in product
- Are sub-suppliers halal certified?
- What is your traceability system?

**Step 2: Certificate verification**

| Check | Method |
|-------|--------|
| Authenticity | Contact certification body directly |
| Validity | Check expiry date |
| Scope | Confirm product listed |
| Recognition | Check if CB is recognized |
| QR/barcode | Scan if available |

**Certificate verification contacts:**
- JAKIM: halal.gov.my (online verification)
- MUI: halalmui.org (CEROL system)
- IFANCA: ifanca.org (contact directly)
- HFA: halalfoodauthority.com
- ESMA: esma.gov.ae

**Step 3: Risk assessment**
Risk scoring factors:
- Product type (animal-derived = high risk)
- Facility type (shared = higher risk)
- Certification status (expiring soon = higher)
- Geographic location (established halal market = lower)

**Step 4: On-site audit (Tier 1)**

Audit checklist:
- Halal certificate displayed
- Halal policy in place
- Staff trained on halal
- Ingredient verification records
- Sub-supplier certificates on file
- Production segregation (if applicable)
- Cleaning procedures
- Traceability demonstration
- Non-conformance handling
- Internal audit records

**Step 5: Ongoing monitoring**

| Activity | Frequency |
|----------|-----------|
| Certificate renewal verification | Before expiry |
| Periodic re-questionnaire | Annual |
| Supplier audit (Tier 1) | 1-3 years |
| Performance review | Quarterly |
| Incoming inspection | Each delivery |""",
        "rejected": "Check that suppliers have valid halal certificates from recognized bodies. Audit high-risk suppliers and maintain an approved supplier list."
    },
    {
        "category": "supply_chain",
        "prompt": "How do I prevent cross-contamination during transportation and logistics?",
        "chosen": """**Halal logistics and transportation controls:**

**Contamination risks:**

| Risk Point | Concern | Severity |
|------------|---------|----------|
| Previous cargo | Non-halal residue | High |
| Shared container | Cross-contact | High |
| Co-loading | Leakage, contact | Medium |
| Handling equipment | Forklifts, pallets | Medium |
| Storage facility | Shared warehousing | Medium |

**Transport control options:**

**Option 1: Dedicated halal transport**
- Vehicles only carry halal products
- Never used for haram
- Clear halal identification
- Highest assurance, highest cost

**Option 2: Cleaned shared transport**
Cleaning protocol:
1. Remove all previous cargo residue
2. Sweep/vacuum thoroughly
3. Wash with water and approved detergent
4. Rinse completely
5. Dry before loading
6. Document cleaning (signed checklist)
7. Verify before loading halal cargo

**Option 3: Containerized/packaged (physical barrier)**
- Product in sealed containers
- No direct contact with vehicle
- Outer packaging protection
- Lower risk of contamination

**Logistics protocol:**

Before loading:
- Previous cargo verification
- Cleanliness check (no visible residue, no odor)
- Cleaning record if shared vehicle
- Vehicle ID recorded
- Driver halal awareness attestation

Loading:
- Halal loaded separately if mixed cargo
- Pallet/barrier between halal and non-halal
- Physical separation maintained
- Clear halal identification on cargo

In transit:
- Maintain temperature per product requirements
- Sealed containers where possible
- Chain of custody records

Receiving:
- Check seal integrity, packaging condition
- Match to halal shipping documents
- Reject if contamination suspected

**Warehouse segregation:**
- Separate rooms/areas preferred
- Clear HALAL / NON-HALAL labels
- Halal above non-halal (prevent drip)
- Separate handling equipment or cleaning between uses
- Color-coded floor marking

**Third-party logistics (3PL) requirements:**

| Requirement | Contract Clause |
|-------------|-----------------|
| Halal policy | 3PL must have documented halal handling policy |
| Training | Staff trained on halal requirements |
| Segregation | Physical or procedural separation |
| Cleaning | Validated cleaning for shared assets |
| Documentation | Full traceability maintained |
| Audit rights | Customer may audit halal compliance |
| Liability | Indemnification for halal breaches |

**Halal logistics certification:**
Standards for halal logistics:
- MS 2400:2019 (Malaysia) - Halal Logistics
- IHIAS - Halal Warehouse & Transportation
- GSO 2055-4 - Halal Storage & Transportation""",
        "rejected": "Use dedicated halal transport or ensure shared vehicles are properly cleaned. Segregate halal products in warehouses and document the chain of custody."
    },
    {
        "category": "supply_chain",
        "prompt": "How do I handle supplier changes without losing halal certification?",
        "chosen": """**Supplier change management for halal compliance:**

**Critical principle:** New supplier/ingredient must be approved BEFORE use in production.

**Change classification:**

| Change Type | Risk | Approval Level |
|-------------|------|----------------|
| Same ingredient, new supplier | Medium | Halal Committee |
| New ingredient (same function) | High | Halal Committee + Certifier |
| Reformulation | High | Certifier required |
| Emergency substitution | Critical | Immediate halt + escalation |

**Standard process:**
Request -> Halal Assessment -> Qualification -> Approval -> Implement

**Step-by-step process:**

**Step 1: Change request**
- Current supplier
- New supplier
- Ingredient
- Reason (cost, supply security, quality)
- Urgency (normal, urgent, emergency)

**Step 2: Halal assessment**

| Check | Verification |
|-------|--------------|
| Halal certificate | Valid, recognized CB |
| Product scope | Ingredient in certificate scope |
| Specification match | Same function, composition |
| Manufacturing location | Certified site |
| Cross-contamination risk | Facility assessment |

**Step 3: Documentation requirements**
Required from new supplier:
- Halal certificate (valid)
- Product specification sheet
- MSDS/SDS
- Certificate of Analysis (CoA)
- Manufacturing process overview
- Sub-ingredient halal status (if applicable)
- Questionnaire (if Tier 1/2 supplier)

**Step 4: Halal Committee review**
- Meeting within 5 business days
- Attendees: Halal Executive, QA, Purchasing, Production
- Decision criteria: Certificate valid/recognized, product in scope, specification equivalent, no additional risk
- Outcomes: Approved, approved with conditions, rejected, more info needed

**Step 5: Certifier notification (if required)**

| Scenario | Notification |
|----------|--------------|
| Same ingredient, same spec | Inform at next audit |
| Different specification | Prior approval required |
| Different ingredient | Application amendment |
| Critical ingredient change | Immediate notification |

**Step 6: Implementation**
- Update Approved Supplier List
- Update ingredient database
- Update product specifications
- Notify production
- First batch verification
- Retain old supplier records
- Update traceability system

**Emergency substitution protocol:**
- HALT production of affected products immediately
- Notify Halal Executive immediately
- Notify certification body same day
- Do NOT use uncertified substitute
- Resolution: Find certified alternative, temporary halt, or withdraw from halal scope

**Risk mitigation:**
For critical suppliers, maintain:
- Dual sourcing with approved alternatives
- Safety stock of certified ingredients
- Pre-qualified backup suppliers""",
        "rejected": "Get halal certificates from the new supplier, have the Halal Committee approve the change, notify your certifier if required, then update your records."
    },
    {
        "category": "supply_chain",
        "prompt": "What is blockchain's role in halal supply chain traceability?",
        "chosen": """**Blockchain for halal supply chain:**

**Value proposition:**

| Traditional System | Blockchain System |
|-------------------|-------------------|
| Centralized records | Distributed ledger |
| Editable history | Immutable records |
| Trust in intermediaries | Trustless verification |
| Point-to-point visibility | End-to-end transparency |
| Paper certificates | Digital attestations |

**Halal-specific blockchain benefits:**

1. **Certificate authenticity**
   - Certification bodies issue on-chain certificates
   - Cannot be forged or altered
   - Real-time validity verification

2. **Ingredient traceability**
   - Every transfer recorded
   - Complete chain of custody
   - Instant backward trace

3. **Cross-contamination prevention**
   - Transport history on-chain
   - Previous cargo verification
   - Cleaning attestations recorded

4. **Multi-party trust**
   - Suppliers, certifiers, brands, consumers
   - Shared source of truth
   - Reduced verification overhead

**Architecture:**
Network participants: Certification Body, Supplier, Manufacturer, Logistics, Retailer, Consumer (App)
Smart contracts handle: Issue/verify certificates, record ingredient transfers, verify halal status, trigger alerts on expiry

**Key smart contract functions:**
- issueCertificate: CB issues halal certificate with company, products, validity, IPFS hash
- verifyCertificate: Check if certificate is valid and not expired
- revokeCertificate: CB can revoke certificate

**Real-world implementations:**

| Platform | Blockchain | Focus |
|----------|------------|-------|
| OneAgrix | Hyperledger | Halal food B2B |
| Halal Trail | Ethereum | Consumer traceability |
| AgrioChain | Private | Agricultural halal |
| UAE Halal Blockchain | Government | National initiative |

**Consumer verification flow:**
1. Consumer scans QR code on product
2. App queries blockchain
3. Returns: Product halal certificate (verified), certification body, manufacturing date/location, ingredient source traceability, transport/logistics chain

**Challenges:**

| Challenge | Mitigation |
|-----------|------------|
| Adoption (all parties must participate) | Start with willing partners |
| Data entry integrity ("garbage in") | IoT sensors, trusted nodes |
| Cost of implementation | Consortium cost-sharing |
| Technical complexity | SaaS blockchain platforms |
| Regulatory recognition | Work with halal authorities |

**ROI considerations:**
- Reduced certificate fraud
- Faster verification (hours to seconds)
- Premium pricing for verified products
- Reduced recall scope (precise traceability)
- Consumer trust and brand value""",
        "rejected": "Blockchain provides immutable records for halal certificates and supply chain transfers. It enables verification without trusting intermediaries."
    },
    {
        "category": "supply_chain",
        "prompt": "How do I handle halal compliance for imported ingredients?",
        "chosen": """**Import halal compliance framework:**

**Pre-import requirements:**
- Halal certificate from origin country
- Certificate recognized by destination authority
- Product within scope of certificate
- Manufacturer site matches certificate
- Export/import permits (if required)
- Product specifications
- Certificate of Analysis (CoA)

**Country-specific requirements:**

| Destination | Authority | Key Requirements |
|-------------|-----------|------------------|
| Malaysia | JAKIM | JAKIM-recognized foreign CB, label compliance |
| Indonesia | BPJPH/MUI | MUI-recognized CB, Halal label registration |
| UAE | ESMA | UAE-recognized CB or local re-certification |
| Saudi Arabia | SFDA | SFDA registration, halal certification |
| Singapore | MUIS | MUIS-recognized CB |

**Recognition verification:**
1. Check official recognition list for destination country
2. If recognized: Proceed with import
3. If not recognized: Obtain local certification or find recognized CB

**Import process workflow:**
1. Overseas supplier provides halal certificate
2. Verify recognition in destination country
3. Check product specs for compliance
4. Prepare shipping documentation
5. Customs clearance
6. Inspection at port
7. Release to importer

**Documentation requirements:**

| Document | Purpose |
|----------|---------|
| Halal certificate | Proof of halal status |
| Certificate of Origin | Source country verification |
| Bill of Lading | Shipment details |
| Packing list | Contents verification |
| Commercial invoice | Customs valuation |
| Health certificate | Food safety (some countries) |
| Import permit | Regulatory approval (some products) |
| Phytosanitary certificate | Plant products |

**Common import challenges:**

| Challenge | Solution |
|-----------|----------|
| Unrecognized foreign CB | Obtain local certification |
| Expired certificate | Request renewal before shipment |
| Certificate mismatch | Verify exact product/site on certificate |
| Transit through non-halal facility | Request transport documentation |
| Multiple transshipments | Full chain of custody records |

**Customs and port handling:**
- Documentation review: Verify halal certificate authenticity
- Physical inspection: Label check, packaging integrity
- Sampling: For laboratory testing (random or risk-based)
- Clearance: All documents verified, inspection passed
- Rejection: Return or destruction if non-compliant

**Labeling requirements for imports:**
Most countries require:
- Halal logo from recognized body
- Certification body name
- Certificate number
- Ingredients in local language
- Country of origin
- Manufacturer name and address

**Risk mitigation:**

| Risk | Control |
|------|---------|
| Fraudulent certificates | Direct verification with CB |
| Document tampering | Secure document exchange |
| Transit contamination | Halal logistics requirements |
| Regulatory changes | Monitor destination country updates |
| Supply chain complexity | Map and verify all intermediaries |""",
        "rejected": "Verify the foreign halal certificate is recognized in the destination country. Ensure all documentation is complete and labels meet local requirements."
    },
    {
        "category": "supply_chain",
        "prompt": "How do I manage sub-supplier halal compliance?",
        "chosen": """**Sub-supplier (tier 2+) halal management:**

**Supply chain tiers:**
- Tier 0: Your company (certified)
- Tier 1: Direct suppliers (managed)
- Tier 2: Sub-suppliers (indirect)
- Tier 3+: Raw material sources (deep supply chain)

**Challenge:** You don't directly purchase from sub-suppliers, but their halal status affects your products.

**Management framework:**

**1. Visibility requirements:**
Tier 1 suppliers must:
- Disclose all sub-suppliers for halal-critical ingredients
- Provide sub-supplier halal certificates
- Notify of any sub-supplier changes

Critical ingredients requiring visibility:
- Animal-derived materials
- Fermentation products
- Processing aids
- Flavors and colors

**2. Contractual requirements:**

| Clause | Requirement |
|--------|-------------|
| Sub-supplier disclosure | Must declare all halal-critical sub-suppliers |
| Certificate provision | Sub-supplier halal certs on file |
| Change notification | Prior approval for sub-supplier changes |
| Audit rights | Right to audit sub-suppliers (direct or via Tier 1) |
| Flow-down | Halal requirements flow to sub-suppliers |
| Liability | Responsibility for sub-supplier compliance |

**3. Risk-based approach:**
High risk (always require sub-supplier verification):
- Gelatin, glycerin, enzymes, emulsifiers
- Animal-derived products
- Multiple-tier supply chains
- High-risk geographic origins

**4. Verification methods:**

| Method | When to Use |
|--------|-------------|
| Tier 1 attestation | Low-risk ingredients |
| Sub-supplier certificate | Medium/high-risk ingredients |
| Questionnaire | Complex supply chains |
| Third-party audit | Critical ingredients |
| On-site audit | Very high-risk situations |

**5. Tier 1 supplier responsibilities:**
- Maintain sub-supplier halal qualifications
- Verify sub-supplier certificates annually
- Flow down halal requirements contractually
- Report sub-supplier non-conformances
- Facilitate audits upon request
- Maintain traceability to sub-suppliers

**6. Traceability chain:**
System should:
- Register supply chain for each product
- Store tier, supplier, material, halal cert for each link
- Verify all certificates in chain are valid
- Trace forward and backward through chain

**7. Monitoring:**

| Activity | Frequency |
|----------|-----------|
| Certificate validity check | Monthly |
| Tier 1 attestation renewal | Annual |
| Risk reassessment | Annual or on change |
| Sub-supplier audit | Risk-based, 1-3 years |
| Supply chain mapping update | Annual |

**Supplier questionnaire (sub-supplier section):**
- Do you use sub-suppliers for halal-critical ingredients?
- List: Sub-supplier name, material provided, halal certificate
- How do you verify sub-supplier halal compliance?
- Do you notify customers of sub-supplier changes?""",
        "rejected": "Require Tier 1 suppliers to disclose and verify sub-supplier halal status. Include contractual requirements and audit rights for the supply chain."
    },
    {
        "category": "supply_chain",
        "prompt": "How do I segregate halal and non-halal products in a shared facility?",
        "chosen": """**Halal/non-halal segregation in shared facilities:**

**Segregation principles:**

| Priority | Method |
|----------|--------|
| 1 (Best) | Physical separation (dedicated areas) |
| 2 | Temporal separation (different times) |
| 3 | Barrier separation (containers, packaging) |
| 4 | Procedural controls (SOPs, verification) |

**Physical segregation design:**
Ideal facility layout:
- Separate HALAL ZONE and NON-HALAL ZONE
- Each zone has: Raw Store, Production, FG Store
- Physical barrier or wall between zones
- Separate handling equipment or cleaning between uses

**Storage segregation:**
Physical requirements:
- Separate rooms/areas preferred
- Minimum: Separate shelving/racking with clear gap
- Halal above non-halal (prevent drip contamination)

Identification:
- Clear HALAL / NON-HALAL signage
- Color coding: Green for halal, Red for non-halal
- Painted floor boundaries
- Authorized personnel only (trained on segregation)

**Production line segregation:**

| Approach | Requirements | Audit Evidence |
|----------|--------------|----------------|
| Dedicated lines | Halal-only equipment | Equipment inventory |
| Campaign production | Halal first, then non-halal | Production schedule |
| Changeover cleaning | Validated cleaning between | Cleaning records |

**Cleaning validation (for shared equipment):**
1. Remove all visible residue
2. Disassemble as needed
3. Wash with approved detergent
4. Rinse thoroughly
5. Sanitize (if applicable)
6. Dry completely
7. Visual inspection
8. Swab test (if required)
9. Halal Committee sign-off
10. Document and retain record

**Testing for cross-contamination:**

| Test | Target | Limit |
|------|--------|-------|
| Visual | Visible residue | None |
| Protein (allergen kits) | Residual product | <10 ppm |
| DNA (PCR) | Pork/non-halal species | Not detected |
| Swab culture | Microbial | Per food safety limits |

**Equipment identification:**
Color coding system:
- GREEN: Halal-only equipment
- RED: Non-halal only
- YELLOW: Shared (requires cleaning validation)
- BLUE: Neutral (no food contact)

Labels include: Equipment ID, halal status, last used product, cleaning date, verified by

**Personnel controls:**

| Control | Implementation |
|---------|----------------|
| Training | All staff trained on segregation |
| Uniforms | Different colored coats for zones |
| Movement | Minimize cross-zone traffic |
| Visitors | Escort, explain requirements |
| Contractors | Brief on halal requirements |

**Utensil and tool management:**
- Dedicated halal utensils
- Color-coded or labeled
- Stored separately
- Cleaned after each use
- Regular inventory check
- Never used in non-halal zone

**Audit verification:**

| Check Point | What to Verify |
|-------------|----------------|
| Signage | Clear, visible, correct |
| Storage | Proper segregation maintained |
| Equipment | Color coding, labeling |
| Personnel | Aware of requirements |
| Records | Complete, current |
| Practices | Actual behavior matches SOPs |""",
        "rejected": "Physically separate halal and non-halal areas, use color-coded equipment, clean between changeovers, and train all staff on segregation requirements."
    },
    {
        "category": "supply_chain",
        "prompt": "What documentation do I need for halal supply chain compliance?",
        "chosen": """**Halal supply chain documentation requirements:**

**Documentation hierarchy:**
1. Policy & Manual: Halal Policy, HAS Manual
2. Procedures (SOPs): Ingredient control, supplier management, production, cleaning, traceability, non-conformance
3. Work Instructions: Receiving inspection, storage segregation, equipment cleaning, batch recording
4. Records: Certificates, inspection logs, batch records, audit reports

**Category 1: Supplier documentation**
Per supplier file:
- Supplier profile
- Halal certificate (current)
- Certificate verification record
- Product specifications
- Questionnaire (if applicable)
- Audit report (if applicable)
- Approved product list
- Correspondence

**Category 2: Ingredient documentation**

| Document | Purpose | Retention |
|----------|---------|-----------|
| Halal certificate | Proof of halal status | Life of relationship + 3 years |
| Specification sheet | Composition, origin | Current version |
| CoA (Certificate of Analysis) | Batch compliance | Per batch + 3 years |
| MSDS/SDS | Safety, composition | Current version |
| Approval record | Internal approval | Life of use |

**Category 3: Receiving documentation**
Record fields:
- Date, time, supplier, material, quantity
- Batch/lot number, halal cert reference, cert expiry
- Inspection: packaging condition, halal label present, documentation complete, segregation verified
- Decision: Accept/Reject/Hold
- Verified by (signature), date signed

**Category 4: Production documentation**
Batch record (halal critical points):
- Batch number, product name, date/time, line
- Ingredients used (with batch/lot numbers)
- Halal status verified checkbox
- Equipment used (cleaning verified)
- Operators, quality checks
- Packaging materials (lot)
- Authorized release signature

**Category 5: Cleaning/changeover records**

| Field | Information |
|-------|-------------|
| Date/time | When cleaning performed |
| Equipment ID | What was cleaned |
| Previous product | What was run before |
| Next product | What will be run |
| Cleaning method | SOP reference |
| Verification | Visual, swab test, etc. |
| Result | Pass/Fail |
| Performed/Verified by | Names and signatures |

**Category 6: Traceability documentation**
Traceability matrix per batch:
- Finished Product Batch
- For each ingredient: Supplier, Batch, Halal Cert #, Cert Expiry
- Distribution: Customer, Ship Date, Invoice, Quantity

**Category 7: Training documentation**

| Record | Content |
|--------|---------|
| Training matrix | Who needs what training |
| Training plan | Schedule for delivery |
| Attendance record | Who attended, date |
| Training materials | Slides, handouts |
| Assessment | Test results if applicable |
| Certificates | Completion certificates |

**Category 8: Audit documentation**
Internal audit: Schedule, checklists, reports, non-conformance records, corrective actions, follow-up
External audit: Certification reports, surveillance reports, CB correspondence, certificate

**Retention periods:**

| Document Type | Retention |
|---------------|-----------|
| Halal certificates | Until expired + 3 years |
| Batch records | Product shelf life + 3 years |
| Training records | Employment + 3 years |
| Audit records | Minimum 3 years |
| Non-conformances | Minimum 3 years |

**Document control:**
- Unique ID numbering
- Revision number and date
- Authorized signatory approval
- Controlled copy distribution
- Annual review minimum
- Secure archival, retrievable
- Authorized disposal after retention""",
        "rejected": "Keep supplier halal certificates, receiving inspection records, batch production records, cleaning logs, and traceability matrices. Retain for at least 3 years."
    },
    {
        "category": "supply_chain",
        "prompt": "How do I audit halal compliance at my suppliers' facilities?",
        "chosen": """**Supplier halal audit program:**

**When to audit suppliers:**

| Trigger | Priority |
|---------|----------|
| New critical supplier | Before first order |
| High-risk ingredients | Within first year |
| Non-conformance history | After each major issue |
| Routine surveillance | Based on risk tier |
| Certificate renewal | Before renewal |
| Customer requirement | As specified |

**Risk-based audit frequency:**

| Risk Tier | Audit Frequency | Scope |
|-----------|-----------------|-------|
| Tier 1 (High) | Annual | Full on-site |
| Tier 2 (Medium) | Every 2-3 years | On-site or remote |
| Tier 3 (Low) | Every 3-5 years | Document review |

**Pre-audit preparation:**

1. Gather information:
   - Supplier halal certificate
   - Previous audit reports
   - Product specifications
   - Process flow diagrams
   - Organizational chart
   
2. Define scope:
   - Products to audit
   - Processes to verify
   - Records to review
   - Personnel to interview

3. Develop audit plan:
   - Date and duration
   - Audit team
   - Schedule by area
   - Logistics

**Audit checklist categories:**

Halal management system:
- Halal policy documented
- Halal committee established
- Responsibilities defined
- Resources allocated

Ingredient control:
- Approved ingredient list
- Sub-supplier certificates
- Incoming inspection
- Change control

Production:
- Process flow review
- Cross-contamination controls
- Equipment dedication/cleaning
- Batch records

Documentation:
- SOPs current and followed
- Training records
- Traceability demonstration
- Internal audit records

**Audit report template:**

SUPPLIER HALAL AUDIT REPORT
Supplier: _____
Location: _____
Date: _____
Auditor(s): _____
Products Audited: _____

EXECUTIVE SUMMARY:
Overall Rating: Approved / Conditionally Approved / Not Approved
Critical findings: ___
Major findings: ___
Minor findings: ___

FINDINGS DETAIL:
(For each finding: Area, observation, classification, evidence, corrective action required)

RECOMMENDATION:
- Approve for continued supply
- Conditional approval pending corrective actions
- Re-audit required
- Do not approve

**Follow-up actions:**

| Finding Type | Response Timeline |
|--------------|------------------|
| Critical | Suspend supply, immediate corrective action |
| Major | 30-day corrective action, evidence required |
| Minor | 90-day corrective action |

**Remote audit considerations:**
When on-site not possible:
- Video conference facility tour
- Screen sharing for documents
- Photo/video evidence
- Third-party audit reports
- Self-assessment questionnaires""",
        "rejected": "Audit high-risk suppliers annually using a checklist covering ingredients, production, and documentation. Follow up on findings with corrective actions."
    },
    {
        "category": "supply_chain",
        "prompt": "What are the requirements for halal supply chain in e-commerce and direct-to-consumer?",
        "chosen": """**E-commerce halal supply chain requirements:**

**Unique e-commerce challenges:**

| Challenge | Halal Risk |
|-----------|------------|
| Multi-vendor platforms | Product authenticity |
| Third-party fulfillment | Cross-contamination |
| Last-mile delivery | Transport integrity |
| Returns handling | Contamination from returns |
| Cold chain | Temperature + halal |

**Platform requirements:**

For marketplace operators:
- Vendor halal certificate verification
- Product listing halal claims control
- Segregated fulfillment options
- Customer complaint handling
- Halal product search/filter

For halal-certified sellers:
- Certificate display on listing
- Halal logo usage compliance
- Product description accuracy
- Segregated inventory management

**Fulfillment center controls:**

Receiving:
- Verify halal status of incoming products
- Segregated receiving area (if shared)
- Documentation check

Storage:
- Dedicated halal storage zone
- Clear labeling and signage
- Segregation from non-halal
- Climate control if needed

Picking/Packing:
- Halal-dedicated equipment
- Segregated packing materials
- Staff training on handling
- No mixed orders (halal + non-halal in same package)

**Packaging requirements:**

| Element | Requirement |
|---------|-------------|
| Primary packaging | Intact, tamper-evident |
| Secondary packaging | Clean, uncontaminated |
| Packaging materials | Halal (no animal-derived adhesives) |
| Labeling | Halal certification visible |
| Inserts | No non-halal promotional materials |

**Last-mile delivery:**

| Scenario | Control |
|----------|---------|
| Dedicated halal delivery | Preferred for meat/perishables |
| Shared delivery | Sealed packaging, no direct contact |
| Temperature-sensitive | Halal-dedicated cold chain |
| Same-day delivery | Maintain segregation throughout |

**Returns handling:**
- Halal products returned should not re-enter halal inventory
- Inspect for contamination
- Document disposition (resell, donate, dispose)
- Separate processing from incoming halal goods

**Customer communication:**

Product page requirements:
- Halal certification body name
- Certificate number
- Scope of certification
- Ingredient list
- Country of origin

Delivery notification:
- Halal handling confirmation
- Delivery segregation status
- Contact for concerns

**Third-party logistics (3PL) for e-commerce:**

| Requirement | Verification |
|-------------|--------------|
| Halal handling policy | Document review |
| Staff training | Training records |
| Storage segregation | Facility audit |
| Vehicle cleaning | Cleaning logs |
| Traceability | System demonstration |

**Technology enablers:**
- Blockchain for traceability
- QR codes for authentication
- GPS tracking for transport
- Temperature monitoring IoT
- Digital halal certificates""",
        "rejected": "E-commerce requires halal certificate verification on listings, segregated fulfillment, proper packaging, and controlled last-mile delivery."
    },
    {
        "category": "supply_chain",
        "prompt": "How do I handle halal compliance during supply chain disruptions or emergencies?",
        "chosen": """**Halal supply chain emergency management:**

**Types of disruptions:**

| Disruption | Halal Impact |
|------------|--------------|
| Supplier shutdown | Loss of certified ingredient |
| Transport disruption | Delivery delays, alternate routes |
| Facility damage | Production interruption |
| Certificate expiry | Compliance gap |
| Pandemic/outbreak | Supply chain breakdown |
| Natural disaster | Multiple supply chain failures |

**Emergency response framework:**

LEVEL 1 - Minor (single supplier issue):
- Activate backup supplier
- Use safety stock
- Expedite certification if needed
- Notify Halal Committee

LEVEL 2 - Moderate (multiple suppliers or critical ingredient):
- Convene emergency Halal Committee
- Assess all alternatives
- Contact certification body
- Consider temporary product withdrawal

LEVEL 3 - Severe (supply chain breakdown):
- Executive escalation
- Multi-stakeholder coordination
- Regulatory notification if needed
- Public communication plan

**Backup supplier strategy:**

For critical halal ingredients:
- Pre-qualify minimum 2 suppliers
- Maintain approved supplier status
- Hold backup certificates on file
- Periodic small orders to maintain relationship
- Include in business continuity plan

Qualification requirements:
- Valid halal certificate
- Recognized certification body
- Equivalent specification
- Capacity to supply

**Emergency ingredient substitution:**

PROHIBITED:
- Never substitute non-halal ingredient
- Never use expired certificate supplier
- Never assume halal without verification

PERMITTED (with controls):
- Use pre-approved alternate supplier
- Use pre-approved alternate ingredient
- Same halal status verified

**Decision tree:**
1. Can we use existing safety stock? -> Yes: Use it
2. Is backup supplier available and certified? -> Yes: Activate
3. Can alternative ingredient be used? -> Yes: Verify halal, get committee approval
4. Can we obtain emergency certification? -> Contact CB immediately
5. None of above possible -> Halt production, withdraw from halal

**Communication protocol:**

Internal:
- Halal Committee: Immediate notification
- Production: Stop if risk identified
- Sales: Customer impact assessment
- Management: Escalation per level

External:
- Certification body: Same day for material issues
- Customers: If product affected
- Suppliers: Expedite alternatives

**Documentation during emergency:**

Maintain records of:
- Decision rationale
- Alternatives considered
- Halal verification of solution
- Committee approvals
- Certifier communications
- Timeline of events

**Post-emergency review:**

1. Root cause analysis
2. Response effectiveness assessment
3. Prevention measures identification
4. Update business continuity plan
5. Improve backup supplier coverage
6. Report to management

**Business continuity planning:**

| Element | Requirement |
|---------|-------------|
| Risk assessment | Identify halal-critical points |
| Backup suppliers | Pre-qualified alternatives |
| Safety stock | Buffer for critical ingredients |
| Communication plan | Internal and external |
| Decision authority | Clear escalation path |
| Training | Regular drill exercises |""",
        "rejected": "Have backup suppliers pre-qualified, maintain safety stock of critical ingredients, and never substitute non-halal ingredients. Contact your certification body immediately for guidance."
    },

    # ============ INGREDIENTS (13 items) ============
    {
        "category": "ingredients",
        "prompt": "What are the main categories of halal and haram ingredients?",
        "chosen": """**Ingredient classification in Islamic dietary law:**

**Category 1: HALAL - Permissible**

| Type | Examples | Notes |
|------|----------|-------|
| Plants | All fruits, vegetables, grains, legumes | Inherently halal |
| Seafood | Fish, shrimp, most sea creatures | No slaughter required (most schools) |
| Halal-slaughtered meat | Cattle, sheep, goat, poultry, camel | Must meet slaughter requirements |
| Eggs | From halal birds | Inherently halal |
| Dairy | Milk, cheese, yogurt | If no haram additives |
| Honey | All honey | Inherently halal |
| Water | All water | Inherently halal |

**Category 2: HARAM - Prohibited**

| Type | Examples | Basis |
|------|----------|-------|
| Pork and derivatives | Pork, lard, gelatin, pepsin | Explicitly prohibited (Quran 2:173) |
| Carrion | Dead animals (not slaughtered) | Explicitly prohibited |
| Blood | Blood, blood products | Explicitly prohibited |
| Carnivorous animals | Lions, tigers, wolves | Fangs for hunting |
| Birds of prey | Eagles, hawks, vultures | Talons for hunting |
| Harmful creatures | Snakes, scorpions | Harmful |
| Intoxicants | Alcohol, drugs | Explicitly prohibited |
| Improperly slaughtered | Stunned to death, strangled | Slaughter violation |

**Category 3: MASHBOOH - Doubtful/Questionable**
Ingredients requiring investigation:
- Gelatin (unknown source)
- Glycerin (animal vs. plant)
- Enzymes (animal vs. microbial)
- Mono/diglycerides
- L-cysteine (hair vs. synthetic)
- Some E-numbers
- Flavors (may contain alcohol)
- Stearic acid/stearates
- Whey (rennet source)

**Category 4: Processed/Derived ingredients**

| Ingredient | Concern | Halal Status |
|------------|---------|--------------|
| Gelatin | Usually pork or non-halal beef | Check source |
| Glycerin | Animal fat or vegetable | Verify source |
| Lecithin | Soy (halal) or egg (halal) | Usually halal |
| Enzymes | Animal, microbial, or plant | Verify source |
| Mono/diglycerides | Animal fat or vegetable | Verify source |
| Stearic acid | Animal or plant | Verify source |
| L-cysteine | Human hair, duck feathers, synthetic | Avoid animal |
| Vanilla extract | Contains alcohol | Check final concentration |
| Wine vinegar | Fully converted? | Scholarly debate |

**Slaughter requirements (for halal meat):**
- Slaughterman: Muslim, sane, adult
- Invocation: "Bismillah, Allahu Akbar"
- Method: Sharp knife, swift cut
- Cut: Throat, windpipe, blood vessels
- Bleeding: Complete drainage
- Animal: Alive at time of slaughter
- Direction: Facing Qiblah (recommended)
- Stunning: Prohibited or restricted (varies)

**Decision tree:**
Is ingredient from animal source?
- No: Generally HALAL (check processing)
- Yes: Is animal halal species?
  - No: HARAM
  - Yes: Was it properly slaughtered?
    - No/Unknown: HARAM or MASHBOOH
    - Yes (certified): HALAL""",
        "rejected": "Halal includes plants, seafood, and properly slaughtered animals. Haram includes pork, blood, and improperly slaughtered meat. Mashbooh ingredients need investigation."
    },
    {
        "category": "ingredients",
        "prompt": "How do I evaluate E-numbers for halal compliance?",
        "chosen": """**E-number halal evaluation guide:**

**E-number categories:**

| Range | Category | Halal Risk |
|-------|----------|------------|
| E100-199 | Colors | Medium (some animal) |
| E200-299 | Preservatives | Low |
| E300-399 | Antioxidants | Low-Medium |
| E400-499 | Emulsifiers, stabilizers | High |
| E500-599 | Acids, anti-caking | Low |
| E600-699 | Flavor enhancers | Low-Medium |
| E900-999 | Glazing, sweeteners | Medium |
| E1000-1599 | Additional additives | Variable |

**HIGH RISK E-numbers (require verification):**
Always verify source:
- E120 (Carmine/Cochineal) - INSECT derived
- E441 (Gelatin) - Usually pork/non-halal beef
- E542 (Bone phosphate) - Animal bones
- E631 (Sodium inosinate) - May be animal
- E635 (Sodium ribonucleotides) - May be animal
- E901 (Beeswax) - Insect (halal in most opinions)
- E904 (Shellac) - Insect secretion
- E920 (L-cysteine) - May be animal/human hair
- E1518 (Glyceryl triacetate) - May be animal fat

**Emulsifiers (E400-499) - Special attention:**

| E-Number | Name | Concern | Halal If |
|----------|------|---------|----------|
| E470a | Sodium/potassium stearate | Animal fat | Vegetable source |
| E470b | Magnesium stearate | Animal fat | Vegetable source |
| E471 | Mono/diglycerides | Animal fat | Vegetable source |
| E472a-f | Esters of mono/diglycerides | Animal fat | Vegetable source |
| E473 | Sucrose esters | May be animal | Vegetable source |
| E475 | Polyglycerol esters | Animal fat | Vegetable source |
| E476 | PGPR | Usually vegetable | Verify |
| E481-2 | Sodium/calcium stearoyl lactylate | Animal fat | Vegetable source |
| E491-5 | Sorbitan mono/tri-stearate | Animal fat | Vegetable source |

**Evaluation process:**
1. Identify E-number category
2. Check if in high-risk list
3. For high risk: Request source documentation
4. For E120 (carmine): HARAM - insect-derived
5. For E441 (gelatin): Check source (fish halal, certified beef halal, pork haram)
6. For emulsifiers: Verify vegetable source or halal certificate

**Generally HALAL E-numbers:**
Low risk (usually halal):
- E100-109: Curcumin, riboflavin (plant/synthetic)
- E140-141: Chlorophylls (plant)
- E150a-d: Caramel colors (sugar-based)
- E160a: Carotenes (plant)
- E162: Beetroot red
- E200-203: Sorbic acid (synthetic)
- E260-263: Acetic acid (vinegar-based)
- E270: Lactic acid (usually fermentation)
- E300-304: Ascorbic acid (vitamin C)
- E306-309: Tocopherols (vitamin E)
- E322: Lecithin (usually soy)
- E330-333: Citric acid
- E400-407: Alginate, agar, carrageenan (seaweed)
- E410-412: Gums (plant)
- E414: Gum arabic
- E420-421: Sorbitol, mannitol

**Documentation requirement:**
For any E-number in medium/high risk:
- Supplier declaration of source
- Halal certificate (if animal-derived)
- Technical specification""",
        "rejected": "E-numbers E400-499 (emulsifiers) and E120 (carmine), E441 (gelatin) need source verification. Most E200-299 preservatives and E300s are generally halal."
    },
    {
        "category": "ingredients",
        "prompt": "What are halal alternatives to gelatin?",
        "chosen": """**Halal gelatin alternatives:**

**Option 1: Halal-certified gelatin**

| Source | Availability | Functionality | Notes |
|--------|--------------|---------------|-------|
| Halal beef gelatin | Common | Same as pork | Must be from halal slaughter |
| Fish gelatin | Common | Lower gel strength | Kosher-fish also halal |
| Poultry gelatin | Limited | Good for confectionery | Halal slaughter required |

**Option 2: Plant-based alternatives**

| Alternative | Source | Applications | Gel Strength |
|-------------|--------|--------------|--------------|
| Agar-agar | Seaweed | Desserts, jellies | High, brittle |
| Carrageenan | Red seaweed | Dairy, meat | Medium, elastic |
| Pectin | Citrus/apple | Jams, jellies | Medium |
| Konjac | Konjac plant | Noodles, jellies | High |
| Gellan gum | Bacterial fermentation | Beverages, desserts | Variable |

**Option 3: Modified starch and others**

| Alternative | Application | Characteristics |
|-------------|-------------|-----------------|
| Modified starch | Sauces, fillings | Thickening, not gelling |
| Xanthan gum | General | Thickening, stabilizing |
| Locust bean gum | Dairy, bakery | Synergy with carrageenan |
| HPMC | Capsules, coatings | Film-forming |

**Application-specific recommendations:**

Capsules: Primary HPMC (vegetable capsules), Alternative Pullulan
Gummy candy: Primary halal beef gelatin, Alternative pectin + starch blend (texture differs)
Marshmallows: Primary halal beef/fish gelatin, Alternative carrageenan + tapioca starch
Yogurt: Primary pectin, Alternative starch or carrageenan
Desserts/jellies: Primary agar-agar, Alternative carrageenan or gellan
Pharmaceutical: Primary HPMC capsules, Alternative halal bovine gelatin

**Technical comparison:**

| Property | Pork Gelatin | Halal Beef | Fish Gelatin | Agar | Pectin |
|----------|--------------|------------|--------------|------|--------|
| Bloom strength | 100-300 | 100-300 | 50-200 | N/A | N/A |
| Gel temp (C) | 25-35 | 25-35 | 8-25 | 32-40 | 85-95 |
| Melt temp (C) | ~35 | ~35 | 25-30 | 85+ | 85+ |
| Clarity | High | High | High | Medium | Low |
| Mouthfeel | Melt-in-mouth | Melt-in-mouth | Melt-in-mouth | Firm, brittle | Soft |
| Cost | Low | Medium | Medium-High | Medium | Low |
| Halal | No | Yes (certified) | Yes | Yes | Yes |

**Formulation tips:**

Agar-agar:
- Use 1/3 to 1/2 amount of gelatin
- Dissolve in hot water (>85C)
- Sets at room temperature
- Does not melt in mouth (different texture)

Carrageenan (iota):
- Good for dairy applications
- Works synergistically with locust bean gum
- Freeze-thaw stable
- Softer gel than kappa-carrageenan

Pectin (HM):
- Requires sugar and acid to gel
- Good for fruit applications
- Heat stable
- pH dependent (3.0-3.5 optimal)

**Suppliers of halal gelatin:**
Major manufacturers offering halal-certified gelatin:
- Rousselot (halal beef)
- Gelita (halal beef)
- Nitta Gelatin (halal beef, fish)
- Weishardt (halal)
- Various fish gelatin specialists""",
        "rejected": "Use halal-certified beef or fish gelatin, or plant alternatives like agar-agar, carrageenan, or pectin depending on the application."
    },
    {
        "category": "ingredients",
        "prompt": "How do I handle alcohol-containing ingredients?",
        "chosen": """**Alcohol in food and ingredients - halal considerations:**

**Scholarly positions:**

| Position | Ruling | Bodies/Scholars |
|----------|--------|-----------------|
| Zero tolerance | Any alcohol prohibited | JAKIM (strict), some scholars |
| Functional permitted | Non-intoxicating amounts OK | Some Middle Eastern scholars |
| Source-based | Khamr-derived prohibited, synthetic OK | MUI (with conditions) |
| Transformation | If chemically transformed, permitted | Classical fiqh principle |

**Types of alcohol in food:**

Khamr (wine, beer, liquor): Status HARAM (unanimous)
Ethanol from grape/date fermentation: Status HARAM (majority view)
Industrial/synthetic ethanol: Status Debated (check certification body)
Naturally occurring (fermentation): Permitted if <0.5% and not intoxicating
Alcohol as processing aid (evaporates): Debated (residue concern)

**Practical guidelines by certifier:**

| Certifier | Position |
|-----------|----------|
| JAKIM | Zero tolerance in final product |
| MUI | Khamr prohibited; industrial alcohol case-by-case |
| ESMA | Very low tolerance, context-dependent |
| IFANCA | Generally prohibits, some exceptions |

**Common alcohol-containing ingredients:**

| Ingredient | Alcohol Type | Typical Level | Action |
|------------|--------------|---------------|--------|
| Vanilla extract | Ethanol solvent | 35-40% | Use vanilla powder or halal vanilla |
| Wine vinegar | Fermented wine | <0.5% | Scholarly debate; avoid for strict markets |
| Mirin | Rice wine | 14%+ | HARAM; use halal mirin substitute |
| Cooking wine | Wine | 10-20% | HARAM |
| Flavor extracts | Ethanol carrier | 1-40% | Check residue in final product |
| Soy sauce | Fermentation | 1-2% | Some halal versions available |
| Kombucha | Fermentation | 0.5-3% | Debated; avoid for strict markets |

**Evaluation framework:**
1. Check alcohol source (khamr-derived = HARAM)
2. Check final product concentration (>0.5% = problematic)
3. If trace level: Check with target market certifier
4. If processing aid that evaporates: Verify with certifier, may require testing

**Halal alternatives:**

| Haram Ingredient | Halal Alternative |
|------------------|-------------------|
| Vanilla extract | Vanilla powder, halal vanilla extract |
| Cooking wine | Grape juice + vinegar, halal wine substitute |
| Mirin | Halal mirin (no alcohol), sugar + rice vinegar |
| Rum flavoring | Halal rum flavor (synthetic) |
| Liqueur | Halal flavor concentrates |
| Wine vinegar | Apple cider vinegar, halal wine vinegar |

**Testing for alcohol:**

| Method | Use | Detection Limit |
|--------|-----|-----------------|
| GC-FID | Quantitative | <0.01% |
| Enzymatic kits | Screening | ~0.01% |
| Refractometer | Rough estimate | Not precise |

**Documentation needed:**
For any ingredient with potential alcohol:
1. Specification showing alcohol type and level
2. Statement of alcohol source
3. Calculation of residue in final product
4. Halal certificate if claiming halal compliance""",
        "rejected": "JAKIM requires zero alcohol. MUI distinguishes between khamr (prohibited) and synthetic. Use halal alternatives like vanilla powder instead of extract."
    },
    {
        "category": "ingredients",
        "prompt": "How do I evaluate enzymes for halal status?",
        "chosen": """**Enzyme halal evaluation:**

**Enzyme sources:**

| Source | Halal Status | Notes |
|--------|--------------|-------|
| Microbial | Generally HALAL | Fermentation-derived |
| Plant | HALAL | Papain (papaya), bromelain (pineapple) |
| Halal animal | HALAL if certified | Pepsin, rennet from halal slaughter |
| Porcine | HARAM | Pig-derived pepsin, pancreatin |
| Non-halal bovine | HARAM | From non-halal slaughter |

**Common enzymes and concerns:**

HIGH RISK (verify source):
- Rennet (cheese) - often calf, may be microbial
- Pepsin - often porcine
- Pancreatin - often porcine
- Lipase - animal or microbial
- Trypsin - often porcine pancreas
- Chymotrypsin - animal pancreas

MEDIUM RISK (check production):
- Amylase - usually microbial, but check
- Protease - often microbial, verify
- Lactase - usually microbial
- Glucose isomerase - microbial

LOW RISK (generally halal):
- Papain - papaya (plant)
- Bromelain - pineapple (plant)
- Ficin - fig (plant)
- Most bacterial/fungal enzymes

**Cheese rennet evaluation:**

| Type | Source | Halal Status |
|------|--------|--------------|
| Animal rennet | Calf stomach | HALAL only if halal slaughter |
| Microbial rennet | Fungi (R. miehei) | HALAL |
| FPC (fermentation-produced chymosin) | GMO microbes | HALAL (most opinions) |
| Vegetable rennet | Thistle, fig | HALAL |

**Evaluation process:**
1. Identify enzyme source
2. If porcine: HARAM - replace with microbial or plant alternative
3. If animal (non-porcine): Check for halal certificate
4. If microbial/plant: Check for animal-derived growth media

**Growth media consideration:**
Even microbial enzymes may be questionable if:
- Grown on animal-derived media (peptone, blood)
- Processing uses animal-derived materials

**Documentation required:**
- Enzyme type and function
- Source organism or animal
- If animal: Halal slaughter certificate
- If microbial: Growth media composition
- Manufacturing process overview
- Halal certificate from enzyme manufacturer
- Technical specification

**Halal enzyme suppliers:**
Major suppliers offering halal-certified enzymes:
- Novozymes (various)
- DSM (various)
- DuPont (Danisco)
- AB Enzymes
- Amano (Japanese, various halal options)

**Transformation debate:**
Some scholars argue that complete chemical transformation (istihalah) makes even porcine-origin enzymes halal because the original substance no longer exists. However, most certification bodies do NOT accept this for porcine-derived enzymes and require halal-source alternatives.""",
        "rejected": "Microbial and plant enzymes are generally halal. Animal enzymes need halal slaughter certification. Porcine enzymes are haram - use alternatives."
    },
    {
        "category": "ingredients",
        "prompt": "What flavoring ingredients require halal verification?",
        "chosen": """**Flavoring halal evaluation:**

**Risk areas in flavorings:**

| Component | Concern | Verification Needed |
|-----------|---------|---------------------|
| Carrier/solvent | Alcohol (ethanol) | Type and level |
| Natural flavors | Animal-derived components | Source |
| Processing aids | Enzymes, glycerin | Source |
| Reaction flavors | Amino acids | Source |
| Masking agents | Various | Composition |

**Alcohol in flavorings:**
Extraction solvent: Ethanol - check source and residue; propylene glycol - generally halal; glycerin - check source
Carrier in final flavor: Ethanol content declaration required
- Some certifiers: <0.5% in finished food OK
- JAKIM: Zero tolerance

Calculation: Flavor alcohol % x usage rate % = contribution to final product

**Natural flavors - animal concerns:**

| Flavor Type | Potential Animal Source | Verify |
|-------------|------------------------|--------|
| Meat flavors | Actual meat, fat | Must be halal meat |
| Butter flavor | Butter, milk fat | Usually halal (dairy) |
| Cheese flavor | Cheese, rennet | Check rennet source |
| Savory/umami | Animal extracts, HVP | Check protein source |
| Castoreum | Beaver glands | HARAM (animal secretion) |
| Civet | Civet cat | HARAM (not halal animal) |
| Ambergris | Whale | Debated, some permit |

**Flavor categories and risk:**

FRUIT FLAVORS - Low risk
- Usually plant-derived, check alcohol

VANILLA - Medium risk
- Natural extract: alcohol-based
- Artificial: usually halal
- Request halal alternative

MEAT/SAVORY - High risk
- May contain animal fat, extracts
- HVP source (animal vs. plant)
- Require halal certificate

DAIRY FLAVORS - Medium risk
- Butter, cream: usually OK
- Cheese: check enzyme/rennet
- Verify composition

SPECIALTY - Case by case
- Reaction flavors
- Smoke flavors
- Fermented flavors

**Verification requirements:**
Flavor supplier questionnaire:
1. Does flavor contain ethanol? (source, percentage, final level)
2. Does flavor contain animal-derived components? (which, source, halal cert)
3. What carriers/solvents are used? (list with sources)
4. Are processing aids used? (enzymes, other)
5. Is flavor halal certified? (provide certificate)

**Documentation required:**

| Document | Purpose |
|----------|---------|
| Flavor specification | Composition overview |
| Ingredient breakdown | All components listed |
| Alcohol declaration | Type, source, percentage |
| Animal-derived statement | Yes/no, details if yes |
| Halal certificate | If claiming halal |
| Allergen statement | Cross-reference |

**Halal flavor suppliers:**
Major flavor houses with halal offerings:
- Givaudan (halal range)
- IFF (halal certified)
- Firmenich (halal options)
- Symrise (halal certified)
- Sensient (halal line)
- Regional suppliers in Muslim countries

**Best practice:**
Request halal certification or detailed breakdown for ALL flavors. "Natural flavor" on label doesn't indicate halal status.""",
        "rejected": "Check flavorings for alcohol content, animal-derived components, and carrier ingredients. Request halal certificates or detailed composition breakdowns."
    },
    {
        "category": "ingredients",
        "prompt": "How do I verify the halal status of processing aids?",
        "chosen": """**Processing aid halal verification:**

**What are processing aids?**
Materials used during manufacturing that:
- Are not intended to remain in final product
- May leave incidental traces
- Often not required on ingredient labels

**Common processing aids and concerns:**

| Processing Aid | Function | Halal Concern |
|----------------|----------|---------------|
| Enzymes | Catalysis | Animal vs. microbial source |
| Fining agents | Clarification | Animal-derived (gelatin, isinglass) |
| Antifoaming agents | Reduce foam | May be animal fat-based |
| Lubricants | Equipment | May be animal fat-based |
| Filtration media | Clarify/filter | May be animal-derived |
| Release agents | Prevent sticking | May be animal fat-based |
| Bleaching agents | Whitening | Usually chemical (halal) |

**Verification process:**
1. Identify: List all processing aids used
2. Classify: enzyme, fining, lubricant, filter, release, other
3. Verify: Supplier declaration, halal certificate if animal-derived
4. Residue: Does any remain in final product? Testing may be required

**Category-specific guidance:**

**1. Fining agents (beverages, vinegar, oil):**

| Agent | Source | Halal Status |
|-------|--------|--------------|
| Gelatin | Animal | HARAM unless halal certified |
| Isinglass | Fish swim bladder | HALAL (fish) |
| Casein | Milk protein | HALAL (dairy) |
| Egg albumin | Egg | HALAL |
| Bentonite | Clay | HALAL |
| Activated carbon | Vegetable/mineral | HALAL |
| PVPP | Synthetic | HALAL |

**2. Release agents/lubricants:**

| Agent | Source | Halal Status |
|-------|--------|--------------|
| Vegetable oils | Plant | HALAL |
| Mineral oil | Petroleum | HALAL |
| Lecithin | Soy/egg | HALAL |
| Stearates | May be animal | Verify source |
| Silicone | Synthetic | HALAL |

**3. Antifoaming agents:**

| Agent | Source | Halal Status |
|-------|--------|--------------|
| Silicone-based | Synthetic | HALAL |
| Vegetable oil-based | Plant | HALAL |
| Animal fat-based | Animal | Verify source |

**Documentation requirements:**
For each processing aid:
- Product name and supplier
- Technical specification
- Source declaration (plant/mineral/synthetic/animal)
- If animal: Halal certificate required
- Function in process
- Residue information (completely removed? traces remain?)
- Halal certificate (if applicable)

**Declaration template (request from suppliers):**
PROCESSING AID HALAL DECLARATION
- Product, Function
- Source: Plant/Mineral/Synthetic/Microbial/Animal (specify species)
- If animal: Halal slaughter certificate attached
- Residue in final product: None/Trace levels/Measurable levels
- Certification by supplier with signature and date

**Residue considerations:**

| Scenario | Halal Impact |
|----------|--------------|
| No residue (completely removed) | Some scholars: transformation complete, halal |
| Trace residue (ppm level) | Most scholars: source still matters |
| Measurable residue | Definitely matters; must be halal source |

**Note:** Most certification bodies require halal-source processing aids regardless of residue level. The "no residue = halal" argument is generally not accepted for porcine-derived processing aids.""",
        "rejected": "Identify all processing aids, check their sources, and verify animal-derived ones have halal certificates. Document even if not on final product label."
    },
    {
        "category": "ingredients",
        "prompt": "What dairy ingredients require halal verification?",
        "chosen": """**Dairy ingredient halal evaluation:**

**Base dairy products:**

| Product | Base Status | Verification Need |
|---------|-------------|-------------------|
| Milk | HALAL | Additives only |
| Cream | HALAL | Additives only |
| Butter | HALAL | Check for additives |
| Yogurt | Usually HALAL | Check gelatin, cultures |
| Cheese | MASHBOOH | Rennet and additives |
| Whey | MASHBOOH | Depends on cheese source |
| Lactose | Usually HALAL | Processing check |

**Key concerns in dairy:**

RENNET (cheese, whey):
- Animal rennet: Must be from halal slaughter
- Microbial rennet: HALAL
- FPC (GMO chymosin): Generally HALAL
- Vegetable rennet: HALAL

CULTURES:
- Bacterial cultures: HALAL
- Media: Check for animal-derived nutrients
- Growth factors: Verify source

ADDITIVES:
- Gelatin (yogurt, desserts): Check source
- Emulsifiers (ice cream): E471, etc.
- Stabilizers: Usually HALAL
- Flavors: See flavor guidelines

PROCESSING AIDS:
- Clarification agents
- Antifoaming agents
- Bleaching agents

**Cheese halal evaluation:**
1. Check rennet type (microbial/vegetable/FPC = halal; animal = needs certificate)
2. If animal rennet without halal certificate: HARAM
3. Check additional additives
4. Both rennet and additives must be halal

**Whey products:**

| Product | Concern | Verification |
|---------|---------|--------------|
| Sweet whey | From cheese; rennet matters | Check cheese source |
| Acid whey | From acid casein; no rennet | Usually HALAL |
| Whey protein concentrate | From cheese whey | Check cheese source |
| Whey protein isolate | From cheese whey | Check cheese source |
| Lactose | Extracted from whey | Check whey source |

**Ingredient-specific guidance:**

Casein and caseinates:
- From milk protein
- Generally HALAL
- Check for processing aids

Lactose:
- From whey
- If acid whey source: HALAL
- If cheese whey: depends on cheese rennet

Milk powder:
- Generally HALAL
- Check for additives (emulsifiers, vitamins)

Ice cream:
Multiple concerns:
- Emulsifiers (E471, E472)
- Stabilizers (gelatin?)
- Flavors (alcohol, animal)
- Colors

Yogurt:
- Culture: Usually OK
- Gelatin: Common additive - check
- Flavors: May contain alcohol
- Fruit preparations: Check for gelatin

**Documentation required:**
- Product specification
- Ingredient declaration (full)
- For cheese/whey: Rennet type and source, halal certificate if animal
- For cultured products: Culture source, media composition
- Additive breakdown: Emulsifiers with source, stabilizers, flavors
- Halal certificate (if available)

**Common halal dairy certifications:**
- Many dairy companies offer halal-certified lines
- "Suitable for vegetarians" often means microbial rennet
- "Halal" or "M" symbol indicates certification""",
        "rejected": "Check cheese and whey for rennet source. Verify yogurt doesn't contain pork gelatin. Emulsifiers in ice cream need source verification."
    },
    {
        "category": "ingredients",
        "prompt": "How do I evaluate confectionery ingredients for halal status?",
        "chosen": """**Confectionery halal evaluation:**

**High-risk confectionery ingredients:**

| Ingredient | Function | Halal Concern | Alternative |
|------------|----------|---------------|-------------|
| Gelatin | Gelling, texture | Pork source | Halal beef, fish, pectin |
| Carmine (E120) | Red color | Insect | Synthetic red, beetroot |
| Glycerin | Humectant | Animal fat | Vegetable glycerin |
| Stearic acid | Texture | Animal fat | Plant stearic acid |
| Shellac (E904) | Glazing | Insect secretion | Carnauba wax, zein |
| L-cysteine (E920) | Dough conditioner | Human hair, duck feathers | Synthetic |
| Mono/diglycerides | Emulsifier | Animal fat | Vegetable source |
| Lecithin | Emulsifier | Soy (halal), egg (halal) | Usually OK |

**Category-specific evaluation:**

**1. Gummy candies checklist:**
- Gelatin source: CRITICAL (often pork)
- Glazing agents: Shellac, beeswax, carnauba
- Colors: Carmine (E120)
- Flavors: Alcohol carrier
- Acids: Usually halal

**2. Chocolate checklist:**
- Cocoa mass: HALAL
- Cocoa butter: HALAL
- Sugar: HALAL (check bone char)
- Milk powder: HALAL
- Lecithin (E322): Usually soy (HALAL)
- Emulsifiers: Check E471, PGPR
- Flavors: Vanilla extract (alcohol)
- Inclusions: Nuts OK, may have other issues

**3. Hard candies checklist:**
- Sugar/glucose: Usually HALAL
- Colors: Check E120
- Flavors: Alcohol content
- Acids: Usually HALAL
- Coating/polish: Shellac, wax

**4. Marshmallows checklist:**
- Gelatin: CRITICAL (often pork)
- Sugar: Usually HALAL
- Corn syrup: HALAL
- Flavor: Check vanilla
- Color: Usually OK

**Evaluation by product type:**

Gelatin products (gummies, marshmallows, mousse, jellies): HIGH risk - main concern is gelatin
Chocolate (plain): LOW risk - check emulsifiers, vanilla
Chocolate (filled): MEDIUM risk - check filling ingredients
Sugar confectionery (hard candy): LOW risk - check colors, flavors
Toffee/caramel: MEDIUM risk - emulsifiers, butter
Coated products: MEDIUM risk - check glazing agent, coating

**Sugar processing note:**
Some refined sugar may use:
- Bone char (from cattle bones) for whitening
- Most certifiers: Allow if fully refined (transformation)
- Strict view: Avoid bone char refined sugar
- Alternative: Beet sugar, unrefined cane sugar

**Confectionery ingredient checklist:**

Gelatin: None / Pork / Halal beef / Fish / Plant alternative (certificate required)
Colors: E120 (Carmine) - REJECT if present
Emulsifiers E471/472: Verify source
Flavors: Alcohol content in flavor and final product
Glazing: Shellac (reject) / Beeswax (acceptable) / Carnauba (HALAL)

**Halal confectionery trend:**
Major manufacturers increasingly offer halal lines:
- Haribo (halal gelatin versions in some markets)
- Mars (working on halal options)
- Regional brands with full halal certification""",
        "rejected": "Check for pork gelatin in gummies and marshmallows, carmine (E120) for red color, and shellac for glazing. Use halal alternatives available."
    },
    {
        "category": "ingredients",
        "prompt": "What meat and poultry ingredients require halal verification beyond whole cuts?",
        "chosen": """**Processed meat/poultry ingredient verification:**

**Beyond whole cuts - ingredient categories:**

| Category | Examples | Halal Concerns |
|----------|----------|----------------|
| Meat extracts | Beef extract, chicken stock | Slaughter method |
| Fats and oils | Tallow, lard, chicken fat | Animal source, slaughter |
| Proteins | Collagen, gelatin | Source animal and slaughter |
| Flavors | Meat flavors, reaction flavors | Source, processing |
| Enzymes | From animal tissues | Source, slaughter |
| Casings | Natural casings | From halal slaughter animal |

**Meat extracts and stocks verification:**
- Animal species: Must be halal animal
- Slaughter method: Must be Islamic slaughter
- Processing facility: Should be halal certified
- Additives: Check all added ingredients
- Certificate: Halal certification required

**Animal fats:**

| Fat | Source | Halal Status |
|-----|--------|--------------|
| Lard | Pig | HARAM |
| Tallow (beef) | Cattle | HALAL if from halal slaughter |
| Tallow (mixed) | Various | Must verify source |
| Chicken fat | Poultry | HALAL if halal slaughter |
| Duck fat | Duck | HALAL if halal slaughter |

**Hidden meat-derived ingredients:**

GELATIN: From bones/skin - requires halal slaughter
COLLAGEN: From connective tissue - requires halal slaughter
BONE PHOSPHATE (E542): From bones - check source
PEPSIN: From stomach lining - often porcine (HARAM)
PANCREATIN: From pancreas - often porcine (HARAM)
GLYCERIN (some): May be from animal fat - verify source
STEARIC ACID (some): May be from animal fat - verify source
NATURAL CASINGS: Intestines - requires halal slaughter
COLLAGEN CASINGS: Made from collagen - check source

**Flavors and seasonings:**

Natural meat flavor: May contain actual meat/fat - halal certificate required
Hydrolyzed protein: Animal HVP from animal protein - check source; Plant HVP from soy/wheat - HALAL
Reaction flavor: Check amino acid source
Yeast extract: Generally HALAL, check growth medium if animal-derived

**Processed meat products:**

| Product | Components to Verify |
|---------|---------------------|
| Sausages | Meat, fat, casings, binders, seasoning |
| Burgers | Meat, fat, binders, seasonings |
| Deli meats | Meat, curing agents, binders, casings |
| Bacon (non-pork) | Source animal, processing |
| Meat balls | Meat, fat, binders, breadcrumbs |
| Pet food | All meat and derivatives |

**Halal meat certification chain:**
Farm -> Slaughterhouse -> Processing -> Distribution -> Retail
All stages require halal compliance

**Documentation required:**
- Species confirmation
- Slaughterhouse halal certificate
- Chain of custody documentation
- Processing facility halal certificate
- If imported: Country of origin, CB recognition, import documentation
- Batch traceability
- Storage/transport segregation evidence

**Slaughter requirements reminder:**
- Slaughterman: Muslim, sane, adult
- Animal: Alive at slaughter
- Method: Sharp knife to throat
- Cut: Trachea, esophagus, jugular veins
- Invocation: "Bismillah, Allahu Akbar"
- Bleeding: Must be complete
- Stunning: Restricted or prohibited (varies)

**Verification challenges:**

| Challenge | Mitigation |
|-----------|------------|
| Multiple suppliers | Approved supplier program |
| Mixed processing | Dedicated or time segregation |
| Imported ingredients | Verify CB recognition |
| Sub-ingredients | Full disclosure requirement |""",
        "rejected": "Verify slaughter method for all meat derivatives including extracts, stocks, fats, gelatin, and casings. Natural casings must be from halal-slaughtered animals."
    },
    {
        "category": "ingredients",
        "prompt": "How do I evaluate ingredients in pharmaceutical excipients?",
        "chosen": """**Pharmaceutical excipient halal evaluation:**

**Common excipients and concerns:**

| Excipient Class | Examples | Halal Concern |
|-----------------|----------|---------------|
| Capsule shells | Gelatin, HPMC | Gelatin often pork |
| Lubricants | Magnesium stearate | Animal or vegetable |
| Binders | Gelatin, starch | Gelatin concern |
| Coatings | Shellac, gelatin | Insect, animal |
| Glycerin | Glycerol | Animal or vegetable |
| Stearates | Various | Animal or vegetable |
| Oleic acid | Emulsifier | Animal or vegetable |

**Capsule shell evaluation:**

| Type | Source | Halal Status |
|------|--------|--------------|
| Hard gelatin (porcine) | Pig skin | HARAM |
| Hard gelatin (bovine) | Cattle | HALAL if halal slaughter |
| Soft gelatin | Often porcine | Usually HARAM |
| HPMC (Hypromellose) | Plant cellulose | HALAL |
| Pullulan | Fungal fermentation | HALAL |
| Starch-based | Plant | HALAL |

**Evaluation by excipient type:**

Capsule shells:
- Gelatin porcine: HARAM
- Gelatin bovine uncertified: MASHBOOH
- Gelatin bovine halal certified: HALAL
- Gelatin fish: HALAL
- HPMC/Pullulan: HALAL

Lubricants:
- Magnesium stearate vegetable: HALAL
- Magnesium stearate animal: Verify source
- Magnesium stearate mixed: MASHBOOH
- Talc: HALAL
- Colloidal silicon dioxide: HALAL

Coatings:
- HPMC coating: HALAL
- Shellac: Debated (insect)
- Gelatin coating: Check source

Sweeteners:
- Sucrose, mannitol, sorbitol, aspartame: HALAL

Colors:
- E120 carmine: HARAM (insect)
- Titanium dioxide, iron oxides: HALAL

**Critical excipients list:**

HIGH RISK - always verify:
- Gelatin (all forms)
- Stearic acid and stearates
- Glycerin/glycerol
- Oleic acid
- Mono/diglycerides
- Polysorbates (some)
- Sodium stearyl fumarate
- Any "animal-derived" labeled

MEDIUM RISK - check when possible:
- Lactose (check whey source if from cheese)
- Shellac (insect - debated)
- Lecithin (usually soy - OK)
- Fatty acid derivatives

LOW RISK - generally halal:
- Cellulose derivatives (HPMC, etc.)
- Starches (plant)
- Sugars
- Mineral compounds
- Synthetic chemicals

**Manufacturer questionnaire:**
PHARMACEUTICAL EXCIPIENT HALAL QUESTIONNAIRE
1. Source of raw materials: Plant/Mineral/Synthetic/Animal (species, halal slaughter certified)
2. For stearic acid/stearates: Vegetable/Animal/Mixed
3. For glycerin: Vegetable/Animal/Synthetic
4. For capsule shells: HPMC/Gelatin (source if gelatin)
5. Manufacturing: Dedicated halal line? Cross-contamination controls?
6. Halal certification available?

**Halal pharmaceutical excipient suppliers:**
Major suppliers offering halal-certified excipients:
- Capsugel (HPMC capsules)
- ACG (capsules)
- Roquette (plant-based)
- BASF (specific lines)
- Croda (oleochemicals)

**Regulatory note:**
While halal is a consumer preference, pharmaceutical products may invoke dharura (necessity) principle if:
- Life-saving medication
- No halal alternative available
- Prescribed by physician

However, manufacturers should still strive for halal formulations when alternatives exist.""",
        "rejected": "Check capsule shells (gelatin vs. HPMC), magnesium stearate source, glycerin source, and any coatings. HPMC capsules are halal alternatives to gelatin."
    },
    {
        "category": "ingredients",
        "prompt": "How do I evaluate natural and artificial colors for halal compliance?",
        "chosen": """**Color additives halal evaluation:**

**Natural colors:**

| Color | Source | Halal Status |
|-------|--------|--------------|
| Carmine (E120) | Cochineal insect | HARAM (insect) |
| Annatto (E160b) | Plant seed | HALAL |
| Turmeric (E100) | Plant root | HALAL |
| Paprika (E160c) | Plant | HALAL |
| Beetroot red (E162) | Plant | HALAL |
| Chlorophyll (E140) | Plant | HALAL |
| Caramel (E150) | Sugar | HALAL |
| Carotenes (E160a) | Plant/synthetic | HALAL |
| Anthocyanins (E163) | Plant | HALAL |

**Synthetic colors:**

| Color | Code | Halal Status |
|-------|------|--------------|
| Tartrazine | E102 | HALAL |
| Sunset Yellow | E110 | HALAL |
| Allura Red | E129 | HALAL |
| Brilliant Blue | E133 | HALAL |
| Indigo Carmine | E132 | HALAL |

**Critical concern - Carmine (E120):**

Why it's problematic:
- Derived from crushed cochineal insects
- Provides bright red color
- Common in beverages, confectionery, cosmetics
- Listed as: Carmine, Cochineal, E120, CI 75470, Natural Red 4

Halal ruling:
- Majority scholarly opinion: HARAM (insect-derived)
- No halal-certified alternative from same source
- Must use alternatives

Carmine alternatives:
| Alternative | Code | Notes |
|-------------|------|-------|
| Beetroot red | E162 | Plant-based, less stable |
| Allura Red AC | E129 | Synthetic, stable |
| Anthocyanins | E163 | Plant-based, pH sensitive |
| Paprika extract | E160c | Orange-red, natural |
| Lycopene | E160d | Tomato-derived |

**Verification process:**

For natural colors:
1. Identify source (plant, animal, insect)
2. If animal: Verify halal slaughter (if applicable)
3. If insect: HARAM (E120, E904 shellac)
4. Check processing aids (may use animal enzymes)
5. Verify carrier/solvent (not alcohol-based)

For synthetic colors:
1. Generally HALAL
2. Check manufacturing process
3. Verify no animal-derived processing aids
4. Check carrier/solvent

**Color ingredient questionnaire:**

Color name: _____
E-number: _____
Source: Plant / Synthetic / Animal / Insect

If plant: Specify plant _____
If animal: Halal certificate required _____
If insect: NOT ACCEPTABLE

Processing aids used: _____
Carrier/solvent: Water / Propylene glycol / Ethanol / Other

Halal certificate available: Yes / No
Certificate number: _____

**Documentation required:**
- Color specification sheet
- Source declaration
- Processing information
- Halal certificate (if animal-derived or complex)
- Carrier/solvent declaration""",
        "rejected": "Carmine (E120) is haram as it's insect-derived. Most synthetic colors and plant-derived colors like turmeric, beetroot, and annatto are halal."
    },
    {
        "category": "ingredients",
        "prompt": "What vitamins and mineral supplements require halal verification?",
        "chosen": """**Vitamins and minerals halal evaluation:**

**Vitamin sources and concerns:**

| Vitamin | Potential Concern | Halal Verification |
|---------|------------------|-------------------|
| Vitamin A | Fish liver oil, synthetic | Check source |
| Vitamin D3 | Lanolin (sheep), lichen, fish | Check source, slaughter |
| Vitamin E | Soy, palm (halal) | Usually OK |
| Vitamin B12 | Fermentation | Usually OK |
| B vitamins | Fermentation, synthetic | Usually OK |
| Vitamin C | Synthetic, plant | HALAL |
| Vitamin K | Synthetic, fermentation | Usually OK |

**Critical vitamin - Vitamin D3:**

Sources:
- Lanolin (sheep wool): Halal if from halal-slaughtered sheep
- Fish liver oil: HALAL (fish)
- Lichen (plant): HALAL
- Synthetic: HALAL

Verification required:
- Most commercial D3 from lanolin
- Some scholars: Lanolin halal regardless of slaughter (external secretion)
- Strict view: Requires halal slaughter certification
- Safest: Lichen-derived or fish oil D3

**Mineral sources:**

| Mineral | Form | Halal Status |
|---------|------|--------------|
| Calcium | Carbonate, citrate | HALAL |
| Calcium | Bone meal | Check source |
| Iron | Ferrous sulfate, fumarate | HALAL |
| Zinc | Sulfate, gluconate | HALAL |
| Magnesium | Oxide, citrate | HALAL |
| Phosphorus | Various forms | HALAL |
| Iodine | Potassium iodide | HALAL |

**Delivery forms - concerns:**

Capsules:
- Gelatin: Check source (porcine HARAM, halal bovine OK, HPMC halal)
- Softgel: Often porcine gelatin - verify

Tablets:
- Binders: May include gelatin
- Lubricants: Magnesium stearate (check source)
- Coatings: May include shellac

Liquids:
- Solvent: May contain alcohol
- Glycerin: Check source

Gummies:
- Gelatin: Often porcine - critical check
- Colors: Check for E120 carmine

**Excipient checklist:**

| Excipient | Concern | Halal If |
|-----------|---------|----------|
| Gelatin | Animal source | Halal certified |
| Magnesium stearate | May be animal | Vegetable source |
| Stearic acid | May be animal | Vegetable source |
| Glycerin | May be animal | Vegetable source |
| Shellac | Insect | Debated, avoid if strict |

**Supplement questionnaire:**

HALAL SUPPLEMENT VERIFICATION
Product: _____
Form: Capsule / Tablet / Softgel / Liquid / Gummy / Powder

ACTIVE INGREDIENTS:
| Vitamin/Mineral | Source | Halal Cert |
|-----------------|--------|------------|
| | | |

CAPSULE SHELL (if applicable):
Type: Gelatin / HPMC / Pullulan
If gelatin, source: Bovine / Fish / Porcine
Halal certificate: _____

EXCIPIENTS:
| Excipient | Source | Halal Cert |
|-----------|--------|------------|
| | | |

Overall halal status: Halal / Not Halal / Needs verification

**Halal vitamin brands:**

Many manufacturers now offer halal-certified lines:
- Specifically marketed halal vitamin brands
- HPMC capsule versions
- Vegetable-source excipients
- Certification from recognized bodies

**Consumer guidance:**

For maximum assurance:
1. Look for halal certification logo
2. Check capsule type (HPMC vs gelatin)
3. Verify D3 source
4. Check gummy products carefully
5. Review all excipients""",
        "rejected": "Check vitamin D3 source (lanolin vs. lichen), capsule shells (gelatin vs. HPMC), and excipients like magnesium stearate. Many vitamins are now available in halal-certified forms."
    },

    # ============ AUDIT (12 items) ============
    {
        "category": "audit",
        "prompt": "What does a halal audit cover and how should I prepare?",
        "chosen": """**Halal audit scope and preparation:**

**Audit types:**

| Type | Purpose | Frequency |
|------|---------|-----------|
| Initial/certification | First certification | Once |
| Surveillance | Maintain certification | 1-2 per year |
| Renewal | Certificate renewal | Before expiry |
| Unannounced | Verify ongoing compliance | Random |
| For-cause | Investigate complaint/issue | As needed |

**Audit scope areas:**

DOCUMENTATION REVIEW:
- Halal policy and manual
- Procedures (SOPs)
- Ingredient specifications
- Supplier halal certificates
- Training records
- Internal audit records
- Non-conformance records

FACILITY INSPECTION:
- Receiving area
- Raw material storage
- Production areas
- Packaging
- Finished goods storage
- Shipping

PROCESS VERIFICATION:
- Ingredient handling
- Production line setup
- Cleaning procedures
- Cross-contamination controls
- Traceability demonstration

PERSONNEL:
- Halal committee competency
- Staff awareness
- Training records
- Roles and responsibilities

RECORDS:
- Batch records
- Receiving logs
- Cleaning logs
- Supplier evaluations
- Corrective actions

**Preparation checklist:**

Documentation:
- Halal policy (signed, dated)
- HAS manual (current revision)
- Organization chart with halal roles
- Halal committee meeting minutes
- Product list with halal status
- Approved supplier list
- Supplier halal certificates (current)
- All SOPs (current)
- Training records (all staff)
- Internal audit reports
- Corrective action records

Facility:
- Clean and organized
- Clear signage (halal zones)
- Segregation in place
- Equipment properly labeled
- No non-halal items in halal areas
- Storage properly segregated

Records:
- Recent batch records ready
- Receiving logs available
- Cleaning records current
- Temperature logs (if applicable)
- Traceability demo prepared

Personnel:
- Halal committee available
- Key staff briefed
- Escorts assigned
- Production schedule shared

**What auditors look for:**

CRITICAL (will fail if not met):
- Non-halal ingredient in halal product
- Pork/haram contamination
- Missing/expired supplier certificates
- False halal claims
- Major undeclared changes

MAJOR (corrective action required):
- Incomplete documentation
- Inadequate segregation
- Training gaps
- Traceability gaps
- Internal audit not conducted

MINOR (improvement needed):
- Documentation not current
- Records incomplete
- Signage unclear
- Minor procedure gaps

**Day of audit:**
1. Opening meeting (introductions, scope, schedule)
2. Document review (policy, procedures, records)
3. Facility tour (receiving to shipping)
4. Traceability exercise
5. Auditor private time
6. Closing meeting (findings, corrective actions, next steps)""",
        "rejected": "Auditors check documentation, facility compliance, ingredient verification, and traceability. Prepare by ensuring all certificates are current and facilities are compliant."
    },
    {
        "category": "audit",
        "prompt": "How do I conduct an internal halal audit?",
        "chosen": """**Internal halal audit process:**

**Purpose:** Self-assessment to ensure ongoing compliance and identify issues before external audit.

**Audit program requirements:**

| Element | Requirement |
|---------|-------------|
| Frequency | Minimum annual (more often recommended) |
| Coverage | All halal-related areas |
| Independence | Auditor not responsible for area audited |
| Competence | Trained in halal and audit techniques |
| Documentation | Checklist, findings, corrective actions |

**Audit planning:**

Scope: All processes affecting halal status
Objectives: Verify compliance, verify HAS effectiveness, identify improvements, prepare for external audit
Areas: Ingredient control, supplier management, production, storage, cleaning, training, documentation, traceability
Schedule: Day 1 documentation review, Day 2 facility and interviews, Day 3 traceability and reporting
Team: Lead auditor (halal trained), technical expert (if needed)

**Audit checklist template:**

INTERNAL HALAL AUDIT CHECKLIST
Area: Ingredient Control
Auditor: _____ Date: _____

1. APPROVED SUPPLIER LIST
   - List maintained and current
   - All halal suppliers on list
   - Non-halal suppliers identified
   Evidence reviewed: _____
   Finding: Conform / Non-conform
   Notes: _____

2. SUPPLIER CERTIFICATES
   - All certificates on file
   - All certificates current (not expired)
   - Scope covers products supplied
   - Certification body recognized
   Sample checked: _____
   Finding: Conform / Non-conform
   Notes: _____

3. RECEIVING INSPECTION
   - Procedure in place
   - Halal verification performed
   - Records maintained
   - Non-conformances handled
   Records reviewed: _____
   Finding: Conform / Non-conform
   Notes: _____

(Continue for all areas)

**Non-conformance classification:**

| Category | Definition | Action Required |
|----------|------------|-----------------|
| Critical | Halal status compromised | Immediate containment, stop production |
| Major | System failure, potential risk | Corrective action within 30 days |
| Minor | Documentation gap, no product risk | Corrective action within 90 days |
| Observation | Improvement opportunity | Not mandatory |

**Audit report template:**

INTERNAL HALAL AUDIT REPORT
Audit Date: _____
Auditor(s): _____
Areas Audited: _____

EXECUTIVE SUMMARY:
Overall compliance status: Satisfactory / Needs improvement / Unsatisfactory
Critical/Major/Minor findings count
Observations count

FINDINGS DETAIL:
For each finding:
- Area
- Requirement
- Observation
- Classification
- Evidence
- Corrective Action Required
- Responsible
- Due Date

TRACEABILITY EXERCISE:
Forward trace result: Pass / Fail
Backward trace result: Pass / Fail
Time to complete: _____

APPROVAL:
Auditor signature and date
Reviewed by signature and date

**Follow-up process:**
1. Finding documented
2. Root cause analysis
3. Corrective action defined
4. Responsible person assigned
5. Due date set
6. Action implemented
7. Verification performed
8. Finding closed
9. Reported to management""",
        "rejected": "Schedule annual internal audits with trained auditors. Use a checklist covering ingredients, production, storage, and documentation. Report findings and track corrective actions."
    },
    {
        "category": "audit",
        "prompt": "What are common non-conformances found in halal audits?",
        "chosen": """**Common halal audit non-conformances:**

**Category 1: Ingredient issues (most common)**

| Non-Conformance | Frequency | Severity |
|-----------------|-----------|----------|
| Expired supplier certificates | Very common | Major |
| Missing halal certificates | Common | Critical/Major |
| Unverified ingredient sources | Common | Major |
| Undeclared ingredient changes | Occasional | Critical |
| Mashbooh ingredients without evaluation | Common | Major |

**Category 2: Documentation gaps**

Common documentation findings:
- Halal policy not signed/dated
- Manual not current revision
- SOPs missing or outdated
- Training records incomplete
- Internal audit not conducted
- Meeting minutes not maintained
- Corrective actions not closed
- Batch records incomplete
- Receiving logs missing entries
- Traceability gaps

**Category 3: Facility issues**

| Non-Conformance | Description | Severity |
|-----------------|-------------|----------|
| Inadequate segregation | Halal/non-halal not separated | Major |
| Poor labeling | Equipment, storage not marked | Minor-Major |
| Cross-contamination risk | Shared equipment, inadequate cleaning | Major-Critical |
| Improper storage | Non-halal above halal, no barriers | Major |
| Cleaning validation lacking | No records for changeover | Major |

**Category 4: Personnel issues**

Personnel-related findings:
- Training not conducted
- Staff unaware of halal requirements
- Halal committee not meeting
- No Muslim representation (where required)
- Roles not defined
- Competence not verified

**Category 5: Process control**

| Non-Conformance | Impact |
|-----------------|--------|
| No verification at receiving | Unknown ingredient status |
| Production without halal check | Non-halal may be used |
| Changeover not validated | Cross-contamination risk |
| Traceability incomplete | Cannot trace issues |
| Non-conformance not handled | Affected product released |

**Root cause analysis:**

Expired certificates root causes:
- No tracking system
- Responsibility not assigned
- Supplier not responsive
- Certificate validity not checked at receiving

Documentation gaps root causes:
- Insufficient resources
- Training inadequate
- No document control system
- Staff turnover

Segregation issues root causes:
- Facility limitations
- Staff awareness
- No procedures
- Cost considerations

**Prevention strategies:**

| Issue | Prevention |
|-------|------------|
| Expired certificates | Automated tracking, 60-day advance notice |
| Documentation gaps | Regular review schedule, document control |
| Segregation | Clear SOPs, physical controls, visual management |
| Training | Annual schedule, new employee onboarding |
| Traceability | Electronic system, regular exercises |

**Top 10 audit findings (ranked by frequency):**

1. Supplier certificates expired or missing
2. Training records incomplete
3. Internal audit not conducted or incomplete
4. SOPs not current or not followed
5. Segregation inadequate or unclear
6. Cleaning validation records missing
7. Ingredient change not communicated
8. Halal committee not meeting regularly
9. Traceability exercise failed or slow
10. Non-conformance not properly closed""",
        "rejected": "Common findings include expired supplier certificates, incomplete training records, inadequate segregation, and documentation gaps. Address root causes systematically."
    },
    {
        "category": "audit",
        "prompt": "How do I handle a critical non-conformance during a halal audit?",
        "chosen": """**Critical non-conformance response protocol:**

**What constitutes "critical":**

| Finding | Classification |
|---------|---------------|
| Non-halal ingredient in halal product | CRITICAL |
| Pork contamination evidence | CRITICAL |
| Falsified halal certificates | CRITICAL |
| Major undeclared changes | CRITICAL |
| Systemic failure in halal control | CRITICAL |

**Immediate response (within hours):**

Step 1 - Containment:
- Stop production immediately
- Identify all potentially affected products
- Quarantine suspect inventory
- Timeline: Within 1 hour of discovery

Step 2 - Notification:
- Internal: Halal Committee Chair, Quality Manager, Plant Manager, Legal (if needed)
- External: Certification body (same day), customers (if product shipped)
- Timeline: Within 4 hours

Step 3 - Investigation:
- What exactly happened?
- When did it occur?
- What products/batches affected?
- Quantity of affected product
- Why (root cause)
- Timeline: Begin immediately, complete within 24-48 hours

Step 4 - Containment verification:
- Verify all affected product identified
- Forward and backward trace
- Complete records
- Timeline: Within 24 hours

**Escalation matrix:**

| Severity | Decision Authority | Notification |
|----------|-------------------|--------------|
| Potential critical | Halal Executive | Halal Committee |
| Confirmed critical | Plant Manager | Certification body + senior management |
| Product released | CEO/MD | Regulatory, customers, potentially public |

**Product disposition decision:**

| Status | Action |
|--------|--------|
| In production | Stop, quarantine |
| In warehouse | Quarantine, pending decision |
| In distribution | Recall consideration |
| With customer | Notification, return/recall |

**Recall decision criteria:**
Factors: Severity of breach, quantity in distribution, customer exposure, regulatory requirements, reputational impact
Decision options: No recall (all contained), customer notification (B2B), voluntary recall (consumer), mandatory recall (regulatory)

**Communication to certification body:**

CRITICAL NON-CONFORMANCE NOTIFICATION
To: [Certification Body]
Date: _____
Reference: Certificate # _____

IMMEDIATE NOTIFICATION
Date/time discovered: _____
Nature of issue: _____
Products affected: _____
Batches affected: _____

IMMEDIATE ACTIONS TAKEN:
1. Production stopped
2. Product quarantined (quantity)
3. Traceability initiated

PRELIMINARY FINDINGS: _____
CONTAINMENT STATUS: All contained / Product in distribution (quantity, customers)

Full investigation report to follow within [X] days.

**Certification body response:**

| Situation | Likely Action |
|-----------|---------------|
| Contained, no distribution | Investigation, possible additional audit |
| Product in market | May require recall, suspension consideration |
| Falsification | Immediate suspension |
| Systemic failure | Certificate suspension pending corrective action |

**Recovery path:**
1. Complete investigation
2. Implement corrective actions
3. Implement preventive measures
4. Submit evidence to certification body
5. Re-audit (usually required)
6. Certification body review
7. Certificate reinstated (with conditions)""",
        "rejected": "Stop production immediately, quarantine affected products, notify your certification body same day, investigate root cause, and implement corrective actions."
    },
    {
        "category": "audit",
        "prompt": "What is a halal traceability exercise and how do I pass it?",
        "chosen": """**Halal traceability exercise:**

**Purpose:** Demonstrate ability to trace products forward and backward through the supply chain within a reasonable time.

**Standard requirements:**

| Standard | Time Limit | Scope |
|----------|------------|-------|
| JAKIM | 4 hours | Full trace |
| MUI | 4 hours | Full trace |
| GFSI schemes | 4 hours | Full trace |
| Best practice | 2-4 hours | Both directions |

**Traceability directions:**

FORWARD TRACE (Ingredient to Product to Customer):
Raw material batch -> Production batch -> Finished product -> Shipment -> Customer

BACKWARD TRACE (Customer to Product to Ingredient):
Customer complaint -> Shipment -> Finished product -> Production batch -> Raw materials

**Exercise procedure:**

Forward trace:
- Auditor provides: Ingredient batch number
- Company demonstrates: Which production batches used this ingredient, which finished product batches, which customers received product, quantity at each step
- Time limit: 2 hours typical

Backward trace:
- Auditor provides: Finished product batch number
- Company demonstrates: All ingredients used (with batch numbers), supplier of each, halal certificate for each, production records, operator information
- Time limit: 2 hours typical

**Information to retrieve:**

Forward trace steps:
1. Ingredient batch, supplier, halal cert
2. Receiving date, inspection record
3. Storage location
4. Production batches using ingredient
5. Finished product batches
6. Shipment records
7. Customer and quantity

Backward trace steps:
1. Finished product batch
2. Production date, line, operators
3. All ingredients with batch numbers
4. Supplier for each ingredient
5. Halal certificate for each
6. Receiving records
7. Storage records

**Preparation:**

SYSTEMS:
- Ensure ERP/records accessible
- Key personnel available
- Documentation organized
- Practice runs conducted

DOCUMENTATION:
- Batch record format complete
- All fields filled correctly
- Ingredient lot numbers recorded
- Supplier info linked
- Customer shipment records

PRACTICE:
- Conduct mock exercises quarterly
- Time the exercise
- Identify bottlenecks
- Improve weak points

READY-ACCESS:
- Recent batch records at hand
- Supplier certificates organized
- Shipment records accessible
- Contact information available

**Common failure points:**

| Issue | Prevention |
|-------|------------|
| Ingredient lot not recorded | Mandatory field in batch record |
| Can't find supplier certificate | Certificate filing system |
| Shipment records incomplete | Link batch to shipment |
| Takes too long | Practice, better systems |
| Paper records missing | Backup copies, digital scanning |

**Example traceability matrix:**

Finished Product Batch: FP-2024-0125
Production Date: 2024-03-15
Line: L2

INGREDIENTS:
| Ingredient | Lot Number | Supplier | Halal Cert | Cert Exp |
|------------|------------|----------|------------|----------|
| Sugar | SUG-24-001 | Supplier A | HA-2024-001 | 2025-01 |
| Flour | FLR-24-055 | Supplier B | HA-2024-010 | 2024-12 |
| Flavor XYZ | FLV-24-010 | Supplier C | HA-2023-050 | 2024-06 |
| Emulsifier | EMU-24-003 | Supplier D | HA-2024-022 | 2025-03 |

DISTRIBUTION:
| Customer | Ship Date | Invoice | Quantity |
|----------|-----------|---------|----------|
| Customer A | 2024-03-16 | INV-1001 | 500 cases |
| Customer B | 2024-03-17 | INV-1002 | 300 cases |

**Pass criteria:**

| Criteria | Requirement |
|----------|-------------|
| Time | Complete within limit (4 hours) |
| Accuracy | All information correct |
| Completeness | No missing links in chain |
| Certificates | All halal certs retrieved |
| Documentation | Records support trace |""",
        "rejected": "Practice forward and backward tracing until you can complete both directions within 4 hours. Record all ingredient lot numbers in batch records and keep certificates organized."
    },
    {
        "category": "audit",
        "prompt": "How do I prepare staff for halal audit interviews?",
        "chosen": """**Staff interview preparation:**

**Why auditors interview staff:**

| Purpose | What They're Checking |
|---------|----------------------|
| Awareness | Do staff understand halal basics? |
| Competence | Can they perform their halal-related tasks? |
| Implementation | Do they actually follow procedures? |
| Culture | Is halal taken seriously? |

**Who may be interviewed:**

Halal Committee members: Deep knowledge expected
Production supervisors: Process knowledge, halal critical points
Production operators: Practical procedures, daily activities
Receiving personnel: Inspection procedures
Warehouse staff: Storage, segregation
Quality staff: Verification, documentation
New employees: Basic awareness, training received

**Common interview questions:**

General awareness (all staff):
- What is halal? (Permissible in Islam)
- Why is halal important here? (Company policy, certification, customers)
- What is haram? (Prohibited: pork, blood, alcohol, improper slaughter)
- What would you do if you saw non-halal item in halal area? (Report to supervisor, do not use)

**Role-specific questions:**

RECEIVING STAFF:
- How do you verify incoming ingredients are halal?
- Where do you check the halal certificate?
- What do you do if a certificate is expired?
- How do you handle non-halal deliveries?
- Show me where you record halal verification.

PRODUCTION OPERATORS:
- How do you know a product is halal?
- What are the halal critical points in your process?
- How do you prevent cross-contamination?
- What do you do between halal and non-halal products?
- How do you record ingredient lot numbers?
- What would you do if you suspected a halal issue?

WAREHOUSE STAFF:
- How do you segregate halal from non-halal?
- Show me where halal products are stored.
- How do you identify halal inventory?
- What is FIFO and why is it important?
- How do you handle a damaged halal product?

QUALITY/HALAL COMMITTEE:
- Describe your Halal Assurance System.
- How do you evaluate new ingredients?
- How do you manage supplier certificates?
- How often does the halal committee meet?
- Describe a recent halal issue and how you handled it.
- How do you conduct internal audits?

**Training for interviews:**

General briefing (1 week before, all staff):
- Audit is coming
- May be asked questions
- Be honest
- If unsure, say so
- Know your role in halal

Department specific (2-3 days before, key staff):
- Review SOPs for your area
- Practice likely questions
- Know where records are
- Be ready to demonstrate

Halal committee (ongoing + refresh before audit):
- Full HAS knowledge
- Recent issues and resolutions
- System performance metrics
- Improvement initiatives

**Do's and Don'ts:**

| DO | DON'T |
|----|-------|
| Answer honestly | Make up answers |
| Say "I don't know" if unsure | Guess or bluff |
| Offer to find out | Provide wrong information |
| Give examples from work | Give textbook answers only |
| Stay calm | Be defensive or argumentative |
| Listen to question fully | Interrupt auditor |
| Ask for clarification | Assume meaning |

**Red flags auditors watch for:**

| Behavior | Implication |
|----------|-------------|
| All answers identical | Scripted, not genuine understanding |
| No one knows basic halal | Training inadequate |
| Conflicting answers | Procedures not clear |
| Cannot show records | Documentation issues |
| Defensive or evasive | Possible concealment |
| Refer all questions to one person | Dependency, not team ownership |

**Positive indicators:**

| Behavior | Implication |
|----------|-------------|
| Confident, specific answers | Good understanding |
| References actual practice | Implementation working |
| Knows where to find info | System in place |
| Asks clarifying questions | Engaged, thoughtful |
| Honest about limitations | Integrity, improvement mindset |""",
        "rejected": "Brief staff on audit expectations, review their role-specific procedures, practice likely questions, and remind them to be honest and stay calm."
    },
    {
        "category": "audit",
        "prompt": "What records should I have ready for a halal audit?",
        "chosen": """**Halal audit documentation checklist:**

**Category 1: Policy and Manual**

| Document | Description | Readiness Check |
|----------|-------------|-----------------|
| Halal Policy | Signed, dated commitment | Required |
| HAS Manual | Complete system description | Required |
| Organization chart | Shows halal roles | Required |
| Halal Committee charter | Terms of reference | Required |

**Category 2: Procedures (SOPs)**

Required SOPs:
- Purchasing procedure
- Receiving inspection
- Ingredient approval
- Supplier management
- Production procedure
- Equipment handling
- Changeover/cleaning
- Non-conformance handling
- Warehouse management
- Segregation procedure
- FIFO procedure
- Batch coding
- Recall procedure
- Traceability exercise
- Document control
- Training procedure
- Internal audit procedure
- Corrective action procedure

**Category 3: Supplier Records**

| Record | Requirements |
|--------|--------------|
| Approved Supplier List | Current, complete |
| Halal certificates | All valid, correct scope |
| Supplier questionnaires | For Tier 1/2 suppliers |
| Supplier audits | If applicable |
| Verification records | Certificate checks |

**Category 4: Ingredient Records**

Per ingredient:
- Specification sheet
- Halal certificate (copy)
- Certificate expiry tracking
- CoA (recent batches)
- MSDS/SDS
- Approval record
- Change history

**Category 5: Receiving Records**

| Record | Content | Retention |
|--------|---------|-----------|
| Receiving log | Date, item, supplier, batch, verification | 3 years |
| Inspection records | Halal check results | 3 years |
| Rejection records | Non-conforming items | 3 years |
| COA on file | Per batch received | 3 years |

**Category 6: Production Records**

Batch record elements:
- Batch/lot number
- Product name
- Production date/time
- Production line
- Operators
- Ingredients used (name, lot number, quantity, halal status verified)
- Equipment used
- Cleaning verification (if applicable)
- Quality checks
- Packaging materials (lot)
- Release authorization

**Category 7: Cleaning Records**

| Record | Content |
|--------|---------|
| Cleaning log | Date, equipment, product before/after |
| Cleaning verification | Visual, swab test results |
| Changeover record | Non-halal to halal verification |
| Cleaning SOP reference | Procedure followed |

**Category 8: Training Records**

Training file contents:
- Training needs assessment
- Training plan/schedule
- Training attendance (date, topic, trainer, attendees, duration)
- Training materials
- Assessment results (if applicable)
- Training certificates
- Training matrix (who needs what)

**Category 9: Audit Records**

| Record | Requirements |
|--------|--------------|
| Internal audit schedule | Planned audits |
| Internal audit reports | Findings documented |
| Corrective actions | From internal audits |
| External audit reports | Previous certifier audits |
| CAR closure | Evidence of completion |

**Category 10: Committee Records**

Halal Committee file:
- Committee membership list
- Terms of reference
- Meeting schedule
- Meeting minutes (date, attendees, agenda, discussions, decisions, action items)
- Action item tracking
- Annual review records

**Category 11: Traceability Records**

| Record | Content |
|--------|---------|
| Batch to ingredient link | Which lots in which batches |
| Batch to shipment link | Which batches to which customers |
| Mock recall records | Practice exercise results |
| Actual recall records | If any occurred |

**Quick access folder:**
Prepare folder with:
- Last 3 months batch records
- Current supplier certificates
- Recent receiving logs
- Recent training records
- Last internal audit report
- Open corrective actions
- Halal Committee minutes (last 2)
- Any recent non-conformances

**Retention requirements:**

| Document Type | Retention Period |
|---------------|------------------|
| Batch records | Product shelf life + 3 years |
| Training records | Employment + 3 years |
| Audit records | Minimum 3 years |
| Supplier certificates | Until expired + 3 years |
| Corrective actions | Minimum 3 years |""",
        "rejected": "Have ready: halal policy/manual, SOPs, supplier certificates, batch records, training records, internal audit reports, committee minutes, and traceability records."
    },
    {
        "category": "audit",
        "prompt": "How do I close corrective actions from a halal audit?",
        "chosen": """**Corrective action closure process:**

**Corrective action lifecycle:**
Finding -> Root Cause -> Action Plan -> Implementation -> Verification -> Closure

**Step 1: Understand the finding**
- What: Exact nature of non-conformance
- Where: Location/process affected
- When: When discovered, how long existing
- Who: Responsible party
- Severity: Critical / Major / Minor
- Deadline: Correction due date

**Step 2: Root cause analysis**

| Tool | When to Use |
|------|-------------|
| 5 Whys | Simple issues |
| Fishbone | Complex, multi-factor |
| Fault tree | Critical issues |
| Process mapping | Process-related |

**5 Whys example:**
Finding: Supplier certificate expired
Why 1: Certificate not renewed before expiry
Why 2: No reminder system in place
Why 3: Certificate tracking is manual spreadsheet
Why 4: No one assigned to maintain spreadsheet
Why 5: Process not formalized
Root cause: No formal process for certificate validity tracking

**Step 3: Corrective action plan**

CORRECTIVE ACTION REQUEST (CAR)
CAR Number: _____
Finding: _____
Severity: Critical / Major / Minor
Deadline: _____

ROOT CAUSE ANALYSIS:
Method used: _____
Root cause(s) identified: _____

CORRECTIVE ACTIONS:
| # | Action | Responsible | Due Date | Status |
|---|--------|-------------|----------|--------|
| 1 | Implement digital certificate tracking | QA Manager | 30-Apr | |
| 2 | Assign ownership for certificate management | Halal Exec | 15-Apr | |
| 3 | Set up 60-day advance alerts | IT/QA | 30-Apr | |

PREVENTIVE ACTIONS:
1. _____
2. _____

**Step 4: Implementation**

| Action Type | Evidence Required |
|-------------|-------------------|
| Procedure update | New SOP revision |
| Training | Attendance records |
| System change | Screenshots, records |
| Facility change | Photos, inspection |
| Process change | Updated flow, records |

**Step 5: Verification of effectiveness**

Verification methods:
- OBSERVATION: Watch process being followed correctly
- RECORDS REVIEW: Check new records meet requirements
- AUDIT: Re-audit the specific area
- TESTING: Test the new system/process
- INTERVIEW: Ask staff if they understand new process

**Step 6: Evidence compilation**

Evidence package:
- CAR form (completed)
- Root cause analysis
- Before state (evidence of issue)
- Actions taken (new SOP, training records, screenshots, photos)
- After state (evidence of correction)
- Effectiveness verification (method, date, verifier, evidence)
- Closure authorization

**Step 7: Closure and submission**

CORRECTIVE ACTION CLOSURE
CAR Number: _____
Original Finding: _____

ACTIONS COMPLETED:
- All actions implemented
- Effectiveness verified
- Evidence documented

VERIFICATION SUMMARY:
Method: _____
Date: _____
Result: _____

CLOSURE AUTHORIZATION:
Verified by: _____ Date: _____
Approved by: _____ Date: _____

SUBMISSION TO CERTIFIER:
- Evidence package prepared
- Submitted on: _____
- Certifier acceptance: _____

**Submission to certification body:**

| Severity | Submission Method |
|----------|-------------------|
| Critical | Immediate, detailed report |
| Major | Within deadline, evidence package |
| Minor | May be verified at next audit |

**Common rejection reasons:**

| Reason | How to Avoid |
|--------|--------------|
| Root cause superficial | Use structured analysis |
| Actions don't address root cause | Verify logic chain |
| Insufficient evidence | Document everything |
| Not verified | Always verify effectiveness |
| Deadline missed | Monitor and expedite |""",
        "rejected": "Analyze root cause, plan and implement corrective actions, verify effectiveness, document evidence, and submit to the certification body before the deadline."
    },
    {
        "category": "audit",
        "prompt": "How often should I conduct internal halal audits?",
        "chosen": """**Internal halal audit frequency:**

**Minimum requirements:**

| Standard | Minimum Frequency |
|----------|------------------|
| JAKIM | Annual |
| MUI (HAS 23000) | Annual |
| Most certification bodies | Annual |
| Best practice | Semi-annual or more |

**Risk-based frequency approach:**

LOW RISK (Annual):
- Stable processes
- No recent non-conformances
- Experienced staff
- Simple product range
- Good audit history

MEDIUM RISK (Semi-annual):
- Some process changes
- Minor non-conformances
- New staff joining
- Moderate product complexity
- Some audit findings

HIGH RISK (Quarterly):
- Frequent changes
- Major non-conformances
- High staff turnover
- Complex products
- Shared facilities
- Critical audit findings

**Factors affecting frequency:**

| Factor | Higher Frequency If |
|--------|---------------------|
| Product complexity | Many ingredients, complex processes |
| Risk level | Animal-derived ingredients, shared facilities |
| Change rate | Frequent new products, suppliers, staff |
| Previous issues | Non-conformances found |
| Staff turnover | High turnover, new training needs |
| Regulatory/customer | Additional requirements |
| External audit schedule | Pre-external audit preparation |

**Annual audit program:**

Q1: Full system audit
- Policy and documentation
- Supplier management
- Ingredient control
- Training

Q2: Process-focused audit
- Production controls
- Cleaning validation
- Traceability exercise
- Follow-up on Q1 findings

Q3: Pre-external audit
- Full scope (prepare for external)
- Mock traceability
- Staff interview practice
- Document review

Q4: Compliance verification
- Corrective action closure
- Supplier certificate status
- Training completion
- Annual review

**Trigger-based additional audits:**

| Trigger | Action |
|---------|--------|
| Major non-conformance | Immediate focused audit |
| Customer complaint | Investigation audit |
| Supplier issue | Ingredient control audit |
| Process change | Changed area audit |
| New product launch | Product-specific audit |
| Pre-certification | Readiness audit |

**Audit schedule template:**

INTERNAL HALAL AUDIT SCHEDULE - YEAR ____
| Month | Audit Scope | Lead Auditor | Status |
|-------|-------------|--------------|--------|
| January | Supplier mgmt | QA Manager | |
| February | Production Line A | Halal Exec | |
| March | Production Line B | QA Manager | |
| April | Traceability | Halal Exec | |
| May | Storage/warehouse | QA Supervisor | |
| June | Training/docs | HR + Halal Exec | |
| July | Full system | Halal Exec | |
| August | Corrective actions | QA Manager | |
| September | Pre-external | External (opt) | |
| October | [External audit] | Certifier | |
| November | Follow-up | Halal Exec | |
| December | Annual review | Committee | |

**Resource allocation:**

| Audit Type | Duration | Resources |
|------------|----------|-----------|
| Full system | 2-3 days | Lead + support |
| Focused area | 0.5-1 day | Lead auditor |
| Follow-up | 0.5 day | Lead auditor |
| Traceability exercise | 0.5 day | Lead + records support |

**Management review integration:**
Internal audit results should feed into:
- Quarterly management review
- Annual halal system review
- Certification body reporting
- Continuous improvement initiatives""",
        "rejected": "Conduct internal audits at least annually, with semi-annual or quarterly audits for higher-risk operations. Schedule additional audits before external certification audits."
    },
    {
        "category": "audit",
        "prompt": "What qualifications should internal halal auditors have?",
        "chosen": """**Internal halal auditor competency requirements:**

**Minimum qualifications:**

| Requirement | Description |
|-------------|-------------|
| Halal knowledge | Understanding of halal principles |
| Audit training | Internal audit techniques |
| Industry knowledge | Relevant to products/processes |
| Independence | Not auditing own work |
| Language | Can communicate with auditees |

**Competency framework:**

Halal knowledge (basic):
- Halal and haram concepts
- Basic fiqh of food
- Company halal policy
- Certification requirements

Halal knowledge (advanced):
- Ingredient evaluation
- Slaughter requirements
- Cross-contamination risks
- Certification body standards

Audit skills (basic):
- Audit principles
- Checklist use
- Evidence gathering
- Basic interviewing
- Report writing

Audit skills (advanced):
- Audit planning
- Non-conformance classification
- Root cause analysis
- Effective questioning
- Conflict management

Technical knowledge:
- Production: Relevant manufacturing processes
- Quality: Quality management systems
- Food safety: HACCP, food safety basics
- Documentation: Document control, records

Personal attributes:
- Ethical (honest, fair)
- Observant (attention to detail)
- Objective (evidence-based)
- Systematic (organized approach)
- Persistent (thorough)

**Training requirements:**

| Training | Provider | Duration |
|----------|----------|----------|
| Halal awareness | Internal or external | 1 day |
| Halal auditor | Certification body or accredited | 2-3 days |
| Internal audit (general) | ISO or industry body | 2 days |
| HAS implementation | Certification body | 1-2 days |

**Certification body requirements:**

| Body | Auditor Requirement |
|------|---------------------|
| JAKIM | Internal Halal Executive training |
| MUI | HAS auditor training (accredited) |
| IFANCA | Halal auditor certification |
| General | Equivalent competency demonstration |

**Training content:**

MODULE 1: Halal Fundamentals
- Islamic principles of halal
- Halal and haram categories
- Fiqh of food
- Certification standards

MODULE 2: Halal Assurance System
- HAS components
- Ingredient control
- Production control
- Documentation requirements
- Traceability

MODULE 3: Audit Principles
- Audit planning
- Conducting audits
- Evidence and sampling
- Non-conformance classification
- Reporting

MODULE 4: Practical Skills
- Interview techniques
- Observation skills
- Document review
- Traceability testing
- Case studies

MODULE 5: Assessment
- Written exam
- Practical exercise
- Competency evaluation

**Independence requirements:**
- Cannot audit own work
- Cannot audit own department (ideally)
- No conflict of interest
- Objective even with colleagues
- Can escalate findings to management
- Protected from retaliation

**Qualification record:**

INTERNAL HALAL AUDITOR QUALIFICATION RECORD
Name: _____
Employee ID: _____
Department: _____

TRAINING COMPLETED:
| Training | Date | Provider | Cert # |
|----------|------|----------|--------|
| Halal Awareness | | | |
| Internal Audit | | | |
| Halal Auditor | | | |
| HAS Implementation | | | |

EXPERIENCE:
- Audits as observer: ___
- Audits as co-auditor: ___
- Audits as lead: ___
- Total audits: ___

COMPETENCY ASSESSMENT:
- Halal knowledge verified
- Audit skills demonstrated
- Technical knowledge adequate
- Personal attributes suitable

QUALIFICATION:
Qualified as Internal Halal Auditor
Qualified by: _____ Date: _____
Valid until: _____ (annual reassessment)

**Maintaining competency:**

| Activity | Frequency |
|----------|-----------|
| Conduct audits | Minimum 1-2 per year |
| Refresher training | As needed |
| Updates (standards changes) | As they occur |
| Competency review | Annual |
| Feedback review | After each audit |

**Auditor pool:**
For reliability, maintain:
- Minimum 2 qualified auditors
- Cross-trained in different areas
- Can cover absences
- Fresh perspectives from different departments""",
        "rejected": "Internal halal auditors need halal training, audit skills training, industry knowledge, and independence from the areas they audit. Maintain records of qualifications."
    },
    {
        "category": "audit",
        "prompt": "How do I prepare for an unannounced halal audit?",
        "chosen": """**Unannounced halal audit preparedness:**

**Purpose of unannounced audits:**
- Verify day-to-day compliance (not just audit-day performance)
- Check consistency of practices
- Identify real operational issues
- Maintain certification integrity

**Key principle:** If you're always compliant, unannounced audits are no different from announced ones.

**Daily readiness checklist:**

Documentation (always current):
- Halal policy posted and accessible
- SOPs at point of use
- Supplier certificates organized
- Recent batch records complete
- Training records up to date
- Internal audit reports available

Facility (always compliant):
- Segregation maintained
- Signage clear and visible
- Equipment properly labeled
- Storage areas organized
- No non-halal in halal zones

Personnel (always prepared):
- Staff trained and aware
- Can answer basic halal questions
- Know who to contact for Halal Committee
- Understand their halal responsibilities

Records (always accessible):
- Recent production records at hand
- Receiving logs current
- Cleaning records complete
- Traceability data retrievable

**Immediate response when auditor arrives:**

1. Greet professionally
2. Verify auditor credentials (ID, authorization letter)
3. Contact Halal Committee Chair/Executive
4. Provide safety briefing
5. Offer escort and cooperation

**Do NOT:**
- Panic or appear flustered
- Delay or obstruct
- Hide or alter records
- Coach staff on answers
- Make excuses

**Common unannounced audit findings:**

| Finding | Prevention |
|---------|------------|
| Records not up to date | Real-time documentation |
| Staff unaware of procedures | Regular training |
| Segregation breakdown | Daily walkthrough |
| Expired certificates on file | Automated tracking |
| Non-compliance with SOPs | Supervision, audits |

**Building a culture of readiness:**

Management commitment:
- Regular halal walkthrough by management
- Resources for compliance
- Recognition for good practices

Systems and processes:
- Automated certificate tracking
- Real-time record keeping
- Digital documentation
- Regular self-inspections

Staff engagement:
- Ongoing training (not just annual)
- Halal awareness in daily huddles
- Empowerment to report issues
- No blame culture for raising concerns

Continuous monitoring:
- Daily checklists
- Weekly supervisor verification
- Monthly internal inspections
- Quarterly mini-audits

**Self-assessment frequency:**

| Activity | Frequency |
|----------|-----------|
| Personal workspace check | Daily |
| Department walkthrough | Weekly |
| Documentation review | Monthly |
| Mock unannounced audit | Quarterly |

**Mock unannounced audit:**

Process:
1. Halal Committee member conducts surprise visit
2. Full audit protocol followed
3. Findings documented
4. Corrective actions assigned
5. Results reviewed in committee meeting

Benefits:
- Identifies gaps before real audit
- Trains staff on audit process
- Builds confidence
- Improves systems""",
        "rejected": "Maintain daily compliance so unannounced audits are no different from announced ones. Keep records current, facilities compliant, and staff trained at all times."
    },
    {
        "category": "audit",
        "prompt": "What are the differences between halal certification body audits?",
        "chosen": """**Halal certification body audit comparison:**

**Major certification bodies:**

| Body | Region | Audit Style |
|------|--------|-------------|
| JAKIM | Malaysia | Rigorous, document-heavy |
| MUI-LPPOM | Indonesia | HAS-focused, systematic |
| ESMA | UAE/Gulf | Gulf standards, practical |
| IFANCA | USA | Food safety integrated |
| HFA | UK | Meat-focused, detailed |
| MUIS | Singapore | Efficient, technology-enabled |

**Audit approach differences:**

JAKIM (Malaysia):
- Online system (MyeHalal) submission required
- Detailed document review before visit
- Focus on sertu compliance (ritual cleansing)
- Strict on alcohol (zero tolerance)
- Emphasis on committee structure
- Duration: 1-2 days typical

MUI-LPPOM (Indonesia):
- HAS 23000 system required
- Strong focus on internal halal team
- Detailed material/ingredient matrix
- Emphasis on written procedures
- Regular training verification
- Duration: 1-3 days

ESMA (UAE):
- GSO standards compliance
- Practical facility focus
- Supplier certificate verification
- Traceability testing
- Market surveillance possible
- Duration: 1-2 days

IFANCA (USA):
- Integration with food safety (GFSI)
- Practical, hands-on approach
- Strong on ingredient verification
- Consumer complaint follow-up
- Annual unannounced visits possible
- Duration: 0.5-2 days

**Documentation expectations:**

| Document | JAKIM | MUI | ESMA | IFANCA |
|----------|-------|-----|------|--------|
| Halal manual | Required | Required (HAS) | Required | Required |
| Policy | Signed, posted | Signed | Posted | On file |
| SOPs | Detailed | Comprehensive | Essential | Practical |
| Training records | Detailed | Mandatory | Required | Required |
| Committee minutes | Quarterly | Regular | Periodic | As needed |
| Internal audit | Annual | Scheduled | Annual | Annual |

**Slaughter audit specifics (meat):**

| Aspect | Stricter Bodies | More Flexible |
|--------|-----------------|---------------|
| Stunning | JAKIM: Generally prohibited | Some bodies: Recoverable permitted |
| Slaughterman | Must be Muslim, verified | Must be Muslim |
| Supervision | Continuous | Periodic |
| Volume | Each animal blessed | Batch blessing (some) |
| Documentation | Detailed per batch | Summary records |

**Common focus areas by body:**

JAKIM priorities:
1. Sertu (ritual cleansing) compliance
2. Alcohol in ingredients
3. Committee structure
4. Supplier certificates

MUI priorities:
1. HAS implementation
2. Internal halal team competence
3. Material verification
4. Written procedures

Gulf bodies priorities:
1. GSO standards compliance
2. Labeling requirements
3. Traceability
4. Supplier approval

**Preparing for different bodies:**

| If Certified By | Focus Preparation On |
|-----------------|---------------------|
| JAKIM | Document completeness, sertu records |
| MUI | HAS manual, training records |
| Gulf | GSO compliance, labeling |
| Western bodies | Practical compliance, traceability |

**Multi-certification considerations:**

If certified by multiple bodies:
- Align to strictest requirements
- Maintain separate documentation if standards conflict
- Coordinate audit schedules
- Understand each body's specific focus
- Budget for multiple audit fees""",
        "rejected": "JAKIM focuses on documentation and sertu compliance. MUI emphasizes HAS implementation. Gulf bodies follow GSO standards. Western bodies are more practical and food-safety integrated."
    },
    {
        "category": "audit",
        "prompt": "How do I use audit findings for continuous improvement?",
        "chosen": """**Using audit findings for continuous improvement:**

**Types of audit findings:**

| Type | Definition | Improvement Opportunity |
|------|------------|------------------------|
| Critical | Halal integrity compromised | System redesign needed |
| Major | Significant gap in compliance | Process improvement |
| Minor | Documentation or minor process gap | Procedure update |
| Observation | Improvement suggestion | Enhancement opportunity |
| Good practice | Exceeds requirements | Share and standardize |

**From finding to improvement:**

Step 1: Categorize findings
- Group by area (ingredients, production, documentation)
- Identify patterns
- Prioritize by risk and frequency

Step 2: Root cause analysis
- For each finding, ask "why" 5 times
- Identify systemic causes
- Distinguish symptoms from root causes

Step 3: Develop improvement actions
- Address root cause, not just symptom
- Define measurable objectives
- Assign ownership and timeline

Step 4: Implement changes
- Update procedures
- Train staff
- Modify systems/facilities
- Communicate changes

Step 5: Verify effectiveness
- Monitor implementation
- Measure results
- Adjust if needed

Step 6: Standardize
- Update documentation
- Train all affected staff
- Include in ongoing monitoring

**Trend analysis:**

Track over time:
- Number of findings by category
- Recurring issues
- Areas of improvement
- Areas of concern

Trending indicators:
- Same finding repeated = systemic issue
- New findings in area = process change impact
- Decreasing findings = improvement working
- Increasing findings = deterioration

**Reporting format:**

HALAL AUDIT FINDINGS TREND REPORT
Period: _____

| Category | Last Audit | Current | Trend |
|----------|------------|---------|-------|
| Ingredients | 2 Major | 1 Minor | Improving |
| Production | 1 Minor | 0 | Resolved |
| Documentation | 3 Minor | 2 Minor | Improving |
| Training | 0 | 1 Minor | Watch |

Recurring issues:
- Issue A: 3rd occurrence - Escalate to management
- Issue B: Resolved after 2nd occurrence

Improvement initiatives:
- Digital certificate tracking (addresses 60% of findings)
- Enhanced training program (addresses 25%)

**Management review inputs:**

From audit findings, report:
- Summary of findings by severity
- Trend analysis
- Root cause categories
- Corrective action status
- Resource needs
- Recommendations

**PDCA cycle for improvement:**

PLAN:
- Review findings
- Analyze root causes
- Define improvement objectives
- Develop action plan

DO:
- Implement changes
- Train staff
- Document procedures
- Pilot test

CHECK:
- Verify implementation
- Measure effectiveness
- Internal audit follow-up
- Staff feedback

ACT:
- Standardize successful changes
- Address remaining gaps
- Update documentation
- Share best practices

**Key performance indicators:**

| KPI | Target | Tracking |
|-----|--------|----------|
| Critical findings | Zero | Per audit |
| Major findings | <2 | Per audit |
| Repeat findings | Zero | Trend analysis |
| Corrective action closure | <30 days | Monthly |
| Training completion | 100% | Quarterly |

**Building improvement culture:**

- Celebrate audit success
- Share learnings across departments
- Recognize improvement initiatives
- No blame for identifying issues
- Management commitment visible
- Resources allocated for improvement""",
        "rejected": "Analyze findings for patterns, identify root causes, implement corrective actions, track trends over time, and report to management for continuous improvement."
    },
]


async def submit_preferences():
    """Submit all preferences to the API."""
    async with httpx.AsyncClient(timeout=60) as client:
        results = {"success": 0, "failed": 0, "errors": []}
        
        for i, pref in enumerate(HALAL_PREFERENCES):
            try:
                response = await client.post(
                    f"{API_BASE}/api/preferences",
                    headers={"X-API-Key": API_KEY},
                    json={
                        "domain": "halal",
                        "category": pref["category"],
                        "prompt": pref["prompt"],
                        "response_a": pref["chosen"],
                        "response_b": pref["rejected"],
                        "preference": "A",
                        "annotator_id": "synthetic_seed",
                        "dimension_scores": {
                            "accuracy": 5,
                            "safety": 5,
                            "actionability": 5,
                            "clarity": 5
                        },
                        "difficulty": "medium",
                        "notes": f"Synthetic preference {i+1}/{len(HALAL_PREFERENCES)} - seed_halal_50_v1",
                        "response_a_model": "claude-expert",
                        "response_b_model": "baseline"
                    }
                )
                
                if response.status_code == 200:
                    results["success"] += 1
                    print(f"[OK] [{i+1}/51] {pref['category']}: {pref['prompt'][:50]}...")
                else:
                    results["failed"] += 1
                    results["errors"].append({
                        "index": i,
                        "status": response.status_code,
                        "response": response.text
                    })
                    print(f"[FAIL] [{i+1}/51] Status {response.status_code}: {response.text[:100]}")
                    
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"index": i, "error": str(e)})
                print(f"[ERR] [{i+1}/51] Error: {e}")
            
            # Rate limiting
            await asyncio.sleep(0.1)
        
        return results


if __name__ == "__main__":
    print(f"Submitting {len(HALAL_PREFERENCES)} halal preferences to {API_BASE}")
    print("=" * 60)
    
    results = asyncio.run(submit_preferences())
    
    print("=" * 60)
    print(f"Results: {results['success']} success, {results['failed']} failed")
    
    if results["errors"]:
        print("\nErrors:")
        for err in results["errors"][:5]:
            print(f"  - Index {err.get('index')}: {err}")

