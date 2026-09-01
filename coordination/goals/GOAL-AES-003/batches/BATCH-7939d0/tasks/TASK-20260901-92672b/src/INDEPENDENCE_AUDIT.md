# INDEPENDENCE_AUDIT.md — TASK-20260901-92672b

Code-level audit, written by the Executor before measurement arms run.
Raw grep record: `src/grep_independence.txt` (G1–G8, this task's own
invocations). Source hashes (G7): archived RC-D source sha256
`9b36c0e714118e11e160b9aec81c9a6c1aceecc6fb2b6c452b3dd3bbf98d8566`;
parameterized source `020a4c29011ee1d1a5c0db8ab215ee079e53bbdff4ef2e23dc038125f615ff70`;
BATCH-015 AES/ff instrument source
`d163b64e6b0d6bce1f23027bb7209c0a8c5ef1984874465119f61adf3e0d450d`.
Worktree HEAD at audit time: `a91cb64ac68c8315eb764edfb89c9fc34d99c3b0`.

## 1. The r=16 variant is line-for-line identical to RC-D except the parameterization point

`src/diff_vs_archived.txt` is the full `diff -u` of
`BATCH-014/tasks/TASK-20260805-b95720/src/rc8probe_feistel.c` against this
task's `src/rc8probe_feistel_rk.c`. The diff contains exactly ONE hunk:

```
+#ifndef FEISTEL_ROUNDS
 #define FEISTEL_ROUNDS 16
+#endif
```

i.e. 2 added lines, 0 deleted, 0 modified content lines (G8: 4 `[+-]` lines
including the two context-free additions). The round function `feistel_F`,
the key schedule `feistel_round_keys`, `feistel_encrypt`/`feistel_decrypt`,
the PW/CW geometry, the worker, the detcheck, the CLI parsing, and every
printf in the JSON reporting are byte-identical to the archived source. This
holds for ALL four variants: they are the same file compiled with
`-DFEISTEL_ROUNDS=<r>`, so variant-vs-variant differences are exactly the
round count and nothing else (same round function, same key-schedule code,
same first-r-subkey prefix property — for a given seed the r=4/8 subkeys are
a prefix of the r=16 subkey stream and r=32 extends it; disclosed in
PREREGISTRATION.md §7(ii)).

## 2. AES arm and Feistel arms share no generation code

Two separate binaries, two separate sources:

- Feistel arms: `src/rc8probe_feistel_rk.c` → `rc8probe_feistel_r{4,8,16,32}`.
  The oracle zone is `feistel_F` / `feistel_round_keys` / `feistel_encrypt` /
  `feistel_decrypt`: 64-bit integer add/xor-shift/multiply (murmur3-fmix64
  family constants `0xff51afd7ed558ccd`, `0xc4ceb9fe1a85ec53`), no GF(2^8)
  arithmetic, no S-box table, no byte permutation. G1/G2: every
  AES-vocabulary token in the file (`sbox`, `MixColumns`, `ShiftRows`,
  `key_expand`, `sub_bytes`, `GF(2^8)`, `aes`, ...) occurs ONLY inside
  provenance-disclosure comments (lines 1–41, 57–59, 69–70, 83, 125 of the
  archived line numbering). The only executable identifiers shared with the
  AES world are the harness call-site names `enc_r`/`dec_r`, whose bodies
  (G3, lines 128–129) call ONLY `feistel_encrypt`/`feistel_decrypt` — a
  naming shim for worker compatibility, no AES code. G6: includes are
  stdio/stdlib/string/stdint/pthread only; nothing is included from any AES
  or other-instrument file.

- AES arm: `src/rc8probe_freshfeistel` built from BATCH-015's archived
  `rc8probe_freshfeistel.c`, run in `arm <name> aes ...` mode. In that mode
  (G5): the worker's oracle branch is `J->oracle == 0`, which calls
  `enc_r(p, c, rk, r)` / `dec_r(c, q, rk, r)` — the AES round functions with
  `key_expand`-derived AES round keys (rc8probe.c's AES code copied
  byte-for-byte per BATCH-015's own audit, including the FIPS-197 C.1 KAT pin
  gate in `do_pin` that refuses to measure if AES encrypt/decrypt is wrong).
  The `ff_*` fresh-Feistel functions are reached ONLY under
  `J->oracle == 1`, which the AES arm never sets. No `ff_*` call is reachable
  from the AES arm's code path.

- Cross-direction check (G4): `rc8probe_freshfeistel.c` contains NO call or
  definition of RC-D's `feistel_F`/`feistel_round_keys` and none of RC-D's
  key-schedule constants. The two grep hits are: line 47, a comment
  disclosing that RC-D's oracle was NOT reused; and line 535, the murmur3
  first constant used as a set-hash mixer inside the `selfcheck` keycheck
  table only — selfcheck is a separate validation mode that the AES arm never
  executes (the AES arm path runs `do_pin`, not `selfcheck`), and this
  cosmetic hit was already disclosed by BATCH-015's own audit. It is not in
  any measurement code path of either the AES arm or this task's Feistel arms.

- Shared machinery, disclosed (harness-only, per the campaign's
  copy/adapt-don't-reinvent practice, same as RC-D's own disclosure):
  splitmix64 plaintext generation, the PW/CW probe geometry, the
  trivial-swap exclusion, the W counting, the order-sensitive plaintext-stream
  digest, and the JSON reporting shape. This shared machinery generates the
  PLAINTEXT pairs and counts the statistic identically in all arms — which is
  exactly what a matched-exposure comparison requires — and contains no
  cipher/round-function code.

## 3. Determinism at fixed thread count (code read)

In `rc8probe_feistel_rk.c` (unchanged from the archived source): each thread
gets `seed_thread = seed ^ armid*0x1234567891 ^ (t+1)*0x9E3779B97F4A7C15`
computed before `pthread_create`; workers share no mutable state (each `job`
struct is thread-private; `RK[]` is written once in `main` before any thread
starts and read-only thereafter); per-thread counters are summed in fixed
thread order after `pthread_join`; JSON is emitted in fixed order. Output is
therefore a deterministic function of (source, compile-time FEISTEL_ROUNDS,
argv) — thread count changes only the deterministic per-thread chunking
(`per = N/nthr`, remainder to thread 0), never introducing scheduling
nondeterminism. This task uses 4 threads for all Feistel arms (identical to
RC-D's M1) and 2 threads for the AES arm (identical to BATCH-015's L1 and
BATCH-009's P1), so no thread-count variation occurs anywhere in the
comparison and no 4-vs-8 thread smoke is required (PREREGISTRATION.md §4).

## 4. What this audit does NOT claim

It does not claim the Feistel construction is ideal, indistinguishable from
AES, or representative of all non-AES PRPs; it claims only code-level
non-sharing of generation code between arms and line-for-line provenance of
the variants. Statistical closeness questions are out of scope for this task
(toy tier; no crypto-scale claim in either direction).
