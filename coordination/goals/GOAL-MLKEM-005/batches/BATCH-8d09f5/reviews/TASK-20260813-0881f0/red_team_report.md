# Red team — BATCH-8d09f5: mutation-testing (positive) control on `D_route`/`D_route''`

`RT-20260814-ee142c` / `TASK-20260813-0881f0` / `BATCH-8d09f5` / `GOAL-MLKEM-005`.
Governed by `PREREG-6`
(`coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/tasks/TASK-20260813-4aec9a/prereg.md`),
notarized at commit `dcaac725f65da93c0ab27eeed970d6d10b2bcde1` (independently
confirmed below to be an ancestor of the reviewed snapshot and the sole
commit touching `prereg.md`). Reviews the lead producer
`TASK-20260813-630414`'s committed snapshot at commit
`e2ad28b3ffe90b2b5390ca83f4e2ba1d431399fd` (**snapshot archive
`TASK-20260813-cb8943`, 9 declared paths**).

**Claim tier TOY, unconditionally.** Nothing in this report bears on ML-KEM
security, any FIPS 203 parameter set, any attack cost, or any cost model. I
changed no research status, rescored no frozen verdict (`T-HKZINDEP-CONFIRMED`
not re-litigated; `AM-3` not retired; `lam1n`'s `T-INDVERIFY-CONFIRMED`
discharge not revisited — out of scope), modified no producer artifact, and
made no commit. `KN-FIND-7d098b`, `KN-FIND-9d44b4`, `KN-FIND-9b5df0`,
`KN-FIND-7de6b6` and `KN-FIND-d29ece` are cited, never restated as new.

## Inference record (AGENTS.md rule 12 / PREREG-6 section 5 disclosure)

```
requested_policy: review-adversarial
reasoning_effort: xhigh (per .claude/agents/red-team.md, role red-team's
  default_policy review-adversarial -> orchestration/model-policies.yaml)
fallback_allowed: false
degraded_allowed: false
independent_session_required: true (honoured: fresh Claude Code subagent
  invocation, independent of the Coordinator session that authored
  PREREG-6 and of the lead producer's TASK-20260813-630414 session)
model_that_answered: claude-sonnet-5 (per this session's own system
  context; NOT independently probe-verified)
model_verified: false
model_verified_reason: >-
  AGENTS.md rule 12 is UNMET AND UNWAIVED in this goal (PREREG-6 section 5,
  restated explicitly there to bind this batch's own reviews too, exactly
  as every prior review of this goal has recorded). No adapter probe
  receipt exists for this session.
host_measured: >-
  hostname "vm", platform "Linux-6.18.5-fc-v20-x86_64-with-glibc2.39",
  Python 3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0], numpy 2.4.6,
  fpylll 0.6.4, cysignals 1.12.5 -- ALL EIGHT of these values are
  IDENTICAL, character-for-character, to the lead producer's own recorded
  environment.json / run_manifest.yaml. Same convention as
  RT-20260813-7930a6 (BATCH-6e08fe) and the BATCH-a6fab5 red team used:
  this is very likely the SAME container/host as the producer, recorded
  plainly as a property of the sandboxed execution recipe, not a claim of
  shared process state -- but material to how much weight the "bit-exact
  reproduction" finding below (built control C) should carry: a shared
  host/library build makes bit-exact reproduction MORE likely by default,
  not evidence of independence by itself. I treat control (C) below as
  confirming *mechanical/arithmetic* correctness only, not as evidence of
  code-level independence (which this task does not claim and PREREG-6
  does not require of the reviewer).
```

## Commit verification (change-set equality, recomputed myself)

`git diff-tree --no-commit-id --name-only -r e2ad28b3f...` in this worktree
lists exactly 9 paths; I independently `sha256sum`'d each of the 8 paths
carrying a declared hash in the snapshot receipt (via `git show
<sha>:<path> | sha256sum`, reading from the git object database, not the
working tree) and they match the receipt's `path_sha256` block
character-for-character:

