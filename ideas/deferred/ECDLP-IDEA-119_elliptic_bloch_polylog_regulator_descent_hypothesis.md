# ECDLP-IDEA-119 — Elliptic Bloch-polylog regulator descent

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- Top lane: `high-risk`
- State: `deferred_regulator_source_inverse_required`
- Cohort: `20260717-f`
- Evidence scale: no run; any future regulator preflight is `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; constructing a Bloch symbol, regulator value, functional
  equation, valid relation, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

For a declared generic family of ordinary prime-field curves with public prime-order
subgroup `<P>` of order `N=p^(1+o(1))`, there is a finite, public, computable quotient of
an elliptic Bloch-Suslin/polylogarithmic complex and a marked-point map `b:E(F_p)->C_E`
with two properties. First, its boundary verifies every accepted symbolic identity as an
elliptic relation on the original `E`. Second, a regulator-residue word has an exact,
scalar-blind inverse to sparse target-independent factor-base atoms. This inverse generates
`B+sigma` exact source rows of rank `B`, all verified factor logs, and blind
`Q+[t]P` descent. Construction, regulator evaluation, atom output, relation collection,
linear algebra, descent, verification, and peak memory all have exponents below `1/2`.

## Mechanism-new operation

The operation is **reduce a marked elliptic Bloch/polylogarithmic class through finite
regulator residues to sparse factor-base atoms, invert those atoms to exact point sources,
and verify the identity through the Bloch boundary on `E`**. The claimed inverse must be
defined before relation collection, return source indices/signs/multiplicities, and expose
all kernel ambiguity.

A formal five-term functional equation, complex or p-adic regulator value, equality in a
quotient, `K_2`/motivic certificate, ordinary divisor relation, or target-specific symbol
chosen after a known relation is only a duplicate or control. The mechanism is new only
if the finite regulator has a public exact atom inverse that reduces source-generation
cost; relation validity alone is explicitly insufficient.

## Assumptions

1. `E(F_p)` has public prime-order subgroup `<P>` of order `N=p^(1+o(1))`, target
   `Q=[x]P`, and target-independent factor base
   `F={F_1,...,F_B}` with `B=N^beta`.
2. The elliptic Bloch/polylogarithmic complex, coefficient modulus or moduli, marked-point
   map, boundary, regulator residues, and exceptional symbols are defined uniformly and
   computably over the declared finite-field family.
3. The product of residue moduli and all torsion/kernel ambiguity are large enough to
   separate accepted atom words without secretly encoding `log_P` values.
4. Every accepted atom word inverts to exact factor-base points, signs, multiplicities,
   and a boundary identity verifiable on the original curve.
5. Factor-base selection, regulator setup, and atom dictionaries are target-independent;
   `Q` appears only in masked blind descent.
6. Symbol height, field extensions, torsion, kernel enumeration, functional-equation
   search, output, misses, rank, linear algebra, verification, and memory are charged.
7. All finite observations remain toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`elliptic_Bloch_Suslin_complex | finite_polylog_regulator_residues | marked_point_symbol | sparse_atom_reduction | exact_atom_to_point_inverse | boundary_verified_blind_descent`

The exact regulator-atom-to-point inverse is load-bearing. A scalar-sensitive invariant
without that inverse, or a relation certificate discovered by ordinary search, does not
instantiate the mechanism.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1051`, where tested low-degree
   public-coordinate and coefficient identities do not generate an accepted relation;
   the proposed motivic functional equation must instead generate exact point sources.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1479`, where tested public linear
   feature spaces do not contain factor logs; a regulator quotient is distinct only if
   its nonlinear atom word has an exact source inverse.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-MX-1478`, where a compact exact local
   norm identity becomes dense on composition; the proposed atom reduction must remain
   compositional without an `L^2` state object.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-RT-1476`, which gives the full
   relation/linear-algebra/descent exponent boundary that any regulator source inverse
   must satisfy.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1470`, where one-large-prime
   arithmetic and target descents replay exactly but remain expensive; this proposal must
   change source-generation cost rather than merely certify correctness.

## Closest primary literature

