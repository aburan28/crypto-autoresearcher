# EXP-MLKEM-007 — implementation note

Experiment: *Toy negacyclic isometry-orbit scoring with covariance-aware GLS
fusion versus single-orbit and ablation baselines.*
Contract: `experiments/EXP-MLKEM-007/specification.yaml` (`status: approved`,
`frozen: true`, `approved_by: coordinator`, `approved_at: 2026-07-27`).
Handoff: `ledger/handoffs/TASK-20260727-012.yaml`.
Hypothesis under test: `ledger/hypotheses/H-MLKEM-007.yaml` (`approved`).
Claim tier: **toy**. This note records *what was implemented and pinned*; it
records no conclusion about H-MLKEM-007.

This note was written **before** RUN-MLKEM-025. Everything in
§2–§6 is a pinning of a parameter the frozen specification explicitly delegates
to `implementation.md`; nothing here changes a hypothesis, success criterion,
threshold, control, budget, or stopping rule.

---

## 1. Environment constraint that shaped the implementation

The execution host provides **CPython 3.11.15 and the standard library only**:
`numpy`, `fpylll`, `sympy` and Sage are all absent, and the frozen budget sets
`network_operations: none`, so no package could be installed. Every routine —
including the lattice reduction — is pure Python. This is the binding
constraint behind the parameter choices in §3 and the n=64 outcome in §7, and
it is recorded as a protocol deviation in `execution-report.yaml`.

## 2. Frozen task definition (delegated by the specification)

The specification defines the scoring task as a *"frozen single-layer
layered-dual scoring task at layer prime p=3: guess-and-score of one planted
secret component layer against dual vectors from the pool, with
modulus-switched residuals defined in implementation.md"*. The definition is:

**Flattened picture.** `I = c*n+i` indexes a secret coordinate, `J = r*n+l` an
LWE equation, and `b_J = sum_I Amat[I][J] s_I + e_J (mod q)` with `Amat` the
block matrix of negacyclic matrices built from `A` by the spec's multiplication
formula. For a dual vector `v ∈ Z^{nk}` put `u_I := (Amat v)_I`; then

```
rho := <v, b> = sum_I u_I s_I + <v, e>   (mod q).
```

**Guess block.** `G` is a set of secret coordinates whose `u_I` is *not* made
short; the projected dual lattice makes `v` and `u_I (I ∉ G)` simultaneously
short, so `rho - sum_{I∈G} u_I s_I` is small. `G` is chosen **shift-invariant**:

```
G = { i : i ≡ 0 (mod d_shift) }   inside ring component 0.
```

**Why shift-invariant.** The orbit element `X^j` acts by `b -> X^j b`. Negacyclic
matrices commute with the negacyclic shift, so `X^j b = A (X^j s) + X^j e` with
the *same* `A`: one pool vector `v` is a dual vector for every orbit element and

```
rho^(j) - sum_{I∈G} u_I (X^j s)_I = small^(j).
```

If `G` were not shift-invariant, orbit element `j` would constrain the shifted
block `G-j`, i.e. *different* unknowns, and no fusion on a common candidate
would be defined. With `G` shift-invariant and `j` a multiple of `d_shift`,
`(X^j s)_G` is a **signed permutation of `s_G`**, so every orbit element scores
the same unknowns and fusion is well posed. The admissible orbits are therefore
exactly `J_d = {0, d_shift, 2·d_shift, …, n-d_shift}` (`X^n = -1` maps a score
to the same score at the globally negated candidate, so shifts `≥ n` are not
distinct elements).

**Layer.** Balanced-ternary decomposition `x = 3u + λ`, `λ ∈ {-1,0,1}`, which is
a bijection on `[-3,3]` and is **odd** (`layer(-x) = -layer(x)`), so signed
permutations act on layer vectors exactly as they act on secret vectors. The
candidate space is `λ ∈ {-1,0,1}^{|G|}`, fully enumerated.

**Modulus-switched residual.** Both the residual and the guess-block
coefficients are switched from `q` to `P = 3^7 = 2187`, a power of the layer
prime:

```
rho~ = round(P·rho/q) mod P      u~_a = round(P·u_{G[a]}/q) mod P
```

and all phases are integer indices into a table of exactly `P` entries
(transform precision `log2 P ≈ 11.1` bits). Switching *before* the guess
correction is what makes the score factor over the guess-block coordinates,
which is precisely the batched path the exact-equality control checks.

**Score.** For orbit element `j` and layer candidate `c`,

```
S_j(c) = Re  sum_t  E[rho~^(j)_t] · prod_a h_{t,a}( (perm_j c)_a )
h_{t,a}(λ) = sum_{x: layer(x)=λ} P_CBD(x) · E[ (-u~_{t,a}·x) mod P ]
E[k]       = exp(2πi k / P)
```

