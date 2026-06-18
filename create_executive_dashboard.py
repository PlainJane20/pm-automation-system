#!/usr/bin/env python3
"""
Create Executive Dashboard for PMO Automation System
Creates a JIRA dashboard with gadgets showing Epic metrics

Usage:
    python3 create_executive_dashboard.py
"""

import requests
import json
from typing import Dict, List

# JIRA Configuration
JIRA_URL = "https://nksaidev.atlassian.net"
JIRA_EMAIL = "nks.ai.dev@gmail.com"
JIRA_API_TOKEN = "***JIRA_TOKEN_REMOVED***"

print("=" * 70)
print("📊 Creating Executive PMO Dashboard")
print("=" * 70)
print()

# ============================================================================
# Step 1: Create Dashboard
# ============================================================================

print("Step 1: Creating Dashboard")
print("-" * 70)

dashboard_payload = {
    "name": "PMO Executive Dashboard",
    "description": "Real-time Epic metrics, roadmap status, and capacity planning",
    "sharePermissions": [
        {
            "type": "authenticated"  # Share with all logged-in users instead of public
        }
    ]
}

url = f"{JIRA_URL}/rest/api/3/dashboard"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}
auth = (JIRA_EMAIL, JIRA_API_TOKEN)

response = requests.post(url, json=dashboard_payload, headers=headers, auth=auth)

if response.status_code in [200, 201]:
    dashboard = response.json()
    dashboard_id = dashboard['id']
    print(f"✅ Dashboard created successfully!")
    print(f"   Dashboard ID: {dashboard_id}")
    print(f"   Dashboard Name: {dashboard['name']}")
    print(f"   URL: {JIRA_URL}/jira/dashboards/{dashboard_id}")
    print()
else:
    print(f"❌ Failed to create dashboard: {response.status_code}")
    print(f"   Error: {response.text}")
    print()
    exit(1)

# ============================================================================
# Step 2: Create Filter for Epic Roadmap
# ============================================================================

print("Step 2: Creating Filter for Dashboard")
print("-" * 70)

filter_payload = {
    "name": "PMO Dashboard - All Epics",
    "description": "All Epics for PMO dashboard visualization",
    "jql": "project = PGMAUTO AND issuetype = Epic ORDER BY priority DESC, \"Committed Quarter\" ASC",
    "sharePermissions": [
        {
            "type": "authenticated"  # Share with all logged-in users
        }
    ]
}

url = f"{JIRA_URL}/rest/api/3/filter"
response = requests.post(url, json=filter_payload, headers=headers, auth=auth)

if response.status_code in [200, 201]:
    filter_data = response.json()
    filter_id = filter_data['id']
    print(f"✅ Filter created successfully!")
    print(f"   Filter ID: {filter_id}")
    print(f"   Filter Name: {filter_data['name']}")
    print()
else:
    print(f"❌ Failed to create filter: {response.status_code}")
    print(f"   Error: {response.text}")
    print()
    # Continue anyway - we can use inline JQL in gadgets
    filter_id = None

# ============================================================================
# Step 3: Add Gadgets to Dashboard
# ============================================================================

print("Step 3: Adding Gadgets to Dashboard")
print("-" * 70)

# Note: JIRA Cloud's gadget API is limited
# Most gadgets must be added via UI
# We can document the recommended gadgets here

RECOMMENDED_GADGETS = [
    {
        "name": "Pie Chart - Epic Status Distribution",
        "type": "pie-chart",
        "position": {"row": 0, "column": 0},
        "config": {
            "filter": filter_id,
            "statType": "statuses"
        }
    },
    {
        "name": "Two Dimensional Filter Statistics",
        "type": "stats-2d",
        "position": {"row": 0, "column": 1},
        "config": {
            "filter": filter_id,
            "xAxis": "Committed Quarter",
            "yAxis": "Priority"
        }
    },
    {
        "name": "Filter Results - Roadmap Epics",
        "type": "filter-results",
        "position": {"row": 1, "column": 0},
        "config": {
            "filter": filter_id,
            "columns": ["summary", "status", "priority", "Committed Quarter", "Business Value Score"]
        }
    },
    {
        "name": "Activity Stream",
        "type": "activity-stream",
        "position": {"row": 2, "column": 0},
        "config": {
            "filter": filter_id
        }
    }
]

print("⚠️  JIRA Cloud Gadget API Limitation:")
print("   Dashboard gadgets must be added via UI")
print()
print("✅ Dashboard created, now add these gadgets manually:")
print()

for i, gadget in enumerate(RECOMMENDED_GADGETS, 1):
    print(f"{i}. {gadget['name']}")
    print(f"   Type: {gadget['type']}")
    print(f"   Position: Row {gadget['position']['row']}, Column {gadget['position']['column']}")
    if filter_id:
        print(f"   Filter: PMO Dashboard - All Epics (ID: {filter_id})")
    print()

# ============================================================================
# Step 4: Summary & Instructions
# ============================================================================

print("=" * 70)
print("📋 Dashboard Creation Summary")
print("=" * 70)
print()
print(f"✅ Dashboard Created: {JIRA_URL}/jira/dashboards/{dashboard_id}")
if filter_id:
    print(f"✅ Filter Created: ID {filter_id}")
print()
print("=" * 70)
print("📖 Next Steps: Add Gadgets via UI")
print("=" * 70)
print()
print(f"1. Go to: {JIRA_URL}/jira/dashboards/{dashboard_id}")
print()
print("2. Click: 'Add gadget' (top right)")
print()
print("3. Add these gadgets:")
print()
print("   a) Pie Chart")
print("      • Filter: PMO Dashboard - All Epics")
print("      • Stat Type: Status")
print("      • Shows: Epic distribution by status")
print()
print("   b) Two Dimensional Filter Statistics")
print("      • Filter: PMO Dashboard - All Epics")
print("      • X-axis: Committed Quarter")
print("      • Y-axis: Priority")
print("      • Shows: Epics by quarter and priority")
print()
print("   c) Filter Results")
print("      • Filter: PMO Dashboard - All Epics")
print("      • Columns: Summary, Status, Priority, Committed Quarter, Business Value")
print("      • Shows: Detailed Epic list")
print()
print("   d) Activity Stream")
print("      • Filter: PMO Dashboard - All Epics")
print("      • Shows: Recent Epic activity")
print()
print("=" * 70)
print("🎉 Dashboard Infrastructure Complete!")
print("=" * 70)
print()
print("The dashboard framework is ready.")
print("Adding gadgets via UI takes ~5 minutes.")
print()
print("=" * 70)
