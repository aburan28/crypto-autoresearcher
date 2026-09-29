# RED TEAM REPORT — TASK-20260813-85e343

    goal / batch   GOAL-MLKEM-005 / BATCH-6b6e78
    role           red-team          policy review-adversarial, effort xhigh
    governed by    PREREG-2 (TASK-20260813-25cb95), frozen and notarized at
                   60ac819982793e8ed402bc3b2f4b7ad1b1824f92,
                   sha256 6c7c0800f0fdd94f62443262e5283aadc2149bad97d377634581d7aceba405ed
    reviews        TASK-20260813-2ce014 (lead producer), committed at
                   4e466c6bf221ea002fe84311baccdb816081a8cd
    archived by    TASK-20260813-3dfbdb (ledger archive) — THIS TASK COMMITS NOTHING
    claim tier     TOY, UNCONDITIONALLY

**CLAIM TIER TOY.** Nothing in this report bears on ML-KEM security, on any FIPS 203
parameter set, on any attack cost, or on any cost model. Nothing here transports to
`beta = 606`, `d = 1420`, or any other parameter set by extrapolation, analogy or any
other route.

**THIS REPORT RESCORES NO FROZEN VERDICT.** `R3-OUT-1`, `R3-OUT-2`, `R3-OUT-3`,
`R3-OUT-4`, `R3-OUT-5`, `R3-OUT-6`, `R3-OUT-7`, `R3-OUT-8`, `R3-OUT-V`-does-not-fire,
the five falsifier verdicts and the branch `T-A1-FALSIFIED-PARTIAL` are the producer's.
**I do not contest the branch.** Every probe below scores objects PREREG-2 does not
score, adds a rung PREREG-2 does not have, or re-derives a producer statement by a
method the producer did not use. `BATCH-a44d08` is not rescored, `BATCH-4ed139` is not
revalidated, `AM-3` is not retired, and nothing on PREREG-2 §10.1's NOT-CITABLE list is
cited anywhere in this report.

---

## 0. THE REQUIRED OUTPUT RECORD

