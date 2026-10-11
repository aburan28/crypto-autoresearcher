# SNFS-S3 design audit

## Audit basis

- Idea: `IDEA-20261006-06fe5e`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  research status was changed.
- Governing records: `KN-TECH-002`, `KR-IC-5a43e5`, and `KR-IC-5931ee`.

## Scientific boundary

The proposed object is a fixed arithmetic regression fixture: evaluate the
displayed `S_3` polynomial on four named points over `F_41`, on their six
explicit sum triples, and at the proposed third-coordinate value `7`. The
vanishing rule and the degree-two formula are established knowledge. The
listed residues, if reproduced, add an exact test vector and implementation
cross-check; they do not add a decomposition method, factor-base result, or
ECDLP algorithm.

The idea is therefore not a new research mechanism. Its useful role is a
small correctness control that can protect later Semaev or solver experiments
from an incorrect formula, sign convention, or field-arithmetic
implementation.

## Required control contract

Before any result is treated as a valid fixture, the record must bind:

- the exact short-Weierstrass equation and nonsingularity check;
- the exact `S_3` normalization and coefficient order;
- the four point coordinates and the six unordered pair ordering;
- the chord-and-tangent implementation used to name the third coordinate;
- two independent arithmetic paths, not two calls through one shared helper;
- the six true-sum evaluations, the six evaluations at `7`, and the repeated
  evaluation outputs; and
- a void/inconclusive outcome when a point check, normalization check, or
  implementation-independence check fails.

The proposed `S_3(x,x,7)` rows must remain outside the six pair assertions.
The control should also state that replacing `x(P+Q)` by `x(-(P+Q))` does not
change the x-coordinate, so this fixture cannot detect that particular sign
mistake. A normalization differing by a nonzero field unit changes the
nonzero residues while preserving the zero set; the expected normalization
must therefore be checked before comparing the six listed integers.

## Interpretation and disposition

Matching all twelve values would certify only the named finite arithmetic
fixture. A mismatch is an implementation or contract defect until the exact
source of the disagreement is isolated; it is not negative evidence against
Semaev summation polynomials. A successful fixture does not challenge the
prime-field index-calculus cost boundary recorded in `KR-IC-5931ee` and does
not transfer from one curve or prime to larger parameters.

Disposition: **keep proposed as a control; do not approve it as an independent
scientific experiment or claim-changing direction.** It may be embedded as a
pre-run correctness gate in a future runnable Semaev experiment, provided the
gate has a separate artifact and a failed gate prevents interpretation of the
dependent run. If no dependent experiment is admitted, the proposed control
does not justify standalone execution under the current high-load and empty
selector conditions.

Next action: either attach this exact two-implementation fixture to a repaired
Semaev experiment with a frozen artifact path, or leave the idea proposed as a
regression-control resource. It must not be promoted by its own twelve-value
recount.
