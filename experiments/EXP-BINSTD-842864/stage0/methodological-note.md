# Methodological note — EXP-BINSTD-842864

## Forbidden reuse

Do **not** import or call `analysis/couveignes-lercier-131/weil_census.py`.

That numerical enumerator has a known gap (211 vs 215 at g=3; shortfall grows
at g=4). Reusing it would make any filtered zero an incomplete-instrument
artifact rather than an enumeration certificate.

## Instrument used

`experiments/EXP-BINSTD-842864/implementation/exact_targets_g56.py`:

- Rolle-pruned depth-first search over integer coefficient vectors
- Exact real-rootedness via rational Sturm sequences with square-free handling
- Boundary factor `x^2 - 8` stripped; brackets around `±2√2` match `exact_targets.py`
- Sympy `count_roots` used only for independent hit re-verification / dual-box samples

## Certificate vocabulary

Structural census runs set `certificate.kind: none` (closed set:
`discrete_log | decomposition | key_recovery | none`).

## Claim guards

- Do not upgrade `a_r >= 0` to "is a Jacobian" (necessary, not sufficient).
- Do not claim outcome A if unfiltered counts mismatch LMFDB or `ambiguous > 0`.
- Timeout / OOM → `failed_infrastructure`, never outcome A / exclusion.
- No break, factor-base, or rho-competitiveness claim.
