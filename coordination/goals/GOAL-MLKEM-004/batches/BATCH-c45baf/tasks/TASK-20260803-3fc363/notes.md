# VAL-20260803-3fc363 — what I actually re-derived

**Validator, TASK-20260803-3fc363. GOAL-MLKEM-004 / BATCH-c45baf (batch 3 of 6).**
Reviewed object: Coordinator snapshot `555a5762`, archiving `TASK-20260803-db170f`.

**SCOPE, binding on every sentence.** Toy scale: Stage A m=35, n=25, d=60, q=127;
Stage B sieve dimension m+k_lat=50. One sieve family (g6k 0.1.2 `bgj1_sieve`), one
modulus. **No ML-KEM break claim, no security proof, no FIPS 203 parameter set
affected or cleared, no speedup, no cost claim.** AGENTS.md **rule 12 UNMET and
UNWAIVED**, inherited: this report changes the status of no `EV-MLKEM-*` record and
no `KN-*` entry, and proposes no change. A passed validation means the receipt is
admissible evidence; it does not interpret that evidence.

**Verdict: `ADMISSIBLE_WITH_DEFECTS`** (validator-contract enum: `passed`).
Nine numbered defects in `report.yaml`. Two are moderate, four minor, three cosmetic.

---

## 0. Re-dispatch hygiene

The first attempt at this task was destroyed uncommitted (see
`coordinator_notes/artifact_loss_incident.md`). Nothing from it reached me: I read
the incident record, which by design contains no findings, and worked from the seven
committed artifacts. The producer's scratch directory
(`.../scratchpad/c45baf/`) does not exist in this container, so I could not have
read a producer intermediate even accidentally — everything below came from the
snapshot or from code I wrote in this session.

---

## 1. What I built before believing anything

The container was replaced, so no `/tmp/sagevenv*` existed. I rebuilt the instrument
myself, in a venv named so it cannot be confused with anyone else's:

```
rm -rf /tmp/sagevenv-val3fc363 ; python3 -m venv /tmp/sagevenv-val3fc363
/tmp/sagevenv-val3fc363/bin/pip install --no-cache-dir passagemath-standard   # fpylll 0.6.4 arrives with it
ln -sf /usr/lib/x86_64-linux-gnu/libgmp.so.10 /tmp/gmplink-val/libgmp.so
LIBRARY_PATH=/tmp/gmplink-val LDFLAGS=-L/tmp/gmplink-val \
  /tmp/sagevenv-val3fc363/bin/pip install --no-cache-dir --no-build-isolation g6k
```

Both `KN-TECH-14efa5` fixes were necessary exactly as written, and g6k 0.1.2 came up
with all five kernels. **The recipe now has a second, independent confirmation, by a
second agent in a second container.** `/tmp/le` survived at `3e48ef4` with a clean
tree, so the estimator I read line 540 from is the one the producer declares.

Snapshot integrity first: all seven `source_path_sha256` values match the working
tree *and* the blobs inside commit `555a5762`; parent `9315225a`; reachable from
`HEAD`; `git diff-tree -r` touches exactly the seven producer paths plus the receipt.

---

## 2. The three questions the card put first

### 2.1 Is the surrogate really a row permutation?

**Yes, exactly — as a multiset identity, not a tolerance.**

Reading the code is not enough, so I regenerated instances 0/1/2 myself, applied *my
own* permutation to `Y`, and checked integer equalities:

| check | result (3/3 instances) |
|---|---|
| sorted multiset of `Y` rows (structured sort over all 25 coordinates) identical | **True** |
| `sorted(Y[:,k])` identical for **every** one of the 25 columns | **True** |
| sorted multiset of `‖y_i‖²` identical | **True** |
| `X` (hence the `x` multiset and every `‖x_i‖`) untouched | **True** by construction |

The producer's arm is `(cosPhi[pi], sinPhi[pi])` with `pi = rng.permutation(N)`;
indexing the row axis by a permutation is a bijection on rows, so nothing but the
pairing can change. Confirmed.

### 2.2 Are the nine instances independent draws, or nine views of one database?

