#!/usr/bin/env python3
"""The single definition of the canonical line-oriented JSON form.

Every writer and both tools must agree on one canonical shape, or `norm --check` is worthless.
That rule lives here, once, for the same reason the interpreter probe lives in one launcher: a
rule stated in two places drifts. It already did - `wiki_lint.py` appended log events with JSON's
default `": "` separators while `wiki_norm.py` canonicalized to `":"`, so `agent.log.jsonl` could
never pass `norm --check`.

Canonical form: one JSON value per line, compact separators, non-ASCII preserved so that any
script stays readable in the file.

This module is imported by the tools, which are separate programs. Running either tool directly
still works, because Python puts the script's own directory on `sys.path`.
"""

from __future__ import annotations

import json

CANONICAL_OPTIONS = {"ensure_ascii": False, "separators": (",", ":")}


def dumps(record) -> str:
    """Serialize one record in canonical form. No trailing newline.

    Every writer of a `*.jsonl` registry must use this instead of `json.dumps`, otherwise the
    file it produces is not canonical and CI will reject it forever.
    """
    return json.dumps(record, **CANONICAL_OPTIONS)


def dumps_line(record) -> str:
    """Serialize one record as a complete canonical line."""
    return dumps(record) + "\n"


def parse_json_stream(text: str):
    """Parse a whitespace-separated stream of JSON values.

    Returns a list of (value, start_offset), or None if the text is not a valid stream. The JSON
    data model does not care about newlines, which is exactly what makes a line-oriented registry
    recoverable after a formatter has pretty-printed it.
    """
    decoder = json.JSONDecoder()
    values = []
    index = 0
    length = len(text)
    while index < length:
        while index < length and text[index].isspace():
            index += 1
        if index >= length:
            break
        try:
            value, end = decoder.raw_decode(text, index)
        except ValueError:
            return None
        values.append((value, index))
        index = end
    return values


def canonicalize(text: str):
    """Return the canonical text for a JSON value stream, or None if it does not parse."""
    values = parse_json_stream(text)
    if values is None:
        return None
    return "".join(dumps_line(value) for value, _ in values)


def read_records(text: str):
    """Read text as a line-oriented registry.

    Returns (records, bad_lines): `records` is [(line_number, value)] for the lines that parse
    standalone, and `bad_lines` lists the line numbers that do not.
    """
    records = []
    bad_lines = []
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            records.append((number, json.loads(line)))
        except json.JSONDecodeError:
            bad_lines.append(number)
    return records, bad_lines


def read_stream(text: str):
    """Read text as a JSON value stream, reporting the line each value starts on.

    Returns [(line_number, value)], or None if the text is not a valid stream. Used to recover a
    registry that is valid JSON but not one record per line.
    """
    values = parse_json_stream(text)
    if values is None:
        return None
    return [(text.count("\n", 0, offset) + 1, value) for value, offset in values]
