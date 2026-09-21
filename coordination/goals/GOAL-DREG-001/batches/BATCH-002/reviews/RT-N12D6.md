# Red-Team Report — GOAL-DREG-001 BATCH-002 / RUN-DREG-001-MEASURE-N12-D6

Independent falsification of the interpretation of the frozen snapshot. This report
does NOT change hypothesis/experiment status, does NOT edit raw artifacts, and does
NOT commit into the shared worktree. It resolves the Validator's open CAVEAT-1
(the "support-matched vs ncols" adjudication explicitly deferred to Red Team).

```yaml
red_team_report:
  id: RT-20260721-001
  task_id: TASK-20260721-DREG-N12D6-RT-R1
  claim_under_review: >-
    "The boolean Semaev m=3 system departs non-generically from the semi-regular
    null at the degree axis: at n=12, t=3, D=6 the full-column exact GF(2) rank
    deficit is 17947 (sem) vs 0 (T11 support-matched null)."
  snapshot:
    commit: bedd64c26343f4d8ad3b9919c4eb3c0103b21e43
    branch: claude/dreg-linear-law
    worktree: /Volumes/Volume/crypto-autoresearcher-worktrees/claude-dreg-law
    run: experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/
    reviewed_as: committed_snapshot   # not working-tree-only

  verdict: >-
    CONFOUNDED-BUT-NOT-EMPTY. The "17947 vs 0" magnitude is NOT an apples-to-apples
    structural signal: ~89% of it (16016 of 17947) is a column-support gap that lies
    ENTIRELY at the probe degree D=6, while the phrase "support-matched" is factually
    false for this null over GF(2). A pure-arithmetic support correction leaves a
    genuine, support-INDEPENDENT deficit of >=1931 at this one cell — so the finding
    is not killed — but that residual points toward d_reg(sem) >= d_reg(null) (a LARGER
    sem quotient / later collapse), which is the WRONG sign for H-DREG-001's cheaper-solve
    WIN and matches the standing negative-control reading. The datum supports at most a
    SCOPED >=1931 non-generic departure at n=12/D6; it does NOT support the 17947 headline,
    a smaller operative d_reg, deficit growth, or any sub-rho signal.

  objections:
    - id: OBJ-1-ncols-confound   # PRIMARY
      severity: high
      target: apples-to-apples of "deficit 17947 vs 0" against the shared sr_pred
      finding: >-
        sr_pred=156520 is computed by semireg_rank_pred(eq_degs, nb, D) from ONLY the
        generator degree multiset ({2:12, 3:12}) and nb=24 — it does not depend on
        either arm's monomial support, so the SAME full-support prediction is applied to
        two DIFFERENT column spaces. The null has ncols=190051 = the FULL squarefree
        monomial space of degree<=6 in nb=24 vars (independently recomputed:
        sum_{d<=6} C(24,d)=190051), so it realises sr_pred exactly (rank 156520,
        deficit 0). The sem lives in a subspace: ncols=174035, i.e. 16016 monomials are
        ABSENT from sem's column support. The deficit sr_pred-rank_sem=17947 therefore
        conflates two effects: (E1) support reduction — 16016 monomials sem never
        reaches, which a full-support semi-regular prediction "expects" to be pivotable;
        (E2) genuine extra row-syzygies. Attributing all 17947 to E2 (non-generic
        degeneracy) is the error.
      quantification: >-
        Column-deletion bound: rank(null restricted to sem's 174035 columns)
        >= rank_null - 16016 = 156520 - 16016 = 140504. sem rank = 138573 < 140504.
        Hence support-INDEPENDENT deficit >= 140504 - 138573 = 1931, and at most
        16016 of the 17947 (=89.2%) is attributable to the support gap. Genuine
        (E2) fraction is >=1931 (>=10.8%); exact value unpinned in [1931, 17947].
    - id: OBJ-2-support-matched-is-a-misnomer
      severity: high
      target: raw-result.json null_type "T11 support-matched semiregular (identical
        degree profile; coefficients randomized)" and H-DREG-001 assumption "identical
        monomial support ... only coefficients randomized"
      finding: >-
        Over GF(2) a boolean polynomial IS a set of monomials (every coefficient is 1);
        there is nothing to "randomize" except WHICH monomials appear. boolean_null draws
        random monomials (rng.sample) with the same per-degree COUNT per equation, so it
        matches the degree multiset but necessarily CHANGES the support. The ncols mismatch
        (174035 vs 190051) is proof the null is NOT support-matched at the Macaulay-column
        level. A strictly support-matched null over GF(2) with only "coefficients
        randomized" is impossible unless it equals sem itself. The label should read
        "degree-multiset-matched random null," and the H-DREG-001 assumption "identical
        monomial support" is false as implemented.
    - id: OBJ-3-gap-is-entirely-at-the-probe-degree
      severity: high
      target: why the confound is maximally damaging at D=6 specifically
      finding: >-
        Independent support reconstruction shows sem and null have IDENTICAL support at
        every degree 0..5 (1,24,276,2024,10626,42504) and differ ONLY at degree 6
        (sem 118580 vs null 134596 = full C(24,6)). All 16016 missing monomials are
        degree 6 — exactly the probe degree whose rank the deficit is measured at. So the
        support gap injects directly into the D=6 comparison. Corollary: the D=5 rank
        comparison is FULLY support-matched (shared 55455-column support), and that cell
        is ALREADY committed: sem D5 rank=28096 vs null/sr_pred[5]=29418 => clean
        support-matched deficit 1322 (RUN-DREG-001-VALIDATE-N12-A; VALIDATE-NULL-N12-D5-B).
        1322 (D5, clean) and >=1931 (D6, support-corrected) are mutually consistent and
        BOTH small — the honest degree-axis signal is O(10^3), not O(1.8x10^4).
    - id: OBJ-4-subdreg-deficit-does-not-lower-operative-degree
      severity: high
      target: the tempting reading that a D6 (< d_reg=7) deficit implies a cheaper solve
      finding: >-
        A rank deficit at D=6 means sem's degree-<=6 quotient (ncols-rank) is LARGER than
        semi-regular, i.e. sem is FURTHER from the s=1 solution collapse => higher, not
        lower, operative solving degree (d_reg(sem) >= d_reg(null)=7). This reproduces
        FINDING_v2 Part D/E ("extra cascade syzygies RAISE the solving degree — the wrong
        direction for an attacker"). A single sub-d_reg deficit does NOT establish: (i) the
        operative d_reg(sem); (ii) d_reg(sem) < d_reg(null); (iii) super-linear deficit
        GROWTH in n (needs a series across n, not one point); (iv) any reduction in
        Groebner/last-fall cost; (v) sub-exponential per-PDP cost. It establishes only a
        single-cell sub-d_reg quotient excess of (support-corrected) >=1931.
    - id: OBJ-5-d_ff-is-non-operative-and-collapses-the-gap-reading
      severity: high
      target: the executor-flagged low first-fall (d_ff=2-3 << d_reg=7) and gap(n)
      finding: >-
        d_ff resolved to 2-3 with ff_s=0.0 on the resolved sem cells. d_ff=2 at ff_s=0
        is the trivial degree-2 boolean fall (field relations x_i^2=x_i / trivial
        quadratic combinations), NOT the operative solving degree — exactly the
        Petit-Quisquater first-fall signature FINDING_v2 Part E already showed carries only
        O(1)-O(n) usable relations, far too few to solve; operative degree ~ d_reg. If d_ff
        is non-operative, gap(n)=d_reg-d_ff is spuriously LARGE and grows only because
        d_reg grows (~0.24n) — an artifact, not a narrowing advantage. This HURTS the
        deficit story. Worse, H-DREG-001's gap clause requires comparison to the NULL gap
        with non-overlapping bootstrap CIs over >=8 R per n; the null d_ff was NEVER
        measured (every null first-fall cell OOM/censored), and for a semi-regular null
        d_ff=d_reg so gap_null~0. The gap prediction is therefore untestable AND its sem
        arm rests on a trivial fall.
    - id: OBJ-6-underpowered-vs-stated-test-boundary
      severity: medium
      target: sufficiency of one cell for H-DREG-001's degree-axis clauses
      finding: >-
        H-DREG-001 predicts deficit growth super-linear in n across n in {17,18,21,24}
        (CI excludes 1) OR d_reg(sem)<d_reg(null), and gap bounded/slower with
        non-overlapping bootstrap CIs over >=8 R per n, both arms. Delivered: 1 seed,
        1 target, 1 degree, 1 n; d_ff inconsistent even across the 2 resolved sem seeds
        at n=12 (ti0=3, ti1=2); null gap entirely absent. No CI, no growth series, no
        cross-arm gap. None of the degree-axis success criteria is evaluable.

  required_controls:
    - id: CTRL-A-ran
      status: RAN
      what: >-
        Independent support/monomial-set audit (rt-control/support_confound_probe.py).
        Rebuilt the EXACT sem and null systems from the committed seed (t=3, n=12, ti=0,
        seed=2026) and verified their system hashes against the receipts; recomputed
        ncols, sr_pred, the support subset relation, and the degree histogram of the gap.
      result: >-
        sem_hash c47d17c... and null_hash f2f6107... reproduce the receipts EXACTLY
        (systems are bit-identical to the producer's). ncols verified: sem 174035, null
        190051; null_is_full_support = true (190051 = sum_{d<=6} C(24,d)). sr_pred
        recomputed = 156520 (matches). sem support SUBSET of null (0 sem-only monomials);
        gap = 16016, ALL at degree 6 (degrees 0..5 identical). Support-independent deficit
        lower bound = 1931. Runtime 12.8s, peak RSS 3.6 GB, disk-safe on
        /Volumes/Volume/sage-scratch-dreg. NOTE: this control does NOT recompute the D6
        rank; it audits supports only. The Validator's CAVEAT-2 (no distinct-engine D6
        rank confirmation) still stands and I inherit it.
      artifacts:
        - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/rt-control/support_confound_probe.py
        - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/rt-control/support_confound_probe.json
    - id: CTRL-B-specified
      status: SPECIFIED (for BATCH-003; not run here)
      what: >-
        Pin the exact support-corrected D6 deficit in [1931, 17947]. Cheapest exact
        route: compute the full-column exact GF(2) rank of the NULL Macaulay matrix
        RESTRICTED to sem's 174035-column support (delete the 16016 degree-6 columns not
        in sem support), via the chunked src/h012c_block_m4ri.py. Reuses the existing null
        adjacency pickle (d6-null/work/h012c_adj_null_...pkl) plus the two colidx maps
        rebuilt in CTRL-A to select the 16016 columns. Report deficit_genuine =
        rank(null|_sem-support) - 138573. Budget ~2100s (< the 2284s full-null run),
        peak RSS ~7 GB, TMPDIR=SAGE_TMP=/Volumes/Volume/sage-scratch-dreg, write under a
        new rt-control-b/ subdir. Equivalent alternative: a THIRD arm = random boolean
        system whose monomials are drawn ONLY from sem's monomial universe with the same
        per-equation degree histogram (a genuinely support-matched null). Not run here
        because it needs a new column-restriction code path + ~35 min on a host with
        documented swap-to-root OOM incidents, exceeding the safe red-team budget and
        risking a wrong number; the arithmetic bound already answers the yes/no.
    - id: CTRL-C-zero-compute
      status: AVAILABLE-NOW
      what: >-
        Use the ALREADY-committed D=5 cell as the fully support-matched degree-axis
        observable (shared 55455 columns; no confound): sem 28096 vs sr_pred 29418 =>
        deficit 1322. Combined with the >=1931 D6 support-corrected bound this gives the
        honest degree-axis signal with zero new compute.

  counterexample_or_mutation: >-
    Counterexample to "deficit 17947 = non-generic degeneracy": construct any structured
    boolean system that simply omits 16016 top-degree monomials from its generator reach
    but is otherwise rank-generic on the monomials it does reach; embedded in the full
    190051-space it exhibits deficit ~16016 against the full-support sr_pred with ZERO
    extra syzygies. The measured sem sits only 1931 below even the worst case of that
    mutation, so 89% of the reported deficit survives a null with no extra syzygies at all.

  baseline_comparison: >-
    certificate.kind=none: this is a pure rank measurement with NO end-to-end cost path,
    so no direct Pollard-rho / BSGS comparison is instantiated (correctly). The closest
    specialized baseline is the semi-regular-d_reg Groebner/last-fall cost model of
    FINDING_v2 Part C: at the crypto config (t=7, n=161) semi-regular d_reg=150 gives
    2^1194 (omega=2) vs Pollard-rho 2^80.5 on E(GF(2^161)) — Groebner loses by >1100
    bits. The direction of THIS datum (larger sem quotient => d_reg(sem) >= d_reg(null))
    makes the structured Groebner solve MORE expensive than the semi-regular baseline,
    i.e. FURTHER from rho/BSGS, not closer. There is no sub-rho signal; the honest reading
    moves the wrong way for an attack, consistent with the boolean Weil-descent route being
    a negative control.

  narrowest_supported_statement: >-
    For the single committed cell (n=12, t=3, ti=0, seed=2026), the boolean chained Semaev
    m=3 degree-<=6 Macaulay matrix has full-column exact GF(2) rank 138573, which is
    >=1931 below the rank any semi-regular system attains on sem's identical 174035-column
    support — a support-INDEPENDENT non-generic rank deficit. The reported 17947
    deficit-vs-sr_pred is NOT this quantity: >=16016 of it is a degree-6-only column-support
    gap (sem reaches 118580 of 134596 degree-6 monomials; the "support-matched" null reaches
    all 134596), so at most 10.8% is genuine extra-syzygy structure. The fully
    support-matched D=5 deficit (identical supports) is 1322. The deficit's direction
    (larger sem quotient) is consistent with d_reg(sem) >= d_reg(null)=7. No d_reg,
    deficit-growth, gap, CI-backed separation, speedup, or sub-rho claim is supported;
    claim tier: toy; certificate.kind=none.

  next_concrete_action: >-
    Adopt the support-corrected framing NOW at zero compute (report the n=12 D6 result as
    "genuine support-independent deficit >=1931; headline 17947 is ~89% degree-6 support
    gap", and treat the already-committed, fully support-matched D5 deficit series
    1322/1862/1999 — which is DECELERATING — as the admissible degree-axis observable),
    and queue CTRL-B (restricted-column null D6 rank) for BATCH-003 to pin the exact
    genuine deficit in [1931, 17947]. Do NOT let the raw 17947 enter any EV/decision record
    as a structural signal without this correction.

  scope_limits:
    - Single cell (n=12, t=3, ti=0, seed=2026, D=6); toy scale; no CIs; not d_reg itself.
    - A bounded audit, not a cross-engine D6 rank recompute (Validator CAVEAT-2 inherited).
    - This is a SCOPED objection to one interpretation, NOT an impossibility result and NOT
      a status change; H-DREG-001 remains inconclusive pending the Coordinator.

  artifact_paths:
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/raw-result.json
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/d6-sem-cont-1/manifest.yaml
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/d6-null/manifest.yaml
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/rt-control/support_confound_probe.py
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/rt-control/support_confound_probe.json
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-VALIDATE-N12-A/manifest.yaml
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-VALIDATE-NULL-N12-D5-B/manifest.yaml
    - src/h012_peel_rank.py
    - src/h012c_block_m4ri.py
    - coordination/goals/GOAL-DREG-001/batches/BATCH-002/reviews/VAL-N12D6.md
    - ledger/H-DREG-001.yaml

  binding_caveats_for_coordinator:
    - id: RT-CAV-1
      blocking_for: any EV/DEC record that cites the deficit as a structural signal
      detail: >-
        Resolves Validator CAVEAT-1: the null is degree-multiset-matched, NOT
        support-matched (impossible over GF(2)); the sem-vs-null "17947 vs 0" is
        cross-support. The admissible structural number is the support-corrected
        deficit >=1931 (D6) or the clean D5 deficit 1322 — never 17947.
    - id: RT-CAV-2
      blocking_for: the archival/ledger commit's post-commit scope check
      detail: >-
        The dispatch_queue declares the red-team write_scope as
        reviews/RT-N12D6.md (this file); the task prompt named reviews/redteam-report.md.
        This report is at the DECLARED-scope path RT-N12D6.md (parallel to VAL-N12D6.md).
        ALSO: the rt-control/ artifacts are under experiments/.../RUN-DREG-001-MEASURE-N12-D6/,
        which is NOT in the declared red-team write_scope. The archival task must add the
        rt-control/ paths to its declared artifacts (or the run dir to the red-team scope)
        before staging, or the scope verifier will reject. Same class of issue as the
        Validator's CAVEAT-4.
```

