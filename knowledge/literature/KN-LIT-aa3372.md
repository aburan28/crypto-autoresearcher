---
id: KN-LIT-aa3372
type: literature
title: "A complete quantum circuit to solve the information set decoding problem"
authors:
  - "Simone Perriello"
  - "Alessandro Barenghi"
  - "Gerardo Pelosi"
year: 2021
venue: "IEEE International Conference on Quantum Computing and Engineering (QCE)"
identifiers:
  eprint: null
  doi: "10.1109/qce52317.2021.00056"
  arxiv: null
  url: "https://re.public.polimi.it/bitstream/11311/1201187/4/main.pdf"
tags: [isd, syndrome-decoding, code-based, mceliece, concrete-security, quantum, quantum-circuit, resource-estimation]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
A **complete** quantum circuit for the information set decoding problem —
complete in the sense that every step, including the Gaussian elimination that
ISD spends most of its time on, is realised in the circuit rather than assumed
as an oracle.

## Key claims (as reported)
- A full quantum circuit solving ISD, with no step left as an abstract oracle.
- Completeness is the paper's stated contribution.

## Relevance to this program
The base of the three-paper progression by these authors, and the clearest
statement of why it matters: **an oracle-level quantum speedup is not a cost
estimate.** Replacing the oracle with a circuit is what converts an
unfalsifiable claim into a countable one.

This is the code-side statement of a discipline this program applies generally
(`docs/claims-and-verification.md`): a claimed cost must be re-verifiable from
declared artifacts, not asserted at a level of abstraction where it cannot be
checked.

**Does not bear on the ECDLP.**

## Not verified here
citation verified against the Crossref record (DOI 10.1109/qce52317.2021.00056).

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Circuit size, depth, and qubit count are NOT recorded here. The Politecnico di
Milano PDF link from the bibliography was not fetched.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
