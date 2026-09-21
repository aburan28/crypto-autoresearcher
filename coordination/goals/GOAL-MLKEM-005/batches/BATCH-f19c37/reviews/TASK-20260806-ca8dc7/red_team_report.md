# Red team — BATCH-f19c37 (AM-1 measurement, AM-2 predicate)

TASK-20260806-ca8dc7 / BATCH-f19c37 / GOAL-MLKEM-005
Governed by `ledger/decisions/DEC-20260806-00deff.yaml` (AM-1, AM-2).
Reviewed artifacts frozen under `archives/TASK-20260806-2e602d/snapshot-receipt.json`.

**Claim tier TOY.** Nothing in this report supports any statement about ML-KEM
security, about any FIPS 203 parameter set, or about any cost model. Every frame
I constructed is at `d <= 140`, `beta <= 60`, `q = 3329`, `k = d/2`. I change no
research status, dispose of no hypothesis, and promote nothing to knowledge.

I modified no producer artifact. Everything I wrote is in this directory.

---

## 0. The two verdicts I was asked for, stated first

**Verdict 1 — predicate generalization: THE DEFENCE DOES NOT HOLD, AND P3 MUST
NOT BE ADOPTED AS THE GOAL'S ADJUDICATOR IN ITS PRESENT FORM.**

The "μ₀ is a theorem" defence is *true* and I confirm it — the null calibration
transports exactly, and I verified it on frames the predicate never saw. It is
also **not the defence that was needed.** A correct null does not make a
statistic a valid adjudicator; it makes it a correctly-calibrated detector of
whatever it detects. What P3 detects is *the orientation of the tail GSO frame
relative to the standard coordinate axes*, and that quantity is **not a function
of the lattice**. On frames P3 was not built against I obtained, in 0.4 s of
numpy:

* **P3 returns its maximum possible DEPARTURE on `Z^d`** — the trivial lattice,
  in its identity basis. `V = beta(1 - beta/d)` is the *global maximum* of `V`
  over all rank-`beta` projectors, so no object can score higher. The producer's
  own out-of-sample "exact point prediction" anchor (`predicate_report.md` §6a,
  `V = 21.000000`) is this object. Its strongest verification and its worst
  null-object failure are the same computation.
* **The verdict changes under a row permutation of the same basis** — same
  lattice, same basis vectors as a set, `V` moves 9.35 → 21.00 → 12.81 at
  `(100,30)`.
* **The verdict inverts under an ambient isometry** — `B -> BH`, `H` orthogonal,
  which preserves every lattice invariant any lattice problem depends on
  (successive minima, determinant, GSO profile, SVP/CVP hardness). At `(100,30)`
  the identical lattice goes **DEPARTURE `z = +465.48` → ANOMALY_BELOW_NULL
  `z = −17.98`** (DCT isometry) → **AGREEMENT `z = −0.50`** (Haar isometry).
  P3 assigns three different verdicts, including its own "instrument fault"
  verdict, to one lattice.

So P3 generalizes *as calibrated* and fails *as construct*. Detail in §3.

**Verdict 2 — can the frozen G3 ever return PASS on a correct instrument?
NO. This is a defect of AM-1 and I state it plainly, as requested.**

On a perfect instrument — true mean curve exactly non-increasing, Gaussian
paired noise, the most favourable possible model for the gate — the frozen G3
returns, per cell:

| plateau steps in the grid | P(cell FAIL) | P(4-cell overall FAIL) | P(4-cell overall PASS) |
|---|---|---|---|
| 3 | 0.4397 | **0.9014** | **0.00025** |
| 4 | 0.5372 | **0.9541** | **0.000015** |

The AM-1 grid **guarantees** 3 plateau steps per cell — see §2.2, established
from the run's own exact `V` values, not from a model. **The frozen G3 fails a
correct instrument roughly 9 times in 10 and passes it roughly once in 4000.**
The INVALID headline of this batch is therefore uninformative about the
instrument: it is the modal outcome of the rule, not a finding about the
measurement. Detail in §2.

