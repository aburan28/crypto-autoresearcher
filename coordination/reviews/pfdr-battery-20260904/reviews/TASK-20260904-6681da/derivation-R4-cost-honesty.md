# Derivation note R4 — concrete-cost honesty, cost-unit bookkeeping and scope

Task TASK-20260904-6681da (Red Team), joint R4. Audit of
`experiments/EXP-PFDR-c04716/runs/STATIC-001/concrete-cost.yaml` against
`docs/evidence-and-reproducibility.md` "Concrete-cost estimation artifacts",
`docs/target-result-profile.md` A8 / C13–C15, and red-team exemplar challenges
4–7 of `agents/red-team.md`. Numbers: `rt_cost_recheck.py` (`R4`),
`rt_r4_extras.py`, `rt_support_size.py`.

## A. What the artifact gets right (checked, not assumed)

1. **Labelling and conditionality.** `bound_kind: heuristic_estimate`,
   `value_kind: estimate (derived)` on every one of the 54 parameter sets, the
   qualifier "assuming HEUR-001" and the `(D_0, omega)` tags in every cell name,
   `conditionality` stating that unconditionally the block claims nothing. No
   cell appears anywhere in the package without its tags. Invalidation rules 2
   and 4 are respected.
2. **Both omega on every cell**; memory as a first-class column on every cell;
   `prior_time_log2` and `prior_memory_log2` on every cell.
