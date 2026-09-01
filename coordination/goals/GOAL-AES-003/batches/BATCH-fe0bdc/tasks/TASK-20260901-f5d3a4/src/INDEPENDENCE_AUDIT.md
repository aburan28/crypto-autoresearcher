# INDEPENDENCE_AUDIT.md — TASK-20260901-f5d3a4

Convention-drift controls mandated by IDEA-20260901-04606c `confounders` ("KAT pins on the
probe binary ... and a mandated source-level port audit — the executor must record the diff of
its round functions against the campaign build") and by the task card.

## 1. KAT pins (external anchor on the round functions)

`affarm046 pin 46060901` (runs/pin.json) under the AES table:

- FIPS-197 C.1 KAT encrypt r=10 match: TRUE (69c4e0d86a7b0430d8cdb78070b4c55a)
- FIPS-197 C.1 KAT decrypt r=10 match: TRUE
- BATCH-003 anchor r=5 ciphertext match (key 2b7e...4f3c): TRUE (4167e8f8367c38cdb7bde2ade620a7a8)
- BATCH-003 anchor r=10 ciphertext match: TRUE (8df4e9aac5c7573a27d8d055d6e4d64b)
- r=5 anchor decrypts back to plaintext: TRUE
- 512 random (key, plaintext) roundtrips r=1..10: 0 failures
- pin_pass: TRUE

These constants are EXTERNAL to the affine census (they come from FIPS-197 and the committed
BATCH-003 cross-instrument anchor), so a self-consistent-but-unpinned convention drift — the
confounder the record says Gate 0 and the census CANNOT catch — fails the KAT pin even though
it passes every algebraic check. The identity arm uses the same enc_r/dec_r/mix/inv-mix/
sub_shift/inv_sub_shift/key_expand code paths the KAT pins; the only table difference is
SBOX[i]=i, verified by `pinidentity` (runs/pinidentity.json: bijective TRUE, 0 roundtrip
failures, pin_pass TRUE) and by table hex in every arm receipt.

## 2. Source-diff audit of the round functions vs the campaign build

Full unified diff recorded in `runs/source_diff.txt` (539 lines;
`diff -u BATCH-b41ba9/tasks/TASK-20260806-47f217/probe_sbox.c src/affarm046.c`).

Kept EXPRESSION-IDENTICAL to probe_sbox.c (exact-port discipline of algebra_rank.py):

| function | status |
|---|---|
| sm64 (splitmix64) | identical |
| xt / gmul / XT2/XT4/XT8 tables | identical |
| build_sbox (AES inverse + affine map) | identical (KAT pins only) |
| build_inv_sbox | identical |
| key_expand (FIPS-197, global-SBOX SubWord) | identical (line 128 here = line 153 there) |
| add_rk / sub_shift / inv_sub_shift | identical |
| mix_columns / inv_mix_columns (xt formulas) | identical |
| enc_r / dec_r round order | identical |
| build_geom (PW/CW formulas) | identical |
| worker trial logic (p0 draw, active-word re-randomisation with zero-word-diff rejection, CW swap with trivial detection, Z/W counters, thread seed formula, trial partition) | identical |

Deltas (all in the audit-relevant direction):

- REMOVED: set_random_sbox, pinsbox mode, SBOX_LABEL random labeling, the arm's aes/random
  sbox selector (zero grep matches, runs/grep_audit.txt). The arm surface accepts the token
  `identity` ONLY and refuses anything else (line 408) — the oracle cannot measure a
  nonlinear cipher, which is the record's affine scope.
- ADDED: identity_tables_ok() startup check; arm token guard; pinidentity simplified to the
  identity-specific pins; header lineage and inference documentation.
- CHANGED (output only, not round functions): pin mode omits probe_sbox.c's
  round_ciphertexts_of_kat_block list printing; pinidentity omits inv_sbox hex printing.
  No semantic change.

Semantic equivalence beyond the textual diff is established three ways: (1) the KAT pins of
section 1; (2) the exact Python replication of a full 2^16 one-thread arm stream
(runs/cal_crosscheck.json vs runs/cal_det_a.json): key_hex, thread seed, and EVERY counter
(trivial, nontrivial, wge1, wword, whist, zhist) match exactly between the fresh C worker and
fresh Python trial code that itself satisfies Gate 0's 1000 keyed trials; (3) determinism
double-runs byte-identical at 1 thread (2^16) and 8 threads (2^18).

## 3. Census / gate / bridge code path (Python): NO cipher round content

gate0.py, census046.py, bridge.py compute under SBOX = id by construction:

- census046.py: no S-box table, no key schedule, no KAT constants, no RNG — pure GF(2)
  column matrices (SR/ISR permutations, MC/IMC byte-linear blocks), cross-checked inside the
  file against the harness byte-level xt/XT2/XT4/XT8 formulas on an exhaustive byte sample.
  Independence from gate0.py: gate0.py builds M_5/D_5 by byte-level basis-vector simulation
  of the round functions (the algebra_rank.py method class); census046.py builds all M_r/D_r
  by explicit matrix products. The two share no code; agreement at the anchor (both reproduce
  ranks 32,0,0,0 and the flat law) is a cross-check.
- gate0.py / bridge.py: identity-S-box key schedule (FIPS-197 expansion, SubWord = identity
  rotation) and byte-level round functions re-derived fresh for this task; used only for the
  keyed trial streams, never for the census.

## 4. What independence is NOT claimed here

- The affine oracle deliberately shares pinned instrument semantics with the campaign probe
  lineage (section 2); instrument independence is not claimed and is not the audit object.
  The cross-lineage re-measurement (IDEA-20260901-02f7c4 arm B3) remains the named full
  mitigation and is NOT discharged here (record confounders).
- Shared-harness bugs conditional on the round function (BATCH-010 red team's residual risk
  class) are not ruled out by any affine arm alone; stated, not discharged (record confounders).
- Harness PATTERN lineage for arm-run conventions (JSON receipts to stdout, /usr/bin/time -l
  timing files, .err capture, calibration-before-frozen-arm, seed/armid/thread determinism
  documentation): BATCH-014 TASK-20260805-b95720/src/rc8probe_feistel.c and BATCH-015
  TASK-20260805-d408ac/src/rc8probe_freshfeistel.c per the task card. No cipher code was
  taken from the Feistel harnesses (different cipher family; not applicable to the SPN
  affine oracle).

## 5. Grep-level attestations

Recorded with commands and outputs in runs/grep_audit.txt:

- `grep -n 'set_random_sbox\|pinsbox' src/affarm046.c` — zero matches (exit 1).
- identity table construction present exactly once; arm token guard at src/affarm046.c:408.

## Inference block

policy: executor-implementation; requested_policy: executor-implementation;
resolved_model_id: fireworks-ai/accounts/fireworks/models/qwen3p8-max (ACTUAL session model);
model_verified: false; fallback_used: true (session-backend transport under inference
amendment DEC-20260831-0d1eeb); degraded_requirements: []; amendment: DEC-20260831-0d1eeb;
standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c.