---

## 1. Integrity — clean, with one observation

All seven declared artifacts hash exactly to `archive.path_sha256` in
`archives/TASK-20260806-2e602d/snapshot-receipt.json`, and `prereg.md` hashes to
`cc7f3e19…` matching all four carriers the AM-1 report names. I re-ran
`sha256sum` independently; every value matches. The producers' provenance
statements — 32/32 reductions at deviation `0.0` against both prior batches, 24
shared points bitwise identical, `spec_sha256` emitted before any research number
— are internally consistent and I found no contradiction in them.

Two observations, neither fatal:

1. **`archive.commit_sha` is `null`** in the snapshot receipt. Under `CLAUDE.md`
   ("Archive receipts bind to CONTENT first") a content-verified archive is
   valid, and the content verifies. Recording it as content-verified rather than
   leaving the field null would make the receipt self-describing.
2. **The "24 shared points bitwise identical" check cannot fail** unless the code
   changed, because it is the same seeds through the same deterministic pipeline
   in the same environment. `report.md` §10.1 presents it as a reproduction
   check; it is a code-identity check. The prereg is scrupulous about exactly
   this distinction for N1/N2 ("an instrument check, not a control") and the same
   care should be applied here. It is not evidence about anything.

**Claim-leakage audit: PASS.** I grepped both reports, the prereg and both JSON
artifacts for `ML-KEM`, `FIPS`, `Kyber`, `606`, `1420`, `security`, `attack
cost`, `cost model`. Every hit is a negation or a scope boundary. No number is
transported. Both producers correctly refuse to interpret the real arms under
INVALID, and both correctly emit upper bounds rather than absences. The residual
leakage risk is not in wording and is recorded in §3.5.

---

## 2. Objection A (SEVERE) — the frozen G3 is a false-failure generator, and the executor's §7.5 objection is right but misdiagnosed

### 2.1 The mechanism

G3-FAIL fires when some step has `Delta_i > 1.0 * SE_step(i)`. For a step whose
**true** value is zero, `Delta_i / SE_step(i)` is a one-sided `t` statistic on
7 degrees of freedom, and

```
P(t_7 > 1.0) = 0.175308        (exact, by quadrature; g3_floor.py)
```

This number **does not depend on how good the instrument is.** I simulated the
frozen rule with the true decreasing steps set to 2, 4 and 8 SE and the cell FAIL
probability was 0.4395 / 0.4393 / 0.4408 — identical to three digits. Spending
more draws does not help either: `P(t_ν > 1)` is 0.1753 at ν=7 and 0.1587 in the
`ν → ∞` limit. **A tolerance expressed as a fixed multiple of an estimated
standard error can never become lenient, because the thing it is a multiple of
shrinks exactly as fast as the precision improves.** That is the root cause. The
executor's §7.5 objection — "the paired `SE_step` and the gate's `SE_diff` are
not commensurable" — describes a true symptom but attributes it to a relation
between two thresholds. Fixing that relation would not fix this. The 1.0 factor
is the defect.

### 2.2 The grid guarantees the plateau — from the run's own exact numbers

This is not a modelling assumption. I applied the **batch's own AM-2 predicate**
to the **batch's own AM-1 graded frames** (`results.json:cells.*.frame_V`), at
the same `n = 8` and the same gate of 4.0:

| cell | `t=0.25` | `t=0.5` | `t=1.0` | (`t=0.1` for reference) |
|---|---|---|---|---|
| d100_b30 | z = +0.20 | +0.07 | +0.21 | +2.03 |
| d100_b40 | +0.98 | +0.29 | +0.03 | +4.18 |
| d140_b30 | −0.65 | −1.09 | −1.21 | +2.21 |
| d140_b40 | +0.23 | −0.20 | −0.44 | +2.91 |

