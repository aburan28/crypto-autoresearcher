# Red Team review — TASK-20260824-6fc282

Goal `GOAL-MLKEM-005` · batch `BATCH-f9780d` · role red-team · fresh independent session.

**Snapshot read:** `e17d95cbfdfcdb047c682c89a626745fe53b72e2` (verified `git status --porcelain`
empty and `git diff` against that commit empty before reading; every artifact below was read
via `git show <snapshot>:<path>`, not from the live tree).

**Requested policy:** `review-adversarial`. **Model that answered:** `claude-opus-5`
(Claude Code subagent `red-team`, `effort: xhigh`, which is the effort
`review-adversarial` requests per CLAUDE.md's binding table). `fallback_used: false`.
`model_verified: false` — no `orchestration.adapter doctor --probe` receipt exists for this
session and `AUTORESEARCH_POLICY` / `AUTORESEARCH_BACKEND` are unset; recorded as unverified
rather than asserted, matching every other session in this goal's history.

**Independence:** this session did not produce, run, dispatch or archive any artifact under
review. It read no sibling review — `blindness.lifted_for` names no task here, and
`reviews/TASK-20260824-bc488d/` did not exist at the snapshot. It executed its own probes.

**Claim tier under review: `toy`.** Nothing in this review asserts anything about ML-KEM,
FIPS 203, any parameter set, any attack cost, or C1/C2 in either direction.

---

## 0. Verdict in one paragraph

**This batch establishes less than it looks like, and it establishes less than it could have
for the compute it spent — but the specific thing it does establish (the 75-bit failure is
terminal, reproducible, and not at `BKZ.Param`) is solid and I do not challenge it.** The
producer's report and the snapshot commit are unusually honest: they refuse all four
pre-declared outcomes, own a runner defect, and pre-state what may not be concluded. I
confirm that discipline and do not manufacture an objection to it. My findings are elsewhere,
and they are worse than the batch's own self-criticism: **the instrument could not have
recorded a successful outcome even if it had got one** (§4 OBJ-1), **the binding condition of
the decision that authorised this work was not implemented and its pre-quantified cost was
incurred verbatim** (OBJ-2), **the budget model wrote down the premise that was true and
irrelevant while the load-bearing one went unstated and is contradicted by the goal's own
strongest number** (OBJ-4), and **the experiment specified — "ONE FULL BKZ TOUR" — is not the
experiment executed** (OBJ-7). I ran nine probes in this container; one of them is the first
completed BKZ-55 cell at *any* dimension in this goal's history, and it collapses the batch's
headline ratio (§5, PROBE G).

---

## 1. The five assigned attack surfaces

### (i) Is the predecessor's 2502.74 s treated as a contrast? — **NO on the interpretive axis; YES on the resource axis.**

I audited every occurrence of `2502.74` in the batch and its authorising records.

**Where it is correctly guarded, and pre-committed before any number existed** — this is real
and I credit it: `DEC-20260824-526f89` ("becomes a cross-container sanity reference only,
never the contrast, and this record says so before any number exists"), the dispatch commit
`2fe7dfebb` ("demoted to a cross-container sanity reference — stated here BEFORE any number
exists, not after"), the snapshot commit ("remains a cross-container sanity reference under
unrecoverable strategies provenance and is not a contrast"), and the executor's report, which
places the two numbers side by side and says "no comparison is drawn." **No artifact in this
batch draws a scientific contrast against it. Surface (i) is satisfied as asked.**

**Where it is not guarded.** Three artifacts use it as a *quantitative budget calibration
input*:

- `dispatch_queue.json` → `budget_justification`: "The predecessor's 75-bit cell at this basis
  cost 2502.74 s. Route (c) runs TWO cells, so ~2x that is the expectation".
- `task_card.yaml` → `budget.justification`: "Two cells put the expectation near 5000 s."
- `instrument_readiness_20260824.md` → route (c): "roughly doubling the run (~2 x 2502.74 s at
  the reference scale)".

A number you multiply by two to set an expectation, and against which you then size a 21600 s
ceiling, is a calibration — not a sanity reference. The "sanity reference only" declaration
guards the interpretive axis and does not reach the resource axis. **The guard was placed on
the axis that held; the axis that broke was unguarded, and it is the axis on which this batch
failed.** Three compounding defects in that use, none disclosed:

1. It is a **time-to-ERROR**, used to predict the cost of a cell hypothesised *not* to error
   (see OBJ-4).
2. It is **cross-container under unrecoverable strategies bytes** — the batch's own premise.
3. It carries a **much larger cross-host spread than the ±5–8 % environmental bar the goal
   records**: `DEC-20260815-3e8e9c` reports the BATCH-0d5018 Validator's independent
   re-execution of *the same cell* measuring **1104.40 s of BKZ work** against the producer's
   2502.74 s total. Anchoring a budget on that figure at ±0 % is not defensible on the goal's
   own record.

### (ii) Is any isolated-step result read as tour-level? — **NO on the outcome axis; YES on the cost axis.** And there is **no tension** to explain.

`KN-FIND-f54a82` holds that an isolated LLL/GSO-preprocessing probe is not evidence about the
full BKZ tour it characterises. Two separate questions here.

**(a) Outcome axis — clean.** No artifact in this batch reads `EV-MLKEM-e4189c`'s "100 bits
COMPLETED at the isolated step" as predicting a tour-level *outcome*. The task card, the
decision and the commits repeatedly refuse it. I find nothing to object to.

**(b) Cost axis — the forbidden inference is present, one level upstream, and this batch
inherited it unexamined.** `GOAL-MLKEM-005.next_action` (carried verbatim from
`DEC-20260815-3e8e9c` §14) reads:

> "100 bits is inside the already-validated window (**this goal's own bisection measured it
> COMPLETED at the isolated step at BOTH bases**) and inside the SAME 2-limb mpfr regime as 75
> bits … so it introduces no new assumption and **costs the same order as the 2502.74s already
> spent**."

An isolated-step completion is the *first of two premises* for a tour-level **cost**
expectation. That is `KN-FIND-f54a82`'s inference, made on the resource axis. This batch did
not restate the premise, but it inherited the conclusion — "~5000 s" — and sized 21600 s
against it. **The finding is not that this batch made the error; it is that this batch was the
place to catch it and did not.**

**(c) The alleged tension: there is none, and reading one in would itself be the
`KN-FIND-f54a82` error.** The 100-bit cell's ≥ 14448 s non-termination is **not** in tension
with the 100-bit isolated-step COMPLETION at this exact basis. The isolated step is the
`lll_obj()` call the goal's own records localise at `bkz.py:123`; the tour is
`BKZReduction.__call__` with real block enumeration at β=55 over 512 dimensions. **Passing the
preprocessing step is precisely what lets the computation enter expensive BKZ work.** The two
observations are not merely compatible — the second is what the goal's own recorded precision
response *predicts*: `DEC-20260815-3e8e9c` records "a measured, monotone **376.4x** growth in
post-outer-LLL residual at fixed cell and fixed beta on **+6 bits** of precision, carrying the
computation from 'never entered a tour' to roughly 35 minutes of real BKZ work." More
precision → the computation gets further → more real work. 69→75 bits gave 376.4x; the batch
then budgeted 75→100 bits (+25) at parity.

What **is** in tension is ≥ 14448 s against the ~2500 s-per-cell expectation. That is a
measurement against a *planning estimate*, and the planning estimate loses. Refuting a
planning estimate with a wall-clock kill is legitimate; refuting a mathematical hypothesis
with one is not, and nothing here refutes any mathematical hypothesis.

**This tension is therefore evidence about the budget model and about nothing else.** It is
not evidence about precision, about the babai obstruction, about C1/C2, about
`H-MLKEM-7d9bcc`, or about ML-KEM.

### (iii) d=512 is toy-scale and licenses no FIPS 203 statement — **satisfied, and I add a stronger limit the batch does not state.**

Scale honesty here is complete and I will not invent a defect: `claim_tier: toy` in the
dispatch queue and in `DEC-20260824-526f89`; an explicit scope statement in the decision; a
dedicated "Toy-scale / transfer statement" section in the executor's report; "nothing is a
statement about ML-KEM at any standardized parameter set" in the snapshot commit; and
`no_interpretation` in the receipt. **Surface (iii) is clean.**

**The stronger limit, which the batch does not state and which the ledger archive should
carry.** It is not merely that d=512 is small. **The object under test is the null object.**
`DEC-20260815-3e8e9c` records this in its own words (RT-CTRL-3(i)): "the object under test IS
the null object — a structureless random q-ary lattice — so every d=512 obstruction this goal
has measured is a property of fpylll 0.6.4's mpfr path on generic bases, on one host." Under
`docs/inventor-protocol.md` §3, a signal present in the null object is not yet a signal. This
licenses no ML-KEM statement **at any dimension**, not just at d=512 — and, symmetrically, it
cannot support the escalation branches' "the construction is exhausted at d=512" either,
because that claim ranges over objects the measurement does not include. The nearby-object
control that would bound both directions (`RT-CTRL-3(ii)`, an ML-KEM-shaped basis, ~2800 s)
has been named **REQUIRED before any escalation branch is named ripe** since
`DEC-20260815-3e8e9c` and has now been deferred twice, while ~36,000 s went to re-attempting
the null object.

### (iv) What the 75-bit reproducibility does and does not buy.

**What it buys — and this is the solid part of the batch, which I affirm:**

1. **It is not the `either_errors_at_BKZ_Param` instrument branch.** The conclusion is
   correct. *One of its three stated supports is not a support, however*: the snapshot commit
   cites "the content-pinned strategies file opened", but `strategies_file_used` and
   `strategies_sha256` are written by the runner at lines 55–56, **before** `BKZ.Param` is
   reached at line 69 — they record the runner hashing the file, not fplll opening it. The
   conclusion survives on the **error identity alone**: a failure at `BKZ.Param` raises
   `RuntimeError: Cannot open strategies file.` (demonstrated by the instrument-readiness
   smoke test), and what was raised is `ReductionError: b'infinite loop in babai'` from inside
   the reduction. The other two supports (outer LLL completed; `gso_float_type_used == mpfr`,
   both written before `BKZ.Param`) do correctly establish that the construction got that far.
2. **The failure is terminal and deterministic, not transient.** Two runs, matching seed,
   matching error string, timings 2974.3 s and 3051.8 s (2.6 % apart) and outer LLL 508.58 s
   and 498.96 s (1.9 % apart) — both inside the goal's recorded 5–8 % environmental bar. This
   rules out transient nondeterminism (memory pressure, scheduling). Real, and worth having.
3. **The failure survives a change of pruning schedule and container.** The predecessor errored
   at 75 bits under an unrecoverable Debian `libfplll8` schedule in another container,
   reproduced frame-for-frame on a second host by the BATCH-0d5018 Validator; this batch errors
   identically under upstream fplll master's schedule here. Nobody in the batch names this,
   and it is the most valuable thing the batch produced — see §7.

**What it does not buy:**

1. **It is not a replication of the 2502.74 s measurement.** Strategies bytes and container
   both changed. The ~19–22 % timing difference exceeds the environmental bar but is
   confounded across two simultaneously-changed variables. No attribution is licensed in
   either direction.
2. **"Two independent attempts" overstates one axis.** The attempts share host, container,
   binary, script bytes, strategies bytes, seed and basis; they differ only in the
   process-detachment mechanism and the `timeout` value. That is a **determinism check**, not
   independence in the sense BATCH-0d5018 earned with second-host re-execution.
   `DEC-20260815-3e8e9c` is scrupulous about exactly this distinction when it refuses to count
   same-family reviewers as corroboration; the same scruple applies here. Recommend the
   evidence record say "reproduced across two same-container runs."
3. **It says nothing about precision.** The 75-bit cell is the *reference* arm. The treatment
   arm produced no observation. A control arm without a treatment arm measures nothing about
   the treatment. **This is the whole batch in one sentence.**
4. **On AGENTS.md rule 3.** The ERROR is *not* an infrastructure outcome: it is a terminal
   exception from a valid run that completed its construction and terminated on its own,
   exactly as `DEC-20260815-3e8e9c` ruled for the analogous predecessor event
   (`negative_observation`). It is admissible in that narrow sense **and in no wider one**: it
   is a negative observation about fpylll 0.6.4's mpfr path at one cell, one precision, one
   schedule, one host, on the null object. The 100-bit non-termination *is* a resource outcome
   and is correctly excluded from any obstruction measurement.

### (v) The cheapest control that would overturn what this batch is tempted to conclude.

Named concretely in §6. **CTRL-B**, and I have already run its cheap end: a **dimension ladder
at fixed β=55 and fixed strategies, at 75 and 100 bits, at d where the tour terminates.** I
measured d=80: **both precisions COMPLETE, 26 tours each, 274.29 s vs 277.56 s — a 1.2 %
difference.** That single measurement collapses the batch's headline ratio (§5, OBJ-11) and
costs 9 minutes against the 21600 s this batch spent.

---

## 2. The Coordinator's conduct of this batch

### (a) Route (c) over a byte-identical re-run — **the substitution was justified; its implementation was not, and it cost the target cell a third of its runway.**

**Justified.** The literal `next_action` was **not executable**. The instrument-readiness note
records a live smoke test (d=60, β=20, mpfr=100) under the pinned predecessor script returning
`RuntimeError: Cannot open strategies file.` at `BKZ.Param`, before any tour. Dispatching an
experiment guaranteed to fail for an instrument reason — and to produce something that *looks
like* the obstruction RT-CTRL-1 exists to measure — would have been the worse error. The
pre-dispatch check, the three ranked routes, the refusal to self-grant, and the pre-commitment
of the four outcomes and of the 2502.74 s demotion **before any number existed** are all
correct practice and I say so plainly. Route (c) is a different experiment, but it is the
right different experiment, and it was declared as such in advance.

**Not justified: the single-invocation coupling.** Route (c)'s matched-pair property comes
from **content-pinning the strategies file and forcing the seed** — not from running both
cells in one process. I verified this at the batch's own parameters (**PROBE C**):

```
d=512, seed 452658293:  basis hash dbfc330340353ef2
  — in a fresh process
  — and after re-seeding inside a process that had already run a cell
```

Two invocations of the same script with an `--mpfr-bits` argument would have produced the
**identical** basis, seed, strategies bytes, container and binary — every matched-pair
property — while giving each cell its own budget. As executed, the 100-bit cell received
14449 s of a 21600 s ceiling (**67 %**), because the reference cell's 3051.8 s came out of the
same ceiling *and* attempt 1's infrastructure kill re-charged ~2974 s of reference-cell work
that the runner cannot resume. **The coupling bought nothing content-pinning had not already
bought, and it is the proximate reason the target cell ran out of clock.**

**Also not disclosed: the strategies input's own provenance gap.** The batch was opened
because the predecessor recorded a load-bearing input *by path, with no hash and no version*.
The successor records the same input **by hash with no origin** — no committed artifact
anywhere (runner docstring, task card, dispatch queue, decision, instrument-readiness note)
says where `f516b0a6…` came from. That is recoverable-by-content inside this repository and
*unidentifiable outside it*, which is exactly where the "upstream fplll bug report" branch
would need it. **I closed this gap myself** — see CTRL-E: it is byte-identical to upstream
fplll master's `strategies/default.json`.

### (b) The runner defect and the completeness of the retraction — **the retraction is incomplete where it does harm; one part of it is too harsh on itself; and the framing understates the finding by a category.**

**Incomplete.** The false claim lives in the **artifact**: `dispatch_queue.json` line 44,
`artifact_paths_note` — "Both cells write into one results JSON, rewritten after each cell so
a kill mid-run still leaves the completed cell recorded." At the snapshot commit that file is
**unchanged and still carries it**. The retraction exists only in a **commit message**. The
receipt does not mention the defect at all. No ledger record does. A reader of the batch's
control-plane record meets the false statement with no pointer to its correction. This goal
has an established precedent for precisely this repair — `DEC-20260815-3e8e9c`'s
`held_no_shell_note` describes a separate control-plane correction commit to BATCH-0d5018's
own `dispatch_queue.json`, "matching commit 217da33ae's own precedent for that same file" —
and it was not used.

**Too harsh on itself, and I correct it in the Coordinator's favour.** The snapshot commit
says the 14448 s "survives only in the executor's report and in this receipt, not in the
machine-readable record." That is too pessimistic. The figure is derivable from three
committed machine-readable artifacts: `stdout.log` (cell 100 started `07:12:10`),
`run_end_utc.txt` (`11:12:59`) and the **absence** of a cell-100 entry in
`rt_ctrl_1_matched_pair_results.json`, corroborated by `exit_rc.txt` (`EXIT_RC=124`).
11:12:59 − 07:12:10 = **14449 s**. What is genuinely unrecoverable is **tour progress and
per-cell resource data** — which is the quantity `DEC-20260815-3e8e9c` condition (i) demanded —
not the elapsed time.

**Understated by a category.** The commit frames this as "A DESIGN DEFECT IN THE RUNNER I
WROTE, FOUND BY THE EXECUTOR AND OWNED HERE." It is not a newly-found defect. It is the
**non-implementation of a binding condition** of the decision that authorised this work, whose
exact cost was pre-computed in that decision and restated in the goal's own `next_action`, and
which recurred at the predicted magnitude. See OBJ-2. Neither commit message mentions
condition (i); no `procedure_deviations` entry records it.

**Anything else overstated in either commit message?** Two items, both minor and both listed
as objections rather than as fabrications — the commit messages are otherwise accurate and
notably careful:
- the "content-pinned strategies file opened" support (§1(iv)(1) above);
- "two independent attempts" (§1(iv)(2) above).
And one presentational hazard that is not an overstatement but will become one downstream:
the "**≥ 4.7x**" figure (OBJ-11).

### (c) Was 21600 s against a ~5000 s expectation defensible? — **No. The ceiling was generous relative to the expectation, and the expectation was wrong by roughly an order of magnitude, on the record available before the run.**

Three independent grounds, all available *ex ante*:

1. **The anchor is a time-to-ERROR.** Under every one of the four outcomes the task card
   declared in advance, ~2500 s per cell had no support. In `both_complete` and
   `hundred_completes_seventyfive_errors` the 100-bit cost is a *tour-completion* cost of which
   the record holds no instance anywhere. In `both_error` the error is *deferred*, which by the
   goal's own 376.4x datum means a **larger** cost. Only `either_errors_at_BKZ_Param` is cheap,
   and that branch is an instrument failure. **The budget expectation was inconsistent with the
   batch's own hypothesis in every branch it declared.**
2. **The only comparable data point in the record pointed the other way and was not used.** The
   predecessor's other d=512 cell (β=70 at its own bisected 73 bits) ran **≥ 14400 s without
   terminating**. The record therefore already contained a d=512 cell that did not error early
   and did not fit in 14400 s. The budget cited the cell that errored early and ignored the one
   that did not.
3. **The coupling made the effective ceiling 67 % of the nominal one** (§2(a)).

**And the deeper problem, which no budget number could have fixed: nobody in this goal has ever
established what this operation should cost.** No completed d=512 cell exists at any precision
in any batch; no tour count exists for any d=512 cell in any record, because `n_tours` is only
assigned on the COMPLETED path. Absent a reference cost, "did not terminate in 14449 s" cannot
be read as anomalous **at all**. My PROBE G supplies the first data point and it suggests
14449 s is entirely unremarkable — see §5.

---

## 3. What I do not object to

Recorded explicitly so the Coordinator can see the boundary of the attack:

- The refusal of all four pre-declared outcomes. Correct, and correctly reasoned.
- The classification of both infrastructure events as non-evidence (AGENTS.md rule 3), and the
  refusal to retune anything in response to the ERROR.
- The executor's handling throughout: artifacts preserved under `*.attempt1_killed.*` rather
  than overwritten (condition (v) honoured, and the reason the 75-bit reproducibility exists at
  all), the identical command relaunched with nothing retuned, `stderr` reported as 0 bytes
  rather than omitted, `tours` and `root_hermite_factor` reported as **not recorded** with the
  reason, dual-mark reporting at 3600 s and 14400 s (condition (ii) honoured), scope respected
  (condition (iv) honoured), and every deviation listed. This is a good executor report.
- The receipt binding 15 paths including the three inputs from the dispatch commit.
- Claim-tier discipline everywhere (§1(iii)).
- The decision not to make the re-run call before the reviews land.

---

## 4. Objections

Severity: **CRITICAL** = the batch cannot support what it appears to; **HIGH** = a conclusion
or a cost figure is unsupported; **MEDIUM** = a record-quality or scoping defect.

### OBJ-1 (CRITICAL) — The instrument could not have discharged its own completion gate on **any** outcome. Verified by execution.

The producer's completion gate requires "Both cells … recorded with **status, wall clock,
tours and root-Hermite factor**." The pinned runner (`bc0524ee…`) can produce neither of the
last two.

**(a) `tours` is dead code.** Line 75: `result["tours"] = getattr(bkz, "tours", None)`.
`BKZReduction` has no `tours` attribute — `hasattr(bkz, "tours")` is **False**; the only
matching name is `tour`, a method (PROBE A). Compounding it, line 73 calls `bkz(par)` **without
`tracer=True`**, and fpylll's own `bkz.py` assigns `self.trace = tracer.trace` only at the end
of `__call__`, so `bkz.trace` is `None` too (PROBE D, verified against installed source). The
runner has **no route to a tour count in any branch**.

**(b) The root-Hermite factor is wrong by a factor of ~57 at d=512.** Line 78:

```python
result["root_hermite_factor"] = float(b0) ** (1.0 / d) / (Q ** 0.5) ** (1.0 / 1)
```

The divisor exponent should be `1.0 / d`, not `1.0 / 1`. Measured at d=60 (PROBE B): the
runner's formula returns **0.018814625179154207** where the standard δ₀ is
**1.0146116704743195** — a ratio of 53.93, exactly q^(1/2 − 1/2d) = 3329^0.4917 as predicted.
At d=512 the error factor is 3329^0.499 ≈ **57.4**.

**(c) Consequence.** Had the batch achieved `both_complete` or
`hundred_completes_seventyfive_errors` — **the two outcomes it existed to obtain** — it would
have reported `tours: null` and a root-Hermite factor wrong by ~57x, and its completion gate
would have been discharged against a null and a wrong number, silently, with no error raised.
**The batch was unable to succeed informatively before it started.** This is a stronger
statement than the snapshot commit's own self-criticism, which addresses only the killed-cell
case.

**(d) It is a regression, not an inherited flaw, and it is undisclosed.** The pinned
predecessor script (`58a1fdc2…`, twice-reviewed in BATCH-0d5018) does all three correctly:

```python
bkz(par, tracer=True)
n_tours = sum(1 for child in bkz.trace.children if child.label[0] == "tour")
log_det = M.get_log_det(0, d); r0 = M.get_r(0, 0)
delta_0 = (float(r0) ** 0.5 / np.exp(float(log_det) / d)) ** (1.0 / d)
result["traceback"] = traceback.format_exc()          # on the ERROR path
```

The new runner was **rewritten**, not reused, and the rewrite dropped every one of these. Its
docstring and `DEC-20260824-526f89` both assert the predecessor is "reused **VERBATIM**".
Verbatim is true of the four items actually named (basis construction, seed formula,
precision-before-GSO ordering, ROW_EXPO-free mpfr GSO) and false of the instrumentation, and
nothing in the batch discloses the difference. A reader is entitled to assume the twice-reviewed
instrument came across intact.

### OBJ-2 (CRITICAL) — `DEC-20260815-3e8e9c` binding condition (i) was not implemented, and its pre-quantified cost was incurred verbatim.

The goal's own `next_action` and `DEC-20260815-3e8e9c` §14 make five conditions binding on this
batch. Condition (i), quoted from the goal record:

> "(i) RT-CTRL-2's zero-compute instrument fixes land **FIRST**, **BEFORE ANY FURTHER CAPPED
> RUN** (psutil `.cpu_times()` in the polling loop that already holds the handle; a SIGTERM
> handler or per-tour flush persisting `bkz.trace`'s tour count; retain `stdout_tail` for a
> timed-out cell; capture load average into `environment.json`) — **this batch spent 63.9 % of
> its compute to learn one bit**, and these fixes turn the next timeout into a tours-per-hour
> cost curve"

The pinned runner implements **none of the four**. Its imports are `hashlib, json, os, sys,
time` — no `signal`, no `psutil`; it writes no `environment.json`; it never reads a tour count
(OBJ-1a).

**The predicted failure recurred at the predicted magnitude.** This batch spent 14449 s — **67 %
of its compute** — to learn one bit ("> 14448 s"). Same failure, larger fraction, one batch
later, against a condition written specifically to prevent it and restated in the goal head.

The snapshot commit owns "a design defect in the runner I wrote" but never mentions condition
(i), never records this as a `procedure_deviations` entry, and frames as a newly-discovered
defect what is a non-implementation of a binding condition. **That framing understates the
finding by a category**, and it matters because the honest version tells the successor
something the current version does not: this is now the *second* consecutive batch to lose the
majority of its compute to the same missing instrument.

**Credit where due, checked item by item:** condition (ii) (dual-mark reporting) **honoured**;
(iv) (scope: no β=40, no d=256, no CTRL-3 search, no Stage 1) **honoured**; (v) (preserve every
artifact including infrastructure-killed) **honoured in substance** — filed under
`*.attempt1_killed.*` rather than a `failed_infrastructure` label, and it is the sole reason the
75-bit reproducibility exists. (iii) was explicitly optional and was skipped; I note only that
it was the named near-free rider that would "very nearly discharge" the knowledge-promotion
revisit criterion, and it was skipped in a batch that then spent 14449 s learning one bit.

### OBJ-3 (HIGH) — Condition (i) **as worded cannot work**, and this is the first place anyone could have noticed. Two traps, both verified.

**Trap 1: `bkz.trace` is `None` for the entire run.** fpylll's `BKZReduction.__call__` assigns
`self.trace = tracer.trace` only *after* the tour loop and `tracer.exit()` (verified by reading
the installed source). A SIGTERM handler reading `bkz.trace` gets `None`. **I reproduced exactly
this** (PROBE F): my handler fired at d=128, β=55, 75 bits, wrote a partial record at 399.66 s
with `outer_lll_s` and `gso_float_type_used` intact — and `tours_completed: null`, despite
`tracer=True`. The working route is the *other half of the condition's own disjunction*:
subclass `BKZReduction` and flush a counter from `tour()`. Verified working (PROBE H:
`flushed_tours: 11` == trace `tours: 11`, written to disk incrementally).

**Trap 2: the obvious `tour()` override over-counts.** `bkz2.svp_preprocessing` calls
`self.tour(prepar, kappa, kappa + block_size, tracer=tracer)` **recursively** (bkz2.py:79). At
any block size whose strategy carries preprocessing — block 55 → `preprocessing_block_sizes:
[36]` in the pinned file — a naive override counts preprocessing tours as top-level tours. I hit
this myself: my first override crashed on the keyword signature at d=512 after 514.84 s of outer
LLL, and the traceback is what exposed the recursion. The counter must gate on the top-level
call (`min_row == 0 and max_row == -1`).

A successor told only to "implement condition (i)" will implement the half that cannot work and
then over-count with the half that can. **Naming both traps is worth more than repeating the
mandate**, and neither is discoverable without running the instrument.

### OBJ-4 (HIGH) — The budget model confuses per-operation cost with total expected cost, and the premise it wrote down is the one that was true and irrelevant.

The chain is: goal `next_action` → `instrument_readiness_20260824.md` → `DEC-20260824-526f89`
→ `dispatch_queue.json` `budget_justification` → `task_card.yaml`. Two premises:

- **P1 — per-operation parity in the 2-limb regime.** Asserted from the GMP limb boundary
  ("129+ bits"), never measured. **I measured it and it HOLDS** (PROBE E): `update_gso()` cost
  ratio 100/75 bits is **0.937** at d=128 and **1.017** at d=256. And at tour level (PROBE G),
  d=80/β=55 completes in **274.29 s at 75 bits and 277.56 s at 100 bits — 1.2 % apart, with
  identical tour counts (26)**. P1 is correct.
- **P2 — total cost parity.** Never stated as a separate premise anywhere, and it **does not
  follow from P1**: total = per-operation cost × operation count, and the operation count is
  exactly what precision moves. The goal's own strongest committed number says so, in the
  opposite direction: **376.4x** growth in post-outer-LLL work on **+6 bits** (69→75). The
  batch then budgeted **+25 bits** at parity.

This is my role contract's cost-bookkeeping challenge instantiated exactly: **per-attempt (here
per-operation) cost was used where total expected cost was required.** The model looked
justified because the true-but-irrelevant premise is the one that got written down.

