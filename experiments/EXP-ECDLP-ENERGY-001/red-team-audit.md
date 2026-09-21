# Red-team audit: EXP-ECDLP-ENERGY-001

Date: 2026-07-17
Audited worktree: `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy`
Audited HEAD: `e4b8978094f9a35c497df683b233cb5e57db1f60`
Mode: read-only audit; no intentional write was issued to the audited worktree or either run. Live worktree/AppleDouble state churn observed during review is documented below.

## Verdict

**REVISE the interpretation.** The arithmetic replay and the frozen gate evaluation are valid, and the correct disposition remains **do not promote these frozen configurations**. The interpretation is not ready as written because its central post-run occupancy correction uses unordered point multisets but still ignores unavoidable equivalences from a sign-complete base. Exact fivefold-support recomputation falsifies the claimed finite-size match to `binomial(B+4,5)`.

The clean surviving result is narrower and stronger:

- Every tested random, x-interval, square-map, and rational-union base attained the exact sign-complete Sidon floor for pair energy, `E_2=3B^2-3B`, with pair support `1+B^2/2`. Thus these frozen sets have no nontrivial pair-sum collision beyond forced sign, diagonal, and permutation effects.
- Exact fivefold support, not the 128-target sample, shows x-interval and rational-union tied the random control at all three instances; square-map was lower at all three instances.
- This supports a frozen-instance no-promotion decision. It does not support rejecting a population-level claim about these coordinate-family generators, fixed-curve preprocessing, or coordinate factor bases generally.

## Findings ordered by severity

### HIGH-1 — The unordered occupancy correction is not the correct finite-size model for a sign-complete base

The analysis replaces ordered tuples by `binomial(B+4,5)` unordered point multisets (`analysis.md:41-48`). That removes permutation overcount but not cancellation overcount. With `A=+-{P_1,...,P_n}`, many different multisets have the same formal sum because pairs `P_i+(-P_i)` cancel. For five terms, a generic dissociated sign-complete base has one formal class for each coefficient vector `z in Z^n` with `||z||_1 in {1,3,5}`. Its finite class count is

```text
D(n,5) = sum over r in {1,3,5} sum over s=1..min(n,r)
         binomial(n,s) binomial(r-1,s-1) 2^s,
where n=B/2.
```

This gives `D(4,5)=456` and `D(6,5)=2668`, not `binomial(12,5)=792` and `binomial(16,5)=4368`. The exact support is directly computable at these toy orders:

| field bits | `q` | `B` | unordered multisets | exact random `|5A|` | exact uniform nonzero-target probability | observed sample |
|---:|---:|---:|---:|---:|---:|---:|
| 15 | 10,799 | 8 | 792 | 456 | 4.223% | 9/128 = 7.031% |
| 17 | 9,851 | 8 | 792 | 456 | 4.629% | 9/128 = 7.031% |
| 19 | 129,737 | 12 | 4,368 | 2,668 | 2.056% | 4/128 = 3.125% |

The reported 7.07%, 7.73%, and 3.31% unordered-Poisson predictions happen to be close to the sampled counts, not to the exact finite supports. The exact counterexample is already inside the immutable run; no new curve or seed is needed.

The leading asymptotic term can still be `B^5/5!` for a sufficiently dissociated sign-complete base, so the rough `(5!)^(1/5)` factor may survive as a large-`B` heuristic. It is not a validated model for `B in {8,12}` and must not be presented as explaining these observations.

**Required correction:** use `|5A minus {O}|/(q-1)` for exact toy occupancy. For extrapolation, state and validate a signed-coefficient occupancy model, including lower-order cancellation classes and collisions modulo `q`.

### HIGH-2 — Sampled success ratios obscure an exactly computable result

The source samples 128 nonzero targets (`coordinate_energy.py:590-600`) and forms ratios from their hit counts (`coordinate_energy.py:615-625`). At these toy orders, the entire fivefold support can be enumerated cheaply, so binomial sampling was unnecessary for the primary coverage comparison.

Independent support recomputation gave:

| field bits | random | x interval | square map | rational union | scalar progression |
|---:|---:|---:|---:|---:|---:|
| 15 | 456 | 456 | 376 | 456 | 41 |
| 17 | 456 | 456 | 400 | 456 | 41 |
| 19 | 2,668 | 2,668 | 2,622 | 2,668 | 61 |

Therefore the exact x-interval/random and rational-union/random coverage ratios are `1.0` at every size. The square-map ratios are approximately `0.825`, `0.877`, and `0.983`. The sampled ratios from `0.444` through `1.250` are not estimates precise enough to rank the tied-support families.

