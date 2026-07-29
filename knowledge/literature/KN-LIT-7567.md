---
id: KN-LIT-7567
type: literature
title: On the Impossibility of Round-Optimal Pairing-Free Blind Signatures in the ROM
authors: [Dietz Marian, Kastner Julia, Tessaro Stefano]
year: 2026
venue: 'Cryptology ePrint Archive, Paper 2026/090'
identifiers:
  eprint: iacr:2026/090
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/090
tags: [blind-signature, impossibility, lower-bound, generic-group-model, maurer-ggm, random-oracle-model, pairing-free, round-complexity, barrier, discrete-logarithm, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-26
superseded_by: null
---

## Contribution
Provides the first negative evidence that the three-move barrier for pairing-free
blind signatures is inherent: in a model combining the Random Oracle Model with
**Maurer's Generic Group Model**, no blind signature scheme can be secure if it signs
sufficiently long messages while making at most a logarithmic number of random-oracle
queries. The stated technical novelty is handling the interaction of the two idealized
models simultaneously.

## Key claims (as reported)
- All known pairing-free blind signature constructions need at least **three moves**,
  treat the group as a black box, and rely on the random oracle; they also require the
  signer to keep per-session state.
- Round-optimal solutions are known from other assumptions and structures (RSA,
  lattices, pairings) or via non-black-box generic transformations such as Fischlin's.
- **Impossibility result:** in ROM + Maurer GGM combined, no blind signature scheme is
  secure that signs sufficiently long messages while making at most `O(log)` random
  oracle queries.
- The lower-bound technique is claimed novel specifically for addressing generic
  groups and random oracles *at the same time*.

## Relevance to this program
`adjacent` on subject matter (blind signatures, not the ECDLP) but **directly relevant
as barrier methodology**, which is what this program spends most of its effort on.

`KN-TECH-005` (generic group model and the square-root discrete-log lower bound)
records the GGM as the program's foundational barrier instrument, and `KN-OPEN-005`
asks whether a non-generic ECDLP representation can escape GGM simulability. The
program's own barrier catalogue is largely built from arguments of the form "any
algorithm treating the group generically cannot do better than X". This paper is a
current, non-trivial example of extending that machinery to a **composite** idealized
model — GGM *and* ROM together — where the interaction between the two oracles is the
hard part rather than either alone.

That composite-model technique is the transferable item. Several of the program's
candidate mechanisms are not purely group-generic: they mix generic group operations
with a hash/sampling oracle or a structured representation. Barriers proved in the
plain GGM do not automatically cover such hybrids, and this paper is evidence that the
extension is provable but requires new argument, not a corollary.

Forecloses nothing about ECDLP hardness and provides no algorithm. It is recorded as a
technique reference for barrier construction, not as a hardness result.

## Not verified here
Full paper not read; all claims relayed from the official ePrint abstract retrieved
from eprint.iacr.org on 2026-07-26 (hence `confidence: reported`). ePrint history:
received 2026-01-20, last of 2 revisions 2026-07-21 — this is a **revision surfaced in
the 2026-07-19..26 window**, not a first posting. No DOI on the ePrint page; peer-review
status not established.

NOT verified here: the proof, the exact quantitative meaning of "sufficiently long
messages" and the `O(log)` random-oracle-query restriction (both are the substance of
how much the impossibility actually rules out), whether the restriction leaves a
practical escape route, and the priority claim ("first negative evidence"). Maurer's
GGM formulation differs from Shoup's in ways that matter for what the result covers;
that distinction was not checked against `KN-TECH-005` / `KN-LIT-011`.
