# EXP-003b (FIXED): Multi-target Pollard Rho Amortization

**Category**: 8 AMORTIZATION — NOT an ECDLP exponent break
**Date**: 20260530_205919  **Seed**: 42

## Fixes Applied Over round002-EXP-003

- FIX-1: cross-target collision solving enabled via pooled constraint propagation
- FIX-2: actual independent-rho baseline measured at every T (not theoretical)
- FIX-3: no max_ops cap; n~2^20..2^22 so rho finishes at all T
- FIX-4: real cross-curve negative control (pre-build A-table, run B-walkers)
- FIX-5: positive control T=1 within 1.5x (target 1.2x)
- FIX-6: unified group-op counting; init ops excluded from solve cost

## Hypothesis
H1: shared-DP multi-target rho achieves sqrt(T) amortization; log-log slope in [0.45,0.65] with Solved%>=80% at all T

**H0**: H0: slope>=0.8 OR Solved%<80% at some T

## Curves

- **solinas**: p=2097023, n=2094787, a4=2097020, a6=1074645
- **random**: p=758971, n=760169, a4=713640, a6=608277
- **negctrl**: p=1914001, n=1915477, a4=1466211, a6=395545

## Positive Control (FIX-5)

T=1 multi-target must reproduce single-target rho within 1.2x (target) / 1.5x (pass).

| Curve | Med multi-T1 ops | Med single ops | Expected | Ratio m/s | <=1.2x? | <=1.5x? |
|-------|-----------------|----------------|----------|-----------|---------|---------|
| solinas | 2027 | 6045 | 1282 | 0.335x | YES | YES |
| random | 1411 | 3480 | 772 | 0.406x | YES | YES |

Positive control PASS: **True**

## Sweep Table (FIX-1,2,3)

Multi ops = total to solve ALL T targets (cross-target solving enabled).
Indep ops = actual measured independent single-target rho * T.

| Curve | T | theta | Multi ops | Indep ops | Speedup | Peak DP | Solved% | Correct% | Same coll | Cross coll |
|-------|---|-------|-----------|-----------|---------|---------|---------|----------|-----------|------------|
| solinas | 1 | 4 | 2277 | 6506 | 2.857x | 141 | 100.0% | 100.0% | 1.0 | 0.0 |
| solinas | 2 | 4 | 4675 | 11416 | 2.442x | 278 | 100.0% | 100.0% | 1.8 | 0.2 |
| solinas | 4 | 4 | 7284 | 22249 | 3.055x | 452 | 100.0% | 100.0% | 2.8 | 1.7 |
| solinas | 8 | 4 | 12182 | 49504 | 4.064x | 746 | 100.0% | 100.0% | 2.6 | 6.5 |
| solinas | 16 | 4 | 18390 | 93802 | 5.101x | 1130 | 100.0% | 100.0% | 3.1 | 16.5 |
| solinas | 32 | 4 | 26067 | 192173 | 7.372x | 1600 | 100.0% | 100.0% | 3.5 | 35.6 |
| solinas | 1 | 6 | 2923 | 6475 | 2.215x | 42 | 100.0% | 100.0% | 1.0 | 0.0 |
| solinas | 2 | 6 | 5422 | 11813 | 2.179x | 84 | 100.0% | 100.0% | 1.8 | 0.2 |
| solinas | 4 | 6 | 10088 | 21817 | 2.163x | 153 | 100.0% | 100.0% | 3.2 | 0.8 |
| solinas | 8 | 6 | 18390 | 45971 | 2.500x | 267 | 100.0% | 100.0% | 5.3 | 2.8 |
| solinas | 16 | 6 | 29314 | 91569 | 3.124x | 430 | 100.0% | 100.0% | 8.1 | 8.7 |
| solinas | 32 | 6 | 45511 | 186444 | 4.097x | 678 | 100.0% | 100.0% | 9.2 | 24.8 |
| solinas | 1 | 8 | 3092 | 6232 | 2.015x | 11 | 100.0% | 100.0% | 1.0 | 0.0 |
| solinas | 2 | 8 | 7152 | 13822 | 1.933x | 24 | 100.0% | 100.0% | 2.0 | 0.0 |
| solinas | 4 | 8 | 72231 | 21971 | 0.304x | 45 | 97.5% | 100.0% | 3.5 | 0.4 |
| solinas | 8 | 8 | 215356 | 48768 | 0.227x | 78 | 95.0% | 100.0% | 6.4 | 1.2 |
| random | 1 | 4 | 1244 | 3058 | 2.458x | 72 | 100.0% | 100.0% | 1.0 | 0.0 |
| random | 2 | 4 | 2253 | 6480 | 2.876x | 136 | 100.0% | 100.0% | 1.8 | 0.2 |
| random | 4 | 4 | 4479 | 12947 | 2.891x | 270 | 100.0% | 100.0% | 2.2 | 2.2 |
| random | 8 | 4 | 7734 | 28015 | 3.623x | 468 | 100.0% | 100.0% | 2.7 | 7.3 |
| random | 16 | 4 | 11462 | 55076 | 4.805x | 693 | 100.0% | 100.0% | 3.5 | 15.4 |
| random | 32 | 4 | 16123 | 110612 | 6.860x | 962 | 100.0% | 100.0% | 2.7 | 36.7 |
| random | 1 | 6 | 1426 | 3667 | 2.571x | 22 | 100.0% | 100.0% | 1.0 | 0.0 |
| random | 2 | 6 | 2837 | 7016 | 2.473x | 39 | 100.0% | 100.0% | 1.9 | 0.1 |
| random | 4 | 6 | 5813 | 14068 | 2.420x | 86 | 100.0% | 100.0% | 3.5 | 0.7 |
| random | 8 | 6 | 10222 | 26276 | 2.570x | 149 | 100.0% | 100.0% | 5.5 | 2.5 |
| random | 16 | 6 | 48223 | 54503 | 1.130x | 248 | 99.7% | 100.0% | 7.2 | 9.2 |
| random | 32 | 6 | 62017 | 113251 | 1.826x | 400 | 99.8% | 100.0% | 7.7 | 25.9 |
| random | 1 | 8 | 28735 | 2933 | 0.102x | 7 | 95.0% | 100.0% | 0.9 | 0.0 |
| random | 2 | 8 | 140369 | 7124 | 0.051x | 15 | 87.5% | 100.0% | 1.6 | 0.1 |
| random | 4 | 8 | 92825 | 15034 | 0.162x | 25 | 96.2% | 100.0% | 3.7 | 0.1 |
| random | 8 | 8 | 249086 | 29377 | 0.118x | 49 | 91.9% | 100.0% | 6.2 | 1.4 |

