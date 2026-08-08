# Red team — BATCH-a44d08, Sections A, B and C

TASK-20260806-e43218 / BATCH-a44d08 / GOAL-MLKEM-005
Governed by `ledger/decisions/DEC-20260806-14ac13.yaml` (AM-3, AM-4, AM-5) and by
the frozen contract `tasks/TASK-20260806-843c40/prereg.md`,
sha256 `8d00ca3f0977e7367cfd10f4eb01cc0d4d24dfdc1ecf9739ba3cc299ee2a6c80`
(recomputed at the shell in this session; agrees with `prereg_sha256.txt` and with
the blob in the notarizing commit `9cb2d3e28ae7a474edbb116d694969470829e112`).

**Claim tier TOY, unconditionally.** Nothing in this report bears on ML-KEM
security, on any FIPS 203 parameter set, on any attack cost, or on any cost
model. Every object I built is at `d <= 140`, `beta <= 40`, `q <= 3329`. I change
no research status, dispose of no hypothesis, promote nothing to knowledge, and
**rescore no frozen verdict**. I modified no producer artifact and made no commit.

## Inference record (verbatim, as directed)

```
requested_policy: review-adversarial (aliases review-xhigh, red-team-adversarial)
resolved: anthropic:claude-opus-5 (effort=xhigh) via `orchestration.adapter resolve --role red-team --independent-session`
fallback_used: false
independent_session: true — separate agent context, did not originate any producer artifact, and a different role from the producing executor
model_verified: false
model_verified_reason: >-
  Under the Claude Code runtime, per CLAUDE.md, per-role model and effort selection is
  process-level; subagents keep model: inherit. The session model is claude-opus-5, matching
  the resolved binding exactly. The xhigh reasoning-effort tier cannot be asserted or probed
  from inside the subagent, and no adapter probe receipt exists for this session. Recorded as
  a verification gap rather than claimed as satisfied.
```

Independence in this batch remains **procedural**, never model-level: all three
producers and both reviews resolve to the same backend. Recorded, not smoothed.

## Snapshot verification — what I actually reviewed

```
snapshot commit   7700090428ae7f8b5dbaaf7bb54a7a253c53fae8
                  "research: GOAL-MLKEM-005 TASK-20260806-f4d678 snapshots all
                   three BATCH-a44d08 producers"
git merge-base --is-ancestor 7700090428... HEAD   -> true
files in that commit  12 producer artifacts + 1 snapshot receipt (13 total)
git diff 7700090428... HEAD -- .../BATCH-a44d08/tasks/   -> EMPTY
git status --porcelain                                   -> clean
```

Every number I quote from a producer is read from that commit's tree. I reviewed
no working-tree-only artifact.

---

## 0. Verdict in one page

| producer | headline | my verdict |
|---|---|---|
| A, TASK-20260806-3084bc | "the confinement boundary tracks `k` and never `d-k`"; NEITHER in four cells | **THE `E_I` ARM RAN IN ITS COULD-NOT-FAIL ARRANGEMENT.** `E_I` is an exact algebraic function of the random matrix `A` alone; I reproduce it to 12 digits from the singular values of `A`, and it returns the identical "M-K confirmed" curve on `Z^d`. The boundary tracks `rank(A)`, not `k`. |
| B, TASK-20260806-e17677 | the AM-3 gate is INADMISSIBLE because the positive control does not fire at `c = 6` in 3 of 4 cells | **THE CONTROL RAN IN ITS COULD-NOT-FAIL ARRANGEMENT, IN THE MIRROR DIRECTION.** Given the recorded data, `P(INADMISSIBLE) = 0.997` under the frozen step-selection lottery. The identical injection fires at `c <= 6` at 6, 7, 9 and 7 of the 12 steps in the four cells. |
| C, TASK-20260806-c973e6 | L2 TAIL-SUFFICIENCY FALSIFIED on 2 of 10 pairs | **NOT ESTABLISHED.** I built the null object the report itself says does not exist (§9.7). On an exact matched-`V`, matched-`m3` null the frozen falsifier fires in **17/20 and 13/20** disjoint null pairs, median null `\|t\| = 11`, against a declared per-pair level of `0.0083`. |

All three producers implemented the frozen text correctly and disclosed more than
they were required to. Every objection below is against the **design and the
reading**, not against the bench. Sections A §10 O-1, B §6.1/A-5 and C §9.6/§9.7
each named the defect I go on to demonstrate; the executors were right and their
objections were under-weighted, not wrong.

---

## 1. SECTION A — the boundary result is a theorem about `A`, not a measurement

### 1.1 The arrangement in which Section A's `E_I` arm could not have failed, and it ran in it

The Coordinator's lead is correct and is worse than stated. Prereg §2.7 and
report §8 both disclose that `E_I^{M-K}(beta) = min(1, k/beta)` is the exact
**upper** capacity bound and `E_I^{M-D}` the exact **lower** one. Both documents
then argue that this is survivable because a generic frame sits strictly
interior. **It is not survivable, because the frame here is not generic and the
producer's own construction forces the extreme.**

Write `B = [[I_k, A],[0, q I_{d-k}]]` exactly as prereg §2.6 freezes it. For
`beta <= d-k` the tail-`beta` frame is the orthogonal complement of
`span(rows 1..d-beta)`, which is exactly

```
{ ( -A_S z , z ) : z in R^beta },      A_S = the last beta columns of A
```

so with `M = [-A_S ; I_beta]` and `P = M(M^T M)^{-1}M^T`,

```
E_I(beta) = tr(P Pi_I)/beta = (1/beta) * tr( (A_S^T A_S + I)^{-1} A_S^T A_S )
          = (1/beta) * sum_i  s_i^2 / (s_i^2 + 1),      s_i = singular values of A_S.
```

Since `A`'s entries are uniform on `[0, q)` with `q = 3329`, every nonzero `s_i`
is of order `q sqrt(k)`, so every term is `1 - O(q^{-2}k^{-1})` and

```
E_I(beta) = min(rank(A_S), beta)/beta  +  O(q^{-2})  =  min(1, k/beta) + O(q^{-2}).
```

**Measured (my own frames, `d = 100`, `k = 30`, `i = 0`; script `rt_secA.py`):**

| `beta` | `E_I` measured | `min(1,k/beta)` | `1 - E_I/pred` | closed form from `svd(A_S)` |
|---|---|---|---|---|
| 15 | 0.999999940882 | 1.000000000000 | 5.912e-08 | **0.999999940882** |
| 25 | 0.999999791873 | 1.000000000000 | 2.081e-07 | **0.999999791873** |
| 30 | 0.999995207000 | 1.000000000000 | 4.793e-06 | **0.999995207000** |
| 35 | 0.857142639097 | 0.857142857143 | 2.544e-07 | **0.857142639097** |
| 50 | 0.599999970700 | 0.600000000000 | 4.883e-08 | **0.599999970700** |
| 65 | 0.461538447348 | 0.461538461538 | 3.075e-08 | **0.461538447348** |

