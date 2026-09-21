# Unpublished draft independent re-derivation

Task: `TASK-20260904-e81e42`  
Role: validator, independent blind re-deriver  
Scope: the three assigned joints only; this is neither a verdict on an ECDLP claim nor a publication or durable-evidence gate.

## Source custody and qualifications

The SHA-256 values independently recomputed for the retrieved source bytes were:

- Voloch-Walker PDF: `626568c410484b7e2df2ca96d895d28329c23650a4b5dfb3003788a8b49f5828`.
- Voloch-Walker text: `f6a14385917d651b1ad97adf901b2b6065c0d45c83f856cd75dbc42f368b1be4`.
- Blache PDF: `324f52f7434afb1ab9fd8998edde15ecefff3f47109d26e1625fc70f83ff6f64`.
- Blache text: `7e7c5a237c5823e21d840a1a50b6eb1b94c50558b7b346936ed9575ad77071b2`.

All four match the frozen source manifest. The PDFs were byte-read only for hashing; the mathematical passages were read in the extracted text. Voloch-Walker Sections 3-4 supply the Witt-vector sum bound, the canonical-lift hypotheses, the derivative formula for `x_1`, and the exact degree statement. Blache Section 3 supplies the definition of reduced pole order and the normalization `D_chi = sum_P (rp_P(f)+1)P`. These are retrieved citations verified in this task. The frozen statement and source manifest are internal inputs.

## J1 digit identity and carry polynomial — holds

Let `theta: W_2(F_p) -> Z/p^2 Z` be the standard identification. Every Witt vector has the Teichmuller-Verschiebung decomposition

`(a_0,a_1) = [a_0] + V([a_1])`,

and, because Frobenius is the identity on `F_p`,

`theta(a_0,a_1) = [a_0] + p[a_1] = [a_0] + p u(a_1) (mod p^2)`.

Writing `[a_0] = u(a_0) + p c_p(a_0)` therefore gives the exact ordinary representative

`theta(a_0,a_1) = u(a_0) + p u(a_1+c_p(a_0))` in `[0,p^2)`.

Consequently

`d_1(theta(a_0,a_1)) = u(a_1+c_p(a_0))`,

or, as an identity in `F_p`, `d_1 = a_1+C_p(a_0)`. Thus the ordinary second digit is generally not the second Witt coordinate.

The primitive additive character of the whole Witt vector is different again. With `psi_p(t)=exp(2 pi i u(t)/p)`,

`exp(2 pi i theta(a_0,a_1)/p^2) = exp(2 pi i u(a_0)/p^2) psi_p(a_1+C_p(a_0))`.

The extra first-digit factor prevents identifying the primitive `p^2`-character with the additive character of the ordinary second digit.

For an integer `u` in `{0,...,p-1}`, the Teichmuller condition gives `[u] = u^p (mod p^2)`, hence

`c_p(u) = (u^p-u)/p (mod p)`.

Let `C_p(X)` be the degree-`<p` representative. For any such polynomial, its `X^(p-1)` coefficient equals `-sum_{a in F_p} C_p(a)`. Pairing `u` with `p-u` shows `sum_{u=0}^{p-1} u^p = 0 (mod p^2)`, while `sum u = p(p-1)/2`. Therefore

`sum_{a in F_p} c_p(a) = -(p-1)/2 = 1/2 (mod p)`.

It follows that

`deg C_p = p-1`, with leading coefficient `-1/2` in `F_p`.

The requested synthetic controls separate the observables:

- As `u` varies, `(u,0)` has constant second Witt coordinate `0`, while `d_1=C_p(u)` and the primitive character `exp(2 pi i [u]/p^2)` are nonconstant.
- As `u` varies, `(u,-C_p(u))` has constant ordinary digit `d_1=0`, while its second Witt coordinate is nonconstant and its primitive character is `exp(2 pi i u/p^2)`, also nonconstant.
- For a fixed constant Witt vector, all three observables are constant.

