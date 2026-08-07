# P3 — an adjudication predicate that separates, demonstrated on committed data

TASK-20260806-0617ed / BATCH-f19c37 / GOAL-MLKEM-005
Governed by DEC-20260806-00deff **AM-2**.

**Claim tier: TOY.** Nothing in this report supports any statement about ML-KEM
security or about any FIPS 203 parameter set. Every frame here is at `d <= 140`,
`beta <= 60`, `q = 3329`, `k = d/2`. Nothing is transported to `beta = 606,
d = 1420`. I am an Executor: this document contains observations and a
construction. **No status is changed and nothing is interpreted.**

Deliverables: `predicate.py`, `separation.json`, this file.

---

## 0. Result, stated first

**A predicate exists, and it separates.** AM-2 is met in **all four cells**, not
one.

The predicate is `P3`, whose statistic is the exact scalar

```
V(Q) = sum_a ( P_aa - beta/d )^2 ,      P = Q Q^T
```

computed on the tail-`beta` GSO frame with **zero error draws**. Its null
expectation `mu_0 = 2 beta (d-beta) / (d (d+2))` is a theorem, not a
calibration. Against the Haar null arm, on the already-committed
BATCH-436ddd / BATCH-a51f91 frames:

| cell | `real_bkz` verdict | Haar null verdict | verdicts differ | separation (SE of difference) |
|---|---|---|---|---|
| `d100_b30` | AGREEMENT (upper bound) | AGREEMENT (upper bound) | no | −1.08 |
| `d100_b40` | AGREEMENT (upper bound) | AGREEMENT (upper bound) | no | +1.58 |
| **`d140_b30`** | **DEPARTURE** | AGREEMENT (upper bound) | **yes** | **+5.48** |
| **`d140_b40`** | **DEPARTURE** | AGREEMENT (upper bound) | **yes** | **+6.37** |

and on the two weaker-reduction real arms, in **every** cell:

| cell | `lll_only` vs Haar | `unreduced` vs Haar |
|---|---|---|
| `d100_b30` | **DEPARTURE**, +5.70 SE | **DEPARTURE**, +249.92 SE |
| `d100_b40` | **DEPARTURE**, +5.31 SE | **DEPARTURE**, +587.32 SE |
| `d140_b30` | **DEPARTURE**, +9.90 SE | **DEPARTURE**, +262.03 SE |
| `d140_b40` | **DEPARTURE**, +13.04 SE | **DEPARTURE**, +499.24 SE |

The incumbent `P1/P2` returns `PASS/PASS` on `real_bkz` and on the Haar null arm
in all four cells, and `T2`'s own gate reaches at most **1.25 SE** on `real_bkz`
anywhere. `P3` reaches **6.37 SE** on the same frames, from the same seeds, with
no error draws at all.

**Detection floor**, declared in `V`-units, reported for every arm and every
verdict: `FLOOR = 4 * sd(V)/sqrt(n)`. At `n = 8` committed frames the realized
`real_bkz` floors are `0.069081 / 0.076887 / 0.086902 / 0.067925`. The two
`d = 100` cells return AGREEMENT, and that verdict is stated **only** as the
upper bound it is: excess in `V` at most **+0.0333** (`d100_b30`) and **+0.1088**
(`d100_b40`).

**The one thing that most needs saying against this result** is in §7: in the
held-out window sweep a *Haar null arm* reached `z = +3.98` against a gate of
`4.00`. It did not fire, but it came within 0.5% of firing, and I report the
mechanism and the measured false-positive rate rather than leaving it to review.

---

## 1. Provenance: what was and was not computed

**No new sampling.** Zero error vectors were drawn — not fewer, none. Zero new
lattices, zero new arms, zero new seeds. Every frame in the demonstration is
regenerated bit-exactly from the seed scheme committed in
`BATCH-436ddd/tasks/TASK-20260806-09ec68/b2a_results.json:seed_scheme`
(sha256 `4d36ca96ea15da25f092bbf680f278ed1515d3feee2e0df0e78f41bac4e875fa`),
which is itself identical to BATCH-a51f91 for the basis and Haar seed families.

