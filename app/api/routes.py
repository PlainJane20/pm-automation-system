"""
API routes for dashboard and external integrations
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta

from app.jira_client import jira_client
from app.rules.stale_cleanup import cleanup_stale_tickets, get_stale_ticket_report
from app.rules.brd_gate import check_brd_gate_status
from app.db.database import get_automation_stats

router = APIRouter()


@router.get("/program-health")
async def get_program_health(project: str = Query(default="PILOT")):
    """
    Get overall program health metrics

    Returns:
    - Total tickets in flight
    - Tickets by status
    - Blocked tickets
    - At-risk tickets
    - BRD compliance rate
    """

    # Fetch all active tickets
    jql = f"project = {project} AND status NOT IN (Closed, Abandoned)"
    tickets = jira_client.search_issues(jql, max_results=500)

    # Categorize by status
    by_status = {}
    blocked_tickets = []
    at_risk_tickets = []

    for ticket in tickets:
        status = ticket.fields.status.name
        by_status[status] = by_status.get(status, 0) + 1

        # Check if blocked
        if "blocked" in (ticket.fields.labels or []):
            blocked_tickets.append({
                "key": ticket.key,
                "summary": ticket.fields.summary,
                "assignee": ticket.fields.assignee.displayName if ticket.fields.assignee else "Unassigned"
            })

        # Check if at-risk (updated > 7 days ago)
        updated = datetime.fromisoformat(ticket.fields.updated.replace('Z', '+00:00'))
        if datetime.now(updated.tzinfo) - updated > timedelta(days=7):
            at_risk_tickets.append({
                "key": ticket.key,
                "summary": ticket.fields.summary,
                "last_updated": ticket.fields.updated
            })

    # Calculate BRD compliance
    feature_tickets = [t for t in tickets if jira_client.get_custom_field_value(t, "Request Type") == "Feature"]
    brd_compliant = 0

    for ticket in feature_tickets:
        status = await check_brd_gate_status(ticket.key)
        if status.get("compliant"):
            brd_compliant += 1

    brd_compliance_rate = (brd_compliant / len(feature_tickets) * 100) if feature_tickets else 100

    return {
        "project": project,
        "timestamp": datetime.utcnow().isoformat(),
        "total_tickets": len(tickets),
        "by_status": by_status,
        "blocked_count": len(blocked_tickets),
        "blocked_tickets": blocked_tickets[:5],  # Top 5
        "at_risk_count": len(at_risk_tickets),
        "at_risk_tickets": at_risk_tickets[:5],  # Top 5
        "brd_compliance_rate": round(brd_compliance_rate, 1),
        "health_score": calculate_health_score(by_status, len(blocked_tickets), brd_compliance_rate)
    }


@router.get("/velocity")
async def get_velocity(project: str = Query(default="PILOT"), weeks: int = Query(default=6)):
    """
    Calculate team velocity over the last N weeks

    Returns weekly story points completed
    """

    velocity_data = []

    for week_offset in range(weeks):
        start_date = datetime.utcnow() - timedelta(weeks=week_offset+1)
        end_date = datetime.utcnow() - timedelta(weeks=week_offset)

        jql = f"""
            project = {project}
            AND status = Closed
            AND resolved >= '{start_date.strftime('%Y-%m-%d')}'
            AND resolved < '{end_date.strftime('%Y-%m-%d')}'
        """

        tickets = jira_client.search_issues(jql, max_results=500)

        # Sum story points (assuming custom field exists)
        total_points = 0
        for ticket in tickets:
            points = jira_client.get_custom_field_value(ticket, "Story Points") or 0
            total_points += points

        velocity_data.append({
            "week_start": start_date.strftime('%Y-%m-%d'),
            "week_end": end_date.strftime('%Y-%m-%d'),
            "tickets_completed": len(tickets),
            "story_points": total_points
        })

    velocity_data.reverse()  # Chronological order

    avg_velocity = sum(w["story_points"] for w in velocity_data) / len(velocity_data) if velocity_data else 0

    return {
        "project": project,
        "weeks": weeks,
        "velocity_by_week": velocity_data,
        "average_velocity": round(avg_velocity, 1)
    }


@router.get("/stale-tickets")
async def get_stale_tickets():
    """Get report of tickets at risk of auto-closure"""
    return await get_stale_ticket_report()


@router.post("/stale-tickets/cleanup")
async def run_stale_cleanup():
    """Manually trigger stale ticket cleanup (also runs on schedule)"""
    result = await cleanup_stale_tickets()
    return result


@router.get("/automation-stats")
async def get_automation_statistics(days: int = Query(default=30)):
    """Get automation execution statistics"""
    return await get_automation_stats(days)


@router.get("/ticket/{ticket_key}/analysis")
async def analyze_ticket(ticket_key: str):
    """
    Deep analysis of a single ticket

    Returns:
    - BRD gate status
    - Classification confidence
    - Duplicate detection results
    - Automation history
    """

    ticket = jira_client.get_issue(ticket_key)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # BRD gate status
    brd_status = await check_brd_gate_status(ticket_key)

    # Get automation history from DB
    from app.db.database import async_session, AutomationExecution
    from sqlalchemy import select

    async with async_session() as session:
        result = await session.execute(
            select(AutomationExecution)
            .where(AutomationExecution.ticket_id == ticket_key)
            .order_by(AutomationExecution.execution_timestamp.desc())
            .limit(10)
        )
        executions = result.scalars().all()

    automation_history = [{
        "rule_name": e.rule_name,
        "timestamp": e.execution_timestamp.isoformat(),
        "success": e.success,
        "trigger_event": e.trigger_event
    } for e in executions]

    return {
        "ticket_key": ticket_key,
        "summary": ticket.fields.summary,
        "status": ticket.fields.status.name,
        "brd_gate_status": brd_status,
        "automation_history": automation_history,
        "labels": ticket.fields.labels or [],
        "last_updated": ticket.fields.updated
    }


def calculate_health_score(by_status: dict, blocked_count: int, brd_compliance: float) -> int:
    """
    Calculate overall program health score (0-100)

    Factors:
    - Blocked tickets (bad)
    - BRD compliance (good)
    - Ratio of in-progress to done (good if balanced)
    """

    score = 100

    # Penalty for blocked tickets
    score -= min(blocked_count * 5, 30)  # Max -30 points

    # Bonus for BRD compliance
    if brd_compliance >= 90:
        score += 0
    elif brd_compliance >= 70:
        score -= 10
    else:
        score -= 20

    # Penalty for too many "Submitted" tickets (backlog grooming issue)
    submitted = by_status.get("SUBMITTED", 0)
    total = sum(by_status.values())
    if total > 0:
        submitted_ratio = submitted / total
        if submitted_ratio > 0.3:  # More than 30% unprocessed
            score -= 15

    return max(0, min(100, score))  # Clamp to 0-100
