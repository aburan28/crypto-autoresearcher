# Independent Q4 source, custody, and enforcement review

TASK-20261029-e276d7 · joint `q4-enforcement-source-runtime-custody-and-transfer` · verdict **breaks**

Required fresh Q4 enforcement coverage is absent. The committed evidence supports a single source-bound native cache-advice pass followed by the required **infrastructure_not_started** refusal. It does not establish actual 8 GiB OOM enforcement, victim attribution, worker peak, driver survival, or post-OOM cleanup. This is a qualification coverage failure; the supervisor's cap behavior remains untested.

The narrower source/advice/refusal record is coherent within its recorded scope. I independently derived its resource, identity, counter, eligibility, and custody conclusions from raw records before comparing producer summaries. I ran no helper, container, launcher, allocator, negative case, Cargo/test, or scientific computation.

## Actual observations and requirement status

| Requirement | Independent result |
| --- | --- |
| One conditional advice pass on exact 80 | Complete: one native `--advise`, exit 0, 80 accepted, 0 exclusions/failures; every raw row has rc=0 and stable_after=1. Accepted capacity4,557,159,684 bytes is not reclaimed-byte proof. |
| Immediate enclosing headroom | Post H12,708,687,872 bytes, **176,214,016 below** unchanged12,884,901,888 threshold. Refusal required and retained. |
| Fresh exact 8 GiB/effective-swap0 allocation | Not attempted. No Q4 container, guard driver/worker or allocator; actual new worker/parent readbacks unavailable. |
| Actual OOM/victim/peak/survival/cleanup | Not tested. No primary PID/starttime, worker-event delta, allocation progress, enforcement peak, surviving driver or post-OOM cleanup exists. |
| Source and immutable custody | Verified:96 prep paths;26 case-inventory paths including25 members+self; case commit changes24 paths because two source files were published earlier. All checked hashes/bytes match. |
| Historical rows and transfer | Old rows preserved. No fresh-host all-five qualification or new Q4 acceptance; earlier accepted fixtures retain only their historical source/runtime scope. |

At owner raw commit `0bcdc1a8f950715e6539780702706b8985071e5f`, the raw pre/post resource JSON gives:

| Observed quantity, bytes | Before16:48:16.998783–16:48:16.999444Z | Immediately after16:48:19.806546–16:48:19.807241Z |
| --- | ---: | ---: |
| Host MemAvailable, raw kB×1024 |17,962,373,120|17,974,874,112|
| Visible init memory.max/current |max /9,020,907,520|max /4,466,995,200|
| Visible parent memory.max/current |17,179,869,184 /9,025,093,632|17,179,869,184 /4,471,181,312|
| Derived H=min(host, finite enclosing max-current) |8,154,775,552|12,708,687,872|
| Shortfall from12,884,901,888 |4,730,126,336|176,214,016|

No new worker exists to include in the minimum. The observed16 GiB outer limit is not a measured Q4 container-parent limit. Both visible raw swap.max values are `max`, current0; host SwapTotal0 does not establish effective cgroup swap0. Both visible raw oom_kill counters are 0 before and after, delta 0. Their retained16.7GB historical outer peaks are not enforcement peaks of an absent worker.

Observer PID 28738 has the same /proc starttime 890876 in both samples, exact namespace0::/, and actual membership in visible init before/after, absent the parent root. The unique cgroup2 mount has literal root/.. . The bounded init→visible-parent mapping is supported by those memberships and the primary man7 namespace description/inherited-mount anomaly. No lexical traversal or remount was performed. Hidden ancestors remain unobserved. Samples are sequential, with no reported error bars; no causal reclaimed-byte attribution is supported.

## Source, authority, and publication

I verified original C1 source at `204735c3f6f3144911df58a6ece7699c0e74d4ad` and the retained Task30 copies, rather than substituting the current repaired-Q3 helper. Original driver/worker source hashes are bd5ffed5… and 14f89fc4…; selected external binaries are2738ade0… and f06e008b… . All 12 protected files match `86ddd19f67e08160c22a0d8ba9a32a92321d18ad` across prep 66ea, correctione946, merge 8217 and raw 0bcdc. Task30, protected tests/runtime, and old programme outcome paths remain unchanged.

