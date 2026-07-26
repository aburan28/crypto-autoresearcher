---
id: KN-LIT-2875
type: literature
title: "Characterizing Deterministic-Prover Zero Knowledge"
authors:
  - "Nir Bitansky"
  - "Arka Rai Choudhuri"
year: null
venue: "Journal of Cryptology"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Randomness is typically thought to be essential for zero knowledge protocols. Following this intuition, Goldreich and Oren (Journal of Cryptology 94) proved that auxiliary-input zero knowledge cannot be achieved with a deterministic prover.

## Key claims (as reported)
- On the other hand, positive results are only known in the honestverifier setting, or when the prover is given at least a restricted source of entropy.
- We prove that removing (or just bounding) the verifier’s auxiliary input, deterministicprover zero knowledge becomes feasible: – Assuming non-interactive witness-indistinguishable proofs and subexponential indistinguishability obfuscation and one-way functions, we construct deterministic-prover zero-knowledge arguments for NP ∩ coNP against verifiers with bounded non-uniform auxiliary input. – Assuming also keyless hash functions that are collision-resistant against boundedauxiliary-input quasipolynomial-time attackers, we construct similar arguments for all of NP.
- Together with the result of Goldreich and Oren, this characterizes when deterministicprover zero knowledge is feasible.
- We also demonstrate the necessity of strong assumptions, by showing that deterministic prover zero knowledge arguments for a given language imply witness encryption for that language.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12550171 (1).pdf`
- `downloads/12550171.pdf`
