# Capacity Planning Guide - Phase 2

**Version:** 1.0  
**Last Updated:** June 18, 2026  
**Audience:** TPMs, IT Leadership, Scrum Masters

---

## What is Capacity Planning?

**Capacity planning** ensures your team doesn't commit to more work than they can deliver in a given quarter.

**Without capacity planning:**
- Teams over-commit → sprints fail → stakeholders disappointed
- No visibility into "how much is too much"
- Ad-hoc decisions ("can we squeeze this in?")

**With capacity planning:**
- Clear view of team utilization per quarter
- Data-driven decisions on what to schedule
- Early warning when approaching capacity limits
- Stakeholder expectations properly set

---

## How Capacity Works in This System

### 1. Team Capacity = 100% Per Quarter

**What does 100% mean?**
- 100% = Full team capacity for a 13-week quarter
- Includes: Development, code review, QA, deployments, meetings
- Excludes: Holidays, PTO, oncall/support (already factored in)

**Example:**
- Team of 5 developers × 13 weeks = 65 developer-weeks
- 100% capacity = 65 developer-weeks available
- Epic needing 16.25 dev-weeks = 25% capacity

---

### 2. Each Epic Gets a Capacity Allocation (%)

**Field:** Team Capacity Allocation (%)  
**Range:** 1-100  
**Meaning:** What percentage of team capacity this Epic requires

**How to Estimate:**

**Method 1: Story Points (If Stories Exist)**
```
Epic has 40 story points estimated
Team velocity = 20 points/sprint
Team does 6 sprints per quarter = 120 points/quarter capacity

Capacity % = (40 / 120) × 100 = 33%
```

**Method 2: Time-Based (If No Story Points Yet)**
```
Epic estimated to take 3 weeks of full-team effort
Quarter has 13 weeks

Capacity % = (3 / 13) × 100 = 23%
```

**Method 3: T-Shirt Sizing (Quick Estimate)**
- Small Epic = 10-15%
- Medium Epic = 20-30%
- Large Epic = 35-50%
- Extra Large Epic = 50%+ (consider splitting!)

**Pro Tip:** Start conservative. It's easier to finish early than explain delays.

---

### 3. Capacity Validation Before Scheduling

**When:** Epic transitions from BACKLOG → IN_ROADMAP  
**What Happens:** System checks if quarter has capacity

**Validation Logic:**
```python
# Get Epic's capacity need
epic_capacity = 25%  # Example: Epic needs 25% of team

# Get target quarter
quarter = "Q3 2026"

# Query all Epics already in that quarter
existing_epics = Query JIRA:
  "Committed Quarter = Q3 2026 AND status IN (IN_ROADMAP, IN_EXECUTION)"

# Sum their capacity allocations
total_allocated = SUM(existing_epics.capacity)
# Example: 30% + 20% + 15% = 65% already allocated

# Calculate new utilization
new_utilization = total_allocated + epic_capacity
# Example: 65% + 25% = 90%

# Decision
if new_utilization > 100%:
    BLOCK transition
    "Insufficient capacity. Need 25%, only 35% available."
elif new_utilization > 80%:
    ALLOW with WARNING
    "Warning: Q3 2026 will be 90% utilized (over-committed risk)."
else:
    ALLOW
    "Capacity OK. Q3 2026 utilization: 90%."
```

**Result:**
- ✅ **Allowed (≤80%):** Green light, schedule it
- ⚠️ **Warning (80-100%):** Allowed but TPM notified (risky)
- ❌ **Blocked (>100%):** Cannot schedule, must move to later quarter

---

## Capacity Planning Workflow

### Step 1: Epics Approved to BACKLOG

**Status:** BACKLOG  
**Required Fields:**
- ✅ Business Value Score (1-10)
- ✅ Technical Complexity Score (1-10)
- ❌ Committed Quarter (not set yet)
- ❌ Team Capacity Allocation (not set yet)

**Action:** Epics wait in BACKLOG until scheduled

---

### Step 2: Quarterly Planning Meeting

