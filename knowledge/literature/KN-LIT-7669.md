---
id: KN-LIT-7669
type: literature
title: "Solving SIS in any norm via Gaussian sampling"
authors:
  - "Maiara F. Bollauf"
  - "Amaury Pouly"
  - "Yixin Shen"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/225"
identifiers:
  eprint: "iacr:2026/225"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/225"
tags: [sis, discrete-gaussian, gaussian-sampling, q-ary-lattice, mcmc, dilithium, provable, lp-norm, concrete-security, cost-model, lattice]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
A **simple, provably correct** algorithm solving the **SIS problem in any norm** when
the norm bound `ℓ` is smaller than half the modulus `q`.

The algorithm is deliberately plain: run a **discrete Gaussian sampler** on the SIS
`q`-ary lattice to obtain many lattice vectors, and estimate the probability that one is
non-zero and lands in a radius-`ℓ` ball in the given norm.

The technical work is the estimate. The authors improve prior analysis of random `q`-ary
lattices by obtaining **tight bounds on the expected value and variance of the Gaussian
mass** of both the whole lattice and an `ℓ_p`-norm ball, for **any `p ∈ (0, ∞]`** —
requiring new results on the discrete Gaussian distribution and on the ratio of two
Gaussian mass functions on `Z`.

Instantiated with an **MCMC-based** discrete Gaussian sampler, the complexity can be
estimated precisely.

## Key claims (as reported)
- Provably correct for any norm, under `ℓ < q/2`.
- Tight expectation and variance bounds on Gaussian mass, all `p ∈ (0, ∞]`.
- **At least 50 bits faster** than Ducas–Engelberts–Loyer (Crypto 2025) at all security
  levels.
- **"Our algorithm does not break Dilithium"** — the authors say so explicitly.

## Relevance to this program
Held for the **provability**, which is rare in this corner and directly relevant to how
this program is required to state results.

Almost every concrete lattice cost figure the sweep turned up is heuristic: it rests on
sieve models, independence assumptions, or an explicit conjecture
([[KN-LIT-7661]], [[KN-LIT-7664]], [[KN-LIT-7668]]). This paper does the opposite —
it takes a **simpler, weaker** algorithm and proves its behaviour outright, paying for
the rigour with a restricted regime (`ℓ < q/2`). Under
`docs/claims-and-verification.md` that is the higher claim tier, and the 50-bit margin
over a Crypto 2025 result is the striking part: **the provable algorithm is reported
faster than the heuristic state of the art**, not slower.

The `any p ∈ (0, ∞]` generality is the second reusable piece. As [[KN-LIT-7668]] shows
from the attack side, `ℓ₂` analyses do not transfer to `ℓ_∞` for free, and `ℓ_∞` is where
Dilithium-type schemes live. A norm-agnostic Gaussian-mass analysis is the kind of tool
that removes a whole class of "not analysed in this norm" caveats.

The authors' explicit **"does not break Dilithium"** is worth noting as the disclosure
norm this program's own evidence records are held to: state the negative scope in the
abstract, not in a footnote.

**Does not bear on the ECDLP.**

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/225,
retrieved 2026-08-01 (hence `confidence: reported`). Citation checked against the
ePrint record: title, three authors, report number, year 2026.

NOT verified here: the algorithm or its correctness proof; the Gaussian-mass bounds or
the new discrete-Gaussian technical results; the MCMC instantiation; the **50-bit
margin over Ducas–Engelberts–Loyer (Crypto 2025)** or the cost model it is measured in;
and the attribution itself, which is relayed and is not an entry in this corpus. The
`ℓ < q/2` restriction is the paper's stated regime and this entry makes **no claim
outside it**.
