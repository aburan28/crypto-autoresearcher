# Methodological note — EXP-BINSTD-5d3ec0 Stage 0

Experiment: `EXP-BINSTD-5d3ec0` / task `TASK-20261001-eaf0c5` /
hypothesis `H-BINSTD-4a07ff` (source `IDEA-20260926-b48c9d`).

## What Stage 0 freezes

1. **Product-law table at n=131** for w in {1,2,3,5,8,10,13,15}:
   `|Gamma_w| <= C(131,w)*2^w`, `attempts_free = 2^131/|Gamma_w|`.
   Re-derived `|Gamma_13|` upper log2 = 71.0109
   (prediction 71.0 ± 0.5:
   True);
   attempts_w13 log2 = 59.9891
   (prediction 60.0 ± 0.5:
   True).

2. **n=19 order check**: measured order 523492
   (expected 4*130873=523492, match=True);
   130873 prime=True; unique 2-torsion (0,1)=True;
   2-Sylow cyclic Z/4=True.
   DO-4 stop would fire if order mismatched.

3. **Preregistered Stage-1/2 bands** written in
   `preregistered-predictions.yaml` **before** any Stage-1 run manifest.

4. **w=1 baseline row**: `|Gamma_1|` upper = 262 at n=131 (exact 2n),
   orbit-union gain exactly n on relations (KN-FIND-47da4e /
   frobenius-orbit README) — reproduced as arithmetic identity, not an
   attack measurement.

## Certificate vocabulary

- Stage-0 / metric-only: `certificate.kind: none`
- DLP solutions: `discrete_log` + independent `[x]P=Q` re-check
- Relation hits (P,z): `decomposition` + re-verify `Q=[z]P` with `x(P) in V'`

## Explicit non-claims

- No deployed-curve attack.
- No claim that the mechanism beats matched Pollard rho.
- No exponent improvement from the tau-adic object.
- No extrapolation of Stage-2 ratios to n=131.
- Amazon Bedrock not used. No AUXIN edits.

## Measured vs modeled

Stage-0 `|Gamma_w|` / attempts columns are **MODELED arithmetic** (upper
bounds). n=19 order is **MEASURED**. Stage-1 scalar-multiplication costs and
Stage-2 closure work will be **MEASURED**; comparison bands above are
**MODELED** and frozen here.
