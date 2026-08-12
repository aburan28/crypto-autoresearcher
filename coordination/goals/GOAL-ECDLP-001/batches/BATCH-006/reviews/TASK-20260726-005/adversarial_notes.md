# Adversarial notes — TASK-20260726-005

Independent review of **H-GGM-001 + EXP-GGM-001 v1**, BATCH-006, GOAL-ECDLP-001.
Companion to `review_report.yaml` (terminal verdict: **REVISE**).

**Binding.** Both reviewed paths are supplied by commit `5de2db97ee3ac60edddd8537f687c7156684d34d`
(parent `a325d824`), an ancestor of HEAD `ab59e26b`. `ledger/hypotheses/H-GGM-001.yaml` →
`023d7fc4576db25d77e9d4b0444a35f67eacc3dc547ea38282841737cbe66372`;
`experiments/EXP-GGM-001/specification.yaml` →
`09931848d2dbe55aa998857db9653d763a5b327a2016dd56e8eab942a8a03c56`.
Git-object, HEAD-object, and working-tree hashes agree for both.

**Independence.** This session did not author H-GGM-001, EXP-GGM-001, or IDEA-20260726-004.
It is distinct from the originating Coordinator session (`proposed_by: coordinator`;
`inference_receipt.resolved_model_id: glm-5p2`, `fallback_used: true`) and from the
concurrent TASK-20260726-006 red-team session.

**Scope.** Everything below is an attack on the *protocol*. Nothing here is a claim about
whether the jet, elliptic-net, incidence, or endomorphism oracle is in fact GGM-simulable.
No crypto-scale, breakthrough, or universal-impossibility claim is made or endorsed.

---

## 1. The strongest case against the specification, in one paragraph

EXP-GGM-001 is presented as a machine-checkable decision procedure. It is not one. Its core
routine — "express the oracle's answer as a function of group-operation results and equality
tests" — is a research question about program equivalence over an unbounded domain, not a
computation. What will actually be implemented is a hand-authored classification, and the
specification hands the implementer the answers: `expected_verdict` for all eight subjects
sits in the same frozen file the Executor must read to build the test. The four controls
that are supposed to certify soundness are the four *easiest* oracles in the model — two are
the model's own primitives, two are its two canonical excluded objects — so a classifier with
no mathematical content passes them 4/4. What the gate certifies, therefore, is that the
implementer read the file. Wrapped around that hollow core is a claim-tier argument that
converts a SIMULABLE verdict into a scale-independent closure at exponent 1/2, and an
`analysis_methodology` clause that instructs the analysis to assert that closure *before any
verdict exists*. The protocol is a mechanism for converting a pre-written expectation into a
derivation-level claim, with a control gate whose passing is uninformative.

---

## 2. The control gate does not discriminate — exhibited

The specification is unambiguous that everything rests here:

> "The controls are the success gate: the test must correctly classify all four controls
> before any augmented-oracle verdict is trusted." … "The control gate is binary: 4/4 correct
> or the test fails."

### 2.1 A content-free classifier that scores 4/4

Define **Classifier B**, which reads only the declared `output_format` and `public_data`
fields and never opens `computational_procedure`:

> SIMULABLE **iff** the output is a group element, or is a member of the declared
> `public_data` list. Otherwise NON-SIMULABLE.

| control | output | Classifier B | `expected_verdict` | match |
|---|---|---|---|---|
| `pure_generic` | `P+Q`, a group element | SIMULABLE | SIMULABLE | ✓ |
| `public_curve` | `(a,b,p,N)`, declared public | SIMULABLE | SIMULABLE | ✓ |
| `discrete_log` | integer `k` | NON-SIMULABLE | NON-SIMULABLE | ✓ |
| `encoding` | x-coordinate in F_p | NON-SIMULABLE | NON-SIMULABLE | ✓ |

**4/4. The gate passes.** No simulator was constructed. No group operation was counted. No
equality test was reasoned about. The classifier does not know what a group is.

### 2.2 …and it then disagrees with the specification on the actual subjects

Run the same rule on the four augmented oracles:

| oracle | output | Classifier B | `expected_verdict` |
|---|---|---|---|
| `jet_oracle` | `(P+Q, eps·(P+Q))` — the eps-block is neither a group element of E(F_p) nor declared public | **NON-SIMULABLE** | SIMULABLE ✗ |
| `elliptic_net_oracle` | `W(a,b)`, a field value, not declared public | **NON-SIMULABLE** | SIMULABLE ✗ |
| `incidence_oracle` | list of factor-base index tuples | undetermined (depends on whether the factor base is typed public) | SIMULABLE ? |
| `endomorphism_oracle` | `phi(P)`, a group element | SIMULABLE | SIMULABLE ✓ |

A classifier that passes the gate perfectly disagrees with the specification on **at least
two of the four subjects the experiment exists to decide**. So 4/4 on this control set
carries *no information* about correctness on the augmented oracles. The gate and the
subjects are not in the same difficulty class, and the specification never notices.

### 2.3 Why the controls are too easy — the structural reason

Every one of the four is **extremal**:

- `pure_generic` **is** the model's native oracle.
- `public_curve` **is** the model's declared public setup.
- `discrete_log` **is** the exact object Shoup's lower bound is about.
- `encoding` **is** the textbook definition of encoding-dependence.

Not one control sits anywhere near a decision boundary. Soundness is only demonstrated by
controls that are *hard for the test*. These are the four easiest oracles in the whole model.

Three control classes that would actually discriminate, and are all absent:

1. **Bounded-overhead boundary.** `query = (P, m) -> m*P`, `m` in binary. Generically
   computable, but only in Θ(log N) operations — so under the spec's own "C ≤ 10,
   N-independent" criterion it must *not* come out plain SIMULABLE. As frozen, **no control
   reaches the overhead branch at all**: `pure_generic` is asserted C=1, `public_curve` C=0,
   and the two NON-SIMULABLE controls short-circuit before any counting. The metric
   `simulator_overhead_C` and H-GGM-001 falsifier 4 are untested by the gate.
2. **Perfect vs. statistical simulation.** An oracle returning a fresh, consistent random
   label per element. The specification names `gg_model_variant: shoup_encoding` but never
   says whether simulation must be exact or may be statistical. Nothing probes it.
3. **Public-but-non-generic.** A Weil-pairing-value oracle on a pairing-friendly curve is
   public, computable from the curve parameters, and paradigmatically non-generic. This is
   the control that would catch the endomorphism oracle's stated inference — see §4.

---

## 3. The witness is the wrong object, and the primary control admits none

### 3.1 "Different answers" without equivariance makes `pure_generic` a false positive

The definition is: *"an encoding pair (E_1, E_2) that are generic-model-indistinguishable but
yield different O-answers."*

Take the `pure_generic` control. Let E₁ be any labelling of E(F_p) and E₂ = π ∘ E₁ for a
label permutation π. On the same abstract inputs, the group-operation oracle returns
different label *strings* under E₁ and E₂. Read literally, `pure_generic` has a witness and
is NON-SIMULABLE — the specification's own declared false-positive falsifier, fired by the
model's native oracle.

The property actually intended is **equivariance**:

> O is encoding-independent iff `O_{π∘E}(π(x)) = π(O_E(x))` for every relabelling π
> (π acting trivially on non-group answer types).

A witness is a **failure of equivariance**, not a difference of answers. The word never
appears in the specification. Without it the criterion is either vacuous or rests on an
unstated convention — and an unstated convention cannot be "verifiable by a third party."

### 3.2 The discrete-log control admits no witness of the mandated form

This is the sharpest defect in the package, and it is internal to the frozen text.

Fix the abstract group G = Z_N. The DL oracle answers: given abstract `a, b` with `b = k·a`,
return `k`. **`k` is a function of the abstract pair alone.** Under any two encodings σ₁, σ₂
of the *same* abstract pair, the answer is the same `k`. The DL oracle is therefore
**encoding-independent**. Its non-simulability is a *query-complexity* fact — Shoup's
Ω(√p) — not an encoding-dependence fact.

