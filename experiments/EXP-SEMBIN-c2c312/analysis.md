# Analysis — EXP-SEMBIN-c2c312 / RUN-SEMBIN-b6eb9f

- **Composed by**: `TASK-20260921-a9f304` (coordinator), review round
  `REVIEW-SEMBIN-20260921-457504`, `GOAL-SEMBIN-5078bc` / `BATCH-457504`.
- **Composes**: J-1 `TASK-20260921-f2d82f` (validator, verdict `breaks`, run
  validity `incomplete`), J-2 `TASK-20260921-411a9d` (red team, verdict
  `breaks`), J-3 `TASK-20260921-f1e5bd` (validator, blind re-derivation, verdict
  `holds` / `passed`). All three packages are hash-bound by
  `TASK-20260921-064ae9`.
- **Records**: `EV-SEMBIN-c6e9ad`, `DEC-20260921-2c62d7`.
- **Runs launched by this analysis**: 0. `maximum_runs: 0`. Every number below is
  either quoted from a committed record or an exact recomputation from committed
  records; recomputations performed by this composition are marked **[C]**.
- **Scope**: commensurability only. `interpretation_limits` of
  `specification.yaml` forbid this run bearing on Assumption 1 or Assumption 2 or
  on any deployed curve, **in either direction**, and nothing in this analysis
  does.

The four sections below are separated strictly. Section 1 contains no
interpretation; the reading of the facts begins in section 3.

---

## 1. Observation

Facts of record and exact recomputations. No inference.

### 1.1 What the package contains

| quantity | value | source |
|---|---|---|
| instances recorded | 126 | `summary.json`, `manifest.yaml`, recomputed **[C]** |
| raw records | 314 | `worker*/cells/results.jsonl`, recomputed **[C]** |
| duplicate records resolved | 44 | `summary.json`; `314 − 44 = 270` distinct `(instance_id, instrument)` keys **[C]** |
| structured (chained) instances | 122 | `manifest.result.n_structured_instances` |
| F4 traces completed | 43 | `manifest`, recomputed by J-1 |
| F4 traces unreached | 79 | `manifest`, recomputed by J-1 |
| closure instrument measured | 14 | `manifest` |
| closure instrument decided | 12 | `manifest` |
| `d_F4_semaev` values over completed | {3, 4} | `manifest` |
| `d_F4_naive` values over completed | {3, 4, 5} | `manifest` |
| `closure_D` values | {4} | `manifest` |

Cells measured: (12,6,6,2), (13,4,4,4), (15,5,3,3), (17,3,3,6), (17,3,3,7),
(17,3,3,8), (19,3,3,7), (21,3,3,7). `n ≤ 21`, `N ≤ 60`.

### 1.2 The separation, per instance

Eleven rows of `results-table.json` carry a non-null
`separation_closure_minus_dF4` **[C]**. Of those, one is the known-false planted
control and one is an instrument-identity repeat; the remaining **nine** are
distinct structured chained instances. The producer's own artifacts report both
numbers, in different files, without a reconciling note:

| artifact | figure | field |
|---|---|---|
| `manifest.yaml` | **9** | `result.instances_with_both: 9` |
| `task-report.md` | **9** | "On the 9 instances where both instruments returned a value" |
| `summary.json` | **11** | `agreements: 11` |

The nine structured instances, recomputed in full from `results-table.json`
**[C]**:

| instance | cell | quotient dim | unit ideal | `d_F4_semaev` | `closure_D` | separation | `closure_D` verdict basis at D = 4 |
|---|---|---|---|---|---|---|---|
| `sem_n13_m4_t4_k4_low_B_equ_s20260913001_d0` | (13,4,4,4) | 36 | no | 4 | 4 | **0** | standard monomials = \|V(I)\| = 36 |
| `sem_n15_m5_t3_k3_low_B_equ_s20260913001_d0` | (15,5,3,3) | 0 | **yes** | 4 | 4 | **0** | `1 in W_D` |
| `sem_n15_m5_t3_k3_low_B_ran_s20260913001_d0` | (15,5,3,3) | 0 | **yes** | 4 | 4 | **0** | `1 in W_D` |
| `sem_n15_m5_t3_k3_ran_B_equ_s20260913001_d0` | (15,5,3,3) | 0 | **yes** | 4 | 4 | **0** | `1 in W_D` |
| `sem_n15_m5_t3_k3_ran_B_ran_s20260913001_d0` | (15,5,3,3) | 0 | **yes** | 4 | 4 | **0** | `1 in W_D` |
| `sem_n17_m3_t3_k6_low_B_equ_s20260913001_d0` | (17,3,3,6) | 6 | no | 4 | 4 | **0** | standard monomials = \|V(I)\| = 6 |
| `sem_n17_m3_t3_k6_low_B_ran_s20260913001_d0` | (17,3,3,6) | 0 | **yes** | 4 | 4 | **0** | `1 in W_D` |
| `sem_n17_m3_t3_k7_low_B_equ_s20260913001_d0` | (17,3,3,7) | 18 | no | 4 | 4 | **0** | standard monomials = \|V(I)\| = 18 |
| `sem_n19_m3_t3_k7_low_B_equ_s20260913001_d0` | (19,3,3,7) | 6 | no | 4 | 4 | **0** | standard monomials = \|V(I)\| = 6 |

