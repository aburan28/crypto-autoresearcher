# TASK-20260813-ea2e96 — Report — THE LEAD PRODUCER

    goal / batch    GOAL-MLKEM-005 / BATCH-6e08fe
    role            executor
    requested policy executor-implementation
    governed by     PREREG-4, coordination/goals/GOAL-MLKEM-005/batches/
                    BATCH-6e08fe/tasks/TASK-20260813-cdcd88/prereg.md
                    sha256 ff577564dcdbb45b1b19885297ffc512888f9442dc99f2057fdf7f86f63fbbda
                    notarized in commit 1e1acf08b151dd31b4d41b8afd287d261adce1e5
    claim tier      TOY, UNCONDITIONALLY

**CLAIM TIER TOY.** Nothing in this report bears on ML-KEM security, on any
FIPS 203 parameter set, on any attack cost, or on any cost model. No number
here transports to beta = 606, d = 1420, or any other parameter set by
extrapolation, analogy, or any other route. `certificate.kind: none` — no
discrete-log solve and no factor-base relation is claimed or produced
anywhere in this task; the `D_route'` comparison below is an
INSTRUMENT/INDEPENDENCE CHECK, never a certificate.

---

## Paths this task wrote (all inside its own `write_scope`)

    coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/measure_route_reimpl.py
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/results_route_reimpl.json
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/report_route_reimpl.md   (this file)
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/command.txt
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/stdout.log
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/stderr.log
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/run_manifest.yaml

Exactly seven files, matching the dispatch queue's `artifact_paths` and the
task card's declared set. No eighth file was written; no `__pycache__` was
created (`PYTHONDONTWRITEBYTECODE=1`, `python3 -B` used throughout,
verified by directory listing after the run). `git status --short` at the
time of writing this report shows only these files (plus the manifest, not
yet written) as untracked under this task's `write_scope`, nothing else in
the working tree.

---

## (a) RC-3 — carried verbatim, NO RECOMPUTATION

Per PREREG-4 section 1, the following text is carried **verbatim** from the
frozen pre-registration, itself sourced directly from the Red Team's own
committed probe (`probe_coverage_beta_mismatch.py` /
`probe_coverage_beta_mismatch_output.json`,
`coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/reviews/TASK-20260813-6ab893/probes/`,
sha256 of the `_output.json` read by this task:
`63ea8124d898d27abb8af141ba05d9231bbc297ebbc4452fe685a329cc4f55b1`). **No
recomputation of any kind was performed for part (a).** `measure_c3lane.py`,
`results_c3lane.json`, `report_c3lane.md` and every Red Team probe file
remain untouched.

> BATCH-fbb639's coverage table (R-C-OUT-0 of results_c3lane.json) falsely
> marks hkz/L9_b15 and hkz/L11_b20 as COVERED (route_i_available: true).
> results_am4.json's gates.hkz.G_REL1.all block reports hkz only at the two
> REL1_PAIR endpoint betas per lattice (L9: 7 and 22; L11: 10 and 30) —
> never the middle beta either lattice's 3-point grid uses (L9: 15; L11:
> 20), and measure_c3lane.py never reads X_hi. **hkz/L9_b15 and
> hkz/L11_b20 are restated as UNCOVERED**, not COVERED. Two further cells,
> hkz/L9_b22 and hkz/L11_b30, cite the WRONG beta's value as their
> D_route source (the beta_lo comparison was reused instead of the true
> beta_hi comparison). **hkz/L9_b22 and hkz/L11_b30 are restated with the
> corrected TRUE beta_hi-based D_route source** — am4_X_hi compared against
> relvar's own G_REL1 X_b at basis 0 — **numerically UNCHANGED at exactly
> 0.0** for both cells (`probe_coverage_beta_mismatch_output.json`,
> `per_cell_beta_coverage_audit["hkz/L9_b22"].TRUE_beta_hi_comparison` and
> `["hkz/L11_b30"].TRUE_beta_hi_comparison`, `true_abs_deviation: 0.0` in
> both). lam1n's equivalent beta reuse is verified LEGITIMATE and is
> explicitly excluded from this correction: lam1n's X_lo == X_hi exactly at
> both lattices, so any beta's comparison genuinely is "the" comparison for
> it. **GENUINE COVERAGE NARROWS FROM 18 TO 16 OF 27**: lam1n 9/9
> unaffected, hkz 7/9 genuinely covered (L7 all 3: b5/b10/b15; L9: b7/b22;
> L11: b10/b30). **THIS SUPERSEDES THE 18/27 COVERAGE FRACTION** and the
> per-cell source attribution for these 4 named cells wherever either is
> quoted without this correction in the same sentence.