Agreement to **12 significant figures at every `beta`**. `E_I` is not a
measurement of where a window sits; it is `rank(A_S)/beta` plus an `O(q^{-2})`
correction, and the frozen tolerance is `0.02`.

**The prediction that could have falsified me, and did not.** If my derivation is
right, `1 - E_I` must scale as `q^{-2}`:

| `q` | `1-E_I` at `beta=15` | at `beta=25` | at `beta=65` |
|---|---|---|---|
| 1 | 5.9118e-08 | 2.0813e-07 | 5.3846e-01 |
| 2 | 1.6070e-01 | 2.3172e-01 | 5.8191e-01 |
| 4 | 4.1303e-02 | 8.6278e-02 | 5.4850e-01 |
| 16 | 2.5152e-03 | 8.1443e-03 | 5.3907e-01 |
| 64 | 1.6063e-04 | 5.5478e-04 | 5.3850e-01 |
| 256 | 1.0010e-05 | 3.5438e-05 | 5.3846e-01 |
| 3329 | 5.9118e-08 | 2.0813e-07 | 5.3846e-01 |

Exact `q^{-2}` over three decades (`4->16`: 16.4x; `16->64`: 15.6x; `64->256`:
16.0x; `256->3329`: 169x against `(3329/256)^2 = 169`).

### 1.2 The null object: the identical "M-K confirmed" curve on `Z^d`

Read the `q = 1` row of that table. At `q = 1`, `B = [[I_k, A],[0, I_{d-k}]]` has
determinant 1: **it is unimodular and the lattice is `Z^d`.** There is no `q·I`
block, no q-ary structure, and no mechanism M-K or M-D can be about. The
statistic returns `1 - E_I = 5.9118e-08` at `beta = 15` and
`E_I = 1 - 0.53846 = k/beta` at `beta = 65` — **bit-for-bit the same curve it
returns at `q = 3329`**, and therefore "M-K survives, M-D FALSIFIED at 50x its
tolerance", on the one object `DEC-20260806-14ac13` records as P3's maximum-
departure null. This is the sixth-instance pattern, seventh instance.

### 1.3 The boundary tracks `rank(A)`, not `k` — the headline restated

Forcing `A` to exact rank `r < k` and rerunning the identical code path:

| `rank(A)` | `beta`=5 | 10 | 15 | 20 | 25 | 30 | 35 |
|---|---|---|---|---|---|---|---|
| 30 (`=k`) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.8571 |
| 20 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.8000 | 0.6667 | 0.5714 |
| 10 | 1.0000 | 1.0000 | 0.6667 | 0.5000 | 0.4000 | 0.3333 | 0.2857 |
| 5 | 1.0000 | 0.5000 | 0.3333 | 0.2500 | 0.2000 | 0.1667 | 0.1429 |
| M-K frozen pred (`k=30`) | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.8571 |

The measured boundary is `min(rank(A_S), beta)/beta`. A uniform `A` over `Z_q` is
full rank with probability `1 - O(q^{-(d-2k+1)})`, so at `q = 3329` the boundary
is `k` with probability indistinguishable from 1. **The headline "the confinement
boundary tracks `k` and never `d-k`, at `beta = 30/70/45/105`" is the statement
`rank(A) = k`.** The `E_I` arm had exactly one outcome available to it.

### 1.4 The arm reads `|A|`, not block identity — the nearby-object control

M-K and M-D are zero-free-parameter claims about *which coordinate block* the
window lies in. They say nothing about the magnitude of `A`. Holding the block
structure fixed and shrinking `A`:

| `max|A|` | `beta=15` | `beta=30` | `beta=65` |
|---|---|---|---|
| 3329 | 1.000000 | 0.999999 | 0.461538 |
| 100 | 0.999920 | 0.998865 | 0.461524 |
| 10 | 0.993255 | 0.952773 | 0.460333 |
| 3 | 0.947620 | 0.852977 | 0.451969 |
| 1 | 0.834145 | 0.692110 | 0.419087 |
| M-K pred | 1.000000 | 1.000000 | 0.461538 |

At `max|A| = 1` — same blocks, same `k`, same `d` — M-K is **falsified at 8x the
frozen `0.02` tolerance** at `beta = 15`. "Confinement to the `k`-block" is a
statement about the entry size of `A`, not about the blocks.

### 1.5 What the `NEITHER` verdict actually decomposes into

The `E_I` arm is forced (§1.1). The `V` arm is not, and it is where M-K failed
(22 of 32). So the frozen `NEITHER` verdict is: **a tautology on one arm, plus a
genuine refutation of the "excess spreads generically over the complement"
clause on the other.** The producer's own §6.6 and post-hoc appendix already
locate this — the `beta <= min(k,d-k)` residual moves from `+0.78%..+19.10%` to
`-0.02%..-11.09%` under a Beta-within-block refinement, overshooting rather than
closing. That is the informative part of Section A and it is not about block
identity at all.

I uphold objection **O-1** and strengthen it. The `2%` `V` floor was justified in
prereg §2.5 by "the `<= 2%` agreement the closed form already shows"; on the
committed anchors the disagreements are `-3.9%, -4.7%, -3.2%, -1.5%, -1.7%`, so
the floor sits below the closed form's own committed error on 3 of 5 anchors.
`sep(tol_V MK)` values reported at `24.9`–`265` are therefore denominated in a
floor the model itself cannot meet. The M-K `V` falsifications at `+0.78%` to
`+7.5%` are **inside the closed form's own error budget** and should not be read
as mechanism failures. The falsifications at `+20%` to `+33%` in the spill window
survive that objection and are the real content.

I do **not** accept A-6 as harmless. Report §3 establishes that fpylll's `k`
counts the `q`-scaled rows. Section A builds its own bases so its own record is
correct, but Section C's committed unreduced arm calls
`IntegerMatrix.random(d,"qary",k=d//2,q=3329)`, and **every committed record in
this goal that reads that `k` as `|K_I|` is mislabelled off the `k = d/2`
diagonal**. At `k = d/2` nothing is affected. This is a nomenclature hazard for
the successor batch, not a defect in any committed number.

---

## 2. SECTION B — INADMISSIBLE was a property of the selection rule

### 2.1 The control's outcome is closed-form, and I recompute it exactly

Injecting `c * SE_diff(A,t_i)` into every draw at `t_{i+1}` shifts `Delta_i` by
`+c*SE_diff(t_i)` and leaves `SE_step(i)`, `SE_diff(t_i)` and `epsilon_i`
unchanged (a constant shift of a paired difference). Hence

```
stat_i(c) = ( Delta_i + (c-1) SE_diff(t_i) ) / SE_step(i)
c_min(i)  = 1 + ( t_crit * SE_step(i) - Delta_i ) / SE_diff(t_i).
```

