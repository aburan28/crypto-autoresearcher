---
id: KN-TECH-046
type: technique
title: Structured-lattice attacks and the approximation-factor ceiling
tags: [ideal-svp, principal-ideal, stickelberger, class-group, cyclotomic, quantum, approximation-factor, ring-lwe, module-lwe, structure, hardness-gap, lattice]
confidence: reported
complexity: quantum polynomial time for Ideal-SVP at approximation factor exp(O~(sqrt(n))) in cyclotomic fields, under stated number-theoretic hypotheses; nothing known at the small polynomial factors deployed schemes rely on
applicability: ideal and principal-ideal lattices in cyclotomic number fields; the results do not extend to general lattices, and their relevance to Ring-LWE at deployed parameters is explicitly disclaimed by their authors
source_refs: [KN-LIT-115, KN-LIT-116, KN-LIT-117, KN-LIT-053, KN-LIT-054, KN-TECH-022, KN-OPEN-012]
added: 2026-07-24
superseded_by: null
---

## Method
The attack line on structured lattices runs through number theory rather than
through lattice reduction:

1. **Quantum class-group and principal-ideal computation** (KN-LIT-117). Both
   problems reduce to computing S-unit groups, which reduces quantumly to the
   continuous hidden subgroup problem, giving polynomial time in arbitrary-degree
   number fields (class group under GRH).
2. **Short generator recovery** (KN-LIT-115). Given *some* generator of a
   principal ideal, decoding the log-unit lattice recovers a *short* generator.
   Proven efficient for prime-power cyclotomics and typical short-generator
   distributions -- this was the step earlier sketches asserted without proof.
3. **From principal to general ideals** (KN-LIT-116). The class group is
   annihilated by the Stickelberger ideal, which under plausible
   number-theoretic hypotheses yields a close principal multiple, extending the
   attack to arbitrary ideals.

Composed: worst-case Ideal-SVP in quantum polynomial time at approximation
factor `exp(O~(sqrt(n)))`.

## The ceiling is the whole point
`exp(O~(sqrt(n)))` is superpolynomial. Ring-LWE and Module-LWE based schemes
rely on hardness at *small polynomial* approximation factors. The gap between
what has been broken and what is deployed is therefore enormous, and the authors
of KN-LIT-116 say so themselves: "it does not seem that the security of
Ring-LWE based cryptosystems is directly affected."

Both halves must be stated together, because each half alone is a
misrepresentation:

- Structure demonstrably changes complexity. There is a proven hardness gap
  between general lattices and ideal lattices that does not exist in the generic
  model, and real schemes (Soliloquy, Smart-Vercauteren FHE, GGH multilinear
  maps) were broken along this line.
- No deployed Ring-LWE or Module-LWE parameter set is affected, and no route
  from `exp(O~(sqrt(n)))` down to polynomial factors is known.

A program proposal in this direction is not well-posed unless it names the
approximation factor it targets. That is the concrete form of the question
KN-OPEN-012 asks.

## Applicability limits
Results are specific to cyclotomic fields, largely prime-power cyclotomics, and
depend on GRH and on unproven number-theoretic hypotheses. The quantum steps are
asymptotic -- nothing here speaks to circuit sizes, in contrast to the concrete
resource estimates available for ECDLP (KN-LIT-099) and for sieving
(KN-LIT-122). Module-LWE's extra structure over Ring-LWE is not addressed by
these results at all.

## Verified vs reported
The composition of the three results, the `exp(O~(sqrt(n)))` factor, the GRH and
hypothesis dependencies, and the authors' own disclaimer about Ring-LWE are
read from the abstracts of KN-LIT-115, KN-LIT-116 and KN-LIT-117. None of the
number theory was verified, and whether later work has improved the
approximation factor or weakened the hypotheses was not checked. The framing of
the approximation factor as a well-posedness requirement for program proposals
is this program's own rule, not a claim from the sources.
