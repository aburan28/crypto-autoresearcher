# TASK-20260804-37a8f2 — red team working notes

**Red team, BATCH-d3a45a (batch 4 of 6), GOAL-MLKEM-004. Reviewing snapshot
`e8cc366e`, archiving `TASK-20260804-7e6b54`.**

**SCOPE, binding on every sentence.** Toy scale: m=35, n=25, d=60, q=127, secret
centred-binomial eta=2, error rounded-Gaussian sigma=2, one instance
(BATCH-f75059 replicate 0, seed 20260803206). **No ML-KEM break claim, no
security proof, no FIPS 203 parameter set affected or cleared, no speedup, no
cost claim, no exponent moved.** AGENTS.md **rule 12 UNMET and UNWAIVED**: this
document changes the status of no `EV-MLKEM-*` record and no `KN-*` entry and
proposes none. I did not produce the package under review, did not repair it,
and did not run `git commit`.

Verdict and the numbered objections are in `report.yaml`. These notes record
what I actually re-derived and what I actually ran, so the derivations can be
checked without trusting me either.

---

## 1. What I did not take on trust

I did not accept the producer transcript as proof of anything. I rebuilt the
instrument, wrote my own scorer from the definition of the score rather than
copying `surrogate.py`'s, re-derived T2's closed form from first principles
before reading the producer's version of it, and recomputed every archived
number I cite from the Coordinator-committed JSON files.

Two runs, against a budget of two. I stopped at two deliberately and named the
remaining measurement as the batch-5 recommendation instead of running it.

---

## 2. Reproduction recipe

Everything below is reproducible from committed artifacts plus the rebuild
recipe `knowledge/techniques/KN-TECH-14efa5.md`.

**Environment.** The card's premise about the container was wrong in the same way
the producer found it wrong: `/tmp/sagevenv-exec7e6b54` was still present and
functional (fpylll 0.6.4, g6k, numpy 2.4.6). I used it read-only rather than
spend five minutes rebuilding an identical venv. This is a convenience, not
evidence: nothing in my conclusions depends on that venv rather than a fresh one.

**Run 1 — reproduction of the producer's build**, archived script unmodified:

```
/tmp/sagevenv-exec7e6b54/bin/python <snapshot>/surrogate.py \
    --stage build --work <scratchpad>/rt_work.npz
```

160.7 s. Regenerated the g6k bgj1 sieve database, the LLL→BKZ-20→BKZ-30→BKZ-40
basis, the randomised nearest-plane pool, the matched family and the long family.

**Run 2 — my own analysis**, script written by me, 168.6 s, peak well under the
6 GB cap. Its six steps are listed in section 4.

Scratchpad only. `rt_analysis.py` and `rt_results.json` are session-local and I
do **not** offer them as durable evidence; every number I rely on is either
recomputed from a committed file or falls out of the derivations below, which
are self-contained.

---

## 3. Provenance check, and a reproducibility defect

The sieve half reproduced exactly: **N = 17919**, `a_x` delta **0.000e+00**,
mean `‖x‖²` 181.4943, mean `‖y‖²` 129.0815. That is a genuinely strong
reproduction and the producer earned it.

The pool half **did not**:

| quantity | archive | my rebuild |
|---|---|---|
| vectors drawn | 8,750,000 | **10,100,000** |
| kept below cut | 546,722 | **843,459** |
| distinct non-zero pool | 27,550 | **29,032** |
| dropped because they ARE sieve vectors | 72 | **74** |
| matched mean `‖x‖²` | 214.54 | **212.67** |
| matched mean `‖y‖²` | 179.08 | **180.15** |
| median abs rel err `‖x‖` / `‖y‖` | 11.38% / 18.08% | **10.92% / 18.94%** |

Cause, located in the archived source: `_sample()` loops on
`while done < per_window and time.time() - t0 < time_cap` with
`--pool-seconds 110`. The producer's run hit the cap partway through the
`k0=48, p=0.50` window and never reached `k0=54`; mine finished that window and
drew 500,000 at `k0=54` before the cap fired. **The family behind "5.4311" is not
determined by the archived script plus the archived seeds.** OBJ-5.

