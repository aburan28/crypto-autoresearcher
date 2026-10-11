# Caller-level integration plan for reusable pair tables

**State: designed, not dispatched.** This PR adds a test design only. It creates no canonical EXP/H/IDEA identifiers, changes no ledger status, launches no run, and makes no scientific-result claim. Before dispatch, the Coordinator must register an additive contract through the repository allocator and bind the accepted input artifacts and execution environment.

## Why this is the next step

The open pair-reuse measurement PR [#1382](https://github.com/aburan28/crypto-autoresearcher/pull/1382) reports a workload-dependent point-decomposition result: at N23/K16 and 512 queries its paired canonical/expanded cold-job time ratio is 0.6468878314 (about 35.3% lower); N19/K4 is near parity. It explicitly names a caller-level public-synthetic integration protocol as the next action. Its validation currently fails two committed-run-supersession tests, so its evidence must first be repaired, reviewed, and accepted. This plan is gated on that disposition.

The narrow question is whether the measured reuse effect survives when a real caller drives a sequence of decomposition requests through the existing API, with target creation, process lifetime, table setup, query work, exact witness checks, and output included. This is a finite point-decomposition engineering test. It does not measure discrete-log recovery, relation-matrix rank, a complete index-calculus attack, or performance against rho.

The earlier N19 correctness contract `EXP-KIC-7bcef8` / `RUN-KIC-278e3e` remains the source for N19 field, point, and inverse-transport controls. Its historical records stay immutable.

## Frozen comparison

Use the same caller, admitted base, target stream, binary, machine, and process boundary for three arms:

1. **Canonical table, reused:** build one exact orbit-canonical table and retain the real pair witnesses plus inverse transport data for all M queries.
2. **Expanded table, reused:** build one full-point pair table and retain it for the same M queries. This is the primary comparator.
3. **Expanded table, rebuilt:** construct the direct table afresh for each query. This estimates the value of table reuse separately from key canonicalization.

Use the two existing public-synthetic bases from #1382: N19/K4 and N23/K16. Use eight independently frozen target streams per base; each stream contains 512 subgroup targets, and M=1, 32, and 512 use the same prefixes. The target producer withholds its scalar/label sidecar from timed workers. Targets are not selected by observed decomposition success. Each arm gets a fresh process and identical input. Run four technical repetitions per arm/stream/M cell, randomizing arm order within each stream. Technical repetitions are not counted as independent streams.

Charge target admission/generation, base discovery or loading as applicable, field conversion, table build, every query (including misses), canonicalization and inverse transport, exact group verification, serialization, and process lifetime. Do not provide a target-specific join cache, precomputed witnesses, logarithms, or a full-group lookup to a timed worker. Keep setup, query, verification, and end-to-end timings separately so that an apparent query-only gain cannot hide startup cost.

## Correctness and outcomes

- Before timing, replay the existing N19 exact-three panel and all 6,909 frozen target-orbit cases through an independent checker. For the new caller, check every supplied target is on-curve and in the admitted subgroup; each successful output must contain only admitted base points and sum exactly to the original target.
- Compare all three arms on the same streams. A disagreement in verdict is an implementation-invalid result. A disagreement in returned witness is acceptable only when both witnesses independently verify.
- Retain zero-yield, timeout, crash, and right-censored cells. A censor is not an UNSAT result. Do not calculate a finite cost per witness for a zero-yield cell; report it as null with its observed cost and outcome.
- Measure peak RSS, table key count, bucket count, load factor, payload bytes, and process RSS separately. Do not equate logical table payload with allocated memory.
- No target or table from a failed attempt may be silently removed or replaced.

## Metrics and decision rule

Primary metric: cold end-to-end seconds per exact verified decomposition. Report valid decompositions per second, query success rate, and paired cold-job ratios as supporting metrics. Report N19 and N23 separately; N19 parity is a real boundary of the present evidence, not noise to pool away.

For each base and M, first aggregate four technical repetitions within each of the eight streams. Compute the canonical/reused-expanded paired ratio over streams and a two-sided 95% paired bootstrap interval with 10,000 stream resamples and a fixed, committed bootstrap seed. The primary confirmation cell is N23/K16, M=512. A caller-level finite win requires complete valid data, median ratio at most 0.80, and a 95% interval upper endpoint below 1.0. M=1 and M=32 identify the reuse break-even curve; N19 is a separately reported replication stratum. Failure to meet the threshold means no demonstrated caller-level win at this tested boundary, not a theorem against pair-table reuse.

## Dispatch gate

This design stays non-dispatchable until all of the following are true:

- PR #1382's validation failures are repaired without weakening the supersession checks, and its experiment/review disposition is committed.
- The Coordinator freezes canonical IDs, hashes for the exact production adapter, bases and target streams, commands, environment, ownership, and output paths in an additive experiment contract.
- The independent point/group checker and caller adapter pass correctness controls before timing starts.

The local checker only enforces selected design-contract invariants. Passing it does not admit or execute an experiment.
