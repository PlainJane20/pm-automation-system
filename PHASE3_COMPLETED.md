# Phase 3 Implementation — Story-Level BRD Workflow

**Status:** ✅ Deployed & validated end-to-end in live JIRA (PGMAUTO)
**Scaffolded:** July 30, 2026
**Deployed & tested:** July 30, 2026

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
- [x] Add fields to Story Create/Edit/View screens — **done 2026-07-30**
      (added to screen 10005 / tab 10008, the shared PGMAUTO default screen)
- [x] Build & publish the **Story BRD Workflow** (Story issue type only) — **done 2026-07-30**
      (8 statuses; added a multi-source "Send Back to BRD" revert transition for S4;
      native "Definition of Ready incomplete" validator on Approve to Ready → READY FOR DEV)
- [x] Deploy updated middleware to Railway (`git push`) — **done** (`/health` healthy,
      `/setup/phase3-fields/check` → all_exist:true)
- [x] Create Automation rules S0–S4 — **done 2026-07-30** (S0 template, S1 notify reviewer,
      S2 dev-ready label, S3 middleware web request, S4 revert on dor-gate-blocked).
      S5 (PR Link → Code Review) left disabled pending GitHub webhook.
- [x] Point Story transition webhook / validator at the middleware — **done** (S3 → Railway)
- [x] Run the end-to-end test (PHASE3_SETUP.md Step 5) — **done 2026-07-30, all passed**

---

## End-to-end test result — ✅ ALL PASSED (2026-07-30)

Tested on **PGMAUTO-9 "DoR Gate Test Story"** (under Epic PGMAUTO-4 "AIRS"), plus a
second Story to exercise the Epic auto-activation:

- [x] Story created under Epic → template applied (S0) — Description auto-populated with
      resolved smart-values (Epic link, "Requested by", DoR notice)
- [x] DoR-incomplete transition **hard-blocked** with a native validator listing all 7
      required fields ("Definition of Ready incomplete…") — synchronous block
- [x] DoR-complete transition succeeds → status holds at READY FOR DEV (no S4 bounce)
- [x] `dev-ready` label added + ✅ "Definition of Ready satisfied" comment (S2); the
      comment resolved custom fields (`Story Points: 5.0`, `BRD Reviewer: Navi`),
      confirming the custom fields — not just the Description — are populated
- [x] Belt-and-suspenders DoR re-check on READY FOR DEV → IN PROGRESS passed clean
- [x] Full lifecycle IN PROGRESS → CODE REVIEW → QA → DONE ran with no errors
- [x] **Parent Epic auto-transitioned In Roadmap → In Execution** (Epic Rule 12) when a
      child Story hit IN PROGRESS

### Epic notification rules — cleaned up (2026-07-30)
Three Epic email rules (**Approval Notification**, **Rejection Notification**,
**Schedule to Roadmap When Quarter Assigned**) originally emailed a non-existent
`{{issue.Email Address}}` field, causing "Please provide at least one valid recipient."
Fixed each to email `{{issue.reporter.emailAddress}}`, set a static Email name, and
replaced display-name body references with field IDs (`{{issue.customfield_10082}}`
Rejection Reason, `{{issue.customfield_10083}}` Alternative Approach). Story S1 was also
gated with a "BRD Reviewer is not empty" condition so it only notifies when a reviewer
is set. All rule configs are now verified clean.

### Key finding — Automation ⚠️ badge is run-based, not config-based
The red ⚠️ badge on the Flows list reflects a rule's **last execution status** (or a
pre-run warning for rules that have never fired). Editing/saving correct config does **not**
clear it — only a successful run does. Confirmed with Story S1: it stayed ⚠️ through every
config edit and went green only after it executed successfully. The remaining ⚠️ on the
three Epic email rules is therefore cosmetic run-history — their configs are correct and each
badge clears the first time that Epic-lifecycle event actually happens (approve / reject /
schedule) in real use.

### Key finding — Epic Rule 12 precondition
Rule 12 ("Epic: Activate on Story Development Start") only fires when the **parent Epic is
in `IN_ROADMAP`**. On the first attempt the Epic sat in `UNDER_REVIEW`, so the rule
correctly triggered-and-skipped (condition `{{issue.parent.status.name}} equals In Roadmap`
failed). After advancing PGMAUTO-4 through UNDER_REVIEW → BACKLOG → IN_ROADMAP (filling
Business Value Score, Technical Complexity Score, Committed Quarter, Team Capacity
Allocation), a fresh Story's Start Development correctly flipped the Epic to `IN_EXECUTION`.
This is intended behavior — un-roadmapped Epics should not auto-activate.

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
