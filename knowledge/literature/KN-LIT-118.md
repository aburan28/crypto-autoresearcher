---
id: KN-LIT-118
type: literature
title: 'LWE with Side Information: Attacks and Concrete Security Estimation'
authors: [Dachman-Soled Dana, Ducas Leo, Gong Huijing, Rossi Melissa]
year: 2020
venue: CRYPTO 2020 (ePrint 2020/292)
identifiers:
  eprint: iacr:2020/292
  doi: null
  url: https://eprint.iacr.org/2020/292
tags: [hints, side-information, side-channel, primal-attack, lattice-reduction, decryption-failure, ntru, frodo, security-estimate, toolkit, lattice]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
A framework and toolkit for integrating "hints" -- partial information about the
LWE secret or error -- into the primal lattice attack, together with a way to
predict the resulting attack cost. It converts side-channel leakage from a
qualitative concern into a quantity measured in lost bits of security.

## Key claims (as reported)
- Generalises the primal lattice attack to allow progressive integration of
  hints before the final lattice reduction. Integration techniques include
  sparsifying the lattice, projecting onto or intersecting with hyperplanes, and
  altering the distribution of the secret vector.
- The framework covers more than side channels: it also applies to exploiting
  decryption failures and to constraints imposed by scheme design, with LAC,
  Round5 and NTRU named.
- A Sage 9.0 toolkit both mounts such attacks when computationally feasible and
  predicts performance on larger instances.
- Reported application: improves a single-trace attack on Frodo due to Bos et
  al. The framework is claimed to estimate security loss even from very little
  side information, giving a smooth measurement/computation trade-off.

## Relevance to this program
The methodological bridge between the program's ECDLP leakage work and its
lattice interest. On the ECDLP side, partial nonce leakage is handled by the
hidden number problem and lattice reduction (KN-TECH-019, KN-OPEN-011); here
the same idea is turned inward -- lattice reduction consuming hints about a
lattice secret. Both are instances of the program's recurring theme that
auxiliary information changes the complexity driver (KN-OPEN-015). Practically,
this is also the right tool for the *defensive* side of the repository's ML-KEM
line: a soft-oracle leakage budget is only meaningful if leakage can be priced,
and this framework is how the literature prices it.

## Not verified here
The ePrint abstract was fetched and read. The hint-integration techniques were
not re-derived, the toolkit was not run, and the Frodo improvement was not
reproduced. The paper has been revised several times; claims here reflect the
abstract of the version fetched on this entry's date.
