# BOOTSTRAP — initialize this wiki for a new domain

You are initializing a fresh knowledge wiki from the `wiki-template` kernel. Your job is to turn a generic skeleton
into a working, domain-specific wiki, and to prove it works by ingesting one real item.

Work through the phases in order. Do not skip Phase 1, and do not skip Phase 4.

## Phase 0 — Load context

1. Read `AGENTS.md` in full. It is the operating contract and it does not change per domain.
2. List `wiki/templates/` and read the front-matter of each template: `required` and `evidentiary` sections,
   `repeatable` or singleton.
3. Read `wiki/PROFILE.md` — you will be rewriting it.

## Phase 1 — Interview

This is a conversation, not a form. Ask in plain chat and wait for answers; do not proceed on guesses.

Cover these seven things before writing the profile. The list is a **checklist, not a script** — work through it in
whatever order the conversation goes:

1. **Domain** — what is this wiki about, in a name and one sentence?
2. **Readers** — who will read it: only the user, a team, other agents, a mix?
3. **Sources** — what material will be fed in, and where does it live? For each kind, ask for the default retention:
   - `keep` — evidence worth keeping forever (books, articles, measurements, scans, photos)
   - `embed_remove` — transcribed into a page verbatim, then the raw copy is disposable (dictations, scratch notes)
   - `axiomatize_remove` — normative notes whose content becomes policy
   - `archive` — worth storing, not worth working with
4. **Content language** — in what language should page content be written? Service records stay English regardless.
5. **Exclusions and boundary** — is there anything that must never be stored in this wiki? And when the wiki is silent,
   may the agent use outside knowledge about the subject (`external_subject`): `forbidden`, `ask`, `labeled`, or
   `open`? Recommend `ask` and explain in one line what it means.
6. **First item** — one real thing to ingest right now: paste text, give a file path, or describe it. The wiki must not
   ship empty.
7. **Working scratch** — will there be temporary documents that need to survive between sessions but are not knowledge:
   a fix plan, a breakdown of a bug, the plan of a large task? If yes, this wiki gets a `scratch/` directory, described
   in `AGENTS.md` §17. Say plainly what it is for: the agent can write there without citations or templates, nothing
   there is ever cited or counted as knowledge, and **it is not a second wiki**. If the user has no such documents, skip
   the directory — that is a normal configuration, not a gap. Do not ask what should happen to material leaving
   scratch: that is a working habit the user develops, not a setting, and the contract leaves it open on purpose.

How to ask:

- Ask in ordinary messages, in small batches. React to what the user actually said and follow up; do not paste all of
  them at once as a numbered form.
- **Do not put open-ended questions into a fixed-choice widget or an options box.** "What is this wiki about?" has no
  answer list, and forcing one narrows the answer and discards the reasoning behind it. If a question cannot be
  answered by picking an option, it belongs in chat.
- Offer options only for a genuinely closed decision, and always leave the answer open — the user must be able to say
  something the options do not cover.
- Never let a widget become the only channel for a question.
- If the user answers something else entirely, follow them. The goal is a correct profile, not a completed form.

Do **not** ask which templates the user wants. Start from the five that ship (`concept`, `howto`, `reference`,
`open-questions`, `glossary`), tell the user they exist and are editable, and let the palette evolve from actual use
(see `AGENTS.md` §10).

## Phase 2 — Write the profile

Rewrite `wiki/PROFILE.md`:

- Fill the prose sections from the interview (domain, readers, source kinds with default retention, content language,
  exclusions, knowledge boundary). Keep it short — a profile is a routing table, not an essay.
- If the wiki has a `scratch/` workspace, say what it is for in the profile's Notes section: one line naming the kind of
  working document this domain produces. Do not describe a shape for it and do not add a template — the workspace has
  no contract to configure (§17).
