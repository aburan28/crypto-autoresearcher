# EXP-LPF-001 implementation note

Authored at TASK-20260801-049 (BATCH-025, GOAL-ECDLP-001). Binding contract:
`experiments/EXP-LPF-001/specification.yaml`, sha256
`0d6c946fb84073feae47865da9b787b7d7ba459617834644680a06bf886d1cda`, hash-bound
at commit `ba1567ee415b680b2d25108d59b9884f432d44d8`.

Driver: `experiments/EXP-LPF-001/implementation/lpf001_driver.py`, sha256
`786aeb0550d75fa3d0785aefbe50b121a24cacae584a4cadd79902c464722d65`.

**This note records implementation choices and deviations. It states no
interpretation, freezes no threshold, selects no branch, and asserts nothing
about HEUR-DS-1, H-LPF-001 or any other hypothesis in either direction.**

---

## 1. What was executed and what was not

- **Executed:** `RUN-LPF-001-calib` (`--mode calib`), authorized by
  `CALIBRATION_AUTHORIZATION: "AUTHORIZED"` in the TASK-20260801-048 snapshot
  receipt. Objects touched: OBJ-NULL-UNIF, OBJ-NULL-SYNTH, OBJ-CTRL-PRODUCT,
  OBJ-PLANT-SMOOTH-gamma, OBJ-PLANT-ROUGH-gamma.
- **Authored complete and NOT executed:** `run_measurement()` and everything it
  reaches — `deterministic_factor_base()`, `int1_fibre_invariants()`,
  `upper_triangle_indices()`, `_deviation_certificate()`,
  `_independent_pmax_recheck()`. ATS-LPF-1 clause 3 requires the file bound at
  TASK-20260801-050 to be the file TASK-20260801-056 executes; that is why the
  measurement arm is written now, in full, rather than later.

### The measurement guard

`--mode measure` refuses to start unless **both** gates are satisfied:

1. `--approval-receipt` names a JSON file whose `APPROVAL_DETERMINATION` is
   exactly `"APPROVED"` (`_check_approval`); and
2. `--reading-rule` names a YAML file that parses, carries a `reading_rule`
   mapping with `frozen: true`, and supplies `bands`, `null_spread` and
   `certifying_set_retained` (`_load_reading_rule`).

A missing band for any statistic id at any cell is also a refusal. There is no
default and no fallback: the driver refuses rather than substituting a number.
Neither gate exists at TASK-20260801-049 — there is **no reading rule yet** —
so the measurement path is unreachable from this task by construction as well
as by omission.

### The reading-rule schema the measurement arm expects

TASK-20260801-052 freezes `experiments/EXP-LPF-001/reading_rule.yaml`. The
driver was authored before that file existed, so the schema it will read is
declared here so the freeze can match it (it is also embedded in the driver as
`READING_RULE_SCHEMA_NOTE` and printed in every refusal message):

```yaml
reading_rule:
  id: RR-LPF-1
  frozen: true
  certifying_set_retained: [STAT-RATE-u, STAT-KS-DICK, STAT-TAIL-DEEP]
  bands:
    '16':
      'STAT-RATE-u@u_target=2': {lower: <float>, upper: <float>}
      'STAT-RATE-u@u_target=3': {lower: <float>, upper: <float>}
      'STAT-RATE-u@u_target=4': {lower: <float>, upper: <float>}
      'STAT-RATE-u@u_target=5': {lower: <float>, upper: <float>}
      'STAT-RATE-u@u_target=6': {lower: <float>, upper: <float>}
      'STAT-KS-DICK':           {lower: <float>, upper: <float>}
      'STAT-TAIL-DEEP':         {lower: <float>, upper: <float>}
    '20': { ... the same seven keys ... }
  null_spread:
    '16': {'<statistic id>': {mean: <f>, sd: <f>, min: <f>, max: <f>, median: <f>}}
    '20': { ... }
  identity_binomial_cut: <int>
```

**This is a coordination dependency, not a licence.** If TASK-20260801-052
freezes a different shape, the correct repair is a Coordinator amendment
producing a new driver under a new hash — never an edit of the hash-bound file.

---

## 2. Structural blindness of the calibration arm (ATS-LPF-1 clause 5)

`run_calibration()` names none of `deterministic_factor_base`,
`int1_fibre_invariants` or `run_measurement`, and reaches none of them by any
route. Concretely, and at the level of **objects** rather than labels — the
distinction RTB-040-1 was about:

