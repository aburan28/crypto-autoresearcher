# Diagnostic methodology for ECDLP transfers

## Purpose and decision vocabulary

Use this methodology to assess whether moving an elliptic-curve discrete-log
problem through a cover, correspondence, restriction of scalars, isogeny,
Jacobian, abelian variety, quotient surface, or lattice representation creates
a useful reduction. A new equation or representation is not itself a reduction.

Classify every obligation as `unknown`, `supported`, `refuted`, or
`not_applicable`, with evidence and scope. Missing evidence is `unknown`, not
failure. Use the following cumulative verdicts:

1. **valid transfer** — map correctness, subgroup preservation, and scalar
   recovery are supported;
2. **algorithmically relevant** — a named destination solver applies to the
   transported subgroup;
3. **modeled advantage** — the complete modeled cost beats the strongest
   applicable source baseline under stated assumptions;
4. **measured advantage** — paired end-to-end measurements support the modeled
   comparison in the tested scope;
5. **novel reduction** — literature and equivalence checks support novelty
   within a stated boundary.

One refuted hard gate rejects the corresponding verdict. Do not collapse these
verdicts into a single score or treat template completion as evidence.

An **abelian surface** has dimension two. A genus-`g > 2` Jacobian is a
`g`-dimensional abelian variety, not an abelian surface. A Kummer surface and an
ordinary Euclidean lattice are not abelian groups; any proposed transfer through
them must name the actual group object carrying the relevant torsion.

## Ground and type the problem

Record the exact source data before assessing a candidate:

- characteristic, base field, extension degree, defining field polynomial or
  prime modulus, element encoding, and subfields;
- curve equation and model, dimension/genus, field of definition, rational-point
  group, subgroup order, cofactor, generator, and target point;
- `field_sha256`, full `curve_uid`, representation identity, candidate identity,
  and workload identity under `docs/curve-identities.md`;
- the best applicable source algorithms and the comparison boundary: classical
  or quantum, cold-start or amortized, hardware, memory, success probability,
  and number of targets.

Distinguish the ambient group from the subgroup

\[
S=\langle P\rangle,\qquad |S|=r,\qquad Q=[x]P.
\]

Type every edge and junction in the proposed path. A common descent path is

\[
E(\mathbb F_{q^n})
\cong \operatorname{Res}_{\mathbb F_{q^n}/\mathbb F_q}(E)(\mathbb F_q)
\xrightarrow{\phi} A(\mathbb F_q)
\dashrightarrow J_C(\mathbb F_q)
\xrightarrow{\text{destination solver}} x.
\]

The first arrow is a rational-point correspondence, not a speedup. The dashed
arrow must be typed as an isomorphism, isogeny, polarized identification,
correspondence, or unsupported aspiration. Preserve the weakest open obligation
on every composed path.

| Transformation | Required certificate |
|---|---|
| Coordinate isomorphism | Forward and inverse formulas, exceptional points, unchanged group |
| Elliptic or abelian isogeny | Homomorphism, kernel, rationality, degree, subgroup restriction |
| Field extension | Embedding and identification of the original subgroup |
| Restriction of scalars | Dimension, rational-point correspondence, arithmetic cost |
| Curve cover | Curve morphism plus induced pullback/pushforward on divisor classes |
| Jacobian correspondence | Cycle or formulas, induced group maps, polarization, working-field descent |
| Characteristic-zero lift | Compatible specialization, not merely existence of a lift |
| Quotient or Kummer surface | Lost sign/phase data, compatible operations, recovery |
| Lattice or decomposition representation | Torsion location, membership, coordinates, signs/phases, reconstruction |

## Hard gate 1: an executable subgroup-preserving map

Require an explicitly computable homomorphism

\[
\iota:S\longrightarrow A(\mathbb F_q)
\]

such that:

1. `iota(P)` and `iota(Q)` are computable without knowing `x`;
2. `iota([a]P) = [a]iota(P)` on the named domain;
3. `ker(iota) intersect S = {0}`; and
4. a destination answer determines `x mod r` and is verified by `[x]P = Q` on
   the source.

