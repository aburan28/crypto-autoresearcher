---
id: KN-LIT-4784
type: literature
title: "Lossy CSI-FiSh: Efficient Signature Scheme with Tight Reduction to Decisional CSIDH-512"
authors:
  - "Ali El Kaafarani"
  - "Shuichi Katsumata"
  - "Federico Pintore"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [class-group, hash, isogeny, number-theory, pairing, pqc, protocol, provable-security, quantum, sidh-csidh, signature, supersingular, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Recently, Beullens, Kleinjung, and Vercauteren (Asiacrypt’19) provided the first practical isogeny-based digital signature, obtained from the Fiat-Shamir (FS) paradigm. They worked with the CSIDH-512 parameters and passed through a new record class group computation.

## Key claims (as reported)
- However, as with all standard FS signatures, the security proof is highly non-tight and the concrete parameters are set under the heuristic that the only way to attack the scheme is by finding collisions for a hash function.
- In this paper, we propose an FS-style signature scheme, called Lossy CSI-FiSh, constructed using the CSIDH-512 parameters and with a security proof based on the “Lossy Keys” technique introduced by Kiltz, Lyubashevsky and Schaffner (Eurocrypt’18).
- Lossy CSI-FiSh is provably secure under the same assumption which underlies the security of the key exchange protocol CSIDH (Castryck et al.
- (Asiacrypt’18)) and is almost as efficient as CSI-FiSh.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12110160 (1).pdf`
- `downloads/12110160.pdf`
