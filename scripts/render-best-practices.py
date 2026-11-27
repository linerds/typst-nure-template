#!/usr/bin/env python3
"""Render visual examples for docs/best-practices.md into assets/best-practices/."""

import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "assets" / "best-practices"

ARCH_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 540 120" width="540" height="120">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#111"/>
    </marker>
  </defs>
  <rect width="540" height="120" fill="#ffffff"/>
  <g fill="#ffffff" stroke="#111111" stroke-width="1.5">
    <rect x="16" y="34" width="110" height="52" rx="4"/>
    <rect x="168" y="34" width="116" height="52" rx="4"/>
    <rect x="326" y="34" width="100" height="52" rx="4"/>
    <ellipse cx="496" cy="44" rx="28" ry="9"/>
    <path d="M 468 44 L 468 78 A 28 9 0 0 0 524 78 L 524 44"/>
  </g>
  <g stroke="#111111" stroke-width="1.5" fill="none">
    <line x1="126" y1="60" x2="165" y2="60" marker-end="url(#arrow)"/>
    <line x1="284" y1="60" x2="323" y2="60" marker-end="url(#arrow)"/>
    <line x1="426" y1="60" x2="465" y2="60" marker-end="url(#arrow)"/>
  </g>
  <g font-family="Liberation Sans, Arial, sans-serif" font-size="14" fill="#111111" text-anchor="middle">
    <text x="71" y="65">Клієнт</text>
    <text x="226" y="65">API-шлюз</text>
    <text x="376" y="65">Сервіс</text>
    <text x="496" y="72">БД</text>
  </g>
  <g font-family="Liberation Sans, Arial, sans-serif" font-size="11" fill="#444444" text-anchor="middle">
    <text x="147" y="51">HTTPS</text>
    <text x="305" y="51">gRPC</text>
    <text x="447" y="51">SQL</text>
  </g>
</svg>
"""

SCREEN_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 120" width="420" height="120">
  <rect x="1" y="1" width="418" height="118" rx="4" fill="#ffffff" stroke="#111111" stroke-width="1.5"/>
  <rect x="1" y="1" width="418" height="24" rx="4" fill="#f0f0f0" stroke="#111111" stroke-width="1.5"/>
  <circle cx="16" cy="13" r="4" fill="#888"/>
  <circle cx="30" cy="13" r="4" fill="#aaa"/>
  <circle cx="44" cy="13" r="4" fill="#ccc"/>
  <text x="210" y="17" font-family="Liberation Sans, sans-serif" font-size="11" fill="#222" text-anchor="middle">Моніторинг вузлів — localhost:8080</text>
  <g font-family="Liberation Mono, monospace" font-size="11" fill="#111">
    <text x="18" y="48" font-weight="bold">STATUS</text>
    <text x="86" y="48" font-weight="bold">NODE</text>
    <text x="210" y="48" font-weight="bold">LATENCY</text>
    <text x="315" y="48" font-weight="bold">UPTIME</text>
    <line x1="18" y1="54" x2="402" y2="54" stroke="#cccccc" stroke-width="1"/>
    <text x="18" y="72">[OK]</text>
    <text x="86" y="72">api-01</text>
    <text x="210" y="72">12 ms</text>
    <text x="315" y="72">99.98%</text>
    <text x="18" y="90">[OK]</text>
    <text x="86" y="90">worker-02</text>
    <text x="210" y="90">18 ms</text>
    <text x="315" y="90">99.95%</text>
    <text x="18" y="108">[OK]</text>
    <text x="86" y="108">db-primary</text>
    <text x="210" y="108">4 ms</text>
    <text x="315" y="108">99.99%</text>
  </g>
</svg>
"""

SAMPLE_BIB = """\
go:
  type: Web
  title: The Go Programming Language Documentation
  author: The Go Authors
  url:
    value: https://go.dev/doc/
    date: 2026-03-10

postgres:
  type: Book
  title: PostgreSQL 16 Internals
  author: Rogov E.
  publisher: Postgres Professional
  date: 2024
  page-total: 520
"""

FRAME_PREAMBLE = """\
#import "@vendor/nure:{ver}": *
#import style: spacing

#show: style.dstu
#set page(
  width: 165mm,
  height: auto,
  margin: (x: 9mm, y: 7mm),
  fill: white,
  numbering: none,
  foreground: place(top + left, rect(width: 100%, height: 100%, stroke: 0.75pt + luma(205))),
)
"""

