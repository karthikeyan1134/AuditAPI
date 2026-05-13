"""Stage 1: Fetch changelogs from all configured sources.

Downloads raw changelog content from each URL. Handles network failures
gracefully by logging errors and creating empty result files.
"""

import json
import logging
from pathlib import Path

import requests

from pipeline.config import PipelineConfig, ChangelogSource

logger = logging.getLogger(__name__)

# Request timeout in seconds
REQUEST_TIMEOUT = 30

# User-agent to avoid being blocked
USER_AGENT = "ChangelogPipeline/1.0 (SDK Monitoring Bot)"


def fetch_all_sources(config: PipelineConfig) -> dict[str, dict]:
    """Fetch changelogs from all configured sources.

    Args:
        config: Pipeline configuration with source definitions.

    Returns:
        Dictionary mapping source_id to fetch results:
        {
            "source_id": {
                "source_id": str,
                "source_name": str,
                "url": str,
                "format": str,
                "content": str | None,
                "success": bool,
                "error": str | None,
                "content_length": int
            }
        }
    """
    results = {}

    for source in config.sources:
        logger.info(f"Fetching changelog for {source.source_id} from {source.url}")
        result = _fetch_single_source(source)
        results[source.source_id] = result

        # Save raw fetched content
        raw_file = config.parsed_changelogs_dir / f"{source.source_id}_raw.json"
        _save_raw_result(result, raw_file)

    success_count = sum(1 for r in results.values() if r["success"])
    logger.info(
        f"Fetched {success_count}/{len(config.sources)} sources successfully"
    )

    return results


def _fetch_single_source(source: ChangelogSource) -> dict:
    """Fetch a single changelog source.

    Args:
        source: The changelog source to fetch.

    Returns:
        Fetch result dictionary.
    """
    result = {
        "source_id": source.source_id,
        "source_name": source.name,
        "url": source.url,
        "format": source.format,
        "content": None,
        "success": False,
        "error": None,
        "content_length": 0,
    }

    try:
        response = requests.get(
            source.url,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
        )
        response.raise_for_status()

        result["content"] = response.text
        result["success"] = True
        result["content_length"] = len(response.text)

        logger.info(
            f"  ✓ {source.source_id}: fetched {result['content_length']} chars"
        )

    except requests.exceptions.Timeout:
        result["error"] = f"Request timed out after {REQUEST_TIMEOUT}s"
        logger.warning(f"  ✗ {source.source_id}: timeout")

    except requests.exceptions.HTTPError as e:
        result["error"] = f"HTTP error: {e.response.status_code} {e.response.reason}"
        logger.warning(f"  ✗ {source.source_id}: HTTP {e.response.status_code}")

    except requests.exceptions.ConnectionError as e:
        result["error"] = f"Connection error: {str(e)[:200]}"
        logger.warning(f"  ✗ {source.source_id}: connection error")

    except requests.exceptions.RequestException as e:
        result["error"] = f"Request failed: {str(e)[:200]}"
        logger.warning(f"  ✗ {source.source_id}: {e}")

    return result


def _save_raw_result(result: dict, path: Path) -> None:
    """Save fetch result to disk (without raw content to save space)."""
    # Save metadata only — raw content is passed to parser in memory
    meta = {k: v for k, v in result.items() if k != "content"}
    meta["has_content"] = result["content"] is not None

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
