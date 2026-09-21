# TASK-20260729-007 — independent recount note

Validator, BATCH-011, GOAL-ECDLP-001. Independent non-originating session: this
session did not author `TASK-20260729-001`, `TASK-20260729-003`,
`TASK-20260729-010` or `TASK-20260729-005`, and did not run the Executor's
driver to produce the package under review. **Model independence is NOT
available and is NOT claimed** (INT-BATCH011-D).

Everything below was computed **in this session**. Numbers I did not compute are
labelled as read from the package.

Bound snapshot: commit `2fb2bb7a111d999859612e52990eea7dc6bbac1a`, parent
`81e5edc3660bf6831734a9e4ac637515cd760ce8`, branch `claude/ecdlp-b011`, HEAD of
the worktree `c3e2f453`.

---

## 0. What was re-derived from scratch, and with what

Two independent programs were written in the session scratchpad, **outside the
repository**, and deleted afterwards. Neither imports, reads or reuses any part
of `experiments/EXP-YIELD-001/driver/yield_census.py`.

- `indep_check.py` — plain-Python affine short-Weierstrass arithmetic
  (`sympy.isprime` for primality), naive point counting by quadratic-residue
  enumeration, the contract's curve-selection and generator rules implemented
  from the contract text, and a from-scratch baby-step giant-step solver.
- `recount.py` — the census itself: factor base from the x-interval, then
  `itertools.combinations_with_replacement` over m-element multisets, each
  multiset summed **by explicit elliptic-curve point addition on the curve**,
  distinct sums collected in a Python `set`.

The package computes the census in the discrete-logarithm image. My recount does
**not**: it never builds a DL table and never converts a point to an integer. So
the recount is an independent path through a different representation, which is
the check that matters for the DEC-20260727-009 failure mode (a metric that is a
statistic of bookkeeping rather than of the named quantity).

---

## 1. Receipt binding (verified against Git, not against the receipt's own text)

| check | result |
|---|---|
| `2fb2bb7a111d` resolves and is an ancestor of `HEAD` | yes |
| first parent equals the receipt's `parent_sha` | yes, `81e5edc3` |
| paths changed by the commit | exactly 20, all additions |
| changed-path set equals the receipt's `committed_paths` | yes, exact |
| all 20 `path_sha256` recomputed from the blobs at that commit | 20/20 match, 0 mismatch |
| all 20 also match the current worktree bytes | 20/20 match |
| untracked or AppleDouble files under `experiments/EXP-YIELD-001` | none; `git status` on that tree is empty |

Chain above the run package:

| commit | receipt | declared vs committed | blob hashes |
|---|---|---|---|
| `82327a02` | TASK-20260729-002 | 3 declared, 3 committed, exact | 3/3 match |
| `59f2e930` | TASK-20260729-012 | **1 source path declared, 2 committed** | 2/2 match |
| `009b90a5` | TASK-20260729-013 | 2 declared, 2 committed, exact | 2/2 match |
| `2fb2bb7a` | TASK-20260729-006 | 20 declared, 20 committed, exact | 20/20 match |

Pre-registration order, checkable by a third party:

- `experiments/EXP-YIELD-001/specification.yaml` is blob
  `586914984c4cd00fca16ee91c739b8363dd0fae1` at **every** commit in the chain —
  `82327a02`, `59f2e930`, `009b90a5`, `81e5edc3`, `2fb2bb7a`, `c3e2f453`. The
  frozen contract was never rewritten; the amendment supersedes it.
- `amendments/v1_to_v2.yaml` is blob `f54fc443cfa4e11476649da9d632a9b2aaa2cb42`
  at `59f2e930` and unchanged at `2fb2bb7a`.
- `experiments/EXP-YIELD-001/driver/yield_census.py` has **exactly one** commit
  in the whole repository history: `2fb2bb7a`. See section 8.

### Does the TASK-20260729-012 overrun affect my inputs?

**No.** That commit changed two paths against one declared source path. The
undeclared path is `coordination/.../BATCH-011/dispatch_queue.json`, a
coordination record. My bound input from that commit —
`experiments/EXP-YIELD-001/amendments/v1_to_v2.yaml` — is properly declared in
that receipt, and its recorded SHA-256 matches the blob at that commit. The
amendment's content binding and its commit order are intact. What the overrun
does affect is the standing of the **archive record**: a verifier checking
exact-declared-paths rejects it, which that receipt itself states is correct and
not to be worked around. That defect stays where it is; it does not propagate
into the run package's evidentiary chain.

