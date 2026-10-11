# Implementation note: EXP-CERTBIN-a58c63 / RUN-CERTBIN-0b8f3a

Task: TASK-20260924-6ab0d8 (executor). Contract in force: **protocol version 2**,
which is the frozen `specification.yaml` (version 1, sha256 167a505d..., approved
by DEC-20260924-8e2f47) plus `amendments/AMD-20260924-3a9f06.yaml` (sha256
805b307f..., commit 8a1d5558e, approved by DEC-20260924-c41e7a, receipt
TASK-20260924-7d2b95). Neither file was edited. This note lists every
deviation, interpretation and execution event. It contains no conclusion.

## 1. Implementation

- `impl/` copies the reviewed Stage-1 regime-A modules from
  `experiments/EXP-CERTBIN-4e92d7/impl/` and generalizes them. Each change is
  listed in `impl/impl-provenance.json`: source sha256, target sha256, unified
  diff and reason. Nothing in EXP-CERTBIN-4e92d7 is imported or edited.
  C-PROV reproduces all 500 archived Stage-1 comparisons (`cprov.json`).
- Regime B (`regimeB.py`, `engineB.py`, `delta.py`, `detmod.py`, `certs.py`)
  is new and written from the specification's object block and the
  amendment. The solver's op log is self-tested against a literal
  dictionary-based transcription of the rule. The R0-R6 classifier is
  self-tested against a literal transcription run on the target's literal
  state. The determinant module is tested against the Leibniz expansion.
  Phi is tested against direct Lagrange interpolation.
- Beyond the specification's C-SELF list, `selftest.py` runs these extra
  items: the regime-B classifier against a literal transcription, with
  guided = own; the determinant against the Leibniz expansion; the
  top-coefficient identity on random functions; and the regime-A literal
  elimination sanity check copied from Stage 1.
- Exact statistics (`statsx.py`, RC-3): Fractions or mpmath at 60 digits. For
  large N the binomial bands sum 60-digit log-space terms with a rigorous
  truncation bound (relative remainder below 1e-80); at N <= 3000 they were
  cross-checked equal to the exact rational bands. The Stage-1 float
  Wilson/Clopper-Pearson helpers are not used.
- `verifier/verify_cert.py` imports nothing from `impl/`. It rebuilds every
  certified row with its own schoolbook arithmetic, its own
  product-definition L_V and its own Weil descent. It re-checks
  unsatisfiability by exhaustive evaluation over V x V.

## 2. Pre-data specification issues, all ruled by AMD-20260924-3a9f06

Issues (1)-(7) were found during implementation, on development runs
outside the repository. The Coordinator ruled them in AMD-20260924-3a9f06
(C-1..C-13), and the executor's fold-in reply added C-14..C-26:

1. PREFIX/COLUMN precedence (C-1, C-2, C-3): first-match rule R0-R6; E3
   success = R3 COLUMN at the target's own first non-pivot column. The
   PREFIX-first reading is reported only as `E3_prefix_first_sensitivity`.
2. C-REPLAYB premise (C-4, C-5, C-6): C-REPLAYB v2, INV-5 v2, and K_B from
   the T_strict-guided computation.
3. F-SAT termination (C-8, C-9, C-17): exhaustion stops. E_SAT uses oracle A
   over every non-degenerate subgroup abscissa and is cross-checked by an
   independent V x V solve. The E3 arm is the union by x_R.