**PROBE G makes the failure precise rather than merely arguable.** At d=80, where the
computation *terminates*, 75 and 100 bits cost the same to within 1.2 %. So the ≥4.7x
wall-clock gap at d=512 is **not** a per-precision cost effect at all — it is the gap between a
computation that **aborted at ~3000 s** and one that **did not abort**. Which is precisely why
anchoring the 100-bit budget on the 75-bit *time-to-error* was the wrong model, and precisely
why the ratio is uninterpretable (OBJ-11).

### OBJ-5 (HIGH) — The isolated-step result is read at tour level, on the cost axis. *(Detailed at §1(ii)(b); recorded here so it carries an objection ID.)*

### OBJ-6 (MEDIUM) — There is no tension to explain between the isolated-step 100-bit COMPLETION and the ≥14448 s non-termination, and asserting one would itself be the `KN-FIND-f54a82` error. *(Detailed at §1(ii)(c).)*

### OBJ-7 (HIGH) — The specified experiment is not the executed experiment.

`GOAL-MLKEM-005.next_action`, `DEC-20260815-3e8e9c`, `DEC-20260824-526f89`, the batch title and
the task card all say **"ONE FULL BKZ TOUR"**. The runner calls:

```python
par = BKZ.Param(block_size=beta, strategies=STRATEGIES, flags=BKZ.AUTO_ABORT)
bkz(par)
```

