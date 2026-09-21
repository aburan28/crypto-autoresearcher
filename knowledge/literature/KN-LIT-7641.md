---
id: KN-LIT-7641
type: literature
title: "The principal ideal problem for endomorphism rings of superspecial abelian varieties"
authors:
  - "Wouter Castryck"
  - "Jonathan Komada Eriksen"
  - "Riccardo Invernizzi"
  - "Frederik Vercauteren"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/454"
identifiers:
  eprint: "iacr:2026/454"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/454"
tags: [principal-ideal-problem, quaternion, quaternion-algebra, endomorphism-ring, abelian-variety, supersingular, superspecial, isogeny, deuring, number-theory, cryptanalysis, elliptic-curve]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
A Las Vegas algorithm for the **principal ideal problem (PIP) in matrix rings
`M_g(O)` for `g ≥ 2`**, where `O` is a maximal order in the rational quaternion
algebra `B_{p,∞}` ramified at `p` and `∞`. Under stated heuristic assumptions the
algorithm runs in **expected polynomial time**, and a SageMath implementation is
reported to be efficient in practice with compact output.

The stated main auxiliary result is a method for **finding endomorphisms of
superspecial abelian varieties** (i.e. powers of supersingular elliptic curves)
**with a prescribed kernel**.

## Key claims (as reported)
- PIP in `M_g(O)`, `g ≥ 2`, is solvable in expected polynomial time — **conditional on
  plausible heuristic assumptions**, which the abstract does not enumerate. The paper
  frames this as heuristic, not proven.
- The result is stated only for `g ≥ 2`. The abstract makes **no claim about `g = 1`**,
  i.e. about PIP in a maximal quaternion order itself.
- An implementation exists (SageMath) and is reported efficient with compact output. No
  timings, parameter sizes, or instance families appear in the abstract.
- Auxiliary: endomorphisms of superspecial abelian varieties with prescribed kernel can
  be found.

## Relevance to this program
`M_g(O)` is the endomorphism ring of a superspecial abelian variety `E^g` for a
supersingular `E`, so this is a statement about **how much structure the endomorphism
ring of a higher-dimensional supersingular object gives away**. Two threads meet here:

- **The Deuring/endomorphism-ring machinery** the program tracks (`KN-TECH-050`,
  `KN-TECH-057`, and the SQIsign literature) treats quaternion-order arithmetic as the
  computational substrate of isogeny problems. A polynomial-time PIP at `g ≥ 2` is a
  data point on which of those substrate problems are actually hard.
- **The rank/dimension boundary.** The `g ≥ 2` restriction is exactly the kind of
  boundary the inventor protocol's lossy-projection test is meant to interrogate: the
  algorithm works once there is room to move inside a matrix ring, and the abstract
  does not claim the `g = 1` case follows. That gap is recorded as [[KN-OPEN-024]] and
  is live because [[KN-LIT-7647]] (SoliloQuat) proposes a scheme whose security rests
  on a **short-generator** PIP variant in quaternion orders.

Note the two problems are not the same even at matching `g`: this paper solves PIP
(find *a* generator), while the cryptographic assumption in [[KN-LIT-7647]] is
**SG-PIP** (find a *short* generator). In the commutative case those are separate
stages and Soliloquy died at the second one — see [[KN-TECH-046]] and [[KN-LIT-115]].
The non-commutative status of both stages is collected in [[KN-TECH-081]].

**Does not bear on the prime-field ECDLP.** It concerns quaternionic and supersingular
structure, not the discrete logarithm in `E(F_p)`.

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/454,
retrieved 2026-08-01 (hence `confidence: reported`). Citation checked against the
ePrint record itself: title, four authors, report number, year 2026.

NOT verified here: the heuristic assumptions and whether they are standard; the claimed
expected-polynomial runtime; the practical timings; the prescribed-kernel endomorphism
method; and whether any part of the method extends to `g = 1`. No exponent, cost, or
security claim in this program's ledger is revised on the basis of this entry.