4. C-TR literal statement (C-10, C-18): the restated check on x(E) uses the
   point test [#E/2] lift(x) = O, cross-checked by the doubling image. The
   literal count is reported.
5. Modal scope (C-11): per family, and none for a family with 100 or fewer
   non-degenerate targets.
6. Probe stream (C-6): ONE PCG64(S_probe) stream in cell order, then
   U1..U3, with at most 10 draws per reference.
7. EXTRA-PIVOT (C-1): adopted, and never counted as E3.

Readings confirmed in C-19..C-23: stream 01 is one logged sequence per cell;
the F-AFF and F-AFFB reference rules (F-AFFB fillers exclude F-S3 targets);
F-RANDX takes its references and then its targets from stream 05; C-BREAK
coverage; C-DET/C-REV scope; the PS0' choice of D. The trial plan
(`trial-plan-v1.json`, interpretations V2-RULINGS and R-1..R-10) records each
one with its specification clause.

## 3. Development-seed exposure (disclosed; ruled by C-14, C-15, C-16)

- Development runs 1 and 2 seeded their generators with "frozen seed + 7".
  Eighteen of those values ARE version-1 frozen seeds:
  2026092420105, 2026092420106, and 2026092420c08..c11 for c = 1..4.
  Those generators were instantiated in dev in different roles. One
  (2026092420105) used the same routine and bound as its frozen role.
  AMD C-14 retired all 18 and replaced each by old + 10000
  (`trial-plan-v1.json` seed_table_C-14; manifest). AMD C-16 records C-PILOT
  as FAILED pre-run and applies its own consequence: the schedule is C_std at
  every cell. The real pilot still ran on S_selftest and wrote timings only.
  Its T_proj (3822 s single-worker) is reported and not binding.
- Development run 3 used "frozen seed + 10^12". None of those values is a
  version-2 seed. It started before C-15 (dev seeds < 10^6) was received and
  was stopped on receipt. Run 4 used seeds below 10^6
  (100000 + 100c + s; 100001, 100002, 100098, 100099).
- The manifest's `dev_exploration` block lists every dev seed with no value.
  Dev outputs stay outside the repository and are not cited. Files that hold
  values of retired streams were not opened after C-15.
- selftest.py (seed S_selftest = 2026092420099) ran in scratch before C-15
  was received, computing self-test items only.

## 4. Other deviations and readings

- Pilot at n = 19 (AMD affirmed reading): the pilot's n = 19 B is drawn from
  the pilot's S_selftest generator. The timed unit is build + column pass +
  row pass.
- Regime-A row-order files are written per (n, l, D), because the row index
  depends on n. Regime-B order files are written per l.
- Manifest shape: the manifest follows the ledger validator's run schema,
  where `run.result.certificate.kind: none` means no solve, decomposition or
  relation is claimed. The PS0' unsatisfiability certificates the
  specification names are INSTRUMENT certificates (C-PROPS). They are
  recorded under `run.result.instrument_certificates`, and the separate
  verifier process checked them (`ps0prime-verification.json`).
- HEUR-CERTBIN-TS2B's text says the K_B probes come from S_selftest. The
  specification and AMD C-6 (S_probe) govern.
- Workers: 2 were enabled only after the serial and sharded outputs of the
  20 lowest-idx F-S3 targets of cell (17, 6) were byte-identical in both
  regimes (checkpoint `workers-identity`, manifest `workers`). Memory caps:
  RLIMIT_AS 1.6 GB for the parent and 1.2 GB per worker (AMD C-26).

## 5. Execution events (all recorded in checkpoint/invocations.jsonl and stdout.log)

- 2026-09-24T05:59:06Z selftest.py: all_pass true (C-SELF and C-FIX, both
  regimes, every cell). The n = 19 modulus found by the rule is
  t^19 + t^5 + t^2 + t + 1, i.e. (a, b, c) = (5, 2, 1), after 5 candidates.
- 05:59:13Z driver --phase pilot (pid 9262): C-PROV passed 500/500; the
  pilot ran on S_selftest and wrote timings only; schedule C_std by C-16
  (T_proj 3822 s, not binding); trial-plan-v1.json written (sha256
  d1498357...) and bound to the amendment (sha256 805b307f...) BEFORE the
  first frozen draw (checkpoint `plan-bound` 05:59:39).
- 05:59:39Z main driver (pid 9369, watchdog `timeout 259200`): n = 19 curve
  from S_curve19/S_pts19: A = 46693, B = 306147, #E = 523646 = 2 * 261823.
  Phases 1-5 ran at every cell in cell order, followed by cells.json and
  120 PS0' certificates. rc 0 after 3226 s wall. Peak RSS 564 MB parent,
  453 MB largest worker.
- The worker identity check passed at cell (17, 6): serial and sharded
  outputs of the 20 lowest-idx F-S3 targets were byte-identical in
  regime A (D = 3, 4) and in regime B. 2 workers were used from then on.
- 06:53:24Z --phase determinism (separate process, pid 14624): C-DET
  1272/1272 T_ops hashes matched.
- 06:54:48Z verifier/verify_cert.py (separate process): 120/120 PS0'
  certificates verified (regime A at D = 4 at every cell; regime B at the
  two l = 5 cells).
- 06:54:50Z --resume (pid 14758): phase 8. rc 0.
- stderr.log is empty. No crash, watchdog expiry or infrastructure event
  occurred. maximum_runs: this is run 1 of 2, and run 2 was not needed.
- Git HEAD moved between invocations: 359751a5f at the pilot and main
  invocations, 9db1d91db at the determinism and resume invocations. Other
  sessions committed to the shared worktree during the run. The executor
  made no commit. `impl/` and `verifier/` are untracked working-tree files,
  and their sha256 values are recorded in manifest.yaml
  (run.code.impl_sha256) and impl/impl-provenance.json. No impl file changed
  after the launch.

## 6. Report defect found after the run (recorded, not corrected in place)

- instrument-checks.json `global.C-PILOT.pass` = false, and the manifest's
  run.result.global_controls.C-PILOT = false. That value comes from the
  report's automated key check. Its allowed-key list omits two keys the pilot
  writes under AMD C-16: `schedule_basis` and
  `schedule_the_rule_would_give_(not_binding)`. With those two keys admitted,
  the key check passes, and the same record shows decision_before_phase_1 =
  true. C-PILOT's CONTROLLING status is FAILED, recorded pre-run by AMD C-16
  (version-1 frozen streams were drawn in dev before the decision). Its
  consequence (C_std at every cell) was applied, and it is not a void. The
  recorded false therefore matches the ruled status, but the automated
  reason in that record is wrong. The phase-8 files are write-once, so this
  note is the correction.

## 7. Unexpected observations (recorded as data; no interpretation)

- At (19, 6), one unsat F-S3 target has delta = 125 < 126 = 2^{l+1} - 2
  (1 of 999; the TS2G tail check reports 0.1%).
- At (17, 5), one unsat F-RANDX target (idx 204) has a ZERO-PIVOT first
  divergence at k = 2257 against every F-S3 reference and every own
  reference. C-BREAK verifies it. The F-S3 unsat arm has no ZERO-PIVOT
  divergence at any cell.
- At (17, 5), F-NULLB has one satisfiable target (idx 5) whose first
  divergence against the unsat references is ZERO-PIVOT (k = 2276), not
  COLUMN. E3 is not defined for null families. F-AFFB has 3 unsat
  ZERO-PIVOT divergences. All are C-BREAK-verified.
- C-REPLAYB v2 (d), data only: X-ZERO REFERENCE labels at (17, 5) on U1
  (5 attributed zeros), U2 (3) and U3 (1), and at (19, 5) on U3 (1). Every
  attributed zero is verified by the determinant module, and on those
  references the fixed replay is schedule-invalid on 50/50 matched targets
  at the predicted k*.
- K_B = 2 for every unsat reference at l = 6 and K_B = 111 for every unsat
  reference at l = 5.
