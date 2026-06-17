# Google Sheets Dashboard Setup
## Free Real-Time Program Management Dashboard

Create a live dashboard that pulls data from your PM Automation System and JIRA - completely free.

**What you'll build:**
- Real-time program health metrics
- Velocity trends chart
- Blocked tickets alert list
- BRD compliance tracking
- Stale tickets report

**Cost:** $0 (Google Sheets is free)  
**Time to build:** 30 minutes  
**Updates:** Every hour (or on-demand)

---

## Step 1: Create Google Sheet

1. Go to: https://sheets.google.com
2. Click "Blank" to create new sheet
3. Rename: "PM Automation Dashboard - [Your Program]"

---

## Step 2: Set Up Tabs

Create these tabs (click + at bottom):

1. **Dashboard** - Main view with charts and KPIs
2. **Raw Data** - Auto-populated from API
3. **Velocity** - Historical velocity data
4. **Stale Tickets** - Tickets at risk
5. **Config** - API URL and settings

---

## Step 3: Configure API Connection

### 3.1 Add Config Tab

In the **Config** tab, add:

| Parameter | Value |
|-----------|-------|
| API_URL | https://your-railway-url |
| PROJECT_KEY | PILOT |
| REFRESH_INTERVAL | 3600 (seconds) |

### 3.2 Add Apps Script

1. Click **Extensions → Apps Script**
2. Delete default code
3. Paste this script:

```javascript
/**
 * PM Automation System - Google Sheets Integration
 * Fetches data from FastAPI middleware and populates sheets
 */

// Get configuration from Config sheet
function getConfig() {
  const configSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Config');
  return {
    apiUrl: configSheet.getRange('B1').getValue(), // API_URL
    projectKey: configSheet.getRange('B2').getValue(), // PROJECT_KEY
    refreshInterval: configSheet.getRange('B3').getValue() // REFRESH_INTERVAL
  };
}

/**
 * Fetch data from API endpoint
 */
function fetchAPIData(endpoint) {
  const config = getConfig();
  const url = `${config.apiUrl}${endpoint}`;

  try {
    const response = UrlFetchApp.fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      },
      muteHttpExceptions: true
    });

    if (response.getResponseCode() === 200) {
      return JSON.parse(response.getContentText());
    } else {
      Logger.log(`API Error: ${response.getResponseCode()} - ${response.getContentText()}`);
      return null;
    }
  } catch (error) {
    Logger.log(`Fetch Error: ${error}`);
    return null;
  }
}

/**
 * Update Program Health Data
 */
function updateProgramHealth() {
  const config = getConfig();
  const data = fetchAPIData(`/api/program-health?project=${config.projectKey}`);

  if (!data) {
    Logger.log('Failed to fetch program health data');
    return;
  }

  // Get Raw Data sheet
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Raw Data');
  sheet.clear();

  // Write headers
  sheet.appendRow([
    'Timestamp',
    'Total Tickets',
    'Blocked Count',
    'At Risk Count',
    'BRD Compliance %',
    'Health Score'
  ]);

  // Write data
  sheet.appendRow([
    new Date(data.timestamp),
    data.total_tickets,
    data.blocked_count,
    data.at_risk_count,
    data.brd_compliance_rate,
    data.health_score
  ]);

  // Write tickets by status
  sheet.appendRow(['']); // Blank row
  sheet.appendRow(['Status', 'Count']);

  for (const [status, count] of Object.entries(data.by_status)) {
    sheet.appendRow([status, count]);
  }

  // Write blocked tickets
  if (data.blocked_tickets && data.blocked_tickets.length > 0) {
    sheet.appendRow(['']); // Blank row
    sheet.appendRow(['Blocked Tickets']);
    sheet.appendRow(['Key', 'Summary', 'Assignee']);

    data.blocked_tickets.forEach(ticket => {
      sheet.appendRow([
        ticket.key,
        ticket.summary,
        ticket.assignee
      ]);
    });
  }

  Logger.log('✅ Program health data updated');
}

/**
 * Update Velocity Trends
 */
function updateVelocity() {
  const config = getConfig();
  const data = fetchAPIData(`/api/velocity?project=${config.projectKey}&weeks=12`);

  if (!data) {
    Logger.log('Failed to fetch velocity data');
    return;
  }

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Velocity');
  sheet.clear();

  // Headers
  sheet.appendRow(['Week Start', 'Week End', 'Tickets Completed', 'Story Points']);

  // Data
  data.velocity_by_week.forEach(week => {
    sheet.appendRow([
      week.week_start,
      week.week_end,
      week.tickets_completed,
      week.story_points
    ]);
  });

  // Add average
  sheet.appendRow(['']); // Blank row
  sheet.appendRow(['Average Velocity', '', '', data.average_velocity]);

  Logger.log('✅ Velocity data updated');
}

/**
 * Update Stale Tickets Report
 */
function updateStaleTickets() {
  const data = fetchAPIData('/api/stale-tickets');

  if (!data) {
    Logger.log('Failed to fetch stale tickets data');
    return;
  }

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Stale Tickets');
  sheet.clear();

  // Warning Zone
  sheet.appendRow(['⚠️ Warning Zone (50-60 days)', '', '', '']);
  sheet.appendRow(['Key', 'Summary', 'Last Updated', 'Reporter']);

  data.warning_zone.tickets.forEach(ticket => {
    sheet.appendRow([
      ticket.key,
      ticket.summary,
      ticket.last_updated,
      ticket.reporter
    ]);
  });

  // Critical Zone
  sheet.appendRow(['']); // Blank row
  sheet.appendRow(['🚨 Critical Zone (60+ days - will auto-close)', '', '', '']);
  sheet.appendRow(['Key', 'Summary', 'Last Updated', 'Reporter']);

  data.critical_zone.tickets.forEach(ticket => {
    sheet.appendRow([
      ticket.key,
      ticket.summary,
      ticket.last_updated,
      ticket.reporter
    ]);
  });

  Logger.log('✅ Stale tickets data updated');
}

/**
 * Main refresh function - updates all data
 */
function refreshAllData() {
  Logger.log('🔄 Starting data refresh...');

  updateProgramHealth();
  updateVelocity();
  updateStaleTickets();

  // Update Dashboard timestamp
  const dashboard = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Dashboard');
  dashboard.getRange('A1').setValue(`Last Updated: ${new Date()}`);

  Logger.log('✅ All data refreshed successfully');
}

/**
 * Set up automatic refresh trigger
 */
function setupAutoRefresh() {
  // Delete existing triggers
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => ScriptApp.deleteTrigger(trigger));

  // Create new trigger - refresh every hour
  ScriptApp.newTrigger('refreshAllData')
    .timeBased()
    .everyHours(1)
    .create();

  Logger.log('✅ Auto-refresh trigger set up (every 1 hour)');
}

/**
 * Menu function for manual refresh
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('PM Automation')
    .addItem('🔄 Refresh Data', 'refreshAllData')
    .addItem('⚙️ Setup Auto-Refresh', 'setupAutoRefresh')
    .addToUi();
}
```