Limitation: the formulas use the standard identification `W_2(F_p)=Z/p^2 Z`; they do not identify an ordinary digit with a Witt coordinate under an unspecified alternative convention.

## J2 canonical global representative and reduced poles — holds

The standard `x` coordinate has `(x)_infinity = 2O`. Since `p>3`, its order `2` is prime to `p`; its Artin-Schreier reduced pole order is `2` and the corresponding conductor divisor is `3O`. This is the precision-one convention check.

Because `C_p` has degree `p-1` and leading coefficient `-1/2`,

`(C_p(x))_infinity = 2(p-1)O`.

The order `2(p-1)` is prime to `p`, so it cannot be removed by adding `g^p-g`: a pole of `g^p-g` arising from a pole of `g` has order divisible by `p`. Thus

`rp_O(C_p(x)) = 2(p-1)`

and Blache's normalization gives conductor divisor

`D_chi(C_p(x)) = (2p-1)O`.

For the canonical lift, the hypotheses needed from Voloch-Walker are: `E/F_p` is ordinary; the lift is the Serre-Tate canonical lift; `tau` is its elliptic Teichmuller section; and the coordinates are compatible Weierstrass coordinates. Proposition 4.2 gives

`d x_1/dx = A^(-1) y^(p-1) - x^(p-1)`,

where the Hasse invariant `A` is nonzero. In the short monic equation, `y^(p-1)=(x^3+ax+b)^((p-1)/2)`. Its leading term has degree `3(p-1)/2` and coefficient `1`. Hence `x_1` has exact polynomial degree

`D = (3p-1)/2`.

Since `D=-1/2 (mod p)`, its leading coefficient is

`A^(-1)/D = -2A^(-1)`.

The derivative leaves an ambiguity by a constant and an `x^p` term, but both have degree below `D`, so neither changes this conclusion. Because `deg C_p=p-1<D`, the specified global representative

`F_can = x_1+C_p(x)`

also has degree `(3p-1)/2` and leading coefficient `-2A^(-1)`. Therefore

`(F_can)_infinity = (3p-1)O`.

Again `p` does not divide `3p-1`, so the pole is already Artin-Schreier reduced:

`rp_O(F_can)=3p-1`, and `D_chi(F_can)=3p O`.

This prime-to-`p` pole also proves that `F_can` is not `g^p-g+c`; the scalar character sheaf is geometrically nontrivial. For

`S_digit = sum_{P in E(F_p)\{O}} psi_p(F_can(P))`,

Blache Theorem 3.1 gives, with genus `1` and one rational pole,

`|S_digit| <= (2(g-1)+(rp_O+1)) sqrt(p) = 3p sqrt(p)`.

The same coefficient follows from Voloch-Walker Theorem 3.1. For the distinct primitive whole-Witt-vector sum on `(x,x_1)`, its coefficient is also

`2g-1 + max(p*2,3p-1) = 3p`,

but the equality of coefficients does not identify the two summands.

Writing `N=#E(F_p)` and `n=N-1` charges the omitted pole `O` explicitly. The normalized source estimate is

`|S_digit|/n <= 3p sqrt(p)/(N-1)`.

The trivial estimate is `|S_digit|/n <= 1`; for `p>=5`, the Hasse upper bound `N-1<=p+2sqrt(p)` shows the source coefficient is larger than the entire summation length. The usable statement at `q=p` is therefore the minimum of these two bounds, namely the trivial normalized bound `1`. If one artificially assigns a unit-modulus value at `O`, the resulting all-point sum differs by at most `1`; the source theorem itself sums only where the coordinate is regular.

Constants and coboundaries are excluded correctly. For `f=0`, for any constant `f=c`, and for `f=g^p-g+c`, the associated sheaf is geometrically trivial (possibly with a constant phase), there is no reduced pole, and a square-root cancellation conclusion does not follow. In Blache's convention the zero class has `rp_P=-1` and contributes no point to the conductor divisor. In particular, `x^p-x` has a raw pole of order `2p` at `O` but reduced class zero.

