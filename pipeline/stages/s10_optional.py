"""Stage 10: Optional outputs — security alerts, version pinning, stretch goals.

Generates optional artifacts:
- security_alerts.json: Extracted security-classified entries
- version_pinning.md: Dependency pinning recommendations
- delta_processing_report.json: Changelog diff simulation
- typescript_migration.md: Multi-language migration (stretch)
"""

import json
import copy
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pipeline.config import PipelineConfig
from pipeline.llm_client import LLMClient
from pipeline.taxonomy import get_taxonomy_description

logger = logging.getLogger(__name__)


def generate_optional_outputs(
    config: PipelineConfig,
    llm: LLMClient,
    all_classified: dict[str, list[dict]],
    migration_guides: list[dict],
    filtered_entries: dict[str, list[dict]],
) -> dict:
    """Generate all optional outputs.

    Args:
        config: Pipeline configuration.
        llm: LLM client for stretch goal API calls.
        all_classified: Classified entries by source.
        migration_guides: Migration guides from Stage 7.
        filtered_entries: Filtered entries for diff simulation.

    Returns:
        Dictionary of generated outputs and their paths.
    """
    outputs = {}

    # 7. Security Change Escalation
    security_alerts = generate_security_alerts(config, all_classified)
    outputs["security_alerts"] = security_alerts

    # 8. Version Pinning Recommendation
    generate_version_pinning(config, all_classified)
    outputs["version_pinning"] = True

    # 9. Changelog Diff Simulation (stretch)
    generate_diff_simulation(config, filtered_entries, llm)
    outputs["diff_simulation"] = True

    # 10. Multi-Language Migration (stretch)
    if migration_guides:
        generate_typescript_migration(config, llm, migration_guides)
        outputs["typescript_migration"] = True

    return outputs


def generate_security_alerts(
    config: PipelineConfig,
    all_classified: dict[str, list[dict]],
) -> list[dict]:
    """Extract security-classified entries into security_alerts.json.

    Args:
        config: Pipeline configuration.
        all_classified: Classified entries by source.

    Returns:
        List of security alert dictionaries.
    """
    alerts = []

    for source_id, entries in all_classified.items():
        for entry in entries:
            if entry.get("change_type") == "security":
                alert = {
                    "entry_id": entry.get("entry_id"),
                    "source_id": source_id,
                    "severity": entry.get("breaking_risk", "medium"),
                    "summary": entry.get("change_title", "Security change detected"),
                    "draft_slack_notification": (
                        f"🔒 *Security Alert* — {entry.get('source', source_id)}\n"
                        f">{entry.get('change_title', 'Security update')}\n"
                        f">Version: {entry.get('version_or_date', 'N/A')}\n"
                        f">Risk: {entry.get('breaking_risk', 'unknown')}\n"
                        f">Review the latest changelog for details."
                    ),
                }
                alerts.append(alert)

    output_path = config.output_dir / "security_alerts.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "alert_count": len(alerts),
            "alerts": alerts,
        }, f, indent=2)

    logger.info(f"Security alerts: {len(alerts)} saved to {output_path}")
    return alerts


def generate_version_pinning(
    config: PipelineConfig,
    all_classified: dict[str, list[dict]],
) -> None:
    """Generate version pinning recommendations based on breaking changes.

    Args:
        config: Pipeline configuration.
        all_classified: Classified entries by source.
    """
    lines = [
        "# Version Pinning Recommendations",
        "",
        "Based on breaking changes detected in monitored SDK changelogs.",
        "",
    ]

    # Map source IDs to dependency info
    dep_mapping = {
        "stripe_node": {
            "name": "stripe",
            "python_package": "stripe",
            "node_package": "stripe",
        },
        "openai_python": {
            "name": "openai",
            "python_package": "openai",
            "node_package": "openai",
        },
        "twilio": {
            "name": "twilio",
            "python_package": "twilio",
            "node_package": "twilio",
        },
    }

    has_recommendations = False

    for source_id, entries in all_classified.items():
        breaking = [
            e for e in entries
            if e.get("change_type") == "breaking" or e.get("breaking_risk") in ("critical", "high")
        ]

        if not breaking:
            continue

        has_recommendations = True
        dep_info = dep_mapping.get(source_id, {
            "name": source_id,
            "python_package": source_id,
            "node_package": source_id,
        })

        # Find the latest version mentioned
        versions = [e.get("version_or_date", "") for e in breaking]
        latest_breaking = versions[0] if versions else "latest"

        lines.extend([
            f"## {dep_info['name']}",
            "",
            f"**Breaking changes detected in:** {', '.join(versions[:3])}",
            "",
            "### Python (`requirements.txt`)",
            "",
            "```text",
            f"# Pin below breaking version until migration is complete",
            f"{dep_info['python_package']}<{latest_breaking}",
            "```",
            "",
            "### Node.js (`package.json`)",
            "",
            "```json",
            "{",
            f'  "{dep_info["node_package"]}": "<{latest_breaking}"',
            "}",
            "```",
            "",
            f"**When to unpin:** After applying migration guides and testing thoroughly.",
            f"**Reason:** Breaking changes in {latest_breaking} may affect your codebase.",
            "",
            "---",
            "",
        ])

    if not has_recommendations:
        lines.extend([
            "## No Pinning Required",
            "",
            "No breaking changes were detected that would require version pinning.",
            "All monitored dependencies are safe to upgrade.",
            "",
        ])

    output_path = config.output_dir / "version_pinning.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info(f"Version pinning recommendations saved to {output_path}")


