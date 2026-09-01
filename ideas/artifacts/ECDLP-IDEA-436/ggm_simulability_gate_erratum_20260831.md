# ECDLP-IDEA-436 — Erratum and re-founding of the GGM-simulability gate memo

- **This artifact supersedes, by reference and never by edit:**
  `ideas/artifacts/ECDLP-IDEA-436/ggm_simulability_gate.md`, as archived at snapshot
  commit `eeffdeb411bbd0b8d327d5799b2c3ed872cbcedb`
  (`sha256 f29841c820c792484d9ab026c062a0df022186316d2aa71225f3df61bc6c4480`, as
  recorded and independently recomputed in the red-team report
  `TASK-20260831-62019a`, `subject_verification.hashes_verified`), together with its two
  companion artifacts at the same commit:
  `coordination/goals/GOAL-ECDLP-001/proposals/B71-IDEA436-GGM-SIMULABILITY-GATE-20260831-c7c3ef/tasks/TASK-20260831-c7c3ef/proof-search-map.yaml`
  (`sha256 598c66a880b584eab63bf175f8ef666d6bfe3864b612f256b17b479d7ff8899a`) and
  `.../source-novelty-audit.yaml`
  (`sha256 564130f26407a70a633d9cb90dd1c33b6ea0b57a09203018fcc2bba4afb8f9c9`).
  **Those three files are byte-unchanged by this task.** They remain the archived
  record of what was said; this erratum is the operative statement where the two
  differ, and every point of difference is enumerated below by repair ID.
- Task: `TASK-20260831-0e7ce6` (goal `GOAL-ECDLP-001`, proposal namespace
  `B71-IDEA436-GATE-ERRATUM-20260831-0e7ce6`). Role: idea-generator.
  Requested policy `research-deep`, reasoning effort `high`.
- Commissioned by: `DEC-20260831-a9716f`, `next_actions[0]`, whose
  `repairs_required_before_any_disposition_is_recorded` block is this erratum's
  binding specification.
- **Runs: 0. Experiments: 0. Implementations: 0. No code was written or executed. No
  `p`-adic arithmetic was implemented, evaluated, or timed. No timing of any kind was
  performed.** `experiment_maximum_runs: 0` is a methodological scope gate on this task
  and was not relaxed.
- Evidence tier: **derivation, zero-run, single-session.** Nothing here is an
  experimental result, an attack, a speedup, a novelty claim, a closure, or a status
  change. Status changes are the Coordinator's authority alone, and none is made or
  implied.

---

## §A. What this erratum does and does not do

**Does.** It applies the six blocking repairs `R-F1`, `R-OBJ1`, `R-OBJ2`, `R-OBJ6`,
`R-OBJ7`, `R-OBJ8` of `DEC-20260831-a9716f`; folds in the nine lower-severity items
that decision lists; re-runs `Control A` half 2 against the repaired statement of the
move `M2` and reports the outcome, including two consequences that run *against* the
superseded memo's own controls; and re-issues the §0 verdict as a **two-part
recommended disposition** founded on the **model-free** ground of Corollary 4.3, with
the strict-GGM simulator, Shoup, and the phrase *closed at exponent 1/2* demoted to
**corroboration**.

**Does not.**

1. It does **not** edit the superseded memo, its `proof-search-map.yaml`, or its
   `source-novelty-audit.yaml`. Those bytes are hash-bound in a committed archive
   receipt (AGENTS.md rules 4 and 15) and changing one byte would break that archive
   permanently.
2. It does **not** edit `ideas/ECDLP-IDEA-436_local_torsion_coordinate_valuation_profile_hypothesis.md`.
   That record is frozen; its `State` remains `proposed_unapproved_pending_review`, and
   any change to it is a separate, later Coordinator action.
