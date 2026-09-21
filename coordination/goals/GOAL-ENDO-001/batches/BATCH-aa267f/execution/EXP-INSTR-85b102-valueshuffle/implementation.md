# Implementation note — CTRL-VALUESHUFFLE (EXP-INSTR-85b102 amendment v2)

Deviations from the approved protocol, implementation decisions the contract
left open, and everything that surprised me. Nothing here is interpretation.

Contract: `experiments/EXP-INSTR-85b102/amendments/v2.yaml`
(`status: approved`, `approved_by: coordinator`, `approved_at: 2026-08-07`).
Runs: `RUN-INSTR-85b102-valueshuffle-gate`, `RUN-INSTR-85b102-valueshuffle`.

---

## D1 — the three declared seeds have no declared mapping onto 200 replicates

**Contract text.** `parameters_frozen.seeds: [20260807, 20260808, 11235813]`
and `parameters_frozen.replicates: 200`. The amendment does not say how the
three seeds map onto the replicates, the pools, or the functionals.

**Resolution, recorded rather than silent.** Every shuffle draws its stream
from a SHA-256 derivation that consumes **all three** declared seeds, so none
is favoured and none is unused:

```
payload = "EXP-INSTR-85b102/v2/CTRL-VALUESHUFFLE|SHUFFLE|<pool>|<functional>"
          "|<replicate>|20260807|20260808|11235813"
seed    = int.from_bytes(sha256(payload.encode("ascii")).digest(), "big") % 2**64
rng     = numpy.random.default_rng(seed)
values  = committed_values[rng.permutation(n)]
```

`harness/ctrl_valueshuffle.py::derive_shuffle_seed`. It mirrors
`run_blocknull.derive_seed`, the convention already committed for this
experiment, so a third party reproduces any single shuffle from
`(replicate, pool, functional)` alone. Verified: replicate 137 re-runs
bit-for-bit to the recorded 144-cell bitmap.

**Why this is a decision and not a defect.** Another mapping (three separate
sub-nulls, or one seed per pool) is an equally legal reading of an
under-specified field. This one is stated so the difference is visible. It was
fixed before any replicate was drawn and no alternative mapping was tried.

## D2 — two runs, not one

`RUN-INSTR-85b102-valueshuffle-gate` executes **only** the SR-B1 reproduction
gate and was committed (`2c928d99`) before a single replicate existed.
`RUN-INSTR-85b102-valueshuffle` re-runs the same gate as a blocking
precondition and then draws the null.

Reason: the dispatching Coordinator required a commit after the gate for
session survival, and the split makes the "gate strictly before any replicate"
ordering auditable from git history rather than from my word. Two runs against
`maximum_runs: 6`. The gate result is identical in both: `reproduction-gate.json`
is **byte-identical**, sha256
`0b6d69f413857d607a81f1ea2f0880acf9249a814b0ba3e910235d24d5477542`.
`frozen_function_diff.txt` differs between the two runs and is *expected* to —
its `base_ref` is `HEAD`, which advanced from `02b1e5db` to `2c928d99` when the
gate run was committed. Both read `VERDICT: ZERO BEHAVIOURAL CHANGE`, and the
frozen files are byte-identical at both refs.

## D3 — the verdict rule is restated, not imported

The frozen rule is an inline expression at `harness/run_blocknull.py:1552`
(`rises = all(b >= a - 1e-12 for a, b in zip(vals, vals[1:]))`), not a
callable, so it could not be imported without editing a frozen v1 emitter.
It is restated in `ctrl_valueshuffle.verdict_rises` and **cross-checked**: on
the full N ladder with the committed empirical ratio it agrees with the
committed `ratio_rises_monotonically_along_N_ladder` boolean in **144 of 144**
cells (36/36 at each pool).

**The vacuous `all()` is reproduced deliberately, not repaired.** `all()` over
a list shorter than 2 is True, so a cell with fewer than two defined R values
scores MONOTONE RISE on no data (OBJ-3 of RT-20260807-743198). The amendment's
`what_this_amendment_does_not_do` states that fixing it requires its own
amendment, so the rule is applied unchanged and `n_comparisons` plus a
`vacuous` flag are recorded beside every verdict. Six cells are vacuous in the
observed data and in **every one of the 200 replicates** — the same six
(`s3_support` weighted and unweighted at POOL_A, POOL_B, POOL_D, whose values
are constant across the pool, so a permutation cannot change them).

Red Team required-controls **RC-2, RC-3 and RC-4 were NOT implemented.** The
amendment "authorizes this control and nothing else."

## D4 — closed forms computed at all five ladder rungs, not just the ones used

The residue construction uses only the non-degenerate prefix of the N ladder.
The module computes the closed form at all five rungs anyway and uses the
degenerate ones as a forced-value check: at a degenerate rung every block is a
single class, so `E[T_pi | B]` must equal `T_obs` and R must be 1. Measured
`max |R - 1| = 4.44e-16` over 258 degenerate rung-cells. Extra computation,
no protocol change; it is the v1 `R5_PERCLASS` stopping-rule invariant checked
in the new code path.

