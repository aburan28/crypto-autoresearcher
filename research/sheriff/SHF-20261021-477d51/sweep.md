# Sheriff sweep SHF-20261021-477d51

Deterministic half of a sheriff case (`docs/sheriff.md`). It lists what the checks flagged. It upholds nothing: verdicts come from the reader pass in `findings.yaml`.

- target: `crypto:`; deep tier: True
- started 2026-10-21T05:12:39.195281+00:00, finished 2026-10-21T05:12:44.510159+00:00
- canary (positive control): **passed** (15 plants caught, 0 missed, 0 false positives)

| repository | HEAD | tree | branch | at origin/main | dirty paths | sparse (files outside) |
| --- | --- | --- | --- | --- | --- | --- |
| crypto-autoresearcher | `b6dbfa28bbe0` | `4b14d9af0768` | main | True | 0 | no |
| crypto | `b4f056101a8d` | `f94aaa65a6f5` | HEAD | False | 0 | yes (119202) |

## Counts

| beat | blocker | major | minor | info | not_covered |
| --- | --- | --- | --- | --- | --- |
| B2 execution proofs, STARKs and zk | 0 | 2 | 0 | 0 | 0 |
| B3 Lean and formal proofs | 0 | 0 | 0 | 4 | 0 |
| B7 provenance, integrity and reproducibility | 0 | 0 | 0 | 0 | 200 |
| B8 prose, papers and numbers | 0 | 0 | 0 | 88 | 0 |

## Checkers

| checker | repo | beat | status | note |
| --- | --- | --- | --- | --- |

## Blockers (0)


## Major (2)

- **zk.no_negative_test** (lead) `crypto:src/zk/groth16.rs`: 1 verifier function(s) and 3 test(s) in this file, none of which shows a forged or tampered proof being rejected
- **zk.discarded_value** (lead) `crypto:src/zk/plonk.rs:368`: `verify` discards `omega`: a value the verifier reads and never checks is a constraint it does not enforce

## Minor findings and leads (92 listed in sweep.json)

- `crypto:prose.strong_claim`: 88
- `crypto:lean.native_decide`: 2
- `crypto:lean.axiom`: 1
- `crypto:lean.sorry`: 1

## What this sweep does not establish

- that any claim is true: verdicts come from the reader pass (findings.yaml)
- anything a not_covered check would have tested
- execution integrity: no execution proof is verified here (docs/execution-proof-chain.md)
- statement fidelity of any Lean theorem: that is a reader's check
