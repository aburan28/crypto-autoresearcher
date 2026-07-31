---
id: KN-LIT-7603
type: literature
title: Linear Descent for Rank-2 and Rank-4 Module-LIP
authors: [Anonymous]
year: null
venue: Anonymous submission (unrefereed; venue and date not stated in the text)
identifiers:
  eprint: null
  doi: null
  url: null
tags: [module-lip, hawk, lattice-isomorphism, linear-descent, symmetric-square, hodge-star, exterior-square, svp, cm-field, lenstra-silverberg, bambury-nguyen, pqc]
confidence: reported
citation_verified: full_text_supplied
added: 2026-07-28
superseded_by: null
---

> **Provenance caveat.** The full text was supplied directly by the user on
> 2026-07-28. The submission is anonymous and states no venue, date, ePrint
> number, or DOI, so **the citation cannot be independently resolved** and the
> results are unrefereed. Everything below is recorded as *reported by the
> paper*, not as verified. The cited prior work (Lenstra–Silverberg,
> Bambury–Nguyen, Luo et al., Mureau et al., HAWK) is separately checkable and
> is where the load-bearing external machinery sits.

> **ID allocation.** Filed as `KN-LIT-7603` because `main`'s literature corpus
> already occupies `KN-LIT-001`…`KN-LIT-7591` while this branch's runs only to
> `081`. Allocating the next local number would have created an add/add
> collision of exactly the kind `CORR-20260724-001` and `KN-LIT-081` already
> record. Chosen above `main`'s maximum so the note merges cleanly.

## Contribution

End-to-end **linear descents** for determinant-one Module-LIP in module ranks
two and four, over a CM extension `L/L+` with `d = [L+ : Q]`, `R = O_L`,
`S = O_{L+}`.

The framing is the paper's main methodological point: a smaller lattice is *not*
a search reduction. Three things must hold together —

1. the auxiliary lattice and metric are computable from public input and
   transported by every hidden isometry;
2. the relevant SVP output is **recognizable** inside that lattice; and
3. the recognized data **determines a transition** for the original instance,
   including its integral module structure.

The paper argues (2) and (3) are routinely blurred: an isometry of an auxiliary
lattice need not lie in the tensor representation of an isometry of the original
module, and independently recovered rank-one pieces need not glue integrally.

**Rank two (symmetric-square descent).** A conjugate-linear symmetry induces a
three-dimensional `L+`-fixed space in `Sym²_L(V)`. Its integral points form a
rank-`3d` lattice, identified via `Φ(u) = κ(u)J₂` with the integral trace-zero
self-adjoint endomorphisms. Cayley–Hamilton forces `X² = q·I₂` with `q` totally
positive, and the trace metric is minimized exactly at `q = 1` — so **the unit
shell consists exactly of involutions**. A matched source/target involution pair
exposes two rank-one submodules; two Lenstra–Silverberg recoveries plus exact
module and Hermitian tests reconstruct the transition. For the standard
power-of-two cyclotomic orbit the source shortest shell is explicit
(`{±D} ∪ {±E_j}`), with gap `√2` to the next length, so **one γ-SVP output with
γ < √2 suffices**.

**Rank four (Hodge descent).** The Hermitian Hodge involution on `Λ²_L V` gives a
rank-`6d` auxiliary lattice. For an orthogonal pseudobasis it decomposes as three
weighted rank-one ideal lattices. Given a matched exterior-square map `T = Λ²C`,
the spaces `T(e_i ∧ V)` recover four image lines by elementary wedge-annihilator
computations; four rank-one Lenstra–Silverberg calls plus exact module,
Hermitian, determinant and compound-matrix tests reconstruct `C`. For the
standard cyclotomic orbit the Hodge lattice is **hypercubic**, and the public
`S`-action of `s = ζ + ζ⁻¹` splits a recovered shortest basis into three signed
`N`-cycles, reducing basis matching to a **polynomial signed-cycle enumeration**
(at most `6(4N)³` candidates).

**Oracle-rank reduction.** Bambury–Nguyen is applied only *after* the direct
decoding chains close. Rank two: a calibrated primal–dual lattice with minima
product `1/2` puts the two required involution types in primal and dual shortest
shells, giving oracle calls of rank `≤ ⌊3d/2⌋ + 1`. Rank four: the hypercubic
algorithm recovers the shortest basis with calls of rank `≤ 3d + 1`.

## Verified scope, as the paper itself delimits it

The paper is unusually explicit about the boundary, and §5 should be read before
citing any result:

