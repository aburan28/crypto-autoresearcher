---
id: KN-LIT-2308
type: literature
title: "Achievable CCA2 Relaxation for Homomorphic Encryption"
authors:
  - "Adi Akavia"
  - "Craig Gentry"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Homomorphic encryption (HE) protects data in-use, but can be computationally expensive. To avoid the costly bootstrapping procedure that refreshes ciphertexts, some works have explored client-aided outsourcing protocols, where the client intermittently refreshes ciphertexts for a server that is performing homomorphic computations.

## Key claims (as reported)
- But is this approach secure against malicious servers?
- We present a CPA-secure encryption scheme that is completely insecure in this setting.
- We define a new notion of security, called funcCPA, that we prove is sufficient.
- Additionally, we show: – Homomorphic encryption schemes that have a certain type of circuit privacy – for example, schemes in which ciphertexts can be “sanitized” – are funcCPA-secure. – In particular, assuming certain existing HE schemes are CPA-secure, they are also funcCPA-secure. – For certain encryption schemes, like Brakerski-Vaikuntanathan, that have a property that we call oblivious secret key extraction, funcCPAsecurity implies circular security – i.e., that it is secure to provide an encryption of the secret key in a form usable for bootstrapping (to construct fully homomorphic encryption).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137470026 (1).pdf`
- `downloads/137470026.pdf`
