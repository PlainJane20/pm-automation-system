"""
Duplicate Detection Rule
Flags potential duplicate tickets to prevent redundant work
"""

import logging
from typing import List, Dict, Any
from difflib import SequenceMatcher

from app.jira_client import jira_client
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def detect_and_flag_duplicates(issue_key: str, summary: str, description: str) -> List[Dict[str, Any]]:
    """
    Detect potential duplicate tickets

    Strategy:
    1. If OPENAI_API_KEY available: Use semantic similarity (embeddings)
    2. Fallback: Use string similarity (Levenshtein distance)

    If duplicates found:
    - Add comment linking to potential duplicates
    - Add 'potential-duplicate' label
    - Notify reporter to review
    """

    logger.info(f"🔍 Checking for duplicates of {issue_key}")

    duplicates = []

    # Try AI-powered semantic search first
    if settings.ENABLE_AI_CLASSIFICATION and settings.OPENAI_API_KEY:
        duplicates = await find_duplicates_with_ai(issue_key, summary, description)

    # Fallback to string similarity
    if not duplicates:
        duplicates = find_duplicates_with_string_similarity(issue_key, summary)

    if duplicates:
        logger.warning(f"   ⚠️  Found {len(duplicates)} potential duplicate(s)")

        # Build comment with duplicate links
        duplicate_list = "\n".join([
            f"• [{d['ticket_key']}|{settings.JIRA_URL}/browse/{d['ticket_key']}] - "
            f"{d['title']} (Similarity: {d['similarity']:.0%})"
            for d in duplicates[:3]  # Show top 3
        ])

        comment = f"""⚠️ *Potential Duplicate Detected*

This ticket may be similar to existing tickets:

{duplicate_list}

*Please review:*
• Is this a duplicate? If yes, close this ticket and reference the existing one.
• Is this different? Add a comment explaining how it differs.

_This is an automated check. False positives are possible._
"""

        jira_client.add_comment(issue_key, comment)
        jira_client.add_label(issue_key, "potential-duplicate")

        return duplicates

    else:
        logger.info(f"   ✅ No duplicates found for {issue_key}")
        return []


async def find_duplicates_with_ai(issue_key: str, summary: str, description: str) -> List[Dict[str, Any]]:
    """
    Use OpenAI embeddings for semantic similarity search
    More accurate than string matching - finds conceptually similar tickets
    """
    try:
        from openai import OpenAI
        import numpy as np

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        # Generate embedding for new ticket
        new_ticket_text = f"{summary}\n{description[:500]}"

        response = client.embeddings.create(
            model="text-embedding-3-small",  # Cheapest embedding model
            input=new_ticket_text
        )

        new_embedding = response.data[0].embedding

        # Fetch recent tickets (last 90 days)
        jql = f"""
            created >= -90d
            AND status NOT IN (Closed, Abandoned)
            AND key != {issue_key}
        """

        existing_tickets = jira_client.search_issues(jql, max_results=100)

        # Calculate similarity for each ticket
        duplicates = []

        for ticket in existing_tickets:
            ticket_text = f"{ticket.fields.summary}\n{(ticket.fields.description or '')[:500]}"

            # Generate embedding
            ticket_response = client.embeddings.create(
                model="text-embedding-3-small",
                input=ticket_text
            )

            ticket_embedding = ticket_response.data[0].embedding

            # Cosine similarity
            similarity = np.dot(new_embedding, ticket_embedding) / (
                np.linalg.norm(new_embedding) * np.linalg.norm(ticket_embedding)
            )

            if similarity >= settings.DUPLICATE_SIMILARITY_THRESHOLD:
                duplicates.append({
                    "ticket_key": ticket.key,
                    "title": ticket.fields.summary,
                    "similarity": similarity,
                    "method": "ai_embedding"
                })

        # Sort by similarity (descending)
        duplicates.sort(key=lambda x: x['similarity'], reverse=True)

        return duplicates

    except Exception as e:
        logger.error(f"AI duplicate detection failed: {e}")
        return []


def find_duplicates_with_string_similarity(issue_key: str, summary: str) -> List[Dict[str, Any]]:
    """
    Fallback: Simple string similarity using Levenshtein distance
    Fast but less accurate than AI embeddings
    """

    # Fetch recent tickets
    jql = f"""
        created >= -90d
        AND status NOT IN (Closed, Abandoned)
        AND key != {issue_key}
    """

    existing_tickets = jira_client.search_issues(jql, max_results=100)

    duplicates = []

    for ticket in existing_tickets:
        similarity = SequenceMatcher(
            None,
            summary.lower(),
            ticket.fields.summary.lower()
        ).ratio()

        if similarity >= settings.DUPLICATE_SIMILARITY_THRESHOLD:
            duplicates.append({
                "ticket_key": ticket.key,
                "title": ticket.fields.summary,
                "similarity": similarity,
                "method": "string_match"
            })

    # Sort by similarity (descending)
    duplicates.sort(key=lambda x: x['similarity'], reverse=True)

    logger.info(f"   String similarity search found {len(duplicates)} matches")

    return duplicates


async def mark_as_duplicate(issue_key: str, duplicate_of: str, close: bool = True) -> bool:
    """
    Mark a ticket as duplicate and optionally close it

    Used when user confirms a duplicate
    """

    try:
        # Add link to duplicate
        jira_client.add_comment(
            issue_key,
            f"🔗 Marked as duplicate of {duplicate_of}"
        )

        # Add label
        jira_client.add_label(issue_key, "duplicate")

        # Create JIRA link (if supported by API)
        # jira_client.create_issue_link("Duplicate", issue_key, duplicate_of)

        # Close if requested
        if close:
            jira_client.transition_issue(
                issue_key,
                "Closed",
                comment=f"Closing as duplicate of {duplicate_of}"
            )

        logger.info(f"✅ Marked {issue_key} as duplicate of {duplicate_of}")
        return True

    except Exception as e:
        logger.error(f"Failed to mark {issue_key} as duplicate: {e}")
        return False
