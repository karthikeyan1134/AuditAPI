"""Stage 2: Parse fetched changelogs into structured entries.

Routes each source to the appropriate parser (markdown or HTML) based on
the configured format. Generates unique entry IDs and saves parsed entries
to per-source JSON files.
"""

import json
import logging
from pathlib import Path

from pipeline.config import PipelineConfig
from pipeline.parsers.markdown_parser import parse_markdown_changelog
from pipeline.parsers.html_parser import parse_html_changelog

logger = logging.getLogger(__name__)


def parse_all_changelogs(
    config: PipelineConfig,
    fetch_results: dict[str, dict],
) -> dict[str, list[dict]]:
    """Parse all fetched changelogs into structured entries.

    Args:
        config: Pipeline configuration.
        fetch_results: Dictionary of fetch results from Stage 1.

    Returns:
        Dictionary mapping source_id to list of parsed entries.
    """
    all_parsed = {}

    for source in config.sources:
        source_id = source.source_id
        fetch_result = fetch_results.get(source_id)

        if not fetch_result or not fetch_result.get("success"):
            # Source fetch failed — create empty result with reason
            error_msg = (
                fetch_result.get("error", "Unknown error")
                if fetch_result
                else "Source not found in fetch results"
            )
            logger.warning(f"Skipping parse for {source_id}: {error_msg}")
            all_parsed[source_id] = []
            _save_parsed_entries(
                config, source_id, [],
                reason=f"Fetch failed: {error_msg}"
            )
            continue

        content = fetch_result.get("content", "")
        if not content:
            logger.warning(f"No content to parse for {source_id}")
            all_parsed[source_id] = []
            _save_parsed_entries(
                config, source_id, [],
                reason="Fetched content was empty"
            )
            continue

        # Route to appropriate parser
        fmt = source.format.lower()
        if fmt == "markdown":
            entries = parse_markdown_changelog(content, source_id, source.name)
        elif fmt == "html":
            entries = parse_html_changelog(content, source_id, source.name)
        else:
            logger.warning(f"Unknown format '{fmt}' for {source_id}, trying markdown")
            entries = parse_markdown_changelog(content, source_id, source.name)

        all_parsed[source_id] = entries
        _save_parsed_entries(config, source_id, entries)

        logger.info(f"  Parsed {len(entries)} entries from {source_id}")

    total = sum(len(e) for e in all_parsed.values())
    logger.info(f"Total parsed entries across all sources: {total}")

    return all_parsed


def _save_parsed_entries(
    config: PipelineConfig,
    source_id: str,
    entries: list[dict],
    reason: str = "",
) -> None:
    """Save parsed entries to a per-source JSON file.

    Args:
        config: Pipeline configuration.
        source_id: Source identifier.
        entries: List of parsed entries.
        reason: Reason for empty result (if applicable).
    """
    output = {
        "source_id": source_id,
        "entry_count": len(entries),
        "entries": entries,
    }

    if not entries and reason:
        output["reason"] = reason

    output_path = config.parsed_changelogs_dir / f"{source_id}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)

    logger.debug(f"Saved {len(entries)} parsed entries to {output_path}")
