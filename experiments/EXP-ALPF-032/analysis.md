# Analysis — Autolab prime-field: round020_solvegate

## Observation
{'e_ic_decomp_ops': 0.8892717464264962, 'e_rho_empirical': 0.25922705660116446, 'rho_theory_exponent': '0.500000000000000', 'ic_solved_sizes': ['10', '12', '14', '16']}

Source excerpt / raw summary:

```
# Round 020 Results — EXP-020 end-to-end solve-gate: m=3 Semaev IC vs rho

Date: 2026-06-01. Closes PAPER §6.2(iii) (the never-run end-to-end measurement). Contract:
`round020_solvegate_contract.md`. Reproduction: `round020_solvegate_ic_vs_rho.sage` (+ `.log`, `_result.json`).

## What was run

A **real m=3 Semaev index calculus that solves a discrete logarithm end-to-end** — factor base
|FB|=L≈n^{1/3} (smallest valid x-coordinates), relation generation by Semaev S_4 decomposition
(enumerate (x1,x2)∈FB + quartic root for x3∈FB + sign-lift, an exact fully-counted decomposition),
linear algebra over Z/n recovering the FB logs and the target x — benchmarked against Pollard rho
(averaged over 8 runs) on the same instances, across 5 sizes.

## Results (`round020_solvegate.log`)

| bits | n | L=\|FB\| | rho_ops (avg) | IC decomp-ops | IC solved x? | rho solved x? | IC_decomp / rho_theory |
|---|---|---|---|---|---|---|---|
| 10 | 1201 | 11 | 44 | 935 | **True** | True | 21.5 |
| 12 | 4021 | 16 | 3324* | 3547 | **True** | True | 44.6 |
| 14 | 16453 | 25 | 153 | 14447 | **True** | True | 89.9 |
| 16 | 65407 | 40 | 859 | 31346 | **True** | True | 97.8 |
| 18 | 262543 | 64 | 559 | 132074 | rank-short† | True | 205.7 |

(* rho op-count is high-variance at toy n — intrinsic to rho + DP-cycle pathology; we anchor the rho
baseline to the textbook √(πn/2), exponent exactly 0.5. † at L=64 the L+24 relations were rank-short
for the final GF(n) solve; the decomposition cost is still exactly counted and the ratio valid.)

**Positive control passes:** the IC recovered the **correct** discrete log at bits 10, 12, 14, 16
(Q = xP verified) — it is a genuine solver, not a proxy.

## Scaling — the deliverable

- **IC decomposition-ops exponent = 0.889** (cost ~ n^{0.89}; the dominant IC cost), fit over all 5 sizes.
- **rho exponent = 0.5** (√(πn/2), textbook; empirical toy-n op-count too noisy to fit — sanity only).
- **IC/rho ratio grows monotonically 21.5→205.7** over bits 10→18.
- **VERDICT (`OBSERVATION`, TOY-EVIDENCE, ≤18 bits): IC exponent 0.89 ≫ rho 0.5 — no crossover; the
  IC/rho gap GROWS as ~n^{0.39}.** This converts the campaign's first-fall result ("no early fall")
  into an end-to-end statement ("no end-to-end win") at toy scale.

## Structural reason it cannot win (the factor-base → linear-algebra floor)
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