The helper source f132fe98…/binary5615bb56… is bound to retained C++17/O2 strict toolchain, ELF RUNPATH, loader and library metadata. The source performs read-only no-follow/no-atime UID1000 regular-file and stable fstat/SHA checks, deduplicates inode, and makes at most one fadvise call per accepted entry. The frozen external exact 80 index narrows its generic398 ceiling. All 80 paths, current UID/device/inode/size/mtime records, historical expected hashes, native seal rows, eligible rows and advice rows agree;80 distinct inodes sum to4,557,159,684 bytes. The reviewer opened **zero candidate contents**.

One historical caveat is retained: pack `/workspace/crypto/.git/objects/pack/pack-fa66ff9e0427b17e645bcacef3dd8fefca53b55e.pack` has original mtime_ns1793053277390270427 and fresh prospective-plan mtime_ns1793056768668436294. Path, UID/device/inode/size/ownership and SHA remain identical. All current plan/lstat/native records match the explicitly published fresh timestamp; its earlier change has no recorded cause. Thus79/80 entries have every historical field identical. The broad `old_metadata_matches` label must not be read as equality of all historical fields.

The actual chronology is consistent:

- Initial packet 72a659 published before prep-admission snapshote6d1 at16:02:30Z; the sole native seal runs16:08:11.807642–16:08:15.644886Z.
- Owner prep 66ea publishes16:15:13Z; exact four-output-plus-receipt programme snapshot 86f4 publishes16:20:19Z; verificationadb309 follows16:22:14Z.
- The published operational ordering amendment distinguishes queued-for-ownership from phase execution. Claim/source-mapping amendment37b52 publishes16:36:02Z; additive source-only correctione946 publishes16:41:17Z.
- Advice-only admission 327869 publishes16:46:07Z, before the native advice argv at16:48:16.999624Z. Its Q4_admitted field is false. The post sample completes16:48:19.807241Z before marker16:48:19.807465Z and before later software/library/Git reads in the retained controller source.
- Terminal refused_Q4 publicationa204291 follows16:57:43Z. There is no admitted_Q4 gate. The unchanged strict launcher requires that exact verdict before its image/create operations.
- Merge8217 follows16:59:22Z; raw 0bcdc follows17:08:14Z. Results snapshotcc367 has exactly the four producer outputs plus receipt, parent35cac; bindingcf844 follows17:21:48Z, normal snapshot release 1fd1 follows, and the independent reviewer claim 0d3b follows17:21:58Z.

Fresh T5 and T6 safe proofs carry distinct task/lease identities and fencing epoch 1. At the native seal/advice calls, proof ages are12.677811/6.431705 seconds and leases extend beyond each retained phase end; the published source/advice/reporting records preserve later renewed T6 observations. The task/session/epoch claims are unforced and unexpired at their actions. This reviews published safe observations, not the private Conductor database or continuous private heartbeat history. I did not access private environment, tokens, or global logs.

All initial content-at-commit hashes match. The combined comparison against current working bytes is false solely for the canonical dispatch queue, which has advanced through published controls; its current bytes equalcf844. Prep/result archive parents, exact path sets, IDs, hashes and sizes match. Push/remote verification is reported in published control receipts; I independently checked available Git objects and did not make a new remote query.

The e946 launcher diff is confined to seal references and bounded own-stable-Bash-PID mapping/capture. It preserves thresholds, original native driver/worker/production code,8 GiB child/16 GiB parent requests, swap0 requirement,CPU 2,pids 64,pinned image,1800 s production timer,1950 s protection and exclusiveQ4. Source syntax evidence is retained; **the launcher was never executed**. Python metadata sources perform admission/custody read/hash/counter work and invoke the existing native helper; candidate hashing/advice is native. Native argv/cwd/selectors/stdout/stderr/exit are retained. A separate outer Python-interpreter launch-argv receipt is not present in the26-file case inventory.

