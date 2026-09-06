# EXP-PFDR-5726af — implementation note (TASK-20260903-b0727c)

Executor implementation of the frozen, approved contract
`experiments/EXP-PFDR-5726af/specification.yaml` (status `approved`,
`approved_by: coordinator`, approval commit `c5742969`, DEC-20260903-93862f).
Tooling prerequisite TASK-20260903-ba41aa satisfied at meter commit `2d2083e5`
(`harness/macaulay_fp/`, `tests/test_macaulay_fp.py`). Repository HEAD at run
time: `3a9c1b0257923bf7772b811963beaf57d67aa713`, tracked tree clean
(`dirty: false` in every manifest; the only untracked paths are this
experiment's deliverables and the concurrent executor's EXP-PFDR-fd901a files).
After the last run and before the execution report was written, HEAD advanced
to `1b49d491` (the Coordinator's snapshot of EXP-PFDR-fd901a); that commit
touches neither `harness/` nor this directory (anomaly A-HEAD-MOVED).

Observations only. Nothing here supports, refutes or closes any hypothesis;
the frozen prediction file is read, never adjusted.

## 1. Files

| path | role |
|---|---|
| `stage0-predictions.yaml` | frozen prediction file, written before any official rank; sha256 `e5198d84094fa299933e0f8bbe6c7bcc41e37cce42a9d58854ce5df6cf339e94` in every manifest (`inputs.parameters.stage0_predictions_sha256`) |
| `stage0-htop.md` | the s = 2 hand fixture and the H-TOP symbolic check at m = 3 |
| `run_pfdr_5726af.py` | the run script (subcommands `htop`, `s2gate`, `cell`, `hwil`, `nearby`); every official run goes through `harness.runner.run_wrapped` |
| `runs/RUN-PFDR-5726af-*/` | one immutable directory per planned run: `manifest.yaml`, `command.txt`, `environment.json`, `stdout.log`, `stderr.log`, `raw-result.json`, plus the sidecar `package-sha256.json` (per-file sha256 of the six files; a manifest cannot contain its own hash) |
| `analysis.md` | residual table, null tables, nearby-object table, H-WIL table, tail checks, verdict against the frozen criteria as observation |
| `execution-report.yaml` | per-run terminal status, stage report, stopping rules, deviations, certificates, inference block |

## 2. What is measured, exactly

- Ring: `harness.macaulay_fp.Ring(p, n_sq = m s, n_free = 0)` — squarefree
  digit mode, `a^2 -> a`, coefficients mod p. At d = 2 the membership
  generators `a(a - 1)` ARE the ring quotient, so the system has the single
  generator `S~ = S_{m+1}(ell_1, ..., ell_m, x_R)` reduced in B, with
  `ell_k = sum_i 2^i a_{k,i}` (`digit_presentation`, `substitute`).
- S_3 is written from scratch in the script (`s3_dict`) and cross-checked at
  20 random points per draw against `harness.semaev.s3_eval`; S_4 at m = 3 is
  the resultant `Res_T(S_3(x_1, x_2, T), S_3(x_3, x_R, T))` of the from-scratch
  S_3 (sympy), cross-checked by vanishing on random planted triples.
- Layers: per-layer convention (`analyze_layer(..., "per_layer")`), rows
  `mu * S~` with `deg mu = D - delta` exactly, `leading_forms = False`,
  `frobenius = False` (p odd); `fall_dim(D) = full_rank - top_rank`,
  `d_ff` = least D with `fall_dim(D) > 0`, `fall_dim(d_ff)` the second
  integer. `D_max = D_null + 1` with `D_null = floor((m s + m e)/2) + 1`
  (the 84cdb7 convention `ceil((m s + 2 m)/2)` is recorded beside it in every
  cell's metrics and never used for scoring).
- Arms per cell: Semaev (3 curves x 2 targets x 2 primes = 12 draws at m = 2;
  1 curve x 2 targets x 1 prime at m = 3); NULL-1 `support_matched_system`
  (identical support, coefficients uniform in [1, p-1]) seeds 7, 11, 13, 17, 19
  per draw; NULL-2 `block_factored_system` (product over blocks of a uniformly
  random degree-e form), seeds 7, 11, 13, 17, 19; NULL-3 = the spread of the
  Semaev integers across curves, targets and primes.
- Curves ("generic-j", the contract fixes only the seeds): for prime p and
  curve seed cs, attempt t = 1, 2, ...: `a = SHA256("cs:p:a{t}") mod p`,
  `b = SHA256("cs:p:b{t}") mod p`; reject a = 0 or b = 0 (j in {0, 1728}),
  singular curves, and curves with fewer than two on-curve x in [0, 4).
  Attempt number and rejections are recorded per draw.
- Targets: `random.Random(SHA256("ts:p:cs:target"))` picks m on-curve x in the
  planting window (with replacement) and y-signs; `R = P_1 + ... + P_m`
  (rejecting the point at infinity); `x_R = x(R)`. Planting window [0, 4) at
  m = 2 so the SAME targets serve every ladder cell s >= 2; [0, 16) at m = 3.
  Certificate `{kind: decomposition, target, summands, curve}` per draw,
  re-verified by (i) a second, separately written affine addition in the script
  (`independent_verify`) and (ii) `harness.semaev.verify_decomposition_certificate`
  (via the wrapper for the manifest-level certificate, which is the frozen
  fixture's for the deciding cell and the first draw's otherwise).
- Nearby objects at (2, 2, 3): MIXED-BLOCK `x_k = sum_{i<6} c_{k,i} a_i` with
  all six digit variables shared across k (c uniform in [1, p-1], seeds 31,
  37, 41 per draw); NON-MONOMIAL-TOP in two readings, A: `S_3(ell_1, ell_2,
  x_R) + ell_1^4`, B: the homogeneous `top(ell_1^2 ell_2^2) + top(ell_1^4)`.
- H-WIL: `top_rank` of the meter's leading-form layer for `ell^2` at degree
  j + 2 (multiplication `A_j -> A_{j+2}` in `F_p[a]/(a_i^2)`), for both
  `ell = sum 2^i a_i` (the digit form) and `ell = sum a_i` (Wilson's form),
  s in 2..8, all j with j + 2 <= s, p in {4099, 65537}; an independently
  constructed matrix's rank over GF(p) by sympy `DomainMatrix` beside it.
- Rank oracle: at the s = 2 gate and the deciding cell every layer's full and
  top rank is recomputed by sympy `DomainMatrix` over GF(p) from the same rows.
- sol(D) covariate (IDEA-20260806-7ea402): `sol(D) = [rank(cumulative Mac_D)
  >= ncols(D) - N_sol]`, N_sol counted by brute force over {0,1}^n; computed
  for the Semaev arm where n <= 10, else recorded as not computed.
- Budget enforcement: `RLIMIT_AS` = 8 GB in the run process; a wall-clock
  guard at 1680 s stops STARTING new NULL-1 systems (censoring the rest,
  listed by draw) and any run past 1800 s is marked `failed_infrastructure`;
  a crash or MemoryError inside a run is caught and written as
  `failed_infrastructure`, never as a result.

## 3. Planned runs and stage order actually executed

| # | run id | stage | content |
|---|---|---|---|
| 1 | `RUN-PFDR-5726af-htop` | 0 | CTRL-H-TOP-SYMBOLIC (m = 3, sympy) |
| 2 | `RUN-PFDR-5726af-m2-s2-gate` | 1 | CTRL-S2-HAND-FIXTURE (one curve, one target, p = 4099, oracle) PLUS the full (2, 2, 2) cell (all draws, all nulls) |
| 3 | `RUN-PFDR-5726af-m2-s3` | 1 | DECIDING CELL (2, 2, 3), oracle on every Semaev layer, full profiles to D = 7 |
| 4 | `RUN-PFDR-5726af-hwil` | 1 | CTRL-H-WIL-DIRECT-RANK |
| 5 | `RUN-PFDR-5726af-m2-s4` | 2 | ladder (2, 2, 4), full profiles to D = 8 |
| 6 | `RUN-PFDR-5726af-m2-s5` | 2 | ladder (2, 2, 5), full profiles to D = 9 |
| 7 | `RUN-PFDR-5726af-nearby-s3` | 2 | NEARBY-MIXED-BLOCK, NEARBY-NON-MONOMIAL-TOP |
| 8 | `RUN-PFDR-5726af-m3-s4` | 3 | (3, 2, 4), p = 65537, curve 1101, targets 1, 2, stop at first fall |
| 9 | `RUN-PFDR-5726af-m3-s5` | 3 | (3, 2, 5), same, stop at first fall |
| 10 | `RUN-PFDR-5726af-m2-s6` | 2 | ladder (2, 2, 6), stop at first fall (budget) |

Stage 2 and 3 were launched only after reading the official Stage 1 records:
`gate_pass: true` (run 2), `P1`, `P2`, `P3` all true at the deciding cell
(run 3), `gate_m3_secondary_open: true` (run 1). The s = 6 cell was run last
because it is the longest.

## 4. Deviations and disclosures (every one also in execution-report.yaml)

- **D-RUNS-10.** The contract allows `maximum_runs: 10`; one run per (m, s)
  cell plus H-WIL, H-TOP and the nearby objects would be 11. The contract's
  budget note counts "6 cells" plus H-WIL and H-TOP, i.e. it treats the s = 2
  gate as the s = 2 cell, so the full (2, 2, 2) cell (12 draws, both nulls)
  was computed INSIDE the gate run, before the deciding cell. Consequence:
  the s = 2 ladder entry was not gated on the deciding cell (it costs 0.3 s),
  and there is zero re-run headroom; no re-run was needed.
- **D-STOP-FIRST.** At (2, 2, 6) and at both m = 3 cells every arm is
  computed in increasing D and stops at the first fall (or at D_max). The
  scratch benchmark (below) showed the s = 6 null arms cost ~33 s per system
  to D_max = 10, i.e. ~4000 s for 120 null systems, above the 1800 s per-run
  cap; stopping at the first fall keeps the primary metrics exact and the
  cell inside the cap. The secondary "full rank profile per degree per arm" is
  therefore truncated at d_ff for those three cells (recorded per draw as
  `D_max_computed`). A null that has not fallen by D_max is censored, as the
  contract states. Cells s <= 5 carry full profiles to D_null + 1 on every arm.
- **D-NULL2-ONCE.** The block-factored null takes no curve or target input;
  with the frozen seeds used verbatim the same 5 polynomials would recur for
  every (curve, target) at a prime. They were computed once per (p, seed) and
  are reported per draw by reference (`null2[p=..., seed=...]`), so the
  "5 seeds per (curve, target, p)" count is 5 distinct objects per prime, not
  60. (The concurrent EXP-PFDR-fd901a executor chose the opposite, mixing the
  labels into the seed; both are disclosed.) NULL-1 depends on the draw's
  support and was computed per draw (60 systems per m = 2 cell).
- **D-HTOP-CAS.** Sage is absent on this host. The contract's
  `inputs.symbolic_S4` names no CAS ("S_4 built by resultant ... from a
  from-scratch S_3"); the handoff's constraint text says "missing Sage is
  failed_infrastructure for that stage". The resultant was computed exactly
  with sympy 1.14 over Z[a, b, x_R] and the run is recorded `completed_valid`
  with this disclosure; whether the handoff's Sage clause re-labels it is the
  Coordinator's call. Stage 3 was run on the strength of the sympy check.
- **D-TESTS-ORDER.** `python3 -m pytest tests/test_macaulay_fp.py -q` (52
  passed in 2.35 s) was run in this session AFTER the four Stage 0/1 runs and
  during Stage 2, not before the first official run. The meter files' sha256
  recorded in every manifest equal those in `harness/macaulay_fp/VALIDATION.md`,
  so the code tested is the code executed.
- **D-SCRATCH.** Before the prediction file was written, one scratch timing
  benchmark of the meter (m = 2, s in {3, 4, 5, 6}, p = 4099, ad-hoc curve
  a = 17, b = 23, x_R = 5, one null seed) printed rank profiles; after the
  prediction file was written, dry runs of every subcommand were executed
  into the session scratchpad (`--out-root`), and one scratch benchmark of the
  m = 3 cells at p = 65537 (curve seed 1101) was run to size Stage 3. None of
  these is a run record; none changed the frozen predictions (which are the
  contract's formulas verbatim).
- **D-PRED-DRAFT.** The first draft of `stage0-predictions.yaml` contained an
  Executor arithmetic slip (a_0 at s = 3 and 5) and a spurious
  "discrepancy" note; it was replaced within the same minute, before any
  official rank. The final file discloses this in `disclosures`.
- **D-FIXTURE-NOT-SHARED.** The contract calls the (2, 2, 3), p = 4099,
  curve seed 1101, target seed 1 instance "the frozen fixture shared with
  EXP-PFDR-fd901a", but neither contract froze the curve/target construction.
  This execution's instance is a = 527, b = 72, j = 892, x_R = 2374; the
  concurrent fd901a execution's is a = 941, b = 428, x_R = 3690. The two
  rank profiles at D = 4..6 are identical (full 1, 6, 15; top 1, 2, 1; fall
  0, 4, 14), which is what NULL-3 predicts, but they are not the same
  instance. Both parameter sets are recorded for the Coordinator.
- **D-MIXED-READING.** NEARBY-MIXED-BLOCK "x_k = sum_i c_{k,i} a_i with the
  a_i shared across k" was read with all six digit variables shared (n = 6);
  under the literal three-shared-variable reading `ell_1^2 ell_2^2` has
  degree 4 in a 3-variable squarefree algebra and vanishes, so the object is
  degenerate; recorded, not run.
- **D-NONMONO-COLLAPSE.** NEARBY-NON-MONOMIAL-TOP `x_1^2 x_2^2 + x_1^4` at
  s = 3: `ell_1^4` has no degree-4 part in three squarefree variables, so the
  substituted top form collapses to `x_1^2 x_2^2`. Both readings were run and
  reported as observed; the object does not realise a non-monomial top form
  at s = 3.
- **D-INFERENCE.** `AUTORESEARCH_POLICY` was deliberately not set for the run
  processes (the adapter would then record `model_verified: true` for
  `claude-sonnet-5`, not known to be true of this session, which reports
  `claude-fable-5-1`). The wrapper's `inference` block says "no model in the
  loop" (true of the deterministic script); the session's block (requested
  `executor-implementation` / medium, `model_verified: false`,
  `fallback_used: unknown`) is in every manifest under
  `inputs.parameters.session_inference` and in the execution report.
- **D-GIT-READONLY.** The handoff says "never run git"; read-only
  `git rev-parse`, `git status`, `git log`, `git diff`, `git show` were run by
  the wrapper and by the script to record the commit, dirty state, meter
  commit and dirty-tree hash the manifests require. No git write of any kind
  was made; nothing was committed.
- **D-ARCHIVED-PROFILE.** The archived EXP-ALPF-011 "[4, 4, 4, 12]" cited by
  the derivation as a per-variable profile is a generator-degree list (three
  |FB| = 4 membership polynomials and S_4); see stage0-htop.md section 2.1.

## 5. Environment

Linux 6.18.44-fc-v24 x86_64, 4 cores shared with one other executor, 15 GB
RAM, Python 3.11, sympy 1.14.0, numpy 2.4.6 (present, unused by the meter),
PyYAML; no Sage. One worker throughout (runs executed sequentially).
