# RED TEAM REPORT — TASK-20260812-696cd4

    goal / batch   GOAL-MLKEM-005 / BATCH-4ed139
    role           red-team          policy review-adversarial, effort xhigh
    governed by    PREREG-1 (TASK-20260812-34b86c), frozen and notarized at
                   commit 8d72f2c038a577e216ab9d6d0e5995f65d5ff819
    archived by    TASK-20260812-655fe9 (ledger archive) — THIS TASK COMMITS NOTHING
    claim tier     TOY, UNCONDITIONALLY

**CLAIM TIER TOY.** Nothing in this report bears on ML-KEM security, on any
FIPS 203 parameter set, on any attack cost, or on any cost model. Nothing here
transports to beta = 606, d = 1420, or any other parameter set by extrapolation,
analogy or any other route.

**THIS REPORT RESCORES NO FROZEN VERDICT.** R2-OUT-1 = FAIL, R2-OUT-2 = FAIL,
R2-OUT-3 = HOLDS, R2-OUT-4, R2-OUT-5, R2-OUT-V does-not-fire, R2-OUT-6, R2-OUT-7
and R2-OUT-8 are the producers'. The termination branch **T-F0FAIL-PARTIAL** is
read off R2-OUT-1 and R2-OUT-2 under R2-OUT-V's precedence and nowhere else, and
**I do not contest it**. Every probe below scores objects the frozen text does
not score, or re-derives a producer statement independently.

---

## 0. THE REQUIRED OUTPUT RECORD