**Independent draws.** `sd_ = 20260803206 + 1000*rep` seeds one stream from which
`A`, the secret `s`, the fpylll seed and the sieve seed are all drawn, so every rep
gets a different matrix *and* a different secret *and* a different sieve run.
Downstream: seeds 9/9 distinct, sieve times 9/9 distinct, `mean_xnorm2` 9/9 distinct
(181.278…181.967), `mean_ynorm2` 9/9, `a_x` 9/9, `a_y` 9/9, and the real near-miss sd
ratio 9/9 distinct (0.137226…0.142994). Only `n_vectors` is identical (17919 on all
nine) — expected, since the bgj1 database size at fixed dimension is a saturation
target.

Provenance is separately established, by me: I recomputed `a_x` from my own
regenerated vectors and got **0.0e+00** difference from BATCH-f75059's published
values on reps 0, 1 and 2. Certificates re-verified independently of g6k:
`mod(X·A − Y, q)` had **0 violating entries** in 1,343,925 entries.

The caveat that provenance does *not* cover, and which the producer states itself:
nine seeds from one entropy source, one design. Instance-level independence is real;
it is independence by distinct seeds.

### 2.3 Does the monotone decay survive my recomputation? And what else could make that shape?

**It survives.** Recomputed from the emitted per-instance blocks:

| N′ | 500 | 2000 | 8000 | 17919 |
|---|---|---|---|---|
| pooled excess | 1.0146 ± 0.0374 | 1.0434 ± 0.0174 | 1.1480 ± 0.0310 | 1.3169 ± 0.0188 |
| instances > 1 | 8/9 | 9/9 | 9/9 | 9/9 |

Strict per-instance monotone increase over all four N′: **7/9**; from N′=2000 upward:
**9/9** — exactly the producer's phrasing. And re-measured from scratch on my own
regenerated instances, with my own row ordering, my own permutations, my own error
draws and the *modular* scoring route rather than the cosine-addition one:

```
rep0  1.0448  1.0684  1.2270  1.2562
rep1  0.9858  1.0593  1.1089  1.3317
rep2  1.0135  1.0606  1.1933  1.3533
```

Monotone increasing in all three.

**Now the part the card asked for, and it matters more than the measurement.**

The statistic is `sd_across_candidates(score) / sqrt(1/(2N′))`. The surrogate's raw
spread decays as `1/√N′` to three digits (implied raw sd 3.338e-03 / 1.680e-03 /
8.429e-04 / 5.628e-04), which is *why* its ratio is flat. Fit the real arm to

```
sd_real(N′)² = k/(2N′) + b²
```

Least squares on the four pooled points gives `√k = 0.1062` — statistically
indistinguishable from the surrogate's own flat 0.1065 — and `b = 4.843e-04`, and
reproduces all four measured ratios to better than 0.4%:

```
fitted  0.107263  0.110495  0.122571  0.140274
measured 0.107079 0.110822  0.122380  0.140324
```

So the real arm is *the surrogate's fluctuation plus one fixed, non-decaying
component*. **Once `b > 0`, the ratio must increase monotonically in N′, with no
further content.** "Monotone increasing" and "excess > 1 at full N′" are the same
fact in two coordinates. The decay control rules out the *sampling-noise* artifact
class — a finite-sample fluke would not grow — and rules out nothing else, because
every systematic coupling, algebraic or not, produces this exact shape.

The producer's framing ("the canonical artifact tell fires here") also misreads
`docs/inventor-protocol.md` §3: the parameter meant to *destroy* the effect is the
fraction of pairing removed, `t`, not the database size. Increasing N′ should sharpen
a real effect, not kill it. The protocol's control is SENS-3 — and SENS-3 is in the
package, and it fires correctly (§4 below). So the right control exists; it is the
wrong one that is headlined. That is **DEF-1**.

---

## 3. The mechanism question, and the control the package is missing

If the shape is "a fixed non-decaying coupling exists", the next question is *which*
coupling. Here is one the package never mentions.

