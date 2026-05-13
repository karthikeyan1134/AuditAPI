"""Stage 3: Filter parsed entries to the last 90 days.

Applies the date-based lookback filter deterministically before any LLM
classification. Entries older than the lookback window are discarded.
Sources with no recent entries get an explicit empty result with a reason.
"""

import json
import logging
from datetime import date, timedelta
from pathlib import Path

from pipeline.config import PipelineConfig

logger = logging.getLogger(__name__)


def filter_recent_entries(
    config: PipelineConfig,
    all_parsed: dict[str, list[dict]],
) -> dict[str, list[dict]]:
    """Filter all parsed entries to the configured lookback window.

    Args:
        config: Pipeline configuration (includes lookback_days).
        all_parsed: Dictionary mapping source_id to parsed entries.

    Returns:
        Dictionary mapping source_id to filtered (recent) entries.
        Entries without parseable dates are INCLUDED (benefit of the doubt).
    """
    cutoff = date.today() - timedelta(days=config.lookback_days)
    cutoff_str = cutoff.isoformat()

    logger.info(
        f"Filtering entries to last {config.lookback_days} days "
        f"(cutoff: {cutoff_str})"
    )

    filtered = {}

    for source_id, entries in all_parsed.items():
        before_count = len(entries)
        recent = []
        skipped = 0
        no_date = 0

        for entry in entries:
            published_at = entry.get("published_at")

            if published_at is None:
                # No date available — include it (benefit of the doubt)
                recent.append(entry)
                no_date += 1
                continue

            try:
                entry_date = date.fromisoformat(published_at)
                if entry_date >= cutoff:
                    recent.append(entry)
                else:
                    skipped += 1
            except (ValueError, TypeError):
                # Unparseable date — include it
                recent.append(entry)
                no_date += 1

        filtered[source_id] = recent

        # Update the saved parsed changelog file with filter info
        _update_parsed_file_with_filter(config, source_id, recent, before_count, skipped, no_date)

        if recent:
            logger.info(
                f"  {source_id}: {before_count} → {len(recent)} entries "
                f"({skipped} older, {no_date} without date)"
            )
        else:
            reason = (
                f"No entries within {config.lookback_days}-day window. "
                f"{before_count} total entries, {skipped} older than {cutoff_str}."
            )
            logger.info(f"  {source_id}: {reason}")

    total_before = sum(len(e) for e in all_parsed.values())
    total_after = sum(len(e) for e in filtered.values())
    logger.info(
        f"Filter complete: {total_before} → {total_after} entries "
        f"({total_before - total_after} discarded)"
    )

    return filtered


def _update_parsed_file_with_filter(
    config: PipelineConfig,
    source_id: str,
    recent_entries: list[dict],
    total_before: int,
    skipped: int,
    no_date: int,
) -> None:
    """Update the parsed changelog file with filter results.

    Overwrites the parsed file to contain only recent entries,
    preserving the audit trail with filter metadata.
    """
    output_path = config.parsed_changelogs_dir / f"{source_id}.json"

    output = {
        "source_id": source_id,
        "entry_count": len(recent_entries),
        "filter_applied": True,
        "filter_lookback_days": config.lookback_days,
        "filter_cutoff": (date.today() - timedelta(days=config.lookback_days)).isoformat(),
        "total_before_filter": total_before,
        "entries_discarded": skipped,
        "entries_without_date": no_date,
        "entries": recent_entries,
    }

    if not recent_entries:
        output["reason"] = (
            f"No entries within {config.lookback_days}-day window "
            f"(cutoff: {output['filter_cutoff']})"
        )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)
