# VAL-20260804-a84239 — what I re-derived, and how

Validator, BATCH-d3a45a (batch 4 of 6), GOAL-MLKEM-004.
Reviewing snapshot `e8cc366eb4ea7da267d97d6c93415e972eacfa3f`, archiving
`TASK-20260804-7e6b54`.

**SCOPE, binding on every line.** m=35, n=25, d=60, q=127, secret centred-binomial
eta=2, error rounded-Gaussian sigma=2, **one instance** (BATCH-f75059 replicate 0,
seed 20260803206). **TOY SCALE. No ML-KEM break claim, no security proof, no FIPS
203 parameter set affected or cleared, no speedup, no cost claim, no exponent
moved.** AGENTS.md **rule 12 UNMET and UNWAIVED**, inherited: this report changes
the status of no `EV-MLKEM-*` record and no `KN-*` entry and proposes none. I did
not produce this package and I have repaired nothing in it. I ran no `git commit`.

**Verdict: `ADMISSIBLE_WITH_DEFECTS`.** Eight numbered defects in `report.yaml`.

---

## 0. Instrument, built by me, verified before any measurement

Own venv `/tmp/sagevenv-vala84239`, own gmp symlink `/tmp/gmplink-vala84239`, built
from scratch per `KN-TECH-14efa5`. Both documented fixes were required and applied
(`--no-build-isolation`; self-provided `libgmp.so`). Build 07:24:05Z → 07:28:03Z,
238 s. Earlier venvs (`/tmp/sagevenv-exec7e6b54`, `/tmp/sagevenv-val3fc363`,
`/tmp/gmplink-val`, `/tmp/le`) were present and **not used**.

Discriminators reproduced **before** any contrast was measured:

| check | pinned | measured by me |
|---|---|---|
| shim not on `sys.path`, `PowerSeriesRing` constructs | KN-TECH-14efa5 | `[]`, constructs |
| `BKZ.EasyParam` raises "Cannot open strategies file." | KN-TECH-14efa5 | reproduced |
| dim 60 qary q=3329 BKZ-30×4: `‖b0‖` 160.4 → 130.3 | KN-TECH-14efa5, 0.3 s | **160.4 → 130.3, 0.24 s** |
| g6k bgj1 on the research instance | archive: N=17919, a_x 0.888475041394716 | **N = 17919, delta 0.0e+00 exactly** |

Environment drift **confirmed as environmental, not a producer error**: passagemath
resolves to 10.8.8 in my venv too. fpylll 0.6.4, g6k 0.1.2, numpy 2.4.6, python
3.11.15 — all as recorded.

Snapshot integrity: commit reachable from `HEAD`, parent as declared, working tree
clean, all six `source_path_sha256` values in the snapshot receipt match on disk,
`git show --stat` changes exactly the six declared paths (2663 insertions, 0
deletions). I validated the committed snapshot, not a working tree.

---

## 1. The reproduction

I wrote my own build and score code rather than running `surrogate.py`. The scorer
is written from the definition

```
means[d,k] = (1/N) sum_i cos( 2*pi*( x_i . E_d + y_i . (s - c_k) ) / q )
```

and cross-checked against a **literal element-by-element evaluation of that same
definition** (no addition formula) on 5 draws × 22 candidates:

```
SIEVE        literal-definition cross-check: max|delta| = 7.772e-16
MATCHED_BKZ  literal-definition cross-check: max|delta| = 6.106e-16
```

Seeds, draw blocking (2000 draws in blocks of 250) and the row-permutation tag
convention were matched to the producer's so that an *exact* numerical comparison
was possible. That makes this a **code-independent** reproduction, not a
seed-independent one (LIM-2).

### 1.1 One thing had to be fixed before reproduction was possible

`surrogate.py`'s `_sample()` stops each window on `time.time() - t0 < time_cap`,
driven by `--pool-seconds 95`. The archived transcript shows this truncating window
`(k0=48, p=0.50)` at 350,000 of 1,200,000 draws and dropping both `k0=54` windows
entirely. **The recorded command therefore does not reproduce the recorded pool on
any other machine.** I substituted the realised per-window counts, which the
transcript happens to record, for the clock. That reproduced the build
**bit-for-bit** — every count, every collision, every norm:

```
[   50.7s]  window k0=30 p=0.25 drew 1200000 kept 5810
[   61.9s]  window k0=30 p=0.50 drew 1200000 kept 1
[   76.4s]  window k0=36 p=0.25 drew 1200000 kept 30790
[   88.9s]  window k0=36 p=0.50 drew 1200000 kept 225
[  101.8s]  window k0=42 p=0.25 drew 1200000 kept 130641
[  114.7s]  window k0=42 p=0.50 drew 1200000 kept 7746
[  129.5s]  window k0=48 p=0.25 drew 1200000 kept 341273
[  134.2s]  window k0=48 p=0.50 drew  350000 kept 30236
[  135.2s]  drew 8750000 kept 546722 below cut (6.248%)
[  137.9s]  distinct non-zero pool 27550 (dropped 72 that ARE sieve vectors)
```

and the BKZ profile (`274/269/422`, `223/223/397`, `223/222/376`, GS `r0=223.0
r59=12.700 sum_r=4875.7`) and the match quality (`+0.0921/0.1142/0.1138` on `‖x‖`,
`+0.1875/0.2178/0.1808` on `‖y‖`, `214.54/179.08` against `181.49/129.08`) came out
identical. This is **DEF-1**: the package is reproducible from the *transcript*,
not from the *command*.

### 1.2 Certificates — my own arithmetic

Three independent checks per family, none of which touches g6k or fpylll:
`R = (X @ A - Y) mod q` in int64; an **exact Python-bigint** recomputation of
`sum_k x_k A[k,j]` on a random 400-row × 25-column sample, which cannot silently
overflow; and an int64 headroom bound `max|x|·(q-1)·m < 2^62`. Plus zero-vector,
duplicate-`(x,y)`, **duplicate-`x`-row** and `v`/`-v` checks — the last two the
producer did not run.

| family | entries | violating (int64) | violating (bigint sample) | zero | dup (x,y) | dup x | v & −v |
|---|---|---|---|---|---|---|---|
| SIEVE | 447,975 | **0** | 0/400 rows | 0 | 0 | 0 | 0 |
| POOL | 688,750 | **0** | 0/400 | 0 | 0 | 0 | 0 |
| MATCHED_BKZ | 447,975 | **0** | 0/400 | 0 | 0 | 0 | 0 |
| MATCHED_LONG | 447,975 | **0** | 0/400 | 0 | 0 | 0 | 0 |

Total 2,032,675 entries, **0 violating** — the producer's number exactly.

**Disjointness, checked on what remains rather than assumed from the construction:**
`|MATCHED_BKZ ∩ SIEVE| = 0` under sign-canonical keys **and** `= 0` raw. The 72
dropped pool vectors reproduce exactly. There is no `x`-collision hiding behind a
different `y` representative — 0 duplicate `x` rows, and in any case two lattice
vectors with equal `x` differ by `q = 127` in some `y` coordinate while the norm cut
forces `|y_j| ≤ 20`.

**`MATCHED_BKZ` is a valid dual family of the same lattice and it is disjoint from
the sieve database. Both claims hold.**

### 1.3 The arms

| arm | real | rowperm | excess | z | producer |
|---|---|---|---|---|---|
| SIEVE | 0.137241 | 0.108030 | 1.2704 | 6.4 | identical |
| MATCHED_BKZ | 0.697050 | 0.128344 | 5.4311 | 167.6 | identical |
| MATCHED_LONG | 0.815887 | 0.151529 | 5.3844 | 695.7 | identical |
| NORMMATCH_RANDDIR | 0.114156 | 0.105036 | 1.0868 | 2.4 | identical |
| NULL_IID_PHASE | 0.940056 | 0.907045 | 1.0364 | 2.0 | identical |