- Fill the **Machine Config** JSON block: set `initialized` to `true`, set `content_language`, prune
  `citation.schemes` to the schemes this domain actually needs (keep `file`; drop `url`/`media`/`note` if unused —
  but keep `note` if any source lacks line numbers).
- Set `external_subject` from the interview (see `AGENTS.md` §16). Recommend `ask` when the domain has spoilers or an
  experience the user is having first-hand; `labeled` for ordinary reference domains.
- Keep `template_gap_threshold` at 3 unless the user asks otherwise.
- The JSON block must stay valid JSON — the lint tool parses it.

## Phase 3 — Create the skeleton

1. **Singletons first.** Create `wiki/pages/open-questions.md` and `wiki/pages/glossary.md` from their templates. They
   always exist, even when nearly empty.
2. **Reset `wiki/index.md`** — replace the placeholder with sections for the templates this domain will actually use,
   under the domain's own title.
3. **Registries stay empty but valid.** `wiki/index/index.jsonl`, `wiki/index/sources.jsonl` and
   `wiki/index/decisions.jsonl` are empty files. An empty registry is a valid state, not an incomplete one — but keep
   them as files, because a missing registry is a warning at lint time.
4. **`scratch/` if the interview asked for it.** Create the directory with a `.gitkeep` so it survives an empty state,
   and nothing inside it. No README, no template, no sample plan: a placeholder would suggest both a required shape and
   a permanence that §17 denies. If the domain has no temporary working documents, do not create it.
5. **Log the bootstrap.** Add the first block to `wiki/log.md`:

   ```markdown
   ## [YYYY-MM-DD] bootstrap | <domain name>

   - operation: bootstrap
   - inputs: BOOTSTRAP.md, AGENTS.md
   - outputs: wiki/PROFILE.md, wiki/index.md, wiki/pages/open-questions.md, wiki/pages/glossary.md
   - notes: <one line on the domain and the chosen default retention>
   ```

   Append the matching event to `wiki/logs/agent.log.jsonl`.

Do **not** pre-create empty `concept` / `howto` / `reference` pages. Pages are created when there is something real to
put in them.

## Phase 4 — First ingest (mandatory)

Take the item from question 6 and run the normal ingest flow from `AGENTS.md` §8:

1. If it is a file, put it in `raw/` first (never edit it afterwards). If it is pasted text, save it as a raw source.
2. Register it in `wiki/index/sources.jsonl` with the agreed `retention` and `status: active`.
3. Pick the template whose question shape matches — do not default to `concept` out of habit.
4. Create one page and fill it properly: every claim in an evidentiary section gets a citation.
5. Update `wiki/index.md`, append facts to `wiki/index/index.jsonl`, append to `wiki/log.md` and
   `wiki/logs/agent.log.jsonl`.

If, while filling the page, you need a section that the template does not have, or you have to leave a claim out for
lack of a section — record that as a template gap (see `AGENTS.md` §10). This first ingest is where such friction is
most visible.

## Phase 5 — Verify and report

1. Run `wiki lint` (Windows: `wiki\tools\wiki.cmd lint`; POSIX: `./wiki/tools/wiki.sh lint`). If Python is
   unavailable, say so and perform the same checks by hand against `wiki/tools/README.md` — lint being unavailable
   must not block the bootstrap.
2. Fix every error. Warnings may be reported as-is.
3. Report to the user:
   - the domain as captured in `PROFILE.md`, and the default retention you set;
   - which templates are live and which pages exist;
   - any template gap you hit;
   - what to do next (where to drop sources, how to ask questions).

## Guardrails

- Write only inside the wiki tree and the workspace: `wiki/**`, `raw/**`, `scratch/**`. Never touch anything else.
  Never write into `scratch/` anything that has to be true tomorrow — that is what pages are for (§17).
- All service records in English; page content in the profile's content language.
- No padding. One real page beats five empty ones.
- If the user has not answered the interview, stop and ask — do not fill the profile with placeholders.
