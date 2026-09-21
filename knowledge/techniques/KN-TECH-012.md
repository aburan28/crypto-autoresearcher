---
id: KN-TECH-012
type: technique
title: Isotypic (equivariant) decomposition of symmetric relation systems
tags: [representation-theory, isotypic, group-algebra, idempotents, symmetry, equivariant, block-decomposition, semaev, ecdlp]
confidence: reported
complexity: block-diagonalizes a G-invariant operator into isotypic blocks; superlinear LA cost sum_b LA(dim_b) < LA(total); storage down by ~|G|
applicability: harvesting/solving relation systems invariant under a finite group G (non-modular case, p not dividing |G|)
source_refs: [KN-LIT-030, KN-LIT-031, KN-LIT-004]
added: 2026-07-22
superseded_by: null
---

## Method
When a relation space carries an action of a finite group G with p not dividing
|G|, Maschke + Wedderburn (KN-LIT-030) guarantee it splits as a direct sum of
*isotypic* components, and the group algebra C[G] decomposes into matrix blocks.
Exact character idempotents (averages over G) project onto each block, so a
G-invariant operator (e.g. the relation matrix) becomes block-diagonal. One
harvests and solves per block, on orbit representatives.

## Complexity indicator
Because linear-algebra cost is superlinear in dimension, sum_b LA(dim_b) can be
below LA(total) once the operator is split; storage drops by a factor ~|G| (orbit
representatives). Faugere-Svartz (KN-LIT-031) realize exactly this as
character-graded block splitting of F4/F5 Macaulay matrices for commutative G.

## Program usage
The mechanism of the program's equivariant index-calculus candidate
(RQ-EQJ-001, EXP-EQJ-001): decompose the Semaev fiber-product relation space
under G = S_{m-1} semidirect (Z/2)^{m-1} into isotypic blocks and measure
per-block relation counts, ranks, and blind-descent success. This is a
DECOMPOSITION (exact idempotent projection), distinct from FHJRV symmetrized
harvesting (KN-LIT-004), which exploits only the trivial-isotype invariants, and
from statistical character *buckets* (a filter, not a splitting).

## Applicability limits
The likely obstruction: solution tuples come in G-orbits, so the trivial isotype
provably carries a large relation share -- exactly what symmetrization already
uses. If block multiplicities are |G|-symmetric with all relations in the
trivial/sign blocks, the method reduces to FHJRV with bookkeeping (disguised
repetition). The advantage exists only if non-trivial blocks carry an
asymptotically non-vanishing, useful share -- unestablished, hence confidence:
reported. Requires the non-modular condition (p does not divide |G|), true at
toy sizes.
