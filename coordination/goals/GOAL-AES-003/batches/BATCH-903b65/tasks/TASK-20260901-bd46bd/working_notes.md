# WORKING NOTES — TASK-20260901-bd46bd (red-team re-run for TASK-20260804-fa4906)

Role: RED TEAM. Policy: review-adversarial (fallback under DEC-20260831-0d1eeb).
Date: 2026-09-01. Branch: aes003-debt903b65-20260901.
Session start proxy: claim commit d96383f4e at 2026-09-01T16:36:30Z (git show -s).

## Files read (all under declared read_scope)
- coordination/goals/GOAL-AES-003/batches/BATCH-903b65/dispatch_queue.json (task card TASK-20260901-bd46bd, lines 71-126)
- coordination/goals/GOAL-AES-003/batches/BATCH-713991/dispatch_queue.json (original cards fa4906 lines 277-344, 91d27e lines 207-254)
- ledger/evidence/EV-AES-048545.yaml (whole, 118 lines)
- ledger/decisions/DEC-20260804-73977c.yaml (whole, 143 lines; note D-6..D-8 are post-BATCH-713991 amendments from BATCH-b41ba9)
- BATCH-713991/tasks/TASK-20260804-f5e58b/PREREGISTRATION.md + RESULTS.json (whole)
- BATCH-713991/tasks/TASK-20260804-d7d0ec/PREREGISTRATION.md + RESULTS.json (whole)
- ledger/goals/GOAL-AES-003.yaml lines 440-639 (merge notes) and 893-1152 (batch_checkpoints; BATCH-713991 entry at 893-938; BATCH-013/RC-C entry at 974-1004)
- BATCH-713991/archives/TASK-20260804-777cb6/snapshot-receipt.json and TASK-20260804-0e75d5/ledger-receipt.json
- BATCH-b41ba9/archives/TASK-20260806-3998cd/ledger-receipt.json (to check the "Red Team R3 report" citation in EV O-8)

## NOT read (blindness within round)
- TASK-20260901-bcde48 (validator re-run) outputs — not opened.
- No arm-count recomputation from raw receipts (validator's joint).

## Provenance verification commands (read-only git)
- ls BATCH-713991/tasks/ -> only d7d0ec/, f5e58b/ (no fa4906/, no 91d27e/).
- git log --all --diff-filter=A -- "coordination/goals/GOAL-AES-003/batches/BATCH-713991/tasks/TASK-20260804-fa4906/*" -> EMPTY.
- git log --all --diff-filter=A -- "coordination/goals/GOAL-AES-003/batches/BATCH-713991/tasks/TASK-20260804-91d27e/*" -> EMPTY.
- git log --all --grep fa4906 -> only the BATCH-903b65 open commit 2a3bfc45f.
- grep -rl "red_team" under BATCH-b41ba9/ -> no matches; BATCH-b41ba9 queue has no red-team card; tasks/ holds only 47f217 + 7a980b.
- grep for RC-C / d81acf in BATCH-713991 records and in EV-AES-048545 / DEC-20260804-73977c -> zero matches.

## My own numerical derivations (3 small python invocations; no experiment runs)
- Poisson(4): P(X<=12)=0.9997263, so alpha of the >=13 rule = 2.737e-4 (prereg's ~2.7e-4 verified).
- P(X<=3 | lam=4) = 0.4335 (r=10 null of 3 is unremarkable).
- 2/2 successes: exact one-sided 95% lower bound on class reproduction rate p_L = 0.05^(1/2) = 0.2236.
- 51 vs 59 counts: two-sample Poisson z = 8/sqrt(110) = 0.763 (well inside 1 sigma; magnitudes not distinguishable).
- Control-band leakage: a control arm with true rate lam=12 (3x null) still passes (X<=12) with prob 0.576; lam=15.2 with prob 0.251.
- Plausibility of cited "0.53 at 80% power": two-sample normal-approx Poisson comparison vs AES arm (lam1=59), 80% power, alpha=0.05: min resolvable relative attenuation 0.438 (one-sided) / 0.487 (two-sided) on excess-over-null basis; 0.408/0.454 on total-mean basis. The cited 0.53 is same order, slightly conservative, but its derivation is in no landed artifact.
- ATTACK-6 adjacency: P(Binom(40,1/8)<=7)=0.881 (SURVIVES cutoff is generous under the null); P(Binom(40,0.25)<=7)=0.182 (a true 2x-elevated forcing rate would still pass ~18% of the time); observed 6/40 is one trial below the cutoff 7/40.

## Key audit findings (full versions in the report)
1. Claim boundary (DEC D-2/D-5 + checkpoint lines 910-913) holds at the rule's resolution; no overreach in the ruling itself.
2. "reproduce" carries three readings; only non-necessity of AES values + 2-instance reproduction is bound (ATTACK-1).
3. [0,12] band is one-sided in practice; lower end vacuous; tolerates ~3x-null leakage in controls (ATTACK-2).
4. Population of two: class reproduction rate lower bound 0.2236; RC-C/EV-AES-d81acf lesson never acknowledged in BATCH-713991 records (ATTACK-4).
5. Both review artifacts (fa4906 red-team, 91d27e validator) exist in no branch, yet are cited by the ledger receipt, DEC D-2/decision_note, and EV O-1/O-3/O-5; EV O-8 additionally cites a "Red Team R3 report" that also has no artifact (ATTACK-5, U-1..U-8).
6. Checkpoint line 901 "The campaign's last untested specificity" contradicted by BATCH-013/RC-C's prior S-box-specificity measurement (U-1).
7. Original-gate items covered: decay-control design (ATTACK-6), BATCH-003 repair audit (ATTACK-7), most-hurting finding named.

Budget: 2400s wall; elapsed ~9 min from claim commit. experiment_runs: 0; analysis invocations: 3.
