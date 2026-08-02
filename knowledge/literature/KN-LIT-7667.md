---
id: KN-LIT-7667
type: literature
title: "Careful with the Ring: Enhanced Hybrid Decoding Attacks against Module/Ring-LWE"
authors:
  - "Jianhua Hou"
  - "Haodong Jiang"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/366"
identifiers:
  eprint: "iacr:2026/366"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/366"
tags: [module-lwe, ring-lwe, hybrid-attack, decoding, cyclotomic, structure, sparse-secret, fhe, concrete-security, cost-model, lattice-estimator, symmetry]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
An **enhanced hybrid decoding attack** against Module/Ring-LWE over
`Z_q[X]/(x^N + 1)` that **uses the ring structure to accelerate the guessing and
decoding steps** — structure that concrete security analyses normally ignore, for want
of a technique to exploit it.

Reported results:

- A theoretical complexity improvement by a factor of **`O(N)`** over the prior hybrid
  decoding attack **in the sparse-secret setting**.
- Implemented on the benchmark instances of [WSM+25, S&P], achieving new records:
  **17× to 114× faster** than the state of the art of [KKN+26, EC] on known broken
  instances.
- A method to estimate concrete bit security **under the same model as the lattice
  estimator**, applied to recent sparse Ring-LWE parameter sets used in FHE schemes
  (five cited EUROCRYPT/CCS/Crypto parameter sets), reporting attack-complexity
  improvements of **up to 13 bits**.

## Key claims (as reported)
- Ring structure accelerates both the guessing and decoding phases of hybrid decoding.
- `O(N)` asymptotic improvement in the sparse-secret setting.
- 17×–114× practical speedups on published benchmark instances.
- Up to **13 bits** improvement against the evaluated FHE sparse Ring-LWE parameter
  sets, computed in the lattice-estimator cost model.

## Relevance to this program
Together with [[KN-LIT-7663]] this is the substance behind [[KN-OPEN-026]], and the two
are **independent** mechanisms reaching a similar conclusion:

- [[KN-LIT-7663]] amortises **hybrid-attack preprocessing** across instances derived by
  coefficient isometries (a symmetry argument), reporting up to 15 bits in sparse-secret
  RLWE and 2–3 bits on ML-KEM.
- **This paper** accelerates the **guessing and decoding steps themselves** using the
  ring's multiplicative structure, reporting up to 13 bits on FHE sparse Ring-LWE.

The shared conclusion — *treating Module/Ring-LWE as equivalent to unstructured LWE
overestimates security at deployed parameters, by a small but nonzero margin, most
sharply for sparse secrets* — is now supported by at least two independent 2026 results,
with [[KN-LIT-7666]] pointing the same way from a third direction.

This matters to the program beyond lattices because it is a **direct answer to the
transfer question in [[KN-OPEN-012]]**: structure-exploitation *does* buy concrete
advantage here, at deployed sizes, without needing the `exp(Õ(√n))` regime that
[[KN-TECH-046]] documents as far out of reach. The mechanism — using automorphisms and
ring multiplication to multiply the useful work extracted per unit of expensive
preprocessing — is the same shape as the symmetry speedups in curve index calculus that
the corpus tracks under `symmetry` and `glv-gls`.

**None of this is a break.** 13 bits against an FHE parameter set is a parameter-choice
input, not a compromise, and this entry claims nothing more.

**Does not bear on the ECDLP.**

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/366,
retrieved 2026-08-01 (hence `confidence: reported`); the abstract is truncated in the
retrieved record. Citation checked against the ePrint record: title, two authors, report
number, year 2026.

NOT verified here: the ring-structure acceleration; the `O(N)` factor; the 17×–114×
benchmark results; the 13-bit figure or the estimator model it is computed under; and
the citations [WSM+25, S&P], [KKN+26, EC], [JM22, EC], [CCKS23, CCS], [BCKS24, EC],
[CHKS25, EC], [AKP25, C], **none of which is an entry in this corpus and none of which
was checked**. No FHE parameter set is reassessed by this program.
