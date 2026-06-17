"""
JIRA API Client
Wrapper around jira-python library with async support
"""

from jira import JIRA
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class JIRAClient:
    """Async-friendly JIRA API client"""

    def __init__(self):
        self.client = JIRA(
            server=settings.JIRA_URL,
            basic_auth=(settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)
        )
        logger.info(f"✅ Connected to JIRA: {settings.JIRA_URL}")

    def get_issue(self, issue_key: str):
        """Fetch a single issue by key"""
        try:
            return self.client.issue(issue_key)
        except Exception as e:
            logger.error(f"Failed to fetch issue {issue_key}: {e}")
            return None

    def search_issues(self, jql: str, max_results: int = 100) -> List:
        """Search issues using JQL"""
        try:
            return self.client.search_issues(jql, maxResults=max_results)
        except Exception as e:
            logger.error(f"JQL search failed: {e}")
            return []

    def create_issue(
        self,
        project: str,
        summary: str,
        description: str,
        issue_type: str = "Task",
        **kwargs
    ):
        """Create a new JIRA issue"""
        issue_dict = {
            'project': {'key': project},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type},
            **kwargs
        }

        try:
            issue = self.client.create_issue(fields=issue_dict)
            logger.info(f"✅ Created issue: {issue.key}")
            return issue
        except Exception as e:
            logger.error(f"Failed to create issue: {e}")
            return None

    def transition_issue(self, issue_key: str, transition_name: str, comment: str = None) -> bool:
        """Transition an issue to a new status"""
        try:
            issue = self.get_issue(issue_key)
            if not issue:
                return False

            # Find transition ID by name
            transitions = self.client.transitions(issue)
            transition_id = None

            for t in transitions:
                if t['name'].lower() == transition_name.lower():
                    transition_id = t['id']
                    break

            if not transition_id:
                logger.error(f"Transition '{transition_name}' not found for {issue_key}")
                return False

            # Perform transition
            self.client.transition_issue(issue, transition_id)

            # Add comment if provided
            if comment:
                self.add_comment(issue_key, comment)

            logger.info(f"✅ Transitioned {issue_key} to {transition_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to transition {issue_key}: {e}")
            return False

    def add_comment(self, issue_key: str, comment: str) -> bool:
        """Add a comment to an issue"""
        try:
            self.client.add_comment(issue_key, comment)
            logger.info(f"✅ Added comment to {issue_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to add comment to {issue_key}: {e}")
            return False

    def update_field(self, issue_key: str, field_name: str, value: Any) -> bool:
        """Update a custom field"""
        try:
            issue = self.get_issue(issue_key)
            if not issue:
                return False

            issue.update(fields={field_name: value})
            logger.info(f"✅ Updated {field_name} for {issue_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to update field {field_name} for {issue_key}: {e}")
            return False

    def get_custom_field_value(self, issue, field_name: str) -> Optional[Any]:
        """Get custom field value by name"""
        try:
            # Map field name to customfield ID
            all_fields = self.client.fields()
            field_id = None

            for field in all_fields:
                if field['name'] == field_name:
                    field_id = field['id']
                    break

            if not field_id:
                logger.warning(f"Field '{field_name}' not found")
                return None

            return getattr(issue.fields, field_id, None)
        except Exception as e:
            logger.error(f"Failed to get custom field {field_name}: {e}")
            return None

    def add_label(self, issue_key: str, label: str) -> bool:
        """Add a label to an issue"""
        try:
            issue = self.get_issue(issue_key)
            if not issue:
                return False

            current_labels = issue.fields.labels or []
            if label not in current_labels:
                current_labels.append(label)
                issue.update(fields={'labels': current_labels})
                logger.info(f"✅ Added label '{label}' to {issue_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to add label to {issue_key}: {e}")
            return False

    def assign_issue(self, issue_key: str, assignee: str) -> bool:
        """Assign an issue to a user"""
        try:
            self.client.assign_issue(issue_key, assignee)
            logger.info(f"✅ Assigned {issue_key} to {assignee}")
            return True
        except Exception as e:
            logger.error(f"Failed to assign {issue_key}: {e}")
            return False


# Singleton instance
jira_client = JIRAClient()