3. It does **not** edit, correct, retier, supersede, or contradict `KN-FIND-002` or
   `KN-FIND-b7e091`. The three recorded defects against them (`CC-1`, `CC-2`, `CC-3` on
   `EV-ECDLP-048824`, plus the validator's `F-5`) are **routed** by
   `DEC-20260831-a9716f` `routed_separately_not_this_lane` / `Q-2` to their own
   `review-breakthrough`, `max`, `degradable: false` round, which has **not been
   opened**. This erratum cites that routing and acts on none of it. Where a repair
   below would otherwise touch one of those records, it is confined to correcting
   **this lane's own reproduction** of the record and says so.
4. It creates no `B71`, `BATCH`, `IDEA`, `EV`, `DEC`, `CORR`, experiment, or
   implementation record, mints no identifier, and changes no status of anything.
5. It claims no attack, speedup, novelty, closure, hardness result, breakthrough,
   universal impossibility, or cryptographic-scale transfer, **in any direction**. The
   re-founding of §0 is a re-founding: it is not a retraction of the superseded memo's
   result and it is not an upgrade of it. See §H.

---

## §B. RE-ISSUED §0 VERDICT — TWO-PART DISPOSITION (repair `R-OBJ8`)

The superseded memo returned a single verdict label, `scoped_rejection_simulable`, and
a single recommendation, *scoped rejection of ECDLP-IDEA-436 as written*. Both are
**withdrawn and replaced** by the two-part disposition below.

The reason is structural, not stylistic. `ECDLP-IDEA-436`'s hypothesis **H** is a
**disjunction**. Verbatim from the frozen record:

> **H:** there is a coordinate/valuation functional on `<Ŝ>` — concretely a member of the
> frozen family [...] **or** a fixed statistic of the precision-`r` coordinate digits of
> `[k]Ŝ` — that is non-constant in `k`, **efficiently invertible**, and whose evaluation
> precision `r` grows slowly enough that recovering `x` from `Q = [x]P` costs less than
> `n^{1/2}` end-to-end, including all precision and query costs.

Only the first disjunct (**D1**) was gated. Closing one disjunct of a disjunctive
hypothesis does not close the hypothesis.

### Part 1 — D1: DISPOSED IN SCOPE

**Recommended disposition label (a recommendation to the Coordinator, not a status
change):** `d1_scoped_rejection_zero_leverage_model_free`.

**The ground is model-free.** Under the repaired frozen setting of §C.1 (`R-F1`) and for
`j, k ≢ 0 mod n`, the D1 functional is *identically* the indicator of the fibre
`k ≡ ±j (mod n)`; equivalently, it is **equality in the quotient `⟨S⟩/{±1}`**
(Corollary 4.3 of the superseded memo, which this erratum promotes to the load-bearing
step). That quotient is available for free in `E(F_p)`: it is decided by **one `F_p`
`x`-coordinate comparison** between two points the querying party must already hold to
pose the query. Therefore, for **any** adversary — generic or non-generic, coordinate-
holding or not, at any scale — the D1 oracle supplies

- **zero information**: its output is a deterministic function of data the querying
  party already possesses or can compute from what it possesses, so its conditional
  entropy given that party's view is exactly 0; and
- **no computational leverage beyond the `⟨S⟩/{±1}` quotient that Pollard rho's
  negation map already exploits** (`KN-TECH-006`, `internal`, verbatim: *"Negation and
  other cheap automorphisms give a further constant-factor speedup."*).

This argument uses no oracle model, no Fork-A branch, no Shoup theorem, and no primality
hypothesis. It is stated precisely as **Proposition E** in §C.2, together with the exact
cost qualification that the phrase "literally nothing" (used in the red team's `OBJ-1`
body) does **not** support and this erratum therefore does not use.

That, and `ECDLP-IDEA-436`'s own contractual gate — verbatim: *"**The GGM-simulability
check is a gate, not a step**: if the functional family is simulable, this record is
rejected without running anything"* — is what carries the D1 disposition.

**Corroboration, demoted (see `R-OBJ1`, `R-OBJ2`, `R-OBJ6`, `R-OBJ7`).** Separately and
**more weakly**, D1 is simulable in the strict Shoup GGM with one group inversion and
two equality tests **on a handle interface**, and by this program's `KN-TECH-005`
convention that is recorded as *closed at exponent 1/2* **in the largest prime factor of
`n`** (equivalently, at exponent 1/2 in `n` when `n` is prime). That corroboration is
carried subject to `KN-TECH-005`'s own applicability limit, quoted forward **verbatim**
as `R-OBJ1` requires:

> The bound is a barrier, NOT a proof that no non-generic attack exists (KN-OPEN-001).

and

> The bound is about the generic model; it says nothing about attacks exploiting
> concrete structure (isogenies, pairings on low-embedding-degree curves, anomalous
> curves with #E = p, summation-polynomial index calculus over extension fields). Those
> live precisely in the model's blind spot.

and subject to `KN-LIT-7606`, quoted **verbatim**:

> A plain-GGM simulability argument cannot close a candidate for real elliptic curves:
> index calculus over small-degree extension fields (KN-LIT-022, KN-LIT-002/003) is a
> genuine non-generic algorithm, which is precisely why this model exists.

— with that record's own disclosure carried too: *"Full text was not read; the fetched
PDF did not yield extractable text. Claims above come from search-result summaries and
the abstract."*

**Scope of Part 1** (this is boundary `B-1` of `EV-ECDLP-048824` as repaired here):
`E/F_p` with good reduction; `S ∈ E(F_p)` of order `n` with `gcd(n, p) = 1`; a
**Weierstrass model over `Z_p` realising the good reduction, `v_p(Δ) = 0`** (`R-F1`);
the canonical order-`n` prime-to-`p` lift; D1 exactly as written. For the *corroboration*
only, additionally `n` prime, or the exponent restated in the largest prime factor of `n`
(`R-OBJ2`). **Explicitly outside scope, and carried up into this §0 as `OBJ-13` and
`F-4` require:** bad or additive reduction; a non-minimal integral model; a
non-Weierstrass model; a functional on the formal group `Ê(pZ_p)`; and **any point whose
order is divisible by `p`, which includes every generator of an anomalous curve
`#E(F_p) = p`** — so this erratum says nothing whatever about the Smart / Satoh–Araki /
Semaev additive transfer (`KN-TECH-033`), and must not be read as saying anything
about it.

### Part 2 — D2: NOT GATED, RETURNED TO THE RECORD

**Recommended disposition label:** `d2_not_gated_returned_open_with_subquestion`.

D2 — *a fixed statistic `T` of the precision-`r` coordinate digits of a **single** lifted
point `[k]Ŝ`* — **does not collapse**. Proposition 4 is specific to a *difference of two
`x`-coordinates* and says nothing about a single point's digits. D2 was assessed in the
superseded memo only at the weaker **relative** tier ("no advantage over an adversary
that already holds `F_p` coordinates"), on the strength of the move `M1`, and `M1` is the
move the anomalous-curve control **broke**. D2 is therefore **not gated**, is **not
disposed**, and is returned to `ECDLP-IDEA-436` open, with the §10 item 2 sub-question
attached:

> Is there a statistic `T` and a precision schedule `r(n)` such that `T(σ(·))` is a
> nonconstant *homomorphism-like* map `⟨S⟩ → (small target)`?

and with the bar `KN-TECH-033` sets for any answer — verbatim: *"representations win
exactly when the curve supplies a global structural coincidence,"* and *"a proposal must
name its coincidence"* — carried **with that record's own self-label**, which the
superseded memo dropped: `KN-TECH-033` states that *"The representation-attack reading in
the second section is this program's own interpretation and is a framing, not a result."*
A D2 proposal that cannot name its coincidence for an **ordinary** curve is not ready for
a gate; that is a bar, not a closure.

### Part 3 — consequence for the record as a whole

Because H is `D1 ∨ D2` and only D1 is disposed, **this erratum does not recommend a
scoped rejection of `ECDLP-IDEA-436` as a record**, and the superseded memo's
recommendation to that effect is withdrawn. What the Coordinator may consider on this
erratum is a disposition of **disjunct D1 in the scope above**, with D2 explicitly
outstanding. `KN-OPEN-3417fc` is **not** closed, resolved, or narrowed: it quantifies
over *any* computable non-group-theoretic coordinate or valuation invariant, and its own
negative-resolution criterion is a **measurement at toy `p` that has not been run**
(`RC-1`, queued as `Q-1` of `DEC-20260831-a9716f`, not dispatched by this task).

---

## §C. The six blocking repairs

### §C.1 `R-F1` — the model hypothesis, and the false universal sentence

**What the superseded memo said (§1.1, verbatim):** *"`E/Q_p` the good-reduction lift
with a Weierstrass model whose coefficients lie in `Z_p`."* And (Proposition, verbatim):
*"There is **no** `j, k, E, p, n` for which the valuation takes a finite value `≥ 1`."*

**The defect (validator `F-1`, `internal`, opened in full).** Coefficients in `Z_p` is
strictly weaker than a model **realising** the good reduction. An elliptic curve with
good reduction has many integral Weierstrass models; on a non-minimal one, the sentence
the memo's Lemma 1 proof relies on — *"A point of `E(Q_p)` outside the kernel of
reduction has non-negative valuation coordinates on an integral model and reduces
coordinatewise to its image in `E(F_p)`"* — is **false**: coordinatewise reduction lands
on the singular point of a singular plane cubic.

**The explicit counterexample.** Let `E : y² = x³ + Ax + B` over `Z_p` with `v_p(Δ) = 0`,
so `E` has good reduction, and let `S, n, Ŝ` be as in §1.1. Apply the admissible
substitution `x = u²X`, `y = u³Y` with `u = 1/p`. The result

```
E' :  Y² = X³ + p⁴ A X + p⁶ B
```

is a Weierstrass model of the **same** curve whose coefficients lie in `Z_p`, so it
satisfies §1.1 as literally written; its discriminant is `p¹²` times that of `E`. On this
model `X = p² x`, so for every `j, k` with `k ≢ ±j mod n`,

```
v_p( X([k]Ŝ) − X([j]Ŝ) )  =  2 + 0  =  2,
```

which is **finite and `≥ 1`** while `[k]Ŝ ≠ ±[j]Ŝ`. The Proposition's literal universal
sentence is therefore **false as stated**, and this is a `FAIL` on the
quantifier-fidelity proof-architecture check. It bites because the **model** is not in
the Proposition's quantifier list `(j, k, E, p, n)` and is not in the
`proof-search-map`'s `quantifier_order.claim_d1` either.

**The repair, applied.**

1. **§1.1 is amended to read:** `E/Q_p` the good-reduction lift with a **Weierstrass
   model over `Z_p` realising the good reduction, that is with `v_p(discriminant) = 0`**
   (equivalently a minimal model, up to a unit `u`).
2. **The §10 exclusion list gains `model non-minimality`.** As repaired, that list reads:
   bad or additive reduction; `p = 2` (inherited — see §D.7); a non-Weierstrass model
   whose distinguished coordinate does not have `±` fibres; a point whose order is
   divisible by `p`; a functional on the formal group `Ê(pZ_p)`; **and a non-minimal
   integral Weierstrass model**.
3. **The quantifier list gains the model.** The Proposition, as repaired, quantifies over
   `(j, k, E, p, n, model)` with the model constrained by (1). With (1) in force,
   Proposition 4 is **true exactly as written**, and the uniform-witness quantifier order
   stands.
4. **The `proof-search-map`'s `dependency_audit` sentence is corrected.** That document
   asserts, verbatim: *"Checked for a hidden dependence of the D1 witness on the
   instance: none found. Sim code is three lines and mentions no curve parameter."* On
   the loose hypothesis this is **wrong**: `Sim` line 4 returns the literal constant `0`,
   and `0` is a model-dependent constant — on `E'` the correct return value is `2`, or
   `min(2, r)` after truncation. Under the repaired §1.1 the audit becomes correct,
   because the model is now pinned by hypothesis rather than left free.

**What survives, and why the erratum's re-founded ground is robust to this.** Under any
admissible model change `x = u²X + s`, the difference scales by `u^(−2)` and the
**partition** of index pairs into the two branches is exactly preserved. So D1 remains
two-valued, remains constant in `k` off the `±` locus, and its separating predicate
remains the group-theoretic `k ≡ ±j mod n`. On a model with `c = −2 v_p(u) > 0` the
correct values are `min(c, r)` off the locus and `r` on it — and when `r ≤ c` these
coincide, so the functional becomes **constant**, image size `2` becomes `1`, and
Corollary 4.2's 1 bit becomes 0 bits. Every secondary consequence moves strictly toward
**more** degeneracy, never less. Consequently **Proposition E of §C.2 holds on every
admissible integral model**, with the single `F_p` comparison joined by the public model
constant `c`; the re-founded ground of §B is not merely repaired by `R-F1` but is
independent of which admissible model is chosen. That is recorded here as a strengthening
that follows from the validator's finding, not as a claim beyond it.

**Alternative considered and declined.** The validator's `R2` — keep the loose hypothesis
and state the result covariantly, with `c` a public model constant entering `Sim` as an
input and the quantifier list gaining *for all integral Weierstrass models* — is strictly
more work and buys nothing, since the good-reduction model is the natural one. `R1` is
adopted, as the validator recommends, and `R2`'s content is preserved as the robustness
observation in the preceding paragraph.

### §C.2 `R-OBJ1` (major) — re-founding §0 on the model-free ground

**The defect.** The superseded memo grounded its §0 verdict on strict-GGM `O(1)`
simulability plus Shoup. That chain certifies strictly less than the verdict claimed, by
three sources this lane has opened:

- the producer's own `proof-search-map` `method_ceiling`, verbatim: the method *"can
  certify NOTHING about (a) any oracle whose output is not so determined, (b) ECDLP
  hardness itself, (c) any non-generic attack, or (d) the real cost of any algorithm on a
  real curve. In particular it can never certify a lower bound in the structured GGM,
  because Shoup theorem does not hold there"*;
- `KN-LIT-7606`, quoted **by the superseded memo itself** in its §6.4: *"A plain-GGM
  simulability argument cannot close a candidate for real elliptic curves"* — and *plain*
  GGM is the strict branch, which is exactly the branch the D1 closure lived in;
- `KN-TECH-005`, verbatim: *"The bound is a barrier, NOT a proof that no non-generic
  attack exists."*

`ECDLP-IDEA-436` is a proposal about attacking **real** ECDLP. A certification that says
nothing about the real cost of any algorithm on a real curve cannot, on its own, ground
its rejection. The superseded memo applied `KN-LIT-7606`'s scoping discipline to D2 (via
`M1`, structured branch) and **not** to D1 (via `M2`, strict branch), even though
`KN-LIT-7606`'s sentence is about the plain — strict — model.

**The re-founding.** State the load-bearing step model-free. Terminology first, because
this lane now carries two different things called a "model": *Weierstrass model* (a
choice of equation, the subject of `R-F1`) and *generic-group model* (a choice of oracle
interface, Fork A). **"Model-free" below means free of the generic-group model.** The
statement is Weierstrass-model-dependent, and §C.1 has just pinned that dependence and
shown the conclusion survives every admissible choice.

> **Proposition E (zero information, no leverage beyond the free quotient).** Under the
> repaired frozen setting of §C.1, for all `j, k ≢ 0 mod n` and all `r ≥ 1`:
>
> ```
> inv_{j,r}(k) = r   if x([k]S) = x([j]S) in F_p,
>              = 0   otherwise,
> ```
>
> where `x([k]S)`, `x([j]S)` are the `F_p` coordinates of the **reduced** points. Hence
> `inv_{j,r}` is computed from the `F_p` coordinates of `[k]S` and `[j]S` by a **single
> `F_p` equality test** — no lifting, no `p`-adic arithmetic, no precision, no group
> operation beyond possessing the two points.

*Derivation.* Immediate from the superseded memo's Lemma 1 (which puts
`x([k]Ŝ) ∈ Z_p` with `x([k]Ŝ) mod p = x([k]S)`), its Lemma 2 as repaired by `F-3`
(§D.9), and its Proposition 4 as repaired by `R-F1`. Off the `±` locus the two lifted
`x`-coordinates have distinct residues, so the valuation is 0; on the locus they are
equal **exactly** in `Q_p`, so the truncated value is the cap `r`. The `F_p` test
`x([k]S) = x([j]S)` decides `k ≡ ±j mod n` by Lemma 2's first clause. ∎ (Derivation
tier, zero runs; it is a re-reading of a derivation the validator independently
blind-re-derived under `TASK-20260831-c6ceb9`, not a new theorem.)

**Consequences, stated with their exact cost qualification.**

- **Information: exactly zero.** The oracle's answer is a deterministic function of the
  `F_p` coordinates of two points the querying party holds or can compute from what it
  holds. Its conditional entropy given that party's view is 0. This is the computational
  reading of `KN-TECH-73630e`'s standing boundary, verbatim: *"The lift is
  information-theoretically empty: `Ŝ` is a deterministic function of `S`, computable to
  any precision from `E(F_p)` data alone by Hensel lifting plus the order condition.
  Nothing is learned that was not already available."*
- **Leverage: none beyond the free `⟨S⟩/{±1}` quotient.** If the party already holds the
  two points — the handle interface, or a rho walk state — the direct computation is
  **one `F_p` comparison**, which is no more than the cost of formulating and issuing the
  query. If it holds only the integers `j, k`, it materialises `[j]S` and `[k]S` in
  `O(log n)` group operations each by double-and-add and then does the one comparison; so
  the oracle saves at most **two scalar multiplications per query**, `O(log n)` group
  operations, and nothing else. **This erratum therefore does not use the unqualified
  phrase "literally nothing"** that appears in the red team's `OBJ-1` body: on the
  integer interface that phrase is imprecise, and the qualified form — *no leverage
  beyond the `⟨S⟩/{±1}` quotient, at a saving of at most `O(log n)` group operations per
  query* — is the operative one. It is still decisive, because `O(log n) ≪ n^{1/2}`.
- **No sub-birthday advantage, by the memo's own bookkeeping.** By Corollary 4.2 each
  query returns at most **1 bit**, and against a fixed reference `j` and uniformly random
  `k` that bit is 1 with probability `2/n`. The optimal use of a `±`-fibre indicator
  against adaptively chosen references **is** an `x`-line collision search — that is,
  Pollard rho, which already has the same quotient for free.

**Why this is stronger than what it replaces, and independent of Fork A.** Proposition E
needs no oracle model, so it is untouched by `OFQ-1` (which branch of the GGM this
program treats as canonical — left open by the superseded memo and left open here); it
needs no primality hypothesis (`R-OBJ2` applies only to the corroboration); it is
indifferent to the query interface (`R-OBJ7`); and it applies to **non-generic**
adversaries, which a GGM argument by construction cannot reach. Those four
independences are the entire content of the re-founding.

**What is demoted, and to what.** The strict-GGM simulator (§5.1 of the superseded memo),
Shoup / `KN-TECH-005`, and the phrase *closed at exponent 1/2* are **corroboration**:
a second, weaker, model-bound route to a conclusion that Proposition E already carries,
useful because it places D1 in the same taxonomy the corpus uses for other augmented
oracles. They carry `KN-TECH-005`'s barrier caveat verbatim (quoted in §B) wherever they
appear. **This is a re-founding, not a retraction and not an upgrade:** the disposition of
D1 is the same disposition the superseded memo reached, reached on a ground that
survives the objection to the ground it used, and nothing broader is asserted than the
superseded memo asserted.

### §C.3 `R-OBJ2` (major) — `n` prime, or the exponent in the largest prime factor

**The defect.** `KN-TECH-005` states its bound, verbatim in its frontmatter `complexity`
field: *"Omega(sqrt(p)) group operations for any generic DLP algorithm (p = largest prime
factor of the group order)"*. The superseded memo's §1.1 and §10 scope block state only
`gcd(n, p) = 1`, never that `n` is prime, while its `proof-search-map` quantifies over
all `n` with `gcd(n,p) = 1` and its `method_ceiling` concludes *"cannot bring any
algorithm below Omega(sqrt(n)) group operations"*. For **composite** `n` that is false:
Pohlig–Hellman reduces a generic DLP to the largest prime factor. `KN-TECH-030`,
`internal`, opened, states it verbatim: *"The cost is dominated by sqrt(p_max) where
p_max is the largest prime factor of n. Consequently the *only* quantity that determines
ECDLP difficulty in the generic model is the size of the largest prime-order subgroup,
not the size of the field or of the full group."* `KN-FIND-b7e091`, whose argument style
the memo extends, **does** carry the hypothesis — verbatim: *"For prime-order prime-field
elliptic curves"* — and the memo dropped it while widening the quantifier.

