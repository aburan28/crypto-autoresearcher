---
id: KN-TECH-029
type: technique
title: Supersingular isogeny-problem algorithms (classical and quantum path-finding)
tags: [isogeny-problem, path-finding, meet-in-the-middle, claw-finding, quantum, delfs-galbraith, cost-model, isogeny, adjacent]
confidence: reported
complexity: classical Otilde(p^{1/2}) meet-in-the-middle, Otilde(p^{1/4}) via F_p-subgraph; quantum Otilde(p^{1/4}); commutative case quantum subexponential
applicability: computing an isogeny/path between two given supersingular curves without auxiliary torsion data
source_refs: [KN-LIT-078, KN-LIT-079, KN-LIT-076]
added: 2026-07-23
superseded_by: null
---

## Method
For the PURE isogeny problem (two curves, no torsion images), the standard
approaches:
- **Meet-in-the-middle** over the F_{p^2} graph: grow ell-isogeny trees from both
  endpoints until they collide; expected Otilde(p^{1/2}) time and space.
- **Delfs-Galbraith** (KN-LIT-078): descend to the F_p-rational subgraph (size
  ~sqrt of the full graph), reducing the F_p case to Otilde(p^{1/4}).
- **Quantum** (Biasse-Jao-Sankar, KN-LIT-079): claw/quantum-search on the same
  structure, Otilde(p^{1/4}).
The endomorphism-ring route (KLPT + equivalence, KN-TECH-028) is the other main
attack surface.

## Complexity landscape (the reference points)
- Non-commutative (supersingular, SIDH-style) pure problem: exponential-ish
  (p^{1/4}) even quantumly -- WHY SIDH chose this setting.
- Commutative (CSIDH-style, KN-TECH-027): subexponential quantum (Kuperberg).
- With torsion images (SIDH's leak): polynomial (KN-TECH-026).
These three regimes are the map of isogeny hardness.

## Relevance to this program
Fixes the baselines against which auxiliary-information attacks are measured
(KN-OPEN-015), and the meet-in-the-middle / claw cost models are kin to the
program's birthday-bound accounting (KN-TECH-006). Adjacent to the ECDLP mission.

## Applicability limits
Costs are heuristic/asymptotic (graph-expansion and prime-distribution
assumptions). The p^{1/4} bounds are for the auxiliary-data-free problem; they say
nothing about the torsion-image regime (which is polynomial) or the concrete
security of specific parameter sets.