This narrowing does not reopen, reduce or extend `T-C3LANE-OPEN-PARTIAL`
(unchanged, PREREG-4 §1, carried, not re-litigated here).

Machine-readable copy: `results_route_reimpl.json.R_IV_OUT_0_RC3`.

---

## Implementation-choice declaration (PREREG-4 §2.2) — READ BEFORE THE D_route' NUMBERS BELOW

**This environment has no `fpylll` installed** (`import fpylll` raises
`ModuleNotFoundError`, verified live at run start and recorded in
`results_route_reimpl.json.environment_check`) and no other
independently-maintained lattice-reduction library is installed (checked:
no sagemath, no python-flint/pari lattice routines, no third-party BKZ/LLL
package present via `pip list`). **PREREG-4 §2.2(2)(i) and (ii) are
therefore unavailable in this environment** and are not used — this is
reported as an infrastructure fact, not asserted.

`ROUTE-I'` uses **§2.2(2)(iii): a from-scratch reduction/enumeration
routine in pure Python/numpy**, written without consulting `make_A`,
`build_basis` or `hkz_profile`'s source in `measure_am4.py` /
`measure_relvar.py` / `replicate_l7l8.py` or any descendant (explicitly
including `BATCH-4ed139`'s `replicate_l7l8.py`), specifically:

1. **Basis construction** reconstructs the SAME numeric matrix `A` from the
   frozen, already-public seed formula
   (`default_rng([1,d,k,i]).integers(0,q,(k,d-k))`) — per PREREG-4 §2.2(3)
   this is explicitly NOT code-sharing (producing an identical, publicly
   declared input independently, exactly what every route in this corpus,
   including ROUTE-P, already does). The `[[I_k,A],[0,qI_{d-k}]]` block
   structure is used because it is the *definition* of the lattice being
   measured, not a copied routine.
2. **The reduction/enumeration step** — the step `hkz_profile()` performs
   in the barred lineage — is replaced by a separate, independently written
   implementation:
   - a standard floating-point **LLL reduction** (Lenstra–Lenstra–Lovász,
     `delta=0.99`), written from the textbook recursion with incremental
     Gram–Schmidt/`mu`-matrix bookkeeping, using only `numpy` dot products
     and no `fpylll` call anywhere;
   - a from-scratch depth-first **Schnorr–Euchner-style enumeration**
     (also textbook, *not* `fpylll.Enumeration`) run on top of the LLL
     basis to find the **exact** shortest nonzero lattice vector
     (`lambda_1`), bounded by the LLL vector's own norm as the starting
     search radius, with per-basis time caps.
3. **`lam1n'`** is computed from the exact enumerated `lambda_1` wherever
   enumeration completes within its per-basis cap:
   `lam1n'(L,i) = exp(0.5*log(lambda_1^2) - logdet/d)`. Because HKZ
   reduction's own defining property makes its first vector equal to
   `lambda_1` exactly, an exact independently-found `lambda_1` is
   **mathematically the identical quantity** ROUTE-P's HKZ pipeline reports
   at index 0, regardless of which algorithm found it — a genuine,
   algorithm-independent check for `lam1n` specifically. Any basis whose
   enumeration does not finish within its cap is flagged
   `svp_exact: False` and its LLL-only upper bound is **excluded from that
   cell's matched-basis count**, never silently reported as exact (see
   §Deviations below — 3 of the 8 `L11` bases hit this).
4. **`hkz'(L,beta,i)`** is computed from the GSO tail of the **same
   LLL-reduced (delta=0.99) basis**:
   `hkz'(L,beta,i) = mean_{j>=d-beta}(log||b*_j||) - logdet/d` — exactly
   PREREG-4/PREREG-3's own formula for the observable, but evaluated on an
   **LLL-quality** reduced basis rather than ROUTE-P's full
   BKZ-pass + explicit-HKZ-sweep + independent-enumeration-verification
   pipeline. **THIS IS AN EXPLICIT, STATED LIMITATION, NOT HIDDEN**: unlike
   `lam1n` (whose index-0 value is algorithm-independent by definition once
   the true minimum is found), the GSO tail profile at indices `1..d-1` of
   a merely-LLL-reduced basis is **not** certified to equal the profile of
   an HKZ-reduced basis. Any `hkz'` `D_route'` reported below may reflect
   **real reduction-quality differences between LLL and full BKZ/HKZ**, in
   addition to (or instead of) genuine cross-implementation noise. This is
   reported as measured, without claiming it isolates code-sharing from
   reduction-quality as a cause — see Interpretation caveat below.
