# TASK-20260729-025 recheck note

Independent, non-originating re-derivation supporting
`amendment_review.yaml`. Every number below was produced in this session by a
Python 3 interpreter operating on scratch files **outside the repository**, from
the committed blob
`experiments/EXP-YIELD-001/runs/RUN-YIELD-001-NULL-RANDOM-SUMSET/results.json`
at commit `2fb2bb7a111d999859612e52990eea7dc6bbac1a` (IN-1), extracted with
`git show`. **The interpreter work is UNARCHIVED AND IS NOT EVIDENCE**; it is a
review check on a contract. **No draw of any specified process was made and zero
curve compute was performed.** The scratch files were deleted after use.

---

## 0. Snapshot verification, performed in this session against Git

| check | result |
|---|---|
| `e3c9cb45` resolves | PASS — `e3c9cb451381625877034174b61ca918b48f790d` |
| first parent | PASS — `9b0ee4d8e7d9fbf4056e0087e10629fc4c467b9d` |
| reachable from `HEAD` | PASS — ancestor of `fe8f28c943859c57bf7929e72e072babc987911c` on `claude/ecdlp-b011` |
| changed-path set at `e3c9cb45` | PASS — exactly one path, `A experiments/EXP-YIELD-002/amendments/v1_to_v2.yaml`. **No other path. The frozen `specification.yaml` is ABSENT from the changed-path set.** |
| frozen spec blob unchanged | PASS — `30a8bf3eb265b37d870581201d51646119531594` at both `f291a624` and `e3c9cb45` |
| criterion feasibility table blob unchanged | PASS — `e5e4db97847dee08d50f3c7258e23914dbd5026d` at both `f291a624` and `HEAD` |
| working tree matches commit | PASS — `git hash-object` on the amendment gives `ff83aa32a5d4a06b0c065183e3729049c8ea33f8`, the committed blob |
| `fe8f28c9` changed-path set | PASS — exactly one path, the `TASK-20260729-024` receipt |
| zero paths under `experiments/EXP-YIELD-002/runs` | CONFIRMED — `git ls-tree -r HEAD` lists only `amendments/v1_to_v2.yaml` and `specification.yaml` under `experiments/EXP-YIELD-002` |
| pre-registration order | CONFIRMED AGAINST COMMIT ORDER — the amendment is committed strictly before any draw exists |

---

## 1. N2 — the four corrected sets, re-derived from IN-1 on SET IDENTITY

Method, independent of the amendment's set surgery: read all 49 cells; apply
RC-C de-duplication on `(k, m, B)` keeping the FIRST-LISTED occurrence, as
`merged_tuple_reference_rule` binds; per surviving tuple take
`T = P_pred_decomposition.S_m_minus_2_term`, `s_001 = antipodal.sd`,
`n_rep = replicates`, `sem_001 = s_001/sqrt(n_rep)`; then enumerate.

The single duplicate found is `(k=12, m=3, B=22)` at `beta = 0.325` and
`beta = 0.350`, both `N = 4001`, `C_red = 1782`,
`P_pred = 1452.1510155838187` — matching the contract's `merged_cells_named`
exactly. 48 tuples survive.

| set | rule | re-derived count | amendment count | set identity |
|---|---|---|---|---|
| CR-1 | `T/sem_001 >= 3.000` | **20** | 20 | **IDENTICAL, tuple by tuple** |
| CR-2 | `T/s_001 >= 3.000` | **5** | 5 | **IDENTICAL, tuple by tuple** |
| CR-3 | `T/(sqrt(2) sem_001) >= 3.000` | **18** | 18 | **IDENTICAL, tuple by tuple** |
| cannot-fire complement | neither can fire | **28** (25 at m=2, 3 at m=3) | 28 (25 / 3) | **IDENTICAL, tuple by tuple** |

For every one of the four sets:
`|realised AND pre-registered|` = the full count,
`|realised MINUS pre-registered|` = 0,
`|pre-registered MINUS realised|` = 0.

The four named differences from the committed lists reproduce exactly:
`T-18-2-B58` at `T/sem_001 = 3.1004` **fires** CR-1;
`T-16-3-B48` at `2.7588` **does not**;
`T-18-2-B264` at `0.0945` **does not**;
`T-16-3-B22` at `T/s_001 = 3.0506` **fires** CR-2.

