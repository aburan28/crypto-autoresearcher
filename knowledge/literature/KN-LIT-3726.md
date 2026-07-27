---
id: KN-LIT-3726
type: literature
title: "Experimenting with Faults, Lattices and the DSA"
authors:
  - "David Naccache"
  - "Phong Q. Nguy ̃ên"
  - "Michael Tunstall"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, lattice, pairing, provable-security, side-channel, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present an attack on DSA smart-cards which combines physical fault injection and lattice reduction techniques. This seems to be the first (publicly reported) physical experiment allowing to concretely pull-out DSA keys out of smart-cards.

## Key claims (as reported)
- We employ a particular type of fault attack known as a glitch attack, which will be used to actively modify the DSA nonce k used for generating the signature: k will be tampered with so that a number of its least significant bytes will flip to zero.
- Then we apply well-known lattice attacks on El Gamal-type signatures which can recover the private key, given sufficiently many signatures such that a few bits of each corresponding k are known.
- In practice, when one byte of each k is zeroed, 27 signatures are sufficient to disclose the private key.
- The more bytes of k we can reset, the fewer signatures will be required.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/33860017 (1).pdf`
- `downloads/33860017 (2).pdf`
- `downloads/33860017 (3).pdf`
- `downloads/33860017.pdf`
