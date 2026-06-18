# PMO Automation System - End-to-End

**Complete program management automation from stakeholder intake → roadmap → scoping → sprint execution**

Built by: Navi Sohi, Staff TPM  
Purpose: Automate strategic planning, enforce governance, eliminate manual overhead  
Status: **Phase 1 Complete ✅ | Phases 2-4 Planned 📋**

---

## 🎯 What This System Does

This is a **complete PMO automation platform** that creates a structured pipeline from business request to delivered software:

### ✅ Phase 1: Epic Intake Automation (COMPLETE)
- **Stakeholder Intake:** Google Form → Auto-creates JIRA Epics when approved
- **Auto-Sync Fields:** Priority, Due Date, Request Type, Labels (Sheet → JIRA)
- **BRD Gate:** Prevents Story transitions without complete requirements
- **One-Way Sync:** Google Sheet controls JIRA (not bidirectional)

### 📋 Phase 2: Epic Workflow & Roadmap (PLANNED)
- **Epic Lifecycle:** INTAKE → UNDER_REVIEW → BACKLOG → IN_ROADMAP → IN_EXECUTION → COMPLETED
- **Roadmap Board:** Now/Next/Later visualization by quarter
- **Capacity Planning:** Track team capacity vs. committed Epics
- **Auto-Notifications:** Stakeholder alerts at each Epic status change

### 📋 Phase 3: Story-Level BRD Workflow (PLANNED)
- **Story Breakdown:** Guided process to split Epics into Stories
- **BRD Template:** User Story, Acceptance Criteria, Technical Approach
- **Definition of Ready:** Enforce checklist before sprint commitment
- **Enhanced BRD Gate:** Block Story transitions without complete BRD

### 📋 Phase 4: Sprint Execution & Metrics (PLANNED)
- **Sprint Planning:** Auto-populate backlog from READY_FOR_DEV Stories
- **Daily Standup:** Slack summary of progress, blockers, burndown
- **Velocity Tracking:** Team performance trends, predictability scores
- **Metrics Dashboard:** Real-time burndown, Epic progress, roadmap status

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                   STRATEGIC LAYER (Epic Level)                 │
│                                                                │
│  Stakeholder → Google Form → Google Sheet → JIRA Epic         │
│                      ↓                                         │
│              IT Leadership Review                              │
│                      ↓                                         │
│         Approve → Roadmap (Now/Next/Later)                     │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                   TACTICAL LAYER (Story Level)                 │
│                                                                │
│       Epic → Stories → BRD Process → READY_FOR_DEV             │
│                      ↓                                         │
│              Sprint Backlog Queue                              │
└────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                  OPERATIONAL LAYER (Sprint Level)              │
│                                                                │
│  Sprint Planning → Daily Execution → Sprint Review/Retro      │
│                      ↓                                         │
│          Velocity Tracking, Burndown Charts                    │
└────────────────────────────────────────────────────────────────┘
```

---

## 📦 Components

### Current (Phase 1)
| Component | Technology | Purpose | Status |
|-----------|-----------|---------|--------|
| **Intake Form** | Google Forms | Stakeholder submissions | ✅ Live |
| **Review Sheet** | Google Sheets | IT Leadership assessment | ✅ Live |
| **Epic Creator** | Google Apps Script | Auto-create JIRA Epics | ✅ Live |
| **Field Sync** | Google Apps Script | Sheet → JIRA updates | ✅ Live |
| **BRD Gate** | Railway (Node.js) | Block transitions without BRD | ✅ Live |
| **JIRA Project** | JIRA Cloud | Project management | ✅ Live |

### Planned (Phases 2-4)
| Component | Technology | Purpose | Status |
|-----------|-----------|---------|--------|
| **Epic Workflow** | JIRA Automation | Status transitions, notifications | 📋 Planned |
| **Roadmap Board** | JIRA Kanban | Now/Next/Later visualization | 📋 Planned |
| **Story Templates** | JIRA Templates | BRD structure enforcement | 📋 Planned |
| **Sprint Automation** | JIRA Automation | Auto-populate sprint backlog | 📋 Planned |
| **Slack Bot** | Slack API | Daily standup summaries | 📋 Planned |
| **Metrics Dashboard** | JIRA Dashboards | Real-time velocity, burndown | 📋 Planned |

---

## 🚀 Quick Start

### For Phase 1 (Current)
See: **[SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)** for step-by-step deployment.

**Summary:**
1. Create JIRA project with Request Type custom field
2. Deploy Google Form + Sheet
3. Install Google Apps Script with JIRA credentials
4. Create installable trigger (On edit)
5. Test Epic creation

### For Phases 2-4 (Future)
See: **[FULL_PMO_ROADMAP.md](FULL_PMO_ROADMAP.md)** for implementation plan.

---

## 📋 Documentation

### Core Docs
- **[FULL_PMO_ROADMAP.md](FULL_PMO_ROADMAP.md)** - Complete end-to-end vision, Phases 1-4
- **[COMPLETED_PHASE1.md](COMPLETED_PHASE1.md)** - Phase 1 full documentation
- **[SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)** - Phase 1 deployment guide
- **[SYSTEM_SUMMARY.md](SYSTEM_SUMMARY.md)** - Technical architecture

### Configuration Files
- **[google-apps-script-COMPLETE-WITH-REQUEST-TYPE.txt](google-apps-script-COMPLETE-WITH-REQUEST-TYPE.txt)** - Apps Script source code
- **[config/jira-custom-fields.json](config/jira-custom-fields.json)** - JIRA field definitions
- **[.env.example](.env.example)** - Environment variables template

### Additional Docs
- **[IT_Project_Intake_Form_MVP.md](IT_Project_Intake_Form_MVP.md)** - Intake form questions
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Railway deployment checklist
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** - Quick reference guide

---

## 🎯 Use Cases

### Strategic Planning (Executives/TPMs)
- **Roadmap Visualization:** See all approved initiatives by quarter
- **Capacity Planning:** Avoid over-commitment, balance workload
- **Stakeholder Communication:** Automated status updates reduce noise

### Requirements Definition (BAs/Product Owners)
- **BRD Enforcement:** No development without clear acceptance criteria
- **Story Templates:** Consistent structure across all teams
- **Definition of Ready:** Checklist ensures dev-ready Stories

### Sprint Execution (Scrum Masters/Developers)
- **Sprint Planning:** Auto-populated backlog based on READY_FOR_DEV queue
- **Daily Standup:** Slack summaries replace manual status updates
- **Velocity Tracking:** Data-driven capacity forecasting

---

## 📊 Success Metrics

### Phase 1 (Current)
- **Intake Time:** 5 minutes (down from 15 minutes manual JIRA entry)
- **Epic Creation:** 10 seconds automated (vs. 5-10 minutes manual)
- **Data Accuracy:** 100% (no manual transcription errors)
- **Epics Created:** 4 production Epics (PGMAUTO-1 to PGMAUTO-4)

### Phases 2-4 (Targets)
- **Backlog Prioritization:** 30 minutes per quarter (vs. 2 hours manual)
- **BRD Completion:** 2 hours per Story (down from 4 hours)
- **Sprint Predictability:** 85% of committed Stories completed
- **Velocity Variance:** <15% sprint-to-sprint
- **Time to Metrics:** Real-time (vs. weekly manual reports)

---

## 🔧 Technology Stack

### Current
- **Frontend:** Google Forms (intake), Google Sheets (review)
- **Automation:** Google Apps Script
- **Project Management:** JIRA Cloud (Scrum template)
- **Middleware:** Railway (Node.js/Express) - BRD gate
- **API:** JIRA REST API v3

### Planned
- **Workflow:** JIRA Automation (native rules engine)
- **Notifications:** Slack API
- **Metrics/BI:** JIRA Dashboards (or Tableau/Power BI)
- **Documentation:** Confluence (sprint reviews, retros)

---

## 🔐 Security

### Current Implementation
- ✅ JIRA API token stored in Google Apps Script (encrypted at rest)
- ✅ Google Sheet access restricted to IT Leadership
- ✅ Form submissions logged with timestamp + email
- ✅ `.env` file in `.gitignore` (credentials never committed)

### Planned Enhancements
- [ ] Rotate API tokens every 90 days
- [ ] Service account for automation (avoid personal tokens)
- [ ] Audit log for all Epic/Story status changes
- [ ] GDPR compliance: Right to delete form submissions

---

## 📈 Production URLs

### Phase 1 (Live)
- **Google Form:** https://forms.gle/w3nfUnipveyAhxss5
- **Google Sheet:** https://docs.google.com/spreadsheets/d/158zDAbms5TR7rIJeTfG6o9FpMDlz3AY2HpYqcizLVtQ/edit
- **JIRA Project:** https://nksaidev.atlassian.net/jira/software/projects/PGMAUTO
- **Railway BRD Gate:** https://pm-automation-system-production.up.railway.app

---

## 🛠️ Development

### Local Setup
```bash
# Clone repo
git clone https://github.com/[your-username]/pm-automation-system.git
cd pm-automation-system

