# Evaluator/reconstruction search

**Task:** TASK-20261006-fa5bac

**Date:** 2026-10-06

**Role:** idea-generator

**Mechanism count:** 1

**Mandatory route count:** 3 (A/B/C)

**Finalist count:** 0

**Scientific / implementation / formalizer / experiment runs:** 0 / 0 / 0 / 0

## Question and exact interface

The single mechanism examined is **reconstruction of the unique calibrated
degree-`D` homomorphism from its public one-column observation**.  The three
routes are representations of that mechanism, not three candidate PKEs:

- A reconstructs the rational map from the orbit equations
  `f([i]P)=[i]X`;
- B reconstructs a factorization into `a` degree-two maps;
- C reconstructs the corresponding primitive cyclic norm-`D` ideal and then
  realizes it geometrically.

The only inputs are the represented/evaluable `O=End(E)`, represented curves
`E,C/F_(p^2)`, `P in E[N]`, `X in C[N]`, `D=2^a`, `N=5^b>4D`, `U,V in E[D]`,
`k=floor(a/2)`, and the inherited fixed encoding/admission interfaces.  No
`Hom(E,C)`, connecting path/isogeny, target order/action/frame, orientation,
retained sender map/dual, instance advice, or exponential preprocessing is an
input.  The analysis is conditional on successful inherited admission; all
seven inherited admission obligations remain open.

## Derived uniqueness boundary, not a construction theorem

Let `f,g:E->C` be separable homomorphisms of degree at most `D` on the exact
labelled models and suppose `f(P)=g(P)` for a point `P` of exact order `N`.
If `h=f-g` is nonzero, then `<P>` is contained in `ker(h)`, hence
`N <= deg(h)`.  The positive-definite degree form on `Hom(E,C)` gives

`deg(f-g) <= 2 deg(f) + 2 deg(g) <= 4D`.

Thus strict `N>4D` forces `f=g`.  This is a derived identifiability statement;
it supplies neither coefficients nor an evaluator.

Nearby relaxed observations do collide:

1. Replacing the signed point `X` by `x(X)` identifies `f` and `[-1] o f`.
   The extra separator is the full signed point (or an equivalent differential
   sign condition).
2. Publishing only `e_N(P,Q)^D` forgets the slope entirely.  The separator is
   a full labelled second column compatible with the map.
3. If `N<=4D`, the degree argument no longer separates maps whose difference
   kills `P`; this is failure of this proof, not an exhibited honest collision.
4. If the codomain is supplied only up to an unrecorded isomorphism, model
   automorphisms remain part of the observable.  The separator is the exact
   normalized model plus the transported signed `X`.

The exact useful condition is therefore: full signed `X`, exact labelled and
normalized `E,C`, group-homomorphism semantics, degree at most `D`, exact
`ord(P)=N`, and strict `N>4D`.

## Route A — orbit rational/Padé reconstruction

Write the short-Weierstrass equations as `y^2=F_E(x)` and `y^2=F_C(x)`; the
inherited prime is odd.  For `i=1,...,2D`, form

`u_i=x([i]P)`, `v_i=x([i]X)`.

Because `N>4D`, the `u_i` are pairwise distinct: `x([i]P)=x([j]P)` would give
`i=+/-j mod N`, impossible for distinct `1<=i,j<=2D`.  Solve the homogeneous
Padé system

`A(u_i)-v_i B(u_i)=0`, with `deg(A)<=D`, `deg(B)<=D-1`,

and choose the canonical projective scaling.  Two solutions would have
`A_1B_2-A_2B_1` of degree at most `2D-1` with `2D` distinct roots, so the
reduced rational function `R=A/B` is unique.  The honest map supplies one.

For a separable homomorphism the `y` coordinate is `y R'(x)/c`.  Determine
the nonzero differential scalar from the signed sample

`c=R'(x(P))*y(P)/y(X)`,

and return

`f(x,y)=(R(x), y R'(x)/c)`

only after checking coprimality, exact degrees, the cleared curve identity,
`f(P)=X`, codomain/model tags, and a degree/kernel certificate.  These checks
also reject Padé rank/degree degeneracy, a sample pole, inseparability, or an
inconsistent ciphertext.

