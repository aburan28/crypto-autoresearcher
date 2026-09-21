# design.md -- TASK-20260817-b4b6e4 (executor)

GOAL-HQC-001 / BATCH-dd0901 / EXP-HQC-982268 / H-HQC-18d1b4 (stays PROPOSED).
Authorized by DEC-20260817-2b638b via BATCH-dd0901's dispatch queue.
Claim tier: **TOY, hard ceiling.**

**PRE-REGISTRATION STATUS -- STATED PLAINLY, NOT OVERCLAIMED.** This file is
written and closed BEFORE either driver script is executed and before any datum
of this task exists. The executing session is under a standing instruction not
to commit (the Coordinator archives), so **this pre-registration is NOT
independently anchored**: no pre-fill blob is committed anywhere by this session
and no anchoring claim is made. What IS claimed, and all that is claimed, is
*content corroboration*: both drivers measure `design.md`'s sha256 at launch,
before any statistic is computed, and record it in their results JSON, in
`stdout.log` and in `run_manifest.yaml`; the Coordinator's archive commit fixes
that content. No anchor line is hand-authored into `stdout.log`. This is exactly
the weakness EV-HQC-e458ef O15(a) recorded against BATCH-91929e, restated here
rather than papered over.

**OBSERVATIONS ONLY.** This task applies NO branch of `batch.yaml`'s frozen
reading rule, names no branch, declares the coupled null BLIND in no verdict
sense, concludes nothing about the k-explanation, A17, A5, HQC's DFR or any
standardized parameter set, recommends nothing about scaling or pausing, and
changes no record's status.

## 0. Parameter set and global constants (frozen)

PS-R3: n=7187, n_e=56, n_2=128, dup=1, N=7168, omega=45, omega_r=51,
omega_e=51. `m_load_bearing_order` = 17. k range 2..26 inclusive.
`N_JACK_BATCHES` = 200 (read from the pinned `stage_a.py`, never hard-coded).
Standardized HQC parameter sets are OUT OF SCOPE and unauthorized.

## 1. Zero decoder calls -- fail-closed enforcement

Part A reads committed JSON only. Part B needs `matched_pair.py`'s `arm_hists`,
`matched_pair_stats` and `stage_a.py`'s `evaluable_k` / `hist_of` /
`batch_hists`, and `matched_pair.py` imports `stage_a.py`, so `stage_a` WILL be
imported -- but nothing in it may be CALLED.

Enforcement, in this process only, editing no file on disk:

1. All three modules (`stage_a.py`, `measure.py`, `matched_pair.py`) are loaded
   through the fail-closed `sha256`-pinned loader. Expected pins:
   - `stage_a.py` `06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405`
   - `measure.py` `a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8`
   - `matched_pair.py` `66266a6178eb46e0b37ec0afdb2620064db56bff82318498e2dd83af1bd1c821`
2. Call-counting wrappers are installed on the LOADED module objects'
   `_t_shard` and `decode_blocks` attributes. Each wrapper increments a counter
   and then raises `SystemExit` -- it never delegates. A call is therefore an
   IMMEDIATE ABORT, not a silently counted event.
3. At exit both counters are asserted exactly 0, and all three module sha256
   pins are re-measured ON DISK and asserted unchanged.
4. `decoder_calls_made: 0` is reported in `run_manifest.yaml`.

A non-zero counter, or a changed on-disk pin, is an INFRASTRUCTURE OUTCOME under
AGENTS.md rule 5 -- never a mathematical result.

## 2. PART A -- the zero-decoder-call low-k recompute

Estimator, identical for every cell in this family:

    alpha(k) = -[ log(se_paired_hi(k)) - log(se_paired_lo(k)) ]
               / [ log(T_hi) - log(T_lo) ]

Reported at k = 5, at k = 10, and at EVERY k in 2..26 that both arrays cover.

### 2.1 The four FRESH cells (windows, T values -- frozen)

Source, READ-ONLY:
`coordination/goals/GOAL-HQC-001/batches/BATCH-91929e/tasks/TASK-20260817-c603c0/cross_regime_arms_results.json`,
node `per_shard_per_window.shard_<S>.<W>.per_k.{ks, se_paired, se_unpaired, unpaired_over_paired_ratio}`.