**The last three grid points are certified indistinguishable from Haar in every
cell by the batch's own predicate**, and `t = 0.1` is too in three cells of four.
So `m(t)` is genuinely flat over `t ∈ {0.1, 0.25, 0.5, 1.0}` — at least 3 truly
null steps per cell, 4 in three cells. AM-1 retained those points deliberately,
for cross-run comparability, and then imposed on them a per-step ordering test
they cannot survive. The two design choices are individually reasonable and
jointly incoherent.

### 2.3 Both INVALID-producing FAILs are inside that region

| cell | FAIL step | `V` excess at the two endpoints (z vs μ₀) | reading |
|---|---|---|---|
| d140_b40 | `0.5 → 1.0` | **−0.003994 (z = −0.20)** and **−0.008087 (z = −0.44)** | Both endpoints sit **below** the exact Haar expectation. There is **no true ordering to violate.** This FAIL is a pure false positive. |
| d100_b30 | `0.05 → 0.1` | +0.2488 (z = +6.86) and +0.0522 (z = +2.03) | A real `V` step of 0.197 — but the cell's own measured floor bracket is `V ∈ [1.8015, 2.6146]`, so the step is **9.2× below the lower end of the floor** of the very instrument G3 is scoring. |

The executor reported that neither endpoint of either FAIL clears its gate. It is
worse than that: at d140_b40 the frozen rule declared a strict ordering violation
between two frames that are, by the batch's own exact deterministic statistic,
**both indistinguishable from the Haar null and both below its mean.**

### 2.4 The multiplicity nobody applied

G3 is 12 one-sided tests per cell at a nominal per-test level of 0.175, and the
overall verdict is defined as the **max over 4 cells** — a max over 48 tests. The
prereg declines multiplicity correction explicitly (§3.2), correctly for the
`4.0 SE` gate, but that declaration was carried into a rule where it is the whole
problem.

### 2.5 The "more severe of two readings" clause

The clause was written to stop permissiveness being bought by choosing an SE
convention. In the event the paired reading exceeded the unpaired one in **9 of
9** increasing steps, so "more severe" reduces to "always paired". Severity and
sensitivity point the same way here, so the conservative-sounding clause is
operationally "always use the most sensitive SE", i.e. always maximize the false
failure rate. The prereg's stated worry — that AM-1 *loosens* G3 — was pointed
the wrong way. AM-1 did not loosen G3 enough to reach a correct instrument's
operating point; it moved per-cell FAIL from ~1 to ~0.5.

### 2.6 Forward guidance (three options, costed)

Measured on a perfect instrument (`g3_repair.py`), tolerance `k × SE_step`:

| k | cell FAIL (3 plateau) | overall FAIL | cell FAIL (4 plateau) | overall FAIL |
|---|---|---|---|---|
| 1.0 (frozen) | 0.4388 | 0.9008 | 0.5368 | 0.9540 |
| 2.0 | 0.1232 | 0.4090 | 0.1591 | 0.4999 |
| 3.0 | 0.0291 | 0.1113 | 0.0388 | 0.1463 |
| **3.5** | 0.0157 | **0.0612** | 0.0203 | **0.0787** |
| 4.0 | 0.0079 | 0.0311 | 0.0101 | 0.0397 |

1. **Raise the tolerance to `>= 3.5 x SE_step`** — the cheapest change, zero new
   compute, restores an overall false-failure rate near 5–8%. Note this makes the
   tolerance numerically equal to the gate's own `4.0`, which is the coherence
   the executor asked for, arrived at from the operating characteristic rather
   than by analogy.
2. **Score a step only if at least one endpoint clears its gate.** Both of this
   batch's FAILs report "no" for both endpoints, so this alone would have
   returned PARTIAL. It is the direct expression of "sub-floor differences carry
   no information", which the prereg already asserts in §5 for absences and does
   not carry into G3.
