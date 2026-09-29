# Red team — BATCH-fbb639 part (c): the two-route dispersion measurement

`TASK-20260813-6ab893` / `BATCH-fbb639` / `GOAL-MLKEM-005`. Governed by
`PREREG-3` (`coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-0eb5a3/prereg.md`),
notarized at commit `3d2eabf8ddfa9e33ed3c9cf5b0cc0d9f14ebcd82` (**PREREG-3
archive, 3 declared paths**). Reviews the lead producer's committed snapshot
at commit `391f811e7b6b23fb40235a0608aebeb05b5b9c4a` (**lead archive, 8
declared paths**), `TASK-20260813-7ac7cd`.

**Claim tier TOY, unconditionally.** Nothing in this report bears on ML-KEM
security, any FIPS 203 parameter set, any attack cost, or any cost model.
I changed no research status, rescored no frozen verdict, modified no
producer artifact, and made no commit.

## Inference record (verbatim, as directed)

```
requested_policy: review-adversarial
reasoning_effort: xhigh (per .claude/agents/red-team.md, role red-team's
  default_policy review-adversarial -> orchestration/model-policies.yaml)
fallback_allowed: false
degraded_allowed: false
independent_session_required: true
model_that_answered: claude-sonnet-5 (Claude Sonnet 5, per this session's own
  system context)
model_verified: false
model_verified_reason: >-
  AGENTS.md rule 12 / PREREG-3 section 7-8: independence in this goal is
  PROCEDURAL and never model-level, and is UNMET AND UNWAIVED. No adapter
  probe receipt exists for this session; AUTORESEARCH_POLICY and
  AUTORESEARCH_BACKEND are unset. Recorded as a verification gap, never as
  satisfied.
independent_session: true (fresh Claude Code subagent invocation, no shared
  conversational state with the Coordinator sessions that authored/notarized
  PREREG-3, the lead producer, or the concurrent Validator task)
host_measured: vm (Linux vm 6.18.5-fc-v20 x86_64, python 3.11.15) -- NOTE:
  this happens to be the SAME hostname string ("vm") the corpus's own
  Linux-side runs (results_relvar.json, results_l7l8.json) report; this is a
  property of the sandboxed execution recipe this harness uses, not a claim
  that my review shares process state with any producer run.
```

## What I reviewed, and the commit verification the task envelope required

I read the **Coordinator-committed snapshots**, not the working tree, and
verified both archives' change-set equality myself with `git diff-tree`:

- `TASK-20260813-6ad846` (PREREG-3 notarization), commit `3d2eabf8d`:
  `git diff-tree --no-commit-id --name-only -r 3d2eabf8d` returns exactly 3
  paths (`snapshot-receipt.json`, `prereg.md`, `prereg_sha256.txt`) — **3/3**,
  matching the declared set. `git show 3d2eabf8d^:.../prereg.md` fails
  ("exists on disk, but not in `3d2eabf8d^`") — the negative test (frozen text
  absent at the parent) holds. `git ls-tree -r 3d2eabf8d -- .../TASK-20260813-7b3039`
  returns only `task_card.md` (a batch-opening coordination artifact, not a
  producer artifact) — **zero producer artifacts**, as required.
  `git log --all --follow` for `prereg.md` returns exactly **1** commit.
- `TASK-20260813-7ac7cd` (lead snapshot), commit `391f811e7`:
  `git diff-tree --no-commit-id --name-only -r 391f811e7` returns exactly 8
  paths, matching the declared set exactly — **8/8**.

Both archives verify as claimed. I did **not** find a notarization defect.

**Verdict, stated up front.** The mechanical arithmetic of obligations 1-3 is
correct given the frozen inputs, and `T-C3LANE-OPEN-PARTIAL` is the branch
`PREREG-3` section 3.5's frozen precedence actually fires from the reported
numbers. But the **primary target** of this task — whether `ROUTE-I` is a
genuinely independent second computation — fails on direct inspection: all
three "routes" this batch and its predecessors call independent
(`measure_am4.py`, `measure_relvar.py`, `replicate_l7l8.py`) run **the same
algorithm, verbatim**, on the same deterministic seeds, and for `L7` even on
the **same host**. `D_route = 0.0` at all 18 covered cells is not a finding
about `lam1n`/`hkz` being clean, well-behaved observables; it is close to a
structural inevitability of this corpus's comparison methodology, confirmed
by a calibration control I built against `rdet`. I also found and verified a
real, previously-unflagged coverage-table defect (a beta mismatch affecting 2
covered cells, harmless to the reported `D_route` values but false in what it
claims to have compared). Neither finding overturns the branch call under
`PREREG-3`'s literal text — I am not arguing for a different branch — but
both narrow, substantially, what a reader is entitled to conclude from
"`SOME-EXCEEDS` at 18/18 covered cells."

---

## 1. PRIMARY TARGET — is `ROUTE-I` genuinely a second, independent route?

