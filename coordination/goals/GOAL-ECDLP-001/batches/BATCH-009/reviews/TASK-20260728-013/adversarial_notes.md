# Adversarial notes — TASK-20260728-013

Red team of the BATCH-009 disposition. Report id `RT-20260728-002`.
Bound snapshot `457d220962f73a3070ebf3d9cb74354d87baf02f`, parent `4f87e165`,
receipt verified against Git before anything below was read (five paths, five
matching SHA-256 values, reachable from `HEAD` at `b7efee01`, clean tree, and
`experiments/EXP-ENDO-001` containing `specification.yaml` plus the new
`amendments/` file and nothing else — **zero runs exist**).

Independent, non-originating session. Not the `TASK-20260728-012` session, not
the `TASK-20260728-004` session. `requested_policy: review-xhigh`,
`resolved_model_id: claude-opus-5` as reported by the runtime,
`model_verified: false` (no adapter probe; Bash is read-only for this task).

Nothing in this document is a cryptanalytic result, an attack, an attack
improvement, a hardness result, a lower bound, a closure or an impossibility
claim. Nothing here reaches any claim tier: there is no instance, no curve, no
field size and no measurement anywhere in the artifacts under review.

The card requires the case **against** to be argued first and in full. It is.

---

## Part 1 — The case that the withdrawal is a rationalised retreat

This is the strongest version I can build, and I want it on the record at full
strength because most of it is true.

### 1.1 The batch consumed a committed action and returned nothing measured

BATCH-009 opened by re-ranking `EXP-ENDO-001` *above* `EXP-STR-004`, a
**committed** action carried forward from `DEFER-BATCH007-001`. It justified
that promotion partly on the claim that the endomorphism experiment "gates
`IDEA-20260727-005`'s classification barrier." It then froze the contract,
received a `REVISE`, cancelled the executor card, and closed with the
experiment withdrawn and no measurement of any kind. The net effect on the
research frontier is that a replication obligation was delayed by one batch.

### 1.2 The gating claim was false, and its own source record said so

`RT-20260728-001` objection N3 says the frozen design could not gate the
classification barrier, because the load-bearing part of that barrier is *which
homomorphisms are efficiently computable* and the design fixes the eigenvalues
by fiat. I confirm that, and I can put it more sharply against the Coordinator.

`IDEA-20260727-005`, committed **before** the contract was frozen, already
contains as `proof_decomposition`:

- Lemma 1, scalar rigidity;
- Lemma 2, `[Z^{2r} : W_r] = N` and `det(W_r) = N` **for every r**;
- Lemma 3, Minkowski shrinkage `N^{1/(2r)}`;
- Lemma 4, MITM at `Θ(2^r √N)` time **and memory**;

and in `target_complexity.tradeoff_note`:

> "the augmented lattice is not merely neutral but Pareto-dominated … sits at
> the `S = T = N^{1/2}` corner of the van Oorschot–Wiener curve, which is
> strictly dominated by parallel rho with distinguished points."

Ground **G6** of the withdrawal — "no outcome could have been target-class,
because the algorithm is Pareto-dominated by BSGS at every rank" — is therefore
not a discovery of this batch's review. It was committed in the proposal that
spawned the experiment. **The single decisive reason for withdrawing the
contract was available before the contract was frozen, in the record the
contract was derived from.** A batch that spends its design, freeze, snapshot
and review cards to rediscover a fact already in its own source record has not
found a result; it has paid for a lookup.

### 1.3 The "result" is the reviewer's, and the one new claim is defective

`refutation_claims.yaml` discloses this honestly, which I credit: D1, D2 and D4
originate in `RT-20260728-001`; only D3 is new. So the batch's own additive
contribution beyond the review it commissioned is D3 — and D3's conclusion
clause is **false as written** (objection S2), refuted by the very algorithm the
contract specifies and by the fact that its "information-free" sublattice `R_2`
is the GLV decomposition lattice, the basis of the only endomorphism speedup
this campaign acknowledges. A batch whose only original claim is over-stated,
and whose author is also its judge, is thin ground for a disposition.

### 1.4 The two-point argument — the most confident claim in the disposition —
rests on a false premise

