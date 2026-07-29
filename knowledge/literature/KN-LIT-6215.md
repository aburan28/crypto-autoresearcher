---
id: KN-LIT-6215
type: literature
title: "Relaxing Full-Codebook Security: A Refined Analysis of Key-Length Extension Schemes"
authors:
  - "Peter Gaži"
  - "Jooyoung Lee"
  - "Yannick Seurin"
  - "John Steinberger"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We revisit the security (as a pseudorandom permutation) of cascading-based constructions for block-cipher key-length extension. Previous works typically considered the extreme case where the adversary is given the entire codebook of the construction, the only complexity measure being the number qe of queries to the underlying ideal block cipher, representing adversary’s secret-key-independent computation.

## Key claims (as reported)
- Here, we initiate a systematic study of the more natural case of an adversary restricted to adaptively learning a number qc of plaintext/ciphertext pairs that is less than the entire codebook.
- For any such qc , we aim to determine the highest number of block-cipher queries qe the adversary can issue without being able to successfully distinguish the construction (under a secret key) from a random permutation.
- More concretely, we show the following results for key-length extension schemes using a block cipher with n-bit blocks and κ-bit keys: – Plain cascades of length ` = 2r + 1 are secure whenever qc qer 2r(κ+n) , qc 2κ and qe 22κ .
- The bound for r = 1 also applies to two-key triple encryption (as used within Triple DES). – The r-round XOR-cascade is secure as long as qc qer 2r(κ+n) , matching an attack by Gaži (CRYPTO 2013). – We fully characterize the security of Gaži and Tessaro’s two-call 2XOR construction (EUROCRYPT 2012) for all values of qc , and note that the addition of a third whitening step strictly increases security for 2n/4 ≤ qc ≤ 23/4n .

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400127 (1).pdf`
- `downloads/85400127.pdf`
