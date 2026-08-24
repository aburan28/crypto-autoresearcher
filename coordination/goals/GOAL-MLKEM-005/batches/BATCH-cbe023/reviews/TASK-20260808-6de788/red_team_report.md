# Red team — BATCH-cbe023, Sections A, B and C

TASK-20260808-6de788 / BATCH-cbe023 / GOAL-MLKEM-005.
Governed by the frozen contract `tasks/TASK-20260808-35efa3/prereg.md`,
sha256 `2da554914e5d78146c1e6cafcdbd109aacbc1a1624ed1f8e94ae769f757fc4f8`
(recomputed at the shell in this session; agrees with `prereg_sha256.txt` and
with the value in the task card).

**Claim tier TOY, unconditionally.** Nothing in this report bears on ML-KEM
security, on any FIPS 203 parameter set, on any attack cost, or on any cost
model. Every object I built is at `d <= 140`, `q <= 3329`. I changed no
research status, disposed of no hypothesis, promoted nothing to knowledge,
**rescored no frozen verdict**, modified no producer artifact, and made no
commit.

## Inference record (verbatim, as directed)

```
requested_policy: review-adversarial
resolved: anthropic:claude-opus-5 (effort=xhigh) via
  `orchestration.adapter resolve --role red-team --independent-session`
fallback_used: false
independent_session: true
model_verified: false
model_verified_reason: >-
  Per CLAUDE.md, per-role model and effort selection is process-level under Claude Code
  and subagents keep model: inherit. The session model is claude-opus-5, matching the
  resolved binding, but the xhigh tier cannot be probed from inside a subagent and no
  adapter probe receipt exists. Recorded as a verification gap, not claimed as satisfied.
```

Independence in this batch remains **procedural**, never model-level.
`AGENTS.md` rule 12 is UNMET and UNWAIVED in this goal.

## What I reviewed

Snapshot commit `6bafef86241fe3d70c21c3e30ed66d99b1f699ea`,
"research: GOAL-MLKEM-005 TASK-20260808-a6a336 snapshots all three BATCH-cbe023
producers". `git diff 6bafef862 -- .../BATCH-cbe023/tasks/` is **empty**, so the
working-tree bytes I read are the committed bytes. I produced none of these
artifacts.

The shared worktree's `HEAD` advanced during this session (`ce3b070a9` at start,
`19880b379` at the end) through commits belonging to other campaigns.
`git merge-base --is-ancestor 6bafef862 HEAD` is TRUE at both, and the diff
above is empty at both, so nothing I reviewed moved. Recorded rather than
smoothed.

**Snapshot completeness, recorded as an integrity observation.** The snapshot
carries 18 producer artifacts: 7 for TASK-20260808-2a9085, 7 for
TASK-20260808-cece0c, and **4** for TASK-20260808-3a5f18, which contributes no
`command.txt`, no `stdout.log` and no `stderr.log`. `AGENTS.md` "Artifact policy"
requires the exact command, stdout and stderr for every run. Section C's console
output is not auditable from this snapshot. See objection RT-C7.

---

