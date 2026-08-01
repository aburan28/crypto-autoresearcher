---
id: KN-LIT-7591
type: literature
title: Lower bounds for the CNOT-complexity of linear reversible operators
authors:
  - "Søren Fuglede Jørgensen"
year: 2026
venue: 'arXiv preprint arXiv:2607.22248 [quant-ph]'
identifiers:
  eprint: null
  doi: null
  arxiv: '2607.22248'
  url: https://arxiv.org/abs/2607.22248
tags: [quantum, circuit-complexity, cnot-count, lower-bound, linear-reversible, additive-complexity, error-correcting-codes, resource-estimation, cost-model, explicit-construction]
confidence: reported
citation_verified: web
added: "2026-07-27"
superseded_by: null
---

## Contribution
Shows that lower bounds for the additive complexity of not-necessarily-reversible linear
operators can be **lifted to the reversible setting with only a small loss**, and uses this
to give the first explicit matrix family beating cyclic permutations in CNOT-complexity.

## Key claims (as reported)
- The CNOT-complexity of an invertible matrix over `F_2` is the minimum number of CNOT
  gates needed to synthesize the corresponding linear reversible operator.
- The maximum CNOT-complexity over all `n x n` matrices is known to be `Θ(n^2 / log n)`,
  but **no explicit family requiring a superlinear number of CNOT gates is known** — the
  hardest explicit family had been the cyclic permutations, at `3(n-1)`.
- Main technique: lifting additive-complexity lower bounds from the non-reversible to the
  reversible setting with small loss.
- Application: an explicit family built from **parity-check matrices of error-correcting
  codes** with CNOT-complexity at least `4n - o(n)`, asymptotically surpassing cyclic
  permutations.
- Concretely exhibits an explicit `A ∈ GL_n(F_2)` with `n = 17167` whose CNOT-complexity
  exceeds that of the cyclic permutation on `n` symbols.

## Relevance to this program
Recorded as a cost-model entry. `KN-TECH-037` (quantum ECDLP resource estimation, Shor
circuits for elliptic curves) is the technique entry in scope, and it is the reason this
otherwise-distant paper is in the corpus at all: CNOT count is one of the units in which
Shor-for-ECDLP circuits are costed, since the modular-arithmetic layers of those circuits
are built substantially from linear reversible operators over `F_2`.

Two things are worth recording precisely, because the gap between them is the entry's
actual content.

First, the **direction** of the result. This is a *lower* bound on synthesis cost for
specific explicit matrices — it says certain linear reversible operators cannot be built
cheaply. That is the opposite of the usual traffic in quantum resource estimation, which
is upper bounds from better circuit constructions. Lower bounds of this kind constrain how
far circuit optimisation can go, which is the sort of statement the program's full-cost
discipline (`KN-TECH-035`) values: an honest cost model needs floors, not only the
best-known ceiling.

Second, and more important, the **magnitude**. The state of the art for explicit families
moves from `3(n-1)` to `4n - o(n)` — both linear, against a known non-explicit maximum of
`Θ(n^2 / log n)`. The gap between what is provable for explicit matrices and what is true
for generic ones remains enormous. Nothing here changes any Shor-for-ECDLP resource
estimate, and this entry must not be cited as though a `4n` lower bound bounded anything in
`KN-TECH-037`. `KN-TECH-037` is unchanged and unsuperseded.

**Does not bear on the classical ECDLP.**

## Not verified here
Full paper not read; all claims relayed from the official arXiv abstract retrieved from
the arXiv API on 2026-07-27 (hence `confidence: reported`). arXiv metadata: submitted
2026-07-24, primary category quant-ph. Preprint — not peer-reviewed, no DOI or venue as of
this entry.

NOT verified here: the lifting theorem from additive to CNOT complexity and the size of its
"small loss"; the `4n - o(n)` bound and the code-based construction achieving it; the
`Θ(n^2 / log n)` maximum attributed to prior work; the `3(n-1)` figure for cyclic
permutations; and the explicit `n = 17167` matrix and its claimed complexity. **Whether
CNOT-complexity lower bounds for these particular code-derived families bear on any circuit
appearing in Shor's algorithm for elliptic curves has not been checked and is not claimed
by the paper** — the connection to `KN-TECH-037` is a unit-of-account observation by this
program, not a transferred result.
