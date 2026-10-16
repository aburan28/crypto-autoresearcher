# Graph-wide isogeny relation study lacks an admitted collector and complete solve path

- **Status:** `investigating`
- **Kind:** implementation gap and protocol-admission gap; a separate Coordinator backend access limit remains tracked in [the arity-3 panel problem](prime-field-arity3-relation-oracle.md).
- **Affected work:** [2,304-edge graph archive](../research/isogeny_relation_yield_scan_20261016/report.pdf), [prospective protocol](../research/isogeny_relation_yield_scan_20261016/PROTOCOL-original-draft.md), [baseline amendment](../research/isogeny_relation_yield_scan_20261016/AMENDMENT.md), [input preparation](../research/isogeny_relation_yield_scan_20261016/preparation/README.md), and [first check-vertex transport](../research/isogeny_relation_yield_scan_20261016/path_transport/insight-20261016.md).
- **Next action owner:** implementation for full-path transport and an admitted collector; Coordinator for a runnable contract and handoff; Executor for admitted trials.
- **Last updated:** 2026-10-16

## Problem

The P29/P37 graph now has 2,304 checked degree-7 edges and 2,306 vertices, but the requested comparison of relation yield, useful rank, and minimum/maximum complete same-point ECDLP cost cannot yet be established. Source-base transport has been checked through the first prespecified vertices, P29 index 8 and P37 index 4. The graph-wide run still lacks full-path transport, exact targetwise relation-count equality, a frozen admitted collector schedule over the fixed vertices and bases, and a complete index-calculus solve and matched-cost pipeline. The existing exact triple collector measures mathematical availability on prepared inputs; that alone does not time relation solving or recover an unknown scalar through the full pipeline.

The prospective design fixes three main bases on every vertex, a fourth on prespecified indices, discovery and fresh confirmation targets, finalist selection, and full cost accounting. It remains a draft rather than an approved `EXP-*` contract. The first 20-arm conductor-step study is a distinct frozen experiment and is not substituted for these 2,306 vertices.

## Evidence and uncertainty

- **Observed:** [Full graph records and independent checks](../research/isogeny_relation_yield_scan_20261016/manifest-v2.json) passed for 2,048 P29 and 256 P37 edges. [Fixed input controls](../research/isogeny_relation_yield_scan_20261016/preparation/controls/attempt-1/insight.md) exercised 22 eight-target arm/vertex cases and saved three independently replayed prepared inputs. A deliberately altered target coefficient was rejected by the group-equation checker. [Two-edge transport control](../research/isogeny_relation_yield_scan_20261016/preparation/controls/attempt-3/insight.md) mapped all 512 P29 and 3,200 P37 signed source-base points across the first two edges and matched four fixed planted target counts at each edge; 21 dual checks per edge passed. The earlier overlong all-point dual attempt is retained as a censored implementation attempt.
- **Observed, later control:** [First check-vertex transport](../research/isogeny_relation_yield_scan_20261016/path_transport/insight-20261016.md) extended checkpointed chains to P29 edge 8 and P37 edge 4. Independent integer replay checked 4,096 and 12,800 point images respectively. The terminal checkpoint SHA-256 digests are `8b40a5c11de49dbfb49a7cedb12f5c5eec1c984a32a3e9effc8638cbe9124f92` and `4b529e7d45b6cc54d8f2e7aa5608196febd9c35d8979394af05fa57c678147d0`.
- **Derived or proved:** Under the checked prime-order path, the same coefficient vector defines paired points via each transported generator; an exact isogeny carrying a factor base preserves decomposition counts targetwise. The saved point images through the first check vertices support the transport part of this control. Targetwise relation-count equality has not yet been executed across the degree-7 path.
- **Suspected explanation:** Unknown. No graph-wide yield or solve measurements exist, so no curve-specific advantage or lack of one is inferred.
- **Missing capability:** Persisted/replayed degree-7 base transport on the remaining 2,040 P29 and 252 P37 edges and all later prespecified check vertices, with exact equality on a fixed target stream; admitted graph-wide relation collection with independent completeness and rank checks; complete native, cold-transfer, and genuinely amortized same-point solve costs with matched rho.
- **What this evidence does not establish:** Any yield extrema, useful-rank ordering, completed ECDLP time, speedup over the frozen IC baseline, or rho comparison on this graph. An input fixture passing does not establish collector correctness at full size.

## What would unblock it

- [ ] Extend the versioned source-base transport from P29 edge 8 and P37 edge 4 through both full paths, with every relevant map and dual checked, and demonstrate exact targetwise relation-count equality at the protocol's precommitted check vertices. The first check-vertex point-image replay is complete; the remaining path and targetwise equality are open.
- [ ] Freeze implementation hashes, graph/base/target roots, quotas, controls, stopping rules and artifact paths in a runnable contract whose execution-state checker reports `ready`; obtain a committed Coordinator approval and handoff under the standing authorization. Run the fixed discovery and fresh confirmation schedules through the public `run` route, retaining all attempts and independent count, row and rank replay.
- [ ] Complete the prespecified finalist same-point solve trials with unseen targets, independent scalar replay, all setup/relation/rank/individual-log/verification costs, cold transfer and genuine reuse accounting, paired source/destination rho, and a qualified progress-fidelity record for any speed claim.

The first two conditions permit a bounded relation-yield and rank conclusion on the selected graph. The third is necessary for an ECDLP cost conclusion; it does not follow from yield alone. Meeting all three would still support only these two fixed prime-field walks and the tested bases, not a universal conductor or isogeny law.

## Next discriminating step

- **Action or proof obligation:** Extend the checked source `low_x` base transport past P29 index 8 and P37 index 4 to every fixed check index and both path endpoints, without selecting vertices by observed yield. Then bind the committed discovery target stream and independently replay exact targetwise counts.
- **Inputs and controls:** The archived graph kernels, source generator and `low_x` base; source-vs-transported targetwise equality, dual identities, the native `low_x` base and the existing `u=2` coordinate control. Keep the random-base null separate.
- **Execution limits and stop condition:** Use the prospective single-worker memory and watchdog guards when formalized; stop on the first failed map, dual, point, or equality certificate. These are machine protections, not a campaign spending cap.
- **Outcomes and next actions:** Passing the remaining transport and targetwise controls permits the Coordinator to assess a runnable collector contract. A concrete mismatch requires correction and a new immutable attempt. A timeout, crash, or missing Coordinator backend leaves the scientific comparison unmeasured and calls for a bounded retry or infrastructure repair, not a negative mathematical inference.
- **Recheck trigger:** A committed transport control, admitted `EXP-*` contract, full collector receipt, or complete finalist solve record.

## Resolution and history

Unresolved. This record names the remaining work and changes no hypothesis or goal status. The graph archive was merged in [PR #2222](https://github.com/aburan28/crypto-autoresearcher/pull/2222); the first check-vertex transport and visual report were merged in [PR #2272](https://github.com/aburan28/crypto-autoresearcher/pull/2272). These controls are implementation evidence only. Preserve all earlier graph and test artifacts when a later run is added.
