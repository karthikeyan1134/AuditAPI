"""Pipeline configuration — loads sources, environment, and paths.

Centralizes all configuration loading so stages don't need to know
where things come from. Fails fast if required config is missing.
"""

import json
import os
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@dataclass
class ChangelogSource:
    """A single changelog source to monitor."""
    source_id: str
    name: str
    url: str
    format: str  # "markdown" or "html"


@dataclass
class PipelineConfig:
    """Complete pipeline configuration."""
    # Paths
    project_root: Path
    sources_file: Path
    codebase_snippet_file: Path
    parsed_changelogs_dir: Path
    output_dir: Path
    llm_log_file: Path

    # API
    gemini_api_key: str
    gemini_model: str

    # Sources
    sources: list[ChangelogSource] = field(default_factory=list)

    # Pipeline settings
    lookback_days: int = 90
    max_retries: int = 1
    retry_delay_seconds: float = 5.0


def load_config(project_root: Optional[Path] = None) -> PipelineConfig:
    """Load pipeline configuration from environment and source files.

    Args:
        project_root: Root directory of the project. Defaults to current working directory.

    Returns:
        Fully populated PipelineConfig.

    Raises:
        FileNotFoundError: If required input files don't exist.
        ValueError: If required environment variables are missing.
    """
    # Load .env file if it exists
    if project_root is None:
        project_root = Path.cwd()

    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        logger.info(f"Loaded environment from {env_file}")

    # Validate API key
    gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_api_key or gemini_api_key == "your_key_here":
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set or is still the placeholder. "
            "Get a free API key from https://aistudio.google.com/apikey "
            "and set it in .env or as an environment variable."
        )

    # Define paths
    sources_file = project_root / "changelog_sources.json"
    codebase_snippet_file = project_root / "codebase_snippet.py"
    parsed_changelogs_dir = project_root / "parsed_changelogs"
    output_dir = project_root
    llm_log_file = project_root / "llm_calls.jsonl"

    # Validate input files exist
    if not sources_file.exists():
        raise FileNotFoundError(
            f"Changelog sources file not found: {sources_file}. "
            f"Create it or check the project root path."
        )

    if not codebase_snippet_file.exists():
        raise FileNotFoundError(
            f"Codebase snippet file not found: {codebase_snippet_file}. "
            f"Create it or check the project root path."
        )

    # Load sources
    sources = load_sources(sources_file)

    # Create output directories
    parsed_changelogs_dir.mkdir(parents=True, exist_ok=True)

    config = PipelineConfig(
        project_root=project_root,
        sources_file=sources_file,
        codebase_snippet_file=codebase_snippet_file,
        parsed_changelogs_dir=parsed_changelogs_dir,
        output_dir=output_dir,
        llm_log_file=llm_log_file,
        gemini_api_key=gemini_api_key,
        gemini_model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
        sources=sources,
        lookback_days=int(os.environ.get("LOOKBACK_DAYS", "90")),
    )

    logger.info(
        f"Configuration loaded: {len(sources)} sources, "
        f"model={config.gemini_model}, lookback={config.lookback_days} days"
    )
    return config


def load_sources(sources_file: Path) -> list[ChangelogSource]:
    """Load changelog sources from JSON file.

    Args:
        sources_file: Path to the changelog_sources.json file.

    Returns:
        List of ChangelogSource objects.
    """
    with open(sources_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    sources = []
    for entry in data.get("sources", []):
        source = ChangelogSource(
            source_id=entry["source_id"],
            name=entry["name"],
            url=entry["url"],
            format=entry.get("format", "markdown"),
        )
        sources.append(source)
        logger.debug(f"Loaded source: {source.source_id} ({source.name})")

    return sources
