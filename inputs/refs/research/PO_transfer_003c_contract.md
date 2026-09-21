# Experiment Contract: PO-transfer-003c Streaming Rank-Basis Transfer

## Hypothesis

Pair-and-delete large-prime elimination plus an online public rank basis removes
the memory and overcollection failures of `PO-transfer-003b` while preserving
full target recovery on the `F_4099` anchor.

Status before execution: `HYPOTHESIS / UNTESTED / MODEL-BOUND`.

## Null Hypothesis

Streaming reduces stored rows but the interpolation attempts needed for full
rank remain far above rho, or deleting large-prime anchors destroys the
collision rate before target recovery.

## Parameters

- same four curves, targets, seeds, factor bases, and cubic relation kernel as
  `PO-transfer-003b`;
- one unmatched partial per canonical large-prime key;
- delete both partials after each collision;
- retain a final row only if it increases public matrix rank;
- stop collection as soon as the full-rank solution satisfies `kG=Q`.

## Metrics

- attempts at first public target recovery;
- online rank tests and retained rank-basis rows;
- peak unmatched large-prime anchor entries;
- public row replay and wrong-sign negative control;
- charged optimistic accounting floor / rho;
- peak memory entries / `sqrt(n)`;
- comparison against direct `003`, retaining-all `003b`, BSGS, and rho.

## Positive Control

The final retained basis must have full rank and recover a scalar satisfying
`kG=Q`; every row and every large-prime cancellation must replay publicly.

## Negative Control

The first wrong-sign large-prime combination must be nonzero, and no row that
fails public replay may enter the rank basis.

## Success Criterion

Structural success requires target recovery on all four cells, including
`F_4099`, with at most `4*sqrt(n)` peak memory on the anchor and fewer charged
operations than `PO-transfer-003b`.

Algorithmic success still requires a cell below `1.0x` rho and a credible
non-increasing exponent trend.  Streaming success alone is not an ECDLP break.

## Falsification Criterion

The streaming lane is narrowed if the anchor misses recovery, exceeds
`4*sqrt(n)` peak memory, or remains above rho after early stopping.  That result
does not rule out batch-resultant sieves, double-large-prime graph cycles, or
non-quadratic correspondences.

## Reproduction Command

```bash
mkdir -p /private/tmp/codex-sage-home
HOME=/private/tmp/codex-sage-home sage experiments/ecdlp_isogeny/po_transfer_003_bielliptic_norm_interpolation.sage \
  --stream-rank --out experiments/ecdlp_isogeny/po_transfer_003c_result.json
```

