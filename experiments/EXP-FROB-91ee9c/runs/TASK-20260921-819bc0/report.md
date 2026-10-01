# RUN-FROB-91ee9c-819bc0 report

**Experiment:** EXP-FROB-91ee9c
**Handoff:** ledger/handoffs/TASK-20260921-819bc0.yaml
**Amendments executed:** DEC-20260921-e81e25 (v2, unchanged by this run) and
DEC-20260921-2f89d4 (v3, the corrected-construction fix this run implements)
**Scope:** object-arm consistency recompute (check only, both cells) and
control **C2_non_stable_matched_dimension** ONLY, using the corrected
per-slot-independent subspace-pool construction specified in
DEC-20260921-2f89d4. **C3 and C4 are out of scope for this run** and are not
computed or reported here.
**Certificate:** `kind: none`. Pure combinatorial measurement; no discrete
log solved, no key recovered.

This report states measured observations only. It does not conclude
anything about H-FROB-d93575's status -- that judgment is a separate
`/review-evidence` decision, per the amendment's `binding` clause.

## 1. Background: the defect being corrected

`ledger/corrections/CORR-20260921-9dc350.yaml` (correction C2), confirmed
independently by both the validator and red-team round-2 audits
(`experiments/EXP-FROB-91ee9c/validation-20260921-round2.md`,
`experiments/EXP-FROB-91ee9c/redteam-20260921-round2.md`, section 3(b)),
identified that `non_stable_subspace_of_dim(d, M, F, n)` in
`RUN-FROB-91ee9c-51bc02/implementation.py` is a pure function of `(d, M, F,
n)` alone. The old C2 construction loop cached ONE subspace per **distinct
dimension** present in an object partition and reused that cached subspace
for **every slot** of that dimension. On the only non-trivial partition
either tested cell reaches -- `[2,2]`, two slots of dimension 2 -- this
summed a non-pi-stable subspace with **itself** (`Q1 + Q2 = Q2 + Q1` for
`Q1 = Q2`), a swap-symmetry artifact unrelated to Frobenius structure.

## 2. The fix (DEC-20260921-2f89d4)

`non_stable_subspace_of_dim` gains an `exclude` parameter: it now searches
the same lexicographic `combinations(range(n), d)` order but skips
index-tuples already assigned. The C2 construction loop replaces the
per-distinct-dimension single cache with a **per-dimension pool**, grown
lazily to the maximum multiplicity of `d` needed by any tested partition in
the battery: entry 1 is the lexicographically first non-pi-stable subspace of
dimension `d` (unchanged from before); entry 2 is the lexicographically
**next** such subspace not already in the pool; and so on. A partition
needing `k` slots of dimension `d` takes the pool's first `k` entries, in
pool order. This is the only change from `RUN-FROB-91ee9c-51bc02`'s
`implementation.py`; the object arm, the search order, the certification
test (non-pi-stability), and everything else about C2's design are
unchanged.

## 3. Object-arm consistency check (both cells)

| cell | I | m1 (coarsest) ratio | m2 (argmin) ratio | argmin slot_dims | all_match |
|---|---|---|---|---|---|
| FROB-SPLIT-q11n5 | 2055/451 | 206733/41 | 5533/5 | [2,2] | **PASS** |
| FROB-EQDEG-q19n5 | 6152/861 | 12097908/205 | 82593/10 | [2,2] | **PASS** |

Both cells reproduce `RUN-FROB-91ee9c-51bc02`'s recorded object-arm values
**exactly** (same as `RUN-FROB-91ee9c-7119f2`'s curve-index-1 values, which
`RUN-FROB-91ee9c-51bc02` itself matched). **No instrument invalidation.**
Independently re-verified by `checker.py` (no Sage, no driver import; see
`work/checker-report.json`), which recomputes the field modulus, the object
arm's `I`/spread/argmin, and confirms agreement.

## 4. C2 result: old (defective) vs new (corrected), side by side

Only the `[2,2]` partition (two slots of dimension 2) is affected -- it is
the only partition either cell reaches with a repeated slot dimension. All
values are exact rationals (`fractions.Fraction`); `extra=0` for
`cost_ratio_neg`.

### FROB-SPLIT-q11n5

| quantity | OLD (defective, RUN-FROB-91ee9c-51bc02) | NEW (corrected, this run) |
|---|---|---|
| basis_indices used per slot | `[0,1]` and `[0,1]` (SAME subspace, reused) | `[0,1]` and `[0,2]` (DISTINCT subspaces) |
| block sizes (`B_W` per slot) | 6, 6 | 6, 4 |
| `U_neg` | 6/2 = 3 | 10/2 = 5 |
| `p_m` | 18/10060 | 24/10060 |
| `cost_ratio_neg` (extra=0) | 20120/9 (approx 2235.6) | 2515/1 |
| C2 spread | 4365/1936 (approx 2.2546) | 485/242 (approx 2.0041) |
| object-arm spread (2055/451 approx 4.5565) -- for reference | same both rows | same both rows |
| C2 spread strictly smaller than object arm's? | **True** | **True** |

