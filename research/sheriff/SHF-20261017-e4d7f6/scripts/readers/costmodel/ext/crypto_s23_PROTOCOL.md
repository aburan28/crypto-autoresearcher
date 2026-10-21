# Ledger §23 protocol: one unseen point, online and cold

Declared 2026-09-30, before any run below. What ran first:
- `predict.py` computed `prediction.json` from frozen files.
- The engineering commit `bdbe1136` was tested:
  - the one-lane rho reproduces batch rho at `k = 1`;
  - the online phases sum exactly to their interval;
  - one claim, assembled from a report, passed the checker.
- Smoke runs went to scratch space: `icv1-f2m47-t22705043-f4e44623` targets `T01`–`T02`
  through the harness, and `icv1-f2m41-tm2308219-7f48b14a` target `T01` through the
  pricer. Their numbers are not quoted and do not enter the record. The
  round runs those targets again like every other.
- A pin: the batch pricer at `icv1-f2m41-tm2308219-7f48b14a` `M1` gave §22's counts and
  logarithms.

## Why §23 is declared again

- **The rule changed.** AGENTS.md's IC measurement rules (#1076,
  `e1020dc6`) make the primary comparison one previously unseen target:
  - the index calculus and Pollard rho on that same point, in one
    resource envelope;
  - each timed from its first target-dependent operation to a verified
    scalar;
  - reusable setup reported apart.

  Multi-target results, including every `k = 32` ratio on the page,
  become historical diagnostics.
- **§23 was first declared at `k = 32`** (#1080's first commit,
  `b24b5313`, `research/ic_exponent_top_20260930/`). Nothing of it ran.
  Its primary figure was a ratio to batch rho at `k = 32`, which the rule
  bars as a headline. It is withdrawn, and its files are kept as the
  record.
- **This declaration keeps its six sizes.** It makes §23 the thread's
  first single-target round.

## Question

For one public point on each of the six Koblitz curves the library can
build with `r ≥ 2^36`:

1. **Online:** what does the index calculus's target-dependent work
   cost, against rho on the same point?
2. **Cold:** what does the whole method cost for that one point,
   reusable setup included, against rho's?
3. **Growth:** how do both grow from `2^36.6` to `2^47.2`?

## The arms

Both arms run in one process, `ic price --single-target` at `bdbe1136`'s
code, on one thread. Each repetition rebuilds both from nothing, the
index calculus first.

**The index calculus**
- **Reusable setup:** everything before the target, on §20's exclusive
  clock. That is select, build, collection, the linear algebra and the
  descent's solver.
- **Online interval:** from the descent's first query to the logarithm
  it has checked as `[d]G = Q` on the single-word ladder.
- **Phases:** the measurement session (`ic_measurement`) splits the
  interval into five exclusive phases that sum to it to the nanosecond:
  `target_query`, `target_PDP`, `target_relation_check`,
  `target_descent` and `target_recovery_check`.

**Rho** is `ParallelRho`. It is the tuned signed-Frobenius walk of
§18–§19, with its walks stepped in lockstep so that a round's additions
share one inversion.
- **Lanes:** the largest power of two up to `E/1024`, capped at 64, for
  a floor of `E = √(πr/4n)` steps.
- **Distinguished points:** `round(½·log₂(E/lanes))` bits.
- **Reusable setup:** its jump table, `[c_j]G`.
- **Online interval:** from lifting the target to the logarithm it has
  checked as `[d]G = Q`.
- With one lane it is §19's batch walk at `k = 1`, operation for
  operation (a test).

**The replay** checks `[d]G = Q` in the general arithmetic for both arms,
after their intervals close.
- It is timed on its own and reported beside the row, as the rule allows
  for a replay outside the interval.
- Each arm's answer is also a certificate with a SHA-256. `claims.py`
  replays it outside the process, in the independent checker `oracle.py`.

## Boundaries, stated before measuring

- **Floor.** One target, a generic algorithm, no precomputation:
  `√(π/4n)` steps per `√r`.
