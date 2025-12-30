default: run

run:
    LOG_LEVEL=INFO uv run --frozen main.py

run-mcp-inspector:
    npx @modelcontextprotocol/inspector

typecheck:
    uv run --frozen pyright

format:
    uv run --frozen ruff check src --fix --exit-non-zero-on-fix
    uv run --frozen ruff format src

test-all:
    uv run --frozen pytest -vv

test TEST:
    uv run --frozen pytest -vv {{TEST}}

coverage-all:
    uv run --frozen coverage erase
    uv run --frozen coverage run --source=src/codemash_mcp --omit "*_test.py" -m pytest -vv
    uv run --frozen coverage report -m

coverage TEST:
    uv run --frozen coverage erase
    uv run --frozen coverage run --source=src/codemash_mcp --omit "*_test.py" -m pytest -vv {{TEST}}
    uv run --frozen coverage report -m

watch-all:
    watchexec -f "**/*.py" uv run --frozen pytest -vv

watch TEST:
    watchexec -f "**/*.py" uv run --frozen pytest -vv {{TEST}}

run-image:
    podman run -it --rm -p 8000:8000 --env LOG_LEVEL=INFO --env CODEMASH_DATA_FILE=./data/endpoint-1.json --pull always ghcr.io/dmikusa/codemash-2026-mcp-demo:main

deps-upgrade:
    uv lock --upgrade
    uv sync
    rm requirements.txt # must remove old one or `uv pip compile` won't overwrite it
    uv pip compile pyproject.toml -o requirements.txt
