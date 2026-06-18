#!/usr/bin/env python3
"""
Phase 2 Setup Script: Create JIRA Custom Fields
Run this once to automatically create all 11 Epic custom fields

Usage:
    python create_phase2_fields.py
"""

import requests
import json
from typing import Dict, List

# JIRA Configuration (from .env)
JIRA_URL = "https://nksaidev.atlassian.net"
JIRA_EMAIL = "nks.ai.dev@gmail.com"
JIRA_API_TOKEN = "ATATT3xFfGF0hKyso0v0zr361o7r1q5oFm440dPBISNZguiKgZ_sb8OXxazgVsIFSRaWMvZ8qaNoHfw0ruOGb9XQM1p5RL94Vm3owqngVxMxMfNEqJOqjshPMihd3ssdz3EbXmCEGTK6ufwNYWzq_RvfXNyFTTWqpbmRVJLwN7bpyhkRasESHgo=F4500CF8"

# Phase 2 Fields Configuration
FIELDS = [
    {
        "name": "Business Value Score",
        "description": "Business impact rating (1-10 scale)",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:float",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:numberrange",
    },
    {
        "name": "Technical Complexity Score",
        "description": "Technical difficulty rating (1-10 scale)",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:float",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:numberrange",
    },
    {
        "name": "Risk Flags",
        "description": "Epic-level risk categories",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:multiselectsearcher",
    },
    {
        "name": "Committed Quarter",
        "description": "Target delivery quarter",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:select",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:multiselectsearcher",
    },
    {
        "name": "Team Capacity Allocation (%)",
        "description": "Percentage of team capacity needed for this Epic",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:float",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:numberrange",
    },
    {
        "name": "Rejection Reason",
        "description": "Reason why Epic was rejected",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:textarea",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
    },
    {
        "name": "Alternative Approach",
        "description": "Suggested alternative to rejected request",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:textarea",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
    },
    {
        "name": "Hold Reason",
        "description": "Reason why Epic is on hold",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:textarea",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
    },
    {
        "name": "Blocker Type",
        "description": "Category of blocker",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:select",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:multiselectsearcher",
    },
    {
        "name": "Expected Resume Date",
        "description": "When Epic is expected to resume",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:datepicker",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:daterange",
    },
    {
        "name": "Completion Date",
        "description": "Date when Epic was completed",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:datepicker",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:daterange",
    },
]


def create_custom_field(field_config: Dict) -> Dict:
    """Create a single custom field in JIRA"""

    url = f"{JIRA_URL}/rest/api/3/field"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    auth = (JIRA_EMAIL, JIRA_API_TOKEN)

    payload = {
        "name": field_config["name"],
        "description": field_config["description"],
        "type": field_config["type"],
        "searcherKey": field_config["searcherKey"]
    }

    response = requests.post(url, json=payload, headers=headers, auth=auth)

    if response.status_code in [200, 201]:
        result = response.json()
        return {
            "success": True,
            "name": field_config["name"],
            "id": result["id"],
            "key": result.get("key", result["id"])
        }
    elif response.status_code == 400 and "already exists" in response.text.lower():
        return {
            "success": False,
            "name": field_config["name"],
            "skipped": True,
            "reason": "Field already exists"
        }
    else:
        return {
            "success": False,
            "name": field_config["name"],
            "error": f"{response.status_code}: {response.text[:200]}"
        }


def main():
    """Main execution"""

    print("=" * 70)
    print("🚀 Phase 2 Setup: Creating JIRA Custom Fields")
    print("=" * 70)
    print()

    print(f"📍 JIRA Instance: {JIRA_URL}")
    print(f"👤 User: {JIRA_EMAIL}")
    print(f"📋 Fields to create: {len(FIELDS)}")
    print()

    results = {
        "created": [],
        "skipped": [],
        "failed": [],
        "field_ids": {}
    }

    for i, field_config in enumerate(FIELDS, 1):
        print(f"[{i}/{len(FIELDS)}] Creating: {field_config['name']}...", end=" ")

        result = create_custom_field(field_config)

        if result["success"]:
            print(f"✅ Created (ID: {result['id']})")
            results["created"].append(result["name"])
            results["field_ids"][result["name"]] = result["id"]
        elif result.get("skipped"):
            print(f"⚠️  {result['reason']}")
            results["skipped"].append(result["name"])
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            results["failed"].append(result["name"])

    print()
    print("=" * 70)
    print("📊 Summary")
    print("=" * 70)
    print(f"✅ Created: {len(results['created'])}")
    print(f"⚠️  Skipped: {len(results['skipped'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    print()

    if results["field_ids"]:
        print("=" * 70)
        print("📝 Field IDs (Document These!)")
        print("=" * 70)
        for name, field_id in results["field_ids"].items():
            print(f"{name}: {field_id}")
        print()

    if results["failed"]:
        print("=" * 70)
        print("❌ Failed Fields")
        print("=" * 70)
        for name in results["failed"]:
            print(f"- {name}")
        print()

    print("=" * 70)
    print("🎯 Next Steps")
    print("=" * 70)
    print("1. ✅ Copy the field IDs above")
    print("2. ✅ Update config/jira-custom-fields.json with actual IDs")
    print("3. ✅ Go to JIRA UI and add options to select fields:")
    print("   - Risk Flags → Add options (Vendor Dependency, etc.)")
    print("   - Committed Quarter → Add options (Q1 2026, Q2 2026, etc.)")
    print("   - Blocker Type → Add options (External Dependency, etc.)")
    print("4. ✅ Associate fields with Epic screens (Create/Edit/View)")
    print("5. ✅ Continue with Part 2: Create Epic Workflow")
    print()
    print("🎉 Phase 2 Field Creation Complete!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
