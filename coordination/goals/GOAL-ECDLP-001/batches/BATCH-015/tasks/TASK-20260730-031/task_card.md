# TASK-20260730-031 — Combined RT35-CTRL-1 structure probe and RT35-CTRL-2 base-row supply probe

**MIRROR ONLY.** The authoritative card is the `tasks[]` entry with this id in
the BATCH-015 `dispatch_queue.json`. **Where they disagree, the queue governs**
and the disagreement is a defect to report, not to resolve by preference.

- **Role:** executor
- **Depends on:** nothing
- **Archived by:** TASK-20260730-032 (snapshot, runs alone)
- **Budget:** 2700 s total — 900 s PART A, 2400 s PART B, 300 s per (cell, arm)
  unit — 2 GB memory, `maximum_runs: 1`
- **Artifact size:** 2 MiB per file, 8 MiB for the probe directory
- **Pre-flight disk check is MANDATORY:** record the exact free-space figure
  before the first write; **below 5 GiB, stop and report and write nothing**

## Claim ceiling

**TOY SCALE, COMMITTED-CODE INSTRUMENT PROBE.** This is not an attack, not an
attack improvement, not a cryptanalytic result, not a closure, and **not a test
of H-STR-002's mechanism**. H-STR-002 stays `weakened`. EXP-STR-004 is **not
approved and is not executed by this card**.

## PART A — structure (RT35-CTRL-1)

Generate `CURVE-J12S1` by the committed path
(`_generate_j0_instance(seed=1, field_bits=12)`, `zeta3` from `_find_zeta3(p)`),
call `_build_phi_invariant_factor_base(inst, B, zeta3)` at **B = 192** and at
**B = 193**, and assert **both** of CTRL-4's conditions:

1. `len(F) == B`
2. `F[3j + k] == pow(zeta3, k, p) * F[3j] % p` for every complete block
   `0 <= j < B // 3` and `k in {0, 1, 2}`

On a condition-(2) failure emit the **full sorted list of failing `(j, k)`
pairs** with the offending values — **never a count alone** (PRED-ID-STR).

## PART B — supply (RT35-CTRL-2)

For **each of the fourteen declared cells** and **each of the two declared
factor bases**, call
`_collect_relations(inst, fb, m, Q, include_phi_orbits=False)` and report
**only** `len(relations)`, against `R_base(B)` and against the **measured**
distinct-target count.

| cell | curve | B | m | R_base | Q |
|---|---|---|---|---|---|
| L12 | CURVE-J12S1 | 12 | 2 | 5 | 60 |
| L13 | CURVE-J12S1 | 13 | 2 | 6 | 60 |
| L24 | CURVE-J12S1 | 24 | 2 | 9 | 60 |
| L25 | CURVE-J12S1 | 25 | 2 | 10 | 60 |
| L48 | CURVE-J12S1 | 48 | 2 | 17 | 60 |
| L49 | CURVE-J12S1 | 49 | 2 | 18 | 60 |
| L96 | CURVE-J12S1 | 96 | 2 | 33 | 106 |
| L97 | CURVE-J12S1 | 97 | 2 | 34 | 107 |
| L192 | CURVE-J12S1 | 192 | 2 | 65 | 202 |
| L193 | CURVE-J12S1 | 193 | 2 | 66 | 203 |
| X96 | CURVE-J16S3 | 96 | 2 | 33 | 106 |
| X97 | CURVE-J16S3 | 97 | 2 | 34 | 107 |
| A12M3 | CURVE-J12S1 | 12 | 3 | 5 | 60 |
| A13M3 | CURVE-J12S1 | 13 | 3 | 6 | 60 |

`CURVE-J16S3` is `_generate_j0_instance(seed=3, field_bits=16)`.
**Recompute** `R_base(B) = (B + 2) // 3 + 1` and `Q(B) = max(60, B + 10)` from
the formulas and **report any disagreement with this table as a finding** —
adopt neither side silently.

Arm A-prime's factor base is `_build_phi_invariant_factor_base`; arm E-prime's
is `_build_random_factor_base`. **The word "arm" here names which factor base
was built and nothing else. Neither arm's closure is invoked, written,
simulated or approximated.** `include_phi_orbits` is **False at every call,
without exception**, and the value actually passed is recorded per call.

## Absolutely forbidden

No closure. No shifted, permuted or appended row. No alpha, no `phi_alpha`, no
displacement rank, no misalignment set, no predicted set, no `rank_M`, no rank
deficiency, no branch determination, no F-1 to F-5 verdict, no ladder
statement, no scaling law. **Do not call `_measure_displacement_rank`. Do not
call `main()`.** No Sage, no subprocess, no certificate, no solve. **No cost
quantity of any kind** — no cost ratio, no density penalty, no crossover, no
rho or BSGS baseline. If you find yourself writing a permutation of a row, you
have exceeded this card.

Wall-clock and memory figures are **budget accounting, not cost quantities**,
and the manifest must say so.

**Create no run identifier. Write nothing under `experiments/`. Do not call
`harness.runner.write_run`.** `probe_manifest.json`'s `run_ids` is an empty
list **with its reason stated** (INT-BATCH015-F).

## The pre-registered falsification condition

Frozen in the BATCH-015 opening commit, **before this probe exists**. Evaluate
it **mechanically** and interpret it **not at all**:

> It fires if `len(F) != B` at B = 192 or at B = 193, **or** if
> `max(0, R_base(B) - len(relations)) >= 2` at any (cell, arm).

Record `falsification_condition_fired` true or false and **name every
contributing cell and arm**. Write no interpretation, no recommendation and no
disposition — those belong to the reviews and the Coordinator.

**A timed-out, cancelled or failed unit is not a shortfall and is not fed to
this condition in either direction.**

## Infrastructure signal

Every timeout, crash, memory exhaustion, disk exhaustion, import failure or
missing binary is **infrastructure signal — never a negative mathematical
result** (AGENTS.md core rule 5). Record the terminal status, continue with the
remaining cells after a per-unit breach, and on a total-cap breach **stop and
report a bounded partial result naming exactly which cells and arms you did not
reach**. Do not overrun silently and do not fabricate a figure.

## Determinism

Re-execute **L12 and A12M3, both arms**, a second time in the same process and
record a determinism PASS or FAIL with the compared values.

## Deliverables — exactly these eight paths, all written even on a partial run

```
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/probe/probe_driver.py
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/probe/command.txt
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/probe/environment.json
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/probe/stdout.log
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/probe/stderr.log
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/probe/structure_probe.json
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/probe/supply_probe.json
coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/probe/probe_manifest.json
```

## MAKE NO COMMIT

TASK-20260730-032 commits these and nothing else does. Write nothing under
`ledger/`, `knowledge/`, `harness/`, `tools/`, `experiments/` or any other
batch directory. Never touch `tools/validate_ledger_baseline.txt`. Write no
macOS AppleDouble `._` sidecar.
