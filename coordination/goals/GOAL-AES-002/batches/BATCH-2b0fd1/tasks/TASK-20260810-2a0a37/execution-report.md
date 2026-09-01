# execution-report.md — TASK-20260810-2a0a37 (GOAL-AES-002 / BATCH-2b0fd1)

Role: executor. Experiment id: EXP not assigned — this task is the toolchain-and-throughput measurement itself; its receipt id is MEAS-TASK-20260810-2a0a37-002 (envelope-receipt.json). Implementation commit: none made and none permitted (this task makes no commit; TASK-20260810-1a81be snapshots these bytes before review); working-tree provenance is carried by the covering manifest's sha256 fields.

**This task runs a benchmark and an inventory. It attempts no key recovery, computes no distinguisher, and asserts nothing about AES security at any round count. This receipt is infrastructure and is expressly NOT a completion (GOAL-AES-002 non_completion_criteria (vi)). No reduced-round finding produced under this goal is asserted here (SC-8). No margin against the published state of the art is stated or admitted here — the published frontier is unadjudicable in this environment in both directions, and the only quantitative reference this campaign may use is the definitional exhaustive-key-search reference under CM-1 (SC-6); this deliverable states no margin at all, so the R5 clause's sentence duty attaches to any LATER record that quotes these numbers, and R5 is quoted verbatim in the covering manifest and again below.**

## What this session is

Session-4 of this task. Sessions 1–3 (recorded in api_direct/, api_direct-run2/, api_direct-run3/) performed the three benchmark runs and exhausted the run budget (maximum_runs=3) — session-3 additionally exhausted its step budget before writing the two remaining deliverables, which is infrastructure signal, never a negative mathematical result (AGENTS.md rule 5). Session-4 performed NO new benchmark runs; it computed the derived quantities from the preserved run records and wrote the covering manifest, this report, and the SC-1 stamps.

## Runs

- completed: RUN-1 toolchain/environment inventory (run1-inventory.json, corrected for the measured host); RUN-2 accelerated benchmark, arm64-native builds (run2-aesni.json, run2-arm64-compile.json, run2-repaired.json, run2r-v4-verify.json); RUN-3 pure-Python AES-128 benchmark (run3-python.json).
- invalid: RUN-2's accelerated throughput numbers — the arm64 v1..v4 benchmark programs all FAIL the FIPS-197 known-answer selftest and disagree with the openssl CLI on 8/8 cross-check vectors, while the pure-Python implementation agrees 4/4 on its vectors. Classification: `invalid_measurement` — the numbers are the throughput of a wrong cipher. Preserved, not discarded, and explicitly barred from budgeting use.
- failed (infrastructure, preserved, never negative evidence about AES): run_measurements.py RUN-1 `FileNotFoundError: /proc/cpuinfo` (driver assumed a Linux host; the measured host is Darwin/arm64); session-3 `stop_reason: step_budget_exhausted` before deliverables were written; `-maes` compile failure (see below — this one is not a failure of the experiment, it IS one of the measured findings).

## The six items, one line each (full raw commands and outputs in envelope-receipt.json and the run records)

1. **gcc exists — measured.** `/usr/bin/gcc` reports "Apple clang version 17.0.0 (clang-1700.0.13.5), Target: arm64-apple-darwin25.6.0". It is not gcc 13.3.0 and not an x86-64 toolchain.
2. **-maes does NOT compile — measured.** Exact error: `clang: error: unsupported option '-maes' for target 'arm64-apple-darwin25.6.0'`. An arm64-native path (`-march=armv8.6-a+crypto`, `vaeseq`/`vaesmcq`) compiles and the binary runs — but no correct accelerated benchmark was produced within the run budget, so `maes_runs` is null and no accelerated throughput is valid.
3. **AES-NI throughput — invalid_measurement.** No x86-64 AES-NI exists on this host; the arm64 accelerated numbers fail the KAT and are preserved as invalid only.
4. **Pure-Python throughput — measured, valid.** Fresh-key (schedule charged per evaluation, CM-1 AEU-128 shape) median **11061.1924 AES-128 evaluations/s/core** (reps 10804.85 / 11061.19 / 11236.65), cross-checked 4/4 against the openssl CLI before timing. Amortised fixed-key median 13379.81/s/core.
5. **Usable RAM — measured.** Physical 51,539,607,552 bytes (48 GiB); conservative vm_stat point snapshot (free+speculative+purgeable at 16 KiB pages) 150,126,592 bytes at measurement time — a loaded-host snapshot, not a stable capacity figure.
6. **Ceiling — derived from item 4 only.** Per 1600 s task: 2^24.08 single-core; 2^26.08 at 4 cores and 2^27.88 at 14 cores, both DERIVED UNDER THE ASSUMPTION OF LINEAR SCALING, which was NOT measured for any valid implementation (stated in the field itself). Campaign total_wall_clock_seconds is null (unbounded) since BUDGET-AMEND-20260828-16e34c, so no finite campaign ceiling is derivable; the pre-amendment 22500 s line would give 2^31.70 at 14 cores assumed-linear.