This is the argument the disposition labels **"the Coordinator's own arithmetic,
not the review's"**, which is the strongest evidential label used anywhere in
the batch. Nobody had checked it. It does not survive.

The claim: with `genuine_r_bound: 2` on J0, the genuine `r`-sweep has exactly
two points, `r = 1` and `r = 2`, and two points cannot separate a `2^r` constant
from an exponent.

The bookkeeping is right *given the definition*. The definition is wrong.

D1 derives `genuine_r_bound = 2` from the **Z-rank** of `End(E)`, which for an
ordinary curve over a finite field is 2 by Deuring. But rank is not the
invariant that produces the degeneracy D2 exhibits. What collapses the first
minimum of `W_r` to 1 is the existence of an integer relation
`Σ c_i λ_i ≡ 0 (mod N)` of **infinity norm at most `X = ⌈N^{1/(2r)}⌉`**. Rank
deficiency guarantees *some* relation; it says nothing about whether that
relation is *short*. The frozen triple `{1, λ, λ²}` is degenerate because its
relation is `(1,1,1)`, of norm 1 — not because `End(E)` has rank 2.

On the **same** `j = 0` curve, take `φ₃ = a + b·φ`. It is a genuine
endomorphism; it is evaluable as `[a]P + [b]φ(P)` in `O(log N)` group
operations; `CTRL-EIGEN`'s check `φ_i(P) = [λ_i]P` passes on the curve exactly
as it does for `φ`. Its eigenvalue is `λ₃ = a + b·λ₂ mod N`, and the relation
vector `(a, b, −1)` has norm `max(|a|,|b|)`. The relation lattice
`R₃ = {c ∈ Z³ : Σ c_i λ_i ≡ 0}` has determinant `N` in dimension 3, so its
generic first minimum is about `N^{1/3}` — the **square** of `X = N^{1/6}`. A
relation short enough to matter is a measure-zero accident, and the CM triple is
exactly that accident.

**Genuine, curve-backed, eigenvalue-checkable `r = 3` and `r = 4` cells
therefore exist**, and `G7`'s premise is false.

The reviewer already had the right invariant and the derivation note did not
carry it across. `RT-20260728-001` objection B4: the list-build term shrinks
"only if a **small-coefficient** Z-relation exists among the `λ_i`." Required
control RC-3: "Reject any synthetic draw admitting a nonzero integer relation
`Σ c_i λ_i = 0 mod N` with `max |c_i| ≤ X`." **RC-3 is the correct
genuine/synthetic criterion, stated by the reviewer, and D1 replaced it with a
rank count.**

### 1.5 The precedent argument is self-fulfilling

The disposition's fourth rationale is: *"Asked what makes an `EXP-ENDO-001` v2
cycle different, the honest answer is: nothing I can name."* The candour is
real. The logic is not. It uses past attrition (`EXP-IC-002`: REVISE → amend →
re-review → never executed) as evidence that repair is futile, and thereby
produces more attrition. A decision procedure that treats its own failure rate
as a reason not to try converges to never executing anything, and it will always
be able to cite an unbroken record — one it is extending with each application.

### 1.6 The stated reason for not promoting `EXP-STR-004` is backwards

The disposition says option (b) loses partly because "the 7200-second Executor
budget it would need was allocated to the contract now being withdrawn."
Withdrawing the contract **releases** that allocation — the amendment's own
commit message records `Executor compute allocation 7200 -> 0 s`, and
`INT-BATCH009-S` records the batch budget falling from 23100 to 18000 seconds.
The budget is an argument *for* (b).

### 1.7 The criterion that killed (a) also kills the recommended BATCH-010

`G6` rejects amendment because no outcome could be target-class. But
`DEFER-BATCH009-001`'s own `deferral_reason` records that `EXP-STR-004`'s

> "lane's only reproducible effect is the constant factor `r = 3` measured at
> 2.62 to 3.20x, which target-result-profile rule A1 places outside target
> class; its best outcome adjudicates an instrument inside that lane and cannot
> move an exponent in either direction."

Applied consistently, the criterion that killed `EXP-ENDO-001` disqualifies the
recommended opening of BATCH-010. As written, the two rulings are inconsistent.

---

## Part 2 — Why the case against nonetheless fails, and the ruling stands

