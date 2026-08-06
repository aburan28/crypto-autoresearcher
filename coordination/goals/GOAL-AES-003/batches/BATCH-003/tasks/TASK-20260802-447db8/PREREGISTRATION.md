# PREREGISTRATION — TASK-20260802-447db8 (GOAL-AES-003, BATCH-003, RANK 2 + RANK 4)

Written and frozen BEFORE any measurement in this task. Predictions below are
stated so that they can be wrong. Measured values are reported beside them in
RESULTS.json.

- task_id: TASK-20260802-447db8
- role: executor
- claim tier: TOY. Reduced-round AES-128 only. Nothing here is a statement about
  full-round or deployed AES, and no comparison to published cryptanalysis is
  made or implied in either direction (RQ-AES-003 R3).
- budget: 3000 s wall clock, 8 GB. start_utc 2026-08-02T22:39:06Z,
  binding_stop_utc 2026-08-02T23:29:06Z (computed, see budget_stamps.jsonl).
- inference: policy executor-implementation / requested_policy
  executor-implementation / resolved_model claude-opus-5 / fallback_used false /
  model_verified false (no adapter probe was run) / standing_basis
  0137a051eb5828789eb267fa83c8278086578d4c.

## RANK 2 — cross-instrument anchor (PRIORITY)

### Object

Two counting engines built in earlier batches have never been anchored against
each other; EV-AES-d8a13e names this as the campaign's one unresolved confound
("conventions were read across by eye").

- ENGINE A: `BATCH-001/tasks/count5/count5.c` — AES-NI only, fixed AES round
  function, no configurable mixing layer. Args: r, j0, expanded RK (176 bytes),
  base, pimode, ptmode.
- ENGINE B: `BATCH-002/tasks/TASK-20260802-142a4b/cnt.c` — software GF(2^8)
  T-table with a configurable 4x4 mixing matrix (also has an AES-NI path). Args:
  engine, r, j0, 16-byte key (expands internally), base, matrix, cw, wbits,
  threads.

NEITHER SOURCE IS EDITED. Both are compiled from byte-identical copies (sha256
recorded in RESULTS.json) placed in this task directory.

### Identical configuration to be run on both

| parameter | value |
|---|---|
| rounds r | 5 |
| j0 | 1 |
| projection | `id` convention: pi_{j0}(c) = state bytes 4*((j0-t) mod 4)+t, byte t at bit 8t |
| plaintext set | full 2^32 coset of D_0 (state bytes 0,5,10,15 free) |
| key | `2b7e151628aed2a6abf7158809cf4f3c` (FIPS-197 key, publicly checkable) |
| base | `00112233445566778899aabbccddeeff` |
| mixing matrix (engine B) | `02030101010203010101020303010102` = real AES MixColumns |
| round structure | C1: r rounds, initial whitening, final round has no mixing layer |

Engine A is given the 176-byte expansion of that key, computed by an INDEPENDENT
Python key schedule written for this task and cross-checked against FIPS-197.

