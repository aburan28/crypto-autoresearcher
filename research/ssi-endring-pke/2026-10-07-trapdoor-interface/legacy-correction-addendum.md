# Additive source-locator correction and inherited controls

This note is additive. It does not modify the historical source note at
`coordination/design/TASK-20261007-8b5d55/tasks/TASK-20261007-efaa15/sources/degree-norm.md`
or the historical manifest at
`coordination/design/TASK-20261007-8b5d55/tasks/TASK-20261007-efaa15/source-evidence.yaml`.

For J.S. Milne, *Elliptic Curves*, second edition, source bytes SHA-256
`646c0c4f193cdaa35f32c7d60fbd46a75e2f5187db4301810e8613726e3ebbee`,
the correct one-based PDF mapping is:

| Printed locator | Correct PDF page(s) |
| --- | --- |
| 69--70 | 74--75 |
| 74 | 79 |
| 75 / Lemma 6.12 | 80 |

The prior note's PDF-page values 73--74, 78, and 79 are off by one. This
correction is bound to the independent inspection at
`coordination/design/TASK-20261007-8b5d55/reviews/TASK-20261007-08f33e/source-visual-audit.yaml`.
It corrects metadata only; it does not strengthen the theorem scope, repair the
separate categorical quotient source gap, resolve the C6 digit-loop ambiguity,
or change any historical J4/J5 verdict.

The normalized `x(X)`, `P=O`, and lower-order-point controls are used exactly
as summarized in `methodology.md`. Fresh T5 review in this batch checks that
new artifacts use this mapping and do not overstate those inherited controls.