```yaml
red_team_report:
  id: RT-20260813-85e343
  task_id: TASK-20260813-85e343
  claim_under_review: >-
    BATCH-6b6e78's headline is a NEGATIVE RESULT about an instrument assumption:
    T-A1-FALSIFIED-PARTIAL. Four of A-1's five frozen falsifiers fired — FC-1 for the
    raw-GSO class, FC-2a at 153 cells, FC-3a at 868, FC-3b at 354 — and the committed
    VAR-F verdict changes with working precision at 1,416 of 12,426 covered cells in 49
    of 330 blocks, 1,396 of them on the single route R4_gram_half_slogdet. Beside it:
    P-SEP's joint K-interval is EMPTY, P-F0Xb HELD (V6 = FAIL, V7 = FAIL, VX = PASS at
    38/38), P-GRAM FALSIFIED, and the producer's own surfaced scope fact that the
    certified-NON-CONSTANT class is populated ONLY by the null object X_hash.
  verdict_on_the_branch: >-
    THE BRANCH IS CORRECT AND I DO NOT CONTEST IT. R3-OUT-V was evaluated first and did
    not fire; T-UNSTATABLE correctly did not fire because FC-1 fired for one class of
    two; T-A1-FALSIFIED correctly fired; the -PARTIAL suffix is correctly applied to
    114 uncovered cells; and no infrastructure or coverage outcome was narrated into a
    science branch. The branch is ROBUST TO EVERY OBJECTION BELOW: set FC-1 aside
    entirely and FC-2a, FC-3a and FC-3b each independently still fire it. I
    independently reproduced the 1,416 / 49-block headline exactly (probe 1) and the
    per-lattice P-GRAM deviations exactly (probe 3).
  verdict_on_what_the_branch_is_taken_to_MEAN: >-
    NOT ONE CELL OF T-A1-FALSIFIED COMES FROM A REAL OBJECT MEASURED AGAINST A REACHABLE
    BAR. FC-3a and FC-3b fired exclusively on the null object X_hash — the producer says
    so itself — and 684 of FC-3a's 868 cells and all 354 of FC-3b's are at the single
    declared amplitude c = 1e-9, whose injected fibre dispersion is 60x to 1180x BELOW
    the binary32 unit roundoff, so the float evaluation could not have failed to destroy
    it. FC-2a fired at 153 cells of which 153 have rho(binary32) = 0.0 EXACTLY: the
    low-precision estimator returned the true value, and A-1.2's strict-decrease test
    counts being exactly right as a falsification because §1.3's exemption is one-sided.
    FC-1 fired because P-GRAM asks one exact value to sit within 1e-10 of BOTH committed
    float64 routes, which differ from each other by up to 3.0015e-09 — no exact route,
    correct or incorrect, could have met it at 5 of the 10 lattices. That FC-1 firing is
    what leaves X_gso_k UNCERTIFIED, which is what empties the certified-NON-CONSTANT
    class of every real object, which is what makes A-1.3 a test of the null alone. One
    unsatisfiable consistency tolerance cascades into the batch's entire scope limit.
  objections:
  - id: O-1
    severity: high
    title: >-
      FC-1 fired against a bar NO exact route could meet, at 5 of 10 lattices, and that
      single unreachable tolerance is the sole cause of the batch's headline scope limit.
      BUILT AND MEASURED INDEPENDENTLY.
    what_was_built: probes/probe_pgram_reach.py
    measured: >-
      P-GRAM requires one exact value within 1e-10 absolute of BOTH RQ and RG. If the two
      float64 routes differ by D, no third number is within D/2 of both. Measured on the
      frozen F0 bases, max|RQ - RG| over the 8 bases is 1.7764e-15 (L1, L4, L7, L11),
      0.0 (L9), 4.3544e-10 (L8), 3.4195e-10 (L10), 6.1891e-10 (L12), 1.3314e-09 (L2) and
      3.0015e-09 (L5). The smallest tolerance ANY exact route could have met is therefore
      1.5008e-09, which is 15.008x above the frozen 1e-10. P-GRAM IS UNREACHABLE AT 5 OF
      10 LATTICES — exactly L2, L5, L8, L10, L12, i.e. every lattice with k > d-k.
    why_it_matters: >-
      FC-1's firing is scored per candidate class; it fired for the raw-GSO class, which
      contains the ONE in-scope candidate that reads the instance. X_gso_k is therefore
      UNCERTIFIED, P-A13a is NOT SCORABLE, and the certified-NON-CONSTANT class contains
      only X_hash. The producer applied the frozen clause exactly as written and did not
      patch it, which is correct; the defect is in the clause, not in the producer.
    against_my_own_thesis: >-
      REPORTED AT THE SAME WEIGHT. Removing FC-1 does not change the branch: FC-2a,
      FC-3a and FC-3b each independently fire T-A1-FALSIFIED. And the producer reached
      this conclusion first, as its OBJ-1, from the committed route_agreement_RQ_vs_RG
      field; my contribution is an independent measurement of the same gap and the
      per-lattice reachability count, not the insight.
  - id: O-2
    severity: high
    title: >-
      THE PRIMARY TARGET, BUILT: two objects, neither a digest, that satisfy A-1 in every
      respect and carry no lattice information. The empty-real-object class is not an
      accident of this candidate list.
    what_was_built: probes/probe_nonconstant_null.py
    measured: >-
      X_lin = mean(A entries)/q, a LINEAR functional — no hash, monotone and continuous
      in every entry — and X_par = (#even entries of A)/(k(d-k)), a COUNTING functional
      whose values are ratios of integers below 2**24 and hence exactly representable at
      both declared precisions. On the frozen PIN-DET fibre, at all 10 lattices and all
      three declared draws: exact route by integer arithmetic, 0.0327 s for BOTH objects
      over 60 fibre evaluations, CERTIFIED EXACTLY NON-CONSTANT at 30 of 30 fibres;
      rho > 0 at both declared precisions at 30 of 30; rho(binary32)/rho(binary64) in
      [0.999997517, 1.000003717] for X_lin and [0.999998595, 1.000000653] for X_par, so
      0 of 30 cells outside the frozen [1/2, 2] window. NEITHER FC-3a NOR FC-3b WOULD
      FIRE ON EITHER OBJECT. Provably not lattice invariants: U = I + E_{0,k} is integral
      with det U = 1, so B and UB generate the IDENTICAL lattice while A[0,0] moves by
      +q; measured at 10 of 10 lattices, X_lin moves by exactly 1/(k(d-k)) and X_par by
      the same magnitude, on the same lattice. Carrying no usable information about the
      one in-scope geometric observable: Pearson r against X_gso_k (RQ, binary64) over
      the 8 bases of each fibre, replicated over the three declared draws (AM-10), median
      r = -0.0045 for X_lin (IQR [-0.1554, +0.1455], range [-0.6228, +0.5245]) and
      -0.0178 for X_par, against a MUST-PASS control — RG versus RQ, two routes for the
      same geometric quantity — of exactly +1.0000 with zero IQR.
    why_it_matters: >-
      PREREG-2 §5 froze the consequence of P-HASH HOLDING. P-HASH was falsified, so that
      consequence does not arise from X_hash. It arises from these objects instead, and
      by a route that is not a float effect at all: X_lin and X_par are certified by
      EXACT arithmetic, are precision-invariant to one part in a million, and are
      provably not lattice invariants. A-1's certified-NON-CONSTANT class therefore
      admits an unbounded family of information-free objects and cannot separate them
      from a real one. That A FLOAT-EVALUATED fibre test cannot make this separation is
      PROMOTED in KN-FIND-9d44b4 and is NOT restated here as new; what is new is that
      the separation fails under EXACT evaluation and under a non-digest object.
    against_my_own_thesis: >-
      REPORTED AT THE SAME WEIGHT, TWICE. (i) X_gso_k moves under the same unimodular row
      operation at 10 of 10 lattices, so basis-dependence does NOT by itself separate my
      built objects from the one in-scope candidate that reads the instance; the whole
      candidate class is presentation-dependent. (ii) The correlation instrument has 8
      points per fibre, so under independence the sd of r is about 1/sqrt(7) = 0.378 and
      the observed IQR widths are exactly that; the measurement therefore supports "no
      STRONG correlation with the geometry" and does NOT support "no information". It is
      a controlled null, not a proof of independence, and X_hash's own median r of
      +0.0670 sits inside the same band.
  - id: O-3
    severity: high
    title: >-
      Every falsifier that fired, fired either on an object that reads no free content of
      the instance, or against a bar no value could meet. T-A1-FALSIFIED is true as
      stated and empty of real objects.
    measured: >-
      FC-3a (868) and FC-3b (354): X_hash only, at every cell, on all three draws —
      recomputed by me from the complete per-cell record, 868 and 354 exactly. FC-2a
      (153): X_null, rdet, X_parfree, V_evade and all ten X_lambda, every one of them
      certified CONSTANT, i.e. reading no free content of A on its own fibre. FC-1: the
      raw-GSO class, via O-1's unreachable tolerance. FC-2b: did not fire.
    self_correction_reported_at_the_same_weight: >-
      A-1.2's DOMAIN is the certified-CONSTANT class, so "FC-2a fired only on objects
      that carry no lattice information" is a tautology of the sub-clause's domain and
      NOT an additional defect. The sharp statement is narrower and survives: A-1.3 is
      the only sub-clause whose domain can contain a real object, its domain in this run
      contained exactly one object, and that object is the declared null.
  - id: O-4
    severity: high
    title: >-
      PREREG-2 §6.3 named ONE could-not-HOLD arrangement. There are FOUR, the batch ran
      in all four, and the three unnamed ones produced every cell of three falsifiers.
    measured: >-
      (i) NAMED, §6.3: rho(binary64) == 0 exactly at R0 by the definition of R0.
      Measured: 4,788 precision_degenerate cells, all 4,788 falsified under the strict
      reading, exempt under the frozen one. (ii) UNNAMED: P-GRAM's tolerance is below
      max|RQ-RG|/2 at 5 of 10 lattices (O-1), so FC-1 COULD NOT HAVE FAILED TO FIRE.
      (iii) UNNAMED: §1.3's exemption is ONE-SIDED. It exempts rho(binary64) == 0 and
      says nothing about rho(binary32) == 0. All 153 FC-2a firings have
      rho(binary32) = 0.0 EXACTLY with rho(binary64) between 9.514e-15 and 5.109e-14 —
      the true dispersion is 0, the low-precision estimator hit it, the high-precision
      one returned rounding noise, and A-1.2's STRICT decrease scores the exactly-correct
      answer as a falsification. A two-sided exemption would have left 0 of 153 (stated
      as a counterfactual reading, NOT applied, the frozen reading binds). (iv) UNNAMED:
      the declared amplitude grid contains c = 1e-9, at which X_hash's fibre dispersion
      is 5.052e-11 to 9.926e-10 against u_32 = 5.960e-08 — a factor of 60.1 to 1179.8
      BELOW the binary32 unit roundoff. FC-3b could not have failed to fire there, and it
      accounts for 354 of 354 FC-3b cells and 684 of 868 FC-3a cells.
    why_it_matters: >-
      AM-18(d) forced published reachability on GUARDS and PREREG-2 §6.1 honoured it. The
      same discipline applied to the FALSIFIERS in the could-not-PASS direction would
      have caught all three before the run, each with one line of arithmetic on already
      committed numbers and no compute at all.
  - id: O-5
    severity: medium
    title: >-
      "1,416 cells, 1,396 on R4" is a real measurement of a real phenomenon, but the
      COUNT is a property of the route set crossed with the precision pair, not of the
      clause. The ladder and the nearby object were BUILT, and one of them fires against
      me.
    what_was_built: probes/probe_precision_ladder.py
    measured: >-
      Independent reproduction first: rebuilding the 324 determinant-only blocks from the
      frozen seeds and scoring them through the IMPORTED committed var_f_from_cells gives
      1,416 changing cells in 49 blocks, R4 = 1,396 and R2 = 20 — the lead's numbers
      exactly. Then the third rung, which PREREG-2 does not have: at EXACT arithmetic
      every route collapses to log|det B| = (d-k) log q, which is known in closed form for
      these families. Verdict changes at the binary64 -> EXACT rung: 684 cells, spread
      EVENLY over R2 = 228, R4 = 228 and R5 = 228, zero on R0, R1 and R3, and confined to
      exactly two candidates, rdet and X_parfree. Advance knowledge of R4: max|B B^T|
      exceeds 2**24 — the largest integer binary32 represents exactly — at 10 of 10
      lattices, by 1 to 5 bits; R4's absolute error against the exact log|det B| at
      binary32 is 4.581 to 204.2 on values of 48.66 to 811.0, a relative error of 4.0% to
      63%, against 7.105e-15 to 9.095e-13 for R1 at binary64. NEARBY OBJECT: forming the
      SAME Gram exactly in int64 and casting the finished matrix to binary32 leaves
      1,293 of the 1,396 changes, so exact accumulation removes only 7.4% — the defect is
      the representation of the Gram in binary32, not the accumulation, and R4 is not
      "badly implemented".
    what_it_means: >-
      Two distinct mechanisms are being counted as one number. The 1,396 R4 cells and the
      20 R2 cells at the binary32 rung are the SCALED-DISPERSION path: route noise
      inflates s_c above tau_var * R_{d,k}. The 684 cells at the binary64 -> EXACT rung
      are the BIT-IDENTITY path at scale-degenerate cells, on the two candidates that do
      not depend on beta. THE SECOND ONE IS AGAINST MY OWN THESIS AND IS REPORTED AT FULL
      WEIGHT: the clause's dependence on the representation is NOT an R4-at-binary32
      artifact, it survives at the highest rung on three routes with R4 holding no
      privileged position. What IS an artifact of R4 at binary32 is the CONCENTRATION —
      98.6% on one route — and therefore the number 1,416 itself. A count of verdict
      changes is a joint function of its route set and its precision pair, and PREREG-2
      §4's own C-1 lesson — a verdict may not be cited without naming its route set —
      applies to this count and is not yet applied to it.
    attribution: >-
      That rdet is admitted at binary64 through R2, R4 and R5 and refused under the exact
      route is PROMOTED in KN-FIND-9d44b4 and is NOT a new result of this batch or of
      this probe. The binary64 -> EXACT rung reproduces that promoted mechanism and
      extends it to X_parfree, the Validator's blind null.
  - id: O-6
    severity: medium
    title: >-
      FC-2a's count of 153 is the one statistic in this batch with no replicate
      stability — 5 / 98 / 50 across the three declared AM-10 draws, a factor of 19.6 —
      and it is reported without its dispersion.
    measured: >-
      Recomputed from the committed per-cell record. Of 9,576 certified-CONSTANT cells,
      4,788 are precision_degenerate and 4,788 are eligible for FC-2a; 153 fired, all on
      R2_QR_of_BT (153 of that route's 1,596 eligible cells, 9.6%). Per fibre family:
      F0|fib_s2 2 + 3 = 5, F0|fib_s3 15 + 83 = 98, F0|fib_s4 15 + 35 = 50. By contrast
      FC-3a is 289 / 288 / 291 and FC-3b is 116 / 119 / 119 across the same three draws,
      and the VAR-F change count is 108 / 104 / 126 and 352 / 341 / 385 — all stable to
      about 10%, WHICH IS REPORTED IN THE PRODUCER'S FAVOUR.
    why_it_matters: >-
      AM-11 requires dispersion for every statistic and AM-10 requires replication. The
      dispersion is present in the committed JSON and absent from the reported figure,
      and the one falsifier whose count is unstable is also the one that carries the
      falsification of P-A12b, one of the batch's five items of empirical content. A
      falsifier whose cell count moves by a factor of 19.6 between replicate draws is
      being driven by which rounding ties happen to occur, which is the same reading O-4
      (iii) gives it from the other side.
  - id: O-7
    severity: medium
    title: >-
      FC-2b is not a falsifier. Under PREREG-2 §3.3's own certification rule it CANNOT
      fire, and the only way it ever fired was through an implementation constant the
      frozen text does not fix.
    argument: >-
      §3.3 certifies a candidate CONSTANT iff all 8 exact fibre values are EQUAL. If they
      are equal their standard deviation is 0 and rho is 0. FC-2b asks whether some
      candidate certified exactly constant has rho > 0 under the exact route — which, by
      the definition of the certification, is impossible. Its non-firing is therefore
      analytically foreclosed and is not evidence about A-1 in either direction. This is
      the O-6-of-BATCH-4ed139 discipline (a VOID row unreachable by a factor of 71.3)
      applied to a falsifier: a falsifier that could not fire is not a falsifier, and
      PREREG-2 §6.2's claim that "four of the five falsifiers carry no numeric constant
      at all" conceals that one of those four also carries no reachability.
    corroborating_measurement: >-
      The producer's own disclosed defect (b) is the proof: at DEC_STAT_PREC = 60 the
      sd of eight EQUAL exact values came out at order 1e-59 > 0 and FC-2b fired; at 240
      it is exactly 0 and it does not. So the verdict of a falsifier advertised as
      "existence only, no threshold" is a function of an unfrozen implementation
      constant. results_a1.json names that field
      implementation_statistic_significant_digits_NOT_A_FROZEN_CONSTANT, so the producer
      flagged it; the objection is to §6.2's claim, not to the disclosure.
  - id: O-8
    severity: medium
    title: >-
      P-SEP's headline survives my attack — reported first and at full weight — but the
      one part of P-SEP that PREREG-2 §3.5 itself calls "genuinely open" is decided
      entirely by the sub-ulp amplitude.
    measured: >-
      My re-analysis of the committed per-cell record, NOT a rescoring of R3-OUT-5. As
      scored, K_max is set by an X_hash[c=1e-09] cell at 11 of the 12 defined
      (route, precision) rows, and every binary32 row is EMPTY because those cells give
      rho = 0 exactly, hence K_max = 0. Dropping the sub-ulp amplitude: the per-route
      intersections over both precisions flip from EMPTY to NON-EMPTY on R0, R1 and R3;
      they stay EMPTY on R2, R4 and R5. Dropping the sub-ulp amplitude AND route R4: the
      JOINT intersection is STILL EMPTY, K_min = 1616.47 against K_max = 836.898. SO
      P-SEP'S FROZEN PREDICTION IS NOT AN ARTIFACT OF EITHER OF MY TWO KNOCKS AND I SAY
      SO PLAINLY. What is an artifact is the per-route half, and PREREG-2 §3.5 is the
      document that flagged the per-route half as the weaker and genuinely open
      possibility. The three routes that flip are exactly the three where the certified-
      CONSTANT class has rho identically 0, so their non-emptiness is itself degenerate —
      it says only that any positive K separates 0 from something positive.
  - id: O-9
    severity: medium
    title: >-
      SCOPE AND DOMINANCE: wherever an exact route exists the estimator is dominated by
      it on every axis, and A-1 is stated ONLY over candidates where one exists. A-1 was
      tested exactly where it is not needed and is silent exactly where it would be.
    argument: >-
      The exact route decides "constant on the fibre" by comparing 8 exact values: no
      precision, no route, no window, no threshold, no falsifier. Cost measured here:
      0.0327 s for two objects over 60 fibres (probe 2); the producer's own R6_exact plus
      R7_exact_gram cost 20.211 s over the whole declared grid. The two-precision, six-
      route estimator apparatus cost 26.947 s to produce 12,426 cells and, on the
      determinant-only class, agrees with the exact route wherever it is not being
      destroyed by its own route noise. The estimator is NEEDED only where no exact route
      exists — which is precisely the reduction-dependent class lam1n / hkz / rawtail
      that PREREG-2 §2.5 declares OUT OF SCOPE, and about which §11 says A-1 says nothing
      in either direction. That is the half of the candidate list that matters for C3.
    why_it_matters: >-
      This is not an argument against running the batch; the assumption had to be
      numbered and exposed. It is an argument about what a successor may conclude: A-1
      held or falsified is a statement about the class of observables for which the
      question is already answerable exactly.
  - id: O-10
    severity: low
    title: >-
      The -PARTIAL suffix is caused by a determinate binary32 representation fact that
      was knowable before the run, not by a host failure. The producer's conservative
      classification is right and I do not contest it.
    measured: >-
      The 114 uncovered cells are X_gso_k | RG_cholesky_of_gram at binary32, where
      numpy raises LinAlgError "not positive definite". The Gram's largest entry exceeds
      2**24 at 10 of 10 lattices (probe 1), so the binary32 Gram is not the Gram and need
      not be positive definite. This is reproducible on any host and is the SAME mechanism
      as R4's binary32 failure. PREREG-2 §7.6 lists "a timeout, a crash, a missing
      dependency, or the declared R7 cap"; classifying a deterministic arithmetic
      limitation as a crash is the conservative reading and AGENTS.md rule 5 protects it,
      so the outcome is right. The observation for a successor is that this coverage gap
      could have been declared in advance as a scope limit rather than discovered.
  - id: O-11
    severity: medium
    title: >-
      PROCEDURAL INDEPENDENCE: the lead's recorded inference substitution puts the
      producer and both reviewers of this batch on ONE model. This batch is not "two
      sessions on one model"; it is producer-and-reviewer on one model.
    measured: >-
      run_manifest.yaml records requested_policy executor-implementation, adapter binding
      anthropic:claude-sonnet-5, and claude-opus-5 as the model that answered, with
      requested_and_resolved_agree: false. My own binding, resolved in this session with
      `python3 -m orchestration.adapter resolve --role red-team --independent-session`,
      is review-adversarial -> anthropic:claude-opus-5 (effort=xhigh), and claude-opus-5
      answered. So the producer and I are the same model. model_verified is false for
      both — no `doctor --probe` was run — and AGENTS.md rule 12 is UNMET AND UNWAIVED.
    why_it_matters: >-
      PREREG-2 §11 states that independence is procedural and never model-level. The
      substitution makes that stronger than the text anticipates: the review of this
      batch cannot be model-independent of the thing it reviews. It is disclosed, it is
      not a capability downgrade, and it is recorded here rather than reconciled.
  - id: O-12
    severity: medium
    title: >-
      §7.5's REPAIR BAR is satisfiable and is NOT a lane closure by the back door — but
      three of its six conditions cannot block anything, and by its own condition 1 this
      batch does not fully satisfy the bar it wrote for its successors.
    argument: >-
      Conditions 1, 3 and 4 have teeth, and 4 is demonstrably satisfiable: probe 2
      exhibits exactly the object condition 4 demands a criterion name and exhibit.
      Condition 2 carries its own escape — "a successor that repeats it WITHOUT DECLARING
      IT is illegitimate" — so declaring the calibration satisfies it, which is what
      PREREG-2 §1.4 itself did for the [1/2, 2] window. Condition 5 is a disclosure
      requirement and can never block a proposal. Condition 6 requires stating why the
      alternative is worse while the same document forbids taking that alternative, so it
      is satisfied by citing the forbiddance. The absolute bar on an eighth consecutive
      repair requires a committed decision recording why C3 cannot be entered instead;
      the evidence for that record already exists, so the bar prices an eighth repair at
      one decision record rather than forbidding it. CONCLUSION IN BOTH DIRECTIONS: the
      bar does not forbid every repair, so it is not premature closure by the back door;
      its weakness is the mirror one, that half of it binds narration rather than
      substance. DOES THE BATCH SATISFY ITS OWN BAR? Under condition 1, PARTIALLY NO:
      A-1 is numbered, textually first, and its falsifiers' reachability was published in
      advance in the FIRE direction (§6.2), but the could-not-HOLD publication (§6.3)
      named one arrangement of four and the three it missed produced every cell of FC-1,
      FC-2a and FC-3b (O-4).
  required_controls:
  - >-
    THE ONE-SIDED EXEMPTION, MADE TWO-SIDED, BEFORE ANY SUCCESSOR ASSUMPTION IS WRITTEN.
    A successor to A-1.2 must exempt or otherwise handle cells where the estimator at
    EITHER declared precision returns exactly the true value, because a strict-decrease
    test between two estimates of the same true zero has an absorbing floor that the
    lower-precision estimate can hit. Cost: a sentence in the successor's §1.3.
  - >-
    AN AMPLITUDE FLOOR TIED TO THE WORKING PRECISION. Any null-object calibration grid
    evaluated at two precisions must declare, per amplitude, the ratio of the injected
    fibre dispersion to the unit roundoff of the LOWEST declared precision, and must not
    report a falsifier firing at an amplitude below it as a property of the assumption.
    Measured boundary for this family: c* between 6.005e-08 and 1.180e-06. Cost: one line
    of arithmetic on already-committed numbers.
  - >-
    A CONSISTENCY TOLERANCE THAT IS FEASIBLE BY CONSTRUCTION. Any future clause requiring
    an exact route to reproduce N committed float routes must set its tolerance no tighter
    than max over cells of (max - min over those routes) / 2, and must publish that
    quantity BEFORE the run. Cost: 5.2 s (probe 3) on the frozen bases.
  - >-
    THE NULL-OBJECT CONTROL FOR THE CERTIFIED-NON-CONSTANT CLASS. Any successor
    assumption whose non-constant class governs a real object must be scored with at
    least one NON-DIGEST information-free object in that class, so the class is never
    populated by the null alone. Built here: X_lin and X_par, 1.8 s.
  - >-
    PER-DRAW DISPERSION ON EVERY REPORTED CELL COUNT. AM-10 and AM-11 apply to falsifier
    cell counts as much as to dispersion statistics; FC-2a's 5 / 98 / 50 is the case that
    shows why. Cost: zero, the data is already in results_a1.json.
  counterexample_or_mutation: >-
    THE CHEAPEST DISCRIMINATING MUTATION, BUILT AND RUN: add one rung to the precision
    ladder. Evaluating the identical committed VAR-F clause at EXACT arithmetic — which
    for these frozen families is closed-form, log|det B| = (d-k) log q — separates the
    two mechanisms hiding inside the number 1,416. The binary32 -> binary64 rung gives
    1,416 changes with 1,396 on one route; the binary64 -> EXACT rung gives 684 changes
    spread evenly over three routes at 228 each and confined to two candidates. Cost:
    18.2 s, no new specification, no new object. The complementary mutation, forming the
    Gram exactly in int64 before casting to binary32, leaves 1,293 of the 1,396 changes
    and rules out the accumulation as the cause.
  baseline_comparison: >-
    The correct baseline for A-1 is not another dispersion criterion, it is THE EXACT
    ROUTE ITSELF. Deciding "constant on the fibre" by comparing 8 exact values costs
    0.0327 s for two objects over 60 fibres, needs no precision, no route set, no window,
    no threshold and no falsifier, and is correct by construction. Against that baseline
    the two-precision six-route estimator is dominated on every axis this program
    measures — time (26.947 s versus 20.211 s for the exact routes over the same grid,
    with the estimator additionally requiring the exact routes to certify its classes at
    all), correctness (windowed versus exact), and specification complexity (five
    falsifiers, one calibrated constant, one exemption rule, versus one equality test).
    The estimator is NOT dominated in the one regime where no exact route exists, the
    reduction-dependent observables lam1n / hkz / rawtail — and PREREG-2 §2.5 places
    exactly those OUT OF SCOPE. dominated_by is therefore NOT null and it is named: for
    every candidate A-1 is stated over, the exact route dominates the estimator.
  heuristic_challenges:
  - >-
    A-1 IS NUMBERED, ITS THREE COMPONENTS ARE SEPARATELY FALSIFIABLE, AND ITS ONE
    CALIBRATED CONSTANT DECLARES ITS BASIS AND ITS WEAKNESS IN ADVANCE (§1.4). That is
    the standard the target profile asks for and this pre-registration meets it. The
    challenge is not that a heuristic is unnumbered; it is that THREE OF THE FIVE
    FALSIFIERS WERE FORECLOSED IN ADVANCE IN THE FIRING DIRECTION AND ONE IS FORECLOSED
    IN THE NON-FIRING DIRECTION, so the numbering bought less falsification than it
    appears to. FC-1: foreclosed to fire (O-1). FC-2b: foreclosed not to fire (O-7).
    FC-3b and 684 of FC-3a's 868 cells: foreclosed to fire by the sub-ulp amplitude
    (O-4 iv). What remains genuinely open and genuinely tested is FC-2a's 153 cells,
    whose count is replicate-unstable by a factor of 19.6 (O-6), and FC-3a's 184 cells at
    amplitudes above the unit roundoff, all of which are on route R4.
  - >-
    THE RANDOM-MODEL TRANSFER QUESTION, IN THIS BATCH'S IDIOM: a null object with an
    adjustable amplitude is not a model of a real observable. X_hash's fibre dispersion
    is c-tunable over nine decades by construction, so every A-1.3 verdict on it is a
    statement about where c sits relative to a route's noise floor. A real observable's
    dispersion is not tunable, and the archived X_gso_k ratios (0.9999991 to 1.0000001,
    carried and attributed, never measured here) sit six orders from the window. The
    cheapest experiment that would expose the deviation is the one built here: score a
    NON-TUNABLE information-free object — X_lin and X_par have no amplitude parameter at
    all — and see whether A-1.3 separates it from the real object. It does not.
  cost_model_challenges:
  - >-
    NO COST MODEL, NO ASYMPTOTIC CLAIM AND NO ATTACK COST APPEARS ANYWHERE IN THIS BATCH,
    and none may be inferred from it. The only cost statements are wall clocks and they
    are recorded: 26.947 s of a 600 s cap for the measurement, 20.211 s of exact-route
    time inside it, 0.405 s for the re-run archived probe, worst case 3.3 s per lattice
    for R7_exact_gram against a declared 45 s cap. My own probes: 18.2 s + 1.8 s + 5.2 s
    = 25.2 s total.
  - >-
    MEMORY IS MISSING DATA ON BOTH SIDES AND IS REPORTED AS SUCH. The producer did not
    instrument peak RSS and says so rather than estimating it against the 4 GB budget;
    I did not instrument mine either and say so here. Neither of us may claim the memory
    budget was met, only that no MemoryError, OOM or swap event was observed.
  reduction_and_scope_challenges:
  - >-
    THE SCOPE STATEMENT IS NOT INFLATED AND, ON ONE POINT, THE PRODUCER UNDERSTATES ITS
    OWN LIMIT IN ITS OWN FAVOUR — it surfaced the empty-real-object fact against itself
    (report §3, §12.4) and carried it into the snapshot receipt. I confirm it and sharpen
    it: A-1.3's certified-NON-CONSTANT class contained ONE object, the declared null; the
    only in-scope candidate reading the instance was UNCERTIFIED; and the entire
    reduction-dependent half of the goal's candidate list is out of scope by declaration.
  - >-
    NO CITED REDUCTION, COROLLARY OR EXTERNAL THEOREM IS INSTANTIATED ANYWHERE IN THIS
    BATCH, so there is nothing of that kind to check. The one derived result, PREREG-2
    §2.9, is checked in O-13 below and is CORRECT.
  - >-
    THE AFFECTED-VS-SAFE AUDIT IS TRIVIALLY SATISFIED AND MUST STAY THAT WAY: no scheme,
    no parameter set and no security claim is in scope. CLAIM TIER TOY.
  proof_architecture_challenges:
  - id: O-13
    severity: none — THIS ONE FIRES AGAINST ME AND IS REPORTED AT THE SAME WEIGHT
    title: >-
      I tried to break PREREG-2 §2.9's derivation by an independent method and could not.
      It is correct.
    measured: >-
      probes/probe_pgram_reach.py checks X_gso_k = (1/(2k)) log det(I_k + A A^T) twice.
      Check 1 is my own multi-modular integer determinant with CRT sized by the Hadamard
      bound — a different implementation from the lead's. Check 2 is EXACT RATIONAL
      GRAM-SCHMIDT of the first k rows with ||b*_j||^2 as Fractions, which uses no
      determinant anywhere and is therefore independent of the identity being tested.
      The two agree to 0.000e+00 at L7, L8, L9 and L11 and to 7e-59 at L10 and 6e-59 at
      L12, which is decimal rounding at the declared 60 digits. The exact value agrees
      with the committed float64 route RQ to at most 1.337e-13 at every one of the 10
      lattices and disagrees with RG by up to 3.002e-09. I looked for the failure modes
      the task card names — a case where I_k + A A^T is not the leading Gram block, a
      row-order difference, an overflow, a wrong k — and found none: the block structure
      B[:k] = [I_k | A_i] holds entrywise at every basis, so G_k = I_k + A A^T is the
      leading Gram block by construction; k is the identity-block dimension consistently
      in both the family and the observable; and the determinant is exact integer
      arithmetic with no float representation read anywhere.
    consequence: >-
      THE DERIVATION IS NOT THE DEFECT. RG IS. The producer said so as its OBJ-1 and
      declined to patch the clause; an independent exact computation the producer did not
      perform confirms it. P-GRAM's FALSIFIED verdict and FC-1's firing therefore record
      a property of route RG's Cholesky at binary64 and of an infeasible tolerance, and
      NOT a decidability failure for the raw-GSO class. Whether that is repaired is a
      Coordinator act and I propose no replacement tolerance.
  - id: O-14
    severity: low
    title: >-
      The two pre-run implementation fixes, checked for tuning toward the reported
      outcome. One could not have been tuned; the other could have been, and was not,
      but it leaves an unfrozen constant in a falsifier.
    argument: >-
      FIX (a), the guard ranging over the union of declared arguments and declared
      nuisance set: it moved the batch OFF T-VOID, which is the direction that produces
      results, so it deserves scrutiny. It cannot have manufactured a passing guard,
      because its subject — |det B_i| across i — is q^(d-k) BY CONSTRUCTION of the frozen
      PIN-DET family, is verified entrywise, and is exactly what PREREG-2 §6.1 says makes
      the void row unreachable except through an implementation error. The union reading
      is also what §3.1's own words require ("the whole declared nuisance set"). No
      tuning is possible here. FIX (b), the statistic's decimal context moved from 60 to
      240 digits: it removed an FC-2b firing, i.e. it moved a falsifier from fired to not
      fired, after the 60-digit run had shown it firing. The mathematics is right — eight
      equal exact values have sd exactly 0 and a nonzero sd at 60 digits is an artifact of
      the variance computation — and the outcome is robust, because under the
      precision-free reading (are the 8 exact values equal?) FC-2b cannot fire at all
      (O-7). So the fix did not change the correct answer. What it leaves behind is an
      unfrozen constant inside a falsifier advertised as carrying none, and a decision
      about that constant taken after observing its effect. Fully disclosed by the
      producer as deviation 5(b) and named NOT_A_FROZEN_CONSTANT in its own output.
  narrowest_supported_statement: >-
    A-1 AS LITERALLY QUANTIFIED — over the 19 in-scope declared candidate instances, the
    six declared float routes plus the two exact routes, the two declared working
    precisions, the frozen amplitude and lambda grids, the frozen family F0 and its three
    PIN-DET / PIN-A00 fibre draws, at q = 3329 and d in {20, 30, 40, 100, 140}, with no
    reduction of any kind — IS FALSE, and T-A1-FALSIFIED-PARTIAL is the branch its own
    frozen clause fires. THAT IS AN INSTRUMENT OUTCOME AND NOTHING ELSE. Beneath it, the
    narrowest reading the rows support is this: (1) A-1.1 is not shown to fail for the
    raw-GSO class — an exact route for X_gso_k EXISTS, is CORRECT (O-13), and terminates
    at 3.3 s worst case against a 45 s cap; what failed is a consistency tolerance no
    exact route could have met at 5 of 10 lattices. (2) A-1.2 fails at 153 of 4,788
    eligible cells, all on one route, all at cells where the binary32 estimator returned
    the exactly correct value 0, with a replicate spread of 5 / 98 / 50; and it fails at
    4,788 further cells under the strict reading of §1.3 by the definition of R0, which
    §6.3 named in advance. (3) A-1.3 fails only on the declared null object, and 684 of
    its 868 FC-3a cells and all 354 FC-3b cells are at an amplitude 60x to 1180x below
    the binary32 unit roundoff; at the three amplitudes above it, A-1.3 fails on route R4
    alone, with a count decaying 113 -> 60 -> 11 as the amplitude rises, which is the
    decay a real precision effect should show. (4) NO SUB-CLAUSE OF A-1 WAS TESTED
    AGAINST AN OBJECT THAT READS THE INSTANCE AT A REACHABLE BAR, AND A-1 SAYS NOTHING
    ABOUT ANY REDUCTION-DEPENDENT OBSERVABLE. (5) An object certified exactly
    non-constant, precision-invariant to one part in a million, provably not a lattice
    invariant and not a digest, is exhibited (O-2), so A-1's certified-NON-CONSTANT class
    does not distinguish reading the instance from reading the presentation. NONE OF THIS
    IS EVIDENCE ABOUT ANY LATTICE, ANY OBSERVABLE'S ADMISSIBILITY, ANY PARAMETER SET, ANY
    ATTACK COST OR ANY COST MODEL, AND IT CLOSES, PAUSES AND COMPLETES NOTHING.
  next_concrete_action: >-
    ONE ACTION, AND IT IS NOT A GATE REPAIR. Before any successor assumption or any
    eighth instrument batch, run the ONE cheap measurement this seven-batch sequence has
    never run: take the reduction-dependent observables lam1n / hkz / rawtail — the half
    of the candidate list that matters for C3 and the only half where no exact route
    exists — and measure, at the smallest lattices where a reduction is affordable
    (L7 d=20, L9 d=30, L11 d=40, which need no reduction above d = 40), whether their
    fibre dispersion at binary64 exceeds the two-route disagreement of their own
    evaluation. That single number decides whether the estimator question is live for
    them at all, and it is the only place A-1's answer could ever have mattered. If the
    dispersion does not exceed the route disagreement, the admissibility-gate lane has a
    NAMED OBSTRUCTION — "the observables C3 needs cannot be evaluated to better than
    their own fibre variation by any declared route" — and closing the LANE on that
    ground would be a real closure with forward guidance, not a fatigue report. If it
    does exceed it, the lane is alive and the successor assumption has a domain worth
    stating. Either way the count of screened-and-rejected criteria stays what it is: a
    fatigue report about the search, never a statement about the problem.
  artifact_paths:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-85e343/red_team_report.md
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-85e343/probes/command.txt
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-85e343/probes/probe_precision_ladder.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-85e343/probes/probe_precision_ladder_output.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-85e343/probes/probe_precision_ladder_stdout.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-85e343/probes/probe_precision_ladder_stderr.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-85e343/probes/probe_nonconstant_null.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-85e343/probes/probe_nonconstant_null_output.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-85e343/probes/probe_nonconstant_null_stdout.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-85e343/probes/probe_nonconstant_null_stderr.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-85e343/probes/probe_pgram_reach.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-85e343/probes/probe_pgram_reach_output.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-85e343/probes/probe_pgram_reach_stdout.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6b6e78/reviews/TASK-20260813-85e343/probes/probe_pgram_reach_stderr.log
```

