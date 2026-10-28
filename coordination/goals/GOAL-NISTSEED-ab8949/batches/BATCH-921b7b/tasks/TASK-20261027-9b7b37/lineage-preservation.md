Source-only custody record for TASK-20261027-9b7b37

Producer: Coordinator administrative producer; resumed thread 01a17f35-4995-7a02-b1cd-6d91be89d30a. Base HEAD 3a447e13d0c2410c760dfe41a1ef2bc599a28d9a; local origin/main fad6be5442fa1e4f7cad6d3cfd2911f44cd1c1f0. Provenance: internal; verified_by: TASK-20261027-9b7b37.

Observation: 34 exact byte exhibits cover nine original paths at four pinned commits; the two postcommit-receipt positions at snapshot time are absent. Each present exhibit passed full SHA256, tree blob OID and computed Git blob OID checks. Every copied .py is an inert custody exhibit. Scientific runs, original-program calls, VM calls, storage operations and copied-source imports: zero. Administrative process address-space limit: 2 GiB.

Primary-source review before production used AGENTS.md, agents/coordinator.md, the entire handoff and matching queue entry, source-inputs.json, review-plan.yaml, DEC-20261027-9eed13, the linked custody and A/A delivery problem records, task/lane contracts and native allocator, merge-hygiene, dispatcher and ledger validators. Their exact current hashes are in nine-path-inventory.json. No paper or scientific claim is made; scientific literature, runtime availability, later-run raw evidence and global T-5518 ownership are outside this administrative act. Local Git and workflow sources are the relevant primary sources. No external source was needed or silently substituted.

The four ref labels remain pinned labels even when a moving branch changes. Full commits:

- main_snapshot: `f80cf4fbf023f4d1722062d458d5d4b72ed9bcfb`

- branch_snapshot: `592ea372d4e75a2a3e7ac6b212ef926b9284079c`

- main: `f4b7d51b8d2c48beab3226424da35f3cfd628aac`

- branch_head: `0ebd30f4752866d99a50bac93584c64cb33f956b`

- envelope_base: `6315b3eb95266a8596ac2c1fdc0892d72e7b0434`


Independent main snapshot map

Qualified archive: TASK-20261025-5dd15e at queue `f4b7d51b8d2c48beab3226424da35f3cfd628aac:coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-62db73/dispatch_queue.json`. Snapshot `f80cf4fbf023f4d1722062d458d5d4b72ed9bcfb`, first parent `54838684121586697ad7c38354bac45cf6e26578`. Binding mode `commit`. Actual changed-path set is exactly the six entries below; all six raw SHA256 values match. Queue metadata and the later postcommit receipt agree with this map.

The precommit snapshot receipt retains commit_sha=null and five source hashes; its own hash is supplied by the later six-path map. The postcommit receipt is absent at this snapshot, so no file is invented there. The archive describes zero-run mocked source. The checks here authenticate custody bytes, not the tests or scientific statements embedded in them.

- `experiments/EXP-NISTSEED-6886da/aa-admission/aa_fixture_producer.py`: `64035dcafbc4df4ee015c82d6156fc5a3090857d448df5d34f40fb033b496481`

- `experiments/EXP-NISTSEED-6886da/aa-admission/test_aa_fixture_producer.py`: `626778ba8967654985f595e13cf809b55a4c3a0efbaa7d7d31e17031058a8bbb`

- `experiments/EXP-NISTSEED-6886da/aa-admission/aa_fixture_schema.json`: `3f7a16ddec9fb3efd0d0fbd99810e78c1d6040d77c9bfb0282900b7218b51a21`

- `experiments/EXP-NISTSEED-6886da/aa-admission/test-report.txt`: `d0b21f534591a70b4c5c1189eb7ad61ecdc7166012c129cfa09204dc81bd2f52`

- `experiments/EXP-NISTSEED-6886da/aa-admission/IMPLEMENTATION_REPORT.md`: `2acc75dd827f3593c8fa58d88da75dd78e970fa53f21e0f7c60fbed558be6ba7`

