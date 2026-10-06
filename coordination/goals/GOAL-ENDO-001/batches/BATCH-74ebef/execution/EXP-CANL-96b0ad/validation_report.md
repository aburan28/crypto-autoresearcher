# Validation report — EXP-CANL-96b0ad, RUN-CANL-78b8bd

- **Validator task**: independent review of TASK-20260810-122b59's execution
  (Executor session) and of Coordinator correction CORR-20260810-308774, scoped
  to `EXP-CANL-96b0ad` / `RUN-CANL-78b8bd` only. `experiments/EXP-ICINV-4d33aa/`,
  `harness/exp_icinv*.py`, `harness/run_fullgroup.py` are out of scope and were
  not reviewed.
- **Snapshot reviewed**: `HEAD` = `ec090f32f243ab8204fe1f95853a78e21061a78d`
  on `claude/ecdlp-endomorphism-analysis-4m2w3z`. Confirmed as a durable,
  Coordinator-committed snapshot (not a working-tree artifact): `git status
  --short` is empty, and the run's own artifact commit (`e294186d`,
  "correct dual-auxiliary-tuple design flaw, fix manifest gap"), the execution
  report commit (`a92d74b7`), and `HEAD` are all mutually reachable ancestors
  (`git merge-base --is-ancestor` confirmed for each). `RUN-CANL-78b8bd`'s own
  `manifest.yaml` records `code.commit: 72d4cbae...`, `dirty: true`, with every
  executed source file individually pinned by sha256 — this commit is also
  reachable from `HEAD`.
- **Documents read in full**: `ledger/hypotheses/H-CANL-e59a06.yaml`,
  `experiments/EXP-CANL-96b0ad/specification.yaml`,
  `ledger/handoffs/TASK-20260810-122b59.yaml`, the execution report,
  `experiments/EXP-CANL-96b0ad/implementation.md`,
  `ledger/corrections/CORR-20260810-308774.yaml`,
  `tools/run_supersession_registry.yaml`, `harness/run_canl.py`,
  `harness/exp_canl.py`, and every artifact under
  `experiments/EXP-CANL-96b0ad/runs/RUN-CANL-78b8bd/` cited below.
- **Verdict: `passed_with_findings`.** Every terminal state, control result,
  certificate, and numeric claim I attempted to independently reproduce
  reproduces exactly from raw committed artifacts — nothing checked here is
  fabricated, cherry-picked, or mischaracterized in direction. CORR-20260810-308774's
  central mathematical claim is independently confirmed. But this review also
  surfaces two findings not previously on record (F4, a required contract
  check that was never executed; F5/F6, a scope gap in what C2's current
  measurements can be said to bear on) that the Coordinator should read before
  drafting a v2 amendment or any evidence record citing this run.

---

## 1. Terminal states re-derived from raw `decision-rule-evaluation.json` — PASS

`decision-rule-evaluation.json`: all five global gates `fires: false`,
`global_state: null`. Applying `specification.yaml`'s `frozen_decision_rule`
by hand: no global gate fires, so both waterfalls are evaluated (matches
`evaluation_order`).

