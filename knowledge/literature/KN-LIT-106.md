---
id: KN-LIT-106
type: literature
title: The General Sieve Kernel and New Records in Lattice Reduction
authors: [Albrecht Martin R., Ducas Leo, Herold Gottfried, Kirshanova Elena, Postlethwaite Eamonn W., Stevens Marc]
year: 2019
venue: EUROCRYPT 2019 (ePrint 2019/089)
identifiers:
  eprint: iacr:2019/089
  doi: null
  url: https://eprint.iacr.org/2019/089
tags: [g6k, sieving, lattice-reduction, svp-challenge, lwe-challenge, records, implementation, bkz, enumeration-crossover, lattice, calibration]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
Defines G6K, an abstract stateful machine whose instruction set expresses a wide
range of sieving-based reduction strategies, and provides an optimised
open-source multi-threaded implementation. Its significance is twofold: it
stops treating a sieve as a black-box SVP oracle inside BKZ, and it produced
the public lattice records that calibrate what is actually computable.

## Key claims (as reported)
- The abstract machine expresses previous sieving strategies concisely and
  supports new ones, including a light BKZ variant that uses strong reduction as
  preprocessing for sieving rather than calling the sieve as an oracle.
- New techniques: recycling vectors between sieves, on-the-fly lifting, and
  flexible insertions in the style of Deep LLL and Random Sampling Reduction.
- **Records reported:** previously unsolved Darmstadt SVP challenges in
  dimensions 151, 153, and 155, and Darmstadt LWE challenge instances including
  (n, alpha) = (75, 0.005). The SVP-151 solution was found 400 times faster than
  the reported time for the previous SVP-150 record.
- **Crossover reported:** for exact SVP, G6K overtakes FPLLL's state-of-the-art
  enumeration at dimension 70.

## Relevance to this program
This is the lattice analogue of the ECDLP record computations (KN-TECH-036,
KN-LIT-095 to KN-LIT-097): the public, independently checkable ceiling on what
lattice reduction can actually do. Any internal claim about lattice attack
feasibility must be positioned against these numbers, and a claim that implies
a dimension far above the published records without an argument for the gap is
extraordinary. The dimension-70 enumeration/sieving crossover is the single
most useful calibration constant here, because it dates the moment the
asymptotically-better algorithm actually became better.

## Not verified here
The ePrint abstract was fetched and read. The records were not independently
re-verified against the Darmstadt hall of fame at the time of writing, the
implementation was not run, and the 400x speedup and dimension-70 crossover are
the authors' reported measurements on their own hardware.