**No, not in the sense a reader of "two independently computed routes
disagree by 0.0" would assume.** I read `replicate_l7l8.py`,
`measure_relvar.py` and `measure_am4.py` side by side and diffed their
`make_A`, `build_basis` and `hkz_profile` functions
(`probes/probe_route_independence.py`, output in
`probes/probe_route_independence_output.json`). All three files use the
**same RNG seed formula**, the **same exact-integer basis construction**, and
the **same BKZ-pass-then-explicit-HKZ-sweep-then-independent-enumeration
reduction pipeline**. The diffs contain nothing but docstring wording,
line-wrapping, one unused `rank=` parameter present only in the original
(`measure_am4.py`), and one extra reported field
(`rows_passed_to_fpylll`) added by `replicate_l7l8.py`. This is not an
inference from "similar shape" — **the source files say so themselves**:
`replicate_l7l8.py`'s `hkz_profile` docstring reads *"CARRIED VERBATIM from
BATCH-9e3584 measure_relvar.py"*, and `measure_relvar.py`'s own
`hkz_profile`/`make_A`/`build_basis` docstrings read *"CARRIED VERBATIM from
BATCH-cbe023 measure_am4.py"* — i.e. `measure_am4.py`, the very script this
batch cites as the L9/L11 `ROUTE-I`, is the **literal ancestor** that
`measure_relvar.py` (`ROUTE-P`) copied its own reduction code from.

Chain of custody, confirmed by my probe:

```
measure_am4.py (BATCH-cbe023, original)
   |  "CARRIED VERBATIM"
   v
measure_relvar.py (BATCH-9e3584, this batch's ROUTE-P)
   |  "CARRIED VERBATIM"
   v
replicate_l7l8.py (BATCH-4ed139, this batch's ROUTE-I for L7)
```

Two further facts sharpen this:

- **For `L7`, the two "routes" ran on the *same host*.** I read
  `results_l7l8.json`'s own `environment` block: `ENVIRONMENTS_DIFFER: false`,
  `matches_producer_field_by_field`: every field `true` (same OS string
  `Linux-6.18.5-fc-v20-x86_64-...`, same host `vm`, same Python 3.11.15, same
  numpy/scipy/fpylll versions as `results_relvar.json`). The L7 `ROUTE-I` is
  the same verbatim code re-run in a fresh virtualenv **on the same
  machine**, not a cross-environment reproduction. `replicate_l7l8.py`'s own
  docstring is explicit about what this is for: *"THIS RESTORES THE COVERAGE
  WAVE 2 LOST and is NEVER to be presented as resolving a doubt, THERE BEING
  NONE TO RESOLVE... If the values reproduce, that is a replication of a
  quantity nobody doubted."* Repurposing that reproduction check as a
  `D_route` disagreement **floor** for a *new* use (whether fibre dispersion
  exceeds it) inherits that limitation without restating it.
- **For `L9`/`L11`, `results_am4.json` genuinely ran on a different host**
  (macOS vs Linux) — but it runs the **same carried-verbatim code**, so
  environment diversity does not establish algorithmic independence, and this
  goal's own binding carry already bars over-reading a cross-platform match:
  `PREREG-1` 11.1, carried at `PREREG-3` section 7, states *"the 'genuinely
  cross-platform' reading of the L7/L8 agreement is NOT CITABLE."* The lead's
  own `report_c3lane.md` (obligation 0 item 3) writes: *"This is a genuinely
  independent computation: measure_am4.py... the same pipeline shape as
  measure_relvar.py's, but executed in a different environment."* "The same
  pipeline shape" is a considerable understatement of what my diff shows
  (byte-for-byte identical construction and reduction code), and "genuinely
  independent computation" is not supported by environment diversity alone
  given that understatement — this is the one place in the report where
  language creeps past what the evidence shown supports. **This is a FINDING,
  not a fabrication**: nothing here was invented; the report's own citations
  (`results_am4.json`, `measure_relvar.py`) are genuine, but the
  characterization of what they jointly show is stronger than warranted.

**Does this move the termination branch toward `T-C3LANE-NODATA`?** I do not
think so, and I am not arguing for that. `PREREG-3` section 3.1 itself
discloses, in its own definition of `ROUTE-I` for L7, that the comparison
"ran the frozen HKZ pipeline" — so the code-sharing fact was not hidden at
the pre-registration level, only under-weighted in the producer's later
characterization of the L9/L11 check specifically. `PREREG-3`'s literal
definition of `ROUTE-I` is satisfied by a re-run of the frozen pipeline in a
fresh install; `COVERED` is genuinely non-empty under that definition, so
`T-C3LANE-NODATA` does not fire. **The narrowest correct statement is not
"no route exists," it is "the reported `D_route` measures cross-environment
reproducibility of one shared deterministic pipeline, not disagreement
between two independently designed computations,"** and `T-C3LANE-OPEN`'s
already-narrow license ("a domain worth stating... nothing stronger") should
be read with that caveat attached, which nothing in this batch's committed
artifacts currently states.

---

## 2. NULL-OBJECT CALIBRATION CONTROL — built, not proposed

Per the task card's own suggestion, I built a control using `rdet`, an `A-1`
IN-SCOPE candidate that is **not** one of `{lam1n, hkz, rawtail}`
(`probes/probe_route_independence.py`, section 3; output in
`probes/probe_route_independence_output.json`). I computed `D_route(rdet)` at
`L11`, basis index 0, comparing `results_relvar.json` (`ROUTE-P`, Linux)
against `results_am4.json`'s `probe_L_supplementary` block (a **genuinely
different host**, macOS — this is real cross-machine data, not the same-host
L7 case) — using the corpus's own `rdet_of`/`build_basis` code (also carried
verbatim across these files).

