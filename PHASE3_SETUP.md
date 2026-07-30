# Phase 3 Setup Guide — Story-Level BRD Workflow

**Goal:** Standardize requirements gathering so every Story is provably *dev-ready*
(Definition of Ready) before it enters a sprint.

**Enforcement model:** Document-and-advise. The Railway middleware validates the
Definition of Ready and, on a violation, comments on the Story and adds a
`dor-gate-blocked` label. A JIRA Automation rule (or a workflow validator) performs the
actual transition block. This matches the Phase 1 BRD-gate pattern.

**Prerequisites:** Phases 1 & 2 complete; `.env` populated with `JIRA_URL`,
`JIRA_EMAIL`, `JIRA_API_TOKEN`; Railway middleware deployable.

---

## Deliverables in this phase

| Artifact | File |
|----------|------|
| Story DoR fields (config) | `config/jira-story-fields.json` |
| Field setup script (reads `.env`) | `create_phase3_fields.py` |
| Story workflow (8 statuses) | `config/jira-story-workflow.yaml` |
| Story automation rules (S0–S5) | `config/jira-story-automation-rules.yaml` |
| Story description template | `config/phase3-story-template.md` |
| DoR gate middleware | `app/rules/brd_gate.py` (`enforce_dor_gate`) |
| Webhook dispatch | `app/webhooks.py` |
| Setup API endpoints | `app/api/setup_routes.py` (`/setup/phase3-fields`) |

---

## Step 1 — Create the Story DoR custom fields

The gate needs seven fields. Two already exist from Phase 1 (BRD Document Link, BRD
Approved Date) and are **not** recreated. The rest are created idempotently — existing
fields (e.g. Story Points) are detected and skipped.

**Option A — script:**
```bash
cd pm-automation-system
python create_phase3_fields.py --check   # dry run: shows what's missing
python create_phase3_fields.py           # create missing fields
```

**Option B — API (if the app is running):**
```bash
curl -X GET  https://<your-app>/setup/phase3-fields/check
curl -X POST https://<your-app>/setup/phase3-fields
```

Copy the printed field IDs into `config/jira-story-fields.json` and
`config/jira-story-workflow.yaml` (the `custom_fields:` block).

Then in the JIRA UI: **Settings → Issues → Screens** — add the new fields to the
Story **Create / Edit / View** screens (grouped as the "Story BRD Screen" in the
workflow YAML).

---

## Step 2 — Create the Story workflow

JIRA has no YAML import, so build this from `config/jira-story-workflow.yaml`:

1. **Project Settings (PGMAUTO) → Workflows → Add workflow → Create from scratch**
2. Name: **Story BRD Workflow**
3. Add the 8 statuses:
   `TO_DO → BRD_IN_PROGRESS → BRD_REVIEW → READY_FOR_DEV → IN_PROGRESS → CODE_REVIEW → QA_TESTING → DONE`
4. Add the transitions listed in the YAML, with native validators (required fields).
5. On the two **DoR-gated** transitions
   (`BRD_REVIEW → READY_FOR_DEV` and `READY_FOR_DEV → IN_PROGRESS`) either:
   - add a **workflow validator** that calls the middleware endpoint (hard block), **or**
   - rely on Automation rules S3 + S4 (label round-trip; see Step 4).
6. Associate the workflow with the **Story issue type only**.
7. Publish (map existing Stories to `TO_DO` during migration).

---

## Step 3 — Deploy the DoR gate middleware

The middleware is already wired:

- `app/rules/brd_gate.py::enforce_dor_gate` — checks all seven DoR fields; on failure
  comments + adds `dor-gate-blocked`; on pass adds a confirmation comment. Bugs and
  Support Requests skip the gate.
- `app/webhooks.py::handle_issue_transitioned` — for **Story** issue types, dispatches
  `enforce_dor_gate` on transitions into `READY_FOR_DEV` or `IN_PROGRESS`. Non-Story
  types keep the legacy Phase 1 `enforce_brd_gate`.

Deploy to Railway (same service as Phases 1–2):
```bash
git add app/ config/ create_phase3_fields.py PHASE3_SETUP.md PHASE3_COMPLETED.md
git commit -m "Phase 3: Story BRD / Definition-of-Ready workflow"
git push   # Railway auto-deploys
```

Confirm the webhook `/webhooks/jira/issue-transitioned` is reachable and that a JIRA
webhook (or Automation rule S3) is pointed at it for Story transitions.

---

## Step 4 — Create the Story automation rules

From `config/jira-story-automation-rules.yaml`, create in **Project Settings →
Automation**:

| Rule | Purpose |
|------|---------|
| **S0** | Apply the BRD template to new Stories created under an Epic |
| **S1** | Email the BRD Reviewer (Tech Lead) when a Story enters `BRD_REVIEW` |
| **S2** | Mark dev-ready + clear `dor-gate-blocked` on `READY_FOR_DEV` |
| **S3** | Call the middleware to validate DoR on dev-ready transitions |
| **S4** | Revert to `BRD_IN_PROGRESS` when `dor-gate-blocked` is present |
| **S5** | (optional) PR Link → `CODE_REVIEW` |

Update the BRD Reviewer smart value to match your exact field name, then enable each
rule after testing.

---

## Definition of Ready checklist

A Story may not move to `READY_FOR_DEV` until **all** are true:

- [ ] User Story written (As a… I want… so that…)
- [ ] Acceptance Criteria defined and testable
- [ ] Technical Approach documented
- [ ] Story Points estimated
- [ ] BRD Document Link populated
- [ ] BRD Approved Date set
- [ ] BRD Reviewer (Tech Lead) assigned

---

## Step 5 — End-to-end test

1. Create a Story under an existing Epic → **S0** applies the template.
2. Move to `BRD_REVIEW` with fields blank → native validator blocks; **S1** emails the reviewer.
3. Approve `BRD_REVIEW → READY_FOR_DEV` with DoR incomplete →
   middleware comments the missing fields + adds `dor-gate-blocked`; **S4** reverts to `BRD_IN_PROGRESS`.
4. Fill all seven DoR fields → approve → middleware posts the ✅ confirmation; **S2** adds
   `dev-ready` and clears `dor-gate-blocked`.
5. Advance `IN_PROGRESS → CODE_REVIEW → QA_TESTING → DONE`; verify the parent Epic
   auto-transitions to `IN_EXECUTION` on first Story start (Epic Rule 12) and
   auto-completes when all Stories are `DONE` (Epic Rule 13).

---

## Notes & known limitations

- **Document-and-advise vs. hard block:** JIRA Automation can't cancel a transition
  mid-flight, so S4 reverts the Story after the fact. For a true synchronous block,
  configure the DoR transition with a **workflow validator** hitting the middleware
  (`validator_endpoint` in the workflow YAML) instead of the S3/S4 label round-trip.
- **Story Points** is often a built-in agile field; the setup script detects and skips it.
- **Security:** all Phase 3 scripts read credentials from `.env`. Note the pre-existing
  hardcoded token in `create_phase2_fields.py` — rotate and scrub it separately.
