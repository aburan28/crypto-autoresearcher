# Special-structure ECDLP leads: search of 2026-10-31

Four reports from a parallel search for special-structure leads that the lead atlas (`knowledge/leads/ecdlp/`) does
not already hold. **They are ideation output, not evidence.** Three agents each took one family; a fourth scanned the
literature. Literature entries were read at abstract level only (several PDFs returned 403), and any claim marked
"recalled" was not opened. The top-level session checked four atlas-hygiene claims directly (a stale citation, two
duplicate Miller leads, a missing Lattes row, an obstruction label) and all four held.

| file | family |
| --- | --- |
| `family-A-arithmetic.md` | arithmetic structure of p, N, t, the discriminant and conductor |
| `family-B-module.md` | module and representation structure (torsion Galois image, twists, level structure, simulability) |
| `family-C-lifting.md` | cross-field, lifting and dynamics structure |
| `literature.md` | 2023 to mid-2026 literature scan, checked against the atlas |

## Outcome

No exponent-level lead was found. All three families report saturation: every closed lead rests on one of three
facts (the scalar action is all of the group's endomorphisms; the pairing half of the torsion lives over the
embedding-degree field; curve and class data are independent of the secret). The value found is closure, one
construction that has never been built, and corrections.

- **New atlas rows:** `LEAD-EXO-lattes-xline-dynamics`, `LEAD-STR-level-structure-torsor`,
  `LEAD-TRF-kernel-of-reduction-lemma`, `LEAD-EXO-minors-guess-and-determine`.
- **New idea:** `IDEA-20261031-6610ed`, the prime-field Koblitz analogue, advancing
  `LEAD-STR-small-cm-disc-nonunit-endo`. Two families proposed it independently. Predicted outcome: a net loss.
- **Draft experiment designs:** `coordination/design/SPECIAL-STRUCTURE-LEADS-20261031/` (see its README).
- **Atlas edits in place:** the two Miller-cocycle leads are cross-linked (`related`); the small-CM obstruction is
  relabelled `cost_model` (its load-bearing clause was never measured at the equality case); a wording fix in
  `LEAD-TRF-second-torsion-direction`.

## Not fixed here (records are immutable or out of scope)

- `DEC-20261023-26a6de` cites `KN-LIT-7593` for a kernel short-vector pre-screen, but that id is an unrelated AES
  paper. Decisions are immutable; a correction record would be needed.
- `LEAD-TRF-global-lift-small-height` cites "uniform reduction" in its obstruction text, which that same decision
  records as contradicted (the closure rests on the counting law). Worth a curated edit at the next atlas review.
- `revisit_when` of `LEAD-ICP-xedni-function-field-sections` and `LEAD-TRF-function-field-xedni-lift` is satisfiable
  by Ulmer-type surfaces and should name the lift-finder cost, not lift existence.
- Seven earlier ideas (`IDEA-20261024-*`) remain without a lead in `coverage.tsv`.

## Corrections the design probes made to these reports

- Koblitz analogue: group order is 4l (not prime) and the prime is N(1 +- 2 delta); only h = 19 and 23 are equality
  cases in 16..24.
- Lattes: the k-independence claim needs d coprime to the order of P.
- Kernel of reduction: the minimum over fibres is a theorem (height at least 4); the test must read a prescribed
  fibre.
- Ulmer: the finder may be table-free at weight 2, and the report's permutation null is invalid.
- Level structure: not closable by derivation alone (gonality over F_p at N comparable to p is unproved).
- Volcano transport: q^0.4 is below sqrt, so the exponent alone does not close that lead.