## Load-bearing numbers (all independently reproduced in CTRL-A)

| quantity | sem | null (T11) | source |
|---|---|---|---|
| nrows | 183312 | 183312 | receipt + CTRL-A |
| ncols (Macaulay column support) | 174035 | 190051 = **full** C(24,≤6) | CTRL-A verified |
| sr_pred (from eq_degs {2:12,3:12}, nb=24) | 156520 | 156520 (**same by construction**) | CTRL-A verified |
| rank_full (D6) | 138573 | 156520 | receipt (not re-run) |
| deficit vs sr_pred | 17947 | 0 | receipt |
| support gap vs the other arm | −16016 (**all deg 6**) | +16016 | CTRL-A |
| **support-independent deficit (D6)** | **≥1931** | — | 156520−16016−138573 |
| clean support-matched deficit (**D5**) | **1322** | 0 | VALIDATE-N12-A / NULL-N12-D5-B |

Degree histogram of sem vs null support (CTRL-A): identical at d=0..5
(1,24,276,2024,10626,42504); at d=6 sem 118580 vs null 134596 — the entire 16016-monomial
gap is degree 6, i.e. at the probe degree. Semi-regular quotient HF = [1,24,264,1724,7104,16920,7494,0]
(d_reg=7, since HF[7]=0), so D=6 is one degree below collapse.

## One-paragraph verdict

The producer's rank measurements are sound and reproducible (I independently rebuilt both
systems from seed and matched their hashes bit-for-bit), but the *interpretation* "17947 vs 0
= non-generic degree-axis departure" does not survive. The two arms are compared to a single
full-support semi-regular prediction while living in column spaces that differ by 16016
monomials, all at the probe degree D=6; the "support-matched" label is a misnomer over GF(2).
A support correction that is free from the committed numbers leaves a genuine deficit of only
≥1931 (≤11% of the headline), and that residual has the wrong sign for the hypothesis — it
says the Semaev quotient is *larger* (d_reg(sem) ≥ d_reg(null)), reinforcing the negative
control rather than opening a cheaper solve. The narrowest honest claim is a scoped ≥1931
non-generic deficit at one toy cell; the exact genuine value in [1931, 17947] should be
pinned by the restricted-column null rank (CTRL-B) before any structural reading is minted.
