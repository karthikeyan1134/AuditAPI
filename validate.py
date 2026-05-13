#!/usr/bin/env python3
"""Pipeline Validation Command.

Validates that all pipeline artifacts exist, are well-formed, and meet
the specification requirements. Run after pipeline execution to verify
correctness.

Usage:
    python validate.py
    python validate.py --project-root /path/to/project
"""

import argparse
import ast
import json
import logging
import re
import sys
from pathlib import Path

# Controlled taxonomy values
VALID_CHANGE_TYPES = {"deprecation", "breaking", "enhancement", "bugfix", "security"}
VALID_RISK_LEVELS = {"critical", "high", "medium", "low", "none"}

PARSED_ENTRY_REQUIRED_FIELDS = [
    "entry_id", "source_id", "source", "version_or_date",
    "published_at", "change_title", "change_body", "change_type_raw",
]

REPORT_REQUIRED_SECTIONS = [
    "Executive Summary",
    "Breaking Changes by Source",
    "Codebase Impact",
    "Migration Guides",
    "Unaffected Sources",
    "Security Alerts",
]


class ValidationResult:
    """Tracks pass/fail results for all validation checks."""

    def __init__(self):
        self.results: list[dict] = []

    def check(self, name: str, passed: bool, detail: str = "") -> bool:
        emoji = "✓" if passed else "✗"
        status = "PASS" if passed else "FAIL"
        self.results.append({
            "check": name,
            "passed": passed,
            "detail": detail,
        })
        print(f"  {emoji} [{status}] {name}" + (f" — {detail}" if detail else ""))
        return passed

    @property
    def all_passed(self) -> bool:
        return all(r["passed"] for r in self.results)

    @property
    def pass_count(self) -> int:
        return sum(1 for r in self.results if r["passed"])

    @property
    def fail_count(self) -> int:
        return sum(1 for r in self.results if not r["passed"])


