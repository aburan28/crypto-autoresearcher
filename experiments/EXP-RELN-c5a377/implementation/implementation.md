# EXP-RELN-c5a377 — protocol-v4 implementation (TASK-20260929-7e6ea7, repaired by TASK-20260929-b72e82)

Protocol version 4 = `specification.yaml` (v1) + `amendments/AMD-20260926-a7d25d.yaml`
+ `amendments/AMD-20260929-988139.yaml` (v3 rulings, `DEC-20260929-3d166b`)
+ `amendments/AMD-20260929-cc7226.yaml` (v4 rulings and required fixes FX-1..FX-7,
`DEC-20260929-7a62cc`); later files govern where they differ. Implementation only: no
scientific run, no `RUN-*` directory, no frozen label evaluated. Execution stays NOT
admitted (`DEC-20260929-ee5b8a` and `DEC-20260929-7a62cc` both leave
`currently_admitted` false and the driver refuses them). The v4 repair is itemised in
`repair_report_v4.yaml`; the frozen trial plan `trial-plan-v2.json` is unchanged
(sha256 `7fb5e40d…29cf`).

## Files

| file | role |
| --- | --- |
| `labels.py` | SHA256 seed labels, frozen namespace `EXP-RELN-c5a377/v2`, smoke namespace `smoke\|EXP-RELN-c5a377/v2` |
| `fixtures.py` | C-1 fixtures, exact integer C-2/C-3 bounds (`B`, `B2`, `A1`, `A2`), Sage regeneration + byte compare |
| `ecarith.py` | instrumented F_p / affine curve arithmetic; every group op, mult, inversion charged |
| `vcurve.py` | independent uncharged verifier arithmetic (Jacobian, Fermat inversion, Cipolla) |
| `relgen.py` | honest 2-LP generator (C-2, C-3), full / 1-LP / 2-LP classification |
| `lpgraph.py` | LP graph with root, cycle rank `|E|-|V|+c`, GF(2) cross-check, Horton MCB, `delta_proof`, `delta_ratio` |
| `nulls.py` | configuration-model rewire, Erdős–Rényi G(|V|,|E|), planted-dense known positive |
| `recovery.py` | sparse LP log recovery over Z/q (charged LA ops), verification, scrambled known false |
| `rho.py` | Pollard rho with negation map, 64 targets per fixture, walk ops / sqrt(q) vs 0.886 |
| `audit.py` | independent accounting audit (completeness, charge formula, 10% replay, all certificates) |
| `celltask.py` | one fixture in a fresh process: generator to A2 (A1 = prefix), both budgets, all controls, rho |
| `hostinfo.py` | C-7 readings, fail closed |
| `driver.py` | admission (explicit, non-superseded decision), C-7, plan and v4 protocol hashes, snapshot-receipt check, per-cell processes, RSS watchdog, canonical run manifest |
| `analysis.py` | C-5 verdict rule with the v3 readings and the v4 F-3 / F-4 / FX-4 rulings |
| `make_trial_plan.py` → `trial-plan-v2.json` | 9 fixtures × {A1, A2} = 18 cells, all control labels, protocol hashes |
| `smoke.py` → `smoke/v4/` | two driver dry runs on b16-s13 (smallest q) in the smoke namespace at budgets that differ from every frozen A1/A2 + `smoke/v4/smoke_summary.json` (the v2 `smoke/dry/` and `smoke/smoke_summary.json` are immutable history) |
| `make_report.py` → `implementation_report.yaml` | file hashes, tests, smoke, open questions |
| `tests/` | 116 tests (`test_v4.py` covers FX-1..FX-7) |

## What is implemented, mapped to the protocol

**Fixtures (C-1).** The nine `EXP-RELN-c5a377` entries of `ic_leads_fixtures_v2.json`
(sha256 `543f49ca…5a45`). `fixtures.reproduce` re-runs `ic_leads_fixtures_v2.py`
(sha256 `bde44afb…f3b2`) under Sage and byte-compares both the whole file and the RELN
entries; the result was byte-identical (test `test_fixture_regeneration_byte_identical`).
The driver refuses a charged run unless the fixture JSON still has the frozen hash.

