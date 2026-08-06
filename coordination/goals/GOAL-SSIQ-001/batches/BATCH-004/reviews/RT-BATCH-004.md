# RT-BATCH-004 — Red Team review of RUN-SSIQ-a85692-a (EXP-SSIQ-a85692,
# H-SSIQ-9e2c71), GOAL-SSIQ-001 BATCH-004

**Reviews the Coordinator-committed snapshot at commit `29953723`**
(`experiments/EXP-SSIQ-a85692/{implementation,runs/RUN-SSIQ-a85692-a}/`) only.
Nothing below is drawn from, or asserted about, any working-tree-only state.
This report changes nothing under `experiments/EXP-SSIQ-a85692/`,
`experiments/EXP-SSIQ-58b642/`, or any ledger record — those remain the
Coordinator's alone to touch.

```yaml
inference:
  requested_policy: review-adversarial
  resolved_model_id: claude-sonnet-5
  resolved_model_provenance: >-
    self-reported by this Claude Code subagent session; not probe-verified
    this session (no `orchestration.adapter doctor --probe` run here).
  model_verified: false
  fallback_used: true
  fallback_reason: >-
    Subagent frontmatter under this runtime cannot express a policy (CLAUDE.md,
    "Model policy note"); this session runs `model: inherit`. Every
    credentialed backend under this environment has previously been found
    unprobeable (VAL-BATCH-003, RT-BATCH-003, RT-PREFREEZE-EXP-SSIQ-a85692),
    so this is recorded as the standing condition, not re-discovered.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent, per
    `ledger/goals/GOAL-SSIQ-001/goal.yaml` `runtime.runtime_note`. This review
    is not corroboration from a distinct model, and it does not upgrade the
    campaign's evidence tier by itself.
```

---

## What this run actually is

`RUN-SSIQ-a85692-a` executed the frozen `EXP-SSIQ-a85692` contract exactly as
written: Phase 0 (`C-CAL-GAP`) passed; the mandatory largest-prime feasibility
smoke test ran and measured 1.9574 s/vertex at p=21601; the pre-registered
truncation fallback fired, applying `T_prime = 300s` **individually** to each
pre-registered prime's estimated full-coverage cost, ascending by prime size;
**every one of the 12 primes' individual estimate exceeded 300s**, so the
confirmatory prime set is empty (0/12) and the run reports
`DATA-UNAVAILABLE-BLOCKED`. Total measured wall clock: 90.57s of the 7200s
budget (1.26%). `C-SEARCH-BIAS` ran regardless (required, unconditional on
Phase -1) and found weak correlations in both arms.

