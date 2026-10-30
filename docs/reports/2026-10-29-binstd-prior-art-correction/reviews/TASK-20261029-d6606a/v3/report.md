# J1 independent V3 recheck — TASK-20261029-d6606a

**Verdict: holds for the V3 candidate attribution claim; R1 is closed in this successor.** Snapshot `c49b7f123d21e4a9c03465f3c56003a3df9917dd` corrects the three provenance entries identified in the sealed review of `dd603f5db2f92076663850fe4c5dd859dc1edb0c`. This is acceptance of the bounded metadata correction, with the original review's scientific, validation and application limits retained. The original report and attestation remain unchanged.

The source base remains `7e45528b293fd42049b1486a03135670ab5ac55c`. I first read `handoff-v3.json` at the successor snapshot and then independently compared the complete parsed V2 and V3 documents using a duplicate-key-rejecting loader and recursive type-sensitive comparison. No producer checker was imported or executed. [check_v3_independently.py](check_v3_independently.py) records the independent method; [output.json](output.json) retains exact changed paths, source hashes, targeted errors and controls.

The complete candidate difference is:

| Candidate | Exact V2-to-V3 change |
| --- | --- |
| IDEA-20261003-43f871 | Byte-identical. |
| IDEA-20261003-4f41d0 | `idea.prior_art.nearest[0].provenance`: `kb` to `retrieved`; add `verified_by` for KR-IC-5765d2. |
| IDEA-20261003-94078e | The same two key changes for KR-IC-73db3f. |
| IDEA-20261003-c9c6c3 | The same two key changes for KR-IC-73db3f. |

No other candidate key or value changes. An additional complete comparison against each original effective source again found no changes outside `idea.prior_art`. Thus the original review's exact lineage preservation, truthful SAT/XOR and factor-base comparison content, historical search preservation, retrospective date, heuristic limitations, and unchanged scientific fields continue to hold.

Each added `verified_by` mapping names `Codex coordinator /root; T-782 / TASK-20261029-8b1359`, dates the reading to `2026-10-29`, describes direct Git reading, and expressly disclaims retrieval-index resolution. Each binds the correct card path, source commit and independently checked source SHA-256. The scope says this was repository-card attribution and comparison only, with no new full-text literature verification and no independent verification of the card findings. That wording describes the documented access and satisfies the provenance distinction in source-base `docs/agent-contract-extended.md:1024-1029`. It does not backdate reading to the proposal, manufacture a historical search, promote a heuristic to a theorem, or turn a card's recorded findings into a newly verified result. This review verifies the submitted reader attribution and source binding; it does not independently observe the coordinator's past cognitive act of reading.

All eight V3 handoff bindings pass. All 24 bindings in the original handoff remain unchanged at the successor. All 22 source records and the registry match their original pinned SHA-256 values at the successor. The V3 manifest correctly binds each previous V2 candidate, each new candidate, and the new candidate's proposed registry target digest. Original/effective paths and hashes, previous selected registry entries, proposed destination paths, and all other proposed route fields are unchanged. The existing registry remains byte-identical and no correction was applied.

The unmodified pinned validator was loaded from the original reviewer's verified scratch copy with its real resolver and six-card scratch tree. On the four effective source documents it again returned the same four prior-art errors; on the four V3 candidates it returned zero. This is the targeted `check_prior_art` function result only. The original scratch registry checks continue to support the unchanged path structure; this narrow recheck independently verified the successor content hashes and manifest bindings rather than claiming a live registry test.

I ran 21 focused negative controls, seven for each corrected entry. The independent provenance guard rejected: false `kb` provenance; a missing `verified_by` mapping; a wrong card hash; a wrong card path; a backdated reading date; a mismatched agent identity; and a scope asserting new full-text/theorem/finding verification. Every control passed. These are independent metadata-contract checks derived from R1 and the pinned source identity. The real prior-art validator does not enforce these semantic requirements; its zero-error result alone did not close R1.

The original report, attestation, independent script and output hashes were rechecked and remain unchanged. The original review preserves its `breaks` verdict for the V2 snapshot; this separate report records the correction at the V3 snapshot. No sibling reports, other agent history, memory, network research, package installations, native builds, experiments, or whole-corpus scans were used. All writes are confined to this `v3-recheck/` directory.

There are no remaining actionable findings within the narrowed V3 recheck. The report packet still does not authorize ledger or registry writes. It establishes no full-ledger pass, literature theorem verification, historical preapproval, experiment validity, performance claim or CI result. Future live application requires the separately admitted scope, current source and registry guards, preservation of prior records, complete current-tree validation and delivery checks already named in the review plan.
