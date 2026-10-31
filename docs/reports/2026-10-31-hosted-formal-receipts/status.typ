#set page(paper: "a4", margin: 22mm)
#set text(font: "DejaVu Sans", size: 10pt)
= Hosted formal receipt audit
#text(fill: rgb("475569"))[PR #2805 · CI test merge `232f4e7` · October 31, 2026]

A fresh full Lake workspace build and the per-target machine/axiom gate completed on hosted run `41155781140`. The downloaded artifact contains 91 exact named target receipts. The reproducible audit reports zero issues.

#table(
  columns: (3.5fr, 1fr), inset: 7pt,
  [*Check*], [*Matched*],
  [Target spec, Lean module, theorem name], [91 / 91],
  [Machine verified, build, axiom audit], [91 / 91],
  [Declared source blobs], [32 / 32],
  [Tracked workspace inputs], [73 / 73],
  [Generated root from 51 modules], [1 / 1],
  [Verifier input blobs], [10 / 10],
)

All 91 receipts mark semantic review `pending`. Independent reviews are separate records; the raw receipts do not inherit their verdicts. The target count is not a denominator for all scientific claims across the repositories.

#v(12pt)
*Claim boundary.* Kernel acceptance and input hash consistency do not authenticate historical execution or prove that the formal statement fully captures a source claim. The Semaev finite-model meaning review is archived separately, with a visible batch-independence protocol gap.

#v(12pt)
*Reproduction.* See `README.md`, `verify_receipts.py`, `audit.json`, and the 91 raw files under `receipts/`.
