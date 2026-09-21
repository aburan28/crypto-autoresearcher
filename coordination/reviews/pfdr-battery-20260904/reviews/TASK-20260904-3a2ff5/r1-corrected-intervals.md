# R1 — the slope interval, the outcome rule and the HEUR-002 falsifier statistic

Red Team, TASK-20260904-3a2ff5. All numbers regenerated from `runs/*/raw-result.json`
by `r0r1_fits.py` (output `r0r1_fits.json`). Scope: m = 2, d = 2, s = 2..5,
p in {4099, 16411, 65537}, D_max = 7, convention `cbdefb-closure-v1`.

## 1. What the per-draw interval is measuring

The 480 Semaev d_lf values in the primary fit are FOUR distinct integers, 5, 5, 6, 6,
each repeated exactly 120 times (40 draws x 3 primes). Within-cell range is 0 at all
twelve (s, p) cells (`r0r1_fits.json`, `B_within_cell_variance`), and the between-prime
range at fixed s is 0 as well. The response is a DETERMINISTIC function of s on this
data set; there is no sampling noise for a t-interval to estimate.

The residual sum of squares is therefore pure lack of fit. Per s-level the residuals of
the OLS line through (2,5), (3,5), (4,6), (5,6) are +0.1, -0.3, +0.3, -0.1, so
SSR = 0.2 per replicate block; with k replicates per s-level, SSR = 0.2k,
s^2 = 0.2k/(4k-2), S_xx = 5k, and the half-width shrinks like 1/sqrt(k) with no lower
bound. Replicating a deterministic value is not information about the s-slope.

THE ARTIFACT TELL, stated as the protocol asks (`docs/inventor-protocol.md` section 3):
the parameter that should destroy the signal is the replication count. Doubling the
number of curves or primes must NOT sharpen a statement about the s-dependence. Here it
halves the interval width. The producer's own bootstrap over draws within cells returns
the degenerate [0.4, 0.4], which is the same tell read from the other side.

## 2. The corrected interval and label table

| unit of replication | n | slope | 95% t-interval | contains 1 | excl. 0.5 | contains 0 | excl. 0.25 | d_lf label | HEUR-002 falsifier "excludes 0" |
|---|---|---|---|---|---|---|---|---|---|
| per draw (as reported) | 480 | 0.4000 | [0.3820, 0.4180] | no | yes | no | yes | unresolved | FIRES |
| one draw per distinct (curve, x_R) system | 332 | 0.4000 | [0.3783, 0.4217] | no | yes | no | yes | unresolved | fires |
| per (s, p) cell mean | 12 | 0.4000 | [0.2591, 0.5409] | no | no | no | yes | unresolved | fires |
| per s-level mean (the only non-replicated unit) | 4 | 0.4000 | [-0.2085, 1.0085] | yes | no | yes | no | unresolved | DOES NOT FIRE |

The per-draw row reproduces the execution report exactly ([0.3820, 0.4180], residual
variance 0.0502, n = 480), so this is not a disagreement about arithmetic.

Distinct generator systems per cell (from the raw `curve` / `target.x_R` fields):
17, 10, 12 at s = 1 and 29, 24, 30 at every s >= 2 out of 40 draws. So duplicate x_R is
a MINOR effect: 332 distinct systems still give a narrow interval. The pseudo-replication
that matters is not duplicate instances, it is zero variance across every axis except s.

## 3. The replication sweep: the exclusions are bought, not observed

Same four integers, k draws per s-level:

| k per s | n | 95% interval | excludes 0.5 | excludes 0.25 | excludes 0 | contains 1 |
|---|---|---|---|---|---|---|
| 1 | 4 | [-0.2085, 1.0085] | no | no | no | yes |
| 2 | 8 | [0.2002, 0.5998] | no | no | yes | no |
| 3 | 12 | [0.2591, 0.5409] | no | yes | yes | no |
| 4 | 16 | [0.2854, 0.5146] | no | yes | yes | no |
| 5 | 20 | [0.3010, 0.4990] | YES | yes | yes | no |
| 40 | 160 | [0.3686, 0.4314] | yes | yes | yes | no |
| 120 | 480 | [0.3820, 0.4180] | yes | yes | yes | no |
| 4800 | 19200 | [0.3972, 0.4028] | yes | yes | yes | no |

