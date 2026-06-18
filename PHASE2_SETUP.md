# Phase 2 Setup Guide: Epic Workflow & Roadmap

**Estimated Time:** 4-6 hours  
**Skill Level:** JIRA Admin  
**Prerequisites:** Phase 1 complete (Epic auto-creation working)

---

## Overview

This guide walks you through implementing Phase 2: Epic Workflow & Roadmap.

**What You'll Build:**
- ✅ 7-status Epic workflow (INTAKE → COMPLETED/REJECTED)
- ✅ 11 custom fields for capacity planning
- ✅ 8 automation rules for notifications & transitions
- ✅ Roadmap Kanban board (Now/Next/Later)
- ✅ Capacity validation (blocks over-committed quarters)

**Timeline:** 1-2 days (with testing)

---

## Prerequisites Checklist

Before starting, ensure:
- [ ] You have JIRA admin access
- [ ] Phase 1 is working (Epics are being created from intake form)
- [ ] You have at least 1 test Epic in JIRA (for testing transitions)
- [ ] You've read `docs/epic-workflow-design.md` (understand the workflow)
- [ ] Railway middleware is running (for capacity validation)

---

## Part 1: Create Custom Fields (30-45 minutes)

### Step 1.1: Access Custom Fields

1. **Go to:** JIRA → Settings (⚙️ icon, top right)
2. **Click:** Issues → Custom fields
3. **Click:** "Create custom field" (top right button)

---

### Step 1.2: Create Each Field

Create these 11 fields one by one:

#### Field 1: Business Value Score

- **Field Type:** Number field
- **Name:** `Business Value Score`
- **Description:** `Business impact rating (1-10 scale)`
- **Searcher:** Number range searcher
- **Associate with screens:** Epic Create Screen, Epic Edit Screen
- **Associate with issue types:** Epic only
- **Click:** Create

**After creation:**
- Go to field configuration
- Set as **Required** for Epic issue type
- Add field to Epic screens (if not already)

---

#### Field 2: Technical Complexity Score

- **Field Type:** Number field
- **Name:** `Technical Complexity Score`
- **Description:** `Technical difficulty rating (1-10 scale)`
- **Associate with screens:** Epic Create Screen, Epic Edit Screen
- **Associate with issue types:** Epic only

---

#### Field 3: Risk Flags

- **Field Type:** Checkboxes (multi-select)
- **Name:** `Risk Flags`
- **Description:** `Epic-level risk categories`
- **Options (one per line):**
  ```
  Vendor Dependency
  Data Migration
  Third-party API
  Compliance Requirement
  Security Review Required
  Infrastructure Changes
  Cross-team Dependencies
  ```
- **Associate with issue types:** Epic only

---

#### Field 4: Committed Quarter

- **Field Type:** Select List (single choice)
- **Name:** `Committed Quarter`
- **Description:** `Target delivery quarter`
- **Options (one per line):**
  ```
  Q1 2026
  Q2 2026
  Q3 2026
  Q4 2026
  Q1 2027
  Q2 2027
  Q3 2027
  Q4 2027
  ```
- **Associate with issue types:** Epic only
- **Set as Required:** Yes (for IN_ROADMAP status)

---

#### Field 5: Team Capacity Allocation (%)

- **Field Type:** Number field
- **Name:** `Team Capacity Allocation (%)`
- **Description:** `Percentage of team capacity needed for this Epic`
- **Associate with issue types:** Epic only
- **Set as Required:** Yes (for IN_ROADMAP status)

---

#### Field 6: Rejection Reason

- **Field Type:** Text Field (multi-line)
- **Name:** `Rejection Reason`
- **Description:** `Reason why Epic was rejected`
- **Associate with issue types:** Epic only
- **Set as Required:** Yes (for REJECTED status)

---

#### Field 7: Alternative Approach

- **Field Type:** Text Field (multi-line)
- **Name:** `Alternative Approach`
- **Description:** `Suggested alternative to rejected request`
- **Associate with issue types:** Epic only

---

#### Field 8: Hold Reason

- **Field Type:** Text Field (multi-line)
- **Name:** `Hold Reason`
- **Description:** `Reason why Epic is on hold`
- **Associate with issue types:** Epic only
- **Set as Required:** Yes (for ON_HOLD status)

