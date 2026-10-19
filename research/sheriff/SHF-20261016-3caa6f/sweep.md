# Sheriff sweep SHF-20261016-3caa6f

Deterministic half of a sheriff case (`docs/sheriff.md`). It lists what the checks flagged. It upholds nothing: verdicts come from the reader pass in `findings.yaml`.

- target: `all`; deep tier: True
- started 2026-10-16T19:31:54.559967+00:00, finished 2026-10-16T19:53:02.894967+00:00
- canary (positive control): **passed** (15 plants caught, 0 missed, 0 false positives)

| repository | HEAD | branch | at origin/main | dirty paths |
| --- | --- | --- | --- | --- |
| crypto-autoresearcher | `3f78e0521bce` | claude/sheriff-audit-skill | True | 8 |
| crypto | `3e7bcb7bc88a` | main | True | 0 |
| cryptanalysis | `77b5c02b96f0` | HEAD | True | 0 |

## Counts

| beat | blocker | major | minor | info | not_covered |
| --- | --- | --- | --- | --- | --- |
| B2 execution proofs, STARKs and zk | 0 | 7 | 17 | 0 | 0 |
| B3 Lean and formal proofs | 1 | 9 | 36 | 5 | 4 |
| B7 provenance, integrity and reproducibility | 0 | 6 | 1 | 0 | 0 |
| B8 prose, papers and numbers | 0 | 0 | 83 | 278 | 2 |

## Checkers

| checker | repo | beat | status | note |
| --- | --- | --- | --- | --- |
| `progress-fidelity` | crypto-autoresearcher | B5 | pass |  |
| `runbook-pending-audits` | crypto-autoresearcher | B7 | fail | 2 finished runbook session(s) with no audit of their journal tip |
| `claim-class` | crypto-autoresearcher | B8 | pass |  |
| `run-source-provenance` | crypto-autoresearcher | B7 | advisory |  |
| `ledger` | crypto-autoresearcher | B7 | fail |  |
| `merge-hygiene` | crypto-autoresearcher | B7 | fail |  |
| `formal-build-and-axioms` | crypto-autoresearcher | B3 | not_covered | missing: lake |
| `formal-targets` | crypto-autoresearcher | B3 | not_covered | missing: lake |
| `curve-names` | crypto | B4 | pass |  |
| `ecbench-bounds` | crypto | B5 | pass |  |
| `ecbench-challenges` | crypto | B5 | pass |  |
| `ecbench-sessions-integrity` | crypto | B7 | fail |  |
| `zk-stark-tests` | crypto | B2 | pass |  |
| `fb-archive` | cryptanalysis | B7 | fail |  |
| `fb-refs` | cryptanalysis | B7 | fail |  |
| `lean-gate-selftest` | cryptanalysis | B3 | not_covered | missing: lake |
| `lean-proof-gate` | cryptanalysis | B3 | not_covered | missing: lake |

## Blockers (1)

- **lean.axiom** (finding) `crypto-autoresearcher:research/THM_QUOTIENT_DESCENT1.lean:10`: custom `axiom`: everything downstream is conditional on an unchecked assumption

## Major (22)

