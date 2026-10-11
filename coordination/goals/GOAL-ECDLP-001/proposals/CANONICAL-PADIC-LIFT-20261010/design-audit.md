# Canonical p-adic lift design audit

## Audit basis

- Idea: `IDEA-20261009-4635cf`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `KN-TECH-73630e`, `KN-TECH-033`, `KR-RHO-53c89f`, and the
  p-adic lift controls.

## Scientific boundary

The prime-to-p torsion reduction isomorphism is a legitimate boundary for
canonical lifts, but the proposed information statistic mixes that canonical
section with arbitrary p-adic lifts. If the section is genuinely the torsion
section, `[N]` is exactly the identity and the formal-log statistic is zero;
if arbitrary lifts are sampled, there is no uniform distribution on an
infinite residue class until a finite perturbation law is specified. The
claimed mutual-information test therefore needs a precise random experiment
and a corrected positive control.

## Load-bearing repairs

1. Separate canonical and arbitrary lifts. Define the canonical prime-to-p
   torsion section using the exact reduction isomorphism, and prove/check
   `[N]s(P)=O`. Then define a separate finite perturbation model
   `s(P)+u` in the formal group, including the distribution of `u`, precision,
   truncation, and whether it is independent of `P` and `k`. Do not call
   infinitely many lifts “random” without that law.
2. Define the statistic algebraically. State the formal-logarithm domain,
   normalization by `N`, residue field, coordinate/basis, precision and
   reduction map. For the canonical section the expected value is the zero
   formal-group element; for perturbed lifts derive the conditional
   distribution before testing independence from `k`.
3. Fix the group and arithmetic assumptions. Certify good reduction,
   `N=#E(F_p)`, `p`-adic invertibility of `N`, subgroup order/cofactor, and
   the exact meaning of `Q=[k]P`. Keep prime-to-p torsion, anomalous `p|N`,
   and bad-reduction cells separate rather than treating them as one panel.
4. Repair the anomalous positive control. Specify the anomalous curve, the
   non-split extension, the point/lift distribution, and the exact statistic
   expected to reveal the Smart attack. A statement that it “becomes
   deterministic” needs an analytic derivation or known-answer certificate;
   failure may indicate only an invalid control implementation.
5. Verify ramified extensions correctly. Define the finite extension field,
   valuation normalization, ramification index, uniformizer, formal-group
   truncation, and the torsion order being tested. The pro-p property excludes
   prime-to-p torsion in the kernel, but it does not remove p-power phenomena
   or prove the chosen numerical statistic is lift-independent.
6. Use information-theoretic controls. Include independent random variables,
   a deliberately k-dependent perturbation, and a known deterministic
   canonical arm. Estimate mutual information with bias-corrected confidence
   intervals, report binning/quantization, and avoid interpreting a large
   chi-squared p-value as proof of zero information.
7. Charge precision and map costs. Record lift construction, Newton/log/exp
   iterations, precision loss, extension arithmetic, sample rejection, and
   target verification. A local isomorphism that does not expose a scalar
   still leaves the generic ECDLP cost unchanged; no transfer claim follows
   from the statistic alone.

## Readiness and disposition

The proposal identifies a useful canonical-lift boundary, but its central
statistic is either identically zero on the canonical section or undefined as
a distribution on arbitrary lifts. The anomalous positive control and
mutual-information estimator also require a complete finite model.

Disposition: **retain proposed as a conditional canonical p-adic lift
control; do not approve or dispatch as filed.** Repair the canonical versus
perturbed lift split, statistic, p-adic arithmetic cells, anomalous control,
information estimator, and resource receipts. Recheck runnable state,
dependencies, and approval capacity after a complete contract exists.