i.e. the marginal likelihood of the layer hypothesis under the **exact** CBD
prior, marginalising over the unguessed p-adic layer. `perm_j` is the induced
signed permutation of `G`. The correct candidate receives the aligned term
`P_CBD(s_G)·E[small]` from every pool vector; wrong candidates receive random
phases.

## 3. Pinned parameters (`CONFIG` in `implementation/run_experiment.py`)

| parameter | value | why pinned here |
|---|---|---|
| `q, eta, k, p` | 3329, 3, 2, 3 | frozen in the specification |
| `d_shift` (n=32) | 8 → `G = {0,8,16,24}`, `|G| = 4`, `J = {0,8,16,24}` | see below |
| `d_shift` (n=64) | 8 → `G = {0,8,…,56}`, `|G| = 8`, `J = {0,8,…,56}` | see below |
| pool construction | LLL(δ=0.99) on the projected q-ary dual lattice, then the `pool_size` shortest of `{±b_i} ∪ {±b_i±b_j}` | spec: "exact enumeration/short-sieve at toy dimension"; charged in full |
| `pool_size` | 2048 | pinned before RUN-MLKEM-025 |
| `P` (switch modulus) | `3^7 = 2187` | power of the layer prime |
| vector-count grid | 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048 | all metrics are cumulative over the pool, so one pass yields every prefix |
| reference vector count | 2048 | used by CTRL-KNOWN-ANSWER and for the reported `r_eff` |
| matched held-out FPR `α` | 1/80 | one wrong candidate out of the 80 wrong candidates per instance |
| standardised threshold `τ` | 3.0 | secondary FPR comparison |
| success target | 0.5 | spec metric: 50 % layer success |
| chi-square tolerance | df = 6, α = 0.001, critical value 22.458 | frozen tolerance for CTRL-COVARIANCE-MODEL |
| moment tolerance | ±4 standard errors on the first and second moments | frozen tolerance |

**Choice of `|G|` at n = 32 and its cost.** `|G| = n/d_shift` and `|J| = n/d_shift`
are forced equal by shift-invariance, and the candidate space is `3^{|G|}`.
`|G| = 8` (`d_shift = 4`) gives 6561 candidates and, because the per-coordinate
prior-weight factor multiplies over `|G|`, needs roughly `m ≈ 5·10^3` pool
vectors for the *unfused* baseline; that is not scoreable for 30 instances in
pure Python inside the frozen 1800 s per-run budget. `|G| = 2` gives `|J| = 2`,
so `r_eff ≤ 2` and the gate threshold `r_eff ≥ 2.0` would be degenerate.
`|G| = 4` is therefore pinned: 81 candidates (fully enumerated, so both success
and false-positive rate are exact, not sampled), `|J| = 4`, `r_eff ≤ 4` against
a gate of 2.0.

**Consequence to record.** The specification's orbit-subset cap is 32. With
`|G| = 4` the admissible orbit subsets have size ≤ 4, so the subset search runs
over prefixes of a 4-element orbit rather than over subsets of up to 32
elements. This is a **reduction of the orbit-subset search space relative to the
specification's cap**, forced by the pure-Python environment, and it is recorded
as a protocol deviation. It does not change any threshold: the frozen n=32 gate
(`r_eff ≥ 2.0`, ≥ 2× vector-count reduction) remains attainable with `|J| = 4`.

## 4. Seed discipline

30 frozen seeds per ring size, **seeds 1–15 training and 16–30 held-out, split
before any covariance estimation, subset selection or threshold pinning**.
Enforced in code by `controls.SeedGuard`, which records every instance-seed read
with its phase and raises if a fitting phase (`covariance_fit`,
`subset_selection`, `threshold_pinning`, `calibration`) touches a held-out seed.
Every manifest carries the resulting attestation.

Every random quantity is derived deterministically as

```
seed_material = SHA256("EXP-MLKEM-007|n=<n>|seed=<seed>|<purpose>")
```

with purposes `public_matrix_A`, `secret_s`, `error_e`,
`control_signed_permutations`, `shuffled_orbit_labels`. The full derivation
strings are recorded in the run records. There is no other source of
randomness; nothing reads the system clock, `/dev/urandom`, or an unseeded RNG.

**Controls are fixed before the secret is used.** `gen_control_permutations`
derives the size-matched random signed permutations from their own derivation
path and is called before any scoring touches the secret.

## 5. Controls as implemented

* **CTRL-KNOWN-ANSWER** — unfused single-orbit baseline (`j = 0`) at the
  reference vector count 2048 on the 15 training instances; pass condition:
  top-1 recovery of the planted layer on ≥ 50 % of them.