**C1.** Recorded `reason: {null_ok: true, pos_ctrl_ok: true,
dual_aux_tuple_ok: false}`. Per `C1_waterfall...C1_INSTRUMENT_INVALID.fires_when`
("the C1 null-object control reproduces the CM ratio's growth, OR the
small-\|D_E\| positive control fails... OR the dual-auxiliary-tuple consistency
check disagrees for any C1 cell"), any one of the three booleans being adverse
fires this state; `dual_aux_tuple_ok: false` alone is sufficient, and this is
checked *first* in the waterfall (before slope-anomaly, reopen, or supported),
so no C1 verdict beyond `C1_INSTRUMENT_INVALID` was or could have been read.
Matches emitted `c1_verdict.state == C1_INSTRUMENT_INVALID` exactly. I also
read `harness/run_canl.py:c1_waterfall` (lines 706–747) directly: the
`if (not null_ok) or (not pos_ctrl_ok) or (not dual_ok): return
{"state": "C1_INSTRUMENT_INVALID", ...}` branch is exactly this logic, not a
stub or a post-hoc literal.

**C2.** Recorded `reason: {shell_ok: false, threshold_sensitive: false,
dual_aux_tuple_ok: false}` — again matches `C2_INSTRUMENT_INVALID.fires_when`
exactly (any one of three conditions), checked first in C2's waterfall
(`c2_waterfall`, lines 981–997). G3 (`fires: false`) passed, so C2's waterfall
was correctly *evaluated* (not withdrawn as `WITHDRAWN_MISSPECIFIED_G3`) —
confirmed against `raw-result.json`'s `G3.fires: false` and
`G3.per_prime: {1009: true, 10009: true, 100003: true, 1000003: true}`.

**Positive controls (C1).** Reported ratios for D0 ∈ {-3,-4,-7,-8,-11}: 1.0,
1.0, 1.4142135623730951, 1.4142135623730951, 1.7320508075688772. I
independently recomputed these from Lemma 1's own equality case
(`predicted_min = |D|/4` for D even, `(|D|+1)/4` for D odd, `ratio =
sqrt(predicted_min)`): D0=-3 (odd) → (3+1)/4=1 → 1.0; D0=-4 (even) → 4/4=1 →
1.0; D0=-7 (odd) → (7+1)/4=2 → √2; D0=-8 (even) → 8/4=2 → √2; D0=-11 (odd) →
(11+1)/4=3 → √3. All match to full float precision.

No SR8 escalation condition fired (`C1_REFUTED_REOPEN`, `C2_GAIN_EXCESSIVE`,
an independently-reproduced Lemma-1 counterexample) — confirmed directly from
the absence of these states in `decision-rule-evaluation.json` and from G1
(`fires: false`, no counterexample at any of the swept discriminants).

## 2. CORR-20260810-308774's dual-auxiliary-tuple finding — CONFIRMED, independently, and against the run's own actual disagreeing cells

**CORR's illustrative example.** Reproduced with a fresh, from-scratch
brute-force script (stdlib `itertools` only, no import from `harness/` or any
campaign code):

```
weights (1,2) over box {-1,0,1}: {-3,-2,-1,0,1,2,3}          -> 7 distinct sums
weights (1,3) over box {-1,0,1}: {-4,-3,-2,-1,0,1,2,3,4}     -> 9 distinct sums
```
Matches CORR's claimed 7 vs 9 exactly.

**RUN-CANL-78b8bd's actual disagreeing cells.** Loaded `c1-measurements.json`
directly (no code from `harness/`), grouped its 100 C1 cells by `(p, C0,
r_Z)`, and found **50 of 100** cells where tuple A and tuple B disagree on
either the O-arm or the Z-baseline reachable count. Picked the first:
`(p=101, C0=1, r_Z=2)`: O-arm tuple A = `[2,1]`, tuple B = `[3,1]`, reported
`reachable_count` 7 and 9 respectively. My fresh script, working entirely from
the raw `k_tuple` and `C0` fields (never importing `aux_tuple` or
`reachable_residue_count`), computed achievable sums of `2·c₁+1·c₂` and
`3·c₁+1·c₂` over `c₁,c₂ ∈ {-1,0,1}`, reduced mod 101 (no wraparound occurs —
span 6 and 8, both < 101): sizes 7 and 9, matching exactly. This is
**structurally the same weight pair as CORR's own illustrative example**
(`{2,1}` ~ `{1,2}`, `{3,1}` ~ `{1,3}`, same box) — the root cause CORR
identifies is not merely plausible in the abstract, it is the literal
mechanism producing this run's actual measured disagreement. I also
cross-checked the paired Z-baseline cell at the same key (`k_tuple`
`[2,3,1]` vs `[4,5,1]`, reported reachable counts 13 and 19): my independent
computation gives 13 and 19 exactly. **CORR's central claim is correct, and I
confirm it against the run's own data, not merely against CORR's abstract
example.**

## 3. Global gate spot-checks (G2, G4) — PASS

**G2, two of six slopes recomputed.** Read raw `(p, rho_lift)` pairs for
`CM-D0=-3-k17` and `nonCM-a1b3` out of `calibration-certificate.json`, and
refit the log-log OLS slope with a fresh, separately-written implementation
(not `harness/run_canl.py:fit_slope_loglog`): `CM-D0=-3-k17` → my slope
`-1.000889060266041`, reported `-1.000889060266041` (exact match);
`nonCM-a1b3` → my slope `-1.0109746017179118`, reported
`-1.0109746017179118` (exact match). Both inside `-1.00 ± 0.15`. Also spot
checked one raw `rho_lift` value directly (`p=101` on `CM-D0=-3-k17`:
`7/102 = 0.06862745098039216`, matches).

**G4, three of twenty cells recomputed.** Independently recomputed
achievable-sums-mod-101 (fresh script, not `harness/`) for three cells: `C0=1,
k=[2,3,1]` → 13 (reported 13); `C0=1, k=[4,5,1]` → 19 (reported 19); `C0=2,
k=[2,3,1]` → 25 (reported 25); and one saturated case, `C0=5, k=[2,3,4,5,1]`
(wraparound expected, `N=101`) → 101 (reported `reachable_count: 101`,
`closed_form_count: 151`, `matches_closed_form: null` correctly not scored —
this is the right behavior per `z_baseline_cell`'s own `no_wraparound` guard).
All match.

## 4. D7 bugfixes present in final committed code; one certificate independently re-verified — PASS

`harness/run_canl.py:c2_tautology_check.apply_zeta` (lines 808–812) applies
`(x,y) -> (mu*x % p, y)` directly to point coordinates — the geometric
automorphism, not `E.mul(mu, P)` (scalar multiplication). Confirmed by
reading the function body directly; no scalar-multiplication call appears
anywhere in the tautology path. `run_c2`'s per-prime `nonunit`/`shell_lambda`
computation (lines 881–887) uses the curve's own realized `(D_E, f_E)`
throughout (via `curve["D_E"]`, `curve["f_E"]`), not a hardcoded `D_E=-3` —
confirmed by reading `c2_nonunit_lambda` and `c2_shell_lambda_images`, which
both take `D_E` as a parameter derived from the curve dict, never a literal.

**Independent certificate re-verification**, not trusting `verified: true`:
took `certificates/tautology-p1009-0.json`'s three raw points `P=(370,183)`,
`zP=(147,183)`, `z2P=(492,183)` and, using `harness/toycurve.py:EllipticCurve`
on `y²=x³+1` mod 1009 (the curve `c2_congruence_curve` constructs), confirmed
each point is on the curve, then computed `E.add(E.add(P,zP),z2P)` myself: the
result is the identity (`None`), matching `claimed_identity: true` and my own
independent recomputation, not merely the certificate's self-reported field.

## 5. f_E finding — independently recomputed for p=1009 (and, for free, all four congruence primes) — CONFIRMED

Using `harness/isogeny_class.py`'s own committed
`trace_of_frobenius`/`frobenius_discriminant`/`fundamental_discriminant`/`twists_of_j`
directly (no reimplementation): for `p=1009`, curve `y²=x³+1`: `t=62,
D_E=-192, D0=-3, f_E=8` — matches the execution report's table exactly.
Checked all 6 sextic twists of `j=0` at `p=1009` via `twists_of_j(1009, 0)`:
realized `f_E` values are `{8, 27, 35, 8, 27, 35}` — **none is 1**. I extended
this check to all four c2-congruence-ladder primes for completeness (not
required, but cheap): confirmed the reported table
(`p=1009→f_E=8, p=10009→f_E=48, p=100003→f_E=14, p=1000003→f_E=2`) by rerunning
`c2_congruence_curve`'s own construction independently. The finding is
correct: no c2-congruence-ladder prime realizes the maximal order for j=0.

## 6. Shell-count tolerance failures and the C0=1 threshold tie — CONFIRMED, and pushed further (see also §8, "also assess")

**D_E=-67, C0=5** and **D_E=-163, C0=8**: independently re-enumerated the
shell with a fresh, separately-written brute-force search (wide box,
boundary-emptiness sanity check to confirm no truncation): sizes 23 and 37
respectively, against predicted `2π·C0²/√|D_E|` = 19.19 and 31.50 —
relative errors 19.85% and 17.47% (reported 19.9%/17.5%; the small residual
difference is display rounding, not a discrepancy). Both exceed the frozen
15% tolerance. Confirmed.

**C0=1 tie**: independently re-enumerated the nonunit shell for **all 13**
class-number-one discriminants at C0=1 (not just the two cited, D_E=-3 and
D_E=-7): every single one has nonunit shell = exactly `{(0,0)}`, size 1. This
is a stronger fact than "these two happen to tie near the boundary": at
`C0=1`, the minimum nonzero norm achievable by any non-unit element of any of
these orders is provably ≥ 2 (units have norm exactly 1, zero has norm 0, and
no order in this list has a nonzero element of norm strictly between 0 and 2),
so the nonunit shell is **forced** to be exactly `{0}` for *every* tested
discriminant at C0=1, regardless of position relative to the C1/C2 threshold.
See §8 for what this implies for the frozen `C_0_grid_full` choice.

## 7. `harness/toycurve.py` / `harness/isogeny_class.py` edit prohibition — PASS

`git diff origin/main -- harness/toycurve.py harness/isogeny_class.py` is
empty (byte-identical). Checked all five EXP-CANL-96b0ad commits individually
(`ed86640e`, `b68b01ef`, `72d4cbae`, `8b39065d`, `e294186d`) with `git show
--stat -- harness/toycurve.py harness/isogeny_class.py`: none touches either
file. `git diff ed86640e~1 e294186d --stat` over the same two paths is also
empty. Confirmed clean.

## 8. `check_run_source_provenance.py --experiment EXP-CANL-96b0ad --strict` — PASS

Ran it myself: `1 pinned, 0 unpinned, 0 unreadable, of 1 run manifest(s) in
scope / of the pinned, 0 also ran from a fully clean tree`, exit code 0.
Matches the execution report's claim exactly (the "0 also ran from a fully
clean tree" is expected and correctly non-blocking: `dirty: true` with
per-file pinning is what the schema requires when the tree is dirty, and
`harness/run_canl.py` is individually pinned and `status: modified` — the only
modified file, consistent with it being new/uncommitted-at-run-time code).

## 9. D1 (one run record for the whole grid) — defensible for the *artifact layout*, but its deeper choice (aggregate verdicts, not per-prime ones) actively undermines a specific completion-gate requirement for any FUTURE run that reaches a real verdict

The contract's `required_artifacts`/`deliverables` do use a single `<RUN-ID>`
path template for every artifact, and `budget.maximum_runs: 30` has ample
headroom either way — so "one run *directory*" is a defensible reading of the
contract's own internal tension (`budget_note`'s "one run record per
(arm, prime) pair" framing vs. the single-`<RUN-ID>` deliverables list). I do
not think that choice alone is a defect.

But `harness/run_canl.py` goes further than "one directory": it computes and
stores **one aggregate `c1_verdict` and one aggregate `c2_verdict` for the
entire sweep**, not a per-prime verdict rolled up under a shared directory.
Concretely: `c1_waterfall` takes `max(...)` and `any(...)` over **all** 100
C1 cells (5 primes × 5 `C0` × 2 `r_Z` × 2 aux tuples) pooled together — a
single cell from a single prime exceeding `ratio > 1` fires
`C1_REFUTED_REOPEN` for the *entire run*, and reaching `C1_SUPPORTED`
requires *every* cell across *all five* primes to satisfy the bound
simultaneously. The same is true of `c2_waterfall`'s `C2_GAIN_EXCESSIVE`
check (`any` cell across all primes/`C0`/`r_Z`/tuples).

This conflicts with `evidence_strength_calibration_frozen`'s own explicit
design intent: *"Any run reaching a verdict on only one regime... caps the
resulting evidence record at `preliminary`... **and the dissenting
prime/seed must be named**."* That sentence presupposes a code path capable
of identifying and naming a *specific* dissenting prime while still reporting
a graded verdict for the rest — a "4 of 5 agree, 1 named dissent →
preliminary" outcome. The current driver has **no such path**: a single
anomalous cell at one prime (plausible on this exact contract's own evidence —
see the shell-count and C0=1 findings above, which are genuine small-scale
artifacts of *this same class of measurement*) does not degrade to
"preliminary, dissenting prime X named" — it **flips the entire run to the
most escalatory category available** (`C1_REFUTED_REOPEN` /
`C2_GAIN_EXCESSIVE`, triggering SR8, GOAL-ENDO-001 pause condition P3, and a
mandatory `review-breakthrough` escalation) or, for weaker disagreements,
silently prevents `C1_SUPPORTED`/`C2_SUPPORTED` from ever being reached at
all short of unanimity across all 5 (or 4) primes.

**This does not affect the validity of the two `*_INSTRUMENT_INVALID`
verdicts actually reported here** — those fire from conditions (null-object
control, positive control, shell tolerance, threshold sensitivity, dual-tuple
consistency) that are each evaluated globally in the frozen contract's own
text, not per-prime, so D1's aggregation is not the cause of *this* run's
outcome. But it is a real, structural problem for the **next** dispatch this
same driver would produce: if a rerun (after the v2 amendment) clears the
instrument-invalidity gates and reaches genuine per-cell measurements, one
anomalous cell out of hundreds — of exactly the kind this run already showed
can occur for benign, small-`|D_E|`/small-`C0` reasons — would either produce
a false `REFUTED_REOPEN`/`GAIN_EXCESSIVE` escalation or silently block
`SUPPORTED` from ever firing, with no mechanism to report the intended
graceful "preliminary, dissenting prime named" outcome the contract's own
calibration text describes. **This should be fixed in the v2 amendment**,
not left for a third dispatch to discover the hard way.

(Minor, unrelated to the above: the execution report's own text states
*"every measured `reachable_k_count_ratio` across all 200 C1 cells (5 primes
× 5 `C0` × 2 `r_Z` × 2 aux tuples)"* — 5×5×2×2 = 100, not 200, and the
underlying data indeed has exactly 100 C1 cells (`len(c1['cells']) == 100`,
independently counted). A harmless arithmetic slip in the prose, not in any
computed quantity or verdict.)

