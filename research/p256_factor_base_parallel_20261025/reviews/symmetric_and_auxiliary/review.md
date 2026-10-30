# Local adversarial check of F1 and F2

25 October 2026. TASK-20261025-1a83bb. Outcome: **the assigned algebra and retained exact certificates hold within the checked scope; no arithmetic or mathematical counterexample was found.** This fresh native agent check is local engineering evidence. It does not discharge a scientific review gate, supply a model attestation, authorize publication, or establish ECDLP performance.

## Observation and custody

The blind derivation was written before opening producer source/results. Its SHA-256, concatenating these two lines, is:

```
cd079c507aad1c0225c83bc33b7a17f14b3
5628bb1a69f268ae37052df58cbd8
```

See [blind-derivation.md](blind-derivation.md). Only the handoff, original plan, and published parameter definitions informed that derivation. No sibling review was read. Subsequent computations import reviewer code and general Python/SymPy/FLINT libraries; they import no producer modules.

The sealed ZIP matches SHA-256 `31d35a0cf3c2977e56c84d3bcd23fe730c8ee396a3de6eda009c8c08a7c0d28a`. The audit and six manifest digests match, including 442 F1-continuation/F2 delta files. A direct ZIP comparison also checks these 442 files plus seven audit/manifest files. The 63 original F1/baseline files match their Git blob IDs in the locally cached logical-base tree `c35b9da6a65e019eaa517fc1a5f7774428ff35db`. The checkout HEAD remains `2c8c71cfff6f7f63297fbe4de4608cd94d857184`. These are distinct, explicitly recorded custody facts; see [custody-independent.json](custody-independent.json) and [custody-supplement-v2.json](custody-supplement-v2.json).

**Procedure deviation, blocking any official gate:** normal dispatch requires committed and pushed inputs. This task instead uses the local sealed-input exception. No canonical admission is asserted. The runtime/model binding is unprobed. No Git index/ref/branch change, PR mutation, upload, scientific transition or external message was performed by this reviewer.

One custody inspection failed operationally: reading a missing promised Git blob with `git cat-file` caused Git to try its implicit fetch, which failed at the unavailable proxy. [custody-supplement.stderr](custody-supplement.stderr) and its original source remain. The successful second attempt sets `GIT_NO_LAZY_FETCH=1` and hashes local bytes as Git objects against cached tree IDs, requiring no blob download. This failure is not mathematical evidence.

## Comparison on the assigned joints

| Assigned joint | Independent check | Local outcome |
|---|---|---|
| F1 symmetric terminal and complete domains | Nine domains; all 27 complete signed decomposition sets; independent quadratic resultant | Holds on every retained finite fixture |
| F1 terminal multiplicity | Fresh quotient lengths 8 and 64 at depths 1 and 2; geometric counts 4 and 20 | Nonreducedness reproduced |
| F1 radical cubic divisors and repeated strata | All 620 divisors at scalar degrees 4, 8 and 16; seven query unions; all 21 basis certificates and 386 critical pairs | Holds, including resultant sign |
| F1 deep representation witnesses | Three scalar roots, symmetric terminal and derivative/resultant Jacobian at all seven retained depths through 96 | Holds as witnesses; no deep solving conclusion |
| F2 rational chain and dual | All 16 edges, exact generator/image orders, 128 dual-composition samples, universal rational identities | Holds for the retained chain |
| F2 complete domains and target lifts | All 12 domains, 16,320 coordinates and 8,279 accepted target lifts, including subgroup tests | Holds for these exact domains |
| F2 poles and branch geometry | Rebuilt reduced maps at degrees 64, 256, 1024 and 4096; complete pole products and derivative identities | Holds, including critical poles |
| F2 matched bases and positives | Degree/cardinality metadata, exact kernel generators, matched sizes 26/121/515/2066, all 12 constructed sums | Holds as constructed correctness controls |

The complete machine observations are in [f1-independent.json](f1-independent.json), [cubic-independent.json](cubic-independent.json), [basis-independent.json](basis-independent.json), [f2-independent.json](f2-independent.json), [algebra-independent.json](algebra-independent.json), [controls-and-depth.json](controls-and-depth.json) and [boundary-checks.json](boundary-checks.json).

![Exact F1 algebraic lengths, not runtime or attack costs. Scalar degrees 4, 8, 16; the divisor and union counts are exhaustively checked in cubic-independent.json.](coverage-diagram.pdf)

## Mathematical interpretation and attempted breaks

**F1 multiplicity and missing-root attacks.** For a generic split scalar fibre with N roots, the symmetric terminal has length N cubed, but only C(N+2,3) geometric points. Distinct triples have local length 6, exactly two equal have length 3, and all equal have length 1. Their weighted sum is N cubed. Generic univariate separability alone therefore cannot justify radicalness of this original terminal scheme. The producer explicitly identifies this issue in `tracks/f1/derivations.md`, section “The symmetric diagonal remains ramified”; the fresh small cases agree.

For a separable F and monic cubic h, differentiating division gives delta R = -q delta h modulo h. In coefficient order (R0,R1,R2) and variable order (u,v,w), the two determinant signs cancel: det Jacobian = Res(h,q). Independent differentiated long division confirms this sign and nonzero determinant at every retained distinct divisor. For the deep witnesses, computing the same determinant as the product of F'(r)/h'(r) avoids dense expansion entirely. These checks support representation validity only.

