#!/usr/bin/env python3
"""Structural lint for a wiki built from wiki-template.

Dependency-free (Python 3.9+, standard library only). Everything domain-specific is read from
`wiki/PROFILE.md` (the Machine Config JSON block) and from the front-matter of
`wiki/templates/*.template.md`, so this tool hardcodes no domain.

Usage:
    python wiki_lint.py [--quiet] [--no-log]

Exit codes:
    0 - clean, or the wiki is not initialized yet
    1 - errors found
    2 - the tool could not run (bad profile, unreadable file)
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
import uuid
from pathlib import Path

# The wiki is a content repository, not a Python project: importing the shared module must not
# drop a __pycache__ next to it. The flag has to be set by the entry module, before the import -
# setting it inside the imported module would already be too late. Every entry point sets it.
sys.dont_write_bytecode = True

TOOL_DIR = Path(__file__).resolve().parent
WIKI_DIR = TOOL_DIR.parent
REPO_ROOT = WIKI_DIR.parent

# The canonical record shape lives in one module, shared with the formatter. Running this script
# directly works because Python puts the script's own directory on sys.path.
from wiki_jsonl import dumps_line, read_records, read_stream

FRONT_MATTER_RE = re.compile(r"^---[ \t]*\n(.*?)\n---[ \t]*\n", re.DOTALL)
SECTION_RE = re.compile(r"^##[ \t]+(.+?)[ \t]*$", re.MULTILINE)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
PLACEHOLDER_RE = re.compile(r"<[^<>\n]*>")
MD_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)")
BACKTICK_RE = re.compile(r"`([^`\n]+)`")
FILE_CITATION_RE = re.compile(r"(?<![\w:/.-])([A-Za-z0-9_][A-Za-z0-9_./-]*:\d+(?:-\d+)?)")
CITATION_LIKE_RE = re.compile(
    r"^(?:[a-z][a-z0-9+.\-]*:|[^\s:]*/[^\s:]*:\d+|[\w.\-]+\.[A-Za-z0-9]+:\d+)"
)
TABLE_SEPARATOR_RE = re.compile(r"^\|[\s:|-]+\|?$")

RETENTIONS = ("axiomatize_remove", "embed_remove", "archive", "keep", "undecided")
EXTERNAL_SUBJECT_POLICIES = ("forbidden", "ask", "labeled", "open")
SOURCE_STATUSES = ("active", "absorbed", "archived", "dropped")
RESOLUTIONS = ("axiomatize_remove", "embed_remove", "archive", "keep")
DECISION_STATUSES = ("approved", "applied")
CONFIDENCES = ("high", "medium", "low")
DECISION_ID_RE = re.compile(r"^compact-\d{4}-\d{2}-\d{2}-\d{3}$")

FACT_FIELDS = ("fact_id", "page", "statement", "citations", "tags", "updated_at", "confidence", "conflict")


def utcnow() -> str:
    return (
        datetime.datetime.now(datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def rel(path) -> str:
    try:
        return Path(path).resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return Path(path).as_posix()


def parse_timestamp(value):
    if not isinstance(value, str):
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed


def parse_scalar(value: str):
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip('"').strip("'") for item in inner.split(",") if item.strip()]
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    if value.lower() in ("null", "none", "~", ""):
        return None
    return value.strip('"').strip("'")


def parse_front_matter(text: str):
    """Return (front_matter_dict_or_None, body, front_matter_line_count)."""
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return None, text, 0
    data = {}
    for raw in match.group(1).splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        data[key.strip()] = parse_scalar(value)
    return data, text[match.end():], match.group(0).count("\n")


def sections_of(body: str):
    """Return an ordered list of (name, text, heading_line_offset)."""
    out = []
    matches = list(SECTION_RE.finditer(body))
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        line_offset = body[: match.start()].count("\n")
        out.append((match.group(1).strip(), body[start:end], line_offset + 1))
    return out


def strip_noise(text: str) -> str:
    return PLACEHOLDER_RE.sub(" ", HTML_COMMENT_RE.sub("", text))


def line_is_meaningful(line: str) -> bool:
    # Unicode-aware: a line of Cyrillic, Greek, or CJK text is content, not emptiness.
    return bool(re.search(r"\w", strip_noise(line)))


def section_has_content(text: str) -> bool:
    """True if the section holds real content rather than template scaffolding.

    HTML comments and `<placeholders>` do not count. For tables, the header row and the
    separator row do not count either - a table needs at least one data row.
    """
    cleaned = HTML_COMMENT_RE.sub("", text)
    table_lines = []
    for raw in cleaned.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("|"):
            table_lines.append(line)
            continue
        if line_is_meaningful(line):
            return True
    if not table_lines:
        return False
    data_rows = 0
    seen_header = False
    for line in table_lines:
        if TABLE_SEPARATOR_RE.match(line):
            continue
        if not seen_header:
            seen_header = True
            continue
        data_rows += 1
    return data_rows > 0


def collect_citations(text: str, schemes) -> tuple:
    """Return (valid_citations, malformed_candidates) found in the text."""
    candidates = []
    for token in BACKTICK_RE.findall(text):
        candidates.append(token.strip())
    for token in FILE_CITATION_RE.findall(text):
        candidates.append(token.strip())
    valid, malformed = [], []
    for token in candidates:
        if token in valid:
            continue
        if is_valid_citation(token, schemes):
            valid.append(token)
        elif CITATION_LIKE_RE.match(token):
            malformed.append(token)
    return valid, malformed


def is_valid_citation(token: str, schemes) -> bool:
    token = token.strip().strip("`").strip()
    if not token:
        return False
    for pattern in schemes.values():
        try:
            if re.match(pattern, token):
                return True
        except re.error:
            continue
    return False


def load_jsonl(path, findings):
    """Load a line-oriented JSON registry. Returns [(line_number, value)].

    Canonical form is one JSON value per line, and that contract is enforced rather than tolerated:
    line orientation is the whole reason these registries are JSONL. But when the file is valid
    JSON that merely is not one value per line (a formatter got to it), a wall of per-line errors
    is useless - it hides the difference between cosmetics and real corruption, and invites a
    destructive "repair". In that case report one actionable finding, and still return the
    recovered records so the remaining checks can run.
    """
    text = path.read_text(encoding="utf-8")
    records, bad_lines = read_records(text)

    if not bad_lines:
        return records

    recovered = read_stream(text)
    if recovered is not None:
        findings.error(
            "registry-not-line-oriented",
            "Valid JSON, but not one record per line (%d line(s) do not parse standalone). "
            "Canonicalize with: wiki norm -w %s" % (len(bad_lines), rel(path)),
            rel(path),
            line=bad_lines[0],
        )
        return recovered

    for number in bad_lines:
        findings.error(
            "registry-invalid-json",
            "Line %d is not valid JSON" % number,
            rel(path),
            line=number,
        )
    return records


class Findings:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.suggestions = []
        self.queue = {}

    def error(self, code, message, path=None, line=None):
        self.errors.append(self._make("error", code, message, path, line))

    def warning(self, code, message, path=None, line=None):
        self.warnings.append(self._make("warning", code, message, path, line))

    def suggest(self, kind, message, **extra):
        item = {"kind": kind, "message": message}
        item.update(extra)
        self.suggestions.append(item)

    @staticmethod
    def _make(severity, code, message, path, line):
        item = {"severity": severity, "code": code, "message": message}
        if path is not None:
            item["path"] = path
        if line is not None:
            item["line"] = int(line)
        return item


def load_profile(findings):
    path = WIKI_DIR / "PROFILE.md"
    if not path.exists():
        findings.error("profile-missing", "wiki/PROFILE.md not found", "wiki/PROFILE.md")
        return None
    text = path.read_text(encoding="utf-8")
    blocks = re.findall(r"```json[ \t]*\n(.*?)```", text, re.DOTALL)
    if not blocks:
        findings.error(
            "profile-invalid",
            "wiki/PROFILE.md has no ```json Machine Config block",
            "wiki/PROFILE.md",
        )
        return None
    try:
        config = json.loads(blocks[-1])
    except json.JSONDecodeError as exc:
        findings.error(
            "profile-invalid",
            "Machine Config is not valid JSON: %s" % exc,
            "wiki/PROFILE.md",
        )
        return None
    if not isinstance(config, dict):
        findings.error("profile-invalid", "Machine Config must be a JSON object", "wiki/PROFILE.md")
        return None
    return config


def load_templates(findings, config):
    directory = REPO_ROOT / str(config.get("templates_dir") or "wiki/templates")
    templates = {}
    if not directory.is_dir():
        findings.error("templates-missing", "templates directory not found", rel(directory))
        return templates
    for path in sorted(directory.glob("*.template.md")):
        name = path.name[: -len(".template.md")]
        text = path.read_text(encoding="utf-8")
        front, body, _ = parse_front_matter(text)
        if front is None:
            findings.error(
                "template-no-front-matter",
                "Template has no front-matter block",
                rel(path),
            )
            front = {}
        declared_name = front.get("template") or name
        if declared_name != name:
            findings.warning(
                "template-name-mismatch",
                "front-matter template '%s' does not match filename stem '%s'"
                % (declared_name, name),
                rel(path),
            )
        declared_sections = [section[0] for section in sections_of(body)]
        templates[declared_name] = {
            "path": path,
            "repeatable": bool(front.get("repeatable", True)),
            "required": [str(item) for item in (front.get("required") or [])],
            "may_be_empty": [str(item) for item in (front.get("may_be_empty") or [])],
            "evidentiary": [str(item) for item in (front.get("evidentiary") or [])],
            "declared_sections": declared_sections,
        }
    if not templates:
        findings.error("templates-empty", "No *.template.md files found", "wiki/templates")
    return templates


def load_pages(findings, config):
    directory = REPO_ROOT / str(config.get("pages_dir") or "wiki/pages")
    pages = []
    if not directory.is_dir():
        findings.error("pages-missing", "pages directory not found", rel(directory))
        return pages
    for path in sorted(directory.rglob("*.md")):
        if path.parent != directory:
            findings.warning(
                "nested-page",
                "Pages must be flat; '%s' lives in a subdirectory" % path.name,
                rel(path),
            )
        text = path.read_text(encoding="utf-8")
        front, body, front_lines = parse_front_matter(text)
        pages.append(
            {
                "path": path,
                "rel": rel(path),
                "name": path.name,
                "text": text,
                "front": front,
                "body": body,
                "front_lines": front_lines,
                "sections": sections_of(body),
            }
        )
    return pages


def check_pages(pages, templates, findings, config):
    reserved = {str(name) for name in (config.get("reserved_sections") or [])}
    min_pages = int(config.get("min_pages_for_shrink_suggestion") or 3)
    threshold = int(config.get("template_gap_threshold") or 3)
    schemes = ((config.get("citation") or {}).get("schemes")) or {}

    counts = {}
    nonempty = {}
    extras = {}
    empty_required = {}

    for page in pages:
        front = page["front"]
        if front is None:
            findings.error(
                "page-no-front-matter",
                "Page has no front-matter block",
                page["rel"],
                line=1,
            )
            continue
        for field in config.get("required_front_matter") or ["template"]:
            # 'template' is handled just below, with a more specific message.
            if field == "template" or field in front:
                continue
            findings.error(
                "page-missing-front-matter-field",
                "front-matter is missing the required key '%s'" % field,
                page["rel"],
                line=2,
            )
        name = front.get("template")
        if not name:
            findings.error(
                "page-no-template",
                "front-matter is missing the required 'template' key",
                page["rel"],
                line=2,
            )
            continue
        if name not in templates:
            findings.error(
                "unknown-template",
                "template '%s' has no wiki/templates/%s.template.md" % (name, name),
                page["rel"],
                line=2,
            )
            continue

        template = templates[name]
        counts[name] = counts.get(name, 0) + 1
        nonempty.setdefault(name, {})
        extras.setdefault(name, {})

        by_name = {}
        for section_name, section_text, heading_line in page["sections"]:
            line = heading_line + page["front_lines"]
            by_name.setdefault(section_name, []).append((section_text, line))

            if section_name in template["declared_sections"] or section_name in reserved:
                pass
            else:
                extras[name][section_name] = extras[name].get(section_name, 0) + 1

            if section_name in template["evidentiary"] and section_has_content(section_text):
                valid, malformed = collect_citations(section_text, schemes)
                if not valid:
                    findings.error(
                        "evidentiary-section-uncited",
                        "Evidentiary section '%s' has no valid citation" % section_name,
                        page["rel"],
                        line=line,
                    )
                for token in malformed:
                    findings.error(
                        "bad-citation-format",
                        "Citation does not match any declared scheme: %s" % token,
                        page["rel"],
                        line=line,
                    )

            if section_name == "Sources" and section_has_content(section_text):
                for raw_line in HTML_COMMENT_RE.sub("", section_text).splitlines():
                    stripped = raw_line.strip()
                    if not stripped or stripped.startswith("#") or stripped.startswith("|"):
                        continue
                    if stripped[:1] in ("-", "*"):
                        item = stripped.lstrip("-*").strip()
                        if item and not is_valid_citation(item, schemes):
                            findings.error(
                                "bad-citation-format",
                                "Sources line is not a valid citation: %s" % item,
                                page["rel"],
                                line=line,
                            )
                    elif line_is_meaningful(stripped):
                        findings.warning(
                            "prose-in-sources",
                            "Sources section should contain only citations: %s" % stripped,
                            page["rel"],
                            line=line,
                        )

        for required in template["required"]:
            occurrences = by_name.get(required)
            if not occurrences:
                findings.error(
                    "missing-required-section",
                    "Missing required section: %s" % required,
                    page["rel"],
                )
                continue
            filled = any(section_has_content(text) for text, _ in occurrences)
            if filled:
                nonempty[name][required] = nonempty[name].get(required, 0) + 1
            elif required in template["may_be_empty"]:
                continue
            else:
                heading_line = occurrences[0][1]
                empty_required.setdefault((name, required), []).append((page["rel"], heading_line))

    for (name, required), occurrences in sorted(empty_required.items()):
        total = counts.get(name, 0)
        if total >= min_pages and len(occurrences) == total:
            findings.warning(
                "section-never-filled",
                "Section '%s' is empty in every %s page (template design issue?)" % (required, name),
                rel(templates[name]["path"]),
            )
            findings.suggest(
                "demote-section",
                "Section '%s' is declared in template '%s' but empty in all %d pages; consider dropping it"
                % (required, name, total),
                template=name,
                section=required,
                empty_pages=total,
                total_pages=total,
            )
        else:
            for page_rel, heading_line in occurrences:
                findings.error(
                    "empty-required-section",
                    "Required section is present but empty: %s" % required,
                    page_rel,
                    line=heading_line,
                )

    for name, template in sorted(templates.items()):
        total = counts.get(name, 0)
        if total < min_pages:
            continue
        for section_name in template["declared_sections"]:
            if section_name in template["required"]:
                continue
            if nonempty.get(name, {}).get(section_name):
                continue
            findings.suggest(
                "demote-section",
                "Optional section '%s' is never filled in any of the %d %s pages; consider dropping it"
                % (section_name, total, name),
                template=name,
                section=section_name,
                empty_pages=total,
                total_pages=total,
            )

    for name, template in sorted(templates.items()):
        if template["repeatable"]:
            continue
        total = counts.get(name, 0)
        if total == 0:
            findings.error(
                "missing-singleton-page",
                "Singleton template '%s' has no page" % name,
                rel(template["path"]),
            )
        elif total > 1:
            findings.error(
                "singleton-multiplicity",
                "Singleton template '%s' has %d pages; exactly one is allowed" % (name, total),
                rel(template["path"]),
            )

    for name, sections in sorted(extras.items()):
        for section_name, page_count in sorted(sections.items()):
            if section_name in reserved:
                continue
            if page_count >= threshold:
                findings.suggest(
                    "promote-section",
                    "Section '%s' appears in %d pages of template '%s' but is not declared in it"
                    % (section_name, page_count, name),
                    template=name,
                    section=section_name,
                    pages=page_count,
                )

    return counts


def check_index_md(pages, findings):
    index_path = WIKI_DIR / "index.md"
    if not index_path.exists():
        findings.error("index-missing", "wiki/index.md not found", "wiki/index.md")
        return
    text = index_path.read_text(encoding="utf-8")
    linked = set()
    for target in MD_LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        resolved = (index_path.parent / target.split("#")[0]).resolve()
        linked.add(resolved)
        if not resolved.exists():
            findings.error(
                "index-entry-missing-page",
                "index.md links to a page that does not exist: %s" % target,
                "wiki/index.md",
            )

    inbound = set()
    for page in pages:
        for target in MD_LINK_RE.findall(page["body"]):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            inbound.add((page["path"].parent / target.split("#")[0]).resolve())

    for page in pages:
        if page["path"].resolve() not in linked:
            findings.warning(
                "page-not-in-index",
                "Page is not listed in wiki/index.md",
                page["rel"],
            )
        if (
            page["path"].resolve() not in linked
            and page["path"].resolve() not in inbound
        ):
            findings.warning(
                "orphan-page",
                "Page has no inbound link from index.md or any other page",
                page["rel"],
            )


def check_index_jsonl(pages, findings, config):
    schemes = ((config.get("citation") or {}).get("schemes")) or {}
    path = WIKI_DIR / "index" / "index.jsonl"
    if not path.exists():
        findings.warning("index-jsonl-missing", "wiki/index/index.jsonl not found", "wiki/index/index.jsonl")
        return 0
    page_paths = {page["rel"] for page in pages}
    seen = {}
    total = 0
    for number, record in load_jsonl(path, findings):
        total += 1
        if not isinstance(record, dict):
            findings.error("index-record-not-object", "Record is not a JSON object", rel(path), line=number)
            continue
        missing = [field for field in FACT_FIELDS if field not in record]
        if missing:
            findings.error(
                "fact-missing-field",
                "Fact is missing field(s): %s" % ", ".join(missing),
                rel(path),
                line=number,
            )
        fact_id = record.get("fact_id")
        if fact_id:
            if fact_id in seen:
                findings.error(
                    "duplicate-fact-id",
                    "fact_id '%s' already used on line %d" % (fact_id, seen[fact_id]),
                    rel(path),
                    line=number,
                )
            else:
                seen[fact_id] = number
        page = record.get("page")
        if page and page not in page_paths:
            findings.error(
                "fact-unknown-page",
                "Fact points to a page that does not exist: %s" % page,
                rel(path),
                line=number,
            )
        citations = record.get("citations")
        if not isinstance(citations, list) or not citations:
            findings.error("fact-no-citation", "Fact has no citations", rel(path), line=number)
        else:
            for citation in citations:
                if not is_valid_citation(str(citation), schemes):
                    findings.error(
                        "bad-citation-format",
                        "Fact citation does not match any declared scheme: %s" % citation,
                        rel(path),
                        line=number,
                    )
        if record.get("confidence") not in CONFIDENCES:
            findings.error(
                "bad-confidence",
                "confidence must be one of %s" % ", ".join(CONFIDENCES),
                rel(path),
                line=number,
            )
        if not isinstance(record.get("conflict"), bool):
            findings.error("bad-conflict-flag", "conflict must be a boolean", rel(path), line=number)
        if parse_timestamp(record.get("updated_at")) is None:
            findings.error(
                "bad-updated-at",
                "updated_at must be an ISO-8601 UTC timestamp",
                rel(path),
                line=number,
            )
    return total


def check_sources(findings, config):
    path = WIKI_DIR / "index" / "sources.jsonl"
    if not path.exists():
        findings.warning("sources-missing", "wiki/index/sources.jsonl not found", "wiki/index/sources.jsonl")
        return 0, {}

    counts = {"status": {}, "retention": {}}
    seen = set()
    candidate_days = int(config.get("compaction_candidate_after_days") or 14)
    now = datetime.datetime.now(datetime.timezone.utc)
    candidates = []
    total = 0

    for number, source in load_jsonl(path, findings):
        total += 1
        if not isinstance(source, dict):
            findings.error("source-not-object", "Record is not a JSON object", rel(path), line=number)
            continue
        source_id = source.get("id")
        if not source_id:
            findings.error("source-missing-id", "Source record has no 'id'", rel(path), line=number)
        elif source_id in seen:
            findings.error("duplicate-source-id", "Duplicate source id: %s" % source_id, rel(path), line=number)
        else:
            seen.add(source_id)

        retention = source.get("retention", "undecided")
        status = source.get("status", "active")
        if retention not in RETENTIONS:
            findings.error(
                "bad-retention",
                "Source '%s' has retention '%s'; expected one of %s"
                % (source_id, retention, ", ".join(RETENTIONS)),
                rel(path),
                line=number,
            )
        if status not in SOURCE_STATUSES:
            findings.error(
                "bad-source-status",
                "Source '%s' has status '%s'; expected one of %s"
                % (source_id, status, ", ".join(SOURCE_STATUSES)),
                rel(path),
                line=number,
            )
        counts["status"][status] = counts["status"].get(status, 0) + 1
        counts["retention"][retention] = counts["retention"].get(retention, 0) + 1

        if status in ("archived", "dropped") and not source.get("decision_id"):
            findings.warning(
                "source-without-decision",
                "Source '%s' is '%s' but has no decision_id" % (source_id, status),
                rel(path),
                line=number,
            )

        locator = source.get("locator") or ""
        if (
            locator
            and ":" not in locator.split("/")[0]
            and not Path(REPO_ROOT / locator).exists()
            and status not in ("archived", "dropped")
        ):
            findings.warning(
                "source-missing-locator",
                "Source '%s' points to a file that does not exist: %s" % (source_id, locator),
                rel(path),
                line=number,
            )

        if retention in ("embed_remove", "axiomatize_remove") and status in ("active", "absorbed"):
            stamp = parse_timestamp(source.get("last_seen")) or parse_timestamp(source.get("added_at"))
            age = (now - stamp).days if stamp is not None else None
            if status == "absorbed" or (age is not None and age >= candidate_days):
                candidates.append(
                    {
                        "id": source_id,
                        "locator": locator,
                        "status": status,
                        "age_days": age,
                        "retention": retention,
                        "reason": "absorbed" if status == "absorbed" else "stale",
                    }
                )

    counts["compaction_candidates"] = candidates
    return total, counts


def check_decisions(findings, config):
    schemes = ((config.get("citation") or {}).get("schemes")) or {}
    path = WIKI_DIR / "index" / "decisions.jsonl"
    if not path.exists():
        findings.warning("decisions-missing", "wiki/index/decisions.jsonl not found", "wiki/index/decisions.jsonl")
        return 0
    seen = set()
    total = 0
    required = (
        "decision_id",
        "ts",
        "requested_by",
        "raw_sources",
        "wiki_targets",
        "resolution",
        "replacement_citation",
        "status",
    )
    for number, record in load_jsonl(path, findings):
        total += 1
        if not isinstance(record, dict):
            findings.error("decision-record-not-object", "Record is not a JSON object", rel(path), line=number)
            continue
        missing = [field for field in required if field not in record]
        if missing:
            findings.error(
                "decision-missing-field",
                "Decision is missing field(s): %s" % ", ".join(missing),
                rel(path),
                line=number,
            )
        decision_id = record.get("decision_id")
        if decision_id:
            if not DECISION_ID_RE.match(str(decision_id)):
                findings.error(
                    "bad-decision-id",
                    "decision_id '%s' must match compact-YYYY-MM-DD-XXX" % decision_id,
                    rel(path),
                    line=number,
                )
            if decision_id in seen:
                findings.error(
                    "duplicate-decision-id",
                    "decision_id '%s' already used" % decision_id,
                    rel(path),
                    line=number,
                )
            else:
                seen.add(decision_id)
        if record.get("resolution") not in RESOLUTIONS:
            findings.error(
                "bad-resolution",
                "resolution must be one of %s" % ", ".join(RESOLUTIONS),
                rel(path),
                line=number,
            )
        if record.get("status") not in DECISION_STATUSES:
            findings.error(
                "bad-decision-status",
                "status must be one of %s" % ", ".join(DECISION_STATUSES),
                rel(path),
                line=number,
            )
        if not isinstance(record.get("raw_sources"), list) or not record.get("raw_sources"):
            findings.error("decision-no-sources", "raw_sources must be a non-empty array", rel(path), line=number)
        if not isinstance(record.get("wiki_targets"), list) or not record.get("wiki_targets"):
            findings.error("decision-no-targets", "wiki_targets must be a non-empty array", rel(path), line=number)
        replacement = record.get("replacement_citation")
        if replacement and not is_valid_citation(str(replacement), schemes):
            findings.error(
                "bad-citation-format",
                "replacement_citation does not match any declared scheme: %s" % replacement,
                rel(path),
                line=number,
            )
    return total


def build_report(findings, config, status, metrics, checked_paths, summary):
    return {
        "ts": utcnow(),
        "status": status,
        "errors": findings.errors,
        "warnings": findings.warnings,
        "template_suggestions": findings.suggestions,
        "source_queue": findings.queue,
        "metrics": metrics,
        "checked_paths": checked_paths,
        "summary": summary,
    }


def write_report(report):
    logs = WIKI_DIR / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    path = logs / "lint-report.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def append_agent_log(report, metrics):
    path = WIKI_DIR / "logs" / "agent.log.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "ts": report["ts"],
        "run_id": uuid.uuid4().hex[:12],
        "agent": "wiki-keeper",
        "operation": "lint",
        "status": report["status"],
        "inputs": {"tool": "wiki/tools/wiki_lint.py", "profile": "wiki/PROFILE.md"},
        "outputs": {"report": "wiki/logs/lint-report.json"},
        "notes": "pages=%s facts=%s sources=%s errors=%s warnings=%s"
        % (
            metrics.get("pages", 0),
            metrics.get("facts", 0),
            metrics.get("sources", 0),
            metrics.get("errors", 0),
            metrics.get("warnings", 0),
        ),
    }
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        # dumps_line, not json.dumps: this is a *.jsonl registry and its records must be canonical,
        # or `wiki norm --check` would reject every log the tool itself wrote.
        handle.write(dumps_line(event))


def print_human(report, quiet=False):
    if quiet:
        return
    metrics = report["metrics"]
    print("wiki-lint %s [%s]" % (report["ts"], report["status"]))
    print(
        "  pages=%s facts=%s sources=%s decisions=%s errors=%s warnings=%s"
        % (
            metrics.get("pages", 0),
            metrics.get("facts", 0),
            metrics.get("sources", 0),
            metrics.get("decisions", 0),
            metrics.get("errors", 0),
            metrics.get("warnings", 0),
        )
    )
    for item in report["errors"]:
        location = item.get("path", "")
        if item.get("line"):
            location += ":%s" % item["line"]
        print("  ERROR   [%s] %s (%s)" % (item["code"], item["message"], location))
    for item in report["warnings"]:
        location = item.get("path", "")
        if item.get("line"):
            location += ":%s" % item["line"]
        print("  warning [%s] %s (%s)" % (item["code"], item["message"], location))
    for item in report["template_suggestions"]:
        print("  suggest [%s] %s" % (item["kind"], item["message"]))
    queue = report.get("source_queue") or {}
    candidates = queue.get("compaction_candidates") or []
    if candidates:
        print("  sources ready for compaction: %s" % ", ".join(item["id"] for item in candidates))
    print("  report: wiki/logs/lint-report.json")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Structural lint for a wiki-template wiki.")
    parser.add_argument("--quiet", action="store_true", help="write the report without printing a summary")
    parser.add_argument("--no-log", action="store_true", help="do not append an event to logs/agent.log.jsonl")
    args = parser.parse_args(argv)

    findings = Findings()
    config = load_profile(findings)
    if config is None:
        report = build_report(findings, {}, "failed", {"errors": len(findings.errors), "warnings": 0}, ["wiki/PROFILE.md"], "Lint could not run: the domain profile is missing or invalid.")
        write_report(report)
        print_human(report, args.quiet)
        return 2

    policy = config.get("external_subject")
    if policy is not None and policy not in EXTERNAL_SUBJECT_POLICIES:
        findings.error(
            "bad-external-subject",
            "external_subject must be one of %s" % ", ".join(EXTERNAL_SUBJECT_POLICIES),
            "wiki/PROFILE.md",
        )

    if not config.get("initialized", False):
        # Problems found in the profile itself are real regardless of initialization state, so they
        # must show up in the metrics and in the exit code, not only in the printed list.
        report = build_report(
            findings,
            config,
            "failed" if findings.errors else "uninitialized",
            {
                "pages": 0,
                "facts": 0,
                "sources": 0,
                "decisions": 0,
                "errors": len(findings.errors),
                "warnings": len(findings.warnings),
            },
            ["wiki/PROFILE.md"],
            "Wiki is not initialized. Run BOOTSTRAP.md to create the domain profile and the first page.",
        )
        write_report(report)
        print_human(report, args.quiet)
        return 1 if findings.errors else 0

    templates = load_templates(findings, config)
    pages = load_pages(findings, config)
    check_pages(pages, templates, findings, config)
    check_index_md(pages, findings)
    facts = check_index_jsonl(pages, findings, config)
    sources, queue = check_sources(findings, config)
    decisions = check_decisions(findings, config)
    findings.queue = queue

    status = "failed" if findings.errors else "ok"
    metrics = {
        "pages": len(pages),
        "templates": len(templates),
        "facts": facts,
        "sources": sources,
        "decisions": decisions,
        "errors": len(findings.errors),
        "warnings": len(findings.warnings),
        "template_suggestions": len(findings.suggestions),
    }
    summary = "Wiki lint completed: structure, citations, index integrity, singletons, source queue, and template gaps were checked."
    report = build_report(
        findings,
        config,
        status,
        metrics,
        ["wiki/PROFILE.md", "wiki/templates", "wiki/pages", "wiki/index.md", "wiki/index/index.jsonl", "wiki/index/sources.jsonl", "wiki/index/decisions.jsonl"],
        summary,
    )
    write_report(report)
    if not args.no_log:
        append_agent_log(report, metrics)
    print_human(report, args.quiet)
    return 1 if findings.errors else 0


if __name__ == "__main__":
    sys.exit(main())
