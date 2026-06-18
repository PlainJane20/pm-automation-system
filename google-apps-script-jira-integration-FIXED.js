/**
 * Google Apps Script - JIRA Epic Auto-Creation
 *
 * This script automatically creates JIRA Epics when intake requests are approved.
 *
 * SETUP INSTRUCTIONS:
 * 1. Open your Google Sheet with intake responses
 * 2. Go to: Extensions → Apps Script
 * 3. Delete any default code
 * 4. Paste this entire script
 * 5. Update the CONFIG section below with your JIRA credentials
 * 6. Click Save
 * 7. Run "setup" function once (authorize permissions)
 * 8. Create installable trigger (Triggers → Add Trigger → onEditInstallable, On edit)
 */

// ========================================
// CONFIGURATION - UPDATE THESE VALUES
// ========================================

const CONFIG = {
  // Your JIRA instance URL (no trailing slash)
  JIRA_URL: 'https://nksaidev.atlassian.net',

  // Your JIRA email
  JIRA_EMAIL: 'nks.ai.dev@gmail.com',

  // Your JIRA API Token (from https://id.atlassian.com/manage/api-tokens)
  JIRA_API_TOKEN: 'ATATT3xFfGF0hKyso0v0zr361o7r1q5oFm440dPBISNZguiKgZ_sb8OXxazgVsIFSRaWMvZ8qaNoHfw0ruOGb9XQM1p5RL94Vm3owqngVxMxMfNEqJOqjshPMihd3ssdz3EbXmCEGTK6ufwNYWzq_RvfXNyFTTWqpbmRVJLwN7bpyhkRasESHgo=F4500CF8',

  // Your JIRA project key
  JIRA_PROJECT_KEY: 'PGMAUTO',

  // Column mapping (adjust if your columns are different)
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
    IT_RECOMMENDATION: 11,  // Column L
    ESTIMATED_EFFORT: 12,   // Column M
    TARGET_QUARTER: 13,     // Column N
    DECISION_DATE: 14,      // Column O
    JIRA_EPIC_LINK: 15,     // Column P
    IT_NOTES: 16            // Column Q
  }
};

// ========================================
// MAIN TRIGGER FUNCTION
// ========================================

/**
 * This function runs automatically when the sheet is edited via installable trigger
 * Checks if IT Recommendation was changed to "Approve"
 * If yes, creates Epic in JIRA
 */
function onEditInstallable(e) {
  try {
    const sheet = e.source.getActiveSheet();
    const range = e.range;
    const row = range.getRow();
    const col = range.getColumn();

    // Only process edits to the IT Recommendation column (after header row)
    if (row > 1 && col === CONFIG.COLUMNS.IT_RECOMMENDATION + 1) {
      const newValue = range.getValue();

      // If changed to "Approve", create Epic
      if (newValue === 'Approve') {
        createJiraEpicFromRow(sheet, row);
      }
    }
  } catch (error) {
    Logger.log('Error in onEditInstallable: ' + error.toString());
    SpreadsheetApp.getUi().alert('Error: ' + error.toString());
  }
}

// ========================================
// JIRA EPIC CREATION
// ========================================

/**
 * Creates a JIRA Epic from an approved intake row
 */
