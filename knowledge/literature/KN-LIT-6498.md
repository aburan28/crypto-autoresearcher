---
id: KN-LIT-6498
type: literature
title: "Security analysis of SPAKE2+"
authors:
  - "Victor Shoup∗"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, protocol, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show that a slight variant of Protocol SPAKE2 +, which was presented but not analyzed in [CKS08], is a secure asymmetric password-authenticated key exchange protocol (PAKE), meaning that the protocol still provides good security guarantees even if a server is compromised and the password file stored on the server is leaked to an adversary. The analysis is done in the UC framework (i.e., a simulation-based security model), under the computational DiffieHellman (CDH) assumption, and modeling certain hash functions as random oracles.

## Key claims (as reported)
- The main difference between our variant and the original Protocol SPAKE2 + is that our variant includes standard key confirmation flows; also, adding these flows allows some slight simplification to the remainder of the protocol.
- Along the way, we also: • provide the first proof (under the same assumptions) that a slight variant of Protocol SPAKE2 from [AP05] is a secure symmetric PAKE in the UC framework (previous security proofs were all in the weaker BPR framework [BPR00]); • provide a proof (under very similar assumptions) that a variant of Protocol SPAKE2 + that is currently being standardized is also a secure asymmetric PAKE; • repair several problems in earlier UC formulations of secure symmetric and asymmetric PAKE.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12550245 (1).pdf`
- `downloads/12550245.pdf`
- `downloads/spake2plus.pdf`
