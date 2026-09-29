# Red team — BATCH-6e08fe: the genuinely non-code-shared independent-route re-measurement

`TASK-20260813-7930a6` / `BATCH-6e08fe` / `GOAL-MLKEM-005`. Governed by
`PREREG-4`
(`coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-cdcd88/prereg.md`,
sha256 `ff577564dcdbb45b1b19885297ffc512888f9442dc99f2057fdf7f86f63fbbda`),
notarized at commit `1e1acf08b151dd31b4d41b8afd287d261adce1e5`
(**PREREG-4 notarization, `TASK-20260813-e24ad9`, 3 declared paths**).
Reviews the lead producer `TASK-20260813-ea2e96`'s committed snapshot at
commit `6ad64048dfee5b87b9df7ebcd9d7f7b80baf44cb` (**lead archive,
`TASK-20260813-2d6b5e`, 8 declared paths**).

**Claim tier TOY, unconditionally.** Nothing in this report bears on ML-KEM
security, any FIPS 203 parameter set, any attack cost, or any cost model. I
changed no research status, rescored no frozen verdict (`AM-3` not retired;
`T-C3LANE-OPEN-PARTIAL` not reopened, re-scored or reversed), modified no
producer artifact, and made no commit. `KN-FIND-7d098b`, `KN-FIND-9d44b4`
and `KN-FIND-9b5df0` are cited, never restated as new.

## Inference record

```
requested_policy: review-adversarial
reasoning_effort: xhigh (per .claude/agents/red-team.md, role red-team's
  default_policy review-adversarial -> orchestration/model-policies.yaml)
fallback_allowed: false
degraded_allowed: false
independent_session_required: true
model_that_answered: claude-sonnet-5 (Claude Sonnet 5, per this session's own
  system context; NOT independently probe-verified)
model_verified: false
model_verified_reason: >-
  AGENTS.md rule 12 / PREREG-4 section 5: independence in this goal is
  PROCEDURAL and never model-level, and is UNMET AND UNWAIVED. No adapter
  probe receipt exists for this session; AUTORESEARCH_POLICY and
  AUTORESEARCH_BACKEND are unset. Recorded as a verification gap, never as
  satisfied. PREREG-4 section 5 states explicitly this binds BOTH this
  batch's reviews, checking the lead's independence claim, exactly as much
  as it binds the lead itself -- noted here rather than glossed over.
independent_session: true (fresh Claude Code subagent invocation; no shared
  conversational state with the Coordinator sessions that authored/notarized
  PREREG-4, the lead producer, or the concurrent Validator task)
host_measured: vm, Linux-6.18.5-fc-v20-x86_64-with-glibc2.39, Python 3.11.15,
  numpy 2.4.6, fpylll NOT INSTALLED (ModuleNotFoundError, confirmed live in
  this session's own process, see probes/probe_independence_and_coverage_
  output.json THIS_PROBES_OWN_fpylll_check) -- NOTE: this is the SAME host
  string, kernel, Python and numpy version the lead producer's own
  run_manifest.yaml reports. This is a property of the sandboxed execution
  recipe this harness uses, not a claim my review shares process state with
  the producer run, and PREREG-4/dispatch_queue.json's own independence_note
  already flags this class of correlation as unresolved in this goal.
```

## Commit verification (change-set equality, checked myself)

`git show --name-status` + `git diff-tree --no-commit-id --name-only -r`
against both cited commits, run in this worktree:

- `1e1acf08b151dd31b4d41b8afd287d261adce1e5` (PREREG-4 notarization,
  `TASK-20260813-e24ad9`): exactly 3 added paths
  (`snapshot-receipt.json`, `prereg.md`, `prereg_sha256.txt`) — **3/3**,
  matching `declared_path_set`. `git show <parent>:.../prereg.md` fails
  ("exists on disk, but not in `d2ee472a4`") — negative test holds.
  `git ls-tree -r <commit> -- .../TASK-20260813-ea2e96` returns only
  `task_card.md` (a batch-opening coordination artifact) — **zero producer
  artifacts**. `git log --all --follow` for `prereg.md` returns **exactly 1**
  commit. Both commits are ancestors of `HEAD` (`git merge-base
  --is-ancestor` on each, exit 0).
- `6ad64048dfee5b87b9df7ebcd9d7f7b80baf44cb` (lead snapshot,
  `TASK-20260813-2d6b5e`): exactly 8 added paths, matching
  `declared_path_set` exactly — **8/8**.
- `prereg_sha256.txt` (`ff577564d...fbbda`) matches `sha256sum prereg.md`
  computed independently in this session.

Both archives verify as claimed. I found no notarization defect.

## Verdict, stated up front

The mechanical arithmetic is correct given the frozen inputs and PREREG-4's
own precedence rule; `T-INDVERIFY-ARTIFACT-PARTIAL` is the branch that fires
from the reported numbers, correctly per-cell-split per PREREG-4 §2.6's own
"reports BOTH" clause. **The primary target — is `ROUTE-I'` genuinely
non-code-shared — holds up under a line-level diff and a structural,
environment-verified argument that it *could not* have shared the barred
kernel even if it wanted to** (§1 below). **The lam1n half is the strongest
result: independently calibrated and, by my own reasoning, not "too clean"
for what it is.** **The hkz half fires `T-INDVERIFY-ARTIFACT` correctly under
PREREG-4's literal, frozen text — but I built two independent controls that
both point toward "reduction-DEPTH confound" rather than "code-sharing
artifact" as the better-supported explanation for *why* the branch fired,
and PREREG-4's own MEANS-text for that branch attributes it to code-sharing
specifically.** This is the central overclaim risk of this batch, named in
§7 below, and it does not reopen or reverse the frozen branch call — it
narrows what a reader may conclude the branch's firing *establishes*.

