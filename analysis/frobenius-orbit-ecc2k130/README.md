# A Frobenius orbit-union factor base at ECC2K-130: a pre-compute audit

**Status: analysis note, not evidence.** Every number here is computed by
`orbit_fb_ecc2k130.py` in this directory. **Nothing was run against the
challenge**: there is no relation search, no decomposition solve, no attack on
any instance. It is a section-8 audit in the sense of
`docs/inventor-protocol.md` — exact baseline embedding and method ceiling at
one parameter point. No `RUN-*` manifest exists for it and none is invented
(AGENTS.md rule 5); it changes no hypothesis status and supports no claim.

Target: ECC2K-130, the **public Certicom challenge curve** `y^2 + xy = x^3 + 1`
over `F_{2^131}` (`KN-LIT-096`, `KN-LIT-661e97`). The audit/instance
distinction this note relies on is the one `RQ-ICPERF-94c86e` states for the
FIPS labels: parameters appear in a cost table, never as a target.

## Ownership is unresolved, deliberately

This note is **not filed under a goal**, and that is a finding in itself:

- `GOAL-FROB-6333a9` owns the Frobenius-stable-factor-base work but excludes
  "Deployed Koblitz / ECC2K-130 as attack instances" (`scope_exclusions[0]`);
  `RQ-FROB-7d8dd4` likewise bars deployed Koblitz parameters as instances.
- `RQ-QSP-f9bbdb` is the question that *does* permit ECC2K-130 ("Lawful
  defensive cryptanalysis on the public Certicom challenge curve and toy
  curves only"), but its ideation card `TASK-20260916-a93a2a` bars the
  Frobenius-orbit lens as *the idea* there: "use it as a component (the orbit
  column of the table), never as the idea."
- `GOAL-ECDLP2M-001` names "Frobenius-orbit and subfield-orbit relation
  generation" among its mechanism families and is the natural adopter, but
  today owns only `RQ-QSP-f9bbdb`.

Adoption is a Coordinator decision and is **not** taken here.

## The question

Can a Frobenius-stable factor base be used for index calculus at the real
ECC2K-130 parameters, and does the resulting pipeline beat Pollard rho with
the Frobenius and negation classes?

## What was computed

**A — field, curve, exact order.** `F_2[z]/(z^131 + z^13 + z^2 + z + 1)`
(irreducibility checked, not assumed). The order is derived from the Koblitz
trace recursion `t_m = t_1 t_{m-1} - 2 t_{m-2}` seeded by `#E(F_2) = 4`,
`t_1 = -1` — no SEA and no recall — giving

```
#E = 2722258935367507707729280517973639940516 = 2^2 * r
r  = 680564733841876926932320129493409985129   (prime, log2 r = 129.0)
```

`r` reproduces the literal committed in `EV-ICPERF-10c5fc` exactly, the Hasse
bound holds, and the computed order annihilates random curve points.

**B — the linear stable factor base does not exist.** `F_2^131` under `sigma`
is the `F_2[X]`-module `F_2[X]/(X^131 - 1)`, so its Frobenius-stable subspaces
correspond to the monic divisors of `X^131 - 1`. Since `ord_131(2) = 130`,
that polynomial splits as `(X+1) * Phi_131` with `Phi_131` irreducible, giving
**exactly four** stable subspaces, of dimensions

```
{0, 1, 130, 131}
```

Nothing in the index-calculus band `[2, 129]`. This independently re-derives
`IDEA-20260918-9abf42` at the target parameters.

**C — the orbit union exists and was built at real scale.** With `V'` a random
`F_2`-subspace of dimension 36 and `S = union_j sigma^j(V')`: `sigma^131` is
the identity, `sigma(V')` equals the shift-1 subspace, `sigma^131(V') = V'`,
every sampled orbit has size exactly 131 (131 is prime), and the shifted
copies meet in dimension 0 — so `|S| = 2^43.03` and `pi(S) = S` genuinely
holds. The object is real and constructible at `n = 131`.