**The repair, applied — both halves, since the decision permits either.**

1. **Scope block.** `n prime` is added to the scope of the **corroboration** (§B, "Scope
   of Part 1"). Under `n` prime, largest-prime-factor(`n`) `= n` and the corroboration
   reads at exponent 1/2 in `n`.
2. **General restatement.** For general `n` with `gcd(n, p) = 1`, the corroboration is
   restated as: **exponent 1/2 in the largest prime factor of `n`**. `Ω(√n)` is withdrawn
   for composite `n` and is not asserted anywhere in this erratum.

**What is unaffected.** Proposition 4, Proposition E, the two lemmas, the simulator, and
the entire §B Part 1 ground. Primality was never needed by any of them; it is needed only
by the imported exponent. This is a further reason the re-founding leads with the
model-free ground: `R-OBJ2` cannot reach it.

**Which curves this leaves in the corroboration's scope.** Cryptographic prime-field
curves are designed with `n` prime (`KN-TECH-030`, verbatim: *"It gives no advantage when
n is prime — which is the designed case for every cryptographic curve, and the case this
program targets"*), so the added hypothesis is not restrictive in the target regime. It
**is** restrictive at toy scale, where accidental smoothness is common, and any successor
run must record the factored order.

### §C.4 `R-OBJ6` (major) — constructive `M2` with its `O(1)` cost bound, and the `Control A` half-2 re-run

**The defect.** `M2` was stated, verbatim: *"If that deterministic function further
factors through group-theoretic predicates (equality, inversion, group law), the
simulation lifts from A-structured to A-strict."* It carries **no cost bound**. On its
natural unbounded reading it proves too much exactly as `M1` does: on an anomalous curve
`ψ`, the additive transfer, **is** a group isomorphism onto `(F_p, +)`, so `ψ(P)` is
determined by `P` as a group element and does factor through group structure — unboundedly,
since `ψ(P) = k·ψ(G)` where `P = [k]G` and `k` is pinned down by equality tests. The
superseded memo blocked that firing only by invoking Shoup, i.e. by the absurdity of the
conclusion. Using one criterion for D1 (an exhibited three-line simulator) and a different
one for `ψ` (absurdity of the conclusion) inside a single control is precisely the failure
a proves-too-much control exists to catch.

**The repaired statement, adopted.**

> **M2 (constructive, cost-bounded).** `M2` **fires** on an augmented oracle `O` **if and
> only if** there is an **EXPLICIT simulator** answering each query to `O` using
> `O(1)` group operations, inversions and equality tests **on handles**, and no other
> access — no coordinate access, no field arithmetic, no local bit-work whose cost grows
> with the instance.

Firing is now a **burden of construction**, discharged only by exhibiting the simulator.
It is no longer an information-theoretic determination criterion.

#### `Control A` half 2 — RE-RUN against the repaired statement

**Object.** `ψ`, the Smart / Satoh–Araki / Semaev additive transfer on an anomalous curve
`#E(F_p) = p`, where the conclusion *"ECDLP needs `Ω(√p)` group operations"* is **known
false**: `KN-TECH-033`, `internal`, opened, verbatim — *"there is an explicit isomorphism
from that group onto the additive group (F_p, +)"* and *"the ECDLP is linear time"*, at
*"O(log p) field operations"*.

**Question.** Does the repaired constructive `M2` fire on `ψ`?

**Outcome — `M2` DOES NOT FIRE. The control PASSES. The exponent-1/2 corroboration is
not broken by this control.** Recorded at two levels, because they have different
strengths and the difference is the whole point of the repair.

- **Level 1 — mechanism check, unconditional, and this is the operative one.** The
  repaired `M2`'s firing condition is the **exhibition** of an explicit simulator
  answering each `ψ`-query in `O(1)` group operations, inversions and equality tests on
  handles. **No such simulator is exhibited for `ψ`**, and the repaired criterion supplies
  no other route to firing. The antecedent of the rule is simply not discharged, so the
  implication chain *(M2 fires) ⇒ (adversary is generic with `O(1)` overhead) ⇒ (Shoup
  applies)* never starts on `ψ`, and the false conclusion is never reached. **This is the
  mechanism check the original statement lacked**, and — unlike the superseded memo's
  reason — it invokes no theorem whose applicability `M2` is supposed to license.
- **Level 2 — non-existence, conditional, and labelled as a consistency check.** The
  stronger statement *no such simulator **can** exist* does hold, but it needs a lower
  bound: composing a hypothetical `O(1)`-group-operation `ψ`-simulator with one field
  division would give a generic DLP algorithm using `O(1)` group operations in a group of
  prime order `p`, contradicting `KN-TECH-005`. **This invokes the same theorem `M2`
  licenses the use of.** It is therefore a *consistency* check, not an independent
  mechanism check, and this erratum labels it as such rather than presenting it as the
  repair. Its logical status is benign but must be stated: conditional on `KN-TECH-005`,
  `M2` is a sound rule; the D1 corroboration is conditional on `KN-TECH-005` too; the two
  conditionals share a hypothesis, and if that hypothesis failed, both would fall
  together and the misfire question would be moot. Shared hypothesis is not circularity —
  but the *negative* direction of the repaired `M2` remains not independently checkable,
  which is a residual weakness inherited in weaker form from the statement it replaces,
  and it is recorded here rather than smoothed over.

**Explicitly, as the task card requires:** the repaired constructive `M2` does **not**
fire on anomalous curves. The exponent-1/2 corroboration is **not** broken by this
control.

**But the repair changes two other things, and both run against the superseded memo.**
These were not asked for and are reported because they are consequences of the repaired
statement.

1. **The repaired `M2` does not fire on D1 under the integer interface.** D1's exhibited
   simulator is `O(1)` on **handles**. On an integer-indexed interface it must first
   materialise handles at `O(log n)` group operations (see `R-OBJ7`), which is not `O(1)`.
   Taken literally, the repaired `M2` therefore fires on D1 **only on the handle branch**.
   The corroboration **narrows** accordingly, and §B states it that way. It does not
   vanish: on the integer branch D1 lands in `KN-FIND-002`'s non-constant-overhead tier,
   whose own wording is *"Not closed at 1/2 by the constant-overhead bound, but
   O(log N) << sqrt(N), so no sub-birthday advantage."* The model-free ground of §C.2 is
   indifferent to the interface and is unaffected.
2. **The repaired `M2` does not fire on the endomorphism oracle either, so the superseded
   memo's §6.2 `M2` check-mark is withdrawn.** See §D.1 and §E.

#### Ancillary: the `RC-2` control the red team asked for is exactly this re-run

`RC-2` of `TASK-20260831-62019a` is, verbatim: *"Re-run Control A half 2 against the
repaired, cost-bounded statement of M2 (OBJ-6). Zero compute."* It is discharged above.
The reviewer recorded *"I expect it to pass"*; it passed, and the two ancillary
consequences above are recorded as new findings of the re-run, not as part of the
expectation.

### §C.5 `R-OBJ7` (medium) — Fork D, the query interface, answered on both branches

**The defect.** The `O(1)` figure presupposes a **handle** interface. §5.1 of the
superseded memo takes `A` and `B` as handles; §2.2 declares that reading only in passing,
under Fork B's `B-reduction` branch. But `ECDLP-IDEA-436` writes the frozen family as
`inv_{j,r}(k)`, **indexed by integers**. The memo never states which interface the gate
runs on, and the two give two different recorded tiers.

**The repair: an explicit FOURTH FORK, answered on both branches.**

> **Fork D — how is the oracle queried?**
>
> - **D-handle.** The adversary presents handles `A` (for `[k]Ŝ` or equivalently `[k]S`)
>   and `B` (for `[j]Ŝ`), and the oracle returns `inv_{j,r}(k)`.
> - **D-integer.** The adversary presents the integers `j, k` (and `r`), as the frozen
>   family is literally written, and the oracle returns `inv_{j,r}(k)`.

**Branch D-handle.** The simulator is the superseded memo's §5.1: one inversion `INV(B)`
and two equality tests `EQ(A,B)`, `EQ(A,B')`, plus one further equality test against the
identity handle for the degenerate `k ≡ 0 mod n` case (§5.3). Cost: **`O(1)` group
operations**, independent of `r`, `n`, `p` and of the coordinates. The repaired `M2`
fires. **Closed by the constant-overhead bound**, at exponent 1/2 in the largest prime
factor of `n` (`R-OBJ2`), subject to the `KN-TECH-005` and `KN-LIT-7606` caveats of §B.

**Branch D-integer.** The simulator must itself **materialise** handles for `[j]Ŝ` and
`[k]Ŝ` from the integers, at `O(log n)` group operations each by double-and-add. Total
per isolated query: `O(log n)` group operations. That overhead is **non-constant**, so the
repaired `M2` does **not** fire and the branch is **NOT closed by the constant-overhead
bound**. It lands in the tier `KN-FIND-002` describes in its own elliptic-net language,
quoted verbatim as `R-OBJ7` directs:

> the net value W(a,b) = a*P + b*Q is computable via group operations, but requires
> O(log a + log b) = O(log N) operations. [...] Not closed at 1/2 by the constant-overhead
> bound, but O(log N) << sqrt(N), so no sub-birthday advantage.

So on branch D-integer: **simulable with non-constant overhead `O(log n)`; not closed at
1/2 by the constant-overhead bound; still no sub-birthday advantage.**

**The profile-vector cost line, with reference-handle materialisation charged.** The
superseded memo's §5.1 says a profile vector over a reference set `J` costs *"`|J|` group
operations and `2|J|` equality tests, still `O(1)` per emitted value"* and **omits the
cost of materialising the `|J|` reference handles**. That omission runs in the
producer-favouring direction. Charged in full, on branch **D-integer**:

- **one-off setup:** materialise `|J|` reference handles, `O(|J| · log n)` group
  operations;
- **per queried `k`:** materialise the handle for `[k]Ŝ`, `O(log n)` group operations;
  then `|J|` inversions and `2|J|` equality tests, `O(|J|)` group operations, emitting
  `|J|` values;
- **per emitted value:** `O(1) + O((log n)/|J|)` — which amortises to `O(1)` once
  `|J| = Ω(log n)`, and is `O(log n)` for `|J| = O(1)`. The reference inversions
  `INV(B_j)` may themselves be hoisted into setup, a further constant-factor saving that
  does not change any exponent.

On branch **D-handle** the setup term is zero and the per-emitted-value cost is `O(1)`
outright.

**Note carried forward, as `R-OBJ7` directs.** The **model-free ground of §C.2 is
indifferent to Fork D**: Proposition E computes the same value from the `F_p` coordinates
in one comparison on either branch, and the `O(log n)` materialisation is a cost the
adversary pays with or without the oracle. That indifference is a further reason to lead
with the model-free ground, and it is why the two-part disposition of §B is unaffected by
which branch of Fork D a later reader adopts.

**Fork D is left open as a formalization question, like `OFQ-1`.** This erratum does not
adjudicate which interface is this program's canonical one; it answers on both and reports
where they differ. They differ **only** in the corroboration, never in the disposition.

### §C.6 `R-OBJ8` (scope-bearing) — the two-part disposition

Applied in full at **§B**, which is the operative re-issue. Recorded here for the audit
table: the single verdict label `scoped_rejection_simulable` and the single
recommendation *scoped rejection of `ECDLP-IDEA-436` as written* are **withdrawn**;
they are replaced by Part 1 (D1 disposed in scope, on the model-free ground, with the
repaired scope block), Part 2 (D2 **not gated**, returned to the record with the §10
item 2 sub-question and the `KN-TECH-033` bar attached), and Part 3 (no disposition of
the record as a whole, because H is a disjunction and only one disjunct was gated).

---

## §D. The nine lower-severity items

Each is addressed or explicitly declined with a reason. None is left silent.

### §D.1 `OBJ-3` and `OBJ-4` — two erratum sentences

**`OBJ-3`, the misattributed caveat. ADDRESSED.** The superseded memo's §6.4 says *"This
is also exactly the caveat `KN-FIND-002` records against itself"*, and its
`proof-search-map` `control_verdict` says the fired sub-control *"independently
re-derives the caveat KN-FIND-002 records against itself"*. **Both sentences are wrong.**
`KN-FIND-002`'s actual caveat, opened and quoted verbatim, is:

> The classification uses the **structured GGM** (curve equation is public), not the
> strictest Shoup GGM (opaque labels). Under the strictest GGM, jet and endomorphism
> would be NON-SIMULABLE because they require coordinate access.

That is a caveat about its oracles being **less** simulable in the strict model. The
caveat the §6.4 control actually establishes is a different one, arguably of opposite
polarity: that a structured-GGM simulability argument **cannot certify a lower bound at
all**, which the producer states correctly in its own `method_ceiling` — *"it can never
certify a lower bound in the structured GGM, because Shoup theorem does not hold there"*
— without drawing the consequence. **Corrected sentence, as it should have read:** *"This
is the caveat the producer's own `method_ceiling` states; it is **not** the caveat
`KN-FIND-002` records against itself, which is a different and narrower statement about
branch-dependence."*

**The consequence the producer did not draw is ROUTED, NOT ACTED ON.** The red team's
`OBJ-3` continues that, combining that method ceiling with the anomalous-curve control,
`KN-FIND-002`'s recorded *"SIMULABLE with O(1) overhead (closed at exponent 1/2 by
KN-TECH-005)"* for the jet and endomorphism oracles may not be available **in the
structured model that record declares**. `KN-FIND-002` is `status: established`,
`confidence: strong`, backed by `EV-GGM-001` and `DEC-20260726-007`. **This erratum does
not act on that.** Per `DEC-20260831-a9716f` it is `CC-3`/`CC-1`, routed to a separate
`review-breakthrough`, `max`, `degradable: false` round (`Q-2`) that **has not been
opened**, with the reviewers' findings as its **input at derivation tier, never its
conclusion**. Until that round runs, `KN-FIND-002` stands exactly as committed and
nothing downstream may cite this erratum as having retiered it.

**`OBJ-4`, the reproduced false premise marked correct. ADDRESSED.** The superseded
memo's §6.2 reproduced, with a check-mark, the justification *"for prime-order
prime-field curves `End_{F_p}(E) = Z`, so `φ = [m]` ... Matches `KN-FIND-b7e091`
exactly."* **`End_{F_p}(E) = Z` is false for every elliptic curve over a finite field:**
the `p`-power Frobenius `π_p` lies in `End_{F_p}(E)` and has degree `p`, while `[m]` has
degree `m²`; `p` prime is not a perfect square, so `π_p ≠ [m]` for any `m`, hence
`End_{F_p}(E)` strictly contains `Z`. *(Provenance of the degree facts:
`recalled` — standard theory of elliptic curves over finite fields, no source opened for
them in this session. They are checkable in one line by any reader: if `π_p = [m]` then
`p = m²`, impossible for prime `p`. The **repair itself** — correcting this lane's own
reproduction — is discharged by the red-team report `OBJ-4`, `internal`, opened in full,
together with the `KN-FIND-b7e091` text quoted verbatim from the opened file. No
`recalled` source discharges a repair here.)*

**Corrected reproduction, as §6.2 should have read.** On a prime-order-`ℓ` subgroup
`⟨G⟩ ⊆ E(F_p)`, `E(F_p)[ℓ]` is the one-dimensional `λ = 1` eigenspace of Frobenius; any
`φ ∈ End_{F_p}(E)` preserves it and acts on it as a scalar `λ_φ mod ℓ`, and `λ_φ` is a
root mod `ℓ` of `φ`'s public characteristic polynomial and is therefore computable in
polynomial time. So `φ(Q) = [λ_φ]Q`, computable in **`O(log ℓ)` group operations** by
double-and-add — **not** *"`m` group operations"*, which as literally written is `Ω(ℓ)`
by repeated addition and is not a constant- or even a log-overhead simulation at all.

**A consequence of combining this with `R-OBJ6`, reported rather than buried.** At
`O(log ℓ)` group operations, the endomorphism oracle does **not** satisfy the repaired
`M2`'s `O(1)` bound. The superseded memo's §6.2 line *"M2: ... collapse succeeds, `m`
group operations, A-strict. Matches `KN-FIND-b7e091` exactly. ✔"* is therefore
**withdrawn** by this erratum as a reproduction: under the repaired `M2` the endomorphism
oracle sits in the **non-constant-overhead** tier, and the reproduction matches
`KN-FIND-b7e091`'s *conclusion* (simulable; no sub-birthday advantage) but **not** its
*tier*. This is the same inconsistency the validator recorded as `F-5` — that the
constant-overhead criterion is applied inconsistently across `KN-FIND-002` and
`KN-FIND-b7e091`. **`F-5` and the `KN-FIND-b7e091` defect are `CC-2`, routed to the same
unopened `review-breakthrough` round.** This erratum corrects only its own lane's
reproduction and touches neither record.

### §D.2 `OBJ-9` — the broken cross-reference at the scope sentence. ADDRESSED.

The superseded memo's §0 said *"The rejection is **scoped**, and §7 states exactly what it
does not cover"*. §7 is the lossy-projection test and contains **no** scope limitation;
the limitation lives in §§5.4, 9.2 and 10.2. Nothing was hidden — the content is stated
inline in §0 — but a reader following the pointer to check the scope finds nothing, which
is the mechanical route by which correctly-labelled tiers leak downstream.

**Repair applied.** The re-issued §B states its scope **inline and in full**, and where it
points, it points at **§§C.5 (Fork D), D.7 (inherited hypotheses) and I (forward
guidance)** of this erratum and at **§§5.4 and 10** of the superseded memo — never at §7.

### §D.3 `OBJ-10` — novelty inflation in §0. ADDRESSED.

The superseded memo's §0 said the closure was reached *"by the same closure mechanism as
`KN-FIND-002`'s jet oracle and `KN-FIND-b7e091`'s endomorphism oracle — and, unlike
**those two**, without needing the structured-GGM weakening"*. But `KN-FIND-b7e091`'s
endomorphism simulation is already strict-branch and needs no structured weakening — as
the memo's own §6.2 shows.

**Repair applied.** The phrase is replaced by **"unlike `KN-FIND-002`'s jet oracle"**, and
the re-issued §B does not carry the comparison at all, because under `R-OBJ1` the
disposition no longer rests on the GGM route and the comparison is corroborative context
rather than a claim. Recorded so that a later reader does not restore the wider phrase.

### §D.4 `OBJ-11` — Pareto wording contradicting the Pareto numbers. ADDRESSED.

The superseded memo's §8 said *"So D1 is dominated on every axis and matched on none"*
while its own numbers were `sota_delta` `+0` on time, `+0` on memory, `+0` on
data/queries, `+0` on the constant factor. A delta of `+0` on every axis is **matched**,
not dominated.

**Repair applied — the restatement the red team specifies, verbatim:** *"equalled at
every exponent and on the constant factor, and strictly dominated once the per-query cost
of the oracle is charged."* The charged per-query cost is `O(log n)` group operations on
branch D-integer and one `F_p` comparison on branch D-handle (§C.5), against a rho that
pays nothing at all for the same predicate (`KN-TECH-006`). See §G.

### §D.5 `OBJ-12` — two missing frontier rows. ADDRESSED, with both rows discharged from opened corpus records.

Added to the frontier in §G:

- **van Oorschot–Wiener parallel collision search with distinguished points**
  (`KN-TECH-006`, `internal`, opened in full): verbatim `complexity` field —
  *"expected ~0.886*sqrt(n) group operations serial; ~sqrt(n)/m wall-clock on m
  processors; small per-processor memory"*, and verbatim from the body — *"a claimed
  improvement must beat the *fully-charged parallel* cost -- including memory traffic and
  distinguished-point overhead -- not an idealized serial count."* This is the row that
  carries the time–memory–parallelism interpolation the target-result profile asks for.
- **Pohlig–Hellman** (`KN-TECH-030`, `internal`, opened): verbatim `complexity` field —
  *"O(sum_i e_i * (log n + sqrt(p_i))) group operations for n = prod p_i^{e_i}; dominated
  by the largest prime factor"*. This is the row that makes `R-OBJ2` an error rather than
  a pedantry.

**Can the omission flip the disposition?** No. `sota_delta` is `+0` on every checked axis,
and under the model-free ground of §C.2 D1 supplies zero information to a
coordinate-holding adversary, so no additional frontier row can make D1 incomparable. The
gap is recorded as a completeness item with that reason attached — not as a fabricated
`null` under AGENTS.md rule 5, which it was not: the superseded memo's `dominated_by` was
genuinely checked against three rows and disclosed which nested citation it had not
opened.

### §D.6 `OBJ-13` and `F-4` — two different controls sharing one object. ADDRESSED.

**They are now named separately.**

- **Argument-level control (proves-too-much).** The anomalous curve is an object on which
  the *conclusion of the argument rule* is known false. It tests `M1` and `M2` **as
  rules**. It fired on `M1` — which is the most valuable thing in the superseded memo —
  and, under the repaired statement, does not fire on `M2` (§C.4).
- **Record instrument-level positive control.** `ECDLP-IDEA-436` declares, verbatim:
  *"Positive: a curve and `n` where a *known* `p`-adic separation exists (e.g. anomalous
  `#E(F_p) = p`, where the Smart/SSSA attack applies) — the instrument must detect it."*
  Per validator `F-4`, **this control is not executable**: an anomalous curve has
  `#E(F_p) = p`, so a generator has `n = p` and `gcd(n, p) = p`, violating the record's
  own Assumption 1. There is no canonical order-`n` prime-to-`p` lift of a point of order
  `p`, so `inv` there is not merely uninformative — it is **undefined**. A positive
  control that cannot be executed is not a control. This does not change the gate outcome,
  since the gate closes the family before any run; it matters for the **next** record in
  this lane that copies the control design.