3. **Replace 12 independent per-step tests with one global monotonicity
   statistic** (isotonic-regression or Jonckheere-type) over the whole path, with
   a null calibrated by permutation of the `t` labels within a draw. This is the
   statistically correct object and costs no new lattice work — the paths are
   already recorded per draw in `results.json`.

**Whichever is chosen, this batch's INVALID must not be recorded as an instrument
failure.** It is a rule failure, and recording it otherwise would put a false
negative about the instrument into the ledger.

---

## 3. Objection B (SEVERE) — P3 does not generalize as an adjudicator

Environment note, stated up front: `fpylll` is not installed in this session, so
I could not regenerate the committed bases. **This is not a limitation for the
question asked** — the question is whether the predicate generalizes to frames it
was not built against, and I therefore constructed my own q-ary bases, my own
seeds, and my own frames. Statistic and verdict rule are copied verbatim from
`predicate.py`. Script: `p3_attack.py`; output `p3_attack.out`.

### 3.1 The unreduced-arm DEPARTURE is a constant of the construction, not a measurement

Independently generated q-ary bases (`[[I_k, A],[0, q I_{d-k}]]`, `A` uniform
mod `q`, my own RNG), `n = 8`, against the committed values:

| cell | committed `V` (unreduced) | my independent `V` | agreement |
|---|---|---|---|
| (100,30) | 9.362794 ± 0.080704 | 9.29472 ± 0.08392 | 0.73 % |
| (140,30) | 6.750435 ± 0.052182 | 6.73988 ± 0.04472 | 0.16 % |
| (100,40) | 16.244628 ± 0.048314 | 16.26475 ± 0.05320 | 0.12 % |
| (140,40) | 11.807462 ± 0.055124 | 11.77714 ± 0.06059 | 0.26 % |

Between-instance dispersion is under 1 % of the value in every cell, in both the
committed data and mine. **`V` on the unreduced arm is a deterministic function
of `(d, k, beta, q)` and the canonical row form. It carries essentially no
information about the instance.** Every `+250` to `+587 SE` separation in
`predicate_report.md` §0 is a measurement of the q-ary *construction*, obtainable
in closed form without reducing a single lattice.

### 3.2 Null object 1 — `Z^d`

| cell | `V` of the identity basis of `Z^d` | `beta(1-beta/d)` | μ₀ | P3 verdict |
|---|---|---|---|---|
| (100,30) | 21.0000000000 | 21.0000000000 | 0.411765 | DEPARTURE, `z = +inf` |
| (100,40) | 24.0000000000 | 24.0000000000 | 0.470588 | DEPARTURE, `z = +inf` |
| (140,30) | 23.5714285714 | 23.5714285714 | 0.331992 | DEPARTURE, `z = +inf` |
| (140,40) | 28.5714285714 | 28.5714285714 | 0.402414 | DEPARTURE, `z = +inf` |

Since `sum_a P_aa^2 <= sum_a P_aa = beta` with equality iff every `P_aa ∈ {0,1}`,
`V <= beta - beta^2/d = beta(1-beta/d)` for **every** rank-`beta` projector. So
`Z^d` in its natural basis attains the **global maximum of the statistic**. The
predicate's most confident possible finding is delivered by the object with the
least possible content. `docs/inventor-protocol.md` "controls before belief"
requires the identical measurement against a null object of the same shape before
a signal is believed; this null object was available for free and was not run.

### 3.3 Null object 2 — the same lattice, reordered and re-oriented

Row permutation (unimodular; same lattice, same basis vectors as a set):

| cell | canonical order | rows reversed | rows randomly permuted |
|---|---|---|---|
| (100,30) | `V = 9.34942`, z = +351.97 | `V = 21.00000`, z = +inf | `V = 12.81364`, z = +51.18 |
| (140,30) | `V = 6.75483`, z = +339.37 | `V = 23.57143`, z = +inf | `V = 12.47839`, z = +42.32 |

