# wiki-template

A domain-agnostic kernel for a **persistent knowledge wiki maintained by an LLM agent together with a human**.

The idea is simple: sources are evidence, pages are the product, and every concrete claim carries a citation. That
makes the wiki re-verifiable instead of an opinion pile — and it lets an agent write into it without inventing facts.

## Layout

```
raw/                     immutable source material
scratch/                 transient working documents — never evidence, never cited
wiki/PROFILE.md          domain profile — the ONLY domain-specific file
wiki/pages/              pages (flat)
wiki/templates/          template palette (concept, howto, reference, open-questions, glossary)
wiki/index/              registries: facts, sources, compaction decisions (all one record per line)
wiki/tools/              launcher and tools: lint (checker), norm (formatter)
AGENTS.md                operating contract (domain-agnostic, never edited per domain)
BOOTSTRAP.md             the initializing prompt
```

## Initialization

Give `BOOTSTRAP.md` to an agent in a copy of this folder. It interviews you with six questions, writes
`wiki/PROFILE.md`, creates the skeleton, and ingests one real item so the wiki never starts empty.

## Quick workflow

1. Drop a source into `raw/`.
2. Ask the agent to ingest it — it updates pages, `index.md`, `index.jsonl`, and the logs.
3. Ask questions; durable answers become pages.
4. Run lint occasionally and review `wiki/logs/lint-report.json`.

```powershell
.\wiki\tools\wiki.cmd lint
.\wiki\tools\wiki.cmd norm -w wiki\index
```

```sh
./wiki/tools/wiki.sh lint
./wiki/tools/wiki.sh norm --check wiki/index
```

`norm` takes files or directories, so the same command works in every shell — PowerShell does not expand `*.jsonl`
for external programs.

## Design decisions worth knowing

- **Flat pages, no numbering.** A path encodes stable identity only. Templates and status change over time; if they
  lived in the path, changing them would break every citation and inbound link.
- **`scratch/` is deliberately not a second wiki.** Working documents — a fix plan, a breakdown, a task in progress —
  need to survive between sessions without pretending to be knowledge: no citations, no templates, no index, no lint.
  Nothing there is evidence, and whether anything ever leaves it is the domain's decision, not the kernel's.
- **Facts and interpretation never share a section.** Each template declares which sections are evidentiary (citations
  required) and which are synthesis.
- **Nothing is deleted without re-pointing its citations.** Source cleanup is a two-phase, all-or-nothing, logged
  operation.
- **The template palette grows from use.** A quiet collector watches for repeated structure and for sections that are
  never filled, and proposes changes only past a threshold.
- **One registry format, one canonical shape.** Every `*.jsonl` file is one record per line: streamable, recoverable
  after a truncated write, and diffable line by line.
- **The checker and the formatter are separate tools.** `lint` never writes; `norm` canonicalizes. A mutation behind a
  `--fix` flag makes "I just ran the lint" a dangerous habit and muddies exit codes.
- **Tools are optional.** Python 3.9+ with no dependencies, no venv. The wiki works without them; `lint` says so and
  exits cleanly rather than blocking anything.
