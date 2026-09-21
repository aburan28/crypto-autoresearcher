---
id: KN-LIT-097
type: literature
title: Faster elliptic-curve discrete logarithms on FPGAs
authors: [Bernstein Daniel J., Engels Susanne, Lange Tanja, Niederhagen Ruben, Paar Christof, Schwabe Peter, Zimmermann Ralf]
year: 2016
venue: Cryptology ePrint Archive, Report 2016/382
identifiers:
  eprint: iacr:2016/382
  doi: null
  url: https://eprint.iacr.org/2016/382
tags: [record-computation, binary-field, sect113r2, negation-map, fruitless-cycles, pollard-rho, distinguished-points, fpga, cost-model, baseline, calibration, ecdlp]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
The current largest publicly completed ECDLP computation. The paper presents
an FPGA architecture roughly 3/2 more area-efficient per high-speed rho core
than prior designs (3 cores on a low-cost Spartan-6 XC6SLX150), uses it to
break the SECG standard curve sect113r2, and then to solve a 117.35-bit
discrete logarithm on a curve "target117" over F_2^127.

## Key claims (as reported)
- 117.35-bit ECDL on target117 over F_2^127 completed: about 2^60 iteration
  steps, conducted over more than six months using up to 576 FPGAs at peak.
  The authors call it "the largest publicly conducted ECDLP computation" and a
  new size record, with prime order more than 40 times larger than the previous
  record holder.
- sect113r2 (a 112-bit DLP) solved in about 48.1 days on up to 120 Spartan-6
  FPGAs with an earlier 2-core 100MHz design, requiring 82,177,699
  distinguished points against an expectation of ~59,473,682
  (= sqrt(pi * 2^112 / 4) / 2^30, distinguished points being x-coordinates with
  top 30 bits zero) -- i.e. the run took about 1.38x its expected work.
- Engineering ingredients: negation map, simultaneous inversion, and explicit
  handling of the fruitless-cycle problem the negation map introduces.
- The paper contextualizes cost against large-scale attackers, estimating a
  budget under 2 * 10^9 USD as comparable to one existing data center, and
  notes that batch techniques make subsequent keys cheaper.

## Relevance to this program
The definitive answer to "how big an ECDLP has anyone actually solved?" -- and
the answer is 117.35 bits, on a *binary* curve, with a negation-map speedup, in
six months on hundreds of FPGAs. Read alongside KN-LIT-095 (112 bits, prime
field) this bounds the program's realistic operating range and makes the
crypto-size threshold concrete: a 256-bit curve needs about 2^128 iterations
against this record's 2^60, a gap of roughly 2^68, so no claimed mechanism can be
validated end-to-end at crypto size within any plausible budget. That is
exactly why GOAL-CRYPTO-001 requires a certificate-verified *advantage over a
matched baseline*, extrapolated with a charged cost model, rather than a
solve. This entry also documents the sampling variance to expect: a single run
finishing at 1.38x its expected work is normal, so an observed speedup of that
order on one instance is not evidence of a mechanism.

## Not verified here
Two author-hosted PDF versions (2016-04-14 and 2016-12-12) were fetched and
the abstracts, the results section, and the cost discussion were read
directly; the numbers quoted above come from those texts. The FPGA
architecture, multiplier design, and power measurements were not checked. The
earlier version describes the 117.35-bit computation as in progress and the
later one as completed -- the completed claim above is taken from the
2016-12-12 revision. Title, author list, and ePrint 2016/382 confirmed against
the IACR record; note the title varies across versions between "Faster
discrete logarithms on FPGAs" and "Faster elliptic-curve discrete logarithms
on FPGAs". No journal version was located.
