# RT-BATCH-001 — Red Team review of GOAL-SSIQ-001 BATCH-001

**Task:** TASK-20260805-fb72f1 · **Goal:** GOAL-SSIQ-001 · **Batch:** BATCH-001
**Role:** red-team · **Compute performed:** none (`runs_authorized: 0`; reading and
one adapter `resolve` invocation only).

**Artifacts attacked (both Coordinator-committed, verified reachable and clean at review time):**

| package | snapshot commit | files |
|---|---|---|
| `tasks/TASK-20260805-85af9d/` | `50596409` | `exponent_budget.md`, `target_conditions.md`, `lever_additions.md`, `line_locators.yaml`, `task_report.yaml` |
| `tasks/TASK-20260805-87e568/` | `7ec7f730` | `L1_ceiling_audit.md`, `L4_baseline_acquisition.md`, `source_access_log.yaml`, `task_report.yaml` |

`git status --porcelain` was empty and both commits are reachable from `HEAD`; no
working-tree-only artifact was reviewed as durable evidence.

**Division of labour respected.** Arithmetic re-derivation of D1 and receipt/hash
checking belong to the Validator (`TASK-20260805-89a2e7`) and are not duplicated
here. This review attacks **interpretation, shape, quantifier structure, scope, and
the Coordinator-authored frame** (goal record `exponent_budget`, `levers`,
`completion_criteria`, and `RQ-SSIQ-9702af`), all of which the task card places in
scope. Where I derive arithmetic, it is a Red Team counterexample/mutation under
`agents/red-team.md` §4-5 and is labelled `derivation`, checkable, not machine-checked.

---

## 0. Inference and independence cap — stated before any finding

```yaml
inference:
  requested_policy: review-adversarial
  policy_binding_per_adapter: "anthropic:claude-opus-5 (effort=xhigh)"
  policy_binding_command: "python3 -m orchestration.adapter resolve --role red-team --independent-session"
  resolved_model_id: claude-opus-5
  resolved_model_provenance: >-
    Self-reported by the running Claude Code subagent session. NOT probe-verified:
    `orchestration.adapter doctor --probe` was not run.
  model_verified: false
  fallback_used: true
  fallback_reason: >-
    Subagent frontmatter under this Claude Code binding cannot express a policy
    (CLAUDE.md, "Model policy note"); this session runs `model: inherit`, so the
    policy alias did not select the model — the session did. The resolved model
    HAPPENS to coincide with the adapter's binding for review-adversarial
    (claude-opus-5), but the reasoning-effort component of that binding (xhigh)
    is neither settable nor verifiable from inside a subagent, so the policy is
    recorded as satisfied-by-coincidence, not as resolved. That is a fallback and
    is recorded as one rather than presented as a clean resolution.
  degraded_allowed: false
  degraded_requirements: ["reasoning_effort=xhigh not assertable or verifiable under this runtime"]
  independent_session: true
  independence_kind: session
```

**The cap, stated plainly.** Independence between the two producer sessions, the
Validator, and this Red Team is **SESSION independence, not MODEL independence**.
Every reader of this batch — producers and reviewers alike — is the same model.
A shared blind spot (a misremembered standard bound, a shared misreading of an
optimal-embedding count) survives every review this campaign can perform. This is
the same cap that held `EV-SSI-005` at `preliminary`, it is disclosed at
`BATCH-001-OPENING.md` §5 and `goal.yaml` `runtime_note`, and it is the single
largest limit on this report's own force. **My concurrence on D1 would not be
independent corroboration of D1, and I do not offer it as such** — which is one
reason my primary recommendation (§7) is an *empirical* check that fails
differently from any amount of re-reading.

---

## 1. FRONT 1 — Is the lever enumeration missing a route?

**Answer: yes, one — plus one structural defect in how the enumeration is
organised, and one defect in the forward guidance that hides a second route class.
I also record four lines I searched along and found nothing.**

### 1.1 The missing route: cross-attempt amortisation of the searched family (call it **A7**)

