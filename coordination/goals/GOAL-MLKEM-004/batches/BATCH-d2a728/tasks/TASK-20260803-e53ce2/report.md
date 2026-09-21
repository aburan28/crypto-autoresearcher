# TASK-20260803-e53ce2 — measured score distribution of sieve-produced dual vectors

**Batch** BATCH-d2a728 (1 of 6) · **Goal** GOAL-MLKEM-004 · **Role** executor
**Status** completed_valid · **Runs** 1 measurement run (budget `maximum_runs: 1`)

> **This report states no finding.** It records what was measured, what the
> controls show, and what remains unchecked. No comparison against any cost
> model's assumed advantage law was performed — in particular none against
> `estimator/lwe_dual.py` class `MATZOV` method `Nf` (line 526). That
> comparison is a later batch, after this raw data is independently reviewed.
>
> No ML-KEM break claim, no security proof, no FIPS 203 parameter set affected
> or cleared. This is a dimension-60 measurement and is **not** crypto-scale
> evidence (AGENTS.md rule 4/7). AGENTS.md rule 12 remains **UNMET and
> UNWAIVED**; nothing here changes the status of any `EV-*` or `KN-*` record.

---

## 1. Step 0 — instrument rebuild

Recorded verbatim in `rebuild_transcript.txt`; every command and its combined
stdout+stderr is appended by a recorder script, unedited.

**What was found.** The venv from the earlier session **was already present**
at `/tmp/sagevenv` (Python 3.11.15), with `fpylll 0.6.4` and `g6k 0.1.2`
already installed. It was therefore not recreated. The task card required
recording this either way, so: *not rebuilt from scratch; found pre-existing
and re-verified functional in this session.* The `KN-TECH-14efa5` install route
was re-executed anyway (gmp symlink + `pip install --no-build-isolation g6k`)
and reported `Requirement already satisfied: g6k ... (0.1.2)`.

**Instrument verified functional before any measurement**, reproducing the
recipe's own numbers:

| component | check | result |
|---|---|---|
| passagemath | `sage.__version__`, `PowerSeriesRing` discriminator | 10.8.7; `1 + x + ... + O(x^6)`; resolves inside the venv, not a shim |
| fpylll 0.6.4 | dim 60 qary q=3329, BKZ-30 ×4 loops | `‖b0‖` 160.4 → 130.3 in 0.31s (recipe: 160.4 → 130.3, 0.3s) |
| g6k 0.1.2 | dim 50 qary q=3329, `gauss_sieve` | db = **4075** vectors in 0.93s (recipe: 4075 in 0.94s) |

Both documented gotchas reproduced exactly as `KN-TECH-14efa5` records them:
`BKZ.DEFAULT_STRATEGY` → `RuntimeError: Cannot open strategies file.`, and
`Siever(GSO.Mat(A))` → `ValueError: Siever requires UinvT enabled`.

**Deviations recorded, not hidden.** The verification script *I* wrote failed
twice before succeeding — once on a non-existent `R.O(6)` (correct spelling
`.add_bigoh(6)`), once on `from g6k.siever import SieverParams` (it lives in
`g6k.siever_params`). Both are `implementation_error` in the executor's own
check, **not** instrument failures; both failing runs are kept verbatim in the
transcript. A smoke test of the measurement pipeline at a tiny configuration
(`--smoke`, d=40) was run before the official run and is also in the transcript,
so no execution of this pipeline is hidden.

---

## 2. What was measured

An LWE instance was generated **by this harness with recorded seeds**, so the
correct secret is known by construction.

Row convention: `A ∈ Z_q^{m×n}`, `b = A s + e mod q`.
Dual lattice, dimension `d = m + n`, determinant `q^n`:

```
L = { (x, y) ∈ Z^m × Z^n : y ≡ Aᵀx  (mod q) },    B = [ I_m   A   ]
                                                      [  0   q·I_n ]
```

For any `(x,y) ∈ L` and any candidate `s'`:
`x·b − y·s' ≡ x·e + y·(s − s')  (mod q)`, which collapses to `x·e` at the
correct secret. The per-vector score is the standard dual-sieve contribution

```
score_i(s') = cos( 2π · t_i(s') / q ),   t_i(s') = centre_mod( x_i·b − y_i·s' , q )
```

### Run parameters (single run)

| field | value |
|---|---|
| sieve algorithm | **`bgj1_sieve`** (g6k 0.1.2), `threads=1` |
| lattice dimension | **60** (`m=35`, `n=25`) |
| modulus `q` | **127** |
| secret distribution | centred binomial `η=2` (ML-KEM-style), entries in [−2,2] |
| error distribution (main) | rounded Gaussian `σ=2.0` (empirical sd 1.929, ‖e‖∞ = 4) |
| sieve vector count `N` | **17 919** |
| wall time | LLL 0.03 s · **sieve 16.55 s** · total run **19.30 s** |
| peak RSS | 243.2 MB (cap 6 GB enforced via `RLIMIT_AS`) |
| seeds | instance `20260803001`, candidates `20260803002`, null target `20260803003`, decay errors `20260803004`, **g6k Siever `469431436621`**, fpylll `20260803005` |
| candidates scored | 33 = 1 correct + 16 uniform-`Z_q` + 8 secret-distribution + 8 near-miss (`s` with one coordinate +1) |
| `‖v‖²` over the db | min 218, median 315, max 329 |

