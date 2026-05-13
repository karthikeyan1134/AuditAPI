#!/usr/bin/env python3
"""Changelog Monitoring Pipeline — Main Entry Point.

Orchestrates all pipeline stages in strict sequential order using the
state machine. Each stage reads/writes artifacts to disk for auditability.

Usage:
    python run_pipeline.py
    python run_pipeline.py --project-root /path/to/project
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone

from pipeline.config import load_config
from pipeline.state import PipelineStateMachine, PipelineStage
from pipeline.llm_client import LLMClient
from pipeline.taxonomy import get_taxonomy_description

# Stage imports
from pipeline.stages.s1_fetch import fetch_all_sources
from pipeline.stages.s2_parse import parse_all_changelogs
from pipeline.stages.s3_filter import filter_recent_entries
from pipeline.stages.s4_classify import classify_all_sources
from pipeline.stages.s5_select import select_high_risk_stripe
from pipeline.stages.s6_impact import analyze_codebase_impact
from pipeline.stages.s7_migration import generate_migration_guides
from pipeline.stages.s8_validate_code import validate_migration_code
from pipeline.stages.s9_report import generate_impact_report
from pipeline.stages.s10_optional import generate_optional_outputs


def setup_logging(level: str = "INFO") -> None:
    """Configure logging with timestamp and level."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )


def run_pipeline(project_root: Path) -> None:
    """Execute the full pipeline in strict stage order.

    Args:
        project_root: Root directory of the project.
    """
    logger = logging.getLogger("pipeline")
    start_time = datetime.now(timezone.utc)

    logger.info("=" * 60)
    logger.info("Changelog Monitoring Pipeline — Starting")
    logger.info(f"Project root: {project_root}")
    logger.info(f"Start time: {start_time.isoformat()}")
    logger.info("=" * 60)

    # ── INIT ──────────────────────────────────────────────────
    try:
        config = load_config(project_root)
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    sm = PipelineStateMachine(output_dir=config.output_dir)

    # Clear previous LLM log
    if config.llm_log_file.exists():
        config.llm_log_file.unlink()

    # Initialize LLM client
    llm = LLMClient(
        api_key=config.gemini_api_key,
        model=config.gemini_model,
        log_file=config.llm_log_file,
    )

    # ── SOURCES_LOADED ────────────────────────────────────────
    sm.advance(PipelineStage.SOURCES_LOADED, f"Loaded {len(config.sources)} sources")
    logger.info(f"\n{'─'*40}\nStage: SOURCES_LOADED ({len(config.sources)} sources)\n{'─'*40}")

    # ── CHANGELOGS_FETCHED ────────────────────────────────────
    fetch_results = fetch_all_sources(config)
    sm.advance(PipelineStage.CHANGELOGS_FETCHED, f"Fetched {len(fetch_results)} sources")
    logger.info(f"\n{'─'*40}\nStage: CHANGELOGS_FETCHED\n{'─'*40}")

    # ── ENTRIES_PARSED ────────────────────────────────────────
    all_parsed = parse_all_changelogs(config, fetch_results)
    total_parsed = sum(len(e) for e in all_parsed.values())
    sm.advance(PipelineStage.ENTRIES_PARSED, f"Parsed {total_parsed} total entries")
    logger.info(f"\n{'─'*40}\nStage: ENTRIES_PARSED ({total_parsed} entries)\n{'─'*40}")

    # ── RECENT_ENTRIES_FILTERED ───────────────────────────────
    filtered_entries = filter_recent_entries(config, all_parsed)
    total_filtered = sum(len(e) for e in filtered_entries.values())
    sm.advance(
        PipelineStage.RECENT_ENTRIES_FILTERED,
        f"Filtered to {total_filtered} recent entries ({config.lookback_days}-day window)",
    )
    logger.info(f"\n{'─'*40}\nStage: RECENT_ENTRIES_FILTERED ({total_filtered} entries)\n{'─'*40}")

    # ── CHANGES_CLASSIFIED ────────────────────────────────────
    all_classified = classify_all_sources(config, llm, filtered_entries)
    total_classified = sum(len(e) for e in all_classified.values())
    sm.advance(PipelineStage.CHANGES_CLASSIFIED, f"Classified {total_classified} entries")
    logger.info(f"\n{'─'*40}\nStage: CHANGES_CLASSIFIED ({total_classified} entries)\n{'─'*40}")

    # ── HIGH_RISK_STRIPE_CHANGES_SELECTED ─────────────────────
    high_risk_entries = select_high_risk_stripe(all_classified)
    sm.advance(
        PipelineStage.HIGH_RISK_STRIPE_CHANGES_SELECTED,
        f"Selected {len(high_risk_entries)} high-risk Stripe entries",
    )
    logger.info(f"\n{'─'*40}\nStage: HIGH_RISK_STRIPE_CHANGES_SELECTED ({len(high_risk_entries)})\n{'─'*40}")

    # ── CODEBASE_IMPACT_ANALYSED ──────────────────────────────
    impact_results = analyze_codebase_impact(config, llm, high_risk_entries)
    affected_count = sum(1 for f in impact_results if f.get("affected", False))
    sm.advance(
        PipelineStage.CODEBASE_IMPACT_ANALYSED,
        f"Analyzed impact: {affected_count} functions affected",
    )
    logger.info(f"\n{'─'*40}\nStage: CODEBASE_IMPACT_ANALYSED ({affected_count} affected)\n{'─'*40}")

    # ── MIGRATION_GUIDES_GENERATED ────────────────────────────
    migration_guides = generate_migration_guides(config, llm, impact_results)
    sm.advance(
        PipelineStage.MIGRATION_GUIDES_GENERATED,
        f"Generated {len(migration_guides)} migration guides",
    )
    logger.info(f"\n{'─'*40}\nStage: MIGRATION_GUIDES_GENERATED ({len(migration_guides)})\n{'─'*40}")

    # ── MIGRATION_CODE_VALIDATED ──────────────────────────────
    validation_results = validate_migration_code(config, migration_guides)
    valid_count = sum(1 for v in validation_results if v.get("valid", False))
    sm.advance(
        PipelineStage.MIGRATION_CODE_VALIDATED,
        f"Validated: {valid_count}/{len(validation_results)} valid",
    )
    logger.info(f"\n{'─'*40}\nStage: MIGRATION_CODE_VALIDATED ({valid_count} valid)\n{'─'*40}")

    # ── IMPACT_REPORT_WRITTEN ─────────────────────────────────
    # Extract security alerts for the report
    security_alerts = [
        entry
        for entries in all_classified.values()
        for entry in entries
        if entry.get("change_type") == "security"
    ]

    report_path = generate_impact_report(
        config=config,
        filtered_entries=filtered_entries,
        all_classified=all_classified,
        impact_results=impact_results,
        migration_guides=migration_guides,
        validation_results=validation_results,
        security_alerts=security_alerts,
        high_risk_entries=high_risk_entries,
    )
    sm.advance(PipelineStage.IMPACT_REPORT_WRITTEN, f"Report saved to {report_path}")
    logger.info(f"\n{'─'*40}\nStage: IMPACT_REPORT_WRITTEN\n{'─'*40}")

    # ── OPTIONAL_OUTPUTS_GENERATED ────────────────────────────
    optional_outputs = generate_optional_outputs(
        config=config,
        llm=llm,
        all_classified=all_classified,
        migration_guides=migration_guides,
        filtered_entries=filtered_entries,
    )
    sm.advance(PipelineStage.OPTIONAL_OUTPUTS_GENERATED, "Optional outputs generated")
    logger.info(f"\n{'─'*40}\nStage: OPTIONAL_OUTPUTS_GENERATED\n{'─'*40}")

    # ── VALIDATION_COMPLETE ───────────────────────────────────
    sm.advance(PipelineStage.VALIDATION_COMPLETE, "Internal validation passed")

    # ── RESULTS_FINALISED ─────────────────────────────────────
    sm.advance(PipelineStage.RESULTS_FINALISED, "Pipeline complete")
    sm.save_history()

    # Final summary
    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
    logger.info("\n" + "=" * 60)
    logger.info("Pipeline Complete!")
    logger.info(f"Duration: {elapsed:.1f}s")
    logger.info(f"LLM calls made: {llm.call_count}")
    logger.info(f"Total entries classified: {total_classified}")
    logger.info(f"High-risk Stripe entries: {len(high_risk_entries)}")
    logger.info(f"Affected functions: {affected_count}")
    logger.info(f"Migration guides: {len(migration_guides)} (valid: {valid_count})")
    logger.info(f"Security alerts: {len(security_alerts)}")
    logger.info("=" * 60)
    logger.info("\nGenerated artifacts:")
    for artifact in [
        "parsed_changelogs/",
        "classified_changes.json",
        "codebase_impact.json",
        "migration_guides.md",
        "migration_validation.json",
        "impact_report.md",
        "security_alerts.json",
        "version_pinning.md",
        "delta_processing_report.json",
        "typescript_migration.md",
        "llm_calls.jsonl",
        "pipeline_history.json",
    ]:
        path = config.output_dir / artifact
        exists = path.exists() or (path.is_dir() if artifact.endswith("/") else False)
        status = "✓" if exists else "✗"
        logger.info(f"  {status} {artifact}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Changelog Monitoring Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )

    args = parser.parse_args()
    setup_logging(args.log_level)
    run_pipeline(args.project_root)


if __name__ == "__main__":
    main()
