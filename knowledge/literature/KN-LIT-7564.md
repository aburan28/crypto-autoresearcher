---
id: KN-LIT-7564
type: literature
title: A Public-Key Cryptosystem Based On Algebraic Coding Theory
authors: [McEliece Robert J.]
year: 1978
venue: DSN Progress Report 42-44, Jet Propulsion Laboratory, Pasadena, pp. 114-116
identifiers:
  eprint: null
  doi: null
  url: null
tags: [code-based, mceliece, goppa, syndrome-decoding, pqc, foundational, trapdoor]
confidence: reported
citation_verified: web
added: 2026-07-27
superseded_by: null
---

## Contribution
The original code-based public-key cryptosystem. The public key is a generator
matrix of a binary Goppa code, scrambled by a secret invertible matrix and a
secret coordinate permutation; encryption adds a random error vector of weight
at most the code's correction capacity; decryption undoes the permutation and
runs the Goppa decoder. Security rests on two separate assumptions: that
decoding a random-looking linear code is hard (message security), and that the
scrambled generator matrix is indistinguishable from a random one (key
security).

## Key claims (as reported)
- A trapdoor one-way function can be built from an efficiently decodable code
  whose description is hidden by a scramble-and-permute transform.
- The construction predates and is unbroken by Shor's algorithm; it is the
  oldest surviving public-key proposal with no known quantum polynomial-time
  attack.
- Public keys are large -- the central practical drawback, unchanged in 48
  years (KN-LIT-7573).

## Relevance to this program
This is the root citation for the entire code-based branch and the anchor for
KN-TECH-058. Its two-assumption structure is the reason code-based cryptanalysis
splits cleanly into generic decoding attacks (KN-TECH-057) and structural
key-recovery attacks (KN-TECH-059) -- a split the program should preserve when
reasoning about any code-based claim, because breaking one assumption says
nothing about the other.

## Not verified here
Primary PDF not fetched. Author, title, venue (DSN Progress Report 42-44),
pages 114-116, and year confirmed via search against secondary bibliographic
records, not against a JPL primary index page. No claim in this entry was
independently checked.
