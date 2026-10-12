#!/usr/bin/env python3
"""Canonicalize line-oriented JSON registries: one JSON value per line.

This is a **formatter**, not a checker. `wiki_lint.py` reports the problem; this tool fixes it.
The split is deliberate: a mutation must not hide behind a flag on a read-only check, because
that breaks exit-code semantics and makes "I just ran the lint" a dangerous habit.

Usage:
    python wiki_norm.py [options] [target ...]

    target          a *.jsonl file, or a directory containing *.jsonl files (one level deep)
    (no targets)    read stdin, write canonical text to stdout
    -w, --write     rewrite the targets in place, atomically
    --check         write nothing; exit 1 if any target is not already canonical

Directories are accepted so that the command is identical in every shell: PowerShell and cmd do
not expand `*.jsonl` for external programs, so a documented glob would silently do nothing there.

Guarantees:
    * All-or-nothing - if any input fails to parse, nothing at all is written.
    * Atomic - a file is replaced only after its full canonical text is on disk.
    * Line endings are normalized to LF and a trailing newline is ensured.

Honest limitation: re-serializing is faithful to the JSON **data model**, not to the original
bytes. Key order and number formatting are normalized along with whitespace, so this tool can
rewrite more than the pretty-printing it is meant to undo. That is precisely why it is a
separate, explicitly invoked operation and not a `--fix` flag.

Exit codes:
    0 - ok, or `--check` found everything canonical
    1 - `--check` found non-canonical files
    2 - parse error, missing target, or write failure
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# The wiki is a content repository, not a Python project: importing the shared module must not
# drop a __pycache__ next to it. The flag has to be set by the entry module, before the import -
# setting it inside the imported module would already be too late. Every entry point sets it.
sys.dont_write_bytecode = True

from wiki_jsonl import canonicalize


def expand_targets(names):
    """Resolve files and directories into a list of `*.jsonl` files.

    Returns (files, error). Directories are searched one level deep, never recursively, and a
    directory with no registries is an error rather than a silent no-op - silence would make
    `--check` a useless CI gate.
    """
    files = []
    for name in names:
        path = Path(name)
        if path.is_dir():
            found = sorted(path.glob("*.jsonl"))
            if not found:
                return None, "%s contains no *.jsonl files" % name
            files.extend(found)
        elif path.is_file():
            files.append(path)
        else:
            return None, "not a file or directory: %s" % name
    return files, None


def write_atomic(path: Path, text: str) -> None:
    """Replace a file only once its full new content is on disk."""
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    os.replace(temporary, path)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="wiki norm",
        description="Canonicalize line-oriented JSON registries (one record per line).",
    )
    parser.add_argument(
        "targets",
        nargs="*",
        help="*.jsonl files, or directories containing them; omit to use stdin",
    )
    parser.add_argument("-w", "--write", action="store_true", help="rewrite the targets in place")
    parser.add_argument(
        "--check",
        action="store_true",
        help="write nothing; exit 1 if any target is not already canonical",
    )
    args = parser.parse_args(argv)

    if args.write and args.check:
        print("wiki norm: --write and --check are mutually exclusive", file=sys.stderr)
        return 2

    if not args.targets:
        if args.write or args.check:
            print("wiki norm: --write and --check need targets", file=sys.stderr)
            return 2
        text = sys.stdin.read()
        canonical = canonicalize(text)
        if canonical is None:
            print("wiki norm: stdin is not a valid stream of JSON values", file=sys.stderr)
            return 2
        sys.stdout.write(canonical)
        return 0

    files, error = expand_targets(args.targets)
    if error:
        print("wiki norm: %s" % error, file=sys.stderr)
        return 2

    # Parse everything before touching anything: all-or-nothing.
    prepared = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        canonical = canonicalize(text)
        if canonical is None:
            print(
                "wiki norm: %s is not a valid stream of JSON values; nothing was written" % path,
                file=sys.stderr,
            )
            return 2
        prepared.append((path, text, canonical))

    changed = [path for path, text, canonical in prepared if text != canonical]

    if args.check:
        for path in changed:
            print(path.as_posix())
        return 1 if changed else 0

    if args.write:
        try:
            for path, text, canonical in prepared:
                if text != canonical:
                    write_atomic(path, canonical)
        except OSError as failure:
            print("wiki norm: write failed: %s" % failure, file=sys.stderr)
            return 2
        return 0

    for _, _, canonical in prepared:
        sys.stdout.write(canonical)
    return 0


if __name__ == "__main__":
    sys.exit(main())
