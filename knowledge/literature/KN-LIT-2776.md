---
id: KN-LIT-2776
type: literature
title: "Bounded Collusion ABE for TMs from IBE"
authors:
  - "Rishab Goyal∗"
  - "Ridwan Syed"
  - "Brent Waters"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mov-fr, mpc, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We give an attribute-based encryption system for Turing Machines that is provably secure assuming only the existence of identitybased encryption (IBE) for large identity spaces. Currently, IBE is known to be realizable from most mainstream number theoretic assumptions that imply public key cryptography including factoring, the search DiffieHellman assumption, and the Learning with Errors assumption.

## Key claims (as reported)
- Our core construction provides security against an attacker that makes a single key query for a machine T before declaring a challenge string w∗ that is associated with the challenge ciphertext.
- We build our construction by leveraging a Garbled RAM construction of Gentry, Halevi, Raykova and Wichs [33]; however, to prove security we need to introduce a new notion of security called iterated simulation security.
- We then show how to transform our core construction into one that is secure for an a-priori bounded number q = q(λ) of key queries that can occur either before or after the challenge ciphertext.
- We do this by first showing how one can use a special type of non-committing encryption to transform a system that is secure only if a single key is chosen before the challenge ciphertext is declared into one where the single key can be requested either before or after the challenge ciphertext.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900128 (1).pdf`
- `downloads/130900128.pdf`