```yaml
red_team_report:
  id: RT-20260812-696cd4
  task_id: TASK-20260812-696cd4
  claim_under_review: >-
    BATCH-4ed139's headline is a NEGATIVE RESULT: T-F0FAIL-PARTIAL. G-VAR2 as
    frozen by PREREG-1 section 3 fails fixture F0 — the fixture AM-16 was
    written against — because `rdet`, which reads zero entries of A, is ADMITTED
    at 38 of 38 cells through routes R2, R4 and R5; with the three rider claims
    P-C1 (rider i), P-FR1 (rider ii) and P-L1 (rider iii) beside it.
  verdict_on_the_branch: >-
    THE BRANCH IS CORRECT AND I DO NOT CONTEST IT. The F0 failure is REAL,
    reproducible, independently reproduced here on a host where fpylll is
    absent, and it is NOT reached through the fpylll gap. The precedence rule
    was applied, R2-OUT-V was evaluated first, and no infrastructure outcome
    was narrated into a science branch.
  verdict_on_what_the_branch_is_taken_to_MEAN: >-
    THE ATTRIBUTION IS WRONG BY ONE CLAUSE, and it is the clause PREREG-1
    itself introduced. PREREG-1 7.3 says T-F0FAIL MEANS "AM-16(a) itself needs
    replacing". AM-16(a) is VAR-S. VAR-S never decided a single `rdet` cell:
    it is scale_degenerate at 38/38 under all six routes. What decided them is
    PREREG-1 3.2 (the degenerate-scale rule) composed with 3.3's BIT-IDENTITY
    fallback — both frozen in THIS batch, neither part of AM-16(a). Built and
    measured: with the float representation of the determinant removed and
    nothing else changed, G-VAR2 REFUSES `rdet` at 38/38 and F0's declared
    target for `rdet` is MET.
  objections:
  - id: O-1
    severity: high
    title: >-
      The declared argument set is DECORATIVE in the implementation, and
      repairing it flips full G-VAR2 verdicts on a FROZEN candidate at 38 of 38
      cells under all six declared routes. This is the primary target, BUILT.
    what_was_built: probes/probe_argset.py, section Q2 — the fibre family
      F0|fib_dec, faithful to PREREG-1 2.4's declared nuisance set.
    measured: >-
      measure_gvar2.py evaluates VAR-F on FIBRE_OF[family], a candidate-
      INDEPENDENT pair of fibre-family lists; the per-candidate declared set
      appears in the output only as the reported string
      `fibre_nuisance_held_fixed`. PREREG-1 2.4 declares A[0,0] a nuisance
      argument held fixed on the fibre for `V_evade` and `X_lambda`; MEASURED
      at all six fibre families and all ten lattices, A[0,0] is NOT held fixed
      at any of them. Rebuilding the seed-prefix-2 fibre with A'[0,0] pinned to
      its i = 0 value — abs(det B) untouched and still bit-identical across the
      8 bases, so PREREG-1 6.4's could-not-PASS guard still holds — flips the
      full G-VAR2 verdict on `X_lambda` from ADMIT to REFUSE at 38 of 38 cells
      for lambda in {1e-1, 1}, and at 22 of 38 for lambda = 1e-2, under EVERY
      one of the six declared routes.
    why_it_matters: >-
      PREREG-1 3.5 concedes before the run that the fibre clause MOVES the free
      parameter to the declared argument set. This is that concession
      instantiated: same observable, same family, same tau_var, same routes,
      same numbers — opposite verdict, decided by which fibre instantiates the
      declaration. AM-17(c)'s sentence "A candidate that is a function of
      |det B| alone must be scored on a family that holds |det B| fixed,
      whatever else varies" is implemented; its generalisation to candidates
      with a LARGER declared nuisance set is not.
    against_my_own_thesis: >-
      REPORTED AT THE SAME WEIGHT. `V_evade` — the one such candidate the batch
      actually scores — does NOT flip: VAR-S REFUSES it at 38/38 on all six
      routes, so the conjunction REFUSES it under both fibres and only the
      VAR-F sub-clause changes. The flip requires lambda >= 1e-2, and at
      lambda in {0, 1e-12, 1e-10, 1e-9, 1e-8, 1e-6, 1e-4} there is no flip at
      any cell on any route. So this objection does not touch R2-OUT-3 (P-V1)
      and does not change R2-OUT-1 or R2-OUT-2.
  - id: O-2
    severity: high
    title: >-
      The F0 failure is a FLOAT-REPRESENTATION effect, and it passes the
      artifact tell of docs/inventor-protocol.md section 3. The null-object
      control was built.
    what_was_built: probes/probe_precision_null.py — null object `rdet` (reads
      zero entries of A) against real object `X_gso_k` (reads the leading k GSO
      norms), with arithmetic precision as the parameter that must destroy an
      artifact, plus route R6_exact.
    measured: >-
      NULL OBJECT `rdet`, relative fibre dispersion s/|m| at float64: exactly
      0.0 (R1), 4.1e-14 to 1.4e-13 (R2), 3.1e-10 to 2.6e-09 (R4), 2.5e-14 to
      1.0e-13 (R5). Moving to float32 multiplies it by 1.4e6 to 5.9e8, median
      5.5e7, against eps32/eps64 = 5.4e8. REAL OBJECT `X_gso_k`, same fibre,
      same code path: relative dispersion 5.7e-4 to 1.1e-2, and the float32/
      float64 ratio is 0.9999991 to 1.0000001 at every one of the ten
      lattices — precision-INVARIANT to within one part in a million.
      NEARBY OBJECT: route R6_exact takes log abs(det B) from the EXACT integer
      determinant through `decimal` at 60 digits, changing nothing else — same
      observable, same family, same fibre, same declared arguments, same
      tau_var, same two clauses. G-VAR2 then REFUSES `rdet` at 38 of 38 cells
      and F0's declared target for `rdet` is MET.
    what_it_means: >-
      The quantity on which the whole F0 verdict turns moves by seven to nine
      orders of magnitude when the parameter meant to destroy it is moved by
      8.7 orders, and vanishes exactly when it is removed. That is the
      canonical artifact signature, and it localises the F0 failure to PREREG-1
      3.3's bit-identity fallback reading a float representation — not to the
      observable, not to VAR-S, not to the family, not to AM-17(c)'s separator.
    against_my_own_thesis: >-
      REPORTED AT THE SAME WEIGHT, TWICE. (a) The effect is FORCED, not
      accidental: the fibre dispersions sit at 170 to 4.4e6 ULPs of the cell
      mean, i.e. exactly the accumulated rounding of a d-term float sum, so any
      host will reproduce non-bit-identity with overwhelming probability. The
      F0 failure is therefore ROBUST and is not a fluke of this machine.
      (b) The cheapest environment falsifier was run: with all five BLAS thread
      caps pinned to 1, every `bit_identical` flag is unchanged at every
      lattice and route, and only two of forty float64 fibre sds move at all
      (rdet|R5 at L4 and L5, in the 13th significant figure). The F0 failure
      survives the environment control.
  - id: O-3
    severity: high
    title: >-
      PREREG-1 7.3's MEANS clause mis-attributes the defect, and its FORBIDS
      list — unlike 7.2's — contains no bar on a seventh consecutive gate
      repair. The batch is therefore at risk of the failure mode symmetric with
      premature closure: an unbounded repair loop.
    measured: >-
      `rdet` is scale_degenerate on VAR-S at 38/38 cells under ALL SIX routes
      (lead's own R2-OUT-5), so AM-16(a)'s statistic decided none of them.
      AM-16(a) has exactly ONE independent miss in this batch: `rawtail`
      through RD at L4 beta 95, D_c = 4.876e-4 against tau_var = 1e-3 — and the
      lead itself records that a reviewer who reads route RD as strictly
      requiring fpylll must read that entire row as UNCOVERED. UNDER THE STRICT
      RD READING, AM-16(a) HAS ZERO MISSES IN THIS BATCH and the whole F0
      failure is attributable to clauses 3.2 and 3.3 of PREREG-1 itself. Both
      readings give F0 = FAIL and both give T-F0FAIL; they differ entirely in
      WHAT THE SUCCESSOR IS SUPPOSED TO REPLACE.
    consequence: >-
      A decision that records "AM-16(a) needs replacing" and specifies a
      seventh scaled-dispersion statistic would be repairing a clause that
      decided nothing, while leaving the clause that decided everything in
      place. 7.2 forbids a seventh consecutive gate repair; 7.3 does not, and
      7.3 is the branch that fired.
  - id: O-4
    severity: high
    title: >-
      AM-11 is a binding carry and it bites harder than any producer states.
      G-VAR2 admits a parameter-determined observable, so under AM-11 no
      admissibility claim may be reported from it — which bounds rider (ii)'s
      P-FR1 second half more tightly than PREREG-1 7.3 does.
    quoted: >-
      AM-11 (DEC-20260808-05b684, carried by PREREG-1 11): "any closed-form
      function of (d, k, beta, q) with zero between-basis variance MUST be
      refused, and a gate that admits one is declared INADMISSIBLE and no
      admissibility claim may be reported from it. ... The parameter-determined
      null must be on the frozen candidate list, scored through the identical
      code path."
    applied: >-
      `rdet` = exp((d-k) log q / d) in F0 is a closed-form function of (d, k, q)
      with zero between-basis variance as a mathematical object; it is on the
      frozen candidate list; it was scored through the identical code path; and
      G-VAR2 ADMITTED it at 38/38 through three of six routes. AM-11's
      consequent therefore fires on its own terms.
    against_my_own_thesis: >-
      REPORTED AT THE SAME WEIGHT AND IT IS THE STRONGEST THING IN THIS BATCH'S
      FAVOUR. AM-11's own required control — a parameter-determined null on the
      frozen candidate list, through the identical code path — is exactly what
      caught this. The control fired. That is a working instrument-of-the-
      instrument and it should be recorded as such.
  - id: O-5
    severity: medium
    title: >-
      There IS a fourth account of wave 2's count of 2, and it preserves wave
      2's own stated 6x threshold. Rider (i)'s Observation 3 is correct about
      the two committed normalizations and over-general as written.
    what_was_built: probes/probe_readings_and_guard.py, part A3 — a 28-cell
      grid over seven normalizations x two thresholds x two boundary rules,
      searched for a count of exactly 2.
    measured: >-
      Rider (i)'s reading axis IS closed, and more tightly than it claims: all
      8 per-basis values are bit-identical in every stored field at all 29
      entries (re-derived here from the raw per_basis records), and all SEVEN
      reductions tested — i0, n-pass, fsum mean, min, max, median and i7 —
      agree bitwise everywhere. BUT the UNNORMALIZED criterion value
      |X_a - X_b|, formed from the same committed fields, is below
      6 * tau_rel = 0.6 at EXACTLY 2 of 29 entries and EXACTLY 2 of the 19
      G-REL2 cells, under BOTH boundary rules — and those two entries are
      precisely 0.486626 (G-REL2 L1/L2 beta 15) and 0.496557 (G-REL2 L4/L5
      beta 20), the two values wave 2 named. Rider (i)'s account keeps the
      normalization and moves the threshold to 5.71x, which wave 2 never
      stated; this account keeps wave 2's stated 6x threshold and removes the
      normalization.
    additional_fragility: >-
      Rider (i)'s account is itself conditional on two implementation choices
      it discloses but does not carry into its Observation-1 wording. Measured:
      a left-to-right sum moves the mean-over-8 by one ulp at 25 of 58
      entry-field pairs; at the 6x threshold every count is unchanged under
      i0, fsum-mean and naive-mean under both rules and both committed
      normalizations, but at the 5.71x threshold under the STRICT rule the
      naive-mean reading gives 12 (maxfloor) and 11 (absX) where i0 and fsum
      give 2 and 0, because the 4/7 plateau sits exactly on that boundary.
    binding_discipline: >-
      NEITHER SUB-6x COUNT BECOMES CITABLE THROUGH THIS. "A factor of 6 to 31"
      is FALSE; the citable range is 4.87x to 31.03x. This probe does not find
      that wave 2 used any particular account, does not declare either wave
      right or wrong, and adjudicates C-1 in no direction. What it does is
      remove the uniqueness from rider (i)'s explanation, so a Coordinator
      ruling that rests on that uniqueness would rest on something the numbers
      do not support.
    against_my_own_thesis: >-
      REPORTED AT THE SAME WEIGHT. Rider (i)'s reproduction of wave 1's count
      is CONFIRMED independently here: 15 of 19 G-REL2 cells below 6x under the
      maxfloor normalization with the 1e-12 boundary rule, and that is the ONLY
      cell of my 28-cell grid that yields 15 of 19. Rider (i)'s central
      structural claim — that the reading axis cannot explain C-1 — is
      CONFIRMED and strengthened, not refuted.
  - id: O-6
    severity: medium
    title: >-
      R2-OUT-V, the VOID row PREREG-1 6.1 declares "live and not a straw man",
      was UNREACHABLE by a factor of 71 before the run. Its non-firing is not
      evidence.
    measured: >-
      VAR-S on X_lambda is exactly linear in lambda: D_c(lambda) = lambda *
      sd_i(A[0,0]_i/q) / R_{d,k}, because the X_null part is bit-identical
      across the 8 bases at every F0 cell under R0/R1/R3 and contributes no
      dispersion. The largest reachable D_c in the frozen grid is its value at
      lambda = 1, and the SMALLEST such value over all ten lattices is
      7.1316e-02 — 71.3 times tau_var = 1e-3. R2-OUT-V could have fired only if
      tau_var had been at least 7.13e-2.
    scope_of_the_objection: >-
      P-G1 is a MUST-PASS guard and a must-pass guard is meant to pass; this
      does not retire it. What it bounds is the citable content: the batch may
      not cite "the guard crossed, so VAR-S is alive at this scale" as a live
      control. The informative content of section 6.1 is lambda*, which IS a
      measurement.
  - id: O-7
    severity: medium
    title: >-
      The reported lambda* over-states the crossing amplitude, and the
      statistic carries neither AM-10 replication nor an AM-11-style dispersion
      as reported by the lead.
    measured: >-
      The frozen lambda grid has NO point between 1e-4 and 1e-2, so a grid
      lambda* localises the true crossing only to two decades and is an UPPER
      BOUND. Solving the linear identity exactly on four independent A draws
      (seed prefixes 1, 2, 3, 4) x ten lattices: continuous lambda* ranges
      3.1102e-03 to 1.4153e-02, median 6.5960e-03, sd 3.3672e-03. The eleven
      cells the lead reports at lambda* = 1e-1 actually cross at about 1.4e-2 —
      an over-statement of roughly 7x. On the frozen grid the replicated
      multiset is {1e-2: 30, 1e-1: 10}, so the grid-level statistic itself
      replicates.
  - id: O-8
    severity: medium
    title: >-
      Rider (ii)'s P-FR1 admission half does not survive the repair its own
      section F.1 names, and the exact cells where it fails are measurable now.
    measured: >-
      Rider (ii)'s VAR-F PASS is obtained at scale_degenerate fibre cells by the
      same scale-free bit-identity test that admits `rdet`: fibre sd 9.02e-02
      (X_gso_k, L7) and 4.18e-11 (rdet|R2, L7) both PASS, about nine orders
      apart. If VAR-F's fallback were replaced by a relative-dispersion test at
      the SAME tau_var = 1e-3, `rdet` would be refused everywhere (max relative
      2.6e-9) but `X_gso_k` would ALSO be refused at L2 (9.36e-4), L4 (8.41e-4)
      and L5 (5.71e-4) — 15 of the 38 cells. The two objects are 5.3 orders
      apart, so a separating threshold exists; tau_var = 1e-3 is not it.
      Worse, the repair is not precision-robust either: at float32, rdet|R4's
      relative fibre dispersion reaches 2.95e-01 and would be admitted by any
      threshold below that.
    what_survives: >-
      P-FR1's FIRST half — refused by G-REL1 — is robust: it is an exact
      algebraic zero through a different, committed clause and no VAR-F repair
      touches it. Rider (ii)'s informativeness measurement (section B: sd
      3.86e-3 to 7.84e-2 across bases at every lattice, with abs(det B_i)
      bit-identical, plus the F0-versus-F0|fib_s2 contrast) is made OUTSIDE the
      instrument and is likewise untouched. The n = 1 constructed false-refusal
      instance therefore survives as a G-REL1 fact; its "ADMITTED by G-VAR2"
      half is instrument-conditional.
  - id: O-9
    severity: medium
    title: >-
      The ledger archive TASK-20260812-655fe9 will produce a D3/DEF-3 defective
      commit unless this report's SIXTEEN probe paths are added to the declared
      set. As the queue stands, my task declares ONE artifact_path.
    detail: >-
      An archive task's declared path set is its own artifact_paths UNION its
      source tasks' artifact_paths, and the completed archive's commit must
      change EXACTLY that set. TASK-20260812-696cd4's `artifact_paths` in
      dispatch_queue.json lists only `red_team_report.md`. Committing this
      report together with its probes — which the completion gate REQUIRES to
      exist — would change 17 paths against a declared set of 1. That is
      precisely the error that made two BATCH-9e3584 archives terminally
      unverifiable. The full list, with sha256, is in section 9 below.
  - id: O-10
    severity: low
    title: >-
      Independence in this review is procedural only, and it is also not
      environmental.
    detail: >-
      AGENTS.md rule 12 is UNMET AND UNWAIVED and is not waived here.
      Additionally, and stated because no earlier record in this batch states
      it: this reviewing session runs on the SAME host and the SAME stack as
      every producer (Linux-6.18.5-fc-v20-x86_64, python 3.11.15, numpy 2.4.6,
      4 cores, fpylll ABSENT). My re-derivations are therefore procedurally
      independent and environmentally CORRELATED, and any agreement between my
      float numbers and a producer's carries no cross-platform weight
      whatever — the same limit rider (iii) correctly imposes on itself.
  - id: O-11
    severity: low
    title: >-
      Rider (iii)'s `ENVIRONMENTS_DIFFER = False` is a statement about the
      RECORDED fields, and rider (iii) itself supplies the counterexample field.
    detail: >-
      Rider (iii) measured that pip resolved a wheel vendoring libfplll 5.5.0
      while the producer's committed environment block records no fplll version
      at all, and states the agreement is UNKNOWN. So the honest boolean is
      RECORDED_FIELDS_DIFFER = False, not ENVIRONMENTS_DIFFER = False. The
      refusal it supports is nevertheless CORRECT AND CONSERVATIVE IN THE SAFE
      DIRECTION: if an unrecorded field did differ, 96-of-96 bit-identity would
      be MORE surprising, not less, so the unknown can only strengthen a
      portability reading that rider (iii) declined to take. Its generality is
      correctly bounded — L7/L8 only, beta in {5,10,15}, 8 bases, hkz and
      lam1n, one host — and it nowhere presents itself as resolving a doubt.
  required_controls:
  - id: RC-1
    control: >-
      BEFORE any successor specifies a replacement clause: re-run G-VAR2's F0
      refusal half with route R6_exact (exact-integer determinant) added, and
      report the F0 verdict with and without it. If F0 passes with R6_exact and
      fails without, the successor must replace PREREG-1 3.3's fallback and NOT
      AM-16(a). BUILT AND ALREADY RUN HERE: probes/probe_precision_null.py.
      Cost to re-run: 0.4 s.
  - id: RC-2
    control: >-
      Any future dispersion criterion must construct its fibre family PER
      CANDIDATE from that candidate's declared nuisance set, and must PRINT,
      per candidate and per fibre family, which declared arguments were
      verified constant across the basis index. The audit is
      probes/probe_argset.py section Q1 and costs under a second.
  - id: RC-3
    control: >-
      Any VAR-F-like clause must be evaluated at two working precisions and
      must report the ratio. A clause whose verdict changes with precision is
      reading a representation, not an observable. Cost: doubling the fibre
      evaluation, 0.2 s at this scale.
  - id: RC-4
    control: >-
      Any must-pass guard must publish the analytic reachability of its VOID
      row — the largest statistic reachable at the top of its frozen grid,
      against the threshold — BEFORE the run. Cost: a closed-form line;
      probes/probe_readings_and_guard.py part B.
  - id: RC-5
    control: >-
      Before the Coordinator rules on C-1, the tabulation must be extended to
      the UNNORMALIZED criterion value and to the summation-algorithm axis, or
      the ruling must state explicitly that it rests on one of several accounts
      of the count 2. probes/probe_readings_and_guard.py parts A3 and D. Cost:
      0.1 s.
  - id: RC-6
    control: >-
      NULL-OBJECT CONTROL FOR ANY FUTURE ADMISSION. Score X_hash — X_null plus
      c times a SHA-256 digest of the exact integer basis mapped into [0,1) —
      through whatever gate is proposed, at c in {1e-9, 1e-3, 1e-2, 1e-1}. It
      reads every entry of A and carries no lattice information whatever, so it
      calibrates how far "non-constant on its declared fibre" is from "carries
      lattice information". BUILT AND RUN: probes/probe_argset.py section Q3.
      Cost: 1.2 s.
  counterexample_or_mutation: >-
    THREE, ALL BUILT AND RUN, NOT PROPOSED.
    (1) THE ARGUMENT-SET MUTATION. F0|fib_dec — the seed-prefix-2 fibre family
    with A'[0,0] pinned across i, abs(det B) untouched, guard still holding.
    `X_lambda`'s full G-VAR2 verdict flips ADMIT -> REFUSE at 38/38 cells for
    lambda in {1e-1, 1} and 22/38 for lambda = 1e-2, under all six routes.
    (2) THE NEARBY OBJECT THAT SHOULD NOT FAIL. Route R6_exact: `rdet` from the
    exact integer determinant via `decimal` at 60 digits, everything else
    unchanged. G-VAR2 REFUSES it at 38/38 and F0's declared target is MET.
    (3) THE NULL OBJECT. X_hash at c = 1e-1: ADMITTED by G-VAR2 at 38/38 with
    VAR-S ADMIT (no scale degeneracy) and VAR-F PASS (no float noise), while
    carrying zero lattice information. At c = 1e-2 it is admitted at 27/38 and
    at c <= 1e-3 refused everywhere.
  baseline_comparison: >-
    NOT APPLICABLE IN THE POLLARD-RHO / BSGS SENSE AND SAID SO RATHER THAN
    OMITTED. This batch produces no algorithm, no attack, no solve, no relation
    and no cost model; the object under review is an INSTRUMENT (a dispersion
    criterion) and its "baseline" is its own predecessor. Against that baseline
    the comparison is: G-VAR (wave 1) was defeated by a change of arithmetic
    route; G-VAR was defeated by a 1e-10 additive perturbation (O-2); G-VAR was
    defeated by a one-line change of family (RT-R1); G-VAR2 defeats the
    perturbation route (P-V1 HOLDS, VAR-S refuses V_evade at 38/38 on six
    routes) and defeats the family route in F1 for X_null, but is defeated at
    its own reference point F0 by the SAME arithmetic-route mechanism that
    defeated its predecessor, now relocated from the scored family into the
    fibre clause. dominated_by: NOT APPLICABLE — there is no Pareto frontier of
    time, memory or data/queries here to be dominated on, and asserting `null`
    would be the fabrication AGENTS.md rule 5 names. sota_delta: NOT
    APPLICABLE for the same reason. TOY tier, instrument-only.
  heuristic_challenges:
  - >-
    NO HEURISTIC IS NUMBERED IN THIS BATCH BECAUSE NONE IS CLAIMED, and that is
    correct for an instrument batch. The exemplar-profile heuristic inventory of
    agents/red-team.md is therefore N/A with its reason rather than omitted.
  - >-
    The one quantity that behaves like an unnumbered heuristic is tau_var =
    1e-3. PREREG-1 3.4 states plainly that it is CALIBRATED ON COMMITTED
    NUMBERS and declares in advance that F0 is a weak test of the calibration.
    That disclosure is exemplary and I do not challenge it. What I challenge is
    the consequence nobody drew: a threshold calibrated to sit 7 orders above
    V_evade's 3.91e-10 and 1.4 orders below hkz's 0.023888 is, by construction,
    unable to separate anything in between — and the null object X_hash sits in
    between, at D_c ~ 1e-2 for c = 1e-1. tau_var's separating power is a
    property of the two calibration points, not of the observables.
  - >-
    The implicit heuristic that DOES need numbering for any successor:
    "non-constant on the fibre in IEEE-754 float64 == non-constant on the
    fibre". Measured false here at 38/38 cells for `rdet` under three of six
    routes. Any replacement clause must state it as a numbered assumption with
    a falsification condition, or must not depend on it.
  cost_model_challenges:
  - >-
    NO COST MODEL IS ASSERTED AND NONE MAY BE READ IN. Claim tier TOY. The only
    resource facts are instrument facts: the lead 2.037 s and 50.0 MB peak RSS;
    rider (ii) 0.762 s with peak RSS NOT INSTRUMENTED (GNU time absent) and no
    value invented; rider (i) peak RSS likewise not instrumented; rider (iii)
    0.054 s of reduction and 0.058 GiB. All are correctly reported as
    measurements or as not-measured.
  - >-
    Budget accounting, flagged for the Coordinator and NOT presented as
    misconduct: rider (i) declares maximum_runs 1 and enumerates FIVE
    invocations; rider (iii) declares maximum_runs 1 and enumerates SIX. Each
    enumerates exactly ONE measurement invocation and lists every other with
    its cause. Only one of the eleven produced numbers at all (rider (i)'s
    superseded left-to-right-sum implementation), and it was superseded rather
    than selected. The determinism of both pipelines on pinned inputs means no
    invocation could have been a re-roll. This report makes the same disclosure
    about itself: see probes/command.txt.
  - >-
    APPLIED TO MY OWN STATISTICS, as required. AM-10(a) replication: the
    lambda* statistic is replicated over four independent A draws (part C);
    the precision-ratio statistic is paired by construction (same basis index,
    two precisions) and reported at all ten lattices. AM-10(b) both
    normalizations: my relative-dispersion statistic is s/|m|; with s_X = 1.0
    and every |m| in [3.6, 292] the max(|X|, s_X) normalization coincides with
    it at every cell, and both s and m are reported so either can be formed.
    AM-10(c) a must-pass control: X_gso_k must be precision-invariant and is
    (ratio 0.9999991 to 1.0000001). AM-11 dispersion: my continuous lambda*
    carries min 3.1102e-03, median 6.5960e-03, max 1.4153e-02, sd 3.3672e-03
    over 40 draw-lattice pairs; my relative-dispersion statistic carries its
    full per-lattice range for both objects. Any statistic of mine not carrying
    both is named as such: the X_hash admission counts (38/38 at c = 1e-1,
    27/38 at c = 1e-2) are from a SINGLE hash and a single A draw and are NOT
    replicated — treat them as one constructed instance, n = 1, exactly as
    rider (ii)'s.
  reduction_and_scope_challenges:
  - >-
    SCOPE IS NOT INFLATED BY ANY PRODUCER, and I checked at the point of
    quotation rather than at the point of occurrence. Every occurrence of "29 of
    48" in this batch carries "47 of 48" in the same sentence (4 producer
    occurrences plus PREREG-1's own). "A factor of 6 to 31" appears only inside
    a non-citation statement. "Genuinely cross-platform" appears only inside a
    non-citation statement. No producer reports, estimates or implies a
    false-refusal RATE — grep over every rider (ii) artifact returns only
    disclosures that no rate exists.
  - >-
    THE ONE SCOPE STATEMENT THE DECISION MUST NOT INHERIT: PREREG-1 7.3
    licenses "a decision recording that the AM-16(a) operationalization does not
    reproduce its own declared target behaviour on the fixture it was written
    against". On the strict RD reading, AM-16(a)'s operationalization
    reproduced its declared target behaviour at every cell it decided, and did
    not decide the cells that failed. The licensed sentence is therefore true
    of the CONJUNCTION G-VAR2 and false of AM-16(a) alone. Write it about
    G-VAR2.
  - >-
    T-F0FAIL DOES NOT CLOSE THE ADMISSIBILITY-GATE LANE — that was T-F1FAIL —
    so this batch closes nothing, and no closure standard is triggered. The
    live risk is the opposite one and is named in objection O-3.
  - >-
    NOTHING HERE RETIRES AM-3, RESCORES BATCH-a44d08 IN ANY RESPECT, REVALIDATES
    BATCH-9e3584 OR BATCH-cbe023, OR CLOSES, PAUSES OR COMPLETES
    GOAL-MLKEM-005. The G-VAR refusal remains cited only as conditional on the
    frozen family F0. AM4-OBS-1 is cited only through KN-FIND-f38a89 and is not
    cited here at all.
  proof_architecture_challenges:
  - attack: OBSERVATION-FIBER
    result: >-
      SUCCEEDED. Hold the observation (`rdet`'s value, and its exact fibre
      constancy) fixed and vary the arithmetic route: R0/R1/R3 give REFUSE and
      R2/R4/R5 give ADMIT at the same 38 cells. Two preimages of the same
      observable land on opposite sides of the conclusion. THE MISSING
      SEPARATOR IS A SCALE: the fibre clause's fallback is scale-free, so it
      cannot distinguish 4.18e-11 from 9.02e-02.
  - attack: QUANTIFIER-ORDER
    result: >-
      SUCCEEDED ON ONE CLAUSE. PREREG-1 3.3 quantifies as "for each candidate X,
      let F|fib be the fibre sub-family holding X's declared nuisance arguments
      fixed" — a family chosen AFTER the candidate. The implementation
      quantifies the other way: one family pair, fixed before any candidate.
      Measured mismatch at A[0,0] for `V_evade` and `X_lambda` (objection O-1).
  - attack: BOUNDARY-AND-STRICTNESS
    result: >-
      PARTIAL. G-VAR2 does strictly improve on G-VAR against the perturbation
      route (P-V1 HOLDS at 38/38 on six routes) and against the family route
      for X_null in F1 (REFUSE at 38/38 on six routes). It does NOT strictly
      improve against the arithmetic-route attack: the old boundary is not
      embedded, it is re-imported, because 3.3's fallback IS the old
      bit-identity statistic.
  - attack: METHOD-CEILING
    result: >-
      The ceiling of any scale-free bit-identity test under ideal tuning is
      "distinguishes exactly-equal floats from unequal floats". Machine
      epsilon guarantees that unequal inputs give unequal floats through any
      route that sums d logs. The ceiling therefore cannot reach "distinguishes
      reads-the-instance from reads-a-nuisance-parameter". The headline fails
      before implementation, and the measurement confirms it.
  - attack: NEARBY-OBJECT
    result: >-
      BUILT (route R6_exact). The closest object for which the desired
      conclusion is FALSE — `rdet` with the float representation removed — is
      correctly refused at 38/38. The missing problem-specific ingredient is
      therefore precisely "read the determinant exactly, or supply a scale".
  - attack: COMPOSITIONAL-INVARIANT
    result: >-
      Deleting VAR-S from the conjunction changes nothing for `rdet` (VAR-S is
      scale_degenerate at every cell), which is the first reduction step that
      fails: the strong invariant "VAR-S AND VAR-F" does not imply the target
      "refuses parameter-determined observables", because the conjunction
      degenerates to VAR-F alone for every beta-free candidate — and PREREG-1
      3.2 says so in advance.
  narrowest_supported_statement: >-
    ON THE FROZEN FAMILY F0, at q = 3329, d in {20,30,40,100,140}, the frozen k
    and beta grids, 8 bases per lattice, fibre seed prefixes 2/3/4, six declared
    arithmetic routes, numpy 2.4.6 float64 on one 4-core host, and CLAIM TIER
    TOY: G-VAR2 as frozen by PREREG-1 section 3 ADMITS the parameter-determined
    candidate `rdet` at 38 of 38 scored cells through routes R2, R4 and R5, so
    fixture F0 FAILS and the frozen branch T-F0FAIL fires, correctly, with the
    -PARTIAL suffix and NOT through the fpylll gap. The admission is decided by
    PREREG-1 3.3's bit-identity fallback at scale_degenerate fibre cells, is a
    float-representation effect that tracks machine epsilon over 7 to 9 orders
    and vanishes exactly under exact-integer arithmetic, and survives a BLAS
    thread-cap control. AM-16(a)'s own statistic decided none of those cells.
    Separately, and on the same tested scope: G-VAR2's verdict on the frozen
    candidate `X_lambda` at lambda >= 1e-2 is determined by which fibre family
    instantiates the declared argument set, flipping at 38 of 38 cells under
    all six routes between the fibre PREREG-1 2.3 builds and the fibre
    PREREG-1 2.4 declares. NOTHING ABOVE bears on ML-KEM, on any FIPS 203
    parameter set, on any attack cost, on any cost model, or on whether any
    observable carries lattice information; nothing above closes, pauses or
    completes GOAL-MLKEM-005, retires AM-3, or rescores BATCH-a44d08.
  next_concrete_action: >-
    ONE ACTION, FOR TASK-20260812-655fe9 AND THE DECISION IT CARRIES: add this
    report's SIXTEEN probe paths (section 9, with sha256) to the archive's
    declared path set BEFORE staging — otherwise the commit changes 17 paths
    against a declared 1 and is the D3/DEF-3 defect for the third time in this
    goal — and write the decision's MEANS clause about the CONJUNCTION G-VAR2
    rather than about AM-16(a), naming PREREG-1 3.3's bit-identity fallback as
    the measured locus and route R6_exact as the built control that meets the
    F0 target. The successor's first task is then NOT a seventh dispersion
    statistic but a one-line question with a frozen answer: does the fibre
    clause read the observable, or its floating-point representation?
  artifact_paths:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/red_team_report.md
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/probes/command.txt
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/probes/probe_argset.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/probes/probe_argset_output.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/probes/probe_argset_stdout.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/probes/probe_argset_stderr.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/probes/probe_precision_null.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/probes/probe_precision_null_output.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/probes/probe_precision_null_stdout.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/probes/probe_precision_null_stderr.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/probes/probe_precision_null_threads1_output.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/probes/probe_precision_null_threads1_stdout.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/probes/probe_precision_null_threads1_stderr.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/probes/probe_readings_and_guard.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/probes/probe_readings_and_guard_output.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/probes/probe_readings_and_guard_stdout.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/probes/probe_readings_and_guard_stderr.log
  inference_provenance:
    requested_policy: review-adversarial
    resolved_model_id: claude-opus-5
    resolved_model_id_basis: >-
      The model that answered this session, as reported by the runtime to the
      session itself. Recorded beside the requested policy as required. NOT a
      probe result.
    reasoning_effort: xhigh
    reasoning_effort_basis: >-
      Bound by .claude/agents/red-team.md `effort: xhigh`, derived by
      orchestration/roles.yaml from default_policy review-adversarial. Honoured
      by the runtime binding rather than asserted here.
    fallback_used: false
    fallback_allowed: false
    degraded_allowed: false
    model_verified: false
    model_verified_reason: >-
      RECORDED AS A VERIFICATION GAP, NEVER AS SATISFIED. No adapter probe
      receipt exists for this session; AUTORESEARCH_POLICY and
      AUTORESEARCH_BACKEND are unset; per CLAUDE.md the resolved model cannot be
      probed from inside a subagent. Identical gap and identical reason as every
      producer and review in this batch and in BATCH-9e3584.
    independent_session: true
    independence_kind: >-
      PROCEDURAL, AND NEVER MODEL-LEVEL. AGENTS.md rule 12 is UNMET AND
      UNWAIVED in this goal and is not waived here. See objection O-10: this
      session is also environmentally correlated with the producers.
    shell_held: true
    commits_made: 0
```