---

#### Field 9: Blocker Type

- **Field Type:** Select List (single choice)
- **Name:** `Blocker Type`
- **Description:** `Category of blocker`
- **Options:**
  ```
  External Dependency
  Reprioritized
  Budget Constraint
  Resource Unavailable
  Technical Blocker
  Stakeholder Decision Pending
  ```
- **Associate with issue types:** Epic only

---

#### Field 10: Expected Resume Date

- **Field Type:** Date Picker
- **Name:** `Expected Resume Date`
- **Description:** `When Epic is expected to resume`
- **Associate with issue types:** Epic only

---

#### Field 11: Completion Date

- **Field Type:** Date Picker
- **Name:** `Completion Date`
- **Description:** `Date when Epic was completed`
- **Associate with issue types:** Epic only
- **Default Value:** None (auto-set by automation)

---

### Step 1.3: Document Field IDs

After creating all fields, **document their IDs**:

1. Go back to Settings → Issues → Custom fields
2. For each field, click "..." → View field details
3. **Copy the field ID** (e.g., `customfield_10042`)
4. **Update** `config/jira-custom-fields.json` with actual IDs

**Example:**
```json
{
  "business_value_score": "customfield_10042",
  "technical_complexity_score": "customfield_10043",
  "committed_quarter": "customfield_10044",
  ...
}
```

**⚠️ Important:** You'll need these IDs later for Railway middleware configuration.

---

## Part 2: Create Epic Workflow (60-90 minutes)

### Step 2.1: Create New Workflow

1. **Go to:** JIRA → Project Settings (PGMAUTO) → Workflows
2. **Click:** "Add workflow"
3. **Select:** "Create from scratch"
4. **Name:** `Epic Lifecycle Workflow`
5. **Description:** `Strategic program management workflow for Epics`
6. **Click:** Create

---

### Step 2.2: Add Statuses

**Add these 8 statuses:**

1. **INTAKE**
   - Category: To Do
   - Description: "New request from stakeholder"

2. **UNDER_REVIEW**
   - Category: In Progress
   - Description: "TPM evaluating capacity, ROI, alignment"

3. **BACKLOG**
   - Category: To Do
   - Description: "Approved but not yet scheduled"

4. **IN_ROADMAP**
   - Category: In Progress
   - Description: "Scheduled for specific quarter"

5. **IN_EXECUTION**
   - Category: In Progress
   - Description: "Active development in sprints"

6. **ON_HOLD**
   - Category: To Do
   - Description: "Paused due to blocker"

7. **COMPLETED**
   - Category: Done
   - Description: "All work delivered"

8. **REJECTED**
   - Category: Done
   - Description: "Request denied"

**How to add:**
- In workflow diagram, click "+ Add status"
- Fill in name, category, description
- Repeat for all 8 statuses

---

### Step 2.3: Create Transitions

**Create these transitions** (drag arrows between statuses in diagram):

| From | To | Name | Type |
|------|-----|------|------|
| INTAKE | UNDER_REVIEW | Start Review | Manual |
| UNDER_REVIEW | BACKLOG | Approve to Backlog | Manual |
| UNDER_REVIEW | REJECTED | Reject Request | Manual |
| BACKLOG | IN_ROADMAP | Schedule to Roadmap | Manual |
| IN_ROADMAP | IN_EXECUTION | Start Execution | Auto |
| IN_ROADMAP | ON_HOLD | Put On Hold | Manual |
| IN_EXECUTION | COMPLETED | Complete Epic | Auto |
| IN_EXECUTION | ON_HOLD | Hold Execution | Manual |
| ON_HOLD | IN_ROADMAP | Resume to Roadmap | Manual |
| ON_HOLD | IN_EXECUTION | Resume Execution | Manual |

**For each transition:**
1. Click on arrow in diagram
2. Set transition name
3. Configure validators (see next step)
4. Configure post-functions (see step after)

---

### Step 2.4: Add Validators to Transitions

**UNDER_REVIEW → BACKLOG:**
- Validator: "Field Required" → Business Value Score
- Validator: "Field Required" → Technical Complexity Score

