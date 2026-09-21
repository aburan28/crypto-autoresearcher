# Execution report -- RUN-RELN-f202be-N14

Stage: curve enumeration (direct, point arithmetic) + spectral cross-check, rung 14.
Wall clock: 56.1s. Curves: [17, 24, 67].

## Per-curve summary
### seed 17 (N=16477, B1_even=48, B2=17)
- x_interval_low_B1: Delta_reduced=0.9026, forced_gap=1.276 (expected 1.411), INV1_ok=True, INV2_ok=True
- x_interval_low_B2: Delta_reduced=0.9815, forced_gap=1.121 (expected 1.279), INV1_ok=True, INV2_ok=True
- x_interval_mid_B1: Delta_reduced=0.9581, forced_gap=1.336 (expected 1.411), INV1_ok=True, INV2_ok=True
- x_interval_mid_B2: Delta_reduced=0.9406, forced_gap=1.127 (expected 1.279), INV1_ok=True, INV2_ok=True
- qr_class_B1: Delta_reduced=0.9774, forced_gap=1.311 (expected 1.411), INV1_ok=True, INV2_ok=True
- qr_class_B2: Delta_reduced=0.9775, forced_gap=1.122 (expected 1.279), INV1_ok=True, INV2_ok=True
- NULL_A B1: band_reduced mean=0.98187 sd=0.07681 (n=100)
- NULL_A B2: band_reduced mean=0.99341 sd=0.05784 (n=100)
- NULL_B_points B1: band mean=0.98762 sd=0.03288
- NULL_B_points B2: band mean=1.00055 sd=0.02943
- ZN_interval/E small-multiples mirror bit-identical: True
- Bose-Chowla E mirror: {'mirror_bit_identical': True, 'E3': 969}
- NULL_B_ZN E-mirror B1: band mean=0.99428 sd=0.03403 sampled_mismatches=0
- NULL_B_ZN E-mirror B2: band mean=0.99983 sd=0.02888 sampled_mismatches=0
### seed 24 (N=16273, B1_even=48, B2=17)
- x_interval_low_B1: Delta_reduced=0.9236, forced_gap=1.297 (expected 1.411), INV1_ok=True, INV2_ok=True
- x_interval_low_B2: Delta_reduced=0.9767, forced_gap=1.122 (expected 1.279), INV1_ok=True, INV2_ok=True
- x_interval_mid_B1: Delta_reduced=0.9793, forced_gap=1.294 (expected 1.411), INV1_ok=True, INV2_ok=True
- x_interval_mid_B2: Delta_reduced=0.9890, forced_gap=1.120 (expected 1.279), INV1_ok=True, INV2_ok=True
- qr_class_B1: Delta_reduced=0.8377, forced_gap=1.244 (expected 1.411), INV1_ok=True, INV2_ok=True
- qr_class_B2: Delta_reduced=1.0421, forced_gap=1.112 (expected 1.279), INV1_ok=True, INV2_ok=True
- NULL_A B1: band_reduced mean=0.99532 sd=0.08694 (n=100)
- NULL_A B2: band_reduced mean=0.99186 sd=0.06053 (n=100)
- NULL_B_points B1: band mean=0.99051 sd=0.03101
- NULL_B_points B2: band mean=0.99835 sd=0.02698
- ZN_interval/E small-multiples mirror bit-identical: True
- Bose-Chowla E mirror: {'mirror_bit_identical': True, 'E3': 969}
- NULL_B_ZN E-mirror B1: band mean=0.98719 sd=0.03146 sampled_mismatches=0
- NULL_B_ZN E-mirror B2: band mean=1.00002 sd=0.03114 sampled_mismatches=0
### seed 67 (N=16699, B1_even=48, B2=17)
- x_interval_low_B1: Delta_reduced=0.9111, forced_gap=1.277 (expected 1.411), INV1_ok=True, INV2_ok=True
- x_interval_low_B2: Delta_reduced=0.9414, forced_gap=1.127 (expected 1.279), INV1_ok=True, INV2_ok=True
- x_interval_mid_B1: Delta_reduced=0.9729, forced_gap=1.337 (expected 1.411), INV1_ok=True, INV2_ok=True
- x_interval_mid_B2: Delta_reduced=0.9864, forced_gap=1.121 (expected 1.279), INV1_ok=True, INV2_ok=True
- qr_class_B1: Delta_reduced=1.0246, forced_gap=1.368 (expected 1.411), INV1_ok=True, INV2_ok=True
- qr_class_B2: Delta_reduced=1.0437, forced_gap=1.113 (expected 1.279), INV1_ok=True, INV2_ok=True
- NULL_A B1: band_reduced mean=0.98334 sd=0.08782 (n=100)
- NULL_A B2: band_reduced mean=1.00454 sd=0.07322 (n=100)
- NULL_B_points B1: band mean=0.99788 sd=0.03704
- NULL_B_points B2: band mean=0.99756 sd=0.02741
- ZN_interval/E small-multiples mirror bit-identical: True
- Bose-Chowla E mirror: {'mirror_bit_identical': True, 'E3': 969}
- NULL_B_ZN E-mirror B1: band mean=0.99194 sd=0.03071 sampled_mismatches=0
- NULL_B_ZN E-mirror B2: band mean=0.99634 sd=0.02411 sampled_mismatches=0

## Accounting rows: 18 (all INV1_ok/INV2_ok/forced_gap_within_0.1 True; see accounting.json)
All accounting checks pass: False
