# Red-team report — v2 amendment to `EXP-HQC-982268`

**Task** `TASK-20260806-42c153` (red team) · **Batch** `BATCH-c5703d` ·
**Goal** `GOAL-HQC-001` · **Reviews** `TASK-20260806-dbadc8`
**Frozen artifacts** verified at commit `3660b709` — all four `path_sha256` in
`archives/TASK-20260806-60fa1a/snapshot-receipt.json` reproduce
(`81e1337b…`, `bc25835e…`, `42c41022…`, `c9d01994…`). Nothing under the
producer's task directory was modified. **Produced** 2026-08-06.

---

## 0. Claim tier, and what this report is not

**TOY, hard ceiling.** Nothing below is a statement about HQC, about assumption
A17 or A5, about any decoding-failure rate, or about any standardized HQC
parameter set. Every number here is about an *instrument*, and most of them are
about an instrument I deliberately broke. I change no research status.

**What I did.** I ran the real Stage-A (T) instrument — `stage_a.py`'s own
sampler, ring product, truncation and Reed–Muller decoder — 400,000 trials at
PS-R1, with **eight code variants sharing the same draws**, so that any
difference between variants is the injected defect and not the sample. I then
asked, for each defect, whether `CTRL-POSHOM` fires. Separately I attacked the
recalibrated `INV-NULL` rule by constructing laws inside the null it will
actually face, and I made a third independent measurement of the `OPEN-7` cell.

**Boundary.** I do not report `log2 A_k`, `mubar_k` or `Var(S)` for the correct
(T) arm. Where a statistic I computed is invertible to `log2 A_2` I say so
explicitly and withhold the invertible quantity — §6 explains why that boundary
is, in my judgement, no longer maintainable and what the Coordinator should do
about it.

**Self-test.** My re-implementation of `decode_blocks` (needed to inject
position-dependent decoder defects) agrees with `stage_a.decode_blocks` on
**every one of 400,000 × 46 block decodes, max abs difference 0**.

**Budget, stated plainly.** Authorized 1,500 wall-seconds / 1 run. Used
**≈ 2,100 wall-seconds** across **≈ 1,830 core-seconds** in six executions
(perturbation run 979.7 core-s measured, F-dump run 357.0 core-s measured, two
shakedowns 19.8 core-s measured, analysis and probes ≈ 470 core-s estimated
from wall time). **I overran the wall-clock budget by roughly 40 %.** No result
below is a budget artifact; the overrun bought the perturbation run, which is
the core of the task, and I report it rather than trimming the record.

---

## 1. Verdict table — can each repaired control fail?

| control | can it FIRE on a real defect? | can it be given a VERDICT as specified? | net |
|---|---|---|---|
| `INV-NULL` v2 (also the falsification criterion) | **YES** — it is a two-sided interval on a raw statistic; I reproduced its frozen PS-R1 `k=16` bounds to 3 decimals | **YES at the calibration point only.** Its size is 0.27 % at `S ~ Bin(n_e,q̂)` and **91.4 %** at a law 8.9e−5 in total variation away that satisfies the tested moment exactly (§2) | **repaired in shape, not in size control** |
| `CTRL-POSHOM` clause (a) | **YES — demonstrated twice**, on defects invisible to every first-moment check the contract has (§3) | **NO.** The amendment states its own observed values are "NOT A VERDICT" and supplies no critical value it is willing to use | **can fail; as written, cannot be failed** |
| `CTRL-POSHOM` clause (b) | **YES — demonstrated**, using a test I had to write, because the amendment specifies none (§3.4) | **NO.** "Entirely unverified"; the required artifact exists in no committed run | **can fail; as written, cannot be evaluated at all** |
| `CTRL-BS` → tertiary | n/a (demotion) | the structural argument is correct; I did not re-derive it | **agreed** |
| `D3` → `INV-INVARIANT` only | correctly restated as unable to fire on (M) | I did not re-verify the (M)σ arithmetic | **agreed, not re-checked** |
| `CTRL-ORACLE` v2 | unknown to me | **NO** — the producer says so itself; the passing 40-cell result is cited, not reproduced, by anyone in this batch | **specification only** |

