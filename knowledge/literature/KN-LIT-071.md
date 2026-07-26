---
id: KN-LIT-071
type: literature
title: Constructing elliptic curve isogenies in quantum subexponential time (Childs-Jao-Soukharev)
authors: [Childs Andrew M., Jao David, Soukharev Vladimir]
year: 2014
venue: Journal of Mathematical Cryptology, 8(1):1-29
identifiers:
  eprint: null
  doi: 10.1515/jmc-2012-0016
  arxiv: "1012.4019"
  url: https://arxiv.org/abs/1012.4019
tags: [quantum, hidden-shift, kuperberg, class-group-action, csidh, isogeny, cryptanalysis, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
A subexponential-time QUANTUM algorithm (under GRH) constructing a nonzero isogeny
between two ordinary elliptic curves -- whereas the best classical algorithm was
exponential. Reduces the problem to a hidden-shift / abelian hidden-subgroup
problem and applies Kuperberg's quantum sieve, plus a subexponential algorithm for
evaluating isogenies from kernel ideals.

## Key claims (as reported)
- The first nontrivial cryptographic application of Kuperberg's hidden-shift
  algorithm (Kuperberg, "A subexponential-time quantum algorithm for the dihedral
  hidden subgroup problem," SIAM J. Comput. 35(1):170-188, 2005,
  doi:10.1137/S0097539703436345, the 2^{O(sqrt(log N))} "Kuperberg sieve").
- Effectively breaks the ordinary-curve (Couveignes / Rostovtsev-Stolbunov,
  KN-LIT-070) isogeny key exchange at subexponential QUANTUM cost.

## Relevance to this program
The quantum-cryptanalysis result that sets the security ceiling for the whole
commutative-isogeny branch, including CSIDH (KN-LIT-069, KN-OPEN-014). Its
hidden-shift reduction over the class-group action ties directly to the program's
orientation / volcano work (ISO-AR). Adjacent to the ECDLP mission; note the
CONTRAST -- this subexponential quantum attack is exactly why SIDH chose the
supersingular (non-commutative) setting in the first place (KN-LIT-062).

## Not verified here
Full paper not read; the subexponential quantum complexity and the Kuperberg
reduction relayed from the abstract (hence confidence: reported). Fields (incl.
Kuperberg) confirmed against the JMC/De Gruyter DOI, arXiv:1012.4019, and SIAM DOI
via search, not by fetching the primary pages.