```yaml
red_team_report:
  id: TASK-20260808-6de788
  task_id: TASK-20260808-6de788
  claim_under_review: >-
    BATCH-cbe023's three producer headlines: (A) OUTCOME R3, "admissible but not
    relevant -- the obstruction is RELOCATED, not removed", R1 empty; (B) "the AM-3
    gate CAN fire", 29 of 48 steps at c = 6, PRED-B1 met in all four cells; (C)
    VERDICT CONSISTENT, G-CAL met at 0/300 in four exact-null units, positive
    control fires at delta = 0.50 at all 10 targets.
  objections:
    - id: RT-A1
      severity: CRITICAL
      target: Section A headline R3 / "R1 is empty"
      statement: >-
        R1 was reachable throughout by an observable that carries no information about
        the lattice. I BUILT one and pushed it through the frozen gate: X_null(B,beta)
        = (beta/d)*(1/d)*log|det B|, s_X = 1.0, a closed-form function of (d,k,beta,q)
        with EXACTLY ZERO variance across the 8 frozen bases. It passes G-NUM
        (rho_T0 = 3.33e-14), G-INV (max rho over T1/T2/T3 = 4.71e-14 over 4800
        residuals), G-Q (1.0000) and BOTH clauses of G-REL (REL-1 = 3.1035,
        REL-2 = 0.6000). Under prereg 2.7 applied in order that is R1, ADMISSIBLE
        OBSERVABLE EXHIBITED. So "R1 is empty" is a fact about the ten-item candidate
        list, not about lattices, and the frozen gate does not certify that an
        admissible observable carries any lattice information.
      evidence: probes/probe_A1_null_observable.py + .out.json
    - id: RT-A2
      severity: CRITICAL
      target: G-REL, and whether it is doing real work
      statement: >-
        For X10 = hkz -- the ONLY candidate on the frozen list that could ever have
        reached R1 -- G-REL is a units convention, not a relevance test. rho uses
        max(|X|, s_X); s_hkz = 1.0 while every recorded |hkz| lies in [0.0661,
        0.4462], so the denominator is ALWAYS exactly 1.0 and the floor is 2.2x to
        15.1x the observable's realized magnitude. REL-2 therefore demands an
        ABSOLUTE move of 0.10 in a quantity whose whole range is 0.45. Under the
        ordinary relative difference that prereg 2.2 itself names ("where
        |X(B)| >= s_X the residual is an ordinary relative difference"), hkz clears
        REL-2 at 2 of 9 mirrored points (0.4036 at (20,beta=5); 0.1315 at
        (20,beta=10)) and REL-1 at all 6 (0.617-0.694). REL-2 requires only "at at
        least one beta of the grid". The headline flips R3 -> R1 on the
        normalization alone. An admissibility gate whose verdict changes when the
        statistic is multiplied by a constant is measuring units, not observables.
      evidence: results_am4.json gates.hkz.G_REL2.all; arithmetic in section A.2 below
    - id: RT-A3
      severity: CRITICAL
      target: Section A's could-not-PASS arrangement
      statement: >-
        prereg 2.10 names both directions for the INVARIANCE and SENSITIVITY criteria
        and NEITHER direction for G-REL. All three Form-2 guards (T0 noise floor;
        X8/X9 must pass G-INV; X8 must pass G-Q) protect G-INV and G-Q. No candidate
        on the frozen list is declared as a positive control that MUST pass G-REL.
        And by the prereg's own algebra 9 of the 10 candidates could not reach R1
        before any datum existed: six f(P) candidates are refused by OBS-GEN (a
        theorem in the prereg, not a measurement); X8 = rdet and X9 = lam1n take no
        beta argument at all, so REL-1 is identically 0 and the prereg SAYS SO in
        2.7; X7 = TRIV is a designed failure; and X4 = D has no measurable G-REL
        under the frozen D arm (one beta per cell, two non-mirrored cells). Exactly
        one candidate, X10, was live -- and it was scored under RT-A2's floor on a
        SINGLE basis. This is BATCH-a44d08's could-not-PASS failure mode relocated
        from the invariance gate to the relevance gate, in the batch whose
        pre-registration was written to catch it.
    - id: RT-A4
      severity: MAJOR
      target: G-REL1, G-REL2 and G-Q have no replication
      statement: >-
        measure_am4.py evaluates all three on basis index 0 only
        (`src.get((lat, lo, 0))`, `src.get((la, beta, 0))`), with no SE, no spread and
        no floor, while G-NUM and G-INV use the full 8x8 replication. The decisive
        number of the batch -- hkz's REL-2 = 0.0697 against tau_rel = 0.10 -- is one
        draw. This choice is NOT in the run's 10-entry `deviations` list; it appears
        only as the phrase "on 1 basis per cell" inside one detection-floor sentence
        in report section 8.3, and not at all for the f(P) candidates or for G-Q.
      evidence: measure_am4.py lines 1171-1213; results_am4.json deviations
    - id: RT-A5
      severity: MAJOR
      target: hkz's REL-2 number is basis noise, in both directions
      statement: >-
        I BUILT the missing replication: the same frozen construction and the same
        frozen HKZ pipeline at the mirrored pair L7 (20,6) / L8 (20,14) over all 8
        frozen bases, HKZ verified (max violation 0.0). At beta = 5 the mirrored gap
        has mean 0.00103 with a between-basis sd of 0.0239 (k=6) and 0.0392 (k=14) --
        the gap is ~3% of its own spread -- and the paired t over the 8 bases is
        -0.064 (df 7). At beta = 10 and 15: mean gaps 0.00065 and 0.00253, paired t
        = 0.088 and -0.784. The frozen gate's basis i = 0 is the LARGEST of the 8 at
        beta = 5 (0.0697 vs a median of 0.0326). Two consequences, and I report both:
        (i) it DEFEATS RT-A2 as a route to R1 -- hkz carries no block-attribution
        content at this cell, so R3 for X10 SURVIVES replication; (ii) it defeats the
        report's stated reason for R3 -- the correct statement is not "hkz falls short
        of 0.10 at 0.0697" but "the quantity being thresholded has an expectation
        indistinguishable from zero and a spread 20-40x its mean, so neither the
        0.0697 nor the 0.10 means anything". The frozen R1/R3 boundary is decided by
        a basis index and a normalization convention, neither of which is a fact about
        lattices.
      evidence: probes/probe_A2_rel2_replication.py + .out.txt
    - id: RT-A6
      severity: MAJOR
      target: R4 did not fire -- legitimate frozen scope, or a gap?
      statement: >-
        A gap, and a repairable one. prereg 2.4 excludes X4 from R4's trigger with a
        stated reason: D's probe outcome "is to be read against D's own SE floor" and
        "reported as an UPPER BOUND when it falls below that floor". It did NOT fall
        below the floor -- 0.15837 vs 0.021137 (7.5x) at L3 and 0.03447 vs 0.026745
        (1.29x) at L4. The exclusion was conditional on an outcome that did not
        occur, and the outcome map has no row for the outcome that did. So a
        refutation of AM4-OBS-1's premise is recorded in prose (report 4.2/4.3/4.4)
        and NOT in the outcome field. The Coordinator must carry it forward as a
        finding and should amend 2.7's R4 row rather than treat the non-firing as a
        scope decision.
    - id: RT-A7
      severity: MAJOR
      target: the six-exact-zeros lead, pushed further
      statement: >-
        The producer's disclosure is right and understated. The frozen collision probe
        is undefined on X8/X9/X10 (not projector functions) and returns arithmetic
        zeros on X1,X2,X3,X5,X6,X7 (manifest closed-form functions of diag(P)). It had
        testable content on exactly ONE of ten candidates, X4 = D -- and there the
        premise was REFUTED at both cells, above D's own floor at both. The honest
        record is therefore stronger than "nearly vacuous": AM4-OBS-1's premise clause
        is refuted at 1 of 1 testable candidates and corroborated at 0 of 0. No
        successor may cite the six zeros as corroboration, and none may cite the
        premise as holding for D.
    - id: RT-A8
      severity: MAJOR
      target: what else the mod-q construction voids besides G-RANK
      statement: >-
        G-Q. Under the frozen construction A = rng([1,d,k,i]).integers(0,q) the q = 1
        rung gives A = 0 and B = I_d exactly, so every G-Q value in the table is a
        comparison of a q-ary lattice against Z^d -- a change of LATTICE, not a
        change of q-ary structure at fixed lattice. That is why rdet passes G-Q at
        0.997 (covol(Z^d) = 1) and why my built null passes at exactly 1.0000. The
        producer's own SUPPLEMENTARY ladder B, which holds A at its q = 3329 draw and
        scales only the lower block, finds 1 - E_I bit-for-bit CONSTANT across the
        entire ladder including q = 1, under which E_I would FAIL G-Q. Correctly
        labelled POST-HOC and uncitable -- but the consequence for the FROZEN reading
        is not drawn: G-Q's demonstrated discrimination (X7 fails, X8 passes) is "a
        constant fails, and a covolume passes because Z^d has covolume 1", which is
        not evidence that G-Q separates informative from uninformative observables.
        RT-A1's null passes G-Q for exactly that reason.
    - id: RT-A9
      severity: MINOR
      target: G-INV for X9 and X10 under T1
      statement: >-
        Disclosed by the producer (deviation 5) and correct as far as it goes, but the
        strength should be stated plainly: for the Gram pipeline, G(BH) = BHH^T B^T =
        BB^T identically, so T1 -- the ONLY transform in the AM-4 triple that tests
        ISOMETRY-CLASS invariance rather than basis invariance -- is the exact
        identity on the input for X9 and X10. Their T1 residuals of 0.00e+00 are not
        a test that could have failed. Their T2/T3 residuals (<= 7.15e-15 and
        1.20e-14) ARE genuine and do establish basis invariance. So of the three
        candidates that "pass AM-4", one (rdet) passes by algebra (det multiplicativity
        under all three transforms) and two pass genuinely on the basis-change subgroup
        only. AM-4's ambient-isometry clause is untested for X9 and X10.
    - id: RT-A10
      severity: MINOR
      target: GEN-2's coverage for X10
      statement: >-
        PROBE-L separates hkz from the frame at 4.26e-04 of scale -- 23x BELOW the
        same gate's tau_inv = 0.01, the threshold at which it calls things invariant.
        So hkz is "not f(P)" at a margin the gate's own resolution treats as
        indistinguishable from invariance. Recorded by the producer as "the weakest of
        the three separations"; the inference is not drawn. Under the strict reading
        of report 1.1, GEN-2 fails anyway.
    - id: RT-B1
      severity: CRITICAL
      target: PRED-B1 could not fail
      statement: >-
        c_min is a deterministic closed form of Delta_i, SE_step(i) and SE_diff(t_i);
        the run reproduced those from the committed record BIT-EXACTLY (max dev 0.0 vs
        results_g3.json) and reproduced c_min at max dev 0.0 in two legs; the
        threshold 4 was set from a review measurement of the SAME map on the SAME data
        (6, 7, 9, 7). The falsifier is therefore empty conditional on the reproduction
        check passing -- and if reproduction had failed the arm would be
        INSTRUMENT-LIMITED and PRED-B1 would not be scored at all. I recomputed the
        counts independently from the committed per-step quantities and got 6, 7, 9, 7.
        The report calls this agreement "unexpected in its exactness"; it is forced.
        That is the same misreading the same batch correctly diagnosed for the
        collision probe's six exact zeros, applied to its own prediction. prereg 3.8
        Form 1 names only the vacuity of "fires at some c" and does not name this
        mirror.
      evidence: probes/probe_BC_artifact_arithmetic.py, block B-1
    - id: RT-B2
      severity: CRITICAL
      target: '"the AM-3 gate CAN fire -- 29 of 48 at c = 6" has no null object'
      statement: >-
        Section B carries NC-B1 (c = 0) and NC-B2 (c = -6), which are the same family
        under different injections, and no null OBJECT at all. I BUILT the missing one
        from the committed numbers: keep SE_step(i) and SE_diff(t_i) exactly and set
        Delta_i := 0, an EXACT NULL STEP with no descent and no increase. On that
        null, c_min has median 2.99 and n_fire(c = 6) = 47 of 48 (per cell 12, 11,
        12, 12); at c = 4 it is 42 of 48. So the headline 29 of 48 must be read
        against a null value of 47 of 48: the reported quantity is 62% of what a
        step with NO violation whatsoever produces, and it MOVES THE WRONG WAY as the
        true violation goes to zero. The gate's behaviour is correct -- at Delta = 0
        the post-injection increase is a real 6*SE_diff -- but the CLAIM is not a
        power demonstration. "n_fire(c=6) = 29" is dominated by the ratio
        SE_step/SE_diff and its null benchmark is nearly the maximum. The prereg's
        Form-1 guard (a count at a fixed c, plus c_min/4) does not discriminate
        either: the exact-null c_min/4 has median 0.75 against the realized 1.12-1.52.
      evidence: probes/probe_BC_artifact_arithmetic.py, block B-2
    - id: RT-B3
      severity: MAJOR
      target: '"c_min(i) > c_pos(i) verified at all 48 steps"'
      statement: >-
        An algebraic identity, not a verification. For every step with Delta_i <= 0,
        c_min - c_pos = 1 + t_crit*SE_step/SE_diff exactly; I checked this at 39 of 39
        such steps and it holds to 1e-9. At the other 9 steps c_pos = 0 by definition.
        The "closed-form guarantee" is the prereg's own algebra restated; 48/48 is
        arithmetic. The producer says a violation "would be an implementation error,
        not a finding" -- correct, and that is precisely why the check carries no
        evidential weight for the gate's power.
    - id: RT-B4
      severity: MINOR
      target: full-table scoring of PRED-B1
      statement: >-
        Defensible and disclosed: prereg 3.6 freezes full-table scoring with the
        excluded count printed beside it, and both numbers are printed. The d100_b30
        drop to 3 matters only in that it makes the demonstrated power at c = 6 on
        steps with no pre-existing increase 20 of 39 pooled and 3 of 9 in one cell.
        Given RT-B1 and RT-B2 the question is moot -- neither number is a power
        measurement.
    - id: RT-C1
      severity: CRITICAL
      target: the CONSISTENT verdict is invariant to the entire AM-7 repair
      statement: >-
        A FALSIFYING PAIR needs BOTH frozen conditions. The largest realized relative
        difference over all 10 targets is 14.12%, against tau_rel = 0.15. Condition
        (ii) therefore fails at EVERY target FOR ANY VALUE OF THE SE, including SE = 0
        (perfect precision, |t| = infinity). Section C exists to rebuild the SE; the
        rebuild could not have changed the verdict. "CONSISTENT" is determined
        entirely by tau_rel and not at all by AM-7. This is not disclosed.
      evidence: probes/probe_BC_artifact_arithmetic.py, block C-2
    - id: RT-C2
      severity: CRITICAL
      target: G-CAL does not test the rebuilt SE
      statement: >-
        G-CAL scores the JOINT criterion. I split it from the per-replicate |t|,
        nu_eff and relative difference recorded in results_am7.json: in the four exact
        nulls condition (ii) alone fires 0 of 1200 (p95 null relative 2.15%-4.40%
        against tau_rel = 15%), so the four 0/300 counts are carried ENTIRELY by the
        relative floor. "G-CAL PASSED at 0/300 four times" is a statement about
        tau_rel, not about the SE that AM-7 clause (1) is about. AGAINST MY OWN THESIS
        AND REPORTED AS SUCH: condition (i) alone fires 0, 0, 0 and 5 of 300 -- 5 of
        1200 overall, 0.42% against a nominal per-pair 0.909% -- so the rebuilt SE and
        its Satterthwaite nu_eff ARE calibrated, slightly conservatively. That is the
        evidence AM-7 clause (2) asked for and it is not in the report.
      evidence: probes/probe_BC_artifact_arithmetic.py, block C-1
    - id: RT-C3
      severity: CRITICAL
      target: the delta_min positive control repeats AM-6 clause (b)
      statement: >-
        measure_am7.py:501 `delta_min_control` performs NO injection and re-runs
        NOTHING. It is closed-form arithmetic in SE(Delta_bar), |Delta_bar| and M,
        algebraically equivalent to "is the detection floor below 50%". It therefore
        cannot detect SE inflation: inflate the SE, delta_min rises with it, and the
        control still reports "fires, at a bigger delta". prereg 4.10 Form 1 lists it
        as THE guard against "the falsifier could not FIRE"; it cannot serve that
        role. A control denominated in the very quantity under repair is exactly the
        defect AM-6 clause (b) names, inside the section the prereg calls "the mirror
        of AM-6's requirement, applied to Section C". It passed with 4 percentage
        points of margin at the worst target (largest floor 45.62% against the frozen
        0.50 clause) and 3 of 10 targets fire ONLY at the top grid point.
    - id: RT-C4
      severity: MAJOR
      target: where the power actually went -- and PRED-C2
      statement: >-
        I computed the plain sample SE of each target's own 8x4 Delta table. The
        rebuilt two-way SE is 0.36x to 1.37x it, median 1.05x -- and SMALLER than the
        naive SE at 4 of 10 targets, as low as 0.36x at d100_b30/unreduced. So the
        AM-7 repair added essentially NOTHING to the SE, which is exactly what
        PRED-C2's failure says (structural share >= 50% at 2 of 10). The entire power
        loss comes from Satterthwaite nu_eff (1.00 to 21.00, median ~3.5), which
        raises |t|crit from 2.783 at nu = 31 to a median of ~5.1 and to 70.023 at one
        target. PRED-C2's failure is NOT independent of the CONSISTENT verdict; read
        with RT-C1 it says the instrument was rebuilt, the rebuild did not enlarge the
        SE, and the verdict was untouched by it either way. Note also that at 4
        targets the rebuilt SE is SMALLER than the plain sample SE of the table it
        summarizes, which is in tension with AM-7 clause (1) as worded ("the SE must
        contain the variance that dominates it") and is not reported.
      evidence: probes/probe_BC_artifact_arithmetic.py, block C-2
    - id: RT-C5
      severity: MAJOR
      target: tau_rel = 0.15 was calibrated against an instrument the batch declares void
      statement: >-
        prereg 4.4's stated rule is "1.67x the top of the measured null median range",
        computed from 8.4%-9.0% measured on the SUPERSEDED instrument's nulls. The
        rebuilt nulls' median relative differences are 0.65%, 0.98%, 0.77% and 1.50%
        -- 6x to 14x smaller. prereg 4.5 required these "direct successors" to be
        reported; they are, and the comparison is never drawn. Applying the frozen
        rule to the rebuilt null gives tau_rel = 1.67 * 1.50% = 0.025, i.e. the frozen
        0.15 is 6x its own design rule. POST-HOC SENSITIVITY, NOT A RESCORING: at
        tau_rel = 0.025 there is still no FALSIFYING PAIR (condition (i) fails
        everywhere, max |t|/|t|crit = 0.885), but d140_b40/graded_t0.0050 becomes
        SUGGESTIVE under the frozen definition. The frozen "n_suggestive = 0" is a
        consequence of a floor set 6x above its own rule.
    - id: RT-C6
      severity: MAJOR
      target: how much of CONSISTENT is absence of power
      statement: >-
        Structurally, all of it. The verdict map awards CONSISTENT if ANY informative
        pair has floor < tau_rel. The four pairs that satisfy it are exactly the four
        with the SMALLEST realized effects (relative 0.26%, 1.88%, 3.46%, 7.27%),
        while the two LARGEST effects -- 14.12% and 9.43% -- sit at pairs whose floors
        are 15.95% and 18.84%, both above tau_rel. The clause certifies power where
        nothing is happening and is silent where something might be. It is satisfiable
        by any target with a small effect and a small SE. The producer's per-pair
        honesty ("six of ten pairs are upper bounds") is exactly right and should be
        the headline; "CONSISTENT" should not be.
    - id: RT-C7
      severity: MINOR
      target: artifact policy
      statement: >-
        TASK-20260808-3a5f18 contributes 4 artifacts to the snapshot
        (measure_am7.py, report_am7.md, results_am7.json, run_manifest.yaml) while the
        other two producers contribute 7 each including command.txt, stdout.log and
        stderr.log. AGENTS.md "Artifact policy" requires the exact command, stdout and
        stderr to be retained. Section C's console output is unauditable from the
        snapshot. This is an evidence-integrity gap, not a mathematical finding.
    - id: RT-X1
      severity: MAJOR
      target: batch-level -- AM-4 applied to what Sections B and C measure
      statement: >-
        AM-8 makes the AM-4 triple a pre-registration gate over EVERY candidate
        observable. Section A measures D's own invariance residuals at 1.10 (T1),
        0.263 (T2) and 0.225 (T3) -- REFUSED. Sections B and C then spend two of the
        batch's three producers repairing instruments whose objects (r = q_emp/q_Beta
        on graded frames; D, V, m3 at the 2^-10 quantile) sit inside the class Section
        A refuses. prereg 5.8 exempts them explicitly and both reports state it, so
        this is a disclosed scope limit rather than a violation -- but the Coordinator
        must not let "the gate CAN fire" or "CONSISTENT" be cited as evidence about
        any lattice, in any successor, for any purpose.
  required_controls:
    - id: RC-1
      for: Section A / G-REL
      control: >-
        Replicate G-REL1 and G-REL2 over the 8 frozen bases already built and report
        the between-basis mean, sd and a paired test, for every candidate. A relevance
        threshold applied to a single draw is not a criterion. I ran this for the
        L7/L8 pair; the remaining pairs are the same cost.
      cost: 0.22 s wall, 44.8 MB RSS, 1 core, for one mirrored pair at d = 20
            (measured). All five mirrored pairs are well under one minute.
      status: RUN by this review for L7/L8; NOT RUN by the producer for any pair.
    - id: RC-2
      for: Section A / G-REL normalization
      control: >-
        Report every G-Q and G-REL number twice -- once at max(|X|, s_X) and once at
        |X| -- with the ratio s_X/|X| printed, so a reader can see when the floor is
        the binding term. For hkz that ratio is 2.2 to 15.1.
      cost: arithmetic on results_am4.json, seconds.
      status: NOT RUN.
    - id: RC-3
      for: Section A / gate laxity
      control: >-
        Add a PARAMETER-DETERMINED negative control to the candidate list: any
        observable that is a closed-form function of (d,k,beta,q) with zero variance
        across the 8 bases MUST be refused, and no gate that admits one is admissible.
        X7 = tr(P^2) cannot serve: it is q-independent and k-independent, so it tests
        only whether G-Q refuses a constant. Equivalently: add a G-VAR criterion --
        an admissible observable must have non-zero dispersion across the frozen bases
        at fixed (d,k,beta,q).
      cost: 2.86 s wall, 55.8 MB RSS (measured, my probe).
      status: RUN by this review (RT-A1); NOT RUN by the producer.
    - id: RC-4
      for: Section B
      control: >-
        The exact-null step control of RT-B2, and better, a null FAMILY: regenerate
        the 13 grid points as 13 independent Haar frames from the carried seeds (pure
        numpy, no BKZ, no LLL -- the producer's own section 2 establishes the seeds
        are the cache) so E[Delta_i] = 0 at every step, and report n_fire(c=6) on it
        beside the 29. Any headline count must be quoted against its null count.
      cost: the closed-form null-step control is 0.73 s (measured). The full null
            family is 448 order statistics at N = 2^20, i.e. of order the producer's
            own reproduction leg, minutes, no reduction.
      status: closed-form version RUN by this review; null family NOT RUN by anyone.
    - id: RC-5
      for: Section C
      control: >-
        Report the null firing rate under EACH frozen condition separately. Condition
        (i) alone is the quantity AM-7 clause (2) is about, and it is the only one of
        the two that carries information about the rebuilt SE.
      cost: 0.73 s on the committed JSON (measured).
      status: RUN by this review; NOT RUN by the producer.
    - id: RC-6
      for: Section C
      control: >-
        A positive control that actually injects. Add the constant offset to the TL
        values and re-run the full scoring path (SE decomposition, nu_eff, both
        conditions) rather than evaluating the closed form. Only an executed injection
        can detect a defect in the path; the closed form is a restatement of the
        detection floor.
      cost: >-
        10 targets x 6 deltas x 32 D-values that are already in memory -- seconds.
      status: NOT RUN.
    - id: RC-7
      for: Section C
      control: >-
        Report SE_2way / SE_naive at every target. A ratio below 1 means the rebuilt
        SE is smaller than the plain sample SE of the table it summarizes, which is
        the opposite of AM-7 clause (1)'s requirement. It is below 1 at 4 of 10
        targets.
      cost: seconds on the committed JSON.
      status: RUN by this review; NOT RUN by the producer.
  counterexample_or_mutation: >-
    Two, both BUILT. (1) NULL OBJECT: X_null(B,beta) = (beta/d)*(1/d)*log|det B| with
    s_X = 1.0 -- zero variance across the 8 frozen bases, a closed-form function of
    (d,k,beta,q) -- reaches R1 under the frozen gate (G-NUM 3.33e-14, G-INV 4.71e-14
    over 4800 residuals, G-Q 1.0000, REL-1 3.1035, REL-2 0.6000). Its rdet cross-check
    through the same code path reproduces the producer's recorded residuals to the
    digit (T1 2.514254164288223e-13 vs 2.51e-13; T2 0.0; T3 9.728156273548676e-16 vs
    9.73e-16), so the pipeline is theirs. (2) UNITS MUTATION: multiplying X10 = hkz by
    10 -- an operation that changes nothing about the observable -- flips its G-REL
    verdict and hence the batch's headline from R3 to R1, because s_hkz = 1.0 exceeds
    every realized |hkz| by 2.2x to 15.1x. (3) The NEARBY-OBJECT control that decides
    between them: replicating REL-2 over the 8 frozen bases shows the mirrored gap has
    mean 0.001 against a between-basis sd of 0.03, paired t = -0.064, so hkz has no
    block-attribution content and R3 survives -- for a reason the report does not give.
  baseline_comparison: >-
    NOT APPLICABLE, and that is the correct entry. None of the three sections proposes
    an algorithm, a cost model, or an attack; all three state claim tier TOY and
    explicitly disclaim any bearing on ML-KEM, FIPS 203 or any attack cost. There is
    therefore no Pollard-rho, BSGS, sieve, or lattice-reduction baseline to compare
    against, and no dominated_by/sota_delta can be non-null. What the batch DOES have
    a baseline against is its own predecessor: BATCH-a44d08's instruments. On that
    axis Section B is a genuine improvement (the argmax-SE_diff selection is removed,
    not replaced), Section C's SE is genuinely calibrated on condition (i) (0.42%
    against a nominal 0.909%), and Section A's gate is a genuine advance over a
    post-hoc criterion (6560 residual samples per f(P) candidate against one session).
    Any successor that presents any of this against a cryptographic baseline must
    first supply the baseline; there is none here.
  heuristic_challenges:
    - >-
      OBS-GEN is stated in the prereg and the report as an argument to be checked and
      is correctly labelled "not a machine-checked proof". It is also, as stated, a
      THEOREM that decides six of the ten candidates before any datum: any O(d)-
      invariant function of the tail projector is constant. The batch's own numerical
      "verification" of it therefore cannot fail, and GEN-1's clause "every f(P)-class
      candidate fails G-INV or G-Q" is entailed by it, not evidence for it. This is
      disclosed in substance but the entailment is not stated.
    - >-
      AM4-OBS-1 is correctly treated as a measured argument rather than a theorem, and
      correctly tested. Its premise clause is now REFUTED for D at both cells above D's
      own floor. No successor may inherit it. See RT-A6 and RT-A7.
    - >-
      "Independent supports do not break the V-matching because V_TL and m3_TL depend
      on u alone" is a closed-form claim and is verified to 7.11e-15 / 1.78e-15. I have
      no objection to it.
    - >-
      The batch makes no exponent-first, heuristic-conditional claim of the
      docs/target-result-profile.md shape. Heuristic inventory, random-model transfer,
      scale honesty, hidden-overhead, cost bookkeeping, reduction instantiation and
      scope inflation are NOT ENGAGED because nothing here claims an exponent, a cost,
      a reduction or an affected scheme. Recorded as not-applicable rather than
      silently omitted.
  cost_model_challenges:
    - >-
      No cost model is claimed and none is challenged. The only cost statements are
      budget accounting: Section A 854.4 s / 789 MB of 10800 s / 8 GB; Section C
      3919.04 s / 1.156 GiB of 5400 s / 4 GB. Both are internally consistent with the
      reported loop structure. Section B's budget accounting is in its own report and I
      did not audit it beyond the reproduction legs.
    - >-
      The one place a cost claim is load-bearing is Section A's budget ladder: L11's
      X9/X10 arm bound at 300.4 s, giving the two readings of R5 in report 1.1. I
      accept the arm-level reading for the headline since X8's arm completed in full,
      but the Coordinator should note that under the strict reading GEN-2 FAILS for
      want of a second non-f(P) candidate, and that RT-A10 weakens the third
      (hkz separates at 23x below the gate's own tau_inv).
  reduction_and_scope_challenges:
    - >-
      No published reduction is cited or instantiated anywhere in this batch. Not
      applicable.
    - >-
      SCOPE, and this is the one that matters: "R3 -- ADMISSIBLE BUT NOT RELEVANT --
      the obstruction is RELOCATED, not removed" reads as a statement about the
      problem. RT-A1 through RT-A5 show it is a statement about a ten-item list, a
      scale floor, and a single basis index. The narrowest supported version is below.
      The producer's own section 10 is scrupulous ("R3 is not an obstruction archived;
      R2 was not reached; no claim that no admissible predicate exists"); my objection
      is to the headline sentence, not to the body.
    - >-
      Sections B and C correctly refuse to adjudicate anything about lattices, and say
      so repeatedly. No scope inflation found in either.
  proof_architecture_challenges:
    - >-
      OBSERVATION-FIBER ATTACK, run and successful: hold the frozen gate's four
      criteria fixed and vary the object. X_null and X10 sit on opposite sides of the
      intended conclusion ("carries lattice information" vs "does not") and the gate
      places X_null on the ADMISSIBLE-AND-RELEVANT side and X10 on the refused side.
      The missing separator is a dispersion criterion: an admissible observable must
      vary across the frozen bases at fixed (d,k,beta,q). See RC-3.
    - >-
      QUANTIFIER-ORDER ATTACK: G-Q, REL-1 and REL-2 are each a MAX over the grid at one
      basis (`max(cands, key=...)`), i.e. "there exists a cell where the difference
      exceeds tau" -- while G-INV is a MAX over replicates read as "for all". Mixing an
      existential relevance criterion with a universal invariance criterion at a common
      threshold and a common scale floor is what produces R3 mechanically. Stated so
      the Coordinator can see that R3 is the gate's structural fixed point, not a
      discovery.
    - >-
      METHOD-CEILING ATTACK: the largest claim this gate can support is "of the ten
      observables on this list, at this grid, at one basis for the relevance criteria,
      these three are invariant to machine precision under two of the three transforms
      and none exceeds an absolute 0.10 on a mirrored pair". That ceiling does not
      reach "the obstruction is relocated".
    - >-
      NEARBY-OBJECT ATTACK, run: RT-A5. The closest object for which the desired
      conclusion is false is the same hkz at a different basis index; the reasoning does
      not distinguish them. The missing ingredient is an error bar on G-REL.
    - >-
      COMPOSITIONAL-INVARIANT ATTACK: delete the tau_rel clause from Section C's
      FALSIFYING-PAIR definition and the verdict is unchanged (condition (i) fails at
      all 10). Delete the SE clause instead and the verdict is ALSO unchanged
      (condition (ii) fails at all 10 for any SE). Each component alone is sufficient
      for the verdict, so neither is load-bearing, so no evidence about the proposition
      is carried by either. See RT-C1.
  narrowest_supported_statement: >-
    SECTION A: on the frozen grid, at 8 bases and 8 replicates per transform, six
    observables that are explicit functions of diag(QQ^T) move by 0.26 to 89.0 of their
    declared scale under lattice-preserving re-presentations and are refused; tr(P^2)
    is invariant to 1.30e-15 and distinguishes q = 3329 from q = 1 by at most 3.55e-16
    of scale; |det B|^{1/d} is invariant to 2.51e-13 and lambda_1/|det B|^{1/d} and the
    HKZ tail-window log-ratio are invariant to 7.15e-15 and 1.20e-14 UNDER T2 AND T3
    ONLY (T1 is the exact identity on their Gram input); and no observable on the frozen
    list exceeded an absolute 0.10 on a mirrored cell pair AT BASIS INDEX 0. The
    diagonal-collision probe separates D at 15.8% and 3.4% of scale at diagonals that
    are identical to 0.0, above D's own pooled-SE floor by 7.5x and 1.29x, so
    AM4-OBS-1's premise is REFUTED for D. G-RANK is NOT ADJUDICATED. NOTHING in this
    supports "no admissible predicate exists", "the obstruction is relocated", or any
    statement about which observables could be relevant: R1 is reachable by a
    parameter-determined null, and the one live candidate's relevance verdict is one
    draw from a distribution whose spread covers the threshold 20-40 fold.
    SECTION B: c_min recomputes bit-exactly from the committed record; at an injection
    of 6*SE_diff the AM-3 statistic exceeds t_{7,0.998} at 29 of 48 steps, against 47
    of 48 on an exact-null step of the same variance structure. BATCH-a44d08's
    argmax-SE_diff selection is genuinely removed. Nothing here demonstrates power
    against a real violation, and PRED-B1's outcome was determined before the run.
    SECTION C: with S = 8 supports and E = 4 pools the two-way SE is 0.36x to 1.37x the
    plain sample SE of the same table; its Satterthwaite nu_eff runs 1.00 to 21.00,
    giving critical values 2.874 to 70.023; on 1200 exact-null replicates the SE-based
    condition fires 5 times (0.42% against a nominal 0.909%), which is the one genuine
    calibration result of the section; no matched-V pair reached both frozen bars, and
    could not have for any value of the SE because the largest realized relative
    difference is 14.12% against a floor of 15%. "CONSISTENT" is the frozen label; the
    supported content is per-pair upper bounds of 3.91% to 45.62% relative.
  next_concrete_action: >-
    Before any successor cites Section A, dispatch ONE bounded task (single run, minutes,
    no new reduction beyond d <= 40) that recomputes G-REL1 and G-REL2 for X8, X9 and X10
    over all 8 frozen bases and reports, per candidate and per mirrored pair, the mean
    difference, the between-basis sd, the paired t, and the criterion evaluated BOTH at
    max(|X|, s_X) and at |X|; and that scores the parameter-determined null of RC-3
    through the identical gate. That single task decides whether R3 is a finding or a
    normalization, whether R1 is empty, and whether the gate needs a dispersion criterion
    -- and it is the cheapest thing in the batch's forward path. Everything else in this
    report can wait behind it.
  artifact_paths:
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/reviews/TASK-20260808-6de788/red_team_report.md
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/reviews/TASK-20260808-6de788/probes/probe_A1_null_observable.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/reviews/TASK-20260808-6de788/probes/probe_A1_null_observable.out.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/reviews/TASK-20260808-6de788/probes/probe_A2_rel2_replication.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/reviews/TASK-20260808-6de788/probes/probe_A2_rel2_replication.out.txt
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/reviews/TASK-20260808-6de788/probes/probe_BC_artifact_arithmetic.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/reviews/TASK-20260808-6de788/probes/probe_BC_artifact_arithmetic.out.txt
```

