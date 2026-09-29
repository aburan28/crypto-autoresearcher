# RT-BATCH-014 — Red Team review of the BATCH-014 accounting, forward plan, and
# archived-comparison standing (GOAL-SSIQ-001, `RUN-SSIQ-a85692-k`, EXP-SSIQ-a85692 v11)

**Reviews the content-verified BATCH-014 package at `5471247e6`** (parent
`a58be63848492aa45c75b8d2d6973a352166de96`, the freeze commit of
`specification_v11.yaml`), archived by `TASK-20260810-dae7ef`, adjudicated by
`DEC-20260810-616fd5`, checkpointed in
`ledger/goals/GOAL-SSIQ-001/checkpoints/BATCH-014.yaml`.

Per `TASK-20260810-971cfa`, this review attacks the batch's **reasoning** — the
accounting, the forward plan, and the standing of the archived comparisons this
lineage rests on. The mechanical verification is `TASK-20260810-098fad`
(Validator), running independently and in parallel; this session did not
coordinate with it, did not read its output, and does not rely on it. Where the
two overlap (the ten declared hashes) that is convergent duplication, not
division of labour.

Every numeric claim below was recomputed in this session directly from the
committed artifacts — `probe_delta_e_comparison.json` (RUN-h),
`truncation_sweep_comparison.json` (RUN-j and RUN-k), the receipt's
`path_sha256` block, and `git log`/`git diff`/`git status` — never taken from
`execution_report.yaml`, from `DEC-20260810-616fd5`'s prose, or from the
producer's commit message. No run artifact, specification, ledger record, or
prior review was written, edited, or re-run. No `git` write of any kind was
performed.

```yaml
inference:
  requested_policy: review-adversarial
  requested_reasoning_effort: xhigh
  resolved_model_id: claude-opus-5
  resolved_effort: xhigh
  resolution_check: >-
    `python3 -m orchestration.adapter resolve --role red_team --independent-session`
    returns `review-adversarial -> anthropic:claude-opus-5 (effort=xhigh)`, which
    is the model that answered and the effort carried by
    `.claude/agents/red-team.md` frontmatter. The requested policy is HONOURED on
    both axes; nothing was downgraded and no refusal was required.
  resolved_model_provenance: >-
    Self-reported by this Claude Code subagent session and cross-checked against
    orchestration/model-bindings.yaml (anthropic -> review-adversarial ->
    claude-opus-5, provenance runtime-verified). Not probe-verified this session.
  model_verified: false
  fallback_used: false
  degraded: false
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent. Shares a model family
    with the Executor, the Coordinator, every pre-freeze reviewer in this
    lineage, and the concurrent Validator. This review does not upgrade the
    campaign's evidence tier and does not itself satisfy or advance any closure
    quorum. It is a fresh session with no producer context: it did not author,
    dispatch, or advise on the contract, the run, the receipt, or the decision.
```

---

## VERDICT: `CHALLENGE-narrow`

**Not `BLOCK`, and not for politeness.** The archive is sound on every check I
could apply independently: all ten declared `sha256` values recompute exactly
against the working tree; `git diff --stat 5471247e6` over the declared paths is
empty; `git log --all -- .../RUN-SSIQ-a85692-k` shows **exactly one** commit and
`git log a58be638..5471247e6` shows **exactly one** commit, so no intervening
state entered history between contract freeze and package landing; the declared
path set is exactly `specification_v11.yaml`'s own `required_artifacts` list
(nine run files, spec lines 2088–2097) plus the one new implementation module;
`git status --porcelain` over `experiments/` and `coordination/` is clean. The
gate fired on archived data I read myself (RUN-h `environment.json`:
`Linux-6.18.5-fc-v18-x86_64-with-glibc2.39`, `cpus_available: 4`). The claim
boundaries in the decision, the receipt, and the shard are stated with unusual
discipline and I found no instance of the non-official CAL-1 figures being cited
as RUN-k data anywhere in the package.

**Not `CONCUR`, and not to look rigorous.** Three findings survive that the
package does not contain, each demonstrated against frozen text or committed
data rather than against anyone's prose:

1. **The frozen contract pre-registered a DO-NOT-DISPATCH rule for exactly this
   condition, the round-4 verification checklist does not contain it, and the
   information needed to apply it was in the Coordinator's own prior correction
   record.** "The gate worked as designed" is true and is not the whole finding
   (RC-4).
2. **The contract's own defer-yield was half delivered.**
   `contribution_accounting_v11` pre-registers that on a defer the run still
   yields item (3) *and* "the calibration measurements for roughly 140 s".
   Item (3) landed; the calibration measurements did not, and the copy of them
   that exists sits outside the official record where the campaign has correctly
   forbidden itself from citing it (RC-1).
3. **Forward branch (A) does not fix the defect this batch exposed.** Every gate
   branch other than G-0c is one-sided against a *slow* host. A
   Linux/x86_64/4-CPU host that is merely newer and faster passes G-0c, passes
   G-0, G-0b, G-1, G-2 and G-2b, reaches G-3 `PROCEED, CLEAN`, and destroys the
   b = 1.10 s control — and an exact identity match actively promotes the *wrong*
   explanation branch in the reading rules (RC-2).

None of these invalidates `RUN-SSIQ-a85692-k`, the archive, or the
`completed_valid` finding. They are challenges to the **accounting** and the
**forward plan**, which is what this task asked for. Narrow, not broad: I am not
asking for any artifact to be withdrawn, and I do not find the Coordinator's
framing dishonest — I find it incomplete in the campaign's own favour, in three
specific and repairable places.

---

## RC-1 — Should a defer this cheap consume a batch at all?

**Outcome: the dilemma as posed is a false one under this campaign's actual
budget regime; the genuine exposure is a third thing neither horn names.**

**Horn one (capacity absorption) does not bite, for a reason the card could not
have known without reading the goal record.** `GOAL-SSIQ-001` is running under
`campaign_budget.maximum_batches: null` ("No budget constraints", user-authorized
2026-08-06). A batch index is descriptive, not budgetary. A 0.1884760856628418 s
environment check therefore absorbs no research capacity in the sense the
question presumes, because there is no capacity ration to absorb. What a batch
slot *does* consume here is narrative position in the goal's history, and the
shard is honest about that: `outcome_summary` states the defer plainly,
`claim_boundary` forbids every citation, and `lever_states` sets
`changed_this_batch: false` for **every** lever without exception, stated
positively rather than left to inference. I checked for slot inflation and did
not find it. The one legibility hazard is the shard's `objective` field, which is
written in the intended tense ("measuring (1) ... (2) ...") and reads, in
isolation, as a description of what happened; a reader is corrected two fields
later. The phrase "Sixth batch under the No budget constraints extension" is a
positional fact and is accurate.

**Horn two (multiple comparisons) does not bite either, and the reason is
important enough to state as a general rule for this campaign.** The
multiple-comparisons hazard that `maximum_runs: 1` exists to prevent is a
*data-dependent stopping rule*: re-running until the environment "cooperates" is
only a garden of forking paths if cooperation is judged against observed
outcomes. A G-0c defer reveals `n_sweep_points_attempted/succeeded/failed =
0/0/0` and no `delta_E` value of any kind, so a re-dispatch decision conditioned
**solely on host identity** — a property of the machine, evaluated before any
measurement — is epistemically free. `maximum_runs: 1` binds the number of
*measurement* attempts under one frozen contract; it does not, and should not,
bind the number of times an environment precondition may be checked.