- `coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-62db73/archives/TASK-20261025-5dd15e/snapshot-receipt.json`: `3374cd05a5d85046ca26b648a4b5b8ebb63166e713a0dbdb93c12c7de3c75bdc`


Claim/release timeline reconstructed from this pinned lineage alone:

- 2026-10-25T02:13:38Z: claim `TASK-20261025-ad9d68` epoch 1, owner `executor-nistseed-aa`; expires 2026-10-25T04:13:38Z; supersedes null. Source `f4b7d51b8d2c48beab3226424da35f3cfd628aac:coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-62db73/claims/TASK-20261025-ad9d68.1.claim.json`; SHA256 `89d4e49a777afb1d493722db5730aab9752a86bcd874a72383536482365a8a92`.

- 2026-10-27T05:50:47Z: claim `TASK-20261025-ad9d68` epoch 2, owner `executor-nistseed-aa-20261027`; expires 2026-10-27T08:50:47Z; supersedes {"epoch": 1, "owner": "executor-nistseed-aa", "status": "expired"}. Source `f4b7d51b8d2c48beab3226424da35f3cfd628aac:coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-62db73/claims/TASK-20261025-ad9d68.2.claim.json`; SHA256 `59e19f4e218a09fdd13ef4fb1ef3c8c15ca27360b69821d19231bfc60af4277f`.

- 2026-10-27T06:00:55Z: release `TASK-20261025-ad9d68` epoch 2, owner `executor-nistseed-aa-20261027`; outcome completed; its artifact hashes match this lineage snapshot. Source `f4b7d51b8d2c48beab3226424da35f3cfd628aac:coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-62db73/claims/TASK-20261025-ad9d68.2.release.json`; SHA256 `71fdd0161183d8395328a58ccee55591fc559948447c24b44617bb71cbc34a26`.

- 2026-10-27T06:01:09Z: claim `TASK-20261025-5dd15e` epoch 1, owner `coordinator-nistseed-aa-20261027`; expires 2026-10-27T09:01:09Z; supersedes null. Source `f4b7d51b8d2c48beab3226424da35f3cfd628aac:coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-62db73/claims/TASK-20261025-5dd15e.1.claim.json`; SHA256 `cbacb61311284f747ccf1bcf751e7cf990a82f6b2818b229340f0a4ff4e75ada`.

- 2026-10-27T16:38:40Z: claim `TASK-20261025-5dd15e` epoch 2, owner `coordinator-nistseed-aa-recovery-20261027`; expires 2026-10-27T19:38:40Z; supersedes {"epoch": 1, "owner": "coordinator-nistseed-aa-20261027", "status": "expired"}. Source `f4b7d51b8d2c48beab3226424da35f3cfd628aac:coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-62db73/claims/TASK-20261025-5dd15e.2.claim.json`; SHA256 `ac4ac47f36427d7eb978942219b4c7b473734e4291925559f0f2591774a00cf2`.

- 2026-10-27T16:44:56Z: release `TASK-20261025-5dd15e` epoch 2, owner `coordinator-nistseed-aa-recovery-20261027`; outcome completed; its artifact hashes match this lineage snapshot. Source `f4b7d51b8d2c48beab3226424da35f3cfd628aac:coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-62db73/claims/TASK-20261025-5dd15e.2.release.json`; SHA256 `868fd29097a6ec7f3cc913ed7bee80446dff637869596edee2b8671b28bbb4a1`.

Main producer epoch 2 and archive recovery epoch 2 are distinct from branch epochs, despite shared TASK IDs.


Independent branch_head snapshot map

Qualified archive: TASK-20261025-5dd15e at queue `0ebd30f4752866d99a50bac93584c64cb33f956b:coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-62db73/dispatch_queue.json`. Snapshot `592ea372d4e75a2a3e7ac6b212ef926b9284079c`, first parent `fcbbdc25372e155f2b7c4c0c7a678980d5487a50`. Binding mode `commit`. Actual changed-path set is exactly the six entries below; all six raw SHA256 values match. Queue metadata and the later postcommit receipt agree with this map.

