---
id: KN-LIT-4971
type: literature
title: "Multi-Authority ABE from Lattices without Random Oracles"
authors:
  - "Brent Waters"
  - "Hoeteck Wee"
  - "David J. Wu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, lattice, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Attribute-based encryption (ABE) extends public-key encryption to enable fine-grained control to encrypted data. However, this comes at the cost of needing a central trusted authority to issue decryption keys.

## Key claims (as reported)
- A multi-authority ABE (MA-ABE) scheme decentralizes ABE and allows anyone to serve as an authority.
- Existing constructions of MA-ABE only achieve security in the random oracle model.
- In this work, we develop new techniques for constructing MA-ABE for the class of subset policies (which captures policies such as conjunctions and DNF formulas) whose security can be based in the plain model without random oracles.
- We achieve this by relying on the recently-proposed “evasive” learning with errors (LWE) assumption by Wee (EUROCRYPT 2022) and Tsabury (CRYPTO 2022).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137470061 (1).pdf`
- `downloads/137470061.pdf`
