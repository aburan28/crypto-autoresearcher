# Module 11 — Isogeny-Based Cryptography

> **Goal.** How the graph gets spent: CGL hashing, SIDH and the 2022
> attack that killed it (and why the mathematics that killed it is now
> the field's favourite tool), CSIDH, and SQIsign via the Deuring
> correspondence. Capstone: implement CGL on your own lab-06 graph.
>
> *Status note.* This module states the state of the art as of
> mid-2026; this field moves fast — verify anything you build on.

## 1. The design space

All isogeny crypto instantiates one slogan:

  **secret = a walk in an isogeny graph; public = its endpoints.**

Security rests on path finding / endomorphism-ring hardness
(module 10 §3) — problems with no known Shor-style quantum break, hence
"post-quantum". The schemes differ in *which* graph and *what extra
data* the protocol publishes. That last clause is where SIDH died.

## 2. CGL hashing (2006) — the minimal scheme

Input bits steer a non-backtracking 2-isogeny walk (1 bit per step,
module 10 Q4); output = final j-invariant. Collisions ⇒ endomorphisms.
No trapdoor, no torsion points published — nothing extra to attack.
Slow but conceptually perfect; implement it today on lab 06's graph
(capstone, §7).

## 3. SIDH/SIKE (2011–2022): key exchange and autopsy

**The protocol** (De Feo–Jao–Plût). p = 2^a·3^b·f − 1; E₀
supersingular with E₀[2^a] and E₀[3^b] rational over F_{p²}.
Diffie–Hellman needs Alice's and Bob's walks to *commute*, but the
graph is deeply non-commutative — SIDH forces commutativity by hand:

* Alice's secret: a cyclic subgroup A = ⟨P_A + [s_A]Q_A⟩ ⊆ E₀[2^a];
  she publishes E_A = E₀/A **plus the images φ_A(P_B), φ_A(Q_B)** of
  Bob's torsion basis;
* Bob symmetrically with B ⊆ E₀[3^b], publishing φ_B(P_A), φ_B(Q_A);
* each pushes their own kernel through the other's map:
  E₀/⟨A, B⟩ computed two ways; shared secret = j(E₀/⟨A, B⟩).

The published torsion images are the crutch that makes the diagram
commute — auxiliary information *beyond* the endpoints of the walk.
NIST alternate-finalist SIKE was this, instantiated.

**The break** (Castryck–Decru, July 2022; Maino–Martindale; completed
in full generality by Robert). Key insight, one level up: **Kani's
lemma** embeds the secret 2^a-isogeny φ_A into an easily-computable
isogeny of *abelian surfaces* (dimension 2, products of elliptic
curves) — provided you know φ_A on enough torsion... which is exactly
what SIDH publishes. Recovering the secret key became **minutes on a
laptop** for SIKEp434. The attack:

* does **not** solve generic path finding — module 10's problems stand
  unharmed;
* breaks specifically the *torsion-image* crutch;
* turned its weapon into the field's standard constructive tool:
  higher-dimensional isogenies now *power* new schemes (SQIsign2D,
  FESTA) — the attack was absorbed as infrastructure. Cryptographic
  natural selection at its finest.

Permanent lessons: (i) "extra published structure" is attack surface —
the security proof must cover *everything* published, not just the
clean underlying problem; (ii) a 25-year-old lemma (Kani 1997) can
detonate a NIST finalist — know the mathematics *around* your problem,
which is what this course has been for.

## 4. CSIDH (2018): commutativity done honestly

Instead of forcing commutativity onto the full graph, restrict to where
it exists naturally: supersingular curves **defined over F_p**, whose
F_p-endomorphisms form a *commutative* imaginary quadratic order 𝒪
(module 08 Q4). The ideal-class group cl(𝒪) **acts freely and
transitively** on these curves:

  [𝔞] ∗ E := E / E[𝔞], and [𝔞][𝔟] = [𝔟][𝔞].

A genuine commutative group action ⇒ textbook Diffie–Hellman:
secrets are ideal classes (in practice: exponent vectors over many
small split primes ℓᵢ, each step a Vélu ℓᵢ-isogeny over F_p), public
keys are curves, and *no torsion images are published* — Kani gets no
crutch; CSIDH stands (2026).

Cost of commutativity: the abelian structure re-admits *quantum*
subexponential attacks — Kuperberg's hidden-shift algorithm — so
parameters are debated (CSIDH-512's quantum margin especially);
signatures on the action exist (SeaSign, CSI-FiSh). Non-commutative
SQIsign has no Kuperberg exposure. Trade-offs, as always.

(Historical arc: Couveignes 1997 and Rostovtsev–Stolbunov 2006 proposed
this for *ordinary* curves — module 08 §5's other world; CSIDH's move
to the supersingular-over-F_p sliver made it fast enough to matter.)

## 5. SQIsign (2020–): the Deuring correspondence, weaponized

The deepest scheme, built directly on module 10 §3's equivalence.

**Deuring correspondence**: a precise dictionary

| geometric world | algebraic world |
| --- | --- |
| supersingular E / F̄_p | maximal order 𝒪 ⊂ B_{p,∞} (module 08 §3) |
| isogeny φ : E → E′ | left ideal I of 𝒪 (right order = 𝒪′) |
| deg φ | norm of I |
| φ̂, composition | conjugate ideal, ideal product |

Knowing End(E) = trapdoor: with quaternion arithmetic (the KLPT
algorithm) the holder can *manufacture* isogenies with prescribed
properties that outsiders can't.

**The signature** (identification, Fiat–Shamir-compiled): secret =
End(E_A) for public E_A (equivalently, a secret isogeny from a special
E₀ with known endomorphism ring); challenge = an isogeny walk; response
= a fresh isogeny whose existence certifies knowledge of End(E_A)
without revealing it (zero-knowledge via KLPT-randomized paths).

Practical profile: the **smallest public keys + signatures of all
post-quantum candidates** (both well under a kilobyte — lattice schemes
are kilobytes), at the price of slow signing and genuinely intricate
mathematics. Status as of writing: SQIsign is in NIST's additional
post-quantum signature process (round 2), with the SQIsign2D family
(higher-dimensional response isogenies — Kani again, §3) improving
speed and proofs. Independently, isogenies give VDFs, OPRFs, threshold
schemes; FESTA-style encryption reuses torsion images *with* masking.

## 6. The map of assumptions (memorize this diagram)

```text
 endomorphism-ring problem  ⟸equivalent⟹  path-finding in G_ℓ(p)
        (module 10 §3, Wesolowski)                 hard, Õ(√p) classical
                 │ underlies                              │ underlies
                 ▼                                        ▼
             SQIsign                          CGL hash, SIDH*(dead), FESTA
                                                          │
 group-action inversion (cl(𝒪) on F_p-curves) ─underlies─ CSIDH
        quantum-subexponential (Kuperberg), classical √-hard
```

*Broken things break sideways*: SIDH fell to Kani + published torsion,
not to progress on either root problem. When you read a new isogeny
scheme, first ask: which box does it stand on, and what *extra* does it
publish?

## 7. Capstone project: CGL over your own graph

In a fresh file next to lab 06:

1. load `build_graph(431)`'s adjacency (or work with curves + Vélu
   directly for full marks: at each step, the three 2-torsion points
   give three subgroups; exclude the one that is the dual's kernel —
   the backtracking edge);
2. hash: start at j = 1728's neighbour; consume one input bit per step
   to pick among the 2 non-backtracking edges (order neighbours by a
   fixed rule, e.g. lexicographic on (Re j, Im j) — determinism
   matters); walk |input| steps; output final j;
3. verify: (a) determinism, (b) avalanche — flip one input bit, count
   how many output walks diverge and never re-meet, (c) find a
   collision by brute force on short inputs and *exhibit the
   corresponding cycle* = endomorphism (module 10 Q2 made real);
4. (stretch) measure endpoint distribution of random 60-bit inputs
   against uniform over all 37 vertices — χ², compare with module 10
   Q3's mixing prediction.

If you complete the capstone you have, with your own hands: built
F_{p²}, curves, Vélu, the supersingular graph, and a working isogeny
hash whose collision resistance you can *prove* reduces to computing
endomorphism rings. That is the entire conceptual stack of
isogeny-based cryptography.

## 8. Self-check

<details><summary><b>Q1.</b> Why exactly does publishing φ_A(P_B),
φ_A(Q_B) break SIDH but publishing E_A alone would not?</summary>

E_A alone = a path-finding instance (still hard). The torsion images
determine φ_A's action on E₀[3^b] — partial linear-algebra data about
the secret isogeny. Kani's lemma converts "isogeny known on big
torsion" into a computable higher-dimensional isogeny whose components
*contain* φ_A; the images are precisely the interpolation data the
attack needs. No images, no interpolation, no attack.
</details>

<details><summary><b>Q2.</b> CSIDH publishes only curves. Why doesn't
Kani apply, and what attack surface remains?</summary>

No torsion images ⇒ no interpolation data. Remaining surface: the
commutative group action itself — abelian hidden-shift structure ⇒
Kuperberg's quantum subexponential algorithm; classically, meet-in-the-
middle over the class group ~√#cl. The non-commutative schemes dodge
Kuperberg but must publish more per protocol run — every design leaks
*somewhere*; the craft is choosing where.
</details>

<details><summary><b>Q3.</b> SQIsign's security reduces to the
endomorphism-ring problem — the *same* problem underlying CGL/path
finding. Why is this considered the "right" foundation?</summary>

It is the *minimal* one: by the Eichler/Kohel–Petit–Wesolowski
equivalence (module 10 §3), every isogeny scheme's security implies
endomorphism-ring hardness anyway — an attack on it breaks everything
supersingular at once. Standing directly on the root problem means no
extra published structure to betray you (SIDH's fate) and no auxiliary
assumption to audit. Minimal assumption = maximal honesty.
</details>

<details><summary><b>Q4.</b> Your employer asks: "post-quantum,
smallest possible keys+signatures, signing speed irrelevant, must
survive a decade of cryptanalysis." Argue for and against SQIsign in
three sentences.</summary>

For: smallest PQ keys+signatures known (sub-kilobyte total), founded on
the field's minimal assumption (Q3), a decade-plus of quaternion
cryptanalysis without structural breaks. Against: the mathematics is
the field's most intricate (audit surface!), signing is orders slower
than lattices, and the 2022 SIDH shock shows this domain can produce
sudden total breaks — though that very event *tested* the
endomorphism-ring foundation and it held. Honest answer: hedge —
deploy alongside a lattice scheme (hybrid), as NIST itself recommends
for novel families.
</details>

## 9. Where to go next

* **De Feo, "Mathematics of Isogeny-Based Cryptography"** — the
  canonical lecture notes; everything here, deeper.
* **Silverman, *The Arithmetic of Elliptic Curves*** — the bible for
  modules 06–09's real proofs.
* **Costello, "Supersingular Isogeny Key Exchange for Beginners"** —
  worked SIDH numbers (pre-break, still the best on-ramp).
* **Castryck–Decru, "An Efficient Key Recovery Attack on SIDH"**
  (EUROCRYPT 2023) + Robert's "Breaking SIDH in polynomial time" — read
  the autopsy yourself.
* **The CSIDH and SQIsign papers** (Castryck–Lange–Martindale–Panny–
  Renes 2018; De Feo–Kohel–Leroux–Petit–Wesolowski 2020) and the
  SQIsign NIST submission documents.
* **Arpin et al., "Adventures in Supersingularland"** — the graphs of
  module 10 explored experimentally, at scales beyond the lab.
* This repository's `knowledge/` corpus — the research program you are
  now equipped to read, question, and contribute to.

*— End of the course. Now go break something (toy-scale, with a frozen
protocol and a run record).*