3. **Total expected cost, not per-attempt cost.** I re-derived the balance:
   relations needed `~B`, per-target success probability `P = B^m/(m! N)`,
   oracle calls `B/P = m! N B^{1-m}`, collection cost `m! 2^m C N / B^{m-1}`,
   set equal to the `B^2` linear algebra gives `B^{m+1} = m! 2^m C N` and
   `T = 2 B^2` — the frozen formula. **The inverse success probability is in the
   total; it is not silently set to 1.** The apparent `2^m` clash between (A)
   ("probability `B^m/(m! N)`, `2^m` filtering charged") and HEUR-003 ("yield
   `2^m B^m/(m! N)` with half of interval solutions on curve") is coherent:
   `2^m` sign choices times `(1/2)^m` on-curve fraction is 1, so the net
   probability is `B^m/(m! N)` and the `2^m` appears once, as a cost.
4. **`dominated_by` is not null and not a headline-only comparison.** It states
   that rho dominates every cell unconditionally, and conditionally dominates
   every cell on memory and every safe-scope cell on time. Memory is not
   quietly dropped: `no cell dominates rho on memory` appears in the artifact
   and in `H-PFDR-06fd60`'s interpretation limits.
5. **Eight optimistic assumptions with an explicit bias direction each, plus
   two over-estimating factors**, including the two that matter most (HEUR-001
   itself, and "bounded last fall implies bounded solve … Huang–Kosters–Yeo
   RECALLED, pointer only, not opened").

## B. Findings

### B1. Declared unit versus the unit of the prior — three cells and one frozen threshold flip

`cost_unit: "F_p field operations (log2)"`, but `prior_time_log2 = 127.8254` is
`log2(0.886 sqrt N)` in **elliptic-curve group operations**
(`H-PFDR-06fd60.asymptotic_claim.prior_best`: "0.886 N^{1/2} group
operations"). `time_minus_prior_log2` subtracts the two directly. The
requirement in `docs/evidence-and-reproducibility.md` is explicit: the previous
best method must be "reported in the same units for comparison".

One group operation costs at least two `F_p` multiplications under any
addition formula (affine: an inversion plus 2–3 multiplications; Jacobian:
11–16). I do not need a precise constant: any conversion factor `>= 2` flips
every cell whose tabulated margin is below 1 in log2.

| cell | `T - rho` as tabulated | flips once a group op costs more than … field ops | flips under any honest conversion? |
|---|---|---|---|
| 256, m 4, D_0 4, omega 2 | +0.914 | 1.88 | **yes** |
| 256, m 5, D_0 6, omega 2.807 | +0.226 | 1.17 | **yes** |
| 128, m 5, D_0 4, omega 2 | +0.219 | 1.16 | **yes** |
| 256, m 4, D_0 6, omega 2 | +10.248 | 1216 | no |

Consequences, all within the artifact's own model: (i) `affected_scope` grows
from 4 cells to 7; (ii) three entries of `safe_scope` are not safe; (iii) the
frozen threshold row "(m 4, omega 2) at 256 bits: `T >= rho` at `D_0 = 4`", which
the package reports as matching the prediction "below 4", becomes `T < rho` at
`D_0 = 4`, i.e. the bracket moves to "between 4 and 6". **A threshold bracket
that moves under the artifact's own declared unit is a cost-model defect, not a
rounding question.** Direction of the bias: the mismatch makes the new route
look *worse*, so the artifact is conservative — but it is conservative by an
undeclared amount at exactly the cells where the verdict is decided.

### B2. The memory column omits the working set of the solve it prices

`memory_log2` is `s` (the factor base `B`) at every cell. The priced object is a
`Ncols(n, D_0)`-column Macaulay matrix solved at cost `Ncols^omega`; with
`omega in {2, 2.807}` — dense fast linear algebra, which the artifact itself
says is the reading (`omega = 2 is not achievable for structured sparse
Macaulay matrices`) — the working set is `Ncols(n, D_0)^2`:

| cell | tabulated memory `log2 B` | `log2 Ncols(n, D_0)` | dense working set `log2 Ncols^2` | exceeds tabulated memory by |
|---|---|---|---|---|
| 256, m 5, D_0 4, omega 2 | 53.88 | 27.69 | 55.38 | +1.50 |
| 256, m 5, D_0 4, omega 2.807 | 57.80 | 28.11 | 56.21 | — |
| 256, m 5, D_0 6, omega 2 | 57.82 | 39.51 | 79.03 | **+21.20** |
| 256, m 5, D_0 8, omega 2 | 61.57 | 50.74 | 101.48 | **+39.92** |

At three of the four cells the artifact declares "affected", the memory number
understates the model's own requirement by up to `2^40`. The escape is the
over-estimating factor already listed ("a sparse XL/Wiedemann charge
`nnz x Ncols` would be lower than `Ncols^2`") — but that reading is
incompatible with charging `Ncols^omega` for the time, and the artifact does
not say which of the two it means. **Memory is a first-class number in the
requirements; here it is the factor base only, and the solver's own memory is
neither tabulated nor flagged.**

### B3. The generator cannot be written down at the cells that carry the claim

Flagged assumption 6 says no cost is charged "for building the Macaulay matrix,
or for constructing the summation polynomial `S_{m+1}`". The flag has no
magnitude. Supplying one (`rt_support_size.py`): the top-degree part of the
reduced generator `S~` has exactly `binom(s, 2^{m-1})^m` nonzero terms (note R1
step 3 — distinct block multidegrees cannot cancel), a lower bound on the cost
of writing `S~` down at all, hence on the cost of forming a single Macaulay row:

| cell | `s` | `log2` #terms in `S~`'s top part | tabulated `log2 T` for the **whole attack** | excess |
|---|---|---|---|---|
| 256, m 3, D_0 4, omega 2 | 79 | 61.56 | 158.75 | −97.19 |
| 256, m 4, D_0 4, omega 2 | 64 | 128.17 | 128.74 | −0.57 |
| **256, m 5, D_0 4, omega 2** | 54 | **221.31** | **108.76** | **+112.55** |
| 256, m 5, D_0 4, omega 2.807 | 58 | 230.92 | 116.60 | +114.32 |
| 256, m 5, D_0 6, omega 2 | 58 | 230.92 | 116.64 | +114.28 |
| 256, m 5, D_0 8, omega 2 | 62 | 239.79 | 124.13 | +115.66 |
| 128, m 5, D_0 4, omega 2 | 32 | 145.81 | 64.04 | +81.77 |
| 64, m 5, D_0 4, omega 2 | 20 | 61.21 | 40.94 | +20.27 |

**Every cell the artifact lists as affected requires writing an object with at
least `2^{221}` terms, `2^{112}` times its own total claimed cost, and this is
independent of HEUR-001, of `D_0` and of omega.** An "assumption flagged
without a magnitude" whose magnitude exceeds the headline is not a caveat.
(At m = 3 and m = 4 the same charge is below or at the cell's total, so this
finding is specific to the m = 5 rows — which are the only sub-rho rows.)

### B4. The time–memory interpolation exists inside the model and is not drawn

`time_memory_tradeoff` says "arity m is the only knob" and that no
van Oorschot–Wiener style interpolation to `O(1)` memory exists. The second
half is right (every member of the family stores a size-`B` factor base and a
`B x B` relation matrix, so no member reaches polynomial memory, and rho owns
the whole low-memory regime). But a tradeoff *curve* does exist inside the model
and is the one the requirements ask for: choosing `B` below the balance gives
`time = m! 2^m C N / B^{m-1}` at `memory = B`. Its crossing with rho
(`rt_r4_extras.py`, 256 bits, conditional on HEUR-001):

| cell | balanced memory `log2 B` | minimum memory at which the route still matches rho on time |
|---|---|---|
| m 5, D_0 4, omega 2 | 53.88 | **48.87** |
| m 5, D_0 4, omega 2.807 | 57.80 | 54.74 |
| m 5, D_0 6, omega 2 | 57.82 | 54.78 |
| m 5, D_0 8, omega 2 | 61.57 | 60.39 |

So even conditionally the advantage lives in a memory window of 1.2–5.0 bits
above a hard floor of `2^48.9`; below it, rho wins on both axes. That is the
sentence the artifact should carry, and it is stronger and more useful than
"arity m is the only knob".

### B5. Standardized sizes

The requirements name `log2 p ~ 256 / 384 / 512` plus a larger size; the frozen
grid is 64 / 128 / 256, so the two sizes where the claim would look strongest
are absent (`rt_r4_extras.py`: m = 5, `D_0` 4, omega 2: `T - rho` = −19.06 at
256, **−39.08** at 384, **−59.43** at 512). The omission is conservative for
the claim, and it is a gap against the doc, not against the contract, which
froze 64/128/256.

### B6. Scope statements

- `affected_scope`: "NONE unconditionally" is correct and well stated. The
  conditional list of 4 cells is not licensed even conditionally once note R1
  is applied — HEUR-001 with `D_0 in {4,6,8}` cannot hold at m in {3,4,5},
  because `d_lf >= d_ff >= delta + 1 = 81` at m = 5 — so the conditional scope
  is empty for a reason internal to the presentation, not merely unmeasured.
  It is also unstable under B1 (grows to 7 cells) and refuted at m = 5 by B3
  independently of HEUR-001.
- `safe_scope`: the entry "m = 3 at every N: `T >= 2^{3.79} N^{1/2}` … by
  arithmetic" is the only unconditional-in-`D_0` statement in the block and it
  checks out (`C >= 1` gives the exponent `1/2` with that constant). Three
  other entries are unit-dependent (B1).
- The `S_6` instrument gap (`KN-OPEN-5b3a08`) is named in the contract's
  `CTRL-CONFOUNDERS-NAMED (iv)` and in optimistic assumption 6, correctly.

## C. Cost-model challenges that do NOT stand

- "Probability set to 1": no (A3 above).
- "Single-omega numbers": no; both columns everywhere.
- "`dominated_by: null`": no; it is filled and correctly signed.
- "Parallelism omitted": no; stated for both the route and rho.