A sieve emits vectors short in the **joint** lattice, so `‖x‖² + ‖y‖²` concentrates
on a shell and the two halves are forced to trade off. I measured it:

```
corr(‖x_i‖², ‖y_i‖²)  =  -0.8877  -0.8863  -0.8850     (instances 0, 1, 2)
```

That is a very strong geometric coupling, present in *any* norm-shell-concentrated
vector family, with nothing algebraic about it. And a plain row permutation destroys
it at the same moment it destroys `y = Aᵀx mod q`. NULL-COLPERM and NULL-RANDDIR
destroy it too. So on the package's own control set, the 32% excess could be a
norm-budget artifact and no arm could tell.

The producer's one length-aware arm, SENS-2c, does not close this: it pairs `‖x‖`
rank to `‖y‖` rank **ascending-to-ascending**, i.e. it *co-sorts*, while the real
database is anti-correlated at −0.886. It is oriented the wrong way round, and D-8
records that it "failed to move the statistic" without noticing why.

**So I ran the missing control.** `NULL-NORMSTRAT`: a row permutation of `Y`
restricted to 60 quantile bins of `‖y_i‖²`. It still destroys the algebraic pairing
completely, but it preserves the empirical joint law of `(‖x_i‖, ‖y_{π(i)}‖)` to
within a bin.

| instance | real | NULL-ROWPERM | NULL-NORMSTRAT | excess vs rowperm | **excess vs normstrat** |
|---|---|---|---|---|---|
| 0 | 0.13913 | 0.10749 | 0.10348 | 1.2943 | **1.3445** |
| 1 | 0.13868 | 0.10514 | 0.10915 | 1.3190 | **1.2705** |
| 2 | 0.14421 | 0.10334 | 0.10523 | 1.3956 | **1.3705** |

**The separation survives undiminished.** Restoring the norm coupling moves the
surrogate slightly *away* from the real database, not toward it. The leading
alternative mechanism is refuted — by a control the package does not contain, and the
answer favours the producer. That is **DEF-2**: a completeness gap, not an error.

One more thing fell out of this. I computed the *draw-free* quantity
`sd_j( mean_i w_i cos φ_ij )` — the across-candidate spread of `E_e[score_j]`, with
`w_i` the exact rounded-Gaussian characteristic function. Real vs rowperm:
5.620e-05 / 5.080e-05, 3.184e-05 / 2.878e-05, 4.716e-05 / 4.255e-05. The
error-averaged spread separates by only ~11%, against ~30% on the statistic actually
reported. **Roughly two thirds of the separation lives in the per-draw covariance
between the x-side and y-side phases, not in the mean scores.** That is precisely why
SENS-2 — which is extremal for the mean-score functional — gives |z| = 0.35…3.79 on
the sd ratio (0/9 pass the pre-declared 5) while giving 7.5…12.2 on correct−best
(9/9 pass). The producer says SENS-2 is "the wrong functional"; this quantifies how
wrong, and it means **SENS-3 is not a convenience, it is the only demonstration
carrying the headline statistic.**

---

## 4. Do the sensitivity demonstrations demonstrate sensitivity?

| demonstration | statistic | reproduced? |
|---|---|---|
| SENS-0 (correct score under rowperm) | correct-secret score | max\|Δ\| = **exactly 0.0** on 9/9. Batch 2's NULL-V defect is proved, not asserted. |
| SENS-1 (`y := 0`) | near-miss sd ratio / correct−best | max **6.235e-15** and **exactly 0.0** over nine, against 0.140 and 1.55e-3. Statistics read `y`. |
| SENS-2 (rearrangement) | correct−best | \|z\| = 12.20 8.19 8.51 10.39 9.41 9.03 10.41 8.20 7.53 — **9/9 pass**. Analytic identity holds to 3.758e-05 max over nine against an 8.353e-04 spread. |
| SENS-2 | **sd ratio** | \|z\| = 3.21 3.79 0.77 0.64 1.27 1.81 1.18 1.05 0.35 — **0/9 pass**. Producer reports this. |
| SENS-2c (length-rank) | both | Co-sorted, wrong sign for this geometry (§3). Uninformative, and reported as such by the producer. |
| SENS-3 (dose in `t`) | near-miss | pooled curves monotone on **both** statistics, graded not stepped; uniform flat and 0/9 per-instance monotone. **This is the protocol's decay control and it fires.** |

