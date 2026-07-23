---
id: KN-OPEN-011
type: open_problem
title: Do lattice-reduction / Hidden-Number-Problem techniques give any advantage for the plain ECDLP (no nonce leakage), or are they confined to the partial-information / side-channel model?
tags: [lattice, hidden-number-problem, ecdlp, lattice-reduction, leakage-model, boundary, open]
confidence: reported
status: open
source_refs: [KN-LIT-043, KN-LIT-044, KN-TECH-019]
added: 2026-07-23
superseded_by: null
---

## Statement
Lattice methods break EC discrete-log signatures spectacularly WHEN partial nonce
information leaks (HNP + lattice reduction, KN-TECH-019). Is there any way to turn
lattice reduction / HNP-style machinery against the PLAIN ECDLP -- recovering a
discrete log with no leaked bits, no biased nonces, no side channel -- or is the
lattice advantage provably confined to the partial-information model?

## Current state (as reported)
All known lattice attacks on EC signatures (KN-LIT-043, KN-LIT-044, KN-LIT-045)
require leaked/biased nonce bits to make the hidden value SMALL enough for a
lattice to find; with uniformly random secret nonces the HNP instance is
underdetermined and the lattice carries no signal. No lattice-reduction attack on
the bare ECDLP is known, and the generic square-root bound (KN-TECH-005) plus the
program's index-calculus results (KN-OPEN-001) are the relevant hardness picture.
Whether some embedding of the ECDLP into a lattice could expose exploitable
shortness is, to the program's knowledge, not ruled out by a theorem.

## Why it matters here
It sharply delimits the lattice/ECDLP relationship for the corpus: lattice methods
are (as far as known) an implementation/leakage concern, ORTHOGONAL to the
program's core question of plain-ECDLP hardness. Making this boundary explicit
prevents conflating "ECDSA fell to a nonce leak" with "ECDLP is weak," and frames
any future attempt to embed ECDLP structure into a lattice as a well-posed,
almost-certainly-negative probe rather than a known route. Cross-domain analogue:
whether ECDLP index-calculus structure has any lattice counterpart (KN-OPEN-012).
