"""HTML changelog parser using BeautifulSoup.

Parses HTML changelogs by looking for common patterns like article elements,
date-stamped sections, and list items. Falls back gracefully if the HTML
structure is not parseable or requires JavaScript rendering.
"""

import re
import logging
from typing import Optional
from datetime import datetime

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Date patterns to find in HTML content
DATE_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2})")
DATE_PATTERN_ALT = re.compile(
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+\d{1,2},?\s+\d{4}",
    re.IGNORECASE,
)

# Month name mapping for alternative date format
MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}


def parse_html_changelog(
    content: str,
    source_id: str,
    source_name: str,
) -> list[dict]:
    """Parse an HTML changelog into individual entries.

    Attempts to extract changelog entries from common HTML patterns.
    Returns an empty list with appropriate logging if the content
    cannot be parsed (e.g., requires JavaScript rendering).

    Args:
        content: Raw HTML content.
        source_id: Source identifier.
        source_name: Human-readable source name.

    Returns:
        List of parsed entry dictionaries.
    """
    if not content or not content.strip():
        logger.warning(f"Empty HTML content for {source_id}")
        return []

    soup = BeautifulSoup(content, "html.parser")
    entries = []
    entry_counter = 0

    # Strategy 1: Look for article or section elements with dates
    articles = soup.find_all(["article", "section", "div"], class_=re.compile(
        r"(?i)changelog|change|release|update|entry|post"
    ))

    if articles:
        for article in articles:
            entry_counter += 1
            entry = _parse_article_element(article, source_id, source_name, entry_counter)
            if entry:
                entries.append(entry)

    # Strategy 2: Look for heading + content pattern
    if not entries:
        headings = soup.find_all(["h1", "h2", "h3", "h4"])
        for i, heading in enumerate(headings):
            # Get content between this heading and the next
            content_parts = []
            sibling = heading.find_next_sibling()
            while sibling and sibling.name not in ["h1", "h2", "h3", "h4"]:
                text = sibling.get_text(strip=True)
                if text:
                    content_parts.append(text)
                sibling = sibling.find_next_sibling()

            if content_parts:
                entry_counter += 1
                heading_text = heading.get_text(strip=True)
                date_str = _extract_date_from_text(heading_text)

                entries.append({
                    "entry_id": f"{source_id}-{entry_counter:03d}",
                    "source_id": source_id,
                    "source": source_name,
                    "version_or_date": heading_text[:100],
                    "published_at": date_str,
                    "change_title": heading_text[:120],
                    "change_body": " ".join(content_parts)[:500],
                    "change_type_raw": None,
                })

    # Strategy 3: Look for list items as individual changes
    if not entries:
        list_items = soup.find_all("li")
        for li in list_items:
            text = li.get_text(strip=True)
            if len(text) > 20:  # Skip trivially short items
                entry_counter += 1
                entries.append({
                    "entry_id": f"{source_id}-{entry_counter:03d}",
                    "source_id": source_id,
                    "source": source_name,
                    "version_or_date": "unknown",
                    "published_at": _extract_date_from_text(text),
                    "change_title": text[:120],
                    "change_body": text,
                    "change_type_raw": None,
                })

    if not entries:
        logger.warning(
            f"Could not parse HTML changelog for {source_id}. "
            f"The page may require JavaScript rendering or uses an unrecognized format. "
            f"Content length: {len(content)} chars"
        )

    logger.info(f"Parsed {len(entries)} entries from HTML for {source_id}")
    return entries


def _parse_article_element(
    article,
    source_id: str,
    source_name: str,
    counter: int,
) -> Optional[dict]:
    """Parse a single article/section element into an entry."""
    # Try to find a heading within the article
    heading = article.find(["h1", "h2", "h3", "h4", "h5"])
    title = heading.get_text(strip=True) if heading else ""

    # Try to find a date
    time_el = article.find("time")
    date_str = None
    if time_el:
        date_str = time_el.get("datetime", time_el.get_text(strip=True))
        date_str = _normalize_date(date_str)

    if not date_str:
        # Search text for dates
        full_text = article.get_text()
        date_str = _extract_date_from_text(full_text)

    # Get the body text
    body = article.get_text(strip=True)
    if title and body.startswith(title):
        body = body[len(title):].strip()

    if not title and not body:
        return None

    return {
        "entry_id": f"{source_id}-{counter:03d}",
        "source_id": source_id,
        "source": source_name,
        "version_or_date": title[:100] if title else "unknown",
        "published_at": date_str,
        "change_title": (title or body[:120]).strip(),
        "change_body": body[:500] if body else "",
        "change_type_raw": None,
    }


def _extract_date_from_text(text: str) -> Optional[str]:
    """Try to extract a date from arbitrary text."""
    # Try ISO format first
    match = DATE_PATTERN.search(text)
    if match:
        return _normalize_date(match.group(1))

    # Try "Month DD, YYYY" format
    match = DATE_PATTERN_ALT.search(text)
    if match:
        return _normalize_date(match.group(0))

    return None


def _normalize_date(date_str: str) -> Optional[str]:
    """Normalize various date formats to ISO-8601."""
    if not date_str:
        return None

    date_str = date_str.strip()

    # Already ISO format
    if re.match(r"^\d{4}-\d{2}-\d{2}", date_str):
        try:
            parsed = datetime.strptime(date_str[:10], "%Y-%m-%d")
            return parsed.date().isoformat()
        except ValueError:
            pass

    # Try "Month DD, YYYY"
    try:
        # Handle with and without comma
        for fmt in ["%B %d, %Y", "%B %d %Y", "%b %d, %Y", "%b %d %Y"]:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.date().isoformat()
            except ValueError:
                continue
    except Exception:
        pass

    return None
