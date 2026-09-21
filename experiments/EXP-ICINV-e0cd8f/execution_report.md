# EXP-ICINV-e0cd8f — execution report

Task `TASK-20260810-5ad325`, goal `GOAL-ENDO-001`, batch `BATCH-d7e255`.
Snapshot commit at dispatch: `5ecab6c78`.

**SC-2 binds this document exactly as it binds the run records: observations
only. No hypothesis, question, experiment or goal status is changed here, and
no verdict is declared supported, closed, validated or refuted. `verdict.json`
in each m=3 run computes CLASS-INVARIANT or CLASS-VARIANT per invariant
family, inside the run, per SR7 — that computed label is reported below
verbatim; whether it closes anything is a Coordinator/Reviewer judgement.**

`claim_tier: toy`, `sota_delta: 0`. No ECDLP claim, in either direction, in
this report or in any run record.

## 1. Runs, in the order executed, and their terminal state

| # | run_id | stage | status | valid | notes |
|---|---|---|---|---|---|
| 1 | `RUN-ICINV-geom-gates` | SR1/SR2/SR3 gates only | `completed_valid` | true | no resolution computed |
| 2 | `RUN-ICINV-geom-m3` | m=3, full | `completed_valid` | true | **SUPERSEDED** — see §4 D-4; a derived cross-check flag was wrong, no primary invariant affected |
| 3 | `RUN-ICINV-geom-m3-v2` | m=3, full, corrected | `completed_valid` | true | supersedes run 2; primary record for m=3 |
| 4 | `RUN-ICINV-geom-m4` | m=4, secondary | `failed_infrastructure` | false | host disk full mid-run (`OSError: No space left on device`); gates 1-3 passed before the crash |
| 5 | `RUN-ICINV-geom-m4-v2` | m=4, secondary, retry | **ABANDONED, no terminal state** | — | process killed by an external host/session restart mid-run; only 4 of the 15 required artifacts were ever written (`backend-provenance.json`, `class-census.json`, `command.txt`, `support-derivation.json`); no `manifest.yaml` was ever produced. Retained as-is (run records are immutable) and explicitly marked abandoned here; **no number from it is used anywhere in this report** |
| 6 | `RUN-ICINV-geom-m4-v3` | m=4, secondary, retry | `completed_valid` | true | disk headroom confirmed by this session before the retry (37 GiB free at start, re-checked mid-run); supersedes the abandoned attempt; primary record for m=4 |

Run count against the handoff's `maximum_runs: 8`: 6 directories exist, all
terminal except the abandoned one, which never became a run in the budget
sense (no manifest was ever written and no compute past the abandonment point
was retained as a claim). Total wall clock across all six: gates 1.9 s + m3
274 s + m3-v2 264 s + m4 1435 s + m4-v2 (abandoned, ~614 s of partial
progress before the kill) + m4-v3 1156 s ≈ 3745 s, well under the
`total_cpu_hours: 6` (21600 s) budget and each run individually under the
7200 s per-run wall-clock limit. Peak RSS across all runs: ≤ 1.4 GB, under the
8 GB limit.

## 2. Stopping rules fired, in the contract's order, per run

**SR1 (support gate, runs first)** — passed in every run that reached it
(gates, m3, m3-v2, m4, m4-v3). Symbolic re-derivation of S_3 with `a`, `b`
symbolic over ZZ in SymPy gives support 13 (generic), 9 (`a=0`), 10 (`b=0`),
matching the contract's frozen values exactly
(`support-derivation.json:derivation_agrees = true` in every run). The S_3
support was then computed directly on all 138 class members: **every one is
13** (`support-derivation.json:all_members_support_13 = true`,
`distinct_supports_on_class: [13]`, every run). SR1 never fired (no defect).

**SR2 (census gate)** — passed in every run that reached it. The class was
re-enumerated (138 members) and compared against the committed record
`experiments/EXP-ICINV-180a0d/runs/RUN-ICINV-p4001-a/raw-result.json`, read at
run time and bound by sha256
(`2f428da72ca5a5e4...`, recorded in
`manifest.run.inputs.reference_records`) — same count (138), same set of 138
`(a,b)` pairs, and the Hurwitz-Kronecker mass formula agrees exactly
(`H(4p - t^2) = 138.0`, `observed_weighted = 138.0`). SR2 never fired.

