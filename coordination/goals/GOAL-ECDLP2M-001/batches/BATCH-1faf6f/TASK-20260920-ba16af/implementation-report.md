# Implementation report — TASK-20260920-ba16af

**Experiment:** EXP-QSP-70b731  
**Hypothesis:** H-QSP-cd0c90  
**Batch:** BATCH-1faf6f · **Goal:** GOAL-ECDLP2M-001  
**Approval:** DEC-20260920-2b276f  
**Archive owner:** TASK-20260920-e869a1  
**Policy:** executor-implementation · **maximum_runs:** 0  

## Verdict

Implemented `I_direct` and `I_indep` from the STATEMENT of
\(N_K(L)=\#\{x\in\mathbb{F}_{2^{n}}:x^{2^{n'}}=\lambda(x)\}\) and derivation (A)
in H-QSP-cd0c90 / IDEA-20260916-3f7a1c; wrote driver/check entrypoints and a
frozen `trial-plan.json`. **Zero scientific runs** were executed under
`experiments/EXP-QSP-70b731/runs/` (only the pre-existing `.gitkeep` remains).
Local smoke checks used `/tmp` only and are not experiment evidence.

`blind_from_respected: true`

## Paths read (complete declaration)

| Path | Purpose |
| --- | --- |
| `agents/executor.md` | Executor contract |
| `docs/agent-runtime-core.md` | Runtime core |
| `docs/experiment-execution.md` | Trial-plan schema |
| `docs/claims-and-verification.md` | Certificate kind: none |
| `experiments/EXP-QSP-70b731/specification.yaml` | Approved frozen contract |
| `ledger/hypotheses/H-QSP-cd0c90.yaml` | STATEMENT + (A) content |
| `ledger/proposals/IDEA-20260916-3f7a1c.yaml` | Derivation (A) detail |
| `ledger/decisions/DEC-20260920-2b276f.yaml` | Approval decision |
| `ledger/decisions/DEC-20260920-f1e672.yaml` | Allowed companion decision (listed in handoff) |
| `ledger/handoffs/TASK-20260920-ba16af.yaml` | This task card |
| `coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-93320c/TASK-20260918-53664e/design-note.md` | Design note |
| `tools/experiment_execution.py` | `coverage` / plan field requirements |
| `analysis/qsp-ecc2k130/explore/gf2rc.c` | Generic GF(2) sparse-mod pattern only (contract `may_read`) |
| `knowledge/literature/KN-LIT-4fe9d2.md` | Proposition 2 for linearized control C6 |
| `experiments/EXP-AUXIN-7e2e3d/implementation/trial-plan.json` | Trial-plan shape example (non-blind) |
| `experiments/EXP-AUXIN-7e2e3d/implementation/driver.py` | Import/layout precedent (non-blind) |

### blind_from — not read

Confirmed **not opened** during this task:

- `experiments/EXP-QSP-33b442/implementation/`
- `experiments/EXP-QSP-33b442/runs/`
- `experiments/EXP-QSP-33b442/execution-report.yaml`
- `experiments/EXP-QSP-33b442/analysis.md`
- `experiments/EXP-QSP-33b442/amendments/`
- `knowledge/techniques/KN-TECH-54c38e.md`
- `coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-5fa7d5/`
- `analysis/qsp-ecc2k130/explore/shape_census_131.json`
- `analysis/qsp-ecc2k130/explore/explore.json`
- `analysis/qsp-ecc2k130/explore/explore_fast.json`

Intersection of the read set with `blind_from` is empty.

## Deliverables written

| Path | Role |
| --- | --- |
| `experiments/EXP-QSP-70b731/implementation/i_direct.py` | Assumption-free \(N=\deg\gcd(X^{2^n}-X,L)\) |
| `experiments/EXP-QSP-70b731/implementation/i_indep.py` | (A)-based H-path / toy enum / A-L independent deg-gcd |
| `experiments/EXP-QSP-70b731/implementation/driver.py` | Stage CLI → `manifest.yaml` + `raw-result.json` |
| `experiments/EXP-QSP-70b731/implementation/check.py` | Artifact / accounting / fixture checker |
| `experiments/EXP-QSP-70b731/implementation/gf2_poly.py` | Bit-packed GF(2)[X] helper |
| `experiments/EXP-QSP-70b731/implementation/field_f2n.py` | \(\mathbb{F}_{2^n}\) helper (n=131 poly from contract) |
| `experiments/EXP-QSP-70b731/implementation/candidates.py` | 244-candidate / toy enumeration |
| `experiments/EXP-QSP-70b731/implementation/__init__.py` | Package marker |
| `experiments/EXP-QSP-70b731/trial-plan.json` | Frozen plan, schema `crypto.autoresearch.trial_plan.v1` |
| `coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-1faf6f/TASK-20260920-ba16af/implementation-report.md` | This report |

## Instrument notes (observations only)

- **I_direct:** repeated squaring of \(X\) modulo \(L=X^{2^{n'}}+\lambda\), then \(\deg\gcd(L,X^{2^n}+X)\).
- **I_indep paths:** `A-toy` (n≤20 STATEMENT enum); `A-H` (build \(H=Y^{2^{n'-r}}+\lambda^{\circ(q+1)}\), roots + closing) when \(\deg H\le H\_DEGREE\_MAX\); else `A-L` (independent copy of the deg-gcd loop; root listing when \(N\le ROOT\_LIST\_MAX\)).
- Band-L cells with large \(d^{q+1}\) use `A-L` for the count; derivation-(A) completeness for Band H remains on `A-H`.
- When \(N>ROOT\_LIST\_MAX\), root lists are deferred (`root_list_deferred`); such rows are **not** counted as certificate-bearing until listing completes (avoids the 732-vs-546 accounting defect).

## Local smoke (not experiment runs)

Executed only under `/tmp` (outside write_scope runs/):

- C2 `(7,3,X^2+X)` → 8 / 8
- C3 `(31,15,Type-2 λ)` → 32768 / 32768
- C4 `(12,6,X)` → 64 / 64
- Stage-1 agreement sample on toys: 0 mismatches on full 252×3 cells checked in a prior /tmp probe
- Candidate count: 244 census / 252 toy
- `driver --stage 0` + `check.py` on `/tmp/qsp70-stage0`: ok

**Runs executed under `experiments/EXP-QSP-70b731/runs/`:** 0

## Trial plan

- `specification_sha256` bound to approved spec bytes
- `source_sha256` covers full driver/checker/helper closure
- 20 trials: Stage 0 → Stage 1 → Band L `n'=3..14` (first wave `3..6`) → bridge `22` → Band H `{33,44,66}` → COMPARE → Stage 5
- `coverage()`: loads; `planned > 0`

### RUN ids minted (`allocate_id.py --next run --area QSP` + `--check`)

`RUN-QSP-cec70a`, `RUN-QSP-9312f7`, `RUN-QSP-097ecd`, `RUN-QSP-5a4afd`, `RUN-QSP-a96be8`, `RUN-QSP-7dd37b`, `RUN-QSP-ffed3c`, `RUN-QSP-86e0d2`, `RUN-QSP-26c91a`, `RUN-QSP-383952`, `RUN-QSP-a6dab8`, `RUN-QSP-10586d`, `RUN-QSP-2e1ff8`, `RUN-QSP-327529`, `RUN-QSP-715b58`, `RUN-QSP-12a389`, `RUN-QSP-7faa1b`, `RUN-QSP-d10c74`, `RUN-QSP-186d9d`, `RUN-QSP-15a2ab`

(Two further minted ids `RUN-QSP-5f1bc2`, `RUN-QSP-6b1425` were unused spare allocations and are not in the plan.)

## Incompleteness / follow-ups for /run

- Stage COMPARE body is a gate stub until Stage-4 freeze hashes exist; sealed EXP-QSP-33b442 paths stay closed until then.
- Large-\(N\) certificate listing (e.g. complete splitters) is deferred by design; a future amendment may add compact orbit certificates.
- C5 null-arm full 100+100 sampling is meta-declared in Stage 5; expand at /run if the Coordinator wants dedicated null trials.
- No commit/push performed (task constraint).

## execution_report (implement-only)

```yaml
execution_report:
  experiment_id: EXP-QSP-70b731
  task_id: TASK-20260920-ba16af
  implementation_commit: null  # worker does not commit; archive TASK-20260920-e869a1
  protocol_deviations:
    - >-
      maximum_runs:0 — no Stage measurement under experiments/EXP-QSP-70b731/runs/;
      only implementation + trial-plan + this report.
  runs:
    completed: []
    invalid: []
    failed: []
  observations:
    - >-
      Instruments and frozen trial-plan written; coverage() loads with planned>0.
      Fixture smokes in /tmp matched C2/C3/C4 forced values (not ledger evidence).
  anomalies: []
  artifact_paths:
    - experiments/EXP-QSP-70b731/implementation/i_direct.py
    - experiments/EXP-QSP-70b731/implementation/i_indep.py
    - experiments/EXP-QSP-70b731/implementation/driver.py
    - experiments/EXP-QSP-70b731/implementation/check.py
    - experiments/EXP-QSP-70b731/implementation/gf2_poly.py
    - experiments/EXP-QSP-70b731/implementation/field_f2n.py
    - experiments/EXP-QSP-70b731/implementation/candidates.py
    - experiments/EXP-QSP-70b731/implementation/__init__.py
    - experiments/EXP-QSP-70b731/trial-plan.json
    - coordination/goals/GOAL-ECDLP2M-001/batches/BATCH-1faf6f/TASK-20260920-ba16af/implementation-report.md
  executor_assessment:
    protocol_complete: true
    data_quality: limited  # no scientific runs by design
    requires_rerun: false
    blind_from_respected: true
    zero_runs_executed: true
```
