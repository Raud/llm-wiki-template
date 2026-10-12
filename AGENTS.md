# AGENTS.md — Wiki Operating Contract

This file is the domain-agnostic contract for this wiki. It never changes per domain.

**Read `wiki/PROFILE.md` first.** It defines the domain: purpose, readers, source kinds, citation schemes,
retention defaults, content language. `PROFILE.md` is the only domain-specific file in the wiki. Whether this wiki
keeps a scratch workspace at all — and what may leave it — is a domain decision; see §17.

## 1) What this is

A persistent knowledge base maintained jointly by a human and an LLM agent.

- **Sources are read-only facts.** They are evidence, not drafts.
- **Pages are synthesized artifacts.** They are the product.
- **Every concrete claim carries a citation.** No uncited model memory as evidence.

A wiki that follows these three rules can be re-verified. A wiki that does not is an opinion pile.

## 2) Language

- **Service records are always English**: this file, `PROFILE.md` machine config, front-matter values, field names,
  enum values, `log.md` operation lines, `logs/*.json*`, and the `log.md` / `Change Log` entry format.
- **Page content** is written in the content language declared in `PROFILE.md` (`content_language`). If that value is
  `null`, page content is English.

## 3) Roles

| Agent | Prompt | Owns |
|---|---|---|
| `wiki-scribe` | `wiki/agents/wiki-scribe.prompt.md` | ingest, query, page writing, gap detection |
| `wiki-keeper` | `wiki/agents/wiki-keeper.prompt.md` | lint, index integrity, cross-links, source compaction, template suggestions |

## 4) Directory contract

```
raw/                            immutable source material
raw/archive/                    retained-but-inactive sources
scratch/                        transient working documents — never evidence, never cited
wiki/PROFILE.md                 domain profile — the only domain-specific file
wiki/index.md                   curated catalog: grouping, order, one-line summaries
wiki/log.md                     append-only human-readable timeline
wiki/pages/*.md                 pages — FLAT, no subdirectories
wiki/templates/*.template.md    the template palette
wiki/index/index.jsonl          fact registry
wiki/index/sources.jsonl        source registry
wiki/index/decisions.jsonl      source-compaction decisions
wiki/logs/agent.log.jsonl       machine log
wiki/logs/lint-report.json      lint output (generated)
wiki/tools/                     launcher and tools (lint, norm)
```

### Path rules

- **Pages are flat.** `wiki/pages/pancakes.md`, never `wiki/pages/howto/pancakes.md`.
- **A path encodes stable identity only.** Never encode mutable classification (template, status, topic) or ordinals
  (`14-`, `21-`) in a filename. Classification lives in front-matter; grouping and order live in `index.md`.
- Rationale: when a page changes template (`plan` becomes `concept`, an incident becomes knowledge), the file must not
  move — moving it breaks citations, the `page` field of every fact record, and inbound links. Views belong in
  `index.md`, where regrouping costs nothing.
- Escalation: only past roughly 50–80 pages may one level of **subject-based** subdirectories be added
  (`pages/projects/`, `pages/team/`) — never template-based ones.

## 5) Page front-matter

Every page starts with a restricted-YAML front-matter block:

```markdown
---
template: concept
status: active
---
```

- `template` (required) must match a file `wiki/templates/<template>.template.md`.
- `status` (optional, default `active`) is one of `active | draft | deprecated`.

Parsing rules for front-matter: `key: value` lines; lists inline as `[a, b]`; booleans as `true` / `false`;
`#` starts a comment. No nested structures — this keeps the lint tool dependency-free.

## 6) Templates

A template is a contract about **what shape knowledge takes on a page and what question the page answers**. It is
declared in the template file's own front-matter, so adding a template means adding a file:

- `repeatable` — `true` for a page shape that recurs, `false` for a singleton page (exactly one in the wiki).
- `required` — sections that must exist and hold content.
- `may_be_empty` — sections that must exist but are allowed to hold nothing. Used for registries: an empty
  `Open Questions` or `Terms` table is a valid state, not an incomplete page.
- `evidentiary` — the subset of sections whose content is observation rather than synthesis, and which therefore
  needs citations.