Regeneration was **verified before any predicate number was computed**: 32 bases
× 6 committed diagnostics (`b0_norm_raw`, `b0_norm_lll`, `b0_norm`, and the
three GSO log-slopes). Maximum relative deviation across all 192 comparisons:

```
0.0                    (exactly zero, not "below tolerance")
```

The script aborts and writes nothing further on any mismatch. This is the
verification the AM-1 lane calls "the seeds are the cache"; it is what makes
"regenerated" and "committed" the same data rather than similar data.

One calibration computation in §7 samples Haar frames — a mathematical object,
not a research datum. It is labelled there, it entered no verdict, and deleting
it changes nothing in `separation.json`.

---

## 2. The predicate

The full frozen spec is `predicate.py:SPEC_MD`, sha256
`c547573c9167ca5a2d9c9359cadbc74287e82600c4a7e405f3b0b034650eec4c`, recorded in
`separation.json:spec_sha256`. Summary:

**Statistic.** `V(Q) = sum_a (P_aa - beta/d)^2`, a deterministic scalar of the
frame. `trace(P) = beta` is forced, so `V` is the dispersion of the
coordinate-participation profile about a mean it cannot avoid.

**Verdict rule.** With `n` frames, `Vbar`, `s` (ddof=1), `SE = s/sqrt(n)`:
`z = (Vbar - mu_0)/SE`; **DEPARTURE** iff `z >= 4`, otherwise
**AGREEMENT_UPPER_BOUND**; `z <= -4` is `ANOMALY_BELOW_NULL` and is an
instrument fault, not a finding.

**Detection floor.** `FLOOR = 4 * SE`, in `V`-units, reported for every arm.
Every AGREEMENT is emitted as `excess <= (Vbar - mu_0) + FLOOR`. The predicate
has no code path that can print the word "absent".

### 2.1 Why this statistic, and not one that happened to work

This is the question the campaign's three failed controls (CTRL-BS,
CTRL-POSHOM, CTRL-IDXMAP) were each accepted without answering. Three reasons,
all exact, none fitted.

**(a) The null mean is a theorem.** For a Haar rank-`beta` subspace,
`P_aa ~ Beta(beta/2,(d-beta)/2)`, so
`E[V] = d * Var(P_aa) = 2 beta (d-beta) / (d (d+2))` exactly. There is nothing
to calibrate and no reference arm the predicate needs.

**(b) `V` is the *only* second-order invariant, not one of many.** The error law
is iid across coordinates and sign-symmetric, so an admissible statistic must be
a function of `P` invariant under signed coordinate permutation — a
rotation-invariant function of `Q` alone is constant and carries nothing. At
second order in the entries of `P` there are exactly two such invariants, and
they are not independent, because `P` is a projector:

```
sum_{a,b} P_ab^2 = trace(P^2) = beta
  =>  sum_{a != b} P_ab^2 = beta - beta^2/d - V
```

The off-diagonal energy is an **affine function of `V` with zero freedom**.
There was no search over candidate statistics because at this order there is
nothing to search.

**(c) `V` is the exact sufficient statistic for the incumbent instrument's own
signal.** For iid unit-variance coordinates with fourth moment `mu_4` and
symmetric `A`, `Var(e^T A e) = (mu_4-3) sum_a A_aa^2 + 2 trace(A^2)`. With
`A = P`:

```
Var(e^T P e) = 2 beta + (mu_4 - 3) ( V + beta^2/d )
```

`d`, `beta`, `mu_4` are fixed by the cell, so **the only frame-dependent term is
`V`**. `T2` is a `2^20`-draw estimator of a tail quantile whose leading frame
dependence is this variance. `P3` computes exactly what `T2` was estimating
noisily. This is the red team's §3 identity, used here as the construction
principle rather than as an after-the-fact rationalization.

**The only tunable constant is the gate `K = 4.0`, and it is inherited verbatim**
from `b2a.py:GATE_K` under DEC-20260805-4823db. It was not chosen by this task.

