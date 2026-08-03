# PREREGISTRATION — TASK-20260803-367b1b

GOAL-AES-003 / BATCH-004 / executor. Written and frozen **before** any
signal-bearing measurement was taken. Claim tier: **TOY**. Certificate kind:
**none** (pure measurement; no solve, no relation, no key recovery is claimed).

Two items: RANK 2 (the true-hint positive control BATCH-003 rank 4 never had)
and RANK 3 (the S-box dependence of the r=5 yoyo signal). RANK 3 is the
declared priority if budget forces a choice.

## Inference block

```yaml
policy: executor-implementation
requested_policy: executor-implementation
resolved_model: claude-opus-5
resolved_model_basis: >-
  self-reported by the running session's own system context; no adapter probe
  was executed, so this resolution is NOT independently verified
fallback_used: true
fallback_basis: >-
  orchestration/model-policies.yaml names GPT-5.6-family policy aliases that
  Claude Code cannot resolve; every subagent in this harness runs model: inherit
model_verified: false
standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
independence_note: >-
  This session supplies SESSION and (for the yoyo probe) IMPLEMENTATION
  independence from the BATCH-002 probe, and supplies NO MODEL independence.
  Nothing here may count toward a closure quorum.
```

## Timeline discipline

Preregistration frozen at elapsed 264 s of a 2400 s budget
(`budget_stamps.jsonl`, stamp `setup_complete_prereg_begin`). What existed
before this file was frozen, and nothing else:

- the yoyo probe source, its build, its geometry dump, and its correctness pin
  (FIPS-197 C.1 known-answer vector + 5120 encrypt/decrypt round-trips);
- one **calibration** arm `CAL` (`aes`, r=5, amask=1, smask=1, log2N=25,
  seed 999000111, armid 99) run solely to measure throughput. Its counts are
  reported in RESULTS.json like every other run and its seed/armid are used by
  no scored arm. Measured: 2^25 trials in 4.86 s on 2 threads (6.9e6 trials/s).

Trial counts below were chosen from that calibration against the remaining
budget. No scored arm had been run.

---

## RANK 2 — true-hint positive control for the BATCH-003 rank-4 instrument

### The gap being closed

BATCH-003 rank 4 reported that corrupting any single hint slot t=0, t=1 or t=2
empties the candidate set, each giving the histogram `{0: 4}` (four diagonals,
zero unique-and-correct). Its declared backward-compatibility check compared a
**false-hint** `{0:4}` against a **false-hint** `{0:4}`. That comparison cannot
distinguish "the modified binary correctly reports emptiness under a false
hint" from "the modified binary reports emptiness for every input", including
correct ones. No arm in BATCH-003 rank 4 demonstrated the instrument capable of
emitting a non-empty result.

### Object

The **same** modified `sq_slot` binary. Source copied byte-identically from
`BATCH-003/tasks/TASK-20260802-447db8/src/sq_slot.c`
(sha256 `13eb85a3a433a7e1d1ce9df292ae696f66075fd55b27ee26c36eb883a7272a79`)
into `src/` here and rebuilt. The only change from `sq_null.c` is the
documented slot-bitmask semantics (`src/sq_slot.diff`).

Arm **PC-TRUE**: `attack6n`, same target key, same hint key, same rounds (6),
same structures (2), same seed (90009) as the BATCH-003 rank-4 arms, with
`nwrong = 0` under `mask` semantics, i.e. **slotmask 0 — every hint byte
taken from the TRUE key schedule**.

Deviation declared in advance: `nthreads = 2` instead of BATCH-003's 1, to fit
the shared 2-thread cap. `nthreads` splits the b0 range of a fold that is
recombined by XOR and does not touch the plaintext RNG (`srand(seed)` in the
main thread), so the result is expected to be thread-count invariant. If the
result were to depend on thread count that is itself a finding and will be
reported.

### Prediction (frozen)

**P2.1**: `diagonals_unique_and_correct = 4` and
`diagonals_with_survivors = 4`, i.e. the histogram `{1: 4}` — all four
diagonals yield a unique surviving byte and it is the true byte.
Confidence: high. This is the ordinary BATCH-001 6-round Square attack
behaviour with a fully correct hint.

**P2.2**: `hint_bytes_actually_differing = 0` on every diagonal.

### Decision rule

- If `diagonals_unique_and_correct = 4`: the instrument is shown capable of
  producing a non-empty, correct result, and the BATCH-003 rank-4 all-empty
  regression hypothesis is **excluded**.
