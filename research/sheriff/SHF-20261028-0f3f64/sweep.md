# Sheriff sweep SHF-20261028-0f3f64

Deterministic half of a sheriff case (`docs/sheriff.md`). It lists what the checks flagged. It upholds nothing: verdicts come from the reader pass in `findings.yaml`.

- target: `all`; deep tier: True
- started 2026-10-28T02:28:24.873362+00:00, finished 2026-10-28T02:30:02.861877+00:00
- canary (positive control): **passed** (15 plants caught, 0 missed, 0 false positives)

| repository | HEAD | tree | branch | at origin/main | dirty paths | sparse (files outside) |
| --- | --- | --- | --- | --- | --- | --- |
| crypto-autoresearcher | `b7d5e65b9fcf` | `6a18c6e7a655` | claude/sheriff-reaudit-20261028 | True | 0 | no |
| crypto | `669809d5c611` | `0764b77a14b9` | main | True | 0 | yes (155016) |
| cryptanalysis | `f3cce49955e5` | `d122a734c1dc` | main | True | 0 | yes (55124) |

## Counts

| beat | blocker | major | minor | info | not_covered |
| --- | --- | --- | --- | --- | --- |
| B2 execution proofs, STARKs and zk | 0 | 2 | 12 | 0 | 0 |
| B3 Lean and formal proofs | 13 | 31 | 98 | 209 | 0 |
| B7 provenance, integrity and reproducibility | 0 | 0 | 0 | 0 | 400 |
| B8 prose, papers and numbers | 0 | 0 | 6 | 678 | 12 |

## Checkers

| checker | repo | beat | status | note |
| --- | --- | --- | --- | --- |

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
- **zk.no_negative_test** (lead) `crypto:src/zk/groth16.rs`: 1 verifier function(s) and 3 test(s) in this file, none of which shows a forged or tampered proof being rejected
- **zk.discarded_value** (lead) `crypto:src/zk/plonk.rs:368`: `verify` discards `omega`: a value the verifier reads and never checks is a constraint it does not enforce

## Minor findings and leads (640 listed in sweep.json)

- `crypto-autoresearcher:lean.metaprogram`: 200
- `crypto:prose.strong_claim`: 200
- `cryptanalysis:prose.strong_claim`: 88
- `crypto-autoresearcher:lean.no_ci`: 68
- `crypto-autoresearcher:lean.vacuous`: 29
- `crypto-autoresearcher:prose.strong_claim`: 27
- `crypto-autoresearcher:zk.proof_language`: 12
- `crypto-autoresearcher:paper.untraced_number`: 6
- `crypto:lean.native_decide`: 2
- `cryptanalysis:lean.native_decide`: 2
- `crypto:lean.metaprogram`: 1
- `crypto:lean.axiom`: 1
- `crypto:lean.sorry`: 1
- `crypto:lean.no_ci`: 1
- `cryptanalysis:lean.axiom`: 1
- `cryptanalysis:lean.sorry`: 1

## What this sweep does not establish

- that any claim is true: verdicts come from the reader pass (findings.yaml)
- anything a not_covered check would have tested
- execution integrity: no execution proof is verified here (docs/execution-proof-chain.md)
- statement fidelity of any Lean theorem: that is a reader's check
