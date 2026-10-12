# Semaev `S_3` hit-rate design audit

## Audit basis

- Idea: `IDEA-20261007-611573`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `KR-IC-f5c584`, `KR-IC-73db3f`, `KR-RHO-13bf67`, and the
  small-x factor-base controls.

## Scientific boundary

The proposed statistic is a finite hit-rate comparison for one interval
factor base. It is not a relation-collection rate, a linear-system result, or
an exponent claim. The proposal has useful safeguards—group-law checking,
random-subset comparison, and an explicit threshold-void rule—but the factor
base construction, x-coordinate sign quotient, null sample, and Semaev root
event need exact definitions before the ratio is interpretable.

## Load-bearing repairs

1. Define the curve and subgroup cell completely. Record the curve equation,
   prime field, prime-order subgroup generator/order, cofactor, ordinary
   certificate, and the exact point enumeration. State whether the input
   subgroup is the whole group and how the point at infinity is handled.
2. Make `F` deterministic at the boundary. Since `x(P)=x(-P)`, selecting
   `ceil(N^(1/3))` points by integer x can split a negation pair or depend on
   an arbitrary tie rule. Choose x-orbits first, state whether F contains
   both signs or one representative, and report the resulting cardinality;
   otherwise the pair-removal convention changes the denominator and hit
   count.
3. Define the root event in x-only and group-law terms. `S_3` vanishing at
   `(x(P1),x(P2),x(Q))` certifies that one sign choice has a sum equal to
   `Q` or `-Q` when the standard nonsingularity conditions hold. Check all
   sign choices, repeated points, the point at infinity, and exceptional
   denominators, and record the witness pair and sign rather than only a bit.
4. Specify `D_x` and the complement after exclusions. State the integer
   representative convention, strict versus inclusive threshold, whether F
   is removed before both rates, and whether negation orbits are counted once.
   Report the exact sizes of D, its complement, F, and the eligible Q set.
5. Repair the random-subset null. A random subset of size `|D_x|` needs a
   precise statistic: is it a replacement for D among all eligible points,
   a subset of Q values, or a random factor base of size `|F|`? Use matched
   sampling and enough independent draws to estimate the null ratio and its
   uncertainty. The threshold is void if the null itself exceeds two, but
   that rule must be applied before inspecting the D_x result.
6. Count collision and multiplicity information. For each Q, retain the
   number of witness pairs, unique unordered pairs, and x-only roots. A binary
   hit bit can hide a large multiplicity advantage or a duplicate-heavy F;
   report those as secondary metrics and predeclare which one is primary.
7. Include independent curves and uncertainty. Two curves are a useful pilot,
   not a population result. Freeze curve-selection rules, use an unseen curve
   or leave-one-curve-out summary, and give confidence intervals or exact
   finite-sample bounds for the two rates and their ratio. Do not generalize
   the small-N result to cryptographic sizes.
8. Price the actual relation pipeline separately. Include pair enumeration,
   Semaev evaluation, root testing, witness verification, factor-base
   storage, relation deduplication, and any future matrix step. A ratio near
   two can be useful evidence about this instrument while still being
   dominated by rho or by a different factor-base choice.

## Readiness and disposition

The proposal is a well-scoped finite control, but its current hit bit hides
sign, multiplicity, and boundary semantics, and the random-subset null is not
defined tightly enough to validate the ratio. It should remain separate from
any claim about a usable index-calculus attack.

Disposition: **retain proposed as a conditional Semaev hit-rate control; do
not approve or dispatch as filed.** Repair subgroup and factor-base
certificates, x-orbit selection, root-witness semantics, null sampling,
uncertainty, and cost accounting. Recheck runnable state, dependencies, and
approval capacity after a complete contract exists.