---

# 1. The could-not-fail arrangement, per producer, in BOTH directions

The batch's own pre-registration is the first document in this goal to name both
directions per section. It named the wrong pair twice.

## Section A — TASK-20260808-2a9085

**Direction "could not REFUSE" (the gate admits anything).**
Named in prereg 2.10 Form 1; guard: `X7 = tr(P^2)` must fail `G-Q`.
**It ran in a version of this arrangement, and the guard did not fire.** The
guard tests only whether `G-Q` refuses a *constant*. `tr(P^2) = beta` is
independent of `q` and of `k` by construction, so it cannot detect a gate that
admits *parameter arithmetic*. I built `X_null = (beta/d)(1/d)log|det B|`, which
has zero variance across the eight frozen bases and is a closed-form function of
`(d,k,beta,q)`, and the frozen gate awarded it **R1**:

```
G-NUM   max rho_T0                    3.33e-14   <= 1e-6      PASS
G-INV   max rho over T1,T2,T3         4.71e-14   <= 0.01      PASS   (4800 residuals)
        per transform  T0 3.33e-14  T1 4.71e-14  T2 0.00e+00  T3 2.22e-16
G-Q     |X(3329)-X(1)|/max(|X|,s)     1.0000     >= 0.10      PASS
REL-1   L4, beta 20->95               3.1035     >= 0.10      PASS
REL-2   L4/L5, beta 40                0.6000     >= 0.10      PASS
        -> R1, ADMISSIBLE OBSERVABLE EXHIBITED
max sd of X_null over the 8 frozen bases at fixed (lattice, beta):  0.0
```

