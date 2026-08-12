---
id: KN-LIT-4612
type: literature
title: "Known–Plaintext–Only Attack on RSA–CRT with Montgomery Multiplication"
authors:
  - "Martin Hlaváč"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, curve-arithmetic, factoring, lattice, provable-security, rsa, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The paper describes a new attack on RSA–CRT employing Montgomery exponentiation. Given the amount of so-called final subtractions during the exponentiation of a known message (not chosen, just known), it creates an instance of the well known Hidden Number Problem (HNP, [2]).

## Key claims (as reported)
- Solving the problem reveals the factorization of RSA modulus, i.e. breaks the scheme.
- The main advantage of the approach compared to other attacks [14, 17] is the lack of the chosen plaintext condition.
- The existing attacks, for instance, cannot harm so-called Active Authentication (AA) mechanism of the recently deployed electronic passports.
- Here, the challenge, i.e. the plaintext, is jointly chosen by both parties, the passport and the terminal, thus it can not be conveniently chosen by the attacker.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/57470127 (1).pdf`
- `downloads/57470127 (2).pdf`
- `downloads/57470127 (3).pdf`
- `downloads/57470127.pdf`
