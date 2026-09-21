---
id: KN-LIT-2607
type: literature
title: "Attacking and defending the McEliece cryptosystem"
authors:
  - "Daniel J. Bernstein"
  - "Tanja Lange"
  - "Christiane Peters"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hyperelliptic, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents several improvements to Stern’s attack on the McEliece cryptosystem and achieves results considerably better than Canteaut et al. This paper shows that the system with the originally proposed parameters can be broken in just 1400 days by a single 2.4GHz Core 2 Quad CPU, or 7 days by a cluster of 200 CPUs.

## Key claims (as reported)
- This attack has been implemented and is now in progress.
- This paper proposes new parameters for the McEliece and Niederreiter cryptosystems achieving standard levels of security against all known attacks.
- The new parameters take account of the improved attack; the recent introduction of list decoding for binary Goppa codes; and the possibility of choosing code lengths that are not a power of 2.
- The resulting public-key sizes are considerably smaller than previous parameter choices for the same level of security.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/mceliece-20080807.pdf`