- **lean.no_axiom_audit** (lead) `crypto-autoresearcher:formal/smoke`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.unpinned** (lead) `crypto-autoresearcher:research/THM_QUOTIENT_DESCENT1.lean`: 15 Lean file(s) with no lean-toolchain pin: the build cannot be reproduced
- **lean.native_decide** (finding) `crypto:research/ic_tree_split_structured_v_20261011/lean/TreeSplit/Leak.lean:22`: compiler-trusted evaluation: the kernel did not check this; the compiler and every `implemented_by` it reaches are in the trusted base
- **lean.native_decide** (finding) `crypto:research/ic_tree_split_structured_v_20261011/lean/TreeSplit/Leak.lean:23`: compiler-trusted evaluation: the kernel did not check this; the compiler and every `implemented_by` it reaches are in the trusted base
- **lean.native_decide** (finding) `crypto:research/ic_tree_split_structured_v_20261011/lean/TreeSplit/Replay.lean:249`: compiler-trusted evaluation: the kernel did not check this; the compiler and every `implemented_by` it reaches are in the trusted base
- **lean.no_axiom_audit** (lead) `crypto:papers/rootfinding-decomposition/lean`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto:research/conductor_gap_cm_pairs_20261010/lean`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **lean.no_axiom_audit** (lead) `crypto:research/ic_tree_split_structured_v_20261011/lean`: lake Lean project with no axiom audit (`collectAxioms`/`#print axioms`): a `sorryAx` or custom axiom reached indirectly would go unseen
- **zk.no_negative_test** (lead) `crypto:src/zk/groth16.rs`: 1 verifier function(s) and 3 test(s) in this file, none of which shows a forged or tampered proof being rejected
- **zk.discarded_value** (lead) `crypto:src/zk/plonk.rs:368`: `verify` discards `omega`: a value the verifier reads and never checks is a constraint it does not enforce
- **zk.discarded_value** (lead) `crypto:src/zk/stark.rs:454`: `verify` discards `val`: a value the verifier reads and never checks is a constraint it does not enforce
- **zk.discarded_value** (lead) `crypto:src/zk/stark_v2.rs:408`: `verify` discards `(f_val, c_val)`: a value the verifier reads and never checks is a constraint it does not enforce
- **zk.discarded_value** (lead) `crypto:src/zk/stark_v2.rs:416`: `verify` discards `h_trace`: a value the verifier reads and never checks is a constraint it does not enforce
- **zk.discarded_value** (lead) `crypto:src/zk/stark_v2.rs:417`: `verify` discards `alpha1`: a value the verifier reads and never checks is a constraint it does not enforce
- **zk.discarded_value** (lead) `crypto:src/zk/stark_v2.rs:418`: `verify` discards `alpha2`: a value the verifier reads and never checks is a constraint it does not enforce
- **lean.unpinned** (lead) `cryptanalysis:experiments/n83-packed-root-capacity-20261013/CapacityBound.lean`: 20 Lean file(s) with no lean-toolchain pin: the build cannot be reproduced
- **check.runbook-pending-audits** (finding) `crypto-autoresearcher:`: existing checker `runbook-pending-audits` fail: 2 finished runbook session(s) with no audit of their journal tip
- **check.ledger** (finding) `crypto-autoresearcher:`: existing checker `ledger` fail: see sweep.json tail
- **check.merge-hygiene** (finding) `crypto-autoresearcher:`: existing checker `merge-hygiene` fail: see sweep.json tail
- **check.ecbench-sessions-integrity** (finding) `crypto:`: existing checker `ecbench-sessions-integrity` fail: see sweep.json tail
- **check.fb-archive** (finding) `cryptanalysis:`: existing checker `fb-archive` fail: see sweep.json tail
- **check.fb-refs** (finding) `cryptanalysis:`: existing checker `fb-refs` fail: see sweep.json tail

## Minor findings and leads (420 listed in sweep.json)

- `crypto:prose.strong_claim`: 165
- `cryptanalysis:prose.strong_claim`: 94
- `crypto:paper.untraced_number`: 64
- `cryptanalysis:lean.no_ci`: 24
- `crypto-autoresearcher:prose.strong_claim`: 19
- `crypto-autoresearcher:paper.untraced_number`: 17
- `crypto:lean.no_ci`: 11
- `crypto-autoresearcher:zk.proof_language`: 8
- `crypto:zk.proof_language`: 5
- `crypto:lean.metaprogram`: 4
- `crypto:zk.trust_comment`: 4
- `cryptanalysis:paper.untraced_number`: 2
- `crypto-autoresearcher:lean.metaprogram`: 1
- `crypto-autoresearcher:lean.no_ci`: 1
- `crypto-autoresearcher:check.run-source-provenance`: 1

## What this sweep does not establish

- that any claim is true: verdicts come from the reader pass (findings.yaml)
- anything a not_covered check would have tested
- execution integrity: no execution proof is verified here (docs/execution-proof-chain.md)
- statement fidelity of any Lean theorem: that is a reader's check
