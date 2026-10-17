# Domain Profile

> **This is the only domain-specific file in the wiki.** It is written once by `BOOTSTRAP.md` and edited afterwards
> when the domain changes. `AGENTS.md` is domain-agnostic and must not be edited per domain.
>
> The block at the bottom is read by the lint tool. It must stay valid JSON.

## Domain

IT-инфраструктура компании «Северный Ветер»: что у нас есть, как это обслуживается и откуда мы это знаем. Не учебник по
PostgreSQL и не зеркало документации — то, что нужно ночью, когда что-то сломалось.

## Readers

Команда эксплуатации, четыре человека, и дежурный, который может быть из них любым. Агент читает эту базу первой и отвечает
дежурному; другие команды заходят по ссылке.

## Sources

| Kind | Where | Default retention |
|---|---|---|
| Выписка из чата инцидента | `raw/infra/` | `embed_remove` |
| Рунбук (одна редакция — один файл) | `raw/infra/` | `keep` |
| Выгрузка инвентарного учёта | `raw/infra/` | `keep` |

Выписка чата — `embed_remove`: после того как разговор перенесён на страницы (в том числе дословно, в раздел
`## Source Excerpt`), копию чата можно удалить. Цитаты при этом не должны сломаться — их перевешивают на страницу.

## Content language

Русский. Служебные записи (`log.md`, реестры, front-matter) остаются английскими.

## Exclusions

Пароли, ключи, токены, приватные адреса за пределами `10.10.0.0/16`, персональные данные клиентов. Правило простое: если
сомневаешься — не пиши, репозиторий читают все, у кого есть доступ.

## Knowledge boundary

`forbidden`. Это собственная инфраструктура: если в базе чего-то нет, значит этого нет. Агент не додумывает ни порты, ни
пути, ни адреса и не подставляет «как обычно бывает в таких системах» — он говорит, что в базе этого нет, и предлагает
посмотреть инвентарь или рунбук. Догадка здесь дороже молчания.

## Notes

- Конфликт редакций рунбука — нормальное состояние, а не ошибка ингеста: обе редакции сохранены, конфликт помечен в
  `wiki/index/index.jsonl`, разрешает его человек документом, а не агент разговором.
- Скриншот из чата, у которого нет строк, регистрируется как источник и цитируется схемой `note:`, когда цитировать строку
  не из чего.
- Рабочие документы на время разбора инцидента можно держать в `scratch/` — но то, что должно быть верно завтра, идёт на
  страницы, а не туда.

## Machine Config

```json
{
  "initialized": true,
  "content_language": "ru",
  "external_subject": "forbidden",
  "pages_dir": "wiki/pages",
  "templates_dir": "wiki/templates",
  "citation": {
    "default_scheme": "file",
    "schemes": {
      "file": "^\\S+:\\d+(-\\d+)?$",
      "note": "^note:[a-z0-9][a-z0-9._-]*$"
    }
  },
  "reserved_sections": ["Source Excerpt"],
  "template_gap_threshold": 3,
  "min_pages_for_shrink_suggestion": 3,
  "compaction_candidate_after_days": 14,
  "required_front_matter": ["template"]
}
```
