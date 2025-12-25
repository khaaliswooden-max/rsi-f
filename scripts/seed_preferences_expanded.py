"""
Expanded Seed Preferences - Additional Domain-Specific Preferences
===================================================================
Extension to seed_preferences.py with ~30 more preferences per priority domain.
Total target: ~40 seeds per priority domain.
"""

# Additional procurement preferences (30 more)
PROCUREMENT_SEEDS_EXPANDED = [
    # FAR/DFARS (10 more)
    {
        "category": "far_dfars",
        "prompt": "What is the difference between FAR Part 12 and FAR Part 15 acquisitions?",
        "response_a": """**FAR Part 12 vs Part 15 - Key Distinctions:**

| Aspect | FAR Part 12 (Commercial) | FAR Part 15 (Negotiated) |
|--------|--------------------------|--------------------------|
| **Use Case** | Commercial items/services | Complex, non-commercial |
| **Procedures** | Simplified | Full competitive |
| **Proposal Complexity** | Streamlined | Detailed (Vol I-IV typical) |
| **Cost Data** | Rarely required | Often required (certified) |
| **Clauses** | FAR 52.212-x series | FAR 52.215-x + others |
| **Source Selection** | LPTA common | Best Value/Tradeoff |

**When to Use Part 12:**
- Product/service is commercially available
- Customization < 25% of value
- FAR 2.101 "commercial item" definition met

**When to Use Part 15:**
- Unique government requirements
- R&D or complex services
- Cost-reimbursement anticipated
- Detailed technical evaluation needed

**Hybrid Approach:**
Some acquisitions use "Commercial Procedures" but incorporate Part 15 evaluation criteria. Check Section L carefully.

**Pro tip:** Part 12 proposals are usually shorter but require demonstrating commercial market pricing.""",
        "response_b": "Part 12 is for commercial items and is simpler. Part 15 is for negotiated procurements and is more complex with detailed proposals.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "compliance": 5, "actionability": 4, "clarity": 5}
    },
    {
        "category": "far_dfars",
        "prompt": "Explain TINA (Truth in Negotiations Act) and when certified cost or pricing data is required.",
        "response_a": """**TINA / Truth in Negotiations Act (41 USC 3501):**

**Purpose:** Requires contractors to submit accurate, complete, and current cost/pricing data for negotiated contracts above threshold.

**Current Threshold (2024):** $2,000,000

**When Required:**
1. Negotiated procurement > $2M
2. Contract modifications > $2M
3. Subcontracts > $2M (flowdown)

**Exceptions (FAR 15.403-1):**
- ✓ Adequate price competition
- ✓ Prices set by law/regulation
- ✓ Commercial items
- ✓ Waiver granted by HCA

**What Constitutes "Cost or Pricing Data":**
- Direct labor rates and hours
- Material costs and quotes
- Indirect rates (fringe, OH, G&A)
- Make-or-buy decisions
- Vendor quotes
- Learning curve projections

**Certificate of Current Cost or Pricing Data:**
Must certify data is accurate, complete, and current as of agreement date.

**Defective Pricing Consequences:**
- Price reduction clause (FAR 52.215-10/11)
- Government can audit 3 years post-final payment
- Potential False Claims Act liability
- Interest on overcharges

**Best Practice:** Maintain contemporaneous documentation of all estimates.""",
        "response_b": "TINA requires you to submit cost data for contracts over $2M. If your data is wrong, the government can reduce the price.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "compliance": 5, "actionability": 4, "clarity": 5}
    },
    {
        "category": "far_dfars",
        "prompt": "What are the key DFARS cybersecurity requirements contractors must meet?",
        "response_a": """**DFARS Cybersecurity Requirements Overview:**

**1. DFARS 252.204-7012 (Safeguarding CDI)**
- Applies to ALL DoD contracts with Covered Defense Information
- Requires NIST SP 800-171 compliance (110 controls)
- 72-hour incident reporting to DoD
- Flowdown to subcontractors with CDI

**2. CMMC 2.0 (Cybersecurity Maturity Model)**
| Level | Requirements | Assessment |
|-------|--------------|------------|
| Level 1 | 17 FCI practices | Self-assessment |
| Level 2 | 110 CUI practices (800-171) | Self or C3PAO |
| Level 3 | 110+ advanced (800-172) | DIBCAC |

**Timeline:**
- CMMC rule finalized late 2024
- Phased rollout in contracts 2025+

**3. Key Compliance Steps:**
1. Identify CUI/CDI in your environment
2. Complete NIST 800-171 self-assessment
3. Submit score to SPRS (Supplier Performance Risk System)
4. Create POA&M for gaps
5. Prepare for CMMC certification

**4. SPRS Score Requirement:**
- Must have current score in SPRS to bid
- Score range: -203 to 110
- Industry average: ~70

**5. Key Controls Often Missed:**
- Multi-factor authentication
- Encryption at rest and in transit
- Security awareness training
- Incident response plan
- Access control procedures

**Resources:** NIST 800-171 Assessment Guide, DIB Cybersecurity Program""",
        "response_b": "You need to follow NIST 800-171 and get CMMC certified. Report any cyber incidents within 72 hours.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "compliance": 5, "actionability": 5, "clarity": 5}
    },
    {
        "category": "far_dfars",
        "prompt": "What is the Service Contract Act and when does it apply?",
        "response_a": """**Service Contract Act (SCA) - 41 USC 6701:**

**Purpose:** Establishes minimum wages and benefits for workers on federal service contracts.

**Applicability:**
- Service contracts > $2,500
- Principal purpose is furnishing services
- Through use of service employees
- In the United States

**Key Requirements:**

**1. Wage Determinations:**
- DOL issues area-specific wage determinations (WD)
- Minimum hourly rates by labor category
- Check SAM.gov for applicable WD
- WD incorporated into contract

**2. Health & Welfare (H&W):**
- Currently ~$4.98/hour (2024)
- Cash equivalent or bona fide fringe benefits
- Includes health insurance, vacation, holidays

**3. Covered Employees:**
- Service employees (non-exempt)
- NOT exempt professionals, admin, executive
- NOT construction workers (Davis-Bacon instead)

**Compliance Obligations:**
```
□ Pay at least WD rates
□ Provide H&W fringe or cash
□ Post WD at worksite
□ Maintain payroll records
□ Include in subcontracts
```

**Price Escalation:**
- FAR 52.222-43 allows price adjustment for WD changes
- Submit request with documentation
- New WD incorporated via modification

**Penalties:** Back wages, contract termination, debarment

**Pro tip:** Always verify WD revision number matches contract.""",
        "response_b": "SCA sets minimum wages for service contracts over $2,500. Check the wage determination for your area and job categories.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "compliance": 5, "actionability": 4, "clarity": 5}
    },
    {
        "category": "far_dfars",
        "prompt": "How do I calculate indirect rates for a government cost proposal?",
        "response_a": """**Indirect Rate Calculation for Cost Proposals:**

**Rate Structure (Typical):**
```
Direct Labor
    + Fringe Benefits (% of DL)
    = Loaded Labor
    + Overhead (% of DL or Loaded Labor)
    = Total Direct Labor Cost
    + G&A (% of Total Cost Input)
    = Total Cost
    + Fee/Profit
    = Total Price
```

**Step-by-Step Calculation:**

**1. Fringe Rate**
```
Fringe Pool ÷ Direct Labor Base = Fringe Rate

Example:
$500K fringe ÷ $2M direct labor = 25%
```
Pool includes: FICA, FUTA, health, 401k, PTO

**2. Overhead Rate**
```
Overhead Pool ÷ Allocation Base = OH Rate

Example:
$1.2M overhead ÷ $2M DL base = 60%
```
Pool includes: Indirect labor, facilities, IT, supplies

**3. G&A Rate**
```
G&A Pool ÷ Total Cost Input = G&A Rate

Example:
$800K G&A ÷ $8M TCI = 10%
```
Pool includes: Executive, accounting, BD, legal, corporate

**Example Calculation:**
| Element | Rate | Amount |
|---------|------|--------|
| Direct Labor | - | $100,000 |
| Fringe (25%) | 25% | $25,000 |
| Overhead (60%) | 60% | $60,000 |
| Subtotal | - | $185,000 |
| G&A (10%) | 10% | $18,500 |
| **Total Cost** | - | **$203,500** |
| Fee (8%) | 8% | $16,280 |
| **Total Price** | - | **$219,780** |

**For DCAA Compliance:**
- Use actual (historical) or budgeted rates
- Be prepared to support with accounting records
- Ensure rate structure matches disclosure statement""",
        "response_b": "Add fringe, overhead, and G&A percentages to your direct labor costs. Multiply each in order to get total cost.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "compliance": 5, "actionability": 5, "clarity": 5}
    },
    # RFP Analysis (10 more)
    {
        "category": "rfp_analysis",
        "prompt": "How do I respond to a Sources Sought notice?",
        "response_a": """**Responding to Sources Sought / RFI:**

**Purpose of Sources Sought:**
- Market research (not a solicitation)
- Determine if small business set-aside viable
- Identify potential sources
- Refine requirements

**What to Include in Response:**

**1. Capability Statement (1-2 pages)**
```
Company Overview:
□ Legal name, DUNS, CAGE, UEI
□ Business size (NAICS, employee count, revenue)
□ Socioeconomic status (SB, WOSB, SDVOSB, HUBZone, 8(a))
□ Years in business
```

**2. Relevant Experience**
- 3-5 similar contracts
- Client, value, period of performance
- Scope alignment to SS requirements
- Performance outcomes/metrics

**3. Technical Capability**
- Direct response to capability questions
- Key personnel qualifications
- Facilities/equipment
- Certifications (ISO, CMMI, clearances)

**4. Teaming (if applicable)**
- Identify potential partners
- Roles and responsibilities
- Combined capabilities

**5. Questions/Feedback**
- Clarifying questions on requirements
- Suggestions for PWS improvement
- Concerns about feasibility

**Format Tips:**
- Follow any page limits strictly
- Use headers matching SS questions
- Include NAICS code capability
- Submit by deadline (no extensions)

**Strategic Value:**
- Shapes final solicitation
- Establishes credibility
- May influence set-aside decision
- No bid obligation

**Don't:** Submit generic capability statements—tailor to specific opportunity.""",
        "response_b": "Send a capability statement with your company info, relevant experience, and answers to their questions. It's market research, not a bid.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "compliance": 4, "actionability": 5, "clarity": 5}
    },
    {
        "category": "rfp_analysis",
        "prompt": "What's the difference between LPTA and Best Value Tradeoff source selection?",
        "response_a": """**LPTA vs Best Value Tradeoff:**

**LPTA (Lowest Price Technically Acceptable)**

| Characteristic | Detail |
|----------------|--------|
| Technical Evaluation | Pass/Fail only |
| Price Role | Sole discriminator |
| Winner | Lowest compliant price |
| Best for | Commodity, well-defined |

**Strategy for LPTA:**
- Meet minimums exactly
- No gold-plating
- Price aggressively
- Focus on compliance proof

---

**Best Value Tradeoff**

| Characteristic | Detail |
|----------------|--------|
| Technical Evaluation | Scored/rated |
| Price Role | Weighed against technical |
| Winner | Best value (may not be lowest) |
| Best for | Complex, quality-sensitive |

**Strategy for Tradeoff:**
- Emphasize discriminators
- Demonstrate added value
- Price reflects quality investment
- Align to evaluation criteria weights

---

**How to Identify (in RFP):**

**LPTA Indicators:**
- "Technically acceptable" language
- Section M shows Pass/Fail criteria
- "Award to lowest priced acceptable offeror"
- No technical scoring rubric

**Tradeoff Indicators:**
- Adjectival ratings (Outstanding/Good/Acceptable)
- Point scoring system
- "Technical is more important than price"
- "May award to other than lowest price"

**Hybrid Approaches:**
Some RFPs use LPTA for some factors, tradeoff for others. Read Section M carefully.

**Key Decision Matrix:**
```
If commodity/clear specs → Expect LPTA → Price to win
If complex/quality matters → Expect Tradeoff → Invest in technical
```""",
        "response_b": "LPTA means lowest price wins if you're acceptable. Best Value means they weigh technical against price and might pick someone more expensive if they're better.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "compliance": 4, "actionability": 5, "clarity": 5}
    },
    {
        "category": "rfp_analysis",
        "prompt": "How do I analyze an RFP's evaluation criteria to prioritize proposal effort?",
        "response_a": """**RFP Evaluation Analysis Framework:**

**Step 1: Map Section M Factors**
```
Factor 1: Technical Approach     [40%] → HIGH PRIORITY
Factor 2: Management Approach    [25%] → MEDIUM
Factor 3: Past Performance       [20%] → MEDIUM  
Factor 4: Price                  [15%] → MODERATE
```

**Step 2: Decode Relative Importance Language**

| RFP Language | Implied Weight |
|--------------|----------------|
| "Significantly more important" | ~60-70% vs rest |
| "More important" | ~55-60% vs rest |
| "Approximately equal" | Equal split |
| "When combined, equal to price" | Tech factors = 50% |

**Step 3: Sub-factor Deep Dive**

For each factor, identify:
1. Sub-factor weights (if stated)
2. Evaluation standards
3. Strengths/weaknesses criteria
4. "Go/No-Go" requirements

**Step 4: Section L Cross-Reference**

| Section M Says | Section L Requires | Effort Level |
|----------------|-------------------|--------------|
| Technical Approach (40%) | 25 pages | HIGH |
| Past Performance (20%) | 5 refs | MEDIUM |
| Price (15%) | Cost workbook | MODERATE |

**Page limit ratio often signals importance.**

**Step 5: Effort Allocation Matrix**

```
Technical Approach (40%):
  - SME time: 60 hours
  - Writer time: 40 hours
  - Review cycles: 4
  
Management (25%):
  - SME time: 30 hours
  - Writer time: 25 hours
  - Review cycles: 3
```

**Step 6: Discriminator Identification**

Ask: "Where can we demonstrate unique value?"
- Features competitors can't match
- Past performance differentiators
- Key personnel with clearances
- Proprietary tools/methods

**Output:** Proposal Investment Plan with justified effort allocation.""",
        "response_b": "Look at the weights in Section M and spend more time on the higher-weighted factors. Match your effort to the importance.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "compliance": 4, "actionability": 5, "clarity": 5}
    },
    {
        "category": "rfp_analysis",
        "prompt": "What questions should I ask during an RFP Q&A period?",
        "response_a": """**Strategic RFP Q&A Questions:**

**Categories of Effective Questions:**

**1. Clarification Questions** (Safe, Always Ask)
```
"Section L.4.2 requires 'relevant experience.' Please define 
'relevant' - does it require exact scope match or similar 
complexity/domain?"

"The PWS references 'current tools.' Is there an incumbent? 
What tools are currently in use?"
```

**2. Requirement Feasibility**
```
"Task 3 specifies 48-hour turnaround. Is this calendar or 
business hours? Are weekends/holidays excluded?"

"The security requirement references 'TS/SCI with poly.' 
What percentage of staff require this level?"
```

**3. Evaluation Process**
```
"Will oral presentations be conducted? If so, what is the 
anticipated format and duration?"

"Are sample tasks anticipated as part of evaluation?"
```

**4. Scope Boundaries**
```
"Section C mentions 'other duties as assigned.' Please 
provide examples of anticipated additional tasks."

"Is travel reimbursed separately or included in FFP?"
```

**5. Incumbent/Transition**
```
"What is the anticipated transition period?"
"Will incumbent personnel information be provided?"
```

**Questions to AVOID:**
- ❌ Fishing for competitor info
- ❌ Questions that reveal your strategy
- ❌ Overly broad ("Please explain the PWS")
- ❌ Questions already answered in RFP
- ❌ Questions that challenge requirements

**Submission Best Practices:**
1. Reference specific section/page numbers
2. One question per submission (easier to track)
3. Submit early (avoid rush amendments)
4. Review all Q&A responses (applies to everyone)

**Pro tip:** Unanswered questions often indicate requirement will be removed or modified via amendment.""",
        "response_b": "Ask about unclear requirements, evaluation criteria, and what the incumbent is doing. Don't ask questions that reveal your approach.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "compliance": 4, "actionability": 5, "clarity": 5}
    },
    {
        "category": "rfp_analysis",
        "prompt": "How do I determine if an RFP is wired for the incumbent?",
        "response_a": """**Incumbent Advantage Analysis:**

**Red Flags (Potential Incumbent Bias):**

**1. Overly Specific Requirements**
```
⚠️ "Must have 5+ years supporting THIS specific system"
⚠️ "Experience with Agency X's proprietary tools"
⚠️ Exact staff count matching current contract
⚠️ Certification only incumbent has
```

**2. Timeline Compression**
```
⚠️ Unreasonably short proposal period (< 30 days for complex)
⚠️ Rapid transition (< 30 days)
⚠️ No Q&A period or very short
```

**3. Evaluation Structure**
```
⚠️ Past Performance weighted very heavily
⚠️ "Relevant to this agency" required
⚠️ LPTA with high technical bar
⚠️ Oral presentations at incumbent location
```

**4. Scope Characteristics**
```
⚠️ Very narrow NAICS code
⚠️ Requirements mirror current contract exactly
⚠️ Organizational Conflict of Interest favoring incumbent
```

**Counter-Strategy If Proceeding:**

**1. Teaming**
- Partner with incumbent if possible
- Hire former incumbent employees (check non-competes)
- Team with agency's other contractors

**2. Differentiation**
- Price significantly lower (if LPTA)
- Propose innovation/improvements
- Highlight incumbent weaknesses (carefully)

**3. Challenge (If Warranted)**
- File agency-level protest pre-award
- GAO protest if specifications unduly restrictive
- Request sources sought for more competition

**4. Bid/No-Bid Decision Matrix:**
| Factor | Score 1-5 |
|--------|-----------|
| Can meet specifications | ___ |
| Competitive pricing possible | ___ |
| Win probability > 20% | ___ |
| Strategic value | ___ |

**Score < 12 = Likely No-Bid**

**Remember:** Not all incumbent advantages are unfair—they earned experience. Focus on what you CAN offer.""",
        "response_b": "Look for requirements that only the incumbent can meet, short timelines, and heavy weighting on past performance with this agency. If it looks wired, consider not bidding.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "compliance": 4, "actionability": 5, "clarity": 5}
    },
    # Proposal Writing (10 more)
    {
        "category": "proposal_writing",
        "prompt": "How do I write a compliant executive summary for a government proposal?",
        "response_a": """**Executive Summary Blueprint:**

**Structure (1-2 pages typical):**

**1. Opening Hook (2-3 sentences)**
```
"[COMPANY] is uniquely qualified to deliver [PROGRAM NAME] 
to [AGENCY], bringing [X years] of proven performance on 
[similar programs] and a team with [key differentiator]."
```

**2. Understanding & Alignment (1 paragraph)**
- Demonstrate understanding of agency mission
- Reference strategic goals/pain points
- Show you've done homework

**3. Solution Overview (2-3 paragraphs)**
```
For each major evaluation factor:
→ Our approach to [Factor]...
→ Key features include...
→ This delivers [benefit to agency]...
```

**4. Discriminators (Bulleted)**
```
Why [COMPANY]:
• [Discriminator 1]: Quantified proof
• [Discriminator 2]: Quantified proof  
• [Discriminator 3]: Quantified proof
```

**5. Risk Mitigation (1 paragraph)**
- Acknowledge complexity
- Show proven risk mitigation
- Reference similar challenges overcome

**6. Closing (2-3 sentences)**
```
"[COMPANY] is committed to [AGENCY]'s mission success. 
We offer [low risk/best value/proven capability] and 
look forward to [partnership/continued service]."
```

**Compliance Checklist:**
```
□ Addresses all Section M factors
□ Includes required elements from Section L
□ Within page limit
□ Uses agency terminology
□ Contains no unsubstantiated claims
□ Features/benefits aligned
□ Themes/discriminators clear
```

**Style Tips:**
- Active voice ("We will deliver" not "Delivery will be made")
- Specific numbers > vague claims
- Agency-centric (their goals, not your capabilities)
- Assume reader reads ONLY this section""",
        "response_b": "Write a brief overview of your approach that covers all the evaluation factors. Include why you're the best choice and keep it under 2 pages.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "compliance": 5, "actionability": 5, "clarity": 5}
    },
    {
        "category": "proposal_writing",
        "prompt": "How do I handle a page-limited proposal when I have too much content?",
        "response_a": """**Page Limit Optimization Strategies:**

**1. Ruthless Prioritization**
```
Must Include (Non-negotiable):
✓ All "shall" requirements responses
✓ Evaluation criteria responses
✓ Compliance matrix items
✓ Key discriminators

Cut First:
✗ Generic company background
✗ Redundant explanations
✗ Methodology theory (vs application)
✗ Multiple examples when one suffices
```

**2. Content Compression Techniques**

**Tables vs Prose:**
```
BEFORE (50 words):
"Our team includes John Smith with 15 years experience, 
Jane Doe with 12 years experience, and Bob Johnson 
with 10 years experience in system administration..."

AFTER (Table - 15 words equivalent):
| Name | Role | Years | Certification |
|------|------|-------|---------------|
| J. Smith | Lead | 15 | PMP, CISSP |
```

**Bullets vs Paragraphs:**
```
BEFORE: The process involves first analyzing requirements,
then designing the solution, followed by implementation...

AFTER:
• Analyze requirements
• Design solution  
• Implement & test
```

**3. Visual Space Optimization**
- Reduce margins to minimum allowed (typically 1")
- Use 11pt font if 12pt not required
- Single space if not specified
- Remove extra line breaks between sections

**4. Strategic Graphics**
- One well-designed graphic > 200 words of description
- Process flows, org charts, schedules
- Ensure graphics are legible at print size

**5. Cross-Reference Strategy**
```
"Our risk management approach (detailed in Section 3.2) 
ensures..." [Don't repeat—reference]
```

**6. Final Compression Review**
- Read aloud: Cut anything that doesn't add value
- "So what?" test: Every sentence must answer this
- Eliminate weasel words: "very," "really," "significantly"

**Red Line Review:** Have someone unfamiliar read and flag anything confusing—usually cuttable.""",
        "response_b": "Use smaller fonts and margins, convert paragraphs to bullet points, and use tables. Cut generic content and focus on what's required.",
        "preference": "A",
        "dimension_scores": {"accuracy": 4, "compliance": 4, "actionability": 5, "clarity": 5}
    },
    {
        "category": "proposal_writing",
        "prompt": "What makes a strong technical approach section?",
        "response_a": """**Technical Approach Excellence Framework:**

**Structure:**
```
1. Understanding (10%)
   → Restate problem in your words
   → Show insight beyond PWS

2. Approach (60%)
   → Methodology
   → Tools & techniques
   → Innovation/differentiation

3. Implementation (20%)
   → How you'll execute
   → Schedule integration
   → Resource allocation

4. Outcomes (10%)
   → Deliverables
   → Success metrics
   → Value to agency
```

**Winning Elements:**

**1. Show Understanding Beyond the Obvious**
```
WEAK: "We understand the agency needs IT support."

STRONG: "The [Agency]'s IT environment faces three critical 
challenges: legacy system integration, zero-trust migration 
timeline pressure, and workforce hybrid support requirements. 
Our approach addresses each systematically."
```

**2. Feature → Benefit → Proof**
```
FEATURE: We use automated testing frameworks
BENEFIT: Reducing defect escape rate by 40%
PROOF: Achieved on [Contract X] with [Agency Y]

"Our automated regression testing [FEATURE] reduces defect 
escape rates by 40% [BENEFIT], as demonstrated on our NASA 
ACES contract where we decreased production defects from 
12/month to 4/month [PROOF]."
```

**3. Specificity Over Generality**
```
WEAK: "We have experienced staff."

STRONG: "Our proposed team includes 6 engineers averaging 
12 years experience, 4 holding active TS/SCI, all with 
AWS Solutions Architect and CISSP certifications."
```

**4. Address Evaluation Criteria Explicitly**
```
"Per Section M.2.1, Technical Understanding is evaluated 
on [criteria]. Our approach demonstrates this through..."
```

**5. Visual Clarity**
- Process flow diagrams
- Architecture diagrams
- Responsibility matrices (RACI)
- Schedule graphics

**6. Risk Acknowledgment**
- Identify technical risks proactively
- Show mitigation strategies
- Reference similar challenges overcome

**Evaluator Mindset:** They're looking for reasons to give you points. Make it easy.""",
        "response_b": "Explain your methodology, show you understand the problem, and prove you can do the work with specific examples from past projects.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "compliance": 4, "actionability": 5, "clarity": 5}
    },
    {
        "category": "pricing_strategy",
        "prompt": "How do I price a Time & Materials (T&M) contract?",
        "response_a": """**T&M Pricing Strategy:**

**Rate Components:**
```
Fully Burdened Rate = Direct Labor + Fringe + OH + G&A + Fee

Example for Senior Engineer:
Base Salary: $120,000/year ÷ 2080 hrs = $57.69/hr
+ Fringe (28%): $16.15
+ Overhead (65%): $37.50
+ G&A (12%): $13.36
= Total Cost: $124.70/hr
+ Fee (10%): $12.47
= Billed Rate: $137.17/hr
```

**Labor Category Development:**

**1. Market Research**
- GSA Schedule rates for similar
- SAM.gov awarded rates
- Agency historical data (if available)

**2. Rate Positioning**
| Strategy | When to Use |
|----------|-------------|
| At market | Competitive field, need credibility |
| Below market | LPTA, incumbent displacement |
| Above market | Unique quals, sole source |

**3. Rate Escalation**
- Plan 2-4% annual increases
- Build into multi-year pricing
- Align with WD increases if SCA

**Hours Estimation:**
```
Task Analysis:
1. Break PWS into WBS elements
2. Estimate hours per task
3. Apply labor mix
4. Add management/QA overhead (8-12%)
5. Include travel if applicable
```

**Ceiling Price:**
- T&M contracts have Not-to-Exceed (NTE)
- Price ceiling ≠ estimated value
- Build ~10-15% margin above estimate

**Common Mistakes:**
- ❌ Underestimating hours
- ❌ Forgetting indirect rate escalation
- ❌ Missing Other Direct Costs (ODCs)
- ❌ Inadequate fee relative to risk

**Profit Considerations:**
- Higher risk than FFP → justify higher fee
- Typical range: 8-12% for T&M
- May be negotiated down

**Compliance:** Ensure rate structure matches your accounting system disclosure.""",
        "response_b": "Calculate your fully loaded labor rates including fringe, overhead, G&A, and fee. Estimate hours for each task and multiply by rates.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "compliance": 5, "actionability": 5, "clarity": 5}
    },
    {
        "category": "pricing_strategy",
        "prompt": "What's the difference between FFP, CPFF, and CPAF contracts, and which should I prefer?",
        "response_a": """**Contract Type Comparison:**

| Type | Risk Bearer | Fee Structure | Best For |
|------|-------------|---------------|----------|
| FFP | Contractor | Fixed, in price | Well-defined scope |
| CPFF | Government | Fixed fee on cost | R&D, uncertainty |
| CPAF | Government | Award fee pool | Performance incentives |

**Firm Fixed Price (FFP):**
```
Characteristics:
• Price set at award, doesn't change
• Contractor absorbs cost overruns
• Contractor keeps cost underruns
• Minimal government oversight

Risk/Reward:
• High risk if scope unclear
• High reward if efficient

Best suited for:
✓ Commodity services
✓ Well-defined deliverables
✓ Mature processes
✓ Historical cost data available
```

**Cost Plus Fixed Fee (CPFF):**
```
Characteristics:
• Government reimburses allowable costs
• Fee fixed at award (% or $)
• Fee doesn't change with cost
• Extensive cost reporting required

Risk/Reward:
• Low contractor risk
• Limited profit potential
• DCAA audit exposure

Best suited for:
✓ R&D programs
✓ Undefined scope
✓ Level-of-effort work
✓ First-time requirements
```

**Cost Plus Award Fee (CPAF):**
```
Characteristics:
• Base fee (usually small, 0-3%)
• Award fee pool (up to 10%+)
• Fee earned based on performance
• Award Fee Board evaluations

Risk/Reward:
• Performance directly impacts profit
• Subjective evaluation risk
• Administrative burden

Best suited for:
✓ Complex programs
✓ Quality-critical work
✓ Long-term relationships
✓ Measurable outcomes
```

**Contractor Preference (Generally):**
```
1. FFP with clear scope (highest margin potential)
2. T&M (balanced risk/reward)
3. CPFF (guaranteed fee, low risk)
4. CPAF (fee uncertainty)
```

**Key Decision Factor:** How well can you estimate costs? High confidence → FFP. Low confidence → cost-reimbursement.""",
        "response_b": "FFP means fixed price and you take the risk. CPFF reimburses your costs plus a fixed fee, so the government takes risk. CPAF gives bonuses for good performance. FFP is best if you can estimate well.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "compliance": 5, "actionability": 4, "clarity": 5}
    },
]

