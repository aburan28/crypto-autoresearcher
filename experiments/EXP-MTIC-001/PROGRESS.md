# EXP-MTIC-001 execution progress log (Executor, TASK-20260727-001, protocol v2)

Append-only checkpoint log so a crash preserves state. Timestamps UTC.

## Stage 1 — contract validation: DONE (2026-07-28)
- Read: specification.yaml v2 (frozen, approved), amendments/AMEND-001.yaml,
  ledger/handoffs/TASK-20260727-001.yaml, AGENTS.md, docs/task-lifecycle.md,
  docs/evidence-and-reproducibility.md, agents/executor.md, harness/{toycurve,
  semaev,rho,runner}.py, ledger/hypotheses/H-MTIC-001.yaml,
  ledger/proposals/IDEA-20260726-001.yaml, EXP-ENDO-001 conventions
  (code/endo_common.py, code/run_ENDO.py, implementation.md, execution-report.yaml).
- v1 stop report preserved at execution-report-specification-error-v1.yaml
  BEFORE any overwrite (byte copy of the previous execution-report.yaml).
- Contract validation result: PASS, no specification_error. Every frozen
  element is pinned:
  * instances: generate_instance(seed, bits, min_prime_order_bits=bits-2),
    seeds 1->16, 2->20, 3->24 (AMEND-001; probe-verified N=17623/139753/11000719)
  * targets: 50 descent + 2000 harvest per curve, R=aP+bQ seeded, (a,b) recorded
  * factor base: B=ceil(sqrt(N)) via build_factor_base; 20-bit ablation
    [ceil(N^(1/3)), ceil(N^(2/5))]
  * m=3, S_4 via semaev.s4_expr; sympy Buchberger; per-solve cap 60 s,
    capped at full cap cost; per-run cumulative 1500 s; 1800 s hard / 4 GB
  * Wiedemann over Z/N, ~BxB
  * cost model: group-op equivalents; calibrations rho_walk_rate +
    bsgs_construction_rate per size; audit across 3 accountings
  * metrics: t_desc median/IQR, s_rel, s_la, K*, frontier_product_ratio,
    amortized cost at K*/10K*, T_verify, rho/BSGS baselines, yield curve,
    calibration factors
  * controls: CTRL-NONINTERFERENCE (3 hash equalities), CTRL-RHO-BASELINE,
    CTRL-BSGS-BASELINE, CTRL-SINGLE-TARGET, CTRL-CALIBRATION-AUDIT
  * 10 planned runs, required_artifacts per run, frozen-instances.yaml,
    analysis.md, execution-report.yaml
- Within-latitude implementation choices (to be disclosed in implementation.md,
  NOT protocol changes): derivation tags via harness _seed_int; grevlex order
  (semaev.py convention); T_verify = 3 group ops (m=3, per v1 stop report's
  frozen reading + mechanism); IC wall->group-op conversion seconds x
  calibration rate (HEUR-001(i)); three accountings group_ops_rho /
  group_ops_bsgs / wall_seconds; S_rel seconds charged by wall x rate with
  tuple evals recorded natively as secondary; Wiedemann rhs from recorded
  harvest (a,b) + frozen k (consistent via <P>-component logs); fV/S4 one-time
  setup recorded separately (preprocessing-derivable, excluded from per-target
  T_desc); aux enumeration ground truth on descent targets (uncharged,
  recorded); naming double-set byte-identical + deviation recorded; darwin
  memory enforcement post-hoc peak RSS + 3.75 GB self-abort.
- Toolchain probe (prior session): python 3.12.8, sympy 1.14.0, numpy 2.4.4,
  pyyaml 6.0.3, SIGALRM available, no installs needed/possible.
- runs/ directory empty (only .gitkeep). Git HEAD a2947025...; dirty = only
  ._ AppleDouble paths (exFAT); dirty basis = non-._ tracked paths, disclosed.

## Stage 2 — implementation: IN PROGRESS
- Groebner S_4 16-bit feasibility probe launched (scratch, implementation-
  validation only): /Volumes/Volume/llm/tmp/opencode/car-scratch/probe_gb.py

## Stage 2 — implementation: DRIVER WRITTEN (2026-07-28)
- code/run_mtic.py (single driver, ~2200 lines): all 10 runs, frozen artifacts,
  manifest writer (both naming sets byte-identical + deviation), budget guard
  (1700 s self-cap / 3.75 GB RSS abort / post-hoc 4 GB), SIGALRM 60 s solve cap.
- Probe (implementation-validation, scratch): 16-bit S4 resultant 0.13 s (227
  terms, deg 16); fV expand 0.55 s at B=133; **16-bit Groebner CAPPED at 60 s**
  => frozen censoring regime expected (capped solves at full cap => regime (i)).
- Design consequences: (a) fV built by exact numpy int64 convolution (unit-checked
  vs sympy.prod; full coefficient equality check at B<=500, seeded point checks
  at larger B) to keep 24-bit setup ~seconds instead of ~350 s; (b) descent
  targets attempted ROUND-ROBIN across instances/bases under the shared frozen
  cumulative cap (order across instances unpinned by protocol) so every instance
  receives measured targets; (c) Wiedemann attempt bounds: true-rhs 1 attempt,
  consistent-rhs 3 attempts (house <=5 precedent); (d) inherited ENDO engine
  s==1 sign bug found+fixed in my collector (undercount-only, EC-verified).