The precommit snapshot receipt retains commit_sha=null and five source hashes; its own hash is supplied by the later six-path map. The postcommit receipt is absent at this snapshot, so no file is invented there. The archive describes zero-run mocked source. The checks here authenticate custody bytes, not the tests or scientific statements embedded in them.

- `coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-62db73/archives/TASK-20261025-5dd15e/snapshot-receipt.json`: `67bc8acb796ede933e3329e69e2b5732e2d899a5c71cd61acb975db5bae37f0d`

- `experiments/EXP-NISTSEED-6886da/aa-admission/IMPLEMENTATION_REPORT.md`: `1625026138582e3fab39e7a4cf30f116b0b89c80bb34aff3f47f6d3e10be8c1a`

- `experiments/EXP-NISTSEED-6886da/aa-admission/aa_fixture_producer.py`: `d481423ee4562c345d575f1dbd8f57a1dd5184e2c599c813a2f91154e790ef18`

- `experiments/EXP-NISTSEED-6886da/aa-admission/aa_fixture_schema.json`: `c8f4f81ef3a092b3ea9360d568802b0b7e346245d02cae7e4f7a01e4af3d3087`

- `experiments/EXP-NISTSEED-6886da/aa-admission/test-report.txt`: `2af104d75aa50ae09562ff7c02e5ec924b0ce42f6dc1ea20e016d198cde2eecb`

- `experiments/EXP-NISTSEED-6886da/aa-admission/test_aa_fixture_producer.py`: `e0dc3abcd3519e54f3cc8d00ee34da4d595b6714c9827a26f648fcb33a21ccc9`


Claim/release timeline reconstructed from this pinned lineage alone:

- 2026-10-25T02:13:38Z: claim `TASK-20261025-ad9d68` epoch 1, owner `executor-nistseed-aa`; expires 2026-10-25T04:13:38Z; supersedes null. Source `0ebd30f4752866d99a50bac93584c64cb33f956b:coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-62db73/claims/TASK-20261025-ad9d68.1.claim.json`; SHA256 `89d4e49a777afb1d493722db5730aab9752a86bcd874a72383536482365a8a92`.

- 2026-10-26T21:47:58Z: claim `TASK-20261025-ad9d68` epoch 3, owner `executor-nistseed-aa-public101`; expires 2026-10-26T23:47:58Z; supersedes {"epoch": 2, "owner": "executor-nistseed-aa", "status": "expired"}. Source `0ebd30f4752866d99a50bac93584c64cb33f956b:coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-62db73/claims/TASK-20261025-ad9d68.3.claim.json`; SHA256 `c60f8c3cd87dbbbc3a00a59c38f2d0e25681c279796e4e7797d97ef69de4c432`.

- 2026-10-26T22:33:57Z: release `TASK-20261025-ad9d68` epoch 3, owner `executor-nistseed-aa-public101`; outcome completed; its artifact hashes match this lineage snapshot. Source `0ebd30f4752866d99a50bac93584c64cb33f956b:coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-62db73/claims/TASK-20261025-ad9d68.3.release.json`; SHA256 `a8fb87cfdf89bb67d5d31a241473c281794142813e226cf20e0eba2466731329`.

- 2026-10-26T22:35:00Z: claim `TASK-20261025-5dd15e` epoch 1, owner `coordinator-nistseed-aa-archive`; expires 2026-10-26T23:35:00Z; supersedes null. Source `0ebd30f4752866d99a50bac93584c64cb33f956b:coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-62db73/claims/TASK-20261025-5dd15e.1.claim.json`; SHA256 `eaf4df8d672735302531a9eb7629d5933c81440eb47686e783e693495177a083`.

