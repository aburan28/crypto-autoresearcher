# EXP-ICINV-fcb497 — implementation note

Executor: TASK-20260807-f9c69c. Contract:
`experiments/EXP-ICINV-fcb497/specification.yaml` (`status: approved`,
`approved_by: coordinator`, `approved_at: 2026-08-07`, DEC-20260807-1538f8).
The gate was re-verified in this session before any code was written.

**This note records what was built, every declared interpretation, and every
deviation and defect — including defects in the executor's own work. It states
no conclusion about the hypothesis or the heuristic.**

## Modules written (the only three permitted)

| module | responsibility |
|---|---|
| `harness/velu_stage0.py` | STAGE-0 retrieval by `curl`, sha256 pinning, text extraction, frozen-term passage location, byte-exact quotation re-verification, mechanical passage classification, the frozen verdict rule. No domain arithmetic. |
| `harness/exp_kerfield.py` | prime ladder, deterministic curve stream, order certificate, norm-form minimisation over `Z[pi]`, `lambda`, verified factorisation, `ord_d(lambda)`, matched null, planted control, m=1 fixture, cost accounting, KS/quantile statistics, analytic peak memory. |
| `harness/run_kerfield.py` | run driver and manifest writer; stages 0/1/2/3/decide; barrier table; concrete-cost table; tail checks; decision-rule evaluation. |

`harness/toycurve.py` and `harness/runner.py` are imported **unmodified**.
`harness/exp_icinv.py`, `harness/exp_icinv_fullgroup.py`,
`harness/run_fullgroup.py`, `harness/run_saturation.py` and
`harness/isogeny_class.py` were neither edited nor imported (`git status`
confirms they are untouched). No file outside
`experiments/EXP-ICINV-fcb497/` and the three new harness modules was written.

## Run-source pinning (CORR-20260807-911ef7) — the reason the driver writes its own manifest

`runner.write_run` emits only six artifacts and hardcodes
`requested_policy: executor-terra`. The contract lists `harness/runner.py`
under `reused_unmodified`, and editing it would independently make this run
INVALID. `run_kerfield.finalise_run` therefore writes the manifest itself while
calling `runner.git_state()`, `runner.environment()`,
`runner.source_provenance()` and `runner.untracked_source_vs_output()`
verbatim, so the blocking `code.source` block is produced by exactly the
committed code the campaign audits. `finalise_run` refuses to write a run whose
`all_pinned` is false.

`python3 tools/check_run_source_provenance.py --experiment EXP-ICINV-fcb497
--strict` → **13 pinned, 0 unpinned, 0 unreadable**, exit 0.

## Declared interpretations of the frozen contract

Each of these is a place where the contract admitted more than one faithful
reading. The reading taken is recorded here; none changes a threshold, a branch
rule, a sample size, a seed or a search term.

1. **Prime ladder.** The contract freezes `k in {12, 14, 16, 18, 20, 22, 24}`
   (seven decades). The dispatching message to the executor said
   `k in {12,...,24}`. **The contract governs**: seven primes were computed,
   certified prime with `sympy.isprime` (BPSW), certified maximal below `2^k`
   with `sympy.nextprime(p) >= 2**k`, and recorded in every stage-2/3 manifest:
   `4093, 16381, 65521, 262139, 1048573, 4194301, 16777213`.
2. **Degree window.** `degree_window` enumerates `v != 0` literally, so `(u, v)`
   and `(-u, -v)` both appear. They yield the *same* `lambda` and the same `d`,
   so the primary statistic is unaffected; the window is provably the k smallest
   (the `v` range is expanded until `v^2 |D|/4` exceeds the current k-th best).
3. **Primary alpha vs degenerate count.** The contract says both "inadmissible
   instances are the degenerate case, excluded" and "the primary statistic uses
   the smallest-degree *admissible* alpha". Implemented as: the primary alpha is
   the smallest-degree admissible, factorisation-verified alpha in the k=5
   window; `minimiser_admissible` records separately whether the global
   minimiser itself was admissible (that flag is what `M5 degenerate_fraction`
   reports); an instance with *no* admissible alpha in the window is excluded
   with its reason. Both quantities are in the artifacts, so a reviewer can
   recompute either reading. Measured: the minimum always occurs at `|v| = 1`,
   where `gcd(u,v) = gcd(v,d) = 1` hold automatically, so
   `M5 degenerate_fraction = 0.000` at every decade and seed.
