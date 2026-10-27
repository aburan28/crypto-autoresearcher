# A bounded x-sensitive Miller-primitive half-root screen

Proposed on 2026-10-27 by `/root/nongeneric_sweep_orientation`. This is a mathematical construction proposal and prior-work orientation, with hand-derived controls. No experiment, benchmark, statistical analysis, ledger transition, or scientific review was performed. The fixed 40-circuit family below is untested. It must receive its own frozen source/protocol and actual admission before execution.

The useful next step is an exhaustive constructor screen on the existing mandatory F11 fixture, rather than another random cohort or another truth-fitted polynomial. The candidate is explicit, has a charged evaluator, and uses both the already-proposed Miller primitive and the x coordinate. It is not a claim of a new primitive or a general ECDLP algorithm.

## Public primitive and exact cost recurrence

Let G=<P> have odd prime order r different from p on E/Fp, with p>3. For finite points let lambda be the affine chord/tangent slope; define it as zero for vertical or identity addition. For a public point R define

    D_1(R) = 0
    D_(2n)(R) = 2 D_n(R) + lambda(nR,nR)
    D_(2n+1)(R) = D_(2n)(R) + lambda(2nR,R).

Carry along nR using the same left-to-right binary addition chain for r. Put Z(O)=0 and Z(R)=-D_r(R)/r in Fp. If the canonical primitive law holds, D_n=Z(nR)-nZ(R); therefore rR=O determines Z(R). This implements the finite-subgroup primitive already proposed in IDEA-20261016-09fd08 without a dense division polynomial, scalar table or a fitted constant.

For L=bit_length(r), the binary loop uses L-1 doubles and popcount(r)-1 adds. Slope work must be charged, including any slope recomputation rather than assuming it is free. A direct affine implementation requires O(L) group steps and O(L) field inversions/multiplications, O(L) scalar bits and O(1) field-element state. Count r verification, primality/point checks, inversion, multiplication, squaring, equality and every exceptional branch. Bit complexity includes the selected field-operation implementation; no unit-cost large integers are assumed.

Before testing a half predicate, validate the primitive by an independent sum-of-slopes construction on this tiny group and check the full cocycle on all pairs. The oracle construction is O(r) validation work and cannot be used in the candidate evaluator or priced as its setup.

## New explicit family

Restrict the proposed branch-selector domain to p=3 mod4 and Z(P)!=0. Odd-prime-order nonidentity P has y(P)!=0. Define the public setup constant c=Z(P)/y(P) and, for fixed integer parameters alpha,beta reduced modulo p,

    g_(alpha,beta)(R)
      = Z(R) + c*y(R)*[alpha + beta*c*(x(R)-x(P))].
    g_(alpha,beta)(P) = (1+alpha)*Z(P).
    H_(alpha,beta)(O) = 0.
    H_(alpha,beta)(R)
      = (1-chi(g_(alpha,beta)(R)/g_(alpha,beta)(P)))/2.

The last expression is a BIT only when both numerator and denominator are nonzero. Z(P)=0, an invalid anchor, or g(R)=0 is an explicit unsupported/undefined result, not an arbitrary sign or a skipped target. No fallback solver is included or silently priced as zero.

Freeze alpha in {0,1,2,-2,-3} and beta in {1,2,3,4,-1,-2,-3,-4}: 40 public, target-independent circuit templates. They are separate fixed arms, not coefficients fitted using known logarithms. Keep the integer-template ID and the reduced field coefficients; detect aliases rather than counting aliases as independent evidence.

Setup computes Z(P), c, and the inverse anchor. Each query computes Z(R), a constant number of extra field operations, and chi(v)=v^((p-1)/2). Thus setup is O(log r), one predicate call is O(log r+log p) group/field work and O(1) field state, and the conditional scalar-recovery reduction costs O(log r*(log r+log p)) plus target doublings and final scalar multiplication. These are constructor/evaluator cost bounds, not a proof of scalar ordering or a measured advantage. With b=ceil(log2 p), multiplication cost M(b) and inversion cost I(b), the direct affine arithmetic bound is O(log r*I(b)+(log r+b)*M(b)), plus separately charged input certification. Integrated slope reuse is counted once; duplicated slope work is counted twice. An actual family search pays for all 40 arms; the cost of selecting a successful constant is not hidden.

Negation gives g(-R)=-g(R). As chi(-1)=-1, every defined predicate has H(-R)=1-H(R). Under x'=u^2*x, y'=u^3*y, slopes and Z scale by u, c scales by u^-2 and c*(x-x(P)) is invariant; consequently g scales by u and its normalized character is unchanged. These necessary symmetries do not establish scalar ordering.

## Why the simpler family should not be swept again

The natural one-variable family g(R)=Z(R)+alpha*c*y(R) is already ruled out by a hand-derived fiber obstruction on the mandatory fixture. More generally the same counterexample applies to every g(R)=y(R)*F(Z(R)/y(R)) with a fixed rational F finite and nonzero at the relevant value, even if F has coefficients depending on the public base.

On E/F11: y^2=x^3+x+6, r=13, P=(2,7):