COMPOSER_HEADER = """\
#set page(width: {width}, height: auto, margin: 4mm, fill: luma(246))
#set text(font: ("Liberation Sans", "DejaVu Sans"), size: 9.5pt, fill: luma(50))

#let card(img, label: none, accent: luma(195), badge-bg: luma(236), badge-fg: luma(45)) = {{
  stack(
    spacing: 2.5mm,
    ..if label != none {{
      (align(center, box(
        fill: badge-bg,
        stroke: 0.5pt + accent,
        inset: (x: 7pt, y: 3pt),
        radius: 3pt,
        text(weight: "semibold", fill: badge-fg, label),
      )),)
    }} else {{ () }},
    block(
      stroke: 0.75pt + accent,
      fill: white,
      image(img, width: 100%),
    ),
  )
}}
"""


def find_typst() -> list[str]:
    if shutil.which("typst"):
        return ["typst"]
    mise_bin = Path.home() / ".local/share/mise/installs/typst"
    if mise_bin.exists():
        candidates = sorted(mise_bin.glob("0.15.*/**/typst"), reverse=True)
        if candidates:
            return [str(candidates[0])]
    if shutil.which("mise"):
        return ["mise", "x", "typst", "--", "typst"]
    sys.exit("error: typst 0.15+ not found")


def compile_typ(typst: list[str], env: dict[str, str], src: Path, out: Path, ppi: int = 160) -> None:
    cmd = [*typst, "compile", "--ppi", str(ppi), str(src), str(out)]
    res = subprocess.run(cmd, env=env, text=True, capture_output=True)
    if res.returncode != 0:
        sys.stderr.write(f"Failed compiling {src}:\n{res.stderr}\n")
        sys.exit(res.returncode)