4. **Null redraw tag.** The contract fixes the first draw tag
   `f"{seed}:null:{p}:{i}"` but not the redraw. Redraws use `":r{j}"`,
   `j = 1, 2, ...`. Recorded in `matched-null.json`.
5. **m=1 fixture qualification.** "the corresponding eigenspace of pi on E[ell]
   is F_p-rational" is implemented as: `X^2 - tX + p` has a root
   `lambda mod ell` with `lambda ≡ 1` (pointwise-rational kernel) or
   `lambda ≡ -1` (the twisted case, which the contract admits provided the
   *eigenvalue computation* declares it — `eigenvalue_case` does exactly that).
   `m` is then `multiplicative_order(lambda, ell)`, **the same function stage 3
   calls**.
6. **Degeneration is an exponent statement.** `Otilde(sqrt(d)*m)` at `d = ell`
   degenerates to `Otilde(sqrt ell)` exactly when `m` does not grow with `ell`.
   `degeneration_check` therefore tests `m in {1, 2}` and reports the constant
   factor `log2(m)` beside the figure rather than absorbing it.
7. **"Flat or decreasing" decay tell.** Made numeric:
   `median(largest decade) - median(smallest decade) <= 0.01`.
8. **What counts as a retrieved FULL TEXT.** The contract freezes "a determinate
   verdict requires a retrieved full text of 2020/341 or 2020/1109 with a
   byte-verified passage". Implemented mechanically as: a PDF document whose
   extracted text exceeds 5000 characters. A landing/abstract page is not one.
   This gate is what caps the STAGE-0 verdict at AMBIGUOUS (see below).
9. **BASE_FIELD is the harder branch to fire, deliberately.** KERNEL_FIELD is
   read from the strict >=400-character window label; BASE_FIELD is read from
   the document-aware label, because its frozen condition is "with **no**
   kernel-rationality qualification" and a qualification anywhere in the same
   artifact defeats it. The asymmetry never makes the record-inverting branch
   easier to fire.
10. **Barrier-table classification** is a set of four named, deterministic rules
    (`R0`–`R4`) recorded per row: `R1` (the quoted figure counts evaluations or
    walk steps, not field operations inside one evaluation) → `exponent_changed
    = no`; `R2` (STAGE-0 not determinate) → `undetermined`; `R3` (small-ell
    rational kernel, kernel field stated in the artifact) → `no`; `R4` (kernel
    field not stated) → `undetermined`, never guessed.

## Ordering guarantees that are auditable from the artifacts

- **STAGE 0 ran first and alone**, before any other module was exercised.
- **Controls before belief.** Stage 3 refuses to start unless
  `RUN-ICINV-kf-stage2-controls/controls.json` exists on disk with a passing
  planted control; it records that file's sha256 in its own artifacts.
- **Null before KS.** Within each stage-3 run, `per-instance-measurements.json`
  and `matched-null.json` are written first; the KS input is then **read back
  from `matched-null.json` on disk**. `distributions.json.null_first_ordering`
  records the null file's sha256, its write timestamp and the KS start
  timestamp.

## Deviations, defects and anomalies — all recorded, none discarded

