kkdrih
# Quick Start Guide
## Get Your PM Automation System Running in 30 Minutes

This guide will get you from zero to a fully operational program management automation system.

---

## ⏱️ Timeline

- **Minutes 0-10**: JIRA setup
- **Minutes 10-20**: Deploy automation middleware
- **Minutes 20-25**: Connect JIRA webhooks
- **Minutes 25-30**: Test and verify

---

## 📋 Prerequisites Checklist

Before you start, make sure you have:

- [ ] Email address for JIRA account
- [ ] GitHub account (free)
- [ ] Railway.app account (free) - [Sign up here](https://railway.app)
- [ ] Text editor (VS Code, Sublime, etc.)
- [ ] 30 minutes of uninterrupted time

**Optional (for AI features):**
- [ ] OpenAI API key - [Get here](https://platform.openai.com/api-keys)

---

## Step 1: Set Up JIRA (10 minutes)

### 1.1 Create Free JIRA Account

1. Go to: https://www.atlassian.com/software/jira/free
2. Click "Get it free"
3. Sign up with your email
4. Create your site: `yourcompany.atlassian.net`
5. Choose "Jira Software"

### 1.2 Create Your First Project

1. Click "Create project"
2. Select "Kanban" template
3. Project details:
   - **Name**: `Pilot Program` (or your actual program name)
   - **Key**: `PILOT`
   - **Access**: Team-managed
4. Click "Create"

### 1.3 Add Custom Fields

Go to: **Settings (⚙️) → Issues → Custom fields**

Create these fields (click "Create custom field" for each):

#### Field 1: Request Type
- Type: **Select List (single choice)**
- Name: `Request Type`
- Options:
  - Bug
  - Feature
  - Enhancement
  - Support Request
- Default: Feature
- Click "Create"

#### Field 2: BRD Document Link
- Type: **URL**
- Name: `BRD Document Link`
- Description: "Link to approved Business Requirements Document"
- Click "Create"

#### Field 3: BRD Owner
- Type: **User Picker (single user)**
- Name: `BRD Owner`
- Description: "Person responsible for creating BRD"
- Click "Create"

#### Field 4: BRD Approved Date
- Type: **Date Picker**
- Name: `BRD Approved Date`
- Description: "Date when BRD was approved"
- Click "Create"

**Important:** After creating each field, click "Associate to screens" and add to:
- Default Screen
- PILOT: Kanban Default Issue Screen

### 1.4 Create Workflow States

Go to: **Project Settings → Board → Columns**

Add these columns (in order):

1. SUBMITTED (To Do)
2. AWAITING_SCOPING (To Do)
3. SCOPING_IN_PROGRESS (In Progress)
4. READY_FOR_DEV (To Do)
5. IN_PROGRESS (In Progress)
6. QA_TESTING (In Progress)
7. DONE (Done)

### 1.5 Get JIRA API Token

1. Go to: https://id.atlassian.com/manage/api-tokens
2. Click "Create API token"
3. Label: `PM Automation System`
4. Click "Create"
5. **Copy the token** and save it securely (you won't see it again)

✅ **JIRA setup complete!**

---

## Step 2: Deploy Automation Middleware (10 minutes)

### 2.1 Get the Code

**Option A: Fork this repository (recommended)**
1. Go to the GitHub repo
2. Click "Fork"
3. Clone your fork:
   ```bash
   git clone https://github.com/YOUR-USERNAME/pm-automation-system.git
   cd pm-automation-system
   ```

**Option B: Download ZIP**
1. Download the ZIP file
2. Extract to a folder
3. Open terminal in that folder

### 2.2 Configure Environment Variables

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your details:
   ```bash
   # Replace these with your actual values
   JIRA_URL=https://yourcompany.atlassian.net
   JIRA_EMAIL=your-email@company.com
   JIRA_API_TOKEN=paste_your_token_here
   JIRA_PROJECT_KEY=PILOT
   ```

   **Don't have a text editor?** Use this command:
   ```bash
   nano .env
   # Edit the file, then press Ctrl+X, Y, Enter to save
   ```

### 2.3 Deploy to Railway (Free Hosting)

1. Go to: https://railway.app
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Select your forked/cloned repo
6. Railway auto-detects the Dockerfile ✅

7. **Add environment variables**:
   - Click "Variables" tab
   - Click "RAW Editor"
   - Paste your entire `.env` file content
   - Click "Add"

8. Click "Deploy"
9. Wait ~2 minutes for deployment
10. Once deployed, click "Settings" → "Generate Domain"
11. **Copy your URL**: `https://pm-automation-production.up.railway.app`

### 2.4 Verify Deployment

Open in browser: `https://your-railway-url/health`

You should see:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-06-11T..."
}
```

✅ **Middleware deployed!**

---

## Step 3: Connect JIRA to Middleware (5 minutes)

### 3.1 Create Webhooks in JIRA

Go to: **JIRA Settings (⚙️) → System → WebHooks**

#### Webhook 1: Issue Created

1. Click "Create a WebHook"
2. Fill in:
   - **Name**: `PM Automation - Issue Created`
   - **Status**: Enabled
   - **URL**: `https://your-railway-url/webhooks/jira/issue-created`
   - **Events**: ✅ Issue → created
3. Click "Create"

#### Webhook 2: Issue Transitioned

1. Click "Create a WebHook" again
2. Fill in:
   - **Name**: `PM Automation - Issue Transitioned`
   - **Status**: Enabled
   - **URL**: `https://your-railway-url/webhooks/jira/issue-transitioned`
   - **Events**: ✅ Issue → updated
3. Click "Create"

✅ **Webhooks configured!**

### 3.2 Add JIRA Automation Rule (BRD Gate)

Go to: **Project Settings → Automation**

#### Create Rule: Block Development Without BRD

1. Click "Create rule"
2. **Trigger**: 
   - Select "Issue transitioned"
   - Transition: to status "IN_PROGRESS"
3. **Condition**:
   - Click "Add condition" → "Issue fields condition"
   - Field: "BRD Approved Date"
   - Condition: "is empty"
4. **Action**:
   - Click "Add action" → "Block issue transition"
   - Error message:
     ```
     ⛔ Development cannot start without approved BRD.
     
     Required fields:
     • BRD Document Link
     • BRD Approved Date
     
     Please complete scoping first.
     ```
5. **Name the rule**: `BRD Gate Enforcement`
6. Click "Turn it on"

✅ **Critical automation rule added!**

---

## Step 4: Test Your Setup (5 minutes)

### 4.1 Test Auto-Classification

1. In JIRA, click "Create"
2. Fill in:
   - **Summary**: "Login page is broken"
   - **Description**: "Error 500 when clicking login button"
   - **Request Type**: Leave empty
3. Click "Create"

**Expected result:**
- Within 5 seconds, "Request Type" should auto-fill with "Bug"
- Label "auto-classified" should be added
- Check Railway logs: `railway logs` (should see webhook received)

### 4.2 Test BRD Gate

1. Create another ticket:
   - **Summary**: "Add dark mode feature"
   - **Request Type**: Feature
2. Try to drag it to "IN_PROGRESS" column

**Expected result:**
- Transition should be **blocked**
- Error message appears: "Development cannot start without approved BRD"
- ✅ **BRD gate is working!**

### 4.3 Test Duplicate Detection

1. Create two similar tickets:
   - Ticket 1: "Add user profile page"
   - Ticket 2: "Create user profile screen"

**Expected result:**
- Ticket 2 should have a comment: "⚠️ Potential Duplicate Detected"
- Link to Ticket 1
- Label "potential-duplicate" added

---

## 🎉 Success! Your System is Operational

### What You Just Built

✅ **JIRA configured** with custom fields and workflows  
✅ **Automation middleware deployed** on Railway (free tier)  
✅ **Webhooks connected** for real-time automation  
✅ **BRD gate enforced** - prevents dev without requirements  
✅ **Auto-classification working** - AI categorizes tickets  
✅ **Duplicate detection active** - flags similar requests  

---

## 🔗 Next Steps

### Immediate (Do Today)

1. **Add your team to JIRA** (up to 10 users free)
   - Go to: Settings → User management
   - Invite team members

2. **Create a real ticket** for your actual program
   - Follow the workflow: SUBMITTED → AWAITING_SCOPING → etc.
   - Fill in BRD fields to test the full flow

3. **Check your dashboard**
   - Visit: `https://your-railway-url/api/program-health?project=PILOT`
   - Bookmark this URL for daily checks

### This Week

1. **Add more automation rules** from `config/jira-automation-rules.yaml`:
   - Stale ticket warning (50 days)
   - Stale ticket auto-close (60 days)
   - Epic linkage enforcement

2. **Set up Slack notifications** (optional):
   - Get Slack Bot Token
   - Add to `.env`: `SLACK_BOT_TOKEN=xoxb-...`
   - Redeploy on Railway

3. **Create Google Sheets dashboard** (see `docs/google-sheets-dashboard.md`)

### This Month

1. **Enable AI features** (optional - requires OpenAI API):
   - Get API key: https://platform.openai.com/api-keys
   - Add to `.env`: `OPENAI_API_KEY=sk-...`
   - Set `ENABLE_AI_CLASSIFICATION=true`
   - Redeploy

2. **Run pilot program**:
   - Use for one real project
   - Gather feedback from team
   - Iterate on workflows

3. **Measure ROI**:
   - Track time saved on status reports
   - Count duplicates prevented
   - Monitor BRD compliance rate

---

## 🆘 Troubleshooting

### Webhooks not working?

**Check Railway logs:**
```bash
railway logs --tail
```

**Test webhook manually:**
```bash
curl -X POST https://your-railway-url/webhooks/jira/issue-created \
  -H "Content-Type: application/json" \
  -d '{"issue": {"key": "TEST-1"}}'
```

**Expected response:** `{"status": "processed"}`

### BRD gate not blocking?

1. Check automation rule is **enabled** (green toggle in JIRA Automation)
2. Verify custom field "BRD Approved Date" exists
3. Test with a new ticket (sometimes cached state causes issues)

### Railway deployment failed?

1. Check build logs in Railway dashboard
2. Verify `.env` variables are set correctly
3. Make sure Dockerfile is in root directory

---

## 💡 Pro Tips

1. **Bookmark these URLs:**
   - JIRA: `https://yourcompany.atlassian.net`
   - Railway Dashboard: `https://railway.app/project/your-project`
   - API Health: `https://your-railway-url/health`
   - Program Health: `https://your-railway-url/api/program-health?project=PILOT`

2. **Set up monitoring:**
   - Railway sends email alerts if service goes down
   - Add `https://your-railway-url/health` to UptimeRobot (free)

3. **Keep costs at $0:**
   - Railway free tier: 500 hours/month (enough for 1 service running 24/7)
   - JIRA free: up to 10 users
   - Only cost: OpenAI API if enabled (~$5/month)

---

## 📞 Need Help?

- **Documentation**: See `docs/` folder for detailed guides
- **Issues**: Check Railway logs and JIRA automation history
- **Questions**: Open a GitHub issue

---

**Congratulations! You now have an enterprise-grade PM automation system running for free.**

Next: Read the [User Guide](USER_GUIDE.md) to learn how to use all features.