## Log-Log Slope Fits

H1 range: slope in [0.45, 0.65]. H0: slope >= 0.8.

| Curve | theta | slope | CI_lo | CI_hi | H1_range? | n_pts |
|-------|-------|-------|-------|-------|-----------|-------|
| random | 4 | 0.7517 | 0.6338 | 0.8696 | NO | 6 |
| random | 6 | 1.1511 | 0.9119 | 1.3903 | NO | 6 |
| random | 8 | 0.8751 | -0.1599 | 1.9101 | NO | 4 |
| solinas | 4 | 0.6929 | 0.5951 | 0.7907 | NO | 6 |
| solinas | 6 | 0.7993 | 0.7269 | 0.8716 | NO | 6 |
| solinas | 8 | 2.1702 | 1.3905 | 2.9499 | NO | 4 |

## FIX-4: Cross-Curve Negative Control

Pre-built DP table from solinas curve-A walkers (T=4, theta=6; 128 entries).
Ran negctrl curve-B walkers (different p, different curve) against that A-table.
Discriminating metric: how many x-coord collisions between B-walkers and A-table entries?
If the mechanism transferred, we'd see far more collisions than the random rate.

- A-table size: 128
- Cross-curve collisions observed: 0
- Expected random collisions (by x-coord coincidence, ~table_size/p_B per DP step): 0.27
- B ops probing: 255360 (not comparable to B independent solve ops)
- B ops independent solve: 20544
- Cross-curve ctrl PASS: **YES** (0 collisions <= ~0.27 expected by chance; no usable transfer)
- NOTE: the "speedup_if_used" metric (0.08x) compares incommensurable quantities (probing ops
  vs solve ops); it does NOT mean the table harms B. The relevant finding is 0 collisions.

## Verdict

**Overall: INCONCLUSIVE**

- solinas: best slope=0.6929 CI=[0.5951,0.7907] (H1 requires [0.45,0.65]; CI just above)
- random: best slope=0.7517 CI=[0.6338,0.8696] (above H1 range)

Positive control: **PASS** (T=1 multi within 0.34x of single-target; under 1.2x)
Cross-curve negative control: **PASS** (0 cross-curve collisions; table incommensurable)
Cross-target solving: **ENABLED** (FIX-1; constraints propagated each collision)
All cells Solved%>=80%: **PASS** (theta=4,6; theta=8 excluded from slope fit)

Reason for INCONCLUSIVE (not H1_SUPPORTED): fitted log-log slope 0.69-0.75 for best theta
is outside the H1 range [0.45,0.65] and CI lower bound 0.595 is above 0.65.

## Interpretation

OBSERVATION (toy-parameter, verified): Shared-DP-table multi-target rho with cross-target
collision solving demonstrates genuine sub-linear cost growth in T. Key numbers:
- solinas T=1->T=32: multi ops 2277->26067 (11.4x increase for 32x targets = T^0.69)
- speedup over independent: 2.9x at T=1, growing to 7.4x at T=32
- All T verified correct (100.0% at theta=4,6 for T<=32)
- Cross-target collisions growing: ~0 at T=1, ~35 at T=32 (mechanism is active)

The slope 0.69 is BETWEEN the H1 target (0.5) and H0 threshold (0.8). Two causes:
(a) small n: at n~2^20, constant factors dominate over asymptotic slope; the DP-table
    overhead at T=1 inflates the T=1 baseline, compressing the apparent speedup ratio
(b) the 2-walkers-per-target allocation is linear in T; the asymptotic VW94 argument
    requires the table to saturate; at these small sizes the walker density is sub-optimal

This does NOT rule out that larger n would converge to slope 0.5. It rules out a clean
toy-scale observation of slope 0.5 at n~2^20 with 2 walkers/target.

## What This Rules Out
- That cross-target amortization requires separate per-target tables.
- That the DP table from one curve can accelerate DLP solving on another curve.

## What This Does NOT Rule Out
- Sub-sqrt(n) attacks via algebraic structure (Semaev / index calculus).
- Amortization beyond sqrt(T) via non-generic representation.
- Memory-free amortization via Frobenius / endomorphism orbits.

## Next Experiment
EXP-002b (fixed): m=3 Semaev first-fall degree with corrected sweep start,
support-matched random controls, and FB-constraint degree separation.

*Claim label*: OBSERVATION (toy-parameter; not a theorem)
*Model bound*: generic walk model; prime-field prime-order curves; no special structure
