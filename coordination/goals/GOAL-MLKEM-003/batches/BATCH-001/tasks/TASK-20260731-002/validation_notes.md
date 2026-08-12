# Validation notes — TASK-20260731-002 / EXP-MLKEM-015

Independent of the Executor. Report id **VAL-20260731-001**. No official state changed. No git commit performed.

## Inference

- `requested_policy`: review-xhigh
- `resolved_model_id`: cursor-grok-4.5 (`fallback_used: true`)
- `independent_session`: true

## Pins / cost-model discipline

- lattice-estimator vendor HEAD and `results.json` both report `3e48ef421ec256afddb3e7d2249a77eab6e9ba12`.
- pq-crystals security-estimates HEAD and results report `75c26949a902ca297b181375bfb7cfaf22cce784`.
- All six source-lock file SHA-256 values match the local vendor checkouts.
- Dual vs primal decision metrics use the same `RC.MATZOV` object (`CTRL-MATCHED-COST-MODEL`). ADPS16 is control-only; GJ21 is not in the decision rule. No cross-model matched claim.

## Official core-SVP control

`kyber_official_security_estimates.txt` classical primal/dual columns and betas match `results.json` (`118/117`, `183/181`, `256/253`; betas `406/403`, `626/620`, `878/868`).

## Conjunct recomputation (from `results.json`)

| set | dual+fft MATZOV | primal_bdd MATZOV | Δ dual−primal | Carrier−dual | MATZOV22−dual | NIST−primal | \|ADPS16−Kyber.py\| |
|---|---:|---:|---:|---:|---:|---:|---:|
| Kyber512 | 143.7885 | 140.1995 | +3.5890 | −4.2885 | −6.2885 | +2.8005 | 0.552 |
| Kyber768 | 203.7879 | 200.9587 | +2.8291 | −8.6879 | −10.2879 | +6.0413 | 0.792 |
| Kyber1024 | 273.8173 | 270.7236 | +3.0936 | −14.1173 | −16.0173 | +1.2764 | 0.792 |

- **C1** holds (dual+fft does not beat primal_bdd; all Δ ≥ 0).
- **C2** holds (Carrier ≤ −4 bits on 3/3 sets; MATZOV-2022 also 3/3).
- **C3** holds (primal_bdd < NIST on all sets).
- **C4** holds (ADPS16 vs Kyber.py within 1.5 bits on all sets).

No H-MLKEM-014 falsification_condition fires. Recorded delta fields match independent recomputation.

## Scope

Estimate-only package. No key recovery, no FIPS-203 break language, Carrier polar heuristics not reimplemented. Matches specification non-claims / claim_tier medium.

## Qualifications (do not invalidate decision rule)

| ID | Issue |
|----|--------|
| Q-MISSING-RAW-BY-SCHEME | Full cost grid (incl. GJ21, fft=False) absent from results.json |
| Q-BEST-ATTACK-OMITS-FFT-FALSE | `best_MATZOV_attack` min omits fft=False despite ±fft wording |
| Q-UNCOMMITTED-WORKING-TREE-PACKAGE | Experiment + draft ledger untracked at validation HEAD |
| Q-NO-SAGE-REEXECUTION | Arithmetic + pin checks only; Sage not re-run |
| Q-LEDGER-DRAFTED-BEFORE-VALIDATION | Draft EV/DEC/KN-FIND already agree numerically |

## Verdict

| Field | Value |
|-------|--------|
| verdict | **accept_with_qualifications** |
| blocks_ledger_record | **false** |
| all four conjuncts | hold |
| matched cost-model | pass |
| scope | pass |
