---
id: KN-LIT-7565
type: literature
title: 'Multilevel Amortized Gaussian Elimination in Information-Set Decoding: Applications to HQC and PCG'
authors: [Carrier Kevin, Hatey Valerian, Luzzi Laura, Tillich Jean-Pierre]
year: 2026
venue: 'Cryptology ePrint Archive, Paper 2026/1498'
identifiers:
  eprint: iacr:2026/1498
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/1498
tags: [information-set-decoding, gaussian-elimination, amortization, linear-algebra-cost, stern, code-based, hqc, pcg, gate-cost-model, branching-process, security-estimate, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-26
superseded_by: null
---

## Contribution
Revisits the Reduce-and-Prange technique of Kim and Lee, which lowers the cost of
Gaussian elimination inside Information Set Decoding (ISD) by **reusing partial
pivots** across iterations, refines its complexity analysis with branching-process
techniques, and extends pivot reuse to Stern's algorithm as **MAGE-Stern** (multilevel
amortized Gaussian elimination). The setting is the sublinear-weight decoding regime,
where the linear-algebra step is no longer a negligible additive term but a
significant share of total attack cost.

## Key claims (as reported)
- In the sublinear regime relevant to HQC and Pseudorandom Correlation Generators, the
  cost of Gaussian elimination "significantly affects the overall attack complexity" —
  it cannot be dropped as lower-order.
- Branching-process analysis gives a more accurate assessment of Reduce-and-Prange
  than the original.
- Under a **consistent logic-gate cost model**, MAGE-Stern improves on the best
  previously known attack against HQC by about **3 bits in time** while *also*
  reducing **memory by about 12 bits**.
- This places the standardized **HQC Category I** parameter set at roughly **140-bit**
  security, about **3 bits below its NIST security target**.
- Combining multilevel amortized Gaussian elimination with the projective-decoding
  framework of Carrier-Hatey-Tillich and applying it to regular decoding improves on
  the best known attacks against the reference PCG parameter sets of
  Boyle-Couteau-Gilboa-Ishai by **up to 6 bits** over a broad range of practical
  parameters.

## Relevance to this program
Code-based, therefore `adjacent` to the ECDLP mission — but methodologically this is
close to the program's own live concerns, on three counts:

1. **The linear-algebra step is not free.** `KN-TECH-008` (sparse and structured linear
   algebra over finite fields) exists because index calculus pays a matrix-solve cost
   after relation collection. This paper is a worked example, in a neighbouring
   problem, of an attack whose exponent statement changed once the elimination step was
   costed honestly rather than absorbed into `O~()`. That is precisely the discipline
   the program applies to relation-matrix solves.
2. **Amortization across iterations is where the gain lives.** The mechanism —
   reusing partial pivots so successive eliminations do not restart — is an
   amortization argument. The program's own barrier catalogue records repeated failures
   of amortization to move the ECDLP exponent (the `BAR-AMORT` family in the ledger).
   This is a case where amortization *did* pay, in a problem whose structure permits
   reuse across iterations. Worth reading for what structural property makes reuse
   possible, and confirming the ECDLP relation-collection loop lacks it.
3. **Consistent gate cost model + memory reported alongside time.** The result is
   stated as a (time, memory) pair under one declared model, and the memory saving is
   larger than the time saving. This is the reporting standard `KN-TECH-035` asks for.

Does **not** bear on the ECDLP directly and forecloses nothing on the index-calculus
line. The HQC security-margin claim is a claim about a code-based standard, recorded
here as context, not as a program result.

## Not verified here
Full paper not read; all claims relayed from the official ePrint abstract retrieved
from eprint.iacr.org on 2026-07-26 (hence `confidence: reported`). ePrint history:
received 2026-07-22, approved 2026-07-25. Not peer-reviewed as of this entry; no DOI.

NOT verified here: the branching-process analysis, the gate-cost model's details and
whether it is the same model used by the HQC team's own estimate (a 3-bit gap is
within the range that model choice alone can produce), the 140-bit figure, the
claimed improvements on PCG parameter sets, and whether the "best previously known
attack" baseline is current. The referenced works (Kim-Lee Reduce-and-Prange,
Carrier-Hatey-Tillich projective decoding, Boyle-Couteau-Gilboa-Ishai PCG parameters)
are not in this corpus and were not checked. **No conclusion about HQC's standing
should be drawn from this entry alone.**
