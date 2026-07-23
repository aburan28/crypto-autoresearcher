# Validator Report — GOAL-DREG-001 BATCH-002 / RUN-DREG-001-MEASURE-N12-D6

Independent artifact/control/metric/reproducibility validation. This report does
NOT change any hypothesis or experiment status, does NOT edit raw artifacts, and
does NOT interpret the science (that is Red Team + Coordinator).

```yaml
validation_report:
  id: VAL-20260721-001
  task_id: TASK-20260721-DREG-N12D6-VAL-R1
  run_ids:
    - RUN-DREG-001-MEASURE-N12-D6
  snapshot:
    commit: bedd64c26343f4d8ad3b9919c4eb3c0103b21e43
    branch: claude/dreg-linear-law
    worktree: /Volumes/Volume/crypto-autoresearcher-worktrees/claude-dreg-law
    working_tree: clean            # receipt is a committed snapshot, not working-tree-only
    implementation_commit: ed83b83fc4cf8f6a8ac0237dec8642128062a20b   # ancestor of bedd64c; dirty_tree=true
    tracked_files_in_run: 43

  artifact_checks:
    - id: receipt_committed
      status: PASS
      detail: >-
        43 files under runs/RUN-DREG-001-MEASURE-N12-D6/ are git-tracked at bedd64c
        (clean tree). Not a working-tree-only receipt.
    - id: instrument_hashes
      status: PASS
      detail: >-
        All 6 instrument sha256s in raw-result.json match the snapshot files:
        src/h012c_block_m4ri.py 0eb38126..., DREG_dff.sage f004edeb...,
        DREG_harness.py edf64ad0..., h012_peel_rank.py c46c871b...,
        macaulay_export.py c00b8aad..., ic_first_fall_fast.py f1c98bd8...
    - id: d6_artifact_hashes_vs_manifest
      status: PASS
      detail: >-
        d6-sem-cont-1/stdout.log 553d71cd... , d6-sem result json a47d0ea0... ,
        d6-null/stdout.log 8858077d... , d6-null result json 40d25f92... all match
        the sha256 recorded in the respective manifest.yaml.

  metric_recomputations:
    - cell: {n: 12, t: 3, ti: 0, d: 6, seed: 2026, arm: sem}
      nrows: 183312
      ncols: 174035
      sr_pred: 156520
      rank_full: 138573
      deficit_reported: 17947
      deficit_recomputed: 17947    # 156520 - 138573
      status: PASS
      cross_sources_agree: [raw-result.json, d6-sem-cont-1/manifest.yaml, d6-sem/work/h012c_d6n12_sem_result_n12_t0.json]
    - cell: {n: 12, t: 3, ti: 0, d: 6, seed: 2026, arm: null}
      nrows: 183312
      ncols: 190051
      sr_pred: 156520
      rank_full: 156520
      deficit_reported: 0
      deficit_recomputed: 0        # 156520 - 156520
      status: PASS
      cross_sources_agree: [raw-result.json, d6-null/manifest.yaml, d6-null/work/h012c_d6n12_null_result_n12_t0.json]
    - metric: sem_minus_null_deficit
      reported: 17947
      recomputed: 17947
      status: PASS
    - metric: d_ff_sem_n12_independent_recompute
      status: PASS
      detail: >-
        Validator re-ran DREG_dff.sage (disk-safe TMPDIR/SAGE_TMP) for n=12 sem
        ti0,ti1. Result reproduced EXACTLY: ti0 d_ff=3 (rows=312,cols=1201),
        ti1 d_ff=2 (rows=12,cols=65), nb=24, sr_pred=156520 — matching
        dff-ladder-sem/dff-raw.json. Independently reproduces nb and sr_pred via a
        distinct code path.

  control_checks:
    - id: same_cell_both_arms
      status: PASS
      detail: sem and null share n=12,t=3,ti=0,d=6,seed=2026; nrows=183312; sr_pred=156520.
    - id: null_baseline_rank_eq_srpred
      status: PASS
      detail: >-
        null rank_full=156520 == sr_pred=156520 (deficit 0), D=6 < d_reg(12)=7 so
        the baseline is well-defined. Reproduces the spec anchor "null == sr_pred_D".
    - id: full_column_not_subset_corank
      status: PASS
      detail: >-
        block-m4ri accumulates new pivots over ALL columns; loop terminates only at
        next_col>=ncols; stdout confirms coverage to ncols in both arms; state.json
        unit tables are contiguous 0->ncols with monotone rank_acc and Sum(k)=rank.
        This is full-column exact GF(2) rank, NOT subset-column corank.
    - id: certificate_tier
      status: PASS
      detail: >-
        certificate.kind=none is correct per docs/claims-and-verification.md (pure
        rank measurement; no discrete-log solve or factor-base decomposition).
    - id: ncols_difference
      status: RECORDED_FACT (interpretation deferred to Red Team)
      detail: >-
        ncols differ: sem 174035 vs null 190051. Mechanism (fact, not interpretation):
        boolean_null preserves the per-equation degree profile but randomizes the
        actual monomials, so the expanded Macaulay column support differs; nrows and
        sr_pred depend only on eq_degs and coincide. See CAVEAT-1.

  control_reproducibility_checks:
    - id: environment_seed_dirty
      status: PASS
      detail: >-
        environment.json present (Darwin 24.6.0 arm64, Sage 10.9, M4RI backend);
        seed=2026; dirty_tree=true with dirty_status_sha256=9bbe759f... on D6/null-dff
        receipts; implementation_commit ed83b83 is an ancestor of the snapshot.
    - id: checkpoint_resume_chain
      status: PASS
      detail: >-
        First leg (d6-sem/work/.../state.json) interrupted at next_col=24000,
        rank_acc=24000, 4 carry entries. d6-sem-cont-1 (identical command + same
        results-dir) resumed; its stdout's first processed chunk is cols 24000..36000
        (NOT 0..24000) -> no re-processing, no double-count. rank_acc monotone,
        contiguous coverage to 174035, Sum(unit k)=138573=rank. Instrument enforces
        resume-identity (n/t/ti/d/seed/which/ncols/nrows) and hash-checks carry files.

  infrastructure_classification_checks:
    - cell: dff sem n18 (ti0,ti1,ti2)
      recorded_as: failed_infrastructure (no manifest; INFRA_FAILURE.txt)
      class: resource_exhaustion
      status: PASS
    - cell: dff sem n12 ti2
      recorded_as: censored_timeout (dff-ladder-sem, watchdog 900s)
      class: resource_exhaustion
      status: PASS
    - cell: dff sem n15 ti0
      recorded_as: censored (per-target cap 30s, graceful)
      class: resource_exhaustion
      status: PASS
    - cell: dff null n12 (all)
      recorded_as: censored_timeout (dff-null-n12 + dff-null-n12-b, no cell)
      class: resource_exhaustion
      status: PASS
    - cell: dff null n15, n18
      recorded_as: not attempted (established host-unsafe), infra-limited
      class: resource_exhaustion
      status: PASS
    note: >-
      Every infra cell carries valid:null and invalid_reason citing AGENTS rule 5;
      none is treated as mathematical evidence.

  verdict: passed_with_caveats   # terminal: receipts are ADMISSIBLE evidence, with binding caveats below

  binding_caveats:
    - id: CAVEAT-1
      owner: red-team / coordinator
      blocking_for: interpretation of the sem-vs-null deficit
      detail: >-
        The frozen spec (specification.yaml) describes the null as "identical
        monomial support / degree profile". The measured null support is NOT
        identical (ncols 190051 vs sem 174035); only the generator degree profile is
        matched. Whether "support-matched" is intended at the generator level
        (satisfied) or the Macaulay column level (not satisfied) must be adjudicated
        before sem deficit=17947 vs null deficit=0 is read as a structural signal.
        Each individual rank remains a valid full-column measurement regardless.
    - id: CAVEAT-2
      owner: coordinator
      blocking_for: any "independently reproduced via a distinct engine" claim
      detail: >-
        The dispatch VAL objective asks to reproduce every rank via a distinct
        engine. Under the bounded, disk-safe budget a from-scratch second-engine D6
        rank was explicitly out of scope. The D6 ranks are validated as
        internally-consistent (carry/rank accounting, stdout, full coverage),
        hash-pinned, and resume-verified, and sr_pred + d_ff were independently
        reproduced — but the D6 rank itself is NOT cross-engine confirmed. A distinct-
        engine D6 rank confirmation remains an OPEN validation item.
    - id: CAVEAT-3
      owner: coordinator
      blocking_for: none (provenance limitation)
      detail: >-
        dirty_status_sha256 hashes `git status` output, not a diff, so the exact
        working-tree delta at ed83b83 is not reconstructible. Mitigated: all
        instrument files are content-hash-pinned and match the snapshot.
    - id: CAVEAT-4
      owner: coordinator
      blocking_for: the ledger commit's post-commit scope check
      detail: >-
        The dispatch_queue declares the validator write_scope as
        reviews/VAL-N12D6.md, but this report was written to
        reviews/validator-report.md per the explicit task instruction. Reconcile
        (rename or update the declared write_scope) before the LEDGER-C2 commit, or
        the scope verifier will reject.

  limitations:
    - Single cell only: n=12, t=3, ti=0, seed=2026, probe degree D=6. D=6 < d_reg(12)=7,
      so this is a sub-d_reg fixed-degree deficit, NOT a measurement of d_reg itself.
    - Single target, single seed: NO >=3-seed / >=8-R replication. The spec success
      criteria (d_reg(sem)<d_reg(null) with CI separation; super-linear deficit growth;
      bounded gap) are NOT evaluable from this cell; no CIs exist.
    - d_ff resolved only for sem n12 {ti0:3, ti1:2} (independently confirmed) and sem
      n15 {ti1:2, ti2:2} (receipt-only). The rest of the gap ladder is infra-censored.
    - No independent second-engine confirmation of the D6 full-column rank (see CAVEAT-2).

  scope_supported:
    tier: toy   # boolean Macaulay system, n=12, nb=24; certificate.kind=none
    n: [12]
    arms: [sem, null]
    what_it_supports: >-
      For the single tested cell (n=12, t=3, ti=0, seed=2026, D=6 < d_reg=7), the
      boolean chained Semaev m=3 sem system has full-column exact GF(2) rank 138573
      (17947 below the semiregular prediction 156520); the degree-profile-matched
      T11 randomized null attains the semiregular prediction exactly (156520,
      deficit 0). Reproducibility bindings are intact; d_ff for the reachable sem
      cells was independently reproduced.
    what_it_does_NOT_support: >-
      No ECDLP solve/relation (certificate.kind=none), no speedup, no d_reg claim,
      no CI-backed sem-vs-null separation, no cross-scale/crypto claim, and no
      authorization to change hypothesis status or promote. A passed validation
      means only that these rank/first-fall observations are admissible evidence.

  artifact_paths:
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/raw-result.json
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/d6-sem-cont-1/manifest.yaml
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/d6-sem/work/h012c_d6n12_sem_result_n12_t0.json
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/d6-sem/work/h012c_d6n12_sem_n12_t0/state.json
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/d6-null/manifest.yaml
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/d6-null/work/h012c_d6n12_null_result_n12_t0.json
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/d6-null/work/h012c_d6n12_null_n12_t0/state.json
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/dff-ladder-sem/dff-raw.json
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/dff-sem-n15/dff-raw.json
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/dff-sem-n18/INFRA_FAILURE.txt
    - src/h012c_block_m4ri.py
    - src/h012_peel_rank.py
    - docs/claims-and-verification.md
```