This cuts both ways and I say both. The *number* is not reproducible. The
*contrast* is: on a materially different pool, with a scorer I wrote myself and
different error draws, I get **5.4461** against the sieve's **1.2937**. The
producer could have claimed that robustness and did not.

---

## 4. What I re-derived

### 4.1 The score, and what the near-miss group actually reads

From `surrogate.py` `arm_stats`/`score_family`, the per-draw candidate score is

```
S_k = (1/N) Σ_i cos( 2π ( x_i·e + y_i·(s − c_k) ) / q )
```

For the near-miss group `make_candidates` builds `c_k = s + unit_k` for
`k = 0..7`, so `s − c_k = −unit_k` and the phase offset is **exactly `−Y[i,k]`,
one entry of `y_i`**. Writing `ψ_i = 2π x_i·e/q`:

```
S_k = (1/N) Σ_i cos( ψ_i − 2π Y[i,k]/q )
```

Two consequences worth stating plainly. First, the headline statistic reads only
**8 of the 25 y-coordinates**. Second, because dual vectors are short, the offsets
`2π Y[i,k]/q` are small (`rms|Y_ij| ≈ 2.27`, so `≈ 0.11` rad), which is what makes
the first-order expansion below accurate.

### 4.2 T2's closed form — derived independently, and it is right

Expand to first order in the small offset:

```
S_k − mean_k(S) ≈ −(2π/(qN)) Σ_i sin(ψ_i) Y[i,k]
```

(the candidate-independent `(1/N)Σ cos ψ_i` term drops out of an across-candidate
spread). Under a **row permutation**, `Y` is re-paired independently of `X`, so
the cross terms vanish in expectation and only the diagonal survives:

```
sd_k ≈ (2π/q) · rms(Y) · rms(sin ψ) / √N
```

Divide by the code's reference `√(1/(2N))` and apply the sample-sd bias for
`k = 8`:

```
sd_ratio_rowperm ≈ c4(8) · rms(2π Y/q) · rms(sin ψ) / √(1/2)
```

with `ψ_i ~ N(0, (2π/q)²σ²‖x_i‖²)`, so
`E[sin²ψ] = (1 − e^{−2v})/2` where `v = (2π/q)²σ²‖x‖²`, and since
`a_x = 2π²σ²·mean‖x‖²/q² = v/2`,

```
rms(sin ψ)² = (1 − exp(−4 a_x))/2
```

**This is the producer's formula, term for term, including `c4(8)` and the
`1/√(1/2)`.** I derived it before reading their version. Evaluated on the nine
committed instances in `stage_a_results.json`: mean prediction **0.107161**
against pooled measured **0.106552**, i.e. **0.57%**, max per-instance **1.11%**.
`c4(8) = 0.9650304561473727` recomputed.

**So T2's forcing argument is CORRECT.** `sd_ratio_rowperm` is a deterministic
function of `mean‖y‖²`, `a_x`, `q` and `n` alone. A row permutation preserves the
`‖y‖` multiset exactly, so the surrogate arm was forced to fail the reference.
The producer is right, and every archived arm that preserves the y-multiset does
indeed sit at 0.1053–0.1131 (I read all eight values out of the committed JSON).
The indictment of four batches of controls is deserved.

### 4.3 The harder question the card asked: is T2's own comparison also forced?

**Yes, and in the same way.** The real arm satisfies `real² = rowperm²·(1+ρ)`
(section 4.4), and *both* factors are fixed by geometry — the first by the norm
profile, the second by the construction. Neither is a free parameter that an
independence assumption could have set differently.

More sharply: `sd_ratio_to_iid` is the **marginal** standard deviation of eight
wrong-candidate scores. Its shortfall below 1 is explained entirely by
`sd ∝ rms(2πY/q)·rms(sin ψ)` — i.e. by the phase offsets being small, i.e. by
`‖y‖` being short, which is **the defining property of a dual vector**. "Short
dual vectors have short `y`" is a tautology.

The dual-attack independence heuristic asserts that wrong-candidate scores are
**independent across candidates**. That is a statement about the *off-diagonal*
of the candidate-score covariance and about the distribution of `max_k` over many
wrong candidates. The campaign has measured the marginal variance of eight of
them and called it a test of independence. Four batches. This is RSC-1 and it is
inherited, not introduced by this producer.

