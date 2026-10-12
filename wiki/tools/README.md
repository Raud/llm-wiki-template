# wiki/tools

Two tools, one launcher. Each tool does one job, and — deliberately — the reading tool and the writing
tool are separate programs rather than one program with a `--fix` flag.

| Tool | Role | Mutates? |
|---|---|---|
| `wiki_lint.py` | checker: structure, citations, index integrity, singletons, source queue, template gaps | no |
| `wiki_norm.py` | formatter: canonicalize `*.jsonl` registries to one record per line | yes, with `-w` |

Both are **optional**. The wiki must stay fully usable with an agent and markdown alone; these tools are a verification
accelerator, not a dependency. Only `lint` degrades gracefully when Python is missing — `norm` genuinely cannot work
without it, so it fails loudly.

## Run

```
wiki lint                          # read-only
wiki norm -w wiki/index            # canonicalize every registry in the directory
wiki norm --check wiki/index       # CI: exit 1 if anything is not canonical
```

Targets may be files or directories; directories are searched one level deep, never recursively, and a directory with
no registries is an error rather than a silent no-op — silence would make `--check` a useless gate. Prefer
**directories** in documentation: PowerShell and cmd do not expand `*.jsonl` for external programs, so a glob in an
example silently does nothing there.

- Windows: `wiki\tools\wiki.cmd lint`
- POSIX: `./wiki/tools/wiki.sh lint`
- Standalone: `python wiki/tools/wiki_lint.py`, `python wiki/tools/wiki_norm.py`

The launchers do exactly two things: **probe for a real Python interpreter**, and run `wiki.py`, which dispatches.
The probe matters because `python` on PATH can be a Microsoft Store execution alias — a stub that answers nothing
useful — so the interpreter is tried, not merely located. That logic lives in one place on purpose: when it was
duplicated per tool, a fix landed in only one copy.

Dispatching lives in Python rather than in the shell so both platforms behave identically and neither launcher needs
argument surgery.

`wiki_jsonl.py` is a small shared library, not a tool: it holds the canonical record shape and the line-oriented
readers used by both. Python would normally write a `__pycache__` next to an imported module, and the wiki is a content
repository, so every entry point disables bytecode writing; `.gitignore` covers anything that slips past.

## Line orientation is a contract

Every `*.jsonl` registry holds one JSON value per line. It is what makes a registry streamable, recoverable after a
truncated write, and diffable line by line.

A pretty-printed registry is *still valid JSON* — nothing is lost, because whitespace between JSON values is not data.
It is simply no longer canonical. `lint` reports that as a single finding:

```
ERROR [registry-not-line-oriented] wiki/index/index.jsonl
      Valid JSON, but not one record per line (14 line(s) do not parse standalone).
      Canonicalize with: wiki norm -w wiki/index/index.jsonl
```

One finding, not one per line, because the two situations need different reactions:

| State | Meaning | Reaction |
|---|---|---|
| Parses, but not line by line | cosmetics — a formatter reformatted it | `wiki norm -w` |
| Does not parse at all | real corruption or a truncated write | investigate; `lint` still reports per-line |

Collapsing those into a wall of errors hides the difference and invites a destructive "repair".

### `wiki norm`

```
wiki norm [options] [target ...]

  target       a *.jsonl file, or a directory containing *.jsonl files (one level deep)
  (no targets) read stdin, write canonical text to stdout
  -w, --write  rewrite the targets in place, atomically
  --check      write nothing; exit 1 if any file is not already canonical
```

Guarantees: **all-or-nothing** (if any input fails to parse, nothing is written) and **atomic** (a file is replaced
only once its full canonical text is on disk). Canonical form is compact separators with non-ASCII preserved.

The canonical shape is defined **once**, in `wiki_jsonl.py`, and imported by both tools. It used to live in two places,
and they drifted: `lint` appended log events with JSON's default `": "` separators while `norm` canonicalized to `":"`,
so `wiki/logs/agent.log.jsonl` could never pass `norm --check`. Any writer of a registry must use
`wiki_jsonl.dumps_line`, never `json.dumps`.

Honest limitation: re-serializing is faithful to the JSON **data model**, not to the original bytes. Key order and
number formatting are normalized along with whitespace. That is why `norm` is an explicitly named operation instead of
a flag on `lint`.

Exit codes: `0` ok / canonical, `1` `--check` found non-canonical files, `2` parse error, missing file, or write
failure.

## Configuration

Nothing about the domain is hardcoded. `lint` reads:

- `wiki/PROFILE.md` → the ` ```json ` **Machine Config** block (citation schemes, thresholds, reserved sections).
- `wiki/templates/*.template.md` → front-matter (`repeatable`, `required`, `may_be_empty`, `evidentiary`) plus the `##`
  headings in the template body, which are its declared sections.

Adding a template means adding a file. Changing lint rules for a domain means editing the profile.

## What `lint` checks

**Pages** — front-matter present with a `template` key; the template exists; required sections present and filled (HTML
comments and `<placeholders>` do not count; a table with only a header row counts as empty); evidentiary sections
carry at least one valid citation; every line of `## Sources` is a valid citation; every citation-shaped token inside
an evidentiary section or `## Sources` matches a declared scheme; pages are flat.

A required section that is empty in **some** pages is an error; empty in **every** page of that template (once enough
pages exist) it becomes a warning plus a shrink suggestion, because that is a template design problem, not an authoring
slip.

**Singletons** — a template with `repeatable: false` must have exactly one page.

**Index** — `index.md` links resolve; every page is listed; no orphan pages; `index.jsonl` records parse, have unique
`fact_id`s, satisfy the field contract, point at existing pages, carry valid citations, and use valid
`confidence`/`conflict`/`updated_at` values.

**Registries** — every `*.jsonl` is one record per line (see above), records parse, and the line numbers in findings
point at real lines.

**Sources** — valid status and retention enums; archived/dropped sources carry a `decision_id`; active sources point at
a file that exists; the compaction queue (marked for removal, either `absorbed` or `active` past the age threshold) is
reported.

**Decisions** — valid `compact-YYYY-MM-DD-XXX` ids, unique, complete fields, valid resolution/status, and a
`replacement_citation` that matches a declared scheme.

**Template gaps** — non-template sections appearing in at least `template_gap_threshold` pages of one template
(`promote-section`), and declared sections that are empty in every page of a template (`demote-section`). Findings land
in `template_suggestions`; surfacing them to the user is the keeper's job, not the tool's.

**Reserved sections** — sections listed in `reserved_sections` (by default `Source Excerpt`) are part of the
compaction mechanism and never count as template gaps.

## What `lint` deliberately does not do

It cannot tell whether a claim *should* have a citation. Enforcing "every atomic claim is cited" is the agent's job,
per `AGENTS.md` §7; the tool only enforces that evidentiary sections contain citations and that citations are
well-formed. It also does not verify that citation targets exist — sources legitimately live outside the wiki tree.

It never writes to a registry, and it never fixes anything. That is `norm`'s job.