**Sources of randomness, all recorded:** numpy `default_rng` streams for `A`,
`s`, `e`, the candidate draws, the null target and the decay errors; fpylll's
global RNG for LLL; and g6k's `Siever(seed=…)`. The sieve seed is explicit, so
the sieve is not an uncontrolled source.

### Certificate

`certificate.kind: lattice_membership`. Every one of the 17 919 emitted vectors
was re-verified to satisfy `y ≡ Aᵀx (mod q)` by integer arithmetic computed from
`A` and the reconstructed lattice vectors, **independent of g6k's internal
representation**: 0 violating entries, 0 all-zero vectors, `verified: true`.
The script aborts before reporting any score if this check fails. This
certifies that the scored objects really are dual-lattice vectors and that the
coefficient→vector interpretation of `Siever.itervalues()` is correct; it is
not a discrete-log or factor-base certificate, and it claims nothing else.

---

## 3. Raw data emitted

`raw_scores.json` (21 036 537 bytes, sha256
`892991c43a602e370b46dc30d40e8bc6b4840f0f9692890f202b422f41bf3642`) contains,
**per vector**, not as summaries:

- `phases_t` — the integer phase `t_i(s')` for **every** vector × candidate, for
  all 8 targets (33 candidates for MAIN and NULL, 5 for each decay target);
- `scores_cos` — the cosine score arrays, emitted in full for MAIN and NULL and
  for the correct-secret population of every target;
- `norm2_v`, `norm2_x`, `norm2_y` — per-vector squared norms, so scores can be
  conditioned on vector length;
- `x_dot_e_main` — the per-vector `x_i·e` for the main target;
- `A`, the secret `s`, every candidate vector, and every target's `b` and error
  vector.

The cosine score is an exact function of the emitted integer phase
(`cos(2π t/q)`), so a reviewer can recompute any statistic they wish — a
different score function, norm-conditioned subpopulations, cross-candidate
correlations, tails — without re-running anything.

---

## 4. What the controls show

All numbers below are **mean per-vector score over the same 17 919 sieve
vectors**, recomputed independently from the raw arrays. They are control
outcomes, reported as observations.

### 4.1 Null object — signal removed (completion-gate control)

The null is the same pipeline with the signal removed: **the identical dual
vectors, identical candidate set and identical scoring code**, with `b`
replaced by a uniformly random vector in `Z_q^m`. No LWE structure remains, so
the nominal secret `s` is not a solution to this target.

| population | n | mean | min | max | sd |
|---|---|---|---|---|---|
| nominal secret | 1 | **+0.00330** | — | — | — |
| uniform-`Z_q` candidates | 16 | +0.00112 | −0.01019 | +0.01010 | 0.00504 |
| secret-distribution candidates | 8 | +0.00828 | +0.00494 | +0.01056 | 0.00216 |
| near-miss candidates | 8 | +0.00337 | +0.00163 | +0.00408 | 0.00086 |

**Null outcome: the pipeline does not find structure that is not there.** The
nominal secret ranks **18th of 33** by mean score — mid-pack — and sits −0.04
empirical standard deviations from the wrong-candidate mean. For contrast the
same pipeline on the real target ranks the correct secret **1st of 33**.

### 4.2 Decay control — sweep the parameter meant to destroy the signal

Same `s`, same dual vectors, error standard deviation swept upward.

| target | σ | mean @ correct secret | mean over wrong (n=4, uniform) | rank |
|---|---|---|---|---|
| DECAY | 0.5 | **+0.94924** | +0.00293 | 1/5 |
| DECAY | 1.0 | **+0.84115** | +0.00331 | 1/5 |
| **MAIN** | 2.0 | **+0.42738** | +0.00385 (uniform group, n=16) | 1/33 |
| DECAY | 4.0 | +0.01827 | −0.00044 | 1/5 |
| DECAY | 8.0 | +0.00464 | +0.00317 | 3/5 |
| DECAY | 16.0 | −0.00371 | −0.00021 | 4/5 |
| DECAY | uniform error on `Z_q` | +0.00898 | +0.00323 | 1/5 |

The correct-secret score decays monotonically toward the wrong-candidate noise
level as σ increases, and is indistinguishable from it by σ=8. It does **not**
fail to decay, which is the canonical artifact tell named in the inventor
protocol.

