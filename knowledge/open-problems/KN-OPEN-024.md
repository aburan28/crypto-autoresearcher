---
id: KN-OPEN-024
type: open_problem
title: Does the rank-1 (quaternion-order) principal ideal problem inherit the tractability now shown for matrix rings M_g(O), g >= 2?
tags: [principal-ideal-problem, quaternion, quaternion-algebra, order, short-generator, unit-group, endomorphism-ring, superspecial, abelian-variety, lattice-isomorphism-problem, non-commutative, open]
confidence: reported
status: open
source_refs: [KN-LIT-7641, KN-LIT-7647, KN-TECH-081, KN-TECH-046, KN-LIT-115, KN-LIT-116, KN-LIT-7648, KN-OPEN-012]
added: 2026-08-01
superseded_by: null
---

## Statement

Two 2026 papers sit on opposite sides of a one-step gap, and neither closes it.

- [[KN-LIT-7641]] (Castryck, Eriksen, Invernizzi, Vercauteren) gives a Las Vegas
  algorithm for the **principal ideal problem in `M_g(O)` for `g ≥ 2`**, `O` a maximal
  order in `B_{p,∞}`, in **heuristic expected polynomial time**, with a working
  SageMath implementation. The result is stated only for `g ≥ 2`.
- [[KN-LIT-7647]] (Mendelsohn, Nelson) proposes a public-key scheme whose security
  **assumes the hardness of the short-generator principal ideal problem (SG-PIP) in
  orders of quaternion algebras** — i.e. at `g = 1` — noting that it is not known
  whether the commutative-case attacks generalize to the non-commutative setting.

The open problem, stated precisely, is **two questions that must not be merged**:

**(Q1) Rank.** Does PIP in a maximal order `O ⊂ B_{p,∞}` itself — the `g = 1` case —
admit a polynomial or subexponential algorithm? Does any part of the `M_g(O)` method
descend, or is `g ≥ 2` essential to it?

**(Q2) Stage.** Even granting an efficient `g = 1` PIP, does a **short**-generator
recovery step exist? In the commutative case this is a separate, later, and historically
decisive stage: decoding the **log-unit lattice** ([[KN-LIT-115]]), which is where
Soliloquy actually broke ([[KN-TECH-046]]). The non-commutative analogue requires a
unit-lattice structure for the unit group of a quaternion order that this corpus does
not record as existing.

## Why it matters

Not hypothetically. Three live consequences:

1. **A deployed-adjacent assumption depends on it.** [[KN-LIT-7647]] relays a Eurocrypt
   2025 reduction from **rank-2 module-LIP instances underlying HAWK to nrd-PIP**. If
   that reduction is as stated, quaternion-order PIP is not an exotic curiosity — it is
   upstream of a NIST-round lattice signature's structural security argument. *That
   reduction is relayed, not verified by this program*, and confirming it is the
   cheapest first move on this entry.
2. **The geometric reading is about supersingular structure.** `M_g(O)` is
   `End(E^g)` for supersingular `E`. So (Q1) asks whether the endomorphism ring of a
   **single** supersingular curve gives away as much as that of a power of it — a
   question in the same family as the Deuring-correspondence hardness the isogeny thread
   rests on ([[KN-TECH-081]], [[KN-LIT-7656]]).
3. **The symmetric failure mode is available in both directions.** Assuming
   non-commutativity protects the problem is the error [[KN-LIT-7644]] documents
   (a class-group obstruction that only complicated the algorithm). Assuming the `g ≥ 2`
   result "obviously" descends is the opposite error. Neither is currently justified.

## Current state (as reported)

- `g ≥ 2`: heuristic expected polynomial time, implemented. The heuristics are **not
  enumerated in the abstract** and were not read.
- `g = 1`, stage 1 (PIP): **no algorithm known to this corpus**. Absence of a record is
  not absence of a result — no systematic literature search on rank-1 quaternion-order
  PIP was run beyond the 2026-08-01 sweep that raised this entry.
- `g = 1`, stage 2 (SG-PIP): assumed hard by [[KN-LIT-7647]]; no analysis either way in
  this corpus.
- **Adjacent warning shot:** [[KN-LIT-7648]] breaks an isomorphism assumption over
  quadratic forms in classical polynomial time using **genus and spinor-genus** theory —
  arithmetic invariants of the ambient structure, no lattice reduction. Whatever
  eventually settles (Q1)/(Q2) may well come from that direction rather than from
  lattice algorithmics.

## What would resolve it

In increasing cost, each independently useful:

1. **Read the two papers.** Extract (a) the exact heuristic assumptions in
   [[KN-LIT-7641]] and (b) whether any step is rank-essential. Cheap, and it converts
   this entry from "two abstracts appear adjacent" to a real statement.
2. **Verify the Eurocrypt 2025 module-LIP → nrd-PIP reduction** and ingest it. Decides
   whether (Q1) is upstream of HAWK or merely adjacent to it.
3. **Characterize the unit group of a maximal order in `B_{p,∞}`** as a lattice under
   the natural logarithmic embedding, and state whether a stage-2 decoding argument is
   even formulable. This is the mathematical crux of (Q2) and is answerable in the
   literature, not by experiment.
4. Only then: any experimental work. Nothing here needs compute yet.

## Not verified here

**No claim is made that (Q1) or (Q2) resolves either way**, and no attack on SoliloQuat,
HAWK, or any quaternion-order assumption is proposed or implied. Both source papers are
recorded at `confidence: reported` from abstracts retrieved 2026-08-01; neither was read
in full. The Eurocrypt 2025 reduction is relayed from [[KN-LIT-7647]]'s abstract and is
not itself an entry in this corpus. The commutative two-stage account is taken from
[[KN-TECH-046]] and inherits its caveats. **Does not bear on the ECDLP.**
