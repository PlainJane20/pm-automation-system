# 🗺️ Full PMO Automation System - End-to-End Vision

**Project:** Complete PMO Intake, Roadmap, Scoping & Execution Automation  
**Status:** Phase 1 Complete ✅ | Phases 2-4 Planned 📋  
**Last Updated:** June 17, 2026

---

## 🎯 Vision: Strategic → Tactical → Operational Pipeline

This system automates the **entire lifecycle** from stakeholder request to sprint execution:

```
📋 STRATEGIC (Epic Level)
   ├─ Stakeholder submits business case
   ├─ TPM reviews capacity, ROI, alignment
   ├─ Approved → Roadmap (Now/Next/Later)
   └─ Backlog management (capacity-constrained)

📝 TACTICAL (Story Level)
   ├─ Break Epic into Stories
   ├─ BRD process (requirements definition)
   ├─ BRD approved → READY_FOR_DEV
   └─ Stories queued in Sprint Backlog

🏃 OPERATIONAL (Sprint Level)
   ├─ Sprint Planning (pull READY_FOR_DEV stories)
   ├─ Daily execution (Scrum board)
   ├─ Sprint Review/Retro
   └─ Velocity tracking, burndown
```

---

## ✅ Phase 1: Epic Intake Automation (COMPLETE)

### What We Built
- ✅ Google Form for stakeholder intake
- ✅ Google Sheet for IT Leadership review
- ✅ Auto-create JIRA Epics when approved
- ✅ Auto-sync Epic fields (Priority, Due Date, Request Type, Labels)
- ✅ One-way sync: Google Sheet → JIRA
- ✅ Request Type as JIRA custom field (not just label)
- ✅ BRD gate on Story transitions (Railway middleware)

### Files
- `google-apps-script-COMPLETE-WITH-REQUEST-TYPE.txt` - Google Apps Script
- `COMPLETED_PHASE1.md` - Full documentation
- `SETUP_INSTRUCTIONS.md` - Deployment guide

### Production URLs
- **Google Form:** https://forms.gle/w3nfUnipveyAhxss5
- **Google Sheet:** https://docs.google.com/spreadsheets/d/158zDAbms5TR7rIJeTfG6o9FpMDlz3AY2HpYqcizLVtQ/edit
- **JIRA Project:** https://nksaidev.atlassian.net/jira/software/projects/PGMAUTO
- **Railway BRD Gate:** https://pm-automation-system-production.up.railway.app

---

## 📋 Phase 2: Epic Workflow & Roadmap (PLANNED)

### Goal
Manage Epic lifecycle from intake → execution → completion with roadmap visualization.

### Components to Build

#### 2.1 Epic Statuses
Create Epic workflow with these statuses:

```
INTAKE
  ↓ (Stakeholder submits)
UNDER_REVIEW
  ↓ (TPM evaluates: capacity, ROI, strategic alignment)
BACKLOG
  ↓ (Approved but capacity-constrained)
IN_ROADMAP
  ↓ (Scheduled for specific quarter)
IN_EXECUTION
  ↓ (Has Stories in active sprints)
ON_HOLD
  ↓ (Paused: dependency, reprioritized)
COMPLETED or REJECTED
```

#### 2.2 Roadmap Board
Create JIRA board to visualize:
- **Now** (Current quarter - in execution)
- **Next** (Next quarter - ready to start)
- **Later** (Future quarters - backlog)

**Configuration:**
- Board type: Kanban
- Columns: Backlog → Now (Q2) → Next (Q3) → Later (Q4+)
- Filter: `project = PGMAUTO AND issuetype = Epic`
- Swimlanes: By Request Type or Department

#### 2.3 Backlog Management
**Prioritization Fields:**
- Business Value (1-10)
- Technical Complexity (1-10)
- Risk/Dependency flag
- Requestor stakeholder group

**Auto-prioritization logic:**
```javascript
Priority Score = (Business Value × 2) - (Technical Complexity × 1.5)
+ (Risk penalty: -5 if flagged)
+ (P0 requests: +20 boost)
```

#### 2.4 Capacity Planning
**Track:**
- Team capacity per quarter (story points or hours)
- Committed Epics vs. capacity
- Utilization % (visual warning at >80%)

**Auto-alert:**
- When capacity exceeded → Notify TPM
- When Epic at risk of missing quarter → Escalate

#### 2.5 Automation Rules

**Auto-transition Epic statuses:**
```
Trigger: IT Recommendation = "Approve" in Google Sheet
Action: Epic → BACKLOG status

Trigger: Target Quarter field updated in Google Sheet
Action: Epic → IN_ROADMAP status

Trigger: First Story in Epic → In Progress
Action: Epic → IN_EXECUTION status

Trigger: All Stories in Epic → Done
Action: Epic → COMPLETED status
```

