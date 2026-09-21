---
id: KN-LIT-1568
type: literature
title: "Be Kind, Rewrite: Benign Projections via"
authors:
  - "John T. Halloran∗"
  - "Noopur S. Bhatt"
year: 2026
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2605.19147"
  url: "https://arxiv.org/abs/2605.19147"
tags: [pairing, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Large language models (LLMs) are highly susceptible to backdoor attacks (BAs), wherein training samples are poisoned using trigger-based harmful content. Furthermore, existing defenses have proven ineffective when extensively tested across BA patterns.

## Key claims (as reported)
- To better combat BAs, we explore the use of LLM rewriting as a proactive defense against data poisoning.
- First, we theoretically show that when LLM rewriting utilizes open-book benign samples—termed open-book benign rewriting (OBBR)—the probability of a rewritten output being benign is strictly greater than that of closed-book rewriting.
- Thus, OBBR neutralizes harmful content by projecting training samples to the space of benign prompts.
- We then show that, in contrast to previous defenses, OBBR effectively mitigates a large number of existing BAs: across five known BAs and four widely used LLMs, OBBR increases safety performance by an average 51% compared to state-of-the-art BA defenses and 25.7% compared to closed-book rewriting methods.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2605.19147v1.pdf`
