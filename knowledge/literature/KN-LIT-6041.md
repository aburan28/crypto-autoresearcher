---
id: KN-LIT-6041
type: literature
title: "Publicly Verifiable Proofs from Blockchains"
authors:
  - "Alessandra Scafuro"
  - "Luisa Siniscalchi"
  - "Ivan Visconti"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A proof system is publicly verifiable, if anyone, by looking at the transcript of the proof, can be convinced that the corresponding theorem is true. Public verifiability is important in many applications since it allows to compute a proof only once while convincing an unlimited number of verifiers.

## Key claims (as reported)
- Popular interactive proof systems (e.g., Σ-protocols) protect the witness through various properties (e.g., witness indistinguishability (WI) and zero knowledge (ZK)) but typically they are not publicly verifiable since such proofs are convincing only for those verifiers who contributed to the transcripts of the proofs.
- The only known proof systems that are publicly verifiable rely on a non-interactive (NI) prover, through trust assumptions (e.g., NIZK in the CRS model), heuristic assumptions (e.g., NIZK in the random oracle model), specific number-theoretic assumptions on bilinear groups or relying on obfuscation assumptions (obtaining NIWI with no setups).
- In this work we construct publicly verifiable witness-indistinguishable proof systems from any Σ-protocol, based only on the existence of a very generic blockchain.
- The novelty of our approach is in enforcing a non-interactive verification (thus guaranteeing public verifiability) while allowing the prover to be interactive and talk to the blockchain (this allows us to circumvent the need of strong assumptions and setups).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114420270 (1).pdf`
- `downloads/114420270.pdf`
