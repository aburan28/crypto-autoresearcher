---
id: KN-LIT-008
type: literature
title: Monte Carlo methods for index computation (mod p)
authors: [Pollard John M.]
year: 1978
venue: Mathematics of Computation, 32(143):918-924
identifiers:
  eprint: null
  doi: 10.2307/2006496
  url: https://www.ams.org/journals/mcom/1978-32-143/S0025-5718-1978-0491431-9/
tags: [pollard-rho, baseline, generic, discrete-logarithm, complexity]
confidence: established
citation_verified: web
added: 2026-07-19
superseded_by: null
---

## Contribution
Introduces the Pollard rho (and lambda/kangaroo) Monte Carlo methods for
discrete logarithms, using a pseudo-random walk and cycle detection to find a
collision in expected O(sqrt(n)) group operations and O(1) storage.

## Key claims (as reported)
- Expected ~sqrt(pi n / 2) group operations to solve a DLP in a group of order
  n; negligible memory.
- Generic: uses only the group operation, so it applies to any ECDLP instance.

## Relevance to this program
THE matched baseline. Every claimed improvement must be compared against the
rho reference under a common cost model (per docs/evidence-and-reproducibility
baseline discipline). Over prime fields it remains the best known attack
(KN-OPEN-001). Implemented in the harness as the control (KN-TECH-001).

## Not verified here
The sqrt-order constant is standard and reconstructible (hence
confidence: established); the exact wording of the original 1978 method
relayed, not re-read.
