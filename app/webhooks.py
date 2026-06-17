"""
JIRA Webhook Handlers
Receives events from JIRA and triggers automation rules
"""

from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from typing import Dict, Any
import logging

from app.jira_client import jira_client
from app.rules.brd_gate import enforce_brd_gate
from app.rules.auto_classify import auto_classify_ticket
from app.rules.duplicate_detection import detect_and_flag_duplicates
from app.db.database import log_automation_execution

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/jira/issue-created")
async def handle_issue_created(request: Request, background_tasks: BackgroundTasks):
    """
    Triggered when a new JIRA issue is created

    Automation:
    - Auto-classify as Bug vs Feature
    - Detect potential duplicates
    - Route to appropriate queue
    """
    try:
        payload = await request.json()
        issue = payload.get("issue", {})
        issue_key = issue.get("key")
        fields = issue.get("fields", {})

        logger.info(f"📥 New issue created: {issue_key}")

        # Extract issue details
        summary = fields.get("summary", "")
        description = fields.get("description", "")
        reporter = fields.get("reporter", {}).get("displayName", "Unknown")

        # Run automation rules in background
        background_tasks.add_task(auto_classify_ticket, issue_key, summary, description)
        background_tasks.add_task(detect_and_flag_duplicates, issue_key, summary, description)

        # Log to database
        await log_automation_execution(
            rule_name="ISSUE_CREATED_HANDLER",
            ticket_id=issue_key,
            trigger_event="issue_created",
            success=True
        )

        return {
            "status": "processed",
            "issue_key": issue_key,
            "actions": ["auto_classify", "duplicate_detection"]
        }

    except Exception as e:
        logger.error(f"Error processing issue-created webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jira/issue-transitioned")
async def handle_issue_transitioned(request: Request, background_tasks: BackgroundTasks):
    """
    Triggered when issue status changes

    Automation:
    - Enforce BRD gate (block dev without BRD)
    - Start/stop SLA timers
    - Send notifications
    """
    try:
        payload = await request.json()
        issue = payload.get("issue", {})
        changelog = payload.get("changelog", {})

        issue_key = issue.get("key")
        fields = issue.get("fields", {})

        logger.info(f"🔄 Issue transitioned: {issue_key}")

        # Extract transition details
        for item in changelog.get("items", []):
            if item.get("field") == "status":
                from_status = item.get("fromString")
                to_status = item.get("toString")

                logger.info(f"   {from_status} → {to_status}")

                # BRD Gate Enforcement (CRITICAL)
                if to_status == "IN_PROGRESS" or to_status == "In Progress":
                    background_tasks.add_task(enforce_brd_gate, issue_key, fields)

                # Add more transition-based rules here
                # Example: Start SLA timer, send Slack notification, etc.

        await log_automation_execution(
            rule_name="ISSUE_TRANSITIONED_HANDLER",
            ticket_id=issue_key,
            trigger_event="issue_transitioned",
            success=True
        )

        return {
            "status": "processed",
            "issue_key": issue_key
        }

    except Exception as e:
        logger.error(f"Error processing issue-transitioned webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jira/issue-updated")
async def handle_issue_updated(request: Request):
    """
    Triggered when issue is updated

    Use for field validation, data quality checks
    """
    try:
        payload = await request.json()
        issue = payload.get("issue", {})
        issue_key = issue.get("key")

        logger.info(f"✏️  Issue updated: {issue_key}")

        # Add custom validation rules here

        return {"status": "processed"}

    except Exception as e:
        logger.error(f"Error processing issue-updated webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jira/comment-created")
async def handle_comment_created(request: Request):
    """
    Triggered when comment is added

    Use for automated responses, keyword detection
    """
    try:
        payload = await request.json()
        comment = payload.get("comment", {})
        issue = payload.get("issue", {})

        issue_key = issue.get("key")
        comment_body = comment.get("body", "")
        author = comment.get("author", {}).get("displayName", "Unknown")

        logger.info(f"💬 Comment added to {issue_key} by {author}")

        # Example: Detect keywords and auto-respond
        # if "blocked" in comment_body.lower():
        #     jira_client.add_label(issue_key, "blocked")

        return {"status": "processed"}

    except Exception as e:
        logger.error(f"Error processing comment-created webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))
