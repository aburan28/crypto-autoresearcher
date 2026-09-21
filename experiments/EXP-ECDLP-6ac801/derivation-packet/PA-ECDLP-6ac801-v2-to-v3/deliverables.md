# What to produce, and in what shape

Read `MANIFEST.yaml` first, then `quantity.md`, then this file, then
`prohibitions.md`. Those four files are the whole of your permitted reading
until your seal exists.

This file says what to produce. It states no expectation of how any of it will
come out.

---

## 1. Your own implementation

Write your own program computing the quantity in `quantity.md` from scratch.
Do not look for an existing implementation — see `prohibitions.md`. Any
language and any libraries are fine.

Deliver the program itself alongside its output. A result without the code
that produced it is not reproducible.

## 2. Per-cell output

A cell is a triple `(N, a, seed)`, over the grid in `quantity.md` §10: two
scales x four `a` x 25 seeds = 200 cells.

Per cell, report:

| field | type |
|---|---|
| `N`, `a`, `seed`, `T`, `T_sel`, `r`, `W`, `cap` | the parameters you used |
| `share_top_Tsel` | float |
| `cov_static` | float |
| `margin` | float, `= share_top_Tsel - cov_static` |
| `share_top_T`, `share_top_Tover4`, `share_top_Tover8` | float |
| `rho_ORACLE` | float |
| `n_dps` | int, the number of DPs in the exact partition |
| `cycle_mass`, `capped_mass` | int |
| `capped_walks` | int |
| `residual_fraction` | float, `= (cycle_mass + capped_mass) / N` |
| `accounting_identity_holds` | bool, `sum_d b(d) + cycle_mass + capped_mass == N` exactly |
| `min_basin_size` | int, to check the `b(d) >= 1` corollary |
| `n_tied_at_Tth_weight` | int |
| `margin_null_oracle_rand_uniform` | float |
| `margin_null_oracle_rand_sizebiased` | float |
| `margin_null_randsel` | float |
| `cov_static_shuf` | float (NULL-SHUF) |

## 3. Per-`(N, a)` output

| field | type |
|---|---|
| `k_25` | int, pass-count out of 25 (`margin >= 0`) |
| `verdict_25` | `G3-FEASIBLE` if `k_25 >= 20`, else `G3-INFEASIBLE` |
| `k_5` | int, pass-count out of the seeds 1..5 subgroup |
| `verdict_5` | by the `>= 4 of 5` rule, reported **separately**, never composited with `verdict_25` |
| `mean_margin` | float |
| `mean_margin_sign` | `+`, `-`, or `0` |
| `ci_lo`, `ci_hi` | the percentile bootstrap endpoints per `quantity.md` §11 |
| `ci_straddles_zero` | bool |
| `bca_lo`, `bca_hi`, `bca_variant` | optional, context only |
| `mean_margin_null_*` | the mean of each null arm over the 25 seeds |
| `n_seeds_margin_null_nonneg_*` | int, per null arm |
| `max_residual_fraction` | float, over the 25 seeds |

## 4. Ordering requirement

Compute and report **`a = 1/4` first**, at each scale, and **`N = 2^20`
before `N = 2^24`**. The reason for the first is in `quantity.md` §13; the
reason for the second is cost.

If your `a = 1/4` reading is `G3-FEASIBLE`, **stop and report that**. Do not
carry on to interpret the other cells: an instrument that passes a
known-false object is not measuring what this quantity says it measures.

## 5. The joints you own

These are yours to get right, and yours to report on. Nobody else's verdict
on any of them is available to you, and none is implied here.

1. **The cap.** That `cap = ceil(8*W)` is applied in **both** places
   (`quantity.md` §3): the basin assignment predicate, and the termination of
   pool-construction walks with no credit to `S_d`/`h_d`.
2. **The residual accounting.** That your three classes are disjoint and
   exhaustive, that the identity in §4 holds **exactly** at every cell, and
   that `b(d) >= 1` for every DP.
3. **The universe asymmetry.** That `cov_static` ranges over the pool's
   selected entries while `share_top` ranges over **all** DPs of the exact
   partition (`quantity.md` §7). Getting these onto the same universe would
   silently change the quantity.
4. **The weight and its tie-break.** That the selection is by
   `S_d + 4*W*h_d` and never by true basin size, and that ties at the `T`-th
   weight are broken by an ascending per-entry pseudorandom key in
   pool-insertion order (`quantity.md` §6).
5. **`T` at the smaller scale.** That `T = 64` at `N = 2^20`, from the frozen
   table, and not `round(2^20^(1/3)) = 102`. The arithmetic of the latter is
   right and the value is wrong; this is exactly why the table is quoted.
6. **The null object's universe.** That NULL-ORACLE-RAND draws its subset
   from **all DPs of the same enumerated partition** — the same universe the
   real `share_top` arm uses — and not from the pool.
7. **The verdicts are resampling-free.** That `k` and the sign of the mean
   margin are computed exactly, and that no verdict of yours depends on the
   bootstrap interval.

## 6. Your reading attestation — required

Report, as part of your deliverable, the **complete list of files you read
before sealing**. If that list is exactly the four packet files, say so. If
it is not, say what else you read and when, relative to your seal.

**A disclosed violation is a usable record of what was compromised. An
undisclosed one destroys the only independence claim this batch has.** There
is no penalty here for disclosing and no way to repair a concealment later.

## 7. Sealing

When your computation is complete and **before you open anything outside this
packet**:

1. Write your program and its output to your own task directory.
2. Compute a `sha256` of each file you are sealing.
3. Record the hashes and a UTC timestamp in a `seal.json` (or equivalent) in
   the same directory.
4. Commit them.

Only then may you open anything else. The seal is what makes your reading
independent; a reading sealed after you looked is a reading, not a blind
reading, and it must be reported as such (`prohibitions.md` §5).

## 8. What you are not asked to do

- Do not compare your result against anyone else's. You cannot: the
  comparison is somebody else's task, performed after your seal exists.
- Do not draw a conclusion about the hypothesis. Report the quantity.
- Do not tune anything to make a control pass. If a control fires, report
  that it fired.
- Do not fill in a cell you did not reach. A cell not computed is reported as
  **not run**, never as a negative and never estimated.
