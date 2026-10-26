# Cartier proposal: a route to the quartic target-component multiplicity

25 October 2026. Root derivation for independent checking; not a formal proof
certificate or a scientific state transition. The arithmetic receipt alone
does not establish the geometric lemmas below.

Let p be the P-256 field prime, E:y^2=f(x)=x^3-3x+b its nonsingular target
curve, and C the smooth completion of u^4=f(x). The earlier F7 package checks
that C is a smooth plane quartic of genus three. Its degree-two map to E is
pi(x,u)=(x,u^2). Put P=ker(pi_*)^0, the two-dimensional Prym. All these objects
are over F_p. Assume the published prime order #E(F_p)=r.

## 1. Differential basis and Cartier action

A basis of H^0(C,Omega^1) over F_p is

    omega1=dx/u^2, omega2=dx/u^3, omega3=x dx/u^3.

At infinity ord(x)=-4, ord(u)=-3, ord(dx)=-5, so their orders are 1,4,0.
At a zero of f, u is a uniformizer, ord(dx)=3, and all three forms are regular.
There are three independent forms, equal to the genus. Away from these points
their regularity follows from the affine equation. The first is the pullback
of dx/y on E.

Over F_(p^2), choose i^2=-1 and tau(x,u)=(x,iu). Its eigenvalues on the basis
are -1,i,i. Cartier is natural under pullback and p^(-1)-linear on scalars.
Since p=3 mod 4, i^(1/p)=-i. Consequently Cartier sends an i-eigenvector to
a -i-eigenvector. The latter eigenspace is zero, so Cartier kills omega2 and
omega3. On omega1 it acts as the elliptic Cartier operator. Thus, in the
F_p-defined basis, its matrix is diag(a,0,0), where a is the elliptic Cartier
coefficient. This argument does not require iterating a semilinear matrix or
assuming that tau is defined over F_p.

## 2. The Prym Frobenius polynomial is even

Write sigma=tau^2, the involution of C over E. On the connected norm kernel,
1+sigma=pi^*pi_*=0, hence sigma=-1 and tau^2=-1. The p-Frobenius satisfies
F tau=tau^(-1) F=-tau F on P. On any prime-to-p Tate module, conjugation by
tau therefore sends F to -F. Its degree-four characteristic polynomial is
even. The Weil reciprocal relation gives

    chi_P(T)=T^4+A T^2+p^2, A in Z.

The isogeny E x P -> Jac(C) is over F_p. In particular
chi_C=chi_E chi_P with chi_E=T^2-tT+p. No claim about the exact value of A is
made at this step.

## 3. A is divisible by p

Use the corrected characteristic-polynomial congruence in Achter--Howe,
section 2.5, for a curve over F_p:

    chi_X(T) = T^g det(T I - Cartier_X) mod p.

The source's earlier published formula is explicitly corrected in its v5;
using the zeta numerator in the wrong direction would be an error. For E
the congruence gives a=t mod p. For C it gives

    chi_C(T) = T^5(T-a) mod p.

On the other hand, the isogeny factorization gives

    chi_C(T) = (T^2-tT)(T^4+(A mod p)T^2) mod p.

Comparing the T^4 coefficient proves A=0 mod p. This avoids using an
uncited a-number-to-superspecial theorem. It still requires independent
checking of the differential, norm-kernel and Frobenius arguments.

## 4. Five possible orders, and the actual r-residue test

Pair the four complex Weil roots as alpha,-alpha,beta,-beta. Each has
absolute value sqrt(p), so A=-(alpha^2+beta^2) satisfies |A|<=2p. With p|A,
it follows that A=c p for c in {-2,-1,0,1,2}. Therefore

    #P(F_p)=p^2+c p+1.

The exact arithmetic receipt checks that none of these five integers is
zero modulo the actual P-256 r. If all preceding lemmas are accepted, the
Prym order is coprime to r even without identifying c. Because #E(F_p)=r,
Jac(C)(F_p) then has exactly one r-factor. Its r-primary subgroup is the
image of pi^*, with inverse [2^(-1)]pi_* on that image.

This would resolve only the extra-component multiplicity question. It
provides neither arbitrary Jacobian arithmetic nor faster relation generation,
unknown-scalar recovery, a hardness result, or an attack-cost claim. The
actual c and a complete component-specific solver remain separate questions.

## Source provenance and next check

- Retrieved and read by root on 2026-10-25: Jeffrey D. Achter and Everett W.
  Howe, *Hasse--Witt and Cartier--Manin matrices: a warning and a request*,
  arXiv:1710.10726v5, sections 2.2--2.5, especially corrected congruence (2.3)
  and the characteristic-polynomial formula following it.
  https://arxiv.org/pdf/1710.10726
- Curve/cover input: the F7 report and exact receipts in this study. Those
  inputs have not received independent scientific promotion in this session.

Next: independently rederive the regular forms and Frobenius anticommutation,
then check the comparison using the corrected congruence. A finite-field
Cartier implementation and known counterexamples to the same conclusion
without p=3 mod4 should be retained as controls. Until that check, this is a
specific, source-grounded derivation for review, not a completed review result.
