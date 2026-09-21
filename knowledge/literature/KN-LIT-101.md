---
id: KN-LIT-101
type: literature
title: 'BKZ 2.0: Better Lattice Security Estimates'
authors: [Chen Yuanmi, Nguyen Phong Q.]
year: 2011
venue: ASIACRYPT 2011, LNCS 7073, Springer, pages 1-20
identifiers:
  eprint: null
  doi: 10.1007/978-3-642-25385-0_1
  url: https://www.iacr.org/archive/asiacrypt2011/70730001/70730001.pdf
tags: [bkz, bkz-2.0, simulator, block-size, pruning, lattice-reduction, security-estimate, enumeration, heuristic, lattice, baseline]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
The first state-of-the-art implementation of BKZ incorporating Gama-Nguyen-Regev
pruning (KN-LIT-102), plus -- the part that matters most for cryptanalytic
practice -- a **simulation algorithm** that predicts the output quality and
running time of BKZ at high block size without running it. Before this paper,
lattice security estimates were extrapolated from NTL's old BKZ; after it,
estimates are produced by simulating the basis profile.

## Key claims (as reported)
- Incorporating GNR pruning significantly decreases enumeration subroutine time
  without degrading output quality at appropriate parameters, allowing much
  larger block sizes than NTL's BKZ; the authors report the first extensive
  experiments with block size >= 40.
- The proposed simulator models BKZ behaviour for block size >= 50 and predicts
  approximately both output quality and running time (heuristic, validated
  experimentally in the paper's range, not proven).
- Concrete consequence reported: the smallest NTRUSign parameter set, claimed to
  offer at least 93-bit security against key-recovery lattice attacks, actually
  offers at most 65-bit security under their revised estimate.

## Relevance to this program
This is the source of the standard costing pipeline the program must use if it
ever states a lattice attack cost: choose a block size, simulate the resulting
basis profile, check an attack success condition against that profile, and
price the SVP oracle calls. It also supplies the cautionary datum that a
28-bit security overestimate survived in the literature purely because
estimates were extrapolated from an outdated implementation -- an argument for
the program's rule that a cost model is an artifact to be pinned and cited, not
an assumption. Contrast with the core-SVP convention (KN-LIT-107), which
deliberately ignores the oracle-call count that this simulator estimates.

## Not verified here
The complete published abstract and the IACR-archived PDF's introduction were
read; the simulator itself was not run or re-implemented, and the NTRUSign
re-estimate was not reproduced. The claim that the simulator is accurate
outside the experimentally tested range is not made by the paper and is not
assumed here.
