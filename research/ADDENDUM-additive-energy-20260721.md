# Addendum: additive energy of natural factor bases (2026-07-21)

Extends SYNTHESIS-PRIME-FIELD-BARRIER-20260721.md with a sharper test of the
core obstruction claim ("an efficiently-describable factor base has additive
group statistics indistinguishable from random").

## New measurement (novel vs. the campaign's degree-3 richness)
The campaign's EV-INCB-001 measured 3-rich lines (collinear triples), a
degree-3 additive statistic, and found no excess. This addendum measures the
**additive energy** E(A) = #{(i,j,k,l): P_i+P_j = P_k+P_l}, the degree-4 sumset
statistic that is the standard, strictly more sensitive detector of hidden
additive structure. It is computed by pure group arithmetic (no discrete logs,
no Sage).

## Result (confound-controlled)
Natural base = B smallest-x on-curve points; control = random full-curve points
(SAME ambient group -- an earlier run comparing against random subgroup
multiples was confounded, since additive energy scales as ~B^4/N and the
subgroup control sat in a smaller N). Matched-group ratio E_natural / E_random:

| bits | #E | B | ratio |
|---|---|---|---|
| 12 | 2377 | 40 | 0.92 |
| 14 | 14680 | 40 | 1.01 |
| 16 | 55564 | 40 | 0.99 |
| 18 | 252276 | 40 | 1.00 |

Ratio ~= 1.0 at every size: no additive-energy excess.

## Interpretation
The natural factor base carries no exploitable additive structure even under the
degree-4 statistic, corroborating EV-INCB-001 at higher sensitivity and further
tightening the obstruction: the map x-coordinate -> discrete log destroys
additive structure, so efficiently-describable bases cannot supply the
super-linear relation source an exponent win requires. Toy scale, generic
curves, expected-negative -- a barrier confirmation, not a breakthrough
(AGENTS rules 5-7). Reproducible deterministically (seed=3; control tag 9999).
