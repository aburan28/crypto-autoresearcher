# RT-20260803-4064e1 — what I re-derived

Red Team, TASK-20260803-bc2f41, BATCH-d2a728 (1 of 6), GOAL-MLKEM-004.
Reviewing snapshot commit `8cc51677`, package `TASK-20260803-e53ce2`.

Independent session. I did not produce this package and did not modify it.
Everything below was computed by code I wrote, in
`/tmp/claude-0/-home-user-crypto-autoresearcher/5cc33d08-b894-5d89-8a26-7f062c61725d/scratchpad/`
(`rt1_load.py` … `rt8_repro.py`), reading only the archived artifacts and the
pinned lattice-estimator source. One measurement run was used
(`rt8_repro.py`, the sieve reproduction), within `budget.maximum_runs: 1`.

**Nothing in this report is a finding about ML-KEM, about FIPS 203 parameter
sets, or about the security of anything. AGENTS.md rule 12 remains UNMET and
UNWAIVED; no `EV-*` or `KN-*` status is touched.**

---

## 0. Full independent reconstruction of the measured object

The producer's limitation 5 says the dual vectors `(x,y)` are absent from
`raw_scores.json`, so "a reviewer ... cannot score a *new* candidate of their
own choosing directly from the JSON." That is true as written but understates
what the archive determines. I recovered every vector:

1. **`y` by linear algebra.** For candidate `c`, the emitted phase is
   `t_i(c) = x_i·b − y_i·c (mod q)`, so
   `t_i(c_0) − t_i(c_j) = y_i·(c_j − c_0) (mod q)`. The 32 candidate
   differences contain 25 that span `Z_q^25` (uniform_00…15,
   secretdist_00…07, nearmiss_00). Inverting that 25×25 system mod 127 gives
   `y_i` for all 17,919 vectors. Because `‖y‖² ≤ 242`, the centred
   representative is the true integer vector.
   **Check: recovered `‖y‖²` equals the emitted `norm2_y` for all 17,919.**
   Independent cross-check: near-miss candidate `k` differs from `s` by `+1`
   in coordinate `k`, so `t(correct) − t(nearmiss_k) = y[k]` directly; agrees
   with the solve for `k = 0,1,2`.

2. **`x` by BDD.** `x` satisfies `xᵀA ≡ y (mod q)` with `‖x‖² ≤ 282`, while
   the kernel lattice `{x : xᵀA ≡ 0}` (rank 35, det `q^25`) has shortest
   BKZ-20 row of norm² 2450 (‖·‖ ≈ 49.5). So `x` is the unique short
   solution. Particular solution from a 25×25 invertible row block of `A`,
   then Babai nearest-plane on a BKZ-20 basis of the kernel.
   **Check: `‖x‖²` equals the emitted `norm2_x` for all 17,919/17,919, and
   `xᵀA ≡ y (mod q)` for all.**

3. **`rt8_repro.py` — my own pipeline, from the declared seeds.** Regenerating
   `A`, `s`, `e` from `numpy.default_rng(20260803001)`, building the same dual
   basis, `LLL` with `FPLLL` seed 20260803005, then
   `Siever(..., seed=0x6D4C4B454D).bgj1_sieve()`:
   - regenerated `A`, `s`, `e` all equal the archived ones;
   - db size 17,919; `‖v‖²` min 218 / median 315 / max 329;
   - **the `(x,y)` multiset is identical to the one I reconstructed in steps
     1–2.**

So the measurement is fully reproducible, the certificate is genuine, and the
scored objects really are `bgj1_sieve` output. The archive is *accidentally*
complete: recoverability depends on the candidate differences happening to
span `Z_q^n`. That should not be relied on (OBJ-3).

---

## 1. Arithmetic reproduction (`rt1_load.py`)

- `raw_scores.json`: 21,036,537 bytes, sha256 `892991c4…3642` — matches
  `results.json` and report §3.
