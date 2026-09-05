---
id: KN-TECH-ee6696
type: technique
title: "ECDLP tracked-object enumeration: what each established attack family F1-F7 tracks, the operation it must survive, what its projection discards, and the named obstruction that stops it -- a synthesis of committed records that supports KN-OPEN-019 outcome 2 for the point-level families and claims no closure"
tags: [ecdlp, methodology, tracked-object, attack-families, enumeration, trichotomy, rigidity, lossy-projection, prime-order, kn-open-019, inventor-protocol, saturation-discipline, synthesis, prime-field]
confidence: reported
complexity: not a computational technique -- a classification instrument assembled from committed records; its cost is reading time and it changes no exponent
applicability: "Any ECDLP ideation or closure session that must (a) declare the established families off-limits as the primary lens with their tracked objects named rather than their lineages, (b) place a candidate object in the trichotomy of IDEA-20260806-c5d183 against a named operation set, or (c) state how far the program's saturation conclusions about the classical prime-field ECDLP rest on an argument rather than a tally. Scoped to prime-order subgroups of prime-field curves; every obstruction below is quoted at the tier its source record carries."
source_refs: [KN-OPEN-019, KN-TECH-056, KN-TECH-080, IDEA-20260802-002, IDEA-20260806-c5d183, IDEA-20260807-df906f, IDEA-20260815-f558e4, IDEA-20260901-863e36, H-TLD-f4c8ba, H-PROP-c95932, KN-FIND-ffe1df, KN-OPEN-020, KN-OPEN-003, KN-OPEN-001, KN-OPEN-005, KN-OPEN-010, KN-OPEN-011, KN-OPEN-018, KN-OPEN-3417fc, RQ-ECDLP-623a32, RQ-ECDLP-002, RQ-JMV-001, KN-TECH-001, KN-TECH-003, KN-TECH-005, KN-TECH-006, KN-TECH-009, KN-TECH-018, KN-TECH-030, KN-TECH-031, KN-TECH-032, KN-TECH-033, KN-TECH-059, KN-TECH-06bb4e, KN-TECH-73630e, KN-TECH-3b593f, KN-FIND-007, KN-FIND-002, KN-FIND-b7e091, KN-FIND-3a7d42, KN-FIND-61347e, KN-LIT-013, KN-LIT-7594, KN-LIT-7595, KN-LIT-7601, IDEA-20260727-005, IDEA-20260806-3b91c7, IDEA-20260807-053a55, IDEA-20260807-631e80, IDEA-20260806-071255, EV-FBG-001, DEC-20260724-007, EV-GGM-001, DEC-20260726-007, EV-GGM-79e710, DEC-20260804-3b4258, EV-TRA-001, TASK-20260905-f8563d]
added: 2026-09-05
superseded_by: null
---

## What this record is

`KN-OPEN-019` asks what object each ECDLP attack family tracks and whether that
enumeration is closed, and records that the enumeration had never been written
down. `docs/inventor-protocol.md` section 1 says object-first generation cannot
run at full strength for the ECDLP until it is. This entry writes it down, in
the form `KN-TECH-056` component 7 demands -- for each family, the object, the
operation it must survive, and the named obstruction -- and then states, from
committed records only, which of the three `KN-OPEN-019` outcomes the
enumeration supports.

It is a **synthesis**. Every cell and every step of the argument is read from a
committed record and cites it. Nothing is derived here that is not already
derived in a cited record; where the corpus names no object or no obstruction
for a family, that is written as a gap. Written under `TASK-20260905-f8563d`,
which forbade web search, new identifiers, edits to existing records, and any
candidate object of this entry's own.

The family list is the F1-F7 list of `IDEA-20260802-002`, which is the record
that first named the established families as off-limits lenses and paired them
with an executable meter -- the loss `L(pi)` and branching `b(pi)` of a
projection `pi` from the prime-order subgroup `G = <P>` to a set `S`. The
trichotomy column is that of `IDEA-20260806-c5d183`: on a prime-order group, a
projection that propagates deterministically under the **full translation
action** is constant or injective, so every lossy tracked object is
**partial-action** (deterministic only under a proper sub-action),
**branching** (`b > 1`), or **coordinate-dependent** (a function of the
representation, not of the group element); a projection that is injective has
no class because it discards nothing. `IDEA-20260901-863e36` adds the second
axis this entry uses throughout: propagation is a property of a projection
**paired with an operation set** `Sigma`, and the lossy objects that propagate
under `Sigma` are exactly the block systems of `<Sigma>` acting on the subgroup.

## The enumeration