**The genuine exposure, which neither horn names and which the package does not
address, is this.** The pre-execution verification exercise — correctly disclosed
under AGENTS.md's record-never-discard rule, correctly fenced from citation, and
which I will not use as a measurement of `RUN-SSIQ-a85692-k` — nonetheless
**revealed outcome-relevant quantities about the candidate execution host to the
campaign**. Its own `standalone_gate_results_if_g0c_had_not_fired` block records
that on this host the gate would have reached `G-3 (load_confounded=false)` and
that the load-adjusted predicted count at both b = 1.10 s and b = 1.45 s would be
194. The "no data seen" property that makes a re-dispatch free is therefore
**intact for `delta_E` and compromised for design choices**: any successor
amendment that selects a host, a budget list, or a threshold is now being
authored by a campaign that knows what the instrument would have said on the
host it can actually reach. That is the quantifier-order failure of
`docs/inventor-protocol.md` §8.2 — a witness chosen after seeing the instance —
arriving through a side channel that the "never cite as a measurement" boundary
does not close, because the boundary governs citation and the hazard is
authorship.

The remedy is not suppression, which would be worse and which AGENTS.md forbids.
The remedy is to pre-register the *rule* by which a successor's budgets and
thresholds are derived, before the successor is drafted, so that the derivation
is checkable independently of what is now known. See the forward recommendation.

**On the contract's own defer accounting, the batch came up short.**
`contribution_accounting_v11` states, in frozen text: "IF THE GATE DEFERS, the
run still yields items (3) and the calibration measurements for roughly 140 s,
which is also worth having and must be recorded as an infrastructure outcome."
Two yields were pre-registered for a defer. Item (3) — the execution host's
platform, ISA, Python build, CPU count and load averages — landed and is real and
is genuinely new to this lineage. The calibration measurements did **not** land:
`cal1_records = []`, `cal2_records = []`. The dispatching handoff's own completion
gate expected them, in terms: "If deferring: the specific gate branch that fired,
the measured values that triggered it, **and the ~140 s calibration cost** reported
as the complete, successful outcome of this task." I record this without
adjudicating the CAL-1/CAL-2 ordering ambiguity, which is the Validator's
assignment. My point is about the *accounting*, and it is narrower and firmer
than the ordering question: **whichever reading is correct, the batch delivered
one of the two yields its own frozen contract pre-registered for a defer, and
neither `DEC-20260810-616fd5` nor the shard notices this.** Calling that outcome
"the frozen contract's own designed, successful behaviour" without qualification
overstates it by exactly one pre-registered item.

A second-order consequence deserves recording: the Coordinator's rationale
defends the Executor's ordering reading partly on the ground that it matches
"TASK-20260808-d458a3's own stated evaluation order". The same handoff's
completion gate expects the ~140 s calibration cost on a defer. The dispatching
handoff supports **both** readings in different clauses, so citing it as support
for one is selective. This is not a finding against the Executor, which disclosed
the ambiguity rather than guessing silently; it is a finding about the strength
of one of the three grounds the adjudication rests on.

---

## RC-2 — Does the ~2×-faster-host finding force a re-derivation of the margin, or merely a host match?

**Outcome: CHALLENGE SUSTAINED. Host identity is the wrong gate for the property
actually required, forward branch (A) is inadequate as stated, and the run
already computes the number that would close the gap.**

I reasoned about the pre-execution CAL-1 figures as RC-2 asks, and every use below
carries the boundary: **they are not measurements of `RUN-SSIQ-a85692-k`, which
recorded `cal1_records = []` and `cal2_records = []`, and they must never be
cited as such.** The structural argument below does not depend on them; they only
establish that the scenario is live rather than hypothetical.

**The structural finding, from the frozen text alone.** I read
`load_defer_gate_v11` in full (spec lines 1840–1986) and enumerated the direction
of every branch:

| branch | fires when | direction |
|---|---|---|
| G-0c | OS family / ISA / CPU count differ from RUN-h's archive | identity only |
| G-0 | any of 8 CAL-1 vertices times out at 15.0 s | slow only |
| G-0b | any of 8 CAL-2 source builds times out at 2.0 s | slow only |
| G-1 | `F_cal >= 1.45` | slow only |
| G-2 | `F_cal > 1.32242279052734375` | slow only |
| G-2b | LAC **at b = 1.45 s** below 58 | slow only |
| G-3 | otherwise | proceed clean |

**There is no lower bound on `F_cal` anywhere in the gate.** Every branch except
G-0c instruments *same-host contention*, which inflates wall times; the frozen
text says so itself, distinguishing "SAME-HOST CONTENTION ... the mechanism CAL-1,
F_cal and G-0/G-1/G-2/G-2b instrument" from "CROSS-HOST DIFFERENCE ... the
mechanism G-0c now instruments" (spec lines 718–726). So the entire defence
against a *faster* host is G-0c, and G-0c tests identity, not speed. It compares
the platform-string prefix `Linux`, `platform.machine() == "x86_64"`, and
`os.cpu_count() == 4`, and it explicitly declines to defer on kernel or glibc
differences: "A DIFFERING KERNEL PATCH LEVEL OR glibc MINOR VERSION ALONE IS NOT
A MISMATCH and does not defer."

**Consequence, computed directly from RUN-h's committed records.** The b = 1.10 s
arm's "guaranteed truncated" control is the statement that zero of 194 vertices
complete naturally at b = 1.10 s. I recomputed the reference from
`probe_delta_e_comparison.json`: 194 records, all `resolved`, none `timed_out`,
minimum `wall_seconds` `1.149932861328125`, count below 1.10 s = **0**, count below
1.45 s = **115**. The control therefore breaks as soon as the execution host is
faster than the archived host by **4.34 %** (`1.10 / 1.149932861328125 =
0.956578`), which is the 49.93 ms margin restated as a ratio. A newer
Linux/x86_64/4-vCPU instance — a different CPU generation, a different Python
build, an idle machine rather than a contended one — clears 4.34 % routinely, and
passes G-0c without a murmur.

**And the failure is worse than silent: the reading rules actively misroute it.**
At b = 1.10 s the reference is 0, so any measured natural completion is read under
P-3. P-3d, the cheapest explanation, explicitly does **not** cover it: "At
b = 1.10 s the corresponding statement is that any measured natural completion at
all implies a slack above 49.93 ms, which would be a genuinely surprising
instrument result and is NOT covered by P-3d." The next branch is P-3a ("RUN-h
itself ran under unrecorded contention"), then P-3b (cross-host difference), then
P-3c (a premise is falsified). And the frozen ordering note says: **"If G-0c
reports an exact host match, P-3a before P-3b is right."** So a matched-identity,
faster host produces a broken control and then has that break explained *first*
by RUN-h contention — an explanation that **cannot be checked in either
direction**, because, as the spec itself states, "RUN-h's side DOES NOT EXIST" (no
run in this lineage ever logged a load average). P-3c, the branch that "must be
surfaced loudly", fires only "IF P-3d, P-3a AND P-3b ARE ALL EXCLUDED", and P-3a
is unexcludable by construction. Identity-matching therefore makes the
misattribution *more* likely, not less.

**So: would a "matched" host pass G-0c and then silently invalidate the control?
Yes.** And the Coordinator's forward branch (A) — "obtain a MATCHED execution host
... and re-dispatch the frozen contract unchanged" — is precisely that scenario,
because the matched host will be a freshly provisioned sandbox rather than the
physical machine that produced RUN-h in early August 2026, and its per-core speed
is unknown, unmeasured, and untested by any branch of the gate. RC-2's
hypothesis is confirmed: **the correct remedy is a re-derived margin or a
speed-calibrated gate, and branch (A) alone is inadequate.**

