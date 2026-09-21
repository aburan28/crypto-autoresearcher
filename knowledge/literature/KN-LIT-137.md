---
id: KN-LIT-137
type: literature
title: Training Compute-Optimal Large Language Models
authors: [Hoffmann Jordan, Borgeaud Sebastian]
year: 2022
venue: 'Advances in Neural Information Processing Systems 35 (NeurIPS 2022); arXiv:2203.15556'
identifiers:
  eprint: null
  doi: null
  url: https://arxiv.org/abs/2203.15556
tags: [scaling-law, extrapolation, power-law, empirical-fit, model-selection, experimental-design, methodology, cautionary-case, cross-domain, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-25
superseded_by: null
---

## Contribution
Recorded here as a **methodological cautionary case, not as cryptography**. A
widely believed empirical scaling law — fitted from a set of smaller-scale
training runs and extrapolated to predict behaviour at much larger scale — was
found to give the wrong prescription, and was corrected by a larger and better
designed sweep. The correction was not a refutation of power-law scaling; it was
a change in which quantities were varied and how the fit was set up.

## Key claims (as reported)
- Over **400 models** were trained, spanning roughly 70M to 16B+ parameters and
  5B to 500B training tokens, to fit the scaling relation empirically.
- The finding is that for compute-optimal training, model size and training-token
  count should be scaled **equally**: doubling model size requires doubling
  tokens.
- Prior large models were consequently "significantly undertrained," a
  consequence of scaling model size while holding data roughly constant.
- The prediction was then **tested by construction**: a compute-matched model
  (Chinchilla, 70B parameters, 4x more data) was trained and reported to
  outperform substantially larger models including one of 280B and one of 530B
  parameters.
- The work is presented as a correction/refinement to the earlier Kaplan et al.
  (2020) scaling relation, specifically on how compute should be allocated.

## Relevance to this program
The program's central epistemic risk, stated in `AGENTS.md` rules 6-7 and in the
claim-tier ceiling, is that an exponent measured on small instances is read as
governing large ones. This is the best-documented modern instance of exactly that
failure and of its repair, and the repair is instructive in three ways that
transfer directly:

1. **The earlier law was not wrong about the functional form.** It was wrong
   about which variable was being held fixed. A power-law fit can be excellent
   in-sample and still give the wrong extrapolation because the experimental
   design confounded two quantities. The program's toy-scale sweeps vary field
   size, factor-base size, and `m` together in places, and this is the shape of
   error that produces.
2. **The fix was a much larger and more systematic sweep**, not a cleverer fit to
   the same data. Where the program's exponent CIs rest on narrow parameter
   ranges, widening the range is worth more than tightening the interval.
3. **The prediction was falsified constructively** — by building the case the law
   predicted and checking it. That is the analogue of the program's own
   pre-registered decisive gates, and the strongest form its evidence can take.

Read alongside `KN-LIT-111` (the dual-sieve attack falsified at the level of its
heuristic rather than its code), which is the same lesson inside cryptanalysis.

## Not verified here
Verification was by web search surfacing primary-index listings (arXiv 2203.15556,
NeurIPS 2022 proceedings PDF, ACM DL record, Semantic Scholar); direct fetches
returned HTTP 403 under this session's egress policy. **The author list is
incomplete**: this paper has many authors and only the first two were confirmed,
so the `authors` field is partial and must be completed before the entry is
cited bibliographically. No DOI was confirmed.

NOT verified here: the fitted coefficients, the three estimation approaches used,
the evaluation results, and the precise nature of the disagreement with Kaplan et
al. (2020), which is **not itself in this corpus**. The three transferable
lessons above are this program's reading of the case, not claims made by the
paper. This entry is deliberately marked `cross-domain` and `adjacent`: it makes
no claim about any cryptographic problem and must never be cited in support of
one.
