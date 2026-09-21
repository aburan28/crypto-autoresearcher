# BATCH-049 scope decision

BATCH-049 is a pure ideation batch for SG-ECDLP-002.

## What this batch does

Dispatch the Idea Generator (TASK-20260804-006) to propose one or more
**falsifiable** revised mechanisms for SG-ECDLP-002 that avoid the
class-invariant obstruction established by BATCH-048. Each proposal must:

1. Name a specific transfer or reduction mechanism that does NOT rely on
   ordinary F_p-isogenies changing the trace of Frobenius.
2. State the mechanism, predictions, minimal discriminating test, and
   falsification criteria.
3. Compare explicitly against Pollard rho: state `dominated_by` and
   quantitative `sota_delta` on time and memory.
4. Respect the Inventor Protocol (docs/inventor-protocol.md): null-object
   controls, Pareto honesty, no premature closure.

## What this batch cannot do

- No hypothesis-status changes (H-IT-001 stays `weakened` throughout)
- No experiment, no implementation, no run
- No crypto-scale claim
- No GOAL completion

## Admission gate

The Coordinator will review proposals against the target-result profile
(docs/target-result-profile.md). A mechanism that moves a sub-exponent-1/2
claim on a central problem is preferred. Logarithmic/constant-factor improvements
that cannot beat rho will be recorded but not prioritized.
