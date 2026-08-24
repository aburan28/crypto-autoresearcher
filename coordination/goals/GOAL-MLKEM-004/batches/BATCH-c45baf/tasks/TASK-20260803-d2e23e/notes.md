# RT-20260803-d2e23e — red team of BATCH-c45baf, what I re-derived

**Reviewed:** snapshot `555a5762` (archiving `TASK-20260803-db170f`), eight files.
**Role:** red team, independent session. **SCOPE: TOY.** m=35, n=25, d=60, q=127.
No ML-KEM break claim, no security proof, no FIPS 203 parameter set affected or
cleared, no speedup, no cost claim. **AGENTS.md rule 12 UNMET and UNWAIVED**: I
change the status of no `EV-MLKEM-*` record and no `KN-*` entry, and propose none.
This document records **observations and objections**. It does not conclude that
any heuristic is validated or refuted.

I did not produce this package and have not repaired it. Nothing was forwarded to
me from the destroyed first attempt (`coordinator_notes/artifact_loss_incident.md`).

---

## 0. What I did, in order

1. Re-read `AGENTS.md`, `docs/inventor-protocol.md`, the card, `EV-MLKEM-50901f`,
   `DEC-20260803-264d6a` (PD-2), and `RT-20260803-dc7568`.
2. Read `stage_a.py` line by line and **derived in closed form what its statistic
   must do under the row permutation**, before looking at the numbers.
3. Recomputed every headline number from `stage_a_results.json` /
   `stage_b_results.json` rather than from `report.md`.
4. **Ran one control experiment of my own** (three ensembles) to test whether the
   separation is a property of the sieve, of the lattice, or of any pairing in
   which `y` is a deterministic function of `x`.
5. Audited the snapshot commit message sentence by sentence.

**Environment.** System `python3` with `numpy 2.4.6`; `fpylll 0.6.4` from
`/tmp/sagevenv-val3fc363` (read-only use of an existing venv — I built no new
venv, and I used **no g6k and no sieve** anywhere). `KN-TECH-14efa5`'s
`Strategy(b) for b in range(41)` fix was required and applied for BKZ, exactly as
the recipe says; `BKZ.EasyParam` was not used. Rebuild recipe therefore exercised
in part (fpylll half only); the g6k half I did not need and did not test.

**Budget.** 1 control run, 96.4 s wall, single-process numpy/fpylll, well under
the card's 1800 s / 4 GB / 1 run. No run was discarded, repeated or unreported.

---

## 1. The closed-form derivation (done before reading the results)

Every score in `stage_a.py` is

```
score_j(e) = (1/N) Σ_i cos( 2π (x_i·e + y_i·(s − c_j)) / q )
```

For a near-miss candidate `c_k = s + e_k` the phase offset is `y_i·(s−c_k) = −Y[i,k]`.
Two facts follow immediately, and neither depends on any measurement.

### 1.1 Under the real pairing the near-miss score is one Fourier coefficient

Lattice membership is `Y[i,k] = a_k·x_i mod q` with `a_k = A[:,k]`. Substituting,

```
score_k(real) = (1/N) Σ_i cos( 2π (e − a_k)·x_i / q )  =  F(e − a_k),
F(t) := (1/N) Σ_i cos(2π t·x_i / q),      score_correct = F(e).
```

So the eight near-miss scores are **the same function `F` sampled at eight
frequencies shifted by columns of `A`**. And `a_k` is not a generic frequency for
this database: `a_k·x_i = Y[i,k]` is *small for every emitted vector*, because the
vector is short — measured `mean‖y‖² = 129.5` over n=25, i.e. rms 2.28 per
coordinate. `a_k` is, by construction of a dual vector, a frequency at which the
database is coherent.

Consequence: the cross-moment `(1/N) Σ_i g(y_i) h(x_i)` converges as `N→∞` to a
**non-zero ensemble limit**, not to the product of marginals. The across-candidate
spread therefore has an **N-independent floor**.