**Unit-ideal count among the nine: 5 of 9** **[C]**, confirming J-2's figure. All
nine are at seed `20260913001`, draw `d0`; the closure instrument ran on draw 0
only. The two certificate families are structurally different: `1 in W_D` is a
single containment test, the standard-monomial route is a quotient-dimension
match.

The D = 3 leg (the minimality half of "smallest `D` with verdict SUFFICIENT")
**[C]**: on the five unit-ideal instances the live D = 3 verdict is
`insufficient` with `solutions_source: f4_quotient_dimension` — `s = 0` supplied
by the F4 run. On the four satisfiable instances the live D = 3 verdict is
`undetermined` with basis "\|V(I)\| unknown: F4 run incomplete and too many free
variables for brute force", and the recovery is `summarize.py`'s post-hoc path,
which also takes `s` from the F4 instance.

Largest separation, as the contract's first tail check requires: **0**, reported
by `summary.json` as `largest_separation: [0, "ctrl_known_false_N35"]` — i.e.
attributed to the known-false control instance.

#### Coverage against the cells the hypothesis declares

`H-SEMBIN-112e2e`'s `test_boundary` sorts cells into three roles. Rows reaching
**both** instruments, per declared cell, recomputed from `results-table.json`
**[C]**. This is reported per cell rather than pooled because the contract's
`tail_checks` require per-instance reporting and an average over cells would hide
which regime was actually reached.

| role | cell | instances generated | rows with **both** instruments | of those, non-degenerate |
|---|---|---|---|---|
| separation | (15,5,3,3) | 20 | 4 | **0** — all four unit-ideal |
| separation | (19,3,3,7) | 20 | 1 | **1** (quotient dim 6) |
| separation | (21,3,3,7) | 20 | **0** | 0 |
| separation | (12,6,6,2) | 15 | **0** | 0 |
| off-diagonal | (17,3,3,7) | 20 | 1 | **1** (quotient dim 18) |
| off-diagonal | (17,3,3,8) | 20 | **0** | 0 |
| reproduction | (13,4,4,4) | 2 | 1 | 1 (quotient dim 36) |
| reproduction | (17,3,3,6) | 8 | 3 | 2 (one is the identity repeat) |

Across the four **separation** cells — the cells where the hypothesis predicts a
*strict* inequality — two produced no row with both instruments, and four of the
five rows from the other two are unit-ideal. **Non-degenerate observations in the
separation-cell set: exactly one** (`sem_n19_m3_t3_k7_low_B_equ_s20260913001_d0`)
**[C]**. The off-diagonal set contributes one more. Generation was not the
bottleneck — most cells were generated at the declared 20 instances; the thinness
is entirely at the comparison step, where the closure instrument ran on draw 0
only.

### 1.3 What the declared primary metric is bound to

`specification.yaml` `metrics.primary` names `d_F4_semaev_definition`,
`D_macaulay_rank_statistic`, `separation_D_minus_d_F4`,
`per_degree_pair_count_profile`, `per_degree_rank_increment_profile`.

`code/run_cells.py:148` binds the second of those names to the value `closure_D`
**[C, read directly]**:

```python
recB = dict(base, instrument="closure_certificate", input_sha256=sha, closure_D=closure_D,
            max_generator_degree=max_gen_deg, per_D=per_D,
            D_macaulay_rank_statistic=closure_D,
```

So every raw closure record carries `"closure_D": 4` and
`"D_macaulay_rank_statistic": 4` side by side, the same value under two names.
The string `separation_D_minus_d_F4` appears nowhere outside the specification;
the computed field is `separation_closure_minus_dF4`.

`code/closure_cert.py`'s own docstring defines `closure_D` by reference to F4
**[C, read directly]**:

> `G_D` is a Groebner basis of the ideal `<=>` F4 completes with step degree
> `<= D`. … `closure_D` = the smallest `D` with verdict SUFFICIENT.

and further: "`s` comes from the F4 run's quotient dimension when that run
completed, else from brute force over the free variables".

The instrument the same file labels the DREG statistic is a different function
**[C, read directly]**:

```python
def macaulay_single_level(N, equations, D, mem_cap_gb):
    res = _run(N, D, equations, max_iter=1, mem_cap_gb=mem_cap_gb)
    ...
    return {"D": D, "instrument": "macaulay_single_level_DREG", "status": ...,
            "rows": rows, "cols": ..., "rank": ..., "sr_pred_rank": pred[D],
            "sr_HF": ..., "deficit_vs_semiregular": ..., "wall_s": ...,
            "contains_one": ...}
```

`D` is a positional call argument echoed back in the return. **The function
returns no degree.**

`manifest.yaml` records `protocol_deviations: []` and
`unexpected_observations: []`, while `task-report.md` and
`NOTES-deviations-and-limitations.md` list seven deviations and three unexpected
events. None of the seven mentions the metric binding.

### 1.4 The single-level instrument's actual coverage

