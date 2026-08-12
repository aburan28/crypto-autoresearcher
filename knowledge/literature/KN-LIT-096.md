---
id: KN-LIT-096
type: literature
title: Breaking ECC2K-130
authors: [Bailey Daniel V., Batina Lejla, Bernstein Daniel J., Birkner Peter, Bos Joppe W., Chen Hsieh-Chung, Cheng Chen-Mou, van Damme Gauthier, de Meulenaer Giacomo, Dominguez Perez Luis Julian, Fan Junfeng, Gueneysu Tim, Gurkaynak Frank, Kleinjung Thorsten, Lange Tanja, Mentens Nele, Niederhagen Ruben, Paar Christof, Regazzoni Francesco, Schwabe Peter, Uhsadel Leif, Van Herrewege Anthony, Yang Bo-Yin]
year: 2009
venue: Cryptology ePrint Archive, Report 2009/541
identifiers:
  eprint: iacr:2009/541
  doi: null
  url: https://eprint.iacr.org/2009/541
tags: [certicom-challenge, ecc2k-130, record-computation, binary-field, koblitz-curve, pollard-rho, distinguished-points, automorphism, fpga, gpu, asic, baseline, calibration, ecdlp]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
The attack design and multi-platform implementation for the Certicom ECC2K-130
challenge: a 131-bit Koblitz curve y^2 + xy = x^3 + 1 over
F_2^131 = F_2[z]/(z^131 + z^13 + z^2 + z + 1), whose group has order 4*l with
l a 129-bit prime. The paper covers the choice and analysis of the rho
iteration function (exploiting the Frobenius automorphism), the finite-field
representation, and implementations on CPUs, Cell processors, GPUs, FPGAs,
with ASIC estimates.

## Key claims (as reported)
- Estimated total work 2^60.9 iterations, corresponding to about 2^35.63
  distinguished points at the chosen granularity (average 2^25.27 iterations
  per distinguished point).
- Per-platform throughput is tabulated, e.g. ~54.03 million iterations/second
  on a GTX 295 card and ~33.67 million on a Spartan-3 XC3S5000 FPGA, with the
  count of each platform needed to finish in one year (1263 GPUs, 2026 FPGAs);
  an estimated 90nm ASIC would need about 85 units.
- The relevant context, stated in the paper: all Certicom challenges over
  109-bit fields were solved between April 2000 and April 2004; the 131-bit
  challenges were open.
- Speedups combine van Oorschot-Wiener parallelization (KN-LIT-012),
  Wiener-Zuccherato negation, and Gallant-Lambert-Vanstone automorphism
  classes (KN-TECH-018).

## Relevance to this program
Supplies the cost anatomy of a real large ECDLP attempt, which the corpus
otherwise lacked: not an asymptotic count but a full budget in
iterations, distinguished points, hardware units, and calendar time. Two uses
here. (1) It shows what the "fully charged" baseline looks like in practice --
the automorphism speedup is a constant-factor sqrt(m) gain on a Koblitz curve
and is claimed *before* the attack starts, so a proposed mechanism competing
with rho on a structured curve must beat the sped-up baseline, not the plain
one. (2) It is the binary-field, structured-curve counterpart to the
prime-field record in KN-LIT-095, and the contrast matters: this program's
target is ordinary prime-field curves, where none of these automorphism
speedups apply.

## Not verified here
The ePrint PDF was fetched and the introduction, iteration-function
discussion, and platform tables were read; the project's public status page
(ecc-challenge.info) supplied the per-platform throughput figures quoted
above. The implementation details and the ASIC estimates were not checked, and
no figure was reproduced. Author list, title, and the ePrint number 2009/541
were confirmed against the IACR record and its BibTeX. The paper is a status /
design report on an ongoing computation, not a completion announcement:
treat 2^60.9 as the authors' estimate of required work, not as a measured
total. Whether and when ECC2K-130 was ultimately solved was not established
here.
