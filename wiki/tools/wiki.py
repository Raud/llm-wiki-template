#!/usr/bin/env python3
"""Dispatcher for the wiki tools.

The shell launchers (`wiki.cmd`, `wiki.sh`) do exactly two things: find a real Python interpreter,
and run this file. Dispatching lives here rather than in the shell so that the behaviour is
identical on every platform and neither launcher has to do argument surgery.

    wiki lint [args]    structural lint - read-only
    wiki norm [args]    canonicalize line-oriented JSON registries - mutating

Each tool also runs standalone, which is the point of keeping them separate programs:

    python wiki/tools/wiki_lint.py
    python wiki/tools/wiki_norm.py -w wiki/index/sources.jsonl
"""

from __future__ import annotations

import sys
from pathlib import Path

# Importing the tool modules would drop a __pycache__ directory into the wiki tree. The wiki is
# a content repository, not a Python project: it should not accumulate build artifacts.
sys.dont_write_bytecode = True

TOOLS = {
    "lint": (
        "wiki_lint",
        "check structure, citations, index integrity, singletons, source queue, template gaps (read-only)",
    ),
    "norm": (
        "wiki_norm",
        "canonicalize line-oriented JSON registries, one record per line (mutating)",
    ),
}


def usage(stream) -> None:
    print("usage: wiki <tool> [args...]", file=stream)
    print("", file=stream)
    print("tools:", file=stream)
    for name, (_, description) in TOOLS.items():
        print("  %-6s %s" % (name, description), file=stream)


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)

    if not args or args[0] in ("-h", "--help", "help"):
        usage(sys.stdout if args else sys.stderr)
        return 0 if args else 2

    name = args[0]
    if name not in TOOLS:
        print("wiki: unknown tool '%s'" % name, file=sys.stderr)
        usage(sys.stderr)
        return 2

    # The tools live next to this file and must be importable regardless of the working directory.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    module = __import__(TOOLS[name][0])
    return module.main(args[1:])


if __name__ == "__main__":
    sys.exit(main())
