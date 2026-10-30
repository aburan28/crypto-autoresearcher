## TASK-20261028-0db201 — M derivation

**PASS for deriving and preparing M from C2. STOP before committing or releasing if the parent cannot refresh the live claim, branch/PR publication, and deadline.** This session verified C2’s committed bytes and the locally live epoch-1 claim at approximately 05:04–05:07Z. It did not create M, run the verifier on an M candidate, publish metadata, or release A. The parent’s remote and PR proofs are time-stamped; they must be rechecked by the control plane before those actions.

### C2 and ownership pins

- Local `HEAD` was **`8c09dd3381fe7bf1dbf1675c64dd6379c6554d62`** on `codex/reln-custody-archive-20261029`. Direct `git show` gave its sole, full first parent as **`7e45528b293fd42049b1486a03135670ab5ac55c`**. C2 is an ancestor of the verifier’s then-current HEAD.
- C2’s message contains the archive task ID and every required `record_ids` entry: `DEC-20261028-99a724`, `TASK-20261028-20d746`, `TASK-20261028-0db201`, `TASK-20261028-43b2e0`, and `TASK-20261028-73c568`. `git diff-tree` and the direct parent diff showed **one changed path**, [the queue](/home/ec2-user/crypto-reln-p-custody-20261028/coordination/goals/GOAL-RELN-001/batches/BATCH-0834cb/dispatch_queue.json): P’s `state` changed from `queued` to `completed`.
- [C2 publication proof](/home/ec2-user/spot-codex-tmp-recovery-20261029/reln-A-C2-publication.json), SHA-256 `e8f2c14a8d0e7600f13a27f0e6e7b9db52c34b470f49e53445ef6b52e12abd88`, records remote head C2 at **05:02:13Z**. [PR proof](/home/ec2-user/spot-codex-tmp-recovery-20261029/reln-A-C2-pr-publication.json), SHA-256 `48821f85a55f6a2dfe0c4e8656cc97bf4d4240e76363f72c3c014bb3f896351d`, reports **PR2685 OPEN**, head branch `codex/reln-custody-archive-20261029`, head OID C2, base OID C2’s parent, and `autoMergeRequest: null`. These files do not establish a later remote state.
- The [claim](/home/ec2-user/crypto-reln-p-custody-20261028/coordination/goals/GOAL-RELN-001/batches/BATCH-0834cb/claims/TASK-20261028-0db201.1.claim.json) still hashed to `89d9838c23e10830fdc40e3f7114a90e54a14d03cb0b6176d32eb8462c0c7762`. Native refs-aware readback found A **live**, epoch **1**, owner `coordinator-reln-archive-20261029`, owning parent session `01a179ee-06bf-7550-bc38-0d98c7e3b9c8`, no release, expiry **05:29:44Z**. Claim publication commit `19eb16d3aeeb98f926a52bf5c0007d1dc09b22da` is an ancestor of C2. The claim’s recorded branch remains the earlier admission branch; do not edit that immutable claim.
- The P completed release still hashed to `885fe953d65e61c7d881a2d6ba90e6a16cb800322790ccaab6a08cc17fd8c3bd`. Its 21 artifact hashes matched C2’s 21 P blobs.

Direct Git reads checked **all 31** `C2:path` objects for blob type, OID, byte count, and SHA-256 against the C2 proof: **31 checked, zero mismatches**. The proof paths are unique and equal precisely the queue’s P21 plus A10 declared `artifact_paths`; the P21 hash map equals the completed release’s map. This is a C2 content check, not a native verification of the future M queue.

### Exact C2 content map

`B/` below expands to `coordination/goals/GOAL-RELN-001/batches/BATCH-0834cb/`. `P/` expands to `B/tasks/TASK-20261028-20d746/`. Columns are **path, C2 SHA-256, C2 Git blob OID**. These are the 31 entries for M’s `archive.path_sha256`; OIDs are comparison pins and are not values in that SHA-256 map.