# Additional defense_wm preferences (30 more)
DEFENSE_WM_SEEDS_EXPANDED = [
    {
        "category": "scene_reconstruction",
        "prompt": "How do I choose between photogrammetry and LiDAR for terrain mapping?",
        "response_a": """**Photogrammetry vs LiDAR Decision Matrix:**

| Factor | Photogrammetry | LiDAR |
|--------|----------------|-------|
| **Cost** | Low (camera) | High (sensor) |
| **Vegetation Penetration** | Poor | Excellent |
| **Accuracy** | 1-5 cm GSD | 1-10 cm absolute |
| **Point Density** | Very High | Medium-High |
| **Texture/Color** | Native | Requires fusion |
| **Weather Dependency** | High (lighting) | Low (active sensor) |
| **Processing Time** | High | Medium |

**Choose Photogrammetry When:**
- ✅ Budget constrained
- ✅ Texture/visual fidelity critical
- ✅ Open terrain (minimal canopy)
- ✅ Good lighting conditions guaranteed
- ✅ High point density needed

**Choose LiDAR When:**
- ✅ Dense vegetation present
- ✅ Bare earth DEM required
- ✅ Night/poor weather operations
- ✅ Absolute accuracy critical
- ✅ Real-time data needed

**Hybrid Approach (Recommended for Defense):**
```
1. LiDAR for terrain base + canopy penetration
2. Photogrammetry for texture/visual layer
3. Fuse in GIS: LiDAR DEM + Photo ortho

Result: Best of both worlds
```

**Accuracy Comparison:**
```
Urban terrain: Photogrammetry ≈ LiDAR
Forested terrain: LiDAR >> Photogrammetry
Coastal/flat: Either works well
Complex structures: Photogrammetry (more points)
```

**Defense-Specific Considerations:**
- ITAR restrictions on some LiDAR systems
- Classification of high-resolution data
- Real-time vs post-processing requirements
- Integration with existing C4ISR systems""",
        "response_b": "Use photogrammetry for cheaper, detailed textures. Use LiDAR for accuracy and seeing through vegetation. LiDAR is better for most military applications.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "safety": 4, "technical_depth": 5, "clarity": 5}
    },
    {
        "category": "scene_reconstruction",
        "prompt": "What's the best way to handle occlusions in 3D scene reconstruction?",
        "response_a": """**Occlusion Handling Strategies:**

**1. Multi-View Acquisition Planning**
```python
# Ensure sufficient angular coverage
def plan_views(scene_bbox, target_overlap=0.7):
    views = []
    for azimuth in range(0, 360, 30):  # 12 angles
        for elevation in [30, 45, 60]:   # 3 heights
            views.append(compute_camera_pose(
                scene_bbox.center, 
                azimuth, 
                elevation
            ))
    return views
```
- Minimum: 60% overlap between adjacent views
- Ideal: 80%+ for complex geometry
- Critical areas: Targeted additional views

**2. Algorithmic Approaches**

**A. Visibility-Aware MVS:**
```
- Depth map fusion with occlusion reasoning
- Per-pixel visibility masks
- Tools: OpenMVS, COLMAP with visibility constraints
```

**B. Neural Methods:**
```python
# NeRF handles occlusions via density field
density = network(position)
# Zero density = transparent → sees through occlusions

# 3DGS handles via Gaussian opacity
opacity = sigmoid(gaussian.alpha)
# Low opacity areas can be seen through
```

**3. Completion/Inpainting**
```
For unrecoverable occlusions:
1. Segment occluded regions
2. Apply depth completion networks
3. Texture inpainting (LaMa, Stable Diffusion)
4. Mark confidence levels in output
```

**4. Temporal Fusion (Dynamic Scenes)**
```
- Aggregate data across time
- Moving objects reveal occluded areas
- Requires registration/tracking
```

**5. Active Sensing (If Available)**
```
- LiDAR penetrates certain occlusions
- Radar for weather/smoke
- Multi-modal fusion improves coverage
```

**Quality Metrics:**
- Completeness: % of scene reconstructed
- Hole count/size: Occlusion impact measure
- Confidence maps: Per-vertex reliability

**Defense Context:**
- Prioritize critical infrastructure reconstruction
- Flag low-confidence regions for manual review
- Document sensor limitations in products""",
        "response_b": "Capture more views from different angles. Use neural methods like NeRF that can interpolate missing areas. For remaining holes, use inpainting.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "safety": 4, "technical_depth": 5, "clarity": 5}
    },
    {
        "category": "isr_analysis",
        "prompt": "How do I detect camouflaged objects in satellite imagery?",
        "response_a": """**Camouflage Detection Pipeline:**

**1. Multi-Spectral Analysis**
```
Camouflage often fails outside visible spectrum:

Visible (RGB): Designed to deceive
Near-IR (NIR): Vegetation reflectance anomalies
SWIR: Material signature differences
Thermal (LWIR): Heat emission patterns

Key: Chlorophyll reflects strongly in NIR.
Painted camouflage often absorbs it → detectable.
```

**2. Texture Analysis**
```python
# GLCM features reveal artificial patterns
from skimage.feature import graycomatrix, graycoprops

def detect_texture_anomalies(image):
    glcm = graycomatrix(image, [1, 2, 4], 
                        [0, np.pi/4, np.pi/2])
    
    # Natural textures have specific statistics
    contrast = graycoprops(glcm, 'contrast')
    homogeneity = graycoprops(glcm, 'homogeneity')
    
    # Flag anomalies
    return contrast > natural_threshold
```

**3. Shadow Analysis**
```
Camouflage nets cast shadows differently than vegetation:
- Shadow shape inconsistent with cover
- Missing shadows where objects should cast them
- Shadow/height ratio anomalies

Method: Sun angle calculation + shadow projection
```

**4. Temporal Change Detection**
```
# Camouflage positions change; terrain doesn't
for t1, t2 in image_pairs:
    diff = normalized_difference(t1, t2)
    if diff > threshold and not_vehicle_traffic(diff):
        flag_as_suspicious(location)
```

**5. Deep Learning Approaches**
```
Architecture: Siamese networks for anomaly detection
Training data: 
- Synthetic camouflage generation
- Historical confirmed detections
- Negative mining from clean terrain

Models: YOLOv8 fine-tuned, RetinaNet, Mask R-CNN
```

**6. Polarimetric SAR**
```
SAR sees through visual camouflage
Polarimetric signatures distinguish:
- Metal vs vegetation
- Flat surfaces vs natural terrain
- Corner reflectors (vehicles)
```

**Operational Workflow:**
1. Screen with automated detectors
2. Multi-spectral confirmation
3. Temporal comparison
4. Analyst verification
5. Confidence scoring

**Key Indicator Checklist:**
- [ ] Regular geometric patterns
- [ ] Spectral inconsistency
- [ ] Shadow anomalies
- [ ] Temporal changes
- [ ] Thermal signature
- [ ] Vegetation stress patterns""",
        "response_b": "Use multiple spectral bands because camouflage often fails in infrared. Look for texture anomalies and shadow inconsistencies. Use change detection between images.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "safety": 5, "technical_depth": 5, "clarity": 5}
    },
    {
        "category": "isr_analysis",
        "prompt": "What's the best approach for automatic target recognition (ATR) in aerial imagery?",
        "response_a": """**ATR Pipeline Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│                    INPUT PROCESSING                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ EO/IR    │  │   SAR    │  │  MSI     │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       └────────────┬┴──────────────┘                    │
│                    ▼                                     │
│           Preprocessing/Normalization                    │
└─────────────────────┬───────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│                    DETECTION STAGE                       │
│   ┌───────────────────────────────────────┐             │
│   │ Two-Stage: Faster R-CNN, Cascade       │             │
│   │ One-Stage: YOLOv8, DETR, RT-DETR       │             │
│   │ Output: Bounding boxes + confidence    │             │
│   └───────────────────────────────────────┘             │
└─────────────────────┬───────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 CLASSIFICATION STAGE                     │
│   ┌───────────────────────────────────────┐             │
│   │ Fine-grained: Vehicle type, variant   │             │
│   │ Hierarchical: Class → Type → Variant   │             │
│   │ Multi-view fusion if available        │             │
│   └───────────────────────────────────────┘             │
└─────────────────────┬───────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│               VERIFICATION/CONFIDENCE                    │
│   • Multi-frame tracking confirmation                    │
│   • Spectral signature verification                     │
│   • Context analysis (base, convoy, etc.)               │
│   • Human-in-the-loop for high-value targets           │
└─────────────────────────────────────────────────────────┘
```

**Model Selection by Sensor:**

| Sensor | Recommended Architecture | Reason |
|--------|-------------------------|--------|
| EO (Visible) | YOLOv8, RTMDet | Fast, high accuracy |
| IR/Thermal | Modified ResNet, EfficientNet | Fewer features |
| SAR | CNN + CFAR, Complex-valued nets | Speckle handling |
| Hyperspectral | 3D CNN, Transformer | Spectral-spatial |

**Training Considerations:**
```python
# Class imbalance handling
weights = compute_class_weights(target_distribution)
loss = FocalLoss(alpha=weights, gamma=2.0)

# Augmentation for robustness
augment = A.Compose([
    A.RandomRotate90(),
    A.RandomBrightnessContrast(),
    A.GaussNoise(),
    A.RandomScale(scale_limit=0.2),
])

# Hard negative mining
hard_negatives = mine_confusing_backgrounds(dataset)
```

**Performance Metrics:**
- Pd (Probability of Detection) > 90%
- Pfa (False Alarm Rate) < 0.001/km²
- Classification accuracy > 85%
- Processing: < 1 sec/frame for real-time

**Operational Requirements:**
- Model size for edge deployment
- Uncertainty quantification
- Explainability for analyst review
- Graceful degradation under noise""",
        "response_b": "Use deep learning object detection like YOLO or Faster R-CNN. Train on labeled military vehicle datasets. Add a classification stage for target identification.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "safety": 5, "technical_depth": 5, "clarity": 4}
    },
    {
        "category": "geospatial",
        "prompt": "How do I compute a viewshed analysis efficiently over large terrain?",
        "response_a": """**Efficient Viewshed Computation:**

**Algorithm Options:**

**1. Sweepline Algorithm (R3)**
```
Complexity: O(n log n) for n cells
- Sort cells by angle from observer
- Sweep in angular order
- Maintain active edge structure
- Best for single observer

Implementation: GRASS GIS r.viewshed
```

**2. Horizon-based (Franklin/Ray)**
```
Complexity: O(n) per ray
- Cast rays from observer
- Track horizon angle per direction
- Parallel implementation friendly

Implementation: GDAL/custom
```

**3. GPU-Accelerated**
```python
# CUDA kernel for parallel ray casting
@cuda.jit
def viewshed_kernel(dem, observer, result):
    x, y = cuda.grid(2)
    if x < dem.shape[0] and y < dem.shape[1]:
        visible = trace_ray(dem, observer, (x, y))
        result[x, y] = visible
```

**Optimization Strategies:**

**A. Multi-Resolution Pyramid**
```
1. Compute at coarse resolution first
2. Identify boundary cells
3. Refine only boundaries at full resolution
4. Speedup: 3-5x typical
```

**B. Horizon Culling**
```
# Pre-compute horizon profile
horizon = compute_horizon(dem, observer)

# Skip cells clearly below horizon
for cell in cells:
    if elevation[cell] < horizon[angle(cell)]:
        result[cell] = NOT_VISIBLE
        continue
    # Full visibility check only if potentially visible
```

**C. Tiled Processing**
```
For very large DEMs:
1. Divide into tiles with overlap
2. Process tiles in parallel
3. Merge results at boundaries
4. Handle tile seams carefully
```

**D. Approximate Methods (When Speed Critical)**
```
- Sample every Nth ray
- Interpolate between samples
- Error-bounded approximation
- 10-100x faster, <5% error typical
```

**Code Example (Optimized Python/NumPy):**
```python
import numpy as np
from numba import jit, prange

@jit(nopython=True, parallel=True)
def fast_viewshed(dem, obs_row, obs_col, obs_height, max_dist):
    rows, cols = dem.shape
    result = np.zeros((rows, cols), dtype=np.uint8)
    obs_elev = dem[obs_row, obs_col] + obs_height
    
    for r in prange(rows):
        for c in range(cols):
            dist = np.sqrt((r - obs_row)**2 + (c - obs_col)**2)
            if dist > max_dist or dist == 0:
                continue
            
            # Simplified visibility check
            target_elev = dem[r, c]
            slope_to_target = (target_elev - obs_elev) / dist
            
            # Check intermediate cells (simplified)
            visible = True
            steps = int(dist)
            for s in range(1, steps):
                t = s / dist
                ir = int(obs_row + t * (r - obs_row))
                ic = int(obs_col + t * (c - obs_col))
                inter_elev = dem[ir, ic]
                slope_to_inter = (inter_elev - obs_elev) / (s)
                if slope_to_inter > slope_to_target:
                    visible = False
                    break
            
            result[r, c] = 1 if visible else 0
    
    return result
```

**Benchmarks (1000x1000 DEM):**
- Naive Python: ~60 seconds
- NumPy optimized: ~5 seconds
- Numba parallel: ~0.3 seconds
- CUDA: ~0.05 seconds""",
        "response_b": "Use a sweepline algorithm for efficiency. For large terrains, process in tiles and use GPU acceleration if available. GRASS GIS r.viewshed is a good starting point.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "safety": 4, "technical_depth": 5, "clarity": 5}
    },
    {
        "category": "geospatial",
        "prompt": "How do I perform route planning that avoids detection by enemy sensors?",
        "response_a": """**Threat-Aware Route Planning:**

**1. Threat Surface Modeling**
```python
def compute_threat_surface(terrain, sensors):
    threat = np.zeros_like(terrain)
    
    for sensor in sensors:
        # Compute detection probability field
        detection = compute_detection_prob(
            terrain, 
            sensor.location,
            sensor.type,  # radar, optical, acoustic
            sensor.params
        )
        # Aggregate (assume independent)
        threat = 1 - (1 - threat) * (1 - detection)
    
    return threat

# Detection model per sensor type
def radar_detection(terrain, sensor_loc, rcs, power):
    # Line of sight mask
    los = compute_viewshed(terrain, sensor_loc)
    # Range-based detection probability
    range_grid = distance_grid(terrain, sensor_loc)
    snr = power * rcs / (range_grid ** 4)  # Radar equation
    p_detect = 1 - np.exp(-snr / threshold)
    return p_detect * los
```

**2. Cost Surface Generation**
```python
def create_cost_surface(terrain, threat, weights):
    \"\"\"
    weights: dict with keys
      - threat: weight for detection probability
      - slope: weight for terrain difficulty
      - distance: base travel cost
      - exposure: time-in-view penalty
    \"\"\"
    
    slope_cost = compute_slope_cost(terrain)
    
    cost = (
        weights['distance'] * 1.0 +
        weights['threat'] * threat * 100 +  # Heavy penalty
        weights['slope'] * slope_cost
    )
    
    # Clamp impassable areas
    cost[terrain < min_elevation] = np.inf  # Water
    cost[slope > max_slope] = np.inf  # Cliffs
    
    return cost
```

**3. Path Finding Algorithms**

**A* (Single path, optimal):**
```python
def astar_threat_aware(cost, start, goal, threat_threshold):
    # Modified heuristic includes threat
    def heuristic(node):
        dist = euclidean(node, goal)
        threat_cost = threat[node] * remaining_exposure_estimate
        return dist + threat_cost
    
    # Standard A* with modified cost
    return astar(cost, start, goal, heuristic)
```

**RRT* (Probabilistic, complex constraints):**
```python
# Good for 3D (altitude) planning
def rrt_star_threat_aware(space, start, goal, threat):
    tree = Tree(start)
    for _ in range(max_iterations):
        sample = sample_low_threat_region(space, threat)
        nearest = tree.nearest(sample)
        new_node = steer(nearest, sample, step_size)
        
        if collision_free(nearest, new_node) and \
           max_threat_along_path(nearest, new_node) < threshold:
            tree.add(new_node, nearest)
            rewire_neighbors(tree, new_node)
    
    return tree.path_to(goal)
```

**4. Multi-Objective Optimization**
```
Pareto-optimal trade-offs:
- Minimum distance vs minimum exposure
- Speed vs stealth
- Single route vs multiple waypoints

Algorithm: NSGA-II, MOEA/D
Output: Set of routes for commander decision
```

**5. Temporal Considerations**
```python
# Threat varies with time (patrols, lighting)
def time_varying_threat(base_threat, time):
    # Optical sensors worse at night
    optical_factor = daylight_factor(time)
    # Patrol schedules
    patrol_factor = patrol_presence(time)
    
    return base_threat * optical_factor * patrol_factor

# Plan route with time windows
def temporal_route_plan(start, goal, departure_time):
    # Discretize time
    # Plan in (x, y, t) space
    # Minimize cumulative detection probability
```

**Output Products:**
- Primary route with waypoints
- Alternate routes
- High-risk segments identified
- Time windows for safe passage
- Go/No-go decision support""",
        "response_b": "Build a threat map from sensor locations using viewshed analysis. Create a cost surface that penalizes high-threat areas. Use A* or Dijkstra to find the path with minimum total threat.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "safety": 5, "technical_depth": 5, "clarity": 5}
    },
    {
        "category": "simulation",
        "prompt": "How do I model uncertainty in terrain and entity positions for simulation?",
        "response_a": """**Uncertainty Modeling Framework:**

**1. Terrain Uncertainty**

**A. DEM Error Models:**
```python
class UncertainTerrain:
    def __init__(self, dem, error_model):
        self.dem = dem
        self.error = error_model  # Per-cell std dev
    
    def sample(self):
        \"\"\"Generate one realization of terrain\"\"\"
        noise = np.random.normal(0, self.error)
        return self.dem + noise
    
    def monte_carlo_viewshed(self, observer, n_samples=100):
        \"\"\"Probabilistic viewshed\"\"\"
        visibility_sum = np.zeros_like(self.dem)
        for _ in range(n_samples):
            terrain_sample = self.sample()
            vs = compute_viewshed(terrain_sample, observer)
            visibility_sum += vs
        return visibility_sum / n_samples  # P(visible)
```

**B. Correlated Errors (More Realistic):**
```python
# Terrain errors are spatially correlated
from scipy.ndimage import gaussian_filter

def correlated_terrain_sample(dem, error_std, correlation_length):
    # White noise
    noise = np.random.normal(0, 1, dem.shape)
    # Apply spatial correlation
    correlated = gaussian_filter(noise, sigma=correlation_length)
    # Scale to desired std
    correlated *= error_std / correlated.std()
    return dem + correlated
```

**2. Entity Position Uncertainty**

**A. Gaussian Models:**
```python
class UncertainEntity:
    def __init__(self, mean_pos, covariance):
        self.mean = np.array(mean_pos)  # [x, y]
        self.cov = np.array(covariance)  # 2x2 covariance
    
    def sample(self, n=1):
        return np.random.multivariate_normal(self.mean, self.cov, n)
    
    def confidence_ellipse(self, confidence=0.95):
        \"\"\"Return ellipse parameters for visualization\"\"\"
        chi2_val = chi2.ppf(confidence, 2)
        eigenvalues, eigenvectors = np.linalg.eig(self.cov)
        angle = np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0])
        width = 2 * np.sqrt(chi2_val * eigenvalues[0])
        height = 2 * np.sqrt(chi2_val * eigenvalues[1])
        return width, height, angle
```

**B. Particle Filters (Non-Gaussian, Dynamic):**
```python
class ParticleFilter:
    def __init__(self, n_particles, initial_state, process_noise):
        self.particles = initial_state + np.random.randn(n_particles, 2) * process_noise
        self.weights = np.ones(n_particles) / n_particles
    
    def predict(self, motion_model, dt):
        self.particles = motion_model(self.particles, dt)
        self.particles += np.random.randn(*self.particles.shape) * self.process_noise
    
    def update(self, observation, observation_model):
        likelihoods = observation_model(self.particles, observation)
        self.weights *= likelihoods
        self.weights /= self.weights.sum()
        self.resample_if_needed()
    
    def estimate(self):
        return np.average(self.particles, weights=self.weights, axis=0)
    
    def uncertainty(self):
        mean = self.estimate()
        return np.cov(self.particles.T, aweights=self.weights)
```

**3. Propagating Uncertainty Through Simulation**

**Monte Carlo Simulation:**
```python
def uncertain_engagement_simulation(friendly, threat, terrain, n_runs=1000):
    results = {
        'detection_times': [],
        'engagement_outcomes': [],
        'casualties': []
    }
    
    for _ in range(n_runs):
        # Sample all uncertain quantities
        t = terrain.sample()
        f_pos = friendly.sample()
        t_pos = threat.sample()
        
        # Run deterministic simulation with samples
        outcome = run_simulation(t, f_pos, t_pos)
        
        # Collect statistics
        results['detection_times'].append(outcome.detection_time)
        results['engagement_outcomes'].append(outcome.winner)
    
    return {
        'p_detection': np.mean([t < np.inf for t in results['detection_times']]),
        'p_win': np.mean([o == 'friendly' for o in results['engagement_outcomes']]),
        'detection_time_ci': np.percentile(results['detection_times'], [5, 95])
    }
```

**4. Visualization:**
```
- Confidence ellipses for positions
- Probability heat maps for terrain visibility
- Ensemble trajectories for predicted paths
- Confidence bounds on engagement ranges
```""",
        "response_b": "Use Gaussian distributions for position uncertainty. Run Monte Carlo simulations sampling from the distributions. Aggregate results to get probability estimates.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "safety": 4, "technical_depth": 5, "clarity": 5}
    },
    {
        "category": "sensor_fusion",
        "prompt": "How do I fuse data from multiple sensor types (EO, IR, radar) for tracking?",
        "response_a": """**Multi-Sensor Fusion Architecture:**

```
         EO Camera          IR Sensor           Radar
              │                  │                 │
              ▼                  ▼                 │
         Detection          Detection            ▼
         (YOLO/CNN)        (Threshold)       Detection
              │                  │            (CFAR)
              ▼                  ▼                 │
         [x,y,w,h,c]      [x,y,intensity]    [r,θ,v]
              │                  │                 │
              └──────────────────┼─────────────────┘
                                 ▼
                    ┌───────────────────────┐
                    │   COORDINATE FUSION   │
                    │  (Common reference)   │
                    └───────────┬───────────┘
                                ▼
                    ┌───────────────────────┐
                    │   DATA ASSOCIATION    │
                    │  (Hungarian/JPDA)     │
                    └───────────┬───────────┘
                                ▼
                    ┌───────────────────────┐
                    │    STATE FUSION       │
                    │  (Kalman/Particle)    │
                    └───────────┬───────────┘
                                ▼
                         Fused Tracks
```

**1. Coordinate Alignment**
```python
class SensorFusionSystem:
    def __init__(self, sensors):
        self.sensors = sensors
        # Calibration: sensor → common frame
        self.transforms = self.calibrate()
    
    def to_common_frame(self, detection, sensor_id):
        T = self.transforms[sensor_id]
        # Homogeneous transform
        pos_sensor = np.array([detection.x, detection.y, detection.z, 1])
        pos_common = T @ pos_sensor
        return pos_common[:3]
```

**2. Data Association**
```python
def associate_detections(tracks, detections, gating_threshold):
    \"\"\"Global Nearest Neighbor with gating\"\"\"
    n_tracks = len(tracks)
    n_dets = len(detections)
    
    # Cost matrix: Mahalanobis distance
    cost = np.zeros((n_tracks, n_dets))
    for i, track in enumerate(tracks):
        for j, det in enumerate(detections):
            innovation = det.position - track.predicted_position
            S = track.innovation_covariance + det.covariance
            cost[i, j] = innovation.T @ np.linalg.inv(S) @ innovation
    
    # Gate unlikely associations
    cost[cost > gating_threshold] = 1e9
    
    # Hungarian algorithm for optimal assignment
    row_ind, col_ind = linear_sum_assignment(cost)
    
    return list(zip(row_ind, col_ind))
```

**3. State Fusion (Extended Kalman Filter)**
```python
class FusedTracker:
    def __init__(self):
        self.state = None  # [x, y, z, vx, vy, vz]
        self.covariance = None
        
    def predict(self, dt):
        F = np.eye(6)
        F[0, 3] = F[1, 4] = F[2, 5] = dt  # Constant velocity
        
        self.state = F @ self.state
        Q = process_noise(dt)
        self.covariance = F @ self.covariance @ F.T + Q
    
    def update_eo(self, detection):
        \"\"\"EO: measures [x, y] with high precision\"\"\"
        H = np.array([[1, 0, 0, 0, 0, 0],
                      [0, 1, 0, 0, 0, 0]])
        R = np.diag([detection.std_x**2, detection.std_y**2])
        self._kalman_update(detection.position[:2], H, R)
    
    def update_radar(self, detection):
        \"\"\"Radar: measures [range, azimuth, velocity]\"\"\"
        # Nonlinear measurement → Extended Kalman
        H = self._radar_jacobian()
        z_pred = self._radar_measurement_model()
        R = np.diag([detection.std_r**2, detection.std_az**2, 
                     detection.std_v**2])
        self._kalman_update(detection.measurement, H, R, z_pred)
    
    def update_ir(self, detection):
        \"\"\"IR: measures [x, y] with medium precision\"\"\"
        H = np.array([[1, 0, 0, 0, 0, 0],
                      [0, 1, 0, 0, 0, 0]])
        R = np.diag([detection.std_x**2, detection.std_y**2])
        self._kalman_update(detection.position[:2], H, R)
```

**4. Track Management**
```python
class TrackManager:
    def __init__(self):
        self.tracks = []
        self.track_id_counter = 0
    
    def process_frame(self, detections_by_sensor):
        # Predict all tracks
        for track in self.tracks:
            track.predict(dt)
        
        # Update with each sensor type
        for sensor_type, detections in detections_by_sensor.items():
            assoc = associate_detections(self.tracks, detections)
            
            for track_idx, det_idx in assoc:
                update_fn = getattr(self.tracks[track_idx], 
                                   f'update_{sensor_type}')
                update_fn(detections[det_idx])
            
            # New tracks from unassociated detections
            unassoc_dets = [d for i, d in enumerate(detections) 
                          if i not in [a[1] for a in assoc]]
            for det in unassoc_dets:
                self.initiate_track(det)
        
        # Prune stale tracks
        self.tracks = [t for t in self.tracks if t.age < max_age]
```

**5. Confidence & Quality**
```python
def compute_track_quality(track):
    return {
        'sensors_contributing': track.sensor_count,
        'position_uncertainty': np.sqrt(np.trace(track.covariance[:3, :3])),
        'velocity_uncertainty': np.sqrt(np.trace(track.covariance[3:, 3:])),
        'track_age': track.age,
        'update_rate': track.updates / track.age
    }
```""",
        "response_b": "Transform all detections to a common coordinate system. Use data association (Hungarian algorithm) to match detections to tracks. Update track states with a Kalman filter using sensor-specific measurement models.",
        "preference": "A",
        "dimension_scores": {"accuracy": 5, "safety": 5, "technical_depth": 5, "clarity": 4}
    },
]

