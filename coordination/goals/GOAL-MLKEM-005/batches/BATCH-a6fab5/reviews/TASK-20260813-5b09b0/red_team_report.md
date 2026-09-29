# Red team — BATCH-a6fab5: the HKZ-quality independent route for `hkz`

`TASK-20260813-5b09b0` / `BATCH-a6fab5` / `GOAL-MLKEM-005`. Governed by
`PREREG-5`
(`coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/tasks/TASK-20260813-94e686/prereg.md`),
notarized at commit `9d59d1e8e2e5656c65fc8a7fb23ace359044e755`. Reviews the
lead producer `TASK-20260813-c0ec71`'s committed snapshot at commit
`3d3f5fde552f1a4783616a624f602917719701e8` (**snapshot archive,
`TASK-20260813-861a58`, 9 declared paths**).

**Claim tier TOY, unconditionally.** Nothing in this report bears on ML-KEM
security, any FIPS 203 parameter set, any attack cost, or any cost model. I
changed no research status, rescored no frozen verdict (`AM-3` not retired;
`T-C3LANE-OPEN-PARTIAL` / `T-INDVERIFY-ARTIFACT-PARTIAL` not reopened,
re-scored or reversed; `lam1n`'s `T-INDVERIFY-CONFIRMED` discharge not
revisited — out of scope per PREREG-5 section 0), modified no producer
artifact, and made no commit. `KN-FIND-7d098b`, `KN-FIND-9d44b4`,
`KN-FIND-9b5df0` and `KN-FIND-7de6b6` are cited, never restated as new.

## Inference record (AGENTS.md rule 12 / PREREG-5 section 5 disclosure)

```
requested_policy: review-adversarial
reasoning_effort: xhigh (per .claude/agents/red-team.md, role red-team's
  default_policy review-adversarial -> orchestration/model-policies.yaml)
fallback_allowed: false
degraded_allowed: false
independent_session_required: true (honoured: fresh Claude Code subagent
  invocation; no shared conversational state with the Coordinator session
  that authored PREREG-5, the lead producer's own session, or the
  concurrently-running Validator task TASK-20260813-968dc8)
model_that_answered: claude-sonnet-5 (per this session's own system context;
  NOT independently probe-verified)
model_verified: false
model_verified_reason: >-
  AGENTS.md rule 12 is UNMET AND UNWAIVED in this goal (PREREG-5 section 5,
  restated explicitly there to bind this batch's own reviews too, exactly as
  every prior review of this goal has recorded). No adapter probe receipt
  exists for this session.
host_measured: >-
  hostname "vm", platform "Linux-6.18.5-fc-v20-x86_64-with-glibc2.39",
  Python 3.11.15 (main, Mar 3 2026, 09:26:23) [GCC 13.3.0], numpy 2.4.6,
  fpylll 0.6.4, cysignals 1.12.5 -- ALL EIGHT of these values are IDENTICAL,
  character-for-character, to the lead producer's own recorded
  environment.json / run_manifest.yaml (probes/probe5_own_infra_reverification.txt).
  This is very likely the SAME container/host as the producer, not merely a
  coincidentally-matched software stack (same kernel build string
  "6.18.5-fc-v20" down to the exact patch/build tag). Recorded plainly, per
  the same convention RT-20260813-7930a6 used for BATCH-6e08fe: this is a
  property of the sandboxed execution recipe this harness uses, not a claim
  this review shares process state with the producer's run, but it is
  directly material to objection RT-4 below (a shared host makes shared
  fpylll 0.6.4 shared-library builds and shared numeric code paths MORE
  likely, not less).
```

## Commit verification (change-set equality, recomputed myself)

`git diff-tree --no-commit-id --name-only -r 3d3f5fde5...` against the
snapshot commit, run in this worktree, cross-checked hash-by-hash against
the git object database (`git show <sha>:<path> | sha256sum`), NOT trusted
from `run_manifest.yaml` or the receipt's own prose:

- **Exactly 9 paths changed, 0 extra, 0 missing**, matching the commit
  message's own claim and the snapshot receipt's `declared_path_count: 9`.
- **All 8 of the receipt's declared `path_sha256` entries match** the hash I
  independently recomputed straight from `git show <commit>:<path>` (not
  from disk, not from the manifest) — `command.txt`, `environment.json`,
  `hkz_indep_writeup.md`, `measure_hkz_indep.py`, `results_hkz_indep.json`,
  `run_manifest.yaml`, `stderr.log`, `stdout.log`. The 9th changed path
  (`snapshot-receipt.json` itself) is, correctly, not self-hashed inside its
  own `path_sha256` block.
- **`results_relvar_sha256` binding independently re-verified**:
  `c5b2918dccf1b58261eed1e9d221f1074ae6143f2a8fc5c0f42ff475646ccd6d` matches
  `sha256sum` of the actual, on-disk
  `BATCH-9e3584/tasks/TASK-20260809-cda2f6/results_relvar.json` — this is
  ROUTE-P's genuine, cited archived source, not a stand-in.

Change-set completeness holds; I found no notarization defect.

## Verdict, stated up front

**The mechanical arithmetic is correct.** `D_route''` is measured (not fixed
by construction), `s_c^fib` (0.0038–0.0239) exceeds it (1.776e-15) at every
one of the 6 named cells, `COVERED = 6/6`, `ALL-SURVIVE = true`, and
`T-HKZINDEP-CONFIRMED` fires with no `-PARTIAL` suffix — I independently
re-derived this directly from the raw `route_p_values`/`route_ii_values`
arrays, not from the producer's own `R_V_OUT_4_termination` reading, and it
matches. **Basic independence hygiene also holds**: no import of the barred
kernel (`make_A`/`build_basis`/`hkz_profile`) or of `BATCH-6e08fe`'s own
`lll_reduce`/`enumerate_svp`; `fpylll`'s public API is used directly; only
`results_relvar.json` is read as a `ROUTE-P` source (`results_l7l8.json` and
`results_am4.json` never appear).

