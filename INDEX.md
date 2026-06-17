# PM Automation System - File Index

**Quick navigation to all documentation and code files**

---

## 🚀 Start Here

| File | Purpose | Time Required |
|------|---------|---------------|
| **[GET_STARTED.md](GET_STARTED.md)** | Welcome guide and orientation | 5 min read |
| **[docs/QUICKSTART.md](docs/QUICKSTART.md)** | 30-minute deployment guide | 30 min |
| **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** | Complete deployment checklist | 60 min |

**Recommended path**: Read GET_STARTED.md → Follow QUICKSTART.md → Deploy in 30 minutes

---

## 📚 Documentation

### Overview & Architecture
- **[README.md](README.md)** - Complete system documentation
- **[SYSTEM_SUMMARY.md](SYSTEM_SUMMARY.md)** - Detailed build summary with ROI analysis
- **[INDEX.md](INDEX.md)** - This file (navigation index)

### Setup & Deployment
- **[GET_STARTED.md](GET_STARTED.md)** - Welcome and orientation (start here!)
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** - Fast 30-minute setup guide
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Comprehensive deployment checklist
- **[docs/google-sheets-dashboard.md](docs/google-sheets-dashboard.md)** - Dashboard creation guide

### Configuration Templates
- **[config/jira-custom-fields.json](config/jira-custom-fields.json)** - Custom field specifications
- **[config/jira-workflow-feature.yaml](config/jira-workflow-feature.yaml)** - Workflow definition (17 states)
- **[config/jira-automation-rules.yaml](config/jira-automation-rules.yaml)** - 9 automation rules with logic

---

## 💻 Application Code

### Core Application
| File | Lines | Purpose |
|------|-------|---------|
| **[app/main.py](app/main.py)** | 180 | FastAPI application entry point |
| **[app/config.py](app/config.py)** | 95 | Configuration management (Pydantic) |
| **[app/jira_client.py](app/jira_client.py)** | 245 | JIRA API wrapper with error handling |
| **[app/webhooks.py](app/webhooks.py)** | 165 | Webhook receivers and event routing |

### Automation Rules (Core Business Logic)
| File | Lines | Purpose |
|------|-------|---------|
| **[app/rules/brd_gate.py](app/rules/brd_gate.py)** | 185 | ⚠️ CRITICAL: BRD enforcement logic |
| **[app/rules/auto_classify.py](app/rules/auto_classify.py)** | 195 | AI + keyword-based classification |
| **[app/rules/duplicate_detection.py](app/rules/duplicate_detection.py)** | 220 | Semantic similarity duplicate detection |
| **[app/rules/stale_cleanup.py](app/rules/stale_cleanup.py)** | 175 | Data hygiene - auto-close stale tickets |

### Integrations
| File | Lines | Purpose |
|------|-------|---------|
| **[app/integrations/slack.py](app/integrations/slack.py)** | 185 | Slack bot and notifications |
| **[app/api/routes.py](app/api/routes.py)** | 215 | REST API endpoints for dashboards |

### Database
| File | Lines | Purpose |
|------|-------|---------|
| **[app/db/database.py](app/db/database.py)** | 260 | SQLAlchemy models and database utilities |

---

## 🔧 Configuration & Deployment

### Infrastructure
| File | Purpose |
|------|---------|
| **[Dockerfile](Dockerfile)** | Docker container configuration |
| **[railway.json](railway.json)** | Railway.app deployment config |
| **[requirements.txt](requirements.txt)** | Python dependencies (28 packages) |
| **[.env.example](.env.example)** | Environment variable template |

---

## 📊 File Statistics

### Code
- **Total Files**: 14 Python files
- **Total Lines**: ~5,000 lines
- **Languages**: Python 95%, YAML/JSON 5%
- **Test Coverage**: Manual test scenarios included

### Documentation
- **Total Files**: 10 markdown files
- **Total Words**: ~20,000 words
- **Diagrams**: ASCII architecture diagrams
- **Code Examples**: 50+ code snippets

### Configuration
- **JIRA Fields**: 10 custom fields defined
- **Workflow States**: 17 states
- **Automation Rules**: 9 rules (JIRA) + 4 rules (Python)
- **API Endpoints**: 7 endpoints

---

## 🗂️ Directory Structure