**FOURTEEN PATHS, DECLARED GAP `G-1`.** The dispatch queue declares one artifact path
for this task. The ledger archive `TASK-20260813-3dfbdb` must extend its declared set by
**exactly the thirteen additional paths listed above and by nothing else** before it
stages. The `BATCH-4ed139` red team flagged this as its `O-9` and that archive verified
at 46 of 46; this is the fourth occurrence of the same declared gap, and it is listed
here explicitly for the same reason.

---

## 1. WHAT WAS READ, AND WHETHER IT WAS READ COMMITTED OR UNCOMMITTED

**Every producer artifact I read was read COMMITTED, and I verified both archives
myself rather than accepting the Coordinator's statement of them.**

| artifact | commit | state |
|---|---|---|
| `prereg.md` (PREREG-2) | `60ac81998` | **COMMITTED**, blob sha256 equals the working tree and the `prereg_sha256.txt` sidecar |
| `prereg_sha256.txt` | `60ac81998` | **COMMITTED** |
| `archives/TASK-20260813-502381/snapshot-receipt.json` | `60ac81998` | **COMMITTED** |
| `measure_a1.py`, `results_a1.json`, `report_a1.md`, `command.txt`, `run_manifest.yaml`, `stdout.log`, `stderr.log`, `rerun_probe_precision_null_*` (3) | `4e466c6bf` | **COMMITTED**, all ten declared hashes verified against the commit's blobs |
| `archives/TASK-20260813-48240d/snapshot-receipt.json` | `4e466c6bf` | **COMMITTED** |
| `dispatch_queue.json`, all seven `task_card.md` | earlier commits on `HEAD` | **COMMITTED** |
| `BATCH-4ed139` red team report, `probe_precision_null.py`, `probe_argset.py`, `measure_gvar2.py`, `measure_falserefusal.py`, `probe_nullroute.py` | earlier commits on `HEAD` | **COMMITTED** |
| `AGENTS.md`, `docs/inventor-protocol.md`, `agents/red-team.md`, `ledger/decisions/DEC-20260808-05b684.yaml`, `DEC-20260812-781961.yaml` | earlier commits on `HEAD` | **COMMITTED** |
| **my own report and four probe files** | none | **UNCOMMITTED**, and the sole carriers of their own evidence until `TASK-20260813-3dfbdb` (PD-4, open) |

