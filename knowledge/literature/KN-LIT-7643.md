---
id: KN-LIT-7643
type: literature
title: "High-Order Galois Automorphisms for TNFS Linear Algebra"
authors:
  - "Haetham Al Aswad"
  - "Cécile Pierrot"
  - "Emmanuel Thomé"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/560"
identifiers:
  eprint: "iacr:2026/560"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/560"
tags: [number-field-sieve, tnfs, dlp, finite-field, extension-field, pairing, galois, automorphism, index-calculus, linear-algebra, cost-model, number-theory, cryptanalysis]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
The Tower Number Field Sieve (TNFS) is the best known algorithm for the discrete
logarithm problem in `F_{p^n}` with composite `n` — the setting of pairing-based
cryptography. Order-`k` **Galois automorphisms** are already known to accelerate TNFS's
**relation-collection** step by a factor `k`; using them to accelerate the **linear
algebra** step was open beyond `k = 2`.

This paper gives constructions for **`k = 6` and `k = 12`**, in `F_{p^6}` and
`F_{p^{12}}` respectively, reported to accelerate the linear-algebra step by
approximately **36×** and **144×** — i.e. the quadratic-in-`k` factor `k²` previously
achieved only at `k = 2` (factor 4). A SageMath implementation of TNFS and of the new
construction is reported, validated on small examples.

## Key claims (as reported)
- New construction permitting an order-6 (resp. order-12) Galois automorphism to be
  used in TNFS linear algebra over `F_{p^6}` (resp. `F_{p^{12}}`).
- Speedups of "approximately" `36` and `144` for that step. The abstract gives these as
  the quadratic factor `k²`; it does **not** state an end-to-end TNFS speedup, and
  linear algebra is one of two dominant steps, so the overall effect is smaller than
  either number and is not quantified here.
- Validation is on **small examples** only. No record-scale computation is claimed.
- The general problem — arbitrary `k` — is stated as previously open; this paper closes
  two specific cases, not the general one. Recorded as [[KN-OPEN-025]].

## Relevance to this program
Direct, and unusually so for a gather item. This is a **cost-model change for the
DLP in extension fields**, the exact algorithmic family the program tracks under
`index-calculus`/`number-field-sieve`, applied to the parameter sizes that
pairing-based cryptography actually deploys (`n = 6, 12`).

- The corpus was thin here: a coverage audit on 2026-08-01 found only two entries
  mentioning TNFS at all, against 218 touching index calculus. This entry and
  [[KN-TECH-081]]'s neighbourhood are a deliberate patch of that gap.
- **Symmetry exploitation is a recurring program theme.** Automorphism/symmetry
  speedups in index calculus over binary and extension fields are already tracked
  (`symmetry`, `weil-descent` threads); this is the same idea acting on the *linear
  algebra* rather than on the sieving, which is the harder half to exploit because the
  matrix structure must be preserved. Worth reading for the mechanism, not only the
  numbers.
- **It moves constants, not exponents.** TNFS asymptotics are unchanged. Under the
  target-result profile (`docs/target-result-profile.md`) this is not an
  exponent-moving result and must not be cited as one.

Bears on `F_{p^n}` DLP and pairing security estimation. **Does not bear on the
prime-field ECDLP**, and says nothing about elliptic-curve group order.

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/560,
retrieved 2026-08-01 (hence `confidence: reported`). Citation checked against the
ePrint record: title, three authors, report number, year 2026.

NOT verified here: the constructions themselves; the 36× and 144× figures or the model
they are measured in; whether the quadratic factor is realised in a full implementation
at cryptographic sizes; and any consequence for concrete pairing-parameter security
levels. **No security estimate for any BLS/BN curve in this program is revised here.**
Deriving one from a linear-algebra-step speedup without the relation-collection side and
without a scale-up would be exactly the partial-cost error `AGENTS.md` rule 4 forbids.
