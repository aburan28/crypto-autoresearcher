# EDS linear-complexity design audit

## Audit basis

- Idea: `IDEA-20261009-9f89ae`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `KN-TECH-009`, `KN-LIT-018`, and the elliptic-net kernel
  controls.

## Scientific boundary

The proposed test can investigate whether a chosen scalar sequence exposes a
low-order linear recurrence beyond its defining elliptic recurrence. The
current prediction is not compatible with the stated observation window:
`W_n mod p` is periodic, so its linear complexity is bounded by the period and
cannot continue to grow like `L/2` through ten full periods. The period, zero
terms, normalization, and the exact recurrence-search object must be fixed
before the control is meaningful.

## Load-bearing repairs

1. Define the EDS sequence and observable. State the curve, point, division
   polynomial or net convention, initial terms, treatment of zeros at
   multiples of `ord(P)`, and whether the sequence is sampled raw, normalized,
   or restricted to nonzero indices. Different EDS conventions have different
   signs and recurrences.
2. Correct the linear-complexity window. For a periodic sequence of period
   `T`, measure the Berlekamp--Massey profile through a declared multiple of
   `T`, report the eventual minimal-polynomial degree, and compare the prefix
   and post-period behavior separately. Do not use `L/2` as a prediction after
   the profile has saturated; compare with random periodic sequences of the
   same period and zero pattern.
3. Make `ord(P)` and the budget feasible. Certify the point order and factor
   the relevant group order/cofactor. At 20--40-bit primes, ten periods may
   require an infeasible number of terms and quadratic Berlekamp--Massey work;
   predeclare smaller period panels, streaming algorithms, or a bounded prefix
   and label any extrapolation. A resource timeout is not a recurrence result.
4. Define the nonlinear recurrence search. Specify the variables (consecutive
   W terms, x/y coordinates, or net values), monomial basis, shifts, degree,
   span, coefficient field, normalization, rank test, and residual criterion.
   “Not a consequence of the EDS recurrence” requires an ideal/module
   reduction or an independent symbolic certificate, not only a nullspace
   dimension.
5. Add exact controls. Use random periodic sequences with the same period,
   alphabet, zero locations, and observed prefix length; include an LFSR with
   known complexity and an EDS instance whose defining recurrence is supplied
   to the verifier. Report false-positive and missed-recurrence rates.
6. Separate point order from DLP recovery. A period or recurrence certificate
   may reveal `ord(P)` or reproduce known sequence values, but it is not a
   discrete-log algorithm. Any transfer from EDS data to a logarithm needs an
   explicit map, target, cost, and independent known-answer certificate.
7. Replicate across arithmetic cells. Freeze prime selection, curve family,
   point sampling, order distribution, precision, implementation, and seeds.
   Report confidence intervals across points/primes and keep exceptional
   torsion or supersingular cells separate from the ordinary generic panel.

## Readiness and disposition

The proposal identifies a relevant shortcut class, but its principal `L/2`
prediction conflicts with periodic-sequence behavior and its recurrence search
is underspecified. The proposed term budget also needs a feasibility audit.

Disposition: **retain proposed as a conditional EDS recurrence control; do
not approve or dispatch as filed.** Repair the sequence convention, periodic
complexity model, order/resource panel, nonlinear search certificate,
matched controls, and separation from logarithm recovery. Recheck runnable
state, dependencies, and approval capacity after a complete contract exists.
