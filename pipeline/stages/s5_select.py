"""Stage 5: Select high-risk Stripe changes for impact analysis.

Filters classified Stripe entries to only those with breaking_risk
of 'critical' or 'high'. This determines what gets sent to Stage 6.
"""

import logging

from pipeline.taxonomy import HIGH_RISK_LEVELS

logger = logging.getLogger(__name__)


def select_high_risk_stripe(
    all_classified: dict[str, list[dict]],
) -> list[dict]:
    """Select Stripe entries with critical or high breaking risk.

    Args:
        all_classified: All classified entries by source.

    Returns:
        List of high-risk Stripe entries.
    """
    stripe_entries = all_classified.get("stripe_node", [])

    if not stripe_entries:
        logger.info("No classified Stripe entries found")
        return []

    high_risk = [
        entry for entry in stripe_entries
        if entry.get("breaking_risk") in HIGH_RISK_LEVELS
    ]

    logger.info(
        f"Selected {len(high_risk)}/{len(stripe_entries)} Stripe entries "
        f"with breaking_risk in {HIGH_RISK_LEVELS}"
    )

    for entry in high_risk:
        logger.info(
            f"  ⚠ {entry['entry_id']}: {entry.get('change_type')} / "
            f"{entry.get('breaking_risk')} — {entry.get('change_title', '')[:80]}"
        )

    return high_risk
