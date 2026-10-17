# llm-wiki-template

**Папка для базы знаний, которую ведёт ИИ-агент, — но каждый факт в ней снабжён цитатой, которую можно открыть.**

Скачал → поговорил с агентом полчаса → складываешь знание, которое не разваливается через год и которое можно проверить,
не спрашивая агента заново.

## Что такое база знаний

Проще всего объяснить через отличие от заметок. Заметку вы пишете для себя и на один раз. В базу знаний кладут то, что
понадобится **спросить снова через месяц** — а к тому моменту вы уже не помните подробностей, и исходный разговор, книга
или чат давно потерялись. Отсюда и слово «база»: это не папка с файлами, а запас, к которому возвращаются.

Из этого следуют два свойства, без которых база знаний превращается в свалку:

- **Порядок.** Через год в ней должно быть что найти. Без оглавления, группировки и названий, которые не врут о
  содержимом, любая коллекция заметок становится архивом, куда никто не заходит.
- **Доверие.** На записанное должно быть можно опереться. Если вы не помните, откуда взялась цифра, у вас не знание, а
  слух: в следующий раз вы перепроверите всё заново, и базы как будто не было.

Инструментов для этого много — от Confluence до Obsidian. Этот шаблон тоже про порядок и доверие, но с одной поправкой:
писать в базу будет агент, а проверять — вы. Поэтому здесь оба свойства не «принято соблюдать», а встроены в правила:
обязательные разделы, обязательная цитата и проверялка, которая падает без неё. Подробнее — в разделе
«Чем это не Notion и не Confluence».

## Что это

Это не приложение и не сервис: **запускать нечего, кнопки нет**. Это папка с правилами и пустой вики, которую вы
наполняете вдвоём с агентом — в чате, в редакторе, где вам удобно. Всё содержимое — обычные markdown-файлы и папка
`raw/` с исходниками.

Идея простая. Агент умеет прочитать что угодно и не помнит ничего. Эта папка — место, где он записывает найденное так,
чтобы вы могли проверить: **источники здесь — доказательства и никогда не меняются**, страницы собраны из них, а каждое
конкретное утверждение несёт цитату, которая открывается в исходнике на указанной строке.

Профит не в том, что агент знает больше. Профит в том, что вы видите разницу между тем, что он **нашёл**, и тем, что он
**придумал** — сегодня и через год. И если в базе ответа нет, агент обязан сказать «в базе этого нет», а не сочинить
правдоподобное.

## Для каких задач подходит

- **Конспекты книг и лекций** — когда перечитывать источник не хочется, а «где это было сказано» нужно.
- **Заметки по проекту**, где важно, откуда взялась цифра: «кто это решил, когда и на основании чего».
- **Разбор интервью и созвонов**: кто что сказал — с цитатой, а не с пересказом по памяти.
- **Семейное и бытовое знание**: рецепты, «как мы это делаем у нас дома», аптечка, сад, ремонт.
- **Исследование по теме**, собранное из статей и ссылок: что утверждают источники и где они противоречат друг другу.
- **Спойлерная база** по книге, сериалу или игре: факты отдельно от ваших впечатлений.

**Когда не подходит.** Для быстрых заметок на салфетку — оверхед. Для планов и задач в работе — для этого есть `scratch/`,
и это не знание. И если вы не готовы, что материал лежит на диске в открытом виде, — это не про секреты.

## Как это выглядит

Было — заметка, с которой всё началось (`raw/notes/pomodoro.md`):

```
12  Помодоро: 25 минут работы, 5 минут отдыха. Придумал Франческо Чирилло в конце 1980-х.
13  Название — от кухонного таймера в виде помидора.
```

Стало — страница (`wiki/pages/pomodoro.md`):

```markdown
## Facts

1. Техника «помодоро» — 25 минут работы и 5 минут отдыха — `raw/notes/pomodoro.md:12`
2. Название техники происходит от кухонного таймера в виде помидора — `raw/notes/pomodoro.md:13`

## Notes

- Подходит только для задач, которые режутся на куски по 25 минут, — мои не режутся.
```

Каждая строка в `Facts` открывается в исходном файле — можно убедиться самому. Свои выводы и предпочтения живут в
`Notes` и никогда не выдаются за факт. Это и есть весь трюк: **факт и мнение не лежат в одном разделе**, поэтому цитата
чего-то стоит.

## Чем это не Notion и не Confluence

Короткий ответ: **не замена, а другой жанр.** Notion, Confluence и Obsidian — места, где пишет человек и где
доказательство необязательно: ссылку можно вставить, а можно не вставлять, и никто не заметит разницы. Здесь пишет агент,
а цитата — часть записи: её отсутствие или кривой формат — ошибка, которую ловит линт.