---

## 2. Reproducibility — the strongest check available, and it passes

Re-executed all six runs from the recorded command, with the committed driver,
into a scratch root **outside the repository** (`--out-root`), then re-derived
`summary.json`. Total 7.8 s wall clock. Nothing in the repository was written.

Every `results.json` was diffed against the committed one **without any
normalisation first**, then the differing leaf keys were enumerated:

| run | raw differing leaves | which keys |
|---|---|---|
| CENSUS-M2 | 73 | `seconds` ×68, `instance_setup_seconds` ×4, `elapsed_seconds` ×1 |
| CENSUS-M3 | 73 | `seconds` ×68, `instance_setup_seconds` ×4, `elapsed_seconds` ×1 |
| NULL-UNIFORM-FB | 5 | `instance_setup_seconds` ×4, `elapsed_seconds` ×1 |
| NULL-RANDOM-SUMSET | 5 | `instance_setup_seconds` ×4, `elapsed_seconds` ×1 |
| CALIB-AP | 1 | `elapsed_seconds` ×1 |
| BASELINE-RHO-BSGS | 5 | `instance_setup_seconds` ×4, `elapsed_seconds` ×1 |

**Every single differing leaf across all six files is a timing field.** No
measured quantity, no seed, no derived statistic and no flag differs. The
Executor's reproducibility claim is exact and is confirmed.

Manifest re-execution differs only in `git.commit` / `git.dirty_entry_count` /
`git.porcelain_sha256` (HEAD has since moved and the package is now committed),
`timestamps`, and the four measured-resource fields. Everything substantive —
command, seeds, input parameters, deviations, contract-in-force block — is
identical.

### summary.json is derived, not hand-entered

Stronger test: the committed six `results.json` and `manifest.json` were copied
to a scratch root and `--summarize` was run over **them**, not over my
re-execution.

```
sha256 committed  : 2287b277b6f6ce842230ca13bf1217a8ba34cc6da1d2d362123502810f7b2aeb
sha256 recomputed : 2287b277b6f6ce842230ca13bf1217a8ba34cc6da1d2d362123502810f7b2aeb
byte-identical    : True
```

That SHA-256 is exactly the one the TASK-20260729-006 receipt binds. No number
in `summary.json` is hand-entered.

---

## 3. The `P_pred` missing-term diagnostic — verified independently

This is the load-bearing claim of the batch, so I recomputed it from the raw
recorded quantities rather than reading the Executor's fields.

For each of the 49 cells in `RUN-YIELD-001-NULL-RANDOM-SUMSET/results.json` I
took only `N`, `B`, `C_red`, `m`, and the antipodal arm's `mean` and `sd`, and
computed for myself:

```
lambda   = C_red / N
S_{m-2}  = 1  if m = 2 ;  B  if m = 3        (the contract's own convention)
P_pred   = N (1 - e^-lambda) + S_{m-2} e^-lambda
z        = (mean - P_pred) / sd
z'       = (mean - N (1 - e^-lambda)) / sd   i.e. the |S_{m-2}| e^-lambda term added back
```

Results:

| quantity | my value | package value |
|---|---|---|
| max abs difference, my `P_pred` vs recorded `P_pred`, over 49 cells | **0.0** | — |
| my `z` vs recorded `mean_minus_P_pred_over_sd` | agree to 1e-9 at all 49 | — |
| my `z'` vs recorded `residual_after_adding_back_over_sd` | agree to 1e-9 at all 49 | — |
| `z` range over all 49 cells | **[-12.43936, +0.24912]** | [-12.439, +0.249] |
| `z'` range over all 49 cells | **[-0.53450, +0.26740]** | [-0.534, +0.267] |
| cells with abs(z) > 3 | **4** | 4 |
| cells where my threshold call disagrees with `INV_4_within_3_empirical_sd` | **0** | — |

The four failing cells, recomputed:

| k | beta | m | B | C_red | z | z' after add-back |
|---|---|---|---|---|---|---|
| 18 | 0.200 | 3 | 16 | 688 | **-12.4394** | +0.0340 |
| 16 | 0.225 | 3 | 16 | 688 | **-5.8995** | +0.0960 |
| 18 | 0.225 | 3 | 24 | 2312 | **-5.7486** | +0.0079 |
| 18 | 0.250 | 3 | 28 | 3668 | **-3.9203** | -0.1097 |

