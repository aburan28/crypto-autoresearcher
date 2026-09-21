---
id: KN-LIT-3451
type: literature
title: "Distributed Broadcast Encryption from Bilinear Groups"
authors:
  - "Dimitris Kolonelos"
  - "Giulio Malavolta"
  - "Hoeteck Wee"
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
Distributed broadcast encryption (DBE) improves on the traditional notion of broadcast encryption by eliminating the key-escrow problem: In a DBE system, users generate their own secret keys noninteractively without the help of a trusted party. Then anyone can broadcast a message for a subset S of the users, in such a way that the resulting ciphertext size is sublinear in (and, ideally, independent of) |S|.

## Key claims (as reported)
- Unfortunately, the only known constructions of DBE requires heavy cryptographic machinery, such as general-purpose indistinguishability obfuscation, or come without a security proof.
- In this work, we formally show that obfuscation is not necessary for DBE, and we present two practical DBE schemes from standard assumptions in prime-order bilinear groups.
- Our constructions are conceptually simple, satisfy the strong notion of adaptive security, and are concretely efficient.
- In fact, their performance, in terms of number of group elements and efficiency of the algorithms, is comparable with that of traditional (non distributed) broadcast encryption schemes from bilinear groups.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438203 (1).pdf`
- `downloads/14438203.pdf`
