# Epic Workflow Design - Phase 2

**Version:** 1.0  
**Last Updated:** June 17, 2026  
**Status:** Ready for Implementation

---

## Purpose

This document explains the design rationale and implementation details for the Epic lifecycle workflow in Phase 2 of the PMO Automation System.

---

## Problem Statement

**Before Phase 2:**
- Epics are created automatically from intake forms ✅
- But they have no structured workflow after creation ❌
- No visibility into which Epics are approved vs. in-progress vs. completed ❌
- No capacity planning or quarter-based scheduling ❌
- Stakeholders don't know the status of their requests ❌

**Phase 2 Solution:**
- 7-status Epic lifecycle (INTAKE → COMPLETED/REJECTED)
- Roadmap board visualization (Now/Next/Later)
- Capacity validation before scheduling
- Automated stakeholder notifications

---

## Design Principles

### 1. **Clarity Over Complexity**
- Each status has a clear, unambiguous meaning
- Transitions are intuitive (no circular loops)
- Status names match business terminology (not technical jargon)

### 2. **Automation Where Possible**
- Auto-transition to IN_EXECUTION when Stories start
- Auto-complete when all Stories are done
- Auto-notify stakeholders at key milestones

### 3. **Validation at the Right Time**
- Capacity check before IN_ROADMAP (not earlier)
- Business Value/Complexity required for BACKLOG (helps prioritization)
- Rejection reason required (stakeholder clarity)

### 4. **Stakeholder Experience First**
- Emails use plain language (not JIRA jargon)
- Status changes trigger notifications (transparency)
- Epic URL included in all emails (easy access)

---

## Epic Lifecycle States

```
┌──────────┐
│  INTAKE  │ ← Epic created from intake form
└────┬─────┘
     │ Manual: IT Leadership reviews
     ▼
┌──────────────┐
│ UNDER_REVIEW │ ← TPM evaluates capacity, ROI, alignment
└──────┬───────┘
       │
       ├─────────────┐
       │ Approved    │ Rejected
       ▼             ▼
   ┌─────────┐   ┌──────────┐
   │ BACKLOG │   │ REJECTED │ ← Not doing this
   └────┬────┘   └──────────┘
        │ Manual: Assign Quarter + Capacity
        ▼
   ┌────────────┐
   │ IN_ROADMAP │ ← Scheduled for specific quarter
   └─────┬──────┘
         │ Auto: First Story → IN_PROGRESS
         ▼
   ┌──────────────┐
   │ IN_EXECUTION │ ← Active development
   └──────┬───────┘
          │ Auto: All Stories → DONE
          ▼
      ┌───────────┐
      │ COMPLETED │ ← Delivered!
      └───────────┘

          │ Manual: Paused
          ▼
      ┌──────────┐
      │ ON_HOLD  │ ← Paused (dependency, reprioritized)
      └────┬─────┘
           │ Manual: Resume
           └──────► IN_ROADMAP or IN_EXECUTION
```

---

## Status Definitions

### INTAKE
**Meaning:** "New request from stakeholder"  
**Who Sets:** Automatic (when Epic created from Google Form)  
**Duration:** 3-5 business days  
**Next Step:** IT Leadership reviews  
**Stakeholder Message:** "Your request has been received and is in the queue."

---