**Result: `D_route(rdet) = 0.0` exactly (bit-identical),** confirming the
"same shared code -> `D_route` -> 0" mechanism generalizes beyond
`lam1n`/`hkz` to a candidate nobody in this goal is disputing.

**However, this control does not complete cleanly**, and I report this
against my own thesis, at the same weight as the finding above: `rdet`'s own
fibre dispersion (`s_c^fib`) is **also exactly 0.0** at every cell I checked
(`float_sd: 0.0`, `bit_identical: true`, from `results_relvar.json`'s own
`G_VAR` block). This is because `|det B| = q^(d-k)` is algebraically
independent of the random matrix draw `A` — the same "forced by algebra"
phenomenon this goal's own `G_VAR`/`AM-11` machinery already documents for
`X_null`. So `rdet` **ties out** (`0.0 == 0.0` -> `"DOES NOT EXCEED"` under
`PREREG-3` 3.3's tie rule) rather than demonstrating a false-positive
`EXCEEDS`. I searched `results_relvar.json`'s own candidate list
(`["rdet", "lam1n", "hkz", "null", "rawtail"]`) for any candidate that is
simultaneously (a) not one of the three under scrutiny and (b) has genuine
non-zero fibre dispersion, and found **none** — `rdet` and `null` are both
algebraically forced to zero dispersion, and `lam1n`/`hkz`/`rawtail` **are**
the candidates under test. **This absence is itself a finding**: this corpus
contains no non-target calibration candidate with real fibre content to
demonstrate a false "`EXCEEDS`" directly; the mechanism is demonstrated
structurally (the code-identity diff, which applies regardless of which
candidate is plugged in) rather than by a second worked false-positive
example. A genuinely discriminating control would require either a
non-code-shared reduction implementation of `lam1n`/`hkz` themselves, or a
new frame-class candidate with real, non-forced dispersion that this corpus
does not currently have.

---

## 3. SECOND TARGET — the `results_am4.json` construction-comparability check

**The construction check itself is correct and I could not falsify it.** I
independently re-derived the four checks the lead's `obligation_0_am4_construction_check`
performs — `(d,k)` match, seed-formula match, AM-9 `k`-convention match, and
bit-identical basis-0 cross-check — directly from both files' own declared
fields, and got the same `ALL_CONSTRUCTION_CHECKS_PASS: true` verdict. This
is a real, falsifiable check (it compares actual computed numeric output, not
just metadata labels) and it would have failed had `results_am4.json` used a
different seed formula or `(d,k)` pair. **This is a place where the
producer's work holds up, reported at full weight.**

**But I found a genuine, previously-unflagged coverage/provenance defect
downstream of it** (`probes/probe_coverage_beta_mismatch.py`, output in
`probes/probe_coverage_beta_mismatch_output.json`). `results_am4.json`'s
`gates.<X>.G_REL1.all` block reports **one row per lattice**, at the two
`REL1_PAIR` endpoint betas only — for `L9` that is `(7, 22)`, for `L11` that
is `(10, 30)`. Both lattices' 3-point beta grids (`L9`: `{7,15,22}`, `L11`:
`{10,20,30}`) have a **middle beta that `REL1` never covers at all**
(`L9`: 15, `L11`: 20). `measure_c3lane.py` reads only `am4_row["X_lo"]`
(confirmed: `"X_hi"` does not appear anywhere in the committed
`measure_c3lane.py` — my probe greps the source directly) and then, in
`obligation_1_comparison`, reuses **that single beta_lo-based comparison
uniformly across all three beta cells of the lattice** for `hkz`.

I verified `hkz` genuinely depends on beta (unlike `lam1n`, which does not):
`results_am4.json`'s own `X_lo`/`X_hi` for `hkz` differ
(`L9`: `-0.3334` vs `-0.1125`; `L11`: `-0.4247` vs `-0.1310`), while for
`lam1n` they are bit-identical (as the lead's own construction check
correctly established). Consequence:

| defect | cells affected | severity |
|---|---|---|
| **Falsely marked `COVERED`** — no genuine `am4` value exists at this beta at all | `hkz/L9_b15`, `hkz/L11_b20` | the coverage table (`R-C-OUT-0`, a first-class deliverable per `PREREG-3` 3.2) reports `route_i_available: true` for a cell with **zero corresponding data** in `results_am4.json` |
| **Wrong beta cited** — a genuine `am4` value (`X_hi`) exists at this cell's own beta but was never read; the beta_lo comparison was substituted instead, unlabelled | `hkz/L9_b22`, `hkz/L11_b30` | the `route_i_source` field cites a comparison that is not the one for that cell |

I computed the **true** `beta_hi` comparison for both mislabelled cells
(`am4.X_hi` vs `relvar.G_REL1.hkz.<L>.per_basis[0].X_b`) and it is **also**
exactly `0.0` — so, on the evidence I could check, the mislabelling did not
flip any reported `D_route` value. This is therefore a **coverage-table /
provenance-labelling defect**, not (on what I could verify) a
verdict-flipping one. `lam1n`'s equivalent middle/hi-beta reuse is
**legitimate** and excluded from this finding: `lam1n` is verified
beta-independent (its `X_lo == X_hi` exactly), so any beta's comparison
genuinely is "the" comparison.

