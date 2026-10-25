# ecbench replay sampler never reaches most arms of a multi-arm session

- **Status:** `open`
- **Kind:** implementation gap; access/tool limit (independent replay)
- **Affected work:**
  - Sheriff case [SHF-20261021-477d51](../research/sheriff/SHF-20261021-477d51/REPORT.md), finding F5 (claims C3 and C6);
  - `crypto:research/ic_planner_validation_20261020` (PR #2343);
  - every multi-arm `ecbench.session/v1` audit in crypto.
- **Next action owner:** unassigned. A crypto ecbench maintainer owns the
  sampler; the Coordinator decides on any replay campaign.
- **Last updated:** 2026-10-21

## Problem

We cannot claim that the counts of most arms in a multi-arm ecbench session
are replayed. This includes the denominators of every ratio in the planner
validation. The reason is that `ecbench verify --replay N` picks evenly spaced
candidates, `candidates[j * len / n]` (`crypto:src/cryptanalysis/ecbench/audit.rs:490-499`).
With k arms run in alternate order, that stride lines up with the arm blocks.

In the planner validation (8 arms, 192 measured runs per session),
`--replay 12` landed only on `plan-aa` (8 replays) and `rho-neg` (4) in all six
sessions. The five one-change arms were never replayed:
`half-base`, `double-base`, `rootfind`, `full-rank` and `random-targets`.
CI runs `--replay 0`. Every replay ran on the producer's own host and
environment class.

## Evidence and uncertainty

- **Observed:**
  - `crypto:research/ic_planner_validation_20261020/sessions/*.audit.json`,
    with each replayed seq mapped to its arm through `records.jsonl` (session
    check in SHF-20261021-477d51);
  - the receipts reader's analysis in
    `research/sheriff/SHF-20261021-477d51/readers/receipts.yaml` (F1, F2).
- **Derived or proved:** for evenly spaced picks over a sequence laid out in
  blocks of k arms, a stride that is a multiple of k revisits the same arm
  positions. Here 192/12 = 16 = 2 × 8.
- **Suspected explanation:** the sampler was designed for single-arm or
  unstructured record order. Not established for other sessions' layouts.
- **Missing capability:**
  - a sampler stratified by arm, or one driven by a nonce;
  - a replay on another host class.
  The sheriff session could not run `ecbench` at all (execution of crypto
  code was denied).
- **What this evidence does not establish:** that any unreplayed count is
  wrong. Every answer is independently verified ([k]G = Q on 1,536/1,536
  records) and every seal recomputes. Replays bound fabrication; they are not
  proofs.

## What would unblock it

- [ ] `ecbench verify` samples replays stratified by arm (at least one per
  arm), or from a nonce the producer cannot predict, and records the arms it
  covered.
- [ ] Each of the six planner-validation sessions is replayed on a host of
  another environment class, with `--replay 192` until the sampler is fixed.
  Every arm must be reproduced identically.

## Next discriminating step

- **Action or proof obligation:** build ecbench at `05a0ebd92`, then run
  `ecbench verify --dir research/ic_planner_validation_20261020/sessions/<s> --replay 192`
  for each session on another host class.
- **Inputs and controls:** the sealed sessions unchanged. Check that the
  binary hash equals `d05271011cd7…7771`, or record the difference.
- **Execution limits and stop condition:** the existing session sizes; stop
  on the first non-identical replay and report it.
- **Outcomes and next actions:**
  - all identical: F5 is closed for these sessions;
  - any difference: a broken-claim review of the affected ratio;
  - infrastructure failure: not negative evidence.
- **Recheck trigger:** a sampler change in `audit.rs`, or a replay receipt
  from another host.

## Resolution and history

- 2026-10-21: opened from SHF-20261021-477d51. Unresolved.
