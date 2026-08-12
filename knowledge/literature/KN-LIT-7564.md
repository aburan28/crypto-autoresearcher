---
id: KN-LIT-7564
type: literature
title: The supersingular isogeny problem in time and memory p^{1/3+o(1)}
authors: [Wesolowski Benjamin]
year: 2026
venue: 'Cryptology ePrint Archive, Paper 2026/1486'
identifiers:
  eprint: iacr:2026/1486
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/1486
tags: [isogeny, supersingular, isogeny-path-problem, endomorphism-ring, complexity, smoothness-heuristic, memory-cost, parameter-selection, post-quantum, cost-model, frontier]
confidence: reported
citation_verified: web
added: 2026-07-26
superseded_by: null
---

## Contribution
Proves, under a plausible heuristic assumption on the smoothness of certain random
integers, that the supersingular isogeny problem can be solved in time **and** memory
`p^{1/3 + o(1)}`, improving on the previous best `p^{1/2} * (log p)^{O(1)}`.

## Key claims (as reported)
- The complexity `p^{1/3+o(1)}` holds in **both** time and memory, conditional on a
  smoothness heuristic for certain random integers (the paper states the heuristic as
  an assumption, not a theorem).
- This improves upon the previous best complexity `p^{1/2} * (log p)^{O(1)}`.
- The supersingular isogeny problem is "arguably the central hard problem underlying
  isogeny-based cryptography", and the cost of resolving it is a major — often the
  only — factor in choosing secure parameters.
- The paper explicitly **declines** to claim an immediate parameter break: the impact
  on concrete parameter sets "remains to be clarified", because the asymptotic
  advantage is mitigated by (a) a superpolynomial overhead hidden in the `o(1)`
  exponent and (b) the high memory requirement.

## Relevance to this program
This is the most consequential entry in the 2026-07-26 gather, and it puts two
existing corpus entries under tension:

- `KN-TECH-029` (supersingular isogeny-problem algorithms, classical and quantum
  path-finding) records the classical baseline in its `p^{1/2}` form. That figure is
  now, conditionally, superseded. **This entry does not rewrite `KN-TECH-029`** —
  corrections supersede rather than overwrite, and a technique revision is the
  Coordinator's call. The tension is flagged here so a grep of the corpus surfaces it.
- `KN-OPEN-013` ("How hard is the supersingular endomorphism-ring / isogeny-path
  problem, and is it a sound post-quantum foundation after the SIDH break?") is the
  open problem this bears on directly. The answer moves, but does not close: a
  heuristic asymptotic improvement with superpolynomial `o(1)` overhead and `p^{1/3}`
  memory is exactly the kind of result the program's own claim-tier discipline
  (`docs/claims-and-verification.md`) would score below a demonstrated solve.

The methodological lesson is the one the program already applies to itself, arriving
from the other direction. `KN-TECH-050` (memory-charged cost models for supersingular
isogeny path-finding) exists because the program charges memory; here an author with
a genuine exponent improvement volunteers the same caveat unprompted — an algorithm
whose memory equals its time is not `p^{1/3}` in any machine model that charges for
storage and wiring (`KN-TECH-035`). A `p^{1/3}` time / `p^{1/3}` memory algorithm and
a `p^{1/2}` time / `O(1)` memory algorithm are not comparable by exponent alone.

**Does not bear on the ECDLP.** The supersingular isogeny problem is a different
object from the elliptic-curve discrete logarithm; nothing here touches the `sqrt(p)`
barrier for the ECDLP or the index-calculus line. It is recorded because the corpus
tracks the post-quantum alternatives whose security would matter if ECDLP fell, and
because the memory-charging argument is a directly reusable instrument.

## Not verified here
Full paper not read; all claims relayed from the official ePrint abstract retrieved
from eprint.iacr.org on 2026-07-26 (hence `confidence: reported`). ePrint history:
received 2026-07-20, approved 2026-07-23. Not yet peer-reviewed or published as of
this entry; no DOI on the ePrint page.

NOT verified here: the proof, the precise statement and plausibility of the smoothness
heuristic, the size of the superpolynomial `o(1)` overhead, the exact memory access
pattern (whether it is sieve-like or random-access, which decides how badly full-cost
accounting degrades it), and the effect on any specific parameter set (SQIsign, CSIDH,
or otherwise). **No concrete parameter set should be re-costed on the basis of this
entry.** The claim that this is the previous-best `p^{1/2}` baseline was not
independently cross-checked against `KN-TECH-029`'s sources.