Ambient isometry `B -> BH` (`H` orthogonal — preserves successive minima,
determinant, GSO profile, and the hardness of every lattice problem):

| cell | identity | DCT isometry | Haar isometry |
|---|---|---|---|
| (100,30) | 9.32031, z = +465.48, **DEPARTURE** | 0.27314, z = **−17.98**, **ANOMALY_BELOW_NULL** | 0.40331, z = −0.50, **AGREEMENT** |
| (140,30) | 6.75532, z = +286.08, **DEPARTURE** | 0.37817, z = +4.66, **DEPARTURE** | 0.31983, z = −1.19, **AGREEMENT** |

Three verdicts, one lattice. The DCT row is the sharpest: an isometric copy is
classified as `ANOMALY_BELOW_NULL`, which the spec defines as **"an instrument
fault, not a finding"**. A predicate that calls a rigid rotation of its own input
an instrument fault cannot adjudicate a research hypothesis about that input.

`predicate_report.md` §8.1 states "`V` is a property of a basis *presentation*,
not of a lattice". That concession is correct and it is **fatal to the adjudicator
role**, not a caveat on it — but it is filed under "what I could not establish"
while §0 leads with "A predicate exists, and it separates."

### 3.4 The "nothing to overfit against" argument fails on its own terms

`predicate_report.md` §2.1(b) is the load-bearing defence: at second order there
is exactly one signed-permutation invariant of `P` modulo `trace(P) = beta` and
`trace(P^2) = beta`, so there was no candidate set to search. **The algebra is
correct** — I checked it, and the affine identity
`sum_{a≠b} P_ab^2 = beta − beta^2/d − V` holds. The argument still fails twice:

1. **The invariance premise is imported from an instrument P3 replaces.** The
   restriction to signed-permutation invariants is derived from the *error law*
   being iid and sign-symmetric. **P3 draws zero error vectors.** With no error
   law in the statistic there is no reason to restrict the candidate set to
   invariants of that law's symmetry group. The uniqueness theorem is inherited
   from `T2`'s setting and does not bind `P3`.
2. **The actual object is not coordinate-exchangeable.** A q-ary lattice at
   `k = d/2` has a distinguished coordinate block. Under the true symmetry group
   — signed permutations *within* each block — the **degree-1** statistic

   ```
   W = sum_{a <= k} P_aa  −  beta * k / d
   ```

   is admissible, is not constant, and is not a function of `V`. Measured on my
   independently generated unreduced arms:

   | cell | `W` | Haar null sd of `W` | significance |
   |---|---|---|---|
   | (100,30) | **+15.00000** | 0.30540 | **+49.1 null-sd** |
   | (140,30) | **+15.00000** | 0.30834 | **+48.6 null-sd** |

   `W = beta/2` exactly in both cases, because `sum_{a<=k} P_aa = beta` — the
   unreduced tail frame lies **entirely inside the first `k` coordinates**. A
   first-order statistic fires at 49 null-sd on precisely the arms `V` fires on.
   The candidate set is not a singleton, and the object being detected is the
   `k`-block structure, which is known a priori from the construction.

### 3.5 AM-2's admissibility criterion is the mirror image of the G3 defect

AM-2 requires "different verdicts on the Haar null arm and the real arm in at
least one cell". **That criterion contains no null-object requirement** — nothing
obliges a candidate predicate to *fail* to separate on an object with no signal.
It is therefore passable a priori by any statistic that detects "this basis came
from a q-ary construction and was not fully randomized", which is true by
construction and needs no experiment. §3.1–3.3 show P3 is such a statistic.

So the two amendments carry symmetric defects, and I state both plainly since I
was asked to:

* **G3 as frozen cannot pass a correct instrument** (~1 in 4000).
* **AM-2 as frozen cannot fail an incorrect predicate**, because it asks only for
  separation and never for non-separation on a null.

