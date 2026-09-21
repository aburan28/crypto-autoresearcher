---
id: KN-LIT-645
type: literature
title: "Succinct Garbling Schemes from Functional Encryption through a Local Simulation Paradigm?"
authors:
  - "Prabhanjan Ananth"
  - "Alex Lombardi"
year: 2018
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2018/759"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2018/759"
tags: [fhe, lattice, mpc, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study a simulation paradigm, referred to as local simulation, in garbling schemes. This paradigm captures simulation proof strategies in which the simulator consists of many local simulators that generate different blocks of the garbled circuit.

## Key claims (as reported)
- A useful property of such a simulation strategy is that only a few of these local simulators depend on the input, whereas the rest of the local simulators only depend on the circuit.
- We formalize this notion by defining locally simulatable garbling schemes.
- By suitably realizing this notion, we give a new construction of succinct garbling schemes for Turing machines assuming the polynomial hardness of compact functional encryption and standard assumptions (such as either CDH or LWE).
- Prior constructions of succinct garbling schemes either assumed sub-exponential hardness of compact functional encryption or were designed only for small-space Turing machines.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11239268 (1).pdf`
- `downloads/11239268.pdf`