- All 96 per-candidate means across the 8 targets recomputed from
  `phases_t` via `cos(2π t/q)`: max |difference| vs `results.json`
  **4.98e-07** (the emitted-cosine rounding to 6 dp).
- All 8 ranks reproduced: MAIN 1/33, NULL 18/33, DECAY 1/1/1/3/4 and
  uniform-error 1/5.
- Emitted `scores_cos` equals `cos(2π·phases_t/q)`: max |diff| 4.87e-07.
- `MAIN` correct-secret phase equals the separately emitted `x_dot_e_main`
  for all 17,919 entries.
- `x·e`: sd **25.6328**, range **[−63, +63]**, **76.6895 %** with
  `|x·e| < q/4`. Error vector: empirical sd **1.9285**, `‖e‖∞ = 4`.
- `norm2_x + norm2_y = norm2_v` for every vector.
- MAIN group table reproduced exactly: correct +0.42738; near-miss n=8
  +0.42496 (sd 0.00108); secret-dist n=8 +0.29062 (sd 0.02396); uniform n=16
  +0.00385 (sd 0.00606). NULL group table likewise.
- Null "−0.04 empirical sd from the wrong-candidate mean":
  (0.003298 − 0.003473)/0.004724 = **−0.037**.
- `states_a_finding: false`, `compared_against_assumed_law: false`:
  `measure_scores.py` imports no estimator and computes no comparison. True.

Every quantitative claim in report.md §2–§4 that I could check reproduces.

---

## 2. What `MATZOV.Nf` actually asserts (pinned estimator, commit `3e48ef4`)

```
N = exp(4·(lσ_s·π/q)²) · (k_enum·H(X_s) + k_fft·log p + log(1/μ)),   μ = 0.5
lσ_s = σ_e^{m/(m+k_lat)} · (σ_s·q)^{k_lat/(m+k_lat)} · √(4/3) · √(β_sieve/2πe)
       · δ(β_bkz)^{m+k_lat−β_sieve}
```

Two separable assertions, and it matters which one batch 2 tests:

- **(A) a per-vector advantage law.** `exp(4(lσπ/q)²) = adv^{−2}` with
  `adv = exp(−2π²ℓ²/q²)` and **one** length `ℓ` for all `N` vectors.
- **(B) an independence/union-bound law.** `N` grows only logarithmically in
  the number of candidates, i.e. wrong-candidate scores are treated as
  independent of the correct one and of each other.

(B) is the Ducas–Pulles-contested structure. Note also the second factor
`exp(k_fft/3·(σ_s·π/p)²)`, whose entire job is the loss from rounding the
secret onto an FFT grid of modulus `p` — the *adjacent-candidate* penalty.

---

## 3. Does the pipeline measure the object the law is about?

### 3.1 Where it does — the per-vector advantage law (A) AGREES

`rt5_controls.py` §I, zero new runs, conditioning the same database on `‖x‖²`:

| `‖x‖²` decile | count | measured mean | `exp(−2π²σ²‖x‖²/q²)` | ratio |
|---|---|---|---|---|
| 74–144 | 1729 | +0.54168 | 0.52908 | 1.024 |
| 144–157 | 1726 | +0.49641 | 0.47921 | 1.036 |
| 157–167 | 1882 | +0.44726 | 0.45306 | 0.987 |
| 167–175 | 1741 | +0.45928 | 0.43410 | 1.058 |
| 175–183 | 1861 | +0.44250 | 0.41730 | 1.060 |
| 183–190 | 1717 | +0.42393 | 0.40233 | 1.054 |
| 190–198 | 1848 | +0.40877 | 0.38794 | 1.054 |
| 198–207 | 1803 | +0.37315 | 0.37242 | 1.002 |
| 207–219 | 1818 | +0.35946 | 0.35422 | 1.015 |
| 219–282 | 1794 | +0.32907 | 0.32345 | 1.017 |

