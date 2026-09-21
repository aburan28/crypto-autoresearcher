# TASK-20260814-ac35d8 — Idea Generator output for GOAL-MLKEM-005 (RQ-MLKEM-001, C1-C3)

Role: idea-generator. Policy requested: `research-deep`, effort `high`
(CLAUDE.md model-policy table; frontmatter `effort: high`). No hypothesis is
created, no status is changed, no `IDEA-*` identifier is minted here (this
role holds no shell — `tools/allocate_id.py` is not run). Every proposal
below uses a placeholder id `IDEA-PENDING-N`; minting and filing under
`ledger/proposals/` is TASK-20260814-0e7de6's job, per the task card's own
declared gap G-1.

---

## 0. Two load-bearing corrections to this task's own opening brief

Per AGENTS.md's novelty-discipline and the inventor protocol's honesty
requirements, these are recorded first, before any proposal, because they
change what "at least one idea must address C2 directly" and "nothing ready
to freeze into a protocol yet" actually mean.

### 0.1 C2 is not "still-untouched." It is already MET.

`PORTFOLIO-RULING-20260814.md` and `dispatch_queue.json`'s handoff both
describe C1, C2 and C3 together as GOAL-MLKEM-005's "three still-untouched
primary completion criteria." Reading `ledger/goals/GOAL-MLKEM-005.yaml`
directly shows this is not correct for C2:

- The goal's own `completion_criteria` items text (line 1262) says C2 is
  "SATISFIED BY 'M = 1 in every standardised mode we could source.'"
- `batch_log` entry `BATCH-a51f91` (`DEC-20260805-4823db`,
  `EV-MLKEM-d146a5`) records `C2: 'MET, with its distribution restated. 24
  sourced rows carrying specification, section, bounding mechanism and
  retrieval date...'` — 2 modes normatively fix `M = 1` (R20 SSH, R21
  IKEv2, giving `G <= log2 1 = 0` there by the goal's own convexity ceiling),
  2 more are single-use with a caveat, 2 state one ciphertext per handshake
  under a reuse-permitting clause, and 8 state no count bound at all.
- Every subsequent `batch_log` entry restates `C2: MET at BATCH-a51f91,
  unchanged` — including the goal's own most recent entry, `BATCH-a5b13c`
  (line 3352), which is the batch this task's own handoff is opened
  against.
- `DEC-20260814-b0a095`'s own `binding_carries_restated_and_not_re_litigated`
  section states explicitly: *"GOAL-MLKEM-005's own untouched primary
  completion criteria (a numeric best-of-M dbeta under a named cost model;
  the projected-error-norm/Beta-law measurement on real BKZ-reduced bases)
  are NOT advanced by anything in this batch"* — naming only C1 and C3.
  Its own `next_actions` block repeats the identical two-item list twice
  more, never including C2.

So the goal's own most authoritative record (`DEC-20260814-b0a095`, decided
the same day this task opened) already treats C2 as closed and names only
C1 and C3 as untouched. The three-item framing in this task's own brief
appears to be an over-generalization of "GOAL-MLKEM-005's own untouched
primary completion criteria" into "C1, C2, C3" without checking C2's own
`criteria_state` cells. This does not change what I was asked to deliver —
the handoff is explicit that at least one idea must address C2 directly —
so `IDEA-PENDING-3` below does that, but honestly: as a bounded audit of an
**already-met** criterion, not as work that closes an open one. Its
`recommended_priority` is `low` for exactly that reason.

### 0.2 The closest existing artifact to C1/C3 is a *proposal*, not a hypothesis, and it was not in scope of the searches that produced this task.

`PORTFOLIO-RULING-20260814.md` section 2 greps `ledger/hypotheses/*.yaml`
for `best-of-M`, `Beta law`, `projected-error-norm`, `dbeta` and finds four
hypotheses, concluding "no hypothesis currently in the ledger, proposed or
otherwise, targets GOAL-MLKEM-005's C1/C3 tracked object directly." That
grep is correct as far as it goes, but it only covers `ledger/hypotheses/`.
`ledger/proposals/IDEA-20260805-3d71ca.yaml` — filed the same day the goal
was created, and explicitly named in `H-MLKEM-dc51f5`'s own mechanism text
as owning "the ciphertext-side multi-target question" — already states,
almost verbatim, GOAL-MLKEM-005's own tracked object: its
`object_first_candidate.tracked_object` is a shared BKZ-reduced basis plus
a per-target Gram-Schmidt tail profile, and its heuristic `H1` states
`||pi_{d-beta}(t~)||^2` behaves like `||e||^2 * Beta(beta/2, (d-beta)/2)` —
the exact object and the exact distribution named in
`ledger/goals/GOAL-MLKEM-005.yaml`'s own `objective` and tracked-object
fields. It already carries a complete `proof_search_map`, three named
`heuristic_assumptions` with validation plans, a `minimal_test` with five
named controls, `falsification_conditions`, `target_complexity`,
`dominated_by` and `sota_delta`. It has never been converted to a
hypothesis and does not appear in any batch's `active_hypothesis_ids`, in
`DEC-20260814-b0a095`'s `target_ids`, or in the Portfolio Ruling.

I am not filing a duplicate of `IDEA-20260805-3d71ca`. AGENTS.md's novelty
discipline and the inventor protocol's §2 lossy-projection test both cut
against restating an already-complete proposal under a new id. Instead,
each of the four ideas below is checked explicitly against it, and where an
idea builds on it, that is stated as `novelty_status: adaptation` with the
specific delta named. The ranking rationale in section 6 states plainly
that `IDEA-20260805-3d71ca` itself — not any idea in this document — is the
single highest-value, lowest-latency action available to whichever
Coordinator session next opens `/design-experiment` on this goal, because
it already clears the schema bar this task's own `completion_gate` holds
new proposals to.

---

## 1. Novelty-check method (so `novelty_status` is not asserted from memory)