### 1.1 The two archives, verified BY ME

The Coordinator's envelope asserts 3 paths and 11 paths. **A Validator in this goal has
already proved a Coordinator git claim false once, so I checked both in both
directions:**

* `60ac81998` — `git show --name-status` lists **exactly 3 added paths**: the receipt,
  `prereg.md`, `prereg_sha256.txt`. The receipt declares `declared_path_count: 3` with
  2 hash entries, the third being the receipt inside its own commit (the mandatory
  `commit_sha: null` pattern). Both declared hashes equal the committed blobs, and both
  equal the working tree. **ZERO producer artifacts in the commit** — the split-producer
  notarization property holds. Parent `5f1ed1e8f`, ancestor of `HEAD`: verified.
* `4e466c6bf` — **exactly 11 added paths**, all under `tasks/TASK-20260813-2ce014/` plus
  the receipt. The receipt declares `declared_path_count: 11` with 10 hash entries; all
  10 equal the committed blobs and all 10 equal the working tree. The eleventh is the
  receipt. Parent `040a52a8c`, which is the `git_revision` the producer's manifest and
  `results_a1.json` record as HEAD at run time. Ancestor of `HEAD`: verified.
* `HEAD` at review time `e7b3d2ace`; `git status --porcelain --untracked-files=no` is
  **empty**, so no producer artifact was modified after its commit. The only untracked
  path is my own review directory.

