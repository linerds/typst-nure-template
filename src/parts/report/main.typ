#import "../base.typ": title-page as base-title-page
#import "nure.typ"
#import "complex.typ"
#import "nure-iki.typ"

#let layouts = (
  "default": nure,
  "nure": nure,
  "complex": complex,
  "nure-iki": nure-iki,
)

/// Титулка звіту з практичної/лабораторної (ЛБ, ПЗ, КР, ІДЗ).
///
/// - layout (str): "default" (те саме, що "nure"), "complex" або "nure-iki"
///
/// Сторінка складається з чотирьох частин: header, info, credentials, footer.
/// Кожна за замовчуванням заповнюється вмістом макета; її можна замінити,
/// передавши `header:`, `info:`, `credentials:` чи `footer:` (або `none`,
/// щоб лишити частину порожньою). Вміст макетів доступний як функції,
/// напр. `report.nure.default-footer(w)`.
#let title-page(w, layout: "default", header: auto, info: auto, credentials: auto, footer: auto) = {
  assert(
    layout in layouts,
    message: "report: unknown layout " + repr(layout) + ", expected one of " + repr(layouts.keys()),
  )
  let l = layouts.at(layout)
  base-title-page(
    if header == auto { l.default-header(w) } else { header },
    if info == auto { l.default-info(w) } else { info },
    if credentials == auto { l.default-credentials(w) } else { credentials },
    if footer == auto { l.default-footer(w) } else { footer },
  )
}