Five draws per s-level suffice to "exclude 0.5" on these integers. The contract's 40
draws per cell were justified as bounding the per-s spread; that spread is 0, so every
draw beyond the fifth only narrows an interval that is not estimating anything.

## 4. The instrument reports a FALSE exclusion against the law the data follow

The measured values are exactly H-PFDR-4148b8's derived step 4 + floor(s/2), whose
ASYMPTOTIC slope in s is 1/2. The finite-window OLS slope of that step on [2, S] is
0.4 at S = 5, 0.5 at S = 6, 0.4571 at S = 7, 0.5 at S = 8, ... -> 1/2
(`r0r1_fits.json`, `window_sweep_of_the_derived_step_law`). So 0.400 is a property of
the WINDOW [2, 5], not of the object; and the reported interval [0.382, 0.418] EXCLUDES
0.5 -- the true growth rate of the very law the integers reproduce with residual 0. On
the generating law the frozen statistic's "excludes 0.5" is wrong with probability 1 at
the tested replication. That is the decisive reason the interval is not an interval for
the quantity of interest.

## 5. Outcome II was unreachable, and the rule collapses to a linearity test

(a) Every fallen system in the package has exactly one fall degree, so d_ff = d_lf on
every draw, no Semaev draw is censored, and the d_ff fit and the d_lf fit are literally
the same fit (both [0.3820, 0.4180], both slope 0.4000; the execution report says so).
The joint rule's Outcome II clause -- "the d_ff interval lies strictly below the d_lf
point estimate" -- asks an interval to lie strictly below its own centre. It is
UNSATISFIABLE on any single-fall system. Outcome II was not rejected by the data; it was
excluded by the pre-registration.

(b) With n = 480 the interval half-width is 0.018, so the rule reduces to a test of the
POINT slope: Outcome I requires slope ~ 1 (i.e. d_lf = s + const exactly, residual 0);
Outcome III additionally requires all four of s = 2..5 to share one d_lf value, i.e.
exact flatness. Both surviving branches are exact-linearity tests. Every integer step
between them -- including the contract's own frozen prediction for d_ff, the step
5, 5, 6, 6 -- lands in "unresolved" by construction.

CONCLUSION FOR THE LABEL. "Unresolved" is the only output the frozen rule can produce on
an object of this shape. It is a fact about the rule, not about the last fall degree.
The rule was mis-specified for a lattice-valued response measured on a four-point window
at resolution 0.25: it can separate slope 0 from slope 1 only when the response is
exactly linear, and it has no branch for the half-slope step the contract itself
predicted for d_ff.

## 6. The honest statistic that the integers do support

No interval is needed. On 480 of 480 Semaev draws, at three primes, with certified
complete histories and no censoring:

  d_lf(2) = d_lf(3) = 5 and d_lf(4) = d_lf(5) = 6.

So d_lf is NOT constant on s = 2..5: it increases by exactly 1 between s = 3 and s = 4,
deterministically. That refutes flatness on the tested range (and therefore Outcome
III's flatness clause, independently of any interval), and it is consistent with, but
does not by itself establish, unbounded growth. The unbounded-growth statement comes
from d_lf >= d_ff together with H-PFDR-4148b8's d_ff law (see
`derivation-r3-single-fall.md` section 8a), not from this ladder's slope.

RESULT FOR R1: BREAKS -- the execution report's "the pre-registered condition fires"
statistic does not survive an honest unit of replication (it does not fire on the four
independent s-points), and the pre-registered rule could not have returned anything but
"unresolved" here. The integers are untouched and reproduce exactly.