## Overall verdict: PASS-WITH-CAVEATS

The run **RUN-DREG-001-MEASURE-N12-D6** is an **admissible research receipt**: every
artifact-integrity, metric, control, and reproducibility check passes. Four binding
caveats (above) must be handled by the Red Team / Coordinator before the evidence is
interpreted or a decision is minted. None of the caveats is an artifact-integrity
failure — the rank measurements themselves are valid, reproducible, and honestly
recorded.

## Per-check results

| # | Check | Result |
|---|-------|--------|
| 1 | Metric consistency (raw-result.json vs manifests vs result JSONs; deficit recompute) | **PASS** |
| 2 | Admissibility (full-column exact rank, not subset corank; certificate tier) | **PASS** |
| 3 | Calibration / controls (same cell; null rank==sr_pred; ncols difference recorded) | **PASS** (ncols diff = recorded fact for Red Team) |
| 4 | Reproducibility (env, hashes, seed, dirty state, checkpoint-resume chain) | **PASS** (with CAVEAT-2, CAVEAT-3) |
| 5 | Infra classification (all censored/failed cells = failed_infrastructure, not evidence) | **PASS** |

### Check 1 — Metric consistency: PASS
`raw-result.json`, `d6-sem-cont-1/manifest.yaml`, and `d6-sem/work/...sem_result...json`
agree exactly (nrows 183312, ncols 174035, sr_pred 156520, rank 138573, deficit 17947);
`d6-null/manifest.yaml` and `d6-null/work/...null_result...json` agree exactly (ncols
190051, rank 156520, deficit 0). Independently recomputed deficits: sem 156520−138573 =
**17947**; null 156520−156520 = **0**; sem−null = **17947**. First-fall values in
`raw-result.json` match `dff-ladder-sem/dff-raw.json` (sem n12 ti0=3, ti1=2) and
`dff-sem-n15/dff-raw.json` (sem n15 ti0 censored, ti1=2, ti2=2).