- Goncharov and Levin,
  [Zagier's conjecture on `L(E,2)`](https://arxiv.org/abs/alg-geom/9508008),
  introduce an elliptic analogue of the Bloch-Suslin complex over an arbitrary field and
  relate it to weight-two `K`-groups; they do not construct a finite-field DLP coordinate
  or source inverse.
- Bloch,
  [Higher Regulators, Algebraic K-Theory, and Zeta Functions of Elliptic Curves](https://bookstore.ams.org/crmm-11),
  develops elliptic regulator and `K_2(E)` structures; it does not give the required
  scalar-blind finite-field atomization algorithm.
- Beilinson and Levin, *The elliptic polylogarithm*, in
  [Motives, Part 2](https://bookstore.ams.org/PSPUM/55.2), construct the elliptic
  polylogarithm in a motivic setting; they do not prove a sub-rho factor-base source
  decoder.

No checked source supplies a finite regulator quotient with exact point-source inversion.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B`, coefficient moduli, elliptic Bloch complex, marked-point map,
   boundary, regulator residues, atom normal form, exceptional symbols, and independent
   source verifier.
2. Compute every factor-base atom `b(F_i)` and certify that construction uses point data
   only; record all coincident atoms, torsion, kernels, and failed symbols.
3. For known public random sums `R_j=[r_j]P`, form `b(R_j)`, reduce it through the frozen
   functional equations and regulator residues, invert every accepted atom word to exact
   points in `F`, and verify both its complex boundary and elliptic sum.
4. Preserve misses, kernel branches, duplicate atomizations, and dependencies; collect
   exactly `B+sigma` verified source rows whose coefficient matrix has rank `B` modulo
   `N`.
5. Solve all factor-base logarithms and independently verify
   `[log_P(F_i)]P=F_i` for every `i`.
6. Freeze all regulator state, select fresh public masks `t`, and apply the identical
   marked-symbol reduction and exact atom inverse to blind targets `Q+[t]P`.
7. Substitute verified factor logs, subtract `t`, enumerate every regulator-kernel scalar
   candidate, and accept only `x` satisfying `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected group operations with constant-state memory;
BSGS costs `N^(1/2+o(1))` time and memory. Let `B=N^beta`. Let complex, coefficient,
modulus, regulator, and atom-normal-form setup cost `N^(a+o(1))` time and
`N^(a_m+o(1))` peak memory. Let one complete marked-symbol reduction plus exact atom
inverse cost `N^(q+o(1))` time and `N^(q_m+o(1))` memory before output. Let accepted
source tuples written per attempt have exponent `o`, residual regulator/kernel scalar
ambiguity have exponent `u`, and one complete source/scalar verification cost
`N^(v+o(1))` time and `N^(v_m+o(1))` memory. Let reciprocal accepted-relation and blind
target success probabilities be `N^delta` and `N^delta_t`. Let factor-log linear algebra
cost `N^(ell_LA+o(1))` time and `N^(m_LA+o(1))` memory, with
`ell_LA>=2beta` absent a proved stronger structure.

Collecting `B+sigma` rows has time exponent

`beta+delta+q+o+v`,

and blind descent has exponent

`delta_t+q+o+u+v`.

The fully charged exponents are therefore

`lambda=max(a,beta+delta+q+o+v,ell_LA,delta_t+q+o+u+v)`

and

`mu=max(a_m,q_m,m_LA,beta+o,o+u,v_m)`.

The `B+sigma` sparse rows, all factor atoms/logs, regulator words, kernel branches,
emitted sources, and scalar candidates are explicit output. Complex/modulus construction,
coefficient bit lengths, extension fields, functional-equation searches, failed
reductions, and verifier work are included. A regulator table or atom dictionary of size
`N^c` contributes exponent `c` even if each lookup is constant time.

## Likely fatal obstruction

Over finite fields the relevant regulator targets can be torsion, too small, or trivial,
and motivic functional equations generally identify classes without providing a unique
factorization into marked point atoms. Any quotient large enough to separate a prime-order
subgroup may encode the original discrete logarithm, while inverting a regulator word can
be the same incidence search in another language. The boundary can verify a relation
after discovery without making its sources cheaper to find.

## Proof track

Construct the finite quotient and regulator uniformly, prove scalar-blind point mapping,
exact sparse atom/source inversion, complete boundary verification, and sub-rho setup,
density, output, linear-algebra, blind-descent, and memory bounds for all seven steps.

## Disproof track

Prove the finite regulator is trivial or too small, exhibit distinct source tuples with
the same complete regulator word, show that atom inversion needs a source-sized table or
the DLP, or derive complete time or peak-memory exponent at least `1/2`.

## Positive and negative controls

- Positive motivic control: published elliptic Bloch-complex identities with independently
  verified boundaries over a supported exact field.
- Positive atom control: a planted finite symbolic complex with known sparse atoms and a
  blinded exact inverse.
- Negative controls: ordinary divisor relations, random group symbols, regulator-kernel
  collisions, and symbols with equal regulator value but different boundary.
- Mechanism controls: Miller/S-unit relations, tame symbols, linear feature compression,
  P1478 norm identities, and post-hoc symbol assignment to already found relations.
- Leakage control: permute factor-base scalar labels while preserving point and regulator
  data; accepted atoms must track points without logs.
- Baseline control: matched Pollard rho and memory-matched BSGS.

## Quantitative promotion and falsification gates

No run is admissible before a theorem constructs the finite regulator quotient, proves
the marked-point/boundary biconditional and exact atom/source inverse, and derives
`lambda,mu<=0.45`. A future toy preflight must cover at least 20 ordinary curves at each
of four increasing sizes, exhaustive symbol/source truth through 18 bits, at least
`1,000` verified relations and `100` blind descents at each of the two largest sizes,
exactly `B+sigma` retained rows of rank `B`, zero source or boundary errors, and upper 95%
bounds `lambda<=0.45` and `mu<=0.45`. Falsify on one reproducible false source/boundary,
regulator collision with no public disambiguator, or a proved or lower-95% complete bound
`lambda>=0.50` or `mu>=0.50`.

## Artifact plan

- Regulator/source-inverse theorem gate: `ideas/artifacts/ECDLP-IDEA-119/regulator_source_inverse_gate.md`
- Frozen complex specification: `ideas/artifacts/ECDLP-IDEA-119/bloch_complex.yaml`
- Prospective regulator reducer: `ideas/artifacts/ECDLP-IDEA-119/regulator_reduce.sage`
- Independent boundary/source verifier: `ideas/artifacts/ECDLP-IDEA-119/verify_regulator_sources.py`
- Prospective receipts: `ideas/artifacts/ECDLP-IDEA-119/runs/<run-id>/`
- Complete analysis: `ideas/artifacts/ECDLP-IDEA-119/analysis.md`

## Interpretation boundary

This deferred record is toy, heuristic, model-bound, and novelty-unverified. A valid
Bloch symbol, polylogarithm value, regulator identity, boundary relation, full-rank toy
matrix, verified factor log, or recovered toy scalar is not a better-than-rho result or a
breakthrough. Only an exact public regulator-atom source inverse and complete charged
blind-descent path could reopen promotion.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-119/regulator_source_inverse_gate.md` constructing one finite regulator quotient and proving either an exact marked-atom-to-point inverse with symbolic `lambda,mu<=0.45` or an explicit regulator collision/circularity obstruction.
