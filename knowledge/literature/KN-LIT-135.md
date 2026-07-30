---
id: KN-LIT-135
type: literature
title: Power-Law Distributions in Empirical Data
authors: [Clauset Aaron, Shalizi Cosma Rohilla, Newman Mark E J]
year: 2009
venue: 'SIAM Review, 51(4):661-703'
identifiers:
  eprint: null
  doi: null
  url: https://aaronclauset.github.io/powerlaws/
tags: [power-law, scaling-exponent, maximum-likelihood, goodness-of-fit, likelihood-ratio, model-selection, log-log-fit, statistics, methodology, extrapolation, cross-domain]
confidence: reported
citation_verified: web
added: 2026-07-25
superseded_by: null
---

## Contribution
A methodological paper on how to fit and — more importantly — how to **test**
power-law hypotheses in empirical data. It supplies maximum-likelihood
estimators for the discrete and continuous cases, a goodness-of-fit based method
for estimating the lower cutoff above which the power law is claimed to hold,
and likelihood-ratio tests for comparing the power law against alternative
distributions. It is the standard reference for the position that a power law
must be tested, not eyeballed.

## Key claims (as reported)
- Power-law distributions occur across many domains (earthquake intensities,
  city populations, war sizes) and identifying them accurately has consequences
  for understanding the underlying systems.
- Fitting should use **maximum likelihood**, for both discrete and continuous
  cases, rather than the widespread practice of least-squares on a log-log plot.
- The **lower cutoff** `x_min` is itself a parameter to be estimated, via a
  goodness-of-fit criterion; a power law is typically claimed only in a tail.
- Candidate power laws must be compared against alternative distributions by
  **likelihood-ratio tests** — showing that a power law fits is not evidence that
  it fits better than a competing form.

## Relevance to this program
The corpus's first entry on how to establish a scaling claim, against a program
in which roughly twenty of twenty-six threads turn on one. `EXP-ICI-001` fits
`cost ~ l^alpha`, `EXP-DREG-001` must decide whether a degree-of-regularity curve
departs from a semi-regular null, `research/dreg-linear-law/` asserts a linear
law, and `FINDING-PF-IC-001` quotes a total-cost exponent as its central result.

Three transferable disciplines, in descending order of importance for this
program:

1. **A straight-looking log-log plot is not evidence.** Least-squares on
   log-transformed data gives biased exponent estimates and no test.
2. **Fitting is not testing.** The relevant question is never "does a power law
   fit?" but "does it fit better than the alternatives I should have considered?"
   — which is a likelihood-ratio comparison against named competitors.
3. **The range of validity is part of the claim.** Estimating `x_min` is the
   distributional analogue of stating the parameter regime in which a measured
   cost exponent holds — precisely the scoping the program's claim-tier rules
   require.

## Not verified here
Verification was by web search surfacing primary-index listings (SIAM Review
51(4):661-703, 2009, corroborated across several independent citation records,
plus the authors' project page and a course-hosted PDF); direct fetches returned
HTTP 403 under this session's egress policy. **The DOI was not confirmed and is
recorded as null**; the URL given is the authors' project page rather than the
publisher's.

An important scope caveat, which is this program's reasoning and not a claim from
the paper: this paper is about power-law **distributions** — the tail of a random
variable — whereas the program mostly fits power-law **relations** (cost as a
function of problem size). The estimators do not transfer directly. What
transfers is the methodological standard: estimate properly, test against
alternatives, and state the range. Anyone applying this entry to a program cost
fit must not import the MLE machinery as though the settings were the same.
