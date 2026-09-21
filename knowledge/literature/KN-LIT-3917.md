---
id: KN-LIT-3917
type: literature
title: "FO derandomization sometimes damages security"
authors:
  - "Daniel J. Bernstein"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, elliptic-curve, hash, lattice, pqc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
FO derandomization is a common step in protecting against chosenciphertext attacks. There are theorems qualitatively stating that FO derandomization preserves ROM OW-CPA security.

## Key claims (as reported)
- However, quantitatively, these theorems are loose, allowing the possibility of the derandomized security level being considerably smaller than the original security level.
- Many cryptosystems rely on FO derandomization without adjusting parameters to account for this looseness.
- This paper proves, for two examples of a randomized ROM PKE, that derandomizing the PKE degrades ROM OW-CPA security by a factor close to the number of hash queries.
- The first example can be explained by the size of the message space of the PKE; the second cannot.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/footloose-20241230.pdf`
