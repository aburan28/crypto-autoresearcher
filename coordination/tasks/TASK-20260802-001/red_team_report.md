# Red-team report — IDEA-20260801-021

id: `RT-20260802-001`  
task_id: `TASK-20260802-001`  
role: red-team  
verdict: `REVISE`

## Scope audited

The audit challenged the proposal's quantifiers, projective intersection
premise, entropy step, retry cost, and universal-claim boundary. It did not
change research status or edit producer artifacts.

## Findings

1. **Bezout:** conditional pass. The factor base must be exactly the rational
   affine zero locus `G intersect V(f_p)` for one polynomial whose projective
   homogenization has degree `d_p >= 1` and shares no component with the
   projective cubic. Arbitrary predicates, unions, inequalities, and multiple
   equations are not covered.
2. **Sumset cardinality:** pass. For the exact ordered `m_p`-fold addition map,
   including repetitions, `|m_p F_p| <= |F_p|^m_p` is immediate.
3. **Entropy:** conditional pass. A uniform constant `C` in
   `H_inf(T_p) >= log_2(N)-C` gives the stated coverage cap.
4. **Fixed-target retry:** the original reciprocal-retry wording was invalid.
   For one fixed factor base and target, `T in m_p F_p` is a static event;
   repeated tuple tests do not amplify it. If the cap is below `delta`,
   constant `delta` success is impossible, rather than merely expensive.
5. **Rerandomized cost:** pass after repair. A reciprocal lower bound requires
   an explicit fresh target-equivalent trial interface with conditional success
   at most `q_p`, source-recovery preservation, and a charged trial. Then
   `P(success by tau) <= q_p E[tau]` gives `E[tau] >= delta/q_p`.
6. **Universal scope:** unrestricted algebraic descriptions remain open.
   Target-dependent lines, high-degree interpolation, growing arity with
   implicit membership, signed/weighted factors, preprocessing oracles,
   extension fields, special curves, and non-sumset identities are escape
   routes, not falsifications.
7. **Asymptotic wording:** the bound is exponential in `log N` when epsilon is
   fixed and the inequality holds eventually. It is not a generic-group lower
   bound and should not be compared with rho unless a separate end-to-end
   reduction and cost model is supplied.

## Required disposition

The producer proposal was revised to split static fixed-target coverage from
the optional fresh-rerandomization lower bound. The universal question remains
open in `KN-OPEN-020`; no theorem status or ECDLP claim was promoted.