- `CalibrationCell.__init__` takes from the harness **only the field prime `p`**
  (via `generate_instance(2301, bits)`). It never computes the x-coordinate
  membership array `X_E`, never selects the first 512 x-coordinates, and never
  evaluates `S_3`. The curve coefficients `a, b` are not stored on the object.
- The only integers the calibration constructs are: uniform draws on
  `[1, p**2]`; `ENC-B` images of uniform `(e_1, e_2)` pairs; the ENC-A product
  control; and the two plant replacements. None of these is a function of the
  factor base, and none is bit-identical to any real-object sample except by
  the coincidence that both live in `[1, p**2]`.
- `deterministic_factor_base()` is the sole function that touches the real
  object; it flips the module-level tripwire `_REAL_OBJECT_TOUCHED`, and
  `run_calibration()` raises `IntegrityFailure` if that tripwire is true when
  it finishes. `LPF_real_object_touched` is written into `raw-result.json`.

**OBJ-NULL-SYNTH is a declared calibration object**, not a back door: it applies
ENC-B (the encoding) to uniform `(e_1, e_2)`, which is not the Semaev
specialization (the map from a half-tuple of factor-base x-coordinates to
`(e_1, e_2)`). The specialization is never invoked in calibration.

---

## 3. Factorization: the primitive, and what "verified" means

No external factorization library was used or is available in this environment
(`gmpy2` is absent). The primitive is carried in the driver itself, so the
"exact module and version" recorded in `environment.json` is this driver file,
identified by `driver_sha256`.

**Algorithm.** For each cell, primes up to `isqrt(X)` (`X = p**2`) are sieved
once. Every entry of that table is then independently re-tested with the
deterministic Miller–Rabin routine — a second code path from the sieve that
produced it — and a non-prime entry is an immediate `IntegrityFailure`. Arrays
are factored by **complete vectorised trial division** with an active set: an
element leaves the active set only when its remaining cofactor is strictly below
`q**2` for the current prime `q`, at which point every prime below `q` has
already been divided out, so the cofactor is 1 or prime.

Measured throughput at n = 130816 on this host: about 0.27 s per sample set at
bits = 16 and about 2.6 s at bits = 20 (see the pilot gate in
`raw-result.json`, which measures it rather than assuming it).

**`LPF_factorization_verified_fraction` is defined as follows, and the definition
is stated rather than left implicit:**

- *Product.* `removed_product * residual == N` is asserted **elementwise on 100
  percent of samples**. `removed_product` accumulates every small prime actually
  divided out, so this is an exact statement that the factorization multiplies
  back to the sample.
- *Primality of every returned factor.* The residual factor of **each sample**
  is Miller–Rabin tested individually. The small factors are members of the
  sieved table, **every entry of which was Miller–Rabin verified prime at
  construction**; per-sample primality of a small factor is therefore membership
  in an independently verified prime table rather than a repeated identical test
  on the same integer.
- A sample counts as verified only if both hold. Any shortfall raises
  immediately and stops the run (frozen stopping rule: a wrong factorization
  silently poisons every statistic).

**Plant integers take a separate verification path.** Their factorization is
known by construction, so they are verified by `verify_known_factorization()`,
which multiplies the recorded factor list back to the value and Miller–Rabin
tests **every** factor individually, per sample, with no reliance on the batch
factorizer. Those counts are added into the same fraction.

The measurement arm additionally re-checks `P_max` on a stated random subsample
of 1000 samples per cell against **`sympy.factorint`**, a second factorization
path sharing no code with the above (`_independent_pmax_recheck`). That check
belongs to the measurement stage and was not run here.

---

## 4. The Dickman function (LPF-CAL-E)

`rho` is obtained by **numerical solution of the delay equation**
`u*rho(u) = integral_{u-1}^{u} rho(t) dt`, `rho == 1` on `[0,1]`, by composite
Simpson on a uniform grid of step `1/4000`, implicit in the unknown right
endpoint. The grid runs to `u = 44`, which covers every attainable
`Z = ln N / ln P_max` (bounded by `log_2 X <= 40`).

The frozen table `rho_1..rho_6` is used **only** as a reproduction check and is
never substituted into any computation. `dickman_reference_reproduction.json`
records the driver's own solved values beside the frozen ones with the relative
discrepancy per point.

---

## 5. Statistics: forms and the two implementation readings

`u` is **recomputed** at every rung from the integer `Bsm` by the frozen formula
`u = ln(D)/ln(Bsm)` with natural logarithms and the frozen per-cell `D`
(`2**32` at bits 16, `2**40` at bits 20, under DREAD-LPF-1's reading applied per
cell). No `u` is asserted.

