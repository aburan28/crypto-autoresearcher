# INDEPENDENCE AUDIT — `rc8probe_feistel.c` (TASK-20260805-b95720)

Side-by-side comparison against (1) AES's actual round-function tables as
they appear in `rc8probe.c` (BATCH-007), (2) the `yoyo_sbox_v2`/`v3`/`v4`
lineage (BATCH-004/006/008/009), and (3) rc8probe's own ideal-permutation
(`perm128`) architecture (BATCH-011/BATCH-012, `rc8probe_ideal.c`). Bar to
meet, per the task card: same independence standard BATCH-011's own audit met
(EV-AES-acddd0 OBS-B11-1: zero shared symbols in either direction, confirmed
by grep and by an independent validator), PLUS independence from AES's own
actual operations (which BATCH-011's rc8probe extension did NOT need, since
it reused AES itself for its live arm).

## 1. AES's actual round-function tables (what `rc8probe_feistel.c` does NOT use)

### 1.1 The AES S-box (first 16 of 256 bytes, FIPS-197 / `rc8probe.c` `SBOX[]`)

```
63 7c 77 7b f2 6b 6f c5 30 01 67 2b fe d7 ab 76 ...
```

Built in `rc8probe.c` (`build_aes_sbox`, lines 77-82) as
`SBOX[a] = inv(a) XOR rotl8(inv(a),1) XOR rotl8(inv(a),2) XOR rotl8(inv(a),3)
XOR rotl8(inv(a),4) XOR 0x63`, where `inv` is multiplicative inverse in
`GF(2^8)` with reduction polynomial `x^8+x^4+x^3+x+1` (the `0x1b` reduction
constant in `gf_init`, line 53).

**`rc8probe_feistel.c` contains no S-box array, no GF(2^8) log/antilog table
(`GLOG`/`GEXP`), no `gmul`/`ginv`, no `0x1b` reduction constant, and no byte
substitution step of any kind.** Grep-verified (see §4).

### 1.2 AES's MixColumns matrix (the `M2/M3/M9/MB/MD/ME` tables, lines 111-119)

MixColumns multiplies each column by the fixed `GF(2^8)` matrix

```
| 02 03 01 01 |
| 01 02 03 01 |
| 01 01 02 03 |
| 03 01 01 02 |
```

(and its inverse, `0e 0b 0d 09` per row for InvMixColumns), computed via the
`gmul` GF(2^8) product tables built from the same `0x1b`-reduction
multiplication.

**`rc8probe_feistel.c` contains no MixColumns step, no GF(2^8) multiply
table, and no `02/03/09/0b/0d/0e` constants anywhere.** The Feistel round
function's only multiplications are by the 64-bit odd integer constants
`0xff51afd7ed558ccd` and `0xc4ceb9fe1a85ec53` (the well-known murmur3
`fmix64` finalizer constants) under plain 64-bit modular (wraparound)
integer multiplication — arithmetic over `Z/2^64`, not `GF(2^8)`, and sharing
no constant with AES's MixColumns matrix.

### 1.3 AES's ShiftRows permutation (lines 154-161, 216-217)

`ShiftRows: out[4c+r] = in[4*((c+r)&3)+r]` — a row-wise cyclic rotation of
the 4x4 byte state, row `r` rotated left by `r` positions.

**`rc8probe_feistel.c` contains no byte-array state, no 4x4 row/column
indexing, and no rotation of state bytes.** The Feistel network operates on
two 64-bit integer halves with a bit-level xor-shift (`v ^= v >> 33`), which
is a shift-and-xor on a 64-bit word, structurally unrelated to a byte-array
row rotation (different operand type, different operation, different width,
no correspondence table exists between the two).

*(The `PW`/`CW` probe-geometry arrays in `rc8probe_feistel.c`, lines
"---------------- geometry", ARE copied byte-for-byte from `rc8probe.c` —
disclosed in the file's header comment. These implement the MEASUREMENT
harness's diagonal probe masks, not the oracle; they are part of what the
task card required to hold fixed across arms for a matched-exposure
comparison, not part of the substitute cipher under test.)*

### 1.4 AES's key schedule (`key_expand`, lines 123-142)

