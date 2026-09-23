#!/usr/bin/env sh
set -eu

uv run python - <<'PY'
import nltk

for package in ("punkt_tab",):
    try:
        nltk.data.find(f"tokenizers/{package}")
    except LookupError:
        nltk.download(package, quiet=True)
PY
