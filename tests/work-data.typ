// Own universities, edu-programs and subjects merged over the built-in data.
#import "../src/lib.typ": *

#let extra = yaml("fixtures/extra-data.yaml")
#let author = (name: "Косач Л. П.", edu-program: "ПЗПІ", group: "23-2", gender: "f")
#let mentor = (name: "Франко І. Я.", degree: "Доцент", gender: "m")

#assert.eq(deep-merge((a: 1, b: (c: 2, d: 3)), (b: (d: 4, e: 5), f: 6)), (a: 1, b: (c: 2, d: 4, e: 5), f: 6))
#assert.eq(deep-merge((a: 1, b: (c: 2)), (a: none, b: (c: none), x: none)), (b: (:)))

// is-empty & gender-get edge cases
#assert.eq(is-empty(none), true)
#assert.eq(is-empty(""), true)
#assert.eq(is-empty(()), true)
#assert.eq(is-empty("a"), false)
#assert.eq(is-empty((1,)), false)
#assert.eq(is-empty(0), false)
#assert.eq(gender-get(((name: "Франко І. Я."),)), none)
#assert.eq(group-form((group: "24-1", edu-program: "КУІБ")), "КУІБ-24-1")
#assert.eq(group-form((group: "КУІБ-24-1", edu-program: "КУІБ")), "КУІБ-24-1")

// title normalization: list titles join with a space once in work()
#let list-title-work = work(type: "ЛБ", number: 1, title: ("A", "B"), authors: (author,), mentors: (mentor,))
#assert.eq(list-title-work.title, "A B")
#assert.eq(list-title-work.document.title, "A B")
#let special-title-work = work(
  type: "ЛБ",
  number: 2,
  title: "C# <x> і *вказівники*",
  authors: (author,),
  mentors: (mentor,),
)
#assert.eq(special-title-work.title, "C# <x> і *вказівники*")
#assert.eq(special-title-work.subject-name, none)

// built-in university: one field overridden, new program and subject added
#let w = work(subject: "НовДис", authors: (author,), data: extra)
#assert.eq(w.edu.code, "F2")
#assert.eq(w.edu.name-long, "Інженерія програмного забезпечення")
#assert.eq(w.subject-name, "Нова дисципліна")
#assert.eq(w.city, "Харків")
#assert.eq(work(subject: "БД", authors: (author,), data: extra).subject-name, "Бази даних")
#assert.eq(work(edu-program: "ШІ", authors: (author,), data: extra).edu.department-gen, "Штучного інтелекту")
// author inherits work-level edu-program when omitted on the author dict
#assert.eq(
  work(edu-program: "ПЗПІ", authors: ((name: "Косач Л. П.", group: "23-2"),)).authors.first().edu-program,
  "ПЗПІ",
)
// city overrides and universities without city
#assert.eq(work(authors: (author,), city: "Львів").city, "Львів")
#assert.eq(work(authors: (author,), city: none).city, none)
#assert.eq(work(authors: (author,), data: ("ХНУРЕ": (city: none))).city, none)
// built-in data untouched
#assert.eq(work(authors: (author,)).edu.code, 121)
#assert.eq(universities.at("ХНУРЕ").edu-programs.ПЗПІ.code, 121)

// a university of your own (with `city` from data.yaml)
#let kpi = work(
  university: "КПІ",
  subject: "ОП",
  type: "ЛБ",
  number: 1,
  title: "Перша лабораторна",
  authors: ((..author, edu-program: "ІПЗ"),),
  mentors: (mentor,),
  data: extra,
)
#assert.eq(kpi.uni.name.starts-with("Національний"), true)
#assert.eq(kpi.city, "Київ")

// recipes forward data, edu-program, year, city and handle optional author/mentor fields
#let minimal-author = (name: "Косач Л. П.", group: "23-2", course: 2, semester: 4, full-name-gen: "Косач Л. П.")
#let minimal-mentor = (name: "Франко І. Я.")
#let sample-date = datetime(year: 2026, month: 5, day: 10)
#let _ = pz-lb(
  [],
  university: "КПІ",
  edu-program: "ІПЗ",
  subject: "ОП",
  type: "ЛБ",
  authors: (minimal-author,),
  mentors: (minimal-mentor,),
  year: 2026,
  city: "Київ",
  data: extra,
)
#let _ = coursework(
  [],
  university: "КПІ",
  edu-program: "ІПЗ",
  subject: "ОП",
  title: "Курсова",
  authors: (minimal-author,),
  mentors: (minimal-mentor,),
  task-list: (initial-date: sample-date, done-date: sample-date),
  calendar-plan: (plan-table: []),
  abstract: (keywords: ("тест",), text: []),
  bib-path: bytes(read("fixtures/bibl.yml")),
  year: 2026,
  city: "Київ",
  data: extra,
)
#let _ = coursework-v2(
  [],
  university: "КПІ",
  edu-program: "ІПЗ",
  title: "Проєкт",
  authors: (minimal-author,),
  mentors: (minimal-mentor,),
  task-list: (initial-date: sample-date, done-date: sample-date),
  calendar-plan: (plan-table: []),
  abstract: (keywords: ("тест",), text: []),
  bib-path: bytes(read("fixtures/bibl.yml")),
  year: 2026,
  city: "Київ",
  data: extra,
)

#set document(..kpi.document)
#show: style.dstu.with(skip: 1)

// city comes from extra-data.yaml (`Київ -- <year>`)
#report.title-page(kpi)
#title-heading(kpi)

== Content
#lorem(20)

// list title, special characters in title, and omitted subject across layouts
#report.title-page(list-title-work)
#report.title-page(list-title-work, layout: "complex")
#report.title-page(list-title-work, layout: "nure-iki")
#title-heading(list-title-work)

#report.title-page(special-title-work)
#report.title-page(special-title-work, layout: "complex")
#title-heading(special-title-work)

#context {
  let bodies = query(heading.where(level: 1)).map(h => h.body)
  assert.eq(bodies.at(1).text, "A B")
  assert.eq(bodies.at(2).text, "C# <x> і *вказівники*")
}
