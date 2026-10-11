# Mersenne embedding-degree control audit

## Audit basis

- Idea: `IDEA-20261009-64a1c0`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `KR-RHO-53c89f`, `EXP-ECDLP-6dacdb`, `H-ECDLP-bd1572`, and
  the public-parameter SNFS references cited by the proposal.

## Valid narrow arithmetic scope

For `p = 2^c - 1`, the identities

`p - 1 = 2(2^(c-1)-1)`, `p + 1 = 2^c`, and
`p^2 + 1 = 2(2^(2c-1)-2^c+1)`

do establish the following finite arithmetic facts for an odd prime `l`:

- `k = 1` implies `ord_l(2) | c-1`;
- `k = 2` cannot occur because an odd `l` dividing `p+1` would have to divide
  `2^c`;
- the exact `k = 3` and `k = 4` tests can be performed from the relevant
  cyclotomic values, with the usual cyclotomic-index exceptional-prime rules;
- divisibility by the displayed `k = 4` factor implies an order constraint,
  but an order constraint alone is not equivalent to divisibility.

These identities are a control or certificate. They do not determine the
distribution of embedding degrees `k >= 5`, nor do they establish a pairing
transfer advantage or disadvantage beyond the tested conditions.

## Load-bearing repairs

1. Bind the exact subgroup for every curve: full group order, cofactor,
   selected odd prime `l`, generator, and a certificate that `l` is prime.
   State whether an observed order is exact, a certified lower bound, or a
   result conditional on factoring `l-1`. Treat `l = 3` and other primes
   dividing cyclotomic indices explicitly when translating `Phi_k(p)`
   divisibility into exact embedding degree.
2. Separate theorem checks from the empirical census. The zero `k = 2`
   prediction is an arithmetic invariant for the declared odd-subgroup scope;
   it is not a statistical observation requiring `10^4` random curves. The
   KS comparison after removing `k = 2` tests a finite sampling model and
   needs a frozen curve-generation distribution, order-selection rule, random
   prime matching, and an independent treatment of the large-prime-factor
   selection bias.
3. Make the `ord_l(2) <= 10^4` census reproducible. Define the candidate-prime
   population, whether primes are counted once or by divisors of `2^d-1`, the
   truncation at `10^4`, treatment of repeated orders and exceptional primes,
   and the exact predicted density. A Cunningham factor table and a density
   heuristic are not interchangeable evidence.
4. For P-521, P-192, P-224, and P-256, bind the exact named curve, subgroup
   order, and parameter source. A direct exponentiation lower bound must
   state which exponents/divisors were checked and cannot be presented as the
   exact embedding degree without the necessary factorization. The four
   low-degree tests are a certificate only for the stated prime and subgroup.
5. Remove the unsupported statement that no cyclotomic-in-2 condition exists
   beyond `k = 4`. The displayed `Phi_6(p)` expression shows only that one
   simple identity is not being used; it is not a proof that all higher `k`
   have no exploitable arithmetic conditions. Limit the claim to the explicit
   identities actually certified.
6. Split the multiplicative-side SNFS comparison into a separate public-field
   arithmetic measurement. Murphy-E is a polynomial-selection score, not an
   end-to-end GNFS/SNFS runtime or an ECDLP transfer result. Freeze software,
   polynomial admissibility, coefficient and norm metrics, selection budget,
   and the baseline population before comparing `2^521-1` with another
   modulus. Do not infer a curve-side consequence from that comparison.
7. For any proposed run, keep the four arms separate: theorem certificate,
   embedding-degree census, public-curve lower bounds, and multiplicative
   polyselect. Each needs its own inputs, validity status, cost, and claim
   ceiling; a failure or timeout in one arm does not refute another.

## Claim ceiling and disposition

A complete finite record could certify the `k = 2` exclusion, verify the
declared `k = 1,3,4` conditions for named subgroups, and report a bounded
census under an explicit null. It would not show that Mersenne-prime curves
are generically protected for `k >= 5`, establish a new ECDLP algorithm, or
turn a Murphy-E score into a cryptanalytic speedup.

Disposition: **retain proposed as a split finite control; do not approve or
dispatch as filed.** The theorem arm may be reduced to a certificate-only
record; the census needs a frozen sampling/null contract; the public-curve
arm needs exact subgroup and lower-bound receipts; and the SNFS arm should be
separately specified or removed. Recheck readiness and approval capacity only
after those boundaries are recorded in an executable contract.
