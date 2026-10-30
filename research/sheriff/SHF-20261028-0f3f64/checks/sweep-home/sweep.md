# Sheriff sweep sweep-home

Deterministic half of a sheriff case (`docs/sheriff.md`). It lists what the checks flagged. It upholds nothing: verdicts come from the reader pass in `findings.yaml`.

- target: `all`; deep tier: True
- started 2026-10-28T02:30:11.215724+00:00, finished 2026-10-28T02:32:05.015873+00:00
- canary (positive control): **passed** (15 plants caught, 0 missed, 0 false positives)

| repository | HEAD | tree | branch | at origin/main | dirty paths | sparse (files outside) |
| --- | --- | --- | --- | --- | --- | --- |
| crypto-autoresearcher | `b7d5e65b9fcf` | `6a18c6e7a655` | claude/sheriff-reaudit-20261028 | True | 1 | no |

## Counts

| beat | blocker | major | minor | info | not_covered |
| --- | --- | --- | --- | --- | --- |
| B2 execution proofs, STARKs and zk | 0 | 0 | 12 | 0 | 1 |
| B3 Lean and formal proofs | 13 | 31 | 97 | 200 | 5 |
| B4 certificates and verified answers | 0 | 0 | 0 | 0 | 1 |
| B5 cost accounting and comparisons | 0 | 0 | 0 | 0 | 2 |
| B7 provenance, integrity and reproducibility | 0 | 2 | 1 | 0 | 3 |
| B8 prose, papers and numbers | 0 | 0 | 6 | 27 | 0 |

## Checkers

| checker | repo | beat | status | note |
| --- | --- | --- | --- | --- |
| `progress-fidelity` | crypto-autoresearcher | B5 | pass |  |
| `runbook-pending-audits` | crypto-autoresearcher | B7 | fail | 4 finished runbook session(s) with no audit of their journal tip |
| `claim-class` | crypto-autoresearcher | B8 | pass |  |
| `run-source-provenance` | crypto-autoresearcher | B7 | advisory |  |
| `ledger` | crypto-autoresearcher | B7 | fail |  |
| `merge-hygiene` | crypto-autoresearcher | B7 | pass |  |
| `formal-build-and-axioms` | crypto-autoresearcher | B3 | not_covered | missing: lake (probed PATH and /root/.elan/bin) |
| `formal-targets` | crypto-autoresearcher | B3 | not_covered | missing: lake (probed PATH and /root/.elan/bin) |
| `curve-names` | crypto | B4 | not_covered | repository crypto is not checked out |
| `ecbench-bounds` | crypto | B5 | not_covered | repository crypto is not checked out |
| `ecbench-challenges` | crypto | B5 | not_covered | repository crypto is not checked out |
| `ecbench-sessions-integrity` | crypto | B7 | not_covered | repository crypto is not checked out |
| `zk-stark-tests` | crypto | B2 | not_covered | repository crypto is not checked out |
| `fb-archive` | cryptanalysis | B7 | not_covered | repository cryptanalysis is not checked out |
| `fb-refs` | cryptanalysis | B7 | not_covered | repository cryptanalysis is not checked out |
| `lean-evidence-metadata` | cryptanalysis | B3 | not_covered | repository cryptanalysis is not checked out |
| `lean-gate-selftest` | cryptanalysis | B3 | not_covered | repository cryptanalysis is not checked out |
| `lean-proof-gate` | cryptanalysis | B3 | not_covered | repository cryptanalysis is not checked out |

## Blockers (13)

- **lean.sorry** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-cryptanalysis-configured-false/project/Omitted.lean:1`: `sorry`: the statement is assumed, not proved
- **lean.sorry** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-cryptanalysis-unconfigured-false/project/Omitted.lean:1`: `sorry`: the statement is assumed, not proved
- **lean.sorry** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-configured-false/project/Omitted.lean:1`: `sorry`: the statement is assumed, not proved
- **lean.sorry** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-lean-configured-false/project/Omitted.lean:1`: `sorry`: the statement is assumed, not proved
- **lean.sorry** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-lean-unconfigured-false/project/Omitted.lean:1`: `sorry`: the statement is assumed, not proved
- **lean.sorry** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-unconfigured-false/project/Omitted.lean:1`: `sorry`: the statement is assumed, not proved
- **lean.sorry** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-ownership/project/nested/Nested.lean:1`: `sorry`: the statement is assumed, not proved
- **lean.sorry** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-ownership/project/tools/lean/Fixture.lean:1`: `sorry`: the statement is assumed, not proved
- **lean.sorry** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/shared-gate/project/Omitted.lean:1`: `sorry`: the statement is assumed, not proved
- **lean.axiom** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/attribute-custom-axiom/CryptoResearch/Test.lean:2`: custom `axiom`: everything downstream is conditional on an unchecked assumption
- **lean.axiom** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/axiom/CryptoResearch/Test.lean:2`: custom `axiom`: everything downstream is conditional on an unchecked assumption
- **lean.axiom** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/indented-dependency-axiom/CryptoResearch/Test.lean:2`: custom `axiom`: everything downstream is conditional on an unchecked assumption
- **lean.sorry** (finding) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/sorry/CryptoResearch/Test.lean:2`: `sorry`: the statement is assumed, not proved

## Major (33)

- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:formal/smoke`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-cryptanalysis-configured-false/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-cryptanalysis-configured-good/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-cryptanalysis-unconfigured-false/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-cryptanalysis-unconfigured-good/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-configured-false/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-configured-good/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-lean-configured-false/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-lean-configured-good/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-lean-unconfigured-false/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-lean-unconfigured-good/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-unconfigured-false/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-crypto-unconfigured-good/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-ownership/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/control-sources/gate-ownership/project/nested`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-695548/artifacts/runtime-sources/formal/smoke`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/cli/formal`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/shared-gate/project`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/attribute-custom-axiom`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/axiom`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/data-name`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/empty-project-audit`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/fake-project-evidence`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/indented-dependency-axiom`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/omitted-module-bad`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/omitted-module-good`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/positive`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/sorry`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/transitive-axiom`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:research/lean_review_evidence_20261018/reports/TASK-20261018-dae80c/artifacts/control-sources/worker/wrong-name`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.unpinned** (lead) `crypto-autoresearcher:docs/reports/2026-10-22-semaev-first-fall-replay/evidence/finite-equation-lean-eval.lean`: 66 Lean file(s) with no lean-toolchain pin: the build cannot be reproduced
- **check.runbook-pending-audits** (finding) `crypto-autoresearcher:`: existing checker `runbook-pending-audits` fail: 4 finished runbook session(s) with no audit of their journal tip
- **check.ledger** (finding) `crypto-autoresearcher:`: existing checker `ledger` fail: see sweep.json tail

## Minor findings and leads (343 listed in sweep.json)

- `crypto-autoresearcher:lean.metaprogram`: 200
- `crypto-autoresearcher:lean.no_ci`: 68
- `crypto-autoresearcher:lean.vacuous`: 29
- `crypto-autoresearcher:prose.strong_claim`: 27
- `crypto-autoresearcher:zk.proof_language`: 12
- `crypto-autoresearcher:paper.untraced_number`: 6
- `crypto-autoresearcher:check.run-source-provenance`: 1

## What this sweep does not establish

- that any claim is true: verdicts come from the reader pass (findings.yaml)
- anything a not_covered check would have tested
- execution integrity: no execution proof is verified here (docs/execution-proof-chain.md)
- statement fidelity of any Lean theorem: that is a reader's check