---

## 3. The AM-2 demonstration, per cell

`n = 8` frames per arm, the committed count. `mu_0` exact. All values in
`separation.json:cells`.

### `d100_b30` — `mu_0 = 0.411765`

| arm | `Vbar` | sd | SE | excess | `z` vs exact null | frames > `mu_0` | verdict |
|---|---|---|---|---|---|---|---|
| `unreduced` | 9.362794 | 0.080704 | 0.028533 | +8.9510 | +313.70 | 8/8 | DEPARTURE |
| `lll_only` | 0.607499 | 0.078845 | 0.027876 | +0.1957 | +7.02 | 8/8 | DEPARTURE |
| `real_bkz` | 0.375945 | 0.048848 | 0.017270 | −0.0358 | −2.07 | 2/8 | AGREEMENT (≤ +0.0333) |
| `haar_null` | 0.406015 | 0.061338 | 0.021686 | −0.0057 | −0.27 | 4/8 | AGREEMENT (≤ +0.0810) |

Separations vs Haar null: `unreduced` **+249.92 SE**, `lll_only` **+5.70 SE**,
`real_bkz` −1.08 SE.

### `d100_b40` — `mu_0 = 0.470588`

| arm | `Vbar` | sd | SE | excess | `z` | pos | verdict |
|---|---|---|---|---|---|---|---|
| `unreduced` | 16.244628 | 0.048314 | 0.017082 | +15.7740 | +923.45 | 8/8 | DEPARTURE |
| `lll_only` | 0.743722 | 0.140573 | 0.049700 | +0.2731 | +5.50 | 8/8 | DEPARTURE |
| `real_bkz` | 0.502484 | 0.054367 | 0.019222 | +0.0319 | +1.66 | 5/8 | AGREEMENT (≤ +0.1088) |
| `haar_null` | 0.457916 | 0.058700 | 0.020754 | −0.0127 | −0.61 | 5/8 | AGREEMENT (≤ +0.0703) |

Separations: `unreduced` **+587.32 SE**, `lll_only` **+5.31 SE**, `real_bkz`
+1.58 SE.

### `d140_b30` — `mu_0 = 0.331992`

| arm | `Vbar` | sd | SE | excess | `z` | pos | verdict |
|---|---|---|---|---|---|---|---|
| `unreduced` | 6.750435 | 0.052182 | 0.018449 | +6.4184 | +347.90 | 8/8 | DEPARTURE |
| `lll_only` | 0.755675 | 0.115132 | 0.040705 | +0.4237 | +10.41 | 8/8 | DEPARTURE |
| **`real_bkz`** | **0.470415** | 0.061449 | 0.021726 | **+0.1384** | **+6.37** | **8/8** | **DEPARTURE** |
| `haar_null` | 0.321874 | 0.045741 | 0.016172 | −0.0101 | −0.63 | 4/8 | AGREEMENT (≤ +0.0546) |

Separations: `unreduced` **+262.03 SE**, `lll_only` **+9.90 SE**, **`real_bkz`
+5.48 SE — verdicts differ.**

### `d140_b40` — `mu_0 = 0.402414`

| arm | `Vbar` | sd | SE | excess | `z` | pos | verdict |
|---|---|---|---|---|---|---|---|
| `unreduced` | 11.807462 | 0.055124 | 0.019489 | +11.4050 | +585.19 | 8/8 | DEPARTURE |
| `lll_only` | 1.117462 | 0.156128 | 0.055200 | +0.7150 | +12.95 | 8/8 | DEPARTURE |
| **`real_bkz`** | **0.513473** | 0.048030 | 0.016981 | **+0.1111** | **+6.54** | **8/8** | **DEPARTURE** |
| `haar_null` | 0.381117 | 0.033942 | 0.012000 | −0.0213 | −1.77 | 2/8 | AGREEMENT (≤ +0.0267) |

Separations: `unreduced` **+499.24 SE**, `lll_only` **+13.04 SE**, **`real_bkz`
+6.37 SE — verdicts differ.**

