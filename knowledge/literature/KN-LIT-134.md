---
id: KN-LIT-134
type: literature
title: 'Bootstrap Methods: Another Look at the Jackknife'
authors: [Efron Bradley]
year: 1979
venue: 'The Annals of Statistics, 7(1):1-26'
identifiers:
  eprint: null
  doi: 10.1214/aos/1176344552
  url: https://projecteuclid.org/journals/annals-of-statistics/volume-7/issue-1/Bootstrap-Methods-Another-Look-at-the-Jackknife/10.1214/aos/1176344552.full
tags: [bootstrap, resampling, confidence-interval, sampling-distribution, jackknife, statistics, methodology, uncertainty-quantification, extrapolation, cross-domain]
confidence: established
citation_verified: web
added: 2026-07-25
superseded_by: null
---

## Contribution
Introduces the **bootstrap**: a general method for estimating the sampling
distribution of a statistic from observed data, without assuming a parametric
form for the unknown underlying distribution. The jackknife is shown to be a
linear approximation to the bootstrap. This is the foundational paper for
essentially all resampling-based uncertainty quantification.

## Key claims (as reported)
- The problem addressed is estimating the sampling distribution of a
  prespecified random variable from data drawn from an unknown probability
  distribution.
- The bootstrap is a general method that is shown to work satisfactorily across
  a variety of estimation problems.
- The jackknife is a **linear approximation** to the bootstrap — which is why
  the bootstrap is generally more accurate for non-linear statistics.

## Relevance to this program
This program already uses the bootstrap and had no entry for it. `EXP-ICI-001`
reports a bootstrap 90% confidence interval on a fitted cost exponent, and the
program's flagship result `FINDING-PF-IC-001` rests on the interval
`[1.86, 2.29]` lying entirely above rho's 0.5. That interval is the load-bearing
quantity in the program's most consequential claim, and until now the corpus
contained nothing describing what a bootstrap interval is or when it is valid.

The applicability conditions matter here more than the method. A bootstrap
interval estimates sampling variability **under the distribution the data
actually came from**. It does not account for model misspecification, for
systematic error, or — critically for this program — for the possibility that
the fitted relation changes form outside the tested range. A bootstrap CI on an
exponent measured at `p <= 2^16` quantifies how much that exponent would wobble
under resampling at that scale. It says nothing about the exponent at
cryptographic scale, and reading it as though it did is the single most likely
way for this program to overclaim.

## Not verified here
Verification was by web search surfacing primary-index listings (Project Euclid
with DOI 10.1214/aos/1176344552, Annals of Statistics 7(1):1-26, plus Semantic
Scholar and multiple course-hosted PDF copies); direct fetches returned HTTP 403
under this session's egress policy. The paper is textbook-foundational and its
existence and content are not in doubt, which is why `confidence: established` is
recorded — but the paper itself was **not** read here, so the summary above
reflects an abstract returned by search.

NOT verified here: the paper's actual technical development, the conditions it
states for the bootstrap's validity, and its worked examples. The applicability
caveats in the section above are this program's own reasoning about its use case,
not claims extracted from Efron.
