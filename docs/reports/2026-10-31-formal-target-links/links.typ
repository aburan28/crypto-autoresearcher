#set page(paper: "a4", margin: 22mm)
#set text(font: "DejaVu Sans", size: 10pt)
= Formal target source pointers
#text(fill: rgb("475569"))[Auto-researcher main `e03417c` · October 31, 2026]

The 91 formal target specs declare 32 distinct source files. Each row in `links.json` binds the target, source, and Lean module to exact-tree SHA-256 hashes.

#table(
  columns: (2.3fr, 0.5fr, 2.2fr),
  inset: 7pt,
  [*Pointer category*], [*Targets*], [*Interpretation*],
  [Source under an `EXP-*` directory], [8], [Direct experiment path],
  [Source under a `RUN-*` directory], [0], [No direct run path],
  [Source bytes mention standalone `EXP-*`], [17], [Six distinct tracked IDs],
  [Source bytes mention standalone `RUN-*`], [11], [Five distinct IDs],
)

The categories overlap. The two FROB run IDs without matching `RUN-*` directory names appear in manifests inside `TASK-*` directories. The prior count of eight unique experiment IDs included two strings inside amendment IDs; the standalone count is six.

#v(12pt)
*Claim boundary.* These are source links. They do not elaborate Lean declarations, review theorem meaning, validate measurements, or authenticate run execution. A source status of `PROVED` is metadata, not a verdict from this inventory. No proof-coverage percentage follows without a claim-level denominator.

#v(12pt)
*Reproduction.* `python3 tools/formal_target_source_inventory.py e03417ca2831c6000f100e55b5cb4185b0421072 docs/reports/2026-10-31-formal-target-links/links.json`