**AM-2 requirement — different verdicts on the Haar null arm and a real arm in
at least one cell, separation in SE of the difference, on already-committed
data — is met in all four cells** (on `lll_only` and `unreduced` everywhere, and
additionally on `real_bkz` at both `d = 140` cells).

### 3.1 Independent-implementation agreement

My 8-basis values reproduce the red team's independently written 16-basis
computation (`red_team_report.md` §4) within its stated error:

| cell / arm | red team (16 bases) | this task (8 bases) |
|---|---|---|
| `d100_b30` unreduced | 9.35940 ± 0.01692 | 9.362794 ± 0.028533 |
| `d100_b30` LLL | 0.59748 ± 0.01814 | 0.607499 ± 0.027876 |
| `d100_b30` BKZ-30 | 0.38785 ± 0.01013 | 0.375945 ± 0.017270 |
| `d140_b30` unreduced | 6.74915 ± 0.01414 | 6.750435 ± 0.018449 |
| `d140_b30` LLL | 0.77053 ± 0.02648 | 0.755675 ± 0.040705 |
| `d140_b30` BKZ-30 | 0.47187 ± 0.01415 | 0.470415 ± 0.021726 |

Two implementations, written independently, agree. That is a check on the code,
not evidence about lattices.

---

## 4. Detection floors (`V`-units, `n = 8`)

| cell | `unreduced` | `lll_only` | `real_bkz` | `haar_null` | `graded t=1` |
|---|---|---|---|---|---|
| `d100_b30` | 0.114133 | 0.111504 | **0.069081** | 0.086745 | 0.054217 |
| `d100_b40` | 0.068326 | 0.198801 | **0.076887** | 0.083014 | 0.069849 |
| `d140_b30` | 0.073796 | 0.162821 | **0.086902** | 0.064688 | 0.065600 |
| `d140_b40` | 0.077957 | 0.220799 | **0.067925** | 0.048001 | 0.073052 |

Every negative verdict above is reported as an upper bound at its own floor and
nowhere as an absence. The floor scales as `1/sqrt(n)`, and the cost of lowering
it is reductions, not draws. At `d100_b30` `real_bkz` (`sd = 0.048848`),
pushing the floor from its present `0.069` down to `0.05` needs `n = 16`
frames, and further reduction is quadratic. That is **eight more LLL+BKZ-30
reductions — about 12 core-seconds at this cell, from the committed 1.5 s per
basis — and no measurement layer at all**, because `V` costs nothing once the
basis exists. At `d140_b40` the same eight extra frames cost about 810
core-seconds, so the floor is cheap at small `beta` and not cheap at large.

---

## 5. Head-to-head against the incumbent

Same four cells, same 8 basis seeds, same Haar seed family, same `n`.
Incumbent numbers from `b2a_results.json`.

| cell | `P1/P2` Haar | `P1/P2` `real_bkz` | `T2` gate on `real_bkz` | **`P3` separation** |
|---|---|---|---|---|
| `d100_b30` | PASS/PASS (r=0.998570) | PASS/PASS (r=0.998295) | −0.06 SE | −1.08 SE |
| `d100_b40` | PASS/PASS (r=0.999141) | PASS/PASS (r=1.000538) | +1.25 SE | +1.58 SE |
| `d140_b30` | PASS/PASS (r=1.001023) | PASS/PASS (r=0.999538) | −0.78 SE | **+5.48 SE** |
| `d140_b40` | PASS/PASS (r=0.999897) | PASS/PASS (r=1.000998) | +0.89 SE | **+6.37 SE** |

The incumbent's verdicts on the real arm and the null arm are identical in all
four cells, exactly as DEC-20260806-00deff records. `P3` is not a better-tuned
version of the same test; it removes the estimator. `T2` spends `2^20` error
draws per frame to estimate a tail quantile whose frame dependence is `V`.
`P3` computes `V`. The measurement layer of the incumbent — roughly 655 of
BATCH-436ddd's 1724 core-seconds — is not reduced, it is **absent**.

