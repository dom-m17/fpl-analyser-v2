.PHONY: run

run:
	python3 -m venv .venv
	.venv/bin/pip install -e ".[dev]"
	.venv/bin/uvicorn fpl.api:app --reload