Every point in Part 1 is a real defect in the **reasoning**. None of them
touches the two grounds that actually decide the question, and both of those
came from the independent reviewer rather than from the deciding session.

**G6 is decisive and repair-proof.** The withdrawn algorithm costs about
`2^{r+1}√N` operations with `2^r√N` memory. BSGS costs `1.5–2√N` with `√N`
memory. Pollard rho costs `0.886√(N/|Aut|)` with `O(w)` memory and parallelises
linearly. The algorithm is dominated in **both** coordinates at **every** rank
including `r = 1`, where it is exactly `2×` BSGS, and shrinking the stored list
to `w` puts it on the Shanks line `N/w`, strictly worse than rho's `√N/m` for
every `w < √N`. There is no time–memory point at which it wins, so no amendment
to the *protocol* can change what the *algorithm* is. Under A1 (governing;
`docs/target-result-profile.md` is ABSENT at this commit and present on
`origin/main`, and I do not cite it as present) nothing in this lane is
target-class, and the largest positive quantity available anywhere in it is the
classical `√6 ≈ 2.449` automorphism constant.

**G3 is independent and also decisive.** `S3` bands the measured ratio within a
factor 2 of `2^{r+1}` at every rank, size and family, while the contract's own
`X = ⌈N^{1/(2r)}⌉` makes the exact ratio reach 3.81 at 16-bit `r = 4` and 3.57
at 20-bit `r = 4` — and the pre-registered degradation order drops 28-bit cells
*first*, so the deterministically failing cells are exactly the ones that always
survive. `S5` fails independently, calibrating against `|Aut| = 6` and `4` while
`CTRL-BASELINE` specifies negation-only rho. The `confirmed` branch is
unreachable from the contract's own arithmetic. Executing v1 would have spent
7200 seconds to return `mixed` for reasons derivable on paper.

**And G7's conclusion survives its premise's failure.** The `r = 3` cell rescued
in §1.4 is, as a lattice, the preimage of `W₂` under an explicit integer matrix
— a Z-linear reparametrisation of the `r ≤ 2` object, carrying no endomorphism
content the `r = 2` cell did not already carry. So the rescued sweep still
measures a **construction** rather than endomorphisms, which is objection B1's
original charge arriving by a different route. A repaired two-point (or
four-point) sweep with RC-1 and RC-3 would establish only what arm D already
establishes with no curve at all: that a uniformly drawn index-`N` sublattice of
`Z^{2r}` has index `N` and roughly attains its Minkowski bound. That is one
cheap arm, not a batch.

So: **the disposition is right and its published reasons are the wrong ones.**
That is not a small finding. A decision whose stated grounds are defective is
not reproducible even when its outcome is correct, and the next Coordinator who
applies `G7`'s reasoning to a different lane will apply a false premise.
`DEFER-BATCH009-002`'s `resume_condition (1)` is stated *against* the two-point
cap, so as written a future session could satisfy it trivially by exhibiting a
four-point genuine sweep while establishing nothing. It must be restated against
relation-freeness.

---

## Part 3 — The strongest case that the endomorphism lane is still live

Required by the card. I argue it honestly and then say what it is worth.

1. **Nothing here is about endomorphisms; it is about one lattice
   parametrisation.** D4 is scoped, correctly, to "attacks that construct and
   then reduce `W_r` **as defined in EXP-ENDO-001 STEP 1**." Every other
   encoding is untouched. In particular `R_r` — the GLV decomposition lattice —
   is fully constructible without `k`, and its short vectors are what make the
   `0.886√(N/|Aut|)` walk and GLV scalar splitting work. Endomorphism lattices
   are not a barred class. `W_r` is.

2. **The self-map barrier is elementary and was never the interesting part.**
   `IDEA-20260727-005` C1 is rigorous and always was: every endomorphism of a
   prime-order group is a scalar. The live part of that record is **C2**, the
   *completeness* of the `E1/E2/E3` classification of exit maps — maps *out of*
   `G` into other algebraic groups. Nothing in D1–D4 touches C2. The lane the
   proposal itself names as "the largest lane, containing all of index calculus"
   — non-algebraic, coordinate-consuming attacks — is explicitly outside the
   classification and is untouched here.

