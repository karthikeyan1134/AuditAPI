"""LLM client wrapping Google Gemini API with audit logging.

Every LLM call is logged to llm_calls.jsonl with full metadata including
prompt hash, input/output artifacts, and timestamps. Responses are validated
against the controlled taxonomy before being returned.
"""

import json
import hashlib
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from google import genai
from google.genai import types

from pipeline.taxonomy import validate_classification

logger = logging.getLogger(__name__)


class LLMClient:
    """Wrapper around Google Gemini API with audit logging and taxonomy validation.

    Attributes:
        model: The Gemini model name to use.
        log_file: Path to the JSONL audit log file.
    """

    def __init__(self, api_key: str, model: str, log_file: Path):
        """Initialize the LLM client.

        Args:
            api_key: Gemini API key.
            model: Model name (e.g., 'gemini-2.5-flash').
            log_file: Path to llm_calls.jsonl for audit logging.
        """
        self.model = model
        self.log_file = log_file
        self.client = genai.Client(api_key=api_key)
        self._call_count = 0
        logger.info(f"LLM client initialized: model={model}")

    def classify_changes(
        self,
        source_id: str,
        source_name: str,
        entries: list[dict],
        taxonomy_description: str,
        input_artifact: str,
        output_artifact: str,
    ) -> list[dict]:
        """Classify changelog entries for a single source.

        Makes one LLM call per source as required by the spec.

        Args:
            source_id: The source identifier (e.g., 'stripe_node').
            source_name: Human-readable source name.
            entries: List of parsed changelog entries to classify.
            taxonomy_description: The controlled taxonomy prompt text.
            input_artifact: Path to the input file for logging.
            output_artifact: Path to the output file for logging.

        Returns:
            List of classified entries with taxonomy-validated fields.
        """
        if not entries:
            logger.info(f"No entries to classify for {source_id}")
            return []

        entry_ids = [e["entry_id"] for e in entries]

        # Build the prompt
        prompt = f"""You are a software changelog analyst. Classify each changelog entry below according to the controlled taxonomy.

SOURCE: {source_name} ({source_id})

{taxonomy_description}

ENTRIES TO CLASSIFY:
{json.dumps(entries, indent=2)}

OUTPUT SCHEMA — Return a JSON array where each element has:
{{
  "entry_id": "string (must match the input entry_id)",
  "change_type": "one of: deprecation, breaking, enhancement, bugfix, security",
  "breaking_risk": "one of: critical, high, medium, low, none",
  "affects_auth": true/false,
  "affects_billing": true/false,
  "affects_data_model": true/false,
  "rationale": "one sentence explaining why you chose this classification"
}}

RULES:
- Classify EVERY entry in the input
- Use ONLY the taxonomy values listed above — do NOT invent new categories
- Match entry_id exactly from input
- Return ONLY the JSON array, no other text"""

        # Make the API call
        response_text = self._call_api(
            prompt=prompt,
            stage="classification",
            source_id=source_id,
            entry_ids=entry_ids,
            input_artifacts=[input_artifact],
            output_artifact=output_artifact,
        )

        # Parse and validate response
        classified = self._parse_json_response(response_text)
        if not isinstance(classified, list):
            logger.error(f"Expected list response for {source_id}, got {type(classified)}")
            return []

        # Validate each entry against taxonomy
        validated = []
        for entry in classified:
            is_valid, errors = validate_classification(entry)
            if is_valid:
                validated.append(entry)
            else:
                logger.warning(
                    f"Classification validation failed for {entry.get('entry_id', 'unknown')}: "
                    f"{errors}. Flagging entry."
                )
                entry["validation_error"] = True
                entry["validation_errors"] = errors
                validated.append(entry)

        return validated

    def analyze_codebase_impact(
        self,
        high_risk_entries: list[dict],
        codebase_snippet: str,
        snippet_path: str,
        input_artifacts: list[str],
        output_artifact: str,
    ) -> list[dict]:
        """Analyze impact of high-risk changes on the codebase snippet.

        Args:
            high_risk_entries: Classified entries with critical/high breaking risk.
            codebase_snippet: The actual Python source code to analyze.
            snippet_path: Path to the codebase snippet file.
            input_artifacts: Paths to input files for logging.
            output_artifact: Path to the output file for logging.

        Returns:
            List of per-function impact assessments.
        """
        entry_ids = [e["entry_id"] for e in high_risk_entries]

        prompt = f"""You are a senior software engineer analyzing the impact of SDK breaking changes on a specific codebase.

HIGH-RISK BREAKING CHANGES:
{json.dumps(high_risk_entries, indent=2)}

CODEBASE TO ANALYZE ({snippet_path}):
```python
{codebase_snippet}
```

For EACH function in the codebase, analyze whether any of the breaking changes affect it.

OUTPUT SCHEMA — Return a JSON array where each element has:
{{
  "function_name": "exact function name from the codebase",
  "affected": true/false,
  "breaking_detail": "specific description of what breaks and why, or 'No impact' if not affected",
  "suggested_fix_summary": "one-sentence description of what to change, or 'No changes needed'",
  "related_entry_ids": ["list of entry_ids that affect this function"]
}}

RULES:
- Analyze EVERY function in the codebase snippet
- Be specific about what API calls, parameters, or patterns are affected
- Only mark affected=true if a change directly impacts the function's behavior
- related_entry_ids must reference actual entry_ids from the input"""

        response_text = self._call_api(
            prompt=prompt,
            stage="codebase_impact",
            source_id="stripe_node",
            entry_ids=entry_ids,
            input_artifacts=input_artifacts,
            output_artifact=output_artifact,
        )

        result = self._parse_json_response(response_text)
        if not isinstance(result, list):
            logger.error(f"Expected list response for impact analysis, got {type(result)}")
            return []

        return result

    def generate_migration_guides(
        self,
        affected_functions: list[dict],
        codebase_snippet: str,
        input_artifacts: list[str],
        output_artifact: str,
    ) -> list[dict]:
        """Generate migration guides for affected functions.

        Args:
            affected_functions: Functions identified as affected by breaking changes.
            codebase_snippet: The current source code.
            input_artifacts: Paths to input files for logging.
            output_artifact: Path to the output file for logging.

        Returns:
            List of migration guides with before/after code.
        """
        entry_ids = []
        for f in affected_functions:
            entry_ids.extend(f.get("related_entry_ids", []))

        prompt = f"""You are a senior software engineer writing migration guides for breaking SDK changes.

AFFECTED FUNCTIONS AND THEIR ISSUES:
{json.dumps(affected_functions, indent=2)}

CURRENT CODEBASE:
```python
{codebase_snippet}
```

For EACH affected function, generate a migration guide.

OUTPUT SCHEMA — Return a JSON array where each element has:
{{
  "function_name": "exact function name",
  "before_code": "the current implementation code (extract from CURRENT CODEBASE above)",
  "after_code": "the corrected implementation with fixes applied",
  "explanation": "one sentence explaining why this change is necessary"
}}

RULES:
- The before_code must be the EXACT current code from the codebase snippet
- The after_code MUST be syntactically valid Python — it will be validated with ast.parse()
- Keep changes minimal — only fix what the breaking change requires
- Include all necessary imports in after_code if they change
- Do NOT add unrelated improvements or refactoring"""

        response_text = self._call_api(
            prompt=prompt,
            stage="migration_generation",
            source_id="stripe_node",
            entry_ids=list(set(entry_ids)),
            input_artifacts=input_artifacts,
            output_artifact=output_artifact,
        )

        result = self._parse_json_response(response_text)
        if not isinstance(result, list):
            logger.error(f"Expected list response for migration, got {type(result)}")
            return []

        return result

    def generate_typescript_migration(
        self,
        python_guides: list[dict],
        input_artifacts: list[str],
        output_artifact: str,
    ) -> list[dict]:
        """Generate TypeScript equivalents of Python migration guides.

        Args:
            python_guides: The Python migration guides to translate.
            input_artifacts: Paths to input files for logging.
            output_artifact: Path to the output file for logging.

        Returns:
            List of TypeScript migration guides.
        """
        prompt = f"""You are a senior full-stack engineer. Convert these Python migration guides to equivalent TypeScript using the Stripe Node.js SDK.

PYTHON MIGRATION GUIDES:
{json.dumps(python_guides, indent=2)}

OUTPUT SCHEMA — Return a JSON array where each element has:
{{
  "function_name": "equivalent TypeScript function name",
  "before_code": "current TypeScript implementation using Stripe Node.js SDK",
  "after_code": "corrected TypeScript implementation",
  "explanation": "one sentence explaining the TypeScript-specific change"
}}

RULES:
- Use the Stripe Node.js SDK (stripe package) equivalents
- TypeScript code must be syntactically valid
- Maintain functional equivalence with the Python fix
- Use modern TypeScript (async/await, proper types)"""

        response_text = self._call_api(
            prompt=prompt,
            stage="typescript_migration",
            source_id="stripe_node",
            entry_ids=[],
            input_artifacts=input_artifacts,
            output_artifact=output_artifact,
        )

        result = self._parse_json_response(response_text)
        if not isinstance(result, list):
            logger.error(f"Expected list response for TS migration, got {type(result)}")
            return []

        return result

    def _call_api(
        self,
        prompt: str,
        stage: str,
        source_id: Optional[str],
        entry_ids: list[str],
        input_artifacts: list[str],
        output_artifact: str,
    ) -> str:
        """Make a single Gemini API call with logging and retry.

        Args:
            prompt: The full prompt text.
            stage: Pipeline stage name for logging.
            source_id: Source identifier (if applicable).
            entry_ids: List of entry IDs being processed.
            input_artifacts: Paths to input files.
            output_artifact: Path to output file.

        Returns:
            The raw response text from the LLM.

        Raises:
            RuntimeError: If the API call fails after retries.
        """
        prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()

        # Log the call
        log_entry = {
            "stage": stage,
            "source_id": source_id,
            "entry_ids": entry_ids,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider": "google",
            "model": self.model,
            "prompt_hash": f"sha256:{prompt_hash}",
            "input_artifacts": input_artifacts,
            "output_artifact": output_artifact,
        }

        # Make the API call with retry
        last_error = None
        for attempt in range(2):  # 1 retry
            try:
                if attempt > 0:
                    logger.info(f"Retrying API call (attempt {attempt + 1})...")
                    time.sleep(5)

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1,  # Low temperature for deterministic output
                        response_mime_type="application/json",
                    ),
                )

                self._call_count += 1

                # Log successful call
                log_entry["success"] = True
                self._append_log(log_entry)

                # Safety delay between calls
                time.sleep(1)

                return response.text

            except Exception as e:
                last_error = e
                logger.warning(f"API call failed (attempt {attempt + 1}): {e}")
                log_entry["success"] = False
                log_entry["error"] = str(e)

        # All retries exhausted
        self._append_log(log_entry)
        raise RuntimeError(
            f"LLM API call failed after retries for stage={stage}, "
            f"source_id={source_id}: {last_error}"
        )

    def _parse_json_response(self, text: str) -> Any:
        """Parse JSON from LLM response, handling common formatting issues.

        Args:
            text: Raw response text from the LLM.

        Returns:
            Parsed JSON data.
        """
        # Strip markdown code fences if present
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Raw response: {text[:500]}")
            return []

    def _append_log(self, entry: dict) -> None:
        """Append a log entry to llm_calls.jsonl."""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    @property
    def call_count(self) -> int:
        """Return the number of API calls made in this session."""
        return self._call_count
