# Red-Team Report — GOAL-DREG-001 BATCH-003 / RUN-DREG-001-CTRLB-N12-D6

Independent falsification of the **interpretation** of the CTRL-B result on the frozen
snapshot. This report changes no hypothesis or experiment status, edits no raw artifact,
commits nothing, and owns no run directory. Integrity of the receipt (hashes, column sets,
coverage, bracket) belongs to the Validator; where I doubt a number I refer it rather than
adjudicate it.

```yaml
red_team_report:
  id: RT-20260726-001
  task_id: TASK-20260726-DREG-CTRLB-RT
  goal_id: GOAL-DREG-001
  batch_id: BATCH-003
  role: red-team
  claim_under_review: >-
    "rank(null restricted to sem's 174035-column support) = 156520 = the unrestricted null
    rank, therefore deficit_genuine = 156520 - 138573 = 17947 is entirely genuine and
    support-independent; the BATCH-002 quarantine ('>= ~89% of 17947 is a degree-6 support
    gap, not syzygies') is refuted by the very control it specified."
  snapshot:
    commit: 8302c83af438e679c7a7085f7de25b79d92b2a9f
    branch: claude/dreg-linear-law
    worktree: /Volumes/Volume/crypto-autoresearcher-worktrees/claude-dreg-law
    run: experiments/EXP-DREG-001/runs/RUN-DREG-001-CTRLB-N12-D6/
    reviewed_as: committed_snapshot     # 9 tracked files at HEAD; `git status --porcelain` clean
    parent: ba28a9496c2fc1063bce032459fd4bd0bc10934e   # queue+handoff commit; carries the pre-registered bracket
    predecessor_reviewed: coordination/goals/GOAL-DREG-001/batches/BATCH-002/reviews/RT-N12D6.md

  verdict: >-
    QUARANTINE-LIFTS, NEGATIVE-STRENGTHENS. The stated ground of the BATCH-002 quarantine is
    refuted: on the identical 174035-column space the null attains 156520 and sem attains
    138573, so ZERO of the 17947 is attributable to sem's 16016 missing degree-6 columns, and
    the committed sentence ">= ~89% of 17947 is a degree-6 support gap, not syzygies"
    (ledger/goals/GOAL-DREG-001.yaml checkpoint BATCH-002; commit 6a141ed4) is now false.
    The number should be released from quarantine AS A MEASUREMENT and simultaneously re-barred
    from any attack reading by a stronger caveat, because its SIGN is unchanged and its
    magnitude makes the negative reading STRONGER, not weaker: sem's degree-<=6 quotient on its
    own support is 35462 versus the semi-regular 17515 on the same space (2.02x), i.e. the
    Semaev ideal is SMALLER, its collapse is LATER, and Groebner moves FURTHER from
    Pollard-rho. Separately, the interpretive framework BATCH-002 fell back on does not
    survive this batch: the "fully support-matched D5 series" is not support-matched
    (sem D5 ncols 46717 vs null 55455, gap 8738 -- independently recomputed below), so the
    fallback observable is, by BATCH-002's own standard, MORE confounded than the datum it
    quarantined. A bigger number is not a bigger claim: this remains one toy cell, at a fixed
    degree below d_reg, with certificate.kind=none, one seed and one target.

  # ---------------------------------------------------------------- objections
  objections:
    - id: OBJ-1-bound-reported-as-estimate      # PRIMARY, and it is now a falsified ledger sentence
      severity: high
      target: >-
        RT-N12D6 verdict + narrowest_supported_statement; DEC-GOAL-DREG-001-B002 rationale;
        ledger/goals/GOAL-DREG-001.yaml BATCH-002 checkpoint; commit message 6a141ed4.
      finding: >-
        The column-deletion inequality rank(M restricted) >= rank(M) - |S| is a WORST-CASE
        bound. RT-N12D6's own OBJ-1 quantification block stated it correctly ("at most 16016
        of the 17947 (=89.2%) is attributable to the support gap. Genuine (E2) fraction is
        >=1931 (>=10.8%)"), but the report's verdict and narrowest_supported_statement
        inverted the quantifiers -- "~89% of it (16016 of 17947) is a column-support gap",
        ">=16016 of it is a degree-6-only column-support gap", "at most 10.8% is genuine
        extra-syzygy structure" -- and the ledger inherited the inverted form. The error class
        is: A WORST-CASE BOUND COLLAPSED TO A POINT ESTIMATE AT ITS UNFAVOURABLE ENDPOINT.
        CTRL-B measured the other endpoint. Measured attribution: support gap 0 of 17947
        (0.0%), genuine 17947 of 17947 (100%).
      what_it_falsifies: >-
        (i) ">= ~89% of 17947 is a degree-6 support gap"; (ii) "The genuine signal is O(10^3),
        not the O(1.8x10^4) headline"; (iii) RT-N12D6 OBJ-3's "1322 (D5) and >=1931 (D6) are
        mutually consistent and BOTH small". At the same n=12 the two degrees differ by 13.6x
        (1322 vs 17947) and by 10.5x in relative terms (5.08% vs 53.52% of the semi-regular
        quotient).
      remedy: >-
        A SUPERSEDING correction record (AGENTS rule 4 -- never overwrite). The bound itself
        was sound and is still true; only its rhetorical collapse was wrong.

    - id: OBJ-2-the-fallback-observable-inherits-the-same-defect
      severity: high
      target: >-
        RT-N12D6 OBJ-3 ("the D=5 rank comparison is FULLY support-matched (shared
        55455-column support)"), CTRL-C-zero-compute, and the BATCH-002 next_action that made
        the D5 series 909/1322/1862/1999 "the admissible degree-axis observable".
      finding: >-
        FALSE as stated, per the committed receipts and my own recomputation. The identical
        degree-0..5 histogram RT-N12D6 cited is the histogram of the D=6 Macaulay matrices;
        the D=5 matrices are a different pair. RUN-DREG-001-VALIDATE-N12-A: sem D5 ncols =
        46717. RUN-DREG-001-VALIDATE-NULL-N12-D5-B: null D5 ncols = 55455. Gap 8738, and it
        is NOT confined to the probe degree (histogram {5: 8736, 4: 2}). The D5 comparison is
        therefore cross-support exactly like D6, and the deficit 1322 was likewise computed
        against the support-independent sr_pred = 29418.
      quantification: >-
        Applying the predecessor's own bound at D5: rank(null|sem-D5-support) >= 29418 - 8738
        = 20680, so deficit_genuine(D5) lies only in [-7416, +1322] -- the bound cannot even
        establish that the D5 deficit is POSITIVE. By BATCH-002's own standard the fallback
        observable is more confounded than the datum it quarantined. The same support gap at
        larger n: n=15 sem D5 ncols 143421 vs full 174437 (gap 31016, 17.8%); n=18 sem 358678
        vs full 443704 (gap 85026, 19.2%) -- the gap grows with n, so the whole D5 series
        carries an unmeasured correction, in the same direction, that grows along the series.
      consequence: >-
        No committed measurement currently establishes that ANY sem deficit at D=5 is
        support-independent. This is repairable for ~1/40 of the CTRL-B cost and is the basis
        of my next_concrete_action.

    - id: OBJ-3-endpoint-landing-is-a-prediction-not-a-coincidence
      severity: medium-high
      target: >-
        the evidential weight of the in_preregistered_bracket flag and of the exact
        endpoint hit
      finding: >-
        The bracket [140504, 156520] is a THEOREM (deletion cannot raise rank; it cannot lower
        it by more than |S|), not a statistical prediction interval, so "inside the bracket"
        is near-vacuous as a check and only its violation would have carried information
        (correctly recorded as integrity_failure in the P1 handoff). Moreover the UPPER
        endpoint was the a priori expected outcome. Exact argument: rank(M|kept) = dim R -
        dim(R \cap F^S) where R = rowspace(M_null) (dim 156520) and F^S is the coordinate
        subspace on the 16016 deleted columns; rank is preserved iff R contains no nonzero
        vector supported entirely inside S. For a subspace in general position,
        dim(R \cap F^S) = max(0, 156520 + 16016 - 190051) = 0 with slack 17515; the crude
        counting bound for a uniformly random R gives P(R \cap F^S != 0) <~ 2^-17515. Graded
        refinement (the honest version, since R is NOT uniformly random): the intersection can
        only live in R \cap F^{deg 6}, whose dimension is at least 156520 - 55455 = 101065,
        and general position inside the degree-6 block requires only that this dimension not
        exceed 134596 - 16016 = 118580 -- which is exactly sem's degree-6 support size. The
        observed outcome sits comfortably inside that window. So the null behaving generically
        under column deletion is the DEFAULT expectation for the arm whose entire purpose is
        to be generic, and the endpoint landing is corroboration, not anomaly.
      bug_that_would_produce_the_same_number: >-
        The dangerous class is "the restriction was a no-op" (the driver ranked the full
        190051-column matrix, or built the kept-index map as the identity). Discriminators
        already present in the committed receipt and NOT explainable by that bug:
        (a) column-audit.json restricted nnz = 5468179 versus full nnz = 5768183, i.e. 300004
        nonzeros were genuinely removed (mean 18.7 per deleted column) -- the deleted columns
        were far from empty, so rank preservation is a real linear-algebra fact and not a
        triviality; (b) chunk coverage totals 174035 over 15 units, not 190051;
        (c) the pivot-break profile differs from the full-null run (independence breaks inside
        chunk [151232, 162636) here; the full-null receipt has rank_acc = j through j=156000).
        The residual risk is narrower: an index-mapping error in the column-restricted VIEW
        that happens to preserve rank. That is not cheaply excluded by re-reading the receipt;
        it is cheaply excluded by replicating the mechanism at D=5 with a distinct engine (see
        next_concrete_action). I refer any deeper integrity question to the Validator.

    - id: OBJ-4-a-projection-is-not-a-support-confined-system
      severity: high
      target: >-
        what "genuine, support-independent deficit" is allowed to MEAN; H-DREG-001
        assumptions[2] ("The T11 null has identical monomial support ... only coefficients
        randomized"); RT-N12D6's proposed "third arm".
      finding: >-
        CTRL-B measures dim of the PROJECTION of the null's row space onto sem's coordinate
        window. The projected object is not the Macaulay matrix of any boolean system --
        truncating degree-6 terms does not commute with multiplication -- so 156520 is "the
        best a semi-regular ideal looks THROUGH sem's window", not "the best an ideal CONFINED
        to sem's window can do". The predecessor proposed the latter as an equivalent
        alternative. I tested whether that alternative is even constructible and it is not, by
        the natural strengthening: a per-equation VARIABLE-SUPPORT-matched null (each
        equation's monomials drawn only from the variables that actually occur in that
        equation, same per-degree counts) expands to 190049 of the 190051 D=6 columns -- it
        recovers essentially the FULL support, not sem's 174035. Sem's equations are genuinely
        variable-sparse (per-equation variable supports 13..20 of 24), so the confinement of
        sem's Macaulay support is a finer algebraic property than variable sparsity and is not
        reproducible by randomization at that level.
      consequence: >-
        Two things follow, and the Coordinator needs both. (1) CTRL-B's design is VINDICATED:
        the projection is the right, and possibly the only cheaply constructible, comparison,
        and the predecessor's "equivalent alternative third arm" should be de-prioritised with
        this reason recorded. (2) The MECHANISM attribution is not licensed: the measurement
        separates sem from generic ideals, but it cannot separate "an O(n) family of extra
        low-degree syzygies" (H-DREG-001's stated mechanism) from "the same algebraic rigidity
        that confines the support in the first place". Calling the 17947 "extra syzygies" is
        an interpretation the data does not distinguish. H-DREG-001 assumption[2] should be
        recorded not merely as false-as-implemented (RT-N12D6 OBJ-2) but as apparently
        UNSATISFIABLE by randomization over GF(2).

    - id: OBJ-5-the-hypothesis-metric-is-anti-aligned-with-its-own-mechanism
      severity: high
      target: H-DREG-001 statement + predictions[0]; any future reading of a growing deficit as progress
      finding: >-
        H-DREG-001 says d_reg "grows strictly slower than the ... null -- EQUIVALENTLY, the
        deficit (sr_pred_D - rank_D) grows with n", and predictions[0] sets direction: higher.
        These are not equivalent; they are opposed. deficit = sr_pred - rank, so a larger
        deficit means a SMALLER degree-<=D ideal, a LARGER quotient, and therefore a LATER
        collapse to s=1 -- d_reg(sem) >= d_reg(null), the wrong direction for an attacker.
        CTRL-B makes this unavoidable rather than academic: 17947 is 53.5% of the semi-regular
        degree-<=6 quotient (33531), which on the stated metric is a spectacular
        "confirmation" of predictions[0] while being unambiguous evidence against the WIN
        scenario the hypothesis exists to test. Only the disjunct "any cell shows d_reg(sem) <
        d_reg(null)", or a bounded d_reg, can support the WIN; the deficit clause is a
        NON-GENERICITY detector, not a WIN detector.
      remedy: >-
        A superseding note on H-DREG-001 recording the mis-orientation, so that no future
        batch reports a growing deficit as progress toward a cheaper solve.

    - id: OBJ-6-fixed-D-series-drifts-relative-to-the-collapse-degree
      severity: medium
      target: >-
        the "decelerating 1322/1862/1999" pillar of DEC-20260720-002, DEC-GOAL-DREG-001-B001
        and DEC-GOAL-DREG-001-B002, and H-DREG-001 falsification_conditions[1].
      finding: >-
        d_reg(n) = 6, 7, 8, 9 at n = 9, 12, 15, 18 (my own recomputation of the semi-regular
        Hilbert series; the same routine reproduces the committed sr_pred values 29418, 70935,
        145881, 156520 exactly). A FIXED D=5 series therefore sits at offsets d_reg - D =
        1, 2, 3, 4 -- the probe degree recedes from collapse as n grows. Normalised by the
        semi-regular quotient at the same cell the "decelerating" series is
        0.2921 / 0.0508 / 0.0180 / 0.0067, a fast DECAY that is exactly what a receding probe
        degree produces, not a statement about growth in n at fixed structural position. At
        the fixed offset d_reg - 1 the only two values available are 909 (n=9, D5 -- reported
        in ledger EV-SIG-002 / EV-SIG-005, a different experiment family; NOT verified by me)
        and 17947 (n=12, D6, this batch). I do not build a conclusion on a two-point,
        cross-experiment, partially unverified comparison, and n=9 is separately flagged in
        EV-SIG-002 as carrying elevated small-n structure. But the Coordinator should stop
        resting the negative verdict on "the deficit decelerates": that pillar is fragile and
        the negative verdict does not need it -- the SIGN carries it at any magnitude.

    - id: OBJ-7-residual-asymmetry-density
      severity: medium
      target: RTQ-4, "is the comparison NOW apples-to-apples?"
      finding: >-
        Yes at the level that matters -- identical 174035-column space, identical 183312 rows,
        same cell and seed, and the producer correctly never subtracted the support-independent
        sr_pred from the restricted rank (manifest expected.sr_pred_is_not_the_predictor_here;
        raw-result sr_pred_note). I confirm the row multiset is structurally matched, not just
        equal in count: 12 generators of degree 2 x sum_{d<=4} C(24,d) + 12 of degree 3 x
        sum_{d<=3} C(24,d) = 155412 + 27900 = 183312 exactly, so neither arm lost a row to
        cancellation or degree overflow. The surviving asymmetry is DENSITY: sem D6 Macaulay
        nnz = 5345451 (29.16 per row) versus null 5768183 (31.47) and restricted null 5468179
        (29.83). Even on the identical column space the null carries 122728 more nonzeros
        (2.2%). Rank is not a function of density, so this does not invalidate the comparison,
        but it does mean the arms differ in more than "which columns", and it is where the
        structure lives. UNCHECKED: whether an nnz-per-row-matched null moves the benchmark.

    - id: OBJ-8-declared-input-missing
      severity: low   # process, not mathematics; RESOLVED mid-review, recorded for the trail
      target: the archive/verification chain, not the measurement
      finding: >-
        At the time I opened this review, the declared input
        coordination/goals/GOAL-DREG-001/batches/BATCH-003/snapshot/snapshot_commit_receipt.json
        did not exist: the directory was empty and nothing was tracked under it at HEAD
        8302c83a. I proceeded because the run artifacts themselves were properly committed
        (9 files at 8302c83a, clean working tree, parent ba28a949 carrying the pre-registered
        bracket), so the object under review was a genuine committed snapshot regardless.
      resolved_during_this_review: >-
        The Coordinator committed the receipt in ed07195b (with CORR-B003-001 explaining the
        omission as SNAP-DEV-1). I read it: it names commit_sha 8302c83a, parent_sha ba28a949,
        and per-path sha256 for all nine files, and its hashes for raw-result.json
        (139cd6cc...), column-audit.json (4cd1e5c2...), chunk-coverage.log (a4b1f2ed...),
        command.txt (3a4f34ec...), stdout (97f424c3...), stderr (c1b7f2a0...) and the driver
        (7803918d...) agree with the values recorded inside manifest.yaml. The snapshot I
        reviewed is therefore the receipted one. No objection remains; recorded only so the
        trail shows the review began before the receipt existed.

  # ------------------------------------------------- explicit answers, RTQ-1..RTQ-5
  answers:
    RTQ-1-degree-axis-license:
      verdict: >-
        It licenses a GRADED HILBERT-FUNCTION statement at degree 6 for this one cell, and
        nothing about d_reg, growth, or gap.
      licensed: >-
        For n=12, t=3, ti=0, seed=2026, nb=24, D=6: sem's degree-<=6 ideal has dimension 138573
        on its own 174035-monomial column support; a degree-multiset-matched random boolean
        null, viewed on that identical support, has dimension 156520; hence sem's degree-<=6
        quotient is 35462 versus 17515 (a factor 2.02), a shortfall of 17947 of which zero is
        attributable to sem's 16016 missing degree-6 columns.
      NOT_licensed:
        - >-
          d_reg(sem) itself. D=6 < d_reg(12)=7, so this is one value of a graded Hilbert
          function, not a collapse degree. A larger quotient at degree 6 does not entail
          HF_sem[7] > 0; it is consistent with and suggestive of d_reg(sem) >= 7, not a proof.
        - >-
          Deficit GROWTH in n. One n. The D5 cross-n series is at a drifting offset (OBJ-6)
          and is itself support-unrepaired (OBJ-2).
        - >-
          The gap(n) = d_reg - d_ff clause. Untouched and still untestable. The null
          first-fall was never measured (infra-limited) and sem's d_ff = 2-3 at ff_s = 0.0
          is the trivial boolean field-relation fall, non-operative (RT-N12D6 OBJ-5,
          unchanged by this batch).
        - >-
          Any CI-backed sem-vs-null separation (1 seed, 1 target index, no replicates).
        - >-
          Any mechanism attribution to extra syzygies specifically (OBJ-4).
        - >-
          Any solve, relation, factor-base, speedup, or sub-rho claim. certificate.kind is none.
        - >-
          Anything about the prime-field ECDLP target. t=3 / t=7 binary Weil descent remains
          this campaign's NEGATIVE CONTROL.
        - >-
          The reading that H-DREG-001's deficit prediction being met is support FOR the
          hypothesis (OBJ-5).
      h_dreg_001_clauses_still_untouched: >-
        predictions[1], the gap(n) clause; and the d_reg(sem) < d_reg(null) disjunct of
        predictions[0]

    RTQ-2-cheapest-falsification:
      ranked_by_information_per_second:
        - rank: 1
          id: CTRL-D5-RESTRICT
          what: rank of the null Macaulay matrix at D=5 restricted to sem's exact 46717-column D5 support
          cost: ~900 s wall cap, ~4 GB, 1-2 invocations
          cost_basis: >-
            The committed D5 cells at this cell ran in 28.2 s (sem, RUN-DREG-001-VALIDATE-N12-A)
            and 32.5 s (null, RUN-DREG-001-VALIDATE-NULL-N12-D5-B); the CTRL-B prepare phase
            (build + restrict + audit) cost 23.24 s at D6 and is cheaper at D5. A distinct-engine
            dense cross-check is affordable here and only here: the dense 31512 x 46717 GF(2)
            matrix is 175 MiB.
          why_first: >-
            It is the only proposal that is simultaneously (a) a direct test of the exact
            mechanism CTRL-B's headline rests on -- "deleting sem-absent columns costs zero
            rank" -- at an independent degree, (b) a repair of a falsified committed claim
            (OBJ-2), and (c) the first chance to clear Validator CAVEAT-2 (no distinct-engine
            confirmation) at a reachable size. Roughly 1/40 the cost of any D6 arm.
        - rank: 2
          id: CTRL-SEED2
          what: sem D6 full-column rank at a second seed / target index, same n=12
          cost: ~2300-2600 s, ~7.7 GB, 1 run
          cost_basis: the committed D6 arms cost 2284.76 s / 7.68 GB (full null, BATCH-002) and 2579.15 s / 6.31 GB (CTRL-B)
          note: >-
            Necessary before 17947 is described as characteristic of the family rather than of
            one instance, but it cannot BREAK the reading -- it can only widen or narrow it.
        - rank: 3
          id: CTRL-GRADED-HF
          what: graded pivot-degree Hilbert function readout of the existing D6 matrices
          cost: instrument change; not costed here, and I will not invent a timing
          note: >-
            This is the observable the goal record itself names as admissible. It converts a
            scalar into a curve HF_sem[0..6] and is the only cheap route toward a d_reg-relevant
            statement at n=12, because the honest route -- the D=7 rank -- is out of reach on
            this host: D7 at n=12 is 820872 x 536155 with sr_pred[7] = 502624, and the
            instrument's O(rank x ncols)-bit carrier alone is ~31.4 GiB (the same estimate gives
            ~3.5 GiB at D6 against an observed 6.3-7.7 GB peak RSS), versus ~14.8 GB free.
        - rank: 4
          id: CTRL-THIRD-ARM (support-matched null)
          what: RT-N12D6's proposed "genuinely support-matched null"
          recommendation: DE-PRIORITISE, with the reason recorded
          note: >-
            My probe indicates it is not constructible by randomization: the natural
            strengthening (per-equation variable-support matching) yields 190049 of 190051 D6
            columns, essentially full support (OBJ-4).
      single_cheapest: CTRL-D5-RESTRICT   # see next_concrete_action for the full task card

    RTQ-3-sign-and-baseline:
      sign_verdict: >-
        UNCHANGED IN DIRECTION, STRONGER IN MAGNITUDE. The residual still points the wrong way
        for an attack, and it now points that way about nine times harder than BATCH-002's
        quarantined floor allowed. deficit = sr_pred - rank means sem's degree-<=6 ideal is
        SMALLER than semi-regular: 138573 vs 156520 on the identical column space, quotient
        35462 vs 17515 (2.02x). A larger quotient one degree below the null's collapse means
        the Semaev cascade RAISES the solving degree, i.e. d_reg(sem) >= d_reg(null) = 7. This
        is consistent with, and independent of, the BATCH-001 result reached by a different
        route (graded HF + q->s collapse with enumerated s=1 at n=6, 9; FINDING_v2 Part D).
        I state the limit precisely: a larger degree-6 quotient does NOT by itself prove
        HF_sem[7] > 0, so "d_reg(sem) > 7" is suggested, not proven, by this datum -- but there
        is no reading of it that is evidence for d_reg(sem) < d_reg(null).
      honest_reading_of_the_batch: >-
        Yes, plainly: NO ATTACK, NEGATIVE CONTROL REINFORCED. The correction that BATCH-002
        applied in the attacker's favour (shrinking the signal to ">= 1931, O(10^3)") was in
        fact unnecessary; removing it does not open anything, it deepens the same hole.
      baseline_honesty_audit: >-
        Correct as recorded. certificate.kind = none with an explicit reason, claim_tier "toy",
        and no end-to-end cost path, so no Pollard-rho or BSGS comparison is instantiated and
        none should be. The producer receipt contains no attack language at all
        (interpretation_note, observation_note) -- that discipline held.

    RTQ-4-residual-asymmetry: >-
      Answered in OBJ-4 (projection versus support-confined system -- the load-bearing
      asymmetry) and OBJ-7 (density -- the residual measurable one). The row multiset is
      verified structurally matched, not merely equal in count (183312 = 12*12951 +
      12*2325), and the producer correctly kept the support-independent sr_pred out of the
      restricted comparison.

    RTQ-5-magnitude-sensitivity:
      magnitude_invariant_across_the_bracket_1931_to_17947:
        - >-
          the SIGN and every conclusion resting on it (wrong direction for the attack;
          negative control reinforced)
        - >-
          the fact that this is not d_reg (fixed probe degree 6 < d_reg = 7)
        - >-
          no growth, no CI, no gap, no speedup, no sub-rho claim; certificate.kind is none;
          toy tier
        - >-
          the baseline verdict (no rho/BSGS comparison instantiated; the specialized
          baseline loses more than 1100 bits)
      magnitude_dependent_and_NOW_FALSIFIED_at_17947:
        - >-
          the claim that the genuine signal is O(10^3) rather than the O(1.8x10^4) headline
          (DEC-GOAL-DREG-001-B002 rationale)
        - >-
          the claim that 1322 (D5) and >=1931 (D6) are mutually consistent and BOTH small
          (RT-N12D6 OBJ-3)
        - >-
          the near-vacuity of the support correction -- it is exactly vacuous, 0 of 17947
      magnitude_dependent_and_now_open: >-
        The D6 datum regains its full magnitude: 53.52% of the semi-regular degree-<=6 quotient
        versus 5.08% at D5 in the same cell. That 10.5x relative jump across one degree is the
        strongest single reason the D5 series cannot be used as a proxy for near-collapse
        behaviour (OBJ-6), and it is an OBSERVATION requiring replication, not a finding.

  # ---------------------------------------------------------------- controls I ran
  required_controls:
    - id: RT-PROBE-1-blocknull-feasibility
      status: RAN (scratch-only, outside the repository; no rank computed; owns no run directory)
      purpose: >-
        Test whether the successor control I intended to propose -- a per-equation
        variable-support-matched ("block") null -- is a genuinely different arm from the
        committed boolean_null and whether it reproduces sem's 174035-column D6 support.
      command: >-
        cd /Volumes/Volume/crypto-autoresearcher-worktrees/claude-dreg-law &&
        TMPDIR=/Volumes/Volume/sage-scratch-dreg SAGE_TMP=/Volumes/Volume/sage-scratch-dreg
        /usr/bin/time -l /usr/local/bin/sage -python
        /Volumes/Volume/sage-scratch-dreg/rt-ctrlb/blocknull_feasibility_probe.py
      verbatim_output: |
        [probe     0.2s] sem system rebuilt: nb=24 n_eqs=24 hash=c47d17c3fd70d5d8 matches_committed=True
        [probe     0.2s] per-equation variable-support sizes (out of 24): {13: 1, 14: 1, 15: 3, 16: 8, 17: 1, 18: 2, 19: 4, 20: 4}
        [probe     0.2s] per-equation degrees: {3: 12, 2: 12}
        [probe     3.6s] sem D6 column support = 174035 (committed 174035), nrows = 183312 (committed 183312)
        [probe     7.3s] block-null D6 column support = 190049, nrows = 183312, hash=6c531ab3ebc84e0d
        [probe     7.5s] SUMMARY: sem_ncols=174035 block_null_ncols=190049 equal=False subset=False peak_rss_gb=0.46
        (/usr/bin/time -l: 27.97 real, maximum resident set size 490995712, 0 swaps)
      result: >-
        My own streaming reconstruction reproduces the committed sem D6 ncols (174035) and
        nrows (183312) exactly, which validates the probe code. The block null reaches 190049
        of 190051 columns: variable-support matching does NOT reproduce sem's confinement.
        This REFUTES my own intended proposal and de-prioritises RT-N12D6's "third arm"
        (OBJ-4). Probe null seed 20260726, declared in the JSON.
      artifacts:
        - /Volumes/Volume/sage-scratch-dreg/rt-ctrlb/blocknull_feasibility_probe.py
        - /Volumes/Volume/sage-scratch-dreg/rt-ctrlb/blocknull_feasibility_probe.json
    - id: RT-PROBE-2-density-and-D5-support
      status: RAN (scratch-only; no rank computed)
      purpose: quantify the residual density asymmetry (OBJ-7) and check the predecessor's D5 "fully support-matched" claim (OBJ-2)
      command: >-
        cd /Volumes/Volume/crypto-autoresearcher-worktrees/claude-dreg-law &&
        TMPDIR=/Volumes/Volume/sage-scratch-dreg SAGE_TMP=/Volumes/Volume/sage-scratch-dreg
        /usr/bin/time -l /usr/local/bin/sage -python
        /Volumes/Volume/sage-scratch-dreg/rt-ctrlb/density_and_d5_support_probe.py
      verbatim_output: |
        [probe2    0.2s] sem hash c47d17c3fd70d5d8 | null hash f2f610730a715593
        [probe2    1.3s] D=5 sem ncols=46717 nnz=941609 (29.88/row) | null ncols=55455 nnz=997147 (31.64/row) | gap=8738 {4: 2, 5: 8736}
        [probe2    9.1s] D=6 sem ncols=174035 nnz=5345451 (29.16/row) | null ncols=190051 nnz=5768183 (31.47/row) | gap=16016 {6: 16016}
        [probe2    9.1s] peak_rss_gb=0.48
        (/usr/bin/time -l: 13.13 real, maximum resident set size 516292608, 0 swaps)
      result: >-
        Both system hashes reproduce the committed ones bit-for-bit, and the D6 null nnz
        5768183 reproduces column-audit.json exactly. D5 is NOT support-matched (46717 vs
        55455, gap 8738, and the gap is not confined to the probe degree: {5: 8736, 4: 2}).
        sem is systematically sparser per row than either null arm.
      artifacts:
        - /Volumes/Volume/sage-scratch-dreg/rt-ctrlb/density_and_d5_support_probe.py
        - /Volumes/Volume/sage-scratch-dreg/rt-ctrlb/density_and_d5_support_probe.json
    - id: RT-PROBE-3-arithmetic-recomputations
      status: RAN (pure arithmetic, no system build)
      result: >-
        Independently recomputed and matching the committed receipts: sum_{d<=6} C(24,d) =
        190051; sum_{d<=5} C(24,d) = 55455; C(24,6) - 16016 = 118580 = sem's degree-6 support;
        rows 12*sum_{d<=4}C(24,d) + 12*sum_{d<=3}C(24,d) = 183312; semi-regular HF partial sums
        33531 (D6) and 26037 (D5); sr_pred reproduced at 29418 (n=12 D5), 70935 (n=15 D5),
        145881 (n=18 D5), 156520 (n=12 D6) -- four committed receipts, four exact matches; and
        d_reg = 6/7/8/9 at n = 9/12/15/18. Derived: restricted-null corank 17515, sem corank
        35462, 35462 - 17515 = 17947, and the deficit/quotient ratios in OBJ-6.

  counterexample_or_mutation: >-
    The counterexample that RT-N12D6 offered against the old headline no longer bites, and its
    failure is instructive. It imagined a system that omits 16016 top-degree monomials but is
    "otherwise rank-generic", exhibiting deficit ~16016 with zero extra syzygies. CTRL-B shows
    that omission by itself costs NOTHING: on the identical window the generic arm keeps all
    156520 pivots. So the mutation class "sparse support, generic elsewhere" predicts deficit
    ~0, not ~16016, and the measured 17947 survives it entirely. The mutation that would still
    bite is the reverse one, and it is the open question of OBJ-4: exhibit any boolean system,
    unrelated to Semaev, whose D6 Macaulay support is confined to ~174035 columns and whose
    rank on that window is also ~17947 short of 156520. If such a system exists, the deficit is
    a generic consequence of support confinement rather than a Semaev signature. My probe shows
    the naive constructions do not confine the support at all (190049 of 190051), so this
    mutation is currently un-instantiated -- which is itself the reason the mechanism claim in
    OBJ-4 must stay open rather than being resolved either way.

  baseline_comparison: >-
    No Pollard-rho or BSGS comparison is instantiated, and correctly so: certificate.kind =
    none, this is a pure exact-rank measurement with no relation, no solve, and no end-to-end
    cost path. The closest specialized baseline is the semi-regular Groebner/last-fall cost
    model of FINDING_v2 Part C: at the real configuration t=7, n=161 (nb=966, 161 deg-2 + 805
    deg-3) the semi-regular d_reg = 150 gives 2^1194.4 (omega=2) to 2^1415.3 (omega=2.37)
    against rho 2^80.5 on E(GF(2^161)) -- a loss of 1113.9 to 1334.8 bits. This datum moves the
    structured system to a LARGER quotient at fixed degree, i.e. a later collapse and a MORE
    expensive Groebner solve, i.e. further from rho, not closer. For scale: even a hypothetical
    reduction of d_reg from 150 to 140 would leave a four-figure bit deficit, so no single toy
    cell on the degree axis of this kind can move the crypto-scale verdict in either direction.

  narrowest_supported_statement: >-
    For the single committed cell n=12, t=3, ti=0, seed=2026, nb=24, D=6, measured with the
    column-chunked block-m4ri instrument under a 2700 s / 12 GB budget (claim tier: toy;
    certificate.kind: none), the boolean chained Semaev m=3 degree-<=6 Macaulay matrix has
    exact GF(2) rank 138573 on its own 174035-monomial column support while a
    degree-multiset-matched random boolean null, restricted to that identical support, has rank
    156520 -- a support-INDEPENDENT shortfall of 17947 (sem quotient 35462 vs 17515, 2.02x)
    whose direction means the Semaev degree-<=6 ideal is SMALLER than semi-regular and its
    collapse therefore no earlier, so it is evidence consistent with d_reg(sem) >= d_reg(null)
    = 7 and against, never for, a cheaper polynomial solve.

  next_concrete_action:
    named_successor_task: TASK-20260727-DREG-CTRLB-D5-P1
    run_id: RUN-DREG-001-CTRLB-N12-D5
    role: executor    # NOT a reviewer; this is a producer task the Coordinator must scope
    write_scope: [experiments/EXP-DREG-001/runs/RUN-DREG-001-CTRLB-N12-D5/]
    arm: null_restricted_to_sem_D5_support
    cell: {n: 12, t: 3, ti: 0, seed: 2026, D: 5, nb: 24, nrows: 31512}
    columns: {kept: 46717, deleted: 8738, full: 55455, deleted_degree_histogram: {5: 8736, 4: 2}}
    budget: {wall_clock_seconds: 900, memory_gb: 4, maximum_runs: 2}
    cost_basis: >-
      Committed same-cell D5 timings 28.2 s (sem, VALIDATE-N12-A) and 32.5 s (null,
      VALIDATE-NULL-N12-D5-B); CTRL-B's prepare/restrict/audit phase cost 23.24 s at the larger
      D6 size. The dense distinct-engine cross-check is 31512 x 46717 bits = 175 MiB. No timing
      is invented: the 900 s cap is a safety margin over measurements roughly 30x smaller.
    preregistered_bracket_theorem: {restricted_rank: [20680, 29418], deficit_genuine_D5: [-7416, 1322]}
    exact_discriminating_prediction: >-
      If the CTRL-B reading is correct, rank(null | sem D5 support) = 29418 EXACTLY, hence
      deficit_genuine(D5) = 29418 - 28096 = 1322, numerically identical to the raw D5 headline
      -- because 29418 + 8738 = 38156 < 55455 leaves the null's row space in general position
      with respect to the 8738-dimensional deleted coordinate subspace (slack 17299), the same
      argument that predicts the D6 endpoint.
    kill_condition: >-
      Any rank strictly below 29418 falsifies "column deletion is rank-free for this family and
      this instrument", which (a) makes the D6 exact-endpoint landing an anomaly that must be
      re-measured before 17947 is released, and (b) simultaneously quarantines the entire D5
      series 909/1322/1862/1999 by the predecessor's own bound. A rank above 29418, or a kept
      set that is not exactly sem's D5 support, is an integrity failure with no interpretation
      attached.
    secondary_gain: >-
      Ranking the same restricted matrix with a distinct engine (dense Sage M4RI on the 175 MiB
      matrix) closes Validator CAVEAT-2 at a reachable size, which no D6 cell can afford.
    explicitly_not_run_by_me: >-
      I own no run directory and commissioned no compute for this. The BATCH-002 deviation
      (red team writing rt-control/ into the coordinator-owned run scope) is not repeated: my
      two probes are scratch-only under /Volumes/Volume/sage-scratch-dreg/rt-ctrlb/ and compute
      no rank.

  # -------------------------------------------------------- caveats for the coordinator
  binding_caveats_for_coordinator:
    - id: RT-CAV-B3-1
      blocks: lifting the quarantine as a bare "17947 is real" without a re-label
      detail: >-
        Lift the quarantine's STATED GROUND (it is refuted) but replace it, in the same record,
        with the stronger bar: 17947 is a WRONG-SIGN, single-cell, single-seed, sub-d_reg,
        certificate-none quantity. It may enter an evidence record as a measurement of the
        degree-6 graded Hilbert function on the tested cell. It may not enter any record as
        progress, as an opening, as a d_reg statement, or as support for H-DREG-001's WIN.
    - id: RT-CAV-B3-2
      blocks: any decision text that reuses the BATCH-002 language
      detail: >-
        Three committed sentences are now falsified and need SUPERSEDING corrections (never
        overwrites, AGENTS rule 4): ">= ~89% of 17947 is a degree-6 support gap, not syzygies"
        (goal checkpoint BATCH-002); "The genuine signal is O(10^3), not the O(1.8x10^4)
        headline" (DEC-GOAL-DREG-001-B002); and the commit subject "D6 deficit is ~89%
        support-confounded" (6a141ed4). Measured attribution: 0% support gap, 100% genuine.
        Name the error class explicitly in the correction so the ledger records it: a
        worst-case bound reported as a point estimate at its unfavourable endpoint.
    - id: RT-CAV-B3-3
      blocks: citing the D5 series 909/1322/1862/1999 as "the support-matched observable"
      detail: >-
        It is not support-matched. sem D5 ncols 46717 vs null 55455 at n=12 (gap 8738,
        histogram {5: 8736, 4: 2}), with the gap growing across the ladder (17.8% at n=15,
        19.2% at n=18). Applying BATCH-002's own bound at D5 yields deficit_genuine(D5) in
        [-7416, +1322] -- it cannot even establish positivity. Until TASK-20260727-DREG-CTRLB-D5-P1
        runs, the D5 series must be cited with the same correction pending that D6 carried, and
        must not be described as clean.
    - id: RT-CAV-B3-4
      blocks: any reading of a growing deficit as progress, in this or any later batch
      detail: >-
        H-DREG-001's primary metric (deficit, direction: higher) is anti-aligned with its own
        stated mechanism (d_reg falls below the null). The word "equivalently" in the
        hypothesis statement is false. Record a superseding note; only "d_reg(sem) <
        d_reg(null)" or a bounded d_reg can support the WIN.
    - id: RT-CAV-B3-5
      blocks: attributing the 17947 to "extra syzygies" or to Semaev-specific algebra
      detail: >-
        CTRL-B compares sem against the PROJECTION of a generic ideal, not against an ideal
        confined to sem's monomial window; my probe indicates the latter is not constructible by
        randomization (a variable-support-matched null reaches 190049 of 190051 D6 columns).
        The measurement separates sem from generic ideals; it does not separate "extra
        syzygies" from "the rigidity that confines the support". Record H-DREG-001
        assumptions[2] as apparently unsatisfiable over GF(2), not merely unimplemented.
    - id: RT-CAV-B3-6
      blocks: describing the D6 rank as independently reproduced
      detail: >-
        Validator CAVEAT-2 is inherited and still open: no distinct-engine confirmation of any
        D6 rank exists, and CTRL-B reuses the BATCH-002 null adjacency (independently rebuilt
        in-process, which is a strong internal check but the same code path). The proposed D5
        control is the first affordable place to close it.
    - id: RT-CAV-B3-7
      blocks: nothing further -- CLEARED during this review; retained for the audit trail
      detail: >-
        The declared input snapshot/snapshot_commit_receipt.json was absent when this review
        opened and was committed mid-review in ed07195b (CORR-B003-001, SNAP-DEV-1). I
        verified it binds the snapshot I reviewed: commit_sha 8302c83a, parent_sha ba28a949,
        nine per-path hashes agreeing with manifest.yaml. See OBJ-8.

  scope_limits:
    - >-
      Single cell -- n=12, t=3, ti=0, seed=2026, nb=24, D=6, one target index, no
      replicates, no CIs.
    - >-
      Toy tier; certificate.kind is none; no solve, no relation, no cost path, no speedup.
    - >-
      A fixed-degree graded Hilbert-function statement, NOT a measurement of d_reg
      (D=6 < d_reg=7).
    - >-
      t=3 / t=7 binary Weil descent is this campaign's NEGATIVE CONTROL for the
      prime-field target.
    - >-
      This is a SCOPED objection set plus a scoped negative reading. It is NOT an
      impossibility result, NOT a proof of security, and NOT a status change. Negative
      evidence closes only the exact tested scope (AGENTS rule 6), H-DREG-001's official
      status is the Coordinator's, and per the goal record's ISOLATION note this campaign
      does not flip it on main.
    - >-
      The n=9 D5 value 909 is quoted from ledger EV-SIG-002 / EV-SIG-005 (a different
      experiment family) and was NOT verified by me; no conclusion here rests on it.
    - >-
      Unchecked -- whether an nnz-per-row-matched null moves the benchmark (OBJ-7);
      whether any non-Semaev system can confine its D6 support to ~174035 columns (OBJ-4);
      HF_sem[7] and hence d_reg(sem) at n=12 (D7 needs ~31.4 GiB of carrier on a host with
      ~14.8 GB free).

  artifact_paths:
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-CTRLB-N12-D6/raw-result.json
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-CTRLB-N12-D6/manifest.yaml
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-CTRLB-N12-D6/column-audit.json
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-CTRLB-N12-D6/chunk-coverage.log
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N12-D6/raw-result.json
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-VALIDATE-N12-A/raw-result.json
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-VALIDATE-NULL-N12-D5-B/raw-result.json
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-VALIDATE-N15-A/raw-result.json
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-VALIDATE-N18-A/raw-result.json
    - coordination/goals/GOAL-DREG-001/batches/BATCH-002/reviews/RT-N12D6.md
    - coordination/goals/GOAL-DREG-001/batches/BATCH-002/reviews/VAL-N12D6.md
    - coordination/goals/GOAL-DREG-001/batches/BATCH-002/decision.yaml
    - ledger/H-DREG-001.yaml
    - ledger/goals/GOAL-DREG-001.yaml
    - research/dreg-linear-law/FINDING_v2.md
    - src/h012_peel_rank.py
    - src/macaulay_export.py
    - /Volumes/Volume/sage-scratch-dreg/rt-ctrlb/blocknull_feasibility_probe.py       # outside the repo
    - /Volumes/Volume/sage-scratch-dreg/rt-ctrlb/blocknull_feasibility_probe.json     # outside the repo
    - /Volumes/Volume/sage-scratch-dreg/rt-ctrlb/density_and_d5_support_probe.py      # outside the repo
    - /Volumes/Volume/sage-scratch-dreg/rt-ctrlb/density_and_d5_support_probe.json    # outside the repo

  inference:
    requested_policy: review-xhigh
    resolved_model: claude-opus-5
    fallback_used: true
    reasoning_effort: "not exposed by this runtime"
    reasoning_effort_note: >-
      This Claude Code session exposes no reasoning-effort parameter to the agent and none was
      requested or resolved. Recorded as unavailable rather than guessed (AGENTS rule 9).
    note: >-
      Claude Code cannot resolve GPT-5.6 policy aliases; .claude/agents/ frontmatter accepts
      only Claude models. Explicit, declared, non-silent fallback per the CLAUDE.md model policy
      note and AGENTS.md rule 11.
    independent_session: true
    independent_session_note: >-
      Dedicated red-team session; did not originate the CTRL-B claim, did not produce the run,
      and is distinct from the Validator session (AGENTS rule 12).
  budget_used:
    wall_clock_seconds_cap: 3600
    memory_gb_cap: 8
    maximum_runs_cap: 2
    runs_used: 2                 # both scratch-only, no rank computed
    peak_rss_gb_observed: 0.48
    repository_writes: [coordination/goals/GOAL-DREG-001/batches/BATCH-003/reviews/RT-CTRLB.md]
    git_operations: none         # no add, no commit, no push
```