Abbreviations: `G = <P>` the prime-order subgroup, `N = |G|`, `Q = [k]P`.
Tier labels in the obstruction column: **(est.)** = the source record carries
`confidence: established` and relays a textbook or published result;
**(finding)** = a `KN-FIND` entry, at the `proof_status` it states;
**(validator-confirmed)** = the specific statement an independent Validator
pass confirmed, per the entry's own text; **(proposal)** = a `proposed`
`IDEA-*` record whose derivation has not been reviewed and whose novelty is
`unverified` or corpus-screen-only; **(hypothesis)** = an `H-*` record.

| family (IDEA-20260802-002) | tracked object | operation it must survive | what the projection discards | trichotomy class (IDEA-20260806-c5d183) | named obstruction, with the record it is read from | what remains open for this family |
|---|---|---|---|---|---|---|
| **F1 walk-collision** (rho, kangaroo, van Oorschot-Wiener, BSGS) | The group element carried with its known representation `aP + bQ` (`IDEA-20260802-002`); the walk state `x_i = a_i P + b_i Q` (`KN-TECH-001`, `KN-TECH-006`). | The walk step `x -> f(x)` of an `r`-adding walk with known scalar offsets, plus the equality test at a collision or distinguished point (`KN-TECH-006`); for BSGS, table lookup by equality (`KN-TECH-031`). | Nothing of the group element: the projection is the identity on `G`, and `(a, b)` is carried, not discarded. The lossy pieces -- the distinguished-point predicate and the automorphism fold -- are store filters and quotients, not the tracked object. `IDEA-20260807-df906f` escape E4: rho tracks a **collision in a walk**, not a congruence, so the rigidity theorem does not touch it. | **None because injective** (`IDEA-20260806-c5d183` (A): injective is a degenerate end of the theorem). The coarse-grained relative -- a partition of `G` into cells followed under the translation walk -- is Class II branching (`IDEA-20260806-c5d183`; `KN-OPEN-010`). | (est.) Shoup's generic bound: any generic DLP algorithm needs `Omega(sqrt N)` group operations (`KN-TECH-005`), realised at `0.886*sqrt(n)` with `O(1)` memory per processor (`KN-TECH-006`); BSGS is `sqrt(n)` steps but `n^{2/3+o(1)}` full cost once memory is charged (`KN-TECH-031`). Anything better must be non-generic (`KN-TECH-005`). (proposal) The fixed-curve tradeoff `S*T^2 = Theta(N)` is the frontier rho occupies at `S = O(1)` (`IDEA-20260806-3b91c7`). | Nothing generic. The one branching relative measured in this corpus -- the coarse-grained transfer operator of the translation-by-`P` walk -- returned localisation `L = O(1)`, growth exponent `delta = 0.0195`, strength `preliminary`, on `x`-interval partitions at toy `n <= ~4200` only, with non-negation-symmetric partitions untested (`EV-TRA-001`; question `KN-OPEN-010`). `IDEA-20260806-c5d183` forward guidance (a): whether Class II admits amortised branching below the survival-depth bound `log(budget)/log(b)`. |
| **F2 factor-base decomposition** (Semaev summation polynomials, Gaudry, Diem, descent) | A relation vector over a factor base (`IDEA-20260802-002`): the decomposition of `R = aP + bQ` as a sum of `m` factor-base points, obtained by a summation-polynomial solve (`KN-TECH-003`). | Translation by **factor-base elements only** (`IDEA-20260806-c5d183` Class I: "this is exactly index calculus"), then the linear-algebra stage mod `N` (`KN-TECH-003`). | Everything about `R` except its decomposition; and for most `R` no decomposition exists, so the object is defined only on the decomposable subset. | **Partial-action** (`IDEA-20260806-c5d183` Class I, with cost obligation "conservation-mean coverage"). **Discrepancy found by this synthesis and resolved 2026-09-05:** `agents/idea-generator.md` search bias 6 previously stated "index calculus lives in the branching class"; bias 6, its mirror in `.claude/agents/idea-generator.md`, and `docs/object-frame-ideation.md` were corrected to match `IDEA-20260806-c5d183`. Reconciliation kept: propagation of the relation vector is deterministic under the partial action; existence of a decomposition is the branching event the `(L, b)` meter prices. | (finding, `proof_status: derivation`, `claim_tier: toy`) Decomposition-yield conservation: the mean per-target yield is `C(B+m-1, m)/N` for **every** base of size `B`, geometry-invariant; coverage headroom is at most `min(1, mu)/(1 - e^{-mu}) <= 1.582`; confirmed with deviation exactly 0 over 144 cells at `N <= 2^18`, `m = 3` (`KN-FIND-007`, promoted from `EV-FBG-001` / `DEC-20260724-007`). (est.) No structured factor base with an advantage is known over prime fields; the obstruction is the missing base and the decomposition/Groebner cost (`KN-OPEN-001`, `KN-TECH-003`). (unverified, `KN-OPEN-020`) Every bounded-degree algebraic factor base over a generic prime-field subgroup is scoped out with charged costs. (proposal) The CM small-norm lane is a Class-I object whose **membership cannot be tested without the answer** (`IDEA-20260806-c5d183`, interpretation limits). | `KN-OPEN-020`'s open classes: high-degree, implicit-membership, and target-dependent factor-base descriptions; the universal no-go needs a formal complexity class for algebraic descriptions. The **solve cost** -- `KN-FIND-007` says nothing about the cost of finding a decomposition or the linear-algebra stage. Representation effects on decomposition cost (`KN-OPEN-003`, `RQ-ECDLP-623a32`). The incidence oracle is GGM-simulable only at non-constant `O(B^m)` overhead and is therefore **not** closed at exponent 1/2 by simulability (`KN-FIND-002`). |
| **F3 isogeny path** | A vertex or walk in an isogeny graph (`IDEA-20260802-002`). At point level, the transported instance `D_ell(E, P, Q) = (E', phi(P), phi(Q))` under an `F_p`-rational Elkies isogeny `phi` (`IDEA-20260807-053a55`), composed along a walk (`IDEA-20260807-631e80`). | The isogeny `phi` itself: the object must carry the instance to `E'` with `k` unchanged, and the walk must mix to uniformity in the class (`IDEA-20260807-631e80`). | On `G`, nothing: every `F_p`-isogeny either is injective on `G` (a relabelling with an efficiently computable inverse via the dual isogeny) or contains `G` in its kernel (annihilating the instance) -- there is no middle case because `N` is prime (`IDEA-20260807-053a55` (B)). The genuinely lossy quotients live on `E[ell] = (Z/ell)^2`, which is not of prime order; those quotients **are** the `ell`-isogenies (`IDEA-20260807-df906f` escape E3). | **None because injective** on `G`; the object is **curve-level**, outside the trichotomy's domain (projections of `G`). `IDEA-20260806-c5d183` itself flags that some catalogue objects "are not projections of a group element at all" and may need a bucket the trichotomy does not have -- recorded here as a gap, not repaired. | (proposal) Kernel-or-injective dichotomy: the transported instance is inter-reducible with the original at polylog group operations plus one isogeny evaluation, so isogeny data cannot reduce query complexity; the only annihilating isogeny has degree `N`, costs `Otilde(sqrt N)`, and is independent of `Q` (`IDEA-20260807-053a55` (B)-(C)). (proposal) Abelian-variety exit class E3 is quantitatively closed over a prime field: `Otilde(p^{2-2/g}) >= p^1` for `g >= 2` (`IDEA-20260727-005` (C3)). (finding, derivation, `confidence: strong`) Cross-genus Poincare-factor embedding cannot beat rho: Tate's theorem forces `#A(F_p) = Theta(N^{g-1})` for the complementary factor (`KN-FIND-61347e`). (derivation) Two post-SIDH higher-dimensional mechanisms do not specialise to genus 1 (`KN-TECH-3b593f`). | **Gap:** no `KN-*` record names the obstruction for the plain isogeny-walk-to-a-weaker-curve family (Jao-Miller-Venkatesan random self-reduction) on ordinary prime-field curves. The open question is `RQ-JMV-001`: the concrete constants of that reduction (G1), whether dlog cost is constant within a level or only equal up to the reduction's overhead (G2), and the cross-level case (G3). The mixing constant of the Elkies walk is proposed for measurement in `IDEA-20260807-631e80` and unmeasured. |
| **F4 pairing transfer** (MOV, Frey-Ruck) | The image in `F_{q^k}^*` (`IDEA-20260802-002`): the pairing values `e(P, T)`, `e(Q, T)` in the `N`-th roots of unity of `F_{q^k}`, `k` the embedding degree (`KN-TECH-032`). | The group law -- a pairing is a group homomorphism, so the object propagates exactly -- followed by the finite-field DLP, where index calculus is subexponential (`KN-TECH-032`). | Nothing on `G`. An exactly propagating map out of a prime-order group is injective or constant (`KN-FIND-ffe1df` Theorem C, validator-confirmed, homomorphism form; `IDEA-20260807-df906f` (A), proposal form), and a non-degenerate pairing is injective on `G` (`KN-TECH-032`). Under the lossy-projection test this is a change of coordinates; the gain lives in the target group's DLP, not in any loss. | **None because injective** -- consistent with `IDEA-20260727-005` (C2), which places it as the toric exit class E2 (target a subgroup of `F_{p^k}^*`, forcing `N | p^k - 1`). | (est.) The embedding degree: the transfer wins only when `k` is small; supersingular curves have `k <= 6`, and for a random prime `p` and random prime-order curve over `F_p` small `k` occurs with negligible probability, so on the program's target family `k` is of size comparable to `p` (`KN-TECH-032`, relaying Balasubramanian-Koblitz as reported). (finding, `conditional_proof`) For generic curves `k ~ N/2`, so the pairing field is of degree `~N/2` and working in it is equivalent in difficulty to the MOV attack itself (`KN-FIND-3a7d42`). (proposal) Exit class E2 costs `L_{p^k}(1/3)` plus the pairing and is governed by `k = ord_N(p)` (`IDEA-20260727-005` (C3)). | Only the negation of the precondition: `KN-TECH-032`'s own screening rule says a transfer proposal is `known` unless it supplies a mechanism that works at **large** `k`, and `IDEA-20260727-005` lists "a fourth exit class" as its falsifier. No committed record names a candidate for either. |
| **F5 p-adic lift** (Smart, Satoh-Araki, Semaev) | A lift into a formal group (`IDEA-20260802-002`): the point lifted to `E(Q_p)` or to `E` mod `p^k`, with the formal logarithm `log_Ehat : Ehat -> Ghat_a` as the intended homomorphism (`KN-TECH-059`, `KN-TECH-033`). | The group law on the lift and reduction back to `E(F_p)`; the formal logarithm must converge on the kernel it is evaluated on (`KN-TECH-059`). | Group-theoretically nothing: for the canonical prime-to-`p` torsion lift, `red : <Shat> -> <S>` is a group isomorphism, so the lifted problem is the **same** instance and the lift is information-theoretically empty; the `p`-adic coordinates are extra symbols added, not information retained (`KN-TECH-73630e`, derivation). | **Coordinate-dependent** (`IDEA-20260806-c5d183` Class III names "p-adic lifts, integer lifts" explicitly). | (est.) The formal logarithm is globally defined on `E(F_p)` only when `#E(F_p) = p` (trace one), where the ECDLP collapses to a division in `(F_p, +)`; for `t != 1` the additive target group disappears and the attack does not degrade, it does not apply (`KN-TECH-033`, `KN-TECH-059`). (proposal) Unipotent exit class E1 forces `N = p` (`IDEA-20260727-005` (C2)). (literature-derived) Silverman's four characteristic-zero faces -- consistency, formal-group annihilation, field degree (Mazur, Serre), Masser independence, canonical height -- plus the program's function-field fifth face (`KN-TECH-06bb4e`). (derivation) Face F2 is closed for **every** group-theoretic invariant by the reduction isomorphism (`KN-TECH-73630e`). | `KN-OPEN-3417fc`: a computable **non-group-theoretic** invariant (coordinate or valuation profile) on the canonical lift, which can offer at most a computational handle, never an information gain (`KN-TECH-73630e`). The function-field face F5 of `KN-TECH-06bb4e`: relations were found that the height obstruction says should not exist, so either F5 escapes the obstruction or the relations are target-blind -- undecided in that record. The Masser (F4a) function-field analogue is unmeasured (`KN-TECH-06bb4e`). |
| **F6 endomorphism or automorphism orbit** | An orbit representative (`IDEA-20260802-002`); concretely the `Gamma`-orbit label of a point for `Gamma <= (Z/N)^*` acting by `R -> [gamma]R`, realised by a canonical form such as the orbit element of least `x` (`IDEA-20260901-863e36`). | Multiplication by every `gamma` in `Gamma` (exact by construction), and the **walk step composed with re-canonicalisation**, whose per-step cost `c_can` is the load-bearing quantity (`IDEA-20260901-863e36`). | `log2 |Gamma|` bits: which element of the orbit is held (`IDEA-20260901-863e36`). The discard is compatible with `Sigma = Gamma`-multiplication and **not** with translation, by the rigidity theorem, which is consistent rather than contradictory (`IDEA-20260901-863e36`). | **Partial-action** -- deterministic under `Sigma = Gamma`-multiplication, a proper sub-action; the lossy objects under `Sigma` are exactly the block systems of `<Sigma>`, and only the orbit partitions (all `F_gamma = id`) shrink the search space (`IDEA-20260901-863e36` (C1), (C3)). Named there as the first concrete inhabitant, other than rho, of `IDEA-20260807-df906f`'s escape E4. | (est.) The automorphism discount is a **constant** factor `~sqrt(|Aut|)`, does not change exponent 1/2, and generic ordinary prime-field curves have `|Aut| = 2` (`KN-TECH-018`). (proposal, conditional on `KN-TECH-005`) Any **generic** canonicalisation has `c_can = Omega(sqrt |Gamma|)`, so no net gain for any `Gamma`; morphism-induced `O(1)` canonical forms exist only for `Gamma` inside the image of `Aut(E)`, hence `|Gamma| <= 6` (`IDEA-20260901-863e36` (C4)-(C5)). (proposal) Self-map neutrality: every homomorphism `G -> G` is a scalar, and endomorphism augmentation inflates the constant by `2^r` without moving the exponent (`IDEA-20260727-005` (C1)). (finding) Endomorphism oracles are GGM-simulable with `O(1)` overhead in the structured GGM (`KN-FIND-002`, `EV-GGM-001`/`DEC-20260726-007`; `KN-FIND-b7e091`, `EV-GGM-79e710`/`DEC-20260804-3b4258`) -- `IDEA-20260901-863e36` records three defects against these two findings routed to review and states it does not depend on them. | `IDEA-20260901-863e36` (C6): **arithmetic selectors** -- canonical forms that are neither generic nor morphism-induced -- whose cost `c_can(r)` is the one number the classification leaves open and which no run has measured. |
| **F7 preprocessing table** | A precomputed advice string (`IDEA-20260802-002`); concretely `S` stored endpoints of curve-specific, target-independent walks with their known logarithms (`IDEA-20260806-3b91c7` (B)); an `S`-bit advice string about a fixed group (`KN-LIT-013`). | The online walk from the target with the **same** step function, merging into a stored chain (`IDEA-20260806-3b91c7`); in the model, generic oracle access during the online phase (`KN-LIT-013`, `KN-TECH-005`). | The advice is a function of the curve, not of the target point: it is **not a projection of a group element at all**. `IDEA-20260806-c5d183` names "the preprocessed advice string" as an object that "may require a fourth 'not an instance-projection' bucket". The online tracked object is F1's, which is injective. | **Not placeable** -- gap. The trichotomy classifies projections of `G`; the advice string is instance-independent and the record that supplies the trichotomy says so itself (`IDEA-20260806-c5d183`, honest prior). | (reported, literature) Generic preprocessing lower bound `S*T^2 = Omega~(epsilon*N)`, tight (`KN-LIT-013`, relayed from the abstract; recorded in `KN-TECH-005`). (proposal) The achievable frontier `S*T^2 = Theta(N)` derived in half a page and calibrated against that lower bound, so rho at `S = O(1)` is the corner of a tradeoff (`IDEA-20260806-3b91c7`). | `KN-LIT-013`'s own statement: a **non-generic** preprocessing attack must surpass `S*T^2 ~ N`, not the `sqrt N` online bound. **Gap:** no committed record names a non-generic advice object, an operation set it survives, or an obstruction specific to it; the family is bounded only in the generic model. |