**The cheapest fix costs no new host, no re-baseline, and no new measurement,
because the run already computes the discriminating number.** G-2b's own text
requires: "Report LAC for BOTH sweep budgets in `truncation_sweep_comparison.json`
and `execution_report.yaml`. IF LAC AT b = 1.45 s IS BELOW 58, set
`load_confounded: true`". The artifact duly carries
`load_adjusted_predicted_counts` keyed `"1.1"` and `"1.45"` — and **no branch of
the gate ever reads the `"1.1"` entry.** The load-adjusted predicted count at
b = 1.10 s is, by construction, the instrument's own prediction of the quantity the
b = 1.10 s control pre-registers at exactly 0. A single added comparison —
*defer if LAC at b = 1.10 s exceeds 0* — converts the control from an unchecked
premise into a measured one, using a number the frozen contract already requires
to be computed and reported. That is the cheapest discriminating control available
and I recommend it over every other option in this report.

A second, even simpler test is available as a cross-check and has an exact
justification: `F_cal` is defined as the minimum measured CAL-1 wall time, and
`A = 1.149932861328125` is attained by `[749, 1684]`, which **is** a member of the
calibration set — so `F_cal` is the measured analogue of exactly the archived
floor. **`F_cal < 1.10` is precisely the negation of the b = 1.10 s control at the
calibration set**, and is a one-line lower bound in the same units as the existing
G-1/G-2 thresholds. Its limitation, stated so it is not oversold: `F_cal` ranges
over 8 vertices, not 194, and I recomputed that the 8th and 9th smallest archived
times are `1.314665` and `1.317644`, only 2.98 ms apart — so under vertex-dependent
(non-uniform) speedup the bottom of the distribution can reorder and `F_cal` is
exactly necessary but only rank-preservingly sufficient. LAC at b = 1.10 s, which
scales all 194 archived times, does not have that limitation. Use LAC; keep
`F_cal < 1.10` as the cheap redundant check.