function createJiraEpicFromRow(sheet, row) {
  // Get all data from the row
  const rowData = sheet.getRange(row, 1, 1, Object.keys(CONFIG.COLUMNS).length).getValues()[0];

  // Check if Epic already exists for this row
  const existingEpicLink = rowData[CONFIG.COLUMNS.JIRA_EPIC_LINK];
  if (existingEpicLink && existingEpicLink.trim() !== '') {
    Logger.log('Epic already exists for row ' + row + ': ' + existingEpicLink);
    SpreadsheetApp.getUi().alert('Epic already created for this request:\n' + existingEpicLink);
    return;
  }

  // Extract data
  const projectName = rowData[CONFIG.COLUMNS.PROJECT_NAME];
  const requestType = rowData[CONFIG.COLUMNS.REQUEST_TYPE];
  const email = rowData[CONFIG.COLUMNS.EMAIL];
  const department = rowData[CONFIG.COLUMNS.DEPARTMENT];
  const problem = rowData[CONFIG.COLUMNS.PROBLEM];
  const impact = rowData[CONFIG.COLUMNS.IMPACT];
  const deliverables = rowData[CONFIG.COLUMNS.DELIVERABLES];
  const targetDate = rowData[CONFIG.COLUMNS.TARGET_DATE];
  const priority = rowData[CONFIG.COLUMNS.PRIORITY];
  const budget = rowData[CONFIG.COLUMNS.BUDGET];
  const estimatedEffort = rowData[CONFIG.COLUMNS.ESTIMATED_EFFORT];
  const targetQuarter = rowData[CONFIG.COLUMNS.TARGET_QUARTER];
  const itNotes = rowData[CONFIG.COLUMNS.IT_NOTES];
  const timestamp = rowData[CONFIG.COLUMNS.TIMESTAMP];

  // Format description for JIRA (using Atlassian Document Format)
  const description = formatEpicDescription({
    requestor: email,
    department,
    timestamp,
    problem,
    impact,
    deliverables,
    targetDate,
    priority,
    budget,
    estimatedEffort,
    targetQuarter,
    itNotes,
    sheetUrl: sheet.getParent().getUrl() + '#gid=' + sheet.getSheetId() + '&range=A' + row
  });

  // Create Epic payload
  const epicPayload = {
    fields: {
      project: {
        key: CONFIG.JIRA_PROJECT_KEY
      },
      summary: projectName,
      description: description,
      issuetype: {
        name: 'Epic'
      }
    }
  };

  // Call JIRA API to create Epic
  try {
    const epic = createJiraIssue(epicPayload);

    if (epic && epic.key) {
      const epicUrl = CONFIG.JIRA_URL + '/browse/' + epic.key;

      // Write Epic URL back to sheet
      sheet.getRange(row, CONFIG.COLUMNS.JIRA_EPIC_LINK + 1).setValue(epicUrl);

      // Write decision date
      sheet.getRange(row, CONFIG.COLUMNS.DECISION_DATE + 1).setValue(new Date());

      // Show success message
      SpreadsheetApp.getUi().alert(
        'Success! Epic created:\n\n' +
        'Epic Key: ' + epic.key + '\n' +
        'URL: ' + epicUrl
      );

      Logger.log('Successfully created Epic: ' + epic.key);
    }
  } catch (error) {
    Logger.log('Error creating Epic: ' + error.toString());
    SpreadsheetApp.getUi().alert('Failed to create Epic:\n' + error.toString());
  }
}

// ========================================
// JIRA API FUNCTIONS
// ========================================

/**
 * Creates a JIRA issue via REST API
 */