Every printed digit. Uniform-group excess across all seven arms lies in
`[0.9859, 1.0171]` — the statistic is null on generic frequencies for every family.
The frozen decision rule recomputes mechanically: bracket
`[1+0.5(se−1), 1+2(se−1)] = [1.135194, 1.540777]`, `me−1 = 4.431107` outside it,
`|mz| = 167.6` not `< 2`, therefore `C_NEITHER`. **That verdict refutes both of the
outcomes the dispatching card named**, which is itself weak evidence against a
post-hoc rule.

---

## 2. T2 — the closed form and the forcing argument

I re-derived the closed form before checking it. To first order in the phase,

```
F_k = (1/N) sum_i cos(u_i)  +  (1/N) sum_i sin(u_i) phi_ik ,   phi_ik = 2 pi Y[i,k]/q
```

The first term is `k`-independent. Under a row permutation the second is a sum of
`N` decoupled products, so `sd_k(F) = rms(sin u)·rms(phi)/sqrt(N)`; dividing by
`sqrt(1/2N)` gives `rms(sin u)·rms(phi)·sqrt(2)`, times `c4(8)` for the sample-sd
bias. And `E[sin^2 u] = (1 − exp(−2·Var u))/2` with
`Var u = 4 pi^2 sigma^2 ‖x‖^2/q^2 = 2 a_x`, giving `rms(sin u)^2 = (1 − e^{−4a_x})/2`.
The producer's formula is correct as written.