| Path | SHA-256 | Blob OID |
| --- | --- | --- |
| `P/capsule/source-content/TASK-20261001-84833e/derive_f2_p5.py` | `26bb182b3b42c438e16f71d5821af90208e9127f13e0d4c924bb829cafe1123d` | `140e27d6914b3424571b556e0992fb8a9edd05a9` |
| `P/capsule/source-content/TASK-20261001-84833e/derivation_output.json` | `60bc1953d4beb3b5bf83daec8972129f41d4d5443e8bb6cb2c0b0c44a9812599` | `ea79a0f2b95ca75d6e3cdac2e6d9c778f765c2bf` |
| `P/capsule/source-content/TASK-20261001-84833e/derivation_report.yaml` | `227f9c7e20acb92fd6b00641aaea2a10c41c1067325c948c5320e69e7530d5a4` | `42ac59477a31f9f66a841e747efa7ff5012fad0c` |
| `P/capsule/source-content/TASK-20261001-84833e/stderr.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391` |
| `P/capsule/source-content/TASK-20261001-8615ec/rederive_f2_p5.py` | `0dee2d59a641805609d8bf3d2d5aa90da55cdef4d65db511b42bd6c93c987552` | `f843823934becdd2a3d40981ea1168e727c68729` |
| `P/capsule/source-content/TASK-20261001-8615ec/rederivation_output.json` | `e4dbb382ff43d927a61eab3bb00f5c009ced6d12498404b2c0e5281a01477232` | `817f61003ef331c8dff97d2bee97c7bbb071c01e` |
| `P/capsule/source-content/TASK-20261001-8615ec/rederivation_report.yaml` | `ac64d3566fd9bb919f6607de67bfb1f9298afeda8c27fcaced460c15084c1df2` | `42f74bfb519ac7dabee6ef92c9bc426fc88305cd` |
| `P/capsule/source-content/TASK-20261001-8615ec/stderr.log` | `e888f3ef50ec9507d6e1037a380bb9a3cf04828a03e84552dd2bedb4b8398c20` | `cfbf0cba914e23429b9f55a0fa5f5299453de91d` |
| `P/capsule/receipts/precommit/snapshot-receipt.json` | `69454715a52bc20977a3743cc4843a05a3402d714c82d6620794f18ad04138a8` | `a2dff8aaa14644c5746f7bf4146f0fc03f4d86e3` |
| `P/capsule/receipts/backfilled/snapshot-receipt.json` | `9ac3638ce0cc74e80c71b3717dfb7fd97476a343079e35ccec63a3cc9ddcb588` | `b37e446be863251c2de6135211de67f78fc54825` |
| `P/capsule/claims/TASK-20261001-84833e.1.claim.json` | `3f526c3c179382ecc14bbb5ee79de6c4095e289a4632cc65094df91728e27e9e` | `944570c4267b81e16f6da93b366124e5bcf4474b` |
| `P/capsule/claims/TASK-20261001-84833e.1.release.json` | `fdca16bfdf64450895369d832be1751cee718aae0a866c91ca2bb69e6f59322b` | `c6762da5c8a6c2d8dbe6d3b6e1859eb4037fb0dc` |
| `P/capsule/claims/TASK-20261001-84833e.2.claim.json` | `0be2f2ed4681001f93c15e5402241adfe52cc6f3689ae7cbcb305837ad8d4692` | `1d0585fab5df6a8cc49b7b0220bf6e24aaa6c82c` |
| `P/capsule/claims/TASK-20261001-84833e.2.release.json` | `c605605c44b55f0ccc4b15878b8211d3eaed6f10dbe56b54a3549c3a64703475` | `ac5a27590e179dca38f4ef777a3e542f02593f04` |
| `P/capsule/claims/TASK-20261001-8615ec.1.claim.json` | `add18f7b9a29325ddccb7556a2f064120cbd93345d65eb0cc00dc3c20f221dd0` | `e225926251b3e2ad460ea04d966e2e2c31044897` |
| `P/capsule/claims/TASK-20261001-8615ec.1.release.json` | `788c1cb50e26d77a2ec305f706831e7be54054da604b8485a2c437037db9cb2f` | `b41d9251cfc1865153c589911770e2a5ab1f2a6c` |
| `P/capsule/claims/TASK-20261001-93c38a.1.claim.json` | `7ab198697013809cd5116af23876f9810a86f025046a04178c208023044491a9` | `7c35120f8ae20120d09310909ffdcebdfcd032b1` |
| `P/capsule/claims/TASK-20261001-93c38a.1.release.json` | `7fd13566363580f85e83d297b531cb87e4683e1bb2a13a161f086cc4b3147a51` | `36e651c49fb998568d854ab88d79ae61bcded9b4` |
| `P/capsule/lane/BATCH-79a580.lane.json` | `c47b1881c47443fddec5f48be535c8b52746763758646c8b759fa184e6bc0a49` | `803cf8bd700286d99cfa2d1dd617fefa0d1ebe12` |
| `P/import-manifest.json` | `19415a5ab5f95e65d85a7ecc04c689058bdb59c9b5ac4c4725ac534b742a962b` | `b04336b5eb3e290f5cef1e0d813f04795ff56de3` |
| `P/custody-report.json` | `798a6c039995e13a0d4023d87515d1a43e416452a68eebaa5f96114cf4f838a0` | `d277cb73d948cd4195332c004b4431bd20e03034` |
| `ledger/decisions/DEC-20261028-99a724.yaml` | `267f4e015a99478a680552f9e87b56a5d692ebb013624cde2b371d6ca87e62c8` | `86184e9f3d6e5bcbe501be377d0ed9e6f241b243` |
| `ledger/handoffs/TASK-20261028-20d746.yaml` | `b69862d00af54628084940d9c57a1f613b7db855a276de44e84ee2d44ee58367` | `f2c41b844ba18c83432cfeae4c357c133d32831d` |
| `ledger/handoffs/TASK-20261028-0db201.yaml` | `c1cdefce14d692613539a0137082e0ae896029c046175ab9588cc1fe8f97896a` | `a02a037c6f2bd8731a212b80abc8708bf5820704` |
| `ledger/handoffs/TASK-20261028-43b2e0.yaml` | `e2721ebea136bb1cd4e9d0d513499b7ce653cf94ebe48ad91f7ce10e1d3ba889` | `ec6e0ca8bb4954c37270537b0882d00853ffba86` |
| `ledger/handoffs/TASK-20261028-73c568.yaml` | `916f365ff6b79302caba3b6260cb5f034fccb2158538894074f4069fc5a1bd05` | `a4449d43bd51e48fda86293e32935ba4898767d8` |
| `B/dispatch_queue.json` | **`fefa018aa9307c7ee3365fe216aa5d3602c5b4c35c62382a4329fe79af59ec28`** | **`de5c1d8aa489c98a5f5972f8df4cef371c399223`** |
| `B/source-bindings.json` | `697feb24a26bfb8cec018a5255b35e845c655c83a44c0e3f3e83359e9b209ab2` | `cc025ca46c16a3403a07c99a1fae58b3ece7bae7` |
| `B/custody-review-plan.yaml` | `15b735e8c455e2a66c943b555f75ce13e8e4018145cf4c6bda7927f43630b63a` | `5899a8ad1081ff58175668ac09a4436bc43905ac` |
| `ledger/goals/GOAL-RELN-001/checkpoints/BATCH-0834cb-20261028-custody-opening.yaml` | `34c8542644280a368a21b8218a480b4a69383bb3af1ec31067be2645edd17f29` | `b53fde6e4764097e763ab34cc1578a5f36ad2d7a` |
| `coordination/goals/GOAL-RELN-001/lanes/BATCH-0834cb.lane.json` | `e59225cbe68717df916d88b2ca2b6e60db0c559fff0995e9ac23751e4255a54a` | `226304777a8a41c1a64b32b0ab1bef81404b51b7` |