**D — the gain it earns, verified on the curve.** On a real point of exact
order `r`, the Frobenius orbit has exactly 131 points and `sigma` acts as
multiplication by

```
mu = 196511074115861092422032515080945363956,  a root of mu^2 + mu + 2 = 0 mod r
ord_r(mu) = 131,  and all 131 powers are distinct
```

So one relation yields exactly 131, and the linear algebra runs at the
orbit-reduced dimension. The gain is `2^7.03` — **exactly `n`, and no more.**

## The cost, charged against rho

Balanced factor base `|S| = 2^(131/m)`, the full factor-`n` collapse granted on
relations and `n^2` on linear algebra, and — absurdly generously — **one
operation charged per decomposition solve**. Baseline: `2^60.9` expected rho
iterations with the Frobenius and negation classes (`KN-LIT-096`; that figure
is the authors' *estimate*, and the real public effort reached about `2^58.3`
iterations, ~17%, over 22 months, per `KN-LIT-661e97`).

| m | Semaev | \|FB\| | descended `F_2` vars | solves | linear algebra | floor | budget per solve for rho parity |
|---|---|---|---|---|---|---|---|
| 2 | `S_3` | `2^65.5` | 117 | `2^59.5` | **`2^116.9`** | `2^116.9` | `2^1.4` |
| 3 | `S_4` | `2^43.7` | 110 | `2^39.2` | **`2^73.3`** | `2^73.3` | `2^21.7` |
| 4 | `S_5` | `2^32.8` | 103 | `2^30.3` | `2^51.4` | `2^51.4` | `2^30.6` |
| 5 | `S_6` | `2^26.2` | 96 | `2^26.1` | `2^38.3` | `2^38.3` | `2^34.8` |
| 6 | `S_7` | `2^21.8` | 89 | `2^24.3` | `2^29.6` | `2^29.6` | `2^36.6` |

`m = 2` and `m = 3` are dead on **linear algebra alone**, before a single
solve is charged: `2^116.9` and `2^73.3` against rho's `2^60.9`. The orbit
collapse is already included in those numbers; it is what brings them down to
there.

For `m >= 4` the bookkeeping fits under rho, and the entire question collapses
to one quantity: **a single decomposition solve must cost under about `2^31`**
(at `m = 4`; `2^30.6`). That solve is a Weil-descended Semaev system in ~103
`F_2` unknowns. The rows that look roomier are worse, not better: `m = 5` and
`m = 6` need `S_6` and `S_7`, which are not constructible at this size.

## The finding

The orbit-union factor base is the **only** Frobenius-stable factor base
available at ECC2K-130 — part B rules out every linear one — and it is
constructible (part C). What it buys is exactly the factor `n = 131` on
relations and `n^2` on linear algebra (part D): the known constant-factor
lever, which rho already answers with its own `sqrt(2n)`. No exponent moves.

Whether the pipeline is viable therefore rests entirely on the per-solve cost
of decomposition — and that is precisely the quantity this program has already
measured, at toy sizes, and found **unmoved by the orbit structure**:
`EV-FROB-b6e1e9` / `KN-FIND-47da4e` report a one-hot-over-baseline conflict
ratio of 1.02, 1.02, 1.47, 1.15 on CaDiCaL at `n = 13, 17, 19, 23` and 1.00 to
1.21 on WDSat in both search modes — never below 1, approaching 1 from above.
The orbit parameterisation relabels the work rather than removing it.

That combination lands on `RQ-FROB-7d8dd4`'s decision target (a): a gain
confined to the constant factor `n` on the factor base and `n^2` on linear
algebra, with no change in decomposition cost per attempt.

## What this does NOT claim

- **No attack, no run, no instance.** Nothing was executed against the
  challenge. There is no relation search and no solve here at any `m`.
- **The toy ratio is not a proof.** A conflict count is a property of a
  search, not of the algebra — it is not a solving degree and not a lower
  bound. A better encoding or solver could move any row of
  `KN-FIND-47da4e`, and the per-solve cost at `n = 131` has **never been
  measured**; the `2^31` budget above is the target such a measurement would
  have to beat, not a demonstration that it cannot.
