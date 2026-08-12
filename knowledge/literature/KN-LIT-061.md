---
id: KN-LIT-061
type: literature
title: On the concrete hardness of Learning with Errors (the LWE estimator)
authors: [Albrecht Martin R., Player Rachel, Scott Sam]
year: 2015
venue: Journal of Mathematical Cryptology, 9(3):169-203
identifiers:
  eprint: iacr:2015/046
  doi: 10.1515/jmc-2015-0016
  url: https://eprint.iacr.org/2015/046
tags: [lwe-estimator, concrete-hardness, bit-security, bkz-cost-model, parameter-selection, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
A software tool (the "LWE-Estimator") plus methodology that collects known attacks
and estimates the concrete cost / bit-security of solving specific LWE instances,
spanning the uSVP/embedding, decoding (BDD), and dual attack families under
varying BKZ cost models.

## Key claims (as reported)
- Makes LWE instances comparable and is widely used to SET PARAMETERS for
  lattice-based primitives.
- Estimates depend on the assumed BKZ/SVP-oracle cost model (KN-TECH-020), so
  outputs carry model uncertainty by design.

## Relevance to this program
POST-QUANTUM hardness-estimation tooling, ADJACENT to the ECDLP mission. Recorded
as context: this is HOW the concrete security of the ECDLP-replacement schemes
(KN-TECH-022) is set -- the lattice analogue of the program's fully-charged cost
accounting for ECDLP attacks. Methodologically kindred (translate attacks into a
concrete cost model) though the object (LWE) is unrelated to discrete logs.

## Not verified here
Full paper not read; the estimator methodology relayed from the abstract (hence
confidence: reported). The De Gruyter JMC DOI matches the standard scheme and DBLP
record; venue/volume/pages firmly confirmed, DOI search-inferred. IACR ePrint
2015/046. Not fetched directly.