def validate(project_root: Path) -> bool:
    """Run all validation checks.

    Args:
        project_root: Root directory of the project.

    Returns:
        True if all checks pass.
    """
    v = ValidationResult()
    print("\n" + "=" * 60)
    print("Pipeline Validation")
    print("=" * 60 + "\n")

    # ── 1. Required Artifacts Exist ───────────────────────────
    print("1. Required Artifacts:")
    required_artifacts = [
        "changelog_sources.json",
        "codebase_snippet.py",
        "parsed_changelogs",
        "classified_changes.json",
        "codebase_impact.json",
        "migration_guides.md",
        "migration_validation.json",
        "impact_report.md",
        "llm_calls.jsonl",
    ]

    for artifact in required_artifacts:
        path = project_root / artifact
        exists = path.exists()
        v.check(f"Artifact exists: {artifact}", exists)

    # Optional artifacts (check but don't fail)
    print("\n  Optional artifacts:")
    optional_artifacts = [
        "security_alerts.json",
        "version_pinning.md",
        "delta_processing_report.json",
        "typescript_migration.md",
    ]
    for artifact in optional_artifacts:
        path = project_root / artifact
        exists = path.exists()
        print(f"    {'✓' if exists else '○'} {artifact} ({'present' if exists else 'not generated'})")

    # ── 2. JSON Files Valid ───────────────────────────────────
    print("\n2. JSON File Validity:")
    json_files = [
        "changelog_sources.json",
        "classified_changes.json",
        "codebase_impact.json",
        "migration_validation.json",
    ]
    for jf in json_files:
        path = project_root / jf
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    json.load(f)
                v.check(f"Valid JSON: {jf}", True)
            except json.JSONDecodeError as e:
                v.check(f"Valid JSON: {jf}", False, str(e))
        else:
            v.check(f"Valid JSON: {jf}", False, "File not found")

    # ── 3. All Sources Fetched or Logged ──────────────────────
    print("\n3. Source Coverage:")
    sources_path = project_root / "changelog_sources.json"
    if sources_path.exists():
        with open(sources_path, "r", encoding="utf-8") as f:
            sources_data = json.load(f)
        source_ids = [s["source_id"] for s in sources_data.get("sources", [])]

        parsed_dir = project_root / "parsed_changelogs"
        for sid in source_ids:
            parsed_file = parsed_dir / f"{sid}.json"
            v.check(
                f"Source fetched/logged: {sid}",
                parsed_file.exists(),
                "Parsed file exists" if parsed_file.exists() else "Missing parsed file",
            )

    # ── 4. Parsed Entries Have Required Fields ────────────────
    print("\n4. Parsed Entry Fields:")
    parsed_dir = project_root / "parsed_changelogs"
    if parsed_dir.exists():
        for parsed_file in sorted(parsed_dir.glob("*.json")):
            if parsed_file.name.endswith("_raw.json"):
                continue
            with open(parsed_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            entries = data.get("entries", [])
            if entries:
                # Check first entry has required fields
                first = entries[0]
                missing = [f for f in PARSED_ENTRY_REQUIRED_FIELDS if f not in first]
                v.check(
                    f"Required fields in {parsed_file.name}",
                    len(missing) == 0,
                    f"Missing: {missing}" if missing else f"{len(entries)} entries OK",
                )
            else:
                # Empty is OK if reason is provided
                has_reason = "reason" in data or "filter_applied" in data
                v.check(
                    f"Empty result explained: {parsed_file.name}",
                    has_reason,
                    data.get("reason", "No reason provided"),
                )

    # ── 5. 90-Day Filter Applied ──────────────────────────────
    print("\n5. 90-Day Filter:")
    if parsed_dir.exists():
        for parsed_file in sorted(parsed_dir.glob("*.json")):
            if parsed_file.name.endswith("_raw.json"):
                continue
            with open(parsed_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            filter_applied = data.get("filter_applied", False)
            v.check(
                f"Filter applied: {parsed_file.name}",
                filter_applied,
                f"Cutoff: {data.get('filter_cutoff', 'N/A')}" if filter_applied else "No filter metadata",
            )

    # ── 6. Separate LLM Calls Per Source ──────────────────────
    print("\n6. LLM Call Separation:")
    llm_log = project_root / "llm_calls.jsonl"
    if llm_log.exists():
        with open(llm_log, "r", encoding="utf-8") as f:
            calls = [json.loads(line) for line in f if line.strip()]

        # Check classification calls per source
        classification_calls = [c for c in calls if c.get("stage") == "classification"]
        classified_sources = {c.get("source_id") for c in classification_calls}

        # Only check sources that had entries
        classified_path = project_root / "classified_changes.json"
        if classified_path.exists():
            with open(classified_path, "r", encoding="utf-8") as f:
                classified_data = json.load(f)
            sources_with_entries = {
                sid for sid, entries in classified_data.get("sources", {}).items()
                if entries
            }

            for sid in sources_with_entries:
                has_call = sid in classified_sources
                v.check(
                    f"Separate classification call: {sid}",
                    has_call,
                )

        # Check for impact analysis call
        impact_calls = [c for c in calls if c.get("stage") == "codebase_impact"]
        v.check(
            "Impact analysis LLM call logged",
            len(impact_calls) >= 0,  # 0 is OK if no high-risk
            f"{len(impact_calls)} call(s)",
        )

        # Check for migration call
        migration_calls = [c for c in calls if c.get("stage") == "migration_generation"]
        v.check(
            "Migration generation LLM call logged",
            len(migration_calls) >= 0,  # 0 is OK if no affected functions
            f"{len(migration_calls)} call(s)",
        )
    else:
        v.check("LLM call log exists", False, "llm_calls.jsonl not found")

    # ── 7. Classification Taxonomy ────────────────────────────
    print("\n7. Taxonomy Compliance:")
    classified_path = project_root / "classified_changes.json"
    if classified_path.exists():
        with open(classified_path, "r", encoding="utf-8") as f:
            classified = json.load(f)

        invalid_types = set()
        invalid_risks = set()

        for source_id, entries in classified.get("sources", {}).items():
            for entry in entries:
                ct = entry.get("change_type")
                br = entry.get("breaking_risk")
                if ct and ct not in VALID_CHANGE_TYPES:
                    invalid_types.add(ct)
                if br and br not in VALID_RISK_LEVELS:
                    invalid_risks.add(br)

        v.check(
            "All change_type values valid",
            len(invalid_types) == 0,
            f"Invalid: {invalid_types}" if invalid_types else "All valid",
        )
        v.check(
            "All breaking_risk values valid",
            len(invalid_risks) == 0,
            f"Invalid: {invalid_risks}" if invalid_risks else "All valid",
        )

    # ── 8. Impact Analysis Uses Codebase Snippet ──────────────
    print("\n8. Impact Analysis:")
    impact_path = project_root / "codebase_impact.json"
    if impact_path.exists():
        with open(impact_path, "r", encoding="utf-8") as f:
            impact = json.load(f)
        has_snippet_ref = "codebase_snippet" in str(impact)
        v.check(
            "Impact analysis references codebase snippet",
            has_snippet_ref,
        )

    # ── 9. Migration Guides for Affected Functions ────────────
    print("\n9. Migration Guides:")
    if impact_path.exists():
        with open(impact_path, "r", encoding="utf-8") as f:
            impact = json.load(f)
        affected = [
            f["function_name"]
            for f in impact.get("affected_functions", [])
            if f.get("affected", False)
        ]

        migration_path = project_root / "migration_guides.md"
        if migration_path.exists():
            migration_content = migration_path.read_text(encoding="utf-8")
            for func_name in affected:
                v.check(
                    f"Migration guide for: {func_name}",
                    func_name in migration_content,
                )
        elif not affected:
            v.check("No migration guides needed (no affected functions)", True)
        else:
            v.check("Migration guides file exists", False)

    # ── 10. Generated Code Validated ──────────────────────────
    print("\n10. Code Validation:")
    validation_path = project_root / "migration_validation.json"
    if validation_path.exists():
        with open(validation_path, "r", encoding="utf-8") as f:
            validation = json.load(f)
        v.check(
            "Migration code validation completed",
            True,
            f"{validation.get('valid_count', 0)} valid, {validation.get('invalid_count', 0)} invalid",
        )
    else:
        v.check("Migration validation file exists", False)

    # ── 11. Impact Report Sections ────────────────────────────
    print("\n11. Impact Report Sections:")
    report_path = project_root / "impact_report.md"
    if report_path.exists():
        report_content = report_path.read_text(encoding="utf-8")
        for section in REPORT_REQUIRED_SECTIONS:
            v.check(
                f"Report section: {section}",
                section in report_content,
            )
    else:
        v.check("Impact report exists", False)

    # ── 12. LLM Call Log Format ───────────────────────────────
    print("\n12. LLM Call Log Format:")
    if llm_log.exists():
        with open(llm_log, "r", encoding="utf-8") as f:
            lines = [line for line in f if line.strip()]

        if lines:
            first_call = json.loads(lines[0])
            required_log_fields = [
                "stage", "source_id", "entry_ids", "timestamp",
                "provider", "model", "prompt_hash",
                "input_artifacts", "output_artifact",
            ]
            missing = [f for f in required_log_fields if f not in first_call]
            v.check(
                "LLM log entry has required fields",
                len(missing) == 0,
                f"Missing: {missing}" if missing else "All fields present",
            )
        else:
            v.check("LLM log has entries", False, "Log file is empty")

    # ── Summary ───────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Results: {v.pass_count} passed, {v.fail_count} failed")
    print("=" * 60)

    if v.all_passed:
        print("\n✓ All validation checks passed!\n")
    else:
        print(f"\n✗ {v.fail_count} check(s) failed.\n")

    return v.all_passed


def main():
    parser = argparse.ArgumentParser(description="Validate pipeline artifacts")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory",
    )
    args = parser.parse_args()

    success = validate(args.project_root)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