### 1.2 Under the row permutation it is a product of marginals

```
E_π[ score_k^π ] = ⟨cos u⟩·⟨cos φ_k⟩ − ⟨sin u⟩·⟨sin φ_k⟩,   u_i = 2πx_i·e/q.
```

A product of two separately-averaged marginals. It has **no** N-independent
cross term, so its across-candidate spread decays as `N^{-1/2}` and its ratio to
the iid prediction `sqrt(0.5/N)` is **flat in N**.

### 1.3 The two predictions, and the measured values

| prediction, derived a priori | measured |
|---|---|
| surrogate sd-ratio flat in N′ | 0.105557 / 0.106222 / 0.106614 / 0.106552 — flat, range **0.001058** |
| real sd-ratio = `sqrt(2A² + 2B²N′)`, i.e. excess = `sqrt(α + βN′)` | see §1.4 |
| excess > 1 and increasing in N′ | 1.0146 / 1.0434 / 1.1480 / 1.3169 |

The **sign and the growth were both fixed before the data were consulted.**

### 1.4 The decay curve contains exactly one number

Fit `excess(N′) = sqrt(α + βN′)`, forcing `α := 1` (the two arms must coincide
when sampling noise dominates) and taking `β` from the **single** N′=17919 point:

```
β = (1.3169² − 1)/17919 = 4.0981e-05
pred   1.0102  1.0402  1.1523  1.3169
obs    1.0146  1.0434  1.1480  1.3169
resid −0.0044 −0.0032 +0.0043   0.0000
resid / across-instance sd:  −0.12  −0.18  +0.14  0.00
```

A free two-parameter least squares returns `α = 1.0053`, i.e. the forced value.
**Four points, one degree of freedom, every residual under 0.2σ.** The "monotone
increase" is not four independent confirmations of anything; it is the shape
`sqrt(1+βN)` that *any* constant across-candidate bias plus `1/√N` noise must
produce. Its entire information content is the single number β.

---

## 2. The control experiment — is it the sieve, the lattice, or `y = f(x)`?

One script, `rt_controls.py`
(`sha256 220aabdbeeb0a59bf6409767474912feee6948685c525745703e71c9254aec1b`,
results `86cc35be6ee7d4e782337b17188b08e0fca935124ef07bf0c0fd67178b9d02a2`),
reproducing `stage_a.py`'s statistic exactly (same phase construction
`mod(Y·(s−C), q)`, same per-draw sd-across-group ÷ `sqrt(0.5/N)`, same
correct−best-of-group, same within-subsample permutation for the decay sweep;
800 draws, 5 row-permutation realisations, N = 17919). Three ensembles:

- **E1 — deterministic dependence, NO lattice, NO sieve, NO `A`, NO modulus in the
  construction of `y`.** `x ~` iid rounded Gaussian in `Z^35` with per-coordinate
  variance matched to the real `a_x`; **`y := x[0:25]`.** This matches the real
  data's `a_x` and `a_y` almost exactly by accident of arithmetic
  (real `mean‖x‖²/m = 181.5/35 = 5.19`, `mean‖y‖²/n = 129.5/25 = 5.18`):
  measured `a_x = 0.904` vs the real 0.888, `a_y = 0.161` vs the real 0.158.
- **E2 — null of the control.** Identical marginals, dependence removed at the
  source: `y := x′[0:25]` for an **independent** draw `x′`.
- **E3 — valid dual lattice, non-sieve route.** The **real `A`** of
  BATCH-f75059 replicate 0 (seed 20260803206), the real dual basis, fpylll
  LLL + BKZ-30 (6 loops), family = the 17919 shortest sparse ±1 combinations of
  the reduced basis. **0 lattice-membership violating entries** on
  17919 × 25 = 447,975 checked by integer arithmetic. Norm profile does **not**
  match the sieve's (`mean‖x‖² = 470.5` vs 181.5, `mean‖y‖² = 331.5` vs 129.5), so
  levels are not comparable; the presence/absence of separation is.

