---
id: KN-LIT-107
type: literature
title: Post-quantum key exchange - a new hope
authors: [Alkim Erdem, Ducas Leo, Poppelmann Thomas, Schwabe Peter]
year: 2016
venue: USENIX Security 2016 (ePrint 2015/1092)
identifiers:
  eprint: iacr:2015/1092
  doi: null
  url: https://eprint.iacr.org/2015/1092
tags: [newhope, core-svp, cost-model, primal-attack, dual-attack, usvp, ring-lwe, bkz, block-size, parameter-selection, quantum-sieve, lattice, baseline]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
A Ring-LWE key exchange with new parameters, a better error distribution, a new
reconciliation mechanism, and a defense against backdoored public parameters.
For cryptanalytic purposes its lasting contribution is Section 6: the
**core-SVP hardness methodology**, which became the default convention for
stating lattice parameter security in the NIST post-quantum process.

## Key claims (as reported)
- **Core-SVP convention.** BKZ calls an SVP oracle in block dimension b a
  polynomial number of times; the paper deliberately ignores that polynomial
  factor and charges only *one* oracle call, which it states plainly is a
  pessimistic estimate from the defender's point of view.
- **Oracle cost.** Sieving cost `2^(0.292b)` classically, `2^(0.265b)` with
  Grover-type quantum speedup, and a "best plausible" floor of `2^(0.2075b)`
  derived from the kissing-number list size (KN-LIT-104). The sub-exponential
  hidden factor is stated to be much greater than one in practice, adding
  further pessimistic margin.
- **Primal attack.** Build the lattice `{x in Z^(m+n+1) : (A | -I_m | -b)x = 0
  mod q}` of dimension `d = m+n+1` and volume `q^m`, with unique-SVP solution
  `v = (s, e, 1)` of norm `~ sigma*sqrt(n+m)`; the required block size follows
  from a success condition modelled with the GSA, which the paper says is
  optimistic from the attacker's point of view. The number of samples m is
  numerically optimised.
- **Dual attack.** Find a short vector in the dual lattice; a vector of length
  `l` gives advantage `eps = 4 exp(-2 pi^2 tau^2)` with `tau = sigma*l/q`
  against decision-LWE. The paper notes a preliminary version contained a bogus
  formula for eps that under-estimated dual-attack cost.
- Enumeration is argued irrelevant above dimension 250, since it is
  superexponential while the sieve bounds are single-exponential.

## Relevance to this program
Core-SVP is the cost convention almost every lattice security claim is quoted
in, so the program cannot read or write such a claim without it. Two properties
matter. It is deliberately conservative in the defender's favour -- charging one
oracle call and ignoring polynomial factors -- so a "break" stated in core-SVP
units is not a break in wall-clock terms. And it is a *convention*, not a
measurement: comparing two numbers computed under different conventions
(core-SVP versus `8d` oracle calls versus RAM-model gate counts, as MATZOV uses
in KN-LIT-110) is the lattice version of the baseline mis-charge the program
guards against on the ECDLP side (KN-TECH-030).

## Not verified here
The ePrint abstract and the USENIX camera-ready PDF's Sections 6.1-6.4 were
fetched and read; the quoted exponents, the primal lattice construction, the
dual advantage formula, and the enumeration argument are read directly from
that text. The security estimation script was not run, and none of the derived
bit-security figures in the paper's Table 1 were reproduced.
