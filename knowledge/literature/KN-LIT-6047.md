---
id: KN-LIT-6047
type: literature
title: "Puncturable Key Wrapping and Its Applications"
authors:
  - "Matilda Backendal"
  - "Felix Günther"
year: null
venue: "Journal of Cryptology"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce puncturable key wrapping (PKW), a new cryptographic primitive that supports fine-grained forward security properties in symmetric key hierarchies. We develop syntax and security definitions, along with provably secure constructions for PKW from simpler components (AEAD schemes and puncturable PRFs).

## Key claims (as reported)
- We show how PKW can be applied in two distinct scenarios.
- First, we show how to use PKW to achieve forward security for TLS 1.3 0-RTT session resumption, even when the server’s long-term key for generating session tickets gets compromised.
- This extends and corrects a recent work of Aviram, Gellert, and Jager (Journal of Cryptology, 2021).
- Second, we show how to use PKW to build a protected file storage system with file shredding, wherein a client can outsource encrypted files to a potentially malicious or corrupted cloud server whilst achieving strong forward-security guarantees, relying only on local key updates.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910050 (1).pdf`
- `downloads/137910050.pdf`
