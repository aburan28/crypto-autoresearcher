# PRE-REGISTRATION — TASK-20260802-142a4b (IMMUTABLE)

GOAL-AES-003 / BATCH-002. Role: Executor. Written **before any full-coset
measurement in this task**. Frozen at the moment of writing; corrections, if
any, appear as separate `AMENDMENT-*.md` files with their own UTC stamp, never
by editing this file.

Session clock (C2): start `2026-08-02T17:07:06Z`, epoch `1785690426`,
declared wall clock `3000 s`, computed binding stop
`2026-08-02T17:57:06Z` (epoch `1785693426`). Memory ceiling 8 GB.

Written at approximately `2026-08-02T17:20Z`, after the instrument pin
(single-block checks only, no full-coset counting) and after the matrix
non-singularity checks, and before any 2^32 counting run.

`claim_tier: toy`. `certificate.kind: none` — this is pure measurement; no
solve and no factor-base relation is claimed, so no solution certificate is
required or offered. Nothing here asserts anything about full-round or
deployed AES, and no comparison to published cryptanalysis is made in either
direction (RQ-AES-003 R3). No hypothesis is declared supported, rejected or
closed; no heuristic is declared validated or refuted.

Governing-contract status, reported and not repaired: there is no
`experiments/<EXP-ID>/specification.yaml` with `status: approved` and non-null
`approved_by` for this work. Missing relative to a formal contract:
`experiment_id`, `status`, `approved_by`, `stopping_rules`,
`required_artifacts`. The authorising record is the dispatch card in
`coordination/goals/GOAL-AES-003/batches/BATCH-002/dispatch_queue.json` and
`DEC-20260802-007`, which is a batch dispatch, not an approved experiment
contract. This is recorded as a deviation, not repaired.

---

## 0. Scope carried forward, unhedged

The BATCH-001 validator ruled that the r=4 bijection and the r=5 mod-8
property are **NOT specific to the AES S-box**. They follow from round
geometry alone and were reproduced with uniformly random bijective S-boxes at
120/120. This **confirms** the derivation, which never used the S-box. Every
statement in this task about those properties carries that scope: they are
properties of an AES-**shaped** SPN, instantiated here on AES-128, and they
carry no information about the AES S-box.

## 1. Object, conventions, instrument

Conventions are those of the BATCH-001 `count5` preregistration section 1,
restated so this file stands alone.

- Cipher convention C1: `s = P ^ RK[0]`; for `i = 1..r-1`,
  `s = ARK_i(M(SR(SB(s))))`; final round `s = ARK_r(SR(SB(s)))` (no mixing
  layer in the last round).
- `M` is the mixing matrix, applied column-wise, `out[:,c] = M * in[:,c]`.
  For AES, `M = AES_MC`.
- Input set `V`: the full 2^32 coset of `D_0` — 16-byte base `b`, bytes
  `{0,5,10,15}` ranging over all 2^32 values, other twelve fixed.
  Byte 0 = `a & 0xff`, byte 5 = `(a>>8) & 0xff`, byte 10 = `(a>>16) & 0xff`,
  byte 15 = `(a>>24) & 0xff`.
- Projection `pi_{j0}(c) = sum_{t=0..3} c[4*((j0-t) mod 4)+t] << 8t`
  (the inverse-ShiftRows diagonal `ID_{j0}`).
- Counted quantity `n_r = sum_v C(m_v, 2)`, `m_v` the occupancy of value `v`.
  Recorded as an exact integer, never only as a residue. Statistic:
  `n_r mod 8` (mod 16 also recorded).

Instrument: `cnt.c`, written for this task. It is **not** BATCH-001's
`count5.c`: threads partition the *input* space and use atomic counter
increments (count5 partitioned the *value* space and re-encrypted the whole
coset in every thread), and it carries a software T-table engine with a
**configurable** GF(2^8) mixing matrix, which `count5.c` does not have. The
AES-NI path is used only for the real-AES / 10-round-AES arms. Reference
implementation `count5.c` was read for its conventions; no code was copied.

Independent cross-check `ref.py`: a pure-Python AES-shaped SPN written for
this task whose S-box is **derived** (GF(2^8) inverse plus the FIPS-197 affine
map), not copied, plus GF(2^8) rank/determinant/inverse and an MDS test.

## 2. RANK 2 — null residue distribution at r=5

