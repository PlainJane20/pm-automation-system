# Phase 3 Story Description Template

Auto-populated into a Story's Description when it is created under an Epic
(see config/jira-story-automation-rules.yaml, Rule S0). Authors fill each section
during BRD_IN_PROGRESS; the fields feed the Definition of Ready gate.

---

## User Story
As a [role], I want [feature], so that [benefit].

## Acceptance Criteria
- [ ] Criterion 1 (testable)
- [ ] Criterion 2 (testable)
- [ ] Criterion 3 (testable)

## Technical Approach
[Describe the implementation at a high level: components touched, key decisions,
any spikes or dependencies to resolve first.]

## Dependencies
[Link blocking issues or external dependencies. Use "is blocked by" links.]

## Testing Notes
[Special testing considerations, edge cases, data setup, environments.]

---
**Epic:** {{issue.epic.key}} — {{issue.epic.summary}}
**Requested by:** {{issue.epic.reporter.displayName}}

> Definition of Ready: this Story cannot move to READY_FOR_DEV until User Story,
> Acceptance Criteria, Technical Approach, Story Points, BRD Document Link,
> BRD Approved Date, and BRD Reviewer are all complete.