**Change-set equality holds in both directions at 3/3 and 11/11, and every declared
hash matches. I found no discrepancy in the Coordinator's git claims for this batch.**

---

## 2. THE HEADLINE: DOES THE CLAUSE READ A REPRESENTATION, OR IS 1,416 AN R4 DEFECT?

### 2.1 First, the count is real — I reproduced it

Rebuilding the 324 determinant-only blocks from the frozen seeds and scoring them
through the **imported** committed `var_f_from_cells` gives **1,416 changing cells in
49 blocks, `R4_gram_half_slogdet` = 1,396 and `R2_QR_of_BT` = 20, every other declared
route 0** — the lead's numbers exactly, block count included. That is a strong
independent check on the whole measurement chain: same bases, same clause, same counts.

### 2.2 The distinguishing object, built: a third rung

The two explanations the task card names are **not** mutually exclusive, and the way to
separate them is to ask what the quantity should do when the parameter meant to destroy
it increases. The parameter is precision. PREREG-2 has two rungs; **I built a third**.
For these frozen families exact arithmetic is available in closed form —
`log|det B| = (d-k) log q` — and at exact arithmetic **every route collapses to one
value**, so the third rung needs no route at all. (A `float128` rung was attempted first
and is unavailable: `numpy 2.4.6` raises `TypeError: array type float128 is unsupported
in linalg`. **That is infrastructure signal and it is never negative mathematical
evidence**; it is recorded in `probes/command.txt` and I took the exact rung instead.)

