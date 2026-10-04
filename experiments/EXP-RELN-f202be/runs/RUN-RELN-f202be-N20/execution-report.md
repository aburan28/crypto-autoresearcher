# Execution report -- RUN-RELN-f202be-N20

Stage: curve enumeration (direct, point arithmetic) + spectral cross-check, rung 20.
Wall clock: 5072.7s. Curves: [21, 51, 80].

## Per-curve summary
### seed 21 (N=1053539, B1_even=186, B2=67)
- x_interval_low_B1: Delta_reduced=0.9766, forced_gap=1.448 (expected 1.476), INV1_ok=True, INV2_ok=True
- x_interval_low_B2: Delta_reduced=1.0135, forced_gap=1.399 (expected 1.436), INV1_ok=True, INV2_ok=True
- x_interval_mid_B1: Delta_reduced=0.9823, forced_gap=1.445 (expected 1.476), INV1_ok=True, INV2_ok=True
- x_interval_mid_B2: Delta_reduced=1.0033, forced_gap=1.389 (expected 1.436), INV1_ok=True, INV2_ok=True
- qr_class_B1: Delta_reduced=0.9990, forced_gap=1.452 (expected 1.476), INV1_ok=True, INV2_ok=True
- qr_class_B2: Delta_reduced=1.0084, forced_gap=1.397 (expected 1.436), INV1_ok=True, INV2_ok=True
- NULL_A B1: band_reduced mean=0.99845 sd=0.01048 (n=100)
- NULL_A B2: band_reduced mean=0.99923 sd=0.01171 (n=100)
- NULL_B_points B1: band mean=0.99934 sd=0.00440
- NULL_B_points B2: band mean=0.99951 sd=0.00438
- ZN_interval/E small-multiples mirror bit-identical: True
- Bose-Chowla E mirror: {'mirror_bit_identical': True, 'E3': 52394}
- NULL_B_ZN E-mirror B1: band mean=0.99916 sd=0.00426 sampled_mismatches=0
- NULL_B_ZN E-mirror B2: band mean=0.99937 sd=0.00377 sampled_mismatches=0
### seed 51 (N=1056173, B1_even=186, B2=67)
- x_interval_low_B1: Delta_reduced=1.0037, forced_gap=1.452 (expected 1.476), INV1_ok=True, INV2_ok=True
- x_interval_low_B2: Delta_reduced=1.0083, forced_gap=1.399 (expected 1.436), INV1_ok=True, INV2_ok=True
- x_interval_mid_B1: Delta_reduced=0.9973, forced_gap=1.463 (expected 1.476), INV1_ok=True, INV2_ok=True
- x_interval_mid_B2: Delta_reduced=1.0009, forced_gap=1.389 (expected 1.436), INV1_ok=True, INV2_ok=True
- qr_class_B1: Delta_reduced=0.9991, forced_gap=1.464 (expected 1.476), INV1_ok=True, INV2_ok=True
- qr_class_B2: Delta_reduced=0.9954, forced_gap=1.390 (expected 1.436), INV1_ok=True, INV2_ok=True
- NULL_A B1: band_reduced mean=0.99940 sd=0.01023 (n=100)
- NULL_A B2: band_reduced mean=1.00121 sd=0.01023 (n=100)
- NULL_B_points B1: band mean=0.99987 sd=0.00425
- NULL_B_points B2: band mean=0.99963 sd=0.00393
- ZN_interval/E small-multiples mirror bit-identical: True
- Bose-Chowla E mirror: {'mirror_bit_identical': True, 'E3': 52394}
- NULL_B_ZN E-mirror B1: band mean=0.99945 sd=0.00417 sampled_mismatches=0
- NULL_B_ZN E-mirror B2: band mean=0.99974 sd=0.00426 sampled_mismatches=0
### seed 80 (N=1055783, B1_even=186, B2=67)
- x_interval_low_B1: Delta_reduced=1.0144, forced_gap=1.467 (expected 1.476), INV1_ok=True, INV2_ok=True
- x_interval_low_B2: Delta_reduced=0.9996, forced_gap=1.399 (expected 1.436), INV1_ok=True, INV2_ok=True
- x_interval_mid_B1: Delta_reduced=0.9930, forced_gap=1.457 (expected 1.476), INV1_ok=True, INV2_ok=True
- x_interval_mid_B2: Delta_reduced=1.0051, forced_gap=1.399 (expected 1.436), INV1_ok=True, INV2_ok=True
- qr_class_B1: Delta_reduced=0.9854, forced_gap=1.452 (expected 1.476), INV1_ok=True, INV2_ok=True
- qr_class_B2: Delta_reduced=0.9904, forced_gap=1.390 (expected 1.436), INV1_ok=True, INV2_ok=True
- NULL_A B1: band_reduced mean=0.99990 sd=0.01198 (n=100)
- NULL_A B2: band_reduced mean=1.00036 sd=0.01024 (n=100)
- NULL_B_points B1: band mean=1.00007 sd=0.00409
- NULL_B_points B2: band mean=0.99920 sd=0.00317
- ZN_interval/E small-multiples mirror bit-identical: True
- Bose-Chowla E mirror: {'mirror_bit_identical': True, 'E3': 52394}
- NULL_B_ZN E-mirror B1: band mean=0.99925 sd=0.00412 sampled_mismatches=0
- NULL_B_ZN E-mirror B2: band mean=0.99902 sd=0.00426 sampled_mismatches=0

## Accounting rows: 18 (all INV1_ok/INV2_ok/forced_gap_within_0.1 True; see accounting.json)
All accounting checks pass: True
