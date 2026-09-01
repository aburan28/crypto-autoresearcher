# INDEPENDENCE AUDIT — TASK-20260901-47b21f (RC-D second seed/key)

Audit required by the task card: (1) the AES arm and the Feistel arm share no
generation code on the oracle side, and (2) S2 = 531002 affects key and trial
stream exactly as documented in the sources — traced below line-by-line. Both
sources were read in full by this task (347 lines rc8probe_feistel.c;
835 lines rc8probe_freshfeistel.c), verbatim copies whose sha256 parity with
the archived files is recorded in `src/BUILD.md`.

This audit reuses and extends the side-by-side established by BATCH-014's own
INDEPENDENCE_AUDIT.md for `rc8probe_feistel.c` (the file is byte-identical, so
that audit applies to this task's copy without change); the new content here
is the AES-arm instrument audit (§2) and the S2 seed-path trace (§3).

## 1. Oracle-side code disjointness: Feistel arm

`rc8probe_feistel.c`'s oracle zone is `feistel_F` (lines 69-78),
`feistel_round_keys` (84-91), `feistel_encrypt` (96-107), `feistel_decrypt`
(109-120), and the global `RK[16]` (62-63). It contains:

- NO AES S-box / inverse S-box arrays, no `GLOG`/`GEXP` tables, no
  `gmul`/`ginv`, no `0x1b` GF(2^8) reduction constant, no byte substitution.
- NO MixColumns tables (`M2/M3/M9/MB/MD/ME`), no GF(2^8) multiply, no
  `02/03/09/0b/0d/0e` column-mix constants.
- NO ShiftRows-style byte-array row rotation (the Feistel state is two 64-bit
  words; the only shifts are word-level `v ^= v >> 33` xor-shifts).
- NO Rijndael key schedule (`key_expand`, RCON, RotWord/SubWord). Its schedule
  is splitmix64 seeded from the key halves (harness RNG, not AES machinery).
- The round function's only arithmetic is add/xor-shift/multiply by the two
  public murmur3 fmix64 64-bit odd constants under Z/2^64 wraparound —
  different field, different width, different constants from anything AES.

## 2. Oracle-side code disjointness: AES arm instrument

The AES arm is run from `rc8probe_freshfeistel.c` in `oracle == 0` (aes) mode
ONLY. In that mode the worker calls exactly `enc_r`/`dec_r` (lines 196-213),
the AES code copied byte-for-byte from rc8probe.c (source header disclosure,
verified by BATCH-015's byte-exact reproduction of P1-R5-PAIR, EV-AES-4ba350
OBS-B15-4): `gf_init`/`GLOG`/`GEXP`, `gmul`/`ginv`, `SBOX`/`ISBOX`,
`build_aes_sbox`, the six MixColumns tables, `key_expand`, `add_rk`,
`sub_bytes`/`inv_sub_bytes`, `shift_rows`/`inv_shift_rows`,
`mix_columns`/`inv_mix_columns`. The binary refuses the AES arm unless the
FIPS-197 C.1 KAT + round-trip pin gate passes (main lines 813-818).

The SAME file also contains BATCH-015's fresh-feistel oracle
(`ff_F`/`sipround`/`ff_trial_subkeys`/`ff_encrypt`/`ff_decrypt`, lines
268-329). **None of it executes in this task:** the worker takes the
`J->oracle == 0` branch for both encryption and decryption (lines 402-404,
429-431); the fresh-key draw (`sm64(&kst)`, line 409), key-stream digest
accumulation, and per-trial subkey derivation are all inside the
`oracle == 1` branch; `main` for `oracle == 0` runs `key_expand` from the
seed-derived key and never calls `ff_gate`'s measurement path (the gate it
runs is `do_pin`). The `aes`-mode JSON additionally self-declares
`fresh_key_per_trial: false` and `resampled_per_trial: false`, which this
task's run output (`runs/AES-P30-S2.json`) carries.

Disjointness between the two arms' oracles therefore holds in both
directions:

| | Feistel arm (rc8probe_feistel) | AES arm (rc8probe_freshfeistel, aes mode) |
|---|---|---|
| round function | murmur3 fmix64: add, xor-shift, ×odd-64-bit-const, Z/2^64 | SubBytes (GF(2^8) inverse + affine), ShiftRows, MixColumns (GF(2^8) tables), AddRoundKey |
| key schedule | splitmix64 from key halves → 16×64-bit subkeys | Rijndael AES-128 44-word expansion, RCON, S-box SubWord |
| block structure | two 64-bit halves, 16-round Feistel ladder | 4×4 byte state, 5-round SPN (r=5) |
| shared tables/constants | none | none |
| shared executable code | none (different binaries) | none (different binaries) |

The murmur3 constants (`0xff51afd7ed558ccd`, `0xc4ceb9fe1a85ec53`) appear in
`rc8probe_freshfeistel.c` exactly once, inside `keycheck`'s set-hash (line
535), a validation-only path not executed by `arm ... aes` runs; disclosed as
a cosmetic-only overlap, matching BATCH-015's own disclosure.

## 3. S2 seed path trace — what 531002 touches, exactly

### 3.1 Feistel arm (`rc8probe_feistel.c`, verbatim)

`main`, arm mode:

1. `seed = strtoull(argv[7])` (line 273) — S2 = 531002 enters here and
   NOWHERE else.
2. **Key path:** `kst = seed ^ 0xA5A5A5A5A5A5A5A5` (278) → two splitmix64
   draws fill `key[16]` (280-283) → `feistel_round_keys(key)` (284) derives
   the 16 round subkeys `RK[]` ONCE, before any thread spawns; `RK[]` is then
   read-only global state for the whole run. S2 → new 128-bit master key →
   new subkeys → a different fixed permutation. Recorded in the run JSON:
   `key_hex 58146703b42fca722bc0ab918cd1409b` (vs RC-D's
   `bdf3823182ad657dab3d556b3886ba72` at 531001 — different, as required).