Contrast the x-coordinate oracle: two realizations of Z_N assign genuinely different
x-coordinates to the same abstract element, so an encoding-pair witness exists there.

Now read the frozen `expected_witness` for the DL control:

> "Any two encodings E_1, E_2 representing the same abstract group element relationship but
> requiring different k"

**Same relationship ⇒ same k.** The object described cannot exist. This is not vagueness; it
is a contradiction inside the certificate specification for the control that H-GGM-001
declares *"the primary unsoundness falsifier."*

The realistic execution path: the test emits NON-SIMULABLE for the DL control with no
well-formed witness, and the gate records a pass. The control passes by **asserting a fact
everyone already knows** — a fact the frozen file itself states in three separate places
(`expected_verdict`, `role`, and H-GGM-001 `predictions`) — not by detecting anything.

**Consequence:** the two NON-SIMULABLE controls fail for two *different* reasons, and the
single mandated witness format fits only one of them. The gate has one bit where it needs two.

### 3.3 `verify_witness` "with independent code" cannot deliver what it promises

`docs/claims-and-verification.md` works because ECDLP claims are in NP with a recomputation
checker: compute `k·P`, compare to `Q`. A non-simulability witness has two conjuncts of
*different logical type*:

| conjunct | type | independently recomputable? |
|---|---|---|
| `O(E_1) ≠ O(E_2)` | existential, finite | **yes** — a genuine certificate |
| `E_1, E_2` are generic-model-indistinguishable | universal over all generic algorithms | **no** — nothing to recompute |

An independent verifier can only *re-apply the definition it was given*. Since the definition
is never stated in the frozen text, constructor and verifier necessarily share it — and a
shared wrong definition passes both paths. "Independent code" buys implementation
independence, never semantic independence. Who writes the code is not the binding constraint;
where the definition lives is.

The specification also contradicts itself on the mechanics: `module_interface` puts
`verify_witness` **inside** the test module, while `witness_verification_method` requires
re-verification "not the test module's own path."

---

## 4. Two concrete scenarios where the protocol returns the wrong verdict

The handoff asks for at least one. Both directions are reachable, and both leave the control
gate reading 4/4.

### Scenario A — **SIMULABLE for an oracle that is not O(1)-simulable** (endomorphism)

The frozen `expected_basis` is:

> "The endomorphism is public and computable from the curve parameters (part of the generic
> model's public setup), hence simulable."

The inference *public ⇒ simulable* is false in Shoup's model. An algorithm holds **opaque
labels**. Being able to write φ as a rational map on affine coordinates does not let you
apply it to a label — that would require inverting the encoding. The real question is:
given only the label of `P`, produce the label of `φ(P)`.

On the prime-order subgroup, φ acts as multiplication by an eigenvalue λ (for GLV j=0 curves,
λ² + λ + 1 ≡ 0 mod n). λ is a residue mod n and is **generically full-size** — GLV's speedup
comes from decomposing `k = k₁ + k₂λ` with small `k_i`, *not* from λ being small. A generic
algorithm reaching only `{c·P}` for `c` in a set of size ≤ 2^t after t operations therefore
needs **Ω(log λ) = Ω(log N)** group operations to produce `λ·P`.

*(Offered as a derivation-level counting argument for independent checking, not as a theorem.)*

So under the specification's own N-independence requirement, this oracle is **not**
O(1)-simulable. The protocol nevertheless returns SIMULABLE, because:

1. The `expected_basis` licenses exactly the wrong inference, and it is in the test's input.
2. The overhead-growth check that should catch it is **disabled by definition**: C is
   *"counted statically from the construction"*, so it is a property of the construction, not
   of the instance. It cannot vary across 8/12/16-bit curves. `overhead_growth_check` compares
   a constant to itself three times and reports "stable" unconditionally.
3. No control exercises the overhead branch, so the gate still reads 4/4.
4. H-GGM-001 falsifier 4 ("C grows with N") was demoted by
   `analysis_methodology.overhead_growth_check` from a *falsification* to a *reclassification*
   the protocol absorbs.