**What the Coordinator got right, stated because symmetry demands it.** Reading
the ~2× observation as vindication of G-0c is correct as far as it goes: the gate
did not fire on a bureaucratic technicality, and on the specific host in question
the observation (non-official, not RUN-k's data) is that the sweep would have
proceeded to `G-3 PROCEED, CLEAN` with LAC = 194 in an arm pre-registered at 0.
The error is not in that reading; it is in concluding that host *matching* is
therefore the remedy.

---

## RC-3 — Would re-baselining the reference strand the archived comparisons runs -a..-j rest on?

**Outcome: NO PRIOR CONCLUSION IS STRANDED, and the reasoning matters as much as
the answer. But THREE NAMED prior conclusions cite a host-specific constant as
though it were an instrument constant, and each needs a re-derivation footnote —
all three are rescuable from already-committed data at zero compute and with no
re-run. I verified the rescue for the load-bearing one by direct computation.**

**Why nothing is stranded.** Re-baselining under branch (B) *adds* a reference; it
does not delete one. `RUN-SSIQ-a85692-h` is immutable, its artifacts are committed,
and every existing record that compares against it continues to name a referent
that exists and can be read. The receipt's own `write_scope_respected` check —
which I re-verified with `git show --stat 5471247e6`: exactly ten files, all newly
added, no prior run touched — is the property that guarantees this. A record whose
comparison basis is a committed artifact cannot be invalidated by the later
creation of a second committed artifact. The failure mode RC-3 fears is real in
general but is not this one.

**The failure mode that IS created by branch (B), and that the decision does not
name.** Re-baselining converts four archived quantities from *campaign constants*
into *host-indexed constants*:

- `1.149932861328125` — the natural-completion floor `A`, and with it the 49.93 ms
  margin and G-1/G-2's thresholds;
- `1.6985499858856201` — the archived maximum, which underwrites the completeness
  margin;
- `1.3924050331115723` — the minimum over the `delta_E >= 5` subset;
- the counts `0 / 115 / 133 / 186 / 194` and the derived boundary `58`.

After a re-baseline there are **two** floors in the corpus and every future record
that writes "the natural-completion floor" without an index is ambiguous. This is
not stranding, it is **silent cross-referencing**, and it is cheap to prevent: any
re-baselined artifact must carry `reference_run_id` and the reference host's
platform/ISA/CPU-count beside every derived constant, and the constants above must
never again be written unindexed. Note that RUN-j's and RUN-k's artifacts already
share the filename `truncation_sweep_comparison.json` with identical field names
and different implicit host bases; a v12 file would be the third.

**The three named prior conclusions that cite a host-specific constant.**

**(1) `EV-SSIQ-48d274` (BATCH-013, `RUN-SSIQ-a85692-j`) — the campaign's strongest
single claim, `proof_status: derivation`.** Two of its clauses cite RUN-h's floor:
observation O-4 ("both sub-populations FULLY CONVERGED to their correct values by
b=1.0, strictly below the 1.14993s natural-completion floor") and, load-bearingly,
the boundary that protects O-7's orthogonality to BATCH-011: "that conclusion rests
entirely on search completeness, which this run never provides at any sweep point
(all three budgets remain strictly below the 1.14993s natural-completion floor)."
Under a re-baselined reference on a host ~2× faster the floor would be ≈ 0.52 s and
budgets of 0.6/0.8/1.0 s would all sit **above** it, so the sentence as written
would become false against the new reference.

**This one is rescuable at zero cost, and I verified the rescue rather than
asserting it.** RUN-j's own `truncation_sweep_comparison.json` records per-vertex
`timed_out` flags. I recomputed them directly:

| b | resolved | timed_out | resolved **and not** timed_out |
|---|---|---|---|
| 0.6 | 25 | 194 | **0** |
| 0.8 | 106 | 194 | **0** |
| 1.0 | 187 | 194 | **0** |

The claim "this run never provides completeness at any sweep point" is therefore a
**direct observation in RUN-j's own artifact** — 194/194 timed out at every budget,
zero naturally completed — and does not require RUN-h's floor at all. The floor was
used as a convenient predictor of something RUN-j directly measured. Re-derive the
boundary from RUN-j's own `timed_out` flags and it becomes host-independent
permanently. Cost: one recomputation, already performed here. No re-run.
`O-3`'s named premise ("a larger declared budget permits at least as many completed
iterations **on the same hardware**") is within-run and single-host and is untouched
by any re-baseline.

**(2) `EV-SSIQ-c3df82` O-2 (BATCH-012, `RUN-SSIQ-a85692-i`).** Its explanation of
why only 8/194 vertices resolved at b = 0.5 s is traced to "RUN-h's own
already-committed per_vertex_records: the MINIMUM full, non-truncated two-sided
completion time across all 194 vertices" — i.e. to `1.1499...` as an absolute
second value. For RUN-i itself the explanation stands unconditionally (RUN-i ran on
the same Linux/x86_64/4-CPU family). What a re-baseline retires is the *transfer*
of that constant as an explanation for any future run. Rescue: index the constant
to RUN-h in any citation. No re-run.

**(3) `EV-SSIQ-69ba8b` O-4 (BATCH-011, `RUN-SSIQ-a85692-h`) — PF-6's RNG-sharing
channel closed for p = 2437 by a scale-bound determinism argument.** Its premise is
search completeness, which its own boundary certifies "via per-vertex timing (max
1.70s of 15.0s)". That is a wall-clock premise. It is not stranded — RUN-h's own
completion is a fact about RUN-h — but it becomes a **per-host obligation** for any
successor: I recomputed the margin as `15.0 / 1.6985499858856201 = 8.831`, so the
argument tolerates a host up to ~8.8× slower before completeness fails. That is a
wide margin and it is why RUN-h's *value map* (as opposed to its *timings*) is
robust: on any host within 8.8× of the archived one, the archived `delta_E` values
are the true minimal values and remain the correct comparison basis. **This is the
single most important fact for branch (B):** re-baselining changes which *timings*
are canonical; it does not change which *values* are canonical, so every
value-comparison conclusion in the corpus — `EV-SSIQ-48d274` O-2/O-3/O-4/O-6,
`EV-SSIQ-c3df82` O-3/O-4, `EV-SSIQ-69ba8b` O-2/O-4/O-5 — survives untouched.

**Explicit statement of what is NOT at risk, so this finding is not read as wider
than it is.** No conclusion about `delta_E` values, no histogram, no conjugate-pair
correction, no equality cross-check, no null-control label, and no
`hypothesis_status` anywhere in this corpus depends on RUN-h's wall-clock timings.
The exposure is confined to the four constants listed above and the three citation
sites named. **No prior conclusion needs to be re-run, withdrawn, or re-graded, and
I recommend none.** RC-3's fear is not realized — but the citation discipline it
implies was not anticipated by `DEC-20260810-616fd5` and should be recorded before
anyone chooses branch (B), which is exactly what the card asked me to determine.

---

## RC-4 — Is the "designed successful behaviour" framing self-serving?

**Outcome: the narrow claim is TRUE and is supported by things other than the
contract's self-description. But the framing is INCOMPLETE, and the different
finding RC-4 anticipates is supported and belongs on the record.**

**First, the symmetric half, because it is owed.** The claim "the gate fired
correctly" does **not** rest only on the contract describing itself. Four
independent supports, three of which I verified myself in this session:

1. RUN-h's archived `environment.json` genuinely records
   `Linux-6.18.5-fc-v18-x86_64-with-glibc2.39` and `cpus_available: 4` — read
   directly by me, not taken from the execution report.
2. The frozen gate text mandates a defer on that comparison — read in full by me
   (spec lines 1859–1878).
3. `git show --stat 5471247e6` confirms RUN-h's directory was untouched by the
   producer commit, so the reference read was the reference as archived.
4. The gate's judgement was substantively, not merely formally, right: I
   recomputed from RUN-h's own records that exactly **0** of 194 vertices complete
   below 1.10 s, so the b = 1.10 s control is a genuine pre-registered null that a
   4.34 % speedup destroys. (The non-official pre-execution exercise's ratio range
   `[0.4308, 0.4703]` — **not** a measurement of `RUN-SSIQ-a85692-k`, which recorded
   `cal1_records = []` — indicates the live host is far outside that tolerance.)

So the defer was correct behaviour and I do not challenge `completed_valid`.

**Second, the incompleteness, which is the actual finding.** The frozen contract
did not merely describe a defer as successful. It pre-registered a **decision rule
about whether to dispatch at all**, in `contribution_accounting_v11`, in the frozen
text, under the heading "WHAT WOULD MAKE THIS AMENDMENT NOT WORTH RUNNING, STATED
IN ADVANCE":

> if a round-4 verification finds that G-0c cannot be satisfied — i.e. that the
> execution host is known in advance not to match the archived one — then item (1)
> is unreadable by construction and **the correct action is to NOT dispatch this
> amendment** and to open a successor that re-establishes an archived reference on
> the actual execution host first. That is a legitimate outcome and is recorded
> here so it can be chosen **without renegotiating the contract after the fact**.

That rule names round-4 verification as the place it is applied. I read the
`round4_verification_plan` and the `round4_verdict` (spec lines 1334–1411) and the
`self_verification` block of `DEC-20260808-c2a470`. Items (a)–(g) check that G-0c
is correctly **ordered** (item d), that thresholds read correctly, that density
figures reproduce, and that the budget arithmetic holds. **No item asks whether
G-0c can be satisfied on the host that would execute.** The one check the frozen
contract itself named as decisive for dispatch is the one check the pre-dispatch
verification does not contain.

**Was the answer available?** The Coordinator's own correction record,
`COORD-CORRECTION-PF26-execution-host.md`, dated 2026-08-07 — the freeze date —
states in the Coordinator's own words: "They are about the *orchestration* host —
the arm64 Darwin machine this Coordinator session runs on", and reports load
figures "19.45 / 24.15 / 33.78 against **14 arm64 Darwin cores**". `RUN-SSIQ-a85692-k`
then executed on `macOS-26.6-arm64-arm-64bit-Mach-O`, `arm64`, `os.cpu_count() = 14`,
recording a 1-minute load average of `33.6787109375`. The platform, ISA and core
count match that description exactly, and the load reading sits beside the
correction record's own third figure. Load averages are not identifiers and I do
not treat this as proof; the platform/ISA/core-count triple is what carries the
weight, and it is decisive enough. The Coordinator had already run `sysctl -n
hw.ncpu` and `uptime` in that environment, so the cost of the check the contract
named was one command in a shell it had demonstrably used.

**Therefore the different finding RC-4 anticipates is supported, and I state it in
the form the record should carry:** *the contract predicted its own blocker, named
in advance the action to take if the blocker was foreseeable, and the pre-dispatch
verification did not include that check — so the batch spent a dispatch to
discover, by measurement, a condition its own frozen text had already told it how
to discover by inspection.* That is a real and different finding from "the gate
worked as designed", and it is the same defect class as PF-26 itself, whose lesson
the Coordinator wrote down in that very correction record: "The check that would
have caught it cost one file read."

Two limits on this finding, stated so it is not over-read. **(i)** It is not a
finding against the Executor, which executed the frozen contract exactly and
disclosed everything. **(ii)** It is not certain the Coordinator could have known
where the Executor would land: runs -a..-j demonstrably executed on a Linux
sandbox, so a belief that this run would too was not unreasonable. The finding
does not require certainty. It requires only that the contract named a check, the
checklist omitted it, and the means to perform it were at hand — all three of
which are established from committed text.

`DEC-20260810-616fd5`'s `next_actions` currently cites `contribution_accounting_v11`
item (3) as showing "the contract predicted its own blocker and the blocker
arrived; that is the gate working, not the plan failing." The same block, twenty
lines further on, contains the do-not-dispatch rule. Citing one and not the other
is the selective-citation pattern RC-4 was written to test for, and it is present.

---

## RC-5 — The archival process deviation, attacked harder

**Outcome: ACCEPTABLE-WITH-CONDITIONS for this package. The deviation is real and
correctly named, "content-verified" is doing genuine work here rather than
relabelling a skipped step, and the specific defect class the ordering cannot catch
is narrower than the framing invites — I identified it, tested for it, and this
package is clean of it.**

**What content hashing after the producer commit genuinely certifies, verified
independently.** I recomputed all ten `sha256` values from the working tree: all
ten match the receipt exactly. `git diff --stat 5471247e6` over the declared paths
is empty. `git log --all --oneline` over the run directory and over the
implementation module each return **exactly one** commit, `5471247e6`; there is no
superseded or amended earlier version of either in any ref. `git log
a58be638..5471247e6` returns exactly one commit, so nothing entered history between
the freeze of `specification_v11.yaml` and the landing of the package. The receipt's
observation that `parent_sha` **is** the freeze commit is load-bearing and correct,
and it is a stronger binding than `code_commit_binding` alone.

**The defect class the ordering cannot catch, named precisely.** It is not
post-hoc tailoring of artifacts to reviewer objections — the freeze at `5471247e6`
is *earlier* than a Coordinator snapshot would have been, and both review handoffs
are on record as pending and undispatched, so the "no reviewer has read it"
property holds and is checkable. It is not selective disclosure of multiple runs
either, in the sense of committing one of several: that hazard is identical under
both orderings, because in both cases the Coordinator sees only what the producer
wrote to the working tree, and an uncommitted discarded run is invisible to a
snapshot commit just as it is to a content hash. Asserting otherwise would
overstate what the correct ordering buys.

**What it genuinely loses is the provenance of the DECLARED PATH SET.** Under the
correct ordering the Coordinator derives the declared set from the contract's
`required_artifacts` list and a directory listing, then commits it. Here the
declared set was derived **from the producer's own commit**: the receipt says so —
"Exactly the ten files added by `5471247e6` (`git show --stat 5471247e6`)". A file
produced by the run but left uncommitted, or committed on a different branch, would
be absent from `git show --stat`, absent from the declared list, and therefore
absent from `git diff --stat` against the declared paths as well. **The verification
method is closed under the producer's own choice of what to commit.** That is the
defect class: an *undeclared sibling artifact*, invisible to a path list defined by
the thing it is meant to audit.

**I tested for it, and this package is clean.** `git status --porcelain` over
`experiments/` and `coordination/` is empty — no untracked or modified file
anywhere in the experiment tree. The run directory contains exactly nine files,
which are exactly `specification_v11.yaml`'s `required_artifacts` list (spec lines
2088–2097), plus the one new implementation module the contract's
`required_artifacts_note` requires: ten, matching the declared set with no residue
in either direction. So the loss is a loss of *guarantee*, not of *fact*, for this
package.

