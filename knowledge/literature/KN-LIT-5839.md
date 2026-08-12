---
id: KN-LIT-5839
type: literature
title: "Practical Electromagnetic Template Attack on HMAC"
authors:
  - "Pierre-Alain Fouque"
  - "Gaëtan Leurent"
  - "Denis Réal"
  - "Frédéric Valette"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, implementation, lattice, pairing, protocol, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we show a very efficient side channel attack against HMAC. Our attack assumes the presence of a side channel that reveals the Hamming distance of some registers.

## Key claims (as reported)
- After a profiling phase in which the adversary has access to a device and can configure it, the attack recovers the secret key by monitoring a single execution of HMAC-SHA-1.
- The secret key can be recovered using a "template attack" with a computation of about 232 3κ compression functions, where κ is the number of 32-bit words of the key.
- Finally, we show that our attack can also be used to break the secrecy of network protocols usually implemented on embedded devices.
- We have performed experiments using a NIOS processor executed on a Field Programmable Gate Array (FPGA) to confirm the leakage model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/57470064 (1).pdf`
- `downloads/57470064 (2).pdf`
- `downloads/57470064 (3).pdf`
- `downloads/57470064.pdf`