**Auto-notify stakeholders:**
```
Trigger: Epic → BACKLOG
Action: Email stakeholder: "Your request has been approved and added to backlog"

Trigger: Epic → IN_ROADMAP
Action: Email stakeholder: "Your request is scheduled for [Quarter]"

Trigger: Epic → IN_EXECUTION
Action: Email stakeholder: "Your request is now in development"

Trigger: Epic → COMPLETED
Action: Email stakeholder: "Your request has been delivered"
```

### Files to Create
- `phase2-epic-workflow-config.json` - JIRA workflow configuration
- `phase2-roadmap-board-config.json` - JIRA board settings
- `phase2-automation-rules.json` - JIRA automation rules
- `phase2-capacity-tracker.js` - Capacity calculation script
- `PHASE2_SETUP.md` - Implementation guide

---

## 📝 Phase 3: Story-Level BRD Workflow (PLANNED)

### Goal
Standardize requirements gathering and ensure Stories are "dev-ready" before sprint commitment.

### Components to Build

#### 3.1 Story Statuses
```
TO_DO
  ↓ (Created from Epic breakdown)
BRD_IN_PROGRESS
  ↓ (BA/TPM defining requirements)
BRD_REVIEW
  ↓ (Tech Lead reviews)
READY_FOR_DEV
  ↓ (BRD approved, acceptance criteria clear)
IN_PROGRESS
  ↓ (Developer working)
CODE_REVIEW
  ↓ (Peer review)
QA_TESTING
  ↓ (QA validates)
DONE
```

#### 3.2 BRD Custom Fields (Story Level)
**Required fields before Story → READY_FOR_DEV:**
- User Story (text): "As a [role], I want [feature], so that [benefit]"
- Acceptance Criteria (multi-line text): Bullet list of testable conditions
- Technical Approach (text): High-level implementation plan
- Dependencies (links): Blocking issues
- Story Points (number): Effort estimate
- Mockups/Designs (attachment): UI screenshots or Figma links

#### 3.3 BRD Gate Validation (Enhanced)
**Expand existing Railway middleware:**

Current BRD gate (Phase 1) blocks transitions on **Stories only**.  
Phase 3 enhances this:

```javascript
// BEFORE: Story can transition to In Progress
// CHECK: All BRD fields filled?
if (!story.userStory || !story.acceptanceCriteria || !story.technicalApproach) {
  return { allowed: false, error: "BRD incomplete. Fill User Story, Acceptance Criteria, Technical Approach." }
}

// BEFORE: Story can transition to READY_FOR_DEV
// CHECK: BRD reviewed by Tech Lead?
if (story.status === "BRD_REVIEW" && !story.brdReviewer) {
  return { allowed: false, error: "BRD must be reviewed by Tech Lead." }
}
```

#### 3.4 Story Templates
**Auto-populate Story description when created from Epic:**

```
## User Story
As a [role], I want [feature], so that [benefit].

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Approach
[Describe implementation at high level]

## Dependencies
[Link blocking issues]

## Testing Notes
[Special testing considerations]

---
**Epic:** [Link to parent Epic]
**Requested by:** [Stakeholder from intake form]
```

#### 3.5 Story Breakdown Workflow
**Option A: Manual (Phase 3a)**
- TPM creates Stories under Epic manually
- Uses Story template
- Fills BRD fields
- Transitions to READY_FOR_DEV when complete

**Option B: Guided Wizard (Phase 3b - Future)**
- Slack/Web UI: "Break down Epic [EPIC-123]"
- Guided form: Title, User Story, Acceptance Criteria
- Auto-creates Stories with BRD template
- Auto-links to Epic

#### 3.6 Definition of Ready Checklist
Before Story enters sprint:
- [ ] User Story written (As a... I want... So that...)
- [ ] Acceptance Criteria defined (testable)
- [ ] Technical Approach documented
- [ ] Story Points estimated
- [ ] Dependencies identified
- [ ] Mockups/designs attached (if UI work)
- [ ] BRD reviewed by Tech Lead

### Files to Create
- `phase3-story-workflow-config.json` - JIRA workflow for Stories
- `phase3-brd-fields-config.json` - Custom field definitions
- `phase3-brd-gate-enhanced.js` - Railway middleware update
- `phase3-story-template.md` - Default Story description template
- `PHASE3_SETUP.md` - Implementation guide

---

## 🏃 Phase 4: Sprint Execution & Metrics (PLANNED)