**A sketch item not given a row.** `KN-OPEN-019`'s own partial mapping lists a
fourth family -- HNP/lattice methods tracking short vectors in a lattice built
from leaked bits. It is not among F1-F7 of `IDEA-20260802-002`, and the corpus
records it as confined to the leakage model rather than the plain ECDLP
(`KN-OPEN-011`, `KN-OPEN-018`). Per the handoff, a row is added only for a
family a committed record names as an ECDLP family; this one is named only as
a sketch the source entry itself labels possibly wrong, so it is noted and not
tabulated.

## Argument

### Step 1 -- the rigidity results, at the tier actually verified

The spine of the enumeration is one fact stated in four committed forms. They
are **not** interchangeable in tier, and this entry does not promote any of
them.

- **Homomorphism form, validator-confirmed.** `KN-FIND-ffe1df` Theorem C: an
  exactly sum-compatible bucket index `h : E(F_p) -> [M]` whose combining rule
  is a quasigroup is a surjective homomorphism onto a group of order dividing
  `N`, impossible for `N` prime and `1 < M < N`. The entry records that the
  Validator "independently confirmed Theorem C in full, including the case
  this entry did not check (non-surjective `h`)". Two cautions carried from the
  entry itself: its frontmatter is `confidence: reported`,
  `proof_status: derivation`, and it states that its usual promotion chain
  (`EV-* -> DEC-* -> KN-FIND-*`) is **absent** "and that is a real gap"; and
  the entry's headline about Wagner `k`-trees is withdrawn -- only Theorem C
  is used here, and only for what it says.
