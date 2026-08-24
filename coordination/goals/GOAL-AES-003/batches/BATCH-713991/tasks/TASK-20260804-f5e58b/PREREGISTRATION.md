# PREREGISTRATION — True-Hint Positive Control (Rank 2, BATCH-713991)

Written BEFORE any measurement in this task (frozen at task start, 2026-08-06T03:11:27Z).

## Task
TASK-20260804-f5e58b, batch BATCH-713991, goal GOAL-AES-003. Executor role, part 1 of 2.

## Question
The campaign's hint-corruption instrument `sq_slot` (modified `sq_null`) was run in
BATCH-003 with FALSE hints only, returning survivor sets {0:4} (all diagonals empty).
No positive control exists proving the instrument can return a NON-EMPTY result.
This task supplies that control with ONE true-hint arm.

## Frozen prediction (H1, pre-registered)
The true-hint arm is **predicted to return {1:4}** — i.e., per diagonal, a
**non-empty** survivor set that **contains the correct key byte**. Rationale: with
the hint correct on every slot, the surviving candidates should concentrate on the
true byte; the {0:4} result in BATCH-003 is attributed to the false hints, not to an
instrument defect.

## Null / falsification
- If the true-hint arm returns **empty survivor sets on all diagonals ({0:4})**,
  the positive control FAILS: an instrument that returns empty even on a true hint
  cannot support the rank-4 conclusion that false hints cause {0:4}. That conclusion
  is then UNSUPPORTED by this instrument.

## Method (frozen)
- Source: byte-identical copy of
  `BATCH-003/tasks/TASK-20260802-447db8/src/sq_slot.c` — no edits.
- Compile: C, AES-NI, -O2, flags per source header.
- Run: one arm, same mode/key/hintkey/rounds/nstruct/seed as BATCH-003 rank-4 arms,
  but argv[8] (slotmask) = 0 -> NO false slots -> ALL hints true:
  `./sq_slot attack6n 2b7e151628aed2a6abf7158809cf4f3c 53787ef6b300ea19f0a43d4915afd440 6 2 90009 1 0 mask`
- Arity per source: argv[1]=mode, argv[2]=key, argv[3]=hintkey, argv[4]=rounds,
  argv[5]=nstruct, argv[6]=seed, argv[7]=nthreads, argv[8]=nwrong/slotmask, argv[9]="mask".
- Capture stdout+stderr to files; parse JSON; compare with BATCH-003 false-hint
  RESULTS.json ({0:4} per diagonal).
- Run UNCONTENDED (taskset -c 0), toy tier only.

## Tier / scope
TOY TIER. No claims about full-round or deployed AES. This is an instrument
validity control, not an attack result.

## Inference block
policy: executor-implementation; requested_policy: executor-implementation;
resolved_model: deepseek-v4-flash-free; fallback_used: false; model_verified: false
(no adapter probe); standing basis commit 0137a051eb5828789eb267fa83c8278086578d4c.

## Budget
2400 s wall clock, 8 GB, max 25 runs (1 run planned).

---

# PREREGISTRATION — RANK 3 S-BOX ARM (same task TASK-20260804-f5e58b, BATCH-713991)

Written BEFORE any cipher call or measurement of the RANK 3 session: source
`probe_sbox.c` written and compiled (clang -O2 -pthread, no warnings) at
2026-08-06T03:42–03:46Z; this section frozen at 2026-08-06T03:47Z; the first
cipher run happens after this text. Timeline is honest: the RANK 3 session
started 03:42:49Z, was interrupted by a session end before any measurement,
resumed 03:46:36Z. Because no measurement existed before this text, this is a
genuine pre-registration, not a late capture.

## Question (the campaign's last untested specificity)

The r=5 yoyo excess (15.63x over the analytic null in BATCH-002,
TASK-20260802-e4fa63, arm A1: amask=1, smask=1, rounds=5, N=2^33, seed
424242001) is the ONLY campaign result whose S-box dependence has never been
measured. The r=4/r=5 counting properties are already known NOT to be
S-box-specific (random bijective S-boxes reproduce them). This arm decides
whether ANYTHING in the campaign is specific to the AES S-box.

## Instrument (frozen)

`probe_sbox.c`: fully software AES-shaped SPN (4x4 byte state, AddRoundKey,
SubBytes(256-entry table), ShiftRows, real AES MixColumns over GF(2^8) poly
0x11b, final round without MixColumns), ported line-for-line from BATCH-002
probe.c's worker/geometry/RNG/schedule, with AES-NI enc/dec replaced by
software byte rounds and a global replaceable SBOX[].

- Geometry: PW[j]={4*((j+row)%4)+row}, CW[j]={4*((j-row)%4)+row} (inverse-
  ShiftRows diagonals — the geometry a prior replication got wrong).
- Trial: p0 uniform; p1=p0 with bytes of words in amask re-randomised
  (zero word-diff rejected); c0=enc_r(p0), c1=enc_r(p1); swap ciphertext
  bytes of words in smask between c0,c1; q0=dec_r(c0), q1=dec_r(c1);
  d=q0^q1; Z=#zero-diff bytes; W=#words (over PW, all 4) with all-zero
  diff bytes; trivial-swap guard (c0==c1 on all swapped bytes) excludes
  and counts the trial.
- Null: per-trial P(W>=1) = 4*2^-32 = 2^-30 (Binomial(4,2^-32) under a
  random permutation; BATCH-002 sec.3). Excess factor = W_ge1 /
  (nontrivial_trials * 2^-30).

## S-boxes (frozen)

- AES: build_sbox() = GF(2^8) inverse + FIPS-197 affine map (probe.c's exact
  function); full table recorded.
