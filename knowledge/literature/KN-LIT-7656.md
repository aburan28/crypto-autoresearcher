---
id: KN-LIT-7656
type: literature
title: "Forensic categories: a framework for SQIsign-like primitives"
authors:
  - "Andrea Basso"
  - "Luca De Feo"
  - "Sikhar Patranabis"
  - "Ilinca Radulescu"
  - "Benjamin Wesolowski"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/1171"
identifiers:
  eprint: "iacr:2026/1171"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1171"
tags: [deuring, quaternion, quaternion-algebra, endomorphism-ring, isogeny, supersingular, sqisign, category-theory, abstraction, signature, chameleon-hash, provable-security, elliptic-curve]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
A categorical framework — "forensic categories" — abstracting the key **algorithmic**
features of the **Deuring correspondence** between supersingular elliptic curves and
quaternion orders, and of the **SQIsign** signature scheme built on it.

Within the framework the authors construct an interactive identification scheme and a
digital signature, and instantiate more advanced primitives including a **chameleon
hash function**. Two instantiations from supersingular-curve isogenies are given: the
first **recovers one-dimensional SQIsign**, the second yields **SQInstructor**.

## Key claims (as reported)
- A category-theoretic abstraction capturing what SQIsign-like constructions actually
  require of the Deuring correspondence.
- Identification scheme, signature, and chameleon hash constructed at the abstract level.
- Two concrete instantiations recovering known schemes — a **consistency check on the
  abstraction**, not a new scheme or a new hardness result.

## Relevance to this program
Ingested for **the abstraction, not the constructions** — and it is the more useful half
for a research harness.

An axiomatization of "what SQIsign needs from the Deuring correspondence" is, read
adversarially, an **enumeration of the structural properties an attack could target**.
If a small list of categorical features suffices to build the scheme, then either those
features are hard to compute in the supersingular instantiation or the scheme is
broken — and the list tells you exactly which computations to price. That is the same
move [[KN-OPEN-019]] asks this program to make for the ECDLP and has not yet made:
*write down what each family actually depends on*. Here a strong author list has done it
for the isogeny side, and the result is worth reading as a template for that exercise
rather than only as a construction paper.

Connected entries: [[KN-LIT-7642]] supplies the concrete quaternion arithmetic these
abstractions are instantiated over; [[KN-LIT-7641]] is a result about what that
arithmetic gives away; and [[KN-LIT-1919]] holds SQInstructor, the second
instantiation.

**No new hardness assumption, attack, or cost claim is reported**, and the entry does
not imply one. **Does not bear on the prime-field ECDLP.**

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/1171,
retrieved 2026-08-01 (hence `confidence: reported`). Citation checked against the
ePrint record: title, five authors, report number, year 2026.

NOT verified here: the framework's axioms; the constructions or their security proofs;
the chameleon hash; and the claim that the instantiations recover SQIsign and
SQInstructor. The adversarial reading in "Relevance" — that the axiom list doubles as an
attack-surface enumeration — is **this program's inference and appears nowhere in the
source**; no attack surface is identified here and none is claimed to exist.
