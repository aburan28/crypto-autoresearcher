# Red-team report — EXP-ICINV-4d33aa v3, terminal state OUTCOME-C

**Scope.** Independent interpretation/cost-model challenge of the
Coordinator-committed snapshot at commit `b9466e54` (`coordination/goals/GOAL-ENDO-001/batches/BATCH-74ebef/execution/EXP-ICINV-4d33aa-v3/execution_report.md`,
under `TASK-20260810-3c448e`), read against `ledger/decisions/DEC-20260809-de11f9.yaml`,
`experiments/EXP-ICINV-4d33aa/amendments/{v2,v3}.yaml`,
`experiments/EXP-ICINV-4d33aa/amendments/v3-verification.py` +
`v3-verification-output.txt`, `experiments/EXP-ICINV-4d33aa/specification.yaml`,
`ledger/hypotheses/H-ICINV-6c7920.yaml`, `ledger/corrections/CORR-20260807-d78e2f.yaml`,
and `ledger/evidence/EV-ENDO-10109d.yaml`. I also independently re-derived (not
merely re-read) the SR3 gate's statistical behavior from the committed
Wilson-Hilferty formula in `v3.yaml` change A7, and pulled raw per-row numbers
from `RUN-ICINV-849d1d/decision-rule-evaluation.json` and
`RUN-ICINV-ff0806/baseline-reproduction.json` to check whether the execution
report's own framing is complete. Per the task's scope note, I did not
re-verify the arithmetic line by line (that is the Validator's parallel job)
and I ignored all uncommitted changes touching `harness/exp_canl.py`,
`harness/canonical_height.py`, `harness/run_canl.py` (EXP-CANL-96b0ad,
out of scope). This experiment makes no ECDLP claim (`claim_tier: toy`,
`sota_delta: 0`); nothing below is a re-litigation of that scope, and I
change no hypothesis or goal status.

**Headline finding, stated up front.** The SR3 redesign's own
"not-vacuous" argument checks the right *shape* of question (does the new
gate still reject something?) but the wrong *quantity* for what a
baseline-reproduction gate needs to certify. I independently derived the
gate's exact acceptance region and its exact false-pass probability under a
genuine null (no real over-dispersion at all), and the false-pass rate is
**44-57%, roughly 40-50x higher than the ~1-2% false-pass rate of the literal
check it replaced.** This does not mean OUTCOME-C is wrong, and it does not
mean p=6007 should have been excluded — but it means "Arm A0 passed the
baseline-reproduction gate at p=6007" is a much weaker statement than the
execution report's flat `gate_passed: True` framing suggests, and a
Coordinator decision record should say so explicitly rather than treat the
pass as equivalent in strength to the p=4001 pass (which the redesign never
touched).

---

## 1. The SR3 redesign is non-vacuous but is not "measuring the same thing, just more honestly" — its discriminating power collapsed by roughly 40-50x

Amendment v3's own verification (`v3-verification-output.txt`, Part 2) probes
11 hand-picked ratios at `n_curves=140` and shows the redesigned CI-overlap
check still rejects `ratio=1.00` and `ratio=4.50`. That is true, and my own
closed-form re-derivation confirms it almost exactly: because
`CI(ratio) = ratio · [df/hi(df), df/lo(df)]` is *linear* in the observed
ratio at fixed `df` (the Wilson-Hilferty bounds `lo(df)`/`hi(df)` do not
depend on the observed statistic), the acceptance region has an exact
closed form, not just a probed approximation:

| prime | df | exact acceptance region for the **observed** ratio |
|---|---:|---|
| p=6007 (n=140) | 139 | **(1.012402, 4.494395)** |
| p=4001 (n=138) | 137 | (1.010445, 4.501244) |
| p=2003 (n=104, ungated) | 103 | (0.969353, 4.647777) |

So the amendment's "roughly (1.00, 4.50)" description is accurate to display
precision — on the narrow question it asked, the check is sound. But that is
not the question that matters for a *baseline-reproduction* gate. What
matters is: **how often would this gate certify "reproduces the campaign's
[1.3, 3.6] over-dispersion band" when the true underlying object shows no
over-dispersion at all (true ratio = 1, i.e. NULL-B's own binomial null)?**
Since NULL-B's statistic is exactly `chi2(df)/df` under a true null, this is
directly computable, exactly, with no simulation needed:

```
df=139 (p=6007): P(gate PASSES | true ratio == 1)  =  44.3%
df=137 (p=4001): P(gate PASSES | true ratio == 1)  =  45.0%
df=103 (p=2003, hypothetically gated): P(...)       =  57.0%
   (compare: P(literal [1.3,3.6] check passes | true ratio == 1) ≈ 1.0-2.2%)
```

That is a **~40-50x inflation in the gate's false-pass rate** relative to
the literal check it replaced, at exactly the sample sizes this experiment
uses. This is not a hypothetical edge case: it is a direct, closed-form
consequence of overlap-testing (as opposed to equivalence-testing) a
finite-sample CI against a fixed band, and it was fully computable from the
same formula the amendment itself derives — no new run, no simulation
infrastructure, five lines of Python. **Amendment v3's own non-vacuousness
argument answers "does this gate still reject something," which it does; it
never asks "how often does this gate admit nothing," which is the actual
operating characteristic a *reproduction* gate needs disclosed.** This is
precisely the null-object control the inventor protocol requires before
trusting a reported "pass" (`docs/inventor-protocol.md` §"Controls before
belief") — applied here to the gate itself rather than to H1's signal, since
the gate is itself now a measurement instrument with its own discriminating
power, and that power was never characterized.

**What this does and does not imply for the run.** It does *not* mean Arm
A0's actual measured baseline at p=6007 is null (the point estimates at
fb=4,5 are 1.23 and 1.11 — plausibly real, modest over-dispersion, not
`ratio≈1`). It does *not* mean SR3 should have failed this run, or that
OUTCOME-C is wrong. What it means is narrower and still consequential: the
`gate_passed: True` label at p=6007 does not certify "this baseline is
statistically consistent with reproducing the specific [1.3,3.6] band"
against any real discriminating standard — it certifies "the baseline is not
statistically excludable from that band," a standard so loose that a
genuinely null object would clear it about half the time at this sample
size. A Coordinator write-up should not describe p=6007's gate pass with the
same confidence as p=4001's (whose gate outcome the A7 redesign never
touched, since it already passed 13/13 under the literal check unchanged).

**Required control (cheap, closed-form, no new run).** Report, alongside
`gate_passed`, the gate's own false-pass probability under the true-null
model at that row's exact `df` — the calculation above, generalized to every
`df` this campaign uses. This is a standing disclosure of the same kind A5
already established for the literal check's floor slack, and it costs
nothing to compute from data already collected.

---

## 2. The blindness discount is real but the execution report's flat "preliminary, regardless of outcome" framing hides *where* it bites and in *which direction*

Amendment v3 correctly caps `confirmatory_status: exploratory_only` because
the redesign was engineered "in view of the exact numeric effect on the two
rows that motivated it" (p=6007, fb=4/fb=5). The execution report (§6)
applies this uniformly: "any resulting evidence record is pre-capped at
`preliminary`... regardless of outcome." That is the procedurally correct
floor, but it is not the whole story a Coordinator needs to write the
decision honestly, because the blindness is **not evenly distributed across
the three primes that produced the 2-1 majority**:

- **p=4001**: SR3 already passed 13/13 rows under the *unchanged* literal
  check (confirmed independently by this Coordinator in
  `DEC-20260809-de11f9`). The A7 redesign made **zero difference** to this
  prime's admissibility. Its `PERSISTS` vote is not touched by the blindness
  concern in the way p=6007's is.
- **p=6007**: this is *both* the prime whose gate-admission required the
  engineered redesign *and* the sole dissenting `COLLAPSES` vote in the 2-1
  majority.
- **p=2003**: has **no committed baseline at all** (`gate_applies_at_this_prime: False`)
  — A7's redesign is entirely inapplicable here, and the Coordinator drafting
  v3 had not seen any p=2003 numbers before filing (§3b of the execution
  report independently confirms Stage 3 never existed at this prime under
  either version). This is the one genuinely blind measurement in the run.

**The decomposition the execution report does not perform, and which
changes the picture:** discarding p=6007 entirely — the one leg carrying the
blindness taint — leaves p=2003 (genuinely blind, `F_p=0.6923`, `PERSISTS`)
and p=4001 (gate outcome untouched by A7, `F_p=0.6923`, `PERSISTS`)
agreeing 2-for-2. **The aggregate `PERSISTS` verdict does not depend on the
engineered prime at all.** If anything, the engineered redesign let in a
prime that *dissents* from, rather than inflates, the persistence majority —
p=6007 votes `COLLAPSES`. So the most common failure mode a reader might
fear (an engineered gate manufacturing the headline result) is not what
happened here; the risk runs the other way.

**What the report should flag but doesn't.** DEC-20260809-de11f9 already
disclosed that p=6007's own re-measured baseline is the *weakest* replicate
of EV-ENDO-10109d's original finding (2 of 13 rows fall below the literal
1.3 floor as point estimates, the noisiest end of the sweep). p=6007 is now
*also* the only prime where persistence collapses. A Coordinator write-up
should name this correlation rather than treat "2-1 majority, dissenting
prime named" as ordinary sampling noise: it is plausible that p=6007 is
simply a weaker, noisier replicate of the whole phenomenon on this
particular class (independent of any r-mechanism), which is a different,
narrower reading than "the r-mechanism partially works at p=6007 but not
elsewhere." Neither reading is established by this run; both should be
named, because the current framing ("2-1 majority... dissenting prime
named", execution report §1) states the fact without connecting it to the
gate-engineering concern the amendment itself raised two paragraphs later.

**A second, separate scope point worth naming explicitly in the write-up:**
p=2003 contributes to the "does EV-ENDO-10109d's over-dispersion survive"
question on a different epistemic footing than p=4001/p=6007, because there
is no committed cyclic-sampler measurement at p=2003 to compare against —
EV-ENDO-10109d's original density sweep covered only p=4001 and p=6007. So
p=2003's `PERSISTS` vote establishes "a similar full-group over-dispersion
exists at this prime," not "the *specific* phenomenon EV-ENDO-10109d
reported survives at this prime under a changed sampler." That distinction
is disclosed candidly in the execution report's per-prime table
(`gate does not apply... no committed reference`), but a casual future
summary ("confirmed at 3 primes") could blur it. Worth a sentence in the
decision record.

---

## 3. Wording risk in the coming Coordinator decision record

Three specific phrases, all inherited from the *original, frozen* contract
(not introduced by v3, but about to be quoted or paraphrased in the next
Coordinator decision), carry real misreading risk for a skimming reader:

1. **"Surviving a targeted... attack" / "strengthened."** `specification.yaml`'s
   `state_4_OUTCOME_C_neither` and `H-ICINV-6c7920`'s falsification criterion
   F3 both use "attack" in the hypothesis-testing sense (this experiment was
   built to overturn EV-ENDO-10109d) and "strengthened" to mean "survived a
   serious attempt at falsification." Out of context, both words read as
   cryptographic-attack language. Given `claim_tier: toy`, `sota_delta: 0`
   throughout, and KN-TECH-030 making the 2-part invariant `r` provably
   irrelevant to the ECDLP, the decision record should not reuse "attack" or
   "strengthened" without an adjacent, explicit restatement — e.g. "this is
   an attack on the hypothesis's own coverage mechanism, not a cryptographic
   attack; nothing here reduces the difficulty of any ECDLP instance."
2. **Asymmetric per-outcome disclaimers in the frozen contract.**
   `state_3_OUTCOME_B_real_r_effect` in `specification.yaml` carries its own
   explicit "does not make r an attack parameter" sentence.
   `state_4_OUTCOME_C_neither` — the outcome actually reached — carries no
   equivalent per-outcome disclaimer; the general "nothing here bears on the
   ECDLP" language lives only in `H-ICINV-6c7920.interpretation_limits`,
   several paragraphs away and outcome-agnostic. The contract cannot be
   edited now (frozen), but the Coordinator's decision record should supply
   the missing sentence explicitly for OUTCOME-C rather than rely on a
   reader to import it from OUTCOME-B's entry.
3. **"Density-independent."** This is not new to v3 but is directly relevant
   to how OUTCOME-C should be characterized, and the execution report
   reuses "does not stratify by r" language without touching it — see §5
   below for the numbers. If a future write-up says "OUTCOME-C confirms the
   density-independent over-dispersion persists," that reinforces a
   characterization the raw row data (both Arm A0's committed baseline and
   this run's own Arm B) does not actually support in the strict sense: the
   ratio moves by roughly 3x across the density sweep at every prime tested,
   in every arm. "Does not decay to 1 at high density" (which is true and is
   what the campaign's own artifact-tell check actually tests) is a
   materially weaker and more accurate claim than "density-independent."

None of this is a defect in the execution report itself, which is
scrupulously neutral (§6: "does not characterise what OUTCOME-C means...
those are Coordinator acts on a later ledger archive"). It is a set of
landmines sitting in already-frozen text that the next decision record is
about to walk into.

---

## 4. OUTCOME-C is not orthogonal to CORR-20260807-d78e2f — it is the direct test that correction called for, and a superseding record is now owed

Amendment v3's own `what_this_amendment_does_not_do` states: "It does not
resolve CORR-20260807-d78e2f... stands exactly as open as it was before this
amendment." Read narrowly and at *filing* time (before any v3 run existed),
that is correct — a protocol redesign cannot resolve anything by itself.
But it should not be read, now that a run has executed, as "OUTCOME-C is
irrelevant to the confound." It is the opposite: `H-ICINV-6c7920`'s entire
mechanism section (STEP 0-5) is a direct formalization of the exact confound
`CORR-20260807-d78e2f` names (the single-generator sampler's coverage
limitation, indexed by `r`), and `EXP-ICINV-4d33aa`'s whole design exists to
test that specific confound to destruction. `OUTCOME-C` = `PERSISTS` +
`S NEGATIVE` is precisely `H-ICINV-6c7920`'s own falsification condition F3
(and F4/F5, given the r=1 stratum tracks r=3 in lockstep — see §5): the
coverage/`r` mechanism is refuted as an explanation. That **is** a direct
answer to the confound `CORR-20260807-d78e2f` raised, with the caveats in
§§1-2 above attached to its strength.

**The risk to flag is the opposite of what a first reading suggests.** The
danger is not that a Coordinator will wrongly claim OUTCOME-C resolves the
confound when it doesn't — the danger is under-crediting it, treating
`CORR-20260807-d78e2f` as still simply "open" with no update, when
`CORR-20260807-d78e2f`'s own `required_action` explicitly pre-commits to a
next step this run has now triggered: *"if EXP-ICINV-4d33aa returns
OUTCOME A (sampler artifact), a superseding evidence record must be written
that retracts the density-independence claim explicitly; if OUTCOME B or C,
a superseding record must state which."* **A superseding correction record
is now owed and is not itself optional or deferred to some later batch — it
is CORR-20260807-d78e2f's own pre-registered obligation, triggered by this
run's terminal state.** The equal and opposite risk is over-crediting it:
the superseding record must not read as "the density-independence claim is
now fully vindicated," because (a) the specific mechanism the campaign was
most confident about is refuted, meaning the campaign now understands the
cause *less*, not more, even though the phenomenon is empirically more
robust; (b) two of three legs carry the blindness caveat from §2; (c) the
evidence is capped `preliminary`, not `replicated`, for a reason stronger
than the reason that already applied to the caps in prior batches.

---

## 5. Cheapest next falsification — and it's already computable from data in hand

The pre-registered falsification map (F1-F8, HEUR-COV-1, HEUR-CVAR-2) is
well designed and none of it points to what I found while checking the raw
rows. Two observations, both free (zero new compute) or nearly free:

**(a) The r=1 and r=3 strata move in lockstep, which is strong independent
support for `S NEGATIVE` — and it also relocates the puzzle.** Pulling
`RUN-ICINV-849d1d/decision-rule-evaluation.json`'s per-row `VR_1_own_null`
and `VR_3_own_null`, at all three primes the two strata rise and fall
together, row by row, almost exactly (e.g. p=6007: both flip from
`invariant`/`under-dispersed` to `over-dispersed` at exactly fb=12; p=4001
and p=2003 show the same co-movement). This is clean, non-cherry-picked
evidence that whatever drives the excess variance is a property shared by
*both* strata at a given `(prime, fb_size)`, not something that
differentially loads onto `r=3`. That directly corroborates `S NEGATIVE`
independent of the S1/S2/S3 thresholds.

**(b) But that same co-movement is clearly NOT flat in density — and the
contract never checks this.** Reading the same rows (and Arm A0's own
committed baseline in `RUN-ICINV-ff0806/baseline-reproduction.json`), the
pooled `VR` rises roughly 3x across the density sweep at every prime: e.g.
p=6007 Arm A0 goes `1.23 → 1.11 → 1.45 → 1.31 → 1.58 → 1.58 → 1.83 → 1.70 →
1.92 → 2.26 → 2.88 → 3.32 → 2.64` from fb=4 to fb=22 — a clear upward trend,
not a flat line, and this shape is present in Arm A0 (the *already committed*
EV-ENDO-10109d-reproducing baseline, unaffected by anything in v3) just as
much as in Arm B. The contract's own checks (`monotonic_decay_is_false`, a
boolean on *decay only*; `fitted_slope_of_VR_minus_1_vs_T`, a slope only
against target count `T`) never compute or report a slope against
`fb_size`/density itself, despite density being the sweep's own primary
independent variable and despite this being a clean ~3x effect visible in
data the campaign has held since before this experiment existed.

**Why this matters as a next falsification step.** A trend that tracks
`fb_size` in lockstep across *both* r-strata and *both* samplers points at
something in how the factor base itself is built, not at sampler coverage.
`factor_base_fixed_size` selects "the first `size` liftable x from 0" — a
fixed, deterministic, non-randomized ordering, not an independent random
subset at each density. That construction is a plausible source of
curve-specific, density-scaling structure (a systematic correlation between
which small `x` are liftable for a given `(a,b)` and something about that
curve) that has nothing to do with `r` and was never named as a candidate
cause anywhere in this campaign's records.

**The cheapest concrete next step, in order of cost:**
1. **Free, right now:** regress each prime's already-collected per-row
   pooled `VR` (or the underlying per-curve rates in
   `per-curve-measurements.json`) against `fb_size`/density directly, at
   both arms, and compute how much of the pooled excess `(VR_pooled - 1)`
   a density term explains versus how much the r-split explains (the same
   `mechanism_accounting` computation the contract already runs for `r`,
   run instead for density). Zero new runs; this is a re-analysis of
   artifacts already committed under `RUN-ICINV-849d1d` and
   `RUN-ICINV-55c2d8`.
2. **If (1) shows density/`fb_size` structure dominates:** run one
   additional arm — same classes, same seeds, same target counts — with a
   **randomized** (not first-N-liftable) factor-base construction of the
   same size at each density, and check whether the over-dispersion and its
   density trend survive. This reuses every piece of existing machinery
   (the `cost_sharing_requirement`'s per-`(curve, fb_size)` sum-set cache
   does not apply directly since the factor base itself changes, but the
   curve/class/enumeration infrastructure is unchanged) and needs only a
   handful of runs, well inside this lane's remaining budget.

This is a genuinely new candidate — distinct from saturation (already
eliminated by `EXP-ICINV-55c2d8`) and sampler coverage (eliminated here) —
and it is testable at a fraction of the cost of either prior lane.

---

## 6. Narrowest supported statement

`RUN-ICINV-849d1d`'s `terminal_state: OUTCOME-C` is a validly computed
output of the frozen decision rule, and I found no defect in how it was
reached mechanically. What I object to is scope of confidence, not the
result: (i) the SR3 "pass" at p=6007 certifies far less than a flat
`gate_passed: True` suggests — I show its false-pass rate under a genuine
null is ~44-57%, not the ~1-2% the literal check it replaced had; (ii) the
2-1 majority's structure is not neutral sampling noise — the engineered
prime is also the dissenting prime, which is reassuring for the direction of
the conclusion but under-explained in the current framing; (iii) this run
is the direct, not orthogonal, test of `CORR-20260807-d78e2f`'s named
confound, and that correction's own pre-registered obligation to supersede
itself is now due; (iv) the pooled variance ratio is clearly density-trending
(~3x across the sweep, in both arms, at all three primes) rather than flat,
which the contract's own checks never quantify and which "density-independent"
overstates; and (v) a free re-analysis of already-collected data, followed
by one cheap randomized-factor-base arm, is a more promising and cheaper
next falsification than anything currently named as a successor in this
lane. None of this reaches a different terminal state, moves any hypothesis
status, or licenses any ECDLP-adjacent claim — `claim_tier: toy`,
`sota_delta: 0` throughout, exactly as stated.

---

## 7. Budget

Read: `DEC-20260809-de11f9.yaml`, `amendments/v2.yaml` + `v3.yaml`,
`v3-verification.py`/`-output.txt`, `specification.yaml`,
`H-ICINV-6c7920.yaml`, `CORR-20260807-d78e2f.yaml`, `EV-ENDO-10109d.yaml`,
the execution report, and selected raw JSON from `RUN-ICINV-849d1d` and
`RUN-ICINV-ff0806`. Independent computation: closed-form re-derivation of
the SR3 acceptance region and its exact false-pass probability under the
null via the regularized incomplete gamma function (`mpmath`, no `scipy`
available in this environment), sub-second; a row-by-row pull of
`VR_1_own_null`/`VR_3_own_null`/`VR_pooled` from committed JSON, sub-second.
No code under this experiment was executed, modified, or imported. No
budget defined for this task was exceeded (read-only review).

---

## 8. Structured summary (per `agents/red-team.md`)

```yaml
red_team_report:
  id: RT-20260810-icinv4d33aav3
  task_id: null
  task_id_note: >-
    This review arrived as a direct instruction in the coordinating session
    rather than through a dispatched TASK-* handoff; no handoff record exists
    to cite, and none is fabricated here (AGENTS.md rule 9).
  claim_under_review: >-
    coordination/goals/GOAL-ENDO-001/batches/BATCH-74ebef/execution/EXP-ICINV-4d33aa-v3/execution_report.md
    (commit b9466e54, TASK-20260810-3c448e): EXP-ICINV-4d33aa contract
    version 3 reached terminal_state OUTCOME-C (RUN-ICINV-849d1d) -- the
    within-class m=3 decomposition-rate over-dispersion of EV-ENDO-10109d
    persists under a certified full-group sampler (2-1 majority across
    p=2003/4001/6007, dissent at p=6007) and does not stratify by r
    (stratification_verdict NEGATIVE), refuting H-ICINV-6c7920's coverage
    mechanism while leaving EV-ENDO-10109d's headline unexplained but
    empirically strengthened. claim_tier toy, sota_delta 0 throughout.
  objections:
    - >-
      Amendment v3 change A7's own non-vacuousness check (v3-verification.py)
      probes 11 arbitrary ratio values and shows the redesigned CI-overlap
      SR3 sub-check still rejects ratio~1.00 and ratio~4.50 -- true, and I
      independently confirm the exact acceptance region by closed form
      (linear in the observed ratio at fixed df): (1.0124, 4.4944) at
      df=139 (p=6007). But the check never computes the gate's false-pass
      rate under a genuine null (true ratio = 1). I computed it exactly via
      the regularized incomplete gamma function: 44.3% at df=139 (p=6007),
      45.0% at df=137 (p=4001) -- a ~40-50x inflation over the ~1-2%
      false-pass rate of the literal check it replaced. The redesign is a
      strict superset of the old check's PASS set (true, as A7's rationale
      claims) but that framing obscures that it is also an enormous
      reduction in discriminating power, not merely a technical widening at
      the margins.
    - >-
      The blindness caveat (confirmatory_status: exploratory_only) is
      applied flatly across all three primes in the execution report's
      framing, but the blindness is concentrated entirely in p=6007 (whose
      gate-admission required the engineered redesign) while p=4001's gate
      outcome is untouched by A7 (already passed 13/13 under the unchanged
      literal check) and p=2003 is genuinely, procedurally blind (no
      committed baseline exists there at all). Discarding p=6007 leaves
      p=2003 and p=4001 agreeing 2-for-2 PERSISTS without it -- the
      aggregate verdict does not depend on the engineered prime, and if
      anything the engineered prime is the dissent, not the driver. The
      execution report states the 2-1 majority and names the dissenting
      prime but does not connect that dissent to the gate-engineering
      concern raised two sections earlier in the same document family.
    - >-
      "Attack"/"strengthened" language, inherited unmodified from the
      original frozen contract's state_4_OUTCOME_C_neither block, carries
      real misreading risk for a claim_tier:toy, sota_delta:0 result;
      state_3_OUTCOME_B_real_r_effect carries an explicit "does not make r
      an attack parameter" disclaimer that state_4_OUTCOME_C_neither (the
      outcome actually reached) lacks, an asymmetry baked into the frozen
      contract that the next Coordinator decision record should repair by
      restating the disclaimer explicitly rather than relying on a reader
      to import it from a different outcome's text.
    - >-
      "Density-independent," used throughout EV-ENDO-10109d and reused by
      this run's own framing ("does not stratify by r"), overstates what
      the raw row data shows: the pooled variance ratio rises roughly 3x
      across the density sweep at every prime, in both Arm A0 (the
      already-committed baseline, unaffected by v3) and Arm B. The
      contract's own checks test only decay-to-1 (monotonic_decay_is_false)
      and T-scaling, never a density/fb_size slope, so this trend has never
      been quantified or disclosed as such anywhere in the campaign's
      records despite being visible in data held since before this
      experiment existed.
  required_controls:
    - >-
      Report the SR3 gate's exact false-pass probability under NULL-B's own
      true-null model (chi2(df)/df, computable in closed form, no
      simulation) alongside gate_passed at every df this campaign uses, the
      same standing disclosure discipline A5 already established for the
      literal check's floor slack.
    - >-
      Free re-analysis of already-collected per-curve data: regress pooled
      VR (Arm A0 and Arm B, all three primes) against fb_size/density
      directly and compute the fraction of the pooled excess (VR_pooled - 1)
      a density term explains, using the same mechanism_accounting machinery
      the contract already runs for the r-split. Zero new runs.
    - >-
      If the density re-analysis shows fb_size-linked structure dominates,
      one additional cheap arm with a RANDOMIZED (not first-N-liftable)
      factor-base construction of matched size at each density, to test
      whether the deterministic ordering rule in factor_base_fixed_size is
      itself contributing curve-specific, density-scaling heterogeneity
      unrelated to r or sampler coverage.
  counterexample_or_mutation: >-
    Independently re-derived the SR3 CI-overlap gate's exact acceptance
    region and its exact false-pass probability under a true-null model
    (ratio == 1) at df in {139, 137, 103} via the regularized incomplete
    gamma function (mpmath, since scipy is unavailable in this environment):
    44.3%, 45.0%, 57.0% respectively, versus ~1.0-2.2% for the literal check
    the redesign replaced. Full script and output reproduced in this
    report's body (section 1); not itself committed as a run artifact,
    analogous in spirit to amendment v3's own v3-verification.py.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/ECDLP sense -- claim_tier toy,
    sota_delta 0, and r is a 2-part invariant KN-TECH-030 already makes
    irrelevant to the discrete logarithm in the prime-order subgroup.
    Nothing here is compared or comparable to Pollard rho, BSGS, or any
    specialized isogeny/lattice baseline, and none of my objections
    introduce such a comparison.
  heuristic_challenges:
    - >-
      HEUR-COV-1 (coverage fraction stratifies exactly by r) and HEUR-CVAR-2
      (a planted index-2 split is detectable) are both explicit, numbered,
      and tested to their own pre-registered falsification conditions in
      this experiment -- I found no gap in how they were stated or tested.
      My objection is orthogonal: the SR3 baseline-reproduction sub-check
      that gates entry to this whole analysis is not itself a numbered
      heuristic with a disclosed random-model justification of ITS
      discriminating power, and should be treated as one going forward
      (see required_controls).
  cost_model_challenges:
    - >-
      No ECDLP cost claim is made or implied anywhere in this run, correctly
      -- this is not a cost-model challenge in the Pollard-rho/BSGS sense.
      The cost-model-adjacent challenge here is about STATISTICAL cost: the
      SR3 redesign's discriminating power (its ability to actually
      distinguish "reproduces [1.3,3.6]" from "shows no effect") was never
      priced or disclosed, only its non-vacuousness at two arbitrary points.
  reduction_and_scope_challenges:
    - >-
      CORR-20260807-d78e2f's confound is the exact mechanism H-ICINV-6c7920
      formalizes and this experiment tests; OUTCOME-C is not orthogonal to
      it, contrary to a naive reading of amendment v3's (correct, filing-time)
      "does not resolve CORR-20260807-d78e2f" disclaimer. CORR-20260807-d78e2f's
      own required_action pre-commits to a superseding record once this
      experiment reports OUTCOME B or C -- that obligation is now live and
      should not be left implicit in the next Coordinator decision.
    - >-
      No scope inflation found in the affected-vs-safe framing: the
      contract's own claim_tier:toy / sota_delta:0 / KN-TECH-030 scoping is
      intact and I found no place where a downstream write-up (so far) has
      exceeded it. The wording risks in section 3 are about future
      misreading of already-frozen language, not about anything currently
      overclaimed in the execution report itself, which is scrupulously
      neutral.
  proof_architecture_challenges: []
  narrowest_supported_statement: >-
    RUN-ICINV-849d1d's OUTCOME-C is a validly computed output of the frozen
    decision rule and I found no mechanical defect in reaching it. Its
    evidentiary strength is narrower than a flat "2-1 majority, preliminary"
    framing conveys: the SR3 gate's pass at p=6007 has a ~44-57% false-pass
    rate under a genuine null (not the ~1-2% of the check it replaced), the
    engineered prime is also the dissenting prime (so the majority's
    direction does not depend on it, which is reassuring, but this
    connection is currently unstated), the pooled variance ratio trends
    roughly 3x with density rather than being flat (undermining
    "density-independent" as a description, in both arms, at all three
    primes), and a superseding record for CORR-20260807-d78e2f is now owed
    by that correction's own pre-registered terms. None of this changes the
    terminal state, moves any hypothesis status, or supports any claim above
    claim_tier toy / sota_delta 0.
  next_concrete_action: >-
    Before any Coordinator decision record characterizes OUTCOME-C: (1) run
    the free density-vs-VR regression on already-committed per-curve data
    (RUN-ICINV-849d1d, RUN-ICINV-ff0806, RUN-ICINV-476e12, RUN-ICINV-4bf6c8)
    to quantify how much of the pooled excess a density term explains versus
    the r-split; (2) if it dominates, dispatch one cheap randomized-factor-base
    arm as the next falsification target, distinct from and cheaper than
    either saturation (already eliminated) or sampler coverage (eliminated
    here); (3) write the CORR-20260807-d78e2f superseding record that
    correction's own required_action already commits to, stating plainly
    that the coverage confound is eliminated as an explanation while the
    phenomenon's actual cause remains unknown and the evidence stays capped
    preliminary.
  artifact_paths:
    - coordination/goals/GOAL-ENDO-001/batches/BATCH-74ebef/execution/EXP-ICINV-4d33aa-v3/execution_report.md
    - ledger/decisions/DEC-20260809-de11f9.yaml
    - experiments/EXP-ICINV-4d33aa/amendments/v2.yaml
    - experiments/EXP-ICINV-4d33aa/amendments/v3.yaml
    - experiments/EXP-ICINV-4d33aa/amendments/v3-verification.py
    - experiments/EXP-ICINV-4d33aa/amendments/v3-verification-output.txt
    - experiments/EXP-ICINV-4d33aa/specification.yaml
    - ledger/hypotheses/H-ICINV-6c7920.yaml
    - ledger/corrections/CORR-20260807-d78e2f.yaml
    - ledger/evidence/EV-ENDO-10109d.yaml
    - experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-849d1d/decision-rule-evaluation.json
    - experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-ff0806/baseline-reproduction.json
```

*Red-team record. I wrote only inside this directory. I hold no authority to
change status and changed none. This is an independent session's judgement,
reviewing a Coordinator-committed snapshot; nothing here is a durable ledger
record and nothing here should be read as evidence until the Coordinator's
ledger archive task processes it alongside the Validator's parallel report.*