| path | my sha256 | receipt sha256 | match |
|---|---|---|---|
| `.../TASK-20260813-630414/command.txt` | `d7500c85...` | `d7500c85...` | yes |
| `.../TASK-20260813-630414/environment.json` | `764cc0b3...` | `764cc0b3...` | yes |
| `.../TASK-20260813-630414/hkz_mutation6_writeup.md` | `b8b47711...` | `b8b47711...` | yes |
| `.../TASK-20260813-630414/measure_hkz_mutation6.py` | `4fc2ee51...` | `4fc2ee51...` | yes |
| `.../TASK-20260813-630414/results_hkz_mutation6.json` | `a4ccb4a8...` | `a4ccb4a8...` | yes |
| `.../TASK-20260813-630414/run_manifest.yaml` | `c40bfa9a...` | `c40bfa9a...` | yes |
| `.../TASK-20260813-630414/stderr.log` | `e3b0c442...` (empty file) | `e3b0c442...` | yes |
| `.../TASK-20260813-630414/stdout.log` | `4c6c28c6...` | `4c6c28c6...` | yes |
| `.../archives/TASK-20260813-cb8943/snapshot-receipt.json` | (self; not self-hashed, 9th path) | n/a | consistent — `git diff-tree` also reports exactly 9 changed paths, 0 extra, 0 missing |