No trend across a 3.8× range of `‖x‖²`; the residual is a common
multiplicative offset (this single error draw sits +6.1 % above the
resampled mean, see §3.3). `corr(‖x‖², per-vector score) = −0.1056`, correct
sign and magnitude. **The exponent's functional form is confirmed to ~2 %,
and this is a far stronger test than the six-point σ sweep, on data already
emitted.**

The σ sweep agrees too, once given error bars (`rt5_controls.py` §G, 600
fresh error draws per σ against the same db):

| σ | package single draw | resampled mean ± 1 sd | model | package draw |
|---|---|---|---|---|
| 0.5 | +0.94924 | +0.92982 ± 0.01690 | 0.94592 | +1.15 sd |
| 1.0 | +0.84115 | +0.78620 ± 0.04582 | 0.80097 | +1.20 sd |
| 2.0 | +0.42738 | +0.40292 ± 0.08564 | 0.41466 | +0.29 sd |
| 4.0 | +0.01827 | +0.03155 ± 0.02918 | 0.03334 | −0.45 sd |
| 8.0 | +0.00464 | +0.00006 ± 0.00535 | 0.00001 | +0.86 sd |

Nothing in the decay sweep is in tension with the law — including the
apparent factor-2 shortfall at σ=4 (0.018 measured vs 0.033 model), which is
−0.45 sd of the error-draw distribution and is noise.

### 3.2 Where the union-bound law (B) is testable, and what it says

`rt7_which.py`, bootstrap subsamples of the emitted MAIN score arrays,
2000 trials per cell, success = correct secret beats the stated wrong set:

| N′ | vs 16 uniform | vs 8 secret-shaped | vs 8 near-miss | vs all 32 |
|---|---|---|---|---|
| 25 | 0.887 | 0.623 | 0.013 | 0.005 |
| 100 | 1.000 | 0.963 | 0.021 | 0.021 |
| 400 | 1.000 | 1.000 | 0.088 | 0.088 |
| 1600 | 1.000 | 1.000 | 0.259 | 0.259 |
| 6400 | 1.000 | 1.000 | 0.645 | 0.645 |
| 17919 | 1.000 | 1.000 | 0.834 | 0.834 |

`MATZOV.Nf` at this configuration: `a_x ≡ 2(ℓπ/q)² = 0.8902`, so
`exp(4(ℓπ/q)²) = 5.93`, and with the log-term read as
`log(1/μ) + log(#candidates=33) = 4.190` the law predicts **N ≈ 25**.
Against the uniform candidate population — the one its independence
assumption describes — that prediction is **correct**: 0.887 at N′=25,
1.000 at N′=100. Against the near-miss population it is short by ≥700×.

Per-vector correlation between the correct and a near-miss score array is
**0.9909**. The near-misses, not the modulus or the dimension, set the
sample requirement.

### 3.3 Where the design measures something the law does not model

`rt4_stats.py` §B, 2000 fresh error draws against the same database:

- correct-secret mean over draws **+0.4029**, sd **0.0856** (21 % relative);
- iid prediction for that sd: `√(0.3325/17919) = 0.00431`;
- **variance inflation 411×, `N_eff` ≈ 44 against N = 17,919.**

`MATZOV.Nf` treats the signal as deterministic `N·adv`. It is not: it has a
21 % relative sd at this configuration. **But see §4 — this is a controlled
null, not a finding about sieves.**

Wrong-candidate noise, 2000 draws (`rt4_stats.py` §C):

| candidate population | mean | sd | iid sd `√(1/2N)` | ratio |
|---|---|---|---|---|
| uniform `Z_q^n` | +0.00010 | 0.005275 | 0.005282 | **1.00** |
| centred binomial η=2 | +0.28806 | 0.025453 | 0.005282 | **4.82** |

For uniform candidates the independence model is exact. For secret-shaped
candidates the noise is centred at +0.288, not 0, and is 4.8× wider. The
offset is not a defect: `exp(−a_y) = 0.728` with
`a_y = 2π²·Var(s−c)·⟨‖y‖²⟩/q² = 0.317` predicts it (measured ratio 0.674).
It is the `k_fft·log p` regime of the law showing up with no `p` to charge it
to.