---

## 1. WHAT WAS READ, AND WHETHER IT WAS READ COMMITTED OR UNCOMMITTED

Verified by me, in this session, with `git`. **Every producer artifact in this
batch was read COMMITTED.** No producer artifact was read uncommitted; had one
been, this section would say so.

| artifact | commit | committed? |
|---|---|---|
| `tasks/TASK-20260812-34b86c/prereg.md` (PREREG-1) | `8d72f2c03` | COMMITTED |
| `tasks/TASK-20260812-34b86c/prereg_sha256.txt` | `8d72f2c03` | COMMITTED |
| `archives/TASK-20260812-1ed548/snapshot-receipt.json` | `8d72f2c03` | COMMITTED |
| lead: `measure_gvar2.py`, `results_gvar2.json`, `report_gvar2.md`, `command.txt`, `stdout.log`, `stderr.log`, `run_manifest.yaml` | `3aac83fd8` | COMMITTED |
| `archives/TASK-20260812-b581a8/snapshot-receipt.json` | `3aac83fd8` | COMMITTED |
| riders (i), (ii), (iii): 7 files each | `d38514d22` | COMMITTED |
| `archives/TASK-20260812-b53c2f/snapshot-receipt.json` | `d38514d22` | COMMITTED |
| `results_relvar.json` (BATCH-9e3584) | on `HEAD` | COMMITTED |
| `probe_nullroute.py`, `probe_gvar_family.py` + outputs | on `HEAD` | COMMITTED |
| `DEC-20260812-7c4a1e.yaml`, `DEC-20260808-05b684.yaml` | on `HEAD` | COMMITTED |
| `dispatch_queue.json`, my `task_card.md` | on `HEAD` | COMMITTED |
| **my own report and probes** | none | **UNCOMMITTED — PD-4 proper, open** |