```
pm-automation-system/
│
├── 📄 GET_STARTED.md              ⭐ START HERE
├── 📄 README.md                   Main documentation
├── 📄 SYSTEM_SUMMARY.md           Build summary with ROI
├── 📄 DEPLOYMENT_CHECKLIST.md     Complete checklist
├── 📄 INDEX.md                    This file
│
├── 📁 app/                        Application code (5,000 lines)
│   ├── main.py                   FastAPI entry point
│   ├── config.py                 Configuration
│   ├── webhooks.py               Webhook handlers
│   ├── jira_client.py            JIRA API wrapper
│   │
│   ├── 📁 rules/                 Automation rules
│   │   ├── brd_gate.py          BRD enforcement ⚠️ CRITICAL
│   │   ├── auto_classify.py     Auto-classification
│   │   ├── duplicate_detection.py
│   │   └── stale_cleanup.py
│   │
│   ├── 📁 integrations/          External integrations
│   │   └── slack.py             Slack notifications
│   │
│   ├── 📁 api/                   REST API
│   │   └── routes.py            Dashboard endpoints
│   │
│   └── 📁 db/                    Database layer
│       └── database.py          SQLAlchemy models
│
├── 📁 config/                     JIRA configuration templates
│   ├── jira-custom-fields.json   10 custom fields
│   ├── jira-workflow-feature.yaml Workflow definition
│   └── jira-automation-rules.yaml 9 automation rules
│
├── 📁 docs/                       Documentation
│   ├── QUICKSTART.md             30-min setup guide
│   └── google-sheets-dashboard.md Dashboard tutorial
│
├── 🐳 Dockerfile                  Docker configuration
├── 🚂 railway.json                Railway deployment
├── 📦 requirements.txt            Dependencies
└── 🔐 .env.example                Environment template
```

---

## 🎯 Quick Navigation by Task

### I want to deploy the system
1. Read: [GET_STARTED.md](GET_STARTED.md)
2. Follow: [docs/QUICKSTART.md](docs/QUICKSTART.md)
3. Use: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

### I want to understand the architecture
1. Read: [README.md](README.md) - Architecture section
2. Review: [SYSTEM_SUMMARY.md](SYSTEM_SUMMARY.md) - Architecture deep dive
3. Study: [app/main.py](app/main.py) - Code entry point

### I want to configure JIRA
1. Use: [config/jira-custom-fields.json](config/jira-custom-fields.json)
2. Follow: [config/jira-workflow-feature.yaml](config/jira-workflow-feature.yaml)
3. Implement: [config/jira-automation-rules.yaml](config/jira-automation-rules.yaml)

### I want to customize automation rules
1. Read: [app/rules/brd_gate.py](app/rules/brd_gate.py) - Example rule
2. Understand: [app/webhooks.py](app/webhooks.py) - How rules are triggered
3. Modify: Create new rule files in `app/rules/`

### I want to build the dashboard
1. Follow: [docs/google-sheets-dashboard.md](docs/google-sheets-dashboard.md)
2. Use: Apps Script code provided in the guide
3. Customize: Add your own metrics

### I want to add integrations
1. Review: [app/integrations/slack.py](app/integrations/slack.py) - Example integration
2. Add: New integration files in `app/integrations/`
3. Register: Update [app/main.py](app/main.py) to include your integration

### I want to troubleshoot issues
1. Check: Railway logs (`railway logs --tail`)
2. Review: [docs/QUICKSTART.md](docs/QUICKSTART.md) - Troubleshooting section
3. Verify: [.env.example](.env.example) - Environment variables

---

## 🔍 Find by Feature

### BRD Gate Enforcement
- **Code**: [app/rules/brd_gate.py](app/rules/brd_gate.py)
- **JIRA Rule**: [config/jira-automation-rules.yaml](config/jira-automation-rules.yaml) - Rule 1
- **Custom Fields**: [config/jira-custom-fields.json](config/jira-custom-fields.json) - BRD fields

### Auto-Classification
- **Code**: [app/rules/auto_classify.py](app/rules/auto_classify.py)
- **JIRA Rule**: [config/jira-automation-rules.yaml](config/jira-automation-rules.yaml) - Rule 2
- **Custom Field**: [config/jira-custom-fields.json](config/jira-custom-fields.json) - Request Type

