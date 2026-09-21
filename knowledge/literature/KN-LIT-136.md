---
id: KN-LIT-136
type: literature
title: 'Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing'
authors: [Benjamini Yoav, Hochberg Yosef]
year: 1995
venue: 'Journal of the Royal Statistical Society, Series B (Methodological), 57(1):289-300'
identifiers:
  eprint: null
  doi: 10.1111/j.2517-6161.1995.tb02031.x
  url: https://academic.oup.com/jrsssb/article/57/1/289/7035855
tags: [multiple-comparison, false-discovery-rate, familywise-error-rate, hypothesis-test, screening, statistics, methodology, experimental-design, cross-domain]
confidence: established
citation_verified: web
added: 2026-07-25
superseded_by: null
---

## Contribution
Introduces the **false discovery rate** (FDR) — the expected proportion of
falsely rejected hypotheses — as an alternative error criterion to the familywise
error rate (FWER) when many hypotheses are tested at once, together with a
practical procedure controlling it. The FDR equals the FWER when all null
hypotheses are true and is smaller otherwise, so controlling it yields more power
than FWER control in exactly the regime where some effects are real.

## Key claims (as reported)
- The conventional approach to multiplicity controls the familywise error rate;
  the paper identifies faults in that approach.
- The proposed criterion is the expected proportion of falsely rejected
  hypotheses — the false discovery rate.
- FDR is **equivalent to FWER when all hypotheses are true**, and smaller
  otherwise — which is why FDR control is more powerful without being reckless.

## Relevance to this program
This program is a multiple-testing machine and has no entry acknowledging it.
Twenty-six area codes, thirty-four experiments, and a screening campaign that ran
twelve batches of candidate mechanisms: the structural situation is a large
number of tested levers of which most are expected to be null, which is the exact
regime the FDR was designed for. Fourteen hypotheses currently sit at
`rejected_scoped`.

The relevance runs in **both** directions, and the second is the one that matters
here:

- Screening many mechanisms and reporting the ones that looked promising, each
  judged at its own threshold, inflates the rate of false positives. Any future
  positive result selected from a wide screen needs a multiplicity argument.
- Symmetrically — and this is the program's actual exposure — a *negative* result
  chosen from many measured comparisons is subject to the same selection effects.
  The program's output is dominated by scoped negatives, so the discipline it
  needs is not only "don't over-report a winner" but "state how many comparisons
  the reported one was drawn from."

The program partly protects itself already by freezing protocols before execution
and pre-declaring gates, which is the strongest available defence. This entry
supplies the vocabulary for stating that defence rather than relying on it
implicitly.

## Not verified here
Verification was by web search surfacing primary-index listings (JRSS-B
57(1):289-300, 1995, DOI 10.1111/j.2517-6161.1995.tb02031.x, corroborated across
Oxford Academic, Wiley, and a Tel Aviv University record); direct fetches
returned HTTP 403 under this session's egress policy. The abstract quoted above
was returned by search. `confidence: established` reflects the result's textbook
status, not a reading of the paper here.

NOT verified here: the Benjamini-Hochberg procedure's exact statement, its
independence and positive-dependence conditions, and its proofs. The application
to this program's screening structure is this program's own reasoning, not a
claim from the paper.