- **Forward guidance (`F-4`, recorded as a design question, not a claim).** Any successor
  record in this lane must name a positive control that satisfies its own assumptions. One
  workable substitute the validator names is a **non-generator `S` of prime-to-`p` order
  on an anomalous curve**, where D1 *is* defined while the transfer still applies to the
  full group. Whether that is a useful calibration is a design question for the successor.

**Carried up into §0, as `OBJ-13` requires.** The exclusion *a point whose order is
divisible by `p` is outside scope* now appears in **§B**, not only in the §10 scope block.
This is the scope sentence the red team calls the single most important of the round: it
is what makes clear that this lane says **nothing** about the anomalous additive transfer
(`KN-TECH-033`), which is *"the one place where lifting to characteristic zero is known to
pay"* and therefore the one object against which a `p`-adic proposal would most want to be
measured.

### §D.7 `OBJ-15` and `F-2` — inherited-and-unused hypotheses, and the query-density exponent. ADDRESSED.

**(a) `ordinary` and `p ≥ 3` are inherited and unused.** Lemma 1 needs good reduction and
`gcd(n, p) = 1`; Lemma 2 needs a Weierstrass model. Neither uses ordinariness, so the
Proposition also covers **supersingular** curves. And per validator `F-2`: on the general
Weierstrass form with `a_1 … a_6` the argument runs unchanged at `p = 2` and `p = 3`,
because the formal group is pro-`p` for every `p` (so reduction stays injective on
prime-to-`p` torsion) and negation is `(x, y) ↦ (x, −y − a_1 x − a_3)`, so the `x`-fibre
is `{P, −P}` in every characteristic. `p ≥ 3` is needed only for the **short** form
`y² = x³ + Ax + B`, which §1.1 does not use.