**No disagreement with the amendment's four sets is raised. L-1 is discharged.**

### 1.1 L-2 — the two derived remarks the amendment did not recompute

Both **CONFIRMED** from IN-1, not from set arithmetic on quoted lists:

- CR-3 (18) is a **strict subset** of CR-1 (20). TRUE.
- `CR-1 MINUS CR-3` = exactly `{T-16-2-B38, T-18-2-B58}` — **two** tuples, as the
  amendment states, not the three the frozen table named. TRUE.

Additionally re-derived and not previously stated: CR-2 (5) is a strict subset of
CR-3 (18), hence of CR-1.

### 1.2 Sensitivity of the merged tuple

The two committed draws of `T-12-3-B22` carry different `sd` (20.2077 at
`beta = 0.325`, 18.4401 at `beta = 0.350`), giving `T/sem_001` of 6.9739 and
7.6424. Both exceed 3.000 and both exceed 4.2426, so **the merge rule does not
change any of the four sets.** The rule is nonetheless load-bearing for the run
itself, and it is pinned pre-data in the frozen spec.

---

## 2. N3 / L-5 — branch structure tested by constructed cases

Under C-1 + C-4:
`P-CORE = NOT P-MISS`;
`MISS-STRUCTURED = (CR-1 fails at >= 2) OR (CR-1 fails with |z_sem| >= 4.000) OR
(CR-2 fails at >= 1) OR (CR-3 fails at >= 2) OR (CR-3 fails with |z_shift| >= 4.000)
OR (CR-4 fires)`;
`MISS-MARGINAL = P-MISS AND NOT MISS-STRUCTURED`.

| # | constructed case | branch | unique? |
|---|---|---|---|
| 1 | one CR-1 failure at `\|z_sem\| = 3.5`, no CR-3 failure, CR-2 and CR-4 clean | **MISS-MARGINAL** | yes — under frozen v1's AND reading this landed in **no branch**; repaired |
| 2 | one CR-1 failure at `4.5`, no CR-3 failure | **MISS-STRUCTURED** (disjunct 2) | yes |
| 3 | one CR-1 failure at `3.5`, three CR-3 failures all below `4.0` | **MISS-STRUCTURED** (disjunct 4) | yes — under frozen v1's OR reading this landed in **two branches**; repaired |
| 4 | zero CR-1 failures, one CR-3 failure at `3.2` | **MISS-MARGINAL** | yes |
| 5 | CR-4 fires alone, every per-tuple criterion clean | **MISS-STRUCTURED** (disjunct 6) | yes |
| 6 | *added by this session* — one CR-1 failure at exactly `4.000` | **MISS-STRUCTURED** (`at least 4.000`) | yes — boundary closed |
| 7 | *added* — one CR-1 failure at `3.5` **and** one CR-3 failure at `3.5` | **MISS-MARGINAL** | yes |
| 8 | *added* — all four criteria clean | **P-CORE** | yes |

**No case lands in no branch, and no case lands in more than one.** Because
`P-CORE` is the negation of `P-MISS` and `MISS-MARGINAL` is the residue of
`P-MISS` after `MISS-STRUCTURED`, disjointness and exhaustiveness hold for
**every** realised outcome without further argument, not only for these eight.

**The non-normative unfolding in `derived_reading_aid_binding_nothing` was
checked clause by clause against `NOT MISS-STRUCTURED` and AGREES exactly.**
The file also states which governs: the residual definition. Correct.

---

## 3. C-4 — the 4.000 edge, re-derived

Expected CR-1 chance exceedance counts over 37 tuples at 99 df and 11 at 29 df,
two-sided Student-t, computed here from an independent incomplete-beta
implementation:

| threshold | this session | amendment |
|---|---|---|
| 3.0 | 0.186865 | 0.18686 |
| 3.5 | 0.0426343 | 4.26e-02 |
| 4.0 | 0.00892401 | 8.92e-03 |
| 5.0 | 0.000370841 | 3.71e-04 |
| 6.0 | 1.87217e-05 | 1.87e-05 |
| 8.0 | 8.82271e-08 | 8.82e-08 |
| 10.0 | 7.25989e-10 | 7.26e-10 |