Recomputing `Delta_i`, `SE_step(i)` and `SE_diff(t_i)` independently from the
recorded per-draw `r` values in `results_g3.json` (my `SE_diff` agrees with the
producer's `gate.se_of_difference` to `< 1e-12` at all 52 grid points) reproduces
the frozen control exactly: `c_min = 2.676` at `d100_b40`'s selected step, so the
smallest `c` in `{1,2,3,4,6}` is **3** — the recorded value; `c_min = 23.41,
30.26, 13.79` at the other three selected steps, so **none** — the recorded
value. The frozen control is a deterministic function of the recorded data.

### 2.2 The same injection at every step of the same frozen grid

| cell | frozen argmax step | `c_min` there | frozen `c` | **steps of 12 firing at `c <= 6`** |
|---|---|---|---|---|
| `d100_b30` | 0 | 23.41 | none | **6** |
| `d100_b40` | 7 | 2.68 | 3 | **7** |
| `d140_b30` | 0 | 30.26 | none | **9** |
| `d140_b40` | 1 | 13.79 | none | **7** |

Restricted to the plateau (`i >= 5`), the median `c_min` is `3.98 / 2.72 / 3.76 /
4.17` — inside the frozen `c` grid in every cell. The plateau is precisely where
§3.5's identification "creates a known monotonicity violation of exactly that
size" is *valid*, because it holds only where the true `Delta_i` is `0`.

### 2.3 The arrangement in which Section B could not have failed, and it ran in it

Prereg §3.6 names two forms, both of which are forms of "the gate cannot fire".
It did not name the mirror: **a positive control that cannot pass.** That is the
one Section B ran in.

`SE_diff(A,t_i)` sets both *which* step is injected and *how large* the injection
is (report A-5, correctly). On this family `SE_diff` is largest at the top of the
steep descent, where `|Delta_i|` is 11x to 26x the injection unit, so firing at
`c = 6` requires `5*SE_diff > |Delta_i| + t_crit*SE_step`, i.e.
`|Delta_i|/SE_diff < ~5`. Realized at the selected steps: `18.69 / 0.57 / 25.70 /
11.09`. Three of four **could not fire at any `c`**, and the frozen grid stops at
6 in any case.

Worse, the selection is a lottery. The 12 `SE_diff` values are near-tied
(`1.19–2.02e-3`, `1.20–1.48e-3`, `1.23–1.76e-3`, `0.80–1.55e-3`) and each is
estimated from 8 draws (a sample sd on 7 df carries about 27% relative noise).
Bootstrapping the 8 draw indices jointly across every `t` and the Haar null,
`B = 20000` (`rt_secB2.py`):

| cell | `P(argmax = observed)` | distinct argmax seen | **`P(selected step cannot fire at c<=6)`** |
|---|---|---|---|
| `d100_b30` | 0.674 | 8 | **0.942** |
| `d100_b40` | 0.443 | 9 | **0.473** |
| `d140_b30` | 0.335 | 9 | **0.659** |
| `d140_b40` | 0.684 | 8 | **0.709** |

```
P(all four cells fire, i.e. gate NOT declared INADMISSIBLE) = 0.058 x 0.527 x 0.341 x 0.291 = 0.0030
P(INADMISSIBLE)                                                                            = 0.9970
```

**A positive control that returns "cannot fire" with probability 0.997 regardless
of the gate's power is not a control on the gate.** The frozen INADMISSIBLE
verdict stands as the output of the frozen rule — I rescore nothing — but it is a
property of the argmax-`SE_diff` selection rule on this family, not a
demonstrated property of the AM-3 gate. This is the seventh instance of the
pattern `DEC-20260806-14ac13` records, and the first in which the *control*
rather than the *statistic* is the object with the invisible defect.

Two things the AM-3 gate *is* shown to have, and they should not be lost with the
INADMISSIBLE label: (i) a false-failure bound of `0.096` that is mechanically
free of every run-supplied quantity (I confirm the derivation and that all 48
`epsilon_i >= 0`, min `7.98423e-04`); (ii) realized firing at `c_min` between
`1.86` and `~5.6` on the plateau of all four cells. The narrowest true statement
is that **the AM-3 gate's power has not been demonstrated at the step the frozen
rule selects, and the frozen rule selects a step at which no gate of this form
could have been demonstrated.**

---

## 3. SECTION C — the falsification is not established; I built the missing null

Report §9.7 states that no null calibration of the frozen falsifier exists in
this batch and names one as a follow-up. I built it. `rt_secC.py`.

### 3.1 First, I reproduce the frozen pipeline exactly

Using `vmatch.py`'s own functions and the committed seeds:

| pair | `D_GR` | `D_TL` | `|t|` | rel | `V_GR` |
|---|---|---|---|---|---|
| `d100_b40 t=0.0075` mine | 0.02285961 | 0.01886438 | **3.6887** | 17.48% | 6.546441 |
| frozen | 0.02285961 | 0.01886438 | 3.689 | 17.48% | 6.546441 |
| `d140_b40 t=0.0050` mine | 0.02638101 | 0.02011863 | **8.1481** | 23.74% | 9.086503 |
| frozen | 0.02638101 | 0.02011863 | 8.148 | 23.74% | 9.086503 |

Agreement to every reported digit. Everything below is measured with the frozen
instrument, not an approximation of it.

### 3.2 The defect: the frozen SE cannot see the TL arm's configuration variance

`vmatch.py`'s `tl_frame` is deterministic and supported on the fixed coordinate
pairs `(a, a+beta)`. **All 8 TL "draws" share one coordinate support**; they
differ only through `u_j`, which is itself a function of `V_GR,j`. So the TL arm
carries no independent randomness, and
`SE = sd_j(D_GR,j - D_TL,j)/sqrt(8)` omits the between-support variance of the TL
family entirely. The producer identified exactly this at the degenerate
instrument check and deflated by `sqrt(1+n) = 3`; the same omission is present at
**every scored pair**, undetected because `sd(D_TL)` is nonzero there for the
spurious reason that `u_j` varies.

### 3.3 The null object, built

Two TL families on **independent random ambient supports at identical `u_j`**.
`V` and `m3` are identical by construction (verified: `|ΔV| <= 8.9e-16`,
`|Δm3| <= 1.7e-16` on the float32 frames), and the CBD error law is i.i.d. across
coordinates, so **the population `D` is identical**. Any firing of the frozen
falsifier is a false falsification. 40 supports per cell, committed error sample.

```
BETWEEN-SUPPORT sd of D_TL at fixed u_j
  d100_b40 : min 2.533e-03  median 2.748e-03  max 2.767e-03   ( = 2.54x the pair's ENTIRE reported SE 1.083e-03 )
  d140_b40 : min 2.271e-03  median 2.458e-03  max 2.566e-03   ( = 3.20x the pair's ENTIRE reported SE 7.686e-04 )
```

| null design | `d100_b40` | `d140_b40` |
|---|---|---|
| **N1** fixed-vs-fixed support, 20 **disjoint** pairs — false falsifications | **17/20** | **13/20** |
| N1 median null `|t|` (crit 3.636) | **11.06** | **11.25** |
| N1 all 780 pairs (dependent, secondary) | 79.0% | 70.6% |
| **N2** varying-vs-fixed support (the *structure* of the real GR-vs-TL comparison), 500 replicates — false falsifications | **24.6%** | **25.2%** |
| N2 replicates exceeding the frozen pair's own `|t|` | **117/500 (23.4%)** | **13/500 (2.6%)** |
| N2 median relative difference | 9.04% | 8.41% |

Against a declared per-pair Bonferroni level of `0.10/12 = 0.0083`, the realized
per-pair false-falsification rate of the frozen statistic on an exact null of the
same shape is **0.246 to 0.85**, a factor of **30 to 100**. Referred to the N2
null distribution, the two FALSIFYING PAIRS have per-pair p-values of about
`0.234` and `0.026`; Bonferroni at `n_C = 12` gives family-wise `~1.0` and
`~0.31`. **Neither pair clears the design's own declared family-wise `0.10` once
the falsifier is calibrated against a null.**

Note also that condition (ii) does no work: the null's *median* relative
difference is `8.4–9.0%`, already above the `5%` "practically meaningful" bar.

### 3.4 The artifact tell: what should have destroyed the signal, and did not

The parameter that ought to destroy a spurious `D_GR - D_TL` offset is the error
sample. Re-running the two falsifying pairs on three fresh CBD samples (same
frames, same `u_j`):

| pair | committed sample | +7919 | +15838 | +23757 |
|---|---|---|---|---|
| `d100_b40 t=0.0075` | 3.689 (FIRES) | **1.700** | 10.630 | **3.375** |
| `d140_b40 t=0.0050` | 8.148 (FIRES) | 8.682 | 4.062 | 4.963 |

The fragile pair fails to falsify in **2 of 3** redraws. The strong pair fires in
4 of 4, but its `|t|` ranges over `4.06–8.68` — a spread the reported SE
`7.686e-04` does not admit. And 4-of-4 does **not** rescue it: the null shows that
a *fixed* pair of frame configurations at identical `V` and `m3` carries a
persistent offset that no redraw of the error sample removes. Persistence across
error samples is exactly what the null object also has.

### 3.5 Quantifier-order and scope objections to the C headline

* **Both falsifying pairs are GR-vs-TL: synthetic-vs-synthetic.** Not one of the
  three real-lattice (unreduced) pairs falsifies — their `|t|` are `1.624`,
  `2.103`, `2.440`. If L2's claim is that `D` is a function of `V` for **lattice
  tail frames**, it has not been touched. If the claim is universal over rank-
  `beta` projectors, then the correct baseline is that it is false for trivial
  reasons — `D` depends on the whole diagonal law of `P`, of which `V` is the
  second moment. Prereg §4.1 already concedes the third cumulant involves
  `sum_a P_aa^3` independently of `V`. **The falsification, if real, is a
  restatement of the design's own stated premise, not new information.**
* **The claimed mechanism does not predict the magnitudes.** `ΔD/Δm3` over the
  10 scored pairs is `-0.26, 1.57, 1.78, 1.78, 3.58, 0.96, 0.42, 1.02, 2.53,
  2.27` (×1e-3), a spread of 8.5x with one sign flip, and 3.7x *within* the
  single cell `d100_b40`. A third-cumulant law at fixed `(d, beta)` should not do
  that. This is not fatal — `V` varies over the pairs and the Edgeworth
  coefficient varies with the quantile location — but it is the cheapest
  discriminating check the design omitted, and it costs one regression.
* **Objection 1 of the report's §9 is correct and is a defect in the frozen
  text**: prereg §4.3 step 5 asserts all four committed unreduced `V` are inside
  the TL-reachable intervals; `6.750435 < 8.571429` at `(140,30)`. The executor
  applied the frozen UNREACHABLE rule, which is the right call.

---

## 4. AM-4 applied to EVERY statistic any producer proposes

AM-4 requires invariance under (a) ambient isometry `B -> BH`, (b) row
permutation of the basis, (c) unimodular `B -> UB`. Every one of those preserves
the lattice (`BH` up to isometry). Built and measured, `d = 100`, `beta = 40`,
`k = 50` q-ary, 8 bases, committed error sample, `N = 2^20` (`rt_am4_D.py`):

| presentation of THE SAME LATTICE | `E_I` | `V` | `m3` | `D` |
|---|---|---|---|---|
| as built (identity presentation) | 1.000000 | 16.29108 | 0.33675 | 0.053166 |
| **row permutation** (unimodular) | 1.000000 | 17.77467 | 2.05476 | **0.060250** |
| **unimodular `U`** | 1.000000 | 16.35285 | 0.41045 | 0.053162 |
| **ambient isometry `B -> BH`** | **0.501690** | **0.42244** | **0.00145** | **-0.000495** |
| Haar / reference | `k/d` = 0.500000 | `E[V]_haar` = 0.470588 | — | — |

| statistic | (a) `B->BH` | (b) row perm | (c) `B->UB` | AM-4 |
|---|---|---|---|---|
| `E_I` (A) | **FAILS** — `1.000000 -> 0.501690 = k/d`, i.e. M-K's extreme becomes the Haar value, which falsifies **both** mechanisms | passes here | passes here; but **the producer's own A-lll arm is a `B->UB`** and moves `E_I` from `min(1,k/beta)` to `0.32–0.39` at `(100,30)` against `k/d = 0.30` | **REFUSED** |
| `V` (A, B, C) | **FAILS** — 38.6x | **FAILS** — 9.1% | 0.4% | **REFUSED** (already refused as P3) |
| `m3` (C) | **FAILS** — 232x | **FAILS** — 6.1x | 22% | **REFUSED** |
| `D` (B, C) | **FAILS** — sign change, `+0.053166 -> -0.000495` | **FAILS** — `+13.3%`, i.e. above C's own 5% "practically meaningful" floor | 0.008% | **REFUSED** |
| `r = q_emp/q_Beta`, `m(t)`, `Delta_i`, `SE_step`, `SE_diff`, `shift_SE`, G1/G2 (B) | all are functions of `D`/`R` on a frame, so all inherit `D`'s failure under (a) and (b) | — | — | **REFUSED** |
| `E_q = 1 - E_I` (A) | inherits `E_I` | — | — | **REFUSED** |
| `E[V]_haar`, `V_TL(u)`, `m3_TL(u)`, `q_Beta(2^-10)`, `t_crit`, the `0.096` bound (design constants) | invariant — they are functions of `(d, beta, u, n)` only, not of any object | invariant | invariant | **N/A — not statistics of an object** |

Ratios across presentations of one lattice: `E_I` 2.0x, `V` 42.1x, `m3` 1420x,
`D` sign-changing.

**No statistic proposed anywhere in BATCH-a44d08 satisfies AM-4.** All three
producers correctly disclaim AM-4 adjudication (prereg §5.8), and I am not
citing this as a violation — it is the answer to the fourth `next_action` of
`DEC-20260806-14ac13`, which asked whether an AM-4-admissible statistic exists.
The measured answer for this family is: **not `E_I`, not `V`, not `m3`, not `D`,
and not the degree-1 alternative `W = sum_{a<=k} P_aa - beta k/d`, which is an
affine function of the same diagonal and dies under `B -> BH` for the same
reason.** The obstruction is nameable: every observable in this goal is a
function of `diag(QQ^T)` in the standard basis, and `diag` is exactly the object
that `B -> BH` destroys. Forward guidance in §6.

---

## 5. The arrangement in which MY OWN check could not have failed

Named before I ran, and the demonstration.

**Named.** (i) A "this was forced" claim can be made about any deterministic
computation and is unfalsifiable if I do not commit to a *quantitative* law that
could be wrong. (ii) A null object can be built quiet — at a `u`, a cell or a
sample size where the statistic happens not to fire — and then "no false
falsifications" is a property of my choice. (iii) A "the frozen rule is a
lottery" claim can be manufactured by bootstrapping any argmax, since argmaxes
are always somewhat unstable. (iv) Reporting only the falsifying redraws of an
error sample.

**Why I am not in it.**

1. Against (i): I committed to `E_I = (1/beta) sum_i s_i^2/(s_i^2+1)` and to
   `1-E_I ~ q^{-2}`. Both are two-sided and both could have failed at any of the
   six `beta` and seven `q` values in §1.1–§1.2. The rank experiment (§1.3) is a
   third independent falsifier: if the boundary tracked `k` rather than
   `rank(A)`, the `rank = 10` row would read `1.0000` through `beta = 30`. It
   does not.
2. Against (ii): my null runs at **exactly the `u_j` of the two claimed
   FALSIFYING PAIRS**, in exactly their cells, on exactly their error sample —
   the least favourable operating point I could have chosen. If the frozen
   falsifier were well calibrated there, my objection would have died. I also
   report **two** null structures, and the one that mirrors the real comparison
   (N2, varying-vs-fixed) gives the **smaller** rate, 24.6%/25.2%, and that is
   the number I lead with.
3. Against (iii): the bootstrap is not the load-bearing evidence. §2.2's
   closed-form `c_min` at **all 12 steps of all 4 cells** is deterministic, and
   §2.3's `|Delta_i|/SE_diff` at the selected step (`18.69/0.57/25.70/11.09`)
   shows three selected steps could not have fired **at any `c`**, with no
   resampling at all. The bootstrap only quantifies how easily the fourth could
   have gone the other way.
4. Against (iv): I report **all** redraws I ran — 3 per pair, chosen as
   `+7919*{1,2,3}` before I saw any of them — including the `+15838` redraw that
   raises `d100_b40` to `|t| = 10.63`, which cuts against me, and the `d140_b40`
   pair that fires in 4 of 4.

**The residue I cannot close.** My null is TL-vs-permuted-TL. It is an exact null
for the *population*, but its frame-to-frame geometry is more homogeneous than
GR-vs-TL, so my rate is a statement about the frozen statistic's calibration and
**not** proof that the GR-vs-TL difference is zero. I do not claim it is. My
probe is on my own frames, at the scale actually run (`N=2^20`, `n=8`, 40
supports), not pre-registered, and **rescores no frozen verdict**: Section C's
`L2 TAIL-SUFFICIENCY FALSIFIED` remains the output of the frozen §4.4 criterion.
Second: my §1 derivation is exact only for `beta <= d-k`; above that fold I
verified `E_I = min(1,k/beta)` numerically but did not derive it. Third: all my
timings are on a host at load average ~240 on 14 shared cores.

---

## 6. Cheapest falsification of each headline, with cost

| headline | cheapest falsifier | cost | status |
|---|---|---|---|
| A: "the confinement boundary tracks `k`" is a discriminating measurement | Run the identical `E_I` code path at `q = 1` (lattice `= Z^d`) and at `rank(A) = 10`. If `E_I` is unchanged at `q=1` and moves to `min(1,10/beta)` at `rank 10`, the arm measures `rank(A)` | **0.14 s**, no lattice reduction, pure numpy | **RUN — falsified** (§1.2, §1.3) |
| A: `E_I` adjudicates anything about the lattice | Compute `E_I` on `BH` for one random orthogonal `H` | **< 1 s** | **RUN — `1.000000 -> 0.501690 = k/d`** (§4) |
| A: M-K's `V` failures at `+0.78%..+7.5%` are mechanism failures | Compare against the closed form's own committed error on the 5 anchors (`-1.5%..-4.7%`) | **arithmetic, 0 s** | **RUN — those points are inside the model's own error** (§1.5) |
| B: "the AM-3 gate is INADMISSIBLE" | Apply the identical injection at all 12 steps: `c_min(i) = 1 + (t_crit·SE_step_i - Delta_i)/SE_diff(t_i)` | **0.09 s**, arithmetic on the recorded per-draw values | **RUN — fires at 6/7/9/7 of 12 steps** (§2.2) |
| B: INADMISSIBLE is a property of the gate | Bootstrap the argmax-`SE_diff` selection over the 8 draws | **2.85 s** | **RUN — `P(INADMISSIBLE) = 0.997`** (§2.3) |
| C: "L2 TAIL-SUFFICIENCY FALSIFIED" | Two TL families on independent random supports at identical `u_j` (identical `V`, `m3`, population `D`); score the frozen §4.4 statistic | **52 s** for both cells, 40 supports each, no reduction | **RUN — 17/20 and 13/20 false falsifications; median null `\|t\| = 11`** (§3.3) |
| C: the effect is a property of the frames, not of the error sample | Re-run the two pairs on 3 fresh CBD samples | **included in the 52 s** | **RUN — the fragile pair fails in 2 of 3** (§3.4) |
| C: `D` is presentation-independent enough for the 5% bar | Row-permute the basis of one lattice and recompute `D` | **2.77 s** | **RUN — `D` moves 13.3%, above C's own 5% floor** (§4) |

Total compute for every falsifier above: **under 60 seconds**, one process, BLAS
pinned to one thread, no lattice reduction, no BKZ, no LLL. Every one of these
was affordable inside the producers' own unused budgets (Section A used 3.0% of
its wall clock, B 0.5%, C 0.31%).

