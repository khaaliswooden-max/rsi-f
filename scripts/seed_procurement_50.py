# File: scripts/seed_procurement_50.py
"""
50 synthetic procurement preferences for DPO cold-start.
Run: python scripts/seed_procurement_50.py
"""

import httpx
import asyncio
import json
import os
import hashlib
from pathlib import Path
from datetime import datetime, timezone

API_BASE = "https://zuup1-zuup-preference-collection.hf.space"
API_KEY = os.getenv("ZUUP_API_KEY", "zuup-seed-key")  # Set via environment or use default

# Local mode: save directly to JSONL file
LOCAL_MODE = os.getenv("LOCAL_MODE", "true").lower() == "true"
DATA_DIR = Path(__file__).parent.parent / "preference_data"

PROCUREMENT_PREFERENCES = [
    # ============ RFP ANALYSIS (13 items) ============
    {
        "category": "rfp_analysis",
        "prompt": "What are the key evaluation factors I should look for in a DoD IT services RFP?",
        "chosen": """Key evaluation factors in DoD IT RFPs typically follow this hierarchy:

**Factor 1: Technical Approach** (usually most important)
- Understanding of requirements
- Technical solution soundness
- Risk mitigation approach
- Innovation/value-added features

**Factor 2: Past Performance**
- Relevance (size, scope, complexity)
- Recency (typically last 3-5 years)
- Quality ratings from CPARS/PPIRS

**Factor 3: Management Approach**
- Key personnel qualifications
- Staffing plan and retention
- Quality control processes
- Transition plan

**Factor 4: Price/Cost**
- Often "fair and reasonable" vs. lowest
- Price realism for cost-type contracts
- Unbalanced pricing review

Look in Section M for weighting. Common: Technical > Past Performance > Price, or Technical/Past Performance equal, significantly more important than Price.""",
        "rejected": "Look at Section M for evaluation criteria. They usually care about technical approach and price."
    },
    {
        "category": "rfp_analysis",
        "prompt": "How do I identify if an RFP is wired for an incumbent?",
        "chosen": """Red flags indicating incumbent advantage:

**Structural indicators:**
- Very short turnaround (< 20 days for complex work)
- Excessive specificity in requirements matching incumbent's current solution
- Unusual NAICS code selection limiting competition
- Brand-name-or-equal specs without justification
- Requirements for existing facility/infrastructure in specific location

**Past performance traps:**
- Requires experience on "same or similar" contracts with narrow definition
- Demands specific certifications incumbent already holds
- References to proprietary systems only incumbent knows

**Pricing signals:**
- Unrealistic LOE estimates (too low to bid profitably)
- Specific labor categories matching incumbent's structure exactly
- Government estimate suspiciously close to incumbent's current pricing

**Mitigation:** File RFI asking for clarification on restrictive requirements. If systemic issues, consider GAO protest pre-award (must file before proposal due date).""",
        "rejected": "If the requirements seem very specific or the timeline is short, it might favor the incumbent."
    },
    {
        "category": "rfp_analysis",
        "prompt": "What does 'LPTA' mean and when should I walk away from an LPTA procurement?",
        "chosen": """**LPTA = Lowest Price Technically Acceptable**

Evaluation method where all technically acceptable proposals are ranked by price alone. Lowest price wins.

**Walk-away indicators:**
1. Your cost structure can't compete (high overhead, expensive location)
2. Requirements are commodity-like but you offer premium differentiation
3. Incumbent has significant cost advantage (amortized startup, trained staff)
4. Your past performance is your strength, not your price
5. Margins would be < 5% at competitive price point

**Viable LPTA scenarios:**
- You have lowest cost structure in competitive set
- You can innovate on delivery to reduce costs
- Strategic capture (accept low margins for past performance)
- Recompete where you're incumbent with sunk costs

**Key insight:** LPTA procurements often have higher protest rates because "technically acceptable" is subjective. If you're close on price, small technical distinctions matter.""",
        "rejected": "LPTA means lowest price wins. Walk away if you can't be the cheapest."
    },
    {
        "category": "rfp_analysis",
        "prompt": "Explain Section L and Section M in a federal RFP.",
        "chosen": """**Section L: Instructions to Offerors**
- Proposal format requirements (page limits, font, margins)
- Volume structure (Technical, Management, Past Performance, Cost)
- Submission instructions (portal, copies, deadlines)
- Required forms and certifications
- Questions/RFI process and deadlines

**Section M: Evaluation Criteria**
- Evaluation factors and subfactors
- Relative importance/weighting
- Rating methodology (adjectival, color, points)
- Basis for award (best value, LPTA, tradeoff)
- Sample evaluation language

**Critical relationship:** Section L tells you WHAT to submit; Section M tells you HOW it's scored. Your proposal structure should mirror Section M's evaluation factors exactly.

**Pro tip:** Create a compliance matrix mapping every L requirement to your proposal location, then a second matrix mapping every M factor to where you address it. Evaluators use similar matrices—make their job easy.""",
        "rejected": "Section L has the instructions and Section M has the evaluation criteria. Follow both carefully."
    },
    {
        "category": "rfp_analysis",
        "prompt": "What is a Sources Sought notice and should I respond?",
        "chosen": """**Sources Sought = Market research tool (not a solicitation)**

Government uses it to:
- Identify potential vendors
- Determine if set-aside is appropriate (8(a), SDVOSB, HUBZone)
- Refine requirements based on industry feedback
- Estimate pricing and capability availability

**Always respond if:**
- You intend to bid the eventual RFP
- You have relevant past performance
- You want to shape requirements
- You qualify for applicable set-asides

**Response strategy:**
1. Capability statement (2-3 pages)
2. Relevant past performance (3-5 contracts)
3. Feedback on draft requirements (be constructive)
4. Teaming interest if you'd pursue as sub
5. Set-aside qualification status

**ROI:** Low effort (4-8 hours), high value. Non-response signals to CO you're not interested. Response gets you on their radar for RFI notifications and potential industry days.

**Not binding:** Responding doesn't obligate you to bid.""",
        "rejected": "Sources Sought notices are for market research. You can respond with your capabilities if interested."
    },
    {
        "category": "rfp_analysis",
        "prompt": "How do I analyze a Statement of Work vs Performance Work Statement?",
        "chosen": """**SOW (Statement of Work) - Prescriptive**
- Specifies HOW to perform work
- Government assumes more risk
- Detailed task descriptions
- Input-focused metrics
- Common in cost-reimbursement contracts

**PWS (Performance Work Statement) - Outcome-based**
- Specifies WHAT outcomes required
- Contractor assumes more risk/flexibility
- Performance standards and metrics
- Output-focused (SLAs, KPIs)
- Common in firm-fixed-price contracts

**Analysis framework for either:**

1. **Extract requirements:** List every "shall" statement
2. **Map to WBS:** Group requirements into work breakdown
3. **Identify deliverables:** CDRLs, reports, artifacts
4. **Find ambiguity:** Requirements needing clarification via RFI
5. **Assess risk:** Which requirements have cost/schedule uncertainty
6. **Quantify LOE:** Estimate labor hours per requirement
7. **Gap analysis:** What's missing that you'll need to assume

**Pro tip:** For PWS, propose your methodology to achieve outcomes. For SOW, demonstrate compliance with prescribed approach while noting efficiencies.""",
        "rejected": "SOW tells you how to do the work, PWS tells you what results are needed. Analyze the requirements carefully."
    },
    {
        "category": "rfp_analysis",
        "prompt": "What is a J&A and when does the government need one?",
        "chosen": """**J&A = Justification and Approval**

Required when government uses other than full and open competition (FAR 6.3).

**Triggers requiring J&A:**
- Sole source awards > $25K
- Brand name specifications without "or equal"
- Limited sources (only one responsible source)
- Urgent requirements (unusual/compelling urgency)
- National security exceptions
- Public interest determinations

**Approval thresholds:**
- ≤ $750K: Contracting Officer
- > $750K to $15M: Competition Advocate
- > $15M to $75M: Head of Procuring Activity (HPA)
- > $75M: Senior Procurement Executive

**What J&A must contain (FAR 6.303-2):**
1. Contracting activity and description
2. Statutory authority cited
3. Demonstration other sources can't meet need
4. Efforts to ensure competition in future
5. Market research conducted
6. Fair and reasonable price determination

**Competitor strategy:** J&As are FOIA-able. If you think competition was improperly restricted, request the J&A and evaluate for protest grounds.""",
        "rejected": "J&A is needed for sole source contracts. It justifies why they can't compete the work."
    },
    {
        "category": "rfp_analysis",
        "prompt": "How do I read a CPARS report and what ratings matter?",
        "chosen": """**CPARS = Contractor Performance Assessment Reporting System**

**Rating scale (worst to best):**
- Unsatisfactory (U) - Unacceptable; jeopardizes contract
- Marginal (M) - Minor problems; higher risk
- Satisfactory (S) - Meets requirements; adequate
- Very Good (VG) - Exceeds some; minor strengths
- Exceptional (E) - Exceeds most; significant strengths

**Evaluated areas:**
1. Quality of Product/Service
2. Schedule
3. Cost Control (cost-type only)
4. Management/Business Relations
5. Small Business Subcontracting (if applicable)
6. Regulatory Compliance (if applicable)

**What evaluators scrutinize:**
- Pattern across contracts (consistent S vs. variable)
- Recency (last 3 years weighted heavily)
- Relevance to current procurement
- Narrative comments (often more telling than ratings)
- Contractor response (did you rebut unfair ratings?)

**Critical insight:** One "Marginal" with good explanation < multiple "Satisfactory" with concerning narratives. Past performance evaluation is subjective—compelling narratives matter.

**Access:** Contractors see own reports in CPARS. Competitors' reports visible during eval only to government.""",
        "rejected": "CPARS ratings go from Unsatisfactory to Exceptional. Higher ratings are better for winning contracts."
    },
    {
        "category": "rfp_analysis",
        "prompt": "What's the difference between an IDIQ and a BPA?",
        "chosen": """**IDIQ = Indefinite Delivery/Indefinite Quantity Contract**

- Actual contract with negotiated terms
- Ceiling value and ordering period
- Task/delivery orders compete or direct award
- FAR Part 16.5 governs
- Minimum guaranteed (often nominal: $2,500)
- Used for: Large, complex, long-term requirements
- Examples: OASIS, Alliant 2, SEWP

**BPA = Blanket Purchase Agreement**

- Not a contract; a charge account mechanism
- Simplified acquisition method (FAR 13.303)
- No ceiling/minimum required
- Individual calls against BPA
- Used for: Recurring, small-dollar purchases
- Typically under SAT ($250K) per call
- Common for: Supplies, simple services

**Key distinctions:**

| Aspect | IDIQ | BPA |
|--------|------|-----|
| Contract? | Yes | No |
| Competition | At TO level or award | At establishment or call |
| Complexity | High | Low |
| Ceiling | Required | Optional |
| Protest rights | Yes (TO > $25M) | Limited |
| Admin burden | High | Low |

**Strategic use:** Win IDIQ for large opportunities; use BPAs for quick, repeat business with minimal overhead.""",
        "rejected": "IDIQ is a contract for ordering work over time. BPA is like a charge account for recurring purchases. Both are indefinite."
    },
    {
        "category": "rfp_analysis",
        "prompt": "How should I analyze the NAICS code selection in an RFP?",
        "chosen": """**NAICS = North American Industry Classification System**

Determines:
- Size standard (revenue or employee threshold)
- Set-aside eligibility
- Competition pool

**Analysis checklist:**

1. **Verify appropriateness:** Does NAICS match primary work?
   - IT services: 541512, 541511, 541519
   - Engineering: 541330, 541712
   - Management consulting: 541611, 541618
   - Professional services: 541990

2. **Check size standard impact:**
   - Your size vs. threshold
   - Competitors' likely size status
   - Affiliation rule implications

3. **Challenge if wrong:** File RFI before proposals due
   - FAR 19.303: SBA appeal process
   - Must show different NAICS is "clearly more appropriate"

4. **Strategic implications:**
   - Wrong NAICS may disqualify you
   - May open/close competition from small business
   - Affects subcontracting goals

**Red flag:** NAICS with very low size standard on complex requirement = potential bundling issue or wired procurement.

**Pro tip:** Check SAM.gov for recent awards under same NAICS to see who's competing and at what size.""",
        "rejected": "NAICS codes determine the size standard for the contract. Make sure you qualify under the selected code."
    },
    {
        "category": "rfp_analysis",
        "prompt": "What should I look for in the Contract Data Requirements List (CDRL)?",
        "chosen": """**CDRL = Contract Data Requirements List (DD Form 1423)**

Specifies deliverable data items on DoD contracts.

**Critical fields to analyze:**

1. **Data Item Description (DID):** Standard format reference
2. **Frequency:** One-time, monthly, quarterly, event-driven
3. **Distribution:** Who receives (CO, COR, PM, end users)
4. **Format:** Electronic, hard copy, specific software
5. **Approval timeline:** Government review period
6. **Rejection impact:** Resubmission requirements

**Pricing implications:**
- Count total deliverables across contract life
- Estimate labor hours per deliverable
- Factor in review/revision cycles (typically 2-3 iterations)
- Include subject matter expert time for technical CDRLs

**Hidden costs to capture:**
- Technical writing staff
- Configuration management
- Document control systems
- Review meetings (IPRs, PMRs)
- Formatting compliance labor

**Red flags:**
- Excessive CDRLs relative to contract value
- Short turnaround requirements
- Complex DIDs requiring specialized tools
- Ambiguous approval criteria

**Negotiation tip:** During discussions, propose reducing CDRL frequency or consolidating reports to reduce administrative burden for both parties.""",
        "rejected": "CDRLs list the deliverables. Make sure to include time for creating reports in your proposal."
    },
    {
        "category": "rfp_analysis",
        "prompt": "How do I interpret 'best value' tradeoff in Section M?",
        "chosen": """**Best Value Tradeoff = Price/technical balance where non-price factors can justify higher cost**

**Common formulations (look for exact language):**

1. **"Technical significantly more important than price"**
   - Premium for strong technical/PP acceptable
   - ~10-15% price premium often traded

2. **"Technical somewhat more important than price"**
   - Moderate premium acceptable (~5-10%)
   - Price becomes tiebreaker

3. **"Technical and price approximately equal"**
   - Limited tradeoff room
   - Approaches LPTA behavior

4. **"All factors combined significantly more important than price"**
   - Maximum technical emphasis
   - Large spreads tolerated

**Evaluator behavior:**

| Your Position | Strategy |
|--------------|----------|
| Strongest technical | Price competitively but don't undercut |
| Strong technical, higher cost | Justify value, quantify benefits |
| Weaker technical, lowest price | Maximize technical score, highlight price gap |
| Middle on both | Differentiate on discriminators |

**Key insight:** "Best value" doesn't mean lowest price. It means government can pay more for better value. Emphasize quantifiable benefits that justify cost differential.""",
        "rejected": "Best value means they consider both technical and price. Try to score well on both."
    },
    {
        "category": "rfp_analysis",
        "prompt": "What is a compliance matrix and how do I build one?",
        "chosen": """**Compliance Matrix = Traceability document mapping every RFP requirement to your proposal response**

**Structure:**

| Column | Content |
|--------|---------|
| Req ID | RFP paragraph reference (L.5.2.1) |
| Requirement | Verbatim "shall" statement |
| Section M Ref | Evaluation factor it supports |
| Proposal Volume | Technical, Management, Cost, etc. |
| Proposal Section | Where addressed (3.2.1) |
| Page | Exact page number |
| Compliance | Full / Partial / Exception |
| Notes | Clarifications, assumptions |

**Build process:**

1. **Extract requirements:** Parse Sections C, L, M for every shall/will/must
2. **Number sequentially:** Use RFP's own numbering
3. **Categorize:** Group by evaluation factor
4. **Assign ownership:** Writer responsible for each
5. **Track status:** Draft → Review → Final
6. **Verify bidirectionally:** Every req in matrix → proposal; every proposal claim → requirement

**Submission tip:** Many RFPs require compliance matrix as Volume I. Even if not required, include one—evaluators appreciate it.

**Common failure:** Matrix says "compliant" but proposal text doesn't explicitly state compliance. Evaluators verify—don't rely on matrix alone.""",
        "rejected": "A compliance matrix maps requirements to your proposal sections. Include one to show you meet all requirements."
    },

    # ============ PROPOSAL WRITING (12 items) ============
    {
        "category": "proposal_writing",
        "prompt": "How do I write an executive summary for a government proposal?",
        "chosen": """**Executive Summary structure (1-2 pages typically):**

**Paragraph 1: Theme statement + discriminators**
- Single sentence capturing your win strategy
- 3-4 key discriminators that differentiate you
- Why you're the best value choice

**Paragraph 2: Understanding + solution overview**
- Demonstrate you understand their mission/problem
- High-level solution approach
- Alignment with their objectives

**Paragraph 3: Proof points**
- Most relevant past performance (quantified)
- Key personnel credentials
- Relevant certifications/capabilities

**Paragraph 4: Benefits to Government**
- Quantified outcomes (cost savings, efficiency)
- Risk reduction
- Innovation/value-add beyond requirements

**Paragraph 5: Call to action**
- Confident commitment statement
- Transition readiness
- Partnership tone

**Writing rules:**
- Lead every paragraph with benefit, not feature
- No generic claims without proof
- Mirror their language from PWS/SOW
- Include 1-2 discriminating graphics
- No fluff—every word earns its place

**Anti-patterns:** Don't start with company history. Don't repeat RFP requirements back. Don't use 'we believe' or 'we feel.'""",
        "rejected": "Start with your company background, then describe your solution and why you're qualified. Keep it concise."
    },
    {
        "category": "proposal_writing",
        "prompt": "What is the STAR format for past performance write-ups?",
        "chosen": """**STAR = Situation, Task, Action, Result**

Structured format proving you've done similar work successfully.

**Template:**

**Situation (1-2 sentences)**
"[Client] faced [challenge/need] requiring [type of work] in a [relevant constraint] environment."

**Task (2-3 sentences)**
"[Company] was contracted to [specific scope]. The effort required [key capabilities relevant to current RFP]. Contract value: $X over Y years."

**Action (3-5 sentences)**
"We [specific actions taken]. Our approach included [methodologies/tools matching current RFP]. Key innovations: [differentiators]. We managed [team size] across [locations]."

**Result (2-3 sentences with metrics)**
"Delivered [quantified outcomes]: X% cost savings, Y% schedule improvement, Z% quality metric. Client feedback: [quote or CPARS summary]. Contract extended/expanded due to performance."

**Evaluation criteria alignment:**
- Match STAR scope to current RFP requirements
- Use same terminology as PWS/SOW
- Quantify everything possible
- Highlight transferable lessons learned

**Page budget:** ~1/2 to 1 page per reference. Quality over quantity—3 stellar relevant examples beat 6 mediocre ones.""",
        "rejected": "Describe the situation, what you did, and the results. Include metrics if you have them."
    },
    {
        "category": "proposal_writing",
        "prompt": "How do I write a technical approach section?",
        "chosen": """**Technical approach structure:**

**1. Understanding section (10-15% of page count)**
- Paraphrase requirements demonstrating comprehension
- Identify critical success factors
- Acknowledge risks/challenges
- Show you understand their mission context

**2. Approach overview (15-20%)**
- Solution architecture/framework
- Key methodology or process
- How approach maps to requirements
- Graphic: Solution overview diagram

**3. Detailed approach by task/requirement (50-60%)**
For each major PWS task:
- Restate requirement (brief)
- Describe your approach
- Explain why this approach works
- Reference relevant experience/proof
- Include task-specific graphic if helpful

**4. Innovation/value-add (10-15%)**
- Exceeds-requirements features
- Efficiency improvements
- Risk mitigations
- Technology advantages

**5. Risk management (5-10%)**
- Top 3-5 risks identified
- Mitigation strategies
- Contingency plans

**Writing discipline:**
- Lead with action verbs: "We will deploy..." not "Our approach is to..."
- Every claim needs proof (past performance, methodology, tool)
- Feature → Benefit → Proof pattern throughout
- Graphics: One per 2-3 pages minimum""",
        "rejected": "Explain your understanding of the work, describe your approach, and show how you'll meet the requirements."
    },
    {
        "category": "proposal_writing",
        "prompt": "How do I write effective proposal graphics?",
        "chosen": """**Proposal graphics principles:**

**Rule of thumb:** Graphic should be understandable in 10 seconds without reading surrounding text.

**Anatomy of effective graphic:**

1. **Action caption (above):** Complete sentence stating benefit
   - Good: "Integrated DevSecOps pipeline reduces deployment time by 40%"
   - Bad: "Figure 3: DevSecOps Pipeline"

2. **Visual content:** Diagram, flowchart, table, timeline
   - Use customer's colors/logo (if allowed)
   - Limit text inside graphic
   - Clear visual hierarchy

3. **Callouts:** 2-4 annotated highlights pointing to discriminators

4. **Source line (below):** Reference if data-driven

**Graphic types by purpose:**

| Purpose | Best Format |
|---------|-------------|
| Process | Flowchart, swim lane |
| Timeline | Gantt, milestone chart |
| Organization | Org chart with faces |
| Comparison | Table, Harvey balls |
| Architecture | Block diagram, layers |
| Location | Map with markers |
| Results | Bar/line chart with callouts |

**Production tips:**
- Design at 50% size—if readable, it works
- Consistent style guide across proposal
- Vector formats (SVG, EMF) for scaling
- Number figures in order of appearance

**Anti-pattern:** Decorative graphics without informational value waste page real estate.""",
        "rejected": "Use diagrams and charts to illustrate your approach. Make sure they're clear and labeled."
    },
    {
        "category": "proposal_writing",
        "prompt": "What are ghost themes and how do I use them?",
        "chosen": """**Ghosting = Subtly highlighting competitor weaknesses without naming them**

Raises doubts about competition while positioning your strengths.

**Technique:**

1. **Identify competitor vulnerabilities:**
   - Incumbent's known issues (CPARS, GAO findings, news)
   - New entrant's lack of experience
   - Competitor's resource constraints
   - Technology gaps in their approach

2. **Craft ghost statement pattern:**
   "[Risky approach] can lead to [negative outcome]. Unlike approaches that [weakness], our [discriminator] ensures [positive outcome]."

**Examples:**

| Competitor Weakness | Ghost Statement |
|--------------------|-----------------|
| High turnover | "Our 92% retention rate ensures continuity—critical when institutional knowledge drives mission success" |
| Offshore staff | "Our 100% U.S.-based cleared workforce eliminates ITAR/export control risks inherent in distributed delivery models" |
| Outdated tech | "Our cloud-native architecture avoids the technical debt and scalability limits of legacy approaches" |
| Small team | "With 500+ engineers, we absorb surge requirements without the delivery risk of capacity-constrained providers" |

**Rules:**
- Never name competitors
- State facts, not opinions
- Tie ghost to evaluable benefit
- Use sparingly (2-3 per volume max)
- Ensure your claim is true and provable""",
        "rejected": "Ghosting means subtly pointing out competitor weaknesses. Frame your strengths in ways that highlight their gaps."
    },
    {
        "category": "proposal_writing",
        "prompt": "How do I write a management approach section?",
        "chosen": """**Management approach structure:**

**1. Management philosophy (5-10%)**
- Governing principles
- Customer relationship approach
- Quality commitment
- Brief—evaluators care about execution

**2. Organizational structure (20-25%)**
- Org chart with names and faces
- Clear reporting lines to Government
- Roles and responsibilities matrix
- Span of control rationale
- Graphic: Program org chart

**3. Key personnel (25-30%)**
For each named position:
- Name, title, availability
- Relevant experience (2-3 bullets)
- Education/certifications
- Commitment level (% or FTE)
- Photo if allowed

**4. Staffing approach (15-20%)**
- Recruitment and retention plan
- Surge/flex capacity
- Subcontractor management
- Transition staffing (Day 1 readiness)

**5. Program management processes (20-25%)**
- Schedule management (tools, reporting)
- Risk management framework
- Quality assurance/control
- Communications plan (meetings, reports)
- Change management

**6. Transition plan (10-15%)**
- Phase-in timeline (typically 30-90 days)
- Knowledge transfer approach
- Parallel operations (if required)
- Day 1 deliverables

**Key differentiator:** Named key personnel with relevant experience. Generic "TBD" positions score lower.""",
        "rejected": "Describe your management structure, key personnel, and how you'll communicate with the government."
    },
    {
        "category": "proposal_writing",
        "prompt": "How do I handle a 'no bid' decision professionally?",
        "chosen": """**No-bid decision framework:**

**1. Document the decision (internal record)**
- Opportunity details (solicitation #, agency, value)
- Evaluation date and participants
- Bid/no-bid criteria scores
- Key factors driving decision
- Date communicated

**2. Notify relevant parties**
- Internal: Capture manager, BD lead, executives
- External (if teaming): Partners, potential subs
- Optional: Contracting Officer (relationship maintenance)

**3. CO notification (recommended for relationship):**

*Sample message:*
"Subject: [Company] No-Bid Notification - [Solicitation Number]

Dear [CO Name],

After careful evaluation, [Company] has decided not to submit a proposal for [Requirement Name]. While we remain committed to supporting [Agency], this opportunity does not align with our current capabilities and strategic focus.

We appreciate the opportunity to review the requirement and look forward to supporting future procurements.

Respectfully,
[Name/Title]"

**4. Lessons learned capture:**
- Why didn't this fit?
- What would make similar opportunities viable?
- Should we develop capabilities in this area?
- Teaming partners for future reference?

**5. Update pipeline/CRM:**
- Mark opportunity as no-bid
- Document reason code
- Set reminder for potential recompete""",
        "rejected": "If you decide not to bid, notify your team and optionally tell the contracting officer. Document why for future reference."
    },
    {
        "category": "proposal_writing",
        "prompt": "How do I write a win theme?",
        "chosen": """**Win theme = Core message repeated throughout proposal proving why you're best choice**

**Formula:** Discriminator + Proof + Benefit to Government

**Construction process:**

1. **Identify discriminators (3-5 maximum)**
   - What do you do better than competition?
   - What unique assets/experience do you have?
   - What risks do you mitigate others can't?

2. **Support with proof**
   - Past performance metrics
   - Key personnel credentials
   - Certifications/tools/facilities
   - Quantified results

3. **Translate to Government benefit**
   - Cost savings
   - Risk reduction
   - Mission success
   - Schedule confidence

**Theme statement template:**
"[Company]'s [discriminator] provides [Agency] with [benefit], as proven by [evidence]."

**Examples:**

| Discriminator | Proof | Benefit | Theme |
|--------------|-------|---------|-------|
| Cleared workforce | 150 TS/SCI staff | Immediate start | "Day-1 ready cleared workforce eliminates onboarding delays" |
| Local presence | Office in agency city | Responsive support | "On-site team provides same-day response to mission needs" |
| Incumbent knowledge | 5 years on predecessor | Reduced risk | "Unmatched program knowledge ensures seamless continuity" |

**Repetition strategy:**
- Executive summary: State all themes
- Each volume: Reinforce relevant themes
- Graphics: Visualize themes
- Headings: Incorporate theme language""",
        "rejected": "A win theme explains why you should win. It should be a clear message about your strengths that you repeat throughout."
    },
    {
        "category": "proposal_writing",
        "prompt": "What page count strategy should I use when there are strict limits?",
        "chosen": """**Page budget allocation strategy:**

**Step 1: Map pages to evaluation weight**

If Section M weights Technical (50%), Management (30%), Past Performance (20%):
- 50-page limit → ~25 tech, ~15 mgmt, ~10 PP

**Step 2: Reserve space for must-haves**

| Element | Pages | Notes |
|---------|-------|-------|
| Executive summary | 2 | Required opening |
| Compliance matrix | 2-3 | Cross-reference |
| Graphics | 1 per 3-4 pages | Visual proof |
| Transition plan | 2-3 | Usually required |
| Risk discussion | 1-2 | Shows maturity |

**Step 3: Allocate remaining by requirement complexity**

- Count "shall" statements per PWS section
- Weight by complexity/risk
- Allocate proportionally

**Step 4: Build page budget tracker**

| Section | Allocated | Draft | Over/Under |
|---------|-----------|-------|------------|
| 1.0 Understanding | 3 | 4 | -1 |
| 2.0 Technical | 20 | 18 | +2 |
| ... | ... | ... | ... |

**Maximizing density:**
- 11pt font minimum (10pt usually not allowed)
- Tables condense information vs. prose
- Bullet sub-points (a, b, c) vs. narrative
- Margin-to-margin graphics
- Remove widows/orphans

**Cardinal rule:** Never exceed page limits. Evaluators may not read overage. Some agencies disqualify.""",
        "rejected": "Allocate pages based on how important each section is. Leave room for graphics and make sure you don't exceed limits."
    },
    {
        "category": "proposal_writing",
        "prompt": "How do I write responses to evaluation notices or questions during discussions?",
        "chosen": """**Evaluation Notice (EN) / Deficiency Response Strategy:**

**EN Types:**
- **Deficiency:** Significant failing; must cure or risk elimination
- **Weakness:** Disadvantage; should address to improve score
- **Clarification:** Information request; straightforward response

**Response structure:**

**1. Header block:**
- EN/Clarification reference number
- Proposal section affected
- Page/paragraph reference in original

**2. Restate the issue (1-2 sentences):**
"The Government identified [paraphrase of issue] in our [section]."

**3. Direct response (body):**
- If correction: "We revise our approach to [new approach]."
- If clarification: "We clarify that [explanation]."
- If challenge: "We respectfully note [rationale] and offer [alternative]."

**4. Revised text (if changing proposal):**
Provide exact replacement language with markup:
- Deletions: ~~strikethrough~~
- Additions: **bold** or underline

**5. Confirmation:**
"This response addresses EN-[X] and does not affect other proposal sections except [cross-references if any]."

**Process discipline:**
- Respond to every EN—no exceptions
- Match their format requirements exactly
- Stay within page limits for responses
- Don't volunteer new information beyond question
- Track all revisions for final proposal update

**Risk:** Over-responding can create new deficiencies. Be precise and bounded.""",
        "rejected": "When responding to evaluation questions, directly address what they asked and provide any corrections needed."
    },
    {
        "category": "proposal_writing",
        "prompt": "What is the 'so what' test in proposal writing?",
        "chosen": """**"So what?" test = Validate every statement provides evaluator value**

**Application:** After writing any claim, ask "So what does this mean for the Government?"

**Before (fails test):**
"Our team has 50 years of combined experience."

**After (passes test):**
"Our team's 50 years of combined [relevant domain] experience means [Agency] gains proven solutions from Day 1—reducing the typical 6-month learning curve to zero."

**Framework: Feature → Benefit → Proof → So What**

| Component | Definition | Example |
|-----------|------------|---------|
| Feature | What you have | "24/7 help desk" |
| Benefit | Why it matters | "Issues resolved without delay" |
| Proof | Evidence it's true | "98.5% first-call resolution" |
| So What | Government impact | "Minimizes mission downtime" |

**Complete statement:**
"Our 24/7 help desk with 98.5% first-call resolution minimizes mission downtime—critical for [Agency]'s continuous operations requirement."

**Self-editing checklist:**
- [ ] Does this statement answer evaluator's "so what?"
- [ ] Is benefit stated explicitly (not implied)?
- [ ] Would this score points in Section M criteria?
- [ ] Is proof attached to claim?
- [ ] Could competitor make identical claim? (If yes, differentiate)

**Common offenders:** Company history, generic qualifications, motherhood statements ("committed to excellence"), requirement parroting.""",
        "rejected": "The 'so what' test means asking if your statements matter to the evaluator. Make sure every claim provides value."
    },
    {
        "category": "proposal_writing",
        "prompt": "How do I structure a proposal for an 8(a) sole source opportunity?",
        "chosen": """**8(a) Sole Source Proposal Structure:**

**Context:** Streamlined process; no competition. Focus: compliance and capability proof.

**Typical required volumes:**

**Volume I: Technical Capability**
- Company overview (8(a) certification, capabilities)
- Understanding of requirements
- Technical approach (abbreviated vs. competitive)
- Past performance (2-3 relevant, emphasize 8(a) work)
- Key personnel (qualifications, availability)

**Volume II: Management**
- Organizational structure
- Quality control approach
- Subcontracting plan (if applicable)
- SBA/8(a) compliance demonstration

**Volume III: Price/Cost**
- Pricing methodology
- Basis of estimate
- Subcontractor pricing (if >50% limitation concern)
- Rates substantiation

**Critical compliance elements:**

1. **Limitation on Subcontracting (LOC):**
   - Services: 50% of personnel costs by 8(a) firm
   - Supplies: 50% of manufacturing costs
   - Document compliance approach explicitly

2. **SBA approval:** Sole source requires SBA district office concurrence

3. **Fair and reasonable price:** Even sole source, government must justify price

**Differentiator vs. competitive:**
- Shorter page counts typical
- Less need for ghosting
- Focus on capability and compliance, not differentiation
- Relationship and prior performance with agency matters more

**Process timeline:** Often faster (30-60 days award after submission vs. 6-12 months competitive).""",
        "rejected": "For 8(a) sole source, you still need technical, management, and cost volumes. Focus on proving your capability since there's no competition."
    },

    # ============ FAR/DFARS (13 items) ============
    {
        "category": "far_dfars",
        "prompt": "What is FAR 52.212-4 and when does it apply?",
        "chosen": """**FAR 52.212-4: Contract Terms and Conditions—Commercial Products and Commercial Services**

**Applicability:** All contracts for commercial products/services under FAR Part 12.

**Key provisions:**

**1. Inspection/Acceptance**
- Government inspection at reasonable times/places
- Acceptance conclusive except for latent defects, fraud

**2. Assignment**
- No assignment without Contracting Officer consent
- Except: Assignment of claims under Assignment of Claims Act

**3. Disputes**
- Contract Disputes Act applies
- Must continue performance during disputes

**4. Payment**
- Net 30 days standard
- Prompt payment interest if Government late

**5. Invoice requirements**
- Proper invoice definition
- Required content elements

**6. Warranty**
- Commercial standard warranty applies
- Minimum: supplies free from defects for reasonable period

**7. Termination for Government's Convenience**
- Government may terminate any time
- Compensation: costs incurred + reasonable profit

**8. Termination for Cause**
- Government may terminate for contractor default
- Contractor liable for excess reprocurement costs

**Why it matters:** Most IT services contracts use commercial acquisition procedures. Know this clause—it's your baseline contract terms.

**Prescription:** FAR 12.301(b)(4)""",
        "rejected": "FAR 52.212-4 contains the standard terms for commercial contracts. It covers things like payment, disputes, and termination."
    },
    {
        "category": "far_dfars",
        "prompt": "Explain the Service Contract Act and its implications for pricing.",
        "chosen": """**Service Contract Act (SCA) — 41 U.S.C. § 6701-6707**

**Requirement:** Service contractors must pay prevailing wages/benefits determined by DOL for each locality.

**Applicability:**
- Service contracts >$2,500
- Principal purpose is furnishing services through service employees
- Performed in U.S.

**Key pricing implications:**

**1. Wage Determination (WD)**
- DOL publishes WD by locality and occupation
- Must use WD in place at time of award
- Minimum hourly rates for each labor category

**2. Fringe benefits requirements**
- Health & welfare rate (currently ~$4.98/hour)
- Paid vacation, holidays
- Pension contributions

**3. Price escalation**
- New WD issued annually
- FAR 52.222-43 allows adjustment for WD changes
- Build escalation into pricing or risk margin erosion

**Pricing model impact:**

| Component | Consideration |
|-----------|---------------|
| Direct labor | ≥ WD hourly rate per occupation |
| Fringe benefits | ≥ WD H&W requirement |
| Paid leave | Factor into availability rates |
| Escalation | Annual WD increases (3-5% typical) |

**Compliance risk:** Underpaying SCA employees = back wages + penalties + debarment exposure.

**Pro tip:** Calculate "fully-burdened SCA floor rate" early. If your cost structure can't meet it profitably, reconsider bidding.""",
        "rejected": "The Service Contract Act requires paying minimum wages set by DOL for service workers. Include these rates in your pricing."
    },
    {
        "category": "far_dfars",
        "prompt": "What is DFARS 252.204-7012 and what does CMMC have to do with it?",
        "chosen": """**DFARS 252.204-7012: Safeguarding Covered Defense Information and Cyber Incident Reporting**

**Requirements:**
1. Provide "adequate security" for Covered Defense Information (CDI)
2. Implement NIST SP 800-171 controls (110 controls)
3. Report cyber incidents within 72 hours
4. Preserve images for 90 days
5. Flow down to subcontractors with CDI

**CDI Definition:** Unclassified controlled technical information (CTI) or other information requiring safeguarding per CUI Registry.

**CMMC Connection:**

**CMMC = Cybersecurity Maturity Model Certification**

- Third-party assessment of NIST 800-171 compliance
- Replaces self-attestation model
- Phased rollout 2025-2028

**CMMC Levels (v2.0):**

| Level | Requirements | Assessment |
|-------|--------------|------------|
| Level 1 | 15 FCI controls | Self-assessment |
| Level 2 | 110 CUI controls (800-171) | C3PAO assessment |
| Level 3 | 110 + enhanced (800-172) | Government-led |

**Current state (2024-2025):**
- 7012 remains in effect
- CMMC rule finalizing
- Contracts will specify required level
- Assessment marketplace emerging

**Contractor action:**
1. Complete SSP (System Security Plan)
2. Document POA&Ms for gaps
3. SPRS score upload (-203 to 110 scale)
4. Prepare for C3PAO assessment when required

**Risk:** No CMMC certification = ineligible for DoD contracts requiring it.""",
        "rejected": "DFARS 252.204-7012 requires cybersecurity for defense information. CMMC is the certification program that will verify compliance."
    },
    {
        "category": "far_dfars",
        "prompt": "What is an Organizational Conflict of Interest (OCI) and how do I avoid it?",
        "chosen": """**OCI = Organizational Conflict of Interest (FAR Subpart 9.5)**

Situation where contractor's interests or access creates unfair advantage or bias.

**Three OCI types:**

**1. Unequal Access to Information**
- Access to nonpublic info providing competitive edge
- Example: Contractor supporting source selection accesses competitors' proposals

**2. Biased Ground Rules**
- Setting specifications/requirements then competing on work
- Example: Contractor writes SOW, then bids on resulting contract

**3. Impaired Objectivity**
- Financial interest conflicting with objective judgment
- Example: Evaluating systems including your own product

**Mitigation strategies:**

| OCI Type | Mitigation |
|----------|------------|
| Unequal access | Firewalls, non-disclosure, personnel exclusion |
| Biased ground rules | Exclusion from downstream competition |
| Impaired objectivity | Recusal, independent review, divestiture |

**Disclosure requirements:**
- Identify potential/actual OCIs in proposals
- Propose mitigation plans
- Update if circumstances change

**Avoidance planning:**
1. Before bidding advisory work: Assess downstream competition impact
2. Firewall policies: Document, train, enforce
3. Subcontractor OCIs: Flow down requirements
4. OCI review: Part of capture process

**Risk:** Undisclosed OCI = contract termination, suspension, debarment. Government can void awards for OCI post-award.

**Reference:** FAR 9.504, 9.505, 9.505-1 through 9.505-4""",
        "rejected": "An OCI happens when a contractor has conflicting interests. Disclose any potential conflicts and propose ways to mitigate them."
    },
    {
        "category": "far_dfars",
        "prompt": "What are the key differences between cost-reimbursement and fixed-price contracts?",
        "chosen": """**Contract Type Comparison:**

**Fixed-Price (FP)**

| Variant | Risk | Use Case |
|---------|------|----------|
| FFP (Firm Fixed Price) | Contractor bears all cost risk | Mature requirements, known scope |
| FPIF (FP Incentive) | Shared risk via target/ceiling | Development with cost motivation |
| FPEPA (FP Economic Adjustment) | Government bears economic factors | Long-term with volatile inputs |

**Cost-Reimbursement (CR)**

| Variant | Risk | Use Case |
|---------|------|----------|
| CPFF (Cost Plus Fixed Fee) | Government bears most risk | R&D, uncertain scope |
| CPIF (Cost Plus Incentive Fee) | Shared risk/reward | Performance-sensitive |
| CPAF (Cost Plus Award Fee) | Fee varies by subjective evaluation | Complex, behavior-driven |

**Key differences:**

| Dimension | Fixed-Price | Cost-Reimbursement |
|-----------|-------------|-------------------|
| Price certainty | Known at award | Estimated; actual costs reimbursed |
| Risk allocation | Contractor | Government |
| Profit motivation | Max profit by cost efficiency | Fee earned regardless |
| Admin burden | Lower | Higher (audit, allowability) |
| Accounting | Standard | CAS compliance required |
| Overrun impact | Contractor loss | Government funds more |
| Termination | Contractor keeps profit to date | Fee proportional |

**Selection factor:** Requirements maturity. Immature scope + FFP = contractor eats overruns or compromises quality.

**FAR guidance:** FAR 16.1 (types), FAR 16.2 (FP), FAR 16.3 (CR)""",
        "rejected": "Fixed-price means you get paid a set amount regardless of costs. Cost-reimbursement means the government pays your actual costs plus a fee."
    },
    {
        "category": "far_dfars",
        "prompt": "What is the Limitation on Subcontracting clause and how do I comply?",
        "chosen": """**Limitation on Subcontracting — FAR 52.219-14 / 13 CFR 125.6**

**Purpose:** Ensure small business set-aside beneficiaries perform meaningful portion of work.

**Thresholds (% of contract value):**

| Contract Type | Prime Must Perform | May Subcontract |
|---------------|-------------------|-----------------|
| Services | ≥50% labor costs | ≤50% |
| Supplies (manufacturing) | ≥50% manufacturing costs | ≤50% |
| Supplies (non-manufacturer) | N/A | Supply of small business manufacturer |
| General construction | ≥15% labor costs | ≤85% |
| Specialty construction | ≥25% labor costs | ≤75% |

**Calculation basis:**
- **Services:** Amount paid for personnel (not materials, ODCs)
- **Supplies:** Cost of manufacturing (not components purchased)

**Compliance mechanics:**

1. **Track labor costs by performer**
   - Prime employees vs. subcontractor employees
   - By-task tracking recommended

2. **Joint venture rules**
   - Populated JV: Each partner's work counts toward prime
   - Unpopulated: Only managing partner's work counts

3. **Similarly situated subcontractor exception**
   - Sub with same small business status
   - Work performed counts toward prime's percentage

**Compliance template:**

| Category | Prime | Sub | % Prime |
|----------|-------|-----|---------|
| Direct labor | $500K | $400K | 55.6% ✓ |

**Risk:** Non-compliance = contract termination + penalties + referral to SBA + potential fraud investigation.""",
        "rejected": "The Limitation on Subcontracting requires small businesses to perform a certain percentage of the work themselves instead of subcontracting it all."
    },
    {
        "category": "far_dfars",
        "prompt": "What is the Truth in Negotiations Act (TINA) and when does it apply?",
        "chosen": """**TINA = Truth in Negotiations Act (41 U.S.C. § 3501-3509)**

Requires contractors to submit certified cost or pricing data for negotiated contracts.

**Threshold:** >$2M (adjusted annually for inflation)

**Certified Cost or Pricing Data = (FAR 15.406-2)**

"All facts that, as of the date of price agreement, prudently expect to significantly affect price negotiations."

**Includes:**
- Vendor quotes
- Labor rates and projections
- Historical costs
- Make-or-buy decisions
- Known cost reductions
- Changes in production methods
- Management decisions affecting cost

**Certification language:** "The cost or pricing data are accurate, complete, and current as of [date]."

**TINA Exemptions:**

| Exemption | Rationale |
|-----------|-----------|
| Adequate price competition | Market established price |
| Commercial item | Catalog/market prices |
| Price set by law/regulation | Utility rates, standard commercial |
| Waiver by HCA | Exceptional circumstances |

**Defective Pricing:**

If certified data was inaccurate, incomplete, or noncurrent AND caused overstated price:

- Government entitled to price reduction + interest
- May pursue False Claims Act damages (treble)
- Potential debarment

**Compliance:**
1. Sweep all cost sources before certification date
2. Disclose anything affecting price
3. Maintain audit trail
4. DCAA audit likely for large contracts

**FAR reference:** FAR 15.403, 15.406""",
        "rejected": "TINA requires submitting cost data for large contracts to ensure pricing is fair. You certify the data is accurate or risk penalties."
    },
    {
        "category": "far_dfars",
        "prompt": "What is FAR 15.306 and how do competitive range discussions work?",
        "chosen": """**FAR 15.306: Exchanges with Offerors After Receipt of Proposals**

**Process flow:**

1. **Clarifications (FAR 15.306(a))**
   - Limited exchanges to clarify proposal
   - No opportunity to revise
   - Used when award without discussions appropriate

2. **Communications (FAR 15.306(b))**
   - Address minor issues (resolve clerical errors, past performance info)
   - Before competitive range determination
   - Not discussions

3. **Competitive Range Determination (FAR 15.306(c))**
   - Government identifies most highly rated proposals
   - Based on rating against all factors
   - Must notify excluded offerors in writing

4. **Discussions (FAR 15.306(d))**
   - Meaningful negotiations with competitive range offerors
   - Must address deficiencies, significant weaknesses
   - May discuss other aspects (general areas of concern)
   - Conducted by Contracting Officer (or delegate)

5. **Final Proposal Revisions (FAR 15.307)**
   - Common cutoff date for all competitive range offerors
   - Last chance to revise price, technical
   - No further discussions after FPR submission

**Discussion rules:**
- Cannot reveal competitor's pricing
- Cannot reveal competitor's technical approach
- Cannot conduct auction
- Must treat offerors fairly and equally
- Must provide same opportunity to revise

**Protest risk:** Unequal discussions = bid protest ground. Disparate treatment actionable at GAO.

**Strategy:** Anticipate discussions. Prepare responses to likely deficiencies before notification.""",
        "rejected": "FAR 15.306 covers how the government communicates with bidders after proposals are in. Discussions let you fix deficiencies before final award."
    },
    {
        "category": "far_dfars",
        "prompt": "What is the Anti-Deficiency Act and why should contractors care?",
        "chosen": """**Anti-Deficiency Act (ADA) — 31 U.S.C. §§ 1341, 1342, 1517**

**Purpose:** Prohibits government officials from:
1. Making obligations exceeding appropriations
2. Accepting voluntary services
3. Spending in advance of appropriations

**Why contractors care:**

**1. Funding ceiling enforcement**
- Contracts have funded ceilings
- Government cannot legally obligate beyond available funds
- "Subject to availability of funds" language common

**2. Work beyond scope risk**
- Work outside contract scope may be unfunded
- Contractor proceeds at own risk
- Recovery uncertain without proper authorization

**3. Options and modifications**
- Options require new funding obligation
- Mods increasing scope need funding before work
- Letters of intent ≠ funding authority

**Contractor protections:**

| Scenario | Risk | Protection |
|----------|------|------------|
| Work under funded ceiling | Low | Contract covers |
| Unfunded change order | Medium | Constructive change claim |
| Unauthorized work | High | May not recover |
| Government shutdown | High | Stop work, claim costs |

**Best practices:**
1. Track obligated vs. funded amounts
2. Never accept verbal direction to exceed funding
3. Get modification before exceeding ceiling
4. Document all government direction
5. Know your COR's authority limits

**Recovery for ADA violations:** Limited. Government may ratify unauthorized commitments (FAR 1.602-3), but not guaranteed.

**Reference:** FAR 32.702, 32.703-2""",
        "rejected": "The Anti-Deficiency Act prevents the government from spending more than appropriated. Contractors should make sure work is properly funded."
    },
    {
        "category": "far_dfars",
        "prompt": "What is the Contract Disputes Act and how do I file a claim?",
        "chosen": """**Contract Disputes Act (CDA) — 41 U.S.C. §§ 7101-7109**

**Purpose:** Provides process for resolving contract disputes between contractors and government.

**Claim requirements:**

1. **Written demand**
   - Specific sum or non-monetary relief
   - Submitted to Contracting Officer

2. **Certification (if >$100K):**
   - Claim made in good faith
   - Supporting data accurate and complete
   - Amount requested accurately reflects contract adjustment believed owed
   - Signed by authorized official

3. **Submit to Contracting Officer**
   - CO has 60 days to issue decision (or state when decision expected)

**CO's Final Decision:**
- Must be in writing
- State reasons for decision
- Inform contractor of appeal rights
- Deemed denial if no decision in 60 days (contractor may appeal)

**Appeal options:**

| Forum | Timeline | Binding? |
|-------|----------|----------|
| Board of Contract Appeals (ASBCA/CBCA) | 90 days from CO decision | Yes |
| Court of Federal Claims | 12 months from CO decision | Yes |
| ADR (with consent) | Anytime | Negotiable |

**Interest:**
- CDA entitles contractor to interest from date claim submitted
- Current CDA rate: ~3-5% annually

**Continuing performance:**
- Must continue performance during dispute (FAR 52.233-1)
- Cannot stop work pending resolution

**Best practice:** Document contemporaneously. Detailed records essential for claim success.

**FAR reference:** FAR Subpart 33.2""",
        "rejected": "The Contract Disputes Act lets contractors file claims against the government. Submit a written claim to the CO and appeal if denied."
    },
    {
        "category": "far_dfars",
        "prompt": "What are Contractor Business Systems and why do they matter for DoD contracts?",
        "chosen": """**Contractor Business Systems — DFARS 252.242-7005**

**Definition:** Six systems subject to government audit and approval for certain DoD contracts.

**The six systems:**

| System | Criteria | Audit |
|--------|----------|-------|
| Accounting | Accumulate, segregate costs; GAAP/CAS compliant | DCAA |
| Estimating | Consistent, accurate cost estimates | DCAA |
| Purchasing | Price reasonably, FAR flow-downs | DCMA |
| MMAS (Material Mgmt & Accounting) | Track, control material costs | DCMA |
| EVMS (Earned Value) | Project cost/schedule management | DCMA |
| Property | Track, control government property | DCMA |

**Applicability:**
- CAS-covered contracts >$50M
- MMAS: Production contracts with material costs
- EVMS: Development contracts >$20M
- Property: Any contract with GFP

**Significant deficiency = Material weakness affecting:**
- Cost accumulation reliability
- System output integrity
- Data representation to Government

**Business system withholds:**

If system has significant deficiencies:
- Government withholds up to 5% of payments per deficient system
- Max total withhold: 10% across all systems
- Released when deficiencies corrected

**Compliance roadmap:**

1. **Document system policies/procedures**
2. **Self-audit against DFARS criteria**
3. **Remediate gaps before DCAA/DCMA audit**
4. **Maintain evidence of compliance**
5. **Respond to auditor findings promptly**

**Risk:** System disapproval impacts all DoD contracts, not just the audited one. Can affect ability to win new work.""",
        "rejected": "DoD audits six contractor business systems. If you have significant deficiencies, the government can withhold payments until fixed."
    },
    {
        "category": "far_dfars",
        "prompt": "What is a small business subcontracting plan and when is it required?",
        "chosen": """**Small Business Subcontracting Plan — FAR 52.219-9**

**Requirement:** All federal contracts >$750K ($1.5M for construction) awarded to other-than-small businesses must include a subcontracting plan.

**Plan elements (FAR 19.704):**

1. **Goals (% of subcontract dollars):**
   - Small Business (SB)
   - Small Disadvantaged Business (SDB)
   - Women-Owned Small Business (WOSB)
   - HUBZone Small Business
   - Service-Disabled Veteran-Owned (SDVOSB)
   - Veteran-Owned Small Business (VOSB)

2. **Total subcontracting dollars** (base for percentages)

3. **Description of efforts:**
   - Outreach methods
   - Source identification process
   - Internal advocacy program

4. **Administrator designation** (small business liaison officer)

5. **Reporting commitments:**
   - ISR (Individual Subcontract Report) — semi-annual
   - SSR (Summary Subcontract Report) — annual
   - Both in eSRS (Electronic Subcontracting Reporting System)

**Government-wide goals (current):**
- SB: 23%
- SDB: 5%
- WOSB: 5%
- HUBZone: 3%
- SDVOSB: 3%

**Evaluation factor:**
- Subcontracting plan is rated in competitive proposals
- Good faith effort matters
- Can be evaluation discriminator

**Non-compliance consequences:**
- Liquidated damages: Difference between goals and actual
- Past performance impact
- Debarment for willful failure

**FAR reference:** FAR 19.702, 19.704, 19.705""",
        "rejected": "Large businesses need a subcontracting plan for big contracts showing how much they'll subcontract to small businesses."
    },
    {
        "category": "far_dfars",
        "prompt": "What is the Procurement Integrity Act and what activities does it prohibit?",
        "chosen": """**Procurement Integrity Act (PIA) — 41 U.S.C. § 2101-2107**

**Prohibitions:**

**1. Obtaining/disclosing contractor bid or proposal information:**
- Cost/pricing data
- Technical approach
- Proposal content

**2. Obtaining/disclosing source selection information:**
- Evaluation criteria weighting
- Competitive range decisions
- Technical scores/rankings
- Source selection recommendation

**Before award — applies to:**
- Government personnel
- Contractors
- Subcontractors
- Consultants

**Post-employment restrictions (FAR 3.104-3):**

| Person | Restriction | Duration |
|--------|-------------|----------|
| Procurement official | Compensation ban from winning contractor | 1 year post-participation |
| Senior officials | Cannot accept compensation if personally/substantially involved | 1 year |
| All officials | Cannot switch to contractor on same procurement while pending | Until award |

**Violations:**

| Penalty | Civil | Criminal |
|---------|-------|----------|
| Individual | $100K per violation | 5 years imprisonment |
| Organization | $1M per violation | N/A |
| Contract impact | Cancellation, rescission | N/A |

**Compliance requirements:**

1. **Training:** Annual for procurement personnel
2. **Certification:** Offerors certify (FAR 52.203-8)
3. **Reporting:** Must report suspected violations

**Contractor action items:**
- Train BD/capture personnel
- Document all government interactions
- Prohibit inappropriate discussions with government employees
- Report violations immediately to CO

**FAR reference:** FAR 3.104""",
        "rejected": "The Procurement Integrity Act prohibits sharing confidential bid information and restricts post-government employment. Violations have serious penalties."
    },

    # ============ PRICING (12 items) ============
    {
        "category": "pricing",
        "prompt": "How do I build a labor rate for a government proposal?",
        "chosen": """**Labor rate buildup (cost-type contract example):**

**Direct labor rate components:**

| Component | Calculation | Example |
|-----------|-------------|---------|
| Base salary | Annual / 2,080 hours | $120,000 / 2,080 = $57.69/hr |
| Fringe benefits | % of salary (typically 25-40%) | 30% × $57.69 = $17.31/hr |
| **Loaded direct rate** | Base + fringe | **$75.00/hr** |

**Indirect rate application:**

| Rate Pool | Typical Range | Applied To |
|-----------|---------------|------------|
| Overhead (OH) | 80-150% | Direct labor |
| G&A | 8-20% | All costs |
| Facilities capital cost of money | 0.5-1% | If claimed |

**Full buildup example:**

| Element | Rate/% | Amount |
|---------|--------|--------|
| Direct labor | - | $75.00 |
| Overhead (100%) | 100% | $75.00 |
| Subtotal | - | $150.00 |
| G&A (12%) | 12% | $18.00 |
| **Total cost** | - | **$168.00** |
| Fee (8%) | 8% | $13.44 |
| **Billing rate** | - | **$181.44/hr** |

**Fixed-price billing rate:**
Include profit margin instead of fee; typically higher (10-15%).

**Rate substantiation:**
- Payroll records (base salary)
- Benefits summary (fringe)
- Audited indirect rates (DCAA-approved or forward pricing)
- Fee/profit per DFARS weighted guidelines or negotiated""",
        "rejected": "Add up salary, benefits, overhead, G&A, and profit to get your billing rate. Use your company's actual rates."
    },
    {
        "category": "pricing",
        "prompt": "What are indirect rates and how do I establish them?",
        "chosen": """**Indirect rates = Costs not directly attributable to a single contract**

**Common indirect pools:**

**1. Fringe Benefits**
- Health insurance, retirement, PTO, payroll taxes
- Base: Direct labor dollars
- Typical: 25-40%

**2. Overhead (OH)**
- Indirect labor, facilities, IT, project support
- Base: Direct labor dollars
- Typical: 80-150%

**3. General & Administrative (G&A)**
- Executive salaries, HR, legal, accounting, BD
- Base: Total costs (or value-added)
- Typical: 8-20%

**Establishing rates:**

**Step 1: Segregate costs**
- Chart of accounts by cost pool
- Clear pool definitions

**Step 2: Select allocation base**
- Consistent with cost behavior
- FAR 31 compliant

**Step 3: Calculate rate**
```
Indirect Rate = Total Pool Costs / Allocation Base
```

**Step 4: Set billing rates**
- Historical (audited prior year)
- Forward pricing (projected current/out-year)
- Provisional (government-approved pending audit)

**DCAA considerations:**
- DCAS Form 1547 Weighted Guidelines
- ICE model (Incurred Cost Electronically)
- Must demonstrate allowability, allocability, reasonableness

**Startup companies:**
- Use provisional rates until history established
- Government may cap rates pending audit
- Focus on allowability from Day 1

**FAR reference:** FAR 31.203 (indirect costs), FAR 42.7 (rate administration)""",
        "rejected": "Indirect rates cover overhead costs like facilities and administration. Calculate by dividing indirect costs by the allocation base."
    },
    {
        "category": "pricing",
        "prompt": "How do I calculate wrap rate for a T&M contract?",
        "chosen": """**Wrap rate = Fully-loaded billing rate for T&M contracts**

**T&M structure (FAR 16.601):**
- Fixed hourly rates by labor category
- Materials at cost (+ handling fee if allowed)

**Wrap rate calculation:**

| Component | Formula | Example |
|-----------|---------|---------|
| Direct labor (DL) | Base wage | $60.00 |
| Fringe (F) | DL × fringe rate | $60 × 30% = $18.00 |
| Overhead (OH) | (DL + F) × OH rate | $78 × 100% = $78.00 |
| Subtotal | DL + F + OH | $156.00 |
| G&A | Subtotal × G&A rate | $156 × 15% = $23.40 |
| Cost | Subtotal + G&A | $179.40 |
| Profit | Cost × profit % | $179.40 × 10% = $17.94 |
| **Wrap rate** | Cost + Profit | **$197.34/hr** |

**Escalation:**
- Multi-year contracts: Apply annual escalation (3-4%)
- Year 1: $197.34, Year 2: $203.26, Year 3: $209.36

**Common wrap rate multipliers:**

| Contract type | Typical multiplier |
|---------------|-------------------|
| Small business | 1.8 - 2.3x base salary |
| Large contractor | 2.2 - 3.0x base salary |
| FFRDC/SETA | 2.8 - 3.5x base salary |

**Verification:** $197.34 / $60.00 = 3.29x multiplier

**T&M risk:** Rates are fixed regardless of actual costs. Underbid = margin erosion. Build in contingency or escalation caps.""",
        "rejected": "The wrap rate includes salary, fringe, overhead, G&A, and profit. Multiply your base salary by about 2-3x for a typical wrap rate."
    },
    {
        "category": "pricing",
        "prompt": "What is the difference between allowable and unallowable costs?",
        "chosen": """**FAR Part 31: Contract Cost Principles**

**Allowable costs must be:**
1. **Reasonable** — Prudent person would incur at that amount
2. **Allocable** — Assignable to contract based on benefit received
3. **In accordance with GAAP/CAS** — Proper accounting
4. **Not specifically unallowable** — Not on the FAR 31.205 list

**Common UNALLOWABLE costs (FAR 31.205):**

| Category | FAR Reference | Status |
|----------|---------------|--------|
| Advertising (general) | 31.205-1 | Unallowable |
| Alcoholic beverages | 31.205-51 | Always unallowable |
| Bad debts | 31.205-3 | Unallowable |
| Contributions/donations | 31.205-8 | Unallowable |
| Entertainment | 31.205-14 | Unallowable |
| Fines/penalties | 31.205-15 | Unallowable |
| Interest expense | 31.205-20 | Generally unallowable |
| Lobbying | 31.205-22 | Unallowable |
| Organization costs | 31.205-27 | Unallowable |
| Selling costs | 31.205-38 | Limited allowability |

**Partially allowable examples:**

| Cost | Allowable Portion |
|------|-------------------|
| B&P (bid and proposal) | With limitations |
| IR&D (R&D) | With limitations |
| Professional services | If reasonable |
| Recruiting | Reasonable costs |
| Travel | Per JTR/FTR limits |

**Compliance imperative:**
- Segregate unallowables in accounting system
- Never charge to government contracts
- DCAA audit will identify and disallow

**Penalty:** Unallowable costs included = repayment + potential fraud referral""",
        "rejected": "Allowable costs can be charged to government contracts. Unallowable costs like entertainment and alcohol cannot be charged."
    },
    {
        "category": "pricing",
        "prompt": "How do I calculate Other Direct Costs (ODCs)?",
        "chosen": """**ODCs = Direct costs other than labor that are directly attributable to the contract**

**Common ODC categories:**

| Category | Examples | Estimating Method |
|----------|----------|-------------------|
| Travel | Airfare, hotel, per diem, rental car | Trip count × avg cost |
| Materials | Hardware, software, supplies | Bill of materials + quotes |
| Subcontracts | Task-specific subs | Quotes or estimates |
| Equipment | Non-capital purchases | Catalog/vendor pricing |
| Other | Shipping, licenses, certifications | Historical or quotes |

**ODC buildup process:**

**Step 1: Extract requirements**
- PWS travel requirements (trips/year, locations)
- Materials/equipment specified
- Deliverable-driven needs

**Step 2: Estimate quantities**

| Item | Qty | Unit Cost | Extended |
|------|-----|-----------|----------|
| DC travel (roundtrip) | 12 | $1,800 | $21,600 |
| Laptops | 5 | $2,000 | $10,000 |
| Software licenses | 10 | $500/yr | $5,000 |
| Training | 3 | $3,000 | $9,000 |
| **Total ODCs** | | | **$45,600** |

**Step 3: Apply G&A (if applicable)**
- ODCs typically subject to G&A
- Some contracts: material handling rate instead

**Step 4: Apply fee (if cost-type)**
- ODCs may or may not earn fee (check Section B)

**Common mistakes:**
- Forgetting travel taxes/fees
- Underestimating inflation on multi-year
- Missing software renewal costs
- Not including subcontractor fee in their price

**Documentation:** Keep basis of estimate for each line item (quotes, historical data, rationale).""",
        "rejected": "ODCs include travel, materials, and equipment. List what you need, get quotes, and add them up. Include in your cost proposal."
    },
    {
        "category": "pricing",
        "prompt": "What is price realism analysis and how do I prepare for it?",
        "chosen": """**Price realism = Government assessment whether proposed prices are realistic for work to be performed**

**Purpose:** Evaluate cost risk for cost-type contracts and performance risk for all types.

**When performed:**
- All cost-reimbursement contracts
- FP contracts where unrealistically low prices indicate misunderstanding
- T&M/LH contracts (labor rate reasonableness)

**What Government examines:**

| Element | Realism Check |
|---------|---------------|
| Labor mix | Appropriate categories for work |
| Labor hours | Sufficient to complete scope |
| Labor rates | Consistent with market/contractor history |
| Indirect rates | Consistent with audited/forward pricing |
| ODCs | Adequate for requirements |
| Subcontractor pricing | Appropriate for sub scope |

**Red flags triggering realism concerns:**

- Price significantly below IGCE
- Price far below competitive range median
- Labor mix too junior for complexity
- Hours insufficient for deliverables
- Rates well below market for skill level

**Preparation strategies:**

1. **Document basis of estimate**
   - Labor hours per task
   - Staffing rationale by category
   - Historical reference data

2. **Support rate substantiation**
   - Payroll data for direct rates
   - Approved indirect rates
   - Industry comparables

3. **Ensure internal consistency**
   - Technical approach matches cost assumptions
   - Risk register reflects contingency in price

4. **Price-to-win cautiously**
   - Too aggressive = realism adjustment upward
   - May be scored as higher risk

**FAR reference:** FAR 15.404-1(d)""",
        "rejected": "Price realism checks if your pricing is realistic for the work. Make sure your hours and rates make sense for what you're proposing."
    },
    {
        "category": "pricing",
        "prompt": "How do I calculate level of effort (LOE) for a proposal?",
        "chosen": """**LOE calculation = Estimating labor hours needed to accomplish contract requirements**

**Bottom-up approach (preferred):**

**Step 1: Decompose work**
- Map each PWS task to WBS element
- Identify deliverables per task
- List activities per deliverable

**Step 2: Estimate per activity**

| Activity | Complexity | Hrs/Occurrence | Occurrences | Total |
|----------|------------|----------------|-------------|-------|
| Status reports | Low | 4 | 52/yr | 208 |
| Sprint planning | Med | 8 | 26/yr | 208 |
| Code development | High | 40 | 50 features | 2,000 |
| Testing | Med | 8 | 50 features | 400 |
| PMR preparation | Med | 16 | 4/yr | 64 |
| **Subtotal** | | | | **2,880** |

**Step 3: Apply productivity factors**

| Factor | Adjustment |
|--------|------------|
| Learning curve (new work) | +10-20% |
| Government interaction | +5-10% |
| Rework/revision | +5-15% |
| Leave/absence | Already in availability |

**Step 4: Allocate to labor categories**

| Category | % of Effort | Hours |
|----------|-------------|-------|
| Senior Engineer | 30% | 864 |
| Engineer | 50% | 1,440 |
| Junior Engineer | 20% | 576 |
| **Total** | 100% | **2,880** |

**Step 5: Calculate FTEs**
```
FTEs = Total Hours / Available Hours per Year
Available = 2,080 - PTO - Holiday - Training ≈ 1,880
2,880 / 1,880 = 1.53 FTE
```

**Validation:** Compare to similar completed contracts, IGCE guidance, team input.""",
        "rejected": "Break down the work into tasks, estimate hours for each, and assign to labor categories. Add some buffer for meetings and rework."
    },
    {
        "category": "pricing",
        "prompt": "What is the difference between direct and indirect labor?",
        "chosen": """**Direct labor = Time charged directly to a specific contract for contract work**

**Characteristics:**
- Identifiable to single contract
- Performing contracted scope
- Billable to customer
- Tracked by charge code/project

**Examples:**
- Engineer coding for Contract A
- Analyst writing deliverable for Contract B
- Tech support resolving tickets for Contract C

---

**Indirect labor = Time supporting multiple contracts or general business operations**

**Characteristics:**
- Not attributable to single contract
- Supporting infrastructure
- Charged to overhead or G&A pools
- Allocated across contracts via indirect rates

**Categories:**

| Pool | Examples |
|------|----------|
| Overhead | Project managers managing multiple projects, QA review across contracts, indirect technical support |
| G&A | Executive management, HR, finance, legal, BD, contracts administration |
| Fringe | PTO, holidays, sick time (for direct labor employees) |

---

**Cost impact comparison:**

| Aspect | Direct | Indirect |
|--------|--------|----------|
| Charging | Specific contract | Pool allocation |
| Revenue | Generates billing | Recovered through rates |
| Utilization | Higher = more revenue | Necessary but minimize |
| Tracking | Timesheet per contract | Timesheet to pool |

**Key ratio: Utilization rate**
```
Utilization = Direct Labor Hours / Total Available Hours
Target: 75-90% for billable staff
```

**Compliance:** Proper timekeeping critical. Mischarging direct vs. indirect = audit finding, potential fraud.""",
        "rejected": "Direct labor is work on a specific contract that gets billed. Indirect labor supports the company generally and is charged to overhead."
    },
    {
        "category": "pricing",
        "prompt": "How do I price subcontractors in my proposal?",
        "chosen": """**Subcontractor pricing approach:**

**Step 1: Define subcontract scope**
- Specific tasks/deliverables
- Period of performance
- Labor categories needed
- ODCs required

**Step 2: Obtain subcontractor proposal**
- Request formal quote
- Match your proposal format requirements
- Include certification requirements
- Set deadline before your submission

**Step 3: Evaluate sub pricing**

| Check | Assessment |
|-------|------------|
| Rate reasonableness | Compare to market, your rates, GSA schedule |
| Hours realism | Sufficient for scope? |
| Indirect rates | Consistent with their history? |
| Fee/profit | Reasonable for risk? |

**Step 4: Include in prime cost proposal**

| Element | Treatment |
|---------|-----------|
| Sub labor | Direct cost (pass-through) |
| Sub ODCs | Direct cost (pass-through) |
| Sub fee | Part of sub total (allowable) |
| Subcontract admin | May be prime indirect or direct |
| Prime G&A | Applied to sub costs (check contract) |
| Prime fee | Applied to sub costs (check contract) |

**Example buildup:**

| Line | Amount |
|------|--------|
| Subcontractor total price | $500,000 |
| Prime G&A on sub (12%) | $60,000 |
| **Subtotal** | $560,000 |
| Prime fee on sub (8%) | $44,800 |
| **Total to Government** | **$604,800** |

**Consent requirements (FAR 44):**
- Subcontracts >$750K or cost-type: CO consent required
- Submit: Sub's cost proposal, competition documentation, price analysis

**Risk:** Sub cost growth = your problem on FFP contracts. Build contingency or cost ceilings.""",
        "rejected": "Get quotes from your subs, add your G&A and fee on top, and include in your cost volume. Get consent if required."
    },
    {
        "category": "pricing",
        "prompt": "What are escalation rates and how do I apply them in multi-year pricing?",
        "chosen": """**Escalation = Annual cost increases applied to multi-year contracts**

**Components to escalate:**

| Element | Typical Annual Rate | Source |
|---------|---------------------|--------|
| Direct labor | 3-4% | Market surveys, BLS data |
| Fringe benefits | 4-6% | Benefits cost trends |
| Overhead | 2-3% | Company projections |
| Materials | 2-4% | Producer Price Index |
| Travel | 2-3% | GSA per diem trends |

**Application methods:**

**Method 1: Compound escalation**
```
Year N Rate = Base Rate × (1 + escalation)^(N-1)

Year 1: $100.00
Year 2: $100.00 × 1.03 = $103.00
Year 3: $100.00 × 1.03² = $106.09
Year 4: $100.00 × 1.03³ = $109.27
Year 5: $100.00 × 1.03⁴ = $112.55
```

**Method 2: Economic Price Adjustment (EPA) clause**
- FAR 52.216-2 through 52.216-4
- Tied to published index (CPI, ECI)
- Protects both parties from unexpected changes

**Pricing table example:**

| Year | Base Hours | Escalation | Hourly Rate | Extended |
|------|------------|------------|-------------|----------|
| 1 | 10,000 | 1.000 | $150.00 | $1,500,000 |
| 2 | 10,000 | 1.030 | $154.50 | $1,545,000 |
| 3 | 10,000 | 1.061 | $159.15 | $1,591,500 |
| 4 | 10,000 | 1.093 | $163.95 | $1,639,500 |
| 5 | 10,000 | 1.126 | $169.00 | $1,690,000 |
| **Total** | **50,000** | | | **$7,966,000** |

**Government expectations:**
- Justify escalation rates with market data
- Apply consistently across proposal
- May negotiate lower rates during discussions

**Risk:** Under-escalating = margin erosion on out-years. Document basis of estimate.""",
        "rejected": "Apply 3-4% annual increases to your rates for each year of the contract. Compound the percentages for accurate calculations."
    },
    {
        "category": "pricing",
        "prompt": "What is a basis of estimate (BOE) and what should it contain?",
        "chosen": """**BOE = Basis of Estimate: Documentation substantiating every cost element**

**Purpose:**
- Supports price reasonableness
- Audit trail for DCAA
- Defends against defective pricing claims
- Enables accurate revisions

**BOE structure per cost element:**

**1. Labor BOE**

| Component | Documentation |
|-----------|---------------|
| Hours | WBS-based estimate, historical actuals, SME input |
| Labor mix | Skill requirements per task, organizational chart |
| Rates | Payroll records, approved salary ranges, market data |
| Escalation | BLS data, company projection, inflation factors |

**2. Indirect Rates BOE**

| Component | Documentation |
|-----------|---------------|
| Fringe | Benefits enrollment data, tax rates |
| Overhead | Pool composition, allocation methodology |
| G&A | Pool composition, historical trends |

**3. ODC BOE**

| Component | Documentation |
|-----------|---------------|
| Travel | Trip estimates, JTR/GSA rates, historical costs |
| Materials | Vendor quotes, catalog prices, BOMs |
| Equipment | Quotes, technical specs justifying selection |

**4. Subcontractor BOE**
- Sub proposal and BOE
- Competition documentation (or sole source justification)
- Price analysis

**BOE template per line item:**
```
Element: Sr. Software Engineer (Labor Category 3)
Basis:
- Requirement: PWS 3.2 requires senior-level development
- Hours: 1,500 annually (WBS mapping attached)
- Rate: $95.00/hr (75th percentile for DC market per salary.com)
- Escalation: 3.0% annually (BLS ECI for professional services)
- Source: Payroll data for incumbent staff, Attachment B-3
```

**Retention:** Keep BOEs 6 years post-contract close (FAR 4.703).""",
        "rejected": "A BOE documents how you calculated each cost. Include your assumptions, data sources, and methodology for hours, rates, and other costs."
    },
    {
        "category": "pricing",
        "prompt": "How do I compare my pricing to the Independent Government Cost Estimate (IGCE)?",
        "chosen": """**IGCE = Independent Government Cost Estimate**

Government's internal estimate of contract cost, developed before receiving proposals.

**What you know:**
- IGCE exists for every negotiated procurement
- Government uses it to assess reasonableness
- Usually not disclosed to offerors

**What you can infer:**

**Source 1: Historical contract values**
- USASpending.gov: Prior contract awards
- FPDS: Contract actions and modifications
- GovWin/Bloomberg Gov: Market intelligence

**Source 2: Market indicators**
- GSA Schedule pricing for similar services
- BLS wage data for labor categories
- Industry benchmarks (FPDS category averages)

**Source 3: RFP signals**
- Estimated value in sources sought
- Contract ceiling mentioned
- Funding profile hints
- Period of performance × typical staffing

**Comparison analysis:**

| Your Price | vs. IGCE Proxy | Assessment |
|------------|----------------|------------|
| <20% below | May trigger realism review | Verify technical approach supports low price |
| Within ±20% | Competitive range likely | Standard positioning |
| >20% above | Competitiveness concern | Justify value or reduce |

**Strategic positioning:**

1. **Price-to-win below IGCE**
   - Risk: Realism adjustment, margin compression
   - Mitigation: Strong technical approach justifying efficiency

2. **Price at IGCE**
   - Balanced risk profile
   - Differentiate on technical/past performance

3. **Price above IGCE**
   - Must demonstrate superior value
   - Risk: Eliminated on price if close competition

**Intel gathering:**
- Pre-RFP industry days: Government sometimes shares estimate range
- Q&A: Can ask for IGCE range (rarely answered)
- Incumbent knowledge: If you're incumbent, you know actual costs

**Document:** Record all sources for your competitive analysis.""",
        "rejected": "Compare your pricing to similar past contracts and market rates. If you're significantly higher or lower than expected, adjust or justify the difference."
    },
]