**UNDER_REVIEW → REJECTED:**
- Validator: "Field Required" → Rejection Reason

**BACKLOG → IN_ROADMAP:**
- Validator: "Field Required" → Committed Quarter
- Validator: "Field Required" → Team Capacity Allocation (%)
- Validator: "Permission" → Only IT Leadership/TPM can execute

**→ ON_HOLD (from any status):**
- Validator: "Field Required" → Hold Reason
- Validator: "Field Required" → Blocker Type

---

### Step 2.5: Add Post-Functions to Transitions

**INTAKE → UNDER_REVIEW:**
- Post-function: "Assign to user" → Project lead or TPM
- Post-function: "Add comment" → "Epic moved to review. TPM will evaluate."

**UNDER_REVIEW → BACKLOG:**
- Post-function: "Add label" → "approved"

**BACKLOG → IN_ROADMAP:**
- Post-function: "Add label" → "roadmap-{{Committed Quarter}}"

**IN_EXECUTION → COMPLETED:**
- Post-function: "Set field value" → Completion Date = {{now}}
- Post-function: "Add label" → "delivered"

---

### Step 2.6: Set Initial Status

1. In workflow editor, right-click "INTAKE" status
2. Select "Set as initial status"
3. This ensures new Epics start in INTAKE

---

### Step 2.7: Publish Workflow

1. **Click:** "Publish" (top right)
2. **Review:** All statuses and transitions
3. **Confirm:** Publish workflow

---

### Step 2.8: Associate with Epic Issue Type

1. **Go to:** Project Settings → Workflows
2. **Find:** "Epic Lifecycle Workflow"
3. **Click:** Associate with Epic issue type
4. **Confirm:** This replaces any existing Epic workflow

**⚠️ Warning:** This affects ALL existing Epics in project. Test first!

---

## Part 3: Create Automation Rules (45-60 minutes)

**Go to:** Project Settings (PGMAUTO) → Automation

Create these 8 rules:

---

### Rule 1: Welcome Comment

**Click:** Create rule → Choose trigger: "Issue created"

**Configuration:**
- **Trigger:** Issue created
- **IF condition:** Issue type = Epic AND Status = INTAKE
- **THEN action 1:** Add comment:
  ```
  🎉 Welcome to the PMO!

  Your request is now in the intake queue and will be reviewed within 3-5 business days.

  Epic ID: {{issue.key}}
  Submitted by: {{issue.Email Address}}
  ```
- **THEN action 2:** Assign to project lead (select user)
- **Name rule:** "Epic: Welcome Comment on Creation"
- **Turn on:** Enable

---

### Rule 2: Schedule to Roadmap

**Click:** Create rule → Choose trigger: "Field value changed"

**Configuration:**
- **Trigger:** Field value changed → Committed Quarter
- **IF condition 1:** Issue type = Epic
- **IF condition 2:** Committed Quarter is not empty
- **IF condition 3:** Status = BACKLOG
- **THEN action 1:** Transition issue → Schedule to Roadmap
- **THEN action 2:** Add label → "roadmap-{{issue.Committed Quarter}}"
- **THEN action 3:** Send email:
  - To: {{issue.Email Address}}
  - Subject: "Your Request Scheduled for {{issue.Committed Quarter}}"
  - Body:
    ```
    Hello,

    Your request has been scheduled for delivery in {{issue.Committed Quarter}}.

    Epic: {{issue.key}} - {{issue.summary}}
    Priority: {{issue.Priority}}

    View Epic: {{issue.url}}

    Best regards,
    IT Program Management
    ```
- **Name rule:** "Epic: Schedule to Roadmap When Quarter Assigned"
- **Turn on:** Enable

---

### Rule 3: Start Execution (Auto)

**Click:** Create rule → Choose trigger: "Issue transitioned"

**Configuration:**
- **Trigger:** Issue transitioned
- **From status:** READY_FOR_DEV
- **To status:** IN_PROGRESS
- **IF condition 1:** Issue type = Story
- **IF condition 2:** Parent is not empty
- **IF condition 3:** Related issue (parent) → Issue type = Epic
- **IF condition 4:** Related issue (parent) → Status = IN_ROADMAP
- **THEN action 1:** Transition related issues (parent) → Start Execution
- **THEN action 2:** Send email:
  - To: {{parent.Email Address}}
  - Subject: "Development Started on Your Request"
  - Body: (see config/jira-epic-automation-rules.yaml for template)
