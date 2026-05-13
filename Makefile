.PHONY: run validate clean install help

# Default target
help:
	@echo "Changelog Monitoring Pipeline"
	@echo "=============================="
	@echo ""
	@echo "Targets:"
	@echo "  make install   - Install Python dependencies"
	@echo "  make run       - Run the full pipeline"
	@echo "  make validate  - Validate pipeline artifacts"
	@echo "  make clean     - Remove all generated artifacts"
	@echo "  make help      - Show this help message"
	@echo ""
	@echo "Environment:"
	@echo "  GEMINI_API_KEY - Required. Set in .env or environment"
	@echo ""

# Install dependencies
install:
	pip install -r requirements.txt

# Run the full pipeline
run:
	python run_pipeline.py

# Validate pipeline artifacts
validate:
	python validate.py

# Clean generated artifacts
clean:
	rm -rf parsed_changelogs/
	rm -f classified_changes.json
	rm -f codebase_impact.json
	rm -f migration_guides.md
	rm -f migration_guides.json
	rm -f migration_validation.json
	rm -f impact_report.md
	rm -f security_alerts.json
	rm -f version_pinning.md
	rm -f delta_processing_report.json
	rm -f typescript_migration.md
	rm -f llm_calls.jsonl
	rm -f pipeline_history.json
	@echo "Cleaned all generated artifacts"