def generate_hash(record: dict) -> str:
    """Generate a unique hash for a preference record."""
    content = f"{record['prompt']}{record['response_a']}{record['response_b']}"
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def save_local(preferences: list) -> dict:
    """Save preferences directly to local JSONL file."""
    results = {"success": 0, "failed": 0, "errors": []}
    
    DATA_DIR.mkdir(exist_ok=True)
    filepath = DATA_DIR / "procurement_preferences.jsonl"
    
    # Read existing hashes to avoid duplicates
    existing_hashes = set()
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    rec = json.loads(line.strip())
                    if rec.get("record_hash"):
                        existing_hashes.add(rec["record_hash"])
                except:
                    pass
    
    with open(filepath, 'a', encoding='utf-8') as f:
        for i, pref in enumerate(preferences):
            record = {
                "domain": "procurement",
                "category": pref["category"],
                "prompt": pref["prompt"],
                "response_a": pref["chosen"],
                "response_b": pref["rejected"],
                "preference": "A",
                "annotator_id": "synthetic_seed_v1",
                "dimension_scores": {
                    "accuracy": 5,
                    "safety": 5,
                    "actionability": 5,
                    "clarity": 5
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "record_hash": "",
                "difficulty": "medium",
                "notes": f"Synthetic DPO seed data - batch {i}",
            }
            record["record_hash"] = generate_hash(record)
            
            if record["record_hash"] in existing_hashes:
                print(f"[SKIP] [{i+1}/50] Already exists: {pref['prompt'][:40]}...")
                continue
            
            try:
                f.write(json.dumps(record) + "\n")
                results["success"] += 1
                print(f"[OK] [{i+1}/50] {pref['category']}: {pref['prompt'][:50]}...")
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"index": i, "error": str(e)})
                print(f"[ERR] [{i+1}/50] Error: {e}")
    
    return results