| cell | lo window | T_lo | hi window | T_hi |
|---|---|---:|---|---:|
| (5000, P) | P1 `[30000:35000)` | 5000 | P2 `[35000:45000)` | 10000 |
| (5000, N) | N1 `[45000:55000)` | 10000 | N2 `[55000:75000)` | 20000 |
| (8002, P) | P1 `[30000:35000)` | 5000 | P2 `[35000:45000)` | 10000 |
| (8002, N) | N1 `[45000:55000)` | 10000 | N2 `[55000:75000)` | 20000 |

### 2.2 The three pre-registered contrasts (frozen definitions)

At every k:
- `regime_main_effect` = mean(P cells) - mean(N cells)
- `shard_main_effect`  = mean(5000 cells) - mean(8002 cells)
- `interaction` = (a(5000,P) - a(5000,N)) - (a(8002,P) - a(8002,N))

### 2.3 The two 4-point ladders

Per shard S in {5000, 8002}: OLS of log(se_paired(W,k)) on log(T(W)) over the
four windows P1 (T=5000), P2 (T=10000), N1 (T=10000), N2 (T=20000);
`alpha_ladder = -slope`. Method: `numpy.polyfit(logT, logSE, 1)`.
Reported with residual RMS = `sqrt(mean(resid^2))` (n=4, NOT n-2) and the OLS
standard error of the slope = `sqrt( (sum resid^2 / (n-2)) / sum((x-xbar)^2) )`.
Reported at k=5, k=10 and every k in 2..26.

### 2.4 The same-T noise handle

`D_shard(k) := |log2( se_paired(P2, k) / se_paired(N1, k) )|` per shard.
P2 and N1 are both T=10,000, same shard, same jackknife batch size 50, same
procedure, same call, disjoint indices, so anything differing between them is
sampling realization BY CONSTRUCTION.
`D_RMS(k) := sqrt( mean over shards {5000, 8002} of D_shard(k)^2 )`.
Reported at EVERY evaluable k. **Stated limit, not softened:** it is a SCALE
FROM n = 2 CONTRASTS, not a distribution; no confidence interval is computable
from it and none is claimed (EV-HQC-e458ef boundaries).

### 2.5 The four HISTORICAL cells -- the reconstruction and its FAIL-CLOSED gate

The mapping below is **BATCH-dd0901's Coordinator's RECONSTRUCTION and is NOT
asserted as fact here**. It is transcribed verbatim from
`batch.yaml: the_four_historical_cells_and_their_reconstruction`, and this task
neither extends it nor searches for an alternative.

| cell | T_lo | lo array (exact JSON path) | T_hi | hi array (exact JSON path) |
|---|---:|---|---:|---|
| (5000, P) | 5000 | `BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair_results.json` -> `stage_1.matched_pair.per_shard.shard_5000` | 10000 | `BATCH-0e126d/tasks/TASK-20260814-8bbdd2/matched_pair_repeat_results.json` -> `matched_pair.per_shard.shard_5000` |
| (6000, P) | 5000 | same file -> `stage_1.matched_pair.per_shard.shard_6000` | 10000 | same file -> `matched_pair.per_shard.shard_6000` |
| (8001, N) | 10000 | same file -> `stage_2.matched_pair.per_shard.shard_8001` | 20000 | `BATCH-174014/tasks/TASK-20260815-e61cca/shard_8001_8002_discard_prefix_results.json` -> `matched_pair.per_shard.shard_8001` |
| (8002, N) | 10000 | same file -> `stage_2.matched_pair.per_shard.shard_8002` | 20000 | same file -> `matched_pair.per_shard.shard_8002` |

Arrays used: `ks` and `se_paired`; `n_batches` recorded beside each.

**THE GATE.** For each cell, compute `alpha_17` from the two arrays ACTUALLY
selected and require

    | alpha_17_recomputed - alpha_17_committed |  <=  1e-12   (absolute)