This is a finite uniform reconstruction, but it is not bit-polynomial in the
encoded input: it consumes `2D` samples and outputs `2D+1` dense field
coefficients up to scale.  With `M(D)` denoting polynomial-multiplication cost,
fast structured interpolation is at best `~O(M(D))` field operations here;
conservative dense linear algebra is polynomial in `D`.  Sample generation is
`Theta(D)` group operations.  Time, workspace, and output are respectively at
least representation-scoped `Omega(D)`, `Omega(D log p)` bits, and
`Theta(D log p)` bits.  Since `D=2^a`, none is polynomial in the input bit
length.  The `O(D)` statement is explicitly about this dense representation.

The returned dense map is executable on `U,V`; the exact message path appears
below.  This route is the one concrete finite construction in the round, but
it is not a finalist under the no-exponential-preprocessing/output contract.

## Route B — forward/backward degree-two chain lifting

Over the inherited fully rational two-power setting, a nonbacktracking chain
has three initial degree-two choices and two choices thereafter.  A forward
state at depth `t` records the exact normalized midpoint, the composed map and
`[map]P`.  A backward state from `(C,X)` transports the unique `N`-torsion
preimage across a degree-two edge using its dual and multiplication by
`2^(-1) mod N`.

At split `t`, the meet predicate is: there is an explicitly enumerated model
isomorphism between the two midpoint curves carrying the forward image of
`P` to the backward point, with edge/dual labels and nonbacktracking state
consistent.  This predicate is sound and complete for the enumerated chain
family.  A curve-only endpoint collision is not sufficient.

There are `3*2^(t-1)` forward paths and `3*2^(a-t-1)` backward paths for
positive depths.  A balanced meet-in-the-middle therefore takes
`Theta(2^(a/2))` path states, evaluations and table memory up to polynomial
field factors.  Cycles and mergers are handled by keying the table by
`(normalized curve, transported point, forbidden dual edge)`; deduplication
may reduce a particular instance but has no uniform polynomial bound.  Initial
backtracking is excluded by construction and later backtracking by retaining
the last dual edge.

Exact-order, model, and certificate failures are local rejection predicates.
No further sound-and-complete local predicate was found that removes a branch
before it has a compatible backward state.  Checking that a completed path
has endpoint `C` and sends `P` to `X` is a full-path check and is not counted
as local pruning.  The route is finite and can return a composed evaluator,
but its balanced time and memory remain exponential in `a`.

## Route C — primitive cyclic ideal and exact calibration

The required algebraic object is a proper primitive left `O`-ideal `I` with

- reduced norm `D` and lattice index `[O:I]=D^2`;
- cyclic local type giving a cyclic degree-`D` kernel;
- right order geometrically identified with `End(C)`; and
- an exact realization `f_I:E->C` satisfying `f_I(P)=X` on the published
  models.

Fixed-rank HNF/SNF can verify a supplied lattice and its index, but does not
select the target ideal class.  Enumerating primitive local norm-`2^a` ideal
chains reproduces the three-then-two branching of Route B.  For each candidate
one must charge saturation, exact norm/cyclicity tests, right-order
computation, effective Deuring/ideal-to-kernel conversion, degree-two chain or
rational-map evaluation, codomain isomorphisms, residual automorphisms,
`f(P)=X` calibration, global normalization, and certificates.

KLPT or an equivalent-ideal routine may change a class to a smoother norm; it
does not by itself preserve exact norm `D`, cyclic type, the public codomain,
or the signed column `X`.  The current exact input does not instantiate the
single needed interface

`CALIBRATED_IDEAL_REALIZE(O,E,C,P,X,D) -> (I,f,certificate)`.

An implementation of that interface must include its own norm/index/
cyclicity, saturation, right-order, codomain-isomorphism, automorphism,
evaluation, normalization, bit-time, memory, output, preprocessing, success,
and failure theorem.  Treating a quaternion lattice, right order, or ideal
class as an evaluated map would be an interface error.  Exhaustive candidate
enumeration is finite but exponential; no bit-polynomial selector/realizer is
established.

## Explicit evaluator-only challenge

Dense output size does not settle the evaluator question.  The challenged
theorem is stronger and output-sensitive:

> A single uniform `PreEval` takes exactly `(O,E,C,P,X,D,N,encodings)` in
> polynomial bit time and memory, produces a polynomial-size data structure,
> and `Eval2(DS,U,V)` returns exactly `(f(U),f(V))` in polynomial bit time for
> every admitted honest instance, with a uniform declared failure bound and
> without connection advice or exponential preprocessing.

The actively examined transposed Padé candidate streams the `2D` orbit
equations, computes only the two evaluation functionals needed at `x(U)` and
`x(V)`, fixes the signed `y` multiplier, and emits four field coordinates.
Its output is small, but constructing either functional still consumes the
same `2D` observations/structured solve; storing a reusable approximant basis
or barycentric data uses `Theta(D)` field elements, and direct query
application uses `Omega(D)` representation work.  Paterson--Stockmeyer or
balanced composition can reduce constants/exponents in `D` but remains
exponential in `a`.  No theorem in the opened knowledge records converts the
single odd-torsion column into a poly(`a,log p`) evaluation data structure.

Accordingly `transposed-evaluator.yaml` records the exact candidate and stops
at `MISSING_SUBLINEAR_ORBIT_EVALUATOR`.  This is a missing interface, not a
lower bound or a universal impossibility statement.

## Returned-object to actual-message path

Whenever any route returns a certified evaluated `f:E->C` of degree `D` with
kernel `<U+sV>` and `f(P)=X`, execute:

1. Reject label, field, curve, degree, kernel, order, or certificate mismatch.
2. Compute `A0=f(U)` and `B0=f(V)`; reject unless `ord(B0)=D`.
3. Set `H=[2^(a-k)]B0`, `G=-[2^(a-k)]A0`; reject unless `ord(H)=2^k`.
4. Recover the binary digits of `t` from `G=[t]H` by the checked `k`-step
   power-of-two digit loop; verify `[t]H=G` and return `m=t`.

Since `f(U)=-[s]f(V)` and `s=m+2^k r`, this returns the actual selected
message `m=s mod 2^k`.  It costs two complete map evaluations, certificates,
and `O(k^2+a)` group operations.  An ideal/order/chain name without an
evaluator is rejected.  A point `W` or `Y` alone is rejected at
`MISSING_FULL_ACTION_DECODER`.

Failures remain separated: admission/setup/key failure; route/evaluator
failure; decoder shape/certificate failure; malformed-input rejection; and
wrong-key rejection when a declared relation fails.  A geometrically plausible
wrong key that passes the available checks has no authenticated universal
rejection guarantee.

## Nonduplication and scoped outcome

BATCH-066c3b stopped before any map at geometric ideal selection, simultaneous
target realization, or target-order/Hom realization.  This round does not
repeat its F1 finite-frame, F2 unevaluated symbolic sandwich, or F3 slope-by-
slope quotient loop.  Route A adds an explicit orbit/Padé finite
reconstruction and pays its `Theta(D)` samples/output; Route B adds the exact
two-sided point-labelled meet predicate and pays `Theta(2^(a/2))`; Route C
isolates the one calibrated ideal-realization interface with every conversion
charged.  These are analyses of the existing one mechanism.

No route satisfies the uniform bit-polynomial contract, so the finalist count
is zero.  This establishes no security, practicality, deployment conclusion,
universal obstruction, or EndRing-to-IND-CPA reduction.  Novelty is
`unverified`: the curated ECDLP frontier is not the governing comparison set,
and no absence from it is used as evidence.

## Sources and provenance used in this report

- `BATCH-066c3b`, `DEC-20261005-fcb424`, and the eight prior producer files:
  **internal**, opened in full for the inherited interface and nonduplication.
- `construction-source-boundaries.md` and `robert-torsion-boundary.md`:
  **internal** source-intake notes; their primary-source reads are not upgraded
  to this worker's retrieval.
- `KN-LIT-073`, `KN-LIT-074`, `KN-LIT-209`, `KN-LIT-527`, `KN-LIT-836`,
  `KN-LIT-961`, `KN-LIT-1084`, `KN-LIT-1248`, `KN-LIT-7642`,
  `KN-TECH-028`, `KN-TECH-029`, and `KN-OPEN-013`: **kb** records, used only
  at their stated abstract/reported/full-text-read tier and with their
  "Not verified here" limits retained.
- External primary retrievals by this worker: none.
