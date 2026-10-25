# Procedure notes

- The initial plan was committed and pushed before four independent reviewer sessions.
- Root began author repairs in the review worktree after J3 sent confirmed findings, while its initial report was sealing. The reviewer detected working-copy divergence, preserved the original committed/frozen source and reconfirmed the failing control directly against it. The initial verdict is unchanged. No frozen snapshot was edited.
- The blind reviewer initially supplied top-level JSON fields rather than the required YAML review_attestation wrapper. The independence checker failed; a separate versioned wrapper was requested and produced without unblinding. Both original evidence and failed checker output are retained. The recheck passes four attestations.
- A broad test attempt initially lacked pytest, then exposed 66 missing target-source files in the sparse checkout. After installing pytest in /tmp and materializing the committed target source paths, all 228 relevant tests pass; earlier logs remain. These were infrastructure/checkout issues, not mathematical refutations.
- Git smart-HTTP publication of the shared-library branch failed authentication despite valid API credentials. The same exact local tree/commit was published with the authenticated GitHub Git API; tree/commit equality was checked. Other repository pushes succeeded normally. No force update or merge was performed.
- This packet changes no official hypothesis/evidence status. Stronger historical coverage remains open.
