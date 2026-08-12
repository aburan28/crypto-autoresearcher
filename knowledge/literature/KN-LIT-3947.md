---
id: KN-LIT-3947
type: literature
title: "FPGA-based True Random Number Generation using Circuit Metastability with Adaptive Feedback Control"
authors:
  - "Mehrdad Majzoobi"
  - "Farinaz Koushanfar"
  - "Srinivas Devadas"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The paper presents a novel and efficient method to generate true random numbers on FPGAs by inducing metastability in bi-stable circuit elements, e.g. flip-flops. Metastability is achieved by using precise programmable delay lines (PDL) that accurately equalize the signal arrival times to flip-flops.

## Key claims (as reported)
- The PDLs are capable of adjusting signal propagation delays with resolutions higher than fractions of a pico second.
- In addition, a real time monitoring system is utilized to assure a high degree of randomness in the generated output bits, resilience against fluctuations in environmental conditions, as well as robustness against active adversarial attacks.
- The monitoring system employs a feedback loop that actively monitors the probability of output bits; as soon as any bias is observed in probabilities, it adjusts the delay through PDLs to return to the metastable operation region.
- Implementation on Xilinx Virtex 5 FPGAs and results of NIST randomness tests show the effectiveness of our approach.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/69170017 (1).pdf`
- `downloads/69170017 (2).pdf`
- `downloads/69170017 (3).pdf`
- `downloads/69170017.pdf`
