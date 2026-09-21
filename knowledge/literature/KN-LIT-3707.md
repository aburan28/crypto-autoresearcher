---
id: KN-LIT-3707
type: literature
title: "Error Correction in The Bounded Storage Model"
authors:
  - "Yan Zong Ding"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We initiate a study of Maurer’s bounded storage model (JoC, 1992) in presence of transmission errors and perhaps other types of errors that cause different parties to have inconsistent views of the public random source. Such errors seem inevitable in any implementation of the model.

## Key claims (as reported)
- All previous schemes and protocols in the model assume a perfectly consistent view of the public source from all parties, and do not function correctly in presence of errors, while the private-key encryption scheme of Aumann, Ding and Rabin (IEEE IT, 2002) can be extended to tolerate only a O(1/ log (1/ε)) fraction of errors, where ε is an upper bound on the advantage of an adversary.
- In this paper, we provide a general paradigm for constructing secure and error-resilient private-key cryptosystems in the bounded storage model that tolerate a constant fraction of errors, and attain the near optimal parameters achieved by Vadhan’s construction (JoC, 2004) in the errorless case.
- In particular, we show that any local fuzzy extractor yields a secure and error-resilient cryptosystem in the model, in analogy to the result of Lu (JoC, 2004) that any local strong extractor yields a secure cryptosystem in the errorless case, and construct efficient local fuzzy extractors by extending Vadhan’s sample-then-extract paradigm.
- The main ingredients of our constructions are averaging samplers (Bellare and Rompel, FOCS ’94), randomness extractors (Nisan and Zuckerman, JCSS, 1996), error correcting codes, and fuzzy extractors (Dodis, Reyzin and Smith, EUROCRYPT ’04).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/3378_576 (1).pdf`
- `downloads/3378_576 (2).pdf`
- `downloads/3378_576 (3).pdf`
- `downloads/3378_576.pdf`