5. `logdet(L) = (d-k)*log(q)` is used as the closed-form determinant
   (exact for `B = [[I_k,A],[0,qI_{d-k}]]`, independent of `A` and of any
   reduction) — a basic linear-algebra fact, not a transcription of any
   barred function.
6. No `fpylll` import, no `fpylll` call, and no import of `measure_am4.py`
   / `measure_relvar.py` / `replicate_l7l8.py` or any function from them
   appears anywhere in `measure_route_reimpl.py` (checkable by `grep`
   against the committed script).
7. `results_l7l8.json` and `results_am4.json` are **never read** anywhere
   in this script (checkable by `grep`); confirmed by direct inspection —
   they are excluded as a `ROUTE-P` source per PREREG-4 §2.1.

---

## Obligation 0 — coverage audit (R-IV-OUT-1), computed BEFORE any `D_route'`

Read (never recomputed) from `results_relvar.json`'s own `G_REL1` block
(sha256 `c5b2918dccf1b58261eed1e9d221f1074ae6143f2a8fc5c0f42ff475646ccd6d`).
`results_l7l8.json` and `results_am4.json` were **never used** as a
`ROUTE-P` source anywhere in this task (verified by grep against the
committed script; confirmed no other read of either path exists in
`measure_route_reimpl.py`).

| cell | beta | `beta_lo` | `beta_hi` | covered | n_bases |
|---|---|---|---|---|---|
| lam1n/L7_b5 | 5 | 5 | 15 | YES | 8 |
| lam1n/L7_b10 | 10 | 5 | 15 | NO (middle beta) | 0 |
| lam1n/L7_b15 | 15 | 5 | 15 | YES | 8 |
| lam1n/L9_b7 | 7 | 7 | 22 | YES | 8 |
| lam1n/L9_b15 | 15 | 7 | 22 | NO (middle beta) | 0 |
| lam1n/L9_b22 | 22 | 7 | 22 | YES | 8 |
| lam1n/L11_b10 | 10 | 10 | 30 | YES | 8 |
| lam1n/L11_b20 | 20 | 10 | 30 | NO (middle beta) | 0 |
| lam1n/L11_b30 | 30 | 10 | 30 | YES | 8 |
| hkz/L7_b5 | 5 | 5 | 15 | YES | 8 |
| hkz/L7_b10 | 10 | 5 | 15 | NO (middle beta) | 0 |
| hkz/L7_b15 | 15 | 5 | 15 | YES | 8 |
| hkz/L9_b7 | 7 | 7 | 22 | YES | 8 |
| hkz/L9_b15 | 15 | 7 | 22 | NO (middle beta) | 0 |
| hkz/L9_b22 | 22 | 7 | 22 | YES | 8 |
| hkz/L11_b10 | 10 | 10 | 30 | YES | 8 |
| hkz/L11_b20 | 20 | 10 | 30 | NO (middle beta) | 0 |
| hkz/L11_b30 | 30 | 10 | 30 | YES | 8 |

**COVERED = 12 / 18**, exactly matching PREREG-4's stated expectation
(§2.1, §G-4 of the dispatch queue): all 6 middle-beta cells
(`L7_b10`, `L9_b15`, `L11_b20` for both candidates) are genuinely
`UNCOVERED` because `results_relvar.json`'s own `G_REL1` block has per-basis
ground truth only at each lattice's two `REL1_PAIR` endpoint betas. This is
this task's own obligation-0 verification, not an assumption carried from
the Coordinator's read.

**`s_c^fib` path resolution (protocol note, recorded per AGENTS.md rule 12 /
`agents/executor.md` #10 — not a defect this task may fix, only report):**
PREREG-4 §2.1 names the `s_c^fib` path as
`results_relvar.json.per_candidate.<X>.per_cell.<L>_<b>.float_sd`;
`results_relvar.json` has **no top-level `per_candidate` key**. The field
matching PREREG-4's own description (`float_sd` of the candidate's raw
value over the 8 frozen bases at fixed `(L, beta)`) is found at
`G_VAR.per_candidate.<X>.per_cell.<L>_<b>.float_sd` and is used here,
read-only, with this resolution stated rather than silently assumed. No
value was computed, altered, or interpreted differently than PREREG-4
describes — only the JSON path prefix differs from the prose.