### Results

| ensemble | uniform excess | secret-dist excess | **near-miss excess** | near-miss decay, N′ = 500/2000/8000/17919 |
|---|---|---|---|---|
| **real data** (producer) | 1.0087 | 1.0254 | **1.3169** | 1.0146 / 1.0434 / 1.1480 / **1.3169** |
| **E1** no lattice, `y := x[0:25]` | 0.9833 | 1.4801 | **17.078** | 3.050 / 6.045 / 11.207 / **17.157** |
| **E2** same marginals, independent | 1.0090 | 0.9977 | **1.0371** | 1.010 / 1.019 / 1.007 / **1.059** |
| **E3** valid lattice, BKZ, no sieve | 1.0073 | 1.7095 | **5.4349** | 2.487 / 3.536 / 4.895 / **5.540** |

E1's row-permuted near-miss sd-ratio is **0.1082**, against the real data's
**0.1066** — the surrogate arm lands in the same place for an object with no
lattice in it at all, because §1.2 says it must.

E1's decay obeys the same one-parameter law: `sqrt(1+βN′)` with β from the last
point alone predicts 3.031 / 5.809 / 11.488 / 17.157 against the observed
3.050 / 6.045 / 11.207 / 17.157.

### What this settles

- **E1 reproduces the entire qualitative pattern** — separation, direction, the
  monotone increase in N′, the flat surrogate, *and* the graded internal contrast
  (uniform none < secret-distribution intermediate < near-miss largest) — using an
  object containing **no lattice, no sieve, no LWE instance, no `A`, and no modular
  arithmetic in the construction of `y`**. Whatever the row-permutation null
  detects, it is detected by `y := x[0:25]`.
- **E2 shows my instrument is not broken.** Same marginals, dependence removed:
  no separation, flat decay. So the statistic *can* return null.
- **E3 shows it is not about sieving.** A valid dual-vector family from a pure
  enumeration route separates *more strongly* than the sieve database.

### Distance sweep (E3), candidates `c = s + δ·e_k`

| δ | 1 | 2 | 3 | 4 | 5 | 8 | 16 |
|---|---|---|---|---|---|---|---|
| excess (sd-ratio) | 5.358 | 5.044 | 5.023 | 4.484 | 4.010 | 2.925 | 1.284 |
| real sd-ratio | 1.304 | 2.354 | 3.604 | 4.287 | 4.798 | 4.432 | 1.352 |

The excess is a smooth decreasing function of how far the candidate sits from the
secret. Together with `VAL-20260803-124629`'s Hamming-distance control
(`EV-MLKEM-50901f` OBS-5: 0.146 / 0.213 / 0.234 / 0.325 / 0.352 / 0.352 at
distance 1/2/3/5/8/12) this makes the three-group "internal contrast" one curve
sampled at three points, not three independent facts.

---

## 3. What the heuristic's own null says, and nobody reported it

The dual-attack independence heuristic's own null object is **not** a
row-permuted database. It is *scores of wrong candidates iid `N(0, 1/2N)`*, which
is exactly the denominator `sqrt(0.5/N)` already in the code. Against that null:

- Stage A near-miss, real arm: **0.140** — a factor **7.1 below** iid.
- Stage A near-miss, row-permuted arm: **0.107** — a factor **9.4 below** iid.

Both arms violate the heuristic's own null by ~7–9×. The campaign's headline
1.3169 is the **ratio between two objects that both fail the reference model**,
and it is the one part of the comparison that §1 shows is fixed a priori.

