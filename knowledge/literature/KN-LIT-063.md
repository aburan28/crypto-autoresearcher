---
id: KN-LIT-063
type: literature
title: Cryptographic Hash Functions from Expander Graphs (CGL)
authors: [Charles Denis X., Lauter Kristin E., Goren Eyal Z.]
year: 2009
venue: Journal of Cryptology, 22(1):93-113
identifiers:
  eprint: iacr:2006/021
  doi: 10.1007/s00145-007-9002-x
  url: https://link.springer.com/article/10.1007/s00145-007-9002-x
tags: [cgl, supersingular, isogeny-graph, ramanujan-expander, hash, path-finding, post-quantum, adjacent]
confidence: established
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Constructs provably collision-resistant hash functions from Ramanujan expander
graphs where cycle/short-path finding is hard. In the Pizer instantiation the
graph is the supersingular elliptic curves over F_{p^2} with ell-isogenies
(ell != p) as edges (a Ramanujan expander), and the digest is the endpoint of a
message-directed walk.

## Key claims (as reported)
- Collision resistance reduces to isogeny path/cycle-finding hardness between
  supersingular curves; preimage resistance to a related path-finding problem.
- Security is conjectural, tied to those graph-theoretic isogeny problems
  remaining hard. (KLPT-style methods, KN-LIT-073, later broke the quaternion
  analogue.)

## Relevance to this program
The supersingular ell-isogeny graph, its Ramanujan/expander structure, and
isogeny path-finding are exactly the objects underlying the program's isogeny /
volcano and cover-attack investigations (RQ-ISO-001, ISO-AR); CGL is the
foundational reference for the graph-hardness assumptions. NOT affected by the
2022 SIDH torsion-image break (CGL publishes no torsion images).

## Not verified here
Full paper not read; the expander-graph hash construction is textbook-level in
isogeny cryptography (hence confidence: established). Fields confirmed against the
JoC/Springer DOI and IACR ePrint 2006/021 via search, not by fetching the primary
pages.