The minimal repair to AM-2 is one added clause: *a candidate predicate must
return AGREEMENT on a declared null-object set of the same shape.* I have supplied
three ready-made null objects (`Z^d`; row-permuted presentations; ambient
isometries) that cost seconds and that P3 fails. The **claim-leakage risk in this
batch is here** — not in wording, but in a predicate accepted on plausibility
becoming the goal's adjudicator, which is exactly the pattern the producer itself
names when it writes that CTRL-BS, CTRL-POSHOM and CTRL-IDXMAP "were each accepted
without answering" this question. This would be the fourth.

### 3.6 What survives, and it is not nothing

* `μ₀ = 2β(d−β)/(d(d+2))` **is** a theorem and **does** transport. My Haar-isometry
  arms return `z = −0.50` and `−1.19`, and the producer's own 4000-frame
  calibration at eight `(d,β)` is consistent. No calibration overfit exists.
* The producer's self-reported §7 near-miss (`z = +3.98` on a null arm) and the
  measured false-positive rate of **0.145 %–0.295 %** against a nominal
  `3e-5` — a factor ≈ 60 — is a genuine and well-handled disclosure. It should be
  carried into any successor: the named `sd_0(d,β)/sqrt(n)` exact-SE fix removes
  it and costs no lattice work.
* `V` is a legitimate, free, exact **diagnostic** of coordinate alignment and is
  strictly better than `T2` at that job. Nothing above argues against using it as
  a diagnostic. It argues against `verdict(V)` adjudicating a hypothesis.

---

## 4. Objection C (SEVERE, new result) — F-A1's admissible content is falsified by a matched-`V` control

### 4.1 F-A1 on the NOVEL subset is near-tautological

F-A1's stated content is "`D` depends on the frame only through `V`, and
increases with `V`". The NOVEL subset is, by the prereg's own §6.2 definition,
**graded-path points only** — `t ∈ {0.0025, 0.0075, 0.015, 0.03}` in four cells
plus `{0.005, 0.01, 0.02}` in three. It contains **zero cross-family pairs.**
Along the graded path `V(t)` and `D(t)` are both monotone decreasing in `t`
(d100_b30 clearing points: `V` = 21.00, 12.95, 8.47, 5.88, 4.30, 2.61; `D` =
0.0968, 0.0589, 0.0384, 0.0261, 0.0190, 0.0098). Two quantities that are each
monotone in the same parameter are automatically co-monotone, so "zero violating
pairs" is forced by the construction. **The admissible F-A1 result is a
monotonicity check on one monotone path, not a test of "`V` alone".** The one
genuinely informative comparison in the report — unreduced (`V = 9.3628`) against
graded `t = 0.005` (`V = 8.4735`), 0.308 SE apart — is a *cross-family* pair, and
the report's own novelty rule excludes it from the admissible subset.

### 4.2 The test that was missing, run here

`l2_vmatch.py`: a second frame family, **exactly matched in `V`**, with a
two-level diagonal profile instead of the graded family's spread profile. Rank-β
projector supported on `2β` coordinates with `P_aa ∈ {u, 1−u}`, `u` solved in
closed form so `V` matches the graded arm to floating point. My own frames, my
own seeds, my own `2^20` CBD_{η=2} draws, `d = 100`, `β = 30`, `n = 8`, prereg
estimator (`sort(R)[1023]`). `D` is reported as `q_emp − q_emp(haar)`, i.e. the
prereg's `D` up to the common positive factor `q_Beta(2^-10)`, which cancels in
every comparison below.

| `V` (both arms, exact) | 3rd diagonal moment: graded / paired | `D_graded` | `D_paired` | ratio | difference |
|---|---|---|---|---|---|
| **8.6334** | +2.2066 / +0.9801 | +0.00471292 | +0.00438771 | 0.931 | **−1.91 SE** |
| **6.0526** | +1.2859 / −0.5684 | +0.00325919 | +0.00260491 | 0.799 | **−3.45 SE** |
| 6.0526 / 6.0000 (family floor, near-matched) | +0.8049 / −0.6000 | +0.00228709 (V=4.4656) | +0.00255881 | — | consistent |

