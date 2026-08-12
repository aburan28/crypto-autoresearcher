---
id: KN-LIT-123
type: literature
title: 'Lattice Attacks on NTRU and LWE: A History of Refinements'
authors: [Albrecht Martin, Ducas Leo]
year: 2021
venue: Survey chapter (ePrint 2021/799)
identifiers:
  eprint: iacr:2021/799
  doi: null
  url: https://eprint.iacr.org/2021/799
tags: [survey, lattice-reduction, bkz, heuristics, ntru, lwe, security-estimate, methodology, history, lattice]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
A survey of how predictions of lattice reduction behaviour have been refined
over four decades, written by two authors central to that refinement. Its
organising question is deliberately narrow: given oracle access for finding
local improvements, what is the *global* behaviour of algorithms like LLL and
BKZ on the specific lattice classes underlying LWE and NTRU?

## Key claims (as reported)
- The worst-case theorems bounding these algorithms are asymptotic and not
  necessarily tight on practical or cryptographic instances; reasoning about
  actual behaviour relies on heuristics and approximations, "some of which are
  known to fail for relevant corner cases."
- The move toward deployment of lattice-based cryptography by standardisation
  bodies, governments and industry made this state of affairs a pressing issue
  and spurred the refinement of those heuristics.
- The survey separates two questions -- the cost of finding local improvements
  versus the global effect of applying them -- and deliberately focuses on the
  second, which the authors say receives less attention.
- The authors include a frank retrospective on their own subfield attack
  (KN-LIT-112): after Kirchner-Fouque showed plain reduction did as well, "the
  new algorithm we invented was completely useless, and old algorithms performed
  just as well, if not better, and were more generally applicable."

## Relevance to this program
The best single entry point to the lattice half of the corpus, and the one to
read before proposing anything in this area. Its central thesis is one the
program has arrived at independently on the ECDLP side: the published complexity
of an attack and the predicted behaviour of its implementation are different
objects joined by heuristics, and the heuristics are where the errors live. The
authors' self-assessment of the subfield attack is also a model of the intended
standard for the program's own negative and superseded results -- record that
the mechanism was unnecessary, in those words, rather than quietly leaving the
original claim standing.

## Not verified here
The ePrint abstract was fetched and read, and the retrospective passage was read
from the PDF text. The survey's technical content -- the specific refinements,
their conditions, and the open problems it lists -- was not extracted in detail
and should be read directly before it is relied on.
