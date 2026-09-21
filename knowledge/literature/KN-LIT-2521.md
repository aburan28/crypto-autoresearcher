---
id: KN-LIT-2521
type: literature
title: "Analysis of QUAD Bo-Yin Yang1 , Owen Chia-Hsin Chen2"
authors:
  - "Daniel J. Bernstein"
  - "Jiun-Ming Chen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In a Eurocrypt 2006 article entitled “QUAD: A Practical Stream Cipher with Provable Security,” Berbain, Gilbert, and Patarin introduced QUAD, a parametrized family of stream ciphers. The article stated that “the security of the novel stream cipher is provably reducible to the intractability of the MQ problem”; this reduction deduces the infeasibility of attacks on QUAD from the hypothesized infeasibility (with an extra looseness factor) of attacks on the well-known hard problem of solving systems of multivariate quadratic equations over finite fields.

## Key claims (as reported)
- The QUAD talk at Eurocrypt 2006 reported speeds for QUAD instances with 160bit state and output block over the fields GF(2), GF(16), and GF(256).
- This paper discusses both theoretical and practical aspects of attacking QUAD and of attacking the underlying hard problem.
- For example, this paper shows how to use XL-Wiedemann to break the GF(256) instance QUAD(256, 20, 20) in approximately 266 Opteron cycles, and to break the underlying hard problem in approximately 245 cycles.
- For each of the QUAD parameters presented at Eurocrypt 2006, this analysis shows the implications and limitations of the security proofs, pointing out which QUAD instances are not secure, and which ones will never be proven secure.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/45930292 (1).pdf`
- `downloads/45930292 (2).pdf`
- `downloads/45930292 (3).pdf`
- `downloads/45930292.pdf`
- `downloads/antiquad-20070817.pdf`
