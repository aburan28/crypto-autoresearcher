# Research problems and obstructions

Track the major named blockers that prevent a research claim, proof step,
implementation, experiment, or audit conclusion from being established.
The [agent rule](../AGENTS.md#name-the-obstruction) requires each record to
explain the gap and what would let the work move past it.

## Index

| Problem | Status | What it blocks | What would unblock it |
| --- | --- | --- | --- |
| [EigenX/CEST EndRing reduction is not established](eigenx-cest-endring-reduction-not-established.md) | investigating | An EndRing-based confidentiality theorem or completion claim; BATCH-d92210 archived with zero survivors (M1 gap, M2 exact-syntax break); novelty, QPT/QROM and Cat-5 obligations remain open | A reviewed, correctly directed reduction on the exact real-key distribution, including any adaptive OneEnd bridge, or a replacement construction whose six scheme obligations are discharged; quantum and concrete-category claims need separate evidence |
| [Koblitz vertical isogeny maps are not persisted](koblitz-vertical-isogeny-maps-not-persisted.md) | open | K-163/K-283 endpoint rho and transported-action tests | One explicit map/dual, subgroup certificate, and matched cost measurement |
| [m=51 deep volcano levels are not constructed](m51-deep-volcano-levels-not-constructed.md) | open | Rho measurements and vertical-transfer tests at `f_E=120,871` and `f_E=271*120,871` | Certified endpoint models and sampling frame; explicit adjacent map/dual certificates for transfer claims |
| [P-224 degree-3 point maps are not certified](p224-degree3-point-maps-not-certified.md) | open | Complete P-224 component and subgroup-transfer tests | Explicit map/dual pairs, conductor labels, graph closure, and recovery checks |

## Add or update a problem

1. Check this index and the affected work for an existing record. Reuse it when
   the obstruction is the same; link the canonical record across repositories
   rather than duplicating its evidence.
2. Copy [TEMPLATE.md](TEMPLATE.md) to a stable, descriptive filename such as
   `subgroup-preserving-transfer-not-established.md`. Name the mechanism or
   missing obligation, not a vague "hard problem". The filename above is an
   illustration, not a recorded finding.
3. State the exact blocked task or claim and its parameters, assumptions, and
   acceptance criteria. Separate evidence from conjecture and cite durable
   artifacts, proofs, reproductions, or source records.
4. Specify the evidence or capability needed to move past the obstruction and
   one concrete next experiment or proof obligation that can distinguish
   explanations. Link an existing execution protocol where applicable; this
   record does not replace it or impose a new campaign spending cap.
5. Add the index row and link the problem from the affected note, plan, audit
   finding, or PR. Update these pointers and the record together as work lands.

Use this directory for consequential or recurring blockers. Routine defects
and TODOs can stay in their existing trackers. Record a blocker even when its
cause is unknown; explicit unknowns are useful, invented explanations are not.

## Status and evidence

- `open`: the obstruction remains and its next action is recorded.
- `investigating`: work on that action is underway; link the task or run.
- `resolved`: linked evidence meets the stated exit criteria for this specific
  obstruction. State any remaining limitations.
- `superseded`: a linked successor now tracks this obstruction; this is not a
  claim that it was solved.

These statuses describe the problem record, not the scientific status of a
hypothesis or the completion of a campaign. Stopping work does not resolve
a problem or authorize abandoning the user's requirement.

Keep observations, calculations, hypotheses, resource/access/assistance gaps,
and proved limits distinct. Bound a negative result by its exact inputs and
search limits. A resource ceiling, missing implementation, or failed search
does not establish a mathematical obstruction or a security theorem.

Preserve historical evidence and append dated updates explaining corrections.
A resolution cites its evidence and the criteria met; a supersession cites its
successor and the reason for replacing the record. Follow the repository's
existing review, archival, and claim-promotion rules.

In this repository, problem records complement the existing
[`GOAL-*` impediments](../AGENTS.md#goals-are-never-paused) and
[inventor-protocol obstruction requirements](../docs/inventor-protocol.md).
Link the relevant impediment, task, experiment, and decision IDs; retain their
existing fields and authority. Problem status does not change a goal's status,
approve an experiment, retire a direction, or promote a claim. An impeded goal
remains `active`; scientific transitions still require the established
Coordinator decision and evidence.