Recomputed from `results-table.json` **[C]**:

| probe | completed measurements | `deficit_vs_semiregular` |
|---|---|---|
| D = 3 | 126 | ∈ {0, 1} (1 on every structured instance, 0 on the planted control) |
| D = 4 | 111 | 0 … 71 (46 … 71 on structured cells) |

No cap other than D = 3 and D = 4 was probed, on any of the 126 instances.
Instances carrying a completed single-level measurement at **both** caps *and* a
`d_F4_semaev` value: **31** **[C]** — of which 29 are structured non-repeat
instances, the other two being the known-false control and one identity repeat.
By cell: (13,4,4,4) 1, (15,5,3,3) 20, (17,3,3,6) 7, (17,3,3,7) 1, (19,3,3,7) 1,
plus the control.

### 1.5 Semaev's exclusion rule, on this engine

Semaev's `d_F4` excludes trailing steps carrying the message "No pairs to
reduce". Across **749** F4 rounds in all `f4_trace_msolve` records — 717 after
duplicate resolution, over 126 instances — the number of rounds with `sel == 0`
is **0** **[C]**. msolve emits no zero-pair round anywhere in this run.

The producer's `d_F4_semaev` instead excludes the trailing run of rounds that
added no new basis element. The two rules diverge on exactly one instance
**[C]**:

`sem_n12_m6_t6_k2_low_B_ran_s20260913004_d3`, where the producer records
`d_F4_semaev: 4`, `d_F4_naive: 5`, `d_F4_last_productive_round: 4`, and
`f4_empty_step_degrees: [4, 5]`. The two rounds named in that field are:

```
deg 4   pairs 553    sel 34    rows 1915  x cols 2220    new 0   zero 34
deg 5   pairs 519    sel 519   rows 84267 x cols 84198   new 0   zero 519
```

Both selected pairs and both computed a row echelon form; the degree-5 round
echelonised an 84267 × 84198 matrix. The instance has no `closure_D` (the
closure instrument was never run on any n = 12 cell), so the divergence reaches
no separation value. J-3 derives `d_F4_semaev_literal = 5` there.

### 1.6 The contract's three tail checks, as answered

1. **Largest separation and its instance** — answered: 0, at
   `ctrl_known_false_N35` (§1.2).
