# Graph-wide isogeny relation study lacks an admitted collector and complete solve path

- **Status:** `investigating`
- **Kind:** implementation gap and protocol-admission gap; a separate Coordinator backend access limit remains tracked in [the arity-3 panel problem](prime-field-arity3-relation-oracle.md).
- **Affected work:** [2,304-edge graph archive](../research/isogeny_relation_yield_scan_20261016/report.pdf), [prospective protocol](../research/isogeny_relation_yield_scan_20261016/PROTOCOL-original-draft.md), [baseline amendment](../research/isogeny_relation_yield_scan_20261016/AMENDMENT.md), and [input preparation](../research/isogeny_relation_yield_scan_20261016/preparation/README.md).
- **Next action owner:** implementation task `T-3327` for two-edge transport controls; Coordinator for fixed check vertices, a runnable contract and handoff; Executor for admitted trials.
- **Last updated:** 2026-10-16

## Problem

The P29/P37 graph now has 2,304 checked degree-7 edges and 2,306 vertices, but the requested comparison of relation yield, useful rank, and minimum/maximum complete same-point ECDLP cost cannot yet be established. The graph-wide run lacks a degree-7 transported-base control, a frozen admitted collector schedule over the fixed vertices and bases, and a complete index-calculus solve and matched-cost pipeline. The existing exact triple collector measures mathematical availability on prepared inputs; that alone does not time relation solving or recover an unknown scalar through the full pipeline.

The prospective design fixes three main bases on every vertex, a fourth on prespecified indices, discovery and fresh confirmation targets, finalist selection, and full cost accounting. It remains a draft rather than an approved `EXP-*` contract. The first 20-arm conductor-step study is a distinct frozen experiment and is not substituted for these 2,306 vertices.

## Evidence and uncertainty

- **Observed:** [Full graph records and independent checks](../research/isogeny_relation_yield_scan_20261016/manifest-v2.json) passed for 2,048 P29 and 256 P37 edges. [Fixed input controls](../research/isogeny_relation_yield_scan_20261016/preparation/controls/attempt-1/insight.md) exercised 22 eight-target arm/vertex cases and saved three independently replayed prepared inputs. A deliberately altered target coefficient was rejected by the group-equation checker. [Two-edge transport control](../research/isogeny_relation_yield_scan_20261016/preparation/controls/attempt-3/insight.md) mapped all 512 P29 and 3,200 P37 signed source-base points across the first two edges and matched four fixed planted target counts at each edge; 21 dual checks per edge passed. The earlier overlong all-point dual attempt is retained as a censored implementation attempt.
- **Derived or proved:** Under the checked prime-order path, the same coefficient vector defines paired points via each transported generator; an exact isogeny carrying a factor base preserves decomposition counts targetwise. The latter control has not yet been executed across the degree-7 path.
- **Suspected explanation:** Unknown. No graph-wide yield or solve measurements exist, so no curve-specific advantage or lack of one is inferred.
- **Missing capability:** Persisted/replayed degree-7 base transport on the full walks and prespecified check vertices using the fixed target stream; admitted graph-wide relation collection with independent completeness and rank checks; complete native, cold-transfer, and genuinely amortized same-point solve costs with matched rho.
- **What this evidence does not establish:** Any yield extrema, useful-rank ordering, completed ECDLP time, speedup over the frozen IC baseline, or rho comparison on this graph. An input fixture passing does not establish collector correctness at full size.

## What would unblock it

- [ ] Save a versioned source-base transport along the full P29/P37 paths, with every relevant map and dual checked, and demonstrate exact targetwise relation-count equality at the protocol's precommitted check vertices.
- [ ] Freeze implementation hashes, graph/base/target roots, quotas, controls, stopping rules and artifact paths in a runnable contract whose execution-state checker reports `ready`; obtain a committed Coordinator approval and handoff under the standing authorization. Run the fixed discovery and fresh confirmation schedules through the public `run` route, retaining all attempts and independent count, row and rank replay.
- [ ] Complete the prespecified finalist same-point solve trials with unseen targets, independent scalar replay, all setup/relation/rank/individual-log/verification costs, cold transfer and genuine reuse accounting, paired source/destination rho, and a qualified progress-fidelity record for any speed claim.

The first two conditions permit a bounded relation-yield and rank conclusion on the selected graph. The third is necessary for an ECDLP cost conclusion; it does not follow from yield alone. Meeting all three would still support only these two fixed prime-field walks and the tested bases, not a universal conductor or isogeny law.

## Next discriminating step

- **Action or proof obligation:** Extend the checked two-edge source `low_x` base transport to the fixed check-index set, without selecting vertices by observed yield; replace planted target controls with the committed discovery target stream and independent exact count replay.
- **Inputs and controls:** The archived graph kernels, source generator and `low_x` base; source-vs-transported targetwise equality, dual identities, the native `low_x` base and the existing `u=2` coordinate control. Keep the random-base null separate.
- **Execution limits and stop condition:** Use the prospective single-worker memory and watchdog guards when formalized; stop on the first failed map, dual, point, or equality certificate. These are machine protections, not a campaign spending cap.
- **Outcomes and next actions:** Passing transport controls permits the Coordinator to assess a runnable collector contract. A concrete mismatch requires correction and a new immutable attempt. A timeout, crash, or missing Coordinator backend leaves the scientific comparison unmeasured and calls for a bounded retry or infrastructure repair, not a negative mathematical inference.
- **Recheck trigger:** A committed transport control, admitted `EXP-*` contract, full collector receipt, or complete finalist solve record.

## Resolution and history

Unresolved. This record names the remaining work and changes no hypothesis or goal status. The graph archive was merged in [PR #2222](https://github.com/aburan28/crypto-autoresearcher/pull/2222); the preparer controls are implementation evidence only. Preserve all earlier graph and test artifacts when a later run is added.