**Decision, recorded:** this erratum **keeps** `ordinary` and `p ≥ 3` in the scope block,
for consistency with the frozen `ECDLP-IDEA-436` Assumption 1 and with `KN-TECH-73630e`'s
scope labels, and **records that both are inherited and unused, and are free to drop on a
general Weierstrass model**. This is deliberate under-claiming and it is stated rather
than silent. The `p = 2` entry stays in the §10 exclusion list on the same basis, now
annotated as inherited rather than required. A later reader wanting the sharper statement
does not have to rediscover that the restriction is free.

**(b) The query-density exponent under Assumption 3.** The superseded memo's §8 computed
reciprocal informative-query density `δ = 1/2` *"under adaptive references"*, and `δ = 1`
for a fixed reference, taking `λ = max(a, δ + q, ℓ, u + q) ≥ 1/2`. `ECDLP-IDEA-436`
Assumption 3 reads, verbatim: *"The functional family is fixed in advance. Post-hoc
selection of `(j, r)` after seeing the scalar is forbidden advice and scores zero."*

Two readings, and this erratum records both because they differ and the difference does
not matter to the outcome:

- **Reviewer's reading (recorded as operative, being the conservative one and the
  reviewer's finding):** the frozen contract fixes the reference, so `δ = 1` and
  `λ ≥ 1`. The record's own promotion gate `λ, μ ≤ 0.45` **fails harder than the memo
  reported**, and the memo chose the reading more favourable to the idea — which is the
  correct direction for a producer to err in, and it should have said so.