- **Complete SVP-to-Module-LIP reductions are proved only for the standard free
  power-of-two cyclotomic orbit** (Thm 20, Thm 36).
- The fixed-space constructions and matched-data decoders hold for **arbitrary
  projective modules**; the rank-four lattice shape is explicit for **every
  orthogonal pseudobasis**.
- **Open, and stated as the remaining obstacle:** completing generic SVP output
  on three weighted ideal summands to a list containing the hidden `S`-linear
  exterior-square map. Such a lattice **need not be hypercubic** and its shortest
  vectors **need not form a recognizable basis**.
- Determinant-one is part of the *normalized problem*, not a free assumption.
  Prop 4 handles free `GL_r(R)` branches via Lenstra–Silverberg norm recovery
  over finitely many root-of-unity branches; a general projective determinant
  line needs separate ideal and norm data.
- Bambury–Nguyen reduces oracle rank only. It performs **no** eigenline recovery,
  Hodge-basis completion, or Lenstra–Silverberg assembly.
- No claim rests on an auxiliary-lattice isometry alone: every candidate is
  checked against the original Module-LIP equations.

## Relevance to this program

**Directly relevant to the PQC lattice goals, not to ECDLP.** Rank-2 Module-LIP
over power-of-two cyclotomics is the structured problem underlying **HAWK**
(KN-LIT-4174), so this bears on `GOAL-MLKEM-001` / `GOAL-CRYPTO-001` and on
nothing in `RQ-ECDLP-002`. Filed for the corpus, not as an ECDLP frontier item.

**Methodological transfer worth flagging.** The paper's three-part standard for
when a descent becomes a reduction is close to the failure mode this campaign has
hit repeatedly, from the other direction:

- *"the SVP output must be recognizable"* ↔ `EXP-STR-002`'s `phi_alpha`, where
  the metric turned out to count row-insertion bookkeeping rather than
  φ-invariance (see `DEC-20260727-009`, `EV-STR-003`).
- *"the recognized data must determine a transition, including integral module
  structure"* ↔ the repeated finding that a quantity can be measured exactly and
  still license nothing, e.g. `EV-IC-002`'s crossover, where `K* = ∞` against the
  correct multi-target baseline regardless of the measured quantity.
- The paper's insistence that recovered rank-one pieces **need not glue
  integrally** is the same class of gap as `EXP-ENDO-001`'s witness lattice
  `W_r`, which is not attacker-constructible at all (`REF-20260728-002`).

The transferable rule: *a lower-dimensional invariant that is transported by the
hidden map is necessary but not sufficient; recognition and lifting are separate
obligations and each needs its own exact test.*

## External machinery relied on

- **Lenstra–Silverberg**, *Testing isomorphism of lattices over CM-orders*, SIAM
  J. Comput. 48(4):1300–1334 (2019) — rank-one norm-constrained generator
  recovery; solutions unique up to `µ(L)`.
- **Bambury–Nguyen**, PQCrypto 2024, LNCS 14771:343–370 — primal–dual and
  hypercubic oracle-rank reduction.
- **Luo–Jiang–Pan–Wang**, ASIACRYPT 2024, LNCS 15487:359–385 — rank-two
  symplectic automorphism eigenspace strategy, used as a black box.
- **Mureau–Pellet-Mary–Pliatsok–Wallet**, EUROCRYPT 2024; **Allombert–
  Pellet-Mary–van Woerden**, EUROCRYPT 2025; **Chevignard et al.**, EUROCRYPT
  2025 — prior rank-2 Module-LIP cryptanalysis under other hypotheses.
- **Ducas–Postlethwaite–Pulles–van Woerden**, ASIACRYPT 2022 — HAWK.

## Related corpus entries

`KN-LIT-4174` (HAWK), `KN-LIT-1356` (commitments from Module-LIP),
`KN-LIT-4314` (hull attacks on LIP), `KN-LIT-5513` (LIP, quadratic forms and
remarkable lattices) — all on `main`; this note is additive and does not
supersede them.

## Open questions this raises

1. Does the rank-four basis-completion obstacle admit a `HAWK`-relevant
   instantiation, or is it confined to non-cyclotomic weighted ideal families?
2. Is there a rank-`2^k` generalization, or do the symplectic (`r=2`) and Hodge
   (`r=4`) identities exhaust the exact determinant identities available?
3. Does the paper's recognition/lifting standard have a stateable analogue for
   index-calculus descents, where the "auxiliary lattice" is a relation matrix?
   This is the one thread with possible ECDLP contact, and it is speculative.