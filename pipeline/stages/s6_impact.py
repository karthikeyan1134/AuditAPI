"""Stage 6: Codebase impact analysis using LLM.

Sends high-risk Stripe entries and the codebase snippet to Gemini
for per-function impact analysis. Only runs if there are high-risk changes.
"""

import json
import logging
from pathlib import Path

from pipeline.config import PipelineConfig
from pipeline.llm_client import LLMClient

logger = logging.getLogger(__name__)


def analyze_codebase_impact(
    config: PipelineConfig,
    llm: LLMClient,
    high_risk_entries: list[dict],
) -> list[dict]:
    """Analyze impact of high-risk changes on the codebase snippet.

    Args:
        config: Pipeline configuration.
        llm: LLM client for the API call.
        high_risk_entries: Entries with critical/high breaking risk.

    Returns:
        List of per-function impact assessments.
    """
    # Load codebase snippet
    snippet_path = config.codebase_snippet_file
    codebase_snippet = snippet_path.read_text(encoding="utf-8")

    if not high_risk_entries:
        logger.info("No high-risk Stripe changes — writing empty impact result")
        result = {
            "has_impact": False,
            "explanation": (
                "No Stripe changes classified as critical or high breaking risk "
                "were found in the recent changelog entries. No codebase impact analysis needed."
            ),
            "affected_functions": [],
            "codebase_snippet_path": str(snippet_path),
        }
        _save_impact_result(config, result)
        return []

    logger.info(
        f"Analyzing codebase impact: {len(high_risk_entries)} high-risk entries "
        f"against {snippet_path}"
    )

    # Make the Stage 2 LLM call
    impact_results = llm.analyze_codebase_impact(
        high_risk_entries=high_risk_entries,
        codebase_snippet=codebase_snippet,
        snippet_path=str(snippet_path.name),
        input_artifacts=[
            "classified_changes.json",
            str(snippet_path.name),
        ],
        output_artifact="codebase_impact.json",
    )

    # Filter to only affected functions
    affected = [f for f in impact_results if f.get("affected", False)]

    result = {
        "has_impact": len(affected) > 0,
        "explanation": (
            f"{len(affected)} function(s) affected by high-risk breaking changes"
            if affected
            else "No functions directly affected by the breaking changes"
        ),
        "high_risk_entries_analyzed": len(high_risk_entries),
        "codebase_snippet_path": str(snippet_path.name),
        "affected_functions": impact_results,
    }

    _save_impact_result(config, result)

    logger.info(
        f"Impact analysis complete: {len(affected)}/{len(impact_results)} "
        f"functions affected"
    )

    return impact_results


def _save_impact_result(config: PipelineConfig, result: dict) -> None:
    """Save impact analysis result to codebase_impact.json."""
    output_path = config.output_dir / "codebase_impact.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)
    logger.info(f"Impact analysis saved to {output_path}")