- 2026-10-26T22:43:49Z: release `TASK-20261025-5dd15e` epoch 1, owner `coordinator-nistseed-aa-archive`; outcome completed; its artifact hashes match this lineage snapshot. Source `0ebd30f4752866d99a50bac93584c64cb33f956b:coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-62db73/claims/TASK-20261025-5dd15e.1.release.json`; SHA256 `473d047529b9d7b290090f860c283db872736aca9f14497583f4199f2ce31140`.

The branch producer epoch 3 supersedes epoch 2, but no epoch-2 producer claim is present in this pinned branch claims tree. Its bytes and ownership are not invented.


Later branch source evolution

The four changed AA files between 592 and pinned branch head are listed below. aa_fixture_schema.json is byte-identical across those two refs. All five branch-head AA files match source publication commit `01980761a4f01b9209fc4095f39ce43a5b8e94a7`. Evolution commits `95b9f589450aa6aba514e9e1a6bded0ee3f262f3` and `ad6701f095f1df051ccb5299916ff85e7f56f29e` were read for metadata and changed paths; exact results are in the inventory. Later source-reported real A/A/cohort work remains unvalidated source provenance and is not attributed to the 592 archive.

- `experiments/EXP-NISTSEED-6886da/aa-admission/IMPLEMENTATION_REPORT.md`: changed=true; 592 `1625026138582e3fab39e7a4cf30f116b0b89c80bb34aff3f47f6d3e10be8c1a`; branch head `473672a91746289f94b0aafd040a4933f8f38cc0c902baddd942aa0ae57f0c39`.

- `experiments/EXP-NISTSEED-6886da/aa-admission/aa_fixture_producer.py`: changed=true; 592 `d481423ee4562c345d575f1dbd8f57a1dd5184e2c599c813a2f91154e790ef18`; branch head `c24f0fe5255e5a2c9802445fd1c0f8afb6214819ef06c840fa7d2049e1300e10`.

- `experiments/EXP-NISTSEED-6886da/aa-admission/aa_fixture_schema.json`: changed=false; 592 `c8f4f81ef3a092b3ea9360d568802b0b7e346245d02cae7e4f7a01e4af3d3087`; branch head `c8f4f81ef3a092b3ea9360d568802b0b7e346245d02cae7e4f7a01e4af3d3087`.

- `experiments/EXP-NISTSEED-6886da/aa-admission/test-report.txt`: changed=true; 592 `2af104d75aa50ae09562ff7c02e5ec924b0ce42f6dc1ea20e016d198cde2eecb`; branch head `9dfeff83159f7c82d09120df13d656664b7b089b482bdce55059554262bc9d5d`.

- `experiments/EXP-NISTSEED-6886da/aa-admission/test_aa_fixture_producer.py`: changed=true; 592 `e0dc3abcd3519e54f3cc8d00ee34da4d595b6714c9827a26f648fcb33a21ccc9`; branch head `d98954ea520850d2687db3727eb296c649c81045538f5e4d86626f59d2efbd27`.


Native feasibility observation and interpretation

The producer conclusion is feasible=false for integrating both historical meanings through the inspected native alias/remap machinery without modifying completed bindings. This is a bounded implementation finding; preserving raw bytes and commit-qualified identities as inert exhibits succeeded. It is not a universal impossibility result.

Native checks and exact observed refusal messages (synthetic probes use deep copies or a temporary /tmp JSON description, never a registry write):

- `verify_original_archive_main`: accepted. 

- `verify_original_archive_branch_head`: refused. archive task TASK-20261025-5dd15e content hash mismatch for coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-62db73/archives/TASK-20261025-5dd15e/snapshot-receipt.json at HEAD: expected 67bc8acb796ede933e3329e69e2b5732e2d899a5c71cd61acb975db5bae37f0d, observed 3374cd05a5d85046ca26b648a4b5b8ebb63166e713a0dbdb93c12c7de3c75bdc

