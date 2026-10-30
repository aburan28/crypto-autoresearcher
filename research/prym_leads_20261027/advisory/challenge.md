# Advisory challenge to the nine Prym branches

TASK-20261027-9b59b9. Advisory synthesis only: no scientific review, official decision, promotion, new trial, new source/target sample or discrete-log table. The root task owns archive and the visual/PDF report. The machine-readable companion is [ranking.json](ranking.json).

## The decisive missing interface

The most material objection is the absence of a public algorithm taking a prescribed Q and returning a certified equation

    beta*k + alpha = v dot z  (mod r),  beta != 0 (mod r),

where v belongs to the retained rowspace and all acquisition costs are charged. For consistent Mz=b, the functional v dot z is determined exactly when v annihilates ker M. This is a standard linear-algebra criterion. It verifies a supplied v; it does not find a decomposition of Q. Choosing v in rowspace and then constructing its known-log point reverses the required interface. A planted known-witness target checks correctness, not natural target descent.

The distinction also applies to a source-labelled constructor: cancellation in the auxiliary factor may return an elliptic point whose scalar is unknown. Norm cancellation is not public source return. The existing [router problem](../../../problems/prym-assisted-source-labelled-router.md) already names this gap; this advice does not resolve or close it.

## What the retained matrices actually say

These are **exploratory post-data finite deductions**, independently recomputed from [RUN-ECDLP-967315 raw data](../../../experiments/EXP-ECDLP-a9b6a5/runs/RUN-ECDLP-967315/raw-result.json.gz), with standalone modular elimination and no producer import. The gzip SHA-256 is `2c957d3bd2c51fb86191db998dec4f2df49a98355a400c660a321ae6718948da`; decompressed bytes hash to `8f3d5b98b91b01dab9694e3a4c59a4559dbd7bcfa1cb7c4a3045475948fdb007`. Column indices below are zero-based in `projection.unknown_points`; the publicly known P anchor has already been removed.

| Fixed curve | Retained rows | Distinct coefficient/affine rows | Rank/U | Kernel dimension | Identifiable unit vectors | Co-support components |
|---|---:|---:|---:|---:|---|---|
| p4099, A2, B13, r4021 | 97 | 13/13 | 13/15 | 2 | none | one, all 15 columns |
| p4099, A2, B16, r4111 | 67 | 9/9 | 9/15 | 6 | none | one, all 15 columns |

The kernel reconstructed from RREF agrees exactly with the retained basis. Its rank is 2/6, every M*K-transpose product is zero, and augmented ranks remain 13/9. The unit-vector result was checked both by kernel coordinates and by appending each e_j to M and recomputing rank. Thus none of the fifteen individual projected atom logs is determined by these equations alone. The earlier known anchor remains publicly known; it is outside these fifteen columns.

A support-component explanation alone fails. Both co-support graphs are connected, and their all-ones component indicator is not a kernel vector. A bipartite matching between retained rows and nonzero columns has size 15 in each case, so the full zero/nonzero pattern itself has structural rank 15. The coefficient equalities between repeated rows matter. On deduplication there are exactly 13/9 distinct supports and rows, all independent; there is no further dependency among the distinct equations. Duplication and limited equation diversity therefore account numerically for the finite ranks. A constructor-wide reason for those exact signatures remains an open derivation. A model that explicitly retains these duplicate-equality constraints can explain the data, but that uses more information than support connectivity.

In each matrix all 225 projective signed directions of support at most two (15 units and e_i plus/minus e_j) fail the annihilator test. This does **not** extend to arbitrary coefficients. Testing proportional kernel columns gives exactly one projective support-two direction in each field:

- B13: `v=e_0+310*e_12`, and the existing affine equations imply `v dot z=1599 (mod 4021)`.
- B16: `v=e_1+2*e_5`, and the existing affine equations imply `v dot z=60 (mod 4111)`.