- **Alternative reading, recorded for completeness:** an attack never *sees* the scalar,
  so choosing references adaptively during an attack is arguably not "post-hoc selection
  after seeing the scalar"; under that reading `δ = 1/2` and `λ ≥ 1/2`.

**Under either reading `λ ≥ 1/2 > 0.45`, so the record's own promotion gate fails**, and
the disposition of §B is unchanged. Recorded so that no later reader has to re-adjudicate
the ambiguity to check the arithmetic.

**(c) Also recorded in the producer's favour, per `OBJ-15`:** D1 is the exact functional
`KN-OPEN-3417fc` names as its **own headline worked example** — verbatim from that record:
*"for instance the profile `v_p(x([k]Ŝ) - x([j]Ŝ))`"*. This erratum is correct not to
claim any closure of that open problem, which quantifies over *any* computable functional
and whose negative-resolution criterion is an unrun measurement; but the object disposed
in §B Part 1 is the open problem's own worked example, which makes the disposition more
consequential than "one named family" conveys — and equally makes the missing measurement
more consequential.

### §D.8 `CM-3` — memory stated beside time. ADDRESSED.

The `docs/target-result-profile.md` discipline requires memory beside time in every cost
statement. The superseded memo did not state it.

**Stated here.** The D1 simulator is **stateless beyond two handles**: memory `O(1)` group
elements, i.e. `O(log n)` bits, on branch D-handle; on branch D-integer, the same plus the
handle being materialised. Queried as a profile vector over a reference set `J`, memory is
`O(|J|)` group elements, `O(|J| log n)` bits, and that is the *adversary's* choice of
`|J|`, not a requirement of the simulation. **D1 offers no memory axis at all**: it
supplies no distinguished-point structure, no table, and no precomputation, so there is no
point at which it interpolates against BSGS's `n^{1/2}` memory or against the van
Oorschot–Wiener time–memory tradeoff (`KN-TECH-006`). Its parallelisation position is
likewise unchanged from rho's: D1 adds nothing to and subtracts nothing from the
`~sqrt(n)/m` wall-clock on `m` processors that `KN-TECH-006` records. The `μ` exponent of
`ECDLP-IDEA-436`'s own cost model is therefore whatever rho or BSGS supplies, with `+0`
from D1.

### §D.9 `F-3` — the nonidentity hypothesis on Lemma 2. ADDRESSED.

Lemma 1 correctly carries its hypothesis (*"For `k ≢ 0 mod n`"*); Lemma 2 as stated does
not, yet its forward direction needs both points to differ from the identity, since `x` is
undefined at the identity in the affine chart.

**Repair applied — Lemma 2 as it should read:**

> **Lemma 2 (repaired).** *For `j, k ≢ 0 mod n`:* on a Weierstrass model, `x(−P) = x(P)`
> identically, and `x(P) = x(P')` implies `P' = ±P`. Hence over `F_p`,
> `x([k]S) = x([j]S) ⟺ k ≡ ±j mod n`; and over `Q_p`,
> `x([k]Ŝ) = x([j]Ŝ) ⟺ [k]Ŝ = ±[j]Ŝ ⟺ k ≡ ±j mod n`.

Nothing downstream was wrong — the Proposition already carries `k, j ≢ 0 mod n` — so this
is hypothesis hygiene in an intermediate lemma, not a coverage gap. The degenerate case
itself remains handled as the superseded memo handles it: §1.2 names the missing
convention in the frozen family explicitly, and §5.3 shows the disposition is independent
of which convention is chosen, the simulator detecting the case with one further equality
test against the identity handle (charged in §C.5).

**Nine items, nine addressed, none declined.**

---

## §E. Consequences of the repairs for the memo's own controls

Recorded separately because two of them run against the superseded memo and would
otherwise be buried inside a repair.

1. **`Control A` (proves-too-much on anomalous curves): PASSES under the repaired `M2`.**
   Half 1 unchanged — `M1` proves too much and is broken as a closure rule. Half 2
   re-run — `M2` does not fire (§C.4). One residual weakness recorded: the *negative*
   direction of the repaired `M2` is establishable only conditionally on `KN-TECH-005`,
   and is labelled a consistency check rather than a mechanism check.
2. **`Control B` (reproduction of the four recorded oracle verdicts) is materially
   changed by the repaired `M2`, and its `M2` score drops to zero.** Under the repaired
   `O(1)`-bounded statement: the **jet** oracle does not fire `M2` (unchanged — derivative
   values separate points in identical group-theoretic relations); the **endomorphism**
   oracle does **not** fire `M2` either, at `O(log ℓ)` group operations under the
   corrected eigenvalue argument (§D.1), **withdrawing** the memo's §6.2 `M2` check-mark;
   the **elliptic-net** oracle does not fire, at `O(log N)` (unchanged); the **incidence**
   oracle does not fire, at `O(B^m)` (unchanged). So **the repaired `M2` fires on none of
   the four corpus-recorded oracles.** `M1`'s reproduction is unchanged.
3. **Therefore `OBJ-5` is sharpened, not resolved, and this is the honest report.** The
   red team's `OBJ-5` said `M2` has no held-out object in the **firing** direction, so its
   discriminating power is asserted rather than measured. Under the repaired statement the
   position is worse: `M2` now has **exactly one** firing instance anywhere in this
   program's corpus, namely **D1 itself**, and zero independent ones. `Control B` was
   already non-independent by construction (`M1` and `M2` were abstracted *from*
   `KN-FIND-002`'s four classifications and then validated *by* reproducing them, a fit
   statistic on the training set); the repair does not make it independent and makes its
   `M2` column empty. **This is a reason to lead with the model-free ground of §C.2, which
   uses neither `M1` nor `M2`, and it is a reason the corroboration is corroboration.**
   `RC-3` — run `M1` and `M2` on one oracle class recorded **outside** `KN-FIND-002` and
   `KN-FIND-b7e091`, the cheapest candidates being a MOV/pairing oracle on a
   low-embedding-degree curve (`KN-TECH-032`, named from `KN-TECH-033`'s applicability
   limits) or a Weil-descent / extension-field index-calculus oracle, which `KN-LIT-7606`
   names as the canonical genuine non-generic algorithm — **remains required and is not
   discharged here.** It is zero-compute and is not in this task's scope.
4. **No null-object control exists for this lane, and none can exist without running
   something.** Zero runs means zero null objects. The reported image size is **flat in
   the precision parameter `r`**, which is the canonical artifact tell of
   `docs/inventor-protocol.md` §3 — a quantity that does not move when the parameter meant
   to move it increases. Here the flatness is **derived** rather than measured, so the tell
   does not fire automatically; but a finite-precision implementation would report the same
   flatness and **can never observe `+∞`, only "at least `r`"**, so the derivation converts
   directly into a demand for the measurement. `ECDLP-IDEA-436`'s own declared negative
   control — *"random profiles with the same precision budget and no scalar dependence"* —
   has not been run, and `KN-OPEN-3417fc`'s own negative-resolution criterion is explicitly
   *"measuring a stated family of coordinate functionals at toy `p`"* and has not been run.
   **`RC-1` remains required and is not discharged here**; it is queued as `Q-1` of
   `DEC-20260831-a9716f` and is a different role and a different task card.

---

## §F. The obstruction, repaired, with its resource reading

