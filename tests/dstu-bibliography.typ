// `dstu-bibliography(full: true)` reports every entry to `doc-stats`, not only the cited ones.
#import "../src/lib.typ": *
#import "../src/parts/common.typ": _entry-count

#let yml = bytes(read("fixtures/bibl.yml"))
#let n = yaml(yml).len()
#let bib = bytes("@string{pub = \"P\"}\n@book{a, title = {A}, note = {x@y{z}}}\n  @Online(b, title = {B})\n")

#assert.eq(_entry-count(yml), n)
#assert.eq(_entry-count(path("fixtures/bibl.yml")), n)
#assert.eq(_entry-count(bib), 2)
#assert.eq(_entry-count((yml, bib)), n + 2)

#show: style.dstu

Text @go.

#dstu-bibliography(path("fixtures/bibl.yml"), full: true)

#context assert.eq(query(<dstu-bib-total>).map(it => it.value), (n,))