---

## Findings from independent review (not on the task's numbered checklist)

### F4 (major) — The certificate_semantics (c) reachable-count spot-check, a BLOCKING, explicitly-required check, was never invoked anywhere in this run

`specification.yaml`'s `certificate_semantics` (c) states: *"The exact
reachable-k / reachable-residue counts are `kind: none`... but each such
count is spot-checked by independently recomputing a random 1% sample of the
enumerated residues through a second, separately written reducer function,
and any disagreement on the spot-check makes the cell INVALID rather than
silently trusted."* `invalidation_rules` repeats this as a blocking
condition: *"The certificate_semantics spot-check (1% independent
re-derivation of enumerated residues) disagrees on any cell -> that cell is
INVALID."* `harness/exp_canl.py` **defines** exactly this function,
`spot_check_reachable` (lines 293–307, "A SECOND, separately written
reducer... does not call `reachable_residue_count`'s own accumulation loop"),
and exports it in `__all__`. I grepped `harness/run_canl.py` for any call to
`spot_check_reachable`: **there is none.** The function is written but never
invoked by `full_run`, `run_c1`, `run_c2`, `z_baseline_cell`, or
`o_arm_cell` — every one of the 180 exact reachable-count cells in this run
(100 C1 + 80 C2) went unspot-checked.

The execution report's own completion-gate checklist (§6) states: *"[x]
Dual-auxiliary-tuple and certificate spot-check consistency: the dual-tuple
check was run on every cell and its disagreement is reported explicitly...
12 certificate spot-checks (tautology) all independently re-verified `true`."*
This conflates two distinct requirements. The "12 certificate spot-checks"
are the **tautology** certificates under `certificate_semantics` (a) — those
genuinely were independently re-verified (§4 above confirms this). But
`certificate_semantics` (c)'s reachable-count spot-check is a **separate,
independently blocking** requirement that the checklist item's label implies
was also satisfied and was not. This is not a fabrication of a result — no
cell is reported as passing a spot-check it did not undergo — but the
completion-gate self-assessment is inaccurate on this specific point, and a
required verification step is silently absent from a run whose own contract
names it as blocking.

**Consequence.** This does not change either terminal state reported here:
`C1_INSTRUMENT_INVALID` and `C2_INSTRUMENT_INVALID` both fire from other,
independently-confirmed conditions (§§1–2, 6) that do not depend on the
spot-check. But every number reported "for the record, not as a verdict" in
`c1-measurements.json`/`c2-measurements.json` (e.g., the execution report's
"`max(ratio) == 1.0` exactly" across all 100 C1 cells) has not actually
cleared the specific verification step the frozen contract itself requires
before such a count may be trusted rather than merely computed. Before any
future rerun is read for a substantive verdict, `spot_check_reachable` must
actually be wired into `run_c1`/`run_c2`/`z_baseline_cell` — this should be
part of the same v2 amendment pass, not a separate follow-up discovered
later.

### F5 (major) — C2's current reachable-residue-count design assumes the very point-count halving (STEP 1, r_Z = 2·r_O) that H-CANL-e59a06's own assumptions list as OPEN precisely for the non-maximal orders every realized C2 curve in this run sits on

H-CANL-e59a06's `assumptions` block flags explicitly: *"[open] E~(H)/tors is a
PROJECTIVE O-module (hence Z-rank exactly 2·r_O) only guaranteed automatic
when O is maximal (f_E=1, Dedekind). For non-maximal O the module can fail to
be projective."* This is the mechanism's STEP 1 (point-count halving:
"m ≥ r_O+1 = r_Z/2+1, half the Z-only threshold r_Z+1"). §5 above confirms,
independently, that **none** of the four realized C2 curves in this run has
f_E=1.