For scale, 95% Wilson intervals for the reported hit counts are:

- `9/128`: `[3.74%, 12.82%]`
- `7/128`: `[2.67%, 10.86%]`
- `5/128`: `[1.68%, 8.82%]`
- `4/128`: `[1.22%, 7.76%]`
- `2/128`: `[0.43%, 5.52%]`

Shared targets do not rescue the comparisons: successes of the random and coordinate sets were disjoint in every frozen pair, leaving only small discordant counts. The apparent `5/128` versus `4/128` rational-union signal at 19 field bits is noise under both paired and exact-support analyses.

**Required correction:** replace target-sample ratios as the primary finite result with exact fivefold support. Retain the 128-target data only as a sampler calibration check.

### HIGH-3 — The scoped rejection is acceptable only as a promotion disposition

`decision.json` says `reject_scoped`, while the research question asks whether a family merits a larger multi-seed study. With one family seed, one curve per nominal field size, non-monotone subgroup orders, and only two factor-base cardinalities, the run cannot reject persistence of a family-generating rule. It can reject promotion under the frozen gate and can establish exact finite-set negatives.

The existing conclusion is too broad if “exact representations” means the x-interval, square-map, or rational-union families as distributions. It is too weak about what was actually proved for the sampled sets: all non-control sets hit the exact forced pair-energy floor, and none had larger exact fivefold support than random.

**Required correction:** record `DO_NOT_PROMOTE_FROZEN_CONFIGURATIONS` or an equivalent scoped decision. Preserve the result as:

> `NEGATIVE RESULT`: on the three frozen curves and seeded bases, no coordinate set had a nontrivial pair-energy collision or exact fivefold-support advantage over the matched random set.

Leave the family-level persistence hypothesis `OPEN` pending multi-seed tests.

### MEDIUM-1 — Online cost measures an exhaustive relation census, not one needed witness

The query loop scans every distinct pair sum and accumulates all ordered representation multiplicities even after finding a witness (`coordinate_energy.py:425-441`). The attack subproblem needs one verified witness. The reported `online_group_operations_per_target` is therefore the cost of a full representation census, not a witness query.

A read-only early-stop replay in the existing insertion order reduced the random-control mean scan as follows:

| field bits | full pair-support scan | early-stop mean |
|---:|---:|---:|
| 15 | 33 | 31.195 |
| 17 | 33 | 30.969 |
| 19 | 73 | 71.367 |

The frozen bias is only a few percent because most targets fail and require a full scan, so it does not reverse the gate. It matters conceptually and can matter greatly once success probability rises. Multiplicity counters are likewise unnecessary for an existence-only query; support sets plus one witness per support element suffice.

**Required correction:** report separate `census_query` and `first_witness_query` costs. For relation generation, report expected operations per obtained witness including failed target attempts.

### MEDIUM-2 — Factor-base construction cost is not matched fairly

The random control is generated from known random scalars (`coordinate_energy.py:285-297`), while coordinate families scan x-images, perform square-root tests, and test subgroup membership with a full `qP` multiplication (`coordinate_energy.py:312-360`). This is a fair cardinality/sign control for additive structure, but not a matched construction-cost control.

The mismatch is largest on the 17-field-bit curve, whose subgroup has `q=9,851` and cofactor 13. Random construction used 63 counted group operations; x-interval, square-map, and rational-union used 1,100, 1,144, and 1,980. The resulting offline ratios `3.652`, `3.765`, and `5.903` conflate predicate cost, subgroup density, and construction method.

**Required controls:**

1. A uniform random x-image control using the same square-root and subgroup-membership path.
2. A random-scalar control retained only for structural occupancy.
3. Prime-order curves, or a separately justified subgroup projection/membership strategy, for construction-cost comparisons.
4. Construction costs reported both including and excluding one-time curve/subgroup setup.

### MEDIUM-3 — Operation and memory accounting omit material costs

The accounting is internally reproducible but not a complete algorithmic cost model:

- Square-root tests, Legendre/modular exponentiations, rational-map inversions, Python hashing, dictionary probes, allocation, and memory traffic are not converted into field-operation or time costs.
- `Curve.add` counts identity and inverse-cancellation branches as one group operation even when no field multiplication or inversion occurs. Sign-complete compilation has many such cheap forced cancellations, while rho has a different branch distribution.
- `compiled_storage_deep_bytes` includes only `pair_counts` and `three_counts` (`coordinate_energy.py:472-473`). It excludes `pair_witness` and `three_witness`, which are required to return a decomposition. A read-only Python deep-size replay placed counters plus witness maps at about 2.4 times the reported counter-only bytes for the random controls. This remains implementation-specific, but it demonstrates the omission.
- Peak RSS in the manifests, 22,429,696 bytes for the generator and 26,132,480 bytes for the verifier, is process-wide and not a per-family advice measurement.
- The independent verifier checks that the storage field is a positive integer but does not independently recompute it.

