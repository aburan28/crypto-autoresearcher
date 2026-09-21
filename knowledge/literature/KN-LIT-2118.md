---
id: KN-LIT-2118
type: literature
title: "A Modular Security Analysis of the TLS Handshake Protocol"
authors:
  - "P. Morrissey"
  - "N.P. Smart"
  - "B. Warinschi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [protocol, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the security of the widely deployed Secure Session Layer/Transport Layer Security (TLS) key agreement protocol. Our analysis identifies, justifies, and exploits the modularity present in the design of the protocol: the application keys offered to higher level applications are obtained from a master key, which in turn is derived, through interaction, from a pre-master key.

## Key claims (as reported)
- Our first contribution consists of formal models that clarify the security level enjoyed by each of these types of keys.
- The models that we provide fall under well established paradigms in defining execution, and security notions.
- We capture the realistic setting where only one of the two parties involved in the execution of the protocol (namely the server) has a certified public key, and where the same master key is used to generate multiple application keys.
- The main contribution of the paper is a modular and generic proof of security for the application keys established through the TLS protocol.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/53500056 (1).pdf`
- `downloads/53500056 (2).pdf`
- `downloads/53500056 (3).pdf`
- `downloads/53500056.pdf`
