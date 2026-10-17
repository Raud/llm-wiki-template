# llm-wiki-template

> **This is an example branch.** The same template, initialized for the domain "company IT infrastructure": an incident chat
> excerpt, two editions of a runbook, an inventory export, five pages and 34 cited facts, a green `lint`. The second example
> built on the same kernel is `example/books` (book notes); the template without a domain lives in `main`. Change anything.
>
> **All data is invented.** The company «Северный Ветер», its servers, chat and runbooks do not exist: addresses, ports and
> wording are made up to show the shape of the pages. The citations are honest, though — they open lines of files in
> `raw/`, and the quoted text is really there.
>
> **Where to start looking:** `wiki/pages/backup-policy.md` — two runbook editions contradict each other, both are kept, the
> conflict is marked and was not resolved by the agent. And `external_subject: forbidden` in the profile: the agent does not
> guess about its own infrastructure, it says "the base has nothing on this".

<!-- languages: this file is en, the Russian original is README.md -->
[Русский](README.md) · **English**

**A folder for a knowledge base that an AI agent maintains — and every fact in it carries a citation you can open.**

Download → half an hour of talking to the agent → you accumulate knowledge that does not fall apart a year later and that
you can verify without asking the agent again.

## What a knowledge base is

The easiest way to explain it is by contrast with notes. A note you write for yourself, once. A knowledge base holds what
you will need to **ask again in a month** — by which time you no longer remember the details, and the original
conversation, book or chat is long gone. Hence the word "base": not a folder of files, but a store you come back to.

Two properties follow from that, and without them a knowledge base turns into a junk drawer:

- **Order.** A year later there must be something to find. Without a table of contents, grouping, and titles that do not
  lie about their contents, any collection of notes becomes an archive nobody opens.
- **Trust.** You have to be able to lean on what is written down. If you do not remember where a number came from, you do
  not have knowledge, you have hearsay: next time you will re-verify everything from scratch, and it is as if the base
  never existed.

There are plenty of tools for this — from Confluence to Obsidian. This template is about order and trust too, with one
correction: the agent does the writing, you do the checking. So here neither property is "supposed to be honoured" — both
are built into the rules: mandatory sections, mandatory citations, and a checker that fails without them. The difference
starts there, and it is described below.

## What this is

This is not an application and not a service: **there is nothing to run, no button to press.** It is a folder of rules
plus an empty wiki that you fill in together with the agent — in chat, in an editor, wherever you like. All of its content
is plain markdown files and a `raw/` folder with source material.

The idea is simple. An agent can read anything and remembers nothing. This folder is a place where it writes down what it
found in a way you can verify: **sources here are evidence and never change**, pages are built from them, and every
concrete claim carries a citation that opens at a specific line of the source.

The payoff is not that the agent knows more. The payoff is that you can tell what it **found** from what it **made up** —
today and a year from now. And when the base has no answer, the agent has to say "the base has nothing on this" instead of
inventing something plausible.

## What it is good for

- **Notes on books and lectures** — when you do not want to reread the source, but you do need to know where something was
  said.
- **Project notes** where the number matters: who decided it, when, and on what grounds.
- **Debriefing interviews and calls**: who said what — with a citation, not a retelling from memory.
- **Family and household knowledge**: recipes, "how we do it at home", the medicine cabinet, the garden, repairs.
- **Research on a topic** assembled from articles and links: what the sources claim, and where they contradict each other.
- **A spoiler-safe base** for a book, a series or a game: the facts kept apart from your own impressions.

**When it does not fit.** For quick napkin notes the overhead is not worth it. For plans and tasks in progress there is
`scratch/`, and that is not knowledge. And if you are not comfortable with the material sitting on disk in the open, this
is not the tool for secrets.

## What it looks like

Before — the note it all started from (`raw/notes/pomodoro.md`):

```
12  Pomodoro: 25 minutes of work, 5 minutes of rest. Invented by Francesco Cirillo in the late 1980s.
13  The name comes from a kitchen timer shaped like a tomato.
```

After — the page (`wiki/pages/pomodoro.md`):

```markdown
## Facts

1. The pomodoro technique is 25 minutes of work and 5 minutes of rest — `raw/notes/pomodoro.md:12`
2. The name of the technique comes from a kitchen timer shaped like a tomato — `raw/notes/pomodoro.md:13`

## Notes

- It only suits tasks that cut into 25-minute chunks — mine do not.
```