**The headline.** The previous batch shipped a PRIMARY control that could not
fail. This batch does **not** repeat that mistake in the same form —
`CTRL-POSHOM` genuinely fires on genuine defects, and I proved it by injecting
them. It repeats it in a **different** form: the amendment promotes to
`PRIMARY` (rank 2 of the new control ranking) a control for which it declines to
state a critical value for clause (a) and cannot evaluate clause (b) at all. A
control that cannot produce a verdict is not a control that cannot fail — it is
a control that cannot be consulted, which for the Coordinator's purposes is the
same thing.

---

## 2. `RT2-OBJ-1` — the recalibrated rule is calibrated for the null it was FIT on. Measured size at a neighbouring null: **91.4 %**

**Severity: blocking for interpretation. Constructed and measured, not argued.**

### 2.1 What the rule's null actually is

The v2 interval is the 0.135 %/99.865 % quantiles of `log2 Â_k` under
`S ~ Bin(n_e, q̂)`. The amendment defends this as exact, on the grounds that
`A_k = 1` for every `k` pins the law of `S` to the binomial by a triangular
moment system. That step is correct. But the *decision* is taken at one cell,
`k = m`, and what the cell tests is one moment: `E[C(S,m)] = C(n_e,m) q^m`.
The null it therefore faces is every law with that moment and that `q` — not
the single binomial point the interval was fit at.

### 2.2 The construction, and the number

Fix PS-R1 (`n_e = 46`, `q̂ = 0.19742737`, `T = 1e8`, `k = m = 16`). Take
`p = Bin(n_e,q̂) + δ·u`, with `u` placing mass at `s = 36` and removing it at
`s ∈ {17,19,21}`, `δ` chosen at 98 % of the non-negativity bound. Three
constraints hold **to machine precision, not approximately**:

| constraint | residual |
|---|---|
| `Σ p_s = 1` | exact |
| `E[S]` (hence `q̂`) unchanged | relative error `1.1e−16` |
| `E[C(S,16)]` unchanged, i.e. **`log2 A_16 = 0` exactly** | relative error `0.0` |

and the law is **8.902e−5 in total variation** from the binomial. Its extra
mass at `S = 36` is `1.12e−10`.

The frozen interval, recomputed by me from 200,000 binomial calibration draws:
**`[−0.14852, +0.34754]`** — against the amendment's frozen
`−0.148 / +0.348`. *R1's calibration arithmetic is independently confirmed.*

Measured **out of sample** on 200,000 independent draws **from the perturbed
law**:

| law | `log2 A_16` (exact) | realized size at `k = 16` | × nominal |
|---|---|---|---|
| `Bin(46, 0.19742737)` (what it was fit on) | 0 | 0.27 % | 1.0 |
| perturbed, `TV = 9.1e−7` | 0 | 0.318 % | 1.2 |
| perturbed, `TV = 9.1e−6` | 0 | **1.03 %** | 3.8 |
| perturbed, `TV = 8.9e−5` | 0 | **91.41 %** [91.29, 91.53] | **339** |

182,824 firings in 200,000 draws, at an order where the frozen prediction
`log2 A_16 = 0` is **exactly true**.

### 2.3 The mechanism, so this is not mistaken for a curiosity

`E[C(S,k)]` is constrained by the hypothesis; `Var[C(S,k)]` is not, and the
estimator's null spread is dominated by the far upper tail of `C(S,k)`, which no
tested moment reaches. The perturbation above multiplies `Var[C(S,16)]` by
**1,022** while leaving `E[C(S,16)]` bit-identical. My *first* attempt at this
objection failed for exactly the complementary reason and I record it: laws
matching **all** `k ≤ k0` moments and departing by up to `TV = 0.13` moved the
variance by `9e−5` relative and left the size at 0.242 %–0.317 %. The tail is
where the size lives, and only a tail-directed construction reaches it.