- **STAT-RATE-u** — `p_hat(u)` is the fraction of the sample set with
  `P_max <= Bsm`; `R(u) = p_hat(u)/rho(u)`.
- **STAT-TAIL-DEEP** — `T_deep` is the **tenth largest** `Z_j`, over the samples
  with `N_j > 1` and `P_max(N_j) > 1`. Rank ten, not rank one.
- **STAT-KS-DICK** — one-sample Kolmogorov–Smirnov distance between the
  empirical CDF of `Z_j` and the classical Dickman largest-prime-factor CDF.
- **STAT-KS2-CAL** — computed in the measurement stage only; non-certifying,
  recorded with no band and no reject boolean.

### Implementation reading A (STAT-KS-DICK reference CDF)

The contract names "the classical Dickman largest-prime-factor CDF for uniform
integers in `(1, X]`" without writing it out. Dickman's theorem states
`P(P_max(N) <= N**(1/z)) -> rho(z)`, i.e. `P(Z >= z) -> rho(z)`, so the CDF used
is

```
F(z) = 0            for z < 1
F(z) = 1 - rho(z)   for z >= 1
```

The alternative phrasing — normalising by `ln X` instead of `ln N` — gives the
**same** limit function, because `ln N / ln X` concentrates at 1 for `N` uniform
on `(1, X]`. The two readings coincide asymptotically and differ only through a
finite-`X` correction, which is exactly the class of error the uniform
calibration arm exists to measure (ABS-REL-LPF-1). This is a CDF **of `Z`** and
not of a raw polynomial degree; the forbidden category error is not committed.

### Implementation reading B (`LPF_movement_beyond_noise_flag`)

The metric is defined as "whether the recorded shift exceeds the measured null
spread", and the shift is carried "in units of the measured null standard
deviation". The driver therefore sets the flag to `|shift| >= 1.0`, i.e. the
measured shift is at least one measured null standard deviation. The alternative
reading — the plant mean lying outside the `[min, max]` range of the 200
measured null replicates — is recorded **separately** in every row as
`movement_beyond_null_range_auxiliary_record`, explicitly labelled an auxiliary
record and **not** a decision variable, not a cut, and not frozen. Both readings
are routed to TASK-20260801-054 under ATS-LPF-1 clause 4; the driver resolves
neither.

### Open item OPEN-LPF049-A (comparison count in LPF-CAL-B)

The contract's LPF-CAL-B note computes its exact-binomial band from
"20 x 4 x 1 = 80 comparisons at that cell". STAT-LPF-1 has four members, but one
of them (STAT-KS2-CAL) is non-certifying and is **not** computed in the
calibration, while STAT-RATE-u spans five frozen `Bsm` rungs — so the number of
comparisons actually available per replicate is seven, not four. The run records
the **raw per-statistic rejection counts** plus both aggregate readings
(`reading_i_*` counting STAT-RATE-u once per replicate, `reading_ii_*` counting
every rung), and **resolves neither**. The cut itself is RR-LPF-1's to freeze;
this driver freezes none. Routed to TASK-20260801-054 per ATS-LPF-1 clause 4.

---

## 6. Bands: computed by the frozen rule, NOT frozen

LPF-CAL-D requires detection rates, and a detection rate requires a band. The
band **rule** is frozen in THR-LPF-1 (the 2nd and 199th ascending order
statistics of the 200 LPF-CAL-A replicate values, rejection strictly outside).
The driver applies that rule to the measured replicates and emits the result
under the key `band_by_frozen_rule`, carrying `band_status`:

> COMPUTED BY THE FROZEN THR-LPF-1 RULE FROM THE MEASURED LPF-CAL-A REPLICATES.
> NOT FROZEN. TASK-20260801-052 OWNS THE FREEZE; THIS DRIVER SUPPLIES A NUMBER
> AND NEVER A CHOICE.

The driver writes no `reading_rule.yaml`, strikes no statistic from the
certifying set, selects no branch, and states no disposition. The full
200-value replicate array for every statistic at every cell is archived in
`results/calib/null_replicate_statistics.json` so the freeze consumes measured
data rather than a summary.

---

## 7. Plant construction — and where each family moves mass

Both plants are built **by replacement with integers of known factorization**,
so no plant rung costs any additional factorization and every rung of both
ladders is affordable. That is what makes PERTURB-MOVE-1's per-rung table
possible; at BATCH-024 the excuse for endpoint-only measurement was cost.

