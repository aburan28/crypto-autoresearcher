---
id: KN-LIT-7660
type: literature
title: "On the Security of Constraint-Friendly Map-to-Curve Relations"
authors:
  - "Youssef El Housni"
  - "Benedikt Bünz"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/590"
identifiers:
  eprint: "iacr:2026/590"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/590"
tags: [hash-to-curve, elliptic-curve, generic-group-model, ec-ggm, model-failure, forgery, zk-proof, constraint-system, curve-arithmetic, cryptanalysis, security-model]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
A security analysis of the **constraint-friendly map-to-curve relations** of Groth,
Malvai, Miller and Zhang (Asiacrypt 2025), which bypass the expensive inner
cryptographic hash in hash-to-curve inside constraint systems and were proved secure in
the **Elliptic Curve Generic Group Model (EC-GGM)**.

Three gaps are identified:

1. The security bound is not explicitly analysed, and the bounds stated for the
   concrete instantiations are **loose**.
2. **The EC-GGM does not capture the algebraic structure of most deployed curves.** The
   authors exhibit a **concrete signature forgery using the parameters claimed secure**.
3. The construction requires a congruence condition on the field that not all deployed
   curves satisfy; the authors extend it to any field.

As a countermeasure they propose a **`y`-increment variant** that neutralises the
algebraic attack, removes the field restriction, and preserves comparable constraint
count. Both constructions are implemented and benchmarked in **gnark** (Go); the attack
is demonstrated by a self-contained SageMath simulation and confirmed at circuit level
against the original authors' **Noir** (Rust) implementation.

## Key claims (as reported)
- A concrete forgery against parameters the prior work claimed secure — **demonstrated
  in code, at circuit level, against the original implementation**, not merely argued.
- The EC-GGM abstracts away structure that deployed curves actually have, and the proof
  inherits that blindness.
- A repair (`y`-increment) with comparable cost.

## Relevance to this program
This is the sharpest **security-model failure** case the sweep found, and it belongs in
the corpus for methodological rather than algorithmic reasons.

**A proof in a generic-group model is a statement about the model, not the curve.** The
program already knows this abstractly — [[KN-OPEN-019]] records that *every* attack
family that matters (index calculus, isogeny methods) works precisely by leaving the
generic group model, so the `√p` generic bound is not a security argument about a
concrete curve. What was missing was a **current, concrete, executed** instance. Here
the gap between EC-GGM and a real curve is not hypothetical: it is a working forgery on
parameters a 2025 Asiacrypt paper certified.

Three transferable rules this supports:

- **Name the model, then ask what it hides.** EC-GGM hides the field arithmetic and the
  curve equation's algebraic relations. If a construction's security *depends* on those
  being opaque, the proof is vacuous for deployed curves.
- **An unanalysed bound is not a bound.** Gap 1 — a proof whose concrete constant was
  never worked out — is the same failure `KN-TECH-035` guards against on the cost side.
- **A demonstrated forgery is a certificate.** Under
  `docs/claims-and-verification.md` this is the strongest claim tier available for an
  attack: a checkable artifact, not an estimate. Contrast with [[KN-LIT-7670]] in the
  same sweep, where the authors explicitly decline to claim a break because their
  heuristics are unverified.

**Does not bear on the ECDLP.** The forgery exploits the map-to-curve relation, not the
discrete logarithm; no curve's DLP is weakened.

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/590,
retrieved 2026-08-01 (hence `confidence: reported`). Citation checked against the
ePrint record: title, two authors, report number, year 2026.

NOT verified here: the forgery, its parameters, or the SageMath/Noir demonstrations;
the looseness of the original bounds; the field-congruence extension; the `y`-increment
countermeasure or its constraint count; and the gnark benchmarks. The Groth–Malvai–
Miller–Zhang source is **not** an entry in this corpus and was not consulted — this
entry records the attacking paper's account of what it attacks.
