# A3 — ECDLP representations and tracked objects (catalogue, 2026-08-05)

Slice: alternative curve models/coordinates; oracle families and generic-group
simulability; elliptic nets; jets; incidence structures; quiver/path-algebra word
search; transfer operators of the translation walk; and the attack-family
**taxonomy** question. Anchors: `KN-OPEN-005`, `KN-OPEN-008`, `KN-OPEN-010`,
`KN-OPEN-019`.

**Status of every entry below: proposal-stage only.** No experiment ran, no ID was
minted, no research state moved, no ECDLP improvement is claimed anywhere in this
file. Novelty is **not adjudicable in this session**: nothing here is asserted new
and nothing here is dismissed as known.

## Standing constraints this catalogue is written against

1. **`KN-FIND-002` / `EV-GGM-001`** record jet and endomorphism oracles as
   GGM-simulable at O(1), closing those families at exponent 1/2 by theorem, and
   elliptic-net (O(log N)) / incidence (O(B^m)) as simulable at non-constant
   overhead — not closed at 1/2, but giving no sub-birthday advantage. **No idea
   below re-proposes any of those four oracles as an advantage.**
2. **`EV-GGM-002`** found the *executed* simulability module was a serializer of
   eight hardcoded verdicts, with a control gate carrying zero degrees of freedom;
   the run set is evidentially VOID. The theorem stands; the run does not. An
   honest re-execution with a control that can fail is legitimate (A3-2).
3. **`EV-ENDO-001`** (contradicts, strong): for the frozen eigenvalue multiset
   {1, λ₂, λ₃} with λ² + λ + 1 ≡ 0 mod N, Vieta forces (1,1,1,0,…) into W_r, so the
   infinity-norm first minimum is EXACTLY 1 and the predicted N^(1/(2r)) is FALSE
   on those cells. **Not re-proposed anywhere below.**
4. **`EV-STR-003`** withdrew the comparative limb of the displacement-rank result
   and left `phi_alpha` **UNADJUDICATED**; `EV-STR-004` returned `mixed` with the
   IL0 truncation reading still available. Adjudicating it is a live target (A3-8).
5. **`KN-OPEN-019`**: the ECDLP has no object-indexed attack taxonomy, so every
   saturation conclusion this program has reached is a statement about its SEARCH.
   The symmetric round-function framing does not obviously port. A3-6 is the
   deliberate attempt at a real enumeration with a real closure argument.
6. **SageMath is unavailable and uninstallable.** Every idea below is executable in
   CPython + `numpy`/`sympy`, or states its Sage-free fallback explicitly.
7. Baseline is Pollard rho at ≈0.886·√N group operations with O(1) memory
   (parallelizable with linear speedup); BSGS at ≈√N time and √N memory;
   prime-field index calculus has **no known advantage**. Preprocessing frontier
   ST² = Õ(N); multi-target frontier √(LN).

## A logical gap this catalogue exploits (stated once, used by A3-1/A3-2/A3-3)

