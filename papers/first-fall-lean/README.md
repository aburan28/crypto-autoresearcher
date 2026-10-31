# Machine-checked first-fall-degree reasoning in Weil-descent ECDLP

**Status: manuscript draft (LaTeX, `make check` passes, 7 pages), anonymized,
not submitted, not cleared for posting.** The checklist below is owed first.
The built PDF (about 330 KB) is not in git: it exceeds the 64 KiB data limit
and waits for an artifact-store push (see Build).

## What it says

1. **Counterexample to Lemma 4 of Nagao, ePrint 2015/984** (d_ff <= d'_ff),
   under the *equality* reading of condition (1) of Definitions 5-6. Two systems
   over F_2 have true first fall degree 3 and fake first fall degree 2, with the
   field equations inside the system (Lean: `lemma4_inside_false`). The printed
   placement fails on the same witnesses (hand and exhaustive search, not Lean).
   Proposition 6 gives the instance-wise recovery rule and a paper proof; the
   paper's own uses (proof of its Lemma 6) satisfy it.
2. **Caminata-Gorla Theorem 2.8, formalized** over Mathlib `MvPolynomial`: with
   finite last fall degree and some fall, d_F is the largest fall degree
   (`lastFallDegree_eq_max_degreeFall`). One observed fall is a lower bound only.
3. **Finite Semaev S3 audit**: Lean-checked direct-row ranks 1/11/53 and new-class
   counts 0/0/1 with an explicit degree-three witness; an independent code review
   gives closure counts (12 new classes at degree three vs 1 direct). Over 80
   draws the grades agree and the degree-three multiplicities differ for 77. The
   earlier uniform degree-two first-fall inference is withdrawn.

## What it does not say

Nothing about Nagao's Proposition 5, Semaev's first-fall assumption in general,
any complexity estimate, or ECDLP cost at any size. The `>=` reading of
2015/984 is not refuted (under it the lemma holds trivially). Change class:
correction of a published lemma plus formalization; no advance, engineering,
relabelling or accounting claim.

## Evidence

| Paper item | Artefact | Kernel | Independent statement review |
|---|---|---|---|
| Thm 5 | `formal/CryptoResearch/Nagao/Lemma4Witness.lean`; target `formal/targets/nagao-lemma4-inside-counterexample-20261029.yaml` | hosted receipt, run 41155781140 (`docs/reports/2026-10-31-hosted-formal-receipts/`) | **not yet reviewed**; producer caps fidelity at partial (`docs/reports/2026-10-29-nagao-lemma4-lean/report.md`) |
| Thm 5, Python | `tools/lemma4_inside_form.py`, `tools/test_lemma4_inside_form.py`; `knowledge/findings/KN-FIND-936151.md`; `ledger/evidence/EV-SEMBIN-1ca3c8.yaml` | n/a | two blind implementations; 94/400 random violations |
| Prop 6 | paper proof; rule stated in `KN-FIND-936151` section 4 | not formalized | none |
| Thm 7 | `formal/CryptoResearch/FallDegree/LastFall.lean` | hosted run 41191503149 | validated at stated scope (`coordination/formal-reviews/lastfall-native-20261031/archive/synthesis.md`) |
| Thm 8 | `formal/CryptoResearch/Semaev/BooleanParity*.lean`, `ConcreteFirstFallWitness.lean`, `FiniteEquationSemantics.lean` | hosted receipts, run 41155781140 | concrete witness validated at scope (`coordination/formal-reviews/BATCH-016711/`); rank family sheriff-audited only (`research/sheriff/SHF-20261023-7b9227/`) |
| Closure counts | `docs/reports/2026-10-26-semaev-closure-review/` | not formalized | independent code review |
| Withdrawn inference | `formal/targets/corrections/2026-10-25-semaev-s3-degree-two.md`; `docs/reports/2026-10-25-semaev-semantic-review/composition.md` | identity machine-verified | identity valid, inference withdrawn |

The witnesses of Theorem 5 (both placements) were also re-derived by an
exhaustive cofactor search while drafting; that script is not committed.

## Build

`make` (pdflatex), `make check`. No bibliography file; references are inline.
Needs TeX Live's latex-base, latex-recommended and fonts-recommended packages
and lmodern.

`paper.pdf` is over the repository's 64 KiB data limit (AGENTS.md, "Data files
live in the artifact store"). Until someone with store credentials runs
`python3 tools/artifacts/artifacts.py push papers/first-fall-lean/paper.pdf`
and commits the `.artifacts.json` and `.gitignore` it writes, `paper.pdf` is
ignored locally and must be rebuilt with `make`.

## Owed before submission

- [ ] Independent statement review of `lemma4_inside_false` (formal lane gate).
- [ ] Lean proof of the printed (outside) placement and of Proposition 6.
- [ ] Bridge from the list-of-monomials model to Mathlib `MvPolynomial`.
- [ ] Independent human check of Proposition 6 and of the reading of 2015/984's
      Lemma 6 (`KN-FIND-936151` section 4).
- [ ] Novelty audit: prior-remark search recorded in `../nagao-lemma4-note/note.md`
      section 4 and `docs/ecdlp-literature-review-20260926.md` section 5; repeat
      against post-2015 citations of 2015/984 and 2021/1611.
- [ ] Decide whether to contact the author of 2015/984 first.
- [ ] `make deanonymize` and ePrint packaging (`make eprint`) only after the above.

Supersedes nothing: `../nagao-lemma4-note/` remains the short Markdown note.