The two z values the report quotes, −12.2 and 3.21, are both instance 0's, and
instance 0 is the best case of nine on both. The verdicts (9/9, 0/9) are unaffected
and the JSON records them correctly — **DEF-8**, cosmetic.

---

## 5. Re-scoring the aggregation

The producer flags that the rule is its own, not Coordinator-pre-registered, and
supplies absolute differences so it can be re-scored. That disclosure is what made
this section possible. Every scoring I ran:

| scoring | near-miss sd ratio | near-miss correct−best | uniform |
|---|---|---|---|
| producer's rule, recomputed from `per_arm` | 1.316946 ± 0.018811, 9/9 | 0.889292 ± 0.011549, 0/9 | 1.008741 ± 0.019188, 5/9 |
| one-sample **t₈** (what "+50.6" actually is) | +50.55, p ≈ 2.4e-11 | −28.76 | +1.37 |
| exact **sign test** | p = **0.003906** | p = **0.003906** | p = 1.0 |
| exact **Wilcoxon** signed-rank (all 512 flips) | p = **0.003906** | p = **0.003906** | p = 0.3008 |
| **absolute differences** instead of ratios | t₈ = +49.74, 9/9 | t₈ = −28.99, 9/9 | t₈ = +1.32, 5/9 |
| per-instance z vs the surrogate's own realisation spread | 9.4…17.2, median 13.1 | — | — |
| exact **within-instance permutation**, joint over 9 | real strictly max of 11 in **9/9** → 11⁻⁹ = **4.24e-10** | real strictly min of 11 in **9/9** → 4.24e-10 | ranks scattered 0…9 |

Two conclusions.

1. **The rule was not chosen to flatter the result.** Ratios vs differences,
   parametric vs distribution-free, pooled vs per-instance — all agree in direction,
   and the uniform group stays null under every one of them.
2. **"+50.6" should not be read as a significance level.** With n = 9 the
   distribution-free floor is p = 0.0039 (both the sign test and exact Wilcoxon
   attain it — it is the *smallest attainable* value at that sample size). The
   +50.6 figure is a normality extrapolation deep into a t₈ tail from nine points,
   reported without dof and without a p-value. The genuinely strong
   distribution-free statement is the exact permutation result, 11⁻⁹ = 4.24e-10,
   which sits in the producer's own data and is not reported. That is **DEF-3**.

---

## 6. Stage B

**The tuple is admissible.** I read `estimator/lwe_dual.py` at the pinned commit
myself: line 540 is literally `k_lat = params.n - k_fft - k_enum  # p.15`, giving
15 = 25 − 10 − 0, and `m + k_lat = 35 + 15 = 50 = β_sieve`, so the
`deltaf(β_bkz)^(m+k_lat-β_sieve)` exponent is 0 and `β_bkz` genuinely drops out. The
batch-2 obstruction does not arise.

Re-derived by hand from the source formula, not from the callable:

```
lsigma_s   = 2^(35/50) · 127^(15/50) · sqrt(4/3) · sqrt(50/(2πe)) = 13.727116155555624
prefactor  = exp(4 (lsigma_s π/127)²)                             =  1.586012417989119
adjacent   = exp(10/3 · (π/p)²)   p=2,3,5   = 3731.8909237202 / 38.6833408142 / 3.7282809402
           = 2^11.8656911042 / 2^5.2736404907 / 2^1.8985105767
log-term   = 10 log p + log 2     = 7.624618986159398 / 11.679270067241044 / 16.787526304900947
Nf         = 45128.7881210813 / 716.5496009363 / 99.2663195927
```

