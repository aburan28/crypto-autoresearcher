Focused fix review for PR #2675

Original reviewed commit: `63ddb2017f0b286841f3f8f00a0ebafde903deb3`.
Successor reviewed commit: `4e43502d0dfd9493120e98d832f0bee1084fa117`.

The previously identified aggregate source-read bug and abbreviated archive selection concern are resolved at the successor commit. The CLI input limit and explicit Git transport denial address the two associated hardening observations. The memory expansion limitation remains and is now described accurately. This is a focused implementation review, with no scientific validity or historical coverage verdict.

1. Aggregate source allowance — resolved. `tools/claim_evidence_matrix.py:141` supplies `MAX_TOTAL - total` to `read_source()`, and line 113 checks the advertised object size before the blob fetch at line 114. The original after-fetch assertion remains as a consistency check. An independent isolated control executed the exact successor reader with a Git stub and scaled limits of 16 bytes per source and 64 bytes total. Four sources were accepted at exactly 64 bytes. A fifth source was refused after its size lookup, with four blob fetches and exactly 64 bytes fetched. The control exercises the same control flow without large allocations. The new regression test at `tests/test_claim_evidence_matrix.py:90` also checks the number of blob fetches, so it detects the original bug rather than merely checking eventual refusal.

2. Archive source selection — resolved. `research/historical-claim-evidence-20261029/build_seed.py:12` defines `ARCHIVE = '615b6d34e3636bf3745ac5c74d5de408f1934233'`, and line 55 uses that literal for the archived sources. There is no abbreviated archive resolution in the inspected successor builder. The constant matches the full archive identity recorded in the original matrix. I verified the literal through Python AST inspection; no seed generation, ref creation or commit creation was performed.

3. CLI matrix input — bounded before parsing. `tools/claim_evidence_matrix.py:205` opens the input in binary mode and reads at most `MAX_MATRIX + 1` bytes. Line 207 rejects an oversized input before UTF-8 decoding, JSON parsing or source lookup. The extra byte is the bounded oversize sentinel. An isolated control replaced the input stream with nine bytes, lowered the limit to eight bytes, and made JSON parsing fail if called; the CLI returned 2 without invoking the parser. The regression test at `tests/test_claim_evidence_matrix.py:98` checks rejection before Git calls. This is a CLI input bound; it is not a process memory bound.

4. Git transport denial — explicit environment verified. `tools/claim_evidence_matrix.py:85` sets `GIT_ALLOW_PROTOCOL` to the empty string alongside `GIT_NO_LAZY_FETCH` and `GIT_NO_REPLACE_OBJECTS`. An isolated subprocess stub confirmed that all three settings reach the Git subprocess. This removes sole reliance on the lazy-fetch setting for transport denial. No transport was attempted, and no version-specific live Git/network behavior was tested.

5. Resource limitation documentation — accurate. `research/historical-claim-evidence-20261029/README.md:44` now distinguishes source-byte caps and the CLI matrix-byte cap from process RSS, explicitly naming JSON objects, decoded Unicode and line splitting as additional allocations. Full-source line splitting remains at `tools/claim_evidence_matrix.py:161`. The earlier observed allocation amplification therefore remains a limitation; this review does not label it fixed or claim a 64 MiB RAM bound.

The new `unit-tests-v2.txt` records thirteen passing tests. I inspected the two added tests and did not rerun the test suite. The focused controls above ran in memory without fixture repositories or persistent files. They test the reported fixes only.

The original and successor `matrix.json` blobs are byte-identical. The original commit's `integrity.json`, the preserved successor `integrity.json`, and the new `integrity-v2.json` are also byte-identical. The receipt's matrix SHA-256 matches `e30f69a49546b1d383596732a8e6d9d0b84a7820e19312bf80a9bc06004e63a7`. Accordingly, the original review's inventory-summary consistency results still apply. I did not reopen historical evidence outside the source allowlist, rerun the source/excerpt replay, or independently establish the receipt's 432,829-byte historical source total.

No unresolved blocking issue from the original focused findings remains in the inspected successor. This conclusion covers the fixes listed above; it is not a broader rescan, hosted-CI result, merge approval, evidence promotion or scientific conclusion. The original review remains an unchanged record of the original commit.

```yaml
review_attestation:
  task_id: /root/claim_evidence_code_review
  original_reviewed_commit: 63ddb2017f0b286841f3f8f00a0ebafde903deb3
  reviewed_commit: 4e43502d0dfd9493120e98d832f0bee1084fa117
  review_scope: Focused verification of previously identified implementation findings and limitations.
  joints_owned:
    - aggregate source cap before blob fetch
    - frozen archive source selection
    - CLI matrix input bound before parsing
    - explicit Git transport denial configuration
    - resource limitation documentation
    - preservation and matrix binding of the successor receipt
  allowed_source_paths:
    - tools/claim_evidence_matrix.py
    - tests/test_claim_evidence_matrix.py
    - research/historical-claim-evidence-20261029/README.md
    - research/historical-claim-evidence-20261029/build_seed.py
    - research/historical-claim-evidence-20261029/matrix.json
    - research/historical-claim-evidence-20261029/integrity.json
    - research/historical-claim-evidence-20261029/unit-tests.txt
    - research/historical-claim-evidence-20261029/integrity-v2.json
    - research/historical-claim-evidence-20261029/unit-tests-v2.txt
  sources_read_this_followup:
    - tools/claim_evidence_matrix.py
    - tests/test_claim_evidence_matrix.py
    - research/historical-claim-evidence-20261029/README.md
    - research/historical-claim-evidence-20261029/build_seed.py
    - research/historical-claim-evidence-20261029/matrix.json
    - research/historical-claim-evidence-20261029/integrity.json
    - research/historical-claim-evidence-20261029/integrity-v2.json
    - research/historical-claim-evidence-20261029/unit-tests-v2.txt
  prior_instruction_sources: Listed in original-review.md; no additional instruction or sibling review files read.
  read_sibling_reports: false
  blind_from_respected: null
  verdict: holds
  verdict_scope: Previously reported implementation defects are resolved; remaining memory amplification is disclosed. No scientific verdict.
  verification:
    - isolated exact-limit acceptance and over-limit pre-fetch refusal
    - isolated CLI oversize refusal before JSON parsing
    - isolated subprocess environment inspection
    - AST check of full archive literal
    - immutable matrix and receipt byte comparisons and SHA-256 check
  unit_test_suite_rerun: false
  network_calls: none
  experiments_or_native_builds: none
  repository_mutations: none
  authorized_report_writes:
    - /home/ec2-user/scratch/claim-evidence-code-review-20261029/original-review.md
    - /home/ec2-user/scratch/claim-evidence-code-review-20261029/fix-review.md
```
