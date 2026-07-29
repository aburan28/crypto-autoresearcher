---
id: KN-LIT-7614
type: literature
title: "Extremal Chowla sets and their linear analogues: A human-AI mathematical investigation using Co-Scientist"
authors:
  - "Mohsen Aliabadi"
  - "Keith Driscoll"
  - "Elliot Krop"
  - "Petar Sirkovic"
  - "Everett Sullivan"
  - "Elahe Vedadi"
year: 2026
venue: 'arXiv preprint arXiv:2607.24847 [math.NT]'
identifiers:
  eprint: null
  doi: null
  arxiv: '2607.24847'
  url: https://arxiv.org/abs/2607.24847
tags: [human-ai-collaboration, co-scientist, agentic-mathematics, methodology, extremal-invariant, finite-groups, field-extensions, normal-basis, research-protocol, adjacent]
confidence: reported
citation_verified: web
added: "2026-07-29"
superseded_by: null
---

## Contribution
Introduces an extremal invariant `C(G)` for **Chowla sets** in a finite group `G` — a
nonempty subset `S` where every element has order greater than `|S|` — and develops a
linear analogue for finite field extensions.

Results as reported: `C(G)` is determined by the distribution of element orders; an
exact divisor formula for cyclic groups with a characterization of when
`C(Z/nZ) = φ(n)`; `liminf C(Z/nZ)/φ(n) = 1` while `limsup C(Z/nZ)/φ(n) = ∞`; an
explicit formula for finite abelian groups via the invariant-factor decomposition; and
for finite separable `L/K`, the exact formula `C(L/K) = [L:K] − d_max(L/K)`, with a
direct normal-basis proof in every degree for finite fields.

The paper states it was developed through **expert-guided human–AI collaboration** using
Google's Co-Scientist.

## Relevance to this program
Ingested as a **methodology** entry. The mathematics is not relevant to the ECDLP —
Chowla sets are an extremal combinatorics/order-distribution question with no bearing
on discrete logarithms, and nothing here touches elliptic curves. **Does not bear on
the ECDLP.**

What earns it a place is that it is a **third independent data point** on
agent-assisted mathematical discovery, alongside the Anthropic cluster ingested last
gather ([[KN-LIT-7594]], [[KN-LIT-7595]]) and `CryptanalysisBench` ([[KN-LIT-7588]]).
Those record an industrial lab's account of its own system; this is an outside academic
group, a different vendor's system, and — importantly — a **published paper with named
mathematician co-authors who retain authorship**, not a capability announcement.

Two specifics worth tracking against `KN-TECH-056` (the object-first invention
protocol):

- The framing is **expert-guided**, and the human authors are domain mathematicians.
  This is the assisted-discovery regime the harness actually operates in, not
  autonomous discovery.
- The output is a **conventional theorem set with exact formulas and proofs**, not a
  heuristic or an unverifiable claim. The results are of a kind that referees can
  check, which is the disposition `docs/claims-and-verification.md` demands.

The honest read is that this is a modest, checkable contribution rather than an
exponent-moving one — which is itself the useful signal, since the surrounding
discourse tends to sample only the headline successes. No harness change is proposed
here and `KN-TECH-056` is unchanged.

## Not verified here
Full paper not read; claims relayed from the arXiv abstract retrieved from the arXiv
API on 2026-07-29 (hence `confidence: reported`). arXiv metadata: submitted
2026-07-25, primary category math.NT. Preprint — not peer-reviewed, no DOI or venue as
of this entry.

NOT verified here: any of the stated formulas or limit results; the normal-basis
construction; and — specifically — **what Co-Scientist actually contributed versus
what the human authors contributed.** The abstract asserts collaboration but does not
apportion it, and this entry makes no claim about the division of labour. The
methodology section must be read before any harness conclusion cites this.
