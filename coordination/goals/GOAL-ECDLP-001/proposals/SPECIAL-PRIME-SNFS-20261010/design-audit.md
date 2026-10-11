# Special-prime SNFS and embedding-degree design audit

## Audit basis

- Idea: `IDEA-20261009-2abd32`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `H-ECDLP-bd1572`, `KR-RHO-53c89f`, `KN-LIT-084`,
  `KN-LIT-085`, `KN-LIT-086`, and `KN-LIT-7635`.

## Scientific boundary

The proposal correctly separates two questions: whether the prime's
representation changes the curve's embedding-degree distribution, and whether
the same representation improves discrete logarithms in the multiplicative
field. Neither question is a curve-side ECDLP speedup without a valid pairing
transfer. The current contract needs sharper sampling of curve orders and a
reproducible finite-field polynomial-selection comparison; a Murphy-E ratio
from polyselection alone is not a sieving or discrete-log cost ratio.

## Load-bearing repairs

1. Bind the curve and subgroup sample. For each fixed prime, specify the
   curve family, sampling law, nonsingularity test, group-order computation,
   selected prime factor `l`, cofactor, and embedding degree
   `ord_l(p)`. “The large prime factor” is ambiguous when the order has
   several comparable factors; record all eligible factors and the rule for
   selecting one, or analyze the subgroup distribution without selection.
2. Match the random-prime null. Use primes with the same bit length and
   comparable residue and primality filters, and use an independently sampled
   curve panel for each prime. The null concerns the joint distribution of
   traces, group orders, prime factors, and multiplicative orders, not just a
   random integer `l`. Predeclare the KS statistic, alternative, minimum cell
   size, multiple-comparison correction, and power/sensitivity analysis.
3. Make the exact Curve25519 arm auditable. Name the exact subgroup order
   `l`, verify primality, compute `p mod l`, and provide the repeated-squaring
   certificate for `ord_l(p)` together with factorization of `l-1`. The
   comparison `ord_l(p) > l/4` is a chosen finite threshold, not a generic
   embedding-degree theorem; state why it is relevant to the transfer cost.
4. Define the special polynomial pair completely. Certify that the resultant
   gives the stated prime, record polynomial degrees, coefficient heights,
   irreducibility conditions, root sizes, and the exact CADO-NFS version and
   parameter file. Compare against a reproducibly generated GNFS candidate
   panel, not only the single best candidate found within an opaque budget.
5. Replace Murphy-E-only evidence with a cost proxy. Fix the sieving region,
   factor-base bounds, algebraic and rational side norms, skew, rotation,
   root properties, and smoothness model. Report Murphy-E, norm quantiles,
   relation-yield projections, and parameter uncertainty. Since the proposed
   arm performs no sieving, it must be labeled polynomial-selection evidence,
   not a measured discrete-log advantage.
6. Keep the positive control in scope. BN254 must have its exact curve order,
   embedding degree, field representation, and known transfer target recorded.
   Show that the same analysis detects its expected pairing-side behavior;
   otherwise a negative pseudo-Mersenne result may be an instrument failure.
7. Separate multiplicative and elliptic conclusions. A special form of `p`
   can improve arithmetic or polynomial selection in `F_p^*` while leaving
   `E(F_p)` at rho cost when no small embedding degree exists. State the
   transfer assumptions, subgroup preservation, final-exponentiation cost,
   and target-log conversion explicitly. Do not infer a curve-side result
   from a field-side Murphy-E or norm improvement.
8. Freeze resource and reproducibility receipts. Record CPU isolation,
   polyselection wall and CPU time, memory, random seeds, candidate counts,
   and the complete output. A fixed 24 CPU-hour budget must be a resource
   receipt with a stopping rule, not a claim that the best candidate is
   globally optimal.

## Readiness and disposition

The proposal is a useful separation control for special-prime arithmetic, but
its three arms currently mix a distributional null, an exact order
calculation, and a polynomial-selection heuristic. The subgroup-selection
rule, paired null, exact certificate, and field-side cost model are not yet
complete.

Disposition: **retain proposed as a conditional special-prime control; do not
approve or dispatch as filed.** Repair the curve-order/subgroup sampling,
Curve25519 order certificate, matched random-prime panel, polynomial-selection
receipt, cost proxy, and explicit separation of field-side from curve-side
claims. Recheck runnable state, dependencies, and approval capacity after a
complete contract exists.
