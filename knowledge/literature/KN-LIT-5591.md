---
id: KN-LIT-5591
type: literature
title: "On the Security of TLS-DHE in the Standard Model"
authors:
  - "Tibor Jager"
  - "Florian Kohlar"
  - "Sven Schäge"
  - "Jörg Schwenk"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, provable-security, rsa, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
TLS is the most important cryptographic protocol in use today. However, up to now there is no complete cryptographic security proof in the standard model, nor in any other model.

## Key claims (as reported)
- We give the first such proof for the core cryptographic protocol of TLS ciphersuites based on ephemeral Diffie-Hellman key exchange (TLS-DHE), which include the cipher suite TLS DHE DSS WITH 3DES EDE CBC SHA mandatory in TLS 1.0 and TLS 1.1.
- It is impossible to prove security of the TLS Handshake protocol in any classical key-indistinguishability-based security model (like for instance the Bellare-Rogaway or the Canetti-Krawczyk model), due to subtle issues with the encryption of the final Finished messages.
- Therefore we start with proving the security of a truncated version of the TLS-DHE Handshake protocol, which has been considered in previous works on TLS.
- Then we define the notion of authenticated and confidential channel establishment (ACCE) as a new security model which captures precisely the security properties expected from TLS in practice, and show that the combination of the TLS Handshake with data encryption in the TLS Record Layer can be proven secure in this model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74170271 (1).pdf`
- `downloads/74170271 (2).pdf`
- `downloads/74170271 (3).pdf`
- `downloads/74170271 (4).pdf`
- `downloads/74170271 (5).pdf`
- `downloads/74170271.pdf`
