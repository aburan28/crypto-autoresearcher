# Chevalley generalized-Jacobian transfer audit

## Audit basis

- Idea: `IDEA-20261009-61fc7f`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `KR-RHO-53c89f`, `KN-LIT-084`, `KN-LIT-085`, and the
  generalized-Jacobian transfer controls.

## Scientific boundary

The proposed family is a reasonable place to organize known transfer
mechanisms, but the claim is not yet a well-defined finite classification. A
generalized Jacobian has an exact sequence involving a linear kernel and the
Jacobian of the base curve; an extension class, an l-torsion point, a group
homomorphism, and a usable discrete-log transfer are different objects. Also,
for `l != p`, defining `k=ord_l(p)` makes `l | p^k-1` automatic, so that
condition cannot by itself distinguish a successful transfer from an ordinary
subgroup.

## Load-bearing repairs

1. Define “transfer” with maps and success criteria. Specify the source
   subgroup, target group, explicit homomorphism or correspondence, kernel and
   cofactor, subgroup preservation, and the operation that turns a source
   discrete logarithm into the target logarithm. A nontrivial extension class
   or an l-torsion point in a kernel is not sufficient without an efficiently
   computable map and a correctness certificate.
2. State the exact generalized-Jacobian sequence. Give the curve, modulus,
   reduced/non-reduced structure, dimension, and sequence
   `1 -> L_m -> J_m -> J -> 0`, including the field of definition. Explain
   how the elliptic factor `E` is obtained from `J`, and keep abelian-factor
   isogenies separate from linear-kernel extensions. “Surjecting onto E” needs
   an actual morphism, not only a structural analogy.
3. Repair the l-divisibility criterion. Split `l=p` unipotent cases,
   `l != p` torus cases, and abelian/isogeny cases. For a torus, record its
   splitting degree and exact rational l-torsion; for an abelian factor,
   record the isogeny degree and rational subgroup. Do not use the tautology
   `l | p^ord_l(p)-1` as evidence that a transfer exists.
4. Define the finite enumeration. “All moduli of degree <=4” needs a bounded
   coefficient/model normalization, equivalence relation, field primes,
   singularity and bad-reduction filters, and a complete count of omitted
   isomorphism classes. A three-prime table can validate implementation cells
   but cannot certify a global classification.
5. Make positive controls executable. For the unipotent and toric controls,
   publish known source/target groups, maps, expected l, splitting degree,
   and independent round-trip checks. Require every negative cell to carry a
   certificate that the relevant l-torsion and map were actually enumerated,
   rather than treating a missing implementation path as a null result.
6. Include nonreduced arithmetic explicitly. Nilpotent local factors are not
   interchangeable with a product of fields; define the group law, p-power
   torsion behavior, and extension-class computation for each local type.
   Report characteristic and inseparability issues separately from separable
   pairing or torus transfers.
7. Bind the cryptanalytic cost. Measure map construction, l-torsion/cofactor
   handling, target logarithm, final exponentiation or rational-function
   evaluation, and representation conversion. A structural transfer table
   without a usable reduction does not alter the rho baseline.
8. Keep the conclusion scoped. A complete table for degree-bounded moduli at
   selected small primes can close only that model and parameter range. It
   cannot assert that no other correspondence, isogeny, cover, or higher-
   degree modulus provides a transfer.

## Readiness and disposition

The proposal is a potentially useful classification receipt, but its transfer
predicate and its enumeration universe are underspecified, and the central
divisibility statement is not discriminating once an embedding degree is
defined. It should not be approved on the strength of Chevalley terminology
alone.

Disposition: **retain proposed as a conditional generalized-Jacobian transfer
control; do not approve or dispatch as filed.** Repair the exact maps,
extension-class semantics, l-divisibility cases, finite enumeration,
positive/negative certificates, nonreduced arithmetic, and end-to-end costs.
Recheck runnable state, dependencies, and approval capacity after a complete
contract exists.
