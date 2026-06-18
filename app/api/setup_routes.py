"""
Phase 2 Setup Routes
One-time API endpoints for creating JIRA custom fields and configuration
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List
import logging
import requests
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/setup", tags=["setup"])


# Phase 2 Epic Custom Fields Configuration
PHASE2_FIELDS = [
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
    """Create a custom field in JIRA via REST API"""

    url = f"{settings.JIRA_URL}/rest/api/3/field"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    auth = (settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)

    payload = {
        "name": field_config["name"],
        "description": field_config["description"],
        "type": field_config["type"],
        "searcherKey": field_config["searcherKey"]
    }

    response = requests.post(url, json=payload, headers=headers, auth=auth)

    if response.status_code in [200, 201]:
        result = response.json()
        logger.info(f"✅ Created field: {field_config['name']} (ID: {result['id']})")
        return {
            "success": True,
            "name": field_config["name"],
            "id": result["id"],
            "key": result.get("key", result["id"])
        }
    elif response.status_code == 400 and "already exists" in response.text.lower():
        logger.warning(f"⚠️  Field already exists: {field_config['name']}")
        return {
            "success": False,
            "name": field_config["name"],
            "error": "Field already exists",
            "skipped": True
        }
    else:
        logger.error(f"❌ Failed to create field {field_config['name']}: {response.status_code} - {response.text}")
        return {
            "success": False,
            "name": field_config["name"],
            "error": f"{response.status_code}: {response.text}"
        }


def add_field_options(field_id: str, field_name: str, options: List[str]) -> bool:
    """Add options to a select/multi-select field"""

    url = f"{settings.JIRA_URL}/rest/api/3/field/{field_id}/context/defaultValue"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    auth = (settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)

    # Note: JIRA Cloud requires creating a field context first, then adding options
    # This is simplified - you may need to use the UI for complex field configurations

    logger.info(f"ℹ️  Field options for {field_name} should be added via JIRA UI")
    return True


@router.post("/phase2-fields")
async def create_phase2_fields():
    """
    Create all Phase 2 Epic custom fields

    This endpoint creates 11 custom fields needed for Epic workflow & capacity planning.
    Run this once during Phase 2 setup.

    Returns:
        Dict with created field IDs and summary
    """

    logger.info("🚀 Starting Phase 2 field creation...")

    results = {
        "created": [],
        "skipped": [],
        "failed": [],
        "field_ids": {}
    }

    for field_config in PHASE2_FIELDS:
        result = create_custom_field(field_config)

        if result["success"]:
            results["created"].append(result["name"])
            results["field_ids"][result["name"]] = result["id"]
        elif result.get("skipped"):
            results["skipped"].append(result["name"])
        else:
            results["failed"].append({
                "name": result["name"],
                "error": result["error"]
            })

    # Summary
    summary = {
        "total_fields": len(PHASE2_FIELDS),
        "created_count": len(results["created"]),
        "skipped_count": len(results["skipped"]),
        "failed_count": len(results["failed"]),
        "success": len(results["failed"]) == 0
    }

    logger.info(f"✅ Phase 2 fields setup complete: {summary}")

    return {
        "summary": summary,
        "results": results,
        "next_steps": [
            "1. Note down the field IDs below",
            "2. Update config/jira-custom-fields.json with actual IDs",
            "3. For select/multi-select fields, add options via JIRA UI:",
            "   - Risk Flags: Add options (Vendor Dependency, Data Migration, etc.)",
            "   - Committed Quarter: Add options (Q1 2026, Q2 2026, etc.)",
            "   - Blocker Type: Add options (External Dependency, Reprioritized, etc.)",
            "4. Associate fields with Epic issue type screens",
            "5. Continue with Part 2: Create Epic Workflow"
        ],
        "field_ids_to_document": results["field_ids"]
    }


@router.get("/phase2-fields/check")
async def check_phase2_fields():
    """
    Check which Phase 2 fields already exist

    Returns:
        Status of each field (exists or not)
    """

    url = f"{settings.JIRA_URL}/rest/api/3/field"

    headers = {"Accept": "application/json"}
    auth = (settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)

    response = requests.get(url, headers=headers, auth=auth)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to fetch JIRA fields: {response.text}"
        )

    existing_fields = response.json()
    existing_names = {f["name"]: f["id"] for f in existing_fields if f.get("custom", False)}

    field_status = {}
    for field_config in PHASE2_FIELDS:
        field_name = field_config["name"]
        if field_name in existing_names:
            field_status[field_name] = {
                "exists": True,
                "id": existing_names[field_name]
            }
        else:
            field_status[field_name] = {
                "exists": False,
                "id": None
            }

    existing_count = sum(1 for s in field_status.values() if s["exists"])

    return {
        "total_required": len(PHASE2_FIELDS),
        "existing": existing_count,
        "missing": len(PHASE2_FIELDS) - existing_count,
        "ready_to_create": existing_count == 0,
        "all_exist": existing_count == len(PHASE2_FIELDS),
        "fields": field_status
    }


@router.delete("/phase2-fields/cleanup")
async def cleanup_phase2_fields():
    """
    ⚠️  DANGER: Delete all Phase 2 fields (for testing/rollback only)

    Use this only if you need to start over.
    """

    logger.warning("⚠️  Phase 2 field cleanup requested...")

    # Get existing fields
    url = f"{settings.JIRA_URL}/rest/api/3/field"
    headers = {"Accept": "application/json"}
    auth = (settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)

    response = requests.get(url, headers=headers, auth=auth)
    existing_fields = response.json()
    existing_names = {f["name"]: f["id"] for f in existing_fields if f.get("custom", False)}

    deleted = []
    failed = []

    for field_config in PHASE2_FIELDS:
        field_name = field_config["name"]

        if field_name in existing_names:
            field_id = existing_names[field_name]
            delete_url = f"{settings.JIRA_URL}/rest/api/3/field/{field_id}"

            delete_response = requests.delete(delete_url, headers=headers, auth=auth)

            if delete_response.status_code in [200, 204]:
                deleted.append(field_name)
                logger.info(f"🗑️  Deleted field: {field_name}")
            else:
                failed.append({
                    "name": field_name,
                    "error": f"{delete_response.status_code}: {delete_response.text}"
                })
                logger.error(f"❌ Failed to delete {field_name}: {delete_response.text}")

    return {
        "deleted_count": len(deleted),
        "failed_count": len(failed),
        "deleted": deleted,
        "failed": failed
    }
