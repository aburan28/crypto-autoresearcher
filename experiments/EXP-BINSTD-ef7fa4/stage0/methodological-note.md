# Methodological note — EXP-BINSTD-ef7fa4 Stage 0
# Written before Stage 1. Observations / protocol only. No claim of break,
# rho competitiveness, or exponent improvement.

## Purpose

Freeze product-space dimension tables and spurious-lift predictions for
`H-BINSTD-770ec3` / `HEUR-BINSTD-770ec3-H1` before any scientific census run.

## Formulae (frozen)

- `dim V^{(k)} = min(k(l-1)+1, n)` for the polynomial-basis coordinate
  subspace `V = span{1, z, …, z^{l-1}}` (before reduction; reduction cannot
  raise dimension).
- Heuristic spurious factor:
  `m! · 2^{∑_k dim V^{(k)} − m·l}` at RC-1 with `m=3`.
- Contract-stated comparison band (do not retune):
  `2^{9.6}`, `2^{13.6}`, `2^{17.6}` at `l ∈ {4,5,6}`.
- Exact arithmetic from Stage-0 dims (MODELED, disclosed, not a retune):
  `≈ 2^{11.585}`, `2^{14.585}`, `2^{17.585}`.

## Stage order

1. **Stage 0** (this packet): n=131 table, RC-1 table, predictions,
   methodological note, subfield proves-too-much row.
2. **Stage 1**: RC-1 symmetrised `S_4` e-space census with lift-by-factoring;
   exhaustive at `l∈{4,5}`; sampled/`≥2^{24}` or closure lower bound at `l=6`.
3. **Stage 2**: size-matched random-subspace null (P3).
4. **Stage 3**: Koblitz n=17 Frobenius-arm null vs ordinary RC-1 null (P4).

## Certificate vocabulary

- Stage-0 / metric-only manifests: `certificate.kind: none`.
- Lift-recovered genuine decompositions: `certificate.kind: decomposition`,
  independently re-checked (roots in V + sum-to-target on a fresh curve).

## Controls

- Exact `V^m` enumeration as ground truth for genuine count.
- Lift-by-factoring distinguisher for spurious e-solutions.
- Random subspace (predicted worse / larger spurious factor).
- Subfield symbolic row (proves-too-much).
- Ordinary RC-1 unrelated targets as Frobenius-arm null.

## Non-claims

This experiment does **not** claim:

- a deployed-curve attack;
- that symmetrisation beats matched rho;
- an exponent improvement from symmetrisation on subspace bases.

Timeouts/crashes are `failed_infrastructure`, never negative mathematical
evidence. Predictions are not retuned after Stage 1+ without a protocol
amendment.

## Provenance note

Huang–Petit–Shinohara–Takagi 2013 product-space form remains **recalled**
(not retrieved) per the frozen hypothesis; n=131 saturation numbers are
hand arithmetic of the packet.
