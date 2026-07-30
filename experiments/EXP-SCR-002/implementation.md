# EXP-SCR-002 implementation note

Executor: `executor` under handoff `TASK-20260727-007` (authorized by
DEC-20260727-002). Protocol: `experiments/EXP-SCR-002/specification.yaml`
(status approved, frozen: true, version 1). No protocol amendment was
requested or applied; runs are scored against the frozen criteria only.

## Design

Single-file adjudicator and run harness:
`experiments/EXP-SCR-002/sheet/apply_sheet.py` (Python 3 stdlib + PyYAML only;
no packages installed). All corpus content is read as git blobs at the pinned
commit `b8af1551e45fbe4435745239d29f4d141eea3356` via `git cat-file blob`,
never the working tree.

- **Corpus integrity control (CTRL-CORPUS-INTEGRITY).** Every path in the
  spec's hash manifest is read at the pinned commit; the git blob SHA-1 is
  recomputed (`blob <len>\0<content>`) and compared to the manifest, and the
  SHA-256 of the content is recorded in
  `experiments/EXP-SCR-002/corpus_manifest.json`. Any missing path or mismatch
  invalidates the run before any adjudication.
- **Sheet model.** Requirements R1–R7 are keyed by the pinned BATCH-006
  repaired-requirement ids. `apply_sheet` is a pure function of the fact
  vector `{R1..R7: bool}` producing per-requirement statuses in R1→R7 order:
  `pass`, `fail` (first failure), `fail_independently` (subsequent failures).
  Verdict: ADMIT iff all seven pass, else REJECT. Undecidable grounding yields
  `undecidable_with_reason`, never a silent verdict.
- **Grounding.** Per item, the fact vector is established only by mechanical
  checks over pinned bytes (exclusion-list dispositions, owner-record markers,
  the EV-CRYPTO-002 z_R closure for I2, the IDEA-20260723-002 exclusion for
  I3, O(1)-simulability markers for I5/I6/I7, the named-control cost record
  for I7). Any failed grounding check makes the item
  `undecidable_with_reason` with the failed check ids (stage stop rule).
- **R7 arithmetic.** Derived terms are computed symbolically with
  `fractions.Fraction` at beta = 1/5:
  `c_rel = max(q_rel, q_rel_replay+o_rel, o_rel)`;
  `L_rel = max(0, beta-r) + delta_rel + eta_rank + c_rel`;
  `tau = delta_t + u_t + max(q_t, q_t_replay+o_t, o_t)`;
  `lambda = max(a, L_rel, ell, tau, beta, b_w)`;
  `mu = max(a_m, q_rel_m, beta, ell_m, m_replay, m_output, b_m)`.
  Unknown terms fail admission (never zero). The (0.45, 0.50] interval is
  checked explicitly: any lambda/mu in it fails R7 (no intermediate admissible
  interval).
- **Calibration (CTRL-SHEET-CALIBRATION), always before corpus verdicts.**
  CAL-PASS-SCR-002 (synthetic descriptor embedded in the script exactly as
  declared in the frozen spec: explicit operation, transcript certified
  non-O(1)-simulable, deterministic rank guarantee r = 0.20 / eta_rank = 0,
  tau = 0.25, lambda = mu = 0.44, every term assigned) must receive ADMIT
  with recomputed aggregates matching the declared 0.44/0.44/0.25.
  CAL-FAIL-SCR-002 (the real I5 record through the sheet first) must fail at
  R1 with R2 `fail_independently`. Accuracy must be exactly 1.0.
- **Threshold recomputation (CTRL-THRESHOLD-RECOMPUTATION).** The four frozen
  identities B^(9/4) = N^0.45, B^(5/2) = N^0.50, B^3 = N^0.60,
  B^(5/4) = N^0.25 are recomputed as `Fraction(k,4or2or1) * Fraction(1,5)`;
  the pinned derivation text and the pinned `current_explicit_control`
  exponents are checked against the recomputation; the named control (I7)
  aggregates give lambda >= 3/5, mu = 3/5, tau = 3/5, failing R6 and R7.
