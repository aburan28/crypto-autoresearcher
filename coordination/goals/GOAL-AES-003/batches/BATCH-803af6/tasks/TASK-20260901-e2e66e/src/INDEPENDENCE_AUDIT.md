# INDEPENDENCE_AUDIT.md -- TASK-20260901-e2e66e B4 build-pair audit

Requirement (task card): "The DISABLED build must differ ONLY in the exclusion flag --
any other difference invalidates the audit (state this was checked)." Documented here with
the actual diff output.

## 1. Source diff (the check)

Command: `diff src/rc8probe_b4_on.c src/rc8probe_b4_off.c`
Run 2026-09-01T17:24Z, exit code 1 (differences present), output EXACTLY:

```
77c77
< #define EXCLUDE_TRIVIAL 1
---
> #define EXCLUDE_TRIVIAL 0
```

That is the ENTIRE difference: one line, the exclusion flag. File lengths identical
(43483 bytes each). `src/rc8probe_b4_off.c` was generated from `src/rc8probe_b4_on.c` by a
script performing exactly this one string replacement (replacement count asserted == 1), so
the diff result is expected and verified, not accidental.

STATEMENT: the disabled build differs from the enabled build ONLY in the exclusion flag
(`EXCLUDE_TRIVIAL`). Checked by the diff above; this audit would be invalidated by any
further difference and none exists.

## 2. Where the toggle lives (identified and cited)

The trivial-trial exclusion logic audited here lives in `worker()`'s trial loop of the
campaign harness lineage, at two sites:

- **Site 1 (word-count gate)** -- BATCH-015 instrument
  `coordination/goals/GOAL-AES-003/batches/BATCH-015/tasks/TASK-20260805-d408ac/src/rc8probe_freshfeistel.c:441`
  (original: `if(z){ W++; if(!trivial) J->wword[j]++; }`).
  In the B4 builds: `if(z){ W++; if(!EXCLUDE_TRIVIAL || !trivial) J->wword[j]++; }`
  (marked "B4 TOGGLE SITE 1"). With EXCLUDE_TRIVIAL=1 this reduces exactly to the original.
- **Site 2 (trial skip)** -- same file, line 443
  (original: `if(trivial){ J->trivial++; continue; }`).
  In the B4 builds the `continue` is conditional: `if(EXCLUDE_TRIVIAL) continue;`
  (marked "B4 TOGGLE SITE 2"), after the shared trivial-index log. With EXCLUDE_TRIVIAL=1
  this reduces exactly to the original.
- Triviality detection itself (unchanged by the toggle, identical in both builds): same
  file, lines 421-428 -- a trial is trivial iff `c0[i] == c1[i]` on every byte of the
  smask-selected CW diagonals.

Lineage confirmation from BATCH-014 (read per task read_scope):
`coordination/goals/GOAL-AES-003/batches/BATCH-014/tasks/TASK-20260805-b95720/src/rc8probe_feistel.c`
lines 196 and 198 carry the identical two-branch structure (`if(z){ W++; if(!trivial)
J->wword[j]++; }` / `if(trivial){ J->trivial++; continue; }`), confirming the exclusion's
location is stable across the campaign harness lineage. The BATCH-015 file's own header
(lines 23-29) discloses the exclusion among the machinery copied from rc8probe.c
(BATCH-007, TASK-20260803-e55757).

## 3. Shared receipt augmentation (present identically in BOTH builds -- not a build difference)

Added to both sources verbatim (visible in the diff as common context, not as changed
lines): per-thread trivial-trial index log (`trivial_idx`/`trivial_w`, cap 64/thread =
HIT_LOG_CAP, overflow counter) and W values stored alongside hit-log entries, with
matching JSON fields. Rationale: IDEA-20260901-02f7c4's confounders field requires trivial
trials to be individually identifiable in the raw receipts, else "B4 [becomes] a new run
rather than a toggle". One receipt-side field, `hit_trials_logged`, was corrected to sum
hit counts across threads (the base instrument printed thread 0's count while its
`hit_trials` array covered all threads); this is reporting-only, identical in both builds,
and cannot affect any counter.

## 4. Byte-identical standard behavior of the ENABLED build (verification plan)

With EXCLUDE_TRIVIAL=1 the two toggle expressions reduce to the originals (`!EXCLUDE_TRIVIAL
|| !trivial` == `!trivial`; `if(EXCLUDE_TRIVIAL) continue` == `continue`), and the receipt
augmentation touches no counter. This is verified ARITHMETICALLY, not by code reading alone:
the ENABLED arms at 2^30/seed 531001/armid 1/threads 2 must reproduce the committed
immutable receipts L1-AES-R5-P30 and M1-FF-P30 field-by-field (PREREGISTRATION.md section
5 equivalence gate). A mismatch there halts the audit as an implementation failure.