The JSON records the support matchings and sparse functional certificates. These are known linear combinations of existing equations, not individual logs, new targets or new relations from a trial. Arbitrary coefficients may be expensive to realize through a natural bounded-degree divisor constructor. Their existence demonstrates why rank deficiency and a failed signed-pair scan do not reject every possible target functional.

Permuting all retained rows preserves final rowspace; source order can change prefix rank and work scheduling. Replacing sources or collecting another schedule would be a new experiment. Complete tuple support here means only the frozen 64 public sources, fixed cubic constructor, fixed base/charts and two selected curves. The known m8 zero-row cases motivated selection; there is no fresh-curve prevalence inference, universal exhaustion or speedup inference.

## Recommended order and cheapest discriminating obligations

The ranking values information per immediate cost and dependency unlock, not a probability of finding an attack.

| Rank | Branch | Cheapest next discriminator | What would invalidate the tempting inference |
|---:|---|---|---|
| 1 | KERNEL | Explain the 13/9 distinct affine signatures from the constructor; check a proposed invariant against all retained rows. | Connected support is not rank; post-data fitted kernels are not universal invariants. |
| 2 | TARGET | Specify the public Q-to-equation interface with nonzero beta and a row-combination certificate. | Picking v and generating its known point does not invert a prescribed Q. |
| 3 | FUNCTION | Complete the regular x=0/projective companion boundary as a separate frozen arm; audit the existing function-space chart before changing D. | Removing guards alone breaks alias/identity semantics; a completed chart is still fixed-family measurement. |
| 4 | PARTIAL | Define a signed packet/cycle certificate retaining outside identities, both residuals and target coefficients modulo r. | Many cycles can be duplicate or zero-Q; one-component cancellation is insufficient. |
| 5 | MULTICOVER | Symbolically construct distinct covers of the same E and an exact common norm-atom dictionary. | Unrelated E curves, native cover columns or signed aliases cannot be stacked as common unknowns. |
| 6 | TORSION | Audit field, actual evaluator, kernel, nonzero r-action and return. | Order overlap does not evaluate a map; Hom=0 does not reject every nonlinear auxiliary use. |
| 7 | ROUTER | Supply executable public pseudocode for the operation outside the fixed-branch premise. | A compact equation/verifier can conceal full decomposition or target-log solving. |
| 8 | PRYMMODEL | Check dimension, finite-field maps and the exact solver stage that changes. | Isogeny existence or equal point counts supply neither transport nor a solver. |
| 9 | PROVENANCE | Identify the original32covers source/revision, equivalence convention and maps. | Another catalogue or an unsuccessful lookup does not certify the historical claim. |

PROVENANCE can run early as narrow read-only housekeeping; it does not gate the other branches. ROUTER ranks below more concrete near-term obligations because no new operation is instantiated, while remaining the strategic missing mechanism. Every scientific successor needs its own frozen runnable protocol; this table authorizes none.

## Cheap mathematical checks before another run

For FUNCTION, the actual cover is `C_B:y^2=x^6+2x^2+B`, of genus two, with two rational points at infinity. For `D=3*infinity_plus+3*infinity_minus`, degree six exceeds `2g-2`, so Riemann-Roch gives `l(D)=5`. The five independent sections `1,x,x^2,x^3,y` form a basis. Consequently `y-v(x)` with cubic v is the full affine chart with nonzero y coefficient in projective L(D). A different interpolation basis in this chart cannot be a new section family. The polynomial-only chart is a separately named boundary to analyze. Enlarging or moving D can change the family, but adds dimension, residual factors, exceptional charts and search cost; favorable splitting is not implied by Riemann-Roch.

The concrete first FUNCTION discriminator is now **projective x=0 completion**, before enlarging D. This lead was suggested by the parent and independently checked against `implementation/relations.py`, `implementation/census.py` and the retained status totals; no collector or source arithmetic was run. The old `lift_source` rejects sqrt(x_E)=0, and `descriptor` excludes every zero-x constraint. But the companion map extends as

    [W:V:Z] = [B*x : B*y : x^3],
    V^2*Z = W^3 + 2*W^2*Z + B^2*Z^3.

