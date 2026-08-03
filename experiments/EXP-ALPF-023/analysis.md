# Analysis — Autolab prime-field: round012_exp028_theta_kummer_surface

## Observation
failed

Source excerpt / raw summary:

```
# EXP-028 -- theta / level-2 Kummer-quartic chart of A = Res_{F_p2/F_p}(E)

**The last un-probed H14 intrinsic representation** (round-10 high-risk direction).

## Model used

level-2 theta-null / Kummer-line model K=E/{+-1}~=P^1 over F_{p^2}, biquadratic (Montgomery/theta) pseudo-addition, Weil-restricted coordinatewise to F_p (Kummer of A=Res_{F_p2/F_p}(E))

Declared: we use the **level-2 theta-null / Kummer-line model** K = E/{+-1} ~= P^1 with the **biquadratic (Montgomery/theta) pseudo-addition** relation, Weil-restricted coordinatewise to F_p (this is the Kummer of the abelian surface A = Res_{F_p2/F_p}(E)). This is NOT the affine (x,y) chart of NR-024 and NOT the F_q x-line Semaev pullback. The full level-2 theta quartic-in-P^3 model was symbolically heavy; the Kummer-line biquadratic carries the same leading-form information for the gate test.

## Theta-relation degree vs elliptic 4^(m-1) Semaev law

| p | m | theta total deg | theta per-var | elliptic Semaev deg | 4^(m-1) ref | theta lower? |
|---|---|---|---|---|---|---|
| 37 | 2 | 4 | {'u': 2, 'v': 2, 'w': 2} | 4 (S_3) | 4 | False |
| 37 | 3 | F12=4 F3t=4 | chained biquadratic | S_4 deg-4/var | 16 | (chain) |
| 37 | 2 | 4 | {'u': 2, 'v': 2, 'w': 2} | 4 (S_3) | 4 | False |
| 37 | 3 | F12=4 F3t=4 | chained biquadratic | S_4 deg-4/var | 16 | (chain) |
| 67 | 2 | 4 | {'u': 2, 'v': 2, 'w': 2} | 4 (S_3) | 4 | False |
| 67 | 3 | F12=4 F3t=4 | chained biquadratic | S_4 deg-4/var | 16 | (chain) |
| 67 | 2 | 4 | {'u': 2, 'v': 2, 'w': 2} | 4 (S_3) | 4 | False |
| 67 | 3 | F12=4 F3t=4 | chained biquadratic | S_4 deg-4/var | 16 | (chain) |
| 131 | 2 | 4 | {'u': 2, 'v': 2, 'w': 2} | 4 (S_3) | 4 | False |
| 131 | 3 | F12=4 F3t=4 | chained biquadratic | S_4 deg-4/var | 16 | (chain) |
| 131 | 2 | 4 | {'u': 2, 'v': 2, 'w': 2} | 4 (S_3) | 4 | False |
| 131 | 3 | F12=4 F3t=4 | chained biquadratic | S_4 deg-4/var | 16 | (chain) |
| 257 | 2 | 4 | {'u': 2, 'v': 2, 'w': 2} | 4 (S_3) | 4 | False |
| 257 | 3 | F12=4 F3t=4 | chained biquadratic | S_4 deg-4/var | 16 | (chain) |
| 257 | 2 | 4 | {'u': 2, 'v': 2, 'w': 2} | 4 (S_3) | 4 | False |
| 257 | 3 | F12=4 F3t=4 | chained biquadratic | S_4 deg-4/var | 16 | (chain) |
| 521 | 2 | 4 | {'u': 2, 'v': 2, 'w': 2} | 4 (S_3) | 4 | False |
| 521 | 3 | F12=4 F3t=4 | chained biquadratic | S_4 deg-4/var | 16 | (chain) |
| 521 | 2 | 4 | {'u': 2, 'v': 2, 'w': 2} | 4 (S_3) | 4 | False |
| 521 | 3 | F12=4 F3t=4 | chained biquadratic | S_4 deg-4/var | 16 | (chain) |

## Gated-meter table  (meter_self_validated = True)

Inline self-validation: {"POS_A": ["3", "4", "True", "True", "True", "{'D': 3, 'nrows_full': 9, 'rank_full': 7, 'ker_full': 2, 'koszul_full': 0, 'nontriv_full': 2, 'n_sum_rows': 9, 'n_fb_rows': 0, 'nrows_fb': 0, 'rank_fb': 0, 'ker_fb': 0, 'koszul_fb': 0, 'nontriv_fb': 0, 'involves_sum_shrink': True, 'involves_sum_direct': True}"], "NEG_1": ["None", "4", "False", "False", "False", "None"], "posA_fires": true, "neg1_gate_meaningful": false}

| p | m | d_ff | D_reg | fires | gate_passes | gate_meaningful |
```

## Comparison
Compared against Autolab's stated baseline (typically Pollard rho / VW / Wesolowski-class
isogeny cost, depending on topic). This import does not recompute those baselines inside
crypto-autoresearcher.

## Inference
`OBSERVATION` / `TOY-EVIDENCE` (or Autolab's original label if stronger, still not upgraded):
the Autolab package is now citeable as `EXP`+`RUN` evidence under the harness. Scientific
content remains bounded by Autolab's original scope and caveats.

## Limitation
- Not independently re-executed in this repository.
- Certificates were not re-verified; do not promote discrete-log / decomposition claims.
- Claim tier remains `toy` unless a later harness experiment re-runs with certificates.
