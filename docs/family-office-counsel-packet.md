# Wooden Family Office — Counsel-Ready Packet

> **This document is not legal advice and is not a filing.** It is a
> structured intake meant to be handed to a securities attorney and a
> tax CPA. It captures the decisions a lawyer will need from you, the
> options you should understand before that meeting, and a checklist
> for the engagement.

---

## 1. Why a Family Office (and which kind)

There are roughly three operating models people call "family office":

| Model | What it is | Why it matters |
|---|---|---|
| **Embedded** | A trust + an investment account managed by an outside RIA. | Cheapest, simplest, but no operating entity, no ability to employ staff or run an agent under it cleanly. |
| **Single-Family Office (SFO)** | A management entity (LLC) that advises a single family's wealth, structured to fit the SEC **Family Office Rule** (17 CFR 275.202(a)(11)(G)-1) so it is exempt from registering as an investment adviser. | The realistic target for what you described. |
| **Multi-Family Office** | Advises more than one unrelated family. | Generally requires SEC or state RIA registration. **Out of scope** — would void the SFO exemption you want. |

The SFO model is what the rest of this document targets.

## 2. SEC Family Office Rule — the three requirements

To rely on the Family Office Rule and avoid Investment Advisers Act
registration, the entity must satisfy **all three** of:

1. **Clients are limited to "family clients"** as defined in the rule
   — this includes lineal descendants of a common ancestor (within 10
   generations), their spouses, key employees, certain trusts and
   estates, and family-owned charitable orgs. **No outside clients.
   Period.**
2. **Wholly owned by family clients and exclusively controlled by
   family members or family entities.** Outside professional managers
   may be employed, but ownership and control stay inside.
3. **Does not hold itself out to the public as an investment adviser.**
   This affects branding, the website, social posts, and how the AI
   agent (`wofo`) is described publicly.

Items the lawyer will analyze for your situation:
- Who counts as a "family client" in your specific family tree.
- Whether any non-family employees you'd want to include (the AI agent
  isn't a person but the *humans* operating it might be) qualify as
  "key employees" under the rule.
- Whether any prior third-party-money relationships exist that would
  blow the exemption on day one.

## 3. Decisions the lawyer will ask you for

Bring answers to these:

### Structure
- [ ] **State of formation for the management entity** — Delaware,
      Wyoming, South Dakota, and your home state are the typical
      candidates. Tradeoffs: DE for governance familiarity; WY/SD for
      privacy + asset protection + no state income tax for trust
      situs; home state to avoid foreign-entity registration overhead.
- [ ] **Entity type** — LLC (taxed as partnership or S-corp) is
      typical for the management company. The investment vehicle is
      usually a separate LP or LLC.
- [ ] **Number of vehicles** — single-pot vs. one per investment
      strategy / per branch of the family.
- [ ] **Operating company / investment vehicle separation** — the
      common pattern is `WoodenFO Management LLC` (the SFO) advising
      `WoodenFO Investments LP` (the capital pool) with family members
      as LPs.

### Family
- [ ] List of family members who will be clients/owners (full names,
      relationship to common ancestor).
- [ ] Existing trusts, foundations, or LLCs that should be brought in
      as family-client entities.
- [ ] Anyone you'd want to employ who is *not* family (this affects
      "key employee" status).

### Capital & operations
- [ ] Approximate AUM at launch.
- [ ] Asset classes you intend to hold (public equities only? real
      estate? private placements?).
- [ ] Whether anyone is currently receiving advisory services from you
      informally — this needs to stop or be papered before the SFO
      launches.
- [ ] Custodian / prime broker preference.

### Tax
- [ ] Tax residence of each family client.
- [ ] Whether the management entity should elect **§475(f)** mark-to-
      market (relevant if the agent trades actively and you want
      ordinary loss treatment + no wash-sale rule).
- [ ] State tax planning — particularly relevant if any family member
      is in a high-tax state.

### AI agent–specific
- [ ] How `wofo` will be described publicly (or not described at all).
- [ ] Who is legally accountable for orders the agent proposes /
      executes.
- [ ] Data licensing terms for any market data feeds — many vendors
      restrict programmatic / model-training use.

## 4. Documents the engagement will produce

You will not be receiving these from me. The lawyer will produce:

- **Certificate of Formation** for the management entity (state-
  specific filing).
- **Operating Agreement** for the management entity.
- **Limited Partnership Agreement** (or LLC equivalent) for the
  investment vehicle, including:
  - Allocation provisions.
  - Capital call / withdrawal mechanics.
  - Manager indemnification.
  - "Family client" eligibility recitals.
- **Subscription documents** for each family-client investor.
- **Side letters** if branches of the family negotiate different terms.
- **Investment Policy Statement** (often produced jointly with the
  CPA / financial advisor).
- **Compliance manual** even though the SFO is exempt — you still need
  written policies (custody, conflicts, books-and-records).
- **Form D / state Blue Sky filings** if the investment vehicle relies
  on Reg D for the family-client interests.

## 5. Tax / accounting items for the CPA

These are CPA-side decisions, distinct from the lawyer's:

- [ ] Federal partnership return (Form 1065) for the investment LP.
- [ ] Schedule K-1s to family clients.
- [ ] §475(f) election timing (must be made by the original due date
      of the prior year's return).
- [ ] Whether the management entity itself should elect S-corp
      treatment for self-employment-tax planning.
- [ ] State nexus analysis if family clients are in multiple states.
- [ ] Lender (Lender Management) precedent — the Tax Court case that
      established a family office can deduct expenses as a trade or
      business under §162 (vs. only §212). Worth discussing whether
      your facts fit that pattern.

## 6. Vendor / counsel shortlist criteria

Look for firms that:
- Specifically list **"single family office"** or **"family office
  formation"** as a practice area, not just "private wealth."
- Have **investment-management** lawyers in-house (not just trusts &
  estates) — you need someone who lives in the Investment Advisers Act.
- Have done at least one SFO formation in the state you'll form in.
- Will quote you a **flat fee** for formation (typical range varies
  widely — get 3 quotes).
- Have a relationship with a CPA firm experienced in fund accounting
  and Lender Management–style tax positions.

## 7. Concrete next steps

1. **Pick a counsel and a CPA.** Get 3 quotes each.
2. **Fill out the decision checklists in §3 above** before the first
   call so the meeting is decisions, not discovery.
3. **Pause any informal advice you give to non-family** until the
   structure is in place.
4. **Audit your public footprint** — anywhere `wofo`, the family
   office, or you-as-investor are described publicly should be
   reviewed against the "holding out to the public" prong of the
   Family Office Rule.
5. **Open the operational accounts** (custody, prime broker, business
   bank) under the entity name once formation is complete.

## 8. What this document is *not*

- Not a substitute for counsel.
- Not jurisdiction-specific advice.
- Not tax advice.
- Not exhaustive. Your lawyer will surface items not on this list.

The job of this document is to make the first meeting cheap and useful.
