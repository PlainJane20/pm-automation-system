# ✅ Phase 1 Complete: Epic Intake Automation

**Status:** Production-ready  
**Last Updated:** June 17, 2026  
**System Type:** PMO Intake & Epic Auto-Creation

---

## 🎯 What We Built

A complete **stakeholder-to-JIRA Epic automation** that:
1. ✅ Collects intake requests via Google Form
2. ✅ Routes to IT Leadership for review in Google Sheet
3. ✅ Auto-creates JIRA Epics when approved
4. ✅ Auto-syncs Epic fields when Google Sheet is edited (one-way sync)
5. ✅ Enforces BRD gate on Story transitions

---

## 📋 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     STAKEHOLDER INTAKE                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Google Form     │ ← Stakeholder submits request
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Google Sheet    │ ← IT Leadership reviews
                    │  + Apps Script   │
                    └──────────────────┘
                              │
                              ▼ (IT Recommendation = "Approve")
                    ┌──────────────────┐
                    │  JIRA API v3     │ ← Auto-create Epic
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  JIRA Epic       │ ← PGMAUTO-X created
                    │  (customfield_   │
                    │   10041 = Req    │
                    │   Type)          │
                    └──────────────────┘
```

---

## 🔧 Components

### 1. Google Form
- **URL:** https://forms.gle/w3nfUnipveyAhxss5
- **Purpose:** Stakeholder intake for projects, enhancements, feature requests
- **Questions:**
  - Project Name
  - Request Type (Project/Enhancement/Feature/Bug Fix)
  - Department
  - Problem Statement
  - Business Impact
  - Expected Deliverables
  - Target Completion Date
  - Priority (P0-P3)
  - Budget Status
  - Email Address

### 2. Google Sheet
- **URL:** https://docs.google.com/spreadsheets/d/158zDAbms5TR7rIJeTfG6o9FpMDlz3AY2HpYqcizLVtQ/edit
- **Columns:**
  - A-K: Form responses
  - L: IT Recommendation (Approve/Hold/Reject)
  - M: Estimated Effort (Small/Medium/Large)
  - N: Target Quarter (Q1/Q2/Q3/Q4)
  - O: Decision Date (auto-filled)
  - P: JIRA Epic Link (auto-filled)
  - Q: IT Notes (syncs as JIRA comment)

### 3. Google Apps Script
- **File:** `google-apps-script-COMPLETE-WITH-REQUEST-TYPE.txt`
- **Triggers:** Installable `onEditInstallable` (On edit)
- **OAuth Scopes:**
  - `https://www.googleapis.com/auth/spreadsheets.currentonly`
  - `https://www.googleapis.com/auth/script.external_request`
- **Functions:**
  - `createJiraEpicFromRow()` - Creates Epic when approved
  - `updateJiraEpicPriority()` - Syncs Priority changes
  - `updateJiraEpicDueDate()` - Syncs Due Date changes
  - `updateJiraRequestType()` - Syncs Request Type field
  - `updateJiraEpicLabels()` - Syncs Effort + Quarter labels
  - `updateJiraEpicDescription()` - Syncs description when Problem/Impact/Deliverables change
  - `addJiraEpicComment()` - Adds IT Notes as comment

### 4. JIRA Configuration
- **Project:** PGMAUTO
- **URL:** https://nksaidev.atlassian.net
- **Issue Types:** Epic, Story
- **Custom Fields:**
  - `customfield_10041` - Request Type (dropdown)
  - BRD-related fields (for Story transitions)
- **Labels:**
  - `Effort-Small`, `Effort-Medium`, `Effort-Large`
  - `Quarter-Q1-'YR`, `Quarter-Q2-'YR`, `Quarter-Q3-'YR`, `Quarter-Q4-'YR`

### 5. Railway Middleware (BRD Gate)
- **URL:** https://pm-automation-system-production.up.railway.app
- **Purpose:** Validates BRD fields before Story transitions
- **Deployment:** Already live and tested

---

## 🔄 Workflow

### Epic Creation Flow
1. **Stakeholder submits** Google Form
2. **Response appears** in Google Sheet
3. **IT Leadership reviews:**
   - Fills Estimated Effort (Column M)
   - Fills Target Quarter (Column N)
   - Adds IT Notes if needed (Column Q)
4. **IT Leadership approves:** Sets Column L = "Approve"
5. **Apps Script triggers:**
   - Creates Epic in JIRA
   - Sets Priority (mapped from P0-P3 → Highest/High/Medium/Low)
   - Sets Due Date (from Target Completion Date)
   - Sets Request Type custom field (customfield_10041)
   - Sets Labels (Effort-X, Quarter-X)
   - Writes Epic URL back to Column P
   - Writes Decision Date to Column O