| k | kP | Z(kP) | Z/y |
|---|---|---:|---:|
|1|(2,7)|3|2|
|2|(5,2)|3|7|
|3|(8,3)|8|10|
|4|(10,2)|3|7|
|5|(3,6)|4|8|
|6|(7,9)|6|8|

For example the chain 1,2,3,6,12,13 has slopes 8,2,1,7,0, giving D_13(P)=5 and Z(P)=-5/13=3 mod11. The primitive addition law then gives the displayed Z values. These are hand calculations, not executed measurements.

Both 5P and 6P are in the lower half. Their equal Z/y values force

    g(5P)/g(6P) = 6/9 = 8 mod11,
    chi(8) = -1,

so normalized characters at those two points are opposite whenever defined. A zero or pole of F at 8 is undefined and does not rescue a half predicate. This excludes exactly the stated decoder form on this fixture; it is not a lower bound for general coordinate circuits. The new beta term sees x(5P)=3 versus x(6P)=7 and escapes this particular forced collision. Whether it meets ordering is untested.

The earlier alpha=0 control also fails at 3P because chi(Z(3P)/Z(P))=chi(8/3)=chi(-1)=-1. The earlier proposed integer alpha list contained aliases modulo11, including 8=-3 and -8=3. An exhaustive alpha-in-F11 screen would therefore only reconfirm a scoped mathematical counterexample and belongs as an instrument control, not a fresh lead.

## Exact fixed-fixture experiment to design

Use the one existing F11 model and all twelve nonidentity generators, all thirteen public targets, and the 40 fixed templates: 6,240 planned candidate-target cases before controls. No new curve cohort or private target root is required. The candidate receives only public E,P,r,R and alpha,beta. An independent validator enumerates the thirteen-element group for truth and is the only component allowed to use scalar indices.

For every arm/base retain every target result, undefined reason, root/sign identity, first counterexample, full two-pulse residual vector, operation counts, temporary-state counts and exact source/input hashes. The exact ordering condition is

    H(O)=0;
    H(R+P)-H(R) = delta_(6P)(R)-delta_(-P)(R).

Controls are the full cocycle and oddness laws; alpha=-1 as an invalid-anchor control; beta=0 as the proved-false fiber family; the anchored -f^3 wrong-root circuit in the existing note; and a truth-derived half/root oracle as a clearly labelled linear-cost validator-only positive control. Check coordinate covariance on all nonzero u in F11 and generator reindexing. Maintain undefined cases rather than converting character zero into a bit. All group operations used by construction, validation and conditional recovery receive separate cost totals.

A fixed alpha,beta template passes the finite constructor test only if it gives a defined bit on every target for all twelve generators, the two-pulse residual is identically zero including O/-P/6P, and every conditional scalar recovery verifies. Report per-base results even when a template fails globally. All-case success advances only that explicit finite circuit to a proof/generalization question; it does not supply the missing all-family ordering proof. A failure supplies an exact counterexample to that fixed template, while leaving x-sensitive/rational/nonlinear families outside this grammar open. If all 40 fail, stop that grammar; do not manufacture a larger random cohort or truth-fit new coefficients in the same experiment.

## Prior work and evidence gaps

The ordered-root report and its audit already distinguish a correct square root, anchors, covariance and dense interpolation from a uniformly priced ordering constructor. The earlier pilot's coordinate grammar and truth-derived coefficient diagnostics do not establish a circuit lower bound. The proposed screen instead supplies an explicit high-degree primitive circuit and a fixed public x-sensitive decoder, with no coefficient fitting or orbit table in the evaluator.

IDEA-20261016-09fd08 proposes the same additive primitive and several correctness/statistical tests. The checked CZLIFT-ae0a13/1a3453 drivers test torsion sections and coordinate digits; the scoped source search found no Z/Miller implementation there. EXP-ECDLP-6dacdb's actual specification/runs concern an embedding-degree census, so its citation in the multiplicative-cocycle proposal is not evidence that this decoder was tested. This bounded source check does not prove repository-wide novelty or absence of other implementations.

The primary Voloch paper was now read, closing the earlier snippet-only reading gap for its addition-law/universal-extension content. It establishes a characteristic-p zeta object on a Frobenius cover and treats normalization carefully. This supports overlap with classical zeta/extension constructions; it does not identify every notation convention with the finite-subgroup Miller evaluator or prove a scalar-half decoder. [Voloch, author preprint](https://www.math.canterbury.ac.nz/~f.voloch/Pdfs/zeta3.pdf), published in Acta Arithmetica79(1997),1-6, DOI10.4064/aa-79-1-1-6. The publisher-host fetch returned403; author PDF text was successfully retrieved/read through the web tool, while a separate local byte download also returnedHTTPError. Do not claim a local PDF byte hash.

Checked repository sources and hashes are in source-manifest.json. The crypto repository's research program separates preprocessing from online work; the cryptanalysis/crypto sources available here are bounded read-only review copies, not a new audit of every file in those repositories. No quantum method, index calculus, multiplicative-field log solver or uncharged lookup is used by this proposed screen.
