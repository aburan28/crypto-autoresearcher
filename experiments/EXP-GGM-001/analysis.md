# EXP-GGM-001 Machine-checkable GGM simulability test

## Objective
Classify four augmented ECDLP oracles as SIMULABLE or NON-SIMULABLE in the
generic group model, validated against four controls.

## Control gate: 4/4 PASS
| Control | Expected | Actual | Correct? |
|---|---|---|---|
| pure_generic | SIMULABLE | SIMULABLE (C=1) | YES |
| discrete_log | NON_SIMULABLE | NON_SIMULABLE | YES |
| public_curve | SIMULABLE | SIMULABLE (C=0) | YES |
| encoding | NON_SIMULABLE | NON_SIMULABLE | YES |

## Augmented oracle verdicts
| Oracle | Verdict | Overhead C | Closed at 1/2? |
|---|---|---:|---|
| jet_oracle | SIMULABLE | 1 | **YES** |
| elliptic_net_oracle | SIMULABLE | O(log N) | NO (non-constant) |
| incidence_oracle | SIMULABLE | O(B^m) | NO (non-constant) |
| endomorphism_oracle | SIMULABLE | 0 | **YES** |

## Key findings

1. **Jet oracle is SIMULABLE with C=1**: the dual-number (eps) data is a
   deterministic function of (P, Q, P+Q, curve_parameters). The derivative
   of the addition map is a rational function of the coordinates, which are
   determined by the group element + public curve. **Closed at exponent 1/2
   by KN-TECH-005.** This closes all jet-based ECDLP candidates.

2. **Elliptic-net oracle is SIMULABLE but NOT with O(1) overhead**: the net
   value W(a,b) = a*P + b*Q is computable via group operations, but requires
   O(log a + log b) = O(log N) operations. The Somos identities are universal,
   so the net encodes only the group law. NOT closed at 1/2 — the O(log N)
   overhead means the generic lower bound does not directly apply. However,
   O(log N) << sqrt(N), so the net provides no sub-birthday advantage.

3. **Incidence oracle is SIMULABLE but NOT with O(1) overhead**: decompositions
   are found by brute-force summing m-subsets, costing O(B^m) group operations.
   For fixed B, m this is constant, but B grows with problem size. NOT closed
   at 1/2 by the constant-overhead bound.

4. **Endomorphism oracle is SIMULABLE with C=0**: phi is a public, deterministic
   map from the curve parameters. No group operations needed. **Closed at
   exponent 1/2.** This means H-STR-002's block-structure advantage is
   non-generic — the endomorphism is available to the generic model, and the
   block-circulant structure does not provide sub-birthday information.

## Scale independence
The SIMULABLE verdicts for jet (C=1) and endomorphism (C=0) are mathematical
closures valid at ALL scales (toy, medium, crypto), not toy-tier observations.
The O(1) simulator constructions are explicit and deterministic. Per
docs/claims-and-verification.md, these are derivation-level results
(proof_status: derivation), not empirical measurements.

## Limitations
- The classification uses the structured GGM (curve equation is public), not
  the strictest Shoup GGM (opaque labels). Under the strictest GGM, jet and
  endomorphism would be NON-SIMULABLE because they require coordinate access.
  The structured GGM is the standard setting for ECDLP analysis.
- The elliptic-net and incidence oracles are SIMULABLE but with non-constant
  overhead. They are not closed at 1/2 by the constant-overhead bound, but
  the overhead is still << sqrt(N), so no sub-birthday advantage exists.
- The test operates on oracle specifications, not implementations. An
  implementation may leak timing or side-channel information outside the GGM.
