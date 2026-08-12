---
id: KN-LIT-5622
type: literature
title: "One-out-of-Many Proofs:"
authors:
  - "Or How to Leak a Secret"
  - "Spend a Coin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, hash, mov-fr, pairing, rsa, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct a 3-move public coin special honest verifier zero-knowledge proof, a so-called Sigma-protocol, for a list of commitments having at least one commitment that opens to 0. It is not required for the prover to know openings of the other commitments.

## Key claims (as reported)
- The proof system is efficient, in particular in terms of communication requiring only the transmission of a logarithmic number of commitments.
- We use our proof system to instantiate both ring signatures and zerocoin, a novel mechanism for bitcoin privacy.
- We use our Sigma-protocol as a (linkable) ad-hoc group identification scheme where the users have public keys that are commitments and demonstrate knowledge of an opening for one of the commitments to unlinkably identify themselves (once) as belonging to the group.
- Applying the Fiat-Shamir transform on the group identification scheme gives rise to ring signatures, applying it to the linkable group identification scheme gives rise to zerocoin.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90560252 (1).pdf`
- `downloads/90560252.pdf`
