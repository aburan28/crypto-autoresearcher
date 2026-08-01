---
id: KN-LIT-057
type: literature
title: Falcon - Fast-Fourier Lattice-based Compact Signatures over NTRU (FN-DSA / FIPS 206 draft)
authors: [Fouque Pierre-Alain, Hoffstein Jeffrey, Kirchner Paul, Lyubashevsky Vadim, Pornin Thomas, Prest Thomas, Ricosset Thomas, Seiler Gregor, Whyte William, Zhang Zhenfei]
year: 2020
venue: NIST PQC standardization submission (Round 3 spec); FIPS 206 (FN-DSA) forthcoming
identifiers:
  eprint: null
  doi: null
  url: https://falcon-sign.info/
tags: [falcon, fn-dsa, ntru-lattice, gpv, hash-and-sign, signature, nist, fips-206, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Falcon is an NTRU-lattice hash-and-sign signature built on the GPV framework
(KN-LIT-058), using fast-Fourier lattice trapdoor sampling. It produces the
smallest signatures and public keys among the NIST PQC signature finalists, at the
cost of floating-point Gaussian sampling that is hard to implement in constant
time. Security rests on SIS over NTRU lattices (KN-LIT-052).

## Key claims (as reported)
- Compact GPV hash-and-sign signature; smallest bandwidth among NIST PQC
  signatures.
- NIST intends to standardize it as FN-DSA in FIPS 206; as of 2026-07 this is a
  DRAFT/in-review, not a final standard (delayed largely by constant-time
  floating-point sampling concerns). Exact final title/date UNVERIFIED.

## Relevance to this program
POST-QUANTUM (forthcoming) standard, ADJACENT to the ECDLP mission -- recorded as a
compact NIST replacement for ECDSA where bandwidth is constrained. It combines the
GPV trapdoor paradigm (KN-TECH-023) with NTRU lattices; unrelated to discrete-log
hardness.

## Not verified here
Specification not read; scheme details relayed from the Falcon team spec and NIST
status materials (hence confidence: reported). There is no canonical IACR ePrint
or DOI for the specification; FIPS 206 is not yet final, so its exact title/pages/
date are UNVERIFIED. Existence and FN-DSA=Falcon designation confirmed via NIST
CSRC status pages (surfaced via search).
