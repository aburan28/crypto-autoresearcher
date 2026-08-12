---
id: KN-LIT-1976
type: literature
title: "(Pseudo) Preimage Attack on Round-Reduced"
authors:
  - "Grøstl Hash Function"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Grøstl hash function is one of the 5 final round candidates of the SHA-3 competition hosted by NIST. In this paper, we study the preimage resistance of the Grøstl hash function.

## Key claims (as reported)
- We propose pseudo preimage attacks on Grøstl hash function for both 256-bit and 512-bit versions, i.e., we need to choose the initial value in order to invert the hash function.
- Pseudo preimage attack on 5(out of 10)-round Grøstl-256 has a complexity of (2244.85 , 2230.13 ) (in time and memory) and pseudo preimage attack on 8(out of 14)-round Grøstl-512 has a complexity of (2507.32 , 2507.00 ).
- To the best of our knowledge, our attacks are the first (pseudo) preimage attacks on round-reduced Grøstl hash function, including its compression function and output transformation.
- These results are obtained by a variant of meet-in-the-middle preimage attack framework by Aoki and Sasaki.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/75490127 (1).pdf`
- `downloads/75490127 (2).pdf`
- `downloads/75490127 (3).pdf`
- `downloads/75490127.pdf`