The C2 queue SHA-256 and OID above differ from plan002’s earlier HEAD values (`09ddd7…`, `1ca0da…`) because C2 recorded P’s completed state. **M must bind the C2 queue bytes**, even though M will subsequently change the live queue again.

### Minimal M queue change

In A’s entry only, change `state` from `queued` to `completed`; set:

```text
archive.commit_sha = 8c09dd3381fe7bf1dbf1675c64dd6379c6554d62
archive.parent_sha = 7e45528b293fd42049b1486a03135670ab5ac55c
archive.path_sha256 = the 31 path→SHA-256 entries in the table above
```

Retain `kind: snapshot`, `binding_mode: content_at_commit`, `source_task_ids: [TASK-20261028-20d746]`, and the five existing `record_ids`. Retain P as `completed`; do not promote V (`blocked`) or L (`queued`) or change their archive blocks. The final receipt is **not** a 32nd content path.

For an unambiguous machine derivation of the complete JSON hash map from C2, the parent can use the C2 proof only after checking its SHA-256 and the direct Git blobs, as done here:

```sh
jq '[.paths[] | {key: .path, value: .sha256}] | from_entries' \
  /home/ec2-user/spot-codex-tmp-recovery-20261029/reln-A-C2-publication.json
```

The resulting key set must equal the P and A `artifact_paths` union in **C2’s committed queue** and contain exactly 31 entries. Do not hash M’s working-tree queue for this field.

### Receipt candidate and verification

