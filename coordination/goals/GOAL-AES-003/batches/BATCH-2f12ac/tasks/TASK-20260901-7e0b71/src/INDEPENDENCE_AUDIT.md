# INDEPENDENCE_AUDIT.md — TASK-20260901-7e0b71 (source-diff audit, non-perturbation proof)

Audit of `src/affarm046e.c` against its lineage
`coordination/goals/GOAL-AES-003/batches/BATCH-fe0bdc/tasks/TASK-20260901-f5d3a4/src/affarm046.c`.
Full machine diff: `runs/source_diff.txt` (generated with `diff -u affarm046.c affarm046e.c`;
765 lines; 66 removed lines, 521 added lines — every removed line is accounted for below).
IDEA-20260901-363851 `integrity_gates.source_diff_audit` requires: round functions, geometry,
RNG, trial loop, and counter updates UNCHANGED; the diff must consist only of (i) the widened
table surface, (ii) the e-logging block (pure reads after all trial decisions into new
counters only), (iii) the widened receipt emission. Any diff line touching the trial stream
or existing counters voids the gate (F4).

## Annotation table (every changed region)

| Diff region (source_diff.txt) | Change | Class | Perturbation analysis |
|---|---|---|---|
| header comment (lines 4-98) | prose replaced | comments only | none |
| `+#include <stddef.h>`, `+#include <time.h>` | new includes | (iii) support | size_t / clock_gettime for reporting helpers; no code-path change |
| `+wall_now()` | new helper | (iii) | timing report only; called outside the trial loop |
| `+POS_ORDER[16]`, `+TPOS[16][256]`, `+INV_TPOS[16][256]`, `+DIL_K`, `+set_diluted_tables`, `+diluted_tables_ok`, `+diluted_position_list` | new table surface | (i) widened table surface | new static tables + constructors; deterministic functions of k; no seeds/draws |
| `+SHA-256 core`, `+sha256_tpos_concat` | new digest utility | (iii) | report-only (arm_table_concat_sha256); validated against Python hashlib on 3 vectors before use |
| `sub_shift`: `t[4*c+r] = SBOX[s[4*((c+r)&3)+r]]` → `int p=4*((c+r)&3)+r; t[4*c+r] = TPOS[p][s[p]]` | table lookup widened | (i) | index expression `4*((c+r)&3)+r` UNCHANGED; at k=0 TPOS[p][v]=v (identity), at k=16 TPOS[p][v]=SBOX[v] for all p — bit-identical to the original expression at both Stage-0 seats; empirical proof = Gate 0 |
| `inv_sub_shift`: `INV_SBOX[...]` → `INV_TPOS[4*c+r][...]` | table lookup widened | (i) | source index expression UNCHANGED; destination-position table per the frozen construction pin; identical reduction at k∈{0,16} |
| `add_rk`, `mix_columns`, `inv_mix_columns`, `enc_r`, `dec_r` | UNCHANGED bodies | — | diff shows comment labels only |
| `sm64`, `xt`, `gmul`, `XT2/XT4/XT8`, `build_sbox`, `build_inv_sbox`, `set_aes_sbox`, `set_identity_sbox`, `identity_tables_ok`, `build_xt_tables`, `key_expand`, `sched_init`, `build_geom`, PW/CW | UNCHANGED | — | RNG and key schedule byte-identical |
| `+#define HIT_LOG_CAP 64`, job-struct additions (`ewhist_*`, `ewbithist_*`, `hit_*`, `pstream_digest`) | new counters appended after the original fields | (ii) | original job fields unchanged; calloc zero-inits; nothing reads the new counters in any decision |
| worker: `+uint64_t pdig = 1469598103934665603ULL;` and digest-update block after the rejection loop | new counter, pure read of final p0,p1 | (ii) | expression-identical port of rc8probe_freshfeistel.c:398-401 at the same loop position; reads p0/p1 only; `st` (RNG state) untouched |
| worker: draws `a=sm64(&st), b=sm64(&st)`, rejection loop (`rnd=sm64(&st)`), `enc_r`, swap+trivial detection, `dec_r`, Z-count, W-loop (`W++; if(!trivial) J->wword[j]++`), `if(trivial){J->trivial++; continue;}`, `J->zhist[Z]++; J->whist[W]++; if(W>=1) J->wge1++;` | UNCHANGED (context lines in diff) | — | trial stream, decisions, and all pre-existing counter updates byte-identical |
| worker: e-logging block after the `wge1` update | pure reads of q0,q1,p0,p1 AFTER all trial decisions, into new counters only | (ii) | computes e_i=(q0[i]^q1[i])^(p0[i]^p1[i]), wt(e) byte/bit, vanishing mask (independent re-computation from q0/q1; the W-loop itself untouched); writes only `ewhist_*`, `ewbithist_*`, `hit_*` — none of which feeds any decision, RNG state, or pre-existing counter |
| worker: `+J->pstream_digest = pdig;` at loop end | store of new counter | (ii) | none |
| `+stream-gap helpers`, `+KEYARM_C1/C2`, `+key_thread_seed` | report-only arithmetic | (iii) | expression-identical port of rc8probe_freshfeistel.c:345-349/462-484; computed at setup/emission, never inside the trial loop |
| `pin()` | UNCHANGED body | — | comment label only |
| `pinidentity()`: `+set_diluted_tables(0)` | table init for the widened surface | (i) | required because enc_r now reads TPOS; sets TPOS = identity, making the round function exactly what it was before on this path |
| `geom_mode()` | UNCHANGED body | — | comment label only |
| `+freeze_mode`, `+mini_arm_emit`, `+FREEZE_KS` | new mode | (iii)+(i) | table freeze for all 7 frozen points + preregistered folded smoke self-checks; reuses the unmodified worker; runs only in freeze mode |
| `main()`: `+set_diluted_tables(16)` at startup | table init | (i) | TPOS = full AES table for pin mode and the k=16 seat |
| `main()`: `+freeze` dispatch; arm-token widening `identity` → `{identity, aes}` with explicit interior-k refusal | arm surface | (i) | k=0 path unchanged; k=16 path sets AES tables + AES schedule (the committed seat convention); interior arms refused, not guessed |
| `main()` arm setup: `jobs[t].ntrials`, `jobs[t].seed_thread = seed ^ armid*0x1234567891 ^ (t+1)*0x9E3779B97F4A7C15`, rounds/amask/smask/s assignments | UNCHANGED (context lines) | — | thread-seed formula and chunking byte-identical (line 625 of the diff is a context line) |
| `main()`: `+cinv`, `+pseed[]`, `+kseed[]`, `+t0`, `+t1` | report-only | (iii) | no trial-path effect |
| `main()` aggregation: original `zh/wh/wword/trivial/wge1` sums UNCHANGED, `+ewhist/ewbithist/hit_overflow` sums appended | counter aggregation | (ii)+(iii) | every original accumulation preserved verbatim within the modified lines |
| `main()` receipt emission | rewritten to the committed L1-AES-R5-P30 field set in committed order + preregistered added fields | (iii) | emission-only; allowed-diff discipline policed by gate0_cmp.py |

