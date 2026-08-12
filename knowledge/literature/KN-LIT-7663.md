---
id: KN-LIT-7663
type: literature
title: "On the Concrete Hardness Gap Between MLWE and LWE"
authors:
  - "Tabitha Ogilvie"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/279"
identifiers:
  eprint: "iacr:2026/279"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/279"
tags: [module-lwe, ring-lwe, lwe, cyclotomic, structure, hybrid-attack, dual-attack, primal-attack, concrete-security, cost-model, kyber, ml-kem, fhe, sparse-secret, symmetry]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
Shows that the standard heuristic of estimating **Module-LWE** security by translating
to an "equivalent" unstructured **LWE** instance — which treats algebraic structure as
pure efficiency with **no security cost** — **fails at realistic parameters**.

The mechanism is **coefficient isometries**: ring elements whose multiplication acts as
a **signed permutation** on coefficient vectors and preserves the secret and error
distributions. Multiplying an MLWE instance by such an isometry produces many derived
instances **sharing the same public matrix**, hence compatible with the **same expensive
offline preprocessing** in a hybrid attack. The authors formalise this and incorporate it
into both **primal and dual hybrid** frameworks, instantiating coefficient isometries for
power-of-two cyclotomic rings.

Quantified in two regimes:

- **Sparse-secret RLWE** (common in homomorphic encryption): gaps of **up to 15 bits**
  over LWE-based estimates.
- **Standardised Kyber / ML-KEM parameters**: a consistent **2–3 bit gap** under
  standard cost models.

## Key claims (as reported)
- Coefficient isometries exist for power-of-two cyclotomic rings and preserve the
  relevant distributions.
- Derived instances amortise hybrid-attack preprocessing.
- **The widely assumed LWE ≡ MLWE equivalence in power-of-two cyclotomics does not
  hold** concretely.
- 15-bit (sparse-secret RLWE) and 2–3-bit (Kyber/ML-KEM) gaps.

**Read the magnitudes carefully.** 2–3 bits on ML-KEM is a real, measurable
overestimate of security, and it is **nowhere near a break** — it does not move any
standardised parameter set out of its NIST category on the figures as stated. The
15-bit sparse-secret figure is the one with practical bite, and it applies to FHE
parameter choices rather than to the KEM.

## Relevance to this program
**This is the most directly program-relevant lattice entry in the sweep**, because it is
a quantitative answer to a question the corpus already carries as open.

[[KN-OPEN-012]] asks whether ideal/module lattices admit structure-exploiting attacks
beyond generic BKZ, and whether the ECDLP program's structure-exploitation experience
transfers. [[KN-TECH-046]] records the established half of the answer — the cyclotomic
PIP line — and states plainly that the `exp(Õ(√n))` approximation factor it reaches is
**far above deployed parameters**, so no deployed scheme is affected.

This paper opens a **second, different** route: not the number-theoretic
class-group/unit-lattice line, but a **symmetry-amortisation** line that bites *at
deployed parameters* and yields small but nonzero bit gaps. That is a materially new
shape of answer, and together with [[KN-LIT-7667]] (which reports up to 13 bits on FHE
RLWE parameters by a different ring-structure mechanism) it is enough to crystallize
[[KN-OPEN-026]].

The methodological parallel to this program's own domain is exact and worth stating:
**index calculus on curves also works by amortising expensive preprocessing (the factor
base) across many derived instances, using automorphisms to multiply the relations
harvested per unit of work.** The `symmetry`/`glv-gls` speedups the corpus tracks are
the same move. Whether that parallel is more than an analogy is what `KN-OPEN-012`
asks and this entry does not answer.

**Does not bear on the ECDLP.**

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/279,
retrieved 2026-08-01 (hence `confidence: reported`); the abstract is truncated in the
retrieved record. Citation checked against the ePrint record: title, sole author
Tabitha Ogilvie, report number, year 2026.

NOT verified here: the coefficient-isometry construction; the distribution-preservation
argument; the primal/dual hybrid incorporations; and the 15-bit and 2–3-bit figures or
the cost models they are computed under — **bit-gap figures are model-relative, and the
model is not recorded here**. **No ML-KEM, Kyber, or FHE parameter set is reassessed by
this program**, and nothing here is a break claim.
