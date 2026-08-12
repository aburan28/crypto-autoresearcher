---
id: KN-LIT-5928
type: literature
title: "Program Obfuscation with Leaky Hardware"
authors:
  - "Nir Bitansky"
  - "Ran Canetti"
  - "Shafi Goldwasser"
  - "Shai Halevi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider general program obfuscation mechanisms using “somewhat trusted” hardware devices, with the goal of minimizing the usage of the hardware, its complexity, and the required trust. Specifically, our solution has the following properties: (i) The obfuscation remains secure even if all the hardware devices in use are leaky.

## Key claims (as reported)
- That is, the adversary can obtain the result of evaluating any function on the local state of the device, as long as this function has short output.
- In addition the adversary also controls the communication between the devices.
- (ii) The number of hardware devices used in an obfuscation and the amount of work they perform are polynomial in the security parameter independently of the obfuscated function’s complexity.
- (iii) A (universal) set of hardware components, owned by the user, is initialized only once and from that point on can be used with multiple “software-based” obfuscations sent by different vendors.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/70730714 (1).pdf`
- `downloads/70730714 (2).pdf`
- `downloads/70730714 (3).pdf`
- `downloads/70730714.pdf`
