# ECDLP-IDEA-129 — Cross-characteristic Lubin-Tate linearizer

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- Top lane: `representation-changing`
- State: `rejected_scoped_formal_log_torsion_no_go`
- Cohort: `20260717-g`
- Evidence scale: zero run; any future cross-characteristic preflight is `toy`
- Contract posture: retired zero-run theorem contract; execution is not authorized
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a formal-module lift, torsion point, formal logarithm,
  compatible toy orientation, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Given an ordinary `E/F_p` with public prime-order subgroup `<P>` of order `N`, the proposed
operation attempted to globalize the marked subgroup to residue characteristic `N`, place
it in `N`-primary Lubin-Tate torsion, and use the characteristic-zero formal logarithm as a
faithful additive scalar coordinate. That load-bearing claim is impossible on the
logarithm's convergence domain: for an `N`-torsion point `T`,

`0=log_F([N]_F T)=N*log_F(T)`,

and the characteristic-zero additive target is torsion-free, so `log_F(T)=0`. Outside the
convergence domain the formal logarithm is not the claimed evaluator. The record is
therefore a scoped rejection with no run. A nonlogarithmic operation based on ramification
or Galois digits would have a different semantic fingerprint and requires a new idea ID.

## Mechanism-new operation

The proposed operation is **globalize the marked finite-field elliptic subgroup to a place
of residue characteristic `N`, identify it with `N`-primary Lubin-Tate torsion, and evaluate
the formal-module logarithm as a public additive scalar coordinate**. This changes residue
characteristic rather than applying a same-field isogeny or a local formal logarithm at
the original characteristic `p`.

The exact operation is closed: a characteristic-zero additive formal logarithm annihilates
all torsion on its convergence domain. Ramification breaks, field-of-norms digits, Galois
characters, or other nonlogarithmic torsion data are not repairs to this fingerprint; they
must be registered under a new ID and independently deduplicated.

Random lifts, choosing a torsion basis using a known scalar, same-field formal-group jets,
pairing orientations, explicit `N`-torsion tables, or post-hoc normalization are
duplicates/controls. The bridge must be functorial in public marked points and expose every
choice, extension, kernel, and precision cost.

## Assumptions

1. `E(F_p)` contains public prime-order `<P>` of order `N=p^(1+o(1))`, target `Q=[x]P`,
   fixed arity five, and target-independent sign-canonical factor base
   `F={F_1,...,F_B}` with `B=L=N^ell`.
2. A number/global field model with marked `E,P` and a place `v` of residue characteristic
   `N` is constructed canonically from public data, with bounded degree and coefficient
   height.
3. A Lubin-Tate formal module at `v` contains a canonical marked image of `<P>` and its
   logarithm is evaluable at the required torsion precision.
4. Normalizing the image of `P` to one is public and does not require an `N`-torsion basis,
   hidden scalar, discrete logarithm, or `N`-scale advice.
5. The coordinate is faithful on all factor points and blind targets, and every lift,
   Galois, ramification, and torsion ambiguity is enumerated and verified back on `E`.
6. Globalization, extension arithmetic, precision, source output, relation collection,
   linear algebra, descent, verification, and peak bit memory are fully charged.
7. All finite observations remain toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`cross_characteristic_marked_globalization | residue_characteristic_N_place | Lubin_Tate_N_primary_formal_module | additive_torsion_logarithm | public_scalar_coordinate`

The public marked globalization and scalar coordinate are jointly load-bearing. A formal
logarithm on an unrelated local disk or a coordinate normalized with a secret torsion basis
does not instantiate the mechanism.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ISO-AR-NR-004`, where scalar-normalized random
   lifts or random-basis sampling do not give a uniformly efficient compatible lift; the
   cross-characteristic marked lift must remove that obstruction algebraically.
2. `ledger/FINDING-PF-IC-001.md` — imported `ISO-SP-001`, where Frobenius/distorted Weil
   self-pairings study cyclic torsion orientation; the proposed coordinate is distinct only
   if it avoids the same hidden-basis problem.
3. `ledger/FINDING-PF-IC-001.md` — imported `OFQ-autolab-05`, which asks whether
   repeated-prime orientation can avoid full torsion-field and torsion-basis costs; those
   costs must be explicit here.
4. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-H003`, where exact trace-fiber
   collapse remains weighted search; a local additive coordinate must return exact sources
   rather than only reduce multiplicity.
5. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-045`, where an auxiliary elliptic
   factor does not yield a useful native-prime transfer without an explicit correspondence;
   the marked globalization is precisely the missing correspondence theorem.

## Closest primary literature

- Lubin and Tate,
  [Formal complex multiplication in local fields](https://www.mathnet.ru/eng/mat456),
  construct formal modules whose torsion generates abelian local extensions; they do not
  globalize an arbitrary finite-field elliptic DLP subgroup into a public scalar coordinate.
- Lubin and Tate,
  [Formal moduli for one-parameter formal Lie groups](https://www.numdam.org/item/?id=BSMF_1966__94__49_0),
  develop deformation/moduli structure for one-parameter formal groups; they do not prove
  a scalar-blind cross-characteristic marked-point bridge.

No checked primary source supplies the required globalization, public normalization, and
fully charged better-than-rho coordinate evaluation.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B=L`, the global marked model, place `v`, Lubin-Tate module, torsion
   field, precision, normalization, inverse map, exceptional branches, and an independent
   verifier on the original `E`.
2. Construct the marked globalization target-independently and certify the images of
   `P` and every `F_i`; record degrees, heights, ramification, basis choices, kernels, and
   failed specializations.
3. For known public `R_j=[r_j]P`, map `R_j` to the formal module, evaluate the normalized
   logarithmic coordinate, convert it through the frozen factor-base source inverse to
   exact signed five-point tuples, and independently verify every elliptic sum.
4. Preserve misses, lift collisions, Galois branches, and duplicate source words; collect
   exactly `B+sigma` verified rows whose coefficient matrix has rank `B` modulo `N`.
5. Solve every factor-base logarithm and independently verify
   `[log_P(F_i)]P=F_i` for all `i`.
6. Freeze the globalization and all local state, choose fresh public masks `t`, and apply
   the identical map, coordinate, and source inverse to blind targets `Q+[t]P`.
