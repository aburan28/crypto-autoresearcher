---
id: KN-LIT-7573
type: literature
title: "Classic McEliece: conservative code-based cryptography (NIST round-4 specification)"
authors: [Albrecht Martin R., Bernstein Daniel J., Chou Tung, Cid Carlos, Gilcher Jan, Lange Tanja, et al.]
year: 2022
venue: NIST PQC Standardization Process, round-4 submission package (mceliece-spec-20221023)
identifiers:
  eprint: null
  doi: null
  url: https://classic.mceliece.org/nist.html
tags: [code-based, mceliece, niederreiter, goppa, kem, pqc, specification, parameter-selection]
confidence: reported
citation_verified: web
added: 2026-07-27
superseded_by: null
---

## Contribution
The specification of record for the modern binary-Goppa KEM: Niederreiter
syndrome form (KN-LIT-7565), fixed-weight error vectors, and an
implicit-rejection CCA2 conversion, with parameter sets named by code length and
error weight (mceliece348864 at category 1 through mceliece6688128,
mceliece6960119, mceliece8192128 at the top category). The design goal is stated
as conservatism: the parameters target a scheme whose security assumption has
not moved since 1978.

## Key claims (as reported)
- Public keys are very large -- of order 10^5 to 10^6 bytes (mceliece6688128 is
  reported at 1,044,992 bytes) -- while ciphertexts are tiny (reported 208 bytes
  for the same set).
- The security assumption is unchanged from KN-LIT-7564; the parameter growth
  since 1978 reflects cryptanalytic progress in ISD constants (KN-LIT-7568,
  KN-LIT-2607) rather than any exponent collapse.

## Relevance to this program
The concrete target that every code-based cost claim in this corpus is
ultimately aimed at, and the reason KN-TECH-061 insists on estimator-based
rather than asymptotic parameter reasoning. The key-size/ciphertext-size
asymmetry is also the practical fact behind NIST's round-4 outcome
(KN-LIT-7575): Classic McEliece was not rejected on security grounds.

## Not verified here
Specification PDF not fetched -- classic.mceliece.org returned HTTP 403 to the
fetch tool used. The document name (mceliece-spec-20221023), the contributor
list, the parameter-set names, and the two size figures were confirmed via
search against the project site's indexed pages and NIST-hosted round-4
materials, not read from the specification itself. The author list is the
project's stated contributor set and may be incomplete; treat it as indicative.
No size figure here was independently recomputed.