- If the result is empty (`diagonals_with_survivors = 0`) or non-empty but
  incorrect: report plainly that BATCH-003's rank-4 conclusion rests on an
  instrument never shown capable of producing a non-empty correct result, and
  mark it **UNSUPPORTED** on that ground. I do not get to soften this.
- If the run does not complete within its cap: that is **resource
  exhaustion**, not evidence about the instrument, and rank 2 is reported as
  dropped and named.

Hard cap: 450 s wall.

---

## RANK 3 — S-box dependence of the r=5 yoyo signal

### The object

Identical to the BATCH-002 yoyo object. Convention

```
E_K^r = ARK_r . SR . SB . [ARK_i . MC . SR . SB]_{i=r-1..1} . ARK_0
round keys = first r+1 of the UNTRUNCATED FIPS-197 AES-128 expansion,
             computed with the SAME S-box the cipher uses.
```

Geometry, stated explicitly on both sides because a replication in this
campaign once read a null purely from getting it wrong:

- **plaintext side (forward ShiftRows diagonals)** `PW[j] = {4*((j+r)%4)+r}`,
  so `PW = [[0,5,10,15],[4,9,14,3],[8,13,2,7],[12,1,6,11]]`;
- **ciphertext side (INVERSE ShiftRows diagonals)** `CW[j] = {4*((j-r)%4)+r}`,
  so `CW = [[0,13,10,7],[4,1,14,11],[8,5,2,15],[12,9,6,3]]`.

Both were dumped from the built binary (`./yoyo_sbox geom`) and agree byte for
byte with BATCH-002's `geom.json`. That dump is in RESULTS.json.

One trial: draw `p0`; form `p1` by re-randomising every byte of every word in
`amask`, rejecting a draw that leaves an active word unchanged; encrypt both
for `r` rounds; **swap the ciphertext words in `smask`** between the two
ciphertexts (a swap in which every swapped byte already agreed is TRIVIAL and
is excluded from all counts); decrypt both; `d = q0 ^ q1`; `W` = number of
plaintext words `j` on which `d` vanishes; the statistic is the count of
trials with `W >= 1`.

Analytic null: `P(W>=1) ~ 4 * 2^-32`, so `NULL = nontrivial_trials * 2^-30`.
Excess factor = observed `W>=1` count / NULL. BATCH-002 measured 15.63x at
r=5 under the real AES S-box (arm A1, 2^33 trials, 125 hits vs null 8).

### Reuse statement

**Rewritten, not reused.** The BATCH-002 probe implements AES with AES-NI
(`_mm_aesenc_si128` / `_mm_aesdec_si128`), which hardwires the AES S-box in
silicon; the S-box cannot be substituted there. `src/yoyo_sbox.c` reimplements
the same object as a T-table software AES whose S-box is a run-time parameter,
reproducing BATCH-002's conventions, geometry, RNG (splitmix64), thread-seed
derivation, key derivation from the arm seed, trivial-swap exclusion and
reporting fields. The trial loop is a line-for-line transcription of
BATCH-002's `worker()` onto byte arrays. Correctness pin: FIPS-197 C.1
known-answer vector reproduced exactly (`69c4e0d86a7b0430d8cdb78070b4c55a`)
and 512 keys x 10 round counts = 5120 encrypt/decrypt round-trips, 0 failures.
For a random S-box the KAT does not apply and the round-trip pin is run in its
place, which is what establishes that `dec_r` is the exact inverse of `enc_r`
for that S-box.

### Random S-box construction (documented draw, verified bijective)

Fisher-Yates shuffle of `[0..255]` driven by splitmix64 seeded with the
recorded seed, with **rejection sampling** for each index (a 64-bit draw is
rejected if it falls in the short tail, so there is no modulo bias). Two
independent draws:

- **R1**: seed `20260803001`
- **R2**: seed `20260803002`

Before any measurement the binary verifies the drawn table is a bijection:
every output value occurs exactly once, all 256 values occur, and
`ISBOX[SBOX[x]] == x` and `SBOX[ISBOX[x]] == x` for all x. If the check fails
the binary **refuses to measure** (exit 4). The same S-box is used in the
cipher and in the key expansion. Full 256-byte tables are recorded.

### Arms

| arm | S-box | r | amask | smask | log2N | seed | armid | role |
|---|---|---|---|---|---|---|---|---|
| Y-AES-main | aes | 5 | 1 | 1 | 31 | 431001 | 1 | main |
| Y-R1-main | rand:20260803001 | 5 | 1 | 1 | 31 | 431002 | 2 | main |
| Y-R2-main | rand:20260803002 | 5 | 1 | 1 | 31 | 431003 | 3 | main |
| Y-AES-sd | aes | 5 | 15 | 1 | 30 | 431004 | 4 | structure-destroyed control |
| Y-R1-sd | rand:20260803001 | 5 | 15 | 1 | 30 | 431005 | 5 | structure-destroyed control |
| Y-R2-sd | rand:20260803002 | 5 | 15 | 1 | 30 | 431006 | 6 | structure-destroyed control |

