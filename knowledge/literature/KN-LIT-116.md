---
id: KN-LIT-116
type: literature
title: Short Stickelberger Class Relations and application to Ideal-SVP
authors: [Cramer Ronald, Ducas Leo, Wesolowski Benjamin]
year: 2017
venue: EUROCRYPT 2017 (ePrint 2016/885)
identifiers:
  eprint: iacr:2016/885
  doi: null
  url: https://eprint.iacr.org/2016/885
tags: [ideal-svp, stickelberger, class-group, cyclotomic, quantum, approximation-factor, ring-lwe, structure, hardness-gap, lattice]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
Extends the principal-ideal results (KN-LIT-115) to *general* ideals in
cyclotomic fields by exploiting the classical theorem that the class group is
annihilated by the Stickelberger ideal. Under stated number-theoretic
hypotheses this solves Ideal-SVP in the worst case in quantum polynomial time at
approximation factor `exp(O~(sqrt(n)))`, deepening the known hardness gap
between general and structured lattices.

## Key claims (as reported)
- The close principal multiple (CPM) problem is solved by exploiting the
  Galois-module action of the Stickelberger ideal on the class group; under
  plausible number-theoretical hypotheses the approach yields a close principal
  multiple in quantum polynomial time. The hypotheses are explicitly flagged as
  unproven by the authors.
- Combined with prior results this solves worst-case Ideal-SVP in quantum
  polynomial time at approximation factor `exp(O~(sqrt(n)))`.
- **The authors' own scoping statement:** "it does not seem that the security of
  Ring-LWE based cryptosystems is directly affected." The result deepens the gap
  between general and structured lattices without breaking deployed schemes.
- Context recalled by the paper: earlier work in this line broke Soliloquy, the
  Smart-Vercauteren FHE scheme, and GGH multilinear maps -- but those used a
  special class of principal ideals.

## Relevance to this program
The strongest available answer to "does ring/module structure weaken the
underlying lattice problem?" -- and the answer is a carefully bounded yes.
Worst-case Ideal-SVP is quantum-polynomial at `exp(O~(sqrt(n)))`, general
lattices are not known to be, and yet Ring-LWE at deployed parameters is
untouched because deployed schemes need only small approximation factors. For
KN-OPEN-012 this is the state of the art and the reason the open problem stays
open: the gap has been demonstrated in a regime that does not reach the
parameters anyone deploys, and nobody has shown how to close the distance. Any
program proposal in this direction must state which approximation factor it
targets, or it is not a well-posed proposal.

## Not verified here
The ePrint abstract was fetched and read. The Stickelberger machinery, the
number-theoretic hypotheses, and the CPM algorithm were not verified or
re-derived. Whether subsequent work has weakened the hypotheses or improved the
approximation factor was not checked as of this entry's date.
