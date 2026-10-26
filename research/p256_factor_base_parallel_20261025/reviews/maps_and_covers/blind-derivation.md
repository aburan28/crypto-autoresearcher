# Independent derivation before producer tables

Task TASK-20261025-9b6553. Local engineering/math check only. Recorded at 2026-10-25T05:51:19.355100+00:00.
The pushed-input precondition is unmet; no canonical review/promotion is claimed.
Model binding is unprobed. No producer code is imported.

## Exposure ledger

Before this record I read the task, local exception, published baseline parameter definitions, repository/skill rules, and filenames. A targeted search of F7 obligations.md intended to recover the geometric statement also exposed producer narrative reporting seven fibre checks and the claim that the Prym coefficient was unknown. This is a procedural deviation from complete blindness; it disclosed neither coefficient tables nor certificates nor the new Cartier proposal. The derivations below use the equations and public parameters. No producer result.json, verification receipt, ranks/root counts, analysis/cartier-proposal/derivation.md or arithmetic output has been opened.

## F5: conductor, kernels and transport

For published P-256 p=2^256-2^224+2^192+2^96-1, N=r=0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551, t=p+1-r=89188191154553853111372247798585809583. Thus Delta=t^2-4p=-455213823400003756884736869668539463648899917731097708475249543966132856781915, congruent 1 mod4. If its absolute value is squarefree, Delta is fundamental, f_pi=1; because f_E divides f_pi, f_E=1 without a separate endomorphism-ring computation. Squarefreeness still needs an exact certificate; I have not assumed it from digit size or a probable-prime factorization.

For ell!=p, a separable degree-ell elliptic isogeny needs a Frobenius-stable cyclic subgroup of E[ell]. Its x-kernel polynomial has degree (ell-1)/2 for ell odd. A factor of the ell-division polynomial can instead be a Frobenius orbit of points across different cyclic lines; its degree alone does not identify a subgroup. Kernel closure under multiplication/addition is essential. A stable subgroup scheme may have nonrational individual points; E(Fp) having prime order r rules out rational ell-torsion for ell!=r, but does not rule out an Fp-rational ell-isogeny. For ell!=p the finite kernel scheme is etale (geometrically disconnected when ell>1); it should not be called connected. A morphism's codomain and its dual must be aligned through any normalization isomorphism. The checks to require are map landing, degrees, exceptional inputs, and dual(phi) o phi=[ell] and phi o dual(phi)=[ell]. If gcd(ell,r)=1, restriction to E[r] is injective and [ell^-1]dual(phi) recovers the source point. This is scalar preservation, with no automatic destination DLP advantage.

## F7: quartic cover and subgroup

C: u^4=f(x)=x^3-3x+b with pi(x,u)=(x,u^2) to E:y^2=f(x). Its plane closure is U^4=X^3 Z-3 X Z^3+b Z^4. The sole point at infinity is [1:0:0], where the Z derivative is nonzero. In the affine chart, singularity would force u=0 and f=f'=0. Thus squarefree f and p!=2 imply smoothness. A smooth plane quartic has genus3. Alternatively the degree4 Kummer cover C->P1 has four totally ramified places (three simple roots and infinity); 2g-2=-8+4*3=4.

The map pi is degree2 and separable for p odd. On Pic0, pi_* pi^*=[2]. Since r is odd, pullback injects E[r]; inverse on its image is [2^-1 mod r] pi_*. This gives a direct-factor decomposition on r-torsion but by itself does not exclude another copy in the connected Prym P=ker(pi_*)^0 of dimension2. Rational points of the kernel versus connected algebraic Prym are distinct objects. A full-Jacobian complexity assertion does not automatically apply to this injected component and its input distribution.

For a companion C2:v^2=f(z^2), provided b!=0 and f squarefree, f(z^2) is squarefree of degree6, so genus2. The quotient (z,v)->(z^2,v) is E. The other involution (z,v)->(-z,-v) has quotient D:w^2=s*f(s)=s^4-3s^2+b*s with (s,w)=(z^2,zv), an elliptic quartic; Jacobian(C2) is degree-power-of-2 isogenous to E x D. If this is the producer's complement, independent elliptic counting can determine its extra r-factor. This companion statement remains conditional until the producer's geometric definition is read.

## New Cartier/Frobenius joint, independently derived

Work geometrically over algebraic closure; p=3 mod4 and i^2=-1. The automorphism sigma:(x,u)->(x,i*u) is defined over Fp2 and sigma^2 is the cover involution. At infinity ord(x)=-4, ord(u)=-3, ord(dx)=-5. A regular basis is dx/u^2, dx/u^3, x*dx/u^3, with sigma eigencharacters -1, i, i respectively. The invariant elliptic summand is dx/u^2, while Prym H0(Omega) has character i twice and no -i summand.

Cartier is p^-1-semilinear, commutes naturally with pullback, and sends an eigenvector of character i to character i^(1/p)=-i. There is no holomorphic -i eigenspace, so Cartier kills both Prym differentials. This argument uses geometric scalar roots and semilinearity; treating Cartier as Fp2-linear would give the wrong conclusion. The degree2 projector exists because p is odd. Hence the Prym Hasse-Witt operator is zero. The mod-p Frobenius characteristic-polynomial congruence then forces its L-polynomial to be 1 modulo p, so its middle coefficient A is divisible by p. This step invokes a precise general congruence still to be checked against the corrected primary source; an unverified citation is not being substituted for that check.

On the ell-adic anti-invariant subspace for ell!=2,p, Frobenius interchanges sigma eigenvalues i and -i because p=3 mod4. Its 4x4 characteristic polynomial is even, T^4+A*T^2+p^2. Frobenius eigenvalues occur as alpha,-alpha,beta,-beta with |alpha|=|beta|=sqrt(p); alpha^2 beta^2=p^2, so |A|<=2p. Thus A=k*p with k in {-2,-1,0,1,2} and #P(Fp)=p^2+k*p+1. These are necessary candidates, not a proof that each is realized. Checking all five modulo r can exclude an extra rational r-factor without identifying A. It does not count extension-field r-torsion or establish an attack cost.

Proves-too-much control: for p=1 mod4, Cartier preserves character i and need not kill it, while Frobenius need not exchange eigenspaces and the Prym polynomial need not be even. At p=5, a=-3=2 and b=1, f=x^3+2x+1 is squarefree. Since dx/u^3=f^3*dx/(u^3)^5, Cartier on the i-character basis has matrix [[2,1],[1,0]] over F5: coefficients selected are x^4 and x^9 in f^3 and x*f^3. Its determinant is 4, nonzero. This explicitly defeats any characteristic-independent Cartier-annihilation argument. Direct small-field counting is planned as an independent check.

## Remaining work

Read producer material only now; independently factor Delta with proved primality where feasible, reconstruct selected maps/dual compositions and genus2 complement; check the corrected Cartier congruence; retain code, exact outputs and failures. No full plane-quartic group implementation or cost comparison is asserted.
