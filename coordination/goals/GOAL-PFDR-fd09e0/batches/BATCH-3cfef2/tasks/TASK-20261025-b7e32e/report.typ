// Complete report rendered from the authoritative adjacent Markdown text.
// This small presentation-only renderer preserves all report prose, equations,
// tables and links, and embeds the editable SVG. It runs no scientific code.
#set document(title: "Weighted joint Semaev applicability and first-test design", author: "Coordinator — TASK-20261025-b7e32e")
#set page(paper: "a4", margin: (x: 15mm, y: 14mm), numbering: "1")
#set text(font: ("Nimbus Roman", "Liberation Serif"), size: 9.4pt)
#set par(justify: false, leading: 0.48em, spacing: 0.62em)
#set heading(numbering: none)
#show heading.where(level: 1): set text(size: 15pt)
#show heading.where(level: 2): set text(size: 11.2pt)
#show raw: set text(font: ("Nimbus Mono PS", "Liberation Mono"), size: 7.5pt)
#show link: set text(fill: rgb("244f72"))

#let inline(s) = {
  let s = s.replace("`", "")
  let chunks = ()
  let cursor = 0
  for m in s.matches(regex("\\[([^\\]]+)\\]\\(([^)]+)\\)")) {
    chunks.push(text(s.slice(cursor, m.start)))
    chunks.push(link(m.captures.at(1), text(m.captures.at(0))))
    cursor = m.end
  }
  chunks.push(text(s.slice(cursor)))
  chunks.join()
}

#for block in read("report.md").split("\n\n") {
  let block = block.trim()
  if block == "" {
    none
  } else if block.starts-with("# ") {
    heading(level: 1, inline(block.slice(2)))
  } else if block.starts-with("## ") {
    heading(level: 2, inline(block.slice(3)))
  } else if block.starts-with("```") {
    let lines = block.split("\n").filter(l => not l.starts-with("```"))
    raw(lines.join("\n"), block: true)
  } else if block.starts-with("| ") {
    let rows = block.split("\n").filter(l => not l.starts-with("| ---"))
    let cells = ()
    for row in rows {
      for cell in row.trim("|").split("|") {
        cells.push(inline(cell.trim()))
      }
    }
    text(size: 8.2pt, table(columns: (1fr, 1.7fr, 1.8fr), inset: 4pt,
      stroke: 0.35pt + rgb("b5c1ca"),
      fill: (x, y) => if y == 0 { rgb("edf2f6") } else { none },
      ..cells))
  } else if block.starts-with("![") {
    figure(image("diagram.svg", width: 100%), caption: [Prospective system and gates; no numerical plot is appropriate for an unexecuted design.])
  } else {
    par(inline(block.replace("\n", " ")))
  }
}