## Load-bearing numbers

All values below are either read from the committed receipts named in the last column or
recomputed by me in this session (marked **RT**); nothing is estimated or carried over
unverified.

| quantity | sem | null (full) | null restricted to sem support | source |
|---|---|---|---|---|
| nrows (D6) | 183312 | 183312 | 183312 | receipts; **RT** 12·12951 + 12·2325 |
| ncols (D6) | 174035 | 190051 | 174035 | receipts; **RT** streaming rebuild |
| exact GF(2) rank (D6) | 138573 | 156520 | **156520** | BATCH-002 / CTRL-B receipts |
| quotient = ncols − rank (D6) | **35462** | 33531 | **17515** | **RT** |
| deficit vs the same-window null | **17947** | — | 0 | **RT** 35462 − 17515 |
| share of the deficit that is support gap | **0 of 17947** | — | — | **RT**, from CTRL-B |
| Macaulay nnz (D6) | 5345451 (29.16/row) | 5768183 (31.47/row) | 5468179 (29.83/row) | **RT** probe 2; column-audit.json |
| ncols (D5) | **46717** | **55455** | not measured | VALIDATE-N12-A / NULL-N12-D5-B; **RT** |
| exact GF(2) rank (D5) | 28096 | 29418 = sr_pred | not measured | receipts |
| deficit (D5) | 1322 | 0 | **unknown, in [−7416, +1322]** | **RT** bound |

