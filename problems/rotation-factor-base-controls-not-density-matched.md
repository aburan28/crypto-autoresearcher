# Rotation factor-base controls do not match actual density

- **Status:** `open`
- **Kind:** protocol/implementation mismatch; statistical inference gap
- **Affected work:** [EXP-ECDLP-ad27ad](../experiments/EXP-ECDLP-ad27ad/specification.yaml), H-ECDLP-986bab, the rotation control overlapping SNFS-A4
- **Next action owner:** Coordinator / Experiment Director for a prospective corrected protocol; independent Reviewer for the assessment
- **Last updated:** 2026-10-17

## Problem

The frozen rotation grid cannot establish its stated comparison against equal-density null subsets because nominal parameter m does not match their actual densities.

The original specification claims D_rot(m) has density about 2^-m. Its implementation tests whether **any cyclic rotation** of x is below 2^(c-m), while the hash and size controls apply one threshold with nominal density 2^-m. The original protocol remains frozen and its run must be preserved without post hoc repair.

## Evidence and uncertainty

- **Observed by static inspection:** at execution source `82cc1338b982c401002f77dc4c19cb2c10a04989`, `experiments/EXP-ECDLP-ad27ad/implementation/run.py`, `make_membership` and `rotmin` implement these different conditions. The frozen parameters are c in {13,17,19,31,61}, m in {1,2,4}, two curves and seeds {1,2,3}. Actual densities are separately recorded by the existing run; terminal observations belong in its immutable run directory and descriptive report.
- **Derived, exact scope:** for m=1, every x in [0,2^c-2] has at least one zero bit in its c-bit representation. Rotating that bit to the leading position makes the value smaller than 2^(c-1). Thus this rotation condition accepts every finite affine curve point, rather than a half-density factor base. This argument concerns membership only; it is not a complexity result or a hypothesis status transition.
- **Additional implementation limits:** `random_point` rejects RHS=0 and never returns O; exact enumeration includes finite y=0 points and excludes O. The domains differ if rational 2-torsion exists. Recorded ratio standard errors divide a binomial numerator standard error by an estimated density, without accounting for denominator uncertainty; decomposition draws also share their target R. These are limitations of the recorded uncertainty formula, not newly measured significance levels.
- **Missing capability:** a prospectively specified, independently checked density-matched control and uncertainty model on a common point domain.
- **What this does not establish:** no measured matched-control advantage, no DLP speedup or impossibility, and no conclusion about arbitrary structured factor bases. Frozen producer/checker success alone does not resolve the design mismatch.

## What would unblock it

- [ ] Independently review the membership and sampling-domain analysis, preserving the original specification and every original run byte.
- [ ] Specify a new version with a common point domain and explicit actual-density/cardinality matching, including how control thresholds are fixed without reusing test outcomes.
- [ ] Specify uncertainty propagation for the density denominator, shared-target sampling and multiple comparisons, plus deterministic replay and small-field exact controls.
- [ ] Obtain exact-byte approval and lawful published dispatch for the new version before scientific execution. Keep original grid observations separate from that version.

These conditions would permit a valid finite comparison. A useful factor-base size, completed decomposition cost, relation yield, matrix cost and verified improvement over the frozen IC baseline would remain separate requirements.

## Next discriminating step

- **Action:** preserve and report the current frozen run with actual per-arm densities and the static caveats above; prepare a corrected prospective protocol only after independent design review.
- **Inputs and controls:** literal frozen membership code and argv, original sampling domains, and independently implemented exact membership/domain checks at small p.
- **Execution limits and stop condition:** retain the current frozen sample counts and machine-protection limits. This record authorizes no additional run or campaign cap.
- **Outcomes:** density mismatch keeps the equal-density interpretation unavailable; a valid prospective matched comparison would permit that interpretation only on its tested domain. A timeout, checker failure or manifest failure is retained with its own scope.
- **Recheck trigger:** current terminal report or an independently reviewed prospective version.

## Resolution and history

2026-10-17: Named during execution of RUN-ECDLP-a5281a. The report will display actual densities; frozen source and protocol are unchanged. Unresolved. Recording or merging this problem is not a research result or a scientific graph/status correction.