### Check 2 — Admissibility: PASS
`src/h012c_block_m4ri.py` (hash-verified) computes an exact full-column GF(2) rank as the
sum of new pivots across contiguous column sub-chunks, carrying a hash-checked staircase
basis; the loop runs `while next_col < ncols` and sets `done` only at full coverage. Both
arms' stdout end with full-coverage `DONE` lines (`cols 168000..174035 ... deficit=17947`;
`cols 180000..190051 ... deficit=0`), and both `state.json` unit tables are contiguous
0→ncols with monotone `rank_acc` and Σk = rank. This is **not** a subset-column corank.
`certificate.kind=none` is the correct tier per `docs/claims-and-verification.md` (pure
measurement; nothing to certify).

### Check 3 — Calibration / controls: PASS
Both arms share n=12, t=3, ti=0, d=6, seed=2026, nrows=183312 and sr_pred=156520. The null
hitting `rank == sr_pred` exactly (deficit 0) at D=6 < d_reg(12)=7 is the well-defined
baseline and reproduces the spec anchor. The `ncols` difference (sem 174035, null 190051)
is **recorded as a fact**; its meaning is left to the Red Team (see CAVEAT-1). Mechanism
(fact only): `boolean_null` matches the per-equation degree profile but randomizes the
monomials, so the expanded Macaulay column support differs while nrows/sr_pred (which
depend only on `eq_degs`) coincide.

