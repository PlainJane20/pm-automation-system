"""
Auto-Classification Rule
Uses AI (OpenAI) or keyword matching to classify tickets as Bug vs Feature
"""

import logging
from typing import Optional
import re

from app.jira_client import jira_client
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def auto_classify_ticket(issue_key: str, summary: str, description: str) -> Optional[str]:
    """
    Automatically classify ticket as Bug, Feature, Enhancement, or Support Request

    Strategy:
    1. If OPENAI_API_KEY available: Use GPT-4 for smart classification
    2. Fallback: Use keyword-based classification

    Updates the 'Request Type' custom field in JIRA
    """

    logger.info(f"🤖 Auto-classifying {issue_key}")

    classification = None

    # Try AI classification first
    if settings.ENABLE_AI_CLASSIFICATION and settings.OPENAI_API_KEY:
        classification = await classify_with_ai(summary, description)

    # Fallback to keyword-based classification
    if not classification:
        classification = classify_with_keywords(summary, description)

    if classification:
        # Update JIRA field
        success = jira_client.update_field(
            issue_key,
            "Request Type",  # Custom field name
            classification
        )

        if success:
            logger.info(f"   ✅ Classified as: {classification}")

            # Add comment explaining the classification
            jira_client.add_comment(
                issue_key,
                f"🤖 Auto-classified as *{classification}* based on content analysis. Please verify and update if incorrect."
            )

            # Add label
            jira_client.add_label(issue_key, "auto-classified")

            return classification

    logger.warning(f"   ⚠️  Could not auto-classify {issue_key}")
    return None


async def classify_with_ai(summary: str, description: str) -> Optional[str]:
    """
    Use OpenAI GPT-4 for intelligent classification
    Cost: ~$0.001 per ticket (negligible)
    """
    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        prompt = f"""Classify this software development ticket into exactly ONE category: Bug, Feature, Enhancement, or Support Request.

**Ticket Summary:** {summary}

**Description:** {description[:500]}

**Classification Rules:**
- Bug: Something is broken, not working as expected, error, crash, incorrect behavior
- Feature: New functionality that doesn't exist yet
- Enhancement: Improvement to existing functionality (performance, UX, optimization)
- Support Request: Question, how-to, configuration help, access request

**Output the classification as a single word only (Bug, Feature, Enhancement, or Support Request):**"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cheapest model, sufficient for this task
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0  # Deterministic
        )

        classification = response.choices[0].message.content.strip()

        # Validate response
        valid_types = ["Bug", "Feature", "Enhancement", "Support Request"]
        if classification in valid_types:
            logger.info(f"   🧠 AI classified as: {classification}")
            return classification
        else:
            logger.warning(f"   ⚠️  AI returned invalid classification: {classification}")
            return None

    except Exception as e:
        logger.error(f"AI classification failed: {e}")
        return None


def classify_with_keywords(summary: str, description: str) -> str:
    """
    Fallback: Simple keyword-based classification
    """
    text = f"{summary} {description}".lower()

    # Bug keywords
    bug_keywords = [
        'error', 'bug', 'broken', 'crash', 'fail', 'issue', 'problem',
        'not working', 'doesn\'t work', 'incorrect', 'wrong', '500', '404',
        'exception', 'stack trace', 'null pointer', 'undefined'
    ]

    # Feature keywords
    feature_keywords = [
        'add', 'new', 'create', 'implement', 'build', 'develop',
        'feature', 'functionality', 'need', 'want', 'should', 'ability to'
    ]

    # Enhancement keywords
    enhancement_keywords = [
        'improve', 'enhance', 'optimize', 'better', 'faster', 'upgrade',
        'refactor', 'performance', 'usability', 'ui/ux', 'redesign'
    ]

    # Support keywords
    support_keywords = [
        'how to', 'how do i', 'question', 'help', 'access', 'permission',
        'unable to', 'can\'t', 'configuration', 'setup', 'install'
    ]

    # Count keyword matches
    bug_score = sum(1 for kw in bug_keywords if kw in text)
    feature_score = sum(1 for kw in feature_keywords if kw in text)
    enhancement_score = sum(1 for kw in enhancement_keywords if kw in text)
    support_score = sum(1 for kw in support_keywords if kw in text)

    # Determine classification based on highest score
    scores = {
        'Bug': bug_score,
        'Feature': feature_score,
        'Enhancement': enhancement_score,
        'Support Request': support_score
    }

    classification = max(scores, key=scores.get)

    # Default to Feature if all scores are 0
    if scores[classification] == 0:
        classification = 'Feature'

    logger.info(f"   🔤 Keyword-based classification: {classification} (scores: {scores})")
    return classification


async def get_classification_confidence(issue_key: str) -> dict:
    """
    For dashboard/reporting: Return confidence score for classification
    """
    issue = jira_client.get_issue(issue_key)
    if not issue:
        return {"error": "Issue not found"}

    summary = issue.fields.summary
    description = issue.fields.description or ""
    classification = jira_client.get_custom_field_value(issue, "Request Type")

    # Simple confidence based on keyword match strength
    text = f"{summary} {description}".lower()

    keyword_sets = {
        'Bug': ['error', 'bug', 'broken', 'crash'],
        'Feature': ['add', 'new', 'create', 'implement'],
        'Enhancement': ['improve', 'enhance', 'optimize'],
        'Support Request': ['how to', 'question', 'help']
    }

    if classification in keyword_sets:
        matches = sum(1 for kw in keyword_sets[classification] if kw in text)
        confidence = min(matches * 25, 100)  # Cap at 100%
    else:
        confidence = 0

    return {
        "classification": classification,
        "confidence": confidence,
        "auto_classified": "auto-classified" in (issue.fields.labels or [])
    }
