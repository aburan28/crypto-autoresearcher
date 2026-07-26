---
id: KN-LIT-3384
type: literature
title: "Deniable Ring Authentication?"
authors:
  - "Moni Naor"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, provable-security, rsa, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Digital Signatures enable authenticating messages in a way that disallows repudiation. While non-repudiation is essential in some applications, it might be undesirable in others.

## Key claims (as reported)
- Two related notions of authentication are: Deniable Authentication (see Dwork, Naor and Sahai [?]) and Ring Signatures (see Rivest, Shamir and Tauman [?]).
- In this paper we show how to combine these notions and achieve Deniable Ring Authentication: it is possible to convince a verifier that a member of an ad hoc subset of participants (a ring) is authenticating a message m without revealing which one (source hiding), and the verifier V cannot convince a third party that message m was indeed authenticated – there is no ‘paper trail’ of the conversation, other than what could be produced by V alone, as in zero-knowledge.
- We provide an efficient protocol for deniable ring authentication based on any strong encryption scheme.
- That is once an entity has published a public-key of such an encryption system, it can be drafted to any such ring.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/24420483 (1).pdf`
- `downloads/24420483 (2).pdf`
- `downloads/24420483.pdf`
