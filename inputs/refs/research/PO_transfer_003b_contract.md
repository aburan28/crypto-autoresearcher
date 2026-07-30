# Experiment Contract: PO-transfer-003b Bielliptic One-Large-Prime Elimination

## Hypothesis

The split bielliptic interpolation source from `PO-transfer-003` can recover
most of the rank lost at larger fields by retaining relations with exactly one
residual point outside the factor base and eliminating repeated residual points
in a streaming one-large-prime table.

Status before execution: `HYPOTHESIS / UNTESTED / MODEL-BOUND`.

## Null Hypothesis

Large-prime collisions improve relation count but remain birthday-shaped,
consume at least `sqrt(n)` memory, produce dependent rows, or leave charged
cost above Pollard rho and the direct `PO-transfer-003` lane.

## Parameters

- field/curve family: exactly the four frozen `PO-transfer-003` cells;
- sizes: `p = 101, 211, 431, 4099`;
- seeds: `20260713..20260716`;
- factor base: exactly the deterministic public `PO-transfer-003` bases;
- relation shape: direct pushed `div(y-v(x))` rows plus rows obtained by
  eliminating one repeated canonical residual point;
- baseline: rho `0.886*sqrt(#E1)`, direct `PO-transfer-003`, and recovering
  `PO-transfer-002` cost `178.04x` rho.

## Model Of Computation

For partial rows

```text
A + s_A*L = O
B + s_B*L = O
```

with the same canonical large prime `L` and signs `s_A,s_B in {-1,1}`, emit

```text
s_B*A - s_A*B = O.
```

Only one anchor row per large-prime key is retained.  Every interpolation,
partial verification, collision, matrix entry, and retained anchor is charged.
Target and factor-base logs remain verifier-only.

## Metrics

- direct, partial, collided, zero, and target relation counts;
- unique large-prime buckets and collision count;
- matrix rank and target recovery;
- relation-kernel attempts and rank per 1000 attempts;
- charged lower-bound operations / rho;
- memory entries / `sqrt(n)`;
- improvement or regression against the direct lane;
- field-operation proxy and wall-clock time.

## Positive Control

Every eliminated row must verify publicly on `E1`, and every retained row must
pass the hidden-log verifier after collection.

## Negative Control

Large-prime keys include canonical point orientation.  Combining rows with a
mismatched point or without the sign correction must fail public verification;
the implementation does not retain such rows.

## Success Criterion

Structural success requires full rank and target recovery on the `F_4099`
anchor, plus either at least `2x` more rank per attempt or at least `16x` more
target relations than direct `PO-transfer-003`, with memory below `4*sqrt(n)`.

Algorithmic success still requires charged cost below `1.0x` rho on one size
and a non-increasing credible trend over the sweep.  A relation-count win alone
is not an ECDLP improvement.

## Falsification Criterion

The one-large-prime lane is narrowed if it fails to recover the `F_4099`
target, if rank and relation-yield gains miss the structural thresholds, if
memory exceeds `4*sqrt(n)`, or if charged cost remains above both rho and the
direct lane.

This does not rule out double-large-prime graph cycles, batch resultants,
non-quadratic split correspondences, or other native function families.

## Reproduction Command

```bash
mkdir -p /private/tmp/codex-sage-home
HOME=/private/tmp/codex-sage-home sage experiments/ecdlp_isogeny/po_transfer_003_bielliptic_norm_interpolation.sage \
  --large-prime --out experiments/ecdlp_isogeny/po_transfer_003b_result.json
```