**Required correction:** provide a functional advice layout with support key, witness payload, count only if needed, allocator overhead, bytes per entry, peak resident bytes, and measured lookup/memory traffic. Normalize arithmetic with separate exceptional-add, generic-add, doubling, multiplication, inversion, square-root, and hash/lookup counters.

### MEDIUM-4 — Pollard rho is an arithmetic sanity baseline, not a comparable attack baseline

The rho replay is valid on the same prime subgroup, but its median counted operations are `353`, `369.5`, and `1162`, or approximately `3.40`, `3.72`, and `3.23` times `sqrt(q)`. It uses Floyd cycle detection with three walk steps per loop, three partitions, affine arithmetic, initialization scalar multiplications, no negation-map optimization, and no distinguished-point/parallel baseline.

More importantly, rho outputs a discrete logarithm, while the energy experiment outputs a five-term decomposition with low success and does not collect a full-rank relation matrix, solve logs, or perform target descent. Direct operation ratios would compare unlike outputs.

The current analysis does not claim a rho win, which is correct. Any successor must compare a complete relation pipeline, including rank, linear algebra, individual logarithm/target descent, failure amplification, memory, and fixed-curve preprocessing, against a stronger rho/VOW implementation and an analytic rho baseline.

### MEDIUM-5 — The `S*T^2` fields have no stated theorem, units, or success model

The implementation sets `S=|2A|+|3A|` entries, `T=|2A|` counted additions per exhaustive query, and reports `S*T^2/q` plus `S*T^2/(epsilon*q)` (`coordinate_energy.py:455-491`). This is not interpretable as a preprocessing frontier without specifying:

- the exact inversion/preprocessing theorem and success convention;
- whether `S` is entries, bits, bytes, or cache-line traffic;
- whether pair storage is necessary when the query can generate pairs;
- witness payload and lookup cost;
- whether `T` means a full census, first-witness time, expected time after failures, or parallel depth;
- how observed `epsilon` and the arbitrary `1/128` floor for zero hits enter the bound.

The decision correctly lists a future success-aware measurement. Treat all current `S*T^2` numbers as uncalibrated diagnostics, not evidence for or against a fixed-curve tradeoff.

### LOW-1 — Numeric exponent fits should be invalidated, not merely caveated

The analysis correctly excludes the fitted exponents. The issue is not that regression requires q values to appear in monotone file order; it is that `q=10,799`, `9,851`, and `129,737` provide only two effective scales, `B` takes only 8 and 12, and curve/cofactor effects are confounded with size. The nominal 15/17/19 field-bit labels correspond to subgroup bit lengths of roughly 14/14/17.

Because numeric fields are easy for downstream tooling to reuse, the raw summary should have emitted `null` with an invalidation reason instead of values labelled as exponents. A successor needs monotone, deliberately spaced `q`, at least four to five effective factor-base sizes, multiple curves/seeds per size, and uncertainty on fitted slopes.

### LOW-2 — AppleDouble did not alter arithmetic, but the checked-out artifact state changed during the audit

The generator run committed six 4,096-byte AppleDouble files. All six have Git-tree SHA-256 `cb14168253e45689a3e650cad2d1e8c3923128fe8b238e660151936233df60e7`. The run-1 manifest lists five because the `._manifest.json` sidecar arose outside its artifact scan. Commit `76ff7d5b8ac34ff453b4c47906780213930b81c8` added scoped AppleDouble removal before publication, and run 2 contains only the intended five artifacts.

At the initial audit snapshot, all six run-1 sidecars were tracked in `HEAD` but absent from the working tree (`git status` showed six `D` entries). At the final verification snapshot, all six had reappeared at the tracked paths with no sidecar diff, while unrelated recursive-lane files also changed. No audit command intentionally wrote the source worktree. The source worktree was therefore live or subject to ExFAT metadata regeneration during review, so a single working-tree snapshot is not a durable integrity statement.

This does not invalidate arithmetic: the semantic files retained their hashes, and current read-only verifier execution reproduced run 2 exactly with SHA-256 `1490fb4e7685dae4b3457f53b83e10312e8472a7638926b7d2653a890660706b`. Future wrappers should reject AppleDouble before artifact enumeration, audit from a quiescent checkout, and assert that immutable run paths remain clean after publication.

