# Domain Profile

> **This is the only domain-specific file in the wiki.** It is written once by `BOOTSTRAP.md` and edited afterwards
> when the domain changes. `AGENTS.md` is domain-agnostic and must not be edited per domain.
>
> The block at the bottom is read by the lint tool. It must stay valid JSON.

## Domain

_Not initialized._ Name and one-sentence purpose go here.

## Readers

_Not initialized._ Who reads this wiki: the owner alone, a team, agents, a mix.

## Sources

_Not initialized._ Table of source kinds, where they live, and the default retention for each.

| Kind | Where | Default retention |
|---|---|---|
| | | |

## Content language

_Not initialized._ The language page content is written in. Service records stay English regardless.

## Exclusions

_Not initialized._ Anything that must never be stored here. Delete this section if there is nothing to exclude.

## Knowledge boundary

_Not initialized._ What the agent may use when the wiki itself is silent — see `AGENTS.md` §16.

- `forbidden` — never use outside knowledge about this subject; say the wiki is silent and stop.
- `ask` — offer, do not reveal, until the user says yes. Safe default for anything with spoilers.
- `labeled` — answer, with the outside part visibly marked as not from this wiki.
- `open` — answer normally.

Whichever value is set, the absence of an answer is always stated plainly, and outside knowledge never becomes a page
without a citation that can be opened.

## Notes

_Not initialized._ Anything else the agent must know about this domain — conventions, special cases, external systems
the sources come from.

## Machine Config

```json
{
  "initialized": false,
  "content_language": null,
  "external_subject": "ask",
  "pages_dir": "wiki/pages",
  "templates_dir": "wiki/templates",
  "citation": {
    "default_scheme": "file",
    "schemes": {
      "file": "^\\S+:\\d+(-\\d+)?$",
      "note": "^note:[a-z0-9][a-z0-9._-]*$",
      "url": "^url:https?://\\S+$",
      "media": "^media:\\S+@\\d{1,2}:\\d{2}(:\\d{2})?$"
    }
  },
  "reserved_sections": ["Source Excerpt"],
  "template_gap_threshold": 3,
  "min_pages_for_shrink_suggestion": 3,
  "compaction_candidate_after_days": 14,
  "required_front_matter": ["template"]
}
```
