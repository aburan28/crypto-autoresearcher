---
id: KN-LIT-3718
type: literature
title: "EWCDM: An Efficient, Beyond-Birthday Secure, Nonce-Misuse Resistant MAC"
authors:
  - "Benoît Cogliati"
  - "Yannick Seurin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security, quantum, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a nonce-based MAC construction called EWCDM (Encrypted Wegman-Carter with Davies-Meyer), based on an almost xoruniversal hash function and a block cipher, with the following properties: (i) it is simple and efficient, requiring only two calls to the block cipher, one of which can be carried out in parallel to the hash function computation; (ii) it is provably secure beyond the birthday bound when nonces are not reused; (iii) it provably retains security up to the birthday bound in case of nonce misuse. Our construction is a simple modification of the Encrypted Wegman-Carter construction, which is known to achieve only (i) and (iii) when based on a block cipher.

## Key claims (as reported)
- Underlying our new construction is a new PRP-to-PRF conversion method coined Encrypted Davies-Meyer, which turns a pair of secret random permutations into a function which is provably indistinguishable from a perfectly random function up to at least 22n/3 queries, where n is the bit-length of the domain of the permutations.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98140117 (1).pdf`
- `downloads/98140117.pdf`