Word-oriented Rijndael key expansion: `RotWord`, `SubWord` (an S-box lookup),
`Rcon` XOR, using the RCON table `{0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,
0x1b,0x36}` (successive powers of `x` in `GF(2^8)`).

**`rc8probe_feistel.c`'s key schedule (`feistel_round_keys`) uses no S-box,
no `RotWord`/`SubWord`, and no RCON table.** It seeds a `splitmix64` PRNG
state from the two 64-bit halves of the master key
(`k0 XOR (k1 * 0x2545F4914F6CDD1D) XOR 0xD1B54A32D192ED03`) and draws 16
round subkeys by iterating `splitmix64`. `splitmix64` is the harness's own
general-purpose PRNG (Vigna's public-domain construction, already used
throughout this campaign for plaintext generation, key derivation from arm
seeds, and thread seeding in `rc8probe.c` itself) — not part of AES's
definition, and reused here exactly as the task card permitted for harness
machinery, not smuggled in as the oracle's cryptographic structure. The
oracle's actual mixing structure is the Feistel network plus `feistel_F`,
§2 below.

## 2. `rc8probe_feistel.c`'s actual construction

- **Structure:** balanced Feistel network, two 64-bit halves, 16 rounds:
  `for i in 0..15: (L,R) <- (R, L XOR F(R, RK[i]))`.
- **Round function** `feistel_F(x,k)`:
  ```c
  v = x + k;
  v ^= v >> 33;
  v *= 0xff51afd7ed558ccdULL;
  v ^= v >> 33;
  v *= 0xc4ceb9fe1a85ec53ULL;
  v ^= v >> 33;
  v += k;
  ```
  (64-bit addition mod 2^64, right xor-shift by 33, 64-bit multiplication mod
  2^64 by two odd constants, repeated.) This is the public-domain murmur3
  `fmix64` avalanche finalizer with the input keyed by addition before and
  after — a widely-used, independently-documented integer-hash construction,
  not derived from or resembling any AES round-function step.
- **Determinism:** round subkeys `RK[0..15]` are computed once
  (`feistel_round_keys`, called once per process invocation before any
  trial) and never touched again. `feistel_encrypt`/`feistel_decrypt` are
  pure functions of `(RK[], input)` with no internal state and no RNG calls.
  Mechanically verified by `rc8probe_feistel detcheck` (`runs/detcheck.json`):
  the SAME key encrypting the SAME input twice gives the SAME output
  (`same_key_same_input_same_output: true`), decryption exactly inverts
  encryption (`decrypt_inverts_encrypt: true`), and re-deriving the round-key
  schedule from the same key a second time reproduces it exactly
  (`round_key_schedule_reproducible: true`).
- **Memory:** O(1) per query — two 64-bit local variables plus the fixed
  128-byte `RK[16]` table shared across all queries. No stored input/output
  pair table of any kind.

Excerpt (see `src/rc8probe_feistel.c` for the full, buildable file):

```c
static inline uint64_t feistel_F(uint64_t x, uint64_t k){
    uint64_t v = x + k;
    v ^= v >> 33;
    v *= 0xff51afd7ed558ccdULL;
    v ^= v >> 33;
    v *= 0xc4ceb9fe1a85ec53ULL;
    v ^= v >> 33;
    v += k;
    return v;
}
static void feistel_round_keys(const uint8_t key[16]){
    uint64_t k0 = 0, k1 = 0;
    for(int i = 0; i < 8; i++) k0 |= (uint64_t)key[i]     << (8*i);
    for(int i = 0; i < 8; i++) k1 |= (uint64_t)key[8 + i] << (8*i);
    uint64_t st = k0 ^ (k1 * 0x2545F4914F6CDD1DULL) ^ 0xD1B54A32D192ED03ULL;
    for(int i = 0; i < FEISTEL_ROUNDS; i++) RK[i] = sm64(&st);
    RK_ready = 1;
}
static void feistel_encrypt(const uint8_t in[16], uint8_t out[16]){
    uint64_t L = 0, R = 0;
    for(int i = 0; i < 8; i++) L |= (uint64_t)in[i]     << (8*i);
    for(int i = 0; i < 8; i++) R |= (uint64_t)in[8 + i] << (8*i);
    for(int i = 0; i < FEISTEL_ROUNDS; i++){
        uint64_t nL = R;
        uint64_t nR = L ^ feistel_F(R, RK[i]);
        L = nL; R = nR;
    }
    for(int i = 0; i < 8; i++) out[i]     = (uint8_t)(L >> (8*i));
    for(int i = 0; i < 8; i++) out[8 + i] = (uint8_t)(R >> (8*i));
}
/* THIS IS DETERMINISTIC, NOT RESAMPLED PER TRIAL: RK[] is computed once by
 * feistel_round_keys(key) in main() before the trial loop starts (called
 * exactly once per process invocation, right after key derivation and
 * before spawning worker threads), and every worker thread's every trial
 * calls feistel_encrypt/feistel_decrypt against the SAME fixed RK[]. */
```

