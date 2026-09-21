---
id: KN-LIT-108
type: literature
title: Revisiting the Expected Cost of Solving uSVP and Applications to LWE
authors: [Albrecht Martin R., Gopfert Florian, Virdia Fernando, Wunderer Thomas]
year: 2017
venue: ASIACRYPT 2017 (ePrint 2017/815)
identifiers:
  eprint: iacr:2017/815
  doi: null
  url: https://eprint.iacr.org/2017/815
tags: [usvp, primal-attack, embedding, lwe, bkz, success-condition, security-estimate, experiments, lattice]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
Resolves a disagreement in the literature about *when the primal attack
succeeds*. Two incompatible success conditions were in circulation -- the
widely used one descending from Gama-Nguyen's 2008 work on predicting lattice
reduction, and the one used by Alkim et al. (KN-LIT-107) -- and they predicted
significantly different costs for published LWE parameter sets. The paper
settles the question empirically and revises affected security estimates.

## Key claims (as reported)
- Lattice-reduction experiments exhibit behaviour "in line with the latter
  estimate," i.e. the Alkim et al. condition, not the older widely-used one.
- In some situations reduction behaves *somewhat better* than the Alkim et al.
  work predicts; the paper explains this under standard assumptions.
- The security estimates of some LWE-based constructions from the literature
  need revision, and refined expected solving costs are given.

## Relevance to this program
This is the paper that makes the primal attack a *measurable* rather than
folkloric procedure, and it is the reference for the success condition used in
KN-TECH-038. It is also directly instructive about method: two plausible
predictors coexisted in the literature for years, gave materially different
security numbers, and were separated by running experiments rather than by
argument. That is exactly the program's own preferred move -- find the cheapest
decisive gate and run it -- applied in the lattice setting, and it is worth
noting that the resolution *raised* attack cost estimates for some schemes
rather than lowering them.

## Not verified here
The ePrint abstract was fetched and read. The experiments were not reproduced,
the refined cost formulas are not restated here, and which specific
constructions required revision was not extracted from the full text.