### Goal
Automate sprint ceremonies, track velocity, and provide real-time metrics to leadership.

### Components to Build

#### 4.1 Scrum Board Configuration
**Columns:**
- TO_DO (Sprint Backlog)
- IN_PROGRESS
- CODE_REVIEW
- QA_TESTING
- DONE

**Swimlanes:** By Epic or Assignee

**Quick Filters:**
- My Issues
- Blocked
- Ready for QA
- Needs Code Review

#### 4.2 Sprint Planning Automation
**Auto-populate sprint backlog:**
```
Trigger: Sprint created
Action: 
  1. Query Stories with status = READY_FOR_DEV
  2. Sort by Priority Score (from Phase 2)
  3. Add top N stories where SUM(story points) ≤ Team Velocity
  4. Notify team: "Sprint backlog ready for review"
```

**Capacity check:**
```
IF: SUM(story points in sprint) > Team Velocity × 1.2
THEN: Alert Scrum Master: "Sprint over-committed by X%"
```

#### 4.3 Daily Standup Automation
**Daily Slack summary (8 AM):**
```
🏃 Sprint 42 - Day 7 of 10

✅ Completed Yesterday:
- [PGMAUTO-101] User login feature
- [PGMAUTO-102] Dashboard widget

🚧 In Progress (3 stories):
- [PGMAUTO-103] API integration (blocked - waiting on vendor)
- [PGMAUTO-104] Report export
- [PGMAUTO-105] Email notifications

⚠️ Blockers (1):
- [PGMAUTO-103] blocked by vendor API delay

📊 Progress: 12/20 story points complete (60%)
🔥 Burndown: On track
```

#### 4.4 Velocity Tracking
**Calculate team velocity:**
```javascript
// Last 3 sprints average
const sprints = [
  { name: "Sprint 39", completed: 18 },
  { name: "Sprint 40", completed: 22 },
  { name: "Sprint 41", completed: 20 }
];

const velocity = sprints.reduce((sum, s) => sum + s.completed, 0) / sprints.length;
// velocity = 20 story points
```

**Trend analysis:**
- Velocity increasing/decreasing over time
- Comparison: committed vs. completed
- Predictability score (variance in velocity)

#### 4.5 Burndown Chart
**Auto-generate:**
- Ideal burndown line (linear)
- Actual burndown (updated daily)
- Scope change line (if stories added mid-sprint)

**Alert if:**
- Actual > Ideal by >20% → "Sprint at risk"
- Day 8 and <50% complete → "Escalate to Scrum Master"

#### 4.6 Sprint Review Automation
**At sprint end:**
1. Auto-generate Sprint Review report:
   - Stories completed
   - Stories carried over
   - Velocity achieved
   - Blockers encountered
   - Stakeholder feedback (manual input)

2. Email report to:
   - Scrum Master
   - Product Owner
   - Stakeholders (from Epics in sprint)

#### 4.7 Retrospective Templates
**Auto-create Confluence page:**
```
# Sprint 42 Retrospective

## What Went Well 🎉
- 

## What Didn't Go Well 😞
- 

## Action Items 🚀
- [ ] Action 1 (Owner: X, Due: Sprint 43)
- [ ] Action 2 (Owner: Y, Due: Sprint 43)

## Metrics
- Velocity: 20 points (planned: 18)
- Stories completed: 8/10
- Carry-over: 2 stories (tech debt)
```

#### 4.8 Metrics Dashboard
**Real-time dashboard (JIRA Dashboard or external BI tool):**

**Sprint Health:**
- Current burndown chart
- Stories by status (pie chart)
- Blockers count (alert if >2)

**Team Performance:**
- Velocity trend (last 6 sprints)
- Predictability score
- Cycle time (avg days from In Progress → Done)

**Epic Progress:**
- Epics in execution (progress bars)
- Stories remaining per Epic
- Forecasted completion date

**Roadmap Status:**
- Epics by quarter (Now/Next/Later)
- Capacity utilization per quarter
- At-risk Epics (missing quarter deadline)

### Files to Create
- `phase4-scrum-board-config.json` - JIRA board configuration
- `phase4-sprint-automation-rules.json` - Sprint planning automation
- `phase4-daily-standup-slack-bot.js` - Slack integration
- `phase4-velocity-tracker.js` - Velocity calculation script
- `phase4-dashboard-config.json` - Metrics dashboard setup
- `PHASE4_SETUP.md` - Implementation guide

---

## 🛠️ Technology Stack

### Current (Phase 1)
- **Intake:** Google Forms + Google Sheets
- **Automation:** Google Apps Script
- **Project Management:** JIRA Cloud (Scrum template)
- **BRD Gate:** Railway (Node.js/Express middleware)
- **API:** JIRA REST API v3

