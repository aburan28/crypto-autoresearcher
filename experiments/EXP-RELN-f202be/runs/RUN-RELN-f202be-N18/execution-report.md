# Execution report -- RUN-RELN-f202be-N18

Stage: curve enumeration (direct, point arithmetic) + spectral cross-check, rung 18.
Wall clock: 1147.7s. Curves: [64, 90, 104].

## Per-curve summary
### seed 64 (N=264529, B1_even=118, B2=43)
- x_interval_low_B1: Delta_reduced=1.0125, forced_gap=1.451 (expected 1.463), INV1_ok=True, INV2_ok=True
- x_interval_low_B2: Delta_reduced=1.0085, forced_gap=1.332 (expected 1.403), INV1_ok=True, INV2_ok=True
- x_interval_mid_B1: Delta_reduced=1.0009, forced_gap=1.430 (expected 1.463), INV1_ok=True, INV2_ok=True
- x_interval_mid_B2: Delta_reduced=0.9938, forced_gap=1.332 (expected 1.403), INV1_ok=True, INV2_ok=True
- qr_class_B1: Delta_reduced=0.9882, forced_gap=1.429 (expected 1.463), INV1_ok=True, INV2_ok=True
- qr_class_B2: Delta_reduced=1.0045, forced_gap=1.332 (expected 1.403), INV1_ok=True, INV2_ok=True
- NULL_A B1: band_reduced mean=0.99787 sd=0.01978 (n=100)
- NULL_A B2: band_reduced mean=1.00157 sd=0.02269 (n=100)
- NULL_B_points B1: band mean=0.99769 sd=0.00858
- NULL_B_points B2: band mean=0.99977 sd=0.00654
- ZN_interval/E small-multiples mirror bit-identical: True
- Bose-Chowla E mirror: {'mirror_bit_identical': True, 'E3': 14190}
- NULL_B_ZN E-mirror B1: band mean=0.99869 sd=0.00925 sampled_mismatches=0
- NULL_B_ZN E-mirror B2: band mean=0.99870 sd=0.00708 sampled_mismatches=0
### seed 90 (N=262877, B1_even=118, B2=43)
- x_interval_low_B1: Delta_reduced=0.9734, forced_gap=1.428 (expected 1.463), INV1_ok=True, INV2_ok=True
- x_interval_low_B2: Delta_reduced=0.9800, forced_gap=1.333 (expected 1.403), INV1_ok=True, INV2_ok=True
- x_interval_mid_B1: Delta_reduced=0.9780, forced_gap=1.429 (expected 1.463), INV1_ok=True, INV2_ok=True
- x_interval_mid_B2: Delta_reduced=0.9870, forced_gap=1.333 (expected 1.403), INV1_ok=True, INV2_ok=True
- qr_class_B1: Delta_reduced=0.9745, forced_gap=1.411 (expected 1.463), INV1_ok=True, INV2_ok=True
- qr_class_B2: Delta_reduced=0.9991, forced_gap=1.332 (expected 1.403), INV1_ok=True, INV2_ok=True
- NULL_A B1: band_reduced mean=0.99606 sd=0.02220 (n=100)
- NULL_A B2: band_reduced mean=1.00139 sd=0.02236 (n=100)
- NULL_B_points B1: band mean=0.99729 sd=0.00837
- NULL_B_points B2: band mean=1.00020 sd=0.00879
- ZN_interval/E small-multiples mirror bit-identical: True
- Bose-Chowla E mirror: {'mirror_bit_identical': True, 'E3': 14190}
- NULL_B_ZN E-mirror B1: band mean=0.99903 sd=0.00692 sampled_mismatches=0
- NULL_B_ZN E-mirror B2: band mean=0.99923 sd=0.00710 sampled_mismatches=0
### seed 104 (N=264757, B1_even=118, B2=43)
- x_interval_low_B1: Delta_reduced=1.0162, forced_gap=1.444 (expected 1.463), INV1_ok=True, INV2_ok=True
- x_interval_low_B2: Delta_reduced=0.9992, forced_gap=1.332 (expected 1.403), INV1_ok=True, INV2_ok=True
- x_interval_mid_B1: Delta_reduced=1.0490, forced_gap=1.452 (expected 1.463), INV1_ok=True, INV2_ok=True
- x_interval_mid_B2: Delta_reduced=1.0113, forced_gap=1.331 (expected 1.403), INV1_ok=True, INV2_ok=True
- qr_class_B1: Delta_reduced=0.9613, forced_gap=1.410 (expected 1.463), INV1_ok=True, INV2_ok=True
- qr_class_B2: Delta_reduced=0.9812, forced_gap=1.333 (expected 1.403), INV1_ok=True, INV2_ok=True
- NULL_A B1: band_reduced mean=0.99603 sd=0.02060 (n=100)
- NULL_A B2: band_reduced mean=1.00101 sd=0.01910 (n=100)
- NULL_B_points B1: band mean=0.99775 sd=0.00882
- NULL_B_points B2: band mean=0.99987 sd=0.00771
- ZN_interval/E small-multiples mirror bit-identical: True
- Bose-Chowla E mirror: {'mirror_bit_identical': True, 'E3': 14190}
- NULL_B_ZN E-mirror B1: band mean=0.99855 sd=0.00943 sampled_mismatches=0
- NULL_B_ZN E-mirror B2: band mean=0.99841 sd=0.00713 sampled_mismatches=0

## Accounting rows: 18 (all INV1_ok/INV2_ok/forced_gap_within_0.1 True; see accounting.json)
All accounting checks pass: True
