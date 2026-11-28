# Довідник API

Усе, що експортує `#import "@vendor/nure:0.3.0": *` (або `@local/...`).

## Дані

- `work(...) -> dictionary` -- дані роботи, поля в [data.md](data.md).
- `universities` -- вбудовані дані.

## Стилі

### `style.dstu(skip: 0, offset: 0, section-numbering: true)`

`#show: style.dstu.with(skip: 1)`. `skip` -- скільки перших сторінок без номера (рахуються); `offset` -- зсув номерів; `section-numbering: false` -- наскрізна нумерація рисунків, таблиць, лістингів і формул (`1`, `(1)`).

### `style.appendices`

`#show: style.appendices` або `#style.appendices(include "chapters/appendices.typ")`.

### `style.overrides` -- відхилення від ДСТУ за вимогою кафедри

Ставляться після `#show: style.dstu`:

```typst
#show: style.dstu.with(skip: 1, section-numbering: false)
#show: style.overrides.plain-heading
#show: style.overrides.inline-code
```

| Функція | Опис |
| --- | --- |
| `style.overrides.plain-heading(numbering: none, alignment: center, weight: "regular", size: 14pt, uppercase: true, pagebreak: false, above: double-spacing, below: double-spacing)` | Перший рівень без номера, по центру, звичайним накресленням, без розриву сторінки; `numbering: auto` лишає нумерацію |
| `style.overrides.inline-code(font: code-font, size: auto, weight: "regular", fill: none, stroke: none, inset: (x: 0.25em), outset: (y: 0.2em), radius: 2pt)` | Моноширинний рядковий код замість лапок |

Інші правки -- звичайні `set`/`show` після `style.dstu` (напр. `#set par(leading: 1.2em)`); вони діють поверх оформлення пакунка.

### Константи

`style.spacing` (для `#v(-spacing)`), `style.indent-size` (1,25 см), `style.double-spacing`, `style.code-font`, `style.ukr-enum`.

## Титулки звітів: `report`

### `report.title-page(w, layout: "default", header: auto, info: auto, credentials: auto, footer: auto)`

| `layout` | Вигляд |
| --- | --- |
| `"default"` (= `"nure"`) | Міністерство, університет, кафедра; «Звіт з лабораторної роботи №N з дисципліни … з теми …»; ліворуч «Виконала: ст. гр. …, ПІБ, Варіант», праворуч «Перевірив: посада, ПІБ»; унизу «Харків – рік» |
| `"complex"` | Плюс спеціальність і освітня програма в шапці; варіант під темою; виконавці й перевіряючі праворуч з підписами «(прізвище та ініціали)»; зручно для кількох авторів |
| `"nure-iki"` | За методичними рекомендаціями кафедри ІКІ (2024): факультет і кафедра з підкресленими полями, «ЗВІТ», дисципліна й тема заняття, виконавець із курсом і групою, унизу «рік р.» |

Частини: `header` (міністерство, університет, кафедра), `info` (тип, номер, дисципліна, тема), `credentials` (хто виконав і перевірив), `footer` (місто й рік). Значення: `auto` -- вміст макета, свій вміст -- заміна, `none` -- порожньо. Типовий вміст: `report.nure.*`, `report.complex.*`, `report.nure-iki.*` -- `default-header(w)`, `default-info(w)`, `default-credentials(w)`, `default-footer(w)`.

```typst
#report.title-page(w, info: [#report.nure.default-info(w) \ Підгрупа 2], footer: [Київ -- 2026])
```

### `title-heading(w)`

Заголовок першого рівня з темою, пронумерований номером роботи. Без теми не вставляється, але підрозділи однаково нумеруються від номера роботи. Не потрібен -- не викликай і починай з власного `= …`.

## Курсові: `cw`, `cw-v2`

Див. [coursework.md](coursework.md).

## Спільні блоки

| Функція | Опис |
| --- | --- |
| `contents(compact-appendices: false, depth: 3)` | Зміст: «ЗМІСТ», позначка «с.», додатки як «Додаток А Назва»; `compact-appendices: true` ховає підзаголовки додатків |
| `bib(source, style: "3008", title: [Перелік джерел посилання], full: false)` | Перелік джерел; `source` -- `path(...)` або байти |
| `doc-stats()` | «N с., N табл., N рис., N джерел» |
| `sort-keywords(keywords, key: it => it)` | Сортування ключових слів: кирилиця за українською абеткою, далі латиниця |

## Рисунки, таблиці, примітки

- `fig(file, caption, source, note: none, label: none, ..args)` (= `dstu-figure`, `utils.dstu-figure`)
- `tab(caption:, columns:, header:, note: none, label: none, tag: none, ..args)` (= `dstu-table`)
- `note(..notes)` (= `dstu-note`)