Every line in `Facts` opens in the source file — you can check it yourself. Your own conclusions and preferences live in
`Notes` and are never passed off as fact. That is the whole trick: **fact and opinion never share a section**, which is
what makes a citation worth anything.

## Why this is not Notion or Confluence

The short answer: **not a replacement, a different genre.** Notion, Confluence and Obsidian are places where a human
writes and where evidence is optional: you can add a link or leave it out, and nobody will notice the difference. Here the
agent writes, and a citation is part of the record: its absence or a malformed one is an error the linter catches.

| | Notion / Confluence / Obsidian | here |
|---|---|---|
| who writes | a human | an agent writes, a human checks |
| unit of knowledge | a document | an atomic cited fact plus a page that answers a question |
| evidence | a link, optional | a citation, mandatory, format-checked |
| in a year | unclear what to believe | visible what was found and what was invented |
| collaboration | comments, permissions, live editing | no: not what the template is for |

And where it loses, honestly, no asterisks: **five editors at once, comments, access permissions, a mobile client,
full-text search out of the box.** If that is exactly what you need, take Confluence; that is what it is built for.

A caveat so this does not read as a dodge. Collaboration is handled by **git**: branches, diffs, review, edit history,
rollback. The template stays out of it not out of modesty, but to avoid doing two things badly at once. Its own subject is
the other half of the job: **making what is written down true, not making it convenient for five people to write**. The
division works out like this: git answers "who changed this, and when", citations answer "where did this come from", and
the linter sees to it that the second has not drifted over time.

## Live examples

You can build very different knowledge bases from this template. Here are two: they share the same kernel, and only one
file changes per domain — `wiki/PROFILE.md`.

- [`example/books`](https://github.com/Raud/llm-wiki-template/tree/example/books) — notes on a book: 2 sources, 4 pages,
  22 facts, `external_subject: ask` (book spoilers), `file` + `url` citation schemes.
- [`example/it-infra`](https://github.com/Raud/llm-wiki-template/tree/example/it-infra) — company infrastructure:
  4 sources, 5 pages, 34 facts, a **marked conflict** between two editions of a runbook, `external_subject: forbidden`,
  `file` + `note` schemes.

## How to start

1. **Download the folder** — `Code → Download ZIP` on GitHub, or `git clone`.
2. **Open it with an agent that can see files.** Claude Projects (upload the files into the project), Cursor, Claude Code,
   ChatGPT with files will do. Important: in an ordinary web chat the agent cannot see a folder — you have to attach the
   files by hand.
3. **Say one sentence:** "Read `BOOTSTRAP.md` and initialize this wiki for my task." It will ask a few questions about the
   domain, the sources and the language — and create the profile and the skeleton.
4. **Give it the first real material** — text, a file, a link. The wiki must not stay empty: initialization ends with one
   real source ingested. From that point you can work.

After that the loop is simple: drop a source into `raw/` → "ingest this" → ask something → durable answers become pages.

## What lives where

```
raw/                     immutable sources — the evidence
scratch/                 transient working documents — never cited, never counted as knowledge
wiki/PROFILE.md          domain profile — the only domain-specific file
wiki/pages/              pages (flat)
wiki/templates/          page templates (concept, howto, reference, open-questions, glossary)
wiki/index/              registries: facts, sources, compaction decisions (one record per line)
wiki/tools/              launcher and tools: lint (checker) and norm (formatter)
AGENTS.md                operating contract (domain-agnostic, never edited per domain)
BOOTSTRAP.md             the initialization prompt
```

## Checks (optional)

Everything works without them: a wiki is markdown. The tools exist to catch drift like a broken citation or a page missing
from the index. Python 3.9+, no dependencies.

```powershell
.\wiki\tools\wiki.cmd lint
.\wiki\tools\wiki.cmd norm -w wiki\index
```

```sh
./wiki/tools/wiki.sh lint
./wiki/tools/wiki.sh norm --check wiki/index
```

`norm` takes files or directories, so the command is the same in any shell: PowerShell does not expand `*.jsonl` for
external programs.

## License

[MIT-0](LICENSE) — no attribution required. A template must not put a legal to-do in front of every copy of itself, and
nothing here distinguishes "code" from "content": the tools, the contract, the templates and the skeleton are all under
the same terms. Pages you write into your own copy are yours, under whatever terms you choose.