- **OBJ-PLANT-SMOOTH-gamma.** A `gamma` fraction of a uniform replicate is
  replaced by a product of primes at most `Bsm(u = 4)` for that cell (256 at
  bits 16, 1024 at bits 20). Primes are multiplied in while the product stays at
  or below the replaced value `v`, so the replacement lies in `(v/Bsm, v]` —
  matched size. **It moves mass into the HIGH-Z (smooth) end of the
  Z-distribution**: `P_max <= Bsm(u=4)` by construction, hence `Z` is large. It
  is not the DESIGN-TRAP-LPF-1 same-law replacement.
- **OBJ-PLANT-ROUGH-gamma.** A `gamma` fraction is replaced by `q*r` with `q` a
  prime above `sqrt(X) = p` and `r` a prime with `q*r <= v` and `q*r > v/2`.
  Since `r <= v/q < X/p = p < q`, the largest prime factor is exactly `q`, known
  by construction, and `Z = ln(q r)/ln q < 2`. **It moves mass into the LOW-Z
  (rough) end of the Z-distribution.** Also not invariant in law.
- **OBJ-CTRL-PRODUCT.** `N = max(lift(e_1),1) * max(lift(e_2),1)` on uniform
  `(e_1, e_2)`. A single object, not a ladder; its detection is derivable in
  advance. ENC-A is never a decision encoding here.

Construction fallbacks (a replaced value too small to admit the rough
construction) are **counted and reported** per rung in
`plant_construction_accounting`, not silently dropped; the original sample is
left in place in that slot and `replacements_effected` records the true count.

Both plant families draw from streams disjoint from every other stream; the
20 base replicates they perturb are the first 20 LPF-CAL-A replicates, reused
element by element with their archived factorizations.

---

## 8. Determinism, seeds and streams

Every random quantity comes from a named `Stream`, whose per-draw seed is
`int(sha256("<seed>:<name>:<k>")[:16], 16)`; each draw index yields an
independent `numpy.random.default_rng`, so any single replicate is regenerable
exactly without replaying the ones before it. Master seed 2301 (the frozen
`generate_instance` seed). Stream offsets are disjoint by construction:

| stream | offset |
| --- | --- |
| `calib_pilot` | 100000 |
| `calib_uniform` | 200000 |
| `calib_identity_uniform` | 300000 |
| `calib_identity_synth` | 400000 |
| `calib_product` | 500000 |
| `calib_plant_smooth` | 600000 |
| `calib_plant_rough` | 700000 |
| `measure_uniform_ks2` | 900000 (measurement stage only) |

The real arm carries **no sampling seed at all**: OBJ-REAL is exhaustive over
the 130816 half-tuples `i < j` and is reproducible from the factor base alone.

---

## 9. Budget handling

The pilot gate runs **first**: 10000 factorizations per cell, the achieved rate
measured, the full calibration cost extrapolated linearly, and an abort **before
any bulk work** if the projection exceeds the 14400 s wall-clock budget. The
projection carries a declared pre-datum overhead multiplier of 2.0 for
statistics, plant construction and I/O; every projected figure is labelled
`MODELED`, and only `pilot_seconds_measured` and
`pilot_rate_per_second_measured` are `MEASURED`.

A `Deadline` object additionally checks the wall clock between every stage and
every replicate block. An abort at either point is a **budget event**: recorded
in `LPF_budget_event`, classified `resource_exhaustion`, reported as L-0
instrument signal, and **never** converted into a reduced-scope run. Reducing
`R_CAL`, the ladders, the cells or `n` would require a Coordinator
`protocol_amendment`; none was requested and none was taken.

---

## 10. Protocol deviations

**None from the frozen protocol.** No statistic, rung, cut, band, ladder or
branch was added, dropped, moved or reordered; `R_CAL = 200`, `R_IDENT = 20`,
`R_PROD = 20`, `R_PLANT = 20`, `n = 130816`, both cells, both ladders at every
rung, exactly as frozen.

Two implementation readings (section 5, A and B) and one open item
(OPEN-LPF049-A) are recorded rather than resolved, and routed to
TASK-20260801-054 under ATS-LPF-1 clause 4. Recording an ambiguity is not a
deviation; resolving one in the driver would have been.

---

## 11. Inference provenance

Requested policy `executor-implementation`; resolved model `claude-opus-5`;
`fallback_used: true` (Claude Code cannot resolve the GPT-5.6-family policy
aliases in `orchestration/model-policies.yaml`); `model_verified: false` (no
`python3 -m orchestration.adapter doctor --probe` was run). Under this harness
independence is procedural, not model-level; nothing here is admissible toward
the AGENTS.md rule 13 three-model closure quorum.