- **D1 (defect in the executor's own work; budget).** **13 runs were written
  against a frozen `maximum_runs: 12`.** The contract's own run accounting
  enumerates 10 core runs plus 2 of headroom and does not enumerate the separate
  aggregate `decide` run that SR7 and the required artifacts demand. Using one
  headroom slot for `decide` left one, and two superseding re-runs (D2, D3) were
  made. All runs are retained; none was deleted or edited. This is a budget
  overrun, reported for a Coordinator decision, not absorbed.
- **D2 (superseded run, retained).** `RUN-ICINV-kf-stage0` mislabels the
  2020/341 abstract passages `base_field` in its quotation tail: the
  kernel-rationality qualification (`\langle{P}\rangle`, "point in
  E(F_q) of prime order ell") sits in the same sentence but outside the frozen
  400-character window, and the braced `\langle{P}\rangle` form was not matched.
  Superseded by `RUN-ICINV-kf-stage0-v2`, which adds a document-level flag
  beside the window label. **The verdict is AMBIGUOUS in both runs and could not
  have differed**: the determinate branches are gated on retrieving a full text
  and no full text was retrievable. The classifier change was made after seeing
  stage-0 output and is disclosed as such.
- **D3 (superseded run, retained).** `RUN-ICINV-kf-stage1-barrier`'s two
  contract-required rows were anchored on a loose regex that captured an
  adjacent passage. Superseded by `RUN-ICINV-kf-stage1-barrier-v2`, whose
  anchors (`[open] The Otilde(p^{1/4})` and `h ~ p^{1/2} class members`) quote
  the intended figures byte-verified, with the `[open]` mark carried forward
  undischarged. **`M4` is identical in both runs** (177 rows, 0
  `exponent_changed = yes`, 127 `undetermined`).
- **D4 (defect in the executor's own work; artifact content).**
  `RUN-ICINV-kf-decide/tail-checks.json` `T5_memory_reconciliation` carries
  `analytic_peak_bytes` only. The measured `peak_rss_bytes`, the analytic value
  and their ratio **are** recorded for every run in
  `manifest.yaml → resources.memory_reconciliation`, and all 13 ratios (0.68 to
  1.74) lie inside the declared `[0.25, 4.0]` band. Correcting the artifact
  would require a further run, which the exhausted `maximum_runs` budget does
  not permit; reported rather than repaired unilaterally.
- **D5 (infrastructure, recorded in the stage-0 manifest).** Both PDF URLs
  (`2020/341.pdf`, `2020/1109.pdf`) return **HTTP 403** with a Cloudflare
  interstitial. This is an infrastructure outcome and is never read as a
  BASE_FIELD verdict (AGENTS.md rule 5).
- **D6 (declared substitution, contract-prescribed).** The m=1 fixture skipped
  12 curves of the frozen stream at `p_12` before finding three with three
  qualifying `ell` each; every skip is recorded with its shortfall reason in
  `controls.json → M6_m1_fixture.substitutions_declared`.
- **D7 (unexpected observation, not interpreted).** The decade-median sequence
  of `log m / log d` is **non-monotone** (seed 20260807: 0.687, 0.615, 0.647,
  0.802, 0.724, 0.723, 0.792) and the matched-null median exceeds the
  curve-derived median at almost every decade and seed. The KS distance exceeds
  its critical value at the three smallest decades for all three seeds, always
  in the DEFICIT direction, with `D` between 0.066 and 0.121 — at or below the
  contract's declared resolvable floor `D_min = 0.10` in most cells.
- **D8 (dissenting seed).** Seed 20260807 fires `OUTCOME_FAMILY_small_m`; seeds
  20260814 and 11235813 fire `OUTCOME_NULL_generic_order`. The frozen rule
  resolves to `OUTCOME_NULL_generic_order` at 2 of 3 seeds and the frozen
  calibration therefore caps any evidence record at `preliminary` with the
  dissenting seed named.
- **D11 (defect in the executor's own work; weak instrument, no verdict
  impact).** The stage-0 attribution check tokenises the contract's prose with a
  regex that keeps hyphenated compounds, so it checked `Bernstein-De`,
  `Feo-Leroux-Smith`, `Content-Type` and `Velu` and reported them absent — which
  reads as an attribution defect where there is none. A **read-only** re-check
  against the *same pinned text file* (sha256
  `15a4c1c9c7bb985d7051f15eb38943fddafa08abf268e6aa3cdd25038f4ca000`, confirmed
  identical) finds `Bernstein`, `Leroux`, `Smith` and `Faster` all present, and
  `Velu` absent only because the artifact renders the name with an accent. The
  recheck wrote nothing and altered no run record. The in-run check remains as
  recorded.
- **D9 (write-scope note).** `experiments/EXP-ICINV-fcb497/implementation.md`
  (this file) is not in TASK-20260807-f9c69c's declared `write_scope`, which
  lists only `runs/**` and `amendments/**` under the experiment. It was written
  on the dispatching message's explicit instruction; flagged for the
  Coordinator.
- **D10 (deliverable not produced).** The D8 execution report at
  `coordination/goals/GOAL-ENDO-001/batches/<BATCH>/execution/EXP-ICINV-fcb497/`
  was **not** written: no `BATCH-*` id is bound to TASK-20260807-f9c69c, and
  minting a batch identifier is Coordinator authority. Its full content was
  returned to the Coordinator in the executor's reply for staging under the
  correct batch.

## What was NOT done, and why

- No amendment was filed, because no frozen threshold, branch rule, sample size,
  seed, search term or decision rule was changed.
- No square-root Vélu implementation was written and no isogeny was evaluated;
  the contract's cost rows are **modeled lower bounds**, never measurements.
- No crypto-scale measurement exists or is possible here: computing `m` requires
  factoring `d ~ p`. PS-P256 and PS-P384 rows are MODELED under H1.
- No hypothesis, experiment or proposal status was changed; no evidence record
  was written; nothing was committed.