against the committed comparators
`(5000,P) = +2.836`, `(6000,P) = +1.402` (EV-HQC-469c08 O6),
`(8001,N) = -0.2682495157085447`, `(8002,N) = -0.8662355237627483`
(EV-HQC-927899 O3-O4, reproduced in `e61cca`'s
`single_shard_only_local_exponent`).

The gate is evaluated BEFORE any low-k value from that cell is reported.

- **PASS** -> the cell's low-k values are reported.
- **FAIL** -> the cell is marked `DATA_AVAILABILITY_OUTCOME`. The mapping is NOT
  adjusted, NO alternative pairing is searched for, and the cell is NOT dropped:
  the selected arrays, the recomputed value, the committed value and the
  absolute residual are reported. Cells that pass continue.

`historical_cell_reconstruction.json` is written **UNCONDITIONALLY**, whatever
the verdicts.

**A COMPARATOR-PRECISION FACT, DECLARED IN ADVANCE SO IT CANNOT BE MISTAKEN FOR
TUNING.** Two of the four comparators, `+2.836` and `+1.402`, exist in the
committed record only at four significant figures (EV-HQC-469c08 O6, sourced
from BATCH-0e126d review TASK-20260814-a49f1c's table, whose own SE inputs are
themselves printed to six decimals). A 1e-12 absolute gate against a
four-significant-figure decimal can only pass if the underlying full-precision
value happens to be exactly that decimal. **The gate is nevertheless applied
exactly as specified at 1e-12 and its verdict stands as the verdict.**
Additionally -- clearly subordinate, explicitly NOT a second gate, NOT a
substitute verdict, and NOT capable of turning a FAIL into a PASS -- each cell
also reports `residual_vs_printed_precision_halfulp`, i.e. the residual compared
against half an ulp of the comparator's printed precision, purely so the
Coordinator can see whether a FAIL is a rounding artifact of the comparator or a
mapping error. The reported `gate_pass` field is the 1e-12 field and nothing
else.

### 2.6 The procedural asymmetry -- declared, not left for a reviewer

In every HISTORICAL cell the two T-points come from DIFFERENT tasks in DIFFERENT
processes (different machines, OS, Python and numpy versions). In all four FRESH
cells both T-points are sliced from ONE call in ONE process (EV-HQC-e458ef O4,
O18). The per-array `n_batches` is recorded for every array read. This asymmetry
is a STANDING LIMITATION of any fresh-versus-historical comparison and is stated
in `low_k_report.md`.

### 2.7 Committed-value verifications run BEFORE any new number is reported

Each is reported with its measured residual. **A FAILURE OF ANY OF THESE IS A
FINDING TO REPORT, NOT A NUMBER TO TUNE.** No array selection, window pairing,
tolerance or fit method will be adjusted to make one pass.

| # | check | comparator | tol |
|---|---|---|---|
| V1 | four fresh cells at k=17 | 2.0488128380076307 / 2.960737268597787 / 0.32362272345795423 / 1.5943364808460014 | 1e-12 |
| V2 | three contrasts at k=17 | -1.091319093989102 / 1.545795451150731 / 0.3587893267978908 | 1e-12 |
| V3 | four fresh cells at k=2 | 0.580733 / 0.506553 / 0.628397 / 0.511866 | 1e-4 |
| V4 | ladders at k=17 | 0.4734 (5000, resid RMS 1.008) / 0.0115 (8002, resid RMS 0.514) | 1e-3 |
| V5 | noise handle at k=17 | 4.063 (5000) / 1.895 (8002), RMS 3.170 | 1e-3 |
| V6 | noise handle at k=2 | 0.061 (5000) / 0.105 (8002) | 1e-3 |
| V7 | historical gate | section 2.5 | 1e-12 |

## 3. PART B -- the coupled-arm null band

### 3.1 The single structural change

    base   ~ Binomial(n_e - 1 = 55, p)                 per trial
    arm_i  =  base + Bernoulli_i(p)                    i in {0, 1}

