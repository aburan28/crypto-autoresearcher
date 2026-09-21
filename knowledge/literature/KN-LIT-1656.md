---
id: KN-LIT-1656
type: literature
title: "Finding Missing Input Validation in TEEs via LLM-Assisted"
authors:
  - "Symbolic Execution"
year: 2026
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: "10.1145/3793655.3793740"
  arxiv: "2605.22058"
  url: "https://arxiv.org/abs/2605.22058"
tags: [lattice, mov-fr]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Syntax Tree (AST) analysis to extract TEE code slices that may lack sufficient input validation, and then employs an LLM (GPT-5 in our case) to automatically convert the extracted slices into KLEE-compatible harness programs containing lightweight mock execution environments for symbolic analysis. Evaluations on 26 vulnerabilities (11 real-world and 15 synthetic) show that SymTEE achieves 100% precision and 92.3% recall in detecting missing input validation vulnerabilities while incurring an average analysis cost of only $0.05.

## Key claims (as reported)
- These results demonstrate the effectiveness and practicality of SymTEE’s pioneering paradigm of LLM-assisted symbolic execution, where LLMs autonomously generate mock environments to enable automated security analysis without complex setup, providing a more accessible and scalable framework for trusted computing systems.
- ACM Reference Format: Chengyan Ma, Jieke Shi, Ruidong Han, Ye Liu, Yuqing Niu, and David Lo.
- Finding Missing Input Validation in TEEs via LLM-Assisted Symbolic Execution.
- In 2026 IEEE/ACM Third International Conference on AI Foundation Models and Software Engineering (FORGE ’26), April 12–13, 2026, Rio de Janeiro, Brazil.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2605.22058v1.pdf`