- **Orbit form, proposal tier.** `IDEA-20260806-c5d183` (A): a projection
  propagating deterministically under the full translation action is a factor
  of a transitive action, hence `|pi(G)|` divides `N`, hence `pi` is constant or
  injective; (B) the three classes are exhaustive **over hypotheses**, not over
  objects. `status: proposed`, `novelty_status: unverified`; the record's own
  prior is that the argument is folklore.
- **Congruence form, proposal tier.** `IDEA-20260807-df906f` (A): if
  `v(R + R') = F(v(R), v(R'))` for all `R, R'` then `v` is injective or
  constant; (C) the four escapes E1 (probabilistic propagation), E2 (auxiliary
  state), E3 (objects on `E[ell]`), E4 (objects not tracked under the group
  law). `status: proposed`; its `novelty_status` is `adaptation` on a corpus
  screen alone, with external novelty recorded as unverified, and it is
  labelled proposal-tier here per the handoff.
- **Block-system form, proposal tier.** `IDEA-20260901-863e36` (C1): a map
  propagates deterministically under an operation set `Sigma` iff its fibre
  partition is a block system of `<Sigma>`; (C2) the translation slice is
  exactly df906f's theorem. `status: proposed`, `novelty_status: unverified`;
  the record discloses it was not machine-parsed at authoring.
