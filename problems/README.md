# Research problems and obstructions

Track the major named blockers that prevent a research claim, proof step,
implementation, experiment, or audit conclusion from being established.
The [agent rule](../AGENTS.md#name-the-obstruction) requires each record to
explain the gap and what would let the work move past it.

## Index

This index does not assert that all repository obstructions are recorded.
Keep resolved and superseded records in the index.

| Problem | Status | What it blocks | What would unblock it |
| --- | --- | --- | --- |
| [250-billion point-data storage](solinas-250b-storage-unavailable.md) | investigating | Full compact retention for later arbitrary ML; aggregate campaign selected October14 | Larger writable storage or configured S3 upload/checksum identity; aggregate mode preserves the fixed count-based inference |
| [EigenX/CEST EndRing reduction is not established](eigenx-cest-endring-reduction-not-established.md) | investigating | An EndRing-based confidentiality theorem or completion claim; BATCH-5313dc and BATCH-3e1bfd both archived with zero survivors, and the endpoint-fiber raw XOR syntax has an exact CCA break; novelty, QPT/QROM and Cat-5 obligations remain open | A concrete endpoint-fiber law and nontrivial label/evaluator pair, or a reviewed correctly directed reduction on the exact real-key distribution; every replacement still needs six-obligation, quantum, and concrete-category evidence |
| [Koblitz vertical isogeny maps are not persisted](koblitz-vertical-isogeny-maps-not-persisted.md) | open | K-163/K-283 endpoint rho and transported-action tests | Finish an admitted K-163 or K-283 forward-map gate, then certify its dual, subgroup recovery, and matched full cost |
| [m=51 deep volcano inference and maps remain open](m51-deep-volcano-levels-not-constructed.md) | open | Release of four-level inference and vertical-transfer tests across the factor-120871 gap | A fresh frozen replication whose control gate passes; explicit adjacent map/dual certificates for transfer claims |
| [P-224 degree-3 point maps are not certified](p224-degree3-point-maps-not-certified.md) | open | Complete P-224 component and subgroup-transfer tests | Explicit map/dual pairs, conductor labels, graph closure, and recovery checks |
| [Hom degree forms finite-field certification](lattice-hom-degree-forms-finite-field-certification.md) | open | EXP-ENDO-371597 finite-field lift and independent certification; RUN-ENDO-859fbd synthetic pilot complete | Certified maps from ordinary finite-field Hom bases; independent review receipt |
| [Order saturation finite-field certification](lattice-order-saturation-finite-field-certification.md) | open | EXP-ENDO-854769 finite-field lift and independent certification; RUN-ENDO-910c24 synthetic pilot complete | Certified maps from ordinary finite-field bases; independent review receipt |
| [Quaternion lattice volume finite-field certification](lattice-quaternion-volume-finite-field-certification.md) | open | EXP-SSI-39bae9 finite-field lift and independent certification; RUN-SSI-5a435c synthetic pilot complete | Certified supersingular maps from supplied Hurwitz orders; independent review receipt |
| [Transport denominators finite-field certification](lattice-transport-denominators-finite-field-certification.md) | open | EXP-ENDO-aec0b2 finite-field lift and independent certification; RUN-ENDO-4d758c synthetic pilot complete | Certified maps from ordinary finite-field bases; independent review receipt |
| [Lattice index-calculus relation construction](lattice-index-calculus-relation-construction-not-demonstrated.md) | open | RQ-IC-a39c7e: usable relation density, independent rank and complete cost; pairing/factor-base/combined observations are unreviewed; polynomial successor running | Complete the polynomial successor and independent mathematical/cost review; no generic speedup established |
| [Polynomial integer-HNF transformation memory growth](lattice-ic-integer-hnf-memory-growth.md) | investigating | EXP-IC-74cbb1 failed before serialized results; polynomial and dependent combined execution | Bounded exact HNF with two-way Z-membership, unchanged criteria/caps/resources, and a fresh native-admitted successor run |
| [Lattice IC blind Reviewer session continuity](lattice-ic-blind-review-session-continuity.md) | investigating | Same-Reviewer later comparison after lost runtime access; source support verified, original history contaminated | Fourth successful archive, refreshed scoped history check on clean isolated tree, new independent blind7 and verified archive8 before same-session gated comparison |
| [Polynomial claim authority and durable progress](lattice-ic-polynomial-lease-progress-observability.md) | investigating | Prior EXP-IC-66c447 expired; new EXP-IC-9f9a4b running with durable boundaries, no complete output yet | Retain unchanged native attempt through actual terminal outcome and custody; full-grid/checker and independent review remain pending |
| [PKM isogeny-chain factor base has no fast decomposition](pkm-isogeny-chain-factor-base-no-fast-decomposition.md) | open | The proposed ~N^(1/3) P-256 route via a 2-isogeny-chain factor base (EXP-ECDLP-f49f75: chain encoding slower than dense/random controls at every toy cell) | A solver beating the dense and random controls on the frozen toy grid, or an L-independent degree-of-regularity bound |

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
