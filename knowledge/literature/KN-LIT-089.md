---
id: KN-LIT-089
type: literature
title: The Discrete Logarithm Problem on Elliptic Curves of Trace One
authors: [Smart Nigel P.]
year: 1999
venue: Journal of Cryptology, 12(3):193-196
identifiers:
  eprint: null
  doi: 10.1007/s001459900052
  url: https://link.springer.com/article/10.1007/s001459900052
tags: [anomalous, trace-one, smart-attack, additive-transfer, linear-time, special-curves, prime-field, parameter-validation, ecdlp, hygiene]
confidence: established
citation_verified: web
added: 2026-07-24
superseded_by: null
---

## Contribution
The most widely cited statement of the anomalous-curve attack, and the one
usually meant by "the Smart attack." An elementary lifting argument gives a
linear-time algorithm for the ECDLP on curves of trace one, i.e. curves with
#E(F_p) = p. The paper's framing is explicitly a parameter-selection warning:
alongside the supersingular curves already excluded by MOV (KN-LIT-084), one
must also exclude every curve whose group order equals the field order.

## Key claims (as reported)
- Linear-time ECDLP on trace-one curves, where "linear" counts basic group
  operations (proven; the paper calls the technique elementary).
- The attack is disjoint from MOV: MOV excludes trace zero (supersingular),
  this excludes trace one.
- Practical consequence stated by the author: curve selection must test
  #E(F_p) != p.

## Relevance to this program
The trio KN-LIT-087/088/089 fixes the anomalous boundary from three
directions, and Smart's is the version whose framing matters most here: it is
a *validation requirement*, not just a theorem. Any curve this program
generates for measurement -- including toy curves at 8 to 32 bits, where
#E = p happens far more often by accident than at cryptographic size -- must
have its order checked against the field order, or a measured "speedup" may be
the Smart attack in disguise. This is the cheapest of all instance-validity
preconditions and belongs in the harness, not in the analysis. See
KN-TECH-033 and KN-TECH-034.

## Not verified here
Full paper not fetched (it is three pages). Author, title, venue
(J. Cryptology 12(3):193-196, 1999; received Dec 1997, revised Mar 1998),
DOI, and the HP Labs technical-report precursor HPL-97-128 were confirmed
against the Springer article record; the abstract and introduction were read
from the publisher page. The lifting argument itself was not re-derived.
