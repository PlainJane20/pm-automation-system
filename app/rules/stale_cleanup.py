"""
Stale Ticket Cleanup Rule
Auto-closes inactive tickets after 60 days to maintain data hygiene
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.jira_client import jira_client
from app.config import get_settings
from app.db.database import log_automation_execution

logger = logging.getLogger(__name__)
settings = get_settings()


async def cleanup_stale_tickets() -> Dict[str, Any]:
    """
    Find and auto-close tickets inactive for 60+ days

    Rules:
    - Only affects: SUBMITTED, AWAITING_SCOPING, NEEDS_MORE_INFO states
    - Excludes: P0/P1 critical tickets
    - Warns at 50 days, closes at 60 days

    Returns summary of actions taken
    """

    logger.info("🧹 Running stale ticket cleanup")

    # Step 1: Warn tickets at 50 days
    warned_tickets = await warn_stale_tickets(days=50)

    # Step 2: Close tickets at 60 days
    closed_tickets = await close_stale_tickets(days=60)

    summary = {
        "execution_time": datetime.utcnow().isoformat(),
        "warned_count": len(warned_tickets),
        "closed_count": len(closed_tickets),
        "warned_tickets": warned_tickets,
        "closed_tickets": closed_tickets
    }

    await log_automation_execution(
        rule_name="STALE_TICKET_CLEANUP",
        ticket_id="BULK_OPERATION",
        trigger_event="scheduled_job",
        success=True,
        details=summary
    )

    logger.info(f"   ✅ Warned: {len(warned_tickets)}, Closed: {len(closed_tickets)}")

    return summary


async def warn_stale_tickets(days: int = 50) -> List[str]:
    """
    Warn reporters that their tickets will be auto-closed in 10 days
    """

    # JQL to find tickets inactive for exactly `days` days
    jql = f"""
        status IN (SUBMITTED, "AWAITING_SCOPING", "NEEDS_MORE_INFO")
        AND updated <= -{days}d
        AND updated > -{days+1}d
        AND priority NOT IN (P0, P1)
        AND labels NOT IN (stale-warning-sent)
    """

    stale_tickets = jira_client.search_issues(jql, max_results=100)

    warned = []

    for ticket in stale_tickets:
        days_until_close = 60 - days  # e.g., 60 - 50 = 10

        comment = f"""⚠️ *Inactivity Warning*

This ticket has been inactive for {days} days and will be automatically closed in **{days_until_close} days** if no activity occurs.

*To prevent auto-closure:*
• Add a comment with an update
• Change the status
• Update any field

If this ticket is no longer needed, you can close it now.

_This is an automated data hygiene check._
"""

        jira_client.add_comment(ticket.key, comment)
        jira_client.add_label(ticket.key, "stale-warning-sent")

        # Optionally send email to reporter
        # await send_email_notification(ticket)

        warned.append(ticket.key)

        logger.info(f"   ⚠️  Warned: {ticket.key}")

    return warned


async def close_stale_tickets(days: int = 60) -> List[str]:
    """
    Auto-close tickets inactive for 60+ days
    """

    jql = f"""
        status IN (SUBMITTED, "AWAITING_SCOPING", "NEEDS_MORE_INFO")
        AND updated <= -{days}d
        AND priority NOT IN (P0, P1)
        AND labels NOT IN (auto-closed-stale)
    """

    stale_tickets = jira_client.search_issues(jql, max_results=100)

    closed = []

    for ticket in stale_tickets:
        comment = f"""🗑️ *Auto-Closed: Inactivity*

This ticket has been automatically closed due to {days}+ days of inactivity.

*To reopen:*
1. Click 'Reopen' in the workflow actions
2. Add a comment explaining why it's still needed

If this was closed in error, please contact your Program Manager.

_Closed by automated data hygiene policy._
"""

        # Add comment
        jira_client.add_comment(ticket.key, comment)

        # Transition to Closed
        success = jira_client.transition_issue(ticket.key, "Closed")

        if success:
            jira_client.add_label(ticket.key, "auto-closed-stale")

            # Optionally notify reporter via email
            # await send_closure_notification(ticket)

            closed.append(ticket.key)
            logger.info(f"   🗑️  Closed: {ticket.key}")

    return closed


async def get_stale_ticket_report() -> Dict[str, Any]:
    """
    Generate report of tickets at risk of being auto-closed

    Used by dashboard and weekly status reports
    """

    # Tickets at 50+ days (warning zone)
    jql_warning = """
        status IN (SUBMITTED, "AWAITING_SCOPING", "NEEDS_MORE_INFO")
        AND updated <= -50d
        AND updated > -60d
        AND priority NOT IN (P0, P1)
    """

    warning_tickets = jira_client.search_issues(jql_warning, max_results=100)

    # Tickets at 60+ days (will be closed next run)
    jql_critical = """
        status IN (SUBMITTED, "AWAITING_SCOPING", "NEEDS_MORE_INFO")
        AND updated <= -60d
        AND priority NOT IN (P0, P1)
    """

    critical_tickets = jira_client.search_issues(jql_critical, max_results=100)

    return {
        "warning_zone": {
            "count": len(warning_tickets),
            "tickets": [
                {
                    "key": t.key,
                    "summary": t.fields.summary,
                    "last_updated": t.fields.updated,
                    "reporter": t.fields.reporter.displayName if t.fields.reporter else "Unknown"
                }
                for t in warning_tickets
            ]
        },
        "critical_zone": {
            "count": len(critical_tickets),
            "tickets": [
                {
                    "key": t.key,
                    "summary": t.fields.summary,
                    "last_updated": t.fields.updated,
                    "reporter": t.fields.reporter.displayName if t.fields.reporter else "Unknown"
                }
                for t in critical_tickets
            ]
        },
        "generated_at": datetime.utcnow().isoformat()
    }
