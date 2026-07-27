---
id: KN-TECH-050
type: technique
title: Memory-charged cost models for supersingular isogeny path-finding
tags: [supersingular, isogeny, path-finding, meet-in-the-middle, golden-collision, van-oorschot-wiener, low-memory, memory, full-cost, cost-model, delfs-galbraith, regime, classical-baseline, quantum, cross-domain, post-quantum, adjacent]
confidence: reported
complexity: not a single expression - a regime-dependent choice among meet-in-the-middle, low-memory collision search, and Delfs-Galbraith; the step-count figures of KN-TECH-029 are the uncharged baseline, and charging memory changes which algorithm wins
applicability: any claim that names "the" classical or quantum baseline for finding an isogeny between supersingular curves; required before a matched-baseline recommendation for GOAL-SSI-001
source_refs: [KN-LIT-124, KN-LIT-125, KN-LIT-126, KN-LIT-132, KN-LIT-078, KN-LIT-012, KN-LIT-094, KN-TECH-029, KN-TECH-035, KN-TECH-044]
added: 2026-07-25
superseded_by: null
---

## Method
Do not name a baseline for supersingular isogeny path-finding without naming
three things: the **field regime**, the **memory model**, and the **degree
constraint**. Changing any one of them changes which algorithm is cheapest, and
the literature disagreements in this area are almost entirely disagreements about
these three, not about algorithms.

The candidate algorithms the corpus now carries:

- **Meet-in-the-middle.** Best step count in the general F_p^2 setting
  (`KN-TECH-029`), and the historical reference for SIDH parameter selection.
  Its cost is dominated by a table whose size is the same order as its step
  count, so it is the algorithm most exposed to memory charging.
- **van Oorschot-Wiener golden collision search** (`KN-LIT-124`, `KN-LIT-125`).
  The low-memory alternative: distinguished points and parallel collision search
  (`KN-LIT-012`) specialised to the isogeny problem. `KN-LIT-124` reports it as
  the lower-cost choice for CSSI and recommends it replace MITM for assessing
  SIDH's classical security; `KN-LIT-125` supplies the optimised implementation
  and the argument that measured behaviour, not the cost expression, is what
  security estimation needs.
- **Delfs-Galbraith** (`KN-LIT-078`). Exploits the F_p-rational subgraph and
  dominates MITM in step count on F_p-rational instances (`KN-TECH-029`), before
  any memory charge — so on that regime the memory question does not even arise.
- **Essentially memory-free fixed-degree search** (`KN-LIT-132`, 2024). When the
  isogeny degree is a fixed known `d`, memory-free algorithms are reported to
  beat MITM over a range of the degree parameter, classically and quantumly.
- **Quantum claw-finding under a charged model** (`KN-LIT-126`). Gate-count and
  depth-times-width metrics, physically justified by error-correction
  requirements, applied to SIKE.

## The result that is easy to get backwards
Charging memory does not uniformly deflate attack costs. On the classical side it
moved the recommendation *away* from MITM toward vOW (`KN-LIT-124`). On the
quantum side, charging memory **raised** SIDH/SIKE security estimates
(`KN-LIT-126`) — the same discipline, the opposite sign. The program's full-cost
rule (`KN-TECH-035`, `KN-TECH-044`) is therefore not a device for shrinking
adversary advantage; it is a device for making cost comparisons well-posed, and
it must be applied even when it works against the conclusion being argued for.

## Applicability limits
This entry is a map of which comparisons are legitimate, not a source of numbers.
It does not supply complexity constants, crossover points, or security levels for
any parameter set — those live in the cited papers and, as recorded below, were
not read here. It also does not cover the broken SIDH/SIKE torsion-image setting
as a positive target (`KN-LIT-065`-`067`, `KN-TECH-026`), which `RQ-SSI-001`
places out of scope; the algorithms above are for path-finding without published
torsion images.

The regime split is the load-bearing part. A comparison that charges memory but
silently mixes F_p^2 and F_p-rational instances, or that ignores whether the
degree is fixed, will produce a confident and wrong ranking.

## Verified vs reported
Every source entry behind this technique (`KN-LIT-124`-`126`, `KN-LIT-132`) is
`citation_verified: web` and was written under an egress policy that blocked all
direct fetches, so their bibliographic details are corroborated but **their
abstracts were not read from a primary source and none of their numbers are in
this corpus**. The step-count figures quoted above are attributed to
`KN-TECH-029`, which predates this entry, not derived here. The claim that vOW
beats MITM for CSSI, and the claim that charged quantum metrics raise SIKE
estimates, are reported from those papers and have not been independently
checked.

Consequently: this entry is sufficient to stop a matched-baseline recommendation
from being made against the wrong algorithm, and **insufficient to state what the
matched baseline costs**. A `GOAL-SSI-001` BATCH-002 derivation may use it to
structure the comparison and must obtain every quoted figure from the papers
themselves.
