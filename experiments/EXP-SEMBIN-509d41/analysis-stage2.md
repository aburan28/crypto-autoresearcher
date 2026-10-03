# Analysis: EXP-SEMBIN-509d41 Stage 2

Review: `REVIEW-SEMBIN-509d41-STAGE2-20261003`  
Evidence: `EV-SEMBIN-7ea861` · Decision: `DEC-20261003-7aa6c1`  
Producer: `TASK-20261002-d67dd7` · Snapshot: `TASK-20261003-2e4a0a`  
Admission: `DEC-20261003-054ae8` · Prior expand: `EV-SEMBIN-d1cf99` / `DEC-20261003-c77494`  
Review handoff: `TASK-20261003-e2dbcc` · Archive: `TASK-20261003-b9db28`  
Tip at review: `2d4143fbf42012d8bb9eb0235131dc8faa2927fd`  
Stages 0–1 analysis (unchanged): `experiments/EXP-SEMBIN-509d41/analysis.md`

## Observation

- **Run set.** One Stage-2 run under `trial-plan-stage2-v1.json` (plan_sha256 `633daf7d…`), `output_validated` / `completed_valid`; `certificate.kind = none`; Amazon Bedrock NOT SELECTED; no Magma/Sage/AUXIN success path.
  - `RUN-SEMBIN-ee4b22` Stage 2 → `O-IMPEDIMENT` / `SKIPPED_IMPEDIMENT` (started `2026-10-03T01:12:17.616420+00:00`, finished `…924865+00:00`, wall ≈ 0.308 s receipt / ≈ 0.154 s producer probe).
  - `check.stdout.log`: `{"ok": true, "stage": 2, "outcome": "O-IMPEDIMENT"}`.
- **Backend probe.** `stage2/backend-probe.json`: sage / magma / Macaulay2 / Singular **absent** on PATH; `sympy.groebner` importable but `admitted_for_semaev_n68: false` (never the success path for `N_boolean=68` under this card). `admitted_backends_present: []`, `backend_available: false`.
- **Stopping rule.** Frozen contract stops Stage 2 as `O-IMPEDIMENT` with `heur_top_verdict=SKIPPED_IMPEDIMENT` when no admitted Groebner/Macaulay backend is present. Instances completed per arm: **0**. No Spearman(σ_top, median T), no path/minimiser median-time ratio, no 95th-percentile tail.
- **Shape binding (custody for re-run).** Per `DEC-20261003-c77494` / `DEC-20261003-054ae8`, `stage2/shape-binding.json`:
  - path / cherry-caterpillar: `((((0, 1), 2), 3), 4)`, σ_top = 52480
  - balanced (near-worst): `(0, ((1, 2), (3, 4)))`, σ_top = **91648** (= max)
  - mid-split rejected: `((0, 1), (2, (3, 4)))`, σ_top = 39424 (= min)
  - near_worst_balanced_over_path ≈ 1.746; mid_split_over_path ≈ 0.751
- **Arm summaries.** All four arms `SKIPPED_IMPEDIMENT`, instances=0, median_wall=null; peak RSS (probe) 51163136 bytes.
- **Non-claims in RESULTS.md.** No exponent move, IC-vs-rho, FIPS verdict, or deployed-curve ECDLP claim. No second `(n,t,k)`. Observations only. Stage-1 `S1-INVARIANTS-OK` remains intact.

## Comparison

| Check | Prediction / control | Observed | Agree? |
|---|---|---|---|
| Stage-2 admission | `DEC-20261003-054ae8` / trial-plan-stage2-v1 | Present; plan_sha256 match | yes |
| Missing admitted backend → O-IMPEDIMENT | Frozen stopping rule | `O-IMPEDIMENT` / `SKIPPED_IMPEDIMENT` | yes |
| Instances / HEUR-TOP meters | ≥100/arm if backend present | 0 / null | yes (impediment) |
| Balanced arm binding | Near-worst max-σ_top, not mid-split | 91648 vs mid-split 39424 rejected | yes |
| Certificate / Bedrock / Magma-Sage-AUXIN | none / NOT SELECTED / unused | Matches | yes |
| Negative math vs (C1)–(C5)? | Never (rule 3 + contract) | Producer + RESULTS explicit non-claim | yes |

Blind re-derivation (ratios only, from stated σ_top integers): 91648/52480 ≈ 1.74634; 39424/52480 ≈ 0.75122 — matches `shape-binding.json` ratios.

## Inference

Stage-2 package is **valid** as an **infrastructure impediment**, not as a HEUR-TOP measurement. Direction on HEUR-TOP / full H-SEMBIN-9af7e1 is **neutral**: zero timed instances means the proxy-vs-solve question is untested. This does **not** weaken or reject (C1)–(C5); Stage-1 combinatorial support (`EV-SEMBIN-d1cf99`, strength preliminary) stands.

Official decision is **pause**: hold the Stage-2 HEUR-TOP measurement lane until a `/run` host presents an admitted Groebner/Macaulay backend (sage / magma / M2 / Singular). Revisit by re-running Stage 2 under the same shape binding and trial plan (or an additive amendment if the plan must name the host), then `/review-evidence`. Do not support full H. Do not promote KN-FIND.

Hypothesis and experiment remain **running**. Shared GOAL head is not edited (concurrent-lane hygiene); operative next_action lives on the decision record.

Strength **inconclusive** (valid impediment receipt; no HEUR-TOP data; Coordinator-direct PD-1).

## Limitation

- No Groebner/Macaulay/HEUR-TOP timing; 0/100 instances per arm.
- Backend absence is host-local; transfer to another host is the revisit path, not a math claim.
- Shape binding is custody only — not evidence that σ_top tracks solve time.
- (C6)/HEUR-ARITY remains conditional and unvalidated under this card.
- Coordinator-direct review without independent validator/red-team (PD-1).
- Retry after aborted prior review session (PD-2); tip verified before write.
- No FIPS security, IC-vs-rho, exponent, or deployed-curve claim.
- Full `O-CLOSURE` / `O-PROXY-MISLEAD` / measured HEUR-TOP awaits a backend-capable re-run.

Amazon Bedrock: NOT SELECTED, NOT CONFIGURED, NOT PROBED, NOT CONTACTED, NOT USED.
