---
id: KN-LIT-2706
type: literature
title: "Big-Key Symmetric Encryption: Resisting Key Exfiltration"
authors:
  - "Mihir Bellare"
  - "Daniel Kane"
  - "Phillip Rogaway"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mov-fr, protocol, provable-security, rsa, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper aims to move research in the bounded retrieval model (BRM) from theory to practice by considering symmetric (rather than public-key) encryption, giving efficient schemes, and providing security analyses with sharp, concrete bounds. The threat addressed is malware that aims to exfiltrate a user’s key.

## Key claims (as reported)
- Our schemes aim to thwart this by using an enormously long key, yet paying for this almost exclusively in storage cost, not speed.
- Our main result is a general-purpose lemma, the subkey prediction lemma, that gives a very good bound on an adversary’s ability to guess a (modest length) subkey of a big-key, the subkey consisting of the bits of the big-key found at random, specified locations, after the adversary has exfiltrated partial information about the big-key (e.g., half as many bits as the big-key is long).
- We then use this to design a new kind of key encapsulation mechanism, and, finally, a symmetric encryption scheme.
- Both are in the random-oracle model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98140360 (1).pdf`
- `downloads/98140360.pdf`
