# Historical Lean coverage and semantic correspondence remain incomplete

- **Status:** open
- **Kind:** formalization gap; semantic-review gap; incomplete prose-claim inventory
- **Affected work:** [three-repository retrospective](../research/lean_retrospective_20261018/README.md), all past claims requested by the owner on 2026-10-18
- **Next action owner:** unassigned formalization and independent-review tasks
- **Last updated:** 2026-10-19

## Problem

We cannot certify every historical claim across crypto, cryptanalysis and
crypto-autoresearcher: no complete claim-by-claim prose inventory has yet been
matched to checked Lean declarations and reviewed bridges to the concrete objects.
An inventory of source paths and a green proof gate do not provide that match.

## Evidence and uncertainty

- **Observed:** the three study inventories bind the starting Git revisions.
  Crypto has 98 Lean paths excluding self-test fixtures and 19 Lake projects;
  autoresearcher has 66 frozen formal target specs, four initially without
  source; cryptanalysis initially had no research Lake project.
- **Derived or proved:** new module builds, transitive axiom audits, and
  per-target autoresearcher receipts are linked from the study proof maps.
  Their guarantees cover the stated models and hypotheses only.
- **Suspected explanation:** none needed; missing coverage is an implementation
  and review obligation, not evidence of mathematical falsity.
- **Missing capability:** complete historical claim extraction, outstanding
  formalizations, concrete model bridges and independent semantic-fidelity
  review. Historical empirical claims additionally require execution evidence
  and replay; a theorem about a cost formula cannot establish a measured speedup.
- **Limits:** snapshots cover current default-branch source, not every earlier
  Git revision or prior conversation. Existing frozen evidence is preserved.

## What would unblock it

- [ ] Enumerate each historical claim in its author's words, with immutable
  source revision and location, and split compound claims.
- [ ] Classify each claim as mathematical, empirical, conditional, conjectural,
  refuted, or not yet supported; never force an empirical or false statement
  into a fabricated proof.
- [ ] Link each mathematical claim to its exact Lean declaration, hypotheses,
  toolchain, dependency pins, build and transitive axiom receipt.
- [ ] Complete outstanding formal targets and concrete geometric/group bridges,
  including the exact two-direction shadow reachability formula, rather than
  replacing them with weaker nearby lemmas.
- [ ] Obtain independent semantic review, including exceptional cases and
  proves-too-much controls, for every claimed correspondence.
- [ ] Reproduce empirical claims with their original workloads and evidence
  contracts; keep runtime, asymptotic and security conclusions separately scoped.

These conditions would establish the stated retrospective coverage. They would
not establish security of a deployed curve, a new attack, or an asymptotic gain.

## Next discriminating step

Formalize `formal/targets/ncp-reachability.yaml` from the full definitions in
`research/THM_COMMUTATOR_KERNEL1.md`. Prove both the length lower bound and a
word construction attaining it, including B=0, d=0 and mixed-sign coordinates.
The input is a word in translations and negation, not a measured cryptographic
run. A checked equivalence discharges that target; a build failure records a
formalization gap. Neither outcome changes scientific state without review.
Recheck this record when a new proof, concrete bridge, independent review, or
claim inventory is committed. No campaign spending limit is introduced.

## Resolution and history

Unresolved. The 2026-10-18 additions are a verified mathematical batch and a
coverage record, not closure of the owner's request for all historical claims.

### 2026-10-18 independent review update

[Separate reviewer reports](https://github.com/aburan28/crypto-autoresearcher/blob/aaccd2f5d0a801fd73209e2a51b587efbda3ee5e/research/lean_review_evidence_20261018/) support the 19 explicitly scoped
new declarations; every original mathematical or empirical claim is still not
covered. Concrete map/duality, cyclic-group implementation and C refinement
bridges remain unproved. The NCP target also states companion witnesses and
a surjectivity description beyond the single kernel-inequality witness.
The full reachability iff is still absent.

The workflow review identified omitted project modules, inconsistent summary
acceptance and incomplete imported-source provenance. Versioned gate/CLI/summary
repairs and their independent follow-up belong to the review packet. The old
receipts are retained; fresh matching receipts do not certify source-claim
fidelity or authenticate execution by themselves. The exit criteria above
remain open.

### Sealed workflow review and remaining coverage

The [sealed independent synthesis](https://github.com/aburan28/crypto-autoresearcher/blob/e792163f3b66b72ca7bac849459aa6eeeafc99bb/research/lean_review_evidence_20261018/synthesis.md) retains19 scoped
mathematical validations and the [independent compact closure](https://github.com/aburan28/crypto-autoresearcher/blob/712435bf2ad76da941291ac960f68c59d17a708f/research/lean_review_evidence_20261018/reports/TASK-20261018-2ea34a/publication/report.md)
reports44 passing workflow controls. This validates the exercised repair
boundaries, not all historical claim correspondence. It records the prior
workflow-attestation read deviation and the two local-only full raw bundles.
The missing reachability proof, concrete bridges, broader target clauses and
empirical replays above remain open; no exit criterion is closed by workflow
tests alone. Versioned status diagrams and semantic-review-v2 metadata point
to the current narrow review while preserving original frozen artifacts.


### 2026-10-19 foundation retrofit

The [new study](../research/lean_foundations_20261019/README.md) supplies the full
reachability equivalence with an explicit shortest word, actual additive-point
actions, the companion kernel witness, and a canonical cyclic encoding with
exact-order injectivity. The shared library additionally derives both rho
recovery branches from actual walk points and an explicit Bézout transport
inverse. New machine checks and independent review are tracked there; this
entry does not borrow the earlier 19-declaration verdict.

The broader inventory/empirical obligations and the full group/path-algebra
presentation and surjectivity clauses remain open. Concrete geometric maps,
point-order certificates for particular instances, parsers and C refinement
remain application obligations. The next step is to review the new exact
statements, then map additional historical claims and their required bridges.

Direct new edits to `aburan28/crypto` currently lack its required Conductor
task admission: the command and `.conductor/WORKFLOW.md` are absent in the
selected checkout and current fetched main. Reusable transport foundations
are implemented in `aburan28/crypto-lean` while that integration prerequisite
is unresolved. A working Conductor task/check and workflow file would unblock
the consumer pin update; this is an infrastructure limit, not a mathematical
obstruction. The earlier crypto PR remains separately tracked.
