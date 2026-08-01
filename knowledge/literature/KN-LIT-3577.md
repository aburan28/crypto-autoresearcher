---
id: KN-LIT-3577
type: literature
title: "Efficient Instantiations of Tweakable Blockciphers and"
authors:
  - "Refinements to Modes OCB"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe highly efficient constructions, XE and XEX, that turn a blockcipher E: K × {0, 1}n → {0, 1}n into a tweakable blocke K × T × {0, 1}n → {0, 1}n having tweak space T = {0, 1}n × I cipher E: where I is a set of tuples of integers such as I = [1 .. When tweak T is obtained from tweak S by incrementing one if its numerical T eK components, the cost to compute E (M ) having already computed some S 0 e EK (M ) is one blockcipher call plus a small and constant number of elementary machine operations.

## Key claims (as reported)
- Our constructions work by associating to the ith coordinate of I an element αi ∈ F∗2n and multiplying by αi when one increments that component of the tweak.
- We illustrate the use of this approach by refining the authenticated-encryption scheme OCB and the message authentication code PMAC, yielding variants of these algorithms that are simpler and faster than the original schemes, and yet have simpler proofs.
- Our results bolster the thesis of Liskov, Rivest, and Wagner [10] that a desirable approach for designing modes of operation is to start from a tweakable blockcipher.
- We elaborate on their idea, suggesting the kind of tweak space, usage-discipline, and blockcipher-based instantiations that give rise to simple and efficient modes.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/33290016 (1).pdf`
- `downloads/33290016 (2).pdf`
- `downloads/33290016 (3).pdf`
- `downloads/33290016.pdf`