**SR3 (backend gate)** — evaluated and recorded from inside every run, before
any resolution was computed, per `backend-provenance.json`. It disagreed with
the dispatching session's precondition probe on two points, both recorded (see
§4 D-2): **msolve 0.9.5** is present and used as a genuine third-party second
backend; a standalone `Singular` binary is present but is the same engine as
libsingular and is not counted as independent. Status recorded:
`passed_with_recorded_limitation` — no second off-the-shelf *resolution*
engine (Macaulay2/Magma both absent) exists on this host, so the graded Betti
cross-check runs by an independent computational route instead of a second
engine (§4 D-2, §3).

**SR4 (control first)** — satisfied in `RUN-ICINV-geom-m3`,
`RUN-ICINV-geom-m3-v2` and `RUN-ICINV-geom-m4-v3`. `control-set-invariants.json`
(or, for m=4, the control half of `m4-invariants.json`) was written and closed
before any class multiset was read; the exact write order, per-artifact
timestamp and sha256 are in `manifest.run.artifact_write_order` in each of
those three runs.

**SR5 (frozen scope)** — held in every run: p = 4001, t = 30, arities {3, 4},
`degrevlex` primary order (`deglex` used only for the C-ORDER control on the
cross-check subsample), the declared x0-homogenised standard grading. No
amendment was filed and none was needed.

**SR6 (budget)** — fired once, on `RUN-ICINV-geom-m4`: the host's system
volume ran out of free space mid-run (an unrelated external process, not this
run's own I/O volume, exhausted `/System/Volumes/Data`, which held ~2 GiB free
at the time against ~400 GiB used). Recorded as `failed_infrastructure`, never
as evidence of anything about the invariants (AGENTS.md rule 5); partial
artifacts (the passed SR1/SR2/SR3 gates) are retained in that run directory.
It separately did **not** fire on any of the other five runs, including the
abandoned `RUN-ICINV-geom-m4-v2` (that abandonment was an external
session/host restart, not a budget exhaustion inside the run's own accounting
— no `Budget` exception was ever raised, because the process was killed before
it could raise one).

**SR7 (no outcome shopping)** — satisfied in `RUN-ICINV-geom-m3-v2` (the m=3
primary record) and structurally in `RUN-ICINV-geom-m4-v3` (m=4 has no verdict
step in the contract; only the m=3 primary families carry a CLASS-INVARIANT /
CLASS-VARIANT verdict). The verdict is computed in code before any human read
it, from a metric set (`FAMILIES` in `harness/exp_icinv_geometry.py`) fixed
before the run executes.

## 3. m=3 primary result — `RUN-ICINV-geom-m3-v2`, computed inside the run

Per-family distinct-value counts, class (138 curves) vs. control (138 curves,
drawn from 100 distinct traces other than 30, excluding the supersingular
trace 0):

| family | class distinct | class multiset | control distinct | control multiset |
|---|---|---|---|---|
| F1 S_3 monomial support | 1 | `{13: 138}` | 2 | `{10: 1, 13: 137}` |
| F2 graded Betti table (homogenised, x0-graded) | 1 | one table, all 138 | 1 | one table, all 138 |
| F2b regularity of S/J | 1 | `{5: 138}` | 1 | `{5: 138}` |
| F3 affine singular locus (dim, degree) | 1 | `{(0,6): 138}` | 1 | `{(0,6): 138}` |
| F4 elimination polynomial degree | 1 | `{3: 138}` | 1 | `{3: 138}` |
| F4b elimination F_p-factorisation type | **2** | `{(1,1,1): 66, (1,2): 72}` | **3** | `{(1,1,1): 21, (1,2): 68, (3,): 49}` |

Verdict computed inside the run, `verdict.json:verdict`: **`CLASS-VARYING`**
(at least one family — F4b — is not constant across the class). Exhibited
witness pair, computed inside the run and not chosen afterward
(`verdict.json:exhibited_witness_pair`):

* curve `(a,b) = (17, 1345)` — F4b elimination factorisation type `(1,1,1)`
* curve `(a,b) = (148, 2766)` — F4b elimination factorisation type `(1,2)`