The mechanical execution is not in dispute: the Executor followed the frozen
rule exactly, disclosed the tension it created (anomaly A-1) rather than
improvising around it, and reported honestly per the contract's own
`success_criterion` ("A DATA-UNAVAILABLE/BLOCKED outcome with an honest,
disclosed obstruction is a fully successful run"). **What this review
disputes is the downstream reading of that outcome as evidence about genuine
infeasibility of lever L4's direct-computation route**, which the run itself
never claims but which a Coordinator synthesis could easily default to absent
this review.

---

## FRONT 1 — Is "genuine infeasibility" the right reading, or did the
## post-freeze fallback itself introduce a new GD-4-shaped defect?

**Verdict: the fallback's own formula, not true infeasibility, is the
dominant, quantitatively demonstrable cause of the empty confirmatory set.
This is GD-4-shaped, one layer downstream of the pre-freeze review.**

The frozen rule (`scope_reduction_fallback_pinned_before_data`) computes
`T_prime = 0.5 x 7200s / 12 = 300s` and requires **each individual prime's**
estimated cost to be `<= T_prime` to enter the ascending-prefix confirmatory
set (`"the largest ascending PREFIX whose estimated per-prime cost is each
<= T_prime"` — confirmed against `raw-result.json.truncation_fallback`,
which literally flags `fits_within_t_prime: false` per-prime against the
constant `300.0`). This is an **even, flat, per-prime cap applied
individually**, not a cumulative check of the ascending prefix's *total* cost
against the *total* reserved budget.

Using **only the numbers already in `raw-result.json`** (no re-measurement,
no new compute — the same arithmetic the frozen contract's own fallback
already performed) and summing the ascending-prefix costs cumulatively
instead of comparing each individually:

| primes included (ascending) | cumulative cost | fits reserved 3600s (0.5×7200)? | fits full 7200s? |
|---|---|---|---|
| {2437} | 379.7s | yes | yes |
| {2437, 3889} | 978.7s | yes | yes |
| {2437, 3889, 5737} | 1879.1s | yes | yes |
| {2437, 3889, 5737, 7333} | **3041.7s** | **yes (< 3600s)** | yes |
| + 8893 | 4447.1s | no (> 3600s) | yes |
| + 10657 | 6138.3s | no | **yes (< 7200s)** |
| + 12541 | 8123.0s | no | no |

The **same, single, largest-prime, most-conservative measured per-vertex
cost** (1.9574 s/vertex — no improvement, no re-measurement, no A-1
substitution) admits **4 primes within the contract's own reserved
half-budget (3600s)**, and **6 primes within the total 7200s budget** (and
comfortably within the actually-unused remainder, 7200 − 90.57 = 7109.4s).
The contract's own decision rule requires exactly `>= 4 primes` to avoid
`INCONCLUSIVE`. **A cumulative-prefix reading of the identical, already-frozen
numbers clears that floor with room to spare; the individual-cap reading does
not admit a single prime.** The empty confirmatory set is therefore not
evidence about the true cost of the direct-computation route — it is an
artifact of choosing to divide the reserved budget evenly across all 12
primes *before* applying the ascending-prefix selection, rather than
checking the prefix's *cumulative* cost against the *total* reserved budget,
which is the natural reading of "truncate to the largest ascending prefix
that fits."

**Why this is GD-4-shaped and one layer downstream of the pre-freeze
review.** `RT-PREFREEZE-EXP-SSIQ-a85692.md` Finding 1 correctly demanded a
feasibility estimate and a fallback, but its own stated fix (numbered items
1–3) does **not** specify `T_prime`'s formula or the individual-vs-cumulative
choice — it only says "a stated per-prime vertex sample cap... pre-registered,
not chosen after seeing results." The exact mechanical formula that actually
fired (`T_prime = 0.5×7200/12`, applied individually) was authored when the
draft was finalized into the frozen contract, **after** the pre-freeze review
concluded, and was never itself put through the cheap stress-test that
Finding 1 demanded of the *smoke test*: does this formula, applied to the
campaign's own already-committed numbers (the same 11,462-vertex total and
2.5ms/entry floor Finding 1 itself cites), actually admit `>= 4` primes under
any plausible measured cost? A five-minute arithmetic check — exactly the
"cheap calculation that would have refuted it" GD-4 exists to demand — was
never run on the fallback formula itself, only on the smoothness-bound pin
(B=23/X=23) that Finding 1 *did* check. The review checked the instrument;
nobody checked the fallback's own arithmetic before it was allowed to decide
the run's headline outcome.

**Is the flat-per-vertex-cost assumption (the `X ~ p^{1/6}` variation)
separately wrong?** It is real but not dispositive on its own. `X` is
pinned **uniformly** at 23 for all 12 primes (derived once from the largest
prime, per `smoothness_parameters_pinned_before_data`) — it does **not**
scale down per prime in the actual search, so the dominant source of
per-vertex cost variation across primes is field-arithmetic cost (bignum /
modular-polynomial root-finding over a smaller `F_{p^2}`), not table size.
A-1's informal ~27% reduction (1.9574s → ~1.43s from largest to smallest
prime) is consistent with that mechanism and is a real, physically plausible
effect — but even applied uniformly to *all* primes it would rescue at most
one additional prime (2437 alone) against the flat individual cap, nowhere
near the `>= 4` floor. **The allocation-formula defect is roughly an order of
magnitude more consequential than the flat-cost-extrapolation concern the
task also raises**, and is the one that actually explains the empty set.

---

## FRONT 2 — A-1: executor defect, contract defect, or neither? Is a new
## defect (GD-7) warranted?

**Decisive answer: neither the Executor nor A-1's flat-per-vertex-cost
observation is the primary defect. A-1 is correctly classified by the
Executor as "not a contract defect and not an executor deviation" *for the
per-vertex-cost question it names* — but Front 1's finding is a distinct,
separately-real contract defect the Executor did not name (it lies in
`raw-result.json.truncation_fallback`'s per-prime cap arithmetic, not in
the per-vertex-cost figure A-1 flags), and it is severe enough to warrant a
new entry.**

- The Executor was right to follow the frozen individual-cap rule mechanically
  rather than substitute A-1's informal number — that is exactly GD-4's own
  discipline (do not improvise around a frozen instrument mid-run) applied
  correctly, and deviating would itself have been the defect.