`git status --porcelain` at the time of writing shows exactly one untracked
path, `coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/`,
containing this task's directory and the concurrent Validator's. The working
tree is otherwise clean; `git diff` between each snapshot commit and `HEAD`
over the batch's `tasks/` tree is EMPTY, so the bytes I read are the bytes that
were committed.

### 1.1 The three-way archive split, verified BY ME

I did not take the Coordinator's word for this. `git diff-tree --no-commit-id
--name-only -r` on each commit:

| commit | subject | files changed | expected | producer artifacts |
|---|---|---|---|---|
| `8d72f2c038a577e216ab9d6d0e5995f65d5ff819` | notarize PREREG-1 | **3** | 3 | **ZERO** |
| `3aac83fd8a7293f1311db710a0d5b9beb9e7982d` | lead producer | **8** | 8 | 7 + receipt |
| `d38514d228b4a9e523e82e0b606f72ae3eeef9ff` | three riders | **22** | 22 | 21 + receipt |

All three are ancestors of `HEAD`. Each receipt rides inside its own commit
with `commit_sha: null` (the mandatory pattern) and its `path_sha256` block
carries 2, 7 and 21 entries respectively — receipt + declared = 3, 8, 22, set
equality exact. I recomputed every one of those 30 hashes against the working
tree: **zero mismatches**. The notarization property holds: `prereg.md` is
absent at `8d72f2c03`'s parent `18dd3819b`.

**The split-producer notarization pattern held for a fifth time.** Reported at
full weight because it is the one thing in this goal's archive history that has
never failed.

---

## 2. THE PRIMARY TARGET — THE DECLARED ARGUMENT SET. BUILT.

PREREG-1 3.5, before any measurement: *"It moves a free parameter; it does not
remove one. ... the **declared argument set** is now the free parameter ...
A reviewer should attack exactly there."*

### 2.1 The declared argument set does not enter the computation

`measure_gvar2.py` evaluates VAR-F on `FIBRE_OF[family]` — two lists, fixed
before any candidate is named. The per-candidate declared set enters only as the
output string `fibre_nuisance_held_fixed`. PREREG-1 3.3 quantifies the other
way round: *"Let `F|fib` be the fibre sub-family of section 2.3 holding **X's
declared nuisance arguments** fixed across the basis index."* PREREG-1 2.4
declares, for `V_evade` and `X_lambda`, the nuisance set **`abs(det B), A[0,0]`**.

Measured at all six fibre families and all ten lattices
(`probes/probe_argset_output.json` → `Q1_fibre_family_audit`):

| fibre family | `abs(det B)` fixed across 8 bases | `A[0,0]` fixed across 8 bases |
|---|---|---|
| `F0|fib_s2`, `F0|fib_s3`, `F0|fib_s4` | **yes at all 10 lattices** | **no at any lattice** |
| `F1|fib_s2`, `F1|fib_s3`, `F1|fib_s4` | **yes at all 10 lattices** | **no at any lattice** |

The guard PREREG-1 6.4 requires holds. The declaration PREREG-1 2.4 makes does
not.

### 2.2 The re-declaration that flips a verdict

`F0|fib_dec`: the seed-prefix-2 draw of 2.3, with `A'[0,0]` overwritten by its
`i = 0` value at every `i`. `abs(det B) = q^(d-k)` is untouched and still
bit-identical across the 8 bases. My unmodified control family reproduces the
lead's `F0|fib_s2` matrix-for-matrix
(`Q2_control_my_unmodified_fibre_equals_the_leads: true`). VAR-S is taken from
the lead's committed per-cell records for `V_evade` and computed on the SCORED
family F0 through the lead's own `var_s_from_cells` for `X_lambda`; VAR-F and
the conjunction go through the lead's own `var_f_from_cells` and `gvar2`.