- **THEN action 3 (optional):** Post to Slack #program-updates
- **Name rule:** "Epic: Activate on Story Development Start"
- **Turn on:** Enable

---

### Rule 4: Auto-Complete Epic

**Click:** Create rule → Choose trigger: "Scheduled"

**Configuration:**
- **Trigger:** Scheduled → Daily at 9:00 AM
- **For each issue matching JQL:**
  ```
  project = PGMAUTO AND issuetype = Epic AND status = IN_EXECUTION
  ```
- **IF condition:** Related issues (children) → JQL:
  ```
  status NOT IN (DONE, CLOSED)
  ```
  → Count equals 0
- **THEN action 1:** Transition issue → Complete Epic
- **THEN action 2:** Set field value → Completion Date = {{now}}
- **THEN action 3:** Add label → "delivered"
- **THEN action 4:** Send email:
  - To: {{issue.Email Address}}
  - Subject: "Your Request Has Been Delivered! ✅"
  - Body: (see config for template)
- **Name rule:** "Epic: Auto-Complete When All Stories Done"
- **Turn on:** Enable

---

### Rule 5: Rejection Notification

**Click:** Create rule → Choose trigger: "Issue transitioned"

**Configuration:**
- **Trigger:** Issue transitioned → To status: REJECTED
- **IF condition:** Issue type = Epic
- **THEN action:** Send email:
  - To: {{issue.Email Address}}
  - Subject: "Request Status Update: Not Approved"
  - Body:
    ```
    Thank you for submitting your request.

    After review, we are unable to proceed at this time.

    Epic: {{issue.key}} - {{issue.summary}}
    Reason: {{issue.Rejection Reason}}

    {{#if issue.Alternative Approach}}
    Alternative Suggested: {{issue.Alternative Approach}}
    {{/if}}

    Questions? Contact your TPM.
    ```
- **Name rule:** "Epic: Rejection Notification"
- **Turn on:** Enable

---

### Rule 6: On Hold Notification

**Click:** Create rule → Choose trigger: "Issue transitioned"

**Configuration:**
- **Trigger:** Issue transitioned → To status: ON_HOLD
- **IF condition:** Issue type = Epic
- **THEN action:** Send email:
  - To: {{issue.Email Address}}
  - Subject: "Request Temporarily On Hold"
  - Body:
    ```
    Your request is temporarily on hold.

    Epic: {{issue.key}} - {{issue.summary}}
    Reason: {{issue.Hold Reason}}
    Blocker Type: {{issue.Blocker Type}}

    {{#if issue.Expected Resume Date}}
    Expected Resume: {{issue.Expected Resume Date}}
    {{/if}}

    We'll notify you when development resumes.
    ```
- **Name rule:** "Epic: On Hold Notification"
- **Turn on:** Enable

---

### Rule 7: Capacity Warning

**Click:** Create rule → Choose trigger: "Issue transitioned"

**Configuration:**
- **Trigger:** Issue transitioned → To status: IN_ROADMAP
- **IF condition 1:** Issue type = Epic
- **IF condition 2:** Issue has label: "capacity-warning"
- **THEN action:** Send email:
  - To: tpm@company.com (UPDATE with actual email!)
  - Subject: "⚠️ Capacity Warning: {{issue.Committed Quarter}}"
  - Body:
    ```
    Warning: Quarter capacity >80% utilized.

    Quarter: {{issue.Committed Quarter}}
    Latest Epic: {{issue.key}} - {{issue.summary}}

    Review roadmap for over-commitment risk.
    ```
- **Name rule:** "Epic: Capacity Warning for TPM"
- **Turn on:** Enable

---

### Rule 8: Approval Notification

**Click:** Create rule → Choose trigger: "Issue transitioned"

