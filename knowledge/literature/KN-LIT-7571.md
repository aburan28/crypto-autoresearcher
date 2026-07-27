---
id: KN-LIT-7571
type: literature
title: Decoding Linear Codes with High Error Rate and its Impact for LPN Security
authors: [Both Leif, May Alexander]
year: 2018
venue: PQCrypto 2018, LNCS 10786, Springer, pp. 25-46
identifiers:
  eprint: iacr:2017/1139
  doi: 10.1007/978-3-319-79063-3_2
  url: https://eprint.iacr.org/2017/1139
tags: [code-based, information-set-decoding, isd, nearest-neighbor, lpn, cryptanalysis, exponent]
confidence: reported
citation_verified: web
added: 2026-07-27
superseded_by: null
---

## Contribution
Improves generic decoding in the high-error-rate regime by combining
representation-technique ISD with nearest-neighbour search, and draws out the
consequences for LPN parameter security. Reported as the leading published
asymptotic exponent for decoding random binary linear codes prior to subsequent
refinements.

## Key claims (as reported)
- Half-distance decoding exponent reduced to c ~ 0.047 (runtime 2^{cn}),
  against Prange's ~0.058 and BJMM's 0.05 (KN-LIT-3367).
- The high-error-rate regime, not the half-distance regime, is what governs LPN
  security, so the improvement bites hardest on LPN-based constructions rather
  than on McEliece-type KEMs.

## Relevance to this program
The current end of the exponent curve tabulated in KN-TECH-057, and the direct
motivation for KN-OPEN-019 (why the exponent has moved so little). The
regime-dependence claim matters for scoping: an ISD improvement stated at one
error rate does not automatically transfer to another, so any code-based cost
claim in this program must name its regime -- the same scoping discipline the
program applies to curve family and parameter range on the ECDLP side.

## Not verified here
Primary paper not fetched. Authors, title, venue (PQCrypto 2018, LNCS 10786),
pages, year, DOI, and ePrint number 2017/1139 confirmed via search against
Springer and the IACR ePrint listing. The ~0.047 exponent is relayed from
secondary sources quoting the result and was not read from the paper's own
tables; treat the third decimal as unconfirmed.