**When:** 4-6 weeks before quarter starts  
**Who:** IT Leadership, TPMs, Engineering Leads  
**Input:** List of Epics in BACKLOG  
**Output:** Epics scheduled for next quarter

**Meeting Agenda:**

**1. Review Backlog (15 min)**
- How many Epics in BACKLOG?
- What are the Priority Scores?
- Any P0 (critical) requests?

**2. Review Team Capacity (10 min)**
- Is team size changing? (hiring, attrition)
- Any planned PTO or holidays?
- Velocity trends (are we getting faster/slower?)

**3. Estimate Epic Capacity (30 min)**
For each Epic:
- Discuss scope
- Estimate story points OR time needed
- Calculate capacity % (use one of 3 methods above)
- Set "Team Capacity Allocation (%)" field

**4. Schedule Epics to Quarter (30 min)**
Sort Epics by Priority Score (highest first)

For each Epic (in priority order):
- Check: Does Q3 have capacity?
- If YES → Set "Committed Quarter = Q3 2026" → Epic transitions to IN_ROADMAP
- If NO → Try Q4 2026, then Q1 2027, etc.
- Continue until quarter is ~80% full

**5. Review & Adjust (15 min)**
- Is any quarter over-committed?
- Are P0 requests all scheduled?
- Any dependencies between Epics?

**Output:** Roadmap for next 2-3 quarters

---

### Step 3: Epic Transitions to IN_ROADMAP

**Trigger:** "Committed Quarter" field set + capacity validated  
**Result:**
- Epic status → IN_ROADMAP
- Stakeholder emailed: "Your request is scheduled for Q3 2026"
- Epic appears in "Next" column on Roadmap board

---

### Step 4: Monitor Utilization During Quarter

**How:** Check Roadmap board or API endpoint

**API Endpoint:**
```bash
GET /api/roadmap/capacity/Q3%202026

Response:
{
  "quarter": "Q3 2026",
  "total_capacity": 100,
  "allocated": 85,
  "utilization_percent": 85,
  "remaining": 15,
  "status": "at_risk",  // >80% utilization
  "epics_count": 4
}
```

**Actions Based on Status:**
- **healthy (<80%):** All good, continue
- **at_risk (80-100%):** Watch closely, may need to descope
- **over_committed (>100%):** Immediate action required (see below)

---

## Handling Over-Committed Quarters

**Scenario:** Q3 2026 is at 110% utilization (10% over capacity)

**Options:**

### Option 1: Move Lower-Priority Epics
- Identify lowest Priority Score Epic in Q3
- Move to Q4 (change "Committed Quarter" field)
- Epic transitions back to BACKLOG → IN_ROADMAP in Q4

**When to use:** Most common solution

---

### Option 2: Reduce Epic Scope
- Break Epic into phases (Phase 1 in Q3, Phase 2 in Q4)
- Reduce capacity allocation (e.g., 40% → 30%)
- Communicate scope change to stakeholder

**When to use:** Epic can be delivered incrementally

---

### Option 3: Increase Team Capacity
- Hire contractors
- Reassign engineers from other teams
- Reduce support/maintenance work

**When to use:** Epic is critical (P0) and can't wait

---

### Option 4: Accept the Risk
- Keep at 110% utilization
- Plan for overtime or weekend work
- Communicate risk to stakeholders

**When to use:** Rarely. High risk of sprint failure.

---

## Capacity Planning Best Practices

### ✅ DO:

**1. Plan Conservatively**
- Aim for 70-80% utilization (not 100%)
- Leave buffer for emergencies, bugs, oncall

**2. Update Estimates as You Learn**
- When Stories are created, refine capacity estimate
- If Epic grows in scope, increase capacity %
- Adjust future quarters based on actuals

**3. Track Actuals vs. Estimates**
- Did Epic actually take 25%? Or 35%?
- Use variance to improve future estimates
- Document lessons learned

**4. Communicate Early**
- If quarter is filling up, tell stakeholders ASAP
- Set expectations: "We can't fit this in Q3, earliest is Q4"

