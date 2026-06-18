// ========================================
// UPDATED CONFIGURATION FOR YOUR SHEET
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

  // Column mapping - UPDATED TO MATCH YOUR SHEET
  COLUMNS: {
    TIMESTAMP: 0,           // Column A: Timestamp
    PROJECT_NAME: 1,        // Column B: Project Name
    REQUEST_TYPE: 2,        // Column C: Request Type
    DEPARTMENT: 3,          // Column D: Department
    PROBLEM: 4,             // Column E: What Problem Are You Solving?
    IMPACT: 5,              // Column F: Business Impact
    DELIVERABLES: 6,        // Column G: What Will Be Delivered?
    TARGET_DATE: 7,         // Column H: Target Completion Date
    PRIORITY: 8,            // Column I: Priority Level
    BUDGET: 9,              // Column J: Budget Status
    EMAIL: 10,              // Column K: Email Address
    IT_RECOMMENDATION: 11,  // Column L: IT Recommendation ⭐ THIS IS WHERE YOU SELECT "Approve"
    ESTIMATED_EFFORT: 12,   // Column M: Estimated Effort
    TARGET_QUARTER: 13,     // Column N: Target Quarter
    DECISION_DATE: 14,      // Column O: Decision Date
    JIRA_EPIC_LINK: 15,     // Column P: JIRA Epic Link ⭐ EPIC URL APPEARS HERE
    IT_NOTES: 16            // Column Q: IT Notes
  }
};

/**
 * REPLACE THE CONFIG SECTION IN THE MAIN SCRIPT WITH THIS ONE
 *
 * Key differences from original:
 * - Removed REQUESTOR field (using EMAIL instead)
 * - EMAIL is at index 10 (Column K)
 * - IT_RECOMMENDATION is at index 11 (Column L)
 * - JIRA_EPIC_LINK is at index 15 (Column P)
 * - IT_NOTES is at index 16 (Column Q)
 */
