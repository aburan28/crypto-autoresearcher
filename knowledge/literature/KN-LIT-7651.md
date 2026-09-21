---
id: KN-LIT-7651
type: literature
title: "Cryptanalysis of Hecke-KE: A Linear-Algebra Attack via Hecke Eigenbasis Decomposition"
authors:
  - "Xiyao Chen"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/770"
identifiers:
  eprint: "iacr:2026/770"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/770"
tags: [hecke, modular-forms, cryptanalysis, key-recovery, number-theory, commuting-operators, broken-platform, one-way-function, unfixable, sturm-bound]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
A passive attack that **breaks Hecke-KE**, a key-exchange scheme proposing products of
**Hecke operators on `S_k(Γ_0(N))`** as a one-way function.

The stated mechanism: the Hecke algebra acting on a fixed space of cusp forms
`S_k(Γ_0(N))` is **simultaneously diagonalizable over an explicit number field
computable from the public parameters alone**. Diagonalizing reduces shared-key recovery
to `d` scalar divisions in that field, where `d = dim S_k(Γ_0(N))`.

Costs as reported: a **one-time public** precomputation of the eigenbasis at
`Õ(B · d³)` rational operations with `B = O(N)` the Sturm bound; then **`O(d²)` field
operations per session**, independent of the pool size `r` and of the number `s` of
Hecke factors. Verified in SageMath 10.7 against all parameter sets from the original
paper, recovering `K' = K` in every case.

## Key claims (as reported)
- Attack is polynomial in `d` for **every** level `N` (prime or composite) and **every**
  weight `k` — proved, per the abstract, not merely observed.
- The honest protocol's public key is `Ω(d)` rationals, so **enlarging `d` cannot
  outrun the attack**: there is no `(N, k)` that is simultaneously secure and
  implementable. The abstract states the scheme is **unfixable within its design
  framework**.
- Implementation public (GitHub link on the ePrint record).

## Relevance to this program
A textbook **lossy-projection failure**, and among the most instructive in this sweep
because the leak is not subtle — it is the defining property of the object.

The scheme's premise was that composing many Hecke operators hides the composition.
But the Hecke algebra is **commutative and simultaneously diagonalizable**: in the
eigenbasis every product is a product of scalars, and the eigenbasis depends only on
`(N, k)`, which are public. The "hard" non-commutative-looking composition was a
diagonal matrix in disguise. Multiplicity of the hiding parameters (`r`, `s`) buys
nothing because the attack cost does not depend on them.

Transferable rules this entry supports, both already in the program's doctrine
(`docs/inventor-protocol.md`, [[KN-TECH-056]]) and now with a concrete 2026 instance:

- **A commuting family of operators is not a hiding structure.** If the platform's
  operators commute, ask for the joint eigendecomposition before believing anything.
- **Check whether the secret survives a basis change computable from public data.**
  Here the entire secret collapses under a public change of basis.
- **Parameter inflation is not a repair** when the attack's cost is independent of the
  inflated parameter. The `Ω(d)` public-key size versus `poly(d)` attack cost argument
  is the clean way to state that, and is worth reusing.

Relevant to modular-forms-based proposals generally; the corpus has 122 entries
touching `Hecke` and this is the first cryptanalytic one indexed as such.

**Does not bear on the ECDLP.**

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/770,
retrieved 2026-08-01 (hence `confidence: reported`). Citation checked against the
ePrint record: title, sole author Xiyao Chen, report number, year 2026.

NOT verified here: the diagonalizability argument; the complexity figures; the claimed
proof of polynomial-time attack for all `(N, k)`; the SageMath verification; and the
"unfixable" assessment, which is a strong claim about a design space rather than about
a parameter set. The Hecke-KE proposal itself is **not** in this corpus and was not
consulted — this entry records the attack's own account of what it attacks.
