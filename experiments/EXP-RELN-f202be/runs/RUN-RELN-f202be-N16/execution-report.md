# Execution report -- RUN-RELN-f202be-N16

Stage: curve enumeration (direct, point arithmetic) + spectral cross-check, rung 16.
Wall clock: 255.4s. Curves: [39, 62, 64].

## Per-curve summary
### seed 39 (N=65629, B1_even=74, B2=27)
- x_interval_low_B1: Delta_reduced=0.9231, forced_gap=1.346 (expected 1.441), INV1_ok=True, INV2_ok=True
- x_interval_low_B2: Delta_reduced=1.0237, forced_gap=1.283 (expected 1.352), INV1_ok=True, INV2_ok=True
- x_interval_mid_B1: Delta_reduced=0.9738, forced_gap=1.397 (expected 1.441), INV1_ok=True, INV2_ok=True
- x_interval_mid_B2: Delta_reduced=0.9496, forced_gap=1.249 (expected 1.352), INV1_ok=True, INV2_ok=True
- qr_class_B1: Delta_reduced=0.9666, forced_gap=1.378 (expected 1.441), INV1_ok=True, INV2_ok=True
- qr_class_B2: Delta_reduced=0.9681, forced_gap=1.247 (expected 1.352), INV1_ok=True, INV2_ok=True
- NULL_A B1: band_reduced mean=0.99804 sd=0.04541 (n=100)
- NULL_A B2: band_reduced mean=0.99962 sd=0.03918 (n=100)
- NULL_B_points B1: band mean=0.99499 sd=0.01677
- NULL_B_points B2: band mean=0.99720 sd=0.01357
- ZN_interval/E small-multiples mirror bit-identical: True
- Bose-Chowla E mirror: {'skipped': True, 'reason': 'bose_chowla_set only implemented for prime q; q=27 is a non-prime prime power (documented scope limit, see implementation.md)'}
- NULL_B_ZN E-mirror B1: band mean=0.99761 sd=0.01851 sampled_mismatches=0
- NULL_B_ZN E-mirror B2: band mean=0.99796 sd=0.01338 sampled_mismatches=0
### seed 62 (N=65701, B1_even=74, B2=27)
- x_interval_low_B1: Delta_reduced=1.0074, forced_gap=1.419 (expected 1.441), INV1_ok=True, INV2_ok=True
- x_interval_low_B2: Delta_reduced=0.9442, forced_gap=1.249 (expected 1.352), INV1_ok=True, INV2_ok=True
- x_interval_mid_B1: Delta_reduced=1.0000, forced_gap=1.394 (expected 1.441), INV1_ok=True, INV2_ok=True
- x_interval_mid_B2: Delta_reduced=0.9769, forced_gap=1.246 (expected 1.352), INV1_ok=True, INV2_ok=True
- qr_class_B1: Delta_reduced=0.9621, forced_gap=1.372 (expected 1.441), INV1_ok=True, INV2_ok=True
- qr_class_B2: Delta_reduced=0.9932, forced_gap=1.244 (expected 1.352), INV1_ok=True, INV2_ok=True
- NULL_A B1: band_reduced mean=0.99277 sd=0.03782 (n=100)
- NULL_A B2: band_reduced mean=1.00353 sd=0.03826 (n=100)
- NULL_B_points B1: band mean=0.99506 sd=0.01721
- NULL_B_points B2: band mean=0.99909 sd=0.01502
- ZN_interval/E small-multiples mirror bit-identical: True
- Bose-Chowla E mirror: {'skipped': True, 'reason': 'bose_chowla_set only implemented for prime q; q=27 is a non-prime prime power (documented scope limit, see implementation.md)'}
- NULL_B_ZN E-mirror B1: band mean=0.99581 sd=0.01572 sampled_mismatches=0
- NULL_B_ZN E-mirror B2: band mean=0.99955 sd=0.01499 sampled_mismatches=0
### seed 64 (N=66137, B1_even=74, B2=27)
- x_interval_low_B1: Delta_reduced=1.0590, forced_gap=1.426 (expected 1.441), INV1_ok=True, INV2_ok=True
- x_interval_low_B2: Delta_reduced=1.0111, forced_gap=1.243 (expected 1.352), INV1_ok=True, INV2_ok=True
- x_interval_mid_B1: Delta_reduced=0.9910, forced_gap=1.399 (expected 1.441), INV1_ok=True, INV2_ok=True
- x_interval_mid_B2: Delta_reduced=0.9631, forced_gap=1.247 (expected 1.352), INV1_ok=True, INV2_ok=True
- qr_class_B1: Delta_reduced=0.9185, forced_gap=1.364 (expected 1.441), INV1_ok=True, INV2_ok=True
- qr_class_B2: Delta_reduced=0.9773, forced_gap=1.246 (expected 1.352), INV1_ok=True, INV2_ok=True
- NULL_A B1: band_reduced mean=0.99477 sd=0.04239 (n=100)
- NULL_A B2: band_reduced mean=1.00442 sd=0.04360 (n=100)
- NULL_B_points B1: band mean=0.99809 sd=0.01679
- NULL_B_points B2: band mean=0.99860 sd=0.01383
- ZN_interval/E small-multiples mirror bit-identical: True
- Bose-Chowla E mirror: {'skipped': True, 'reason': 'bose_chowla_set only implemented for prime q; q=27 is a non-prime prime power (documented scope limit, see implementation.md)'}
- NULL_B_ZN E-mirror B1: band mean=0.99707 sd=0.01600 sampled_mismatches=0
- NULL_B_ZN E-mirror B2: band mean=0.99885 sd=0.01576 sampled_mismatches=0

## Accounting rows: 18 (all INV1_ok/INV2_ok/forced_gap_within_0.1 True; see accounting.json)
All accounting checks pass: False