BATCH-001 refuted *deterministically* that `n_5 mod 8 = 0` is forced for any
bijection: a forced property reads 0 with probability 1, so a single non-zero
null reading settles it. That refutation stands and is not re-litigated here.
What is measured here is the *shape* of the null residue distribution.

New arms: five random-permutation surrogate arms (10-round AES-128, the same
surrogate family BATCH-001 used), same full 2^32 coset, same projection,
independent keys, bases and `j0` derived from master seed
`TASK-20260802-142a4b/seed=20260802142` by SHA-256 expansion; parameters
frozen in `params.json` before measurement.

Predictions:

- **R2-P1.** Each arm yields `n` near the balls-in-bins mean
  `(2^32 - 1)/2 = 2147483647.5`, within a few times the s.d. (~2^15.5 ≈ 46341
  under a Poissonised model). No arm overflows a uint8 counter
  (predicted `max_occ` in 10..15).
- **R2-P2.** The five new residues are not all 0 and show no evident
  structure. Pooled with the prior arms the residue multiset is consistent
  with uniform on {0..7}; with ~13 readings a chi-square test on 8 bins is
  **underpowered** and will be reported as such. Predicted chi-square
  p-value > 0.05, i.e. uniformity not rejected. **Uniformity will not be
  claimed** whatever the outcome; failure to reject is not evidence for.
- **R2-P3 (predicted answer to the question the card asks).** The
  distribution characterisation adds **nothing of consequence** beyond the
  deterministic refutation. Predicted before measurement so that the honest
  answer cannot be an after-the-fact deflation. The one thing it could add is
  a *surprise* — a strongly non-uniform null, e.g. a residue class never
  observed or a mod-16 clustering — which would indicate a second counting
  identity acting on the null object; predicted **not** to appear.

A p-value framing is the WEAKEST correct statement available on this
question, and this is preregistered as the reporting stance, not decided
after seeing the numbers: forcing is a probability-1 statement, already
refuted by exhibiting counterexamples. A p-value can only ever say the null
is *unlikely*; the deterministic argument already says it is *false*.

## 3. RANK 4 — the derivation's asserted no-zero-entry dependence

The BATCH-001 derivation asserts, in section 3.5 fact 2, that "MC has no zero
entry", and uses `v_col[t] != 0` in 3.2/3.4. `EV-AES-005` carries this forward
as "any column-preserving mixing layer with **no zero in the relevant
entries**". That condition was asserted and never tested; the validator's
candidate zero-entry matrix was singular and its control never ran.

### 3.1 Matrices (non-singularity verified BEFORE measurement)

All over GF(2^8) with the AES modulus `x^8+x^4+x^3+x+1`. Verification is by
`ref.py` Gauss-Jordan: rank, determinant, explicit inverse, and the product
`M * M^{-1}` checked equal to the identity.

| name | rows | zero entries | rank | det | non-singular | MDS |
|---|---|---|---|---|---|---|
| `AES_MC` | `[[2,3,1,1],[1,2,3,1],[1,1,2,3],[3,1,1,2]]` | none | 4 | 0x01 | yes | yes |
| `M0` | `[[0,3,1,1],[1,2,3,1],[1,1,2,3],[3,1,1,2]]` | (0,0) | 4 | 0x1d | yes | no |
| `M1` | `[[0,3,1,1],[1,2,3,0],[1,1,0,3],[3,0,1,2]]` | (0,0),(1,3),(2,2),(3,1) | 4 | 0x14 | yes | no |

`M0` and `M1` are **MDS-substitutes**: non-singular, column-preserving, but
not MDS — a true MDS matrix cannot contain a zero entry, so "non-singular with
a zero entry" and "MDS" are mutually exclusive by definition. That is stated
here so no reader mistakes the object for an MDS layer.

Everything else is identical to the AES arms: same AES S-box, same ShiftRows,
same AES-128 key schedule (which uses no mixing layer, so it is unchanged by
construction), same coset, same projection, same key
`6fe52e2e9b3ea04085c370f9bc609245` and base
`e35f00e7631cdd862e59d126e72b8fc9` across all RANK 4 arms.

### 3.2 What the derivation's own algebra predicts, worked out before measuring