Meanwhile, Stage B's raw real-arm sd-ratios under the **principled** candidate
definition (adjacent FFT bins, which is what a real dual attack enumerates) are
**1.074 / 1.049 / 0.989** for p = 2/3/5 — consistent with the iid prediction.
That comparison needs **no surrogate and no null**, so the producer's (correct)
PD-2 refusal to report Stage B's *null* does not block it, and it was not
reported. The producer's own OBS-B1 says the 7× concentration is a property of
the ad-hoc `s + e_k` definition; §2's E1 says the row-permutation excess on that
family is also not about lattices.

---

## 4. Numeric audit — everything I recomputed

All from the archived JSON, not from `report.md`.

| quantity | report | recomputed | status |
|---|---|---|---|
| near-miss sd-ratio excess pooled | 1.3169 ± 0.0188, z = +50.6, 9/9 | 1.316946 ± 0.018811, z = 50.546, 9/9 above | reproduced |
| near-miss correct−best excess | 0.8893 ± 0.0115, z = −28.8, 9/9 | 0.889292 ± 0.011549, z = −28.757, 9/9 below | reproduced |
| near-miss real / rowperm levels | 0.140324 / 0.106552 | identical | reproduced |
| uniform excess (sd-ratio) | 1.0087 ± 0.0192, z = +1.37, 5/9 | 1.008741 ± 0.019188, z = 1.367, 5 of 9 | reproduced |
| secret-dist excess | 1.0254 ± 0.0113 (z +6.78), 1.0238 ± 0.0022 (z +32.4) | identical | reproduced |
| decay excess | 1.0146 / 1.0434 / 1.1480 / 1.3169 | identical | reproduced |
| surrogate "flat to within 0.001 over 36×" | 0.001 | **0.001058** over 35.8× | reproduced with correction (0.00106, not ≤0.001) |
| per-instance monotone from N′=2000 | 9/9 | 9/9 (500→2000 is 7/9; correctly qualified) | reproduced |
| 8 of 9 above 1 at N′=500 | 8/9 | 8/9 (rep 0 = 0.9292) | reproduced |
| provenance `a_x` agreement | 0.00e+00 on all nine | `a_x_abs_difference = 0.0` exactly, all nine; seeds and N match | reproduced |
| certificates | 4,031,775 entries, 0 violations, 0 zero, 0 dup-y | 9 × 447,975 = 4,031,775; all zero | reproduced (arithmetic; I did not re-run the sieve) |
| SENS-0 invariance | max |Δ| = 0.0 | 0.0 on all nine | reproduced |
| fast-route vs modular route | 3.1e-14 | 3.12e-14 (rep 0; `null` on reps 1–8 — checked once, as coded) | reproduced |
| SENS-2 fails |z|>5 on sd-ratio | z = 3.21 | producer-reported; not independently recomputed | unable_to_check (would need the raw per-draw series, not archived) |
| Stage B near-miss excess p=2 | 0.9607 ± 0.0187, "within one to two sd of 1" | 0.9607 ± 0.0187, but **Stage A's own z convention gives z = −3.64**, 3/3 below 1 | reproduced with correction |
| Stage B `Nf` line-540 identity 15 = 25−10−0 | admissible | arithmetic checks; **I did not run the pinned estimator** | unable_to_check (estimator callable not exercised in my session) |
| Stage B 2^11.391 ML-KEM-512 figure | modeled | not recomputed | unable_to_check |
| cross-statistic independence | presented as two confirmations | Pearson r across the 9 instances = **−0.9387** | **not_reproduced as two independent confirmations** |

The last row matters: the per-instance sd-ratio excess and correct−best excess
correlate at r = −0.94. They are two views of one quantity — extra per-draw spread
across the eight near-miss candidates mechanically raises `max_k` and so lowers
`correct − max_k`. "9/9 on both statistics" is 9/9 on one.

---

## 5. Snapshot commit message audit (`555a5762`)

The message opens *"UNREVIEWED. Every number below is the producer's, stated as
the producer's, pending two independent reviews. **I draw no conclusion from them
here.**"* That framing is good and mostly held. Four places break it:

1. **"THE PRODUCER DECLARES ITS OWN STAGE B NULL INADMISSIBLE, and that is the
   most encouraging thing in this package."** — an evaluative conclusion, in a
   message that promises none, about material still pending review.
2. **"The rule adopted last batch worked."** — a conclusion about the harness's own
   corrective rule (PD-2), stated as established, pre-review. It is also the
   Coordinator grading its own prior decision.
3. **"STAGE A: the ... separation REPLICATES on 9 of 9 instances"** — `REPLICATES`
   is an interpretation, not a number, so the "every number below is the
   producer's" qualifier does not cover it. The producer's own report.md scoped
   this ("nine instances of one design at dimension 60"); the commit's headline
   sentence does not carry that scope until three paragraphs later.
4. **"the nine instances are provably BATCH-f75059's own"** — `provably` overstates
   a reproduction check. `a_x` agreement at 0.0 across nine instances is strong
   evidence of pipeline reproduction; it is not a proof of instance identity.

**No security claim found.** I searched `report.md`, `stage_a.py`, `stage_b.py`,
both results JSONs, `receipt.json` and the commit message for an ML-KEM break, a
security proof, a FIPS 203 parameter set affected or cleared, a speedup, a cost
claim, or an `EV-*`/`KN-*` status change. **None.** The scope banners are present,
first, and binding; `states_a_conclusion` is `false` in both results files;
`rule12_status` is carried in every artifact. This is the cleanest scope
discipline in the campaign so far and I want that on the record.

**One dropped qualifier.** At the point of use the commit says the adjacent-bin
term is "MODELED ... with the ML-KEM-512 reference reproducing at 2^11.391". The
producer attached, at that exact number, *"This is arithmetic inside a cost model
at FIPS 203 parameters. It is not a measurement, not an extrapolation of anything
this task measured, and asserts nothing about ML-KEM's security. Rule 4 applies in
full."* The commit carries a global non-claim paragraph later but drops that
local disclaimer. Minor, and the global catch works; recorded because the card
asked specifically for dropped qualifiers.

**What the commit did NOT do wrong, and should be credited with:** it reports the
producer's self-declared weaknesses (SENS-2 failing on the sd ratio, 3 instances
not 9, the aggregation rule not being Coordinator-pre-registered) in the message
itself. That is new in this campaign.

---

## 6. Stage B — did the tuple buy testability?

**Partly, and the producer's caution was correct but incomplete.**

- It bought a real structural improvement: because `k_lat < n`, the correct bin's
  score is no longer invariant under the row permutation (SENS-0 does not apply),
  and it measurably moves (paired |z| median 14.8–31.3). Batch 2's design could
  not do that. This is genuine.
- It did **not** buy a group-level statistic with demonstrated sensitivity, and
  the producer says so and refuses the blindness reading. **That refusal is
  correct** and I endorse it under PD-2.
- But the producer stopped one step early. The group-level excesses are **not**
  consistent with noise under the producer's *own* Stage A z convention: p=2
  near-miss sd-ratio gives z = −3.64 with 3/3 below 1, and correct−best gives
  z = +3.29 with 3/3 above 1 — **both in the opposite direction to Stage A**.
  The producer's phrase "within about one to two across-instance sd of 1" silently
  switches from the Stage A yardstick (sd/√n) to a weaker one (sd). Using the
  strict yardstick where the answer was null and the loose one where it was
  positive is the asymmetry to watch, even though I agree the p=2 result should
  **not** be reported as a finding at n=3 with no sensitivity demonstration.
- And the power question was never asked. With across-instance sd ≈ 0.019 at
  n = 3, a Stage-A-sized 32% excess would sit at roughly 30σ. So Stage B's null is
  **not** a power failure. It is a sensitivity question, and only a sensitivity
  question. Saying that costs nothing and is more informative than silence.

---

## 7. Scale (card item 6)