Deficit normalised by the semi-regular quotient at the same cell, with the probe degree's
offset below collapse (**RT**; the same routine reproduces the committed `sr_pred` at four
independent cells — 29418, 70935, 145881, 156520):

| n | nb | d_reg | D | offset d_reg−D | sr_pred | quotient | deficit | deficit/quotient |
|---|---|---|---|---|---|---|---|---|
| 9 | 18 | 6 | 5 | 1 | 9504 | 3112 | 909 † | 0.2921 |
| 12 | 24 | 7 | 6 | **1** | 156520 | 33531 | **17947** | **0.5352** |
| 12 | 24 | 7 | 5 | 2 | 29418 | 26037 | 1322 | 0.0508 |
| 15 | 30 | 8 | 5 | 3 | 70935 | 103502 | 1862 | 0.0180 |
| 18 | 36 | 9 | 5 | 4 | 145881 | 297823 | 1999 | 0.0067 |

† 909 is quoted from ledger `EV-SIG-002` / `EV-SIG-005` (a different experiment family) and was
**not** verified by me; the quotient and ratio in that row are my recomputation applied to a
number I did not check. No conclusion in this report rests on it.

The middle three rows are the "decelerating series"; read at a common offset instead of a
common degree, they are not a series at all.

## One-paragraph verdict