**Factor base and large primes (C-2).** `B = ceil(p^{1/5})`, `B2 = ceil(p^{2/5})` with
exact integer roots. FB = liftable x-classes `x < B`, LP = liftable `B <= x < B2`,
`L` = number of FB x-classes (recorded; it is 2–14 across the fixtures, see trial plan).
Enumeration (curve RHS, Euler criterion, Tonelli–Shanks) is charged as setup.

**Generator (C-3).** `k` from `EXP-RELN-c5a377/v2|target|<bits>|<seed>`; `Q = kG` is
instance construction and is counted on a separate, uncharged counter. Attempt `j`:
`a_j`, `b_j` from `…|attempt|<bits>|<seed>|<j>` (drawn as `<label>|a`, `<label>|b`),
`R_j = a_j G + b_j Q`, then for every point `P1` with `x < B2` (both signs, sorted)
`T = R_j - P1` is computed and charged as one group operation, trivial cases included.
Each attempt is charged exactly (bitlen−1)+(popcount−1) per scalar multiplication,
+1 addition, +|S| scan operations; the audit recomputes that formula independently.
Every attempt (misses included) is written to `<cell>.attempts.jsonl`. A1 and A2 come
from one generator run to A2; A1 is the prefix.

**Graph and metrics (C-4).** Root vertex 0; each 1-LP relation is an LP–root edge,
each 2-LP relation an LP–LP edge (self-loop when both points share an x-class);
full relations are counted separately and enter only the recovery system.
`cycle_rank = |E| - |V| + c` (union-find) is cross-checked against `|E| - rank_GF2(incidence)`.
Horton minimum cycle basis at 16- and 20-bit: size must equal the cycle rank and every
basis element must be an even-degree edge set (checked against networkx's
`minimum_cycle_basis` on simple graphs in tests). 24-bit reports the GF(2) cycle rank only.
`delta_proof = log_L(cycle_rank) - 1`, `delta_ratio = log_L(cycle_rank/|E|)`, both null
with a reason when `L < 2` or `cycle_rank = 0`. Secondary metrics: giant-component
fraction, `|E|/|V|`, full-relation count, failed-attempt count, LP log recovery fraction,
verification failures, charged work / sqrt(q), per-fixture peak RSS (self and `os.wait4`).

**Controls (C-6).** Per fixture and budget: 32 configuration-model rewires, 32 ER
G(|V|,|E|), a planted-dense graph (must give `delta_proof > 1/4`), scrambled coefficients
(must fail LP log recovery verification), and the accounting audit. There are also 64 rho
targets per fixture. Defects stop the run (exit 7) per the stopping rules: an identity
failure, a failed known positive where it is reachable, a known false that passes, a
treatment verification failure, an audit rejection, or an unsolved or unverified rho target.

**Known positive below its gate (v4 F-4).** The planted graph has cycle rank
`ceil(|V|^1.5)`, so it can clear `delta_proof > 1/4` only when `ceil(|V|^1.5) > L^{1.25}`.
`celltask.planted_gate_min_v(L)` gives the smallest such `|V|` (2, 5, 5, 7, 8, 10 for
L = 2, 6, 7, 10, 12, 14; none for L < 2). Below it the control is recorded
`not_exercised` with `gate_min_V`: neither a pass nor a defect, and the run continues.
The planted cycle-rank construction check is still a defect. `analysis.py` lists the
size × budget cells lacking known-positive power confirmation and scopes negative
conclusions to the others; the verdict is unchanged.

