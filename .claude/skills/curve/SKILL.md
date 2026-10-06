---
name: curve
description: "Inspect or maintain exact curve identities, EC1 aliases, global curve UIDs, field metadata, trait catalogs, and curve comparison imports. Use for curve catalog work and identity mismatches. Use endo for CM/endomorphism analysis, transfer for maps, and run for existing trials."
---

# Curve records

Read `docs/curve-identities.md` and `tools/curve_identity.py`. For UI ingestion read `ui/README.md` and `ui/curves.py`.

1. Bind the exact field (including basis/polynomial), curve model, coefficients, subgroup, cofactor, generator and target group. Keep unknown facts null.
2. Preserve the producer's hash preimage. Use `curve_identity`, `inspect_manifest`, and `candidate_identity` from the existing helper; do not build a parallel identity convention.
3. Keep curve identity separate from factor-base, isogeny route, algorithm, workload and run identities. Equal degree, order or j-invariant does not identify a curve representation.
4. For a trait import, retain upstream commit/path/hash, measurement parameters, source status and applicability. Place supplementary traits outside the curve identity preimage. Unknown and not applicable are different states.
5. Check conflicts and precision at the UI boundary; preserve large integers and fail closed on pin/identity mismatches. Update catalog pins with the corresponding artifact.
6. Return exact IDs, sourced traits, unresolved values, and a focused diff or identity report. Never turn a metadata hash into a security or speedup badge.

Follow current `AGENTS.md` authority, provenance and immutable-record rules. This profile adds no prerequisite to `run`; preserve explicit execution requests.
