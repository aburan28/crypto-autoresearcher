---
id: KN-LIT-7616
type: literature
title: "Can PCE solve the factorisation problem via optimisation?"
authors:
  - "Fernando Alonso"
  - "Colomán Samprón"
  - "Jacobo Veiga"
  - "Andrés Gómez"
year: 2026
venue: 'arXiv preprint arXiv:2607.23727 [quant-ph]'
identifiers:
  eprint: null
  doi: null
  arxiv: '2607.23727'
  url: https://arxiv.org/abs/2607.23727
tags: [pauli-correlation-encoding, factorization, binary-optimization, qubit-compression, quantum-annealing-style, preliminary, negative-result, cost-model, rsa, adjacent]
confidence: reported
citation_verified: web
added: "2026-07-29"
superseded_by: null
---

## Contribution
A **preliminary feasibility study** of adapting Pauli Correlation Encoding (PCE) to
integer factorisation recast as a binary optimisation problem. PCE's appeal is
compression: it is claimed to sharply reduce the qubit count relative to standard
optimisation-based factorisation encodings, which currently need qubit counts that put
them out of reach of available hardware.

The authors are explicit about what this is not. As reported, the work "aims to provide
a preliminary examination of the feasibility and limitations of the proposed
adaptation" and is expressly **not** offered as a replacement for established quantum
factorisation methods. The abstract reports algorithmic design, conceptual relationship
to existing approaches, and practical constraints — **no successful factorisation of a
cryptographically relevant integer is claimed.**

## Relevance to this program
Ingested as a **cost-model / cautionary** entry, and deliberately at low weight.

Three reasons it is worth a line in the corpus:

- **Factoring is not the ECDLP.** Optimisation-encoding results on integer
  factorisation do not transfer to elliptic-curve discrete logarithms: there is no
  known analogous binary-optimisation encoding of the ECDLP with comparable structure,
  and the group structure that makes factoring amenable to these encodings is absent.
  **Does not bear on the ECDLP.**
- Optimisation-based factorisation is a **recurring source of overclaimed results** in
  the quantum literature — the pattern is a small semiprime factored on hardware,
  reported in a way that implies a path to RSA. This paper is a useful counter-example
  in the corpus precisely because it does *not* do that.
- The qubit-compression question is the same question `KN-LIT-7600` raises about
  distributed-quantum resource estimates: whether a headline qubit count survives
  contact with the costs it omits. Here the authors themselves flag "practical
  constraints associated with implementation".

Pairs with `KN-TECH-037` (quantum ECDLP resource estimates) as a contrast case only —
that entry concerns Shor-style algorithms with proven asymptotics, this concerns a
heuristic optimisation encoding with none. **Nothing here revises `KN-TECH-037`.**

The honest summary: a preliminary, self-limiting study whose main value to this program
is as a well-behaved example of how to report an unfinished idea.

## Not verified here
Full paper not read; claims relayed from the arXiv abstract retrieved from the arXiv
API on 2026-07-29 (hence `confidence: reported`). arXiv metadata: submitted
2026-07-26, primary category quant-ph. Preprint — not peer-reviewed, no DOI or venue as
of this entry.

NOT verified here: the PCE adaptation; the claimed compression factor, which the
abstract does **not** quantify; whether any factorisation was actually performed, at
what size, and on what hardware or simulator. **The abstract reports no experimental
results, and this entry asserts none.** No scaling claim of any kind should cite this
entry.
