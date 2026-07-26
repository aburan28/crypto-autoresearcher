---
id: KN-LIT-2038
type: literature
title: "A Double-Piped Mode of Operation for MACs, PRFs and PROs: Security beyond the Birthday Barrier"
authors:
  - "Kan Yasuda"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We revisit the double-pipe construction introduced by Lucks at Asiacrypt 2005. Lucks originally studied the construction for iterated hash functions and showed that the approach is effective in improving security against various types of collision and (second-)preimage attacks.

## Key claims (as reported)
- Instead, in this paper we apply the construction to the secret-key setting, where the underlying FIL (fixed-input-length) compression function is equipped with a dedicated key input.
- We make some adjustments to Lucks’ original design so that now the new mode works with a single key and operates as a multi-property-preserving domain extension of MACs (message authentication codes), PRFs (pseudo-random functions) and PROs (pseudo-random oracles).
- Though more than twice as slow as the Merkle-Damgård construction, the double-piped mode enjoys security strengthened beyond the birthday bound, most notably, high MAC security.
- More specifically, when iterating an FIL-MAC whose output size is n-bit, the new double-piped (mode )yields an AIL-(arbitrary-inputlength-)MAC with security up to O 25n/6 query complexity.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54790243 (1).pdf`
- `downloads/54790243 (2).pdf`
- `downloads/54790243 (3).pdf`
- `downloads/54790243.pdf`