**All seven reproduce exactly.** The tail constants also reproduce:
`P(|t_99| > 3.000) = 0.003416`, `P(|t_29| > 3.000) = 0.005499`,
`P(|Z| > 3.000) = 0.002700`.

**Where the constant lives.** `grep` of the committed frozen spec returns
`10.000` at exactly four places — lines 703 and 705 (the two MISS-STRUCTURED
disjuncts) and lines 716 and 717 (the two MISS-MARGINAL band bounds). It returns
**zero** occurrences in the criterion feasibility table. C-1 deletes the
MISS-MARGINAL enumerated condition, so the remaining two are exactly the two
MISS-STRUCTURED disjuncts. **The amendment's claim that 4.000 now lives in
exactly two places is verified.**

---

## 4. C-5 — CR-4's Poisson-binomial half, re-derived

Per-tuple `p_i = Phi(-bias_i/sem_i)` with `bias_i` the exact process bias
`E[distinct] - P_pred` computed from
`E[distinct] = N - (1 - s/N)[(N-1)(1-2/N)^(C/2) + (1-1/N)^(C/2)]`:

| quantity | this session | amendment |
|---|---|---|
| `p` range | **[0.47003, 0.49859]** | [0.47003, 0.49859] |
| lower end at | **T-12-2-B46**, `bias/sem = 0.07519` | T-12-2-B46, `Phi(-0.07519)` |
| `E[n_neg]` | **23.504** | 23.504 |
| true `P(n_neg <= 13)` | **0.001660** | 0.001660 |
| `P(n_neg <= 13)` at `p = 0.500` | **0.001044** | 0.001044 |
| anti-conservative factor | **1.590** | 1.59 |
| true two-sided | **0.002302** | 0.002302 |
| declared figure | **0.002436** bounds it | bounds it |

**All correct.** One point of precision worth recording: the *exact* Binomial
two-sided figure is `0.002088`, which does **not** bound `0.002302`. The
amendment is careful to say the **declared** figure `0.002436` — the normal
approximation with continuity correction, `2 Phi(-3.0311)` — bounds it, and that
is true. The distinction is stated correctly and narrowly.

Max exact process bias re-derived as `0.130512` bins at `T-16-3-B58` and
`0.07519` SEM at `T-12-2-B46`, both matching.

---

## 5. C-7 — CR-2's per-tuple chance-alarm bound, re-derived

At 30 replicates, `|z_sd| >= 3.000` means `|t_29| >= 3.000 sqrt(30) = 16.4317`,
and `P(|t_29| > 16.4317) = 3.1275e-16`. At 100 replicates the threshold is
`|t_99| >= 30.0000` and `P = 1.7008e-51`.

**Both reproduce.** The frozen `below 1e-20` is wrong by four orders of magnitude
at the 11 tuples with 30 replicates, and the amendment's `below 1e-15` /
`below 1e-50` restatement is correct. `11 x 3.13e-16 = 3.4e-15` is indeed
negligible against 0.377.

---

## 6. C-6 — `sem_001` sourcing

`git show 2fb2bb7a:.../results.json | grep -c sem` returns **0**. IN-1 carries
`sd` and `replicates` and no `sem` field anywhere. `sem_001` is therefore DERIVED
as `s_001/sqrt(n_rep)`, not QUOTED. **C-6 is correct**, and IN-1's `replicates`
equals the C-14 schedule value at all 49 cells, so the derivation is unambiguous.

---

## 7. C-9 — the IV-1 blind-spot figures, re-derived

Under the scenario `the committed BATCH-011 residuals are real`, with
`mu_asrec` at the exact analytic as-recorded mean and
`sem_asrec = sem_001`, the quantity `|mu_asrec - mu_001|/(sqrt(2) sem_001)` is:

| rank | tuple | value |
|---|---|---|
| 1 | **T-18-2-B264** | **2.074** |
| 2 | **T-14-2-B118** | **1.867** |
| 3 | T-16-3-B22 | 1.532 |
| 4 | T-18-2-B140 | 1.391 |
| 5 | T-14-3-B34 | 1.350 |