With `v_m := M[:, (-m) mod 4]`, column `m` of the round-2 state is
`b_m ^ a_m * v_m` with `a_m` free (3.2 of the BATCH-001 derivation; this needs
only that every column of `M` is non-zero, i.e. `M` non-singular).

- **r = 4** the condition is `w ^ w' in D_J`, i.e. for every column `m`,
  `(a_m ^ a'_m) * v_m[(m - j0) mod 4] = 0`. So `n_4 = 0` **iff** the four
  entries `M[(-c-j0) mod 4][c]`, `c = 0..3`, are all non-zero. A single zero
  entry at `(r0,c0)` is therefore critical for **exactly one** `j0`, namely
  `j0 = (-c0-r0) mod 4`. For `M0` the zero is at (0,0), so **`j0 = 0` is
  critical and `j0 = 1,2,3` are not**.
- **r = 5** the condition is `sum_col g_col = 0` with
  `g_col(a,a')[i] = M[i][t] * f_{col,t}(a,a')`, `t = (col - j0 - i) mod 4`.
  Fact 1 (symmetry in the unordered pair) uses no property of `M`.

### 3.3 Predictions

- **R4-P1 (r=4, critical `j0`).** `M0`, `r=4`, `j0=0`: the property is
  **DESTROYED**. Exact prediction
  `n_4 = 2^24 * C(256,2) = 16777216 * 32640 = 547608330240`,
  occupancy histogram exactly `{0: 4278190080, 256: 16777216}`,
  `max_occ = 256`. This run needs uint16 counters; a uint8 run would overflow
  and is preregistered as invalid, not as a number.
- **R4-P2 (r=4, non-critical `j0`).** `M0`, `r=4`, `j0=1`: `n_4 = 0` exactly,
  `max_occ = 1`. The property **SURVIVES** the zero entry at this `j0`.
- **R4-P3 (r=5, `M0`).** `j0 = 0` (the critical index for r=4) and `j0 = 1`:
  `n_5 mod 8 = 0` in both. The r=5 property **SURVIVES** the zero entry.
- **R4-P4 (r=5, `M1`, fact 2 destroyed).** For `M1` at `j0 = 0`, column 0 has
  `g_0 == 0` identically: every `i` is covered by a zero of `M` or of `v_0`,
  so fact 2 of section 3.5 **fails outright** — pairs differing only in
  column 0 all satisfy the condition. Prediction: `n_5 mod 8 = 0` **anyway**,
  and `n_5 >= 547608330240`, `max_occ >= 256` (uint16 counters required).
- **R4-P5 (engine controls, same software engine, `AES_MC`).** `r=4, j0=0`:
  `n = 0`, `max_occ = 1`. `r=5, j0=0`: `n mod 8 = 0`. These show the custom-
  matrix engine reproduces the AES readings, so any difference under `M0`/`M1`
  is attributable to the matrix and not to the engine.
- **R4-P6 (the interpretation, frozen in advance).** If R4-P1..P4 measure as
  predicted, then the derivation's *stated* dependence is:
  - **CORRECT BUT OVERSTATED at r=4** — only 4 of the 16 entries matter, and
    which 4 depends on `j0`; "no zero entries" is sufficient, not necessary;
  - **WRONG at r=5** — section 3.5 fact 2, and with it the "no zero entry"
    hypothesis, is **not load-bearing** for `n_5 = 0 mod 8`. The reason is
    internal to the derivation's own counting: the `k = 1` class contributes
    `256^3 * (number of admissible unordered pairs)`, a multiple of `2^24`,
    hence a multiple of 8 whether or not fact 2 excludes it; `k = 2,3` carry
    `256^{4-k}`; and `k = 4` rests on fact 1 alone, which uses no property of
    `M`. Fact 2 is therefore dispensable for the mod-8 conclusion.
    Named failing step: **section 3.5, fact 2** (and its restatement in
    `EV-AES-005` boundaries as "no zero in the relevant entries" applied to
    the r=5 claim). This will be recorded as a defect in the derivation's
    stated hypothesis, not softened, and it does **not** overturn the r=5
    conclusion itself.
  If instead the r=5 property is destroyed by the zero entry, the
  derivation's stated dependence is corroborated and that will be recorded as
  such with equal directness.

## 4. VOID conditions (an affected reading is `invalid_measurement`, never a negative observation)

