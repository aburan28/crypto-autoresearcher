---
id: KN-LIT-3548
type: literature
title: "Efficient Covert Two-Party Computation"
authors:
  - "Stanislaw Jarecki"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Covert computation strengthens secure computation by hiding not only participants’ inputs (up to what the protocol outputs reveal), but also the fact of computation taking place (up to the same constraint). Existing maliciously-secure covert computation protocols are orders of magnitude more costly than non-covert secure computation, and they are either non-constant round [5] or they use non-black-box simulation [10].

## Key claims (as reported)
- Moreover, constant-round covert computation with black-box simulation is impossible in the plain model [10].
- We show that constant-round Covert Two-Party Computation (2PC) of general functions secure against malicious adversaries is possible with black-box simulation under DDH in the Common Reference String (CRS) model, where the impossibility result of [10] does not apply.
- Moreover, our protocol, a covert variant of a “cut-and-choose over garbled circuits” approach to constant-round 2PC, is in the same efficiency ballpark as standard, i.e. non-covert, 2PC protocols of this type.
- In addition, the proposed protocol is covert under concurrent self-composition.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10770268 (1).pdf`
- `downloads/10770268 (2).pdf`
- `downloads/10770268 (3).pdf`
- `downloads/10770268 (4).pdf`
- `downloads/10770268.pdf`
