# EXP-FROB-30006a — implementation and execution notes

Executor record for handoff `TASK-20260920-66a30e` against the frozen contract
`experiments/EXP-FROB-30006a/specification.yaml` (version 1, approved by
`DEC-20260920-cf8ded`). Observations only: nothing here asserts a verdict under the
pre-registered `decision_rule`, promotes any claim, or interprets the heuristic
`HEUR-FROB-WDSAT-NULL` (a new prior; **not** attributed to `IDEA-20260906-a77711`,
per `DEC-20260920-f1e672`). `IDEA-20260918-9abf42` was read for its dimension table
only (card constraint EX-5).

Run inventory, hashes and per-trial argv are frozen in `trial-plan.json`
(`crypto.autoresearch.trial_plan.v1`); every run directory carries the
reproduction package (`manifest.yaml`, `command.txt`, `environment.json`,
`stdout.log`, `stderr.log`, `raw-result.json`, ANF inputs, certificates, WDSat
`builds/*/config_used.json`, per-process logs).

## 1. What was built (`implementation/`)

| file | role |
| --- | --- |
| `gf2n.py` | GF(2^n) in the polynomial basis (lowest-weight irreducible modulus: `t^41+t^3+1`, `t^43+t^6+t^4+t^3+1`); Koblitz curve `y^2+xy = x^3+ax^2+1` arithmetic, `#E` via the Frobenius trace recurrence, Semaev S3/S4 in Trimoska's elementary-symmetric form; self-tests. |
| `frob_basis.py` | Frobenius-stable subspaces `V_f = ker f(σ)`, `σ: x→x^2`, `f` an irreducible factor of `(T^n−1)/(T−1)` computed from cyclotomic cosets of 2 mod n; random subspaces of matched dimension (rejected and resampled if rank-deficient or Frobenius-stable); RREF/kernel/parity-check linear algebra over F_2. |
| `gen_instance.py` | Weil-descent ANF (WDSat ANF format) of "∃ X_1..X_m ∈ V : S_{m+1}(X_1..X_m, x_R)=0". Variables: `x_{i,k}` (m·l), `e2_j` (n), and for m=3 `e3_j` (n); `e1 = ΣX_i` is substituted as a linear form. Equations: n "E" product equations per e-block plus n "D" descended equations. Modelling is identical for both arms, so the arms differ only in V. Target stream: `random.Random(seed)`, candidate k = k-th uniformly random affine point of E. |
| `pdp_enum.c` / `certify.py` | **Independent certifier** (C, PCLMUL, Gray-code enumeration of V): decides the same algebraic predicate directly over the field — m=2: for every X_1 ∈ V solve the quadratic S3(X_1, ·, x_R) and test membership in V; m=3: for every unordered pair (X_1, X_2) find X_3 ∈ V with Res(p,q)=0 via the common-root / proportional-polynomial case split — plus a rational geometric cross-check. Shares no code with WDSat or with the ANF generator. `certificate.json` binds the verdict to the ANF's sha256. |
| `wdsat_build.py` | Verifies every vendored WDSat source file against `inputs/TRIMOSKA-WDSAT-2024/UPSTREAM_SHA256SUMS.txt` (15 files, all match, recorded in every `environment.json`); sizes `MAX_ANF_ID, MAX_DEGREE, MAX_ID, MAX_EQ, MAX_EQ_SIZE, MAX_XEQ, MAX_XEQ_SIZE, MAX_BUFFER_SIZE` and `__STATIC_CLAUSE_STRING_SIZE__` from the ANF; rewrites `config.h`/`wdsat_utils.h`; builds with the upstream makefile (`gcc -O3 -Wall`, `__XG_ENHANCED__` defined as shipped); records constants, source hashes as shipped and as used, and the binary hash in `config_used.json`. |
| `run_trial.py` | Per-run driver: one invocation = one immutable run directory. Process supervision with a resident-set watchdog (5.5 GB over the child's process group, 0.25 s polling) and per-process wall-clock watchdogs; load average and `MemAvailable` recorded at each process start; manifests with the exact command, git commit read from `.git/HEAD` (no git command was run), dirty-tree flag with per-file sha256 of every implementation file, environment, seeds, inference block, certificate block, validity status and reason. |
| `check_run.py` | Independent completion check used as `check_argv` in the trial plan (manifest/raw agreement, C-CERT, C-SIZE, EX-4, ratio recomputation, on-disk certificate binding). |
| `make_trial_plan.py` | Writes `trial-plan.json` from `run_trial.TRIALS` and the pre-minted run ids. |
| `bin/pdp_enum` | Built from `pdp_enum.c` with `gcc -O3 -march=native -mpclmul`; sha256 recorded in every certificate and manifest. |

### Curves (spec `inputs.curve_family`; order factorisations recorded in every `instance.json`)

| n | a | #E | factorisation | note |
| --- | --- | --- | --- | --- |
| 41 | **0** | 2199025563772 | 2² · 549756390943 (40-bit prime) | a=1 gives 2·739·2543·585071 (20-bit largest), so a=0 chosen |
| 43 | **1** | 8796094020926 | 2 · 947 · 4644189029 (33-bit) | a=0 gives 2²·1033·22877·93053 (17-bit largest), so a=1 chosen |

### Factor bases

* **n=41 stable V** (spec `primary_cell.stable_V`): `(T^41−1)/(T−1)` splits over F_2 into two irreducible factors of degree 20 (`ord_41(2)=20`); `vindex 0` is `g = 0x1b4e5b` (coset {1,2,4,5,8,9,10,16,18,20,21,23,25,31,32,33,36,37,39,40}); `V = ker g(σ)`, dimension 20, verified σ-stable; RREF basis in every `instance.json`.
* **n=41 random V** (`C-RAND`): one dimension-20 subspace from `random.Random(2026092010)` (1 sampling try; not Frobenius-stable), shared by the three random-arm replicates.
* **n=43 stable V**: `(T^43−1)/(T−1)` = three irreducible factors of degree 14 (`ord_43(2)=14`); `vindex 0` is `g = 0x4ff9` (coset {1,2,4,8,11,16,21,22,27,32,35,39,41,42}).
* Dimension table cross-check against `IDEA-20260918-9abf42`: n=41 stable dimensions {0,1,20,21,40,41}, n=43 {0,1,14,15,28,29,42,43} — agree.

### Instance shape and WDSat sizing

| cell | unary vars | equations | `MAX_ID` | `MAX_EQ` | `MAX_XEQ` | `MAX_BUFFER_SIZE` | ANF size |
| --- | --- | --- | --- | --- | --- | --- | --- |
| n=41, m=2, l=20 | 81 (40 x + 41 e2) | 82 | 481 | 1264 | 83 | 60000 | 74 kB |
| n=43, m=3, l=14 | 128 (42 x + 43 e2 + 43 e3) | 129 | 8018 | 26478 | 130 | 827506 | 1.75 MB |

`max_id_anf_match` is `true` on every WDSat row (C-SIZE). The n=43 `MAX_BUFFER_SIZE`
comes from the term-count rule added after the shipped 60000 tripped WDSat's
`__MAX_BUFFER_SIZE__` assertion on a pre-run smoke test (never a scored run).

### Solver configurations

The contract names WDSat but not its flag. Both are run and reported on every
non-decisive instance; neither is selected here:

* `gauss_elim` — `wdsat_solver -i ANF -x` (XORGAUSS Gaussian elimination during search);
* `default` — `wdsat_solver -i ANF` (XOR unit propagation only), under a 600 s
  machine-protection watchdog (the default configuration's tree grows like 2^{ml}
  in the small-cell series, i.e. ~10^6 s at ml=40).

Both binaries are compiled with `__XG_ENHANCED__` as shipped, and WDSat runs its
initial Gaussian elimination (`xorgauss_initiate_from_dimacs`, `wdsat.c:473`) in
**both** configurations; "UNSAT on XORGAUSS init" is parsed as UNSAT with 0
conflicts and flagged `unsat_on_xorgauss_init: true`.

## 2. Runs

All runs were executed sequentially by one shell (`/tmp/frob_batch.sh`, argv
recorded in each `command.txt`): one WDSat process at a time (EX-2). Load average
at each arm's start is in each WDSat row (`loadavg_at_start`); the 1-minute value
of ≈1.0 on every cell after the first is this batch's own immediately preceding
WDSat process — no other workload ran on the machine (4 cores, 16 GB, Xeon).

### 2.1 Regression gate — `RUN-FROB-5016e7` — **C-REG PASS**

Shipped Trimoska `Xn15l5-11-U.anf` (sha256 matches `TRIMOSKA-ECICB-2024/UPSTREAM_SHA256SUMS.txt`), archived reference `EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3/results.jsonl`:

| configuration | archived conflicts | measured conflicts | within 2× |
| --- | --- | --- | --- |
| default | 31257 | **31257** | yes (identical) |
| gauss_elim | 21488 | **21488** | yes (identical) |

Also: the independent certifier declares the shipped U instance UNSAT (exhaustive)
and the shipped S instance `Xn15l5-1-S.anf` SAT with the shipped witness set
{0xb, 0x0, 0xb} found; WDSat's SAT assignment on the S instance decodes to the same
set and verifies on Trimoska's curve. `check_run.py`: OK.

### 2.2 Pipeline control — `RUN-FROB-520e19` — completed, 24/24 agreements

Small-n controls of the whole pipeline, both V kinds, both configurations, every
WDSat verdict compared with the independent certifier; every planted witness
recovered by the certifier; every WDSat SAT assignment decoded and verified on the
field. Conflict counts (context only, not scored):

| row | ml | certifier | gauss_elim conflicts (ratio) | default conflicts (ratio) |
| --- | --- | --- | --- | --- |
| unsat-n17-m2-stable (l=8) | 16 | UNSAT | 127 (0.0039) | 64769 (1.977) |
| unsat-n17-m2-random | 16 | UNSAT | 122 (0.0037) | 65159 (1.988) |
| unsat-n23-m2-stable (l=11) | 22 | UNSAT | 1022 (0.00049) | 4186135 (1.996) |
| unsat-n23-m2-random | 22 | UNSAT | 1021 (0.00049) | 4169743 (1.988) |
| unsat-n31-m2-stable (l=5) | 10 | UNSAT | 0 (XORGAUSS init) | 0 (XORGAUSS init) |
| unsat-n31-m2-random | 10 | UNSAT | 0 (XORGAUSS init) | 0 (XORGAUSS init) |
| unsat-n31-m3-stable (l=5) | 15 | UNSAT | 30770 (5.63) | 30783 (5.64) |
| unsat-n31-m3-random | 15 | UNSAT | 30783 (5.64) | 31744 (5.81) |
| unsat-n23-m3-stable (l=11) | 33 | UNSAT (candidate 1) | resource_exhaustion 600 s | resource_exhaustion 600 s |
| unsat-n23-m3-random (l=11) | 33 | 32/32 candidates SAT | — | — |
| plant-* (4 rows) | — | SAT, witness found | SAT, verified | SAT, verified |

Ratios are conflicts / (2^{ml}/m!). In the m=2 default rows the count is ≈2^{ml}
(ratio ≈2) and in the m=3, l=5 rows ≈2^{ml} (ratio ≈5.6): stable and random agree
to ≈1% in every row where both finished.

### 2.3 Primary cell n=41, m=2, l=20 (null 2^40/2 = 549755813888)

Every replicate: one WDSat instance, target = first candidate of the seed's stream
that the certifier proves UNSAT (exhaustive over 2^20 values of X_1, 1.75 s) with
x_R ∉ V; `max_id_anf_match` true; `check_run.py` OK.

| arm | seed | run | candidates (verdicts) | gauss_elim conflicts | ratio | default |
| --- | --- | --- | --- | --- | --- | --- |
| stable | 2026092001 | `RUN-FROB-1b45b0` | 0: UNSAT | 524348 | 9.5378e-07 | resource_exhaustion (600.1 s, 3.8 MB) |
| stable | 2026092002 | `RUN-FROB-7ffd2d` | 0: UNSAT | 524362 | 9.5381e-07 | resource_exhaustion (600.1 s) |
| stable | 2026092003 | `RUN-FROB-47429f` | 0: SAT (6 witnesses), 1: UNSAT | **0** (UNSAT on XORGAUSS init) | 0 | UNSAT, 0 conflicts (XORGAUSS init) |
| random | 2026092001 | `RUN-FROB-0be765` | 0: UNSAT | 524283 | 9.5367e-07 | resource_exhaustion (600.1 s) |
| random | 2026092002 | `RUN-FROB-31d33a` | 0: UNSAT | 524279 | 9.5366e-07 | resource_exhaustion (600.2 s) |
| random | 2026092003 | `RUN-FROB-ba422f` | 0: UNSAT | 524280 | 9.5366e-07 | resource_exhaustion (600.2 s) |

Counts: attempted 3 / certified UNSAT 3 / scored 3 per arm (`gauss_elim`); the
`default` configuration is scored on 1 stable replicate (0 conflicts) and on none
of the random replicates — its five timeouts are `resource_exhaustion`, never
UNSAT, never a ratio (EX-4). Exact ratios are in each `raw-result.json`
(`conflict_ratio_exact`), e.g. 131087/137438953472.

Medians of the scored `gauss_elim` ratios, reported for the Reviewer without a
verdict: stable {9.5378e-07, 9.5381e-07, 0} → median 9.5378e-07; random
{9.5367e-07, 9.5366e-07, 9.5366e-07} → median 9.5366e-07. In every finished
row the `gauss_elim` count is ≈2^19 (= 2^{l−1}), on both arms.

### 2.4 Decisive cell n=43, m=3, l=14 (null 2^42/6) — `RUN-FROB-c77c53`

See §2.4 outcome below (filled after the capacity-gated attempt finished).

### 2.5 Regression gate re-run with the final code — `RUN-FROB-360b10`

`run_trial.py` and `wdsat_build.py` were edited after `RUN-FROB-5016e7` (below);
the gate was re-run with the final hashes so that every scored cell's
`implementation_sha256` block matches `trial-plan.json`'s `source_sha256`. See
§2.5 outcome below.

## 3. Failed and superseded attempts (preserved, never edited)

* `RUN-FROB-bb2096` (pipeline-control, `implementation_error`): the pipeline plan asked
  for a Frobenius-stable subspace of dimension 15 in GF(2^31); `ord_31(2)=5`, so the
  generator refused (SystemExit) and the driver died before writing a manifest.
  Its `manifest.yaml`/`raw-result.json` were written **post hoc by the Executor** and
  say so; the driver's own instances/logs up to the abort are intact. Fix: catch
  SystemExit in the driver; rows changed to l=5 and an ml=33 bridge row added.
* `RUN-FROB-d172b5` (pipeline-control, `implementation_error`): 10 rows completed, then
  the row `unsat-n23-m3-random` (ml=33 > n=23) found no certified-UNSAT target among 32
  candidates and the driver raised, losing the structured rows (process logs, instances
  and certificates are on disk). Fix: per-row exception isolation and a graceful
  `no_certified_unsat_among_32_candidates` status; every candidate's witness count is
  now recorded (`candidate_survey`).
* Driver edits after `RUN-FROB-5016e7`, all non-scientific: accept pre-existing empty
  `stdout.log`/`stderr.log` redirection targets in a fresh run directory; strip the
  compiled `wdsat_solver` from `builds/` after the run (sources, makefile, `make.log`
  and `config_used.json` with `binary_sha256` stay — the `EXP-ICPERF-e21835`
  convention); parse "UNSAT on XORGAUSS init" as 0 conflicts with a flag; the pipeline
  changes above. The first invocation of the gate refused a directory that already
  held the empty redirect logs; the same run id was then used for the real gate run
  (no measurement preceded it).

## 4. Deviations from the approved protocol and needs for amendment (reported, not written)

1. **Two solver configurations, not one.** The contract names "WDSat" without a
   flag. Both `-x` and default are reported on every non-decisive instance. On the
   n=41 cell the default configuration cannot finish inside any session-scale
   watchdog (≈2^{40} conflicts at ≈3·10^5 conflicts/s), so the scored ratios are
   `gauss_elim` ratios. Which configuration the `decision_rule` refers to needs a
   Coordinator amendment before any verdict is derived.
2. **Zero-conflict certified UNSAT is scored as ratio 0** (`RUN-FROB-47429f`): the
   metric definition admits it, but it is UNSAT by initial linear algebra, not by
   search. Whether such rows count toward the median is a protocol question.
3. **n=43 capacity gate**: see §2.4; a timeout there is an impediment, not evidence
   (spec `budget.n43_note`).
4. **C-CERT variant**: the contract lists "Macaulay2/Singular unit ideal ... or
   exhaustive on a declared reduced fixture"; the certificate used is an exhaustive
   independent enumeration of the *full* instance (2^20 X_1 values at n=41; 2^28
   unordered pairs at n=43), which is stronger than a reduced fixture and needs no
   CAS. Reported for the Validator's judgement.
5. Machine-protection watchdogs (600 s default configuration; 3 h n=43 attempt;
   5.5 GB RSS) are Executor-declared machine protection, not research budgets.

## 5. Unexpected observations (recorded per core rule 8; no interpretation asserted)

* **Stable-arm targets split by the trace of 1/x_R.** `RUN-FROB-47429f` candidate 1
  (stable V, x_R = 0x18ade3b3a79) is UNSAT on XORGAUSS init with 0 conflicts in both
  configurations. Executor's check (not a protocol result): Tr vanishes identically on
  every Frobenius-stable V here (Tr = ((T^n−1)/(T−1))(σ), which kills `ker g(σ)` for
  g | (T^n−1)/(T−1)); on the stable arm Tr(1/x_R) = 1 for exactly that candidate and 0
  for the three certified-UNSAT-after-search / SAT candidates, while the random V has
  nonzero trace on V. This is consistent with the m=2 descended system
  e1²x_R² + e2·x_R + e2² = 1 being linearly infeasible iff Tr(1/x_R)=1 when Tr|V ≡ 0,
  i.e. about half the stable-arm targets would be linearly UNSAT. Not pre-registered;
  a hypothesis for the Reviewer, not a conclusion.
* **n=23, m=3, l=11 (ml > n) with stable V**: candidate 0 has 1056 algebraic witnesses,
  candidate 1 has 0; with random V of the same dimension all 32 candidates have
  422–609 witnesses (expected ≈2^{33}/(6·2^{23})·3! ≈ 500). Recorded in
  `RUN-FROB-520e19/raw-result.json` (`candidate_survey`).
* **m=3 with `-x` is far harder than m=2**: n=23, m=3, l=11 (ml=33) exceeds 600 s in
  both configurations, whereas n=41, m=2, l=20 (ml=40) finishes in ≈21 s with `-x`.
  The m=2 descended equations are linear in the e2 coordinates; the m=3 ones are
  quadratic in the e-coordinates.
* Default-configuration conflict counts at small n track ≈2^{ml}, not 2^{ml}/m! (ratio
  ≈2 for m=2, ≈5.6 for m=3); stable and random agree to ≈1% in every finished row.

## 6. Inference and environment

Every manifest records `requested_policy: executor-implementation`,
`resolved_model_id: claude-fable-5.1 (Cursor cloud agent; user-selected)`,
`model_verified: false` (no adapter backend credentialed), `fallback_used: false`,
`bedrock_prohibition_observed: true`. Environment: Python 3.12.3, gcc 13.3.0,
Linux 6.12.94 x86_64, Intel Xeon, 4 cores, 16 GB (≈6 GB available at start).
Git commit `ce4a99ce228fa9c1c38df4c698e2b716b0c0f318` on
`cursor/semaev-2015-audit-program-5b8b`, dirty tree (this task's uncommitted
artifacts); per-file hashes in each manifest's `code.implementation_sha256`.