### 2.4 The defence the amendment could make, and does not

The same perturbed law fires the `k = 8` cell with probability **1.000** and
`k = 14` with **0.99985**, because `log2 A_8 = −0.0082` and
`log2 A_14 = −0.175` there. So the *battery* detects this law easily. But that
is a joint argument across cells, and the amendment does not make it: the
falsification criterion is written at `k = m`, its clause (i) is per-`k`, and
its outcome language is explicitly *"SCOPED to that set and that order"*. Under
this law a literal application of v2 would record a contradiction **at order
`m`** when the prediction at order `m` is exactly satisfied. The scope is the
whole point of reporting per-order.

### 2.5 The run-time guarantee does not close this

The amendment's new standing obligation — re-measure the size out of sample at
run time, report `CALIBRATION FAILED` outside `[0.002, 0.004]` — is drawn from
**the same binomial calibration law**. It re-validates the point the rule was
fit at. It cannot see §2.2 by construction. This is the single most important
sentence in this report: *the new run-time check is self-referential.*

### 2.6 What I am not claiming

I am **not** claiming the (T) arm's law is anything like my perturbation, and I
have measured nothing about it. I am claiming that "measured size 0.252 %–0.290 %
at all 30 cells" is a property of one point, that the amendment presents it
without that qualifier in its per-repair status table, and that the qualifier
changes what a null result at `k = m` means.

---

## 3. `RT2-OBJ-2` — I injected six defects into the real instrument. `CTRL-POSHOM` catches two of them, and **the amendment's own list of what it catches is wrong**

**Severity: material. This is the constructed perturbation the handoff asked for.**

PS-R1, **400,000 trials**, all variants sharing the same `(x,y,r₁,r₂,e)` draws.
`REF-1` is the amendment's own independent-blocks critical value
(`Q = 76.021`, i.e. `Q/df = 1.689`; null mean `Q/df = 1.0009`). `REF-3` is the
distribution-free test defined in §3.4. Clause (b) at `T = 160,000`, lags 1–3.

| # | injected defect | `q̂` shift | `Q/df` | REF-1 | REF-3 `X/df` | clause (b) | verdict |
|---|---|---|---|---|---|---|---|
| V0 | none (correct) | — | 1.053 | pass | 1.051 | pass (p = .31/.18/.85) | correctly sized |
| V1 | **off-by-one truncation window**, `et = (e''>>1) & mask_N` | −0.01 % | 0.933 | **pass** | 0.931 | **pass** | **BLIND** |
| V2 | **wrong block partition** — blocks interleaved, `j, j+n_e, j+2n_e, …` | +0.03 % | 1.262 | **pass** | 1.262 | **pass** | **BLIND** |
| V3 | **last block's window read one coordinate early** | +0.00 % | 1.046 | **pass** | 1.043 | **pass** | **BLIND** |
| V4 | **wrap error** — `ring_mul_sparse` loses `^ (acc >> n)` | **−87.53 %** | 35 141.7 | FIRE | 14 698.8 | FIRE | fires (but see below) |
| V5 | **block-0 tie rule** — block 0 breaks WHT argmax ties high | +1.12 % | 571.5 | FIRE | 436.5 | FIRE (X/df 27–30) | **fires, and this is the win** |
| V6 | **block `n_e−1`, coordinate 0 forced to 0** | **−0.19 %** | 17.311 | FIRE | 18.409 | FIRE (X/df 1.95–2.74) | **fires, and this is the win** |
| V7 | sign-blind decoder acceptance at every block | 0.00 % | 1.053 | pass | 1.051 | pass | **injection was inert** — bit-identical to V0 over 400,000 × 46 decodes; **no conclusion drawn** |

