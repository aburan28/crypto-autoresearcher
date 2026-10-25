# Independent derivation before producer results

Date: 2026-10-25. TASK-20261025-1a83bb. Internal provenance: handoff,
original-week-plan.json statements and baseline/parameters.py definitions only.
No producer source, result tables, certificate counts or other reviewer report
has been read as of this write. Fresh native agent session; model binding
unprobed. This is an isolated local engineering/math check, not an official
scientific review gate or model attestation.

Custody deviation: inputs are sealed locally, rather than committed/pushed as
normal dispatch requires. reviews/local-custody-exception.json binds the ZIP
SHA256 31d35a0cf3c2977e56c84d3bcd23fe730c8ee396a3de6eda009c8c08a7c0d28a
and archive/payload-audit.json. No publication or official transition follows.

## F1: symmetric terminals

Let x_i=z_i+z_i^-1, D_n(x_i)=z_i^n+z_i^-n, and N=2^k.
For elementary coordinates s1=sum x_i, s2=sum_{i<j}x_i*x_j,
s3=x1*x2*x3, simultaneous x_i -> x_i^2-2 induces
s1'=s1^2-2*s2-6,
s2'=s2^2-2*s1*s3-4*s1^2+8*s2+12,
s3'=s3^2-2*s2^2+4*s1*s3+4*s1^2-8*s2-8.
Terminal all-three-equal c means (s1,s2,s3)=(3c,3c^2,c^3).

For generic c != +/-2, D_N-c is separable with N geometric roots.
The ordered three-fold fibre has length N^3. Its unordered image has
choose(N+2,3) geometric points allowing repeats. The symmetric terminal
scheme instead has length N^3 (map on Sym^3 has degree N^3), with local
length 6 for three distinct preimages, 3 for exactly two equal, and 1 for
all three equal. Thus generic scalar roots do not make the simultaneous
symmetric terminal scheme reduced. For k=0 its length is 1.
At c=2, roots of z^N=1 produce x=2,-2 simple (N even), all other
x-roots double; distinct x count N/2+1. For scalar multiplicities m_a,
the symmetric terminal local length at a multiset with occupation n_a
is (3!/product(n_a!))*product(m_a^n_a). Their sum remains N^3.
A reducedness claim from generic univariate roots alone is invalid.
A coordinate affine change preserves these facts.

## F1: cubic divisors and repeated strata

For a monic squarefree membership polynomial g of degree n, a monic cubic
q(t)=t^3-s1*t^2+s2*t-s3 divides g iff all three coefficients of rem(g,q)
vanish. Over an algebraic closure such q choose three distinct roots of g,
so the count is choose(n,3), with no repeated-root cubic divisors.
The divisor scheme is reduced: after splitting g over an etale extension,
its degree-three subschemes are discrete choices of three components;
invertible Vandermonde matrices give nonsingular coefficient equations.
Rational coefficient cubics include irreducible and partially split q;
coefficient rationality alone does not prove each coordinate is rational.
To recover actual F_p coordinate triples one must require full splitting
and then lift each coordinate to a target point and verify the point sum.

To include repeats while retaining a radical system, use separate reduced
strata: (a,a,b), a != b, with g(a)=g(b)=0 and the inequation saturated or
certified; and (a,a,a), g(a)=0. The exact geometric counts are n(n-1) for
an identified repeated value and n for the triple stratum. Combined with
choose(n,3), this equals choose(n+2,3). The repeated-value stratum is not
represented by q dividing squarefree g. If g is D_N-2, first removing its
repeated factors is essential; divisibility in the nonreduced polynomial
permits selected repeated roots and does not have the same conclusion.
The remainder recurrence is compact in k but its total polynomial degree
and solving cost need their own analysis. Small-degree circuits alone
prove neither a Groebner cost nor a relation-finding speed advantage.

## F2: auxiliary group, maps and complete fibres

For P-256, p=2^256-2^224+2^192+2^96-1 is 3 mod 4 and
v2(p+1)=96. On A:y^2=x^3+x, pairing x with -x cancels the quadratic
character sum because -1 is nonsquare; hence #A(F_p)=p+1.
Only (0,0) is nonzero rational 2-torsion. Consequently the 2-primary
rational subgroup is cyclic of order 2^96. Multiplication by odd
h=(p+1)/2^96 projects onto it; exact order requires [2^95]K != O,
[2^96]K=O. A deep rational 2-isogeny chain is possible from this subgroup,
but each kernel/image/order witness must be checked, not inferred from a
short initial chain. The auxiliary group and P-256 target remain distinct.

For E:y^2=x^3+a*x^2+b*x, b !=0 and a^2-4b !=0, quotient by (0,0)
has E':y^2=x^3-2a*x^2+(a^2-4b)*x, and
phi(x,y)=(x+a+b/x, y*(1-b/x^2)). At x=0 the affine formula is a pole
but its projective image is O; O maps to O. The quotient twice is
isomorphic to E by (x,y)->(x/4,y/8), yielding the dual and [2].
A chain using a different rational 2-torsion point first translates its
x-coordinate to zero. Denominator clearing can add pole roots; kernels
and O must be enumerated separately and cleared equations need exclusion.

A generic image Q with a rational full preimage P has fibre P+ker(phi).
A degree 2^k isogeny with all kernel points rational then gives exactly
2^k distinct rational points. In x-only coordinates it gives 2^k roots
except where P+K contains inverse pairs (Q is 2-torsion). Kernel x-values
have 2^(k-1) nonzero-pair representatives plus the order-two point:
2^(k-1) distinct finite x-values for k>=1. A generic elliptic fibre has
2^k x-values, while a Dickson fibre of degree n has n values only if its
chosen target enforces rationality and unramifiedness. Target-lift counts
need complete enumeration and Legendre/square-root checks; no independence
between lifts or between relation trials follows from one matched fibre.

Controls: a pole must not be accepted as an ordinary affine fibre root;
an x-only candidate with nonsquare auxiliary RHS is not an A(F_p) point;
a corrupted quotient target must fail map/complete-fibre verification.
No isogeny map from the target P-256 group into this smooth auxiliary group
is supplied by defining a coordinate domain on A.