---

## 7. Required controls for the successor batch

1. **Before any statistic is frozen again, run the AM-4 triple on it.** It costs
   under 3 seconds and it has now refused four statistics in a row. Make it a
   pre-registration gate, not a post-hoc review finding.
2. **`E_I` must not be re-frozen without a `q`-sweep and a `rank(A)` sweep.** Any
   observable whose value is unchanged from `q = 3329` to `q = 1` is not
   measuring the q-ary construction.
3. **A positive control must be scored where its injection identification is
   valid**, i.e. at steps whose true `Delta` is `~0`. The frozen argmax-`SE_diff`
   rule is data-independent but not defect-independent; replace it with "report
   `c_min` at all 12 steps" — that is a strictly stronger, cheaper, and
   lottery-free characterization, and it is what §2.2 computes.
4. **No cross-family `D` comparison without a permutation null.** Every family
   whose frames have a coordinate support must be replicated over supports, and
   the between-support sd must be added to the SE. Here that sd is 2.5x–3.2x the
   entire reported SE.
5. **Replicate the error sample.** One shared `2^20` sample per cell is a single
   draw of a nuisance quantity that the SE does not see; three samples cost
   seconds and would have caught the fragile pair.
6. **Report `dominated_by` for the instrument.** Nothing in this goal has yet
   been compared against the obvious baseline for the question it is asking —
   what a Haar frame, a random coordinate projector, and a `Z^d` frame return —
   as a *frontier*, only as spot nulls.