| candidate | VAR-S | G-VAR2 ADMIT, fibre AS SCORED | G-VAR2 ADMIT, fibre AS DECLARED | cells flipping |
|---|---|---|---|---|
| `V_evade` (lambda 1e-9) | REFUSE 38/38 | 0/38 | 0/38 | **0**, all six routes |
| `X_lambda`, lambda 1e-4 | REFUSE 38/38 | 0/38 | 0/38 | **0**, all six routes |
| `X_lambda`, lambda 1e-2 | ADMIT 27, REFUSE 11 | 22/38 | **0/38** | **22**, all six routes |
| `X_lambda`, lambda 1e-1 | ADMIT 38/38 | 38/38 | **0/38** | **38**, all six routes |
| `X_lambda`, lambda 1 | ADMIT 38/38 | 38/38 | **0/38** | **38**, all six routes |

The flip is **route-robust** because `X_lambda` is beta-dependent, so its fibre
`R^fib_{d,k}` is non-zero and VAR-F takes the SCALED path rather than the
bit-identity fallback: at `L1_b15` under R2, `s^fib` drops from 2.233e-02 to
2.211e-14 when `A'[0,0]` is pinned.

**AGAINST MY OWN THESIS, AT THE SAME WEIGHT.** The candidate the batch actually
scores — `V_evade` — does **not** flip. VAR-S refuses it either way, so the
conjunction refuses it either way and only the sub-clause moves. R2-OUT-3 is
untouched. The flip needs `lambda >= 1e-2`, and `X_lambda` at that amplitude
appears in this batch only inside the graded guard, which is adjudicated on
**VAR-S alone**. So O-1 changes **no outcome row of this batch**. It is a
statement about what the criterion would do next.

### 2.3 The null object, and what the separator actually separates

`X_hash(B, beta) = X_null(B, beta) + c * u(B)`, `u(B)` a SHA-256 digest of the
exact integer basis mapped into `[0,1)`. It reads **every entry of A** and
carries **no lattice information whatever**. Through the lead's own G-VAR2:

| c | VAR-S ADMIT | scale_degenerate | VAR-F PASS | **G-VAR2 ADMIT** |
|---|---|---|---|---|
| 1e-9 | 0/38 | 0 | 0/38 | 0/38 |
| 1e-3 | 0/38 | 0 | 0/38 | 0/38 |
| 1e-2 | 30/38 | 0 | 32/38 | **27/38** |
| 1e-1 | 38/38 | 0 | 38/38 | **38/38** |

**This is not a contradiction of anything G-VAR2 claims** — PREREG-1 3.5 says
in advance that passing carries no claim of lattice information — and I say so
rather than scoring a point. What it does is **measure the width of the
disclaimed gap**: the separator G-VAR2 implements is *"depends on the
presentation bits of A at relative amplitude >= tau_var"*, and the distance from
there to *"carries lattice information"* is at least the distance from a
cryptographic digest. A successor that reads a G-VAR2 admission as any kind of
positive signal is reading past 3.5.

