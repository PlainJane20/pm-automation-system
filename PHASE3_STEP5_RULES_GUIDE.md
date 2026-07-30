# Phase 3 — Step 5: Automation Rules Click-by-Click Guide

Concrete build guide for the Story automation rules, with the real PGMAUTO field
names, field IDs, and Railway URL filled in. Companion to
`config/jira-story-automation-rules.yaml`.

**Location:** Project Settings (PGMAUTO) → **Automation** → **Create rule**

**Field IDs (created 2026-07-30):**
| Field | ID |
|-------|-----|
| User Story | customfield_10153 |
| Acceptance Criteria | customfield_10154 |
| Technical Approach | customfield_10155 |
| BRD Reviewer | customfield_10156 |
| Story Points | customfield_10040 |
| BRD Document Link | customfield_10042 |
| BRD Approved Date | customfield_10044 |

**Middleware URL:** `https://pm-automation-system-production.up.railway.app/webhooks/jira/issue-transitioned`

> **Sequencing:** Enable S0–S2 immediately. Leave **S3 and S4 disabled** until PR #1 is
> merged and the middleware is deployed — otherwise S3's web request hits the old build.

---

## Rule S0 — Apply BRD template on Story creation
- **Trigger:** Work item created
- **Conditions (all):**
  - Issue type = `Story`
  - Parent is not empty
  - Description is empty
- **Actions:**
  1. Edit work item → **Description** = template block from `config/phase3-story-template.md`
  2. Add comment → "📝 BRD template applied. Complete User Story, Acceptance Criteria, and Technical Approach before requesting review."

## Rule S1 — Notify Tech Lead on BRD_REVIEW
- **Trigger:** Work item transitioned → **To status:** `BRD_REVIEW`
- **Condition:** Issue type = `Story`
- **Action:** Send email
  - To: `{{issue.BRD Reviewer.emailAddress}}`
  - Subject: `🔍 BRD review requested: {{issue.key}}`
  - Body: references `{{issue.summary}}`, `{{issue.parent.key}}`, `{{issue.url}}`

## Rule S2 — Mark dev-ready on READY_FOR_DEV
- **Trigger:** Work item transitioned → **To status:** `READY_FOR_DEV`
- **Condition:** Issue type = `Story`
- **Actions:**
  1. Add label `dev-ready`
  2. **Remove** label `dor-gate-blocked`
  3. Add comment → "✅ Definition of Ready satisfied. Story Points: `{{issue.Story Points}}`, Reviewer: `{{issue.BRD Reviewer.displayName}}`"

## Rule S3 — Call middleware to validate DoR  *(enable after merge)*
- **Trigger:** Work item transitioned → **To status:** `READY_FOR_DEV` **or** `IN_PROGRESS`
- **Condition:** Issue type = `Story`
- **Action:** Send web request
  - URL: `https://pm-automation-system-production.up.railway.app/webhooks/jira/issue-transitioned`
  - Method: `POST`
  - Header: `Content-Type: application/json`
  - Body:
    ```json
    {"issue":{"key":"{{issue.key}}","fields":{"issuetype":{"name":"Story"}}},
     "changelog":{"items":[{"field":"status","fromString":"{{fromStatus.name}}","toString":"{{toStatus.name}}"}]}}
    ```

## Rule S4 — Block/revert when DoR incomplete  *(enable after merge)*
- **Trigger:** Field value changed → **Field:** `Labels`
- **Conditions (all):**
  - Issue has label `dor-gate-blocked`
  - Status is one of `READY_FOR_DEV`, `IN_PROGRESS`
- **Actions:**
  1. Transition work item → **`Send Back for Rework`** (→ BRD_IN_PROGRESS)
  2. Send email → To `{{issue.assignee.emailAddress}}`, Subject `⛔ {{issue.key}} not dev-ready — DoR incomplete`, body points at the middleware's comment listing missing fields

## Rule S5 — PR Link → Code Review  *(optional, keep disabled until GitHub webhook populates PR Link)*
- **Trigger:** Field value changed → **Field:** `PR Link`
- **Conditions:** Status = `IN_PROGRESS` **AND** PR Link is not empty
- **Actions:** Transition → `Submit for Code Review`; comment "🔀 PR linked ({{issue.PR Link}})."

---

## Test after building (Step 6)
1. Create a Story under an Epic → S0 applies template.
2. Enter `BRD_REVIEW` → S1 emails the BRD Reviewer.
3. Approve `BRD_REVIEW → READY_FOR_DEV` with DoR incomplete → S3 → middleware comments
   missing fields + adds `dor-gate-blocked` → S4 reverts to `BRD_IN_PROGRESS`.
4. Fill all 7 DoR fields → approve → middleware posts ✅ → S2 adds `dev-ready`, clears block.
5. Advance `IN_PROGRESS → CODE_REVIEW → QA_TESTING → DONE`; confirm parent Epic
   auto-transitions to IN_EXECUTION (Epic Rule 12) and auto-completes (Epic Rule 13).

## Smart-value notes
- Named custom fields with spaces are referenced directly: `{{issue.User Story}}`,
  `{{issue.BRD Reviewer.emailAddress}}`, `{{issue.Story Points}}`.
- Document-and-advise: the middleware never cancels a transition mid-flight; S4 reverts
  after the fact. For a hard synchronous block, use a workflow validator hitting the
  middleware URL instead (see `jira-story-workflow.yaml` validator_endpoint).