Checked this session, all read in full before any proposal below was
drafted: `ledger/goals/GOAL-MLKEM-005.yaml` (`research_goal` header,
`completion_criteria`, `batch_log` — all thirteen entries' `criteria_state`
grepped, the three most relevant read in full); `ledger/questions/
RQ-MLKEM-001.yaml`; `ledger/hypotheses/H-MLKEM-dc51f5.yaml` and
`H-MLKEM-11aabf.yaml` (full text, as the handoff required); `ledger/
decisions/DEC-20260814-b0a095.yaml` (full text); `PORTFOLIO-RULING-
20260814.md` (full text); `ledger/proposals/IDEA-20260805-3d71ca.yaml`
(full text, found via grep, not named in the handoff); a grep of `ledger/
proposals/*.yaml` for `projected-error|pi_{d-beta}|Beta\(|order statistic|
best-of-M` (22 files matched; the other 20 were skimmed for the matched
term's context and are not on-object — mostly incidental "GSA"/"best of"
matches in unrelated ML-KEM/AES/other-curve proposals); a grep of
`knowledge/` for the same and adjacent terms (41 files matched, dominated
by unrelated literature notes; none found describing a discreteness floor,
a census-grounded C1 bound, or a GSA-profile covariate for this specific
object); `docs/inventor-protocol.md`, `docs/target-result-profile.md`
(read via AGENTS.md's embedded summary and the Portfolio Ruling's own
citations — full standalone read not repeated this session given the
budget), `templates/research-records.md` (full text), `agents/
idea-generator.md` (full text). **No external web search was run this
session** — novelty-checking time went into the in-repo corpus, which the
handoff's own `context_and_corrections` treats as the load-bearing check.
This is disclosed, not papered over: no idea below is labelled `known`, and
external-literature novelty is inherited from `IDEA-20260805-3d71ca`'s own
2026-08-05 check (Bernstein ePrint 2022/1580; Duman-Hoevelmanns-Kiltz-
Lyubashevsky-Seiler CCS'21; `KN-LIT-7661`, itself flagged there as unread)
rather than independently re-verified here.

---

## 2. IDEA-PENDING-1 — Census-grounded C1 bound via the GAIN(u) balance argument, reparametrized to the ciphertext-side Beta order statistic

```yaml
idea:
  id: IDEA-PENDING-1
  question_id: RQ-MLKEM-001
  title: >-
    A zero-lattice-compute C1 deliverable: evaluate the best-of-M block-size
    saving at the REAL M values GOAL-MLKEM-005's own (already-met) C2 census
    reports, using H-MLKEM-dc51f5's exact GAIN(u) balance argument
    reparametrized from the key-side CBD-sum order statistic to the
    ciphertext-side projected-error-ratio (Beta) order statistic, with the
    C1-criterion's own mandatory f''-curvature sensitivity table.
  class: composition

  claim: >-
    GOAL-MLKEM-005's completion criterion C1 asks for "a stated numeric
    bound, with derivation, on the dbeta ... attainable by best-of-M
    selection at the M established in C2," explicitly allowing X = 0, and
    explicitly requiring an f'' sensitivity table wherever the figure
    depends on BKZ-profile curvature. This can be produced today, at zero
    lattice-reduction compute, by composing two already-existing,
    already-validated program artifacts that have never been combined: (a)
    H-MLKEM-dc51f5 Part C's exact balance argument GAIN(u) = (c_T
    gamma/2) u + log2 p(u), which converts a fractional shortfall u in a
    norm statistic into a bit saving net of the failure tax, evaluated
    against an EXACT (not Gaussian-approximated) left tail; and (b)
    IDEA-20260805-3d71ca's H1, which gives p(u) for the CIPHERTEXT-side
    object as the order statistic of Beta(beta/2, (d-beta)/2) rather than
    dc51f5's key-side CBD-sum order statistic. Composed and evaluated at the
    actual M values EV-MLKEM-d146a5's census reports (M = 1 for the two
    normatively single-use rows; the stated numeric caps for the
    caveated/per-handshake rows; left explicitly open/parametric for the 8
    unbounded rows), this directly answers C1 in the form the criterion
    demands, with the required f''-sensitivity table attached, rather than
    at the illustrative M = 2^20/2^30 both dc51f5 and 3d71ca used. The
    claim under test is quantitative, not qualitative: at every census
    row with a stated finite M, either GAIN(u*) at the interior optimum is
    materially negative (X = 0, best-of-M ciphertext selection buys nothing
    at real deployment M) or it is materially positive by a stated number
    of bits with a stated model-assumption share Y — both are complete,
    citable C1 answers.

  object_first_candidate:
    tracked_object: >-
      The pair (the GAIN(u) balance functional itself, as a closed-form
      function of one real parameter u; the census-derived support set of M
      values it is evaluated at). This is a THIRD object, distinct from
      both parent artifacts' own objects: dc51f5 tracks GAIN(u) evaluated at
      illustrative (beta, d) rows with u drawn from the KEY-side CBD-sum
      order statistic across N INDEPENDENTLY KEYED sessions (different
      bases); 3d71ca tracks the single-draw law of R = ||pi_{d-beta}(e)||^2
      / ||e||^2 itself, at an illustrative M. This idea tracks neither raw
      statistic — it tracks the SAME balance functional dc51f5 built,
      re-fed a different order statistic (3d71ca's Beta law, for CIPHERTEXTS
      under ONE shared basis, matching GOAL-MLKEM-005's own tracked object
      exactly) and evaluated at census-real M rather than illustrative M.
    established_families_off_limits: >-
      Inherited from IDEA-20260805-3d71ca's own declared list (dual-sieve +
      FFT distinguisher; estimator cost-table/primal_bdd-vs-matzov
      differencing; hybrid MITM/decoding; coefficient-isometry
      preprocessing amortisation; class-group/unit-lattice/PIP; decryption-
      failure/failure-boosting; implementation side channels), plus
      H-MLKEM-dc51f5's own object (KEY-side selection across independently
      keyed sessions) declared off-limits as this idea's primary lens: this
      idea reuses dc51f5's BOOKKEEPING TEMPLATE only, never its object.
    newness_score: >-
      Repackaging at the level of each individual ingredient (the GAIN(u)
      functional is dc51f5's; the Beta order statistic is 3d71ca's; the
      census numbers are EV-MLKEM-d146a5's). New at the level of the
      COMPOSITION and at the level of the INPUT (real census M rather than
      an illustrative row) and the DELIVERABLE (an f''-sensitivity table,
      which neither parent produces and which C1's own criterion text
      explicitly requires). No proposal, hypothesis or knowledge entry
      found this session performs this composition.
    testability_score: >-
      High for the derivation itself (pure closed-form arithmetic, no
      sampling, no lattice reduction — verifiable by hand or by a short
      script in minutes). The GENUINE uncertainty this idea inherits and
      does not resolve is whether the Beta order statistic (3d71ca's H1) is
      itself correct at ML-KEM-relevant scale; this idea's own numeric
      output is explicitly staged as PROVISIONAL, using the THEORETICAL
      Beta CDF now, and re-computable once IDEA-PENDING-2 or 3d71ca's own
      C3 measurement lands an empirical tail.
    survival_score: >-
      The object survives exactly as long as (i) the census's own M values
      remain the cited ones and (ii) the Beta order statistic is treated as
      provisional rather than confirmed. It dissolves the moment either
      changes — a future census update (IDEA-PENDING-3) or a measured tail
      departure (IDEA-PENDING-2, IDEA-PENDING-4, or 3d71ca's own C3 arm)
      forces a re-computation, which is by design: this idea is meant to be
      cheap to redo, not a one-shot answer.

  mechanism: >-
    Fix a census row's M. Under the Beta order-statistic model, the
    best-of-M achieved ratio R_min(M) has CDF F_M(x) = 1 - (1 -
    I_x(beta/2, (d-beta)/2))^M where I_x is the regularized incomplete beta
    function — the direct M-fold generalization of dc51f5's own p(u) but
    with the CBD-sum tail replaced by the Beta tail. The fractional
    shortfall u(M) this induces in ln||pi_{d-beta}(e)|| is then fed,
    UNCHANGED, into dc51f5's own gamma-based conversion beta(u) = beta_full
    - gamma u/2, and GAIN(u) = (c_T gamma/2) u + log2 p(u) is maximised over
    u exactly as dc51f5 Part C already did, replacing dc51f5's own D-fold
    CBD convolution for p(u) with the Beta order-statistic CDF above. Every
    other piece of dc51f5's derivation (the cost convention that a failed
    attempt costs full price; c_T = 0.292, RELAYED not re-derived; the
    gamma_crit threshold test) is reused as-is, because it is a property of
    the BALANCE, not of which statistic feeds it. The f''-sensitivity table
    C1 requires is produced by recomputing GAIN(u*) under a stated +/-20%
    perturbation of gamma (mirroring dc51f5's own disclosed fragility: its
    gamma/gamma_crit ratio sits at 0.55-0.69, "a factor 1.45 to 1.81 in
    gamma flips the verdict") and reporting whether the census-row verdict
    (X = 0 vs X > 0) is stable under that perturbation.

  novelty_status: adaptation

  lossy_projection_identifiability_audit:
    projection: >-
      The full triple (basis B, the M-target population, the census's
      sourced M distribution) --> the single scalar GAIN(u*) per census row,
      plus its perturbation-stability flag.
    what_is_discarded: >-
      Everything about individual targets' identities, the exact shape of
      the Beta CDF away from its optimum, and every census row's own
      qualitative sourcing detail (specification text, bounding mechanism) —
      retained only as the row's label, not as an input to the number.
    why_genuinely_lossy: >-
      Many different (basis, M-population) pairs with the same order-
      statistic tail and the same M produce the identical GAIN(u*); the
      fibre is large and nothing about which targets exist is recoverable
      from the scalar.
    why_compatible_with_the_operations: >-
      GAIN(u*) is exactly the quantity the C1 criterion asks for (a bit
      saving under a named cost model); the projection commutes with the
      only operation this idea performs on it (evaluation at a set of M
      values and a +/-20% gamma perturbation), so the retained scalar
      propagates deterministically through both.
    is_it_only_a_change_of_coordinates: >-
      No — a change of coordinates would need to recover the full CDF or
      the target population from GAIN(u*) alone, and it cannot: GAIN is a
      single real number, the input space is infinite-dimensional.

  proof_search_map:
    bottleneck: >-
      Whether the interior optimum of GAIN(u) is positive at ANY census-real
      M, under the ciphertext-side Beta order statistic rather than the
      key-side CBD-sum order statistic dc51f5 already showed does not clear
      it (ratio 0.554-0.689 against gamma_crit there). Removing this
      bottleneck (showing GAIN(u*) > 0 at a real M) is the entire content of
      a positive C1 answer; failing to remove it (GAIN(u*) <= 0 everywhere)
      is the entire content of the X = 0 answer, equally complete.
    baseline_embedding:
      parameter_slice: >-
        M = 1 (the two normatively single-use census rows, R20/R21).
      reproduction_check: >-
        At M = 1, p(u) collapses to the M = 1 marginal and the Beta
        order-statistic CDF reduces to the plain Beta CDF; GAIN(0) = -1
        exactly, matching dc51f5's own M=1/N=1 reproduction check
        (GAIN(0) = -1 there too, since both share the identical "full price
        for a failed attempt" convention). An implementation returning
        anything else at M = 1 has an off-by-one and must be fixed before
        any census-row number is trusted.
    observation_collision:
      observable: >-
        GAIN(u*) and its perturbation-stability flag, per census row.
      distinct_preimage_search: >-
        As in dc51f5, gamma_crit depends on (D, kappa) only through
        r = sqrt(D/kappa) for the CBD-sum case; here the analogous
        collision is that GAIN(u*) depends on (beta, d, M) only through the
        Beta order-statistic tail and gamma, so two structurally different
        census rows sharing the same (beta, d, M) triple would report the
        identical GAIN(u*) — the observable does not identify the row, only
        the triple. This is expected and harmless (the triple, not the
        row's prose, is what the physics depends on) and is stated in the
        run record rather than assumed away.
    constructive_transforms:
      - transform: representation_reduction
        proposed_object: >-
          Replace dc51f5's CBD-sum order-statistic feed to GAIN(u) with
          3d71ca's Beta order-statistic feed, holding the balance functional
          itself fixed.
        predicted_gain: >-
          Converts two disconnected, illustrative-parameter analyses into
          one census-grounded, criterion-shaped answer at zero additional
          compute.
    quantifier_order: >-
      FOR EACH census row with a stated finite M (not "for all M" — the
      unbounded rows are reported parametrically, as GAIN(u*) as a function
      of M, never extrapolated to a fabricated number), EXISTS a GAIN(u*)
      value and a stability flag under the stated +/-20% gamma perturbation.
      The witness u* is computed, not assumed, and the claim is never
      extended past the rows actually in EV-MLKEM-d146a5.
    method_ceiling:
      strongest_certifiable_claim: >-
        At most a labelled MODEL READOUT (not a measurement) of the C1
        bound under the stated cost convention, the RECALLED-UNVERIFIED
        2016 uSVP condition form (dc51f5's own stage-0 risk, inherited
        unresolved here), and the THEORETICAL (not yet empirically
        confirmed) Beta order-statistic tail. It cannot certify an actual
        attack cost and cannot resolve whether the Beta tail law itself
        holds — that is IDEA-PENDING-2's and 3d71ca's own C3 job.
      nearby_object_control: >-
        The nearby object on which this method's conclusion is known to be
        VACUOUS is any census row with M = 1: GAIN(0) = -1 there by
        construction, so the method correctly reports X = 0 rather than
        manufacturing a nonzero figure from a degenerate input.
    proof_obligations:
      - claim: GAIN(0) = -1 exactly at M = 1, both order-statistic models.
        responsibility: baseline
      - claim: >-
          The Beta order-statistic CDF F_M(x) = 1 - (1-I_x(beta/2,
          (d-beta)/2))^M is the correct M-fold extension of 3d71ca's H1.
        responsibility: correctness
      - claim: gamma's conversion is reused unmodified from dc51f5 Part C.
        responsibility: interface
      - claim: >-
          Every census row's own GAIN(u*) is reported with its
          +/-20% gamma-perturbation stability flag, never bare.
        responsibility: scope
    not_applicable_reason: null

  predictions:
    - metric: GAIN(u*) at the two M=1 census rows (R20, R21)
      direction: different
      minimum_effect: >-
        Exactly -1 bit, forced by the M=1 boundary reproduction check; this
        is the trivial X = 0 branch and must be reported, not omitted, per
        C1's own "X may be 0" allowance.
    - metric: >-
        GAIN(u*) at the census's largest STATED finite M (among the
        caveated/per-handshake rows)
      direction: different
      minimum_effect: >-
        NO NUMBER IS PRE-COMMITTED here (none has been computed; committing
        one without running the arithmetic would be a fabricated
        prediction). The pre-registered decision rule is: >= 2 bits at
        stable-under-perturbation is citable as a genuine C1 finding
        (matching 3d71ca's own materiality bar); < 2 bits, or a sign that
        flips under the +/-20% gamma perturbation, is reported as X = 0 /
        not citable without the caveat, per the same discipline dc51f5 used
        for its own margin (1.45-1.81x).
    - metric: >-
        f''-sensitivity: the fraction of census rows whose X=0-vs-X>0
        verdict flips under a +/-20% perturbation of gamma
      direction: lower
      minimum_effect: >-
        Report the exact fraction; 0% (no verdict flips) supports citing a
        stable C1 bound, any nonzero fraction requires the flipped rows to
        be reported with the caveat attached, exactly as
        EV-MLKEM-159715.m2_magnitude_corrected_citable_wording already
        established the precedent for narrowing a default citation.

  minimal_test:
    design: >-
      A single short, deterministic script (no lattice reduction, no
      sampling): (1) load EV-MLKEM-d146a5's 24-row census table (or its
      restated distribution from GOAL-MLKEM-005.yaml's own batch_log if the
      raw table needs re-fetching); (2) for each row with a stated finite M,
      compute F_M and its interior-optimum GAIN(u*) via dc51f5's Part C
      formula, reusing c_T = 0.292 and the three illustrative (beta, d) rows
      already computed there (or the actual FIPS 203 beta(key-side) figures
      H-MLKEM-11aabf's own C1-Stage-B already computed: 389/606/855 at
      ML-KEM-512/768/1024, which are a strictly better baseline than
      dc51f5's own "illustrative, recalled" rows and should be preferred
      once stage-0 verification of the 2016 condition form clears); (3)
      recompute at gamma * 0.8 and gamma * 1.2 for the sensitivity table;
      (4) for the 8 unbounded rows, report GAIN(u*) as a function of M over
      a stated grid (e.g. M in {2^10, 2^20, 2^30, 2^40}) rather than a
      single fabricated number.
    controls:
      - >-
        M=1 reproduction check (GAIN(0) = -1 exactly) — REQUIRED to pass
        before any other row is reported, matching both parent artifacts'
        own M=1/N=1 boundary checks.
      - >-
        Cross-check against dc51f5's own three illustrative-row GAIN(u*)
        values (-0.987/-0.991/-0.992 bits at u<=0.001) by running THIS
        idea's own script with the CBD-sum order statistic substituted back
        in for the Beta order statistic — must reproduce dc51f5's own
        numbers to within numerical tolerance, or the reparametrization has
        a bug.
    required_metrics:
      - GAIN(u*) and u* per census row (finite-M rows) and per grid point
        (unbounded rows)
      - the f''-sensitivity flag per row
      - the M=1 and dc51f5-reproduction control outcomes

  falsification_conditions:
    - >-
      The dc51f5-reproduction control (Beta statistic swapped back for the
      CBD-sum statistic) fails to reproduce dc51f5's own published numbers
      to numerical tolerance — the reparametrization is broken and no
      census-row number may be reported until fixed.
    - >-
      GAIN(u*) is positive and stable-under-perturbation at ANY census-real
      M — this is the outcome C1's own bound would then have to report as
      X > 0, promoting the lane's priority, exactly as dc51f5's own F1
      condition (gamma/gamma_crit >= 1) would have promoted its lane.
    - >-
      The M=1 boundary check fails (GAIN(0) != -1) — implementation defect,
      no row is reportable until fixed.

  confounders:
    - >-
      Inherits dc51f5's own unresolved "stage 0" risk in full: the 2016
      uSVP condition's exact published form was never read by the author of
      dc51f5, and gamma is entirely a consequence of it. This idea does not
      re-verify that source; it inherits the risk and states so.
    - >-
      Inherits 3d71ca's own H3 risk (shared-basis exchangeability across
      the M targets is unproven) — if H3 fails materially, the Beta
      order-statistic feed itself is wrong and this idea's numbers are
      provisional twice over, not once.
    - >-
      The census's 8 "no bound stated" rows are reported parametrically
      specifically BECAUSE treating "no bound" as an actual numeric M would
      fabricate a number the source specifications do not state.

  interpretation_limits:
    - >-
      CLAIM TIER: derivation, not measurement. No lattice reduction, no
      sampling, no attack is run or claimed. Labelled a MODEL READOUT
      throughout, matching C1's own explicit textual requirement.
    - >-
      Every number this idea would produce is PROVISIONAL on the Beta
      order-statistic tail (3d71ca's own H1) being at least approximately
      correct; it must be re-run once IDEA-PENDING-2, IDEA-PENDING-4, or
      3d71ca's own C3 experiment lands an empirical reading, and any
      citation of a number from this idea before that must carry that
      caveat.
    - >-
      Does not touch, re-score, or supersede dc51f5's own PART C KEY-side
      finding (gamma/gamma_crit 0.554-0.689 there) — that remains a
      separate, unadvanced object.

  heuristic_assumptions:
    - id: H1
      statement: >-
        The M-fold order statistic of 3d71ca's H1 Beta model correctly
        composes with dc51f5's own gamma-based Delta-beta conversion — i.e.
        that a fractional shortfall u derived from the BEST of M
        ciphertext-side draws converts to a block-size reduction via the
        SAME first-order formula dc51f5 derived for a single key-side norm
        shortfall.
      rigorous_support: >-
        The Delta-beta conversion itself is exact GIVEN the 2016 condition's
        form (dc51f5's own disclosure); composing it with a different order
        statistic changes only WHICH random variable u is drawn from, not
        the conversion's own validity, so no new heuristic is introduced
        beyond the two already-named ones (dc51f5's gamma-form risk;
        3d71ca's H1 Beta-law risk) — this assumption is that composing them
        introduces no THIRD, independent failure mode, which is a
        structural claim checkable by the M=1 and dc51f5-reproduction
        controls above.
      supporting_results: []
      validation_experiment_ids: []
      falsification_condition: >-
        The dc51f5-reproduction control (above) fails — direct evidence a
        third failure mode was introduced by the composition.

  target_complexity:
    time_exponent: >-
      UNCHANGED, 2^{0.292 * beta(u*)}. This idea produces no exponent claim
      and cannot: GOAL-MLKEM-005's own ceiling_known_in_advance proves
      dbeta/beta ~ 0.29*sqrt((1-rho)*ln M / beta), so an exponent would need
      ln M = Theta(beta) (~2^Theta(600) ciphertexts under one key), far
      beyond any census-real M this idea evaluates. G <= log2 M holds
      unconditionally by convexity regardless of what this idea computes.
    memory_exponent: UNCHANGED, 2^{0.2075 * beta(u*)}. Not moved by this idea.
    best_known: >-
      Single-target primal uSVP at beta_full for the named parameter set
      under the pinned cost model (c_T = 0.292, RELAYED from KN-TECH-044/040,
      not re-derived here).
    hidden_overhead: >-
      The 2016 condition's own unverified error (dc51f5's stage-0 risk); the
      first-order expansion of beta(u) hides O(u^2), inherited unmodified
      from dc51f5; the Beta order-statistic model's own unverified accuracy
      at ML-KEM scale (3d71ca's H1 risk).
    tradeoff_note: >-
      Trades DATA (M ciphertexts, already-collected per C2's census, not an
      operational cost this idea charges) for TIME, exactly as 3d71ca's own
      target_complexity states; not a time-memory tradeoff. GOAL-MLKEM-005's
      ceiling caps this trade's entire value at log2(M) bits regardless of
      how the trade is structured.

  dominated_by: >-
    Neither IDEA-20260805-3d71ca (illustrative M only, no census-grounding,
    no f''-sensitivity table) nor H-MLKEM-dc51f5 (key-side object,
    illustrative rows, no census-grounding) performs this specific
    composition; neither dominates it. No external row of the frontier was
    checked this session beyond the in-repo corpus (section 1 above) — this
    is disclosed, not a claim of a clear frontier.
  sota_delta: >-
    Not an attack-cost claim. Procedural delta only: turns two existing,
    already-validated derivations into GOAL-MLKEM-005's own C1 deliverable
    at zero incremental lattice compute, closing (or explicitly bounding at
    X=0) the single most decision-relevant of the goal's three completion
    criteria first.

  estimated_cost:
    implementation: low
    compute: low
  recommended_priority: high
```

---

## 3. IDEA-PENDING-2 — Order-statistic floor test: does the projected-error ratio's deep left tail obey the continuous Beta law, or does CBD/compression discreteness impose a hard floor?

```yaml
idea:
  id: IDEA-PENDING-2
  question_id: RQ-MLKEM-001
  title: >-
    Testing a second, distinct candidate mechanism for C3's own "fails by a
    measured factor" branch: a combinatorial floor on the best-of-M
    projected-error ratio, from the CBD error's finite alphabet, rather than
    basis-error correlation (3d71ca's own H3).
  class: control

  claim: >-
    IDEA-20260805-3d71ca's own H1/H3 test whether R = ||pi_{d-beta}(e)||^2 /
    ||e||^2 follows the CONTINUOUS Beta(beta/2, (d-beta)/2) law and whether
    any departure correlates across targets sharing one basis. Neither tests
    a THIRD, structurally distinct failure mode: because e is drawn from a
    CBD(eta) alphabet of finite support (each coordinate in
    {-eta,...,eta}), the set of achievable values of R for a FIXED basis is
    itself finite, so the running minimum R_min(M) over M independent draws
    CANNOT decay below some basis-specific floor r_min(B) > 0, however large
    M grows — whereas the continuous Beta model predicts R_min(M) -> 0 as
    M -> infinity with no floor. The claim under test: does the empirical
    decay of R_min(M), over the reachable range of M (up to ~2^20-2^22, per
    3d71ca's own minimal_test budget), show measurable deceleration
    relative to the Beta-law extreme-value rate — and, independently and at
    zero sampling cost, does an exact brute-force/branch-and-bound search
    for the minimum achievable R over the FULL finite CBD support at toy
    dimension (d <= ~20-30, tractable exactly) sit ABOVE the Beta law's own
    prediction at the corresponding effective M (the alphabet size to the
    power d)? Either a positive or negative answer on both fronts is a
    complete, citable contribution to C3.

  object_first_candidate:
    tracked_object: >-
      The running-minimum TRAJECTORY R_min(M) as a monotone step function of
      M (not the single-draw marginal law 3d71ca's H1 tracks, and not the
      between/within-basis variance decomposition H3 tracks), plus, at toy
      dimension only, the EXACT combinatorial minimum of R over the CBD
      alphabet's full finite support.
    established_families_off_limits: >-
      Same list as IDEA-PENDING-1, inherited from 3d71ca; additionally,
      3d71ca's own H1 (single-draw marginal comparison) and H3
      (basis-error correlation) are declared off-limits as THIS idea's own
      primary lens — this idea is deliberately not a restatement of either.
    newness_score: >-
      Genuinely new at the object level: the order-statistic TRAJECTORY
      (the sufficient statistic the best-of-M SELECTION mechanism actually
      consumes, since an attacker only cares about the running minimum as M
      grows) and the exact finite-support floor are not proposed anywhere
      found this session. Repackages 3d71ca's own experimental apparatus
      (fpylll BKZ, real CBD samplers, real FIPS 203 compression) as
      infrastructure, not as the claim.
    testability_score: >-
      High. The trajectory is a deterministic function of an already-
      generated sample sequence (no new sampling scheme). The brute-force
      floor is a bounded combinatorial search at TOY d, feasible or not
      within budget, and its feasibility is itself reported rather than
      assumed (a stated fallback to branch-and-bound with a certified gap
      is named below if exhaustive search is infeasible at the chosen d).
    survival_score: >-
      Survives exactly as long as the CBD alphabet is finite (always true)
      and the basis is fixed (as in 3d71ca). Dissolves at continuous-error
      instances by construction (see NULL-2 below) — that dissolution IS
      the discriminating test.

  mechanism: >-
    For fixed basis B, the achievable set {||pi_{d-beta}(e)||^2 : e in
    CBD(eta)^d} is finite (bounded by (2 eta + 1)^d elements, with far fewer
    DISTINCT projected-norm values after collisions). Its minimum,
    r_min(B), is a hard floor no amount of additional sampling can beat.
    The continuous Beta model has no such floor. Two independent,
    complementary checks separate "floor present" from "floor absent" at
    the reachable experimental scale: (1) STATISTICAL — fit the local decay
    rate of R_min(M) in log-log (or the Beta-appropriate) coordinates at
    each decade of M up to the tested maximum and compare it against the
    closed-form Beta extreme-value asymptotic rate; systematic deceleration
    (not noise) is the statistical signature of an approaching floor. (2)
    EXACT — at toy dimension small enough for exhaustive or certified
    branch-and-bound search (this is a NEW, small measurement, chosen
    independently of the hkz lineage's own archived toy cells, which are
    a different quantity), compute r_min(B) exactly and compare it to the
    Beta law's OWN predicted value at M = (2 eta + 1)^d (the total
    population size, so every draw has in principle been exhausted) — if
    r_min(B) sits strictly above the Beta-law's prediction at that M, the
    floor is confirmed exactly, not merely inferred from a decay-rate
    trend.

  novelty_status: adaptation

  lossy_projection_identifiability_audit:
    projection: >-
      The full sequence of M drawn error vectors --> the single monotone
      step function R_min(1), R_min(2), ..., R_min(M) --> (for the exact
      arm) the single scalar r_min(B).
    what_is_discarded: >-
      Every non-record-setting draw's own R value and identity; only the
      running minimum and its update times are retained.
    why_genuinely_lossy: >-
      Many distinct draw sequences share the identical running-minimum
      trajectory (any permutation of the same multiset of R values below
      each running record produces the same trajectory once sorted by
      arrival), so the trajectory does not identify the sequence.
    why_compatible_with_the_operations: >-
      Best-of-M SELECTION is defined exactly as "track the running
      minimum and stop improving when a decode succeeds" — the trajectory
      is precisely the sufficient statistic that operation consumes; it
      propagates deterministically because a running minimum is a
      deterministic function of the prefix of draws seen so far.
    is_it_only_a_change_of_coordinates: >-
      No. A change of coordinates would let the full sequence be recovered
      from the trajectory; it cannot be (see "what is discarded" above).

  proof_search_map:
    bottleneck: >-
      Whether the continuous Beta extreme-value law remains a valid
      description of R_min(M) at the LARGE-M end of the range any C1
      extrapolation (including IDEA-PENDING-1's own unbounded-row rows)
      would need, or whether it silently breaks down against a hard floor
      before that end is reached.
    baseline_embedding:
      parameter_slice: >-
        M = 1: R_min(1) equals the single draw, trivially, and the
        "trajectory" degenerates to a single point with no order-statistic
        content — must be excluded from any decay-rate fit as a
        degenerate case, not a data point.
      reproduction_check: >-
        At the SAME (n, beta) cells 3d71ca's own minimal_test already
        specifies, this idea's trajectory computation, run on 3d71ca's own
        NULL-2 (Gaussian, continuous, matched-variance) arm, must show NO
        measurable deceleration and NO brute-force floor above the
        Beta-law prediction (a continuous distribution has unbounded left
        support) — this is the forced-null check and it is a real check,
        not a tautology, because a bug that always reports "floor detected"
        regardless of input would fail it.
    observation_collision:
      observable: >-
        The pair (measured decay-rate deceleration, exact r_min(B) versus
        its Beta-law prediction).
      distinct_preimage_search: >-
        A floor detected by BOTH the real-CBD arm and 3d71ca's own NULL-2
        (Gaussian) arm would be a collision on the discreteness explanation:
        it would instead implicate the BASIS (overlapping with H3), not the
        error's own discreteness, since a continuous error has no
        combinatorial floor by construction. This collision is explicitly
        sought (not assumed away) and, if found, this idea's own verdict is
        downgraded from "discreteness floor" to "an unexplained floor,
        basis-effect not excluded" rather than over-claimed.
    constructive_transforms:
      - transform: observable_fiber
        proposed_object: >-
          Hold the basis B fixed; vary the forgotten structure (the
          identity of which draw achieved the running minimum, and every
          non-minimal draw). The trajectory and the exact floor are both
          intrinsic invariants of (B, the CBD alphabet) that a single-draw
          marginal law does not expose.
        predicted_gain: >-
          Separates "the Beta law is adequate everywhere reachable" from
          "the Beta law is adequate in bulk but caps out," which changes
          how far IDEA-PENDING-1's own unbounded-M rows may be
          extrapolated.
    quantifier_order: >-
      FOR the specific (n, beta, d) cells 3d71ca's own minimal_test
      specifies, EXISTS a measured deceleration statistic and an exact
      r_min(B) at the toy sub-cell chosen for brute-force search. No
      uniform claim over all ML-KEM parameter sets is made or attempted;
      any extrapolation beyond the tested cells is flagged as exactly that
      (AGENTS.md rule 7).
    method_ceiling:
      strongest_certifiable_claim: >-
        At most: a quantified floor r_min(B) at toy dimension, exactly, plus
        a statistical deceleration reading at the (n, beta) cells actually
        reached. It cannot certify the floor's value at ML-KEM dimension
        (d ~ 1000+), where exhaustive search is infeasible by construction
        — this ceiling is stated plainly, not implied away.
      nearby_object_control: >-
        The nearby object where the desired conclusion (floor exists) must
        FAIL is any CONTINUOUS error law of matched variance (3d71ca's own
        NULL-2) — it has no finite alphabet and so cannot exhibit a
        combinatorial floor by construction; this control is REQUIRED to
        pass (show no floor) before any real-CBD floor finding is
        reportable, exactly matching this program's own established
        planted-positive-control discipline (dc51f5's WK-5, this program's
        NULL-forcing convention throughout the hkz lineage).
    proof_obligations:
      - claim: R_min(M) trajectory is a deterministic function of the draw
          prefix.
        responsibility: correctness
      - claim: NULL-2 (Gaussian) shows no deceleration and no brute-force
          floor above the Beta prediction.
        responsibility: strictness
      - claim: The brute-force/branch-and-bound search at toy d either
          completes exactly or reports a certified gap, never a silent
          approximation presented as exact.
        responsibility: feasibility
      - claim: Any floor found is reported with the collision check
          (basis-effect not excluded) rather than as a clean discreteness
          verdict when NULL-2 also shows a floor.
        responsibility: scope
    not_applicable_reason: null

  predictions:
    - metric: >-
        Deceleration statistic: ratio of the measured local decay slope of
        R_min(M) at the largest reached decade of M to the closed-form Beta
        extreme-value asymptotic slope at the same M
      direction: lower
      minimum_effect: >-
        A ratio significantly below 1 (report the confidence interval over
        the >= 8 independent draws 3d71ca's own design already calls for)
        is the deceleration signature; a ratio statistically
        indistinguishable from 1 is a clean negative (Beta law adequate
        throughout the reached range) and is an equally complete result.
    - metric: >-
        r_min(B) at the brute-force toy cell, versus the Beta law's own
        predicted quantile at M = (2 eta + 1)^d
      direction: higher
      minimum_effect: >-
        r_min(B) exceeding the Beta-law prediction by any measurable, exact
        margin confirms the floor exactly; equality (within floating-point
        tolerance) refutes it at that cell.
    - metric: NULL-2 (Gaussian) floor-detection outcome
      direction: different
      minimum_effect: >-
        FORCED TO ZERO — no deceleration, no floor above the Beta
        prediction. Any nonzero reading here voids the real-arm finding as
        an instrument artifact, per the inventor protocol's controls-
        before-belief discipline.

  minimal_test:
    design: >-
      Layered directly onto 3d71ca's own minimal_test (design steps 1-2:
      real ML-KEM-shaped instances, n in {64,128}, real CBD samplers, real
      FIPS 203 compression, one BKZ-beta-reduced basis per instance, >=
      2^20 targets, >= 8 independent (key, basis) draws) with two additions:
      (a) record the RUNNING MINIMUM trajectory, not only the final-M
      distribution, and fit its local decay rate at each decade; (b) at a
      SEPARATE, smaller toy sub-cell (n <= 16-20, chosen specifically for
      brute-force tractability, a strict subset of 3d71ca's own tested
      range), exhaustively or via certified branch-and-bound enumerate the
      CBD alphabet and compute r_min(B) exactly, reporting wall-clock and,
      if exhaustive search proves infeasible, the certified gap of whatever
      bound-and-prune method is substituted.
    controls:
      - >-
        NULL-2 (Gaussian, matched variance) reused directly from 3d71ca —
        REQUIRED, forced-zero-floor check, run first.
      - >-
        NULL-3 (ephemeral arm, fresh basis per target) reused directly from
        3d71ca as a second sanity check that any floor found is not an
        artifact of basis reuse across a small effective sample.
      - >-
        Brute-force-feasibility check: report exhaustive-search wall-clock
        at increasing toy d (e.g. d in {8, 12, 16, 20}) BEFORE committing to
        a specific d for the headline floor number, so the chosen d is
        justified by measured feasibility, not guessed.
    required_metrics:
      - R_min(M) trajectory per (n, beta, arm), machine-readable
      - local decay-rate ratio at each tested decade of M, with intervals
        over >= 8 draws
      - r_min(B) exactly, at the chosen toy sub-cell, with wall-clock and
        certified-gap status
      - NULL-2 and NULL-3 floor-detection outcomes

  falsification_conditions:
    - >-
      NULL-2 shows a deceleration or a floor — the instrument is
      miscalibrated (a continuous distribution cannot have a combinatorial
      floor by construction) and no real-arm finding may be reported until
      fixed.
    - >-
      No deceleration is measured at the reached M range AND the exact
      brute-force floor equals the Beta-law prediction within tolerance —
      the discreteness-floor hypothesis is refuted at the tested scale; a
      complete, informative negative contributing directly to C3's "Beta
      tail law holds" branch.
    - >-
      A floor IS detected in BOTH the real-CBD arm and NULL-2 — the
      collision case; the verdict is downgraded to "floor present, basis-
      effect not excluded, discreteness not established," per the
      observation_collision handling above.

  confounders:
    - >-
      SCALE. Toy d for the exact arm (d <= 20-30) is far below ML-KEM's own
      d, and any floor value found there is a demonstration of the
      MECHANISM, not a transportable number — must be labelled exactly
      that, per AGENTS.md rule 7.
    - >-
      SHARED-BASIS DEPENDENCE, inherited from 3d71ca's own H3 confounder:
      the trajectory's own basis-to-basis variation is subject to the
      identical concern and is why >= 8 independent draws remain required
      here too.
    - >-
      DECAY-RATE ESTIMATION NOISE at the largest reached M decade is
      inherently the noisiest part of the fit (fewest effective
      observations); the confidence interval, not a point estimate, is the
      reportable quantity.

  interpretation_limits:
    - >-
      CLAIM TIER: toy, for the exact-floor arm; medium at best for the
      decay-rate arm at 3d71ca's own tested n (64/128) — matching 3d71ca's
      own stated tier. No number transports to ML-KEM parameters by
      extrapolation.
    - >-
      Does not, by itself, produce a C1 bit figure. A confirmed floor only
      TIGHTENS how far IDEA-PENDING-1's own unbounded-M rows may be
      extrapolated; a refuted floor leaves IDEA-PENDING-1's own Beta-law
      provisional status unchanged, neither confirmed nor further
      undermined.
    - >-
      This idea is a NECESSARY COMPLEMENT to, not a replacement for,
      3d71ca's own H1/H3 measurement — it should be commissioned as an
      addition to that same protocol, not as an independent second
      experiment, to avoid duplicating the (basis, target) generation cost.

  heuristic_assumptions:
    - id: H1
      statement: >-
        The finite-alphabet CBD error's own combinatorial minimum
        achievable projected-norm ratio, r_min(B), is strictly positive and
        computable at some toy dimension small enough for exact or
        certified-gap search within budget.
      random_model_justification: >-
        Not a random-model heuristic — a deterministic combinatorial fact
        (a finite set has a minimum). The only heuristic content is
        FEASIBILITY (whether that minimum is findable within budget at a
        dimension still informative), which is an engineering claim
        validated by directly measuring wall-clock at increasing d, not
        assumed.
      supporting_results: []
      validation_experiment_ids: []
      falsification_condition: >-
        Exhaustive search is infeasible at every d small enough to remain
        informative (e.g. d <= 8, where the projected-error statistic is
        too degenerate to be meaningful) — reported as "not computed:
        infeasible within budget," never defaulted to either verdict, per
        this program's own established convention (measure_hkz_indep.py's
        own "NOT COMPUTED: budget exhausted" discipline).
    - id: H2
      statement: >-
        The Beta(beta/2, (d-beta)/2) order statistic's classical extreme-
        value asymptotic rate is the correct comparator for "deceleration,"
        i.e. departure from it is attributable to the object under test and
        not to a mismatch between the asymptotic regime and the tested M
        range.
      random_model_justification: >-
        The Beta distribution's own extreme-value behaviour is a
        theorem, not a heuristic; the heuristic content is only whether the
        TESTED M range (up to ~2^22) is already in the asymptotic regime
        for the specific beta/d used, which is checked directly by
        comparing the fit's residuals at increasing M rather than assumed.
      supporting_results: []
      validation_experiment_ids: []
      falsification_condition: >-
        The NULL-2 (Gaussian) control itself shows apparent deceleration —
        would indicate the comparator, not the CBD object, is the source of
        any real-arm reading, voiding the whole measurement per the
        controls-before-belief discipline.

  target_complexity:
    time_exponent: >-
      UNCHANGED. This idea produces no attack and no exponent claim.
      GOAL-MLKEM-005's own ceiling_known_in_advance (dbeta/beta ~
      0.29*sqrt((1-rho)*ln M / beta); G <= log2 M unconditionally) bounds
      any downstream use of a confirmed floor exactly as it bounds
      IDEA-PENDING-1 — a floor can only ever TIGHTEN (lower) that ceiling
      further, never raise it, since it caps how much a large M can help.
    memory_exponent: UNCHANGED. Not moved by this idea.
    best_known: >-
      Same baseline as IDEA-PENDING-1 and 3d71ca: single-target primal uSVP
      under the pinned cost model.
    hidden_overhead: >-
      The exact floor's own scale-transfer gap (toy d only) is the entire
      hidden overhead here, disclosed explicitly in interpretation_limits.
    tradeoff_note: >-
      None introduced; inherits 3d71ca's own data-for-time framing
      unmodified.

  dominated_by: >-
    Neither 3d71ca's H1 (single-draw marginal, no trajectory, no exact
    floor) nor H3 (between/within-basis variance decomposition only) covers
    this object; no dominating prior art found this session (section 1).
  sota_delta: >-
    Not an attack-cost claim. A methodological tightening of how far C3's
    own eventual measurement may be extrapolated to the census's own
    unbounded-M rows.

  estimated_cost:
    implementation: medium
    compute: low_to_medium
  recommended_priority: high
```

---

## 4. IDEA-PENDING-3 — C2 audit: has anything changed since the 2026-08-05 census, and are the 8 unbounded rows still genuinely unbounded?

```yaml
idea:
  id: IDEA-PENDING-3
  question_id: RQ-MLKEM-001
  title: >-
    A bounded, low-priority literature audit of the already-MET C2 census
    (EV-MLKEM-d146a5), addressing this task's own explicit requirement to
    file at least one C2-facing idea while being honest that C2 is not an
    open criterion.
  class: measurement

  claim: >-
    GOAL-MLKEM-005's own C2 criterion is already satisfied
    (`ledger/goals/GOAL-MLKEM-005.yaml` batch_log, every entry from
    BATCH-a51f91 forward, most recently BATCH-a5b13c: "C2: MET at
    BATCH-a51f91, unchanged"; DEC-20260814-b0a095's own
    binding_carries_restated_and_not_re_litigated section names only C1 and
    C3, not C2, as GOAL-MLKEM-005's "STILL FULLY UNTOUCHED primary
    completion criteria"). This idea does not propose to re-open or re-do
    that census. It proposes a bounded, cheap audit of exactly two things
    that could, in principle, change the ALREADY-FILED distribution without
    requiring a full re-census: (a) whether any of the 8 rows the original
    census reported as stating "no count bound at all" have since received
    an errata, revision, or superseding draft (checked directly against
    each source's own published revision history) in the ~9 days between
    the census's 2026-08-05 retrieval and this task's 2026-08-14 date; (b)
    whether any NEW standardised or widely-deployed ML-KEM specification
    has been published in that window that the original 24-row census did
    not and could not have covered. Both are genuinely two-outcome
    questions: "nothing changed" is a complete, cheap, citable maintenance
    finding; "something changed" requires a new sourced row (or a
    correction to an existing one) and, if it moves the distribution's
    maximum, feeds directly back into IDEA-PENDING-1's own census-grounded
    C1 computation.

  object_first_candidate:
    tracked_object: >-
      The set of 24 sourced rows in EV-MLKEM-d146a5 itself, tracked for
      DRIFT against their own live sources over a stated time window — not
      a re-derivation of the object GOAL-MLKEM-005's own tracked object
      (basis, R) touches at all.
    established_families_off_limits: not_applicable — this idea performs no
      lattice or algorithmic attack; the object-first framing applies
      loosely here (a literature-drift check, not an attack family), and is
      included only for schema completeness per this task's own explicit
      instruction that every idea state this.
    newness_score: >-
      Not a new object or mechanism; a maintenance check on an existing,
      already-filed record. Its only "new" content is the specific 9-day
      drift window and the explicit tie-back to IDEA-PENDING-1.
    testability_score: >-
      High and cheap: each of the 8 rows and the 24-row list has a
      concrete, checkable source (specification, section) already recorded
      in EV-MLKEM-d146a5; checking each source's own revision history is a
      bounded, literature-only task.
    survival_score: not_applicable — no computational object to dissolve;
      this is a point-in-time audit, re-runnable at any future date at the
      same low cost.

  mechanism: >-
    Pure literature/citation re-verification, structurally identical to the
    original C2 census's own method (already validated: "the validator
    re-fetched the load-bearing sources byte-identically" per BATCH-a51f91's
    own criteria_state). No lattice compute, no code, no sampling.

  novelty_status: adaptation

  proof_search_map:
    not_applicable_reason: >-
      Purely a literature-drift audit of an already-filed record, not a
      novel algorithmic construction, asymptotic claim, or reduction; no
      bottleneck, observable, or quantifier structure to map, matching the
      treatment H-MLKEM-11aabf's own C1 (the exact fibre census) received
      for the identical reason.

  predictions:
    - metric: >-
        Count of the 8 originally-unbounded rows whose governing
        specification has received a materially relevant errata, revision,
        or superseding draft since 2026-08-05
      direction: different
      minimum_effect: >-
        0 is a complete, citable "nothing changed" finding; any nonzero
        count requires the specific row(s) to be re-sourced and reported
        with a fresh retrieval date, and re-triggers IDEA-PENDING-1's own
        computation at the updated M if the change is numeric.
    - metric: >-
        Count of newly-published, widely-deployed ML-KEM specifications not
        covered by the original 24-row census
      direction: different
      minimum_effect: >-
        0 is a complete "nothing new" finding; any nonzero count is a new
        sourced row appended to the census, never fabricated without a
        checked primary source.

  minimal_test:
    design: >-
      For each of the 8 unbounded-M rows and the 24-row list overall,
      re-fetch the governing specification's own current revision/errata
      page and record whether it postdates 2026-08-05 with material content
      change; separately, a bounded search (not exhaustive — bounded by a
      stated query budget) for newly-published standardised/deployed
      ML-KEM specifications since that date.
    controls:
      - >-
        Byte-identical re-fetch check on at least 2 of the original 24 rows
        (a spot-check that the original census's own sources have not
        silently moved or been mis-cited), matching the discipline
        BATCH-a51f91's own validator already established for the full set.
    required_metrics:
      - per-row drift status (changed / unchanged / source unreachable)
      - retrieval date for every re-checked source
      - count and list of any newly-added rows

  falsification_conditions:
    - >-
      A source cited by the original census is found to be MIS-cited
      (section or bounding-mechanism does not match what EV-MLKEM-d146a5
      states) — this is a correction to the existing record (a
      `correction:` record per templates/research-records.md), not a
      silent edit, and must be filed as such rather than folded into this
      audit's own output.

  confounders:
    - >-
      A 9-day window is short; a "nothing changed" finding here has a short
      shelf life and should not be over-cited as durable — the audit's own
      value is bounded and re-runnable, not one-shot.

  interpretation_limits:
    - >-
      DOES NOT REOPEN C2. C2 remains MET regardless of this audit's outcome
      unless a change is found that materially alters the distribution's
      own bounding claims — and even then, the correct action is a
      `correction:` record superseding the specific row, per AGENTS.md
      rule 4, never a re-opening of the criterion itself.
    - >-
      recommended_priority is LOW specifically because C2 is already met;
      this idea should not consume dispatch capacity ahead of
      IDEA-PENDING-1 or IDEA-PENDING-2, which serve the goal's genuinely
      open criteria.

  heuristic_assumptions:
    - id: H1
      statement: >-
        The 8 unbounded rows' governing specifications are versioned,
        publicly checkable documents whose revision/errata history is
        directly retrievable.
      random_model_justification: not_applicable — an engineering/sourcing
        claim, not a distributional one.
      supporting_results: []
      validation_experiment_ids: []
      falsification_condition: >-
        A source is found to be unversioned or unreachable — reported as
        "not checkable," not defaulted to "unchanged."

  target_complexity:
    time_exponent: >-
      NOT APPLICABLE — this idea makes no attack, cost, or complexity claim
      of its own. Stated explicitly, per this task's own instruction that
      every idea address target_complexity rather than omit it: even a
      maximally adverse outcome (every unbounded row turns out to have a
      large but finite deployment-specific M) still funnels into
      GOAL-MLKEM-005's own proven, unconditional ceiling G <= log2 M and
      the constant-factor-only regime dbeta/beta ~ 0.29*sqrt((1-rho)*ln M /
      beta) — no census update, however large the resulting M, can move an
      exponent.
    memory_exponent: NOT APPLICABLE, same reasoning.
    best_known: not_applicable
    hidden_overhead: not_applicable
    tradeoff_note: not_applicable

  dominated_by: >-
    EV-MLKEM-d146a5 itself dominates this idea in the ordinary sense: it
    already achieves C2 in full. This idea only asks whether anything has
    changed since.
  sota_delta: "n/a (no result claimed; optional maintenance only)"

  estimated_cost:
    implementation: low
    compute: low
  recommended_priority: low
```

---

## 5. IDEA-PENDING-4 — GSA-profile-fidelity covariate: does departure from the Beta law correlate with how well a basis matches the hkz-lineage's own Chen-Nguyen prediction?

```yaml
idea:
  id: IDEA-PENDING-4
  question_id: RQ-MLKEM-001
  title: >-
    A third, distinct candidate explanation for any C3 departure from the
    Beta law — reduction-quality artifact, diagnosed by reusing this same
    goal's own already-validated "hkz" GSA-profile-deviation observable as
    a per-basis covariate, cheaply appended to 3d71ca's/IDEA-PENDING-2's own
    experiment.
  class: composition

  claim: >-
    If (or once) 3d71ca's own C3 measurement, or IDEA-PENDING-2's own
    extension of it, finds a departure from Beta(beta/2, (d-beta)/2) in the
    empirical distribution of R across the >= 8 independent (key, basis)
    draws 3d71ca's own minimal_test already calls for, that departure's
    basis-to-basis VARIATION correlates with the SAME basis's own "hkz"
    value — mean(logb[d-beta:]) - logdet/d, the quantity the hkz/HKZ-
    independence lineage has already validated across seven prior batches
    (T-HKZINDEP-CONFIRMED) as measuring how closely a reduced basis's
    Gram-Schmidt profile matches the Chen-Nguyen BKZ simulator's
    prediction. Concretely: |Spearman rho| >= 0.5 between (per-basis "hkz"
    deviation) and (per-basis departure-from-Beta magnitude), across the
    same >= 8 draws, implicates atypical reduction quality as at least a
    partial explanation; |rho| < 0.3 refutes it as an explanation at the
    tested cells.

  object_first_candidate:
    tracked_object: >-
      The PAIR (per-basis "hkz" GSA-deviation scalar; per-basis
      departure-from-Beta magnitude), correlated across the basis draws —
      a genuinely different object from 3d71ca's own single-draw marginal
      law (H1) and its between/within-basis variance decomposition (H3):
      H3 asks whether targets sharing ONE basis are more correlated with
      EACH OTHER than iid; this idea asks whether that basis's own,
      independently-defined reduction-quality score explains how far ITS
      OWN targets depart from the model, which H3 does not test.
    established_families_off_limits: >-
      Same list as IDEA-PENDING-1/2. Additionally, the hkz lineage's own
      seven-batch admissibility-gate/independence-instrument object (route
      comparison, mutation testing) is declared off-limits as this idea's
      primary lens: this idea reuses only the "hkz" OBSERVABLE's
      mathematical DEFINITION (explicitly licensed for reuse under this
      program's own established convention — PREREG-5 2.2's own point 3,
      "the observable's own mathematical definition ... is not
      code-sharing"), never the hkz lineage's own barred reduction/
      enumeration wrapper code, and never its own object (comparing two
      REDUCTION ROUTES against each other).
    newness_score: >-
      Genuinely new: no proposal or hypothesis found this session connects
      the hkz lineage's own GSA-fidelity measurement to the ciphertext-
      side Beta-law object at all — these have been two structurally
      separate lineages within this same goal for its entire ~20-batch
      history.
    testability_score: >-
      High. "hkz" is an already-precisely-defined, closed-form scalar
      computed directly from GSO data any BKZ-beta reduction already
      produces as a byproduct; computing it alongside 3d71ca's own reduced
      bases adds bookkeeping, not new reduction work.
    survival_score: >-
      Survives exactly as long as a real reduced basis exists to compute
      "hkz" on; dissolves at any construction that does not produce a real
      GSO (e.g. a purely closed-form estimator readout, which is why this
      idea is inapplicable to H-MLKEM-11aabf's own object).

  mechanism: >-
    For each of the >= 8 independent (key, basis) draws 3d71ca's own
    protocol already specifies, compute the SAME "hkz" quantity the hkz
    lineage uses (reusing the DEFINITION, computed fresh at 3d71ca's own
    dimension/beta cells — n in {64,128}, beta in {40,55,70} — which is a
    DIFFERENT regime from the hkz lineage's own confirmed cells, d <= 40,
    beta <= 30, so this is itself a small new measurement, not a free reuse
    of archived numbers) alongside that basis's own empirical
    departure-from-Beta magnitude (e.g. the Kolmogorov distance between
    that basis's own empirical R distribution and the Beta CDF, or its own
    tail-quantile ratio, exactly as 3d71ca's own H1 validation_plan already
    computes per basis). Report the Spearman correlation across the >= 8
    draws.

  novelty_status: adaptation

  lossy_projection_identifiability_audit:
    projection: >-
      The full per-basis GSO matrix and the full per-basis empirical R
      distribution --> two scalars per basis (the "hkz" value; the
      departure-from-Beta magnitude), correlated across bases.
    what_is_discarded: >-
      Every individual target's own R value beyond its contribution to the
      basis-level departure summary; every Gram-Schmidt coordinate beyond
      its contribution to the single "hkz" mean.
    why_genuinely_lossy: >-
      Many distinct GSO profiles share the same "hkz" scalar (it is a mean
      over a log-norm profile, not the profile itself); many distinct
      per-basis R distributions share the same departure-magnitude scalar.
    why_compatible_with_the_operations: >-
      Both scalars are computed by operations (a GSO log-norm average; a
      CDF-distance statistic) that are already deterministic functions of
      the reduced basis and the drawn targets respectively; the correlation
      itself is then a deterministic function of the two scalar sequences.
    is_it_only_a_change_of_coordinates: >-
      No — the two scalars cannot reconstruct either the full GSO or the
      full target distribution; the correlation is a genuinely coarser
      question than either underlying object.

  proof_search_map:
    bottleneck: >-
      Distinguishing "the Beta law departs because of atypical reduction
      quality" (correctable, in principle, by different reduction
      strategies — the hkz lineage's own seven-batch history is entirely
      about characterizing and improving this) from "the Beta law departs
      for a structural reason unrelated to reduction quality" (H3's basis-
      error correlation; IDEA-PENDING-2's discreteness floor) — these three
      candidate mechanisms are not distinguished by 3d71ca's own protocol
      alone.
    baseline_embedding:
      parameter_slice: >-
        A basis whose "hkz" value is closest to zero (best-matching the
        Chen-Nguyen prediction) among the >= 8 draws.
      reproduction_check: >-
        At that basis, the empirical departure-from-Beta magnitude should
        be, if this idea's mechanism is real, among the SMALLEST of the >=
        8 draws — a directional, checkable prediction at a single named
        instance, not only a correlation over the whole set.
    observation_collision:
      observable: >-
        The Spearman correlation coefficient itself.
      distinct_preimage_search: >-
        A near-zero correlation is consistent with BOTH "reduction quality
        genuinely does not matter" and "the >= 8-draw sample is too small
        to detect a real but modest correlation" — these are not
        distinguished by the coefficient alone, so the falsification
        condition below requires the confidence interval, not the point
        estimate, to exclude |rho| >= 0.5 before refuting the mechanism.
    constructive_transforms:
      - transform: representation_reduction
        proposed_object: >-
          Represent each basis by one scalar (its own "hkz" value) rather
          than its full GSO, turning a structural question about reduction
          quality into a correlation question answerable from data 3d71ca's
          own protocol already generates as a byproduct.
        predicted_gain: >-
          A cheap (near-zero marginal compute), genuinely new diagnostic
          that redirects future effort toward reduction-strategy work (if
          confirmed) or away from it (if refuted), which neither 3d71ca's
          own H1/H3 nor IDEA-PENDING-2 can do on their own.
    quantifier_order: >-
      FOR the >= 8 independent (key, basis) draws 3d71ca's own protocol
      specifies, EXISTS a measured Spearman correlation with a reported
      confidence interval. No claim is made or attempted about whether the
      correlation holds at other dimensions, betas, or reduction
      strategies not tested.
    method_ceiling:
      strongest_certifiable_claim: >-
        At most a correlation finding at the specific tested cells,
        diagnostic rather than bound-producing (see interpretation_limits).
        It cannot certify causation and cannot, on its own, produce a C1
        bit figure.
      nearby_object_control: >-
        The nearby object where this method's conclusion is known to be
        VACUOUS is H-MLKEM-11aabf's own object: a closed-form ESTIMATOR
        readout with no real GSO at all, where "hkz" is undefined. This
        idea is explicitly inapplicable there, and is not proposed as an
        extension of H-MLKEM-11aabf.
    proof_obligations:
      - claim: >-
          "hkz" is computed at 3d71ca's own dimension/beta cells, not
          reused from the hkz lineage's own archived, different-scale
          cells.
        responsibility: scope
      - claim: >-
          The correlation's confidence interval, not only its point
          estimate, is reported.
        responsibility: strictness
      - claim: >-
          The single-instance directional check (baseline_embedding above)
          is reported alongside the aggregate correlation.
        responsibility: baseline
    not_applicable_reason: null

  predictions:
    - metric: >-
        Spearman correlation between per-basis "hkz" deviation and
        per-basis departure-from-Beta magnitude, across >= 8 draws
      direction: higher
      minimum_effect: >-
        |rho_s| >= 0.5 (matching 3d71ca's own materiality bar for its own
        selection-efficiency prediction) is required to call
        reduction-quality a live explanation; |rho_s| < 0.3, with a
        confidence interval that excludes 0.5, refutes it at the tested
        cells.
    - metric: >-
        Directional single-instance check: is the best-"hkz" basis also
        among the lowest-departure bases (rank <= 3 of 8)?
      direction: higher
      minimum_effect: >-
        A pass/fail report at this single named instance, reported
        alongside the aggregate correlation rather than substituting for it.

  minimal_test:
    design: >-
      Layered onto 3d71ca's own (or IDEA-PENDING-2's extended) protocol at
      zero additional basis generation: for each of the already-planned >=
      8 (key, basis) draws, additionally compute "hkz" from the same GSO
      data already produced, and the same per-basis departure-from-Beta
      statistic 3d71ca's own H1 validation_plan already computes per basis;
      correlate.
    controls:
      - >-
        NULL-2 (Gaussian, matched variance) reused from 3d71ca: "hkz"
        should still vary basis-to-basis (it is a property of the basis,
        not the error), but the CORRELATION with departure-from-(the now
        exact-by-construction)-Beta-model should be measured and reported
        as a sanity baseline, not assumed zero.
    required_metrics:
      - per-basis "hkz" value at the tested cells
      - per-basis departure-from-Beta magnitude (reused from 3d71ca's own
        H1 computation)
      - Spearman rho with confidence interval
      - the single-instance directional check outcome

  falsification_conditions:
    - >-
      |rho_s| < 0.3 with a confidence interval excluding 0.5 — refutes
      reduction-quality as a live explanation at the tested cells; shifts
      explanatory weight to H3 / IDEA-PENDING-2's discreteness floor.
    - >-
      The single-instance directional check fails (best-"hkz" basis is
      NOT among the lowest-departure bases) while the aggregate
      correlation is reported as positive — a reporting inconsistency that
      must be resolved (likely a small-sample artifact) before either
      number is cited.

  confounders:
    - >-
      SAMPLE SIZE. >= 8 draws is a small sample for a correlation
      coefficient; the confidence interval, not the point estimate, must
      carry the finding, exactly as this idea's own falsification
      condition requires.
    - >-
      SCALE MISMATCH between the hkz lineage's own confirmed regime (d <=
      40, beta <= 30) and 3d71ca's own tested regime (d in {256,512}, beta
      in {40,55,70}) — "hkz" is computed FRESH at the new regime, not
      reused, precisely because this mismatch means the lineage's own
      confirmation does not automatically transfer.

  interpretation_limits:
    - >-
      DIAGNOSTIC ONLY. A positive finding here does not itself move C1's
      bound in either direction; it only redirects future effort (toward
      reduction-strategy work) versus a structural finding (IDEA-PENDING-2,
      H3), which would instead cap C1's bound directly. This is stated
      explicitly so a positive correlation here is never mis-cited as a
      C1 or C3 answer on its own.
    - >-
      Requires 3d71ca's own protocol (or IDEA-PENDING-2's extension of it)
      to actually run first; this idea is not independently dispatchable
      without that host measurement.

  heuristic_assumptions:
    - id: H1
      statement: >-
        The "hkz" observable's own validated meaning (deviation from the
        Chen-Nguyen BKZ simulator prediction) remains a meaningful
        covariate at 3d71ca's own dimension/beta regime, which is outside
        the hkz lineage's own seven-batch confirmed range.
      random_model_justification: >-
        The Chen-Nguyen simulator itself is a widely-used heuristic model
        of BKZ's own Gram-Schmidt profile, not specific to the toy
        dimensions the hkz lineage happened to test; the EXTRAPOLATION risk
        is that its accuracy could degrade differently at larger beta, which
        is exactly why this idea computes "hkz" fresh rather than assuming
        transfer.
      supporting_results: []
      validation_experiment_ids: []
      falsification_condition: >-
        "hkz" itself fails to vary meaningfully across the >= 8 draws at
        the new regime (near-constant) — the covariate has no discriminating
        power there regardless of the correlation question, and the idea
        is void at that regime until a covariate with actual spread is
        found.

  target_complexity:
    time_exponent: >-
      NOT APPLICABLE — diagnostic only, no attack or bound produced
      directly. GOAL-MLKEM-005's own ceiling_known_in_advance bounds any
      DOWNSTREAM use of this idea's findings exactly as it bounds
      IDEA-PENDING-1/2: no correlation finding here can move an exponent,
      since it only redirects which mechanism (reduction quality vs
      structural) future constant-factor work should target.
    memory_exponent: NOT APPLICABLE, same reasoning.
    best_known: not_applicable
    hidden_overhead: >-
      The scale-mismatch risk (H1 above) is the primary hidden risk,
      disclosed explicitly rather than assumed away.
    tradeoff_note: not_applicable

  dominated_by: >-
    No proposal or hypothesis found this session connects these two
    lineages; not dominated by any in-repo artifact. External literature
    not independently re-checked this session (section 1).
  sota_delta: "n/a (diagnostic only, no attack-cost claim)"

  estimated_cost:
    implementation: medium
    compute: low
  recommended_priority: medium
```

---

## 6. Ranking rationale, honest accounting, and recommendation

### Ranking rationale (expected information gain vs. cost)

**IDEA-PENDING-1** is the cheapest possible action of the four (pure
arithmetic reusing two already-validated derivations and an already-filed
census; no sampling, no lattice reduction) and directly produces
GOAL-MLKEM-005's own C1 deliverable in the exact shape its criterion
demands, including the mandatory f''-sensitivity table no existing
artifact currently supplies. Because C1's own criterion text explicitly
allows X = 0 as a complete answer, this idea has a real chance of
discharging C1 outright at essentially zero compute — the single highest
information-gain-per-cost action in this set. **IDEA-PENDING-2** is the
next most valuable: it is a cheap, near-zero-marginal-cost addition to
whatever experiment eventually measures 3d71ca's own H1 (C3's actual
measurement), and it closes a real gap neither 3d71ca nor GOAL-MLKEM-005's
own criterion text currently addresses (a hard combinatorial floor versus
a smooth continuous tail), directly bearing on how far IDEA-PENDING-1's own
unbounded-M rows may honestly be extrapolated. **IDEA-PENDING-4** is a
genuine, cheap diagnostic add-on with real but secondary value: it does
not produce a bound on its own and depends on the same host measurement
IDEA-PENDING-2 depends on, so it should be commissioned alongside rather
than instead of IDEA-PENDING-2. **IDEA-PENDING-3** is the least valuable
of the four by design: it audits an already-met criterion, is filed only
because the task's own brief required a C2-facing idea, and its
recommended_priority is explicitly `low`.