# Additional halal preferences (30 more)
HALAL_SEEDS_EXPANDED = [
    {
        "category": "ingredient_analysis",
        "prompt": "Is gelatin halal, and what are halal alternatives?",
        "response_a": """**Gelatin Halal Status:**

**Standard Gelatin: Usually NOT Halal**
- Most commercial gelatin is pork-derived
- Bovine gelatin requires halal slaughter verification
- Fish gelatin is generally halal

**Gelatin Sources & Status:**

| Source | Status | Notes |
|--------|--------|-------|
| Pork | ❌ Haram | Most common in Western markets |
| Beef (non-halal) | ❌ Haram | Slaughter method matters |
| Beef (halal certified) | ✅ Halal | Requires certification |
| Fish | ✅ Halal | Generally accepted |
| Poultry (halal) | ✅ Halal | Less common |

**Verification Steps:**
1. Request specification sheet
2. Look for "bovine" or "porcine" designation
3. If bovine: require halal certificate for source
4. Cross-reference with CB approved supplier list

**Halal Alternatives:**

**1. Agar-Agar (Seaweed)**
```
Properties:
- Vegetarian/vegan
- Sets firmer than gelatin
- Melts at higher temperature
- Use: 1/4 tsp agar = 1 tsp gelatin

Applications: Jellies, puddings, glazes
```

**2. Carrageenan (Seaweed)**
```
Properties:
- Multiple types (kappa, iota, lambda)
- Different gel strengths
- Works with dairy proteins

Applications: Dairy desserts, plant milks
```

**3. Pectin (Fruit)**
```
Properties:
- Requires acid + sugar to gel
- Apple or citrus derived

Applications: Jams, fruit snacks, gummies
```

**4. Konjac (Plant)**
```
Properties:
- Very strong gel
- Low calorie
- Thermally stable

Applications: Noodles, jellies, meat alternatives
```

**5. Halal-Certified Gelatin**
```
Sources:
- Islamic Food and Nutrition Council (IFANCA)
- Certified halal bovine suppliers
- Fish gelatin (no certification needed)

Cost: ~2-3x conventional gelatin
```

**Application Comparison:**

| Application | Best Alternative |
|-------------|-----------------|
| Gummies | Pectin, halal gelatin |
| Marshmallows | Halal gelatin, carrageenan |
| Yogurt | Pectin, carrageenan |
| Capsules | HPMC, pullulan, fish gelatin |
| Cosmetics | Plant-based gelling agents |

**Procurement Tip:** Always specify "halal" or "fish-based" when ordering gelatin for halal products.""",
        "response_b": "Most gelatin is from pork and is haram. Use agar-agar, pectin, or carrageenan instead. Halal-certified bovine gelatin or fish gelatin are also options.",
        "preference": "A",
        "dimension_scores": {"compliance": 5, "accuracy": 5, "clarity": 5, "actionability": 5}
    },
    {
        "category": "ingredient_analysis",
        "prompt": "How do I evaluate whether a food flavor is halal?",
        "response_a": """**Halal Flavor Evaluation Guide:**

**Why Flavors Are Complex:**
- Proprietary formulations (trade secrets)
- Multiple sub-ingredients
- Carrier/solvent systems
- Extraction methods matter

**Red Flag Ingredients in Flavors:**

| Ingredient | Concern | Status |
|------------|---------|--------|
| Ethyl alcohol | Solvent | Debated* |
| Propylene glycol | Carrier | ✅ Halal |
| Glycerin | Carrier | Check source |
| Natural flavors | May contain animal | Investigate |
| Castoreum | Beaver-derived | ❌ Haram |
| Civet musk | Cat-derived | ❌ Haram |
| Carmine | Insect-derived | Debated |

**Alcohol in Flavors:**
```
Scholarly Positions:
1. Strict: Any alcohol = haram
2. Moderate: Trace amounts (< 0.5%) OK if:
   - Not from grape/date wine
   - Evaporates in cooking
   - Not for intoxication purpose
3. JAKIM: < 0.01% in final food product

Practical Approach:
- Request alcohol-free flavor variants
- Calculate final product concentration
- Document for certification body
```

**Evaluation Process:**

**Step 1: Request Documentation**
```
□ Complete ingredient list
□ Specification sheet
□ Halal certificate (if claimed)
□ Allergen statement
□ Source declarations
```

**Step 2: Ingredient Analysis**
```python
# Systematic review
for ingredient in flavor_ingredients:
    if ingredient in known_haram:
        return "HARAM"
    if ingredient in need_verification:
        request_source_documentation(ingredient)
    if ingredient in alcohol_based:
        calculate_final_concentration()
```

**Step 3: Source Verification**
For each questionable ingredient:
- Animal-derived? → Halal slaughter required
- Alcohol-based? → Check type and concentration
- Enzymatically produced? → Check enzyme source

**Step 4: Manufacturing Process**
- Extraction solvents used?
- Shared equipment with non-halal?
- Cleaning validation?

**Common "Natural Flavor" Sources:**

| Flavor Type | Potential Sources | Halal Concern |
|-------------|------------------|---------------|
| Vanilla | Bean, castoreum | Verify not castoreum |
| Raspberry | Fruit, castoreum | Verify not castoreum |
| Butter | Dairy, animal fat | Check fat source |
| Meat flavors | Hydrolyzed proteins | Animal source |
| Smoke | Wood, liquid smoke | Usually OK |

**Documentation Template:**
```
Flavor: [Name]
Supplier: [Company]
Halal Certificate: [Yes/No/Pending]
Alcohol Content: [%]
Animal-Derived: [Yes/No/Unknown]
Verification Status: [Approved/Rejected/Pending]
Notes: [Details]
```

**Best Practice:** Work with flavor houses that offer halal-certified product lines (Givaudan, IFF, Firmenich all have halal options).""",
        "response_b": "Ask for the ingredient list and check for alcohol or animal-derived ingredients. Request halal certification from the flavor supplier. Natural flavors need extra scrutiny.",
        "preference": "A",
        "dimension_scores": {"compliance": 5, "accuracy": 5, "clarity": 5, "actionability": 5}
    },
    {
        "category": "certification",
        "prompt": "What are the common non-conformances found during halal audits?",
        "response_a": """**Common Halal Audit Non-Conformances:**

**Category 1: Documentation (40% of findings)**

| Finding | Severity | Corrective Action |
|---------|----------|-------------------|
| Missing supplier certificates | Major | Obtain before next production |
| Expired halal certificates | Major | Request renewal immediately |
| Incomplete ingredient specs | Minor | Update specification system |
| Traceability gaps | Major | Implement batch tracking |
| Missing training records | Minor | Conduct and document training |

**Category 2: Ingredient Control (25% of findings)**

```
Common Issues:
□ Unapproved ingredient substitution
□ New ingredients without halal review
□ Supplier change without re-verification
□ Animal-derived ingredients undeclared
□ Alcohol-based ingredients above threshold
```

**Prevention:**
- Ingredient change management procedure
- Approved supplier list with expiration tracking
- Incoming inspection for critical ingredients

**Category 3: Cross-Contamination (20% of findings)**

| Issue | Risk Level | Solution |
|-------|-----------|----------|
| Shared equipment with pork | Critical | Dedicated or validated cleaning |
| Inadequate cleaning validation | Major | ATP testing, visual inspection |
| Improper storage segregation | Major | Physical barriers, labeling |
| Personnel handling | Minor | Training, dedicated PPE |
| Utensil mixing | Minor | Color coding, labeling |

**Category 4: Production Control (10% of findings)**

```
Issues Found:
□ Production sequence violations
□ Missing halal supervisor during production
□ Incomplete batch records
□ Non-halal products on same line same day
□ Rework procedures not documented
```

**Category 5: Labeling & Claims (5% of findings)**

- Halal logo used without approval
- Incorrect certification body referenced
- Claims not matching certificate scope
- Missing required statements

**Severity Classification:**

| Severity | Definition | Timeline |
|----------|-----------|----------|
| Critical | Haram contamination confirmed | Immediate stop, recall assessment |
| Major | System failure, high risk | Correct within 30 days |
| Minor | Documentation gap, low risk | Correct within 90 days |
| Observation | Improvement opportunity | Address at next audit |

**Audit Preparation Checklist:**

```
Pre-Audit (30 days before):
□ Internal audit completed
□ Previous NCRs closed
□ All certificates current
□ Training records updated
□ Equipment logs reviewed

Day Before:
□ Key personnel available
□ Documents organized
□ Production schedule reviewed
□ Sample products available
□ Cleaning records accessible
```

**Root Cause Categories:**
1. Training gap (35%)
2. Procedure not followed (25%)
3. Procedure inadequate (20%)
4. Resource constraint (10%)
5. Communication failure (10%)

**Tip:** Most NCRs are preventable with robust incoming ingredient control and documentation systems.""",
        "response_b": "Common issues include missing or expired certificates, cross-contamination risks, inadequate cleaning procedures, and documentation gaps. Train staff and verify suppliers to prevent these.",
        "preference": "A",
        "dimension_scores": {"compliance": 5, "accuracy": 5, "clarity": 5, "actionability": 5}
    },
    {
        "category": "supply_chain",
        "prompt": "How do I set up a halal supplier qualification program?",
        "response_a": """**Halal Supplier Qualification Program:**

**1. Program Structure**

```
┌─────────────────────────────────────────────────────────┐
│              SUPPLIER QUALIFICATION TIERS               │
├─────────────────────────────────────────────────────────┤
│ Tier 1: Critical (Halal-sensitive ingredients)          │
│   → Full audit, annual verification, batch traceability │
│                                                         │
│ Tier 2: Important (Supporting ingredients)              │
│   → Document review, periodic verification              │
│                                                         │
│ Tier 3: Low Risk (Non-food contact)                    │
│   → Declaration only                                    │
└─────────────────────────────────────────────────────────┘
```

**2. Qualification Requirements by Tier**

**Tier 1 (Critical):**
```
Required Documents:
□ Valid halal certificate from recognized CB
□ Certificate of Analysis (COA) per batch
□ Product specification sheet
□ Manufacturing process description
□ Cleaning validation records
□ Supplier's supplier certificates (if applicable)

Verification:
□ On-site audit (initial + periodic)
□ Certificate authenticity verification
□ Sample testing (as applicable)
□ Annual reassessment
```

**Tier 2 (Important):**
```
Required Documents:
□ Halal certificate OR halal declaration
□ Product specification sheet
□ Ingredient list with sources

Verification:
□ Desktop audit
□ Certificate verification
□ Periodic sampling
□ Biannual reassessment
```

**Tier 3 (Low Risk):**
```
Required Documents:
□ Product specification sheet
□ Halal status declaration

Verification:
□ Declaration review
□ As-needed verification
```

**3. Supplier Assessment Form**

```
HALAL SUPPLIER QUALIFICATION ASSESSMENT

Section A: Company Information
- Legal name, address, contacts
- Years in business
- Quality certifications (ISO, FSSC, etc.)

Section B: Halal Status
- Current halal certification: Y/N
- Certifying body: __________
- Certificate number: __________
- Validity: __________
- Scope: __________

Section C: Product-Specific
- Product name: __________
- Halal-sensitive ingredients: __________
- Animal-derived components: __________
- Alcohol content: __________
- Processing aids: __________

Section D: Manufacturing
- Dedicated halal facility: Y/N
- Shared lines with non-halal: Y/N
- Cleaning procedure: __________
- Segregation method: __________

Section E: Traceability
- Batch tracking system: Y/N
- Recall capability: Y/N

Assessment Result: □ Approved □ Conditional □ Rejected
```

**4. Ongoing Monitoring**

```python
# Supplier monitoring schedule
monitoring_activities = {
    "certificate_review": {
        "frequency": "quarterly",
        "action": "verify_certificate_status"
    },
    "specification_update": {
        "frequency": "annual",
        "action": "request_updated_specs"
    },
    "performance_review": {
        "frequency": "annual",
        "action": "assess_delivery_quality"
    },
    "on_site_audit": {
        "frequency": "biannual",  # Tier 1 only
        "action": "conduct_supplier_audit"
    }
}
```

**5. Non-Conformance Handling**

| Issue | Action | Timeline |
|-------|--------|----------|
| Certificate expired | Suspend until renewed | Immediate |
| Specification change | Re-evaluate | 30 days |
| Quality issue | Investigation | 15 days |
| Failed audit | Corrective action plan | 60 days |

**6. Approved Supplier List (ASL) Management**

```
ASL Entry:
- Supplier ID
- Products approved
- Tier classification
- Certificate expiry (auto-alert 60 days prior)
- Last audit date
- Status: Active/Suspended/Pending
- Notes/restrictions
```

**KPIs:**
- % suppliers with current certificates
- Certificate renewal compliance rate
- NCRs per supplier
- Supplier audit completion rate""",
        "response_b": "Classify suppliers by risk level. Require halal certificates and documentation from high-risk suppliers. Audit critical suppliers and verify certificates are valid and from recognized bodies.",
        "preference": "A",
        "dimension_scores": {"compliance": 5, "accuracy": 5, "clarity": 5, "actionability": 5}
    },
    {
        "category": "documentation",
        "prompt": "What records do I need to maintain for halal compliance?",
        "response_a": """**Halal Documentation Requirements:**

**1. Core Documentation Categories**

```
┌─────────────────────────────────────────────────────────┐
│                 HALAL RECORD HIERARCHY                   │
├─────────────────────────────────────────────────────────┤
│ Level 1: Certificates & Policies                        │
│   ├── Halal policy statement                           │
│   ├── Halal certificates (yours & suppliers)           │
│   └── CB recognition documents                          │
│                                                         │
│ Level 2: Procedures & Specifications                    │
│   ├── Halal control plan                               │
│   ├── SOPs (cleaning, production, receiving)           │
│   └── Product/ingredient specifications                 │
│                                                         │
│ Level 3: Operational Records                           │
│   ├── Production records                               │
│   ├── Traceability records                             │
│   └── Training records                                  │
│                                                         │
│ Level 4: Verification Records                          │
│   ├── Audit reports                                    │
│   ├── Inspection records                               │
│   └── Non-conformance records                          │
└─────────────────────────────────────────────────────────┘
```

**2. Document Matrix**

| Document | Owner | Review Freq | Retention |
|----------|-------|-------------|-----------|
| Halal Policy | QA Manager | Annual | Permanent |
| Halal Certificate | QA | Per validity | Expiry + 3 years |
| Supplier Certificates | Procurement | Per validity | Expiry + 3 years |
| Ingredient Specs | QA | Per change | Current + 3 years |
| Halal Control Plan | QA Manager | Annual | Current + 5 years |
| Production Records | Production | Per batch | 3 years |
| Cleaning Records | Production | Per cleaning | 2 years |
| Training Records | HR | Annual | Employment + 3 years |
| Audit Reports | QA | Per audit | 5 years |
| NCR/CAPA | QA | Per event | 5 years |

**3. Halal Control Plan Contents**

```
HALAL CONTROL PLAN (HCP)

1. Scope
   - Products covered
   - Facilities included
   - Certificate reference

2. Halal Committee
   - Members and roles
   - Meeting frequency
   - Authority/responsibilities

3. Ingredient Control
   - Approved ingredient list
   - Supplier qualification process
   - Incoming inspection procedure
   - Non-conforming material handling

4. Production Control
   - Production sequence requirements
   - Equipment cleaning validation
   - Cross-contamination prevention
   - Halal supervisor requirements

5. Storage & Handling
   - Segregation requirements
   - Labeling requirements
   - FIFO/FEFO procedures

6. Traceability
   - Batch coding system
   - Forward/backward trace capability
   - Recall procedure

7. Training
   - Training requirements by role
   - Competency assessment
   - Refresher schedule

8. Internal Audit
   - Audit schedule
   - Checklist
   - Reporting

9. Document Control
   - Record retention
   - Access control
   - Change management
```

**4. Production Batch Record Template**

```
HALAL PRODUCTION BATCH RECORD

Batch #: ___________  Date: ___________
Product: ___________  Line: ___________

PRE-PRODUCTION
□ Line cleaned per SOP-xxx
□ Cleaning verification: □ Visual □ ATP (Result: ___)
□ Previous product: ___________
□ Halal supervisor present: ___________

INGREDIENTS USED
| Ingredient | Batch # | Qty | Halal Cert Ref |
|------------|---------|-----|----------------|
|            |         |     |                |

PRODUCTION
□ Start time: ___  □ End time: ___
□ Equipment used: ___________
□ Deviations: □ None □ See NCR #___

POST-PRODUCTION
□ Finished product batch #: ___________
□ Quantity produced: ___________
□ QC release: ___________

Verified by Halal Supervisor: ___________
Date: ___________
```

**5. Digital vs Paper Records**

```
Recommended: Electronic Document Management System

Benefits:
- Automatic retention/archival
- Version control
- Access logging
- Search capability
- Certificate expiry alerts

Minimum Requirements:
- Backup procedures
- Access controls
- Audit trail
- Signature/approval workflow
```

**6. Audit-Ready File Structure**

```
/Halal_Compliance/
├── 01_Certificates/
│   ├── Company_Certificate/
│   └── Supplier_Certificates/
├── 02_Policies_Procedures/
│   ├── Halal_Policy.pdf
│   ├── Halal_Control_Plan.pdf
│   └── SOPs/
├── 03_Specifications/
│   ├── Ingredients/
│   └── Products/
├── 04_Production_Records/
│   └── [Year]/[Month]/
├── 05_Training/
├── 06_Audits/
│   ├── Internal/
│   └── External/
└── 07_NCR_CAPA/
```""",
        "response_b": "Keep certificates, supplier documents, production records, cleaning logs, training records, and audit reports. Maintain a halal control plan and retain records for 3-5 years minimum.",
        "preference": "A",
        "dimension_scores": {"compliance": 5, "accuracy": 5, "clarity": 5, "actionability": 5}
    },
]

# Export all expanded seeds
EXPANDED_SEEDS = {
    "procurement": PROCUREMENT_SEEDS_EXPANDED,
    "defense_wm": DEFENSE_WM_SEEDS_EXPANDED,
    "halal": HALAL_SEEDS_EXPANDED,
}

if __name__ == "__main__":
    print("Expanded Seeds Summary:")
    for domain, seeds in EXPANDED_SEEDS.items():
        print(f"  {domain}: {len(seeds)} additional seeds")
    print(f"  TOTAL: {sum(len(s) for s in EXPANDED_SEEDS.values())} new seeds")