No `max_loops`, no `BKZ.MAX_LOOPS`. This runs tours **until auto-abort or full reduction**, not
one tour. Measured: **11 tours** at d=60/β=20 (PROBE D/H) and **26 tours** at d=80/β=55
(PROBE G).

This is inherited, not introduced here — the predecessor script does the same, and its own field
is `n_tours`, plural, so the descriptor has been inaccurate across at least three batches. But it
is **not merely nomenclature**: it is load-bearing for the budget, because a reader — and the
~2500 s expectation — sizes "one tour" and gets "tours to auto-abort", which PROBE G shows is
26x more work at the one β=55 dimension anyone has measured. It is also load-bearing for what
the goal believes it has failed to do: **no record in this goal's entire d=512 history contains a
tour count for any d=512 cell at any precision**, because `n_tours` is assigned only on the
COMPLETED path and no d=512 cell has ever completed.

### OBJ-8 (HIGH) — The batch changed the pruning schedule and deleted the only instrument that could have detected whether that mattered.

The predecessor captured `traceback.format_exc()` on ERROR, and `DEC-20260815-3e8e9c` relies on
it: the predecessor's failure is localised "at fpylll `bkz.py:186` inside a **doubly-nested
`svp_preprocessing`**", distinct from the `bkz.py:123` call the isolated-step harness bisects.
The new runner records only `f"{type(exc).__name__}: {exc}"` — **no traceback**.

So this batch **cannot establish whether its 75-bit error is at the same call site as the
predecessor's.** That is the one comparison that would have shown whether swapping the pruning
schedule changed the failure mode — and `svp_preprocessing` is *precisely where the schedule
enters* (the substituted file gives block 55 → `preprocessing_block_sizes: [36]`). The batch
introduced a confound and removed its detector, at zero cost saved: one line, present in the
script being "reused verbatim". Identical error *strings* do not localise a call site.

### OBJ-9 (MEDIUM) — 2502.74 s is guarded on the interpretive axis and used as a budget calibration on the resource axis. *(Detailed at §1(i).)*

### OBJ-10 (MEDIUM) — "Two independent attempts" overstates the independence axis. *(Detailed at §1(iv)(2).)*

### OBJ-11 (MEDIUM, and the item most likely to leak into the evidence record) — the "≥ 4.7x" ratio should not be reported at all.

14448 / 3051.8 = 4.73 divides a **censored** observation by an **uncensored** one. It has no
interpretation as a cost multiplier. The snapshot commit does say it is "a LOWER BOUND ON AN
UNFINISHED COMPUTATION, not a cost" — correct — but it also states the figure in the
`WHAT THE RUN PRODUCED` header, which is the single number most likely to be lifted into
`EV-MLKEM-59e4a4` and read as "precision costs 4.7x". **PROBE G shows the true tour-level cost
ratio at a terminating dimension is 1.012.** Report the two raw numbers and the censoring; drop
the ratio.