**Effect on the numbers.** Coverage `18/27` is overstated by at least 2
cells: a corrected genuine-per-cell coverage count is **16/27** for
`lam1n + hkz` (9 `lam1n` + 7 genuinely-covered `hkz`: `L7` all 3, `L9`
`b7`/`b22`, `L11` `b10`/`b30`), plus 2 cells whose cited source should be
corrected from `X_lo` to `X_hi` (numerically unchanged). **Effect on the
termination branch: none.** Even at 16/27, `SOME-EXCEEDS` still holds (all
16 genuinely-covered cells verdict `EXCEEDS`), so `T-C3LANE-OPEN-PARTIAL`
still fires and the `-PARTIAL` suffix was already applied. I am not arguing
for a different branch. I am reporting that `R-C-OUT-0`, which `PREREG-3`
3.2 explicitly designates a first-class, independently-checkable
deliverable, contains a real defect that should be corrected in a
superseding record.

---

## 4. THIRD TARGET — the `ROUTE-W` labelling discipline for `rawtail`

**Verified clean.** I read `results_c3lane.json` directly: the single
`rawtail/L7_b5` cell carrying a `ROUTE-W` value is stored under a distinct
key (`verdict_informational_only`, not `verdict`), is listed separately in
`R-C-OUT-2_aggregate.cells_route_w_excluded`, and is **not** counted in
`n_covered` (18), `coverage_fraction` (`18/27`), `n_exceeds` (18), or
`cells_exceeds`. `obligation_2_aggregate`'s Python only ever reads
`v.get("verdict")` (never `verdict_informational_only`) when building
`covered_cells`/`exceeds`, so the `ROUTE-W` cell is structurally excluded by
construction, not merely by a label a human could later misread. This
matches `PREREG-3` 3.1/3.3's requirement exactly. **No objection here,
reported at full weight against my own search for a defect.**

---

## 5. FOURTH TARGET — the termination clause's precedence

**Verified correct.** `obligation_3_termination_branch`'s logic checks
`n_covered == 0` (`NODATA`, does not fire — `n_covered=18`) before
`aggregate_verdict == "SOME-EXCEEDS"` (fires, `T-C3LANE-OPEN`) before
`"ALL-CLEAR"` (`T-C3LANE-OBSTRUCTED`, would not fire regardless since
`SOME-EXCEEDS` is checked first) — this correctly implements `PREREG-3`
3.5's stated precedence ("a single exceeding cell is sufficient to fire
`T-C3LANE-OPEN` and prevents `T-C3LANE-OBSTRUCTED`"). The `-PARTIAL` suffix
condition (`n_covered < n_total`, `18 < 27` -> `True`) is correctly applied.
I re-derived this branch independently from `results_c3lane.json`'s raw
per-cell verdicts without importing the producer's module and got the same
answer: `T-C3LANE-OPEN-PARTIAL`.

---

## 6. FIFTH TARGET — RC-1/RC-2 carried verbatim

**Verified correct.** I compared `report_c3lane.md`'s quoted RC-1 and RC-2
blocks against `PREREG-3` sections 1 and 2 character-by-character (modulo
markdown blockquote reflow, which does not change content). Both match
exactly. The report states plainly, in both cases, that no recomputation
occurred and that `measure_a1.py`/`results_a1.json`/`report_a1.md`
(commit `4e466c6bf221ea002fe84311baccdb816081a8cd`) were not edited or
re-run. No objection.

---

## 7. The `rawtail` rider (iv) exclusion — verified correct, against my own thesis

The dispatch instructions specifically directed me to attack whether the
lead's exclusion of `BATCH-4ed139/TASK-20260812-56b9da` (the
`RD_rawgso_no_reduction` rawtail recomputation) discards genuine independent
coverage. **I read `report_gvar2.md` and `results_gvar2.json` directly and
the exclusion is correct.** The producing report's own section A states, in
its own words: *"`raw_gso_logs` and `x_rawtail_of` are TRANSCRIBED VERBATIM
from BATCH-9e3584 `measure_relvar.py`"* and its own prediction register
labels the row *"P-V1 | CONSISTENCY CHECK (AM-15(a))"*, never a route or a
prediction — reproducing the committed values at 38/38 cells, max absolute
difference `0.0`, exactly the same "shared code, of course it reproduces"
pattern documented in Section 1 above. Treating this as a `ROUTE-I` would
have been the **same defect** I raise in Section 1, compounded. The lead's
decision to report it (with its path) but exclude it from the coverage
table is the correct call, and I record this as a finding **against** my
own thesis that this batch's obligation-0 search was inadequate — on this
specific point, it was not.

---

## 8. PREMATURE CLOSURE / OVER-CLOSURE CHECK

`T-C3LANE-OPEN-PARTIAL` licenses only *"a statement that 'a successor
assumption analogous to A-1... has a domain worth stating' -- and nothing
stronger."* I read `report_c3lane.md` end to end looking for language that
implies more than this. **I did not find a lane-closure or gate-replacement
overclaim** — the report explicitly declines to treat this as `A-1` held,
declines to propose a criterion, and restates the full scope disclaimer
(no `ML-KEM`, no FIPS 203, no attack cost, no cost model) at its close. This
is a genuine finding in the report's favor.

