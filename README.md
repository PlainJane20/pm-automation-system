# PM Automation System

**End-to-end program management automation with strict governance guardrails**

Built by: Navi Sohi, Staff TPM  
Purpose: Eliminate manual overhead, ensure process compliance, maintain data hygiene

---

## 🎯 What This System Does

This is a **complete automation platform** that transforms chaotic program management into a structured, governed, data-driven process:

✅ **BRD Gate Enforcement** - Prevents development from starting without approved requirements  
✅ **Auto-Classification** - AI-powered ticket categorization (Bug vs Feature)  
✅ **Duplicate Detection** - Flags similar tickets to prevent redundant work  
✅ **Stale Ticket Cleanup** - Auto-closes inactive tickets after 60 days  
✅ **Real-time Dashboards** - Executive-ready metrics without manual reporting  
✅ **Slack/Email Integration** - Automated status updates and notifications  

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       INTAKE LAYER                           │
│    Slack │ Email │ Web Forms │ JIRA Portal                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   JIRA (Single Source of Truth)              │
│   Workflows │ Custom Fields │ Native Automation             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              AUTOMATION MIDDLEWARE (FastAPI)                 │
│   • BRD Gate Enforcement                                     │
│   • AI Classification                                        │
│   • Duplicate Detection                                      │
│   • Stale Cleanup                                            │
│   • Metrics Tracking                                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  INTEGRATIONS & OUTPUTS                      │
│   Slack │ GitHub │ Email │ Dashboards │ Reports             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start (30 Minutes to Operational)

### Prerequisites

