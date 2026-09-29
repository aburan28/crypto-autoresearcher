# R4 — nulls, nearby object, censoring design, presentational budget and the named confounds

Red Team, TASK-20260904-3a2ff5. Sources: the regenerated tables (`r0_controls.json`),
`analysis.md` sections G, H, K, L, N, `stage0-transfer.md` section 3,
`stage1-closure-convention.md` section 3, the equal-d^s and m = 3 raw records.

## (a) The controlled null fired: nothing Semaev-specific survives

F5 regenerated from raw: NULL-1 false, NULL-2 false, NON-CURVE CUBIC **true** -- the
singular Weierstrass cubic (4A^3 + 27B^2 = 0, nodal) with the same digit generators
reproduces the Semaev (d_ff, d_lf) pair at EVERY one of the 15 cells, on all 600 draws,
including the censoring status. That is the pre-registered controlled-null condition of
the contract's own `falsification_criterion`.

NARROWEST SUPPORTED STATEMENT (this is the statement the package licenses, and no
stronger one):

  On the tested ladder (m = 2, d = 2, s = 2..5, p in {4099, 16411, 65537}, 8 curves x
  5 planted targets per cell, D_max = 7, convention cbdefb-closure-v1), the first and
  last fall degrees of a SINGLE degree-4 multilinear generator in 2s squarefree digit
  variables whose top form is the monomial-supported tensor square of the digit linear
  forms are equal, take the values 5, 5, 6, 6, and every fallen system's first cascade
  computes the whole ideal cap at that degree. The measurement is about digit complete
  intersections of this shape. It says nothing that is specific to summation
  polynomials, to a non-singular elliptic curve, or to the ECDLP.

Audit of the package for statements exceeding that scope: `analysis.md` is uniformly
scoped and states F5 noncurve = true in section H and section M; `execution-report.yaml`
observations record it verbatim; the executor_assessment makes no Semaev-specific claim.
I found NO Semaev-specific statement in the package that the controls do not license.
NULL-3 (block-factored) also matches the full pair at s = 3, 4, 5 with difference 0 in
both coordinates, which is H-PFDR-4148b8's prediction for d_ff and, for d_lf, a further
demonstration that the curve does not enter the observable.

## (b) D_max = 7 removed the null's own top cell

