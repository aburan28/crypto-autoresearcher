#set page(paper: "a4", margin: (x: 1.6cm, y: 1.5cm), footer: context align(right, text(size: 8pt, counter(page).display("1"))))
#set text(font: "Liberation Sans", size: 9pt, lang: "en", ligatures: false)
#show raw: set text(font: "Liberation Mono")
#set par(justify: false, leading: 0.55em)
#set heading(numbering: none)
#show heading: set block(above: 0.8em, below: 0.4em)
#heading(level: 1)[#text("F6 second pass: prepared, not executed")]
#figure(image("diagram.svg", width: 100%, height: 5.4cm, fit: "contain"), caption: [Editable study diagram; exact scope and evidence paths appear in the report.])


#text("The task is TASK-20261026-2746d0. Source preparation follows the committed Phase A card. The runner will screen twelve total-degree staircase families at five fixed widths, inspect a root-independent public-target 8-by-8 box, and reduce two fixed small matrices, including a labelled known-root control.")
#parbreak()

#text("No second-pass observation is claimed here. Execution requires root's exact frozen protocol/source release and a successful real S3 checkpoint gate. The source accepts --help without collecting data. protocol.draft.json is prospective and must not be presented as a frozen preregistration.")
#parbreak()

#text("After release, run run.py --out runs/run-01 --seed 2026102606, then analysis.py --run runs/run-01 --out reports/run-01, and export the same run using export.py --run runs/run-01 --protocol protocol.json --out export.json. Commands are run from this track directory with the released interpreter.")
#parbreak()