- **Dedup control (CTRL-DEDUP-PRIOR-NEGATIVES).** Every rejected item carries
  its named rejection basis matching the frozen `audit_item_index` expected
  basis, verified against the pinned BATCH-006 `excluded_nonconstructors`
  dispositions (I1–I6) or the named explicit control (I7), with named owners.
  Coverage must be 1.0.
- **Determinism replay (CTRL-REPLAY-DETERMINISM).** Pass 1 = RUN-SCR-002-B
  R1–R4 cells merged with RUN-SCR-002-C R5–R7 cells; pass 2 = a fresh full
  application over all 7 items inside RUN-SCR-002-C. The canonical-JSON matrix
  payloads must be byte-identical (SHA-256 recorded).

## Runs (frozen plan, `replication.planned_runs`)

| Run | Payload | Stage budget | Per-run cap |
|---|---|---|---|
| RUN-SCR-002-A | `run-a`: corpus manifest + calibration + threshold recomputation | 900 s | 1800 s |
| RUN-SCR-002-B | `run-b`: adjudicate R1–R4 over all 7 items + dedup | 1500 s | 1800 s |
| RUN-SCR-002-C | `run-c`: adjudicate R5–R7, replay, emit matrix + decision | 1500 s | 1800 s |

Each run is executed by the script's `harness` mode, which: creates the
immutable run directory (refuses if it exists); records `command.txt` and
`environment.json`; spawns the payload with a 1800 s wall-clock timeout;
measures wall via `time.monotonic`, CPU via
`resource.getrusage(RUSAGE_CHILDREN)` delta, and peak RSS from the child
rusage; enforces the 4 GB memory budget **post-hoc against measured peak RSS**
(darwin rejects `setrlimit(RLIMIT_AS)`); classifies the terminal status
(timeout → `resource_exhaustion`; spawn failure → `failed_infrastructure`;
nonzero exit without raw result → `failed_implementation`; raw `valid` flag →
`completed_valid`/`completed_invalid`); and writes `manifest.yaml` with
commit, disclosed dirty basis, seeds/seed policy, environment, timing,
resources, controls, anomalies, and SHA-256 of every artifact.

## Protocol deviations

- **DEV-1 (artifact naming ambiguity resolution, severity none).** The frozen
  specification's `required_artifacts` names per-run files
  `raw-result.json` / `stdout.log` / `stderr.log`; the handoff deliverables
  name `raw.json` / `summary.json` / `stdout.txt` / `stderr.txt`. Resolution
  (same as EXP-SCR-001): each run directory carries BOTH naming sets with
  byte-identical content, plus the harness-generated `summary.json`. No
  required artifact is missing; no protocol content is altered.
- **DEV-2 (enforcement mechanism, severity none).** darwin rejects
  `setrlimit(RLIMIT_AS)`; the 4 GB memory budget is enforced post-hoc against
  measured peak RSS and the 1800 s cap via subprocess timeout, disclosed in
  every manifest.

## Dirty-flag basis (disclosed)

`code.dirty` in each manifest is computed over **tracked, non-`._` paths**
from `git status --porcelain`. Tracked `._` AppleDouble exFAT artifacts and
new untracked run artifacts under `experiments/EXP-SCR-002/` do not set the
flag; counts of each class are recorded in `dirty_detail`. The Executor
commits nothing; archival is the Coordinator's task (TASK-20260727-902).

## Notes and known anomalies checked

- The pinned `knowledge/INDEX.md` at the frozen commit is not read by any
  sheet check (the frozen item list is the specification's
  `audit_item_index`); its state is recorded as an anomaly if it carries
  unresolved merge-conflict markers (same pinned commit as EXP-SCR-001).
- The audit is zero-compute beyond table construction: no fixtures, no curve
  arithmetic, no sampling; seeds = [] with the frozen seed policy.
