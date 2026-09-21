# =====================================================================
# RED TEAM REPORT -- TASK-20260822-de2fa2
# GOAL-ECRANK-002 / BATCH-e0caa5
#
# THIS FILE IS STRICT YAML DESPITE ITS .md EXTENSION. The extension is
# fixed by ledger/handoffs/TASK-20260822-de2fa2.yaml (deliverables and
# artifact_paths both name red_team_report.md); the role contract and the
# dispatch card ask for a YAML record. Both are honoured by emitting YAML
# at the handoff-declared path. Exactly one file was written by this task.
# WRITE-ONCE. Corrections are new records, never edits to this one.
# This report CHANGES NO STATUS and ADJUDICATES NO HYPOTHESIS.
# =====================================================================

red_team_report:
  id: RT-20260904-de2fa2
  id_note: >-
    The role contract's RT-* form is not a governed identifier type in
    CLAUDE.md "Conventions", so no token was minted from tools/allocate_id.py.
    The id is derived from this task id and the authoring date, which cannot
    collide with a governed namespace.
  task_id: TASK-20260822-de2fa2
  goal_id: GOAL-ECRANK-002
  batch_id: BATCH-e0caa5
  role: red-team
  snapshot_read: 2938068a3000c9b06ae5b972be86647c803f94a3
  branch: claude/degree-regularity-polynomial-systems-pssesi

  claim_under_review: >-
    As the review plan states it: (a) the maximum rank over Q reached by a
    Mestre-style construction within budget, certified by exhibited
    independent points; (b) the k = 3 and k = 4 twist-family optima on the
    augmented pool; (c) the base rank that reaching 31 at k = 3 would
    require, derived from measured coset structure. This report owns the two
    joints assigned to TASK-20260822-de2fa2 and attacks (c) directly; (a) and
    the maximality of (b) are the sibling reviewer's joints and are not
    adjudicated here.

  # ===================================================================
  # ASSIGNED JOINTS
  # ===================================================================
  joint_verdicts:

  - joint: >-
      The claimed base rank needed for 31 at k = 3 is MEASURED, not assumed:
      specifically that the non-maximal-class contribution is separable from
      the maximal class.
    verdict: breaks
    verdict_scope: >-
      BREAKS AS A PROPOSITION ABOUT THE BATCH'S CLAIM, NOT AS AN ACCUSATION
      AGAINST THE PRODUCER. TASK-20260822-8df232 states the separability
      failure itself (O4, conclusion) and labels every "required" figure
      MODELED. The joint breaks because the quantity the review plan calls
      MEASURED does not exist in the committed bytes: what exists is four
      mutually inconsistent in-sample extrapolations resting on a relation
      the data refuses.
    breaking_artifact_found: true
    breaking_artifact: >-
      Two cosets with the same maximum single-class rank and materially
      different totals exist in quantity. Recomputed by this review directly
      from runs/RUN-8df232-005-all/k3_coset_rows.json: in deg32_multiplicity
      at max = 3 the total takes 10, 12, 14, 16, 18; at max = 2 it takes 8,
      10, 12, 14, 16. In deg16_multiplicity at max = 4 it takes 14, 16, 18,
      20. Across all five parent certificates, max = 3 admits totals 10
      through 20. The additive form total = max + constant is false on the
      measured data, so the extrapolation behind the claimed ceiling is
      invalid and the four "required" numbers must not be quoted as one.
    second_breaking_artifact: >-
      "Fitted on the same cosets it is then validated on" understates it:
      there is NO held-out set anywhere in the record. Every fit in O4 and O5
      is in-sample over the same 12431 rows, and no fit is evaluated on any
      object it did not see.
    supporting_artifacts:
    - coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/tasks/TASK-20260822-8df232/runs/RUN-8df232-005-all/k3_coset_rows.json
    - coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/tasks/TASK-20260822-8df232/coset_structure.json
    - coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/tasks/TASK-20260822-8df232/report.md

  - joint: >-
      Any degree-8 result is reported as WEAKER IN KIND than the held
      degree-32 exact certificate, not as a strict improvement.
    verdict: holds
    verdict_scope: >-
      HOLDS ON THE COMMITTED BYTES OF THIS BATCH. The declared breaking
      artifact -- a deliverable claiming improvement on degree while hiding
      the certificate downgrade -- is ABSENT. No degree-8 result at 31 was
      produced; 8df232 disclaims interpretation explicitly; a7a9e8 states
      plainly that its claims rest on exhibited points plus height
      regulators and that RUN-008 obtained no upper bound. The guardrail was
      not violated. It is, however, NOT MAINTAINED: the certificate-kind axis
      is missing from every table in this batch, which is how the violation
      would enter the next record rather than this one. See
      objection O-06 for the exact numbers and the required control.
    breaking_artifact_found: false
    supporting_artifacts:
    - experiments/EXP-ECRANK-e1e30e/certificates/verification_summary.json
    - experiments/EXP-ECRANK-e1e30e/source/twist_family.py
    - coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/tasks/TASK-20260822-8df232/report.md

  joints_not_owned:
    ids: [TASK-20260822-0de988]
    joints:
    - every rank attributed to a Mestre-constructed curve is a certified lower bound from exhibited points
    - the reported k = 3 optimum is the true maximum over the enumerated space
    - the proves_too_much control and the blind re-derivation of the k = 3 optimum
    statement: >-
      NOT ATTACKED HERE AND NOT ASSUMED HERE. Where a finding below would be
      affected by the sibling's verdict, the dependence is named in the
      finding. No sibling output was read.

  # ===================================================================
  # OBJECTIONS
  # ===================================================================
  objections:

  - id: O-01
    severity: high
    title: The measured coset relation is a control that cannot fail; it is invariant under randomising the data it claims to describe.
    target: coset_structure.json relations.relation_2_total_vs_max_single_class, and O4's per-source and pooled fits
    finding: >-
      Relation 2 (total = a * max_single_class + b) and relation 2' (total =
      max + mean(others)) carry the two "required max single class" figures,
      17.87 and 23.80. This review ran the null-object control the record
      does not contain: hold the k = 3 sub-coset enumeration fixed and
      randomly PERMUTE the certified rank values across the classes of each
      parent certificate, destroying every association between a class d and
      its rank while preserving the multiset. Over 200 shuffles the fit does
      not move. Pooled over all 12431 rows, observed R^2 = 0.6682 against a
      null median of 0.6691 (range 0.6679-0.6703) and observed required max
      17.874 against a null median of 17.863 (17.849-17.878). On the
      n_classes rows the shuffled statistic is IDENTICAL in 200 of 200 trials
      (R^2 = 0.9402, required 22.722). On the sum_mult rows the observed R^2
      = 0.3146 is slightly WORSE than the null median 0.3280 and lies inside
      the null band 0.3078-0.3458.
    why_it_cannot_fail: >-
      This is structural, not luck. The k = 3 sub-cosets of a k-dimensional
      coset form a 2-design: this review verified that every pair of classes
      lies in a constant number of sub-cosets (7 for deg16, 35 for both
      deg32 certificates, 155 for deg64). A least-squares fit is a
      second-moment statistic, so on a 2-design it depends on the class
      values only through their multiset and their pairwise co-occurrence,
      which the design holds constant. Relation 2 therefore CANNOT detect
      coset structure even in principle. It is a restatement of the histogram
      of per-class ranks.
    consequence: >-
      The two figures 17.87 and 23.80 contain no information about cosets.
      Any record that reports them as "measured coset structure" is reporting
      a marginal distribution under another name. docs/inventor-protocol.md
      section 3: a quantity that stays flat when the parameter that should
      destroy it is varied is an artifact tell.
    verified_by: this review, recomputation from the committed rows file; seed 20260904, 200 shuffles per pool

  - id: O-02
    severity: high
    title: The record warns against the pooled row set and then computes its headline figures from it.
    target: coset_structure.json relations.relation_2_*, report.md Limitation 5 and O4 note
    finding: >-
      The producer's Limitation 5 states that 11780 of the 12431 rows come
      from n_classes certificates "whose classes carry one point by
      construction" and that "the single 'all' row is the one to distrust".
      O5's relations 2 and 2' are computed on exactly that "all" row. This
      review recomputed both variants: restricted to the 651 sum_mult rows,
      required max single class is 10.32 (linear) and 20.59 (additive),
      against the reported 17.87 and 23.80. The choice of pool moves the
      headline by 7.6 units -- larger than the 6-unit disagreement between
      relations 2 and 2' that the report itself flags as the honest width.
    degeneracy_named: >-
      The n_classes rows are degenerate by construction in the strongest
      sense. Their underlying data is 32 class values all equal to 1
      (deg32_eigenspace, so total = 8 and max = 1 on all 620 of its rows,
      zero variance) and 64 class values of which 62 equal 1 and 2 equal 3
      (deg64_eigenspace). 9145 of the 12431 rows are the single repeated
      point (max, total) = (1, 8), and 11780 of them occupy only three
      distinct points. That is not a regression; it is a weighted
      interpolation between two points, and the objects were built to make it
      so, because the n_classes objective maximises the number of classes
      carrying a point.
    verified_by: this review, recomputation from the committed rows file

  - id: O-03
    severity: high
    title: Pseudo-replication -- 12431 "measurements" are 152 numbers on four base curves.
    target: coset_structure.json coset_decomposition, all R^2 values in O4 and O5
    finding: >-
      The 12431 rows are combinatorial re-uses of 152 per-class certified
      values (8 + 16 + 32 + 32 + 64), enumerated over five parent cosets that
      sit on FOUR distinct base curves: the deg16_multiplicity curve
      A = -22275, B = -232733250 is the quadratic twist by 5 of the
      deg32_multiplicity curve A = -891, B = -1861866 (-22275 = -891*25,
      -232733250 = -1861866*125), which the producer records as the same
      a-invariants twice with coset representatives 5 and 1 (Limitation 4).
      Every R^2 and every confidence one might read into n = 12431 is
      inflated by roughly two orders of magnitude in effective sample size.
    consequence: >-
      Limitation 4 correctly says the rows "are not a sample of the pool". It
      does not say the rows are not independent OF EACH OTHER, which is the
      part that invalidates the fit statistics rather than merely their
      external validity.

  - id: O-04
    severity: high
    title: The frontier extrapolation 1b is an order-statistic artifact, and its optimistic end is the least defensible number in the batch.
    target: coset_structure.json relations.relation_1b_frontier, base_rank_required_for_31 = 7.857
    finding: >-
      Relation 1b fits max-observed k3_mult against base rank on four points
      whose sample sizes are n = 1, 1, 497, 3. A maximum is an increasing
      function of n, so the r0 = 3 point (max of 497 draws = 20) is not
      comparable with the r0 = 4 point (max of 3 draws = 19) or with the
      single curves at r0 = 1 and 2. This review bootstrapped the r0 = 3
      group (20000 resamples): the expected max of 3 draws is 16.91, not 20.
      Refitting at a common n = 3 gives required base rank 8.83 rather than
      7.86; refitting on group MEANS gives 11.83. A jackknife of the four
      points gives required base rank 6.00, 7.56, 8.11, 9.06 depending on
      which single point is dropped -- a 24 percent swing from the k3_mult of
      ONE curve.
    consequence: >-
      The report calls the span "base rank ~8 to ~12 ... the honest width of
      what was measured". It is not a width of the phenomenon: it is the gap
      between an uncorrected order statistic and a mean. Once the sample-size
      confound is removed, every defensible variant lands in 9-12, and the
      encouraging end of the published range is the artifact. A single number
      standing in for that spread would be an overclaim in the direction the
      campaign wants.
    verified_by: this review, bootstrap and jackknife on the committed subspace_scan.json and pool.json

  - id: O-05
    severity: medium
    title: Relation 1's slope must be read against a definitional floor of 1, not against 0.
    target: coset_structure.json relations.relation_1_k3_total_vs_base_rank
    finding: >-
      For any coset containing the trivial class, the k = 3 total includes
      the base curve's own rank as one of its eight summands, so
      total >= base_rank identically. A regression of total on base rank
      therefore has a built-in slope-1 component whenever the optimising
      coset contains d = 1, which it does for the fixture certificate
      (twist_coset_representative 1). The fitted 1.750 means the other seven
      classes add about 0.75 per unit of base rank; stated as "1.750" against
      an implicit null of 0 it reads as three-quarters more signal than is
      there. With R^2 = 0.023 and 497 of 502 curves at a single predictor
      value, the fit is in any case describing a single point cloud.

  - id: O-06
    severity: high
    title: The certificate-kind axis is absent from every rank total this batch reports.
    target: 8df232 report.md O1/O2/O4/O5 tables; the campaign's degree ladder
    finding: >-
      The committed pipeline separates two kinds of bound. twist_family.py's
      normative docstring says n_classes "bounds rank ... with a purely
      algebraic (Galois-eigenspace) certificate: no numerics", while sum_mult
      counts "points sharing a class [that] need a height-regulator argument
      (see regulator_check.py)". verification_summary.json carries both
      columns: for the degree-8 control, bound_eigenspace_exact = 8 and
      bound_with_multiplicity = 20. The 8df232 report reproduces the sum_mult
      totals (20, 32, 52) in one table with a single "C1-C6 all pass" column
      and never carries the split. Its C1-C6 list contains NO within-class
      independence check -- C3 certifies each point non-torsion by Mazur
      individually, which does not make two points on the same twist
      independent. So the exact part is re-verified here and the numerical
      part is inherited from PARI and from a regulator computed elsewhere,
      in the same bolded number.
    quantification_by_this_review: >-
      k3_cls = 8 for ALL 502 curves of the committed scan: the eigenspace
      ceiling at k = 3 is saturated everywhere in the pool. Hence 8 of the
      fixture's 20 are exact and 12 are regulator-dependent, and a
      hypothetical degree-8 total of 31 or 32 would be 8 exact plus 23 or 24
      regulator-dependent -- against a held degree-32 result that is 32 exact
      with no floating point anywhere in its proof (analysis.md). Any future
      framing of "degree 8 beats degree 32" would be trading a 100-percent
      exact certificate for a 25-percent exact one. H-ECRANK-f2a2f7's
      method_ceiling says exactly this; the batch's tables do not carry it.
    also: >-
      The certified convention is min(r_low, #points) with r_low from PARI,
      not re-derived. The producer discloses this in O2 for level B; the O1
      table's column header "recomputed sum of min(r_low, #pts)" invites the
      opposite reading, since what was recomputed is the sum, not r_low.

  - id: O-07
    severity: high
    title: The high-rank pool is fit for its own claim and probably unfit for the measurement the campaign needs next, and nobody has costed that.
    target: highrank_pool.json; a7a9e8 report.md sections 1, 3, 5
    finding: >-
      The certified rank >= 11 curves have median max |a_i| about 7.5e24
      (rank 13: 3.4e23 and 1.3e28). a7a9e8's own RUN-008 reports 31 of 31
      ellrank calls hitting a 25 s alarm on exactly these curves, correctly
      classified as an infrastructure outcome that decides nothing. But the
      campaign's next step is the twist-family measurement, which needs a
      descent or a point search per class on E^(d) with coefficients
      A d^2, B d^3 -- for d up to the product of the seven support classes
      this multiplies |a6| by roughly 1e13. If 2-descent is already
      infeasible on the base curve, it is more infeasible on 7 or 127 twists
      of it. The blockage is therefore NOT only "PARI absent in 8df232's
      container"; there is a second, mathematical-cost blockage that no
      record in this batch prices.
    consequence: >-
      "Required base rank ~9-12, and the construction reached 13" reads as
      the campaign being one step from its target. It is not, unless someone
      shows the twist ranks of a 1e25-coefficient curve can be certified at
      all. The relevant quantity is not base rank alone; it is base rank at a
      conductor small enough for the measurement instrument.
    verified_by: this review, coefficient statistics over the committed pool; timeout counts read from the producer's own report

  - id: O-08
    severity: medium
    title: The pool's declared selection rule does not reproduce the pool, and 37 curves are counted twice at two different ranks.
    target: highrank_pool.json selection_rule, n_curves, rank_histogram_in_pool
    finding: >-
      highrank_pool.json declares "ALL curves of certified rank >= 11 ...
      plus the first 150 in search order at rank 10 and 9 (m10) and rank 7
      (m8 control)" -- rank 8 is absent from the rule, and the file contains
      150 rank-8 curves. The report's section 4 gives a different rule
      (ranks 10, 9, 8 and 7). Neither produces the delivered histogram, which
      has 300 at rank 9. Only a per-source-run reading does, and this review
      confirmed it: 150 at rank 9 from RUN-002 (m10 alone) and 150 at rank 9
      from RUN-004 (m10+extra). Consequently 1206 records are 1169 distinct
      minimal models: 37 curves appear twice, once at rank 9 un-augmented and
      once at rank 10 or 11 augmented. Same curve, two different certified
      ranks, both in the pool.
    consequence: >-
      Not a rank error -- the weaker record is true of the same curve -- but
      any downstream per-curve statistic on this pool double counts 37
      objects and any "1206 curves" phrasing overstates the distinct supply
      by 3 percent. The selection rule is exactly the field a reviewer must
      be able to replay to judge selection bias, and it cannot be replayed as
      written.
    cheap_fix: >-
      A superseding record stating the per-source-run quotas and a
      distinct_minimal_models count. Not an edit to the committed file.

  - id: O-09
    severity: medium
    title: Selection-on-the-outcome in the pool's construction route, and what it biases.
    target: a7a9e8 construction sections 2.3 and 4, highrank_pool.json
    finding: >-
      Ranks above the function-theoretic ceilings (7 for M8, 9 for M10) come
      entirely from the extra-point scan over u = n/d with |n| <= 400,
      d <= 12. A curve enters the interesting part of the pool by having
      several EXTRA RATIONAL POINTS OF SMALL HEIGHT in a fixed box. That is
      selection on small canonical height, not only on rank. Any statistic
      later taken on this pool that touches heights, regulators, point
      density, or Mestre-Nagao style sums is conditioned on that selection
      and is not a property of Mestre-constructed curves in general. The
      report's own numbers show the conditioning is strong: 84.6 percent of
      augmented curves stay at 9 and 71 percent of curves with extra points
      gain no rank at all.
    what_is_not_biased: >-
      The headline "maximum certified rank reached = 13" is an EXISTENCE
      claim about exhibited witnesses and is not damaged by selection; a
      search may look wherever it likes. This objection is about every
      DISTRIBUTIONAL use of the pool that comes after.

  - id: O-10
    severity: medium
    title: The fixture's level split is honest, and the batch's derived numbers nevertheless rely on the level that was not established.
    target: 8df232 report.md O2 levels A/B/C, and O5
    finding: >-
      Level A is a max over a column of a committed intermediate artifact --
      it verifies nothing about the underlying descents and the producer says
      so. Level B verifies the 20 exhibited points but not r_low and not
      within-class independence (O-06). Level C, the only level that makes 20
      a MAXIMUM, is OPEN AND UNATTEMPTED. Yet maximality is load-bearing
      downstream: relation 1b is a frontier fit built from the MAX k3_mult in
      each base-rank group; the review plan's claim (b) speaks of "the k = 3
      optimum"; and GOAL-ECRANK-002's completion criterion C2 asks for "the
      resulting k = 3 optimum". Every one of those uses the word the record
      cannot support at level C.
    correct_reading: >-
      20 is the maximum over the committed scan table as computed by the
      committed pipeline. That is a statement about an artifact, not a proof
      of optimality over the pool, and it should be worded that way wherever
      it is quoted.

  - id: O-11
    severity: medium
    title: A base rank in the committed input data is wrong, and the error was copied verbatim into this batch.
    target: experiments/EXP-ECRANK-e1e30e/source/scan_pool.py seed table; TASK-20260822-8df232/src/coset_structure.py SEED_CURVES
    finding: >-
      scan_pool.py declares seeds = [... {'ai':[1,1,1,-2,0],'rank':3}], and
      coset_structure.py copies the table verbatim by its own comment. The
      curve [1,1,1,-2,0] is LMFDB 79.a1: conductor 79, discriminant 79,
      Mordell-Weil RANK 1, trivial torsion, generator (0,0). This review
      corroborated the identification independently by computing the
      discriminant from the a-invariants (b2 = 5, b4 = -3, b6 = 1, b8 = -1,
      Delta = 79), which is prime, so the model is minimal and the conductor
      is 79; and a curve of conductor 79 cannot have rank >= 2, since the
      minimal conductors for ranks 2 and 3 are the classical 389 and 5077.
    impact_quantified_by_this_review: >-
      base_rank_distribution_in_pool should read {1: 2, 2: 1, 3: 496, 4: 3},
      not the recorded {1: 1, 2: 1, 3: 497, 4: 3}. Relation 1 becomes
      a = 1.7907, b = 10.3721, R^2 = 0.0367, required base rank 11.52 in
      place of 11.72. Relation 1b is UNCHANGED, because both true rank-1
      curves have k3_mult = 12. The defect is therefore numerically minor for
      this batch and material for the record's integrity and for any later
      pool with wider base-rank coverage.
    producer_is_not_at_fault: >-
      This review reproduced relations 1 and 1b to the last recorded digit
      from the producer's declared inputs (a = 1.7500, b = 10.4871,
      R^2 = 0.0234, required 11.722; frontier a = 2.8000, b = 9.0000,
      R^2 = 0.7840, required 7.857). The producer's arithmetic is faithful.
      The defect is upstream, in a committed experiment source.
    handling: >-
      Committed records are immutable. This is a correction record's job, not
      an edit, and the correction belongs to EXP-ECRANK-e1e30e's owner.

  - id: O-12
    severity: medium
    title: The batch's own dataset cannot represent the value it extrapolates to, and the reason is structural and unreported.
    target: coset_structure.json coset_decomposition, relations, and O5's "total = 31 requires mean 3.875 per class"
    finding: >-
      Every one of the 12431 measured k = 3 totals is EVEN (observed odd
      totals: 0). The mechanism is exact: on each of the five parent cosets
      the PARITY of the per-class certified rank is an affine-linear function
      of the class's F_2 coordinate vector over the support. This review
      solved for it by brute force and found exactly 2^(7-k) solutions per
      certificate (16, 8, 4, 4, 2 for k = 3, 4, 5, 5, 6), i.e. a UNIQUE
      functional on each coset's own direction space, which is precisely what
      an affine parity law predicts and what coincidence does not. Summing an
      affine functional over an 8-point affine subspace is always even, hence
      the totals. Against the label-shuffle null the signal is strong where
      it can be: on the two mixed-parity certificates the null produces about
      half odd totals (14.6 of 30 for deg16, 310.5 of 620 for deg32_mult)
      and the observed count is 0 in both.
    consequence_1: >-
      The response variable of every fit in O4 and O5 takes only even values
      in {8, 10, ..., 20}, and the extrapolation target 31 is odd. O5's
      arithmetic remark "total = 31 requires mean certified rank 3.875 per
      class" solves for a value that no object in the fitted dataset can
      take. Under the observed structure the reachable neighbours are 30 and
      32, and H-ECRANK-f2a2f7's ">= 31" is satisfied only at 32, i.e. mean
      exactly 4 per class.
    consequence_2_and_the_limit_of_this_finding: >-
      THIS IS NOT AN IMPOSSIBILITY RESULT AND MUST NOT BE READ AS ONE. The
      committed 502-row scan contains 78 curves with ODD k3_mult (values 13,
      15, 17, 19 occur). So parity is not a universal obstruction; it is a
      property of the five certificate cosets. That is the point: the dataset
      carrying every fit is structurally unlike the pool the fits are used to
      reason about, which upgrades the producer's Limitation 4 from a caveat
      to a mechanism.
    candidate_explanation_not_established: >-
      Affine parity across a twist coset is what the parity conjecture plus
      the standard quadratic-twist root-number behaviour would predict. This
      review did not verify root numbers -- no PARI in this session -- and
      records the reading as a hypothesis for the ranking, never as evidence.

  - id: O-13
    severity: medium
    title: A claim in the review plan corresponds to no commissioned task, and its absence must not be recorded as a measurement.
    target: review_plan.claim_under_review (b); dispatch_queue.json; 8df232 report.md O3
    finding: >-
      The review plan puts "the k = 3 and k = 4 twist-family optima on the
      AUGMENTED pool" under review. The dispatch queue asked 8df232 to work
      "On the committed GOAL-ECRANK-001 pool", and 8df232 used exactly that
      -- 497 pool curves plus 5 seeds, committed support [-1,2,3,5,7,11,13].
      No task in BATCH-e0caa5 was commissioned to scan the a7a9e8 curves, and
      none did. The augmented-pool optimum is unproduced BY BATCH DESIGN, not
      by producer failure, and separately it is blocked by the missing PARI
      and by O-07.
    the_rule_3_risk_stated_precisely: >-
      Both producers handle the missing tool correctly in their own records
      (8df232's O3, Limitation 1 and deviation 2; a7a9e8's section 3 on
      RUN-008). The live risk is downstream and directional: H-ECRANK-f2a2f7
      P2 predicts the k = 3 optimum RISES above 20 once a higher-rank base
      curve enters the pool, and the only k = 3 number in this batch, 20, is
      from the pre-Mestre pool. If a decision record cites 20 as the post-
      Mestre optimum, or reads "P3 holds, the optimum stayed below 31", the
      absent tool will have been converted into negative mathematical
      evidence -- the exact failure AGENTS.md rule 3 forbids, in the
      direction that is easy to miss because it agrees with the prior.
    required_wording: >-
      P2 is UNTESTED BY THIS BATCH. Not screened, not negative, not weakly
      supported. Untested.

  - id: O-14
    severity: low
    title: A cheap, currently-runnable answer that the batch left empty -- the k = 4 nearby-object control.
    target: H-ECRANK-f2a2f7 proof_search_map.nearby_object_control; 8df232 deliverable 2
    finding: >-
      The hypothesis declares k = 4 as its nearby-object control and the
      handoff asked for a k = 4 optimum. No k = 4 optimum is stated anywhere
      in the batch's deliverables (extended_support.k4_optimum is null, and
      correctly so, since extended support needs new descents). But the
      COMMITTED-support k = 4 optimum needs no PARI at all: it is a max over
      a column of the same subspace_scan.json the producer already read for
      level A. This review computed it: k4_mult max = 32 on [1,-1,1,-1,-40],
      which agrees with the independently recomputed deg16_multiplicity
      certificate total of 32 in O1. Also computed, same source: k5_mult max
      = 52, k6_mult max = 88, and k3_cls = 8 for every curve.
    a_loose_end_worth_a_look: >-
      k6_mult max = 88 sits in the committed scan while the campaign's degree
      ladder tops out at 64 for degree 64. Different objectives (the ladder's
      degree-64 row is the exact n_classes bound), but nobody has reconciled
      them and no certificate was ever built for the 88. Irrelevant to C1,
      relevant to the goal's framing, and cheap.
    classification: >-
      This is a level-A re-derivation from a committed intermediate artifact,
      with exactly the independence level the producer assigns to level A. It
      is not an independent recomputation of any descent.

  - id: O-15
    severity: medium
    title: The archive's own digest binding rests on one actor asserting agreement with itself; this review replaced it with a computation.
    target: BATCH-e0caa5/archives/TASK-20260822-e7c486/receipt.yaml
    finding: >-
      Every value in the receipt's path_sha256 is null, for a stated and
      legitimate capability reason. Its corroboration block then cites the
      GOAL-ECQ-001 receipt (BATCH-7e06d3/archives/TASK-20260822-66bacf) as
      committed confirmation of two of the six digests. Both digest sets were
      supplied by the same orchestrating session, so agreement demonstrates
      that one actor is self-consistent, not that two independent parties
      hashed the bytes. The receipt's own hedge ("NOT a verification of the
      current working tree") is correct but does not name the common author.
    resolution_by_this_review: >-
      Moot now, and moot by computation rather than by argument. This review
      recomputed all six declared producer paths with sha256sum directly from
      the committed blobs, at BOTH the receipt's commit_to_read
      (c7316eef052df105be2f822fb8ccd8615448d114) and the archive commit named
      on the dispatch card (2938068a3000c9b06ae5b972be86647c803f94a3). All
      six match the supplied 16-hex prefixes and byte sizes, and are
      byte-identical at the two commits. The content binding HOLDS. The
      seventh declared path is the receipt itself, which by its own text
      carries no digest, so six is the number a reader can verify.
    digests_recomputed:
      a7a9e8/highrank_pool.json: 3d8620ea993436880fc4a70d4028cc92c087481fd6c2c46b391f2d667f5e1a24
      a7a9e8/report.md: 00cd7dd54b07e081ca248beb922bc5ba6e816b621d95ddd4cc39128d066be440
      a7a9e8/src/construct_highrank.py: 52abb370557b397c8744b1426be8e009695775bdd27c846fd3ccb8966ea6fc27
      8df232/coset_structure.json: a6eda120b352ce3d720e00a26e566a9eca3349915f11fb1f8f5819d87b61cd85
      8df232/report.md: 168e84abe3abf1783bc1ddf02f7cab901d094003a83438bbe0e970b01d955dab
      8df232/src/coset_structure.py: 6a08546ce897d1f578c1e26795d2f9fb0866468db9b86dcc7d26de9def3593b1
    double_binding_check: >-
      CLEAN. highrank_pool.json and report.md are bound by both this batch's
      receipt and the completed GOAL-ECQ-001 archive; the digests agree with
      this review's recomputation, and the ECQ receipt explicitly records
      that the paths "are not restated as this batch's own production" and
      that GOAL-ECRANK-002 must be named wherever they are used. Nothing read
      here cites the two archives as two independent bindings, except the
      corroboration block above, which is a claim about digest provenance
      rather than about evidence.

  - id: O-16
    severity: medium
    title: The attribution dispute, adjudicated.
    target: a7a9e8 report.md anomaly A1; CORRECTION-anomaly-A1-attribution.md
    ruling: >-
      THE CORRECTION IS RIGHT AND THE PRODUCER'S A1 ATTRIBUTION IS WRONG. The
      producer attributed the concurrent writes into its run directory to
      "the archiving task TASK-20260822-e7c486". Three checkable facts, none
      of which the producer could see from inside its run: (i) the coordinator
      subagent that authors e7c486 has tool surface Read, Grep, Glob, Write,
      Edit, SendMessage -- verified in .claude/agents/coordinator.md -- and
      therefore holds no command-execution tool; (ii) producing
      raw-result.json.gz requires running a compressor and adding a
      .git/info/exclude entry requires a shell, neither of which that tool
      surface permits; (iii) e7c486's own receipt states it wrote exactly one
      file, its own receipt, and issued no git command. The writes were the
      orchestrating session's, exactly as the CORRECTION says. The producer
      had no way to know and is not at fault for the attribution.
    what_it_does_not_touch: >-
      Nothing in A1 touches any rank claim. The interference was additive --
      a compressed copy and a note -- never a modification of a result file.
    the_finding_that_outlives_the_ruling: >-
      The same fault occurred against BOTH producers in this one batch: the
      orchestrator wrote into a7a9e8's live write_scope, and committed
      8df232's in-flight files at ba9bd1bcd while that producer was still
      running (8df232 deviation 8; the e7c486 receipt records it too). Two
      producers, one batch, same fault. That is a pattern, not an incident,
      and it costs review budget every time: both producers spent report
      space reasoning about files they did not create. Recording it is this
      review's job; the standing process change is the Coordinator's.

  - id: O-17
    severity: low
    title: The immutability deviation is real and its recovery path is now verified, not merely declared.
    target: DEVIATION-immutability-trim.md
    finding: >-
      In-place overwrite of completed run records and of seven manifests is
      the operation AGENTS.md rule 2 forbids, and the deviation record says
      so plainly. This review verified the recovery claims it could verify:
      RUN-004's untrimmed raw-result.json is reachable at 78584ab8 at exactly
      the declared 35,039,973 bytes (277,063 bytes at the snapshot), and
      RUN-002's raw-result.json.gz at the snapshot decompresses to
      112,301,654 bytes with sha256
      ff0935a0c68c58da7da3fdb861f36d80e33f72365fb2ecb57d8196b0af5ccb47 --
      byte-identical to the declared original, computed here rather than
      taken from the record. Nothing was lost.
    residual: >-
      The deviation's warning that a producer which rewrites its own
      completed records to make them smaller is doing the same category of
      thing as one that rewrites them to make them better is correct and
      should stand in the ledger. The recovery being verified does not
      retire the rule; it retires the data-loss worry.

  # ===================================================================
  # REQUIRED CONTROLS
  # ===================================================================
  required_controls:

  - id: C-01
    name: Label-shuffle null on every coset relation, before any of them is quoted again.
    what: >-
      Permute the per-class certified values within each parent certificate,
      keeping the sub-coset enumeration fixed, and recompute the fit and the
      derived "required" figure. Report observed against null band.
    cost: seconds; Python standard library; no PARI; no new descent
    status: RUN BY THIS REVIEW. It fires (O-01). Any re-run should reproduce it.
    discriminating_power: >-
      Total. A relation that survives label permutation is a statement about
      a histogram. This control is the difference between "we measured the
      coset structure" and "we measured how many classes have rank 1".

  - id: C-02
    name: Decide, explicitly, whether an external witness satisfies C1 -- because one now appears to exist over Q.
    what: >-
      GOAL-ECRANK-002's C1 reads "a committed certificate of rank >= 31 over
      a number field of degree <= 8, accepted with zero errors by
      source/verify_certificate.py (exact) and with no singular regulator by
      regulator_check.py". Degree 1 satisfies "degree <= 8". Two external
      sources consulted by this review record a curve over Q of rank >= 31:
      Dujella's rank-history table lists rank 30 and rank 31, both 2026,
      Alpoge-Howell; the ICARM leaderboard entry for curve #302 records
      rank >= 31, credited to Claude, Levent Alpoge and Ava Howell,
      submitted 2026-08-23 20:02:58 UTC. The committed statement in
      EXP-ECRANK-e1e30e/analysis.md that "Rank >= 31 over Q is open" was true
      when written and is out of date as of 2026-08-23, one day after this
      batch's task ids are dated. The campaign has ALREADY accepted the
      external-witness pattern: its degree-2 ladder row is "external 30,
      exact +1".
    the_action: >-
      Fetch that curve's exhibited points, run the committed exact verifier
      and regulator check on it as a k = 0 configuration (V trivial, degree
      1), and record the outcome. Then either close C1 on it, or restate C1
      as "by this construction" and say so in the ledger. Do NOT let the
      question stay implicit while more budget goes to Mestre searches aimed
      at base rank 9-12.
    cost: minutes of verification once the points are in hand; no new search
    caveats_stated_rather_than_smoothed: >-
      This review did NOT verify the 31 points and asserts no rank. The
      leaderboard page also mentions BSD+GRH in connection with rank 31,
      which plausibly concerns the upper bound; a lower bound from exhibited
      independent points should be unconditional, and checking that is
      exactly the action above. An external record is a pointer, not
      evidence, until this program's own verifier accepts the bytes.
    if_it_holds: >-
      The degree ladder's answer to "how small a field" becomes 1 by external
      work, the degree-2 row becomes >= 32, and the remaining scientific
      content of GOAL-ECRANK-002 is the narrower question of what THIS
      construction reaches. That is a legitimate question and should be
      stated as the narrower one rather than inherited silently.

  - id: C-03
    name: Break the five-certificate monoculture before any coset relation is believed.
    what: >-
      Build per-class certified vectors for a RANDOM sample of pool curves --
      not the five that were selected as certificate carriers -- and refit.
      One k = 3 coset on each of about 20 randomly drawn pool curves is about
      160 ellrank calls at the committed alarm, versus 502 x 128 for the full
      job.
    cost: needs PARI; roughly 160 descents on small-conductor curves; hours at most
    discriminating_power: >-
      This is the only control that turns O4 from a statement about five
      selected objects into a statement about the pool. Until it is run, no
      number in O4 or O5 is about the pool, and the record should not use
      pool-scoped words for it.

  - id: C-04
    name: Carry the certificate-kind split in every rank total the campaign reports.
    what: >-
      Every total gets two numbers: bound_eigenspace_exact (classes carrying
      at least one point; exact, no numerics) and bound_with_multiplicity
      (regulator-dependent). verification_summary.json already computes both.
      A degree comparison without this column is not a comparison.
    cost: zero; the data exists in committed artifacts
    discriminating_power: >-
      It is the guardrail joint 4 exists to protect, and it is currently
      unmaintained rather than violated.

  - id: C-05
    name: Root numbers instead of descents, as the cheap half of the blocked measurement.
    what: >-
      For a base curve and the 128 classes of the committed support, compute
      the twist root numbers rather than the twist ranks. Under the parity
      conjecture that gives, for free, which cosets can have all eight
      classes of odd rank -- hence all eight carrying a point, which is the
      exact n_classes bound -- and it would test the affine-parity structure
      this review found (O-12) on curves outside the five certificate
      carriers.
    cost: >-
      Needs PARI but NO descent. HONEST CAVEAT: a root number needs the
      conductor, hence a factorisation of the discriminant. For the
      small-conductor pool curves this is trivial. For the a7a9e8 curves with
      |a_i| about 1e25 the factorisation may itself be the blocker, and this
      review does not promise otherwise.

  - id: C-06
    name: The k = 4 level-A control, and the frontier's sample-size correction.
    what: >-
      Record the committed-support k = 4 optimum (32; see O-14) as the
      hypothesis's declared nearby-object control, and refit relation 1b at a
      common sample size with the jackknife reported alongside (O-04).
    cost: seconds; no PARI
    status: RUN BY THIS REVIEW for both parts; results in O-14 and O-04.

  # ===================================================================
  counterexample_or_mutation: >-
    The cheapest single mutation that exposes the batch's central inference:
    replace the certified rank vector of each parent certificate by a random
    permutation of itself and re-run coset_structure.py's relation block. If
    the reported "required max single class" moves by less than a unit -- and
    it moves by 0.01 on the pooled rows, and by nothing at all on the
    n_classes rows across 200 trials -- then the relation is a function of
    the histogram and the phrase "measured coset structure" is not available
    for it. The mutation costs seconds and needs no PARI, which is why its
    absence from the record is the finding rather than its result.

  # ===================================================================
  baseline_comparison:
    applicability: >-
      Pollard-rho and BSGS are not the baselines here and forcing them would
      be a category error: nothing in this batch is a discrete-logarithm
      complexity claim, H-ECRANK-f2a2f7 records asymptotic_claim as
      explicitly null, and EXP-ECRANK-e1e30e's scale_relevance is `toy` with
      the claim-tier table declared inapplicable. Recorded so that a later
      reader does not read the omission as an oversight.
    closest_specialized_baseline_for_rank_over_Q: >-
      Elkies 28 (2006), Elkies-Klagsbrun 29 (2024), Alpoge-Howell 30 and 31
      (2026), per the rank-record history consulted for C-02 and per the
      committed analysis.md's own citation of the first three. a7a9e8's 13 is
      well below all of them and does not claim otherwise; the report makes
      no record claim anywhere.
    what_13_actually_measures: >-
      A 1218-second budget with an unwidened extra-point box, not a ceiling
      of Mestre-style construction. The implemented route's function-theoretic
      ceilings are 7 (M8) and 9 (M10) and were both hit exactly, which is a
      clean structural result; everything above 9 came from scanning
      |n| <= 400, d <= 12, which the report itself names as the untouched
      knob. Any later record that reads "the Mestre route tops out near 13"
      would be a fatigue report about a search, not a statement about the
      method -- the failure mode docs/inventor-protocol.md section 4 names.
      The producer's own section 5 wording ("where the method stopped paying
      off", stated as measurements) does not commit that error.
    against_the_batch_s_own_predecessor: >-
      Versus the twist route measured in GOAL-ECRANK-001 (no twist of rank
      >= 5 in 364756 candidates; 2 curves of rank 4 in 49692 enumerated),
      13 is a large move on the quantity H-ECRANK-f2a2f7 P1 named, subject to
      the sibling reviewer's joint on point-certification. This review takes
      no position on P1.
    the_comparison_that_is_missing: >-
      Nowhere in the batch is the delivered rank compared against the
      COST-RELEVANT axis for the campaign: rank at a conductor small enough
      for the twist measurement to run. On that axis the 502-curve
      small-coefficient pool (base rank <= 4, descent trivial) and the
      1206-record Mestre pool (base rank <= 13, descent 31/31 timeouts) are
      not on the same Pareto frontier at all, and neither dominates. See
      O-07.

  # ===================================================================
  heuristic_challenges:
  - id: HC-01
    challenge: >-
      No heuristic is stated in this batch, and H-ECRANK-f2a2f7 records
      heuristic_assumptions as an empty list with the justification that the
      deliverable is "either a finite exact certificate or a measured number,
      neither of which rests on a heuristic". That is right for the
      certificate and WRONG for the measured number. The separability
      assumption in assumptions[2] -- "the non-maximal-class contribution at
      k = 3 is approximately independent of the base curve" -- is a
      heuristic in everything but name: it is the modelling assumption that
      turns 20 into a prediction about 31. The hypothesis at least flags it
      as "THE ASSUMPTION MOST LIKELY TO BE WRONG", and the measurement duly
      found it false (joint 3). The record should say heuristic_assumptions
      is empty for the CERTIFICATE branch and non-empty for the CEILING
      branch, rather than empty overall.
  - id: HC-02
    challenge: >-
      A second unstated assumption carries all four extrapolations: that a
      linear relation fitted on base ranks 1-4 and on small-coefficient
      curves transfers to a Mestre curve of rank 13 with |a_i| about 1e25.
      That is not an extrapolation in one variable outside its fitted range;
      it is a covariate shift of roughly eighteen orders of magnitude in
      coefficient size, across which conductor, Selmer structure and
      root-number behaviour all change. The record labels the extrapolation
      MODELED, which is correct and insufficient: MODELED names the fit's
      uncertainty, not the change of object.
  - id: HC-03
    exemplar_profile_applicability: >-
      docs/target-result-profile.md's exemplar checks (numbered heuristics
      with a rigorous bound plus a classical distribution theorem, random-model
      transfer, o(1) overheads, per-attempt versus total expected cost,
      cited-reduction instantiation, affected-versus-safe scope) are NOT
      applicable to this batch and are recorded as inapplicable rather than
      silently skipped: there is no exponent claim, no asymptotic claim, no
      cited reduction, and no scheme scope. HC-02 is the one exemplar check
      that does transfer, in the form of random-model transfer: a curve
      selected for high rank and for many small-height points is not a
      uniformly drawn curve, and no statistic taken on the selected pool
      should be read as one.

  # ===================================================================
  cost_model_challenges:
  - id: CM-01
    challenge: >-
      The batch prices construction (9.4 ms/curve for M10, 20 ms/curve for
      augmentation) and prices nothing for the measurement that has to follow
      it. The end-to-end path to a degree-8 certificate is: construct base
      curve -> obtain certified ranks on 7 further twist classes -> establish
      within-class independence by height regulators -> verify exactly. Step
      2 has one committed implementation, PARI ellrank, and this batch's own
      evidence is 31 of 31 timeouts on the constructed curves. Cost of step 2
      on this pool: UNKNOWN AND UNPRICED. A campaign whose next step is
      unpriced is not one step from its target.
  - id: CM-02
    challenge: >-
      The augmentation scan is O(nmax * dmax) per curve and delivered ranks
      10-13 at 0.0058 percent yield for 13, with "each further step costing
      roughly a 10x larger sample than the last" by the producer's own
      measurement. Extrapolating that curve, base rank 15-16 costs about
      100-1000x the RUN-004 budget on the same knob. The report says the scan
      box is the obvious knob and was not widened; it does not say what
      widening buys, and the yield table is enough to estimate it. Naming the
      number would convert "the obvious knob" into a decision.
  - id: CM-03
    challenge: >-
      Memory and artifact cost is the one axis the batch DID hit: a 112 MB
      raw result that could not be pushed, a 35 MB one that was trimmed in
      place, and a rule-2 violation as the consequence. The run harness
      should cap raw-result size at declaration time and stream per-record
      output to a side file, so that the storage decision is made before the
      record is immutable rather than after.

  # ===================================================================
  reduction_and_scope_challenges:
  - id: RS-01
    challenge: >-
      "Rank >= 31 over a field of degree 8" and "rank >= 31 over Q" are
      different claims with a reduction between them in ONE direction only:
      a curve of rank r over Q gives rank >= r over any extension, so a
      degree-1 witness settles the degree-<=8 question and not conversely.
      C1 as written is satisfied by the weaker-to-obtain object. See C-02.
      This is not a defect in the batch; it is a scope statement the goal
      record should make explicit before it is closed either way.
  - id: RS-02
    challenge: >-
      Scope inflation check on the batch's own wording: none found. 8df232
      scopes every statement to "these 12431 cosets on these five base
      curves", declares toy scale, and refuses to interpret; a7a9e8 scopes
      its 13 to its parameter box and declares its infrastructure outcomes
      inert. Recorded plainly because premature closure and manufactured
      objections are symmetric failures: on scope discipline, both producers
      are above the program's average and should be told so.
  - id: RS-03
    challenge: >-
      GOAL-ECRANK-002's C2 requires "the base rank that would be needed for
      31 at k = 3, derived from the measured coset structure rather than
      asserted. A negative result closes this goal only if it carries that
      number." On the findings above, THE BATCH DOES NOT CARRY THAT NUMBER:
      it carries four in-sample extrapolations spanning 7.86 to 11.72 (base
      rank) and 10.32 to 23.80 (max single class, depending on which pool is
      used), of which the two coset-derived ones fail a null control and the
      optimistic frontier value is a sample-size artifact. Closing this goal
      on C2 today would be closure on an artifact. That is a statement about
      the number's support, NOT a claim that the campaign is dead: see
      narrowest_supported_statement and next_concrete_action.

  # ===================================================================
  proof_architecture_challenges:
  - id: PA-01
    attack: observation-fiber
    result: >-
      FIRES. The observable is (max single class, total) and the underlying
      object is the assignment of ranks to classes. Two preimages on
      different sides of the conclusion are abundant: same max, totals 10 and
      18 (deg32_multiplicity, max = 3). The missing separator is anything
      that distinguishes WHICH classes carry the rank -- and O-01 shows the
      chosen observable is provably blind to it, because the sub-coset
      enumeration is a 2-design.
  - id: PA-02
    attack: quantifier-order
    result: >-
      A soft version fires. H-ECRANK-f2a2f7's quantifier_order is stated
      correctly as EXISTS E, EXISTS V, FOR ALL 8 classes -- finite and
      exhibitable. But the fitted relations silently swap the order: they
      estimate a typical relation over cosets (FOR ALL cosets, on average)
      and then use it to predict the EXISTENCE of an extreme coset. A mean
      relation cannot bound a maximum. Relation 1b tries to fix this by
      fitting the frontier instead of the mean, and pays for it with 4 points
      of incomparable sample size (O-04).
  - id: PA-03
    attack: method-ceiling
    result: >-
      FIRES CLEANLY AND IS ALREADY IN THE HYPOTHESIS. At k = 3 the eigenspace
      argument certifies at most 8, and this review confirms k3_cls = 8 for
      all 502 pool curves, so the exact ceiling is not merely reachable, it
      is saturated everywhere. Everything from 9 to 31 is multiplicity, hence
      height regulators, hence a strictly weaker certificate. The largest
      claim the exact method can support at degree 8 is 8. Any degree-8
      headline must say which of the two ceilings it is under.
  - id: PA-04
    attack: nearby-object
    result: >-
      PARTLY UNRUN. k = 4 is the hypothesis's declared nearby object and no
      k = 4 optimum is stated in the deliverables, though the committed-support
      answer (32) costs seconds and is supplied in O-14. The informative
      version of the control -- k = 4 on the AUGMENTED pool -- is blocked by
      the same missing tool as everything else and is OPEN AND UNATTEMPTED.
  - id: PA-05
    attack: boundary-and-strictness
    result: >-
      The old method is genuinely embedded: the twist route's measured
      ceiling (rank 4) and the new route's 13 are on the same axis and the
      new one is strictly higher. The perturbation is strictly better ON BASE
      RANK. It is not shown to be better, or even feasible, on the axis that
      decides the campaign (O-07), and no record says which axis the
      improvement is on.
  - id: PA-06
    attack: compositional-invariant
    result: >-
      The strengthened invariant here is "certified total = sum over classes
      of certified per-class rank". Deleting the within-class independence
      component is exactly the C1-C6 gap in O-06: the remaining checks still
      certify the eigenspace bound 8, and the recursion to 20 fails at the
      first class carrying two points. The strong invariant does imply the
      target; the batch verifies the weak one and reports the strong one's
      number.

  # ===================================================================
  closure_attack:
    what_would_be_closed: >-
      The Coordinator prior recorded in the review plan expects P1, P2 and P3
      to hold, i.e. a C2 closure carrying "the base rank 31 would require".
    verdict: >-
      A C2 closure is NOT SUPPORTED TODAY, on the number's own terms (RS-03,
      O-01, O-04). Equally, nothing here supports a closure in the other
      direction: no obstruction has been measured, no impossibility shown,
      and the one structural regularity this review found (O-12) explicitly
      does not generalise past the five certificate cosets.
    the_fatigue_report_test: >-
      Applied to this batch and PASSED, in the sense that neither producer
      writes one. The risk sits one level up: "the Mestre construction
      reached 13 and the k = 3 optimum was 20, so degree 8 is out of reach"
      would be a count of what one budget did, dressed as a statement about
      the problem -- and it would additionally use an absent tool as evidence
      (O-13). If the goal is closed, the closure must name the obstruction it
      measured, and the honest answer is that it measured a search boundary
      at 1218 seconds and 24 seconds respectively.
    the_reversal: >-
      Taking the measurement as a hypothesis rather than as a fatal
      quantity: separability FAILED, which means the other seven classes are
      NOT a fixed tax to be paid by a big base rank -- they vary by 11 units
      at fixed max. That says the productive object is not a higher base
      rank at all; it is a curve whose SEVERAL TWISTS simultaneously carry
      forced points. Mestre's construction forces s(a_i) to be a square; the
      same machinery can force s(a_i) = d * square for a chosen d, putting
      prescribed points on E^(d) rather than on E. A construction that
      prescribes points across four or five classes of one k = 3 coset
      attacks the 8-class total directly instead of paying for it through
      one class. This is a candidate for the ranking, not evidence, and it
      changes no status. It is also the only route in view that is not
      blocked by O-07, since it produces the twist points by construction
      rather than by descent.
    spawned_ids: []
    spawned_ids_note: >-
      No identifier was minted. This role does not create ledger records, and
      an unminted candidate cannot be mistaken for an approved one.

  # ===================================================================
  narrowest_supported_statement: >-
    On the committed bytes of BATCH-e0caa5 at 2938068a3, and scoped to the
    502-curve small-coefficient pool, the support [-1,2,3,5,7,11,13], the
    five committed certificates, and the stated budgets: (1) the k = 3
    additive separability assumption of H-ECRANK-f2a2f7 is FALSE on the
    measured cosets -- at a fixed maximum single-class rank of 3 the total
    ranges over 10, 12, 14, 16, 18 within one certificate; (2) consequently
    no MEASURED base rank required for 31 at k = 3 exists in this batch, only
    four in-sample extrapolations spanning roughly 8 to 12 (base rank) and
    10 to 24 (max single class), of which the two coset-derived ones are
    invariant under randomising their own input and the most optimistic is a
    sample-size artifact; (3) the k = 3 fixture reproduces at 20 as a
    re-derivation from a committed artifact and as a re-verification of 20
    exhibited points, of which 8 are exact-certificate units and 12 are
    height-regulator units, with maximality UNVERIFIED; (4) the
    committed-support k = 4 optimum is 32, re-derivable at level A; (5) the
    archive's content binding holds on all six declared producer paths, now
    by independent recomputation. Nothing here is a statement about
    cryptographic scale, about any curve outside the tested pools, or about
    whether degree 8 is reachable.

  # ===================================================================
  next_concrete_action: >-
    Run C-02 before anything else: verify the externally reported rank->=31
    curve over Q against the committed verifiers and decide, in a recorded
    Coordinator decision, whether GOAL-ECRANK-002's C1 admits an external
    witness at degree 1 or must be restated as "by this construction". It
    costs minutes, it is the only action in this report that can settle the
    goal rather than refine it, and every other queued expense -- wider
    Mestre scans, extended support, a PARI-equipped re-run -- is ranked
    against a target that this decision may have already moved.

  # ===================================================================
  open_and_unattempted:
  - >-
    Independent verification of any per-twist rank lower bound r_low. NOT
    ATTEMPTED: no PARI, cypari, cypari2, gp or Sage in this session, verified
    by import and PATH check. This is an infrastructure fact and is not
    mathematical evidence in any direction.
  - >-
    Root numbers for any twist class, hence any test of the affine-parity
    reading in O-12 outside the five certificate cosets. OPEN AND
    UNATTEMPTED, same reason.
  - >-
    Any recomputation of the a7a9e8 height pairing matrices, eigenvalues or
    regulator determinants. NOT ATTEMPTED HERE -- point certification is the
    sibling reviewer's joint and duplicating it would trade coverage for
    correlation.
  - >-
    Verification of the 31 exhibited points of the external rank->=31 curve.
    OPEN AND UNATTEMPTED: this review read two external index pages and did
    not fetch or check a point list. The external record is cited as a
    pointer, never as evidence.
  - >-
    Any statement about whether 20 is the MAXIMUM k = 3 total over the pool
    (the producer's level C). OPEN AND UNATTEMPTED by this review as well.

  # ===================================================================
  artifact_paths:
  - coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/tasks/TASK-20260822-de2fa2/red_team_report.md

  # ===================================================================
  review_attestation:
    joints_owned:
    - the claimed base rank needed for 31 at k = 3 is MEASURED, not assumed (separability)
    - any degree-8 result is reported as WEAKER IN KIND than the held degree-32 exact certificate
    joints_owned_verdicts:
      separability: breaks
      certificate_kind: holds
    read_sibling_reports: false
    sibling_blindness_respected: >-
      review_plan.blindness.mutual is true and lifted_for is empty. No output
      of TASK-20260822-0de988 was opened, listed, or searched for, and no
      message was exchanged with any peer during this task.
    coordinator_prior_note: >-
      The dispatch card deliberately withheld the orchestrating session's
      conclusions and none were requested. The review plan's coordinator_prior
      was read as part of the handoff envelope, as the handoff requires; the
      verdicts above were reached from recomputation on committed bytes, and
      one of them (P3's supporting number) contradicts the prior's premise
      rather than agreeing with it.
    paths_read:
    - ledger/handoffs/TASK-20260822-de2fa2.yaml
    - agents/red-team.md
    - AGENTS.md and docs/inventor-protocol.md (role-binding contracts)
    - coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/archives/TASK-20260822-e7c486/receipt.yaml
    - coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/dispatch_queue.json
    - coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/tasks/TASK-20260822-a7a9e8/report.md
    - coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/tasks/TASK-20260822-a7a9e8/highrank_pool.json
    - coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/tasks/TASK-20260822-a7a9e8/CORRECTION-anomaly-A1-attribution.md
    - coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/tasks/TASK-20260822-a7a9e8/DEVIATION-immutability-trim.md
    - coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/tasks/TASK-20260822-8df232/report.md
    - coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/tasks/TASK-20260822-8df232/coset_structure.json
    - coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/tasks/TASK-20260822-8df232/runs/RUN-8df232-005-all/k3_coset_rows.json
    - ledger/hypotheses/H-ECRANK-f2a2f7.yaml
    - experiments/EXP-ECRANK-e1e30e/specification.yaml
    - experiments/EXP-ECRANK-e1e30e/analysis.md
    - experiments/EXP-ECRANK-e1e30e/source/twist_family.py
    - experiments/EXP-ECRANK-e1e30e/source/scan_pool.py
    - experiments/EXP-ECRANK-e1e30e/certificates/verification_summary.json
    - experiments/EXP-ECRANK-e1e30e/certificates/cert_deg8_control.json
    - experiments/EXP-ECRANK-e1e30e/runs/RUN-ECRANK-e1e30e-001/subspace_scan.json
    - experiments/EXP-ECRANK-e1e30e/runs/RUN-ECRANK-e1e30e-001/pool.json
    - coordination/goals/GOAL-ECQ-001/batches/BATCH-7e06d3/archives/TASK-20260822-66bacf/receipt.yaml (grep only, for the double-binding check)
    - .claude/agents/coordinator.md and orchestration/roles.yaml (tool-surface check for O-16)
    paths_read_note: >-
      Every producer and experiment path above was read from the committed
      tree, extracted with `git archive` at 2938068a3, not from the live
      worktree. The two harness files at the end were read from the worktree
      because they are runtime configuration, not research evidence.
    external_sources_used:
    - url: https://web.math.pmf.unizg.hr/~duje/tors/rankhist.html
      used_for: rank-record history over Q; entries for rank 30 and 31, Alpoge-Howell, 2026
    - url: https://elliptic-rank.icarm.cloud/curve/302
      used_for: the rank->=31 curve's credit line and submission timestamp 2026-08-23 20:02:58 UTC
    - url: https://www.lmfdb.org/EllipticCurve/Q/79/a/1
      used_for: rank, conductor, discriminant and torsion of [1,1,1,-2,0] for objection O-11
    - query: elliptic curve rank 30 record Alpoge Howell 2026 (WebSearch)
      used_for: locating the two pages above
    external_sources_note: >-
      Retrieval was used only where it could change a verdict: O-11 (a
      committed base rank is wrong) and C-02 (the goal's completion criterion
      may already be satisfiable). Nothing found externally is treated as
      evidence in this program's sense; each is a pointer to be verified by
      the committed verifier. An unfound source would have been evidence of
      nothing.
    knowledge_index_note: >-
      The kb MCP retrieval tools (search_knowledge, get_context, get_source,
      find_related) are NOT present in this session's tool surface, so the
      corpus was searched with grep instead. That is a weaker instrument and
      is disclosed as such: parity- and root-number-adjacent literature exists
      in the corpus (KN-LIT-212, KN-LIT-213, KN-LIT-376, KN-LIT-787 among
      others) and neither twist_family.py nor coset_structure.py mentions
      parity or root numbers at all. No novelty claim is made from this and
      no absence is inferred.
    computations_performed_by_this_review: >-
      All read-only, all on committed bytes, all in a scratch directory
      outside the repository, no repository file created or modified except
      the single deliverable. Recomputation of six sha256 digests at two
      commits; independent gunzip and sha256 of RUN-002's archived raw
      result; independent enumeration of the k = 3 sub-cosets of all five
      certificates (30/620/620/11160/1, matching the producer's row counts);
      recomputation of every fit in O4 and O5 (all reproduced to the recorded
      digits); a 200-trial label-shuffle null on each pooled fit; a 2-design
      pair-co-occurrence check; a brute-force search for affine parity
      functionals; a 20000-resample bootstrap and a 4-point jackknife on the
      frontier fit; k3/k4/k5/k6 optima and k3_cls/k4_cls histograms off the
      committed scan; pool composition, duplicate-model and coefficient-size
      statistics on highrank_pool.json; and the discriminant of the five seed
      curves from their a-invariants.
    no_committed_record_edited: true
    nothing_written_outside_write_scope: true
    committed_anything: false
    write_scope_used:
    - coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/tasks/TASK-20260822-de2fa2
    write_scope_note: >-
      The handoff declares no write_scope key; its deliverables and
      artifact_paths name exactly one file, and that is the only file
      written. Nothing under ledger/ was read for writing, created, staged or
      touched.
    fabrication_statement: >-
      Every number in this report was either read from a committed artifact
      named beside it or computed here from committed bytes by the
      computations listed above. Nothing was estimated, remembered, or filled
      in. Where a quantity could not be computed in this session it is listed
      under open_and_unattempted with the capability reason, per
      DEC-20260903-9c3e26 ruling_1.

  # ===================================================================
  provenance:
    requested_policy: review-adversarial
    requested_in: ledger/handoffs/TASK-20260822-de2fa2.yaml inference.policy; restated on the dispatch card
    resolved_model: claude-opus-5
    resolved_model_verification: >-
      Verified rather than self-reported: `python3 -m orchestration.adapter
      resolve --role red-team --independent-session` returns
      "review-adversarial -> anthropic:claude-opus-5 (effort=xhigh)", which
      matches this session's own runtime identity and the effort bound to the
      red-team subagent in .claude/agents/red-team.md. Without
      --independent-session the adapter refuses to resolve, which is the
      guard working.
    reasoning_effort_as_answered: xhigh
    reasoning_effort_capped: >-
      NONE KNOWN AND NONE ANNOUNCED TO THIS SESSION. Recorded as "not known
      to this role" rather than as "no cap was applied": under
      DEC-20260903-16bfc2 disclosure of a cap is owed by the session that
      applies it, and silence is the failure that decision exists to prevent.
    fallback_used: false
    degraded: false
    degraded_note: >-
      The handoff sets fallback_allowed false and degraded_allowed false and
      instructs REFUSE rather than downgrade. No downgrade occurred, so no
      refusal was required.
    independent_session: true
    backend: >-
      Not Amazon Bedrock. No provider, endpoint or model identifier
      containing `bedrock` was selected, requested or probed.
    budget:
      declared:
        wall_clock_seconds: 1800
        memory_gb: 2
        maximum_runs: 12
      measured:
        runs_executed: 0
        note: >-
          `runs_executed: 0` is exact and deliberate: a review executes no
          experiment. The read-only recomputations listed under
          computations_performed_by_this_review are analysis of committed
          bytes, not runs, and produce no run record. Wall clock and peak
          memory were not instrumented; memory stayed far below 2 GB (largest
          object handled was a 43 MB extracted subtree and a 112 MB
          decompression streamed through a pipe).
      charged_at: declared
