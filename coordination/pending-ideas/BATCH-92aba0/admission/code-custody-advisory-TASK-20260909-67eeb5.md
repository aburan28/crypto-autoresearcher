**TASK-20260909-67eeb5: read-only code advisory complete.** The ordinary archive verifier preserves a historical version of a code/test path through Git. It does **not** generally require that path’s latest worktree bytes to remain unchanged. The distinction changes for content-based archive verification, recovery bindings, and explicitly frozen record inventories.

All source citations below have provenance **`internal`**: I read these files during this task. The CI failure description is a parent-observed record, not an independently retrieved CI log.

1. **Completed archives normally verify historical Git blobs.**

   `validate_queue()` derives the expected archive paths from the archive task’s own artifacts plus its source tasks’ artifacts, requires exact `path_sha256` coverage for completed archives, and invokes the repository verifier. See [research_dispatch.py:742](/Volumes/SSD990/1083/ultra-recovery-20260909/tools/research_dispatch.py:742), particularly lines 772–788 and 809–818.

   `GitRepositoryVerifier.verify_archive()` then:

   - Resolves `archive.commit_sha` and checks whether it is an ancestor of `HEAD`: lines 1485–1525.
   - Checks the actual first parent against `archive.parent_sha`, with null required for a root commit: lines 1528–1544.
   - For ordinary `binding_mode: commit`, requires the commit to change exactly the expected paths: lines 1572–1588. `_changed_paths()` uses `diff-tree --no-renames --name-status ...` and rejects deletions: lines 1379–1410.
   - Reads each artifact with **`git show <archive_commit>:<path>`**, checks that it is a Git blob, and compares its SHA-256 to the declared hash: **lines 1590–1599**.
   - Requires the archive task ID and declared record IDs in that commit’s message: lines 1602–1612.

   The decisive pointer is [research_dispatch.py:1590](/Volumes/SSD990/1083/ultra-recovery-20260909/tools/research_dispatch.py:1590). Neither live worktree bytes nor the latest `HEAD:<path>` bytes enter this ordinary hash check.

   Consequently, a subsequent code/test revision can coexist with a valid historical archive when the original archive commit and its receipt remain intact and reachable. Altering an old queue’s declared artifact set, hashes, parent, or record IDs can still break its binding; creating a later code revision is a different operation.

   **Two important code-enforced exceptions exist:**

   | Verification route | Bytes actually hashed | Other behavior |
   |---|---|---|
   | Ordinary `commit`, archive commit reachable from `HEAD` | Historical `<archive_commit>:<path>` | Parent, exact changed paths, and message IDs checked |
   | Ordinary `commit`, commit unresolved or no longer an ancestor | **Committed `HEAD:<path>`** | Falls back before the historical parent/diff/message checks; degradation recorded |
   | Explicit `content_first` | **Committed `HEAD:<path>`** | Still requires a resolvable ancestor commit, matching parent, and message IDs; exact changed-path requirement replaced |
   | Recovery `_pinned_document()` | Pinned historical blob **and live worktree equality** | No content fallback |

   `_verify_content_only()`’s prose says “current tree,” but its executable code specifically runs **`git show HEAD:<path>`**, not `Path.read_bytes()` on the worktree. See [research_dispatch.py:1451](/Volumes/SSD990/1083/ultra-recovery-20260909/tools/research_dispatch.py:1451). Fallback mode can skip absent **or mismatched** generated paths named by `GENERATED_ARTIFACTS`—`knowledge/INDEX.md`, `dispatch_plan.json`, and `dispatch_plan.md`; explicit `content_first` disables that exception. See lines 1460–1483, 1546–1557, and 1303–1310.