Note the amplitudes coincide: the graded guard's crossing amplitudes are
`lambda* in {1e-2, 1e-1}` and X_hash is admitted at exactly `c in {1e-2, 1e-1}`.
The guard's resolution floor and the null object's admission threshold are the
same number.

**n = 1.** One hash, one A draw, no replication. Treated exactly as rider (ii)
treats its own instance.

---

## 3. IS THE F0 FAILURE REAL, OR AN ARTIFACT OF HOW THIS IMPLEMENTATION READS F0?

### 3.1 It is real, and the separation from the fpylll gap holds

Independently checked, three ways:

1. **By reading the code.** R2 is `numpy.linalg.qr`, R4 is `numpy.linalg.slogdet`
   of `B B^T`, R5 is `numpy.linalg.slogdet` of `B H`. `fpylll` appears only in a
   `try/except` that sets an environment string, and in the `lam1n`/`hkz` RD
   blocks. No failing path touches it.
2. **By re-execution.** `probes/probe_precision_null.py` reproduces the `rdet`
   R2 admission at 38/38 with numpy alone, on a host where fpylll is ABSENT.
3. **By dependency audit** (`probe_readings_and_guard_output.json` →
   `E_F0_failure_dependency_audit`): `F0_would_FAIL_from_rdet_alone: true`, and
   the only other miss is `rawtail|RD` at the single cell `L4_b95`.

**The separation is sound and I confirm it.** One bound worth recording, because
the lead does not state it: with the ADMITTED half uncovered, F0 could not have
been **PASS** on this host under any `rdet` outcome — the reachable alternatives
were FAIL and PARTIAL. So the fpylll gap removed `T-PASS`; it did not remove the
distinction between `T-F0FAIL` and `T-F1FAIL`, which is the distinction that
mattered.

### 3.2 It is a float-representation effect, and that is measurable

`docs/inventor-protocol.md` section 3: name the parameter that should destroy
the signal, and run the identical measurement on a null object of the same
shape.

- **Null object**: `rdet` on the fibre — reads zero entries of A, so its fibre
  dispersion cannot be information about A.
- **Real object**: `X_gso_k` on the same fibre through the same code path.
- **Parameter**: arithmetic precision.
- **Prediction, written into the probe before the numbers were read**: rdet's
  relative fibre dispersion tracks machine epsilon; X_gso_k's does not.
  Falsifier: either half failing.

Measured (`probe_precision_null_output.json`):

| object | relative fibre dispersion, float64 | float32/float64 ratio |
|---|---|---|
| `rdet` R1 | **exactly 0.0** at all 10 lattices | — |
| `rdet` R2 | 4.06e-14 … 1.43e-13 | 1.40e6 … 1.21e7 |
| `rdet` R4 | 3.05e-10 … 2.64e-09 | 3.65e6 … 5.91e8 |
| `rdet` R5 | 2.46e-14 … 1.02e-13 | 1.29e8 … 3.52e8 |
| **all rdet routes** | **max 2.64e-09** | **min 1.4e6, median 5.5e7, max 5.9e8** |
| `X_gso_k` RQ | 5.71e-04 … 1.09e-02 | **0.9999991 … 1.0000001** |

`eps32/eps64 = 5.369e8`. The null object's dispersion moves by up to 5.9e8 when
epsilon moves by 5.4e8; the real object's does not move at all. **The falsifier
did not fire in either direction.**

### 3.3 The nearby object that should NOT fail — and does not

Route `R6_exact`: `rdet = |det B|^(1/d)` from the **exact integer determinant**
via `decimal` at 60 significant digits. Observable, family, fibre family,
declared argument set, `tau_var` and both clauses unchanged; only the float
representation removed.

    R6_exact          VAR-F FAIL 38/38   G-VAR2 REFUSE 38/38   F0 target MET
    R2 float64        VAR-F PASS 38/38   G-VAR2 ADMIT  38/38   F0 target MISSED

Identical under BLAS threads pinned to 1. **The F0 failure localises entirely to
PREREG-1 3.3's bit-identity fallback reading a float.**

### 3.4 Two measurements against my own reading, at the same weight

1. **The effect is forced, not accidental.** The fibre dispersions sit at 170 to
   4.4e6 ULPs of the cell mean — exactly the accumulated rounding of a d-term
   float sum. Any host reproduces non-bit-identity with overwhelming
   probability. **The F0 failure is robust and is not a fluke of this machine.**
2. **The environment control does not rescue it.** With `OMP_NUM_THREADS`,
   `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`, `NUMEXPR_NUM_THREADS` and
   `VECLIB_MAXIMUM_THREADS` all pinned to 1, every `bit_identical` flag is
   unchanged at every lattice and route, and only two of forty float64 fibre sds
   move at all — `rdet|R5` at L4 and L5, in the 13th significant figure.
   `probes/probe_precision_null_threads1_output.json`.

---

## 4. IS IT OVER-CLOSED, UNDER-CLOSED, OR MIS-ATTRIBUTED?

**Not over-closed.** `T-F0FAIL` closes no lane — that was `T-F1FAIL` — so no
closure standard is triggered and no obstruction needs naming. The batch closes
nothing and says so.

**Not under-claimed.** The lead reports the failure at full strength, states
that F0 would fail from `rdet` alone, and does not soften it.

**Mis-attributed by one clause.** PREREG-1 7.3's MEANS text is *"AM-16(a) itself
needs replacing"*. Measured:

| clause | who decided the failing cells |
|---|---|
| AM-16(a) / VAR-S | **decided none of them** — scale_degenerate at 38/38, all six routes |
| PREREG-1 3.2, degenerate-scale rule | routed the decision to VAR-F alone |
| PREREG-1 3.3, bit-identity fallback | **decided all of them** |
| AM-17(c), the fibre separator | correct as specified — R6_exact meets the target |

AM-16(a) has exactly one independent miss in the batch: `rawtail|RD` at `L4_b95`,
`D_c = 4.876e-4` against `tau_var = 1e-3`. The lead itself records that a
reviewer who reads route RD as strictly requiring fpylll must read that whole
row as UNCOVERED. **Under the strict RD reading, AM-16(a) has zero misses and
the entire F0 failure belongs to clauses PREREG-1 froze in this batch.** Both
readings give F0 = FAIL and both give T-F0FAIL. They differ only in what the
successor is meant to replace — which is the whole content of the branch.

**The structural risk this creates.** PREREG-1 7.2's FORBIDS list bars *"a
seventh consecutive gate repair"*. 7.3's does not, and 7.3 is the branch that
fired. A decision that inherits 7.3's MEANS text verbatim licenses a seventh
scaled-dispersion statistic to repair a clause that decided nothing, while
leaving the deciding clause untouched. That is the failure mode symmetric with
premature closure, in its other direction: an unbounded repair loop. The
decision needs an explicit stopping condition, and section 8 below proposes the
narrowest one.

---

## 5. THE TERMINATION BRANCH — CHECKED CLAUSE BY CLAUSE

| requirement | checked | result |
|---|---|---|
| R2-OUT-V evaluated FIRST | `measure_gvar2.py` branch chain: `if not crossed_anywhere: VOID; elif F0 == FAIL: T-F0FAIL; elif F1 == FAIL: T-F1FAIL; else T-PASS` | **YES** |
| F0 evaluated before F1 | same chain | **YES** |
| "If F0 fails, T-F0FAIL fires whatever F1 does" | F0 = FAIL, F1 = FAIL, branch = T-F0FAIL | **APPLIED** |
| the reported branch is the branch the FROZEN clause fires | quoted clause matches 7.3 verbatim | **YES** |
| `-PARTIAL` suffix per 7.4 | fpylll absent, ADMITTED half uncovered | **CORRECT** |
| no infrastructure outcome narrated into a science branch | F0 failure is in the reduction-free half at 38/38; fpylll absence is reported only as coverage | **CORRECT** |
| latent gap: is there a branch for "F0 PARTIAL, F1 FAIL"? | 7.4 explicitly contemplates `T-F1FAIL-PARTIAL` and states F1 is unaffected by partial coverage of the ADMITTED half | **NO GAP — I checked and it holds** |

**Nothing to report against the branch.** Stated as plainly as the objections.

---

## 6. PER PRODUCER — THE ARRANGEMENT IN WHICH ITS CHECK COULD NOT HAVE FAILED, IN BOTH DIRECTIONS

### 6.1 The lead, TASK-20260812-56b9da

| direction | arrangement | did it run in it? |
|---|---|---|
| **could-not-FIRE** (criterion could never refuse) | `tau_var = 0`, or `D_c >= tau_var` everywhere by construction | **NO.** Measured: `X_null` in F0 has `s_c` exactly 0.0 at 38/38 under R0 and R1; the run emitted 1142 REFUSE verdicts. |
| **could-not-PASS** (criterion could never admit) | `tau_var` above every real dispersion | **NO.** Measured: `hkz` RC max `D_c` = 2.833e-1; `rawtail` RD max 8.751e-2; 302 ADMIT verdicts. |
| **VAR-F could-not-FAIL** | every fibre family holds X constant | **NO.** VAR-F PASSes at 38 cells in each of three `rdet` blocks and 37 in `rawtail|RD`. |
| **VAR-F could-not-PASS** | a fibre family that failed to hold the nuisance fixed | **NO for `abs(det B)`**, guarded and printed at every fibre family and lattice. **YES for `A[0,0]`** — objection O-1: for `V_evade` and `X_lambda` the fibre does not hold the declared nuisance fixed, so VAR-F passes them for a reason the declaration excludes. Unmeasured by the lead because the lead's fibre families are candidate-independent. |
| **P-G1 / R2-OUT-V could-not-FAIL** | the VOID row unreachable in the frozen grid | **YES, IT RAN IN THAT ARRANGEMENT.** Min `D_c` at `lambda = 1` is 7.1316e-02 = 71.3 x `tau_var`. PREREG-1 6.1 calls the row "live and not a straw man"; it was unreachable by a factor of 71 before the run. |

