# VAL-BATCH-014 — Independent validation of RUN-SSIQ-a85692-k

- **Report id:** VAL-20260810-098fad
- **Task:** TASK-20260810-098fad (validator), authorized by DEC-20260810-616fd5
- **Goal / batch:** GOAL-SSIQ-001 / BATCH-014
- **Package under review:** the content-verified BATCH-014 package at commit
  `5471247e66263f3f2c590be63d78fefd0d9e673e` (`RUN-SSIQ-a85692-k`), archived by
  TASK-20260810-dae7ef
- **Verdict:** `valid` (role-contract equivalent: `passed`), with VC-4 reported
  as **partially answered** and five non-material findings recorded below.
- **Independently recomputed gate outcome:** `DEFERRED_AT_G0C` — matches the
  recorded outcome.

This file carries the working. The structured report is
`coordination/goals/GOAL-SSIQ-001/batches/BATCH-014/reviews/TASK-20260810-098fad/validation_report.yaml`.
`validation_notes.md` is deliberately not written: the task card lists it under
`deliverables` but declares no path for it, and `artifact_paths` is
authoritative. Everything that would have gone there is here.

---

## 0. Independence, policy, and method

Fresh session, no producer context, no prior state from the Executor or from
the archiving Coordinator. Requested policy `review-adversarial`
(`reasoning_effort: xhigh`, `independent_session: true`, `fallback_allowed:
false`, `degraded_allowed: false`).

`orchestration/model-policies.yaml` defines `review-adversarial` by a
capability contract, not by a model name: `requires.reasoning_effort: xhigh`,
`tool_use: true`, `structured_output: true`, `min_context_tokens: 180000`,
`min_output_tokens: 16000`, `independent_session_required: true`,
`fallback_policy: null`. Every one of those is met by this session. The model
that actually answered is `claude-opus-5`; per CLAUDE.md's model policy note
this runtime cannot bind a model per policy (subagents run `model: inherit`),
so the model is the session model rather than a policy-resolved identifier.
That is a *runtime binding property*, not a capability downgrade — no
`requires` field of `review-adversarial` is unmet — so I record
`fallback_used: false` and state the binding limitation explicitly rather than
recording a fallback that did not occur. Not probe-verified
(`orchestration.adapter doctor --probe` was not run here), so `model_verified:
false`.

**Method.** Every value below was recomputed from raw artifacts or from git
objects. I did not take any figure from the execution report, from
`truncation_sweep_comparison.json`'s own summary prose, from the archive
receipt, or from DEC-20260810-616fd5. I did not execute, re-run, edit, or
repair anything under review; the only code I ran was `git`, `shasum`, and a
static `ast` parse of the implementation module (parsing, not importing — no
module under review was executed).

---

## 1. VC-1 — the G-0c comparison, re-verified against RUN-h's archived environment

**Read directly:** `experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-h/environment.json`.

```
"platform": "Linux-6.18.5-fc-v18-x86_64-with-glibc2.39"
"cpus_available": 4
```

**CONFIRMED.** The archived host is exactly what the gate claims it read.

**RUN-k's own recorded host** (from `runs/RUN-SSIQ-a85692-k/environment.json`,
`host_capture_run_start` and `host_capture_run_end`, and independently
restated in `raw-result.json` and `truncation_sweep_comparison.json`):
`platform_platform = macOS-26.6-arm64-arm-64bit-Mach-O`, `platform_machine =
arm64`, `os_cpu_count = 14`. **CONFIRMED.** Start and end captures are
identical, as they should be for a 0.19 s run.

**Applying the frozen G-0c text myself** (`specification_v11.yaml` lines
1859–1872): "DEFER the entire run if EITHER of the following holds: — RUN-k's
`platform.platform()` does not begin with "Linux" or RUN-k's
`platform.machine()` is not "x86_64" …; — RUN-k's `os.cpu_count()` differs
from RUN-h's recorded `cpus_available` of 4."

- `"macOS-26.6-arm64-arm-64bit-Mach-O".startswith("Linux")` → False → first
  disjunct satisfied.
- `"arm64" != "x86_64"` → True → first disjunct satisfied a second way.
- `14 != 4` → True → second disjunct satisfied.

The clause is imperative ("DEFER the entire run if"), and its only carve-out —
"A DIFFERING KERNEL PATCH LEVEL OR glibc MINOR VERSION ALONE IS NOT A
MISMATCH" — is inapplicable: this is an OS-family, ISA and CPU-count
difference, not a patch-level one. **The frozen text MANDATES a defer on this
data; it does not merely permit one.** All three compared dimensions
mismatch, so the defer survives the failure of any two of the three tests.

**RUN-h was not mutated.** Stronger than the receipt's check:

```
git log --oneline --follow -- .../RUN-SSIQ-a85692-h/environment.json
  fcd9deacf  GOAL-SSIQ-001 BATCH-011: Coordinator snapshot commit of RUN-SSIQ-a85692-h
```

One commit in the file's entire history. Blob id at the run's own execution
commit `a58be638`, at HEAD, and in the working tree are all
`bf92a5d53c54d79bf80e4d97954b23f357a7e3cb`. `git log -- .../RUN-SSIQ-a85692-h/`
likewise shows a single commit for the whole directory. The producer commit
`5471247e6` touched exactly ten files, all `A` (added), none under RUN-h.
**The gate read the reference as archived; it is not a gate reading a mutated
reference.**

One faithfulness note, not a defect: `evaluate_g0c` (module lines 383–392)
compares against the literals `"Linux"` and `"x86_64"` rather than re-deriving
them from the archived platform string, while reading `cpus_available`
dynamically. That is exactly what the frozen text specifies (it hard-codes the
same two literals and only `cpus_available` by reference), so the module is
contract-faithful. It does mean the OS/ISA half of G-0c would not notice a
mutated archived platform string — moot here, since the file is provably
unmutated, but worth naming for any future amendment.

