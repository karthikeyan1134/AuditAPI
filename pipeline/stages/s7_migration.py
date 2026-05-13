"""Stage 7: Generate migration guides for affected functions.

Creates before/after code migration guides using the LLM.
Only generates guides for functions identified as affected in Stage 6.
"""

import json
import logging
from pathlib import Path

from pipeline.config import PipelineConfig
from pipeline.llm_client import LLMClient

logger = logging.getLogger(__name__)


def generate_migration_guides(
    config: PipelineConfig,
    llm: LLMClient,
    impact_results: list[dict],
) -> list[dict]:
    """Generate migration guides for affected functions.

    Args:
        config: Pipeline configuration.
        llm: LLM client for the API call.
        impact_results: Per-function impact results from Stage 6.

    Returns:
        List of migration guide dictionaries.
    """
    # Filter to only affected functions
    affected = [f for f in impact_results if f.get("affected", False)]

    if not affected:
        logger.info("No affected functions — writing empty migration guide")
        _save_migration_markdown(config, [], no_affected=True)
        return []

    # Load codebase snippet for context
    codebase_snippet = config.codebase_snippet_file.read_text(encoding="utf-8")

    logger.info(f"Generating migration guides for {len(affected)} affected functions")

    # Make the Stage 3 LLM call
    guides = llm.generate_migration_guides(
        affected_functions=affected,
        codebase_snippet=codebase_snippet,
        input_artifacts=[
            "codebase_impact.json",
            str(config.codebase_snippet_file.name),
        ],
        output_artifact="migration_guides.md",
    )

    # Save as markdown
    _save_migration_markdown(config, guides)

    # Also save as JSON for later stages
    guides_json_path = config.output_dir / "migration_guides.json"
    with open(guides_json_path, "w", encoding="utf-8") as f:
        json.dump(guides, f, indent=2)

    logger.info(f"Generated {len(guides)} migration guides")
    return guides


def _save_migration_markdown(
    config: PipelineConfig,
    guides: list[dict],
    no_affected: bool = False,
) -> None:
    """Save migration guides as a markdown document."""
    output_path = config.output_dir / "migration_guides.md"

    lines = [
        "# Migration Guides",
        "",
        "Auto-generated migration guides for functions affected by breaking SDK changes.",
        "",
    ]

    if no_affected:
        lines.extend([
            "## No Migrations Required",
            "",
            "No functions were identified as affected by the recent breaking changes.",
            "No migration action is needed at this time.",
            "",
        ])
    elif not guides:
        lines.extend([
            "## Migration Generation",
            "",
            "Migration guide generation was attempted but produced no results.",
            "",
        ])
    else:
        for guide in guides:
            func_name = guide.get("function_name", "unknown")
            explanation = guide.get("explanation", "")
            before = guide.get("before_code", "")
            after = guide.get("after_code", "")

            lines.extend([
                f"## `{func_name}`",
                "",
                f"**Why:** {explanation}",
                "",
                "### Before (Current Implementation)",
                "",
                "```python",
                before,
                "```",
                "",
                "### After (Migrated Implementation)",
                "",
                "```python",
                after,
                "```",
                "",
                "---",
                "",
            ])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info(f"Migration guides saved to {output_path}")
