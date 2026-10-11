# Semaev small-root threshold design audit

## Audit basis

- Idea: `IDEA-20261009-85062c`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `KR-IC-5931ee`, `KR-IC-fbdb61`, `KN-LIT-037`, and the
  size-based factor-base controls.

## Scientific boundary

This proposal can measure the success boundary of a specified lattice solver
on bounded roots of selected summation polynomials. It does not by itself
recover a discrete logarithm: a recovered tuple of x-coordinates must still
be converted to valid curve points, a relation must be certified, and the
factor-base/target pipeline must use the relation. The current contract also
uses planted algebraic roots whose distribution may differ from the natural
factor-base relation distribution.

## Load-bearing repairs

1. Freeze the polynomial family and coordinates. Publish the exact normalized
   `S_3` and `S_4` polynomials, curve parameters, field primes, coefficient
   embedding into centered integers, and the variable ordering. Remove or
   separately classify singular/degree-drop cells, repeated roots, and cases
   where a leading coefficient vanishes modulo `p`.
2. Define the root event precisely. A successful root must include bounded
   `x_i`, a valid curve point for each x-coordinate, compatible y-signs, the
   claimed sum relation, and an independently checked output point. Count
   all roots found, unique roots, false positives, and missed planted roots;
   x-coordinate recovery alone is not a relation certificate.
3. Match planted and natural nulls. Sample points uniformly from the stated
   curve subgroup, map their x-coordinates to the centered interval, and
   report the induced distribution. Compare with uniform bounded integers and
   with naturally generated Semaev roots. A planted root constructed by first
   choosing small inputs can introduce algebraic or curve-side structure that
   flatters the solver.
4. Define the size parameter. State whether `|x_i| < p^beta` means centered
   integer representatives, positive representatives, or a residue interval,
   and report the actual bit lengths and boundary inclusion. Use independent
   primes/curves at each size and avoid presenting a beta fitted on 40--80
   bits as an asymptotic threshold.
5. Separate solver families and resources. Freeze lattice shifts, dimension
   selection, LLL/BKZ versions and parameters, pruning, precision, restart
   policy, and stop conditions. Report success against dimension and wall/CPU
   time, memory, and failure mode. “First success” and “maximum dimension”
   are different statistics and need separate confidence intervals.
6. Repair the S4 comparison. State the exact number of variables after
   eliminating any coordinate, the per-variable degree, the lattice volume
   model, and the chosen Coppersmith/Howgrave--Graham construction. A
   heuristic beta threshold cannot be inferred only from a degree slogan;
   give the predicted bound and sensitivity to shifts and determinant loss.
7. Add calibration and chance controls. The linear bivariate calibration
   must have a known root domain and an independently computed success
   threshold. Include random-polynomial controls with the same degree,
   coefficient size, modulus, and root domain, plus a no-root panel to measure
   false positives and accidental short-vector outputs.
8. Bound the interpretation. A low beta threshold is evidence about this
   solver and polynomial family. It does not close every algebraic relation
   method, and a high threshold would not establish an ECDLP speedup without
   factor-base size, relation yield, sparse linear algebra, target coverage,
   and matched rho costs.

## Readiness and disposition

The proposal has a concrete minimal test and appropriate instrument-failure
language, but its planted-root distribution, root-validity certificate,
polynomial normalization, S4 lattice model, and solver-resource contract are
not complete. The proposed beta thresholds should remain finite empirical
benchmarks rather than asymptotic claims.

Disposition: **retain proposed as a conditional Semaev small-root control; do
not approve or dispatch as filed.** Repair the root and point certificates,
natural/null distributions, size definition, S4 construction, calibration,
and complete resource receipts. Recheck runnable state, dependencies, and
approval capacity after a complete contract exists.
