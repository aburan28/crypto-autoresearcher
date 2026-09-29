# EXP-PFDR-cbdefb — implementation note (TASK-20260903-6745ea)

Executor implementation of the frozen, approved contract
`experiments/EXP-PFDR-cbdefb/specification.yaml` (status `approved`,
`approved_by: coordinator`, approval commit `c5742969`, DEC-20260903-93862f).
Dependency TASK-20260903-ba41aa satisfied at meter commit `2d2083e5`
(`harness/macaulay_fp/`, `tests/test_macaulay_fp.py`: 52 passed in this
session BEFORE the first official run). Ordering condition satisfied:
EXP-PFDR-fd901a (commit `1b49d491`) and EXP-PFDR-5726af (commit `89dc58e3`)
are snapshotted; their values used here are listed in `stage0-transfer.md`
section 4. Repository HEAD at run time: `3029ff14` for every run (tracked tree
clean, `dirty: false`; the only untracked paths are this experiment's
deliverables and the concurrent executors' files), unless a manifest says
otherwise (see execution-report.yaml `anomalies`).

Observations only. Nothing here supports, refutes or closes any hypothesis;
the frozen prediction is read, never adjusted; no status is touched.

## 1. Files

| path | role |
|---|---|
| `stage0-transfer.md` | Stage 0 (zero compute): dictionary, the two non-transferring steps, the null / analogue-constant table, the sibling inputs, the frozen prediction restated |
| `stage1-closure-convention.md` | the FROZEN closure convention, its derivation from Huang-Kosters-Yeo's definition, the censoring flag and completeness certificate, the known-answer fixtures and the F_2-fixture substitution, the s = 1 slice design, the engine policy, the pre-declared Stage 4 analysis choices, the seeds; sha256 `99190ce39524669056e818bcbc510c9699baf2beabdafaddf2c2663ae93f6437` recorded in every manifest under `inputs.parameters.closure_convention_sha256` |
| `closure.py` | the closure instrument: two engines (the meter's `Echelon` as reference; an exact dense float64/BLAS RREF as accelerator), the graded-rank layers for P1, the zero set / ideal dimensions / completeness certificate, `measure_system` |
| `run_cbdefb.py` | the run script (subcommands `s1slice`, `fixture`, `dffagree`, `cell`, `equalds`, `m3cell`); every official run goes through `harness.runner.run_wrapped` (wrapper-measured wall time) and gets a `package-sha256.json` sidecar |
| `analyze.py` | Stage 4 (zero compute): reads `runs/*/raw-result.json` only, writes `analysis.md` and `analysis.json` |
| `runs/RUN-PFDR-cbdefb-*/` | one immutable directory per planned run: `manifest.yaml`, `command.txt`, `environment.json`, `stdout.log`, `stderr.log`, `raw-result.json`, plus the sidecar |
| `analysis.md`, `analysis.json` | Stage 4 output |
| `execution-report.yaml` | per-run terminal status, stage report, stopping rules, deviations, anomalies, certificates, inference block, completion gate |

## 2. What is measured, exactly

- Ring: `harness.macaulay_fp.Ring(p, n_sq = m s, n_free = 0)`, the multilinear
  quotient B = F_p[a]/(a(a - 1)); generator S~ = S_3(ell_1, ell_2, x_R)
  reduced in B with ell_k = sum_i 2^i a_{k,i} (`digit_presentation`,
  `substitute`); S_3 written from scratch (`s3_dict`, the same text as
  EXP-PFDR-5726af's) and cross-checked at 20 random points per draw against
  `harness.semaev.s3_eval`. S_4 (m = 3) by the sympy resultant of the
  from-scratch S_3, cross-checked by vanishing on random planted triples.
- The closure: `stage1-closure-convention.md` section 1 (implemented in
  `closure.py`), D from deg S~ to D_max = 7; per degree: dim W_0, dim V_{F,D},
  the fall-space dimension, the fall flag, the iteration count and the per-pass
  (rows multiplied, pivots inserted) record. d_ff / d_lf / the fall history per
  system; `no_fall_in_window`; the completeness certificate and
  `right_censored`; the graded-rank (per-layer meter) first fall on the same
  system and `closure_dff_equals_graded_dff` (P1).
- Arms per (s, p) cell: Semaev (8 curves x 5 targets = 40 draws); NULL-1
  `support_matched_system` per draw, seeds 7, 11, 13, 17, 19 (200 systems);
  NULL-2 (own `random_blockdegree_poly`: uniformly random multilinear
  polynomial with per-block degree <= 2, coefficients uniform in F_p) and
  NULL-3 (`block_factored_system`, product of uniformly random degree-2 forms
  per block), both computed ONCE per (p, s, seed) with the frozen seeds and
  reported per draw by reference (deviation D-NULL-ONCE); the non-curve cubic
  (8 nodal cubics, seeds 3101..3108, x 5 root targets); the y^2 = f(x)
  soundness subsample on the target-seed-5 draws (20 percent): zeros of S~ on
  the digit cube by exact evaluation, the fraction with a non-square
  right-hand side, and the planted digit vector's membership.
- Curves: EXP-PFDR-5726af's construction verbatim (SHA-256 draws, rejection
  of j in {0, 1728}, singular curves, and fewer than two on-curve x in [0, 4)).
  Targets: 5726af's construction verbatim at window [0, 4) (so the
  CTRL-DFF-AGREEMENT instances coincide with that package's: a = 527, b = 72,
  x_R = 2374 for (1101, 1) at p = 4099), with the window in the RNG tag for
  other windows ([0, 2) at s = 1; [0, 64) for the equal-d^s arm).
  Certificate `{kind: decomposition}` per target, re-verified by a second
  affine addition in the script and by `harness.semaev.verify_decomposition_certificate`
  (the wrapper re-verifies the manifest-level certificate independently).
  Non-curve root targets carry `{kind: s3_root}` re-verified by
  `harness.semaev.s3_eval`.
- Engines and cross-checks: policy in the note, section 7. Wherever both
  engines ran the histories agreed integer for integer (`analysis.md`
  section C); the dense engine's exactness bound p^2 (N + 1) < 2^53 is
  asserted at construction.
- Budget enforcement: `RLIMIT_AS` = 8 GB; `signal.alarm(7200)` per run
  (raises inside the measurement, caught, written as `failed_infrastructure`
  with the partial draws preserved); a guard at 6600 s stops STARTING new
  systems and makes the run `failed_infrastructure`; pre-flight counts per
  ring against the 50,000-column / 4 GiB dense-equivalent gate; BLAS threads
  pinned to 1 (one worker).

## 3. Planned runs and the order actually executed

| # | run id | stage | content |
|---|---|---|---|
| 1 | `RUN-PFDR-cbdefb-fixture` | 1 | CTRL-KNOWN-ANSWER-FIXTURE: planted-fall fixture P (seed 5, squarefree n = 10 and ordinary n = 3), hand fixture H |
| 2 | `RUN-PFDR-cbdefb-s1-slice` | 1 | CTRL-S1-BASELINE: s = 1, three primes, 8 curves, 5 targets at window [0, 2); digit form, 84cdb7's literal direct list, the reduced-generator polynomial-ring list |
| 3 | `RUN-PFDR-cbdefb-dff-agreement` | 1 | CTRL-DFF-AGREEMENT on EXP-PFDR-5726af's p = 4099 instances, s = 2..5 |
| 4-18 | `RUN-PFDR-cbdefb-m2-s{s}-p{p}` | 2 | the 15 ladder cells, s = 1..5 x p in {4099, 16411, 65537}, all arms |
| 19-21 | `RUN-PFDR-cbdefb-equalds-d{d}-s{s}` | 2 | CTRL-EQUAL-DS-SPREAD, (2, 6), (4, 3), (8, 2) at B = 64, p = 65537, D <= 6 |
| 22-23 | `RUN-PFDR-cbdefb-m3-s{2,3}` | 3 | optional m = 3 cells (gated open by 5726af's H-TOP) |

Stage 2 was started only after the three Stage 1 runs were read
(stopping rule 1); cells were run in increasing s, all three primes per s,
with stopping rules 2 and 3 evaluated between s-levels (execution-report.yaml
`stopping_rules`).

## 4. Deviations and disclosures (every one also in execution-report.yaml)

- **D-F2-FIXTURE-SUBSTITUTED.** The F_2 Weil-descent known-answer fixture
  is not exhibited: conformance to Theorem 2.6's "reducible for k" cannot be
  established from the retrieved statement (proof bodies not read by the
  proposing session; no web access here). The contract's sanctioned
  substitute, the planted-fall fixture, is the known answer (note section 4).
- **D-ENGINE.** The closure's linear algebra is the meter's `Echelon` for
  every system with at most 256 columns and on the declared subsample above
  it; above 256 columns the measurement is an exact dense float64/BLAS RREF
  written for this experiment (`closure.py: DenseRREF`), because the meter's
  dict-row engine takes 110-183 s per s = 5 Semaev system (scratch benchmark)
  against ~9 s dense, i.e. the (5, p) cells would not fit the 7200 s cap with
  the meter alone. Exactness is by the 2^53 bound; agreement with the meter
  is required and recorded wherever both ran (every s <= 4 system, every
  fixture, the s = 5 subsample).
- **D-NULL-ONCE.** NULL-2 and NULL-3 take no curve or target input; with the
  frozen seeds used verbatim they were computed once per (p, s, seed) — 5
  objects per cell per arm — and reported per draw by reference (the same
  disclosure as EXP-PFDR-5726af's D-NULL2-ONCE). NULL-1 depends on the draw's
  support and was computed per draw (200 systems per cell).
- **D-S1-DIRECT-LISTS.** The s = 1 slice runs three generator lists (note
  section 5). The scratch dry run showed that Huang-Kosters-Yeo's closure on
  84cdb7's literal direct list (unreduced S_3, nominal degree 4) falls at 4
  while the digit closure falls at 3; the reduced-generator polynomial-ring
  list reproduces the digit history exactly. The note's sections 2 and 5 were
  worded accordingly BEFORE the first official run; the dry runs are D-SCRATCH.
- **D-ITERATION-COUNT-RULE.** At s = 1 (n = 2, B has four monomials) the
  cumulative Macaulay space at D = 3 already equals the ideal, so the closure
  multiplies the fallen rows and inserts nothing: the fall at 3 carries
  iteration count 1. Contract invalidation rule 3 is applied LITERALLY in the
  analysis: such a fall ENTRY is invalidated (the draw's d_ff / d_lf are read
  from the surviving entries; raw closure values are shown beside them), and
  the event is reported as a protocol event with the saturation diagnostic
  (`W0_saturated`: dim W_0 = dim(I cap B_{<=D}) at that degree). The Stage 1
  fixtures P and H, which the contract names as the instrument's known
  answers, carry iteration count 2 at their planted falls, so the instrument
  iterates; the "return to Stage 1" the rule prescribes is satisfied by those
  fixtures and Stage 2 proceeded with the rule applied to every cell.
- **D-CLOSURE-DIAG.** The per-degree diagnostic `dim_I_at_D` /
  `W0_saturated` was added to `closure.py` after runs 1-2 and before run 4
  (run 3 was in flight and was not touched); it changes no computed metric.
  Runs 1-2 were re-executed into the scratchpad with the final code and their
  `metrics` compared with the official packages (execution-report.yaml
  `anomalies`, A-CLOSURE-DIAG-RECHECK).
- **D-SCRATCH.** Before the first official run: scratch prototypes and
  benchmarks of the closure (s = 2..5 on the 5726af instance), the
  certificate, the dense engine, and dry runs of every subcommand into the
  session scratchpad (`--out-root`); a dry (4, 4099) and (5, 4099) cell for
  timing ran concurrently with the first official runs. None is a run record;
  none changed the frozen prediction or the criteria.
- **D-CONCURRENT-LOAD.** Wall times are covariates: the host's four cores
  were shared with another executor's session throughout and, during runs
  1-3, with this session's own scratch timing runs. Every official run was
  executed sequentially (one worker); no official run overlapped another.
- **D-INFERENCE.** As in the sibling packages: `AUTORESEARCH_POLICY` was not
  set for the run processes (the adapter would then assert
  `model_verified: true` for `claude-sonnet-5`, not known to be true of this
  session); the wrapper's own `inference` block records the harness default
  (`requested_policy: executor-terra`, "no model in the loop" — the
  `_inference_block` shadowing already reported by EXP-PFDR-fd901a D9/A4;
  `harness/` is outside this task's write scope); the session's block
  (requested `executor-implementation` / medium, adapter resolution
  `anthropic:claude-sonnet-5 (effort=medium)`, runtime-reported
  `claude-fable-5-1`, `model_verified: false`, `fallback_used: unknown`,
  independent session, no Bedrock, no degradation) is in every manifest under
  `inputs.parameters.session_inference`.
- **D-GIT-READONLY.** The handoff says "never run git"; read-only
  `git rev-parse` / `status` / `log` / `diff` / `show` / `ls-files` were run by
  the wrapper and the script to record the commit, dirty state, meter commit
  and dirty-tree hash the manifests require. No git write; nothing committed.
- **D-PACKAGE-SIDECAR.** Each run directory carries a seventh file
  `package-sha256.json` (per-file sha256 of the six required files), written
  immediately after the wrapper returned, because a manifest cannot contain
  its own hash.
- **D-M3-S3-ABOVE-DMAX.** At (3, 2, 3) the reduced S_4 generator has digit
  degree 9 > D_max = 7 (ell_k^4 has degree 3 in three squarefree variables),
  so no layer exists below D_max; the cell was run and recorded with empty
  histories (no fall observable; right-censored by construction) rather than
  skipped. NULL-3 at m = 3 (degree-4 forms in <= 3 squarefree variables) and
  at m = 2, s = 1 (degree-2 forms in one variable) vanish identically and are
  recorded degenerate; at (2, 2, 2) NULL-3 is a single monomial and has no
  closure fall (analysis.md section F).

## 5. Environment

Linux 6.18.44-fc-v24 x86_64, 4 cores shared, 15 GB RAM, Python 3.11.15,
numpy 2.4.6 (dense engine only), sympy 1.14.0 (resultant, Tonelli-Shanks,
t-quantile via mpmath in the analysis), PyYAML; no Sage; no scipy.

## 6. Reproduction

From the repository root at commit `3029ff14` with the untracked
`experiments/EXP-PFDR-cbdefb/{closure.py,run_cbdefb.py}` at the sha256
recorded in each manifest's `code.source.files`:

```
python3 -m pytest tests/test_macaulay_fp.py -q                       # 52 passed
python3 experiments/EXP-PFDR-cbdefb/run_cbdefb.py fixture   --run-suffix fixture
python3 experiments/EXP-PFDR-cbdefb/run_cbdefb.py s1slice   --run-suffix s1-slice
python3 experiments/EXP-PFDR-cbdefb/run_cbdefb.py dffagree  --run-suffix dff-agreement
for s in 1 2 3 4 5; do for p in 4099 16411 65537; do
  python3 experiments/EXP-PFDR-cbdefb/run_cbdefb.py cell --s $s --p $p --run-suffix m2-s$s-p$p; done; done
python3 experiments/EXP-PFDR-cbdefb/run_cbdefb.py equalds --d 2 --s 6 --run-suffix equalds-d2-s6
python3 experiments/EXP-PFDR-cbdefb/run_cbdefb.py equalds --d 4 --s 3 --run-suffix equalds-d4-s3
python3 experiments/EXP-PFDR-cbdefb/run_cbdefb.py equalds --d 8 --s 2 --run-suffix equalds-d8-s2
python3 experiments/EXP-PFDR-cbdefb/run_cbdefb.py m3cell --s 2 --run-suffix m3-s2
python3 experiments/EXP-PFDR-cbdefb/run_cbdefb.py m3cell --s 3 --run-suffix m3-s3
python3 experiments/EXP-PFDR-cbdefb/analyze.py
```

(`--out-root DIR` redirects a run package elsewhere; run ids are immutable
and the wrapper refuses to overwrite an existing one.)