**Configuration:**
- **Trigger:** Issue transitioned → To status: BACKLOG
- **IF condition:** Issue type = Epic
- **THEN action:** Send email:
  - To: {{issue.Email Address}}
  - Subject: "Your Request Has Been Approved"
  - Body:
    ```
    Great news! Your request has been approved.

    Epic: {{issue.key}} - {{issue.summary}}
    Business Value Score: {{issue.Business Value Score}}/10

    Next: Your request will be scheduled for a specific quarter based on capacity.

    View Epic: {{issue.url}}
    ```
- **Name rule:** "Epic: Approval Notification"
- **Turn on:** Enable

---

## Part 4: Create Roadmap Board (30-45 minutes)

### Step 4.1: Create Kanban Board

1. **Go to:** Boards → Create board
2. **Select:** Kanban board
3. **Name:** `PMO Roadmap - Epics`
4. **Project:** PGMAUTO
5. **Click:** Create board

---

### Step 4.2: Configure Board Filter

1. **Click:** Board → Board settings (⚙️ icon, top right)
2. **Click:** Edit filter query
3. **Set JQL:**
   ```
   project = PGMAUTO 
   AND issuetype = Epic 
   AND status IN (BACKLOG, IN_ROADMAP, IN_EXECUTION, COMPLETED, ON_HOLD)
   ORDER BY "Committed Quarter" ASC, Priority DESC
   ```
4. **Save filter**

---

### Step 4.3: Configure Columns

**Go to:** Board settings → Columns

**Delete default columns**, create these:

1. **Backlog**
   - Status: BACKLOG

2. **Now - Q2 2026**
   - Status: IN_ROADMAP
   - Filter: Committed Quarter = Q2 2026

3. **Next - Q3 2026**
   - Status: IN_ROADMAP
   - Filter: Committed Quarter = Q3 2026

4. **Later - Q4+ 2026**
   - Status: IN_ROADMAP
   - Filter: Committed Quarter >= Q4 2026

5. **In Execution**
   - Status: IN_EXECUTION

6. **On Hold**
   - Status: ON_HOLD

7. **Completed**
   - Status: COMPLETED

**Note:** You'll need to manually update "Now/Next/Later" column filters each quarter.

---

### Step 4.4: Configure Swimlanes

**Go to:** Board settings → Swimlanes

- **Group by:** Request Type (customfield_10041)
- **Swimlanes:**
  - Project Request (large initiative, multiple features)
  - Enhancement Request (improve existing feature)
  - Feature Request (new capability)
  - Bug Fix Request (production issue)

---

### Step 4.5: Configure Card Layout

**Go to:** Board settings → Card layout

**Show these fields on cards:**
- Priority
- Committed Quarter
- Business Value Score
- Team Capacity Allocation (%)
- Assignee

**Card colors:**
- **Priority = Highest (P0)** → Red
- **Priority = High (P1)** → Orange
- **Priority = Medium (P2)** → Yellow
- **Priority = Low (P3)** → Green

---

### Step 4.6: Create Quick Filters

**Go to:** Board settings → Quick filters

**Add these:**

1. **At Risk**
   - Name: "At Risk"
   - JQL: `duedate < 30d AND status != COMPLETED`

2. **P0 Only**
   - Name: "P0 Only"
   - JQL: `priority = Highest`

3. **This Quarter**
   - Name: "This Quarter"
   - JQL: `"Committed Quarter" = "Q3 2026"`  (update each quarter)

4. **Over Capacity**
   - Name: "Over Capacity"
   - JQL: `labels = capacity-warning`

---

## Part 5: Update Google Apps Script (Optional, 15 minutes)

**Only do this if you want Epic status synced back to Google Sheet.**

### Step 5.1: Open Apps Script

1. Open your Google Sheet (intake responses)
2. Extensions → Apps Script

---

### Step 5.2: Add New Column

In Google Sheet:
- Add new column: **R** (Epic Status)
- Header: "Epic Status"

---

### Step 5.3: Add Sync Function

At the end of your script, add:

```javascript
function syncEpicStatusFromJira() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const lastRow = sheet.getLastRow();
  
  for (let row = 2; row <= lastRow; row++) {
    const epicLink = sheet.getRange(row, CONFIG.COLUMNS.JIRA_EPIC_LINK + 1).getValue();
    
    if (epicLink && epicLink.trim() !== '') {
      const epicKey = extractEpicKey(epicLink);
      
      const url = CONFIG.JIRA_URL + '/rest/api/3/issue/' + epicKey;
      const options = {
        method: 'get',
        headers: {
          'Authorization': 'Basic ' + Utilities.base64Encode(CONFIG.JIRA_EMAIL + ':' + CONFIG.JIRA_API_TOKEN)
        },
        muteHttpExceptions: true
      };
      
      const response = UrlFetchApp.fetch(url, options);
      
      if (response.getResponseCode() === 200) {
        const epic = JSON.parse(response.getContentText());
        const status = epic.fields.status.name;
        
        sheet.getRange(row, 18).setValue(status);  // Column R
        
        // Color coding
        if (status === 'COMPLETED') {
          sheet.getRange(row, 18).setBackground('#d4edda');  // Green
        } else if (status === 'IN_EXECUTION') {
          sheet.getRange(row, 18).setBackground('#fff3cd');  // Yellow
        } else if (status === 'REJECTED') {
          sheet.getRange(row, 18).setBackground('#f8d7da');  // Red
        }
      }
    }
  }
}
```

---

### Step 5.4: Create Time-Based Trigger

1. **Click:** Triggers (⏰ icon, left sidebar)
2. **Click:** + Add Trigger (bottom right)
3. **Function:** syncEpicStatusFromJira
4. **Event source:** Time-driven
5. **Type:** Minutes timer
6. **Interval:** Every 15 minutes
7. **Click:** Save

---

## Part 6: Testing (60-90 minutes)

### Test 1: Epic Creation

1. **Submit intake form** (or create Epic manually)
2. **Verify:** Epic status = INTAKE
3. **Verify:** Welcome comment added
4. **Verify:** Epic assigned to TPM

**✅ Pass Criteria:** Epic created with INTAKE status

---

### Test 2: Manual Transitions

1. **Transition:** INTAKE → UNDER_REVIEW
2. **Verify:** Status changed, comment added
3. **Set:** Business Value Score = 8, Technical Complexity = 3
4. **Transition:** UNDER_REVIEW → BACKLOG
5. **Verify:** Email sent to stakeholder
6. **Verify:** Label "approved" added

**✅ Pass Criteria:** All manual transitions work

---

### Test 3: Capacity Validation

1. **Set:** Committed Quarter = Q3 2026
2. **Set:** Team Capacity Allocation = 25%
3. **Try:** Transition BACKLOG → IN_ROADMAP
4. **Verify:** Transition allowed (or blocked if >100%)
5. **Check:** Railway middleware logs for capacity check

**✅ Pass Criteria:** Capacity validation runs (allow/warn/block)

---

### Test 4: Auto-Transition to IN_EXECUTION

1. **Create child Story** under Epic
2. **Set:** Story status = READY_FOR_DEV
3. **Transition:** Story → IN_PROGRESS
4. **Wait:** 5-10 seconds
5. **Verify:** Parent Epic auto-transitioned to IN_EXECUTION
6. **Verify:** Email sent to stakeholder

**✅ Pass Criteria:** Epic auto-transitions when Story starts

---

### Test 5: Auto-Complete Epic

1. **Create Epic** with 2 child Stories in IN_EXECUTION
2. **Mark both Stories:** DONE
3. **Wait:** Until next day 9 AM (or manually run automation)
4. **Verify:** Epic auto-transitioned to COMPLETED
5. **Verify:** Completion Date set
6. **Verify:** Email sent to stakeholder

**✅ Pass Criteria:** Epic auto-completes when all Stories done

---

### Test 6: Roadmap Board

1. **Open:** PMO Roadmap - Epics board
2. **Verify:** Epics appear in correct columns
3. **Verify:** Swimlanes group by Request Type
4. **Verify:** Card shows: Priority, Quarter, Capacity %
5. **Test:** Quick filters (At Risk, P0 Only)

**✅ Pass Criteria:** Board displays correctly

---

### Test 7: Email Notifications