### Which idea I would test first, and why

Among this session's own four proposals, **IDEA-PENDING-1** is the one I
would dispatch first: it requires no new infrastructure, no lattice
reduction, and no new sampling — only a short deterministic script
combining EV-MLKEM-d146a5's own already-filed census numbers with
H-MLKEM-dc51f5's own already-derived GAIN(u) formula and
IDEA-20260805-3d71ca's own already-stated Beta order-statistic law. Its
minimal test is the cheapest valid discriminator in this document because
it discriminates between two mutually exclusive, exhaustive, and equally
citable outcomes (X = 0 vs. X > 0 with a stated bit figure) using
arithmetic alone, and it fails safe: the M = 1 boundary check and the
dc51f5-reproduction control both catch an implementation bug before any
census-row number is trusted.

**However**, stated plainly because it is the single most decision-relevant
fact this session surfaced: the highest-value action available to whichever
Coordinator session next opens `/design-experiment` on this goal is **not**
any idea in this document. It is converting **`IDEA-20260805-3d71ca`**
itself — filed 2026-08-05, unconverted for roughly nine days and twenty
batches, already schema-complete against `agents/idea-generator.md`'s own
bar — directly to a hypothesis. IDEA-PENDING-1 and IDEA-PENDING-2 in this
document are designed to be commissioned alongside it (IDEA-PENDING-1
consumes its H1; IDEA-PENDING-2 and IDEA-PENDING-4 extend its own
minimal_test), not instead of it.

