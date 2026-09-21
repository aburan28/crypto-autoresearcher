---
id: KN-LIT-4979
type: literature
title: "Multi-Client Non-Interactive Verifiable Computation Seung Geol Choi1?"
authors:
  - "Ranjit Kumaresan"
  - "Carlos Cid"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
(Crypto 2010) introduced the notion of noninteractive verifiable computation, which allows a computationally weak client to outsource the computation of a function f on a series of inputs x(1) , . . . to a more powerful but untrusted server. Following a preprocessing phase (that is carried out only once), the client sends some representation of its current input x(i) to the server; the server returns an answer that allows the client to recover the correct result f (x(i) ), accompanied by a proof of correctness that ensures the client does not accept an incorrect result.

## Key claims (as reported)
- The crucial property is that the work done by the client in preparing its input and verifying the server’s proof is less than the time required for the client to compute f on its own.
- We extend this notion to the multi-client setting, where n computationally weak clients wish to outsource to an untrusted server the compu(1) (1) tation of a function f over a series of joint inputs (x1 , . . . , xn ), . . . without interacting with each other.
- We present a construction for this setting by combining the scheme of Gennaro et al. with a primitive called proxy oblivious transfer.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/77850497 (1).pdf`
- `downloads/77850497 (2).pdf`
- `downloads/77850497 (3).pdf`
- `downloads/77850497.pdf`
