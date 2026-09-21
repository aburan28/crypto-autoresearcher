---
id: KN-LIT-2970
type: literature
title: "Combined Attack on CRT-RSA"
authors:
  - "Why Public Verification Must Not Be Public"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, factoring, lattice, provable-security, quantum, rsa, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This article introduces a new Combined Attack on a CRTRSA implementation resistant against Side-Channel Analysis and Fault Injection attacks. Such implementations prevent the attacker from obtaining the signature when a fault has been induced during the computation.

## Key claims (as reported)
- Indeed, such a value would allow the attacker to recover the RSA private key by computing the gcd of the public modulus and the faulty signature.
- The principle of our attack is to inject a fault during the signature computation and to perform a Side-Channel Analysis targeting a sensitive value processed during the Fault Injection countermeasure execution.
- The resulting information is then used to factorize the public modulus, leading to the disclosure of the whole RSA private key.
- After presenting a detailed account of our attack, we explain how its complexity can be significantly reduced by using lattice reduction techniques.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/77780196 (1).pdf`
- `downloads/77780196 (2).pdf`
- `downloads/77780196 (3).pdf`
- `downloads/77780196 (4).pdf`
- `downloads/77780196.pdf`