### Honest accounting (docs/inventor-protocol.md §5)

- **Object(s) studied**: `R = ||pi_{d-beta}(e)||^2 / ||e||^2` under a
  shared BKZ-beta-reduced basis (GOAL-MLKEM-005's own tracked object),
  examined through four lenses: (1) the census-grounded GAIN(u) balance
  evaluation (IDEA-PENDING-1); (2) the order-statistic trajectory and its
  finite-alphabet floor (IDEA-PENDING-2); (3) the C2 census's own drift
  over time (IDEA-PENDING-3, does not touch R); (4) a GSA-profile-fidelity
  covariate for any departure from the Beta law (IDEA-PENDING-4).
  Established families declared off-limits as the primary lens this
  session (inherited from `IDEA-20260805-3d71ca`'s own declaration, and
  extended to include KEY-side selection, `H-MLKEM-dc51f5`'s own object,
  and the hkz lineage's own route-comparison object): dual-sieve + FFT
  distinguishers; estimator cost-table/primal_bdd-vs-matzov differencing;
  hybrid MITM/decoding on sparse secrets; coefficient-isometry
  preprocessing amortisation; class-group/unit-lattice/PIP attacks;
  decryption-failure/failure-boosting attacks; implementation side
  channels; key-side multi-target selection; hkz-lineage route comparison.
- **Depth of verified structure**: Nothing in this document is measured.
  Every idea is a proposal; IDEA-PENDING-1 and IDEA-PENDING-3 are
  zero-compute derivations/audits that could be run and verified cheaply;
  IDEA-PENDING-2 and IDEA-PENDING-4 require dispatching (an extension of)
  `IDEA-20260805-3d71ca`'s own not-yet-run experiment before they produce
  anything. No claim above `derivation`-tier (for IDEA-PENDING-1's own
  arithmetic, once run) is asserted anywhere in this document.
- **`dominated_by`**: stated per idea above. Session-level: for the
  underlying mechanism and asymptotics of multi-ciphertext degradation
  itself, Bernstein ePrint 2022/1580 is inherited as the dominator from
  `IDEA-20260805-3d71ca`'s own 2026-08-05 check — **not independently
  re-verified this session**, and this gap is disclosed rather than
  papered over: no fresh external web search was run (section 1). For the
  four specific measurement/derivation refinements proposed here (census-
  grounding with an f''-sensitivity table; the order-statistic floor; the
  C2 drift audit; the GSA-profile covariate), the in-repo corpus check
  (`ledger/proposals/`, `ledger/hypotheses/`, `knowledge/`) found no
  dominating prior art, and this is stated as an in-repo-only finding, not
  a global clearance.
- **`sota_delta`**: none of the four ideas claims an attack-cost or
  security-margin delta. All are procedural or diagnostic contributions
  toward GOAL-MLKEM-005's own C1-C3, explicitly and repeatedly bounded by
  the goal's own proven `ceiling_known_in_advance`
  (`dbeta/beta ~ 0.29*sqrt((1-rho)*ln M / beta)`; `G <= log2 M`
  unconditionally by convexity) in every idea's own `target_complexity`
  field, per this task's own explicit instruction.
- **Enumerated closures**: none. No lane is closed by this document. The
  one closure-shaped finding this session produced is the correction in
  section 0.1 (C2 is already met, not open) — that is a correction to the
  task's own premise about the ledger's current state, not a new closure
  with a named obstruction under `docs/inventor-protocol.md` §4, and it is
  not presented as one.
- **Open directions for the next session**: (a) whether the Coordinator
  converts `IDEA-20260805-3d71ca` directly to a hypothesis (recommended,
  see above) versus selecting from this document instead or in addition;
  (b) if IDEA-PENDING-1 is run, whether any census row clears the >= 2-bit
  materiality bar, which would sharply re-prioritize this goal's next
  batch; (c) the shared, unresolved "stage 0" risk both `H-MLKEM-dc51f5`
  and IDEA-PENDING-1 inherit — the 2016 uSVP condition's exact published
  form has never been read by anyone in this program's own record and is
  the single quantity ("gamma") every numeric verdict in this family
  ultimately rests on.
