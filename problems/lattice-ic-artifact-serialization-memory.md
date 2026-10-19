# Exact artifact serialization exceeds the polynomial memory envelope

- **Status:** investigating
- **Kind:** observed implementation allocation failure and resource limit; no mathematical obstruction established
- **Affected work:** RQ-IC-a39c7e, H-IC-4fb1db, EXP-IC-9f9a4b/RUN-IC-fe080b, Executor TASK-20261015-61db74; [actual receipt](../experiments/EXP-IC-9f9a4b/runs/RUN-IC-fe080b/execution-receipt.json), [inspected report](../experiments/EXP-IC-9f9a4b/reports/run-20261015T1113Z/report.pdf), [custody inputs](../research/lattice_ic_experiments_20261015/coordinator/polynomial-serialization-failure-custody/actual-failure-inputs.json)
- **Next action owner:** Coordinator/root for published currentclosure5 proof and prospective fresh full-science-equal admission; full-grid/checker and independent review remain open
- **Last updated:** 2026-10-16

## Problem

The unchanged full polynomial schedule cannot yet supply serialized and separately checked observations because shared-core artifact preparation raises `MemoryError` under the frozen 2 GiB address-space guard.

The prescribed three curves, windows2/4/8, m2/3 reductions and m2/3/5 density controls, t/L/arms/targets/cohorts/criteria/caps, seed1729 and one worker remain unchanged. The scientific-body function returned, but its in-memory object was not saved. No raw result, manifest or checker result exists. This blocks the fourth successful observation archive and all dependent independent scientific reviews; it does not refute the polynomial mechanism.

## Evidence and uncertainty

- **Observed:** Native `infrastructure_error`, driver1, checker null; started2026-10-15T11:13:56.203333UTC, finished2026-10-16T05:05:34.296975UTC. Exact runtime8 commit `6c23687ca2fc5193f284c15a507b2d9cf1b93ec5` and inspected six-file report `de160f04c2d06040e9ae1aca9852ffd58356a558` retain the outcome. Event22257 is scientific-body function return;22258 writer start;22259 writer `MemoryError`;22260 CLI exception. Traceback ends at core.py480 `_json_safe(result)` through recursive dict/list conversion.
- **Observed custody:** receipt7 bindings/current8/Git8 hashes agree; missing raw/manifest remain absent. Native owner release is failed at2026-10-16T16:08:09Z, `was_expired:true`, epoch1; this release timing does not change the earlier infrastructure-error receipt or cached authority.
- **Source inspection:** writer recursively normalizes the result, then normalizes again while encoding a complete string and bytes object. Avoidable copy/buffering overhead is a concrete repair target, not a measured peak-memory diagnosis. The original raw schema and all exact certificates remain required.
- **Unknown:** saved cell/root/rank/certificate yields, complete raw size, peak native memory and whether writer repair alone leaves enough checker headroom. Telemetry return/status/timing fields are operational and cannot replace serialized checked outputs. No new HNF/LLL defect or useful-relation result is established.
- **Separate prior problems:** [HNF memory](lattice-ic-integer-hnf-memory-growth.md) retains its original failure and full-grid/review conditions; [authority/observability](lattice-ic-polynomial-lease-progress-observability.md) retains the distinct expiry and successful diagnostic telemetry boundary, without attributing this failure to expiry.

## What would unblock it

- [x] Distinct actual8+ownreceipt9 administrative custody passes native Git verification and is published; original scientific10 archive3047d1 and local9403cb remain uncompleted, absent outputs untouched.
- [x] [Narrow source handoff](../ledger/handoffs/TASK-20261016-282fd3.yaml) passes meaningful exact-byte/value/error/I/O and bounded synthetic serialization/check controls plus all shared-consumer regressions under unchanged hard+soft2GiB; actual software insight report retains every failure/limit. No study trial as a software test.
- [x] Accepted source2+ownreceipt3 and a fresh current-source closure4+ownreceipt5 are actually archived/native verified. Currentclosure5 proof metadata publication is pending in this change before further admission; historical source snapshots are immutable and no old/new hash-map union was used.
- [ ] A prospective fresh full-science-equal EXP/RUN/plan/amendment receives native-ready Coordinator approval and completes its full cold schedule and separate checker with exact custody, followed by required independent review. Execution-proof support/limits are explicit; no unsupported verification claim.

