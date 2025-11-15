.PHONY: check format

check:
	uv run pyright ./src/

format:
	uv run ruff check --fix ./src/
	uv run ruff format ./src/