### OBJ-12 (MEDIUM) — The retraction is incomplete where it does harm; one part of it is too harsh. *(Detailed at §2(b).)*

### OBJ-13 (HIGH) — Route (c) did not require single-invocation coupling, and the coupling cost the target cell a third of its runway. *(Detailed at §2(a); PROBE C.)*

### OBJ-14 (HIGH) — No reference cost exists for this operation, so "did not terminate in 14449 s" is not yet known to be a finding.

There is no completed d=512 cell at any precision in any batch of this goal, and no tour count
for any d=512 cell in any record. Absent a reference cost, the headline non-result has no frame.
**PROBE G supplies the first data point and it suggests 14449 s is unremarkable**: β=55 costs
274 s for 26 tours at d=80 and does **not** complete within 400 s at d=128 (PROBE F). One tour
is ≈ (d − β) SVP calls — 25 at d=80 against 457 at d=512, before any growth in per-call cost —
so a full auto-abort run at d=512 plausibly sits in the **tens of thousands of seconds**.
*Stated as an order-of-magnitude reasoning check, explicitly not a measurement.* If it is even
roughly right, the 21600 s ceiling was below the job's cost **at either precision**, the
100-bit cell's non-termination carries no information about precision whatsoever, and the batch
could not have produced its declared outcomes for reasons entirely unrelated to the mechanism
under test. CTRL-B measures this directly instead of extrapolating.

---

## 5. Probes run by this session

All in this container, on the same 4-CPU host, using the task card's own declared interpreter
`…/scratchpad/sagevenv/bin/python` (Python 3.11.15, fpylll 0.6.4, numpy 2.4.6) and the
snapshot's own strategies bytes. Full sources are in §9 so every number below is reproducible.
**No repository artifact was modified and nothing was committed.**