| | Notion / Confluence / Obsidian | здесь |
|---|---|---|
| кто пишет | человек | агент пишет, человек проверяет |
| единица знания | документ | атомарный факт с цитатой и страница-ответ |
| доказательство | ссылка по желанию | цитата обязательна, формат проверяется |
| что будет через год | непонятно, чему верить | видно, что найдено, а что придумано |
| совместная работа | комментарии, права, живое редактирование | нет и не планируется |

И где проигрывает — честно, без звёздочек: **пятеро редакторов одновременно, комментарии, права доступа, мобильный
клиент, полнотекстовый поиск из коробки.** Если нужно именно это — берите Confluence, он для этого и сделан.

Выигрывает там, где вопрос звучит «откуда мы это знаем», а не «где лежит документ». Рабочий компромисс обычно такой:
официальный документ живёт в Confluence, а эта папка — слой «что мы на самом деле знаем и на чём это стоит».

## Живые примеры

Два демо одного и того же ядра, в разных доменах. Ради этого всё и сделано: **ядро одно, а под домен меняется один файл —
`wiki/PROFILE.md`.**

- [`example/books`](https://github.com/Raud/llm-wiki-template/tree/example/books) — конспект книги: 2 источника, 4 страницы,
  22 факта, `external_subject: ask` (книжные спойлеры), схемы `file` + `url`.
- [`example/it-infra`](https://github.com/Raud/llm-wiki-template/tree/example/it-infra) — инфраструктура компании:
  4 источника, 5 страниц, 34 факта, **помеченный конфликт** двух редакций рунбука, `external_subject: forbidden`, схемы
  `file` + `note`.

`main` при этом остаётся чистым: примеры живут в ветках, шаблон можно скачать и не глядя на них — удалять ничего не нужно.

## Как начать

1. **Скачайте папку** — `Code → Download ZIP` на GitHub или `git clone`.
2. **Откройте её агентом, который видит файлы.** Подойдёт Claude Projects (файлы загружаются в проект), Cursor, Claude
   Code, ChatGPT с файлами. Важно: в обычном веб-чате папку агент не увидит — туда файлы надо приложить руками.
3. **Скажите одну фразу:** «Прочитай `BOOTSTRAP.md` и инициализируй эту вики под мою задачу». Дальше он задаст
   несколько вопросов о домене, источниках и языке — и создаст профиль и скелет.
4. **Дайте первый реальный материал** — текст, файл, ссылку. Вики не должна остаться пустой: инициализация заканчивается
   тем, что в неё загружен один настоящий источник. С этого момента можно работать.

Дальше обычный цикл: положить источник в `raw/` → «загрузи это» → спросить что-нибудь → устойчивые ответы становятся
страницами.

## Что где лежит

```
raw/                     неизменяемые исходники — доказательства
scratch/                 временные рабочие документы — никогда не цитируются и не считаются знанием
wiki/PROFILE.md          профиль домена — единственный доменно-специфичный файл
wiki/pages/              страницы (плоским списком)
wiki/templates/          шаблоны страниц (concept, howto, reference, open-questions, glossary)
wiki/index/              реестры: факты, источники, решения по чистке (по записи в строке)
wiki/tools/              запуск и инструменты: lint (проверка) и norm (формат)
AGENTS.md                рабочий контракт (доменно-нейтральный, не правится под домен)
BOOTSTRAP.md             промпт инициализации
```

## Проверки (необязательно)

Всё работает и без них: вики — это markdown. Инструменты нужны, чтобы ловить расхождения вроде битой цитаты или
страницы, которой нет в оглавлении. Python 3.9+, без зависимостей.

```powershell
.\wiki\tools\wiki.cmd lint
.\wiki\tools\wiki.cmd norm -w wiki\index
```

```sh
./wiki/tools/wiki.sh lint
./wiki/tools/wiki.sh norm --check wiki/index
```

`norm` принимает файлы или папки, поэтому команда одинакова в любой оболочке: PowerShell не раскрывает `*.jsonl` для
внешних программ.

## Решения, которые стоит знать

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

## Abstract (EN)

A domain-agnostic kernel for a **persistent knowledge wiki maintained by an LLM agent together with a human**. Raw
sources are evidence and never change; pages are the product and are synthesized from them; every concrete claim on a
page carries a citation you can open for yourself. So an agent's answer can be audited, and when the wiki is silent it
says so instead of filling the gap from model memory — you can tell what it *found* from what it *invented*.

## License

[MIT-0](LICENSE) — no attribution required. A template must not put a legal to-do in front of every copy of itself, and
nothing here distinguishes "code" from "content": the tools, the contract, the templates and the skeleton are all under
the same terms. Pages you write into your own copy are yours, under whatever terms you choose.