Split by arity — this is the part that decides the reading:

| arity | cells | `z` range | `z'` range |
|---|---|---|---|
| m = 2 | 29 | [-0.938, +0.249] | [-0.534, +0.267] |
| m = 3 | 20 | **[-12.439, -0.231]** — every one negative | [-0.187, +0.224] |

**Finding.** The diagnostic is confirmed exactly as stated. The shortfall of the
empirical null mean below `P_pred` equals `P_pred`'s own `|S_{m-2}| e^-lambda`
term: adding that one term back collapses a 12.4-sigma discrepancy to 0.03
sigma, and collapses the whole 49-cell spread from `[-12.44, +0.25]` to
`[-0.53, +0.27]`. At m = 2 the term is `|S_0| = 1` and is invisible; at m = 3 it
is `|S_1| = B` and it is the entire discrepancy. So the amendment's C-4 sentence
"P_pred is therefore CORRECT to O(1)" holds at m = 2 and fails at m = 3, because
at m = 3 the omitted term is O(B) and B is large against the null's own spread.

I confirm this **arithmetically**. I do **not** rule on what it means for the
void verdict — that is `TASK-20260729-008` and the Coordinator (ST-4, and my own
card's DO-NOT-INTERPRET constraint).

Two structural facts a reader of that decision will want, both checked here and
both purely factual:

- The v2 C-4 derivation of the antipodal mean gives `(N-1)(1 - e^-lambda)` — it
  contains **no** `|S_{m-2}| e^-lambda` term. The v1 `P_pred` it declares
  "correct to O(1)" does contain one. The gap is between two committed contract
  clauses, not between the contract and the driver.
- The driver implements the C-4 process **exactly as written**: draw `g`
  uniformly from G, insert both `g` and `-g`, `C_red/2` times, into a zeroed
  N-bit array; it never pre-marks any bin. Verified by reading
  `occupancy_null()`. So the discrepancy is not an implementation departure.

---

## 4. Independent recount of the census metric

Four cells recounted from scratch by explicit curve arithmetic, including the
**smallest criterion-evaluable cell** (k = 12, beta = 0.275, m = 3, B = 16). For
each cell my program independently re-derived p, the curve (a, b), the group
order N, the generator, the factor base, and then `|S_m|` by summing every
m-multiset as curve points.

| cell | quantity | mine | package |
|---|---|---|---|
| k=12 beta=0.275 m=3 | L / B / C_all / C(B,m) / C_red | 10 / 16 / 816 / 560 / 688 | identical |
| | `S_{m-2}` | 16 | 16 |
| | **`\|S_m\|`** | **642** | **642** |
| | P_pred / E / R / R_max | 645.568750542 / 0.994471928 / 0.9634644562 / 1.2245903368 | identical |
| k=12 beta=0.400 m=2 | L / B / C_all / C(B,m) / C_red | 28 / 36 / 666 / 630 / 648 | identical |
| | **`\|S_m\|`** | **587** | **587** |
| | P_pred / E / R / R_max | 599.09744201 / 0.9798072214 / 0.9280523233 / 1.0529520398 | identical |
| k=12 beta=0.325 m=3 | B / C_all / C_red | 22 / 2024 / 1782 | identical |
| | **`\|S_m\|`** | **1232** | **1232** |
| | P_pred / E / R | 1452.151015584 / 0.8483966108 / 0.7112188895 | identical |
| k=14 beta=0.350 m=2 | B / C_all / C_red | 34 / 595 / 578 | identical |
| | **`\|S_m\|`** | **563** | **563** |
| | P_pred / E / R | 569.030071499 / 0.9894028949 / 0.9618574521 | identical |

Every printed digit agrees. **The primary metric is a measurement of the
quantity it names, not a statistic of bookkeeping**, at these cells and by an
independent representation.

Convention checks, from the same recount:

- **`\|I\|` vs point count.** Every criterion is evaluated on measured `B`, never
  on `L`. Confirmed in code (`classify_cell(B, m, p)` takes B, m, p only) and in
  data (`B/L` ranges 1.2–1.67 at small L; both `B` and `L` are reported at all
  136 cells).
- **The `m!` denominator.** `C_all = C(B+m-1, m)` and
  `C_all·m!/B^m = prod(1 + j/B)` are reported and reproduce exactly. My
  recount's `C_all` matches at all four cells.
- **Repeated factor-base elements.** Multisets with repetition; my
  `combinations_with_replacement` count equals the package's `C_all` at all four
  cells, and `C(B,m)` is reported alongside.
- **The identity element.** `\|S_m\|` includes the identity at m = 2
  (my recount: identity present at both m = 2 cells) and not at m = 3 (absent at
  both m = 3 cells). This matches the contract's statement that the identity is
  in `S_m` for even m and never in F.
- **Unordered vs ordered.** Unordered multisets throughout; no ordered variant
  appears anywhere in the reported ratios.

**No silent divergence from the frozen contract was found on any of the five
convention risks.**

---

## 5. Cell classing, recounted from the predicate

I implemented the v2 C-2 rule R-1 predicate myself — `h = B^m/(m! p) <= 0.5` AND
`C_red(B) >= 500`, with `C_red = sum_{k=1..m} C(B/2,k) C(m-1,k-1) 2^k` — and ran
it over all 136 recorded `(k, beta, m, B, p)` tuples.

| quantity | my count | package |
|---|---|---|
| criterion-evaluable on measured B | **49** | 49 |
| criterion-evaluable on the B = L basis | 44 | 44 |
| cells that changed class on measurement | 11 | 11 |
| my `C_red` vs recorded, all 136 cells | 0 mismatches | — |
| my `h` vs recorded, all 136 cells | 0 mismatches | — |
| my `evaluable_on_measured_B` vs recorded | 0 mismatches | — |
| `class_changed` flag consistency | 0 mismatches | — |

R-7 drift: realised 49 against the amendment's 44, drift **5 > 4**, so R-7
fires. Confirmed. It is a disclosure obligation, not a stop, and the disclosure
is present in `summary.json` under `realised_evaluable_set.R_7_drift_disclosure`
with all eleven moved cells named and their direction given.

**Was the class frozen before `S_m` existed?** Yes, and this is verified at code
level, not by assertion:

- `run_census()` runs a **pass 1** over all 68 cells of the arity that calls
  `classify_cell(B, m, inst.p)` and appends the frozen record to
  `out["classification"]`. `classify_cell` receives only `B`, `m`, `p`; it has no
  access to any sum set and none exists yet.
- **Pass 2** then computes the census, and copies the class in from the pass-1
  record (`cell["evaluable_on_measured_B"] = rec["evaluable_on_measured_B"]`).
  It never recomputes or revises it.

A class that is a function of its outcome would void the design. It is not one.

---

## 6. Parity

| claim | my check | result |
|---|---|---|
| measured B even at all 136 cells | recomputed `B % 2` at every cell | **136/136 even, zero odd** |
| `C_red` even at all criterion-evaluable cells | recomputed | **all even** |
| `C_red` even at **all** 136 cells | recomputed | **all even** — stronger than claimed |

`C_red` is even everywhere, not merely at the evaluable cells. The recorded
`C_red_is_even` flags agree.

---

## 7. Variance doubling, controls, baselines

**Variance ×2 (v2 C-4), from the archived contrast arm.** Recomputed the ratios
myself from the two arms' raw `sd` values at all 49 cells:

| statistic | my value | package |
|---|---|---|
| variance ratio, mean | **2.117811** | — |
| variance ratio, median | **2.015342** | — |
| variance ratio, min / max | 1.047669 / 3.622515 | — |
| sd ratio, mean | **1.442891** | 1.4428909556 |
| sd ratio, median | **1.419627** | 1.4196272816 |
| sd ratio, min / max | 1.023557 / 1.903291 | identical |
| analytic sd ratio | sqrt(2) = 1.4142136 | 1.4142135624 |

Matches the reported 2.118 mean / 2.015 median variance ratio and the 1.4196
median sd ratio against the analytic sqrt(2). The contrast arm is genuinely
inside the driver and archived, not imported from the unarchived TASK-20260729-003
probe.

**CTRL-CALIB-AP.** Recomputed the recovered penalty myself from the per-seed
`ap_supply_distinct` values, as `C(B,m) / median(supply)`:

| n | m | B | seeds | C(B,m) | median supply | ratio-of-medians | EV-STR-001 target | factor | within 2 |
|---|---|---|---|---|---|---|---|---|---|
| 211 | 3 | 15 | 24 | 455 | 21.0 | 21.6667 | 17.5 | 1.2381 | yes |
| 211 | 4 | 15 | 24 | 1365 | 5.0 | 273.0000 | 214.9 | 1.2704 | yes |
| 1009 | 3 | 32 | 6 | 4960 | 118.0 | 42.0339 | 41.9 | 1.0032 | yes |
| 1009 | 4 | 32 | 6 | 35960 | 40.0 | 899.0000 | 924.5 | 1.0284 | yes |
| 4099 | 3 | 65 | 6 | 43680 | 510.5 | 85.5632 | 87.8 | 1.0261 | yes |
| 4099 | 4 | 65 | 6 | 677040 | 168.0 | 4030.0000 | 4128.6 | 1.0245 | yes |

**6 of 6 inside the factor-2 window on ratio of medians. Confirmed by my own
recomputation.** Every derived field in the package's calibration cells —
`C_B_m`, `supply_median`, `supply_min`, `supply_max`, `seeds`, both estimator
forms, `factor_vs_target`, `within_factor_2` — reproduces exactly. Monotone
growth in n at fixed m holds on my numbers (21.7 → 42.0 → 85.6 and 273 → 899 →
4030); superlinear growth in m under the declared DEV-5 reading
`penalty(m=4) > (4/3)·penalty(m=3)` holds at all three n. **INV-2a did not fire**
(the shared-routine known-answer test agrees on 7/7 cases in every one of the six
runs) and **INV-2b did not fire** (0 cells outside the window, no trend clause
failure). The census void verdict from this leg is NOT-VOID, per v2 C-8, and only
INV-2a could have voided.

Seed counts honour v2 C-8(a): 24 at both n = 211 cells, 6 elsewhere. B = 15 / 32
/ 65 as C-8 freezes it, recorded per cell. The AP admissibility predicate is
recorded verbatim as read from the committed EXP-STR-001 contract, so ST-3
correctly did not fire.

Recorded observation, not a defect: C-8's own pre-data estimate was "about 91.6
and 4396.4 against targets 87.8 and 4128.6" at n = 4099. The realised values are
85.56 and 4030. Both are still comfortably inside the window; the prediction was
heuristic and the window is the rule.

**Baselines.** All four sizes:

| k | N | rho steps mean | 0.886 sqrt(N) | ratio | INV-6 (>20% below) |
|---|---|---|---|---|---|
| 12 | 4001 | 59.125 | 56.043 | 1.0550 | no |
| 14 | 16619 | 117.062 | 114.218 | 1.0249 | no |
| 16 | 65633 | 260.938 | 226.984 | 1.1496 | no |
| 18 | 261707 | 492.125 | 453.254 | 1.0858 | no |

Every measured rho cost is **above** the model position; INV-6 cannot fire.
BSGS memory (64 / 129 / 257 / 512 stored elements) sits at sqrt(N) as modelled,
and is reported beside its time as the contract requires.

**Certificates — re-verified in this session, not spot-checked.** I re-derived
each curve and generator from the contract's deterministic rules with my own
code and re-solved **every one of the 64 targets** with my own from-scratch BSGS:

| k | p | a | b | N | G | my derivation matches package | N·G = O | my BSGS re-solve |
|---|---|---|---|---|---|---|---|---|
| 12 | 4099 | 4 | 8 | 4001 | (1, 264) | yes | yes | 16/16, 0 mismatches |
| 14 | 16411 | 4 | 1 | 16619 | (0, 1) | yes | yes | 16/16, 0 mismatches |
| 16 | 65537 | 12 | 2 | 65633 | (0, 4080) | yes | yes | 16/16, 0 mismatches |
| 18 | 262147 | 5 | 1 | 261707 | (0, 1) | yes | yes | 16/16, 0 mismatches |

`curve_candidates_tried` and `curve_selection_t_reached` also reproduce exactly
(59/12, 10/5, 90/14, 15/6), which means my reading of the curve-selection rule
and the driver's are the same reading. At all 64 targets
`rho_d == bsgs_d == d_true`, and my independent solver returns the same integer.
**All 128 claimed solves are confirmed correct by an implementation that shares
no code with rho, with BSGS, or with the DL table.**

Standing control: census / rho operation ratio 2.8e4 to 2.6e6. The census costs
far more than solving the instance. Not an attack, and cannot be read as one.

**CTRL-NULL-FB (destroy parameter).** Ran at 49 cells, 0 skipped, draws 10 where
B <= 64 and 3 otherwise — v2 C-13 exactly, verified cell by cell. Code path
verified identical to the census: same `distinct_sumset()`, same
`shared_membership_distinct()`, same measured B, same curve. Shape-matched,
identically measured, correctly parameterised.

**Destroy-parameter decay.** Reported, not adjudicated. The package records
`n_cells_compared = 49`, `n_not_shrinking_strict_reading = 16`,
`n_not_shrinking_and_out_of_band = 0`, and `firing_determination: null` under
DEV-6. The three out-of-band cells (all k = 12, m = 3, all E below 0.90) each
have `deviation_shrinks_under_randomisation_strict_reading: true`, i.e. the
deviation **does** decay at every out-of-band cell. Per my card I state the
statistic and do not make the INV-5 determination: the contract never quantifies
"shrink" and v2 C-13 gives the disposition a three-way reading the Executor was
right to refuse and that I am not authorised to choose either. It belongs to
TASK-20260729-008 and the Coordinator.

**CTRL-DL.** 8 control records (4 sizes × 2 arities), 10^4 samples each, **0
mismatches** between curve-side and DL-image sums; walk closure and the
`2x+1 = N` point count both OK. INV-3 did not fire. Minor undeclared reading:
the contract does not say at which beta CTRL-DL should draw its factor base; the
driver fixes beta = 0.500 and records it as `beta_used`. Recorded, not listed
among DEV-1..DEV-6.

**NOISE-LIMITED.** No cell excluded. Max measured relative null sd is **1.641%**
against the 2% rule. Note that the amendment's stated worst case was 1.49%, so
the realised margin is 1.22x rather than the 1.34x C-4 predicted. The threshold
was not crossed and was not moved.

---

## 8. The dry-run disclosure — tested, and what the test can and cannot show

The claim: a scratch-root dry run preceded the declared runs, revealed the INV-4
firing, and in response the driver gained **reporting only** — no threshold, no
criterion, no seed, no control process, no replicate count, no cell class and no
measurement.

**What cannot be checked, stated first.** `git log --all` shows
`experiments/EXP-YIELD-001/driver/yield_census.py` has **exactly one commit** in
the entire repository — the run package itself. There is no committed
pre-dry-run driver blob, and the dry run wrote outside the repository, leaving
no receipt of any kind. The claim is therefore **not directly corroborable from
Git**. Any validator who says otherwise is overstating.

**What can be checked, and was.** The contamination surface is bounded by
checking the committed driver against the committed contract pair, both of which
predate any execution and whose commit order a third party can verify:

| item the claim says did not change | where it lives in the driver | traced to |
|---|---|---|
| evaluable predicate | `H_CAP = 0.5`, `C_RED_FLOOR = 500`, `classify_cell()` | v1 criteria_definitions / v2 C-2 R-1 |
| the six master seeds | `MASTER_SEEDS` = 110201/110301/110401/110501/110601/110701 | v1 replication.seeds, v2 `not_changed` |
| seed derivation | `derive_seed()` = SHA-256 over `master\|parts`, recorded per number | manifest, applied uniformly |
| INV-4 test | `bool(abs(ma - p_pred) <= 3 * sa)` | v1 INV-4, DEV-4's literal reading |
| null process | `occupancy_null(..., antipodal=True)`: draw g, insert g and -g, `C_red/2` times | v2 C-4, verbatim |
| contrast arm | same function, `antipodal=False` | v2 C-4's declared contrast |
| replicate counts | `replicate_count()` = 100 / 30 / 10 at 1e4 / 1e6 | v2 C-14, exactly |
| FB-null draws | `fb_null_draws()` = 10 if B <= 64 else 3 | v2 C-13, exactly |
| NOISE-LIMITED | `rel_sd > 0.02` | v1, unmoved by v2 |
| calibration window | `fac <= 2.0`; fires at `>= 2` misses | v2 C-8 |
| superlinearity | `penalty(m=4) > (4/3)*penalty(m=3)` | DEV-5, declared |
| INV-6 | `mean_rho < 0.8 * model_rho` | v1 INV-6 |
| grid | `BETA_GRID` = 0.200..0.600 step 0.025, `FIELD_BITS` = 12/14/16/18, `ARITIES` = 2/3 | v1 inputs |

I also grepped the whole driver for hard-coded cell coordinates. The only
`(k, beta)` literals in the file are inside a **quoted PC-2 disclosure string**
copied from the committed TASK-20260729-011 review — they appear in a text
field, never in a branch condition. There is no cell-specific special-casing
anywhere.

And the decisive structural check on the diagnostic itself: **the add-back
quantities are computed and recorded but consumed by nothing.**
`residual_after_adding_back_S_m_minus_2_term`,
`residual_after_adding_back_over_sd` and `P_pred_decomposition` appear only in
output dictionaries. `INV_4_within_3_empirical_sd` is evaluated against
`p_pred`, the frozen formula, and nothing else. The one data-dependent branch is
`if failed:` guarding emission of the `derived_diagnostic` block — a reporting
conditional, exactly as disclosed.

**Conclusion on contamination.** Every threshold, criterion, seed, control
process, replicate count and class rule in the committed driver matches the
committed contract pair, which was frozen at `82327a02` and amended at
`59f2e930`, both strictly before the driver existed and both checkable by commit
order. INV-4 was evaluated against `P_pred` exactly as frozen. The residual
contamination surface is confined to **what got reported**, which is precisely
what the Executor disclosed and which does not affect a single measured number —
and the whole package re-executes bit-exactly, so no reported number is
adjustable after the fact without changing the driver's hash. **I find no
evidence of pre-registration contamination, and I record that the disclosure is
bounded by contract conformance rather than proven by a receipt.**

---

## 9. Protocol deviations DEV-1..DEV-6, assessed

- **DEV-1 (command/environment folded into `manifest.json`, stderr tee'd into
  `stdout.log`) — ACCEPTABLE, NOT A POLICY BREACH.** AGENTS.md "Artifact policy"
  requires each run to **retain** the exact command, environment and dependency
  versions, and stdout and stderr. It nowhere requires particular filenames. The
  frozen contract's `required_artifacts_rule` is emphatic in the other direction
  — "EXACTLY TWENTY FILES, NO MORE AND NO FEWER", three per run directory, no
  stderr file — and it states that this is what makes the 21-path declaration
  (20 artifacts + the receipt) exact in advance. Writing `command.txt`,
  `environment.json` and `stderr.log` would have violated the frozen contract and
  the task card. I verified retention rather than accepting the assertion:
  `command`, `invocation_cwd`, the full `environment` block with Python version,
  platform, cpu_count, dependency versions, driver SHA-256 and randomness sources
  are all present in **6/6** manifests, `stderr_location` names `stdout.log`, and
  the in-process `Tee` is present in the driver. Nothing is lost; the location
  changed for a stated contractual reason. Correctly recorded as a deviation
  rather than done silently.
- **DEV-2 (implementation notes inside the manifest) — acceptable, same
  reasoning.** Notes are present in 6/6 manifests and in `summary.json`.
- **DEV-3 (sampled collision-profile estimator defined)** — a genuine
  under-specification in v1 (SAMPLED is named, the statistic is not). The
  estimator is defined, the sample maximum load is explicitly labelled a sample
  statistic and not an estimate of the true maximum, and CTRL-EXHAUSTIVE-TRUTH
  runs the same estimator where the exhaustive value exists. Acceptable.
- **DEV-4 (INV-4's "3 empirical standard deviations" denominator)** — v1 really
  is silent on single-replicate sd vs standard error of the mean. The **literal**
  and **more conservative-to-fire** reading was applied (single-replicate sd),
  and both z values are reported per cell. I confirmed the applied rule in code
  and that my own threshold call agrees at all 49 cells. Had the standard error
  of the mean been used instead, INV-4 would have fired far more widely, so the
  reading chosen is not the one that manufactures the firing. Acceptable.
- **DEV-5 (superlinearity operationalised)** — declared with its formula. Holds
  at all three n on my recomputation. Acceptable.
- **DEV-6 (INV-5 not adjudicated)** — correct. The trigger turns on an
  unquantified "shrink" and C-13 gives it a three-way disposition. Refusing to
  choose, archiving the statistics, and routing the determination upward is what
  ST-4 requires. Acceptable, and the right call.

---

## 10. Defects on the record

**D-1 (material, upstream, not the Executor's).** No committed record sets
`experiment.status` to `approved` or fills `approved_by` for EXP-YIELD-001. I
checked the blob at the snapshot commit directly: `status: review_required` and
`approved_by: null` at lines 11 and 706. AGENTS.md "Research states" puts
`approved` before `running`. The contract's own execution gate — TASK-20260729-011
returning PASS, plus INT-BATCH011-A — **is** satisfied by committed records: the
PASS review is committed at `009b90a5`, and BUDGET-AMEND-20260729-001 raising
`maximum_batches` 10 to 11 is committed at `93d961e0`, which I verified is an
ancestor of the snapshot. So the substantive authorization exists; the formal
status transition does not, and it cannot be supplied by editing an immutable
file. The Executor reported this rather than editing anything, which is correct.
It is the Coordinator's to close in the ledger record.

**D-2 (material, upstream).** PC-1, PC-2 and PC-4 have no separate committed
Coordinator recording. Their own binding note in the TASK-20260729-011 review
requires them to be "recorded BEFORE TASK-20260729-005 is dispatched, so that it
is pre-data". The texts do exist verbatim in the committed review at `009b90a5`,
which is an ancestor of the run package, so the **pre-data property survives** —
what was skipped is the separate Coordinator recording. The Executor applied the
sole committed candidate reading in each case, which is not a guess, and flagged
the gap. PC-3 is discharged in the committed TASK-20260729-013 receipt; I
confirmed that receipt exists and its two paths hash-match.
Related observation: PC-2 predicted eleven cells would flip class. Eleven did.
But the sets are **not** the same eleven — only five overlap
(m=2 k14 b0.350, m=2 k14 b0.500, m=2 k18 b0.275, m=2 k18 b0.500, m=3 k12 b0.375).
The count agreement is coincidental and should not be read as a confirmed
prediction.

**D-3 (minor).** CTRL-DL's factor-base beta is unspecified by the contract; the
driver fixes 0.500 and records `beta_used`, but this is not enumerated among
DEV-1..DEV-6.

**D-4 (minor, observation).** Realised max relative null sd 1.641% against C-4's
stated 1.49% worst case, and against the unmoved 2% NOISE-LIMITED rule. No
exclusion fired; the margin is 1.22x, not the 1.34x the amendment stated.

**D-5 (recorded, not repairable here).** The requested inference policy
`executor-implementation` resolves through the adapter to
`anthropic:claude-sonnet-5` at effort medium; the executing session reports
itself as `claude-opus-5` with `AUTORESEARCH_POLICY` and `AUTORESEARCH_BACKEND`
unset. The manifest records this as a `policy_binding_mismatch` with
`fallback_used: false` and `model_verified: false`, and states that
`doctor --probe` was run and could verify nothing. That is the honest recording
CLAUDE.md's process-level note calls for. It is a real per-role model-selection
gap in the runtime, disclosed rather than silently substituted.

---

## 11. Checks not reached inside the cap

- The dry-run driver itself. It does not exist as a receipt anywhere (section 8).
  Bounded, not verified.
- `\|S_m\|` was recounted independently at **4** of 136 cells, not all 136. Full
  independent recount at m = 3 on k = 16 and k = 18 is out of reach for a
  Python-object-set implementation inside this card's budget. The four cells were
  chosen to include the smallest evaluable cell and both arities at two sizes.
- Independent BSGS re-solve covered all 64 targets; I did not reimplement Pollard
  rho, so the reported rho **step counts** are read from the package. Their
  **solutions** are independently confirmed (all 64 equal `d_true`, which my own
  solver reproduced).
- The Monte-Carlo null means and sds are Monte-Carlo outputs; I did not
  reimplement the sampler. They are confirmed by exact re-execution of the
  committed driver, which is a reproducibility check rather than an independent
  estimate.
- `tools/validate_ledger.py` was not run (INT-BATCH011-F says it exits nonzero
  independently of this batch, and it is outside my write scope to act on).
- Model independence: **not available and not claimed.** The adapter resolves
  `review-adversarial` to `anthropic:claude-opus-5` at effort xhigh on the default
  backend, and refuses it on `zai-anthropic` because the policy requires xhigh
  against a binding ceiling of high. `$ZAI_API_KEY` and `$ANTHROPIC_API_KEY` are
  both unset, so no probe verification of any identifier was possible.

---

## 12. Working-tree hygiene

No file in the repository was created, modified or deleted by this validation
other than the two artifacts this card declares. All re-execution wrote to a
scratch root outside the repository and has been deleted. No commit was made. No
status was changed. `git status` on `experiments/EXP-YIELD-001` and on
`coordination/.../BATCH-011` was empty before I started and the pre-existing
AppleDouble deletions elsewhere in the tree were left untouched.