Recomputed on the nine archived instances: pooled prediction **0.10716077** against
measured **0.10655157** — ratio 1.005717, i.e. **0.57%** (the report's 0.6%); max
per-instance `|ratio − 1| = 0.011053`, matching the archived
`forced_value_max_rel_error` to all digits. I also confirmed
`a_x = 2 pi^2 sigma^2 mean‖x‖^2/q^2` reproduces `a_x_measured` exactly on all nine.

Out of sample I now have **five** families, not three:

| family | mean‖x‖² | mean‖y‖² | measured rowperm | closed form | ratio |
|---|---|---|---|---|---|
| SIEVE | 181.5 | 129.1 | 0.108030 | 0.106924 | 0.9898 |
| MATCHED_BKZ | 214.5 | 179.1 | 0.128344 | 0.126822 | 0.9881 |
| MATCHED_LONG | 397.5 | 270.0 | 0.151529 | 0.156877 | 1.0353 |
| **VAL_SIEVE_SUMS** | 362.5 | 258.1 | 0.153821 | 0.153354 | **0.9970** |
| **VAL_POOL_PAIRRED** | 211.2 | 148.6 | 0.114035 | 0.115476 | **1.0126** |

All within 3.6%, and the residual grows with the phase scale exactly as a
first-order expansion should. **It is a prediction, not a fit.**

**The forcing argument holds, and it holds as algebra rather than as measurement.**
Every input to the closed form — `mean‖y‖²` through `rms(2πY/q)`, `mean‖x‖²` through
`a_x` — is *exactly* invariant under a row permutation. The row-permuted arm's value
is therefore fixed by the real family's own norms and cannot approach `c4(8)` for a
short dual family. Every archived arm preserving the `y` multiset lands in
`[0.1053, 0.1131]`.

**Can the null placed on T2 fail?** Yes, and I re-measured it: `NULL_IID_PHASE` (the
sieve's own `X`, uniform residues mod `q` for `Y`) returns 0.940056 against
`c4(8) = 0.965030`; the uniform candidate group returns 0.9300–1.0043 across all
seven families; `SENS-1` (`y := 0`) is archived at 6.19e-15. Dynamic range
`[0, ≈1]`, arms at 0.107–0.140. **`NULL-IID` is admissible; `NULL-ROWPERM` is not.**

**One thing does not reproduce (DEF-3).** The factors *7.126×* and *9.385×* are
computed against **1.0**, not against `c4(8)` — `results.json` literally computes
`1.0/value`. Against `c4(8)` they are **6.877×** and **9.057×**. Report §2 asserts
the correct reference, says in the same paragraph that using 1.0 is "a 3.5% error,
not negligible at this effect size", and then tabulates the 1.0-referenced numbers
under the heading "vs the model". `KN-TECH-9d21c4` carries the same pair. The
archived `stage_a.py` already emits `sd_ratio_to_iid_c4_corrected`, so the corrected
number cost nothing.

---

## 3. The card's question 3, answered by construction rather than by extrapolation

The producer's argument — excess flat at 5.38–5.43 across a "2.2×" range in
mean `‖x‖²` while the sieve at 181 sits at 1.27 — does not close it, and the
producer said so. The measured range here is 1.85× (214.5 → 397.5); 2.2× needs E3
(470.5), a batch-3 red-team number obtained under different scoring parameters and
explicitly *not* re-measured. Worse, every point is from **one construction**, and
the inference runs **downward**, from 214 to 181, in a direction never sampled.

So I built the family the producer's design excluded.

**`VAL_SIEVE_SUMS`** — `v_i ± v_j` over random pairs of g6k sieve vectors,
deduplicated, `N = 17919`, certified **0/447,975 violating**. A valid dual family of
the same lattice, **sieve provenance**, at `MATCHED_LONG`'s norm scale.

```
VAL_SIEVE_SUMS   mean||x||^2 362.5   mean||y||^2 258.1   excess 1.2115  z  12.1
MATCHED_LONG     mean||x||^2 397.5   mean||y||^2 270.0   excess 5.3844  z 695.7
```

Two certified valid dual families of the same lattice, within 10% in mean `‖x‖²` and
5% in mean `‖y‖²`, **separating 4.4× apart**. Norm scale does not determine the
excess, and the residual +18%/+39% mismatch cannot be what separates 5.43 from 1.27.

And the direction matters: doubling the sieve family's norms moves its excess
slightly **down** (1.2704 → 1.2115). That also kills the reading that the sieve would
climb toward 5.4 if its norms were raised.

**The producer's conclusion is right. The producer's evidence did not establish it;
this does.**

---

## 4. The card's question 4 — the sieve-is-least-separating observation

Real as a measurement. An artifact as an interpretation.

### 4.1 Pair reduction — the sieve's own operation — moves it

**`VAL_POOL_PAIRRED`** — one round of pair reduction on the *same* fpylll
nearest-plane pool (pair reduction being exactly what the producer excluded, "pair
reduction is what a sieve does"), then the 17,919 shortest, deduplicated, disjoint
from the sieve database (intersection 0), certified 0/447,975 violating:

```
MATCHED_BKZ        mean||x||^2 214.5  mean||y||^2 179.1  excess 5.4311
VAL_POOL_PAIRRED   mean||x||^2 211.2  mean||y||^2 148.6  excess 3.2439  (z 104.0)
```

At **unchanged** `mean‖x‖²`, one sieve-like reduction step cuts excess−1 from 4.43 to
2.24. The sieve/non-sieve axis is doing work — but as a *continuous* property of
database geometry, not as the binary that the card's outcomes A and B assumed.

### 4.2 A model that predicts all five families and contains neither provenance nor norms

Write `u_i = 2π x_i·E/q`, `phi_ik = 2π Y[i,k]/q`. The near-miss spread is driven at
first order by `B_k = (1/N) Σ_i sin(u_i) phi_ik`, whose covariance over error draws
is

```
Cov[k,k'] = (1/N^2) phi_k^T S phi_k' ,
S_ii' = 0.5 ( exp(-c ||x_i - x_i'||^2) - exp(-c ||x_i + x_i'||^2) ),  c = 2 pi^2 sigma^2/q^2
```

and the row-permuted arm replaces `S` by its diagonal. I evaluated this on the
**full** 17,919-row databases (no subsampling — subsampling destroys neighbour
structure proportionally and would bias the ratio) and Monte-Carlo'd the expected
sample sd over the 8 near-miss candidates:

| family | measured excess | model excess |
|---|---|---|
| SIEVE | 1.2704 | 1.290 |
| MATCHED_BKZ | 5.4311 | 5.757 |
| MATCHED_LONG | 5.3844 | 5.940 |
| VAL_SIEVE_SUMS | 1.2115 | 1.235 |
| VAL_POOL_PAIRRED | 3.2439 | 3.337 |

Five families, 2–10% agreement, from inputs that are only the `x`-database's
pairwise-distance kernel and the `y` columns.

### 4.3 It is *not* raw clustering

I also measured the phase-free effective-neighbour count
`kappa = mean_i Σ_{i'} ( e^{-c‖x_i-x_i'‖²} + e^{-c‖x_i+x_i'‖²} )`:

```
SIEVE 6456.1 > POOL_PAIRRED 4942.4 > MATCHED_BKZ 4761.3 > SIEVE_SUMS 1363.7 > MATCHED_LONG 1176.8
```

**Anti-correlated with the excess.** The sieve database is the most densely packed
of the five and still the least separating. What varies is the quadratic form — the
*alignment* of the `y` columns with the near-neighbour geometry of `x` — not the
clustering.

### 4.4 Where this sits

On the same one-parameter axis as the archived batch-3 red team's E1
(`RT-20260803-d2e23e`: no lattice, no sieve, no `A`, no modulus, `y := x[0:25]`,
excess 17.078):

```
SIEVE_SUMS 1.21 ~ SIEVE 1.27 < POOL_PAIRRED 3.24 < MATCHED_LONG 5.38 ~ MATCHED_BKZ 5.43 < E1 17.08
```

The producer's §5.1 hypothesis — "the nearest-plane families are internally
structured, so their `x`-database is far more coherent at the frequencies `a_k`" —
is essentially right, and is now measured rather than named, with the correction
that coherence **at those frequencies** is the operative quantity, not coherence.

**None of this is a measurement of the independence heuristic**, which remains
untested after four batches. That is the producer's own §5.4 and I confirm it.

---

## 5. T4, checked against the archived files myself

**T4a.** `stage_b_results.json → B3_per_instance` gives `n_vectors = [4253, 4253,
4253]`; `B1_admissible_tuples` gives `Nf_modeled = 45128.788121081096` (p=2),
`716.5496009363183` (p=3), `99.26631959271373` (p=5). Ratios **10.611048229739266**,
0.168481, 0.023340 — the report's 10.611×, 0.168×, 0.023×. The measured-vs-modelled
labelling is correct: `N` is a count of sieve vectors, `Nf` is a cost-model output.

**T4b.** The resolution checks out. `nulls[0].statistic` names **three group**
statistics under one field; `statistic_reads_the_object: "YES"` is justified by the
residual phase `psi_i` and explicitly by the **correct bin**. §5.3 says the opposite
of the *group* statistics and gives its evidence (SENS-1 barely moves the near-miss
sd ratio, 1.09472 → 1.14012 at p=2; SENS-3 non-monotone on 0 of 3 instances at every
p) while separately confirming the correct bin *does* move (paired `|z|` median
14.8–31.3, max 101.0). Two statements about different statistics; the unqualified
field is the defective one; §5.3 is the correct side. **Producer's resolution
confirmed.**

**One partial dissent.** The same entry also records
`can_it_fail: "YES, for every group AND for the correct bin"`. That is not merely
unqualified — "for every group" is *contradicted* by the package's own failed
sensitivity demonstrations, and "both statements are true of different statistics"
does not cover it. A future correction should name `can_it_fail` as defective too.

---

## 6. T3 — reading `KN-TECH-9d21c4` as a stranger

**Could someone who knows nothing about this campaign apply it? Mostly yes.**

What works: the four-part obligation is ordered and short; each of the three failure
modes has a worked case with a transferable tell (Mode 1's "the correct candidate's
offset is `y·(s−s) = 0`, so the control is bitwise invariant"; Mode 2's "total
removal must be at least as extreme as partial removal and on the same side";
Mode 3's "substitute the defining relation into the statistic and expand"); "how to
run step 4" is cheapest-first and correctly identifies move 3 as the one that gets
skipped; the YAML checklist is copyable verbatim. The single most transferable line —
`statistic_reads_the_object` is a property of an *(object, statistic)* **pair** and
must be recorded per statistic — is precise enough to check compliance
mechanically, and I verified the archived contradiction it is grounded in.

**Is the four-part obligation stated precisely enough to check compliance, or is it
advice?** Three of the four are checkable. **Obligation 3 is advice.** "Exhibit a
case where the statistic provably moves when the object is removed" names no
threshold: how much movement, against what spread, at what sample size, and compared
with *which arm*. This batch's own package shows why that matters —
`NORMMATCH_RANDDIR` "moves" at z = 2.4, and the entry gives no rule for whether that
counts, while report §1.6 scores it against the **most** separating arm available
(5.4311) to claim a factor of ~50, when against the arm the null is actually about
(the sieve, 1.2704) the factor is **3.1** (DEF-7). Concrete fix: require the
demonstration to be reported as a signed effect against the *same* surrogate spread
used for the headline, with the comparator named, and require the comparator to be
the arm the null is about.

Two further precision gaps: obligation 4's exit condition is checkable only where a
closed form exists (the entry should say plainly that move 3 alone discharges it when
moves 1–2 are infeasible); and the symbols in
`c4(k)·rms(2πY/q)·rms(sin u)/sqrt(1/2)` are undefined for a stranger — `Y`, `q`,
`k`, `u`, `N` and the underlying score are never introduced, and I had to read the
producer's code to get `rms(Y)` right. `a_x` *is* defined. Three sentences would fix
it.

Two factual defects are inherited by the entry: the 7.13×/9.39× table referenced to
1.0 rather than the `c4(8)` it advocates (**DEF-3**), and "was never reported", which
is false against the archived `RT-20260803-d2e23e` §3 (**DEF-4**). The entry does
list that report in `source_refs`, so this is not concealment — but a false priority
claim now sits inside a knowledge entry whose whole subject is honesty about
controls.

**This is a review finding only. Rule 12 is UNMET and UNWAIVED; I change the status
of no `KN-*` entry and propose no change.**

---

## 7. The defect that governs how much any of this is worth archiving

`results.json` contains **no vectors**. The `.npz` work file lives only in `/tmp`.
So the headline certificate — "0 violating entries in 2,032,675 checked, re-verified
from `A` and the emitted integers" — **cannot be checked from the snapshot**, because
the snapshot has no emitted integers. I could only check it because DEF-1's
mitigation let me regenerate the families. A validator on a different machine, or
after `/tmp` is cleared and the pool timing shifts, would have had to take the
certificate on trust. Four int64 arrays of 17,919 × 60 compress to a few MB
(**DEF-2**).

---

## 8. Budget and runs

| | allowed | used by me |
|---|---|---|
| wall clock | 2400 s | venv 238 s, discriminators 10 s, build 163 s, score 187 s, coherence/clustering 127 s |
| memory | 6 GB | peak RSS 1211 MB (build), 639 MB (score); `RLIMIT_AS` 6 GB set in-process |
| measurement runs | 2 | **2** (one build, one score) |

The clustering pass in §4.3 is a derived-statistics pass over the work file already
produced by the build run — no new family, no new contrast. Recorded here rather
than hidden.

I could not verify the producer's own timings (1055 s compute, session wall clock
over 3000 s): they are self-reported and there is no external clock in the artifacts.
Marked `unable_to_check`. The producer recorded the overrun rather than hiding it.

## 9. Non-claims

- No ML-KEM break. No attack implemented, run or claimed. No speedup.
- No security proof and no security claim in either direction.
- No FIPS 203 parameter set affected or cleared. Toy scale, AGENTS.md rule 7 in full.
- The independence heuristic is neither validated nor refuted here.
- No lane closed or opened. Certificates establish lattice membership only; no
  discrete-log solve, no factor-base relation, no solution certificate of any kind.
- `ADMISSIBLE_WITH_DEFECTS` means the receipt is admissible evidence. It does not
  support an ML-KEM claim, demonstrate a speedup, or authorize any promotion.
