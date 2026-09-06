# INDEPENDENCE AUDIT — `rc8probe_freshfeistel.c` (TASK-20260805-d408ac)

Side-by-side audit of the SUBSTITUTE ORACLE (fresh-key-per-trial 16-round
Feistel, SipRound round function) against (1) AES's actual round-function
operations, and (2) every prior instrument in this campaign: the
`yoyo_sbox_v2`/`v3`/`v4` lineage (BATCH-004/006/008/009), rc8probe's
`perm128` ideal-permutation code (BATCH-011/012 `rc8probe_ideal.c`), and
BATCH-014's `rc8probe_feistel.c` (RC-D). Bar to meet, per the task card: the
same standard BATCH-011 and BATCH-014 met (zero shared oracle vocabulary,
grep-verified), PLUS independence from AES's actual operations, PLUS no
verbatim reuse of RC-D's round-function code.

**Audit boundary, stated first:** this source file DELIBERATELY CONTAINS AES
code — the comparison's LIVE side is 5-round AES itself, run as a matched arm
by this same instrument (lines 79-261, copied byte-for-byte from rc8probe.c,
disclosed in the header). The audited claim is narrower and is about the
substitute oracle only: the oracle zone (lines 262-330), the worker's
fresh-feistel branch (lines 406-420), the per-trial key machinery
(338-349), and the oracle gates (486-584) share no table, constant,
permutation, or code path with AES's S-box/MixColumns/ShiftRows/key schedule,
and none with any prior campaign oracle.

## 1. AES's actual operations (what the oracle does NOT use)

### 1.1 AES S-box (`SBOX`/`ISBOX`, file lines 105-121, live-arm zone)

Built by `build_aes_sbox` as multiplicative inverse in GF(2^8) (reduction
polynomial x^8+x^4+x^3+x+1, the `0x1b` constant in `gf_init`) followed by
the FIPS-197 affine map.

**The oracle zone contains no S-box array, no byte-substitution step, no
GF(2^8) log/antilog tables (`GLOG`/`GEXP`), no `gmul`/`ginv`, and no `0x1b`
reduction constant.** Grep G1 (runs/grep_independence.txt): zero
AES-vocabulary matches in lines 262-584 (exit 1). The oracle's round
function operates on 64-bit words with addition mod 2^64, rotation, and xor
— arithmetic with no field structure at all.

### 1.2 AES MixColumns (M2/M3/M9/MB/MD/ME tables, lines 127-196, live-arm zone)

The fixed GF(2^8) column matrix (02 03 01 01 / ...) and its inverse.

**The oracle zone contains no MixColumns step, no GF(2^8) multiply tables,
and none of the 02/03/09/0b/0d/0e constants.** The oracle contains NO
multiplication in its round function at all (SipRound is pure add/rotl/xor),
which separates it from MixColumns by operation type as well as by
constants.

### 1.3 AES ShiftRows (lines 162-175, live-arm zone)

`out[4c+r] = in[4*((c+r)&3)+r]` — a row-wise byte rotation of the 4x4 state.

**The oracle zone contains no byte-array state and no byte permutation.**
Its only word movement is 64-bit rotation inside SipRound (`rotl64` on a
single 64-bit integer), structurally unrelated to a 16-byte row rotation
(different operand, width, and operation). The `PW`/`CW` probe-geometry
arrays (lines 331-337) ARE copied from rc8probe.c — disclosed: they are the
MEASUREMENT harness's diagonal probe masks, held fixed across arms by
design, not part of the oracle.

### 1.4 AES key schedule (`key_expand`, lines 133-149, live-arm zone)

Word-oriented Rijndael expansion with RotWord/SubWord/RCON.

**The oracle's per-trial key derivation (`ff_trial_subkeys`, lines 300-303)
uses no S-box lookup, no RotWord/SubWord, no RCON table**: it initializes a
splitmix64 state from the trial's two 64-bit key words
(`k0 ^ rotl64(k1,27) ^ 0x6A09E667F3BCC908`) and draws 16 subkeys by
iterating splitmix64 — the campaign's harness PRNG, exactly as BATCH-014's
audit accepted for harness machinery, with a different mixing constant than
RC-D's.

## 2. The oracle's actual construction