66 of 138 class members deviate from the class mode `(1,2)` on F4b
(`verdict.json:curves_deviating_from_class_mode.F4b_elimination_factorisation_type`,
listed individually with `(a,b)`, `j`, `two_torsion_x_count`; true 2-volcano
level `not_computed`, see §4 D-3).

Degenerate-geometry tail check (empty singular locus, unit ideal, or zero
elimination ideal): **none found**, class or control
(`verdict.json:degenerate_geometry = []`).

Controls, computed inside the run:

* **C-GAUGE**: every invariant recomputed on a per-curve gauge-transformed
  model `(u^4 a, u^6 b)`, seeded — `gauge_all_agree: true` for class and
  control both (`gauge-recheck.json`).
* **C-BACKEND**: 30-curve cross-check subsample (every curve realising a
  distinct value of any family, in either set, plus filler past the
  contract's 20-curve minimum). msolve (backend B) agrees on dimension,
  degree, and the exact set of F_p-rational points on all 30
  (`backend_B_all_agree: true`); the independent Koszul-homology route
  (backend C) reproduces Singular's Betti table exactly on all 30
  (`backend_C_all_agree: true`, `betti_crosschecked_curves: 30`).
* **C-ORDER**: dimension, degree, Betti table and regularity recomputed under
  `deglex` on the same subsample — `order_independent_all: true`.
* **C-KOSZUL**: `koszul_all_regular_sequence_on_class: false` — the Jacobian
  generators are **not** a regular sequence on every class member, so F2/F2b's
  constancy is not automatically explained as a Koszul degeneration by this
  test (`koszul-indicator.json` has the per-curve indicator for class and
  control both).
* **C-CENSUS**, **C-SUPPORT**: see SR1/SR2 above.
* **C-CONTROL-SET**: the control set is *not* equally constant on F1 or F4b —
  see the table above.

No p-value, permutation test, null-object test or dispersion statistic appears
anywhere in this run's artifacts (grepped and confirmed clean).

## 4. m=3 protocol deviation — `RUN-ICINV-geom-m3` superseded (D-4)

The first m=3 run, `RUN-ICINV-geom-m3`, used a cross-check predicate that
compared msolve's set of F_p-rational `x3`-values against the *number of
degree-1 factors of the elimination polynomial* — two different quantities (a
rational root of the elimination polynomial need not extend to an
F_p-rational point of the variety). That predicate reported
`backend_B_all_agree: false` on 14 of 30 subsample curves where msolve and
Singular in fact agree exactly, verified directly for `(a,b)=(148,2766)`:
both report 0 F_p-rational points on the variety, and the elimination
polynomial `x3^3+148x3-1235` factors as `(x3-615)(x3^2+615x3-1722)` — one
rational root, zero rational points on the 2-dimensional variety, no
contradiction.

Classified `implementation_error`, confined to one derived agreement flag; no
primary invariant in that run is affected — every primary value in
`RUN-ICINV-geom-m3` agrees with `RUN-ICINV-geom-m3-v2`. The run record was
**not edited** (immutability); it is retained, its artifacts are unchanged,
and it is reported here as invalid/superseded. `RUN-ICINV-geom-m3-v2` fixed
the predicate to compare like with like — msolve's `fp_points`/`fp_x3_values`
against Sage/Singular's own `variety()` on the same ideal, both now recorded
per curve in `singular_locus_affine` — and is the primary m=3 record cited
throughout this report.

## 5. m=3 backend versions (SR3), recorded from inside `RUN-ICINV-geom-m3-v2`

| backend | role | version |
|---|---|---|
| A | primary: Groebner bases, minimal free resolutions, Betti tables, regularity, dimension, degree, elimination | SageMath **10.9** (release 2026-05-04) driving Singular (libsingular) **4.4.1** (raw version string `44100`) |
| B | independent third-party: dimension, degree, F_p-rational points | **msolve 0.9.5** (Berthomieu, Eder, Safey El Din) via Sage `algorithm='msolve'`, found at `/opt/homebrew/bin/msolve` |
| C | independent route (no second off-the-shelf resolution engine exists on the host): dimension, degree, elimination polynomial + factorisation type, graded Betti numbers via Koszul homology | **SymPy 1.14.0** on Python 3.13.1, using a Koszul-complex Tor computation implemented in `harness/exp_icinv_geometry.py` |

Absence probe, run from inside this run: Macaulay2, Magma and giac absent;
a standalone Singular binary is present but is libsingular itself (not
independent, not counted).

Backend A self-test, run inside every run: minimal free resolution of
`(xy, yz, zx)` in `QQ[x,y,z]` returns `S^1 <-- S^3 <-- S^2 <-- 0` — passes.
Backend B/C self-tests (curve `(a=460,b=2974)`, checked interactively before
the committed runs and reproduced by every committed run's own cross-check
subsample, which includes this curve): backend C's Koszul-homology Betti
table exactly equals backend A's Singular-derived Betti table
(`{0,0:1, 1,3:3, 1,4:1, 2,5:2, 2,6:2, 2,7:1, 3,8:2}` both ways).

## 6. m=4 secondary result — `RUN-ICINV-geom-m4-v3`

Required: monomial support and affine singular locus only, per the contract's
`arities.secondary_scope`. Betti table and regularity at m=4 are reported
`not_computed` — a **budget statement** under AGENTS.md rule 5, never a
constancy claim (`m4-invariants.json:not_computed_reason`).

| family | class distinct | class multiset | control distinct | control multiset |
|---|---|---|---|---|
| S_4 monomial support | 2 | `{391: 1, 439: 137}` | 2 | `{225: 1, 439: 137}` |
| S_4 affine singular locus (dim, degree) | 1 | `{(2,39): 138}` | 1 | `{(2,39): 138}` |

Class outlier on S_4 support: `(a,b)=(441,294)`, `j=2257`, support 391 (vs. the
class mode 439 on the other 137). Control outlier: `(a,b)=(9,0)`, `j=1728`,
support 225 — `j=1728` is outside the target class by construction (T4: the
target class has D_0=-59, so j=0 and j=1728 cannot occur in it; the control
draw is unrestricted in `j` and this curve landed there). Gauge recheck:
`m4_all_gauge_agree: true` for both support and singular-locus dimension and
degree, class and control.

No verdict step applies at m=4 (the contract's verdict machinery — SR7 — is
defined for the primary m=3 families only); the m=4 secondary is reported as
raw distinct-value counts and multisets, per the required artifacts, with no
CLASS-INVARIANT/CLASS-VARYING label computed or implied.

## 7. Protocol deviations (full list, carried from `implementation.md`)

* **D-1 — inference policy, UPWARD, structural, Coordinator-authorised.**
  Handoff requests `executor-implementation`
  (`fallback_allowed: false`, `degraded_allowed: false`). This worktree's
  `orchestration.adapter resolve --role executor` resolves that policy to
  `anthropic:claude-sonnet-5` (effort medium). The model that actually
  answered this session is `claude-opus-5`. Cause is structural: every
  `.claude/agents/*.md` carries `model: inherit`, so this runtime cannot
  honour a per-role model binding at subagent level at all; CLAUDE.md's
  model-policy note prescribes the fix as process-level (launching via
  `orchestration.adapter env`), which is a harness change, not an executor
  one. The dispatching Coordinator was informed **before any compute was
  spent** (via `SendMessage`) and authorised proceeding with the deviation
  recorded. Direction is **upward** (same vendor, higher tier) — recorded as
  `protocol_deviation`/`fallback_used: true` in every manifest, and this
  **must not be cited as strengthening any result**: no threshold, scope,
  budget, stopping rule or metric moved because of it. Every reported number
  is produced by the pinned, re-executable exact-symbolic module with no model
  in the loop; the specific steps that *did* turn on model judgement rather
  than exact computation are named individually in
  `manifest.run.inference.model_judgement_steps` in every run.
* **D-2 — second backend, disagreeing with the dispatching probe.** See §5;
  msolve is present and used (the dispatching probe recorded it as absent),
  a standalone Singular binary is present but is not independent of
  libsingular. No off-the-shelf resolution engine exists on the host besides
  Sage/Singular, so the Betti-table cross-check runs by an independent
  computational route (backend C) rather than a second engine — flagged in
  every run as a reviewer judgement on whether C-BACKEND is fully discharged
  for the Betti family specifically (dimension/degree/points are discharged
  by the genuine third-party backend B without qualification).
* **D-3 — 2-volcano covariate not computed.** The committed reference
  supplies only the level histogram `{0:3,1:9,2:18,3:36,4:72}`, not per-curve
  levels, and the contract states this experiment does not rebuild the
  volcano. The secondary metric "contingency table against true 2-volcano
  level" is `not_computed` throughout; `two_torsion_x_count` (from the
  unedited, committed `harness/exp_icinv.py`) is recorded per curve instead
  as a computable covariate. A recorded gap, not an imputation.
