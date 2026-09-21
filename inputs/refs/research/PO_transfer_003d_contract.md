# Experiment Contract Amendment: PO-transfer-003d Bounded-Anchor Sweep

## Provenance Warning

This was an exploratory amendment to `PO-transfer-003c`, not a fully
pre-registered experiment.  Anchor caps `4, 8, 12, 9, 10, 11` were tested on
the `F_4099` anchor before freezing cap `9` for the four-cell sweep.  The cap-9
anchor result is therefore selection evidence, not held-out confirmation.

Status: `HYPOTHESIS / EXPLORATORY / MODEL-BOUND / TOY-EVIDENCE`.

## Hypothesis

A bounded pair-and-delete cache can preserve full target recovery while keeping
peak attack memory below `4*sqrt(n)` on the `F_4099` anchor.

## Null Hypothesis

The cache either misses full rank, exceeds the memory gate, or pays enough
extra interpolation attempts that it remains above rho and stronger baselines.

## Parameters

- inherited curves, targets, seeds, factor bases, relation kernel, public
  online rank basis, and controls from `PO-transfer-003c`;
- exploratory anchor caps: `4, 8, 9, 10, 11, 12`;
- frozen sweep cap after exploration: `9` unmatched large-prime rows;
- cap eviction: insertion-order eviction before a new unmatched key is stored;
- baseline: rho, BSGS, `PO-transfer-002`, direct `003`, retaining `003b`, and
  unbounded streaming `003c`.

## Metrics

- full rank and public `kG=Q` recovery;
- kernel attempts, online rank tests, and cache evictions;
- peak sparse entries and ratio to `sqrt(n)`;
- public row replay and wrong-sign negative control;
- optimistic charged accounting floor / rho;
- four-cell attempts-per-rank fit, labeled as toy evidence only.

## Positive Control

Every retained row replays on the public curve; a full-rank solution must
satisfy `kG=Q`.

## Negative Control

The first wrong-sign large-prime combination must be nonzero.  Public
verification failures must remain zero.

## Success Criterion

Structural success on the selected anchor requires full rank, target recovery,
and peak memory below `4*sqrt(n)`.

Algorithmic success requires charged cost below rho on at least one cell and a
credible non-increasing trend.  The selected-anchor structural gate alone is
not sufficient.

## Falsification Criterion

The bounded-cache mechanism is baseline-lost if recovery requires an
attempts-per-rank trend above `n^0.5` or every recovering cell remains above
rho.  This narrows only insertion-order bounded caches for this bielliptic
cubic sampler.

## Reproduction Commands

```bash
HOME=/private/tmp/codex-sage-home sage experiments/ecdlp_isogeny/po_transfer_003_bielliptic_norm_interpolation.sage \
  --stream-rank --anchor-cap 9 \
  --out experiments/ecdlp_isogeny/po_transfer_003d_result.json
```

The exploratory cap artifacts are `po_transfer_003d_cap{4,8,9,10,11,12}_result.json`.