**Recovery.** Unknowns: `l(x)` for the FB classes and the LP classes in relations, plus
`k`. Equations: `s1 l(x1) + s2 l(x2) - b_j k = a_j`, with the anchor `l(x(G)) = 1` (G is
canonical in every fixture, which is tested). Gauss–Jordan elimination on sparse rows
pivots on LP columns first, then FB, then `k`. Every mod-q product and inversion is
charged as `la_ops_charged`. A variable counts as determined only if its reduced row has
no free column. Every determined value is verified with independent arithmetic
(`l(x) G = V_x`, `k G = Q`).

**Verdict rule (C-5, v3 readings, v4 rulings).** OQ-2..OQ-5 readings as accepted in v3.
v4 F-3: a size × budget cell with no feasible ER replicate has the ER clause
`undetermined`; if every other supercritical clause holds and no determined cell has ER
above 1/4, the supercritical rule is `undetermined` and the verdict is inconclusive
(also when the subcritical rule fires, OQ-21). Feasible ER replicates are reported per
cell. v4 FX-4: where the known false is `not_exercised` the LP log recovery fraction is
reported as `undetermined`.

**Admission and C-7.** The driver refuses to start (exit 9) if `psutil` is missing, since
the 8 GiB watchdog could not run (FX-7). `driver.check_decision` admits only a named
`ledger/decisions/DEC-*.yaml` whose `coordinator_decision.id` matches, whose `target_ids`
include `EXP-RELN-c5a377`, whose `execution_admission.currently_admitted` is exactly
`true`, and which is not superseded or withdrawn: no `status` superseded/withdrawn, no
non-null `superseded_by`, and no later decision listing it under `supersedes` (FX-5).
`DEC-20260929-ee5b8a` and `DEC-20260929-7a62cc` are refused (tested).
C-7 (15-min load ≤ 14, `/` ≥ 5 GiB free, repository volume ≥ 20 GiB free) is read at
start and recorded in the manifest. Any unreadable or unparseable reading fails closed.
Refusal order: psutil, C-7, run id, decision, plan hashes, v4 protocol records
(the v3/v4 amendments must carry the pinned sha256 that their decisions record in
`amendment_sha256_at_decision`), snapshot receipt, existing run directory.

**Snapshot receipt (FX-5).** A scientific run needs `--snapshot-receipt PATH`. Every
receipt entry under `implementation/` must match the working tree (the receipt itself is
excluded), every implementation `*.py`, `tests/*.py` and `trial-plan-v2.json` must be
pinned, and `git status` of `implementation/` (untracked included) must be empty; otherwise
exit 10. `celltask.py` refuses a namespace without `smoke` unless the admitted driver
launched it: the driver passes the decision id, repository root and run directory in the
environment, and the cell process re-checks the decision and that the run manifest is
`running` for that decision and namespace.

**Run record (FX-1, FX-2, FX-7).** `manifest.yaml` has the repository's top-level `run:`
block (id, experiment_id, hypothesis_id, protocol_version 4, status, code, inference,
environment, inputs, timing, resources, result, artifacts) and a `driver:` companion with
per-cell details. It is written with status `running` before the first cell and rewritten
atomically after each cell. `inputs.protocol` records the path and sha256 of the
specification, the three amendments, `DEC-20260929-3d166b`, `DEC-20260929-7a62cc`, the
fixture JSON and the generator. The driver console is teed to `stdout.log` / `stderr.log`
in the run directory. An exception or SIGTERM / SIGHUP / SIGINT is recorded as
`failed_infrastructure` (failure_class `exception` or `signal`); a procedure defect is
`invalid`. `command.txt` records the driver's own argv, including when `main(argv)` is
called from `smoke.py`. `environment.json` records the OS, Python, Sage version and
pyyaml / scipy / networkx / psutil / numpy / pytest versions, implementation sha256s, and
the inference block from `AUTORESEARCH_*` only (unset → null / `unverified`).

## Smoke v4 (implementation check only, TASK-20260929-b72e82)