The same script recomputes `rdet` through the identical transform path and
reproduces the producer's recorded residuals to the digit — `T1`
`2.514254164288223e-13` against their `2.51e-13`, `T2` `0.0`, `T3`
`9.728156273548676e-16` against their `9.73e-16` — so this is their pipeline and
not a different object. Probe: `probes/probe_A1_null_observable.py`, 2.86 s
wall, 55.8 MB peak RSS, single core, measured.

**Direction "could not PASS" (the gate refuses everything).**
Named in prereg 2.10 Form 2 — but only for `G-INV` and `G-Q`. All three declared
guards protect those two criteria. **There is no positive control for `G-REL`
anywhere on the frozen list, and the run ran in the arrangement where `G-REL`
could not pass.** Before any datum existed, nine of the ten candidates were
excluded from `R1` by the prereg's own algebra:

| candidate | why it could not reach R1 | where the prereg says so |
|---|---|---|
| `X1,X2,X3,X5,X6` | OBS-GEN: any `O(d)`-invariant `f(P)` is constant, so it fails `G-INV` or `G-Q` | prereg 2.4, as a theorem |
| `X7 = TRIV` | designed to fail `G-Q` | prereg 2.3, "negative control" |
| `X8 = rdet`, `X9 = lam1n` | no `beta` argument, so `REL-1 ≡ 0` exactly | prereg 2.7, "hence fail REL-1" |
| `X4 = D` | frozen `D` arm is one `beta` per cell at two non-mirrored cells, so neither `G-REL` clause has its two points | prereg 2.9 |
| `X10 = hkz` | **the only live candidate** | — |