Then `claim_tier_basis` promotes that SIMULABLE verdict to a **scale-independent
derivation-level closure at exponent 1/2** — resting on an overhead bound that was never
measured and is wrong.

The **incidence oracle** is the same failure a second time: its own stated basis is that
decompositions are found by "summing factor-base points and comparing to R," which costs
Θ(B^m) sums and equality tests under the model's own accounting. That exceeds `C ≤ 10` for
any B ≥ 4 at m = 2, and is not a constant. `expected_verdict: SIMULABLE` contradicts the
overhead threshold frozen in the same file. Two of four augmented oracles fail the criterion
on their own stated bases.

### Scenario B — **NON-SIMULABLE for a simulable oracle** (jet, via the wording lever)

The frozen jet specification reads:

> "Query type (P, Q) -> (P+Q, eps*(P+Q)) in F_p[eps]/eps^2 … the first-order (dual-number /
> jet) part of the addition law."

Written in *that register*, the ε-block is affine coordinate data computed from the
coordinates of P and Q — **the same register as the encoding control's x-coordinate**, which
the specification declares to be the paradigm of non-simulability. Any witness procedure that
makes the `encoding` control return NON-SIMULABLE returns NON-SIMULABLE for this wording of
the jet oracle too, and the witness will check on all three toy curves (seeds 1, 2, 3),
satisfying `witness_robustness` cleanly.

Yet H-GGM-001's own mechanism, and KN-OPEN-005's kill argument, say the jet data is
*determined by* the zeroth-order solution — the ε-block is implied by the Zariski tangent
space. The apparent divergence would be an artifact of presenting the answer in coordinates
rather than as a basis-free tangent vector.

The **elliptic-net oracle** falls the same way. `W(a,b)` as frozen is a field value on a
concrete curve. Its stated basis — "Somos identities are universal" — establishes that the
values satisfy a curve-independent *recurrence*, not that the *values* are reconstructible
from group operations. Universality of the identities is not simulability of the values.

**The protocol has no third branch.** When the frozen wording and the frozen
`expected_verdict` disagree, there are exactly two paths:

- report the wording-driven verdict → the experiment **manufactures non-generic signals**,
  each of which then demands AGENTS.md rule-12 review-xhigh follow-up; or
- override the wording to match `expected_verdict` → **answer-key fitting**.

Nothing in the specification detects, records, or reports that the two diverged. H-GGM-001
`interpretation_limits` item 5 *concedes this exact lever* — and files it as a confounder to
be recorded rather than resolving it in the frozen text. For a test whose entire input is
wording, an unresolved wording dependence is not a confounder. It is the free parameter that
sets the answer.

**Net effect of Scenarios A and B together:** under the frozen text, the protocol plausibly
returns NON-SIMULABLE for jet and elliptic-net (against expectation, generating false
non-generic signals) *and* SIMULABLE for endomorphism and incidence (against their true
overhead, generating a false derivation-level closure) — with the control gate reading 4/4
throughout. The gate cannot see either error.

---

## 5. Decidability: the negative outcome is formally reachable, practically not

`falsification_criterion`: *"Any of the four controls is misclassified."*

**Formally decidable** — eight emitted verdicts against four expected values is a finite
comparison. That is better than designs whose criteria are not well-formed.

**Practically unreachable**, for a reason that is not evidence of soundness:

1. The four expected control verdicts appear in the frozen specification three times over
   (`expected_verdict`, `role`, and H-GGM-001 `predictions`).
2. The classification routine is not an algorithm (§6), so emitted verdicts are whatever the
   implementer encodes.
3. The implementer is *required* to read the file containing the answers.

The criterion fires only if someone builds a genuine decision procedure **and then gets one
of the four easiest oracles in the model wrong.**

The falsification set was also **narrowed relative to the hypothesis it is the sole test of**:

| H-GGM-001 falsifier | fate in EXP-GGM-001 |
|---|---|
| 1. DL control returns SIMULABLE | retained |
| 2. pure-generic / public-curve returns NON-SIMULABLE | retained |
| 3. no checkable witness producible | demoted to `alternative_outcome`, explicitly non-falsifying |
| 4. C grows with N | dropped; reappears as "reclassify as effectively non-simulable" |