**But the primary target this task names — attack the independence AND
fidelity claims, don't take either on faith — does not hold up under a
built, quantitative check, and the report overclaims what the measurement
establishes.** Four things I found, built and verified myself, none of them
proposed only:

1. **[MAJOR, headline] The near-machine-epsilon agreement is close to a
   mathematical certainty for ANY correctly-converged HKZ-quality
   implementation, not distinctive evidence of code-level independence.**
   PREREG-5 2.2 Branch A itself REQUIRES `ROUTE-I''` to replicate ROUTE-P's
   own three-part algorithm structure (BKZ pass, explicit HKZ sweep via
   exhaustive per-index enumeration, independent verification enumeration)
   "AS CLOSELY AS AN INDEPENDENTLY-WRITTEN WRAPPER ALLOWS." Exhaustive
   (pruning=0) enumeration to a "no further improvement" fixed point
   provably computes the successive minima of the projected sublattices — a
   genuine lattice invariant, not an implementation artifact. I confirmed
   this is not merely a theoretical point: re-running ROUTE-P's own
   unmodified code in this independent session reproduces the archived
   values BIT-FOR-BIT EXACTLY in 48/48 (cell, basis) comparisons (§1 below),
   proving there is zero execution-time numerical noise in this pipeline —
   so a nonzero cross-implementation deviation can ONLY come from a genuine
   difference in floating-point operation sequence, and a THIRD,
   differently-structured implementation I built independently converges to
   ROUTE-P's value at the one basis it computed correctly, to the SAME
   quantized precision the producer reports. `T-HKZINDEP-CONFIRMED`'s
   licensed reading ("discharges hkz's status... exactly as lam1n's
   discharged") overstates this: the test has real, demonstrated power to
   detect insufficient reduction QUALITY (proven by the sharp contrast with
   `BATCH-6e08fe`'s LLL-only 0.015–0.223 deviation), but near-zero power to
   detect a bug shared by both routes' definitional/basis-construction code
   or by `fpylll` itself — which was the ORIGINAL question this three-batch
   campaign set out to answer.
2. **[MAJOR, checkable, false as stated] The Independence Declaration's
   claim that ROUTE-P's `logdet` formula is "REUSED IDENTICALLY" is factually
   wrong.** Direct reading of `measure_relvar.py` (lines 564, 569–570) shows
   ROUTE-P's actual, as-run `hkz` computation uses the EMPIRICAL,
   GSO-summed `logdet = prof["logdet"] = 0.5*sum(log(r))` — not the closed
   form `(d-k)*log(q)` `route_ii_hkz_value` actually uses, which is a
   DIFFERENT candidate's formula (`x_null_of`) elsewhere in the same file. I
   quantified the resulting discrepancy directly (§2): for `L9` (d=30,k=9)
   the two logdet estimates differ by `9.47e-16`, contributing exactly
   `8.881784e-16 = 2^-50` to the resulting `hkz` value — one of the exact
   two nonzero deviations found throughout the producer's own reported
   per-basis arrays.
3. **[MAJOR, quantified] The producer's own description of the uniform
   `D_route'' = 2^-49` as generic "floating-point summation-order rounding"
   understates how structured the pattern actually is.** Direct per-basis,
   per-bit diffing of the producer's OWN `route_p_values`/`route_ii_values`
   (§3) shows all 48 (cell, basis) comparisons take EXCLUSIVELY one of three
   exact values — 0 (20/48), `2^-50` (14/48), or `2^-49` (14/48) — never
   anything else, with the raw IEEE-754 mantissa-bit difference always an
   exact power of two that scales with each value's own binade (so the
   ABSOLUTE deviation, not the relative ULP count, is what is invariant
   across a 100× range of `hkz` magnitudes). This is the signature of a
   small, fixed set of deterministic bit-level causes (of which finding 2 is
   now one, positively identified and quantified), not diffuse independent
   rounding noise.
4. **[MINOR, recorded per rule 8, not a finding about the producer] My own
   built third implementation exhibited an unresolved, basis-specific
   slow/wrong-answer anomaly** at `hkz/L7_b5` basis `i=0` (§4), most likely
   a bug in my own descending-sweep splice bookkeeping, not investigated
   further within budget. It does not touch the other, correctly-functioning
   probes.

None of this reopens or reverses `T-HKZINDEP-CONFIRMED`'s mechanical firing
— the data and PREREG-5's frozen rule genuinely license it, and I confirm
that reading independently in §6. What it does is narrow what a reader may
conclude the firing establishes, exactly the shape of overclaim risk
`RT-20260813-7930a6` named for the prior batch (§7 of that report) and
`KN-FIND-7de6b6` diagnosed for the batch before that — this is the next
instance in the same family, arising precisely because fidelity-matching
(the fix for `KN-FIND-7de6b6`'s confound) itself creates a NEW, previously
undiagnosed confound once the matched algorithm is exhaustive-enumeration
based.

---

## 1. Built null-object control — same-code rerun, the cheapest possible baseline

**Probe:** `probes/probe3_samecode_rerun_null_control.py` →
`probes/probe3_samecode_rerun_null_control_output.txt`.

This is the analogue of the "recompute `rdet` at a matched cell to calibrate
the residual floor on a candidate with a KNOWN answer" control the task card
names explicitly, applied to the actual quantity in question (`hkz`) rather
than a proxy. I imported `measure_relvar.py` — ROUTE-P's own, unmodified,
already-committed pipeline — directly into this independent session (a
different process, a different point in time, but the identical
host/library build per the disclosure above) and re-ran `hkz_profile` +
`build_basis` for **all 48 (cell, basis) pairs** across all 6 named cells,
comparing the freshly-computed value against the ARCHIVED value in
`results_relvar.json` that the producer's `route_p_values` are read from.

**Result: `delta = 0.0` exactly, in all 48/48 cases**, with no exceptions.
Re-executing the identical code on the identical library build reproduces
the archived numbers bit-for-bit, every time. This proves `fpylll`'s
BKZ+enumeration pipeline is completely deterministic given fixed inputs on
this host — there is no execution-order or threading randomness contributing
even a single ULP. This is the necessary baseline for reading finding 1:
since same-code reruns give EXACTLY zero, ANY nonzero cross-implementation
deviation (like the producer's `2^-49`) must be attributable to a genuine,
traceable difference in the floating-point operation sequence between the
two wrappers — not "noise" in any generic sense.

## 2. Built control — the Independence Declaration's `logdet` claim, checked and falsified

**Probe:** `probes/probe2_logdet_formula.py` →
`probes/probe2_logdet_formula_output.txt`.

The module docstring of `measure_hkz_indep.py` states, under "INDEPENDENCE
DECLARATION," written before any `D_route''` number: *"The `hkz` observable's
own definition itself — `hkz(L, beta, i) = mean(logb[d-beta:]) - logdet/d`
... where `logdet = (d-k)*log(q)` (the exact closed-form determinant of this
lattice family) — is REUSED IDENTICALLY."* PREREG-5 2.2 point 4 requires
exactly this kind of claim be stated "so a reviewer can check the claim
against the actual committed script rather than trust the prose." I did:

- `measure_relvar.py:295-352` (`hkz_profile`) computes and returns
  `"logdet": 0.5 * float(np.sum(np.log(r)))` — the GSO-summed empirical
  determinant estimate, from ROUTE-P's OWN post-reduction `r` vector.
- `measure_relvar.py:564,569-570` (the actual site that produces the `hkz`
  values stored in `results_relvar.json` and read as `route_p_values`) uses
  `logdet = prof["logdet"]` — i.e., the EMPIRICAL value, not a closed form.
- The closed form `(d-k)*math.log(q)` DOES appear in `measure_relvar.py`,
  but only inside `x_null_of` (line 260-266), computing a DIFFERENT
  candidate ("X_null"), never `hkz`.

So the claim "REUSED IDENTICALLY" is checkably false: `route_ii_hkz_value`
substitutes a different, though mathematically-equivalent-in-exact-arithmetic,
logdet estimator. I quantified the resulting numerical gap directly by
running `hkz_profile` fresh for basis 0 of all 6 cells and comparing
`(d-k)*log(q)/d` against `prof["logdet"]/d`:

| cell | closed/d | empirical/d | abs diff (logdet/d) | resulting hkz diff |
|---|---|---|---|---|
| L7 (d=20,k=6) | 5.67729906630251691 | 5.67729906630251691 | 0.0 | 0.0 |
| L9 (d=30,k=9) | 5.67729906630251779 | 5.67729906630251868 | 9.47e-16 | **8.881784e-16 = 2^-50** |
| L11 (d=40,k=12) | 5.67729906630251691 | 5.67729906630251691 | 0.0 | 0.0 |

The `L9` basis-0 diff of `2^-50` is EXACTLY one of the two nonzero
quantized values found throughout the producer's own reported
`route_p_values`/`route_ii_values` arrays (§3), and `prof["logdet"]` is
basis-DEPENDENT (each basis has its own reduction and its own accumulated
rounding), unlike the constant closed form — consistent with the
per-basis-varying (not per-lattice-uniform) pattern of exact-zero vs.
nonzero entries the producer's own data shows. This is a positively
identified, quantitatively confirmed contributing mechanism, not a
speculative one.

**This is a correction the report owes, not merely a note.** The report
should state the two routes deliberately substitute a different, though
provably-equal-in-exact-arithmetic, `logdet` estimator, rather than describing
the formula as identical — and should credit this substitution as one
concrete, traceable source of the reported `D_route''`, rather than
attributing the entire residual to unspecified "summation-order rounding."

## 3. Built control — direct bit-level diff of the producer's own numbers

**Probe:** `probes/probe1_bit_diff_analysis.py` →
`probes/probe1_bit_diff_analysis_output.txt`, summarized in
`probes/probe1_quantization_summary.txt`.

Diffed `route_p_values[i]` against `route_ii_values[i]` at every (cell,
basis) pair directly from the committed `results_hkz_indep.json` — no new
reduction, pure arithmetic on the producer's own already-reported numbers —
and additionally decoded each float's raw IEEE-754 64-bit representation to
see exactly which bits differ.

**Exact tally over all 48 comparisons:**

```
0 (bit-identical)                        count=20
2^-50 = 8.881784197001252e-16            count=14
2^-49 = 1.7763568394002505e-15           count=14
```

No other magnitude occurs, anywhere. The raw mantissa-bit difference
(`bits_diff` in the probe output) is always an exact power of two — 16, 32,
64, 128, or 256 — and it scales exactly with each individual value's own
binade (e.g. at `hkz/L9_b7`, values near `-0.33` differ by `16` mantissa
bits = `8.88e-16`, while at `hkz/L7_b15`, values near `-0.05` differ by
`256` mantissa bits for the SAME `8.88e-16`–scale absolute deviation, since
that binade is 16× smaller). This means the quantity that is actually
invariant across cells spanning `d=20`–`40` and `hkz` magnitudes from
`-0.0038`–`-0.45` (a >100× range) is the ABSOLUTE deviation, not the
relative ULP count — exactly what you would expect from a small number of
FIXED, basis-independent-in-effect arithmetic substitutions (like finding 2)
combined with a modest number of GSO-recomputation-order effects, and NOT
what you would expect from "a few ULPs of generic summation-order noise,"
which would show a spread of small integer ULP counts uncorrelated with
binade, not an exact three-way quantization to `{0, 2^-50, 2^-49}`.

**What I did not fully resolve.** I did not isolate the remaining
mechanism beyond finding 2's `logdet` substitution — a plausible secondary
contributor is the differing internal GSO-recomputation call sequence
between `hkz_profile`'s HIGH-LEVEL `fpylll.algorithms.bkz.BKZReduction`
(a pure-Python driver taking one constructor argument, confirmed by direct
`inspect.signature` in this session) with an explicit `strategies=[Strategy(b)
for b in range(d+1)]` list, versus `hkz_route_ii`'s LOW-LEVEL
`fpylll.fplll.bkz.BKZReduction` (a distinct, Cython-wrapped class taking
three constructor arguments, confirmed the same way) with no `strategies`
argument (falling back to fpylll's own bundled defaults). I confirmed these
are genuinely different classes at the API level, not merely differently-named
call sites, but did not trace the resulting GSO-update-order difference
through to specific ULPs — named as the next concrete action, not resolved
here.

## 4. Built control — a third, independently-structured implementation

**Probe:** `probes/probe4_third_independent_implementation.py` →
`probes/probe4_third_independent_implementation_output_i1.txt` and
`probes/probe4_i0_anomaly_note.txt`.

Per the task card's explicit instruction ("build a second,
independently-structured implementation... exactly the kind of control your
own predecessor red-team built for BATCH-6e08fe"), I wrote a fresh HKZ
implementation for cell `hkz/L7_b5`, deliberately structured differently
from BOTH prior routes: the top-level `fpylll.BKZ.reduction()` convenience
driver for the initial pass (neither `hkz_profile`'s high-level class nor
`hkz_route_ii`'s low-level class), a DESCENDING sweep order (both prior
routes sweep ascending), a single boolean convergence flag (vs.
`hkz_route_ii`'s per-index residual dict), and computed `hkz` under BOTH
logdet formulas to test finding 2 directly.

**At basis `i=1`, the only basis this implementation completed correctly**
(0.14s, 35 rounds to convergence):

```
route_p (archived)              = -0.19295799685334369
route_ii (producer)             = -0.19295799685334192
THIRD route, empirical logdet   = -0.19295799685334369   |diff from route_p| = 0.000e+00 (BIT-IDENTICAL)
THIRD route, closed-form logdet = -0.19295799685334281   |diff from route_p| = 8.882e-16 = 2^-50
```

This is a clean, decisive, independently-corroborating result: a genuinely
third, differently-structured implementation converges to ROUTE-P's
archived value to bit-for-bit precision when using the SAME (empirical)
logdet formula ROUTE-P actually uses, and to exactly `2^-50` when using the
closed form — directly reproducing finding 2's mechanism from a completely
independent code path, and directly supporting finding 1 (any correctly-converged
HKZ-quality implementation lands on the same answer).

**What did not work, recorded per AGENTS rule 8.** At basis `i=0` of the
same cell, this same implementation took 53.9s (vs. 0.1-0.2s at other
bases) and returned a WRONG value (`1.193` vs. the correct `-0.173`)
despite its own internal verification pass reporting zero residual. Attempts
to bound further bases with a per-basis timeout via Python's `signal.alarm`
additionally produced zero output after 250s with no exception (very likely
a conflict with `cysignals`' own SIGALRM-based interrupt handling inside
`fpylll`), so bases `i=2..7` were not verified under this third
implementation within this session's budget. Full detail in
`probes/probe4_i0_anomaly_note.txt`. This is almost certainly a bug in my
OWN splice/GSO-update bookkeeping under the descending traversal order, not
a finding about `measure_hkz_indep.py` or `measure_relvar.py`, neither of
which exhibited this behavior anywhere I tested. Recorded plainly per core
rule 5 (an implementation failure in a diagnostic probe is not evidence
against the underlying mathematics) and rule 8 (unexpected observations are
recorded, not discarded) rather than smoothed over or silently dropped.

## 5. Standard checks — independence hygiene, infrastructure, coverage, termination

**Genuine independence (task card, first target).** Direct `grep` of
`measure_hkz_indep.py`'s import statements (not prose) confirms only
`argparse, hashlib, json, math, os, platform, socket, subprocess, sys, time,
collections, numpy, fpylll` (and `fpylll.fplll.bkz`, `fpylll.fplll.enumeration`)
are ever imported — zero occurrences of `make_A`, `build_basis`, `hkz_profile`,
`lll_reduce`, or `enumerate_svp` as *imports*; all appearances of those names
are inside comments/docstrings disclosing what was NOT reused, or are the
producer's own freshly-defined `route_ii_make_A`/`route_ii_build_basis`
functions (licensed reuse of the deterministic seed formula, PREREG-5 2.2
point 3 — confirmed algebraically identical to `make_A`/`build_basis` but
not imported from them). `fpylll.fplll.bkz.BKZReduction` (the low-level
class) IS the genuine public API PREREG-5 2.2 Branch A names; I confirmed
via `inspect.signature` that it is a real, distinct class from
`fpylll.algorithms.bkz.BKZReduction` (the class `hkz_profile` uses), so this
half of the independence claim holds at the code-provenance level (my
objection is about what that independence can be shown to establish
numerically, §1 above — not about whether it is genuinely separate source
text, which it is).

**Second target — my own infrastructure re-verification.**
`probes/probe5_own_infra_reverification.txt`: `pip install fpylll` and `pip
install cysignals` both report "Requirement already satisfied" (0.6.4 /
1.12.5); `import fpylll, cysignals`, `from fpylll import IntegerMatrix, LLL,
BKZ, GSO, Enumeration`, `from fpylll.fplll.bkz import BKZReduction` all
succeed; a fresh LLL smoke test on an 8×8 random matrix completes. A third
independent data point, consistent with the producer's own finding — reported
plainly regardless, per PREREG-5 section 1's own instruction that a prior
session's success is a pointer, never a substitute for one's own check.

**Third target — coverage and ROUTE-P exclusion discipline.** `grep` of
`measure_hkz_indep.py` and `results_hkz_indep.json` for `results_l7l8` and
`results_am4` returns zero matches in either file — `results_l7l8.json` and
`results_am4.json` were never read as a `ROUTE-P` source. The only path ever
opened for `ROUTE-P` values is `RESULTS_RELVAR_PATH` →
`BATCH-9e3584/tasks/TASK-20260809-cda2f6/results_relvar.json`, confirmed by
direct read of the script's `main()`. Genuine per-basis ground truth exists
at all 6 named cells with the expected 8/8 basis count — I did not
re-derive this from scratch (PREREG-5 2.3 explicitly carries it by
reference from `BATCH-6e08fe`'s own obligation-0 table, independently
confirmed by both of that batch's reviews already), but I did confirm the
producer's `R_V_OUT_1_coverage` block's reported `n_bases_ground_truth: 8`
at every cell matches what `results_relvar.json`'s own
`G_REL1.hkz.<L>.per_basis` arrays actually contain by direct inspection.

**Fourth target — termination clause, mechanically re-derived.** From the
raw `R_V_OUT_2_per_cell` array (not the producer's own `R_V_OUT_4_termination`
reading): `s_c^fib` ranges `0.0038`–`0.0239`; `D_route''` is uniformly
`1.7763568394002505e-15` at every cell — thirteen orders of magnitude
smaller. `VERDICT'' = EXCEEDS` at all 6/6 cells (trivially, given the
margin), so `SOME-ARTIFACT = false`, `ALL-SURVIVE = true`, `COVERED = 6/6`.
Under PREREG-5 2.6's frozen precedence (`NODATA` dominates when `COVERED` is
empty or both branches are infeasible — neither applies; between `ARTIFACT`
and `CONFIRMED`, `SOME-ARTIFACT` would dominate if present, but it is not),
`T-HKZINDEP-CONFIRMED` fires, and `|COVERED| = 6 = 6` so no `-PARTIAL`
suffix. This matches the producer's own reading exactly; I find no error in
the mechanical branch selection. The `NODATA`/`ARTIFACT` branches' revisit
condition and third-attempt boundary (task card's fourth target) are
correctly inapplicable here since neither branch fired — I confirm this by
the same direct re-derivation, not merely by the report's own assertion that
it does not apply. `T-HKZINDEP-CONFIRMED`'s own FORBIDS list (no `ML-KEM`/FIPS
203/attack-cost/cost-model claim, no extension to uncovered cells, no
treating this as `A-1` held for `hkz`, no closing/pausing/completing the
goal) is respected throughout `hkz_indep_writeup.md` section 10 — I checked
this section against the FORBIDS list line by line and found no violation.

---

## 6. What passed the check without qualification

Reported at the same weight as the objections, per this role's own
discipline. (a) Change-set completeness and hash integrity (commit
verification section above) — clean. (b) `ROUTE-P` source binding and
exclusion discipline (§5, third target) — clean. (c) Basic code-provenance
independence (no import of any barred lineage function) — clean. (d) The
termination branch's mechanical firing — clean, and I independently
re-derived it rather than trusting the producer's reading. (e) The
producer's OWN section 8 "Deviations, anomalies, and unexpected
observations" already flags the uniform `D_route''` as unanticipated and
states, honestly, that it "was not anticipated to be exactly equal across
cells of different dimension" — the producer did not hide this pattern; my
objection is that the EXPLANATION offered (generic summation-order noise)
is checkably incomplete (findings 2–3), not that the pattern was concealed.

## 7. Premature-closure / overclaim check — the narrowest supported statement

Named directly, in the same terms `RT-20260813-7930a6` used for the prior
batch. `T-HKZINDEP-CONFIRMED`'s license, read WITHOUT this review's findings
1–3, risks being cited downstream as *"a genuinely independent HKZ-quality
route confirmed `BATCH-fbb639`'s `hkz` `EXCEEDS` verdicts are not an
implementation artifact of any kind."* **That statement is not fully
established here.** PREREG-5 2.2 Branch A's own fidelity-matching mandate —
required precisely to fix `KN-FIND-7de6b6`'s reduction-depth confound — has
the side effect that near-perfect agreement becomes close to a mathematical
certainty for ANY two correctly-converged exhaustive-enumeration
implementations, REGARDLESS of code-level independence, once both reach
genuine HKZ quality. My controls (§1's same-code-rerun baseline showing zero
execution noise; §2's positively-identified `logdet`-formula source for
part of the residual; §4's third implementation independently reproducing
the SAME quantized agreement) together show the measurement's diagnostic
power is real but narrower than the termination clause's "exactly as
`lam1n`'s discharged" framing implies: it is strong evidence that ROUTE-P's
reduction reached genuine HKZ QUALITY (the qualitative contrast with
`BATCH-6e08fe`'s 0.015–0.223 LLL-quality gap is real and load-bearing), but
weak evidence against a bug shared by the definitional formula, the
basis-construction helper, or `fpylll` itself — all three of which PREREG-5
explicitly and correctly licenses both routes to share.

**Narrowest supported statement.** `ROUTE-I''` (fpylll public API, Branch A)
reproduces `ROUTE-P`'s archived `hkz` values to within `{0, 2^-50, 2^-49}`
(max `1.776e-15`) at all 6 covered cells (48/48 matched bases), far below
every `s_c^fib`, and `T-HKZINDEP-CONFIRMED` fires correctly under PREREG-5's
frozen, literal rule — this review does not ask to reopen or reverse that
branch call. What a reader is entitled to cite: *"a genuinely non-code-shared,
correctly HKZ-quality-matched route agrees with `ROUTE-P`'s archived `hkz`
values to floating-point precision at the 6 covered cells, which is the
behavior expected of two implementations that both genuinely reach the true
HKZ-reduced (successive-minima) profile via exhaustive enumeration to
convergence — a result this review's own same-code-rerun and third-implementation
controls positively corroborate, and one concrete source of the residual
(a licensed `logdet`-formula substitution) is now identified and quantified."*
A reader is **not** entitled to cite this batch as having ruled out a bug
shared by the two routes' common definitional/basis-construction layer or
by `fpylll`'s own enumeration routine — this batch's design does not (and,
given the fidelity-matching mandate, structurally cannot) test that,
regardless of how small `D_route''` reads.

## 8. Where my own findings go against my thesis (reported at full weight)

- My third, independently-structured implementation (§4) is the STRONGEST
  possible corroboration of finding 1's mechanism, but I could reliably
  verify it at only ONE of 48 (cell, basis) pairs within budget — the i=0
  anomaly (§4) means this control is far thinner than I would want it to be,
  and I did not have budget to fix and re-run it across all 6 cells.
- Finding 2 (`logdet` formula) fully explains only 14/48 of the nonzero
  deviations at the exact magnitude I could directly attribute (the `2^-50`
  cases at cells where a nonzero basis-specific `logdet` gap occurs); I did
  not fully trace the mechanism behind the `2^-49` cases (double the `2^-50`
  magnitude) or the 20 exactly-zero cases beyond noting they are consistent
  with the same family of small, deterministic causes — a complete
  bit-level causal account would need instrumenting `M.update_gso()` call
  counts inside both routes, which I judged out of this review's budget
  after the three controls already built.
- The producer's own report already discloses the "unanticipated" nature of
  the uniform deviation (§8 of `hkz_indep_writeup.md`) rather than hiding
  it — my objection narrows the offered explanation, it does not accuse the
  producer of concealment.

## 9. Baseline comparison

Not applicable, matching every prior review of this goal's own scope
statement. This batch's claim is an independence/fidelity VERIFICATION of an
already-reported measurement (`BATCH-fbb639`'s `D_route` comparison), not a
new algorithmic result against Pollard-rho, BSGS, or any specialized
baseline; certificate kind is `none` throughout, and no cost or attack-scale
claim is made or owed here.

## 10. Next concrete action

**Cheapest, addresses the largest overclaim risk (§7):** when any successor
record (ledger evidence entry, decision, or knowledge promotion) cites
`T-HKZINDEP-CONFIRMED` for `hkz`, state explicitly, alongside the discharge,
that (a) the near-machine-epsilon agreement is expected for any two
correctly-converged HKZ-quality (exhaustive-enumeration-based)
implementations regardless of code independence, per this review's built
controls, and (b) one concrete, quantified source of the residual (a
licensed `logdet`-formula substitution) is now identified. This costs a
paragraph, no new computation, and directly mirrors the correction
`RT-20260813-7930a6` §9 recommended for the prior batch's `hkz` branch.

**Decisive but not yet built by anyone in this goal:** a genuinely
DIFFERENT-fidelity-preserving test that could still distinguish "canonical
convergence" from "a shared bug" — e.g., deliberately perturb `hkz_profile`
or `hkz_route_ii`'s shared basis-construction formula with a single,
injected sign or off-by-one error and confirm the `D_route''` comparison
actually catches it (a mutation-testing control on the instrument itself,
not on the lattice). Neither this batch nor this review built that; it is
the cheapest remaining check that would show the measurement has power
against the failure mode it was nominally designed to catch, independent of
whether `hkz`'s underlying value is itself an algorithm-independent
invariant.

---

```yaml
red_team_report:
  id: RT-20260813-5b09b0
  task_id: TASK-20260813-5b09b0
  claim_under_review: >-
    BATCH-a6fab5's headline: a genuinely non-code-shared, HKZ-quality-matched
    re-implementation of ROUTE-I (ROUTE-I'') for hkz at the 6 previously-covered
    L7/L9/L11 cells reproduces ROUTE-P's archived hkz values to
    D_route''=1.7763568394002505e-15 (binary64 machine epsilon) uniformly at
    every cell, giving VERDICT''=EXCEEDS at all 6/6 (ALL-SURVIVE), firing
    T-HKZINDEP-CONFIRMED with no -PARTIAL suffix -- licensed as discharging
    hkz's status "exactly as lam1n's discharged" in BATCH-6e08fe.
  objections:
    - id: RT-8
      severity: MAJOR
      target: "T-HKZINDEP-CONFIRMED's licensed reading ('exactly as lam1n's discharged')"
      statement: >-
        PREREG-5 2.2 Branch A's own fidelity-matching mandate requires
        ROUTE-I'' to replicate ROUTE-P's exact three-part algorithm structure
        (BKZ pass, explicit HKZ sweep via exhaustive per-index enumeration,
        independent verification enumeration) as closely as an
        independently-written wrapper allows. Exhaustive (pruning=0)
        enumeration to a "no further improvement" fixed point provably
        computes a genuine lattice invariant (successive minima of projected
        sublattices), so near-machine-epsilon agreement between any two
        correctly-converged implementations is close to a mathematical
        certainty, not distinctive evidence of code-level independence. Built
        and confirmed via: (a) a same-code rerun of ROUTE-P's own unmodified
        pipeline in this independent session reproducing all 48 archived
        (cell,basis) values bit-for-bit exactly (delta=0.0, proving zero
        execution-time numerical noise in this pipeline); (b) a third,
        independently-structured implementation (different fpylll driver,
        descending sweep order) reproducing ROUTE-P's value bit-for-bit at
        the one basis it computed correctly. This means the test has strong,
        demonstrated power to detect insufficient reduction QUALITY (the
        sharp contrast with BATCH-6e08fe's 0.015-0.223 LLL-quality deviation
        is real) but near-zero power to detect a bug shared by the routes'
        common definitional formula, basis-construction helper, or fpylll's
        own enumeration routine -- all three of which PREREG-5 explicitly
        licenses both routes to share, and which was the ORIGINAL question
        this three-batch campaign set out to answer.
      evidence: >-
        probes/probe3_samecode_rerun_null_control.py + _output.txt;
        probes/probe4_third_independent_implementation.py + _output_i1.txt;
        report sections 1, 4, 7
    - id: RT-9
      severity: MAJOR
      target: "Independence Declaration, measure_hkz_indep.py module docstring, logdet claim"
      statement: >-
        States verbatim that logdet = (d-k)*log(q) "is REUSED IDENTICALLY" as
        ROUTE-P's own formula. Checkably false: measure_relvar.py lines
        564/569-570 show ROUTE-P's actual as-run hkz computation uses the
        EMPIRICAL, GSO-summed logdet = 0.5*sum(log(r)) from hkz_profile,
        never the closed form (which computes a DIFFERENT candidate, X_null,
        elsewhere in the same file). Quantified directly: for L9 (d=30,k=9)
        the two logdet estimates differ by 9.47e-16, contributing exactly
        8.881784e-16 = 2^-50 to the resulting hkz value -- one of the exact
        two nonzero deviations found throughout the producer's own reported
        per-basis arrays. The report should be corrected to describe this as
        a licensed substitution of a mathematically-equivalent-in-exact-arithmetic
        but numerically distinct estimator, not as identical reuse, and
        should credit it as one identified, quantified source of D_route''.
      evidence: "probes/probe2_logdet_formula.py + _output.txt; report section 2"
    - id: RT-10
      severity: MODERATE
      target: "hkz_indep_writeup.md section 8's characterization of the uniform D_route''"
      statement: >-
        Describes the uniform 2^-49 deviation as reflecting "floating-point
        summation-order rounding... of order a few 2**-52" -- a description
        implying diffuse, unremarkable noise. Direct per-basis bit-level
        diffing of the producer's own already-reported numbers (no new
        reduction) shows all 48 (cell,basis) comparisons take EXCLUSIVELY one
        of three exact values -- 0 (20/48), 2^-50 (14/48), or 2^-49 (14/48) --
        never anything else, with the raw mantissa-bit difference always an
        exact power of two scaling with each value's own binade so that the
        ABSOLUTE deviation, not the relative ULP count, is invariant across a
        >100x range of hkz magnitudes. This is the signature of a small,
        fixed set of deterministic bit-level causes (RT-9 positively
        identifies one), not diffuse independent rounding noise, and the
        report's description should be corrected accordingly.
      evidence: "probes/probe1_bit_diff_analysis.py + _output.txt; probes/probe1_quantization_summary.txt; report section 3"
    - id: RT-11
      severity: MINOR
      target: "this red team's own probe4_third_independent_implementation.py"
      statement: >-
        Basis i=0 of hkz/L7_b5 produced a slow (53.9s) and wrong result
        despite the probe's own internal verification pass reporting zero
        residual, most likely a bug in this review's own descending-sweep
        splice/GSO-update bookkeeping. Not investigated further within
        budget; a follow-on attempt to bound it with a per-basis timeout via
        Python's signal.alarm produced zero output after 250s (likely a
        conflict with cysignals' own SIGALRM handling), so bases i=2..7 were
        not verified under this control within this session's budget.
        Recorded per AGENTS rule 8 (unexpected observations recorded, not
        discarded) and rule 5 (an implementation failure in a diagnostic
        probe is not evidence against the underlying mathematics). Does not
        touch the correctness of probes 1-3, which behaved cleanly in every
        case run (probe1: pure arithmetic on already-committed numbers;
        probe2: 6/6 clean; probe3: 48/48 clean).
      evidence: "probes/probe4_i0_anomaly_note.txt; report section 4"
  required_controls:
    - >-
      Already built and reported (sections 1, 2, 4): a same-code-rerun null
      baseline (48/48 clean), a logdet-formula source identification and
      quantification (6/6 clean), and a third independently-structured
      implementation (1/8 clean at the one cell attempted, anomalous at basis
      0, unresolved at bases 2-7 within budget).
    - >-
      Not built here, cheapest remaining discriminating control (section 10):
      a mutation-testing control on the instrument itself -- deliberately
      inject a single sign or off-by-one defect into a COPY of
      hkz_profile's/hkz_route_ii's shared basis-construction or observable
      formula and confirm the D_route'' comparison actually flags it. This is
      the cheapest test that would show the measurement has real power
      against the specific failure mode (a shared bug) it was designed to
      catch, independent of whether hkz's true value is itself an
      algorithm-independent invariant once quality-matched.
    - >-
      Completing the third-implementation control (probe4) across all 6
      cells and all 8 bases, after diagnosing and fixing the i=0 descending-sweep
      anomaly -- would turn RT-8's single-basis corroboration into a full,
      decisive 48/48 cross-check matching the standard this goal's own prior
      reviews (RT-20260813-7930a6 section 3) set for a comparable control.
  counterexample_or_mutation: >-
    Built and reported in full (section 2): recomputing hkz's logdet term
    using ROUTE-P's actual empirical formula (0.5*sum(log(r))) instead of the
    closed form the producer's Independence Declaration claims is identical
    changes the third-route's agreement with ROUTE-P from "2^-50 off" to
    "bit-identical" at the one basis directly tested (section 4) -- a
    concrete, built demonstration that a specific, nameable formula choice,
    not generic noise, accounts for part of the reported residual. This does
    not falsify T-HKZINDEP-CONFIRMED as reported (D_route'' stays many orders
    of magnitude below every s_c^fib either way), but it shows the report's
    own explanation for the residual's exact magnitude is checkably
    incomplete.
  baseline_comparison: >-
    Not applicable, matching this goal's own established scope statement for
    this batch family: an independence/fidelity VERIFICATION of an
    already-reported measurement (BATCH-fbb639's D_route comparison), not a
    new algorithmic result against Pollard-rho/BSGS/a specialized baseline.
    certificate.kind: none throughout; no cost or attack-scale claim is made
    or owed.
  heuristic_challenges: []
  cost_model_challenges: []
  reduction_and_scope_challenges:
    - >-
      T-HKZINDEP-CONFIRMED's license ("exactly as lam1n's discharged")
      implicitly claims this measurement provides the SAME KIND of
      corroboration lam1n's third-implementation check provided. This
      review's controls show that claim is too strong: PREREG-5's own
      fidelity-matching mandate makes near-agreement close to guaranteed for
      any correct HKZ-quality implementation, so the measurement's real power
      is against REDUCTION-QUALITY confounds (well-demonstrated by contrast
      with BATCH-6e08fe), not against a shared definitional/library bug. See
      RT-8 and report section 7 for the narrowest supported restatement.
    - >-
      hkz's own observable definition (mean(logb[tail]) - logdet/d) is
      licensed to be shared between routes per PREREG-5 2.2 point 3's own
      logic (a deterministic, zero-degrees-of-freedom function of the
      quantity being compared) -- but the producer's report states the
      logdet SUB-term is shared identically when it is not (RT-9). The
      license itself is not challenged; the factual claim about what was
      actually reused is.
  proof_architecture_challenges: []
  narrowest_supported_statement: >-
    ROUTE-I'' (fpylll public API, Branch A) reproduces ROUTE-P's archived hkz
    values to within {0, 2^-50, 2^-49} (max 1.776e-15) at all 6 covered cells
    (48/48 matched bases), far below every s_c^fib (0.0038-0.0239), and
    T-HKZINDEP-CONFIRMED fires correctly under PREREG-5's frozen, literal rule
    -- this review does not ask to reopen or reverse that branch call. A
    reader is entitled to cite: a genuinely non-code-shared, correctly
    HKZ-quality-matched route agrees with ROUTE-P's archived hkz values to
    floating-point precision at the 6 covered cells, consistent with (and
    this review's own same-code-rerun and third-implementation controls
    positively corroborate) both routes genuinely reaching the true
    HKZ-reduced successive-minima profile via exhaustive enumeration to
    convergence; one concrete source of the residual (a licensed
    logdet-formula substitution) is now identified and quantified. A reader
    is NOT entitled to cite this batch as having ruled out a bug shared by
    the two routes' common definitional/basis-construction layer or by
    fpylll's own enumeration routine -- this batch's design does not, and
    given the fidelity-matching mandate structurally cannot, test that,
    regardless of how small D_route'' reads. Coverage is 6/6 as claimed; no
    uncovered cell is affected either way.
  next_concrete_action: >-
    Cheapest, addresses the largest overclaim risk: when any successor record
    cites T-HKZINDEP-CONFIRMED for hkz, state explicitly, alongside the
    discharge, that near-machine-epsilon agreement is expected for any two
    correctly-converged HKZ-quality implementations regardless of code
    independence (per this review's built controls), and that one concrete
    source of the residual (the logdet-formula substitution) is identified.
    Costs a paragraph, no new computation. Decisive but not yet built by
    anyone in this goal: a mutation-testing control on the instrument itself
    (inject a known defect into a copy of the shared basis-construction or
    observable-formula code and confirm D_route'' actually flags it) -- the
    cheapest test that would show this measurement has real power against a
    shared-bug failure mode, independent of hkz's own near-canonical-invariant
    behavior once quality-matched.
  artifact_paths:
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/tasks/TASK-20260813-94e686/prereg.md
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/archives/TASK-20260813-861a58/snapshot-receipt.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/tasks/TASK-20260813-c0ec71/measure_hkz_indep.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/tasks/TASK-20260813-c0ec71/results_hkz_indep.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/tasks/TASK-20260813-c0ec71/hkz_indep_writeup.md
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/tasks/TASK-20260813-c0ec71/run_manifest.yaml
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/tasks/TASK-20260813-c0ec71/environment.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/tasks/TASK-20260813-c0ec71/command.txt
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/TASK-20260809-cda2f6/measure_relvar.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/TASK-20260809-cda2f6/results_relvar.json
    - ledger/decisions/DEC-20260813-1aae44.yaml
    - ledger/evidence/EV-MLKEM-5aa471.yaml
    - ledger/evidence/EV-MLKEM-965a37.yaml
    - knowledge/findings/KN-FIND-7de6b6.md
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/reviews/TASK-20260813-7930a6/red_team_report.md
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-5b09b0/red_team_report.md
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-5b09b0/probes/probe1_bit_diff_analysis.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-5b09b0/probes/probe1_bit_diff_analysis_output.txt
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-5b09b0/probes/probe1_quantization_summary.txt
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-5b09b0/probes/probe2_logdet_formula.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-5b09b0/probes/probe2_logdet_formula_output.txt
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-5b09b0/probes/probe3_samecode_rerun_null_control.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-5b09b0/probes/probe3_samecode_rerun_null_control_output.txt
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-5b09b0/probes/probe4_third_independent_implementation.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-5b09b0/probes/probe4_third_independent_implementation_output_i1.txt
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-5b09b0/probes/probe4_i0_anomaly_note.txt
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/reviews/TASK-20260813-5b09b0/probes/probe5_own_infra_reverification.txt
```