---

## 6. Behaviour on data the predicate did not see

This is where a predicate built against one dataset fails, so I report four
independent out-of-sample checks and one structural argument.

**(a) Exact point prediction at the coordinate-aligned extreme.** A frame that
is a coordinate selector has `P_aa in {0,1}`, so `V = beta(1-beta/d)` exactly.
The graded family at `t = 0` is that frame. Predicted before measurement,
measured after:

| cell | predicted | measured (all 8 frames) | max abs error |
|---|---|---|---|
| `d100_b30` | 21.000000 | 21.000000000000 | 7.1e-15 |
| `d100_b40` | 24.000000 | 24.000000000000 | 3.6e-15 |
| `d140_b30` | 23.571429 | 23.571428571429 | 3.6e-15 |
| `d140_b40` | 28.571429 | 28.571428571429 | 7.1e-15 |

All eight frames per cell give the identical exact value. This is a
falsification test with a pre-computable answer, not a fit.

**(b) A Haar arm from a disjoint seed family.** The graded family at `t = 1`
draws from `seed_graded`, disjoint from the `seed_haar` family the demonstration
uses. `P3` returns AGREEMENT in all four cells, `z` in `[-1.21, +0.21]`. These
frames were used to construct nothing.

**(c) Held-out tail windows.** `reduce_one` retains 60 GSO columns, so windows
at `betap in {50,60}` are available free on frames not used in §3. Eight
window-cells, `separation.json:held_out_window_sweep`. The `d = 100` / `d = 140`
pattern replicates in windows the predicate was never demonstrated on:

| window | `lll_only` vs Haar | `real_bkz` vs Haar |
|---|---|---|
| `d100` block-30 win-50 | +9.85 SE (DEPARTURE) | +1.49 SE (AGREEMENT) |
| `d100` block-30 win-60 | +6.18 SE (DEPARTURE) | +1.05 SE (AGREEMENT) |
| `d100` block-40 win-50 | +6.56 SE (DEPARTURE) | +3.90 SE (AGREEMENT) |
| `d100` block-40 win-60 | +4.63 SE (DEPARTURE) | +1.10 SE (AGREEMENT) |
| `d140` block-30 win-50 | +11.12 SE (DEPARTURE) | **+6.48 SE (DEPARTURE)** |
| `d140` block-30 win-60 | +10.90 SE (DEPARTURE) | **+5.65 SE (DEPARTURE)** |
| `d140` block-40 win-50 | +10.55 SE (DEPARTURE) | **+8.35 SE (DEPARTURE)** |
| `d140` block-40 win-60 | +10.21 SE (DEPARTURE) | **+5.70 SE (DEPARTURE)** |

**(d) The null needs no recalibration at a new `(d, beta)`.** `mu_0` is a closed
form. Verified by 4000-frame Haar sampling at eight `(d,beta)` including four
not in the cells (`predicate.py --calibrate`): every sample mean lands within
1.6 SE of the exact value, largest deviation `−1.34 SE` at `(100,60)`.

**The structural argument, which matters more than any of the four.** `P3` was
not selected by searching for something that separated. §2.1(b) shows that at
second order in `P` there is exactly one signed-permutation invariant, so there
was no candidate set to overfit against; and §2.1(c) shows that this same scalar
is forced as the sufficient statistic by an algebraic identity that holds for
any iid coordinate error law. A statistic with a theorem-valued null and no
free parameters cannot be tuned to a dataset, because there is nothing to tune.

**What this does not license.** None of (a)–(d) is a new `(d, beta)` regime, a
new `k`, or a new lattice family. The predicate's *calibration* transports by
theorem; its *verdicts* do not transport at all, and §8 lists what is untested.

---

## 7. The objection I am raising against my own result

In the held-out window sweep at `d = 140`, `betap = 60`, the **Haar null arm**
returned `z = +3.98` against a gate of `4.00`. It did not fire. It came within
0.5% of firing, and had it fired it would have been a false DEPARTURE on the
null.