- **The cost model is a model.** It grants the attack every gain and charges
  one operation per solve; it is a *floor* for this pipeline shape, not an
  achievable cost, and not a security statement about ECC2K-130.
- **`m >= 4` is not evaluated on its own terms.** Those cells are dismissed on
  summation-polynomial constructibility, which is a literature judgement
  recorded here, not something this note measured.
- **Nothing about the linear stable factor bases at rich `n`.**
  `H-FROB-a5bf86` / `EXP-FROB-30006a` test `n = 41, 43`; different object,
  different cells. This note scores none of that hypothesis's predictions.

## Reproducing

```sh
/opt/conda-sage/bin/sage -python orbit_fb_ecc2k130.py --json results.json
```

Runs in under a minute. `results.json` in this directory is that command's
output. Part C draws a random `V'`, so its subspace-level facts (all booleans
and the orbit sizes) reproduce while the particular `V'` does not; parts A, B
and D's cost sweep are fully deterministic, and part D's `mu` is determined by
the curve, not the draw.

---

# Part 2 — measuring the one unmeasured number: cost of a single decomposition solve

**Status: analysis note, not evidence — same standing as Part 1.** Everything
below was produced by `solve_cost_ladder.py`, `gf2_131_mul_bench.c` and
`collect_results.py` in this directory, inside one interactive session. **It is
not a harness run**: there is no `RUN-*` manifest and none is invented
(AGENTS.md rule 5). It changes no hypothesis status, closes nothing, and
supports no claim beyond the parameters it names.

**It is an instrument measurement, not an attack.** It prices *one decomposition
solve*. It performs no relation search, computes no discrete logarithm, and
makes **no progress whatsoever toward the ECC2K-130 challenge** — Part 1 already
shows the `m = 2` pipeline needs `2^58.5` relations and `2^116.9` linear
algebra against rho's `2^60.9`, so the cell measured here is one that the cost
model has *already* ruled out. Precedent for solver runs on this public curve:
`EV-ICPERF-10c5fc`.

Part 1 ended on a single open quantity: the per-solve cost of decomposition,
never measured above `n = 23` (`EV-FROB-b6e1e9` / `KN-FIND-47da4e`, which states
that gap itself). Part 2 pushes that measurement as far up the `n` ladder as
this machine allows, and reports exactly where it stops.

## The instrument control: `n = 23` reproduces EXACTLY

Before any new cell, the prior instrument was re-run unchanged at its recorded
cell:

```sh
python3 ../frobenius-orbit-union/frob_union_m2.py \
        --n 23 --targets 16 --seed 7 --no-linear --out logs/control_n23_repro.json
```

| quantity (15 refuted targets) | recorded `union_n23.json` | reproduced here |
|---|---|---|
| baseline conflicts (sum over `n` systems) | 99563.533 | 99563.533 |
| one-hot conflicts | 114540.667 | 114540.667 |
| **one-hot / baseline** | **1.150428** | **1.150428** |
| one-hot seconds | 31.79 | 34.71 |

**PASS.** All 16 target rows agree in **every non-timing field** — conflicts,
decisions, propagations and every SAT/UNSAT verdict are bit-identical (0
differences over all rows); only wall clock differs, this machine being about
9% slower. `python-sat` here is 1.9.dev15 against the prior work's earlier
version, and `Cadical153` (CaDiCaL 1.5.3) was chosen to match; the match is
exact, so the solver identity is confirmed rather than assumed. Everything
below is therefore reported by an instrument that reproduces the recorded
number it is being extended from.

## `S_3` is derived, not recalled

Every cell derives the third summation polynomial before using it, by fitting
the ansatz `sum_{i,j,k<=2} c_ijk x1^i x2^j x3^k` against real curve triples
with `P1 + P2 + P3 = O` on the cell's own curve, and refusing to proceed unless
the kernel is one-dimensional. At `n = 131` on `y^2 + xy = x^3 + 1` the fit
returns, from 80 samples, kernel dimension exactly 1 and support