**Honesty note on the last row.** `DECAY_uniform_error` shows `rank 1/5` at a
mean of +0.00898. With only 4 wrong candidates and all means at the ~0.003–0.01
noise level, **that rank is uninformative** and must not be read as residual
signal. It is reported because it was observed, not because it means anything.

### 4.3 The signal target (MAIN, σ=2), by candidate type

| population | n | mean | min | max | sd |
|---|---|---|---|---|---|
| correct secret | 1 | **+0.42738** | — | — | — |
| near-miss (one coord +1) | 8 | +0.42496 | +0.42349 | +0.42672 | 0.00108 |
| secret-distribution wrong | 8 | +0.29062 | +0.26510 | +0.32165 | 0.02396 |
| uniform-`Z_q` wrong | 16 | +0.00385 | −0.00708 | +0.01388 | 0.00606 |

Also measured: `x·e` over the db has sd 25.63 with range [−63, +63] against
`q/2 = 63.5`, and 76.69% of vectors have `|x·e| < q/4`.

---

## 5. Observations to check (NOT results)

Flagged per the task card as things a later batch should examine. **None of
these is a finding, and none has been compared against any assumed law.**

1. **Near-miss candidates score almost identically to the correct secret**
   (+0.42496 vs +0.42738; the whole 8-candidate near-miss group spans a range
   of 0.0032, narrower than the uniform group's own sd). Mechanically the
   phase differs by `y_i·(s − s')` = a single coordinate of `y`, which is small
   for short dual vectors. Whether this matters for anything is unchecked.
2. **The three wrong-candidate populations are not exchangeable.** Uniform,
   secret-distribution and near-miss candidates give clearly different means
   *and* clearly different spreads (sd 0.00606 / 0.02396 / 0.00108). "Wrong
   candidate" is therefore not one population, so any statistic quoted over a
   pooled wrong population depends on how the pool was built.
3. In the null, the secret-distribution group has a visibly smaller spread
   (sd 0.00216) than the uniform group (sd 0.00504) despite the same vector
   count. Unexplained; worth a look before any variance argument is made.
4. Between σ=2 and σ=4 the correct-secret mean falls from 0.427 to 0.018 —
   most of the decay happens inside one doubling. The sweep is too coarse to
   locate that transition.

---

## 6. What remains unchecked

- **No comparison against `MATZOV.Nf`'s advantage law, by instruction.** The
  raw data needed for it is emitted; the comparison is batch 2's work.
- **Dimension 60, q=127, m=35, n=25 only.** One instance, one seed, one sieve
  algorithm (`bgj1_sieve`). Nothing here extrapolates to FIPS 203 dimensions,
  and no extrapolation heuristic is offered.
- **One LWE instance.** Instance-to-instance variation is entirely unmeasured;
  every number above is a single draw.
- **The distinguishing form only.** Candidates are full secrets. The real
  dual attack scores an FFT sub-block after a guessing/dimension-reduction
  split; that structure is not modelled here.
- **The dual vectors `(x,y)` themselves are not in `raw_scores.json`** — only
  their norms, phases and scores. A reviewer can regenerate them exactly by
  re-running the recorded command (deterministic, 19 s), but cannot score a
  *new* candidate of their own choosing directly from the JSON. Emitting the
  vectors would fix this and is a concrete recommendation for batch 2; it was
  not done here because it would have required a second measurement run and
  `budget.maximum_runs` is 1.
- **Sieve saturation/quality parameters were left at g6k defaults** and their
  effect on the db is unmeasured.
- **No model probe.** `orchestration.adapter doctor --probe` cannot verify any
  backend model id in this environment (all API keys unset), so
  `model_verified: false`.

---

## 7. Reproduction

```sh
/tmp/sagevenv/bin/python \
  coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-e53ce2/measure_scores.py \
  --out-dir <dir> --mem-cap-gb 6
```

Git commit at execution: `d2f521875cc889eb4c2b3338a91e4c574263fe43`, tree clean
except this task's own untracked output directory.

**Reproduction check performed.** The identical script was re-run with the same
seeds into a scratch directory. Result: **every scientific value is
bit-identical** — same 17 919 vectors, same certificate, and all phase, score,
candidate and secret arrays equal. The two files differ in exactly **five
leaves, all of them wall-clock timing fields** (`check_seconds`,
`scoring_seconds`), which produced a 1-byte file-size difference and hence a
different sha256. The measurement is deterministic; only its timings are not.

**Raw-vs-summary agreement verified independently.** A separate script sharing
no code with `measure_scores.py` reloaded `raw_scores.json` and re-derived
every number in `results.json`: 72 cosine arrays confirmed equal to
`cos(2π t/q)` on their emitted phases, 96 per-candidate means reproduced, all 8
ranks reproduced, all array lengths equal to `N`, and MAIN's correct-secret
phase confirmed equal to the independently emitted `x·e` for all 17 919
vectors. All checks passed.
