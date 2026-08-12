---
id: KN-LIT-880
type: literature
title: "Isogeny-based Group Signatures and"
authors:
  - "Yu-Hsuan Huang"
  - "Tanja Lange"
  - "Bo-Yin Yang"
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/1368"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/1368"
tags: [hash, hyperelliptic, isogeny, lattice, mov-fr, pairing, pqc, provable-security, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide the first isogeny-based group signature (GS) and accountable ring signature (ARS) that are provably secure in the quantum random oracle model (QROM). We do so by building an intermediate primitive called openable sigma protocol and show that every such protocol gives rise to a secure ARS and GS.

## Key claims (as reported)
- Additionally, the QROM security is guaranteed if the perfect unique-response property is satisfied.
- Our design, with the underlying protocol satisfying this essential unique-response property, is sophisticatedly crafted for QROM security.
- From there, with clever twists to available proving techniques, we obtain the first isogeny-based ARS and GS that are proven QROM-secure.
- Concurrently, Beullens et al.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2021-1368.pdf`