* **CTRL-COVARIANCE-MODEL** — for every selected orbit element, (a) an *exact*
  structural check that `X^j·a` is a signed permutation of `a` (so the multiset
  of coefficient magnitudes is preserved exactly), and (b) a chi-square test of
  the pooled coefficients of `X^j s` and `X^j e` against the exact integer CBD
  weights (df = 6, critical value 22.458 at α = 0.001) plus first- and
  second-moment checks at ±4 standard errors. Run at **both** n = 32 and n = 64,
  since it needs no lattice. *Recorded limitation:* the samples across orbit
  elements are, by construction, signed permutations of one another and are
  therefore dependent; this control is a distributional-identity check, not an
  independent-sample test.
* **CTRL-FUSION-ABLATION** — naive unweighted mean over the identical selected
  orbit, identical pool vectors, identical instances, identical thresholds.
  Always measured.
* **CTRL-RANDOM-SIGNED-PERMUTATION** — size-matched random signed permutations
  fixed before the secret is seen. They are drawn so that they **preserve the
  guess-block index set** (a random signed permutation of `G` extended by a
  random signed permutation of its complement), which is the most favourable
  size-matched control: it keeps the guess-block structure intact and breaks
  only the commutation with the public matrix action. Scored and fused
  identically, including its own GLS fit on training seeds.
* **CTRL-SHUFFLED-ORBIT-LABELS** — a derangement of orbit labels between the
  residual of an element and the candidate-coordinate map of another element.
  Negative control: any held-out gain invalidates the pipeline.
* **CTRL-EXACT-EQUALITY** — four checks: (1) `rho^(j)_t` from the batched
  negacyclic correlation equals `<v_t, X^j b>` computed scalar-wise, exactly
  mod q; (2) the switched phase index of each factored score term equals the
  index from the direct scalar computation, exactly mod P; (3) the CBD weight of
  each expanded term computed as a product of per-coordinate integer weights
  equals the direct product, exactly as a `Fraction`; (4) the accumulated
  complex score agrees to ≤ 1e-9 relative — checks 1–3 are exact integer/rational
  identities, check 4 is a float bound because floating-point addition is not
  associative.
* **CTRL-SEED-DISCIPLINE** — `SeedGuard`, §4.

Additionally, the LLL output is re-verified by `verify_lll_output`, which
recomputes the Gram matrix over the integers and the Gram–Schmidt data over
exact `Fraction`s, sharing no floating-point state with the solver. (A float64
version of this verifier was written first and reported spurious violations at
dimension 124; it is numerically unreliable there and was replaced by the exact
one. Recorded as an implementation-development note, not a run outcome.)

## 6. Frozen comparison definitions

Two phrases in the frozen specification admit more than one reading. Both
readings are pinned **before** the runs and **both** are reported, so no
post-hoc choice is possible.

* *"50 percent layer success at matched held-out false-positive rate"* —
  per instance, all 81 candidate scores are standardised by that instance's own
  empirical mean and standard deviation over all 81 candidates (no oracle: the
  correct candidate is not excluded). The threshold is the `(1-α)`-quantile of
  the pooled held-out **wrong-candidate** standardised scores, `α = 1/80`, which
  matches the false-positive rate across rules by construction. `m50` is the
  smallest grid vector count whose held-out success rate reaches 0.5.
* *"held-out wrong-candidate false-positive rate of GLS fusion divided by naive
  unweighted averaging at the same vectors and threshold"* — **primary reading:**
  at matched pool size and matched held-out *detection* rate 0.5, compare the
  wrong-candidate FPRs (`held_out_fpr_at_matched_detection`). **Secondary
  reading:** at matched pool size and the common standardised threshold
  `τ = 3.0` (`held_out_fpr_at_tau`). Both are reported at every grid point.

**Charged-work accounting.** `charged_work()` sums, for a given rule and pool
size `m`: vector generation (measured LLL operation counter + measured sieve
counter + pool formation + `u_G` formation), transform count, score operations
(residuals, `h` tables, candidate products, fused scores), covariance
estimation, orbit-subset search, candidate verification, and memory traffic at
a declared **8 bytes per element touched**. The LLL and sieve terms are
*measured*; the remaining terms are *counted_exact* operation counts of the
executed code path at pool size `m`; the byte term is *modeled*. A second,
explicitly **modeled** accounting that re-charges LLL and sieve proportionally
to `m` (a sieve-dominated rather than reduction-dominated regime) is reported
beside it and is **not** used for the frozen gate decision.

**Reference for `r_eff`.** The covariance is estimated from per-instance
standardised wrong-candidate orbit-score vectors — 15 training instances × 80
wrong candidates = 1200 samples, and likewise 1200 held-out samples. The gate
reads `r_eff` at the reference vector count 2048. All grid points are reported.

## 7. n = 64 feasibility