CTRL-B did exactly what a good control does and it went against the agent that specified it.
Deleting all 16016 degree-6 columns that sem cannot reach cost the null zero rank, so none of
the 17947 is a support gap and my predecessor's headline correction — a worst-case bound
reported as if it were an estimate — is falsified by its own control. The quarantine's stated
ground should therefore be lifted, in a superseding record that names the error. But the
release is not good news: the same measurement says the Semaev degree-≤6 ideal is 17947
dimensions *smaller* than semi-regular on the identical column space, a quotient of 35462
against 17515, so the cascade pushes the collapse *later* and Gröbner *further* from
Pollard-rho — the negative control is reinforced roughly nine times harder than the
quarantined floor allowed, and H-DREG-001's own "deficit grows" metric turns out to be
anti-aligned with the win it was written to detect. What the cell licenses is one value of a
graded Hilbert function at one toy cell, one seed, one target, at a degree below d_reg, with
`certificate.kind: none`; it licenses no d_reg claim, no growth claim, no gap claim, and no
cryptanalytic claim of any kind. The one thing worth buying next is small: at D=5 the same
restriction costs about thirty seconds instead of forty minutes, it can be checked by a second
engine, it predicts 29418 exactly, and it repairs the fallback observable that BATCH-002 leaned
on and that this review found is not support-matched either.