**What I do find is a narrower version of the same problem, one level down:**
the report's characterization of the L9/L11 `results_am4.json` check as *"a
genuinely independent computation"* (Section 1 above) is language stronger
than the underlying code supports, and it feeds directly into the evidential
weight a reader assigns to `T-C3LANE-OPEN` firing at all — not into the
branch's stated *license*, but into how much a reader should trust that the
branch fired for a substantive reason rather than a methodological artifact.
`PREREG-3`'s own text is more careful than the lead's report here: it
describes the L7 route as running "the frozen HKZ pipeline" (disclosing the
shared code) and explicitly flags `results_am4.json`'s comparability as
"genuinely open pending the lead's own... check," never asserting
independence itself. The overclaim is local to the lead's report, not to
`PREREG-3`.

---

## 9. Attacking `PREREG-3` 3.6's reasoning on the `PREREG-2` 7.5 repair bar

`PREREG-3` 3.6 argues part (c) is not an eighth consecutive gate repair
because (1) it specifies no criterion/clause/gate for future reuse, (2) it
measures a class `A-1` never touched, (3) its outcome is a measurement
result, not a repaired gate's pass/fail. **I accept the conclusion — I do
not think this batch should be scored as an eighth gate repair — but the
argument understates something worth naming.** The *internal mechanism* of
obligation 1 (compare a dispersion statistic, `s_c^fib`, against a reference
noise floor, `D_route`, and emit a binary `EXCEEDS`/`DOES-NOT-EXCEED`
verdict with an explicit tie-breaking rule) is **structurally identical in
kind** to the `G_VAR`/`G_REL` dispersion-vs-floor family this goal has
already repaired seven times. `PREREG-3` 3.6's defense rests entirely on the
claim that the *output* is not reused as a gate against future candidates —
which is true and is the correct distinguishing test for "is this a repair"
— but it is a different claim from "this measurement's internal logic is not
a dispersion criterion," which is not quite true, and the text's phrasing
("It specifies no criterion, clause or gate") could be read to imply the
latter. Because the mechanism is the same *kind* of test, the same scrutiny
this goal has repeatedly had to apply to *floor/threshold choice* in the
retired `G_VAR`/`G_REL` family (units mismatches, `k`-convention, forced
zeros, the `max(|X|,s_X)` floor problem `RT-A2` found in `BATCH-cbe023`)
should have applied here to `D_route` as a floor choice — and it did not:
nothing in `PREREG-3` or the lead's report checks whether `D_route` is a
*meaningful* floor before comparing `s_c^fib` against it. Section 1 of this
report supplies exactly that missing check, and the answer is that it is
not a meaningful floor for this purpose in this corpus. **I am not
recommending this measurement be treated as a gate repair, and I am not
asking for `PREREG-2` 7.5's repair bar to apply retroactively** — I am
saying `PREREG-3` 3.6's argument would be stronger if it acknowledged the
mechanism's kinship to the retired family explicitly, rather than resting
solely on "no future reuse."

---

## 10. Cheapest falsification of each headline, with its cost

| headline | cheapest falsification | cost | status |
|---|---|---|---|
| "`ROUTE-I` is an independent second computation" | read+diff `make_A`/`build_basis`/`hkz_profile` across the 3 producing scripts | minutes, zero compute | **DONE — falsified**: byte-identical algorithm, self-declared "CARRIED VERBATIM" |
| "`D_route=0.0` reflects clean, well-behaved observables" | compute `D_route` for a non-target candidate (`rdet`) via the same cross-host methodology | one JSON read + arithmetic, seconds (**measured**) | **DONE — falsified as stated**: `D_route(rdet)=0.0` too, but `rdet`'s own `s_c^fib=0.0` (forced by algebra) so this specific control ties out rather than demonstrating a false EXCEEDS |
| "coverage is 18/27, each covered cell independently checked at its own beta" | grep `measure_c3lane.py` for `X_hi`; cross-check `REL1_PAIR` betas against each lattice's 3-point grid | one grep + arithmetic, seconds (**measured**) | **DONE — falsified**: `X_hi` never read; 2 cells (`hkz/L9_b15`, `hkz/L11_b20`) have no genuine per-beta comparison at all |
| "`ROUTE-W`/transcribed rawtail sources are correctly excluded" | read `report_gvar2.md`'s own self-labelling and `results_c3lane.json`'s tally logic | minutes | **DONE — held up**: both exclusions verified correct |
| "the termination branch fired correctly" | re-derive `R-C-OUT-2`/`R-C-OUT-3` from raw per-cell verdicts without importing the producer's module | seconds | **DONE — held up**: `T-C3LANE-OPEN-PARTIAL` reproduces |
| the STRONGER, not-yet-run falsifier of the whole `D_route` mechanism | commission a genuinely non-code-shared reduction implementation (different library or from-scratch enumeration, no reference to `measure_am4.py`/`measure_relvar.py`) of `lam1n`/`hkz` at `L7`/`L9`/`L11`, and re-run the same comparison | a fresh small-lattice reduction implementation (hours of dev; runtime itself is seconds at `d<=40`) | **NOT RUN, by anyone, in this corpus's history** |

