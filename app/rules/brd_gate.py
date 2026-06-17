"""
BRD Gate Enforcement Rule
CRITICAL: Prevents development from starting without approved BRD
"""

import logging
from typing import Dict, Any
from datetime import datetime

from app.jira_client import jira_client
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def enforce_brd_gate(issue_key: str, fields: Dict[str, Any]) -> bool:
    """
    Enforce BRD requirement before development starts

    Checks:
    1. BRD Document Link is populated
    2. BRD Approved Date is set
    3. Request Type is Feature/Enhancement (Bugs skip this gate)

    If checks fail:
    - Block transition (done via JIRA Automation UI)
    - Add comment explaining the block
    - Notify assignee and BRD owner
    """

    logger.info(f"🔒 Enforcing BRD gate for {issue_key}")

    try:
        # Fetch fresh issue data
        issue = jira_client.get_issue(issue_key)
        if not issue:
            logger.error(f"Issue {issue_key} not found")
            return False

        # Check if this is a Bug (Bugs skip BRD requirement)
        request_type = jira_client.get_custom_field_value(issue, "Request Type")
        if request_type in ["Bug", "Support Request"]:
            logger.info(f"   ✅ Skipping BRD check for {request_type}")
            return True

        # Get BRD fields
        brd_link = jira_client.get_custom_field_value(issue, "BRD Document Link")
        brd_approved_date = jira_client.get_custom_field_value(issue, "BRD Approved Date")

        # Check BRD compliance
        brd_missing = not brd_link
        approval_missing = not brd_approved_date

        if brd_missing or approval_missing:
            # BRD gate violated
            logger.warning(f"   ⛔ BRD gate violation for {issue_key}")

            violation_reasons = []
            if brd_missing:
                violation_reasons.append("BRD Document Link is missing")
            if approval_missing:
                violation_reasons.append("BRD Approved Date is not set")

            # Add blocking comment
            comment = f"""⛔ *BRD Gate Enforcement*

Development cannot proceed without an approved Business Requirements Document (BRD).

*Issues found:*
{chr(10).join(f'• {reason}' for reason in violation_reasons)}

*Required actions:*
1. Create a BRD document (use template: [BRD Template|{settings.JIRA_URL}/wiki/spaces/PM/pages/123456])
2. Get stakeholder approval
3. Update the 'BRD Document Link' field with the approved document URL
4. Set the 'BRD Approved Date' field

*Questions?* Contact your Product Manager or TPM.

_This is an automated governance check. Bypass requires VP approval._
"""

            jira_client.add_comment(issue_key, comment)

            # Add label for tracking
            jira_client.add_label(issue_key, "brd-gate-blocked")

            # Note: The actual transition block happens in JIRA Automation rule
            # This function logs and documents the violation

            return False

        else:
            # BRD gate passed
            logger.info(f"   ✅ BRD gate passed for {issue_key}")

            # Add confirmation comment
            jira_client.add_comment(
                issue_key,
                f"✅ BRD gate check passed. BRD approved on {brd_approved_date}. Development can proceed."
            )

            # Remove blocking label if it exists
            # jira_client.remove_label(issue_key, "brd-gate-blocked")

            return True

    except Exception as e:
        logger.error(f"Error enforcing BRD gate for {issue_key}: {e}")
        return False


async def check_brd_gate_status(issue_key: str) -> Dict[str, Any]:
    """
    Check BRD gate status for a ticket (for dashboard/reporting)

    Returns:
    {
        "compliant": bool,
        "brd_link": str or None,
        "approved_date": str or None,
        "blockers": list of str
    }
    """

    issue = jira_client.get_issue(issue_key)
    if not issue:
        return {"compliant": False, "error": "Issue not found"}

    request_type = jira_client.get_custom_field_value(issue, "Request Type")
    if request_type in ["Bug", "Support Request"]:
        return {"compliant": True, "reason": "BRD not required for bugs"}

    brd_link = jira_client.get_custom_field_value(issue, "BRD Document Link")
    brd_approved_date = jira_client.get_custom_field_value(issue, "BRD Approved Date")

    blockers = []
    if not brd_link:
        blockers.append("BRD Document Link missing")
    if not brd_approved_date:
        blockers.append("BRD Approved Date not set")

    return {
        "compliant": len(blockers) == 0,
        "brd_link": brd_link,
        "approved_date": str(brd_approved_date) if brd_approved_date else None,
        "blockers": blockers
    }