Recorded at the `docs/inventor-protocol.md` §4 standard, with the repairs of §C folded in.

**Named obstruction (derivation tier, zero runs).**

- *Quantity:* the size of the image of `inv_{j,r}` on `⟨Ŝ⟩`, and the group-operation
  overhead of simulating it.
- *Value:* image size exactly **2** for every `r ≥ 1`, on a model realising the good
  reduction; simulation overhead exactly **1 inversion + 2 equality tests** (plus 1 for
  the degenerate case) on branch **D-handle**, and **`O(log n)`** on branch **D-integer**.
  On a non-minimal integral model with `c = −2 v_p(u) > 0`, the image is
  `{min(c,r), r}`, which **degenerates to size 1** when `r ≤ c`.
- *Error bars:* **none — this is a derivation over stated hypotheses, not a measurement.**
  No runs are cited because none exist. This is disclosed rather than dressed as a
  measured obstruction, and no later record may cite the flatness in `r` as a measured
  quantity until `RC-1` runs.
- *Scope:* as §B "Scope of Part 1", repaired by `R-F1` and `R-OBJ2`.

**`resource_check` — which theory wants this measurement.** `examined: true`, and the
reading is recorded in two parts.

1. *Carried forward from the superseded memo, with its provenance caveat intact.* The
   degeneracy is hypothesis-shaped in the **bad**- and additive-reduction regime. A bounded
   web search in the superseded memo's session surfaced *Recovering Kodaira types from
   ℓ-torsion on elliptic curves* (arXiv:2607.02678), which *"endows `E[ℓ]` with a distance
   function that records the `p`-adic distances between the `x`-coordinates of the
   points"* and shows this determines the Kodaira type. That is the **same tracked object**,
   informative exactly where Lemma 1 fails. **Provenance: `retrieved`, abstract level only,
   by the superseded session; not re-fetched by this session, and nothing here rests on
   it.** The abstract does **not** state that the good-reduction case is degenerate; that
   is this lane's own derivation, and the adjacency is corroborating context, never
   support. Reading: the object is not empty in general — it is empty precisely under
   `ECDLP-IDEA-436`'s own good-reduction hypothesis, which the ECDLP setting cannot drop,
   since bad reduction is not the cryptographic case.
2. *Added by this erratum, and it is the sharper reading.* The collapse is not a
   pairwise-versus-multipoint phenomenon; it is **rigidity**. Lemma 1 puts every lifted
   `x`-coordinate in `Z_p` reducing to its `F_p` value, so for **any** polynomial functional
   `F` of several lifted coordinates, `v_p(F) = 0` unless `F` vanishes mod `p`.
   Two-valuedness needs the *second* step — that `F` vanishing mod `p` forces `F` to vanish
   **exactly** in `Q_p` — and for the pairwise `x`-difference that is supplied by Lemma 2's
   `±`-fibre structure holding on **both** sides. For a general multi-point functional that
   step fails: a determinant, a resultant, or a division-polynomial value can vanish mod `p`
   without vanishing in `Q_p`, and then `v_p` takes a **finite value `≥ 1`** and the
   precision `r` **stops being inert**. So the measured degeneracy is the hypothesis of a
   sharper search: it predicts that any product of pairwise differences (a Vandermonde in
   the `x`-coordinates) and any functional whose vanishing encodes a group-law relation
   (the collinearity determinant, which vanishes iff `P₁ + P₂ + P₃ = O`) **still**
   collapses, for free; and it localises the first genuinely untried object as a
   multi-point functional whose mod-`p` vanishing locus is **neither** a union of `±` fibres
   **nor** a group-law relation. **Provenance and status: this reading is `RTF-1` of the
   red-team report `TASK-20260831-62019a`, `internal`, opened in full. It is a candidate for
   ranking, NEVER evidence — derivation tier, zero runs, produced in that red-team session,
   not independently checked, changing no status and supporting no promotion.** It is
   testable by part 3 of `RC-1`, which has not been run. Reproduced here because the
   erratum is the artifact a later reader will open, and because it upgrades the superseded
   memo's §10 item 3 from *"whether it collapses by a similar route is open"* to a named
   separator — **but only if `RC-1` part 3 confirms it.**

---

## §G. Pareto honesty (`OBJ-11`, `OBJ-12`, `CM-3`, `CM-4`)

**Object studied.** The `p`-adic coordinate-valuation profile of pairwise `x`-differences
along the canonical prime-to-`p` torsion lift `⟨Ŝ⟩ ⊂ E(Q_p)` — disjunct D1 of
`ECDLP-IDEA-436`.

**Depth of verified structure.** Derivation tier, zero runs, single producer session,
independently reviewed by two blinded sessions under a pre-committed review plan, with the
load-bearing Proposition independently **blind re-derived** by the validator (sealed
pre-read hash `14b80674828ce3ff91d4d636e3ce494f61d9fb32a252264db13fdd25ad9630fc`, per
`DEC-20260831-a9716f`). No measurement exists anywhere in this lane.

**`dominated_by`: Pollard rho with the negation map on the `x`-line**, at
`n^{1/2+o(1)}` time and `O(1)` memory — in its fully-charged parallel form, `~0.886·√n`
group operations serial and `~√n/m` wall-clock on `m` processors (`KN-TECH-006`).

**Frontier rows checked — all five, across time, memory and data/queries.**

| row | time | memory | source, provenance |
| --- | --- | --- | --- |
| Pollard rho with negation map | `n^{1/2+o(1)}`; `~0.886·√n` group ops serial | `O(1)` per processor | `KN-TECH-005`, `KN-TECH-006`, `internal`, both opened |
| BSGS | `n^{1/2+o(1)}` | `n^{1/2+o(1)}` | `KN-TECH-005`, `internal`, opened |
| generic preprocessing tradeoff | `S·T² = Ω̃(n)` (Corrigan-Gibbs–Kogan) | `S` bits advice | `KN-TECH-005`, `internal`, opened |
| van Oorschot–Wiener parallel collision search + distinguished points | `~√n/m` wall-clock on `m` processors | small per-processor; `d` sets the memory/steps tradeoff | `KN-TECH-006`, `internal`, opened — **row added by `OBJ-12`** |
| Pohlig–Hellman | `O(Σ e_i(log n + √p_i))`, dominated by `√p_max` | `O(1)`–`√p_max` depending on the sub-solver | `KN-TECH-030`, `internal`, opened — **row added by `OBJ-12`** |

`KN-TECH-001` is cited *inside* `KN-TECH-005` and was **not** opened, in this session or
the superseded one; the rho/BSGS matching is taken from `KN-TECH-005`'s own statement of
it. Disclosed rather than asserted.

**Data/query axis.** D1 supplies no axis on which it is incomparable: by Corollary 4.2
each query yields `≤ 1` bit, and the optimal use of the `±`-fibre indicator against
adaptively chosen references **is** an `x`-line collision search, i.e. rho.

