# Binary twist control conflicts with the cofactor-two admission rule

- **Status:** `open`
- **Kind:** proved mathematical obstruction to one frozen protocol arm; protocol correction required
- **Affected work:** [EXP-ICPERF-42ef30 Stage 1 C-TWIST and AR-3](../experiments/EXP-ICPERF-42ef30/specification.yaml)
- **Next action owner:** Coordinator for GOAL-ICPERF-e6b6a4
- **Last updated:** 2026-10-16

## Problem

EXP-ICPERF-42ef30 requires a quadratic-twist C-TWIST prediction on the same
binary field but AR-3 admits only curves with `#E = 2r`, `r` odd. For every
ordinary binary curve of the specified form satisfying AR-3, its quadratic
twist has group order divisible by four and is refused by AR-3. The current
contract cannot both evaluate C-TWIST's `lambda_x` prediction and obey its
curve admission rule.

This concerns `y^2+xy=x^3+a x^2+b` over `F_q`, `q=2^n`, `b != 0`, including
the shipped Koblitz cells n=15,17,19. It is a protocol conflict, not evidence
about class-aligned factor bases, solver cost, or ECDLP difficulty.

## Evidence and uncertainty

- **Observed:** Sage 10.10.rc0 counted the shipped `a=1,b=1` curve and its `a'=0,b=1` twist at n=7,15,17,19. The respective `(N,N')` pairs were `(142,116)`, `(32494,33044)`, `(131174,130972)`, `(525086,523492)`. Every first count is `2 mod 4`, every twist count is `0 mod 4`, and each pair sums to `2(2^n+1)`. This was a local diagnostic; the proof below, rather than a numerical sample, establishes the general obstruction.
- **Derived or proved:** For nonzero `x`, write `z=y/x`. The curve equation becomes `z^2+z=x+a+b/x^2`. Replacing `a` by `a'` with opposite absolute trace flips the solvability of this Artin-Schreier equation, so exactly one of the two curves has two points at each nonzero `x`. Both have the point at infinity and one point at `x=0`, hence `#E + #E' = 2(q+1)`. Since `q` is even, `2(q+1)=2 mod 4`. AR-3's `#E=2r`, `r` odd, gives `#E=2 mod 4`, forcing `#E'=0 mod 4`. This conclusion does not depend on sample size.
- **Suspected explanation:** C-TWIST was specified as a nearby-object count check without reconciling it with the later cofactor-two-only `lambda_x` model. The mathematical contradiction is independent of that drafting history.
- **Missing capability:** A Coordinator-approved correction: either an independently checked cofactor-four landing/count model that extends C-TWIST, or a revised admissible nearby-curve control with a separately reported twist refusal and explicit inference policy.
- **What this evidence does not establish:** It does not refute the count formula on admitted cofactor-two curves or rule out a valid cofactor-four extension. It does not authorize silently omitting the twist arm.

## What would unblock it

- [ ] Commit a Coordinator correction to EXP-ICPERF-42ef30 resolving C-TWIST versus AR-3, with the chosen control, curve admission rule, expected outcomes, and inference limits stated before any Stage-1 run.
- [ ] If admitting cofactor-four twists, implement and independently validate the additional `2E/4E` landing criterion and resulting `lambda_x` formula. If retaining AR-3, identify an admitted replacement control and preserve the twist's factorization/refusal as an explicit observation.
- [ ] Recheck the resulting protocol and launcher with `tools/newest_experiments.py --experiment EXP-ICPERF-42ef30` before approval or execution.

These conditions would make the control evaluable under its declared scope. They
would not establish a relation-yield gain, full-cost improvement, or 50–63-bit
transfer.

## Next discriminating step

- **Action or proof obligation:** Coordinator chooses and freezes one of the two correction routes above; the executor implements its independent arithmetic control.
- **Inputs and controls:** The four counted curve/twist pairs above, the exact `#E+#E'` proof, AR-3, C-TWIST, and the n=15/17/19 selected cells. Retain the original frozen specification as provenance.
- **Execution limits and stop condition:** Arithmetic/protocol correction only; no solver or relation search under an unresolved contract. Stop if the proposed control still requires a cofactor-four curve while AR-3 remains unchanged.
- **Outcomes and next actions:** A complete, runnable correction permits normal approval and a frozen Stage-1 run. An incomplete cofactor-four criterion keeps C-TWIST unevaluable. A different admissible control requires its own falsification rule and must be reviewed before execution.
- **Recheck trigger:** A committed Coordinator correction and independently checked implementation for its chosen route.

A planned correction is not a completed experiment. Existing execution,
review, budget, and archival rules still apply.

## Resolution and history

Unresolved. This record names an exact conflict in the frozen protocol; it
changes no goal, hypothesis, or experiment status.