- **V1** The pin fails: C soft engine vs `ref.py`, or C soft engine with
  `AES_MC` vs the AES-NI path, or FIPS-197 C.1. (Run before this file was
  finalised; all passed, recorded in `pin_result.json`.)
- **V2** Counter overflow, or any lost atomic update: detected exactly by
  `sum_v v * hist[v] != (number of outputs falling in the window)`, reported
  as `counter_integrity_ok: false`. Such a run is INVALID and its `n` is not
  reported as a number.
- **V3** `n` from `sum_v C(m_v,2)` disagrees with the independent identity
  `n = (sum_v m_v^2 - N)/2` on the same histogram, or `N != 2^32`.
- **V4** A matrix used in a RANK 4 arm turns out singular. (Checked before
  measurement; both are rank 4.)
- **V5** Wall-clock halt at `2026-08-02T17:57:06Z`. Runs not started are
  reported as not run, with the dropped work named. A budget halt is never a
  null result and never evidence about AES.
- **V6** Memory: a single counting process must stay at or under 4 GiB of
  counter allocation (uint8 over 2^32 entries, or uint16 over 2^31 entries in
  two windows). No 8 GiB single allocation is attempted — BATCH-001 had an
  8 GB allocation killed.

## 5. Run order (executed top-down until halt)

1. RANK 2 arms N1..N5 (AES-NI, r=10, uint8, one window).
2. RANK 4 engine controls: `AES_MC` soft r=4 j0=0; `AES_MC` soft r=5 j0=0.
3. RANK 4 `M0`: r=4 j0=0 (uint16, two windows); r=4 j0=1 (uint8).
4. RANK 4 `M0`: r=5 j0=0; r=5 j0=1 (uint8).
5. RANK 4 `M1`: r=5 j0=0 (uint16, two windows); r=4 j0=0 (uint16, two windows).

Anything not reached by the binding stop is reported as dropped, by name.

## 6. Randomness

Single master seed string `TASK-20260802-142a4b/seed=20260802142`. All keys,
bases and `j0` are derived from it by SHA-256 expansion
(`SHA-256(seed|tag|counter)` concatenated) in Python and passed on the command
line. The C program contains no RNG. Frozen in `params.json`.

## 7. Inference block

```yaml
inference:
  policy: executor-implementation
  requested_policy: executor-implementation
  resolved_model: claude-opus-5
  fallback_used: false
  model_verified: false        # no adapter probe was run in this session
  standing_basis: 0137a051eb5828789eb267fa83c8278086578d4c
```

---

# CONTINUATION SECTION — SEGMENT 3 (appended 2026-08-02T20:18Z)

Nothing above this line was edited. This section is appended, timestamped, and
frozen in turn: it is written **before the M1 arm is executed** and before any
M1 full-coset number exists.

Segment 3 clock (C2): start `2026-08-02T20:17:01Z`, epoch `1785701821`,
declared wall clock `1800 s`, computed binding stop `2026-08-02T20:47:01Z`
(epoch `1785703621`). Memory ceiling 8 GB. Segment 1 and segment 2 stamps are
untouched.

## S3.1 Why this arm, stated in the reviewers' terms

Both reviewers held that the M0 arms do not settle what D-DERIV-1 asserts.

- Red team: `M0` has a single zero, at (0,0). For the one column `col = j0`
  it relaxes exactly **one** of the four `i`-constraints; the other three
  still force `f = 0`. So under `M0` the **conclusion** of fact 2 still holds
  at every `j0`. `M0` falsifies the literal sentence "MC has no zero entry" as
  a *necessary* condition, but it never exercises the exclusion fact 2
  actually performs.
- Validator: fact 2's `k = 1` class contributes `256^3 * N_ord/2`, a multiple
  of `2^24` and hence of 8, so the mod-8 conclusion survives deleting fact 2
  entirely; its ruling is that fact 2 is a TRUE statement about AES's MC that
  is **non-minimal** rather than false, and that any supersession must be
  **split by round count** — dropped at r=5, kept at r=4 where the paired
  `M0_r4_j0_CRIT` / `M0_r4_j1_NONCRIT` arms show it is measurably
  load-bearing.

Both point at the same untested arm: `M1`, in which fact 2 fails **outright**.
I accept both readings; they are sharper than the one I recorded, and the arm
they name is the one my own R4-P4 already identified and I dropped on budget.

## S3.2 The object

