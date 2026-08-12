---
id: KN-LIT-5734
type: literature
title: "Password Interception in a SSL/TLS Channel"
authors:
  - "Brice Canvel"
  - "Alain Hiltgen"
  - "Serge Vaudenay"
  - "Martin Vuagnoux"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [protocol, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Simple password authentication is often used e.g. from an email software application to a remote IMAP server. This is frequently done in a protected peer-to-peer tunnel, e.g. by SSL/TLS.

## Key claims (as reported)
- At Eurocrypt’02, Vaudenay presented vulnerabilities in padding schemes used for block ciphers in CBC mode.
- He used a side channel, namely error information in the padding verification.
- This attack was not possible against SSL/TLS due to both unavailability of the side channel (errors are encrypted) and premature abortion of the session in case of errors.
- In this paper we extend the attack and optimize it.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/27290581 (1).pdf`
- `downloads/27290581 (2).pdf`
- `downloads/27290581.pdf`
