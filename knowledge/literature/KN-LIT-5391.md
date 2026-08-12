---
id: KN-LIT-5391
type: literature
title: "On Reverse-Engineering S-Boxes with Hidden Design Criteria or Structure"
authors:
  - "Alex Biryukov"
  - "Léo Perrin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, point-decomposition, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
S-Boxes are the key components of many cryptographic primitives and designing them to improve resilience to attacks such as linear or dierential cryptanalysis is well understood. In this paper, we investigate techniques that can be used to reverse-engineer S-box design and illustrate those by studying the S-Box F of the Skipjack block cipher whose design process so far remained secret.

## Key claims (as reported)
- We rst show that the linear properties of F are far from random and propose a design criteria, along with an algorithm which generates S-Boxes very similar to that of Skipjack.
- Then we consider more general S-box decomposition problems and propose new methods for decomposing S-Boxes built from arithmetic operations or as a Feistel Network of up to 5 rounds.
- Finally, we develop an S-box generating algorithm which can x a large number of DDT entries to the values chosen by the designer.
- We demonstrate this algorithm by embedding images into the visual representation of S-box's DDT.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92160208 (1).pdf`
- `downloads/92160208 (2).pdf`
- `downloads/92160208.pdf`
