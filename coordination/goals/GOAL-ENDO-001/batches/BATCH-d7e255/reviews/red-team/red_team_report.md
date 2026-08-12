# Red Team Report — EXP-ICINV-e0cd8f, F4b CLASS-VARYING claim

`RT-20260810-2ee0af` / `TASK-20260810-9bed1d` / `GOAL-ENDO-001` / `BATCH-d7e255`

Reviewed at commit `2abacac36bfe704ee1e4336b954b30cc718cdfef` (the task's
named snapshot). This commit's tree is content-identical, for every path
touched below, to `1721063e42169479062b283ce05f4b3e642a88c1` (the "snapshot
EXP-ICINV-e0cd8f execution (pre-review)" commit the handoff itself names) —
`2abacac36` is its direct child and adds only the two review handoffs, so
reading the run artifacts at `2abacac36` is reading the same committed
snapshot the handoff points at. Only committed state was read; nothing in the
working tree (including any parallel Validator output) was used as evidence.

`claim_tier: toy`, `sota_delta: 0` throughout this report. No ECDLP claim is
made in either direction. No status was changed, no committed record was
edited, no commit was made, zero runs were executed.

## Model/policy note (binding instruction, not optional)

Requested policy: `review-adversarial`. `PYTHONPATH=. python3 -m
orchestration.adapter resolve --role red-team --independent-session` resolves
this policy, in this worktree's configuration, to `anthropic:claude-opus-5`
(effort xhigh). The model actually answering this session is `claude-sonnet-5`
(stated by the runtime environment itself). This is **not** treated here as an
undisclosed downgrade requiring refusal: the precedent red-team report on this
same goal (`RT-20260807-6042b7`, `coordination/goals/GOAL-ENDO-001/batches/BATCH-cb71b5/reviews/red-team/red_team_report.yaml`,
its own `inference` block) records the identical structural fact — "This
Claude Code harness cannot resolve the policy aliases in
orchestration/model-policies.yaml; every alias falls back to the one model the
session runs on" — for that session's own `resolved_model_id: claude-opus-5`.
The fallback is a standing, harness-wide, `model: inherit` limitation
(CLAUDE.md "Model policy note"), not a per-task discretionary act, so it does
not need a fresh Coordinator authorization the way `EXP-ICINV-e0cd8f`'s D-1
(a genuine upward, Coordinator-informed substitution inside a single run) did.
Recorded transparently rather than silently accepted: `requested_policy:
review-adversarial`, `resolved_model_id (adapter, theoretical):
claude-opus-5`, `actual_answering_model: claude-sonnet-5`, `fallback_used:
true`, `model_verified: false` (no adapter probe receipt for this session).
Per the task's own framing, "independent" here means independent context and
a fresh adversarial reading of a snapshot neither model produced, not
independent judgement from a materially different model tier than the
reviewed run (which itself answered on `claude-opus-5` under D-1). This
session's substantive findings below are all machine-checkable facts about
committed JSON/manifest content, directly re-derived from the raw artifacts,
and do not depend on which model performed the check — that is deliberate,
and is the calibration this report uses throughout.

## Claim under review

Over 138 curves of the certified ordinary class `p=4001, t=30, D=-15104`:
five of six exact geometric invariants of the `m=3` Semaev variety's
`f_V`-free Jacobian ideal are CLASS-INVARIANT; the sixth, elimination
`F_p`-factorisation type (F4b), is reported CLASS-VARYING (`{(1,1,1):66,
(1,2):72}`), against a matched control (138 curves, 100 other traces) showing
`{(1,1,1):21, (1,2):68, (3,):49}`.

## A1 — is the control comparison fatal to the finding's significance? (the crux)

**Sharp form of the objection, as directed:** the control set — curves drawn
from 100 *different* traces, i.e. genuinely between-class — exhibits **more**
distinct F4b values (3) than the class under test exhibits **within** itself
(2). If "isogeny-class membership" were the operative variable, the natural
prior is that within-class variation should be a *restriction* of, not
comparable to or exceeding, generic across-curve variation; here the class
shows *less* diversity than the control, not more, and specifically the class
shows **zero** occurrences of the third type `(3,)` (irreducible cubic) that
the control exhibits at 49/138 ≈ 36%. On its face this is exactly the pattern
you would see if F4b is a generic per-curve quantity with no special relation
to isogeny-class membership at all, and the CLASS-VARYING label is doing more
rhetorical work than the comparison supports.

**I pressed further than the stated objection and found the mechanism, which
settles A1 more decisively than the distinct-value count alone.** I
independently re-derived, directly from the committed run artifacts (not
from the report's prose), what the elimination polynomial actually is.

- `RUN-ICINV-geom-m3-v2/per-curve-invariants.json`, curve `(a,b)=(17,1345)`:
  `elimination.polynomial = "x3^3 + 17*x3 + 1345"`.
- That string is `x3^3 + a*x3 + b` **verbatim** — the curve's own Weierstrass
  right-hand side, not a derived object of the Jacobian-ideal elimination in
  any nontrivial sense.
- I checked this against **every one of the 138 class curves and all 138
  control curves** (276 total) programmatically: for each curve, the recorded
  `elimination.polynomial` string equals `x3^3 + a*x3 + b` under the
  representative-mod-`p` sign convention actually used in the file (match on
  138/138 class curves; 138/138 control curves modulo one string-formatting
  case where `b=0` omits the `+0` term — not a mathematical mismatch).
- I independently re-factored `x^3 + a*x + b` over `F_4001` with SymPy for
  five sampled curves (three class, two control) and its factorisation-type
  partition matches the recorded `elimination.factorisation_type` exactly in
  every case, including the specific partition shape, not just the degree
  count.
- Cross-tabulating `factorisation_type` against the already-recorded
  `two_torsion_x_count` covariate across all 138 class curves gives a
  **deterministic, zero-exception** correspondence: `(1,1,1) ↔
  two_torsion_x_count=3` (66/66), `(1,2) ↔ two_torsion_x_count=1` (72/72). The
  control set gives the third leg of the same correspondence:
  `(3,) ↔ two_torsion_x_count=0` (49/49).

**Conclusion: F4b is not an independent geometric discovery about the
`m=3` Semaev variety. It is, on this evidence, exactly the `F_p`-factorisation
type of the curve's own 2-division-related cubic `x^3+ax+b` — i.e. the
classical count/shape of the curve's rational 2-torsion.** That quantity is
already computed by the campaign's *existing*, unedited harness
(`harness/exp_icinv.py:164-169`, `two_torsion_x_count`) with a docstring that
states, in the campaign's own words, written before this experiment ran: *"z
is in {0, 1, 3} and is NOT an isogeny-class invariant: an isogeny can change
the group structure, so curves of the same trace can differ here."* The
elaborate Groebner-elimination-of-a-4-generator-Jacobian-ideal pipeline this
contract built and ran (274–264 s of Sage/Singular/msolve wall time across
two full runs) reproduces, exactly, a fact the codebase already knew and
already flagged as generic — checkable with `sympy.factor(x**3+a*x+b, modulus=p)`
in milliseconds, no Semaev polynomial, no ideal, no Groebner basis, no
backend cross-check required at all.

This also explains why the control shows *more* diversity than the class: the
control's `{21, 68, 49}` split is close to the classical Chebotarev/Galois
density for a "generic" monic cubic over `F_p` with splitting field of Galois
group `S_3` — identity class density `1/6` (→ `(1,1,1)`, expected ≈23),
transposition density `1/2` (→ `(1,2)`, expected ≈69), 3-cycle density `1/3`
(→ `(3,)`, expected ≈46) — which is exactly the behaviour of a "random" curve.
The class's restriction to two of the three generic types, with the
irreducible type at **exactly zero** occurrences (0/138, versus an expected
~46 under the generic rate), is itself real and exact, but it is a classical
fact about how the prime 2 interacts with the CM order of this specific
discriminant (`D_0=-59`; `-59 mod 8 = 5`, which is at minimum *suggestive of*
2 being inert in the maximal order and constraining achievable 2-torsion
Galois types class-wide — **I have not rigorously derived this from CM theory
and flag it explicitly as unchecked**, not asserted). Either way, this is
elementary elliptic-curve/CM arithmetic, not a discovery about Semaev-variety
geometry, and it is a **narrower, more specific, more explainable** fact than
"CLASS-VARYING" as a headline communicates.

**Answering A1 as sharply as instructed: yes, the control comparison
undercuts the finding's significance, and the mechanism I found makes it
worse than the raw distinct-value count alone suggests** — this is not merely
"between-class variance happens to exceed within-class variance"; the
within-class quantity is definitionally the same classical, generic,
non-isogeny-class-specific invariant the harness already knew not to trust for
this purpose.

**Context from the campaign's own prior work (cited, not imported as
evidence — SC-4):** `MATCHED-ORDER-DESIGN.md` §4 E2 (a design document
governing this L1 lane and its sibling `EXP-ICINV-4d33aa`, which I have
otherwise stayed out of per SC-4) already names `r = #{x : x^3+ax+b=0}` — the
same quantity as `two_torsion_x_count` under a different name — as a
confound the campaign had to explicitly stratify on for a *different*
experiment's over-dispersion statistic (citing committed `H-ICINV-6c7920`).
The campaign has prior form for exactly this covariate disguising itself as
signal. I am not importing `EXP-ICINV-4d33aa`'s findings as evidence for
`EXP-ICINV-e0cd8f`'s claim; I note only that the design document common to
both lanes already flagged this exact covariate, which makes it more
striking that F4b's identity with it went uncaught in this contract's own
C-KOSZUL/C-BACKEND discipline (which caught the unrelated D-4 defect at the
same review depth).

## A2 — is CLASS-VARYING the right verdict label for what was found?

The contract's `verdict_definition` fires on "at least one explicitly
exhibited pair of class members differing in at least one family" — verified
directly in `verdict.json:verdict_definition`, and it is exactly that low a
bar. To the execution report's credit, §3's table *does* disclose, in the
body of the document, that 5 of 6 families are `class_constant: true` and
that F4b splits 66/72 (48%/52%) — this is not hidden or buried, and I did not
have to reconstruct it from raw files. The presentation problem is at a
level above the run record: the dispatching commit message and the
handoff's `why_this_matters` both describe this as *"the campaign's first
EXACT, non-statistical result bearing directly on RQ-ICINV-475b5e, the gating
lane"* — language that, combined with a headline binary verdict computed from
a single low-bar family out of six, reads stronger than "5/6 invariant, 1/6
splits roughly evenly and turns out (per A1) to be a re-encoding of a known
generic quantity" supports. I also note a structural asymmetry in the
contract's own falsification apparatus that made this specific failure mode
more likely to slip through: **F2** (falsification for the CLASS-INVARIANT
direction) explicitly requires the control set to be non-constant before an
invariance finding may be read as class-specific — a real, working guard.
There is **no symmetric requirement** for the CLASS-VARYING direction: nothing
in `success_criterion` or `falsification_criterion` requires within-class
variance to be *distinguished from* (e.g. smaller than, or differently
structured than) between-class/control variance before a variation finding is
treated as isogeny-class-relevant. `DECOMPOSITION.md`'s own L1 "decisive test"
description (§3) says the comparison should be "within-class variance against
between-class variance," but `specification.yaml`'s operationalised
`success_criterion`/`verdict_definition` does not encode that comparison into
the verdict logic — it only requires a control-set artifact to *exist*, not
that its outcome constrain the label. That gap is exactly where this finding
fell through.

**Answer:** the low-level table is fair; the headline framing above it is not
earned by the data, and is now demonstrably not earned by the mechanism
either (A1).

## A3 — did the D-4 defect touch the 66/72 split itself?

Checked directly, not taken on the report's word. I diffed
`per-curve-invariants.json` between `RUN-ICINV-geom-m3` (superseded) and
`RUN-ICINV-geom-m3-v2` (primary) programmatically:

- `elimination.factorisation_type` is **identical on all 138 curves** between
  the two runs (0 diffs). `RUN-ICINV-geom-m3/verdict.json` independently
  computes the **same** verdict (`CLASS-VARYING`) and the **same** F4b
  multiset `{(1,1,1):66, (1,2):72}` as `-v2`.
- `betti`, `regularity_of_quotient_S_mod_J`, `s3_support` are identical on all
  138 curves between the two runs (0 diffs each).
- `singular_locus_affine` differs on all 138 curves, but only *additively*:
  the corrected run adds `fp_rational_points`/`fp_rational_x3_values` fields;
  `dimension` and `degree` (the actual F3 primary-invariant values) are
  unchanged on all 138 curves (0 diffs). This matches exactly what D-4
  describes — the fix compared like-with-like quantities and recorded the new
  cross-check fields, without touching the primary geometry.

**A3 confirmed benign, independently, not by trusting the execution report's
assertion.** The D-4 defect was confined to the derived `backend_B_all_agree`
flag; it did not touch the 66/72 split, the verdict, or any primary invariant.

## A4 — is F4b tracking volcano level, or something else entirely?

`true_volcano_level` remains `not_computed` (D-3 stands; I did not compute it
— that would exceed this review's zero-executed-runs budget and is out of
scope for a read-only pass). I cannot confirm or rule out a volcano-level
correlation directly. What I *can* and did check: `two_torsion_x_count` (the
one per-curve covariate that **is** recorded) correlates with the F4b split —
not statistically, but **exactly and deterministically** (A1): every
`(1,1,1)` curve has `two_torsion_x_count=3`, every `(1,2)` curve has
`two_torsion_x_count=1`, with zero exceptions across all 138 class members.
This reframes the question A4 asks: the more important finding is not
"F4b might secretly be tracking volcano level, which the D-3 gap hides" — it
is that F4b **is** (not "correlates with," **is**, as an algebraic identity)
the already-known-generic `two_torsion_x_count`/`r` covariate, which the
harness's own code already documents as *not* an isogeny-class invariant
regardless of what it correlates with at the volcano level. Whether
`two_torsion_x_count` itself stratifies by volcano level is a real,
still-open question — but it is a question about classical CM/2-isogeny
theory, answerable without any further Semaev-geometry computation (see A6),
and D-3's gap does not block answering A1's crux, which is already settled.

## A5 — did the Coordinator's D-1 authorisation predate compute?

**Unchecked — no committed artifact makes this independently verifiable, and
I say so rather than pass it.** I searched every `manifest.yaml`,
`environment.json`, and other run artifact across all six run directories for
a timestamp field (run start/end, artifact write time beyond the qualitative
`artifact_write_order` sequence used for SR4); none exists — no run in this
experiment records wall-clock start/completion timestamps as committed data,
only elapsed `seconds` per curve and aggregate wall-clock totals in prose
(execution_report.md §1). The only durable time signal available is git
commit timestamps: the dispatch commit `5ecab6c78` is `2026-08-10 18:59:57
-0700`, and the pre-review snapshot commit `1721063e4` is `2026-08-10 20:28:50
-0700` — an ≈89-minute window, consistent with (not proof of) the reported
≈3745 s (≈62 min) of run wall-clock plus overhead for the D-6
abandon/restart cycle and git operations. This bounds the *whole session*,
not the specific claim that the Coordinator's `SendMessage` authorisation for
D-1 preceded "any compute." Per AGENTS.md, `SendMessage` traffic is
explicitly undurable ("Messages leave no auditable trace"), so **this
specific ordering claim is structurally unverifiable from the committed
snapshot by design**, not merely unchecked by oversight. I flag this as a
standing process gap worth the Coordinator's attention (a lightweight,
committed pre-compute authorisation stamp — even just a one-line note in the
run's first artifact write — would make this class of claim checkable in the
future) rather than as a specific finding against this run.