| Template | Answers the question | Multiplicity |
|---|---|---|
| `concept` | "What is true about X?" | repeatable |
| `howto` | "How do I do X?" | repeatable |
| `reference` | "What are the X?" (catalog / inventory) | repeatable |
| `open-questions` | "What do we not know yet?" | singleton |
| `glossary` | "What does this word mean here?" | singleton |

**Evidentiary vs synthetic sections.** Sections listed in `evidentiary` are where claims are observations and therefore
need citations. Everything else (Summary, Notes, Variants, Change Log, and the registry tables) is synthesis, a
question, or metadata. This is the generalization of the facts-first rule: facts and interpretation must never share a
section — and no claim is ever moved into `Notes` to avoid citing it.

**Choosing:** pick the template whose question shape matches. Do not force a shape — "how do I make pancakes" is a
`howto`, not a `concept`, because a `concept` page has no `Failure Modes` section and that knowledge would be lost.

**Singleton templates** must have exactly one page. Three different glossaries is a classic wiki death.

## 7) Citation policy

Format: `<scheme>:<locator>`. The `file` scheme is the default and its prefix may be omitted.

| Citation | Meaning |
|---|---|
| `raw/notes.md:12-18` | lines 12–18 of a text file (default `file` scheme) |
| `note:2026-10-01-transcript` | a registered source with no line numbers (photo, audio, card, chat) |
| `url:https://example.org/page` | a web page |
| `media:raw/card.jpg@12:30` | a point inside a media file |

The exact scheme set is declared in `PROFILE.md` under `citation.schemes`.

Rules:

- Every atomic claim in an **evidentiary** section has at least one citation.
- Put synthesis, preference, and reasoning in a non-evidentiary section (`Notes`, `Variants`, ...) — never in `Facts`.
- If a new source contradicts existing claims, **keep both** and mark the conflict. Do not silently overwrite.
- Citations are relative to the repository root, POSIX-style separators.
- **A citation must survive change.** Prefer the locator that stays valid longest under the changes this domain actually
  sees; a locator that breaks silently is a liability, not a cost of doing business. A line range over an artifact that
  moves is the most fragile form available — a last resort, never a default.
- **The anchor palette is a domain decision, made once.** Which locator forms exist here is declared in
  `citation.schemes` and settled when the wiki is initialized: propose the most change-independent palette the domain
  allows, and let the user decide. Do not invent a scheme per page.

## 8) Ingest

1. Read the source and extract **atomic** claims (one claim per record).
2. Decide retention for this source (see §9); default comes from `PROFILE.md`.
3. Register the source in `wiki/index/sources.jsonl` with `status: active`.
4. Update existing pages in preference to creating new ones.
5. Update `wiki/index.md` (link + one-line summary).
6. Append fact records to `wiki/index/index.jsonl`.
7. Append an entry to `wiki/log.md` and an event to `wiki/logs/agent.log.jsonl`.

Constraints: never edit a raw source; never duplicate an existing page; contradictions become marked conflicts.

## 9) Source lifecycle and compaction

Sources are evidence, so they are removed only under a guarded invariant:

> A raw source may be removed **only** when everything extracted from it is preserved in pages **and** every citation
> pointing to it has been re-pointed (`recite`) to something that still exists.

Four resolutions:

| `resolution` | Raw source | Citations re-pointed to | Use for |
|---|---|---|---|
| `axiomatize_remove` | deleted | the decision record in `decisions.jsonl` | normative notes whose content became policy |
| `embed_remove` | deleted | a verbatim `## Source Excerpt` section inside a page | transcripts, dictations, scratch notes |
| `archive` | moved to `raw/archive/` | the archived file itself | artifacts worth keeping but not worth working with |
| `keep` | stays | itself | evidence: books, articles, measurements, scans, photos |

Retention is chosen **per source**, not per domain; `PROFILE.md` only sets the default.

**Compaction is two-phase and manual:**

1. The keeper reports the queue: sources whose retention implies removal (`embed_remove`, `axiomatize_remove`) and
   which are either already marked `absorbed`, or still `active` past the age threshold.
