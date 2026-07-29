---
id: KN-LIT-4462
type: literature
title: "Improving the Security of MACs via Randomized Message Preprocessing"
authors:
  - "Yevgeniy Dodis"
  - "Krzysztof Pietrzak"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
“Hash then encrypt” is an approach to message authentication, where first the message is hashed down using an ε-universal hash function, and then the resulting k-bit value is encrypted, say with a block-cipher. The security of this scheme is proportional to εq 2 , where q is the number of MACs the adversary can request.

## Key claims (as reported)
- As ε is at least 2−k , the best one can hope for is O(q 2 /2k ) security.
- Unfortunately, such small ε is not achieved by simple hash functions used in practice, such as the polynomial evaluation or the Merkle-Damgård construction, where ε grows with the message length L.
- The main insight of this work comes from the fact that, by using randomized message preprocessing via a short random salt p (which must then be sent as part of the authentication tag), we can use the “hash then encrypt” paradigm with suboptimal “practical” ε-universal hash functions, and still improve its exact security to optimal O(q 2 /2k ).
- Specifically, by using at most an O(log L)-bit salt p, one can always regain the optimal exact security O(q 2 /2k ), even in situations where ε grows polynomially with L.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/45930419 (1).pdf`
- `downloads/45930419 (2).pdf`
- `downloads/45930419 (3).pdf`
- `downloads/45930419.pdf`