## Overclaim corrections

| Current interpretation | Defensible replacement |
|---|---|
| Unordered-multiset occupancy closely explains the observed random coverage. | The ordered model is wrong; the unordered model is a better numerical coincidence for this 128-target sample but overcounts exact sign-complete support by 64-74% at the tested `B`. |
| The sampled rational-union `5/128` versus random `4/128` is a largest-size near-signal. | Exact support is tied at 2,668 versus 2,668; the sample difference is noise. |
| `reject_scoped` rejects the tested coordinate representations. | Do not promote the three frozen seeded configurations; family-level persistence remains open. |
| Offline group-operation ratios measure hidden preprocessing cost fairly. | They measure this Python construction schedule against a privileged random-scalar constructor and omit several field/computational costs. |
| Online operations are query cost. | They are exhaustive ordered-representation census cost; first-witness and expected-per-relation costs are separate metrics. |
| Pollard rho is a comparable baseline. | It is a same-arithmetic correctness and rough scale control; no end-to-end attack comparison was performed. |
| `S*T^2` diagnoses fixed-curve viability. | It is an uncalibrated quantity until its theorem, units, advice layout, output task, and success model are fixed. |

## Required controls before a successor interpretation can receive GO

1. Enumerate exact `mA` support at toy `q`; verify sampled-target estimates against it.
2. Compare ordered tuples, unordered point multisets, signed coefficient classes, and sign-canonical formulations explicitly for `m in {5,6,8}`.
3. Use multiple independent curve and family seeds at each of at least four monotone, well-separated subgroup sizes; avoid a minimum-`B` plateau dominating the sweep.
4. Add both random-scalar and random-x/subgroup-filter controls; separate structure fairness from construction fairness.
5. Implement census and first-witness query modes and report expected failed-attempt amplification.
6. Account for functional witness storage, bytes, RSS, memory traffic, lookups, square roots, modular exponentiations, and inversions.
7. Define the fixed-curve preprocessing model and `S*T^2` theorem before interpreting the diagnostic.
8. Compare an end-to-end relation pipeline, including rank and target descent, with analytic rho and optimized rho/VOW baselines.
9. Enforce clean immutable-run paths and reject AppleDouble files before artifact hashing/publication.

## Next falsification tests

1. **Cleanest immediate counterexample test:** for every frozen family, compute exact `|5A|` and compare it with `binomial(B+4,5)` and `D(B/2,5)`. This already falsifies the finite unordered correction and confirms the revised frozen negative.
2. **Sign test:** generate the same fibers in sign-complete and sign-canonical encodings; compare exact support, multiplicity orbits, witness-query time, and functional bytes.
3. **Sampling test:** repeatedly draw 128 targets from each frozen group and measure the distribution of family/random ratios; verify that ratios as large as 1.25 occur under equal-support controls.
4. **Construction-fairness test:** compare random scalar, random x-scan, x-interval, square-map, and rational-union under identical subgroup tests and under prime-order curves.
5. **Witness-only test:** store one witness per support value, stop at first hit, and compare cost/bytes with the current all-representations counters.
6. **Scale test:** preregister monotone `q`, at least four distinct `B`, and multiple seeds; suppress exponent output unless design and residual checks pass.
7. **End-to-end kill test:** collect enough relations to test rank, solve the factor-base logs, and descend held-out targets; charge preprocessing over explicit target counts and compare total work with rho/VOW.

## Handoff: EXP-ECDLP-ENERGY-001 interpretation audit

### Claim or task

Red-team the completed experiment and determine whether its interpretation survives sign symmetry, exact occupancy, fair baselines, complete accounting, and artifact-integrity checks.

### Status

NEGATIVE RESULT

### Assumptions

- `TOY-EVIDENCE`: all exact-support conclusions concern the three frozen toy subgroups and seeded factor bases.
- `MODEL-BOUND`: recomputed operation and Python deep-size observations describe the checked implementation, not a machine-independent cost model.
- The immutable raw arithmetic records are trusted only after hash checks and successful independent verifier replay.
- No asymptotic, deployed-curve, or faster-than-rho claim is inferred.

### Evidence so far

- Both raw arithmetic records hash-match their manifests; current verifier replay reproduces run 2 exactly.
- Exact fivefold supports are `456/456/376/456`, `456/456/400/456`, and `2668/2668/2622/2668` for random/x-interval/square-map/rational-union.
- `binomial(B+4,5)` overcounts the exact random sign-complete supports (`792 vs 456`, `4368 vs 2668`).
- Every tested non-control coordinate base has the exact forced sign-complete pair-energy floor; no coordinate family has an exact fivefold-support advantage.
- The no-promotion result survives, but the occupancy explanation and family-level rejection wording do not.