2. `compact dry-run` prints one line per impact as `locator | action | details` and **requires explicit user
   confirmation**. Allowed actions: `keep`, `archive`, `delete`, `recite`.
3. `compact apply` runs **all-or-nothing**: it appends a decision row, re-points citations in pages and
   `index.jsonl`, updates `sources.jsonl` (`status` + `decision_id`), and only then removes or moves the raw files.

`dry-run` is preview-only and is never written to `log.md` or `agent.log.jsonl`.

Decision id format: `compact-YYYY-MM-DD-XXX`, where `XXX` is a zero-padded daily sequence.

An empty `decisions.jsonl` is a normal state, not a defect.

## 10) Template gaps — the palette grows and shrinks

The template palette is meant to evolve from observed use, not from speculation. Collect silently, **report only on
threshold** (nagging on every ingest destroys trust faster than silence).

Signals:

1. **Friction at write time** (strongest, and observed rather than guessed): you needed a section that does not exist,
   or you had to **drop a claim** because no section could hold it. A dropped claim is a direct knowledge loss.
2. **Repetition**: the same non-template section appears in at least `template_gap_threshold` distinct pages of the same
   template.
3. **Symmetric shrinkage**: a section declared in a template is empty in **every** page of that template (only judged
   once enough pages exist). Templates must be able to lose weight, or every page carries dead boilerplate forever.

Findings go to `wiki/logs/lint-report.json` under `template_suggestions`, and are surfaced to the user only once the
threshold is crossed. **The user decides.** Never rewrite a template or migrate pages unilaterally.

## 11) Index formats

### Line orientation (canonical form)

Every `*.jsonl` file holds **one JSON value per line**. This is a contract, not a style preference: line orientation
is what makes a registry streamable, recoverable after a truncated write, and diffable line by line.

A registry that a formatter pretty-printed is still valid JSON — no data is lost, because whitespace between JSON
values is not data. But it is no longer canonical, and the contract is **enforced rather than tolerated**: `wiki lint`
reports `registry-not-line-oriented` once and names the fixer.

The exact byte form is `json.dumps(record, ensure_ascii=False, separators=(",", ":"))` followed by `\n`. Write records
that way: a record produced by `json.dumps` with its **default** separators is valid JSON but not canonical, and
`wiki norm --check` will reject it forever. `wiki/tools/wiki_jsonl.py` holds this definition once, for the tools; it is
the same shape you have to write by hand.

```
wiki norm -w wiki/index          # canonicalize every registry in the directory
wiki norm --check wiki/index     # CI: exit 1 if anything is not canonical
```

Targets may be files or directories (one level deep). Prefer directories in documentation: PowerShell and cmd do not
expand `*.jsonl` for external programs, so a glob in an example silently does nothing there.

`norm` is a separate tool from `lint` on purpose. A mutation must not hide behind a flag on a read-only check, and
re-serializing is faithful to the JSON data model but not to the original bytes, so it deserves to be an explicitly
named operation.

### `wiki/index/index.jsonl`

One JSON object per line:

- `fact_id` (stable string, unique), `page` (path relative to repo root), `statement` (one atomic claim),
  `citations` (array), `tags` (array), `updated_at` (ISO-8601 UTC), `confidence` (`high|medium|low`),
  `conflict` (boolean).

Keep the `statement` atomic: one verifiable claim, not a paragraph.

### `wiki/index/sources.jsonl`

One JSON object per line:

- `id` (stable, unique), `locator` (path or URI of the raw source), `kind`, `hash`, `added_at`, `last_seen`
- `retention`: `axiomatize_remove | embed_remove | archive | keep | undecided`
- `status`: `active | absorbed | archived | dropped`
- `decision_id`: `null` while the source is live; set when a compaction decision covers it.

### `wiki/index/decisions.jsonl`

One JSON object per line: `decision_id`, `ts`, `requested_by`, `raw_sources`, `wiki_targets`, `resolution`,
`replacement_citation`, `status` (`approved|applied`), `notes`.

### `wiki/logs/agent.log.jsonl`

One JSON event per line: `ts`, `run_id`, `agent`, `operation`, `status`, `inputs`, `outputs`, `notes`.

### `wiki/log.md`

