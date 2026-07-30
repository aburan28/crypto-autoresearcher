---
id: KN-LIT-5155
type: literature
title: "New Techniques for SPHFs and E cient One-Round PAKE Protocols"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, protocol, provable-security, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Password-authenticated key exchange (PAKE) protocols al- low two players to agree on a shared high entropy secret key, that depends on their own passwords only. Following the Gennaro and Lindell's approach, with a new kind of smooth-projective hash functions (SPHFs), Katz and Vaikuntanathan recently came up with the rst concrete one-round PAKE protocols, where the two players just have to send simultaneous ows to each other.

## Key claims (as reported)
- The rst one is secure in the BellarePointcheval-Rogaway (BPR) model and the second one in the Canetti's UC framework, but at the cost of simulation-sound non-interactive zeroknowledge (SS-NIZK) proofs (one for the BPR-secure protocol and two for the UC-secure one), which make the overall constructions not really e cient.
- This paper follows their path with, rst, a new e cient instantiation of SPHF on Cramer-Shoup ciphertexts, which allows to get rid of the SS-NIZK proof and leads to the design of the most e cient one-round PAKE known so far, in the BPR model, and in addition without pairings.
- In the UC framework, the security proof required the simulator to be able to extract the hashing key of the SPHF, hence the additional SS-NIZK proof.
- We improve the way the latter extractability is obtained by introducing the notion of trapdoor smooth projective hash functions (TSPHFs).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80420126 (1).pdf`
- `downloads/80420126 (2).pdf`
- `downloads/80420126 (3).pdf`
- `downloads/80420126.pdf`