- **Probabilistic-regime bound, proposal tier.** `IDEA-20260815-f558e4` (C):
  by Cauchy-Davenport the **strict** propagation rate of every balanced lossy
  partition of `Z/N` is exactly zero; (D) the majority-extremal partitions are
  claimed to be arithmetic progressions in the discrete-log coordinate, with
  the Vosper bridge named as "the record's real mathematical debt"; (E)
  efficiently computable bounded-degree coordinate statistics are predicted
  pinned to the `1/s` baseline within the Weil scale `O(N^{-1/2})`. `status:
  proposed`, `novelty_status: unverified`; its ideation-time arithmetic is
  stated by the record to be no run record.
- **Two hypotheses consume these.** `H-PROP-c95932` (`status: proposed`) states
  the auxiliary-state corollary `|S|*|A| >= N` in the exact regime as a
  corollary of df906f, and the probabilistic frontier as an open cell.
  `H-TLD-f4c8ba` (`status: specified`, from `IDEA-20260806-071255`) specifies
  a typed generator whose first prediction is the forced zero count of lossy
  full-translation-deterministic lenses, and whose baseline embedding is
  exactly "F1-F7 typed by hand once, then reproduced mechanically".

### Step 2 -- what the table shows

Reading the trichotomy column down the table (`IDEA-20260806-c5d183` for the
classes, `IDEA-20260901-863e36` for the operation-set pairing):

