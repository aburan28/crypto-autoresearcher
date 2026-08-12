# Red-team falsification review — TASK-20260724-943 / EXP-MLKEM-009

Independent of Executor and Validator. Snapshot: `226ea0cf`.

## Attack lines

1. **OBJ-RT006-001 recurrence (INTERPOSE_COMPARE tautology)** — Cleared.
   Probes call `mlkem_cmp*`; GNU ld `--wrap` supplies `__wrap_*`; counters prove
   backend-specific library-symbol invocation.
2. **Aliased counters (OBJ-RT006-002)** — Cleared (`avx2=4`, others `0`).
3. **H-MLKEM-004 / criterion-2 paraphrase** — Cleared in package labeling.
4. **Incomplete nm listing of `__wrap_mlkem_cmp_avx2`** — Noted, non-fatal;
   runtime attestation is load-bearing and passes.
5. **claim_tier inflation** — Cleared.

## Verdict

**confirm** executor class `second_impl_unavailable` with CTRL pass via true
GNU ld `--wrap`. Do not displace to `synthetic_control_inadequate`.
