# Hosted Lean receipt audit for 91 formal targets

A fresh GitHub Actions formal workspace gate on [PR #2805](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2805) completed its full Lake build and `tools/verify_formal_targets.py` at run `41155781140`, job `124402203382`. The exact PR head was `f9f36cd81bba99872cdec73dd23e2e69213fd446`; the CI test merge was `232f4e78abe6cd8eca285fb2be075d3fdd40ee33` with base parent `a1f3d0fde48d8a09301d65f8b8056f3cf42fc307` and that PR head as its second parent.

The downloaded `formal-verification-receipts` artifact (GitHub artifact ID `13025547799`) contains [91 raw JSON receipts](receipts/). The [audit](audit.json) checks them against the [pinned source-link inventory](../2026-10-31-formal-target-links/links.json). It completed with zero issues:

| Check | Matched |
| --- | ---: |
| Target spec hash, Lean module hash, and named theorem | 91 / 91 |
| `machine_verified`, build passed, axiom audit passed, no forbidden constructs | 91 / 91 |
| Declared source blobs at the CI test merge | 32 / 32 |
| Tracked workspace input blobs, across main and scoped workspaces | 73 / 73 |
| Derived main workspace root, rebuilt from 51 tracked module names | 1 / 1 |
| Verifier input blobs | 10 / 10 |

All 91 raw receipts retain `semantic_review.status: pending`. This field records the machine pipeline's boundary; independent claim-level reviews, including the separately archived Semaev J2 report, are not folded into these receipt JSON files. A Lean kernel result checks the proposition it was given. It does not authenticate a historical experiment, measured runtime, source-to-theorem interpretation, or a broader solver claim.

The [diagram](status.svg) and [PDF](status.pdf) show the two review layers. The 91 target specs are not a denominator for all scientific claims in the three repositories.

## Reproduce

From the repository root, after obtaining or retaining the raw artifact files:

```sh
python3 docs/reports/2026-10-31-hosted-formal-receipts/verify_receipts.py \
  --inventory docs/reports/2026-10-31-formal-target-links/links.json \
  --receipts docs/reports/2026-10-31-hosted-formal-receipts/receipts \
  --source-commit 232f4e78abe6cd8eca285fb2be075d3fdd40ee33 \
  --base a1f3d0fde48d8a09301d65f8b8056f3cf42fc307 \
  --head f9f36cd81bba99872cdec73dd23e2e69213fd446 \
  --output /tmp/formal-receipt-audit.json
```

The reported statistics and receipt SHA-256 rows should match `audit.json`; its `observed_at` is absent, so byte-for-byte output is deterministic. A negative control changed the Semaev receipt's theorem hash to zero: the auditor exited 1 and reported `theorem_module_hash` for that target. This is an integrity control on the auditor, not a theorem falsification.