`M1 = [[0,3,1,1],[1,2,3,0],[1,1,0,3],[3,0,1,2]]`, already in `matrices.json`:
rank 4, det `0x14`, explicit inverse computed, `M1 * M1^{-1}` verified equal to
the identity. Non-singular; not MDS (a zero entry precludes MDS).

Its zeros sit at `(i, (-i) mod 4)` for `i = 0..3`. In the r=5 condition the
term column `col` contributes to equation `i` through `M[i][t_i]` with
`t_i = (col - j0 - i) mod 4`, so `M[i][t_i] = 0` for **all four** `i` exactly
when `col = j0`. Hence for **every** `j0`, the column `col = j0` has
`g_col == 0` identically: every pair differing only in that column satisfies
the r=5 condition, whatever the S-box does. Fact 2 does not merely become
unnecessary under `M1`, it is **false** under `M1`.

Run: `./cnt soft 5 0 <K> <B> 00030101010203000101000303000102 16 1 4`
with the frozen `K = 6fe52e2e9b3ea04085c370f9bc609245`,
`B = e35f00e7631cdd862e59d126e72b8fc9`. uint16 counters over two windows of
2^31 entries (4 GiB), honouring segment 1's VOID condition V6, which forbids a
single 8 GiB allocation.

## S3.3 PREDICTIONS, frozen before measurement

- **S3-P1.** `n_5 mod 8 = 0`. The mod-8 property SURVIVES even though fact 2
  is false for this matrix.
- **S3-P2.** `n_5 >= 547608330240`, because the `k = 1` class alone
  contributes `256^3 * C(256,2) = 16777216 * 32640 = 547608330240` exactly.
  I expect `n_5` to be that value plus the ordinary `k >= 2` and coincidence
  terms, i.e. of order `5.48e11 + ~2.1e9`.
- **S3-P3.** `max_occ >= 256`, since each class of 256 states differing only
  in column `j0` collides identically. I expect `max_occ` in roughly 256..300.
- **S3-P4.** `n_5 mod 16 in {0, 8}`; not further predicted. The `k = 1` term
  itself is `0 mod 16`.

## S3.4 What would FALSIFY the "fact 2 is dispensable" analysis

Stated now so it cannot be retro-fitted:

1. **`n_5 mod 8 != 0` under `M1` falsifies it outright.** That is the decisive
   reading. It would mean the analysis is wrong somewhere, that D-DERIV-1 must
   be withdrawn rather than split, and that the exact r=4 hit sits next to an
   r=5 error — precisely the transfer of belief the red team warned this
   package leans on. I would record that plainly and against my own prior
   claim.
2. `n_5 < 547608330240` would falsify S3-P2 and with it my identification of
   the `k = 1` contribution, even if the residue read 0. The residue could
   then be right for a reason I have not established.
3. `max_occ < 256` would likewise contradict the claimed structure of the
   `k = 1` class.

A reading of `0 mod 8` **with** `n >= 547608330240` **and** `max_occ >= 256`
is the confirmation. Any of 1-3 is a refutation of my analysis, not a nuance.

## S3.5 VOID conditions (unchanged, restated)

Counter overflow (`max_occ >= 65535`, or the per-window integrity identity
failing) makes the reading `invalid_measurement` and its `n` is NOT reported
as a number. A timeout is resource exhaustion, never negative evidence. No
claim about full-round or deployed AES; no comparison to published
cryptanalysis in either direction.

## S3.6 Corrections carried in from the reviewers, accepted

- My "three exactness checks" are **two**. `n` and `n_alt` are both computed
  from the same occupancy histogram `gh[]`, so `agree` is algebraically
  equivalent to `sum_b b*gh[b] == N`, which the per-window
  `if (wsum != inw)` integrity test already implies. It is arithmetic
  self-consistency of one histogram, not independent corroboration, and
  RESULTS.json will say so.
- The `8^-2 = 1/64` figure I attached to my two M0 r=5 arms assumed an
  independence I had not established: those arms are two projections of the
  **same** 2^32 ciphertexts (same matrix, key and base, differing only in
  `j0`). The honest 1/64 across two independent keys exists only because the
  **validator** ran `M0_r5_j2_ALTKEY` on its own key
  (`n = 2147227472`, `mod 8 = 0`). That is attributed to the validator, not
  to my arms.
