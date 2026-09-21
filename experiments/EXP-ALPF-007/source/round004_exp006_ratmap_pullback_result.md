# EXP-006 Result: TRUE rational-map pullback (D_reg-conservation escape)

SEED=42  timestamp=2026-05-30 22:19:34

## Meter validation (fix DEFECT-A)

| control | d_ff | D_reg_pred | early_fall | role |
|---|---|---|---|---|
| P2 planted shared-factor syzygy | 7 | 7 | False | GATING positive |
| P1 overdetermined 4 quadrics | 3 | 3 | False | informational positive |
| N regular [2,2,2] CI | 4 | 4 | False | negative |

**METER VALIDATED: False** (positive fires=False, negative quiet=True)

## Degree table: pullback vs x-ring baseline

S4 baseline: total_deg=12, per-var deg=4 (m=3 Semaev S4).

| curve | |FB| | phi | deg(phi) | S4_phi total | S4_phi per-var | FB-deg(t) | D_reg(pull) | d_ff(pull) | D_reg(base) | d_ff(base) | net D_reg lower? | both degrees down? | preimg verify |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| structured/13b | 4 | id | 1 | 12 | 4 | 4 | 10 | 10 | 10 | 10 | False | False | True |
| structured/13b | 4 | t2 | 2 | 24 | 8 | 3 | 7 | 7 | 10 | 10 | True | False | True |
| structured/13b | 4 | t2c | 2 | 24 | 8 | 1 | 1 | 1 | 10 | 10 | True | False | True |
| structured/13b | 4 | t3ct | 3 | 36 | 12 | 1 | 1 | 1 | 10 | 10 | True | False | True |
| structured/13b | 6 | id | 1 | 12 | 4 | 6 | 14 | 14 | 14 | 14 | False | False | True |
| structured/13b | 6 | t2 | 2 | 24 | 8 | 3 | 7 | 7 | 14 | 14 | True | False | True |
| structured/13b | 6 | t2c | 2 | 24 | 8 | 2 | 4 | 4 | 14 | 14 | True | False | True |
| structured/13b | 6 | t3ct | 3 | 36 | 12 | 3 | 7 | 7 | 14 | 14 | True | False | True |
| structured/13b | 9 | id | 1 | 12 | 4 | 9 | 18 | 18 | 18 | 18 | False | False | True |
| structured/13b | 9 | t2 | 2 | 24 | 8 | 3 | 7 | 7 | 18 | 18 | True | False | True |
| structured/13b | 9 | t2c | 2 | 24 | 8 | 3 | 7 | 7 | 18 | 18 | True | False | True |
| structured/13b | 9 | t3ct | 3 | 36 | 12 | 6 | 16 | 16 | 18 | 18 | True | False | True |
| structured/15b | 4 | id | 1 | 12 | 4 | 4 | 10 | 10 | 10 | 10 | False | False | True |
| structured/15b | 4 | t2 | 2 | 24 | 8 | 1 | 1 | 1 | 10 | 10 | True | False | True |
| structured/15b | 4 | t2c | 2 | 24 | 8 | 1 | 1 | 1 | 10 | 10 | True | False | True |
| structured/15b | 4 | t3ct | 3 | 36 | 12 | 3 | 7 | 7 | 10 | 10 | True | False | True |
| structured/15b | 6 | id | 1 | 12 | 4 | 6 | 14 | 14 | 14 | 14 | False | False | True |
| structured/15b | 6 | t2 | 2 | 24 | 8 | 2 | 4 | 4 | 14 | 14 | True | False | True |
| structured/15b | 6 | t2c | 2 | 24 | 8 | 2 | 4 | 4 | 14 | 14 | True | False | True |
| structured/15b | 6 | t3ct | 3 | 36 | 12 | 5 | 13 | 13 | 14 | 14 | True | False | True |
| structured/15b | 9 | id | 1 | 12 | 4 | 9 | 18 | 18 | 18 | 18 | False | False | True |
| structured/15b | 9 | t2 | 2 | 24 | 8 | 4 | 10 | 10 | 18 | 18 | True | False | True |
| structured/15b | 9 | t2c | 2 | 24 | 8 | 3 | 7 | 7 | 18 | 18 | True | False | True |
| structured/15b | 9 | t3ct | 3 | 36 | 12 | 7 | 19 | 19 | 18 | 18 | False | False | True |
| structured/17b | 4 | id | 1 | 12 | 4 | 4 | 10 | 10 | 10 | 10 | False | False | True |
| structured/17b | 4 | t2 | 2 | 24 | 8 | 2 | 4 | 4 | 10 | 10 | True | False | True |
| structured/17b | 4 | t2c | 2 | 24 | 8 | 2 | 4 | 4 | 10 | 10 | True | False | True |
| structured/17b | 4 | t3ct | 3 | 36 | 12 | 3 | 7 | 7 | 10 | 10 | True | False | True |
| structured/17b | 6 | id | 1 | 12 | 4 | 6 | 14 | 14 | 14 | 14 | False | False | True |
| structured/17b | 6 | t2 | 2 | 24 | 8 | 4 | 10 | 10 | 14 | 14 | True | False | True |
| structured/17b | 6 | t2c | 2 | 24 | 8 | 3 | 7 | 7 | 14 | 14 | True | False | True |
| structured/17b | 6 | t3ct | 3 | 36 | 12 | 3 | 7 | 7 | 14 | 14 | True | False | True |
| structured/17b | 9 | id | 1 | 12 | 4 | 9 | 18 | 18 | 18 | 18 | False | False | True |
| structured/17b | 9 | t2 | 2 | 24 | 8 | 4 | 10 | 10 | 18 | 18 | True | False | True |
| structured/17b | 9 | t2c | 2 | 24 | 8 | 4 | 10 | 10 | 18 | 18 | True | False | True |
| structured/17b | 9 | t3ct | 3 | 36 | 12 | 6 | 16 | 16 | 18 | 18 | True | False | True |
| random/13b | 4 | id | 1 | 12 | 4 | 4 | 10 | 10 | 10 | 10 | False | False | True |
| random/13b | 4 | t2 | 2 | 24 | 8 | 3 | 7 | 7 | 10 | 10 | True | False | True |
| random/13b | 4 | t2c | 2 | 24 | 8 | 1 | 1 | 1 | 10 | 10 | True | False | True |
| random/13b | 4 | t3ct | 3 | 36 | 12 | 3 | 7 | 7 | 10 | 10 | True | False | True |
| random/13b | 6 | id | 1 | 12 | 4 | 6 | 14 | 14 | 14 | 14 | False | False | True |
| random/13b | 6 | t2 | 2 | 24 | 8 | 3 | 7 | 7 | 14 | 14 | True | False | True |
| random/13b | 6 | t2c | 2 | 24 | 8 | 2 | 4 | 4 | 14 | 14 | True | False | True |
| random/13b | 6 | t3ct | 3 | 36 | 12 | 5 | 13 | 13 | 14 | 14 | True | False | True |
| random/13b | 9 | id | 1 | 12 | 4 | 9 | 18 | 18 | 18 | 18 | False | False | True |
| random/13b | 9 | t2 | 2 | 24 | 8 | 4 | 10 | 10 | 18 | 18 | True | False | True |
| random/13b | 9 | t2c | 2 | 24 | 8 | 2 | 4 | 4 | 18 | 18 | True | False | True |
| random/13b | 9 | t3ct | 3 | 36 | 12 | 5 | 13 | 13 | 18 | 18 | True | False | True |
| random/15b | 4 | id | 1 | 12 | 4 | 4 | 10 | 10 | 10 | 10 | False | False | True |
| random/15b | 4 | t2 | 2 | 24 | 8 | 3 | 7 | 7 | 10 | 10 | True | False | True |
| random/15b | 4 | t2c | 2 | 24 | 8 | 2 | 4 | 4 | 10 | 10 | True | False | True |
| random/15b | 4 | t3ct | 3 | 36 | 12 | 2 | 4 | 4 | 10 | 10 | True | False | True |
| random/15b | 6 | id | 1 | 12 | 4 | 6 | 14 | 14 | 14 | 14 | False | False | True |
| random/15b | 6 | t2 | 2 | 24 | 8 | 3 | 7 | 7 | 14 | 14 | True | False | True |
| random/15b | 6 | t2c | 2 | 24 | 8 | 3 | 7 | 7 | 14 | 14 | True | False | True |
| random/15b | 6 | t3ct | 3 | 36 | 12 | 3 | 7 | 7 | 14 | 14 | True | False | True |
| random/15b | 9 | id | 1 | 12 | 4 | 9 | 18 | 18 | 18 | 18 | False | False | True |
| random/15b | 9 | t2 | 2 | 24 | 8 | 5 | 13 | 13 | 18 | 18 | True | False | True |
| random/15b | 9 | t2c | 2 | 24 | 8 | 4 | 10 | 10 | 18 | 18 | True | False | True |
| random/15b | 9 | t3ct | 3 | 36 | 12 | 6 | 16 | 16 | 18 | 18 | True | False | True |
| random/17b | 4 | id | 1 | 12 | 4 | 4 | 10 | 10 | 10 | 10 | False | False | True |
| random/17b | 4 | t2 | 2 | 24 | 8 | 3 | 7 | 7 | 10 | 10 | True | False | True |
| random/17b | 4 | t2c | 2 | 24 | 8 | 2 | 4 | 4 | 10 | 10 | True | False | True |
| random/17b | 4 | t3ct | 3 | 36 | 12 | 4 | 10 | 10 | 10 | 10 | False | False | True |
| random/17b | 6 | id | 1 | 12 | 4 | 6 | 14 | 14 | 14 | 14 | False | False | True |
| random/17b | 6 | t2 | 2 | 24 | 8 | 3 | 7 | 7 | 14 | 14 | True | False | True |
| random/17b | 6 | t2c | 2 | 24 | 8 | 2 | 4 | 4 | 14 | 14 | True | False | True |
| random/17b | 6 | t3ct | 3 | 36 | 12 | 5 | 13 | 13 | 14 | 14 | True | False | True |
| random/17b | 9 | id | 1 | 12 | 4 | 9 | 18 | 18 | 18 | 18 | False | False | True |
| random/17b | 9 | t2 | 2 | 24 | 8 | 5 | 13 | 13 | 18 | 18 | True | False | True |
| random/17b | 9 | t2c | 2 | 24 | 8 | 4 | 10 | 10 | 18 | 18 | True | False | True |
| random/17b | 9 | t3ct | 3 | 36 | 12 | 7 | 19 | 19 | 18 | 18 | False | False | True |

## Controls outcome

- Identity map phi(t)=t reproduces x-ring baseline (D_reg match): **True**
- Meter validated on known positive: **False**

## Verdict

INCONCLUSIVE -- meter not validated; 'no early fall' results cannot be promoted to NEGATIVE (DEFECT-A unmet).

## What this rules out / does not rule out

- Rules out (scoped): finite-set rational-map pullback FB lowering D_reg for m=3 Semaev on the swept toy prime curves, given a validated meter.
- Does NOT rule out: (a) maps phi whose image is cut by a FIXED low-degree equation independent of |FB| (e.g. trace/norm/subfield membership) -- the structural-pullback variant; (b) non-Buchberger solvers (crossbred/XL) where d_ff, not D_reg, governs cost; (c) larger m where the S4-degree/FB-degree tradeoff shifts.

## Next

- Test a FIXED-degree membership FB (trace-zero / subfield / norm-1) where the FB-constraint degree is bounded INDEPENDENTLY of |FB|, the only remaining lever to drop both degrees at once.