**The amendment's 2.074 and 1.867 reproduce exactly**, and the maximum is below
IV-1a's 3.000 at all 48, so IV-1a indeed does not fire under that scenario.
(Using the asymptotic `P_pred - T` in place of the exact analytic mean gives
2.070 and 1.891; the amendment's figures are the exact-mean ones.)

---

## 8. The pre-registered power curve, re-derived

Model: the repaired null still falls short of `P_pred` by `phi T` at every
tuple, `sem_rep = sem_001`, per-tuple sign probability
`p_i(phi) = Phi((phi T_i - bias_i)/sem_i)`, `n_neg` Poisson-binomial.

| phi | `E[n_neg]` here | amendment | `P(CR-4 fires)` here | amendment | tuples with `E\|z_sem\| >= 3` here | amendment |
|---|---|---|---|---|---|---|
| 0.00 | 23.50 | (23.504 via C-5) | 0.002 | — | 0 | — |
| 0.02 | **26.66** | 26.66 | **0.009** | 0.009 | **0** | zero |
| 0.05 | **29.22** | 29.22 | **0.048** | 0.048 | **1** | one |
| 0.10 | **31.71** | 31.71 | **0.179** | 0.179 | **5** | five |
| 0.20 | **34.46** | 34.46 | **0.499** | 0.499 | **8** | eight |
| 0.50 | **37.97** | 37.97 | **0.919** | 0.919 | **16** | sixteen |
| 1.00 | **40.72** | 40.72 | **0.997** | 0.997 | **20** | twenty |

**Every one of the eighteen published figures reproduces exactly.** The curve is
correct and its `phi = 1.00` row is internally consistent with the corrected CR-1
count of 20.

---

## 9. NEW FINDING NB-1 — the adopted counterfactual is still two-valued

The amendment says: *"The counterfactual is `mu_rep = P_pred - T` at every
declared tuple, and NOTHING ELSE, from which the counterfactual statistics are
DETERMINED as `T/sem_001` for CR-1, `T/s_001` for CR-2 and `T/(sqrt(2) sem_001)`
for CR-3, with CR-4 unchanged at `n_neg = 48` with certainty."*

The CR-3 entry **does not follow from that premise.** CR-3's statistic is
`|(mu_rep - mu_001) - T| / sqrt(sem_rep^2 + sem_001^2)`. Substituting
`mu_rep = P_pred - T` and leaving `mu_001` at its committed value gives

```
|(P_pred - T - mu_001) - T| / (sqrt(2) sem_001)
    = |(mu_001 - P_pred) + 2T| / (sqrt(2) sem_001)
    = |residual_after_adding_back + T| / (sqrt(2) sem_001)
```

which equals `T/(sqrt(2) sem_001)` only if `mu_001 = P_pred - T` — i.e. only
under the identification the amendment **explicitly deletes and rejects**.

Re-derived from IN-1, the CR-3 counterfactual firing set under the **literal**
adopted counterfactual is:

| reading | CR-3 count | difference |
|---|---|---|
| `T/(sqrt(2) sem_001) >= 3.000` (published) | 18 | — |
| literal `mu_rep = P_pred - T`, committed `mu_001` | **19** | **adds `T-18-2-B58`** (3.4579 vs 2.1923) |

The only coherent single counterfactual that yields all four published sets is
a statement about **both arms' true means** —
`E[mu_rep] = E[mu_001] = P_pred - T` — under which `mu_001` is replaced by its
counterfactual mean rather than used as a realised value. **Under that reading
all four published sets are exactly right, as section 1 above verifies.** The
defect is that the amendment never states that reading, and its own stated
justification for choosing this counterfactual (*"T is DETERMINED and `mu_001`
is SAMPLED ... a firability claim built on `mu_001` is a property of ONE DRAW"*)
cannot apply to CR-3 at all, because `mu_001` appears in CR-3's statistic by
construction.

The same unstated ambiguity shows up a second time: `n_neg = 48 with certainty`
is a statement under the deterministic-realised reading, and the amendment's own
power curve gives `P(CR-4 fires) = 0.997` at `phi = 1.00` under the true-mean
reading. Both appear in the same file, four hundred lines apart, unreconciled.

**Cheapest repair — one sentence, pre-data, no threshold moves:** state the
counterfactual as *"under the counterfactual BOTH arms have the analytic
as-recorded mean, `E[mu_rep] = E[mu_001] = P_pred - T`, and the committed draw
`mu_001` is replaced by that mean and is not used as a realised value; from this
the counterfactual statistics are `T/sem_001`, `T/s_001`, `T/(sqrt(2) sem_001)`
and `E[n_neg] = 48`, and the four sets below are EXPECTED-statistic feasibility
sets, not realised-firing predictions."*

---

## 10. NEW FINDING NB-2 — the chance-alarm budget's CR-3 line

Table section 8 reads:

```
CR-3  same per-tuple reference as CR-1    = 0.18726 expected exceedances
```

justified by the sentence *"Under a correct diagnostic the statistics are
centred to within `0.16466` standard errors (section 5.4)."*

**That premise is false for CR-3.** `mu_001` is a committed constant, not a
quantity redrawn at run time. Under a **perfectly correct** repaired null the
only randomness in CR-3's numerator is `mu_rep`, so

```
z_shift  ~  |N(delta_i, 1)| / sqrt(2),
delta_i  =  (bias_i - residual_after_adding_back_i) / sem_001,i
```

and `max |delta_i| = 2.9340` at `T-18-2-B264`, i.e. a non-centrality of
**2.074 standard errors on the `z_shift` scale** — the *same* 2.074 the
amendment already quotes in C-9 — against a claimed centring of `0.16466`.
**That is a factor of 12.6.**

Re-derived conditional figures, all computable pre-data from committed numbers:

| quantity | declared | conditional on the committed `mu_001` |
|---|---|---|
| expected CR-3 exceedances at 3.000 | 0.18726 | **0.22989** |
| `P(at least one CR-3 chance alarm)` | — | **0.2108** |
| largest single-tuple contribution | — | **0.0953 at `T-18-2-B264`** (41% of the mass) |
| second largest | — | 0.0545 at `T-14-2-B118` |
| `P(CR-3 fails at >= 2)` → MISS-STRUCTURED | — | **0.0183** |
| expected CR-3 exceedances at 4.000 | — | **0.0052** |
| union-bound total across criteria | **0.377** | **0.4196** (0.18726 + 0.22989 + 0.002302) |

Two consequences.

1. **The declared 0.377 does not bound the conditional union-bound total.** The
   first review rebuilt 0.37582 and endorsed 0.377 as a valid upper bound; that
   rebuild reproduced the contract's own model rather than testing its premise,
   and the amendment carries the endorsement forward verbatim under
   `carried_forward_as_already_discharged.tail_constants_and_the_budget:
   CONFIRMED`.

2. **The single most likely miss under a CORRECT diagnostic is now a CR-3
   exceedance at `T-18-2-B264`**, at `p = 0.095`, driven entirely by the
   committed draw's own known 2.07-SEM offset. Nothing pre-registered tells the
   analyst that this named tuple is the expected chance offender. Summing the
   spurious routes into MISS-STRUCTURED — the branch that **SUPERSEDES**
   `EV-ECDLP-008` observation O-4 and records `the VOID reflects a MEASUREMENT
   FAULT` — gives roughly **3 to 4 percent** under a perfectly correct repaired
   null (`CR-3 >= 2` 0.0183, `CR-3 >= 4.000` 0.0052, `CR-1 >= 2` ~0.0175,
   `CR-1 >= 4.000` 0.0031, CR-4 0.0023, less the CR-1/CR-3 correlation of
   `1/sqrt(2)` the table itself names). **No chance rate for the
   MISS-STRUCTURED branch appears anywhere in the contract, the table or the
   amendment.**

Note that this is *not* an argument against C-4: the conditional CR-3 rate at
the new 4.000 edge is 0.0052, the same order as the CR-1 figure 0.00892 that
C-4 was derived from, so **the 4.000 edge survives the conditional analysis**.
It is an argument that the budget and the centring claim, which C-11 re-scoped
without naming this term, are wrong for CR-3.

**Cheapest repair — pre-data, feeds no criterion, moves no threshold:** record
the per-tuple `delta_i` table, restate the CR-3 budget line as `0.230
conditional on the committed draw` with the corrected total, extend C-11's
scoping sentence to name the committed draw's own sampling error at 2.074 SEM as
the largest non-centrality, and add a reporting-only clause in the C-9 pattern
pre-registering `T-18-2-B264` and `T-14-2-B118` as CR-3's two expected chance
offenders and their probabilities.

---

## 11. Determinism — what the named calls do and do not deliver

Re-read of the frozen `replication.seed_derivation_binding` confirms that the
**main-arm** seed convention was already fully specified in v1 (pipe-joined
ASCII, SHA-256, low 64 bits as an unsigned little-endian integer,
`numpy.random.default_rng`, one generator per tuple per arm, replicates
sequential without re-seeding, pre-marking draw before the throwing draws). C-3a
uses the same convention for the KNOWNANSWER arm, keyed on the case label.

`KA-1` and `KA-4` do share `(N = 11, s = 3, C_red = 0)` exactly as OBJ-3 states,
so case-label keying is necessary and it does make all eight seed strings
distinct. **Verified.**

Two residuals survive.

- **`KA-5`, `KA-7` and `KA-8` consume no independent stream.** The frozen text
  binds KA-5 to *"the same `10^6` pre-markings of KA-4"*, KA-7 to *"the same
  `10^6` replicates of KA-6"*, and KA-8 to *"consumes no random number"*. C-3a
  says *"seed one `numpy.random.default_rng` per case"* for `KA-1 through KA-8`,
  which reads as eight generators. An Executor may therefore draw KA-5 and KA-7
  fresh or reuse KA-4's and KA-6's streams. Both readings pass the
  tolerance-zero structural checks, so **no numeric harm** — but bit-exact
  third-party reproduction of the KNOWNANSWER arm is **not** determined, which
  is the exact property OBJ-3 says was lost.
- **`KA-6` has `s = 0`**, so C-3d's *"OMITTED ENTIRELY when `s = 0`"* is
  load-bearing rather than decorative, and it is correct.

Granularity mismatch: C-3c (verbatim from the reviewer) binds *"the numpy major
and minor version"*, while `the_numpy_pin_and_what_this_session_may_not_do`
binds *"the exact `numpy.__version__` string"*. The stricter one should govern
and the file does not say which does. `rng.choice`'s `shuffle` keyword is left
at its API default and is not named; the default is deterministic within a
version, so this is a nit, not a hole.

---

## 12. What was verified and what was not

**Verified in this session:** the snapshot integrity table of section 0; all four
corrected sets on set identity; both L-2 remarks; the merge-rule sensitivity; the
eight branch cases; the full seven-row exceedance table and the three tail
constants; C-5's eight figures; C-7's two figures; C-6's zero-`sem` grep; C-9's
two figures; all eighteen power-curve figures; the four-place location of
`10.000` in the frozen spec and its absence from the table; the CR-3 counterfactual
set under the literal reading; the conditional CR-3 chance-alarm table.

**Not verified in this session, and named rather than assumed:** the `E[distinct]`
derivation was recomputed numerically but not re-proved from first principles;
`P_pred` was not re-derived at all 49 cells; the `f < g` inequality was not
re-proved; the identity-bin convention formulas were not re-derived; sections 10
through 12 of the criterion feasibility table were not audited; `tools/validate_ledger.py`
was not run; no adapter probe was performed; no numpy version in any intended
execution environment was observed, so `L-4` is answered on the contract text
alone and not empirically.

**AppleDouble sidecars.** `._*` files exist elsewhere in this worktree —
including `coordination/goals/GOAL-ECDLP-001/batches/._BATCH-012`,
`.../BATCH-012/._dispatch_queue.json` and `experiments/._EXP-YIELD-002`. **None
is inside this task's `write_scope`**, so none was removed by this session;
they are reported for the Coordinator, since a staged sidecar would break the
`TASK-20260729-026` changed-path check.
