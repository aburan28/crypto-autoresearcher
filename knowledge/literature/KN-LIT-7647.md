---
id: KN-LIT-7647
type: literature
title: "SoliloQuat: Throwing Caution to the Wind"
authors:
  - "Andrew Mendelsohn"
  - "Ben Nelson"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/859"
identifiers:
  eprint: "iacr:2026/859"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/859"
tags: [principal-ideal-problem, quaternion, quaternion-algebra, lattice, ideal-lattice, lattice-isomorphism-problem, pqc, provable-security, number-theory, soliloquy, hawk]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
Proposes **SoliloQuat**, a plausibly post-quantum **additively homomorphic PKE** whose
security rests on the **short-generator principal ideal problem (SG-PIP) in orders of
quaternion algebras** — i.e. the non-commutative analogue of the assumption behind
Soliloquy.

Soliloquy is the cautionary precedent the name invokes: introduced *and broken* by
Campbell–Groves–Shepherd in 2014, in the commutative cyclotomic setting. The authors'
stated position is that **it is not known whether that attack generalizes to the
non-commutative setting**, and they note the setting has drawn cryptanalytic attention
via a Eurocrypt 2025 reduction from **rank-2 module-LIP instances underlying HAWK to
nrd-PIP**.

Correctness requires new results on the **eigenvalues of the left regular representation
of quaternions**, which the authors offer as of independent interest. IND-CPA security
is proved assuming hardness of SG-PIP in quaternion orders plus "less-exotic"
lattice-based assumptions.

## Key claims (as reported)
- SoliloQuat is additively homomorphic and IND-CPA secure **under SG-PIP in quaternion
  orders** and further lattice assumptions.
- Whether the Campbell–Groves–Shepherd/Cramer–Ducas–Peikert–Regev-style attacks
  generalize to non-commutative orders is stated as **open**.
- New eigenvalue results for the left regular representation of quaternions.
- The title and framing are self-aware about the risk: this is a *proposal on an
  unbroken-but-unstudied assumption*, and the paper says so.

## Relevance to this program
This is the cryptographic-design end of the same object [[KN-LIT-7641]] attacks
algorithmically, and reading the two together is the point of ingesting both:

- **[[KN-LIT-7641]] solves PIP in `M_g(O)` for `g ≥ 2`** in heuristic expected
  polynomial time. **SoliloQuat assumes SG-PIP is hard in an order `O` itself.** These
  are not in contradiction — different rank, and *find a generator* versus *find a
  short generator* — but the distance between them is small, well-defined, and
  unresolved. That gap is recorded as [[KN-OPEN-024]] and is, on this sweep's reading,
  the single most concrete open question the algebraic-number-theory literature is
  currently putting in front of this program.
- **The commutative precedent is a solved case with a known shape**, and this program
  already holds it: [[KN-TECH-046]] sets out the three-stage line — quantum class-group
  and principal-ideal computation, then **short-generator recovery by decoding the
  log-unit lattice** ([[KN-LIT-115]]), then Stickelberger-based extension from principal
  to general ideals ([[KN-LIT-116]]). Soliloquy died at the second stage. Whether
  quaternion orders admit an analogous **unit-lattice decoding** step is precisely what
  SoliloQuat is betting against, and it is the substance of [[KN-OPEN-024]].
- **Non-commutativity as claimed protection.** [[KN-LIT-7644]] is a documented case of
  an algebraic obstruction ("`O_K` isn't Euclidean") turning out to complicate rather
  than block an algorithm. That is not evidence against SoliloQuat — it is the reason
  the assumption deserves the attention the authors invite.

**Does not bear on the ECDLP.**

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/859,
retrieved 2026-08-01 (hence `confidence: reported`). Citation checked against the
ePrint record: title, two authors, report number, year 2026.

NOT verified here: the scheme, its correctness, the IND-CPA proof, the eigenvalue
results, the parameters, or any concrete security level. The attributions to
Campbell–Groves–Shepherd (2014) and to the Eurocrypt 2025 module-LIP-to-nrd-PIP
reduction are **relayed from this abstract and not independently checked against those
sources**; neither is currently an entry in this corpus. **No assessment of whether
SG-PIP in quaternion orders is hard is made or implied here.**
