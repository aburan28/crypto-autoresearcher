# Fiber obligation

`blocked_by: O1/CompleteBasisAtEndpoint`, then O2/`EdgeLabel` and `RingPotential`. No endpoint-fiber theorem is claimed for CEFC-I.

Required quantified target after those definitions exist: for every valid `pp`, every valid generated `(E,W_E)`, and every pair of supported honest walks `w,w'` from `E` to the same canonically encoded endpoint `C`, the sums `sum_{e in w} EdgeLabel(pp,e)` and `sum_{e in w'} EdgeLabel(pp,e)` are identical in the declared group and equal `RingPotential(pp,E,W_E,C)-RingPotential(pp,E,W_E,E)`. Equality must include edge multiplicity, parallel edges, dual relations and canonical automorphism identifications. The proof must then imply `Dec(sk,Enc(pk,m;coins))=m` for every allowed `m` and supported coins, except a quantified failure event under the real law.

The algebraic suborder certificate does not define such a label, sum, potential or PKE. A public coboundary satisfies the formal sum identity but does not establish recipient asymmetry. A path-dependent hash can assign distinct sums to same-endpoint walks. No collision or circulation check was run.