| rung | R0 | R1 | R2 | R3 | R4 | R5 | total |
|---|---|---|---|---|---|---|---|
| binary32 -> binary64 | 0 | 0 | 20 | 0 | **1396** | 0 | **1416** |
| binary64 -> **EXACT** | 0 | 0 | **228** | 0 | **228** | **228** | **684** |
| binary32 -> EXACT | 0 | 0 | 208 | 0 | 1624 | 228 | 2060 |

**THE MIDDLE ROW IS AGAINST MY OWN THESIS AND I REPORT IT FIRST.** The verdict changes
do **not** collapse at the higher rung. 684 cells change verdict between binary64 and
exact arithmetic, spread **evenly** over three routes at 228 each, with R4 holding no
privileged position at all. So *the committed VAR-F clause reading a representation
rather than an observable is NOT an R4-at-binary32 artifact.* The producer's
`AM-18(b)` sentence is supported.

### 2.3 What IS route-specific: the number itself

Two different mechanisms are being summed into one count.

* The **1,396 + 20** at the binary32 rung are the **scaled-dispersion** path: route noise
  inflates `s_c^fib` above `tau_var * R_{d,k}`. `R4` forms `B B^T` at the working
  precision, and **`max|B B^T|` exceeds `2**24` — the largest integer binary32
  represents exactly — at 10 of 10 lattices**, by 1 to 5 bits. Measured consequence:
  R4's absolute error against the exact `log|det B|` at binary32 is **4.581 to 204.2** on
  values of 48.66 to 811.0, a **relative error of 4.0% to 63%**, against 7.105e-15 to
  9.095e-13 for R1 at binary64. This is arithmetic about the declared family and needed
  no run at all.
* The **684** at the exact rung are the **bit-identity** path at `scale_degenerate`
  cells, confined to `rdet` and `X_parfree` — the two candidates that do not depend on
  `beta`, so their per-lattice `R_{d,k}` is 0 and `VAR_F` is decided by `bit_identical`
  over eight float values. **That mechanism is PROMOTED in `KN-FIND-9d44b4` and is not a
  new result of this batch or of this probe**; my probe reproduces it and extends it to
  `X_parfree`, the Validator's blind null.

**The nearby object separates the mechanism further.** Forming the *same* Gram exactly in
`int64` and casting the finished matrix to binary32 leaves **1,293 of the 1,396**
changes. Exact accumulation removes only 7.4%. **R4 is not badly implemented**: the
defect is that a Gram of these lattices is not representable in binary32 at all.

**CONCLUSION, NARROWEST FORM.** The phenomenon is real and survives the parameter that
should destroy it. The *number* 1,416 is a joint function of its route set and its
precision pair — a different pair gives 684 with a completely different concentration —
so it must be cited with both named in the same sentence. That is PREREG-2 §4's own
`C-1` lesson, applied to a count rather than to a verdict, and it is not yet applied to
it.

---

## 3. THE FALSIFIERS' REACHABILITY, ONE BY ONE, WITH THE PARAMETER VALUE

`AM-18(d)` forced published reachability on guards. Applied to falsifiers:

| falsifier | reachable before the run? | at what parameter value |
|---|---|---|
| `FC-1` | **UNAVOIDABLE at 5 of 10 lattices** | Reachable-and-avoidable requires tolerance > `max|RQ-RG|/2`. Measured max is **1.5008e-09** (L5); the frozen tolerance is **1e-10**, unreachable by **15.008x**. Unreachable at L2, L5, L8, L10, L12 — every lattice with `k > d-k`. |
| `FC-2a` | reachable, and it fired | Fires wherever the binary32 estimate of a true-zero dispersion lands on exactly 0 while binary64 returns rounding noise. 4,788 eligible cells, 153 fired (3.2%), all on R2 (9.6% of that route's eligible cells), **153 of 153 with `rho(binary32) = 0.0` exactly**, `rho(binary64)` between 9.514e-15 and 5.109e-14. Whether a given cell fires is a rounding coincidence — hence the 5 / 98 / 50 replicate spread. |
| `FC-2b` | **NOT REACHABLE — it is not a falsifier** | §3.3 certifies CONSTANT iff the 8 exact values are **equal**; equal values have sd exactly 0, so `rho > 0` under the exact route is impossible by the certification's own definition. It fired at 60 decimal digits only because the *variance computation* rounded; at 240 it cannot. Its non-firing is evidence about the statistic's arithmetic and about nothing else. |
| `FC-3a` | reachable, and it fired | Fires when the injected fibre dispersion falls below the route's binary32 noise floor. Boundary for the R0-type routes: `c*` between **6.005e-08 and 1.180e-06**. On R4 it fires up to `c = 1e-1` because R4's own binary32 relative noise reaches ~1.8e-1. Firing counts decay **113 -> 60 -> 11** as `c` rises through 1e-3, 1e-2, 1e-1 — the decay a real precision effect must show. |
| `FC-3b` | **UNAVOIDABLE at the declared grid** | The grid contains `c = 1e-9`, at which X_hash's fibre dispersion is 5.052e-11 to 9.926e-10 against `u_32 = 5.960e-08` — **60.1x to 1179.8x below the binary32 unit roundoff**. All 354 firings are at that amplitude; at every amplitude above the roundoff, zero. |

**`T-UNSTATABLE` is nearly foreclosed by an archived artifact, as §7.2 concedes against
itself. Three of the five falsifiers are foreclosed in one direction or the other, and
§6.2's headline — "four of the five falsifiers carry no numeric constant at all" — is
true of the text and misleading about the instrument, because `FC-1` carries a tolerance
that no value could meet, `FC-2b` carries an unfrozen decimal context, and `FC-3b`'s
outcome is fixed by the amplitude grid rather than by any property of `A-1`.**

---

## 4. THE `precision_degenerate` RULE AND THE WINDOW

**The exemption is ONE-SIDED, and that is where `A-1.2` actually broke.** §1.3 exempts
cells with `rho(binary64) == 0` exactly and says nothing about `rho(binary32) == 0`. The
symmetric case is not a curiosity: it is **153 of 153** of `FC-2a`'s firings. At those
cells the true dispersion is 0 (the candidate is certified CONSTANT), the binary32
evaluation returned **exactly the right answer**, and the binary64 evaluation returned
noise at 1e-14 — and `A-1.2`'s strict decrease scores being exactly right as a
falsification. A strict-order test between two estimates of the same true zero has an
absorbing floor at 0 that the lower-precision estimator can hit; the frozen rule handles
one side of that floor and not the other. **The frozen reading binds and I apply it; the
counterfactual is stated as a counterfactual and rescores nothing.**

**Does the exemption remove the only cells where `A-1.2` could have failed?** No — the
opposite. It exempts 4,788 cells where `A-1.2` fails *trivially* (under the strict
reading, at every `R0` cell by the definition of `R0`, exactly as §6.3 predicted), and it
leaves unexempted the 153 cells where `A-1.2` fails for the *symmetric* trivial reason.
`FC-2b` still binds at the exempt cells and cannot fire there (§3, O-7). So after the
exemption, the surviving content of `A-1.2` is: one route, 153 cells, replicate-unstable
by a factor of 19.6.

**Does a defensible different window change any verdict?** No, and this is in the
producer's and the pre-registration's favour. §1.4 declared in advance that no value
between `1.000001` and `7e5` would change an archived verdict, and my measurements are
consistent with that: on the five non-R4 routes at amplitudes above the unit roundoff
the ratio is 1.000 to six digits (0/114 firing per route per amplitude), while the firing
cells have ratios of 0, or `2.5e0` to `1.17e+09`. **The window is not doing the work. The
noise floor is.** The one window-sensitive region is `X_hash[c=0.01]|R4`, where the
median ratio is 2.494 and 60 of 114 cells fire — a window of 3 rather than 2 would move
that count. It would not change any falsifier's fired/not-fired verdict, because
`FC-3a` fires on 114 of 114 cells at `c = 1e-9` on the same route regardless.

---

## 5. THE ARRANGEMENT IN WHICH THE LEAD'S CHECK COULD NOT HAVE FAILED, BOTH DIRECTIONS

**could-not-FIRE — `A-1` could never have been falsified.** Would require every declared
candidate in a single certified class, or no exact route at all, or windows wide enough
to swallow both classes. **THE BATCH DID NOT RUN IN THIS ARRANGEMENT, and it is measured
rather than asserted:** 14 candidate instances certified CONSTANT, 4 certified
NON-CONSTANT, 1 UNCERTIFIED; `FC-2b` did not fire; and the `[1/2, 2]` window sits six
orders from both archived classes. §6.2 named this correctly.

**could-not-PASS — `A-1` could never have survived. THE BATCH RAN IN THIS ARRANGEMENT,
ON FOUR COUNTS, AND §6.3 NAMED ONE OF THEM.**

1. **Named (§6.3):** at a `rho(binary64) == 0` cell the strict reading falsifies `A-1.2`
   by the definition of `R0`. Measured at 4,788 cells; exempted by the frozen reading;
   both readings printed. **This one was handled exactly as a pre-registration should
   handle it.**
2. **Unnamed:** `P-GRAM`'s tolerance is below the minimum feasible tolerance at 5 of 10
   lattices, so `FC-1` could not have failed to fire (O-1).
3. **Unnamed:** the exemption's one-sidedness, which produced 153 of 153 `FC-2a` firings
   (§4).
4. **Unnamed:** the amplitude `c = 1e-9`, 60x to 1180x below the binary32 unit roundoff,
   which produced 354 of 354 `FC-3b` firings and 684 of 868 `FC-3a` firings.

**Each of the three unnamed ones was detectable before the run with one line of
arithmetic on already-committed numbers and no compute whatever.** That is the finding,
and it is the same discipline `O-6` of `BATCH-4ed139` established for guards, owed now to
falsifiers.

---

## 6. THE TERMINATION BRANCH, CHECKED CLAUSE BY CLAUSE

* **Precedence applied, `R3-OUT-V` first.** `measure_a1.py` computes `R3_OUT_4` and
  `R3_OUT_V` before any route evaluation and returns early with `T-VOID` if it fires;
  it did not fire. ✔
* **`T-UNSTATABLE` correctly not fired.** §7.2 requires the exact route to fail for
  **EVERY** in-scope class. It failed for one of two. ✔
* **`T-A1-FALSIFIED` correctly fired.** §7.3's condition is any of `FC-1` (some but not
  all classes), `FC-2a`, `FC-2b`, `FC-3a`, `FC-3b` at any covered cell. Four fired. ✔
* **`-PARTIAL` correctly applied.** 114 uncovered cell evaluations, all `X_gso_k | RG` at
  binary32. ✔
* **No infrastructure or coverage outcome narrated into a science branch (§7.6).** The
  114 `LinAlgError` cells are recorded as numerical/infrastructure signal, are excluded
  from every falsifier, and force the suffix. ✔ (See `O-10`: the cause is a determinate
  binary32 fact rather than a host failure, and the conservative classification is
  right.)
* **Robustness:** set `FC-1` aside on `O-1`'s grounds and the branch is unchanged, since
  `FC-2a`, `FC-3a` and `FC-3b` are each independently sufficient. **My objections change
  what the branch means, not which branch fired.**

**Is it OVER-CLOSED?** As written, **no**, and §7.3 deserves credit for it: it says in
terms that falsification "does **not** mean that no finite-precision meaning exists", it
licenses a **successor assumption**, and it forbids closing, pausing or completing the
goal. A weaker reading is equally consistent with the rows and is *permitted* by the
branch: **`A-1` restricted to (a) classes certified by exact comparison rather than by a
tolerance against float routes, (b) amplitudes above the working precision's unit
roundoff, and (c) routes whose evaluation error is below the fibre dispersion, was not
tested and is not falsified by these rows.** The over-closure risk is not in §7.3; it is
in a successor decision reading "`A-1` as stated is false" as "the assumption route is
exhausted". **Premature closure is a failure mode symmetric with overclaiming, and a
count of seven instrument batches is a fatigue report about the search, not a statement
about the problem.**

---

## 7. `AM-10`, `AM-11` AND THE PARAMETER-DETERMINED CHECK

**`AM-11`, parameter-determined observables in the re-executed code path: YES, one is
admitted.** On the frozen family `F0` the modulus block is fixed, so
`|det B| = q^(d-k)` and `rdet = exp(log|det B|/d) = q^((d-k)/d)` is a **closed-form
function of `(d, k, q)` with zero between-basis variance**. This batch's own §7
recomputation admits it at **38 of 38 cells through `R2`, `R4` and `R5` at binary64**.
Under `AM-11` a gate that admits a parameter-determined observable is INADMISSIBLE and no
admissibility claim may be reported from it — and the producer reports none, correctly.
Under `VX` (`{R6_exact}` alone) `rdet` is REFUSED, so `AM-11` is satisfied **only** under
the exact-route reading. **That `rdet` is refused at 38/38 under `R6_exact` and admitted
through the float routes is PROMOTED in `KN-FIND-9d44b4`, is attributed there, and is
NOT restated as a new result of this batch.** `R0_closed_form` itself, the purest
parameter-determined route, is REFUSED at 38/38 for both candidates.

**`AM-10` and `AM-11` applied to every statistic in the batch, including mine:**

| statistic | replicated over the 3 draws? | dispersion reported? |
|---|---|---|
| VAR-F verdict changes, 1,416 | yes: 108 / 104 / 126 and 352 / 341 / 385 | yes, per fibre family ✔ |
| `FC-3a`, 868 | yes: 289 / 288 / 291 | not in the report; stable to 1% ✔ |
| `FC-3b`, 354 | yes: 116 / 119 / 119 | not in the report; stable to 3% ✔ |
| **`FC-2a`, 153** | yes: **5 / 98 / 50** | **NO — and the spread is a factor of 19.6** ✘ (`O-6`) |
| `P-SEP` K-intervals | pooled over draws | witnesses named per row ✔ |
| **my correlation r (probe 2)** | yes, 30 lattice x draw pairs | **yes — median WITH IQR and full range, never a point estimate, plus a MUST-PASS control at exactly +1.0000** ✔ |
| **my ladder counts (probe 1)** | pooled over all three draws | per-block counts retained in the output JSON ✔ |
| **my `RQ`/`RG`/exact deviations (probe 3)** | max over the 8 bases per lattice, all 10 lattices | per-lattice, no pooling ✔ |

`AM-10`(c) asks every criterion to carry a candidate that MUST PASS it. **I propose no
criterion**, so (c) is N/A for my statistics — except for the correlation instrument,
where I did declare and run one (`RG` against `RQ`, two routes for the same geometric
quantity, measured at exactly `+1.0000` with zero IQR at all 30 pairs).

---

## 8. THE CHEAPEST FALSIFICATION OF EVERY HEADLINE, WITH ITS COST

