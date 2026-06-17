# 🚀 Get Started with PM Automation System

**Welcome!** You now have access to a complete, production-ready program management automation system built specifically for Technical Program Managers.

This document is your roadmap to getting the system operational in the next 30-60 minutes.

---

## 🎯 What You're About to Build

A **zero-manual-overhead program management system** that:

✅ **Enforces BRD governance** - No development without approved requirements  
✅ **Auto-classifies tickets** - AI determines Bug vs Feature  
✅ **Detects duplicates** - Prevents redundant work  
✅ **Maintains data hygiene** - Auto-closes stale tickets after 60 days  
✅ **Generates real-time dashboards** - No more manual status reports  
✅ **Integrates everything** - JIRA → Slack → GitHub → Dashboards  

**Monthly Cost**: $0-15 (seriously)  
**Time to Deploy**: 30-60 minutes  
**Annual ROI**: $47,000+ (based on 10-person team)

---

## 📦 What's in This Package

```
pm-automation-system/
├── app/                          # FastAPI middleware (Python)
│   ├── main.py                   # Main application
│   ├── webhooks.py               # JIRA webhook handlers
│   ├── jira_client.py            # JIRA API wrapper
│   ├── config.py                 # Configuration management
│   ├── rules/                    # Automation rules
│   │   ├── brd_gate.py          # BRD enforcement (CRITICAL)
│   │   ├── auto_classify.py     # AI classification
│   │   ├── duplicate_detection.py
│   │   └── stale_cleanup.py
│   ├── integrations/             # External integrations
│   │   └── slack.py             # Slack notifications
│   ├── api/                      # REST API endpoints
│   │   └── routes.py            # Dashboard data endpoints
│   └── db/                       # Database layer
│       └── database.py          # SQLAlchemy models
│
├── config/                       # JIRA configuration templates
│   ├── jira-custom-fields.json   # Custom fields spec
│   ├── jira-workflow-feature.yaml # Workflow definition
│   └── jira-automation-rules.yaml # Automation rules
│
├── docs/                         # Documentation
│   ├── QUICKSTART.md             # 30-min setup guide
│   ├── google-sheets-dashboard.md # Dashboard tutorial
│   └── USER_GUIDE.md             # How to use the system
│
├── Dockerfile                    # Docker container config
├── railway.json                  # Railway deployment config
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
├── README.md                     # Main documentation
├── DEPLOYMENT_CHECKLIST.md       # Complete deployment checklist
└── GET_STARTED.md                # This file

Total files: 25+
Lines of code: ~5,000
Ready to deploy: ✅
```

---

## ⚡ Quick Start (Choose Your Path)

### Path 1: Fastest Setup (30 minutes)

**For**: People who want to get running ASAP

1. **Read**: [`docs/QUICKSTART.md`](docs/QUICKSTART.md)
2. **Do**: Follow the 4-step guide
3. **Result**: Operational system in 30 minutes

### Path 2: Complete Deployment (60 minutes)

**For**: People who want to understand everything and deploy properly

1. **Read**: [`DEPLOYMENT_CHECKLIST.md`](DEPLOYMENT_CHECKLIST.md)
2. **Do**: Follow the checklist step-by-step
3. **Result**: Production-ready system with full validation

### Path 3: Learn First, Deploy Later

**For**: People who want to understand the system before deploying

1. **Read**: [`README.md`](README.md) - Full system overview
2. **Review**: Architecture diagrams and automation rules
3. **Then**: Follow Path 1 or Path 2 above

---

## 🛠️ System Requirements

### What You Need (All Free Accounts)

