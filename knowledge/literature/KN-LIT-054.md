---
id: KN-LIT-054
type: literature
title: Worst-case to average-case reductions for module lattices (Module-LWE/SIS)
authors: [Langlois Adeline, Stehle Damien]
year: 2015
venue: Designs, Codes and Cryptography, 75(3):565-599
identifiers:
  eprint: iacr:2012/090
  doi: 10.1007/s10623-014-9938-4
  url: https://eprint.iacr.org/2012/090
tags: [module-lwe, module-sis, module-lattice, worst-case-average-case, structured-lattice, kyber, dilithium, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Defines Module-SIS and Module-LWE, which interpolate between the unstructured
(SIS/LWE, KN-LIT-049, KN-LIT-050) and fully ring-structured (Ring-LWE,
KN-LIT-053) settings over module lattices. Proves these average-case problems are
at least as hard as worst-case lattice problems restricted to module lattices.

## Key claims (as reported)
- Module lattices trade some Ring-LWE efficiency for a more conservative hardness
  assumption (larger, tunable "module rank").
- This module framework is the concrete hardness basis for Kyber (KN-LIT-055) and
  Dilithium (KN-LIT-056).

## Relevance to this program
POST-QUANTUM foundation, ADJACENT to the ECDLP mission. Recorded as context: the
NIST-standardized lattice schemes rest on Module-LWE/SIS, so the corpus documents
the exact assumption behind the intended ECDLP replacements. The module structure
is intermediate between unstructured and ideal -- relevant to KN-OPEN-012 (does the
structure admit index-calculus-style attacks?).

## Not verified here
Full paper not read; the module-lattice reductions relayed from the abstract
(hence confidence: reported). Fields confirmed against the DCC/Springer DOI and
IACR ePrint 2012/090 via search, not by fetching the primary pages.