```
S_3 = (x1 x2)^2 + (x1 x3)^2 + (x2 x3)^2 + x1 x2 x3 + 1
    = (x1 x2 + x1 x3 + x2 x3)^2 + x1 x2 x3 + b,   b = 1
```

verified on **200/200** fresh real triples (vanishes) and **200/200** random
triples (does not vanish). The Weil descent is checked the same way: the
descended `F_2` system is evaluated against field arithmetic on random
assignments — **0 mismatches** in every cell. At the toy cells exhaustive
ground truth over `V'` is retained, and the solver verdict matched it on every
target in every cell that ran it.

Field and curve at the `n = 131` cell are the real ones, re-derived per run:
modulus exponents `[131, 13, 2, 1, 0]`, `#E = 2722258935367507707729280517973639940516`,
`r = 680564733841876926932320129493409985129`, `h = 4` — identical to Part 1
and to `EV-ICPERF-10c5fc`.

## The encoding is a first-order confound, and it had to be measured

The prior instrument expands `S_3(X1, X2, c)` symbolically over `F_{2^n}` and
descends it (`direct`). In the one-hot arm that costs `l'^2 * n` cubic
monomials — at `n = 131`, `58^2 * 131 = 440684` monomials, whose XOR chains do
not fit in memory. So `n = 131` forces intermediate `F_2` variable vectors:

- `stagew` — stage `w = x2` only (`n` bits); `x1 * x2` stays a direct quadratic
  ANF in `{t_a, w_i}`.
- `staged` — stage both `w = x2` and `p = x1 * x2`.

Both are correct and both are far worse for CDCL. Measured at `n = 19`, 4
targets, same subspace and targets throughout (`logs/enc_n19_*.json`):

| encoding | branching order | baseline conflicts | one-hot conflicts | ratio | one-hot CNF (vars/clauses) |
|---|---|---|---|---|---|
| direct | default | 4566 | 7080 | **1.55** | 6075 / 24300 |
| direct | shift-first | 4566 | 6292 | **1.38** | 6075 / 24300 |
| stagew | default | 18688 | 863213 | 46.19 | 2217 / 8735 |
| stagew | shift-first | 18688 | 437314 | 23.40 | 2217 / 8735 |
| staged | default | 32067 | 784364 | 24.46 | 2231 / 8753 |
| staged | shift-first | 32067 | 1592267 | 49.65 | 2231 / 8753 |

Three things follow, and all three matter for reading the `n = 131` row:

1. **Staging costs one to two orders of magnitude.** The encoding that makes
   `n = 131` buildable is ~60x worse in one-hot conflicts at `n = 19`. The
   `n = 131` numbers are therefore **not comparable to the `direct` ladder**,
   and are an upper bound for the encoding used, not a property of the algebra.
2. **A smaller CNF is not a cheaper solve.** The staged CNFs are 3x *smaller*
   and 60–200x *harder*. Clause count is not a cost model here.
3. **The shift-bit branching prefix is not uniformly good.** It helps `direct`
   (1.55 -> 1.38) and `stagew` (46.2 -> 23.4) and **hurts** `staged`
   (24.5 -> 49.7). The prefix is realised here as variable renumbering (the
   shift bits take the lowest indices), which is a weaker instrument than
   WDSat's `-g`: `python-sat` exposes no decision-priority API for CaDiCaL.

## The ladder

`direct` encoding, shift-first order, fresh random `V'` per cell,
`l' = ceil(n/2) - ceil(log2 n)` as in the prior instrument. Ratios are one-hot
conflicts over the summed `n`-system baseline, on refuted targets.

