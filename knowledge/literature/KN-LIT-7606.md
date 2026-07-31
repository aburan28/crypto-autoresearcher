---
id: KN-LIT-7606
type: literature
title: "The Structured Generic-Group Model"
authors:
  - "Corrigan-Gibbs, Henry"
  - "Henzinger, Alexandra"
  - "Wu, David J."
year: 2026
venue: "IACR Cryptology ePrint Archive (also in Springer LNCS proceedings)"
identifiers:
  eprint: "iacr:2026/384"
  doi: "10.1007/978-3-032-25330-9_4"
  arxiv: null
  url: "https://eprint.iacr.org/2026/384"
tags: [generic-group-model, lower-bound, simulability, index-calculus, discrete-logarithm, dlp, ecdlp, elliptic-curve, smooth-integers, preprocessing, prior-art]
confidence: reported
citation_verified: web
added: "2026-07-29"
superseded_by: null
---

## Contribution

Extends Shoup's generic-group model (Eurocrypt 1997) to capture algorithms
that exploit **some** non-generic structure of the group, rather than treating
the group as a featureless oracle. This is the modern framework for the
question "does this extra structure buy an attacker anything beyond the
generic bound?"

## Key claims (as reported)

- Any discrete-log algorithm in a group of prime order `q` that exploits the
  structure of at most a `δ` fraction of group elements must run in time
  `Ω(min{√q, 1/δ})`.
- A tight **subexponential-time** lower bound is proved against discrete-log
  algorithms that exploit the multiplicative structure of smooth integers but
  are otherwise generic. The authors state this applies to a broad class of
  index-calculus algorithms.
- Similar lower bounds are stated against algorithms exploiting the structure
  of smooth polynomials and of **elliptic-curve points**.

## Relevance to this program

**Direct prior art for KN-FIND-002.** That finding builds an ad-hoc
simulability test and classifies four augmented ECDLP oracles (jet,
endomorphism, elliptic-net, incidence) as generically simulable, concluding
the candidate families are "closed at exponent 1/2". This paper is the same
project carried out as a general model with proven quantitative lower bounds,
and it already covers elliptic-curve point structure.

It also supplies the correct scoping discipline. A plain-GGM simulability
argument cannot close a candidate for real elliptic curves: index calculus
over small-degree extension fields (KN-LIT-022, KN-LIT-002/003) is a genuine
non-generic algorithm, which is precisely why this model exists. The
`δ`-fraction parameter is what makes "how non-generic is this attack" a
quantity rather than a binary.

The constructive follow-up for this program is to re-express the four oracle
classifications inside this model and check whether any survives with a
non-trivial `δ`.

## Not verified here

- Full text was not read; the fetched PDF did not yield extractable text.
  Claims above come from search-result summaries and the abstract.
- Whether the paper's elliptic-curve-point result covers the *specific*
  augmented oracles in KN-FIND-002 (dual-number/jet data, elliptic nets,
  incidence structure) was **not** determined. This is the check that decides
  whether KN-FIND-002 has any residue, and it requires reading the body.
- Exact venue and page numbers not recorded.