with an INDEPENDENT Bernoulli per arm. Each arm's marginal law is therefore
Binomial(56, p) EXACTLY -- identical to BATCH-91929e's arms -- so any change in
the band is attributable to the coupling ALONE. This replaces
`null_object_control.py:256-257`'s two independent streams. **The realized
marginal mean and variance of each arm are measured and reported against
Binomial(56, p)'s `56p` and `56p(1-p)` with the Monte Carlo standard error of
each, and that check is what makes the comparison controlled.**

### 3.2 What is UNCHANGED (frozen)

- **p = 0.31923392857142857**, FROZEN at BATCH-91929e's calibrated value and
  **NOT re-calibrated here**. Re-calibrating would confound the coupling change
  with a calibration change.
- Ladder: T in {5000, 10000, 20000, 40000} (jackknife batch sizes 25, 50, 100,
  200). Rung pair 5000->10000 is regime P; 10000->20000 is regime N.
- **R = 200** replicates.
- Estimator path: the same pinned `mp.arm_hists` -> `sa.evaluable_k` ->
  `measure.comb_matrix` -> `mp.matched_pair_stats` (-> `measure.log2_A_from_hists`)
  -> 2-point-OLS-in-log-log chain, imported READ-ONLY. Both of
  `matched_pair.py`'s fail-closed selftests run before any statistic.
- **Reuse claim, with its disclosed exception in the same bullet:**
  `arm_hists`, `matched_pair_stats`, `evaluable_k`, `comb_matrix`,
  `log2_A_from_hists` and both selftests ARE imported, never re-derived. The
  bootstrap utilities `sha256_file`, `core_seconds`, `git_state` and the
  fail-closed loader MUST be locally re-defined, because `matched_pair.py`'s own
  loader cannot load `matched_pair.py` -- the chicken-and-egg exception
  EV-HQC-469c08 O10 recorded. The local copies are verified byte-identical to
  the pinned originals' source text at run time and the verdict is reported.

### 3.3 k values

k = 5 and k = 10 as the directive names, **PLUS k = 17 as a REQUIRED COMPARISON
POINT, declared here as a STRICT ADDITION and NOT a substitution** -- without it
the coupled band cannot be compared against BATCH-91929e's uncoupled widths
2.788 / 3.188 or the reviewer-built coupled widths 3.398 / 3.508 / 4.326.

### 3.4 The five banded contrasts -- each DIRECTLY simulated

Per replicate, FOUR independent null cells are drawn -- labelled (5000,P),
(5000,N), (8002,P), (8002,N) by rung pair, plus a fifth independent cell used
only for the replication delta -- and all five quantities are formed from them
directly. **No single alpha is banded and algebraically rescaled**; that is the
exact defect DEC-20260817-2b638b rationale item (j) named.

1. `single_cell_alpha`
2. `regime_main_effect` = mean(P cells) - mean(N cells)
3. `shard_main_effect` = mean(5000 cells) - mean(8002 cells)
4. `interaction` = (a(5000,P) - a(5000,N)) - (a(8002,P) - a(8002,N))
5. `replication_delta` = difference of two independent same-(shard, regime) alphas

Each reports its OWN mean, SD and 2.5 / 50 / 97.5 percentiles at each of
k = 5, 10, 17, and its MEASURED SD ratio against `single_cell_alpha`'s SD beside
the analytic factors under cell independence: **1.000, 1.000, 1.000, 2.000,
1.414**. **A discrepancy above 10% is REPORTED AS A FINDING, not smoothed.**

Note on independence: the "shard" label carries no distinct law in the null --
the null object is shard-free by construction -- so the four cells are four
independent draws from the same law and the analytic factors above follow from
cell independence alone. This is stated so no reader mistakes the labels for
structure.

### 3.5 The two blindness tests -- pre-declared, mandatory, mechanical

- **SHAPE.** Is the coupled null's median `se_unpaired/se_paired` at order k
  inside the closed range spanned by the EIGHT real cells' values at the same k?
  At k=17 that range is [2.338, 28.691]; BATCH-91929e's uncoupled null returned
  0.9965 and would have been declared SHAPE-BLIND by this test in advance. The
  real cells' range at k=5 and k=10 is computed from committed arrays in Part A
  so the test is evaluable at every k the rule uses. `PASS` = inside.