The experiment is therefore **harder to falsify than the hypothesis it tests**.

This reproduces, in a different guise, the structural defect BATCH-004 found in EXP-IC-001
(REV-20260726-003, BO-5: tautological success criterion). Two consecutive designs in this
program have shipped a headline criterion that cannot fail. That pattern is worth the
Coordinator's attention independent of this package's fate.

---

## 6. The core routine is an undecidable search wearing an algorithm's clothes

> "the test attempts to express the oracle's answer as a function of (a) group-operation
> results and (b) equality tests, without reference to the concrete encoding. If the answer
> can be so expressed with a bounded number of group operations (counted statically from the
> construction), the query type is simulable."

The input is `computational_procedure`, defined as *"pseudocode or Python."* Deciding whether
an arbitrary program of that kind is extensionally equal to *some* program in a restricted
basis, over an unbounded domain (all primes p, all curves, all point tuples), is program
equivalence for a Turing-complete language. Undecidable in general; and even the positive
half is a universally quantified statement over an infinite domain, not a finite search.

Three consequences:

- **No third verdict.** The procedure can only ever report "my search found nothing," but the
  specification's branches are "can be so expressed" and "*provably* depends on
  encoding-specific data." Absence of a found simulator is silently promoted to
  NON-SIMULABLE — violating `docs/evidence-and-reproducibility.md` negative-result semantics
  and the spirit of AGENTS.md rule 5. And it is promoted in the *more consequential*
  direction, since NON-SIMULABLE is reported as a non-generic signal.
- **The output-type gap is never addressed.** A generic algorithm's outputs are group-element
  labels and equality-test bits. Six of the eight subjects have answers that are none of
  those — a ring element in F_p[ε]/ε², a field value W(a,b), a list of index tuples, an
  integer k, a coordinate in F_p. How a simulator may produce a non-group-element answer is
  *exactly where the question lives*, and the specification is silent.
- **What gets built is a lookup table.** With no algorithm available and the answers in the
  input, `classify_oracle(oracle_spec)` will dispatch on oracle name.

### The constructive fix

Replace free-form `computational_procedure` with a **closed answer-form grammar** and decide
*membership* rather than searching for a program:

```
answer_form ::= group_element(sle)
              | public_datum(name)
              | boolean(equality_test_expr)
              | integer_from_public(expr)
              | concrete_coordinate(...)      -- NON-SIMULABLE, encoding axis
              | external(...)                 -- UNDETERMINED, hand adjudication

sle         ::= input_i | sle + sle | c * sle   -- c a declared N-independent public constant
```

SIMULABLE **iff** the declaration parses into one of the first four productions **and** the
straight-line expression's operation count — with every scalar multiple `c` expanded to
`ceil(log2 c)` doublings plus additions, **not counted as one operation** — is ≤ C and
independent of N.

This is decidable, has a real negative branch, and counting scalar multiplication honestly is
precisely what catches Scenario A.

Add a third verdict **UNDETERMINED** so a failed or out-of-grammar analysis has somewhere to
go other than NON-SIMULABLE.

---

## 7. The claim-tier argument, in the narrow slice that gates execution

*(TASK-20260726-006 owns the deep attack on `claim_tier_basis`; recorded here only insofar as
it bears on whether v1 may be executed.)*

**What is right:** an explicitly exhibited O(1) simulator plus Shoup's theorem *is* a
scale-independent argument, and `docs/claims-and-verification.md` already supplies the right
label — `proof_status: derivation`, *"a checkable argument, not a machine-verified proof —
label it derivation, never proved."* The specification is correct that such a verdict is not
toy-tier *empirical* evidence.

**Four defects in how it cashes that out:**

1. **`claim_tier` and `proof_status` are conflated.** `claim_tier` is a function of instances
   tested; `proof_status` is artifact strength. `claim_tier_basis` uses the latter to lift the
   former off `toy`, while the doc states derivation-level status *"does not relax the ceiling
   above."*