| probe | question | result |
|---|---|---|
| **A** | does `BKZReduction` expose `.tours`, as the runner assumes? | **No.** `hasattr` → `False`; only `tour`, a method. `getattr(bkz,"tours",None)` is always `None`. |
| **B** | is the runner's root-Hermite formula correct? | **No.** d=60: runner 0.018814625179154207 vs standard δ₀ 1.0146116704743195; ratio 53.93 = q^(1/2−1/2d). At d=512 the factor is ≈ 57.4. |
| **C** | does the matched pair require one invocation? | **No.** d=512, seed 452658293 → basis hash `dbfc330340353ef2` identically in a fresh process and after re-seeding post-cell. (d=60: `51424948e22871f3`, all three positions.) |
| **D** | is a tour count reachable at all? | Only with `tracer=True`: trace children `['lll', ('tour',0)…('tour',10)]` = **11 tours** at d=60/β=20. Without it, `bkz.trace is None`. Installed `bkz.py` assigns `self.trace` only after the tour loop. |
| **E** | does the 2-limb per-operation parity premise hold? | **Yes.** `update_gso()` ratio 100/75 = **0.937** (d=128), **1.017** (d=256). Also: isolated LLL COMPLETED at 75 and 100 bits mpfr at d=128 and d=256; the `double` path errors `infinite loop in babai` at d=256; d=128/75 deterministic 8/8. |
| **F** | does a SIGTERM handler recover progress? | Partially. Handler fired at d=128/β=55/75b, wrote a partial record at 399.66 s with `outer_lll_s: 1.16` and `gso_float_type_used: mpfr` — but `tours_completed: null`, because `bkz.trace` is `None` mid-run. d=128/β=55 did **not** complete within 400 s. |
| **G** | **is there a dimension where β=55 terminates, and what does precision cost there?** | **Yes, and precision is nearly free.** d=80, β=55, same strategies, same seed: **75 bits COMPLETED, 26 tours, 274.29 s**; **100 bits COMPLETED, 26 tours, 277.56 s**. Ratio **1.012**. |
| **H** | does a per-tour flush work? | **Yes.** `BKZReduction.tour()` override → `flushed_tours: 11` == trace `tours: 11`, `tourlog.json` written incrementally. Must gate on the top-level call (see OBJ-3 trap 2). |
| **I** | d=512 at `max_loops=1` — the specified experiment | outer LLL **514.84 s** (consistent with the batch's 498.96 / 508.58 s, third independent measurement). Full result in §8. |

**PROBE G is the important one.** It is, so far as any record in this goal shows, **the first
completed BKZ block-size-55 cell at any dimension in this goal's history**, and the first
tour-level, end-to-end measurement of the 75-vs-100-bit cost question. It says the precision
question, *at a dimension where the computation terminates*, has the answer **"both complete,
1.2 % apart, identical tour counts"** — for **9 minutes** of compute against the **21600 s**
this batch spent to learn nothing about it.

---

## 6. Required controls

Ordered by cost. **CTRL-A is a precondition, not a control**: without it, a re-run at any budget
can reproduce this batch's zero-information outcome exactly.

### CTRL-A — Fix the instrument before any further capped lattice run. *(Zero lattice compute. This is condition (i), still undischarged.)*

Under a **new runner hash** (the pinned runner is bound in the receipt and must not be
retroactively edited):

1. **STARTED stub written before each cell**, so a killed cell is evidence of something.
2. **`bkz(par, tracer=True)`** — restores the predecessor's behaviour and is the only way a tour
   count exists.
3. **Per-tour flush by overriding `BKZReduction.tour()`**, gated on `min_row == 0 and
   max_row == -1` — **not** a SIGTERM read of `bkz.trace`, which is `None` until `__call__`
   returns (OBJ-3, both traps).
4. **`traceback.format_exc()` on ERROR** — restores the predecessor's, and is the only way the
   pruning-schedule confound (OBJ-8) can ever be bounded.
5. **The predecessor's `get_log_det`-based root-Hermite factor**, replacing the `1.0/1`
   exponent (OBJ-1b).
6. **psutil `.cpu_times()` and load average into `environment.json`** — the remaining half of
   condition (i).
7. **Two invocations, not one**, with an `--mpfr-bits` argument (OBJ-13; PROBE C shows the basis
   is identical).

### CTRL-B — **The cheapest control that would overturn what this batch is tempted to conclude.** A dimension ladder at fixed β=55.

Run the identical construction and strategies at **d ∈ {80, 96, 112, 128, 160, 192}** × **{75,
100} bits**, with the CTRL-A instrument. I have already run d=80 (**both complete, 274.29 s /
277.56 s, 26 tours each**) and observed d=128/75 not completing within 400 s. This yields, for a
few thousand seconds total:

- **the first measured cost-vs-dimension curve for this operation** — which is what OBJ-14 says
  the goal has never had and what any Stage-1 sizing requires;
- **the d at which 75 bits starts failing while 100 still succeeds** — which is the actual
  RT-CTRL-1 question, tested where it is affordable rather than where it is not;
- **a tours-per-hour figure**, i.e. exactly what condition (i) said the fixes would buy.

It **overturns** the readings this batch is tempted toward, in either direction: if 100 bits
succeeds where 75 fails at some d, the precision mechanism is real at tour level and the d=512
cell simply needs a budget sized from the curve. If both fail together at every d above some
threshold, the obstruction is not about precision at all and the 25-bit gap the goal has been
bisecting is empty. Either is decisive; neither costs 21600 s.

### CTRL-C — The nearby-object control, `RT-CTRL-3(ii)`, ~2800 s. **Named REQUIRED since `DEC-20260815-3e8e9c` and now deferred twice.**

Every d=512 obstruction this goal has measured is on a **generic random q-ary lattice**, which
`DEC-20260815-3e8e9c` itself identifies as the null object. Under `docs/inventor-protocol.md`
§3 a signal present in the null object is not yet a signal. Until the identical measurement runs
on an ML-KEM-shaped basis, nothing here transfers to the object PREREG-8's Stage 1 reduces — **in
either direction**, so it equally blocks any escalation branch's "the construction is exhausted"
claim. It is now cheaper than the thing the goal keeps re-attempting.

### CTRL-D — The parameter that is supposed to destroy the signal, and what it should do.

*(`docs/inventor-protocol.md` §3, and my standing obligation to ask this.)* The reported quantity
is the `infinite loop in babai` failure; the parameter meant to destroy it is **mpfr precision**.
Prediction: as precision rises, the failure should first be **deferred** (more work before it
fires) and then **disappear**, after which cost saturates at the true tour cost.

**The goal's own data already behaves this way** — 69 bits: never entered a tour; 75 bits: ~35
minutes of real BKZ work, then failure; 100 bits: no failure observed in ≥ 13 950 s of reduction
work. **The canonical artifact tell — a quantity that fails to decay when the parameter meant to
destroy it increases — is ABSENT.** I record this as a point *in the batch's favour*: the
obstruction is behaving like a genuine numerical-precision effect rather than an artifact.
CTRL-B is what turns that behaviour into a measured curve instead of three anecdotes.

### CTRL-E — The strategies input's identity. **Free, and I have already done it.**

The pinned file — sha256 `f516b0a6f0c580cff72e1e2c3562c44dc6f17e8f99613e9e4020e35481b27a18` — is
**byte-identical to upstream fplll's `strategies/default.json`**, fetched by this session on
2026-08-25 from `https://raw.githubusercontent.com/fplll/fplll/master/strategies/default.json`
(sha256 match; 8 606 859 bytes; 101 entries, `block_size` 0…100; block 55 carries
`preprocessing_block_sizes: [36]` and 21 pruning parameter sets — so it is a genuine tuned
schedule, **not** `KN-TECH-14efa5`'s pruning-free `[Strategy(b) for b in range(41)]`, which would
not have covered β=55 at all).

`master` is a moving reference, so the durable pin is the **git blob sha1
`3e80d1636be1e6d67f6dc082dc95225842e0aa25`**, which a successor can resolve against the fplll
repository without trusting this fetch. **The successor record should carry this origin**: the
batch pinned a load-bearing input by content and recorded no origin anywhere, which repeats in a
weaker form the exact provenance failure the batch was opened to fix.

---

## 7. Counterexample / mutation, and the resource re-reading

### The cheapest mutation that would expose whether this batch measured anything about *precision*

Re-run the **75-bit cell only**, at the same seed and basis, under a **different strategies
source** — e.g. `KN-TECH-14efa5`'s pruning-free `[Strategy(b) for b in range(56)]`. Cost: one
cell, ~3000 s.

- If `infinite loop in babai` **persists** at the same wall-clock order, the failure is
  independent of the pruning schedule; the substitution route (c) introduced is harmless, route
  (c) is retroactively validated, and the reproducer strengthens.
- If it **changes**, then this batch's 75-bit ERROR is partly a strategies artifact, is not
  comparable to the predecessor's at all, and OBJ-8's deleted traceback becomes load-bearing.

This is the **null object of the same shape for the strategies variable specifically**, and it is
the only way to bound the one confound route (c) introduced.

### Resource re-reading — running the reversal against the obstruction this record measures

*(Role contract item 8. The author is the reader least able to do this, having spent the task
establishing that the batch produced nothing. Both readings are candidates for the ranking,
**never evidence**, and neither changes any status.)*

**R1 — the failure's robustness is an asset, and nobody in the batch names it.** The 75-bit
`ReductionError('infinite loop in babai')` now reproduces across **two containers, two hosts**
(counting BATCH-0d5018's Validator re-execution), **two different pruning schedules** (an
unrecoverable Debian `libfplll8` build and upstream fplll master), and **four runs**. A failure
that survives a change of pruning schedule, container, host and strategies provenance is a
robust, publicly reproducible defect. Combined with CTRL-E's identification of the strategies
input and CTRL-A's traceback restoration, the **"upstream fplll bug report" branch** — which
`DEC-20260815-3e8e9c` recorded as better supported than the others but not ripe, on the ground
that a reproducer at an inadequate precision is a weak report — now has a **materially stronger
reproducer than it had**, and PROBE F shows a candidate cheap reproducer at **d=128** rather than
d=512.

**R2 — the censored 100-bit observation is weak evidence for the mechanism, in the direction the
goal wants.** The 100-bit cell performed ≥ 13 950 s of reduction work (14449 s minus ~500 s outer
LLL) without raising, against the 75-bit cell's ~2 550 s to failure. PROBE E and PROBE G make the
wall-clock comparison a legitimate proxy for operation count (per-operation parity holds to
1.2–2 %), so this is weakly consistent with precision **deferring or removing** the failure — the
continuation of the goal's own 376.4x trend. **A censored observation cannot separate "removed",
"deferred", and "the tour is simply slow at this d"**, and CTRL-B separates all three cheaply.

---

## 8. Late-arriving probe result — PROBE I (d=512, `max_loops=1`)

PROBE I runs the experiment the goal's `next_action` literally specifies and which nothing in
this goal's history has run: **(d=512, β=55) with `flags=BKZ.MAX_LOOPS, max_loops=1`** — one
genuine tour — at 75 and 100 bits, with the CTRL-A instrument. Result appended below; it was
still executing when this review was written, and **nothing in §§0–7 depends on it.** Whatever it
returns, it does not change any objection above; it either supplies or fails to supply the first
d=512 tour-level cost datum, and CTRL-B remains the recommendation either way.

<!-- PROBE_I_RESULT -->

---

## 9. Narrowest supported statement

> At **(d = 512, β = 55, q = 3329, k = d/2, seed 452658293)**, under **fpylll 0.6.4** with a
> ROW_EXPO-free **mpfr** GSO, BKZ block size 55 with `AUTO_ABORT` and no loop bound, under
> upstream fplll master's `strategies/default.json`
> (sha256 `f516b0a6…`), on one 4-CPU container:
>
> - the **mpfr_bits = 75** configuration raises `ReductionError: b'infinite loop in babai'`
>   after **2974.3 s** and **3051.8 s** in two same-container runs, having completed its outer
>   LLL (**508.58 s** / **498.96 s**) and built the mpfr GSO — and therefore **not at
>   `BKZ.Param`**;
> - the **mpfr_bits = 100** configuration **did not reach any terminal status** within
>   **14 449 s** of elapsed wall clock and produced no record of any kind.
>
> **Nothing else.**

**What this does not support**, stated so no later reader must infer it:

- **no comparison of 75 against 100 bits** — the treatment arm produced no observation, and a
  reference arm without a treatment arm measures nothing about the treatment;
- **no cost** for the 100-bit cell, and **no ratio** between the cells (OBJ-11);
- **no statement about precision's effect at tour level** at this cell, in either direction;
- **no support for or against** any of `DEC-20260814-4ac30a`'s escalation branches, and **no
  ripeness** for any of them;
- **no obstruction measurement** at a precision above the isolated-step minimum — which is what
  RT-CTRL-1 was commissioned to obtain and did **not** obtain;
- **no Stage-1 sizing**, no change to `H-MLKEM-7d9bcc` (`proposed`) or `EXP-MLKEM-42ea04`
  (`review_required` / `approved_by: null`), no claim-tier movement;
- **no statement about ML-KEM at any parameter set, at any dimension** — the object under test is
  the null object (§1(iii)).

**On closure:** nothing here supports closing anything, and I would object to a closure on this
record under `docs/inventor-protocol.md` §4 — a batch that produced no declared outcome, on an
instrument that could not have recorded a success, against a budget inconsistent with its own
hypothesis, is a **fatigue report about the search**, not a statement about the problem. The
symmetric error is equally live: **this record does not support pausing or deprioritising the
lane either**, and CTRL-B is cheap.

---

## 10. Baseline comparison

**Pollard-rho and BSGS are not applicable** and I decline to manufacture a comparison: this is
lattice basis reduction, not a discrete-log solve — there is no group, no relation collection, no
rank condition, no source recovery and no target descent, and the batch claims no algorithmic
gain over anything.

**`dominated_by`: not applicable, and correctly so.** The batch proposes no algorithm and asserts
no Pareto position; `claim_tier: toy` is set throughout and no `sota_delta` is claimed anywhere.
That is the honest state and I confirm it rather than requiring a fabricated `null`.

**The baseline that IS due and is missing** is the one in OBJ-14 / CTRL-B: the cost of the *same
operation* in a configuration that terminates. My PROBE G supplies the first point (d=80, β=55:
274.29 s, 26 tours). Until that curve exists, the goal cannot say whether 14 449 s at d=512 is
anomalous or ordinary, and **an eliminated or unmeasured cost dimension is not a result until its
own cost is in the total** (`KN-LIT-7593`).

---

## 11. Next concrete action — exactly one

**Before any further capped lattice run, land the instrument fixes as a successor task under a
new runner hash (CTRL-A, items 1–7), and in the same task run CTRL-B's dimension ladder at fixed
β=55 — d ∈ {80, 96, 112, 128, 160, 192} × {75, 100} bits, two invocations per cell — instead of
re-running the d=512 100-bit cell at a larger budget.**

This discharges `DEC-20260815-3e8e9c` condition (i), which is still undischarged one batch later;
runs the specified "ONE FULL BKZ TOUR" for the first time; produces the cost-vs-dimension curve
and the tours-per-hour figure the goal has never had and that any Stage-1 sizing requires;
answers RT-CTRL-1's actual question at a dimension where it is affordable; and removes the budget
coupling — all for a few thousand seconds against the 21600 s this batch spent. **Re-running the
d=512 100-bit cell at a larger budget before this is done would be the third consecutive batch to
spend the majority of its compute learning one bit**, and on an instrument that still cannot
record a success.

---

## 12. Required output record

```yaml
red_team_report:
  id: RT-20260824-6fc282
  task_id: TASK-20260824-6fc282
  goal_id: GOAL-MLKEM-005
  batch_id: BATCH-f9780d
  snapshot_commit_read: e17d95cbfdfcdb047c682c89a626745fe53b72e2
  claim_tier: toy

  claim_under_review: >-
    That BATCH-f9780d's RT-CTRL-1 matched pair, as archived, supports any conclusion at all
    about the effect of mpfr precision on the full BKZ tour at (d=512, beta=55). The producer
    and the snapshot commit already refuse all four pre-declared outcomes; what this review
    challenges is what remains, what the batch is likely to be read as having shown, and the
    Coordinator's conduct of the batch.

  verdict: >-
    ACCEPTED AS AN HONEST AND CAREFULLY SCOPED RECORD OF A NON-RESULT; ITS INSTRUMENT AND ITS
    COST MODEL ARE REJECTED. The 75-bit ERROR is terminal, deterministic across two
    same-container runs, and correctly established as NOT occurring at BKZ.Param -- that part
    is solid and is not challenged. Everything else the batch could have shown was foreclosed
    before the run: the pinned runner cannot record either quantity its own completion gate
    names, the binding instrument condition of the authorising decision was not implemented,
    and the budget expectation was inconsistent with every outcome the task card declared.

  objections:
    - id: OBJ-1
      severity: critical
      title: The instrument could not have discharged its own completion gate on any outcome.
      finding: >-
        The gate requires status, wall clock, TOURS and ROOT-HERMITE FACTOR for both cells.
        `result["tours"] = getattr(bkz, "tours", None)` is dead code -- BKZReduction has no
        `tours` attribute (hasattr False; only `tour`, a method) -- and `bkz(par)` is called
        without tracer=True, so bkz.trace is None as well; the runner has no route to a tour
        count in any branch. The root-Hermite factor uses `(Q**0.5)**(1.0/1)` where the
        divisor exponent must be 1.0/d, wrong by q^(1/2-1/2d) ~= 57.4 at d=512 (measured at
        d=60: 0.0188 vs 1.0146, ratio 53.93 exactly as predicted). Had the batch achieved
        `both_complete` or `hundred_completes_seventyfive_errors` -- the two outcomes it
        existed to obtain -- it would have reported tours=null and a root-Hermite factor wrong
        by ~57x, silently. This is a REGRESSION: the twice-reviewed pinned predecessor
        (58a1fdc2...) does all three correctly, plus traceback.format_exc() on ERROR. The
        runner was rewritten, not reused, while its docstring and DEC-20260824-526f89 assert
        the predecessor is reused VERBATIM; the difference is nowhere disclosed.
      verified_by: PROBE A, PROBE B, PROBE D, source diff against 58a1fdc2...
    - id: OBJ-2
      severity: critical
      title: DEC-20260815-3e8e9c binding condition (i) was not implemented; its pre-quantified cost recurred.
      finding: >-
        Condition (i) -- binding, restated verbatim in GOAL-MLKEM-005.next_action -- required
        psutil .cpu_times(), a SIGTERM handler or per-tour flush persisting the tour count,
        stdout_tail retention for a timed-out cell, and load average in environment.json, ALL
        BEFORE ANY FURTHER CAPPED RUN, because "this batch spent 63.9% of its compute to learn
        one bit". The pinned runner implements none of the four (imports: hashlib, json, os,
        sys, time). This batch then spent 14449 s -- 67% of its compute -- to learn one bit.
        The snapshot commit owns "a design defect in the runner I wrote" but never mentions
        condition (i), records no procedure_deviation, and frames a non-implementation of a
        binding condition as a newly-discovered defect. Conditions (ii), (iv) and (v) WERE
        honoured; (v) is why the 75-bit reproducibility exists at all.
    - id: OBJ-3
      severity: high
      title: Condition (i) as worded cannot work; two traps, both verified.
      finding: >-
        (1) fpylll assigns self.trace = tracer.trace only after the tour loop and tracer.exit(),
        so bkz.trace is None for the entire run and a SIGTERM handler reading it gets None --
        reproduced (PROBE F: handler fired at 399.66 s, wrote outer_lll_s and float type, but
        tours_completed null despite tracer=True). (2) bkz2.svp_preprocessing calls self.tour()
        RECURSIVELY (bkz2.py:79), so a naive tour() override over-counts at any block size with
        preprocessing -- block 55 carries preprocessing_block_sizes [36]. The working route is
        a tour() override gated on min_row==0 and max_row==-1 (PROBE H: flushed 11 == trace 11).
        A successor told only to "implement condition (i)" implements the half that cannot work.
    - id: OBJ-4
      severity: high
      title: Per-operation cost used where total expected cost was required.
      finding: >-
        The budget asserts P1 (75 and 100 bits are the same 2-limb regime, so no step change in
        per-operation cost) from the GMP limb boundary and never measures it, then concludes P2
        (total cost parity). P2 does not follow from P1: total = per-op cost x operation count,
        and the operation count is exactly what precision moves. I MEASURED P1 AND IT HOLDS
        (update_gso ratio 100/75 = 0.937 at d=128, 1.017 at d=256; full-tour ratio 1.012 at
        d=80), which isolates the failure to P2 -- contradicted in direction by the goal's own
        committed 376.4x growth on +6 bits (69->75), against which the batch budgeted +25 bits
        at parity. The anchor is additionally a TIME-TO-ERROR used to predict the cost of a
        cell hypothesised not to error.
      verified_by: PROBE E, PROBE G
    - id: OBJ-5
      severity: high
      title: The isolated-step result is read at tour level, on the cost axis.
      finding: >-
        No artifact reads EV-MLKEM-e4189c's 100-bit isolated-step COMPLETION as a tour-level
        OUTCOME -- that axis is clean and repeatedly guarded. But GOAL-MLKEM-005.next_action
        uses that same completion as the first of two premises for a tour-level COST
        expectation ("inside the already-validated window ... so ... costs the same order as
        the 2502.74s"), which is KN-FIND-f54a82's forbidden inference on the resource axis.
        This batch inherited the conclusion without re-examining the premise and sized 21600 s
        against it.
    - id: OBJ-6
      severity: medium
      title: There is NO tension between the isolated-step 100-bit COMPLETION and the >=14448 s non-termination.
      finding: >-
        Asserting one would itself be the KN-FIND-f54a82 error. The isolated step is lll_obj()
        at bkz.py:123; the tour is BKZReduction.__call__ with real block enumeration at beta=55
        over 512 dimensions, and PASSING the preprocessing step is what LETS the computation
        enter expensive BKZ work. The two observations are what the goal's own 376.4x precision
        response predicts. The tension that DOES exist is between >=14448 s and the ~2500 s
        budget expectation -- a measurement against a planning estimate, in which the planning
        estimate loses. It is evidence about the BUDGET MODEL and about nothing else: not about
        precision, the obstruction, C1/C2, H-MLKEM-7d9bcc, or ML-KEM.
    - id: OBJ-7
      severity: high
      title: The specified experiment is not the executed experiment.
      finding: >-
        Every record says "ONE FULL BKZ TOUR". The runner sets flags=BKZ.AUTO_ABORT with no
        max_loops and calls bkz(par), which runs tours until auto-abort -- measured at 11 tours
        (d=60, beta=20) and 26 tours (d=80, beta=55). Inherited from the predecessor, whose own
        field is n_tours (plural), so the descriptor has been inaccurate across at least three
        batches. Load-bearing for the budget (a reader sizes one tour and gets 26) and for what
        the goal believes it has failed to do. No record in this goal's entire d=512 history
        contains a tour count for any d=512 cell, because n_tours is assigned only on the
        COMPLETED path.
      verified_by: PROBE D, PROBE G
    - id: OBJ-8
      severity: high
      title: The batch changed the pruning schedule and deleted the detector for that change.
      finding: >-
        The predecessor captured traceback.format_exc() on ERROR and DEC-20260815-3e8e9c relies
        on it, localising the predecessor failure at bkz.py:186 inside a doubly-nested
        svp_preprocessing, distinct from bkz.py:123. The new runner records only
        "TypeName: message". So this batch cannot establish whether its 75-bit error is at the
        SAME call site as the predecessor's -- the one comparison that would show whether
        swapping the pruning schedule changed the failure mode, and svp_preprocessing is
        precisely where the schedule enters (block 55 -> preprocessing [36]). Cost of keeping
        it: one line, already present in the script being "reused verbatim".
    - id: OBJ-9
      severity: medium
      title: 2502.74 s is guarded as a contrast and used as a budget calibration.
      finding: >-
        No artifact draws a scientific contrast against it -- surface (i) is satisfied, and the
        demotion was pre-committed before any number existed, which I credit. But three
        artifacts multiply it by two to set an expectation and size a ceiling against it
        (dispatch_queue budget_justification, task_card budget.justification,
        instrument_readiness). That is a calibration, not a sanity reference, and the "sanity
        reference only" declaration does not reach it. It is additionally a cross-container
        time-to-ERROR under unrecoverable strategies bytes, on a host the goal's own record
        shows measuring far slower than the one independent re-execution of the same cell
        (1104.40 s of BKZ work, per DEC-20260815-3e8e9c). The guard was placed on the axis that
        held; the axis that broke was unguarded.
    - id: OBJ-10
      severity: medium
      title: "\"Two independent attempts\" overstates the independence axis."
      finding: >-
        The attempts share host, container, binary, script bytes, strategies bytes, seed and
        basis, differing only in the process-detachment mechanism and the timeout value. That
        is a determinism check (real, and worth having -- timings 2.6% apart, outer LLL 1.9%
        apart, both inside the goal's 5-8% environmental bar), not independence in the sense
        BATCH-0d5018 earned with second-host re-execution. DEC-20260815-3e8e9c applies exactly
        this scruple to same-family reviewers. Recommend "reproduced across two same-container
        runs".
    - id: OBJ-11
      severity: medium
      title: The ">= 4.7x" ratio should not be reported at all.
      finding: >-
        14448/3051.8 divides a CENSORED observation by an UNCENSORED one and has no
        interpretation as a cost multiplier. The snapshot commit correctly calls it a lower
        bound on an unfinished computation, but also states it in the WHAT THE RUN PRODUCED
        header, making it the number most likely to be lifted into EV-MLKEM-59e4a4 and read as
        "precision costs 4.7x". The measured tour-level ratio at a terminating dimension is
        1.012 (PROBE G). Report the two raw numbers and the censoring; drop the ratio.
    - id: OBJ-12
      severity: medium
      title: The retraction is incomplete where it does harm; one part of it is too harsh.
      finding: >-
        The false claim lives in dispatch_queue.json line 44 (artifact_paths_note), which is
        UNCHANGED at the snapshot; the retraction exists only in a commit message, the receipt
        does not mention the defect, and no ledger record does. This goal has a precedent for
        exactly this repair (DEC-20260815-3e8e9c's held_no_shell_note, control-plane correction
        to BATCH-0d5018's dispatch_queue.json, "matching commit 217da33ae"). CORRECTION IN THE
        COORDINATOR'S FAVOUR: the claim that 14448 s "survives only in the executor's report
        and in this receipt, not in the machine-readable record" is too pessimistic -- it is
        derivable from stdout.log (07:12:10), run_end_utc.txt (11:12:59) and the absence of a
        cell-100 entry, corroborated by exit_rc.txt. What is genuinely unrecoverable is tour
        progress and per-cell resource data.
    - id: OBJ-13
      severity: high
      title: Route (c) did not require single-invocation coupling, which cost the target cell a third of its runway.
      finding: >-
        The matched-pair property comes from content-pinning the strategies file and forcing the
        seed, not from one process. VERIFIED at the batch's own parameters: d=512, seed
        452658293 yields basis hash dbfc330340353ef2 identically in a fresh process and after
        re-seeding post-cell. Two invocations would have preserved every matched-pair property
        with independent budgets. As executed the 100-bit cell got 14449 s of a 21600 s ceiling
        (67%), because the reference cell's 3051.8 s came out of the same ceiling and attempt
        1's infrastructure kill re-charged ~2974 s of unresumable reference-cell work.
      verified_by: PROBE C
    - id: OBJ-14
      severity: high
      title: No reference cost exists for this operation, so the headline non-result is not yet known to be a finding.
      finding: >-
        No completed d=512 cell exists at any precision in any batch, and no tour count for any
        d=512 cell in any record. PROBE G supplies the first data point and suggests 14449 s is
        unremarkable: beta=55 costs 274 s for 26 tours at d=80 and does not complete within
        400 s at d=128. One tour is ~(d-beta) SVP calls -- 25 at d=80 vs 457 at d=512 -- so a
        full auto-abort run at d=512 plausibly sits in the tens of thousands of seconds (stated
        as an order-of-magnitude reasoning check, NOT a measurement). If roughly right, the
        ceiling was below the job's cost at EITHER precision and the non-termination carries no
        information about precision whatsoever.

  required_controls:
    - id: CTRL-A
      cost: zero lattice compute
      title: Fix the instrument before any further capped run -- condition (i), still undischarged.
      items: >-
        Under a NEW runner hash (the pinned runner is receipt-bound and must not be edited):
        (1) STARTED stub before each cell; (2) bkz(par, tracer=True); (3) per-tour flush by
        overriding BKZReduction.tour() gated on min_row==0 and max_row==-1, NOT a SIGTERM read
        of bkz.trace; (4) traceback.format_exc() on ERROR; (5) the predecessor's
        get_log_det-based root-Hermite factor; (6) psutil .cpu_times() and load average into
        environment.json; (7) two invocations with an --mpfr-bits argument, not one.
    - id: CTRL-B
      cost: a few thousand seconds total
      title: THE CHEAPEST OVERTURNING CONTROL -- a dimension ladder at fixed beta=55.
      items: >-
        d in {80, 96, 112, 128, 160, 192} x {75, 100} bits, same construction, same strategies,
        with the CTRL-A instrument. Already partially run here: d=80 completes at BOTH
        precisions (274.29 s / 277.56 s, 26 tours each); d=128 does not complete within 400 s.
        Yields the first cost-vs-dimension curve for this operation, the d at which 75 fails
        while 100 still succeeds (RT-CTRL-1's actual question, tested where affordable), and a
        tours-per-hour figure. Decisive in either direction and cheaper than one d=512 cell.
    - id: CTRL-C
      cost: ~2800 s
      title: RT-CTRL-3(ii), the ML-KEM-shaped nearby-object control -- REQUIRED since DEC-20260815-3e8e9c, deferred twice.
      items: >-
        Every d=512 obstruction this goal has measured is on a generic random q-ary lattice,
        which DEC-20260815-3e8e9c itself identifies as the NULL OBJECT. A signal present in the
        null object is not yet a signal (docs/inventor-protocol.md section 3). Blocks transfer
        in BOTH directions, so it equally blocks any escalation branch's "the construction is
        exhausted" claim.
    - id: CTRL-D
      cost: subsumed by CTRL-B
      title: The parameter meant to destroy the signal, and what it should do.
      items: >-
        The parameter is mpfr precision; the failure should first be DEFERRED and then
        DISAPPEAR, after which cost saturates. The goal's own data already behaves this way
        (69: never entered a tour; 75: ~35 min then failure; 100: no failure in >=13950 s), so
        THE CANONICAL ARTIFACT TELL IS ABSENT and the obstruction behaves like a genuine
        numerical-precision effect. Recorded as a point in the batch's favour. CTRL-B turns
        three anecdotes into a curve.
    - id: CTRL-E
      cost: free -- ALREADY PERFORMED BY THIS SESSION
      title: The strategies input's identity, which no committed artifact records.
      items: >-
        sha256 f516b0a6f0c580cff72e1e2c3562c44dc6f17e8f99613e9e4020e35481b27a18 is
        byte-identical to upstream fplll master strategies/default.json, fetched 2026-08-25
        from raw.githubusercontent.com/fplll/fplll/master/strategies/default.json. 8,606,859
        bytes; 101 entries, block_size 0..100; block 55 carries preprocessing_block_sizes [36]
        and 21 pruning parameter sets, so it is a genuine tuned schedule and NOT
        KN-TECH-14efa5's pruning-free [Strategy(b) for b in range(41)] (which would not cover
        beta=55). `master` is a moving ref: the durable pin is git blob sha1
        3e80d1636be1e6d67f6dc082dc95225842e0aa25. The batch pinned a load-bearing input by
        content and recorded NO ORIGIN anywhere, repeating in weaker form the exact provenance
        failure it was opened to fix.

  counterexample_or_mutation: >-
    Re-run the 75-bit cell ALONE, same seed and basis, under a DIFFERENT strategies source
    (e.g. KN-TECH-14efa5's pruning-free [Strategy(b) for b in range(56)]). ~3000 s. If
    "infinite loop in babai" persists at the same wall-clock order, the failure is independent
    of the pruning schedule, route (c)'s substitution is harmless and retroactively validated,
    and the upstream reproducer strengthens. If it changes, this batch's 75-bit ERROR is partly
    a strategies artifact, is not comparable to the predecessor's at all, and OBJ-8's deleted
    traceback becomes load-bearing. This is the null object of the same shape for the
    strategies variable specifically, and the only way to bound the one confound route (c)
    introduced.

  baseline_comparison: >-
    Pollard-rho and BSGS are NOT APPLICABLE and no comparison is manufactured: this is lattice
    basis reduction, not a discrete-log solve -- no group, no relation collection, no rank
    condition, no source recovery, no target descent, and no algorithmic gain is claimed.
    dominated_by: not applicable, and correctly so -- the batch proposes no algorithm and
    asserts no Pareto position; claim_tier toy is set throughout and no sota_delta is claimed
    anywhere. THE BASELINE THAT IS DUE AND MISSING is the cost of the SAME operation in a
    configuration that terminates (OBJ-14 / CTRL-B); PROBE G supplies the first point (d=80,
    beta=55: 274.29 s, 26 tours). Until that curve exists the goal cannot say whether 14449 s
    at d=512 is anomalous or ordinary, and an unmeasured cost dimension is not a result until
    its own cost is in the total (KN-LIT-7593).

  heuristic_challenges:
    - >-
      THE ONE UNSTATED HEURISTIC IS THE LOAD-BEARING ONE. "100 bits costs the same order as the
      2502.74 s already spent at 75 bits" rests on two premises of which only the irrelevant one
      is written down: per-operation parity in the 2-limb regime (P1, asserted from the GMP limb
      boundary, MEASURED HERE AND TRUE) and total-cost parity (P2, never stated, false in
      direction by the goal's own 376.4x datum). Numbering P2 explicitly and giving it a
      falsification condition is the minimum repair.
    - >-
      The "2-limb regime" argument is a per-operation claim doing total-cost work. It should be
      restated as: per-operation cost is flat below the 129-bit limb boundary (now measured:
      ratio 0.937 / 1.017 / 1.012), and total cost is per-operation cost times operation count,
      of which only the first factor is bounded by the limb argument.
    - >-
      "One full BKZ tour" is an unstated modelling assumption, not a description: the executed
      job is BKZ-to-auto-abort, 26 tours at the one beta=55 dimension anyone has measured
      (OBJ-7).

  cost_model_challenges:
    - >-
      Total expected cost was never computed. Per-attempt cost x inverse success probability is
      the required form; the batch used a per-attempt cost that was itself a TIME-TO-FAILURE,
      with the success probability silently set to 1 in a batch whose own pre-declared outcome
      set contained two failure branches.
    - >-
      Memory is recorded (peak RSS ~175 MB, single-threaded) and is not a binding constraint
      here; the binding resource is wall clock, and the coupling in OBJ-13 removed 33% of it
      from the target cell before any science ran.
    - >-
      The budget's own error bar is missing. The goal records a 5-8% within-host environmental
      bar, and DEC-20260815-3e8e9c records the SAME cell measuring 1104.40 s of BKZ work on a
      second host against the producer's 2502.74 s total -- a cross-host spread far exceeding
      it. A ceiling sized from a single cross-container figure at +/-0% is not defensible on
      the goal's own record.
    - >-
      No reference cost exists for the operation at any dimension in this goal's history
      (OBJ-14). PROBE G supplies the first: d=80, beta=55 -> 274.29 s / 26 tours.

  reduction_and_scope_challenges:
    - >-
      SCOPE IS NOT INFLATED and I confirm it: claim_tier toy throughout, explicit toy-scale and
      transfer statements in the executor report, the decision, the dispatch queue, the receipt
      and the snapshot commit. Surface (iii) is clean.
    - >-
      THE SCOPE LIMIT THE BATCH DOES NOT STATE, and which is stronger than the one it does: the
      object under test IS the null object (a structureless random q-ary lattice), as
      DEC-20260815-3e8e9c itself records. This licenses no ML-KEM statement AT ANY DIMENSION,
      not merely at d=512 -- and symmetrically it cannot support "the construction is exhausted
      at d=512" either, since that claim ranges over objects the measurement excludes.
    - >-
      No cited reduction is instantiated by this batch; there is no corollary chain to audit.
      The only inherited claim-transfer is the isolated-step-to-tour-level cost inference of
      OBJ-5, which KN-FIND-f54a82 forbids.

  proof_architecture_challenges:
    - >-
      Not applicable: this batch is a measurement, not a proof-oriented claim, and carries no
      proof_search_map obligation under docs/inventor-protocol.md section 8. The nearest
      analogue that DOES apply is the NEARBY-OBJECT control, and it is missing: CTRL-C.
    - >-
      METHOD-CEILING ATTACK, applied to the batch's design rather than to a theorem: the largest
      claim this instrument could support under ideal tuning was "both cells terminal, with
      status and wall clock" -- because tours and the root-Hermite factor were unrecordable in
      every branch (OBJ-1). That ceiling does not reach the batch's own declared outcomes
      `both_complete` or `hundred_completes_seventyfive_errors`, both of which promise a per-cell
      cost and a quality metric for Stage-1 sizing. The design fails its own ceiling check before
      any compute is spent.

  closure_challenge: >-
    NOTHING HERE SUPPORTS CLOSING ANYTHING, and I would object to a closure on this record under
    docs/inventor-protocol.md section 4: a batch that produced no declared outcome, on an
    instrument that could not have recorded a success, against a budget inconsistent with its
    own hypothesis, is A FATIGUE REPORT ABOUT THE SEARCH, not a statement about the problem.
    The symmetric error is equally live and I name it: this record does not support pausing or
    deprioritising the lane either. CTRL-B is cheap, and CTRL-D records that the artifact tell
    is ABSENT -- the failure decays under the parameter meant to destroy it, at every point
    anyone has measured.

  resource_reading:
    examined: true
    readings:
      - id: R1
        reading: >-
          The 75-bit failure's ROBUSTNESS is an asset nobody in the batch names. It now
          reproduces across two containers, two hosts, TWO DIFFERENT PRUNING SCHEDULES (an
          unrecoverable Debian libfplll8 build and upstream fplll master) and four runs. With
          CTRL-E's identification of the strategies input and CTRL-A's traceback restoration,
          the "upstream fplll bug report" branch -- recorded in DEC-20260815-3e8e9c as better
          supported than the others but not ripe -- now has a materially stronger, publicly
          reproducible reproducer, and PROBE F suggests a cheap one at d=128 rather than d=512.
        status: candidate for the ranking, NOT evidence; changes no status.
      - id: R2
        reading: >-
          The censored 100-bit observation is weak evidence FOR the mechanism, in the direction
          the goal wants: >=13950 s of reduction work without raising, against the 75-bit cell's
          ~2550 s to failure, with per-operation parity now measured (PROBE E/G) so the
          wall-clock comparison is a legitimate proxy for operation count. A censored
          observation cannot separate "removed", "deferred" and "the tour is simply slow at this
          d"; CTRL-B separates all three.
        status: candidate for the ranking, NOT evidence; changes no status.
    spawned_ids: []
    spawned_ids_note: >-
      No new record identifier is minted by this review. R1 and R2 are candidates for the
      Coordinator's ranking; if either is carried forward it should be minted by the ledger
      archive via tools/allocate_id.py, not here.

  narrowest_supported_statement: >-
    At (d=512, beta=55, q=3329, k=d/2, seed 452658293) under fpylll 0.6.4 with a ROW_EXPO-free
    mpfr GSO and BKZ block size 55 with AUTO_ABORT and no loop bound, under upstream fplll
    master's strategies/default.json (sha256 f516b0a6...), on one 4-CPU container: the
    mpfr_bits=75 configuration raises ReductionError('infinite loop in babai') after 2974.3 s
    and 3051.8 s in two same-container runs, having completed its outer LLL (508.58 s /
    498.96 s) and built the mpfr GSO, and therefore NOT at BKZ.Param; and the mpfr_bits=100
    configuration did not reach any terminal status within 14449 s of elapsed wall clock and
    produced no record of any kind. NOTHING ELSE. In particular: no comparison of 75 against
    100 bits (the treatment arm produced no observation), no cost for the 100-bit cell, no
    ratio between the cells, no statement about precision at tour level in either direction, no
    support for or against any escalation branch and no ripeness for any, NO OBSTRUCTION
    MEASUREMENT AT A PRECISION ABOVE THE ISOLATED-STEP MINIMUM (which is what RT-CTRL-1 was
    commissioned to obtain and did not obtain), no Stage-1 sizing, no change to H-MLKEM-7d9bcc
    or EXP-MLKEM-42ea04, no claim-tier movement, and no statement about ML-KEM at any parameter
    set at any dimension.

  next_concrete_action: >-
    BEFORE ANY FURTHER CAPPED LATTICE RUN, land the CTRL-A instrument fixes as a successor task
    under a NEW runner hash, and IN THE SAME TASK run CTRL-B's dimension ladder at fixed
    beta=55 -- d in {80, 96, 112, 128, 160, 192} x {75, 100} bits, two invocations per cell --
    INSTEAD OF re-running the d=512 100-bit cell at a larger budget. This discharges
    DEC-20260815-3e8e9c condition (i), still undischarged one batch later; runs the specified
    "ONE FULL BKZ TOUR" for the first time; produces the cost-vs-dimension curve and
    tours-per-hour figure the goal has never had and any Stage-1 sizing requires; answers
    RT-CTRL-1's actual question at a dimension where it is affordable; and removes the budget
    coupling -- for a few thousand seconds against the 21600 s this batch spent. Re-running the
    d=512 100-bit cell at a larger budget before this is done would be the third consecutive
    batch to spend the majority of its compute learning one bit, on an instrument that still
    cannot record a success.

  artifact_paths:
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/reviews/TASK-20260824-6fc282/review.md

  artifacts_read:
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/dispatch_queue.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/archives/TASK-20260824-c7248f/receipt.yaml
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/task_card.yaml
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/rt_ctrl_1_matched_pair.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/rt_ctrl_1_matched_pair_results.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/rt_ctrl_1_matched_pair_results.attempt1_killed.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/execution_report.md
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/stdout.log
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/stdout.attempt1_killed.log
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/stderr.log
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/exit_rc.txt
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/run_start_utc.txt
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/run_end_utc.txt
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/run_start_utc.attempt1_killed.txt
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/killed_at_utc.attempt1.txt
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/inputs/fplll_strategies_default.json
    - coordination/goals/GOAL-MLKEM-005/instrument_readiness_20260824.md
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-0d5018/tasks/TASK-20260815-f14d3c/stage0_d512_beta5570_precision_bisection_and_reattempt.py
    - ledger/decisions/DEC-20260824-526f89.yaml
    - ledger/decisions/DEC-20260815-3e8e9c.yaml
    - ledger/evidence/EV-MLKEM-e4189c.yaml
    - ledger/goals/GOAL-MLKEM-005.yaml
    - knowledge/findings/KN-FIND-f54a82.md
    - knowledge/techniques/KN-TECH-14efa5.md
    - AGENTS.md
    - agents/red-team.md

  review_attestation:
    joints_owned:
      - "surface (i): 2502.74 s as contrast vs sanity reference"
      - "surface (ii): isolated-step vs tour-level reading, and the alleged tension"
      - "surface (iii): toy scale and FIPS 203"
      - "surface (iv): what the 75-bit reproducibility buys"
      - "surface (v): the cheapest overturning control"
      - "coordinator conduct: route (c) substitution, retraction completeness, budget sizing"
    read_sibling_reports: false
    read_sibling_reports_note: >-
      blindness.lifted_for names no task here, and
      reviews/TASK-20260824-bc488d/ did not exist at the snapshot commit. The Validator's
      arithmetic and receipt checks were deliberately NOT duplicated; where a figure of mine
      touches theirs it is flagged as their territory.
    independent_session: true
    independence_kind: >-
      PROCEDURAL, AND ONLY PARTLY MODEL-LEVEL. This session did not produce, run, dispatch or
      archive any artifact under review, and executed its own probes rather than re-reading the
      producer's. It is the same model family as the producing and archiving sessions
      (claude-opus-5), which is disclosed rather than counted: NO AGREEMENT BETWEEN THIS REVIEW
      AND ANY OTHER SESSION IN THIS BATCH MAY BE RECORDED AS DISTINCT-MODEL CORROBORATION.
      AGENTS.md rule 12 remains UNMET AND UNWAIVED.
    requested_policy: review-adversarial
    resolved_model_id: claude-opus-5
    reasoning_effort: xhigh
    fallback_used: false
    degraded_allowed: false
    degraded_requirements: []
    model_verified: false
    model_verified_reason: >-
      No orchestration.adapter probe receipt exists for this session; AUTORESEARCH_POLICY and
      AUTORESEARCH_BACKEND are unset. Recorded as unverified rather than asserted.
    attestations_recorded: >-
      NONE. This review obtained no attestation from any model or session and records none. It
      performs no state transition, moves no hypothesis, and writes no ledger record.
    prohibitions_honoured: >-
      No producer artifact and no ledger record was altered. Nothing was committed. No bounded
      failure is called an impossibility result. No broader ECDLP or ML-KEM conclusion is
      claimed. All probe scripts and outputs were written OUTSIDE the repository, under this
      session's scratchpad, so that this task's declared artifact_paths set remains exactly the
      single review.md the dispatch queue names.
  verdict_on_assigned_joints: >-
    surface (i) HOLDS on the interpretive axis, BREAKS on the resource axis (OBJ-9).
    surface (ii) HOLDS on the outcome axis, BREAKS on the cost axis (OBJ-5); the alleged
    tension does not exist and asserting it would itself be the KN-FIND-f54a82 error (OBJ-6).
    surface (iii) HOLDS, with a stronger limit added that the batch does not state.
    surface (iv) the 75-bit reproducibility is SOLID for determinism and for "not at
    BKZ.Param", and BREAKS as "independent" and as anything about precision (OBJ-10).
    surface (v) DISCHARGED: CTRL-B, partially executed here.
    coordinator conduct: the route (c) SUBSTITUTION IS JUSTIFIED; its single-invocation
    IMPLEMENTATION BREAKS (OBJ-13); the retraction is INCOMPLETE (OBJ-12); the budget sizing is
    NOT DEFENSIBLE on the record available before the run (OBJ-4, and section 2(c)).
```

---

## 13. Appendix — probe sources

All probes ran under the task card's declared interpreter, wrote only into this session's
scratchpad (`…/15de1654-2503-5954-afd1-67e6db6674e9/scratchpad/`), and touched no repository
artifact. `strat.json` below is the snapshot's own
`inputs/fplll_strategies_default.json`, extracted with `git show` and sha256-verified as
`f516b0a6f0c580cff72e1e2c3562c44dc6f17e8f99613e9e4020e35481b27a18`.

### Probes A, B, C (instrument assumptions; `rtprobe.py`)

```python
def run_cell(mpfr_bits):
    A = gen()                                   # FPLLL.set_random_seed(SEED); IntegerMatrix.random(...)
    LLL.reduction(A); FPLLL.set_precision(mpfr_bits)
    M = GSO.Mat(A, float_type="mpfr"); M.update_gso()
    bkz = BKZReduction(LLL.Reduction(M, flags=LLL.DEFAULT))
    bkz(BKZ.Param(block_size=BETA, strategies=STRAT, flags=BKZ.AUTO_ABORT))
    out["A_getattr_tours"] = getattr(bkz, "tours", None)      # -> None
    out["A_has_tours_attr"] = hasattr(bkz, "tours")           # -> False
    b0 = float(A[0].norm())
    out["B_runner_formula"]   = b0 ** (1.0/D) / (Q ** 0.5) ** (1.0/1)   # the runner's line 78
    out["B_standard_delta0"]  = (b0 / (Q ** 0.5)) ** (1.0/D)            # standard definition
```

Output (d=60, β=20, 75 bits): `A_has_tours_attr false`, `A_tourlike_attrs ["tour"]`,
`B_runner_formula 0.018814625179154207`, `B_standard_delta0 1.0146116704743195`,
`C_basis_hash_after_a_cell 51424948e22871f3` — matching a fresh process's `51424948e22871f3`.
At d=512 with the batch's own seed 452658293: `dbfc330340353ef2` in both positions and in a
second fresh process.

### Probe D (tour count reachability)

`bkz(par, tracer=True)` → `trace.children` labels
`['lll', ['tour',0], … ['tour',10]]` = 11 tours. Without `tracer=True`,
`repr(bkz.trace) == 'None'` and `hasattr(bkz,'tours') == False`. Installed
`fpylll/algorithms/bkz.py` `__call__` assigns `self.trace = tracer.trace` at line 72, after the
tour loop and `tracer.exit()`.

### Probe E (per-operation parity, and isolated-step status)

```json
{"128": {"75": {"gso_update_s": 0.1231, "isolated_lll_status": "COMPLETED"},
         "100": {"gso_update_s": 0.1154, "isolated_lll_status": "COMPLETED"},
         "per_op_ratio_100_over_75_gso_update": 0.937},
 "256": {"75": {"gso_update_s": 0.9272, "isolated_lll_status": "COMPLETED"},
         "100": {"gso_update_s": 0.9434, "isolated_lll_status": "COMPLETED"},
         "per_op_ratio_100_over_75_gso_update": 1.017}}
```

Additional: the `double` path errors `ReductionError: infinite loop in babai` at d=256 while
mpfr at 75 and 100 bits completes; d=128/75-bit mpfr is deterministic, 8/8 COMPLETED.

### Probes F, H (the condition (i) fix, and its two traps)

```python
signal.signal(signal.SIGTERM, on_term)     # on_term: flush(...); os._exit(124)
flush("STARTED")                           # the stub the pinned runner never writes
...
class FlushingBKZ(BKZReduction):
    def tour(self, params, min_row=0, max_row=-1, tracer=None):
        r = super().tour(params, min_row, max_row, tracer)
        if min_row == 0 and max_row == -1:          # top-level only: svp_preprocessing
            self.n_tours += 1                       # calls tour() recursively (bkz2.py:79)
            json.dump({"tours_so_far": self.n_tours}, open("tourlog.json", "w"))
        return r
```

PROBE F (d=128, β=55, 75 bits, killed at the 400 s cap):
`{"status":"SIGTERM_PARTIAL","elapsed_s":399.66,"tours_completed":null,"outer_lll_s":1.16,
"gso_float_type_used":"mpfr"}` — the handler works; `tours_completed` is null because
`bkz.trace` is `None` mid-run.
PROBE H (d=60, β=20): `flushed_tours: 11` == trace `tours: 11`, written incrementally.

### Probe G (the dimension ladder's first rungs)

```json
{"d": 80, "beta": 55, "bits": 75,  "status": "COMPLETED", "outer_lll_s": 0.22, "bkz_s": 274.29, "tours": 26}
{"d": 80, "beta": 55, "bits": 100, "status": "COMPLETED", "outer_lll_s": 0.21, "bkz_s": 277.56, "tours": 26}
```

Ratio 100/75 = **1.012**, identical tour counts. d=128/β=55/75 bits did not complete within
400 s (PROBE F).

### Probe I (d=512, `max_loops=1`)

Source as PROBES F/H with `flags=BKZ.MAX_LOOPS, max_loops=1` at d=512, β=55, seed 452658293.
First run measured `outer_lll_s: 514.84` — a third independent measurement consistent with the
batch's 498.96 s / 508.58 s — and then crashed on my own subclass's keyword signature, whose
traceback is what exposed the `svp_preprocessing` recursion documented in OBJ-3 trap 2. Result of
the corrected run in §8.

### CTRL-E (strategies provenance)

```
sha256(snapshot inputs/fplll_strategies_default.json)                 = f516b0a6…b27a18
sha256(raw.githubusercontent.com/fplll/fplll/master/strategies/default.json, 2026-08-25)
                                                                      = f516b0a6…b27a18
git blob sha1                                                         = 3e80d1636be1e6d67f6dc082dc95225842e0aa25
bytes 8,606,859 · 101 entries · block_size 0..100 · block 55 → preprocessing_block_sizes [36], 21 pruning sets
```
