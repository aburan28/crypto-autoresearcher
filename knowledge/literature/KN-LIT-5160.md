---
id: KN-LIT-5160
type: literature
title: "NIZK from SNARG"
authors:
  - "Fuyuki Kitagawa"
  - "Takahiro Matsuda"
  - "Takashi Yamakawa"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, mpc, pairing, provable-security, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We give a construction of a non-interactive zero-knowledge (NIZK) argument for all NP languages based on a succinct non-interactive argument (SNARG) for all NP languages and a one-way function. The succinctness requirement for the SNARG is rather mild: We only require that the proof size be |π| = poly(λ)(|x| + |w|)c for some constant c < 1/2, where |x| is the statement length, |w| is the witness length, and λ is the security parameter.

## Key claims (as reported)
- Especially, we do not require anything about the efficiency of the verification.
- Based on this result, we also give a generic conversion from a SNARG to a zero-knowledge SNARG assuming the existence of CPA secure publickey encryption.
- For this conversion, we require a SNARG to have efficient verification, i.e., the computational complexity of the verification algorithm is poly(λ)(|x| + |w|)o(1) .
- Before this work, such a conversion was only known if we additionally assume the existence of a NIZK.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12550176 (1).pdf`
- `downloads/12550176.pdf`