### 4.4 The closed form for 1.27 vs 5.43 — the producer's "open question"

Keep the cross terms this time. With `K(i,i') = E_e[sin ψ_i sin ψ_{i'}]`:

```
E[sin ψ_i sin ψ_{i'}] = ½[ exp(−c‖x_i − x_{i'}‖²) − exp(−c‖x_i + x_{i'}‖²) ],
c = ½ (2πσ/q)² = 0.00489525
```

(the diagonal `i = i'` gives `½(1 − e^{−4a_x,i}) = rms(sin ψ)²`, consistent with
4.2 — a useful internal check). Then

```
excess² = 1 + ρ,   ρ = Σ_{i≠i'} ⟨y_i, y_{i'}⟩₈ K(i,i')  /  Σ_i ‖y_i‖²₈ K(i,i)
```

where `⟨·,·⟩₈` is over the 8 columns the near-miss group reads. **Measured with
no scoring at all**, one blocked N×N kernel pass per family:

| family | ρ | predicted excess | measured excess | ratio |
|---|---|---|---|---|
| SIEVE | **+0.718** | 1.3108 | 1.2937 | 1.013 |
| MATCHED_BKZ | **+31.353** | 5.6880 | 5.4461 | 1.044 |
| MATCHED_LONG | **+34.387** | 5.9487 | 5.4298 | 1.096 |

The producer's "why 1.27 ≠ 5.43" is `ρ_matched / ρ_sieve = 44`.

**ρ is a sum over pairs, so it is linear in N.** Subsampling both families to
`N' = 6000` and predicting `√(1 + ρ·N'/N)`:

| family | predicted at N'=6000 | measured |
|---|---|---|
| SIEVE | 1.1138 | **1.1017** |
| MATCHED_BKZ | 3.3909 | **3.3303** |

1.1% and 1.8%. This is, as far as I can tell, the **first empirical confirmation
of the `√(1 + βN)` algebra that `KN-TECH-9d21c4` states at its lines 53–56** —
credit to that entry, and it applies to the new quantity exactly as it applied to
the old one.

Consequence for the campaign's headline: **1.3169 is not an effect size.** It is
`ρ₁ = 4.1×10⁻⁵` evaluated at `N = 17919`, which is whatever bgj1 returned at
d = 60 under that memory budget. Quoting the excess without N quotes a number
with a free multiplier in it.

### 4.5 My first hypothesis was wrong, and the control said so

I began, as the card's framing invited, believing the mechanism was
**near-duplicate clustering**: sieve databases are pair-reduced by construction,
nearest-plane pools are not, so the pool should be full of short pairwise
differences. **That is false and the measurement killed it.**

Minimum sign-aware squared pairwise distance, 6000-vector sample:

| family | median | p05 | fraction < 100 | fraction < 50 |
|---|---|---|---|---|
| SIEVE | 294.0 | 256.0 | 0.000 | 0.000 |
| MATCHED_BKZ | **364.0** | 315.0 | 0.000 | 0.000 |
| MATCHED_LONG | 519.0 | 412.0 | 0.000 | 0.000 |

The matched family's vectors are **further apart** than the sieve's. And applying
a greedy sieve-like pair-separation filter (`min(‖v−w‖², ‖v+w‖²) ≥ τ`) at
τ = 150 / 250 / 350, against a random subsample of identical size:

| family | τ | N' | separated | random, same N' |
|---|---|---|---|---|
| SIEVE | 150 | 6000 | 1.0944 | 1.1017 |
| SIEVE | 250 | 6000 | 1.0942 | 1.1017 |
| MATCHED_BKZ | 150 | 6000 | 3.2973 | 3.3303 |
| MATCHED_BKZ | 350 | 6000 | 3.2682 | 3.3303 |

Pair separation does **nothing**. ρ is a *global second-moment covariance*
between `⟨y_i,y_{i'}⟩` and `K(i,i')` across all 3.2×10⁸ pairs, not a
near-neighbour effect. I record the wrong hypothesis because it was cheap to
refute and because the card asked me to derive what the statistic must be for
each construction before comparing them — I did, got it wrong, and the control
corrected me. That is the protocol working.

