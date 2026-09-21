---
id: KN-OPEN-018
type: open_problem
title: Does lattice machinery bear on the plain ECDLP at all, outside the leakage model?
tags: [cross-domain, lattice, ecdlp, hnp, coppersmith, index-calculus, descent, leakage, genericity, open]
confidence: reported
status: open
source_refs: [KN-OPEN-011, KN-TECH-019, KN-TECH-015, KN-LIT-037, KN-LIT-046, KN-TECH-020, KN-OPEN-005]
added: 2026-07-24
superseded_by: null
---

## Statement
Lattice reduction appears in ECDLP work in exactly two places: solving the
hidden number problem when nonce bits leak (KN-TECH-019, KN-LIT-043 to
KN-LIT-045), and Coppersmith-style root-finding inside index-calculus descent
and relation search (KN-TECH-015, KN-LIT-037). Both are auxiliary. The question:
**is there any route by which lattice methods bear on the plain ECDLP -- no
leakage, no implementation fault, a random point on a well-formed
prime-order curve -- or is the confinement to auxiliary roles structural?**

## Current state (as reported)
- **Leakage model only.** KN-OPEN-011 already records that the lattice/HNP line
  is confined to the leakage setting. Given enough nonce bits the lattice attack
  is devastating; given none it says nothing, because there is no hidden number
  instance to build.
- **Auxiliary inside index calculus.** Coppersmith/LLL is used as a subroutine
  for finding small roots in relation search, not as the source of any claimed
  advantage over rho. The advantage, where claimed, comes from the summation
  polynomial machinery, and the program's own work has closed several such
  routes.
- **A negative-looking structural reason.** The ECDLP has no obvious lattice
  embedding: there is no known map taking a discrete log instance in a
  prime-order elliptic curve group to a short-vector instance whose solution
  returns the log. Generic-group arguments (KN-OPEN-005) suggest why -- a
  reduction of that kind would have to exploit the curve's representation, and
  the program has already audited representation-exploiting families without
  finding an admissible candidate.
- **But no theorem.** This corpus contains no proof that such an embedding
  cannot exist. The absence is an observation about the literature, not a
  result.

## Why it matters here
The program's two focus areas are elliptic curves and lattices, and this is the
precise statement of whether they touch. The answer shapes what a combined
research direction can even be. If the confinement is structural, then work in
the two areas is methodologically shared (cost discipline, certificates,
heuristic scepticism -- see KN-TECH-044, KN-TECH-047, KN-OPEN-017) but
mathematically separate, and proposals should stop looking for a bridge. If it
is not structural, the bridge is a high-value target precisely because so little
attention has gone to it.

Note the asymmetry worth keeping in view: lattices attack *implementations* of
elliptic curve cryptography with great success, and do not attack the
*mathematical problem* at all. The program should be careful never to let the
first fact colour a claim about the second.

## What would close it
Either direction is a result. A concrete embedding of prime-order ECDLP into a
lattice problem, with an honest cost comparison against `0.886*sqrt(n)` under a
stated cost convention, would be a major finding. A scoped impossibility -- for
instance, that any such embedding respecting the group action is simulable in
the generic group model with constant overhead, in the style of the program's
existing GGM-simulability screens -- would close the direction cleanly and is
the cheaper of the two to attempt. Neither has been attempted here.
