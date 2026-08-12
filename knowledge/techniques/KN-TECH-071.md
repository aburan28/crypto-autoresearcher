---
id: KN-TECH-071
type: technique
title: Algebraic modelling of block ciphers - equation systems, XL/XSL, and the negative result that defines the technique's limits
tags: [algebraic-cryptanalysis, equation-system, xl, xsl, bes, sat-solver, groebner, algebraic-differential, aes, overdefined, negative-result, symmetric-cryptanalysis, symmetric, adjacent]
confidence: established
complexity: "no established complexity: writing the system is cheap and solving it is the whole problem; published XSL complexity claims for AES were shown not to hold, and no algebraic attack faster than exhaustive search on a full standardised block cipher is recorded in this corpus"
applicability: reduced-round ciphers, ciphers with algebraically simple round functions, and hybrid attacks where an algebraic solver replaces the final key-guessing step of a statistical attack; NOT a general-purpose method against wide-trail SPNs
source_refs: [KN-TECH-004, KN-TECH-011, KN-TECH-053, KN-LIT-3223, KN-LIT-2466, KN-LIT-2467, KN-LIT-2409, KN-LIT-2392, KN-LIT-2495, KN-LIT-2382, KN-LIT-7593, KN-TECH-075]
added: 2026-07-31
superseded_by: null
---

## Method

Write the cipher as a system of polynomial equations over `F_2` (or over the
S-box's native field) in the plaintext, ciphertext and key variables; recovering
the key is then solving the system. The construction is straightforward:

- **S-boxes give the equations.** An S-box that is an inversion in `F_{2^8}` —
  the AES case — satisfies an **overdefined** system of low-degree relations
  between its input and output bits, because `x · y = 1` is itself quadratic.
  Overdefined means: more equations than the generic count for the number of
  variables, which is the property that motivated the whole line.
- **Linear layers are free.** They contribute linear equations, adding no
  degree.
- **Intermediate variables keep the degree down** at the price of variable
  count, and the trade between the two is the modelling decision that matters.

The system is then handed to a solver — Gröbner basis methods
(`KN-TECH-004`, `KN-TECH-011`), an MQ/Boolean solver (`KN-TECH-053`), or a
SAT/SMT solver. **This is the same solver machinery the program uses for
summation-polynomial systems**, which is the main reason this entry belongs in
this corpus at all.

### XL, XSL, and what actually happened

Courtois–Pieprzyk (`KN-LIT-3223`) proposed **XSL**, an XL-style method
(`KN-TECH-053`) specialised to the sparse, overdefined structure of an SPN, and
claimed complexities that would have broken AES. The claim did not survive
scrutiny: dedicated analyses of the algorithm (`KN-LIT-2466`) and of its
application to the BES embedding (`KN-LIT-2467`) showed that **XSL does not work
as claimed** — the linear-algebra step does not behave as the complexity
argument assumed. Murphy–Robshaw's BES embedding, which re-expresses AES over
`F_{2^8}` to make its algebraic structure explicit, remains a real
contribution; the attack complexity does not.

**This is the technique's defining episode and belongs in any citation of it.**
An algebraic attack's cost is the *solving* cost, and solving cost is not
predicted by the ease of writing the system down. Counting equations and
variables is not a complexity analysis.

### Where algebraic modelling does pay

- **Reduced-round and structurally weak targets**, where SAT or Gröbner solvers
  finish: KeeLoq (`KN-LIT-2382`), round-reduced hash compression functions
  (`KN-LIT-2392`, `KN-LIT-2495`).
- **Hybrid statistical-algebraic attacks** (`KN-LIT-2409`): use a differential to
  constrain the state, then let an algebraic solver do the final key recovery
  instead of exhaustive guessing. The algebra replaces the guessing step, not the
  distinguisher.
- **Designs whose security argument is algebraic in the first place** — low
  multiplicative complexity, low degree over a large field — which is where the
  method is genuinely dominant (`KN-TECH-075`).
- **Structural analysis of components**, such as reading AES's S-box algebra to
  drive a round-reduced attack (`KN-LIT-7593`).

## Program usage

- **Solver-side continuity is the concrete link.** The degree-of-regularity and
  first-fall-degree discipline this program applies to summation-polynomial
  systems (`KN-TECH-004`, `KN-TECH-011`) is the same discipline that governs
  algebraic attacks on ciphers, and `KN-FIND-006` — the Macaulay rank deficit
  being bounded structural syzygy content — is exactly the kind of result that
  decides whether a structured system solves faster than a generic one. Cipher
  systems and summation-polynomial systems are both *structured and
  non-generic*, and both punish the assumption that structure implies
  tractability.
- **XSL is the corpus's best external example of the failure mode `AGENTS.md`
  exists to prevent**: a headline complexity, derived from a plausible but
  unvalidated model of a solver's behaviour, published against a flagship
  target, and later shown not to hold. The program's own guard is
  `docs/claims-and-verification.md` — a claimed solve carries a certificate the
  wrapper re-verifies. XSL claimed no certificate and produced no key.
- **Cost-model honesty.** `KN-TECH-053` already warns against quoting a solver
  exponent as an end-to-end exponent. Algebraic cryptanalysis is where that
  warning was earned.

## Applicability limits

- **Writing the system is not attacking the cipher.** Any claim in this family
  stands or falls on measured solving behaviour, on the actual system, at the
  actual scale.
- **Solving-degree behaviour on structured systems is not predicted by generic
  bounds.** Semi-regularity assumptions do not hold for cipher systems, and
  extrapolating a solving degree observed at small round counts is subject to
  the scope rules of `KN-TECH-052`.
- **Wide-trail SPNs at full round count are not a target.** No entry in this
  corpus records an algebraic attack faster than exhaustive search on a full
  standardised block cipher.
- **SAT-solver timings are not complexities.** A wall-clock result on one
  instance with one solver is an observation, not an exponent, and needs the
  full-cost framing of `KN-TECH-035` before it is compared to anything.

## Verified vs reported

Governed by `KN-TECH-062`'s sourcing note. The modelling construction, the
overdefined-system property of inversion-based S-boxes, and the shape of the
XL/XSL proposal are standard published knowledge, written from established
knowledge and not re-derived here. **The statement that XSL does not achieve its
claimed complexity is recorded as an established result of the public
literature; it is corroborated in this corpus only by the titles of
`KN-LIT-2466` and `KN-LIT-2467`, whose contents were not read.** The
Murphy–Robshaw BES paper and the Cid–Leurent analysis are named in prose where
no `KN-LIT` entry exists; no identifier was minted. `KN-LIT-3223` is, per its own
record, a title-level entry with no extracted abstract and auto-assigned tags
that are wrong for the paper — citing it establishes the paper's presence in
this corpus and nothing about its contents. The claim that no full-cipher
algebraic break appears in this corpus is an observation about **this corpus**
as read on 2026-07-31, not a survey of the literature. The parallel to
`KN-FIND-006` and to the program's certificate rule is this program's own
reasoning.
