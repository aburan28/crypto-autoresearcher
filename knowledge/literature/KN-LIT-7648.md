---
id: KN-LIT-7648
type: literature
title: "Cryptanalysis of Definite and Indefinite Lattice Isomorphism Problems With Applications to DEFI"
authors:
  - "Markus Kirschmer"
  - "Cong Ling"
  - "Ali Sadreddin"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/890"
identifiers:
  eprint: "iacr:2026/890"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/890"
tags: [lattice-isomorphism-problem, lattice-isomorphism, quadratic-form, genus, spinor-genus, cryptanalysis, signature, pqc, number-theory, group-action, hawk, key-recovery]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
Cryptanalysis of the **Lattice Isomorphism Problem (LIP)** for both **definite and
indefinite** quadratic forms, applied to the **DEFI** signature scheme (built on
isotropic quadratic forms).

The stated mechanism is arithmetic rather than lattice-reduction: for indefinite forms
of dimension `≥ 3` arising in DEFI, the authors prove that under suitable assumptions
the **genus, spinor genus, and equivalence class coincide** — a *structural collapse*
that makes Decision/Distinguishing-LIP solvable in **classical polynomial time** on
those instances.

They further report an efficient **secret-key recovery** algorithm against DEFIv2, with
**signature forgeries demonstrated within minutes** on the authors' public challenge
instances. They evaluate the same methods against **HAWK** and report that HAWK is
**not** compromised.

## Key claims (as reported)
- Genus = spinor genus = equivalence class for the relevant indefinite forms, under
  suitable (unstated in the abstract) assumptions.
- Classical polynomial-time Decision/Distinguishing-LIP for DEFI-derived instances.
- Practical key recovery and forgery against **DEFIv2**, minutes on public challenges;
  Magma code stated to be public.
- **HAWK is explicitly reported unaffected.** The definite case behaves differently
  from the indefinite one; this is a scoped break, not a break of LIP.

## Relevance to this program
The cleanest recent example of the pattern the inventor protocol calls a **lossy
projection**, and it is worth holding for that reason as much as for the break itself:

- The scheme's hardness was supposed to come from *isomorphism of quadratic forms*. But
  the **genus** is a cheap, computable invariant (local data at every place), and the
  **spinor genus** refines it. When the class-field-theoretic machinery forces those
  invariants to *coincide* with the isomorphism class, the "hard" isomorphism problem
  was never hiding anything — the public data already determines the answer. The attack
  is classical, polynomial, and uses no lattice reduction.
- This is a **class-field-theory-driven cryptanalysis**: genus theory and spinor genera
  are exactly the arithmetic of quadratic forms over adeles. It is the strongest
  argument in this sweep that the algebraic-number-theory literature — not just the
  algorithmic-cryptography literature — is a live source of attacks.
- **Group-action/isomorphism cryptography is a broad current family** (LESS, MEDS,
  ALTEQ, LIP-based schemes, and the class-group actions in
  [[KN-LIT-7655]]). The transferable lesson is procedural: *before* believing an
  isomorphism assumption, enumerate the classical invariants of the objects and check
  whether they separate the orbits. Compare [[KN-LIT-7652]], which attempts the
  invariant-theoretic route on linear-code equivalence and reports it infeasible at
  cryptographic parameters — the same question, opposite outcome.

**Does not bear on the ECDLP.**

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/890,
retrieved 2026-08-01 (hence `confidence: reported`). Citation checked against the
ePrint record: title, three authors, report number, year 2026. The record carries a
note that v1 was submitted to CRYPTO on 2026-02-13 with Magma code published at the
same time.

NOT verified here: the genus/spinor-genus collapse theorem or its "suitable
assumptions"; the polynomial-time claim; the key-recovery and forgery results; the
minutes-scale timings; and the assessment that HAWK is unaffected. **The HAWK
non-result is relayed, not confirmed, and must not be cited as an endorsement of HAWK's
security.** No DEFI or HAWK parameter set is assessed by this program.