3. **Settings this batch says nothing about.** The preprocessing/advice model
   (Corrigan-Gibbs–Kogan, `N^{1/3}` online with `N^{1/3}` target-independent
   advice, already charged in `DEC-20260727-008`): the advice is built without
   any target, so a "cannot construct without `k`" barrier is silent there.
   Multi-target/batch DLP (Kuhn–Struik, about `√(MN)` for `M` targets):
   untouched. Interval and partial-information settings: the natural object is
   not `W_r`. Extension fields and Weil descent: outside the frozen scope
   entirely.

4. **The supersingular and higher-rank cases are not addressed.** D1's rank-2
   fact is about *ordinary* curves. `H-ENDO-001`'s own `interpretation_limits`
   note that a supersingular endomorphism ring has rank 4. Nothing in this batch
   examines what happens when four Z-independent efficiently evaluable
   endomorphisms genuinely exist. I do **not** claim that helps — the reduction
   `End(E) → Z/N` can introduce relations of its own, and supersingular ECDLP
   over `F_p` has its own dominant attacks — but the batch's algebra does not
   cover it and no record may imply otherwise.

5. **The premise repair of §1.4 is itself a small live thread.** The correct
   genuine/synthetic criterion is relation-freeness at threshold
   `X = ⌈N^{1/(2r)}⌉`, not rank. That is a cleaner and more general statement
   than anything in the derivation note, it is decidable by one SVP in dimension
   `r`, and it is the thing a future contract in this lane should pre-register.

**What it is worth.** All five points constrain what may be *written down*, and
none of them makes the lane worth compute. Point 1 concedes the parametrisation.
Points 2–4 are lanes this batch never entered. Point 5 is a definition. Against
`G6` — Pareto domination in both coordinates at every rank — none of them
identifies an outcome that could be target-class. **The lane stays live as a
scope boundary and dead as a compute allocation**, which is exactly the
distinction `EV-ENDO-001` must make and must not blur in either direction.

---

## Part 4 — `INT-BATCH009-S`: honest count, optimistic diagnosis

The self-diagnosis was "mostly selection bias, plus one real defect." I checked
the record rather than the narrative.

**The count is true.** Verified against Git and the queues:

| batch | executed? | evidence |
|---|---|---|
| BATCH-006 | no | executor `TASK-20260727-005` **cancelled** |
| BATCH-007 | **YES** | commit `c79e3a8d`, 20 runs under `experiments/EXP-STR-003/runs`, 120 tracked files, 132.6 s of 5400 s |
| BATCH-008 | no | executor `TASK-20260727-028` never dispatched |
| BATCH-009 | no | executor `TASK-20260728-005` **cancelled** |

"Three of the last four batches have measured nothing" is literally correct, and
stating it plainly rather than as efficiency is to the Coordinator's credit.

**The denominator is contaminated.** BATCH-008's own opening objective declares
it "a bounded LEDGER-INTEGRITY repair" that "contains no research work of any
kind" — a YAML quoting fix for two unparseable specifications. It had no
experiment to execute. The honest research denominator is three: 006, 007, 009,
of which one executed.

**The mechanism differs per case, and the story fits one of three.** The
selection-bias claim is "for quantities that are *determined* rather than
sampled, paper analysis beats a run by construction."

- **BATCH-009: fits.** Vieta on a monic quadratic and a ceiling formula are
  determined. Paper genuinely beat the run here.
- **BATCH-006: does not fit.** `EXP-IC-002` went REVISE → v2 amendment →
  independent re-review → never executed. It died of *process attrition*, not of
  a determined quantity. And the defect the disposition itself attributes to it
  — "a stopping rule halted the primary arm at instance 1 of 34" — is a defect
  only a **run** could have exhibited.
- **BATCH-008: not applicable.**

So the correct weighting is one determined-quantity pre-emption, one process
attrition, one non-research batch. **"Mostly" is the wrong word.**

**The discriminating counter-evidence already exists, and the disposition does
not mention it.** The one batch in four that executed produced a run that
*falsified a paper-level adjudication*. In BATCH-007, red-team observation
`OBS-1`/`RT-OBJ-1` — that a φ-free construction beats the φ-invariant factor
base at every headline `B` — was adjudicated **YES** by `TASK-20260727-017` on
unarchived scratchpad probes. The executed `EXP-STR-003` package returned:

> "F1 FIRES at I1 (11 ≤ 9 false) and I4 (29 ≤ 1 false). The red team's central
> argument … does **NOT** reproduce. Those numbers came from an unarchived
> scratchpad script; 14 of 16 alpha cells reproduced, arm E did not at two of
> four instances."

with the pre-fixed consequence that `OBS-1` had to be withdrawn or rescoped and
`DEC-20260727-009` could not rest on it. The campaign's base rate of executed
batches overturning a paper-level adjudication is **1 of 1**. That is `n = 1`
and I do not over-read it — but it is direct evidence against "paper beats a run
by construction" as a general posture, and the disposition argues that posture
from a two-case sample while its own record holds the counterexample.

**Verdict: honest in count, optimistic in diagnosis, and the incompleteness runs
in the self-serving direction.** Part 3 of the self-diagnosis — the
dangerous-misreading paragraph, "a program that only critiques cannot produce a
result at any tier" — is the most credible thing in the disposition and I
endorse it without reservation. Part 2's identified defect (a threshold
pre-registered without being evaluated at the cells that would run) is real, and
its fix is cheap, correct and **insufficient**: a criterion-feasibility table
checks thresholds against cells, and it would *not* have caught this batch's
opening error, which was freezing a contract whose Pareto position was already
recorded in its own source proposal. That needs `RC-7`.

### What would distinguish the two empirically

Pre-classify, in every future frozen contract, each decisive pre-registered
quantity as **DETERMINED** (a closed-form function of the declared parameters,
evaluable without drawing an instance) or **SAMPLED** (requires drawn
instances). The two hypotheses then predict different things:

- **Selection bias** predicts review pre-empts DETERMINED-quantity contracts and
  SAMPLED-quantity contracts execute.
- **Stopped harness** predicts non-execution regardless of quantity type — for
  budget, scope or attrition reasons.

One additional data point decides it: **if a contract whose decisive quantities
are all SAMPLED also fails to execute, selection bias is falsified on its own
terms.** `EXP-STR-004` is exactly such a contract — arms A′ and E′ produce
measured `α` counts across drawn instances. So **BATCH-010 is the experiment
that decides this question, and it decides it for free.** The classification
costs nothing beyond the table `DEFER-BATCH009-003` already requires (`RC-8`).

---

## Part 5 — Is D3 load-bearing?

**No, and that is the only reason the disposition survives its defect.**