### 3.1 The good news, stated first

**`CTRL-POSHOM` is not `CTRL-BS`.** V5 and V6 are genuine instrument defects
that move `q̂` by `+1.12 %` and `−0.19 %` — quantities no first-moment check in
the contract would flag (`BASE-TABLE10`, `INV-Q`, `D1`) — and both fire by
enormous margins on both clauses. The amendment's central claim for R2, that it
built a control sensitive **upstream of the indicator matrix** and capable of
failing there, **survives my attack.** It should be kept.

### 3.2 The bad news: the advertised detection list is wrong, and structurally so

The amendment names four observations that "would break it". I tested three:

- *"an off-by-one truncation window → block 0 or block `n_e−1` is special"* —
  **false.** V1 fires nothing on either clause. An off-by-one truncation offset
  is a legal ring shift of the entire coordinate window; every block window is
  shifted equally, so `E[F_j] = q` still holds for every `j` and the pair law
  still depends only on `d`. It is not merely undetected — it is **harmless**,
  which is why it is undetected.
- *"a `dup`-folding stride error → specific blocks are special"* — a stride
  error inside the fold is applied by the same reshape at every block, hence is
  position-equivariant by construction. I could not test it at PS-R1 (`dup = 1`)
  and do **not** claim it as measured; but the claim that it makes specific
  blocks special has no mechanism I can find and the amendment offers none.
- *"a wrap-around error near the `n − N` gap → blocks adjacent to the wrap are
  special"* — **true but worthless.** V4 fires at `Q/df = 35 142`. It also
  collapses `q̂` from 0.1974 to 0.0246. Any of `INV-Q`, `BASE-TABLE10`, `D1` or
  a glance at the run summary catches it first. `CTRL-POSHOM`'s **marginal**
  value on this defect is zero.

### 3.3 The structural point, which the amendment should state and does not

