---
id: KN-LIT-062
type: literature
title: Towards quantum-resistant cryptosystems from supersingular elliptic curve isogenies (SIDH)
authors: [Jao David, De Feo Luca, Plut Jerome]
year: 2014
venue: J. Math. Cryptology 8(3):209-247 (PQCrypto 2011, LNCS 7071:19-34)
identifiers:
  eprint: iacr:2011/506
  doi: 10.1515/jmc-2012-0015
  url: https://eprint.iacr.org/2011/506
tags: [sidh, supersingular, isogeny, key-exchange, torsion-points, post-quantum, foundational, adjacent]
confidence: established
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Proposes SIDH (Supersingular Isogeny Diffie-Hellman): Alice and Bob each compute
a secret isogeny by walking the supersingular ell-isogeny graph (ell=2 and ell=3)
over F_{p^2}, then reach a shared curve / j-invariant despite the noncommutative
endomorphism ring. Security rests on the conjectured hardness of computing the
secret isogeny. PQCrypto 2011 (Jao-De Feo); full version J. Math. Cryptol. 2014
(De Feo-Jao-Plut).

## Key claims (as reported)
- To arrive at a shared commutative square, each party PUBLISHES the images of the
  counterparty's torsion-point basis under its secret isogeny (auxiliary points)
  -- the leakage later shown fatal (KN-LIT-065, KN-LIT-067).
- Motivated by the supersingular case resisting the subexponential quantum attack
  that breaks the ordinary case (KN-LIT-071).

## Relevance to this program
Directly adjacent to the ECDLP mission: isogeny walks, Velu computation, and
endomorphism-ring structure are shared machinery, and the torsion-image leakage
motif connects to the program's isogeny transfer/cover attacks and volcano
structure (RQ-ISO-001, ISO-AR). Supersingular (F_{p^2}) setting, distinct from
the ordinary-prime-field ECDLP target.

## Not verified here
Full paper not read; the SIDH construction is textbook-level in isogeny
cryptography (hence confidence: established); its being broken in 2022 is recorded
separately (KN-LIT-065..067). Fields for both PQCrypto 2011 and JMC 2014 confirmed
against IACR ePrint 2011/506 and the De Gruyter DOI via search, not by fetching
the primary pages.
