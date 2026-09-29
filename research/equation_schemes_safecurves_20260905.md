# Equation schemes on the SafeCurves list: what a published curve shape certifies, verified with stdlib arithmetic, and the ideation lane it opens

Session `coordinator-eqschemes-1`, worktree `elliptic-curve-equations-5210ae`,
branch `aburan28/elliptic-curve-equations-5210ae`, 2026-09-05. Seed: the user
instruction "Investigate novel equation schemes" together with the SafeCurves
*Equations* page (version 2013.10.14) pasted into the session; both are stored
verbatim in
`coordination/ideation/equation-schemes-20260905-802f7c/tasks/TASK-20260905-802f7c/context.md`.
Producer handoff for the ideation lane: `TASK-20260905-802f7c`
(coordinator -> idea-generator). Snapshot archive: `TASK-20260905-73ac7e`.
Artifacts: `research/equation-schemes-20260905/` (fetched pages with hashes,
parser, checker, `results.json`, `table.md`).

**What this is.** A recomputation, with Python integers only (no PARI, no
Sage, no network at compute time), of the SafeCurves "equation" criterion and
of the curve-model (equation-scheme) availability structure of all twenty
SafeCurves curves, from pages fetched in this session; and the frame for an
ideation lane on equation schemes as tracked objects, kept disjoint from the
live representation lane BATCH-23ec69.

**What this is not.** Not an attack, not a cost measurement, not a safety or
weakness statement about any curve, not an adjudication of any SCURVE
criterion cell (each belongs to its `GOAL-SCURVE-*` goal), not a novelty
claim, not a validation of any proposal it cites. No ledger status changes.
Claim tier: arithmetic verification of published parameters; nothing above
`toy`.

## 1. Sources and provenance

Fetched live from `https://safecurves.cr.yp.to/` at 2026-09-05T22:58:54Z with
`curl`, stored under `research/equation-schemes-20260905/retrieved-pages/`:

| page | sha256 |
|---|---|
| `safecurves-equation.html` | `035dddc23bedb7754f8b54f1d2601b3a941509ce1d68d2b9537bb9dcb2602c58` |
| `safecurves-field.html` | `bf62f1f141ca35a8e9ad13741944147343693d2d1d504e662153149398b6292a` |
| `safecurves-base.html` | `796397643ebe92985741d71c57f584e6a2a506de83aef20aba64807938933b69` |
| `safecurves-rho.html` | `54bb052de554bb8dd037944a424f2b456811c7ad349d3d37d07eb7d9b3186b6f` |
| `safecurves-twist.html` | `c1c421e7265120b3d9813c5c75f3db184ae514dc48b1484a44d63f3e6a3902c1` |
| `safecurves-disc.html` | `0af34331dd70916cd38fa3f27ac6a2d6518cdcfa7dd44f7e805a7af6bbefab2c` |
| `safecurves-index.html` | `bb6b0a868098d9b1b415fc769c65e9bc854899255545abeffc5b3b1983bd031c` |