The exact deliverable is [A’s receipt](/home/ec2-user/crypto-reln-p-custody-20261028/coordination/goals/GOAL-RELN-001/batches/BATCH-0834cb/archives/TASK-20261028-0db201/receipt.json); it did **not** exist at this read. The repository’s existing `crypto.autoresearch.archive_receipt.v1` example supports these fields and meanings:

- `schema`, `task_id`, `goal_id`, `batch_id`, and actual `recorded_at`.
- `claim`: actual owner, epoch **1**, and claim publication commit `19eb16d3aeeb98f926a52bf5c0007d1dc09b22da`.
- `archive`: an exact copy of A’s completed queue archive block, including actual C2, actual parent, and the 31-entry C2 map.
- `expected_paths`: those same 31 paths, with no receipt path.
- `verification`: the **actual** native invocation, return code, stdout/stderr, and checked C2-tree scope after the parent runs it. Leave any pass result unset until it occurs.
- Source pins: P’s completed-release path and SHA-256 `885fe953d65e61c7d881a2d6ba90e6a16cb800322790ccaab6a08cc17fd8c3bd`, and the P21 completion-check manifest SHA-256 `3b25412cae1ff2a0b267037be99b5589f0666e48a9fd2207a7a9c0ec5e1de40e`. State exactly what was checked; do not convert custody into scientific acceptance.
- `self_reference_policy`: receipt excluded from `artifact_paths` and `path_sha256`; M’s later queue bytes may differ because verification reads C2’s tree.
- `scientific_trials_launched: 0`, `scientific_status_changes: []`, `goal_status: active`, `metadata_publication_verified: false`, `merge_verified: false`, and accurate `remaining_gates`/`asserts_nothing_about` text at M creation. No M SHA or later remote success can be placed in the receipt before it exists.

The parent must check the **actual** receipt’s size and `docs/artifacts.md` policy before staging it. A tracked non-code `.json` over 1 MiB requires the artifact-store route; an oversized output or unavailable authorized route is STOP. No such receipt or size check was fabricated here.

After preparing the M candidate, run both native modes before claiming success:

```sh
GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1 \
python3 tools/research_dispatch.py \
  coordination/goals/GOAL-RELN-001/batches/BATCH-0834cb/dispatch_queue.json \
  --claims off --ready-only

GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1 \
python3 tools/research_dispatch.py \
  coordination/goals/GOAL-RELN-001/batches/BATCH-0834cb/dispatch_queue.json \
  --claims refs --ready-only
```

The first tests the queue without claim-overlay help. The second includes current refs-aware ownership. For a completed A, native `content_at_commit` verification requires C2 to resolve and be an ancestor of verifier HEAD, its declared parent to equal C2’s first parent, all 31 declared hashes to match blobs **at C2**, and every required ID in C2’s message. It does not verify remote publication, the receipt’s prose, independent V review, or scientific claims. Record actual command results in the receipt, commit M, rerun native verification at M HEAD, publish M to PR2685, and recheck PR head, remote branch, claim epoch, and deadline. PR2685’s proof currently shows no auto-merge request; apply the repository’s normal PR gates without asserting they have passed.

Only after M exists, verifies, and is published may the parent create the **exact-epoch completed release**. `goal_lanes.py` automatically hashes A’s ten `artifact_paths` in their then-current form—including the M-version queue—but does **not** automatically hash the receipt deliverable. Supply its actual, post-write digest explicitly:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tools/goal_lanes.py release \
  coordination/goals/GOAL-RELN-001/batches/BATCH-0834cb/dispatch_queue.json \
  TASK-20261028-0db201 \
  --as coordinator-reln-archive-20261029 \
  --expected-epoch 1 \
  --outcome completed \
  --artifact coordination/goals/GOAL-RELN-001/batches/BATCH-0834cb/archives/TASK-20261028-0db201/receipt.json=ACTUAL_SHA256 \
  --publish
```

Replace `ACTUAL_SHA256` only after hashing the real receipt. Use no missing-artifact override. Recheck the published release’s owner, epoch, receipt hash, and remote/PR state; none is established by this turn.

The two historical receipt versions and all BATCH-79a580 bytes remain separate and unchanged. The missing `GOAL-` alias was still absent at C2 and remains unresolved. C2 and M do not repair historical admission or the original off-main archive. The frozen review plan still assigns V its independent custody audit; L disposition remains later work. Preserve NA-2, the full 12-fixture panel, all C-7, free-space, watchdog, worker, `nice10`, literal path, model, transport, and independent-review holds. **No administrative custody step licenses a scientific result or status change.**