For prime `r`, a proved homomorphism with `iota(P) != 0` is injective on `S`.
For composite order, record the image order and recovery of every prime-power
component. Several lossy maps are sufficient only when their combined kernel on
the source subgroup is trivial and the scalar recombination is explicit.

A certificate `R o iota = [m]` with `gcd(m,r)=1` establishes injectivity on
`S`. Identify the proof, field, domain, normalization, exceptional points, and
implementation formulas. Random tests check code; they do not prove the
homomorphism identity.

For a finite separable degree-`d` cover `pi:C -> E`, assess the induced maps

\[
\pi^*:E=J_E\longrightarrow J_C,\qquad
\pi_*:J_C\longrightarrow E,\qquad
\pi_*\pi^*=[d].
\]

Thus `gcd(d,r)=1` is a sufficient subgroup-injectivity certificate. If `r`
divides `d`, compute the actual kernel intersection; the degree alone neither
proves nor refutes preservation. Do not treat a curve map as a pointwise group
embedding into `C`.

## Hard gate 2: cheap algebraic consistency screens

Run these screens before deriving or benchmarking expensive formulas. They are
necessary filters for algebraic transfers, not substitutes for explicit maps.

| Screen | Evidence to record | Refutation condition |
|---|---|---|
| Dimension | Dimensions of every abelian variety and Jacobian | A claimed embedding of the full source factor has a smaller destination dimension |
| Group order | `r`, destination order, multiplicity of the `r`-primary part | `r` does not divide the destination group order |
| Frobenius / Weil polynomial | Exact characteristic polynomials over the working field | The proposed source factor and destination share no compatible isogeny factor |
| Field of definition | Galois action on maps, kernels, and formulas | The claimed base-field map exists only after an unaccounted extension |
| Riemann--Hurwitz | Degree, ramification/different, predicted genus | Genus and ramification data are inconsistent |
| Polarization / Jacobian locus | Polarization type and explicit curve reconstruction | An unpolarized isogeny class is asserted to be a usable Jacobian without support |

For $W=\operatorname{Res}_{\mathbb F_{q^n}/\mathbb F_q}(E)$, $\dim W=n$.
If an algebraic map embeds $W$ as an isogeny factor of $J_C$, the Frobenius
polynomial of $W$ must occur in that
of `J_C` over the relevant rational coefficient field. For a cover over one
field, the source elliptic factor should appear in the Jacobian/Prym
decomposition. A matching polynomial establishes compatibility of isogeny
classes, not an executable map.

For a separable cover of an elliptic curve, Riemann--Hurwitz reduces to

\[
2g(C)-2=\deg R_\pi.
\]

Use the different divisor in wild or inseparable cases. An unramified connected
cover of an elliptic curve remains genus one.

## Hard gate 3: destination-solver applicability

Name the exact destination algorithm and verify every hypothesis against the
image of `S`, not merely against the ambient variety. Record:

- supported object class, field regime, genus/dimension, curve model, cyclicity
  or group-structure assumptions, and heuristic assumptions;
- factor-base definition and exact identity, smoothness model, relation
  generation, duplicate handling, and cost per new independent verified
  relation;
- relation-matrix rank modulo `r`, generation of the relevant `r`-primary
  component, linear-algebra cost, and memory;
- individual-log descent for both transported inputs, scalar recovery, and
  source verification;
- whether a general abelian-variety algorithm applies when the destination is
  not a Jacobian.

Do not infer an algorithm from dimension, genus, a smaller base field, or fast
group arithmetic. If a cited algorithm has cost `q^(alpha+o(1))`, define

\[
\kappa=\log_q r
\]

and use `alpha < kappa/2` only as a first classical exponent screen against a
square-root subgroup algorithm. Recompute both sides for the actual subgroup,
field, hypotheses, and strongest baseline. Equality of exponents leaves
constants, memory, preprocessing, and success probability unresolved.