3. **Trial-stream path:** `jobs[t].seed_thread = seed ^ (armid*0x1234567891)
   ^ ((t+1)*0x9E3779B97F4A7C15)` (292-293) → each worker's splitmix64 state
   `st` (151) → plaintext draws `a,b = sm64,sm64` (155) → p0/p1 bytes, then
   the rejection loop's draws (163). S2 → a different plaintext/trial stream
   in every thread.
4. Nothing else in the binary reads `seed`: geometry (`build_geom`) is
   constant; masks, rounds, thread count come from other argv fields held at
   RC-D's values.
5. `detcheck` mode derives its key by the identical formula (251-258), so
   `runs/detcheck-S2.json` gated exactly the key the arms used.

### 3.2 AES arm (`rc8probe_freshfeistel.c`, aes mode)

`main`, arm mode:

1. `A.seed = strtoull(argv[8])` (line 806) — S2 enters here.
2. **Key path:** `oracle == 0` branch: `kst = A.seed ^ 0xA5A5A5A5A5A5A5A5`
   (819) → two splitmix64 draws fill `key[16]` (821-824) → `key_expand` (825)
   produces the AES-128 round keys `rk[11][16]` used for the whole run. The
   derivation formula is BYTE-IDENTICAL to the Feistel arm's master-key
   derivation (same constant, same RNG, same draw order), so at S2 both arms
   use keys derived from the same 128-bit master bytes — one as an AES-128
   key, one as the Feistel master key. This is the campaign's standing
   key-coupling design (also how 531001's key was shared in BATCH-009/014).
3. **Trial-stream path:** `jobs[t].seed_thread = A.seed ^ (A.armid*
   0x1234567891) ^ ((t+1)*0x9E3779B97F4A7C15)` (603-604) → worker `st` (370)
   → identical draw sequence to the Feistel worker (a,b at 381; rejection
   loop 386-397 with identical order and geometry).
4. The key-stream seed `seed_key_thread` (608) is also computed from S2, but
   in aes mode its stream is NEVER drawn (worker line 409 is inside the
   oracle==1 branch); it only appears in reported fields. No effect on the
   measurement.

### 3.3 Matched-stream verification at S2 (recorded from the run JSONs)

Both arms at (seed 531002, armid 1, threads 4) report IDENTICAL
`thread_seeds` arrays — `AES-P30-S2.json` and `F16-P30-S2.json`:
`[11400714758317678270, 4354685486758533761, 15755400460690855572,
8709371206315774719]` — and their plaintext-draw loops are line-for-line the
same construction (same sm64 call order per trial, same rejection rule, same
PW/CW geometry), so the two arms walk byte-identical plaintext streams by
construction. This is a code-inspection + thread-seed-equality verification,
the same standard RC-D applied (V3); a byte-level digest EQUALITY check is
not available across these two binaries because they implement two different
order-sensitive digest formulas over the stream (RC-D: byte-wise FNV,
`digest ^= byte; digest *= 1099511628211`, lines 176-177; BATCH-015
instrument: word-wise FNV over 8-byte words, lines 398-401). Disclosed, as
RC-D disclosed it; the digests in each JSON still pin each arm's own stream
for the validator.

The cipher-DEPENDENT per-trial exclusion (trivial swaps) legitimately
differs: AES-P30-S2 excluded 1 trivial swap, F16-P30-S2 excluded 0 — whether
a drawn pair is trivial depends on the ciphertexts, hence on the oracle,
exactly as across BATCH-009/014/015's arms. `nontrivial_trials` therefore
differs by 1 between the arms and the frozen comparator machinery consumes
each arm's own value (exposure-weighted p0), as it did for RC-D's M1.

## 4. Shared harness machinery (disclosed, required, not oracle code)

By design of the matched-exposure comparison, the two arms SHARE the trial-
generation and counting harness: splitmix64; the plaintext draw + rejection
loop; trivial-swap exclusion; PW/CW ShiftRows-diagonal probe geometry; W
counting; the per-thread seed formula; the worker/job threading structure;
CLI/JSON shape. This shared machinery is what makes the comparison matched;
it was copied from rc8probe.c in both lineages and is disclosed in both
sources' headers. It contains no cipher-specific operation: nothing in it
depends on which oracle is called at `enc_r`/`dec_r`.

## 5. Verbatim control restatement

`src/rc8probe_feistel.c` here is byte-for-byte the archived BATCH-014 file
(sha256 match, `cmp` identical — `src/BUILD.md`); the Feistel arm's validity
therefore inherits BATCH-014's validator-confirmed independence audit
(EV-AES-dec938 OBS-B14-1, by direct code read) without modification, and this
task varied ONLY the seed CLI field. `src/rc8probe_freshfeistel.c` is
byte-for-byte the archived BATCH-015 file, whose AES path BATCH-015's
validator confirmed reproduces the frozen comparator byte-exactly
(EV-AES-4ba350 OBS-B15-4).

## Inference block

```yaml
inference:
  policy: executor-implementation
  requested_policy: executor-implementation
  resolved_model: fireworks-ai/accounts/fireworks/models/qwen3p8-max
  fallback_used: true        # transport fallback to session backend under DEC-20260831-0d1eeb (zai billing outage)
  model_verified: false
  standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
```

Parse statement: prose audit; the machine-parseable records are the JSON
artifacts of this task, each parsed whole before the task finishes.