## Removed-line accounting (66 lines)

All 66 `-` lines are one of: (a) header-comment prose replaced by the derivative's header;
(b) the two `sub_shift`/`inv_sub_shift` lookup lines replaced by their widened-surface
equivalents (class (i), bit-identical at k∈{0,16}); (c) the old receipt-emission printf
block replaced by the widened emission (class (iii)) — including the old
`"sbox": "identity"` / `sbox_bijective` / `sbox_table_hex` / `key_hex` / `zhist` emission
lines, all of which reappear in the new emission with identical semantics; (d) the old
arm-token check line `if(strcmp(argv[10],"identity")!=0)` replaced by the widened
`{identity, aes}` parse (class (i)); (e) the old `set_identity_sbox()` /
`identity_tables_ok()` pair, now inside the `ksel==0` branch (unchanged semantics for the
identity seat). NO removed line touches sm64, the trial draws, the rejection loop, the key
derivation `kst = seed ^ 0xA5A5A5A5A5A5A5A5`, the round functions' bodies, the geometry, or
any pre-existing counter update.

## Thread-seed / key conventions (attested identical)

- per-thread plaintext seed: `seed ^ armid*0x1234567891 ^ (t+1)*0x9E3779B97F4A7C15`
  — byte-identical line in both files (context line in the diff).
- AES key derivation: `kst = seed ^ 0xA5A5A5A5A5A5A5A5`, two splitmix64 draws,
  little-endian — byte-identical line in both files.
- chunking: `per = N/nthr`, remainder on thread 0 — byte-identical.
- Build-phase numeric check: the formulas reproduce L1-AES-R5-P30's thread_seeds,
  key_stream_seeds, and key derivation exactly (see BUILD.md).

## Empirical non-perturbation proof

Gate 0 (R4): the logging-ON worker must reproduce L1-AES-R5-P30 FIELD-BY-FIELD at seed
531001 — 14 hit indices, whist, W_ge1_*, trivial, nontrivial, thread_seeds,
plaintext_stream_digest, sbox_first8. Any perturbation of stream, key, round function, or
existing counters would move at least one of the 14 indices or one histogram/digest field.
Result recorded in `runs/R4_gate0_cmp.json`.

## Inference block

policy: executor-implementation; requested_policy: executor-implementation;
resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max (ACTUAL session model
under inference amendment DEC-20260831-0d1eeb); model_verified: false; fallback_used: true;
degraded_requirements: []; amendment: DEC-20260831-0d1eeb;
standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c.