## Contradiction resolution (neither committed record edited)

- Supports RQ-AES-001 on: a C compiler exists under the name gcc.
- Resolves AGAINST RQ-AES-001 on its specific claim: "gcc 13.3.0 with -maes" is measured false on this host — wrong version string, and -maes does not compile. Also pycryptodome, which it lists as available, is measured absent.
- Resolves AGAINST GOAL-AES-001 on its specific claim: numpy IS importable (2.4.4) and a small C program CAN be compiled — the census-leg blocking premise is wrong on both named dependencies.
- The receipt is silent on: census-leg feasibility (memory/work profile unmeasured), any valid accelerated throughput, multi-core scaling for any valid implementation, AES cryptanalysis at any round count, and every host other than the one measured (Darwin 25.6.0, Apple M4 Pro, Mac16,7, 14 logical CPUs).

## Relation to the prior receipt MEAS-GOAL-AES-002-001 (input, not answer; not copied; none of its numbers restated as this task's own)

- gcc/-maes: DISAGREES — the prior receipt records an x86-64 gcc 13.3.0 with -maes compiling and running; this task measures -maes as not compiling on this host. The two receipts describe different toolchains; the difference is recorded, not adjudicated here.
- Hardware throughput: NOT COMPARABLE — this task's accelerated figure is invalid (KAT failure), so no valid pair exists to compare.
- Multi-core scaling: AGREES ON THE WARNING — both declare scaling assumed-not-measured; this task labels every multi-core ceiling derived-under-an-assumption in the field itself.
- Pure-Python throughput, usable RAM: not stated by the prior receipt; this task's figures are new and independent.

## Protocol deviations and anomalies (all recorded, none discarded)

1. Three prior sessions of this same task exist in the working tree; session-4 completed the deliverables they left unwritten. All runs were theirs; run budget was already at maximum_runs=3, so no re-measurement was possible and none was attempted.
2. Driver v1 assumed a Linux host (/proc/cpuinfo) — specification/infrastructure error, corrected in v2; failure preserved in run1-inventory.json.
3. Four versions (v1–v4) of the arm64 benchmark were authored attempting to compose ARM AESE/AESMC correctly; all fail the FIPS-197 KAT. The correct composition was NOT established within budget — this is named OPEN AND UNATTEMPTED-beyond-budget, never recorded as a negative result about AES or about the host's capability, and a successor task with fresh run budget is required before any hardware-AES throughput may be quoted on this host.
4. The only measured multi-core datum (14 processes, 8.57× on 14) comes from the INVALID build and is itself unusable.
5. measure_envelope.c (the declared deliverable, x86-64 source) cannot compile on this host by measurement — that is a finding of this task, not a defect of the artifact; it carries its comment-block inference stanza and its compile probes are preserved in run1-inventory.json.

## SC-4 verbatim (binding on every deliverable of this task)

"R5. THE ANTI-LAUNDERING CLAUSE. Any record, in any location, that states a margin MUST in the SAME SENTENCE (i) name the reference as exhaustive key search at the stated key size under CM-1, and (ii) declare the published-state-of-the-art comparison UNADJUDICABLE in this environment. Transcribing a definitional-reference margin as a state-of-the-art margin — in a headline, an evidence record, a decision, a synthesis, a status line, a cross-reference, a knowledge entry, a PR title or a commit message — is a CLAIM-TIER VIOLATION and is handled exactly as docs/claims-and-verification.md handles dropping a conditional qualifier: as an assertion above what the record supports. OPERATIONALLY, under docs/inventor-protocol.md section 5: every ideation and closure deliverable under this question sets `dominated_by: \"unresolvable in this environment: no primary source reachable; every recalled frontier row is unverified-from-memory\"` and NEVER `null`, because `null` asserts the frontier was checked row by row and it cannot be. `sota_delta` records the DEFINITIONAL-REFERENCE delta, explicitly labelled as such, plus the word `unadjudicable` for the published frontier."

## Artifact paths

- coordination/goals/GOAL-AES-002/batches/BATCH-2b0fd1/tasks/TASK-20260810-2a0a37/envelope-receipt.json (covering manifest)
- coordination/goals/GOAL-AES-002/batches/BATCH-2b0fd1/tasks/TASK-20260810-2a0a37/measure_envelope.c (source with stanza; pre-existing from session-1, verified)
- coordination/goals/GOAL-AES-002/batches/BATCH-2b0fd1/tasks/TASK-20260810-2a0a37/execution-report.md (this report)
- plus the run records, drivers, arm64 sources, stamps and session receipts enumerated in the covering manifest's artifact_provenance.

## executor_assessment

- protocol_complete: true (SC-1 through SC-11 discharged; stamps and budget block written; covering manifest with closed kind vocabulary; R5 verbatim in both deliverables)
- data_quality: limited — pure-Python throughput and all inventory items are good; the accelerated throughput item is honestly invalid, which is the measured truth, not a shortfall in diligence
- requires_rerun: a successor task is needed for (a) a correct arm64 hardware-AES benchmark and (b) measured multi-core scaling; this task's own scope is complete