At x=0, y^2=B!=0, this is `[0:1:0]=O`, and `2y!=0` makes C smooth there. `Context.pi2` already encodes that image as `None`; it is the descriptor/source domain that excludes it. Scalar1 gives source -P at x_E=0, without requiring any new point calculation. Every active source block rejects all triples containing the one zero-x anchor: `C(15,2)*4^3=6,720` descriptors. The raw S totals imply 29/33 active blocks, and the D totals are exactly `29*6,720=194,880` and `33*6,720=221,760`. These mandatory exclusions exhaust D under the guard order. This accounting predicts **no** new accepted rows or rank.

A projective-x0-only successor can preserve the exact E, base, sources and 35,840 descriptor attempts/source. It needs principal-divisor, E1, projective E2, known-anchor, alias and transported-encoding checks. At x=0 the deck +/- lifts coincide, so options0/2 and options1/3 become aliases; source/base duplicate-x still needs handling. Keep leading-degree drops, polynomial-only function sections and V4 additions in separate arms. The frozen old guards are part of the old finite experiment, not evidence that it was invalid. This narrow completion is more discriminating than a generic larger-function-space proposal and still requires a new frozen runnable contract before any scientific collection.

For MULTICOVER, a simple symbolic candidate is

    C_c: y^2=(t^2+c)^3+a*(t^2+c)+b,
    pi_c(t,y)=(t^2+c,y) into the SAME E: y^2=u^3+a*u+b.

For a smooth E in odd characteristic and `f_E(c)!=0`, the sextic is squarefree, giving a genus-two double cover. Different branch square classes can certify distinct covers over E. This construction alone does not promise independent relations. A frozen atom `(u,y)` lifts only when `u-c` is a square or via an explicitly charged extension; common lift availability can shrink the base. The aligned projected E points, signs, public source labels and U must be fixed before comparing rowspaces. Torsion gluing instead needs its own rational anti-isometry and map certificate. No concrete new cover, point or relation was sampled in this advisory.

For PRYMMODEL, dimension is a first gate: the retained genus-two double cover of E has a **dimension-one Prym**. The Enolski-Fedorov source context concerns **dimension-two Pryms** with genus-two Jacobian models. Applying that ingredient requires a separately identified genus-three-cover construction, correct field/polarization hypotheses and maps; it is not a new genus-two model of this experiment's dimension-one auxiliary factor. Its over-C theorem is not automatically a finite-field algorithm.

For TORSION, rational Hom, finite subgroup-order overlap and a public evaluator are different questions. Shared r-order can supply an abstract rational cyclic r-subgroup without computing the image of an arbitrary Q. The map `kP -> kT` is circular unless evaluated without k. The natural anti-invariant projector kills the pullback E component of a double cover. That excludes this direct projector route, not auxiliary relation construction in the full Jacobian. A coprime map degree can certify injectivity on G; it does not bound discovery or evaluation cost.

## Loss, branching and complete costs

The object is always paired with its named operation set. Fixed IC relation vectors belong to the partial-action family; they are retained as measurement/control work, not relabelled a new arithmetic breakthrough. Pure injective model/isogeny transport loses no information and fails the new-lossy-object test on its own. A branching router must define the actual projection, what it discards and compatible propagation before it can quote L or b.

The program's meter defines `L=log2(mean fibre size)` and b as the mean number of possible propagated outputs over input fibres. The definition must be conditioned on the operation law actually claimed; enumeration branch count and inverse useful-output probability are additional costs. The identity, random-label and relabelled cyclic-group controls must use the same frozen law and support/fibre shape. No numerical L,b, smoothness law, useful-cycle probability or independent-cover heuristic is inferred from these two matrices.