**Change-set complete, 9/9, 0 extra, 0 missing — confirmed independently,
not taken on the dispatching session's word.** `git log --oneline --all --
.../TASK-20260813-4aec9a/prereg.md` shows exactly one commit
(`dcaac725f`, the notarization) touches `prereg.md`, and
`git merge-base --is-ancestor dcaac725f... e2ad28b3f...` returns true —
the frozen text was fixed before any measuring task ran.

## Standard checks (task-card items 1-6, "also required")

1. **Detection-mapping / D_route_mut recomputation.** Recomputed
   `D_route_mut`/`VERDICT_mut`/`detection_reading` from the raw
   `route_p_values`/`route_mut_values`/`s_c_fib` arrays myself
   (`probes/rt_reverify.py`, section D). Result: `DOES NOT EXCEED` →
   `DETECTED` at both cells, matching the lead's own reported verdicts and
   detection readings exactly. The mapping (`DOES NOT EXCEED` = detected,
   `EXCEEDS` = not detected) is applied the right way round in the lead's
   report — I checked this is not inverted by re-deriving it from PREREG-6
   §2.4 point 5's prose independently, not by trusting the lead's restated
   sentence.
2. **Change-set completeness.** See above — 9/9 paths, all hashes
   independently recomputed and matched.
3. **AGENTS.md rule 12 disclosure.** See "Inference record" above —
   `model_verified: false`, same host/stack as the producer, recorded
   plainly.
4. **Termination branch, re-derived mechanically.** `COVERED` = 2/2 (both
   cells produced a status-`ok` `D_route_mut`) → `T-MUTCTRL-NODATA` does
   not fire. `|COVERED| = 2`; `T-MUTCTRL-MIXED` is checked first per
   PREREG-6's stated precedence and does not fire (`DETECTED_SET` = both
   cells, `NOT_DETECTED_SET` = empty — they agree). Both cells
   `DOES NOT EXCEED` → **`T-MUTCTRL-DETECTED` fires, unsuffixed**. This
   matches the lead's own `R_MC_OUT_4_termination` exactly. I re-derived
   this from `R_MC_OUT_2_per_cell`'s raw `VERDICT_mut` fields directly,
   not from the lead's own `R_MC_OUT_4_termination` block.
5. **`results_l7l8.json`/`results_am4.json` never used; no `d>40`
   anywhere.** `grep` of `measure_hkz_mutation6.py`,
   `hkz_mutation6_writeup.md` and `run_manifest.yaml` for
   `results_l7l8|results_am4` finds only one hit, in the write-up's own
   negative statement ("never `results_l7l8.json`/`results_am4.json`") —
   no actual reference to either file exists anywhere in the code or
   manifest. The only external data source used is `results_relvar.json`
   (BATCH-9e3584/TASK-20260809-cda2f6), read-only, sha256 independently
   re-verified as `c5b2918d...`, matching PREREG-6 §2.1's declared value.
   `CELLS` in `measure_hkz_mutation6.py` covers exactly `d ∈ {20, 40}`; no
   `d > 40` literal or computed dimension appears anywhere in the script.
6. **PREREG-6 §2.1's cell-selection rationale, checked directly — FALSE AS
   STATED.** See the headline finding below; this is folded into MAJOR-2.

## Target 1 — mechanical diff, built independently, not trusted from the lead

I wrote a second, structurally different extractor
(`probes/rt_reverify.py`, function `extract_functions_regex`, a
line-scanning regex extractor rather than the lead's `ast`-based one),
extracted the same four function pairs from both files, normalized away
the `_mut` suffix / default-arg cosmetic renames, and diffed line-by-line:

```
n_functional_differing_lines_after_cosmetic_normalization = 1
expected_exactly_one_functional_change = True
single_diff_is_the_declared_seed_shift = True
frozen_reference_sha256_live  = 74875b4197cee69dc78c2999f9f60f27b678da3159c6cdd0bbc7039a4fb09096
frozen_reference_sha256_declared_by_lead = 74875b4197cee69dc78c2999f9f60f27b678da3159c6cdd0bbc7039a4fb09096
frozen_reference_untouched = True
```

**Confirmed, by a from-scratch method, not by re-reading the lead's own
`difflib` output: exactly one functional line differs
(`rng = np.random.default_rng([1, d, k, i])` →
`rng = np.random.default_rng([1, d, k, (i + 1) % n_bases])`), and
`measure_hkz_indep.py`'s own committed bytes are untouched.** No CRITICAL
finding on this target.

## Target 2 — independent `fpylll`/`cysignals` re-verification, this session

`import fpylll, cysignals` succeeded in this red-team session:
`fpylll.__version__ = "0.6.4"`, `cysignals` reports `"unknown"` from its
own attribute but `pip freeze` shows `cysignals==1.12.5` — identical to
the lead's own re-verification and to `PREREG-5`/`PREREG-6`'s prior
history. Reported plainly as infrastructure signal only, per `AGENTS.md`
rule 5: `T-MUTCTRL-NODATA` branch (b) does not fire, independently
confirmed in this session, not merely inherited from the lead's report.

## Target 3 — frozen prediction and `HEURISTIC-M1`

Recomputed the frozen prediction directly from `results_relvar.json`'s own
`G_REL1.hkz.L7/L11.per_basis[i].X_a/X_b` arrays (`probes/rt_reverify.py`,
section B): `hkz/L7_b5 = 0.0665893489077094`,
`hkz/L11_b30 = 0.00948000985335451` — bit-exact matches to both PREREG-6's
stated numbers and the lead's own independent recomputation. `basis_status`
in the lead's own results is `"ok"` for 8/8 bases at both cells — no
convergence failure occurred, and none was silently merged or defaulted
(I checked every entry of `basis_status`, not just the summary count).
**`HEURISTIC-M1` held cleanly at both cells; the measured `D_route_mut`
does not diverge from the frozen prediction (residual ≤ ~1.8e-15,
discussed below) — there is no convergence-failure explanation to weigh
against an instrument-behaved-differently explanation, because neither
alternative is needed here.**

## Target 4 — built control: does `ROUTE-MUT` genuinely compute a mislabeled `(i+1)`?

This is the specific, falsifiable claim the task card asks to check, not
just "some big number." I read `measure_hkz_indep.py`'s text (never
edited) and `exec`'d it into an isolated namespace so I could independently
call **its own, unmutated** `route_ii_build_basis` / `hkz_route_ii` /
`route_ii_hkz_value` on shifted index `(i+1) mod 8`, for every matched
basis at both cells, and compared the result against (a) the mutant's own
reported `route_mut_values[i]` and (b) `ROUTE-P`'s own archived value at
slot `(i+1) mod 8` (`probes/rt_reverify.py`, section C; raw output in
`probes/rt_reverify_results.json`):

| cell | max\|my recompute − lead's `route_mut_values`\| | max\|my recompute − archived `ROUTE-P[(i+1)%8]`\| |
|---|---|---|
| `hkz/L7_b5`   | **0.000e+00 (bit-exact)** | 1.776e-15 |
| `hkz/L11_b30` | **0.000e+00 (bit-exact)** | 1.776e-15 |

The bit-exact match against the lead's reported values (same host/library
build, see the inference-record caveat above) confirms the arithmetic is
exactly reproducible; the `1.776e-15` residual against `ROUTE-P`'s own
already-archived value is the identical machine-epsilon floor
`BATCH-a6fab5` established for genuine convergence, now independently
extended to basis index `(i+1) mod 8` at these two cells specifically.
**Confirmed: mutant slot `i`'s HKZ value equals a genuine HKZ-quality
computation of `ROUTE-P`'s own slot `(i+1) mod 8`, to within the same
floor as every other correctly-converged comparison in this lineage — not
"some big number," and not an artifact of the lead's own mutant-writing
process. The mutation does exactly what PREREG-6 §2.2 claims and nothing
more.**

I additionally re-ran the lead's own unmodified `measure_hkz_mutation6.py`
fresh, in this session, to a separate output path
(`probes/rt_rerun_lead_script_results.json`) rather than overwriting the
lead's own file. `R_MC_OUT_2_per_cell`, `R_MC_OUT_3_aggregate` and
`R_MC_OUT_4_termination` are **identical, field-for-field**, between the
lead's committed run and my fresh re-run (`command:
python3 .../measure_hkz_mutation6.py --out
.../probes/rt_rerun_lead_script_results.json`). The result is genuinely
reproducible, not a one-off artifact of a single invocation.

## MAJOR-1 — the "positive detection" margin is a near-tautology of the comparison's own arithmetic, not a demonstration of instrument sensitivity

This is the task card's central named target (item (d)) and, on
investigation, the load-bearing finding of this review.

**The relation, checked directly, not conjectured.** `s_c^fib(hkz,L,b)` is
`results_relvar.json`'s own `G_VAR...float_sd` field. I confirmed by direct
recomputation that this is exactly `numpy.std(X, ddof=1)` of the *same*
8-element per-basis array `X` that PREREG-6 §2.3's frozen prediction reads
its cyclic-adjacent-max-difference from (`std(X_a[L7], ddof=1) =
0.023887966155964283`, bit-exact to the archived `s_c^fib`, likewise for
`X_b[L11]`). **Both quantities being compared — the predicted/measured
`D_route_mut` and the threshold `s_c^fib` it is checked against — are two
different functionals of the identical 8-number array.**

**Null-object control (`probes/rt_reverify.py`, section E; 200,000 trials
per distribution, `n=8`, no lattice, no `fpylll`, no HKZ, nothing about
this problem at all):**

| distribution | P(max cyclic-adjacent \|diff\| > sample std) | mean ratio | median ratio |
|---|---|---|---|
| Normal(0,1) | 0.99998 | 2.496 | 2.495 |
| Uniform(0,1) | 0.99999 | 2.423 | 2.426 |
| Student-t(df=3) | 0.99999 | 2.569 | 2.574 |

**All 6 of `BATCH-a6fab5`'s own archived `hkz` cells' real ratios**
(`max_cyclic_diff / s_c^fib`, computed directly from the same
`results_relvar.json`): `L7_b5 = 2.788`, `L7_b15 = 2.555`,
`L9_b7 = 2.341`, `L9_b22 = 2.369`, `L11_b10 = 2.287`, `L11_b30 = 2.483` —
**every one of them falls inside the null-object control's central band**
(mean/median ≈ 2.4–2.6, generic to *any* n=8 sample with non-degenerate
dispersion), indistinguishable from noise unrelated to lattices, `q`,
dimension, or `fpylll` at all.

**What this means, stated narrowly.** The seed-index-off-by-one defect
class, by construction, produces `route_mut_values[i] = f(A(i+1))` for the
*same* per-basis functional `f` that produced `ROUTE-P`'s own archived
values — i.e., the injected "defect" is mathematically indistinguishable,
from `D_route_mut`'s point of view, from *just picking a different one of
the 8 already-archived basis-to-basis comparisons*. Because `s_c^fib` is
the standard deviation of that same 8-number set and `D_route_mut`
(predicted) is the maximum of 8 cyclic pairwise differences of it, the
ratio between them is an order-statistic fact (`max` over `n=8` samples vs
`std` of the same `n=8` samples) that holds for **essentially any**
continuous distribution with non-trivial dispersion, independent of
`fpylll`, HKZ reduction, or lattice dimension entirely. **The "detected"
outcome was overwhelmingly likely (empirically ≥99.998%, matching the
observed real-cell range almost exactly) before any lattice reduction ever
ran, given only that the defect swaps in a genuinely different
(correctly-computed) basis's value.** This directly answers task item (a):
**2.5–2.8x is a soft test, not a demanding one** — it does not probe
anywhere near the boundary between "detected" and "not detected"; it
probes a region the comparison's own construction makes almost impossible
to land outside of, for this entire defect *class*, regardless of which of
the 6 archived cells (or any future cell of this same family) a document
chooses.

**Quantitative distance from the actual boundary.** `BATCH-a6fab5`'s own
genuine (unmutated) `D_route''` at these same two cells is `1.7764e-15`
(`results_hkz_indep.json`, `R_V_OUT_2_per_cell`), i.e. a ratio to
`s_c^fib` of `7.44e-14` (`L7_b5`) and `4.65e-13` (`L11_b30`) — **~13–14
orders of magnitude below** threshold. The injected defect lands
**~2.5–2.8x above** threshold. Nothing in this document, or in this
defect class, probes the ~13-order-of-magnitude gap in between; the two
data points that exist (genuine agreement, injected swap) sit at opposite
extremes with nothing tested near the boundary that actually determines
whether the mechanism has real sensitivity to a *subtle* shared-code
defect (a small arithmetic slip, a rounding truncation, an off-by-one
affecting one matrix entry) — exactly the kind of bug `KN-FIND-d29ece`
was concerned about, and exactly the kind this document's own defect
*class* structurally cannot produce a small-magnitude instance of.

**This is not a rejection of the branch call.** `T-MUTCTRL-DETECTED` fired
correctly and mechanically on genuinely, independently reproduced data
(Target 4 above), and PREREG-6's own FORBIDS list for that branch is
already reasonably narrow (no generalization to other defect classes,
cells, or magnitudes is licensed). The objection is to how much the
*narrower* LICENSES clause — "a positive calibration result ... at THIS
approximate magnitude" and "the instrument is not blind to every
conceivable shared-code defect, at least not one of this shape and size"
— can honestly be read to establish. The demonstrated fact is closer to
"the comparison mechanism is not fixed-by-construction to always read
`EXCEEDS`, and correctly reports a basis-mislabeling as a discrepancy" —
already covered by PREREG-6 §3.1's own could-not-fail check — than to "the
mechanism has demonstrated sensitivity at a magnitude that meaningfully
probes its detection threshold."

## MAJOR-2 — PREREG-6 §2.1's own stated cell-selection rationale is false when checked directly

PREREG-6 §2.1 states the two cells were chosen to "bracket ... the
tightest and a looser predicted signal-to-`s_c^fib` ratio among the 6
covered cells, so the test is not accidentally calibrated to its easiest
case alone." Task item 6 asks this be checked by direct arithmetic on
already-archived data. Result (table above, `probes/rt_reverify.py`
section E, `real_hkz_cells`):

- **Tightest ratio among all 6 archived cells: `hkz/L11_b10` (2.287x) —
  NOT one of the two tested cells.**
- **Loosest (largest, easiest-to-detect) ratio among all 6: `hkz/L7_b5`
  (2.788x) — IS one of the two tested cells.**
- `hkz/L11_b30` (2.483x) sits in the middle of the 6-cell range (3rd
  loosest / 4th tightest), neither extreme.

So the two tested cells do **not** bracket the tightest-and-a-looser pair;
one of them (`hkz/L7_b5`) is literally the single loosest/easiest cell of
the entire archived 6-cell set, and the genuinely tightest cell
(`hkz/L11_b10`) was left untested. Given MAJOR-1's finding that this whole
ratio band (2.29x–2.79x) is itself indistinguishable from generic n=8
noise, this particular mis-statement does not change the outcome (every
untested cell's real ratio also sits inside the same null-object band, so
testing `L11_b10` instead would very likely also have read `DETECTED`) —
but the stated rationale ("not accidentally calibrated to its easiest case
alone") is factually incorrect as written, and should be corrected or
retracted in any future citation of PREREG-6 §2.1, rather than repeated.

## FORBIDS compliance (§2.6 / §2.8 / §6)

Read the lead's `hkz_mutation6_writeup.md` in full against PREREG-6's
FORBIDS lists. No claim about `hkz`'s own admissibility is made; the
writeup explicitly defers admissibility judgments and states the outcome
"says nothing about `hkz`'s admissibility." `T-HKZINDEP-CONFIRMED` is
cited but not re-scored or re-litigated (the writeup explicitly states its
outcome does not touch it either way). No `ML-KEM`/FIPS-203/attack-cost/
cost-model claim appears anywhere. No `GOAL-MLKEM-005` status claim is
made — the writeup explicitly defers that judgment to the Coordinator.
**Compliant.**

## Objections

- **MAJOR** (see MAJOR-1 above): the injected defect's measured margin
  over `s_c^fib` (~2.5–2.8x) is statistically indistinguishable from what
  a null-object control (iid random n=8 samples, no lattice/HKZ/fpylll
  content) produces with probability ≥99.998%, because both `D_route_mut`
  (predicted) and `s_c^fib` are functionals of the *same* archived
  8-element array. "Detected" for this defect class was near-certain
  before any reduction ran; the result demonstrates the comparison
  mechanism is not broken/fixed-by-construction, but does **not**
  demonstrate meaningful sensitivity near a real detection boundary — the
  genuine (unmutated) agreement sits ~13–14 orders of magnitude below
  threshold and the tested defect sits ~2.5–2.8x above it, with nothing
  tested in between.
- **MAJOR** (see MAJOR-2 above): PREREG-6 §2.1's stated cell-selection
  rationale ("bracket the tightest and a looser ratio ... so the test is
  not accidentally calibrated to its easiest case alone") is false by
  direct computation: the tested `hkz/L7_b5` is the single loosest cell of
  the archived 6, and the genuinely tightest cell (`hkz/L11_b10`) was not
  tested.
- **MODERATE**: PREREG-6 §2.6's declared forward boundary (bar further
  seed-index-off-by-one tests at these two cells; require a "genuinely
  DIFFERENT defect class" for further probing) should be strengthened with
  the reasoning from MAJOR-1: it is not merely that *these two cells* are
  exhausted — the entire seed-index/basis-swap defect *class*, at *any*
  cell of this lattice family, is structurally incapable of producing a
  magnitude appreciably below ~1.8x `s_c^fib` (the null-object control's
  5th percentile), so it cannot ever be used to probe the mechanism's
  small-defect sensitivity boundary, independent of which cell a future
  document might pick. This is forward guidance the current text does not
  give, and a future Coordinator relying on PREREG-6's own text alone
  could otherwise recommission the same defect *class* at a different cell
  expecting a more informative result.
- **MINOR**: PREREG-6's/the writeup's repeated phrase "at THIS approximate
  magnitude" (used to scope what `T-MUTCTRL-DETECTED` licenses) invites a
  reading in which the tested magnitude is an independent, meaningful
  parameter of the defect. MAJOR-1 shows it is not, for this defect class;
  a future citation should read the licensed claim as "against a defect
  that substitutes one archived basis's correctly-computed value for a
  different one," not "against a defect of magnitude ~2.5–2.8x `s_c^fib`"
  — the latter phrasing implies a controllable/informative dial that this
  defect construction does not actually provide.
- No objection to the mechanical correctness of the run: diff, prediction
  recomputation, shift mechanism, `D_route_mut`/`VERDICT_mut` computation,
  detection mapping, and termination-branch precedence all independently
  reproduced, bit-exact where checkable (Targets 1–4, "Standard checks").

## Required controls

1. **Already run, reported above**: null-object control (iid n=8 samples
   vs. `max`-cyclic-diff-to-`std` ratio, 3 distributions, 200,000 trials
   each) — the cheapest possible discriminating control here, pure
   arithmetic, no lattice computation, and it is the control the task card
   and `docs/inventor-protocol.md` "controls before belief" both call for.
2. **Already run, reported above**: built control confirming
   `route_mut_values[i]` is bit-exact to an independent call of the
   FROZEN, unmutated route on shifted index `(i+1) mod 8` (Target 4).
3. **Recommended before any future mutation-testing document in this
   lineage**: run the same null-object check (cheap, arithmetic-only, no
   new reduction) against any *proposed* defect's predicted magnitude
   *before* choosing which cell(s) to test, specifically checking whether
   the predicted `D_route_mut` is a functional of the same archived array
   that defines the comparison threshold. If it is (as here), the result
   is foreseeably near-certain and should be flagged as such in the
   pre-registration itself, not discovered after the fact by a reviewer.
4. **Cheapest genuinely more demanding follow-up** (not commissioned by
   this report — a Coordinator decision): a defect construction whose
   expected effect size is *not* structurally tied to `s_c^fib` — e.g. a
   perturbation to a single seed *component* by a small integer offset
   (not a full index swap to a different archived basis), or a
   rounding/truncation defect affecting one matrix entry — so the
   predicted magnitude can be dialed near, below, and above `s_c^fib` and
   the mechanism's actual detection threshold can be mapped, rather than
   confirmed to lie somewhere below ~1.8x (this document's null-object
   floor) by construction.

## Baseline comparison

Not applicable in the ECDLP/Pollard-rho/BSGS sense — this is a TOY-tier
instrument-calibration check on a comparison formula (`PREREG-3` §3.3),
not an algorithmic claim. The relevant "baseline" is the mechanism's own
prior demonstrated behavior: `BATCH-a6fab5`'s genuine route comparison
(`D_route'' = 1.776e-15`, ratio to threshold `~1e-13`), against which this
document's injected-defect ratio (`~2.5–2.8x`, above threshold) is the only
other calibration point this lineage has ever produced — leaving the
entire intermediate range (from `~1e-13` to `~2.5x`) of the mechanism's
behavior completely unmapped.

## Narrowest supported statement

`T-MUTCTRL-DETECTED` (unsuffixed, `|COVERED|=2/2`) fired correctly and is
mechanically, independently reproducible bit-exact. It supports: "the
`D_route`/`D_route''` comparison mechanism, applied unchanged, correctly
flags a defect that substitutes one archived basis's correctly-computed
value for a different (also correctly-computed) archived basis's value, at
`hkz/L7_b5` and `hkz/L11_b30`." It does **not** support — and should not be
cited as supporting — any claim that the mechanism has been shown to have
"real power" at a *meaningful, dialed* defect magnitude, because the
tested magnitude was not an independently chosen or controllable
parameter: for this entire defect class, at any of the 6 archived `hkz`
cells, the predicted margin is a near-tautological consequence of
comparing a max-of-8 statistic to a std-of-the-same-8 statistic
(null-object control: P(exceed) ≥ 99.998%, matching the observed real-cell
range 2.29x–2.79x almost exactly). `hkz`'s own admissibility,
`T-HKZINDEP-CONFIRMED`'s correctness, any other defect class, any
uncovered cell, and `GOAL-MLKEM-005`'s status are untouched by this
document, exactly as PREREG-6 §2.6/§2.8 already state.

## Next concrete action

Before any successor mutation-testing document in this lineage is
commissioned, the Coordinator should require a pre-registered check
(arithmetic-only, no reduction) of whether the proposed defect's predicted
effect size is a functional of the *same* archived data used to define the
comparison threshold — as demonstrated here, that structural coupling
alone can make "detection" near-certain regardless of the mechanism's true
sensitivity, and the cheapest way to catch it is the null-object
simulation run in this report (`probes/rt_reverify.py`, section E; ~1
second of pure numpy arithmetic, no `fpylll`, no lattice).

## Every path this task wrote

```
coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/reviews/TASK-20260813-0881f0/red_team_report.md   (this file)
coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/reviews/TASK-20260813-0881f0/probes/rt_reverify.py
coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/reviews/TASK-20260813-0881f0/probes/rt_reverify_results.json
coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/reviews/TASK-20260813-0881f0/probes/rt_reverify_stdout.log
coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/reviews/TASK-20260813-0881f0/probes/rt_rerun_lead_script_results.json
coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/reviews/TASK-20260813-0881f0/probes/rt_rerun_lead_script_stdout.log
```

Nothing was written outside this task's `write_scope`. No commit was made
by this task; the Coordinator's ledger archive task performs that
separately. `knowledge/INDEX.md` was not written, regenerated, or staged.