## A6 — cheapest next measurement to decisively settle A1

**Already performed, at effectively zero cost, and reported under A1**:
factor `x^3+ax+b` over `F_p` directly (or read the already-recorded
`two_torsion_x_count`) and compare to F4b's `factorisation_type` — this
requires no Semaev polynomial, no ideal, no Groebner basis, and settles that
F4b carries zero information beyond the classical 2-torsion structure. That
check is complete and its answer is exact identity, not correlation.

**What remains genuinely open, and the cheapest way to close it, named
concretely:**

1. **Close D-3 cheaply, without re-running Semaev geometry.** Build the
   already-certified 2-isogeny graph on this class by Vélu (the class census
   and its `(a,b)` pairs are already committed in `EXP-ICINV-180a0d`), assign
   each curve its true 2-volcano level by graph distance to the floor
   (`MATCHED-ORDER-DESIGN.md` §4 E2 already names this exact construction:
   "Build the volcano by Vélu, not by `two_torsion_x_count`"), and
   cross-tabulate level against `two_torsion_x_count`/F4b type. This settles
   whether the observed 66/72 split (and the missing `(3,)` type) is a
   re-encoding of volcano level specifically, or independent of it. Cost: one
   census-scale enumeration plus Vélu isogeny steps on 138 curves — the same
   order of computation as the campaign's own committed `RT-20260807-6042b7`
   §13 stratification on a different class, not a new Groebner run.
