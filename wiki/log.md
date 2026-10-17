# Wiki Log

Append-only timeline of operations, newest first. One block per operation.

## [2026-10-17] ingest | Чат инцидента 2026-09-12

- operation: ingest
- inputs: raw/infra/incident-2026-09-12-chat.md
- outputs: wiki/pages/backup-policy.md, wiki/pages/restore-a-backup.md, wiki/pages/open-questions.md, wiki/pages/glossary.md
- notes: chat registered with retention embed_remove; the conversation is embedded verbatim in a Source Excerpt section, so the raw copy can be compacted once the user approves. 34 fact records across five pages in total.

## [2026-10-17] ingest | Рунбуки и инвентарь

- operation: ingest
- inputs: raw/infra/runbook-backup-2024.md, raw/infra/runbook-backup-2026.md, raw/infra/inventory-2026-10-01.txt
- outputs: wiki/pages/servers.md, wiki/pages/backup-policy.md, wiki/pages/restore-a-backup.md, wiki/index.md
- notes: the two runbook editions contradict each other on backup time and retention; both kept, conflict flagged in index.jsonl, resolution left to a human with a document

## [2026-10-17] bootstrap | IT-инфраструктура компании

- operation: bootstrap
- inputs: BOOTSTRAP.md, AGENTS.md
- outputs: wiki/PROFILE.md, wiki/index.md, wiki/pages/open-questions.md, wiki/pages/glossary.md
- notes: domain "company IT infrastructure"; chat excerpts embed_remove, runbooks and inventory keep; external_subject forbidden because guessing about your own infrastructure is worse than silence
