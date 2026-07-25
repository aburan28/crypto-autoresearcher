---
id: KN-TECH-050
type: technique
title: Matched classical baselines for supersingular path-finding under full cost
tags: [isogeny-problem, path-finding, full-cost, mitm, delfs-galbraith, claw-finding, pcs, baseline, cost-model, supersingular, isogeny]
confidence: reported
complexity: F_p2 honest full-cost baseline is low-memory claw-PCS at O~(p^{1/2}) steps or high-memory MITM charged as O~(p^{2/3+o(1)}); F_p-rational baseline remains Delfs-Galbraith O~(p^{1/4})
applicability: any GOAL-SSI / CGL / pure path-finding cost comparison that quotes classical algorithms without torsion images
source_refs: [KN-TECH-029, KN-TECH-024, KN-LIT-078, KN-LIT-094, KN-TECH-035, EV-SSI-002, DEC-20260725-003]
added: 2026-07-25
superseded_by: null
---

## Method
Split pure supersingular path-finding into two regimes before naming a baseline:

1. **\(\mathbb{F}_{p^2}\) pure graph.** Step-count MITM is \(\tilde{O}(p^{1/2})\) time
   and space (`KN-TECH-029`). Under Wiener full-cost accounting (`KN-LIT-094`),
   a \(\tilde{\Theta}(p^{1/2})\)-size table is not free; by BSGS-shaped analogy the
   high-memory MITM full cost is \(\tilde{O}(p^{2/3+o(1)})\). The honest small-memory
   comparator is claw-finding distinguished-point parallel collision search on
   public isogeny-graph walks (modelled; no torsion oracle).
2. **\(\mathbb{F}_p\)-rational instances.** Delfs–Galbraith \(\tilde{O}(p^{1/4})\)
   already dominates MITM in step count; charging MITM memory only widens that
   gap. Matched baseline remains DG (`KN-LIT-078`, `KN-TECH-029`).

## Why the program needs it
Prevents straw-baseline advantages: a candidate must not claim to beat
"MITM \(\tilde{O}(p^{1/2})\)" while ignoring MITM memory, and must not use MITM as
the \(\mathbb{F}_p\) baseline when DG applies. This is the isogeny counterpart of
`KN-TECH-035` / `KN-TECH-044` cost discipline.

## Applicability limits
The MITM \(\mapsto p^{2/3}\) statement is a **reported Wiener analogy**, not a
wiring theorem re-proved for isogeny-graph tables. The claw-PCS algorithm is a
**modelled baseline-hygiene definition**, not a pinned primary complexity
theorem. Quantum baselines (`KN-LIT-079`) and CSIDH hidden-shift costs are out
of scope. Promoted from `GOAL-SSI-001` BATCH-002 review (`EV-SSI-002`,
`DEC-20260725-003`); not an internal cryptanalytic finding.

## Verified vs reported
Regime split and DG dominance: reported from `KN-TECH-029` / `KN-LIT-078`.
Wiener BSGS \(n^{2/3}\): established in `KN-LIT-094`. MITM full-cost map and
claw-PCS baseline identity: program derivation confirmed under weakened
independence in BATCH-002; treat as reported hygiene, not established complexity.
