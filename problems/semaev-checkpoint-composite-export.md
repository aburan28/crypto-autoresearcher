# Checkpoint qualification: composite cases versus rectangular export

Requirement: retain truthful, protocol-bound qualification evidence and a valid experiment export before promoting recovery qualification. No manufactured reference/control executions.

Observed: the fourteen local fake-S3 cases passed, with all283 archived files verified in commit de2231d534. However checkpoint-transport-protocol-002 declares four arms, while its harness executes fourteen composite cases with embedded assertions. The exporter expects56 rows. The truthful14-row export in `../analysis/semaev-degree-five-quotient-lift/reports/checkpoint-transport-001/` fails validation. Its findings also preserve the collector's noncanonical instance identifiers and missing fixed schedule labels. These are reporting/protocol defects, not failed transport assertions or cloud evidence.

The schema requires at least two arms, so a single-composite-arm draft was refused before data and was never executed. A prospective protocol003 instead specifies two actual, useful retention configurations: retain local snapshots, and prune only after verified publication. The same fourteen controls execute in each configuration, with case-specific pruning overrides held fixed, explicit instance ids0..13 and schedule seed0 (no RNG). Original records and export failure remain unchanged. New data must be collected under the new frozen protocol and yield28 actual rows.

Next test: run `qualify_checkpoint_transport_modes.py` once per frozen retention arm after checkpoint gate, preserve both result sets and raw files, and validate the complete export. Passing the mock suite still does not establish actual S3 permissions, pod recovery, or an LFD bound. The separate producer qualification remains active and needs its own scope/coverage/export audit when complete; do not silently treat composite assertions as independent arms there either.

Exit criteria: accurately registered prospective configurations, all fixed cases executed, no missing or invented rows, export file hashes and protocol validation pass, then actual cloud publication/restoration and original independent checker acceptance. No change to the original degree-six objective.

## 2026-10-30 completed evidence

The prospective transport protocol003 now has28 actual rows: all14cases ran in each of retain/prune, allpassed, and export validation with file verification has zero findings. Evidence and report: `../analysis/semaev-degree-five-quotient-lift/reports/checkpoint-transport-002/`. This closes the mock transport registration gap only.

The producer suite also completed:150descriptions,147native cases and3unsupported zero-codomain seeds;1245childsteps. All10coverage flags true; no recorded assertion failures. Full36003-file archive verified and stored, pointers in `validation/checkpoint-producer-001`. Its four-arm protocol implies600rows but it records150composite fixtures, so its truthful export remains invalid; see `reports/checkpoint-producer-001/export-validation.json`. Three unsupported native rows are marked cancelled, not successes. Do not reconstruct independent arms from embedded assertions.

The real cloud protocol separately registers reference/publication and restored roles across the same3fixtures. Attempt001 failed before native launch; all3failedsource rows and missingdependentrows remain in its report. Corrected protocol002 is frozen and its sourcejob is active at06:22UTC. A successful source job alone will not resolve fresh-worker recovery.