| n | l' | log2 \|S\| | baseline conflicts | one-hot conflicts | ratio | source |
|---|---|---|---|---|---|---|
| 13 | 3 | 6.5 | 166.9 | 169.7 | 1.017 | prior `EV-FROB-b6e1e9` |
| 17 | 4 | 8.0 | 950.4 | 966.2 | 1.017 | prior |
| 19 | 5 | 9.2 | 4773.3 | 7001.4 | 1.467 | prior |
| 19 | 5 | 9.2 | 4566 | 6292 | 1.38 | here, fresh `V'`, shift-first |
| 23 | 7 | 11.5 | 99563.5 | 114540.7 | **1.150** | prior, **reproduced exactly here** |
| 29 | 9 | 13.9 | — | — | — | **did not complete** (below) |
| 31 | 10 | 14.9 | — | — | — | **did not complete** (below) |
| 131 | 58 | 65.0 | censored | censored | — | ECC2K-130 cell (below) |

**`n = 29` did not complete, and that is the honest top of the ladder.** The
cell was launched with a `4 * 10^6` conflict budget per solve and a 2400 s cell
wall; the baseline arm finished, and the single one-hot solve was still running
after **62 minutes of CPU** without reaching its budget, so no target row was
emitted (final accounting in `logs/incomplete_cells.json`). A conflict budget is the only censoring mechanism available:
`Cadical153.interrupt()` raises `NotImplementedError` in `python-sat`
1.9.dev15, so a per-solve wall clock cannot be imposed on this solver, and the
instrument now **refuses** `--solve-wall` rather than silently ignoring it.
This is a resource outcome and is **not** negative mathematical evidence
(AGENTS.md rule 3). The reachable range of this instrument with complete
ratios is thus still `n <= 23` — the gap `KN-FIND-47da4e` declared is narrowed
in scale but not closed.

**`n = 31` did not complete either, the same way.** Launched alongside the
rest, it was stopped during review after **1h40m of CPU**, still inside the
*single* one-hot solve for target 0 and still short of the same `4 * 10^6`
conflict budget — the baseline arm had finished, and a stack dump put it in
`build_and_solve -> solve_limited`. No `cell_n31.json` was emitted, so nothing
is reported for it beyond the cost accounting in `logs/incomplete_cells.json`.
Two cells failing identically at `n = 29` and `n = 31`, both inside one
uninterruptible solve, is the clearest statement of this instrument's ceiling:
what stops the ladder is not the algebra and not memory, but that
`Cadical153` cannot be interrupted and a conflict budget of `4 * 10^6` is
already too coarse a censor at these sizes.

## The `n = 131` ECC2K-130 cell

Real curve, real field, `l' = 58`, `|S| = 2^65.0`, planted decomposition so
that a satisfying assignment provably exists, one-hot arm in `stagew`, baseline
arm in `direct`, baseline sampled at `j = 45` (`logs/cell_n131_smallbudget.json`).

| | baseline (one gauge-fixed system) | one-hot (all 131 shifts) |
|---|---|---|
| CNF variables | 231151 | 1024605 |
| CNF clauses | 921038 | 4090753 |
| build time | 0.83 s | 4.84 s |
| conflicts at cutoff | 501 (budget) | 501 (budget) |
| seconds for those conflicts | 1.86 | 10.14 |
| propagations | 2.09e7 | 6.69e7 |
| conflict rate | 270 /s | 49 /s |
| verdict | **censored** | **censored** |

Peak resident memory for the whole cell: **645 MiB**, well inside the 8 GiB
cap. The cell wall was 46 s.

So the object is real and the instance is buildable and runnable at the true
ECC2K-130 parameters — but **neither arm terminated**, at any budget reached
here. A second cell with a 20000-conflict budget was also run and
**did not complete**: after 36 minutes of CPU it was still inside the baseline
arm, having not reached 20000 conflicts on a single gauge-fixed system. It is
recorded as non-completing, with its cost accounting, in
`logs/incomplete_cells.json` and in `solve-cost-results.json`; nothing is
reported from it beyond that. Two rules bind how this is read:

- **No UNSAT at `n = 131` is ground truth.** Exhaustive enumeration over `V'`
  is `2^58` and was not attempted; the instrument sets `ground_truth: false`
  for this cell and asserts nothing. Any UNSAT here would be
  **solver-asserted and uncertified**. The planted construction is what makes a
  *positive* answer certifiable: every SAT model at every cell is re-decoded and
  re-checked against `S_3`, against `x1 in V'` and against `x2 in S` before it
  counts, and the staged `w` vector is cross-checked against the decoded `x2`.
  No SAT model was returned at `n = 131`, so no certificate is claimed.
