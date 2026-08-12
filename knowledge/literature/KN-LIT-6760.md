---
id: KN-LIT-6760
type: literature
title: "Spartan and Bulletproofs are simulation-extractable (for free!)"
authors:
  - "Quang Dao"
  - "Paul Grubbs"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, pairing, provable-security, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Increasing deployment of advanced zero-knowledge proof systems, especially zkSNARKs, has raised critical questions about their security against real-world attacks. Two classes of attacks of concern in practice are adaptive soundness attacks, where an attacker can prove false statements by choosing its public input after generating a proof, and malleability attacks, where an attacker can use a valid proof to create another valid proof it could not have created itself.

## Key claims (as reported)
- Prior work has shown that simulation-extractability (SIM-EXT), a strong notion of security for proof systems, rules out these attacks.
- In this paper, we prove that two transparent, discrete-log-based zkSNARKs, Spartan and Bulletproofs, are simulation-extractable (SIM-EXT) in the random oracle model if the discrete logarithm assumption holds in the underlying group.
- Since these assumptions are required to prove standard security properties for Spartan and Bulletproofs, our results show that SIM-EXT is, surprisingly, “for free” with these schemes.
- Our result is the first SIM-EXT proof for Spartan and encompasses both linear- and sublinear-verifier variants.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004277 (1).pdf`
- `downloads/14004277.pdf`
