"""Stage 9: Generate the developer impact report.

Assembles impact_report.md from all pipeline stage outputs.
Includes executive summary, breaking changes, codebase impact,
migration guides, unaffected sources, and security alerts.
"""

import json
import logging
from datetime import date, datetime, timezone
from pathlib import Path

from pipeline.config import PipelineConfig

logger = logging.getLogger(__name__)


def generate_impact_report(
    config: PipelineConfig,
    filtered_entries: dict[str, list[dict]],
    all_classified: dict[str, list[dict]],
    impact_results: list[dict],
    migration_guides: list[dict],
    validation_results: list[dict],
    security_alerts: list[dict],
    high_risk_entries: list[dict],
) -> str:
    """Generate the complete developer impact report.

    Args:
        config: Pipeline configuration.
        filtered_entries: Recent entries after 90-day filter.
        all_classified: Classified entries by source.
        impact_results: Per-function impact analysis.
        migration_guides: Migration guides with before/after code.
        validation_results: Code validation results.
        security_alerts: Security-classified entries.
        high_risk_entries: High-risk Stripe entries.

    Returns:
        Path to the generated report.
    """
    # Compute statistics
    total_ingested = sum(len(e) for e in filtered_entries.values())
    total_recent = sum(len(e) for e in filtered_entries.values())

    breaking_count = 0
    high_risk_count = 0
    for entries in all_classified.values():
        for entry in entries:
            if entry.get("breaking_risk") in ("critical", "high"):
                high_risk_count += 1
            if entry.get("change_type") == "breaking":
                breaking_count += 1

    affected_functions = [f for f in impact_results if f.get("affected", False)]

    lines = []

    # Header
    lines.extend([
        "# Developer Impact Report",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Pipeline Version:** 1.0.0",
        f"**Lookback Window:** {config.lookback_days} days",
        "",
        "---",
        "",
    ])

    # Executive Summary
    lines.extend([
        "## Executive Summary",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total changes ingested | {total_ingested} |",
        f"| Recent entries (after {config.lookback_days}-day filter) | {total_recent} |",
        f"| Breaking or high-risk changes | {high_risk_count} |",
        f"| Affected functions | {len(affected_functions)} |",
        f"| Sources monitored | {len(config.sources)} |",
        f"| Security alerts | {len(security_alerts)} |",
        "",
    ])

    # Sources summary
    lines.extend([
        "### Sources Monitored",
        "",
    ])
    for source in config.sources:
        sid = source.source_id
        entry_count = len(all_classified.get(sid, []))
        status = f"{entry_count} entries classified" if entry_count > 0 else "No recent entries"
        lines.append(f"- **{source.name}** (`{sid}`): {status}")
    lines.append("")

    # Breaking Changes by Source
    lines.extend([
        "---",
        "",
        "## Breaking Changes by Source",
        "",
    ])

    has_breaking = False
    for source in config.sources:
        sid = source.source_id
        entries = all_classified.get(sid, [])
        breaking = [
            e for e in entries
            if e.get("change_type") == "breaking" or e.get("breaking_risk") in ("critical", "high")
        ]

        if breaking:
            has_breaking = True
            lines.extend([
                f"### {source.name}",
                "",
            ])
            for entry in breaking:
                risk = entry.get("breaking_risk", "unknown")
                emoji = "🔴" if risk == "critical" else "🟠" if risk == "high" else "🟡"
                lines.extend([
                    f"#### {emoji} {entry.get('change_title', 'Untitled')}",
                    "",
                    f"- **Entry ID:** `{entry.get('entry_id')}`",
                    f"- **Version:** {entry.get('version_or_date', 'N/A')}",
                    f"- **Type:** {entry.get('change_type')}",
                    f"- **Risk Level:** {risk}",
                    f"- **Affects Auth:** {entry.get('affects_auth', False)}",
                    f"- **Affects Billing:** {entry.get('affects_billing', False)}",
                    f"- **Affects Data Model:** {entry.get('affects_data_model', False)}",
                    f"- **Rationale:** {entry.get('rationale', 'N/A')}",
                    "",
                ])
            lines.append("")

    if not has_breaking:
        lines.extend([
            "No breaking or high-risk changes detected across any monitored source.",
            "",
        ])

    # Codebase Impact
    lines.extend([
        "---",
        "",
        "## Codebase Impact",
        "",
        f"**Snippet analyzed:** `{config.codebase_snippet_file.name}`",
        "",
    ])

    if not impact_results:
        lines.extend([
            "No high-risk Stripe changes found — codebase impact analysis was not required.",
            "",
        ])
    else:
        for func in impact_results:
            affected = func.get("affected", False)
            emoji = "⚠️" if affected else "✅"
            lines.extend([
                f"### {emoji} `{func.get('function_name', 'unknown')}`",
                "",
                f"- **Affected:** {'Yes' if affected else 'No'}",
                f"- **Detail:** {func.get('breaking_detail', 'N/A')}",
                f"- **Suggested Fix:** {func.get('suggested_fix_summary', 'N/A')}",
                f"- **Related Entries:** {', '.join(func.get('related_entry_ids', []))}",
                "",
            ])

    # Migration Guides
    lines.extend([
        "---",
        "",
        "## Migration Guides",
        "",
    ])

    if not migration_guides:
        lines.extend([
            "No migration guides were generated (no affected functions).",
            "",
        ])
    else:
        for guide in migration_guides:
            func_name = guide.get("function_name", "unknown")
            # Check validation status
            valid = any(
                v.get("function_name") == func_name and v.get("valid", False)
                for v in validation_results
            )
            status = "✅ Validated" if valid else "⚠️ Needs Review"

            lines.extend([
                f"### `{func_name}` — {status}",
                "",
                f"**Why:** {guide.get('explanation', 'N/A')}",
                "",
                "**Before:**",
                "```python",
                guide.get("before_code", "# No code"),
                "```",
                "",
                "**After:**",
                "```python",
                guide.get("after_code", "# No code"),
                "```",
                "",
            ])

    # Unaffected Sources
    lines.extend([
        "---",
        "",
        "## Unaffected Sources",
        "",
    ])

    unaffected = [
        s for s in config.sources
        if not any(
            e.get("change_type") == "breaking" or e.get("breaking_risk") in ("critical", "high")
            for e in all_classified.get(s.source_id, [])
        )
    ]

    if unaffected:
        for source in unaffected:
            entry_count = len(all_classified.get(source.source_id, []))
            lines.append(f"- **{source.name}**: {entry_count} changes, none breaking or high-risk")
    else:
        lines.append("All monitored sources had breaking or high-risk changes.")
    lines.append("")

    # Security Alerts
    lines.extend([
        "---",
        "",
        "## Security Alerts",
        "",
    ])

    if security_alerts:
        for alert in security_alerts:
            lines.extend([
                f"### 🔒 {alert.get('summary', 'Security Alert')}",
                "",
                f"- **Entry ID:** `{alert.get('entry_id')}`",
                f"- **Source:** `{alert.get('source_id')}`",
                f"- **Severity:** {alert.get('severity', 'Unknown')}",
                "",
            ])
    else:
        lines.append("No security-related changes detected.")
    lines.append("")

    # Version Pinning Recommendation
    version_pinning_path = config.output_dir / "version_pinning.md"
    if version_pinning_path.exists():
        lines.extend([
            "---",
            "",
            "## Version Pinning Recommendation",
            "",
            f"See [version_pinning.md](version_pinning.md) for detailed pinning recommendations.",
            "",
        ])

    # Footer
    lines.extend([
        "---",
        "",
        f"*Report generated by Changelog Monitoring Pipeline on {date.today().isoformat()}*",
        "",
    ])

    # Write report
    report_content = "\n".join(lines)
    output_path = config.output_dir / "impact_report.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    logger.info(f"Impact report saved to {output_path}")
    return str(output_path)
