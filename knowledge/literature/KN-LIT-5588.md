---
id: KN-LIT-5588
type: literature
title: "On the Security of the TLS Protocol: A Systematic Analysis"
authors:
  - "Hugo Krawczyk"
  - "Kenneth G. Paterson⋆"
  - "Hoeteck Wee⋆⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, provable-security, quantum, rsa, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
TLS is the most widely-used cryptographic protocol on the Internet. It comprises the TLS Handshake Protocol, responsible for authentication and key establishment, and the TLS Record Protocol, which takes care of subsequent use of those keys to protect bulk data.

## Key claims (as reported)
- In this paper, we present the most complete analysis to date of the TLS Handshake protocol and its application to data encryption (in the Record Protocol).
- We show how to extract a keyencapsulation mechanism (KEM) from the TLS Handshake Protocol, and how the security of the entire TLS protocol follows from security properties of this KEM when composed with a secure authenticated encryption scheme in the Record Protocol.
- The security notion we achieve is a variant of the ACCE notion recently introduced by Jager et al.
- Our approach enables us to analyse multiple different key establishment methods in a modular fashion, including the first proof of the most common deployment mode that is based on RSA PKCS #1v1.5 encryption, as well as Diffie-Hellman modes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80420234 (1).pdf`
- `downloads/80420234 (2).pdf`
- `downloads/80420234 (3).pdf`
- `downloads/80420234.pdf`
