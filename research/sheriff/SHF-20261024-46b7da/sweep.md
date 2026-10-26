# Sheriff sweep SHF-20261024-46b7da

Deterministic half of a sheriff case (`docs/sheriff.md`). It lists what the checks flagged. It upholds nothing: verdicts come from the reader pass in `findings.yaml`.

- target: `all`; deep tier: True
- started 2026-10-24T06:23:20.238077+00:00, finished 2026-10-24T09:23:32.892860+00:00
- canary (positive control): **passed** (15 plants caught, 0 missed, 0 false positives)

| repository | HEAD | tree | branch | at origin/main | dirty paths | sparse (files outside) |
| --- | --- | --- | --- | --- | --- | --- |
| crypto-autoresearcher | `4647b1d072ff` | `56e0d3ac2198` | codex/sheriff-full-20261024 | True | 0 | no |
| crypto | `172f84c7b014` | `26291a47eab2` | HEAD | True | 0 | no |
| cryptanalysis | `9d320ae7df3b` | `afd5618516f9` | HEAD | True | 0 | no |

## Counts

| beat | blocker | major | minor | info | not_covered |
| --- | --- | --- | --- | --- | --- |
| B2 execution proofs, STARKs and zk | 0 | 2 | 14 | 0 | 0 |
| B3 Lean and formal proofs | 0 | 6 | 37 | 14 | 0 |
| B7 provenance, integrity and reproducibility | 0 | 6 | 1 | 0 | 0 |
| B8 prose, papers and numbers | 0 | 0 | 79 | 470 | 3 |

## Checkers

| checker | repo | beat | status | note |
| --- | --- | --- | --- | --- |
| `progress-fidelity` | crypto-autoresearcher | B5 | pass |  |
| `runbook-pending-audits` | crypto-autoresearcher | B7 | fail | 2 finished runbook session(s) with no audit of their journal tip |
| `claim-class` | crypto-autoresearcher | B8 | pass |  |
| `run-source-provenance` | crypto-autoresearcher | B7 | advisory |  |
| `ledger` | crypto-autoresearcher | B7 | fail |  |
| `merge-hygiene` | crypto-autoresearcher | B7 | pass |  |
| `formal-build-and-axioms` | crypto-autoresearcher | B3 | pass |  |
| `formal-targets` | crypto-autoresearcher | B3 | error | timed out after 3600 s |
| `curve-names` | crypto | B4 | pass |  |
| `ecbench-bounds` | crypto | B5 | pass |  |
| `ecbench-challenges` | crypto | B5 | pass |  |
| `ecbench-sessions-integrity` | crypto | B7 | fail | 388 of 617 committed ecbench.session/v1 sessions (enumerated from HEAD) pass --replay 0 --allow-interrupted; 53 fail; 176 not run (time budget); 0 not materialised in this checkout |
| `zk-stark-tests` | crypto | B2 | pass |  |
| `fb-archive` | cryptanalysis | B7 | fail |  |
| `fb-refs` | cryptanalysis | B7 | fail |  |
| `lean-gate-selftest` | cryptanalysis | B3 | fail |  |
| `lean-proof-gate` | cryptanalysis | B3 | fail |  |

## Blockers (0)


## Major (14)

- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:formal/smoke`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.unpinned** (lead) `crypto-autoresearcher:docs/reports/2026-10-22-semaev-first-fall-replay/evidence/finite-equation-lean-eval.lean`: 15 Lean file(s) with no lean-toolchain pin: the build cannot be reproduced
- **lean.native_decide** (finding) `crypto:research/ic_tree_split_structured_v_20261011/lean/TreeSplit/Replay.lean:249`: compiler-trusted evaluation: the kernel did not check this; the compiler and every `implemented_by` it reaches are in the trusted base
- **lean.no_axiom_audit** (lead) `crypto:research/eigen_seta_assessment_20261017/lean`: standalone Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **zk.no_negative_test** (lead) `crypto:src/zk/groth16.rs`: 1 verifier function(s) and 3 test(s) in this file, none of which shows a forged or tampered proof being rejected
- **zk.discarded_value** (lead) `crypto:src/zk/plonk.rs:368`: `verify` discards `omega`: a value the verifier reads and never checks is a constraint it does not enforce
- **sheriff.checker_wrote** (finding) `crypto-autoresearcher:`: the working tree changed while the sweep ran: a checker is not read-only
- **check.runbook-pending-audits** (finding) `crypto-autoresearcher:`: existing checker `runbook-pending-audits` fail: 2 finished runbook session(s) with no audit of their journal tip
- **check.ledger** (finding) `crypto-autoresearcher:`: existing checker `ledger` fail: see sweep.json tail
- **check.ecbench-sessions-integrity** (finding) `crypto:`: existing checker `ecbench-sessions-integrity` fail: 388 of 617 committed ecbench.session/v1 sessions (enumerated from HEAD) pass --replay 0 --allow-interrupted; 53 fail; 176 not run (time budget); 0 not materialised in this checkout
- **check.fb-archive** (finding) `cryptanalysis:`: existing checker `fb-archive` fail: see sweep.json tail
- **check.fb-refs** (finding) `cryptanalysis:`: existing checker `fb-refs` fail: see sweep.json tail
- **check.lean-gate-selftest** (finding) `cryptanalysis:`: existing checker `lean-gate-selftest` fail: see sweep.json tail
- **check.lean-proof-gate** (finding) `cryptanalysis:`: existing checker `lean-proof-gate` fail: see sweep.json tail

## Minor findings and leads (469 listed in sweep.json)

- `crypto:prose.strong_claim`: 200
- `cryptanalysis:prose.strong_claim`: 97
- `crypto:paper.untraced_number`: 72
- `crypto-autoresearcher:prose.strong_claim`: 27
- `cryptanalysis:lean.no_ci`: 25
- `crypto:lean.no_ci`: 10
- `crypto-autoresearcher:zk.proof_language`: 9
- `crypto:lean.metaprogram`: 8
- `crypto-autoresearcher:paper.untraced_number`: 6
- `crypto:zk.proof_language`: 5
- `crypto-autoresearcher:lean.metaprogram`: 2
- `crypto:lean.native_decide`: 2
- `crypto-autoresearcher:lean.no_ci`: 1
- `crypto:lean.axiom`: 1
- `crypto:lean.sorry`: 1
- `cryptanalysis:paper.untraced_number`: 1
- `crypto-autoresearcher:check.run-source-provenance`: 1
- `crypto-autoresearcher:check.formal-targets`: 1

## What this sweep does not establish

- that any claim is true: verdicts come from the reader pass (findings.yaml)
- anything a not_covered check would have tested
- execution integrity: no execution proof is verified here (docs/execution-proof-chain.md)
- statement fidelity of any Lean theorem: that is a reader's check
