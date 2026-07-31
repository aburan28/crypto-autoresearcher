# TASK-20260730-036 — Executor — CTRL-RT034-A, the mutation test of CTRL-4

> **NON-AUTHORITATIVE MIRROR.** The authoritative card is the `tasks[]` entry
> for `TASK-20260730-036` in
> `coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/dispatch_queue.json`.
> Where this mirror and that queue disagree, **THE QUEUE GOVERNS** and the
> disagreement is a defect to report, not to resolve by preference.

- **Goal / batch:** GOAL-ECDLP-001 / BATCH-016 (sixteenth of fifty authorized by
  BUDGET-AMEND-20260730-001, the user's explicit direction of 2026-07-30)
- **Role:** executor · **depends_on:** none · **archived by:** TASK-20260730-037
- **Budget:** 600 s total, 1 GB memory, maximum_runs 1

## Objective

Execute **CTRL-RT034-A alone**: re-run the CTRL-4 assertion — **the same checker
code, copied verbatim from the committed BATCH-015 `probe_driver.py`, not a
fresh reimplementation** — against one unmutated baseline and three deliberately
broken inputs at B = 192 on CURVE-J12S1.

Observe only. Interpret nothing.

## The cases

| Case | Input | Pre-registered expectation |
|---|---|---|
| 0 — baseline | true `zeta3`, unmutated factor base | **PASS.** Instrument sanity check, **not a result** |
| 1 — bogus `zeta3` | build and check with z = 5 and z = 1234 | **PASS — pre-stated, not a prediction to be scored** |
| 2 — replaced element | `G[1]` replaced by an unrelated on-curve x | **MUST FAIL** |
| 3 — interleaved blocks | `H[0..5] = [F[0], F[3], F[1], F[4], F[2], F[5]]` | **MUST FAIL** |

**Case (1)'s outcome is pre-stated and is already the committed finding of the
TASK-20260730-034 red team** (OBJ-1, `counterexample_or_mutation`), carried at
EV-STR-005 L-1 and DEC-20260730-031. **You may not record its reproduction as a
new result, a discovery, a replication, or evidence about phi-invariance.** If
it does not reproduce, that is a discrepancy against a committed record and is
reported as a finding.

**Cases (2) and (3) carry the information.** A control blind only to a bogus
`zeta3` is vacuous on one axis; a control also blind to a corrupted or reordered
factor base is **broken outright** — strictly worse, and information nobody
currently has.

## Load-bearing constraint — the checker is COPIED, not rewritten

Extract the CTRL-4 checking code from the committed
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/probe/probe_driver.py`,
copy it into `mutation_driver.py` unchanged except for the function signature
and input binding, **list every changed character** in
`mutation_manifest.json`, and record the SHA-256 of the copied text with its
source path, line range and commit. **A rewritten checker measures the rewrite,
not CTRL-4, and would make this card vacuous in exactly the way it exists to
detect.** If the checker cannot be isolated, **stop and report that as a
finding**; do not substitute your own.

## Deterministic mutation rules (fixed before this card existed)

- **Case 2 replacement x:** scan x = 1, 2, 3, … upward; take the **first** x with
  `E.lift_x(x)` not None, x not in F, and x != `pow(zeta3, t, p) * F[0] % p` for
  t in {0, 1, 2}. Record the x, the rule, and the candidates-scanned count. If no
  such x exists, **stop and report** — do not weaken the rule or change the index.
- **Case 3 permutation:** exactly `H[0..5] = [F[0], F[3], F[1], F[4], F[2], F[5]]`,
  every other index unchanged. Do not choose a different permutation.

## Hard prohibitions

- **`harness/` is the object of measurement and is never modified.** Every
  mutation is applied to a returned list or to an argument passed in.
- Never call `main()`, `_measure_displacement_rank`, `_collect_relations`,
  `_build_random_factor_base`, or `harness.runner.write_run`.
- Compute **no** closure, relation, supply count, alpha, phi_alpha, displacement
  rank, misalignment set, rank, branch, verdict, ladder statement, scaling law,
  Sage invocation, certificate, solve, or cost quantity of any kind.
- **Mint no `RUN-*` identifier**; write nothing under `experiments/`,
  `ledger/`, `knowledge/`, `tools/`, or any other batch directory.
- **Make no commit.** TASK-20260730-037 commits these files and nothing else does.
- Wall-clock and memory figures you record are **budget accounting, not cost
  quantities**, and the manifest must say so.

## What you report

Both CTRL-4 conditions **separately** for every case — (i) `len(F) == B` with the
observed length beside it, (ii) the block identity — plus the **joint** PASS/FAIL
(PASS only if both pass). On every condition-(ii) failure, emit the **full sorted
list of failing (j, k) pairs with offending values** — never a count alone
(PRED-ID-STR). **Do not predict which pairs will fail; report which did.**

Compute every instance parameter (p, n, a, b, zeta3, curve_id, derived seed);
transcribe none. The figures p = 2293, n = 733, derived seed 100 and the cubes
125 and 1799 are **prior-record figures to check, not to adopt** — a mismatch is
a finding, never a defect to fix.

Record `assertion_passed_a_mutated_case` mechanically: true if the joint result
is PASS for case (1) at either z, or for case (2), or for case (3). Name the
contributing cases. **Write no interpretation, recommendation or disposition** —
in particular, do not write that CTRL-4 is retired or rewritten. That is the
Coordinator's decision at TASK-20260730-040.

## Budget and stopping rules

- 120 s per case (case 0, case 1 at z = 5, case 1 at z = 1234, case 2, case 3),
  180 s instance generation, 180 s determinism re-execution, **600 s total**.
- Artifact size: 512 KiB per file, 2 MiB for the mutation directory.
- **Mandatory pre-flight disk check before the first write**; below 5 GiB free,
  **stop and report and write no artifacts**.
- **Every budget breach, timeout, crash or import failure is INFRASTRUCTURE
  SIGNAL** — never a PASS, never a FAIL, never fed to the pre-registered
  consequence, never a negative mathematical result (AGENTS.md core rule 5).
- Determinism check: re-execute all four cases a second time in the same process.

## Deliverables (all seven, even for a partial or failed card)

`mutation_driver.py`, `mutation_probe.json`, `mutation_manifest.json`,
`command.txt`, `environment.json`, `stdout.log`, `stderr.log` — all under
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/mutation/`.

## Completion gate

G1–G13 as stated in the queue entry. G1 (verbatim checker provenance) is the
gate this card exists for; a rewritten checker fails it.
