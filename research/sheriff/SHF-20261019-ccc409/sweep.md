# Sheriff sweep SHF-20261019-ccc409

Deterministic half of a sheriff case (`docs/sheriff.md`). It lists what the checks flagged. It upholds nothing: verdicts come from the reader pass in `findings.yaml`.

- target: `ledger/evidence`; deep tier: False
- started 2026-10-19T18:43:02.586750+00:00, finished 2026-10-19T18:43:17.178216+00:00
- canary (positive control): **passed** (15 plants caught, 0 missed, 0 false positives)

| repository | HEAD | tree | branch | at origin/main | dirty paths | sparse (files outside) |
| --- | --- | --- | --- | --- | --- | --- |
| crypto-autoresearcher | `d0f70c0a0905` | `45c7953fd0f2` | claude/sheriff-ledger-sweep-c | True | 0 | no |

## Counts

| beat | blocker | major | minor | info | not_covered |
| --- | --- | --- | --- | --- | --- |
| B2 execution proofs, STARKs and zk | 0 | 0 | 1 | 0 | 1 |
| B3 Lean and formal proofs | 0 | 0 | 0 | 0 | 4 |
| B4 certificates and verified answers | 0 | 0 | 0 | 0 | 1 |
| B5 cost accounting and comparisons | 0 | 0 | 0 | 0 | 2 |
| B7 provenance, integrity and reproducibility | 0 | 1 | 0 | 0 | 6 |

## Checkers

| checker | repo | beat | status | note |
| --- | --- | --- | --- | --- |
| `progress-fidelity` | crypto-autoresearcher | B5 | pass |  |
| `runbook-pending-audits` | crypto-autoresearcher | B7 | fail | 1 finished runbook session(s) with no audit of their journal tip |
| `claim-class` | crypto-autoresearcher | B8 | pass |  |
| `run-source-provenance` | crypto-autoresearcher | B7 | not_covered | deep tier not requested (--deep) |
| `ledger` | crypto-autoresearcher | B7 | not_covered | deep tier not requested (--deep) |
| `merge-hygiene` | crypto-autoresearcher | B7 | not_covered | deep tier not requested (--deep) |
| `formal-build-and-axioms` | crypto-autoresearcher | B3 | not_covered | deep tier not requested (--deep) |
| `formal-targets` | crypto-autoresearcher | B3 | not_covered | deep tier not requested (--deep) |
| `curve-names` | crypto | B4 | not_covered | repository crypto is not checked out |
| `ecbench-bounds` | crypto | B5 | not_covered | repository crypto is not checked out |
| `ecbench-challenges` | crypto | B5 | not_covered | repository crypto is not checked out |
| `ecbench-sessions-integrity` | crypto | B7 | not_covered | repository crypto is not checked out |
| `zk-stark-tests` | crypto | B2 | not_covered | repository crypto is not checked out |
| `fb-archive` | cryptanalysis | B7 | not_covered | repository cryptanalysis is not checked out |
| `fb-refs` | cryptanalysis | B7 | not_covered | repository cryptanalysis is not checked out |
| `lean-gate-selftest` | cryptanalysis | B3 | not_covered | repository cryptanalysis is not checked out |
| `lean-proof-gate` | cryptanalysis | B3 | not_covered | repository cryptanalysis is not checked out |

## Blockers (0)


## Major (1)

- **check.runbook-pending-audits** (finding) `crypto-autoresearcher:`: existing checker `runbook-pending-audits` fail: 1 finished runbook session(s) with no audit of their journal tip

## Minor findings and leads (1 listed in sweep.json)

- `crypto-autoresearcher:zk.proof_language`: 1

## What this sweep does not establish

- that any claim is true: verdicts come from the reader pass (findings.yaml)
- anything a not_covered check would have tested
- execution integrity: no execution proof is verified here (docs/execution-proof-chain.md)
- statement fidelity of any Lean theorem: that is a reader's check