async def submit_preferences_api():
    """Submit all preferences to the API."""
    async with httpx.AsyncClient(timeout=60) as client:
        results = {"success": 0, "failed": 0, "errors": []}
        
        for i, pref in enumerate(PROCUREMENT_PREFERENCES):
            try:
                response = await client.post(
                    f"{API_BASE}/api/preferences",
                    headers={"X-API-Key": API_KEY},
                    json={
                        "domain": "procurement",
                        "category": pref["category"],
                        "prompt": pref["prompt"],
                        "response_a": pref["chosen"],  # Chosen response is A
                        "response_b": pref["rejected"],  # Rejected response is B
                        "preference": "A",  # Always prefer A (the chosen one)
                        "annotator_id": "synthetic_seed_v1",
                        "dimension_scores": {
                            "accuracy": 5,
                            "safety": 5,
                            "actionability": 5,
                            "clarity": 5
                        },
                        "difficulty": "medium",
                        "notes": f"Synthetic DPO seed data - batch {i}",
                        "metadata": {
                            "source": "synthetic",
                            "generator": "seed_procurement_50_v1",
                            "batch_index": i,
                            "generated_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
                
                if response.status_code == 200:
                    results["success"] += 1
                    print(f"[OK] [{i+1}/50] {pref['category']}: {pref['prompt'][:50]}...")
                else:
                    results["failed"] += 1
                    results["errors"].append({
                        "index": i,
                        "status": response.status_code,
                        "response": response.text
                    })
                    print(f"[FAIL] [{i+1}/50] Failed: {response.status_code}")
                    
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"index": i, "error": str(e)})
                print(f"[ERR] [{i+1}/50] Error: {e}")
            
            # Rate limiting: 100ms between requests
            await asyncio.sleep(0.1)
        
        return results


def submit_preferences():
    """Submit preferences - locally or via API based on mode."""
    if LOCAL_MODE:
        return save_local(PROCUREMENT_PREFERENCES)
    else:
        return asyncio.run(submit_preferences_api())

if __name__ == "__main__":
    mode = "LOCAL" if LOCAL_MODE else "API"
    print(f"Seeding 50 procurement preferences [{mode} mode]")
    if LOCAL_MODE:
        print(f"Writing to: {DATA_DIR / 'procurement_preferences.jsonl'}")
    else:
        print(f"API: {API_BASE}")
        print(f"Key: {API_KEY[:4]}...{API_KEY[-4:] if len(API_KEY) > 8 else '****'}")
    print("=" * 60)
    
    results = submit_preferences()
    
    print("=" * 60)
    print(f"Results: {results['success']} success, {results['failed']} failed")
    
    if results["errors"]:
        print("\nErrors:")
        for err in results["errors"][:5]:
            print(f"  - Index {err.get('index')}: {err}")

