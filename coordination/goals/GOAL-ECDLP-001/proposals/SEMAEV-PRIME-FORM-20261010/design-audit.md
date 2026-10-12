# Semaev prime-form invariance design audit

## Audit basis

- Idea: `IDEA-20261009-0f3a09`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `KR-IC-5a43e5`, `KR-IC-5931ee`, `KN-LIT-001`, and the
  special-prime control proposals.

## Scientific boundary

The algebraic part is a reasonable control: a fixed integer polynomial is
reduced modulo a prime, so the prime’s bit shape does not automatically alter
its formal support. The current record overstates the scope of that statement.
Specialization can make coefficients vanish, factorization can change over the
finite field, and timing on one workload does not measure an ECDLP cost or
prove a uniform constant-factor bound.

## Load-bearing repairs

1. Separate formal and specialized support. Publish the symbolic polynomial in
   `Z[a,b][x]`, its coefficient support, and the exact specialization rule.
   For each prime and `(a,b)`, report coefficient values modulo `p`, zero
   coefficients, degree drops, repeated factors, and factorization patterns.
   The claim “support is identical” needs a coefficient nonvanishing condition;
   it is not automatic when coefficients or specialized values are divisible
   by `p`.
2. Define matched parameters across primes. A pair `(a,b)` must mean either
   fixed integer representatives reduced into each field or independently
   sampled field elements with a stated coupling. Also certify nonsingular
   curves, characteristic exclusions, and the exact Semaev normalization for
   every cell.
3. Use a complete arithmetic null. Match bit length, residue constraints,
   primality filter, curve parameters, coordinate representation, field
   implementation, and backend flags between pseudo-Mersenne and random-prime
   cells. Otherwise a timing difference can be a library dispatch or operand
   distribution effect rather than prime form.
4. Define the fixed workload and success metric. Freeze polynomial sizes,
   factor-base/domain distribution, solver parameters, restart/timeout policy,
   output verification, and seeds. Report throughput, operation counts,
   memory, failure rate, and modular-reduction share, with paired runs and
   confidence intervals; a single wall-time ratio is descriptive only.
5. Calibrate arithmetic separately. Include a modular multiplication and
   reduction microbenchmark with the same operands, then compare the full
   symbolic/Semaev workload. State whether the ratio is expected to remain
   within `[1/3,3]` over the entire size range; that band is a chosen finite
   acceptance interval, not a mathematical consequence.
6. Keep the interpretation finite. Formal support equality supports no
   curve-side speedup claim. A measured arithmetic advantage can affect an
   implementation cost while leaving relation yield, linear algebra, target
   coverage, and rho comparison unchanged. A support or coefficient mismatch
   is evidence about the tested specialization, not a general contradiction
   of Semaev’s construction.

## Readiness and disposition

The proposal is a low-cost control and its expected symbolic identity is
plausible, but the formal-versus-specialized support distinction, matched
parameter rule, arithmetic null, and paired timing contract are incomplete.

Disposition: **retain proposed as a conditional Semaev prime-form control; do
not approve or dispatch as filed.** Repair support semantics, parameter
matching, specialization certificates, paired workload/timing receipts, and
finite interpretation. Recheck runnable state, dependencies, and approval
capacity after a complete contract exists.