2. **Test whether the missing `(3,)` type is CM-theoretic, not sample noise.**
   Repeat the *same zero-Groebner* check (factor `x^3+ax+b` per curve) on 2-3
   more already-enumerable classes at the same `p` (or nearby toy primes)
   with different fundamental discriminants `D_0`, chosen so 2 has a
   *different* splitting behaviour (split / inert / ramified) than the
   `D_0=-59` case here. If the "one factorisation type is class-wide absent"
   pattern tracks the predicted CM splitting behaviour of 2 in `D_0`, that is
   a genuine (if classical) isogeny-class-level fact worth a citation-backed
   writeup; if it does not reproduce, the 0/138 observation here was a
   small-sample artifact of one 138-curve draw. Cost: curve enumeration plus
   cubic factorisation over 2-3 more classes — orders of magnitude cheaper
   than another `EXP-ICINV-geom_m3`-style Groebner run, and requires no new
   backend, no cross-check subsample, and no ideal-theoretic machinery at
   all.

Both of these are cheaper than anything this contract itself ran, and both
are decisive in a way the current F4b framing is not.

## Verdict

**CONFIRMED WITH SCOPE CORRECTION.**

The exact computation is real and I found no defect in it: the 66/72 F4b
split, the verdict, and the underlying per-curve values are correctly
computed and are unaffected by the D-4 predicate bug (A3, independently
verified). This is not a REFUTED finding — nothing here shows the reported
numbers are wrong. But the finding's *significance*, as framed in the
execution report's headline and the dispatching commit message ("the
campaign's first EXACT, non-statistical result bearing directly on
RQ-ICINV-475b5e, the gating lane"), is not supported at that strength:

- (A1) the between-class control shows *more*, not less, diversity than the
  within-class result, which is the opposite of the pattern a genuinely
  class-specific signal should show; and, decisively,
- (A1, extended) F4b is — as an exact, independently-verified algebraic
  identity across all 276 sampled curves, not a statistical correlation — the
  classical `F_p`-factorisation type of the curve's own `x^3+ax+b`, i.e. the
  rational 2-torsion structure, which the campaign's own unedited harness
  code already documents as **not** an isogeny-class invariant. F4b adds zero
  information beyond a quantity the codebase already had and already knew not
  to trust for this purpose.

The **narrowest supported statement**: at `p=4001, t=30, D=-15104`, under the
declared `f_V`-free ideal, monomial order, and grading, five of six tested
exact geometric invariants of the `m=3` Semaev-variety Jacobian ideal
(monomial support, Betti table, regularity, affine singular locus, elimination
degree) are class-invariant across all 138 members and are *not* explained by
a Koszul degeneration (`koszul_all_regular_sequence_on_class: false`) — this
part is sound and independently re-checkable. The sixth, elimination
`F_p`-factorisation type, does take two values on the class (66/72) — but this
is definitionally the curve's classical rational-2-torsion type, already known
to vary within an isogeny class by ordinary 2-isogeny-volcano theory and
already flagged as non-class-invariant in the campaign's own prior code; it
carries no demonstrated new content about Semaev-variety geometry
specifically, and per this contract's own `success_criterion` its only
license (`min_{E'~E} C(E')` as a target, deferred to `EXP-VOLC-9f5571`) should
not be read as informative for cost-functional target selection until it is
either (a) shown to correlate with an actual solving-cost quantity (first-fall
degree, relation yield — none of which this contract measures, matching the
same "observation-collision" pattern the contract's own §0 already documents
for the `S_3` support drop at `j=0,1728`), or (b) confirmed to add information
beyond `two_torsion_x_count` at all, which on the evidence gathered here it
currently does not.