- **Censoring is a resource outcome.** It bounds the cost from below and says
  nothing about solvability.

## Conflicts to field operations: the conversion, stated in the open

The Part 1 budgets (`2^1.43` per solve at `m = 2`, `2^30.6` at `m = 4`) are in
`F_{2^131}` operations; solver work is in conflicts. The conversion is an
assumption and is numbered so it can be attacked:

> **Assumption C1 (unit).** Solver work is counted in CaDiCaL *conflicts*,
> which are deterministic for a fixed CNF and solver — this is why the control
> above reproduces bit-exactly, and it is the unit the prior work reports.
>
> **Assumption C2 (conversion).** One `F_{2^131}` multiplication costs
> **23.55 ns** on this machine, measured — not assumed — by
> `gf2_131_mul_bench.c` (PCLMULQDQ 3x3 schoolbook plus sparse reduction mod
> `z^131+z^13+z^2+z+1`; median of five runs of `2*10^7` multiplications; 23.53 /
> 23.63 / 24.49 ns spread; 49.5 cycles at the nominal 2.1 GHz). Its correctness
> is cross-checked by `check_mul_bench.py` against the same Python
> `GF(2^131)` the measurement instrument uses. Solver work is then converted by
> **measured seconds on the same machine**: `field_ops = t_solve / 23.55 ns`.
>
> **Why this direction is conservative.** The benchmark is a dependent chain,
> so it is latency-bound and is the *slowest* reasonable optimised multiplier;
> a pipelined one (~5–8 ns) would multiply every field-op figure below by 3–5.
> C2 therefore **understates** the cost of a solve. It also charges the solver
> nothing for its own memory traffic beyond elapsed time.

Applying C2 to the measured rows:

| measured quantity | measured | converted (modelled via C2) |
|---|---|---|
| one conflict, `n = 131` one-hot | 20.24 ms | 8.6e5 field ops = `2^19.7` |
| one conflict, `n = 131` baseline system | 3.71 ms | 1.6e5 field ops = `2^17.3` |
| building the `n = 131` one-hot CNF | 4.84 s | `2^27.6` field ops |
| 501 conflicts, `n = 131` one-hot, **not terminated** | 10.14 s | **> `2^28.7` field ops** |
| `n = 23` baseline, complete solve (16 targets) | 2.20 s | `2^26.5` field ops |

**What that does and does not license.**

- Against the `m = 2` budget of `2^1.43 ≈ 2.7` field operations per solve: the
  measurement clears nothing. A single `n = 131` solve had already spent more
  than `2^28.7` field operations *without finishing*, and merely **constructing**
  the instance costs `2^27.6`. The miss is by more than `2^27`, and the same
  miss is already visible at `n = 23` (`2^26.5` for a complete solve). This
  does not rescue or change Part 1's verdict on `m = 2`, which was decided on
  linear algebra (`2^116.9`) before any solve was charged.
- Against the `m = 4` budget of `2^30.6`: **not measured, and not claimed.**
  `m = 4` is a different system — `S_5`, ~103 `F_2` unknowns, a different
  factor base — and nothing here was run at `m = 4`. The `m = 2` figure exceeds
  `2^30.6` in trend but that is an observation about a different cell.
- If C2 is rejected, the raw numbers stand on their own and the comparison is
  simply **not available**: 501 conflicts / 10.14 s / 4.09e6 clauses,
  non-terminating.

## Wall clock, memory, budget

Advisory budget 4 hours, single worker per cell, memory cap 8 GiB. Observed:
about 3.8 hours, peak resident memory **645 MiB** in the heaviest
cell (`n = 131` one-hot, 4.09e6 clauses), never above 2 GiB across all
concurrent cells. Some cells ran two or three at a time on a 4-core machine;
that perturbs **seconds** and not **conflicts**, which are deterministic — and
it is why the control is reported on conflicts, where it is exact.