function createJiraIssue(payload) {
  const url = CONFIG.JIRA_URL + '/rest/api/3/issue';

  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: {
      'Authorization': 'Basic ' + Utilities.base64Encode(CONFIG.JIRA_EMAIL + ':' + CONFIG.JIRA_API_TOKEN)
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  const response = UrlFetchApp.fetch(url, options);
  const responseCode = response.getResponseCode();
  const responseBody = response.getContentText();

  if (responseCode === 201) {
    return JSON.parse(responseBody);
  } else {
    throw new Error('JIRA API Error (' + responseCode + '): ' + responseBody);
  }
}

// ========================================
// FORMATTING FUNCTIONS
// ========================================

/**
 * Formats the Epic description using Atlassian Document Format (ADF)
 */
function formatEpicDescription(data) {
  return {
    "type": "doc",
    "version": 1,
    "content": [
      {
        "type": "heading",
        "attrs": { "level": 3 },
        "content": [{ "type": "text", "text": "INTAKE REQUEST" }]
      },
      {
        "type": "paragraph",
        "content": [
          { "type": "text", "text": "Submitted by: ", "marks": [{ "type": "strong" }] },
          { "type": "text", "text": data.requestor || "Not provided" }
        ]
      },
      {
        "type": "paragraph",
        "content": [
          { "type": "text", "text": "Department: ", "marks": [{ "type": "strong" }] },
          { "type": "text", "text": data.department || "Not provided" }
        ]
      },
      {
        "type": "paragraph",
        "content": [
          { "type": "text", "text": "Submitted on: ", "marks": [{ "type": "strong" }] },
          { "type": "text", "text": formatDate(data.timestamp) }
        ]
      },
      {
        "type": "rule"
      },
      {
        "type": "heading",
        "attrs": { "level": 3 },
        "content": [{ "type": "text", "text": "Problem Statement" }]
      },
      {
        "type": "paragraph",
        "content": [{ "type": "text", "text": data.problem || "Not provided" }]
      },
      {
        "type": "heading",
        "attrs": { "level": 3 },
        "content": [{ "type": "text", "text": "Business Impact" }]
      },
      {
        "type": "paragraph",
        "content": [{ "type": "text", "text": data.impact || "Not provided" }]
      },
      {
        "type": "heading",
        "attrs": { "level": 3 },
        "content": [{ "type": "text", "text": "Expected Deliverables" }]
      },
      {
        "type": "paragraph",
        "content": [{ "type": "text", "text": data.deliverables || "Not provided" }]
      },
      {
        "type": "heading",
        "attrs": { "level": 3 },
        "content": [{ "type": "text", "text": "Target Completion" }]
      },
      {
        "type": "paragraph",
        "content": [{ "type": "text", "text": formatDate(data.targetDate) || "Not specified" }]
      },
      {
        "type": "heading",
        "attrs": { "level": 3 },
        "content": [{ "type": "text", "text": "Priority" }]
      },
      {
        "type": "paragraph",
        "content": [{ "type": "text", "text": data.priority || "Not specified" }]
      },
      {
        "type": "heading",
        "attrs": { "level": 3 },
        "content": [{ "type": "text", "text": "Budget Status" }]
      },
      {
        "type": "paragraph",
        "content": [{ "type": "text", "text": data.budget || "Not specified" }]
      },
      {
        "type": "rule"
      },
      {
        "type": "heading",
        "attrs": { "level": 3 },
        "content": [{ "type": "text", "text": "IT ASSESSMENT" }]
      },
      {
        "type": "paragraph",
        "content": [
          { "type": "text", "text": "Estimated Effort: ", "marks": [{ "type": "strong" }] },
          { "type": "text", "text": data.estimatedEffort || "TBD" }
        ]
      },
      {
        "type": "paragraph",
        "content": [
          { "type": "text", "text": "Target Quarter: ", "marks": [{ "type": "strong" }] },
          { "type": "text", "text": data.targetQuarter || "TBD" }
        ]
      },
      {
        "type": "paragraph",
        "content": [
          { "type": "text", "text": "IT Notes: ", "marks": [{ "type": "strong" }] },
          { "type": "text", "text": data.itNotes || "None" }
        ]
      },
      {
        "type": "rule"
      },
      {
        "type": "paragraph",
        "content": [
          {
            "type": "text",
            "text": "View Intake Form Submission",
            "marks": [
              {
                "type": "link",
                "attrs": { "href": data.sheetUrl }
              }
            ]
          }
        ]
      }
    ]
  };
}

/**
 * Formats a date object to readable string
 */
function formatDate(date) {
  if (!date) return '';
  if (typeof date === 'string') return date;

  try {
    return Utilities.formatDate(date, Session.getScriptTimeZone(), 'MMM dd, yyyy');
  } catch (e) {
    return date.toString();
  }
}

// ========================================
// SETUP & TESTING FUNCTIONS
// ========================================

/**
 * Run this once to set up the script
 * Grants necessary permissions
 */
function setup() {
  Logger.log('Setup started...');

  // Test JIRA connection
  try {
    const testUrl = CONFIG.JIRA_URL + '/rest/api/3/myself';
    const options = {
      method: 'get',
      headers: {
        'Authorization': 'Basic ' + Utilities.base64Encode(CONFIG.JIRA_EMAIL + ':' + CONFIG.JIRA_API_TOKEN)
      },
      muteHttpExceptions: true
    };

    const response = UrlFetchApp.fetch(testUrl, options);
    const responseCode = response.getResponseCode();

    if (responseCode === 200) {
      const user = JSON.parse(response.getContentText());
      Logger.log('✅ JIRA connection successful! Connected as: ' + user.displayName);
      SpreadsheetApp.getUi().alert('Setup successful!\n\nJIRA connection verified.\nConnected as: ' + user.displayName);
    } else {
      throw new Error('JIRA authentication failed: ' + response.getContentText());
    }
  } catch (error) {
    Logger.log('❌ Setup failed: ' + error.toString());
    SpreadsheetApp.getUi().alert('Setup failed:\n\n' + error.toString());
  }
}

/**
 * Test function - creates Epic from row 2
 * Use this to test before relying on automatic trigger
 */
function testCreateEpicFromRow2() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  createJiraEpicFromRow(sheet, 2);
}

/**
 * Manual trigger: Create Epics for ALL approved rows that don't have Epic links yet
 * Useful for batch processing
 */
function createEpicsForAllApproved() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const lastRow = sheet.getLastRow();

  let created = 0;
  let skipped = 0;

  // Start at row 2 (skip header)
  for (let row = 2; row <= lastRow; row++) {
    const recommendation = sheet.getRange(row, CONFIG.COLUMNS.IT_RECOMMENDATION + 1).getValue();
    const existingLink = sheet.getRange(row, CONFIG.COLUMNS.JIRA_EPIC_LINK + 1).getValue();

    // Only process Approved rows without existing Epic links
    if (recommendation === 'Approve' && (!existingLink || existingLink.trim() === '')) {
      try {
        createJiraEpicFromRow(sheet, row);
        created++;
        Utilities.sleep(1000); // Wait 1 second between API calls to avoid rate limiting
      } catch (error) {
        Logger.log('Error processing row ' + row + ': ' + error.toString());
        skipped++;
      }
    } else {
      skipped++;
    }
  }

  SpreadsheetApp.getUi().alert(
    'Batch processing complete!\n\n' +
    'Epics created: ' + created + '\n' +
    'Rows skipped: ' + skipped
  );
}
