---
id: KN-LIT-1688
type: literature
title: "Identity-Based Revocable and Linkable Ring Signature"
authors:
  - "Muyuan Wang"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1111"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1111"
tags: [implementation, provable-security, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Revocable and linkable ring signatures (RLRS) provide a practical mechanism for controllable anonymity, enabling a revocation authority (RA) to mandatorily revoke the anonymity of the real signer. However, existing constructions often rely on the assumption of a fully trusted RA, where the correctness of the revocation is not publicly verifiable rendering honest users vulnerable to undetected framing by a compromised RA.

## Key claims (as reported)
- Furthermore, the concrete deployment of these schemes is hindered by the certificate management burden of PKI and computation or communication overheads that scale linearly with the ring size, limiting their real-world applicability.
- In this paper, we formalize the notion of Identity-Based Revocable and Linkable Ring Signatures (IB-RLRS), inherently eliminating cumbersome PKI management.
- Our primary contribution is the enhancement of revocability alongside a newly adapted property termed revocation soundness, guaranteeing that the real signer’s identity can always be extracted, and that a malicious RA cannot frame honest users who did not participate in the signature generation.
- We present an efficient instantiation of IB-RLRS scheme, and prove its security in the random oracle model.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1111.pdf`
