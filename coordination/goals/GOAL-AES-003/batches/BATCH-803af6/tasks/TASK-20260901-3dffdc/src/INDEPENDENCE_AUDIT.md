# INDEPENDENCE_AUDIT.md — TASK-20260901-3dffdc

## 1. Census path (src/census.py): NO AES ROUND CONTENT

The census computes T_{r,S} = M_r^{-1} Z_{CW[S]} M_r as exact GF(2) linear algebra.
Content audit of `census.py`:

- S-box table: ABSENT. No 256-byte substitution table, no S-box construction, no
  inverse-S-box, no SubBytes anywhere. The census is the SBOX=id limit by construction.
- Key schedule / round keys: ABSENT. AddRoundKey drops out on differences (record
  `object`); no key bytes, no rcon, no key expansion in the file.
- KAT vectors: ABSENT. No FIPS-197 known-answer constants.
- RNG: ABSENT. No randomness anywhere; the census is a deterministic exact computation.

What IS present, and why it is probe geometry rather than round content:

- ShiftRows geometry: the pinned PW/CW diagonal tables
  (PW[j][row]=4*((j+row)%4)+row, CW[j][row]=4*((j-row)%4)+row) and the SR/ISR byte
  permutations. These are the PROBE's word/swap geometry (BATCH-002 pinned convention;
  values taken from BATCH-b41ba9 TASK-20260806-47f217 `geom.json`, cross-equal to the
  formulas in `probe_sbox.c` build_geom). The census is a statement ABOUT this geometry;
  it cannot be computed without it.
- MixColumns column map {2,3,1,1} (and inverse {14,11,13,9}) over GF(2^8) with the
  pinned reduction polynomial (xtime with 0x1b). This is the LINEAR layer the census
  measures; it contains no substitution content. Both maps are cross-checked inside
  census.py against the harness's byte-level xt/XT2/XT4/XT8 formulas on an exhaustive
  byte sample (checks `MC_harness_formula`, `IMC_harness_formula`) and against
  MC.IMC = I_128.

## 2. Independence of the anchor recomputation (record baseline_embedding)

The record requires the anchor rank quadruple "recomputed independently of the census
code". Two disjoint construction paths are used:

- `census.py`: explicit 128x128 GF(2) matrices for SR and MC built on bit basis
  vectors, M_r by matrix product SR.(MC.SR)^{r-1}, inverse by Gauss-Jordan on rows.
- `anchor_check.py` (RUN 1): byte-level simulation of the pinned round functions
  (sub_shift/mix_columns/inv_sub_shift/inv_mix_columns with identity S-box, the method
  class of the archived algebra_rank.py, re-derived fresh) applied to basis vectors to
  obtain the columns of M_5 and D_5; the inverse is ALSO obtained independently by
  Gauss-Jordan on the column representation and checked equal to D_5.
- The two files share no code and no imports. anchor_check.py runs FIRST and is
  blocking: if its F1 gate fails, the census does not run (HALT per F1).
- anchor_check.py additionally recomputes the ARCHIVED object P_j (D.M) P_0^T and
  verifies D.M = I_128, reproducing the archived Validator's check (EV-AES-048545 O-7).

## 3. Affine oracle (src/affprobe.c): HARNESS-ONLY REUSE, DISCLOSED

`affprobe.c` is an adaptation of the campaign probe lineage, used because the arms must
measure the SAME pinned instrument (a fresh-from-nothing trial implementation would risk
measuring a different instrument, which is exactly the convention-mismatch confounder
the record names). Reuse itemized, with sources:

KEPT IDENTICAL (instrument semantics):
- splitmix64 RNG — from `BATCH-b41ba9/tasks/TASK-20260806-47f217/probe_sbox.c`
  (lineage: BATCH-713991 TASK-20260804-f5e58b probe.c).
- Trial worker logic: p0 draw, active-word re-randomisation with zero-word-diff
  rejection, enc/enc, CW-word ciphertext swap with trivial-swap detection, dec/dec,
  Z/W counters over all four PW words — verbatim from probe_sbox.c `worker`.
- Round functions enc_r/dec_r and their round order (pinned cipher convention;
  probe_sbox.c, BATCH-002 preregistration section 1).
- PW/CW geometry (probe_sbox.c build_geom / geom.json).
- Per-thread seed formula and trial partitioning (probe_sbox.c main).
- Arm JSON schema fields (probe_sbox.c arm output).
- MixColumns xtime/XT2/XT4/XT8 byte tables (S-box-independent linear-layer constants).

REMOVED (no AES content in the affine oracle):
- build_sbox (AES table from GF(2^8) inverse + affine map) and set_aes_sbox — REMOVED.
- set_random_sbox (Fisher-Yates random bijective tables) — REMOVED.
- gmul helper (used only by the AES table build) — REMOVED.
- `pin` mode (FIPS-197 C.1 KAT, BATCH-003 anchor ciphertexts) — REMOVED.
- `pinsbox` mode — REMOVED.
- The SBOX/INV_SBOX arrays are identity-only, verified at startup (identity_tables_ok).

KEY SCHEDULE: kept in FIPS-197 expansion shape with SubWord = identity rotation
(key_expand_identity), which is exactly what probe_sbox.c computes under SBOX[i]=i.
It is linear and drops out of differences, but keeping it makes ABSOLUTE ciphertext
values bit-identical to the pinned instrument, so trivial-swap detection (an
absolute-value test) matches. It consults no substitution table.

Lineage reading for harness PATTERN (per task card): BATCH-014
TASK-20260805-b95720/src/rc8probe_feistel.c and BATCH-015
TASK-20260805-d408ac/src/rc8probe_freshfeistel.c + RESULTS.json were read for the
campaign's arm-run conventions (JSON-to-stdout arm receipts, /usr/bin/time -l timing
files, .err capture, calibration-before-frozen-arm practice, seed/armid/thread
determinism documentation, run-count accounting). No cipher code was taken from the
Feistel harnesses (different cipher family; not applicable to the SPN affine oracle).

## 4. Statistics (src/analysis.py): frozen-comparator convention reuse

Garwood Poisson CI and exact conditional-binomial machinery ported from BATCH-015
TASK-20260805-d408ac/src/analysis.py (campaign frozen comparator; its own lineage
cited there). Verified inside analysis.py against the published figures before any
new statistic: garwood(1,1)=[0.025,5.572], garwood(6,8)=[0.275,1.632], 14-vs-1 exact
test p=9.765625e-4 (EV-AES-e4c091). This is statistical convention, not cipher content.

## 5. Grep-level attestations

- `grep -in sbox src/census.py` — no AES S-box construction; the only occurrences are
  the documented "SBOX = id" convention comments. (Command and output recorded in
  runs/grep_independence.txt.)
- `grep -n "build_sbox\|set_aes_sbox\|set_random_sbox\|gmul\|kat_ct\|fips197" src/affprobe.c`
  — zero matches: AES construction paths absent from the affine oracle.

## 6. What independence is NOT claimed here

- The affine oracle deliberately shares instrument semantics with the pinned probe
  lineage (section 3); independence of the INSTRUMENT is not claimed and is not the
  object of this audit. Independence of the census computation (section 2) and absence
  of AES round content in the census path (section 1) are the audited properties.
- Shared-harness bugs conditional on the round function (BATCH-010 red team's residual
  risk class, record `confounders`) are NOT discharged by this task; the record assigns
  that mitigation to IDEA-20260901-02f7c4 arm B3.
