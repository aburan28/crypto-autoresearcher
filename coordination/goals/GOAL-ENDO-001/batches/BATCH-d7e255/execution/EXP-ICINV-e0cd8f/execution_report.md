# Execution report — EXP-ICINV-e0cd8f, contract version 1

- **Handoff**: `TASK-20260811-d9d01e` (coordinator → executor)
- **Goal / batch**: GOAL-ENDO-001 / BATCH-d7e255
- **Contract**: `experiments/EXP-ICINV-e0cd8f/specification.yaml` (v1, `status:
  approved`, `approved_by: coordinator`, approved 2026-08-10 by
  `DEC-20260810-a4bec4`)
- **Branch**: `claude/ecdlp-endomorphism-analysis-4m2w3z`
- **Task starting commit**: `76a48ff3d852473e743741e768319d9721124088` (the
  snapshot commit named in the handoff)
- **origin/main at start of task**: `44525b6f7aad8f69a9909d0721518e0934e7f10a`
  — `git rev-list --left-right --count HEAD...origin/main` = `26 0`: the
  starting commit already contains every commit on `origin/main` (0 commits
  on `origin/main` not already in the branch). No merge was needed or
  performed.
- **New harness module**: `harness/exp_icinv_e0cd8f.py` — new file, does not
  edit `harness/semaev.py` or `harness/isogeny_class.py` (both read-only
  imports only). Reuses `harness.runner.git_state`, `.source_provenance`,
  `.environment`, `._iso` unedited for manifest provenance.
- **Executed**: 2026-08-11

**This report records what ran and what did not. It interprets nothing.** No
evidence record is written here, no hypothesis status is moved, and nothing is
characterised about what `CLASS-VARYING` means for `H-ICINV-d5e351`,
`RQ-ICINV-475b5e`, or `GOAL-ENDO-001`. Those are Coordinator acts on a later
ledger archive after independent review.

---

## 1. Stage 0 — SR3 backend gate (this task's own required first act)

Per the handoff's constraint, **neither Singular nor Macaulay2 was installed
in this environment before this task**, confirmed via `which`/`apt-cache
policy` by the dispatching Coordinator. Both were confirmed available as apt
candidates. This task's own Stage-0 work was to attempt the installs.

| step | command | outcome | measured elapsed |
|---|---|---|---|
| 1 | `apt-get update` | succeeded (exit 0) | ~4 s |
| 2 | `apt-get install -y singular` | succeeded (exit 0) | 19 s |
| 3 | `apt-get install -y macaulay2` | succeeded (exit 0) | 86 s |

Both installs succeeded. Versions confirmed after install:

- **Singular** 4.3.2 (`dpkg` version `1:4.3.2-p10+ds-1.1build1`), binary
  `Singular` on `PATH`.
- **Macaulay2** 1.22 (`dpkg` version `1.22+ds-6build2`), binary `M2` on
  `PATH`.

**SR3 PASSES.** This is a `completed_valid` run outcome, not
`failed_infrastructure` — the contract's own text states plainly that a
successful install is the alternative to that outcome, and that a failed
install (not what happened here) is the only case requiring
`failed_infrastructure`. Full detail, including the recorded apt-get timings
and versions, is in every run's `backend-provenance.json`
(`experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/backend-provenance.json`),
written **before** any resolution was computed, per SR3's own ordering
requirement.

---

## 2. Runs produced

| run id | status | verdict | wall seconds | notes |
|---|---|---|---|---|
| `RUN-ICINV-e0cd8f-m3class` | `completed_valid` | `CLASS-VARYING` | 855.5 s | the one and only run of this contract |

1 run of 8 maximum. No invalid or failed run occurred; no rerun was
performed. `RUN-ICINV-e0cd8f-dryrun-m3class` and other prototype/dry-run
executions used during development (`control_size=5`, `control_size=3`) were
run **outside** `experiments/EXP-ICINV-e0cd8f/runs/` (in the executor's
scratch space, never inside the write-scoped run tree) precisely so they
would not appear as run records; the two-curve M2 elimination-script defect
they caught (§5, deviation D1) is disclosed below regardless.

**Budget accounting**:

| | this run | budget |
|---|---|---|
| wall clock | 855.5 s | 7200 s / run |
| CPU (single-threaded, ≈ wall) | ≈ 0.24 CPU-hours | 6 CPU-hours total |
| peak memory | well under 8 GB (no OOM, no `RLIMIT_AS` trip) | 8 GB |
| runs | 1 | 8 max |

