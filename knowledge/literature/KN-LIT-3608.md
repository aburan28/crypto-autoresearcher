---
id: KN-LIT-3608
type: literature
title: "Efficient Power and Timing Side Channels for Physical Unclonable Functions"
authors:
  - "Ulrich Rührmair"
  - "Xiaolin Xu"
  - "Jan Sölter "
  - "Ahmed Mahmoud"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, pairing, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
One part of the original PUF promise was their improved resilience against physical attack methods, such as cloning, invasive techniques, and arguably also side channels. In recent years, however, a number of effective physical attacks on PUFs have been developed [17, 18, 20, 8, 2].

## Key claims (as reported)
- This paper continues this line of research, and introduces the first power and timing side channels (SCs) on PUFs, more specifically on Arbiter PUF variants.
- Concretely, we attack so-called XOR Arbiter PUFs and Lightweight PUFs, which prior to our work were considered the most secure members of the Arbiter PUF family [28, 30].
- We show that both architectures can be tackled with polynomial complexity by a combined SC and machine learning approach.
- Our strategy is demonstrated in silicon on FPGAs, where we attack the above two architectures for up to 16 XORs and 512 bits.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/87310188 (1).pdf`
- `downloads/87310188 (2).pdf`
- `downloads/87310188 (3).pdf`
- `downloads/87310188.pdf`
