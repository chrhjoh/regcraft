.PHONY: lint format format-check typecheck test build check clean

lint:
	uv run ruff check .

format:
	uv run ruff check --fix .
	uv run ruff format .

format-check:
	uv run ruff format --check .

typecheck:
	uv run pyrefly check

test:
	uv run pytest

build:
	uv build --no-sources

precommit: lint format-check typecheck test

clean:
	rm -rf dist build *.egg-info .pytest_cache .ruff_cache