---

## 11. The arrangement in which each obligation could not have failed — both directions

**Obligation 0 (coverage audit).**
*Could-not-PASS* (finds nothing regardless of what exists): would require an
excluded read scope; `PREREG-3` 5.2 already checked this and the lead's
`read_scope` includes all of `GOAL-MLKEM-005` — **not in this arrangement**.
*Could-not-FAIL on the per-beta granularity specifically*: the code sets
`route_i_available` **once per (candidate, lattice)**, from a single
beta_lo-based flag, then applies it uniformly to every beta of that lattice
— for `hkz`, this **structurally could not discover** that a specific beta
(the middle one) has no data, because no per-beta check was ever attempted
at that level. **This arrangement fired**, and is exactly Section 3's
finding.

**Obligation 1 (dispersion-vs-disagreement comparison).**
*Could-not-FAIL on `EXCEEDS` firing*: `PREREG-3` 5.1's own could-not-fail
check considered only "`D_route` defined so large" or "`s_c^fib` so small by
construction" as failure modes to rule out. It did **not** consider "`D_route`
forced toward 0 by code-sharing, regardless of the candidate," which is the
mechanism Section 1 demonstrates is actually in force **corpus-wide**
(confirmed for `rdet`, not just `lam1n`/`hkz`). Given `D_route ≈ 0` for
*every* candidate this corpus has ever compared this way, and given
`lam1n`/`hkz` are the *only* non-degenerate-dispersion candidates in
`results_relvar.json`'s own list (`rdet` and `null` are algebraically forced
to zero), `EXCEEDS` was close to structurally guaranteed for `lam1n`/`hkz`
under this methodology **before any cell was read** — not because of
anything specific to their information content, but because no comparison
in this corpus has ever been a genuine test of algorithmic independence.
**This arrangement fired.** This is the central objection of this report.

