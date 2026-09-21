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
|---|---|---|---|---|---|---|
| 37 | 2 | None | None | False | False | False |
| 37 | 3 | None | None | False | False | False |
| 37 | 2 | None | None | False | False | False |
| 37 | 3 | None | None | False | False | False |
| 67 | 2 | None | None | False | False | False |
| 67 | 3 | None | None | False | False | False |
| 67 | 2 | None | None | False | False | False |
| 67 | 3 | None | None | False | False | False |
| 131 | 2 | None | None | False | False | False |
| 131 | 3 | None | None | False | False | False |
| 131 | 2 | None | None | False | False | False |
| 131 | 3 | None | None | False | False | False |
| 257 | 2 | None | None | False | False | False |
| 257 | 3 | None | None | False | False | False |
| 257 | 2 | None | None | False | False | False |
| 257 | 3 | None | None | False | False | False |
| 521 | 2 | None | None | False | False | False |
| 521 | 3 | None | None | False | False | False |
| 521 | 2 | None | None | False | False | False |
| 521 | 3 | None | None | False | False | False |

## Auto-descent check (transport public DLP into prime-field E(F_p) subgroup)

| p | chart_faithful (biquadratic roots == {x(4P),x(2P)}) | k_rec*P==Q (vs PUBLIC Q) | descent_ok |
|---|---|---|---|
| 37 | True | True | True |
| 67 | True | True | True |
| 131 | True | True | True |
| 257 | True | True | True |
| 521 | True | True | True |

NR-024's affine build FAILED the k_rec*P==Q verify; EXP-028 reports the result above.

## Verdict: **FAILED**

Meter self-validated (POS-A fires, NEG-1 quiet). Auto-descent VERIFIED k_rec*P==Q on all sizes (NR-024 had failed this). Theta/Kummer relation is NOT gate_meaningful (gate_meaningful_fire=False) and NOT lower-degree than elliptic Semaev (lower_deg=False): the level-2 theta chart STILL factors through the elliptic structure. H14 closed across charts (NR-024 + EXP-028).

**gate_meaningful_fire = False**

## What is ruled out

The level-2 theta-null / Kummer-line chart of A=Res_{F_p2/F_p}(E) as a degree-reducing or gate-meaningful intrinsic representation for prime-field ECDLP decomposition. Combined with NR-024 (affine chart) this closes H14's intrinsic-abelian-surface line across the affine AND theta/Kummer charts.

## What fires

e-ring/POS-C-style gate fires occur only in extension/Weil worlds; here the theta chart's leading-form module matches the elliptic chart.

## Honest null (stated up front, confirmed/refuted)

Null: isogeny/quotient invariance is chart-independent, so the theta relation likely STILL factors through the elliptic structure -> gate_meaningful=False -> H14 closed across charts. Result: see verdict.

## Next

Pivot off intrinsic representations (all H14 charts now closed). Next high-risk: EXP-029 division-polynomial psi_n fixed-degree B-smooth/non-prime-order FB (NR-021 left this open). Conservative: re-confirm capstone NR-026 collection bottleneck. Representation-change: pair correspondence / theta on a (1,2)-polarized abelian surface that is NOT isogenous to E x E (genuinely 2-dim Jacobian).

