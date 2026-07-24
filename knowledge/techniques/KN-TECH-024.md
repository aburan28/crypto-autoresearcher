---
id: KN-TECH-024
type: technique
title: Supersingular isogeny graphs and the CGL hash
tags: [supersingular, isogeny-graph, ramanujan-expander, cgl, hash, path-finding, isogeny, adjacent]
confidence: established
complexity: graph is (ell+1)-regular Ramanujan on ~p/12 vertices; generic path-finding ~O(p^{1/2}) classical, O(p^{1/4}) over F_p / quantum
applicability: hashing and hardness assumptions from walks in the supersingular ell-isogeny graph
source_refs: [KN-LIT-063, KN-LIT-078, KN-LIT-079]
added: 2026-07-23
superseded_by: null
---

## Method
The supersingular ell-isogeny graph has as vertices the supersingular elliptic
curves over F_{p^2} (~p/12 of them, up to isomorphism) and as edges the
ell-isogenies (ell != p); it is (ell+1)-regular and Ramanujan (optimal expander).
The CGL hash (KN-LIT-063) walks this graph under message-bit control and outputs
the endpoint's j-invariant; collision/preimage resistance reduce to isogeny
cycle/path-finding hardness.

## Complexity indicator
The pure path-finding problem (no auxiliary data) has classical cost
~Otilde(p^{1/2}) by meet-in-the-middle, improved to Otilde(p^{1/4}) on the
F_p-rational subgraph (Delfs-Galbraith, KN-LIT-078) and quantumly (Biasse-Jao-
Sankar, KN-LIT-079). Endpoint j-invariants leak no torsion data, so this family
is UNAFFECTED by the 2022 SIDH break.

## Relevance to this program
The graph, its Ramanujan/expander structure, and isogeny path-finding are the
objects underlying the program's isogeny / volcano and cover-attack work
(RQ-ISO-001, ISO-AR). The expander mixing and birthday/meet-in-the-middle cost
models are kin to the program's own walk-based cost accounting (KN-TECH-006).

## Applicability limits
Adjacent to the ECDLP mission (supersingular F_{p^2} setting, not ordinary prime-
field ECDLP). Security is conjectural (path-finding hardness); the quaternion
analogue is NOT hard (KLPT, KN-LIT-073), and endomorphism-ring knowledge collapses
path-finding (KN-LIT-074), so "hardness" is precisely the endomorphism-ring
assumption (KN-OPEN-013).