Each arm derives its own AES key from its own seed, so each S-box arm carries
an independent key. Each arm carries its own **matched analytic null**
(`nontrivial_trials * 2^-30`) and its own **structure-destroyed control**
(`amask = 15`: all four plaintext words active, so no diagonal-coset structure
remains, everything else identical).

Declared power asymmetry: mains at 2^31 (null 2.0), structure-destroyed
controls at 2^30 (null 1.0), chosen from the calibration to fit the budget.
The controls therefore have less resolution than BATCH-002's A4 at 2^32 and
that limit is restated beside their numbers.

Expected cost from calibration: 3 x ~311 s + 3 x ~155 s ~= 1400 s.

### Predictions (frozen)

I hold **no preference** between the two outcomes and register both. The prior
below is stated so that it can be scored later, not to license softening.

**P3.1 (reference arm)**: Y-AES-main reproduces the BATCH-002 r=5 signal in a
third, software, S-box-parameterized implementation: excess factor in the
range **8x–25x** (point expectation ~15.6x, i.e. ~31 hits against a null of
2.0). If Y-AES-main does *not* reproduce it, the S-box arm is uninterpretable
and I report that instead of reading anything into the random-S-box arms.

**P3.2 (random S-box arms)**: exactly one of
- **H-INDEP**: both random arms show excess >= 5x (point expectation ~15x,
  ~31 hits) — the yoyo is a fact about SPN round geometry, and then **no
  result in this campaign is specific to the AES S-box**;
- **H-DEP**: both random arms show excess <= 2.5x (point expectation ~1x,
  ~2 hits) — the yoyo is the campaign's **one genuinely AES-specific object**.

Registered prior, honestly: **50/50**. The argument for H-INDEP is that the
r=4 and r=5 counting properties of this campaign already reproduced 120/120
under uniformly random bijective S-boxes, so the campaign's other signals are
geometric. The argument for H-DEP is that the yoyo statistic is a two-sided
encrypt/decrypt coincidence rather than a counting/balance property, and it is
the only one of these signals whose S-box dependence has never been tested —
which is exactly why it is being measured.

**P3.3 (structure-destroyed controls)**: all three sd arms sit at the null,
excess <= 2.5x (point expectation ~1x, ~1 hit against a null of 1.0),
regardless of S-box. If an sd arm shows an excess, the diagonal-coset
attribution of the signal is wrong and that will be reported.

### Decision rule (frozen)

Let `X` be the observed `W>=1` count and `v` the matched analytic null.

- **ALIVE** iff `X/v >= 5` and the one-sided Poisson tail
  `P(K >= X | lambda = v) < 1e-6`.
- **DEAD** iff `X/v <= 2.5` and `P(K <= X | lambda = 15.63*v) < 1e-3`.
- Otherwise **INDETERMINATE**.

Reading:
- **S-BOX-INDEPENDENT** iff Y-AES-main is ALIVE and both random mains are
  ALIVE;
- **S-BOX-DEPENDENT** iff Y-AES-main is ALIVE and both random mains are DEAD;
- any other combination (including a mixed pair, or a reference arm that is
  not ALIVE) is reported as **MIXED / INDETERMINATE** with the raw counts, and
  no reading is asserted.

Both tail tests are computed exactly from the Poisson CDF in the analysis
script and both p-values are reported for every arm, whichever way they fall.

### What this cannot establish

Toy tier. r=5 of a reduced-round AES-128 permutation with a full 128-bit key
schedule, on one implementation, two random S-box draws, and at most 2^31
trials per arm. Nothing here speaks to full-round or deployed AES, and no
comparison to published cryptanalysis is made in either direction. Two random
draws bound very little about the space of 256! bijections; a DEAD reading
would say those two draws killed it, not that the AES S-box is unique. A
timeout is resource exhaustion and never negative evidence.

## Budget and halt

2400 s wall, 8 GB, at most 2 threads (one other producer runs concurrently),
at most 25 runs. `budget_stamps.jsonl` carries the computed
`binding_stop_utc`. At that stop I halt, record `halted_on_budget` truthfully
and name the dropped work. If budget forces a choice, RANK 3 is completed
first and RANK 2 is dropped and named.

## Artifact parse check

RESULTS.json will be parsed with a JSON parser before this task finishes and
the check will be recorded inside the artifact.
