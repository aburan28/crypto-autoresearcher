# Review Lean artifacts and proof workflows

Use this route for a supplied theorem, a proof map, retrospective proofs, or a
Lean-related skill/verifier. It performs a technical evidence review without
requiring an experiment. Official evidence decisions and hypothesis/knowledge
promotion retain the experiment route's Coordinator, archive and review gates.

## 1. Bind the claim and inputs before review

Record the producer's exact claim, source revision and location, theorem/module
names, hypotheses and quantifiers, proof-map rows, Lean toolchain, dependency
manifest, source hashes, and cited build/audit receipts. For a workflow, also
bind its skill, adapter, entry point, gate and relevant CI configuration.
Use committed, pushed immutable inputs, including unmerged PR head SHAs where
appropriate. Review from current `main` ledger state in a separate worktree if
the producer branch is stale. Preserve the producer snapshot; do not merge
new code into it and call the old receipt current.

Write a `review_plan` before dispatch: the Coordinator's prior, one owner per
load-bearing joint and a worked attack, mutual blindness, known-false controls,
and a blind re-derivation from the statement and parameters alone. Use the
handoff and independence contracts in `AGENTS.md` and
`templates/research-records.md`. If the Coordinator authored a proof, they may
organize and repair it but cannot supply its independent fidelity verdict.

Use separate reviewer sessions under `review-adversarial`; a breakthrough,
closure or contradiction between validated claims retains `review-breakthrough`.
Bind each handoff to an archival task and publish inputs before dispatch.
Keep each reviewer's output in its own task directory. The Coordinator composes
their findings only after receiving the required reports.

## 2. Check machine verification

Rebuild the actual theorem modules on the exact pins using the repository's
existing verifier or proof gate. For autoresearcher, use
`autoresearch formal verify --task-file ... --artifact-out <fresh-path>` or
`tools/verify_formal_targets.py`; for consumer Lake projects, run their pinned
gate. Retain commands, exit statuses, stdout/stderr and source/input hashes in
new evidence paths. Check the exact named declaration, not just a project root
that might omit its module. Run `#print axioms` and a fail-closed transitive
axiom audit for all cited theorems; use `lean4checker --fresh` when available.

A default `lake build` may omit a source module. Build each cited module
explicitly (`lake build +Module.Name`), and reconcile the tracked source
inventory with the gate's source/module list. The shared gate's complete-source
version attempts each tracked project source as a Lake source target.
Unregistered auxiliary sources compile into a private directory and are audited
too, without changing frozen Lake configurations. Any source build failure fails
the gate. Lake configuration, the gate tools and deliberate
self-test fixtures are explicit exclusions, never silently counted as proofs.
An older gate that lists only existing `.olean` files cannot establish source
coverage. A named audit covers its named declarations, not all adjacent files.

Retain the CLI's complete local `workspace_inputs` and `verifier_inputs` in
new receipts, and compare them before and after verification and on reuse.
This binds imported helpers, audit code and Lake configuration, including
created/deleted files and configured hidden source directories; four hashes for
only the target/spec/pins are insufficient. Only `.git`/`.lake` infrastructure
is excluded from the local snapshot. Check that configured local source roots
are inside the immutable workspace and outside these excluded directories.
Dependency binaries retain Lean/Lake's trust boundary: record exact dependency
pins and clean installed revisions, and disclose the absence of an independent
binary/kernel rechecker. Pre/post hashes do not prove absence of a transient
concurrent edit; use an isolated immutable input tree.

Receipt validation checks consistent task/result identities, forbidden-construct
flags, versions, source/verifier inputs and nonempty audit evidence. It does
not authenticate execution: a fully fabricated JSON can contain fabricated
hashes and logs. Fresh Lean checks are mandatory for this review route, even
when an archived receipt passes every consistency check. Preserve legacy
receipts, label their narrower provenance and create new evidence paths.
When reviewing an older verifier run, select its exact reviewed revision
explicitly (`--verifier-revision <SHA>`) and match the recorded verifier bytes
to that Git tree. Never attribute later input-binding repairs to an older run.
Both main-workspace counted audits and scoped zero-axiom audits are supported;
neither log format authenticates execution by itself.

Reject unapproved axioms, holes, kernel bypasses and unverified native
evaluation as ordinary theorem proofs. Report deliberate compiler-trust
exceptions explicitly, never as kernel-only verification. A missing toolchain,
cache or service is `infrastructure_error`, not a refuted theorem. A missing
proof is `not_verified`; an old receipt whose hashes no longer match is stale.