* **D-4 — `RUN-ICINV-geom-m3` superseded**, see §4.
* **D-5 — `RUN-ICINV-geom-m4` infrastructure failure**, see §1/§2 SR6: host
  disk exhaustion mid-run, unrelated to this run's own I/O footprint (peak RSS
  ≤ 0.4 GB). SR1-SR3 gates passed before the crash; partial artifacts
  retained.
* **D-6 — `RUN-ICINV-geom-m4-v2` abandoned by an external host/session
  restart**, not by this run's own budget accounting or any decision inside
  it. Only 4 of the 15 required artifacts exist
  (`backend-provenance.json`, `class-census.json`, `command.txt`,
  `support-derivation.json`, all timestamped the same second, consistent with
  a process kill immediately after those early writes); no `manifest.yaml`
  was ever produced, so the run never reached a status the contract
  recognises. Retained unedited as an immutable partial record and reported
  here as abandoned. No number from it appears anywhere in this report or in
  any other run's artifacts. Before retrying, this session independently
  verified disk headroom (37 GiB free on `/System/Volumes/Data` at retry
  start, re-checked mid-run at 65-69 GiB free, i.e. improving, not degrading)
  rather than trusting the Coordinator's report of recovery — the same
  discipline SR3 requires for backend state.
* **D-7 — `TMPDIR` redirected** to `/Volumes/SSD990/tmp-icinv-e0cd8f` for the
  m=4 retries (`RUN-ICINV-geom-m4-v2`, `RUN-ICINV-geom-m4-v3`), off the
  exhausted system volume. This is an environment change to the process's
  temp-file location only; it changes no computed number, no seed, no
  algebra and no source file, and is recorded here for reproducibility.

