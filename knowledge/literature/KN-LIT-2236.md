---
id: KN-LIT-2236
type: literature
title: "A Simpler and More Efficient Reduction of DLog to CDH for Abelian Group Actions"
authors:
  - "Steven Galbraith"
  - "Yi-Fu Lai"
  - "Hart Montgomery"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, dlp, isogeny, mpc, pqc, protocol, provable-security, sidh-csidh, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Abelian group actions appear in several areas of cryptography, especially isogeny-based post-quantum cryptography. A natural problem is to relate the analogues of the computational Diffie-Hellman (CDH) and discrete logarithm (DLog) problems for abelian group actions.

## Key claims (as reported)
- Galbraith, Panny, Smith and Vercauteren (Mathematical Cryptology ’21) gave a quantum reduction of DLog to CDH, assuming a CDH oracle with perfect correctness.
- Montgomery and Zhandry (Asiacrypt ’22, best paper award) showed how to convert an unreliable CDH oracle into one that is correct with overwhelming probability.
- However, while a theoretical breakthrough, their reduction is quite inefficient: if the CDH oracle is correct with probability ε then their algorithm to amplify the success requires on the order of 1/ε21 calls to the CDH oracle.
- We revisit this line of work and give a much simpler and tighter algorithm.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14602155 (1).pdf`
- `downloads/14602155.pdf`