For any new factor-base mechanism identify high-degree, implicit-membership or target-dependent content, or declare that it remains inside the bounded-degree control class. Charge description and construction, membership, every failed branch, section solving and residual factoring, nonrational fields, root/sign/subgroup recovery, distinct norm-atom canonicalization, cycle storage, rank after aliases/duplicates, linear algebra, target attachment, source return and verification. The divisor base on C and its projected base on E are different objects: counting both as independent unknowns can manufacture rank. Report peak live memory and cold setup beside genuinely reusable setup, with target count and amortization scope. A target-dependent base usually needs per-target setup unless reuse is actually proved.

A future cost account must split correctness, size, runtime and useful-output probability into separate obligations. It must reproduce the exact current IC boundary, compare matched rho with the same subgroup/symmetries and give BSGS/preprocessing tradeoffs where relevant. The existing operation counters are explicitly partial S and do not price omitted power internals, bookkeeping, movement and custody. Nothing here changes a frontier or supplies a quantitative attack-cost advantage.

## How the P-256 prior work changes this advice

The [supplied P-256 report](../context/p256-prior-report.md) is prior implementation/derivation context with its stated local custody, blindness and model exceptions, not new official promotion. F1 already reaches an unexpanded cubic-divisor extraction bottleneck: a short membership circuit and a depth-three success do not bound implicit solving. F3 already distinguishes useful and zero-Q constructed fixtures; its nonzero aggregate coefficient condition is in F_r, not merely over integers. F4 already supplies stitching certificates, while natural all-draw cycle yield, useful rank and target attachment remain missing. Those are close predecessors for TARGET, FUNCTION and PARTIAL, so simply restating them is a duplicate.

F7 already has same-field maps and injectivity through norm after pullback=[2]. The scoped Cartier/component derivation excludes an extra rational r-component for that particular P-256 quartic under its stated hypotheses; it neither implements arbitrary-class arithmetic nor supplies a target-component solver. Current toy genus-two and P-256 genus-three covers must not be conflated. F8's fixed orbit factor must also be given to the rho baseline. These details point toward interface/solver work, rather than inferring a new attack from cover existence or a genus label. The [existing component-solver problem](../../../problems/p256-cover-target-component-solver.md) remains the named obligation.

## Sources, scope and uncertainty

Internal reads cover the supplied search plan, source context, both frontier renderings, the full 147-lead inventory and relevant atlas rows, the P-256 report, linked proposal/problem state, object-frame section 3, inventor protocol and target profile. `ranking.json` binds exact source digests. Relevant existing leads include algebraic-membership factor bases, partial residual relations, signed relation graphs, cover-catalog transfer, same-field embeddings, split-Jacobian projection, second torsion direction and deck-period selectors. Existing atlas obstruction labels are attributed to their records; this advisory does not independently promote every theorem in the atlas.

External literature scope is the root retrieval recorded in [sources.json](../context/sources.json): Diem gives construction/gluing context, not a prime-field DLP algorithm; Enolski-Fedorov has over-C hypotheses; Genus3Covers was checked at README level and is not identified with original32covers. The Joux-Vitse full-text request returned403 and the Frey-Kani URL redirected without paper text. This advisory did not independently fetch/read those primary texts; their statements remain attributed to the supplied read scopes. No `search_knowledge`/`find_related`/`get_context` tool is exposed, and missing sparse corpus records prevent an exhaustive novelty audit. Novelty remains unverified except where the named method is already known/adaptation. These are retrieval limitations, not evidence that further constructions do not exist.

`dominated_by: n/a (no algorithmic result claimed)`; `sota_delta: no attack; conceptual/measurement contribution only`. No direction is closed. The finite nullity can be reused constructively as a quotient certificate for a target functional, but its public inverse remains missing; this is the resource reading of the obstruction, not a theorem of futility. A new constructor, a genuinely different same-E cover/aligned relation space, a public useful-dependency solver or an identified source can each trigger a scoped rerank.

Independence disclosure: matrix checks and support-two/RHS deductions were independently computed from sealed raw bytes before the parent supplied matching details. Parent-supplied support-three counts were not used. The x0 idea was parent-suggested and then independently audited at source/geometry/count level. No parent derived-analysis output was read; this advisory is not a blinded independent scientific review.