The n = 64 projected dual lattice has dimension `nk + (nk - |G|) = 128 + 120 =
248`. A bounded, **measured** probe is executed inside RUN-MLKEM-025
(`n64_feasibility_probe`): the same LLL is started on that basis with a hard
wall-clock bound, and the record states only how much time was consumed and
whether reduction completed. Nothing is extrapolated in the run record; any
projection appears in the analysis stage, labelled `modeled`.

If the n = 32 gate passes, RUN-MLKEM-027 attempts the n = 64 test inside its own
frozen 1800 s stage budget and reports whatever terminal state it reaches. If
the n = 32 gate fails, RUN-MLKEM-027 is recorded `cancelled_by_budget` with
reason `gate_stop`, per the specification's `gate_rule`.

## 8. Pre-run calibration

Before RUN-MLKEM-025 the pipeline was exercised on **training seeds only**
(n = 32, seeds 1–5, and a reduced 3-training/3-held-out smoke configuration) to
confirm correctness and to fix the vector-count grid. What was checked:

* `b = A·s + e` in the ring and in the flattened picture agree exactly;
* the orbit commutation `X^j b = A(X^j s) + X^j e` holds exactly for `j = 8`;
* the reduced basis is exactly LLL-reduced (0 size-reduction and 0 Lovász
  violations over an exact-rational check of the first 40 rows);
* measured pool norms at n = 32 are ≈ 465–760 and the empirical per-vector score
  contrast is `delta ≈ 0.196`, from which the vector-count grid was extended
  downwards to 4 so that `m50` is resolved rather than truncated at the grid
  floor.

No held-out seed was read during calibration. Calibration wall-clock is counted
against the experiment's total budget in `execution-report.yaml`.

## 9. Files

```
implementation/mlwe_sampler.py      exact CBD(3), negacyclic ring arithmetic,
                                    instance generation, seed derivation,
                                    signed-permutation controls, p=3 layer
implementation/orbit_scoring.py     dual lattice, LLL + exact verifier, pool
                                    sieve, scalar/batched residuals, modulus
                                    switch, factored score, scalar reference,
                                    charged-work counters
implementation/covariance_fusion.py covariance, r_eff, GLS weights, fusion,
                                    standardisation, Wilson intervals
implementation/controls.py          SeedGuard, covariance-model control,
                                    exact-equality control, shuffled labels
implementation/run_experiment.py    stage driver, charged-work model, gate
                                    decision, outcome classification
implementation/package_run.py       run packaging: summary.json, manifest.yaml,
                                    docs-named artifact aliases, and the
                                    independent planted-layer re-verification
                                    (refuses to overwrite an existing manifest)
```

Commands, environments, stdout/stderr, raw results and manifests for each run
are under `runs/<RUN-ID>/`. Analysis artifacts are under `analysis/`.

## 10. Deviations from the approved protocol

Recorded here and repeated in `execution-report.yaml`:

1. **Pure-Python environment.** No numpy/fpylll/Sage and no network; all
   lattice work is pure Python. This bounds the reachable parameters (§3, §7).
2. **Orbit-subset search space reduced.** Admissible orbit subsets have size
   ≤ 4 at n = 32 (spec cap: 32), forced by (1) via `|G| = |J| = n/d_shift`.
3. **Artifact-name reconciliation.** The frozen `required_artifacts` list names
   `raw.json`, `summary.json`, `stdout.txt`, `stderr.txt`, while
   `docs/evidence-and-reproducibility.md` names `raw-result.json`,
   `stdout.log`, `stderr.log`. Both name sets are produced with identical
   content; the `*.log` / `raw-result.json` files are byte-identical copies of
   the specification-named files, and both hashes are recorded.
4. **Goal status.** `EXP-MLKEM-007.goal_id` is `GOAL-MLKEM-001`, whose status is
   `closed_at_budget`. The experiment's own approval is independent and current,
   so execution is authorised; this is flagged for the Coordinator, not resolved
   here.
5. **Inference policy.** The handoff sets `fallback_allowed: false`, but this
   harness runs Claude models while `orchestration/model-policies.yaml` names
   GPT-5.6 policy aliases (see CLAUDE.md "Model policy note"). Every manifest
   records `requested_policy: executor-implementation`, the resolved model,
   `fallback_used: true`, and `model_verified: false`.
6. **Stop-rule vs precedence wording.** The `n32_gate` stage stop rule groups
   three conditions under the label `correlated_reindexing`, while
   `outcome_classification.precedence` classifies an exact-check disagreement as
   `invalid_implementation_or_instrumentation` and a work ratio ≥ 1 as
   `non_bottleneck_local_gain`. The stage stop rule is applied for **stopping**
   (any of the three halts RUN-MLKEM-027) and the precedence list is applied for
   **classification**, first match wins. Recorded as an interpretation of an
   ambiguity in the frozen contract; no threshold was changed.