**At exactly equal `V`, `D` differs by 7 % and 20 %, the second at 3.45 SE.**
`D` is therefore **not** a function of `V` alone. The direction tracks the third
diagonal moment `sum_a (P_aa − β/d)^3`, which is what one expects: the identity
`Var(e^T P e) = 2β + (μ₄−3)(V + β²/d)` makes the *variance* a function of `V`
alone — L2's derivation is correct at second order — but `D` is a `2^-10` **tail
quantile**, whose third cumulant involves `sum_a P_aa^3` independently of `V`.

This matters because the prereg declared F-A1 "the falsifier that counts",
explicitly *L2's content stripped of its magnitude map* and therefore immune to
the map's known `1.0–1.7×` defect. **It is not immune.** The mechanism claim
fails at the tail the design measures at, and the frozen F-A1 could not see it
because an ordering test is blind to a level offset that preserves order.

I am careful about what this is: a red-team probe on my own frames, not
pre-registered, at TOY tier, `d = 100`, `β = 30` only. It does not overturn the
recorded CONSISTENT verdict, which was computed correctly under the frozen rule.
It shows the frozen rule tested a weaker proposition than the one it named, and
it hands a successor a cheap, ready falsifier.

### 4.3 F-A2's band

`rho ∈ [0.89, 1.10]` measured against a declared band of `[0.5, 2.0]`. The
executor correctly calls this a weak test passed widely. Worth adding for a
successor: the *observed* tightness is itself informative — `rho` cancels a
constant multiplicative bias exactly, and F-A3 shows the bias is a stable
1.2–1.7×, so `rho ≈ 1` says the bias is near-constant in `V` within a cell. The
frozen scoring discards that. A successor should pre-register the band at the
achieved precision.

---

## 5. Objection D — "F-B falsified both laws" is correct bookkeeping and the wrong reading

**The observable is the defect, not the two laws.** Three reasons, in order of
force:

1. **At `d = 100` the ratio straddles a structural fold.** `k = 50`, and the
   trend runs to `β = 60 > k`. The run's own exact `V` for the unreduced arm goes
   `V(50) = 24.995 → V(60) = 16.269` — it *falls* — and `D` follows,
   `+0.078555 → +0.048091`. The report names the cause correctly (the tail window
   is forced out of the `k`-block). A decay law is a statement about a
   monotone regime; `D(60)/D(30)` at `d = 100` is a ratio across a phase change
   in the object. **No law of either kind is defined across that fold**, so
   falsifying two of them there is not informative about either. At `d = 140`
   (`k = 70 > 60`) no fold occurs, and there the honest reading is that L1 misses
   by 247 % and L2 by 36 % against a ±25 % band — a distinction the
   band-membership rule discards by design.

2. **The only scorable arm is the one whose `V` is a constant of the
   construction.** `lll_only` and `real_bkz40` are NOT APPLICABLE at both `d`
   (their `D(30)` does not clear its gate), so F-B has exactly **one scorable arm
   per `d`, and it is `unreduced`.** By §3.1, that arm's `V` is a deterministic
   function of `(d, k, β, q)` with under 1 % instance variation. F-B's
   discriminating measurement is therefore a measurement of the q-ary
   construction, not of any reduction phenomenon. That is why both laws miss: they
   were frozen about lattice reduction and scored on a construction artifact.

3. **The `0.90` artifact tell is bound to the wrong parameter.** The inventor
   protocol's canonical tell is "a quantity that fails to decay when **the
   parameter meant to destroy it** increases". `β` is not that parameter — it is
   the width of the probe window, not a randomization strength. Widening the
   window into the same aligned `k`-block is *expected* to increase `D`, and
   indeed L2 predicts growth at `d = 140`. The parameters meant to destroy the
   departure in this design are `t` (graded) and reduction strength, and against
   both of those the quantity does decay, monotonically, exactly as a real signal
   should. The tell fires here because it was carried verbatim from the superseded
   prereg together with the wrong binding, not because an artifact was detected.

