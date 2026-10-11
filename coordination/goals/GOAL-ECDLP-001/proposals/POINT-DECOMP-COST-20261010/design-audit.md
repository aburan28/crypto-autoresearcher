# Point-decomposition cost-scaling audit

## Audit basis

- Idea: `IDEA-20261009-f24f8a`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `KR-IC-5931ee`, `KN-LIT-025`, the Semaev decomposition
  records, and the existing IC performance experiments.

## Scientific boundary

The proposal measures whether bounded-coordinate point decomposition scales
linearly in the factor-base size for several solver families. That is a useful
finite cost study, but its current contract does not define the measured
object tightly enough to support the claimed exponent or the cross-solver
comparison. In particular, `m`, `S_{m+1}`, `|F_beta|`, and the expected
decomposition fraction are not linked by one fixed arity and point-versus-
x-coordinate convention.

## Load-bearing repairs

1. Define the factor base exactly: x-values or signed points, affine-point
   multiplicity, subgroup/order, coordinate interval, treatment of the
   identity, inverse pairs, repeated points, and the exact cardinality as a
   function of `p` and `beta`. Define whether `m` counts summands or free
   variables and derive the expected `p^(m beta - 1)/m!` expression from the
   same convention. Verify it by exhaustive or independently sampled group
   arithmetic before timing solvers.
2. Define a decomposition success. State the target distribution, whether
   ordered tuples and multiplicity are retained, how `P=Q` and `P=-Q` are
   handled, and whether a Semaev root counts only after direct point-addition
   verification. A planted witness validates encoding and recovery but does
   not measure search on an unseen target.
3. Freeze the size panel before fitting. Seven p sizes with `p`, bit length,
   factor-base size, field arithmetic cost, and solver encoding width all
   changing together can create a misleading log-log slope. Predeclare the
   fit range, robust estimator, bootstrap unit, confidence interval, and
   minimum successful/failed observations. Report field-operation counts and
   wall time separately for pseudo-Mersenne and random-prime controls.
4. Keep solver comparisons honest. SAT, F4/F5, enumeration, and Coppersmith
   solve different encoded problems unless their variables, equations,
   auxiliary digit constraints, root multiplicities, and output certificates
   are matched. “Where applicable” is not a frozen Coppersmith arm. Record
   version, preprocessing, parameter search, compilation, peak memory, and
   all failed or timed-out instances.
5. Charge the complete decomposition path: factor-base construction,
   target generation, equation/encoding construction, solver, root
   extraction, direct group verification, duplicate removal, and output
   serialization. A solver-stage timing or a planted-target shortcut cannot
   support the stated `T_decomp` metric.
6. Treat first-fall degree and degree of regularity as separate measured
   quantities. Define both for inconsistent, non-regular, and positive-
   dimensional systems, and specify how a solver abort is represented. The
   gap is a diagnostic, not itself a complexity theorem.
7. Match random-prime and pseudo-Mersenne controls on bit length, group/order,
   factor-base cardinality, target distribution, and arithmetic operation
   costs. If the aim is only representation sensitivity, say so; do not mix
   it with a claim about the underlying decomposition exponent.
8. Limit the inference. An exponent fit over the declared finite panel can
   describe that panel only. A fitted exponent at or below the proposed
   threshold would require an unseen same-point target, matched rho and full
   phase accounting before it could support any speedup claim; a null fit does
   not prove a universal lower bound.

## Readiness and disposition

The record is proposal-only and has no committed launcher, solver-specific
contracts, frozen input certificates, or run directory. Its high compute
estimate and multiple solver arms require a complete bounded protocol before
approval; the selector currently has no ready row.

Disposition: **retain proposed as a conditional finite scaling study; do not
approve or dispatch as filed.** Repair arity/cardinality semantics, target and
root certificates, fit/statistical rules, solver matching, and full-cost
accounting. Recheck runnable state and approval capacity after the successor
contract is complete.
