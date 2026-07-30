---
id: KN-LIT-649
type: literature
title: "Towards Bidirectional Ratcheted Key Exchange?"
authors:
  - "Bertram Poettering"
  - "Paul Rösler"
year: 2018
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2018/296"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2018/296"
tags: [lattice, mov-fr, pairing, protocol]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Ratcheted key exchange (RKE) is a cryptographic technique used in instant messaging systems like Signal and the WhatsApp messenger for attaining strong security in the face of state exposure attacks. RKE received academic attention in the recent works of Cohn-Gordon et al.

## Key claims (as reported)
- (EuroS&P 2017) and Bellare et al.
- While the former is analytical in the sense that it aims primarily at assessing the security that one particular protocol does achieve (which might be weaker than the notion that it should achieve), the authors of the latter develop and instantiate a notion of security from scratch, independently of existing implementations.
- Unfortunately, however, their model is quite restricted, e.g. for considering only unidirectional communication and the exposure of only one of the two parties.
- In this article we resolve the limitations of prior work by developing alternative security definitions, for unidirectional RKE as well as for RKE where both parties contribute.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993325 (1).pdf`
- `downloads/10993325.pdf`