---

## 5. The decisive mutation: one line, and it settles T1

`surrogate.py` lines 684–688 build the `NORMMATCH_RANDDIR` arm:

```python
Gx = rngd.normal(size=(N, M_)); Gx /= np.linalg.norm(Gx, axis=1, keepdims=True)
Gy = rngd.normal(size=(N, N_)); Gy /= np.linalg.norm(Gy, axis=1, keepdims=True)
Xr = Gx * np.sqrt(xs2)[:, None]
Yr = Gy * np.sqrt(ys2)[:, None]
```

`Gx` and `Gy` are **two independent draws**. So this arm differs from a dual
family in *two* ways at once: it is not in the lattice, **and its `y` carries no
information about its `x`**. Section 1.6 of the report attributes its null to the
first and reads the result as "the statistic separates a valid dual family from a
norm-identical non-lattice family … the statistic has dynamic range on family
identity". That attribution is untested and it is wrong.

I changed exactly one thing — `y` becomes a deterministic function of `x`:

```
y_i := normalise(Rᵀ x_i) · ‖y_i‖_sieve,   R a fixed random 35×25 matrix
```

Norms are now matched **exactly**, row for row (mean `‖x‖²` 181.5, mean `‖y‖²`
129.1) — a strictly better match than MATCHED_BKZ's +17% / +40%. There is no
lattice, no `A`, no modulus, no sieve.

| arm | in lattice | y = f(x) | clustered | excess |
|---|---|---|---|---|
| producer's NORMMATCH_RANDDIR, replicated | no | **no** | no | **0.9767** |
| mine, coupling only, no clustering | no | **yes** | no | **12.1507** |
| mine, g=30, ε=0.25 | no | yes | yes | 12.0097 |
| mine, g=100, ε=0.10 | no | yes | yes | 11.3516 |
| mine, g=300, ε=0.06 | no | yes | yes | 10.7206 |
| SIEVE (reference) | yes | yes | — | 1.2937 |
| MATCHED_BKZ (reference) | yes | yes | — | 5.4461 |

**A family with no lattice membership at all separates 9.4× harder than the sieve
database.** Clustering is irrelevant across a 300× sweep. The coupling is
everything.

Caveat I state rather than bury: my `y` is real-valued and the map is linear, so
there is no mod-`q` wrapping. That is part of *why* the coupling is so strong —
mod-`q` reduction is what suppresses the angle correlation in a real dual family.
The conclusion is unaffected: lattice membership is neither necessary nor
sufficient to place a family anywhere on this scale, so it is not what the
statistic reads.

**This is not new to the campaign, which is the aggravating part.**
`RT-20260803-d2e23e`'s `counterexample_or_mutation` already states it: *"Sieving
is not necessary for the effect; the lattice is not necessary for the effect; a
deterministic dependence of y on x is sufficient for it"*, with E1 (no lattice,
`y := x[0:25]`) at 17.078 and E2 (dependence removed) at 1.0371. My arm is the
norm-exact version of E1 and agrees with it.

---

## 6. So: is "the sieve is the least separating" real, or an artifact?

**Both, precisely.**

- **Real as a measurement.** I reproduced it on an independently rebuilt
  instrument with an independently written scorer: 1.2937 vs 5.4461 vs 5.4298.
  It is not a bug, not noise, and not a fabrication.
- **An artifact as an observation.** It is `√(1+ρ)` with ρ computable in closed
  form from the two arrays, to 1.3% / 4.4% / 9.6%; ρ is linear in N; a
  non-lattice family beats both; and the ordering ranks *vector-generation
  algorithms by the angle-coherence of their x→y coupling*. It carries no
  information about sieving, about lattice membership, or about candidate-score
  independence.

The producer's own §5 item 1 guessed the right *direction* — "the nearest-plane
families are internally structured, so their x-database is far more coherent" —
and called testing it cheap. It is cheap. It is also already done, above, and it
does not need a batch.