`KN-FIND-002` reaches its O(1)-simulability verdicts in a **structured GGM** where
the curve equation and point coordinates are public (its own scope note says so:
"Under the strictest Shoup GGM, jet and endomorphism would be NON-SIMULABLE
because they require coordinate access"). But the Ω(√N) bound it invokes
(`KN-TECH-005`, Shoup) is proved in the **opaque-label** model, in which
coordinates do not exist. So "SIMULABLE (with coordinates) ⇒ closed at exponent
1/2 (a bound proved without coordinates)" is a **model switch inside one
inference**, and `EV-GGM-002` independently records that the model variant was not
held fixed across oracles ("Which model any given verdict was reached under is
therefore not recoverable from the artifact"). The correct home for
coordinate-visible oracles is the *structured* generic-group model of `KN-LIT-7606`
(Corrigan-Gibbs–Henzinger–Wu 2026), which parameterises non-genericity by the
fraction δ of group elements whose structure is exploited and reports
Ω(min(√q, 1/δ)). A3-1 and A3-3 are the two cheap moves that either repair this
inference with a cited theorem or expose that it does not close what it claims.
This is a gap in an *argument*, not an error in a *fact*, and either outcome is
decision-relevant.

---

## Ideas

### A3-1. The δ-mass screen: re-price every corpus representation inside the structured generic-group model, and find where the two-sided squeeze on |structured set| actually bites

**Claim.** For each representation family in the corpus, the *exploited-structure
set* S ⊆ G (the elements at which the augmented oracle's answer is not a function
of the generic transcript) has a computable density δ = |S|/N, and `KN-LIT-7606`'s
reported Ω(min(√N, 1/δ)) turns the binary question "simulable?" into an exponent.
Sharp prediction, stated in advance: a prime-field factor base of size B = N^(1/2)
gives δ = N^(-1/2), hence 1/δ = N^(1/2) — the bound is **exactly tight at the rho
exponent**, which is a model-internal account of why prime-field index calculus has
no advantage. Therefore any representation that beats 1/2 must carry
δ > N^(-1/2), i.e. a structured set of size *strictly more than* √N; and a set of
size > √N cannot be enumerated within a sub-√N budget, so it must additionally
have a succinct description. That two-sided squeeze — δ from below by the lower
bound, description-degree from above by the solve cost — is the deliverable.

**Mechanism / tracked object.** The tracked object is **the structured subset S
itself**, carried as a pair (δ, description complexity). This is a lossy
projection of a representation: it discards *what* the oracle says at each point of
S and retains only *how many* points it says anything non-generic about, and that
retained scalar propagates through composition of oracles (S₁∪S₂ under
conjunction), which is what the lower bound consumes. It is not a change of
coordinates: two representations with the same δ can have entirely different
answers, which is exactly the observation-collision the design must probe.

**Minimal discriminating test.** (i) Literature deep-read of `KN-LIT-7606` body —
**blocking**, because `KN-LIT-7606` itself records "Full text was not read" and
"Whether the paper's elliptic-curve-point result covers the *specific* augmented
oracles in `KN-FIND-002` was **not** determined." (ii) Write S and δ in closed form
for: x-only/Kummer coordinates, alternative curve models, jets, elliptic nets,
incidence reporting, endomorphism orbits, quiver word evaluation, transfer-operator
cells, and the coordinate-box factor base. (iii) Tabulate log_N(δ) against −1/2 and
against `IDEA-20260801-021`/`IDEA-20260803-e2f5bd`'s description-degree window,
which is the same squeeze approached from the algebraic side.

**Null object / control.** The **coordinate-box factor base at B = N^(1/2)**, whose
δ = N^(-1/2) is known and whose algorithm is known to have no advantage: any screen
that scores it as promising is void. Second control: the **full group** S = G,
δ = 1, which the bound must score as vacuous (min(√N, 1) = 1) — a screen that does
not degrade to vacuity there is misreading the theorem.

**Falsifier (reachable).** (F1) The deep read shows the structured GGM's δ-structure
is defined over *sets of group elements with algebraic relations* and does not cover
pointwise coordinate functions → **screen void**, recorded as such, and
`KN-FIND-002`'s inference gap (see above) is left standing rather than repaired.
(F2) Some corpus family has δ > N^(-1/2) with a poly-size description → that family
is **not** screened out and the two-sided squeeze has a gap at a named place.
(F3) The factor-base calibration does not come out at exactly −1/2 → my reading of
the model is wrong and nothing is read.

**Cost.** Implementation: none (paper). Compute: none. One reading session plus a
derivation table.

**Ceiling.** This is a **screen and a repair, not an attack**; it moves no exponent
by itself. Its best case is converting several ad-hoc "simulable ⇒ closed" verdicts
into one cited theorem with a quantitative parameter, and naming the exact δ-region
where a representation could still live.

**Kills-it-early.** If the deep read shows the paper's ECDLP-point result already
covers jets/nets/incidence explicitly, then `KN-FIND-002` has no residue, this idea
collapses to a citation, and its honest disposition is `known` — which is a fine and
cheap thing to discover before spending anything.

---

### A3-2. Re-execute the simulability classification as a *measurement*: transcript-indistinguishability decided by enumeration, with a mutation ladder that must move the verdict

**Claim.** Simulability is decidable by brute force at toy scale, and therefore the
verdicts of `EXP-GGM-001` can be *measured* rather than asserted. Definition made
operational: fix a toy group G ≅ Z/n with a random encoding τ: G → labels. An
augmented query type q is **simulable at overhead C** iff for every pair of
instances that produce identical generic transcripts under all C-step extensions of
the query sequence, q's answers agree. At n ≤ 2^12 with C ≤ 3 this is a finite
enumeration. Prediction: the classifier reproduces at most some of the eight
`EXP-GGM-001` verdicts and **necessarily disagrees on at least the two whose model
variant `EV-GGM-002` found unrecoverable** (jet, endomorphism), because their
recorded verdicts were reached under a coordinate-visible model while the
transcript definition is coordinate-free.

**Mechanism / tracked object.** The tracked object is **the generic transcript** —
the sequence of equality/collision patterns among queried labels. It is genuinely
lossy: it discards every label value and retains only the incidence pattern of
equalities, and that pattern propagates deterministically through group operations
(the pattern after one operation is a function of the pattern before, by
construction of the model). An oracle is simulable exactly when its answer
factors through this projection. This is the lossy-projection test *applied to the
GGM itself* rather than to a curve object.

**Minimal discriminating test.** Implement three components `EXP-GGM-001` declared
in `implementation_requirements` and never built (per `EV-GGM-002`: "No parser,
simulator constructor, overhead checker or witness generator exists"): a spec
parser, a transcript enumerator, and a witness generator that returns an explicit
indistinguishable pair with differing answers on a NON_SIMULABLE verdict. Run over
the eight subjects with the model variant **frozen and stamped into every raw
result**, once under opaque-label Shoup and once under the structured
coordinate-visible model, and report the 8×2 table.

**Null object / control.** Three controls with **free variables**, repairing the
exact defect `EV-GGM-002` names ("The comparison contains no free variable, so
controls_correct == 4 on every possible execution"): (a) a random-function oracle,
which must come out NON_SIMULABLE and must yield a printed witness pair; (b) the
identity oracle, SIMULABLE at C=0; (c) a **mutation ladder** — a one-parameter
family of oracles interpolating from "answer is a function of the transcript" to
"answer is a function of the label", whose measured verdict must flip somewhere
along the ladder and whose measured C must increase monotonically.

**Falsifier (reachable).** (F1) The ladder does not move the verdict → the
classifier is void, no subject is read, and the honest report is an instrument
outcome (this is the specific way the predecessor failed and it must be able to
happen again). (F2) The witness generator cannot produce a witness for the
random-function control → the NON_SIMULABLE branch is unsound. (F3) An oracle
recorded SIMULABLE in `KN-FIND-002` measures NON_SIMULABLE under opaque-label
Shoup → the recorded closure is carried by the *structured* model only, which is
precisely the gap A3-1 prices.

**Cost.** Implementation: medium (three real components, no Sage — pure CPython).
Compute: low; enumeration at n ≤ 2^12, C ≤ 3 is minutes, and the budget must be
declared per subject with a hard cap so that a cap hit is reported as a cap hit.

**Ceiling.** Decides an **instrument**, not a mechanism. Even a full clean pass
moves no exponent and asserts nothing about crypto scale; it converts a void run
into a real one and pins which GGM variant each verdict lives in.

**Kills-it-early.** If the transcript enumeration's state space blows up before
C = 2 at n = 2^10, the decision procedure is not finite in practice at any useful
overhead, and the whole "machine-checkable simulability test" framing — not just
the previous implementation — is the thing that fails. Report that and stop.

---

### A3-3. Twist weight as the lossy-projection test for oracle answers: does the oracle output transform as a section of a line bundle, and what does that decide?

**Claim.** Every corpus oracle answer can be assigned an integer **weight** w under
the Weierstrass isomorphism (x, y) → (u²x, u³y), which sends E_{a,b} → E_{a/u⁴,
b/u⁶} and the invariant differential ω = dx/2y → u^(-1)ω. Three-way dichotomy,
pre-registered: **w = 0** ⇒ the answer is an isomorphism invariant of the group
element ⇒ it is a function of (group element, j-invariant) and carries nothing
about k beyond the group law; **w ≠ 0 but homogeneous** ⇒ the answer depends on the
chosen model only through a public scalar u^w, which is normalizable away by fixing
a model, so again nothing about k; **not weight-homogeneous** ⇒ the answer mixes
weights, is not a section of any single line bundle, and is the only case that can
carry model-independent extra information. Prediction: jet, endomorphism, net and
transfer-operator-cell answers are all weight-homogeneous, and the interesting cell
of the table is empty — or it is not, and that entry is the object worth work.

**Mechanism / tracked object.** The tracked object is **the weight vector of the
oracle's output under the twist torus F_p\***. Lossy: it discards the entire value
and retains one integer per output coordinate. Compatible: twisting is a group
isomorphism, so it commutes with the group law, and the weight of a sum is
determined by the weights of the summands — the retained integer propagates
deterministically through exactly the operation the target exposes. A weight
computation loses everything except the scaling exponent, which is the definition
of a genuinely lossy projection rather than a change of coordinates.

**Minimal discriminating test.** Pure algebra, no compute: for each of the eight
`EXP-GGM-001` subjects plus the alternative-model coordinates of A3-7, substitute
(x, y) → (u²x, u³y), (a, b) → (a/u⁴, b/u⁶) and read off the u-degree of the output.
Then run the **Weierstrass-twist invariance check on the jet oracle specifically** —
pre-registered twice already (`RT-20260726-001`; `REV-20260727-002` BO-3) and, per
`EV-GGM-002`, **never run** — to settle which of its two readings is frozen
("return the ε-coefficient of P+Q", encoding-dependent, versus "return the
derivative of the addition map", a universal identity). Numeric confirmation on a
toy curve at 2–3 values of u costs seconds.

**Null object / control.** (a) The x-coordinate itself, whose weight is exactly 2 —
a known answer the calculation must return. (b) The j-invariant, weight 0. (c) A
deliberately weight-inhomogeneous synthetic oracle (e.g. x + y), which the
instrument must classify into the third cell; if it cannot, the third cell is
unreachable by construction and the dichotomy is untestable.

**Falsifier (reachable).** (F1) The jet answer is twist-*invariant* → it is a
universal identity, `KN-FIND-002`'s jet closure is strengthened and stated with a
mechanism instead of an assertion. (F2) The jet answer is twist-*covariant with
nonzero weight* → the recorded C=1 verdict was reached by applying a coordinate
formula that the opaque-label model forbids, exactly as `EV-GGM-002` boundary item 5
suspects, and the verdict is structured-model-only. (F3) Some subject is
weight-inhomogeneous → the dichotomy fails as a classification and that subject is
promoted to its own question.

**Cost.** Implementation: low. Compute: negligible (minutes; CPython + sympy).

**Ceiling.** **Moves no exponent, not even a constant.** It is a screen whose whole
value is deciding which generic-group model each corpus verdict lives in, and
thereby deciding whether A3-1's δ-repair is needed. It is the cheapest item in this
catalogue.

**Kills-it-early.** If every subject lands at w = 0, the table is uniform, the
dichotomy separates nothing, and the twist action is simply not a discriminating
symmetry for this family of oracles — record and move to the scalar/translate
actions of A3-6, which are the ones that act on k.

---

### A3-4. Break the ± fold: a sign-splitting partition for the translation-walk transfer operator, to decide whether `KN-OPEN-010`'s barrier is the negation quotient or character orthogonality

**Claim.** `EV-TRA-001` recorded an unexpected structural observation — all 54 exact
coarse operators were *exactly reversible* (detailed-balance residual 2.5e-17) with
entirely real spectra (max |Im λ| = 3.7e-16), because for negation-symmetric
x-interval partitions "the k-encoding character phases are destroyed structurally by
the ± fold, not merely statistically" — and recorded the matching confound
explicitly: "non-negation-symmetric partitions and multi-mode estimators untested."
CLAIM: a partition by (x-interval, sign of y) is **not** negation-symmetric, so its
coarse operator is non-reversible with a genuinely complex spectrum (predicted
detailed-balance residual > 1e-3 relative and max |Im λ| > 1e-2), and this
**removes the recorded structural obstruction while leaving the statistical one
intact**. The localization exponent δ in L_eff ∝ n^δ is then measured against
`EV-TRA-001`'s x-cell value of **δ = 0.0195**, at the same sizes, the same estimator
family, and the same budgets S ∈ {n^(1/4), n^(3/8)}.

**Mechanism / tracked object.** The tracked object is **the coarse cell occupation
measure of the translation-by-P walk under a partition that distinguishes P from
−P**. Lossy: ≈N/C group elements collapse to one cell index. Compatible in the
required weak sense: translation by P maps cells to cells *stochastically*, and the
transfer operator IS that propagation — the object's propagation law is the very
matrix being estimated, which is what makes it measurable rather than argued.

**Minimal discriminating test.** Two arms at each of three sizes: **arm X** = the
frozen x-interval partition (reproduces `EV-TRA-001` exactly, cell for cell — a
baseline-reproduction audit, not a similar-looking plot), **arm S** = the
sign-split partition with the same C. Report, per arm: detailed-balance residual,
max |Im λ|, λ₂, L_eff mean and median against the chance floor, and the fitted δ.
The single decisive number is δ(S) − δ(X).

**Null object / control.** (a) The **random-permutation negative control** already
frozen in `EXP-TRA-001` (measured hit ratio 0.993), rerun under the sign-split
partition — any localization surviving it is estimator artifact. (b) The **positive
control at C = n**, which must still recover k exactly. (c) A **shuffled-sign
control**: assign the y-sign bit uniformly at random per point, preserving cell
cardinalities and destroying the algebraic sign structure; this separates "the
operator became non-reversible" from "the operator became non-reversible *for a
reason connected to the curve*".

**Falsifier (reachable).** (F1) δ(S) ≈ δ(X) ≈ 0 with complex spectrum present →
the ± fold was **not** the obstruction; the barrier is character orthogonality
proper, and `KN-OPEN-010` upgrades from "strong expectation, unproven" to a
measured barrier with its named confound removed. (F2) δ(S) > 0.05 sustained across
three sizes AND absent on both nulls → live, and routed to independent review
before it is described anywhere. (F3) The sign-split operator is *also* exactly
reversible → my structural prediction is simply wrong and the reversibility has a
cause I have not identified, which is itself the finding.

**Cost.** Implementation: low (the `EXP-TRA-001` estimator exists; the change is the
partition function). Compute: low — toy primes to ≈2^12–2^14, dense C×C operators
with C ≤ 256, CPython + numpy, single-digit CPU-hours with a hard cap.

**Ceiling and GGM position, stated plainly.** The cell index is a function of the
affine coordinates, so as an *oracle* this object is simulable at O(1) in the
structured model — it is on the **closed side** of the O(1) line by
`KN-FIND-002`'s own argument (subject to A3-3's model audit), and **it cannot beat
exponent 1/2 as an oracle**. Its value is therefore not an advantage but a
**measured barrier with the recorded confound removed**, and the honest expected
outcome is F1. Priority is set accordingly.

**Kills-it-early.** If arm X fails to reproduce `EV-TRA-001`'s committed numbers
cell for cell, the instrument is not the frozen one and nothing else is read.

---

### A3-5. Non-affine arrows: does the quiver collapse survive a second vertex? (`THM-COMMUTATOR-KERNEL1` gaps G1 and G3)

**Claim.** `THM-COMMUTATOR-KERNEL1` proves that for the single-vertex
translation/negation quiver on a prime-field cyclic G, the evaluation kernel is
generated by commutators, forced dihedral torsion and the commutative subset-sum
lattice — at any B, any factor base, any word degree, any n — so word order can only
**prune** the commutative shadow set, never extend it, and `KN-OPEN-008`'s
commutator-collapse obstruction is a theorem there. The theorem names its own
structural cause (§G3): "on a cyclic group every group endomorphism is scalar
multiplication, so {translations} ∪ {automorphisms} always act affinely", and names
the only escapes: **G1** multi-vertex/groupoid quivers and **G3** arrows acting
non-affinely. CLAIM: the two-vertex quiver with vertex 0 = G, vertex 1 = degree-m
effective divisors (unordered m-tuples of x-values), arrows = per-coordinate
translations and the S_m coordinate permutations at vertex 1, the summation
correspondence split: G ⇸ vertex 1, and the sum: vertex 1 → G, has a shadow group
that is **not** metabelian-with-commutative-translation-lattice, and the collapse
argument's normal-form step therefore does not go through as written.

**Mechanism / tracked object.** The tracked object is **the word** — the ordered
sequence of arrows, i.e. the order of operations, projected to its shadow. Lossy:
the shadow (ε, a) discards the word entirely and retains a signed exponent vector.
The theorem's content is that at one vertex this projection loses **nothing that
matters** (Lemma 1: "the action and the orbit value of a word depend only on its
shadow") — which by the lossy-projection test means the one-vertex word is a change
of coordinates, not an object. The two-vertex question is whether the analogous
projection still exists: if the S_m permutations at vertex 1 do not descend, there
is no shadow homomorphism and the word is a genuine object.

**Minimal discriminating test.** Two stages, cheapest first. **Stage 1 (derivation,
no compute):** attempt the Theorem-1 normal-form argument on the two-vertex
groupoid. Either produce the shadow homomorphism (collapse extends; G1/G3 partially
discharged with a mechanism) or exhibit the precise step that fails. **Stage 2
(only if Stage 1 fails to collapse):** the exact control `EXP-NCP-001` used —
value-set inclusion S_nc(d) ⊆ S_comm(d) on full histograms — at toy p, m ∈ {2,3},
B ∈ {4,8}, degree ≤ 6. At one vertex that control was **algebraically guaranteed to
pass** (Corollary 1). At two vertices it **can fail**, and a single violation is the
positive signal.

**Null object / control.** (a) Re-run the one-vertex quiver as a positive control:
inclusion must hold with 0 violations, reproducing `EV-NCP-001`'s 94,472 shadow
replays, and the degree-6 value-set count must match the Corollary-2 formula (350
of 439 at p=431, B=4, n=439). (b) A **null second vertex**: replace the summation
correspondence by a random m-to-1 map with the same fan-out, giving a two-vertex
quiver with no curve content — if that also breaks inclusion, the break is
combinatorial fan-out, not geometry.

**Falsifier (reachable).** (F1) Stage 1 produces the shadow homomorphism → collapse
extends, `KN-OPEN-008` closes further with a named mechanism, and the quiver lane's
remaining escape is only G1's isogeny-graph groupoid. (F2) Stage 2 shows inclusion
holding at 0 violations across all cells → scoped negative, as before, now at two
vertices. (F3) Inclusion breaks but the null second vertex breaks it identically →
the effect is fan-out, not structure.

**Cost.** Implementation: medium. Compute: low–medium; Stage 1 is paper. **Sage-free
note:** `EXP-NCP-001`'s instrument was a `.sage` file and Sage is unavailable — the
word search and the affine evaluation are elementary integer arithmetic mod n and
must be reimplemented in CPython, with the one-vertex positive control serving as
the port-correctness check against committed numbers.

**Ceiling, stated bluntly.** Even full non-collapse **moves no exponent by itself**,
because the split arrow is exactly a summation-polynomial solve and costs what index
calculus already pays; the honest ceiling is a *relation-class* statement, and any
cost claim must be charged against the B^m decomposition search. There is a real
risk this object is index calculus in quiver notation, and that risk is why Stage 1
is a derivation and Stage 2 is gated behind it.

**Kills-it-early.** If the S_m permutations at vertex 1 descend to the shadow (which
they may, since the summation polynomial is symmetric), the shadow homomorphism
exists immediately and Stage 2 is never run.

---

### A3-6. An object-indexed ECDLP taxonomy from **equivariance under the self-reduction group**, with a sharp-2-transitivity closure argument — the `KN-OPEN-019` attempt

**Claim.** The symmetric-side taxonomy is indexed by "what survives one round"; the
ECDLP has no rounds, and this catalogue's proposal is that the right invariant is
**what symmetry of the instance the tracked object respects**. Concretely, for
n prime the random self-reduction group acting on the index is
AGL(1, Z/n) = {k ↦ tk + c}, which is **sharply 2-transitive** on Z/n. Hence:
**THEOREM-SHAPED CLAIM (T1): any tracked object invariant under both the scalar and
the translation action is constant across all instances with the same (E, P), and
therefore carries exactly zero information about k.** Corollary-shaped claim (T2):
an object *equivariant* under all of AGL(1, Z/n) is a generic object and Shoup's
Ω(√N) applies to it; **an algorithm below 1/2 must break equivariance under at
least one of scalar or translation**. Enumeration claim (T3): a computable
projection's stabilizer is a subgroup of AGL(1, Z/n), and for n prime those
subgroups are exactly {1}, the translations Z/n, the multiplicative subgroups H_r
for each r | n−1, and the subgroups containing translations — so **the stabilizer
lattice is the divisor lattice of n−1 plus two degenerate ends, which is a finite,
explicitly computable enumeration.**

**Mechanism / tracked object.** The tracked object is a projection π of the instance
state; the *classifying data* is π's **stabilizer subgroup** in
AGL(1, Z/n) × (twist torus) × (End(E)). This is itself a lossy projection of the
projection: it discards π's values and retains only which symmetries fix it, and it
propagates because stabilizers compose (the stabilizer of a composite is the
intersection). Placement of the known families, offered as this record's own sketch
and **not** as a verified taxonomy: F1 rho/BSGS tracks (element, known
representation aP+bQ) and is **fully AGL-equivariant** — which is why it is generic
and why √N binds it; F2 index calculus tracks a relation vector over a
**coordinate box**, and a box is *not* preserved by k ↦ tk, so index calculus is
exactly the family that **breaks scalar equivariance**; F3 isogeny methods break
**model/curve** equivariance; F6 endomorphism-orbit methods have stabilizer
⟨λ⟩ ≤ H_r; the multiplicative-coset index object of `IDEA-20260802-006` has
stabilizer H_r and thus already occupies a named cell of this lattice — which is
evidence the frame is generating rather than merely relabelling.

**Minimal discriminating test.** Entirely paper, plus a small verification script.
(i) Prove or refute T1 and T2 (T1 is a two-line consequence of transitivity; T2
requires care about what "generic" means for a coordinate-visible algorithm and is
where it may fail). (ii) Write the stabilizer lattice for a toy n and place F1–F7
plus the corpus's live candidate objects into it, recording for each the exact
action that is broken. (iii) Enumerate the **empty cells** — divisors r of n−1 with
no known family — and state, per empty cell, what an object living there would have
to look like. (iv) Verification script: for a toy curve, for each claimed
equivariance, check π(g·s) = ρ(g)·π(s) numerically on 10^4 random instances; a
claimed equivariance that fails numerically was mis-assigned.

**Null object / control.** (a) A projection with **known** stabilizer — π(k) = k mod
r for r | n−1 is stabilized by nothing in the scalar action but by the translations
by multiples of r; the script must recover that. (b) A **random** projection, whose
stabilizer must come out trivial; if the instrument assigns it structure, it
manufactures stabilizers. (c) The **generic-group transport** control: recompute
every stabilizer on Z/nZ with a random relabelling; any family whose stabilizer is
unchanged is carrying no elliptic content, which is the attribution failure
`DEC-20260801-003`/`EV-DS-003` recorded for the degree-split lane.

**Falsifier (reachable).** (F1) Some known family has **no well-defined stabilizer**
— its defining projection is not equivariant under any subgroup, not even trivially,
because it is not a function of the instance at all → the frame fails, and that is
`KN-OPEN-019` outcome 1: record the failure and close the entry. (F2) T2 is false as
stated because a fully-equivariant object can still exploit coordinates (a concrete
counterexample would be decisive and is actively sought) → the closure argument
collapses to T1 alone, which is much weaker. (F3) Two families with **different**
known power land in the **same** cell → the classification is not identifying, which
is a direct observation-collision falsifier and must be reported as one.

**Cost.** Implementation: low (a few hundred lines of CPython). Compute: negligible.

**Ceiling.** **Zero on every ECDLP cost axis.** The deliverable is methodological:
if T1–T3 survive, this program obtains, for the first time, a saturation statement
that is an *argument over an enumerated index set* rather than a tally — which is
exactly what `KN-OPEN-019` says it currently cannot produce, and exactly what
`docs/inventor-protocol.md` §4 demands of a closure. If they do not survive, the
program learns that its saturation conclusions must be justified some other way.
Neither branch is an attack and neither may be written as one.

**Kills-it-early.** If T1's transitivity argument is already implicit in the standard
random-self-reducibility of the DLP (it may well be — this is a literature-blocking
check), then T1 is `known` and the contribution reduces to T3's enumeration; say so
in the same sentence as the claim.

---

### A3-7. Is summation-polynomial degree a property of the *curve model* or a birational invariant of the summation correspondence? A closure test over the whole alternative-model class

**Claim.** Alternative curve models (Edwards, Montgomery, Hessian, Jacobi quartic,
level-2/4 theta, Kummer) are the standard answer to "change the representation", and
this catalogue's claim is that **for the ECDLP they cannot move an exponent, for a
statable reason**: the exponent-relevant quantity is the degree of the m-th
summation polynomial (2^(m−2) in each variable in Weierstrass, per the corpus at
`IDEA-20260727-006` and `IDEA-20260802-003`), and that degree is set by **the degree
of the quotient map used to define the factor-base coordinate**, not by the model.
Every listed model's natural coordinate is a coordinate on a **degree-2** quotient
of E (x on E/±; Edwards y is invariant exactly under (x,y) ↦ (−x,y) = negation), so
the degree is predicted **identical across all of them**. Point prediction that can
fail: symbolic S₃ and S₄ built in Edwards and in level-2 theta coordinates have the
same per-variable degrees as Weierstrass, and the same Bézout product.

**Mechanism / tracked object.** The tracked object is **the summation correspondence
S_m ⊂ (E/ι)^m** together with the degree d_ι of the quotient E → E/ι used to define
the coordinate. Lossy: it discards the model, the coefficients and the field, and
retains a single integer d_ι. Compatible: composing correspondences multiplies
degrees, so the retained integer propagates through the arity ladder
deterministically — which is why d_ι, and not the model, is the exponent-carrying
datum.

**Minimal discriminating test.** (i) Construct S₃ and S₄ symbolically in
Weierstrass, Edwards and level-2 theta coordinates over a toy prime, in `sympy`
(**Sage-free fallback**: resultant elimination via `sympy.resultant` on the
biquadratic addition relations, with the Weierstrass output checked against the
published S₃ as a fixture — a baseline-reproduction audit). (ii) Record per-variable
degrees and total degree. (iii) Additionally compute the **order-3 quotient** case:
on a j=0 curve, use the coordinate on E/⟨ζ₃⟩ (d_ι = 3) and check whether the degree
base moves from 2 to 3 — the prediction is that it moves **the wrong way** (larger
degree), which if confirmed converts the "use a bigger automorphism group" intuition
into a stated obstruction.

**Null object / control.** (a) The published Weierstrass S₃/S₄ as a frozen fixture —
if the pipeline cannot reproduce it, nothing else is read. (b) A **degree-1**
control: a coordinate on E itself (no quotient), where the "summation polynomial"
degenerates to the addition law and the degree must drop; this demonstrates the
statistic is capable of moving before any model is read.

**Falsifier (reachable).** (F1) Some model gives a **strictly smaller** per-variable
degree at the same d_ι → the birational-invariance claim is false and that model is
immediately interesting. (F2) All models agree, and the d_ι = 3 case is larger →
**closure over the alternative-model class with a named obstruction**: model change
is a change of coordinates on a fixed correspondence, and the degree is intrinsic to
the correspondence. (F3) The symbolic construction of S₄ does not terminate in
budget in the non-Weierstrass models → not measured, reported as not measured.

**Cost.** Implementation: low–medium. Compute: low, with a hard cap on the S₄
elimination (an uncapped resultant in three models is the realistic way this
overruns).

**GGM position.** A change of curve model is a public rational map, hence simulable
at O(1) in the structured model — so the alternative-model class is on the **closed
side** as an oracle, subject to A3-3's model audit, and this idea does not contest
that. What it adds is the *reason* stated as an obstruction over the whole class,
rather than model-by-model.

**Ceiling.** At most a **constant factor** on the positive side (faster field
arithmetic per group operation), which is real engineering and irrelevant to the
exponent. The deliverable is the closure with its mechanism.

**Kills-it-early.** If d_ι alone already predicts every published summation degree
(including the extension-field cases), the claim is arithmetic bookkeeping rather
than a discovery, and its honest status is `known`.

---

### A3-8. Adjudicate `phi_alpha` by removing the one nuisance variable both prior experiments left in: factor-base truncation across φ-orbits

**Claim.** `EV-STR-003` left the as-committed `phi_alpha` metric explicitly
**UNADJUDICATED** — "not shown to measure phi-invariance and not shown to be an
artifact" — and `EV-STR-004` returned `instrument_verdict: mixed` with all four
disagreeing cells in the direction A′ > E′ and with `UC-2` recording that this is
"consistent with truncation artifact (IL0) and not proven as endomorphism content".
Every disagreeing cell (`L25`, `L49`, `L97`, `A13M3`) is a **residue-1** cell. CLAIM:
the residue-dependence is caused by the `xs[:B]` truncation cutting a φ-orbit, and
therefore an **orbit-complete factor base** of size B′ = 3⌈B/3⌉ (no orbit ever cut)
makes the A′ > E′ disagreement vanish at every cell, at every residue class of the
*nominal* B. Falsified if the disagreement survives with the truncation removed, in
which case `phi_alpha` is carrying something the truncation reading does not explain
and the metric is adjudicated in the *other* direction.

**Mechanism / tracked object.** Per `EV-STR-003` O-4, α is "a phase-tracking
statistic of WHERE skips fall, not of how many there are." So the tracked object is
**the position sequence of orbit-boundary breaks in the row-emission stream** — not
the break count and not the displacement rank. This is a lossy projection of the
emission stream (it discards every row's content and retains the positions at which
the stream departs from a clean concatenation of σ-orbit triples) and it propagates
through the append rule deterministically, which is exactly the derivational limb
`EV-STR-003` O-6 recorded as CONFIRMED at 4 of 4 (equality at 3 of 4).

**Minimal discriminating test.** One-variable ablation with the base-row budget
matched by construction rather than by driver patch (repairing `EV-STR-004` `UC-1`):
arms A′ and E′ exactly as frozen in `specification.v3.yaml`, each run at nominal B
and at B′ = 3⌈B/3⌉, at the same fourteen cells. The decision variable is the size of
the F-4 disagreement set at B′ versus its committed value 4/14 at B. Also archive
`sha256` of the factor base and of the final row list per cell — `EV-STR-003` `UC-6`
notes this "would close this at no cost" and it has not been done, so an α is
currently reproducible by re-execution but not checkable from artifacts.

**Null object / control.** (a) Arm E′ itself is the phi-free null and is already
frozen. (b) **Residue control:** the same measurement at nominal B ≡ 0, 1, 2 mod 3
with B′ orbit-complete in all three — if the residue dependence persists after
truncation is removed, it is not truncation. (c) **Committed-baseline reproduction:**
arm A at instance I1 must still agree with `RUN-STR-phi-b12-s1-m2` on all five
compared fields (B 27, n 733, hits 15, attempts 27, phi_alpha 9).

**Falsifier (reachable).** (F1) Disagreement set → 0/14 at B′ → `phi_alpha` is
adjudicated as a **truncation artifact**, `EV-STR-003` `UC-1` is discharged, and the
displacement-rank lane closes as an instrument with a named mechanism. (F2)
Disagreement set unchanged → truncation is **not** the cause, `phi_alpha` survives
its sharpest artifact explanation, and the instrument question moves to the append
rule. (F3) The baseline reproduction fails → the port is wrong and nothing is read.

**Cost.** Implementation: low (the harness and both frozen arms exist; the change is
the factor-base builder). Compute: low — `EXP-STR-003` consumed 132.6 s of a 5400 s
budget at peak RSS 0.099 GB.

**Ceiling, stated bluntly.** Decides an **instrument**, not a mechanism. `EV-STR-003`
boundary 3 is explicit that "the only reproducible speedup measured anywhere in this
line of work is the classical constant factor r = 3 in relation collection (O-11)",
which is already the specialized baseline (Wiener–Zuccherato, Duursma–Gaudry–Morain).
**No exponent moves under any outcome**, and the open cost objections RT-CM-1..6
remain open and untouched.

**Kills-it-early.** If the orbit-complete construction changes the density penalty as
well as α, the ablation is no longer one-variable and the design must be respecified
before anything is read.

---

### A3-9. Elliptic nets: measure the **excess** relation dimension over the universal Somos ideal — is any net relation k-dependent at all?

**Claim.** The recurring kill argument for nets (`KN-TECH-009`, `KN-OPEN-005`) is
that "Somos identities are universal (hold for every k), so restricted to a single
k-fiber they may yield only tautologies", and `KN-FIND-002` records the net oracle
as simulable at O(log N) — which, under `IDEA-20260727-004`'s simulation-overhead
budget (T ≥ c√N / C_sim), leaves a floor of √N / log N. **So the entire residue of
the elliptic-net lane is a logarithmic cofactor, and this record says so in the same
sentence as the claim.** What is nonetheless open and cheap is the *tautology*
question: define, for a box A ⊂ Z² of net indices, the F_p-dimension D(A) of the
space of linear relations among the net values {W(a,b) : (a,b) ∈ A}, and let
D_univ(A) be the dimension generated by the universal Somos identities restricted to
A. CLAIM: the **excess** D(A) − D_univ(A) is exactly 0 at every box on every curve,
which would make "the net encodes only the group law, not k" a measured statement
instead of a suspicion.

**Mechanism / tracked object.** The tracked object is **the relation module of the
net restricted to a box** — a subspace of F_p^|A|. Lossy: it discards every net
value and retains only the linear dependencies among them. Compatible: the Somos
recurrence maps relations on a box to relations on a shifted box, so the retained
subspace propagates under index translation, which is the only operation the net
exposes.

**Minimal discriminating test.** Toy curves, n ≤ 2^16. Compute W over boxes
A = [0,L]² for L ∈ {4, 6, 8, 10}; build the |A|-column value matrix over several
independent (P, Q) fibers on the same curve; take its rank; compare against
D_univ(A) computed by generating the Somos identities symbolically on the same box.
Report excess(L) with the fiber count as the sample dimension.

**Null object / control.** (a) A **random Somos-shaped sequence**: a sequence
generated by the same quadratic recurrence from random initial terms, with no curve
behind it. Its excess must be 0 for the same structural reason; if it is not, the
instrument manufactures excess. (b) A **random sequence with no recurrence**, whose
D(A) must be 0 for L² > fiber count — the instrument must be able to report "no
relations". (c) Generic-group transport: the identical statistic on Z/nZ with a
random bijection to F_p in place of the net map.

**Falsifier (reachable).** (F1) excess = 0 at every box → the tautology argument is
**measured**, `KN-OPEN-005`'s net limb tightens, and the lane closes with a named
obstruction ("the net's relation module on a box is generated by the k-free Somos
ideal"). (F2) excess > 0 and **growing with L** and surviving both nulls → net
relations carry k-dependence and the question becomes arrival rate — which must then
be measured against the birthday threshold **before** anything is described as an
advantage. (F3) The Somos ideal generators cannot be enumerated on a box within
budget → D_univ is not computable and the excess is undefined; nothing is read.

**Cost.** Implementation: medium. Compute: low (ranks of matrices with ≤ a few
hundred columns over F_p; CPython + `sympy`/`numpy` — **no Sage**; note
`ECDLP-IDEA-006` in this repository is an adjacent, differently-framed record on
nets and must be read before this is specified).

**Ceiling, stated bluntly.** Best case is a **log cofactor**, per the overhead budget
above; this idea **does not move an exponent** and is proposed as a building block
that converts a suspicion into a measurement. Its priority should be ranked
accordingly and it should not outrank A3-1/A3-3/A3-6.

**Kills-it-early.** If the Lauter–Stange equivalence between EDS problems and the
ECDLP already entails excess = 0 as a corollary, the measurement is confirmatory
and its honest status is `known`.

---

### A3-10. Turn the F_p incidence bound around: use it as an upper bound on **relation supply** for chord/secant factor bases

**Claim.** The corpus treats incidence as an *oracle* (`KN-FIND-002`: simulable at
O(B^m), not closed at 1/2) and, in the `ECDLP-IDEA-012` line, as an *algorithmic*
question (kSUM/3SUM-indexing, pair-wedge normal forms). Neither uses the direction
the incidence literature actually supplies: point–line incidence bounds over F_p
(Stevens–de Zeeuw; Rudnev's point–plane bound) are **upper** bounds on the number of
incidences, which upper-bound the number of chord relations a factor base of size B
can possibly supply. CLAIM: for a factor base F of size B in E(F_p), the number of
2-term chord decompositions available is bounded by an incidence count to which
these theorems apply, and the resulting supply bound can be compared directly
against the ≈B relations index calculus requires. If the bound gives supply = o(B),
the 2-term chord route is **dead by counting**, independent of any solver — a
closure resting on an external theorem rather than on a screening tally.

**Mechanism / tracked object.** The tracked object is **the incidence count** — a
single scalar counting (point, chord) incidences between F and the chord family. It
is maximally lossy (retains one integer from a whole configuration) and it composes:
incidences of a union bound by the sum, incidences under an affine change of
coordinates are preserved, which is exactly the invariance the theorems exploit.

**Minimal discriminating test.** (i) **Literature-blocking transcription**: obtain
and transcribe the exact hypotheses and exponents of the Stevens–de Zeeuw and Rudnev
bounds from source. **The exact exponents must not be written from memory**, and the
applicability hypotheses (which restrict |P| and |L| relative to p) are precisely
where this idea will most likely die. (ii) Instantiate at B = p^(1/2) and check
whether the bound is non-vacuous — i.e. whether it beats the trivial B² count. (iii)
Numeric non-vacuity check on toy p: count actual chord incidences for random and for
structured F and compare against the transcribed bound.

**Null object / control.** (a) A **random point set** of the same size in the plane
F_p², where the incidence count must sit at the random-configuration expectation —
if the curve's count matches it, the curve structure contributes nothing and the
whole framing is generic. (b) The **trivial bound** B², which the transcribed bound
must beat at the relevant range or it is vacuous. (c) A **structured** point set
(a line, a coset) where incidences are known to be extremal — the instrument must
detect the extremal case or it cannot detect elevation.

**Falsifier (reachable).** (F1) The bound's hypotheses require |P| ≪ p^(something)
that excludes B = p^(1/2) → **not applicable at the parameters that matter**, the
idea is void, and that is recorded as the named reason. (F2) The bound is applicable
and gives supply ≥ B → **no closure**; the lane stays open with a quantified supply,
which is more than exists now. (F3) The bound gives supply = o(B) → a counting
closure over 2-term chord factor bases, requiring independent review before it is
described anywhere.

**Cost.** Implementation: low. Compute: negligible (toy counting).

**GGM position.** The incidence *oracle* is the one corpus subject that is **not**
poly-time computable from public data — it reports the results of a search. That is
why its O(B^m) overhead does not close it at 1/2: it is not a representation at all
(see A3-11). This idea sidesteps the oracle entirely and reasons about supply, so
the simulability question does not arise for it.

**Ceiling.** A closure branch **moves no exponent** — it removes a lane. A
non-closure branch produces a supply figure, not an algorithm. Neither is an attack.

**Kills-it-early.** F1 is the likely outcome and it is checkable in one reading
session; do that before anything else in this entry.

---

### A3-11. The representation/advice dichotomy: sort every corpus oracle by poly-time computability from public data, and check whether the "not closed at 1/2" verdicts are exactly the advice oracles

**Claim.** `KN-FIND-002` produces two kinds of "not closed at 1/2" for two
structurally different reasons and does not distinguish them. Proposed dichotomy: an
augmented oracle is a **representation** if its answer is computable in time
poly(log N) from public data (curve, points, factor base), and an **advice oracle**
otherwise. CLAIM, checkable per subject: the elliptic-net oracle is a representation
(W(a,b) costs O(log N) group operations — so by `IDEA-20260727-004`'s budget its
residue is a **log cofactor** and nothing more), while the incidence oracle is an
**advice** oracle (reporting all m-term decompositions is a search nobody can
perform in poly time), so its "not closed by the constant-overhead bound" verdict is
an artifact of positing an oracle that cannot be built. Under this dichotomy the
open region of `KN-OPEN-005` is **empty of representations** and consists entirely of
advice oracles, whose study is the study of *lower bounds relative to an oracle*, not
of algorithms.

**Mechanism / tracked object.** The tracked object is **the simulation-overhead pair
(C_sim, C_real)** for each oracle: the cost of answering one query generically, and
the cost of answering it in the concrete representation. `IDEA-20260727-004` already
establishes the attack-cost floor √N·C_real/C_sim; this record's content is that the
floor drops below √N **only when C_real ≪ C_sim**, which is precisely the advice
case, and that the corpus has never sorted its oracles by that ratio. The pair is a
lossy projection of an oracle (retains two integers, discards the semantics) and it
composes multiplicatively under oracle composition.

**Minimal discriminating test.** Paper, one table. For each of the eight
`EXP-GGM-001` subjects plus the objects of A3-4, A3-5, A3-7 and A3-9: state C_sim,
state C_real with an explicit algorithm, and compute the ratio and the resulting
floor. Cross-check two rows numerically at toy scale by actually timing the concrete
answer against a generic simulation.

**Null object / control.** (a) The **discrete-log oracle** itself: C_real = ∞ by
assumption, C_sim = ∞; it must land in the advice column or the sorting rule is
broken. (b) The **pure group-operation oracle**: C_real = C_sim = 1, floor = √N
exactly. (c) A synthetic oracle with **deliberately** C_real ≪ C_sim (e.g. "return
whether x(g) is a quadratic residue", O(log p) real versus no generic simulation) —
the instrument must place it in the advice column and must report a floor below √N,
demonstrating the statistic can move. Note this control's own fate is instructive:
`IDEA-20260803-e2f5bd` records that the quadratic-residue base has B ≈ N/2, so
linear algebra alone charges ≈N²/4 — cheap to answer, useless to use.

**Falsifier (reachable).** (F1) Some corpus subject has C_real ≪ C_sim **and** a
poly-size usable structured set → the dichotomy has a live cell and that subject is
the one worth work. (F2) The dichotomy does not partition — a subject is neither
poly-time computable nor an honest advice oracle (e.g. its cost depends on the
instance) → the sorting rule is too coarse and must be refined before use. (F3) The
numeric cross-check contradicts a stated C_real → the table is wrong where it was
checked, and by inference where it was not.

**Cost.** Implementation: none (paper) plus a small timing script. Compute:
negligible.

**Ceiling.** **No exponent moves.** The deliverable is a re-reading of
`KN-OPEN-005`'s open region that says what is actually open there. If the claim
holds, the honest statement is that the representation route to prime-field ECDLP is
closed up to log cofactors *given* the model audit of A3-3 and the δ-repair of A3-1,
and that everything left in the open region is an oracle-relative question.

**Kills-it-early.** If A3-3 shows the corpus verdicts live in a model with no proved
√N bound, then C_sim is not defined against a bound at all and this table has no
theorem to feed; A3-3 must therefore run first or concurrently.

---

## Batches

Three sequential batches, each with **at most 3 concurrent non-archive tasks** and
**disjoint write scopes**. Every batch's write scope is its own task directory; no
task in any batch edits a shared ledger, hypothesis, or experiment record — that is
the Coordinator's authority alone.

### Batch A3-B1 — Screen before compute (paper-only)

- **Objective.** Decide, at zero compute, which representation lanes survive a
  model-audit and a lower-bound screen, and repair or expose the model switch inside
  `KN-FIND-002`'s inference before any further compute is spent on representations.
- **Ideas.** A3-3 + A3-7 (task 1); A3-1 + A3-11 (task 2); A3-10 (task 3).
- **Grouping rationale.** All three tasks are derivations or literature
  transcriptions with no experimental dependency, and two of the three are
  *blocking* for later batches: A3-3 decides which GGM variant every corpus verdict
  lives in, and A3-1 decides whether a cited theorem exists to replace the ad-hoc
  argument. A3-11 consumes both, so it is paired with A3-1. A3-10 is independent and
  literature-blocked in its own right, so it is isolated.
- **Budget.** No compute beyond seconds of symbolic work; three reading/derivation
  sessions; hard cap on the S₄ symbolic elimination in A3-7, with a cap hit reported
  as "not measured".
- **What it decides.** (1) Whether "SIMULABLE ⇒ closed at 1/2" is a theorem-backed
  inference or a model switch. (2) Whether the alternative-curve-model class closes
  with a named obstruction. (3) Whether the structured-GGM δ-screen applies to
  coordinate oracles at all. (4) Whether the F_p incidence bound is applicable at
  B = p^(1/2) or vacuous there.

### Batch A3-B2 — Instruments that can fail (low compute)

- **Objective.** Convert three asserted-or-unadjudicated instrument verdicts into
  measured ones, each with a control that has a free variable and can therefore fail.
- **Ideas.** A3-2 (task 1); A3-8 (task 2); A3-4 (task 3).
- **Grouping rationale.** All three are re-executions or ablations of *existing*
  frozen instruments (`EXP-GGM-001`, `EXP-STR-003/004`, `EXP-TRA-001`), all three
  have committed baseline numbers to reproduce as a gate, all three are cheap, and
  their write scopes are naturally disjoint by experiment lineage. A3-2 is sequenced
  after Batch B1 because A3-3 tells it which model variants to stamp.
- **Budget.** Single-digit CPU-hours total; hard per-subject caps; toy tier only
  (`n ≤ 2^14`), and every arm must reproduce its committed baseline cell-for-cell
  before any new cell is read.
- **What it decides.** (1) Whether the simulability classification survives an
  honest re-execution, and under which model. (2) Whether `phi_alpha` is a
  truncation artifact (`EV-STR-003` UC-1 / `EV-STR-004` UC-2 discharged either way).
  (3) Whether `KN-OPEN-010`'s barrier is the ± fold or character orthogonality, with
  the recorded confound removed.

### Batch A3-B3 — New objects (medium compute, gated on B1)

- **Objective.** Attempt the one deliverable in this slice that could change how the
  program searches — an object-indexed taxonomy with a real closure argument — and
  test the two concrete new objects that the taxonomy frame and the collapse theorem
  both point at.
- **Ideas.** A3-6 (task 1); A3-5 (task 2); A3-9 (task 3).
- **Grouping rationale.** A3-6 is the flagship and is paper-first, so it runs
  concurrently rather than behind the other two; A3-5 is gated internally (Stage 1
  derivation before Stage 2 compute) and is the direct successor to
  `THM-COMMUTATOR-KERNEL1`'s named gaps G1/G3; A3-9 is the lowest-priority item in
  the batch and is included only because it is cheap and converts a suspicion into a
  measurement — its ceiling is a log cofactor and it must be ranked last.
- **Budget.** A3-6: negligible compute. A3-5: Stage 2 only if Stage 1 fails to
  collapse, capped at single-digit CPU-hours, with the one-vertex positive control as
  the port-correctness gate for the Sage-free reimplementation. A3-9: matrix ranks
  over F_p at ≤ a few hundred columns.
- **What it decides.** (1) Whether an object-indexed ECDLP taxonomy exists, with the
  divisor lattice of n−1 as its index and a sharp-2-transitivity closure argument —
  i.e. `KN-OPEN-019` outcome 1, 2 or 3. (2) Whether the quiver collapse extends to a
  second vertex, discharging or sharpening `KN-OPEN-008` and the G1/G3 gaps. (3)
  Whether any elliptic-net relation is k-dependent at all.

---

## Honest accounting (`docs/inventor-protocol.md` §5)

- **Objects considered.** The structured subset S and its density δ (A3-1); the
  generic transcript (A3-2); the twist-weight vector of an oracle output (A3-3); the
  coarse cell occupation measure under a sign-splitting partition (A3-4); the quiver
  word and its shadow at two vertices (A3-5); the stabilizer subgroup of a projection
  in AGL(1, Z/n) × twist torus × End(E) (A3-6); the summation correspondence with
  its quotient degree d_ι (A3-7); the position sequence of orbit-boundary breaks in a
  row-emission stream (A3-8); the relation module of an elliptic net on a box (A3-9);
  the incidence count (A3-10); the overhead pair (C_sim, C_real) (A3-11).
- **`dominated_by`.** `n/a (no result claimed)` for every entry. No idea in this
  catalogue claims an algorithm, a solve, a relation, a certificate, or a cost
  improvement, so no entry occupies a point on the frontier and none is dominated or
  dominating. The frontier rows checked in reaching this statement, for each entry's
  *hypothetical* positive branch: Pollard rho (≈0.886√N time, O(1) memory, linear
  parallel speedup), BSGS (≈√N time, √N memory), the automorphism-quotient rho
  variant (√(N/|Aut|)), the Corrigan-Gibbs–Kogan preprocessing tradeoff
  (ST² = Õ(N)), the Kuhn–Struik multi-target frontier (√(LN)), and prime-field index
  calculus (no known advantage). This is **not** an unchecked null.
- **`sota_delta`.** Quantitatively **zero on every ECDLP cost axis** for all eleven
  entries. The claimed deltas are methodological and are stated as such: a model
  audit of a load-bearing inference (A3-3, A3-1), a void run replaced by a
  measurement (A3-2), two unadjudicated instruments adjudicated (A3-8, A3-4), a
  closure over the alternative-model class (A3-7), a possible enumeration with a
  transitivity argument where the program currently has a tally (A3-6), and a
  re-reading of `KN-OPEN-005`'s open region (A3-11). A3-9's best case is explicitly a
  **log cofactor**, and A3-5's and A3-10's best cases are relation-class and
  supply-counting statements, not exponents.
- **Enumerated closures proposed (each with its intended mechanism, per §4).**
  (i) A3-7: alternative curve models cannot move the summation-polynomial degree
  because that degree is a birational invariant of the summation correspondence set
  by d_ι, not by the model — forward guidance: quotients of degree > 2 make it worse,
  and the remaining escape is a factor base not defined by a quotient coordinate.
  (ii) A3-6/T1–T2: an object equivariant under all of AGL(1, Z/n) is generic and
  Ω(√N) binds it, and an object invariant under scalar and translation carries zero
  information about k by sharp 2-transitivity — forward guidance: the open classes
  are objects with stabilizer H_r for r | n−1 and objects with trivial stabilizer,
  i.e. instance-specific coordinate structure, which is where index calculus already
  lives. (iii) A3-11: the "not closed at 1/2" region of `KN-OPEN-005` may contain no
  representations, only advice oracles — forward guidance: oracle-relative lower
  bounds, not algorithms. **None of these is asserted here; each is the *branch* of
  its idea that the proposed test could produce, and each would require independent
  review before being described as a closure.**
- **Open directions for the next session, not covered by this slice.** Objects
  requiring more than one group operation to reveal structure (every meter in this
  catalogue and in `IDEA-20260802-002` is one-step, and that is a declared blind
  spot); adaptive and set-valued objects; joint multi-element structure — pairings,
  isogenies to other curves, Weil descent — which is where the real non-generic
  attacks live and which A3-6's frame predicts must be the escape from AGL
  equivariance; and multiplicative-character rather than additive statistics.
- **Premature-closure guard.** No lane in this slice is declared closed by this
  catalogue, and no entry declines to generate on saturation grounds. Where a lane is
  expected to close, the entry names the obstruction, gives the argument, and names
  what remains open — and where an entry's honest ceiling is a constant factor or a
  log cofactor, it says so in the same sentence as its claim.
