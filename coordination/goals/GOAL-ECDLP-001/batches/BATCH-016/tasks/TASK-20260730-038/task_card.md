# TASK-20260730-038 — Validator — Independent verification of the mutation test

> **NON-AUTHORITATIVE MIRROR.** The authoritative card is the `tasks[]` entry
> for `TASK-20260730-038` in
> `coordination/goals/GOAL-ECDLP-001/batches/BATCH-016/dispatch_queue.json`.
> Where this mirror and that queue disagree, **THE QUEUE GOVERNS**.

- **Goal / batch:** GOAL-ECDLP-001 / BATCH-016
- **Role:** validator · **depends_on:** TASK-20260730-037 · **archived by:**
  TASK-20260730-040
- **Budget:** 1800 s, 2 GB, maximum_runs 1 ·
  `independent_session_required: true`
- **Runs concurrently with TASK-20260730-039.** Neither touches the Git index.

## Objective

Verify, independently and from primary sources, that the committed mutation
package says what it says and is what it claims to be. **The single most
important check in this review is that the checker under test is genuinely the
committed BATCH-015 CTRL-4 checker and not a reimplementation.**

## Check the checker provenance FIRST — a failure here is BLOCKING

Diff the CTRL-4 checker text in `mutation_driver.py` against the committed
`.../BATCH-015/probe/probe_driver.py` yourself, character by character. Verify
the recorded SHA-256, the cited source path, the cited line range and the cited
commit. Confirm every difference is listed in `mutation_manifest.json` and is
confined to the function signature and input binding. **If the checker was
rewritten rather than copied, the batch measured the rewrite and not CTRL-4.**

## Then: primary source before prior analysis

- **Re-execute all four cases yourself in a fresh process**, applying the three
  mutations exactly as the queue specifies, **before** reading the package's
  reported outcomes. A difference is a finding to report, not a defect to fix.
- **Re-derive the case-2 replacement x** from the stated rule and compare against
  the recorded x. **Re-apply the case-3 permutation** from the fixed
  specification and compare. A different x or permutation is **BLOCKING** — the
  outcome would then have been obtained on an input nobody pre-registered.
- **Recompute `pow(5, 3, p)` and `pow(1234, 3, p)`** on the computed p and
  confirm neither is 1, before accepting case (1) as a valid mutation at all.
- Re-derive every path SHA-256 in the TASK-20260730-037 receipt from the Git
  blobs at that commit and verify the parent. **An unfinished verification is
  reported as unfinished** — never PASS, never FAIL.
- **Verify `harness/` was not modified** against Git. A modified harness
  invalidates the batch and is BLOCKING.
- **Check the prohibitions from the driver source**, not only the deliverables:
  `_measure_displacement_rank`, `_collect_relations`,
  `_build_random_factor_base`, `main()` and `write_run` not called; no closure,
  no relation, no supply count, no alpha, no rank, no cost quantity, no Sage, no
  certificate, no run identifier, nothing under `experiments/`.
- **Recompute `assertion_passed_a_mutated_case`** yourself by exactly the queue's
  rule and no other, and compare. A disagreement is **BLOCKING**.
- **Check that case (1) is nowhere presented as a new result and case 0 nowhere
  presented as a result, a replication, or evidence about the factor base.**
  Flag either as BLOCKING.

## Recount everything and name its members (PRED-ID-STR)

The cardinality-not-identity failure has been recorded six times in this program
and two instances passed independent review before they were caught. Recount the
failing (j, k) sets, the candidates-scanned count, the budget sum
600 + 300 + 1800 + 1800 + 2400 = 6900, and the path declarations.

## Ceiling and honesty

Confirm no artifact asserts an alpha, a rank, a supply count, a cost, a
diagnosticity verdict, a hypothesis movement, a discharge of
DEFER-BATCH009-001, an approval of EXP-STR-004, a re-adjudication of BATCH-014
or BATCH-015, or a disposition on CTRL-4's retirement. Flag any as BLOCKING.

**State what you did not check and why.** A check whose object does not exist is
recorded as NOT PERFORMED, never as PASSED.

Session independence is required and asserted separately. **Model independence
is not available and is never claimed (INT-BATCH016-D).** Note in your report
that this batch exists because your predecessor's independent re-derivation
reproduced a tautology without detecting it (DEC-20260730-031 R-9), and that
re-deriving the same expression is not a check of it.

## Hard prohibitions

- **Mint no `VAL-*` identifier.** Two duplicated immutable identifiers are
  already on record. Your report is cited by path and task id only and must say
  so in its own text.
- **Make no commit.** Write nothing outside your review directory. Your files
  must not be committed before the TASK-20260730-040 ledger commit — three
  consecutive batches committed review artifacts one commit early.
- Bounded card: 1800 s. If you cannot finish, **stop and report a bounded
  partial review** naming exactly which checks you did not reach.

## Deliverables

- `validation_report.yaml` — explicit PASSED/FAILED verdict,
  `blocks_ledger_record` boolean, numbered findings, explicit NOT PERFORMED
  list, checker-provenance diff result, archive-chain verification results
- `recount_note.md` — every re-execution, the re-derived case-2 x, the
  re-applied case-3 permutation, the recomputed cubes, every recount with its
  arithmetic shown

## Completion gate

G1–G13 as stated in the queue entry.