Neither `L1–L5` nor `A1–A6` covers it. `A5` is the nearest neighbour and is a
*different* object: `A5` is precomputation **across instances** over the same `p`
("a precomputation depending on `p` alone … after which each subsequent OneEnd
instance costs…"). **A7 is sharing work across the re-randomisation attempts
inside one instance.**

**Why it is not covered.** Both packages compose costs multiplicatively:
`target_conditions.md` §1 fixes `TOTAL = per-attempt cost × P0^{-1}`, and
`L1_ceiling_audit.md` §6.4 fixes `total ≈ p^θ · fraction(p^θ)^{-1}`. Every symbol
in `T = c·q·d/k + r` lives *inside one attempt*. The composition law itself — the
`×` — is an unexamined modelling assumption, and no lever acts on it.

**Why the assumption is not free.** Algorithm 3 re-randomises `E → E′` by a
non-backtracking walk `ω` of known length `O(log p)` and known small degree, then
builds `L(E′, X, B)` from scratch. But the attempts are **not independent
instances**: `E′` and `E″` from two attempts are connected by a *known* isogeny of
*known small degree*, and an entry `ψ′ : E′ → F` of one table composes with that
known isogeny to give an isogeny out of `E″` of degree `deg(ω) · deg(ψ′)`. Whether
the union of `A` tables costs `A ×` one table, or materially less, is an open
counting question that nobody in this batch asked.

**Why it matters here, and only here.** At the source's parameters it does not
matter: `P0^{-1} = p^{o(1)}`, so amortising over `p^{o(1)}` attempts saves at most
`p^{o(1)}`. **It matters exactly in the regime `L1_ceiling_audit.md` §6.4 invents
to derive its method ceiling.** There, at degree threshold `p^θ` with `θ < 1/3`,
the attempt count is `fraction^{-1} = p^{1/2−3θ/2}`, i.e. `p^{Θ(1)}` attempts.
`§6.4` multiplies. If attempts share work, the composition is not a product, and
`total ≫ p^{1/2−θ/2}` does not follow. At `θ = 1/4` the difference is `p^{3/8}`
(product) versus, at the ideal limit, `p^{1/4}` (perfect sharing).

**What this does and does not damage.** It does **not** damage the L1 closure: D1
is a statement about the *density of a stratum*, and its refutation of both L1
disjuncts stands whatever the composition law is. It **does** damage the *method
ceiling* of §6.4, which is presented as "the strongest result the proposed measure
could certify even under ideal tuning". Under ideal tuning of a law the audit did
not vary, it certifies less than claimed. See objection **O6**.

**First audit for A7, cheap and zero-compute.** Count `|⋃_a L(E_a, X, B)|` against
`Σ_a |L(E_a, X, B)|` for `A` attempts, where the `E_a` are connected by known
walks. The union is contained in the set of isogenies out of `E` of degree
`≤ deg(ω)·X` with `deg(ω)^{-1}`-constrained prefix, whose cardinality is bounded by
Lemma 3.2 at the enlarged threshold. If the union is `Θ(A)` times one table, A7 is
dead on the same page it is proposed, and §6.4's product law is vindicated with an
argument instead of an assumption. **Charge the build cost of any shared structure
into the total** (`KN-LIT-7593`: an eliminated dimension is not a speedup until the
invariant's own cost is in the total).

### 1.2 Structural defect: the coverage table is a coordinate list of one identity

`lever_additions.md`'s "Coverage check" is a table over the symbols `d, k, q, c, r`
of `T = c·q·d/k + r`. That identity is a model of **one algorithm family**:
degree bound → balanced split → enumerate a list → claw-find. `L1_ceiling_audit.md`
§10.3 states this correctly for D1 ("a ceiling on a *method* … A mechanism that does
not route through a bound on `δ_E` is entirely outside its reach"), but the
coverage table carries no such caveat and is the artifact a later batch will
quote. **"Not a symbol in `T`" is not "not a route", exactly as
`lever_completeness_disclaimer` says "not in L1–L5" is not "not a route."** The
disclaimer must be inherited by the coverage table or the table becomes the
exhaustiveness proof the disclaimer denies. See **O19**.

### 1.3 Forward-guidance defect that hides a route class: the rank axis

`L1_ceiling_audit.md` R3 states the audit criterion for N5 as: *"does the substitute
target have a rank-3 governing lattice of discriminant `≪ p^{3/4}`, or a governing
lattice of rank `< 3`? **Those are the only two ways** to reach exponent `1/4` from
a lattice-minimum bound"*.

That is false as stated. For a positive-definite **quadratic** form the Hermite
exponent is `log_p(det)/rank`; reaching `1/4` needs `log_p(det)/rank ≤ 1/4`, which
admits **rank 4 with `det ≲ p`**, rank 6 with `det ≲ p^{3/2}`, and so on. The
criterion excludes `rank > 3` by fiat, and `rank > 3` is precisely where N5's own
third case — *higher-dimensional objects (superspecial abelian surfaces)* — lives.
The audit's own generalisation R4 ("exponent = (1/rank) × (log_p discriminant)")
contradicts R3's enumeration.

I do **not** claim the rank axis works. Raising the ambient dimension changes the
homogeneity degree of the degree form (it is quadratic on `Hom` of elliptic curves;
it is not quadratic on `Hom` of higher-dimensional abelian varieties), so
"Hermite exponent = `log_p det / rank`" does not transfer unexamined — and that is
the point: R3's criterion would return "not rank 3, not rank < 3, therefore no" on
an object where the criterion does not even apply. **The correct N5 audit question
is: rank, homogeneity degree of the degree form, and determinant, then the
Minkowski exponent computed from all three.** That is still a zero-compute lookup.
See **O5**.

Note also that `exponent_budget.md` §6.6 dismissed Kani-style higher-dimensional
machinery for a *different* reason ("a change of representation alone does not
change the *count* of objects to be searched") — an argument about `q`, not about
`d`. **The two packages dismissed the same object on two different grounds, neither
of which addresses the axis on which it would act.**

### 1.4 Lines I searched along and found nothing — recorded as such

Per the task's explicit permission that "I looked here and found nothing" is a
legitimate answer, and to keep this report from manufacturing levers:

1. **Special-form primes.** `lever_additions.md` "not found #2" argues only that the
   *frozen text* is uniform in `p`. That is the weak form. The strong form is now
   available and is *stronger against the lever*: D1 is `∀p`, so no special prime
   family can have a `p^{-o(1)}` fraction of curves below exponent `1/3`. This
   route is closed harder than the producer closed it, and by their own derivation.
   **No lever.**
2. **Unbalanced splits and per-side smoothness bounds.** Line 181's balance chain
   makes `X = (B·D)^{1/2}` the minimum admissible per-side bound; any imbalance
   raises the larger side and therefore `T`. Distinct `B` per side moves only inside
   `p^{o(1)}` (see O13). **No lever; folded into A1.**
3. **The correctness argument (non-scalarity via inseparable degree `p`).** Confirmed
   exponent-free; it is a *constraint* on A2's requirement (iii), not a saving.
   **No lever.**
4. **Quantum.** Out of the goal's classical `F_{p^2}` framing, and line 41 relays the
   opposite suggestion. **No lever.**

---

## 2. FRONT 2 — Does the L1 CLOSED verdict establish what it claims, in the direction claimed?

**Answer: the mathematical content survives, but three things about its shape are
misstated, and the verdict token is wrong for the ledger it feeds.** Specifically:
the closure is **single-pillar and derivation-tier**, its claimed independent
corroboration is not independent, its headline consistency signal was forced, and
N5 makes the honest token `CLOSED-IN-SCOPE`, not `CLOSED`.

### 2.1 Does refuting a UNIVERSAL bound close the lever? No — and P1 is redundant anyway.

The task asks the right question. The algorithm does not need a universal bound;
Algorithm 3 re-randomises, so it needs the bound on a `p^{-o(1)}` fraction of the
curves it lands on. P1 (AOV Remark 4.3) closes **disjunct 1**, which the algorithm
never needed. The producer says this ("the second … is the one the algorithm
actually needs … **load-bearing**") — full credit — and then, in the VERDICT block,
leads the one-sentence reason with P1 and puts P1 first in the pillar table under
`basis: cited primary text, unconditional`. A reader who reads the verdict block and
stops — which is what a checkpoint writer does — takes away "closed by cited
unconditional primary text".

Worse for the two-pillar presentation: **D1 subsumes P1.** D1 is `∀p ∀T ≤ (p/2)^{1/3}`:
`#{E : δ_E ≤ T}/(p/12) ≪ T^{3/2}p^{-1/2+o(1)}`. A universal bound `δ_E ≤ Cp^{1/4}` for
all `E` would force that fraction to be `1` at `T = Cp^{1/4}`, contradicting
`p^{-1/8+o(1)}`. So D1 refutes disjunct 1 as well, for **every** `p` — a strictly
stronger statement than Remark 4.3's infinitely-often, extremal-curve form.

**Consequence.** The closure has **one** load-bearing pillar, D1, and D1 is
`proof_status: derivation` with three ingredients not fetched. P1's residual value
is real but narrow: it is the only part that survives if D1 falls, and it survives
covering the disjunct nobody needs. The correct headline is therefore:

> **L1 is closed by a single derivation-tier argument (D1). The unconditional,
> primary-text pillar closes a strictly weaker statement that D1 already implies,
> and covers nothing the algorithm requires.**

This is **O1**, severity HIGH — not because anything asserted is false, but because
the evidential status of the batch's only closure is presented one tier stronger
than it is, and the task card explicitly forbids flattening the two pillars.

### 2.2 Does D1's quantifier order match what L1 requires? Yes.

I checked this directly and it survives.

- L1 disjunct 2 requires a bound holding on a `p^{-o(1)}` fraction. D1 quantifies over
  the **population** at each `p`, uniformly. Match.
- Algorithm 3's re-randomised `E′` is claimed indistinguishable from uniform on
  supersingular `j`-invariants (walk + mixing, F6). D1's fraction is over the same
  population. Match, up to the `p^{o(1)}` slack the walk already carries.
- D1 counts `{E : δ_E ≤ T}`, which is a **superset** of `{E : the minimal B-smooth
  isogeny E → E^{(p)} has degree ≤ T}`. An upper bound on the superset is the safe
  direction for the refutation. Correct.
- `L1_ceiling_audit.md` §8's quantifier table is accurate, and its stated trap —
  that `(iii-a)` and `(iii-b)` are both "lower-bound shaped" and point in opposite
  directions, and that neither alone closes L1 — is exactly right and is the best
  paragraph in either package.

**One quantifier gap that the two-pillar presentation would have left open, and D1
closes:** P1's witness prime `p` may depend on `η` and `C'`, so P1 alone does not
refute "for all `E`, for all `p` **in a special family**". D1 does. This is the
formal version of §1.4 item 1.

### 2.3 D1 saturating at 1/3: consistency check or circularity? **Neither — it is forced.**

`task_report.yaml` calls it *"the strongest internal consistency signal the audit
produced"* and `L1_ceiling_audit.md` §6.3 says a bound that goes vacuous exactly
where the truth is 1 *"is consistent and cannot be improved at that exponent"*.

Apply `docs/inventor-protocol.md` §3: **ask what the quantity should have done.**
Any *correct* upper bound on a fraction must be `≥` the true fraction. The true
fraction at `T = (p/2)^{1/3}` is exactly `1` by AOV Theorem 4.2. Therefore **every
correct upper bound is vacuous at `1/3`**; a bound that were *not* vacuous there
would be wrong. Saturation at `1/3` is a **necessary condition, not a signal**. It
is a check that would have caught an error — worth recording — but it discriminates
nothing, and calling it the strongest signal is exactly the artifact tell §3 warns
about: a reported quantity that could not have come out any other way.

It is not circular, because D1's derivation (class numbers) never uses AOV
Theorem 4.2. But it is not corroboration either.

**The informative endpoint was not reported.** At `T = O(1)`, D1 gives
`fraction ≪ p^{-1/2+o(1)}`. The frozen text states, at **line 53**, that generating
random `E′` until `E′` is *"adjacent"* to its conjugate succeeds with probability
`O(p^{-1/2})` — the [24, 26] mechanism. And `{δ_E = 1}` is exactly the `F_p` locus, of
size `≍ p^{1/2}` in `≍ p/12` curves. **D1 is tight at the small-`T` endpoint too**,
and that endpoint is checkable against text already in this repository. That is the
check worth reporting; the audit reported the one that was forced and missed the one
that could have failed. **O3**, severity MEDIUM.

(Being fair to the producer: because D1 is pinned at both `log_p T = 0` and
`log_p T = 1/3`, the exponent `3/2` is the unique log-linear interpolant between two
independently known anchors. That is genuinely reassuring — and it is a much better
argument for D1 than the one the audit made.)

### 2.4 The "independent reproduction" of `p^{1/3}` is not independent

`§6.4` and `task_report.unexpected_observations_preserved` present D1's return of
`p^{1/3}` at `θ = 1/3` as *"reproduced from a completely independent direction (a
class-number count, versus the source's Hermite/Cassels bound plus smoothness
heuristic)"*.

Both routes are driven by **one** input: the governing rank-3 lattice has
discriminant `≍ p`. Cassels/Hermite turns that into `min ≪ (p/4)^{1/3}`; the
class-number count turns the same fact into a short-vector count. The audit's own
R4 names the shared engine: *"exponent = (1/rank) × (log_p discriminant)"*. Two
computations sharing their single load-bearing input are two views, not two
witnesses. Note further that D1's shape `T^{3/2}p^{-1/2}` is exactly the Gaussian
heuristic for short vectors in a **random** rank-3 lattice of determinant `≍ p`
(`≈ T^{3/2}/√det`). **D1's content is therefore precisely: Gross lattices are not
anomalously short-vector-rich compared with random ternary lattices of the same
discriminant** — proved as an upper bound, which is the right direction, but it is a
null-model count and should be labelled as one. **O2**, severity MEDIUM. The
labelling is not cosmetic: it tells the next session exactly where D1 could fail
(an arithmetic conspiracy making Gross lattices anomalous) and confirms that no such
conspiracy is available uniformly in `p`, since ingredient (d) is uniform.

### 2.5 N5 and the verdict token: should it read REDIRECTED?

My answer: **not REDIRECTED, but not the bare token `CLOSED` either.**

- REDIRECTED would misdescribe N1–N4, which the control genuinely covers: N1 is
  degenerate, N2 is isometric bookkeeping, N3 transfers with the invariant `mT`, and
  N4 — the null object, a generic supersingular target — returns exponent `1/2`, not
  `1/3`. **N4 is a real null-object control and it passes**: the method distinguishes
  the structured object from the structure-free surrogate, which is exactly what
  `docs/inventor-protocol.md` §3 demands before belief. Credit where due; this is the
  strongest methodological element in the batch.
- But L1's own `claim_that_would_have_to_be_true` says "*or to another
  cheaply-recognisable auxiliary target*", and N5 is a **member of the lever's own
  statement** that the argument does not reach. A verdict of `CLOSED` on a lever
  one of whose stated disjuncts is untouched is a scope overstatement in the token,
  even though the verdict *line* names its scope correctly.
- The concrete harm is mechanical, not rhetorical. `goal.yaml`
  `pause_conditions[1]` fires when "**every enumerated lever … is CLOSED** by a
  committed ceiling argument or executed falsification, and no successor route is
  identified". That condition consumes **bare tokens**. A checkpoint that records
  `L1: CLOSED` moves the campaign one lever closer to a pause that the evidence does
  not support.

**Required fix (O4, severity MEDIUM-HIGH).** The BATCH-001 checkpoint records
`L1: CLOSED-IN-SCOPE` with the scope string verbatim from the verdict line, plus a
**newly minted lever identifier for N5** so that the open component has its own row
and cannot be absorbed into a closed one. Minting an id is the Coordinator's act;
`python3 tools/allocate_id.py` is the mechanism. Without a row of its own, N5 is a
sentence inside a document titled with the word CLOSED.

### 2.6 The method ceiling is weaker than the lever closure — do not merge them

`§6.4` derives `total ≫ p^{1/2−θ/2}`, concludes `θ = 1/3` is the interior optimum,
and labels this "the method ceiling in the §8 sense". Two separate problems:

1. It multiplies per-attempt cost by inverse fraction, which assumes attempts share
   no work (§1.1, **O6**). A ceiling claimed "under ideal tuning" that fixes a
   composition law it never varied is not a ceiling.
2. It is explicitly conditional on the goal record's **self-declared-unverified**
   opening exponent reading — the producer flags this — and
   `TASK-20260805-85af9d` has since **corrected** parts of that reading (F2 and F3
   attributions, the line range). The substance of `F1 → total` survived
   (`exponent_budget.md` §3.3 master identity), so §6.4's arithmetic stands, but the
   recomputation the producer promised ("if F1↔total is corrected, §6.4 must be
   recomputed") is now **due** and has not been performed by anyone. Assign it.
   **O20**, severity LOW (I expect it to pass; it is an open loop, not an error).

D1 and the §6.3 verdict do not depend on either point. Keep them separate in every
downstream record.

---

## 3. FRONT 3 — Is the framing overclaiming, or setting up a premature closure?

**Answer: it is not overclaiming — the batch is unusually disciplined about
`0.25 is a target, not a claim`, and I found no scope inflation. The premature-closure
risk is real but is located in the Coordinator's frame, not in the producers' work:
four of five `named_obstruction_to_audit_first` fields are defective, and three of
them are defective in the direction that would retire a live lever.**

### 3.1 The Minkowski defect generalises — check of L2, L3, L4, L5

The task asks whether a Coordinator who got L1's obstruction wrong got the others
wrong. Verdict: **yes, in four of five cases, each differently.**

**L1 — WRONG, confirmed by the producer.** Two independent category errors:
Minkowski/Hermite/Cassels give *upper* bounds and cannot force a floor; and applied
to the rank-4 object they give exponent `1/2`, weaker than the known `1/3`. The
producer recorded rather than silently repaired it. Correct handling.

**L2 — UNSOURCED AND OPTIMISTIC IN DIRECTION (O8, MEDIUM).** The obstruction reads
"the exchange rate … *is usually 1:1 — every natural restriction tried so far
divides the list and the hit probability by the same factor*". **Tried by whom?**
No experiment ID, no citation, no knowledge entry, nothing in this repository. Under
`docs/inventor-protocol.md` §4 that is a **fatigue report about a search**, presented
as a statement about the problem, and its honest status is `unverified`. Worse, it
is optimistic: the producer's A4 shows the *generic* case is **worse than 1:1** —
independent membership gives `e = 2δ` and `T = (2+δ)/6 > 1/3` for every `δ > 0`,
because line 185 requires **both** `ψ` and the conjugated `χ` to be in the family.
Alignment (`e = δ`) is exact break-even at `T = 1/3` for every `δ`. The obstruction
should read: *the two natural nulls are `e = 2δ` (strictly worse than no restriction)
and `e = δ` (exact break-even); `1/4` requires `e = δ − 1/2`, i.e. positive
correlation of `F` with the sought `ψ` at strength `X^{1/2}`.* A4 supplies this and
it should replace the field.

**Direct answer to the task's named duty on L2's exchange rate:** the 1:1 rate is
**not forced by a theorem**, but it is forced by a *symmetry* that the source
exhibits and that any restriction must break: the table is queried at the Frobenius
conjugate of each codomain (line 171), so membership is a **two-event conjunction**
over an involution-paired set. A restriction defined by any property invariant under
that involution gives `e = δ` (break-even); a restriction not invariant under it
gives `e = 2δ` (worse). **To beat 1:1 the family must be invariant under the
conjugation involution AND positively correlated with the solution** — the second is
where the whole lever lives, and it is not a measurement of an exchange rate, it is a
measurement of a correlation. A4 says this; L2's field does not; and a toy
measurement of the raw rate returns the null in both natural cases and is therefore
uninformative as currently specified.

**L3 — FALSE AS A GENERALITY (O7, HIGH).** The obstruction asserts "*for UNSTRUCTURED
claw finding, k-way splits do not beat the two-list bound*". As a general claim about
`k`-list problems that is well known to be **false** — Wagner-style generalised-birthday
`k`-tree algorithms beat the two-list bound whenever the lists live in a group and
solutions are abundant. The claim is true in the setting that actually applies here
(a single expected solution, no group operation on `j`-invariants to which a tree
algorithm could apply), but that restriction is *the content* and it is missing. This
matters more than a pedantic point, for two reasons: (a) the field is one of the two
places the Coordinator tells producers what to audit first, and a false generality
there either invites rejection of the field or, worse, licenses a later record to
pre-close **A1** (the `k ≥ 3` lever) by citing a claim that does not say what it
appears to say; (b) L3's obstruction is about `k`, while L3's lever is about `c` — the
field is attached to the wrong symbol. Replace with: *the unique-solution claw bound
applies; `k`-tree/generalised-birthday accelerations do not, because there is no group
operation on the match space and a single solution is expected; a `k`-way proposal
must exhibit an anchor (see §3.4) or it collapses to an unbalanced 2-way split.*

**L4 — POINTED AT THE WRONG QUESTION (O9, MEDIUM).** The obstruction directs the
auditor at the *sourcing* of the `Õ(p^{1/4})` figure. The decision-relevant structural
fact — that Delfs–Galbraith's **general** cost is `Õ(p^{1/2})`, that the descent is the
bottleneck, and that the `p^{1/4}` phase is asymptotically free — was already derivable
from the frozen text in this repository (line 51: "*A memory-free algorithm with the
same complexity was proposed in [21]*"). The acquisition task was still worth running
(RC4 is now resolved with a mechanism, and the absence of a memory profile is now
established rather than merely unobtained), but the field sent the cheapest work in
the batch at a bibliographic question while the structural question sat one line away
in a file already frozen here.

**L5 — NO OBSTRUCTION FIELD AT ALL (O10, MEDIUM).** L5 carries `status_note`, not
`named_obstruction_to_audit_first`. Its note ("does not move the time exponent and so
does not serve this goal's target") is a legitimate **scope** statement and is *not* a
closure — but it therefore leaves L5 neither OPEN nor CLOSED, with no revisit
condition and none of the AGENTS rule 9 parts (evidence, budget, test boundary,
remaining uncertainty, successor). If `pause_conditions[1]` is ever evaluated, L5's
status is undefined. Cheap fix: record L5 explicitly as `OUT-OF-TARGET (memory axis)`
with a revisit condition (a genuine sub-vOW point), so it is never counted as closed
and never blocks a pause it should not block.

**The meta-finding.** `named_obstruction_to_audit_first` is written **before** anything
is checked and **determines which cheap work happens first**. In this batch it was
wrong in L1, unsourced-and-optimistic in L2, falsely general in L3, and misdirected in
L4. It should be treated as *a hypothesis about the obstruction, carrying its own
source requirement*, not as a given the auditor must first disprove. **O11**: the same
Minkowski category error is also replicated in `RQ-SSIQ-9702af`
`scope.methods` ("*lattice / quaternion-order arguments bounding the minimal degree of
E -> E^{(p)} **from below** (Minkowski-type obstructions)*"). Any correction must reach
both records, or the RQ will re-seed the error into the next batch.

### 3.2 The F4 refutation: I tried to break it. It holds for the exponent — with one added case and one narrowing.

The claim under attack (`BATCH-001-OPENING.md` §2): any proposal saving via success
probability is "refuted at the whiteboard, for free". The producers' argument is
`r ≥ 0` because `P0 ≤ 1`, so `T = 1/4` needs `P0 = p^{1/12} > 1`. That is airtight
**given the identity**.

**Break attempt 1 — move `B` and trade F3 against F4 jointly** (the task's named
duty). The producers assert F5 is exponent-free but only check it *at* the source's
`B = e^{(1/3)√log(p/2)}`. I checked both directions out of that regime:

- `B = p^β` with `β > 0` fixed: `X = (B·D)^{1/2} = p^{(β+1/3)/2}`, list `= p^{β+1/3}`,
  so per-attempt cost exponent `= β + 1/3`; meanwhile `u = log(p/2)/(3 log B) = 1/(3β)`
  is a **constant**, so `u^{u}` is a constant and `r = 0` still. Net
  `T = 1/3 + β > 1/3`. **Strictly worse.**
- `B` polylogarithmic (below Heuristic 1's uniformity range): `u ≈ log p / (3 log log p)`,
  so `u^{u} = p^{1/3−o(1)}` and `r → 1/3`, while the list only falls to `p^{1/3}`.
  `T → 2/3`. **Much worse.**

So the joint move is doubly one-sided and the refutation survives the strongest form
of the attack the task named. **Confirmed, with the missing case supplied.**

**Narrowing (O13, LOW-MEDIUM).** It follows that `r = 0` and "F5 is exponent-free" hold
**only inside Heuristic 1's stated uniformity range** `(log p)^ε < u < (log p)^{1−ε}`.
`exponent_budget.md` §2.2 and `lever_additions.md` A6 state F4/F5 exponent `0` flatly.
The anti-lever register must carry the range, or a later proposal that moves `B` out of
it will be waved away by a register entry that does not apply to it — and, in that
regime, `r > 0` and the register's own conclusion changes sign.

**Break attempt 2 — attack the composition law rather than `r`.** This is §1.1/A7 and it
**does** find a gap, but not in the F4 refutation: the refutation is about the *value*
of `r`, and A7 is about whether `TOTAL = per-attempt × P0^{-1}` is the right law. At the
source's parameters `P0^{-1} = p^{o(1)}` so the distinction is invisible; it becomes
visible only in §6.4's lowered-threshold regime. **The F4 refutation stands; the
`total = per-attempt × inverse-success-probability` bookkeeping it lives inside is the
thing that needed the audit and did not get one.**

**On the producer's narrowing.** `exponent_budget.md` §4.3 already narrows the opening's
phrasing using Remark 1 (line 191, *"While practically relevant, this phenomenon is
absorbed in the hidden term"*). That narrowing is correct and necessary and I endorse it
without reservation: **the claim holds for the EXPONENT and would be false if carried to
practical impact.** Given `GOAL-P13-001`'s measured per-entry overhead findings
(`EV-PEC-2e67ff`, `EV-PEC-857664`, cited here as inputs and not re-derived), a
success-probability improvement is one of the few things that could matter concretely,
and no record under this goal may cite "F4 is exponent-free" as a reason not to look.

### 3.3 Inherited scope and the unverified cascade

**Scope: no widening found.** I grepped the goal record, the RQ record, the batch
opening, and both producer packages for every scheme name in the source's two lists.
The affected set (CGL, SQIsign family, GPS, PRISM, ⊗-MIKE) and the out-of-range set
(CSIDH/(qt-)Pegasis, M(D)-SIDH, FESTA, POKE) appear **exactly once**, in
`goal.yaml` `affected_scope_if_a_result_were_obtained`, correctly attributed to the
source, with an explicit non-widening clause. No producer artifact names a scheme at
all except in a bibliography line. **This is clean and I record it as clean.** The one
residual note: the source's "safe" list is safe because *other cryptanalysis dominates
those parameter choices* — that is a claim about **today's** parameter choices, and if
this campaign's target were ever reached the "safe" classification would need
re-derivation, not inheritance. No record has made that error; the checkpoint should
say so explicitly so that no later record makes it.

**Cascade: the producer packages are clean; the GOAL RECORD is where it is treated as
verified (O12, MEDIUM).**

- `exponent_budget.md` §5 marks `[35, Theorem 1]` and `[35, Proposition 8.5]` as
  CITED-NOT-VERIFIED, states that no exponent is assigned to them anywhere, and
  §7/`target_conditions.md` §7 restrict **every** derived condition to *OneEnd over
  `F_{p^2}`* (Problem 2.2, line 119). `lever_additions.md` "not found #1" records that
  no lever was found there and none was invented. This is exemplary and I have no
  objection to it.
- But `goal.yaml`'s **title** ("*supersingular isogeny algorithm*"), **objective**
  ("*Attack the exponent of the supersingular isogeny problem over F_{p^2}*"), and
  **completion criterion 4** ("*a mechanism whose charged time exponent over F_{p^2} is
  strictly below 1/3*") all state the target on the problem reachable **only through
  the uninspected cascade**, while every quantity the campaign can actually derive is
  a OneEnd quantity. `RQ-SSIQ-9702af` handles this better (it says "via the reductions
  it cites, never checked by this program"). The goal record should match.

**Does the missing exponent on those reductions matter for the 1/4 target?** Yes, in one
specific and checkable way. A reduction that is polynomial in `log p` contributes
`p^{o(1)}` and is harmless at any target exponent. A reduction whose cost is polynomial
in something else — or that is itself heuristic, or GRH-conditional, or that consumes a
smoothness assumption — is not harmless, and **nobody in this program has read either
statement.** At the `1/3` level the risk is *inherited* from the source and is not this
campaign's to carry; the moment criterion 4 is claimed at `1/4` for "the supersingular
isogeny problem", the risk becomes this campaign's own. The fix is cheap and is
recommendation **REC-2** in §7: `[35]` is Page–Wesolowski, EUROCRYPT 2024, publicly
available as IACR ePrint 2023/1399, and the environment demonstrably reaches
`eprint.iacr.org` (retrieval `sccs_abs` succeeded). One fetch records the cost
statements and the hypotheses of Theorem 1 and Proposition 8.5, and closes a standing
`KN-TECH-058` gap at the same time.

### 3.4 L4: is it a lever at all? **Yes — and the producer's correct finding does not kill it. Do not let a record read it as killed.**

The task asks whether L4 is "already dead on the source's own accounting". I disagree
with that reading, and this is my most consequential disagreement with the batch's
likely take-away.

What the producer established is correct and well sourced: the `Õ(p^{1/4})` figure is
**heuristic** (birthday), for the **`F_p`-restricted** problem, on a **high-storage**
search, with **memory unstated**; the general Delfs–Galbraith cost is `Õ(p^{1/2})`; the
descent is the bottleneck; the `p^{1/4}` phase is asymptotically free. All of that kills
**the use of the `p^{1/4}` figure as evidence**, which is exactly what the batch asked
for and what `BATCH-001-OPENING.md` §4 forbids.

But apply it to the lever, whose statement is "*a descent to the `F_p`-rational subgraph
cheaper than `p^{1/2}`*". Delfs–Galbraith's total is `max(descent, F_p-phase)`. The
`F_p` phase is `Õ(p^{1/4})`. Therefore:

> **The Delfs–Galbraith architecture's method ceiling under ideal tuning of the descent
> is exactly `Õ(p^{1/4})` — the goal's target exponent — and L4 is the only enumerated
> lever whose ideal ceiling equals the target exactly.**

"The `p^{1/4}` phase is asymptotically free" and "L4 is dead" are opposite conclusions
from the same sentence. The phase being free is what makes the descent the *whole*
cost, which is precisely what makes a cheaper descent worth the full remaining
distance. **O14, severity MEDIUM-HIGH**, aimed at the checkpoint rather than at the
producer, who explicitly returned `l4_verdict_returned: false` and said the observations
were "recorded for whoever runs it". That restraint was right; the risk is that a
checkpoint reads the L4 section's tone and retires the lever without ever running its
audit. Under AGENTS rule 9 and `docs/inventor-protocol.md`, retiring L4 on this evidence
would be premature closure.

**What would have to be true for L4 to live, stated so the audit is decidable.** The
descent's `p^{1/2}` is a **hitting-time** bound: the `F_p` locus has density `≍ p^{-1/2}`
in an expander, and an undirected walk pays `1/density`. Beating it requires a
**steering** ingredient: a cheaply computable signal on `j(E)` correlated with proximity
to the `F_p` locus — equivalently, correlated with `δ_E`. Note the deep connection the
batch nearly makes and does not: the `F_p` locus is exactly `{δ_E = 1}`, and **D1 gives
the density of every stratum `{δ_E ≤ T}`**. So descending to a stratum instead of to the
locus costs `p^{1/2}T^{-3/2}` undirected — which is §6.4's family again, with
Delfs–Galbraith at `θ = 0` and the archived algorithm at `θ = 1/3`. **The two
"different" levers are two points of one curve whose optimum D1 already locates at
`θ = 1/3`.** That is the honest reason L4 is unattractive *undirected*, and it is far
sharper than "the `p^{1/4}` phase is free". It also isolates the one thing that would
change the picture: **a computable gradient on `δ_E`.** Named obstruction: the graph is
Ramanujan and no such distinguisher is known; [15] (Corte-Real Santos–Costello–Shi,
CRYPTO 2022) improved subfield **detection cost**, explicitly not the step count, and
states the asymptotic is unchanged. That is a real closure-standard obstruction —
named, argued, with forward guidance — and it is what L4's field should have said.

**Whether such a gradient exists is empirically testable, cheaply, on data the producer
already located** (§7, REC-1b).

### 3.5 A1 (`k ≥ 3`) is the most attractive addition and it is refutable at zero cost without an anchor

`lever_additions.md` A1 is the highest-payoff addition in the batch (`k = 3` gives
`T = 2/9 < 1/4`), and the producer correctly identifies that its requirement (ii) —
`c = 1` at arity `k` — "is where the whole route lives". I ran the audit they deferred.
It is pen-and-paper and it is negative absent an anchor:

> Split `φ : E → E^{(p)}` as `φ = η_k ∘ ⋯ ∘ η_1` with each `deg η_i ≤ Y = (B·D)^{1/k}`.
> The endpoints `E` and `E^{(p)}` are known; the `k − 1` intermediate curves are not.
> Any algorithm must determine them. Meeting in the middle from both ends produces two
> lists of isogenies of degree `≤ Y`; joining them requires testing whether two candidate
> intermediates are within degree `Y` of each other. **That test is the isogeny problem
> at scale `Y`; there is no `p^{o(1)}` oracle for it.** The only way to discharge it
> without such an oracle is to *extend* one side — i.e. to regroup the `k` pieces into
> two blocks — at which point the algorithm **is** a two-way split, and line 181's
> balance argument already proves the balanced two-way split optimal. Worked instance,
> the `(k−1, 1)` grouping: cost `Y^{2q}` against per-side cardinality `Y^{q}`, i.e.
> `c = k − 1`, giving `T = (2/3)·(k−1)/k` — `1/3` at `k = 2`, **`4/9` at `k = 3`,
> `1/2` at `k = 4`**, rising to the naive `2/3`.

`k = 2` is special for exactly one reason, which the producer identified: the Frobenius
involution makes the second endpoint a **computable function of the first** (line 171,
justified at line 183). That is the anchor, and no analogue for an interior vertex is
stated anywhere.

**Consequence (O15, MEDIUM-HIGH, constructive).** A1 must not enter BATCH-002 as an
open lever with the arithmetic table `k = 3 → 2/9`, `k = 4 → 1/6` presented as a payoff.
That table assumes `c = 1`, which is refuted by default. A1's correct statement is:
*exhibit an anchor for at least one interior vertex — a `p^{o(1)}`-computable relation
determining an intermediate curve from known data — or the arity lever is strictly
worse than the incumbent by the quantified amount above.* This also retro-justifies
L3's obstruction (which is right here, for reasons L3 does not give, and attached to the
wrong lever — see O7).

---

## 4. Numbered objections

Severity scale: HIGH = would mislead a downstream record about what is established;
MEDIUM = a real defect with a bounded, cheap fix; LOW = hygiene.

| # | objection | sev. | resolution route |
|---|---|---|---|
| **O1** | The L1 closure is presented as two-pillar with the unconditional pillar first; in fact **D1 subsumes P1** (a universal `p^{1/4}` bound forces fraction `= 1`, contradicting `p^{-1/8+o(1)}`, for **every** `p`). The closure is single-pillar and derivation-tier. §2.1 | HIGH | Rewrite the verdict headline to lead with D1 and state the tier. Keep P1 as the fallback that survives if D1 falls, noting it covers only the disjunct the algorithm does not need. |
| **O2** | The "completely independent direction" corroboration is not independent: Cassels/Hermite and the class-number count share their single load-bearing input (rank-3 lattice, disc `≍ p`), as the audit's own R4 pattern says. D1's shape is the Gaussian-heuristic short-vector count for a random ternary lattice of that discriminant. §2.4 | MEDIUM | Relabel as "second view of the same input", and state D1's content as the null-model statement it is: Gross lattices are not anomalously short-vector-rich. |
| **O3** | Saturation at `1/3` is reported as "the strongest internal consistency signal"; it is a **necessary property of any correct upper bound** and could not have come out otherwise (inventor-protocol §3 artifact tell). The informative endpoint (`T = O(1)`, where D1 must return `p^{-1/2}` and the frozen text line 53 independently states `O(p^{-1/2})`) was not reported. §2.3 | MEDIUM | Demote the `1/3` observation to a sanity check; add the `T = O(1)` endpoint check, which is a zero-cost lookup in a file already frozen here. |
| **O4** | Verdict token `CLOSED` on a lever one of whose stated disjuncts (N5) is untouched, feeding `goal.yaml` `pause_conditions[1]`, which consumes bare tokens. §2.5 | MED-HIGH | Checkpoint records `CLOSED-IN-SCOPE` with the verdict line's scope string verbatim, **and mints a new lever id for N5** via `tools/allocate_id.py` so the open component has its own row. |
| **O5** | R3's N5 criterion ("rank-3 with disc `≪ p^{3/4}`, or rank `< 3` — the only two ways") excludes `rank > 4` by fiat, and rank `> 3` is exactly where N5's own higher-dimensional case lives. It also assumes the degree form stays quadratic, which fails for higher-dimensional targets. §1.3 | MED-HIGH | Restate the criterion as: rank, **homogeneity degree of the degree form**, and determinant, then the Minkowski exponent from all three. Still zero-compute. |
| **O6** | `§6.4`'s method ceiling multiplies per-attempt cost by inverse fraction, assuming attempts share no work. That law is never varied, yet the ceiling is claimed "under ideal tuning". At lowered thresholds attempts are `p^{Θ(1)}`, so the assumption is load-bearing. §1.1 | HIGH | Either prove the union of per-attempt tables is `Θ(A)` times one table (bounded by Lemma 3.2 at the enlarged threshold — cheap), or restate §6.4 as conditional on independent attempts. **The L1 closure itself is unaffected.** |
| **O7** | L3's `named_obstruction_to_audit_first` ("`k`-way splits do not beat the two-list bound for unstructured claw finding") is false as a generality (generalised-birthday `k`-tree algorithms), true only for the unique-solution, no-group-operation setting that applies here — and is attached to the `c` lever while being a statement about `k`. §3.1 | HIGH | Replace with the unique-solution claw bound plus the explicit reason `k`-tree does not apply, and move the `k` content to A1 with the anchor requirement of O15. |
| **O8** | L2's obstruction ("every natural restriction **tried so far**") is an uncited fatigue report (inventor-protocol §4) and is optimistic in direction: A4 shows the generic case is `e = 2δ`, strictly **worse** than 1:1, with alignment only breaking even. §3.1 | MEDIUM | Replace the field with A4's `e = δ − 1/2` condition and its two pre-registered nulls; restate the cheap test as a **correlation** measurement, not an exchange-rate measurement. |
| **O9** | L4's obstruction pointed the batch's cheapest work at the figure's *sourcing* when the decision-relevant structural fact (general DG is `p^{1/2}`; the descent is the bottleneck) was derivable from frozen text already in this repo (line 51). §3.1 | MEDIUM | Replace with the hitting-time obstruction of §3.4 and its steering requirement. |
| **O10** | L5 has no obstruction field and none of the AGENTS rule 9 deprioritisation parts; its status is undefined against `pause_conditions[1]`. §3.1 | MEDIUM | Record L5 as `OUT-OF-TARGET (memory axis)` with an explicit revisit condition (a genuine sub-vOW point), so it is never counted as closed. |
| **O11** | The Minkowski category error is replicated in `RQ-SSIQ-9702af` `scope.methods` ("bounding the minimal degree … **from below** (Minkowski-type obstructions)"), not only in `goal.yaml`. §3.1 | MEDIUM | Any correction must supersede both records, or the RQ re-seeds the error into BATCH-002. |
| **O12** | `goal.yaml` title, objective, and **completion criterion 4** state the target on "the supersingular isogeny problem", reachable only via the uninspected `[35]` cascade, while every derived condition is a **OneEnd** condition. The producer packages are clean; the goal record is not. §3.3 | MEDIUM | Amend criterion 4 to name OneEnd (Problem 2.2) and to require any EndRing/Isogeny extension to carry the `[35]` dependency explicitly. Discharge by REC-2. |
| **O13** | "F4/F5 exponent-free" is stated flatly; it holds only inside Heuristic 1's uniformity range. Outside it (`B` polylogarithmic) `r → 1/3` and the register's conclusion changes sign. §3.2 | LOW-MED | Add the uniformity range to the A6 anti-lever register and to `exponent_budget.md` §2.2's F5 row. |
| **O14** | The correct L4 finding ("the `p^{1/4}` phase is asymptotically free") is one sentence away from the incorrect inference "L4 is dead". The same sentence implies the DG architecture's ideal ceiling **is** `p^{1/4}` — the goal's exact target — making L4 the only lever whose ceiling meets the target. §3.4 | MED-HIGH | The checkpoint must record L4 as **OPEN, re-specified**: obstruction = hitting time for a density-`p^{-1/2}` set in an expander; live question = existence of a computable proximity/`δ_E` gradient; `Õ(p^{1/4})` figure explicitly **not** usable as evidence for `F_{p^2}`. |
| **O15** | A1's payoff table (`k=3 → 2/9`) assumes `c = 1`, which is refuted by default: absent an anchor at an interior vertex, a `k`-way split regroups into an unbalanced two-way split, dominated by line 181's balanced optimum; the `(k−1,1)` grouping gives `T = (2/3)(k−1)/k`, i.e. `4/9` at `k = 3`. §3.5 | MED-HIGH | Restate A1 as conditional on exhibiting an anchor, with the quantified penalty otherwise. Do not carry the payoff table into BATCH-002 unqualified. |
| **O16** | AOV's exhaustive `δ_E` data (`p ≤ 265,207`, i.e. `log2 p ≤ 18`) sits **below** `RQ-SSIQ-9702af`'s own declared toy band `log2 p ∈ [20, 60]`. | LOW | Any empirical D1 check is reported as **sub-toy**, falsification-only, and never as validation of an asymptotic (AGENTS rule 7). Stated in REC-1 below. |
| **O17** | `knowledge/literature/KN-LIT-1732.md` (the corpus entry for the keystone AOV source) declares a local PDF that does not exist and records "ITS CONJUGATE" as an author. Producer logged this as A5; I endorse it as material, because it is the pointer a Validator will follow to the one external result the entire headline exponent rests on. | LOW-MED | Coordinator supersedes `KN-LIT-1732` (corpus entries are immutable; this is a supersession, not an edit). |
| **O18** | The L1 audit is a **closure deliverable** under `docs/inventor-protocol.md` §5 and carries none of §5's required fields: `object`, `depth of verified structure`, `dominated_by`, `sota_delta`, enumerated closures, open directions. The substance is present; the fields are not, so an automated reader sees an unchecked absence rather than a checked `n/a`. | LOW-MED | Checkpoint carries `dominated_by: "n/a (no algorithm claimed)"` and `sota_delta: "no attack; ceiling and bookkeeping contribution only"` — valid, complete answers per §5 — plus the depth-of-structure tier. |
| **O19** | `lever_additions.md`'s coverage table is a coordinate list of one cost identity and carries no inheritance of `lever_completeness_disclaimer`. As written it will be quoted as an exhaustiveness argument. §1.2 | MEDIUM | Add one sentence to the table: *"not a symbol in `T`" is not "not a route"; `T` models one algorithm family.* A7 (§1.1) is the immediate counterexample. |
| **O20** | The producer's own conditionality flag on §6.4 ("if F1↔total is corrected, §6.4 must be recomputed") is now **due** — `TASK-20260805-85af9d` corrected parts of the opening reading — and is assigned to nobody. | LOW | Assign the recomputation in BATCH-002. I expect it to pass: the master identity of `exponent_budget.md` §3.3 preserves `F1 → total`. |

**Objections I could not resolve and label as unresolvable within this batch:**
none of the above is unresolvable; O1–O5 and O14–O15 are resolvable by rewording
and re-labelling at zero cost, O6/O15 by pen-and-paper argument, O12/O17 by one
fetch each, and O3 by a lookup in a file already frozen here. The **only** genuinely
unresolvable item under this harness is the model-independence cap of §0, which no
action inside this repository can lift.

---

## 5. Required controls

1. **Null-object control for D1 (not run; required before D1 is cited as more than a
   count).** D1's shape `T^{3/2}p^{-1/2}` **is** the Gaussian-heuristic short-vector
   count for a random rank-3 lattice of determinant `≍ p`. The control is: run the
   identical count against random ternary forms of discriminant `p/4`. The expected
   outcome is a **match** — and a match is a **controlled null**, not a finding: it
   says the closure asserts no arithmetic structure beyond "Gross lattices are not
   anomalous". Record it that way.
2. **The endpoint the audit owed and did not pay.** D1 at `T = O(1)` must return
   `p^{-1/2+o(1)}`, which must agree with (a) the `F_p` locus size `≍ p^{1/2}` in `≍ p/12`
   curves and (b) the frozen text's own **line 53** statement that adjacency to the
   conjugate occurs with probability `O(p^{-1/2})`. Zero cost.
3. **"What should the quantity do."** For any empirical `δ_E` statistic proposed in
   BATCH-002: `fraction(T)` must **rise** to 1 as `T → p^{1/3}` and must **fall** like
   `p^{-1/2}` at fixed `T` as `p` grows. A `fraction` that does not decay in `p` at
   fixed `T` is an instrument bug, not a finding.
4. **Nearby-object control for A1/A7.** Any `k`-way search or any cross-attempt
   amortisation must be run against a structure-free surrogate (`k` lists with no
   conjugation relation; unrelated tables with no known connecting isogeny). If the
   speedup appears there, it is an artifact. `lever_additions.md` A1 already requires
   this for `k`; extend it to A7.
5. **Pre-registration of L2's nulls.** `e = δ` (aligned) and `e = 2δ` (independent) are
   the null outcomes and must be written down **before** any exchange-rate measurement.
   A measured `e ≈ δ` is the null, not a signal.
6. **Cost-charging control.** Any invariant, precomputation, or shared structure
   proposed under A3, A5, or A7 must have its own construction cost inside the total
   before any exponent is claimed (`KN-LIT-7593`; an eliminated search dimension is not
   a speedup until the invariant's cost is charged).

---

## 6. Baseline comparison and Pareto honesty

The batch claims no algorithm, so there is no Pareto position to defend; but the
frontier it must eventually be compared against is stated correctly across the records
and I confirm it row by row:

| row | figure | axis coverage | status in these records |
|---|---|---|---|
| unconditional | `p^{1/2}·(log p)^{O(1)}` time, **polynomial memory** [21] | time + memory | correctly carried |
| heuristic-conditional | `p^{1/3+o(1)}` time **and** memory, above a **superpolynomial** `o(1)` | time + memory + disclosed overhead | correctly carried, with all four qualifiers (`exponent_budget.md` §0) |
| interpolation | vOW: time `p^{1/2+o(1)}/w^{1/2}` at memory `w`; with `n` processors, `/(w^{1/2}n)` | time–memory–parallelism | correctly carried; `target_conditions.md` §6 charges it as `c = 3/2` |
| `F_p`-restricted | `Õ(p^{1/4})`, **heuristic**, **high-storage**, **memory unstated** | time only; memory absent **in the source** | correctly characterised and correctly barred from use as `F_{p^2}` evidence |

**Memory is charged, and charged correctly** — `target_conditions.md` §6 is explicit
that every admissible route takes memory to `1/4` too, and that **no route in the table
gives `p^{1/4}` time at polynomial memory**. That is the honesty the exemplar profile
(A8/C14–C15) demands and most records in this program omit.

**One gap on the frontier.** No record states where a hypothetical `p^{1/4}`-time,
`p^{1/4}`-memory algorithm would sit against vOW **at matched memory**: at `w = p^{1/4}`
vOW gives `p^{1/2}/p^{1/8} = p^{3/8}`, so the hypothetical would dominate the entire
frontier at that memory point. Worth stating once, in the checkpoint, so that a future
candidate is compared against the right row rather than against the headline.

**`dominated_by` for this batch:** `n/a (no algorithm claimed)`.
**`sota_delta`:** `no attack; ceiling, bookkeeping, and baseline-acquisition contribution
only`. Both are checked against every row above, not asserted.

---

## 7. Cheapest next falsification for BATCH-002

The producer's own R1 (Validator re-derives D1 ingredient (c)) is already running as
`TASK-20260805-89a2e7`. The task asks for the **next** one. Ranked by
(decisiveness ÷ cost):

### REC-1 (primary) — Fit D1's *shape* against AOV's released exhaustive `δ_E` data, with a stated prediction and a stated artifact tell

**Why this and not more reading.** D1 is now the sole load-bearing pillar of the batch's
only closure (O1). The Validator's re-derivation and this measurement **fail
differently**: a shared misreading of the optimal-embedding count survives any amount
of re-derivation by the same model (§0's cap) and shows up immediately in a fit.

**The measurement.** AOV computed `δ_E` for *every* supersingular curve for every
`p ≤ 22,000`, with sieved ranges to `p ≤ 265,207`, and released code (`[AOV26]`, "WISDE").
Fit `#{E : δ_E ≤ T} = c · T^α · p^β` in two directions: `α` from log-log regression in `T`
at fixed `p`; `β` from regression in `p` at fixed small `T`.

**Prediction if D1 is right:** `α = 3/2`, `β = 1/2`.
**Artifact tell / the thing that reopens L1:** the failure mode the producer named —
ingredient (c) contributing a factor `n^{1/2}` — gives `α = 2`, whence
`fraction(p^{1/4}) ≪ p^{2·(1/4) − 1/2} = p^{0}`, i.e. **L1's second disjunct reopens at
exactly exponent `1/4`.** `α = 3/2` versus `α = 2` is a large, easily separated
difference over `T ∈ [1, 30]` across thousands of primes.
**Null-object control:** the identical fit on random ternary forms of discriminant `p/4`
(control 5.1). Expect a match; record a controlled null.
**Free anchor checks, before any regression:** `α, β` must reproduce
`#{δ_E = 1} ≍ p^{1/2}` (the `F_p` locus) and `fraction → 1` at `T = (p/2)^{1/3}`.

**The honesty constraint, stated before the measurement (O16, AGENTS rule 7).**
`log2 p ≤ 18` is **below** this question's own declared toy band. This measurement can
**falsify** D1's exponent; it can **never validate** D1 asymptotically, and no record may
present a passing fit as validation of the closure. The producer's R2 dismissed this
route as "numerically vacuous at `T = p^{1/4} ≈ 22`" — correct about the *bound's value*
at that point, and beside the point: the object being measured is the pair of
**exponents in D1's shape**, not the bound's numeric value at one `T`.

**Cost:** one session, near-zero compute, on already-published data the producer has
already located.

### REC-1b (rider, same dataset, no extra acquisition) — Is `δ_E` predictable from cheap invariants of `j(E)`?

The same table answers L4's live question (§3.4): does any `p^{o(1)}`-computable function
of `j(E)` correlate with `δ_E` above chance? Null control: random relabelling of `δ_E`
across curves. A null result is a real, recordable strengthening of L4's obstruction
(no steering signal at reachable `p`), scoped to the tested invariants. A non-null
result is the single most valuable thing this campaign could find, because L4's ideal
ceiling is exactly the goal's target. **Scope it hard:** at `log2 p ≤ 18` this is a
sub-toy screen for the *existence* of a signal, never a claim about cryptographic sizes.

### REC-2 (cheapest of all, and it is a lookup) — Fetch `[35]` and cost the cascade

Page–Wesolowski, *The Supersingular Endomorphism Ring and One Endomorphism Problems are
Equivalent*, EUROCRYPT 2024 — publicly available as IACR ePrint 2023/1399, and the
environment demonstrably reaches `eprint.iacr.org` (retrieval `sccs_abs` succeeded).
Record the exact cost statement and the hypotheses (heuristic? GRH? error model?) of
Theorem 1 and Proposition 8.5. This discharges O12, closes a `KN-TECH-058` standing gap
(`RT-20260728-013` RSC1), and is the only thing standing between "OneEnd at exponent X"
and "the supersingular isogeny problem at exponent X" — the problem the goal's own title
names.

**Prerequisite for REC-2 and for any second reading of AOV: fix the environment.**
Anomaly A2 records that no PDF text extractor exists here (`pdftotext` absent, `pypdf`
and `PyMuPDF` unimportable, `pip install pypdf` panics). That blocks the `[35]` body, the
second independent rendering of AOV, and the `[15]` body. It is the cheapest action in
the entire batch and it unblocks three others.

### Not recommended as "cheapest"

- **Re-attacking F1 / D1 by further reading.** §0's cap makes additional same-model
  reading nearly free of information. REC-1 is the substitute.
- **A toy measurement of L2's exchange rate as currently specified.** It returns the
  null in both natural cases (O8). Re-specify it as a correlation measurement with A4's
  pre-registered nulls first, or it burns a batch to observe `e ≈ δ`.
- **Building anything on A1.** §3.5 refutes its default accounting at zero cost; the
  anchor question is a whiteboard question and must be answered before any measurement.

---

## 8. Narrowest supported statement

> **Scoped to BATCH-001's two committed packages, at commits `50596409` and `7ec7f730`,
> under session-only (not model) independence:**
>
> 1. The exponent budget of the archived `p^{1/3+o(1)}` algorithm is correctly
>    decomposed from primary text, with corrected locators, and its total time exponent
>    equals the exponent of the Theorem 1.5 degree bound (`exponent_budget.md` §3.3).
>    Time and memory are equal in every admissible route of the table, and the batch
>    charges memory beside time throughout.
> 2. `F4` carries exponent `0`, and no total-exponent reduction can be placed on it,
>    because `r ≥ 0` — **inside Heuristic 1's stated uniformity range**. I attempted the
>    joint `B`-move attack named by the task and it fails in both directions
>    (`B = p^β` gives `T = 1/3 + β`; `B` polylogarithmic gives `T → 2/3`). The refutation
>    holds **for the exponent** and would be false if carried to practical impact.
> 3. **L1 is closed for the target `E^{(p)}` and its small-degree-modified neighbours,
>    by a SINGLE derivation-tier argument (D1) whose three arithmetic ingredients were
>    not fetched.** The unconditional pillar P1 is logically subsumed by D1 and closes
>    only the disjunct the algorithm does not need. N5 (structurally different auxiliary
>    targets) is **open** and belongs in its own lever row.
> 4. The `Õ(p^{1/4})` Delfs–Galbraith figure is genuine, heuristic, `F_p`-restricted,
>    high-storage, with memory unstated by the source, and contributes nothing toward
>    `F_{p^2}`. **L4 is not thereby dead**: its ideal ceiling is exactly `p^{1/4}` and
>    its live question is the existence of a computable descent-steering signal.
> 5. Nothing in either package states, implies, or is arranged to suggest that a
>    `p^{1/4}` algorithm exists, is likely, or is near. The source's affected-vs-safe
>    scheme scope is inherited **unwidened** — I checked every name in both lists.
> 6. Nothing here bears on whether the supersingular isogeny problem is `p^{1/3}`-hard.
>    D1 is a ceiling on **one method family**, and the batch says so itself.

---

## 9. Verdict

> **CONFIRM-SCOPED.**

The mathematical content of both packages survives adversarial reading. Nothing asserted
is false; no claim exceeds its tier; the `0.25 is a target, not a claim` constraint is
honoured throughout; the scope is inherited unwidened; memory is charged beside time; the
null-object control N4 is a genuine control and it passes; and both producers recorded the
Coordinator's own errors rather than silently repairing them, which is the behaviour this
contract is supposed to produce.

It is **not** a bare CONFIRM because three things would mislead the checkpoint that reads
them: the closure's evidential tier (single-pillar, derivation, unfetched ingredients — O1),
the bare token `CLOSED` on a lever with an untouched disjunct feeding a pause condition
(O4), and the one-sentence distance between L4's correct finding and L4's incorrect
retirement (O14). Add to that four defective obstruction fields (O7–O10), one missing
route (§1.1/A7), one criterion excluding the case it was written for (O5), and one
lever whose advertised payoff is refuted by default (O15).

It is **not** a CHALLENGE. Nothing requires reversal; everything requires relabelling,
one route added, and one measurement run.

**On the specific question the task asks:** L1's verdict should stand, **relabelled** —
`CLOSED-IN-SCOPE`, single-pillar, derivation-tier, with N5 minted as its own lever and
the producer's reversion condition (`if D1 falls, disjunct 2 reverts to UNRESOLVED`)
carried verbatim into the checkpoint.

---

## 10. Required output block

```yaml
red_team_report:
  id: RT-BATCH-001
  task_id: TASK-20260805-fb72f1
  goal_id: GOAL-SSIQ-001
  batch_id: BATCH-001
  reviewed_commits: ["50596409", "7ec7f730"]
  claim_under_review: >-
    (a) the re-derived exponent budget F1-F8 and the numeric conditions for total
    exponent 1/4; (b) the L1 CLOSED verdict and its two pillars; (c) the L4 baseline
    acquisition; (d) the Coordinator frame in goal.yaml (levers L1-L5, exponent_budget,
    completion criteria) and RQ-SSIQ-9702af.
  objections: [O1, O2, O3, O4, O5, O6, O7, O8, O9, O10, O11, O12, O13, O14, O15, O16, O17, O18, O19, O20]
  objection_severity:
    high: [O1, O6, O7]
    medium_high: [O4, O5, O14, O15]
    medium: [O2, O3, O8, O9, O10, O11, O12, O19]
    low_medium: [O13, O17, O18]
    low: [O16, O20]
  unresolvable_objections:
    - "None inside the repository. The model-independence cap of section 0 is unresolvable under this harness."
  required_controls:
    - "Null-object control for D1: identical count on random ternary forms of discriminant p/4; a match is a CONTROLLED NULL, not a finding."
    - "D1 small-T endpoint check against the F_p locus size and frozen-text line 53 (probability O(p^{-1/2}))."
    - "Decay discipline: fraction(T) must rise to 1 at T = p^{1/3} and fall like p^{-1/2} at fixed T as p grows."
    - "Nearby-object control for A1 (k lists with no conjugation relation) and for A7 (unrelated tables with no known connecting isogeny)."
    - "Pre-register L2's nulls e = delta and e = 2 delta before any exchange-rate measurement."
    - "Charge the construction cost of any invariant, precomputation, or shared structure into the total (KN-LIT-7593)."
  counterexample_or_mutation: >-
    Two, both zero-compute and both derived in this report. (1) A1 mutation: absent an
    anchor at an interior vertex, a k-way split regroups into an unbalanced two-way
    split, dominated by the balanced optimum of line 181; the (k-1,1) grouping gives
    c = k-1 and T = (2/3)(k-1)/k, i.e. 4/9 at k = 3 - strictly worse than the incumbent.
    (2) F4 mutation (the task's named duty): moving B out of the p^{o(1)} regime fails in
    both directions - B = p^beta gives T = 1/3 + beta, B polylogarithmic gives T -> 2/3 -
    so the joint F3/F4 trade cannot recover an exponent and the F4 refutation survives its
    strongest stated attack.
  baseline_comparison: >-
    Frontier checked row by row: p^{1/2}(log p)^{O(1)} unconditional at polynomial memory;
    p^{1/3+o(1)} time AND memory conditional on Heuristic 1 above a superpolynomial o(1);
    the van Oorschot-Wiener interpolation p^{1/2+o(1)}/w^{1/2} at memory w (and
    /(w^{1/2} n) parallel); and the F_p-restricted Otilde(p^{1/4}) heuristic high-storage
    figure, which is NOT a row of this problem's frontier. All four are carried correctly
    and memory is charged beside time throughout. One gap: no record states that a
    hypothetical p^{1/4}-time p^{1/4}-memory algorithm would dominate vOW at matched
    memory (vOW at w = p^{1/4} gives p^{3/8}).
  dominated_by: "n/a (no algorithm claimed by this batch)"
  sota_delta: "no attack; ceiling, bookkeeping and baseline-acquisition contribution only"
  heuristic_challenges:
    - "D1's shape is the Gaussian-heuristic short-vector count for a RANDOM rank-3 lattice of determinant ~p; its content is that Gross lattices are not anomalously short-vector-rich. Proved as an upper bound (right direction), but it is a null-model count and must be labelled as one (O2)."
    - "Heuristic 1's uniformity range is load-bearing for the claim that F4/F5 are exponent-free; outside it r becomes positive and the anti-lever register's conclusion changes sign (O13)."
    - "Saturation of D1 at 1/3 is forced for any correct upper bound and is not evidence of sharpness (O3)."
  cost_model_challenges:
    - "TOTAL = per-attempt x P0^{-1} is an unaudited composition law; it is invisible at the source's parameters (P0^{-1} = p^{o(1)}) and load-bearing in section 6.4's lowered-threshold regime, where attempts number p^{Theta(1)} (O6, and route A7)."
    - "Section 6.4's method ceiling is additionally conditional on the goal record's self-declared-unverified opening reading, whose promised recomputation after TASK-20260805-85af9d's corrections is now due and unassigned (O20)."
    - "A1's payoff table assumes c = 1 at arity k, which is refuted by default (O15)."
  reduction_and_scope_challenges:
    - "Corollary 1.2's cascade via [35, Theorem 1] and [35, Proposition 8.5] is correctly marked CITED-NOT-VERIFIED in both producer packages, with no exponent assigned. But goal.yaml's title, objective and completion criterion 4 state the target on the problem reachable ONLY through that cascade, while every derived condition is a OneEnd condition (O12). Discharged by fetching ePrint 2023/1399."
    - "Affected-vs-safe scheme scope: checked every name in both of the source's lists across goal.yaml, RQ-SSIQ-9702af, BATCH-001-OPENING.md and both producer packages. NO WIDENING FOUND. Residual note: the source's 'safe' classification rests on other cryptanalysis dominating TODAY'S parameter choices and would need re-derivation, not inheritance, if this campaign's target were ever reached."
  proof_architecture_challenges:
    - "Quantifier-order attack: D1's population quantifier matches what L1 requires; PASSES. But D1 subsumes P1, so the closure is single-pillar (O1)."
    - "Method-ceiling attack: section 6.4's ceiling fixes a composition law it never varies (O6)."
    - "Nearby-object attack: N1-N4 genuinely run and N4 is a passing null-object control. N5 is untouched and R3's criterion for auditing it excludes rank > 3 by fiat and assumes a quadratic degree form (O5)."
    - "Observation-collision: correctly recorded as not applicable in its usual form (the conclusion is a population count); AOV's p = 22,273 unrealised-Gram-matrix collision is correctly recorded as harmless to D1 and material to any construct-a-curve lever."
  lever_enumeration_finding:
    missing_route_named: "A7 - cross-attempt amortisation of the searched family under re-randomisation (distinct from A5, which is cross-INSTANCE precomputation)"
    route_class_hidden_by_guidance: "the rank axis - raise the rank / lower the normalised determinant of the governing lattice by changing the ambient object; excluded by R3's criterion and dismissed in exponent_budget.md section 6.6 on a q-argument that does not address d"
    structural_finding: "the coverage table is a coordinate list of ONE cost identity modelling ONE algorithm family; 'not a symbol in T' is not 'not a route' (O19)"
    searched_and_not_found: ["special-form primes (closed harder by D1's uniformity in p)", "unbalanced splits and per-side smoothness bounds", "the non-scalarity correctness argument", "quantum time-exponent"]
  narrowest_supported_statement: "See section 8 of this report, items 1-6."
  next_concrete_action: >-
    REC-1: fit #{E : delta_E <= T} = c T^alpha p^beta against AOV's released exhaustive
    delta_E data (p <= 265,207), predicting alpha = 3/2 and beta = 1/2, with the
    ingredient-(c) failure mode predicting alpha = 2 (which reopens L1's second disjunct
    at exactly exponent 1/4), with a random-ternary-form null control and the free
    endpoint anchors at T = O(1) and T = (p/2)^{1/3}, and reported as SUB-TOY,
    falsification-only evidence per AGENTS rule 7. Rider REC-1b on the same dataset:
    test whether delta_E is predictable from cheap invariants of j(E) against a
    random-relabelling null, which is L4's live question. REC-2 (cheapest lookup): fetch
    IACR ePrint 2023/1399 and record the cost statements and hypotheses of [35, Theorem 1]
    and [35, Proposition 8.5]. Prerequisite for REC-2: install a PDF text extractor
    (anomaly A2), the cheapest action in the batch, which unblocks three others.
  verdict: CONFIRM-SCOPED
  l1_verdict_recommendation: "STAND, RELABELLED: CLOSED-IN-SCOPE, single-pillar, derivation-tier, with N5 minted as its own lever row and the reversion condition carried verbatim."
  independence_cap: "SESSION independence only, NOT model independence. My concurrence on D1 is not independent corroboration of D1."
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-001/reviews/RT-BATCH-001.md
  files_written_outside_scope: []
  ledger_touched: false
  record_statuses_changed: 0
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits", the Coordinator's ledger
    archive task commits this report. It is not durable until that archive exists.
```