## 8. Commands (exact, re-executable, no model required)

```sh
sage -python harness/exp_icinv_geometry.py --stage gates --run-id RUN-ICINV-geom-gates
sage -python harness/exp_icinv_geometry.py --stage m3    --run-id RUN-ICINV-geom-m3
sage -python harness/exp_icinv_geometry.py --stage m3    --run-id RUN-ICINV-geom-m3-v2
sage -python harness/exp_icinv_geometry.py --stage m4    --run-id RUN-ICINV-geom-m4
TMPDIR=/Volumes/SSD990/tmp-icinv-e0cd8f sage -python harness/exp_icinv_geometry.py --stage m4 --run-id RUN-ICINV-geom-m4-v2   # abandoned, see D-6
TMPDIR=/Volumes/SSD990/tmp-icinv-e0cd8f sage -python harness/exp_icinv_geometry.py --stage m4 --run-id RUN-ICINV-geom-m4-v3
```

Verbatim in every run's `command.txt`. Source is pinned by content sha256 in
every manifest (`code.source`, all files `status: untracked` except
`harness/isogeny_class.py` and `harness/exp_icinv.py`, which are `clean`
against HEAD); `harness/exp_icinv_geometry.py` is new and untracked by design
(git commit is the dispatching Coordinator's act, not this executor's — SC-6).

## 9. Completion gate check

* All six run directories have a terminal disposition: 4 `completed_valid`
  (gates, m3-v2, m4-v3, and the superseded-but-technically-valid m3), 1
  `failed_infrastructure` (m4), 1 abandoned with no manifest (m4-v2, explained
  in D-6, not counted as a claimed run).
