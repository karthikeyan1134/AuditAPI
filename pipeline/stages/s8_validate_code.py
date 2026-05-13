"""Stage 8: Validate generated migration code using Python AST.

Extracts after-code blocks from migration guides and validates them
as syntactically valid Python using ast.parse(). Results are saved
to migration_validation.json.
"""

import ast
import json
import logging
from pathlib import Path

from pipeline.config import PipelineConfig

logger = logging.getLogger(__name__)


def validate_migration_code(
    config: PipelineConfig,
    migration_guides: list[dict],
) -> list[dict]:
    """Validate that all generated after-code is syntactically valid Python.

    Args:
        config: Pipeline configuration.
        migration_guides: List of migration guide dictionaries with after_code.

    Returns:
        List of validation result dictionaries.
    """
    results = []

    if not migration_guides:
        logger.info("No migration guides to validate")
        _save_validation_results(config, results, summary="No migration guides generated")
        return results

    valid_count = 0
    invalid_count = 0

    for guide in migration_guides:
        func_name = guide.get("function_name", "unknown")
        after_code = guide.get("after_code", "")

        validation = {
            "function_name": func_name,
            "has_after_code": bool(after_code),
            "valid": False,
            "error": None,
            "ready_to_apply": False,
        }

        if not after_code:
            validation["error"] = "No after_code provided"
            invalid_count += 1
            results.append(validation)
            continue

        # Validate using ast.parse
        try:
            ast.parse(after_code)
            validation["valid"] = True
            validation["ready_to_apply"] = True
            valid_count += 1
            logger.info(f"  ✓ {func_name}: valid Python syntax")
        except SyntaxError as e:
            validation["error"] = f"SyntaxError: {e.msg} (line {e.lineno})"
            validation["ready_to_apply"] = False
            invalid_count += 1
            logger.warning(f"  ✗ {func_name}: {validation['error']}")

        results.append(validation)

    summary = (
        f"{valid_count} valid, {invalid_count} invalid "
        f"out of {len(migration_guides)} migration guides"
    )
    _save_validation_results(config, results, summary=summary)

    logger.info(f"Migration validation: {summary}")
    return results


def _save_validation_results(
    config: PipelineConfig,
    results: list[dict],
    summary: str = "",
) -> None:
    """Save validation results to migration_validation.json."""
    output = {
        "summary": summary,
        "all_valid": all(r.get("valid", False) for r in results) if results else True,
        "total_guides": len(results),
        "valid_count": sum(1 for r in results if r.get("valid", False)),
        "invalid_count": sum(1 for r in results if not r.get("valid", False)),
        "results": results,
    }

    output_path = config.output_dir / "migration_validation.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    logger.info(f"Validation results saved to {output_path}")