The lead's own could-not-fail section is honest, measured rather than cited, and
correct on the four arrangements PREREG-1 names. The two it misses are ones
PREREG-1 does not name.

### 6.2 Rider (i), TASK-20260812-78a6e3

| direction | arrangement | did it run in it? |
|---|---|---|
| **could-not-FIRE** (P-C1 could not be falsified) | if any reading trivially reproduced any count | **NO.** The falsifier — no reading reproduces either count — was reachable: wave 2's count does not reproduce under any of the tabulated readings or normalizations. |
| **could-not-PASS** (P-C1 could not hold) | if the committed file's fields could not reproduce a validator count at all | **NO.** Wave 1's 15-of-19 reproduces exactly, and my 28-cell grid finds that cell is the *unique* one yielding 15 of 19. |
| **hidden third arrangement** | if "reading" is defined so narrowly that the axis is closed by construction | **PARTLY YES, AND IT IS NOT A DEFECT.** With all 8 per-basis values bit-identical, EVERY symmetric reduction returns the same double — I tested seven, including four rider (i) did not name, and all agree bitwise. The reading axis is closed **by algebra**. That makes rider (i)'s Observation 1 unfalsifiable given the data, which is why its real work is on the normalization axis — where objection O-5 shows it is not closed. |

### 6.3 Rider (ii), TASK-20260812-4b8ede

