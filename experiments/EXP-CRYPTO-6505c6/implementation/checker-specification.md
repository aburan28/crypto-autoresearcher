# Checker specification (EXP-CRYPTO-6505c6, preparation only)

This document specifies what a **future** checker for the symbolic
trace-transfer audit takes as input and what it produces. It does not run
any check. No numerical runner, subprocess, or execution wrapper exists in
this preparation task (`maximum_runs: 0`); this is an interface
specification for a checker that has not been built or invoked.

## 1. Inputs

The checker consumes, once the future audit has produced them:

- Immutable claim statements (per-case, per-obligation, per-chart-cell).
- Symbolic case predicates (`symbolic-fixtures.yaml` in this bundle, and the
  future audit's `case-index.yaml`).
- Source passages actually read and matched (future `source-readings.yaml`,
  `source-hypothesis-matrix.yaml`).
- Certificate text / formal artifacts (future `certificate-bundle.md`, keyed
  by `cert_id` per `certificate-schema.json` in this bundle).
- The dependency DAG among certificates (future `dependency-dag.yaml`).
- The complexity ledger (future `complexity-ledger.yaml`).
- All quantifier/normalization declarations (`symbolic-fixtures.yaml`,
  future `normalization-and-weights.yaml`).

## 2. Structural outputs (mechanical; anyone, or a script, can run these)

These checks operate on shape, keys, hashes, and graph structure only. They
require no mathematical expertise and prove nothing mathematically.

- **Schema validity**: every certificate, obligation row, and chart row
  validates against `certificate-schema.json`.
- **Coverage completeness**: exactly 160 `(case_id, obligation_id)` keys are
  present in `obligation-results.yaml`, and exactly 400
  `(case_id, left_tag, right_tag)` keys are present in `chart-coverage.yaml`,
  with no duplicates and no omissions, matching the frozen specification's
  fixed case/obligation/chart panel exactly (16 cases, 10 obligations, 25
  chart-pair keys per case).
- **Anchor resolution**: every `certificate_anchor` / `dependency` /
  `cert_id` reference resolves to exactly one definition in
  `certificate-bundle.md`; no dangling or duplicate anchors.
- **Hash consistency**: every file listed in the 20-file root bundle (except
  `artifact-sha256.json` itself) has a recorded sha256 in
  `artifact-sha256.json` that matches its actual bytes.
- **Dependency graph well-formedness**: `dependency-dag.yaml` is acyclic and
  every edge endpoint is a defined `cert_id`.
- **Status-value validity**: every `status` / `result_status` field takes a
  value from the frozen enum
  `[CERTIFIED, REFUTED, OPEN, OUTSIDE_MAIN_SCOPE_CLASSIFIED,
  NOT_APPLICABLE_WITH_CERTIFICATE, NOT_ATTEMPTED_AFTER_STOP]`.
- **Missing-cell / unbound-source reporting**: for any row lacking a
  required certificate field, or citing a source without a `read_status` of
  `read_and_matched`, the checker reports the exact missing-cell or
  unbound-source finding rather than silently passing it.

A full PASS on every item above establishes only that the audit's paperwork
is internally consistent and complete. It establishes nothing about whether
any statement in that paperwork is true.

## 3. Independent semantic outputs (require genuine mathematical review; not performed here or by any script)

- An independently reasoned, per-claim verdict on whether the cited source
  passage actually supports the stated certificate, produced by a reviewer
  who has actually read the source.
- Verification that a cited proof's premises are actually satisfied in the
  declared scope (family, base, parameter locus), not merely that a citation
  exists.
- Identification of counterexamples, if any, to a quantified statement.
- A judgment on whether an `OPEN` or `NOT_ATTEMPTED_AFTER_STOP` classification
  is itself correctly scoped (i.e., that nothing was silently narrowed to
  avoid a hard sub-case).

This category requires an actual qualified independent review task under a
Coordinator-preregistered review plan (see `independent-check-plan.md`). It
is explicitly **not** performed by this preparation Executor task, by the
future audit-producing task acting alone, or by any structural/mechanical
script.

## 4. Soundness boundary (binding)

- A schema-valid or hash-consistent bundle is **not** a proved theorem.
- A source citation without an actual reading/matching record (i.e.
  `read_status != read_and_matched`) cannot discharge a mathematical
  premise.
- Open moment / uniformity / effectiveness premises (the all-extension
  fourth-moment bound `B(C)`, exceptional-locus degree bound `D(C)`,
  off-locus constant `K(C)`) remain `OPEN` until an actual, independently
  checked proof or an actual, independently checked counterexample exists —
  never inferred from mechanical PASS alone.
- `NOT_APPLICABLE_WITH_CERTIFICATE` requires an actual certificate of
  inapplicability/emptiness; it is never used as a substitute for an
  unattempted or inconvenient obligation.
- This preparation task performs zero instances of section 2 or section 3 above.
  It only specifies what they will be.