def main() -> None:
    ver = tomllib.loads((ROOT / "typst.toml").read_text(encoding="utf-8"))["package"]["version"]
    typst = find_typst()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="nure-bp-") as tmp_str:
        tmp = Path(tmp_str)
        pkg_dir = tmp / "packages" / "vendor" / "nure"
        pkg_dir.mkdir(parents=True)
        (pkg_dir / ver).symlink_to(ROOT)

        env = {**os.environ, "TYPST_PACKAGE_PATH": str(tmp / "packages")}

        figures_dir = tmp / "figures"
        figures_dir.mkdir()
        (figures_dir / "arch.svg").write_text(ARCH_SVG, encoding="utf-8")
        (figures_dir / "screen.svg").write_text(SCREEN_SVG, encoding="utf-8")
        (tmp / "bibl.yml").write_text(SAMPLE_BIB, encoding="utf-8")

        def write_src(name: str, body: str) -> Path:
            p = tmp / f"{name}.typ"
            p.write_text(body, encoding="utf-8")
            return p

        # 1. Three report title page layouts side by side
        title_src = write_src(
            "title-layouts-pages",
            f"""\
#import "@vendor/nure:{ver}": *
#show: style.dstu.with(skip: 3)

#let base = (
  university: "ХНУРЕ",
  subject: "СМП",
  type: "ЛБ",
  number: 2,
  title: "Потік керування та алгоритмічні структури Bash",
  authors: ((name: "Косач Л. П.", edu-program: "КУІБ", group: "24-1", gender: "f", variant: 8, course: 2),),
  mentors: ((name: "Шевченко Т. Г.", degree: "Доцент кафедри ПІ", gender: "m"),),
  year: 2026,
)
#let w = work(..base)

#report.title-page(w)
#report.title-page(w, layout: "complex")
#report.title-page(w, layout: "nure-iki")
""",
        )
        compile_typ(typst, env, title_src, tmp / "title-p{0p}.png", ppi=105)
        title_comp = write_src(
            "title-layouts-comp",
            COMPOSER_HEADER.format(width="225mm")
            + """\
#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 4mm,
  card("title-p1.png", label: [`layout: "default"`]),
  card("title-p2.png", label: [`layout: "complex"`]),
  card("title-p3.png", label: [`layout: "nure-iki"`]),
)
""",
        )
        compile_typ(typst, env, title_comp, OUT_DIR / "title-layouts.png", ppi=150)

        # 2. Adjacent headings spacing: without vs with #v(-spacing)
        h_bad = write_src(
            "headings-bad",
            f"""\
#import "@vendor/nure:{ver}": *
#import style: spacing
#show: style.dstu
#set page(width: 112mm, height: auto, margin: (x: 7mm, y: 6mm), fill: white, numbering: none)
#counter(heading).update(1)

== Хід роботи
=== Підготовка середовища
Встановлено необхідні пакунки та перевірено версію компілятора.
""",
        )
        h_good = write_src(
            "headings-good",
            f"""\
#import "@vendor/nure:{ver}": *
#import style: spacing
#show: style.dstu
#set page(width: 112mm, height: auto, margin: (x: 7mm, y: 6mm), fill: white, numbering: none)
#counter(heading).update(1)

== Хід роботи
#v(-spacing)
=== Підготовка середовища
Встановлено необхідні пакунки та перевірено версію компілятора.
""",
        )
        compile_typ(typst, env, h_bad, tmp / "headings-bad.png", ppi=165)
        compile_typ(typst, env, h_good, tmp / "headings-good.png", ppi=165)
        h_comp = write_src(
            "headings-comp",
            COMPOSER_HEADER.format(width="205mm")
            + """\
#grid(
  columns: (1fr, 1fr),
  gutter: 4mm,
  card(
    "headings-bad.png",
    label: [Без `#v(-spacing)` — подвійний проміжок],
    accent: rgb("#d97777"),
    badge-bg: rgb("#fdecec"),
    badge-fg: rgb("#991b1b"),
  ),
  card(
    "headings-good.png",
    label: [Із `#v(-spacing)` — правильно за ДСТУ 7.1.24],
    accent: rgb("#4ca172"),
    badge-bg: rgb("#eaf7ef"),
    badge-fg: rgb("#166534"),
  ),
)
""",
        )
        compile_typ(typst, env, h_comp, OUT_DIR / "headings-spacing.png", ppi=155)

        # 3. plain-heading + section-numbering: false
        plain_src = write_src(
            "headings-plain",
            f"""\
#import "@vendor/nure:{ver}": *
#import style: spacing

#show: style.dstu.with(section-numbering: false)
#show: style.overrides.plain-heading
#set page(
  width: 155mm,
  height: auto,
  margin: (x: 9mm, y: 7mm),
  fill: white,
  numbering: none,
  foreground: place(top + left, rect(width: 100%, height: 100%, stroke: 0.75pt + luma(205))),
)

= Звіт з практичної роботи
#v(-spacing)
== Постановка задачі
У першому пункті розглянуто базові вимоги. Обчислення виконуються за @eq:sum[формулою]:
$ S = sum_(i=1)^n x_i $ <eq:sum>

=== Вхідні параметри
Підрозділи нумеруються без початкового «0.» (`1`, `1.1`).
""",
        )
        compile_typ(typst, env, plain_src, OUT_DIR / "headings-plain.png", ppi=160)

        # 4. Prefixed labels & inflected cross-references
        refs_src = write_src(
            "refs-and-labels",
            FRAME_PREAMBLE.format(ver=ver)
            + """\
#counter(heading).update(1)
#place(hide[
  == Огляд архітектури <sub:arch>
  #fig(path("figures/arch.svg"), [Архітектура сервісу], label: <fig:arch>)
  #tab(caption: [Результати], columns: 2, header: ([А], [Б]), label: <tab:results>, [1], [2])
  $ E = m c^2 $ <eq:energy>
  #figure(```c\nint main(void) { return 0; }\n```, caption: [Приклад]) <lst:main>
])
У @sub:arch[підрозділі] розглянуто структуру сервісу (див. @fig:arch[рисунок]). Заміри продуктивності зведено у @tab:results[таблиці], а розрахунок виконано за @eq:energy[формулою]. Повну реалізацію наведено у @lst:main[лістингу].
""",
        )
        compile_typ(typst, env, refs_src, OUT_DIR / "refs-and-labels.png", ppi=165)

        # 5. Figure with fig(), path(), note:, source: none
        fig_src = write_src(
            "figure-dstu",
            FRAME_PREAMBLE.format(ver=ver)
            + """\
#counter(heading).update(1)
Взаємодію компонентів зображено на @fig:arch[рисунку].

#fig(
  path("figures/arch.svg"),
  [Архітектура мікросервісу],
  none,
  note: [Обмін між шлюзом і сервісом відбувається за протоколом gRPC.],
  label: <fig:arch>,
  width: 92%,
)
""",
        )
        compile_typ(typst, env, fig_src, OUT_DIR / "figure-dstu.png", ppi=160)

        # 6. Table with tab() and note:
        tab_src = write_src(
            "table-dstu",
            FRAME_PREAMBLE.format(ver=ver)
            + """\
#counter(heading).update(1)
Результати вимірювань наведено в @tab:perf[таблиці].

#tab(
  caption: [Порівняння режимів кешування],
  columns: (2.2fr, 1.5fr, 1.5fr),
  align: (left, center, center),
  header: ([Режим], [Затримка, мс], [RPS]),
  note: [Середнє значення за 10 000 запитів при 64 потоках.],
  label: <tab:perf>,
  [Без кешу], [42,5], [1 480],
  [In-memory], [4,1], [15 200],
  [Redis], [7,8], [8 150],
)
""",
        )
        compile_typ(typst, env, tab_src, OUT_DIR / "table-dstu.png", ppi=160)

        # 7. Multi-page table continuation (2 compact pages side by side)
        tbreak_src = write_src(
            "table-break-pages",
            f"""\
#import "@vendor/nure:{ver}": *
#show: style.dstu
#set page(
  width: 145mm,
  height: 68mm,
  margin: (top: 8mm, right: 8mm, bottom: 8mm, left: 10mm),
  fill: white,
  numbering: none,
)
#counter(heading).update(1)

#tab(
  caption: [Результати тестування вузлів],
  columns: (0.7fr, 2.5fr, 1.5fr, 1.5fr),
  align: (center, left, center, center),
  header: ([№], [Вузол], [Затримка, мс], [Статус]),
  label: <tab:nodes>,
  [1], [api-gateway-01], [8,2], [ОК],
  [2], [auth-service-01], [11,4], [ОК],
  [3], [billing-core-01], [15,9], [ОК],
  [4], [notify-worker-01], [9,7], [ОК],
  [5], [search-index-01], [21,3], [ОК],
  [6], [storage-node-01], [6,5], [ОК],
  [7], [metrics-agg-01], [12,1], [ОК],
)
""",
        )
        compile_typ(typst, env, tbreak_src, tmp / "tbreak-p{0p}.png", ppi=155)
        tbreak_comp = write_src(
            "table-break-comp",
            COMPOSER_HEADER.format(width="215mm")
            + """\
#grid(
  columns: (1fr, 1fr),
  gutter: 4mm,
  card("tbreak-p1.png", label: [Сторінка 1 — початок таблиці]),
  card("tbreak-p2.png", label: [Сторінка 2 — автоматичний перенос і повтор шапки]),
)
""",
        )
        compile_typ(typst, env, tbreak_comp, OUT_DIR / "table-break.png", ppi=150)

        # 8. Equations: referenced vs unreferenced, decimal comma, noindent
        eq_src = write_src(
            "equations-dstu",
            FRAME_PREAMBLE.format(ver=ver)
            + """\
#counter(heading).update(1)
Частотну ефективність обчислюємо за @eq:eff[формулою]:
$ beta = gamma / (2^gamma - 1) $ <eq:eff>
#utils.noindent де $gamma = 1.5$ -- частотна ефективність, біт/(с·Гц); $beta$ -- енергетична ефективність.

Проміжна оцінка без посилання номера не отримує:
$ f(1.5; 2.5) = 0.85 dot beta $
""",
        )
        compile_typ(typst, env, eq_src, OUT_DIR / "equations-dstu.png", ppi=165)

        # 9. Listing + inline code comparison (DSTU vs style.overrides.inline-code)
        lst_src = write_src(
            "listing-card",
            f"""\
#import "@vendor/nure:{ver}": *
#show: style.dstu
#set page(width: 155mm, height: auto, margin: (x: 8mm, y: 6mm), fill: white, numbering: none)
#counter(heading).update(1)

#figure(
  ```bash
  for f in src/*.typ; do
    typst compile "$f"
  done
  ```,
  caption: [Пакетна компіляція файлів],
) <lst:build>
""",
        )
        inl_dstu = write_src(
            "inline-dstu",
            f"""\
#import "@vendor/nure:{ver}": *
#show: style.dstu
#set page(width: 155mm, height: auto, margin: (x: 8mm, y: 6mm), fill: white, numbering: none)

Збірка запускається командою `mise run watch`, а дані роботи беруться з `src/doc.toml`.
""",
        )
        inl_override = write_src(
            "inline-override",
            f"""\
#import "@vendor/nure:{ver}": *
#show: style.dstu
#show: style.overrides.inline-code.with(fill: luma(240))
#set page(width: 155mm, height: auto, margin: (x: 8mm, y: 6mm), fill: white, numbering: none)

Збірка запускається командою `mise run watch`, а дані роботи беруться з `src/doc.toml`.
""",
        )
        compile_typ(typst, env, lst_src, tmp / "listing-card.png", ppi=160)
        compile_typ(typst, env, inl_dstu, tmp / "inline-dstu.png", ppi=160)
        compile_typ(typst, env, inl_override, tmp / "inline-override.png", ppi=160)
        code_comp = write_src(
            "code-comp",
            COMPOSER_HEADER.format(width="165mm")
            + """\
#stack(
  spacing: 3.5mm,
  card("listing-card.png", label: [Лістинг із підписом (`figure`)]),
  card("inline-dstu.png", label: [Рядковий код за ДСТУ (типово)]),
  card("inline-override.png", label: [Рядковий код із `style.overrides.inline-code`]),
)
""",
        )
        compile_typ(typst, env, code_comp, OUT_DIR / "listing-and-inline-code.png", ppi=155)

        # 10. Lists, notes, and footnotes (compact page so footnote sits cleanly at bottom)
        lnf_src = write_src(
            "lists-notes-footnotes",
            f"""\
#import "@vendor/nure:{ver}": *
#show: style.dstu
#set page(
  width: 165mm,
  height: 124mm,
  margin: (top: 8mm, right: 9mm, bottom: 8mm, left: 9mm),
  fill: white,
  numbering: none,
  foreground: place(top + left, rect(width: 100%, height: 100%, stroke: 0.75pt + luma(205))),
)

Основні етапи налаштування середовища#footnote[Перевірено на Typst 0.15.1 у Linux і Windows.]:
+ підготовка даних роботи у `doc.toml`:
  + заповнення реквізитів автора та викладача;
  + вибір скорочення дисципліни:
    - вбудована назва або власний `data.yaml`;
+ компіляція документа й перевірка полів, інтервалів і перенесення довгих рядків переліку від лівого берега.

#note[Один аргумент формує ненумеровану примітку.]
#note[Перша з кількох приміток.][Друга примітка нумерується автоматично.]
""",
        )
        compile_typ(typst, env, lnf_src, OUT_DIR / "lists-notes-footnotes.png", ppi=160)

        # 11. Bibliography + Appendix (2 pages side by side)
        bib_app_src = write_src(
            "bib-app-pages",
            f"""\
#import "@vendor/nure:{ver}": *
#show: style.dstu
#set page(
  width: 150mm,
  height: 108mm,
  margin: (top: 10mm, right: 8mm, bottom: 9mm, left: 10mm),
  fill: white,
  numbering: none,
)

#bib(path("bibl.yml"), style: "3008", full: true)

#show: style.appendices
= Знімки екрана
#fig(path("figures/screen.svg"), [Панель моніторингу вузлів], width: 88%, label: <fig:monitor>)
""",
        )
        compile_typ(typst, env, bib_app_src, tmp / "bibapp-p{0p}.png", ppi=155)
        bib_app_comp = write_src(
            "bib-app-comp",
            COMPOSER_HEADER.format(width="215mm")
            + """\
#grid(
  columns: (1fr, 1fr),
  gutter: 4mm,
  card("bibapp-p1.png", label: [`#bib(path("bibl.yml"))` — перед додатками]),
  card("bibapp-p2.png", label: [`#show: style.appendices` — літерна нумерація]),
)
""",
        )
        compile_typ(typst, env, bib_app_comp, OUT_DIR / "bib-and-appendices.png", ppi=150)

    imgs = sorted(OUT_DIR.glob("*.png"))
    print(f"Rendered {len(imgs)} images into {OUT_DIR}:")
    for img in imgs:
        print(f"  {img.name} ({img.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
