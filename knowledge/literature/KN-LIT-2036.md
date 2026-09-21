---
id: KN-LIT-2036
type: literature
title: "A Distributed Online Certificate Status Protocol with a Single Public Key"
authors:
  - "Satoshi Koga"
  - "Kouichi Sakurai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Public Key Infrastructure (PKI) technology is very important to support secure global electronic commerce and digital communications on networks. The Online Certificate Status Protocol (OCSP) is the standard protocol for retrieving certificate revocation information in PKI.

## Key claims (as reported)
- To minimize the damages caused by OCSP responder’s private key exposure, a distributed OCSP composed of multiple responders is needed.
- This paper presents a new distributed OCSP with a single public key by using key-insulated signature scheme [6].
- In proposed distributed OCSP, each responder has the different private key, but corresponding public key remains fixed, so the client simply obtains and stores one certificate and can verify any responses by using a single public key.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/29470386 (1).pdf`
- `downloads/29470386 (2).pdf`
- `downloads/29470386.pdf`
