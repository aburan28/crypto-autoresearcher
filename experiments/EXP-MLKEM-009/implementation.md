# EXP-MLKEM-009 implementation notes

Executor task: `TASK-20260724-940`. Observations only.

## Repairs relative to EXP-MLKEM-006

- Replaced `-DINTERPOSE_COMPARE` call-site bypass (OBJ-RT006-001) with true
  GNU ld `-Wl,--wrap=mlkem_cmp,--wrap=mlkem_cmp_avx2,--wrap=mlkem_cmp_neon`
  on Docker `linux/amd64` (GNU Binutils ld 2.40).
- Substantive probes call `mlkem_cmp*` as usual; the linker redirects those
  references to `__wrap_mlkem_cmp*`, which implement the defective control.
- Per-symbol wrap call counters are independent (OBJ-RT006-002).
- Load-bearing CTRL pass requires `wrap_link_method=gnu_ld_Wl_wrap_mlkem_cmp_family`
  and a positive backend-specific counter.
- Second peer: re-check strict fixed-bound once; if empty, record
  `goal_criterion_2_disposition=second_impl_unavailable`; optional widened
  PQClean measurement is laboratory continuity only (not H-MLKEM-004 / criterion 2).
- Exact argv in every `command.txt`; build wall-clock in
  `/tmp/exp-mlkem-007/pre-run/build_timing_receipt.json`.
- claim_tier remains `laboratory_implementation_conformance`.

## Scope

No key recovery, oracle construction, exploitation path, disclosure,
or deployed-system interaction occurred. Library comparison logic was
not modified.
