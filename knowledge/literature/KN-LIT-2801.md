---
id: KN-LIT-2801
type: literature
title: "Breaking the decisional Diffie-Hellman problem for class group actions using genus theory"
authors:
  - "Wouter Castryck"
  - "Jana Sotáková"
  - "Frederik Vercauteren"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [class-group, dlp, elliptic-curve, endomorphism, isogeny, number-theory, pairing, pqc, prime-field, provable-security, quantum, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we use genus theory to analyze the hardness of the decisional Diffie–Hellman problem (DDH) for ideal class groups of imaginary quadratic orders, acting on sets of elliptic curves through isogenies; such actions are used in the Couveignes–Rostovtsev–Stolbunov protocol and in CSIDH. Concretely, genus theory equips every imaginary quadratic order O with a set of assigned characters χ : cl(O) → {±1}, and for each such character and every secret ideal class [a] connecting two public elliptic curves E and E 0 = [a] ?

## Key claims (as reported)
- E, we show how to compute χ([a]) given only E and E 0 , i.e. without knowledge of [a].
- In practice, this breaks DDH as soon as the class number is even, which is true for a density 1 subset of all imaginary quadratic orders.
- For instance, our attack works very efficiently for all supersingular elliptic curves over Fp with p ≡ 1 mod 4.
- Our method relies on computing Tate pairings and walking down isogeny volcanoes.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171224 (1).pdf`
- `downloads/12171224.pdf`