Mechanism, measured rather than asserted. At `(140,60)` the true null sd of `V`
is `0.056058` (4000 frames), but that 8-frame arm's sample sd was `0.0347` — a
0.62× underestimate — while its mean sat `+2.3` true-sigma high. The `n = 8`
sample-SE `z` is over-dispersed relative to a standard normal by a measured
factor of **`z_sd = 1.18`–`1.20`** across all eight `(d,beta)`.

Measured one-sided false-positive rate of the `4 * SE`, `n = 8` gate under the
exact null (20 000 bootstrap arms per cell, `predicate.py --calibrate`):

| `(d, beta)` | FP rate | `z` sd |
|---|---|---|
| (100,30) | 0.00175 | 1.200 |
| (100,40) | 0.00145 | 1.186 |
| (140,30) | 0.00150 | 1.194 |
| (140,40) | 0.00145 | 1.198 |
| (100,50) | 0.00195 | 1.184 |
| (100,60) | 0.00190 | 1.195 |
| (140,50) | 0.00235 | 1.188 |
| (140,60) | 0.00295 | 1.193 |

So the gate operates at roughly the 0.15–0.3% one-sided level, **not** at a
4-sigma-normal level (`3e-5`), and a reviewer entitled to assume the latter
would be misled by a factor of ~60.

How lucky or unlucky was the near-miss? This task exercised **12 null arms**:
eight `seed_haar` arms (four cells plus four sweep windows) and four
independent-seed `seed_graded` `t = 1` arms. Measured `P(z >= 3.98)` at
`(140,60)` is `0.00147` (200 000 bootstrap arms), so
`P(at least one of 12 >= 3.98) = 0.017`. A 1-in-57 event did occur. That is
mildly unlucky rather than diagnostic of a broken null — the exact `mu_0` is
confirmed to 4000-frame precision at that same `(d,beta)` in §6(d) — but it is
the kind of thing that gets discovered by a reviewer if the producer does not
report it, so I am reporting it.

**Consequence for the AM-2 result.** It does not overturn it: the qualifying
separations are `+5.31` to `+13.04 SE` on `lll_only` and `+5.48` / `+6.37 SE` on
`real_bkz`, all well past the near-miss scale, and the `real_bkz` DEPARTURES are
`8/8` sign-consistent across bases. It does mean a `P3` DEPARTURE **in the
4–5 SE band** should not be trusted at `n = 8` without more frames.

**The successor I did not adopt.** Replacing the sample `SE` with the null `SE`
— `sd_0(d,beta)/sqrt(n)`, a fixed function of `(d,beta)` computable to arbitrary
precision from the null alone, with no research datum — removes the
over-dispersion entirely. I did **not** adopt it, because I demonstrated the
sample-SE version and adopting an undemonstrated improvement is precisely the
error AM-2 exists to prevent. It is a named, costed successor: one calibration
run per `(d,beta)`, no lattice work.

---

## 8. What I could not establish

1. **`V` is a property of a basis *presentation*, not of a lattice.** The same
   lattice under a different presentation gives a different `V`. Nothing here
   bears on attack cost, on any BKZ cost model, or on ML-KEM. A `P3` DEPARTURE
   on `real_bkz` at `d = 140` says the tail GSO frame of *those bases produced by
   that reduction pipeline* has excess coordinate-participation dispersion. It
   says nothing more.
2. **`P3` sees one thing.** A tail frame Haar-like in `V` but structured in any
   other invariant — a third-order diagonal moment, an off-diagonal pattern of
   fixed total energy, alignment with a secret direction — is invisible to `P3`
   at any `n`. AGREEMENT from `P3` is a statement **about `V`, at the stated
   floor**. It is not "the frame is Haar". §2.1(b) closes the second order only;
   third order and above are open and untouched.
3. **Nothing here discharges C3 or any other completion criterion.** AM-2 asks
   whether an admissible instrument exists. This answers that. It adjudicates no
   hypothesis.
