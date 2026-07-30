# Phase 3 Implementation — Story-Level BRD Workflow

**Status:** 🏗️ Code & config scaffolded — pending JIRA deployment & end-to-end test
**Scaffolded:** July 30, 2026

> Check items off as you deploy. See `PHASE3_SETUP.md` for the step-by-step guide.

---

## Summary

Phase 3 adds a Story-level Definition of Ready (DoR) gate: a Story must have complete,
Tech-Lead-reviewed requirements before it becomes dev-ready. It extends the Phase 1 BRD
gate from 2 checks to a full 7-field DoR check, adds an 8-status Story workflow, a
description template, and Story-level automation rules.

**Enforcement model:** document-and-advise (middleware validates + comments + labels;
JIRA Automation / workflow validator blocks the transition).

---

## What was built (code complete)

### 1. Story DoR custom fields ✅ (config + script)
- `config/jira-story-fields.json` — 7 DoR fields (5 new + 2 referenced from Phase 1)
- `create_phase3_fields.py` — idempotent creator, **reads `.env`**, `--check` dry-run
- `app/api/setup_routes.py` — `POST /setup/phase3-fields`, `GET /setup/phase3-fields/check`

New fields: User Story, Acceptance Criteria, Technical Approach, BRD Reviewer, Story Points
(skipped if present). Referenced (not recreated): BRD Document Link, BRD Approved Date.

### 2. Story workflow ✅ (config)
- `config/jira-story-workflow.yaml` — 8 statuses, transitions, DoR-gated transitions,
  screens, validators, integration points.

### 3. DoR gate middleware ✅ (code)
- `app/rules/brd_gate.py` — `enforce_dor_gate()` + `check_dor_gate_status()` +
  `_is_empty()` helper; `DOR_REQUIRED_FIELDS`, `DOR_BLOCKED_LABEL` constants.
- `app/webhooks.py` — Story transitions into `READY_FOR_DEV` / `IN_PROGRESS` dispatch the
  DoR gate; non-Story types keep the legacy BRD gate.

### 4. Story template + DoR checklist ✅
- `config/phase3-story-template.md` — default Story description
- Checklist embedded in `PHASE3_SETUP.md`

### 5. Story automation rules ✅ (config)
- `config/jira-story-automation-rules.yaml` — Rules S0–S5.

---

## Deployment checklist (user-run)

- [x] Populate `.env` and run `python create_phase3_fields.py` — **done 2026-07-30**
      (User Story 10153, Acceptance Criteria 10154, Technical Approach 10155,
      BRD Reviewer 10156; Story Points 10040 pre-existing)
- [x] Copy field IDs into `config/jira-story-fields.json` + workflow YAML — **done**
- [ ] Add fields to Story Create/Edit/View screens
- [ ] Build & publish the **Story BRD Workflow** (Story issue type only)
- [ ] Deploy updated middleware to Railway (`git push`)
- [ ] Create Automation rules S0–S5; update BRD Reviewer smart value
- [ ] Point Story transition webhook / validator at the middleware
- [ ] Run the end-to-end test (PHASE3_SETUP.md Step 5)

---

## End-to-end test result

_Fill in after testing:_

- [ ] Story created under Epic → template applied (S0)
- [ ] BRD_REVIEW notifies Tech Lead (S1)
- [ ] DoR-incomplete transition blocked + commented (middleware + S4)
- [ ] DoR-complete transition succeeds + confirmation comment (S2)
- [ ] Full lifecycle to DONE; parent Epic auto-transitions

---

## Next steps

**Phase 3b (future):** Guided breakdown wizard (Slack/Web UI) to create Stories with the
BRD template and auto-link to the Epic.

**Phase 4:** Sprint execution & metrics (scrum board, sprint planning automation, daily
standup Slack bot, velocity/burndown, metrics dashboard).

---

## Lessons / notes

- JIRA Automation cannot cancel a transition mid-flight → chose document-and-advise with
  an S4 revert; a workflow validator gives a hard block if needed.
- Story Points is frequently a built-in agile field → setup script detects & skips.
- All Phase 3 scripts read creds from `.env` (unlike the Phase 2 script) — rotate the
  leaked Phase 2 token separately.