- `combine_original_queues`: refused. artifact path experiments/EXP-NISTSEED-6886da/aa-admission/aa_fixture_producer.py is owned by both TASK-20261025-ad9d68 and TASK-20261025-ad9d68

- `register_duplicate_archive_id`: refused.  ["branch-qualified/archive: duplicate ID TASK-20261025-5dd15e (also in main-qualified/archive)"]

- `schema_source_discovery`: unsupported. 

- `schema_source_discovery`: unsupported. 

- `schema_source_discovery`: unsupported. 

- `schema_source_discovery`: unsupported. 

- `native_schema_alias_probe`: refused. schema supersession kind 'ledger' does not match discovered source kind None: coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-62db73/archives/TASK-20261025-5dd15e/snapshot-receipt.json

- `renamed_archive_id_with_original_binding`: refused. archive task TASK-20261027-94e327 commit message is missing IDs ['TASK-20261027-94e327']

- `check_collisions_against_pinned_branch`: refused.  ["experiments/EXP-NISTSEED-6886da/aa-admission/IMPLEMENTATION_REPORT.md: identifier IMPLEMENTATION_REPORT is already published on 0ebd30f4752866d99a50bac93584c64cb33f956b with different content. Identifiers are immutable and never reused: reissue this record under the next free id (tools/allocate_id.py --next ...) and file a CORR recording the alias. Do not resolve this by choosing a side.", "experiments/EXP-NISTSEED-6886da/aa-admission/aa_fixture_producer.py: identifier aa_fixture_producer is already published on 0ebd30f4752866d99a50bac93584c64cb33f956b with different content. Identifiers are immutable and never reused: reissue this record under the next free id (tools/allocate_id.py --next ...) and file a CORR recording the alias. Do not resolve this by choosing a side.", "experiments/EXP-NISTSEED-6886da/aa-admission/aa_fixture_schema.json: identifier aa_fixture_schema is already published on 0ebd30f4752866d99a50bac93584c64cb33f956b with different content. Identifiers are immutable and never reused: reissue this record under the next free id (tools/allocate_id.py --next ...) and file a CORR recording the alias. Do not resolve this by choosing a side.", "experiments/EXP-NISTSEED-6886da/aa-admission/test-report.txt: identifier test-report is already published on 0ebd30f4752866d99a50bac93584c64cb33f956b with different content. Identifiers are immutable and never reused: reissue this record under the next free id (tools/allocate_id.py --next ...) and file a CORR recording the alias. Do not resolve this by choosing a side.", "experiments/EXP-NISTSEED-6886da/aa-admission/test_aa_fixture_producer.py: identifier test_aa_fixture_producer is already published on 0ebd30f4752866d99a50bac93584c64cb33f956b with different content. Identifiers are immutable and never reused: reissue this record under the next free id (tools/allocate_id.py --next ...) and file a CORR recording the alias. Do not resolve this by choosing a side."]

The main native archive verifies with no content-only fallback. For the branch archive, the original 592 commit exists but is not an ancestor of this main-based HEAD; the native commit-mode fallback compares HEAD content and refuses the branch receipt SHA256. Direct verification of all six bytes and parent at 592 passes. These are different questions; the native refusal does not invalidate the historical snapshot. No fallback was bypassed. Renaming an archive task while retaining its historical commit also fails the immutable commit-message ID check.

Schema supersession is keyed by repository source path. Its discovered kinds exclude the AA source/report and coordination archive/claim/queue paths. The synthetic source_commit/source_blob_oid fields do not make an unsupported source kind valid. Legacy remapped_ids map one path to one ID; run-id-remap-v1 covers RUN directory renames and provides no TASK dual-lineage resolver. check_merge_hygiene reports five AA collisions and excludes coordination paths via ID_DIRS; it cannot be cited as independently covering all nine. No native general correction JSON schema was found at schemas/correction.schema.json; nonexistent tool lookups tools/remap_ids.py and tools/remap_record_ids.py were read errors, then the actual validators and registries were inspected.

