---
id: KN-LIT-7673
type: literature
title: "HAWK: Having Automorphisms Weakens Key"
authors:
  - "van Gent Daniël M. H."
  - "Pulles Ludo N."
year: 2025
venue: "IACR Communications in Cryptology, Vol. 2, No. 2, 12 pages"
identifiers:
  eprint: "iacr:2025/928"
  doi: "10.62056/a3qjp2w9p"
  arxiv: null
  url: "https://cic.iacr.org/p/2/2/20"
tags: [hawk, module-lip, lattice-isomorphism-problem, smlip, automorphism, galois-automorphism, cyclotomic, svp, bkz, root-hermite-factor, omsvp, signature, pqc, lattice, heuristic]
confidence: reported
citation_verified: read
added: "2026-08-02"
superseded_by: null
---

## Contribution
Shows that the search rank-2 module Lattice Isomorphism Problem (**smLIP**) over a
power-of-two cyclotomic ring reduces to an LIP instance of **at most half the rank**
when the adversary knows a **nontrivial automorphism** of the underlying integer
lattice — speeding up HAWK key recovery "at least quadratically, which would halve
the number of security bits."

The paper is also, and this is easy to miss from the title, **partly reassuring
about HAWK**: it argues that after the HAWK team amended `omSVP` in response to Luo
et al. (Asiacrypt 2024), there are "plausibly no more trivial automorphisms that
allow winning the omSVP game easily."

## Claim structure (read from the full text)
```
nontrivial Z-automorphism σ            ← INPUT, assumed available, not produced
   ↓  Proposition 2   PROVEN, polynomial time
sublattice Λ ⊂ rot(Q), rank ≤ n/2, λ1(Λ) ≤ √2
   ↓  Heuristic 1     HEURISTIC — "2016 estimates" BKZ success condition
BKZ-β recovers a shortest vector of Λ at β = k/2 + 1
   ↓
Theorem 1: solve smLIP for Q by BKZ-β with β = n/4 + 1   ⇒ "halves the security bits"
   ↓  §5 unnumbered   HEURISTIC — group-theoretic
random σ likely gives rank ≤ log(n) ⇒ "heuristically break HAWK with high probability"
```

**The paper contains exactly one numbered heuristic** (`Heuristic 1`) plus the
unnumbered group-theoretic argument of §5. Regex census over the full extraction:
`Heuristic 1` ×1, `Theorem 1`, `Proposition 2`, `Lemma 1`–`3`, `Conjecture` ×0.

`Heuristic 1` is a root-Hermite-factor success condition in the
Alkim–Ducas–Pöppelmann–Schwabe "2016 estimates" methodology, which the authors note
was "verified experimentally [AGVW17, DDGR20, PV21]".

## Two claim levels that must not be merged
- **"Halves the security parameter"** — rests on `Heuristic 1` alone, with no
  condition on the automorphism beyond nontriviality.
- **"Break HAWK with high probability"** — additionally rests on the **unnumbered**
  §5 argument that a uniformly random `σ ∈ O(rot(Q))` likely yields a lattice of
  rank `≤ log(n)`, where SVP is polynomial.

The authors state the first as their result and the second as what one may
"reasonably suspect". Any citation must say which it relies on.

## Relevance to this program
This is the **load-bearing prior** for `GOAL-HAWK-001` and for `RQ-HAWK-001`, which
names it explicitly as a source to read before ideation. Its descent step is reused
by [[KN-LIT-7592]] (the disclosed Straznickas–Weis attack), and — decisively — that
work **discharges this paper's heuristic**: by proving the relevant lattice exactly
near-hypercubic it admits Ducas's *provable* block reduction, which its authors
describe as upgrading "the endgame from the heuristic pricing of [GP25, Thm. 1] to
the unconditional accounting of Theorem 6.1."

So the current state of the HAWK line, as read in BATCH-001, is: **this paper's
Theorem 1 is the heuristic version of a result that now also exists
unconditionally.** That is a stronger position for the attack side than either
paper states alone, and it was not recorded anywhere in this corpus before
2026-08-02.

Connects to [[KN-LIT-7670]] (2026/1318, a *separate* four-heuristic attack via
nrd-PIP), [[KN-LIT-7648]] (definite/indefinite LIP, reports HAWK unaffected by that
route), [[KN-LIT-7671]] (SLIP ∈ AM ∩ coAM), and [[KN-OPEN-027]].

**Does not bear on the ECDLP.**

## Not verified here
**Full text read** (hence `citation_verified: read`), obtained 2026-08-02 from
`https://cic.iacr.org/p/2/2/20/pdf`,
PDF `sha256:56107a8a72a662b2475a70ffc2a02a4b5303a2ae4855af01627c9ef3b40baf50`.
Peer-reviewed journal article, not a preprint.

`confidence` remains `reported`: reading a paper is not reproducing it. **Nothing
here was re-derived.** NOT verified: Proposition 2's algorithm, Heuristic 1's
success condition, Theorem 1's assembly, the §5 group-theoretic argument, or the
`omSVP` reassurance.

**Formula-level caveat.** The transcription in
`coordination/goals/GOAL-HAWK-001/batches/BATCH-001/tasks/TASK-20260802-004/heuristics_transcription.md`
was produced by pdfminer.six over a two-column LaTeX PDF; **mathematical layout is
damaged** (flattened exponents, `(cid:NN)` glyphs, a visibly dropped clause in the
Theorem 1 hypothesis). Prose is faithful; **formulas are not, and are marked as
such**. No formula from that file may be used in an argument without checking the
typeset PDF.