`Decidable` instances and definitions are data, not theorem declarations. A
theorem-only target audit must keep that check: expose the actual executable
instance and a proposition stating its soundness/completeness. Do not weaken
the verifier to accept an arbitrary constant. Tests of a verifier show the
instrument's behavior, not the truth or fidelity of a research theorem.

## 3. Review semantic fidelity independently

For every cited declaration, compare its elaborated type with the source claim:

- quantifier order, universes, uniformity and exceptional/empty cases;
- exact field, characteristic, modulus, curve, subgroup and finiteness;
- genuine algebraic laws and the connection to concrete mathematical objects;
- forward and reverse implications when the source states an equivalence;
- surjectivity, injectivity, nonzero denominators, degree coprimality and
  reverse-map identities, identifying which are proved and which are assumed;
- executable certificate predicate versus a single hard-coded example,
  mathematical decidability versus an efficient checker, and typed valid
  points versus a parser of untrusted serialized coordinates;
- satisfiability/nonvacuity of assumptions, circular hypotheses, assumed
  conclusions, omitted hypotheses and an arithmetic lemma substituted for
  geometric, algorithmic or security content;
- all required bridges: scalar models to point groups, homomorphisms to
  isogenies, abstract additive structures to actual groups/Jacobians, and
  symbol-level operations to implementation code.

List missing bridges individually. A conditional theorem may be faithful to a
conditional claim; it cannot certify an unconditional or concrete claim whose
assumptions were never established. A theorem about a formula does not prove
that the formula measures the cited run or establishes its performance.

## 4. Attack the proof boundary and the workflow

Run positive controls and known-false nearby cases. Remove or mutate the
load-bearing assumption and obtain a checked counterexample or a concrete
failure to apply the theorem. Distinguish an expected elaboration failure
from a mathematical counterexample, and an infrastructure failure from both.
Cover applicable exceptional cases such as zero denominators, composite
moduli, noncoprime degrees, empty tuples/bases and singular coordinates.

A blind re-derivation receives only mathematical definitions, the requested
statement and parameters. It may not read producer code, proof text, reports,
receipts or sibling verdicts. Record permitted and forbidden paths in the plan
and actual reads in the attestation. Do not call ordinary replay independent
derivation. Use an isolated, minimal input snapshot when histories or adjacent
files would reveal the producer's answer.

For a Lean skill or tool, trace the documented command to the actual entry
point and gate. Verify module discovery, named-declaration handling, pin and
hash checks, failure propagation, empty-audit rejection, trusted-axiom handling,
and CI coverage. Demonstrate that wrong names, holes, custom axioms, stale
inputs, omitted modules and fake/empty success evidence are rejected by the
relevant existing controls. Disclose any untested interface or unsupported
failure mode. Never record a new passing test as a semantic proof.

## 5. Record separate verdicts and reconcile findings

Keep three dimensions separate for each claim:

| Dimension | Values | Meaning |
| --- | --- | --- |
| Machine status | passed / failed / not_verified / infrastructure_error | The exact declaration and inputs were checked by the named tool |
| Fidelity | faithful_scoped / partial / mismatch / not_reviewed | Independent comparison with the producer's claim, including model bridges |
| Review outcome | validated_scoped / needs_revision / inconclusive | The review's result over its expressly enumerated scope |

`validated_scoped` requires passing machine evidence, independently supported
`faithful_scoped` correspondence, satisfiable assumptions or an explicit
justification, and all required controls and reviewer attestations. A partial
bridge, missing reviewer, stale receipt, failed control or unreviewed theorem
prevents that outcome for the affected claim. Different claims in one batch
may receive different verdicts; never replace that table with an approval vote.

Reviewers provide `review_attestation` with their own `joints_owned`, complete
`sources_read`, sibling-report access, blind-rederivation compliance and
`holds | breaks | inconclusive` verdicts. Run
`tools/check_review_independence.py` on the precommitted plan and reports.
That tool checks the declarations, not the truthfulness of session isolation.
Retain failures. A correction is a new producer version and a new verification
and affected-joint re-review, never an edit to an earlier signed-off artifact.

## 6. Archive and report

Keep the technical review packet, source-linked per-claim table, machine logs,
controls, independent reports and attestations, unresolved obligations and
next actions together. Include a diagram and an inspected report PDF per
`research-visuals`; pure proof reviews need no invented performance chart.
Describe any protocol deviations. Publish via a PR and return its link.

A technical packet changes no hypothesis or official evidence status by
itself. When the user requests promotion or the review warrants an official
scientific transition, dispatch the Coordinator and use the existing evidence,
decision, knowledge-promotion and ledger-archive rules. Preserve existing
`proof_status` enums; link the Lean packet through `proof_refs` rather than
inventing a machine-verified ledger tier. A workflow correction alone is not
a refutation of its subject theorem.