1. **Use real email address** in test Epic
2. **Transition through all statuses**
3. **Check inbox:** Verify emails received at each transition
4. **Verify:** Email content matches templates
5. **Verify:** Links work (click Epic URL in email)

**✅ Pass Criteria:** Emails sent at key milestones

---

## Part 7: Go Live (30 minutes)

### Step 7.1: Update Existing Epics

**If you have existing Epics from Phase 1:**

1. **Bulk edit** Epics to set Business Value + Complexity scores
2. **Set** Committed Quarter for any already scheduled
3. **Transition** from INTAKE to appropriate status

**JQL for bulk edit:**
```
project = PGMAUTO AND issuetype = Epic AND status = INTAKE
```

---

### Step 7.2: Train Team

**Training Topics:**
- How to transition Epics through workflow
- How to set Business Value + Complexity scores
- How to use Roadmap board for planning
- How capacity validation works
- What stakeholder notifications are sent

**Training Materials:**
- `docs/epic-workflow-design.md`
- `docs/capacity-planning.md`
- Live demo of Roadmap board

---

### Step 7.3: Announce to Stakeholders

**Email template:**
```
Subject: New PMO Roadmap Available

Hello,

We've launched Phase 2 of our PMO automation system!

What's new:
✅ Roadmap visibility (see what's planned for each quarter)
✅ Automatic status updates (you'll get emails when your request progresses)
✅ Capacity planning (ensures we don't over-commit)

View the roadmap: [JIRA Board URL]

Questions? Contact your TPM.

Best regards,
IT Leadership
```

---

## Troubleshooting

### Problem: "Transition blocked - Required field missing"

**Cause:** Custom field not marked as required for that status

**Solution:**
- Go to Field Configuration
- Set field as required for Epic issue type
- Associate with correct screen

---

### Problem: "Auto-transition not working (IN_ROADMAP → IN_EXECUTION)"

**Cause:** Automation rule disabled OR condition not met

**Solution:**
- Check: Project Settings → Automation → Find rule
- Verify: Rule is enabled (toggle on)
- Test: Create Story, transition to IN_PROGRESS
- Check: Automation execution log for errors

---

### Problem: "Capacity validation not running"

**Cause:** Railway middleware not called OR webhook not configured

**Solution:**
- Check: Railway middleware is running
- Check: JIRA webhook configured (Settings → System → Webhooks)
- Test: POST to middleware endpoint manually
- Check: Middleware logs for errors

---

### Problem: "Emails not sending"

**Cause:** JIRA notification settings OR wrong email field

**Solution:**
- Check: JIRA notification scheme (Project Settings → Notifications)
- Verify: Email field populated in Epic
- Test: Send test email from automation rule
- Check: Spam folder

---

### Problem: "Board not showing Epics"

**Cause:** Filter JQL wrong OR Epic status not in filter

**Solution:**
- Check: Board settings → Filter query
- Verify: JQL includes all Epic statuses
- Test: Run JQL in Issue Navigator first
- Refresh board

---

## Success Criteria

**Phase 2 is complete when:**
- ✅ All 7 Epic statuses work (can transition manually)
- ✅ All 11 custom fields exist and are on Epic screens
- ✅ All 8 automation rules are enabled and tested
- ✅ Roadmap board displays Epics by quarter
- ✅ Capacity validation blocks over-committed quarters
- ✅ Auto-transitions work (IN_EXECUTION, COMPLETED)
- ✅ Stakeholder emails send at key transitions
- ✅ TPM team trained on new workflow

---

## Next Steps

After Phase 2 is live:
1. **Monitor:** Watch automation execution logs for errors
2. **Gather Feedback:** Ask TPMs what's working/not working
3. **Iterate:** Adjust automation rules based on feedback
4. **Plan Phase 3:** Story-level BRD workflow (next quarter)

---

## Support

**Need Help?**
- **Documentation:** `docs/epic-workflow-design.md`, `docs/capacity-planning.md`
- **Configuration:** `config/jira-epic-workflow.yaml`, `config/jira-epic-automation-rules.yaml`
- **GitHub Issues:** https://github.com/PlainJane20/pm-automation-system/issues
- **Email:** nks.ai.dev@gmail.com

**Good luck with Phase 2! 🚀**