Journal deferral is explicit under the merge hold. I verified the raw journal begins with every byte of the actual149,842-byte merged8217 journal, SHA d6e2c47f…; the154,427-byte raw journal matches its historical raw-commit binding. Historical66ea log hashes are checked at66ea, not against a later mutable journal. Source correction, prepublication comment adjustment, ordering controls, and journal deferral remain visible; no frozen artefact was modified.

## Attacks and limits

The actual high host MemAvailable but insufficient enclosing margin is a concrete proves-too-much control: host-only admission would be wrong. Exact cap readback without allocation, mmap failure, inherited OOM counts, unrelated SIGKILL, outer historical peaks, driver/container death or surviving processes cannot establish OOM qualification. The raw counter keys must exist, not default to zero. Static C1 code uses map operator[] for oom_kill and substring membership readback, so a future acceptance must independently check exact raw keys and PID/starttime/first-worker identity; unexecuted source alone is insufficient. min(max,0,max)=0 and min(max,max,max)=max keep inherited swap limits distinct from literal child zero.

The corrected outer mapping, fresh host epoch and changed outer resource state prevent automatic runtime transfer. Matching protected source, image and binary identities establish lineage. They do not establish newly observed delegation/cap/swap/OOM/victim/peak/survival/cleanup. Historical Q1/Q2/Q5 and repaired-Q3 remain evidence only for their earlier recorded trusted-worker fixture; original Q3 remains failed. There is no all-five rerun and no combined qualification.

Ancillary Rust validation is separate. Historical 12c reports5198 passed/8 failed/123 ignored/exit101 plus8 successful individual same-binary replays; its464,884-byte full log lacks complete canonical custody. Current 8217 validation was reported compiling after terminal case closeout; this review neither reruns it nor asserts terminal PASS. Merge whitespace/promisor diagnostics remain reported as failures, not normalized evidence.

The original 24 scientific cells remain unrun. Joint reach/cost, theorem applicability and verified prime-field IC improvement remain unresolved. Full process-tree CPU, global-host/hostile-worker isolation, scientific readiness and mathematical negatives are not established; old mathematical independence issues remain unchanged. No scientific graph or official status changes in this review. Existing TASK947247 owns composition, diagram/PDF and archive.

## Independence and completion

Fresh agent `/root/independent_q4_review_e276d7`, canonical session `native-q4-independent-20261029`: managed gpt-6.1-sol/xhigh, review-adversarial, operator-supplied binding/API probe unverified, fallback false, no degraded requirements. No producer/Coordinator history or new-round sibling report was inherited/read; old review input reads are explicitly authorized by the plan. Complete read paths and source modes are in review-attestation.yaml. The single owned-joint verdict is breaks for absent required coverage; the source/advice/refusal subfinding holds within the stated limits.

Ready-only output and actual published epoch 1 reviewer claim were checked before writing. Only the four declared files were written. After root verifies these final frozen bytes/hashes, I expressly consent to root publishing the normal completed **reporting-only** release as reviewer-native-q4-independent-e276d7/session native-q4-independent-20261029/epoch 1, without force/takeover or alternate-principal mutation. This completes review reporting and grants no Q4 pass, scientific approval, current Cargo PASS, or official transition. I did not commit, release claims, or change queue/status.

Primary retrieval: https://man7.org/linux/man-pages/man7/cgroup_namespaces.7.html, supplied retrieved copy SHA d843d0410f732bcbd89d0f3c3acbf1646f7aaf7db930e1d223da9b5369976a91, actually read for namespace-relative paths and inherited mount anomaly; no remount instructions executed. Repository contracts, canonical review schema/checker, fixed plan, original/native source and immutable records supply the other evidence. Detailed numerical checks, full case path hashes, provenance caveats and diagnostics are in checks.json/source-review.json.

Canonical independence validation returned exit1: `blindness.lifted_for must be a list of valid TASK owners`. The frozen plan lists the two prior DEC IDs in that field. The attestation uses the correct `joints_owned` field and declares no sibling access. This is a retained plan/schema failure; I did not edit the frozen plan or checker. Mechanical independence acceptance remains unresolved pending any root-owned additive correction under the existing composition scope.
