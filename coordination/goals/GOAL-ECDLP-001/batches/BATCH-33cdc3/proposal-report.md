# Lifting structural-audit proposals

Handoff: `TASK-20260905-f27236`. Goal: `GOAL-ECDLP-001`. Research question:
`RQ-ECDLP-002`. Date: 2026-09-05. Author role: idea-generator.

Three new proposals formalize the lifting discussion as bounded mathematical
audits. All remain `status: proposed`, `approved_by: null`, and
`novelty_status: unverified`. No experiment, hypothesis, approval or research
status transition was created, and no experiment was executed.

The motivating Satoh/Kedlaya question involves three distinct constructions:
Satoh's canonical curve lift, the cohomological lifting used by Kedlaya without
requiring that canonical curve lift, and unique prime-to-p torsion point lifting
on a fixed good-reduction lift. The parent retrieved the Maiga–Robert introduction
and Kedlaya abstract supporting this distinction; this author received that source
coverage from the parent and did not independently retrieve either paper.

| Proposal | Question | Existing overlap and method ceiling |
| --- | --- | --- |
| `IDEA-20260905-4dca34` | Does a declared coordinate observable use canonicality beyond ordinary torsion lifting? | Distinct from the global construction-cost scope of `IDEA-20260807-ee6ef7`; excludes the sign-fibre valuation already recorded in `KN-FIND-1ba0fe`. A result would classify one observable. |
| `IDEA-20260905-3e9133` | Which torsion-section deformation jets are coordinate artifacts, and what precisely does etale rigidity imply? | Follows the explicit lemma-audit guidance in rejected or merged `ECDLP-IDEA-109`; does not reopen scalar linearization by assertion. |
| `IDEA-20260905-8829cc` | What information does a specified marked cohomological object retain after auxiliary choices are accounted for? | Overlaps `ECDLP-IDEA-019`, `ECDLP-IDEA-114` and `ECDLP-IDEA-021`; proposes no cover decoder or path-based solver. |

The concrete candidate objects are now explicit. The first proposal compares
`F=x²/A mod p²` on a bounded panel of synthetic ordinary curves, three coefficient
perturbations and two model scalings. Its digit convention is declared separately
from invariance of the finite-ring value. The second audits the first-order
coefficient of the same expression over a dual-number base, including its
parameter-covariance law and a constant-family null. The third audits
`H1_dR(E,{P,Q})` for distinct rational marks, with a predicted dimension triple
`(3,2,1)` for the relative object, ordinary object and kernel. Its rank collision
is an intended null result; a Frobenius structure would require additional
compatible marking and coefficient data. All these statements are proposed
predictions or proof targets, not results obtained in this intake.

Each record declares its baseline, observation collisions, quantifier order,
coordinate or nearby-object controls, proof obligations, confounders, costs and
falsification scope. No probability model is assumed: `heuristic_assumptions` is
empty with an explicit explanation. Claimed improvements in time exponent,
memory exponent and data/query requirements are all zero. The full solver
frontier was not screened; `dominated_by` records that incompleteness explicitly
and is not an unchecked null.

These are prerequisites to assessing a possible representation advantage.
Nonconstant coordinates, a surviving invariant or dependence on a marked point
would not establish scalar recovery. A negative audit would constrain only its
frozen observable or construction. Missing proofs or unresolved transformations
remain inconclusive. No blanket lifting-method closure is proposed.

## Source and execution boundary

The author received direct-source inspection summaries from parent `/root` dated
2026-09-05. Every source citation is marked `internal` and attributes its inspection
to that parent; the author did not independently read the underlying files or
verify their experiment receipts. Parent supplied the role requirements and the
committed handoff scope. No callable `search_knowledge` tool was available; the
parent's direct `rg` and source reads supplied the retrieval substitute. This is
targeted overlap checking, not an exhaustive novelty search. No external paper
is cited as independently retrieved by this author.

The only author file operations created the three scoped proposal YAML files and
this report. The author executed no shell commands, experiments, schema validator,
commits or publication operations. Manual structural checking confirmed that all
three records contain the supplied required field families, complete
`proof_search_map` blocks and explicit provenance. Machine parsing, ledger and
identifier checks remain with the parent Coordinator; this report does not claim
they passed.

## Next harness step

After the Coordinator archives and validates these proposals, the open-idea
worklist can be inspected with `python3 tools/ecc_priority.py --open-ideas`.
The recommended first design target is `IDEA-20260905-3e9133`: its symbolic
transformation-law audit is cheap and clarifies how the proposed observable
should be interpreted before comparing canonical and arbitrary lifts. This is
a recommendation only, with no task assignment or approval.
Under the ECC policy, open proposals are candidates for `/design-experiment`,
which may create a hypothesis and a frozen contract. Designing does not approve
execution: any successor contract remains at `approved_by: null` until a committed
Coordinator decision approves it. This report assigns no work to an Executor.
