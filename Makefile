.PHONY: check format

check:
	uv run pyright ./src/ ./tests/ ./packages

format:
	uv run ruff check --fix ./src/ ./tests/
	uv run ruff format ./src/ ./tests/
