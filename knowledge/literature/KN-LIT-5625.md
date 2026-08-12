---
id: KN-LIT-5625
type: literature
title: "One-Round Key Exchange with Strong Security:"
authors:
  - "An Efficient"
  - "Generic Construction"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
One-round authenticated key exchange (ORKE) is an established research area, with many prominent protocol constructions like HMQV (Krawczyk, CRYPTO 2005) and Naxos (La Macchia et al., ProvSec 2007), and many slightly different, strong security models. Most constructions combine ephemeral and static Diffie-Hellman Key Exchange (DHKE), in a manner often closely tied to the underlying security model.

## Key claims (as reported)
- We give a generic construction of ORKE protocols from general assumptions, with security in the standard model, and in a strong security model where the attacker is even allowed to learn the randomness or the longterm secret of either party in the target session.
- The only restriction is that the attacker must not learn both the randomness and the long-term secret of one party of the target session, since this would allow him to recompute all internal states of this party, including the session key.
- This is the first such construction that does not rely on random oracles.
- The construction is intuitive, relatively simple, and efficient.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90200160 (1).pdf`
- `downloads/90200160 (2).pdf`
- `downloads/90200160 (3).pdf`
- `downloads/90200160 (4).pdf`
- `downloads/90200160.pdf`