Append-only, newest first. One block per operation:

```markdown
## [YYYY-MM-DD] <operation> | <title>

- operation: ingest | query | decision | lint | compact | bootstrap
- inputs: ...
- outputs: ...
- notes: ...
```

## 12) Query

1. Start at `wiki/index.md`.
2. Open only the pages whose summaries match.
3. Answer **only** from cited statements. For uncertain areas answer `unknown` and list the missing evidence.
4. When the wiki is silent, the silence itself is always declared (§16). What happens next — whether outside knowledge
   may be used at all — is governed by the knowledge boundary (§16) and `external_subject` in `PROFILE.md`.
5. Store durable, high-value answers as pages, and only with a citation that can be opened (§16).

## 13) Tools

Two tools, each doing one job, plus a launcher whose only job is to find a **real** Python interpreter (a `python`
on PATH can be a Microsoft Store stub, so the interpreter is probed rather than merely located — and that probe lives
in exactly one place).

```
wiki lint                     read-only — structure, citations, index integrity, singletons, source queue, template gaps
wiki norm -w <targets>        mutating — canonicalize *.jsonl registries to one record per line
wiki norm --check <targets>   read-only — exit 1 if any registry is not canonical
```

`<targets>` are `*.jsonl` files or directories containing them, searched one level deep.

- Windows: `wiki\tools\wiki.cmd lint`
- POSIX: `./wiki/tools/wiki.sh lint`
- Standalone (the tools are separate programs): `python wiki/tools/wiki_lint.py`, `python wiki/tools/wiki_norm.py`

Configuration is read from `PROFILE.md` and from the template front-matter — the tools hardcode nothing about this
domain. Lint output goes to `wiki/logs/lint-report.json`.

**Lint is optional.** The wiki must remain fully usable with an agent and markdown alone. If Python is missing, `lint`
prints a message and exits 0; `norm` fails loudly, because it genuinely cannot work without Python.

## 14) Change safety

- Changes under `wiki/**` may be made without extra confirmation.
- Never modify raw sources.
- `scratch/` is a workspace, not a knowledge base: write there freely, delete from there freely, and cite nothing
  from it (§17).
- Never touch code or files outside the wiki tree, `raw/`, and `scratch/`.
- Keep edits precise. Do not rewrite whole pages when a targeted edit will do.

## 15) Talking to the user

The wiki is built in conversation. This holds in every harness: if the environment offers structured input widgets —
option boxes, forms, confirmation dialogs — treat them as the rare exception, not the default way to ask.

- **Open-ended questions are asked in plain chat.** Domain, purpose, source kinds, and intent have no answer list. A
  multiple-choice box narrows the answer and discards the reasoning behind it.
- Options are acceptable only for a genuinely closed decision, **and always with the answer left open** — the user must
  be able to say something the options do not cover.
- **Never let a widget be the only channel.** A question that cannot be answered by picking an option belongs in chat.
- **Confirmations are asked in chat, with the concrete change spelled out.** Compaction, template edits, page
  migrations: name the files and the statements, then let the user answer in their own words. A yes/no button hides
  what is about to happen, and what is about to happen is often irreversible.
- A checklist is not a script. Cover what is needed in whatever order the conversation goes, and follow up on answers —
  including answers that contradict each other.

## 16) Knowledge boundary

Evidence is what the wiki itself holds: immutable raw sources, and pages citing them. Nothing else is evidence — and
the boundary matters most at the point where a helpful answer would otherwise quietly become knowledge (see §7 and §12).
Repository files that are neither raw sources nor pages are not evidence either: that a document is nearby and easy
to read says nothing about whether it may be cited (§17).

Three channels, and only two leave a trace:

| Channel | Traceable? | May be evidence? |
|---|---|---|
| Wiki pages and raw sources | yes — the citation opens a file | yes |
| Tools (search, fetch) | yes, if cited as `url:` | only as an external-cited claim |
| Model memory (pretrained) | **no trace at all** | **never** |

### Method, subject, memory

External knowledge is not one thing. Ask what it does:

- **Method** — a general skill applied to input the user supplied: decoding a cipher, arithmetic, translation, a regex,
  a format conversion. It asserts nothing about the subject of this wiki. Always allowed, always labelled.
- **Subject** — a claim about the very thing this wiki is about. It competes with the wiki, may describe a different
  version than the user's, and may spoil an experience the user is deliberately having first-hand. Governed by
  `external_subject` in `PROFILE.md`.
- **Model memory** — neither. Unverifiable, because there is no artifact to open.

### Absence is always declared

This is an invariant, not a policy, and it follows from §12: when the wiki does not answer, say so plainly — "the wiki
has no information on this" — and name the evidence that would settle it. Never fill the gap quietly, and never go
silent either. Only what happens **after** that declaration depends on the policy.

### `external_subject` policies

| Value | After the wiki is found silent |
|---|---|
| `forbidden` | Stop. Say that external sources are switched off by the profile, so the user knows it is a choice and can change it. Offer to record whatever the user verifies first-hand. |
| `ask` (default) | Offer without revealing: "this is outside the wiki and may be a spoiler — look it up?" Reveal only after a yes. |
| `labeled` | Answer, with the external part visibly separated and marked as not from this wiki. |
| `open` | Answer normally. |

### Answer format

Keep the channels visibly apart:

```
From the wiki:
- ...  - wiki/pages/quests.md:12-14

Outside the wiki (unverified, not from your own notes):
- ...
```

### The storage invariant never relaxes

Chat policy is configurable; storage policy is not. **An outside claim becomes a page only with a citation that can be
opened** — a `url:` the user accepted, or the user's own observation recorded as a raw note first. Model memory never
becomes a page: if it looks worth keeping, it goes to the singleton `open-questions` page as something to verify, or the
user is asked to confirm it and the confirmation is written to `raw/` first.

This is what makes the boundary enforceable at all. Raw sources are immutable and retained, so a fabricated citation is
**detectable** — the user can open the file at the cited lines and find nothing there. Lint cannot tell a true citation
from a false one; only a human can. The mechanism does not assume an honest model, it makes claims checkable.

## 17) Scratch — the transient workspace

A page states what is true now. A fix plan, a debugging breakdown, or the plan for a large task is a different kind of
artifact: it is not knowledge, it is the thread of work in progress, and its job is to survive between sessions and then
be discarded. `scratch/` is the home for those artifacts.

- **It is not part of the knowledge base.** No front-matter, no template, no citations, no entry in `index.md`, no fact
  record, no `log.md` entry, no lint. A workspace artifact is never evidence, and nothing in `scratch/` is ever cited.
  The direction is one-way: scratch may read pages and raw sources as context, never the reverse.
- **Scratch cannot be used to dodge the citation rule.** A claim is not evidence because it is written down; it is
  evidence when a source that can be opened says so. A rationale invented into a scratch file, or a model's own memory
  quoted there, is worth exactly as much as it was before it was written down (§16).
- **Nothing in `scratch/` is immutable**, and deleting it — or replacing it wholesale when a task pivots — is normal.
  A page, by contrast, is not deleted to make room for a new idea.
- **A page is never a transcription of a scratch file.** If something learned while working belongs in the wiki, it
  enters the way everything else does: as a raw source under `raw/`, registered and retained, or as a page resting on
  citations that already exist.
- **Whether anything ever leaves `scratch/` is a domain decision.** A wiki where scratch is discarded at the end of
  every task is a perfectly valid configuration, and so is one where the plan becomes a page.

Working rules: keep a live workspace artifact to one topic and one task — it is a place to hold focus, not a second
wiki; and treat an artifact nobody has opened in weeks as finished rather than as pending.

**The kernel provides the zone, not a shape.** This contract declares no `plan` template, registers no workspace file as
a source, and ties no page to a working document. It also does not police the boundary with the lint tool: the rules
above are a contract between agent and user, and the checker stays structural. If the domain shows over time that "what
to do next" really is a recurring page shape, it becomes a template by the usual observed-use route (§10), and the user
decides.

Whether `scratch/` exists in a given wiki is settled once, in `BOOTSTRAP.md` (Phase 1). If the domain has no temporary
working documents, the directory is simply absent and nothing else changes.