**Obligation 2 (aggregation).** No independent could-not-fail defect beyond
what it inherits from obligation 1: `SOME-EXCEEDS` is guaranteed once any
one cell reports `EXCEEDS` (by `PREREG-3`'s own falsifier-style design,
matching `A-1`'s "any one of `FC-2a`/.../`FC-3b`" logic) — the aggregation
arithmetic itself is mechanically sound and I found no defect in it
independent of obligation 1's structural bias.

---

## 12. Narrowest supported statement

`PREREG-3` part (c)'s mechanical protocol was followed correctly — modulo
the coverage-table beta-mismatch defect in Section 3, which changes the
genuine coverage count (18 -> 16 for the affected cells) but not the fired
branch — and `T-C3LANE-OPEN-PARTIAL` is the branch the frozen precedence
correctly fires from the reported numbers. I am **not** arguing for a
different branch and I am **not** calling this an instrument failure or an
impossibility result. What this measurement **establishes**: `lam1n` and
`hkz` have non-zero fibre dispersion (`s_c^fib > 0`, genuinely measured) that
is not detectably smaller than what this **specific** corpus's same-code,
cross-environment reproduction methodology can resolve. What it does **not**
establish, and what neither `PREREG-3`'s license nor the lead's report is
currently explicit enough about: that this dispersion would exceed a
**genuinely algorithmically independent** second computation's disagreement
— because no such computation exists anywhere in this corpus, for these
candidates or (per the `rdet` control) for any candidate this corpus has
ever tested this way. `T-C3LANE-OPEN`'s already-narrow license ("a domain
worth stating... nothing stronger") should be read narrower still: as a
statement about this corpus's reproducibility floor, not about `lam1n`/`hkz`
carrying fibre content beyond what a genuinely independent check would also
show.

## Next concrete action

Before any successor cites `T-C3LANE-OPEN-PARTIAL` for anything beyond a bare
"worth stating" note: (1) correct `R-C-OUT-0`'s coverage table in a
superseding record for the 2 falsely-`COVERED` cells (`hkz/L9_b15`,
`hkz/L11_b20`) and the 2 mislabelled-source cells (`hkz/L9_b22`,
`hkz/L11_b30`) — cheap, minutes, no new computation, uses this report's
probes directly. (2) Record, in the evidence/decision record this batch's
ledger archive produces, an explicit caveat that `ROUTE-I` in this batch is
a same-code reproduction (not an algorithmically independent implementation)
at every covered cell, citing this report's code-identity finding, so a
future reader does not conflate `SOME-EXCEEDS` with cross-algorithm
agreement. (3) The decisive, higher-cost follow-up, not yet run by anyone:
commission a genuinely non-code-shared reduction implementation of
`lam1n`/`hkz` (different library, or a from-scratch enumeration written
without reference to `measure_am4.py`/`measure_relvar.py`) at `L7`/`L9`/`L11`
and re-run this exact comparison — if `D_route` stays at machine-epsilon
scale, that is real evidence the observables are numerically well-behaved
under independent recomputation; if it grows toward `s_c^fib`'s scale, the
`EXCEEDS` verdicts reported here were a methodological artifact, not a
finding about `lam1n`/`hkz`.

---

## What I am NOT saying

* I am not calling `T-C3LANE-OPEN-PARTIAL` wrong or arguing for a different
  branch; `PREREG-3`'s frozen precedence fires it correctly from the
  reported numbers, and I independently re-derived that.
* I am not rejecting this measurement for being conditional, bounded, or
  partial-coverage; `PREREG-3` 3.5's `-PARTIAL` suffix rule anticipated
  exactly this and I am not treating partial coverage as a defect in itself.
* I am not calling this an eighth gate repair, and I accept `PREREG-3`
  3.6's conclusion even while pushing on its argument (Section 9).
* Sections 4, 5 and 6 above are clean audits with no objection — the
  termination-clause precedence, the RC-1/RC-2 carry, the `ROUTE-W`
  labelling discipline, and the rawtail-transcription exclusion all held up
  under independent re-derivation and are reported at full weight in the
  producer's favor.
* `AM-3` is not retired here; `BATCH-a44d08` is not rescored; `BATCH-4ed139`,
  `BATCH-9e3584`, `BATCH-cbe023` and `BATCH-6b6e78` are not revalidated by
  anything in this report. `KN-FIND-7d098b` and `KN-FIND-9d44b4` are not
  restated as new. Claim tier TOY, unconditionally, throughout.

**No commit was made. No producer artifact was modified. No ledger record
was touched.**

---

```yaml
red_team_report:
  id: RT-20260813-6ab893
  task_id: TASK-20260813-6ab893
  claim_under_review: >-
    BATCH-fbb639 part (c)'s headline: two-route dispersion comparison over
    lam1n/hkz/rawtail at L7/L9/L11 finds D_route = 0.0 (bit-identical) at
    every one of 18 covered cells while s_c^fib > 0 at all 18, firing
    T-C3LANE-OPEN-PARTIAL ("a successor assumption analogous to A-1... has a
    domain worth stating -- and nothing stronger").
  objections:
    - id: RT-1
      severity: CRITICAL
      target: "ROUTE-I independence (obligation 0/1 for L7 AND L9/L11)"
      statement: >-
        make_A, build_basis and hkz_profile are byte-identical algorithms
        (confirmed by direct diff) across measure_am4.py (BATCH-cbe023),
        measure_relvar.py (ROUTE-P, BATCH-9e3584) and replicate_l7l8.py
        (ROUTE-I/L7, BATCH-4ed139), self-declared "CARRIED VERBATIM" in the
        two later files' own docstrings; measure_am4.py, cited as ROUTE-I
        for L9/L11, is the literal ancestor measure_relvar.py's own
        reduction code was copied from. For L7 the two "routes" additionally
        ran on the SAME host (results_l7l8.json's own environment block:
        ENVIRONMENTS_DIFFER: false). D_route = 0.0 at 18/18 covered cells
        therefore measures cross-environment/re-install reproducibility of
        one shared deterministic pipeline, not disagreement between two
        independently designed computations. The lead's report calls the
        L9/L11 am4 check "a genuinely independent computation" -- language
        stronger than the underlying code supports.
      evidence: >-
        probes/probe_route_independence.py +
        probes/probe_route_independence_output.json
    - id: RT-2
      severity: MAJOR
      target: "obligation 0's coverage table (R-C-OUT-0) for hkz at L9/L11"
      statement: >-
        results_am4.json's G_REL1 block reports hkz only at the two REL1_PAIR
        endpoint betas per lattice (L9: 7,22; L11: 10,30), never the middle
        beta (L9:15, L11:20); measure_c3lane.py never reads "X_hi" (confirmed
        by direct grep) and reuses the single beta_lo comparison across all 3
        betas of each lattice. hkz IS beta-dependent (am4's own X_lo != X_hi:
        L9 -0.3334 vs -0.1125; L11 -0.4247 vs -0.1310), unlike lam1n (X_lo ==
        X_hi exactly, so lam1n's equivalent reuse is legitimate). Result: 2
        cells (hkz/L9_b15, hkz/L11_b20) are falsely marked COVERED with no
        genuine per-beta am4 value at all; 2 more cells (hkz/L9_b22,
        hkz/L11_b30) cite the wrong beta's comparison as their D_route
        source. I computed the TRUE beta_hi comparison for the latter two and
        it is also exactly 0.0, so no reported D_route value is numerically
        wrong on the evidence checked -- this is a coverage/provenance defect
        in a PREREG-3-3.2-designated first-class deliverable, not (as far as
        I could verify) a verdict-flipping one. Corrected genuine coverage is
        16/27, not 18/27; the fired branch (T-C3LANE-OPEN-PARTIAL) is
        unchanged.
      evidence: >-
        probes/probe_coverage_beta_mismatch.py +
        probes/probe_coverage_beta_mismatch_output.json
    - id: RT-3
      severity: MINOR
      target: "PREREG-3 3.6's argument that part (c) is not a gate repair"
      statement: >-
        The argument correctly shows the measurement's OUTPUT is not reused
        as a future gate, which is the right test for "is this a repair" --
        but its phrasing ("specifies no criterion") understates that the
        measurement's INTERNAL mechanism (compare a dispersion statistic to
        a reference floor, emit a binary verdict with an explicit tie rule)
        is structurally the same kind of test as the retired G_VAR/G_REL
        family. That kinship is exactly why D_route as a floor choice
        deserved the same scrutiny this goal has repeatedly had to apply to
        floor/threshold choices (units, k-convention, forced zeros) -- and
        it did not get that scrutiny before this batch ran. RT-1 supplies
        the missing check. I am not asking for the repair bar to apply
        retroactively; I am asking that PREREG-3 3.6's defense be stated
        more precisely.
      evidence: "PREREG-3 section 3.6; this report's section 9"
  required_controls:
    - >-
      A genuinely non-code-shared reduction implementation of lam1n/hkz
      (different library, or a from-scratch enumeration with no reference to
      measure_am4.py/measure_relvar.py), re-run against the same L7/L9/L11
      cells, to establish what D_route looks like under actual algorithmic
      independence rather than shared-code reproduction. NOT RUN by anyone
      in this corpus's history.
    - >-
      A non-target candidate with genuine (non-algebraically-forced) fibre
      dispersion, to complete the calibration control RT-1's rdet check
      could not: rdet and X_null are the only non-target candidates in
      results_relvar.json's own list and both are forced to zero dispersion
      by algebra, so no clean false-positive demonstration is currently
      possible inside this corpus.
  counterexample_or_mutation: >-
    Built: D_route(rdet) at L11 basis 0, comparing results_relvar.json
    (Linux) against results_am4.json's probe_L_supplementary block (macOS,
    genuinely different host), using the corpus's own carried-verbatim
    rdet_of/build_basis code, gives D_route = 0.0 exactly -- the same floor
    the batch measured for lam1n/hkz, for a candidate nobody disputes. rdet's
    own s_c^fib is also exactly 0.0 (algebraically forced), so this control
    ties out rather than flips a verdict; reported against my own thesis at
    the same weight as the finding it partially supports.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS sense -- this batch performs no
    reduction and makes no attack-cost claim (claim tier TOY throughout).
    The relevant "baseline" here is methodological: a genuine second-route
    comparison would use an algorithmically distinct implementation, which
    this corpus has never produced for lam1n, hkz, or rawtail (or, per the
    rdet control, for rdet either) -- every "ROUTE-I" or consistency check in
    this goal's history to date (BATCH-4ed139's P-L1, BATCH-4ed139's
    RD_rawgso_no_reduction, this batch's am4 check) is a same-code
    reproduction, confirmed for three of them directly in this report.
  heuristic_challenges: []
  cost_model_challenges: []
  reduction_and_scope_challenges:
    - >-
      No reduction was performed by this task or its probes; fpylll is not
      imported anywhere in probes/. Confirmed by grep.
    - >-
      T-C3LANE-OPEN-PARTIAL's scope is exactly as PREREG-3 states (no A-1
      claim, no ML-KEM/FIPS-203/cost claim, no lane closure) -- verified
      clean, no overclaim found in report_c3lane.md's own scope language
      (section 8 of this report).
  proof_architecture_challenges: []
  narrowest_supported_statement: >-
    PREREG-3 part (c)'s mechanical protocol fires T-C3LANE-OPEN-PARTIAL
    correctly from the reported numbers (independently re-derived), modulo a
    coverage-table defect (RT-2) that narrows genuine coverage to 16/27
    without changing the branch. What is established: lam1n and hkz have
    non-zero fibre dispersion not detectably smaller than this corpus's own
    same-code, cross-environment reproduction floor. What is NOT established:
    that this dispersion would exceed a genuinely algorithmically independent
    second computation's disagreement -- no such computation exists anywhere
    in this corpus, for these candidates or (per the rdet control) for any
    candidate tested this way to date.
  next_concrete_action: >-
    Cheapest: correct R-C-OUT-0's coverage table for the 4 cells RT-2 names
    and add an explicit "same-code reproduction, not independent
    implementation" caveat to the evidence/decision record this batch's
    ledger archive produces, citing RT-1 -- minutes, no new computation,
    both probes in this report supply the exact corrected values. Decisive
    but higher-cost, not yet run by anyone: commission a genuinely
    non-code-shared reduction implementation of lam1n/hkz and re-run this
    comparison; if D_route stays near machine epsilon that is real evidence
    of well-behaved observables, if it grows toward s_c^fib's scale the
    EXCEEDS verdicts here were a methodological artifact.
  artifact_paths:
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-0eb5a3/prereg.md
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/archives/TASK-20260813-6ad846/snapshot-receipt.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/archives/TASK-20260813-7ac7cd/snapshot-receipt.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-7b3039/measure_c3lane.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-7b3039/results_c3lane.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-7b3039/report_c3lane.md
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-7b3039/run_manifest.yaml
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-0e930c/replicate_l7l8.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-0e930c/results_l7l8.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/TASK-20260809-cda2f6/measure_relvar.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/TASK-20260809-cda2f6/results_relvar.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/TASK-20260808-2a9085/measure_am4.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/TASK-20260808-2a9085/results_am4.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-56b9da/report_gvar2.md
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-56b9da/results_gvar2.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/reviews/TASK-20260813-6ab893/probes/probe_route_independence.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/reviews/TASK-20260813-6ab893/probes/probe_route_independence_output.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/reviews/TASK-20260813-6ab893/probes/probe_coverage_beta_mismatch.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/reviews/TASK-20260813-6ab893/probes/probe_coverage_beta_mismatch_output.json
```