4. Click **Save** (💾 icon)
5. Name the project: "PM Automation Integration"

### 3.3 Authorize Script

1. Close Apps Script tab
2. Refresh your Google Sheet
3. You'll see new menu: **PM Automation**
4. Click **PM Automation → Refresh Data**
5. Click "Continue" → "Advanced" → "Go to PM Automation Integration (unsafe)"
6. Click "Allow"

**First run will populate all data tabs!**

---

## Step 4: Build Dashboard Tab

### 4.1 Add KPI Cards

In the **Dashboard** tab, create this layout:

**Row 1:**
```
Last Updated: =NOW()
```

**Row 3 (KPI Headers):**
| Health Score | Total Tickets | Blocked | At Risk | BRD Compliance |
|--------------|---------------|---------|---------|----------------|

**Row 4 (KPI Values - formulas):**

- **A4** (Health Score):
  ```
  ='Raw Data'!F2
  ```

- **B4** (Total Tickets):
  ```
  ='Raw Data'!B2
  ```

- **C4** (Blocked):
  ```
  ='Raw Data'!C2
  ```

- **D4** (At Risk):
  ```
  ='Raw Data'!D2
  ```

- **E4** (BRD Compliance):
  ```
  ='Raw Data'!E2 & "%"
  ```

**Format KPIs:**
1. Select Row 4 (KPI values)
2. Font size: 24pt
3. Bold
4. Center align

**Conditional Formatting:**

Health Score (A4):
- Green if ≥ 80
- Yellow if 60-79
- Red if < 60

BRD Compliance (E4):
- Green if ≥ 90
- Yellow if 70-89
- Red if < 70

### 4.2 Add Velocity Trend Chart

1. Select data in **Velocity** tab: columns A, D (Week Start, Story Points)
2. Insert → Chart
3. Chart type: Line chart
4. Customize:
   - Title: "Velocity Trend (Story Points/Week)"
   - Horizontal axis: Week Start
   - Vertical axis: Story Points
5. Move chart to **Dashboard** tab (below KPIs)

### 4.3 Add Status Breakdown Pie Chart

1. Go to **Raw Data** tab
2. Select status data (starts after row 8)
3. Insert → Chart
4. Chart type: Pie chart
5. Title: "Tickets by Status"
6. Move to **Dashboard** tab

### 4.4 Add Blocked Tickets Table

In **Dashboard** tab (below charts):

**Headers:**
| 🚨 BLOCKED TICKETS |
|-------------------|