---

## Obligation 1 — `D_route'` / `VERDICT'` per covered cell (R-IV-OUT-2)

`VERDICT'(X,L,b) = EXCEEDS` if `s_c^fib(X,L,b) > D_route'(X,L,b)`, else
`DOES NOT EXCEED` (ties resolve to `DOES NOT EXCEED`) — PREREG-3 §3.3's own
formula, reused verbatim, exactly as PREREG-4 §2.4 requires.

| cell | matched bases | `s_c^fib` | `D_route'` | `VERDICT'` | agrees with `BATCH-fbb639` EXCEEDS |
|---|---|---|---|---|---|
| lam1n/L7_b5 | 8/8 | 0.0433925 | 2.220446e-15 | EXCEEDS | yes |
| lam1n/L7_b15 | 8/8 | 0.0433925 | 2.220446e-15 | EXCEEDS | yes |
| lam1n/L9_b7 | 8/8 | 0.0847592 | 2.664535e-15 | EXCEEDS | yes |
| lam1n/L9_b22 | 8/8 | 0.0847592 | 2.664535e-15 | EXCEEDS | yes |
| lam1n/L11_b10 | 5/8 | 0.0388474 | 9.992007e-15 | EXCEEDS | yes |
| lam1n/L11_b30 | 5/8 | 0.0388474 | 9.992007e-15 | EXCEEDS | yes |
| hkz/L7_b5 | 8/8 | 0.0238880 | 5.861709e-02 | DOES NOT EXCEED | no |
| hkz/L7_b15 | 8/8 | 0.0088797 | 1.529305e-02 | DOES NOT EXCEED | no |
| hkz/L9_b7 | 8/8 | 0.0128880 | 1.076313e-01 | DOES NOT EXCEED | no |
| hkz/L9_b22 | 8/8 | 0.0038927 | 4.993140e-02 | DOES NOT EXCEED | no |
| hkz/L11_b10 | 8/8 | 0.0101094 | 2.234585e-01 | DOES NOT EXCEED | no |
| hkz/L11_b30 | 8/8 | 0.0038183 | 9.637448e-02 | DOES NOT EXCEED | no |

**`lam1n/L11_*` matched only 5/8 bases**: 3 of the 8 `L11` bases
(basis indices 1, 5, 6) did not finish exact SVP enumeration within their
150 s per-basis cap (each ran a full 150 s of Schnorr–Euchner search
without terminating: 19.6M / 18.4M / 19.4M nodes explored, timeout
recorded, LLL-only upper bound reported instead and correctly excluded
from the matched count — see `route_i_prime_per_basis_log` in
`results_route_reimpl.json` for the per-basis timing/exactness of every
one of the 24 bases actually computed). This reduces the matched-basis
count for `lam1n/L11_b10` and `lam1n/L11_b30` from 8 to 5; the reported
`D_route'` uses only the 5 exact bases. This is reported per PREREG-4
§2.4.1 ("report the exact subset size used"), not silently merged with the
8-basis cells.

Full per-basis detail (all 24 basis reductions actually run: `L7`×8,
`L9`×8, `L11`×8; LLL/enumeration timings, node counts, exactness flags) is
in `results_route_reimpl.json.route_i_prime_per_basis_log`.

