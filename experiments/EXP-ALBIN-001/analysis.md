# Analysis — Autolab binary-field BIN-EXP-001: Weil-descent gate

## Observation
**Date:** 2026-05-31. Script: `bin_exp001_weil_descent_gate.sage`. Log: `bin_exp001_weil_descent_gate.log`.

Source excerpt / raw summary:

```
# BIN-EXP-001 Result — binary Weil-descent Semaev first fall + gated meter

**Date:** 2026-05-31. Script: `bin_exp001_weil_descent_gate.sage`. Log: `bin_exp001_weil_descent_gate.log`.
**Completion:** 5 of 6 planned cells completed; the 6th cell (n=11, m=3) was KILLED after ~16 min (expensive S₄ resultant + variety) and is NOT reported (no fabricated row). Meter self-validated OVERALL_PASS=True in-run.

## SURVIVOR: NO · CANDIDATE: NO · primary finding = a RED-TEAM CATCH (the gate does not discriminate here)

## Raw results — read byte-for-byte from the log (5 cells)

| n | m | S_{m+1} genuine | real d_ff | D_reg | fires | gate_meaningful | **neg-ctrl gate_mng** | pos_ctrl | nvars | descended degs |
|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 2 | True (25/25 vanish) | 3 | 3 | False | False | False | True | 4 | [2,4] |
| 7 | 2 | True | 4 | 5 | True | True | **True** | True | 8 | [4] |
| 11 | 2 | True | 4 | 7 | True | True | **True** | True | 12 | [4] |
| 13 | 2 | True | 4 | 7 | True | True | **True** | True | 12 | [4] |
| 7 | 3 | True | None | 7 | False | False | False | None | 6 | [9,12] |

(n=11, m=3: not completed — killed; reported as OPEN, not as a result.)

## What is genuinely established (positive)

1. **Binary Semaev polynomials built and VERIFIED.** S₃ = (X₁X₂+X₁X₃+X₂X₃)² + X₁X₂X₃ + a₆ vanishes 25/25 on real summing triples, nonzero on non-summing; S₄ (resultant of two S₃) likewise GENUINE_VERIFIED=True at n=7. Char-2 group-law construction correct.
2. **The descended system has an early first fall over binary for m=2** (d_ff=4 < D_reg=5/7) — unlike the prime-field x-ring which had no early fall (NR-017/NR-032). Consistent with FPPR/Kosters–Yeo.
3. **Positive control validates the Weil descent** (m=2): a real decomposition R=P₁+P₂ with x(Pᵢ)∈V satisfies the descended F₂ system (pos_ctrl=True). Descent code correct.

## The RED-TEAM CATCH (decisive scope correction)

**In every firing m=2 cell, the random matched-degree negative control ALSO reports gate_meaningful=True** (neg-ctrl column). Therefore over binary, `gate_meaningful=True` is **not** evidence of exploitable Semaev/IC leverage — it is a generic property of the degree profile.

**Mechanism (why the prime-field gate does not transfer):** the localization gate asks "does deleting the summation rows shrink the nontrivial kernel at d_ff?" In the prime-field e-ring artifact (NR-019) the Semaev row and FB-constraint rows occupied the *same low degree tier*, so the gate could isolate whether the *Semaev* row drove the fall. In the binary Weil-descent setting the descended-Semaev components (degree 4, or 9–12 for m=3) and the field equations c²+c (degree 2) occupy *separated degree tiers*; the descended-Semaev rows are the unique highest-degree rows, so they trivially participate in the first fall — and so does **any** random system of the same degrees. The gate here measures *degree-tier participation*, not *structural genuineness*.

**Instrumented confirmation of the literature:** this reproduces Kosters–Yeo 2015 ("low FFD ≠ fast solving") and Huang–Kosters–Yeo 2015 ("FFD↔D_reg link unjustified for ECDLP systems") with a controlled measurement: the binary descended-Semaev first fall carries no more leverage than a random system of identical degree profile at toy n.

## Claim label

`NEGATIVE RESULT` (methodological / scope, TOY-EVIDENCE n≤13) → **BIN-NR-001**: the prime-field localization gate does NOT transfer as a discriminator to the binary Weil-descent Semaev setting; at toy n the binary descended first fall is generic to the degree profile (real-system d_ff and gate_meaningful match the random control), so gate_meaningful=True is not evidence of IC leverage.

## What this does NOT rule out

- It does NOT say binary IC can't beat rho. The FPPR/Petit–Quisquater subexponential heuristic concerns **asymptotic D_reg growth at large n with optimal m** (crossover estimated n≫2000), which toy n∈{5..13} cannot reach.
```

## Comparison
Compared against Autolab's stated baseline (typically Pollard rho / VW / Wesolowski-class
isogeny cost, depending on topic). This import does not recompute those baselines inside
crypto-autoresearcher.

## Inference
`OBSERVATION` / `TOY-EVIDENCE` (or Autolab's original label if stronger, still not upgraded):
the Autolab package is now citeable as `EXP`+`RUN` evidence under the harness. Scientific
content remains bounded by Autolab's original scope and caveats.

## Limitation
- Not independently re-executed in this repository.
- Certificates were not re-verified; do not promote discrete-log / decomposition claims.
- Claim tier remains `toy` unless a later harness experiment re-runs with certificates.