Every figure matches the producer's to 13 significant digits, and `k_fft = 0` gives
exactly 1.0. **The ML-KEM-512 reference reproduces independently**: with
σ_s = √(3/2) = 1.224744871391589, k_fft = 40, p = 5, the term is
**2685.6646571506 = 2^11.3910634600**, and the cross-check `40 log 5 = 64.377`
matches batch 2's 64.38. I verified the *arithmetic* given (0, 40, 5); that this is
the estimator's optimum is inherited from RT-20260803-dc7568 and I did not re-run the
optimiser. The figure is labelled MODELED everywhere and nothing is asserted from it.

All 18 B3 pooled excesses recompute from `per_arm` to 1e-9.

### Is the producer's INADMISSIBLE declaration on its own Stage B null warranted?

**Yes, and the reason is structural rather than a small-sample accident. The producer
has not been over-cautious and has not discarded a result.**

Compare where candidate-dependence lives:

- **Stage A** (`stage_a.py:410-412`): the candidate-discriminating phase is
  `φ_ij = −2π·Y[i,j]/q` — **a function of `y_i`**. A row permutation of `Y` rewires
  the candidate contrast row by row, at first order.
- **Stage B** (`stage_b.py:386-393`): the candidate-discriminating phase is
  `θ_ij = 2π[(x_iᵀA_fft·s_fft)/q − (âhat_i·c_j)/p]` — **a function of `x_i` alone**.
  The pairing carrier `ψ_i = 2π(y_lat,i·s_lat)/q` is **candidate-independent**;
  `phase_arrays()` applies it as `cp*cosT − sp*sinT` with `cp, sp` permuted and
  `cosT, sinT` not. It multiplies every candidate's row-`i` term identically.

So the pairing cannot generate across-candidate contrast at first order in Stage B —
only through a second-order correlation between the per-row rotation `e^{iψ_i}` and
the x-side contrast structure. The emitted data confirm it. SENS-1 sets `ψ ≡ 0`, the
*maximal* removal of the object; if the group statistic read the object, SENS-1 should
be at least as extreme as NULL-ROWPERM and on the same side of real:

| p=2 | real | NULL-ROWPERM | SENS-1 (ψ ≡ 0) |
|---|---|---|---|
| rep0 | 1.09472 | 1.11794 | 1.14012 |
| rep1 | 1.08974 | 1.13384 | 1.15133 |
| rep2 | 1.03790 | 1.10194 | 1.13626 |

Total removal of the object lands **beyond** the random-repairing arm and on the
**opposite side** from real. Same picture at p=3 and p=5. SENS-3 is non-monotone on
0/3 instances at every p — and on the *uniform* group too, so it separates nothing.
The statistic has essentially no usable dynamic range with respect to the object, and
"no separation detected" from it is uninformative. The refusal is correct.

It is worth naming what this is: **a subtler recurrence of the batch-2 NULL-V
failure**. NULL-V's statistic contained no `y` at all; Stage B's group statistic
contains `y_lat` only as a candidate-independent common rotation, which the
across-candidate *contrast* is blind to at first order. PD-2 caught it — this time
from inside, by the producer. That is the strongest process result in the package.

One inconsistency the producer left standing: `stage_b_results.json → nulls[0]`
still says `statistic_reads_the_object: "YES"` and `can_it_fail: "YES, for every
group AND for the correct bin"`. That is true of the *scores* and of the correct bin
(which does move — paired |z| medians 26.1 / 31.3 / 14.8, max 101.0, though minima
0.8 / 3.1 / 0.2, which the report does not give) and false of the across-candidate
contrast. A consumer reading the JSON instead of §5.3 would conclude the opposite —
**DEF-4**.

And one thing nobody states: **the p=2 arm was measured at N = 4253 vectors against
its own modelled requirement Nf = 45128.8, a 10.6× shortfall.** p=3 (716.5) and p=5
(99.3) are comfortably covered; only p=2 is not, and p=2 is the arm carrying the
largest deviation (0.9607 ± 0.0187). OBS-B2 reports the 454× Nf range but never
compares it to the N actually used — **DEF-5**.

---

## 7. Two numbers that do not reproduce