### UNDER_REVIEW
**Meaning:** "TPM evaluating feasibility"  
**Who Sets:** IT Leadership (manual transition)  
**Duration:** 1-2 weeks  
**Evaluation Criteria:**
- Strategic alignment (does this fit our roadmap?)
- Business value (what's the ROI?)
- Technical feasibility (can we build this?)
- Capacity availability (do we have resources?)

**Next Step:** Approve to BACKLOG or Reject  
**Stakeholder Message:** "Your request is being evaluated by IT Leadership."

---

### BACKLOG
**Meaning:** "Approved but not yet scheduled"  
**Who Sets:** IT Leadership (after approval)  
**Duration:** Variable (depends on capacity)  
**Required Fields:**
- Business Value Score (1-10)
- Technical Complexity Score (1-10)

**Why These Fields?**
- Used for prioritization algorithm
- Priority Score = (Business Value × 2) - (Technical Complexity × 1.5)
- High business value + low complexity = prioritized first

**Next Step:** Assign to quarter when capacity available  
**Stakeholder Message:** "Your request has been approved and is in the backlog."

---

### IN_ROADMAP
**Meaning:** "Scheduled for a specific quarter"  
**Who Sets:** IT Leadership (manual transition with capacity validation)  
**Duration:** Until quarter starts  
**Required Fields:**
- Committed Quarter (e.g., Q3 2026)
- Team Capacity Allocation (%) (e.g., 25%)

**Capacity Validation:**
- Before transitioning, system checks: Is there capacity in target quarter?
- Blocks if >100% allocated
- Warns if >80% allocated

**Next Step:** Auto-transition to IN_EXECUTION when first Story starts  
**Stakeholder Message:** "Your request is scheduled for [Quarter]."

---

### IN_EXECUTION
**Meaning:** "Active development in sprints"  
**Who Sets:** Automatic (when first child Story → IN_PROGRESS)  
**Duration:** Variable (depends on Epic size)  
**Trigger:** JIRA Automation Rule watches for Story transitions

**What "In Execution" Means:**
- Epic has been broken down into Stories
- At least one Story is actively being developed
- Work is happening in sprints

**Next Step:** Auto-complete when all Stories → DONE  
**Stakeholder Message:** "Development has started on your request."

---

### COMPLETED
**Meaning:** "All work delivered"  
**Who Sets:** Automatic (when all child Stories → DONE or CLOSED)  
**Duration:** Final state  
**Trigger:** Scheduled automation (runs daily at 9 AM)

**Completion Logic:**
```sql
FOR EACH Epic IN (status = IN_EXECUTION):
  IF COUNT(child Stories NOT IN (DONE, CLOSED)) = 0:
    THEN transition to COMPLETED
```

**Next Step:** None (final state)  
**Stakeholder Message:** "Your request has been delivered! ✅"

---

### REJECTED
**Meaning:** "Request denied"  
**Who Sets:** IT Leadership (manual from UNDER_REVIEW)  
**Duration:** Final state  
**Required Fields:**
- Rejection Reason (text, required)
- Alternative Approach (text, optional)

**Why Reject?**
- Not aligned with strategy
- Insufficient business value (ROI too low)
- Technical infeasibility
- Better solution already exists

**Next Step:** None (final state)  
**Stakeholder Message:** "Your request was not approved. Reason: [...]"

---

### ON_HOLD
**Meaning:** "Paused due to blocker"  
**Who Sets:** IT Leadership or TPM (manual)  
**Duration:** Until blocker resolved  
**Required Fields:**
- Hold Reason (text)
- Blocker Type (select: Dependency, Budget, Resource, etc.)
- Expected Resume Date (optional)

**Common Blockers:**
- Waiting on vendor
- Budget freeze
- Key resource unavailable
- Reprioritized (other work more urgent)

**Next Step:** Resume to IN_ROADMAP or IN_EXECUTION  
**Stakeholder Message:** "Your request is temporarily on hold. Reason: [...]"

---

## Transition Logic

### Manual Transitions

| From | To | Who | Validators | Post-Functions |
|------|-----|-----|------------|----------------|
| INTAKE | UNDER_REVIEW | IT Leadership | Request Type populated | Assign to TPM, add comment |
| UNDER_REVIEW | BACKLOG | IT Leadership | Business Value + Complexity set | Email stakeholder, add label "approved" |
| UNDER_REVIEW | REJECTED | IT Leadership | Rejection Reason required | Email stakeholder with reason |
| BACKLOG | IN_ROADMAP | IT Leadership | Quarter + Capacity set, Capacity check passes | Email stakeholder, add roadmap label |
| IN_ROADMAP | ON_HOLD | IT Leadership/TPM | Hold Reason + Blocker Type | Email stakeholder + team |
| IN_EXECUTION | ON_HOLD | IT Leadership/TPM | Hold Reason required | Email stakeholder + team |
| ON_HOLD | IN_ROADMAP | IT Leadership/TPM | Blocker resolved | Email stakeholder |
| ON_HOLD | IN_EXECUTION | IT Leadership/TPM | Has active Stories | Email stakeholder + team |

### Automatic Transitions

| From | To | Trigger | Logic |
|------|-----|---------|-------|
| IN_ROADMAP | IN_EXECUTION | First Story → IN_PROGRESS | JIRA Automation Rule 12 |
| IN_EXECUTION | COMPLETED | All Stories → DONE/CLOSED | JIRA Automation Rule 13 (scheduled daily) |

---

## Validation Rules

### Capacity Validation (Railway Middleware)

**When:** Before BACKLOG → IN_ROADMAP transition  
**What:** Check if team has capacity in target quarter  
**How:**

```python
# Pseudocode
epic_capacity = Epic.fields.team_capacity_allocation  # e.g., 25%
quarter = Epic.fields.committed_quarter  # e.g., "Q3 2026"

# Query all Epics in same quarter
existing_epics = JIRA.search(
  jql="Committed Quarter = '{quarter}' AND status IN (IN_ROADMAP, IN_EXECUTION)"
)

# Sum allocated capacity
total_allocated = SUM(existing_epics.team_capacity_allocation)

# Check threshold
if (total_allocated + epic_capacity) > 100:
  BLOCK transition
  MESSAGE "Insufficient capacity. Need {epic_capacity}%, only {100 - total_allocated}% available."
elif (total_allocated + epic_capacity) > 80:
  ALLOW transition with WARNING
  MESSAGE "Warning: {quarter} will be {total_allocated + epic_capacity}% utilized (over-committed)."
else:
  ALLOW transition
  MESSAGE "Capacity OK. {quarter} utilization: {total_allocated + epic_capacity}%."
```

**Implementation:** See `app/rules/capacity_validator.py`

---

### Required Fields Validation

**BACKLOG → IN_ROADMAP:**
- Committed Quarter (must be set)
- Team Capacity Allocation (%) (must be 1-100)
- Business Value Score (must be 1-10)
- Technical Complexity Score (must be 1-10)

**UNDER_REVIEW → REJECTED:**
- Rejection Reason (must be filled)

**→ ON_HOLD:**
- Hold Reason (must be filled)
- Blocker Type (must be selected)

---

## Notification Strategy

### Email Notifications

| Transition | Recipient | Subject | Tone |
|------------|-----------|---------|------|
| → BACKLOG | Stakeholder | "Your Request Has Been Approved" | Positive |
| → IN_ROADMAP | Stakeholder | "Your Request Scheduled for {Quarter}" | Informative |
| → IN_EXECUTION | Stakeholder | "Development Started on Your Request" | Exciting |
| → COMPLETED | Stakeholder | "Your Request Has Been Delivered! ✅" | Celebratory |
| → REJECTED | Stakeholder | "Request Status Update: Not Approved" | Empathetic |
| → ON_HOLD | Stakeholder + Team | "Request Temporarily On Hold" | Transparent |

**Email Template Structure:**
1. **Greeting:** "Hello,"
2. **Status Update:** What happened
3. **Epic Details:** Key, Summary, relevant fields
4. **Next Steps:** What to expect
5. **Link:** View Epic in JIRA
6. **Signature:** "Best regards, IT Program Management"

---

### Slack Notifications (Optional)

**Channel:** #program-updates  
**When:** IN_EXECUTION, COMPLETED  
**Format:**
```
🚀 **Epic Started: PGMAUTO-123**
*New Dashboard Widget*

First Story: PGMAUTO-124
Sprint: Sprint 42
Owner: Jane Doe

<link|View Epic>
```

---

## Capacity Planning Algorithm

### Priority Score Calculation

**Formula:**
```
Priority Score = (Business Value × 2.0) - (Technical Complexity × 1.5) + Adjustments
```

**Adjustments:**
- P0 (Critical) requests: +20 boost
- Risk Flags present: -5 penalty
- Vendor dependencies: -3 penalty

**Example:**
```
Epic A:
  Business Value = 8
  Technical Complexity = 3
  Priority = P1 (no boost)
  Risk Flags = None

Priority Score = (8 × 2.0) - (3 × 1.5) + 0
               = 16 - 4.5
               = 11.5

Epic B:
  Business Value = 6
  Technical Complexity = 2
  Priority = P0 (+20 boost)
  Risk Flags = Vendor Dependency (-5 penalty)

Priority Score = (6 × 2.0) - (2 × 1.5) + 20 - 5
               = 12 - 3 + 15
               = 24

Result: Epic B prioritized (higher score)
```

---

### Capacity Allocation

**Team Capacity Per Quarter:** 100%

**Example Quarter Allocation:**
```
Q3 2026:
  Epic 1: 30% (high complexity, large scope)
  Epic 2: 25% (medium complexity)
  Epic 3: 20% (low complexity)
  Epic 4: 15% (small enhancement)
  ─────────
  Total: 90% utilized

  Status: ✅ Healthy (under 80% threshold)
  Remaining: 10% (buffer for emergencies)
```

**Over-Capacity Example:**
```
Q4 2026:
  Epic 5: 40%
  Epic 6: 35%
  Epic 7: 30%
  ─────────
  Total: 105% utilized

  Status: ❌ Over-committed (>100%)
  Action: Move Epic 7 to Q1 2027 OR reduce scope
```

---

## Roadmap Board Layout

### Columns

1. **Backlog** (status = BACKLOG)
   - Approved but not scheduled
   - Sorted by Priority Score (high to low)

2. **Now - Q2 2026** (status = IN_ROADMAP, Quarter = Q2 2026)
   - Currently scheduled work
   - May be in execution (overlaps with current sprint)

3. **Next - Q3 2026** (status = IN_ROADMAP, Quarter = Q3 2026)
   - Next quarter's work
   - In planning/breakdown phase

4. **Later - Q4+ 2026** (status = IN_ROADMAP, Quarter >= Q4 2026)
   - Future quarters
   - May change as priorities shift

5. **In Execution** (status = IN_EXECUTION)
   - Active development
   - Has Stories in current sprints

6. **Completed** (status = COMPLETED)
   - Delivered work
   - Archive after 30 days

### Swimlanes

**Group By:** Request Type
- Project Request (large initiatives)
- Enhancement Request (improve existing)
- Feature Request (new capabilities)
- Bug Fix Request (production issues)

**Why Group by Request Type?**
- Easy to see balance (are we doing too much new vs. fixing bugs?)
- Different request types have different stakeholder expectations
- Helps capacity planning (bugs often need immediate attention)

### Card Layout

**Card Title:** Epic Summary  
**Card Fields:**
- Priority (visual: P0=Red, P1=Orange, P2=Yellow, P3=Green)
- Committed Quarter
- Business Value Score (e.g., "Value: 8/10")
- Team Capacity Allocation (e.g., "Capacity: 25%")
- Request Type (if not using swimlanes)

### Quick Filters

1. **"At Risk"** - `Due Date < 30 days AND status != COMPLETED`
2. **"P0 Only"** - `Priority = Highest`
3. **"This Quarter"** - `Committed Quarter = {current quarter}`
4. **"Over Capacity"** - `labels = "capacity-warning"`

---

## Design Decisions & Trade-offs

### Why 7 Statuses (Not More/Less)?

**Considered Options:**
- **3 statuses:** To Do, In Progress, Done (too simple, no visibility)
- **5 statuses:** INTAKE, APPROVED, IN_EXECUTION, ON_HOLD, DONE (missing roadmap visibility)
- **10+ statuses:** INTAKE, SCOPING, REVIEW, APPROVAL, BACKLOG, PLANNING, SCHEDULED, IN_PROGRESS, QA, DONE (too complex)

**Chose 7 Because:**
- Clear distinction between approved (BACKLOG) vs. scheduled (IN_ROADMAP)
- Separate UNDER_REVIEW allows TPM evaluation phase
- ON_HOLD as separate status (not same as BACKLOG)
- COMPLETED vs. REJECTED (different final states)

---

### Why Automatic Transitions?

**IN_ROADMAP → IN_EXECUTION (Auto):**
- Manual transition = extra work for TPM
- First Story → IN_PROGRESS is a clear, unambiguous signal
- Reduces overhead, increases accuracy

**IN_EXECUTION → COMPLETED (Auto):**
- Manual completion often delayed (TPM forgets to close)
- All Stories done = Epic done (objective measure)
- Daily scheduled check ensures timely completion

---

### Why Capacity Validation in Middleware (Not JIRA)?

**JIRA Native Validators:**
- Can't query other Epics to sum capacity
- No complex calculations (only field checks)

**Railway Middleware:**
- Full JIRA API access (can query, sum, calculate)
- Custom logic (thresholds, warnings, penalties)
- Logging & audit trail in database

---

## Implementation Checklist

- [ ] Create Epic workflow in JIRA UI (8 statuses, transitions)
- [ ] Add 11 custom fields for Epics (Business Value, Complexity, etc.)
- [ ] Create 8 automation rules in JIRA
- [ ] Configure Roadmap board (columns, swimlanes, filters)
- [ ] Implement capacity_validator.py in Railway middleware
- [ ] Update webhooks.py to call capacity validator
- [ ] Test all transitions manually
- [ ] Test auto-transitions with real Epics
- [ ] Verify email notifications
- [ ] Train TPM team on new workflow

---

## Success Metrics

**Phase 2 is successful when:**
1. ✅ All 7 statuses functional in JIRA
2. ✅ Capacity validation blocks over-committed quarters
3. ✅ Epics auto-transition to IN_EXECUTION when Stories start
4. ✅ Epics auto-complete when all Stories done
5. ✅ Stakeholders receive emails at each status change
6. ✅ Roadmap board shows Now/Next/Later clearly
7. ✅ TPM team actively uses Roadmap for planning

---

## References

- **Configuration:** `config/jira-epic-workflow.yaml`
- **Automation Rules:** `config/jira-epic-automation-rules.yaml`
- **Custom Fields:** `config/jira-custom-fields.json`
- **Setup Guide:** `PHASE2_SETUP.md`
- **Capacity Planning:** `docs/capacity-planning.md`
