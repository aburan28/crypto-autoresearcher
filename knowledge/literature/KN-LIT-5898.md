---
id: KN-LIT-5898
type: literature
title: "Privacy-Enhancing Auctions Using Rational Cryptography"
authors:
  - "Peter Bro Miltersen"
  - "Jesper Buus Nielsen"
  - "Nikos Triandopoulos"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, mpc, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider enhancing with privacy concerns a large class of auctions, which include sealed-bid single-item auctions but also general multi-item multi-winner auctions, our assumption being that bidders primarily care about monetary payoff and secondarily worry about exposing information about their type to other players and learning information about other players’ types, that is, bidders are greedy then paranoid. To treat privacy explicitly within the game theoretic context, we put forward a novel hybrid utility model that considers both monetary and privacy components in players’ payoffs.

## Key claims (as reported)
- We show how to use rational cryptography to approximately implement any given ex interim individually strictly rational equilibrium of such an auction without a trusted mediator through a cryptographic protocol that uses only point-to-point authenticated channels between the players.
- By “ex interim individually strictly rational” we mean that, given its type and before making its move, each player has a strictly positive expected utility.
- By “approximately implement” we mean that, under cryptographic assumptions, running the protocol is a computational Nash equilibrium with a payoff profile negligibly close to the original equilibrium.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/56770534 (1).pdf`
- `downloads/56770534 (2).pdf`
- `downloads/56770534 (3).pdf`
- `downloads/56770534.pdf`
