# Sheriff sweep SHF-20261023-7b9227

Deterministic half of a sheriff case (`docs/sheriff.md`). It lists what the checks flagged. It upholds nothing: verdicts come from the reader pass in `findings.yaml`.

- target: `all`; deep tier: True
- started 2026-10-23T00:20:28.292705+00:00, finished 2026-10-23T00:36:27.363859+00:00
- canary (positive control): **passed** (15 plants caught, 0 missed, 0 false positives)

| repository | HEAD | tree | branch | at origin/main | dirty paths | sparse (files outside) |
| --- | --- | --- | --- | --- | --- | --- |
| crypto-autoresearcher | `e9b91d62a9b8` | `cbeeb110d45a` | claude/sheriff-all-20261023 | True | 0 | no |
| crypto | `6ed792e860c9` | `ae8d4da4628c` | HEAD | True | 0 | yes (120369) |
| cryptanalysis | `6dfc25d2b064` | `5ba80eacbc08` | main | True | 0 | yes (53458) |

## Counts

| beat | blocker | major | minor | info | not_covered |
| --- | --- | --- | --- | --- | --- |
| B2 execution proofs, STARKs and zk | 0 | 3 | 9 | 0 | 0 |
| B3 Lean and formal proofs | 0 | 3 | 1 | 9 | 4 |
| B4 certificates and verified answers | 0 | 1 | 0 | 0 | 0 |
| B5 cost accounting and comparisons | 0 | 1 | 0 | 0 | 1 |
| B7 provenance, integrity and reproducibility | 0 | 4 | 1 | 0 | 401 |
| B8 prose, papers and numbers | 0 | 0 | 6 | 381 | 7 |

## Checkers

| checker | repo | beat | status | note |
| --- | --- | --- | --- | --- |
| `progress-fidelity` | crypto-autoresearcher | B5 | pass |  |
| `runbook-pending-audits` | crypto-autoresearcher | B7 | fail | 2 finished runbook session(s) with no audit of their journal tip |
| `claim-class` | crypto-autoresearcher | B8 | pass |  |
| `run-source-provenance` | crypto-autoresearcher | B7 | advisory |  |
| `ledger` | crypto-autoresearcher | B7 | fail |  |
| `merge-hygiene` | crypto-autoresearcher | B7 | pass |  |
| `formal-build-and-axioms` | crypto-autoresearcher | B3 | not_covered | missing: lake (probed PATH and /root/.elan/bin) |
| `formal-targets` | crypto-autoresearcher | B3 | not_covered | missing: lake (probed PATH and /root/.elan/bin) |
| `curve-names` | crypto | B4 | fail | sparse checkout: a missing file can fail this checker; confirm on a full checkout |
| `ecbench-bounds` | crypto | B5 | fail | sparse checkout: a missing file can fail this checker; confirm on a full checkout |
| `ecbench-challenges` | crypto | B5 | partial | sparse checkout: passed on the materialised tree only; 120369 tracked file(s) outside the sparse set (repos.crypto.sparse) |
| `ecbench-sessions-integrity` | crypto | B7 | partial | 7 of 504 committed ecbench.session/v1 sessions (enumerated from HEAD) pass --replay 0 --allow-interrupted; 0 fail; 0 not run (time budget); 497 not materialised in this checkout |
| `zk-stark-tests` | crypto | B2 | fail | sparse checkout: a missing file can fail this checker; confirm on a full checkout |
| `fb-archive` | cryptanalysis | B7 | fail | sparse checkout: a missing file can fail this checker; confirm on a full checkout |
| `fb-refs` | cryptanalysis | B7 | fail | sparse checkout: a missing file can fail this checker; confirm on a full checkout |
| `lean-gate-selftest` | cryptanalysis | B3 | not_covered | missing: lake (probed PATH and /root/.elan/bin) |
| `lean-proof-gate` | cryptanalysis | B3 | not_covered | missing: lake (probed PATH and /root/.elan/bin) |

## Blockers (0)


## Major (12)

- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:formal/smoke`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.unpinned** (lead) `crypto-autoresearcher:docs/reports/2026-10-22-semaev-first-fall-replay/evidence/finite-equation-lean-eval.lean`: 15 Lean file(s) with no lean-toolchain pin: the build cannot be reproduced
- **lean.native_decide** (finding) `crypto:research/ic_tree_split_structured_v_20261011/lean/TreeSplit/Replay.lean:249`: compiler-trusted evaluation: the kernel did not check this; the compiler and every `implemented_by` it reaches are in the trusted base
- **zk.no_negative_test** (lead) `crypto:src/zk/groth16.rs`: 1 verifier function(s) and 3 test(s) in this file, none of which shows a forged or tampered proof being rejected
- **zk.discarded_value** (lead) `crypto:src/zk/plonk.rs:368`: `verify` discards `omega`: a value the verifier reads and never checks is a constraint it does not enforce
- **check.runbook-pending-audits** (finding) `crypto-autoresearcher:`: existing checker `runbook-pending-audits` fail: 2 finished runbook session(s) with no audit of their journal tip
- **check.ledger** (finding) `crypto-autoresearcher:`: existing checker `ledger` fail: see sweep.json tail
- **check.curve-names** (finding) `crypto:`: existing checker `curve-names` fail: sparse checkout: a missing file can fail this checker; confirm on a full checkout
- **check.ecbench-bounds** (finding) `crypto:`: existing checker `ecbench-bounds` fail: sparse checkout: a missing file can fail this checker; confirm on a full checkout
- **check.zk-stark-tests** (finding) `crypto:`: existing checker `zk-stark-tests` fail: sparse checkout: a missing file can fail this checker; confirm on a full checkout
- **check.fb-archive** (finding) `cryptanalysis:`: existing checker `fb-archive` fail: sparse checkout: a missing file can fail this checker; confirm on a full checkout
- **check.fb-refs** (finding) `cryptanalysis:`: existing checker `fb-refs` fail: sparse checkout: a missing file can fail this checker; confirm on a full checkout

## Minor findings and leads (333 listed in sweep.json)

- `crypto:prose.strong_claim`: 200
- `cryptanalysis:prose.strong_claim`: 88
- `crypto-autoresearcher:prose.strong_claim`: 19
- `crypto-autoresearcher:zk.proof_language`: 9
- `crypto-autoresearcher:paper.untraced_number`: 6
- `crypto:lean.metaprogram`: 3
- `crypto-autoresearcher:lean.metaprogram`: 2
- `crypto:lean.native_decide`: 2
- `crypto-autoresearcher:lean.no_ci`: 1
- `crypto:lean.axiom`: 1
- `crypto:lean.sorry`: 1
- `crypto-autoresearcher:check.run-source-provenance`: 1

## What this sweep does not establish

- that any claim is true: verdicts come from the reader pass (findings.yaml)
- anything a not_covered check would have tested
- execution integrity: no execution proof is verified here (docs/execution-proof-chain.md)
- statement fidelity of any Lean theorem: that is a reader's check