---

## 8. Closure discipline — the negative results in this batch carry the same burden

Under `docs/inventor-protocol.md` §4, "the gate is INADMISSIBLE" is a closure
claim about the gate and needs a named obstruction, an argument, and forward
guidance. Section B's INADMISSIBLE has an obstruction (§2.3: `SE_diff` sets both
the selection and the scale) but the obstruction belongs to the **control**, not
to the gate, and the report does not claim otherwise — its §8 explicitly declines
to declare the AM-3 repair adequate or inadequate. That restraint is correct and
should be preserved in the Coordinator's decision: **do not retire AM-3 on this
evidence.** Retiring a gate whose only demonstrated failure is a defect in its
own positive control would be premature closure in the exact sense §4 names.

Symmetrically, `NEITHER in all four cells` (Section A) is not a closure of the
M-K/M-D question. What is closed is narrower and firmer: **the `E_I` observable
cannot separate M-K from M-D, because it is `rank(A_S)/beta + O(q^{-2})` for any
basis of that shape and returns M-K's curve on `Z^d`.** That is a named
obstruction with an argument, and the forward guidance is §6/§7 below and above.

---

## 9. Narrowest supported statement

* **Section A.** On 8 explicitly-constructed q-ary bases at
  `(d,k) in {(100,30),(100,70),(140,40),(140,100)}`, the measured `E_I` equals
  `min(1, k/beta)` to `<= 1.3e-3` at all 36 points. That equality is an algebraic
  consequence of `B = [[I_k,A],[0,qI]]` with `A` of full rank and entries of
  order `q`, holds identically at `q = 1` where the lattice is `Z^d`, and tracks
  `rank(A)` rather than `k`. The `E_I` arm therefore supports no statement about
  either spill mechanism. The `V` arm's falsification of M-K's generic-spread
  clause in the window `min(k,d-k) < beta <= max(k,d-k)` (`+20%` to `+33%`)
  survives objection O-1 and is the section's real result. Reproduction of the
  committed `k=d/2` anchors to `<= 0.6%` and the fpylll `k`-convention read
  (fpylll's `k` counts `q`-rows) are both sound and useful.
* **Section B.** The frozen AM-3 positive control returned AM3-TIE at `c = 6` in
  3 of 4 cells. Given the recorded per-draw values, that outcome had probability
  `0.997` under the frozen step-selection rule, and the identical injection fires
  at `c <= 6` at 6, 7, 9 and 7 of the 12 steps in the four cells. The AM-3 gate's
  false-failure bound of `0.096` is correctly derived and free of run-supplied
  quantities; its power is undemonstrated, not disproved.
* **Section C.** The reported `|t| = 3.689` and `8.148` are reproduced exactly.
  On an exact matched-`V`, matched-`m3` null of the same shape, at the same `u_j`
  and the same error sample, the frozen falsifier fires at a per-pair rate of
  `0.246`–`0.85` against a declared `0.0083`, with median null `|t| ~ 11`.
  Referred to that null, neither falsifying pair reaches the design's declared
  family-wise `0.10`. **`L2 TAIL-SUFFICIENCY FALSIFIED` is not supported by this
  evidence.** Nothing here shows the effect is absent: the `d140_b40` pair fires
  on 4 of 4 independent error samples, which is consistent with a real
  configuration-dependent offset that `V` and `m3` do not determine — and equally
  consistent with the null, which also produces persistent per-configuration
  offsets. The variance-level identity
  `Var(e^T P e) = 2 beta + (mu_4-3)(V + beta^2/d)` is untouched.
* **Everything above is TOY.** `d <= 140`, `beta <= 40`, `n = 8`, `N = 2^20`,
  `q <= 3329`, presentation-dependent observables, no reduced arm beyond LLL.
  Nothing bears on ML-KEM, on FIPS 203, or on any cost model.

---

## 10. `red_team_report` record

```yaml
red_team_report:
  id: RT-20260808-e43218
  task_id: TASK-20260806-e43218
  batch_id: BATCH-a44d08
  goal_id: GOAL-MLKEM-005
  claim_tier: TOY
  snapshot_reviewed: 7700090428ae7f8b5dbaaf7bb54a7a253c53fae8
  prereg_sha256: 8d00ca3f0977e7367cfd10f4eb01cc0d4d24dfdc1ecf9739ba3cc299ee2a6c80
  claim_under_review: >-
    Section A: the confinement boundary tracks k and never d-k, in mirrored (k,d-k)
    pairs, verdict NEITHER in four cells. Section B: the AM-3 gate is INADMISSIBLE
    because the mandatory positive control does not fire at c=6 in three of four
    cells. Section C: L2 TAIL-SUFFICIENCY FALSIFIED on 2 falsifying pairs of 10.
  objections:
  - id: RT-A1
    severity: SEVERE
    target: TASK-20260806-3084bc, the E_I arm
    statement: >-
      E_I is not a measurement. For B = [[I_k,A],[0,qI_{d-k}]] the tail-beta frame is
      {(-A_S z, z)} and E_I = (1/beta) sum_i s_i^2/(s_i^2+1) over singular values of
      A_S, which equals min(rank(A_S),beta)/beta + O(q^-2). Reproduced to 12
      significant figures at every beta. The arm therefore had one outcome available
      to it and the E_I half of the NEITHER verdict is a tautology.
    evidence: rt_secA.py section A1; report_k.md section 6.1 measured values
  - id: RT-A2
    severity: SEVERE
    target: TASK-20260806-3084bc, the E_I arm
    statement: >-
      The identical curve is returned at q = 1, where B is unimodular and the lattice
      is Z^d. On the one object DEC-20260806-14ac13 records as P3's maximum-departure
      null, the statistic reports M-K survives and M-D falsified at 50x tolerance.
      1-E_I scales exactly as q^-2 over three decades, confirming the mechanism.
    evidence: rt_secA.py section A2
  - id: RT-A3
    severity: SEVERE
    target: TASK-20260806-3084bc, the headline
    statement: >-
      The boundary tracks rank(A), not k. At rank(A)=10 with k=30 the departure is at
      beta=10. "The boundary tracks k" is the statement that a uniform k x (d-k)
      matrix over Z_q has full rank.
    evidence: rt_secA.py section A3
  - id: RT-A4
    severity: MODERATE
    target: TASK-20260806-3084bc, the E_I arm
    statement: >-
      With the block structure held fixed and A's entries in {0,1}, M-K is falsified
      at 8x the frozen 0.02 tolerance at beta=15. The arm reads the entry magnitude of
      A, not block identity.
    evidence: rt_secA.py section A5
  - id: RT-A5
    severity: MODERATE
    target: TASK-20260806-3084bc, objection O-1 upheld and strengthened
    statement: >-
      The 2% V floor sits below the closed form's own committed error on 3 of 5
      anchors (-3.9, -4.7, -3.2, -1.5, -1.7 percent). M-K's V falsifications at
      +0.78% to +7.5% are inside the model's own error budget. The +20% to +33%
      falsifications in the spill window survive and are the section's real content.
    evidence: report_k.md section 10 O-1; prereg section 2.5
  - id: RT-B1
    severity: SEVERE
    target: TASK-20260806-e17677, the INADMISSIBLE headline
    statement: >-
      The injection shifts Delta_i by exactly c*SE_diff(t_i) and changes nothing else,
      so c_min(i) = 1 + (t_crit*SE_step_i - Delta_i)/SE_diff(t_i) in closed form. The
      identical injection fires at c <= 6 at 6, 7, 9 and 7 of the 12 steps in the four
      cells; plateau-median c_min is 3.98 / 2.72 / 3.76 / 4.17. INADMISSIBLE is a
      property of the argmax-SE_diff selection, not of the gate.
    evidence: rt_secB.py; reproduces the frozen control's own c=3 / none outcomes exactly
  - id: RT-B2
    severity: SEVERE
    target: TASK-20260806-e17677, the positive control's design
    statement: >-
      The prereg named two could-not-fail forms, both "the gate cannot fire". The
      mirror -- a positive control that cannot pass -- was not named and is the one
      that ran. Bootstrapping the 8 draws, P(INADMISSIBLE) = 0.997. At the selected
      step |Delta_i|/SE_diff = 18.69 / 0.57 / 25.70 / 11.09, so three of four could
      not have fired at any c.
    evidence: rt_secB2.py, B = 20000
  - id: RT-C1
    severity: SEVERE
    target: TASK-20260806-c973e6, the FALSIFIED verdict
    statement: >-
      vmatch.py's tl_frame is deterministic on one fixed coordinate support, so all 8
      TL draws share it and the frozen paired SE omits the TL family's between-support
      variance entirely. Measured, that sd is 2.54x and 3.20x the pair's entire
      reported SE. On an exact matched-V matched-m3 null the frozen falsifier fires in
      17/20 and 13/20 disjoint pairs (median null |t| = 11.06 / 11.25), and 24.6% /
      25.2% under the null structure that mirrors the real comparison, against a
      declared per-pair level of 0.0083.
    evidence: rt_secC.py C3; reproduces the frozen |t| = 3.6887 / 8.1481 exactly first
  - id: RT-C2
    severity: MODERATE
    target: TASK-20260806-c973e6, the fragile pair
    statement: >-
      Re-run on 3 fresh CBD error samples, d100_b40 t=0.0075 gives |t| = 1.700, 10.630,
      3.375 -- not falsifying in 2 of 3. d140_b40 t=0.0050 fires in 4 of 4 but ranges
      over 4.06-8.68, a spread the reported SE 7.686e-04 does not admit.
    evidence: rt_secC.py C2
  - id: RT-C3
    severity: MODERATE
    target: TASK-20260806-c973e6, scope
    statement: >-
      Both falsifying pairs are synthetic-versus-synthetic. None of the three
      real-lattice unreduced pairs falsifies (|t| = 1.624, 2.103, 2.440). If L2's
      claim is about lattice tail frames it is untouched; if it is universal over
      rank-beta projectors, prereg section 4.1 already concedes the third cumulant
      depends on sum_a P_aa^3 independently of V, so the result restates the premise.
      Additionally, dD/dm3 spans 8.5x across the 10 pairs and 3.7x within d100_b40
      alone, with a sign flip -- the claimed mechanism does not predict the magnitudes.
    evidence: vmatch_report.md section 4 table; arithmetic on it
  - id: RT-X1
    severity: MODERATE
    target: all three producers
    statement: >-
      No statistic proposed anywhere in this batch satisfies AM-4. Under ambient
      isometry B->BH on one lattice: E_I 1.000000 -> 0.501690 (= k/d, the Haar value,
      which falsifies BOTH mechanisms); V 16.29 -> 0.42; m3 0.337 -> 0.0014; D
      +0.053166 -> -0.000495 (sign change). Under row permutation (unimodular, same
      lattice): D moves 13.3%, above Section C's own 5% practical floor; m3 moves 6.1x.
      Section A's own A-lll arm is a B->UB that moves E_I from min(1,k/beta) to
      0.32-0.39 against k/d = 0.30. All three producers correctly disclaim AM-4
      adjudication; this is recorded as the measured answer to DEC-20260806-14ac13's
      fourth next_action, not as a contract violation.
    evidence: rt_am4_D.py; rt_secA.py section A4; report_k.md section 9
  - id: RT-X2
    severity: MINOR
    target: committed records off the k = d/2 diagonal
    statement: >-
      Report_k section 3 establishes that fpylll's k counts the q-scaled rows. Any
      committed record reading that k as the identity-block size is mislabelled off
      k = d/2. Nothing at k = d/2 is affected; this is a hazard for the successor.
    evidence: report_k.md section 3, anomaly A-4
  required_controls:
  - Run the AM-4 triple (B->BH, row permutation, B->UB) on any statistic before it is frozen. Cost under 3 s.
  - Sweep q down to q = 1 and sweep rank(A) on any block-confinement observable.
  - Score a positive control at every step, or at steps whose true Delta is ~0; report c_min per step rather than a single argmax-selected verdict.
  - Replicate any coordinate-supported frame family over its supports and add the between-support sd to the SE.
  - Replicate the error sample at least 3 times per cell before any tail-quantile difference is declared.
  - Regress dD on dm3 within a cell before attributing a matched-V difference to the third cumulant.
  counterexample_or_mutation: >-
    BUILT. (1) q = 1 in the frozen Section A construction: the lattice is Z^d,
    E_I returns min(1,k/beta) bit-identically to q = 3329, so the frozen boundary
    result holds on an object with no q-ary structure. (2) rank(A) forced to 10:
    the boundary moves to beta = 10, not k = 30. (3) Two TL families on independent
    random ambient supports at identical u_j: V and m3 identical to 1e-16, population
    D identical by exchangeability of the CBD law, and the frozen Section C falsifier
    fires in 17/20 and 13/20 disjoint null pairs.
  baseline_comparison: >-
    Not applicable in the Pollard-rho / BSGS sense: no attack, no cost claim, no
    asymptotic claim is made or reviewed here, and dominated_by is "n/a (no attack
    claimed; instrument measurement only)". The relevant baselines for this goal are
    null objects, and against them: Section A's E_I arm is DOMINATED by the trivial
    baseline rank(A_S)/beta, which reproduces it to 12 digits at zero cost and on any
    lattice including Z^d; Section C's falsifier is DOMINATED by its own null, which
    produces larger |t| than either claimed falsifying pair at a rate of 0.25-0.85.
    sota_delta: Section A E_I adds nothing over the algebraic identity; Section A's V
    arm adds a genuine +20% to +33% refutation of the generic-spread clause; Section B
    adds a correctly-derived 0.096 false-failure bound; Section C adds an exact
    reproduction of the committed instrument and 10 fully reported pairs.
  heuristic_challenges:
  - The prereg's "generic within a coordinate block" clause is the only free content in M-K/M-D, and it is the only part that failed (V arm). The block-identity part is forced. The heuristic that was actually tested is not the heuristic that was named.
  - Section C's mechanism heuristic (the 2^-10 tail's third cumulant depends on sum_a P_aa^3 independently of V) is stated in prereg 4.1 as the design's own premise. Falsifying it on synthetic projectors confirms the premise rather than testing it; the untested proposition is whether it holds for lattice tail frames, where no pair falsified.
  cost_model_challenges:
  - No asymptotic or cost claim is made in this batch, so the hidden-overhead and per-attempt-times-inverse-success-probability audits do not apply and are recorded as non-applicable rather than omitted.
  - Every falsifier in this report cost under 60 s in total, well inside the producers' unused budgets (A used 3.0% of wall clock, B 0.5%, C 0.31%). The controls were affordable and were not run.
  reduction_and_scope_challenges:
  - No published reduction is cited or instantiated in this batch; that audit is non-applicable.
  - Affected-versus-safe scope: correctly stated everywhere. All three producers hold claim tier TOY and disclaim ML-KEM, FIPS 203, attack cost and AM-4 adjudication. I found no scope inflation in any producer artifact.
  proof_architecture_challenges:
  - Observation-fiber attack, Section A: SUCCEEDS. Hold E_I fixed and vary the object -- B at q = 3329 (q-ary) and B at q = 1 (Z^d) give the same E_I curve at every beta. The missing separator is any observable that depends on q.
  - Nearby-object attack, Section A: SUCCEEDS. The closest object with the conclusion false is the same block structure with |A| ~ 1; E_I falls to 0.834 at beta = 15, falsifying M-K at 8x tolerance.
  - Method-ceiling attack, Section A: the E_I arm's ceiling is "which of the two algebraic extremes does the frame sit at", and the construction forces the upper one. That ceiling does not reach the headline.
  - Boundary-and-strictness attack, Section B: the positive control's rejection region at the selected step is empty for c in {1,2,3,4,6} in three of four cells; the old baseline is not embedded because no c the frozen grid offers can reach it.
  - Quantifier-order attack, Section C: the claim "D is a function of V alone" is falsified for-all-projectors but the scored family contains no lattice frame at either falsifying pair, so the for-all-lattice-tail-frames statement is untouched.
  narrowest_supported_statement: >-
    A: the measured E_I equals min(1,k/beta) to <= 1.3e-3 at all 36 points, and that
    equality is an algebraic consequence of the frozen construction that also holds on
    Z^d and tracks rank(A) rather than k; the E_I arm supports no statement about
    either spill mechanism. The V arm's +20% to +33% refutation of the generic-spread
    clause in the window min(k,d-k) < beta <= max(k,d-k) stands. B: the frozen positive
    control returned AM3-TIE at c = 6 in 3 of 4 cells, an outcome with probability
    0.997 under the frozen selection rule given the recorded data; the AM-3 gate's
    0.096 false-failure bound is correctly derived and its power is undemonstrated
    rather than disproved. C: the reported |t| = 3.689 and 8.148 are reproduced
    exactly, and on an exact matched-V matched-m3 null at the same u_j and error sample
    the frozen falsifier fires at 0.246-0.85 per pair against a declared 0.0083, so
    neither pair reaches the declared family-wise 0.10 and L2 TAIL-SUFFICIENCY
    FALSIFIED is not supported. Nothing shows the effect is absent. All TOY.
  next_concrete_action: >-
    Before any further measurement in this goal, run the three-line AM-4 triple
    (B -> BH, row permutation, B -> UB) plus a q-sweep to q = 1 on every candidate
    observable, as a pre-registration gate rather than a review finding. It costs under
    3 seconds, it has now refused E_I, V, m3 and D, and it would have caught Section A's
    E_I arm before the batch was dispatched. The successor's first task should be the
    obstruction argument this makes available: every observable proposed in this goal is
    a function of diag(QQ^T) in the standard basis, and diag is exactly what B -> BH
    destroys -- so either name an observable that is not a function of the standard-basis
    diagonal, or record "NO ADMISSIBLE PREDICATE EXISTS, HERE IS THE OBSTRUCTION", which
    DEC-20260806-14ac13 AM-4 already declares the preferred outcome.
  dominated_by: "n/a (no attack or cost claim reviewed; instrument-measurement batch)"
  sota_delta: "n/a (no attack claimed); see baseline_comparison for the null-object comparison that does apply"
  artifact_paths:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a44d08/reviews/TASK-20260806-e43218/red_team_report.md
  probe_scripts_not_committed:
  - rt_secA.py     (Section A: closed form, q-sweep, rank sweep, AM-4, nearby object) 0.14 s
  - rt_secB.py     (Section B: closed-form c_min at all 12 steps of all 4 cells)      0.09 s
  - rt_secB2.py    (Section B: bootstrap of the argmax-SE_diff selection, B = 20000)  2.85 s
  - rt_secC.py     (Section C: exact reproduction, 3 error-sample redraws, 40-support null) 52.0 s
  - rt_am4_D.py    (AM-4 table for E_I, V, m3 and D on one lattice, N = 2^20)         2.77 s
  probe_status: >-
    These are RED TEAM PROBES on my own frames. Not pre-registered, at the scale
    actually run, and NOT a rescoring of any frozen verdict. They live in this session's
    scratchpad and are not committed; every number they produce is reported above with
    the command and the environment needed to regenerate it.
  environment: >-
    python 3.13.1, numpy 2.4.0, scipy 1.15.3, macOS-26.6-arm64, 14 shared cores at load
    average ~240, single process, OMP/OPENBLAS/MKL/VECLIB/NUMEXPR pinned to 1. All
    timings are wall clock on a loaded host and are not clean benchmarks.
  prohibitions_observed:
  - I altered no Executor receipt and no Validator report.
  - I called no bounded failure an impossibility result; Section B's gate is undemonstrated, not disproved, and Section C's effect is uncalibrated, not shown absent.
  - I rejected no conditional result for being conditional.
  - I made no commit and wrote nothing outside this task directory.
```