`X8` and `X9` fail `REL-1` at exactly `0.0000` at all six lattices, with
`X_lo == X_hi` bit-for-bit. That is the same arithmetic-zero pattern the producer
correctly flagged in the collision probe, and it is not flagged here: the report
calls it "confirmed". Refusing a lattice invariant for failing to depend on a
readout-window parameter it does not take as an argument is a category mistake,
not a measurement. And the conjunction `G-INV ∧ REL-1` — invariance forces the
observable to be a function of the isometry class, `REL-1` forces it to be a
`beta`-indexed family — has exactly **one** satisfier on the frozen list.

## Section B — TASK-20260808-cece0c

**Direction "could not PASS" (no violation is ever presented).**
Named in prereg 3.8 Form 2; guards: `c_pos` printed at every step, `c_min > c_pos`
verified, and no step selection at all. **It did NOT run in this arrangement.**
This is a genuine repair: `argmax SE_diff` is removed rather than replaced, all
48 steps are reported, and every firing sits on a positive post-injection `Delta`.
Credit where due — Section B fixed the defect it was built to fix.

The verification of `c_min > c_pos` at 48/48 is nonetheless arithmetic. For every
step with `Delta_i <= 0`, `c_min - c_pos = 1 + t_crit·SE_step/SE_diff` identically;
I checked this at **39 of 39** such steps and it holds to `1e-9`. At the other 9
steps `c_pos = 0` by definition.

