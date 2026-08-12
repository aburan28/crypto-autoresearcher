---
id: KN-LIT-5917
type: literature
title: "Private Puncturable PRFs From Standard Lattice Assumptions"
authors:
  - "Dan Boneh"
  - "Sam Kim"
  - "Hart Montgomery"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, lattice, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A puncturable pseudorandom function (PRF) has a master key k that enables one to evaluate the PRF at all points of the domain, and has a punctured key kx that enables one to evaluate the PRF at all points but one. The punctured key kx reveals no information about the value of the PRF at the punctured point x.

## Key claims (as reported)
- Punctured PRFs play an important role in cryptography, especially in applications of indistinguishability obfuscation.
- However, in previous constructions, the punctured key kx completely reveals the punctured point x: given kx it is easy to determine x.
- A private puncturable PRF is one where kx reveals nothing about x.
- This concept was defined by Boneh, Lewi, and Wu, who showed the usefulness of private puncturing, and gave constructions based on multilinear maps.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10210281 (1).pdf`
- `downloads/10210281.pdf`