- **JIRA Free Account** (up to 10 users) - [Sign up here](https://www.atlassian.com/software/jira/free)
- **Python 3.11+** installed
- **GitHub account** (for version control)
- **Railway.app account** (for free hosting) - [Sign up here](https://railway.app)

### Step 1: Set Up JIRA (10 minutes)

1. **Create JIRA account** at atlassian.com/software/jira/free
2. **Create your first project**:
   - Template: Kanban
   - Name: "Pilot Program"
   - Key: `PILOT`

3. **Add custom fields** (Settings → Issues → Custom fields):
   - Copy configurations from [`config/jira-custom-fields.json`](config/jira-custom-fields.json)
   - Create these fields:
     - Request Type (select list)
     - BRD Document Link (URL)
     - BRD Owner (user picker)
     - BRD Approved Date (date picker)

4. **Configure workflow**:
   - Use the template from [`config/jira-workflow-feature.yaml`](config/jira-workflow-feature.yaml)
   - Add these statuses: SUBMITTED → AWAITING_SCOPING → SCOPING_IN_PROGRESS → READY_FOR_DEV → IN_PROGRESS → QA_TESTING → DONE

5. **Get API token**:
   - Go to: https://id.atlassian.com/manage/api-tokens
   - Click "Create API token"
   - Save it securely

### Step 2: Deploy Automation Middleware (10 minutes)

1. **Clone this repository**:
   ```bash
   git clone <your-repo-url>
   cd pm-automation-system
   ```

2. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` with your JIRA credentials**:
   ```bash
   JIRA_URL=https://yourcompany.atlassian.net
   JIRA_EMAIL=your-email@company.com
   JIRA_API_TOKEN=your_jira_api_token
   JIRA_PROJECT_KEY=PILOT
   ```

4. **Deploy to Railway** (free tier):

   [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

   - Connect your GitHub repo
   - Railway auto-detects Dockerfile
   - Add environment variables from `.env`
   - Click "Deploy"
   - Copy your deployment URL (e.g., `https://pm-automation-production.up.railway.app`)

   **Alternative: Run locally**:
   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   # Access at: http://localhost:8000
   ```

### Step 3: Connect JIRA to Middleware (5 minutes)

1. **Configure webhooks** in JIRA:
   - Go to: Settings → System → WebHooks
   - Click "Create a WebHook"

2. **Add webhook for "Issue Created"**:
   - Name: `PM Automation - Issue Created`
   - URL: `https://your-railway-url.up.railway.app/webhooks/jira/issue-created`
   - Events: ✅ Issue Created
   - Click "Create"

3. **Add webhook for "Issue Updated"**:
   - Name: `PM Automation - Issue Transitioned`
   - URL: `https://your-railway-url.up.railway.app/webhooks/jira/issue-transitioned`
   - Events: ✅ Issue Updated
   - Click "Create"

### Step 4: Add JIRA Automation Rules (5 minutes)

1. Go to: **Project Settings → Automation**
2. Click "Create rule"
3. **Copy rules from** [`config/jira-automation-rules.yaml`](config/jira-automation-rules.yaml)

**Most Critical Rule to Add First: BRD Gate Enforcement**

- Trigger: Issue transitioned → to "IN_PROGRESS"
- Condition: BRD Approved Date is empty
- Action: Block issue transition with error message

---

## 📊 Access Your Dashboard

Once deployed, access these endpoints:

- **Health Check**: `https://your-url/health`
- **Program Health**: `https://your-url/api/program-health?project=PILOT`
- **Velocity Trends**: `https://your-url/api/velocity?project=PILOT`
- **Stale Tickets**: `https://your-url/api/stale-tickets`
- **Automation Stats**: `https://your-url/api/automation-stats`

### Google Sheets Dashboard (Free Alternative to Tableau)

See [`docs/google-sheets-dashboard.md`](docs/google-sheets-dashboard.md) for instructions on creating a real-time dashboard in Google Sheets.

---

## 🧪 Test Your Setup

1. **Create a test ticket** in JIRA:
   - Summary: "Test feature request"
   - Request Type: (leave empty to test auto-classification)

2. **Check automation worked**:
   - Ticket should auto-classify as "Feature"
   - Label "auto-classified" should be added
   - Check Railway logs to see webhook received

3. **Test BRD gate**:
   - Try to transition ticket to "IN_PROGRESS" without filling BRD fields
   - Should be blocked with error message ✅

---

## 📚 Documentation

- **[Setup Guide](docs/SETUP.md)** - Detailed step-by-step setup
- **[User Guide](docs/USER_GUIDE.md)** - How to use the system
- **[API Documentation](docs/API.md)** - API endpoints reference
- **[Automation Rules](config/jira-automation-rules.yaml)** - All automation rules explained
- **[Architecture](docs/ARCHITECTURE.md)** - Technical deep dive

---

## 🛠️ Configuration

### Environment Variables

All configuration is managed via `.env` file:

```bash
# Required
JIRA_URL=https://yourcompany.atlassian.net
JIRA_EMAIL=your-email@company.com
JIRA_API_TOKEN=your_token
JIRA_PROJECT_KEY=PILOT

# Optional - AI Features
OPENAI_API_KEY=sk-...
ENABLE_AI_CLASSIFICATION=true

# Optional - Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_NOTIFICATIONS_CHANNEL=#program-status
ENABLE_SLACK_NOTIFICATIONS=true

# Optional - Database (defaults to SQLite)
DATABASE_URL=sqlite+aiosqlite:///./pm_automation.db
```

### Automation Rules Configuration

Edit these values in `.env`:

```bash
STALE_TICKET_DAYS=60                    # Days before auto-close
SLA_CHECK_INTERVAL_MINUTES=30           # How often to check SLAs
DUPLICATE_SIMILARITY_THRESHOLD=0.8      # 0-1, higher = more strict
```

---

## 🔥 Key Features

### 1. BRD Gate Enforcement (Most Critical)

**Problem:** Development starts before requirements are clear, leading to rework  
**Solution:** Hard gate that prevents "IN_PROGRESS" transition without approved BRD

**How it works:**
- Ticket must have `BRD Document Link` populated
- Ticket must have `BRD Approved Date` set
- Bugs/Support Requests bypass this gate (only applies to Features/Enhancements)
- Violation attempts are blocked + logged + alerted

### 2. Auto-Classification (AI-Powered)

**Problem:** Tickets incorrectly categorized, wrong workflow applied  
**Solution:** AI analyzes title + description, classifies as Bug/Feature/Enhancement/Support

**How it works:**
- If OpenAI API key configured: Uses GPT-4 for semantic understanding
- Fallback: Keyword-based classification
- Updates "Request Type" field automatically
- Adds "auto-classified" label for tracking

### 3. Duplicate Detection

**Problem:** Multiple people request the same thing, wasting effort  
**Solution:** Semantic similarity search flags potential duplicates

**How it works:**
- Searches last 90 days of open tickets
- AI mode: Uses OpenAI embeddings for semantic similarity
- Fallback: String similarity (Levenshtein distance)
- Adds comment with links to similar tickets
- Adds "potential-duplicate" label

### 4. Stale Ticket Cleanup (Data Hygiene)

**Problem:** Hundreds of abandoned tickets clutter the backlog  
**Solution:** Auto-warns at 50 days, auto-closes at 60 days

**How it works:**
- Daily cron job scans for inactive tickets
- Day 50: Adds warning comment + sends email
- Day 60: Auto-closes + notifies reporter
- Exceptions: P0/P1 tickets never auto-close

### 5. Real-Time Metrics & Dashboards

**Problem:** Status reports take 4 hours/week to create  
**Solution:** Auto-generated metrics via API endpoints

**Available Metrics:**
- Program health score (0-100)
- Tickets by status
- Blocked tickets list
- BRD compliance rate
- Velocity trends (story points/week)
- Cycle time analysis
- Automation execution stats

---

## 🔐 Security & Compliance

- **API Authentication**: JIRA webhooks verified via signature
- **Data Encryption**: All JIRA API calls use HTTPS + API tokens
- **Audit Trail**: Every automation execution logged to database
- **GDPR Compliant**: No PII stored outside JIRA
- **Role-Based Access**: Inherits JIRA permission scheme

---

## 💰 Cost Breakdown

**Total Monthly Cost: $0-15**

| Service | Cost | Usage |
|---------|------|-------|
| JIRA Free | $0 | Up to 10 users, 2GB storage |
| Railway Free Tier | $0 | 500 hours/month compute |
| Google Sheets Dashboard | $0 | Unlimited |
| OpenAI API (optional) | ~$5/month | ~5,000 tickets/month |
| **TOTAL** | **$0-5/month** | |

**To scale to 50 users:**
- JIRA Standard: $7.75/user/month = $387.50
- Railway Hobby Plan: $5/month
- **Total: ~$393/month** for 50 users

---

## 📈 Expected ROI

Based on a 10-person TPM/PM team:

| Manual Process | Time Before | Time After | Savings |
|----------------|-------------|------------|---------|
| Weekly status reports | 4 hrs | 30 min | **3.5 hrs/week** |
| Duplicate request cleanup | 2 hrs | 0 hrs | **2 hrs/week** |
| Stale ticket grooming | 3 hrs | 0 hrs | **3 hrs/week** |
| BRD compliance tracking | 2 hrs | 0 hrs | **2 hrs/week** |
| **TOTAL** | **11 hrs/week** | **30 min/week** | **10.5 hrs/week** |

**Annual savings:**
- 10.5 hrs/week × 50 weeks = **525 hours/year**
- At $100/hour TPM rate = **$52,500/year saved**
- Cost of system: **$393/month × 12 = $4,716/year**
- **Net ROI: $47,784/year (10x return)**

---

## 🧪 Testing

Run automated tests:

```bash
pytest tests/ -v
```

Test coverage:
- Webhook handlers
- Automation rules logic
- JIRA API client
- Database operations

---

## 🚧 Roadmap

### Phase 1: MVP ✅ (Complete)
- [x] BRD gate enforcement
- [x] Auto-classification
- [x] Duplicate detection
- [x] Stale cleanup
- [x] Basic API endpoints

### Phase 2: Integrations (Next 30 days)
- [ ] Slack bot for ticket creation
- [ ] GitHub PR auto-linking
- [ ] Email intake automation
- [ ] Google Sheets dashboard template

### Phase 3: Advanced Features (Next 90 days)
- [ ] AI-powered BRD generation from meeting notes
- [ ] Predictive risk scoring
- [ ] Automated sprint planning suggestions
- [ ] Resource allocation optimizer

---

## 🐛 Troubleshooting

### Webhooks not triggering

1. Check Railway logs: `railway logs`
2. Verify webhook URL in JIRA is correct
3. Test webhook manually: `curl -X POST https://your-url/webhooks/jira/issue-created`

### BRD gate not blocking transitions

1. Verify automation rule is enabled in JIRA
2. Check custom field "BRD Approved Date" exists and is mapped correctly
3. Test with a ticket: leave BRD fields empty, try to move to IN_PROGRESS

### Database errors

- SQLite file permissions: `chmod 666 pm_automation.db`
- PostgreSQL connection: verify `DATABASE_URL` format

---

## 📞 Support

- **Issues**: Open a GitHub issue
- **Questions**: Email your-email@company.com
- **Slack**: #pm-automation (internal)

---

## 📝 License

Proprietary - Navi Sohi (Staff TPM)

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [JIRA Python API](https://jira.readthedocs.io/) - JIRA integration
- [OpenAI API](https://platform.openai.com/) - AI features
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM

---

**Built with ❤️ by Navi Sohi**  
*Staff Technical Program Manager | Lean Six Sigma Black Belt | Automation Advocate*
