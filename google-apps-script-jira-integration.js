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
 * 8. Test by changing a row's IT Recommendation to "Approve"
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
    TIMESTAMP: 0,           // Column A (0-indexed)
    PROJECT_NAME: 1,        // Column B
    REQUEST_TYPE: 2,        // Column C
    REQUESTOR: 3,           // Column D
    DEPARTMENT: 4,          // Column E
    PROBLEM: 5,             // Column F
    IMPACT: 6,              // Column G
    DELIVERABLES: 7,        // Column H
    TARGET_DATE: 8,         // Column I
    PRIORITY: 9,            // Column J
    BUDGET: 10,             // Column K
    IT_RECOMMENDATION: 11,  // Column L (where you select Approve/Reject)
    ESTIMATED_EFFORT: 12,   // Column M
    TARGET_QUARTER: 13,     // Column N
    IT_NOTES: 14,           // Column O
    DECISION_DATE: 15,      // Column P
    JIRA_EPIC_LINK: 16      // Column Q (script writes Epic URL here)
  }
};

// ========================================
// MAIN TRIGGER FUNCTION
// ========================================

/**
 * This function runs automatically when the sheet is edited
 * Checks if IT Recommendation was changed to "Approve"
 * If yes, creates Epic in JIRA
 */
function onEdit(e) {
  try {
    const sheet = e.source.getActiveSheet();
    const range = e.range;
    const row = range.getRow();
    const col = range.getColumn();

    // Only process edits to the IT Recommendation column (after header row)
    if (row > 1 && col === CONFIG.COLUMNS.IT_RECOMMENDATION + 1) {
      const newValue = e.value;

      // If changed to "Approve", create Epic
      if (newValue === 'Approve') {
        createJiraEpicFromRow(sheet, row);
      }
    }
  } catch (error) {
    Logger.log('Error in onEdit: ' + error.toString());
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
  const requestor = rowData[CONFIG.COLUMNS.REQUESTOR];
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

  // Format description for JIRA (using JIRA markdown)
  const description = formatEpicDescription({
    requestor,
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
      // Note: Epic Name field may vary by JIRA configuration
      // If you get an error about Epic Name, uncomment and adjust:
      // 'customfield_10011': projectName  // Check your JIRA for correct Epic Name field ID
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
 * Formats the Epic description with all intake data
 */
function formatEpicDescription(data) {
  return `*INTAKE REQUEST*

*Submitted by:* ${data.requestor}
*Department:* ${data.department}
*Submitted on:* ${formatDate(data.timestamp)}

---

h3. Problem Statement
${data.problem || 'Not provided'}

h3. Business Impact
${data.impact || 'Not provided'}

h3. Expected Deliverables
${data.deliverables || 'Not provided'}

h3. Target Completion
${formatDate(data.targetDate) || 'Not specified'}

h3. Priority
${data.priority || 'Not specified'}

h3. Budget Status
${data.budget || 'Not specified'}

---

*IT ASSESSMENT*

*Estimated Effort:* ${data.estimatedEffort || 'TBD'}
*Target Quarter:* ${data.targetQuarter || 'TBD'}
*IT Notes:* ${data.itNotes || 'None'}

---

[View Intake Form Submission|${data.sheetUrl}]
`;
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

// ========================================
// INSTALLATION NOTES
// ========================================

/**
 * HOW TO INSTALL:
 *
 * 1. Open your intake Google Sheet
 * 2. Go to: Extensions → Apps Script
 * 3. Delete any default code
 * 4. Paste this entire script
 * 5. Update CONFIG section with your JIRA credentials
 * 6. Save (Ctrl+S or Cmd+S)
 * 7. Run "setup" function:
 *    - Click dropdown next to "Debug" button
 *    - Select "setup"
 *    - Click "Run"
 *    - Authorize permissions when prompted
 * 8. Test it:
 *    - In your sheet, change a row's IT Recommendation to "Approve"
 *    - Epic should auto-create and link appear in last column
 *
 * TROUBLESHOOTING:
 *
 * - If you get "Epic Name" field error:
 *   Go to JIRA → Settings → Issues → Custom fields
 *   Find "Epic Name" field ID (e.g., customfield_10011)
 *   Uncomment and update the epicPayload section in createJiraEpicFromRow()
 *
 * - If columns don't match:
 *   Update the COLUMNS mapping in CONFIG
 *
 * - To see logs:
 *   View → Logs (or Ctrl+Enter / Cmd+Enter)
 *
 * - To batch process all approved rows:
 *   Run the "createEpicsForAllApproved" function
 */
