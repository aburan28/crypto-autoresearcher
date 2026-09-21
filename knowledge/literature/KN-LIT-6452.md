---
id: KN-LIT-6452
type: literature
title: "Secure Network Coding Over the Integers?"
authors:
  - "Rosario Gennaro"
  - "Jonathan Katz"
  - "Hugo Krawczyk"
  - "Tal Rabin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, hash, pairing, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Network coding offers the potential to increase throughput and improve robustness without any centralized control. Unfortunately, network coding is highly susceptible to “pollution attacks” in which malicious nodes modify packets improperly so as to prevent message recovery at the recipient(s); such attacks cannot be prevented using standard endto-end cryptographic authentication because network coding mandates that intermediate nodes modify data packets in transit.

## Key claims (as reported)
- Specialized “network coding signatures” addressing this problem have been developed in recent years using homomorphic hashing and homomorphic signatures.
- We contribute to this area in several ways: – We show the first homomorphic signature scheme based on the RSA assumption (in the random oracle model). – We give a homomorphic hashing scheme that is more efficient than existing schemes, and which leads to network coding signatures based on the hardness of factoring (in the standard model). – We describe variants of existing schemes that reduce the communication overhead for moderate-size networks, and improve computational efficiency (in some cases quite dramatically – e.g., we achieve a 20-fold speedup in signature generation at intermediate nodes).
- Underlying our techniques is a modified approach to random linear network coding where instead of working in a vector space over a field, we work in a module over the integers (with small coefficients).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/60560142 (1).pdf`
- `downloads/60560142 (2).pdf`
- `downloads/60560142 (3).pdf`
- `downloads/60560142.pdf`