**VC-1: CONFIRMED.**

---

## 2. VC-2 — closed-list compliance, enumerated at every level

I enumerated `truncation_sweep_comparison.json` myself with a recursive walk:
**102 key paths, 21 at top level.** Full list in the structured report's
`artifact_checks`. Findings:

**(a) No sweep-derived quantity produced by this run appears anywhere in the
file.** No `n_attempted`, `n_resolved`, `n_timed_out`,
`n_naturally_completed`, `n_still_truncated`, `n_unresolved_and_*`,
`coverage_fraction`, `n_naturally_completed_matching_archived`, no
`mixed_regime_cross_check`, no `final_pop_overshoot`, no `sweep_points`, no
`per_vertex_records`, no `new_delta_map`, no I-1/I-2/I-3 identity outcome.
Consistent with `raw-result.json`'s `n_sweep_points_attempted/succeeded/failed
= 0/0/0`. **CONFIRMED.**

**(b) The file DOES contain nested keys whose names contain
`n_naturally_completed` and `histogram`** — all under
`pre_registered_reference_curve_v11`: `b_1_10.reference_n_naturally_completed`,
`b_1_45.reference_n_naturally_completed`,
`b_1_45.reference_delta_E_ge_5_histogram`,
`b_1_45.P1_P2_boundary_measured_n_naturally_completed`,
`full_population_at_1_70.full_value_histogram`, and others. The Coordinator's
receipt enumerated **only the top level**, so it did not reach these.

They are not a leak, and the frozen text settles it: the closed list
*requires* "the pre-registered reference curve with its two-sided
corrections", so the same clause's exclusion of "every histogram field" must
be read as scoped to sweep-derived histograms or the clause contradicts
itself. I verified these are frozen, not computed:

- A static `ast.literal_eval` of the module's `PRE_REGISTERED_REFERENCE_CURVE_V11`
  constant compares **equal** to the artifact's `pre_registered_reference_curve_v11`
  subtree (exact structural equality, verified programmatically).
- The constant's values match `specification_v11.yaml`'s own
  `pre_registered_prediction_curve_v11` text (lines 1631–1650): 115, 36,
  `{5:20, 6:4, 7:6, 8:6}`, 20, 79, `{2:28, 3:43, 4:8}`, 0.725, 133/186, and
  the floor/max literals 1.149932861328125 / 1.3924050331115723 /
  1.6985499858856201.

So every one of those numbers is a byte-copy of frozen pre-registered text and
could not have been produced at runtime. **CONFIRMED.**

**(c) FINDING F-1 (minor, non-material): seven top-level keys are present that
the closed list does not enumerate.** The closed list (spec lines 1943–1955)
says the file contains ONLY: `deferred`, `deferral_branch`, `load_confounded`,
the host captures, RUN-h's archived host values and the G-0c comparison
outcome, the CAL-1/CAL-2 records, the load-adjusted predicted counts, the
pre-registered reference curve, and the NO-SWEEP statement — and adds "THAT
LIST IS CLOSED: the word ONLY is load-bearing".

Present but not on that list: `gate_g0_result` (null), `gate_g0b_result`
(null), `gate_g1_result` (null), `f_cal_seconds` (null),
`measured_load_inflation_ratio_median_non_timed_out` (null),
`graph_identity_verification` (a real computed value), and
`ordering_interpretation_note` (prose). (`deferral_reason` and `cal1_summary`
are adjuncts of listed items and I do not count them against it.)

I classify this as a **strict-letter deviation with no substantive
consequence**: five of the seven are nulls that make the artifact *more*
honest about what was not evaluated (and are the same "ABSENT, not zero"
discipline PF-29(b) mandates for the LAC field); one is a step-(0)
instrument-integrity value that precedes the gate and is not sweep-derived;
one is the Executor's honesty-rule disclosure. None of them is a delta_E
quantity or a sweep result. It is nevertheless a real gap in the receipt's
`closed_list_compliance_on_defer` check, which asked only the sweep-derived
question at only the top level and returned an unqualified PASS.

**(d) FINDING F-2 (minor, non-material): a required top-level field is
absent.** The BATCH-010 in-band obligation (spec lines ~674–690) requires
`truncation_sweep_comparison.json` to carry, as top-level fields, among
others, "a caveats list containing the EXECUTION-HOST CONTENTION AND
HOST-IDENTITY caveat and the CROSS-HARDWARE caveat". There is no `caveats`
key. Two frozen clauses conflict on a defer branch (that obligation also
demands "the measured final-pop overshoot distribution", which is definitively
excluded on a defer), and the Executor resolved in favour of the explicitly
closed list, which is the coherent resolution. The *substance* of both
caveats is in-band anyway, under
`pre_registered_reference_curve_v11.transferability_note`,
`b_1_10.conditions`, and `statement`. Non-material; named for the amendment
list.

**(e) Leakage into the other artifacts.** `raw-result.json` is clean —
its only run-produced content is the host captures, the archived-host read,
`g0c_comparison`, `graph_identity_verification`, `wall_clock_seconds`, and
`git`. `stdout.log` is 15 lines and clean (no count, no histogram, no
delta_E). `stderr.log` is 0 bytes and its sha256 is
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, which I
confirmed by hashing the empty string.

`execution_report.yaml` is a different matter, and I record it as **FINDING
F-3 (advisory)**: it carries, in a section fenced three separate times as
non-official, calibration-derived figures and one probe-derived resolved
count from a smoke test at a *non-frozen* budget. None of these is a delta_E
value, a delta_E histogram, an equality cross-check, a final-pop overshoot
distribution, or a per-vertex record at a frozen sweep budget, and the frozen
closed list constrains `truncation_sweep_comparison.json` only — so this is
**not a closed-list breach and not a leak of a sweep-derived quantity**. But
those figures now live inside a declared, hash-bound run artifact, one click
from a future reader. The fact that this task card had to open with an
explicit prohibition against citing them shows the risk is not hypothetical.
Any downstream `EV-*` or decision citing this package must carry the
receipt's own `non_official_observation.status:
NOT_A_MEASUREMENT_OF_RUN_SSIQ_a85692_k` boundary with it.

**VC-2: CONFIRMED, with F-1, F-2 recorded as minor and F-3 as advisory.**

---

## 3. VC-3 — could the disclosed CAL-1/CAL-2 ordering interpretation have changed the outcome?

### (a) Is the other reading also admissible on the frozen text? **YES — and the frozen document contradicts itself at line level.**

The two formulations are both inside the frozen contract:

- `load_defer_gate_v11`, opening (line 1844): "it is evaluated immediately
  after step (0b)'s **host capture and calibration** and BEFORE the sweep loop
  begins" → calibration precedes gate evaluation (the *ungated* reading).
- `pre_freeze_review.round4_verdict` (d), line 1386: "G-0c is listed and
  evaluated FIRST, before G-0/G-0b/G-1/G-2/G-2b, **immediately after step
  (0b)'s host capture** and BEFORE the sweep loop" → the *gated* reading.

That is a direct internal inconsistency in the frozen text, and it is the real
root of the ambiguity. Two further pointers cut each way:

**Toward the ungated reading** (not cited by the Executor or the Coordinator):
the frozen budget note (line ~2216) says "IF A DEFER BRANCH FIRES the run
costs roughly 140 s (host capture plus CAL-1 and CAL-2 worst case) and
produces **the calibration and host facts** and nothing else", and the
dispatching handoff TASK-20260808-d458a3's completion gate says "If deferring:
the specific gate branch that fired, the measured values that triggered it,
and **the ~140s calibration cost** reported as the complete, successful
outcome". Both read most naturally as presupposing calibration on *every*
defer branch. (They can be read as a worst case over defer branches, which is
how the Executor read them; the Executor disclosed the 0.19 s versus ~140 s gap
explicitly rather than hiding it.) The round-3 reviewer who invented the gate
also asked for it "ordered with the other infrastructure branches" G-0/G-0b —
branches that by construction read calibration output.

**Toward the gated reading** (also not cited by anyone, and the strongest
single ground available): **PF-29(b)**, spec lines 1968–1973 — "LOAD-ADJUSTED
COUNTS ON A DEFER BRANCH: the closed list requires them, but **on G-0c or G-0**
they may be uncomputable (**no CAL-1 ratios**, or only timed-out ones)." Under
the ungated reading, CAL-1 always produces eight records before G-0c is
evaluated, so "no CAL-1 ratios" is unreachable except in the all-timed-out
case — which is precisely the second disjunct, making the first redundant.
Under the gated reading the two disjuncts map one-to-one onto G-0c and G-0.
Read against surplusage, PF-29(b) favours the Executor's reading. The
artifact's own null reason string ("undefined: G-0c fired before CAL-1
calibration was run/interpreted") is generated from exactly that clause's
template.

**Assessment of the Executor's four stated grounds.** (i) G-0c's "FIRST,
BEFORE ANY CALIBRATION IS **INTERPRETED**" — weak, and arguably points the
other way: "interpreted" is a deliberate word choice distinct from "run".
(ii) "to whatever extent they exist" — suggestive but not decisive; it is
equally satisfied by the G-0/G-0b/G-1 branches, where CAL-2 records genuinely
do not exist. (iii) economy — real, but an argument about what the contract
*should* say, not what it does. (iv) the dispatching handoff — **defective on
two counts**, see F-4.

**FINDING F-4 (minor, citation hygiene).** `execution_report.yaml` lines 54–56
justify the reading by "the dispatching Coordinator's own handoff
(TASK-20260808-d458a3), which lists G-0c ahead of *'any of the 8 CAL-1
calibration vertices timing out'* in its own evaluation order." That phrase in
quotation marks **does not occur in TASK-20260808-d458a3.yaml**. I searched
the whole 109-line record: "CAL" appears twice, once inside the word
"specifically" (line 45) and once as "the ~140s calibration cost" (line 105);
"timing out" / "timed out" / "timeout" appear zero times. What the handoff
actually says (line 43) is "evaluate load_defer_gate_v11 (G-0c, then G-0,
G-0b, G-1, G-2, G-2b, in that exact order)". The gloss is *substantively*
faithful — G-0 is indeed the CAL-1-timeout branch — so this is a citation
defect, not a fabricated fact, but AGENTS.md rule 9 forbids fabricating
citations and quotation marks around a paraphrase of a named ledger record is
the wrong side of that line. Separately, ground (iv) is **non-probative**: the
handoff states a *gate evaluation* order, and both readings agree on gate
evaluation order — they differ on whether *calibration executes* beforehand.
DEC-20260810-616fd5 reproduces this ground ("TASK-20260808-d458a3's own stated
evaluation order") as one of "three independent grounds" without checking the
quotation or noticing that the same handoff's completion gate points the other
way.

**My conclusion on (a): the other reading is admissible; the Coordinator's
"defensible on three independent grounds" is overstated; but the Executor's
reading is nonetheless the better-supported one, on a ground (PF-29(b)) that
nobody in the chain identified.** The Executor did the required thing — it
disclosed rather than guessed silently.

### (b) Could the other reading have produced any different recorded outcome? **NO — and not merely here.**

This is structural, not circumstantial:

1. G-0c's inputs are the run-start host capture and RUN-h's `environment.json`
   **only** (`evaluate_g0c(host_cap, archived_host)`, module lines 354–412).
   No calibration output enters it. Running CAL-1/CAL-2 first cannot change
   any input to G-0c: the host capture is taken at run start, before STEP (0),
   and `platform`/`machine`/`cpu_count` are load-invariant.
2. The gate is an else-chain: G-0 is "Else if", G-0b is "Else if", G-1 is
   "Else if", G-3 is "Else". Once G-0c fires, no later branch applies under
   either reading.

Therefore under **both** readings: `deferred = true`, `deferral_branch =
G-0c`, `load_confounded = true`, `n_sweep_points_attempted = 0`. What would
differ is only artifact *richness* — `cal1_records` would hold 8 entries,
`cal1_summary`/`f_cal_seconds`/`measured_load_inflation_ratio_...` would be
populated, and `load_adjusted_predicted_counts` would carry integers instead
of null-with-reason. Note the gate result fields would still be null even
then, since G-0/G-0b/G-1 are never *evaluated* under either reading.

**The two readings are outcome-equivalent for this contract in general, not
just on this run.** They can never yield a different deferral branch or a
different sweep outcome. This is a materially different finding from "the
Executor guessed correctly", and I state it as such.

**Adversarial cross-check on outcome-shopping.** The Executor's pre-execution
exercise had already established, before the official run, how the later
branches would resolve on this host. I tested whether the interpretation
choice could therefore have been used to select a preferred outcome: it could
not. Because G-0c sits at the head of an else-chain and fires unconditionally
on this host under either reading, *every* later branch — including any
proceed branch — is unreachable. There is no interpretation of the frozen
text on which this run reaches a sweep. **Clean.**

### (c) Does anything downstream depend on `cal1_records` being non-empty? **NO.**

PF-29(b) explicitly provides for null-with-reason LAC on a G-0c defer. The
closed list says "to whatever extent they exist", and the BATCH-010 in-band
obligation requires the CAL-1/CAL-2 records to be *present*, which empty lists
satisfy. Reading rules P-1/P-2/P-3 are per sweep point and there are no sweep
points; P-4 forecloses any reading regardless. No contract clause, decision
rule, or downstream artifact requires a non-empty `cal1_records`.

There is a real but non-contractual loss: RUN-k's own artifacts record the
*fact* of a host mismatch but no measured *magnitude* of host difference. G-0c
is defined on identity, not magnitude, so the gate is unaffected — but a
future reader of RUN-k alone cannot see how large the difference was without
leaving the run's official measurement set.

### (d) Should the frozen text be amended regardless? **YES.**

Independently of (b). A frozen contract that contradicts itself at lines 1386
and 1844 forced an Executor to interpret rather than execute; the next run of
this lineage will face the same fork, and on a host where G-0c does *not* fire
the two readings converge, so the ambiguity only ever bites on the branch
where the contract is least observable. A versioned Coordinator
`protocol_amendment` should (i) pin the ordering in one sentence, (ii) make
the defer-cost note branch-specific rather than a flat "~140 s", (iii) list
`graph_identity_verification` and the schema-null gate fields explicitly in
the closed list (F-1), and (iv) resolve the `caveats`-list conflict on defer
branches (F-2).

**VC-3: ANSWERED in full — (a) yes, admissible, with the frozen text
self-contradictory; (b) NO, outcome-equivalent by construction; (c) no
downstream dependency; (d) amend.**

---

## 4. VC-4 — the unenforced `ulimit -v` (PARTIALLY ANSWERED)

**What was actually executed** (`command.txt` lines 118–122, verbatim, the
only executable lines in the file):

```
mkdir -p experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-k
timeout 1000 python3 experiments/EXP-SSIQ-a85692/implementation/delta_e_floor_straddling_sweep_v11.py \
  --run-dir experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-k \
  > .../stdout.log \
  2> .../stderr.log
