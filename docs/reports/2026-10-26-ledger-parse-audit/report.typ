#set page(paper: "a4", margin: (x: 18mm, y: 17mm))
#set text(font: "DejaVu Sans", size: 9.5pt)
#set par(leading: 0.66em)

= Ledger YAML parse disposition audit
_26 October 2026 · crypto-autoresearcher main `6a69b2d02ecd53f1649bcf56e23e4ffe91d953ad`_

This is a read-only syntax and archive-routing audit. It makes no cryptographic
performance or proof-completeness claim.

== Question and source

The exact-main static dashboard reports 24 unparseable ledger YAML originals.
`audit.py` parses every `ledger/**/*.yaml` file, verifies registered original
and replacement SHA-256 pins, parses each replacement, checks its record ID,
cross-checks the merge gate, and compares the legacy baseline. The complete
per-path result is `evidence.json`; `render.py` produces the chart below.

#image("parse-dispositions.svg", width: 100%)

== Observation and meaning

#table(
  columns: (2.7fr, 0.5fr, 3.8fr),
  inset: 5pt,
  [Disposition], [Count], [Meaning],
  [Verified schema replacement], [9], [Archived malformed original with hash-bound, parseable, same-ID copy; semantic fidelity still needs review.],
  [Legacy parse baseline], [15], [Disclosed syntax defect with no verified replacement in this audit.],
  [Other unresolved], [0], [No further malformed ledger YAML in this exact-main sweep.],
)

The original records remain immutable. The 15 baseline entries remain defects;
the repository's merge gate allows them only as disclosed historical debt.
Neither the chart nor a parseable replacement verifies the research statement.

== Exit check

For each baseline record, preserve the original, add a semantically reviewed
parseable schema copy, pin both hashes, remove its baseline line, and rerun the
absolute merge-hygiene gate, ledger validator and this audit. Success requires
the baseline count to fall without creating an unresolved failure. The full
experiment and Lean proof validation remains separate.

_Source: `docs/reports/2026-10-26-ledger-parse-audit/report.md` and the files beside it._