# Install dependencies (for Railway middleware)
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your JIRA credentials
nano .env

# Run locally (Railway middleware only)
uvicorn app.main:app --reload
```

### Google Apps Script Development
1. Open Google Sheet
2. Extensions → Apps Script
3. Edit `google-apps-script-COMPLETE-WITH-REQUEST-TYPE.txt`
4. Save and test with `setup()` function

---

## 🗺️ Roadmap

| Phase | Timeline | Status |
|-------|----------|--------|
| **Phase 1: Epic Intake** | ✅ Complete (June 2026) | Production |
| **Phase 2: Epic Workflow & Roadmap** | Q3 2026 (2 weeks) | Planned |
| **Phase 3: Story BRD Workflow** | Q3-Q4 2026 (3 weeks) | Planned |
| **Phase 4: Sprint Execution & Metrics** | Q4 2026 (4 weeks) | Planned |

**Total Timeline:** 9-10 weeks (with testing & rollout)

See **[FULL_PMO_ROADMAP.md](FULL_PMO_ROADMAP.md)** for detailed implementation plan.

---

## 🤝 Contributing

We welcome contributions for Phases 2-4 implementation!

**To contribute:**
1. Fork the repo
2. Create feature branch: `git checkout -b phase2-roadmap-board`
3. Implement with tests
4. Submit PR with:
   - Implementation guide (`PHASE_X_SETUP.md`)
   - Configuration files (JSON)
   - Test results (screenshots)

**Discussion:**
- GitHub Issues: Feature requests & bugs
- GitHub Discussions: Architecture decisions for future phases

---

## 📞 Support

### Maintainers
- **Primary:** nks.ai.dev@gmail.com
- **GitHub:** [your-repo]/pm-automation-system

### Getting Help
1. Check **[SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)** for troubleshooting
2. Search GitHub Issues for known problems
3. Create new issue with:
   - Phase number (1, 2, 3, or 4)
   - Error message or unexpected behavior
   - Steps to reproduce

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **JIRA REST API v3** - For comprehensive project management API
- **Google Apps Script** - For serverless automation platform
- **Railway** - For simple middleware hosting
- **Slack API** - For team communication integration (Phase 4)

---

**Built with ❤️ by Navi Sohi**