- **Three families are injective on `G`** -- F1 (the walk state), F3 (isogeny
  transport, by the kernel-or-injective dichotomy of `IDEA-20260807-053a55`),
  F4 (a non-degenerate pairing, by `KN-FIND-ffe1df` Theorem C). Under the
  lossy-projection test of `docs/inventor-protocol.md` section 2 these are
  changes of coordinates. Each obtains what it obtains from somewhere other
  than a loss: generic collision (F1, `KN-TECH-005`), the target group's own
  DLP (F4, `KN-TECH-032`), or a transport that changes nothing about `k`
  (F3, `IDEA-20260807-053a55`).
- **Two families are partial-action** -- F2 under translation by factor-base
  elements (`IDEA-20260806-c5d183` Class I), F6 under multiplication by
  `Gamma` (`IDEA-20260901-863e36` (C3)). In both, the record that classifies
  them also names the single cost the class must pay: the conservation mean
  and coverage headroom for F2 (`KN-FIND-007`), the canonicalisation cost
  `c_can` for F6 (`IDEA-20260901-863e36` (C4)-(C6)).
- **One family is coordinate-dependent** -- F5, and its obstruction is stated
  precisely as the coordinate-versus-group-structure boundary
  (`KN-TECH-73630e`: the lift is a group isomorphism; only a non-group-theoretic
  invariant could offer a computational handle, `KN-OPEN-3417fc`).
- **One family does not fit** -- F7, whose object is not an instance
  projection, as the trichotomy record itself anticipates.

### Step 3 -- which `KN-OPEN-019` outcome this supports

**Outcome 1** ("genuinely different objects with no common frame") is **not**
supported. Six of the seven objects are described by one frame -- a projection
of the point paired with the operation set it must survive
(`IDEA-20260901-863e36`), classified by which hypothesis of the rigidity
theorem it violates (`IDEA-20260806-c5d183`) -- and the same theorem governs
all of them: the injective families are its degenerate end, the partial-action
families are its Class I, and F5 is its Class III. `IDEA-20260807-df906f` (B)
records the frame's content for the symmetric-side analogy: differential,
linear, integral and division-property objects are exact lossy projections
that survive one round, and on a prime-order subgroup no such object exists,
which is why the taxonomy of `KN-LIT-7595` does not port verbatim and instead
ports as a redirection.