Деталі -- [markup.md](markup.md).

## Утиліти: `utils`

| Функція | Опис |
| --- | --- |
| `utils.nheading(title)` | Ненумерований заголовок першого рівня у змісті |
| `utils.noindent` | Знімає абзацний відступ з рядка: `#utils.noindent де …` |
| `utils.bold(content)` | Напівжирний текст |
| `utils.uline(align: center, ..args, content)` | Підкреслене поле на всю ширину |
| `utils.ruled-field(value, prefix: none, min-lines: 1)` | Поле, де кожен рядок підкреслено при переносі |
| `utils.img-caption(caption, source)` | Підпис з приміткою про джерело |

## Допоміжні функції

| Функція | Опис |
| --- | --- |
| `month-gen(n)` | `month-gen(9)` → «вересня» |
| `gender-form(verb, gender: "p")` | `gender-form("author", gender: "f")` → «Виконала»; `"mentor"` → «Перевірив…» |
| `gender-get(people)` | Рід єдиної людини або `"p"` |
| `group-form(author)` | «КУІБ-24-1» |
| `pz-lb-title(type, number: none)` | «Звіт з лабораторної роботи №2» |
| `key-get(dict, key)` | Значення або `none` |
| `is-empty(value)` | Чи порожнє (`none`, `""`, `()`) |
| `is-cyr(text)` | Чи починається з кирилиці |
| `deep-merge(base, override)` | Рекурсивне злиття; `none` видаляє ключ |

## Рецепти

| Функція | Опис |
| --- | --- |
| `pz-lb` | `#show: pz-lb.with(..toml("doc.toml"), type: "ЛБ", number: 1, title: "...")`; приймає поля роботи (включно з `data`, `year`, `city`, `faculty`), `layout`, частини титулки, `skip-heading: true` |
| `coursework`, `coursework-v2` | Курсові одним викликом, див. [coursework.md](coursework.md#рецепти) |

## Власна сторінка

Блоки -- чисті функції від `w`; рецепти -- їх композиції. Власна сторінка -- функція від `w` у `utils.typ` проєкту (`#import "utils.typ": *`):

```typst
#let approval-sheet(w) = {
  align(center, utils.bold[АРКУШ ПОГОДЖЕННЯ])
  v(1em)
  forms.label-line([Здобувач], w.authors.first().name, caption: [(прізвище та ініціали)], label-width: 90pt)
  v(1em)
  forms.label-line([Керівник], w.mentors.first().name, caption: [(прізвище та ініціали)], label-width: 90pt)
  pagebreak()
}

#cw.title-page(w)
#approval-sheet(w)
```

| `forms.*` | Що це |
| --- | --- |
| `label-line(label, value, caption: none, label-width: auto)` | Назва і підкреслене поле, за потреби з підписом |
| `inline-label-line(label, value)` | Те саме, підкреслено кожен рядок при переносі |
| `note(content)` | Дрібний підпис під полем |
| `form-field(alignment: center, content)` | Однорядкове підкреслене поле |
| `task-head-fields(fields)` | Сітка «назва -- поле» |
| `task-num(n)` | «1.» |
| `title-field(value)` | Поле теми з підписом «(тема)» |
| `commission-lines(members)` | Лінії для підписів комісії |

Повністю своя титулка звіту -- передай усі чотири частини:

```typst
#report.title-page(
  w,
  header: [#upper(w.uni.name) \ Кафедра #w.edu.department-gen],
  info: [Розрахунково-графічна робота \ з дисципліни «#w.subject-name»],
  credentials: report.nure.default-credentials(w),
  footer: [Харків -- #w.year],
)
```

## Перехід з 0.2 на 0.3

- Typst 0.15+; імпорт `@vendor/nure:0.3.0` або `@local/nure:0.3.0`; у mise -- новий `.mise/config.toml` з `template/mise`, тека `vendor/` більше не потрібна.
- `img` → `fig(path("figures/a.png"), [...], label: <fig:a>)`. Мітка з назви файлу більше не утворюється: для старих `@figures_a` додай `label: <figures_a>`.
- `bib-path: bytes(read("bibl.yml"))` → `bib-path: path("bibl.yml")`; `dstu-bibliography` → `bib(path("bibl.yml"), style: "3008")`.
- Посилання на `tab` тепер «Таблиця 1.1»: «у таблиці @tab:x» → `@tab:x[таблиці]`.
- Формули без посилань більше не нумеруються: потрібен номер -- пошлися.
- Прибрано `tp`, `utils.img-label`, `utils.path-str`, локальну `img` у `template/default/utils.typ`.
- Свої дисципліни -- через `data.yaml`, а не правки `universities.yaml`.
- Здані роботи не оновлюй: кожна збирається на своїй версії.