## Surfaces I could not check

- **A5**: unchecked, and structurally unverifiable from the committed
  snapshot — no run artifact records wall-clock timestamps, and
  `SendMessage` authorisation traffic is explicitly undurable per AGENTS.md.
  Only a ≈89-minute git-commit-level window is available, which is consistent
  with but does not prove the claimed ordering.
- **D-3's volcano-level correlation** (part of A4): not computed here (zero
  executed runs; this review's budget). I checked the one covariate that
  *is* recorded (`two_torsion_x_count`) and found a perfect deterministic
  correspondence with F4b; I did not build the 2-isogeny graph to get true
  per-curve level, and I name that as A6's first concrete next step rather
  than asserting an answer.
- **The CM-theoretic explanation for the class-wide absence of the `(3,)`
  type** (raised under A1/A6): I noted `D_0=-59 ≡ 5 (mod 8)` as suggestive of
  2 being inert in the maximal order, but I did not derive from CM theory
  (Deuring correspondence / class field theory) that this forces the observed
  0/138 rate, and I explicitly did not assert it as established — flagged as
  the second concrete next step in A6.
- I did **not** read or import anything from `EXP-ICINV-4d33aa`,
  `EXP-INSTR-36c8cf`, `EXP-JINV-bd141d`, or `EXP-VOLC-9f5571` (SC-4), beyond
  citing `MATCHED-ORDER-DESIGN.md`'s design-level mention of the `r`/
  `two_torsion_x_count` confound (a document common to this lane, not a
  finding from the sibling experiment) — flagged explicitly under A1.