4. **No closed form for `Var(V)`.** The false-positive rates in §7 are measured
   by null bootstrap, not proven. The exact-SE successor therefore currently
   rests on simulation of the null, not on a theorem.
5. **Untested regimes:** `k != d/2` (the discriminating test the red team names
   in its §11 and §2 — still not run); `d > 140`; `beta/d` outside `[0.21,
   0.43]`; block sizes other than `{30,40}`; any non-`q`-ary lattice family;
   `beta = 606, d = 1420`.
6. **This was not a blind pre-registration, and I will not claim it was.**
   `red_team_report.md` §4 already published approximate `V` values for these
   arms before this task ran. What I can claim is narrower and I state it
   exactly: `P3` has **no parameter fitted to any of that data** — `mu_0` is a
   theorem, the gate `4.0` is inherited from DEC-20260805-4823db, and the
   statistic is forced by §2.1(b)–(c). The `spec_sha256` was emitted before any
   research number in this run, but that is a within-run ordering, not an
   external timestamp, and it is weaker than the notarization the AM-1 lane gets.
7. **A cosmetic defect I chose not to spend budget fixing.** For the `graded
   t=0` anchor all 8 frames give the identical exact `V`, so the sample sd is
   floating-point dust (`~3e-15`), `SE` is ~0, and `separation.json` records
   `z ≈ 3e16` and `floor = 0.0`. Those two fields are a division by rounding
   noise and should be read as "exactly determined". The verdict (DEPARTURE) and
   the value (`21.000000000000` etc.) are correct. Fixing the reporting requires
   re-running the reductions, which would take me from 1032 to ~2064 core-seconds
   against a 1500 core-second authorization. **I did not overrun the budget to
   improve a cosmetic field.** One-line fix for a successor: flag `SE == 0` as
   degenerate rather than dividing.
8. **I did not establish why the residual is larger at `d = 140` than `d = 100`.**
   The red team's candidate — weakly reduced tails retaining partial `q`-vector
   structure — is consistent with the pattern here and is still a candidate, not
   a finding.

---

## 9. Reproduction and budget

```
AUTORESEARCH_EXTRA_PYTHONPATH=<dir containing fpylll 0.6.4, cysignals> \
OMP_NUM_THREADS=1 python3 predicate.py --workers 4
OMP_NUM_THREADS=1 python3 predicate.py --calibrate     # §7 only, writes nothing
```

`fpylll` is imported from `AUTORESEARCH_EXTRA_PYTHONPATH`; the committed script
hard-codes no machine-local path. `fpylll 0.6.4` / `numpy 2.4.6` / Python
3.11.15, matching the BATCH-436ddd run manifest for `fpylll`.

| | used | authorized |
|---|---|---|
| core-seconds | **1032.18** (1032.11 of it lattice reduction) | 1500 |
| wall seconds | **273.05** | 2400 |
| peak RSS | **0.089 GB** | 3 GB |
| error draws | **0** | — |

No timeout, no crash, no infrastructure failure. The whole measurement layer of
the incumbent is gone; what remains is the reduction, which `V` is computed
*from* and which cannot be avoided.

Artifacts: `predicate.py` (sha256 at time of writing
`89516a3071e4a206c4c959703a8c5c8d0a3a4199b1a2c21a3541266f929071ae`),
`separation.json`
(`d65e1590074d1ab2eab49d4c9c3e16b743df543ce076f11e6fed9c39e5668b6f`).
`predicate.py` was extended after the recorded run with the `--calibrate` entry
point of §7; it touches no frozen constant, no statistic and no verdict rule,
and `SPEC_SHA256` is unchanged at `c547573c…` as recorded in `separation.json`.

---

## 10. Scope

Every number in this report is measured at `d <= 140`, `beta <= 60`, `q = 3329`,
`k = d/2`, on `q`-ary bases from the committed seed family, under LLL and
BKZ-`beta` with `max_loops = 2`. No statement here concerns ML-KEM, any FIPS 203
parameter set, any attack cost, or any hypothesis status. I changed no research
status and promoted nothing to knowledge.