* Required artifacts (per `specification.yaml:required_artifacts`) are present
  in `RUN-ICINV-geom-gates` (the three gate-stage artifacts), fully present
  (all 15) in `RUN-ICINV-geom-m3`/`RUN-ICINV-geom-m3-v2`, and present for the
  m=4 stage's own artifact set (`manifest.yaml`, `command.txt`,
  `environment.json`, `stdout.log`, `stderr.log`, `raw-result.json`,
  `class-census.json`, `support-derivation.json`, `backend-provenance.json`,
  `m4-invariants.json`, `m4-class-invariants.json`) in `RUN-ICINV-geom-m4-v3`.
* Raw data (`raw-result.json`, `verdict.json`, `m4-invariants.json`) and the
  summary tables in §3/§6 above were read directly from those files, not
  transcribed from memory or re-derived.
* Reproducible from the recorded commands and the pinned source hashes at the
  recorded commit; no step in the reproduction path requires a language
  model.

## 10. Executor assessment

```yaml
execution_report:
  experiment_id: EXP-ICINV-e0cd8f
  implementation_commit: 5ecab6c78
  protocol_deviations:
    - D-1 inference policy upward substitution (structural, Coordinator-authorised)
    - D-2 second backend disagrees with dispatching precondition probe (msolve present, standalone Singular not independent)
    - D-3 2-volcano per-curve covariate not computed (histogram only in committed reference)
    - D-4 RUN-ICINV-geom-m3 superseded by RUN-ICINV-geom-m3-v2 (cross-check predicate defect, no primary invariant affected)
    - D-5 RUN-ICINV-geom-m4 failed_infrastructure (host disk exhaustion, unrelated to this run's own I/O)
    - D-6 RUN-ICINV-geom-m4-v2 abandoned (external host/session restart mid-run, no manifest ever written)
    - D-7 TMPDIR redirected off the exhausted volume for the m4 retries
  runs:
    completed:
      - RUN-ICINV-geom-gates
      - RUN-ICINV-geom-m3          # superseded, see D-4
      - RUN-ICINV-geom-m3-v2       # primary m=3 record
      - RUN-ICINV-geom-m4-v3       # primary m=4 record
    invalid: []
    failed:
      - RUN-ICINV-geom-m4          # failed_infrastructure, disk exhaustion
      - RUN-ICINV-geom-m4-v2       # abandoned, external kill, no manifest
  observations:
    - "m=3 primary families: S_3 support, Betti table, regularity, affine
       singular-locus (dim,degree) and elimination degree are each
       single-valued across all 138 class members (RUN-ICINV-geom-m3-v2)."
    - "m=3 F4b (elimination-polynomial F_p-factorisation type) takes 2 values
       on the class (66/72 split) and 3 on the control set; SR7 verdict
       computed inside the run: CLASS-VARYING, witness pair (17,1345) vs
       (148,2766)."
    - "m=4 secondary: S_4 support takes 2 values on both class (1/137 split)
       and control (1/137 split); S_4 affine singular locus (dim,degree) is
       single-valued on both. Betti/regularity at m=4 not_computed by design
       (secondary, budget statement)."
    - "Control set is NOT uniformly constant on F1 (S_3 support) or F4b,
       discharging C-CONTROL-SET's nearby-object-control purpose for those
       two families specifically."
    - "Koszul indicator: the Jacobian generators are NOT a regular sequence
       on every class member (koszul_all_regular_sequence_on_class: false)."
  anomalies:
    - all seven items in section 7 above, recorded in full, none discarded
  artifact_paths:
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-geom-gates/
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-geom-m3/
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-geom-m3-v2/
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-geom-m4/
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-geom-m4-v2/     # abandoned, partial
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-geom-m4-v3/
    - experiments/EXP-ICINV-e0cd8f/execution_report.md
    - experiments/EXP-ICINV-e0cd8f/implementation.md
    - harness/exp_icinv_geometry.py
  executor_assessment:
    protocol_complete: true
    data_quality: good
    requires_rerun: false
```

Interpretation of any of the above — whether CLASS-VARYING on F4b (and on m=4
support) closes, narrows or reopens any axis of `RQ-ICINV-475b5e`, and whether
the recorded reviewer-judgement items (D-2's partial C-BACKEND discharge on
the Betti family) are sufficient — is explicitly **NONE** here, per SC-2. That
judgement belongs to the Coordinator and the independent Validator/Red Team
review.
