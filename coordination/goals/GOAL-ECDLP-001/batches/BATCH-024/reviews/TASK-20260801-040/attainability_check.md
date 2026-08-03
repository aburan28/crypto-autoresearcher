# TASK-20260801-040 attainability check

Verdict: **REVISE**.

I read the six frozen conditions in their precedence order: D-0, D-1, D-5,
then exactly one of D-2, D-3 or D-4. No condition references a hypothesis or
ledger status. Status changes appear only in dispositions. The prospective
OPEN-BATCH023-B repair therefore passes.

THR-DEP-REPRO's lower leg is expressly declared dead: zero is both the minimum
attainable count and the lower edge of `[0,8]`. The rule does not silently rely
on an under-rejection check.

## Branch-by-branch classification

| Branch | Classification | Independent ruling from measured calibration numbers |
|---|---|---|
| D-0 | REACHABLE-IN-PRINCIPLE | The eight genuine DEP-CAL-A identity-null exceedance counts are `0,2,3,2` and `0,2,1,0`; D-0's reproduction leg fires at 9. Nine is an attainable integer out of 200, while no calibration integrity leg actually fired. Digest mismatch, short-arm, nonzero-c2, timeout and hash-failure legs are failure predicates rather than mathematical outcomes. |
| D-1 | **UNDECIDABLE-AS-FROZEN; REVISE** | Calibration demonstrates that the measured quantities vary: DEP-CAL-C K=16 joint TV is about 0.023 and the comonotone anchor about 0.92; plant Spearman ranges near zero to essentially one. But the branch says `beyond sampling noise` without a tolerance or test, and gives the CELL-TV monotonicity leg no noise rule. Reachability of some monotone/nonmonotone numerical sequence is not enough: identical arrays can be classified differently by honest readers. |
| D-5 | **DEMONSTRATED-REACHABLE, AND FIRED UNDER THE LITERAL RULE** | DEP-CAL-C's largest count is 6/200, so its first leg is reachable in principle but did not fire. DEP-CAL-E measured `0,0,0,0` at bits 16 and `0,0,0,1` at bits 20. The specification defines DEP-CAL-E as 20 comparisons and says `a rejection is an implementation defect`; D-5 says the control rejects at either cell. The single bits-20 STAT-KS1-E2 exceedance is therefore a control rejection under the natural frozen reading. |
| D-2 | REACHABLE-IN-PRINCIPLE | DET-DEP-1 is mechanically equivalent to at least 190/200: the exact one-sided lower bound at 190 is 0.9166648489336275, above 0.90. DEP-CAL-D measured 20/20 for both chi-square statistics at both cells on a dependence-only anchor. A minimum at any frozen rho rung at or below 0.05 is arithmetically attainable, though no such rung was measured. |
| D-3 | REACHABLE-IN-PRINCIPLE | Counts below the bar occur at both measured endpoints and for certifying statistics at both cells. It is possible for every RHO and CELL rung to stay below 190 at at least one cell. No ladder rung was measured, so this is not demonstrated. This branch is interpretable only if the repaired D-1 movement gate first establishes that non-detection is not an inert-plant artifact. |
| D-4 | REACHABLE-IN-PRINCIPLE | The terminal value domain explicitly permits a rho floor in `{0.10,0.25,0.50,1.00}`, or no rho floor with an eps floor in `{0.005,0.01,0.02,0.05,0.10,0.25}`. The measured near-zero and 20/20 endpoint counts show the instrument attains both ends of its count range; they do not predict a rung. |

## D-5 contract interpretation

The two readings listed in RR-DEP-1 are not equally supported by the frozen
source. Reading A follows the defined unit: each DEP-CAL-E comparison produces
four strict-threshold rejection booleans, and the specification says “a
rejection is an implementation defect.” Reading B invents an aggregate test
whose statistic, multiplicity unit, nominal reference and materiality cut were
never frozen. This conclusion is based on grammar and data structure, not on
whether the observed count was zero or one.

After that interpretation is fixed, applying it to the archived number is
mechanical: 1 is nonzero, so D-5 fires. Because D-5 precedes every substantive
terminal branch, RUN-DEP-001-measure must not be authorized under version 1.

## Additional design-merit checks

- `rho_star=0.05` is explicitly a convention, not an estimate. Reporting the
  full curve makes that defensible, but it cannot be described as a derived
  structural boundary.
- `eps_det/0.02` compares touched-record fractions, not a common effect size.
  The CELL plant and the prior e1-marginal plant induce different joint-TV,
  rank and noncentrality changes. The ratio is honest only if labelled as the
  ratio of smallest detected rungs for those two named constructions.
- With 130816 samples per arm, average occupancy is about 511 per K=16 joint
  cell and 31.9 per K=64 joint cell. Both grids are feasible at the frozen toy
  cells; this is not a scale or asymptotic claim.

The attainability inventory is therefore useful, and four terminal/failure
regions have clear achievable numerical assignments. It does not pass the
completion gate because D-1 is not mechanically decidable and the literal D-5
control has already rejected.