## What Part 2 does NOT claim

- **No attack and no progress toward the challenge.** No relation search, no
  discrete logarithm, no certificate of any solve. The `m = 2` cell measured
  here is one Part 1 already priced out at `2^116.9` linear algebra.
- **Nothing is validated or refuted about the orbit-union heuristic.** The
  numbers are observations; whether they support or undercut anything is a
  Reviewer and Coordinator judgement, not this note's.
- **The ladder did not reach `n = 131` with a complete ratio, or even `n = 29`.**
  The largest `n` with a complete one-hot/baseline ratio is still 23. Every
  incomplete cell is reported as incomplete with its cost accounting.
- **No UNSAT at `n = 131` is ground truth**, and none is asserted; exhaustive
  ground truth stops at `l' <= 16`.
- **The `n = 131` ratio is an encoding artefact if read as algebra.** The
  measured 23x–200x staging penalty at `n = 19` bounds how much of any large-`n`
  ratio belongs to the CNF rather than the mathematics.
- **A conflict is not a solving degree and not a lower bound on the algebra.**
  A better encoding, a better solver, or an algebraic method (Groebner, WDSat's
  XORGAUSS) could move every row here. WDSat was not built for this pass.
- **C2 is an assumption, not a measurement of the attack.** It converts elapsed
  solver time to field operations on one machine; it is not a cost model for
  any implementation an adversary would write.
- **Nothing here scores `H-FROB-a5bf86` / `EXP-FROB-30006a`** or any other
  hypothesis, and no ledger record was written.

## Reproducing Part 2

```sh
# 0. instrument control -- must reproduce 1.150428 on conflicts, exactly
python3 ../frobenius-orbit-union/frob_union_m2.py \
        --n 23 --targets 16 --seed 7 --no-linear --out logs/control_n23_repro.json

# 1. field-operation denominator for assumption C2
gcc -O3 -mpclmul -msse4.1 -o gf2_131_mul_bench gf2_131_mul_bench.c
./gf2_131_mul_bench --selftest | python3 check_mul_bench.py     # correctness
./gf2_131_mul_bench 20000000                                    # ns per multiply

# 2. encoding / branching-order confound at n = 19
sh run_encoding_confound.sh

# 3. the ladder (direct encoding, shift-first order)
sh run_ladder.sh

# 4. the real ECC2K-130 cell
sh run_131_probe.sh      # small budget: always completes, gives rates and sizes
sh run_131.sh            # larger budget

# 5. index the raw per-cell outputs
python3 collect_results.py                  # writes solve-cost-results.json
```

Raw per-target rows live in `logs/cell_*.json` and `logs/enc_*.json`;
`solve-cost-results.json` indexes them with their sha256. Each cell draws its
own random `V'`, generator and targets from its `--seed`, so a rerun with the
same seed reproduces that cell exactly, and the derived `S_3`, the modulus, the
curve order and `r` are determined by the parameters rather than the draw.

---

## Concurrent work that bears on this note

Two PRs opened by other sessions the same day overlap this note directly, and
recording them is cheaper than two lanes spending budget on the same object
without knowing it — the failure mode CLAUDE.md's concurrency section exists to
prevent.

**Status, stated precisely because it changed while this section was being
written.** `PR #1360` **merged to `main` on 2026-09-22**, so
`EXP-FROB-ec08b5`, `EXP-ICPERF-783e9e`, `EV-FROB-d336b0`, `EV-ICPERF-784b25`
and `DEC-20260922-925da8` are committed records, not proposals. Merged is not
reviewed: that PR's own text records independent `validator` and `red-team`
passes as still outstanding, and caps its strength at `strong` (FROB) and
`moderate` (ICPERF) for declared model-dependence. `PR #1361` — which opens
`BATCH-5286b0` on `GOAL-FROB-6333a9` — was still open, its
`coordination/review/frob-20260922-5286b0` and `DEC-20260922-f4d910` not yet on
`main`. Read the current state rather than this paragraph.

