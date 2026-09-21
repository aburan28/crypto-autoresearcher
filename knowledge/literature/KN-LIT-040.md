---
id: KN-LIT-040
type: literature
title: Hamiltonian Systems and Transformation in Hilbert Space
authors: [Koopman Bernard O.]
year: 1931
venue: Proceedings of the National Academy of Sciences (PNAS), 17(5):315-318
identifiers:
  eprint: null
  doi: 10.1073/pnas.17.5.315
  url: https://www.pnas.org/doi/10.1073/pnas.17.5.315
tags: [koopman, transfer-operator, spectral, unitary, ergodic, walk, dlog-channel]
confidence: established
citation_verified: web
added: 2026-07-22
superseded_by: null
---

## Contribution
Introduces the linear operator (now the *Koopman operator*) acting on
observables/functions by composition with a dynamical map. For a measure-
preserving map it is a UNITARY operator on L^2, lifting nonlinear dynamics to a
linear (infinite-dimensional) operator whose spectrum encodes ergodic
properties. It is the adjoint/dual of the transfer (Perron-Frobenius) operator.

## Key claims (as reported)
- Measure-preserving dynamics -> unitary Koopman operator -> spectrum on the unit
  circle (pure point for nice group actions, with characters as eigenfunctions).
- Spectral machinery for transfer operators: Baladi, "Positive Transfer Operators
  and Decay of Correlations," World Scientific ASND 16, 2000
  (doi:10.1142/9789812813633) -- spectral gap vs essential spectrum controls
  mixing; a worked group-action instance: Mayer-Muhlenbruch-Stromberg, DCDS-A
  32(7):2453-2484, 2012 (doi:10.3934/dcds.2012.32.2453); modern Koopman spectral
  decomposition: Mezic, Nonlinear Dynamics 41(1-3):309-325, 2005
  (doi:10.1007/s11071-005-2824-x).

## Relevance to this program
The operator whose spectrum the program's transfer-operator candidate would
estimate (RQ-TRA-001, EXP-TRA-001, KN-TECH-017, KN-OPEN-010): coarse-grain the
translation-by-P walk on E(F_p) into a Markov operator and read its leading
spectrum. The unitarity here is exactly the expected BARRIER: a translation gives
a unitary Koopman operator with characters as eigenfunctions -- and the character
phases *are* the logarithm data -- so coarse-graining kills the phase and no
spectral gap is available (character orthogonality). The candidate is expected to
deliver a barrier theorem plus measurements.

## Not verified here
Note not read; the Koopman-operator/unitarity content is textbook-level in
ergodic theory (hence confidence: established). Fields (incl. Baladi, Mayer et
al., Mezic) confirmed against PNAS / publisher DOI records via search (title is
"Transformation," singular), not by fetching the primary pages.