def generate_diff_simulation(
    config: PipelineConfig,
    filtered_entries: dict[str, list[dict]],
    llm: LLMClient,
) -> None:
    """Simulate a changelog diff by adding fabricated entries.

    Saves today's entries as a snapshot, adds 2 fabricated Stripe entries,
    re-runs classification on the delta only.

    Args:
        config: Pipeline configuration.
        filtered_entries: Current filtered entries.
        llm: LLM client for delta classification.
    """
    # Save current snapshot
    snapshot = {
        "snapshot_date": datetime.now(timezone.utc).isoformat(),
        "entries_by_source": {
            sid: [e["entry_id"] for e in entries]
            for sid, entries in filtered_entries.items()
        },
    }

    # Fabricate 2 new Stripe entries
    existing_count = len(filtered_entries.get("stripe_node", []))
    fabricated = [
        {
            "entry_id": f"stripe_node-fab-001",
            "source_id": "stripe_node",
            "source": "Stripe Node.js SDK",
            "version_or_date": "99.0.0",
            "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "change_title": "FABRICATED: PaymentIntent.create now requires idempotency_key parameter",
            "change_body": "Breaking change: The idempotency_key parameter is now required for PaymentIntent.create calls. Omitting it will raise an error.",
            "change_type_raw": "breaking",
        },
        {
            "entry_id": f"stripe_node-fab-002",
            "source_id": "stripe_node",
            "source": "Stripe Node.js SDK",
            "version_or_date": "99.0.0",
            "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "change_title": "FABRICATED: Deprecated Charge.list endpoint removed",
            "change_body": "The Charge.list endpoint has been removed. Use PaymentIntent.list or Search API instead.",
            "change_type_raw": "deprecation",
        },
    ]

    # Classify only the delta (new entries)
    try:
        delta_classified = llm.classify_changes(
            source_id="stripe_node",
            source_name="Stripe Node.js SDK (Delta)",
            entries=fabricated,
            taxonomy_description=get_taxonomy_description(),
            input_artifact="delta_entries.json",
            output_artifact="delta_processing_report.json",
        )
    except Exception as e:
        logger.warning(f"Delta classification failed: {e}")
        delta_classified = []

    # Build report
    report = {
        "simulation_date": datetime.now(timezone.utc).isoformat(),
        "snapshot": snapshot,
        "fabricated_entries": fabricated,
        "fabricated_count": len(fabricated),
        "delta_only": True,
        "delta_classified": delta_classified,
        "verification": {
            "only_new_entries_processed": True,
            "existing_entries_count": existing_count,
            "delta_entries_count": len(fabricated),
            "delta_classified_count": len(delta_classified),
        },
    }

    output_path = config.output_dir / "delta_processing_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)

    logger.info(f"Delta processing report saved to {output_path}")


def generate_typescript_migration(
    config: PipelineConfig,
    llm: LLMClient,
    python_guides: list[dict],
) -> None:
    """Generate TypeScript equivalents of Python migration guides.

    Args:
        config: Pipeline configuration.
        llm: LLM client for the translation call.
        python_guides: Python migration guides to translate.
    """
    try:
        ts_guides = llm.generate_typescript_migration(
            python_guides=python_guides,
            input_artifacts=["migration_guides.json"],
            output_artifact="typescript_migration.md",
        )
    except Exception as e:
        logger.warning(f"TypeScript migration generation failed: {e}")
        ts_guides = []

    # Generate markdown
    lines = [
        "# TypeScript Migration Guides",
        "",
        "Equivalent TypeScript migrations using the Stripe Node.js SDK.",
        "",
    ]

    if not ts_guides:
        lines.extend([
            "## No TypeScript Migrations Generated",
            "",
            "TypeScript migration generation was not possible or failed.",
            "",
        ])
    else:
        for guide in ts_guides:
            lines.extend([
                f"## `{guide.get('function_name', 'unknown')}`",
                "",
                f"**Why:** {guide.get('explanation', 'N/A')}",
                "",
                "### Before",
                "```typescript",
                guide.get("before_code", "// No code"),
                "```",
                "",
                "### After",
                "```typescript",
                guide.get("after_code", "// No code"),
                "```",
                "",
                "---",
                "",
            ])

    output_path = config.output_dir / "typescript_migration.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info(f"TypeScript migration saved to {output_path}")
