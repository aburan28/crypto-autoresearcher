---
id: KN-LIT-7568
type: literature
title: Hybrid hash function based on the DLP and SIS problems
authors: [Koshelev Dimitri, Sebe Francesc]
year: 2026
venue: 'Cryptology ePrint Archive, Paper 2026/1459'
identifiers:
  eprint: iacr:2026/1459
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/1459
tags: [hash-function, discrete-logarithm, sis, pedersen, ajtai, hybrid, double-provable-security, parameter-selection, elliptic-curve, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-26
superseded_by: null
---

## Contribution
A short note analysing in detail a folklore but little-documented **hybrid hash
function** whose collision resistance rests simultaneously on the discrete logarithm
problem and on the Short Integer Solution problem — a natural common generalization of
the classical Pedersen (DL-based) and Ajtai (SIS-based) hash functions. Concrete
parameters are given for 128-bit security of the lattice component with a 256-bit
module.

## Key claims (as reported)
- The construction is a natural generalization of Pedersen and Ajtai hashing; to the
  authors' knowledge its hybrid version has not previously been explicitly analysed.
- Specific parameters are supplied achieving the standard **128-bit security level for
  the lattice (SIS) component with a 256-bit module**; the authors note this parameter
  statement "may be useful in its own right".
- The value claimed is **double provable security**: the hash stands as long as
  *either* underlying problem remains hard.
- The authors expect significant further optimization by importing tricks from both
  elliptic-curve and lattice cryptography, and frame the work as introductory, with
  more hybrid schemes intended.
- The abstract contains an explicit editorial position — that curve-based cryptography
  has been "severely and unfairly undermined by the potential but still vague quantum
  threat" — which is the authors' opinion, not a technical claim.

## Relevance to this program
`adjacent`. The program studies whether the ECDLP is hard, not how to build on it, so
a hash construction is out of scope as a research target. Two reasons it is worth a
corpus slot:

- **It is a hedge whose security floor is the ECDLP.** If the program's `sqrt(p)`
  barrier findings hold, the DL half of this construction retains value even under
  partial lattice cryptanalysis; if a program experiment ever *did* move the ECDLP
  exponent, this is one of the constructions whose stated guarantee would degrade to
  the SIS half alone. Recording it makes that dependency greppable.
- **The parameter statement is a calibration datum.** A concretely stated
  "128-bit SIS security, 256-bit module" pairing sits alongside the calibration anchors
  the corpus already keeps (`KN-TECH-049`, lattice challenge records; `KN-TECH-036`,
  ECDLP record computations) — with the caveat below that it has not been checked.

Forecloses nothing; supplies no attack technique; bears on no open problem in the
corpus.

## Not verified here
Full paper not read; all claims relayed from the official ePrint abstract retrieved
from eprint.iacr.org on 2026-07-26 (hence `confidence: reported`). ePrint history:
received 2026-07-17, last of 2 revisions 2026-07-24. Self-described as a short
introductory note; not peer-reviewed as of this entry; no DOI.

NOT verified here: the security proof or its reduction structure, whether "double
provable security" holds in the strong sense (both problems must be broken) or only
under specific parameter coupling, the concrete SIS parameters and which estimator
produced them, the novelty claim (the authors themselves hedge with "to the authors'
knowledge"), and the claimed folklore status. The authors' framing of the quantum
threat is opinion and is **not** endorsed by this entry.
