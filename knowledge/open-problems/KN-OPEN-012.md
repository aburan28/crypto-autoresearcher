---
id: KN-OPEN-012
type: open_problem
title: Do ideal/module lattices admit structure-exploiting (index-calculus-like) attacks beyond generic BKZ, and does the ECDLP program's structure-exploitation experience transfer?
tags: [ideal-lattice, module-lattice, ring-lwe, structure-attack, index-calculus, cross-domain, post-quantum, open]
confidence: reported
status: open
source_refs: [KN-LIT-053, KN-LIT-054, KN-TECH-022]
added: 2026-07-23
superseded_by: null
---

## Statement
The efficiency of deployed lattice crypto comes from ALGEBRAIC structure
(ideal/module lattices, KN-LIT-053, KN-LIT-054). Does that structure enable
attacks that beat generic (unstructured) lattice algorithms like BKZ -- an
"index-calculus for lattices" that exploits the ring/ideal structure the way
Semaev/Gaudry index calculus exploits the group law -- or is the structure
provably no easier for the parameters in use?

## Current state (as reported)
There is genuine precedent on BOTH sides: structured problems have fallen in some
regimes (e.g. attacks on Ideal-SVP / Ring-LWE for specific parameters and large
approximation factors, and on overstretched-NTRU parameters), but for the
conservative parameters of Kyber/Dilithium/Falcon (KN-TECH-022) no structural
attack beats generic BKZ/sieving (KN-TECH-020). This is an ADJACENT
(post-quantum) question, not the program's ECDLP mission -- but it is the closest
methodological bridge, since the program's core expertise is precisely
structure-exploiting cryptanalysis (index calculus, symmetry, sparse elimination).

## Why it matters here
It is the one place the program's index-calculus / structure-exploitation
methodology could transfer to the lattice domain: the guiding question "does
exploitable algebraic structure lower the effective complexity driver?" is
identical in form to the program's ECDLP questions (KN-OPEN-001, KN-OPEN-004).
Recording it marks a legitimate cross-domain research direction while keeping it
clearly labelled as outside the current ECDLP scope; any concrete work here would
be a scope decision, not a continuation of the existing roadmap.

## Caveat
This entry states an EXTERNAL open problem to map the terrain; it is not a claim
that the program has results here, and no lattice attack is asserted. The
conservative-parameter status above is the community consensus as reported, not a
program finding.