- **Structure:** balanced Feistel, two 64-bit halves, 16 rounds, per-trial
  subkeys passed on the stack (NO file-scope key array — grep G10 shows no
  `static ... RK`; contrast RC-D's global `RK[FEISTEL_ROUNDS]`).
- **Round function `ff_F(x,k)` (lines 289-298):** SipHash-style state
  initialization from (x,k) with SipHash-2-4's public IV constants, TWO
  SipRounds (lines 278-283: 4 additions mod 2^64, 5 rotations, 4 xors per
  round — no multiplication), final four-word xor. Structurally distinct
  from both AES's round function (§1) and RC-D's murmur3-fmix64 mix
  (multiply/xor-shift; different operations AND different constants).
- **Freshness (the OPPOSITE of RC-D's defining property):** RC-D derived
  `RK[]` ONCE in `main()` from a fixed key and read it from a global in
  every trial (verified deterministic, EV-AES-dec938 OBS-B14-2). Here, each
  trial draws `k0,k1` from a dedicated per-thread key stream, derives RK on
  its own stack frame, and no key material persists across trials. Verified
  mechanically (runs/SELFCHECK.json keycheck: 4,194,304 keys, 0 duplicates)
  and logged per arm (first 4 trial keys + key-stream digest in each arm's
  JSON).
- **Memory:** O(1) per query — two 64-bit halves, one 128-byte stack RK, no
  stored pairs (contrast perm128's 32-byte-per-pair dom/rng storage,
  EV-AES-837cd8 OBS-B12-5).

## 3. Independence from prior campaign instruments

### 3.1 `yoyo_sbox_v2`/`v3`/`v4` lineage

- No `#include` of any lineage file; single self-contained .c.
- Zero lineage oracle vocabulary in this file (grep G8, exit 1): no
  `idealperm`, `seed_cipher`, `ideal_redraws`, `c0o`/`c1o`, `pdigest`,
  `wgek` — v4's ideal-branch and RC-10 prefix-counter machinery is absent.
- ONE v4 code fragment was copied, and is disclosed in the source header and
  here: the order-sensitive FNV-1a 64-bit digest over 8-byte words of the
  (p0,p1) plaintext stream (grep G9 shows the matching lines in both
  files). This is MEASUREMENT BOOKKEEPING, not oracle code: it reads only
  the harness-generated plaintexts, draws no randomness, and touches no
  cipher path. It was copied deliberately so this task can VERIFY
  byte-identical plaintext generation against BATCH-009's recorded digests
  by equality — closing the V3 gap BATCH-014 disclosed (its byte-wise FNV
  variant was a different formula and could not be compared). Verified:
  runs/L1-AES-R5-P30.json and runs/M1-FF-P30.json reproduce BATCH-009's
  recorded digests `de8dee29c9310a13`/`01089d650f48ca1b` exactly.

### 3.2 `perm128` (`rc8probe_ideal.c`, BATCH-011/012)

- Zero perm128 architecture in this file (grep G5): no `dom[]`/`rng[]`
  pair-storage arrays, no `idx_cap`/load-factor logic, no `max_pairs`, no
  lazy-sampling/injectivity-rejection code. The only `perm128` and
  `injectivity` string matches are disclosure comments and the ff_gate's
  2-point injectivity LABEL (a correctness check on the Feistel bijection,
  architecturally nothing like perm128's exact-injectivity hash table).
- The constructions are also SEMANTICALLY opposite in memory behavior:
  perm128 stores every realized pair (O(4N) memory — the ceiling this batch
  exists to escape); this oracle stores nothing.

### 3.3 `rc8probe_feistel.c` (BATCH-014, RC-D)

- Zero RC-D oracle code (grep G6): the only matches for
  `feistel_F`/`feistel_round_keys`/`feistel_encrypt`/`feistel_decrypt`/
  `FEISTEL_ROUNDS` are inside the header's NOT-reused disclosure comment.
  The round function is NOT reused verbatim (contract requirement): RC-D's
  is the murmur3-fmix64 multiply/xor-shift mix; this task's is the
  SipRound add/rotate/xor mix — different operations, different constants,
  different keying (per-trial vs once-per-process).
- **One cosmetic grep hit, disclosed plainly (grep G3):** the murmur3
  constant `0xff51afd7ed558ccd` appears at line 535 inside `keycheck()` —
  the selfcheck's hash-set PLACEMENT function for the key-distinctness
  table. It is tooling for a duplicate lookup, not oracle code: it affects
  only which bucket a key starts probing at; duplicate detection itself is
  exact byte comparison; it is never called from any worker, gate, or
  oracle path. Recorded here so an auditor grepping for RC-D constants
  finds the explanation before forming a suspicion.
- Reverse direction (grep G7): no prior instrument contains any of this
  file's oracle symbols (`ff_F`, `ff_encrypt`, `ff_decrypt`,
  `ff_trial_subkeys`, `key_thread_seed`, `KEYARM_C1`, `freshfeistel`,
  `sipround`) — zero matches in all five prior files.

## 4. Grep-verified zero shared oracle vocabulary

Commands and their exact output are archived verbatim in
`runs/grep_independence.txt` (G1-G10), run against the actual committed
paths of rc8probe.c (BATCH-007), yoyo_sbox_v4.c (BATCH-009), both
rc8probe_ideal.c files (BATCH-011/012), and rc8probe_feistel.c (BATCH-014).
Summary:

- G1: AES vocabulary inside the oracle+worker+gates zone (lines 262-584):
  **zero matches, exit 1.**
- G2: every AES-vocabulary match in the whole file maps to the live-arm
  zone (79-261), its header disclosure (30-33), live-arm JSON reporting
  guarded by `oracle == 0` (635), or live-arm key setup (764, 825). None in
  the oracle.
- G4: SipRound/SipHash vocabulary in all five prior instruments: **zero.**
- G7: this file's oracle vocabulary in all five prior instruments: **zero.**
- G8: v4 oracle/ideal-branch vocabulary in this file: **zero, exit 1.**
- G10: no file-scope key array; RK is a per-trial stack local (freshness),
  opposite of RC-D's global fixed RK[].

## 5. Summary

No table, matrix, permutation, constant, or code path in the substitute
oracle (`sipround`, `ff_F`, `ff_trial_subkeys`, `ff_encrypt`, `ff_decrypt`,
the per-trial key draw, and the worker's fresh-feistel branch) appears in
AES's S-box, MixColumns, ShiftRows, or key schedule as implemented in the
same file's live-arm section or in rc8probe.c; nor in the yoyo_sbox_v2-v4
lineage (barring the disclosed plaintext-digest bookkeeping fragment); nor
in perm128; nor in RC-D's oracle (barring the disclosed keycheck set-hash
constant). The construction is keyed, fresh-per-trial, O(1)-memory, and its
freshness — the exact opposite of RC-D's verified determinism — is
demonstrated mechanically (keycheck, per-arm key logs), not asserted.