---

## 1. Primary target — is `ROUTE-I'` genuinely non-code-shared? (BUILT, not asserted)

**Probe:** `probes/probe_independence_and_coverage.py` →
`probes/probe_independence_and_coverage_output.json`.

I extracted `make_A`/`build_basis`/`hkz_profile` verbatim (by regex, not
manual transcription) from all three barred files (`measure_am4.py`,
`measure_relvar.py`, `replicate_l7l8.py` including the `BATCH-4ed139` copy)
and diffed each against every function `measure_route_reimpl.py` defines
(`make_A_indep`, `build_basis_indep`, `gso_full`, `refresh_row`,
`lll_reduce`, `enumerate_svp`), using both a character-level
`difflib.SequenceMatcher` ratio and an exact longest-common-consecutive-line
scan (a non-fuzzy verbatim-copy detector, threshold 5 lines).

**Result: `n_verbatim_copy_flags = 0`.** No barred function shares 5 or more
consecutive lines with any reimpl function. The two functions with the
highest similarity ratio (`build_basis` vs `build_basis_indep`, ratio
0.54–0.74 depending on source file) are the ones PREREG-4 §2.2(3) explicitly
and correctly carves OUT of the independence requirement: both are 5-line
block-matrix constructions (`B = [[I_k,A],[0,qI_{d-k}]]`) dictated entirely
by the *definition* of the lattice, not by any algorithmic choice — there is
essentially one natural way to write this in numpy, so a nonzero similarity
here is expected and uninformative, exactly as PREREG-4 anticipated. The
functions that matter — the reduction/enumeration step `hkz_profile()`
performs — have NO meaningful overlap (`ratio` 0.28–0.29, `lcl` = 1 line, the
common line being a shared `return` or `for` boilerplate token, checked by
eye against the raw diff).

