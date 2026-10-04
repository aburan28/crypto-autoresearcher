# Galbraith ECDLP threads: open experimental successors (2026-09-18)

This note records the repository check triggered by the Galbraith slides on larger
group actions, symmetry breaking, Frobenius, finite-field-DLP analogies and
Sarkar-Singh relation generation.

The conclusion is not that these mechanisms are new. Several are established prior
art. The repository gap is that some mechanisms were measured only outside their
intended regime, have engineering/specification work but no admitted scientific
execution, or have never been implemented as a matched backend in the current harness.

## 1. Distinct coset factor bases: do not duplicate the old idea

The distinct-factor-base construction is already present in the repository and has
priority history through Nagao/Diem/Matsuo, with Galbraith-Gebregiyorgis as another
published treatment.

Existing chain:

- H-SEMBIN-c59e50
- EXP-SEMBIN-92724f
- EV-SEMBIN-4614e7
- knowledge/literature/KN-LIT-ebd657.md
- inputs/GG-2014-806/paper_fulltext.txt

The existing run is real, but it did not measure a Groebner/F4 solving degree and
none of its seven image-size cells satisfied the heuristic's own large-k,
low-saturation regime. The evidence itself recommends an in-regime successor scored
against the exact finite-k counting cap.

Opened successor:

- IDEA-20260918-c05e71 - in-regime coset-typed solver-degree conservation test.

The scientific question is now whether the combinatorial symmetry saving survives
the actual solver or is conserved as degree/Macaulay growth.

## 2. Small-torsion / PGL2 quotient coordinates: correctness machinery exists

Prior art already establishes small-order torsion symmetries and equivariant maps to
P1. No novelty is assigned to that mechanism.

The repository already has retrieved source text under
research/equation-schemes-20260905/retrieved-pages/hal-00935050.txt, literature
review in the BATCH-011 coverage review, and exact finite model/transport controls in
EXP-ECDLP-abf981.

But EXP-ECDLP-abf981/source-v4/runner-integration.md still says that an admitted
scientific run has not demonstrated the final path. More importantly, that
experiment's main independent variable is the curve model / finite presentation; it
does not directly answer the full torsion-quotient factor-base trade.

Opened successor:

- IDEA-20260918-7a11c2 - torsion-equivariant quotient-map PDP benchmark.

The design compares ordinary x, an actual torsion quotient/equivariant coordinate
phi, and fixed PGL2 conjugates mu o phi while measuring relation density, independent
rank, solver cost and final linear-algebra dimension.

## 3. Sarkar-Singh incidence vs Semaev vs function-first

The repo contains Sarkar-Singh decomposition references and substantial Nagao /
function-first work, but the search did not locate a direct experiment implementing
the Sarkar-Singh relation generator as a benchmark backend against both Semaev and
the current H|L_V coefficient-first solver.

The Galbraith slide supplies a pointer to Palash Sarkar and Shashank Singh,
'A Simple Method for Obtaining Relations Among Factor Basis Elements for Special
Hyperelliptic Curves', ePrint 2015/179.

That source is not yet frozen/read in this repository, so it carries no evidentiary
weight until retrieved.

Opened successor:

- IDEA-20260918-5a9a51 - Sarkar-Singh incidence plus function-first relation generator.

The first task is a faithful reproduction on the special curve family, not an
attempted generic-ECC transfer. Only after exact relation equivalence is established
should it be compared with H|L_V, quotient-space rank testing and Semaev.

## Common acceptance rule

All three successors use the same bar:

1. Same mathematical relation predicate and matched support wherever a comparison is claimed.
2. Exact recovery and independent group/divisor verification.
3. Failed candidates, preprocessing, extraction and final linear algebra are charged.
4. Relation rank, not raw relation count, is the downstream quantity.
5. A promotion-worthy signal is at least 20% lower complete cost per verified independent relation across an increasing size ladder.
6. Toy/medium wins remain scoped and do not imply a sub-rho asymptotic result.

## Proposed execution order

1. Freeze/read ePrint 2015/179 and build the exact Sarkar-Singh reproducer.
2. In parallel, make a real solver backend available for the coset-typed in-regime degree experiment.
3. Reuse EXP-ECDLP-abf981 transport/verifier code to instantiate the actual torsion quotient coordinate and PGL2 controls.
4. Run all three through the same end-to-end cost ruler and relation-rank accounting.

The purpose is to turn three literature-adjacent threads into falsifiable experiments,
not to count literature ingestion or unexecuted engineering as evidence.
