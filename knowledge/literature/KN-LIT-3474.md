---
id: KN-LIT-3474
type: literature
title: "DPA, Bitslicing and Masking at 1 GHz"
authors:
  - "Josep Balasch"
  - "Benedikt Gierlichs"
  - "Oscar Reparaz"
  - "Ingrid Verbauwhede"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, mov-fr, rsa, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present DPA attacks on an ARM Cortex-A8 processor running at 1 GHz. This high-end processor is typically found in portable devices such as phones and tablets.

## Key claims (as reported)
- In our case, the processor sits in a single board computer and runs a full-fledged Linux operating system.
- The targeted AES implementation is bitsliced and runs in constant time and constant flow.
- We show that, despite the complex hardware and software, high clock frequencies and practical measurement issues, the implementation can be broken with DPA starting from a few thousand measurements of the electromagnetic emanation of a decoupling capacitor near the processor.
- To harden the bitsliced implementation against DPA attacks, we mask it using principles of hardware gate-level masking.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92930578 (1).pdf`
- `downloads/92930578.pdf`
