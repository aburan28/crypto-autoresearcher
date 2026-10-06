# Red Team report — EXP-ICINV-e0cd8f v1 (TASK-20260811-d9d01e)

Reviewed at snapshot commit `904841f8`, branch
`claude/ecdlp-endomorphism-analysis-4m2w3z`. Scope per role contract:
interpretation, hidden assumptions, cheapest discriminating control — not
line-by-line arithmetic reproduction (a separate Validator session covers
that). This report is a review artifact; it changes no ledger record and no
hypothesis status.

**Bottom line up front.** The run is procedurally sound — SR1–SR7, F1–F6, and
every declared control (C-GAUGE, C-BACKEND, C-ORDER, C-KOSZUL, C-CENSUS,
C-SUPPORT, C-CONTROL-SET) pass exactly as reported, and I found no defect in
the arithmetic. But the one family the whole `CLASS-VARYING` verdict rests on
— `elimination_factor_partition` — is, by an exact symbolic identity I
re-derived independently below, **the classical rational-2-torsion
factorization type of the curve, nothing else.** That same quantity, under
its usual name (`r` / `two_torsion_x_count`), already exists in this
campaign's own harness (`harness/exp_icinv.py:164`), was already computed on
this exact class in a prior batch (BATCH-cb71b5) with the identical 66/72
split, was already found there to explain none of the campaign's actual
signal of interest ("Neither the 2-torsion count nor `|Aut|` explains the
spread"), and is the explicit subject of a sibling hypothesis
(H-ICINV-6c7920) that treats it as a **sampling-artifact nuisance
covariate**, not a curve-geometry discovery. `CLASS-VARYING` as *computed* is
correct; `CLASS-VARYING` as it is about to be *used* — "licenses
`min_{E'~E} C(E')` as a campaign target" and "promotes EXP-JINV-bd141d and
EXP-VOLC-9f5571" (spec `success_criterion`; DEC-20260810-a4bec4 rationale) —
is not supported without a new argument this record set does not currently
contain.

---

## 1. Is the varying invariant meaningful, or an artifact of the construction?

**It is a re-encoding of a classical, curve-generic quantity — not evidence
about Semaev-variety geometry.**

The elimination step the harness performs
(`harness/exp_icinv_e0cd8f.py:104`, `eliminate(Jaff, x1*x2)` on
`Jaff = <S3, dS3/dx1, dS3/dx2, dS3/dx3>`) computes the locus, in `x3` alone,
where the plane curve `S3(x1,x2;x3)=0` acquires a singular point in `(x1,x2)`
— i.e. the branch locus of the map `(x1,x2,x3) -> x3` restricted to `S3=0`. I
reproduced this symbolically with sympy, treating `a, b` as indeterminates
(same `S3` formula quoted verbatim in `specification.yaml`):

```
R1 = resultant_{x1}(S3, dS3/dx1) = -16*(x2-x3)^2*(x2^3+a*x2+b)*(x3^3+a*x3+b)
```

and, computing the full lex Gröbner basis of `<S3, dS3/dx1, dS3/dx2, dS3/dx3>`
with `x1 > x2 > x3` over `Q(a,b)`, the unique element of the basis lying in
`Q(a,b)[x3]` alone is

```
x3^3 + a*x3 + b
```

— exactly the curve's own Weierstrass cubic, monic, degree 3 (matching the
run's own reported `elimination_poly_degree = 3` on every one of 276 curves).
This is not a coincidence of one curve: it is a polynomial identity over
`Q(a,b)`, hence true after specialization to every `(a,b) mod p` the run
touched. **The "elimination polynomial" the contract spent a Betti-table
pipeline computing IS `x^3+ax+b`.** Its "`F_p`-factorisation type" is
therefore, by identity and not by inference, the count and field-degree of
the curve's rational 2-torsion points — a quantity with no dependency on
Semaev geometry, degree of regularity, or anything the campaign's
`d_reg`/attack-cost axis is chasing. I confirmed the identity empirically too
(not just symbolically): computing `#{x in F_p : x^3+ax+b=0 mod 4001}` by
brute-force root count for all 138 class members and all 138 control members
and comparing against the run's own `elimination_factor_partition` gives
**0/276 mismatches** (script and output below, §5).

So: does class-varying on this family license `min_{E'~E} C(E')` as the
contract's `success_criterion` says? Not as stated. The contract's own T3
rule (`DECOMPOSITION.md` §4, restated in `MATCHED-ORDER-DESIGN.md` line
180-181) treats *any* surviving variation among the seven families as
decisive for the same conclusion, with no mechanism argument differentiating
a family whose variation plausibly reflects Gröbner-solving-relevant geometry
(Betti numbers, regularity — these at least have an established connection to
elimination/solving cost) from a family that is a re-encoding of an
elementary, curve-generic, already-tracked classical invariant. This is
exactly the failure mode the contract itself named and tried to design around
for the S_3-support-drop case (`red_team_notes.md` §11, quoted in the
contract's own preamble: "the observation collision is real and exact and
does not survive projection onto the cost functional"). Removing `f_V` did
not prevent the same failure mode from recurring in a different guise: an
exact, gauge-stable, cross-backend-verified difference that is real and does
not (on current evidence) survive projection onto anything the campaign
cares about.

## 2. The control's three-way split vs the class's two-way split

**Fully explained by elementary group theory plus a fact the campaign already
uses elsewhere (fixed `#E(F_p)` across an isogeny class), with nothing
isogeny-class-specific in the mechanism.**

`t=30` is even, so `N = p+1-t = 3972` is even for *every* member of the
class (isogenous curves share `#E(F_p)` — this is the same "same N" fact the
batch's own matched-order design is built on, cf. DEC-20260810-a4bec4's "T1
transport"). Cauchy's theorem: any finite abelian group of even order has an
element of order 2. So every class member's `E(F_p)` has a rational point of
order 2, so `x^3+ax+b` has ≥1 root mod `p`, so the irreducible-cubic case
`(3,)` is *structurally impossible* on the class — independent of isogeny,
independent of `D_0`, independent of anything the contract is trying to
measure. It would hold identically for *any* set of curves sharing an even
group order, isogenous or not. The control set draws from 92 *different*
traces, roughly half of which give odd `N`; odd `N` forces trivial 2-torsion
by the same Cauchy argument, i.e. forces `(3,)`. I verified this directly:
reconstructing each control curve's trace via the (unedited, read-only)
`harness.isogeny_class.isogeny_classes(4001)` and checking `N mod 2` against
the reported partition gives **0/138 mismatches between "N is odd" and
"partition is `(3,)`"** (script and output in §5). The class/control
three-way-vs-two-way contrast is not evidence of "exploitable within-class
structure" in any sense beyond "the class was constructed by fixing an even
trace, so its `N` never happens to be odd" — which was already known before
this run started (the class definition fixes `t=30`).

The residual, genuinely within-class variation — 66 vs 72 split between
`(1,1,1)` and `(1,2)`, both compatible with the same fixed `N=3972=4·993` —
is real (H-ICINV-6c7920 §"STEP 1" derives, correctly, why: `N` alone doesn't
pin the invariant-factor decomposition `Z/n1 × Z/n2`, only `#E` does, and
whether `n1` is 1 or 2 is not an isogeny-class invariant). That variation is
not a new discovery of this run — see §3.

## 3. Is this actually novel given what's already in the ledger?

**No — this is a rediscovery, at ~900 CPU-seconds of Gröbner/Betti/two-backend
cost, of a quantity this campaign already named, already computed on this
exact class, and already found irrelevant to its actual object of interest.**

`harness/exp_icinv.py:164`, `two_torsion_x_count(p, a, b)`, already commited
and used across `run_icinv.py`, `run_volc_mtgt.py`, `run_blocknull.py`,
`exp_icinv_fullgroup.py`:

```python
def two_torsion_x_count(p: int, a: int, b: int) -> int:
    """z = #{x in F_p : x^3 + ax + b = 0}, i.e. rational 2-torsion x-coordinates.
    z is in {0, 1, 3} and is NOT an isogeny-class invariant: an isogeny can
    change the group structure, so curves of the same trace can differ here.
    """
```

`coordination/goals/GOAL-ENDO-001/batches/BATCH-cb71b5/reviews/red-team/red_team_notes.md`
§C1 (line 101) already reports, on this *exact* class (`p=4001, t=30`, 138
curves): `rate_m3 by two_torsion_x: {1: (72, 0.5334, 0.0348), 3: (66, 0.5275,
0.0365)}` — the **identical 72/66 split**, on the same class, using the
already-existing function, months (in campaign time) before this contract
ran — followed immediately by: "Neither the 2-torsion count nor `|Aut|`
explains the spread." That is, this campaign already tested this exact
covariate against its actual attack-relevant metric (`decomposition_rate_m3`)
and already found it inert.

More directly: `ledger/hypotheses/H-ICINV-6c7920.yaml` (status `specified`,
under the *same* `RQ-ICINV-475b5e`, explicitly not adjudicated by
DEC-20260810-a4bec4) is built entirely around this quantity, calling it `r`,
with an elementary derivation ("`r=3 <=> E[2] subset E(F_p) <=> n1 is even`")
that is line-for-line the same argument I reconstructed in §1–2 above,
independently, before finding this hypothesis. H-ICINV-6c7920 uses `r` as a
**sampling-bias nuisance covariate** — it explains *why* `targets_uniform`
under-covers the group on `r=3` curves, not as a source of curve-to-curve
attack-cost signal — and states explicitly (line 44-46): "`r` is a 2-part
invariant, `N` is a large prime, and by KN-TECH-030 the 2-part is irrelevant
to the discrete logarithm." `KN-TECH-030` (Pohlig-Hellman
reduction/prime-order-subgroup hygiene) establishes that only the largest
prime-order subgroup determines generic/Pohlig-Hellman ECDLP hardness; the
2-part is hygiene, not a hardness lever, in that setting. (Note the scope
limit I am *not* overreaching past: KN-TECH-030 is about generic/rho/PH
hardness, not the summation-polynomial Gröbner-solving-degree axis this
contract targets, so it does not by itself prove 2-torsion structure is
irrelevant to `C(E')` in the index-calculus sense — but it does mean no
existing record in this campaign gives 2-torsion structure a mechanism
argument for mattering to *any* attack-cost axis, generic or specialized;
every existing mention of it treats it as a nuisance to control for.)

Reporting `elimination_factor_partition`'s class-variation as the campaign's
"first real curve-dependent signal" would overclaim its novelty. It is the
same, already-named, already-tested, already-explained quantity, reached this
time via a Betti-table/two-backend computer-algebra pipeline instead of a
five-line root count.

## 4. Does the execution report or run output overstate anything?

**The artifacts themselves are disciplined; the pre-registered decision rule
they satisfy is what needs qualification.** `execution_report.md` repeats,
correctly and multiple times, that it "interprets nothing," that no ECDLP
cost claim is supported, and that removing `f_V` makes any result here
non-transferable to solving time. `verdict.json`'s own `reason` field states
the bare fact ("shows >1 distinct value ... surviving gauge and backend
checks") without editorializing. I did not find a sentence in either artifact
that oversells the result.

What *is* a real risk is upstream of the executor: `specification.yaml`'s
`success_criterion` and `MATCHED-ORDER-DESIGN.md`'s T3 pre-commit, **before
knowing what would vary**, to treat any surviving cross-family variation as
licensing `min_{E'~E} C(E')` "as a campaign target" and as promoting
EXP-JINV-bd141d/EXP-VOLC-9f5571. That pre-registration was reasonable *ex
ante* (per AGENTS rule on not rejecting a result merely for being surprising)
but the record set, taken at face value by a reader who does not independently
do the §1–3 analysis, invites exactly the overclaim the executor was careful
not to state directly: "a real, curve-dependent, control-surviving,
gauge-stable signal was found" reads, without the missing context, as
evidence of something the campaign should chase, when it is a rediscovery of
an already-shelved covariate. The gap is an omission, not a
misstatement — nothing in the required_artifacts asked the executor to check
what the elimination polynomial actually *is*, and the contract's own
"interprets nothing" discipline (correctly) kept that check out of the
execution report. That is precisely the gap this red-team review exists to
fill before any evidence record relies on the result.

## 5. Cheapest falsification control — run, not just proposed

Two checks, both against the committed run's own JSON, no new run, no edit
to `experiments/` or `harness/`:

**(a) Exact symbolic re-derivation** (sympy, `Q(a,b)` coefficients, using the
`S3` formula quoted verbatim from `specification.yaml`):

```python
R1 = sp.resultant(sp.Poly(S3, x1), sp.Poly(diff(S3,x1), x1), x1)
# -16*(x2 - x3)**2*(a*x2 + b + x2**3)*(a*x3 + b + x3**3)
G = sp.groebner([S3, d1, d2, d3], x1, x2, x3, order='lex', domain=QQ.frac_field(a,b))
# unique pure-x3 basis element: a*x3 + b + x3**3
```

**(b) Correlation check against `class-census.json` (which already carries
`a, b` per curve, needing nothing this run didn't already produce) and against
`harness.isogeny_class` for the control's traces:**

```
class:   computed root-count-of-(x^3+ax+b) partition vs run's own
         elimination_factor_partition  -> 0 / 138 mismatches
control: same check                     -> 0 / 138 mismatches
control: (N=p+1-trace is odd) vs (partition == (3,)) -> 0 / 138 mismatches
```

All three checks are exact matches, not statistical correlations — consistent
with §1's proof that the two quantities are identical, not merely associated.
This is the cheapest possible discriminating control (milliseconds, no CAS
backend, data already in the run's own artifacts) and it fully undercuts the
"novel curve-dependent signal" reading while leaving the run's own reported
facts (which values occur, on which curves, gauge-stable, backend-agreed)
completely intact and uncontested.

---

## Required controls before this result licenses anything downstream

1. **Independent reproduction of the `I_3 ∩ F_p[x3] = <x^3+ax+b>` identity**
   by the Validator or Coordinator (trivial — a five-minute Gröbner
   computation) before any evidence record characterizes
   `elimination_factor_partition` as a novel Semaev-geometry signal.
2. **An explicit, cited mechanism argument** for why rational-2-torsion
   structure should affect Gröbner-solving degree / regularity of the
   summation-polynomial elimination system (`f_V`-free or `f_V`-bearing) —
   currently absent from `specification.yaml`, `MATCHED-ORDER-DESIGN.md`, and
   `DECOMPOSITION.md` alike — before EXP-JINV-bd141d or EXP-VOLC-9f5571 is
   described as "promoted" by this result.
3. **A null-object control the contract did not run**: the current control
   (a size-matched set of *other* elliptic curves) cannot distinguish "this
   family's shape is forced by any degree-`(2,2)`-type trivariate object of
   this kind" from "this family reflects elliptic-curve-specific structure."
   Per the inventor protocol's null-object requirement, run the same seven
   families on a size-matched set of *generic* (non-elliptic-curve-derived)
   polynomials of the same bidegree/shape as `S_3` and its partials. If the
   six currently-"constant" families are also constant there, they were never
   testing curve geometry at all, only shape; that would sharpen (not negate)
   the F2 caution the run's own code already computes but only activates on
   full constancy.
4. **A re-audit of the six "constant" families** against the same "is this
   secretly a generic/classical fact and not curve-class geometry" question
   applied to the seventh — the fact that all six are identically constant
   on a 92-trace control drawn from unrelated classes is itself the kind of
   evidence the contract's own F2 clause treats as informative, and it fired
   as a documented risk on every one of the six even though the overall
   verdict routed around it because family seven varied.

## Narrowest supported statement

EXP-ICINV-e0cd8f v1 correctly and reproducibly establishes, by exact
symbolic computation cross-checked on two independent backends and two
monomial orders, that `elimination_factor_partition` is not constant across
the 138-curve class at `p=4001, t=30`. It does **not** establish, and no
record in this campaign currently establishes, that this variation reflects
anything about Semaev-variety geometry, degree of regularity, or attack cost
`C(E')`: the varying quantity is, by exact identity, the curve's classical
rational-2-torsion factorization type, a quantity this same campaign already
computed on this same class (BATCH-cb71b5), already found uncorrelated with
its actual relation-yield metric, and already treats elsewhere
(H-ICINV-6c7920) as a sampling nuisance rather than a discovery. `toy` claim
tier, `sota_delta: 0`, and the contract's own `f_V`-removal non-transferability
caveat all continue to bind and are not disputed here. Six of the seven
primary families being simultaneously constant on the class *and* on a
92-trace control is independently a signal that this `m=3` object may be too
shape-constrained to carry curve-class-specific information at all — a
question the contract's own F2 clause is built to catch but which the
overall `CLASS-VARYING` routing bypassed.

## Next concrete action

Before any Coordinator evidence record cites this run as grounds for
`min_{E'~E} C(E')` or as promoting EXP-JINV-bd141d/EXP-VOLC-9f5571: file the
§1 symbolic identity and the §5 correlation results as a disclosed finding
against this run (they do not change any measured value, only its
interpretation), and require either (a) a stated, checked mechanism argument
connecting 2-torsion structure to Gröbner/elimination solving cost before
using this result to prioritize successor contracts, or (b) explicit
re-scoping of the `CLASS-VARYING` verdict's consequence to "this class is not
`d_reg`-invariant under the seven tested families, cause identified and
off-target" rather than "hands the campaign a target."

---

```yaml
red_team_report:
  id: RT-20260811-001
  task_id: TASK-20260811-d9d01e
  claim_under_review: >-
    EXP-ICINV-e0cd8f v1, RUN-ICINV-e0cd8f-m3class: verdict CLASS-VARYING on
    the elimination-polynomial factorisation-partition family (66 curves
    (1,1,1) / 72 curves (1,2) on the class; control set additionally shows
    49/138 (3,)), reported as surviving gauge, second-backend and
    monomial-order controls, and (per specification.yaml success_criterion
    and DEC-20260810-a4bec4) as licensing min_{E'~E} C(E') as a campaign
    target and promoting EXP-JINV-bd141d / EXP-VOLC-9f5571.
  objections:
    - >-
      The elimination polynomial computed by eliminate(x1,x2) on
      <S3, dS3/dx1, dS3/dx2, dS3/dx3> is, by an exact symbolic Groebner-basis
      identity over Q(a,b) reproduced independently in this review, equal to
      x^3 + a*x3 + b -- the curve's own Weierstrass cubic. Its
      F_p-factorisation type is therefore, by identity and not inference,
      the classical rational-2-torsion structure of E(F_p), a quantity with
      no established connection to Semaev-variety geometry or Groebner
      solving cost.
    - >-
      The class-vs-control 2-way-vs-3-way split difference is fully
      explained by elementary group theory: the class's fixed even trace
      t=30 forces #E(F_p) even on every member (Cauchy's theorem then rules
      out zero 2-torsion, i.e. rules out partition (3,) identically), while
      the control spans 92 traces roughly half of which give odd #E. Nothing
      isogeny-class-specific is needed for this half of the finding.
    - >-
      This exact quantity, under the name two_torsion_x_count / r, is
      already committed in harness/exp_icinv.py, was already computed on
      this exact class in BATCH-cb71b5 with the identical 72/66 split, was
      already found there not to explain the campaign's relation-yield
      signal, and is the explicit subject of ledger/hypotheses/H-ICINV-6c7920.yaml,
      which treats it as a sampling-bias nuisance covariate, not a discovery.
      Reporting this run's finding as a novel curve-dependent signal
      overclaims relative to the campaign's own committed record.
    - >-
      The execution_report.md and verdict.json artifacts do not themselves
      overstate the result -- both explicitly decline to interpret it. The
      risk is upstream, in specification.yaml's success_criterion and
      MATCHED-ORDER-DESIGN.md's T3 rule, which pre-commit to treating ANY
      surviving cross-family variation as licensing a campaign target
      without a mechanism argument distinguishing attack-cost-relevant
      families from classical off-target ones.
    - >-
      Six of seven primary families are simultaneously constant on the
      138-curve class AND on a 92-trace, 138-curve control drawn from
      unrelated classes -- a pattern the contract's own F2 clause treats as
      informative when it is the WHOLE verdict, but which was not surfaced
      as a caution here because the seventh family varied and routed the
      verdict to CLASS-VARYING instead.
  required_controls:
    - >-
      Independent reproduction (Validator/Coordinator, ~5 minutes, no new
      backend needed) of the symbolic identity I_3 intersect F_p[x3] =
      <x^3+ax+b> before any evidence record characterises
      elimination_factor_partition as novel Semaev-geometry signal.
    - >-
      An explicit, cited mechanism argument connecting rational-2-torsion
      structure to Groebner-solving degree/regularity of the
      summation-polynomial elimination system, f_V-free or f_V-bearing --
      absent from every document reviewed -- before EXP-JINV-bd141d or
      EXP-VOLC-9f5571 is described as promoted by this result.
    - >-
      A null-object control not yet run: the same seven families computed on
      a size-matched set of GENERIC (non-elliptic-curve) trivariate
      polynomials of S_3's bidegree/shape, to test whether the six
      currently-"constant" families are forced by shape alone rather than by
      curve structure.
    - >-
      Re-audit of the six constant families against the same
      classical-quantity-in-disguise question applied here to the seventh.
  counterexample_or_mutation: >-
    Ran, not merely proposed: (a) symbolic Groebner elimination over Q(a,b)
    reproduces x^3+ax+b exactly as the pure-x3 ideal generator; (b) brute-
    force root-count of x^3+ax+b mod 4001 against the run's own
    elimination_factor_partition matches on all 138 class and all 138
    control curves (0 mismatches); (c) (#E(F_p) odd) vs (partition == (3,))
    matches on all 138 control curves (0 mismatches), using the run's own
    class-census.json data and the unedited harness.isogeny_class module.
    These three exact matches jointly falsify the reading of this family as
    a novel isogeny-class-geometry signal distinct from the already-known,
    already-shelved 2-torsion covariate.
  baseline_comparison: >-
    Not separately engaged: claim_tier is toy and sota_delta is 0 by
    contract design (no attack, no exponent, no speedup claimed by this
    pure-measurement contract). dominated_by (parallel Pollard rho at
    0.886*sqrt(N), CM-automorphism-discounted variant) is correctly declared
    in DEC-20260810-a4bec4 and not disputed here; it is not read past,
    because no attack-cost claim is made for this run to be dominated on.
  heuristic_challenges: []
  cost_model_challenges:
    - >-
      The run spent ~855 wall-seconds / ~0.24 CPU-hours across a
      Betti-table/minimal-free-resolution/two-backend pipeline (Singular +
      Macaulay2, 276 curves plus 66-curve cross-check plus alt-order
      recheck) to recover, for its one varying family, information
      obtainable from data already present in this run's own
      class-census.json via a five-line root-count in milliseconds. This is
      not a claim-tier issue (toy/0 stands) but a design-efficiency finding
      relevant to how future contracts in this campaign should separate
      classical/elementary families from families that genuinely require
      the heavy machinery.
  reduction_and_scope_challenges:
    - >-
      The implicit reduction "family X varies across the class" ->
      "min_{E'~E} C(E') is a licensed campaign target" (specification.yaml
      success_criterion; MATCHED-ORDER-DESIGN.md T3) is not validly
      instantiated for this specific family without an argument connecting
      2-torsion structure to the Groebner/elimination cost functional the
      campaign's C(E') is meant to track. No such argument appears in
      specification.yaml, DEC-20260810-a4bec4, MATCHED-ORDER-DESIGN.md, or
      DECOMPOSITION.md. The nearest analogous discussion in this campaign
      (H-ICINV-6c7920, citing KN-TECH-030) treats the same quantity as
      attack-irrelevant/nuisance in every context it currently appears.
  proof_architecture_challenges: []
  narrowest_supported_statement: >-
    EXP-ICINV-e0cd8f v1 correctly and reproducibly establishes that
    elimination_factor_partition is not constant across the 138-curve class
    at p=4001, t=30, surviving gauge, second-backend, and alternate-order
    checks. It does not establish, and no record in this campaign currently
    establishes, that this variation bears on Semaev-variety geometry,
    degree of regularity, or attack cost C(E'): the varying quantity is, by
    exact symbolic identity, the curve's classical rational-2-torsion
    factorisation type, already computed on this exact class in a prior
    batch, already found uncorrelated with the campaign's relation-yield
    metric there, and already treated elsewhere in this campaign
    (H-ICINV-6c7920) as a sampling-bias nuisance covariate rather than a
    discovery. toy claim tier, sota_delta 0, and the contract's own
    f_V-removal non-transferability caveat continue to bind unchanged.
  next_concrete_action: >-
    Before any Coordinator evidence record cites this run as grounds for
    min_{E'~E} C(E') or as promoting EXP-JINV-bd141d / EXP-VOLC-9f5571: have
    the Validator or Coordinator independently reproduce the symbolic
    identity I_3 intersect F_p[x3] = <x^3+ax+b> (section 1/5 of this
    report), then either supply and check a mechanism argument connecting
    2-torsion structure to Groebner/elimination solving cost, or re-scope
    the verdict's stated consequence from "hands the campaign a target" to
    "this class is not d_reg-invariant under the seven tested families,
    with the sole varying family's cause identified and off-target."
  artifact_paths:
    - experiments/EXP-ICINV-e0cd8f/specification.yaml
    - ledger/decisions/DEC-20260810-a4bec4.yaml
    - coordination/goals/GOAL-ENDO-001/batches/BATCH-d7e255/execution/EXP-ICINV-e0cd8f/execution_report.md
    - harness/exp_icinv_e0cd8f.py
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/verdict.json
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/per-curve-invariants.json
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/control-set-invariants.json
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/class-census.json
    - harness/exp_icinv.py
    - ledger/hypotheses/H-ICINV-6c7920.yaml
    - knowledge/techniques/KN-TECH-030.md
    - knowledge/findings/KN-FIND-b7e091.md
    - coordination/goals/GOAL-ENDO-001/batches/BATCH-cb71b5/reviews/red-team/red_team_notes.md
    - analysis/endomorphism-isogeny-decomposition/MATCHED-ORDER-DESIGN.md
    - analysis/endomorphism-isogeny-decomposition/DECOMPOSITION.md
```