| direction | arrangement | did it run in it? |
|---|---|---|
| **could-not-FIRE** (never refusable) | the candidate satisfies every clause by construction | **NO.** G-REL1 `rho = 0` exactly at all 10 lattices, both routes, all 8 bases, both normalizations; 0 of 8 passing bases everywhere. |
| **could-not-PASS** (never informative) | `X_gso_k` constant across the 8 bases | **NO.** Between-basis sd 3.86e-3 … 7.84e-2, 8/8 distinct doubles, with `abs(det B_i)` bit-identical — measured, and re-derived here at L7 (float64 fibre sd 9.0199e-02, reproducing rider (ii)'s 9.02e-02). |
| **the arrangement rider (ii) found itself** | VAR-F PASS obtained through a scale-free test that float noise also passes | **YES, AND IT SAYS SO IN F.1.** Objection O-8 quantifies what it costs: under a relative-dispersion repair at the same `tau_var`, `X_gso_k` fails at L2, L4, L5 — 15 of 38 cells. |

**On the `n = 1` claim specifically, as required.** I grepped every rider (ii)
artifact — script, JSON, report, manifest. Every occurrence of "rate" is a
disclosure that **no rate is reported, estimated or implied**. No proportion, no
percentage, no denominator over a population, and no sentence from which a rate
could be read appears anywhere. **The `n = 1` discipline holds.**

**On the informativeness half being demonstrated rather than asserted.**
Demonstrated, two ways, both outside the instrument: the between-basis sd table
at fixed `(d, k, q, |det B|)`, and the F0-versus-`F0|fib_s2` contrast at
identical determinant (per-index absolute difference 8.30e-03 to 1.81e-01). It
also states its own bound — this shows A-dependence, not lattice information —
and its F.5 objection is exactly right about `X_gso_k` being a presentation
statistic. **This is the strongest producer artifact in the batch.**

### 6.4 Rider (iii), TASK-20260812-0e930c

| direction | arrangement | did it run in it? |
|---|---|---|
| **could-not-FIRE** (P-L1 could not be falsified) | if the comparison were against values the same code had just produced | **NO.** The comparison is against the committed `results_relvar.json`, sha-pinned, read-only, produced by textually distinct code. 96 comparisons, max abs deviation 0.0, 96/96 bit-identical. |
| **could-not-PASS** (P-L1 could not hold) | if fpylll were absent or the pipeline unrunnable | **NO.** The install succeeded; 16 reductions, all `status: ok`. Had it failed, PREREG-1 8.3 forces an infrastructure outcome and no deviation may be reported — which is the correct handling and did not need to be used. |
| **the arrangement it self-identified** | identical environments make agreement unsurprising | **YES, AND IT REFUSED THE CLAIM ON THAT BASIS.** See O-11: the boolean should read RECORDED_FIELDS_DIFFER, and the unknown fplll field cuts in the conservative direction. |

**On its framing specifically, as required.** It is nowhere presented as
resolving a doubt — its own section 0 says "It RESOLVES NO DOUBT, THERE BEING
NONE TO RESOLVE" and section 7 repeats it. The one missing-dependency outcome
(INV-4, `/usr/bin/time` absent, exit 127, no Python ran) is classified as an
infrastructure event, is used as evidence about nothing, and in particular is
nowhere treated as evidence about `lam1n`, `hkz`, the 48 reductions or the
reported max violation of 0.0. It correctly distinguishes its own L7/L8-arm 0.0
from the committed all-lattice 0.0. AM-9 is applied and, better, made
structurally moot: the full 20-row integer Gram is handed to fpylll, so no `k`
convention can drift. **Nothing to report against the framing.**

---

## 7. THE CHEAPEST FALSIFIER OF EVERY HEADLINE, WITH ITS COST

| headline | cheapest falsifier | cost |
|---|---|---|
| R2-OUT-1 F0 = FAIL | Show `rdet`'s fibre values are bit-identical under R2/R4/R5 on some host. **RUN: they are not, at 38/38, under default and pinned BLAS threading, and the ULP analysis says they cannot be.** | 0.4 s, `probe_precision_null.py` |
| "the F0 failure was not reached through the fpylll gap" | Find one failing cell whose computation imports fpylll. **RUN: none exists; reproduced with numpy alone on an fpylll-free host.** | 0.4 s |
| "AM-16(a) needs replacing" | Show AM-16(a)'s statistic decided no failing cell. **RUN: `rdet` is scale_degenerate at 38/38 on all six routes; AM-16(a)'s only miss is one cell on a route the lead itself flags as possibly UNCOVERED.** | free, from the committed JSON |
| branch = T-F0FAIL-PARTIAL | Show the frozen chain fires a different branch. **RUN: it does not; precedence and 7.4 both check out.** | free, code read |
| R2-OUT-3 P-V1 HOLDS | Find a cell where VAR-S admits `V_evade`. Max `D_c` = 3.215e-10 against `tau_var` = 1e-3 — six orders of headroom. **Not falsifiable at this scale.** | free |
| P-G1 / R2-OUT-V does not fire | Show the VOID row was reachable. **RUN: it was not — 71.3 x below `tau_var` at the top of the frozen grid. The guard's binary pass is not evidence; its lambda* is.** | 0.1 s, `probe_readings_and_guard.py` part B |
| R2-OUT-4 `lambda*` in {1e-2, 1e-1} | Solve the exact linear identity. **RUN: continuous lambda* is 3.11e-3 … 1.42e-2; the eleven cells reported at 1e-1 cross at ~1.4e-2, a 7x over-statement from grid coarseness.** | 0.1 s |
| R2-OUT-6 "wave 2's count corresponds to a 5.71x threshold" | Find another (normalization, threshold) pair giving 2. **RUN: the UNNORMALIZED value at wave 2's own 6x threshold gives exactly 2 of 29 and 2 of 19, both boundary rules, and names the same two entries.** | 0.1 s, part A3 |
| R2-OUT-6 "the reading axis cannot explain C-1" | Find an eighth reduction that disagrees. **RUN: seven tested, all agree bitwise; closed by algebra. CONFIRMED.** | 0.1 s, part A2 |
| R2-OUT-7 P-FR1 HOLDS | Repair VAR-F's fallback and re-score. **RUN: under relative dispersion at the same `tau_var`, `X_gso_k` fails at 15 of 38 cells. The G-REL1 half survives; the G-VAR2 half does not.** | 0.4 s |
| R2-OUT-8 P-L1 HOLDS | Re-run on a genuinely different stack. **NOT RUN — fpylll is absent here and installing it is out of my scope. Cost if run: rider (iii) measured 24 s of install plus ~1 s.** Reported as not attempted, not as a null result. |
| "no false-refusal rate is reported" | Find a rate. **RUN: grep over all four rider (ii) artifacts returns only disclosures that none exists.** | seconds |

---

## 8. WHAT REMAINS OPEN, AND THE STOPPING CONDITION THE SUCCESSOR NEEDS

This batch closes nothing, so nothing here is a closure. What it has newly
narrowed, and what it has not:

**Narrowed.** The dispersion-criterion lane's obstruction is now named more
precisely than "a dispersion criterion cannot separate reads-the-instance from
reads-a-nuisance-parameter". The measured obstruction is: *a fibre-constancy
test evaluated on floating-point values cannot separate them, because machine
epsilon makes every route that sums d logs non-constant on the fibre; and a
fibre-constancy test evaluated exactly requires a scale, which reintroduces the
threshold the fibre clause was meant to avoid.* Both halves are measured here:
R6_exact supplies the first, and O-8's 15-of-38 supplies the second.

**Still open, and it should be said rather than inferred.** Whether a scale for
`scale_degenerate` fibre cells exists that separates `rdet` from `X_gso_k`
without being calibrated on them. The measured separation is 5.3 orders in
relative dispersion at float64 — genuinely wide — but `tau_var = 1e-3` sits
inside `X_gso_k`'s own range, and at float32 `rdet|R4` reaches 2.95e-01, above
any threshold that would admit anything. So the scale, if it exists, must be
declared **relative to the working precision**, not to the observable. Nobody in
this goal has tried that, and it is one line.

**The stopping condition.** The gate has now been repaired six times. PREREG-1
7.2 barred a seventh; 7.3, the branch that fired, does not. The narrowest bar
that does not prejudge the science: *no further dispersion criterion may be
specified in this goal until the successor states, as a numbered assumption with
a falsification condition, what "non-constant on the fibre" means at finite
precision.* That is a specification requirement, not a lane closure, and it
retires nothing.

---

## 9. EVERY PATH THIS TASK WROTE — DECLARE ALL SEVENTEEN OR THE ARCHIVE FAILS

`TASK-20260812-696cd4`'s `artifact_paths` in `dispatch_queue.json` lists **one**
path. This task wrote **seventeen**, because the completion gate requires built
probes with recorded output. An archive that commits seventeen against a
declared one is the **D3/DEF-3** defect that made two BATCH-9e3584 archives
terminally unverifiable. All seventeen, with sha256 as of writing, relative to
the repository root, all under
`coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/TASK-20260812-696cd4/`:

    <this file>                                       red_team_report.md
    06f92593b51cfc67473bb4b2c3fcc0b9a233f11bfe8c06b13116e09fccc8dbde  probes/command.txt
    b87ff9bd4fa8d1b5e5ad90fe84cd531c4cbf92ffefefc2e6d3b1237a138f8f8b  probes/probe_argset.py
    b8a063a3f63166430d616d2c227c027590e3f02504cc714519a63092cf53dd0b  probes/probe_argset_output.json
    11aae960665ddf16ce71443d2cdb1f1b7a96732d79133fee2bc2dfb2c299b12a  probes/probe_argset_stdout.log
    e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  probes/probe_argset_stderr.log
    c7f18ec2f4f6c282a5e60f38c23e8d5d493c24018c1fd55479bb9198c1c8e87c  probes/probe_precision_null.py
    3c183c998f10e98a40c3a77940ef773ed6cb7d32658c4addf0c68a530bcbd735  probes/probe_precision_null_output.json
    3cdb3ef8f980c1c21c447b009f28d500b9f72a57ad87570ed2c6e97f936feea3  probes/probe_precision_null_stdout.log
    e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  probes/probe_precision_null_stderr.log
    c00eccbc5b15b3c21ab7e91e7c1d1fdaadd958928286ec5423dd03d6ef97e1be  probes/probe_precision_null_threads1_output.json
    074768116a6db991ec46079074d029c48aef06fee02e56c74f14d061690f21f8  probes/probe_precision_null_threads1_stdout.log
    e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  probes/probe_precision_null_threads1_stderr.log
    0fec11e3299b569118efec3bf8c623992e1700c15c27562ad91db59851426fee  probes/probe_readings_and_guard.py
    a94dcf45c2858ebd4835524c9b4fefb631758c59e3218a46e559aac41e5055b1  probes/probe_readings_and_guard_output.json
    976fe957e1f3e169c46c3e18149743188973864215f0f7cd581ee8fd6a62fbdd  probes/probe_readings_and_guard_stdout.log
    e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  probes/probe_readings_and_guard_stderr.log

`e3b0c442…` is the sha256 of the empty file; four stderr logs are empty, and
that is their measured content, not an omission. The three empty stderr logs and
`red_team_report.md` itself must be in the declared set too — a file's emptiness
does not exempt it.

**No file outside this task's `write_scope` was created, modified or deleted.**
`knowledge/INDEX.md` was not written, regenerated or staged. Nothing was
committed. `PYTHONDONTWRITEBYTECODE=1` and `python3 -B` were set for every
invocation and `sys.dont_write_bytecode = True` is set at the top of each probe;
**no `__pycache__` exists in this task's directory.**

**One observation outside my scope, recorded rather than acted on.** Four
`__pycache__` directories exist elsewhere under `GOAL-MLKEM-005`, at
`BATCH-9e3584/tasks/TASK-20260809-311784/` (15:32), the two BATCH-9e3584 probe
directories (20:58) and the concurrent Validator's own `probes/` directory
(21:49). My first Python invocation was at 21:49 and created none of them; I
deleted none, since deleting outside my write scope is itself a violation. They
are gitignored at repository root and therefore cannot enter any change set,
which is why they are an advisory to the archive task and not a defect.

---

## 10. SCOPE, BINDING CARRIES, AND WHAT THIS REPORT CANNOT DO

**SCOPE.** q = 3329; d in {20, 30, 40, 100, 140}; the frozen k and beta grids;
8 bases per lattice per family; families F0, F1, their fibre sub-families at
seed prefixes 2, 3 and 4, and one new fibre family `F0|fib_dec` built here; six
declared arithmetic routes plus one exact-integer route built here; float32,
float64 and `decimal`-at-60-digits; numpy 2.4.6 on one 4-core host with fpylll
ABSENT; no reduction was run at all. Every observation transports nowhere.

**BINDING CARRIES, in force and not re-litigated** (PREREG-1 11 and 11.1 in
full): AM-10 through AM-14 (DEC-20260808-05b684); AM-15 and AM-16
(DEC-20260809-afe29b) as extended by AM-17 (DEC-20260812-7c4a1e); **AM-3 IS NOT
RETIRED** and its 0.096 family-wise false-failure bound stands, and nothing here
retires it; **BATCH-a44d08 IS NOT RESCORED IN ANY RESPECT** and its Section C
verdict and detection floors remain VOID IN BOTH DIRECTIONS; AM4-OBS-1 is cited
ONLY through `knowledge/findings/KN-FIND-f38a89.md` and is not cited here;
**AM-9**: fpylll's k counts the q-scaled rows, NOT the identity block; **the
G-VAR refusal is cited ONLY as conditional on the frozen family F0**; the
split-producer notarization pattern and the receipt-with-`commit_sha: null`
pattern are retained; `knowledge/INDEX.md` is not written, regenerated or
staged; **CLAIM TIER STAYS TOY**.

**NOT CITABLE ANYWHERE IN THIS BATCH, carried at the point of quotation.**
"A factor of 6 to 31" is **FALSE** — the citable range is **4.87x to 31.03x**;
"no admissibility claim is reportable in either direction" is replaced by
DEC-20260812-7c4a1e C-2's three-part decomposition; the **"genuinely
cross-platform"** reading of the L7/L8 agreement is not citable and the citable
form is a PORTABILITY result across three textually distinct implementations
with fpylll pinned at 0.6.4; **both sub-6x counts remain NOT CITABLE** pending
the Coordinator's ruling on rider (i), and objection O-5 makes them no more
citable, only less uniquely explained; "the null fires more often than the real
arm" as a general statement; "G-VAR cannot be tuned into or out of firing" is
FALSE; "three predictions of actual empirical content" — the official count for
BATCH-9e3584 Section R remains ONE; the blanket "Residuals are 0 identically" —
cite per transform; "the obstruction is relocated"; "CONSISTENT" in either
direction; **"29 of 48" without the exact-null benchmark of 47 of 48 in the same
sentence** — this report makes no use of either figure and restates the pairing
because the carry binds at quotation; the 3.91% floor without its
NEGATIVE-VARIANCE-COMPONENT qualifier, the non-degenerate figure being 10.83%.

**WHAT THIS REPORT CANNOT DO.** It cannot say anything about ML-KEM, any FIPS
203 parameter set, any attack cost or any cost model. It cannot measure a
false-refusal rate and reports none. It cannot establish that any observable
carries lattice information, and X_hash in particular establishes the opposite
direction: that G-VAR2 admission does not imply it. It cannot revalidate
BATCH-9e3584 or BATCH-cbe023, cannot retro-validate any verdict, cannot change a
hypothesis status, and cannot close, pause or complete GOAL-MLKEM-005. It does
not decide which termination branch fired — that is read off R2-OUT-1 and
R2-OUT-2 under R2-OUT-V's precedence and nowhere else — and it does not
adjudicate C-1. Every repair sketched in section 8 is a Coordinator act in a
successor record and is specified by nobody here.

**INDEPENDENCE.** Procedural only, never model-level. AGENTS.md **rule 12 is
UNMET AND UNWAIVED** in this goal and is not waived here; `model_verified:
false` with its reason, recorded in section 0. See objection O-10: this session
is also environmentally correlated with every producer, running on the same host
and the same stack, and no agreement between my float numbers and a producer's
carries cross-platform weight.
