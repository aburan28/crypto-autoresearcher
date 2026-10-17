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
| [PR merge checks are not enforced on main](pr-merge-checks-not-enforced.md) | open | Contract-compliant pre-merge check gate, including required progress-fidelity CI; late-check merges recurred through #2341 | Authorized Actions and main protection settings, then a controlled PR proving pending/failed checks block merge |
| [Full-width IC arity grid has no complete measurement](full-width-ic-arity-grid-unmeasured.md) | investigating | Verified 50–63-bit prime/Koblitz/ordinary-binary end-to-end baseline and m=2–8 candidate comparison; exact fixtures, a 316-column weighted binary base, same-width local random control, matched four-channel m=8 XCNF inputs, an older planted point certificate and representation ceilings are prepared | Run matched candidate/control solving with complete lift/sign/pole handling; then measure useful rank, full phase costs, censoring, matched rho and independent replay |
| [Direct binary subfield x base has zero large-prime component](binary-subfield-base-has-no-large-prime-component.md) | open | Exact subfield closure cannot supply target-subgroup rank on a descended 50–63-bit binary curve when the target prime exceeds the proved Hasse ceiling | A target-blind near-subfield or other sparse base with independently checked subgroup projection and rank, then a complete-cost comparison |
| [Affine Weil-descent fixture and solver admission](affine-weil-descent-byte-identity.md) | investigating | EXP-ICPERF-42ef30 AP-2 and Stage 2 affine factor-base solver comparison; 60/60 shipped byte matches now recorded | Independent selected-slice checks and per-cell WDSat parser/MAX_ID admission |
| [Binary twist control conflicts with the cofactor-two admission rule](binary-twist-cofactor-stage1-conflict.md) | open | EXP-ICPERF-42ef30 Stage-1 C-TWIST cannot satisfy AR-3 on a quadratic twist of any admitted binary curve | Coordinator correction to the control/admission rule with an independent landing criterion or an admitted replacement control |
| [ICPERF D6 archive commit is unreachable from main](icperf-d6-archive-commit-unreachable.md) | investigating | Verified dispatch and closure of the D6 correction lane after PR #2084 | Reachable prospective archive binding, dispatcher replay, and merge-method check |
| [Historical selection rule for skipped NIST prime-field seeds](nist-seed-selection-rule-unexplained.md) | open | Explaining why eleven qualifying candidates in recovered timestamp streams were omitted | Provenanced original code/logs and exact replay, or a predeclared predictive reconstruction with independent historical validation |
| [Prescribed execution is not enforced through the proof chain](execution-proof-chain-not-enforced.md) | open | Cryptographic execution integrity from frozen protocol through raw results, evidence and Cairn settlement/audit | Real proofs for the walk/count pilots, independent audits in both Cairn implementations, all promotion bindings, adversarial controls and a scoped cost report |
| [Experiments reported ready are refused by the supervisor's archive-coverage check](ready-plans-lack-supervisor-archive-coverage.md) | open | 17 of 18 `ready` experiments; the run selector's ranking | Selector applies `authorize()`'s coverage rule; Coordinator supersedes the 17 queues |
| [Prime-field arity-3 relation-yield panel and shared Coordinator access limit](prime-field-arity3-relation-oracle.md) | investigating | EXP-ECTD-0cf008: 3 validated arms, 13 infrastructure failures, 4 unlaunched arms; the unavailable Coordinator backend also gates ICPERF N53 integration and use of the now verified larger-field Koblitz subgroup fixtures | Verify a policy-compliant Coordinator backend; freeze the separate ECTD recovery and ICPERF baseline/candidate handoffs, then apply each experiment's admission and review gates |
| [Graph-wide isogeny relation study lacks an admitted collector and complete solve path](isogeny-graph-wide-relation-solver.md) | investigating | P29 full 2,048-edge transport and P37 edge-20 prefix passed independent replay; 128 public first-check target counts matched, while graph-wide yield, rank, and complete same-point ECDLP costs remain unmeasured | Finish P37 edges 21–256 and discovery-stream equality, admit and run the fixed collector schedule, then complete independently replayed finalist solves with full costs |
| [250-billion point-data storage](solinas-250b-storage-unavailable.md) | investigating | Full compact retention for later arbitrary ML; aggregate campaign selected October14 | Larger writable storage or configured S3 upload/checksum identity; aggregate mode preserves the fixed count-based inference |
| [EigenX/CEST EndRing reduction is not established](eigenx-cest-endring-reduction-not-established.md) | investigating | An EndRing-based confidentiality theorem or completion claim; BATCH-5313dc and BATCH-3e1bfd both archived with zero survivors, and the endpoint-fiber raw XOR syntax has an exact CCA break; novelty, QPT/QROM and Cat-5 obligations remain open | A concrete endpoint-fiber law and nontrivial label/evaluator pair, or a reviewed correctly directed reduction on the exact real-key distribution; every replacement still needs six-obligation, quantum, and concrete-category evidence |
| [Koblitz vertical isogeny maps are not persisted](koblitz-vertical-isogeny-maps-not-persisted.md) | open | K-163/K-283 endpoint rho and transported-action tests | Finish an admitted K-163 or K-283 forward-map gate, then certify its dual, subgroup recovery, and matched full cost |
| [m=51 deep volcano inference and maps remain open](m51-deep-volcano-levels-not-constructed.md) | open | Release of four-level inference and vertical-transfer tests across the factor-120871 gap | A fresh frozen replication whose control gate passes; explicit adjacent map/dual certificates for transfer claims |
| [P-224 degree-3 point maps are not certified](p224-degree3-point-maps-not-certified.md) | open | Complete P-224 component and subgroup-transfer tests | Explicit map/dual pairs, conductor labels, graph closure, and recovery checks |
| [Hom degree forms finite-field certification](lattice-hom-degree-forms-finite-field-certification.md) | open | EXP-ENDO-371597 finite-field lift and independent certification; RUN-ENDO-859fbd synthetic pilot complete | Certified maps from ordinary finite-field Hom bases; independent review receipt |
| [Order saturation finite-field certification](lattice-order-saturation-finite-field-certification.md) | open | EXP-ENDO-854769 finite-field lift and independent certification; RUN-ENDO-910c24 synthetic pilot complete | Certified maps from ordinary finite-field bases; independent review receipt |
| [Quaternion lattice volume finite-field certification](lattice-quaternion-volume-finite-field-certification.md) | open | EXP-SSI-39bae9 finite-field lift and independent certification; RUN-SSI-5a435c synthetic pilot complete | Certified supersingular maps from supplied Hurwitz orders; independent review receipt |
| [Transport denominators finite-field certification](lattice-transport-denominators-finite-field-certification.md) | open | EXP-ENDO-aec0b2 finite-field lift and independent certification; RUN-ENDO-4d758c synthetic pilot complete | Certified maps from ordinary finite-field bases; independent review receipt |
| [Lattice index-calculus relation construction](lattice-index-calculus-relation-construction-not-demonstrated.md) | open | RQ-IC-a39c7e: usable relation density, independent rank and complete cost; pairing/factor-base/combined observations are unreviewed; polynomial serialization failed before saved output | Complete the polynomial successor and independent mathematical/cost review; no generic speedup established |
| [Polynomial integer-HNF transformation memory growth](lattice-ic-integer-hnf-memory-growth.md) | investigating | EXP-IC-74cbb1 failed before serialized results; polynomial and dependent combined execution | Bounded exact HNF with two-way Z-membership, unchanged criteria/caps/resources, and a fresh native-admitted successor run |
| [Lattice IC blind Reviewer session continuity](lattice-ic-blind-review-session-continuity.md) | investigating | Same-Reviewer later comparison after lost runtime access; source support verified, original history contaminated | Fourth successful archive, refreshed scoped history check on clean isolated tree, new independent blind7 and verified archive8 before same-session gated comparison |
| [Polynomial claim authority and durable progress](lattice-ic-polynomial-lease-progress-observability.md) | investigating | Prior EXP-IC-66c447 expired; EXP-IC-9f9a4b telemetry identifies later serialization failure, no complete output | Retain actual failed terminal custody; separate serialization-memory remedy owns next step; full-grid/checker and independent review remain pending |
| [PKM isogeny-chain factor base has no fast decomposition](pkm-isogeny-chain-factor-base-no-fast-decomposition.md) | open | The proposed ~N^(1/3) P-256 route via a 2-isogeny-chain factor base (EXP-ECDLP-f49f75 Singular + EXP-ECDLP-502ae2 msolve F4: chain slower than dense/random at every toy cell) | A solver beating the dense and random controls on the frozen toy grid (e.g. block/elimination order), or an L-independent degree-of-regularity bound |
| [Exact artifact serialization memory](lattice-ic-artifact-serialization-memory.md) | investigating | Historical artifact MemoryError under2GiB; bounded software controls/report8/source3 verified, fresh currentclosure5 native proof awaiting publication; full-grid/checker memory unknown | Publish currentclosure5 proof, then fresh full-science-equal native admission/full-grid/checker and independent review |

| [Lattice IC runbook sparse output admission](lattice-ic-runbook-sparse-output-admission.md) | investigating | Native prelaunch refusal despite READY/LINT; stopped book session6/report5 retained/native verified, no RUN/scientific process | Publish report5 proof, then fresh same-science admission with native selected-experiment materialization before launch |

| [Ten lead formal model bridge and raw artifact access](ten-lead-proof-scope-and-artifact-access.md) | investigating | Applying generic formal statements to concrete curve/domain claims and replaying private raw evidence from a public checkout | Independent semantic review, checked concrete-model bridges, and authorized artifact access |

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

- [Compact candidate selection and incomplete certificate instance](compact-isogeny-candidate-selection.md) — M8191 raw rejection retained; fresh M44497 native gate pending.
