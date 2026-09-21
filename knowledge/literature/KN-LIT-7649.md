---
id: KN-LIT-7649
type: literature
title: "Principal ideal problem and ideal shortest vector over rational primes in power-of-two cyclotomic fields"
authors:
  - "Gaohao Cui"
  - "Jianing Li"
  - "Jincheng Zhuang"
year: 2026
venue: "arXiv preprint arXiv:2601.07511 [cs.CR]"
identifiers:
  eprint: null
  doi: null
  arxiv: "2601.07511"
  url: "https://arxiv.org/abs/2601.07511"
tags: [principal-ideal-problem, ideal-lattice, cyclotomic, lattice, number-theory, ring-lwe, decomposition-field, minkowski, shortest-vector, pqc]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
Studies the **length of the shortest vector in prime ideals** lying over rational primes
`p` in power-of-two cyclotomic fields `Q(ζ_{2^{n+1}})` — the fields used to instantiate
Ring-LWE.

Extending Pan et al. (Eurocrypt 2021), who determined the shortest-vector length for
`p ≡ 3, 5 (mod 8)` via explicit reduced lattice bases, this paper:

- gives a **new method** for the `p ≡ 3, 5 (mod 8)` case that does not proceed by
  analysing lattice bases;
- **precisely characterizes** the shortest-vector length for `p ≡ 7, 9 (mod 16)`;
- derives a general upper bound `⁴√(2^{2n+1} p)`, reported **tighter** than the bound
  `2^n · ⁴√p` obtainable from Minkowski's theorem.

The stated key technique: determine whether a **generator of a principal ideal**
achieves the shortest length under the canonical embedding. Where it does, ideal-SVP in
that ideal **reduces to finding a shortest generator** — i.e. to SG-PIP.

## Key claims (as reported)
- New derivation for `p ≡ 3, 5 (mod 8)`; new exact results for `p ≡ 7, 9 (mod 16)`.
- Upper bound `⁴√(2^{2n+1} p)`, tighter than the Minkowski bound `2^n ⁴√p`.
- Reduction of ideal-SVP to shortest-generator-finding, **for those ideals where the
  generator is shortest** — a conditional, per-ideal statement, not a general reduction.
- Scope is **prime ideals over rational primes in power-of-two cyclotomic fields**. No
  claim about general ideals, general fields, or deployed Ring-LWE parameters.

## Relevance to this program
Held as the **commutative reference point** for the PIP thread that [[KN-LIT-7641]],
[[KN-LIT-7647]] and [[KN-TECH-081]] open on the non-commutative side. The cyclotomic
case is the one where the historical arc is complete and known: PIP became tractable,
then short-generator recovery followed from log-unit-lattice structure, and Soliloquy
fell. This paper is a current increment inside that well-understood setting, and it is
useful precisely because it shows **which quantities the analysis turns on** — the
splitting behaviour of `p`, the canonical embedding, and whether a generator is short.

Those are the quantities an analogous quaternion-order analysis would need. **This
entry asserts no such analogue exists**; it records the commutative template.

Also worth noting for honesty about direction of travel: the results here are **bounds
and structure**, not an attack. The abstract claims no break of any Ring-LWE instance.

**Does not bear on the ECDLP.**

## Not verified here
Full paper not read. Claims relayed from the arXiv API abstract for 2601.07511,
retrieved 2026-08-01 (hence `confidence: reported`). arXiv metadata: submitted
2026-01-12, category cs.CR, three authors, v2. Preprint — not peer-reviewed, no DOI or
venue as of this entry.

NOT verified here: the new method; the exact characterizations for `p ≡ 7, 9 (mod 16)`;
the upper bound or its comparison to Minkowski; the conditional ideal-SVP reduction; or
the attribution to Pan et al. (Eurocrypt 2021), which is relayed from this abstract and
is not itself an entry in this corpus. No consequence for any deployed Ring-LWE or
Module-LWE parameter set is claimed.
