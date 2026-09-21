---
id: KN-TECH-081
type: technique
title: The principal ideal problem beyond commutative orders - quaternion orders, matrix rings, and the non-commutative gap
tags: [principal-ideal-problem, quaternion, quaternion-algebra, endomorphism-ring, order, ideal-lattice, lattice-isomorphism-problem, class-group, unit-group, short-generator, non-commutative, superspecial, abelian-variety, number-theory, lattice]
confidence: reported
complexity: "Commutative cyclotomic case (KN-TECH-046): PIP quantum-polynomial, short-generator recovery efficient for prime-power cyclotomics, composed Ideal-SVP at approximation factor exp(O~(sqrt(n))). Non-commutative case: PIP in M_g(O) for g >= 2 over a maximal order O in B_{p,infty} reported in heuristic expected polynomial time (KN-LIT-7641); PIP and SG-PIP in a maximal quaternion order itself (g = 1) have no comparable published algorithm known to this corpus. The two-stage structure - find a generator, then shorten it - is what must be tracked, not a single exponent"
applicability: "Orders in quaternion algebras over Q and matrix rings over them; endomorphism rings of supersingular elliptic curves (g = 1) and of superspecial abelian varieties E^g (g >= 2). Bears on isogeny-based schemes through the Deuring correspondence and on lattice schemes through the module-LIP-to-nrd-PIP direction. Does NOT bear on the ECDLP"
source_refs: [KN-TECH-046, KN-LIT-115, KN-LIT-116, KN-LIT-7641, KN-LIT-7647, KN-LIT-7648, KN-LIT-7649, KN-LIT-7650, KN-LIT-7642, KN-OPEN-024, KN-OPEN-012]
added: 2026-08-01
superseded_by: null
---

## Why a separate entry from KN-TECH-046

`KN-TECH-046` documents the **commutative** structured-lattice attack line: cyclotomic
fields, class groups, log-unit lattices, Stickelberger. It is complete for what it
covers and this entry does not restate it.

What it does not cover is that the same problem name — *the principal ideal problem* —
now appears in **three structurally different settings** in the 2026 literature, with
three different states of knowledge, and that they are routinely cited in the same
breath. This entry exists to keep them apart, because conflating them is the easiest
available way for this program to make a false novelty or false-hardness call.

## The three settings

| Setting | Ring | PIP status | Short-generator status |
|---|---|---|---|
| Commutative | `O_K`, `K` cyclotomic | quantum polynomial (`KN-TECH-046`, `KN-LIT-117`) | efficient for prime-power cyclotomics (`KN-LIT-115`) |
| Non-commutative, rank 1 | maximal order `O ⊂ B_{p,∞}` | **no algorithm known to this corpus** | **assumed hard** — the SoliloQuat assumption (`KN-LIT-7647`) |
| Non-commutative, rank ≥ 2 | `M_g(O)`, `g ≥ 2` | heuristic expected polynomial (`KN-LIT-7641`) | not addressed by that paper |

The middle row is the load-bearing one and is currently an assumption, not a result in
either direction. [[KN-OPEN-024]] states it precisely.

## The two-stage discipline

The single most transferable thing in this area is that **PIP and SG-PIP are different
problems and break at different times**. The commutative history is unambiguous:

1. **Stage 1 — find some generator.** Reduces to `S`-unit group computation; quantum
   polynomial time in arbitrary number fields.
2. **Stage 2 — shorten it.** Decode the **log-unit lattice**. This is where Soliloquy
   actually died, and it was the step earlier sketches asserted without proof until
   `KN-LIT-115` proved it.

Therefore: **a cryptographic proposal resting on "PIP is hard" must say which stage it
means**, and an algorithmic result solving PIP does not by itself break a scheme
resting on SG-PIP. `KN-LIT-7641` (stage 1, `g ≥ 2`) and `KN-LIT-7647` (stage 2, `g = 1`)
are exactly this pair, and reading either as bearing directly on the other would be
wrong.

Corollary for the non-commutative case: the natural attack question is not "can PIP be
solved?" but **"does a quaternion order have a unit-lattice structure that supports a
stage-2 decoding argument?"** — the reduced-norm-one unit group of an order in `B_{p,∞}`
is not the rank-`r` free-modulo-torsion object Dirichlet's unit theorem hands you in the
commutative case. This corpus records no answer, and this entry asserts none.

## Where the rank boundary comes from

`KN-LIT-7641`'s restriction to `g ≥ 2` is not incidental. `M_g(O)` for `g ≥ 2` has room
for elementary-matrix-style manipulation that a rank-1 order does not, and `M_g(O)` is
the endomorphism ring of the superspecial abelian variety `E^g`. So the same result
reads two ways:

- **algebraically**, as "matrix rings over orders are more tractable than orders";
- **geometrically**, as "the endomorphism ring of `E^g` gives away more than that of
  `E`" — a statement about how much structure higher-dimensional supersingular objects
  expose, which is directly relevant to the higher-dimensional isogeny constructions
  (Kani-style embeddings, `(g ≥ 2)`-dimensional SQIsign variants) the corpus already
  tracks.

Whether the second reading has any consequence for those constructions is **not
established here**. It is the reason the entry exists rather than a claim it makes.

## How PIP reaches lattice cryptography

Not only through ideal lattices. `KN-LIT-7647` relays a Eurocrypt 2025 reduction from
**rank-2 module-LIP instances underlying HAWK to nrd-PIP** — i.e. the lattice
isomorphism problem in the module setting pulls quaternion-order PIP into a
lattice-scheme security argument. That reduction is **not itself an entry in this
corpus and has not been checked**; it is recorded here as the stated reason
quaternion-order PIP has attracted attention, not as an established link.

`KN-LIT-7648` is the adjacent cautionary case: an isomorphism assumption over quadratic
forms that collapsed under **genus and spinor-genus** theory, in classical polynomial
time and with no lattice reduction. Arithmetic invariants of the *ambient algebraic
structure*, not lattice geometry, did the work — the same shape of threat this table's
middle row would face.

## Known limits of this entry

- **Everything in the non-commutative rows is `reported`**, from abstracts read on
  2026-08-01. No paper in this area was read in full, no algorithm was reproduced, and
  no experiment in this program has touched PIP in any setting.
- **No hardness assessment is made.** The middle row being blank is a statement about
  this corpus's knowledge, not evidence that the problem is hard. Premature closure in
  either direction is the failure mode `docs/inventor-protocol.md` names.
- **No ECDLP bearing.** Nothing in this technique family touches the discrete logarithm
  in `E(F_p)`. It is recorded because the program's isogeny thread runs through
  quaternion orders, not because it is an ECDLP attack route.
- The commutative complexity figures are copied from `KN-TECH-046` and inherit its
  caveats, including its GRH and heuristic dependencies and its explicit statement that
  **no deployed Ring-LWE or Module-LWE parameter set is affected**.
