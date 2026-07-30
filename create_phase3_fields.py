#!/usr/bin/env python3
"""
Phase 3 Setup Script: Create JIRA Story-Level BRD / Definition-of-Ready Fields

Creates the custom fields that back the Story DoR gate. Idempotent: fields that
already exist (e.g. Story Points, BRD Document Link, BRD Approved Date from earlier
phases) are detected and skipped.

Credentials are read from .env via app.config.get_settings() -- they are NEVER
hardcoded in this file. Populate .env first (JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN).

Usage:
    python create_phase3_fields.py            # create missing fields
    python create_phase3_fields.py --check    # report status only, create nothing
"""

import sys
import requests

from app.config import get_settings

settings = get_settings()

# Story-level fields required by the Definition of Ready gate.
# Fields marked existing_ok are commonly already present from Phase 1 / JIRA agile;
# the script checks first and skips them either way, but this documents intent.
FIELDS = [
    {
        "name": "User Story",
        "description": "As a [role], I want [feature], so that [benefit]",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:textarea",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
    },
    {
        "name": "Acceptance Criteria",
        "description": "Testable, bullet-listed conditions that define done",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:textarea",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
    },
    {
        "name": "Technical Approach",
        "description": "High-level implementation plan agreed with the Tech Lead",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:textarea",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
    },
    {
        "name": "BRD Reviewer",
        "description": "Tech Lead who reviewed and signed off the requirements",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:userpicker",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:userpickergroupsearcher",
    },
    {
        "name": "Story Points",
        "description": "Effort estimate in story points",
        "type": "com.atlassian.jira.plugin.system.customfieldtypes:float",
        "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:numberrange",
        "existing_ok": True,
    },
]

# Fields intentionally NOT recreated here (already created in Phase 1).
REFERENCE_ONLY = ["BRD Document Link", "BRD Approved Date"]


def _auth():
    return (settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)


def get_existing_custom_fields():
    """Return {field_name: field_id} for all existing custom fields."""
    url = f"{settings.JIRA_URL}/rest/api/3/field"
    response = requests.get(url, headers={"Accept": "application/json"}, auth=_auth())
    response.raise_for_status()
    return {f["name"]: f["id"] for f in response.json() if f.get("custom", False)}


def create_custom_field(field_config):
    """Create a single custom field in JIRA (idempotent via 'already exists')."""
    url = f"{settings.JIRA_URL}/rest/api/3/field"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    payload = {
        "name": field_config["name"],
        "description": field_config["description"],
        "type": field_config["type"],
        "searcherKey": field_config["searcherKey"],
    }

    response = requests.post(url, json=payload, headers=headers, auth=_auth())

    if response.status_code in (200, 201):
        result = response.json()
        return {"success": True, "name": field_config["name"], "id": result["id"]}
    elif response.status_code == 400 and "already exists" in response.text.lower():
        return {"success": False, "name": field_config["name"], "skipped": True,
                "reason": "Field already exists"}
    else:
        return {"success": False, "name": field_config["name"],
                "error": f"{response.status_code}: {response.text[:200]}"}


def main(check_only=False):
    print("=" * 70)
    mode = "CHECK (no changes)" if check_only else "CREATE"
    print(f"🚀 Phase 3 Setup: Story DoR Fields  [{mode}]")
    print("=" * 70)
    print(f"📍 JIRA Instance: {settings.JIRA_URL}")
    print(f"👤 User: {settings.JIRA_EMAIL}")
    print(f"📋 Fields to ensure: {len(FIELDS)}")
    print()

    try:
        existing = get_existing_custom_fields()
    except Exception as e:
        print(f"❌ Could not reach JIRA (check .env credentials): {e}")
        return 1

    results = {"created": [], "skipped": [], "failed": [], "field_ids": {}}

    for i, field_config in enumerate(FIELDS, 1):
        name = field_config["name"]
        print(f"[{i}/{len(FIELDS)}] {name}...", end=" ")

        if name in existing:
            print(f"⚠️  Already exists (ID: {existing[name]})")
            results["skipped"].append(name)
            results["field_ids"][name] = existing[name]
            continue

        if check_only:
            print("➕ Would create (missing)")
            continue

        result = create_custom_field(field_config)
        if result["success"]:
            print(f"✅ Created (ID: {result['id']})")
            results["created"].append(name)
            results["field_ids"][name] = result["id"]
        elif result.get("skipped"):
            print(f"⚠️  {result['reason']}")
            results["skipped"].append(name)
        else:
            print(f"❌ Failed: {result.get('error')}")
            results["failed"].append(name)

    print()
    print("=" * 70)
    print("📊 Summary")
    print("=" * 70)
    print(f"✅ Created: {len(results['created'])}")
    print(f"⚠️  Skipped (already exist): {len(results['skipped'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    print()
    print(f"ℹ️  Reference-only (from Phase 1, not touched): {', '.join(REFERENCE_ONLY)}")
    print()

    if results["field_ids"]:
        print("=" * 70)
        print("📝 Field IDs (copy into config/jira-story-fields.json & workflow)")
        print("=" * 70)
        for name, field_id in results["field_ids"].items():
            print(f"{name}: {field_id}")
        print()

    print("=" * 70)
    print("🎯 Next Steps")
    print("=" * 70)
    print("1. Copy the field IDs above into config/jira-story-fields.json")
    print("2. Associate fields with Story Create/Edit/View screens (JIRA UI)")
    print("3. Create the Story workflow (config/jira-story-workflow.yaml)")
    print("4. Create Story automation rules (config/jira-story-automation-rules.yaml)")
    print("5. Deploy the updated Railway middleware (DoR gate)")
    print()
    print("🎉 Phase 3 Field Setup Complete!")
    print("=" * 70)
    return 1 if results["failed"] else 0


if __name__ == "__main__":
    check = "--check" in sys.argv
    try:
        sys.exit(main(check_only=check))
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
