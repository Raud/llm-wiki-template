#!/bin/sh
# Launcher for the wiki tools.
#
# It exists for one non-obvious reason: `python` on PATH can be a stub that answers nothing
# useful (a Microsoft Store execution alias on Windows). So the interpreter is probed, not just
# located. This is the only place that probe lives; per-tool copies are how it drifted before.
#
#   wiki lint [args]   structural lint (read-only)
#   wiki norm [args]   canonicalize line-oriented JSON registries (mutating)
#
# If Python is unavailable, `lint` is skipped (the wiki works without it) and any other tool
# fails loudly, because those genuinely require Python.
set -u
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROBE='import sys; sys.exit(0 if sys.version_info >= (3, 9) else 3)'

for CMD in python3 python; do
  if command -v "$CMD" >/dev/null 2>&1 && "$CMD" -c "$PROBE" >/dev/null 2>&1; then
    exec "$CMD" "$DIR/wiki.py" "$@"
  fi
done

if [ "${1:-}" = "lint" ]; then
  echo "Python 3.9+ not found - lint skipped. The wiki works without it." >&2
  exit 0
fi

echo "Python 3.9+ not found - the wiki tools require Python 3.9+." >&2
exit 2