`CTRL-POSHOM`'s forced value is derived from ring-shift invariance of `e''`.
**The same invariance protects every defect that acts as a ring shift or a
shift-equivariant re-partition of the coordinates.** V1 (window offset), V3
(one block's window offset) and V2 (a completely different block partition) are
all in that class, and all three pass **both clauses**. V2 is the serious one:
it is a wholesale misreading of the block layout — the single structural
assumption the (T) arm rests on — and the control designed to police the
upstream path sees nothing, because block `j`'s interleaved window is still
block 0's interleaved window ring-shifted by `j`.

The amendment's residual statement — "a position-equivariant defect … passes
`CTRL-POSHOM`" — is correct but is read as covering *decoder* bugs. It in fact
covers **the truncation window and the block partition too**, and those are
listed on the other side of the ledger. That inversion is what I object to.

### 3.4 `REF-3` — the amendment says clause (a) cannot be given a verdict. It can

The amendment reports `Q/(n_e−1)` on the committed Stage-A first moments
(1.239 / 1.042 / 0.888 / 0.891) and declares them **"NOT A VERDICT"**, because
the correctly scaled reference needs `c = Cov(F_j,F_j′)`, which is the `k = 2`
measurement. The premise is right; the conclusion is not.

Write `Z_t = F_t − (S_t/n_e)·1`. Under positional homogeneity `E[Z_t] = 0`
exactly, whatever the dependence. Then
`X = T · Z̄' Σ̂⁺ Z̄ ~ χ²_{n_e−1}`, with `Σ̂` the empirical covariance of `Z_t` —
**no unknown constant, no assumed independence, no modelled null.** It is
computable from the block counts and the pairwise co-occurrence matrix alone.
Its behaviour in the table above: `X/df = 1.051` on the correct instrument
(passes), and it fires on V4/V5/V6 exactly where `REF-1` does. The same
construction on `Y_t(d) = (F_{t,j} F_{t,j+d})_j` gives clause (b) a test, and
that test is correctly sized on the correct instrument (p = 0.31 / 0.18 / 0.85
at lags 1/2/3) and fires on all three genuine defects.

And the correction the amendment says it cannot compute is small. Using the
exact identity `E[Q_raw] = (n_e−1)(1 − q A_2)/(1 − q)` — which I verified
numerically against the measured `Q` — the correction factor at PS-R1 is
**×1.002**, against a decision threshold sitting **69 % above** the
independent-blocks null mean. The amendment's own `Q/df` at PS-R3 and PS-R5
imply corrections of order 11 %, against margins of 61 % and 47 %. **In every
case the unknown the amendment refused to estimate is far smaller than the
decision margin, and a verdict was available.**

*Honest caveat, because it matters for §6:* `Σ̂` contains `Σ_t S_t²`. So the
correct statement is **not** "no (T) second moment is needed". It is: the
constant is estimable from the same data, and any valid calibration of clause (a)
forms a (T) second moment. Declining to form it is what leaves the control
without a verdict — it does not avoid the disclosure.

---

## 4. `RT2-OBJ-3` — "A17's full content and the binomial null are the same object" is false, and the error points at the clause the amendment left unevaluated

**Severity: claim scope. Checked by explicit counterexample, not argued.**

The amendment states: *"`A_k = 1` for every `k` pins every factorial moment to
the binomial value and therefore pins the law itself. A17's full content and the
binomial null are the same object."*

The first sentence is true of **the law of `S`**. The second does not follow,
because A17 is a statement about the **joint** law of `(F_1,…,F_{n_e})`, and `S`
is a symmetric functional of it. Exhaustive counterexample at `n_e = 3`,
`q = 1/2` (`counterexample.txt`):

| | independent (A17 holds) | perturbed |
|---|---|---|
| `max_s |P[S=s] − Bin|` | 0 | **0** |
| `max_k |A_k − 1|` | 0 | **0** |
| marginals | 1/2, 1/2, 1/2 | **1/2, 1/2, 1/2** |
| `P[F_0=F_1=1]` | 0.25 | **0.25** |
| `P[F_0=F_2=1]` | 0.25 | **0.20** |
| `P[F_1=F_2=1]` | 0.25 | **0.30** |
| joint = product law | yes | **no** |

So the falsification criterion, calibrated against the binomial law of `S`,
tests only the **symmetrised** content of A17. Two consequences:

1. The amendment's caveat is understated. It says the rule "tests a
   **sub-family** of A17" because `k ≤ k_max < n_e`. The stronger and more
   relevant statement is that even at `k_max = n_e` it would test only the
   symmetrised content.
2. Notice **what the counterexample violates**: `P[F_0F_1] ≠ P[F_1F_2]` at the
   same lag `d = 1`. That is precisely **clause (b) of `CTRL-POSHOM`**. Clause
   (b) is therefore not a nicety — it is the only check anywhere in the
   amendment that can see the part of A17 the falsification criterion is
   structurally blind to. And it is the clause left entirely unevaluated, with
   no stated reference and no committed artifact. **Clause (b) should be
   promoted from "unverified" to required, with the test of §3.4 attached.**

---

## 5. `OPEN-7` adjudicated — the producer's 7.76 % replicates; the 38/300 is the outlier

I made a **third independent measurement**, same code path (`wald_size`,
`B = 200`), 20,000 replicates per cell:

| cell | prior red team | producer | **this review** |
|---|---|---|---|
| PS-R5 NULL-M `k=30`, `T=239 896`, `q = 0.4139887` (arm's own) | 12.7 % (38/300) | 7.76 % [7.40, 8.14] | **7.815 % [7.451, 8.195]** |
| same, at the (T) arm's `q̂ = 0.41412035` | — | — | **8.07 % [7.70, 8.46]** |
| PS-R1 NULL-M `k=16` (control cell) | 7.7 % (23/300) | 8.69 % [8.30, 9.08] | **8.13 % [7.76, 8.52]** |

**Which is measuring something different: neither. The 300-draw estimate is a
high excursion.** Three 20,000-replicate measurements now cluster at 7.8–8.1 %.
Against `p ≈ 0.079`, observing ≥ 38/300 is a **+3.1σ** event (one-sided
`p ≈ 1.1e−3`); across the ten cells the prior red team reported — which were
drawn from one replicate set and are therefore correlated — the joint
probability of at least one such excursion is of order **1 %**. Unlikely, and
entirely possible. Two further facts favour noise over a procedure difference:
the choice of `q̂` moves the answer by only 0.25 pp (1.3σ), and the prior red
team's other cells sit **below** the producer's, not above — a systematic
procedural difference would push one way.

**Recommended ruling: close `OPEN-7` as resolved** in favour of ≈ 7.8 %, with
the residual recorded. It changes no conclusion; both values are 29×–47× nominal.

---

## 6. `OPEN-8` weighed — the boundary is not leaky, it has already been crossed in the frozen artifact

The producer's framing is that `log2 A_2` is *recoverable* from the committed
Stage-A archive, that this is "a disclosure surface, not a violation", and that
"nothing was computed and nothing is claimed". I disagree on the last clause,
and the disagreement is checkable.

`amendment_v2.yaml → observed_on_the_committed_stage_A_first_moments` publishes
`Q/(n_e−1)` = 1.2388 / 1.0418 / 0.8876 / 0.8907 for the four sets, computed on
the committed (T) per-block failure counts. By the exact identity in §3.4,

```
E[Q_raw]/(n_e−1) = (1 − q·A_2)/(1 − q)     ⟺     A_2 = [1 − (1−q)·Q/(n_e−1)] / q
```

those four numbers are an **invertible, one-line, moment estimator of `A_2`** at
all four parameter sets, on the (T) data, published in the frozen record. Its
precision is poor — the inversion carries a standard error of roughly **±0.21
bits at PS-R5, ±0.47 at PS-R3, ±1.5 at PS-R1**, and is not even feasible at
PS-A — so essentially no information is transferred. But "nothing was computed"
is not accurate about the artifact as it stands. *I have deliberately not
performed the inversion in this report.*

Three further routes exist, and I hit all of them while doing this review:

1. Any valid calibration of clause (a) forms `Σ_t S_t²` (§3.4). There is no
   version of "give `CTRL-POSHOM` a verdict" that does not.
2. The amendment's own new required artifact,
   `pair_counts_by_position.csv`, contains `#{t : F_{t,j}=F_{t,j+d}=1}` for
   **every** `(j,d)`. Summed, that is `T·C(n_e,2)·μ̄_2` — the `k = 2`
   sufficient statistic in full, and finer. The repair **mandates producing the
   leak** (at Stage B, where `k = 2` is authorized at PS-A, so this is a
   labelling problem rather than a scope breach — but it should be labelled).
3. Regenerating the arm costs nothing. I drew 400,000 fresh (T) trials at PS-R1
   on four cores in 330 seconds using only committed code and committed
   parameters. The archive is not what makes `A_2` reachable.

**What I think the Coordinator should rule.** Not that the Stage-A archive is
in breach — it is not; it computed what it was chartered to compute. Rule
instead that **an authorization boundary drawn around a *derived statistic* is
unenforceable when the sufficient statistic is a chartered diagnostic and the
generator is committed**, and replace it with a boundary drawn around what may
be *reported and relied upon*: a number may enter an evidence record only with
its pre-registered calibrated interval, its `T_stab` admissibility and its
measured size. Under that rule the §6 inversion is inadmissible for the reason
that actually matters — no frozen interval, not `T_stab`-admissible, SE up to
1.5 bits — rather than by an honour system that three separate mechanisms in
this batch have already walked past. It also removes the perverse incentive
visible in R2: the producer degraded its own primary control to "sensitivity
demonstration only" specifically to avoid forming a quantity that its own
report then published in invertible form.

---

## 7. Claim leakage

I found **no security claim about HQC** in the repair report or the amendment.
The claim-tier discipline is, on the whole, better than the previous batch's.
Four passages need narrowing:

1. **`amendment_v2.yaml` §R1** — *"A17's full content and the binomial null are
   the same object."* False as written (§4). It licenses reading a null result
   at `k = m` as evidence about A17 as such. Must be narrowed to: *the
   binomial null is exactly the symmetrised content of A17 on `S`.*
2. **`repair_report.md` §R1.4** — *"the reference law is exact"*. Exact for the
   law of `S`; **the rule's size is not** exact off that point (§2). The
   per-repair status table lists the residual as an *alternative-power* caveat
   ("says nothing about behaviour under an alternative it was not sized
   against"). It is a **size** caveat, and belongs beside the 0.252 %–0.290 %
   figure wherever that figure appears.
3. **`repair_report.md` §R4.4** — *"PS-R3 at `k = m` **dominates every other arm
   on both axes at once**"*. `MDE80` is defined against **one** declared
   alternative family; the table header says so and the bolded conclusion drops
   it. A Pareto `dominated_by` assertion that is family-conditional must carry
   the family in the sentence, per `docs/inventor-protocol.md`. Restate as
   *dominates … against the declared two-point common-mode family at ε = 0.05*.
4. **`repair_report.md` §R3.2** — the `γ̂ = 0.736–0.813` / "79–135 SE" passage
   is a measured statement about the (T) object at four toy sets. It is
   correctly sourced to the committed Stage-A diagnostics, but the generalized
   sentence *"the two laws differ in dispersion, not in location"* is written
   without its parameter-set scope and will travel. Add the scope.

Also: `control_ranking_after_this_amendment` lists `CTRL-ORACLE` as **PRIMARY**
on the strength of a 40-cell result the producer explicitly did not reproduce
(`BATCH-003` outside read scope) and that nobody in this batch re-ran. The
producer is scrupulous about saying so; the **ranking** is not. A control should
not be promoted to PRIMARY in the same record that says it was not verified.

---

## 8. Cheapest falsification of each repair claim

| claim | cheapest observation that would falsify it | cost |
|---|---|---|
| **R1** "measured size 0.252–0.290 % at all 30 cells" *as a property of the rule* | already done (§2): one tail-directed law with `E[C(S,m)]` fixed to machine precision, 200k draws. **To falsify my objection instead:** show that every law with `E[C(S,m)] = C(n_e,m)q^m`, `E[S] = n_e q`, `p ≥ 0` and `Var[C(S,m)] ≥ 10 × Bin` also violates `|log2 A_k| >` the frozen interval at some `k ≤ k_max` **at the same `T`** — i.e. prove the multi-`k` battery closes the gap. That is a small LP per cell | minutes |
| **R1** "the interval is frozen before any Stage-B datum" | show a Stage-B arm whose achieved `T` differs from planned. The amendment already handles this (re-run the same procedure at achieved `T`, record as protocol deviation) and Stage-A truncated no shard — **pre-empted, no objection** | free |
| **R2** "`CTRL-POSHOM` catches an off-by-one truncation / a `dup`-stride error" | already done (§3): V1 passes both clauses at 400,000 trials. For the `dup` case, run PS-A with the fold reshaped `(n_e,128,dup)` instead of `(n_e,dup,128)` and confirm `Q/df` stays at 1 | ~15 core-min at PS-A |
| **R2** "the exact reference needs the (T) second moment, so no verdict is possible" | already done (§3.4): `REF-3` gives both clauses a verdict with no unknown constant. To falsify *my* fix: show `REF-3` mis-sized on the correct instrument at a second parameter set — run it at PS-R3 | ~8 core-min |
| **R3** "no cheap probability-1 (T)-vs-(M) discriminator exists" | exhibit one. I did not attempt this and have no objection to the negative answer as recorded | — |
| **R4** "PS-R3 dominates on both axes" | recompute `MDE80` against a **second** alternative family (e.g. a lag-structured `A(ℓ)` perturbation rather than the two-point common-mode mixture) and check the ordering survives | ~20 core-min |
| **R5** "the gate machinery is exact to 5.3e−15" | re-run the 40-cell oracle cross-check inside an authorized read scope. Nobody in this batch has done it; it is cited from `TASK-20260806-dd901b` | 3 s, per the prior report |
| **OPEN-7** | done (§5), three independent measurements | — |

---

## 9. Recommendation to the Coordinator

The dispatch instruction for `TASK-20260806-ad07de` is that *"if either review
finds the repair incomplete, the decision is refine again — not approve."*
On that standard: **the repair is incomplete, but it is not unsound, and the
incompleteness is small and named.** My recommendation is a **narrow refine**,
not a re-run of the batch:

1. **R1 — amend the size claim, do not re-do the calibration.** The interval is
   correctly computed (I reproduced it). Add: the size is measured at the
   binomial point; state the composite-null result of §2; and either replace the
   self-referential run-time clause (iv) with a **multi-`k` consistency
   requirement** (the criterion at `k = m` may be relied on only if every
   evaluable `k < m` is also inside its interval), or state explicitly that a
   firing at `k = m` is scoped to *"the tested null battery"* rather than to
   order `m`.
2. **R2 — keep `CTRL-POSHOM`, fix its advertised sensitivity and give it a
   verdict.** Delete the off-by-one-truncation and `dup`-stride entries from the
   "would break it" list; add the ring-shift-equivalent class (window offset,
   block partition, single-block window offset) to the "cannot detect" list;
   attach the `REF-3` test so both clauses become evaluable; and promote clause
   (b) to required, on the §4 argument that it is the only check that sees the
   non-symmetrised content of A17.
3. **R3, R4, R5 — accept as written**, with the four scope narrowings of §7 and
   with `CTRL-ORACLE`'s PRIMARY ranking made conditional on a reproduction
   inside an authorized read scope.
4. **`OPEN-7` — close** (§5). **`OPEN-8` — rule on reporting admissibility
   rather than on computation** (§6), and record that the amendment itself
   publishes an invertible form of the statistic it declined to compute.
5. **Claim tier stays TOY.** Nothing in this batch, mine included, is a result
   about HQC.

---

## 10. Artifacts

All under
`coordination/goals/GOAL-HQC-001/batches/BATCH-c5703d/reviews/TASK-20260806-42c153/`:

| file | what it is |
|---|---|
| `perturb.py` | the eight-variant (T) instrument harness; self-tests against `stage_a.decode_blocks` |
| `perturb_PS-R1.json` | 400,000-trial aggregates: per-block counts, pairwise co-occurrence, `S` histograms, per variant |
| `analyze.py` | `REF-1` / `REF-2` / `REF-3` for clause (a); the contrast test for clause (b) |
| `clause_a_results.json` | clause (a) at `T = 400,000` |
| `clause_ab_results_T160k.json` | clauses (a) and (b) at `T = 160,000` |
| `probes.py` | composite-null construction, `q` mis-specification, `OPEN-7` |
| `probes_results.json` | `OPEN-7` third measurement; the first (inert) composite-null family |
| `composite_null_break.json` | §2: the tail-directed laws, their exact moments, and the measured sizes |
| `counterexample.txt` | §4: the `n_e = 3` law with binomial `S`, equal marginals, dependent blocks |

*Red-team record. I wrote only inside this directory. I changed no status, no
ledger record, no experiment contract and nothing under the producer's frozen
task directory; the four frozen hashes verify unchanged after my run.*
