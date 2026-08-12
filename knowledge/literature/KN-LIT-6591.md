---
id: KN-LIT-6591
type: literature
title: "Short Signatures from Regular Syndrome Decoding in the Head"
authors:
  - "Eliana Carozza"
  - "Geoffroy Couteau"
  - "Antoine Joux"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, pqc, quantum, signature, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce a new candidate post-quantum digital signature scheme from the regular syndrome decoding (RSD) assumption, an established variant of the syndrome decoding assumption which asserts that it is hard to find w-regular solutions to systems of linear equations over F2 (a vector is regular if it is a concatenation of w unit vectors). Our signature is obtained by introducing and compiling a new 5-round zero-knowledge proof system constructed using the MPC-in-thehead paradigm.

## Key claims (as reported)
- At the heart of our result is an efficient MPC protocol in the preprocessing model that checks correctness of a regular syndrome decoding instance by using a share ring-conversion mechanism.
- The analysis of our construction is non-trivial and forms a core technical contribution of our work.
- It requires careful combinatorial analysis and combines several new ideas, such as analyzing soundness in a relaxed setting where a cheating prover is allowed to use any witness sufficiently close to a regular vector.
- We complement our analysis with an in-depth overview of existing attacks against RSD.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004109 (1).pdf`
- `downloads/14004109.pdf`
