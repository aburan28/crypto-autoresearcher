Reviewed **`63ddb2017f0b286841f3f8f00a0ebafde903deb3`** only. I found one confirmed reader-limit bug and one seed reproducibility concern. The saved receipt’s matrix binding and inventory summaries are internally consistent. I did not inspect the successor working changes.

1. **P2 — The reader exceeds its stated 64 MiB total before refusing the input.**  
   At [tools/claim_evidence_matrix.py:139](/home/ec2-user/crypto-autoresearcher-claim-evidence-20261029/tools/claim_evidence_matrix.py:139), `read_source()` fetches and retains the next blob before lines 140–141 check the aggregate size. Consequently, four accepted 16 MiB sources exhaust the allowance, and a fifth 16 MiB source is still fetched and hashed. This contradicts the total read cap stated in [README.md:44](/home/ec2-user/crypto-autoresearcher-claim-evidence-20261029/research/historical-claim-evidence-20261029/README.md:44).

   **Reproduction:** I executed the exact pinned reader in memory with a Git stub supplying one valid 16 MiB blob under five distinct source IDs. The original `read_source()` performed its mode, identity, size and SHA-256 checks. It fetched **83,886,080 bytes**, then raised `matrix exceeds bounded total reader limit`; the configured cap was **67,108,864 bytes**. The stub reused one bytes allocation, keeping the reproduction below the requested memory bound.

   **Minimal fix:** Pass the remaining aggregate allowance into `read_source()`. After `cat-file -s`, reject a size exceeding that allowance **before** `cat-file blob`; retain the aggregate bookkeeping afterward. Add a control asserting that the fifth blob is never fetched.

2. **P2 — The seed builder does not pin its archive selection to the recorded full commit.**  
   [build_seed.py:22](/home/ec2-user/crypto-autoresearcher-claim-evidence-20261029/research/historical-claim-evidence-20261029/build_seed.py:22) resolves `615b6d34e^{commit}` on every invocation. The published matrix records the full archive commit `615b6d34e3636bf3745ac5c74d5de408f1934233`, but the builder neither uses that literal nor checks its resolution against it.

   An abbreviated revision depends on the repository’s current object/ref namespace: an added matching object can make it ambiguous, and a matching ref can affect revision resolution. A successful alternate resolution would cause the builder to generate new hashes from that selection; the reader would correctly validate those bytes without detecting departure from the intended frozen archive. This is a **builder reproducibility/source-selection concern**, not a bypass of the reader’s full-commit checks.

   **Minimal fix:** Use the recorded full archive commit as a constant, as already done for `AUTO`, `FORMAL` and `COVER`. I did not create refs or commits to reproduce this condition.

The resource limits also have two narrower limitations:

- **The original CLI does not bound matrix input size before reading and parsing it** at [tools/claim_evidence_matrix.py:203](/home/ec2-user/crypto-autoresearcher-claim-evidence-20261029/tools/claim_evidence_matrix.py:203). The source-byte counters do not constrain JSON input allocation.
- **Raw blob caps are not memory caps.** At [tools/claim_evidence_matrix.py:159](/home/ec2-user/crypto-autoresearcher-claim-evidence-20261029/tools/claim_evidence_matrix.py:159), each claim decodes and splits its entire source into a list of strings. In an isolated 2 MiB `b'x\n'` fixture, that expression produced 1,048,576 lines occupying **61,926,104 bytes** for the list and line strings alone. A linear projection to a permitted 16 MiB blob is approximately **495 MB**, excluding retained blobs and other allocations. That projection was not executed. Repeated claims also repeat this work. This does not invalidate the byte/excerpt result; it means the documented byte caps should not be described as an equivalent RAM bound. Scanning to the requested line interval without retaining every line would reduce this expansion.

For the local-only contract, `git()` relies on `GIT_NO_LAZY_FETCH` at [tools/claim_evidence_matrix.py:83](/home/ec2-user/crypto-autoresearcher-claim-evidence-20261029/tools/claim_evidence_matrix.py:83). The code contains neither a minimum Git-version check nor a transport-denial fallback. **I did not establish a version-specific failure or attempt a network reproduction.** Adding `GIT_ALLOW_PROTOCOL=''` is a reasonable explicit safeguard against transport on versions that do not honor the lazy-fetch variable.

I independently checked that the committed receipt matches the matrix’s SHA-256, six claim IDs/count, fifteen declared Git sources, unavailable source IDs, bound/missing role sets, unavailable evidence references, open obligations and omissions. All those comparisons passed. The saved test log records eleven successful tests; I did not rerun that suite because it creates commits.

The reader’s stated scientific limitations match its implementation. Evidence roles are curated pointers; using the same available source for multiple roles is deliberately accepted. Missing evidence remains visible, scientific validity remains unassessed, and complete coverage cannot be emitted. I found no additional false acceptance or rejection in the inspected identity/excerpt checks. I did not inspect historical evidence outside the supplied allowlist, so the saved **432,829-byte** source total and the historical source/excerpt hashes were not independently replayed.

```yaml
review_attestation:
  task_id: /root/claim_evidence_code_review
  reviewed_commit: 63ddb2017f0b286841f3f8f00a0ebafde903deb3
  joints_owned:
    - reader correctness and false acceptance/rejection
    - source identity and seed reproducibility
    - output receipt consistency
    - bounded resource behavior
    - fidelity of documented reader limitations
  sources_read:
    - AGENTS.md
    - docs/agent-contract-extended.md
    - docs/lab-contract.md
    - docs/skill-routing.md
    - .claude/skills/pr/SKILL.md
    - agents/validator.md
    - agents/red-team.md
    - templates/research-records.md
    - tools/claim_evidence_matrix.py
    - tests/test_claim_evidence_matrix.py
    - research/historical-claim-evidence-20261029/README.md
    - research/historical-claim-evidence-20261029/build_seed.py
    - research/historical-claim-evidence-20261029/matrix.json
    - research/historical-claim-evidence-20261029/integrity.json
    - research/historical-claim-evidence-20261029/unit-tests.txt
  sources_read_scope: Applicable instruction sections and listed implementation artifacts; some long instruction output was truncated.
  read_sibling_reports: false
  blind_from_respected: null
  verdict: breaks
  verdict_scope: The documented aggregate read cap is violated at the reviewed commit; this is not a scientific verdict.
  mutations: none
  network_calls: none
  successor_changes_inspected: false
```