As one published example, Diem gives expected
$\widetilde O(q^{2-2/g})$ time for fixed-genus degree-zero class groups under
the paper's nonsingular bounded-degree plane-model and cyclicity hypotheses
([source](https://arxiv.org/abs/math/0606607), provenance: `retrieved`,
abstract). For that exact family, the first exponent screen is

\[
2-\frac{2}{g}<\frac{\kappa}{2}.
\]

This screen is neutral at $g=2$ when $r$ has scale $q^2$, fails for an
$r\asymp q$ prime-field subgroup, and can pass after descent from
$\mathbb F_{q^n}$ when $r\asymp q^n$. These are symbolic regime comparisons,
not measured costs or claims about every genus-$g$ solver. Specialized models
can differ: the Tian record cited below describes a cubic-extension transfer to
a genus-three Jacobian with a different destination bound.

Prior work supplies examples, not a universal genus rule: fixed-genus curve
index calculus, small-dimensional abelian-variety index calculus, explicit
cubic-extension cover attacks, and genus-three hyperelliptic-to-plane-quartic
isogenies have different hypotheses and costs. Cite the exact construction and
solver instead of substituting one result for another.

## Representation-specific rejection tests

### Restriction of scalars and covers

Restriction of scalars preserves the rational-point problem while changing its
representation and dimension. Require a second, independently useful edge to a
solver-compatible object. For a split Jacobian `J_C ~ E x B`, identify whether
the transported subgroup remains entirely in the elliptic factor; appending
`B` does not by itself weaken that factor.

For Prym or correspondence constructions, record both induced group maps,
kernel and polarization type. A principally polarized abelian variety still
needs an explicit curve realization if the claimed solver works only in a
Jacobian representation.

### Abelian and Kummer surfaces

A general algebraic surface has no relevant group law until the proposal names
an Albanese, `Pic^0`, Jacobian, Prym, or abelian-surface object. A Kummer surface
`A/{+/-1}` loses sign and supports pseudomultiplication rather than the full
abelian group law. Treat it as an arithmetic or orbit representation until a
compatible walk, collision interpretation, sign recovery, and scalar recovery
are supplied.

### Lattices

An ordinary lattice `Lambda ~= Z^m` is torsion-free, so every homomorphism
`Z/rZ -> Lambda` is zero. A nontrivial proposal must identify torsion in a
finite quotient `Lambda/L`, a torus, an endomorphism-kernel lattice, or a
relation lattice.

If elements of `Lambda/L` arrive as explicit integer-coordinate vectors, audit
whether normal-form computation already exposes their discrete-log coordinates.
If producing those coordinates requires the unknown scalar, the reduction is
circular. A GLV/GLS kernel lattice can accelerate known-scalar multiplication;
it does not reveal an unknown scalar. For a cheap effective automorphism action
with mostly full orbits of size `m`, an ideal rho orbit quotient changes the
expected transition count by about `sqrt(m)`, before canonicalization, cycle,
and per-step costs. Keep this separate from an index-calculus or recovery claim.

## Complete cost comparison

State a falsifiable benefit: cheaper arithmetic, orbit quotient, relation
yield, decomposition geometry, equation solving, linear algebra, individual
logarithm, or reusable preprocessing. Input sparsity is not elimination
complexity.

Use the complete cold-start cost

\[
C_{new}=C_{search}+C_{construction}+C_{map}+C_{preprocessing}
       +C_{relations}+C_{linear\ algebra}+C_{individual\ log}
       +C_{recovery}+C_{verification}.
\]

Include unsuccessful construction attempts, duplicates, timeouts, conversion,
rank updates, data movement, memory, hardware, parallelism, and success
probability. Report setup amortization separately:

\[
C_{amortized}(N)=\frac{C_{reusable\ setup}}{N}+C_{per\ target},
\]

only when the exact setup is reusable across the stated `N` targets. Also
report the cold-start value. Keep measured and modeled columns separate, and
separate exponent changes, constant factors, primitive weights, and hardware
throughput. Follow `docs/progress-fidelity.md` and
`docs/bounds-and-frontiers.md` for any project performance or attack-cost
claim; this methodology creates no such claim.

Compare against every applicable baseline, including Pohlig--Hellman, optimized
parallel rho with source automorphisms, pairing transfer where applicable,
existing Weil descent, and direct decomposition methods. A candidate advantage
requires

\[
\log_2 C_{baseline}-\log_2 C_{new}>U_{model}+U_{measurement},
\]

where the right side records the relevant uncertainty rather than hiding it in
a point estimate; express both uncertainties in bits for this comparison.

## Controls and bounded validation

Use paired instances, fixed budgets, predefined stopping and invalidation rules,
independent seeds/classes, and held-out instances. At minimum include:

1. the strongest direct source baseline;
2. the same generic solver on the transported subgroup;
3. a coordinate-isomorphic destination control;
4. a matched random object with the same field, genus/dimension, and subgroup
   scale;
5. transported data versus data reselected after seeing the destination;
6. null and known-false controls for any structural detector.

Record CPU/NUMA pinning, processor, memory, OS, dependencies, accelerator, exact
commands, revision, seeds, raw output, and validity. Toy arithmetic validates
formulas; it does not establish scaling or a cryptographic advantage.
Infrastructure failures are not mathematical evidence. Route actual trials
through `run`; this assessment profile launches none.

## Novelty and exploration boundary

Novelty is the last gate. Fingerprint a construction by

\[
(fields,\ Weil\ polynomials,\ dimensions,\ map\ type,\ degree,\ kernel,
polarization,\ target\ model,\ solver).
\]

Check twists, field automorphisms, birational models, dual/conjugate isogenies,
factor permutations, reverse paths, and alternative equations for the same
polarized abelian variety. A new equation, coordinate system, or name is not a
new reduction.

Search the repository knowledge base before claiming novelty, prior failure, or
literature obstruction. Record searched sources, queries/families, dates,
parameters, and unavailable material. A defensible novelty statement says only
`not found within <families, sources, parameters, and date>` unless an
independent review supports something stronger.

Possible novelty dimensions include a new source family, smaller target genus
or degree, a new characteristic/extension regime, executable formulas where
only existence was known, a new subgroup-recovery certificate, a better proved
bound, or a measured complete-cost improvement. State which one is asserted.

## Required report

Return:

- the typed correspondence graph and exact identities;
- an obligation table with state, evidence, scope, and weakest open obligation;
- preservation and recovery certificates;
- destination-solver applicability and full cost tables;
- controls, parameter scope, and exploration boundary;
- the narrowest supported verdict, limitations, and one checkable next
  obligation.

Do not recommend an official research-state change without Coordinator
authority and the required independent review. A bounded unsuccessful search
returns `not found within this family and boundary`, never universal
nonexistence.

## Literature anchors

These sources illustrate distinct transfer and solver families; they are not
evidence for a new candidate or a project performance claim.

- Pierrick Gaudry, *Index calculus for abelian varieties of small dimension and
  the elliptic curve discrete logarithm problem* — repository record
  `knowledge/literature/KN-LIT-002.md` (provenance: `kb`).
- Song Tian, *Cover attacks for elliptic curves with prime order* — repository
  record `knowledge/literature/KN-LIT-b4a89c.md` (provenance: `kb`).
- Benjamin Smith, *Isogenies and the Discrete Logarithm Problem in Genus Three*
  — repository record `knowledge/literature/KN-LIT-39d9ed.md` (provenance:
  `kb`).
- Claus Diem, [*Index calculus with double large prime variation for curves of
  small genus with cyclic class group*](https://arxiv.org/abs/math/0606607)
  (provenance: `retrieved`, abstract).
- Victor Shoup, [*Lower Bounds for Discrete Logarithms and Related
  Problems*](https://www.shoup.net/papers/dlbounds1.pdf) (provenance:
  `retrieved`, primary PDF).