Software controls would establish only exact artifact-path behavior at their tested payloads/resources. Only actual complete fresh outputs/checker and independent review can establish scientific observations or satisfy the final condition. Full-grid memory feasibility is currently unestablished.

## Next discriminating step

- **Action:** publish the [fresh currentclosure5 native proof](../research/lattice_ic_experiments_20261015/coordinator/polynomial-current-closure-20261016/snapshot-git-verification.json), then design a NEW full-science-equal prospective protocol and obtain native readiness before any fresh cold full-grid/checker attempt. No trial is authorized by source custody alone.
- **Controls:** frozen bounded synthetic nested exact payload; matched old/new writer fixture and guard; exact-byte oracle; no whole-result mutation/copy; malformed late values/keys; provenance/timing/exclusive-create/hash/I/O tests; shared-core plus all four consumer regressions; separately measured writer/checker costs.
- **Limits:** zero scientific runs, one worker, hard+soft2GiB; no full grid, retuning, output omission, changed caps, partial-cell replay or same-directory rerun. A justified software-process watchdog is operational, not scientific negative evidence.
- **Outcomes:** passing software evidence permits only accepted source custody and later prospective design. A further writer/checker failure remains preserved and identifies a narrower repair. Full-science completion still needs a fresh admitted attempt. No synthetic pass releases full/local/blind review.
- **Recheck:** actual native failure9, actual software report/source3/currentclosure5, then future fresh actual full-output/checker custody.

## Resolution and history

2026-10-16: opened after actual serialization failure. Both prior attempts, frozen23 inputs and all historical archives remain immutable. Three distinct failure9 archives must accompany future four successful observations and the preserved old/new blind archives. No review plan/candidate applied, independent reviewer dispatched, scientific status changed or improvement claimed.


2026-10-16 custody/source release: actual9 snapshot `8e50dcacdd42d3f048899e6979581c6f9fdbdbc7`, parent `2230990122d78a9a12d97f44f4047782218ad9e3`, has native Git proof published at `049bb2b82a2744d54f78a6bd63bbe5da14049231`. Capturea59f61/archivef4a410 are completed administrative tasks only. Coordinator has explicitly queued source282fd3; root must publish that queued release and acquire a normal native source claim before implementation. Source acceptance, fresh currentclosure5, future full-grid/checker and independent review remain uncompleted.

2026-10-16 bounded software progress: final source282fd3 passed actual107 non-study regressions and the same frozen synthetic writer/reader controls under unchanged hard+soft2GiB. Historical baseline writer MemoryError/censored reader, retained v1 timing defect and all other failures remain in the [durable software report](../research/lattice_ic_experiments_20261015/coordinator/polynomial-serialization-remedy/software-report/report.pdf); actual report8 snapshot `9f23942d6e35d1a1f592fea26bc24c21ebcec203` has native proof published `3223816611377ac16cc7fcf1d1e4c2fb7f73ef2c`. Exact source3 `1551cb5698f0d7e09d3ba671de13444dc2edcab5` has native proof published `2cc3fde59348088d06f6a53c39f4c92e37f19c67` and [final narrow software source acceptance](../research/lattice_ic_experiments_20261015/coordinator/polynomial-serialization-remedy/final-software-source-acceptance-20261016.json). Fresh currentclosure5 `0f3e2d6a8b562824721dfbe952eb9c98b788419c` binds current core/test and unchanged accepted polynomial/test together, natively verified with one own receipt and no older-proof union; this proof metadata awaits publication. These controls establish only bounded software behavior; full scientific object/checker memory remains unknown. Status stays investigating; no scientific fourth success, independent review, baseline/S improvement or execution-proof claim.