**Applying the card's own artifact test to the new quantity.** What is the
parameter that should destroy it, and what should the measurement do as that
parameter increases? Growth in **N** is *forced* (`√(1+ρ₁N)`, confirmed at 1.1%
and 1.8%) and therefore proves nothing — this is the campaign repeating batch 3's
error one level up. The parameter that *should* destroy ρ, and which nobody has
varied in four batches, is the **dimension d at fixed N**: ρ is a second-moment
covariance and isotropy in higher dimension should shrink it. That is RC-5, it is
the only direction in which this quantity could carry information that transfers
toward scale, and it is untested.

---

## 7. `KN-TECH-9d21c4`, adversarially

The card asked whether the four-part obligation would have caught the three
failures **prospectively**, at design time, not in hindsight. Mode by mode:

- **Mode 1** (batch 1's null that could not fail) — **yes, prospectively.**
  Step 3 asks you to *exhibit* a case where the statistic moves. Attempting that
  for the correct-secret score under row permutation fails in two lines
  (`y_i·(s−s) = 0` for every `i`, whatever sits in row `i`), and the failure *is*
  the discovery. Cheap, forward-looking, decisive.
- **Mode 2** (batch 2's `NULL-V`) — **yes, prospectively.** The
  `maximal_removal_control` — total removal must be at least as extreme as
  partial removal and on the same side — is runnable before you know the answer,
  and `ψ := 0` landing on the opposite side would have fired it.
- **Mode 3** (batch 3's forced excess) — **partially, and here the entry
  overstates itself.** Step 4 says derive the forced value under *"the
  alternative"*. It never asks whether your alternatives **exhaust** the space.
  That is exactly how batch 4 failed: the producer executed step 4 impeccably —
  two named hypotheses, both forced values derived and frozen before the run, a
  mechanical verdict, no re-scoring against a different rule — and got
  `C_NEITHER`, because the operative alternative (coupling strength) was in
  neither branch.

**Verdict: it is a technique, not a narrative — with three corrections owed.**
Modes 1 and 2 carry real prospective catches. The `√(1 + 2Nb²/k)` algebra at
lines 53–56 is correct, non-obvious, and I have now confirmed it empirically for
the first time. The generalisation *"ask which property of the real object causes
the departure from your reference model, then check whether your null preserves
that property"* is the best sentence this campaign has produced.

What is not earned: (i) `confidence: verified_by_execution` — verified by
executing *what*? It was written in batch 4; a retrospective account of batches
1–3 is not execution, and its one live application returned `C_NEITHER`.
(ii) `source_refs` lists `TASK-20260804-7e6b54`, the task that produced it —
provenance, not corroboration. (iii) "Cost of not doing it: four batches of one
campaign" asserts the check would have saved them; unsupported, and batch 4 *did*
the check and still did not answer its question. It should read "the check is
cheap."

And one addition owed — a **fifth obligation**:

> **Alternative exhaustiveness.** Before freezing a decision rule, list every
> archived measurement of the same statistic and verify that at least one named
> outcome is consistent with all of them.

Here that list was E1 17.078, E2 1.0371, E3 5.4349, rowperm 0.1058, `y:=0`
6.19e-15. Reading it would have shown that outcome A ("≈1.32") and outcome B
("≈1.00") were both already excluded by the archive. Reading time, zero compute.
It is the only obligation I can construct that would have caught batch 4 *before*
the batch.

I propose no edit and no status change. Rule 12 is UNMET and UNWAIVED.

---

## 8. The upstream defect

`DEC-20260803-81b778` NA-1 says: *"If it separates at about 1.32, the central
result is lattice membership and the lane is settled. If the sieve separates and
the matched family does not, the red team is wrong."*

`RT-20260803-d2e23e` — the report that **proposed** that control — records in the
same file that its E3, a valid dual family of the same `A` with 0 membership
violations on 447,975 entries and no sieve, separated at **5.4349**. On the day
NA-1 was frozen, the archive already said the answer would be neither 1.32 nor
1.00.

The producer executed the commissioned check faithfully and reported `C_NEITHER`
honestly rather than picking a nearest label. **The design defect is upstream, in
the decision record, and I place it there.**

---

## 9. Snapshot commit message `e8cc366e`

Five prior Coordinator commit messages in this program carried a defect. I was
told to assume a sixth. There is one, and it is two kinds.

**Security-claim audit: NONE FOUND**, and it deserves to be said plainly. I
searched `report.md`, `surrogate.py`, `results.json`, `receipt.json`,
`rebuild_transcript.txt`, `KN-TECH-9d21c4.md` and the commit message for an
ML-KEM break, a security proof, a FIPS 203 parameter set affected or cleared, a
speedup, an exponent, a cost claim, or an `EV-*`/`KN-*` status change. There is
none. Scope banners are first and binding in every artifact,
`states_a_conclusion` is `false`, `rule12_status` is carried everywhere, and the
message reprints the full non-claim paragraph. The producer's eight
self-declarations are real, and one of them corrects the Coordinator's own card.

**Defect 1 — a factual error, and it is the exact error the sentence warns
about.** The message states: *"Real 0.140324 = 7.126x below the iid prediction;
row-permuted 0.106552 = 9.385x below, **against a reference that is strictly
c4(8) = 0.96503 and not 1.0**."* Those factors are `1/0.140324` and
`1/0.106552` — **against 1.0**. Against `c4(8)` they are **6.877×** and
**9.057×**. The producer's report §2 makes the same slip in the paragraph that
insists 1.0 is a 3.5% error, and it has already propagated into
`KN-TECH-9d21c4`'s diagnostic table, where it will be read by agents with no
access to this campaign. OBJ-6.

**Defect 2 — six present-indicative conclusions in a message that opens "I draw
no conclusion."** (a) "outcome B … is EXCLUDED"; (b) "The matched family
separates four times HARDER than the sieve" — *separates* is an interpretation,
not a number, so the every-number-is-the-producer's qualifier does not cover it;
(c) "Outcome A's direction holds but not its magnitude"; (d) "T2, BOTH ARMS FAIL
THE ASSUMPTION UNDER TEST" — a heading that adopts as fact the very framing under
review (see §4.3: `sd_ratio_to_iid` is *not* the assumption under test);
(e) "the registry contradiction RESOLVED … the JSON field is defective" — a
status word plus a judgement on committed evidence, pre-review; (f) "disjoint
from the sieve database BY CONSTRUCTION", where disjointness comes from an
explicit post-hoc filter and the count itself is build-dependent.

`RT-20260803-d2e23e` OBJ-9 raised class (b) **one batch ago** and named the fix —
*"grep the draft message for evaluative adjectives and for any verb in the
present indicative applied to a producer conclusion"*. It was not applied. That
is the durable finding here: the program has the correction and does not run it.

---

## 10. What I am **not** saying

- Not that the measurements are wrong. They reproduce, and on an independently
  rebuilt instrument they reproduce better than the producer claimed.
- Not that the producer misconducted itself. Its `C_NEITHER`, its eight
  self-declarations, its refusal to re-score against a different rule, and its
  explicit flagging of §1.5 as an argument rather than a result are the best
  conduct in this campaign. The blocking objections are interpretive and two of
  them are inherited from a decision record.
- Not that the lane is dead. Closing here would be premature and I refuse it
  under `docs/inventor-protocol.md` §4. I have named an obstruction for **one
  comparison** — the row-permutation excess equals `√(1+ρ₁N)` and ρ is a
  construction property — and that closes that comparison, not the question
  behind it. Forward guidance is RC-3 (measure across-candidate dependence, which
  is what the heuristic actually asserts), RC-4 (adjacent-FFT-bin candidates,
  unmet since batch 3), and RC-5 (vary d at fixed N and ask whether ρ decays).
- Not anything about ML-KEM. Toy scale, one instance, d=60, q=127. No FIPS 203
  parameter set is affected or cleared, no attack exists, no cost is claimed, and
  no security property is asserted in either direction.

## 11. Batch 5, in one line

**CHANGE, not continue and not close.** Decline the producer's recommendation to
chase 1.27 vs 5.43 across instances — that replicates a construction-determined
ordering, which is the failure `KN-TECH-9d21c4` was written to prevent, applied
to a new number. The cheapest check that decides it is **two seconds of numpy**:
make the RANDDIR arm's `Y` a deterministic function of its `X` instead of an
independent draw. I measure 12.15. If it separates, batch 5 goes to RC-3 and
RC-4. If it returns ≈1, I am wrong and the producer's question stands — in which
case chase ρ, not more instances.