2. **Shoup's qualifier is dropped.** "Closes the candidate at exponent 1/2" appears
   unconditionally in both `objective` and `claim_tier_basis`. The bound constrains **generic**
   adversaries. KN-TECH-005 says so in terms: *"The bound is a barrier, NOT a proof that no
   non-generic attack exists."* A SIMULABLE verdict closes the candidate *within the model*,
   not as a research direction.
3. **The interpretation is pre-committed.** `analysis_methodology.scale_independence_note`
   *requires* analysis.md to assert scale-independent closure for each SIMULABLE verdict —
   written into the contract before any verdict exists. A frozen protocol may pre-commit
   metrics and decision rules; pre-committing the *interpretation of a result not yet
   obtained* is the same defect as pre-committing the expected verdicts, and it compounds with
   Scenario A: the one verdict most likely to be wrong is the one the protocol pre-authorizes
   the strongest language for.
4. **Toy curves are load-bearing, not decorative.** `claim_tier_basis` says they "serve only to
   make witnesses concrete." For every NON-SIMULABLE verdict the witness **is** the entire
   basis, so 8–16 bit realizations carry the claim, and such a verdict is toy-tier unless the
   indistinguishability argument is supplied in general form.

---

## 8. What survives

The attack above is on the protocol, and the protocol is repairable. What survives intact:

- **The question is the right one.** KN-TECH-005 and KN-OPEN-005 both identify GGM
  simulability as the cheapest decisive screen for this program's representation candidates.
  Screening before spending compute is correct methodology.
- **Gating is the right architecture.** Soundness controls first, augmented verdicts only if
  the gate passes. The defect is *which* controls and *where the answer key sits* — not the
  idea of gating.
- **Run-integrity discipline is correct.** `invalidation_rules` explicitly hold that control
  misclassification is **not** an invalidation but a scientific result, and `stopping_rules`
  classify crashes as `failed_infrastructure`. Both comply with AGENTS.md rule 5.
- **Scope hygiene is good.** No crypto-scale target, no live key, an explicit statement that
  the test covers specifications rather than implementations, and an explicit refusal to claim
  KN-OPEN-001 is settled.
- **The authors saw the sharpest objection.** `interpretation_limits` item 5 names the wording
  lever exactly. The failure was filing it as a confounder instead of resolving it in the
  frozen text.
- **Nothing has been executed.** Status is `review_required`, `approved_by: null`. Every defect
  above is still cheap to fix. That is why the verdict is REVISE and not FAIL.

---

## 9. The single next action

Open **one** Coordinator-authored design-revision task for **EXP-GGM-001 v2** in a separately
budgeted successor campaign, addressing BO-1 … BO-8 in order. Authorize no implementation and
no execution of v1.

| # | requirement |
|---|---|
| a | Seal the eight expected verdicts into a separate withheld, separately hashed file |
| b | Add the three boundary control classes (§2.3) — a control on each side of each axis |
| c | Split the verdict onto an **encoding-dependence** axis and a **query-overhead** axis, with a distinct witness type per axis |
| d | Define the witness as an **equivariance failure**, with a finite third-party-checkable indistinguishability predicate stated in the frozen text |
| e | Replace free-form `computational_procedure` with the closed answer-form grammar (§6) plus an **UNDETERMINED** verdict |
| f | Measure C **dynamically**, with scalar multiplications expanded; re-derive the endomorphism and incidence expectations under the corrected criterion |
| g | Restore all four H-GGM-001 falsifiers as experiment falsifiers; delete the reclassification escape hatch |
| h | Replace the pre-committed scale-independence note with neutral reporting; set `claim_tier` from tested instances, carry scale-independence via `proof_status: derivation` |

**First unmet obligation** (per BATCH-006 `negative_branch`): *the control gate cannot
discriminate a sound test from an unsound one, because its answers are inside its input and
its controls are all extremal.*

---

*No record status was changed. No execution was authorized or performed. Nothing was committed.
This review endorses no crypto-scale, breakthrough, or universal-impossibility claim. Toy scale
stays toy scale.*
