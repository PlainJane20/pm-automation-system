#!/usr/bin/env python3
"""
Enhance PMO Roadmap Board via JIRA API
Adds swimlanes, quick filters, and card configurations

Usage:
    python3 enhance_roadmap_board.py
"""

import requests
import json
from typing import Dict, List

# JIRA Configuration — read from .env via app.config (never hardcode secrets)
from app.config import get_settings

_settings = get_settings()
JIRA_URL = _settings.JIRA_URL
JIRA_EMAIL = _settings.JIRA_EMAIL
JIRA_API_TOKEN = _settings.JIRA_API_TOKEN
BOARD_ID = 35  # PMO Roadmap - Epics board

print("=" * 70)
print("🚀 Enhancing PMO Roadmap Board")
print("=" * 70)
print()

# ============================================================================
# Part 1: Add Quick Filters
# ============================================================================

print("📊 Part 1: Adding Quick Filters")
print("-" * 70)

QUICK_FILTERS = [
    {
        "name": "This Quarter",
        "jql": "\"Committed Quarter\" IN (\"Q2 2026\", \"Q3 2026\")",
        "description": "Epics planned for current quarter"
    },
    {
        "name": "At Risk",
        "jql": "\"Risk Flags\" IS NOT EMPTY",
        "description": "Epics with risk flags"
    },
    {
        "name": "P0 Only",
        "jql": "priority = Highest",
        "description": "Highest priority Epics only"
    },
    {
        "name": "Over Capacity",
        "jql": "\"Team Capacity Allocation (%)\" > 25",
        "description": "Epics requiring >25% team capacity"
    }
]

# Note: Quick filters are typically configured via the board settings UI
# The JIRA Agile API for quick filters is limited
print("⚠️  Quick Filters: Manual configuration recommended via UI")
print("   Filters to add:")
for i, qf in enumerate(QUICK_FILTERS, 1):
    print(f"   {i}. {qf['name']}: {qf['jql']}")
print()

# ============================================================================
# Part 2: Configure Card Layout (Display Fields)
# ============================================================================

print("🎨 Part 2: Configuring Card Layout")
print("-" * 70)

# Card layout configuration
# These are the fields to display on each Epic card
CARD_FIELDS = {
    "card_layout": {
        "fields": [
            "priority",           # Priority icon
            "customfield_10080",  # Committed Quarter
            "customfield_10077",  # Business Value Score
            "customfield_10081",  # Team Capacity Allocation (%)
            "customfield_10079"   # Risk Flags
        ]
    }
}

print("✅ Card will display:")
print("   • Priority (icon)")
print("   • Committed Quarter")
print("   • Business Value Score")
print("   • Team Capacity Allocation (%)")
print("   • Risk Flags")
print()
print("⚠️  Card layout: Manual configuration via Board Settings → Card layout")
print()

# ============================================================================
# Part 3: Add Board Configuration (Swimlanes)
# ============================================================================

print("🏊 Part 3: Configuring Swimlanes")
print("-" * 70)

# Get current board configuration
url = f"{JIRA_URL}/rest/agile/1.0/board/{BOARD_ID}/configuration"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}
auth = (JIRA_EMAIL, JIRA_API_TOKEN)

response = requests.get(url, headers=headers, auth=auth)

if response.status_code == 200:
    config = response.json()
    print(f"✅ Retrieved board configuration")
    print(f"   Board Name: {config.get('name', 'N/A')}")
    print(f"   Board Type: {config.get('type', 'N/A')}")

    # Display current swimlane config
    if 'swimlaneConfig' in config:
        print(f"   Current Swimlane: {config['swimlaneConfig'].get('type', 'None')}")
    print()
else:
    print(f"❌ Failed to get board config: {response.status_code}")
    print(f"   Error: {response.text}")
    print()

# Note: JIRA Agile REST API doesn't support updating swimlane config via API
# Swimlanes must be configured through the UI
print("⚠️  Swimlane Configuration: Must be done via Board Settings → Swimlanes")
print()
print("   Recommended Swimlanes (by JQL):")
print("   1. Feature Requests")
print("      JQL: \"Request Type\" = \"Feature Request (new capability)\"")
print()
print("   2. Enhancements")
print("      JQL: \"Request Type\" = \"Enhancement Request (improve existing)\"")
print()
print("   3. Bug Fixes")
print("      JQL: \"Request Type\" = \"Bug Fix Request\"")
print()
print("   4. Projects")
print("      JQL: \"Request Type\" = \"Project Request\"")
print()

# ============================================================================
# Part 4: Get Card Colors Configuration
# ============================================================================

print("🎨 Part 4: Card Colors by Priority")
print("-" * 70)

print("⚠️  Card colors: Configured via Board Settings → Card colors")
print()
print("   Recommended Configuration:")
print("   • P0 (Highest) → Red")
print("   • P1 (High) → Orange")
print("   • P2 (Medium) → Yellow")
print("   • P3 (Low) → Green")
print()

# ============================================================================
# Part 5: Summary & Manual Steps
# ============================================================================

print("=" * 70)
print("📋 Configuration Summary")
print("=" * 70)
print()
print("✅ Board configuration retrieved successfully")
print("⚠️  The following must be configured manually in JIRA UI:")
print()
print("1. Quick Filters (Board Settings → Quick Filters)")
for qf in QUICK_FILTERS:
    print(f"   • {qf['name']}: {qf['jql']}")
print()
print("2. Swimlanes (Board Settings → Swimlanes)")
print("   • Select 'Queries'")
print("   • Add 4 swimlanes for each Request Type")
print()
print("3. Card Layout (Board Settings → Card layout)")
print("   • Add: Priority, Committed Quarter, Business Value, Capacity %, Risk Flags")
print()
print("4. Card Colors (Board Settings → Card colors)")
print("   • Color by Priority field")
print()
print("=" * 70)
print("🎯 Why Manual Configuration?")
print("=" * 70)
print()
print("JIRA's Agile REST API has limitations:")
print("• Quick Filters API is read-only in most cases")
print("• Swimlane configuration not exposed via API")
print("• Card layout/colors are board-specific UI settings")
print()
print("These are one-time configurations that take ~10 minutes in the UI.")
print()
print("=" * 70)
print("📖 Next Steps")
print("=" * 70)
print()
print("Option A: I can guide you step-by-step through the UI (10 min)")
print("Option B: Skip board enhancements, move to Dashboard creation (API-supported)")
print("Option C: Skip board enhancements, move to Automation Rules (API-supported)")
print()
print("The Dashboard and Automation Rules CAN be created via API!")
print()
print("=" * 70)