### Auto-Update Flow (One-Way: Sheet → JIRA)
When IT Leadership edits the Google Sheet:
- **Column I (Priority)** → Updates Epic Priority in JIRA
- **Column H (Target Date)** → Updates Epic Due Date in JIRA
- **Column C (Request Type)** → Updates Epic Request Type field in JIRA
- **Column M (Effort)** → Updates Epic Labels in JIRA
- **Column N (Quarter)** → Updates Epic Labels in JIRA
- **Column E/F/G (Problem/Impact/Deliverables)** → Updates Epic Description in JIRA
- **Column Q (IT Notes)** → Adds comment to Epic in JIRA

---

## 📊 Data Mapping

### Priority Mapping
| Google Sheet                                              | JIRA Priority |
|----------------------------------------------------------|---------------|
| P0 - Critical (Business-stopping issue...)               | Highest       |
| P1 - High (Significant impact...)                        | High          |
| P2 - Medium (Important but can wait...)                  | Medium        |
| P3 - Low (Nice to have...)                               | Low           |

### Request Type Options
- Project Request (large initiative, multiple features)
- Enhancement Request (improve existing feature)
- Feature Request (new capability)
- Bug Fix Request (production issue)

### Effort Options
- Small (< 2 weeks)
- Medium (2-6 weeks)
- Large (> 6 weeks)

### Quarter Options
- Q1 'YR
- Q2 'YR
- Q3 'YR
- Q4 'YR

---

## 🔐 Security Configuration

### Credentials
- **JIRA Email:** `nks.ai.dev@gmail.com`
- **JIRA API Token:** Stored in Google Apps Script CONFIG (rotatable)
- **JIRA Project:** `PGMAUTO`

### Access Control
- **Google Form:** Public (stakeholder-facing)
- **Google Sheet:** Restricted to IT Leadership
- **Apps Script:** Runs as authenticated user
- **JIRA:** API authentication via email + token

---

## ✅ Testing Checklist

- [x] Submit intake form → Row appears in Google Sheet
- [x] Set IT Recommendation = "Approve" → Epic created in JIRA
- [x] Epic has correct Priority (mapped from P0-P3)
- [x] Epic has correct Due Date (from Target Completion Date)
- [x] Epic has Request Type custom field populated (customfield_10041)
- [x] Epic has Labels (Effort-X, Quarter-X) - NO Type- label
- [x] Epic URL written back to Google Sheet Column P
- [x] Decision Date written to Column O
- [x] Change Priority in Sheet → Epic Priority updates in JIRA
- [x] Change Target Date in Sheet → Epic Due Date updates in JIRA
- [x] Change Request Type in Sheet → Epic Request Type field updates in JIRA
- [x] Change Effort/Quarter in Sheet → Epic Labels update in JIRA
- [x] Change Problem/Impact/Deliverables → Epic Description updates in JIRA
- [x] Add IT Notes → Comment added to Epic in JIRA

---

## 📈 Current Production Data

- **Google Form:** https://forms.gle/w3nfUnipveyAhxss5
- **Google Sheet:** https://docs.google.com/spreadsheets/d/158zDAbms5TR7rIJeTfG6o9FpMDlz3AY2HpYqcizLVtQ/edit
- **JIRA Project:** https://nksaidev.atlassian.net/jira/software/projects/PGMAUTO
- **Epics Created:** PGMAUTO-1, PGMAUTO-2, PGMAUTO-3, PGMAUTO-4

---

## 🚀 Deployment Instructions

See: `SETUP_INSTRUCTIONS.md` for step-by-step deployment guide.

---

## 🔜 Future Phases (Not Built Yet)

### Phase 2: Epic Workflow Management
- Epic statuses: INTAKE → UNDER_REVIEW → BACKLOG → IN_ROADMAP → IN_EXECUTION → COMPLETED
- Roadmap view (Now/Next/Later by quarter)
- Backlog management

### Phase 3: Story-Level BRD Workflow
- Break Epics into Stories
- Story-level BRD process
- READY_FOR_DEV status gate

### Phase 4: Sprint Execution
- Sprint Planning automation
- Scrum board configuration
- Velocity tracking & burndown

---

## 📞 Support

For issues or questions:
- GitHub Issues: https://github.com/[your-repo]/pm-automation-system/issues
- Email: nks.ai.dev@gmail.com