### Check 4 — Reproducibility: PASS (with limitations)
Environment, seed=2026, and dirty-tree state recorded; all 6 instrument hashes match; the
4 D6 artifact hashes match their manifests. The **checkpoint-RESUME chain is clean**: the
continuation's first processed chunk is `cols 24000..36000`, exactly the first-leg
boundary (`next_col=24000`), so no columns were re-processed (no double-count) or dropped
(contiguous to ncols; Σk = 138573 = rank). The instrument enforces resume-identity and
verifies carry-file hashes on load. An **independent** DREG_dff recompute reproduced the
n=12 sem d_ff (ti0=3, ti1=2) and sr_pred=156520 exactly. Limitations: no second-engine D6
rank confirmation (CAVEAT-2); dirty delta not fully reconstructible (CAVEAT-3).

### Check 5 — Infra classification: PASS
Every infra-limited cell (dff sem n18; dff sem n12 ti2; dff sem n15 ti0; dff null n12
attempts; dff null n15/n18) is recorded as `failed_infrastructure`/`censored` with class
`resource_exhaustion`, `valid: null`, and an `invalid_reason` citing AGENTS rule 5. None is
treated as mathematical evidence. `dff-sem-n18` correctly has no manifest (the harness
blocked in D-state before writing) and only an `INFRA_FAILURE.txt`.

## Binding items the Coordinator must resolve before the decision
1. **CAVEAT-1 (Red Team):** null "support-matched" semantics vs the ncols mismatch — must
   be adjudicated before the deficit is read as a sem-vs-null structural signal.
2. **CAVEAT-2:** the D6 rank is internally-consistent + hash-pinned + resume-verified but
   NOT confirmed by a distinct engine; do not assert "independently reproduced" for the
   rank.
3. **CAVEAT-4:** write_scope path discrepancy (VAL-N12D6.md declared vs validator-report.md
   written) — reconcile before the ledger commit.

## Exact scope the evidence can support
- **One cell** for the D6 full-column exact rank: n=12, t=3, ti=0, seed=2026, D=6 (a
  sub-d_reg fixed-degree deficit, since D=6 < d_reg(12)=7 — NOT d_reg itself), both arms.
- **Single target, single seed** — no CIs; the spec's d_reg/deficit-growth/gap success
  criteria are not evaluable here.
- **d_ff:** sem n12 {ti0:3, ti1:2} (independently confirmed) and sem n15 {ti1:2, ti2:2}
  (receipt-only); the rest of the ladder is infra-censored.
- **Claim tier: toy** structural measurement; `certificate.kind=none`. This PASS admits the
  rank/first-fall observations as evidence; it does **not** support any ECDLP claim, does
  **not** demonstrate a speedup, and does **not** authorize promotion or a status change.