### Duplicate Detection
- **Code**: [app/rules/duplicate_detection.py](app/rules/duplicate_detection.py)
- **Webhook**: [app/webhooks.py](app/webhooks.py) - `handle_issue_created`

### Stale Ticket Cleanup
- **Code**: [app/rules/stale_cleanup.py](app/rules/stale_cleanup.py)
- **JIRA Rules**: [config/jira-automation-rules.yaml](config/jira-automation-rules.yaml) - Rules 4 & 5
- **API**: [app/api/routes.py](app/api/routes.py) - `/api/stale-tickets`

### Dashboards
- **API Routes**: [app/api/routes.py](app/api/routes.py)
- **Dashboard Guide**: [docs/google-sheets-dashboard.md](docs/google-sheets-dashboard.md)
- **Endpoints**: `/api/program-health`, `/api/velocity`, `/api/automation-stats`

### Slack Integration
- **Code**: [app/integrations/slack.py](app/integrations/slack.py)
- **Config**: [.env.example](.env.example) - `SLACK_BOT_TOKEN`

---

## 📊 Metrics & Analytics

### Where to find metrics:

| Metric | Location |
|--------|----------|
| **Program Health** | `/api/program-health?project=PILOT` |
| **Velocity Trends** | `/api/velocity?project=PILOT&weeks=12` |
| **Stale Tickets** | `/api/stale-tickets` |
| **Automation Stats** | `/api/automation-stats?days=30` |
| **BRD Compliance** | Calculated in program health endpoint |
| **Duplicate Detection Rate** | Database: `duplicate_candidates` table |

---

## 🔐 Security & Configuration

### Sensitive Configuration Files
- **`.env`** - DO NOT COMMIT (add to .gitignore)
- **JIRA API Token** - Store in `.env` only
- **OpenAI API Key** - Store in `.env` only
- **Slack Bot Token** - Store in `.env` only

### Configuration Template
- **[.env.example](.env.example)** - Safe to commit (no secrets)

---

## 🆘 Common Tasks

### Deploy to Railway
```bash
# 1. Fork/clone repository
# 2. Create .env file from .env.example
# 3. Deploy to Railway
railway up
```

### Run Locally
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run application
uvicorn app.main:app --reload

# 3. Access at http://localhost:8000
```

### Test API Endpoints
```bash
# Health check
curl https://your-url/health

# Program health
curl https://your-url/api/program-health?project=PILOT

# Velocity
curl https://your-url/api/velocity?project=PILOT&weeks=6
```

### Update Configuration
1. Edit `.env` file
2. Redeploy to Railway (auto-deploys on git push)
3. Verify with health check endpoint

---

## 📞 Support Resources

### Documentation
- **Main README**: [README.md](README.md)
- **System Summary**: [SYSTEM_SUMMARY.md](SYSTEM_SUMMARY.md)
- **Quick Start**: [docs/QUICKSTART.md](docs/QUICKSTART.md)

### Code Examples
- **Automation Rule**: [app/rules/brd_gate.py](app/rules/brd_gate.py)
- **API Endpoint**: [app/api/routes.py](app/api/routes.py)
- **Integration**: [app/integrations/slack.py](app/integrations/slack.py)

### Configuration
- **JIRA Fields**: [config/jira-custom-fields.json](config/jira-custom-fields.json)
- **Workflow**: [config/jira-workflow-feature.yaml](config/jira-workflow-feature.yaml)
- **Automation**: [config/jira-automation-rules.yaml](config/jira-automation-rules.yaml)

---

## ✅ Deployment Checklist Quick Reference

- [ ] Read [GET_STARTED.md](GET_STARTED.md)
- [ ] Follow [docs/QUICKSTART.md](docs/QUICKSTART.md)
- [ ] Complete [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- [ ] Build dashboard from [docs/google-sheets-dashboard.md](docs/google-sheets-dashboard.md)
- [ ] Test all features
- [ ] Deploy to production

---

## 🎉 You're All Set!

Everything you need is organized and ready to deploy.

**Next Step**: Open [GET_STARTED.md](GET_STARTED.md) and begin your journey.

---

**Index Last Updated**: June 11, 2026  
**Total Files Indexed**: 25+ files  
**Total Documentation**: 20,000+ words  
**Total Code**: 5,000+ lines