Both review rejection controls hold: an unqualified TASK-20261025-5dd15e cannot collapse the two six-path maps, and evolved producer SHA256 c24f0fe5255e5a2c9802445fd1c0f8afb6214819ef06c840fa7d2049e1300e10 does not match the producer hash archived at 592.


Prospective namespace, withheld from enactment

Native allocator/check returned locally free candidate BATCH-ccc24c, import task TASK-20261027-72083d, new archive task TASK-20261027-94e327, and source namespace EXP-NISTSEED-6bd651. Allocation/check stdout and all exact proposed exhibit destinations are in successor-alias-plan.json. These are suggestions, not registrations, claims, experiments or renames. They must be rechecked before any later use. CORR-20261027-db0489 remains the reserved prospective correction; its native occupancy check does not create or prove an alias. No import is recommended while feasibility is false.

A possible future act would leave main untouched, add commit-qualified byte exhibits at the exact prospective destinations and archive the NEW import at a NEW actual commit. The old 592 receipt and task IDs would stay historical data. That act still needs native representation, isolated snapshot, independent review, administrative disposition and normal publication gates; none is completed here.


Method, commands and limits

nine-path-inventory.json records the raw extraction and hash algorithms, full source identities, snapshot maps, timeline records and source hashes. custody-feasibility.json records exact native outcomes and the command ledger: each Git blob stdout is retained in its declared exhibit; command records bind stdout lengths and SHA256 rather than rewriting blob content. Allocator stdout and refusal messages are retained verbatim. All JSON is strict JSON, with explicit booleans/nulls and no NaN.

The administrative extraction driver used git ls-tree/show/rev-parse, SHA256(raw bytes), and SHA1 of the Git blob header plus raw bytes; it wrote only exclusive binary copies after pinned input checks passed. Snapshot checking separately compared parent, exact six changed paths, all six full hashes, queue map, postcommit map and commit-message task identity. Releases were matched by (commit, path, task_id, epoch, owner), and artifact hashes compared to their own snapshot. No receipt script, copied Python module or AA test was executed.

The runtime receipt `/home/ec2-user/nist-custody-producer-runtime-probe-20261027T2113.json` verifies the earlier read-only probe for this exact thread. Its SHA256 is in custody-feasibility.json. The current workspace-write authorization comes from the user turn; this producer did not manufacture a second runtime admission receipt or upgrade global model_verified.

T-5518 remains an unresolved source-side ownership reference; the handoff reports a local 404, which establishes neither global absence nor owner termination. No recreate/release action was performed.

The linked open problem remains `problems/nistseed-dual-archive-custody-20261027.md`. This task may write only its 38 declared artifacts, so new obstruction details are recorded here and in custody-feasibility.json rather than editing that problem record. Exit criterion: a separately reviewed native representation resolves both qualified historical bindings and later provenance, leaves every old byte/commit binding intact, and passes archive/ownership/collision checks. A problem pointer or a CORR narrative alone does not meet it.

Control plane duties remain isolated snapshot TASK-20261027-c8c73f, independent validator TASK-20261027-30109b under review-plan.yaml, and administrative ledger archive TASK-20261027-1b8cd8. The available independent review binding was unresolved in the frozen envelope; no independent review was attempted here. Source integration, protocol design/admission, real execution, storage access, scientific status and official decisions stay outside this act.

User scope overrides generic Coordinator fetch/merge/dispatch/receipt-writing steps: no .git writes, commits, push, PR, lane/queue/goal/ledger edits, claim release, subagent or session-receipt file. origin/main and the merge digest were inspected from existing refs; freshness beyond the local refs was not asserted. Cloud environment_status tool was searched for and unavailable; no network or credentials operation was attempted. No graph/PDF is produced: this is administrative custody rather than an experiment/evidence review/mathematical search, and only the 38 explicit paths are writable.

Final artifact and repository scope self-check is recorded in custody-feasibility.json. This producer leaves the 38 files uncommitted for control-plane verification.
