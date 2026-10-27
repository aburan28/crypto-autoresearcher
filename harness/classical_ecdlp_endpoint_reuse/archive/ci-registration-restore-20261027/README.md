# Restore lost schema-registration metadata

PR #2590 CI run40573421379 stopped in the schema-supersession loader before normal ledger reporting. The only failing harness test checked that the validator completed its sweep; the aggregate job propagated the ledger failure.

Restore exactly two `registered: '2026-10-23'` fields that already existed in introduction commit `82416965ef49a214ab0473a73d09965a67422bf5`. Merge history lost those fields. This repairs the mutable routing index; original and replacement research-record bytes and all four hash pins remain unchanged. It changes no validator, test, gate, scientific result or status.

Sources: the actual three GitHub Actions job logs and hash-verified `harness-ci-ledger` artifact, the registry and `tools/validate_ledger.py` loader, original introduction/merge commits, and the existing coverage test. `registry-audit.json` records the source commits, exact original field dictionaries and hash checks. `ci-excerpts.json` retains actual CI failure/completion excerpts.

Local validation is explicitly limited to the materialized checkout when the documented `CRYPTO_AR_ALLOW_SPARSE=1` mode is used. A completed validator report can still contain other validation findings; this change does not assert repository-wide health or hosted CI success.

The original 2,828-byte `harness-ci-ledger.zip` is retained directly, verified against the artifact service digest. Complete job logs and the 98,671-byte compressed combined source-log bundle remain outside the repository under `/workspace/classical-ecdlp-endpoint-reuse/continuation-ci/`; their hashes and actual excerpts are retained here. No oversized raw log was added to Git.
