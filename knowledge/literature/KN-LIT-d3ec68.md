---
id: KN-LIT-d3ec68
type: literature
title: "Preimage Attacks on 3-Pass HAVAL and Step-Reduced MD5"
authors:
  - "Jean-Philippe Aumasson"
  - "Willi Meier"
  - "Florian Mendel"
year: 2008
venue: "IACR ePrint 2008/183"
identifiers:
  eprint: "iacr:2008/183"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2008/183"
tags: [cryptanalysis, hash, md5, haval, preimage, step-reduced]
confidence: reported
citation_verified: read
provenance_level: "abstract obtained and read"
added: "2026-08-20"
superseded_by: null
---

## Contribution
Preimage attacks on the compression functions of 3-pass HAVAL and
step-reduced MD5. This is the paper behind the RQ-MDFIVE-6870c1 provenance
title "Preimage Attacks on Step-Reduced MD5" — the RQ's title is a truncated
form of this paper's full title, and the attribution is corrected here against
the ePrint record.

## Key claims (as reported, from the ePrint abstract read 2026-08-20)
- Two preimage attacks on the 3-pass HAVAL compression function with
  complexity about 2^224 compression-function evaluations instead of 2^256.
- Several preimage attacks on the MD5 compression function that invert up to 47
  (out of 64) steps within 2^96 trials instead of 2^128.
- The authors state explicitly: "Though our attacks are not practical, they show
  that the security margin of 3-pass HAVAL and step-reduced MD5 with respect to
  preimage attacks is not as high as expected."

## Relevance to this program
This is the step-reduced MD5 preimage line, relevant to GOAL-MD5-001's
method-ceiling audit: it shows the preimage method breaking through on
step-reduced MD5 (up to 47 of 64 steps) while explicitly NOT reaching a
practical full-MD5 preimage. The authors' own "not practical" wording is a
useful data point for the flagged-error question in KN-LIT-582d77 (a different
paper, but the same frontier).

## Not verified here
Only the ePrint ABSTRACT was obtained and read (2026-08-20); the full text was
not read. The step counts and complexities are relayed from the abstract, not
independently reproduced. No figure here is asserted as a fact about MD5; it is
recorded as what the source CLAIMS, at the stated provenance level.
