---
id: KN-LIT-4290
type: literature
title: "How to manipulate curve standards: a white paper for the black hat"
authors:
  - "Daniel J. Bernstein"
  - "Tung Chou"
  - "Chitchanok Chuengsatiansup"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, hyperelliptic, protocol]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper analyzes the cost of breaking ECC under the following assumptions: (1) ECC is using a standardized elliptic curve that was actually chosen by an attacker; (2) the attacker is aware of a vulnerability in some curves that are not publicly known to be vulnerable. This cost includes the cost of exploiting the vulnerability, but also the initial cost of computing a curve suitable for sabotaging the standard.

## Key claims (as reported)
- This initial cost depends heavily upon the acceptability criteria used by the public to decide whether to allow a curve as a standard, and (in most cases) also upon the chance of a curve being vulnerable.
- This paper shows the importance of accurately modeling the actual acceptability criteria: i.e., figuring out what the public can be fooled into accepting.
- For example, this paper shows that plausible models of the “Brainpool acceptability criteria” allow the attacker to target a one-in-a-million vulnerability and that plausible models of the “Microsoft NUMS criteria” allow the attacker to target a one-in-a-hundred-thousand vulnerability.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/bada55-20150927.pdf`