**Outcome 2** ("a common frame emerges, so candidate objects outside the
enumerated set become generatable") is what the enumeration **supports**, with
two qualifications stated at the strength the records carry:

1. The frame's spine is validator-confirmed only in the homomorphism form
   (`KN-FIND-ffe1df` Theorem C). The forms that do the classificatory work --
   the orbit argument, the block-system classification, the escape list -- are
   proposal-tier derivations with novelty unverified. Outcome 2 is therefore
   supported **at proposal tier**, and this entry cannot raise it.
2. The frame covers the six point-level families. F7 sits outside it (its
   object is not an instance projection), and F3's lossy content lives on
   `E[ell]` rather than on `G` (`IDEA-20260807-df906f` E3). The frame is
   exhaustive over the hypotheses of one theorem, not over every object an
   attack can carry; `IDEA-20260806-c5d183` (B) says exactly this.

What outcome 2 makes usable is already committed: `KN-TECH-056` components 1-4
run against the frame (`docs/object-frame-ideation.md`), `H-TLD-f4c8ba`'s
typed generator, and search bias 6 of `agents/idea-generator.md`.

**Outcome 3** ("a frame *and* a transitivity-style argument closes it") is
**not** supplied by any committed record, and per the handoff it may be stated
only as what such an argument would need. The source-session model in
`KN-TECH-056` component 7 is: two operation classes, each killing the
invariants the other preserves, jointly generating a group that acts
transitively enough that only trivial invariants survive both. The ECDLP
analogue would need, at minimum:

- a **formal class of "efficiently computable" projections**. Every
  probabilistic-regime bound in the corpus restricts to such a class and says
  the restriction is doing the work: `IDEA-20260815-f558e4`'s quantifier-order
  block states that a uniform majority ceiling over all `v` is **false** (the
  DL-interval partition attains `~1/2`) and holds only for the efficiently
  computable class; `KN-FIND-ffe1df` item 2 says the dlog-interval pullback
  achieves `eps ~ 1/2` at arbitrarily large `M` on every prime-order group and
  "only a definitional cost restriction closes this, and the cost clause is not
  a theorem"; `KN-OPEN-020` names "a formal complexity class for algebraic
  descriptions" as the required next result for the universal factor-base
  statement. No committed record defines that class.
- a **closure of Class I**: the universal algebraic-factor-base no-go
  (`KN-OPEN-020`, open; only the bounded-degree case is scoped out, and only
  conditionally).
- a **closure of Class II in the probabilistic regime**: `IDEA-20260815-f558e4`
  bounds one escape (E1) for bounded-degree coordinate statistics with the
  Vosper bridge unwritten; escapes E2 (auxiliary state, probabilistic half open
  per `H-PROP-c95932` Claim F), E3 and E4 of `IDEA-20260807-df906f` are
  untouched.
- a **closure of Class III**: `IDEA-20260806-c5d183` states Class III is "the
  ONLY class in which a sub-1/2 exponent for prime-field ECDLP can possibly
  live" and that its cost obligation is conditional on the structured-versus-
  opaque-label model question `KN-FIND-002` leaves open.
- **F7 and the curve-level part of F3 brought inside the frame**, or argued
  about separately.

Until those exist, the program's standing saturation conclusions about the
classical ECDLP remain, under `docs/inventor-protocol.md` section 4, a
statement about the search. What this entry changes is narrower and is stated
exactly: the enumeration `KN-OPEN-019` said had never been written down now
exists, each family carries a named obstruction read from a committed record,
and the obstructions are stated at their tiers. A count of rejected mechanisms
is not an argument, and none is offered.

## Forward guidance

Classes that remain generatable, read from the records that leave them open.
No candidate object is proposed here; `TASK-20260905-f8563d` forbids it, and
each item below is a class, not an instance.

1. **(Representation, operation set) pairs** -- search bias 6 of
   `agents/idea-generator.md`: a representation of the point in class R1
   (field representations of coordinates), R2 (curve models and embeddings) or
   R3 (non-function representations: elliptic nets, torsor and modular-curve
   coordinates, cubical and biextension lifts, `E x E` and Kummer-surface
   gluings, Weil restriction, local rings) of `RQ-ECDLP-623a32`, paired with an
   operation set `Sigma` other than translation -- endomorphisms, isogenies,
   Frobenius on an extension, a walk step composed with re-canonicalisation.
   Translation is closed for lossy objects (`IDEA-20260806-c5d183`,
   `KN-FIND-ffe1df` Theorem C); the Kummer-line and degree-`d`-function-on-`E`
   paradigm is closed at model lever 1 (`RQ-ECDLP-623a32`); the candidate's
   lossy-projection test is run against the named `Sigma`
   (`IDEA-20260901-863e36`).
2. **The branching class with the `(L, b)` meter** -- `IDEA-20260802-002`:
   objects with `L >= 1` bit and bounded `b`, priced by survival depth
   `log(budget)/log(b)`; `IDEA-20260806-c5d183`'s forward guidance names the
   two ways such an object could help -- `b` subconstant in an amortised sense,
   or branches prunable by a test cheaper than following them. The meter's
   declared blind spot is two-step and adaptive objects (`IDEA-20260802-002`,
   `no_power_against`); the auxiliary-state probabilistic frontier is
   `H-PROP-c95932` Claim F, unmeasured.
3. **The `KN-OPEN-020` open factor-base classes** -- high-degree,
   implicit-membership, and target-dependent descriptions, each charged for
   description, membership, relation, descent, time and memory; and the solve
   cost, which `KN-FIND-007` explicitly does not bound.
4. **Class III objects that survive the simulability screen at non-constant
   overhead** -- `IDEA-20260806-c5d183` guidance (c), `KN-FIND-002` (the
   elliptic-net and incidence oracles are the recorded examples of non-constant
   overhead), `KN-OPEN-005`; and the F5 openings: coordinate/valuation
   invariants on the canonical lift (`KN-OPEN-3417fc`) and the function-field
   face (`KN-TECH-06bb4e`).
5. **F6 arithmetic selectors** -- `IDEA-20260901-863e36` (C6): non-generic,
   non-morphism canonical forms for `Gamma`-orbits, whose `c_can(r)` is
   unmeasured.
6. **F3 within-class cost variance** -- `RQ-JMV-001` G2 and G3, and the walk
   mixing constant of `IDEA-20260807-631e80`.
7. **F7 non-generic advice** -- the object `KN-LIT-013` says a non-generic
   preprocessing attack must have and no committed record names.
8. **The escapes E3 and E4 of `IDEA-20260807-df906f`** -- objects on `E[ell]`,
   and objects not tracked under the group law, of which the corpus names two
   inhabitants (rho, `IDEA-20260807-df906f`; the `Gamma`-orbit label,
   `IDEA-20260901-863e36`).
9. **The formal cost class** that outcome 3 would need before any
   transitivity-style argument can be attempted (`KN-OPEN-020`,
   `KN-FIND-ffe1df` item 2, `IDEA-20260815-f558e4` quantifier order).

## Limits and cautions

- **This is a synthesis of committed records.** Every statement is read from
  the record it cites and is stated at that record's tier. No derivation,
  measurement, or literature check was performed here; web search was not
  used; the trichotomy placements of F1-F7 are this entry's reading of the
  cited records and are checkable against them, not against anything else.
- **No closure is claimed.** No class is argued empty, no family is declared
  exhausted, and outcome 3 of `KN-OPEN-019` is stated only as a requirement
  list. `KN-OPEN-019` is not edited and is not closed by this entry.
- **This entry must not be cited as evidence that a candidate object exists.**
  Outcome 2 says candidate objects become *generatable*; it does not say any
  exists, survives its controls, or moves an exponent. `sota_delta` is zero on
  every ECDLP cost axis.
- **Proposal-tier derivations remain proposal-tier.** `IDEA-20260806-c5d183`,
  `IDEA-20260807-df906f`, `IDEA-20260815-f558e4` and `IDEA-20260901-863e36`
  are `proposed` records with novelty `unverified` (or corpus-screen
  `adaptation`), unreviewed. Only `KN-FIND-ffe1df` Theorem C is
  validator-confirmed, and that finding's own promotion chain is recorded as
  absent.
- **The trichotomy is exhaustive over hypotheses, not over objects**
  (`IDEA-20260806-c5d183` (B)), and it does not place F7. Its Class III is
  described by its own author as "a dumping ground".
- **Recorded discrepancies.** F2's class differed between
  `IDEA-20260806-c5d183` (partial-action) and `agents/idea-generator.md`
  search bias 6 (branching); the discrepancy was found by this synthesis and
  resolved on 2026-09-05 by correcting bias 6, its mirror in
  `.claude/agents/idea-generator.md`, and `docs/object-frame-ideation.md` to
  match `IDEA-20260806-c5d183`, keeping the two-step reading (deterministic
  propagation of the relation vector under the partial action; existence of a
  decomposition as a branching event) as the reconciliation. The
  transfer-operator evidence file `ledger/EV-TRA-001.yaml` carries the
  internal id `TRA-EV-001`, which differs from its filename; its numbers are
  quoted with that caveat.
- **Established-tier obstructions are relayed, not re-derived.** `KN-TECH-005`,
  `KN-TECH-018`, `KN-TECH-032`, `KN-TECH-033` relay textbook results whose
  sources those entries state were not read in full; `KN-LIT-013` is relayed
  from an abstract.
- **Nothing here is at cryptographic scale**, and nothing here is a statement
  about the hardness of the ECDLP. `KN-LIT-7594` records why an enumeration
  that reads as saturation must not be used as one.