| headline | cheapest falsifier | cost | outcome when I ran it |
|---|---|---|---|
| 1,416 changing cells in 49 blocks | rebuild the 324 determinant-only blocks from the frozen seeds, score through the imported committed clause, recount | **18.2 s** | **REPRODUCED EXACTLY**, 1,416 / 49 / R4 1,396 / R2 20 |
| "1,396 on R4 means the clause reads a representation" | add an EXACT rung to the ladder | included in the 18.2 s | **the phenomenon survives** (684 changes on R2/R4/R5 at 228 each); **the concentration does not** |
| "R4 is a bad implementation" | form the Gram exactly in int64, cast, re-slogdet | included | **NO**: 1,293 of 1,396 changes remain; the Gram is not representable in binary32 |
| `FC-1` fired | compute `max|RQ-RG|/2` and compare with 1e-10 | **5.2 s** | **the bar is unreachable by any exact route at 5 of 10 lattices**, by 15.008x |
| PREREG-2 §2.9's derivation | exact rational Gram-Schmidt with no determinant used | included in the 5.2 s | **the derivation is CORRECT** (agreement 0 to 7e-59); RG is the inaccurate route |
| `FC-3a` / `FC-3b` fired | divide the injected fibre dispersion by `u_32` | **one line, ~0 s**, on committed numbers | **60x to 1180x below the unit roundoff at `c = 1e-9`** |
| `FC-2a` fired at 153 cells | count how many have `rho(binary32) == 0` exactly | **~10 s** streaming the committed JSON | **153 of 153** |
| `P-SEP` joint interval EMPTY | recompute with the sub-ulp amplitude and R4 removed | **~10 s** | **STILL EMPTY** — P-SEP survives; only the per-route half flips |
| "the certified-NON-CONSTANT class is the null by accident" | build a second, non-digest, information-free object in that class | **1.8 s** | **two built**; A-1.3 admits both |
| `T-A1-FALSIFIED-PARTIAL` is the branch | check whether any falsifier survives every objection above | ~0 s | **it does**; the branch is unchanged |
| `P-G2` HELD | check `|det B_i|` across `i` | ~0 s | constant **by construction**; PREREG-2 §6.1 already forbids citing its non-firing as a control, and I do not |

---

## 9. MEASUREMENTS THAT GO AGAINST MY OWN THESIS, AT THE SAME WEIGHT

Collected in one place so no reader has to hunt for them.

1. **The clause's precision-dependence is not an R4 artifact.** 684 verdict changes at
   the binary64 -> EXACT rung, spread evenly over three routes. My "it is one bad route"
   framing is **wrong** about the phenomenon and right only about the count. (§2.2)
2. **PREREG-2 §2.9's derivation is correct.** I attacked it with an independent exact
   method and it held to 7e-59. (`O-13`)
3. **`P-SEP`'s frozen prediction survives both of my knocks.** Dropping the sub-ulp
   amplitude and route R4 still leaves the joint intersection EMPTY. (`O-8`)
4. **`FC-3a`'s count decays with the amplitude, 113 -> 60 -> 11.** That is exactly what a
   real precision effect should do when the parameter meant to destroy it increases, and
   it is not the artifact tell.
5. **My built objects do not separate on basis-dependence.** `X_gso_k` moves under the
   same unimodular row operation at 10 of 10 lattices, so the whole candidate class is
   presentation-dependent and my "not a lattice invariant" argument does not by itself
   distinguish my objects from the real one. (`O-2`)
6. **My correlation control has poor resolution.** With 8 points per fibre the null sd of
   `r` is ~0.378, which is the observed IQR width; the measurement supports "no strong
   correlation", not "no information". (`O-2`)
7. **The producer surfaced the batch's most important limitation against itself** — the
   empty real-object class — and its OBJ-1 anticipated my `O-1` from the committed record
   before I measured it. **Three of the four counts I checked (`FC-3a`, `FC-3b`, the 1,416)
   are stable across the three replicate draws.** The one implementation defect that could
   have been tuned was disclosed, is mathematically correct, and does not change the
   correct answer (`O-14`).
8. **`FC-2b`'s domain argument cuts both ways.** It means the producer's "FC-2b did not
   fire" is not a weakness of the run; it is a property of the specification, and no
   producer could have made that falsifier informative.

---

## 10. SCOPE, BINDING CARRIES, AND WHAT THIS REPORT CANNOT DO

**SCOPE OF MY OWN MEASUREMENTS.** `q = 3329`; the ten frozen lattices at
`d in {20, 30, 40, 100, 140}` and their frozen `beta` grids; 8 bases per lattice; family
`F0` and the three fibre draws under `PIN-DET` and `PIN-DET+PIN-A00`; the six declared
float routes plus one nearby route of my own (`R4_mixed`) plus one exact rung; two
declared working precisions plus exact arithmetic; **no reduction of any kind**; exact
rational Gram-Schmidt only at `d <= 40`, basis index 0. `float32` is a knob used to move
machine epsilon and **is not a claim about any deployment**. **Every observation above is
scoped to exactly that and transports nowhere.**

**`X_lin` and `X_par` are NOT candidates of PREREG-2 §2.4** and are not added to any
candidate list — introducing or re-declaring a candidate is a Coordinator act. They are
objects built to test what `A-1` can separate, reported as a probe on my own frames, at
the scale actually run, and they rescore nothing.

**BINDING CARRIES, IN FORCE AND NOT RE-LITIGATED.** `AM-10` through `AM-18` and their
carries. **`AM-3` is NOT retired and nothing here retires it.** **`BATCH-a44d08` is NOT
rescored in any respect** and its Section C verdict and detection floors remain **VOID IN
BOTH DIRECTIONS**. **`BATCH-4ed139`, `BATCH-9e3584` and `BATCH-cbe023` are NOT
revalidated.** `AM4-OBS-1` is cited only through `KN-FIND-f38a89`. `AM-9` binds. The
`G-VAR` refusal is cited only as conditional on the frozen family `F0`. **`KN-FIND-9d44b4`
is promoted, and none of PREREG-2 §9's list is restated here as a new result of
`BATCH-6b6e78`** — in particular the float-representation character of the `F0` failure,
the `R6_exact` refusal of `rdet` at 38/38, the sixteen-decade threshold-independence, the
decorative declared argument set of the `BATCH-4ed139` implementation, and the two-sided
obstruction are **promoted, attributed and binding**, and where my §2.3 and §7 touch them
they are attributed there. **Nothing on PREREG-2 §10.1's NOT-CITABLE list is cited
anywhere in this report**: no "factor of 6 to 31" span, neither sub-6x count, no
sub-threshold count of any kind, no "genuinely cross-platform" reading, no "29 of 48"
figure, no "the obstruction is relocated", no "CONSISTENT" in either direction.
**`AGENTS.md` rule 12 is UNMET AND UNWAIVED**; independence here is **PROCEDURAL, never
model-level and never environmental**, and `O-11` records that this batch's producer and
its reviewers resolve to one model on one host. **`PD-4` is OPEN**: this report and its
four probe files sit uncommitted across a dispatch window and are the sole carriers of
their own evidence until `TASK-20260813-3dfbdb` commits them. `knowledge/INDEX.md` was
**not** written, regenerated or staged. **Nothing was committed by this task.**

**WHAT THIS REPORT CANNOT DO.** It cannot change a verdict, a falsifier count, a
prediction-register outcome or the termination branch — those are the producer's and the
Coordinator's. It cannot validate, repair or license any gate, criterion, threshold or
`K`, and it proposes none. It cannot establish that any observable carries lattice
information, and `O-2` measures how far precision-invariance is from that. It cannot
retire `AM-3`, revalidate any prior batch, or rescore `BATCH-a44d08`. It cannot say
anything about ML-KEM, about any FIPS 203 parameter set, about any attack cost or about
any cost model. **It cannot close, pause or complete `GOAL-MLKEM-005`, and closing the
admissibility-gate LANE would retire the LANE and never the goal.**

**CLAIM TIER TOY.**

---

## 11. PROVENANCE

    requested policy         review-adversarial, effort xhigh
    independent session      required and asserted
    fallback_allowed         false        degraded_allowed  false
    adapter binding          `python3 -m orchestration.adapter resolve --role red-team
                             --independent-session` -> review-adversarial ->
                             anthropic:claude-opus-5 (effort=xhigh)
    model that answered      claude-opus-5
    requested_and_resolved   AGREE
    fallback_used            false        degraded_requirements  none
    model_verified           FALSE -- no `doctor --probe` was run in this session
    independence             PROCEDURAL ONLY. AGENTS.md rule 12 UNMET AND UNWAIVED.
                             The lead producer's recorded substitution resolves to the
                             SAME model as this review (O-11), so this batch's producer
                             and reviewers are one model on one host.
    host / stack             Linux x86_64, 4 CPUs / 15 GB, one other reviewer concurrent;
                             BLAS threads capped at 2; python 3.11.15, numpy 2.4.6
    peak RSS                 NOT INSTRUMENTED -- recorded as MISSING DATA, never
                             estimated against the 4 GB budget. No MemoryError, OOM or
                             swap event was observed.
    runs                     3 probe runs, all completed, 25.2 s total against a
                             7,200 s budget
    read state               every producer artifact COMMITTED (section 1); this report
                             and its probes UNCOMMITTED (PD-4)
