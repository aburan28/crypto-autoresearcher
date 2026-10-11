# Teichmuller-lift smoothness design audit

## Audit basis

- Idea: `IDEA-20261009-9e4a40`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `KR-IC-cd159a`, `EXP-ECDLP-15534c`, and the multiplicative
  special-prime controls.

## Scientific boundary

The proposal addresses a useful distinction: a homomorphic lift need not
provide the size-bounded representatives used by NFS. Its stated null is not
yet justified, however. Teichmuller representatives modulo `p^k` form a
structured set of exactly `p-1` roots of unity inside `Z/p^k`, not a uniform
sample from all integers below `p^k`; homomorphism alone does not prove their
smoothness distribution. The proposed Dickman comparison and sample size also
need finite-probability calibration.

## Load-bearing repairs

1. Define the lift and sample space exactly. State the prime conditions, the
   unique Teichmuller representative, the canonical interval used after
   reducing modulo `p^k`, and whether `a` is uniform in `F_p^*` or sampled
   with a different weighting. Record the resulting set cardinality and
   duplicates; do not call it pseudo-random without a matched distributional
   test.
2. Use matched smoothness nulls. Compare the Teichmuller set with uniform
   integers in `[1,p^k)`, with a uniform set of `p-1` integers of the same
   cardinality, and with residue/congruence-matched controls. Report smoothness
   counts by prime factorization, not only a fraction. This distinguishes a
   size effect from a structured-set effect.
3. Replace the Dickman point estimate with finite bounds. State the exact
   smoothness definition, treatment of `0` and `1`, prime factors at most B,
   and the finite-size correction at each `u=log(p^k)/log(B)`. Give binomial
   or exact hypergeometric intervals and a power calculation; at rare-event
   rates, 10^5 samples may show zero hits and cannot support a ten-percent
   ratio claim.
4. Calibrate the k=1 arm independently. The naive representatives can test
   the finite-size correction for uniform integers below `p`, but the same
   sampler, factorization limit, and prime-factor table must be used. A
   pass at k=1 does not validate the Dickman extrapolation at k=2,3,4.
5. Freeze arithmetic and factorization costs. Record how Teichmuller roots
   are computed, precision/lifting steps, truncation, integer conversion,
   factorization method, smoothness bound, CPU/memory, and failed samples.
   If the lift-construction cost is part of the proposed obstruction, charge
   it separately from the smoothness test.
6. Add prime and size replication. One `p` near 40 bits and one run cannot
   support “no bias at any k”. Use multiple primes, k values, and B values,
   predeclare multiple testing, and include an unseen-prime panel. Report
   logarithmic sizes and event counts rather than relying on a single ratio.
7. Keep the cryptanalytic interpretation narrow. A smoothness difference in
   this finite representative set concerns a multiplicative-side control. It
   does not create an elliptic transfer or alter an ECDLP exponent without a
   complete relation algorithm and target reduction.

## Readiness and disposition

The proposal has a useful conceptual target, but the Teichmuller sample space,
matched null, finite rare-event statistics, and construction/factorization
costs are incomplete. The claimed Dickman ratio should remain a hypothesis,
not a theorem-derived prediction.

Disposition: **retain proposed as a conditional Teichmuller smoothness
control; do not approve or dispatch as filed.** Repair the lift definition,
matched nulls, finite probability model, k=1 calibration, replication, and
complete resource accounting. Recheck runnable state, dependencies, and
approval capacity after a complete contract exists.