**5. Prioritize Ruthlessly**
- Use Priority Score algorithm
- P0 requests always scheduled first
- Low-value, high-complexity Epics = last (or never)

---

### ❌ DON'T:

**1. Don't Over-Commit "Just This Once"**
- 110% utilization = 110% chance of problems
- Once you over-commit, it becomes the norm

**2. Don't Ignore Warnings**
- Capacity warning at 85%? Pay attention.
- Don't schedule "one more Epic" when already at 95%

**3. Don't Forget Non-Dev Work**
- Code review takes time
- QA testing takes time
- Deployment, docs, training all count

**4. Don't Schedule All Capacity**
- Leave 10-20% buffer
- Bugs happen, people get sick, priorities change

**5. Don't Use Capacity % as Deadline**
- 25% capacity ≠ 25% of quarter timeline
- Epics can be parallel, sequential, or blocked

---

## Capacity Planning Examples

### Example 1: Healthy Quarter (70% Utilization)

**Q3 2026 Epics:**
1. New Dashboard Widget (25%)
2. API Performance Upgrade (20%)
3. User Settings Page (15%)
4. Email Notification System (10%)

**Total:** 70%  
**Remaining:** 30%  
**Status:** ✅ Healthy

**Analysis:**
- Good buffer for emergencies
- Can add 1-2 small Epics if priorities change
- Low risk of over-committing

---

### Example 2: At-Risk Quarter (90% Utilization)

**Q4 2026 Epics:**
1. Payment Integration (40%)
2. Mobile App MVP (30%)
3. Admin Panel Redesign (20%)

**Total:** 90%  
**Remaining:** 10%  
**Status:** ⚠️ At Risk

**Analysis:**
- Very little buffer
- One Epic slipping = quarter in jeopardy
- Should consider moving Admin Panel to Q1 2027

**Action:** TPM monitors weekly, ready to descope if needed

---

### Example 3: Over-Committed Quarter (115% Utilization)

**Q1 2027 Epics:**
1. Data Migration (50%)
2. New Checkout Flow (35%)
3. Reporting Dashboard (30%)

**Total:** 115%  
**Remaining:** -15%  
**Status:** ❌ Over-Committed

**Analysis:**
- Mathematically impossible to deliver all 3
- High risk of sprint failure, stakeholder disappointment

**Action Required:**
- **Option A:** Move Reporting Dashboard to Q2 2027 (total = 85%, healthy)
- **Option B:** Hire 2 contractors for Q1 (increases capacity to 130%)
- **Option C:** Reduce Data Migration scope to Phase 1 only (50% → 35%, total = 100%)

**Decision:** Choose Option A (move to Q2)

---

## Capacity Planning Tools

### 1. Roadmap Board (Visual)

**How to Use:**
- Open "PMO Roadmap - Epics" board
- Look at "Next - Q3 2026" column
- Each card shows capacity %
- Quick visual: Are there too many cards?

**Limitations:**
- No automatic calculation
- Need to mentally add up percentages

---

### 2. API Endpoint (Programmatic)

**Endpoint:** `GET /api/roadmap/capacity/{quarter}`

**Use Case:** Dashboard, Slack bot, weekly report

**Example:**
```bash
curl https://pm-automation-system-production.up.railway.app/api/roadmap/capacity/Q3%202026

{
  "quarter": "Q3 2026",
  "total_capacity": 100,
  "allocated": 75,
  "utilization_percent": 75,
  "remaining": 25,
  "status": "healthy",
  "epics_count": 3,
  "epics": [
    {"key": "PGMAUTO-10", "summary": "Dashboard Widget", "capacity": 25},
    {"key": "PGMAUTO-11", "summary": "API Upgrade", "capacity": 30},
    {"key": "PGMAUTO-12", "summary": "Settings Page", "capacity": 20}
  ]
}
```

---

### 3. JIRA JQL Query (Manual)

**Query:**
```sql
project = PGMAUTO 
AND issuetype = Epic 
AND "Committed Quarter" = "Q3 2026" 
AND status IN (IN_ROADMAP, IN_EXECUTION)
ORDER BY "Team Capacity Allocation (%)" DESC
```

