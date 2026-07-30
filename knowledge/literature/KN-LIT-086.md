---
id: KN-LIT-086
type: literature
title: The Improbability That an Elliptic Curve Has Subexponential Discrete Log Problem under the Menezes-Okamoto-Vanstone Algorithm
authors: [Balasubramanian R., Koblitz Neal]
year: 1998
venue: Journal of Cryptology, 11(2):141-145
identifiers:
  eprint: null
  doi: 10.1007/s001459900040
  url: https://link.springer.com/article/10.1007/s001459900040
tags: [mov, embedding-degree, genericity, random-curve, probability, transfer, hasse-interval, prime-field, ecdlp, baseline]
confidence: reported
citation_verified: web
added: 2026-07-24
superseded_by: null
---

## Contribution
Quantifies how rare the MOV-vulnerable case is. Two results: first, that the
obviously necessary condition l | (q^k - 1) is also *sufficient* for the MOV
reduction to be realizable, under a mild condition (l does not divide q-1)
that holds in practical parameter choices; second, an improved upper bound on
the frequency of prime pairs (l, p) with l | (p^k - 1) for small k and l in the
Hasse interval.

## Key claims (as reported)
- l | (q^k - 1) is necessary and sufficient for MOV in practice (proven under
  the stated mild condition). The authors note this is somewhat surprising:
  the condition had been widely assumed to be far from sufficient.
- For a random prime p and a random elliptic curve over F_p with a prime
  number of points, the probability that the embedding degree is small enough
  for MOV to be subexponential is negligible -- the bound reported downstream
  (Luca-Mireles-Shparlinski) as O(x^{-1} log^9 x (log log x)^2) for p in
  [x/2, x].
- Therefore the generic ordinary curve has embedding degree of size comparable
  to the field, and pairing transfer is not a threat to it.

## Relevance to this program
This is the entry that makes the pairing route *closed rather than untested*
for the program's target class. GOAL-CRYPTO-001 scopes to ordinary curves of
large prime order over prime fields; for those, MOV/Frey-Rück are
overwhelmingly inapplicable, so an idea proposing a pairing transfer must
either supply a curve family with artificially small embedding degree (which is
outside the declared scope) or be screened as `known`. It is also the reason
the program cannot treat a supersingular or small-k success as evidence about
its target: the curve classes are separated by this probability bound, not by
a matter of degree. See KN-TECH-032.

## Not verified here
Full paper not fetched. Authors, title, venue (J. Cryptology 11(2):141-145,
1998) and DOI confirmed against the Springer article record and the IAS
repository entry; the abstract was read. The explicit probability bound quoted
above comes from the Luca-Mireles-Shparlinski restatement
(doi:10.1215/ijm/1258131069), not from the original paper's own wording, and
was not re-derived.