2. **Instances where the statistics agree but the per-degree profiles differ**
   (the contract's "dangerous case") — J-3: **11 of 11** under a raw
   all-degrees comparison, **0 of 11** restricted to degrees ≥ 2. The raw hit is
   uniform across instances: the closure profile carries pivots at degree 1 (and
   0 where the ideal is unit) and an F4 run has no step at degree 0 or 1 because
   there are no critical pairs there. `degrees_only_in_f4` is empty on all 11.
3. **F4's "no pairs" degrees against the degrees where the Macaulay block gains
   rank** — J-3: untestable as literally stated on all 48 instances with a
   trace. The F4 side of the predicted coincidence is the empty set (§1.5), and
   the Macaulay side probed only two caps, so at most one rank increment
   (4 − 3) exists and the increment at D = 3 is undefined because D = 2 was
   never probed.

### 1.7 Controls, as recorded and as independently checked

| control | recorded outcome | J-1's independent finding |
|---|---|---|
| baseline (reproduction cells) | both instruments return 4 at (13,4,4,4) and (17,3,3,6) | `satisfied_differently`. True, and at (13,4,4,4) it rests on **one** instance, one variant, one draw, one record per instrument. `random_k_dimensional` and `B_random` absent at that cell; `random_k_dimensional` absent at (17,3,3,6) too. (17,3,3,6) carries 6 instances, 6 F4 completions all 4, 2 closures both 4. |
| known false | `d_F4 = 2`, `closure_D = 2`, `passed: true` | `satisfied_as_specified`. Verified the object: 69 equations in 35 variables, max degree 2, 35 of degree exactly 1; the retained `meta.planted_point` vanishes on all 69 over GF(2). Measured five times per instrument, identical. |
| invalid input | `t = 1` and `k = 0` rejected | `satisfied_as_specified`; rejection strings match `boolsys.py` (hash-verified) character for character; no measurement record exists for either. |
| instrument identity | `passed: true` on (17,3,3,6) | Verified field by field; the 15-round F4 profile exactly equal. The (13,4,4,4) entry is **not** a comparison — its "repeat" F4 record is `unreached_declared`. `result.identity_repeat_instances: 2` beside one `controls.instrument_identity` entry reads as two comparisons where there is one. |
| byte identity | "system_sha256 and input_sha256 recorded per record and **equal by construction**" | `satisfied_differently`. The two fields are one variable written twice (`run_cells.py:92, 97, 120, 146, 161`), so contract invalidation rule 1 can never fire. J-1 **performed** the missing comparison with an independent parser: 139 of 139 retained `.ms` files agree exactly with the canonical system in the sibling `.json`; field-equation block exactly one `v^2+v` per variable on all 139; 0 disagreements. 136 of 136 canonical re-hashes match the recorded `system_sha256`. |
| matched null | `unreached_wall_cap`, `null_f4_d_F4: null`, `null_closure_D: null` | **unevaluable**: the null has no `d_F4`, therefore no separation. Contract invalidation rule 3 cannot be evaluated from the records. |

Contract invalidation rules: rule 1 does not fire; rule 2 does not fire; rule 4
does not fire on any of 125 structurally recomputed instance files (equation
count `n(t−1)`, variable count `n(t−2)+kt`, max algebraic degree 3, no zero
equation, no out-of-range mask — 0 failures); rule 3 is unevaluable. No rule
fires. `stopping_rules[0]` is met at both reproduction cells;
`stopping_rules[2]` is met — 0 discordant duplicate pairs.

### 1.8 Artifact integrity

- Duplicate audit: 30 keys duplicated, 44 extra records, **0 discordant pairs**
  across `d_F4_semaev`, `d_F4_naive`, `closure_D`, `D_macaulay_rank_statistic`
  and every per-degree profile. "First completed record wins" never had to break
  a tie between disagreeing measurements.
- `artifact-digests.json`: 483 of 483 files match, none missing.
- `results-table.json` agrees with the raw records on `d_F4_semaev`,
  `d_F4_naive` and `closure_D` for all 126 instances; the only difference is
  `quotient_dimension` on 7 instances, always `null → value`, from the disclosed
  post-hoc re-read of the retained `.gb`.
- J-3's independent parse of every retained `.msolve.log` agrees field-for-field
  with the producer's `rounds` arrays: zero field mismatches.
- `closure_D` reproduces exactly on all 126 instances (15 values, 111 nulls) from
  per-cap primitives alone, never reading the recorded `verdict`.
- **Code identity is broken for 4 of 11 declared modules**: `f4_trace.py`,
  `run_cells.py`, `summarize.py`, `make_manifest.py` do not match
  `manifest.code_sha256`; `libclosure.so` and `libgf2ech.so` are absent.
  `boolsys.py`, `closure_cert.py`, `closure.c`, `gf2_echelon.c`,
  `run_wrapper.py` match. The run records `dirty: true`, so the commit never
  held the code that ran and `code_sha256` was the only binding.
- The manifest lists 5 commands; the progress logs record **22** invocations
  with materially different `--mem-cap` / `--wall-cap` / `--cells` arguments.
  One recorded outcome (`heavy:1`, `unreached_memory_cap`) was produced under
  `--mem-cap 8`, a value appearing in no `command.txt`.
- 129 instance stems exist on disk against 126 ids in `results.jsonl`. Three
  instances left artifacts and produced no record; one of them
  (`null_n17_m3_t3_k6_low_B_ran_s20260913001_d0`, the `B_random` matched null)
  genuinely ran and yields `d_F4_naive = 4` from its retained log. Both the
  producer's `summary.json` and J-3's derivation enumerate from
  `results.jsonl`, so both omit these three.
- `resources.within_budget` states a 7 GB msolve cap; `heavy:5` records
  `peak_rss_bytes` = 11.86 GB, above the contract's declared
  `maximum_memory_gb: 8` (enforcement is `advisory`).

### 1.9 Infrastructure outcomes, kept separate

Every F4 record with a status other than `completed` carries a null
`d_F4_semaev` and `d_F4_naive`; five carry only
`d_F4_partial_max_deg_seen = 4` alongside the rounds reached before the cap. The
manifest reports that field as
`partial_max_step_degree_seen_over_unreached`, not as a degree. msolve's
monomial-hash / exponent-vector tables exceeded the process cap on every cell
with `N ≥ 38`; 79 of 122 structured F4 traces are unreached, and
(17,3,3,8) produced no F4 trace and no closure decision at all. Under AGENTS.md
rule 5 none of this is evidence about any degree.

### 1.10 The two reviewer disagreements of record

- **J-1 versus the records, on certificate assignment.** J-1's report states
  that of the nine, "5 decided by `verdict_basis = "standard monomials = |V(I)|
  = s"` … 4 by `verdict_basis = "1 in W_D"`". The committed records show the
  reverse: 5 unit-ideal instances by `1 in W_D`, 4 satisfiable instances by the
  standard-monomial match (§1.2, recomputed **[C]**). J-2's assignment matches
  the records.
- **J-1 versus J-2, on whether an F4-supplied quantity decided `closure_D`.**
  J-1: "No `closure_D` among the 9 was decided by an F4-supplied quantity."
  J-2 (OBJ-7): "on 9 of 9, the recorded reason `closure_D` is not 3 is a number
  the F4 instrument produced." These address **different legs** and both are
  right about their own: the D = 4 *sufficiency* leg is F4-independent on all
  nine (`1 in W_D` is set from the closure's own `contains_one`; the
  standard-monomial route uses the closure's own brute-force count), while the
  D = 3 *minimality* leg cites an F4-produced `s` on all nine (§1.2). J-2
  concedes the first explicitly; J-1 did not examine the second.

---

## 2. Comparison

### 2.1 Contract-declared against what exists

| the contract declared | what the package contains |
|---|---|
| `D_macaulay_rank_statistic` as a primary metric | the name, bound to `closure_D`'s value (`run_cells.py:148`); no independent value anywhere |
| `separation_D_minus_d_F4` | absent as a string and as a quantity; `separation_closure_minus_dF4` instead |
| a `D` comparable to `d_F4` | `closure_D`, defined by F4 termination; and a single-level rank instrument that returns no degree |
| 20 draws per cell × 2 subspaces × 2 B modes | 5 draws for F4/single-level, 1 draw for the closure; (13,4,4,4) has one instance |
| field-equation convention as an independent variable | confounded with the instrument (msolve explicit, closure implicit) — disclosed as deviation 3 |
| matched-null separation compared against structured | null has no `d_F4`; comparison not evaluated; a closure-sufficiency comparison substituted |
| `per_degree_rank_increment_profile` | Macaulay caps D ∈ {3, 4} only, so at most one increment and none at the lower point |

### 2.2 Predicted against observed

| prediction (`H-SEMBIN-112e2e`) | observed |
|---|---|
| `d_F4 = 4` at both reproduction cells | 4 at both, on both instruments. Met. |
| `d_F4 ≤ D` on every measured instance | not evaluated for the hypothesis's `D`; `closure_D − d_F4 = 0` on 9 (11 including control and repeat) |
| `D − d_F4 ≥ 1` on at least one instance, and on instances closest in shape to GOAL-DREG-001's | **not observed.** Separation is 0 everywhere both instruments were reached, and no instance shares GOAL-DREG-001's cell |
| structured separation differs from matched-null separation by ≥ 1 | **unevaluable.** The null produced no separation |
| `D − d_F4` constant across the 20 R draws and across B | R-draw arm structurally untestable (closure on draw 0 only); B arm exercised at (15,5,3,3) and (17,3,3,6), no variation |

The `success_criterion` has four conjuncts. Two are met (both instruments return
4 at both reproduction cells; a map is written down with its profiles over the
instances measured). One is unevaluable (null separation differs). One —
`d_F4 ≤ D` on every measured instance — is met only for `closure_D`, not for the
declared `D`.

#### The predicted mechanism against the engine's behaviour

The hypothesis does not merely predict *that* there is a separation; it says what
the separation **is**: "the predicted separation is exactly the excluded tail: the
degrees at which the Macaulay instrument still finds rank-contributing rows are
degrees at which F4, by Semaev's own accounting, has no critical pairs left to
reduce."

| the hypothesis's predicted separation | what the engine supplies |
|---|---|
| the extent of the excluded "No pairs to reduce" tail | that tail is **empty**: 0 of 749 F4 rounds have `sel == 0`; msolve emits the string never (§1.5, J-3) |

So on the engine actually used, the quantity the hypothesis predicts the
separation to *equal* is zero. The predicted separation and the observed
separation agree at 0 — not because the prediction was tested and confirmed, but
because the engine cannot produce the phenomenon the prediction is about. This is
a statement about instrument selection, and §3.5 reads it.

Two independent coverage facts compound it: the hypothesis's declared instrument
(GOAL-DREG-001's block-m4ri Macaulay-rank instrument, "re-run on instances
generated here") was never run, and the separation-cell set yielded exactly one
non-degenerate observation (§1.2).

### 2.3 The falsification criterion

The contract: "`D − d_F4 = 0` on every measured instance including the
off-diagonal cells refutes the hypothesis … the two statistics would then be the
same quantity here, and GOAL-DREG-001's degree-5/6 measurements WOULD be in
tension with Assumption 1."

- Antecedent, first clause: the observed zero is `closure_D − d_F4`, not
  `D_DREG − d_F4`. Not the criterion's `D`.
- Antecedent, second clause: of the two off-diagonal cells, (17,3,3,7) produced
  one separation value and (17,3,3,8) produced none. "Every measured instance"
  is 9 of 126.
- Consequent: `EV-DREG-008` is a rank measurement at a **frozen input** D = 6
  whose output is `deficit_genuine = 17947`, and whose own `boundaries` block
  reads "Structural `deficit_genuine` ≠ theoretical `d_reg`" — verified against
  the record **[C]**. Building a Macaulay matrix at degree 6 and measuring its
  rank asserts no degree statistic of 6, so no equality `D_DREG = d_F4` could put
  it in tension with a bound on `d_F4`.

### 2.4 Against GOAL-DREG-001

Verified directly against that goal's committed record **[C]**: its objective
asks whether `d_reg(n)` tracks the semi-regular null "or departs
non-generically (bounded `d_reg`, or a deficit / `gap(n) = d_reg − d_ff` that
grows with n)", and its completion criterion asks for "`d_reg` OR
`gap(n) = d_reg − d_ff` measurements … evaluated at D up to and including
`d_reg` where reachable" — `D` swept, `d_reg` read off as an **output**.

`EV-DREG-008` (single frozen cell, D = 6, output a rank deficit, `claim_tier:
toy`, `strength: preliminary`) and those campaign-level degree quantities are
therefore different objects. This run computed no `d_reg`, no `d_ff`, no
`gap(n)`, and measured no instance at GOAL-DREG-001's cell (n = 12, t = 3). Its
only n = 12 cell, (12,6,6,2), has closure coverage 0 of 15.

### 2.5 The 9-versus-11 reconciliation

Adopted: **9** for the map claim, **11** for the separation-bearing row count.

The two numbers are the producer's own, in two of its own files (§1.2): the
manifest and task report say 9, `summary.json` says 11. They count different
sets and both are arithmetically correct. 11 = the 9 distinct structured chained
instances + `ctrl_known_false_N35` (a planted-dependency control, where F4
derives a degree-2 answer by construction) + one instrument-identity repeat of
`sem_n17_m3_t3_k6_low_B_equ_s20260913001_d0` (a byte-identical re-measurement of
an instance already in the 9). I recomputed the partition **[C]** and it is
exact.

The map is asserted over independent structured systems, so 9 is the count the
claim may use: a control and a duplicate of a counted instance add no
independent support. J-3's convention-independence result is established over
the 11 and therefore covers the 9 *a fortiori* — its strength is undiminished by
adopting the smaller set. J-3's own summary phrase "9 of them distinct systems
(two are identity repeats)" is loose in its labels (one of the two non-independent
rows is the planted control, not a repeat) and exact in its arithmetic.

### 2.6 The three joint verdicts

No single verdict is a verdict on the run; each reviewer saw one joint by
construction.

| joint | owner | verdict | what it establishes |
|---|---|---|---|
| J-1, validity and controls | `TASK-20260921-f2d82f` | `breaks` (narrowly), run validity `incomplete` | No invalidation rule fires and every reported number reproduces; the byte-identity control as *shipped* has zero detection power, and 4 of 11 declared module hashes do not resolve against a dirty tree |
| J-2, the metric and the map | `TASK-20260921-411a9d` | `breaks` | The declared primary metric was never computed; the headline is an agreement between two F4-side quantities; the map named by completion criterion 1 has no measured value in the package |
| J-3, blind re-derivation | `TASK-20260921-f1e5bd` | `holds` / `passed` | The headline reproduces exactly on 11 instances under all four `d_F4` conventions, from an implementation that never read the producer's; one definitional divergence, localised, reaching no separation |

J-1 and J-3 answer *whether the numbers are real*: they are. J-2 answers *what
the numbers are about*: not the declared metric. The verdicts do not conflict —
they attach to different questions — and the composition must carry both.

---

## 3. Inference

What follows from sections 1 and 2. Scoped to this run.

### 3.1 The run measured a real thing, and it is not the thing the contract declared

`closure_D` is defined by an F4-termination equivalence and takes its solution
count from the F4 run when available (§1.3). The quantity the contract named as
its second instrument is a single-level Macaulay rank that returns no degree.
So the headline `closure_D − d_F4 = 0` is an agreement between two F4-side
quantities. The inference the run draws from it — about GOAL-DREG-001's
statistic — passes through a third instrument that emitted no comparable number
and, by the run's own disclosure, could not be calibrated against any archived
DREG rank because the archived n = 12 fixture hash was not reproducible on the
host.

This is a defect of the **run** (an undeclared substitution, recorded nowhere;
`manifest.protocol_deviations: []`), and it sits on top of two defects of the
**contract**: the contract names `D_macaulay_rank_statistic` as a primary metric
and never defines it, and its falsification criterion attaches an unsound
consequent to a numerical antecedent (§2.3). The distinction matters because the
remedies differ — a protocol that asked for an undefined quantity is repaired by
a successor contract, while an undeclared metric substitution is repaired by
computing the declared metric.

Computing it is **not** free, and an earlier draft of this analysis said it was.
Correcting that here: §1.4's 31 instances carry single-level ranks at **D = 3 and
D = 4 only**, and on every structured instance the degree-4 Macaulay matrix is far
from determining — rank 4707 of 12951 columns at (15,5,3,3), 11140 of 59536 at
(17,3,3,6), 16136 of 102091 at (19,3,3,7), with `deficit_vs_semiregular` 46 … 67
**[C]**. A degree-valued statistic is the *least* D at which a stated rank
condition is reached, and for every structured instance that D is **above 4** and
was never probed. So no degree can be read off the existing records; only the
planted control reaches the condition (rank 59535 of 59536, deficit 0) and it is
not a Semaev instance. Obtaining the declared metric therefore requires new
measurements at D ≥ 5 — which is exactly where the memory caps bit at N ≥ 38 — and
the existing ranks at D = 3 and D = 4 are starting data for that sweep, not a
substitute for it.

### 3.2 What the run did earn

One result, and it is genuine. `closure_cert.py`'s equivalence between its
degree-capped closure and F4 termination is an **argument**, not a theorem the
run inherited. msolve is an independently written F4 with the opposite
field-equation convention — explicit `x² + x` generators against the closure's
Boolean ring where `x² = x` is implicit — and `H-SEMBIN-112e2e` names that
convention as an effect that can shift a reported degree by one. It did not
shift it on any of the nine. That is a falsifiable cross-engine,
cross-convention consistency check on an argued equivalence, and it passed.
Both reproduction cells return 4 on both instruments, matching the value
`KN-LIT-fa346d` Table 1 reports, which is the calibration `EXP-SEMBIN-7e1371`
was blocked on.

Its scope is narrow and must travel with it: nine instances, one seed, one
draw, `n ≤ 19`, `N ≤ 42`, five of the nine unit-ideal and decided by the coarser
`1 ∈ W_4` containment test, none exercising the empty-tail exclusion that
distinguishes Semaev's reading from the naive maximum. The conventions had the
least room to differ precisely where they were compared.

A second, smaller result: the single-level deficit against the archived
semi-regular prediction is exactly 1 at D = 3 on every structured instance and
46–71 at D = 4, on systems whose bytes are also the F4 instrument's bytes. That
is per-instance raw material for a `d_reg` reading that did not exist before
this run.

### 3.3 The commensurability question is not settled by this run

The run's load-bearing claim is that the DREG statistic is not the quantity
Assumption 1 bounds *because its degree is an input while `d_F4` is an output*.
That distinction is a property of the function signature
`macaulay_single_level(N, equations, D, mem_cap_gb)` — readable before the
function is called, on zero instances. Byte-identical measurement adds
auditability to it and adds the cross-engine check of §3.2; it does not convert
it into a measured result. And the distinction was already in the committed
ledger: `EV-DREG-008`'s own `boundaries` block said "Structural
`deficit_genuine` ≠ theoretical `d_reg`" seven weeks earlier.

Worse for the general claim: the distinction holds for `EV-DREG-008`'s frozen-D
rank and **fails** for GOAL-DREG-001's campaign-level `d_reg(n)`, `d_ff` and
`gap(n)`, which that goal's own completion criterion sweeps `D` to obtain as
outputs (§2.4). A decision citing this run to say "GOAL-DREG-001's measurements
do not bear on Assumption 1" would be true of one record and unsupported for the
campaign's central quantities. That residual is recorded, not dissolved.

### 3.4 Completion criterion 1 is not met, on either branch

The criterion asks for a committed decision stating the map between `d_F4` and
GOAL-DREG-001's Macaulay-rank `d_reg`/`D`, **instrumented on identical
instances**, so that campaign's measurements read either as bearing on
Assumption 1 or explicitly as not bearing on it.

1. The map instrumented on identical instances is `d_F4` ↔ `closure_D`, which is
   not the criterion's map (§3.1). The criterion's map has no measured value
   anywhere in the package.
2. "Instrumented on identical instances" is not satisfiable across the two
   campaigns from this package: there is no shared cell (§2.4).
3. The narrow scoped map that *can* be stated — `EV-DREG-008`'s reported
   quantity is a rank deficit at frozen input D = 6, not a degree the system
   attains, and therefore does not bear on Assumption 1 — rests on a
   definitional argument plus that record's own committed text, not on this
   run's instrumentation, and it covers only part of "that campaign's existing
   measurements". A criterion that asks for an instrumented map is not
   discharged by an argued one, and a criterion about a campaign's measurements
   is not discharged by a statement about one of them.

The criterion is explicit that either answer satisfies it and an unstated map
does not. The honest position is the third one it does not enumerate: a map
stated for one record on an argued basis, and unmeasured for the quantities that
motivated the question.

### 3.5 `H-SEMBIN-112e2e` does not move

Two facts bear on this and point in different directions: the predicted
strictness was not observed, and the quantity the hypothesis named may never
have been measured. The second governs.

They point in different directions because, read on its own, the first is
*adverse* — a prediction of strictness met by zeros everywhere looks like a
weakening — while the second is *neutral*, since a prediction scored against a
quantity it did not name has not been scored at all. Three findings resolve the
tension in favour of the second, and the third of them is the strongest:

1. **The zero is between `d_F4` and an F4-side quantity** (§1.3, §3.1). Reading it
   as adverse requires treating `closure_D` as the hypothesis's `D`, which is the
   substitution this round identified. A weakening would have to adopt the error
   in order to record it.
2. **Coverage cannot carry a strictness verdict.** The separation-cell set — the
   cells where strictness is predicted — yielded exactly **one** non-degenerate
   observation, two of its four cells yielding none (§1.2). One row does not test
   a prediction quantified over instances, in either direction.
3. **The engine zeroes the predicted cause.** The hypothesis states the separation
   *is* the excluded "No pairs to reduce" tail. That tail is empty here — 0 of 749
   rounds (§1.5, §2.2). So the hypothesis's own mechanism predicts separation 0 on
   this engine. The observed 0 is therefore *consistent with* the hypothesis under
   the instrument used, and carries no adverse weight whatever. A non-observation
   inside a regime where the predicted cause is absent by construction is not
   evidence about the prediction — it is evidence about the instrument.

Point 3 also disposes of the most tempting misreading of this round, which is that
the run quietly falsified the hypothesis and the composition is declining to say
so. It did not: on the engine used, zero separation is what the hypothesis
predicts.

A status change must rest on evidence about the hypothesis's own claim. That
claim is about the Macaulay-rank statistic `D` under one of three readings the
hypothesis itself enumerates, and no reading of it produced a degree in this run.
The observed zero separation is between `d_F4` and an F4-side quantity. Moving
the hypothesis on that measurement would repeat exactly the substitution the
round identified — scoring a prediction against a different quantity than the
one it named.

Further, the hypothesis's third assumption ("GOAL-DREG-001's instrument can be
run on instances chosen here") was not satisfied: the instrument was not run,
and what was copied verbatim is its semi-regular *prediction formula*, not its
rank instrument or its degree-reporting logic, with no numeric calibration
against an archived DREG rank possible on the host. The hypothesis's own second
assumption states the consequence: if the instrument cannot be made
commensurable, "this hypothesis is untestable as stated and the honest outcome is
an impediment, not a result."

So the status stays `specified`. The counter-argument is recorded rather than
glossed: a run under this hypothesis's own validation experiment did complete,
and a purely procedural reading of the lifecycle would advance it to `analyzed`.
That reading is declined because `analyzed` asserts that evidence about this
hypothesis has been analysed, and the finding of this round is that none was
produced for its declared quantity.

What would move it is named in `DEC-20260921-2c62d7`, and it is **not** a zero-run
recomputation — §3.1 corrects an earlier draft of this analysis that said it was.
Moving this hypothesis requires new measurements: a sweep of the Macaulay
instrument to D ≥ 5 on instances shared with GOAL-DREG-001, because the existing
records stop at D = 4 where no structured instance is near determining. That is
the honest cost, and it is the cost at which the memory caps already bit.

---

## 4. Limitation

1. **Tier `toy`, and no transfer.** `n ≤ 21`, `N ≤ 60`, `correspondence: null`.
   Semaev's own conclusion needs n = 409 and 571 at m = 11, 12 — roughly a
   27-fold extrapolation in n that nothing here touches. No transfer to
   cryptographic n is claimed or implied.
2. **Commensurability only.** Nothing in this analysis bears on Assumption 1 or
   Assumption 2, in either direction, or on the security of any deployed curve.
   J-2 checked the run for leakage in both directions and found none; this
   analysis asserts the same limit for itself.
3. **Coverage is thin where it matters most.** The map rests on 9 instances at
   one seed and one draw; 5 of 9 are unit-ideal. The baseline at (13,4,4,4)
   rests on n = 1, which admits no variance estimate. `random_k_dimensional` is
   absent at both reproduction cells. (17,3,3,8) produced no value from either
   instrument; (12,6,6,2) has closure coverage 0 of 15; n = 21 contributes no
   separation.
4. **Most unreached cells are infrastructure outcomes and say nothing
   mathematical.** 79 of 122 structured F4 traces are unreached, every cell with
   `N ≥ 38` exceeded the process memory cap, and the matched null hit the
   3600 s wall cap. Under AGENTS.md rule 5 none of this is negative evidence
   about any degree, and no inference above rests on any of it.
5. **Two declared controls were not established by the run.** Byte identity is
   true but was verified for the first time in J-1's validation, not by the run;
   the matched-null separation comparison and contract invalidation rule 3 are
   unevaluable, not passed. The run labels a different comparison "the control
   the contract asks for".
6. **The instrument bytes are not recoverable from this snapshot.** Four of
   eleven declared `code_sha256` values do not match and two build products are
   absent, against `dirty: true`. Findings that follow from the data alone (every
   recomputed number; the hash equality on 314/314 records) survive this; readings
   of `f4_trace.py`, `run_cells.py`, `summarize.py` and `make_manifest.py`
   describe the current bytes, which are not provably the bytes that ran.
   `boolsys.py` and `closure_cert.py` **are** hash-verified, which is why the
   generator, known-false and closure-definition findings above do not carry the
   caveat.
7. **`closure_D`'s re-derivation has a floor at the linear algebra.** J-3
   recomputed it from recorded per-cap primitives (`contains_one`,
   `standard_monomials`, `solutions`), which the producer's closure instrument
   computed; with `maximum_runs: 0` the rank computations underneath cannot be
   independently recomputed. The re-derivation is independent at the level of the
   statistic definitions applied to the profiles, which is what was asked, and
   not below that.
8. **Unresolved confounds.** Field-equation convention is confounded with
   instrument. The D = 3 minimality leg of `closure_D` cites an F4-produced
   solution count on all nine instances, though an F4-independent recovery
   exists in the data. The `f4_empty_step_degrees` field name does not describe
   its contents. Three generated instances have artifacts and no record, one of
   which ran.
9. **One reviewer number is wrong and is corrected here, not repaired.** J-1's
   assignment of the two closure certificate bases is inverted relative to the
   committed records (§1.10); the report is immutable and stays as filed. The
   swap runs in the direction of understating the unit-ideal finding, so this
   analysis adopts the records' values.
10. **The round's proves-too-much control does not pass its own tooling gate.**
    `tools/check_review_independence.py` reports the plan's
    `proves_too_much.failure_signature` as empty; the plan states the signature
    per object instead, under a non-schema field name, and J-2 ran all four
    objects against their declared signatures. The control was declared and
    executed; the gate as written does not pass. Recorded in
    `DEC-20260921-2c62d7` `procedure_deviations`.