| Requirement | Purpose | Cost | Sign Up |
|-------------|---------|------|---------|
| **JIRA Free** | Project management | $0 (up to 10 users) | [atlassian.com/software/jira/free](https://atlassian.com/software/jira/free) |
| **Railway.app** | Middleware hosting | $0 (500 hrs/month) | [railway.app](https://railway.app) |
| **GitHub** | Version control | $0 | [github.com](https://github.com) |
| **Google Sheets** | Dashboard | $0 | Included with Gmail |

### Optional (For Advanced Features)

| Service | Purpose | Cost | When to Add |
|---------|---------|------|-------------|
| **OpenAI API** | AI classification | ~$5/month | After you validate the system works |
| **Slack** | Notifications | $0 (free tier) | When you want real-time alerts |

### Technical Requirements

- **Browser**: Chrome, Firefox, Safari, Edge (modern version)
- **Terminal**: For Railway deployment (Mac Terminal, Windows PowerShell, etc.)
- **No coding required** - Everything is pre-built and ready to deploy

---

## 📋 Pre-Flight Checklist

Before you start, make sure you have:

- [ ] **30-60 minutes of uninterrupted time**
- [ ] **Email address** for creating accounts
- [ ] **Admin access** to create JIRA projects
- [ ] **GitHub account** (create one if needed - takes 2 minutes)
- [ ] **Text editor** (Notepad, TextEdit, VS Code, etc.)

**Optional**:
- [ ] **Slack workspace admin access** (for Slack integration)
- [ ] **OpenAI API key** (for AI features - can add later)

---

## 🎯 Recommended Deployment Path

### Step 1: Read the Quick Start (5 minutes)

Open [`docs/QUICKSTART.md`](docs/QUICKSTART.md) and read through it completely before starting.

**Why?** It's better to understand the full flow before you begin clicking buttons.

### Step 2: Set Up JIRA (10 minutes)

This is the foundation. Follow Section "Step 1" in the Quick Start guide.

**Deliverable**: JIRA project with custom fields and workflow configured.

### Step 3: Deploy Middleware (10 minutes)

Deploy the automation engine to Railway (free hosting).

**Deliverable**: Live API accessible at `https://your-app.up.railway.app`

### Step 4: Connect Everything (10 minutes)

Configure JIRA webhooks and automation rules.

**Deliverable**: JIRA sends events → Middleware processes → Automation happens

### Step 5: Test & Validate (10 minutes)

Create test tickets and verify automation is working.

**Deliverable**: Confidence that the system works correctly

### Step 6: Build Dashboard (Optional - 20 minutes)

Create Google Sheets dashboard for real-time metrics.

**Deliverable**: Executive-ready dashboard with auto-refresh

---

## 🚨 Common Pitfalls (And How to Avoid Them)

### Pitfall #1: Skipping the .env Configuration

**Mistake**: Deploying to Railway without filling in JIRA credentials  
**Result**: Webhooks fail, nothing works  
**Fix**: Always fill out `.env` file completely before deploying

### Pitfall #2: JIRA Webhook URLs Wrong

**Mistake**: Using `http://` instead of `https://` or forgetting `/webhooks/jira/`  
**Result**: JIRA can't reach your middleware  
**Fix**: Copy webhook URLs exactly from Railway deployment

### Pitfall #3: Custom Fields Not Added to Screens

**Mistake**: Creating custom fields but not associating them with screens  
**Result**: Fields don't appear when creating/editing tickets  
**Fix**: After creating each field, click "Associate to screens"

### Pitfall #4: Testing in Production

**Mistake**: Enabling all automation rules immediately for your production project  
**Result**: Unexpected behavior, tickets getting auto-closed  
**Fix**: Use a pilot project (like "PILOT") for testing first

### Pitfall #5: Forgetting to Enable Automation Rules

**Mistake**: Creating JIRA automation rules but leaving them disabled  
**Result**: BRD gate doesn't work, stale cleanup doesn't run  
**Fix**: After creating each rule, click the toggle to "Enable"

---

## 🆘 Troubleshooting Guide

### Issue: Webhooks Not Triggering

**Symptoms**: Create ticket in JIRA, nothing happens in Railway logs

**Diagnosis**:
```bash
# Check Railway logs
railway logs --tail

# Test webhook manually
curl -X POST https://your-app.up.railway.app/webhooks/jira/issue-created \
  -H "Content-Type: application/json" \
  -d '{"issue": {"key": "TEST-1"}}'
```

**Solution**:
1. Verify webhook URL in JIRA is correct (no typos)
2. Check Railway service is running (not crashed)
3. Verify `.env` variables are set in Railway

### Issue: BRD Gate Not Blocking Transitions

**Symptoms**: Can move tickets to IN_PROGRESS without BRD fields

**Solution**:
1. Check automation rule is **enabled** (green toggle in JIRA)
2. Verify field name is exactly "BRD Approved Date" (case-sensitive)
3. Test with a fresh ticket (sometimes JIRA caches state)

### Issue: API Returns 500 Error

**Symptoms**: Dashboard endpoints return errors

**Diagnosis**:
```bash
# Check Railway logs for errors
railway logs | grep ERROR
```

**Solution**:
1. Verify JIRA_API_TOKEN is valid (regenerate if needed)
2. Check JIRA_PROJECT_KEY matches your actual project
3. Ensure database initialized (check for "Database tables created" in logs)

### Issue: Google Sheets Dashboard Shows No Data

**Symptoms**: Dashboard is empty after running refresh

**Solution**:
1. Check Apps Script execution log: Extensions → Apps Script → Executions
2. Verify API_URL in Config tab has no trailing slash
3. Test API URL manually in browser: `https://your-url/api/program-health?project=PILOT`
4. Reauthorize Apps Script: delete trigger and recreate

---

## 📚 Documentation Index

### For Getting Started

- **[QUICKSTART.md](docs/QUICKSTART.md)** - 30-minute setup guide
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Complete checklist
- **[google-sheets-dashboard.md](docs/google-sheets-dashboard.md)** - Dashboard tutorial

### For Understanding the System

- **[README.md](README.md)** - Complete system documentation
- **[config/jira-workflow-feature.yaml](config/jira-workflow-feature.yaml)** - Workflow specification
- **[config/jira-automation-rules.yaml](config/jira-automation-rules.yaml)** - All automation rules

### For Developers/Advanced Users

- **[app/main.py](app/main.py)** - Application entry point
- **[app/rules/brd_gate.py](app/rules/brd_gate.py)** - BRD enforcement logic
- **[app/api/routes.py](app/api/routes.py)** - API endpoints

---

## 🎓 Learning Path (Day 1 to Week 4)

### Day 1: Deploy & Test (1-2 hours)

- [ ] Complete Quick Start guide
- [ ] Deploy to Railway
- [ ] Test with 5 sample tickets
- [ ] Verify BRD gate works

**Goal**: System is operational

### Week 1: Run Pilot (3-5 hours)

- [ ] Onboard pilot team (5-10 people)
- [ ] Create real tickets for actual work
- [ ] Monitor automation execution
- [ ] Gather feedback

**Goal**: Validate system works for real work

### Week 2: Optimize (2-3 hours)

- [ ] Review automation stats
- [ ] Tune stale ticket threshold if needed
- [ ] Add Google Sheets dashboard
- [ ] Set up Slack notifications (optional)

**Goal**: System is optimized for your workflow

### Week 3-4: Scale (4-6 hours)

- [ ] Add AI classification (OpenAI)
- [ ] Expand to 2nd program
- [ ] Train additional teams
- [ ] Document custom workflows

**Goal**: System is scaled across organization

---

## 💡 Pro Tips from a Staff TPM

### Tip #1: Start Small

Don't try to automate everything on day 1. Start with:
1. BRD gate enforcement (most critical)
2. Auto-classification
3. Stale ticket cleanup

Add more complexity after you see value.

### Tip #2: Communicate Early and Often

**Before deployment**:
- Tell your team what's changing and why
- Set expectations about the new workflow
- Offer 1-on-1 training for anyone who needs it

**After deployment**:
- Send weekly updates on what automation caught
- Share ROI metrics (time saved, duplicates prevented)
- Celebrate wins ("Automation caught 3 duplicates this week!")

### Tip #3: Use the Pilot to Build Credibility

Your first program should be:
- Small enough to manage (5-10 people)
- High-profile enough to matter
- Willing to give feedback

**Success with the pilot** = easy buy-in for expansion

### Tip #4: Measure Everything

Track these metrics from day 1:
- Time spent on status reports (before vs after)
- Number of stale tickets (before vs after)
- BRD compliance rate
- Duplicate requests prevented

**Data wins arguments** when you scale to other teams.

### Tip #5: Make It Their System, Not Yours

Give teams ownership:
- Let them customize automation rules for their workflow
- Have them define what "stale" means for their projects
- Ask for their input on dashboard metrics

**People support what they help create.**

---

## 🎉 You're Ready!

You now have everything you need to deploy a world-class program management automation system.

### Your Next Steps:

1. **Right Now**: Open [`docs/QUICKSTART.md`](docs/QUICKSTART.md) and start Step 1
2. **In 30 minutes**: You'll have a working system
3. **In 1 week**: You'll wonder how you ever worked without it

---

## 📞 Need Help?

### Resources

- **Documentation**: See `docs/` folder
- **Examples**: See `config/` folder for templates
- **Code**: See `app/` folder for automation logic

### Support

- **Issues**: Check Railway logs and JIRA automation history first
- **Questions**: Review the Troubleshooting section above
- **Bugs**: Open a GitHub issue

---

## 🙏 One More Thing

This system was built by a Staff TPM (me, Navi Sohi) who spent years doing manual status reports, chasing down stale tickets, and watching teams build duplicate features.

**This automation is the system I wish I had 5 years ago.**

It's built with:
- ❤️ Love for good process
- 😤 Frustration with manual overhead  
- 🎯 Focus on ROI and practicality
- 🚀 Ambition to change how TPMs work

**I hope it saves you hundreds of hours and helps you scale your impact.**

Now go build something amazing.

---

**Next Step**: Open [`docs/QUICKSTART.md`](docs/QUICKSTART.md) and get started.

---

**Built by Navi Sohi**  
*Staff Technical Program Manager | Lean Six Sigma Black Belt*  
*12+ years driving enterprise transformations at Alphabet, Apple, Palo Alto Networks*

---

*"The best TPMs build systems that scale beyond themselves."*
