---
id: KN-LIT-5452
type: literature
title: "On the Connection between Leakage Tolerance and Adaptive Security"
authors:
  - "Jesper Buus Nielsen"
  - "Daniele Venturi"
  - "Angela Zottarel"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, provable-security, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We revisit the context of leakage-tolerant interactive protocols as defined by Bitanski, Canetti and Halevi (TCC 2012). Our contributions can be summarized as follows: 1.

## Key claims (as reported)
- For the purpose of secure message transmission, any encryption protocol with message space M and secret key space SK tolerating poly-logarithmic leakage on the secret state of the receiver must satisfy |SK| ≥ (1 − )|M|, for every 0 <  ≤ 1, and if |SK| = |M|, then the scheme must use a fresh key pair to encrypt each message.
- More generally, we show that any n party protocol tolerates leakage of ≈ poly(log κ) bits from one party at the end of the protocol execution, if and only if the protocol has passive adaptive security against an adaptive corruption of one party at the end of the protocol execution.
- This shows that as soon as a little leakage is tolerated, one needs full adaptive security.
- In case more than one party can be corrupted, we get that leakage tolerance is equivalent to a weaker form of adaptivity, which we call semi-adaptivity.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/77780494 (1).pdf`
- `downloads/77780494 (2).pdf`
- `downloads/77780494 (3).pdf`
- `downloads/77780494 (4).pdf`
- `downloads/77780494.pdf`