**`sota_delta`, quantitatively:** time exponent **`+0`**, memory exponent **`+0`**,
data/query exponent **`+0`**, constant factor **`+0`**. **Wording repaired per `OBJ-11`:**
D1 is **equalled at every exponent and on the constant factor, and strictly dominated once
the per-query cost of the oracle is charged** — `O(log n)` group operations per query on
branch D-integer, one `F_p` comparison on branch D-handle, against a rho that pays nothing
at all for the same predicate. The `√2`-type saving from the negation map is already
realized inside rho (`KN-TECH-006`, `internal`: *"Negation and other cheap automorphisms
give a further constant-factor speedup"*), and that saving is not free in practice, since
the `±` walk introduces fruitless cycles requiring a correction that consumes part of it
(*provenance: `recalled`, standard; not load-bearing — it makes the baseline slightly
optimistic in the producer's favour and cannot change a `sota_delta` of `+0`*).

**`CM-4`, the van Oorschot–Wiener interpolation, now performed rather than omitted:** D1
offers **no memory axis and no parallelism axis** (§D.8), so there is no point at which it
interpolates anywhere along the vOW curve; it neither improves nor degrades rho's
`~√n/m`. The row is added for completeness and it cannot change the disposition, for the
reason in §D.5.

**`target_complexity` in `ECDLP-IDEA-436`'s own notation.** The record requires
`λ, μ ≤ 0.45` for promotion. Corollary 4.1 gives `ρ_r = 0` — precision is **free**, the
exact opposite of the record's own predicted fatal obstruction — but Corollary 4.2 gives
reciprocal informative-query density `N^δ` with `δ = 1` under the frozen contract
(`δ = 1/2` under the alternative reading of Assumption 3, §D.7), so
`λ = max(a, δ+q, ℓ, u+q) ≥ 1/2` on either reading. `μ ≥` whatever rho or BSGS supplies,
with `+0` from D1. **The record's own promotion gate fails, by a different term than the
record predicted.** Nothing hides in an `o(1)`: the `O(1)` in the corroboration is
literally one inversion and two equality tests, not an exponent.

---

## §H. What this erratum does not claim

1. **No usefulness claim, in either direction.** `KN-TECH-73630e` already establishes that
   this lift is information-theoretically empty for group-theoretic invariants;
   non-simulability would not have implied usefulness, and the disposition here adds no new
   hardness claim about ECDLP. It is about one disjunct of one functional family.
2. **No closure of `KN-OPEN-3417fc`.** That problem quantifies over *any* computable
   non-group-theoretic coordinate or valuation invariant, and its own negative-resolution
   criterion is a measurement at toy `p` that has not been run.
3. **No closure of face F2 (`KN-TECH-06bb4e`) beyond what `KN-TECH-73630e` already
   recorded.** `KN-TECH-06bb4e` was not opened by this session.
4. **No experimental content.** Zero runs, zero implementations, zero `p`-adic arithmetic,
   zero timing.
5. **No status change**, and no identifier minted. §B is a **recommendation**.
6. **No Fork-A adjudication** (`OFQ-1` stays open) and **no Fork-D adjudication**
   (§C.5 answers both branches and picks neither).
7. **No retiering of `KN-FIND-002` or `KN-FIND-b7e091`**, and no downstream record may
   cite this erratum as having retiered either. Those items are routed and unopened.
8. **No claim that any direction is impossible.** §I names what remains.
9. **No independence claim beyond what was obtained.** The mechanical independence check
   for the superseded round is recorded as a **procedure deviation, not a passing check**
   (`PD-1` of `DEC-20260831-a9716f`), and no record may state that it passed.
10. **No novelty claim.** The composition in §C.2 is a re-reading of a derivation this
    program already produced and reviewed; its honest label is `adaptation`, and the
    literature position of the lane is `novelty_status: unverified` — no external source
    was fetched by this session.

---

## §I. Forward guidance — what remains open after this erratum

1. **`OFQ-1`: this program's canonical GGM branch.** `KN-FIND-002` declares the structured
   branch; `KN-FIND-b7e091` declares none and argues in the strict branch. Until one is
   declared canonical — or `KN-LIT-7606`'s `δ`-parameterised model is adopted, which would
   replace the binary with a quantity — every *closed at exponent 1/2* in this corpus
   carries a model parameter that is unstated in at least one record. Cheap, zero-compute.
   Both reviewers judged this a **scoping observation, not a contradiction**, and the
   escalation condition **did not fire**.
2. **Fork D: the canonical query interface.** New with this erratum (§C.5). Handle and
   integer interfaces give two different recorded tiers for the *same* functional, so the
   corpus's `O(1)`-versus-`O(log n)` taxonomy carries a second unstated parameter beside
   `OFQ-1`'s. Zero-compute to settle; it would re-scope more than one record.
3. **The D2 residue.** Not gated (§B Part 2), with the §10 item 2 sub-question and the
   `KN-TECH-033` "name your coincidence" bar attached, that bar carrying its own
   self-label as a framing rather than a result.
4. **Multi-point functionals, sharpened.** §F's second resource reading predicts *where*
   the collapse stops (non-rigid mod-`p` vanishing loci) and where it continues
   (Vandermonde products; group-law-relation determinants). Untested; `RC-1` part 3 is its
   cheapest probe.
5. **Non-Weierstrass models.** Lemma 2 is model-dependent. On a model whose distinguished
   coordinate does not have `±` fibres, the collapse argument does not run as written.
   Whether an equivalent collapse holds is open.
6. **`KN-OPEN-019`.** This lane used an object-first framing **without** the ECDLP object
   enumeration `KN-OPEN-019` calls for. The family-to-object mapping in the superseded
   memo's §7 is a **sketch, not a taxonomy**, exactly as `docs/inventor-protocol.md` §1
   requires it to be labelled, and this erratum inherits that label rather than repairing
   it.
7. **The controls that remain required and are not discharged here:** `RC-1` (toy-scale
   tabulation with the null lift and the three-point probe — the discriminating half nobody
   has run, and the toy-`p` measurement `KN-OPEN-3417fc`'s own criterion asks for),
   `RC-3` (a held-out object for `M2`, now more necessary than before — §E.3), and `RC-4`
   (a frozen regression fixture against `experiments/EXP-GGM-001/simulability_test.py`,
   which no session in this lane has opened, so every "reproduction" here is of **prose**,
   never of an implementation).

---

## §J. Source ledger and citation provenance for this erratum

Provenance labels follow `templates/research-records.md`: `recalled | retrieved | kb |
internal`. **No `recalled` source discharges any repair in this erratum.**

**Opened in full in this session and quoted verbatim (`internal`):**
`AGENTS.md`; `agents/idea-generator.md`; `docs/inventor-protocol.md`;
`ledger/decisions/DEC-20260831-a9716f.yaml`;
`ideas/artifacts/ECDLP-IDEA-436/ggm_simulability_gate.md` (the superseded artifact, read
only, unmodified);
`.../reviews/TASK-20260831-62019a/red-team-report.yaml` (red team, `OBJ-1`–`OBJ-15`,
`CM-1`–`CM-4`, `RTF-1`, `RC-1`–`RC-4`, escalation and routing);
`ideas/ECDLP-IDEA-436_local_torsion_coordinate_valuation_profile_hypothesis.md` (frozen,
read only, unmodified); `knowledge/techniques/KN-TECH-005.md`;
`knowledge/literature/KN-LIT-7606.md`; `knowledge/findings/KN-FIND-002.md`;
`knowledge/findings/KN-FIND-b7e091.md`; `knowledge/techniques/KN-TECH-73630e.md`;
`knowledge/open-problems/KN-OPEN-3417fc.md`; `knowledge/techniques/KN-TECH-033.md`;
`knowledge/techniques/KN-TECH-006.md`; and the committed task card
`coordination/goals/GOAL-ECDLP-001/proposals/B71-IDEA436-GATE-ERRATUM-20260831-0e7ce6/dispatch_queue.json`.

**Opened in part in this session, and read only in the parts named (`internal`, disclosed
as partial):**
`.../reviews/TASK-20260831-c6ceb9/validation-report.yaml` — the `findings` block `F-1`
through `F-5` and the `escalation_assessment` block were read in full; the remainder of
that report (including the blind-re-derivation transcript) was **not** read.
`ledger/evidence/EV-ECDLP-048824.yaml` — the `boundaries` block `B-1`–`B-7` and the
`strength`/`proof_status` fields were read; the observation, contradiction and confound
blocks were **not** read in full, and this erratum makes no claim about their contents
beyond the `CC-1`/`CC-2`/`CC-3` routing that `DEC-20260831-a9716f` states.
`knowledge/techniques/KN-TECH-030.md` — frontmatter `complexity` field and the two
sections quoted were read; the record was not read end to end.

**Not opened by this session, and therefore carried only as the superseded memo or the
reviewers state them:** the `proof-search-map.yaml` and `source-novelty-audit.yaml` of the
superseded round (their `method_ceiling`, `dependency_audit`, `quantifier_order` and
`control_verdict` texts are quoted **as the red team quotes them**, `internal`, from a
report that opened them and verified their hashes); `KN-TECH-06bb4e`; `KN-TECH-032`;
`KN-LIT-6935a1`; `KN-LIT-7595`; `KN-TECH-001`; `experiments/EXP-GGM-001/*`;
`KN-LIT-011`, `KN-LIT-013`, `KN-LIT-082`, `KN-LIT-012`, and every other `KN-LIT-*` cited
*inside* an opened record. **No web fetch and no retrieval query was performed by this
session**, so no source in this erratum carries `retrieved` or `kb` provenance on this
session's authority.

**`recalled`, marked and non-load-bearing:** the degree facts `deg π_p = p` and
`deg [m] = m²` underlying §D.1's correction (checkable in one line: if `π_p = [m]` then
`p = m²`, impossible for prime `p`); the fruitless-cycle correction to the negation-map
speedup in rho (§G).

**`retrieved`, by the superseded session and not re-fetched here:** arXiv:2607.02678, at
abstract level only (§F); `eprint.iacr.org/2006/230` (Koblitz–Menezes, *Another Look at
Generic Groups*), whose fetch **failed** to yield extractable text and which is cited only
at web-search-snippet level, for a fact that is independently textbook and load-bearing on
nothing.

**Novelty status of this lane: `unverified`.** No literature was checked by this session
beyond the internal corpus. That is the honest label, not a weakness in the erratum.

---

## §K. Limitations of this session

1. **No execution capability.** This session's tool surface is read, search, glob, write
   and message only: **there is no shell, no interpreter, and no hashing tool.**
   Consequently (a) the `sha256` values of this erratum and its companion artifacts were
   **not computed** and are recorded as `null` with this reason in the session receipt —
   the archival task `TASK-20260831-95b530` computes them; and (b) the strict
   duplicate-key-raising YAML parse required by the completion gate **could not be
   executed by this session**. What *was* performed is a mechanical structural audit of the
   YAML deliverable using the pattern-search tool plus a line-by-line manual review — see
   the receipt's `yaml_self_check` block for exactly what that audit does and does not
   cover. **It is not a substitute for a strict parse, and it is not recorded as one.**
   This limitation is disclosed here and in the receipt rather than left for the
   orchestrator to discover; the strict parse must be run before this erratum is relied on.
2. **Zero runs, zero measurements.** Every quantity in this erratum is derived over stated
   hypotheses. There is no null object, no seed, no sample, and no measured obstruction
   anywhere in this lane, and none is asserted.
3. **Resolved model not probe-verified.** `orchestration.adapter doctor --probe` is a
   network-touching backend call and was not run; the resolved model identifier in the
   receipt is session configuration, not verified configuration. Amazon Bedrock was not
   used and no network request was made (AGENTS.md rule 16).
4. **Partial reads disclosed.** Three records were read in part, named in §J. Nothing in
   this erratum rests on an unread portion of them.
5. **The routed items are unopened.** `CC-1`, `CC-2`, `CC-3` and `F-5` require a
   `review-breakthrough`, `max`, `degradable: false` round that has not been opened. Until
   it runs, `KN-FIND-002` and `KN-FIND-b7e091` stand exactly as committed, and §D.1's
   corrections are confined to this lane's own reproduction of them.