- **POWER.** For each banded contrast at order k, its minimum detectable effect
  -- the smallest |contrast| its own 95% interval could ever declare outside --
  is `MDE = max(|p2.5|, |p97.5|)`. `PASS` = MDE <= 3.702 alpha units, the entire
  historical exponent spread; `FAIL` = MDE > 3.702.

Both are reported as PASS/FAIL at each of k = 5, 10, 17 **WITHOUT
interpretation**. The executor does NOT declare the control BLIND in a verdict
sense; `batch.yaml`'s frozen rule reads the two tests.

### 3.6 No planted-departure leg -- a DECLARED substitution

BATCH-91929e's plant class was shown incapable of firing at ANY magnitude (rho
peaks near 1.3462 at g=2 and REVERSES to 0.8688 by g=50 against a required
2.5256), and its "forced identity" check was an algebraic tautology whose
residual measures float64 rounding (EV-HQC-e458ef O10, O11). Neither is re-run
and NO substitute leg is invented. The two structural tests above replace it.

### 3.7 The cost-projection reduction protocol -- applied in order, never improvised

After the first 20 replicates of the T=40000 rung, project total Part B cost
from measured per-replicate cost and write the arithmetic to
`cost_projection.json`.

1. If the projection exceeds **60% of the 150 core-second authorization**
   (= 90.0 core-seconds), reduce R to the largest multiple of 50 that fits,
   **floor 100**.
2. If R would fall below 100, instead restore R=200, **drop the T=40000 rung**,
   and re-project.
3. If still infeasible, report Part B as **UNDERPOWERED** with the achieved R
   and rungs, and do NOT present its bands as a calibration.

`cost_projection.json` is written **UNCONDITIONALLY**, recording
`no_reduction_fired: true` when nothing fires, and the achieved R and rungs.

### 3.8 Randomness

`numpy.random.Generator(PCG64(SeedSequence([BASE_SEED=20260817, T, r, cell, stream])))`,
where `cell` in 0..4 indexes the five independent null cells and `stream` is 0
for the shared base and 1+i for arm i's private Bernoulli. Every draw is
reproducible from this specification alone.

## 4. The persist-per-trial-S standing requirement does NOT bind here

**SAID EXPLICITLY RATHER THAN OMITTED.** DEC-20260817-2b638b next_actions item
(3) makes persisting the retained per-trial S arrays a standing requirement
"effective from the NEXT SAMPLING TASK". **This task makes ZERO decoder calls
and samples no shard, so it is not a sampling task and the requirement does not
bind on it.** It is carried forward BY NAME to the next sampling task in this
family (the next task that calls `stage_a._t_shard`), and is restated in
`run_manifest.yaml`.

## 5. Budget (hard limits)

300 wall-clock seconds, 150 core-seconds, 4 GB, maximum_runs 2, **0 decoder
calls**. MEASURED core-seconds and wall-clock are reported SPLIT BY PART; spend
is never estimated after the fact.

## 6. Standing reporting requirement

Wherever `low_k_report.md` characterises the 2-point local exponent, it records
VERBATIM: "4-rung OLS in log-log on identical data, SD 0.234334 against
0.700666, a 2.99x noise reduction at zero cost." A `dominated_by: null` there
would be a FABRICATION under AGENTS.md rule 9. This batch's OWN measured SD of
the 2-point estimate and of the 4-rung OLS on ITS coupled replicates is reported
beside those committed uncoupled figures.

## 7. Artifacts -- exactly twelve, all unconditional

`design.md`, `low_k_recompute.py`, `low_k_recompute_results.json`,
`historical_cell_reconstruction.json`, `coupled_null_control.py`,
`coupled_null_control_results.json`, `coupled_null_replicate_summary.csv`,
`cost_projection.json`, `low_k_report.md`, `run_manifest.yaml`, `stdout.log`,
`stderr.log`. Nothing outside
`coordination/goals/GOAL-HQC-001/batches/BATCH-dd0901/tasks/TASK-20260817-b4b6e4/`
is created or modified. If Part A aborts on the reconstruction gate,
`low_k_recompute_results.json` is still written carrying
`status: aborted_on_reconstruction_gate`.
