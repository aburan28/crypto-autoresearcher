---
id: KN-LIT-5356
type: literature
title: "On IND-qCCA security in the ROM and its applications CPA security is sufficient for TLS 1.3"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pqc, protocol]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Bounded IND-CCA security (IND-qCCA) is a notion similar to the traditional IND-CCA security, except the adversary is restricted to a constant number q of decryption/decapsulation queries. We show in this work that IND-qCCA is easily obtained from any passively secure PKE in the (Q)ROM.

## Key claims (as reported)
- That is, simply adding a confirmation hash or computing the key as the hash of the plaintext and ciphertext holds an IND-qCCA KEM.
- In particular, there is no need for derandomization or re-encryption as in the Fujisaki-Okamoto (FO) transform [15].
- This makes the decapsulation process of such IND-qCCA KEM much more efficient than its FO-derived counterpart.
- In addition, IND-qCCA KEMs could be used in the recently proposed KEMTLS protocol [29] that requires IND-1CCA ephemeral key-exchange mechanisms, or in TLS 1.3.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760278 (1).pdf`
- `downloads/132760278.pdf`
