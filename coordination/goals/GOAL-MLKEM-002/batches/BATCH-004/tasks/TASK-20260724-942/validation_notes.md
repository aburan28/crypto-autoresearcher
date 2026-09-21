# Validation notes — TASK-20260724-942 / EXP-MLKEM-009

Independent of Executor session. Snapshot basis: `226ea0cf` (TASK-20260724-941).

## Hash integrity

Recomputed SHA-256 for all 63 paths in the snapshot receipt: **0 mismatches**.

## OBJ-RT006-001 / OBJ-RT006-002 repair

| Check | Result |
| --- | --- |
| `library_cmp` calls `mlkem_cmp*` (no `INTERPOSE_COMPARE`) | pass |
| Link method `gnu_ld_Wl_wrap_mlkem_cmp_family` | pass |
| `__wrap_mlkem_cmp*` in `compare_wrap.c` | pass |
| AVX2 wrap counter = 4; scalar/neon = 0 | pass (independent counters) |
| GNU ld 2.40 + wrap flags archived | pass |

## Outcome

Executor class `second_impl_unavailable` with CTRL pass is consistent with frozen EXP-007 precedence when the strict fixed-bound neighborhood is empty. Adequacy repair is admitted at instrument level; empty-neighborhood disposition is bookkeeping for GOAL criterion 2, not evidence against wrap adequacy.

## Qualifications

Docker linux/amd64 on arm64 host; no NEON builds this batch; claim_tier laboratory only; no H-MLKEM-004 paraphrase of EV-MLKEM-008/009.