**Condition for acceptance, which is the cheap general repair.** Future receipts
taken after a producer commit must derive `declared_paths` from the frozen
contract's `required_artifacts` list **and** a filesystem listing of the run
directory, then verify that set against `git show --stat` — rather than deriving
the set from the commit and verifying it against itself. That inverts the
dependency and closes the class at no cost. I recommend it as a standing
correction, not as a condition on this package's admissibility.

**"Content-verified" is not a relabelling here.** It is doing real work: ten
independently recomputed hashes, a clean tree diff, a single-commit history, and a
parent that is the freeze commit. The receipt's `what_is_genuinely_lost` block
states the loss accurately and does not soften it, including the explicit
concession that "precommit" is a misnomer for this batch. I found nothing in the
deviation block that overstates what survives.

---

## RC-6 — Is the unenforced 2 GiB memory cap being waved through?

**Outcome: PARTIALLY. The dismissal is correct for this run and the disclosure is
exemplary, but the two questions RC-6 actually asks are not answered anywhere in
the package, and one of them has a consequential answer that bears directly on the
forward branch.**

**Question 1 — would any future execution of this contract, on any plausible host,
run unbounded in memory?** The answer is host-conditional and the package does not
state it. `ulimit -v 2097152` is the mechanism runs -a..-j used (I confirmed it in
`RUN-SSIQ-a85692-j/command.txt` line 28) and it works on Linux. So under **forward
branch (A)** — a matched Linux/x86_64/4-CPU host — the cap is enforced and the gap
closes automatically. Under **forward branch (B)** — re-baselining onto the host
that is actually available, which is Darwin/arm64 — `setrlimit` rejects `RLIMIT_AS`
and the cap is **not** enforced, so every future run under that branch is unbounded
in memory with `timeout 1000` as the only binding cap. **The enforcement gap is
therefore not a dormant issue: it is a specific, unremediated cost of branch (B)
that `DEC-20260810-616fd5`'s branch comparison does not price.** The portable
replacement is cheap and standard — `resource.setrlimit(RLIMIT_DATA, ...)` or an
in-process `tracemalloc`/`ru_maxrss` sampler that aborts on breach — and a v12
amendment choosing branch (B) must specify one, or must honestly restate its
`budget.maximum_memory_gb` as unenforced.

**Question 2 — can the frozen contract honestly be described as budget-enforced on
a non-Linux host?** No. On a non-Linux host only `wall_clock_seconds_per_run` is
enforced. `maximum_memory_gb: 2` is, on such a host, a declared intention with no
mechanism. The receipt and the decision both say this plainly and I record that
they do; what neither says is that the *contract* — as opposed to *this run* —
therefore carries a platform-conditional budget, which is a property of the frozen
document that a later reader will not infer.

**A third fact, which I checked and which neither the Coordinator nor the Executor
states.** I searched every run directory in this experiment for any recorded peak
memory (`peak_memory`, `max_rss`, `maxrss`): **there is none, in any run, -a
through -k.** The 2 GiB bound has only ever been a tripwire that never tripped, not
a measurement. So the campaign's actual epistemic position on memory is: "no run
under this contract has ever exceeded 2 GiB on Linux, and no run has ever measured
how close it came." That is weak but not empty evidence, and it is the honest
statement. The Coordinator's `budget_compliance` check is careful here — "No figure
for peak memory was measured and none is asserted" — and I endorse that wording. My
objection is not that a figure was fabricated; it is that the enforcement gap was
priced at zero for the future when it is priced at zero only for the past and only
on one of the two forward branches.

**On the "immaterial for a 0.19 s run" reasoning specifically:** it is true, and
RC-6's suspicion of it is well-placed but resolves in the campaign's favour here,
because the Executor did **not** absorb it silently — it was classified as
`infrastructure_error`, disclosed in `command.txt`, `environment.json`, the
execution report, the receipt, the decision, and the shard, and explicitly handed to
the reviewers rather than adjudicated away. That is the opposite of waving through.
What is missing is the forward analysis, not the disclosure.

---

## Forward-branch recommendation

The decision frames the choice as binary — (A) matched host, unchanged contract, or
(B) versioned amendment re-baselining the reference. **Per RC-2, (A) does not fix
the defect this batch exposed, and per RC-6, (B) carries an unpriced memory
enforcement gap.** I recommend a third option, which is strictly cheaper than (B),
strictly safer than (A), and which uses only quantities the frozen contract already
computes.

**Recommended: (C) — a v12 amendment that makes the gate two-sided, before any
host question is settled.**

1. **Add a lower-bound branch to `load_defer_gate_v11`: defer if the
   load-adjusted predicted count at b = 1.10 s exceeds 0.** The LAC at b = 1.10 s is
   already required, already computed, already reported, and already present in the
   artifact — no branch reads it. It is the instrument's own prediction of the exact
   quantity the b = 1.10 s control pre-registers at 0. Keep `F_cal < 1.10` as a
   redundant cheap check with its stated 8-vertex limitation.
2. **Do this before choosing (A) or (B), not after.** With a two-sided gate, branch
   (A) becomes safe (a matched-but-faster host defers instead of silently breaking
   the control) and branch (B) becomes optional rather than forced.
3. **If (B) is nonetheless chosen, pre-register the derivation rule before drafting
   the numbers** — per RC-1, the campaign now knows what the instrument would have
   said on the reachable host, so budgets and thresholds must be derived by a rule
   stated in advance. The natural rule, which also dissolves the 49.93 ms problem
   permanently: **express sweep budgets as fixed multiples of the new reference
   host's own measured floor** rather than as absolute seconds. The design question
   ("does convergence change as budget crosses the natural-completion floor") is
   intrinsically floor-relative; the margin then becomes a fixed fraction rather
   than a fixed 49.93 ms, and host speed drops out of the control entirely.
4. **If (B) is chosen, specify a portable memory cap or restate the budget as
   unenforced** (RC-6), and **index every re-derived constant to its reference run**
   (RC-3).

**Cost.** (C) item 1 is a few lines of gate logic plus one pre-freeze round on the
amendment text; no compute. (B), if taken, needs one complete 194-vertex probe on
the new host — RUN-h's own total was 278.49618768692017 s wall on the archived
host — plus re-derivation of roughly ten interlocked frozen literals (`A`, the
49.93 ms margin, G-1's 1.45, G-2's 1.32242279052734375, G-2b's 58 = 0.5 × 115, the
0/115/133/186/194 counts, the 8-vertex calibration set by coordinate) and the
pre-freeze review chain that re-verifies their coupling. The compute is small; the
review chain is the real cost, and `DEC-20260810-616fd5` is right that (B) is "more
expensive than it looks" — though for the reason that its constants are interlocked,
not primarily because they are numerous.

