# [Specific name of the obstruction]

- **Status:** `open` (`open`, `investigating`, `resolved`, or `superseded`)
- **Kind:** [unknown cause, proof gap, empirical bottleneck, implementation gap,
  access/tool limit, assistance restriction, resource limit, or proved obstruction;
  separate multiple kinds]
- **Affected work:** [links to tasks, claims, proof steps, protocols, or audit findings]
- **Next action owner:** [person, role, task, or explicitly unassigned]
- **Last updated:** [YYYY-MM-DD]

## Problem

[In one sentence: we cannot yet establish or accomplish X because Y is missing
or fails under Z. If the cause is unknown, say so.]

[State the construction, curve/subgroup or other instance identity, parameter
range, threat model, assumptions, workload, and original acceptance criterion
where relevant. Explain exactly why this gap blocks the affected work.]

## Evidence and uncertainty

- **Observed:** [results or failures with artifact paths, source revisions,
  commands, input identities, controls, and actual resource/search limits;
  link existing run records rather than copying large logs]
- **Derived or proved:** [argument or proof, with its hypotheses and exact scope;
  otherwise "not established"]
- **Suspected explanation:** [explicitly labeled conjecture and what would
  distinguish it from alternatives; otherwise "unknown"]
- **Missing capability:** [implementation, measurement, proof, access, or resource
  that is unavailable; otherwise "none identified"]
- **What this evidence does not establish:** [limits on inference and transfer;
  timeouts, bounded searches, and missing measurements remain such]

## What would unblock it

[Name the required lemma, construction, executable map, implementation,
measurement, independent verification, access, or resource.]

- [ ] [Concrete, checkable acceptance condition, including parameters, metric,
  threshold, and correctness/replay evidence when applicable.]
- [ ] [Additional condition only if necessary.]

[Explain whether these conditions are necessary or sufficient, what meeting
them would establish, and which downstream obligations would remain.]

## Next discriminating step

- **Action or proof obligation:** [one concrete step; link its task or protocol]
- **Inputs and controls:** [fixed instances, reference, and alternative explanations]
- **Execution limits and stop condition:** [scope, resource envelope, or existing
  protocol limits where applicable; do not invent a campaign spending cap]
- **Outcomes and next actions:** [what success, a bounded negative result,
  inconclusive evidence, or an infrastructure failure would each change]
- **Recheck trigger:** [new evidence, capability, dependency completion, or date]

A planned step is not a completed experiment. Apply the existing execution,
review, budget, and archival rules before acting on it.

## Resolution and history

[Append dated evidence and next-action updates here. Preserve frozen artifacts
and explain corrections instead of silently rewriting prior conclusions.]

[For `resolved`, link the evidence satisfying each exit condition and state
remaining limits. For `superseded`, link the successor and explain why.
Otherwise state "Unresolved". Completing this record or merging its PR
does not establish a research result.]
