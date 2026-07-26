---
id: KN-TECH-027
type: technique
title: CSIDH commutative class-group action and the quantum hidden-shift attack
tags: [csidh, class-group-action, commutative, hidden-shift, kuperberg, quantum, volcano, isogeny, adjacent]
confidence: established
complexity: classical vectorization ~O(sqrt(#Cl)) sub-exponential in log p via class group; quantum subexponential 2^{O(sqrt(log p))} (Kuperberg)
applicability: non-interactive isogeny key exchange / group action; survived the SIDH break
source_refs: [KN-LIT-069, KN-LIT-070, KN-LIT-071]
added: 2026-07-23
superseded_by: null
---

## Method
The ideal class group Cl(O) of an imaginary quadratic order O acts (freely,
transitively on a suitable set) on supersingular curves over the PRIME field F_p
by isogenies, a COMMUTATIVE group action (Couveignes' hard homogeneous space,
KN-LIT-070; CSIDH, KN-LIT-069). A public key is [a]*E_0; shared secret is
[a][b]*E_0 = [b][a]*E_0. No torsion-point images are published.

## Security / complexity
- Classical: recovering the secret ideal (vectorization) via class-group /
  meet-in-the-middle is subexponential in log p.
- QUANTUM: the abelian hidden-shift structure makes it vulnerable to Kuperberg's
  sieve (KN-LIT-071), giving subexponential 2^{O(sqrt(log p))} quantum cost --
  which drives CSIDH's (large) parameter sizing and is actively debated
  (KN-OPEN-014).
- Because it reveals no torsion images, CSIDH is UNAFFECTED by the 2022 SIDH
  break.

## Relevance to this program
The commutative branch that survived the break; its class-group action, CM
structure, and volcano/orientation are directly the program's isogeny-volcano
research objects (RQ-ISO-001, ISO-AR). The orientation of a supersingular curve by
an imaginary quadratic order is exactly the "orientation" the program's ISO-AR
work manipulates. Adjacent to the ECDLP mission (CM / class-group machinery is
shared).

## Applicability limits
Adjacent (post-quantum) domain, not the ECDLP mission. The quantum subexponential
attack is asymptotic with contested concrete constants (KN-OPEN-014). Commutativity
is what enables both the efficient action AND the quantum attack -- the trade SIDH
avoided by going non-commutative (at the cost of torsion leakage).