`python3 tools/check_run_source_provenance.py --experiment EXP-ICINV-e0cd8f
--strict`:

```
1 pinned, 0 unpinned, 0 unreadable, of 1 run manifest(s) in scope
  of the pinned, 0 also ran from a fully clean tree
```

Passes `--strict` (0 unpinned). `all_clean: false` because the run's own new
module, `harness/exp_icinv_e0cd8f.py`, is untracked at the starting commit
(it was written in this task and had not yet been committed) — it is
nonetheless `sha256`-pinned (`status: untracked`), which is exactly what
`all_pinned: true` certifies. `code.dirty: false`: no *tracked* file differs
from `HEAD`. (`--since-commit` scoping was attempted first and reported "no
run manifests in scope" — expected, since this run directory is itself
untracked pending the Coordinator's snapshot commit, so a `git diff
--diff-filter=A <commit>..HEAD` sees nothing; the unscoped `--strict` check
above is the correct substitute pending that commit.)

---

## 3. Stopping-rule gates, in order

### SR1 — support gate (before any resolution)

Symbolic re-derivation, `support-derivation.json`:

| quantity | value |
|---|---|
| generic support (symbolic `a`, `b`) | 13 |
| `a = 0` support | 9 |
| `b = 0` support | 10 |
| matches 13/9/10 | **True** |
| all 138 class members' `S_3` support = 13 | **True** |

**SR1 PASSES.**

### SR2 — census gate (before any class-wide computation)

`class-census.json`: re-enumerated `p = 4001`, `t = 30` via
`harness.isogeny_class.isogeny_classes` and `.class_census` (unedited,
read-only import) — **138 members**, Hurwitz-Kronecker weighted count
`138.0` vs predicted `138.0` (`agrees: True`).

**SR2 PASSES.**

### SR4 — control-set-first ordering

`control-set-invariants.json` was written (log timestamp: control computed
and written in 369.4 s) **before** `per-curve-invariants.json` was written
(392.4 s later, at cumulative 392.4 s more) — enforced structurally in
`run_experiment`'s own control-flow, not just by log order.

### SR5 — frozen scope

Exactly `p = 4001`, `t = 30`, arities `{3, 4}`, `x0`-homogenisation with
standard grading, `degrevlex` primary order (`lp` on the cross-check
subsample per C-ORDER). No other prime, class, arity or grading was computed.

### SR6 — budget

Not triggered; run completed within budget (§2).

### SR7 — no outcome shopping

The verdict and every reported metric are computed inside `run_experiment`
and written to `verdict.json`; the reported metric set (all seven primary
families, secondary `m=4` support/singular-locus, Koszul indicator, gauge
recheck, backend crosscheck) does not depend on which verdict fired — the
same code path runs regardless of outcome.

---

## 4. Primary invariant families — the exact multisets

All 138 class members and all 138 control-set members computed at `m = 3`,
gauge-rechecked, backend-cross-checked. `per-curve-invariants.json`,
`control-set-invariants.json`, `verdict.json`.

| family | class distinct values (count) | control distinct values (count) |
|---|---|---|
| `S_3` monomial support | `{13: 138}` | `{13: 138}` |
| singular-locus dimension (affine) | `{0: 138}` | `{0: 138}` |
| singular-locus degree (affine) | `{6: 138}` | `{6: 138}` |
| regularity (homogenised Jacobian ideal) | `{5: 138}` | `{5: 138}` |
| elimination-polynomial degree | `{3: 138}` | `{3: 138}` |
| elimination-polynomial factorisation partition | `{(1,2): 72, (1,1,1): 66}` | `{(1,2): 63, (1,1,1): 26, (3,): 49}` |
| graded Betti table (homogenised Jacobian ideal) | one table on all 138 (below) | the same table on all 138 |

The one Betti table shared by every class and every control-set member (`i`
= homological degree, `j` = internal degree, `beta_{i,j}`):

```
(i=0, j=0, beta=1)
(i=1, j=3, beta=3)   (i=1, j=4, beta=1)
(i=2, j=5, beta=2)   (i=2, j=6, beta=2)   (i=2, j=7, beta=1)
(i=3, j=8, beta=2)
```

Regularity `= max(j-i) = 5`, read off this same table (not from a
backend-provided `regularity` builtin — see §6 deviation D1).

**Six of the seven primary families take exactly one value on all 138 class
members AND on all 138 control-set members.** Reported plainly: this makes
those six families constant on curves far more generally than "this isogeny
class" — the control set (random ordinary ($a\neq0$, $b\neq0$) curves at the
same prime, drawn from 92 *other* traces) shows the identical single value on
every one of them. No interpretation of what that means is offered here.

**The seventh, the elimination-polynomial factorisation partition, is NOT
constant on the class**: 66 of 138 class members have partition `(1,1,1)`
(the cubic elimination polynomial splits into three distinct linear factors
over `F_4001`) and 72 have partition `(1,2)` (one linear factor times one
irreducible quadratic). The control set additionally contains 49 curves with
partition `(3,)` (an irreducible cubic) — a factorisation type that occurs
**zero** times among the 138 class members.

---

## 5. Controls discharged

### C-GAUGE

Every one of the 276 curves (138 class + 138 control) was recomputed on a
gauge-transformed model `(u^4 a, u^6 b) mod p` with `u` drawn deterministically
from `seed = 20260810`. `gauge-recheck.json`: **0 class failures, 0 control
failures, `all_agree: true`** — the full `m=3` signature (all seven primary
families) is identical before and after the gauge transform, on every curve,
including every one of the 66 class members carrying the elimination-partition
deviation (explicitly checked in the F5 withdrawal logic below).

### C-BACKEND

Cross-check subsample: **66 curves** (all curves carrying the elimination-
partition deviation; the required minimum of 20 is met with room to spare,
`meets_minimum_20: true`, `includes_all_deviating_curves: true`).
`backend-crosscheck.json`: **every one of the 66 curves' Macaulay2-computed
signature (support, singular locus, regularity, elimination degree and
partition, Betti table) matches the Singular-computed signature exactly**
(`m2_all_agree: true`). This is not a restatement of Singular's own output —
the M2 script independently builds the ideal from the same `(a,b)` (via
`harness.exp_icinv_e0cd8f.build_m3_m2_script`, a wholly separate code path
using M2's own `res`, `eliminate`, and `factor`) and its regularity figure is
derived from ITS OWN betti table (see deviation D1) rather than trusted from
M2's `regularity` builtin.

### C-ORDER

The same 66 curves were recomputed under `lp` (lexicographic) monomial order
in Singular. `order_agrees: true` on all 66 — every order-independent
quantity (support, singular locus, regularity, elimination degree/partition,
Betti table) is unchanged under the order swap, as theory requires.

### C-KOSZUL

Reported per curve in `koszul-indicator.json`: for every one of the 138 class
members and 138 control-set members, `codim_hom` (computed as
`nvars(rhom) − dim(std(J_hom))` = `4 − 1 = 3`) is **less than** the number of
Jacobian generators (`4`: `S_3` plus its three partials). `class_all_koszul:
false`, `class_any_koszul: false`, `control_all_koszul: false` — **the
Jacobian generators are NOT a regular sequence on any curve in either set.**
Per F3, this rules out "constancy is a Koszul degeneration" as the
explanation for the six constant families; it is reported here as a fact
about every curve, not as an interpretation of what it implies.

### C-CENSUS, C-SUPPORT

SR1/SR2 above.

### C-CONTROL-SET

138-curve control set drawn deterministically from the 92 non-target traces
present at `p = 4001` (`control-set-invariants.json`: `drawn_traces` lists
all 92; ranked by `sha256(seed:"control:a:b")` and truncated to 138 — fully
reproducible from the recorded seed `20260810`).

---

## 6. F5 — did the one claimed difference survive?

**Yes.** The elimination-partition difference is the only family where
`class_distinct_count > 1`. Its F5 check (in `run_experiment`) requires: (a)
every deviating curve appears in the C-BACKEND subsample and its M2 and
alt-order signatures both match the Singular `dp` signature; (b) every
deviating curve's own gauge-transformed model shows the SAME (not the modal)
value. Both hold for all 66 deviating curves — `surviving_families_after_f5:
["elimination_factor_partition"]`, `withdrawn_families: []`.

---

## 7. Emitted verdict

```
verdict: CLASS-VARYING
```

Per `verdict.json`'s own `reason` field: *"At least one primary invariant
family shows >1 distinct value across the class, surviving gauge and backend
checks: ['elimination_factor_partition']."* This is the run's own computed
output, unedited here.

Per the contract's success criterion, `CLASS-VARYING` fully satisfies it (the
contract is decisive both ways) — it is not a lesser or partial outcome than
`CLASS-INVARIANT` would have been.

---

## 8. Tail checks (contract §`tail_checks`)

### 8a. Extreme/deviating-curve listing

All 66 class members whose elimination-partition value (`(1,1,1)`) differs
from the class mode (`(1,2)`) are listed individually in
`verdict.json:deviating_curves_by_family.elimination_factor_partition`, each
with `(a, b)` and the observed value. Their `j`-invariants (cross-referenced
from `class-census.json`) span the class; the first eight, for illustration:

| a | b | j |
|---:|---:|---:|
| 460 | 2974 | 49 |
| 505 | 1010 | 76 |
| 2394 | 787 | 147 |
| 1122 | 748 | 155 |
| 204 | 408 | 227 |
| 869 | 1738 | 247 |
| 973 | 1946 | 305 |
| 1493 | 2329 | 398 |

(Full 66-curve list: `verdict.json`. Every one of these 66 also appears in
`backend-crosscheck.json` with `m2_agrees: true`, `order_agrees: true`, and
in `gauge-recheck.json` with `m3_agrees: true`.) No true 2-volcano level is
reported for these curves: computing it would require a per-curve `ell = 2`
isogeny-graph classification, which `harness/isogeny_class.py`'s own
`velu_odd` explicitly refuses to build (`ell` must be odd — see that
function's docstring) and no other committed module provides one. This is
recorded as a budget/infrastructure-scope gap on the secondary "contingency
table against volcano level" metric (per `secondary_scope`, explicitly
permitted to be `not_computed`), not as a finding of any kind.

### 8b. Degenerate-geometry check

Zero curves, in either set, have an empty singular locus, a unit-ideal
Jacobian, or a zero elimination ideal (`singular_locus_is_unit_ideal: false`
and `elimination_empty: false` on all 276 curves — checked programmatically,
not asserted).

### 8c. Control-set spread

Full multiset (not just cardinality), from `control-set-invariants.json`:

- `S_3` support: `{13: 138}`
- singular-locus dim: `{0: 138}`
- singular-locus degree: `{6: 138}`
- regularity: `{5: 138}`
- elimination degree: `{3: 138}`
- elimination partition: `{(1,2): 63, (3,): 49, (1,1,1): 26}`
- Betti table: the one table in §4, on all 138

The control set is **concentrated, not spread**, on six of the seven
families (identical to the class); it is **more spread** than the class on
the seventh (three partition types against the class's two, including a type
absent from the class entirely).

### 8d. `m=3` vs `m=4` consistency

`m=4` support and singular locus (dimension, degree) were computed for all
276 curves (required by `arities.secondary_scope`; Betti table/regularity at
`m=4` were **not computed**, explicitly `not_computed` for budget, as the
contract permits).

- Singular-locus dimension at `m=4`: constant, `{2: 138}` on the class and
  `{2: 138}` on the control set.
- Singular-locus degree at `m=4`: constant, `{60: 138}` on the class and
  `{60: 138}` on the control set.
- **`S_4` monomial support is NOT perfectly constant**: class multiset
  `{227: 136, 225: 1, 210: 1}`; control multiset `{227: 137, 225: 1}`.

Per the required consistency check, the two class outlier curves are named
explicitly (both gauge-stable — identical `s4_support` before and after the
gauge transform):

| a | b | j | `s4_support` | gauge `s4_support` |
|---:|---:|---:|---:|---:|
| 1509 | 1006 | 1153 | 225 | 225 |
| 441 | 294 | 2257 | 210 | 210 |

`S_4` support is a **secondary** metric (`metrics.secondary`, not one of the
seven `metrics.primary` families that drive §7's verdict), so this deviation
does not itself change the emitted verdict — it is reported here in full
because the tail check requires it, not because it is folded into
`CLASS-VARYING`.

---

## 9. Deviations from the approved protocol

**D1 (implementation defect, self-caught before the run that is reported
above; no run record affected).** The first version of
`build_m3_m2_script`/`compute_curve_m3_m2` (a) used `**` for exponentiation
in the generated Macaulay2 source, which Macaulay2 parses as its own tensor-
product operator rather than an error, silently producing a wrong ideal and a
spuriously "different" support/singular-locus/Betti readout; and (b) did not
compute an elimination polynomial or its factorisation at all, so every
`elimination_factor_partition` cross-check would have spuriously disagreed
with Singular's non-empty value regardless of curve. Caught by an isolated
single-curve unit check (`compute_curve_m3_m2(7, 11, 4001)` compared against
`compute_curve_m3(7, 11, 4001)`) run against this task's own dry-run scratch
output — **before** `RUN-ICINV-e0cd8f-m3class` (the one run recorded under
`experiments/EXP-ICINV-e0cd8f/runs/`) was started. Both defects were fixed
(`**` → `^`; added `eliminate`/`factor` calls to the M2 script and matching
parse logic) and the fix was re-verified on the same single curve
(bit-for-bit signature match) before the real run was launched. No
`experiments/EXP-ICINV-e0cd8f/runs/` directory was ever written under the
defective code — the defect is disclosed here as a development-time finding,
not as a defective run record, because AGENTS.md rule 9 requires recording
every deviation and unexpected observation encountered while producing this
result, not only ones that reached a committed run.

**D2 (reported, not a defect).** M2's own `regularity` builtin, evaluated on
the homogenised ideal, returned a value one higher than `max(j-i)` computed
from that SAME run's own Macaulay2-produced Betti table, even though the
Betti table itself agreed with Singular's entry-for-entry. This is a
convention difference (which object — the ideal or its quotient — the
builtin's regularity is computed for), not a computational disagreement. The
harness derives `regularity` from the betti table Directly in both backends
(§4), never from either backend's own `regularity` command, which removes the
ambiguity; the M2 builtin's raw value is retained under
`regularity_m2_builtin` in every M2 cross-check row for transparency but is
never compared against anything.

**No other deviation from the frozen contract occurred.** In particular:
`harness/semaev.py` and `harness/isogeny_class.py` were not edited (both are
read-only imports in `harness/exp_icinv_e0cd8f.py`, confirmed by this run's
own `source_provenance` block, `code.source.modified: []`); no factor-base
membership polynomial `f_V` appears anywhere in `harness/exp_icinv_e0cd8f.py`
(grep-checkable: the module never imports or reproduces
`harness.semaev.build_factor_base` or `measure_s3_decomposition`); the
grading is exactly as declared (`x0`-homogenisation, standard grading,
`degrevlex` primary / `lp` cross-check); no p-value, permutation test, or
dispersion statistic appears anywhere in any of this run's JSON artifacts.

---

## 10. Scope and honesty (restated from the handoff)

Toy scale throughout: `p = 4001` (~12 bits), one trace `t = 30`, one isogeny
class of 138 curves, arities `m ∈ {3, 4}`. `claim_tier: toy`, `sota_delta:
0`. No run of this contract supports or rejects an ECDLP cost claim in either
direction, and — per the contract's own explicit design rationale (§"WHY THE
FACTOR-BASE MEMBERSHIP POLYNOMIALS f_V ARE REMOVED") — removing `f_V` is what
makes any result here **non-transferable** to the solving time of the
deployed, `f_V`-bearing formulation the harness's `harness/semaev.py`
actually runs. `CLASS-VARYING` licenses `min_{E' ~ E} C(E')` as a campaign
target and **nothing else**; T5 remains binding and the reachability gate is
a separate contract (`EXP-VOLC-9f5571`), not this one. This report does not
characterise what the emitted verdict means for `H-ICINV-d5e351`,
`RQ-ICINV-475b5e`, or `GOAL-ENDO-001` — those are Coordinator acts on a later
ledger archive after independent review.

---

## 11. Artifact index

- `harness/exp_icinv_e0cd8f.py` — new harness module (does not edit
  `harness/semaev.py` or `harness/isogeny_class.py`).
- `experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/` — the one
  run, `completed_valid`, `CLASS-VARYING`, carrying every
  `required_artifacts` path from `specification.yaml` verbatim:
  `manifest.yaml`, `command.txt`, `environment.json`, `stdout.log`,
  `stderr.log`, `raw-result.json`, `class-census.json`,
  `support-derivation.json`, `per-curve-invariants.json`,
  `control-set-invariants.json`, `gauge-recheck.json`,
  `backend-crosscheck.json`, `koszul-indicator.json`, `verdict.json`,
  `backend-provenance.json`.
- This file:
  `coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/execution/EXP-ICINV-e0cd8f/execution_report.md`.

`certificate.kind: none` on this run — a pure measurement run makes no
discrete-log or relation claim (`raw-result.json` / `manifest.yaml:
run.result.certificate`).