2. **The affected v1 test belongs to an ordinary, currently reachable archive.**

   The queue declares completed archive `TASK-20260908-96aa5c`, explicitly `binding_mode: commit`, with:

   - Commit: `382be7a07b4e928a30dae7abb8d7beaf970a7d1a`
   - Parent: `336c70adc70668cd464a3e18cc1ce27a6ebf88af`
   - Test path: `tests/test_finite_yaml_locked_v1.py`
   - Test SHA-256: `a740c12de50474c9ad986bcb6e04b59c712e1d22a1fe54fed52b601a61ae882c`

   See [dispatch_queue.json:5109](/Volumes/SSD990/1083/ultra-recovery-20260909/coordination/goals/GOAL-ECDLP-001/batches/BATCH-855d5d/dispatch_queue.json:5109).

   I directly observed `git merge-base --is-ancestor <commit> HEAD` exit **0**, read the actual parent above, and computed that **both historical and current test bytes match the declared test hash**. I also inspected the actual commit message; it contains the archive/source task IDs and both experiment IDs. I did not run the complete dispatcher or its full archive verification.

   This establishes the technical mechanism permitting a later test revision. It does **not** independently authorize an edit: the old handoff explicitly says to preserve archived source bytes ([dispatch_queue.json:5065](/Volumes/SSD990/1083/ultra-recovery-20260909/coordination/goals/GOAL-ECDLP-001/batches/BATCH-855d5d/dispatch_queue.json:5065)), and the QA record calls for an additive engineering successor. A Coordinator should explicitly identify whether a prospective test-only portability correction at the ordinary test path is permitted, give its scope, and preserve the original archive/QA records and bindings. That interpretation is a Coordinator responsibility.

3. **Recovery authorization has stronger current-byte requirements, including for historical successor cards.**

   `_pinned_document()` requires a full 40-hex commit, SHA-256, an ancestor commit, a regular Git file mode (`100644` or `100755`), and a matching historical blob hash. It additionally rejects a symlink, missing file, path escaping the repository, or **live bytes differing from the pinned historical blob**. See [task_recovery.py:97](/Volumes/SSD990/1083/ultra-recovery-20260909/tools/task_recovery.py:97), especially lines 107–116.

   `verify()` applies this function to the **predecessor queue** at line 129 and the **Coordinator decision** at line 172. It binds the authorization to the predecessor/successor IDs, predecessor queue digest, successor contract digest, worktrees, session, and observed predecessor owner/epoch: lines 187–204. Contract hashing excludes only `recovery`, `state`, `lease`, and `receipt`: lines 54–60.

   The terminal-card early return occurs only at line 205, **after** both pinned-document checks and authorization matching. Thus completing a successor stops dependence on a later lease clock; it does not permit either bound document’s worktree bytes to drift. This matches [isolated-task-recovery.md:110](/Volumes/SSD990/1083/ultra-recovery-20260909/docs/isolated-task-recovery.md:110).

   Other current-byte enforcement in the inspected ledger validator includes:

   - Both sides of registered schema supersessions for ledger, experiment, knowledge, and goal-checkpoint records: [validate_ledger.py:1119](/Volumes/SSD990/1083/ultra-recovery-20260909/tools/validate_ledger.py:1119).
   - Both sides of registered run supersessions: lines 1418–1460.
   - Frozen legacy run inventory: lines 1463–1475.
   - Frozen root-level legacy ledger records: lines 1513–1541.
   - Provenance-quarantine replacements and their named searched-source inventory: lines 623–630 and 662–677.

   These are explicit current-file bindings. The inspected code does not establish a blanket requirement that every ordinary archived code/test path keep its latest bytes forever.

4. **The smallest useful root-test correction is deterministic root simulation, with a precise refusal assertion.**

   The existing test fails at its environment assertion, before exercising `validate_lock()`: [test_finite_yaml_locked_v1.py:426](/Volumes/SSD990/1083/ultra-recovery-20260909/tests/test_finite_yaml_locked_v1.py:426).

   The production resource policy rejects UID 0 at [runner.py:1078](/Volumes/SSD990/1083/ultra-recovery-20260909/src/crypto_autoresearcher/runner.py:1078). `validate_lock()` calls that real function and wraps its exception at [finite_yaml_locked_v1.py:398](/Volumes/SSD990/1083/ultra-recovery-20260909/harness/finite_yaml_locked_v1.py:398).

   A portable test-only correction can replace the host assertion with a scoped `pytest` monkeypatch of `core_runner.os.geteuid` to return `0`, leave `_locked_resource_policy()` active, and require the specific **non-root effective UID / RLIMIT_NPROC** refusal. Rename/reword the test to disclose simulated identity. The supported POSIX/RLIMIT_NPROC platform prerequisite should be explicit so an unrelated unsupported-platform refusal cannot satisfy the root-specific assertion.

   Merely skipping the test on non-root hosts avoids the failure but removes this coverage from non-root CI unless paired with the deterministic control. This unit test would exercise refusal logic; it would not claim that a real root subprocess’s resource limits were tested.