**Risk to existing records.** (C) item 1: **none** — it adds a defer branch and
changes no archived value. (B): **no prior conclusion is invalidated** (RC-3), but
it creates the two-floor ambiguity, which items 3–4 above are designed to prevent.
(A) alone: the risk is spending the campaign's next run to produce a b = 1.10 s
control that may be broken and a P-3 reading that would misattribute it to
unfalsifiable RUN-h contention — precisely the "a number nobody could read" outcome
`contribution_accounting_v11` says makes the amendment not worth running.

---

## Scope limits of this review

- **No claim is asserted, in either direction, about `delta_E`, `delta_E`
  convergence, `n_naturally_completed` at any budget, the final-pop overshoot
  distribution, `H-SSIQ-36e970`, lever `L4`, or the `p^{1/3+o(1)}` exponent budget.**
  `RUN-SSIQ-a85692-k` measured none of them (`n_sweep_points_attempted/succeeded/
  failed = 0/0/0`) and this review measures none of them. Every recomputation
  above is over *previously committed* artifacts (RUN-h, RUN-j) and is used only to
  test the standing of comparisons, never to license a new mathematical statement.
- **The G-0c defer is an infrastructure outcome and is never negative mathematical
  evidence.** I attacked how that principle is being applied to the accounting and
  the forward plan; I did not convert the absence of a measurement into a claim.
- **The pre-execution CAL-1 figures are not measurements of `RUN-SSIQ-a85692-k`**
  (`cal1_records = []`, `cal2_records = []`) and are not cited as such anywhere
  above; they are reasoned *about* in RC-1/RC-2/RC-4 and every use carries the
  boundary. RC-2's structural finding does not depend on them.
- **The CAL-1/CAL-2 ordering ambiguity is not adjudicated here.** It is the
  Validator's assignment (`TASK-20260810-098fad`). RC-1's finding about the
  half-delivered defer yield holds under **either** reading and does not presuppose
  one.
- **No Pollard-rho / BSGS / specialized-baseline comparison applies.** This batch
  makes no algorithmic claim, so there is no cost curve to place on a frontier and
  I fabricate none. The applicable baseline discipline is the null-object one, and
  it is stated in the next bullet.
- **Null-object framing for this batch's one durable yield.** The claimed yield is
  "a pre-registered host-identity gate that demonstrably fires". The parameter that
  should destroy that signal is *host similarity*: as the execution host becomes
  more similar to the archived one along the three compared dimensions while
  remaining faster, the gate's detection rate must fall to zero while the control's
  invalidity persists. `RUN-SSIQ-a85692-k` exercised exactly one cell of that
  matrix — maximal mismatch, true positive. The matched-and-comparable cell (should
  proceed) has never been exercised officially, and the matched-but-faster cell
  (should defer, will proceed) is the demonstrable **false negative** of RC-2. Any
  `EV-*` or `KN-FIND` drafted from this batch must say that the gate is validated on
  one cell of four, not that it is validated.
- **Session-independent, not model-independent.** This review does not upgrade the
  campaign's evidence tier and does not satisfy or advance any closure quorum.
- Nothing here closes, opens, or re-grades a hypothesis, and nothing here is a
  ledger record. Handing to the Coordinator's ledger archive task
  `TASK-20260811-fbf1bf`.

---