As a source fixture, Voloch-Walker's characteristic-five example has `A=2` and `x_1=4x^7+x^3`; the derived leading coefficient `-2/A=4` and degree `(3p-1)/2=7` reproduce it exactly. This is only a representation check.

Limitation: the exact results above concern the canonical lift and its specified global section. They do not apply to an arbitrary interpolation of the same finite set of values.

## J3 sample-equivalence and method ceiling — holds

Let `R(X)` be the remainder of the polynomial `F_can(X)` modulo `X^p-X`. For every affine `P in E(F_p)`, `x(P)^p=x(P)`, so

`R(x(P))=F_can(P)`.

This is equality of samples only. Globally, the difference is a multiple of `x^p-x`, and such a multiple need not be an Artin-Schreier coboundary. Because `deg R<p`, its global pole order is at most `2(p-1)`, whereas the canonical representative has pole order `3p-1`. Thus the source's leading pole does not survive polynomial reduction. If `R` is nonconstant of degree `d`, its order `2d` is prime to `p` and its conductor divisor is `(2d+1)O`; the exact `d` depends on the curve/model coefficients. If `R` is constant, the sheaf is geometrically trivial.

The known-false/global control is explicit:

`h=(x^p-x)x`

vanishes at every affine `E(F_p)` point and is sample-equivalent to zero, but globally it is nonzero with pole order `2p+2`, already reduced because `p` does not divide it, and has conductor divisor `(2p+3)O`. Thus affine sample equality cannot establish equality of Artin-Schreier classes or conductors.

Similarly, `0` and `g^p-g` are globally Artin-Schreier equivalent despite potentially very different raw poles. Taking `g=x` gives the raw-pole/reduced-pole control directly. Together the two controls show both directions of the failure: raw global expressions may differ while the Artin-Schreier class agrees, and affine samples may agree while the global Artin-Schreier class and conductor differ.

The method ceiling is therefore narrow. A source bound may be applied to a declared global representative and its reduced class. Polynomial reduction supplies a lower-degree sample-equivalent representative and a corresponding bound, but it does not determine the minimal conductor over all sample-equivalent functions. No subgroup or hybrid sum, bucket distribution, majority advantage, ECDLP algorithm, or cost improvement follows from the full affine-curve sum.

Finally, good reduction alone does not transfer the canonical-lift statement to b4e6eb's arbitrary model. Voloch-Walker identify the coordinate functions through the canonical lift and its elliptic Teichmuller section; Proposition 4.2's converse says that a suitably low-degree global section forces the lift to be canonical. A transfer to an arbitrary good-reduction model would require a proved isomorphism to the canonical lift, compatibility of the section, and an explicit coordinate-change calculation preserving the ordinary-digit observable. None is among the frozen hypotheses, so that transfer is unproved and must remain outside the derived scope.

## Joint verdicts and publication limitation

- `J1 digit identity and carry polynomial`: **holds** for the standard `W_2(F_p)` identification.
- `J2 canonical global representative and reduced poles`: **holds** under the ordinary canonical-lift and compatible-coordinate hypotheses stated above.
- `J3 sample-equivalence and method ceiling`: **holds**; sample equivalence does not preserve the global conductor, and transfer to an arbitrary good-reduction model is unproved.

This report is an unpublished draft independent re-derivation. It attests only to the blind work actually performed. The formal publication, durable-evidence, and scientific-review gates are not complete.

## Citation provenance

- Voloch-Walker, *Euclidean weights of codes from elliptic curves over rings*, Sections 3-4: `retrieved`; source bytes matched the frozen manifest; verified by `TASK-20260904-e81e42` for the claims used above.
- Blache, *Lifts of points on curves and exponential sums*, Section 3: `retrieved`; source bytes matched the frozen manifest; verified by `TASK-20260904-e81e42` for reduced-pole and conductor normalization.
- `frozen-statement.md` and `source-manifest.json`: `internal`; frozen task inputs, not external mathematical authority.