- Smoke tests into scratch out-root next (no experiment records polluted).

## Stage 2 — implementation: SMOKE-VALIDATED (2026-07-28)
- Smoke (scratch out-root): RUN-001 (69 s, completed_valid; instances match
  AMEND-001; calibrations rho 1.26e6-1.56e6, bsgs 2.78e5-1.46e6 ops/s;
  NOTE: 16-bit bsgs rate 5.6x below rho rate -- tiny-sample timer granularity,
  anomaly to record), RUN-002/003/004 (completed_valid; 160/449/3981 relations;
  24-bit needs only 2 harvest targets -- decompositions plentiful as predicted),
  RUN-005 + RUN-006 (completed_valid after fixes below; 24-bit Wiedemann 8.7 s,
  attempt 1; non-interference hash equalities all true, RUN-005 reproduced).
- Defects found in smoke and fixed BEFORE any recorded run:
  1. Signed matrix rows: relation rows now carry summand signs [[col,sign]]
     (all-+1 0/1 rows -- ENDO structural convention -- are inconsistent against
     the true harvested rhs; 31-708 row verification failures measured in
     smoke). Fixed in collector (_signed_terms), assemble, GE, matvec, verify.
  2. Maxrank nonsingular subsystem LA construction (ENDO DEV-7 precedent):
     weight-3 matrices at 1.2B rows are rank-deficient (129/133, 364/374,
     3272/3317); plain Wiedemann cannot converge (measured). Row basis x
     column basis -> nonsingular r x r block, true-rhs solve, solution
     zero-extended on B-r free columns, verified on ALL harvested rows.
  3. Wall-accounting frontier product is CUBIC: N converts by rho_rate^3
     (was wrongly squared; unit check).
  4. ENDO engine s==1 sign bug fixed in my collector (undercount-only there).
  5. fast fV numpy convolution (full coefficient check B<=500, point checks
     larger); capped solves record trivial_ideal=None (verdict unknown);
     interleaved round-robin descent execution (order unpinned by protocol).
- Descent code-path probe: ALL sizes incl. ablations cap at 60 s (frozen
  censoring regime confirmed); aux ground truth + signed certs verified;
  ablation_cbrt (B=52) decompositions rare (~0.16/target expected).
- Remaining: execute the real 10 runs; RUN-009/010 happy-path validated only
  against real data (aggregation math unit-checked).

## Stage 3 — real execution: START (2026-07-28)
- implementation.md written (all 17 design decisions + smoke corrections).
- Executing RUN-MTIC-001 .. 010 in dependency order, real run records.
- RUN-MTIC-001 completed_valid (~68 s): instances/factor bases/targets/calibrations frozen, SHA-256; N=17623/139753/11000719
- RUN-MTIC-002/003/004 completed_valid: S_rel 0.022/0.062/9.86 s; 160/449/3981 relations; no censoring
- RUN-MTIC-005 completed_valid (~17 s): S_LA true-rhs maxrank subsystem, converged attempt 1 all sizes, verified on ALL harvested rows
- RUN-MTIC-007 completed_valid (1504 s): 16-bit T_desc 25 attempted, ALL capped 60 s, 25 cancelled_by_budget, median 60.0 s, aux found on all attempted
- RUN-MTIC-008 completed_valid (1543 s): 20-bit 13 attempted all capped, 24-bit 12 attempted all capped, medians 60.0 s, aux found on all attempted; round-robin order disclosed
- RUN-MTIC-009 completed_valid (2 s): rho 50/50 solved+verified per size, medians 1720/2893/12244 ops; BSGS measured; CTRL-SINGLE-TARGET holds all sizes/accountings
- RUN-MTIC-010 failed_implementation (~1503 s descent work lost with the record):
  KeyError 's_la_seconds' in ablation aggregation (run_005 sets that key on the
  caller side; run_010 read it from the callee). implementation_error, NOT
  evidence. Record preserved immutably; fixed the lookup (+ vacuous-IQR edge
  case); executing repair successor RUN-MTIC-010b (same frozen planned run).
- RUN-MTIC-010b completed_valid (1503 s): ablation descents all capped; ablation LA converged (cbrt full rank 52/52, 2_5 rank 111/115); aggregation + analysis.md written

## Stage 4 — validation + report: DONE (2026-07-28)
- Validation checks ALL PASS: run count (10 planned terminal + 010b repair),
  schema, byte-identical duplicate sets, raw/summary agreement, seeds distinct
  per size (1/2/3 -> 16/20/24), frozen SHA-256 verified by dependent runs,
  certificates all verified, dirty=false everywhere, budgets within limits
  (max run 1543.2 s < 1800; total 6201 s < 13200; max RSS 842 MB < 4 GB).
- Controls: NONINTERFERENCE pass (3 hash equalities all sizes); RHO-BASELINE
  pass (150/150 verified); BSGS measured; SINGLE-TARGET pass (all sizes/
  accountings); CALIBRATION-AUDIT pass (no flips).
- Results: K* infinite on all instances and all accountings (regime (i)
  stable); no below-frontier observation; no K*=1. T_desc fully
  censoring-dominated (all solves capped 60 s). S_rel/S_LA measured.
- execution-report.yaml written (overwrites v1; v1 preserved at
  execution-report-specification-error-v1.yaml). TASK COMPLETE.