---

## 4. The null-object control the package does not contain

The delivered null replaces `b` by uniform in `Z_q^m`. For any fixed nonzero
`x`, `x·b` is then uniform mod `q`, so every phase is uniform and every mean
score is 0 in expectation. **That null cannot fail unless the scoring code
ignores `b`.** It removes the LWE structure; it leaves the sieve database —
the object whose independence `MATZOV.Nf` asserts — completely untouched.

`rt5_controls.py` §F ran the null object of the shape this goal needs: the
same target and scoring, with the sieve vectors replaced by a random-model
surrogate of matched `‖x‖` distribution.

| vector population | mean | sd over e | inflation vs iid | `N_eff` |
|---|---|---|---|---|
| sieve db (bgj1, dim 60) | +0.40931 | 0.08957 | 467× | 38 |
| random directions, matched `‖x‖` | +0.40123 | 0.08572 | 286× | 63 |
| iid phases (the literal `Nf` model) | +0.41474 | 0.00433 | 1.3× | 13,903 |

`rt6_law.py` §L, surrogate only, `a_x` held fixed:

| m | N | sd over e | `N_eff` |
|---|---|---|---|
| 35 | 17,919 | 0.08996 | 40 |
| 70 | 17,919 | 0.05911 | 94 |
| 140 | 17,919 | 0.04498 | 154 |
| 280 | 17,919 | 0.03013 | 402 |

and at m=35, sd over e = 0.08532 / 0.09173 / 0.08825 / 0.08828 for
N = 1,000 / 5,000 / 17,919 / 60,000.

**Reading.** `N_eff` grows roughly linearly in `m` and is *independent of N*:
adding vectors does not reduce the signal's fluctuation at all, because the
statistic is a function of an `m`-dimensional random `e`. The random-vector
surrogate reproduces the effect to within a factor 1.6. So with respect to
the hypothesis "*sieve* correlations break the independence assumption",
this is a **controlled null** (inventor protocol §3): the effect is a
small-`m` property of any vector family. With respect to the weaker
statement "the law's determinstic-signal treatment is not exact at finite
`m`", it stands — but its measured magnitude at m=35 says nothing about
m ≈ 10³ except through the `m`-scaling above.

This is the exact shape of the trap GOAL-MLKEM-003 fell into: a large,
reproducible, real number that is a property of the measurement's regime
rather than of the object. Batch 2 must run the surrogate before quoting any
inflation factor.

---

## 5. Null-control pool composition (`rt4_stats.py` §E)

| population | n | mean | sd | rank of nominal secret vs this group alone |
|---|---|---|---|---|
| uniform | 16 | +0.001121 | 0.005035 | **5 / 17** |
| secret-dist | 8 | +0.008283 | 0.002157 | **9 / 9** (last) |
| near-miss | 8 | +0.003365 | 0.000857 | 6 / 9 |
| pooled | 32 | +0.003473 | 0.004724 | 18 / 33 |

The nominal secret sits 0.62 iid-sd from zero. The comfortable "mid-pack 18
of 33" exists only after pooling three non-exchangeable populations — the
producer's own observation 2, applied to the producer's own headline null
number. Every secret-shaped candidate beats the nominal secret under the
null, and that group's spread is 0.41× the iid value.

---

## 6. Near-miss: the measurement is working, with the wrong error bar

`rt5_controls.py` §H, 600 fresh error draws, `nearmiss_00`:

- delta (correct − near-miss) = **+0.002606 ± 0.000987** (t ≈ 2.6);
- package single draw +0.002962, i.e. +0.36 sd — typical;
- `P(delta ≤ 0) = 0.0017`: the ordering is stable for this instance.

