---
id: KN-LIT-7279
type: literature
title: "Tweaking Even-Mansour Ciphers"
authors:
  - "Benoît Cogliati"
  - "Rodolphe Lampe"
  - "Yannick Seurin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study how to construct efficient tweakable block ciphers in the Random Permutation model, where all parties have access to public random permutation oracles. We propose a construction that combines, more efficiently than by mere black-box composition, the CLRW construction (which turns a traditional block cipher into a tweakable block cipher) of Landecker et al.

## Key claims (as reported)
- (CRYPTO 2012) and the iterated EvenMansour construction (which turns a tuple of public permutations into a traditional block cipher) that has received considerable attention since the work of Bogdanov et al.
- More concretely, we introduce the (one-round) tweakable Even-Mansour (TEM) cipher, constructed from a single n-bit permutation P and a uniform and almost XOR-universal family of hash functions (Hk ) from some tweak space to {0, 1}n , and defined as (k, t, x) 7→ Hk (t) ⊕ P (Hk (t) ⊕ x), where k is the key, t is the tweak, and x is the n-bit message, as well as its generalization obtained by cascading r independently keyed rounds of this construction.
- Our main result is a security bound up to approximately 22n/3 adversarial queries against adaptive chosen-plaintext and ciphertext distinguishers for the two-round TEM construction, using Patarin’s H-coefficients technique.
- We also provide an analysis based on the coupling technique showing that asymptotically, as the number of rounds r grows, the security provided by the r-round TEM construction approaches the information-theoretic bound of 2n adversarial queries.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92160253 (1).pdf`
- `downloads/92160253 (2).pdf`
- `downloads/92160253.pdf`