### FROB-EQDEG-q19n5

| quantity | OLD (defective, RUN-FROB-91ee9c-51bc02) | NEW (corrected, this run) |
|---|---|---|
| basis_indices used per slot | `[0,1]` and `[0,1]` (SAME subspace, reused) | `[0,1]` and `[0,2]` (DISTINCT subspaces) |
| block sizes (`B_W` per slot) | 24, 24 | 24, 18 |
| `U_neg` | 24/2 = 12 | 42/2 = 21 |
| `p_m` | 288/117990 | 432/117990 |
| `cost_ratio_neg` (extra=0) | 85215/16 (approx 5325.94) | 24035/4 (approx 6008.75) |
| C2 spread | 24632/2223 (approx 11.0805) | 6158/627 (approx 9.8214) |
| object-arm spread (6152/861 approx 7.1452) -- for reference | same both rows | same both rows |
| C2 spread strictly smaller than object arm's? | **False** | **False** |

## 5. Did the fix change the strictly-smaller verdict?

**No, for either cell.** Both cells' strictly-smaller-than-object verdicts
for C2 are **unchanged** by the fix:

- **FROB-SPLIT-q11n5:** old verdict True (4365/1936 < 2055/451); new verdict
  also True (485/242 < 2055/451). The corrected C2 spread is numerically
  *smaller* than the defective one (approx 2.00 vs approx 2.25) but the
  comparison against the object arm's much larger spread (approx 4.56) does
  not flip.
- **FROB-EQDEG-q19n5:** old verdict False (24632/2223 > 6152/861); new
  verdict also False (6158/627 > 6152/861). The corrected C2 spread is
  numerically *smaller* than the defective one (approx 9.82 vs approx 11.08)
  and moved closer to the object arm's spread (approx 7.15) but is still
  strictly larger, so C2 still does NOT retain its role as an independent
  instance of "strictly smaller than object" on this cell, under either
  construction.

Per the handoff's `uncertainty_reduced` framing: the fixed C2 does **not**
change which of the two cells shows C2 as strictly-smaller-than-object. It
answers the narrower instrumental question -- the corrected C2 changes the
*numeric* spread on both cells but not the *verdict* on either.

## 6. Distinct-subspace verification (completion-gate requirement)

For both cells, the `[2,2]` partition's two slots are confirmed --
independently, by `checker.py` reading only the raw `C2_raw` pool, without
importing the driver or Sage -- to use **DISTINCT** basis-index tuples:

| cell | slot 1 basis_indices | slot 2 basis_indices | distinct? |
|---|---|---|---|
| FROB-SPLIT-q11n5 | `[0, 1]` | `[0, 2]` | **True** |
| FROB-EQDEG-q19n5 | `[0, 1]` | `[0, 2]` | **True** |

This directly falsifies the old defect's precondition (both slots sharing
`[0, 1]`): the pool for dimension 2 in both cells now has two entries,
`[0,1]` (the same lexicographically-first entry as before, unaffected) and
`[0,2]` (the lexicographically-next non-pi-stable subspace not already in
the pool), consumed in that order by the `[2,2]` partition's two slots.

## 7. Instrument invalidation

**None.** Both cells' object arms reproduced the recorded consistency
targets exactly (section 3); no `cell_status: instrument_invalidation` was
returned by either target.

## 8. Independent checker summary

`checker.py` (pure stdlib Python; does not import `implementation.py`,
`work/core.py`, `work/lattice.py`, or any Sage module, per control C8)
independently re-derived, for both cells: the field modulus, every reported
`cost_ratio_neg` value from raw `(U_neg, p_m)`, the object-arm `I`/spread/
argmin against the frozen consistency targets, the C2 spread, and -- the
purpose-specific check for this run -- that the C2 pool's `basis_indices`
per dimension are pairwise distinct and sufficient for the multiplicity each
partition needs. All checks **PASS** for both cells (full JSON:
`work/checker-report.json`, echoed into `work/checker-run1.log`). For
FROB-SPLIT-q11n5 only, a full independent brute-force `#E(F_{11^5})` point
count (Euler-criterion method, no Sage) matches the driver's recomputed
curve order exactly; FROB-EQDEG-q19n5's full re-enumeration (19^5 =
2,476,099 points) is disclosed as skipped for scale, matching the
disclosed-skip discipline of both prior runs' checkers.

## 9. Protocol deviations

None. No infrastructure failure or protocol deviation occurred. C3 and C4
were intentionally not computed, per the handoff's and amendment's explicit
scope narrowing (not a deviation).

## 10. Out of scope, explicitly

Per the handoff and DEC-20260921-2f89d4: control C3 (`random_matched_
cardinality`) and control C4 (`matched_null_curve`) were not recomputed.
Their constructions draw an independent value per slot already (C3: random
subset per slot; C4: per-slot draw inside a separate null curve) and do not
share C2's per-dimension-cache defect; both were independently re-verified
correct by the round-2 validator and red-team reports. `RUN-FROB-91ee9c-
51bc02`'s C3/C4 results stand, untouched, and are not superseded by anything
in this run.
