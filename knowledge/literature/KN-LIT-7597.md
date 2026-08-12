---
id: KN-LIT-7597
type: literature
title: "Decision trees, Frobenius traces, and Weierstrass coefficients of elliptic curves"
authors:
  - "Barinder S. Banwait"
  - "Xiaoyu Huang"
  - "Kyu-Hwan Lee"
  - "Seewoo Lee"
  - "Thomas Oliver"
  - "Alexey Pozdnyakov"
year: 2026
venue: 'arXiv preprint arXiv:2607.24251 [math.NT, cs.LG]'
identifiers:
  eprint: null
  doi: null
  arxiv: '2607.24251'
  url: https://arxiv.org/abs/2607.24251
tags: [elliptic-curve, frobenius-trace, weierstrass-coefficients, isogeny-class, conductor, machine-learning, decision-tree, ml-to-theorem, murmurations, methodology]
confidence: reported
citation_verified: web
added: "2026-07-28"
superseded_by: null
---

## Contribution
Uses decision-tree models to discover, and then **proves**, explicit formulae recovering
the first three reduced minimal Weierstrass coefficients of an elliptic curve over `Q`
from a very small amount of Frobenius data.

## Key claims (as reported)
- Decision trees recover the **first two** reduced minimal Weierstrass coefficients with
  perfect accuracy from the Frobenius traces at `p = 2` and `p = 3` alone.
- The **third** coefficient is recovered by supplementing those two traces with the
  conductor parity.
- Explicit formulae for all three are then proved from the traces and conductor parity;
  the authors state these formulae "appear to be new."
- Corollary: the first three reduced minimal Weierstrass coefficients are **determined by
  the isogeny class**.

## Relevance to this program
Two reasons, one methodological and one substantive — and the substantive one is weak, so
it is stated narrowly.

**Methodological, and the stronger reason.** This is a clean instance of the loop this
harness is built around: a statistical model over curve data surfaces an exact pattern,
and the pattern is then converted into a proved statement rather than reported as an
empirical finding. The discipline worth noting is that the machine-learning step is used
as a *discovery* device and appears nowhere in the final claim — the theorem stands on its
own proof. That is the correct relationship between a screen and a result under
`AGENTS.md` rule 4, and it is the same shape as the LLM-discovery results recorded in
[[KN-LIT-7593]] and [[KN-LIT-7595]], at much smaller scale and with the advantage that the
end product is provable outright.

**Substantive, and deliberately understated.** Isogeny-class invariance of curve data is
adjacent to the program's interest in what Frobenius/trace data determines about a curve.
But this is over `Q` with minimal models and conductors — an arithmetic-geometry setting —
not over `F_p` where the ECDLP lives, and it recovers *coefficients of a curve*, not
anything about the discrete logarithm on it. **There is no route from this to the ECDLP
and none is claimed.** It is recorded because the corpus is thin on the ML-to-theorem
pipeline for elliptic curves and this is a compact, verifiable example of it.

## Not verified here
Full paper not read; all claims relayed from the official arXiv abstract retrieved from
the arXiv API on 2026-07-28 (hence `confidence: reported`). arXiv metadata: submitted
2026-07-27, primary category math.NT, cross-listed cs.LG. Preprint — not peer-reviewed,
no DOI or venue as of this entry.

NOT verified here: the perfect-accuracy decision-tree results, the explicit formulae and
their proofs, the novelty claim for those formulae, and the isogeny-class corollary.
