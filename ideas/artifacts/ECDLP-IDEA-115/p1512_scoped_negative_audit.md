# P1512 scoped-negative independent audit

Status: `PASS_SCOPED_ULRICH_SINGLE_MAP_SOURCE_LENGTH_NEGATIVE`

This is a non-run theorem-audit receipt. It checks the immutable
`ulrich_source_gate.md` derivation without modifying it. It is not an approved
experiment, a general lower bound for algebraic circuits, or evidence of an ECDLP
breakthrough.

## Frozen scope

Let the oriented public factor deck have size `B`, fix arity `t>=3`, and retain every
ordered source sum together with its target on the plane cubic `E`. Projection to the
`t` sources is an isomorphism of finite schemes. Even after the favorable permutation
quotient, the canonical multiset cycle has length

`L_t(B)=binomial(B+t-1,t)=Theta(B^t)`.

The immutable receipt instantiates `t=5` and `B=2r`, giving
`L_5(2r)=binomial(2r+4,5)=Theta(r^5)`. The general form also covers the contract's
frozen arities three and four.

If `nu_R` counts accepted source multisets over target `R`, with scheme multiplicity,
then `sum_R nu_R=L_t(B)` when repeated and cancelling oriented occurrences are retained,
as required by the declared exact-source convention. If a precommitted normalization
deletes degenerate cancellation patterns, it removes only `O(B^(t-1))` multisets for
fixed `t`, leaving `Theta(B^t)` generic distinct noncancelling atoms. All such targets
are rational because the source deck is rational. The count is a conservative lower
bound for any convention at least as informative as an unordered oriented source row.

## Strict Ulrich single-map check

Assume an `s x s` matrix `M` of homogeneous linear target forms is generically
invertible on `E` and that its normalized kernel or cokernel has at least `nu_R`
independent, publicly source-invertible atoms at each accepted target. Restriction of
`det M` to the plane cubic is a nonzero section of `O_E(s)`, whose zero divisor has
degree `3s`.

Smith normal form over the local discrete valuation ring at `R` gives

`ord_R(det M) >= corank_R(M) >= nu_R`.

Summing over targets yields

`3s >= sum_R nu_R = L_t(B)`,

so `s>=ceil(L_t(B)/3)=Omega(B^t)`. If the determinant vanishes identically,
generic invertibility fails and the required target/source biconditional is already
lost.

On the frozen comparison family `N=Theta(r^5)`, the charged scalar-linear dimension is
`Omega(N)`, whereas Pollard rho is `Theta(N^(1/2))=Theta(r^(5/2))`. The declared
target-independent scalar-linear atomizer therefore fails before kernel computation,
relation rank, factor logarithms, or blind target descent.

## Complete rho comparison across factor-base sizes

Write `B=N^beta`. The scalar-linear setup lower bound is `N^(t*beta)`. Under the same
random-support model used by the hypothesis, a random known target has source density
at most `pi=min(1,B^t/N)`. In the sparse regime, merely obtaining `Theta(B)` rows needs
at least `N/B^(t-1)` target attempts, even before charging each attempt. Thus the
complete time exponent obeys

`lambda >= max(t*beta, 1-(t-1)*beta)`.

Its best possible balance occurs at `beta=1/(2t-1)` and equals
`t/(2t-1)>1/2`. In the dense regime `t*beta>=1`, the setup bound is already worse.
Consequently shrinking the factor base cannot repair the scalar-linear cycle-length
obstruction. This density step is heuristic and model-bound; the exact matrix-size
theorem itself is not.

For the contract's frozen arms, `t in {3,4,5}` and
`beta in {0.18,0.20,0.22}`. Even the smallest strict-Ulrich payload exponent is
`3*0.18=0.54`, already above the `0.50` falsification boundary without using the
random-support step.

## Complex and representation boundary

The credited complex case is the strict Ulrich two-term Chow presentation that reduces
to one square linear map. A longer generically exact Chow or Tate complex is covered
only after a separate proof that every accepted source contributes an independent atom
in one effective homology degree, with no opposite-parity local torsion cancellation,
and that the determinant-line rank-twist payload is explicitly charged.

This receipt does not claim a lower bound for:

- arbitrary nonlinear or target-specialized arithmetic circuits;
- a packed aggregate followed by a separately charged nonlinear source splitter;
- weakly Ulrich or multiterm complexes with unproved determinant cancellation;
- rectangular or common-minor encodings without a separate Fitting-ideal source proof;
- succinct high-degree pullbacks whose operator circuit is not explicitly serialized;
- a representation whose atoms are not independent kernel or cokernel basis elements.

Any such construction is outside the IDEA-115 fingerprint. To qualify as a successor,
it must be constructed before source enumeration, expose an exact scalar-blind
`t`-source inverse, charge its splitter and all ambiguity, have every complete exponent
below `1/2`, and receive a new idea ID, fingerprint, and contract.

## Literature boundary

Eisenbud and Schreyer construct canonical Chow complexes and identify the Chow form as
their determinant for suitable sheaves. In the strict Ulrich case relevant to this
fingerprint, the Chow complex collapses to one nonzero square linear map; that is the
single-map case proved above. Buchweitz and Pavlov construct small Moore-matrix
representations and Ulrich bundles for a plane cubic. These are valid positive controls
for determinantal representation, but neither source supplies a compressed `t`-factor
source-biconditional atomizer.

## Independent verdict

The strict Ulrich single-map argument is exact under the declared independent-source-atom
assumptions. Any multiterm extension requires the noncancelling effective-homology and
charged-payload proof above. IDEA-115 is therefore scoped-falsified as a
target-independent strict-Ulrich square-linear source atomizer. No unconditional runtime
or peak-memory lower bound is claimed for succinct implicit operators, and no claim is
made against a mechanism-new nonlinear target-specialized representation.
