#!/usr/bin/env bash
# Setup the repository using `uv`.

# Stop on errors
set -e

cd "$(dirname "$0")"

REQUIRED_PYTHON="$(
	grep -E '^requires-python[[:space:]]*=' pyproject.toml | head -n1 | grep -Eo '[0-9]+\.[0-9]+' | head -n1
)"

if [ -z "$REQUIRED_PYTHON" ]; then
	echo "Could not derive requires-python from pyproject.toml"
	exit 1
fi

UV_BIN=""
if command -v uv >/dev/null 2>&1; then
	UV_BIN="$(command -v uv)"
else
	echo "uv not found, installing..."
	if command -v curl >/dev/null 2>&1; then
		curl -LsSf https://astral.sh/uv/install.sh | sh
	elif command -v wget >/dev/null 2>&1; then
		wget -qO- https://astral.sh/uv/install.sh | sh
	else
		echo "Could not install uv automatically (curl/wget missing)."
		exit 1
	fi

	if [ -x "$HOME/.local/bin/uv" ]; then
		UV_BIN="$HOME/.local/bin/uv"
	else
		echo "uv installation completed, but uv executable was not found."
		exit 1
	fi
fi

"$UV_BIN" python install "$REQUIRED_PYTHON"
"$UV_BIN" sync --python "$REQUIRED_PYTHON" --all-extras
"$UV_BIN" run pre-commit install
