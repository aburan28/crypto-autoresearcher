# k11 target admission does not bind the torsion pole gamma

- **Status:** `open`
- **Kind:** specification gap; independent reproducibility gap. No mathematical obstruction is claimed.
- **Affected work:** [EXP-ICPERF-018b0c](../experiments/EXP-ICPERF-018b0c/specification.yaml), [H-ICPERF-195806](../ledger/hypotheses/H-ICPERF-195806.yaml), [EV-ICPERF-54ac6b](../ledger/evidence/EV-ICPERF-54ac6b.yaml), [DEC-20261017-3b87bf](../ledger/decisions/DEC-20261017-3b87bf.yaml), [full-width IC grid](full-width-ic-arity-grid-unmeasured.md).
- **Next action owner:** Coordinator for a prospective successor specification and blind review plan; Executor only after an approved and admitted protocol.
- **Last updated:** 2026-10-17

## Problem

The frozen k11 m=8 ordinary-binary target schedule cannot be uniquely reconstructed from the documents permitted to blind reviewer J0. The specification's admission rule rejects `x=gamma` as the pole of `t=gamma/(x+gamma)`, but neither that specification nor the curve fixture explicitly defines `gamma` symbolically or numerically. Thus a reviewer can reproduce the archived eight-target panel under one natural interpretation while another literal pole value changes which candidates are admitted. This prevents a blind, statement-only proof of the common-target schedule required by REVIEW-ICPERF-20261017-b5d54d. It does not invalidate the archived prepared inputs by itself or establish anything about relation yield.

The exact fixture is `y²+xy=x³+31` over GF(2^61) represented by `x^61+x^5+x^2+x+1`, with prime subgroup order 576460752557211763. The pilot has two target-blind B=316 bases, eight summands via seven chained S3 equations, eight admitted public subgroup targets, four raw channels per target and 64 planned natural solver calls. Both planted solver controls were wall censored at 300 seconds, so the natural panel was never attempted; that independent instrument limit remains even if gamma is clarified.

## Evidence and uncertainty

- **Observed:** The [blind J0 report](../coordination/review/icperf-20261017-018b0c/TASK-20261017-93d17d/report.md) and [blind counts](../coordination/review/icperf-20261017-018b0c/TASK-20261017-93d17d/blind_counts.json), content-first archived by TASK-20261017-46f47f, derive `T=[r]P_source=(70364449406991,2147483661)`. Its x coordinate equals the unique fourth root of b=31, `gamma=70364449406991`. Under that interpretation counters 0–7 are admitted and the 66 labels match the prepared manifest. Independent J1 arithmetic under the same interpretation matches all 32 prepared raw channels and 64 target constants; see [J1–J4 report](../coordination/review/icperf-20261017-018b0c/TASK-20261017-b5d54d/review_report.md).
- **Discriminating ambiguity:** J0 used `gamma=714891581849174975`, the first raw channel's x coordinate, as an alternative literal value of the otherwise unbound symbol. It rejects counter 0 as a pole and admits counters 1–8. This counterexample is to *unique derivability from the allowed documents*, not to the arithmetic of the archived panel. The changed domain-separator control also changes the first scalar, and the derived pole point T is rejected by the point map.
- **Archived outcome:** [EV-ICPERF-54ac6b](../ledger/evidence/EV-ICPERF-54ac6b.yaml) and [DEC-20261017-3b87bf](../ledger/decisions/DEC-20261017-3b87bf.yaml) classify J0 as inconclusive. The two planted calls in RUN-ICPERF-712e85 were wall censored; RUN-ICPERF-1c8bfe attempted zero of 64 natural calls. No natural relation or degree-of-regularity inference follows.
- **Derived or proved:** The supplied frozen specification and fixture do not select a unique value for gamma. The reviewer supplies two distinct admission schedules consistent with that omission. This is a finite specification-identifiability statement, not a proof about factor-base quality or solver feasibility.
- **Suspected explanation:** The author intended the conventional torsion-coordinate definition `gamma=x([r]P_source)=b^(1/4)` but relied on implementation/manifests to supply it. This intent is an inference, not an additional frozen rule.
- **Missing capability:** A prospectively frozen, exact symbolic and numeric gamma binding in the statement/fixture available to a blind reviewer, plus independently replayed schedule and altered-object controls.
- **What this evidence does not establish:** It does not show that any prepared XCNF is wrong, that a point relation is absent, that the two bases differ in yield, or that an ECDLP pipeline is faster. The separate [execution-proof-chain problem](execution-proof-chain-not-enforced.md) remains open.

## What would unblock it

- [ ] A new prospective contract or immutable allowed fixture states `gamma` as the unique fourth root of b=31 and as `x([r]P_source)`, fixes its value 70364449406991 under the named GF(2^61) basis, and states the exact pole predicate for all four raw channels. Freeze its byte hash before any successor target or solver work.
- [ ] A reviewer who reads only that new statement and fixture independently rederives `T`, scans at most j=0..1023, obtains the first eight admitted targets and all 32 raw channels, and reproduces the exact 66-label schedule without reading prepared manifests or producer code. The same reviewer checks a changed domain separator and rejects T at the pole. An alternate-gamma control must demonstrably change admission, including counter 0 versus counters 1–8 for the J0 example.
- [ ] A separately scoped checker compares the frozen target/formula manifests to that blind derivation, including every target constant and hash, before a newly approved solver panel. Any mismatch is an input-preparation defect, not a relation result.

These conditions would establish unique prospective target admission and prepared-input consistency for that successor fixture. They would not establish positive solver certification, natural relation yield, useful rank, degree of regularity, whole-pipeline cost, or rho distance.

## Next discriminating step

- **Action or proof obligation:** Freeze the gamma definition in a new contract, then run a *read-only, no-solver* blind schedule derivation under a new review plan before any successor panel is admitted.
- **Inputs and controls:** Same certified curve, source point, subgroup order, target domain and j=0..1023 scan as the archived pilot; the bound gamma and field basis; changed-domain separator, pole point T and alternate-gamma admission controls. The archived v1 manifests are comparison material only after the blind derivation is sealed.
- **Execution limits and stop condition:** At most 1024 candidate counters, eight admissions and 32 raw channels; no SAT or ECDLP trial in this control. Stop and mark input preparation invalid on a mismatched field representation, gamma, point, pole predicate or target constant.
- **Outcomes and next actions:** Exact blind agreement clears this specification gap for the successor only and permits normal approval/admission checks. A mismatch requires a new input/contract correction and preserves both schedules. An inconclusive reviewer read or implementation failure leaves the gap open. None of these outcomes alone changes the pilot's scientific verdict.
- **Recheck trigger:** A newly frozen gamma-bound contract and committed blind replay, or evidence that another admitted definition yields the same complete schedule.

## Resolution and history

2026-10-17: Opened from the independently archived J0/J1 review and the Coordinator's inconclusive DEC-20261017-3b87bf. The v1 specification, input manifests, run records and review reports remain immutable. Unresolved; filing this record does not meet its exit criteria.