**Direction "could not FAIL" (the prediction cannot be falsified).**
Prereg 3.8 Form 1 names only the vacuity of "fires at *some* `c`". The mirror it
did not name is that **PRED-B1's falsifier is empty**:

- `c_min(i)` is a deterministic closed form of `Delta_i`, `SE_step(i)`,
  `SE_diff(t_i)`;
- the run reproduced those from the committed record at max deviation `0.0`, and
  `c_min` at max deviation `0.0` in two independent legs;
- the threshold `4` was set from a review measurement of the *same map on the same
  data* (`6, 7, 9, 7`);
- so `n_fire(c=6) >= 4` was decided before the run, conditional only on the
  reproduction check — and had the reproduction check failed, the arm would have
  been INSTRUMENT-LIMITED and PRED-B1 would not have been scored.

I recomputed the counts independently from the committed per-step quantities:
`6, 7, 9, 7`. The report records the agreement as "unexpected in its exactness".
It is forced. That is the same misreading the same batch correctly diagnosed for
the collision probe's six exact zeros, turned on its own prediction.

## Section C — TASK-20260808-3a5f18

**Direction "could not FIRE" (an inflated SE plus a raised floor makes firing
impossible).** Named in prereg 4.10 Form 1; the primary guard is the `delta_min`
positive control with the frozen `delta = 0.50` admissibility clause. **The guard
cannot serve.** `measure_am7.py:501` performs no injection and re-runs nothing; it
is closed-form arithmetic in `SE`, `|Delta_bar|` and `M`, algebraically equal to
"is the detection floor below 50%". Inflate the SE and `delta_min` inflates with
it, and the control still reports "fires, at a bigger delta". A control
denominated in the quantity under repair is precisely AM-6 clause (b)'s defect,
here inside the section the prereg calls "the mirror of AM-6's requirement". It
passed with four percentage points of margin at the worst target (largest floor
45.62% against the 0.50 clause), and 3 of 10 targets fire only at the top grid
point.

**Direction "could not PASS its calibration".** Named in Form 2 and correctly
guarded — `G-CAL` is reachable in both directions by the frozen Wilson table, and
the run reproduces that table. But `G-CAL` was scored on the JOINT criterion, and
I split it (below): in the four exact nulls the *relative-floor* condition fires
**0 of 1200** on its own, so all four `0/300` counts are carried entirely by
`tau_rel`. `G-CAL` is a test of the floor, not of the rebuilt SE.

**The direction neither Form names, and the one it ran in: the VERDICT could not
be falsified.** The largest realized relative difference over the 10 targets is
**14.12%** against `tau_rel = 0.15`. Condition (ii) fails at every target for
**any** value of the SE, including `SE = 0`. The section that exists to rebuild
the SE produced a verdict that the rebuild could not have changed.

---