Primary source opened in this session (provenance `retrieved`, verified by
`TASK-20260905-802f7c`'s orchestrating session): Bernstein, Birkner, Joye,
Lange, Peters, *Twisted Edwards Curves*, ePrint 2008/013, PDF sha256
`568b8bdd8145bacc46ef4f0601d73a94fccb4e3be0e6ba7d72b6ef68cb64c6d0`, text
extracted with `pdftotext -layout` to `retrieved-pages/eprint-2008-013.txt`.
Theorem 3.2 (line 145 of the text): every twisted Edwards curve is
birationally equivalent to a Montgomery curve and conversely, char != 2.
Theorem 3.3 (line 225): `E(k)` has an element of order 4 if and only if `E`
is birationally equivalent over `k` to an Edwards curve. Section 3 (lines
195-210): on `B y^2 = x^3 + A x^2 + x` the point `(0,0)` has order 2, and
points of order 4 above it exist at `x = 1` iff `(A+2)/B` is a square and at
`x = -1` iff `(A-2)/B` is a square.

Two further primary sources were retrieved from HAL in this session
(provenance `retrieved`, same verifier); the PDFs are not committed, their
hashes and URLs are, and the `pdftotext -layout` extractions are committed
beside them:

- Faugère, Gaudry, Huot, Renault, *Using Symmetries in the Index Calculus for
  Elliptic Curves Discrete Logarithm* (the source of `KN-LIT-004`),
  `https://hal.science/hal-00700555/document`, PDF sha256
  `c7de88521e60143ab60de46221adb5bf608bc39fccbb5350cde8567538ebd7b1`, text
  `retrieved-pages/hal-00700555.txt`. Theorem 1.1 (lines 189-195) is stated
  for `E` over a non-binary field `F_{q^n}` with `n > 1` that can be put in
  twisted Edwards or twisted Jacobi-intersection form, and removes a factor
  `2^(omega(n-1))` from the point-decomposition complexity bound (line 187).
  Lines 251-254, verbatim: "We do not change the very nature of the attack;
  therefore it applies only to curves defined over small extension fields.
  This work has no implication on the ECDLP instances recommended by the
  NIST [42], since they are defined over prime finite fields of high
  characteristic or binary fields of prime degree extension."
- Faugère, Huot, Joux, Renault, Vitse, *Symmetrized summation polynomials:
  using small order torsion points to speed up elliptic curve index calculus*
  (the source of `KN-LIT-6917`),
  `https://inria.hal.science/hal-00935050/document`, PDF sha256
  `57fec77b9c8111a832bfd8f5d0d6b1bed71ae883e34f840a04dedad8e39f93db`, text
  `retrieved-pages/hal-00935050.txt`. Setting: the point decomposition
  problem over `E(F_{q^n})` with the subfield factor base
  `{P : x(P) in F_q}` and its Weil restriction (lines 94-98). Field-
  independent algebra: a morphism `phi: E -> P^1` of degree divisible by `m`
  with `phi o tau_T = f_T o phi`, `f_T` a homography, makes the summation
  polynomial invariant under `(P_i + [k_i] T)` with `sum k_i = 0 (mod m)`
  (lines 120-133); every degree-2 morphism has this property for a 2-torsion
  point (Lemma 6, line 421); the factor base `{P : phi(P) in P^1(F_q)}` is
  then divided by `m`, by 2 more with `[-1]`, by 8 with full 2-torsion,
  against an `m^(n-1)` loss in decomposition probability (lines 344-353); in
  odd characteristic about three quarters of curves with a 2-torsion point
  admit the simplest form of the construction, using a 2-isogeny to a curve
  with a rational 4-torsion point where needed (Remark 9, lines 534-541).

Corpus records read (provenance `internal`; the literature notes are
abstract-level bulk-seeded entries, `citation_verified: read`; the sources of
`KN-LIT-004` and `KN-LIT-6917` were retrieved from HAL in this session, see
below, and no other note was opened beyond the note itself): `KN-OPEN-003`, `KN-OPEN-019`, `KN-OPEN-020`,
`KN-TECH-ee6696`, `KN-LIT-004`, `KN-LIT-6917`, `KN-LIT-439`, `KN-LIT-7284`,
`KN-LIT-7286`, `KN-LIT-4950`, `KN-LIT-828`, `KN-LIT-3013`;
`RQ-ECDLP-623a32`, `RQ-MODEL-e61cb2`, `RQ-ECDLP-002`, `RQ-CRYPTO-001`,
`RQ-SCURVE-d9b7d2`; `IDEA-20260807-dadcd2`, `IDEA-20260807-8027a2`,
`IDEA-20260807-e6d79e`, `IDEA-20260808-2e14f7`, `IDEA-20260811-fe0934`,
`IDEA-20260905-0cc259`, `IDEA-20260905-4dff7b`, `IDEA-20260905-40aa90`,
`IDEA-20260905-7d14f8`, `IDEA-20260905-89e352`; `TASK-20260905-a6ea8a` and
its live claim; `docs/object-frame-ideation.md`. The `crypto-kb` retrieval
index was empty in this session (`:memory:`), so no `kb` provenance exists
here; screening was by reading the records named.

## 2. The invariance principle, and what an equation scheme can change

Every model of a given elliptic curve `E` over `F_p` is `F_p`-birational to
`E`: the rational point set, the group, and therefore the discrete-logarithm
instance are the same. SafeCurves says the same thing about `a = -3`: the
short Weierstrass, Montgomery and Edwards choices are efficiency claims, not
security claims. So a "novel equation scheme" cannot change the cost of a
generic algorithm, and this program's own proposed deck-group law
(`IDEA-20260807-dadcd2`, status `proposed`, not validated) states that on a
prime-order curve every coordinate map `E -> P^1` has an `F_p`-rational deck
group of order exactly 2, so the model lever on the Semaev decomposition
system is exactly 1 there. That is the closure `RQ-ECDLP-623a32` records
("Kummer-line and degree-d-function paradigm closed at model lever 1").

What the equation scheme does carry:

1. **It certifies rational torsion.** A curve can be *written* in a given
   shape over `F_p` only if `E(F_p)` has the torsion that shape needs
   (criteria in section 4). SafeCurves' Montgomery and Edwards curves are
   exactly its cofactor-4 and cofactor-8 curves; its prime-order curves are
   all short Weierstrass because nothing else is available to them over
   `F_p`.
2. **Rational torsion is the resource the symmetrised summation polynomials
   use** (`KN-LIT-004`, `KN-LIT-6917`; sources retrieved, section 1): the
   summation polynomial is invariant under `(P_i + [k_i] T)` with
   `sum k_i = 0 (mod m)` for a torsion point `T` of order `m`, and a
   coordinate invariant under negation and under a cyclic rational torsion
   subgroup `C` of order `k` is the `x`-coordinate of `E/C` pulled back
   through the degree-`k` isogeny, a degree-`2k` map whose rational deck
   group is the dihedral group of order `2k`. In `IDEA-20260807-dadcd2`'s
   notation that is `g = 2k`: the lever the law predicts to be exactly 1 on
   prime-order curves is *not* 1 on the eleven cofactor curves, where `g` in
   {4, 8, 16} is available. Two cautions bound this. First, both papers prove
   their speedups for curves over non-prime fields `F_{q^n}`, `n > 1`, with
   the subfield factor base and its Weil restriction, and the FGHR paper
   states that it has no implication on the NIST instances, which live over
   prime fields of high characteristic; what is field-independent is the
   algebra (the invariance, the equivariant morphism, the factor-base
   division by `m` against the `m^(n-1)` loss in decomposition probability),
   and over `F_p` the subfield factor base does not exist, so any prime-field
   use must supply its own factor base and charge it (`KN-OPEN-020`).
   Second, which way the constant moves at prime-field toy scale is an open
   contrast: the proposed law gives per-variable degree `g^(m-2)`, larger,
   while the literature reports the symmetrised polynomials as more compact
   and sparser at a smaller factor base. Nothing in this note measures that;
   formulating it as a falsifiable proposal is what the ideation lane is
   asked to do. `RQ-MODEL-e61cb2`'s decision target applies unchanged:
   constants and small-`m` behaviour only, no exponent.
3. **Implementation-security properties** (completeness, ladders, twist
   security): SafeCurves' ECC-security criteria, outside the ECDLP-cost
   question and outside this lane.
4. **A verification surface**: model-conversion certificates
   (`IDEA-20260905-7d14f8`, `IDEA-20260905-89e352`), which belong to the
   SCURVE audit lane, not to this one.

## 3. Results: all twenty curves, every check passes

Produced by `research/equation-schemes-20260905/equation_schemes_check.py`
in 0.75 s; raw values in `results.json`.

| curve | shape | h | p mod 4 | E[2] rank | rational torsion | Montgomery | twisted Edwards | Edwards (a=1) | Legendre | Jacobi quartic (recalled crit.) | twisted Hessian (recalled crit.) | deck orders 2k | all checks |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Anomalous | short Weierstrass | 1 | 3 | 0 | trivial | no | no | no | no | no | no | [2] | pass |
| M-221 | Montgomery | 8 | 1 | 1 | Z/8 | yes | yes | yes | no | yes | no | [2, 4, 8, 16] | pass |
| E-222 | Edwards | 4 | 3 | 1 | Z/4 | yes | yes | yes | no | yes | no | [2, 4, 8] | pass |
| NIST P-224 | short Weierstrass | 1 | 1 | 0 | trivial | no | no | no | no | no | no | [2] | pass |
| Curve1174 | Edwards | 4 | 3 | 1 | Z/4 | yes | yes | yes | no | yes | no | [2, 4, 8] | pass |
| Curve25519 | Montgomery | 8 | 1 | 1 | Z/8 | yes | yes | yes | no | yes | no | [2, 4, 8, 16] | pass |
| BN(2,254) | short Weierstrass | 1 | 3 | 0 | trivial | no | no | no | no | no | no | [2] | pass |
| brainpoolP256t1 | short Weierstrass | 1 | 3 | 0 | trivial | no | no | no | no | no | no | [2] | pass |
| ANSSI FRP256v1 | short Weierstrass | 1 | 3 | 0 | trivial | no | no | no | no | no | no | [2] | pass |
| NIST P-256 | short Weierstrass | 1 | 3 | 0 | trivial | no | no | no | no | no | no | [2] | pass |
| secp256k1 | short Weierstrass | 1 | 3 | 0 | trivial | no | no | no | no | no | no | [2] | pass |
| E-382 | Edwards | 4 | 3 | 1 | Z/4 | yes | yes | yes | no | yes | no | [2, 4, 8] | pass |
| M-383 | Montgomery | 8 | 1 | 1 | Z/8 | yes | yes | yes | no | yes | no | [2, 4, 8, 16] | pass |
| Curve383187 | Montgomery | 8 | 1 | 1 | Z/8 | yes | yes | yes | no | yes | no | [2, 4, 8, 16] | pass |
| brainpoolP384t1 | short Weierstrass | 1 | 3 | 0 | trivial | no | no | no | no | no | no | [2] | pass |
| NIST P-384 | short Weierstrass | 1 | 3 | 0 | trivial | no | no | no | no | no | no | [2] | pass |
| Curve41417 | Edwards | 8 | 3 | 1 | Z/8 | yes | yes | yes | no | yes | no | [2, 4, 8, 16] | pass |
| Ed448-Goldilocks | Edwards | 4 | 3 | 1 | Z/4 | yes | yes | yes | no | yes | no | [2, 4, 8] | pass |
| M-511 | Montgomery | 8 | 1 | 1 | Z/8 | yes | yes | yes | no | yes | no | [2, 4, 8, 16] | pass |
| E-521 | Edwards | 4 | 3 | 1 | Z/4 | yes | yes | yes | no | yes | no | [2, 4, 8] | pass |

Checks behind the `pass` column, per curve:

- **E1** the SafeCurves "elliptic?" quantity (`4a^3 + 27b^2`, `B(A^2 - 4)`
  or `d(1 - d)` mod `p`) recomputed from the published equation equals the
  page's value *and* the value in the user-pasted table, and is nonzero.
- **E2** the base point satisfies its native equation; the page's
  conversion formulas (Montgomery `x = Bu - A/3, y = Bv` giving
  `a = (3 - A^2)/(3B^2)`, `b = (2A^3 - 9A)/(27B^3)`; Edwards
  `x = u/v, y = (u-1)/(u+1)` giving `A = 2(1+d)/(1-d)`, `B = 4/(1-d)`)
  carry the base point onto a point of the converted curve, whose
  discriminant is nonzero.
- **E3** the subgroup order `l` passes 40 Miller-Rabin rounds; `#E = h l`
  satisfies Hasse; `p + 1 - #E` equals the page's trace; `l G = O` and, for
  `h > 1`, `h G != O` on the Weierstrass model; the twist order
  `2p + 2 - #E` equals the page's `l' h'`; the page's CM discriminant `D`
  divides `t^2 - 4p` with a perfect-square cofactor.
- **T1** the number of `F_p`-rational roots of the Weierstrass cubic
  (`gcd(x^p - x, f)`, split when needed) gives the rank of `E(F_p)[2]`.
- **T2** for each rational 2-torsion point, whether a rational point of order
  4 lies above it (criterion in section 4), cross-checked against the group
  structure forced by `h` and the 2-torsion rank.

Reading the table:

- The **nine prime-order short Weierstrass curves** (Anomalous, NIST P-224,
  BN(2,254), brainpoolP256t1, ANSSI FRP256v1, NIST P-256, secp256k1,
  brainpoolP384t1, NIST P-384) have trivial rational torsion. No Montgomery,
  twisted Edwards, Edwards, Legendre, Jacobi-quartic or Hessian model exists
  over `F_p`; the only rational deck order is 2. They are the lever-1
  controls of the lane.
- The **six cofactor-8 curves** (M-221, Curve25519, M-383, Curve383187,
  Curve41417, M-511) have `E(F_p)[2^inf] = Z/8` (one rational 2-torsion
  point, halvable), and the **five cofactor-4 curves** (E-222, Curve1174,
  E-382, Ed448-Goldilocks, E-521) have `Z/4`. All eleven have a rational
  point of order 4, hence an Edwards model with `a = 1` (BBJLP Theorem 3.3),
  consistent with SafeCurves publishing every one of them in Montgomery or
  Edwards shape. The six Edwards-shaped curves have non-square `d`, i.e.
  complete Edwards form.
- **No SafeCurves curve has full rational 2-torsion** (so no Legendre model
  and no model needing three rational points of order 2 over `F_p`), and
  **none has `3 | #E`** (so no twisted Hessian model over `F_p`). Those
  shapes exist for these curves only over extension fields.
- `p = 1 (mod 4)` holds exactly for the five Montgomery-shaped curves and
  NIST P-224; the six Edwards-shaped curves and the remaining Weierstrass
  curves have `p = 3 (mod 4)`. This is recorded as a table fact, not read as
  anything.

## 4. Criteria and derivations used

- **Montgomery form.** Let `y^2 = x^3 + a x + b` have a rational root
  `alpha`. Substituting `x -> x + alpha` gives `y^2 = x (x^2 + u x + c)` with
  `u = 3 alpha`, `c = 3 alpha^2 + a`. If `c = s^2` is a nonzero square,
  `x = s X` gives `(1/s^3) y^2 = X^3 + (u/s) X^2 + X`: Montgomery form with
  `A = u/s`, `B = 1/s^3`. Conversely a Montgomery curve has the rational
  2-torsion point `(0,0)` with `c = 1`. So: Montgomery form over `F_p` iff
  some rational 2-torsion point `(alpha, 0)` has `3 alpha^2 + a` a nonzero
  square. (Derived here; the literature statement is `KN-LIT-4950`,
  Bernstein-Lange, *recalled*, not opened.)
- **Twisted Edwards form** iff Montgomery form: BBJLP Theorem 3.2
  (*retrieved*).
- **Edwards form (`a = 1`)** iff a rational point of order 4: BBJLP
  Theorem 3.3 (*retrieved*). **Complete** Edwards form additionally needs
  `d` a non-square (SafeCurves completeness criterion; BBJLP section 3 lists
  the exceptional points of the maps).
- **Order-4 point above `T = (0,0)`** on `y^2 = x(x^2 + u x + c)`: the
  doubling formula gives `x(2Q) = (x^2 - c)^2 / (4 y^2)`, so `2Q = T` iff
  `x(Q)^2 = c`, i.e. `x(Q) = +-s`; then `y^2 = c (2s + u)` at `x = s` and
  `y^2 = c (u - 2s)` at `x = -s`. Hence an order-4 point above `T` exists iff
  `c` is a nonzero square and `2s + u` or `u - 2s` is a nonzero square. On a
  Montgomery curve (`c = 1`, `u = A`) this is BBJLP's `(A +- 2)/B` square
  condition (*retrieved*, lines 195-210), which the script reproduces.
- **Legendre form** `y^2 = x(x-1)(x-lambda)` iff the cubic has three
  rational roots (scale the roots to `0, 1, lambda`): elementary.
- **Jacobi quartic** iff a rational 2-torsion point: *recalled* (Billet and
  Joye, 2003), not opened, not relied on beyond the table column.
- **Twisted Hessian** iff a rational point of order 3: *recalled*
  (Bernstein, Chuengsatiansup, Kohel, Lange, 2015; corpus note
  `KN-LIT-7286` is abstract-level), not opened. Only `3 | #E` was computed.
- **Huff form** was not tabulated: its availability criterion was not
  verified in this session.
- **Group structure from `h` and the 2-torsion rank.** `#E = h l` with `l`
  prime, so `E(F_p)[2^inf]` has order `h` in {1, 4, 8}; rank 1 forces
  `Z/h`, rank 2 forces `Z/2 x Z/(h/2)`; an order-4 point exists iff
  (`h >= 4`, rank 1) or (`h >= 8`, rank 2). The quadratic-residue criterion
  and this structural prediction agree on all twenty curves.
- **Deck order of a torsion-quotient coordinate.** For a cyclic rational
  torsion subgroup `C` of order `k` with quotient isogeny `phi_C: E -> E/C`,
  the map `x o phi_C: E -> P^1` has degree `2k`, its generic fibre is
  `+-Q + C`, and the automorphisms of `E` permuting fibres are exactly the
  group generated by `[-1]` and the translations by `C`, a dihedral group of
  order `2k`, all of it `F_p`-rational. The table's
  `deck orders 2k` column lists `2k` for every cyclic rational torsion
  subgroup: {2} on prime-order curves, {2, 4, 8} on `Z/4` curves,
  {2, 4, 8, 16} on `Z/8` curves.

## 5. The ideation lane this opens, and what it must not touch

`TASK-20260905-802f7c` asks the Idea Generator for four to six proposals on
`RQ-ECDLP-623a32` whose tracked object is an *equation scheme paired with
what it certifies* (rational torsion translations, the isogenies it makes
rational, its automorphisms, Frobenius on the extension where a further
model appears), placed in the trichotomy of `IDEA-20260806-c5d183` and run
through the lossy-projection test against that named operation set. The
eleven cofactor curves are the instance set where `g > 2` is available and
the nine prime-order curves are the lever-1 controls. The lane is disjoint
from BATCH-23ec69 (`TASK-20260905-a6ea8a`, live on branch
`claude/ecdlp-goal-brainstorm-nz3uem`, which owns the R3 exotic
representations), from the SCURVE conversion-certificate proposals, from the
saturation-defect chart proposals under `RQ-MODEL-e61cb2`, and from the
user-supplied Edwards/Hessian and theta drafts of PR #750; each of those is
a nearest neighbour whose delta a proposal must state, never a lens.

## 6. Limits

- Primality of `p` and `l` is probabilistic (40 Miller-Rabin rounds, seeded);
  no certificate was produced. `D` was checked only for divisibility with a
  square cofactor, not for being fundamental.
- Every parameter comes from one source, the live SafeCurves pages, cross-
  checked against the user-pasted table for the twenty E1 values only. The
  program's own SCURVE parameter capsules were not re-parsed (their schemas
  are heterogeneous across the twenty batches); another session's stdlib
  check of the NIST P-224 capsule (`MSG-20260904-95f34f`) agrees with the
  page values used here for that curve.
- `IDEA-20260807-dadcd2` is a proposed law, not a validated one; section 2
  uses it as the program's stated prediction, not as a fact.
- The Jacobi-quartic and twisted Hessian criteria are recalled and unopened;
  Huff was omitted for that reason.
- No cost was measured, no relation searched, no decomposition run. The
  literature's symmetrisation speedups (`KN-LIT-004`, `KN-LIT-6917`) were read
  in the retrieved texts and are extension-field results (section 1); the two
  corpus notes remain abstract-level and were not upgraded here (that is a
  `/curate-knowledge` act). `KN-LIT-439` reports that in characteristic two
  Pollard rho still wins, and `KN-OPEN-001` remains open.

## 7. Reproduction

```sh
cd research/equation-schemes-20260905
python3 parse_safecurves.py > parsed_safecurves.json
python3 equation_schemes_check.py          # prints ALL VERIFICATION CHECKS PASS
shasum -a 256 retrieved-pages/*.html retrieved-pages/eprint-2008-013.pdf
```