**Export to Excel:** Add up "Team Capacity Allocation" column manually

---

### 4. Weekly Capacity Report (Automated)

**Setup:** JIRA Automation scheduled trigger (Monday 9 AM)

**Action:** Email to TPM
```
Subject: Weekly Capacity Report

Q3 2026: 75% utilized (25% remaining)
Q4 2026: 45% utilized (55% remaining)
Q1 2027: 30% utilized (70% remaining)

At-Risk Quarters: None
Over-Committed Quarters: None

Action: Review backlog for Q3 2026 (can add 1-2 more Epics)
```

---

## Capacity Planning Metrics

Track these over time to improve estimates:

### 1. Estimation Accuracy

**Metric:** Avg(Actual Capacity / Estimated Capacity)

**Example:**
- Epic A: Estimated 25%, Actual 30% → 1.2x
- Epic B: Estimated 40%, Actual 35% → 0.875x
- Epic C: Estimated 20%, Actual 25% → 1.25x

**Average:** (1.2 + 0.875 + 1.25) / 3 = 1.1x

**Meaning:** We underestimate by 10% on average

**Action:** Multiply future estimates by 1.1

---

### 2. Quarter Completion Rate

**Metric:** % of scheduled Epics completed in quarter

**Example:**
- Q2 2026: 4 Epics scheduled, 3 completed → 75%
- Q1 2026: 5 Epics scheduled, 4 completed → 80%

**Meaning:** We complete ~75-80% of planned work

**Action:** Only schedule to 80% capacity (not 100%)

---

### 3. Carryover Rate

**Metric:** % of Epics that slip to next quarter

**Example:**
- Q2 2026: 1 Epic carried over to Q3 → 25% carryover

**Meaning:** 1 in 4 Epics takes longer than expected

**Action:** Build larger buffer, improve estimates

---

## Troubleshooting

### Problem: "We always finish early (only 60% utilization)"

**Cause:** Estimates too conservative OR team velocity increased

**Solution:**
- Review actual vs. estimated for last 3 quarters
- Increase estimates OR schedule more work

---

### Problem: "We never finish on time (Epics always slip)"

**Cause:** Estimates too optimistic OR capacity calculation wrong

**Solution:**
- Add 1.5x buffer to all estimates
- Reduce quarter utilization target to 70%
- Track interruptions (oncall, bugs, meetings)

---

### Problem: "Stakeholders complain about long wait times"

**Cause:** Backlog too large OR capacity too small

**Solution:**
- Hire more engineers (increase capacity)
- Reject more requests (reduce backlog)
- Reduce Epic scope (deliver MVPs faster)

---

### Problem: "Capacity warnings ignored, we keep over-committing"

**Cause:** Culture issue (leadership pushes for "yes")

**Solution:**
- Show data: Over-committed quarters = failed sprints
- Set policy: Hard stop at 85% utilization
- Escalate to leadership when pressure to over-commit

---

## Summary

**Capacity Planning in 5 Steps:**

1. **Estimate** Epic capacity % (story points OR time OR t-shirt)
2. **Validate** capacity available in target quarter
3. **Schedule** Epic to quarter (set "Committed Quarter" field)
4. **Monitor** utilization during quarter (API or Roadmap board)
5. **Adjust** if over-committed (move, descope, or hire)

**Key Principles:**
- ✅ Plan conservatively (70-80% utilization)
- ✅ Prioritize ruthlessly (use Priority Score)
- ✅ Communicate early (set expectations)
- ✅ Learn from actuals (improve estimates)
- ❌ Never over-commit "just this once"

**Success Metrics:**
- Quarter completion rate >80%
- Estimation accuracy within ±20%
- Stakeholder satisfaction (no surprise delays)

---

## References

- **Epic Workflow Design:** `docs/epic-workflow-design.md`
- **Capacity Validator Code:** `app/rules/capacity_validator.py`
- **API Endpoints:** `app/api/epic_routes.py`
- **JIRA Automation Rules:** `config/jira-epic-automation-rules.yaml` (Rule 16: Capacity Warning)
