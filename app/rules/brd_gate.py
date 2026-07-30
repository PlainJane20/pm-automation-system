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


# Phase 3: Definition of Ready (DoR) field set for Stories.
# A Story may not move BRD_REVIEW -> READY_FOR_DEV (or READY_FOR_DEV -> IN_PROGRESS)
# until every field below is populated. Enforcement is "document-and-advise": on a
# violation we comment + label; the JIRA Automation rule performs the actual block.
DOR_REQUIRED_FIELDS = [
    "User Story",
    "Acceptance Criteria",
    "Technical Approach",
    "Story Points",
    "BRD Document Link",
    "BRD Approved Date",
    "BRD Reviewer",
]

DOR_BLOCKED_LABEL = "dor-gate-blocked"


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


# ---------------------------------------------------------------------------
# Phase 3: Story-level Definition of Ready (DoR) gate
# ---------------------------------------------------------------------------

async def enforce_dor_gate(issue_key: str, fields: Dict[str, Any]) -> bool:
    """
    Enforce the full Definition of Ready before a Story becomes dev-ready.

    Runs on transitions BRD_REVIEW -> READY_FOR_DEV and READY_FOR_DEV -> IN_PROGRESS.

    Checks every field in DOR_REQUIRED_FIELDS (User Story, Acceptance Criteria,
    Technical Approach, Story Points, BRD Document Link, BRD Approved Date,
    BRD Reviewer). Bugs / Support Requests skip the gate, matching enforce_brd_gate.

    Behavior is document-and-advise:
    - On violation: add a blocking comment listing each missing field, add the
      'dor-gate-blocked' label, return False. The JIRA Automation rule uses that
      label to block the transition.
    - On pass: remove the block signal via confirmation comment and return True.
    """

    logger.info(f"🔒 Enforcing DoR gate for {issue_key}")

    try:
        issue = jira_client.get_issue(issue_key)
        if not issue:
            logger.error(f"Issue {issue_key} not found")
            return False

        # Bugs / Support Requests skip requirements definition (same as BRD gate)
        request_type = jira_client.get_custom_field_value(issue, "Request Type")
        if request_type in ["Bug", "Support Request"]:
            logger.info(f"   ✅ Skipping DoR check for {request_type}")
            return True

        # Evaluate every required field
        missing = []
        for field_name in DOR_REQUIRED_FIELDS:
            value = jira_client.get_custom_field_value(issue, field_name)
            if _is_empty(value):
                missing.append(field_name)

        if missing:
            logger.warning(f"   ⛔ DoR gate violation for {issue_key}: {missing}")

            comment = f"""⛔ *Definition of Ready - Not Met*

This Story cannot become dev-ready until the requirements are complete.

*Missing / incomplete fields:*
{chr(10).join(f'• {name}' for name in missing)}

*Definition of Ready checklist:*
1. User Story written (As a... I want... so that...)
2. Acceptance Criteria defined and testable
3. Technical Approach documented
4. Story Points estimated
5. BRD Document Link populated
6. BRD Approved Date set
7. BRD Reviewer (Tech Lead) assigned

Complete the missing items, then retry the transition.

_This is an automated governance check (PMO Phase 3). Bypass requires TPM approval._
"""
            jira_client.add_comment(issue_key, comment)
            jira_client.add_label(issue_key, DOR_BLOCKED_LABEL)
            return False

        # DoR satisfied
        logger.info(f"   ✅ DoR gate passed for {issue_key}")
        jira_client.add_comment(
            issue_key,
            "✅ Definition of Ready satisfied. All requirements complete - "
            "Story is dev-ready and eligible for sprint planning."
        )
        return True

    except Exception as e:
        logger.error(f"Error enforcing DoR gate for {issue_key}: {e}")
        return False


async def check_dor_gate_status(issue_key: str) -> Dict[str, Any]:
    """
    Report the Definition of Ready status for a Story (for dashboards/reporting).

    Returns:
    {
        "compliant": bool,
        "missing": [field names not yet populated],
        "checklist": {field name: bool populated},
        "reason": optional str (e.g. bug skips gate)
    }
    """

    issue = jira_client.get_issue(issue_key)
    if not issue:
        return {"compliant": False, "error": "Issue not found"}

    request_type = jira_client.get_custom_field_value(issue, "Request Type")
    if request_type in ["Bug", "Support Request"]:
        return {"compliant": True, "reason": f"DoR not required for {request_type}"}

    checklist = {}
    missing = []
    for field_name in DOR_REQUIRED_FIELDS:
        populated = not _is_empty(jira_client.get_custom_field_value(issue, field_name))
        checklist[field_name] = populated
        if not populated:
            missing.append(field_name)

    return {
        "compliant": len(missing) == 0,
        "missing": missing,
        "checklist": checklist,
    }


def _is_empty(value: Any) -> bool:
    """True when a JIRA field value counts as unset for DoR purposes."""
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, tuple, dict)):
        return len(value) == 0
    return False
