# Uniform constructor for the generator-ordered half-root is missing

- **Status:** open
- **Kind:** proof gap and missing construction; not a proved impossibility.
- **Affected work:** [Non-generic continuation report](report.md), [proof-search map](proof-search-map.json).
- **Next action owner:** Coordinator / non-generic mathematical design lane.
- **Last updated:** 2026-10-26

## Problem

No uniform procedure has been supplied that constructs and evaluates the generator-ordered root A_P from public (E,P,r) below the intended complete solver cost. Interpolation proves existence by enumerating known scalar multiples; it does not supply the required algorithm.

The domain is ordinary prime-field E:y^2=x^3+ax+b, p>3, and a supplied odd prime subgroup of order r different from p. Let m=(r-1)/2, K_P=product_{j=1}^m(X-x(jP)), and specify A_P(x(jP))=y(jP), deg A_P<m. The required predicate recognizes canonical scalar halves. Setup, constants/advice, kernel construction, evaluation, bit costs, exceptions and scalar recovery remain charged. The original classical, non-generic objective is unchanged.

## Evidence and uncertainty

- **Observed:** source inspection found the completed pilot's bounded EDS grammar, enumerated orientation, coefficient diagnostics, and related orientation/period proposals. No new scientific run was made. The knowledge-index tools were not exposed.
- **Derived:** root congruence has 2^m solutions. Dense ordered-root output has degree at least ceil(m/2) for r>=11. The half predicate uniquely solves the stated two-pulse difference equation, and its values on doubled targets recover the scalar. These facts do not produce its constructor.
- **Derived control:** the anchored F11 circuit -f^3 satisfies the root equation, P anchor and negation covariance but fails at 3P; details are in the report. Correct roots alone are insufficient.
- **Suspected explanation:** unknown. High degree can have a short circuit, so the degree bound is not a circuit-size lower bound.
- **Missing capability:** an explicit uniform low-cost ordered-root / finite-coordinate antiderivative constructor.
- **Not established:** impossibility of all coordinate circuits, a new algorithm, novelty, an exponent improvement, or a scientific status transition.

## What would unblock it

- [ ] Supply a uniform public-input construction with a complete straight-line circuit or executable evaluator and a stated cost recurrence including constants and any preprocessing.
- [ ] Prove correct scalar ordering for every target in the declared family, including identity and point-addition exceptions; the root congruence and anchors alone do not meet this.
- [ ] Price construction plus O(log r) evaluations, point operations and final verification against the named baseline in its declared memory/reuse regime.

Meeting these conditions would establish an executable candidate and its claimed scope. It would not replace prospective protocol admission, correctness checks, matched performance evidence or independent scientific review.

## Next discriminating step

- **Action:** examine one supplied constructor against the exact two-pulse equation and the anchored F11 known-false circuit, before collecting a cohort.
- **Inputs and controls:** E/F11:y^2=x^3+x+6, P=(2,7), r=13; the explicit wrong circuit -f^3; identity and -P; generator and coordinate changes; the claimed constructor.
- **Execution limits and stop condition:** this note authorizes no run. No constructor is supplied, so no timing or parameter sweep is scheduled. Any mathematical failure is scoped to the exact proposed construction.
- **Outcomes:** a proved identity with a valid cost recurrence advances implementation design; a counterexample returns the exact construction for repair; a missing proof remains a proof gap. Missing software or a timeout is not evidence against the family.
- **Recheck trigger:** a specific uniform circuit/evaluator or a scoped circuit lower-bound argument is supplied.

## Resolution and history

2026-10-26: Unresolved. This is a draft in the assigned scratch scope. Before carrying it as a canonical handoff blocker, the Coordinator should place it under problems/ and add its index link. No historical evidence or official state was changed.