**Import data from Raw Data:**
```
=QUERY('Raw Data'!A:C, "SELECT * WHERE A contains 'PILOT-' LIMIT 5")
```

This shows top 5 blocked tickets.

---

## Step 5: Set Up Auto-Refresh

1. Click **PM Automation → Setup Auto-Refresh**
2. Confirm authorization
3. Data will now refresh every hour automatically ✅

**Manual refresh anytime:**
- Click **PM Automation → Refresh Data**

---

## Final Dashboard Layout Example

```
┌─────────────────────────────────────────────────────────────┐
│ Last Updated: 2024-06-11 14:30:22                           │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ Health   │ │ Total    │ │ Blocked  │ │ At Risk  │      │
│  │ Score    │ │ Tickets  │ │          │ │          │      │
│  │   85     │ │   142    │ │    3     │ │    8     │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │       Velocity Trend (12 weeks)                  │      │
│  │                                                   │      │
│  │    📈 [Line chart showing story points/week]     │      │
│  │                                                   │      │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────────────┐       │
│  │ Tickets by Status │  │ 🚨 BLOCKED TICKETS       │       │
│  │                   │  │ PILOT-123: API latency   │       │
│  │  🥧 [Pie chart]   │  │ PILOT-456: DB migration  │       │
│  │                   │  │ PILOT-789: Auth issue    │       │
│  └──────────────────┘  └──────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## Advanced Features

### Add Email Alerts for Blocked Tickets

Add this to Apps Script:

```javascript
function checkAndAlertBlockedTickets() {
  const data = fetchAPIData('/api/program-health?project=PILOT');

  if (data && data.blocked_count > 0) {
    const emailBody = `
      🚨 Blocked Tickets Alert

      ${data.blocked_count} tickets are currently blocked:

      ${data.blocked_tickets.map(t => `• ${t.key}: ${t.summary}`).join('\n')}

      View dashboard: [Your Sheet URL]
    `;

    MailApp.sendEmail({
      to: 'your-email@company.com',
      subject: `🚨 ${data.blocked_count} Blocked Tickets`,
      body: emailBody
    });
  }
}

// Set up daily alert (run at 9 AM)
function setupDailyAlert() {
  ScriptApp.newTrigger('checkAndAlertBlockedTickets')
    .timeBased()
    .atHour(9)
    .everyDays(1)
    .create();
}
```

### Add Slack Integration

Post daily summary to Slack:

```javascript
function postToSlack() {
  const data = fetchAPIData('/api/program-health?project=PILOT');

  const slackWebhook = 'YOUR_SLACK_WEBHOOK_URL';

  const message = {
    text: `📊 Daily Status: ${data.project}`,
    blocks: [
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `*Health Score:* ${data.health_score}/100\n*Total Tickets:* ${data.total_tickets}\n*Blocked:* ${data.blocked_count}`
        }
      }
    ]
  };

  UrlFetchApp.fetch(slackWebhook, {
    method: 'POST',
    contentType: 'application/json',
    payload: JSON.stringify(message)
  });
}
```

---

## Sharing Your Dashboard

### Option 1: View-Only Link

1. Click "Share" (top right)
2. Click "Get link"
3. Change to: "Anyone with the link can **view**"
4. Copy link
5. Share with stakeholders

### Option 2: Embed in Confluence/Notion

1. Publish to web: File → Share → Publish to web
2. Choose: "Entire Document" or "Dashboard" tab
3. Copy embed code
4. Paste in Confluence/Notion

---

## Maintenance

### Weekly
- Review accuracy of data
- Check for API errors in Apps Script logs

### Monthly
- Archive old velocity data (keep last 12 weeks)
- Update Config if API URL changes

---

## Troubleshooting

### "Reference error" in formulas

- Check that tab names match exactly: "Raw Data", "Velocity", etc.
- Verify data exists in source tabs before referencing

### Data not refreshing

1. Check Apps Script execution logs: Extensions → Apps Script → Executions
2. Verify API URL in Config tab is correct
3. Test API manually: open `https://your-railway-url/health` in browser

### Charts showing wrong data

1. Click chart → "Edit chart"
2. Check data range matches your data
3. Ensure "Use row 1 as headers" is checked

---

## 🎉 You Now Have a Free, Real-Time Dashboard!

**What you built:**
- ✅ Live KPI cards (health, tickets, blocked, compliance)
- ✅ Velocity trend chart (12 weeks)
- ✅ Status breakdown pie chart
- ✅ Blocked tickets alert table
- ✅ Auto-refresh every hour
- ✅ One-click manual refresh

**Total cost: $0**

**Compare to:**
- Tableau: $70/user/month
- Looker: $50/user/month
- Power BI: $10/user/month

---

**Next:** Share this dashboard with your team and watch manual status reporting disappear!