Three arms on the identical configuration:
- A1 `count5` (AES-NI, 4 threads by construction),
- B1 `cnt soft` (software T-table with the AES MixColumns matrix),
- B2 `cnt aesni` (engine B's own AES-NI path; a within-engine control).

Comparison statistic: the tuple (N, n, n_alt, max_occ, full occupancy
histogram). n = sum_v C(m_v, 2). Agreement is reported as EXACT (identical
integers, identical histogram) or NOT AT ALL. No tolerance is defined, because
none is admissible.

### Predictions (frozen)

- **P2.1 (primary).** All three arms return the SAME integer n, the same N, the
  same max_occ and the same occupancy histogram. Basis: reading both sources,
  the coset layout (bytes 0,5,10,15), the projection index set and bit
  placement, the C1 round structure and the counting statistic are the same
  object in both. Predicted with the engines' conventions believed to match, so
  a disagreement falsifies that belief, not the prediction's admissibility.
- **P2.2 (magnitude, weaker).** n is near the generic value
  C(2^32,2)/2^32 = 2147483647.5, within about +/- 1e6; max_occ in 10..15;
  N = 4294967296.
- **P2.3 (pin).** A single-block r=5 encryption of one fixed plaintext agrees
  across: my independent Python reference, engine B `block` mode soft path,
  engine B `block` mode AES-NI path, and BATCH-001's own `pin` binary (which is
  engine A's round function with the expansion I supply). Four-way byte
  equality. This isolates key-schedule/round-function agreement from
  coset/projection/counting agreement.
- **P2.4 (predicted representational asymmetry, stated in advance).** Engine A's
  counter is `uint8_t` SATURATING at 255 with a 256-bin histogram; engine B
  supports cw=16. Therefore any configuration whose occupancy reaches 255 —
  including BATCH-002's r=4 critical arm with max_occ exactly 256 — CANNOT be
  represented by engine A at all, and engine A would report max_occ 255 with
  `overflow:true` and a wrong n. This is an engine capability limit, NOT a
  convention disagreement, and it is why the anchor configuration is chosen at
  r=5 where max_occ is predicted around 12. If it materialises it will be
  reported as a limit, separately from P2.1.

### Falsifier and its handling

If the integers differ, the finding is: CROSS-BATCH COMPARISONS IN THIS CAMPAIGN
ARE UNSOUND, including the r=4 exact-bijection result BATCH-001 established and
BATCH-002 built on. It will be reported as such. NEITHER ENGINE WILL BE ADJUSTED
TO MATCH THE OTHER. I will state which engine I believe is wrong and give the
reason from the code, and that statement will be labelled an inference from code
reading, not a measurement.

## RANK 4 — single-slot hint corruption at t=1 and t=2

### Object

BATCH-002's `sq_null.c attack6n` corrupts hint bytes by PREFIX:
`hint[d][t] = (t < nwrong) ? wrongkey_byte : true_byte`. So "a single false hint
byte" was only ever tested at slot t=0 (nwrong=1). Slots t=1 and t=2 were never
singly corrupted (OBS-B2-1 limits, EV-AES-d8a13e unresolved confound 2).

`sq_null.c` is copied unedited into this task directory as `sq_slot.c` with ONE
change: the last argument may be read as a SLOT BITMASK.

    hint[d][t] = ((slotmask>>t)&1) ? hrk[rounds][DIAGP[d][t]] : rk[rounds][DIAGP[d][t]];
    slotmask = (mask flag given) ? argv_value : ((1<<nwrong)-1)

Without the flag this is EXACTLY the old prefix semantics, so the modification is
a strict generalisation. The diff will be recorded in RESULTS.json.

### Runs

Same target key, same hint key, same rounds, same nstruct and same seed as
BATCH-002's existing t=0 arm PART6-1of3-A, so the ONLY variable changed is which
slot is false:

- R4-T1: `attack6s 2b7e151628aed2a6abf7158809cf4f3c 53787ef6b300ea19f0a43d4915afd440 6 2 90009 <threads> 2 mask`  (slot t=1 false)
- R4-T2: same with mask 4 (slot t=2 false)

Reference arm already in BATCH-002 (NOT re-run, NOT edited): PART6-1of3-A,
nwrong=1 prefix = slot t=0 false.

### Predictions (frozen)

- **P4.1.** Both runs give survivor-count histogram `{0: 16}` over the 16
  (diagonal, row) cells — i.e. the candidate set is EMPTIED, exactly as at slot
  t=0. Basis: each hint byte enters the fold through the same inverse-S-box
  partial-sum position, so no slot is privileged.
- **P4.2.** `diagonals_with_survivors` = 0, `diagonals_unique_and_correct` = 0,
  and the true byte does not appear in any survivor set.
- **P4.3 (falsifier).** If either slot leaves survivors, the emptiness reported
  by OBS-B2-1 is SLOT-DEPENDENT and the observation is narrower than stated.
  That would be the reportable finding.

### Reporting form

Survivor-count histograms per diagonal in the same `{0: n}` / `{1: n}` form
BATCH-002 used, per run, plus the per-cell survivor counts.

## Standing constraints acknowledged

- Two other producers run concurrently on this 4-core machine. Engine A spawns 4
  threads by construction and cannot be given a thread count without editing it,
  which would compromise the anchor; it is therefore CPU-pinned to 2 cores with
  `taskset`, and this is recorded as a deviation with its reason.
- A timeout or an out-of-budget halt is resource exhaustion, never negative
  evidence.
- If the clock forces a choice, RANK 2 is completed and RANK 4 is dropped and
  named as dropped.
