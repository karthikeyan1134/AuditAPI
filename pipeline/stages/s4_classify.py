"""Stage 4: Classify changes using LLM (one call per source).

Makes a separate Gemini API call for each source's recent entries.
Validates all LLM outputs against the controlled taxonomy before
saving to classified_changes.json.
"""

import json
import logging
from pathlib import Path

from pipeline.config import PipelineConfig
from pipeline.llm_client import LLMClient
from pipeline.taxonomy import get_taxonomy_description

logger = logging.getLogger(__name__)


def classify_all_sources(
    config: PipelineConfig,
    llm: LLMClient,
    filtered_entries: dict[str, list[dict]],
) -> dict[str, list[dict]]:
    """Classify entries for each source with a separate LLM call.

    Args:
        config: Pipeline configuration.
        llm: LLM client for Gemini API calls.
        filtered_entries: Dictionary mapping source_id to recent entries.

    Returns:
        Dictionary mapping source_id to classified entries.
    """
    taxonomy_desc = get_taxonomy_description()
    all_classified = {}

    for source in config.sources:
        source_id = source.source_id
        entries = filtered_entries.get(source_id, [])

        if not entries:
            logger.info(f"No entries to classify for {source_id}")
            all_classified[source_id] = []
            continue

        logger.info(
            f"Classifying {len(entries)} entries for {source_id} "
            f"(separate LLM call)"
        )

        classified = llm.classify_changes(
            source_id=source_id,
            source_name=source.name,
            entries=entries,
            taxonomy_description=taxonomy_desc,
            input_artifact=f"parsed_changelogs/{source_id}.json",
            output_artifact="classified_changes.json",
        )

        # Merge classification results back with original entry data
        classified_map = {c["entry_id"]: c for c in classified}
        merged = []
        for entry in entries:
            eid = entry["entry_id"]
            if eid in classified_map:
                merged_entry = {**entry, **classified_map[eid]}
                merged.append(merged_entry)
            else:
                logger.warning(f"Entry {eid} was not classified by LLM")
                # Include unclassified entry with defaults
                merged_entry = {
                    **entry,
                    "change_type": "enhancement",
                    "breaking_risk": "none",
                    "affects_auth": False,
                    "affects_billing": False,
                    "affects_data_model": False,
                    "rationale": "Not classified by LLM — default applied",
                    "validation_error": True,
                }
                merged.append(merged_entry)

        all_classified[source_id] = merged
        logger.info(f"  Classified {len(merged)} entries for {source_id}")

    # Save all classified changes to a single file
    _save_classified_changes(config, all_classified)

    return all_classified


def _save_classified_changes(
    config: PipelineConfig,
    all_classified: dict[str, list[dict]],
) -> None:
    """Save classified changes to classified_changes.json."""
    output = {
        "sources": {},
        "summary": {
            "total_classified": 0,
            "by_change_type": {},
            "by_breaking_risk": {},
        },
    }

    for source_id, entries in all_classified.items():
        output["sources"][source_id] = entries
        output["summary"]["total_classified"] += len(entries)

        for entry in entries:
            ct = entry.get("change_type", "unknown")
            br = entry.get("breaking_risk", "unknown")
            output["summary"]["by_change_type"][ct] = (
                output["summary"]["by_change_type"].get(ct, 0) + 1
            )
            output["summary"]["by_breaking_risk"][br] = (
                output["summary"]["by_breaking_risk"].get(br, 0) + 1
            )

    output_path = config.output_dir / "classified_changes.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)

    logger.info(
        f"Classified changes saved to {output_path} "
        f"({output['summary']['total_classified']} total)"
    )
