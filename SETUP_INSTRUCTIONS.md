# 🚀 Setup Instructions - Epic Intake Automation

**Time Required:** 30 minutes  
**Skill Level:** Intermediate (JIRA Admin, Google Apps Script basic knowledge)

---

## Prerequisites

- [ ] JIRA Cloud instance with admin access
- [ ] Google account with Google Forms/Sheets access
- [ ] JIRA API token (generate at https://id.atlassian.com/manage/api-tokens)

---

## Step 1: Set Up JIRA Project

### 1.1 Create JIRA Project
1. Go to JIRA → Projects → Create project
2. Select **Team-managed** or **Company-managed** (Scrum template)
3. **Project Key:** `PGMAUTO` (or your preferred key)
4. **Project Name:** "PMO Automation" (or your preferred name)

### 1.2 Create Request Type Custom Field
1. Go to JIRA → Settings (⚙️) → Issues → Custom fields
2. Click **Create custom field**
3. **Field Type:** Select (single choice)
4. **Field Name:** `Request Type`
5. **Options (one per line):**
   ```
   Project Request (large initiative, multiple features)
   Enhancement Request (improve existing feature)
   Feature Request (new capability)
   Bug Fix Request (production issue)
   ```
6. Click **Create**
7. **Associate with screens:** Epic, Story screens
8. **Note the field ID:** Go to Settings → Issues → Custom fields → Click "..." next to "Request Type" → View field details
   - You'll see: `customfield_10041` (your ID may differ - update script if needed)

### 1.3 Verify Issue Types
Ensure your project has:
- **Epic** issue type
- **Story** issue type

---

## Step 2: Set Up Google Form

### 2.1 Create Form
1. Go to https://forms.google.com
2. Click **+ Blank form**
3. **Title:** "IT Project Intake Request"
4. Add the following questions:

#### Question 1: Project Name
- Type: Short answer
- Required: Yes

#### Question 2: Request Type
- Type: Multiple choice
- Options:
  ```
  Project Request (large initiative, multiple features)
  Enhancement Request (improve existing feature)
  Feature Request (new capability)
  Bug Fix Request (production issue)
  ```
- Required: Yes

#### Question 3: Department
- Type: Short answer
- Required: Yes

#### Question 4: What problem are you trying to solve?
- Type: Paragraph
- Required: Yes

#### Question 5: What is the business impact if we don't solve this?
- Type: Paragraph
- Required: Yes

#### Question 6: What will be delivered when this project is complete?
- Type: Paragraph
- Required: Yes

#### Question 7: Target Completion Date
- Type: Date
- Required: Yes

#### Question 8: Priority Level
- Type: Multiple choice
- Options:
  ```
  P0 - Critical (Business-stopping issue, immediate action required)
  P1 - High (Significant impact, needed within this quarter)
  P2 - Medium (Important but can wait 1-2 quarters)
  P3 - Low (Nice to have, no specific deadline)
  ```
- Required: Yes

#### Question 9: Budget Status
- Type: Multiple choice
- Options:
  ```
  Budget approved
  Budget pending approval
  No budget required
  Budget needs to be created
  ```
- Required: Yes

#### Question 10: Email Address
- Type: Short answer
- Validation: Email
- Required: Yes

### 2.2 Link to Google Sheet
1. Click **Responses** tab
2. Click the Google Sheets icon (green)
3. Select **Create a new spreadsheet**
4. Name: "IT Project Intake - 2026"
5. Click **Create**

---

## Step 3: Configure Google Sheet

### 3.1 Add IT Assessment Columns
The form responses populate columns A-K. Add these columns after column K:

| Column | Header Name                  | Purpose                              |
|--------|------------------------------|--------------------------------------|
| L      | IT Recommendation            | Approve / Hold / Reject              |
| M      | Estimated Effort             | Small / Medium / Large               |
| N      | Target Quarter               | Q1 'YR / Q2 'YR / Q3 'YR / Q4 'YR   |
| O      | Decision Date                | Auto-filled by script                |
| P      | JIRA Epic Link               | Auto-filled by script                |
| Q      | IT Notes                     | IT team comments (syncs to JIRA)     |

### 3.2 Add Data Validation (Optional but Recommended)

**Column L: IT Recommendation**
1. Select cell L2
2. Data → Data validation
3. Criteria: List of items
4. Items: `Approve,Hold,Reject`
5. Apply to entire column

**Column M: Estimated Effort**
1. Select cell M2
2. Data → Data validation
3. Criteria: List of items
4. Items: `Small (< 2 weeks),Medium (2-6 weeks),Large (> 6 weeks)`
5. Apply to entire column

**Column N: Target Quarter**
1. Select cell N2
2. Data → Data validation
3. Criteria: List of items
4. Items: `Q1 'YR,Q2 'YR,Q3 'YR,Q4 'YR`
5. Apply to entire column

---

## Step 4: Install Google Apps Script

### 4.1 Open Apps Script Editor
1. In your Google Sheet, click **Extensions → Apps Script**
2. Delete any default code in `Code.gs`

### 4.2 Copy Script
1. Open the file: `google-apps-script-COMPLETE-WITH-REQUEST-TYPE.txt` from this repo
2. Copy the **entire contents**
3. Paste into `Code.gs`

### 4.3 Update Configuration
Find the `CONFIG` section (lines 19-48) and update:

```javascript
const CONFIG = {
  JIRA_URL: 'https://YOUR-DOMAIN.atlassian.net',  // ← Change this
  JIRA_EMAIL: 'your-email@domain.com',             // ← Change this
  JIRA_API_TOKEN: 'YOUR_API_TOKEN_HERE',           // ← Change this
  JIRA_PROJECT_KEY: 'PGMAUTO',                     // ← Change if different
  
  // Column mapping - UPDATE if your columns are different
  COLUMNS: {
    TIMESTAMP: 0,           // Column A
    PROJECT_NAME: 1,        // Column B
    REQUEST_TYPE: 2,        // Column C
    DEPARTMENT: 3,          // Column D
    PROBLEM: 4,             // Column E
    IMPACT: 5,              // Column F
    DELIVERABLES: 6,        // Column G
    TARGET_DATE: 7,         // Column H
    PRIORITY: 8,            // Column I
    BUDGET: 9,              // Column J
    EMAIL: 10,              // Column K
    IT_RECOMMENDATION: 11,  // Column L ← IT adds "Approve" here
    ESTIMATED_EFFORT: 12,   // Column M
    TARGET_QUARTER: 13,     // Column N
    DECISION_DATE: 14,      // Column O ← Auto-filled
    JIRA_EPIC_LINK: 15,     // Column P ← Auto-filled
    IT_NOTES: 16            // Column Q
  }
};
```

**⚠️ IMPORTANT:** If your Request Type field has a different custom field ID than `customfield_10041`, update line 195:
```javascript
customfield_10041: requestType ? { value: requestType.replace(/\s*\(.*?\)\s*/g, '').trim() } : null
```
Change `customfield_10041` to your actual field ID.

### 4.4 Save the Script
1. Click the **disk icon** or press `Cmd+S` (Mac) / `Ctrl+S` (Windows)
2. Name your project: "JIRA Epic Automation"

---

## Step 5: Configure OAuth Scopes

### 5.1 Create appsscript.json
1. In Apps Script editor, click **Project Settings** (⚙️ icon on left)
2. Check **"Show 'appsscript.json' manifest file in editor"**
3. Go back to **Editor** tab
4. Click on `appsscript.json` file
5. Replace contents with:

```json
{
  "timeZone": "America/Los_Angeles",
  "oauthScopes": [
    "https://www.googleapis.com/auth/spreadsheets.currentonly",
    "https://www.googleapis.com/auth/script.external_request"
  ]
}
```

6. **Save**

---

## Step 6: Test JIRA Connection

### 6.1 Run Setup Function
1. In Apps Script editor, select function: **setup** (from dropdown)
2. Click **Run** (▶️ button)
3. **First time:** You'll be prompted to authorize:
   - Click **Review Permissions**
   - Select your Google account
   - Click **Advanced**
   - Click **Go to [Project Name] (unsafe)**
   - Click **Allow**
4. Wait for success message: "Setup successful! JIRA connection verified."

**If you see an error:** Check your JIRA URL, email, and API token in the CONFIG section.

---

## Step 7: Create Installable Trigger

### 7.1 Why We Need This
Simple triggers (like `onEdit()`) **cannot** make external API calls. We need an **installable trigger**.

### 7.2 Create Trigger
1. In Apps Script editor, click **Triggers** (⏰ icon on left)
2. Click **+ Add Trigger** (bottom right)
3. Configure:
   - **Function:** `onEditInstallable`
   - **Deployment:** Head
   - **Event source:** From spreadsheet
   - **Event type:** On edit
4. Click **Save**
5. **Authorize** if prompted (same process as Step 6.1)

---

## Step 8: Test Epic Creation

### 8.1 Test Method 1: Use Form
1. Open your Google Form
2. Fill out a test request
3. Submit
4. Go to Google Sheet → verify row appears
5. Fill Column M (Estimated Effort): `Medium (2-6 weeks)`
6. Fill Column N (Target Quarter): `Q3 'YR`
7. Set Column L (IT Recommendation): `Approve`
8. **Wait 2-3 seconds**
9. You should see a popup: "Success! Epic created: ..."
10. Column P should now have a JIRA URL
11. Column O should have today's date

### 8.2 Test Method 2: Manually Add Row
1. Add a row directly in Google Sheet with sample data
2. Fill Column M and N
3. Set Column L = `Approve`
4. Verify Epic creation

### 8.3 Verify in JIRA
1. Open the JIRA Epic URL from Column P
2. Check:
   - ✅ Summary = Project Name
   - ✅ Priority = Mapped from P0-P3
   - ✅ Due Date = Target Completion Date
   - ✅ Request Type field = From form (e.g., "Feature Request (new capability)")
   - ✅ Labels = Only `Effort-Medium` and `Quarter-Q3-'YR` (NO Type- label)
   - ✅ Description = Formatted intake details

---

## Step 9: Test Auto-Updates

### 9.1 Test Priority Update
1. In Google Sheet, change Column I (Priority) for an existing Epic row
2. Change from P2 to P1
3. Wait 2-3 seconds
4. You should see a toast notification: "Updated priority to High"
5. Verify in JIRA: Epic priority changed to "High"

### 9.2 Test Due Date Update
1. Change Column H (Target Date)
2. Verify in JIRA: Epic due date updated

### 9.3 Test Request Type Update
1. Change Column C (Request Type)
2. Verify in JIRA: Request Type field updated

### 9.4 Test Labels Update
1. Change Column M (Estimated Effort) or Column N (Target Quarter)
2. Verify in JIRA: Labels updated

### 9.5 Test IT Notes Comment
1. Add text to Column Q (IT Notes)
2. Verify in JIRA: Comment added to Epic

---

## Step 10: Share Form with Stakeholders

### 10.1 Get Form Link
1. Open Google Form
2. Click **Send** button (top right)
3. Click **Link** icon (🔗)
4. Click **Shorten URL**
5. Click **Copy**

### 10.2 Distribute
Send the form link to stakeholders via:
- Email announcement
- Slack channel
- Internal wiki/intranet
- Confluence page

---

## Troubleshooting

### Error: "Operation value must be an Atlassian Document Format"
- **Cause:** JIRA API v3 requires ADF format for descriptions
- **Fix:** Ensure you're using the latest script version with `formatEpicDescription()` function

### Error: "Specified permissions are not sufficient to call UrlFetchApp.fetch"
- **Cause:** Missing OAuth scope
- **Fix:** Ensure `appsscript.json` has `https://www.googleapis.com/auth/script.external_request`

### Error: "JIRA API Error (401)"
- **Cause:** Invalid JIRA credentials
- **Fix:** Check JIRA_EMAIL and JIRA_API_TOKEN in CONFIG section

### Error: "JIRA API Error (400): Field 'customfield_10041' cannot be set"
- **Cause:** Custom field ID is different in your JIRA instance
- **Fix:** Get your Request Type field ID and update line 195 in the script

### Epic Not Creating
1. Check Apps Script Executions: View → Executions (look for errors)
2. Check Trigger: Triggers tab → verify `onEditInstallable` is set to "On edit"
3. Check Column L value: Must be exactly `Approve` (case-sensitive)

### Auto-Updates Not Working
1. Verify Column P has a JIRA Epic URL
2. Check Apps Script Executions for errors
3. Ensure you're editing the correct column (not just any cell)

---

## Security Best Practices

1. **Restrict Google Sheet access:** Only IT Leadership should have edit access
2. **Keep API token secure:** Never commit to version control
3. **Rotate API tokens:** Every 90 days (generate new token in JIRA)
4. **Monitor Apps Script executions:** Check for unusual activity
5. **Use service account (optional):** For production, consider a dedicated JIRA service account

---

## Support

For issues or questions:
- GitHub Issues: [your-repo]/pm-automation-system/issues
- Email: nks.ai.dev@gmail.com
