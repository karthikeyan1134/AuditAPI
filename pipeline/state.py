"""Pipeline state machine enforcing strict stage ordering.

The pipeline progresses through a fixed sequence of stages. Each stage
can only be entered from its predecessor. Attempting to skip stages or
go backwards raises a PipelineStateError.
"""

from enum import Enum, auto
from typing import Optional
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    """Pipeline stages in execution order."""
    INIT = auto()
    SOURCES_LOADED = auto()
    CHANGELOGS_FETCHED = auto()
    ENTRIES_PARSED = auto()
    RECENT_ENTRIES_FILTERED = auto()
    CHANGES_CLASSIFIED = auto()
    HIGH_RISK_STRIPE_CHANGES_SELECTED = auto()
    CODEBASE_IMPACT_ANALYSED = auto()
    MIGRATION_GUIDES_GENERATED = auto()
    MIGRATION_CODE_VALIDATED = auto()
    IMPACT_REPORT_WRITTEN = auto()
    OPTIONAL_OUTPUTS_GENERATED = auto()
    VALIDATION_COMPLETE = auto()
    RESULTS_FINALISED = auto()


# Define the allowed transitions: each stage maps to the next valid stage
STAGE_ORDER = list(PipelineStage)
STAGE_TRANSITIONS = {
    STAGE_ORDER[i]: STAGE_ORDER[i + 1]
    for i in range(len(STAGE_ORDER) - 1)
}


class PipelineStateError(Exception):
    """Raised when an invalid stage transition is attempted."""
    pass


class PipelineStateMachine:
    """Manages pipeline state transitions and logging.

    Enforces that stages execute in strict sequential order.
    Logs each transition with timestamp for auditability.
    """

    def __init__(self, output_dir: Path):
        self.current_stage = PipelineStage.INIT
        self.history: list[dict] = []
        self.output_dir = output_dir
        self._log_transition(PipelineStage.INIT, "Pipeline initialized")

    def advance(self, target_stage: PipelineStage, message: str = "") -> None:
        """Advance to the next stage.

        Args:
            target_stage: The stage to transition to.
            message: Optional message describing what happened in this stage.

        Raises:
            PipelineStateError: If the transition is not allowed.
        """
        expected_next = STAGE_TRANSITIONS.get(self.current_stage)

        if expected_next is None:
            raise PipelineStateError(
                f"Pipeline is at terminal stage {self.current_stage.name}. "
                f"Cannot advance further."
            )

        if target_stage != expected_next:
            raise PipelineStateError(
                f"Invalid transition: {self.current_stage.name} -> {target_stage.name}. "
                f"Expected next stage: {expected_next.name}. "
                f"Stages must execute in strict sequential order."
            )

        previous = self.current_stage
        self.current_stage = target_stage
        self._log_transition(target_stage, message)
        logger.info(
            f"Pipeline: {previous.name} -> {target_stage.name}"
            + (f" ({message})" if message else "")
        )

    def require_stage(self, required_stage: PipelineStage) -> None:
        """Assert that the pipeline is at a specific stage.

        Args:
            required_stage: The stage the pipeline must be at.

        Raises:
            PipelineStateError: If the pipeline is not at the required stage.
        """
        if self.current_stage != required_stage:
            raise PipelineStateError(
                f"Pipeline must be at stage {required_stage.name}, "
                f"but is at {self.current_stage.name}."
            )

    def require_at_least(self, minimum_stage: PipelineStage) -> None:
        """Assert that the pipeline is at or past a specific stage.

        Args:
            minimum_stage: The minimum stage required.

        Raises:
            PipelineStateError: If the pipeline hasn't reached the minimum stage.
        """
        current_idx = STAGE_ORDER.index(self.current_stage)
        required_idx = STAGE_ORDER.index(minimum_stage)
        if current_idx < required_idx:
            raise PipelineStateError(
                f"Pipeline must be at least at stage {minimum_stage.name}, "
                f"but is at {self.current_stage.name}."
            )

    def _log_transition(self, stage: PipelineStage, message: str) -> None:
        """Record a stage transition in the history."""
        self.history.append({
            "stage": stage.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": message,
        })

    def save_history(self) -> None:
        """Save the pipeline execution history to a JSON file."""
        history_path = self.output_dir / "pipeline_history.json"
        history_path.parent.mkdir(parents=True, exist_ok=True)
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2)
        logger.info(f"Pipeline history saved to {history_path}")

    def get_summary(self) -> str:
        """Return a human-readable summary of the pipeline execution."""
        lines = ["Pipeline Execution History:", "=" * 40]
        for entry in self.history:
            ts = entry["timestamp"]
            stage = entry["stage"]
            msg = entry.get("message", "")
            lines.append(f"  [{ts}] {stage}" + (f" — {msg}" if msg else ""))
        return "\n".join(lines)