5. **The tree-state correction should supply the tree condition it claims to test.**

   The second failure comes from an assertion tied to the producer’s once-dirty worktree: [test_finite_yaml_locked_v1.py:583](/Volumes/SSD990/1083/ultra-recovery-20260909/tests/test_finite_yaml_locked_v1.py:583), particularly lines 591–603.

   `_tree_clean_except()` checks actual unstaged changes, staged changes, and untracked files outside the permitted run directory. See [runner.py:183](/Volumes/SSD990/1083/ultra-recovery-20260909/src/crypto_autoresearcher/runner.py:183). `execute_locked()` uses that result to override the terminal status to `failed_infrastructure`: [finite_yaml_locked_v1.py:482](/Volumes/SSD990/1083/ultra-recovery-20260909/harness/finite_yaml_locked_v1.py:482).

   The preferred correction is a disposable Git fixture with its own run directory and a deliberate file outside that directory, while keeping the **real** `_tree_clean_except()` active. The v1 module’s repository-root reference and `VerifiedLaunch.run_dir` can be scoped to the fixture. If the test claims **postlaunch mutation**, introduce the sentinel after the genuine synthetic child runs and before postflight inspection; preexisting dirt must be described as preexisting dirt. Retain the exact failure/status/artifact assertions.

   A clean counterpart can verify the benign success branch under a known clean fixture. A deterministic monkeypatch returning `False` is a smaller alternative for **status-mapping coverage**, but requires a separate real Git dirtiness control and must not be described as testing mutation detection.

   Simply deleting the tree assertion, accepting either Boolean/status, marking the whole test expected-failure, or forcing the production check to return `True` would not preserve the claimed control.

   The current helper manually constructs `VerifiedLaunch` at test lines 535–567. Correcting these tests therefore remains **synthetic `execute_locked()` coverage through that disclosed seam**. It does not establish normal admission-to-execution completeness.

The archived QA snapshot explicitly records engineering **FAIL** and **nine findings**, covering authority/envelope, configuration membership, provenance, source/runtime/environment, launch revalidation, output integrity, manifest/profile completeness, resource classification/types, and producer coverage claims. See [QA snapshot:272](/Volumes/SSD990/1083/ultra-recovery-20260909/coordination/pending-ideas/BATCH-855d5d/integration/archives/TASK-20260908-c0f57f/snapshot.json:272). These portability changes would address the two CI assumptions only. In particular, QA-F05, QA-F08, and QA-F09 already disclose the dirty-tree confound; a cleaner test setup must preserve that historical finding and support only newly observed, explicitly bounded coverage.

Observed inspection provenance: initial `HEAD` was `feb1789dd297094d2a6927c40de2351a5e13c3b6`, branch `codex/ultra-recovery-20260909`; local Python was **3.13.1**, Darwin **25.6.0**, effective UID **501**. The supplied CI observation records the two failure names and **2 failed, 1936 passed, 15 skipped**. UID **1001** is from the parent handoff; this short observation file does not itself expose that UID.

Additional live source hashes observed:

```text
tools/research_dispatch.py
5c40d891369c38f8d9013603fdf627f286243dffe4443878dd9e75926ec32c5c
tools/task_recovery.py
a87f47b5158709fbcbda850c3125b38626f45fee9116c71cec2ac6e653b9e4cd
tools/validate_ledger.py
fc197c80bd5f6b47765fed6948d7842c834c12e64d5f0cd236edfb75a94846c0
harness/finite_yaml_locked_v1.py
d0ae29cd9074bb0b055ca6459258e9639a45b0806e62e321ec0e6def1cac1c39
src/crypto_autoresearcher/runner.py
45129762b5ddc76877420addf184c53af8964f3f5e55f36ba1b9cb17df5455e3
```

The handoff requested `gpt-6-astra` with literal `ultra`, no fallback or degradation. I performed no serving probe and have no independently observed provider/model-verification receipt to add. I made no file writes, ran no tests or scientific processes, and changed no research status or authorization.
