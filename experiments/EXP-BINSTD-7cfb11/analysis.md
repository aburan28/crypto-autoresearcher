## Observation

EXP-BINSTD-7cfb11 Stage 1 measured toy n=17 GF(2) matrices with frozen |FB|=24, row weight 4, and beta frozen at 16. Four relation surpluses completed. On each relation cell the bits route and the sets route report the same nnz_after and nnz_initial. The relation fill-in ratios F = nnz_after/nnz_initial are 44/96 = 11/24 at surplus 1.0, 46/120 = 23/60 at surplus 1.25, 46/144 = 23/72 at surplus 1.5, and 46/192 = 23/96 at surplus 2.0. Each ratio is at most 16. Stage 0 raw outcome is O-STAGE0-OK. Stage 1 raw outcome is O-SUPPORT, and RESULTS.md names O-SUPPORT. A temp-directory Stage 1 replay returned O-SUPPORT with the same four relation ratios. This is a toy sparse-matrix fill-in measurement. It states no exponent and no n>=131 result.

## Comparison

The bits route and the sets route agree on every relation cell. The er_null cells are a same-shape comparison; their ratios are not the claimed band. Beta stays the value frozen in stage0/preregistered-predictions.json. Beta=16 is loose against the measured relation ratios: the largest relation F is 44/96 = 11/24, which is below 0.5, and the other three relation ratios are smaller. That looseness does not change the O-SUPPORT label, which asks only whether each completed relation F is at most 16.

## Inference

The pre-registered conjunction holds on this package: the two routes agree, four surpluses completed (at least three were required), and every completed relation F is at most 16. The label reads those relation cells. Direction supports H-BINSTD-480fb5 inside that toy boundary. One package is not a replication. The dual meter is an internal control inside the same package, not a second experiment.

## Limitation

Scope is toy n=17 synthetic sparsity only. Beta=16 is loose relative to measured F below 0.5. The package does not solve a discrete logarithm, does not move an exponent, and carries certificate.kind none. A single unreplicated package does not make the band a durable attack boundary, and it does not authorize Stage 2 at n in {23, 31}. code.dirty is true on both manifests and is reconciled by a present dirty note plus SHA-256 agreement on the five committed implementation files.