Net: `L1 FALSIFIED` is robust — it was genuinely pre-registered, it predicts decay,
and growth was measured at both `d`, on the fold-free `d = 140` row as well. `L2
FALSIFIED` is bookkeeping on a reproduction, on one non-lattice arm, half of it
across a fold; it should not be recorded at the same strength. And the right
record is that `D_A(60)/D_A(30)` at fixed reduction is not an admissible
observable for a decay law and should not be frozen about again. §4.2 supplies
the replacement: matched-`V` cross-family comparison, which tests the mechanism
directly and costs no lattice reduction beyond what already exists.

---

## 6. Cheapest falsification of each headline

| headline | cheapest falsification | cost |
|---|---|---|
| **AM-1: "the instrument is INVALID"** | Re-score G3 on a second `seed_graded` family, or simply jackknife the 8 recorded draws leave-one-out. The verdict is a ~50/50 coin per cell (§2); it will not replicate. The graded arms need **no lattice reduction at all** — they are pure numpy. | seconds |
| **AM-2: "a predicate exists and it separates"** | Run P3 on `Z^d`, on a row-permuted presentation, and on an ambient isometry. | 0.4 s — done, §3 |
| **F-A1: "L2 CONSISTENT on the NOVEL subset"** | One frame family matched in `V` with a different third diagonal moment. | 60 s — done, §4.2 |
| **F-B: "both laws falsified"** | Re-score `D(50)/D(30)` at `d = 100` (both endpoints `<= k`, no fold) from data already in `results.json`. | free, already recorded |
| **"the grid fix worked"** | I concur with this one and could not falsify it. The crossing lands inside the sampled range in all four cells and the 24 shared points are bitwise identical. It is the batch's soundest claim. | — |

---

## 7. What I could not check

1. **I could not regenerate the committed bases** — `fpylll` is not installed in
   this session and I did not install it. Every frame I computed is my own
   construction. This does not affect §2 (which reads only the run's own recorded
   numbers) or §3 (whose question *is* out-of-sample behaviour), and it means my
   §4.2 `D` values are not comparable in absolute terms to the run's — only
   within my own run, which is how I used them.
2. **`k != d/2`** remains untested, as both producers correctly say. It remains
   the largest single hole, and §3.4 now gives a second reason to want it: the
   `W` statistic isolates the `k`-block directly and would separate the two spill
   boundaries at first order.
3. **I did not attempt to falsify the notarization chain** beyond re-hashing all
   seven artifacts and the prereg. The `merge-base` ancestry claim is the
   validator's assignment (TASK-20260806-64089c) and I did not duplicate it.
4. **`Var(V)` has no closed form** (producer §8.4), so my `z` values in §3 rest on
   the same bootstrap null the producer measured. This does not affect the
   `z = +inf` / `z = +465` / `z = −17.98` conclusions, whose magnitudes are far
   outside any plausible correction.
5. **No statement here is about ML-KEM, any FIPS 203 parameter set, any attack
   cost, or any hypothesis status.**

## 8. Budget

No budget overrun. Total compute: about 3 minutes wall, single machine, numpy
only, peak RSS under 1.5 GB (the `2^20`-draw comparison in §4.2 dominates at
~1 GB). No timeout, no crash, no infrastructure failure. Nothing was left
unmeasured for budget reasons; the only capability limit was the absent `fpylll`,
recorded in §7.1 rather than worked around.

Artifacts in this directory: `red_team_report.md`, `g3_floor.py` / `.out`,
`g3_repair.py` / `.out`, `p3_attack.py` / `.out`, `l2_vmatch.py` / `.out`,
`l2_vmatch_qemp.json`. All scripts are deterministic under their recorded seeds.
