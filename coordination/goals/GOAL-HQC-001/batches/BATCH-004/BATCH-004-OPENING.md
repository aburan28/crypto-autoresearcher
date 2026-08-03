# GOAL-HQC-001 — BATCH-004 opening

- **Goal**: `GOAL-HQC-001` (status `active`)
- **Prior batch**: BATCH-003, closed `refine`, `DEC-20260803-…` → `DEC-20260802-d94a64`,
  `EV-HQC-0e9116`, verified ledger commit `e580f33a`
- **Opened**: 2026-08-03
- **Base merged from `main`**: `50f73a42`
- **Owner**: coordinator

## 1. Mandate

BATCH-004 executes `DEC-20260802-d94a64`'s single `next_action`: **repair, then
freeze**. In its stated order:

1. Fix the four high-severity design defects.
2. Rescope the two-rung claim and **evaluate the red team's `dup = 2` rung**.
3. Ship `calib_m0.py` / `calib_m0b.py` so the cost model is reproducible.
4. **Then** freeze `EXP-HQC-982268` and create `H-HQC-18d1b4` — and only then is
   a run authorised.

`H-HQC-18d1b4` and `EXP-HQC-982268` are the identifiers allocated for BATCH-003
and deliberately left unused when both reviews declined the contract. They are
carried forward rather than re-minted: nothing was ever written under them.

## 2. The four defects, stated so the repair can be checked

| # | Defect | Required repair |
|---|---|---|
| **D-1** | `CTRL-BS` requires offsets `o_j` "pairwise distinct and coprime to `T`" and concludes every block pair comes from distinct trials. The condition needed is on the **shifts** `j·o_j`. Counterexample inside the stated condition: `o_1 = 3`, `o_3 = 1` are distinct and coprime, yet `1·3 = 3·1`, so blocks 1 and 3 of *every* pseudo-trial share a source trial and retain the full space-(T) dependence. `0·o_0 = 0` always, so block 0's offset is inert. Coprimality does no work: `t ↦ t+s` is a bijection of `Z_T` for every `s`. | Require the **shifts** pairwise distinct; assert at run start. |
| **D-2** | The wash-out hole is **named but not closed**. `γ̂` is a property of `ẽ` alone and is **invariant under `dup`**, so the guard passes regardless; the `uninformative_null` trigger cannot fire; `CTRL-WBP` is inoperative under a null; the destroy-parameter ladder is optional and first to be cut. | A guard that is **not** invariant under `dup`, and a trigger that can actually fire. |
| **D-3** | Exchangeability, correctly removed from the estimand, **re-enters** in `HEUR-HQC-2`'s closure and the `Cov(W_1,W_2)` label. `F2a`/`F2b` can fire from covariance heterogeneity alone — which the oracle *demonstrates* is real — giving a spurious `ST-6` shutdown. | Remove it from the closure and the label. |
| **D-4** | `HEUR-HQC-4`'s formal statement inverts its own destroy-parameter direction: `Corr = −τ/(n_e−1)` is *increasing* in τ. It contradicts its own `F4` and the frozen contract. | Correct the direction. |

**D-1 and D-2 are the ones that matter most.** Each would make a *null result
uninterpretable*, and D-2 specifically would let a null **falsely confirm A17** —
the worst outcome available to this campaign. Neither is a cosmetic fix.

## 3. The rung the Coordinator wrongly foreclosed

`DEC-20260802-d94a64` D-7 retracts the claim that the ladder "has exactly two
rungs" with "no walkable path". That was an **unscoped restatement of a scoped
result**: the producer's finding holds with `p*`, `n_e`, `m` fixed — its own
text says "change nothing else".

Relaxing that, the red team found a `dup = 2` rung at
`n = 11779, ω = 62, ω_r = 70, p* = 0.388705, m = 16, n_e = 46`, costing
**2.0×10⁴ core-seconds** with `T_req = 8.16×10⁷` and `m/λ = 1.586`.

**It supplies the only matched test `HEUR-HQC-6` will ever get.** It therefore
belongs *in* the protocol unless it can be shown not to work — and BATCH-004's
job is to check it, not to accept it. The red team's arithmetic has not been
independently verified.

## 4. What BATCH-004 does and does not do

It repairs, evaluates, ships the calibration, and — **only if both reviews
admit the repaired contract** — freezes `EXP-HQC-982268` and creates
`H-HQC-18d1b4`.

**It does not run the confirmatory measurement.** `DEC-20260802-d94a64`'s next
action puts the run strictly after the freeze, and freezing is itself
conditional on review. A batch that repaired and ran in one pass would be
spending compute against a contract no independent session had yet accepted —
which is exactly what BATCH-003 refused to do.

Claim-tier ceiling stays **toy**. Nothing here is admissible toward the
AGENTS.md rule 13 closure quorum.

## 5. Batch composition

| Task | Role | Purpose |
|---|---|---|
| `TASK-20260803-04377d` | executor | Repair D-1 … D-4 in a revised specification and heuristics; rescope the ladder claim; **evaluate the `dup = 2` rung independently**. |
| `TASK-20260803-1b30d8` | executor | Write and run `calib_m0.py` / `calib_m0b.py`, list them in `required_artifacts`, and re-derive the cost model from measured constants. |
| `TASK-20260803-c9b5a2` | coordinator | Snapshot archive. Runs alone. |
| `TASK-20260803-1eec43` | validator | Verify each repair actually closes its defect; re-derive the cost model from the shipped scripts. |
| `TASK-20260803-23e232` | red-team | Attack the repairs, and specifically try to break its own `dup = 2` rung. |
| `TASK-20260803-b029f4` | coordinator | Ledger archive: `EV-HQC-97ea36`, `DEC-20260803-54bee2`, and `H-HQC-18d1b4` + `EXP-HQC-982268` **only if admitted**. |

The two producers have disjoint write scopes and no dependency: the calibration
work does not need the repaired protocol, and the repair does not need measured
machine constants to fix a mis-stated shift condition.

## 6. Standing instruction to both reviewers

A repair that *appears* to close a defect but does not is worse than the
original defect, because the second review is where it would otherwise have been
caught. Check each repair against the **counterexample that exposed it** — in
particular, D-1's fix must defeat `o_1 = 3, o_3 = 1`, and D-2's replacement
guard must be demonstrably **not** invariant under `dup`.

Four consecutive batches have had Coordinator claims corrected by review. Assume
this opening contains errors too, and read §3's arithmetic as unverified.

## 7. Repository state at open

`validate_ledger.py`: **110** errors above the grandfathered baseline —
identical on this branch and `origin/main`, so this lane contributes zero. None
names a `GOAL-HQC-001` record. All four BATCH-003 archives re-verify after the
merge from `50f73a42`.