- Random #1, #2: Fisher-Yates over bytes 0..255 with splitmix64 (probe.c
  sm64), seeds **SBOX1_SEED=424242201**, **SBOX2_SEED=424242202** (recorded);
  bijectivity verified (inverse maps back) in C and independently recomputed
  in Python; modulo bias of `r mod (i+1)` documented (~2^-64 scale).

## Pins (frozen, all REQUIRED)

1. AES S-box: FIPS-197 C.1 KAT at r=10 (key 000102..0f, pt 0011..ff ->
   ct 69c4e0d86a7b0430d8cdb78070b4c55a) and at r=5 ->
   4167e8f8367c38cdb7bde2ade620a7a8 (the value BATCH-003's cross-instrument
   pin exposed; also re-anchored by this task's RANK 2 selftest); dec of the
   r=5 anchor restores the KAT plaintext; 5120/5120 enc/dec roundtrips over
   r=1..10 on 512 random (key,plaintext) vectors, zero failures.
2. Random S-boxes: (a) table recomputed deterministically from the seed —
   pinsbox run twice + independent Python recomputation; (b) self-consistency
   invariant — bijectivity, INV_SBOX exact inverse; (c) encrypt the known
   KAT block under the KAT key and decrypt back to the plaintext at r=1
   (also r=5, r=10).

## Arms (frozen; N=2^32 per arm)

BATCH-002's yoyo configuration is rounds=5, amask=1, smask=1. BATCH-002 A1
used N=2^33; A1b used N=2^32 and read 60 hits / 15.0x. This session fixes
N=2^32 for every arm so the three S-boxes and both controls are compared at
identical power inside the 2400 s budget (null expectation 4.0, resolution
log2(2^32/3) = 30.4 bits covers 2^-30; 2^32 is BATCH-002's own A1b power).

| Arm | S-box | rounds | amask | smask | N | master seed | arm_id |
|-----|-------|--------|-------|-------|-----|-------------|--------|
| R3-A1 | AES | 5 | 1 | 1 | 2^32 | 424242101 | 101 |
| R3-A2 | random #1 | 5 | 1 | 1 | 2^32 | 424242102 | 102 |
| R3-A3 | random #2 | 5 | 1 | 1 | 2^32 | 424242103 | 103 |
| R3-A4 | AES (null) | 10 | 1 | 1 | 2^32 | 424242104 | 104 |
| R3-A5 | AES (struct-destroyed) | 5 | 15 | 1 | 2^32 | 424242105 | 105 |
| R3-A6 | random #1 (struct-destroyed) | 5 | 15 | 1 | 2^32 | 424242106 | 106 |
| R3-A7 | random #2 (struct-destroyed) | 5 | 15 | 1 | 2^32 | 424242107 | 107 |

Keys are derived from each arm's seed (sm64 stream, probe.c formula) so every
arm uses an independent key; the null arm R3-A4 is the r=10 decay check
(BATCH-002's A3 analog, independent key). If the budget allows, a
random-S-box null at r=10 is added. A small 2^26-trial calibration run may
precede the arms to size the wall clock; it is recorded as calibration, not
as an arm.

## Pre-registered predictions

- **R3-P1 (pin).** All pins pass (KAT r=10, r=5 anchor, roundtrips,
  bijectivity, determinism, Python cross-check). If any pin fails, all arms
  are VOID.
- **R3-P2 (AES arm).** R3-A1 replicates the yoyo: count > 12, expected band
  ~45–75 hits (A1b at 2^32 read 60; excess ~15x, band 8x–25x per BATCH-002
  PR-2).
- **R3-P3 (the question).** R3-A2, R3-A3 — the two readings that are
  pre-committed:
  - **S-BOX-INDEPENDENT**: BOTH random arms count >= 13 (outside the 99%
    Poisson interval [0,12] of null expectation 4.0; Poisson(4) P(X>=13)
    ≈ 2.7e-4), with excesses of the same order as the AES arm.
  - **S-BOX-DEPENDENT**: BOTH random arms count <= 12 (inside the null
    interval), while the AES arm is above it. The yoyo is then the
    campaign's one AES-specific object.
  - Mixed (one random arm >=13, the other <=12): reported plainly as such;
    verdict driven by the null arm and stated without softening.
- **R3-P4 (controls).** Null arm R3-A4 count inside [0,12] (BATCH-002 A3
  read 5 at 2^33, 0.625x); structure-destroyed R3-A5 count inside [0,12]
  (BATCH-002 A4 read 4 at 2^32, 1.0x). A count > 12 in either control is a
  V-flag on the pipeline (V-flag also if trivial-swap degenerates are not
  excluded or PW/CW tables differ from the frozen geometry).

## Tier / scope / prohibitions

TOY TIER. No statement about full-round or deployed AES; no comparison to
published cryptanalysis in either direction (RQ-AES-003 R3); no promotion or
dismissal of any hypothesis (executor role). Edit NO prior-batch artifact and
no RANK 2 block of this task's files. No git. Structured artifacts must
parse (JSON validated with python3 json.load).

## Inference block (RANK 3)

policy: executor-implementation; requested_policy: executor-implementation;
resolved_model: deepseek-v4-flash-free (ACTUAL model serving this session,
self-reported from session context; no adapter probe run);
fallback_used: false; model_verified: false; standing_basis:
0137a051eb5828789eb267fa83c8278086578d4c.

## Budget (RANK 3)

2400 s wall (window 2026-08-06T03:42:49Z -> 04:22:49Z), 8 GB, max 25 runs.
HALT at binding_stop; partial results reported as measured, never as nulls.
