---
id: KN-LIT-6501
type: literature
title: "Security Analysis of the Strong Diffie-Hellman Problem"
authors:
  - "Jung Hee Cheon"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, dlp, elliptic-curve]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Let g be an element of prime order p in an abelian group and d α ∈ Zp . We show that if g, g α , and g α are p given for a √ positive divisor d of p−1, we can compute the secret α in O(log p·( p/d+ d)) group operations p √ i using O(max{ p/d, d}) memory.

## Key claims (as reported)
- If g α (i = 0, 1, 2, . . . , d) are provided for p a positive divisor d of p + 1, α p can be computed in O(log p · ( p/d + d)) √ group operations using O(max{ p/d, d}) memory.
- This implies that the strong Diffie-Hellman problem √ and its related problems have computational complexity reduced by O( d) from that of the discrete logarithm problem for such primes.
- Further we apply this algorithm to the schemes based on the Diffie-Hellman problem on an abelian group of prime order p.
- As a result, p we reduce the com√ plexity of recovering the secret key from O( p) to O( p/d) for Boldyreva’s blind signature and the original ElGamal scheme when p − 1 (resp. p + 1) has a divisor d ≤ p1/2 (resp. d ≤ p1/3 ) and d signature or decryption queries are allowed.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/40040001 (1).pdf`
- `downloads/40040001 (2).pdf`
- `downloads/40040001 (3).pdf`
- `downloads/40040001.pdf`