### Failure modes

- A downstream reader may treat the unordered-Poisson coincidence as a validated occupancy law.
- Sample ratios may be mistaken for structural coverage differences despite exact tied supports.
- Counter-only bytes and exhaustive census operations may be mistaken for functional one-witness advice/query cost.
- Random-scalar construction and the measured rho walk may be mistaken for matched, competitive baselines.
- Numeric toy fits or `S*T^2` fields may be consumed without their invalidation boundaries.
- AppleDouble regeneration or concurrent worktree activity may change the checked-out artifact set during an audit even when semantic run hashes stay fixed.

### Next concrete action

Create a versioned interpretation amendment that replaces the unordered finite-size claim with exact signed-support results, changes the decision to a frozen-configuration no-promotion disposition, and preregisters the controls above before any multi-seed successor run. Do not rewrite either immutable run.

### Artifact paths

- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/experiments/EXP-ECDLP-ENERGY-001/contract.md` — SHA-256 `a4ae563dc74dfec6d276bd40226e967c4e759ee3b9b9373fbd36daaef5872cd9`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/experiments/EXP-ECDLP-ENERGY-001/implementation.md` — SHA-256 `0a823ae70460568bcf1a6bdfd346553b6932e40fcfb683b26ac8865aff26d6fd`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/experiments/EXP-ECDLP-ENERGY-001/specification.json` — SHA-256 `bb6a9a4aee10140db94e130bb8019086b3728813da20da5aec8e3694578e8f12`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/experiments/EXP-ECDLP-ENERGY-001/hypothesis.json` — SHA-256 `a34c50fc09bb0876dd07c49c027beb0d90728d2402684858ecf455d13daa5c6d`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/experiments/EXP-ECDLP-ENERGY-001/src/coordinate_energy.py` — SHA-256 `7e9b16c18c5855ef7786f78d42300e63fb2a3dcf768413355a31d14160c6ea71`; generator manifest commit `3b1ef1f3dcb77675742539bc40683db4b45e5876`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/experiments/EXP-ECDLP-ENERGY-001/src/verify_coordinate_energy.py` — SHA-256 `f81245954e33ef113e35cb4b1cf602a20b5000e2ee7d9ffdaa7fb1e681d1f533`; verifier manifest commit `76ff7d5b8ac34ff453b4c47906780213930b81c8`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/experiments/EXP-ECDLP-ENERGY-001/runs/RUN-ECDLP-ENERGY-001/manifest.json` — SHA-256 `75cf51e3c9ddb8b92d4551b9d333ec0c0c40afd0328c15f3f52260bcba586f9f`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/experiments/EXP-ECDLP-ENERGY-001/runs/RUN-ECDLP-ENERGY-001/raw-result.json` — SHA-256 `6cd94937c425402044d80becfdc209cc39fcfe3e6496308250631ed47338a009`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/experiments/EXP-ECDLP-ENERGY-001/runs/RUN-ECDLP-ENERGY-002/manifest.json` — SHA-256 `8d7b2022355014f36d6e6050c82f6ba2077495d1e12296b2c20bbb0cdcf1eef3`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/experiments/EXP-ECDLP-ENERGY-001/runs/RUN-ECDLP-ENERGY-002/raw-result.json` — SHA-256 `1490fb4e7685dae4b3457f53b83e10312e8472a7638926b7d2653a890660706b`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/experiments/EXP-ECDLP-ENERGY-001/analysis.md` — SHA-256 `fbe9fd02c3b219510ab4e2df33a3168bb198e19f0524df334f7f8649a9fbe1e3`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/experiments/EXP-ECDLP-ENERGY-001/evidence.json` — SHA-256 `320d6d3e7c19f32d147e58d95fab2f434cf9ace35013c14e4cb19972db2a0ca0`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/experiments/EXP-ECDLP-ENERGY-001/decision.json` — SHA-256 `73be46493deb1d2008f22b1af613e610b68446e77e811b2c73a5e457716890c7`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/tests/test_coordinate_energy.py` — SHA-256 `de04fe8368658ff89d2f519049edb15294ce04f38d192e97c66edf5244f4ae2a`
- `/Volumes/Volume/autolab/research/crypto_autoresearcher_exp_ecdlp_energy_001_red_team_20260717.md` — this audit; compute its external SHA-256 after finalization to avoid a self-referential hash.