D3 appears in **none** of the seven withdrawal grounds `G1`–`G7`; `G5` cites D4
only. It is load-bearing for exactly one claim: rationale bullet 5, that "D3 and
D4 bear on [`IDEA-20260727-005`'s classification barrier] differently and more
directly" — the surviving residue of the batch-opening rerank rationale, which
fails for the independent reason given in §1.2 and objection S4.

So a decision *would* have rested on a claim its author never had checked, had
the Coordinator not routed it to `TASK-20260728-012` and `TASK-20260728-013`
before writing any ledger record. `INT-BATCH009-R` names this as the batch's
principal methodological weakness and is right to. The gate worked.

D3's parts (i), (ii), (iii) are correct — and (ii) is *stronger* than stated:
any two distinct `k` in `[1, N−1]` force `B = 0` and then `A = 0` for prime `N`,
so the argument needs neither `k = 1` and `k = 2` specifically nor `N ≥ 3` as a
separate hypothesis. What fails is the **conclusion clause**:

> "Every vector of `W_r` that an attacker can write down without already knowing
> `k` lies in `R_r × R_r` and carries zero information about `k`."

Refuted by the contract's own algorithm: an attacker writes any `(a, b)` with
`B(b)` invertible — no knowledge of `k` required — computes `k* = −A/B mod N`
and tests `[k*]P = Q`. That vector was written without knowing `k` and it
decides one candidate. The whole meet-in-the-middle is a procedure for writing
such vectors. "Constructible" equivocates between *constructible-with-a-
guarantee* (must lie in the `k`-independent intersection, hence useless) and
*constructible-and-testable* (the actual attack model).

And the framing is contradicted by the literature: `R_2 = {(c₁,c₂) : c₁ + c₂λ ≡
0 mod N}` **is the GLV decomposition lattice**. Its short vectors of norm about
`√N` are what Gallant–Lambert–Vanstone use to split `k = k₁ + k₂λ`, and the same
structure underlies the automorphism-quotient rho walk this batch repeatedly
names as the known correct way endomorphisms help. The sublattice D3 calls
information-free and useless is, in the published record, the useful one.

D3 also invokes **HEUR-1** — the Gaussian random-lattice heuristic — as an
unlabelled premise ("generically `R_r` has first minimum about `N^{1/r}`") in
the same lattice family where D2 has just shown HEUR-1 fails. That paragraph
happens to cut in my favour for objection S1, and I object to it anyway: an
argument I benefit from is not thereby derived.

The weakest hypothesis under which D3 fails outright is **`N` composite**: a
nonzero non-invertible `B` then recovers `k mod N/gcd(B,N)` — Pohlig–Hellman,
partial information, not zero. Within the frozen contract `N` is prime, so D3
holds in scope; but `EV-ENDO-001` must carry the primality hypothesis *inside*
the clause or the clause is false as stated.

---

## Part 6 — Scope confirmations

- **No research result at any tier.** I read every claim in `derivation_note.md`
  and `refutation_claims.yaml`. All are universally quantified over `N`; there is
  no `p`, no curve coefficient, no `N`, no `k`, no field size, no timing, no
  count anywhere. The artifacts are **tier-free**, not toy — and the Coordinator
  says exactly that. Zero runs of `EXP-ENDO-001` exist, confirmed against Git.
- **No hypothesis moved, and none should.** `ledger/hypotheses/` is not among
  the five committed paths of `457d2209`. `H-ENDO-001` stays `approved` (which
  carries no evidential standing), `H-STR-002` and `H-IC-001` stay `weakened`.
  An adverse transition of `H-ENDO-001` is defensible only after the narrowed P2
  clause is committed and `TASK-20260728-012` reports, and even then it should
  be scoped to prediction 2 on the frozen eigenvalue source, not to the
  hypothesis.
- **Nothing is target-class**, under rule A1 as governing (the document is
  ABSENT at this commit, present on `origin/main`; not cited as present). The
  largest positive quantity in the lane is `√6 ≈ 2.449`. The withdrawn algorithm
  is Pareto-dominated by BSGS by about `2^r` in both time and memory at every
  rank including `r = 1`.
- **No closure, no quorum, no impossibility claim, no promotion-gate progress,
  no claim that the ledger validates.** All four gates remain open. The
  disposition asserts none of these and neither do I.
- **Process note (not load-bearing).** The branch is 312 commits behind
  `origin/main` and 24 ahead. Every "AGENTS.md at this commit has no rule 13"
  disclaimer is true *of a stale contract*: `origin/main` carries the goal
  closure quorum and rule 13, and `docs/target-result-profile.md` exists there.
  Nothing here turns on the difference — nothing closes, so no quorum applies
  under either version — but `CLAUDE.md` requires keeping a branch current by
  **merging** main in, and the next batch should do that before freezing
  anything.

---

## Part 7 — What BATCH-010 should open on

**Agree with `EXP-STR-004` (`DEFER-BATCH009-001`), with three corrections and
one addition.** The recommendation is right; two of its three stated reasons are
not.

**Correction 1 — change the stated reason.** Target-class cannot be the
criterion, because `DEFER-BATCH009-001` itself records that `EXP-STR-004` is not
target-class and cannot move an exponent in either direction (§1.7). The two
criteria that *do* select it, and they are sufficient, are: (i) it discharges a
**mandatory** replication obligation that `DEFER-BATCH009-001` makes binding on
the next transition of `H-STR-002` in either direction; and (ii) **its failure
mode is measurement rather than design**. Say that plainly, so no reader
concludes target-class ambition selected it.

**Correction 2 — drop the backwards budget argument** (§1.6). Withdrawal freed
7200 executor seconds. The honest constraints are that BATCH-009's design,
freeze and review cards are consumed, that a fresh cycle is a batch's work, and
that `campaign_budget.maximum_batches = 9` is consumed so a tenth batch requires
explicit user authorisation the Coordinator may not self-grant.

**Correction 3 — restate `DEFER-BATCH009-002`'s resume condition** against
relation-freeness rather than against the two-point cap, which is false (S1).

**Addition — pre-register an execution gate (`RC-9`).** "The next batch must
execute" is an intention, and BATCH-006 shows what happens to intentions on this
route. Make it checkable: BATCH-010 may not close without at least one committed
run record carrying a manifest; a `REVISE` on its contract permits **at most one**
amendment cycle, after which the batch either executes the reduced-scope core or
records the non-execution as a **batch failure**, never as a result. Pair it with
`RC-7` (baseline position stated in the contract before freezing) and `RC-8`
(determined-vs-sampled labels), both of which are free riders on the
criterion-feasibility table `DEFER-BATCH009-003` already requires.

**One dissent worth recording.** `EXP-STR-004`'s arm E′ carries a sharp
prediction — `α = 0` at every instance with `B mod 3 == 0` — which is
determined-quantity-shaped and, by the Coordinator's own selection-bias theory,
is at risk of being pre-empted at review. Its arms A′ and E′ nonetheless produce
`α` counts across *drawn* instances, which are sampled. That mix is exactly
right for the diagnostic in §4: if a contract whose decisive quantities are
sampled *still* fails to execute, the selection-bias story is falsified on its
own terms and the harness diagnosis takes over. **BATCH-010 should be opened
with that stated as a second, declared purpose**, so the campaign learns
something about itself whichever way the measurement goes.

---

## Bottom line

- The **withdrawal ruling survives** — on `G6` and `G3`, both reviewer-originated
  and each sufficient alone. It does **not** survive on `G7`, `G5`, or the
  roadmap claim, and those are the arguments it leads with.
- The **two-point argument does not hold**: `G7`'s premise is false (Z-rank is
  the wrong invariant; genuine `r = 3` and `r = 4` cells exist), while its
  conclusion holds for a different reason (any such cell is a Z-linear
  reparametrisation of the `r ≤ 2` lattice).
