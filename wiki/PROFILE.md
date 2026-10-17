# Domain Profile

> **This is the only domain-specific file in the wiki.** It is written once by `BOOTSTRAP.md` and edited afterwards
> when the domain changes. `AGENTS.md` is domain-agnostic and must not be edited per domain.
>
> The block at the bottom is read by the lint tool. It must stay valid JSON.

## Domain

Конспекты книг: что книга утверждает, и чем это подтверждается. Одна книга — один набор выписок в `raw/`, страницы
собираются вокруг вопросов, а не вокруг глав.

## Readers

Владелец — один человек, который читает и конспектирует. Агент пишет страницы и отвечает по ним; другие люди читают
редко и только по ссылке.

## Sources

| Kind | Where | Default retention |
|---|---|---|
| Выписки из книги: цитаты с номерами страниц | `raw/books/` | `keep` |
| Собственные заметки после чтения | `raw/books/` | `keep` |

Заметки после чтения — тоже источник, но он даёт не факты, а мнение: их место в `Notes` и в `Open Questions`, не в
`Facts`.

## Content language

Русский. Служебные записи (`log.md`, реестры, front-matter) остаются английскими.

## Exclusions

Чужие личные данные, рабочие документы под NDA и что угодно, что нельзя показывать третьим лицам. Выписки — это
цитаты из изданной книги, а не внутренние материалы.

## Knowledge boundary

`ask`. Книги содержат спойлеры, а иногда и ответ на загадку, которую человек ещё читает: агент не пересказывает
содержание за пределами выписок, не спросив. Если в вики ответа нет, он говорит это прямо и предлагает посмотреть
вовне.

## Notes

- Номера страниц в выписках — по бумажному изданию 2024 года («Редкий шрифт»); в электронной версии они не совпадут
  никогда, поэтому цитата всегда идёт с диапазоном строк файла выписок, а не только с номером страницы.
- Одна книга — один конспект. Не сливаем две книги в одну страницу: тогда цитата перестаёт говорить, откуда она.

## Machine Config

```json
{
  "initialized": true,
  "content_language": "ru",
  "external_subject": "ask",
  "pages_dir": "wiki/pages",
  "templates_dir": "wiki/templates",
  "citation": {
    "default_scheme": "file",
    "schemes": {
      "file": "^\\S+:\\d+(-\\d+)?$",
      "url": "^url:https?://\\S+$"
    }
  },
  "reserved_sections": ["Source Excerpt"],
  "template_gap_threshold": 3,
  "min_pages_for_shrink_suggestion": 3,
  "compaction_candidate_after_days": 14,
  "required_front_matter": ["template"]
}
```