```

No `ulimit -v`. **Confirmed: the only binding cap in force was `timeout
1000`.** `environment.json` records `resource_caps_applied.address_space_ulimit_kb:
null` and `manifest.yaml` records `resources.peak_rss_bytes: null`. So there
is no memory measurement of any kind in this package.

**Part 1 — could the missing bound have altered any RECORDED value? NO, and
this I can settle analytically.** The argument is one-sided:

- `ulimit -v` sets `RLIMIT_AS`. Its only effect is to make an allocation
  fail once address space exceeds the cap, raising `MemoryError`.
- The G-0c code path is: imports → `host_capture()` → STEP (0)
  `build_graph_for_prime` + `verify_graph_identity` → read RUN-h's
  `environment.json` → `evaluate_g0c` → write two JSON files. Per the module's
  own frozen discipline (docstring lines 63–78, code lines 812–825), STEP (0)
  is **not** wrapped in try/except, and neither is anything else on this path.
  A `MemoryError` therefore propagates uncaught and the run terminates with
  **no `truncation_sweep_comparison.json` written at all**.
- Hence, with the cap enforced, exactly one of two things happens: peak
  address space stayed under 2 GiB and every recorded value is bit-identical,
  or it did not and *no artifact exists*. The cap cannot silently perturb a
  value inside a written artifact.
- The one exception is `wall_clock_seconds` (0.1884760856628418), which
  allocator pressure could in principle perturb without removing the
  artifact. It feeds nothing: it is compared only against the 1000 s budget
  (0.02% consumed), no gate reads it, and no threshold in the frozen contract
  depends on it. So no gate outcome and no reported quantity depends on it.

**Part 2 — is the Coordinator's "trivially far under 2 GiB" established? NO,
and I decline to adopt it.** Two objections:

1. **It is an inference about the wrong quantity.** `ulimit -v` caps *virtual
   address space*, not resident set or workload size. The receipt, the
   decision, `manifest.yaml`, `environment.json`, `command.txt` and
   `execution_report.yaml` all argue from workload ("one 203-vertex graph
   build, then defer") to a conclusion about the cap. Workload size bounds
   working set; it does not bound `RLIMIT_AS`. Address space on a modern
   arm64 runtime is inflated by interpreter arenas, thread stacks and mmap'd
   regions that are unrelated to how many vertices the graph has. A 2 GiB
   `RLIMIT_AS` failing on a process with a tiny working set is a well-known
   phenomenon, which is one reason the cap is applied on Linux and not here.
2. **It is unmeasured.** No `ru_maxrss`, no peak VSZ, nothing. `manifest.yaml`
   says so plainly (`peak_rss_bytes: null`, "not instrumented"), which is the
   honest disclosure, and then the very next sentence asserts "actual peak
   memory use was trivially far under the 2 GiB budget". That assertion is not
   supported by anything in the package.

**Settling part 2 would require executing the module on a comparable host
under instrumentation — an execution my constraints forbid ("do not
originate, edit, repair, or re-run the artifacts under review"). I therefore
report VC-4 as PARTIALLY ANSWERED with that boundary named, rather than
silently dropping it or resolving it by re-running.** I substitute no
estimate for the missing measurement.

Note the asymmetry that makes this benign for *this* run: since the cap can
only ever delete an artifact rather than alter one, and an internally
consistent artifact exists, the practical consequence of part 2 remaining open
is nil for RUN-SSIQ-a85692-k specifically. What is not nil is the standing
enforcement gap.

**Part 3 — must the gap be repaired before any FUTURE run of this contract on
a non-Linux host? Yes, with a precise scope.** Under *this* contract a
non-Linux host defers at G-0c before CAL-1, CAL-2 or either sweep pass, so it
can never reach the workload where a 2 GiB cap could plausibly bind; the gap
is therefore not urgent for re-running specification_v11 as frozen. It **is**
required for anything broader, and for the harness generally: any contract
declaring `budget.maximum_memory_gb` and executed on Darwin currently declares
a budget it does not enforce, and no run in that situation can demonstrate
compliance. Concretely I would require, before the next non-Linux execution of
any memory-budgeted contract:

- a portable enforcement mechanism (in-process `resource.setrlimit` on a limit
  Darwin accepts, or an external RSS watchdog), and
- **mandatory recording of `resource.getrusage(RUSAGE_SELF).ru_maxrss` in
  every run**, which costs nothing and would have converted this entire check
  from an inference into a measurement.

**VC-4: PARTIALLY ANSWERED. Part 1 settled (no recorded value could differ).
Part 2 NOT PERFORMED — requires a forbidden execution; the Coordinator's
inference is tested and rejected as unestablished, not adopted. Part 3
answered: yes, with scope.**

---

## 5. VC-5 — gate order and short-circuit, against the real module

**Order.** From `delta_e_floor_straddling_sweep_v11.py`, not from any report:

| branch | module line | reached only if |
| --- | --- | --- |
| G-0c | 841 `g0c = evaluate_g0c(...)` | unconditional |
| G-0 | 880 `g0_result = evaluate_g0(cal1_records)` | `not g0c["fired"]` |
| G-0b | 897 `g0b_result = evaluate_g0b(cal2_records)` | `not g0_result["fired"]` |
| G-1 | 908 `g1_result = evaluate_g1(f_cal)` | `not g0b_result["fired"]` |
| G-2 / G-2b / G-3 | 926 `evaluate_g2_g2b_g3(...)` | `not g1_result["fired"]` |

Exactly `[G-0c, G-0, G-0b, G-1, G-2, G-2b, G-3]`. **CONFIRMED.**

**G-0c precedes any sweep point.** The sweep loop is guarded by `if
deferred_branch is None:` at line 943; `deferred_branch` is set to `"G-0c"` at
line 859. **CONFIRMED** — no sweep point is reachable once G-0c fires.

**The open question the card raised: can a null mean "evaluated and produced
nothing"? NO — refuted structurally.**

- `g0_result`, `g0b_result`, `g1_result` are initialized to `None` at module
  lines 850–852 and assigned **only** inside the `else:` branch of `if
  g0c["fired"]:` (lines 868+), each nested one level deeper than the last.
- `evaluate_g0`, `evaluate_g0b` and `evaluate_g1` each return a `dict` on
  every path (lines 495–507, 510–520, 531–541). **None of them can return
  `None`.**

Therefore `gate_g0_result: null` in the artifact is logically equivalent to
"`evaluate_g0` was never called". The same for G-0b and G-1. The artifact
*can* distinguish the two cases, contrary to the concern the card raised, and
it distinguishes them correctly here.

`f_cal_seconds` deserves the sharper treatment, because `compute_f_cal` *can*
return `None` (line 526–527, when every CAL-1 record timed out), so a null
there is ambiguous in isolation. But `compute_f_cal` is called only at line
907, immediately followed by `evaluate_g1`, which always returns a dict. So
`gate_g1_result: null` ⟹ `compute_f_cal` was never called ⟹ `f_cal_seconds:
null` means "not computed", not "computed as undefined". The identical
argument covers
`measured_load_inflation_ratio_median_non_timed_out` (called at 918, after
G-1 does not fire). The joint null pattern in the artifact is consistent with
exactly one execution path: G-0c fired first.

`load_adjusted_predicted_counts` carries `{value: null, reason: "undefined:
G-0c fired before CAL-1 calibration was run/interpreted"}` at both `1.1` and
`1.45`. I traced this to module lines 1073–1079: the reason string is
generated by `"undefined: %s fired before CAL-1 calibration was
run/interpreted" % deferred_branch`, and the keys come from `str(b) for b in
SWEEP_BUDGETS`. The recorded strings and keys match that template exactly.
This is PF-29(b)'s "ABSENT, not zero" discipline behaving correctly, and it is
**not** a contradiction of the never-evaluated claim.

Corroborating trace: `stdout.log` shows the run going host capture → STEP (0)
build → STEP (0) verify → STEP (0b) archived-host read → `GATE G-0c:
fired=True` → `DEFERRING at G-0c` → gate evaluation complete → run-end host
capture. No `GATE G-0:` / `GATE G-0b:` / `GATE G-1:` / `GATE G-2/G-2b/G-3:`
lines appear, and the module emits one for each whenever it evaluates one
(lines 881, 898, 909, 929). **The logs corroborate the code's structure
rather than merely asserting the conclusion.**

**VC-5: CONFIRMED. The finding reported to me is correct, and I confirm it on
the stronger ground that the code cannot reach those assignments on the G-0c
path at all.**

---

## 6. VC-6 — step (0)'s graph-identity re-verification

**Ran exactly once.** `grep -n verify_graph_identity` over the module returns
one call site (line 822) among comment mentions; `build_graph_for_prime`
likewise one call site (line 816). Both are outside any loop and outside any
try/except. **CONFIRMED.**

**Ran before G-0c.** Build at 816, verify at 822, archived-host read at 835,
`evaluate_g0c` at 841. **CONFIRMED**, and corroborated by `stdout.log` line
ordering (STEP (0) lines 4–7 precede the STEP (0b) / GATE G-0c lines 8–9).

**Recorded values.** `n_built_vertices = 203`, `archived_n_vertices = 203`,
`vertex_count_match = true`, `degree_sequence_check = {n_vertices: 203,
n_degree_ne_3: 0, examples: [], pass: true}`, `pass: true`. Identical in
`raw-result.json` and `truncation_sweep_comparison.json`. `stdout.log` also
records `non_fp_rational_set` size 194 (expected 194). **CONFIRMED.**

**Is the comparison target the archived graph it claims?** This needs a
precise answer, and the honest one is *partly*.

`verify_graph_identity` (in `delta_e_independent_rng_probe_v8.py`, lines
164–175) does exactly two things: `len(g["vertices"]) == archived_n_vertices`,
and `build_isogeny_graph.degree_sequence_check(g)`, which is `all degrees ==
3` (lines 668–672). The comparison target is therefore **two frozen scalars**
(`ARCHIVED_N_VERTICES = 203`, passed at the call site as a module constant,
and 3-regularity), **not** RUN-h's archived graph object. No archived vertex
set, vertex coordinate list, or j-invariant map is read for this check. The
run's only coordinate-level binding to the archived graph would have been
`run_cal1`'s `assert set(THE_EIGHT) <= set(graph["vertices"])` (line 425) —
which is on the CAL-1 path and therefore never executed officially.

I verified the *scalar* is right, from RUN-h's own artifacts rather than from
the module: `RUN-SSIQ-a85692-h/raw-result.json` records
`graph_identity_verification.n_built_vertices = 203`,
`archived_n_vertices = 203`, `degree_sequence_check.n_degree_ne_3 = 0`, and
`comparison_against_archived_summary.non_fp_rational_only.n_both_resolved =
194`. So 203/194 are the archived graph's true figures and RUN-k's rebuild
reproduces them.

**FINDING F-5 (limitation, not a defect).** "Graph-identity re-verification"
verifies cardinality and 3-regularity, not identity. Two different 203-vertex
3-regular graphs would both pass. The link to the archived graph rests on the
determinism of `build_graph_for_prime(2437, 20260805)` against byte-identical
vendored `modpoly_data`, which is a reasonable but *unverified-in-band*
premise for this run. This is **contract-compliant**: the frozen text names
`delta_e_independent_rng_probe_v8.verify_graph_identity` and the Executor
called it unchanged, so the run did what it was told. The weakness is in the
check's name versus its content, and belongs on the amendment list, not
against RUN-SSIQ-a85692-k. Scoped correctly, what step (0) establishes is that
the instrument was assembled to the right shape on this host — nothing more,
and nothing about delta_E.

**VC-6: CONFIRMED, with F-5 recorded as a scope limitation of the frozen
check.**

---

## 7. VC-7 — code-commit binding and the `dirty: true` flag

**Commit binding.** `manifest.yaml` `run.code.commit =
a58be63848492aa45c75b8d2d6973a352166de96`. Verified:

- `git rev-parse 5471247e6^` → `a58be638…`, whose subject is `coord: freeze
  EXP-SSIQ-a85692 v11 (DEC-20260808-c2a470), dispatch executor`.
- `git rev-list --count a58be638..5471247e6` → **1**. Exactly one commit
  between the freeze and the landing of the package, and it is the package.
- `git show --stat a58be638` → 4 files: `specification_v11.yaml`,
  `DEC-20260808-c2a470.yaml`, `GOAL-SSIQ-001/goal.yaml`,
  `TASK-20260808-d458a3.yaml`. So a58be638 genuinely *is* the freeze-and-
  dispatch commit.
- `specification_v11.yaml`'s blob at a58be638 (`83a84feb9a…`) equals its blob
  now. The contract has not moved since the freeze.

**CONFIRMED, including the receipt's stronger claim that no intervening commit
exists between freeze and execution.**

**The `dirty: true` scoping.** This is the part that needed testing, because
`dirty` is computed by `git_state()` (module lines 746–756) as
`bool(git status --porcelain)` — a single boolean that **cannot distinguish
"only new untracked paths" from "tracked files modified"**. The
`dirty_note`'s scoping claim is therefore not verifiable from the flag itself.
I verified it by other means:

- `git diff-tree --name-status -r 5471247e6` → all ten paths marked `A`
  (added). Zero `M`, zero `D`. `git show --stat` → 10 files, 2491
  insertions, **0 deletions**.
- `git diff --stat a58be638 HEAD -- experiments/EXP-SSIQ-a85692/implementation/
  experiments/EXP-SSIQ-58b642/implementation/` → the *only* change across both
  implementation trees between the freeze commit and now is the addition of
  `delta_e_floor_straddling_sweep_v11.py`. Every module the run imports
  (`delta_e_truncation_probe_v9.py`, `delta_e_truncation_sweep_v10.py`,
  `compute_delta_e.py`, `trapping_diagnostic_v5.py`,
  `delta_e_independent_rng_probe_v8.py`, `build_isogeny_graph.py`,
  `calibration_synthetic.py`) is byte-unchanged.
- `RUN-SSIQ-a85692-h/environment.json`, the one archived file the run read, is
  unchanged since its own snapshot commit (VC-1).

`git_state()` also runs *late* — at line 1162, after
`truncation_sweep_comparison.json` was written at 1151 and while
`stdout.log`/`stderr.log` were open under shell redirection — so the two
untracked paths the note names are exactly what a `git status --porcelain` at
that moment would have reported. The note is **consistent and not
understated** on all available evidence.

**Residual, stated rather than glossed:** the run executed in an ephemeral
worktree (`/tmp/wt-ssiq-b014-cont`, per `command.txt`). A tracked file
modified there and never committed would be invisible to every check above.
Nothing suggests it happened — the run's own outputs (203 / 194 / 3-regular)
reproduce RUN-h's archived figures exactly, which is what unmodified modules
predict — but the dirty boolean cannot rule it out and I do not claim it does.
The general repair is the obvious one: record the `git status --porcelain`
*output*, or per-input file hashes, rather than a boolean. `source_access_log.yaml`
already names the inputs but records `hashing: n/a`.

**VC-7: CONFIRMED, with the boolean's structural limitation named.**

---

## 8. VC-8 — audit of the archive receipt and its process deviation

**Hash recomputation.** I recomputed **all ten** declared `path_sha256` values
(the card asked for at least three), twice over: once against the working tree
and once by piping `git show 5471247e6:<path>` for six of them, which is
independent of the worktree entirely. **All ten match the receipt exactly**,
including `stderr.log` =
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, which I
confirmed is the sha256 of the empty string, corroborating the empty-stderr
claim by hash rather than by reading the claim.

**`declared_paths` vs the commit's file set.** `git diff-tree --no-commit-id
--name-status -r 5471247e6` returns exactly the ten declared paths, all `A`.
Set equality in both directions. The receipt's exclusion of itself from
`declared_paths` is correct — it does not exist at 5471247e6 and its hash
would be unverifiable there.

**`git diff --stat 5471247e6 -- <run dir> <impl file>`** is empty: the tree I
read is byte-identical to the producer commit.

**Is content-first binding sufficient here? YES, on these facts.** I say so
for reasons stronger than the receipt's own:

1. All ten hashes verify against both the tree and the commit object.
2. The producer commit's parent is *exactly* the freeze commit, with `git
   rev-list --count` = 1, so no post-freeze state could have influenced the
   executed code.
3. The one archived artifact the gate depends on (RUN-h's `environment.json`)
   has a single commit in its entire history and an unchanged blob id at the
   execution commit, at HEAD and in the tree.
4. The package is small, complete against the frozen `required_artifacts`
   list, and internally consistent across five independent files.

**What is genuinely lost, stated more sharply than the receipt states it.**
The receipt says the Coordinator lost the ability to inspect the package
before it entered history, and that its checks could detect but not prevent a
defective package. That is correct as far as it goes. The sharper statement is
this: **when the producer chooses what enters history, anything the producer
did not write is unrecoverable and undetectable by any later check, including
mine.** Had a first artifact been written, found wanting, and replaced before
the single commit, no hash, tree diff or reachability check in this repository
would show it. That risk is *bounded* here — one commit, parented directly on
the freeze commit, no amends or intervening commits in the range, and a
package whose every recomputable value I independently reproduce — but it is
not *eliminated*, and content-first binding cannot eliminate it by
construction. Content binding proves what the bytes are; only a
snapshot-before-review ordering proves what the bytes were *first*.

**Where I disagree with the Coordinator's characterization.** Three points,
none of which changes the archive's admissibility:

- The receipt's `closed_list_compliance_on_defer` check returns an unqualified
  PASS on a top-level enumeration only. At depth, the artifact carries the
  pre-registered reference curve's nested counts and histograms (correct, and
  required — see VC-2), and at the top level it carries seven keys the closed
  list does not enumerate (F-1). Neither is material, but "not one
  sweep-derived field is present" was verified over a smaller domain than the
  check's phrasing implies.
- The receipt's `budget_compliance` check asserts "actual peak memory was
  trivially far under 2 GiB" in the same breath as "No figure for peak memory
  was measured and none is asserted here." The second sentence is right; the
  first is an assertion about an unmeasured quantity, and it reasons from
  workload to a bound on address space (VC-4). It should be withdrawn or
  restated as "no evidence of over-budget use, and no measurement either way".
- DEC-20260810-616fd5 calls the ordering interpretation "defensible on the
  Executor's three stated grounds", one of which rests on a quotation that is
  not in the record it cites and which does not discriminate between the two
  readings anyway (F-4). The conclusion (defensible) is right; the support
  offered for it is weaker than stated, and the strongest actual ground
  (PF-29(b)) went unnoticed.

I regard the process deviation as **honestly and adequately recorded, and the
lost before-history inspection window as a real process gap but NOT a material
integrity gap for this package.** I would not accept the same argument for a
package with recomputable scientific content — here there is none to
misreport, which is precisely why content binding suffices.

**VC-8: AUDITED. Receipt accurate on every fact I could recompute; three
characterizations disputed; content-first binding sufficient here.**

---

## 9. Independently recomputed gate outcome

Applying `specification_v11.yaml`'s frozen `load_defer_gate_v11` branch G-0c
myself, to the raw recorded host data (`macOS-26.6-arm64-arm-64bit-Mach-O` /
`arm64` / 14) and the directly-read archived host
(`Linux-6.18.5-fc-v18-x86_64-with-glibc2.39` / `cpus_available: 4`), and
respecting the else-chain structure of the remaining branches:

> **`DEFERRED_AT_G0C`.** The gate branch the frozen text implies from the raw
> data is G-0c, mandated (not merely permitted), on all three compared
> dimensions independently, with G-0/G-0b/G-1/G-2/G-2b/G-3 unreachable. This
> **matches** the recorded outcome.

Recomputed as a check on the gate's operation and nothing else. Under both
admissible readings of the CAL-1/CAL-2 ordering, the branch is the same.

---

## 10. Findings summary

| id | severity | finding |
| --- | --- | --- |
| F-1 | minor, non-material | Seven top-level keys present beyond the defer artifact's explicitly closed list (5 schema nulls, `graph_identity_verification`, `ordering_interpretation_note`). No sweep-derived leakage. Receipt's PASS was top-level and sweep-derived-only. |
| F-2 | minor, non-material | The BATCH-010 in-band obligation's required top-level `caveats` list is absent; conflicts with the closed list on a defer branch; caveat substance present in-band elsewhere. |
| F-3 | advisory | `execution_report.yaml` carries non-official pre-execution calibration figures and one non-frozen-budget probe count inside a declared, hash-bound artifact. Fenced three times, not a closed-list breach, but a standing mis-citation surface. |
| F-4 | minor, citation hygiene | `execution_report.yaml` attributes a quoted phrase to TASK-20260808-d458a3 that does not appear in it; the ground is also non-probative. Reproduced (in paraphrase) by DEC-20260810-616fd5 without check. |
| F-5 | limitation of the frozen check | "Graph-identity re-verification" verifies vertex count + 3-regularity against frozen scalars, not coordinate identity against the archived graph. Contract-compliant; the check's name overstates its content. |

None of these is an evidence-integrity defect against RUN-SSIQ-a85692-k.
F-1, F-2 and F-5 are amendment items for the Coordinator; F-3 is a
citation-discipline requirement on any downstream record; F-4 is a correction
that belongs in a superseding record, never an edit (AGENTS.md rule 4).

## 11. Boundaries — what this report does NOT say

- A G-0c defer is an **infrastructure outcome** (AGENTS.md rule 5). This
  report offers **no interpretive claim, in either direction**, about delta_E,
  delta_E convergence, truncation bias, H-SSIQ-36e970, lever L4, or the
  p^{1/3+o(1)} exponent budget. Nothing was measured; nothing is implied.
- The gate operating correctly is **not** a positive mathematical result
  either. It is an instrument behaving as specified.
- A `valid` verdict means this run package is **admissible evidence of its own
  execution**. It does not support any ECDLP or isogeny claim, does not
  demonstrate a speedup, and does not authorize promotion, an `EV-*` record,
  or any hypothesis-status move. Those remain the Coordinator's, on the
  reviews taken together.
- BATCH-014's measurement objective is unmet. That is a statement about
  execution-host availability, not about the mathematics.
- I did not cite, and no part of this report rests on, the pre-execution
  CAL-1 figures as measurements of RUN-SSIQ-a85692-k. They are not.
- Scope of this validation: the ten declared artifacts at 5471247e6, the
  frozen `specification_v11.yaml` at blob `83a84feb9a…`, RUN-h's archived
  `environment.json`, the dispatching handoff, DEC-20260808-c2a470,
  DEC-20260810-616fd5, the archive receipt, and the five pre-freeze reports.
  Toy scale: p = 2437, N = 203.

## 12. Checks not applicable, stated rather than dropped

- **Null-object control (`docs/inventor-protocol.md` §3).** Not triggered:
  this run reports no correlation, bias, or excess of any kind, so there is no
  statistical signal requiring a null object of the same shape. Correspondingly
  there is no evidence here, and none is claimed.
- **Scaled-down-instance ladder (§6).** Not triggered: no improvement,
  speedup, or complexity claim is made anywhere in this package.
- **Heuristic-validation and cost-model checks** (pre-registered prediction,
  sample integrity, correspondence validity, cost-unit honesty, cost
  bookkeeping). Not applicable: no heuristic is validated and no cost table is
  reported. The one pre-registered object present — the reference curve — is
  verified frozen-before-execution in VC-2 and was never compared against
  anything, because nothing was measured.
- **Proof-architecture checks (§8 / KN-TECH-080).** Not applicable: this is
  not a proof-oriented deliverable.
- **Metric recomputation.** The only recomputable quantities in the package
  are the G-0c predicate (§9), the graph-identity scalars (§6), and the
  budget ratios; all recomputed. There is no metric derived from measurement
  data, because there is no measurement data.

---

*Prepared under TASK-20260810-098fad. Report handed to the Coordinator's
ledger archive task TASK-20260811-fbf1bf for durable commit. This Validator
committed nothing and wrote nothing outside the two declared `artifact_paths`.*
