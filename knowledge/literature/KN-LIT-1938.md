---
id: KN-LIT-1938
type: literature
title: "TriSweep: A Four-Drone Swarm Framework for Electromagnetic Side-Channel Analysis"
authors:
  - "Eric Yocam∗"
  - "Varghese Vaidyan"
year: 2026
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2605.22709"
  url: "https://arxiv.org/abs/2605.22709"
tags: [cryptanalysis, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Electromagnetic (EM) side-channel analysis traditionally assumes a stationary, closeproximity probe—a threat model that underestimates aerial adversaries. TriSweep is a simulation framework that designs and evaluates a four-drone swarm architecture for autonomous standoff EM-SCA of embedded microcontrollers at 0.25–1.5 m.

## Key claims (as reported)
- Three spatially specialized collector drones—Anchor (full-spectrum), Mask Probe (mask-register loading leakage), and Cipher Probe (masked SubBytes output leakage)—feed a stationary Accumulator drone that performs coherent combining (+4.8 dB SNR gain) and second-order mask cancellation via a centered product of the two spatially separated leakage streams.
- Evaluated against three real ANSSI ASCAD datasets (ATmega8515 masked AES-128 and 50/100-sample desynchronized variants), the framework achieves a simulated key rank 18 ± 1.7 (five-seed) at 0.25 m on the primary masked dataset.
- Profiling-trace cross-correlation alignment reduces the single-drone rank from 89 to 21 on the 100-sample-jitter variant, demonstrating compensation for drone hover vibration.
- A two-channel CNN in the Accumulator converges to a loss of 0.454 (vs. random baseline 5.545) and improves rank on desynchronized datasets.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2605.22709v1.pdf`
