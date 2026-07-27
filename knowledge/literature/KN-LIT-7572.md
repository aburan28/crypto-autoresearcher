---
id: KN-LIT-7572
type: literature
title: More on average case vs approximation complexity
authors: [Alekhnovich Michael]
year: 2003
venue: FOCS 2003, pp. 298-307; journal version Computational Complexity 20:755-786 (2011)
identifiers:
  eprint: null
  doi: 10.1007/s00037-011-0029-x
  url: null
tags: [code-based, syndrome-decoding, provable-security, complexity-theory, lpn, random-codes]
confidence: reported
citation_verified: web
added: 2026-07-27
superseded_by: null
---

## Contribution
Builds public-key encryption whose security reduces to the hardness of decoding
a *random* linear code at low error rate -- that is, to an average-case
assumption over random codes with no hidden algebraic structure and therefore no
structural attack surface of the KN-LIT-7569 kind. The price is inefficiency
relative to McEliece-type schemes.

## Key claims (as reported)
- Public-key encryption is constructible from random-code decoding hardness
  alone, without a trapdoor code family.
- Connects average-case coding hardness to approximation complexity, the paper's
  broader theme.

## Relevance to this program
The reference point for what code-based security looks like when the second
assumption of KN-LIT-7564 (indistinguishability of the public code) is removed
entirely. It is the honest answer to "can code-based crypto avoid structural
attacks?" -- yes, at a cost nobody deploys -- and it bounds how much of
code-based cryptanalysis is really about generic decoding versus about hidden
structure. Cited in KN-TECH-056 and KN-OPEN-021.

## Not verified here
Primary paper not fetched. Author, title, venue (FOCS 2003, pages 298-307), year,
and the Computational Complexity journal version with its DOI confirmed via
search against DBLP and the FOCS 2003 program. The characterization of the
cryptosystem's assumption is relayed from secondary summaries and was not read
from the primary text.