## D5 — `T_obs` recomputed through the frozen scalar statistics

The v1 runs compute `T_obs` through `_Layout.observed` (the vectorized
permutation path, identity permutation). This control computes it through the
frozen `statistic_weighted` / `statistic_unweighted`, because the null needs a
`T_obs` for *shuffled* values and those are the declared scalar statistics.
The two paths differ only in float summation order. **Measured**, over all
4 × 180 = 720 committed ladder cells:

| pool | max relative deviation in `T_obs` | max relative deviation in `closed_form_null_mean` |
|---|---|---|
| POOL_A | 2.255e-16 | **0.000e+00** |
| POOL_B | 2.756e-16 | **0.000e+00** |
| POOL_C | 5.274e-16 | **0.000e+00** |
| POOL_D | 3.439e-16 | **0.000e+00** |

The closed-form null mean — the quantity the whole control turns on —
reproduces **bitwise**. `T_obs` reproduces to a few ulp, against a verdict
tolerance of 1e-12 on ratios of order 1. Recorded as a measurement, not
assumed: this is exactly the class of one-ulp difference that produced
deviation D6 of the v1 execution.

Reproduce with:

```
python3 - <<'PY'
import json, numpy as np
from harness import ctrl_valueshuffle as cv
from harness.run_blocknull import (statistic_weighted, statistic_unweighted,
                                   closed_form_null_mean)
for pl in cv.POOLS:
    v = cv.load_pool_view(pl, cv.SOURCE_RUNS[pl])
    L = json.load(open(f"experiments/EXP-INSTR-85b102/runs/{cv.SOURCE_RUNS[pl]}/results.json"))["ladder"]
    ...  # compare cell by cell against L["cells"][f"{pl}|{k}|{rung}|{stat}|B{L['B']}"]
PY
```

(the full script is 20 lines and is restated in section 9 of the execution
report; it is a read of committed files and writes nothing).

## D6 — both denominators reported; the statistic is a count

`definitions_frozen.denominator_note` requires the residue count against both
144 and 138 and a statement of which the decision rule used. Reported as
**50/144** and **50/138**. The frozen statistic is a **count**, and the null is
drawn over the identical 144-cell frame with the identical six vacuous cells
(verified: `cells_comparable == 138` in all 200 replicates), so the denominator
does not enter the p-value at all. 50 reproduces under **both**: the six-cell
difference is cells with no defined R at any rung, which cannot be in the
residue under either denominator. SR-B1 therefore does not fire on the
denominator clause.

## D7 — no permutation study, no re-measurement, no frozen function touched

`B` is not a parameter of this control. No curve was re-enumerated, no
functional re-measured, no Monte-Carlo draw taken. `harness/exp_icinv.py`,
`harness/isogeny_class.py`, `harness/run_icinv.py`, `harness/toycurve.py` and
`harness/run_blocknull.py` are unmodified (`git diff` empty against both the v1
base commit `02487c19` and `HEAD`); the regenerated CTRL-FROZEN-DIFF receipt
reads **ZERO BEHAVIOURAL CHANGE** with all eleven frozen functions UNCHANGED by
live-source hash and the declared behavioural probe re-run. All new code is in
one new file, `harness/ctrl_valueshuffle.py`.

## D8 — nothing else

No hypothesis, success criterion, protocol, prediction or frozen number was
modified. The frozen observed value 50 was **not** adjusted at any point; the
gate compares the re-derivation to it and never the reverse. No run was
repeated, discarded or rescored. No evidence record was written, no status
moved, no branch pushed, no PR opened, no `main` merged.

---

## Unexpected observations (recorded, not interpreted)

**U1 — the observed value lies below the entire null support.** Null min 89,
observed 50. The frozen rule is two-sided on `|x - median(null)|`, so it fires
without regard to direction; the direction is recorded because it is an
observation and discarding it would be a contract violation.

**U2 — the p-value is exactly at the resolution floor.** `0 of 200` replicates
were at least as extreme, so p = 1/201 = 0.004975124378109453, the smallest
value the design can produce. The reported p is the floor, not an estimate of
the true tail probability; at 200 replicates nothing smaller is resolvable.
This is the mirror image of the contract's declared asymmetry note and is
stated with the same care.

**U3 — the m = 3 family's 8-of-8 is not separated from the null.** Under the
shuffle, `sumset_m3` reaches 8 of 8 in 27 of 200 replicates and `sumset_eff_m3`
in 36 of 200. Two-sided p 0.2637 and 0.2587; one-sided upper 0.1393 and
0.1841. This quantity does **not** enter the terminal state, which the frozen
rule keys to the residue count alone.

**U4 — the N-coupled functionals lose their coupling under the shuffle, by
construction.** `order`, `full_liftable`, `liftable_density_W4001` and
`liftable_density_W6007` are in the residue 0 of 8, 0 of 8, 0 of 6 and 0 of 2
times in the observed data, and have null mean residue 6.34, 6.36, 4.78 and
1.65 under the shuffle. This is what the null object is built to do (it
destroys every value–N association) and it is recorded as a property of the
control, not as a result.
