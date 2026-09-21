---
id: KN-TECH-073
type: technique
title: Cube attacks and cube testers - superpoly recovery as key-recovery higher-order differential cryptanalysis
tags: [cube-attack, cube-tester, superpoly, dinur-shamir, higher-order-differential, algebraic-degree, dynamic-cube, conditional-cube, correlation-cube, trivium, grain, keccak, symmetric-cryptanalysis, symmetric, adjacent]
confidence: established
complexity: "summing the output over a cube of dimension k costs 2^k chosen-IV queries and yields the superpoly, of degree at most d - k for a master polynomial of degree d; a linear superpoly gives one linear equation in the key bits, and enough independent ones give key recovery"
applicability: primitives with public tweakable input (IV, nonce, message) and a secret key, where the output bit is a polynomial of exploitably bounded degree in the combined variables; standard against stream ciphers with nonlinear update and against keyed sponge modes
source_refs: [KN-TECH-063, KN-TECH-072, KN-TECH-074, KN-LIT-3344, KN-LIT-3345, KN-LIT-2792, KN-LIT-3091, KN-LIT-4389, KN-LIT-3177, KN-LIT-3178, KN-LIT-3342, KN-LIT-2153, KN-LIT-2087]
added: 2026-07-31
superseded_by: null
---

## Method

Dinur–Shamir (2009, `KN-LIT-3344`) reframe higher-order differentials
(`KN-TECH-063`) as a key-recovery method against black-box polynomials.

Model an output bit as an unknown polynomial `P(k_1..k_m, v_1..v_n)` over `F_2`
in secret key bits and public IV bits. Choose a **cube** `I ⊆ {v_1..v_n}` of
size `k` and write

  `P = t_I · P_{S(I)} + Q`,

where `t_I` is the product of the cube variables, the **superpoly** `P_{S(I)}`
contains no cube variable, and every monomial of `Q` misses at least one. Then

  `Σ_{v ∈ cube} P = P_{S(I)}`  — summing over all `2^k` assignments to `I`.

The sum is a higher-order derivative; the content of the cube attack is that the
derivative is **not** taken far enough to vanish, so what survives is a usable
function of the key. Degree bookkeeping: if `deg P ≤ d` then `deg P_{S(I)} ≤
d − k`, so cube dimension is chosen to drive the superpoly down to degree 1.

**The two phases.**

- **Preprocessing (offline, chooses cubes).** With the key under the attacker's
  control, search for cubes whose superpoly is linear (or low-degree), verify
  with BLR-style linearity tests, and record the superpoly's coefficients.
- **Online.** Against the real key, sum the output over each recorded cube; each
  linear superpoly yields one linear equation in the key bits. Enough
  independent equations give key recovery.

**Cube testers** (`KN-LIT-3345`) drop key recovery and keep the distinguisher:
test the superpoly for a property a random polynomial would not have — balance,
degree, presence or absence of specific monomials, constancy. Cheaper, and
usually reaches more rounds.

**The variant family, each fixing a different limitation.**

- **Dynamic cube attacks** (`KN-LIT-2792`): choose the non-cube public variables
  *as functions of the cube variables* to nullify state bits, simplifying the
  polynomial before summation. This is what broke Grain-128 in its reported
  form.
- **Conditional cube attacks** (`KN-LIT-3091`): impose conditions that stop
  chosen cube variables from multiplying together early, keeping the degree low
  for extra rounds. The standard tool against round-reduced keyed Keccak modes,
  with cube selection itself delegated to MILP (`KN-LIT-4389`, `KN-TECH-076`).
- **Correlation cube attacks** (`KN-LIT-3178`, `KN-LIT-3177`): exploit a
  *probabilistic* relation between the superpoly and key expressions when no
  exact linear superpoly is available.
- **Cube-attack-like cryptanalysis** of sponge modes (`KN-LIT-3342`), and
  side-channel-assisted variants with error tolerance (`KN-LIT-2153`).

**The scaling barrier and its removal.** Cube dimension is limited by the `2^k`
query cost and, more restrictively, by the need to *know* the superpoly — which
originally meant computing it experimentally. Division-property methods
(`KN-TECH-074`) recover superpolies for cubes far too large to evaluate by
experiment, and that combination produced the deepest published results in this
line, such as key recovery on 855-round Trivium (`KN-LIT-2087`).

## Program usage

- **The tightest available example of "a distinguisher exists" versus "the
  distinguisher is computable".** A cube sum is a well-defined quantity for any
  cube; what limits the attack is knowing the resulting superpoly. That is the
  same distinction the program draws between an object existing and a
  certificate for it existing (`docs/claims-and-verification.md`), and the same
  gap `KN-FIND-008` recorded on the lifting side — rare-event density gates are
  settled exactly by fibering over solutions, once you can enumerate them.
- **Keyed-Keccak relevance is real and bounded.** Conditional cube attacks are
  the live line against round-reduced keyed Keccak modes, and Keccak underlies
  every hash and expansion in FIPS 203/204. **The published results in this
  corpus are round-reduced**; nothing recorded here affects the standardised
  parameter sets.
- **Preprocessing is a cost.** The offline cube search is often the dominant
  expense and is charged, not discounted, under `KN-TECH-035`.

## Applicability limits

- **Public tweakable input is required.** No IV/nonce/message freedom, no cube.
- **Degree must be bounded and known**, or the superpoly is unpredictable; that
  is exactly what `KN-TECH-074` supplies, and without it cube selection is
  experimental and shallow.
- **`2^k` is a hard query cost** in the online phase, and the data limit of the
  target caps `k` regardless of what preprocessing found.
- **Preprocessing assumes key-controlled access**, which is a modelling
  assumption about the attacker, not a property of the primitive.
- **Superpoly linearity is fragile.** A superpoly linear for one cube is
  generally not for a neighbouring one, and reported attacks depend on specific
  cubes found by search, which is why reproducibility of the search matters as
  much as the attack.

## Verified vs reported

Governed by `KN-TECH-062`'s sourcing note. The cube decomposition, the
`Σ_{cube} P = P_{S(I)}` identity, the `deg ≤ d − k` bound and the
preprocessing/online split are standard published results, written from
established knowledge and not re-derived here. `KN-LIT-3344` and `KN-LIT-3345`
are the corpus's records for the originating papers, carried at **title level**.
Attributions of technique-to-target — dynamic cubes to Grain-128, conditional
cubes to Keccak, 855 rounds to Trivium — are read from the **titles** of
`KN-LIT-2792`, `KN-LIT-3091` and `KN-LIT-2087`, which name them explicitly; **no
complexity figure from any of those papers is quoted, and none was verified.**
The comparison to `KN-FIND-008` and to the program's certificate rule is this
program's own reasoning.
