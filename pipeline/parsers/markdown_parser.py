"""Deterministic markdown changelog parser.

Parses standard markdown changelogs with version headers (## [version] or ## version)
and extracts individual change entries with dates, types, and bodies.
All parsing is deterministic — no LLM calls.
"""

import re
import logging
from datetime import datetime, date
from typing import Optional

logger = logging.getLogger(__name__)

# Patterns for version headers
# Matches: ## [1.2.3] - 2024-01-15, ## 1.2.3 (2024-01-15), ## v1.2.3 — 2024-01-15, etc.
VERSION_HEADER_PATTERN = re.compile(
    r"^##\s+\[?v?(\d+\.\d+[\.\d]*(?:-[\w.]+)?)\]?"  # version number
    r"(?:\s*[-—(]\s*(\d{4}-\d{2}-\d{2}))?",           # optional date
    re.MULTILINE,
)

# Pattern to extract date from various formats in the header line
DATE_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2})")

# Patterns for change type indicators
CHANGE_TYPE_PATTERNS = {
    "breaking": re.compile(r"(?i)(?:breaking|⚠️|BREAKING CHANGE)"),
    "deprecation": re.compile(r"(?i)(?:deprecat|removed|removal)"),
    "security": re.compile(r"(?i)(?:security|vulnerabilit|CVE-)"),
    "bugfix": re.compile(r"(?i)(?:fix|bug|patch|resolve|correct)"),
    "enhancement": re.compile(r"(?i)(?:feat|add|enhanc|improv|new|support)"),
}

# Sub-section headers like ### Bug Fixes, ### Features, ### Breaking Changes
SUBSECTION_PATTERN = re.compile(r"^###\s+(.+)$", re.MULTILINE)

# Individual change entry (bullet point)
ENTRY_PATTERN = re.compile(r"^\s*[-*]\s+(.+)$", re.MULTILINE)


def parse_markdown_changelog(
    content: str,
    source_id: str,
    source_name: str,
) -> list[dict]:
    """Parse a markdown changelog into individual entries.

    Args:
        content: Raw markdown content of the changelog.
        source_id: Identifier for the source (e.g., 'stripe_node').
        source_name: Human-readable source name.

    Returns:
        List of parsed entry dictionaries with required fields.
    """
    entries = []
    entry_counter = 0

    # Split content into version blocks
    version_blocks = _split_into_version_blocks(content)

    for version, version_date, block_content in version_blocks:
        # Parse the date
        published_at = _parse_date(version_date) if version_date else None

        # Split block into sub-sections (### headers) or treat as flat
        sub_sections = _split_into_subsections(block_content)

        for section_type, section_content in sub_sections:
            # Extract individual change entries (bullet points)
            change_items = ENTRY_PATTERN.findall(section_content)

            if not change_items:
                # If no bullet points, treat the entire section as one entry
                clean_content = section_content.strip()
                if clean_content:
                    change_items = [clean_content]

            for item in change_items:
                entry_counter += 1
                entry_id = f"{source_id}-{entry_counter:03d}"

                # Detect change type from section header or content
                change_type_raw = section_type or _detect_change_type(item)

                entries.append({
                    "entry_id": entry_id,
                    "source_id": source_id,
                    "source": source_name,
                    "version_or_date": version or "unknown",
                    "published_at": published_at,
                    "change_title": _extract_title(item),
                    "change_body": item.strip(),
                    "change_type_raw": change_type_raw,
                })

    logger.info(f"Parsed {len(entries)} entries from {source_id} ({source_name})")
    return entries