## Artifact paths read

- `experiments/EXP-ICINV-e0cd8f/specification.yaml`
- `experiments/EXP-ICINV-e0cd8f/execution_report.md`
- `experiments/EXP-ICINV-e0cd8f/implementation.md`
- `experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-geom-m3-v2/{verdict.json,per-curve-invariants.json,control-set-invariants.json,backend-crosscheck.json,manifest.yaml,raw-result.json}`
- `experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-geom-m3/{per-curve-invariants.json,verdict.json,backend-crosscheck.json}`
- `experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-geom-gates/manifest.yaml`
- `harness/exp_icinv_geometry.py` (grep for `two_torsion_x_count` wiring)
- `harness/exp_icinv.py:164-169` (`two_torsion_x_count` definition and docstring)
- `analysis/endomorphism-isogeny-decomposition/DECOMPOSITION.md` (T3/T4/T5, L1 decisive-test description)
- `analysis/endomorphism-isogeny-decomposition/MATCHED-ORDER-DESIGN.md` §4 E1/E2 (design-level `r` confound note)
- `coordination/goals/GOAL-ENDO-001/batches/BATCH-cb71b5/reviews/red-team/{red_team_report.yaml,red_team_notes.md}` (precedent model-policy convention; searched for prior mention of the elimination-polynomial identity, found none)
- `ledger/handoffs/TASK-20260810-9bed1d.yaml`, `AGENTS.md`, `agents/red-team.md`

