---
id: KN-LIT-092
type: literature
title: Differential Fault Attacks on Elliptic Curve Cryptosystems
authors: [Biehl Ingrid, Meyer Bernd, Mueller Volker]
year: 2000
venue: Advances in Cryptology - CRYPTO 2000, LNCS 1880, pp. 131-146
identifiers:
  eprint: null
  doi: 10.1007/3-540-44598-6_8
  url: https://iacr.org/archive/crypto2000/18800131/18800131.pdf
tags: [invalid-curve, fault-attack, point-validation, pseudo-addition, register-fault, smooth-order, crt, parameter-validation, ecdlp-adjacent, hygiene]
confidence: established
citation_verified: web
added: 2026-07-24
superseded_by: null
---

## Contribution
Introduces the invalid-curve idea. If a device performs scalar multiplication
using formulas that ignore the curve coefficient b (as the standard
pseudo-addition on x-coordinates does), then feeding it a point that lies on a
*different* curve E' -- one with smooth group order -- causes it to compute
d*P on E' instead. The output reveals d modulo the small factors of #E'(F_q),
and Chinese remaindering over several such curves recovers d. The paper frames
this as a differential fault attack and gives three variants, including one
that survives an input-validity check by injecting a register fault
immediately after the check.

## Key claims (as reported)
- Three attack types recovering information about the secret scalar when bit
  errors can be injected into elliptic-curve computations in a tamper-proof
  device; effectiveness demonstrated in software simulation.
- The attacks work for curves over arbitrary finite fields.
- The second variant defeats input-point validation alone, because the fault
  is injected after the test; defending requires also checking that the
  *output* lies on E.

## Relevance to this program
The elliptic analogue of KN-LIT-091, and the reason "check the point is on the
curve" is a two-sided obligation. For this program the value is twofold. As
scope: an attack requiring fault injection or chosen invalid inputs is outside
the plain-ECDLP model the program measures against, and a proposal relying on
it is not a mathematical advance on the ECDLP. As instrument hygiene: the
program's own harness computes on generated curves, and a formula that drops
the b coefficient will silently compute on the wrong curve if a coordinate is
mis-encoded -- exactly the failure mode this paper weaponizes. A "solve" that
is actually a solve on a smooth-order neighbour curve is an integrity failure,
which is precisely what the certificate re-verification in
docs/claims-and-verification.md is meant to catch. See KN-TECH-034.

## Not verified here
Full paper not fetched, though the IACR-hosted PDF is open; only its opening
sections and the DOI landing page were read. Authors, title, venue (CRYPTO
2000, LNCS 1880, pp. 131-146) and DOI confirmed against three independent
records. The three attack variants are described here from the abstract and
the DOI page's excerpt of Section 4; the simulation results were not examined.
