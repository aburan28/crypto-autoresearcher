---
id: KN-TECH-075
type: technique
title: Interpolation and Groebner-basis attacks on low-degree and arithmetization-oriented ciphers
tags: [interpolation-attack, groebner-attack, arithmetization-oriented, mimc, poseidon, anemoi, griffin, marvellous, low-multiplicative-complexity, solving-degree, prime-field, zero-knowledge, symmetric-cryptanalysis, symmetric, adjacent]
confidence: established
complexity: "interpolation: about d+1 known plaintext-ciphertext pairs and Lagrange reconstruction for a cipher of polynomial degree d over the native field; Groebner route: cost is the solving degree of the round-by-round system, which is the quantity these attacks and these designs argue over"
applicability: ciphers designed for low multiplicative complexity over a large field - ZK/MPC/FHE-oriented primitives - where the security argument is algebraic rather than trail-based; not applicable to bit-oriented wide-trail SPNs
source_refs: [KN-TECH-004, KN-TECH-011, KN-TECH-053, KN-TECH-063, KN-TECH-071, KN-LIT-4921, KN-LIT-2451, KN-LIT-2396, KN-LIT-5695, KN-LIT-4246, KN-LIT-5110, KN-LIT-5472, KN-LIT-5676, KN-LIT-7202]
added: 2026-07-31
superseded_by: null
---

## Method

### The design class, and why it changes the analysis

Primitives built for zero-knowledge proofs, MPC and FHE are costed in **field
multiplications**, not in gates. That pushes designers toward round functions
that are algebraically simple over a large field `F_p` or `F_{2^n}` — a single
power map `x → x^3` or `x → x^{1/α}`, few rounds, minimal linear layers. MiMC
(`KN-LIT-4921`), the MARVELlous family (`KN-LIT-2396`), Griffin
(`KN-LIT-4246`) and Anemoi (`KN-LIT-5110`) are representative.

The consequence for cryptanalysis is structural: **the wide-trail argument of
`KN-TECH-070` is unavailable and largely irrelevant.** There are too few S-boxes
for active-S-box counting to say anything, and statistical trails are not the
threat. The security argument is about **algebraic degree and solving degree**,
so the attacks are the algebraic ones.

### Interpolation attacks (Jakobsen–Knudsen, 1997)

If the cipher, as a function of the plaintext over its native field, is a
polynomial of degree `d` with `d` small enough, an attacker reconstructs it by
Lagrange interpolation from about `d+1` known pairs — obtaining a functionally
equivalent decryption box with **no key recovery at all**. Variants push the
interpolation through part of the cipher and solve for the remaining key
material; optimised versions apply to designs like LowMC (`KN-LIT-5676`).

The design response is to force degree growth; the attack's reach is then set by
how fast degree actually grows, which for a power map over `F_p` is far slower
than intuition from bit-oriented ciphers suggests.

### The Gröbner route

The general form: introduce a variable per round state, write one low-degree
equation per round, and solve the resulting system with a Gröbner basis
computation (`KN-TECH-004`, `KN-TECH-011`) or an MQ-style solver
(`KN-TECH-053`). The attack cost is the **solving degree** of that system — the
same quantity, with the same estimation difficulties, that this program tracks
for summation-polynomial systems.

Results in this style include the algebraic attacks on STARK-friendly designs
(`KN-LIT-2396`), the low-degree round-function attack reaching full MiMC
(`KN-LIT-2451`), and the collection of techniques aimed specifically at
integrity-oriented primitives in `KN-LIT-5695`. Higher-order differentials
(`KN-TECH-063`) transfer to this setting with `F_p`-subspaces in place of
`F_2`-subspaces, and the division property has a field-based analogue built for
it (`KN-LIT-5472`).

**The recurring pattern in this literature:** a design's security margin is
argued from an *estimated* solving degree or an *assumed* degree-growth rate; a
subsequent paper computes the actual system's behaviour and the margin moves —
sometimes far. The unifying-view surveys (`KN-LIT-7202`) exist because this
class keeps producing that pattern.

## Program usage

- **This is the closest external analogue to the program's own main-line
  technical problem.** Point-decomposition index calculus reduces the ECDLP to
  solving structured polynomial systems whose solving degree decides the
  exponent (`KN-TECH-003`, `KN-TECH-004`); arithmetization-oriented
  cryptanalysis reduces a cipher to structured polynomial systems whose solving
  degree decides the attack. **The same solvers, the same estimation problem,
  the same failure mode** — an assumed degree of regularity that the structured
  system does not obey. The program's own `KN-FIND-006` (the Macaulay rank
  deficit is bounded structural syzygy content) is a result of exactly the type
  this literature needs and often lacks.
- **It is therefore a source of transferable technique, not just of
  literature.** Methods developed to bound solving degree for round-based
  systems are candidates for adaptation to summation-polynomial systems, and the
  reverse. Any such adaptation is a proposal to be tested under
  `/design-experiment`, not an established transfer — the systems differ in
  structure and field, and nothing here licenses assuming the behaviour carries.
- **The margin-moves pattern is a warning about the program's own extrapolated
  exponents.** `KN-TECH-052` governs fitting exponents from bounded runs; this
  design class is the field's ongoing demonstration of what happens when such a
  fit is treated as a security argument.

## Applicability limits

- **Design-class specific.** Nothing here applies to AES, Keccak or any
  bit-oriented wide-trail design; conversely, trail-counting says nothing useful
  about these primitives.
- **Solving degree is not the same as degree of regularity**, and structured
  systems routinely violate the semi-regularity assumptions under which the
  latter is computed. Estimates in this area carry that caveat by default.
- **Field matters.** `F_p` and `F_{2^n}` behave differently for degree growth,
  for interpolation cost and for division-property analogues; a result over one
  does not transfer to the other.
- **Claimed complexities in this class have historically moved.** Treat any
  single reported solving-degree estimate as provisional unless it is backed by
  a computation on the actual system at the actual parameters.

## Verified vs reported

Governed by `KN-TECH-062`'s sourcing note. The interpolation-attack principle,
the `d+1` reconstruction cost, the round-system Gröbner formulation and the
reason wide-trail arguments do not apply to this design class are standard
published knowledge, written from established knowledge and not re-derived here.
Jakobsen–Knudsen's interpolation paper is named in prose; this corpus holds no
entry for it and no identifier was minted. All cited `KN-LIT` records are
**title-level**: that `KN-LIT-2451` reaches full MiMC is read from its title,
and **no complexity figure from it or from any other record here is quoted or
verified.** The statement that margins in this class have historically moved is
this program's characterisation of the literature, corroborated in this corpus
only by the presence of successive attack papers against the named designs — it
is not a claim any single cited source makes. The parallel to the program's own
index-calculus solving-degree problem, and the suggestion that techniques may
transfer, are this program's own reasoning and are **untested hypotheses**, not
results.
