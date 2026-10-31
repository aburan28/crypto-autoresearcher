# Last fall degree review input binding

- Producer tree: `199f3aaaa6d37d2fce59f4d8c8fe8d2eb8b50672` on `crypto-autoresearcher/main`.
- Claim: `THM-FALLDEG-INVARIANTS1-THM-2-8` in `research/THM_FALLDEG_INVARIANTS1.md`; producer task `TASK-20260916-5559c8`.
- Named declaration: `CryptoResearch.FallDegree.lastFallDegree_eq_max_degreeFall` in `formal/CryptoResearch/FallDegree/LastFall.lean`.
- Git blob IDs: source note `aebd86a88a45634cebd6d301a8e1844843967ad8`; target `6218c1a4ac4600fe9148f3376b6bab8f47430405`; Lean source `b702d4c8bc5c0a3b6b2eafd10e8b349ab61d2fbc`; toolchain `3d1dc1d0f50b488e6c6b3496524dd7df672082e8`; Lake manifest `bed58e530beda3e048c5f537af47fdf987c96a78`.
- Pinned Lean: `leanprover/lean4:v4.35.0-rc1`; Mathlib revision `7fa22735254ddf7e11f119250a9f2d0352bc7c3a`.
- Hosted historical receipt: `docs/reports/2026-10-31-hosted-formal-receipts/receipts/lastfall-is-max-degree-fall.json`, source commit `232f4e78abe6cd8eca285fb2be075d3fdd40ee33`; it reports `machine_verified`, build and axiom audit passed, semantic review pending. Its recorded input sets contain 68 workspace and 10 verifier entries. It has not been independently authenticated by this review.
- Primary paper: Caminata and Gorla, *Solving degree, last fall degree, and related invariants*, ePrint 2021/1611, Definition 1.5 and Theorem 2.8.
- Scope distinction to test: the theorem characterizes the global invariant under explicit hypotheses. A concrete Macaulay rank run additionally requires a verified row-space bridge, full degree coverage or a valid stopping bound, and exact run inputs.

This is a precommitted review plan, not a semantic verdict. Reviewer reports, fresh machine evidence, controls and an inspected PDF follow separately.