- A-1's own informal 1.43s/vertex figure, if adopted, still would not clear
  the `>= 4` floor under an individual-cap reading (it rescues at most the
  single smallest prime). So "the extrapolation rule needed a per-prime
  re-measurement step" (the literal shape the task offers as one candidate)
  is not quite right either — a re-measurement at every prime would help
  modestly but is not what actually produced the empty set.
- The actual defect is the **allocation formula's individual-per-prime cap**
  (Front 1), which guarantees emptiness independent of whether the per-vertex
  cost figure is exactly right, exactly the smallest-prime-optimistic A-1
  figure, or anything physically plausible in between — because the formula
  compares each prime's *own* estimated cost against a 1/12 share of the
  reserved budget rather than the ascending prefix's *cumulative* cost against
  the total reserved budget.

**GD-7 is warranted.** Proposed shape, in the one-sentence form each prior
`known_defects_of_this_record` entry uses:

> **GD-7**: A pre-registered budget-truncation fallback computed an EVEN,
> INDIVIDUAL per-prime cap (`T_prime = 0.5×budget/N_primes`, each prime's own
> estimate checked against it) rather than a CUMULATIVE check of the
> ascending prefix's total cost against the total reserved budget — an
> unexamined allocation-formula assumption, finalized into the frozen
> contract *after* the pre-freeze review concluded and never itself
> stress-tested against the campaign's own already-committed numbers, that
> on this run's own official (unmodified, unimproved) measurement would have
> admitted 4–6 primes under a cumulative reading and admits zero under the
> individual reading actually frozen — the same shape as GD-4, one layer
> downstream, this time inside a fix rather than inside the original
> instrument.

---

## FRONT 3 — Cheapest way to find out whether this was a real dead end

**The cheapest test is not primarily a re-measurement; it is re-applying the
ALREADY-COLLECTED numbers under a corrected (cumulative) allocation rule,
followed by actually executing Phase -1 on the resulting prefix.** Concretely,
in two steps:

1. **Free, zero-compute step (already demonstrated above):** re-derive the
   confirmatory prime set from `raw-result.json`'s own
   `truncation_fallback.per_prime_estimate` list by taking the largest
   ascending prefix whose **cumulative** cost is `<=` the reserved 3600s (or
   `<=` the full 7200s). This requires no new code, no new search, and no
   re-measurement — it is pure arithmetic on numbers already committed in
   this run's own artifact, and it already shows `>= 4` primes clear the
   floor.
2. **Bounded, cheap real-compute step:** actually execute Phase -1 (the real
   delta_E search) on that corrected prefix (4–6 primes, an estimated
   3042–6138s of compute at the *same* conservative largest-prime per-vertex
   cost this run already measured — no improvement assumed), to obtain real
   `M-COVERAGE` and a real delta_E multiset, then run Phase 1 (descent
   simulation) on whatever coverage results. This fits comfortably within the
   7200s budget (42–85% of it) with room left for descent simulation, which
   this run measured as near-zero cost once labels exist (BATCH-003's own
   `descent_hitting_time.py` timing was seconds, not the dominant cost).

This is **far cheaper and more direct than re-designing the smoke test**.
The task's suggested alternative — a two-point (smallest + largest prime)
smoke test to build an interpolated per-vertex-cost model — is also cheap
(each smoke test measured ~5.9s here; two points would cost well under a
minute) and is a reasonable **secondary** refinement, but it treats the wrong
layer: even a perfectly-measured, prime-specific per-vertex cost would still
be defeated by an individual-cap allocation rule, because (per Front 1) the
allocation formula, not the cost figure, is what forces the empty set. Fix
the allocation rule first; the two-point smoke test is worth adding
*afterward* only if the resulting cost model needs sharpening for the
primes beyond the cheap prefix.

**One caveat that must travel with this recommendation, not be silently
dropped:** the corrected cumulative-prefix reading admits the *cheapest*
primes first, which are also the *smallest* (N=203 to ~888, roughly a 4.4×
range) — a materially narrower span than the full pre-registered N=203–1800
(8.9× range) the original 12-prime design intended. `goal.yaml`'s
`instrument_calibration` entry already recorded, from BATCH-002, that this
same descent estimator is **biased low by ~0.36 in the T-exponent** on a
**narrow retained window**, and that a decile sweep on the biased window
"peaks at 1.254 and never reaches 1.5." A corrected re-run that only ever
resolves the 4–6 cheapest (smallest) primes risks reproducing exactly that
narrow-window bias mechanism on a *different* estimator (`M-GAMMA` here, not
the WISDE counting-fit that produced the earlier bias) — this is a *new*
instance of the same named risk, not a resolved one, and should be checked,
not assumed away. A fuller amendment (BATCH-005 recommendation below)
should widen coverage rather than settle for the cheapest prefix alone.

