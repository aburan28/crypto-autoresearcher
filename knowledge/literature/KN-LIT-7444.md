---
id: KN-LIT-7444
type: literature
title: "Vector Commitments and their Applications"
authors:
  - "Dario Catalano"
  - "Dario Fiore"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We put forward the study of a new primitive that we call Vector Commitment (VC, for short). Informally, VCs allow to commit to an ordered sequence of q values (m1 , . . . , mq ) in such a way that one can later open the commitment at specific positions (e.g., prove that mi is the i-th committed message).

## Key claims (as reported)
- For security, Vector Commitments are required to satisfy a notion that we call position binding which states that an adversary should not be able to open a commitment to two different values at the same position.
- Moreover, what makes our primitive interesting is that we require VCs to be concise, i.e. the size of the commitment string and of its openings has to be independent of the vector length.
- We show two realizations of VCs based on standard and well established assumptions, such as RSA, and Computational Diffie-Hellman (in bilinear groups).
- Next, we turn our attention to applications and we show that Vector Commitments are useful in a variety of contexts, as they allow for compact and efficient solutions which significantly improve previous works either in terms of efficiency of the resulting solutions, or in terms of ”quality” of the underlying assumption, or both.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/77780054 (1).pdf`
- `downloads/77780054 (2).pdf`
- `downloads/77780054 (3).pdf`
- `downloads/77780054 (4).pdf`
- `downloads/77780054.pdf`