Reading `run_c2`'s Stage-D cell loop directly (`harness/run_canl.py` lines
896–914): `s = r_Z // 2 + 1` is used as the CM-shell arm's slot count for
**every** C2 cell in this run — i.e., the driver hard-codes the *halved*
slot count for the CM arm regardless of whether the curve's order is maximal,
and compares it against the Z-baseline computed at the *full* `r_Z+1` slots
(`z_baseline_cell`'s `s = r_Z + 1`) — exactly matching H-CANL-e59a06's own
STEP 4 formula, which is the correct comparison **when the halving actually
holds**. But since every realized curve here is non-maximal (f_E ∈ {2, 8,
14, 48}), and projectivity — hence r_Z = 2·r_O — is precisely the fact the
hypothesis's own assumptions list as unverified in that regime, the
`reachable_residue_gain` metric this run computes (and reports "for the
record") is built on an assumed slot count that may not be the curve's
actual requirement. If a non-maximal O's module is not projective of rank
r_O, the true number of points needed for O-dependence at these curves could
be larger than r_Z/2+1 — in which case the CM arm is not entitled to the
reduced slot count its `reachable_residue_gain` denominator (relative to the
Z-baseline at full slots) assumes, and the comparison is not simply "on a
less interesting curve" but potentially **testing the wrong combinatorial
object** for these specific curves.

This is a materially different, and I think more serious, framing than the
"f_E=1 gap" as CORR-20260810-308774 leaves it (required_action item 2: *"decide
whether the f_E=1 gap requires an extended or different C2-congruence-ladder
rule"*). It is not only that the tested curves are a non-maximal-order
variant of the intended claim; the driver's own reachable-count computation
for those curves silently assumes the maximal-order point-count halving that
the hypothesis itself does not certify for them. Answering the "also assess"
question directly: **as currently tested, C2's measurements do not
straightforwardly bear on the regime H-CANL-e59a06 STEP 5 derives its
formulas for**, and the gap is not merely "different regime, still
informative" — the slot-count premise baked into every C2 cell may not even
be the right one for the curves actually measured. The most direct fix is
either (a) extend the C2-congruence-ladder rule to search for an f_E=1 j=0
curve at an accessible toy prime (my own independent check in §5 shows this
fails at all four *frozen* ladder primes, but the ladder rule itself, not
just the primes, could be revisited — e.g. searching a wider prime range or
a different congruence condition), or (b) keep the current primes but
explicitly verify projectivity (or its absence) for these specific
non-maximal orders before trusting `s = r_Z/2+1`, and report the result
un-pooled and explicitly scoped as "assumes projectivity, unverified" rather
than as a number bearing on C2's claim as stated.

### F6 (minor) — The 15% shell-count tolerance is unjustified in the frozen contract, and the two observed failures are exactly where the tolerance is analytically weakest, not merely "small-count" coincidences

Pushing on whether "genuine finite-size effect" is the right characterization
(it is) versus whether 15% was the right number to freeze (I don't think it
was, on the evidence): I computed relative error for every `C0 ≥ 5` shell
cell (65 cells) and sorted by error. The two flagged failures (D_E=-67,
C0=5, 19.85%; D_E=-163, C0=8, 17.47%) are not outliers among otherwise-flat
errors — they sit at the top of a **smooth, monotone-in-the-expected-direction**
ranking: -19 (13.77%), -43 (12.71%), -27 (10.68%), -163 at C0=10 (7.69%,
versus 10.59% at C0=5 for the *same* discriminant). The shell-size formula's
own stated error term, `O(C0·|D_E|^{-1/4}+1)`, has relative weight (against
the leading term `2π·C0²/√|D_E|`) that **grows with `|D_E|` at fixed C0** and
**shrinks with C0** at fixed `|D_E|` — exactly the pattern observed: the two
failures sit at the two *largest*-magnitude discriminants in the frozen
13-entry class-number-one list (`-163` and `-67`, the two largest by
absolute value), and the *same* discriminant's error improves substantially
as `C0` grows. This is real, structurally-predictable behavior of the
formula's own asymptotic error term, not code noise — reinforcing that these
are genuine finite-size effects, not defects.

But the frozen contract (`H-CANL-e59a06` prediction P5) states the 15%
threshold as a bare number, with no derivation of an explicit constant for
the O(...) error term and no citation. Given the error is *systematically*
worst at exactly the two largest-`|D_E|` entries in the frozen discriminant
list — not randomly distributed — a flat percentage applied uniformly across
all 13 discriminants is structurally biased to fail at the tails of the very
list the contract itself froze, independent of any change in `C0`. A v2
amendment revisiting this (CORR's required_action item 2, "should independently
assess... the shell-count tolerance... finding") should either derive an
explicit constant for the stated O(...) bound and set a `C0`/`|D_E|`-scaled
tolerance, or explicitly acknowledge 15% flat is an engineering round number
and treat a marginal miss (17–20%) at the two largest discriminants as
"at the edge of a deliberately rough band," not as a verdict on the
formula's correctness either way.

### F7 (minor) — The C0=1 threshold "tie" is a universal degeneracy of C0=1, not a boundary-specific coincidence between D_E=-3 and D_E=-7

§6 above already reports this as independently reconfirmed for all 13
discriminants, not just the two the execution report cites. Restated as its
own finding because it changes the recommended fix: the C0=1 row of
`C_0_grid_full = [1, 2, 3, 5, 8]` can **never** show a nonzero
threshold-sensitivity signal for *any* discriminant in the class-number-one
list, because the smallest achievable nonzero non-unit norm in any of these
orders is provably ≥ 2 — a fact independent of proximity to the `|D_E| =
4·C0²` boundary. The threshold-sensitivity check (`fires_when` clause of
`C2_INSTRUMENT_INVALID`) will therefore *always* misfire at `C0=1` regardless
of which discriminants are chosen or how the boundary is drawn. A v2
amendment should either drop `C0=1` from the threshold-sensitivity grid
specifically, or state explicitly (as the current contract does not) that the
threshold check only applies for `C0 ≥ 2`.

---

## Answers to the task's "also assess" questions

- **Is CORR-20260810-308774's "mathematical defect in the frozen contract, not
  an implementation bug" characterization correct?** Yes, for the literal
  requirement as frozen ("the two counts must agree exactly" for the specific
  weight values `k_i=i+1`/`k_i=slots+i`) — no implementation choice can make
  that true for these particular integer sequences, which do not satisfy the
  Sidon/mixed-radix separation condition CORR names, and an Executor has no
  authority to silently substitute different weight values while claiming
  compliance with a frozen rule (SR5). But there **is** a narrower,
  implementation-level alternative CORR's required_action does not mention:
  `gate_G4`'s own `z_baseline_cell` already computes, for *each* tuple
  independently, an exact `closed_form_count` and a `matches_closed_form`
  check against *its own* prediction (not against the other tuple) — and this
  already-implemented, already-passing (20/20 cells) per-tuple check gives
  everything the cross-tuple consistency check was trying to buy (catching a
  genuine code bug in the counting/reduction pipeline) without needing the two
  tuples to agree *with each other* at all, and without needing new weight
  values. A v2 amendment could therefore either (a) replace the two tuples
  with a genuinely collision-free pair as CORR proposes, or (b) keep the
  current tuples (or any two convenience tuples) and replace "the two counts
  must agree with each other" with "each tuple's own count must match its own
  closed-form prediction" — reusing the pattern already validated in G4. Both
  are legitimate; (b) is simpler and requires no new number-theoretic
  construction, but does mean C1/C2 lose the (unsound) cross-tuple redundancy
  check entirely rather than gaining a working replacement for it.
- **Are the shell-count tolerance and C0=1 findings correctly "genuine
  finite-size effects, not defects"?** Yes on direction — confirmed
  independently in §6/F6/F7 above, with additional structural evidence (the
  failures track `|D_E|` and `C0` exactly as the stated asymptotic error term
  predicts; the C0=1 tie is universal, not discriminant-specific). But 15% was
  not independently justified in the frozen contract, and the C0=1 grid point
  is unconditionally uninformative for this specific check regardless of
  tolerance — both should be revisited in the v2 amendment, not merely
  reconfirmed as benign and left as-is.
- **Does the f_E=1 gap mean C2's claim says nothing about the regime STEP 5
  derives its formulas for?** See F5. My reading is stronger than "says
  nothing" in one direction (the shell/lambda/unit-group combinatorics of
  STEP 5 itself are generic ring theory, valid for any order, maximal or
  not) and stronger in the other (the specific `reachable_residue_gain`
  metric this run computes assumes the STEP 1 point-count halving that is
  explicitly open for non-maximal orders, and every realized C2 curve here is
  non-maximal) — so the honest characterization is not "a different but
  still-informative regime" but "a regime where a load-bearing premise of the
  measurement's own construction (the slot count) is unverified," which is a
  materially different, narrower claim than either the execution report or
  CORR currently states.

**Do I agree a v2 protocol_amendment is required before any second dispatch?**
Yes, and I think its scope needs to be larger than CORR-20260810-308774's
required_action currently states: (1) the dual-auxiliary-tuple construction
(CORR's own item, confirmed here); (2) wiring in the never-invoked
certificate-semantics (c) spot-check (F4) before any reachable-count number is
trusted; (3) the D1 aggregation-granularity problem (§9), which will silently
either over-escalate a single anomalous cell to `REFUTED_REOPEN`/
`GAIN_EXCESSIVE` or block `SUPPORTED` from ever firing on a future clean rerun,
with no path to the "preliminary, dissenting prime named" outcome the
contract's own calibration text describes; (4) the C2 slot-count/f_E
interaction (F5), which needs an explicit decision (extend the ladder to seek
f_E=1, or explicitly scope the current measurements as premise-unverified);
and (5), lower priority, the 15% tolerance derivation and the C0=1 grid point
(F6/F7).

---

## Artifact paths cited

- `ledger/hypotheses/H-CANL-e59a06.yaml`, `experiments/EXP-CANL-96b0ad/specification.yaml`,
  `ledger/handoffs/TASK-20260810-122b59.yaml`, `experiments/EXP-CANL-96b0ad/implementation.md`,
  `ledger/corrections/CORR-20260810-308774.yaml`
- `coordination/goals/GOAL-ENDO-001/batches/BATCH-74ebef/execution/EXP-CANL-96b0ad/execution_report.md`
- `experiments/EXP-CANL-96b0ad/runs/RUN-CANL-78b8bd/` — `manifest.yaml` and
  `manifest_v2.yaml` (both sha256-verified against `tools/run_supersession_registry.yaml`'s
  `RUN-CANL-78b8bd` entry), `decision-rule-evaluation.json`, `raw-result.json`,
  `c1-measurements.json`, `c2-measurements.json`, `calibration-certificate.json`,
  `lemma1-search.json`, `prime-verification.json`, `tail-checks.json`,
  `command.txt`, `environment.json`, `certificates/tautology-p1009-0.json`
  (independently re-verified against `harness/toycurve.py:add`)
- `harness/exp_canl.py` (`norm_form`, `alpha_min`, `shell_enumerate`,
  `lambda_reduce`, `reachable_residue_count`, `spot_check_reachable` — read,
  the last confirmed never called), `harness/canonical_height.py` (read),
  `harness/run_canl.py` (read in full: `gate_G0`–`gate_G4`, `aux_tuple`,
  `z_baseline_cell`, `o_arm_cell`, `run_c1`, `c1_waterfall`, `run_c2`,
  `c2_waterfall`, `gate_G3`, `full_run`), `harness/isogeny_class.py`
  (`trace_of_frobenius`, `frobenius_discriminant`, `fundamental_discriminant`,
  `twists_of_j` — executed directly, unmodified), `harness/toycurve.py`
  (`EllipticCurve.add` — executed directly, unmodified)
- `tools/run_supersession_registry.yaml`, `tools/check_run_source_provenance.py`
  (executed directly)
- git commits `ec090f32` (`HEAD`, reviewed snapshot), `e294186d`
  (dual-tuple/manifest-gap fix), `a92d74b7` (execution report), `72d4cbae`,
  `8b39065d`, `b68b01ef`, `ed86640e` (EXP-CANL-96b0ad build/run commits,
  checked individually for `toycurve.py`/`isogeny_class.py` non-modification)

## Limitations of this review

- I did not independently re-derive `canonical_height.py`'s archimedean local
  height implementation itself (the mpmath-based doubling/local-height code);
  I relied on G0's own known-answer self-test (multiplication-by-m,
  the zeta_3/i unit checks) and the fact that P2 (`ratio_of_minima`) is
  computed from the exact algebraic formula `sqrt(N(alpha_min))`, not
  transcendentally, per deviation D5 — so no live measurement in this run
  actually depends on `canonical_height.py`'s numerical output beyond its own
  self-test.
- I did not independently re-derive all 6 of G2's covering-fraction slopes,
  the full N1–N5 null battery, or the planted-signal recovery/false-positive
  rates beyond the two slopes and the reasoning already checked in §3; I
  spot-checked rather than exhaustively re-verified.
- I did not exhaustively re-enumerate all 80 C2 shell cells or all 100 C1
  cells; I spot-checked representative cells (including the specific
  disagreeing cell driving the dual-tuple finding, and the two flagged
  shell-tolerance failures) and one saturated/wraparound G4 cell.
- This report makes no claim about H-CANL-e59a06, RQ-CANL-63098f, or
  GOAL-ENDO-001. Toy scale throughout (p ≤ 1000003, ≈20 bits), `claim_tier:
  toy`, `sota_delta: 0`. Neither C1 nor C2 reached a substantive
  (`*_SUPPORTED`/refuted) state in this run — both terminated at
  `*_INSTRUMENT_INVALID` — so nothing here supports or rejects the CM
  dichotomy in either direction, and nothing here bears on an ECDLP claim in
  any direction.
- No hypothesis or goal status is changed by this report, and no evidence
  record is written. That is reserved for the Coordinator, on a separate
  ledger archive, after this and any companion Red Team review return.