7. Substitute verified factor logs, subtract `t`, enumerate every lift/torsion scalar
   candidate, and accept only `x` satisfying `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected group operations with constant-state memory;
BSGS costs `N^(1/2+o(1))` time and memory. Set `B=L=N^ell`. Let marked globalization,
the place, torsion field, Lubin-Tate module, normalization, and factor-source setup cost
`L^(s+o(1))` time and `L^(s_m+o(1))` peak bit memory. Let one complete lift, local
coordinate evaluation, all ambiguity/source output, and original-curve verification cost
`L^(alpha+o(1))` time and `L^(m_q+o(1))` memory.

Unless a theorem proves a changed density, use `pi=min(1,L^5/N)`. In the sparse regime,

`T_rel=N*L^(alpha-4+o(1))`

and

`T_desc=N*L^(alpha-5+o(1))`.

Sparse linear algebra costs `L^(2+o(1))` time and at least `L^(1+o(1))` memory. Thus

`lambda=max(s*ell,1+(alpha-4)*ell,2*ell,1+(alpha-5)*ell)`

and

`mu=max(s_m*ell,m_q*ell,ell)`

At `ell=1/5`, strict time below rho requires `alpha<3/2`; promotion
`lambda,mu<=0.45` requires `alpha<=1.25` and `s,s_m,m_q<=2.25`. Global degree and
height, a torsion extension of degree `d`, discriminants, ramification, basis conversion,
`N`-adic precision, all Galois branches, failed lifts, source output, factor logs, and
verification are charged; if `d=N^(c+o(1))`, exponent `c` enters setup and memory.

## Likely fatal obstruction

The fatal obstruction is exact, not heuristic. For a one-parameter formal group `F` over a
characteristic-zero field and any torsion point `T` inside the formal logarithm's
convergence domain, homomorphism compatibility gives
`N*log_F(T)=log_F([N]_F T)=0`; torsion-freeness of the additive field forces
`log_F(T)=0`. Thus the logarithm cannot distinguish, orient, or invert nonzero
`N`-torsion. In addition, the original subgroup is prime-to-`p` torsion on `E/F_p` and has
no canonical marked connection to an `N`-primary Lubin-Tate module at another residue
characteristic. These secondary globalization and torsion-basis costs reinforce but are
not needed for the no-go.

## Proof track

The proof track for this exact fingerprint is complete at the no-go level: formalize the
convergence-domain assumptions and the equality
`log_F([N]_F T)=N*log_F(T)=0`, then verify that every torsion point maps to zero. Any
purported counterexample must identify which hypothesis of the formal logarithm it
abandons; abandoning additivity or the logarithm creates a different mechanism and ID.

## Disproof track

Independently check the formal-log identity over exact small Lubin-Tate examples and reject
the candidate on universal zero output. Separately document that points outside the
convergence domain do not provide the claimed logarithmic coordinate and that analytic
continuation cannot be a nonzero homomorphism from finite torsion to a torsion-free
additive characteristic-zero group.

## Positive and negative controls

- Positive formal-log control: a nontorsion point in a convergence disk with a supplied
  parameter, verifying `log_F([a]_F U)=a*log_F(U)` exactly where defined.
- Positive globalization control: tiny marked curves where every global lift and torsion
  branch is exhaustively enumerated and independently reduced back to `E`.
- Negative controls: exact nonzero Lubin-Tate torsion, random global lifts, randomized
  torsion bases, wrong residue places, and noncanonical Galois conjugates; every torsion
  logarithm must be zero.
- Mechanism controls: same-field isogenies, Serre-Tate/formal jets at `p`, pairings,
  explicit torsion tables, scalar-normalized lifts, and post-hoc basis choices.
- Leakage control: permute hidden scalar labels while preserving all public point data;
  globalization and coordinate choices must remain invariant.
- Baseline control: matched Pollard rho and memory-matched BSGS including extension-field
  arithmetic in base-field-equivalent operations.

## Quantitative promotion and falsification gates

The retired zero-run contract authorizes no experiment because the load-bearing logarithmic
coordinate is identically zero on torsion. This ID cannot reopen by changing globalization,
precision, parameters, or torsion basis. Reopening would require a proof that the proposed
map is simultaneously the characteristic-zero formal logarithm, additive on `N`-torsion,
and nonzero, which contradicts the displayed identity. A nonlogarithmic ramification/Galois
digit proposal must receive a new ID, full deduplication, its own source inverse, and
symbolic `lambda,mu<=0.45` before any run. The scoped candidate is falsified by any nonzero
torsion instance, since its predicted public coordinate is always zero.

## Artifact plan

- Globalization/coordinate theorem gate: `ideas/artifacts/ECDLP-IDEA-129/globalization_gate.md`
- Frozen marked model: `ideas/artifacts/ECDLP-IDEA-129/marked_global_model.yaml`
- Prospective local coordinate evaluator: `ideas/artifacts/ECDLP-IDEA-129/lubin_tate_coordinate.sage`
- Independent lift/source verifier: `ideas/artifacts/ECDLP-IDEA-129/verify_globalized_sources.py`
- Prospective receipts: `ideas/artifacts/ECDLP-IDEA-129/runs/<run-id>/`
- Complete analysis: `ideas/artifacts/ECDLP-IDEA-129/analysis.md`

## Interpretation boundary

This scoped rejected record is toy, heuristic, model-bound, representation-changing, and
novelty-unverified. A globalization, Lubin-Tate module, torsion lift, or formal logarithm is
not a better-than-rho result or a breakthrough. The formal logarithm is zero on torsion and
cannot be promoted as a scalar coordinate. Any nonlogarithmic ramification/Galois digit
bridge is a new mechanism requiring a new ID.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-129/globalization_gate.md` as a zero-run theorem note proving `log_F([N]_F T)=N*log_F(T)=0` for every in-domain `N`-torsion point and recording that any nonlogarithmic ramification/Galois digit operation requires a new ID.