def _split_into_version_blocks(content: str) -> list[tuple[str, Optional[str], str]]:
    """Split changelog into blocks by version header.

    Returns:
        List of (version, date_string, block_content) tuples.
    """
    blocks = []
    matches = list(VERSION_HEADER_PATTERN.finditer(content))

    if not matches:
        # Try a fallback: look for any ## headers with dates
        fallback_pattern = re.compile(r"^##\s+(.+)$", re.MULTILINE)
        fallback_matches = list(fallback_pattern.finditer(content))

        for i, match in enumerate(fallback_matches):
            header_text = match.group(1).strip()
            # Try to extract a date from the header
            date_match = DATE_PATTERN.search(header_text)
            date_str = date_match.group(1) if date_match else None

            start = match.end()
            end = fallback_matches[i + 1].start() if i + 1 < len(fallback_matches) else len(content)
            block_content = content[start:end].strip()

            blocks.append((header_text, date_str, block_content))

        return blocks

    for i, match in enumerate(matches):
        version = match.group(1)
        # Try to get date from capture group or search the full match line
        date_str = match.group(2) if match.group(2) else None
        if not date_str:
            full_line_end = content.find("\n", match.start())
            if full_line_end == -1:
                full_line_end = len(content)
            full_line = content[match.start():full_line_end]
            date_match = DATE_PATTERN.search(full_line)
            if date_match:
                date_str = date_match.group(1)

        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        block_content = content[start:end].strip()

        blocks.append((version, date_str, block_content))

    return blocks


def _split_into_subsections(
    block_content: str,
) -> list[tuple[Optional[str], str]]:
    """Split a version block into subsections by ### headers.

    Returns:
        List of (section_type, section_content) tuples.
    """
    matches = list(SUBSECTION_PATTERN.finditer(block_content))

    if not matches:
        return [(None, block_content)]

    sections = []

    # Content before first subsection
    pre_content = block_content[:matches[0].start()].strip()
    if pre_content:
        sections.append((None, pre_content))

    for i, match in enumerate(matches):
        section_type = _normalize_section_type(match.group(1).strip())
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(block_content)
        section_content = block_content[start:end].strip()
        sections.append((section_type, section_content))

    return sections


def _normalize_section_type(header: str) -> Optional[str]:
    """Map subsection header to a raw change type hint."""
    header_lower = header.lower().strip()

    mapping = {
        "breaking changes": "breaking",
        "breaking": "breaking",
        "deprecated": "deprecation",
        "deprecations": "deprecation",
        "removed": "deprecation",
        "security": "security",
        "bug fixes": "bugfix",
        "bugfixes": "bugfix",
        "fixes": "bugfix",
        "fixed": "bugfix",
        "features": "enhancement",
        "added": "enhancement",
        "enhancements": "enhancement",
        "improvements": "enhancement",
        "new features": "enhancement",
        "performance": "enhancement",
        "chores": None,
        "documentation": None,
        "refactoring": None,
    }

    for key, value in mapping.items():
        if key in header_lower:
            return value

    return None


def _detect_change_type(text: str) -> Optional[str]:
    """Detect change type from entry text using keyword matching."""
    for change_type, pattern in CHANGE_TYPE_PATTERNS.items():
        if pattern.search(text):
            return change_type
    return None


def _extract_title(text: str) -> str:
    """Extract a concise title from a changelog entry."""
    # Take the first sentence or first 120 characters
    text = text.strip()

    # Remove leading markdown formatting
    text = re.sub(r"^\*\*(.+?)\*\*", r"\1", text)

    # First sentence
    sentence_end = re.search(r"[.!?]\s", text)
    if sentence_end and sentence_end.start() < 120:
        return text[:sentence_end.start() + 1].strip()

    # Truncate at 120 chars
    if len(text) > 120:
        return text[:117].strip() + "..."

    return text


def _parse_date(date_str: str) -> Optional[str]:
    """Parse a date string into ISO-8601 format.

    Args:
        date_str: Date string like '2024-01-15'.

    Returns:
        ISO-8601 date string or None if unparseable.
    """
    if not date_str:
        return None

    try:
        parsed = datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return parsed.date().isoformat()
    except ValueError:
        logger.debug(f"Could not parse date: {date_str}")
        return None