**`EXP-FROB-ec08b5` (merged)** designs `IDEA-20260918-9abf42`, the same idea
Part 1 re-derives, and reaches the same structural conclusion from the module
side with far more generality. It reports the stable subspaces as the ideals of
`F_q[T]/(T^n - 1)`, availability decided by `ord_n(q)` alone, exactly four
stable subspaces of dimensions `0, 1, n-1, n` at `n = 131` **and** at
`n = 163`, and the orbit gain exactly `n` and never more — verified on 14 curve
cells. Part 1 here reaches the `n = 131` case independently and on the real
curve; that is corroboration from a different direction, not novelty on this
note's part. It also costs the ECC2K-130 net loss across `m` at 57 to 122 bits,
which this note does not do.

**`EXP-ICPERF-783e9e` (merged)** bears on the question Part 1 left open and
Part 2 failed to measure. Part 1 reduced viability at `m >= 4` to a single
unmeasured number — the per-solve budget of about `2^31` — and Part 2 could not
reach it. That PR argues the binding constraint at this degree is not the solve
at all: forming the descended system for one target costs about
`C(n, m(m-1))`, which it puts at **+40.8 bits over the whole per-decomposition
budget at `n = 131`**. If that holds, the `2^31` target is unreachable for a
reason this note's framing understates, because it charges a cost paid *before*
the solver is called.

Part 2's own measurement is an empirical instance of exactly that mechanism and
was read that way only in hindsight: **building** the `n = 131` one-hot CNF cost
4.84 s = `2^27.6` field operations, against a `2^1.43` budget at `m = 2` — the
instance construction alone overran the budget by more than `2^26`, before a
single conflict. This note reported that number without recognising it as the
general obstruction.

**`PR #1361`** opens `BATCH-5286b0` on `GOAL-FROB-6333a9` and composes
`EV-FROB-b6e1e9` and the promotion gate on `KN-FIND-47da4e` — the two records
Part 2 extends. Anyone acting on this note should read the state of that batch
first, and the ownership question in Part 1's header should be re-asked against
whatever those PRs settle rather than answered from this note alone. With
`EXP-FROB-ec08b5` now merged under `GOAL-FROB-6333a9`'s own question, the
likeliest resolution is that this note's subject already has an owner and this
directory should be superseded by, or folded into, that lane rather than
adopted on its own.

---

## Coordinator ruling, 2026-09-22 (appended; nothing above is edited)

**`DEC-20260922-61cdc1`** rules the ownership question this note left open.
Read that record. It supersedes the "likeliest resolution" guess in the
paragraph above, which was written before `RQ-CERTBIN-836ce2` existed.

- **Owner: `RQ-CERTBIN-836ce2`.** This directory is a **pre-compute artifact**
  of that question: a section-8 audit plus a single-session instrument probe.
  Future CERTBIN contracts reuse it by reference and say what they add.
  CERTBIN admits ECC2K-130 as an instance, with the challenges as declared
  endpoints. It also names Frobenius-stable and orbit-aware `V` as a
  factor-base choice. `GOAL-FROB-6333a9` and `RQ-FROB-7d8dd4` exclude both.
- **Not folded into `EXP-FROB-ec08b5`.** That contract covers Part 1 section B
  only. Its frozen scope is the linear Gaudry/Diem `F_V` family, and it
  explicitly excludes decomposition cost. So the orbit union (C, D), the
  charged floor table and all of Part 2 fall outside it. It is
  cross-referenced, not an owner.
- **Still not evidence.** No `RUN-*` exists and none is created. No status
  moves. No completion criterion is discharged, including
  `GOAL-FROB-6333a9` C1/C2. The sentence above placing this note on
  `RQ-FROB-7d8dd4`'s target (a) is **not** adopted as a ruling on that
  question.
- **Pending:** attaching `RQ-CERTBIN-836ce2` to `GOAL-ECDLP2M-001` is a named
  next action (NA-2), not done here.