### Planned Additions (Phases 2-4)
- **Workflow Automation:** JIRA Automation (native) + Railway middleware
- **Notifications:** Slack API (for daily standups, alerts)
- **Metrics/BI:** JIRA Dashboards (or Tableau/Power BI if advanced)
- **Documentation:** Confluence (sprint reviews, retros)
- **Capacity Planning:** Custom Google Sheets or JIRA Portfolio

---

## 📊 Success Metrics

### Phase 1 Metrics (Current)
- **Intake submission time:** < 5 minutes
- **Epic creation time:** < 10 seconds (automated)
- **Manual effort saved:** ~15 minutes per Epic (vs. manual JIRA entry)
- **Data accuracy:** 100% (no manual transcription errors)

### Phase 2 Metrics (Target)
- **Backlog prioritization time:** < 30 minutes per quarter
- **Roadmap visibility:** 100% of stakeholders can view roadmap
- **Capacity accuracy:** ±10% variance from planned capacity

### Phase 3 Metrics (Target)
- **BRD completion time:** < 2 hours per Story (down from ~4 hours manual)
- **Dev-ready Stories:** 90% of sprint backlog has complete BRD
- **Rework due to unclear requirements:** < 5% of Stories

### Phase 4 Metrics (Target)
- **Sprint predictability:** 85% of committed Stories completed
- **Velocity variance:** < 15% sprint-to-sprint
- **Time to metrics:** Real-time (vs. weekly manual reports)
- **Standup efficiency:** < 15 minutes (down from 30 minutes manual)

---

## 🚀 Implementation Timeline

| Phase | Duration | Effort | Priority |
|-------|----------|--------|----------|
| **Phase 1: Epic Intake** | ✅ COMPLETE | 2 days | P0 |
| **Phase 2: Epic Workflow & Roadmap** | 2 weeks | 5 days | P1 |
| **Phase 3: Story BRD Workflow** | 3 weeks | 7 days | P1 |
| **Phase 4: Sprint Execution & Metrics** | 4 weeks | 10 days | P2 |

**Total estimated timeline:** 9-10 weeks (calendar time with testing & rollout)

---

## 🔐 Security & Compliance

### Current (Phase 1)
- ✅ JIRA API token stored in Google Apps Script (encrypted at rest)
- ✅ Google Sheet access restricted to IT Leadership
- ✅ Form submissions logged with timestamp + email

### Planned (Phases 2-4)
- [ ] Rotate API tokens every 90 days
- [ ] Implement service account for automation (avoid personal tokens)
- [ ] Audit log for all Epic/Story status changes
- [ ] Stakeholder notification opt-in/opt-out
- [ ] GDPR compliance: Right to delete form submissions

---

## 📞 Support & Contribution

### Maintainers
- **Primary:** nks.ai.dev@gmail.com
- **GitHub:** [your-repo]/pm-automation-system

### Contributing
Contributions welcome for Phases 2-4 implementation!

**To contribute:**
1. Fork the repo
2. Create feature branch: `git checkout -b phase2-roadmap-board`
3. Implement with tests
4. Submit PR with:
   - Implementation guide (PHASE_X_SETUP.md)
   - Configuration files (JSON)
   - Test results (screenshots)

### Roadmap Discussions
- GitHub Issues: Feature requests & bugs
- GitHub Discussions: Architecture decisions for Phases 2-4

---

## 📚 Related Documentation

- [COMPLETED_PHASE1.md](COMPLETED_PHASE1.md) - Phase 1 full documentation
- [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) - Phase 1 deployment guide
- [README.md](README.md) - Project overview
- [SYSTEM_SUMMARY.md](SYSTEM_SUMMARY.md) - Technical architecture

---

## 🎯 Next Steps

### Immediate (Week 1)
- [ ] Test Phase 1 in production with real stakeholder requests
- [ ] Gather feedback from IT Leadership on Google Sheet UX
- [ ] Document any edge cases or bugs

### Short-term (Month 1)
- [ ] Design Phase 2: Epic workflow statuses
- [ ] Build Phase 2: Roadmap board configuration
- [ ] Train TPM on backlog prioritization process

### Mid-term (Months 2-3)
- [ ] Design Phase 3: Story BRD workflow
- [ ] Build Phase 3: Enhanced BRD gate validation
- [ ] Pilot Phase 3 with 1-2 Epics

### Long-term (Months 4-6)
- [ ] Design Phase 4: Sprint automation & metrics
- [ ] Build Phase 4: Slack integrations + dashboards
- [ ] Full rollout across all teams

---

**End of Roadmap**
