---
id: KN-LIT-2550
type: literature
title: "Anonymous Permutation Routing"
authors:
  - "Paul Bunn⋆"
  - "Eyal Kushilevitz⋆⋆"
  - "Rafail Ostrovsky"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Non-Interactive Anonymous Router (NIAR) model was introduced by Shi and Wu [SW21] as an alternative to conventional solutions to the anonymous routing problem, in which a set of senders wish to send messages to a set of receivers. In contrast to most known approaches to support anonymous routing (e.g. mix-nets, DC-nets, etc.), which rely on a network of routers communicating with users via interactive protocols, the NIAR model assumes a single router and is inherently non-interactive (after an initial setup phase).

## Key claims (as reported)
- In addition to being noninteractive, the NIAR model is compelling due to the security it provides: instead of relying on the honesty of some subset of the routers, the NIAR model requires anonymity even if the router (as well as an arbitrary subset of senders/receivers) is corrupted by an honest-but-curious adversary.
- In this paper, we present a protocol for the NIAR model that improves upon the results from [SW21] in two ways: – Improved computational efficiency (quadratic to near linear): Our protocol matches the communication complexity of [SW21] for each sender/receiver, while reducing the computational overhead for the router to polylog overhead instead of linear overhead. – Relaxation of assumptions: Security of the protocol in [SW21] relies on the Decisional Linear assumption in bilinear groups; while security for our protocol follows from the existence of any rate-1 oblivious transfer (OT) protocol (instantiations of which are known to exist under the DDH, QR and LWE assumptions [DGI+ 19,GHO20]).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14369017 (1).pdf`
- `downloads/14369017.pdf`