The frozen band is s + 2 + c, c in {0, 1, 2}, so at s = 5 the band predicts d_lf up to 9;
D_max = 7 makes any value above 7 unobservable. Result: NULL-1 (600 objects) and NULL-2
(15) are fully censored at s = 5 -- no fall in (4, 7] on any of them -- and the band is
not testable at the ladder's top. WHAT THE BAND CHECK LOST: the only cell where the band
could have been violated upward is the one that was not measured. HEUR-001 is supported
at s = 2, 3, 4 (offset c = 1 on every uncensored draw, i.e. the null's last fall is
exactly s + 3 = EXP-PFDR-5726af's D_null convention) and NOT TESTED at s = 5.

Two further readings the tail check should carry:
- "band offset grows with s: True" is driven ENTIRELY by the s = 1 cell (c = 0 there,
  c = 1 at s = 2, 3, 4). At s = 1 the ring has n = 2 and only 4 monomials, so no fall
  above D = 3 is possible at all: c = 0 is a ring-size boundary effect, not evidence
  about the null's growth. On s = 2..4 the offset is CONSTANT. The tail check's own
  trigger ("a growing c means the band must be widened") therefore fired on a boundary
  artifact; the executor's prose discloses the pattern but the boolean does not.
- the retained s = 1 NULL-1 draws are not a random subset: see (e).

## (c) The presentational artifact budget is unmeasured

CTRL-EQUAL-DS-SPREAD at B = 64 ran (2, 6), (4, 3), (8, 2) with D_max = 6. All 45
instances report NO fall in any presentation, all right-censored, so the observed spread
in d_ff and d_lf is the empty set. This was forced by the design, not by the data: the
(2, 6) arm is the digit presentation at s = 6, whose derived first fall is
4 + floor(6/2) = 7 > 6 = D_max; the (4, 3) and (8, 2) arms are ordinary rings whose
membership generators have degree 4 and 8 and which are never certifiable in any case.
CONSEQUENCE: 84cdb7's "a claimed effect must exceed the presentational spread by a factor
2" rule has no denominator on this package. Any statement in this lane that leans on that
rule is currently uncalibrated, and should say so.

## (d) The (3, 2, 3) cell and NULL-3's boundary

At m = 3, s = 3 the reduced S_4 generator has digit degree 9 > D_max = 7, so every arm is
degenerate and the cell yields nothing. This is the same fact -- deg S_{m+1} = m 2^{m-1},
so 12 at m = 3 and 9 after reduction in 3s = 9 squarefree variables -- that voids
EXP-PFDR-c04716's m >= 3 cells. It was run and recorded rather than skipped, which is
correct practice; it is a design ceiling, not a failure. NULL-3 is likewise degenerate
below s = 2^{m-1} (zero form at m = 2, s = 1; a single monomial with no closure fall at
m = 2, s = 2; identically zero at m = 3, s = 2, 3), so the NULL-3 comparison exists only
at s >= 3 at m = 2. Anomaly A-NULL3-BOUNDARY (the closure and the graded-rank meter
disagree at that boundary cell) is disclosed and is confined to the degenerate object.

## (e) The count-1 rule at s = 1: the tell fired on a non-artifact, and it selected

Regenerating the s = 1 histories and cross-tabulating the iteration count at D = 3
against the certificate's Z_size (`ptm4_s1.json`) gives a complete separation, 1200 of
1200 systems:

| arm | Z_size | iteration count at D = 3 | dim W_0 | dim V | dim(I cap B) | count |
|---|---|---|---|---|---|---|
| semaev | 1 | 1 | 3 | 3 | 3 | 89 |
| semaev | 2 | 1 | 2 | 2 | 2 | 31 |
| noncurve | 1 | 1 | 3 | 3 | 3 | 55 |
| noncurve | 2 | 1 | 2 | 2 | 2 | 65 |
| null1 | 1 | 1 | 3 | 3 | 3 | 165 |
| null1 | 0 | 2 | 3 | 4 | 4 | 435 |
| null2 | 0 | 2 | 3 | 4 | 4 | 15 |

At s = 1 the ring has n = 2 and 4 monomials; B_{<=3} = B_{<=2} = B, so at D = 3 EVERY
element is fallen and W_0(3) is the full Macaulay space {S~, a_1 S~, a_2 S~}. Whenever
the system has a root, dim(I cap B) <= 3 = dim W_0(3), so W_0 is already the whole ideal
cap and multiplying the fallen rows inserts nothing: iteration count 1 BY SATURATION.
When the system has no root, I = B has dimension 4 > 3 and one insertion occurs: count 2.

WHAT THE TELL ACTUALLY DETECTS. `iteration_count(D) = 1 at a fall` means "the fallen
rows' variable multiples added no new pivot". That has two causes: a non-iterating
closure (the artifact the control was written for) and W_0(D) already equal to the ideal
cap (saturation). The tell cannot separate them; the `W0_saturated` diagnostic can, and
it is TRUE on all 405 invalidated Semaev/non-curve entries and all 165 invalidated
NULL-1 entries. So invalidating those falls was the literal application of the frozen
rule and was correct as procedure, but the resulting analysis row "s = 1: no valid fall"
is an artefact of the rule and not a measurement: the raw, correct s = 1 answer is
(d_ff, d_lf) = (3, 3) on all 120 Semaev draws, which is what CTRL-S1-BASELINE actually
passed on (floor d_lf >= 2 satisfied). The instrument was returned to Stage 1 as the rule
demands and the fixtures P and H (iteration count 2 at their planted falls) cleared it.

EFFECT ON THE FITS: none. s = 1 is outside the pre-declared primary range, and the
secondary fit is numerically identical (n = 480 in both) because the invalidation removed
every s = 1 Semaev draw.

SELECTION EFFECT WORTH NAMING: at s = 1 the rule keeps exactly the NULL-1 objects with NO
root and discards exactly those with one. The band table's s = 1 row is therefore
computed on a conditioned subsample. Here it changes nothing (both classes have raw
(3, 3), hence c = 0), but a rule that removes precisely the solvable systems is the wrong
default for a lane whose object is solvability, and should be re-worded before reuse:
"iteration count 1 AND W0_saturated false" is the artifact tell; "iteration count 1 AND
W0_saturated true" is a saturated ring.

## (f) The named confounds

- IDEA-20260830-cb8e46 (CRT / complete-splitting artifact of a tiny planted zero set):
  the certificate DOES use ideal-level objects -- Z, I(Z), dim(I cap B_{<=D}) -- but only
  to decide the censoring flag and the diagnostics, never to compute d_ff or d_lf. I
  checked `measure_system` in `closure.py`: `falls`, `d_ff`, `d_lf`,
  `fall_iteration_counts`, `no_fall_in_window` and `single_fall_degree` are all read off
  the closure history alone, before `certify_history` is called; the certificate result
  only sets `right_censored`. That is legitimate: certifying "no fall above D_max" is a
  statement about the closure sequence's limit, for which the ideal is the correct
  reference object, and the reported metric stays generator-level. NOTE for the record,
  though: because the certificate is C1 alone (see `r2-closure-and-certificate-note.md`),
  the censoring flag is exactly the ideal-level predicate "the closure has solved by
  D_max". So the DATA SET entering a d_lf fit is selected by an ideal-level quantity even
  though each d_lf value is generator-level. That is the honest form of the confound and
  it should be stated in the evidence record.
- IDEA-20260807-899c5e (output-degree proxy): no Groebner basis and no reduced-basis
  degree appears anywhere in `closure.py`, `run_cbdefb.py`'s measurement path or
  `analyze.py`'s metrics. Confirmed by reading the code and by the absence of any such
  field in the raw records.

RESULT FOR R4: HOLDS as validity. Four scope findings must reach the evidence record:
the non-curve cubic makes every conclusion a statement about digit complete
intersections (a); the null band is untested at the ladder's top and its "grows with s"
flag is an s = 1 boundary artifact (b); the presentational artifact budget is unmeasured,
so 84cdb7's factor-2 rule is uncalibrated (c); and the censoring flag is an ideal-level
selector on the fitted sample (f).