**Stronger than the diff: an environmental impossibility argument, checked
in this probe's own process, not assumed.** All three barred `hkz_profile`
implementations hard-import `fpylll` (`IntegerMatrix`, `GSO.Mat`, `LLL`,
`BKZ`, `Enumeration`) — confirmed by regex over the actual committed source.
This probe's own process re-ran the `import fpylll` check independently
(not trusting the lead's report) and found it unavailable
(`ModuleNotFoundError`), matching the lead's own finding. **This means the
barred kernel's reduction step could not have been called successfully in
this environment by ANY script, regardless of whether it were imported** —
an additional, independent line of evidence beyond the code diff that
`ROUTE-I'`'s reduction/enumeration path did not and structurally could not
derive from the barred lineage here.

**A genuine (if minor) discrepancy I found and did not smooth over.** The
lead's report, implementation-choice declaration point 6, states verbatim:
*"No fpylll import, no fpylll call, ... appears anywhere in this script."*
Taken literally this is **false**: line 401 of the committed script reads
`import fpylll  # noqa: F401`. By direct inspection this sits inside a
try/except block used ONLY to test whether fpylll is installed
(`environment_check.fpylll_available`); it raises `ModuleNotFoundError` and
is caught, feeds no subsequent computation, and no `lam1n'`/`hkz'` value
derives from it. **The substantive claim holds; the literal sentence
overstates it.** A naive substring search for the three barred module names
similarly "hits" 3 times in the script, but every hit is inside the
`IMPLEMENTATION_CHOICE_DECLARATION` string literal disclosing what was
*not* imported — `reimpl_real_barred_module_import_statements` (a check
restricted to genuine `import`/`from` statement lines) is empty. Reported
at full weight because the task explicitly asks that claim 6 be checked
against the script rather than trusted from prose; it is checked, and found
technically imprecise but not load-bearing.

**Second Target — the ROUTE-P exclusion discipline (also BUILT).** A naive
grep of the committed script and `results_route_reimpl.json` for
`results_l7l8.json`/`results_am4.json` DOES match (my probe's raw count is
nonzero) — but every match is inside `RC3_TEXT` or
`IMPLEMENTATION_CHOICE_DECLARATION`, string literals PREREG-4 *requires* to
name these files as excluded. I refined the check to distinguish a path
variable that is actually `open()`/`sha256_file()`'d from a filename
mentioned in disclosure prose: **no `results_l7l8`/`results_am4` `*_PATH`
variable is ever defined or opened anywhere in the script.** Confirmed.

**One traceability gap found, worth naming though it is not a ROUTE-P
violation.** `RESULTS_C3LANE_PATH` and `PREREG4_PATH` are *defined* in the
script but never passed to `open()`/`sha256_file()` anywhere — dead code.
Yet `run_manifest.yaml`'s `input_shas` lists a sha256 for
`results_c3lane.json` with a note that it was "read only to confirm this
batch's own understanding." **That hash could not have been produced by
this committed script**, since the script never reads that path — it was
computed some other way (a shell `sha256sum`, or a read outside this
script) during report-writing. Minor provenance gap, not a ROUTE-P
exclusion violation (`results_c3lane.json` is neither barred file), but the
manifest's implicit claim that every listed input was read *by this script*
does not hold for this one entry.

**Third target — independent coverage re-derivation (also BUILT).** I
re-read `results_relvar.json`'s `G_REL1` block myself, without importing the
lead's script or its JSON output, and independently rebuilt the 18-cell
table from scratch: **12/18 covered, exactly matching the lead's own
obligation-0 table**, with all 6 middle-beta cells (`L7_b10`, `L9_b15`,
`L11_b20` × 2 candidates) genuinely uncovered — confirmed, not merely
trusted.

---

## 2. Is lam1n's ~1e-15 agreement "too good", reasoned quantitatively (not qualitatively)

**This is the question the task card asks me to reason about quantitatively,
and I built two controls to do so** (`probes/probe_rdet_null_control.py`).

**Why exact agreement on the *combinatorial* part is expected, not
suspicious.** `lambda_1^2` is an exact integer (a sum of squares of an
integer combination of an integer basis) with a UNIQUE correct value. Two
CORRECT implementations of exact SVP enumeration — regardless of code —
*must* land on the identical integer, because the decision problem they are
both solving has one right answer. "Bit-identical agreement on an exact
combinatorial invariant" is not evidence of shared code; it is evidence
both sides solved the same well-posed problem correctly. I verified in
`measure_relvar.py` (lines 316–336) that ROUTE-P's own `r[0]` is exactly
this: a BKZ+explicit-HKZ-sweep-plus-independent-enumeration-verified value,
i.e. ROUTE-P *also* certifies `lambda_1` exactly, not approximately — so
both sides are targeting the same certified exact quantity, and agreement is
the *expected* result of two correct computations, not an artifact.

**The genuinely interesting question is the POST-PROCESSING residual (the
1e-15–1e-14 `D_route'`), and I traced its structural source.**
`measure_relvar.py` line 349 computes ROUTE-P's `logdet` as
`0.5 * sum(log(r_i))` over the FULL, `d`-long reduced-GSO-norm sequence — a
sum of `d` independent float64 log terms. `measure_route_reimpl.py` computes
`logdet` as the closed form `(d-k)*log(q)` — a SINGLE log evaluation. These
are two mathematically identical but numerically DIFFERENT floating-point
paths to the same quantity, and `lam1n = exp(0.5*log(lambda1_sq) -
logdet/d)` propagates whichever residual that difference produces. This is
exactly the kind of genuinely-different-code-path floating-point
disagreement the task asks me to look for.

**Built null-object control, quantified.** rdet is algebraically forced to
have EXACTLY ZERO true dispersion (`results_relvar.json`'s own
`"P-R5_rdet_lam1n_REL1_forced_zero"` / `forced_arithmetic` blocks;
`|det B| = q^{d-k}` independent of `A`). I recomputed rdet completely fresh
(imports nothing from any committed script) via THREE independent numeric
paths — `np.linalg.slogdet` (mirroring ROUTE-P's own `rdet_of`),
`(d-k)*log(q)` (mirroring ROUTE-I''s closed form), and a from-scratch
Gram-Schmidt `0.5*sum(log(sqn_i))` on the UNREDUCED basis (mirroring the
*structure* of ROUTE-P's `hkz_profile` logdet, though not its reduced
input) — and compared each against ROUTE-P's own archived `G_REL1.rdet`
values.

| lattice (d) | via `slogdet` vs ROUTE-P | via `sum-of-d-logs` GSO vs ROUTE-P |
|---|---|---|
| L7 (20) | **0.0** exactly | 1.32e-11 |
| L9 (30) | **0.0** exactly | 2.03e-10 |
| L11 (40) | **0.0** exactly | 5.27e-10 |

**Reading, reported at full weight including where it complicates my own
argument.** The `slogdet`-vs-`slogdet` comparison is EXACTLY zero at every
lattice — because both sides call the identical numpy/BLAS primitive on a
bit-identical matrix on the same machine, so there is no algorithmic freedom
left to produce a residual; this shows bit-identical agreement is NOT
automatic between "different" code, but IS automatic when the operation
itself is identical. The `sum-of-d-logs`-vs-`closed-form` residual DOES
grow with `d` (1.3e-11 → 2.0e-10 → 5.3e-10, roughly a 40× growth for a 2×
dimension increase) — the correct qualitative direction for a genuine
floating-point accumulation mechanism, an artifact-tell check the parameter
`d` should destroy a spurious flat/zero residual and does not. **But this
proxy over-estimates the true floor by roughly 3–5 orders of magnitude
relative to the observed lam1n' `D_route'` (1e-15 to 1e-14)**, because my
proxy sums logs over an UNREDUCED basis (huge dynamic range: unit-norm rows
next to norm-`q≈3329` rows, poorly conditioned Gram-Schmidt), whereas
ROUTE-P's actual `logdet` sum runs over a REDUCED, well-conditioned
HKZ-quality basis. **I am reporting this mismatch plainly rather than
picking the control that flatters my conclusion**: my calibration control is
directionally right (grows with `d`, several orders above exact-zero,
several orders below `hkz`'s residual) but is not numerically precise
enough to certify the exact 1e-15 figure — a tighter control would need to
sum logs over an *already-reduced* basis, which I did not build here for
budget reasons (named as the next concrete action, §9).

**Bottom line on lam1n, stated at the precision the evidence supports.** The
observed `D_route'` (1e-15 to 1e-14) sits comfortably inside the range
bounded below by "same-operation exact-zero" and above by "worst-case
unreduced-basis accumulation noise" (5e-10) — it is NOT implausibly small
for a genuinely different code path on an exact combinatorial quantity, and
I found no evidence it is "too clean." I could not build a control precise
enough to certify the *exact* 1e-15 magnitude as expected rather than
merely plausible; I name that gap rather than paper over it.

---

## 3. hkz's disagreement (0.015–0.223): reduction-quality confound, or code-sharing artifact? (BUILT control, per the task card's exact instruction)

**The task card asks for the exact control**: run the SAME code-shared
lineage forced to LLL-quality reduction. **I could not build that exact
control — infrastructure-blocked, checked directly, not assumed**:
`measure_am4.py`'s `hkz_profile` hard-imports `fpylll` at call time; without
it the barred lineage cannot run at all in this environment (§1 above; this
probe's own process re-confirmed `fpylll` absence). This is INFRASTRUCTURE
SIGNAL (AGENTS.md rule 5), reported as such, not smoothed into a result.

**The cheapest available proxy, BUILT** (`probes/probe_second_lll_hkz_control.py`,
660.1s total, all 3 lattices × 8 bases, no SVP enumeration needed for `hkz`):
a SECOND, independently-structured LLL implementation — different GSO
bookkeeping (full recompute per outer iteration rather than the lead's
incremental single-row refresh), written fresh in this probe file, importing
nothing from `measure_route_reimpl.py` or any barred file — computing `hkz`
at the 6 currently-covered cells.

| cell | this probe's independent LLL vs ROUTE-P | vs lead's own `route_i_prime` |
|---|---|---|
| hkz/L7_b5 | 0.05862 | 0.0 (exact) |
| hkz/L7_b15 | 0.01529 | 1.78e-15 |
| hkz/L9_b7 | 0.10763 | 8.88e-16 |
| hkz/L9_b22 | 0.04993 | 0.0 (exact) |
| hkz/L11_b10 | 0.22346 | 6.22e-15 |
| hkz/L11_b30 | 0.09637 | 2.66e-15 |

**Two findings, reported together because they cut in different
directions.** (i) A SECOND, independently-coded LLL route ALSO disagrees
with ROUTE-P's HKZ pipeline at essentially the SAME magnitude at every
covered cell — supporting "any LLL-quality route disagrees with ROUTE-P by
roughly this much" as a property of the reduction METHOD, not an artifact of
the lead's own particular implementation choices. This is real, additional,
buildable evidence for the reduction-quality-confound reading over the
code-sharing reading. (ii) **My independent LLL implementation and the
lead's own independent LLL implementation agree with EACH OTHER to
1e-15-scale machine epsilon at every cell** — i.e. two differently-coded
`LLL(delta=0.99)` routines converge to the SAME reduced-basis GSO tail
profile. On reflection this is the expected behaviour of a largely
CANONICAL, deterministic textbook algorithm (fixed delta, fixed
round-to-nearest convention leaves little room for path-dependent
divergence for this instance family) rather than a second instance of the
"too-clean-to-be-independent" worry: unlike an ARBITRARY choice, LLL with a
fixed delta and rounding rule has one well-defined output for a fixed input,
so two correct implementations SHOULD converge, exactly as two correct SVP
enumerations converge on `lambda_1` (§2). I flag this explicitly so it is
not mistaken for the SAME finding as lam1n's calibration — it demonstrates
implementation-to-implementation *consistency* of the LLL route, not
agreement WITH ROUTE-P, and the two should not be conflated.

**Order-of-magnitude check against the null-control floor.** hkz's reported
`D_route'` (0.015–0.223) is **3 to 6 orders of magnitude larger** than
*either* null-control reading from §2 (0.0 exact, or up to 5.3e-10 for the
worst-case unreduced-log-sum proxy) at every lattice. Whatever the true
explanation, hkz's disagreement is definitively NOT floating-point noise of
any kind measured here or in this goal's own prior calibration
(`EV-MLKEM-aa39ad` OBS-1, `rdet_T1_ambient_isometry_residual = 3.865e-12`,
itself an order of magnitude below hkz's smallest cell). I did not find or
attempt to source a published LLL(0.99)-vs-HKZ root-Hermite-factor gap
figure at `d=20`–`40` to cross-check against literature (out of this
review's budget); this is named as an unfulfilled check rather than
implied to have been done.

---

## 4. The termination clause's precedence and the revisit condition (Fourth target)

Independently re-derived from `R-IV-OUT-2`/`R-IV-OUT-3` (not imported from
the lead's `R-IV-OUT-4`): `COVERED` non-empty (12), `SOME-ARTIFACT` true (6
hkz cells `DOES NOT EXCEED`), so `T-INDVERIFY-ARTIFACT` fires under
PREREG-4 §2.6's stated precedence (`SOME-ARTIFACT` dominates `ALL-SURVIVE`
whenever both could be read from the same data — here they can, per-cell,
by candidate). `|COVERED| = 12 < 18` ⇒ `-PARTIAL` suffix correctly applied.
PREREG-4 §2.6's own "reports BOTH" clause (a batch that fires ARTIFACT at
some cells and would independently have fired CONFIRMED at others reports
both, per-cell) is applied correctly: the 6 lam1n cells, which independently
satisfy `ALL-SURVIVE` among themselves, are reported under
`T-INDVERIFY-CONFIRMED`'s license; the 6 hkz cells under
`T-INDVERIFY-ARTIFACT`'s license. **The revisit condition (§2.8) is stated
with the exact 6 cells named** (`hkz/L7_b5`, `L7_b15`, `L9_b7`, `L9_b22`,
`L11_b10`, `L11_b30`) — not diluted into a vague caveat. Confirmed correct.

---

## 5. The L11 3-of-24 timeout exclusions — bias check (BUILT, not just asked about)

I recomputed, from the already-archived `route_i_prime_per_basis_log`, what
`D_route'` for `lam1n/L11` would have been had the 3 timed-out bases
(indices 1, 5, 6) been INCLUDED using their "best value found before
timeout" (not the naive LLL-vector upper bound, which would be even larger
— the enumeration's `best[0]` improves on that whenever it finds a shorter
vector before the cap):

| basis | route_p | route_i_prime (best found, unproven) | abs diff |
|---|---|---|---|
| 1 | 1.6997111305 | 1.6997111305 | 4.66e-15 |
| 5 | 1.6527117774 | 1.6803427432 | **2.76e-2** |
| 6 | 1.6178652206 | 1.6178652206 | 2.89e-15 |

**Two of the three timed-out bases (1, 6) were already essentially exact**
(residual at the same 1e-15 scale as the 5 "proven exact" bases) despite not
being certified within the time cap — their exclusion, while methodologically
conservative and correctly disclosed, made no material difference. **The
third (basis 5) genuinely did not converge and carries a real, large
residual (0.0276)** — comparable in scale to several hkz cells. Had it been
included instead of excluded, `D_route'` for `lam1n/L11_b10`/`L11_b30` would
have risen from the reported 9.99e-15 to 0.0276 — **but the verdict would
NOT have flipped**: `s_c^fib = 0.0388 > 0.0276`, so `EXCEEDS` still holds,
just with a materially narrower margin (≈1.4×) than the reported figure
suggests. **Answering the task card's question directly: the exclusion
choice did not bias the reported CONFIRMED verdict for lam1n in this run,
but the margin is closer than the headline "near machine epsilon" framing
implies, and a single additional non-convergent basis at this margin could
plausibly have flipped it.** This is exactly the kind of check that could
have failed and did not — but it came closer to failing than the report's
own framing discloses.

---

## 6. "For each obligation, the arrangement in which it could not have failed"

- **RC-3 carry.** Could not have failed if the claim "carried verbatim" were
  never checked against the source text. I diffed `RC3_TEXT` (extracted from
  the committed script) against PREREG-4 §1's blockquoted text directly:
  **exact match** modulo one em-dash→`--` ASCII substitution (a typographic,
  non-substantive normalization). A real, could-have-failed check, and it
  passed.
- **Obligation 0 (coverage audit).** Could not have failed if computed AFTER
  seeing `D_route'` (allowing post-hoc cherry-picking of favorable cells).
  The script computes it structurally first and independent of any
  `D_route'` value; my own from-scratch re-derivation (§1, Third target)
  matches 12/18 exactly. Genuine, could-have-failed, passed.
- **Obligation 1 (matched-basis exclusion).** Could not have failed if the
  exclusion criterion (`svp_exact`) were a function of the comparison OUTCOME
  rather than of search convergence alone. §5 verifies this directly: 2 of
  the 3 excluded bases turned out to already be non-materially-different had
  they been included, and the one that mattered did not flip the verdict —
  consistent with a criterion that is genuinely convergence-based, not
  outcome-based.
- **ROUTE-P exclusion discipline.** Could not have failed under a check that
  only greps for the filename substring (§1, Second target shows this gives
  a FALSE positive). My refined, structural check (path-variable-opened, not
  merely mentioned) is stronger but has a **named limit**: it would miss a
  deliberately obfuscated read (e.g. a path built by string concatenation
  with no `_PATH`-suffixed variable, or a hardcoded literal never assigned to
  a name). I found no such obfuscation by manual inspection of the full
  script, but my automated check does not itself rule it out — disclosed as
  a limitation of my own probe, not resolved.
- **Termination-branch precedence.** Could not have failed if the branch
  were a fixed function of `|COVERED|` alone rather than of the genuinely
  data-dependent per-cell `VERDICT'` array. §4 confirms the branch is a real
  function of measured data (a different `D_route'` distribution would have
  produced a different branch — e.g., had hkz's `D_route'` come in below
  `s_c^fib`, `T-INDVERIFY-CONFIRMED` would have fired for all 12 cells
  instead).

---

## 7. Premature closure / overclaim check — the narrowest supported statement

**Named directly, per the task card.** `T-INDVERIFY-ARTIFACT-PARTIAL`'s
per-cell hkz license, read WITHOUT the per-cell split and without §3's two
controls, risks being cited downstream as *"BATCH-fbb639's hkz findings were
shown to be a code-sharing artifact."* **That statement is not what this
batch establishes.** PREREG-4 §2.6's own MEANS-text for `T-INDVERIFY-ARTIFACT`
(quoted verbatim from `DEC-20260813-28d7b2`) attributes the branch causally
to *"a methodological artifact of code-sharing"* — but this batch's own
design necessarily CONFOUNDS two changes at once: (a) code independence
(ROUTE-I' vs the barred kernel) and (b) reduction DEPTH (LLL-quality vs
HKZ-quality), because `fpylll` was unavailable and the lead could not build
an independent HKZ-quality route. My two controls (§2's null-object
calibration bounding the floating-point floor at ≤5.3e-10, and §3's second
independent LLL implementation reproducing essentially the SAME disagreement
with ROUTE-P) together point toward reduction DEPTH, not code-sharing, as
the better-supported driver of hkz's `D_route'`. **The lead's own report
already states this caveat** ("at least as consistent with a real
reduction-DEPTH gap... as with a finding about code-sharing"); my
controls make that caveat load-bearing rather than merely hedged prose.

**Narrowest supported statement.** `T-INDVERIFY-ARTIFACT-PARTIAL` correctly
fires per PREREG-4's frozen, literal rule, and its LICENSE (flagging the 6
named hkz cells' `BATCH-fbb639` `EXCEEDS` verdicts as methodologically
unsupported pending a higher-fidelity independent route) should be applied
exactly as written — I am not asking to reopen or reverse the branch call.
But a reader citing this batch is entitled to say only: *"a genuinely
non-code-shared LLL-quality route disagrees with ROUTE-P's HKZ-quality hkz
values by 0.015–0.223 at the 6 covered cells, an amount this batch's own
tests could not isolate as caused by code-independence rather than by
reduction depth, and which two independent LLL implementations reproduce at
essentially the same magnitude."* They are NOT entitled to say *"hkz's
original findings were an artifact of code-sharing"* — that attribution is
not established here, and PREREG-4's own MEANS-text should not be read as
having established it either, given the confound this same batch's own
design carries. For lam1n, by contrast, the narrower and better-supported
statement is exactly what the report already claims: the `EXCEEDS` verdict
at the 6 covered cells survives a genuinely independent, non-code-shared
verification, at a residual consistent with (though not precisely
calibrated against) ordinary floating-point disagreement between two
correct implementations of an exact combinatorial invariant.

---

## 8. Where my own findings go against my thesis (reported at full weight)

- My rdet null-control's `sum-of-d-logs` proxy over-estimates the true
  floating-point floor for lam1n by 3–5 orders of magnitude (§2) — I could
  not precisely calibrate the exact 1e-15 figure, only bound it plausibly.
- My "independence" structural check for the ROUTE-P exclusion discipline
  has a real, named blind spot (obfuscated reads) that a more adversarial
  producer could exploit undetected by this exact check (§6).
- The second independent LLL implementation I built agrees with the LEAD's
  own LLL implementation to machine epsilon (§3) — a result that, read
  carelessly, could itself be mistaken for "too clean to be independent";
  I argue this is expected (LLL is largely canonical for a fixed delta and
  rounding rule) rather than suspicious, but I did not build a further
  control (e.g. a THIRD LLL variant with a genuinely different tie-breaking
  rule under near-degenerate Lovász conditions) to test whether this
  canonicality claim itself would break down under adversarial parameter
  choice — named as an open gap, not resolved.
- The L11 basis-5 near-miss (§5) shows the reported "near machine epsilon"
  framing for lam1n/L11 is closer to flipping than the headline implies,
  even though it did not flip in this run.

---

## 9. Next concrete action

**Cheapest, addresses the largest overclaim risk (§7):** in the ledger
archive's decision record, when discharging the `T-INDVERIFY-ARTIFACT`
revisit condition for the 6 hkz cells, state the reduction-depth confound
explicitly alongside the flag — do not let the branch's MEANS-text stand
uncontextualized. This costs nothing beyond a paragraph and directly
prevents the overclaim named in §7.

**Decisive but not yet run by anyone in this goal:** build ROUTE-I' for hkz
using an HKZ-QUALITY route (fpylll installed in a follow-up environment, or
a from-scratch full BKZ-block-`d` + explicit-HKZ-sweep + independent
per-index enumeration implementation matching ROUTE-P's own algorithm
description) rather than LLL-only, and re-run PREREG-4 §2.4's comparison.
This is the only test that actually separates the reduction-depth confound
from the code-sharing question for hkz, and neither this batch nor this
review could build it (infrastructure-blocked, `fpylll` unavailable).

---

```yaml
red_team_report:
  id: RT-20260813-7930a6
  task_id: TASK-20260813-7930a6
  claim_under_review: >-
    BATCH-6e08fe part (b)'s headline: a genuinely non-code-shared
    re-implementation of ROUTE-I (ROUTE-I') for lam1n/hkz at L7/L9/L11 fires
    T-INDVERIFY-ARTIFACT-PARTIAL, split per-cell -- lam1n's 6 covered cells
    (D_route' ~1e-15 to 1e-14) fire T-INDVERIFY-CONFIRMED's license (the
    strongest genuinely independent confirmation claimed in this goal's
    history); hkz's 6 covered cells (D_route' 0.015-0.223) fire
    T-INDVERIFY-ARTIFACT's license, whose MEANS-text (quoted from
    DEC-20260813-28d7b2) attributes the disagreement to "a methodological
    artifact of code-sharing".
  objections:
    - id: RT-4
      severity: MAJOR
      target: "T-INDVERIFY-ARTIFACT's causal attribution for hkz (PREREG-4 section 2.6 MEANS-text)"
      statement: >-
        This batch's own design confounds code-independence with reduction
        DEPTH for hkz: fpylll was unavailable, so ROUTE-I' for hkz is
        necessarily LLL-quality against ROUTE-P's HKZ-quality pipeline --
        two changes at once. I built two controls (a null-object rdet
        calibration bounding the floating-point floor at <=5.3e-10, and a
        SECOND independently-coded LLL implementation reproducing
        essentially the SAME 0.015-0.223 disagreement with ROUTE-P at every
        covered cell) that together point toward reduction depth, not
        code-sharing, as the better-supported driver. PREREG-4's frozen
        MEANS-text nonetheless attributes the branch to "code-sharing"
        specifically. The branch fires correctly per the frozen rule and
        should not be reopened; its causal attribution should not be cited
        without this qualification.
      evidence: >-
        probes/probe_rdet_null_control.py + _output.json;
        probes/probe_second_lll_hkz_control.py + _output.json; section 3 and
        7 of this report
    - id: RT-5
      severity: MINOR
      target: "implementation-choice declaration point 6 (measure_route_reimpl.py)"
      statement: >-
        States verbatim "No fpylll import ... appears anywhere in this
        script." Literally false: line 401 contains `import fpylll` inside a
        try/except environment-capability probe that never succeeds and
        feeds no computation. Substantively correct, literally imprecise --
        checked against the actual script per the task card's instruction,
        not trusted from prose.
      evidence: "probes/probe_independence_and_coverage_output.json, A_primary_independence_diff.FINDING_report_claim_6_precision"
    - id: RT-6
      severity: MINOR
      target: "the L11 3-of-8 timeout exclusion for lam1n (obligation 1)"
      statement: >-
        Recomputing D_route' for lam1n/L11 with the 3 timed-out bases'
        best-found (not naive-upper-bound) values included instead of
        excluded: 2 of 3 were already at 1e-15-scale agreement despite not
        being certified exact; the third carried a real 0.0276 residual.
        Including it would NOT have flipped the EXCEEDS verdict
        (s_c^fib=0.0388 > 0.0276) but narrows the margin from the reported
        "near machine epsilon" framing to about 1.4x -- closer to flipping
        than the headline implies, though it did not flip in this run.
      evidence: "section 5 of this report, computed directly from route_i_prime_per_basis_log in the committed results_route_reimpl.json"
    - id: RT-7
      severity: MINOR
      target: "run_manifest.yaml input_shas entry for results_c3lane.json"
      statement: >-
        RESULTS_C3LANE_PATH and PREREG4_PATH are defined in
        measure_route_reimpl.py but never opened or hashed anywhere in the
        committed script (confirmed by regex over every open()/sha256_file()
        call site). The manifest nonetheless lists a sha256 for
        results_c3lane.json with a note it was "read only to confirm this
        batch's own understanding" -- that hash could not have been produced
        by this committed script. Not a ROUTE-P exclusion violation
        (results_c3lane.json is neither barred file), but a provenance gap:
        the manifest implies every listed input was read by the script, and
        this one was not.
      evidence: "probes/probe_independence_and_coverage_output.json, B_second_route_p_exclusion.ADDITIONAL_FINDING_dead_path_variables"
  required_controls:
    - >-
      Already built and reported (section 3, section 9): a from-scratch
      HKZ-QUALITY route (full BKZ-block-d + explicit HKZ sweeps + independent
      per-index enumeration, matching ROUTE-P's own algorithm) is the ONE
      remaining control that actually separates the reduction-depth confound
      from the code-sharing question for hkz. Neither this batch nor this
      review could build it: fpylll is unavailable in this environment, and
      a from-scratch HKZ implementation at d<=40 was judged out of this
      review's budget after the two cheaper controls already built.
    - >-
      A third, deliberately non-canonical LLL variant (different
      tie-breaking under near-degenerate Lovász conditions, e.g. a
      random-restart or worst-improvement swap rule) to test whether the
      lam1n/hkz independent-LLL-to-independent-LLL agreement found in
      section 3 would survive a genuinely adversarial choice of algorithmic
      freedom, rather than the largely-canonical delta=0.99 textbook
      recursion both this review and the lead happened to choose.
  counterexample_or_mutation: >-
    Built and reported in full: the L11 basis-5 near-miss (section 5) is the
    closest thing to a counterexample found -- a case where a different,
    equally defensible protocol choice (include the best-found value from a
    timed-out enumeration rather than exclude it) would have materially
    changed D_route' (9.99e-15 -> 0.0276) without flipping the verdict, but
    by a margin (1.4x) narrow enough that a slightly less lucky run could
    have flipped it. This does not falsify T-INDVERIFY-CONFIRMED for lam1n
    as reported, but it shows the reported "near machine epsilon" framing
    understates how close the margin actually is at L11.
  baseline_comparison: >-
    Not directly applicable -- this batch's own claim is an independence
    VERIFICATION of an already-reported measurement (BATCH-fbb639's D_route
    comparison), not a new algorithmic result against Pollard-rho/BSGS/a
    specialized baseline; PREREG-4 section 2.0 states explicitly this
    measurement answers only "does a genuinely independent route confirm
    D_route", nothing about attack cost. No baseline comparison is owed or
    attempted by this report, matching the producer's own scope statement.
  heuristic_challenges: []
  cost_model_challenges: []
  reduction_and_scope_challenges:
    - >-
      T-INDVERIFY-ARTIFACT-PARTIAL's MEANS-text attributes hkz's
      disagreement to code-sharing specifically; this batch's own design
      (LLL-only ROUTE-I' forced by fpylll's absence) confounds that
      attribution with a reduction-depth effect this report's two controls
      show is at least as well, and by this reviewer's reading better,
      supported by the data. See objection RT-4 and report section 7 for the
      narrowest supported restatement.
    - >-
      Coverage is correctly narrower than PREREG-3's 18/27 (here 12/18, not
      18/18) because results_relvar.json's own G_REL1 block has no per-basis
      ground truth at any lattice's middle beta -- independently
      re-confirmed in section 1 (Third target), not merely trusted from the
      lead's own obligation-0 table.
  proof_architecture_challenges: []
  narrowest_supported_statement: >-
    For the 6 covered lam1n cells: a genuinely non-code-shared LLL+exact-
    enumeration route, independently structurally verified (line-diff plus
    an environmental impossibility argument, both built), agrees with
    ROUTE-P to a residual (1e-15 to 1e-14) this review found plausible but
    could not precisely calibrate as the EXPECTED floating-point floor for
    two correct implementations of an exact combinatorial invariant -- not
    implausibly small, not certified as exactly the expected magnitude.
    T-INDVERIFY-CONFIRMED's license (citing BATCH-fbb639's EXCEEDS verdict
    for these 6 cells without F-1/RT-1's qualification) is supported, with
    the L11 near-miss margin (section 5) named as a caveat on how close the
    result came to being narrower. For the 6 covered hkz cells: a genuinely
    non-code-shared LLL route disagrees with ROUTE-P's HKZ-quality pipeline
    by 0.015-0.223, reproduced independently by a SECOND, differently-coded
    LLL implementation at essentially the same magnitude, and 3-6 orders of
    magnitude above any floating-point floor measured in this goal.
    T-INDVERIFY-ARTIFACT fires correctly per PREREG-4's frozen rule and its
    LICENSE (flag the 6 named BATCH-fbb639 EXCEEDS verdicts as
    methodologically unsupported) should be applied as written -- but its
    causal attribution to "code-sharing" specifically is not established by
    this batch's own confounded design, and this review's two controls make
    "reduction depth" the better-supported explanation. A reader is entitled
    to cite the flag; a reader is NOT entitled to cite this batch as having
    shown BATCH-fbb639's hkz findings were a code-sharing artifact.
    Coverage is 12/18 (not 18/18); the 6 uncovered middle-beta cells are
    decided in neither direction, unchanged from PREREG-4's own framing.
  next_concrete_action: >-
    Cheapest, addresses the largest overclaim risk: when the ledger archive
    discharges the T-INDVERIFY-ARTIFACT revisit condition for the 6 hkz
    cells, state the reduction-depth confound explicitly in the same record
    as the flag, citing this report's sections 3 and 7 -- a paragraph, no
    new computation. Decisive but not yet run by anyone in this goal: build
    an HKZ-QUALITY (not LLL-quality) genuinely independent route for hkz
    (fpylll in a follow-up environment, or a from-scratch full
    BKZ-block-d + HKZ-sweep + verified-enumeration implementation) and
    re-run PREREG-4 section 2.4's comparison -- the only test that actually
    separates reduction depth from code-sharing for hkz.
  artifact_paths:
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-cdcd88/prereg.md
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/archives/TASK-20260813-e24ad9/snapshot-receipt.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/archives/TASK-20260813-2d6b5e/snapshot-receipt.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/measure_route_reimpl.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/results_route_reimpl.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/report_route_reimpl.md
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/run_manifest.yaml
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/TASK-20260809-cda2f6/measure_relvar.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/TASK-20260809-cda2f6/results_relvar.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/TASK-20260808-2a9085/measure_am4.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-0e930c/replicate_l7l8.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/reviews/TASK-20260813-6ab893/probes/probe_coverage_beta_mismatch_output.json
    - ledger/decisions/DEC-20260813-28d7b2.yaml
    - ledger/evidence/EV-MLKEM-965a37.yaml
    - ledger/evidence/EV-MLKEM-aa39ad.yaml
    - knowledge/findings/KN-FIND-9b5df0.md
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/reviews/TASK-20260813-7930a6/probes/probe_independence_and_coverage.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/reviews/TASK-20260813-7930a6/probes/probe_independence_and_coverage_output.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/reviews/TASK-20260813-7930a6/probes/probe_rdet_null_control.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/reviews/TASK-20260813-7930a6/probes/probe_rdet_null_control_output.json
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/reviews/TASK-20260813-7930a6/probes/probe_second_lll_hkz_control.py
    - coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/reviews/TASK-20260813-7930a6/probes/probe_second_lll_hkz_control_output.json
```
