# Checker specification (preparation interface, EXP-CRYPTO-6505c6)

Status: unfilled interface. This document specifies what an independent checker
program or reviewer must do against a future proof-producing symbolic audit's
20-file output bundle. It does not run any check, does not evaluate any
fixture, and asserts no mathematical result. `scientific_execution_authorized:
false` for this preparation task; `maximum_runs: 0`.

Source of truth: `experiments/EXP-CRYPTO-6505c6/specification.yaml`
(`independent_checker_plan`), approved by `DEC-20260907-d42056`.

## 1. Inputs

The checker consumes, unmodified:

- Immutable claim statements (the hypothesis `H-CRYPTO-fde1f1` and the frozen
  `main_transfer_target` in the specification).
- Symbolic case predicates from `symbolic-fixtures.yaml` (this preparation
  package) and, once produced, `case-index.yaml` from the future audit bundle.
- Source passages actually read by the audit, recorded in
  `source-readings.yaml` and `source-hypothesis-matrix.yaml`.
- Certificate text/formal artifacts in `certificate-bundle.md`, conforming to
  `certificate-schema.json` (this preparation package).
- The dependency DAG in `dependency-dag.yaml`.
- The complexity ledger in `complexity-ledger.yaml`.
- All quantifier/normalization declarations from `normalization-and-weights.yaml`
  and the frozen specification's `frozen_symbolic_domain`.

## 2. Structural outputs (mechanical checks)

These are schema/path/hash/coverage/dependency checks that any independent
program can run without mathematical judgment:

- Schema validity of every artifact against `certificate-schema.json` and the
  YAML shapes declared in `obligation-matrix.yaml` / `symbolic-fixtures.yaml`.
- Exact file count and filenames: all 20 root files listed in
  `certificate-schema.json`'s `bundle_constraints.root_filenames`, no more, no
  fewer, no per-cell directory trees.
- Full coverage: `obligation-results.yaml` contains all 160 keyed
  `(case_id, obligation_id)` rows; `chart-coverage.yaml` contains all 400 keyed
  `(case_id, left_tag, right_tag)` rows. A missing key is a structural finding,
  reported by exact key.
- Hash consistency: `artifact-sha256.json` hashes match every other
  materialized artifact in the bundle (it does not hash itself).
- Certificate-anchor integrity: every `cert_id` referenced in
  `dependency-dag.yaml` or `checker-results.yaml` resolves to exactly one
  anchor in `certificate-bundle.md`; no duplicate or dangling anchor.
- Dependency-graph well-formedness: the DAG in `dependency-dag.yaml` is
  acyclic, and every edge references a `cert_id` that exists.
- Status-domain conformance: every `status` field value is one of the six
  enumerated statuses in `specification.obligation_matrix.statuses`, or an
  explicit unfilled/null with a stated reason.
- Reuse-binding check: a certificate marked as reused across cells carries an
  explicit matching statement/scope/dependency substitution record, per
  `specification.obligation_matrix.reuse`; a bare copied verdict without that
  binding is a structural failure.

A structural-output report is a **finding list**: exact missing cells, exact
unbound sources, exact schema violations. It carries no verdict on any
mathematical claim.

## 3. Independent semantic outputs (not performed by this preparation task)

These require an independently reasoned per-claim verdict from a qualified
reviewer with actual source-reading and mathematical judgment — never this
preparation Executor, and never inferred from structural PASS:

- For each certificate: does the cited source (`source.ref`,
  `source.provenance`, `source.claim`) actually state what the certificate
  claims it does, at the claimed generality (quantifier order, hypotheses)?
- For each obligation: is the recorded `statement` mathematically correct
  given its `scope`, and does the recorded `dependency` list actually suffice
  to derive it?
- For the matched-null controls: does the recorded rank/ramification/Swan
  comparison actually establish the required equality, per
  `specification.controls.matched_nulls`, or is it OPEN?
- For the constant-sheaf controls (`case-15`, `case-16`): does the argument
  that certifies the main-family cancellation also, incorrectly, accept the
  constant sheaves? (An argument that does is invalid, per
  `specification.falsification_criterion`.)
- Counterexample verification: is a claimed counterexample in
  `counterexamples.yaml` an actual, checkable violation of the exact stated
  quantified target, and does it stay within its named family/base/scope?

This output requires an independent qualified review task (a `validator` or
`red-team` handoff with its own `review_plan`, per `docs/task-lifecycle.md`
and `templates/research-records.md`), never the preparation Executor and
never the audit's own producer.

## 4. Exact soundness limits

- Schema-valid or hash-consistent is **not** theorem-proved. Coverage
  completeness (all 160/400 keys present) is a completeness property, not a
  correctness property.
- A source citation without an actual reading/matching record (i.e.
  `provenance: recalled`, or `verified_by: null` where required) **cannot**
  discharge a mathematical premise — see `templates/research-records.md`,
  "Citation provenance".
- Open moment/uniformity/effectiveness premises (`specification.main_transfer_
  target.effective_B`, `.stratification`, `.no_free_constants`) remain OPEN
  until an independent semantic reviewer actually checks the proof, no matter
  how complete the structural coverage is.
- A checker PASS on structural checks alone must never be reported, summarized,
  or relied upon as "the audit is correct." The two output classes (Section 2
  vs Section 3) must be reported in visibly separate fields, never merged into
  one aggregate verdict.
- This document specifies the checker; it does not instantiate or run one.
  No checker output exists yet, and none is fabricated here.