```yaml
red_team_report:
  id: RT-BATCH-014
  task_id: TASK-20260810-971cfa
  goal_id: GOAL-SSIQ-001
  batch_id: BATCH-014
  verdict: CHALLENGE-narrow
  reviewed_snapshot:
    commit: 5471247e6
    parent: a58be63848492aa45c75b8d2d6973a352166de96
    verification_basis: content_verified_via_declared_path_sha256
    archive_receipt: coordination/goals/GOAL-SSIQ-001/batches/BATCH-014/archives/TASK-20260810-dae7ef-receipt.yaml
    independently_reverified_this_session:
      - 10/10 declared path_sha256 recomputed and matched
      - "`git diff --stat 5471247e6` over declared paths: empty"
      - "`git log --all -- runs/RUN-SSIQ-a85692-k`: exactly one commit (5471247e6)"
      - "`git log a58be638..5471247e6`: exactly one commit (no intervening state)"
      - "`git status --porcelain experiments/ coordination/`: clean"
      - declared set == specification_v11 required_artifacts (9) + 1 new module
  claim_under_review: >-
    That RUN-SSIQ-a85692-k, which consumed 0.1884760856628418 s of a 1000 s
    budget, performed one 203-vertex graph build, deferred at gate G-0c and
    produced n_sweep_points_attempted/succeeded/failed = 0/0/0, is correctly
    recorded as a fully successful execution of frozen contract
    specification_v11.yaml; that the archival process deviation
    PD-ARCH-BATCH-014-producer-committed preserves the snapshot-before-review
    integrity property; and that the forward choice is the binary (A) matched
    host / (B) re-baselined reference named in DEC-20260810-616fd5.
  objections:
    - "OBJ-1 (RC-4, primary): specification_v11.yaml's own contribution_accounting_v11 pre-registers a DO-NOT-DISPATCH rule -- 'if a round-4 verification finds that G-0c cannot be satisfied ... the correct action is to NOT dispatch this amendment' -- and names round-4 verification as where it is applied. Items (a)-(g) of round4_verification_plan and of DEC-20260808-c2a470's self_verification check that G-0c is correctly ORDERED (item d) but never ask whether G-0c CAN BE SATISFIED on the executing host. The Coordinator's own COORD-CORRECTION-PF26-execution-host.md, dated the freeze date, records the orchestration host as '14 arm64 Darwin cores'; RUN-k executed on macOS-26.6-arm64-arm-64bit-Mach-O / arm64 / os.cpu_count()=14. 'The gate worked as designed' is true and incomplete: the contract named the pre-dispatch check, the checklist omitted it, and the means to perform it (one shell command in an environment the Coordinator had already queried with sysctl/uptime) were at hand. Not a finding against the Executor."
    - "OBJ-2 (RC-2, primary): host IDENTITY is the wrong gate for the property required. I enumerated every branch of load_defer_gate_v11 from the frozen text: G-0 (CAL-1 timeout at 15.0 s), G-0b (CAL-2 timeout at 2.0 s), G-1 (F_cal >= 1.45), G-2 (F_cal > 1.32242279052734375), G-2b (LAC at b=1.45 below 58) are ALL one-sided against a SLOW host. No lower bound on F_cal exists anywhere. Recomputed from RUN-h's own per_vertex_records: min wall 1.149932861328125, count below 1.10 s = 0, so the b=1.10 s 'guaranteed truncated' control breaks at a 4.34% speedup (1.10/1.149932861328125 = 0.956578). A Linux/x86_64/4-CPU host that is merely newer passes G-0c (which explicitly does not defer on kernel or glibc differences), passes every load branch, reaches G-3 PROCEED CLEAN, and breaks the control. Forward branch (A) IS that scenario and is inadequate as stated."
    - "OBJ-3 (RC-2, aggravating): an exact identity match actively MISROUTES the failure. P-3d explicitly does not cover a natural completion at b=1.10 s; the frozen ordering note says 'If G-0c reports an exact host match, P-3a before P-3b is right', so the first explanation offered would be 'RUN-h itself ran under unrecorded contention' -- which the specification itself says cannot be checked because 'RUN-h's side DOES NOT EXIST' (no run in this lineage logged a load average). P-3c, the branch that 'must be surfaced loudly', fires only if P-3a is excluded, and P-3a is unexcludable by construction."
    - "OBJ-4 (RC-1): the contract's pre-registered defer yield was HALF DELIVERED and nothing in the package notices. contribution_accounting_v11: 'IF THE GATE DEFERS, the run still yields items (3) and the calibration measurements for roughly 140 s.' Item (3) landed. cal1_records = [] and cal2_records = []. TASK-20260808-d458a3's own completion gate expected 'the ~140s calibration cost' on a defer. Holds under EITHER side of the ordering ambiguity, which is not adjudicated here. Calling the outcome 'fully successful' without qualification overstates it by one pre-registered item."
    - "OBJ-5 (RC-1, forking path): the pre-execution exercise -- correctly disclosed, correctly fenced from citation -- nonetheless revealed to the campaign that on the reachable host the gate would reach G-3 clean with LAC = 194 at both budgets. The 'never cite as a measurement' boundary governs CITATION; the exposure is AUTHORSHIP. Any successor amendment now selects hosts, budgets and thresholds knowing what the instrument would have said (inventor-protocol 8.2, witness chosen after seeing the instance). Remedy is pre-registration of the derivation rule, never suppression."
    - "OBJ-6 (RC-6): the memory enforcement gap is priced at zero for the future when it is zero only for the past and only on ONE forward branch. Under (A) a Linux host restores `ulimit -v 2097152` automatically; under (B), re-baselining onto the reachable Darwin host, every future run is unbounded in memory with `timeout 1000` the only binding cap. DEC-20260810-616fd5's branch comparison does not price this. Separately: NO run in this experiment, -a through -k, records any peak-memory figure -- the 2 GiB bound has only ever been a never-tripped tripwire, never a measurement."
    - "OBJ-7 (RC-5, conditional and narrow): the receipt derives declared_paths FROM the producer's own commit (`git show --stat 5471247e6`), so the verification method is closed under the producer's choice of what to commit. The defect class it cannot catch is an UNDECLARED SIBLING ARTIFACT -- a run-produced file left uncommitted or committed elsewhere, invisible to both the declared list and the diff against it. I tested for it: `git status --porcelain` clean, run directory contains exactly the 9 required_artifacts plus the 1 required new module. This package is clean of the class; the loss is of guarantee, not of fact."
    - "OBJ-8 (RC-3, citation discipline): re-baselining strands NOTHING, but it converts four archived constants (1.149932861328125; 1.6985499858856201; 1.3924050331115723; the counts 0/115/133/186/194 and the derived 58) from campaign constants into host-indexed constants, after which any unindexed reference to 'the natural-completion floor' is ambiguous. RUN-j's and RUN-k's artifacts already share the filename truncation_sweep_comparison.json with identical field names and different implicit host bases."
    - "OBJ-9 (minor, RC-1): DEC-20260810-616fd5's rationale cites TASK-20260808-d458a3's stated evaluation order as one of three grounds supporting the Executor's CAL ordering reading, while the same handoff's completion gate expects the ~140 s calibration cost on a defer. The dispatching handoff supports both readings in different clauses; citing one is selective. Adjudication of the ambiguity itself belongs to TASK-20260810-098fad."
    - "OBJ-10 (null-object framing): the batch's one durable yield is 'a host-identity gate that demonstrably fires'. That is one cell of a four-cell matrix -- maximal-mismatch true positive. The matched-and-comparable cell has never been exercised officially and the matched-but-faster cell is a demonstrable FALSE NEGATIVE (OBJ-2). Any EV-* or KN-FIND drafted from this batch must say the gate is validated on one cell of four."
  no_objection_raised_on:
    - "Archive integrity: 10/10 hashes recomputed and matched; tree byte-identical to 5471247e6; single-commit history for the package; parent IS the freeze commit."
    - "The G-0c defer itself: the gate fired on archived data I read directly (RUN-h environment.json: Linux-6.18.5-fc-v18-x86_64-with-glibc2.39, cpus_available 4) and its judgement was substantively right (0 of 194 archived vertices complete below 1.10 s)."
    - "validity: completed_valid, outcome DEFERRED_AT_G0C, certificate.kind none, scale_qualifier 'toy; N = 203; single prime p=2437' -- all correct and none asserting above tier."
    - "Claim-boundary discipline: I found no instance anywhere in the package of the non-official CAL-1 figures being cited as RUN-k measurements, and lever_states records changed_this_batch: false for every lever without exception."
    - "Executor conduct throughout: three deviations disclosed rather than absorbed, including the one that most invited silent absorption (the ordering ambiguity)."
  required_controls:
    - "C-1 (cheapest discriminating control, recommended above all others): add a LOWER-BOUND branch to load_defer_gate_v11 -- defer if the load-adjusted predicted count at b = 1.10 s exceeds 0. G-2b already requires LAC to be computed and reported at BOTH budgets and the artifact already carries load_adjusted_predicted_counts keyed '1.1' and '1.45'; no branch reads the '1.1' entry. Cost: one comparison against a number the run already computes. Closes the matched-but-faster false negative without a new host, a re-baseline, or a new measurement."
    - "C-2 (redundant cheap cross-check): defer if F_cal < 1.10. F_cal is the measured analogue of A = 1.149932861328125, attained by [749, 1684], which IS in the calibration set, so F_cal < 1.10 is exactly the negation of the b=1.10 s control at the calibration set. Limitation to state: F_cal ranges over 8 vertices, not 194, and the 8th and 9th smallest archived times are 1.314665 and 1.317644 (2.98 ms apart), so under vertex-dependent speedup the bottom of the distribution can reorder. Necessary exactly; sufficient only under rank preservation. Use C-1 as primary."
    - "C-3 (RC-3 rescue, already performed here at zero cost): re-derive EV-SSIQ-48d274's boundary claim from RUN-j's OWN timed_out flags rather than from RUN-h's 1.14993 s floor. Recomputed this session from RUN-j's truncation_sweep_comparison.json: at b = 0.6/0.8/1.0 the counts are resolved 25/106/187, timed_out 194/194/194, and resolved-and-not-timed-out = 0/0/0. 'This run never provides completeness at any sweep point' is thus a DIRECT OBSERVATION in RUN-j's own artifact, host-independent permanently. No re-run required."
    - "C-4: index every re-derived timing constant to its reference run. Any re-baselined artifact must carry reference_run_id plus the reference host's platform / ISA / cpu count beside every derived constant, and the four constants in OBJ-8 must never again be written unindexed."
    - "C-5: if branch (B) is chosen, specify a portable memory cap (resource.setrlimit RLIMIT_DATA, or an in-process ru_maxrss/tracemalloc sampler that aborts on breach) or restate budget.maximum_memory_gb honestly as unenforced on non-Linux hosts."
    - "C-6 (standing archival correction, not a condition on this package): future receipts taken after a producer commit must derive declared_paths from the frozen contract's required_artifacts list AND a filesystem listing of the run directory, then verify that set against `git show --stat` -- inverting the dependency so the path list is not defined by the artifact it audits."
    - "C-7: pre-register the derivation RULE for any successor's budgets and thresholds before drafting its numbers (OBJ-5). Recommended rule: express sweep budgets as fixed multiples of the new reference host's measured floor rather than as absolute seconds, which makes the protective margin a fixed fraction instead of a fixed 49.93 ms and removes host speed from the control entirely."
  counterexample_or_mutation: >-
    THE MUTATION THAT BREAKS THE GATE WITHOUT TRIPPING IT: hold the three
    dimensions G-0c compares fixed (platform prefix Linux, machine x86_64,
    os.cpu_count() == 4) and vary only per-core speed upward by more than 4.34%
    -- a newer CPU generation, a newer Python build, or simply an idle machine
    instead of a contended one. G-0c passes by construction (it does not defer on
    kernel or glibc differences and measures no clock). G-0/G-0b/G-1/G-2/G-2b all
    pass, being one-sided against slowness. G-3 sets load_confounded: false. The
    b = 1.10 s arm, pre-registered at exactly 0 natural completions, returns a
    nonzero count; P-3d does not cover it; and the frozen ordering rule routes the
    explanation first to P-3a, which cannot be checked because RUN-h logged no
    load average. The run consumes its single maximum_runs slot and produces a
    number nobody can read -- exactly the outcome contribution_accounting_v11
    says makes the amendment not worth running. CHEAPEST CONTROL THAT
    DISTINGUISHES THIS FROM A GENUINE RESULT: control C-1, which is one
    comparison against a value the run already computes and already reports.
  baseline_comparison: >-
    NOT APPLICABLE AND NOT FABRICATED. BATCH-014 makes no algorithmic claim, has
    no cost curve, and produced no measurement, so there is no Pollard-rho, BSGS,
    or specialized baseline to compare against and no Pareto axis on which a
    dominated_by field could be non-null. The applicable baseline discipline is
    the null-object one and it is recorded as OBJ-10: the batch's only durable
    yield -- a host-identity gate that fires -- is validated on ONE cell of a
    four-cell matrix (maximal-mismatch true positive), with the
    matched-and-comparable cell never officially exercised and the
    matched-but-faster cell a demonstrable false negative. The parameter that
    should destroy the signal is host similarity: as the execution host becomes
    more similar along the three compared dimensions while remaining faster, the
    gate's detection rate must fall to zero while the control's invalidity
    persists. Measured at one extreme point only, gate firing and control
    invalidity are confounded.
  heuristic_challenges:
    - "Not the exemplar profile: BATCH-014 advances no exponent-first, heuristic-conditional claim, so the heuristic-inventory / random-model-transfer / hidden-overhead / reduction-instantiation battery of docs/target-result-profile.md does not apply and is not applied. One structurally analogous item DOES apply and is raised as OBJ-2: an unstated premise (execution host not faster than the archived host) was converted into a gate that tests a PROXY for the premise (host identity) rather than the premise itself, and the proxy has a null region in which the premise fails undetected. That is the same defect shape as a random-model justification that does not transfer to the structured object at hand."
  cost_model_challenges:
    - "The frozen defer-cost accounting and the realized defer cost differ by three orders of magnitude (~140 s pre-registered vs 0.1884760856628418 s realized) because the pre-registered figure assumes calibration ran. The Executor states this plainly and does NOT claim the ~140 s was incurred, which is correct. The cost-model consequence is OBJ-4: the ~140 s was not merely an estimate, it was the price of the second pre-registered defer yield, and not paying it meant not receiving it."
    - "Branch (B)'s cost is understated in one dimension and overstated in another. Compute is small: RUN-h's own total was 278.49618768692017 s wall, and the completeness margin is wide (15.0 / 1.6985499858856201 = 8.831), so a new reference run is cheap and robust. The real cost is the interlock: roughly ten frozen literals (A; the 49.93 ms margin; G-1's 1.45; G-2's 1.32242279052734375; G-2b's 58 = 0.5 x 115; the 0/115/133/186/194 counts; the 8-vertex calibration set by coordinate) must be re-derived consistently, plus the pre-freeze chain that re-verifies their coupling. DEC-20260810-616fd5's 'more expensive than it looks' is right, for a reason it does not name."
    - "budget.maximum_memory_gb is platform-conditional and the frozen contract does not say so (OBJ-6). On a non-Linux host only wall_clock_seconds_per_run is enforced."
  reduction_and_scope_challenges:
    - "No scope inflation found in the package. DEC-20260810-616fd5's limitations, the shard's claim_boundary, and the receipt's non_official_observation boundary each state the null result symmetrically -- explicitly noting that an environment gate firing before any computation is not a POSITIVE mathematical result either -- and knowledge_promotion is empty on two independently sufficient grounds. I checked specifically for the reverse failure (a negative-result closure smuggled in as a saturation claim) and found none: no lever is retired, L4 is explicitly not retired, and changed_this_batch is false for every lever."
    - "One scope statement to add before any EV-*: the gate's validation covers one cell of four (OBJ-10). A KN-FIND asserting that a host-identity gate 'catches a host substitution that would silently invalidate a timing-based control' would be broader than the evidence, since the substitution class it demonstrably does NOT catch is the one this report identifies."
  proof_architecture_challenges:
    - "Observation-fiber attack (successful): hold the observation G-0c makes -- the triple (OS family, ISA, cpu count) -- fixed, and vary the underlying object (the host). Two preimages sit on opposite sides of the conclusion: the archived 4-CPU x86_64 Linux sandbox (control valid) and a newer 4-vCPU x86_64 Linux instance more than 4.34% faster (control invalid). Both produce identical observations and identical gate verdicts. The missing separator is a measured speed bound; control C-1 supplies it from data the run already collects."
    - "Quantifier-order attack (flagged, not yet realized): the campaign now knows, from a disclosed non-official exercise, what the instrument would report on the reachable host. Any successor that chooses its host, budgets or thresholds after that knowledge is choosing a witness after seeing the instance. C-7 (pre-register the derivation rule) restores the correct order."
    - "Boundary/strictness attack (clean): the b=1.10 s arm is genuinely embedded as the stated boundary -- I recomputed count(archived wall < 1.10) = 0 from RUN-h's own 194 records, matching the frozen reference exactly. The boundary is correct; what is unprotected is its transfer to a different host."
  narrowest_supported_statement: >-
    On the package: RUN-SSIQ-a85692-k is a valid, complete execution of
    TASK-20260808-d458a3 under specification_v11.yaml; it evaluated
    load_defer_gate_v11 in the frozen order, deferred at G-0c on a genuine
    three-dimension mismatch against RUN-SSIQ-a85692-h's true archived
    environment.json, computed no delta_E value of any kind, and its ten declared
    artifacts are immutably frozen at 5471247e6 with all ten sha256 values
    independently recomputed and matched. The defer is an infrastructure outcome
    and is evidence for nothing and against nothing about delta_E,
    H-SSIQ-36e970, lever L4, or the p^{1/3+o(1)} exponent budget.
    On the accounting: the defer delivered ONE of the TWO yields the frozen
    contract pre-registered for a defer, and the contract's own pre-dispatch
    do-not-dispatch rule was neither on the round-4 checklist nor applied.
    On the forward plan: obtaining a matched host does not by itself protect the
    b = 1.10 s control, because every gate branch other than G-0c is one-sided
    against a slow host and G-0c measures identity, not speed.
    On the archived comparisons: re-baselining the reference strands no prior
    conclusion -- RUN-h is immutable and remains the referent of every record that
    cites it, and every value-based conclusion in the corpus is host-independent
    within an 8.831x completeness margin -- but four timing constants become
    host-indexed and three named records (EV-SSIQ-48d274, EV-SSIQ-c3df82,
    EV-SSIQ-69ba8b) need a re-derivation footnote, all three obtainable from
    already-committed data with no re-run.
  next_concrete_action: >-
    BEFORE choosing forward branch (A) or (B), draft a v12 amendment whose ONLY
    substantive change is control C-1: add a lower-bound branch to
    load_defer_gate_v11 that defers when the load-adjusted predicted count at
    b = 1.10 s exceeds 0. The quantity is already required, already computed and
    already written to truncation_sweep_comparison.json under key '1.1'; no gate
    branch reads it. This costs no compute and no new host, it makes branch (A)
    safe and branch (B) optional, and it converts the b = 1.10 s control from an
    unchecked premise into a measured one -- which is exactly what PF-26 did for
    host comparability and is the same repair one level down.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-014/reviews/RT-BATCH-014.md
  wrote_nothing_else: true
  git_writes_performed: none
  recorded_at: '2026-08-11'
```