**No cell was `NOT COMPUTED: budget exhausted`** at the cell level — every
one of the 12 `COVERED` cells produced a `D_route'`/`VERDICT'` (the internal
compute deadline, 1500 s, was never reached; total computation took 981.52
s of this task's 1800 s budget).

---

## Obligation 2 — aggregate (R-IV-OUT-3)

    COVERED         = 12 / 18
    ALL-SURVIVE      = False
    SOME-ARTIFACT    = True   (at least one covered cell VERDICT' = DOES NOT EXCEED)

    EXCEEDS cells (6):          lam1n/L7_b5, lam1n/L7_b15, lam1n/L9_b7,
                                 lam1n/L9_b22, lam1n/L11_b10, lam1n/L11_b30
    DOES NOT EXCEED cells (6):  hkz/L7_b5, hkz/L7_b15, hkz/L9_b7,
                                 hkz/L9_b22, hkz/L11_b10, hkz/L11_b30
    UNCOVERED cells (6):        lam1n/L7_b10, lam1n/L9_b15, lam1n/L11_b20,
                                 hkz/L7_b10, hkz/L9_b15, hkz/L11_b20
    NOT COMPUTED (budget) (0):  none

---

## Termination branch (R-IV-OUT-4) — PREREG-4 §2.6's frozen precedence

**`COVERED` is non-empty and `SOME-ARTIFACT` holds** (at least one covered
cell — in fact all 6 `hkz` covered cells — has `VERDICT' = DOES NOT
EXCEED`). Per PREREG-4 §2.6: *"T-INDVERIFY-ARTIFACT — FIRES WHEN COVERED is
non-empty and SOME-ARTIFACT holds."* `|COVERED| = 12 < 18`, so the
`-PARTIAL` suffix applies per §2.6's own rule.

### BRANCH FIRED: `T-INDVERIFY-ARTIFACT-PARTIAL`

**Per PREREG-4 §2.6's own precedence-and-per-cell rule, quoted:** *"A batch
that fires T-INDVERIFY-ARTIFACT at some cells and would independently have
fired T-INDVERIFY-CONFIRMED at others reports BOTH: the flagged cells under
T-INDVERIFY-ARTIFACT's license, the surviving cells under
T-INDVERIFY-CONFIRMED's."* Applying that per-cell rule exactly as this
document's data requires:

- **The 6 `lam1n` covered cells** (`L7_b5`, `L7_b15`, `L9_b7`, `L9_b22`,
  `L11_b10`, `L11_b30`) independently satisfy `ALL-SURVIVE` among
  themselves (`VERDICT' = EXCEEDS` at every one, `D_route'` at machine
  epsilon, `1.3e-15` to `1.0e-14`) — these fire under
  **`T-INDVERIFY-CONFIRMED`'s license**: for these cells only,
  `BATCH-fbb639`'s `EXCEEDS` verdict may be cited WITHOUT F-1/RT-1's
  "not under independent verification" qualification.
- **The 6 `hkz` covered cells** (`L7_b5`, `L7_b15`, `L9_b7`, `L9_b22`,
  `L11_b10`, `L11_b30`) all show `VERDICT' = DOES NOT EXCEED` and fire
  under **`T-INDVERIFY-ARTIFACT`'s license**: per PREREG-4 §2.6, quoted
  from `DEC-20260813-28d7b2`'s `next_actions` verbatim, *"if D_route grows
  toward s_c^fib's scale, the EXCEEDS verdicts reported in \[BATCH-fbb639\]
  were a methodological artifact of code-sharing, not a finding about
  lam1n/hkz, and that must be recorded as such rather than argued away."*
  These 6 cells' `BATCH-fbb639` `EXCEEDS` verdicts must be flagged
  methodologically unsupported in a superseding record (§2.8 revisit
  condition), and no successor may cite them without that flag.
- **UNCOVERED**: the 6 middle-beta cells remain UNCOVERED and decided in
  neither direction; F-1/RT-1's qualification continues to apply there,
  unchanged.

**What this branch LICENSES, stated exactly as PREREG-4 states it:** for
`lam1n`'s 6 covered cells, citing `BATCH-fbb639`'s `EXCEEDS` without the
code-sharing qualification; for `hkz`'s 6 covered cells, recording a
methodological-artifact flag on those specific past verdicts. **What it
FORBIDS**: retroactively changing `T-C3LANE-OPEN-PARTIAL` itself (unchanged,
`BATCH-fbb639`'s own frozen-clause outcome); any claim about `ML-KEM`, any
FIPS 203 parameter set, any attack cost or any cost model; closing, pausing
or completing `GOAL-MLKEM-005`; extending either license to any UNCOVERED
cell.

---

## Interpretation caveat on the `hkz` `DOES NOT EXCEED` reading (recorded, not resolved here)

Per the implementation-choice declaration above, `hkz'` is computed from an
**LLL-quality** (not HKZ-quality) reduced basis, by explicit necessity of
this run environment lacking `fpylll` or any alternative reduction library
and the resulting infeasibility, within this task's 1800 s budget, of a
from-scratch full BKZ+HKZ-sweep implementation at `d` up to 40 in pure
Python. The `D_route'` values reported for `hkz` (`0.015` to `0.223`) are
**at least as consistent with a real reduction-DEPTH gap between LLL and
ROUTE-P's HKZ pipeline as with a finding about code-sharing** — this task
cannot and does not distinguish the two causes, and does not claim to. This
is reported as the measured, honest limit of what this task's own
infrastructure could reach, not resolved in either direction; a
higher-fidelity independent `hkz'` route (e.g. with `fpylll` installed, or
a from-scratch full HKZ implementation given more budget) is the natural
successor measurement, named here as a revisit condition rather than
pursued further under this task's budget. By contrast, `lam1n'`'s `EXCEEDS`
finding does NOT carry this caveat: `lambda_1` is an algorithm-independent
lattice invariant, and an exact enumeration finding the identical value (to
`1e-15`-scale floating-point residual) as ROUTE-P's HKZ pipeline, via a
provably different code path, is a comparison on equal mathematical
footing regardless of preprocessing quality.

This paragraph is an **observation**, not an interpretation of what the
Validator/Red Team/Coordinator should conclude — per `agents/executor.md`
#9 and the Executor's prohibition on declaring a hypothesis supported,
rejected, refuted or closed. It exists only so the caveat is not missed
between this report and any later reading.

---

## Deviations from the frozen protocol, recorded per `agents/executor.md` #10/#12

1. **`fpylll` unavailable; no alternative reduction library available.**
   PREREG-4 §2.2(2) options (i)/(ii) could not be used; option (iii) (a
   from-scratch pure Python/numpy routine) was used instead, as PREREG-4
   itself anticipates and licenses. This is INFRASTRUCTURE SIGNAL, reported
   as such, never as a negative result of any kind.
2. **`hkz'` uses an LLL-quality profile, not an HKZ-quality profile**,
   for the reasons stated in the implementation-choice declaration and the
   interpretation caveat above. This is a genuine scope limit of this
   task's infrastructure and budget, stated explicitly rather than hidden.
3. **`s_c^fib` JSON-path resolution**: PREREG-4 §2.1's stated path
   (`results_relvar.json.per_candidate...`) does not exist verbatim in
   `results_relvar.json`; the matching field is at
   `G_VAR.per_candidate...float_sd`. Recorded above; read-only, no value
   altered.
4. **3 of 8 `L11` bases (indices 1, 5, 6) did not complete exact SVP
   enumeration within their 150 s per-basis cap** and are excluded from
   the `lam1n/L11_*` matched-basis count (reduced from 8 to 5), rather than
   silently included at their LLL-only upper bound. Recorded per-basis in
   `results_route_reimpl.json.route_i_prime_per_basis_log`.
5. **No cell hit the task-level "NOT COMPUTED: budget exhausted" guard**
   (PREREG-4 §3.2) — total computation completed in 981.52 s against an
   internal 1500 s compute deadline and the task's overall 1800 s budget.
   This guard exists in the committed script (`COMPUTE_DEADLINE_SECONDS`,
   `PER_BASIS_LLL_CAP`, `PER_BASIS_ENUM_CAP`) and would have fired had the
   deadline been reached; it was not needed this run.

No other deviation from PREREG-4 occurred. No committed artifact of any
prior batch (`measure_relvar.py`, `results_relvar.json`, `replicate_l7l8.py`,
`results_l7l8.json`, `measure_am4.py`, `results_am4.json`,
`measure_c3lane.py`, `results_c3lane.json`, any prior report, any ledger
record, PREREG-1/2/3/4) was edited, re-run, or vendored. No reduction above
`d = 40` was performed anywhere, at any point (verified: the only `d`
values ever passed to `lll_reduce`/`enumerate_svp` are 20, 30, 40 — see
`LATTICES` in the committed script).

---

## Environment (measured)

    python_version   see run_manifest.yaml
    numpy            2.4.6
    scipy            (not used by this script)
    fpylll           NOT INSTALLED (ModuleNotFoundError)
    host / platform  see run_manifest.yaml
    total wall clock 981.52 s (of an 1800 s budget)
    max_runs         1 (single invocation; command.txt records it)

---

## Executor's own assessment (observation, not interpretation)

Every planned obligation of PREREG-4 part (b) ran to completion: obligation
0 (coverage audit) verified 12/18 genuinely covered, matching the
prereg's stated expectation; obligation 1 computed `D_route'`/`VERDICT'`
at all 12 covered cells with no budget-exhaustion gaps; obligation 2's
aggregate and the §2.6 termination branch were read off exactly as
specified, per-cell, with the `-PARTIAL` suffix applied per its own rule.
The one substantive infrastructure limitation (`fpylll` unavailable,
forcing an LLL-quality rather than HKZ-quality `hkz'` route) is disclosed
in the implementation-choice declaration and interpretation caveat above,
not smoothed into the result.