- **Reference (primary, the rule's).** One-target rho on the same point,
  measured.
- **Model reference (secondary).** This keeps continuity with
  §19–§22.
  - The price is rho's counted walk operations at the canonical step:
    one batched addition plus the table canonicalisation, priced in the
    same process.
  - The walk as built costs more a step:
    - 4.1–4.8 units at `n = 41` and `47` in the declaration's probes,
      against the canonical step's 2.3;
    - the probes' cache and branch simulation puts the gap in
      mispredicted branches and cache misses in the canonicalisation,
      and in the walk's own bookkeeping;
    - the canonical step is timed over a fixed set of 1,024 points, whose
      branches a predictor can partly learn.
  - **So the measured speedup is the upper reading and the model's is
    the conservative one.** Both are reported. Neither is quoted
    without the other.
- **The precomputation boundary (a model).** The online interval leaves
  out the index calculus's setup, and a generic algorithm could use a
  setup too.
  - Bernstein and Lange (2012): a walk that spends `P` steps building a
    table of distinguished points solves a new target in `O` steps, with
    `O·P ≈ 1.93·1.21·r/A`.
  - With `A = 2n`, and `P` the index calculus's own measured setup
    converted at the canonical step `c`, that online cost is
    `2.335·r·c²/(2n·P)` units.
  - This round measures no such walk. The rule bars it as the one-target
    reference, and multi-target work is a separate question. It is
    reported as the boundary that the online speedup must be read
    against.

## Sizes

Every Koblitz curve with `n ≤ 63` and `r ≥ 2^36`. The records are
`curve_records.json` and `curve_ids.json`, as in the withdrawn
declaration.

| curve | `log₂ r` | `r` | model | proper intermediate subfields over `GF(2)` | `ord_n(2)` |
|:--|--:|--:|:--|:--|--:|
| `icv1-f2m47-t22705043-f4e44623` | 36.6 | 106,781,081,677 | `E_1` | none | 23 |
| `icv1-f2m57-tm747311035-c1f545af` | 38.0 | 275,295,876,199 | `E_0` | `GF(2^3)`, `GF(2^19)` | — |
| `icv1-f2m41-tm2308219-7f48b14a` | 39.0 | 549,756,390,943 | `E_0` | none | 20 |
| `icv1-f2m53-tm56619371-dac20a85` | 44.3 | 21,044,858,204,113 | `E_0` | none | 52 |
| `icv1-f2m59-tm943548413-98844ecc` | 44.5 | 25,179,555,920,633 | `E_1` | none | 58 |
| `icv1-f2m61-t158598901-ab42b6c5` | 47.2 | 162,888,033,982,417 | `E_0` | none | 60 |

- `E_0` is the ECC2K-130 family; `E_1` is a different Koblitz model
  (AGENTS.md §8b).
- The method's base is Frobenius orbits of subgroup points. It uses no
  subfield and no invariant linear subspace, so the split cyclotomic
  blocks at `n = 41` and `47` enter no argument here.

## Recipe

§20's rules (`research/ic_exponent_20260926/make_params.py`), with
recipe seed 201. No recipe is chosen or changed on a measurement:

| curve | columns | descent summands | source |
|:--|--:|--:|:--|
| `icv1-f2m47-t22705043-f4e44623` | 56 | 3 | §20's sweep; the frozen `M1` recipe, rebuilt exactly |
| `icv1-f2m57-tm747311035-c1f545af` | 64 | 2 | §20's model optimum, 61 columns, read as `8⌈c/8⌉` |
| `icv1-f2m41-tm2308219-7f48b14a` | 80 | 2 | §20's sweep; the frozen `M1` recipe, rebuilt exactly |
| `icv1-f2m53-tm56619371-dac20a85` | 264 | 2 | §20's sweep; the frozen `M1` recipe, rebuilt exactly |
| `icv1-f2m59-tm943548413-98844ecc` | 256 | 2 | §20's model optimum, 251 columns, read as `8⌈c/8⌉` |
| `icv1-f2m61-t158598901-ab42b6c5` | 320 | 2 | §20's sweep; the frozen `M1` recipe, rebuilt exactly |

The two new sizes were never swept. Their recipes follow §20's model
rather than §20's measurement, and they are labelled so wherever they
appear.

## Targets and rows

- **Targets `T01`–`T64` at every size.** `T<i>` is the public
  hash-to-curve point with `public_hash_seed` `23000 + i`, in
  `ic workflow`'s domain. Nobody constructs its logarithm.
- **Rho's seed for `T<i>`** is `0x230000 + i`.
- **One process per target** (`R1`). `T01`–`T04` run again in a second
  process (`R2`), as the A/A.
- **In each process:** three repetitions (fifteen under 50 ms), with the
  unit measured around each. Each arm's median repetition is the row's
  figure.
- **Keys.** A row is keyed by `(candidate_id, workload_id, run_id)`.
  These are built by the tournament's canonical adapter
  (`research/ic_candidate_tournament_20260915/identity.py`):
  - the IC1 candidate from the recipe and the factor base's actual
    orbits;
  - the workload from the curve, the target, the seeds and the resource
    envelope;
  - `run_id = <candidate>W<workload>R<run>`.

  Rho gets its own reference identity from `tools/curve_identity.py`,
  never an IC1 label.
- **Checks.** `claims.py` assembles each row's `vs_rho` claim and runs
  the repository's checker (`boundary_autolab.validate_claim`).

## Accounting

- **Unit:** one batched addition (§20), measured around each
  repetition. `S` = units over `√r`.
- **Setup:** the sum of the index calculus's setup phases.
- **Online:** each arm's interval.
- **Cold:** an arm's setup plus its online cost.
- **Per size, over the `R1` rows:**
  - **the online speedup:** mean rho online over mean index-calculus
    online, each row in its own unit. Its 95% interval comes from 10,000
    bootstrap resamples of the targets, paired. The median of the
    rows' own ratios goes beside it.
  - **the same with rho at the canonical step:** the model, secondary.
  - **the cold ratio:** index calculus over rho, with its interval.
  - **the break-even count:** setup over the online saving, the number
    of targets at which one-target rho runs and one index-calculus setup
    cost the same.
  - **the precomputation boundary:** the model above, against the index
    calculus's mean online cost.
- **Growth:** least-squares slopes of `ln S` on `ln r` over the six
  sizes, with 95% intervals (`t`, 4 degrees of freedom), for:
  - the index calculus online;
  - rho online;
  - the setup;
  - the online speedup;
  - the cold ratio.

## Isolation (AGENTS.md §10)

- **Every timed process runs through the isolation tool:** one
  `ic price --single-target` as `tools/isolated_bench.py run --wait
  --cpus 2`, with `RAYON_NUM_THREADS=1`. The tool's defaults stand.
- **Waiting for pressure to fall.** The harness waits for PSI
  `some avg10` below 4.0 before each start.
  - A refused start is logged to `refusals.log` and tried again after
    15 s.
  - A contended or failed run is kept and run again up to twice. The
    first clean run is the row. Contended and clean runs are never
    pooled.
- **The A/A** is `T01`–`T04`'s second process against its first. The
  repetitions within a process are the other noise measure.
- **The pin** is untimed, under `taskset -c 2`, and nothing timed runs
  beside it.

## The pin, before any size

The batch pricer on §20's frozen `M1` files at the four old sizes must
give §22's isolated record's counts and recovered logarithms. If it does
not, the pricer is not the one §22 measured, and nothing runs.

## Predictions (`prediction.json`)

- **Where they come from:**
  - the four old sizes from §22's isolated records;
  - the two new sizes interpolated between their neighbours;
  - rho at the declaration probe's step (4.3 units) and at the
    canonical step (2.3).
- **All figures are in units.**

| curve | IC online | setup | rho online, probe step | speedup, probe / canonical step | cold ratio | break-even | IC online over the BL model |
|:--|--:|--:|--:|--:|--:|--:|--:|
| `icv1-f2m47-t22705043-f4e44623` | 22,834 | 1.51 M | 181,640 | 8.0× / 4.3× | 8.4 | 9.5 | 2.5 |
| `icv1-f2m57-tm747311035-c1f545af` | 29,524 | 2.82 M | 264,835 | 9.0× / 4.8× | 10.8 | 12.0 | 2.8 |
| `icv1-f2m41-tm2308219-7f48b14a` | 35,619 | 4.45 M | 441,272 | 12.4× / 6.6× | 10.2 | 11.0 | 1.9 |
| `icv1-f2m53-tm56619371-dac20a85` | 87,576 | 33.7 M | 2,401,311 | 27.4× / 14.7× | 14.1 | 14.6 | 1.2 |
| `icv1-f2m59-tm943548413-98844ecc` | 102,079 | 39.0 M | 2,489,496 | 24.4× / 13.0× | 15.7 | 16.3 | 1.5 |
| `icv1-f2m61-t158598901-ab42b6c5` | 503,099 | 175 M | 6,227,204 | 12.4× / 6.6× | 28.2 | 30.6 | 5.3 |

**Expected:**
- the index calculus faster online at every size, by either rho price;
- slower cold at every size;
- slower online than the precomputation model at every size.

## Targets

1. **Correct.**
   - Every row is complete: both arms verify on every repetition, their
     counts repeat, and the two arms give the same scalar.
   - Both certificates replay in `oracle.py`.
   - Every declared row exists.
2. **Rule-conformant.** Every row passes `validate_claim` at `vs_rho`.
3. **Primary.** The online speedup at each size, with its interval.
   - *The index calculus is faster online* if the interval lies wholly
     above 1.
   - *Rho is faster online* if it lies wholly below 1.
   - *Not separated* otherwise.
4. **Cold, reported first beside it** (AGENTS.md §8): the cold ratio and
   its interval, read the same way.
5. **Secondary:**
   - the speedup with rho at the canonical step;
   - the index calculus's online cost against the precomputation model;
   - the break-even count;
   - the slopes.

   A figure off its prediction by more than 2× is reported as such.

The round's aim is met if targets 1 and 2 hold. The reading is then the
primary table. This is a measurement: no outcome of 3–5 is a success or
a failure of the method, and none is tuned for.

## Inadmissible

- Choosing or changing a recipe, a lane count or a distinguished-point
  rule after any row ran.
- Dropping a target, a repetition, a failed, contended or retried
  attempt, or a row that fails the checker, from the record.
- Pooling `R2` rows into the per-size figure, or contended with clean
  runs.
- Using batch rho, or any rho with a table from other targets, as the
  primary reference.
- Quoting the online speedup without the cold ratio and the model
  reading beside it.
- Presenting the canonical-step figure or the Bernstein–Lange figure as
  a measurement.

## Stop and abandon

- **The pin fails:** nothing runs.
- **A row that does not verify** (either arm, or a disagreement between
  them) stops its size. The size is reported, with no figure until
  resolved.
- **A row that fails the checker:** if the fault is in the assembly, the
  assembler (`claims.py`) is fixed and rerun, never the data. A row whose
  own data fail stays in the record, is excluded from its size's figure,
  and is counted.
- **The machine stays busy for 60 tries:** the harness stops. It is
  resumable.

## Cost, as an estimate

- 408 processes: 64 plus 4 at each size.
- About 1–1½ hours on this host, isolated. A process at `2^47.2` takes
  about 15 s.

## Host

- **Binary:** `ic` built from a clean tree at this declaration's
  commit, with rustc 1.94.1, kept outside the tree. `runs/host.json`
  records its sha256 and the host.
- **Host class:** one x86-64 cloud container with AVX-512 and
  `pclmulqdq`. Nothing is claimed for Arm64, GPUs or other hosts.

## Suite, class and scope

- **Suite.** The AGENTS.md §8 WDSat suite does not apply. The index
  calculus's code is unchanged: the pin checks its counts. The new code
  is the reference and the timer.
- **Class: accounting.** A measurement under a new rule, with no
  algorithm change. The reference changes because the rule changed it,
  not to move a ratio. The `k = 32` figures stay on the page as
  historical diagnostics.
- **Scope, AGENTS.md §8a.** There is no `m = 83` run, since
  `n = 83 > MAX_N`. High-fidelity ECC2K-130 improvement stays
  unestablished.
