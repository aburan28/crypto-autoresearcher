---
id: KN-LIT-3675
type: literature
title: "Encrypt or Decrypt? To Make a Single-Key Beyond Birthday Secure Nonce-Based MAC"
authors:
  - "Nilanjan Datta"
  - "Avijit Dutta"
  - "Mridul Nandi"
  - "Kan Yasuda"
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
At CRYPTO 2016, Cogliati and Seurin have proposed a highly secure nonce-based MAC called Encrypted Wegman-Carter with Davies-Meyer (EWCDM) construction, as EK2 EK1 (N ) ⊕ N ⊕ HKh (M ) for a nonce N and a message M . This construction achieves roughly 22n/3 bit MAC security with the assumption that E is a PRP secure n-bit block cipher and H is an almost xor universal n-bit hash function.

## Key claims (as reported)
- In this paper we propose Decrypted Wegman-Carter with Davies-Meyer (DWCDM) construction, which is structurally very similar to its predecessor EWCDM except that the outer encryption call is replaced by decryption.
- The biggest advantage of DWCDM is that we can make a truly single key MAC: the two block cipher calls can use the same block cipher key K = K1 = K2 .
- Moreover, we can derive the hash key as Kh = EK (1), as long as |Kh | = n.
- Whether we use encryption or decryption in the outer layer makes a huge difference; using the decryption instead enables us to apply an extended version of the mirror theory by Patarin to the security analysis of the construction.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993413 (1).pdf`
- `downloads/10993413.pdf`