The paired per-vector iid error bar would give t = 5.1 (`rt4_stats.py` §D);
that is the optimistic one. Over the *instance* randomness — one `A`, one
`s` — nothing is measured at all.

So: the near-miss result is the measurement resolving what it needs to
resolve, at ~2.6 sd over error randomness, for one instance. It is also the
single most informative thing in the package, because it is the only place
where the contested assumption visibly fails.

---

## 7. `N` is a library default

`17919 = ceil(3.2 · (4/3)^30)`; verified against the instrument,
`SieverParams().db_size_factor = 3.2`, `db_size_base = 1.1547…`. Also
`saturation_ratio = 0.5`, so the database is not the complete set of lattice
vectors in its ball. `N` is the quantity `MATZOV.Nf` *computes*; here it was
whatever g6k returned by default, and it was not varied.

---

## 8. Scale

The measurement's dimensionless coordinates (`rt5_controls.py` §J):

- `a_x = 2π²σ_e²⟨‖x‖²⟩/q² = 0.8902` → per-vector advantage **0.4106**;
- `a_y = 2π²Var(s−s′)⟨‖y‖²⟩/q² = 0.3171` → wrong-candidate retention 0.728
  (measured 0.674);
- near-miss coordinate `2π²⟨y_k²⟩/q² = 0.0063` → retention 0.9937 (measured
  0.99434).

Rearranging `Nf`: `a = ½·ln(N/L)`. The measurement sits at `a_x ≈ 0.89`. A
cryptographic dual-attack estimate runs at `ln N` of order 10², i.e.
`a_x` of order 10 and per-vector advantage of order `10⁻⁸`. That is eight
orders of magnitude in the very quantity the law is about, and the two
regimes are qualitatively different: here the statistic is ~10⁴ terms of mean
0.41, there it is ~2^{80+} terms of mean ~10⁻⁸. No extrapolation is offered
by the package and none is warranted from it.

---

## 9. Package prose I would not have written

- Commit `8cc51677` and report.md §4.1: *"The pipeline does not find structure
  that is not there."* Section 5 above contradicts this on the package's own
  table. The supported sentence is: *when the target carries no LWE structure,
  the nominal secret is not ranked first.*
- Commit `8cc51677`: *"THE NULL RAN, and it behaved as a null must."* A null
  that cannot fail behaves as it must by construction; the sentence reads as
  corroboration and is not.
- Report §1: the instrument was **found pre-existing and re-verified**, not
  rebuilt. The producer says this plainly and the receipt sets
  `instrument_prebuilt: true`, so this is disclosed, not concealed — but
  `GOAL-MLKEM-004.instrument.reproducibility_warning` says every batch must
  rebuild it, and that requirement was not met. Record it as not met.

No sentence in the package or the commit message claims an ML-KEM break, a
security proof, or a FIPS 203 parameter set affected or cleared. I looked for
one specifically; the scope disclaimers are present and correct in
`report.md` header, `receipt.json`, and the commit message.

---

## 10. Claims I could not check

- Wall-clock and memory figures (sieve 16.55 s, total 19.30 s, peak RSS
  243.2 MB, LLL 0.03 s). Machine- and load-dependent; my reproduction ran my
  own code. Not evidence either way.
- "the two files differ in exactly **five** leaves, all wall-clock timing" —
  I did not diff two runs of the producer's script leaf by leaf. The stronger
  claim (scientific determinism) I confirmed independently: regeneration from
  seeds gives the identical vector multiset.
- Step-0's dim-50 `gauss_sieve` db = 4075 in 0.93 s and fpylll BKZ-30
  160.4 → 130.3 in 0.31 s. Recorded verbatim at `rebuild_transcript.txt`
  lines 265–317 including both documented gotchas; not re-run, to stay inside
  `maximum_runs: 1`. The instrument's functionality is independently
  established by my own dim-60 `bgj1_sieve` run, which is a stronger check.
- Instance-to-instance variation: unmeasured by the package and unmeasurable
  by me from it. One `A`, one `s`.
