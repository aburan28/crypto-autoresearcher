---
id: KN-LIT-2582
type: literature
title: "Asymmetric Group Key Agreement"
authors:
  - "Qianhong Wu"
  - "Yi Mu"
  - "Willy Susilo"
  - "Bo Qin"
  - "Josep Domingo-Ferrer"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A group key agreement (GKA) protocol allows a set of users to establish a common secret via open networks. Observing that a major goal of GKAs for most applications is to establish a confidential channel among group members, we revisit the group key agreement definition and distinguish the conventional (symmetric) group key agreement from asymmetric group key agreement (ASGKA) protocols.

## Key claims (as reported)
- Instead of a common secret key, only a shared encryption key is negotiated in an ASGKA protocol.
- This encryption key is accessible to attackers and corresponds to different decryption keys, each of which is only computable by one group member.
- We propose a generic construction of one-round ASGKAs based on a new primitive referred to as aggregatable signaturebased broadcast (ASBB), in which the public key can be simultaneously used to verify signatures and encrypt messages while any signature can be used to decrypt ciphertexts under this public key.
- Using bilinear pairings, we realize an efficient ASBB scheme equipped with useful properties.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54790154 (1).pdf`
- `downloads/54790154 (2).pdf`
- `downloads/54790154 (3).pdf`
- `downloads/54790154.pdf`