```yaml
red_team_report:
  id: RT-20260810-2ee0af
  task_id: TASK-20260810-9bed1d
  claim_under_review: >-
    EXP-ICINV-e0cd8f RUN-ICINV-geom-m3-v2: over 138 curves of the certified
    isogeny class p=4001, t=30, D=-15104, five of six exact geometric
    invariants of the m=3 Semaev variety's f_V-free Jacobian ideal are
    CLASS-INVARIANT; the sixth (elimination F_p-factorisation type, F4b) is
    reported CLASS-VARYING (class {(1,1,1):66,(1,2):72} vs. control
    {(1,1,1):21,(1,2):68,(3,):49}), reported as the campaign's first EXACT,
    non-statistical result bearing on the gating lane RQ-ICINV-475b5e.
  objections:
    - >-
      A1: the control (between-class) shows MORE distinct F4b values (3) than
      the class (2), the opposite of the pattern a class-specific signal
      should show; and, decisively, F4b is verified (exact identity across all
      276 sampled curves, class+control) to equal the classical
      F_p-factorisation type of the curve's own x^3+ax+b, i.e. the rational
      2-torsion structure already documented in harness/exp_icinv.py's
      two_torsion_x_count docstring as NOT an isogeny-class invariant. F4b
      adds zero information beyond a quantity the codebase already had.
    - >-
      A2: the CLASS-VARYING headline (dispatch commit message,
      why_this_matters) overstates what the low-bar verdict_definition and the
      report's own 5/6-invariant, 48/52-split table support; the contract's
      falsification apparatus asymmetrically guards the invariance direction
      (F2 requires the control be non-constant) but has no symmetric guard
      requiring within-class variance to be distinguished from between-class
      variance before the variance direction is read as class-specific.
  required_controls:
    - >-
      Cross-tabulate F4b (or two_torsion_x_count) against TRUE per-curve
      2-volcano level (closing D-3) via Velu isogeny-graph construction on the
      already-certified class census -- no new Semaev/Groebner computation
      required.
    - >-
      Repeat the zero-Groebner x^3+ax+b factorisation-type check on 2-3 more
      toy classes with different D_0 2-splitting behaviour to test whether the
      class-wide absence of the (3,) type at D_0=-59 is CM-theoretic or a
      138-curve sample artifact.
    - >-
      Before F4b is used to license min_{E'~E} C(E') as a target
      (EXP-VOLC-9f5571), check it against an actual solving-cost quantity
      (first-fall degree, relation yield) -- none measured in this contract --
      to rule out the same observation-collision pattern the contract's own
      section 0 already documents for the S_3 support drop at j=0,1728.
  counterexample_or_mutation: >-
    Direct re-derivation, not a mutation of the run: for every one of the 138
    class curves and 138 control curves, elimination.polynomial (as recorded
    in per-curve-invariants.json / control-set-invariants.json) equals x3^3 +
    a*x3 + b verbatim (verified programmatically, 276/276, one string-format
    exception at b=0 that is not a mathematical mismatch), and
    factorisation_type corresponds 1:1 and with zero exceptions to the
    already-recorded two_torsion_x_count covariate: (1,1,1)<->3 (66/66, class),
    (1,2)<->1 (72/72, class), (3,)<->0 (49/49, control). This is the cheapest
    possible discriminating check (a single cubic factorisation per curve, no
    Semaev polynomial, ideal, or Groebner basis) and it shows F4b carries no
    information beyond a quantity the campaign's own harness already computed
    and already flagged as generic.
  baseline_comparison: >-
    Not applicable in the ECDLP-solving sense (claim_tier toy, sota_delta 0,
    no attack-cost claim made by this contract). The relevant "baseline" for
    this review is the campaign's own harness: two_torsion_x_count
    (harness/exp_icinv.py, pre-existing, unedited, computable in
    milliseconds with no Semaev/Groebner machinery) versus the m=3
    F4b pipeline (Sage/Singular/msolve Groebner elimination of a 4-generator
    Jacobian ideal, ~270s per full run); the two are shown to be equivalent on
    this class, so the elaborate pipeline buys no signal the cheap baseline
    did not already have.
  heuristic_challenges: []
  cost_model_challenges: []
  reduction_and_scope_challenges:
    - >-
      Scope: claim_tier toy, sota_delta 0, single class at a single toy prime.
      No transfer to another D_0, conductor, arity, or to the f_V-bearing
      formulation is licensed by this contract or by this review, matching
      specification.yaml's own scale_relevance statement.
    - >-
      The contract's own success_criterion licenses CLASS-VARYING to mean
      only "min_{E'~E} C(E') as a campaign target," deferred to
      EXP-VOLC-9f5571 for reachability -- already a narrow license. This
      review's finding narrows it further: that license should not be spent
      on F4b specifically until it is shown to correlate with an actual
      solving-cost quantity, given it is now known to reduce to a classical,
      generic, non-cost-linked invariant.
  proof_architecture_challenges:
    - >-
      Observation-fiber attack on the F4b=CLASS-VARYING reading: hold the
      claimed invariant (F4b factorisation type) fixed and vary the
      underlying object -- every curve sharing a factorisation type shares the
      identical two_torsion_x_count with zero exceptions, meaning F4b's fiber
      over each value is exactly the fiber of the pre-existing, already-known
      two_torsion_x_count covariate. The missing separator between "novel
      Semaev-variety fact" and "restatement of classical 2-torsion structure"
      does not exist on this data; they are the same partition.
  narrowest_supported_statement: >-
    At p=4001, t=30, D=-15104, under the declared f_V-free ideal, monomial
    order and grading: five of six tested exact geometric invariants (S_3
    monomial support, graded Betti table, regularity, affine singular locus,
    elimination polynomial degree) are exactly class-invariant across all 138
    members and are not explained by a Koszul degeneration -- sound and
    independently re-checked here. The sixth, elimination F_p-factorisation
    type, does take two values on the class (66/72) but is, as an exact
    algebraic identity verified on all 276 sampled curves, the classical
    F_p-factorisation type of x^3+ax+b (the curve's rational 2-torsion
    structure), a quantity the campaign's own pre-existing harness code
    already documents as not an isogeny-class invariant. This carries no
    demonstrated content about Semaev-variety geometry specifically and should
    not be cited, on this evidence, as informative for cost-functional target
    selection without further work (see required_controls).
  next_concrete_action: >-
    Close D-3 by building the true per-curve 2-volcano level via Velu on the
    already-certified class census (no new Semaev/Groebner computation) and
    cross-tabulate against two_torsion_x_count/F4b; in parallel, repeat the
    zero-Groebner x^3+ax+b factorisation check on 2-3 classes with different
    D_0 2-splitting behaviour to test whether the class-wide absence of the
    (3,) type here is CM-theoretic or a sample artifact of this one 138-curve
    draw. Both are cheaper than any further Semaev-geometry Groebner run and
    would settle what remains open in A1/A4/A6.
  artifact_paths:
    - experiments/EXP-ICINV-e0cd8f/specification.yaml
    - experiments/EXP-ICINV-e0cd8f/execution_report.md
    - experiments/EXP-ICINV-e0cd8f/implementation.md
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-geom-m3-v2/verdict.json
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-geom-m3-v2/per-curve-invariants.json
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-geom-m3-v2/control-set-invariants.json
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-geom-m3-v2/backend-crosscheck.json
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-geom-m3/per-curve-invariants.json
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-geom-m3/verdict.json
    - harness/exp_icinv.py
    - analysis/endomorphism-isogeny-decomposition/DECOMPOSITION.md
    - analysis/endomorphism-isogeny-decomposition/MATCHED-ORDER-DESIGN.md
  inference:
    requested_policy: review-adversarial
    resolved_model_adapter_theoretical: anthropic:claude-opus-5
    actual_answering_model: claude-sonnet-5
    reasoning_effort: xhigh
    fallback_used: true
    fallback_reason: >-
      Structural, harness-wide: this Claude Code runtime cannot honour a
      per-role model binding at subagent level (model: inherit in every
      .claude/agents/*.md); every policy alias falls back to the one model
      this session runs on. Same standing gap the precedent red-team report
      RT-20260807-6042b7 recorded for this goal, and the same class of gap as
      EXP-ICINV-e0cd8f's own D-1.
    degraded_allowed: null
    degraded_requirements: []
    model_verified: false
    model_verified_reason: "No adapter probe receipt exists for this session."
    independent_session: true
    originated_the_claim: false
```
