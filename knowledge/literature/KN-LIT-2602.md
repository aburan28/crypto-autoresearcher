---
id: KN-LIT-2602
type: literature
title: "Asynchronous Secure Multiparty Computation in Constant Time"
authors:
  - "Ran Cohen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, implementation, mov-fr, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In the setting of secure multiparty computation, a set of mutually distrusting parties wish to securely compute a joint function. It is well known that if the communication model is asynchronous, meaning that messages can be arbitrarily delayed by an unbounded (yet finite) amount of time, secure computation is feasible if and only if at least twothirds of the parties are honest, as was shown by Ben-Or, Canetti, and Goldreich [STOC’93] and by Ben-Or, Kelmer, and Rabin [PODC’94].

## Key claims (as reported)
- The running-time of all currently known protocols depends on the function to evaluate.
- In this work we present the first asynchronous MPC protocol that runs in constant time.
- Our starting point is the asynchronous MPC protocol of Hirt, Nielsen, and Przydatek [Eurocrypt’05, ICALP’08].
- We integrate threshold fully homomorphic encryption in order to reduce the interactions between the parties, thus completely removing the need for the expensive king-slaves approach taken by Hirt et al..

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96140175 (1).pdf`
- `downloads/96140175 (2).pdf`
- `downloads/96140175 (3).pdf`
- `downloads/96140175 (4).pdf`
- `downloads/96140175.pdf`