- `INT-BATCH009-S` is **honest in count, optimistic in diagnosis**; the
  discriminating counter-evidence is already in the campaign's record
  (BATCH-007, `OBS-1` falsified by execution), and BATCH-010 can decide the
  question for free.
- **D3 is not load-bearing** for the withdrawal, is load-bearing only for the one
  claim that fails anyway, and its conclusion clause is false as written and must
  not enter `EV-ENDO-001`.
- Nothing here is a research result at any tier, no hypothesis moved or should,
  and nothing is target-class.
- **BATCH-010 should open on `EXP-STR-004`**, for the right reasons, behind a
  pre-registered execution gate.

*One next concrete action:* run `RC-6` — one SVP in the rank-3 relation lattice
`R₃`, for the frozen J0 triple and for one alternative curve-backed triple
`λ₃ = a + b·λ₂` — inside `TASK-20260728-012`'s `instantiation.json`, and use the
result to restate `G7` and narrow the P2 clause to the frozen eigenvalue source
before `DEC-20260728-004` is written. Seconds of integer arithmetic, already
inside that card's scope and budget.

---

**Probe disclosure — NOT EVIDENCE.** One scratch script, run **outside** the
repository, integer arithmetic only, no curve arithmetic, no repository file
read or written by it:
`/private/tmp/claude-501/-Volumes-Volume-crypto-autoresearcher/455e8ba4-931b-40ce-8b54-c2895583be26/scratchpad/rt013_probe.py`.
It re-checks Vieta at `N = 65521` and `N = 1048573`, confirms the frozen triple
admits a relation of norm 1, and finds no relation of norm `≤ X` for twelve of
twelve alternative triples `λ₃ = a + b·λ₂`. It is **unarchived and is not
evidence**, and **no conclusion in this report rests on it**: §1.4's argument is
the determinant-`N` count for `R₃` in dimension 3 against `X = N^{1/6}`, which is
paper arithmetic, and D2's core is Vieta. It is disclosed *because* this campaign
has already had one adjudication (BATCH-007 `OBS-1`) rest on an unarchived probe
and then fail to reproduce under execution.

**Handoff.** This report is working-tree-only and is not a durable research
artifact until the Coordinator's ledger archive task commits it and the
post-commit verifier accepts the receipt. No commit was made by this session; no
status was changed; no evidence, decision or knowledge record was created;
nothing under review was edited; and no file outside the assigned `write_scope`
was created or modified.