## 3. Independence from the `yoyo_sbox_v2`/`v3`/`v4` lineage and from `perm128`

- `rc8probe_feistel.c` does not `#include` or link against any file from
  `BATCH-004/006/008/009` (`yoyo_sbox.c`, `yoyo_sbox_v2.c`, `yoyo_sbox_v3.c`,
  `yoyo_sbox_v4.c`) or from `BATCH-011/012` (`rc8probe_ideal.c`,
  `rc8probe_ideal_old.c`, `rc8probe_pfx.c`). It is a single self-contained
  `.c` file with no oracle-related dependency on any of them.
- It contains no injectivity-rejection sampling, no persistent hash table,
  no `dom[]`/`rng[]` pair-storage arrays, no `idx_cap`/load-factor logic —
  the entire `perm128` architecture (EV-AES-837cd8) is absent, by design:
  the task card required an O(1)-memory-per-query construction, which a
  stored-pair ideal-permutation table structurally cannot be.
- It contains no RC-10/prefix-counter fields from `yoyo_sbox_v4`'s
  `W_ge1_prefix_k` machinery (this task's harness reports only the plain
  `W_ge1_nontrivial`/`whist` fields, matching `rc8probe.c`'s own v1 report
  shape, not v4's extended one).

## 4. Grep-verified zero shared oracle vocabulary

Commands actually run and their exact output are archived verbatim in
`runs/grep_independence.txt`. Summary of that run:

- `grep -n "GLOG\|GEXP\|gmul\|ginv\|SBOX\|MixColumns\|mix_columns\|ShiftRows\|shift_rows\|RCON\|key_expand\|0x1b\b" src/rc8probe_feistel.c`
  matched **only inside `rc8probe_feistel.c`'s own `/* ... */` header comments**
  (the provenance disclosure and the "NOT AES's ... ShiftRows" design-intent
  lines quoted in this audit) — zero matches in compiled code (any C
  identifier, table, or executable statement). `exit=0` because grep found
  matches, all of them in comment text, none in code.
- `grep -n "feistel\|Feistel\|fmix64\|0xff51afd7ed558ccd\|0xc4ceb9fe1a85ec53"`
  against `rc8probe.c` (BATCH-007), `yoyo_sbox_v4.c` (BATCH-009),
  `rc8probe_ideal.c` (BATCH-011), and `rc8probe_ideal.c` (BATCH-012):
  **zero matches**, `exit=1` (grep's "no match" exit code). None of those
  four files contains the Feistel construction, the murmur3-finalizer
  constants, or the word "feistel"/"Feistel" anywhere.

## 5. Summary

No table, matrix, permutation, or code path in `rc8probe_feistel.c`'s oracle
(`feistel_F`, `feistel_round_keys`, `feistel_encrypt`, `feistel_decrypt`)
appears in AES's S-box, MixColumns matrix, ShiftRows permutation, or key
schedule as implemented in `rc8probe.c`, nor in the `yoyo_sbox_v2-v4`
lineage, nor in rc8probe's own `perm128` ideal-permutation code. The
construction is a keyed, deterministic, fixed-round Feistel PRP verified by
mechanical self-check (§2, `runs/detcheck.json`) to be reproducible
(same key + input -> same output, every call) rather than resampled.
