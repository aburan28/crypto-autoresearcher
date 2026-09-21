---
id: KN-LIT-1565
type: literature
title: "Babel: Jailbreaking Safety Attention via Obfuscation"
authors:
  - "Distribution Optimized Sampling"
year: 2026
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2605.17971"
  url: "https://arxiv.org/abs/2605.17971"
tags: [pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Despite rigorous safety alignment, Large Language Models (LLMs) remain vulnerable to jailbreak attacks. Existing black-box methods often rely on heuristic templates or exhaustive trials, lacking mechanistic interpretability and query efficiency.

## Key claims (as reported)
- In this study, we investigate an intrinsic vulnerability in the safety mechanisms of LLMs, where safety alignment relies on a small set of sparsely distributed attention heads, leaving much of the representational space weakly monitored.
- We formalize this phenomenon with a mathematical jailbreaking model that characterizes the delicate boundary of effective text obfuscation and analytically explains observed jailbreak behaviors.
- Guided by this model, we propose Babel, an efficient black-box attack framework that exploits the identified safety gap through systematic obfuscation sampling with iterative, feedback-driven distribution refinement, enabling reliable and high-success jailbreak attacks without access to model internals.
- Comprehensive evaluations on frontier commercial models demonstrate that Babel achieves state-of-the-art attack success rates and superior query efficiency.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2605.17971v1.pdf`
