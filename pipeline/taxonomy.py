"""Controlled taxonomy definitions and validation.

Defines the allowed change types, breaking risk levels, and classification
fields as specified by the pipeline requirements. All LLM outputs are
validated against these enums before being accepted.
"""

from enum import Enum
from typing import Any


class ChangeType(str, Enum):
    """Allowed change type categories."""
    DEPRECATION = "deprecation"
    BREAKING = "breaking"
    ENHANCEMENT = "enhancement"
    BUGFIX = "bugfix"
    SECURITY = "security"


class BreakingRisk(str, Enum):
    """Allowed breaking risk levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


# Sets for fast membership testing
VALID_CHANGE_TYPES = {e.value for e in ChangeType}
VALID_RISK_LEVELS = {e.value for e in BreakingRisk}

# High-risk levels that trigger codebase impact analysis
HIGH_RISK_LEVELS = {BreakingRisk.CRITICAL.value, BreakingRisk.HIGH.value}

# Required fields in a parsed changelog entry
PARSED_ENTRY_REQUIRED_FIELDS = [
    "entry_id",
    "source_id",
    "source",
    "version_or_date",
    "published_at",
    "change_title",
    "change_body",
    "change_type_raw",
]

# Required fields in a classified entry
CLASSIFICATION_REQUIRED_FIELDS = [
    "entry_id",
    "change_type",
    "breaking_risk",
    "affects_auth",
    "affects_billing",
    "affects_data_model",
    "rationale",
]

# Required fields in a codebase impact entry
IMPACT_REQUIRED_FIELDS = [
    "function_name",
    "affected",
    "breaking_detail",
    "suggested_fix_summary",
    "related_entry_ids",
]


def validate_classification(entry: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a classified entry against the controlled taxonomy.

    Returns:
        Tuple of (is_valid, list_of_errors).
    """
    errors = []

    # Check required fields exist
    for field in CLASSIFICATION_REQUIRED_FIELDS:
        if field not in entry:
            errors.append(f"Missing required field: {field}")

    if errors:
        return False, errors

    # Validate enum values
    if entry["change_type"] not in VALID_CHANGE_TYPES:
        errors.append(
            f"Invalid change_type: '{entry['change_type']}'. "
            f"Must be one of: {VALID_CHANGE_TYPES}"
        )

    if entry["breaking_risk"] not in VALID_RISK_LEVELS:
        errors.append(
            f"Invalid breaking_risk: '{entry['breaking_risk']}'. "
            f"Must be one of: {VALID_RISK_LEVELS}"
        )

    # Validate boolean fields
    for bool_field in ["affects_auth", "affects_billing", "affects_data_model"]:
        if not isinstance(entry[bool_field], bool):
            errors.append(f"Field '{bool_field}' must be boolean, got {type(entry[bool_field]).__name__}")

    # Validate rationale is a non-empty string
    if not isinstance(entry.get("rationale"), str) or not entry["rationale"].strip():
        errors.append("Field 'rationale' must be a non-empty string")

    return len(errors) == 0, errors


def validate_parsed_entry(entry: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a parsed changelog entry has all required fields.

    Returns:
        Tuple of (is_valid, list_of_errors).
    """
    errors = []
    for field in PARSED_ENTRY_REQUIRED_FIELDS:
        if field not in entry:
            errors.append(f"Missing required field: {field}")

    if "entry_id" in entry and not isinstance(entry["entry_id"], str):
        errors.append("entry_id must be a string")

    if "source_id" in entry and not isinstance(entry["source_id"], str):
        errors.append("source_id must be a string")

    return len(errors) == 0, errors


def validate_impact_entry(entry: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a codebase impact entry has all required fields.

    Returns:
        Tuple of (is_valid, list_of_errors).
    """
    errors = []
    for field in IMPACT_REQUIRED_FIELDS:
        if field not in entry:
            errors.append(f"Missing required field: {field}")

    if "affected" in entry and not isinstance(entry["affected"], bool):
        errors.append("'affected' must be boolean")

    if "related_entry_ids" in entry and not isinstance(entry["related_entry_ids"], list):
        errors.append("'related_entry_ids' must be a list")

    return len(errors) == 0, errors


def get_taxonomy_description() -> str:
    """Return a human-readable description of the taxonomy for LLM prompts."""
    return """CONTROLLED TAXONOMY — You MUST use ONLY these values:

Change Types (pick exactly one):
- deprecation: Feature or API marked for future removal
- breaking: Backward-incompatible change that will break existing code
- enhancement: New feature or improvement (backward-compatible)
- bugfix: Fix for an existing bug
- security: Security-related fix or improvement

Breaking Risk Levels (pick exactly one):
- critical: Will break production code immediately on upgrade
- high: Likely to break code that uses affected APIs
- medium: May break code in specific edge cases
- low: Unlikely to break code but worth noting
- none: No breaking risk

Boolean Classification Fields:
- affects_auth: Does this change affect authentication or authorization?
- affects_billing: Does this change affect billing, payments, or pricing?
- affects_data_model: Does this change affect data models, schemas, or data formats?

DO NOT invent new categories. If a change doesn't fit, use the closest match and explain in rationale."""