The exactly-two-equal divided difference excludes the diagonal because it becomes F'(x) there. Its N(N-1) points and the N all-equal points complete the C(N+2,3) reduced union. Quotienting their finite reduced algebras by S4 preserves reducedness. Rational coefficient cubics do not generally imply rational individual roots, but every retained fixture has a complete linear factorization. Signed target lifts and complete point sums were independently enumerated, including inverse-pair cancellations. The nonseparable control F=D8-2, h=t cubed-4t still divides F and has zero Jacobian determinant, so the separability hypothesis cannot be dropped. These findings agree with `tracks/f1/cubic-divisor/derivation.md`, sections 1, 3-5.

**F2 rationality, poles and group-confusion attacks.** Character-sum cancellation proves the auxiliary order p+1. The unique nonzero rational 2-torsion point proves its 2-primary group cyclic, of order 2 to the 96th power. The explicit generator and all image generators have their declared exact orders. Symbolic substitution independently checks the quotient curve identity and normalized dual doubling formulas; point arithmetic checks both composition directions on all retained samples.

The elliptic isogeny is unramified, while its induced rational x-map has ramification. At degree N the pole divisor consists of infinity and x=0 as simple poles, with N/2-1 double finite poles. Rebuilt derivative numerators have degree 2N-2 and are squarefree. They are coprime to source 2-torsion; every finite non-pole critical image satisfies destination 2-torsion. Hence the complete certificates include critical poles rather than silently dropping them. These conclusions agree with `tracks/f2/derivation.md`, sections “Each degree-two map and its dual” and “Finite fibres, kernel coordinates, poles and ramification”.

A non-2-torsion endpoint prevents inverse-pair collisions in its generic x-fibre. Together with the map degree, all distinct enumerated preimages prove completeness. Kernel counts are checked against the actual chain degree and exact cyclic generator orders. The degree-65,536 compact fibre satisfies its theorem's endpoint/kernel hypotheses; full target lifts at that degree remain unenumerated. Negative controls reject a pole as an ordinary finite image, an off-curve point, a genuinely nonsquare auxiliary coordinate (x=3), and a corrupted terminal point. Projective scalar multiplication also passes eight affine comparisons and both true-order and false-order controls.

Finally gcd(p+1,r)=1 and the traces differ. These checks exclude any nonzero rational-point group homomorphism from P-256 into the auxiliary group, and any Fp-isogeny between the two curves. The producer treats auxiliary coordinates as a domain selection rule and does not claim group or logarithm transfer.

## Coverage limits and next obligations

There is no producer correctness issue requiring a correction in this checked scope. There are two material unresolved obligations, already acknowledged by the producer:

1. The cubic-divisor depth-4 distinct-coordinate Groebner runs remain unknown. My exhaustive reference recovers its single constructed solution, but does not turn the stopped implicit solver into a completed run. A complete implicit solve and certificate on the unchanged depth-4 positive and empty fixtures would distinguish progress on that obligation.
2. F2 supplies no ordinary-public-target relation solver. A solver must preserve denominator exclusions and the sorted-prefix matched-base predicate, recover all signs, and certify positive and empty cases. Setup, failed lifts, root recovery, relation rank, scalar labels, linear algebra and target attachment still require full accounting before any end-to-end claim.

No relation-yield distribution, independence law, asymptotic solving bound or speed advantage follows from these computations. No high-depth domain/triple enumeration was attempted beyond the retained scope. The audit does not formally verify Python/SymPy/FLINT, independently prove primality, validate every historical performance/literature claim, or replay the producer's launcher exception/early-return guards. Native failure receipts and watchdogs were inspected as scope records; they were not rerun to seek a different outcome.

No shared graph or problem record was changed. Existing F1/F2 diagrams remain producer artifacts because the checked mathematical relationships need no correction; the accompanying graph records this local check's exact scope. Original obstruction pointers are `tracks/f1/problem-implicit-global-solver.md`, `tracks/f1/cubic-divisor/problem.md`, and `problems/pkm-isogeny-chain-factor-base-no-fast-decomposition.md`; the Coordinator owns their integration.

## Reproduction and local provenance

From this directory use `/workspace/dickson-solver/.venv/bin/python` with `PYTHONDONTWRITEBYTECODE=1`. The retained JSON files record exact commands, source SHA-256, wall time and resident memory for these checks. They are verification resource observations, not comparative benchmarks. Primary script invocations are `independent_check.py custody`, `f1`, `cubic`, `basis`, `f2`, `algebra`, followed by `controls_and_depth.py`, `boundary_checks.py` and `custody_supplement_v2.py`. Outputs refuse overwrite; use a fresh copy of the review directory for replay. Matching `.stdout` and `.stderr` files retain native output. CPython 3.12.14, SymPy 1.14.0 and python-flint 0.8.0 were used; all arithmetic checks ran sequentially below the 2 GiB envelope.

Local provenance: joints owned are F1 symmetric/cubic-divisor and F2 auxiliary-chain/fibre scope. Sources are the handoff, original plan, parameter definitions, the named derivation/report/source files and certificate data recorded above, plus repository instructions. Sibling reviews read: none. Blindness respected until the saved derivation. No external model or inference probe was made. Local joint outcomes: holds within the specified checks; scaling and ordinary-target solving remain unestablished. Official research attestation: not supplied.