- **"the uniform curves are flat (every value within 0.005 of the mean)"** — false.
  The pooled curve is 1.000466 / 0.998114 / 0.995518 / **0.987232** / 0.997834 /
  0.995123, mean 0.995715, max deviation **0.008483** = 1.7× the stated bound. The
  substance survives (0.0085 against an across-instance sd of 0.0540, 0/9 per-instance
  monotone); the bound does not. **DEF-6**.
- **"the surrogate stays flat to within 0.001 over a 36× range"** — marginal both
  ways. Max deviation from the mean is 0.000679 (claim holds); max−min range is
  0.001058 (claim fails); N′ range is 35.8×, not 36×. **DEF-7**.

Both are rounding-level and neither changes a conclusion. I record them because a
validator that lets small stated bounds slide has no standing to insist on large ones.

---

## 8. What I could not check

The container replacement destroyed the producer's scratch, which is where the
timings, the peak-RSS figures, the five smoke-run JSONs and both stdout logs lived.
So: **all timings, all memory figures, the smoke-run count, the
zero-discarded-runs claim and the Stage-A-before-Stage-B ordering are unverifiable**
from the archive. I found nothing contradicting them, and two weak positive signs —
the header's frozen reference and `|z| > 5` criterion appear as pre-run constants,
and the results file preserves *failures* (SENS-2c, SENS-2 on the sd ratio, Stage B's
inadmissible null) that a tuned run would have removed. But unverifiable is
unverifiable, and I do not treat them as verified. Also unchecked: KA-0a/KA-0b
(namespace identities, not load-bearing), the three Stage B certificates, the D-2
`gauss_sieve` database-size anomaly, and whether (0, 40, 5) really is ML-KEM-512's
optimum.

---

## 9. What this validation does and does not say

It says the receipt is admissible: the artifacts are bound to a real commit, the
numbers in the report are the numbers in the data, the instances are what they claim
to be, the surrogate is what it claims to be, and the headline observation survives
re-measurement by different code on a different instrument build with different
seeds — plus one control the package lacked, which came out in its favour.

It does not say the dual-attack independence heuristic fails. The replicated effect
is a ~32% modulation of a statistic that is already ~7–10× below the iid prediction
**in both arms**, and that larger effect belongs to the ad-hoc candidate definition
`c = s + e_k`, not to the pairing — as the producer's own OBS-B1 shows from the other
side: under the principled adjacent-FFT-bin definition the raw ratio is ≈1.0 and
nothing separates. Nine toy instances of one design at d=60, q=127 support an
observation and no more.

Independence here is procedural — separate session, separate code, separate seeds,
separate instrument build, no access to the producer's scratch. It is **not**
model-level: this validator resolves to `claude-opus-5`, as did both prior producers
and all four prior reviewers. `DEC-20260803-264d6a` already records that a genuinely
independent check is outstanding; it still is.

**Rule 12 remains UNMET and UNWAIVED. No `EV-MLKEM-*` and no `KN-*` record changes
status, and none is proposed.**

---

## Appendix — commands and scripts I ran

Analysis scripts written this session (scratch, not archived):
`repool.py` (pooled re-derivation from `per_arm`), `decay.py` (decay recomputation and
the `k`/`b` fit), `rescore.py` (permutation ranks, sign/Wilcoxon/t, instance
distinctness), `build.sh` (instrument rebuild), `indep.py` (full independent
re-derivation: instance regeneration, multiset checks, modular-route scoring,
NULL-NORMSTRAT, draw-free `E_e[score]` spread, decay control).

Instrument: `/tmp/sagevenv-val3fc363` (passagemath-standard, fpylll 0.6.4, g6k 0.1.2,
numpy 2.4.6); estimator `/tmp/le` at `3e48ef4`, clean.

`indep.py` runtime 99.6 s / 100.6 s / 99.5 s for instances 0 / 1 / 2 at 500 draws.

**Note on committing.** The dispatch-queue card says "Do NOT run `git commit`". The
Coordinator's re-dispatch instruction overrides that one line, because the first
pass's output was lost precisely by being left uncommitted. I committed exactly the
two files in my `write_scope` and nothing else. I edited no producer artifact, no
ledger record, and no dispatch queue.
