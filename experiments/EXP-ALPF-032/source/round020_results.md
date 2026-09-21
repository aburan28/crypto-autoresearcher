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

The measured exponent is not an artifact of the enumerate-decomposition; it is forced by the IC
structure, and the point is sharper than the measurement:

- m-point IC needs ≈|FB| relations with |FB|≈n^{1/m} (so relation probability |FB|^m/n is ~constant).
- **Even with a *free* decomposition oracle**, the sparse linear algebra over the |FB|×|FB| relation
  matrix costs ≈|FB|² = n^{2/m}. For **m=3 that is n^{2/3} > √n = n^{1/2}** — already above rho.
  So m=3 IC **cannot beat rho even if decomposition were free**; our measured n^{0.89} (decomposition
  dominating at toy scale) is consistent and conservative.
- m=4 is the boundary (|FB|≈n^{1/4} ⇒ linalg ≈ n^{1/2} = rho), but there the **decomposition** cost
  (S_5, degree 32, D_reg pinned by Yokoyama 2020) explodes faster than the linalg saving — the
  Diem/Gaudry tradeoff. So the linear-algebra floor and the decomposition ceiling close from both sides.

`HEURISTIC`/structural: this is the end-to-end cost reason that the first-fall (D_reg) resistance map
was a proxy for — now measured directly and explained.

## Claim label after experiment

`OBSERVATION` (TOY-EVIDENCE, ≤18 bits, verified solver): end-to-end m=3 Semaev IC solves prime-field
ECDLP but at cost exponent ≈0.89 (≥ n^{2/3} structurally), strictly above rho's n^{1/2}, with the gap
growing — no crossover at toy scale. Combined with the structural floor argument it is a `HEURISTIC`
that m=3 IC cannot beat rho at any scale.

## What this rules out / does not rule out

- **Rules out** (at toy scale, measured): that the first-fall resistance map was hiding a cheap
  end-to-end IC — it was not; the end-to-end cost is above rho and the gap grows.
- **Does not rule out**: m=4 with a sub-D_reg crossbred decomposition (the §6.2(ii) door — the only
  place the linalg floor (n^{1/2}) does not by itself exceed rho); a non-Semaev relation source. The
  solve-gate should next be run at m=4 to confirm the decomposition ceiling there.

## Next

Run the m=4 solve-gate (S_5) to confirm the decomposition-ceiling side of the tradeoff; and (orthogonal)
push toy sizes higher with a faster decomposition to tighten the exponent.
