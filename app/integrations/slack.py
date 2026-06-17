"""
Slack Integration
Send notifications and updates to Slack channels
"""

import logging
from typing import Optional

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def post_to_slack(channel: str, message: str, blocks: Optional[list] = None) -> bool:
    """
    Post a message to Slack channel

    Args:
        channel: Channel name (e.g., "#program-status") or ID
        message: Plain text message (fallback)
        blocks: Rich formatting blocks (optional)

    Returns:
        True if successful, False otherwise
    """

    if not settings.ENABLE_SLACK_NOTIFICATIONS or not settings.SLACK_BOT_TOKEN:
        logger.info(f"Slack disabled - would have sent to {channel}: {message}")
        return False

    try:
        from slack_sdk import WebClient
        from slack_sdk.errors import SlackApiError

        client = WebClient(token=settings.SLACK_BOT_TOKEN)

        response = client.chat_postMessage(
            channel=channel,
            text=message,
            blocks=blocks
        )

        logger.info(f"✅ Posted to Slack {channel}")
        return True

    except Exception as e:
        logger.error(f"Failed to post to Slack: {e}")
        return False


async def notify_dev_started(ticket_key: str, assignee: str, summary: str):
    """Notify when development starts on a ticket"""

    message = f"🚀 Development started on {ticket_key}"

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🚀 Development Started*\n\n*Ticket:* <{settings.JIRA_URL}/browse/{ticket_key}|{ticket_key}>\n*Summary:* {summary}\n*Assignee:* {assignee}"
            }
        }
    ]

    await post_to_slack(settings.SLACK_NOTIFICATIONS_CHANNEL, message, blocks)


async def notify_deployment(ticket_key: str, environment: str, status: str):
    """Notify about deployment events"""

    emoji = "✅" if status == "success" else "❌"

    message = f"{emoji} Deployment to {environment}: {ticket_key} - {status}"

    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{emoji} Deployment Update*\n\n*Environment:* {environment}\n*Ticket:* <{settings.JIRA_URL}/browse/{ticket_key}|{ticket_key}>\n*Status:* {status.upper()}"
            }
        }
    ]

    await post_to_slack("#engineering-deploys", message, blocks)


async def notify_sla_breach(ticket_key: str, priority: str, hours_overdue: int):
    """Notify about SLA breach"""

    message = f"🚨 SLA BREACH: {ticket_key} ({priority}) is {hours_overdue} hours overdue"

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🚨 SLA BREACH ALERT"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Ticket:* <{settings.JIRA_URL}/browse/{ticket_key}|{ticket_key}>\n*Priority:* {priority}\n*Overdue by:* {hours_overdue} hours"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Ticket"
                    },
                    "url": f"{settings.JIRA_URL}/browse/{ticket_key}"
                }
            ]
        }
    ]

    await post_to_slack("#sla-alerts", message, blocks)


async def send_daily_standup(project: str, summary: dict):
    """
    Post daily standup summary

    Args:
        project: Project key
        summary: Dict with counts and ticket lists
    """

    message = f"📊 Daily Standup: {project}"

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"📊 Daily Status: {project}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Yesterday:*\n• Closed: {summary.get('closed_yesterday', 0)}\n• Deployed: {summary.get('deployed_yesterday', 0)}\n\n*Today:*\n• In Progress: {summary.get('in_progress', 0)}\n• Blocked: {summary.get('blocked', 0)}"
            }
        }
    ]

    if summary.get('blockers'):
        blocker_text = "\n".join([
            f"• <{settings.JIRA_URL}/browse/{b['key']}|{b['key']}>: {b['summary']}"
            for b in summary['blockers'][:3]
        ])

        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🚨 Blockers:*\n{blocker_text}"
            }
        })

    await post_to_slack(settings.SLACK_NOTIFICATIONS_CHANNEL, message, blocks)


async def create_ticket_from_slack_message(channel_id: str, message_ts: str, text: str, user: str) -> Optional[str]:
    """
    Create JIRA ticket from Slack message

    Used for Slack bot that converts requests into tickets
    """

    from app.jira_client import jira_client

    # Create ticket
    issue = jira_client.create_issue(
        project=settings.JIRA_PROJECT_KEY,
        summary=text[:100],  # Truncate long messages
        description=f"Request from Slack by {user}:\n\n{text}",
        issue_type="Task"
    )

    if issue:
        # Reply in Slack thread
        await post_to_slack(
            channel_id,
            f"✅ Created ticket: {issue.key}",
            blocks=[{
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*✅ Ticket Created*\n\n*{issue.key}:* {text[:50]}...\n\n<{settings.JIRA_URL}/browse/{issue.key}|View in JIRA>"
                }
            }]
        )

        return issue.key

    return None