---

## The C-SEARCH-BIAS result: does it have any bearing on anything?

`raw-result.json.c_search_bias`: true-target correlation `0.0961`,
random-target correlation `0.0308`, both at p=2437, n=20 sampled vertices,
flagged `magnitudes_comparable_flag: true` under the run's own pre-registered
comparability rule ("comparable if... OR both magnitudes are below 0.1").

**This is genuinely orphaned data with no home in the decision rule as
things stand — and the contract's own text says so.** `C-SEARCH-BIAS`'s
`failure_consequence` text is written entirely in terms of voiding "the real
arm's M-GAP" — a quantity that does not exist in this run (`descent_metrics:
{ran: false}`). The decision-rule ordering in
`preregistered_prediction.decision_rule_frozen_before_data` checks the Phase
-1 gate **first**; on failure it names `DATA-UNAVAILABLE/BLOCKED` directly and
instructs "Do not report this outcome as VOID" — nowhere does the contract
state what a comparable-magnitude `C-SEARCH-BIAS` finding should do to a
`DATA-UNAVAILABLE-BLOCKED` outcome, because the control's entire textual
purpose is to gate a computed `M-GAP`, and none was computed. Reading this
result as "evidence the descent test would have failed anyway" or "evidence
the search-order artifact PF-3 worried about is real" would both be
overreading data whose interpretive frame (a real M-GAP to compare against)
is absent.

**It is not, however, worthless — it should be carried forward, not
dropped.** Two things are worth stating plainly for the Coordinator and for
whichever amended run comes next: (1) at n=20 and this magnitude, both
correlations (0.096 and 0.031) are statistically indistinguishable from zero
under any conventional threshold (roughly r > 0.44 needed for significance at
n=20) — so `magnitudes_comparable_flag: true` here means "both are noise,"
which is a *reassuring* reading for the search-order-bias concern PF-3 raised
(no detected construction-order artifact at this sample size), not an
alarming one; (2) this diagnostic should be re-examined, not re-derived from
scratch, once a real M-GAP exists under the corrected allocation rule (Front
3) — if the corrected run's own `C-SEARCH-BIAS` sample later shows a
comparable-magnitude correlation *against a real, non-empty M-GAP*, that is
when the contract's stated `CONTROL-FAILURE-VOID` consequence actually
applies.

---

## Numbered objections

1. **[HIGH]** The prime-set truncation fallback computes `T_prime` as an even,
   individual per-prime cap rather than a cumulative check of the ascending
   prefix against the total reserved budget, and this formula — not true
   infeasibility of the direct-computation route — is the demonstrated cause
   of the empty (0/12) confirmatory set. Resolution route: GD-7 (proposed
   above); Coordinator-approved protocol amendment correcting the allocation
   rule, then a bounded real re-execution of Phase -1 on the resulting
   prefix (Front 3).
2. **[MEDIUM]** The corrected allocation rule, if adopted naively (cheapest
   ascending prefix, nothing else changed), admits only the narrowest-N
   subset of the pre-registered primes (N≈203–888, a 4.4× range against the
   originally intended 8.9×), which risks reproducing the narrow-window
   `M-GAMMA` estimator bias `instrument_calibration` already documented for a
   related estimator in this campaign. Resolution route: the BATCH-005
   amendment should widen achievable coverage (per-prime B/X pinning, or a
   pre-registered vertex-sampling rule within a prime) rather than accept the
   cheapest-prefix outcome as final; report the achieved N-range explicitly
   against the original design's range in any amended run.
3. **[LOW]** A-1's flat-per-vertex-cost concern is real (a single global
   estimate, taken from the most expensive prime, is conservative for every
   cheaper prime) but is not, on its own, large enough to move the
   confirmatory set past 1 prime under the individual-cap reading — it should
   not be read as *the* explanation for the empty set, only as a secondary,
   correctly-disclosed design tension. Resolution route: address as part of
   the same amendment as objection 1 (a per-prime, or two-point interpolated,
   cost model), not as a standalone fix.
4. **[LOW]** `C-SEARCH-BIAS`'s result (0.096 true-target, 0.031 random-target
   correlation, both statistically indistinguishable from noise at n=20) has
   no active role in this run's decision outcome, because the contract's
   `failure_consequence` text presupposes a computed M-GAP that does not
   exist here; it should not be read either as an ominous finding or as a
   clean bill of health for the instrument at scale, only as a favorable,
   provisional, carry-forward diagnostic pending a real M-GAP. Resolution
   route: re-examine against the amended run's own `C-SEARCH-BIAS` output
   once a real M-GAP exists, rather than citing this run's numbers as
   standalone evidence either way.
5. **[INFORMATIONAL]** The pre-freeze review (`RT-PREFREEZE-EXP-SSIQ-a85692.md`)
   correctly demanded a fallback in general terms but did not itself specify,
   and therefore did not itself stress-test, the exact allocation formula
   that was finalized into the frozen contract afterward — the review's own
   discipline (a cheap arithmetic check against already-committed numbers)
   was not applied to the one number that ended up deciding the run. Not a
   fault of that review's stated scope, but a process gap worth naming so a
   future pre-freeze review re-checks a fix's own arithmetic after it is
   finalized, not only the need for the fix.

---

## Required controls / checks for BATCH-005

- Re-derive the confirmatory prime set from `RUN-SSIQ-a85692-a`'s own
  `truncation_fallback.per_prime_estimate` under a cumulative-ascending-prefix
  rule against the total reserved (or total) budget, as a pre-freeze
  arithmetic check on the amendment itself (objection 1) — this must be done
  and shown to actually clear `>= 4` primes *before* any new compute is
  spent, exactly the standard GD-4/GD-7 demand.
- Report the achieved N-range of any amended run's confirmatory set against
  the originally-intended N=203–1800 span, and flag explicitly whether the
  narrow-window bias mechanism from `instrument_calibration` is plausible for
  the achieved window (objection 2).
- Carry `C-SEARCH-BIAS`'s current (orphaned) result forward as context, and
  re-run/re-interpret it once a real M-GAP exists, rather than treating this
  run's numbers as a standalone verdict (objection 4).

## Counterexample or mutation

The cheapest discriminating check for Front 1 is exactly the one performed
above: take `raw-result.json.truncation_fallback.per_prime_estimate`,
already committed and immutable, and compute the cumulative sum of the
ascending prefix against the reserved 3600s / full 7200s budget instead of
checking each prime individually against the flat 300s cap. This uses no new
compute, changes no measured number, and flips the confirmatory set from
empty to 4–6 primes — a direct falsifier of "the empty set reflects true
infeasibility" as a general characterization of this run's finding.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense — this
remains a toy-scale, gradient-existence screen with `asymptotic_claim: null`
throughout, inherited unchanged and correctly through H-SSIQ-18dc91 to
H-SSIQ-9e2c71. The relevant baseline is, again, this campaign's own
instrument- and fix-scrutiny discipline (GD-4, GD-5, GD-6): this run's
Executor discharged its obligations honestly and disclosed A-1 rather than
silently smoothing it, but the fallback formula it mechanically applied
carries a defect of exactly GD-4's shape, undetected by the pre-freeze review
because that formula was finalized after the review concluded.

## Heuristic challenges

`H-SSIQ-9e2c71.heuristic_assumptions` remains correctly empty (gradient
-existence screen, not a heuristic-conditional complexity claim) — attacked
and held, consistent with every prior review in this lineage. No numbered
heuristic requiring a random-model justification is implicated by this
review's findings; the defect identified here is an allocation-arithmetic
error in a fallback rule, not a heuristic about the underlying arithmetic
object.

## Cost model challenges

No asymptotic-cost claim is made anywhere in this run (`asymptotic_claim:
null`, correctly), so the per-attempt-cost × inverse-success-probability
review does not apply in the complexity-claim sense. What does apply is
ordinary resource bookkeeping, and it is where this review's entire
substantive finding lives: the run measured its own budget split honestly
(90.57s of 7200s, itemized), but the fallback rule that consumed the
remaining 7109s of *unused* budget by declaring the run blocked did so on an
individual-per-prime cap that a cumulative reading of the identical numbers
contradicts by a wide margin (4–6 primes admissible vs. 0).

## Reduction and scope challenges

No scheme from the archived source's affected-vs-safe lists appears anywhere
in this run or its hypothesis. `scope_ceiling` (toy, inherited from
BATCH-003's pinned prime set) is correctly stated and not exceeded. No
scope-inflation concern found.

## Proof architecture challenges

`proof_search_map.not_applicable_reason` remains correctly reasoned and
inherited unchanged — this is a direct instrument-level gradient-existence
screen, not a proof-oriented proposal, and nothing in this run converts it
into one. Attacked and held, same verdict as every prior review in this
lineage.

## Narrowest supported statement

Scoped to `RUN-SSIQ-a85692-a` as committed at snapshot `29953723`: the
Executor's mechanical execution of the frozen contract was honest, complete,
and correctly disclosed (A-1, PD-1–3). The run's `DATA-UNAVAILABLE-BLOCKED`
label is a faithful mechanical application of the frozen decision rule and
should not be read as evidence of genuine infeasibility of the
direct-computation delta_E-search route within this campaign's own budget:
a cumulative (rather than individual, per-prime) reading of the *same*
already-measured numbers admits 4–6 of the 12 pre-registered primes well
within the reserved and total budget, with zero re-measurement. Whether the
descent-gradient signal (M-GAP) itself is DETECTED or UNRESOLVED-BY-THIS-TEST
remains genuinely untested by any record to date — this review does not
supply that answer, only that the *means* to attempt it were available and
were foreclosed by an allocation-formula defect, not a resource shortfall.

## BATCH-005 recommendation

Not a full new contract, and not abandonment of lever L4's direct-computation
route. A **Coordinator-approved protocol amendment** to `EXP-SSIQ-a85692`
(versioned, per `docs/task-lifecycle.md`, since the frozen contract itself
must not be silently edited) that:

1. Replaces the individual-per-prime `T_prime` cap with a cumulative
   ascending-prefix-against-total-reserved-budget rule (objection 1 / GD-7),
   verified against this run's own already-committed numbers as a zero-compute
   pre-freeze check before any new run is authorized.
2. Widens achievable N-range coverage beyond the cheapest 4–6-prime prefix —
   e.g. per-prime (B,X) pinning derived from each prime's own Theorem 1.5
   ceiling rather than the current uniform B=23/X=23 pin, or a pre-registered,
   disclosed vertex-sampling rule within the more expensive primes — so the
   amended run does not reintroduce the narrow-window `M-GAMMA` estimator
   bias `instrument_calibration` already flagged for a related estimator
   (objection 2).
3. Actually executes Phase -1 on the corrected prefix (estimated 3042–6138s
   of the 7200s budget at this run's own unimproved, conservative per-vertex
   cost figure) to obtain real M-COVERAGE and a real delta_E multiset, then
   runs Phase 1 (descent simulation) and reports M-GAP with its bootstrap CI
   for the first time in this campaign under H-SSIQ-9e2c71/H-SSIQ-18dc91.
4. Re-examines `C-SEARCH-BIAS` against the resulting real M-GAP rather than
   this run's orphaned diagnostic (objection 4).

This is the cheapest path that could still produce the confirmatory result
this experiment was built to obtain, and it does so by correcting an
allocation-rule defect the run itself already contains every number needed to
diagnose, not by spending new compute on re-measurement or by declaring L4
closed on a `DATA-UNAVAILABLE-BLOCKED` label that a five-minute arithmetic
check shows was largely self-inflicted.

## Next concrete action

Coordinator: before authorizing any further BATCH-004/BATCH-005 compute,
require (1) the zero-compute cumulative-prefix re-derivation from
`raw-result.json.truncation_fallback` demonstrated in Front 1 above, checked
independently (this is arithmetic on already-committed numbers, appropriate
for the Validator or a bounded research task, not new experimentation); (2)
if confirmed, a versioned protocol amendment to `EXP-SSIQ-a85692` per the
BATCH-005 recommendation above; (3) record GD-7 in
`ledger/goals/GOAL-SSIQ-001/goal.yaml`'s `known_defects_of_this_record`, in
the same lineage as GD-4/GD-5/GD-6, at the Coordinator's next ledger archive.

## Overall verdict

**CHALLENGE.**

Not a challenge to the Executor's honesty, completeness, or mechanical
fidelity to the frozen contract — all three are exemplary here, and A-1 is a
model of correct disclosure-without-improvisation. The challenge is to the
implicit inference that `DATA-UNAVAILABLE-BLOCKED` reflects genuine
infeasibility of lever L4's direct-computation route at this campaign's own
budget scale. It does not, demonstrably: the run's own already-committed
numbers, read under a cumulative rather than individual per-prime budget
check, admit 4–6 of the 12 pre-registered primes with zero additional
compute. The entire point of this contract — testing whether a computable
delta_E-gradient exists — was foreclosed by an unexamined allocation formula
in the frozen fallback, not by the true cost of the search. This warrants a
new named defect (GD-7, proposed above) in the same lineage as GD-4/GD-5/GD-6,
and a bounded, cheap, same-lineage amendment (BATCH-005 recommendation above)
rather than treating this lane as closed or narrowed by genuine infeasibility.

```yaml
red_team_report:
  id: RT-BATCH-004
  task_id: >-
    NOT SUPPLIED IN THE LAUNCHING HANDOFF. Only the Validator's
    TASK-20260805-798a16 was named in this task's instructions; no sibling
    task identifier for this red-team review was visible in
    ledger/handoffs/ or coordination/goals/GOAL-SSIQ-001/batches/BATCH-004/
    at the time this report was written. Recorded as unsupplied rather than
    fabricated, per AGENTS.md rule 9.
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-a (snapshot commit
    29953723): the frozen contract's mechanically-applied truncation fallback
    produced an empty (0/12) confirmatory prime set and a DATA-UNAVAILABLE
    -BLOCKED outcome, with anomaly A-1 (an informal, non-official smallest
    -prime cost measurement, disclosed but not substituted) and a required
    C-SEARCH-BIAS control that ran regardless and found weak correlations in
    both arms.
  objections:
    - "OBJ-1 [HIGH]: the prime-set truncation fallback's T_prime=300s is an EVEN, INDIVIDUAL per-prime cap (0.5x7200/12), not a CUMULATIVE check of the ascending prefix against the total reserved budget. Using ONLY raw-result.json's own already-measured per-prime cost estimates (no re-measurement), a cumulative reading admits 4 primes within the reserved 3600s and 6 primes within the full 7200s, clearing the contract's own >=4-prime floor; the individual-cap reading admits zero. This formula, not true infeasibility, is the demonstrated cause of the empty confirmatory set, and it was finalized into the frozen contract AFTER the pre-freeze review concluded, so it was never itself stress-tested against the campaign's own committed numbers -- GD-4's own discipline, skipped one layer downstream. Resolution: GD-7 (proposed), Coordinator-approved protocol amendment (BATCH-005 recommendation)."
    - "OBJ-2 [MEDIUM]: a naive correction (cheapest ascending prefix only) admits only N in [203,888] (4.4x range) against the intended [203,1800] (8.9x range), risking reintroduction of the narrow-window M-GAMMA-estimator bias goal.yaml's instrument_calibration already documented for a related estimator in this campaign. Resolution: widen coverage (per-prime B/X, or a pre-registered vertex-sampling rule) as part of the same amendment, and report the achieved N-range explicitly against the design's intended range."
    - "OBJ-3 [LOW]: A-1's flat-per-vertex-cost concern (a single largest-prime measurement applied uniformly, ~27% higher than an informal smallest-prime figure) is real but on its own rescues at most one prime against the individual cap -- it is not the primary explanation for the empty set and should be folded into, not treated as separate from, the allocation-rule fix."
    - "OBJ-4 [LOW]: C-SEARCH-BIAS's result (true-target corr 0.0961, random-target corr 0.0308, n=20, both statistically indistinguishable from zero at this sample size) is genuinely orphaned data: the contract's failure_consequence text is written entirely in terms of voiding a computed M-GAP, which does not exist in this run. It should be carried forward and re-examined against a real M-GAP once one exists, not read as evidence either way about this run's outcome or about the instrument at scale."
    - "OBJ-5 [INFORMATIONAL]: the pre-freeze review correctly demanded a fallback in general terms but did not itself specify or stress-test the exact allocation formula finalized afterward into the frozen contract -- a process gap in when a fix's own arithmetic gets checked, worth naming for future pre-freeze reviews."
  required_controls:
    - "Zero-compute re-derivation of the confirmatory prime set from RUN-SSIQ-a85692-a's own truncation_fallback.per_prime_estimate under a cumulative-ascending-prefix rule against the total reserved/total budget, checked and shown to clear >=4 primes before any new compute is authorized."
    - "Report of the amended run's achieved N-range against the originally-intended N=203-1800 span, with an explicit check against goal.yaml's instrument_calibration narrow-window bias mechanism."
    - "Re-examination of C-SEARCH-BIAS against a real, non-empty M-GAP once the amended run produces one, rather than treating this run's orphaned result as a standalone verdict."
  counterexample_or_mutation: >-
    Take raw-result.json.truncation_fallback.per_prime_estimate (already
    committed, immutable) and compute the cumulative sum of the ascending
    prefix against the reserved 3600s / full 7200s budget instead of checking
    each prime individually against the flat 300s cap. Zero new compute,
    zero changed measurements; flips the confirmatory set from empty (0
    primes) to 4-6 primes -- a direct falsifier of "the empty set reflects
    true infeasibility of the direct-computation route" as a general
    characterization of this run.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense
    (toy-scale gradient-existence screen, asymptotic_claim null throughout,
    correctly inherited through H-SSIQ-18dc91 to H-SSIQ-9e2c71). The relevant
    baseline is this campaign's own instrument- and fix-scrutiny discipline
    (GD-4/GD-5/GD-6): the Executor discharged its obligations honestly, but
    the mechanically-applied fallback formula carries a defect of exactly
    GD-4's shape, undetected by the pre-freeze review because the exact
    formula was finalized after that review concluded.
  heuristic_challenges:
    - "H-SSIQ-9e2c71.heuristic_assumptions correctly remains empty (gradient-existence screen, not a heuristic-conditional claim) -- attacked and held, consistent with every prior review in this lineage. This review's finding is an allocation-arithmetic defect in a fallback rule, not a heuristic about the underlying arithmetic object."
  cost_model_challenges:
    - "No asymptotic-cost claim is made (asymptotic_claim: null, correctly); the per-attempt x inverse-success-probability review does not apply in the complexity-claim sense."
    - "Ordinary resource bookkeeping is the live issue and the substance of this review's entire finding: the run measured its own budget split honestly (90.57s of 7200s used), but the fallback that declared the remaining 7109.4s unusable did so on an individual-per-prime cap that a cumulative reading of the SAME already-measured numbers contradicts by a wide margin (4-6 primes admissible vs. 0)."
  reduction_and_scope_challenges:
    - "No scheme from the archived source's affected-vs-safe lists appears anywhere in this run or its hypothesis; no scope widening found."
    - "scope_ceiling (toy, inherited from BATCH-003's pinned prime set) is correctly stated and not exceeded."
  proof_architecture_challenges:
    - "proof_search_map.not_applicable_reason remains correctly reasoned and inherited unchanged -- a direct instrument-level gradient-existence screen, not a proof-oriented proposal; nothing in this run converts it into one. Attacked and held."
  narrowest_supported_statement: >-
    Scoped to RUN-SSIQ-a85692-a at snapshot 29953723: the Executor's
    mechanical execution was honest, complete, and correctly disclosed. The
    run's DATA-UNAVAILABLE-BLOCKED label is a faithful mechanical application
    of the frozen decision rule but should NOT be read as evidence of genuine
    infeasibility of lever L4's direct-computation route within this
    campaign's own budget: a cumulative (rather than individual, per-prime)
    reading of the SAME already-measured numbers admits 4-6 of the 12
    pre-registered primes with zero additional compute. Whether the
    descent-gradient signal (M-GAP) itself is DETECTED or
    UNRESOLVED-BY-THIS-TEST remains genuinely untested by any record to
    date; this review supplies only that the means to attempt it were
    available and were foreclosed by an allocation-formula defect, not by a
    genuine resource shortfall.
  next_concrete_action: >-
    Coordinator: before authorizing further BATCH-004/BATCH-005 compute,
    require (1) independent confirmation of the zero-compute
    cumulative-prefix re-derivation demonstrated in this report (Validator or
    a bounded research task, arithmetic only, no new experimentation); (2) if
    confirmed, a versioned Coordinator-approved protocol amendment to
    EXP-SSIQ-a85692 per this report's BATCH-005 recommendation (corrected
    allocation rule, widened N-range coverage, then a bounded real execution
    of Phase -1 on the corrected prefix); (3) record GD-7 (this report's
    proposed shape) in ledger/goals/GOAL-SSIQ-001/goal.yaml's
    known_defects_of_this_record at the Coordinator's next ledger archive.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-004/reviews/RT-BATCH-004.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    Arithmetic only, entirely on numbers already committed in
    experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-a/raw-result.json
    (cumulative summation of truncation_fallback.per_prime_estimate entries
    against the contract's own stated reserved/total budget figures); no
    code executed, no graph built, no search run, no new measurement taken.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is not
    durable until that archive exists. Per write_scope, this task modified
    nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-004/reviews/RT-BATCH-004.md
    -- experiments/EXP-SSIQ-a85692/, experiments/EXP-SSIQ-58b642/, and every
    ledger record are untouched.
  verdict: CHALLENGE
```