# 2. AM-4 applied to the new candidates, and to everything else any producer proposed

AM-8 makes the AM-4 triple a pre-registration gate over **every** candidate
observable. Applying it to the three that passed and to the statistics Sections B
and C propose:

| statistic | proposed by | T1 (ambient isometry) | T2 (row permutation) | T3 (unimodular) | verdict |
|---|---|---|---|---|---|
| `rdet` | A / X8 | `2.51e-13` — **invariant by algebra**, `det(BH) = ±det B` | `0.0` by algebra | `9.73e-16` by algebra | AM-4-invariant, and **parameter-determined**: `|det B| = q^{d-k}` exactly for all 8 bases, zero dispersion |
| `lam1n` | A / X9 | `0.0` — **VACUOUS**: `G(BH) = BHH^TB^T = BB^T`, so `T1` is the exact identity on the Gram input | `4.51e-15` genuine | `7.15e-15` genuine | invariant on the basis-change subgroup `{T2,T3}`; the isometry clause is **untested** |
| `hkz` | A / X10 | `0.0` — VACUOUS, same reason | `1.20e-14` genuine | `9.99e-15` genuine | same; and PROBE-L separates it from the frame at `4.26e-04`, i.e. **23x below the same gate's `tau_inv`** |
| `E_I, V, m3, W, OD` | A | `0.74`–`70.1` | `0.667`–`89.0` | `0.690`–`57.9` | REFUSED (as reported) |
| `D` | A / C | `1.10` | `0.263` | `0.225` | REFUSED |
| `r = q_emp/q_Beta`, `Delta_i`, `SE_step`, `SE_diff`, `c_min`, `c_pos`, `n_fire` | B | not measured | not measured | not measured | functions of the graded frame in the standard coordinate basis — inside the class Section A refuses; exempted by prereg 5.8 and disclosed |
| `Delta_bar`, `SE(Delta_bar)`, `nu_eff`, detection floor, `delta_min` | C | not measured | not measured | not measured | same; the report states it in its own header |

The reading the Coordinator needs: **of the three candidates that "pass AM-4", one
passes by algebra with zero lattice information, and two pass on the basis-change
subgroup only, with the ambient-isometry clause structurally untestable in the
pipeline that computes them.** That is not a refutation of Section A's `G-INV`
column, which is honestly measured and honestly disclosed. It is a statement that
"three observables are AM-4-admissible" carries less than it reads.

---

# 3. The null and nearby objects I BUILT, and what they showed

### 3.1 The parameter-determined null (`probe_A1_null_observable.py`)

Built, run, **reaches R1**. Numbers in §1. What it shows: the frozen gate
(`G-NUM ∧ G-INV ∧ G-Q ∧ G-REL`) does not certify that an admissible observable
carries any information about the lattice. It is satisfiable by arithmetic in the
declared parameters. Therefore "R1 is empty" is a property of the ten-item list.

### 3.2 The REL-2 replication / nearby-object control (`probe_A2_rel2_replication.py`)

Built and run: the frozen construction and the frozen HKZ pipeline at the mirrored
pair `L7 (20,6)` / `L8 (20,14)`, all **8** frozen bases, HKZ verified at max
violation `0.0`. 0.22 s wall, 44.8 MB RSS, measured.

```
beta=5    frozen REL-2 at i=0  0.06969   over 8 bases  min 0.00852  med 0.03261  max 0.06969  sd 0.02008
          relative  at i=0     0.40360   over 8 bases  min 0.04203  med 0.17833  max 0.40360
          between-basis sd of hkz WITHIN a cell: k=6  0.02389   k=14 0.03924
          mean mirrored gap 0.00103        paired t over the 8 bases  -0.064 (df 7)
beta=10   mean mirrored gap 0.00065        paired t  +0.088
beta=15   mean mirrored gap 0.00253        paired t  -0.784
```

What it shows, in both directions:

* **Against the producer.** The number that decides the batch's headline is one
  draw. At `beta = 5` basis `i = 0` is the **largest of the eight**. The mirrored
  gap's mean is ~3% of its own between-basis spread. Comparing `0.0697` to `0.10`
  is comparing a single realization to a fixed constant with no error bar.
* **Against me.** It **defeats my own units objection as a route to R1**. Under
  the relative normalization `i = 0` gives `0.4036`, which would clear `REL-2` —
  but the median over eight bases is `0.178` and the paired test says the true gap
  is indistinguishable from zero. So `hkz` has no block-attribution content at
  this cell, and **R3 for X10 survives replication** — for a reason the report
  does not give. I report this against my own thesis.
* **The artifact tell.** The parameter that should destroy a spurious
  block-attribution signal is `d`. The producer's own table has the maximum at the
  *smallest* `d` and the smallest `beta` (`0.0697` at `d=20`; `0.0139` at `d=30`;
  `0.0215` at `d=40`), i.e. it decays where a real block effect should persist —
  and my replication shows why: it is noise, and the noise is largest where the
  HKZ profile is shortest.

### 3.3 The exact-null step control for Section B (`probe_BC_artifact_arithmetic.py`, block B-2)

Section B carries no null object — `NC-B1` (`c = 0`) and `NC-B2` (`c = -6`) are
the same family under different injections. I built one from the committed numbers
alone: keep `SE_step(i)` and `SE_diff(t_i)` exactly, set `Delta_i := 0`, an exact
null step with no descent and no increase.

```
cell         n_fire(6) real   n_fire(6) NULL     n_fire(4) real   n_fire(4) NULL
d100_b30            6               12                  4               10
d100_b40            7               11                  5               11
d140_b30            9               12                  4               11
d140_b40            7               12                  3               10
POOLED/48          29               47                 16               42
c_min on an exact-null step:  min 1.920   median 2.990   max 6.079
```

The headline `29 of 48` must be read against a null value of `47 of 48`. As the
true violation goes to zero the reported count goes **up**, from 29 to 47 — the
canonical artifact tell of `docs/inventor-protocol.md` §3, here in its exact form:
a quantity that fails to decay when the parameter meant to destroy it is removed.
The gate's behaviour is *correct* (at `Delta = 0` the post-injection increase is a
real `6·SE_diff`), but "the AM-3 gate CAN fire at 29 of 48" is not a power
demonstration; it is dominated by `SE_step/SE_diff` and its null is nearly the
ceiling.

### 3.4 Section C's null, split into its two conditions (block C-1)

```
unit                R    cond(i) alone   cond(ii) alone   both   med |t|crit   p95 rel
N-A d100_b40      300      0 (0.0000)      0 (0.0000)       0        8.16       0.0230
N-A d140_b40      300      0 (0.0000)      0 (0.0000)       0        7.41       0.0248
N-B d100_b40      300      0 (0.0000)      0 (0.0000)       0        7.44       0.0215
N-B d140_b40      300      5 (0.0167)      0 (0.0000)       0        7.65       0.0440
N-C d100_b40       60      0 (0.0000)     56 (0.9333)       0       13.06       1.9406
N-C d140_b40       60      0 (0.0000)     58 (0.9667)       0       13.60       1.7696
```

* `G-CAL`'s four `0/300` counts are carried **entirely** by the relative floor.
* **Reported against my own thesis:** condition (i) alone fires 5 of 1200 = 0.42%
  against a nominal per-pair 0.909%. The rebuilt SE and its Satterthwaite `nu_eff`
  **are** calibrated, slightly conservatively. That is the genuine result of
  Section C, it is the thing AM-7 clause (2) asked for, and it is not in the
  report.

---

# 4. Where Section C's power actually went (block C-2)