Fixture b16-s13 (smallest q), namespace `smoke|EXP-RELN-c5a377/v2`, output under
`smoke/v4/dry/`. Budgets 64/256 (`DRYRUN-v4-tiny`) and 400/1500 (`DRYRUN-v4-controls`)
differ from all 18 frozen A1/A2 values; `smoke.py` and the driver refuse a clash (FX-6).
Both runs exited 0 with status `completed_valid` and no procedure defect. Both manifests
have the canonical `run:` block with protocol version 4, and all six run files are
present. Every identity held. The known positive passed (|V| ≥ its gate minimum 5 for
L = 6). The known false was `not_exercised` in the tiny run and `fails_verification` in
the controls run, where treatment recovery verified all of its determined values. The
audit accepted every receipt with 0 replay mismatches and 0 certificate failures, and all
rho targets were solved and verified. `smoke/v4/smoke_summary.json` contains no treatment
delta, ER-null delta, subcritical-rule input or verdict. The F-3 and F-4 branches are not
reached on this fixture; they are covered by unit tests.

## Smoke v2 (historical, immutable)

Per AMD-20260929-cc7226 F-2, the `smoke/dry/DRYRUN-controls` delta, ER-null and
subcritical-rule readings are excluded from every analysis. They were not opened during
the v4 repair.

Fixture b16-s11, namespace `smoke|EXP-RELN-c5a377/v2`, output under `smoke/dry/`.
There are two dry runs through the driver: `DRYRUN-tiny` (A1'=64, A2'=256, 4 replicates,
2 rho targets) and `DRYRUN-controls` (A1'=249, A2'=751, 8 replicates, 4 rho targets).
The second is needed because at the tiny counts no log is determined, so the known false
is `not_exercised`. Both exited 0 with no procedure defect. All identities held: cycle
rank equals the GF(2) dimension, the Horton basis size equals the cycle rank and every
element has even degree, and the audited charge total equals setup plus attempts. The
known positive passed in all 4 budget blocks. The known false was `fails_verification`
where exercised: at A2'=751 it gave 5 inconsistent rows and 39 failed verifications,
while treatment recovery verified all 39 of its determined values. The audit accepted
every receipt with 0 replay mismatches and 0 certificate failures, and all rho targets
were solved and verified. Peak RSS was about 25 MB. C-7 readings at smoke time failed
(load 29.1, `/` 1.76 GiB, repository volume 6.8 GiB free); they were recorded, not
enforced, because smoke is not a charged run. The smoke summary omits treatment delta
readings and never calls the verdict rule; `analysis.py` refuses smoke-namespace cells.
The raw smoke cell files still contain smoke-namespace graph metrics, which are not
evidence and are not inputs to any verdict.

## Cost (advisory, modeled, not measured on frozen fixtures)

The trial plan lists expected scan group operations at A2 per fixture: from 4.0e4
(b16-s13) to 1.5e7 (b24-s12), 3.9e7 in total. The smoke rate on this loaded Mac was
roughly 2–3 µs per charged group operation, so the modeled whole run is on the order of
minutes. Memory is dominated by the attempt log and the null replicates, which is far
below 8 GiB.

## Open questions (literal readings adopted; protocol unchanged)

See `implementation_report.yaml` → `open_questions` (OQ-1 … OQ-26) for each ambiguity
and the literal reading implemented. OQ-4, OQ-13 and OQ-14 now carry the v4 rulings.
OQ-21 … OQ-26 are new readings of the v4 text. The reviewer-relevant ones:
- **OQ-4**: the ER-null clause of C-5 and the structural fact that G(|V|,|E|) shares
  `|E|-|V|` with the treatment graph.
- **OQ-2 and OQ-3**: the CI and trend readings.
- **OQ-6**: the vertex set.
- **OQ-14**: a `not_exercised` known false.
- **OQ-21**: F-3 when the subcritical rule also fires (fail-closed: inconclusive).
- **OQ-25**: the dirty-tree rule makes any post-snapshot file under `implementation/`
  (including smoke output) block a scientific run until a new snapshot covers it.
