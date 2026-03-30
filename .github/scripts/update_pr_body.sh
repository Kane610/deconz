#!/usr/bin/env bash

# Write PR description to a temp file and update PR #883
set -euo pipefail

cat > /tmp/pr_desc.txt <<'PRBODY'
Use `uv` for development setup and CI

Summary
- Switch development setup from venv + pip to `uv` in `setup.sh`.
- Add a Development section to `README.rst` documenting the new setup.
- Update CI workflows to install `uv` and run tools via `uv run`.
- Minor typing/lint fixes to satisfy ruff/mypy where needed.

Files changed
- `setup.sh`
- `README.rst`
- `.github/workflows/test.yml`
- `.github/workflows/pythonpublish.yml`
- `pydeconz/interfaces/api_handlers.py`

Testing
- Ran `ruff check .` and `pytest` locally: 156 passed, coverage 95.60%.
- CI will run the updated workflows when this PR is updated.

How to test locally
1. Run `./setup.sh` (it will install `uv` if missing).
2. Use `uv run pytest` to run tests in the uv-managed environment.
3. Use `uv run ruff check .` and `uv run mypy pydeconz` for linting/type checks.

Notes
- `setup.sh` installs `uv` via the official installer if missing and then uses it to create/sync the Python environment and install pre-commit hooks.
PRBODY

# Attempt to edit the PR body via gh
if command -v gh >/dev/null 2>&1; then
    gh pr edit 883 --repo Kane610/deconz --body-file /tmp/pr_desc.txt
else
    echo "gh CLI not found; cannot edit PR body"
    exit 2
fi