Nothing in this package bears on cryptographic parameters, and the package does
not claim it does. For the record, transfer would need at least:

- **HX-1** that a separation measured at d=60, q=127, one sieve, one modulus
  persists at ML-KEM dimensions — untested, and `EV-MLKEM-50901f` OBS-4 already
  records one correction in this campaign behaving *oppositely* as scale grows;
- **HX-2** that the `s + e_k` candidate family has an analogue in a real dual
  attack — **the producer's own OBS-B1 says it does not**: under adjacent FFT bins
  the concentration vanishes (sd ratio ≈ 1.0);
- **HX-3** that the row-permutation surrogate is a null for the independence
  heuristic — **§1 and §2 say it is not**, at any scale.

I assert none of these as heuristics; I name them so that the gap is explicit
rather than implied. HX-3 is not a scale problem — it fails at toy scale already.

---

## 8. `rt_controls.py` (verbatim record of the control I ran)

Kept in session scratch, not in the repository (write scope is two files). Full
source is reproduced here so the check is rebuildable from this record alone.
Invocation: `/tmp/sagevenv-val3fc363/bin/python3 rt_controls.py`, exit 0, 96.4 s.

Key excerpts — the statistic (identical in form to `stage_a.py`
`per_draw_series` / `group_stats`) and the three ensembles:

```python
def phases(Y, s, C):
    """Phi[i,j] = 2 pi (y_i . (s - c_j) mod q)/q -- exactly stage_a.py line 410."""
    D = np.mod(Y.dot((s[None, :] - C).T), Q).astype(np.float64)
    return TWOPI * D / Q

# per draw: sd across the group / sqrt(0.5/N) ; and correct - max over the group
    iid = np.sqrt(0.5 / N)
    for g, idxs in gid.items():
        gm = means[:, idxs]
        ratio = gm.std(axis=1, ddof=1) / iid
        dbest = means[:, 0] - gm.max(axis=1)

# E1  deterministic dependence, no lattice at all
sd_coord = np.sqrt(181.49 / M)          # match the real mean||x||^2 = 181.49
X1 = np.rint(rng.normal(0.0, sd_coord, size=(N_TARGET, M))).astype(np.int64)
Y1 = X1[:, :N_].copy()                              # y := f(x), DETERMINISTIC
# E2  same marginals, dependence removed at the source
Xp = np.rint(rng.normal(0.0, sd_coord, size=(N_TARGET, M))).astype(np.int64)
Y2 = Xp[:, :N_].copy()
# E3  valid dual lattice of the REAL A, fpylll LLL + BKZ-30, NO g6k, NO sieve
par = BKZ.Param(block_size=30, strategies=[Strategy(b) for b in range(41)],
                max_loops=6, flags=BKZ.MAX_LOOPS)
...
bad = int(np.count_nonzero(np.mod(X3.dot(A) - Y3, Q)))   # -> 0
```

Console output, verbatim:

```
[    0.0s] E1/E2: synthetic, no lattice
[    9.7s] E1 done
[   19.3s] E2 done
[   19.3s] E3: valid dual lattice, fpylll BKZ, NO sieve
[   19.9s]   BKZ-30 done, ||b0||^2 = 255
[   50.1s]   family N=17919  membership violating entries=0  mean||x||^2=470.5 mean||y||^2=331.5
[   60.4s] E3 done
[   60.4s] E3 distance sweep
[   65.7s]   delta= 1  excess_sd=5.3581  excess_cb=37.4862  real_sd_ratio=1.3037
[   71.0s]   delta= 2  excess_sd=5.0436  excess_cb=-5.2623  real_sd_ratio=2.3542
[   76.0s]   delta= 3  excess_sd=5.0234  excess_cb=-1.7452  real_sd_ratio=3.6038
[   81.2s]   delta= 4  excess_sd=4.4835  excess_cb=-0.8474  real_sd_ratio=4.2866
[   86.0s]   delta= 5  excess_sd=4.0102  excess_cb=-0.2768  real_sd_ratio=4.7982
[   91.3s]   delta= 8  excess_sd=2.9252  excess_cb=0.4577  real_sd_ratio=4.4318
[   96.4s]   delta=16  excess_sd=1.2837  excess_cb=0.9514  real_sd_ratio=1.3516
[   96.4s] E1_det_dependence_no_lattice       a_x=0.904 a_y=0.161
[   96.4s]    uniform               real_sd=1.0436 rp_sd=1.0613 EXCESS=0.9833 | cb_excess=0.9997
[   96.4s]    secret_distribution   real_sd=8.0834 rp_sd=5.4612 EXCESS=1.4801 | cb_excess=0.5983
[   96.4s]    near_miss             real_sd=1.8476 rp_sd=0.1082 EXCESS=17.0777 | cb_excess=-6.9786
[   96.4s]    decay(near_miss): N'=500 ex=3.0502  N'=2000 ex=6.0454  N'=8000 ex=11.2073  N'=17919 ex=17.1567
[   96.4s] E2_same_marginals_independent      a_x=0.904 a_y=0.162
[   96.4s]    uniform               real_sd=1.0043 rp_sd=0.9953 EXCESS=1.0090 | cb_excess=0.9993
[   96.4s]    secret_distribution   real_sd=5.4807 rp_sd=5.4931 EXCESS=0.9977 | cb_excess=1.0025
[   96.4s]    near_miss             real_sd=0.1123 rp_sd=0.1083 EXCESS=1.0371 | cb_excess=0.9804
[   96.4s]    decay(near_miss): N'=500 ex=1.0100  N'=2000 ex=1.0187  N'=8000 ex=1.0070  N'=17919 ex=1.0587
[   96.4s] E3_valid_lattice_bkz_no_sieve      a_x=2.303 a_y=0.406
[   96.4s]    uniform               real_sd=0.9900 rp_sd=0.9828 EXCESS=1.0073 | cb_excess=0.9775
[   96.4s]    secret_distribution   real_sd=3.4793 rp_sd=2.0352 EXCESS=1.7095 | cb_excess=0.7847
[   96.4s]    near_miss             real_sd=1.2727 rp_sd=0.2342 EXCESS=5.4349 | cb_excess=43.7272
[   96.4s]    decay(near_miss): N'=500 ex=2.4867  N'=2000 ex=3.5362  N'=8000 ex=4.8947  N'=17919 ex=5.5400
```

**Limits of my own control, stated plainly.** E1's coupling (`y` literally a
sub-vector of `x`) is far stronger than a lattice's, which is why its excess is
17 and not 1.32 — I do not claim to have reproduced the *magnitude*, only the
sign, the growth law, the flat surrogate and the group ordering. E3's norm
profile is 2.6× the sieve's, so its levels are not comparable either. Three
ensembles, one instance each, one seed each, one statistic. Everything here is at
toy scale and none of it is a statement about ML-KEM.

**What would falsify my objection.** A surrogate that preserves `y = A^Tx mod q`
exactly — a *different* valid dual-vector family from the same lattice with the
sieve's norm profile matched — showing **no** separation, while the sieve database
does. E3 is the cheap version of that and it separated; a norm-matched version is
the definitive one and is objection 1's cheapest check.

---

## 9. Closure discipline

I am not closing this lane. Objection 1 says the row-permutation comparison cannot
distinguish the campaign's hypothesis from `y = A^Tx mod q`; it does **not** say
the independence heuristic holds, that no measurable structure exists, or that the
question is dead. The obstruction is named (the surrogate's contrast is fixed by
the definition of a dual vector), the argument is in §1 and §2, and §10 of
`report.yaml` names what remains open and testable. Per
`docs/inventor-protocol.md` §4 a negative reading of a measurement carries the
same burden as a positive one, and I have tried to carry it.