| cell | target | SE_2way | SE_naive | ratio | nu_eff | \|t\|crit | \|t\|crit at nu=31 | rel% |
|---|---|---|---|---|---|---|---|---|
| d100_b30 | graded_t0.0025 | 9.008e-04 | 8.649e-04 | 1.04 | 2.64 | 6.966 | 2.783 | 1.88 |
| d100_b30 | graded_t0.0050 | 9.796e-04 | 8.032e-04 | 1.22 | 3.73 | 4.979 | 2.783 | 7.27 |
| d100_b30 | unreduced | 2.543e-04 | 6.996e-04 | **0.36** | 1.00 | **70.023** | 2.783 | 3.20 |
| d100_b40 | graded_t0.0025 | 7.027e-04 | 6.545e-04 | 1.07 | 21.00 | 2.874 | 2.783 | 0.26 |
| d100_b40 | graded_t0.0075 | 7.664e-04 | 6.231e-04 | 1.23 | 3.41 | 5.357 | 2.783 | 9.43 |
| d100_b40 | unreduced | 5.141e-04 | 6.052e-04 | 0.85 | 1.50 | 18.901 | 2.783 | 4.34 |
| d140_b30 | graded_t0.0025 | 1.168e-03 | 8.537e-04 | 1.37 | 3.92 | 4.797 | 2.783 | 3.46 |
| d140_b40 | graded_t0.0025 | 6.968e-04 | 7.220e-04 | 0.97 | 1.35 | 25.356 | 2.783 | 3.67 |
| d140_b40 | graded_t0.0050 | 8.007e-04 | 6.780e-04 | 1.18 | 3.60 | 5.118 | 2.783 | 14.12 |
| d140_b40 | unreduced | 4.695e-04 | 5.591e-04 | 0.84 | 1.43 | 21.618 | 2.783 | 0.39 |

The rebuilt SE is the plain sample SE of the same 32-cell table to within a median
factor of **1.05**, and is **smaller** than it at 4 of 10 targets. That is exactly
what PRED-C2's failure reports from the other side. All of the power loss comes
from `nu_eff`, which raises the bar from `2.783` to a median `5.1` and to `70.023`
at one target. Under a plain SE at `nu = 31`, condition (i) fires at 4 of 10
targets rather than 0 — and condition (ii) still fires nowhere, which is why the
verdict is invariant either way.

So the honest answer to "does PRED-C2's failure undermine the CONSISTENT verdict?"
is: **no, because nothing could.** The verdict is a function of `tau_rel` and the
realized effect sizes alone.

---

# 5. Cheapest falsification of each headline, with its cost

| headline | cheapest falsification | cost | status |
|---|---|---|---|
| A: "R1 is empty" | score any parameter-determined observable (`X_null`) through the frozen gate | 2.86 s, 55.8 MB, 1 core (**measured**) | **DONE — falsified**; `X_null` reaches R1 |
| A: "R3 — admissible but not relevant" *as a statement about the problem* | recompute `G-REL1`/`G-REL2` on all 8 frozen bases for X8/X9/X10 and print the between-basis sd and paired `t`, at both normalizations | 0.22 s per mirrored pair at `d=20` (**measured**); < 1 minute for all five pairs | **DONE for L7/L8** — the decisive number is one draw from a distribution with mean ≈ 0; the *label* R3 survives, the *reason* does not |
| A: "hkz fails G-REL" | divide the criterion by `\|X\|` instead of `max(\|X\|, 1.0)` | arithmetic on `results_am4.json`, seconds | **DONE** — flips to PASS at 2 of 9 mirrored points; superseded by the replication above |
| B: "the AM-3 gate CAN fire — 29 of 48" | recompute `n_fire(c=6)` with `Delta_i := 0` at the same SEs | 0.73 s (**measured**) | **DONE** — null value is 47 of 48; the claim is not a power statement |
| B: "PRED-B1 MET" | check whether the prediction's falsifier is reachable given a bit-exact reproduction | 0.73 s (**measured**) | **DONE** — falsifier empty; outcome determined before the run |
| B (stronger, not run) | regenerate the 13 grid points as 13 independent Haar frames from the carried seeds (`E[Delta_i] = 0`) and report `n_fire(c=6)` on that null family | 448 order statistics at `N = 2^20`, pure numpy, no reduction — minutes | **NOT RUN**, by anyone |
| C: "VERDICT CONSISTENT" | compare `max` realized relative difference (14.12%) with `tau_rel` (0.15) | seconds | **DONE** — no pair can falsify at any SE; the verdict is invariant to the repair |
| C: "G-CAL PASSES at 0/300 x4" | split the null rate by condition | 0.73 s (**measured**) | **DONE** — condition (ii) alone gives 0/1200; the gate tests the floor. Condition (i) gives 5/1200 = 0.42%, which *is* good news and is unreported |
| C: "positive control fires at delta = 0.50 at every target" | read `measure_am7.py:501` — the control performs no injection | minutes of reading | **DONE** — closed form in the SE it is meant to validate; passes iff every detection floor is below 50%, and the worst is 45.62% |
| C (stronger, not run) | re-run the scoring path with the offset actually injected | seconds, data already in memory | **NOT RUN** |

---

# 6. The arrangement in which THIS review could not fail — in both directions

**Direction 1 — I could not fail to find a defect.** I chose the null observable,
the normalization, the replication cell, and which committed numbers to
recompute. A red team that builds its own null can build one that any gate with
laxity admits, and can find a between-basis spread by picking `d` small enough.
*Guards, and they are checkable:* my transform pipeline reproduces the producer's
recorded `rdet` residuals to the digit (`T1 2.514254164288223e-13` vs `2.51e-13`,
`T2 0.0`, `T3 9.728156273548676e-16` vs `9.73e-16`); my REL-2 replication
reproduces their basis-0 values exactly (`-0.172674`, `-0.242366`, `0.06969`); my
Section B and C probes use **only** their committed numbers and reproduce their
`c_min`, `n_fire`, `SE`, `nu_eff` and `|t|crit` at deviation `0.0`. Every probe
is in `probes/` and reruns in under 3 seconds.

**Direction 2 — I could not PASS the batch (I only looked for defects).** *This
one fired, twice.* My REL-2 replication **defeated my own units objection** as a
route to R1 and left the producer's R3 label standing. My condition-split
**corroborated** the rebuilt SE's calibration (0.42% against a nominal 0.909%)
against my own thesis that Section C had over-inflated it. Both are reported
above at the same weight as the objections.

**Direction 3 — the residue I cannot close.** I replicated one mirrored pair at
one `d` with eight bases; I did not replicate `L9/L10` or `L11/L12`, did not
rebuild Section B's graded family, and generated no error pool. Everything I say
about Sections B and C is arithmetic on the producers' committed numbers, not an
independent measurement of the underlying draws. A defect that lives in the
generation of those numbers rather than in their use would be invisible to me.
The Validator's leg, not mine.

---

# 7. What I am NOT saying

* I am not calling any of this an impossibility result. Section A's `R3`,
  Section B's `29 of 48` and Section C's `CONSISTENT` are the outputs of frozen
  rules on frozen data, run as written, and I rescore none of them.
* I am not rejecting a conditional result for being conditional. My objections are
  to what the headlines license, not to their conditionality.
* Section B's repair is real: the `argmax SE_diff` selection is removed rather
  than replaced, and that was the right fix. Section C's SE is genuinely
  calibrated on the condition that carries SE information. Section A's gate is a
  real advance over a post-hoc criterion. All three producers reported against
  their own interest — the `d100_b30` drop to 3, PRED-C2's failure, the six exact
  zeros, the `mod q` rank defect, the `D-2` git defect — and in every case my
  criticism is that the *implication* of the honest disclosure was not drawn, not
  that it was hidden.
* Nothing here bears on ML-KEM, on any FIPS 203 parameter set, or on any attack
  cost. Claim tier TOY, unconditionally.

**No commit was made. No producer artifact was modified. No ledger record was
touched.**
