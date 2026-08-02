# Ten Advances in Mathematics and Theoretical Computer Science

**OpenAI** — PDF dated 2026-08-01 (`/CreationDate D:20260801082921-00'00'`)

> Frozen source record. Text mechanically extracted from the primary PDF
> `https://cdn.openai.com/pdf/ten-proofs-oai.pdf` (2.27 MB, 249 pages,
> retrieved 2026-08-02, HTTP 200) using `pypdf`. It is preserved here as an
> immutable input because this container is ephemeral and acquiring the PDF
> required an egress-policy change.
>
> EXTRACTION CAVEAT: this is a mechanical text layer, not a faithful
> transcription. Mathematical display is reflowed and often broken across
> lines; ligatures render as `ﬁ`/`ﬂ`; subscripts, superscripts and fractions
> lose their structure. Any formula quoted from this file MUST be checked
> against the PDF itself before it is relied on. Prose and theorem statements
> survive far better than formulas.
>
> PDF metadata as read: Title "Ten Advances in Mathematics and Theoretical
> Computer Science"; Author "OpenAI"; Subject "A collection of research papers
> by an internal model at OpenAI"; Creator "LaTeX with hyperref"; Producer
> "xdvipdfmx (0.1)".

---


===== PAGE 1 =====
Ten Advances in Mathematics
and Theoretical Computer Science
OpenAI
===== PAGE 2 =====
Abstract
We present a collection of results obtained by an internal OpenAI model, spanning mathe-
matics and theoretical computer science:
1. High-dimensional sphere packing. The asymptotic strength of the Cohn–Elkies
linear program is determined exactly. This gives an improved general packing bound
in high dimensions and settles the corresponding Fourier sign-uncertainty problem
asymptotically.
2. Binary and spherical codes. Classical upper bounds for ﬁxed-distance binary and
spherical codes are improved by exponential factors for all parameters. The spherical
construction also recovers the sphere-packing exponent of Chapter 1.
3. Non-soﬁc groups. An explicit non-soﬁc group is constructed, resolving the question
of whether every countable group admits ﬁnite permutation approximations. The
argument uses property- (T ) expanders and the binary Leavitt algebra.
4. Connes’s rigidity conjecture. Inﬁnitely many pairwise nonisomorphic property-
(T ) groups are constructed with the same group von Neumann algebra, disproving
Connes’s conjecture and answering a related ﬁnite-to-one question of Popa.
5. Arithmetic circuit complexity . For the permanent, division-free circuits require
Ω(n2 log log n) gates, while formulas require Ω(n4/ log n) leaves.
6. Quantum parallel repetition. Exponential parallel repetition is proved for every
ﬁnite two-player entangled game, extending the classical repetition principle beyond
previously treated special classes of quantum games.
7. Closest vector problem. A direct reduction from 3SAT gives n1/400-factor hard-
ness for the Euclidean closest vector problem, with related consequences for binary
decoding and other lattice norms.
8. Ehrhart’s volume conjecture. The sharp bound (n + 1)n/n! is proved in every
dimension for convex bodies whose barycenter is their only interior lattice point.
9. Multicolor Ramsey numbers. A superexponential lower bound proves Rk(3) =
kΘ(k).
10. Compactness and degeneracy . Separate bipartite graph constructions disprove
two conjectures in extremal graph theory: the compactness conjecture of Erdős and
Simonovits and a degeneracy conjecture of Erdős.
i
===== PAGE 3 =====
Chapter 1
Exponential Growth Rate of the Cohn–Elkies
Sphere Packing Linear Program
Abstract. We determine the exact exponential decay rate of the Cohn–Elkies
sphere-packing linear program. If ∆d denotes the maximal sphere-packing den-
sity in Rd and LPd denotes the optimal density bound furnished by this program,
then
lim sup
d→∞
∆1/d
d ≤ lim
d→∞
LP1/d
d =
√e
2π.
The positive- and negative-eigenvalue Fourier sign-uncertainty radii are both
(1/π +o(1))
√
d.
Contents
1. Introduction
2. Fourier-analytic preliminaries
3. The universal Cohn–Elkies lower bound
4. The admissible primal upper bound
Appendix A. Comparison of the sign-uncertainty constants
References
1
===== PAGE 4 =====
1. Introduction
Sphere packing asks how densely congruent balls can ﬁll Euclidean space. For centers sep-
arated by at least 1, let ∆d be the supremum of the upper densities of radius- 1/2 balls in Rd.
The Fourier-analytic linear-programming method of Gorbachev and Cohn–Elkies [ Gor00, Coh02,
CE03] bounds this density using an auxiliary function and its Fourier transform. Viazovska used
this framework to prove that the E8 lattice gives the optimal packing in dimension eight [ Via17];
Cohn, Kumar, Miller, Radchenko, and Viazovska subsequently established the optimality of the
Leech lattice in dimension twenty-four [ CKMR V17]. Related Fourier interpolation formulas re-
veal further structure behind these exceptional conﬁgurations [ R V19, CKMR V22].
By contrast, the behavior of the linear program in high dimensions remained poorly under-
stood. Cohn and Zhao proved that it is always at least as strong as the Kabatianskii–Levenshtein
spherical-code bound [ CZ14], but whether it improves the classical high-dimensional sphere-
packing exponent remained open. Motivated by the modular bootstrap [ HMR19], Afkhami-
Jeddi, Cohn, Hartman, de Laat, and Tajdini conjectured its high-dimensional rate [ AJCHLT20,
§ 3].
We use the Fourier convention and unit-ball volume
ˆf (ξ) =
∫
Rd
f (x)e− 2πix·ξdx, v d = πd/2
Γ(d/2 + 1). (1)
A ball of radius 1/2 has volume vd/2d. For the real Schwartz space S(Rd; R), deﬁne
Ad =
{
f ∈ S (Rd; R) : ˆf (0)> 0, ˆf ≥ 0 on Rd, f ≤ 0 on {|x| ≥1}
}
, (2)
and the associated linear-programming bound by
LPd = vd
2d inf
f ∈Ad
f (0)
ˆf (0)
. (3)
Fourier inversion gives f (0) > 0. The Gorbachev–Cohn–Elkies bound [ Gor00, CE03] assigns
everyf ∈ Ad the density upper bound vdf (0)/(2dˆf (0)), so ( 3) yields
∆d ≤ LPd. (4)
Our main theorem proves the exponential rate conjectured in [ AJCHLT20, Conjs. 3.1–3.2].
Theorem 1.1. Asd → ∞ , LP1/d
d − →
√
e/(2π).
By ( 4), the theorem gives ∆d ≤ LPd = 2 − (α∗ +o(1))d, where α∗ = 1
2 log2(2π/e) = 0 .6044... .
This is the ﬁrst improvement since 1978 to the general sphere-packing exponent. The classi-
cal Kabatianskii–Levenshtein exponent was 0.59905576... [KL78, Lev79]; subsequent spherical-
code reﬁnements had improved only lower-order factors [ CZ14, SZ24, Z24]. The matching lower
bound shows that no Cohn–Elkies auxiliary function can improve this exponent.
Our companion paper in Chapter 2 recovers the upper-bound direction of Theorem 1.1 as a
small-distance limit of spherical-code bounds.
The packing sign conditions are related to the Bourgain–Clozel–Kahane uncertainty princi-
ple for eventually nonnegative Fourier eigenfunctions [ BCK10, GOSS17, GOSR21]. Cohn and
Gonçalves [ CG19] introduced its anti-self-Fourier counterpart and connected it with sphere
packing. If g ∈L1(Rd; R) satisﬁes ˆg =ςg for ς ∈ {−1, +1}, then ˆg ∈L1 and Fourier inversion
supplies a continuous representative of g. Using this representative for all pointwise values and
sign conditions, deﬁne
r(g) = inf {R ≥ 0 : g(x) ≥ 0 for |x| ≥R}, (5)
Aς (d) = inf {r(g) : 0 ̸=g ∈L1(Rd; R), ˆg =ςg, g(0) = 0 }. (6)
Here r(g) = ∞ when no such radius exists. The signs +1 and −1 give the original and comple-
mentary uncertainty problems, respectively.
The negative-eigenvalue problem also arises in the spinless modular bootstrap, where mod-
ular S-antisymmetry produces anti-self-Fourier test functions whose eventual sign controls the
2
===== PAGE 5 =====
spectral gap [ HMR19, AJCHLT20]. General lower bounds for sign uncertainty and limita-
tions of Gaussian–polynomial test functions of sublinear degree appear in [ Edw25] and [ CDG24,
Thm. 1.2], respectively. The next theorem proves the asymptotic equality conjectured in [ CG19,
Conj. 1.5] and [ AJCHLT20, (3.5)], with the common value predicted in [ AJCHLT20, (3.3)]. Al-
though these asymptotics coincide, Appendix A observes that A+(d)< A− (d) for all d.
Theorem 1.2. The Fourier-eigenfunction sign-uncertainty constants satisfy
lim
d→∞
A+(d)√
d
= lim
d→∞
A− (d)√
d
= 1
π.
The proof reduces both problems to the last sign changes of Fourier eigenfunctions. In § 3,
Proposition 3.1 shows that a radial Schwartz function g satisfying ˆg = ±g and g(0) = 0 has
exponentially little L1 mass inside B(0,c
√
d) whenever c < 1/π. For an admissible packing
function F , let a = ( ˆF (0)/F (0))1/d and h(x) = F (ax). Then h(0) = ˆh(0), while the nonzero
functiong =ˆh−h is anti-self-Fourier, vanishes at the origin, and is nonnegative outsideB(0, 1/a).
Since
∫
g = 0, its negative part has mass ∥g∥1/2, all of which lies in this ball. The mass estimate
therefore forces 1/a ≥ (1/π − o(1))
√
d. In § 4, Theorem 4.1 modiﬁes the Mellin transform of
a Gaussian to construct a Fourier pair and a self-Fourier function whose required exterior sign
conditions begin at (1/π +o(1))
√
d. Stirling’s formula converts the matching radius bounds
into the packing exponent
√
e/(2π).
2. Fourier-analytic preliminaries
We reduce the packing and sign-uncertainty problems to radial functions and establish the
Mellin–Fourier identities used in both bounds. We repeatedly use the gamma recurrence and
reﬂection formulas [ DLMF, § 5.5], together with their consequences for real b ̸= 0:
Γ(z + 1) = zΓ(z), Γ(z)Γ(1 −z) = π
sin(πz),
|Γ(ib)|2 = π
b sinh(πb), |Γ(1/2 +ib)|2 = π
cosh(πb).
(7)
2.1. Radial reduction. Throughout, Fourier transforms use the convention ( 1), and we denote
a radial function and its one-variable proﬁle by the same symbol. With normalized Haar measure
on O(d), deﬁne the rotational average
Rf (x) =
∫
O(d)
f (Ux )dU.
Write Srad(Rd; R) for the real Schwartz functions depending only on |x|, and L1
rad(Rd; R) for the
radial real integrable functions. Set Arad
d = Ad ∩ Srad(Rd; R). For every continuous integrable
f , rotational invariance gives
ˆRf = Rˆf, (Rf )(0) = f (0), ˆRf (0) = ˆf (0).
Consequently, rotational averaging preserves every sign condition in ( 2), so the inﬁmum in ( 3)
is unchanged when Ad is replaced by Arad
d [CE03, CG19]. If ˆg =ςg , then
ˆRg =ςRg, r (Rg) ≤ r(g).
Moreover, Rg ̸= 0 wheneverg ̸= 0 is eventually nonnegative. Indeed, if Rg = 0, the nonnegative
values ofg outside a ball have zero rotational average, so g vanishes outside that ball. Its Fourier
transform is then entire, and ˆg =ςg makes this entire function vanish on the same exterior region,
forcing g = 0.
We also need approximation by Schwartz functions preserving the Fourier eigenvalue and
vanishing at the origin. Suppose that g ∈ L1
rad(Rd; R) satisﬁes ˆg = ςg and g(0) = 0 , where
ς ∈ {−1, +1}. For n ≥ 1, set
κn(x) = nde− πn2|x|2
, η n(x) = e− π|x|2/n2
, q n =ηn(g ∗κn).
3
===== PAGE 6 =====
Gaussian molliﬁcation gives qn ∈ Srad(Rd; R),qn → g, and ˆqn =κn ∗(ηnˆg) → ˆg inL1. Moreover,
qn(0) → g(0) = 0 and ˆqn(0) =
∫
qn → ˆg(0) = 0 . Deﬁne
pn = qn +ςˆqn
2 , ψ +(x) = e− π|x|2
, ψ − (x) =
(
|x|2 − d
4π
)
e− π|x|2
.
Since ˆpn =ςp n, ˆψς =ςψ ς , and ψς (0) ̸= 0, the correction
gn =pn − pn(0)
ψς (0)ψς
satisﬁes gn ∈ Srad(Rd; R), ˆgn =ςg n, gn(0) = 0 , and gn → g in L1.
2.2. The radial Mellin transform. For a radial Schwartz functiong, writer = |x|andρ = |ξ|
for the spatial and frequency radii, respectively, and set
λ = d
2, S d = 2πd/2
Γ(d/2).
Here Sd is the area of the unit sphere, and polar integration gives
∫
Rd
g(x)dx =Sd
∫∞
0
g(r)rd− 1dr.
Forρ> 0, the Fourier transform has the Hankel representation
ˆg(ρ) = 2πρ1− d/2
∫∞
0
g(r)Jd/2− 1(2πrρ)rd/2dr.
Because its Bessel kernel depends on rρ, the radial Fourier transform becomes particularly
simple after a Mellin transform: it reﬂects the Mellin variable and multiplies by an explicit
gamma factor. For Rez > 0, t ∈ R, and r > 0, the Mellin transform, its restriction to the
critical line, and Mellin inversion [ PK01] are
Mg(z) =
∫∞
0
g(r)rz− 1dr, X g(t) = Mg(λ −it),
g(r) = r− λ
2π
∫
R
Xg(t)ritdt.
(8)
In particular, the radial integration normalization is
ˆg(0) =
∫
Rd
g(x)dx =SdMg(d).
In logarithmic radius v = log r, set Φg(v) = eλvg(ev). Smoothness at r = 0 gives exponential
decay of Φg and all its derivatives as v → −∞ , while the Schwartz decay of g gives rapid decay
as v → +∞ . Thus Φg ∈ S (R; R), and ordinary one-dimensional Fourier inversion gives
Xg(t) =
∫
R
Φg(v)e− itvdv, Φg(v) = 1
2π
∫
R
Xg(t)eitvdt.
The standard Mellin transform of the Hankel kernel gives, for 0< Rez <d, the Mellin–Hankel
functional equation [ SW71, Ch. IV], [ DLMF, (10.22.43)]:
Mˆg(z) = πλ− z Γ(z/2)
Γ((d −z)/2)Mg(d −z). (9)
If g(0) = ˆg(0) = 0 , smooth radiality gives g(r),ˆg(r) = O(r2) at the origin. Both Mellin
transforms therefore extend holomorphically to Rez >−2, and ( 9) continues to Rez = 0:
Mg(d) = S− 1
d ˆg(0) = 0, M g(d −z) = −zM ′
g(d) +O(z2), Γ(z/2) = 2
z +O(1),
so the apparent gamma pole at z = 0 cancels. The line Rez = d/2 is ﬁxed by the reﬂection
z ↦→d −z. On this line the Fourier transform acts, for t ∈ R, by
Xˆg(t) = mλ(t)Xg(−t), m λ(t) = πit Γ((λ −it)/2)
Γ((λ +it)/2). (10)
4
===== PAGE 7 =====
Fort ∈ R, its multiplier satisﬁes
mλ(−t) = mλ(t) = mλ(t)− 1, |mλ(t)|= 1.
3. The universal Cohn–Elkies lower bound
By the radial reduction in § 2.1, assume that the admissible packing function F is radial. Let
a = ( ˆF (0)/F (0))1/d and deﬁne h(x) = F (ax). Then h(0) = ˆh(0), and g = ˆh − h is anti-self-
Fourier, vanishes at the origin, and is nonnegative for |x| ≥ 1/a; see ( 29)–(30). The proof of
Theorem 3.8 veriﬁes that g ̸= 0. Since
∫
g = 0, its negative part has mass ∥g∥1/2, all of which
lies in B(0, 1/a).
Proposition 3.1 shows that every radial Schwartz Fourier eigenfunction vanishing at the origin,
of either eigenvalue, has exponentially little L1 mass in B(0,c
√
d) when c < 1/π. Thus the
negative half-mass of g cannot ﬁt inside this ball, forcing 1/a ≥ (1/π −o(1))
√
d.
The obstruction comes from the Mellin–Fourier identity ( 9). Lemma 3.2 bounds a normalized
Mellin transform Z on the strip |Imt|< d/2: total L1 mass controls the upper boundary,
while the Fourier functional equation controls the lower boundary. Writing λ = d/2, Poisson
interpolation gives
log |Z(s +iσλ)| ≤Hσ(s) ≤ λMσ
(
log(2πc2) +Jσ
)
+Oσ(logλ), M σ = 1 −σ
2 ,
by Lemma 3.3. The sharp constant enters through Lemma 3.4: Jσ → log(π/2) as σ ↑ 1, so the
parenthesized rate tends to log(π2c2). It is negative exactly when c <1/π. An all-frequency
bound and shifted Mellin inversion, in Lemmas 3.5 and 3.6, turn this negativity into the interior-
mass estimate; Stirling’s formula then yields the packing lower bound.
3.1. The Mellin-strip obstruction.
Proposition 3.1. For every 0 < c <1/π, there exist Cc,γ c > 0 and d0(c) ∈ N such that, for
every d ≥ d0(c), every ς ∈ {−1, +1}, and every nonzero g ∈ S rad(Rd; R) satisfying ˆg =ςg and
g(0) = 0 , one has ∫
|x|<c
√
d
|g(x)|dx ≤ Cce− γcd∥g∥1. (11)
Fix 0 < c <1/π, d ∈ N, λ = d/2, R = c
√
d, and a nonzero g ∈ S rad(Rd; R) with ˆg = ςg ,
ς ∈ {− 1, +1}, and g(0) = 0 . Let Sd = 2πλ/Γ(λ) be the area of the unit sphere. In the
logarithmic coordinate r =Rev, normalize the Mellin inversion formula ( 8) by setting
φ(v) = Sd
∥g∥1
(Rev)dg(Rev), Z (t) = Sd
∥g∥1
Rλ+itXg(t), (12)
∥φ∥1 = 1,
∫
R
φ = 0,
∫0
−∞
|φ(v)|dv = 1
∥g∥1
∫
|x|<R
|g(x)|dx. (13)
The second line follows from polar integration and ˆg(0) = ςg (0) = 0 .
Lemma 3.2. For every −1<σ < 1, the function Z is bounded and holomorphic on a neighbor-
hood of the strip |Imt| ≤λ. Its boundary values satisfy |Z(y+iλ)| ≤1 and log|Z(y−iλ)| ≤hλ(y)
for y ̸= 0, where the lower-boundary majorant is
hλ(y) = λ log(πR2) + log |Γ(−iy/2)| −log |Γ(λ +iy/2)|. (14)
Writingθ =π(1 +σ)/2, deﬁne
Pσ(T ) = sinθ
4(cosh(πT/ 2) − cosθ), M σ =
∫
R
Pσ = 1 −σ
2 . (15)
Then
|Z(s +iσλ)| ≤exp
( ∫
R
Pσ(T )hλ(s −λT )dT
)
(s ∈ R).
5
===== PAGE 8 =====
Proof. Since g(0) = ˆg(0) = 0 , the holomorphic continuation and pole cancellation following
(9) show that Z is holomorphic whenever Imt >−λ − 2. In particular, it is holomorphic on
a neighborhood of the closed strip. Its upper-boundary values follow from ( 12), whereas the
Mellin–Fourier functional equation ( 9) gives the lower-boundary values:
Z(y +iλ) =
∫
R
φ(v)e− iyvdv, |Z(y +iλ)| ≤1, (16)
Z(y −iλ) = ς(πR2)λ+iy Γ(−iy/2)
Γ(λ +iy/2)Z(−y +iλ). (17)
Taking absolute values and using ( 16) gives log |Z(y − iλ)| ≤ hλ(y), independently of ς. At
y = 0, the zero Z(iλ) = 0 from ( 13) cancels the gamma pole in ( 17). Hence Z(y −iλ) remains
bounded there, although
hλ(y) = − log |y|+Oλ(1) ( y → 0).
Fort0 =s+iσλ, the conformal map t ↦→exp(π(t+iλ)/(2λ)) and the upper-half-plane Poisson
formula [ Ahl79] give the lower-edge harmonic measure λ− 1Pσ((s − y)/λ)dy, with Pσ and Mσ
as in ( 15). The complementary upper-edge measure is (1 +σ)/2, and its boundary bound ( 16)
contributes nothing.
The logarithmic singularity of hλ requires a bounded truncation before applying the Poisson
principle. The actual lower-boundary values satisfy
sup
y∈R
|Z(y −iλ)| ≤SdRd
∥g∥1
∫∞
0
|g(r)|
r dr< ∞.
Indeed, g(r) = O(r2) at zero and is Schwartz at inﬁnity. More generally, for −λ ≤ η ≤ λ, ( 12)
gives
|Z(s +iη)| ≤SdRλ− η
∥g∥1
∫∞
0
|g(r)|rλ+η− 1dr.
Splitting at r = 1 bounds this expression uniformly in s and η, so Z is bounded on the closed
strip. Choose D> max{0, supy log |Z(y −iλ)|}. The strip Poisson principle [ Ahl79], applied to
log |Z|with lower-boundary majorant min{hλ,D } and upper-boundary majorant 0, gives
log |Z(t0)| ≤
∫
R
1
λPσ
( s −y
λ
)
min{hλ(y),D }dy.
The kernel in ( 15) decays exponentially, the singularity of hλ is locally integrable, and Stirling’s
formula gives hλ(y) = −λ log |y|+Oλ(1) at inﬁnity [ DLMF, § 5.11]. Dominated convergence
therefore permits D → ∞ , and the substitution T = (s −y)/λ yields
|Z(s +iσλ)| ≤eHσ(s), H σ(s) =
∫
R
Pσ(T )hλ(s −λT )dT. □ (18)
Lemma 3.3. For every −1<σ < 1, there exists Cσ > 0, independent of d, c, and g, such that
∫
R
Pσ(T )
⏐⏐⏐⏐hλ(λT ) −λ
(
log(2πc2) −
∫1
0
log
√
x2 +T 2/4dx
) ⏐⏐⏐⏐dT ≤ Cσ log(2 +λ). (19)
Deﬁne
Jσ = − 1
Mσ
∫
R
Pσ(T )
∫1
0
log
√
x2 +T 2/4dxdT.
Then, for every s ∈ R,
Hσ(s) ≤ Hσ(0) = λMσ
(
log(2πc2) +Jσ
)
+Oσ(log(2 +λ)). (20)
Proof. To estimate the lower-boundary majorant ( 14) with R =c
√
2λ, put
fT (x) = log
√
x2 +T 2/4, b = λT
2 .
6
===== PAGE 9 =====
If d = 2n, so that λ =n, the gamma recurrence in ( 7) and |Γ(−ib)|= |Γ(ib)|give, for T ̸= 0,
hn(nT ) = n log(2πc2) −
n− 1∑
k=0
fT (k/n).
Monotonicity of fT bounds the Riemann-sum error by fT (1) −fT (0); thus
0 ≤ hn(nT ) −n
(
log(2πc2) −
∫1
0
fT (x)dx
)
≤ 1
2 log
(
1 + 4
T 2
)
.
If d = 2n + 1, so that λ =n + 1
2 , the gamma identities ( 7) instead give
hλ(λT ) = λ log(2πc2) −
n− 1∑
k=0
fT
( k + 1/2
λ
)
+ 1
2 logλ + 1
2 log coth(π|b|)
|b| .
The midpoint Riemann-sum error on [0,n/λ ] is at most fT (n/λ) −fT (0); the remaining interval
[n/λ, 1] has length 1/(2λ). Together, these contributions are bounded by
C
(
1 + log(2 + |T |) + log(2 + |T |− 1)
)
.
AddingC log(2 +λ) also bounds the gamma endpoint correction 1
2 logλ + 1
2 log(coth(π|b|)/|b|).
Since (15) givesPσ(T ) ≪ σ e− π|T |/2, and log(2 +|T |− 1) is locally integrable, integrating the even-
and odd-dimensional bounds proves ( 19).
It remains to identify the maximum of the Poisson extension Hσ. Both hλ and Pσ are even,
and the digamma series [ DLMF, § 5.7] gives, for y >0,
h′
λ(y) = 1
2 (Imψ(λ +iy/2) − Imψ(iy/2))< 0, Imψ(a +ib) =
∞∑
k=0
b
(k +a)2 +b2.
Hereψ = Γ ′/Γ. The explicit kernel ( 15) is likewise decreasing on (0, ∞ ). For N >0, the function
qN = (hλ +N )+ is nonnegative, integrable, even, and decreasing there. The convolution of two
such functions is largest at zero. Subtracting NM σ and letting N → ∞ , using the exponential
decay of Pσ, therefore gives Hσ(s) ≤ Hσ(0). Evaluating at zero with ( 19) proves ( 20). □
Lemma 3.4. ForJσ deﬁned in Lemma 3.3,
lim
σ↑1
Jσ = log π
2.
Consequently, for every 0<c< 1/π, there exists σ =σ(c) ∈ (−1, 1) such that log(2πc2) +Jσ <
0.
Proof. With T = 2u, divide the lower-edge harmonic measure Pσ(T )dT from ( 15) by its total
mass Mσ. The corresponding probability density in u is
pσ(u) = 2Pσ(2u)
Mσ
= sinθ
(1 −σ)(cosh(πu) − cosθ).
Asσ ↑1, sinθ/(1 −σ) → π/2. The densities pσ are uniformly bounded by Ce− π|u|and therefore
converge in L1(R) to
p(u) = π
4 sech2
( πu
2
)
.
The characteristic function of this density is
∫
R
p(u)eitudu = t
sinht, t ∈ R, (21)
interpreted as 1 at t = 0 . For t > 0, a contour shift by 2i across the double pole at i gives
(1 − e− 2t)
∫
p(u)eitudu = 2te− t; evenness handles t <0. Deﬁne I(x) =
∫
Rp(u) log
√
x2 +u2du.
Forx> 0, the Laplace representation of x/(x2 +u2), ( 21), and the trigamma integral [ DLMF,
§ 5.9] yield
I ′(x) =
∫∞
0
e− xt t
sinhtdt = 1
2ψ′
( x + 1
2
)
.
7
===== PAGE 10 =====
Since both I(x) and ψ((x + 1)/2) + log 2 equal logx +o(1) at inﬁnity [ DLMF, § 5.11], their
integration constants agree. Local integrability at u = 0 extends the identity to x = 0:
∫
R
p(u) log
√
x2 +u2du =ψ
( x + 1
2
)
+ log 2 ( x ≥ 0). (22)
The uniform exponential bound on pσ and local integrability of log |u|justify dominated con-
vergence in Jσ. Since ∫1
0
ψ
( x + 1
2
)
dx = 2 log Γ(1)
Γ(1/2) = − logπ,
(22) gives the exact threshold
lim
σ↑1
Jσ = log π
2, log(2πc2) + log π
2 = log(π2c2).
If c< 1/π, choose σ =σ(c)< 1 suﬃciently close to 1 that
δc = −
(
log(2πc2) +Jσ(c)
)
> 0. □ (23)
Fixσ =σ(c) andδc> 0 as in ( 23). We ﬁrst bound the Mellin transform Z on the horizontal
line Imt =σλ, and then use that bound to control the mass of g inside B(0,c
√
d).
Lemma 3.5. There exist γc,C c,B c > 0, depending only on c, such that, for every suﬃciently
larged,
Hσ(s) ≤ −γcλ (s ∈ R),
∫
R
|Z(s +iσλ)|ds ≤ Ccλe− γcλ.
Moreover, after increasing Bc if necessary,
Hσ(λS) ≤ − Mσλ
2 log |S|
Cc
(|S| ≥Bc).
Proof. The maximum estimate for Hσ in ( 20), together with log(2πc2) +Jσ = −δc, gives
Hσ(s) ≤ −λMσδc +Oσ(logλ) ≤ −γcλ (s ∈ R)
for all suﬃciently large d, with γc> 0 independent of s, g, and the Fourier eigenvalue ς.
To control all Mellin frequencies, apply the gamma identities ( 7) to ( 14). In both parities,
hλ(λU ) ≤ λ log 4πc2
|U | +Eλ(U ) ( U ̸= 0),
where
Eλ(U ) =



0, λ ∈ N,
1
2 log coth
( πλ|U |
2
)
, λ ∈ N + 1
2.
Each gamma-recurrence factor has modulus at least |λU |/2; in odd dimension, the remaining
ratio at b = λU/2 contributes Eλ(U ). Expanding log cothx in its convergent odd-exponential
series gives, in odd dimension,
∫
R
Eλ(U )dU = 2
πλ
∫∞
0
log cothxdx = π
4λ.
Thus in both parities the Pσ-convolution of Eλ is at most π∥Pσ∥∞ /(4λ). Consequently, ( 18)
gives
Hσ(λS) ≤ λMσ log(4πc2) −λ
∫
R
Pσ(T ) log |S −T |dT +Oσ(λ− 1).
Split the logarithmic integral at |T |= |S|/2. The exponential decay of ( 15) gives mass Mσ +
Oσ(e− π|S|/4) on |T | ≤ |S|/2; the possible negative contribution from |S −T |< 1 isOσ(e− π|S|/2),
by local integrability of log |S −T |. Hence, for some Bc,C ′
c> 0,
∫
R
Pσ(T ) log |S −T |dT ≥ Mσ
2 log |S| −C′
c (|S| ≥Bc).
8
===== PAGE 11 =====
After increasing C′
c, the estimates for Hσ on the whole line and at large frequencies become
Hσ(s) ≤ −γcλ (s ∈ R), (24)
Hσ(λS) ≤ − Mσλ
2 log |S|
C′c
(|S| ≥Bc). (25)
Choose B >max{Bc,C ′
c} and q =Mσλ/2> 1. The two bounds in ( 24)–(25) yield
∫
|s|≤Bλ
eHσ(s)ds ≤ 2Bλe− γcλ,
∫
|s|>Bλ
eHσ(s)ds ≤ 2λC′
c
q − 1
( B
C′c
) 1− q
.
The second bound decays at rate (Mσ/2) log(B/C ′
c) > 0. Decreasing γc if necessary, and
applying ( 18), we obtain
∫
R
|Z(s +iσλ)|ds ≤ Ccλe− γcλ. □ (26)
The global L1 estimate ( 26) for Z on Imt =σλ now controls φ(v) for v <0, corresponding
by ( 13) to |x|<c
√
d.
Lemma 3.6. For every 0 < c <1/π, there exist Cc,γ c > 0 and d0(c) ∈ N, independent of g
and ς, such that ∫0
−∞
|φ(v)|dv ≤ Cce− γcd (d ≥ d0(c)).
Proof. Let G(v) = e(σ− 1)λvφ(v). The normalized proﬁle φ from ( 12) satisﬁes
∫
R
|G(v)|dv = SdR(1− σ)λ
∥g∥1
∫∞
0
|g(r)|r(1+σ)λ− 1dr< ∞.
Thus G ∈ L1(R), and ( 12) identiﬁes its angular-frequency Fourier transform
∫
RG(v)e− isvdv
withZ(s +iσλ). The integrability of this transform follows from ( 26), so Fourier inversion gives
Z(s +iσλ) =
∫
R
e(σ− 1)λvφ(v)e− isvdv, φ (v) = e(1− σ)λv
2π
∫
R
Z(s +iσλ)eisvds.
Taking absolute values and integrating over v <0 contributes
∫0
−∞ e(1− σ)λvdv = ((1 − σ)λ)− 1.
Combining this with ( 26) and λ =d/2, and decreasing γc if necessary, gives
∫0
−∞
|φ(v)|dv ≤ 1
2π(1 −σ)λ
∫
R
|Z(s +iσλ)|ds ≤ Cce− γcd. □ (27)
Proof of Proposition 3.1. By (13), the left side of ( 27) is precisely ∥g∥− 1
1
∫
|x|<c
√
d |g(x)|dx. Thus
(27) proves ( 11), uniformly in g and its Fourier eigenvalue ς. □
3.2. The packing lower bound.
Proposition 3.7. For every 0<c< 1/π, there exists d0(c) ∈ N such that, for every d ≥ d0(c)
and ς ∈ {− 1, +1}, no nonzero g ∈ L1(Rd; R) satisﬁes ˆg = ςg , g(0) = 0 , and g(x) ≥ 0 for
|x| ≥c
√
d. Here g denotes its continuous Fourier-inversion representative.
Proof. First, suppose that g is a radial Schwartz eigenfunction. Since
∫
g = ˆg(0) = ςg (0) = 0 ,
its negative part g− = max{−g, 0} has integral ∥g∥1/2. The assumption g(x) ≥ 0 for |x| ≥c
√
d
forces g− to vanish outside B(0,c
√
d), contradicting ( 11) once Cce− γcd< 1/2.
For general g ∈ L1, the radial reduction in § 2.1 shows that h = Rg ̸= 0 and has the
same Fourier eigenvalue, origin value, and exterior sign. The approximation constructed there
gives radial Schwartz eigenfunctions hn → h in L1 with ˆhn = ςh n and hn(0) = 0 . Writing
(hn)− = max{−hn, 0} and R =c
√
d, the exterior nonnegativity of h gives
∫
Rd
(hn)− ≤
∫
|x|<R
|hn(x)|dx +
∫
|x|≥R
|hn(x) −h(x)|dx.
9
===== PAGE 12 =====
Applying ( 11) to hn therefore implies
1
2 ∥hn∥1 =
∫
Rd
(hn)− ≤ Cce− γcd∥hn∥1 + ∥hn −h∥1.
Letting n → ∞ gives ∥h∥1/2 ≤ Cce− γcd∥h∥1, which contradicts h ̸= 0 for all suﬃciently large
d. □
Theorem 3.8. There is a sequence ϵd → 0 such that, for every suﬃciently large d and every
F ∈ Ad,
F (0)
ˆF (0)
≥ 2d
vd
( √e
2π −ϵd
) d
. (28)
Proof. By radial reduction, replace F with its rotational average, which preserves F (0), ˆF (0),
and admissibility. Deﬁne a = (ˆF (0)/F (0))1/d > 0, h(x) = F (ax), and g =ˆh − h. The Fourier
convention (1) and the admissibility conditions ( 2) give
ˆh(ξ) = a− dˆF (ξ/a), h (0) = ˆh(0) = F (0), (29)
ˆg = −g, g(0) = 0, g(x) = a− dˆF (x/a) −F (ax) ≥ 0 ( |x| ≥1/a).(30)
Moreover,g ̸= 0: otherwise h =ˆh ≥ 0, while h(x) = F (ax) ≤ 0 for |x| ≥1/a. Thus h would be
a nonzero compactly supported self-Fourier function, contradicting Fourier analyticity. Hence
Proposition 3.7 gives 1/a > c
√
d, uniformly in F , for each ﬁxed c < 1/π and all suﬃciently
large d. Consequently,
lim inf
d→∞
1√
d
inf
F ∈Ad
(
F (0)
ˆF (0)
) 1/d
≥ c (0<c< 1/π).
Taking the supremum over c< 1/π yields
inf
F ∈Ad
(
F (0)
ˆF (0)
) 1/d
≥
( 1
π −o(1)
) √
d. (31)
Combining (31) with Stirling’s formula [ DLMF, § 5.11], v1/d
d = (1 +o(1))
√
2πe/d gives (28), for
a sequence ϵd → 0 independent of F . □
4. The admissible primal upper bound
Section 3 established
min


inf
F ∈Ad
(
F (0)
ˆF (0)
) 1/d
, A− (d), A+(d)


≥
( 1
π −o(1)
) √
d.
We explain how the upper bounds in the introduction reduce to constructing functions whose
sign changes occur at the same radius. Suppose that real radial Schwartz functions f−,f + satisfy
ˆf− =f+> 0, f − (0) = f+(0), f − (x)< 0 ( |x| ≥R).
ForF (x) = f− (Rx), Fourier scaling gives
ˆF (ξ) = R− df+(ξ/R)> 0, F (x)< 0 ( |x| ≥1), F (0)
ˆF (0)
=Rd.
Consequently F ∈ A d and LPd ≤ vd(R/2)d. The diﬀerence g− = f+ − f− is anti-self-Fourier,
vanishes at the origin, and is positive for |x| ≥ R, so it also proves A− (d) ≤ R. A self-
Fourier function f0 satisfying f0(0) = 0 and f0(x)> 0 for |x| ≥R similarly proves A+(d) ≤ R.
Thus all the upper bounds reduce to producing one Fourier pair, one self-Fourier function, and
R = (1/π +o(1))
√
d.
10
===== PAGE 13 =====
Theorem 4.1. There is ϵ0> 0 such that, for every ﬁxed 0<ϵ<ϵ 0 and every suﬃciently large
dimension d, there exist real radial Schwartz functions f−,f +,f 0 and a radius Rϵ,d > 0 such
that f+> 0 everywhere,f− < 0<f 0 whenever |x| ≥Rϵ,d, and
ˆf− =f+, ˆf0 =f0, f − (0) = f+(0)> 0, f 0(0) = 0.
Moreover,
lim
ϵ↓0
lim
d→∞
Rϵ,d√
d
= 1
π.
4.1. Outline of the construction. We need a Fourier pair f−,f + = ˆf− and a self-Fourier
function f0, with f+ > 0 everywhere and f− < 0 < f0 outside a common radius. In Mellin
coordinates, ( 10) reduces these Fourier symmetries to reﬂection of the frequency. The Gaussian
gG(r) = 2πλ/2e− πr2
, E G
λ (t) = πit/2Γ
( λ −it
2
)
, λ = d
2,
already obeys mλ(t)EG
λ (−t) = EG
λ (t). Multiplication by an even factor therefore preserves
Fourier symmetry. We choose Eλ(t) = EG
λ (t)eλhϵ(t/λ), where the even perturbation hϵ in ( 36) is
determined by a signed density w.
The variablea in that density parametrizes radial dilations: the Mellin multiplier cos(at/λ)− 1
corresponds to
g(r) ↦− →eag(rea/λ) +e− ag(re− a/λ)
2 −g(r).
A shell is an interval of these dilation parameters supporting one component of w. Our negative
componentws moves the sign radius inward, and a positive component wB, supported on much
larger dilation parameters, restores decay at every nonzero Mellin frequency.
We multiply the common envelope by polynomials P−,P +,P 0. Reﬂection exchanges P− and
P+ and ﬁxes P0, giving the desired Fourier symmetries. The ﬁrst gamma pole, at normalized
frequency ζ = −i, controls the value at the origin: the polynomial P0 cancels this pole, while
P− and P+ retain equal positive residues. On the imaginary axis, the polynomials are chosen
so that P+(iu)> 0 for u> −1, whereas P− (iu)< 0 and P0(iu)> 0 just above u = 1; see ( 39).
Thus the essential contour is t =λ(T +iu) with u ≈ 1.
On this contour, the radius r = ev(u) for which the Mellin integrand is stationary at T = 0
satisﬁes ( 44). For ﬁxed u> −1, the digamma asymptotic gives
ev(u)
√
d
− →
√
1 +u
4π exp
( ∫∞
0
w(a)a sinh(ua)da
)
.
Consequently, negativew decreases the logarithm of the stationary radius when u> 0. However,
it also reduces the decay of the Mellin integrand away from T = 0 . At u = 1 , after dividing
the damping by λ, the limiting gamma contribution has density e− 2a/(2a2), while the pertur-
bation contributes w(a) cosha. A suﬃcient pointwise condition for nonnegative total damping
is therefore
|w(a)|cosha ≤ e− 2a
2a2 .
Within this pointwise constraint, the greatest inward displacement is achieved formally by
w∗(a) = − e− 2a
2a2 cosha,
∫∞
0
w∗(a)a sinhada = − 1
2 logπ
2, (32)
where the integral evaluation follows from the gamma duplication formula [ DLMF, § 5.5]. The
Gaussian stationary radius at u = 1 is (2π)− 1/2√
d, so the displacement in ( 32) gives
1√
2π exp
(
− 1
2 logπ
2
)
= 1
π. (33)
Although its Mellin perturbation is well deﬁned, the formal density w∗ has inﬁnite mass at
zero and saturates the gamma damping. Its Mellin factor therefore lacks the strict decay needed
for a Schwartz function. Instead, we truncate it to a bounded interval and taper it slightly,
obtaining a negative shell ws that preserves the displacement up to O(ϵ) while leaving a deﬁnite
11
===== PAGE 14 =====
damping margin. This margin suﬃces near u = 1, but not on contours with arbitrarily large u.
A second shell wB, supported on [B,B + 1], is chosen to have negligible eﬀect on the stationary
radius at u = u0 while dominating the negative shell at every frequency when u ≥ U > u0.
Using an interval rather than a single dilation avoids frequencies at which its damping would
vanish.
The remaining proof has two analytic parts. Uniform saddle estimates show that the Mellin
integral at r = ev(u) has the sign of Pj(iu), which gives the exterior signs and positivity of f+
for r ≥ r∗. A downward contour shift then expresses f+ on [0,r ∗] as a perturbed exponential
series, proving positivity at the remaining radii. The negative-shell displacement in ( 32) ﬁnally
yields the sharp radius ( 33).
4.2. The Mellin ansatz. We turn the ideal negative density w∗ in ( 32) into two compactly
supported shells. The negative shell ws retains its logarithmic-radius displacement up to O(ϵ),
while the positive shell wB is negligible at u =u0 and dominates the damping for u ≥ U .
Putλ =d/2, and throughout the construction ﬁx ϵ before taking d → ∞ . Constants in Oϵ(·)
and ≪ ϵ may depend on ϵ, but are independent of d and of the saddle parameter whenever a
bound is stated uniformly in that parameter; unadorned implicit constants are absolute.
Introduce cutoﬀs 0<a 0<A<B , a positive-shell amplitude Q> 0, and saddle parameters
u0 = 1 + ϵ
4, U = 1 + ϵ
2, C 0 =A +a− 1
0 .
As ϵ ↓0, the cutoﬀs should satisfy
a0 =o(ϵ), e− 2A
A =o(ϵ), ϵA =o(1), A =o(B).
The ﬁrst two conditions make the omitted portions of the ideal saddle displacement negligible,
and the third permits an O(ϵ(1 + a)) taper on the negative shell. For the positive shell, of
amplitude Q, the required separation is
BQe(u0− 1)B =o(1), C 0Q− 1e− (U − 1)(B− A) =o(1).
The bound on BQe(u0− 1)B keeps the positive shell from moving the target saddle. The bound
on C0Q− 1e− (U − 1)(B− A) makes that shell dominate the negative shell once u ≥ U . Because
u0 − 1<U − 1, both conditions are compatible: writing Q =e− qϵB, choose u0 − 1<q ϵ<U − 1
with enough separation that ϵB dominates logB + logC0.
One convenient realization of all these requirements is
a0 =ϵ2, A = log(1/ϵ), B =ϵ− 3,
qϵ = (u0 − 1) + (U − 1)
2 , Q =e− qϵB,
b(a) = 1 − 2ϵ(1 +a), β =u0 − 1.
(34)
The exponential slope qϵ is the midpoint between the two contour heights u0 − 1 and U − 1.
The taper leaves a damping margin of order ϵ, and β =u0 − 1 places the sign transition at the
target saddle. For suﬃciently small ϵ, we have b> 0 on [a0,A ] and B >A + 1. Deﬁne
ws(a) = − b(a)e− 2a
2a2 cosha 1[a0,A](a),
wB(a) = Q
cosha 1[B,B+1](a), w =ws +wB.
(35)
The signed density w determines the even entire Mellin perturbation
hϵ(ζ) =
∫∞
0
w(a)
(
cos(aζ) − 1
)
da. (36)
Forη >0, the positive density describing the unperturbed gamma damping is
µλ,η(a) = e− ηa
a(1 −e− 2a/λ) (a> 0). (37)
12
===== PAGE 15 =====
Lemma 4.2. There are absolute constants ϵ0,c,C > 0 such that, for every 0 < ϵ < ϵ0, the
shells in (35) have the following properties. For every λ> 0, −1<u ≤ U , and a ∈ [a0,A ],
λ|ws(a)|cosh(ua) ≤ (1 −cϵ)µλ,1+u(a).
At the target saddle, ∫A
a0
ws(a)a sinh(u0a)da = − 1
2 logπ
2 +O(ϵ),
0 ≤
∫B+1
B
wB(a)a sinh(u0a)da ≤ Ce− c/ϵ2
.
Finally, the target-saddle contribution and the remote-saddle domination ratio satisfy
BQe(u0− 1)B ≤ Ce− c/ϵ2
, C 0Q− 1e− (U − 1)(B− A) ≤ Ce− c/ϵ2
.
The implicit constant in O(ϵ) is absolute.
Proof. Write
w∗(a) = − e− 2a
2a2 cosha.
The negative shell agrees with w∗, up to its taper, on [a0,A ]. Its omitted saddle contributions
are ∫a0
0
|w∗(a)|a sinhada =O(a0),
∫∞
A
|w∗(a)|a sinhada =O
(
e− 2A
A
)
,
because tanha ≤ min(a, 1). The taper changes the same integral by only
∫A
a0
|1 −b(a)| |w∗(a)|a sinhada =O
(
ϵ
∫∞
0
(1 +a)e− 2a tanha
a da
)
=O(ϵ).
Moving from u = 1 to u =u0 contributes another O(ϵ): the mean-value theorem gives
∫A
a0
|ws(a)|a|sinh(u0a) − sinha|da ≪ ϵ
∫∞
0
e− 2a cosh(u0a)
cosha da ≪ ϵ.
Since a0 = o(ϵ) and e− 2A/A = o(ϵ), the identity
∫∞
0 w∗(a)a sinhada = − 1
2 log(π/2) now gives
the asserted negative-shell saddle displacement.
To compare the negative shell with gamma damping, divide its density by µλ,1+u:
λ|ws(a)|cosh(ua)
µλ,1+u(a) =b(a)Θλ(a)e(u− 1)a cosh(ua)
cosha , Θλ(a) = 1 −e− 2a/λ
2a/λ .
The ﬁnite-dimensional correction satisﬁes 0< Θλ(a) ≤ 1, by 1 − e− x ≤ x. When −1< u≤ 1,
both e(u− 1)a and cosh(ua)/ cosha are at most 1, so the ratio is at most b(a). When 1 ≤ u ≤ U ,
the elementary inequality cosh(ua) ≤ e(u− 1)a cosha bounds it by b(a)e2(u− 1)a ≤ b(a)eϵa. Since
ϵA =o(1), uniformly on the negative shell,
b(a)eϵa = (1 − 2ϵ(1 +a))(1 +ϵa +O(ϵ2a2)) ≤ 1 −cϵ.
Thus the taper retains a damping margin of order ϵ on every contour −1<u ≤ U .
It remains to check that the positive shell has opposite eﬀects at the two saddle locations. At
u0, sinh(u0a)/ cosha ≤ e(u0− 1)a, and hence
0 ≤
∫B+1
B
wB(a)a sinh(u0a)da ≤ (B + 1)Qe(u0− 1)(B+1).
The amplitude in ( 34) has exponential slope strictly between u0 − 1 and U − 1. Hence
Qe(u0− 1)B =e− cϵB, Qe (U − 1)B =ecϵB
for an absolute c >0. Since ϵB = ϵ− 2, while B and C0 grow only polynomially in 1/ϵ, both
separation quantities are O(e− c′/ϵ2
) for another absolute c′> 0. The same estimate controls the
positive-shell saddle displacement. □
13
===== PAGE 16 =====
The shells now determine the common envelope; it remains to impose the Fourier symmetries
and select the signs. The ﬁrst gamma pole occurs at t = −iλ, or ζ = −i. Thus P0 should vanish
at −i, while P± should take the same positive value there. Reﬂection ζ ↦→ −ζ should also
exchangeP− with P+. These requirements lead to the following envelope and polynomials:
Eλ(t) = πit/2Γ
( λ −it
2
)
eλhϵ(t/λ),
P± (ζ) = 1 + ζ 2 +β ±iζ(1 +ζ 2), P 0(ζ) = −(1 +ζ 2),
Xfj (t) = Eλ(t)Pj(t/λ), f j(r) = r− λ
2π
∫
R
Xfj (t)ritdt (j ∈ {−, 0, +}).
(38)
Indeed, P− (−ζ) = P+(ζ), P0 is even, and
P± (−i) = β >0, P 0(−i) = 0.
On the imaginary saddle branch,
P+(iu) = β + (1 −u)2(1 +u),
P− (iu) = β + (1 −u)(1 +u)2,
P0(iu) = u2 − 1.
(39)
ConsequentlyP+(iu)> 0 for every u> −1, whereas β =u0 − 1 gives
P− (iu0) = ϵ
4
(
1 −
(
2 + ϵ
4
) 2)
< 0, P 0(iu0) =
(
1 + ϵ
4
) 2
− 1> 0.
The saddle calculation below will transfer precisely these polynomial signs to the radial func-
tions.
Lemma 4.3. For every suﬃciently small ϵ > 0 and every integer d ≥ 1, with λ = d/2, the
inverse Mellin integrals in (38), initially deﬁned for r > 0, extend to fj ∈ S rad(Rd; R) for
j ∈ {−, 0, +}. These extensions satisfy ˆf− =f+, ˆf0 =f0, f− (0) = f+(0)> 0, and f0(0) = 0 .
Proof. Fixd andϵ. Compact support of w makeshϵ entire, and on each horizontal line t =s+iτ
it gives
|hϵ((s +iτ )/λ)| ≤2
∫∞
0
|w(a)|cosh(aτ/λ )da.
Thus the perturbation is bounded on every ﬁxed horizontal strip. Uniformly for τ in compact
pole-free intervals, the standard gamma asymptotics [ DLMF, § 5.11] give
|Xfj (s +iτ )| ≤Cd,ϵ,τ (1 + |s|)(λ+τ − 1)/2+3e− π|s|/4.
In particular, the vertical sides of rectangular contour shifts tend to zero. Shifting the Mellin
contour upward arbitrarily far proves rapid decay as r → ∞ , also after diﬀerentiation. Shifting
downward past the gamma poles
t = −i(λ + 2n), n = 0, 1, 2,...,
gives an expansion in even powers r2n, with a remainder of arbitrarily high order. Thus each
fj extends to a smooth radial Schwartz function on Rd. Conjugate symmetry of its real-line
Mellin data makes this extension real.
Because hϵ is even, the envelope obeys mλ(t)Eλ(−t) = Eλ(t). The polynomial reﬂection
identities and the multiplier ( 10) therefore give
ˆf− =f+, ˆf0 =f0. (40)
Finally, the value at the origin is determined by the ﬁrst pole of the downward-shifted contour.
More generally, Resz=− n Γ(z) = ( −1)n/n! shows that the pole t = −i(λ + 2n) contributes
2πλ/2+nr2n (−1)n
n! eλhϵ(− i(1+2n/λ))Pj(−i(1 + 2n/λ)). (41)
14
===== PAGE 17 =====
Atn = 0, evenness gives hϵ(−i) = hϵ(i), and P± (−i) = β, whereas P0(−i) = 0 . Consequently,
f+(0) = f− (0) = 2πλ/2eλhϵ(i)β >0, f 0(0) = 0. □ (42)
4.3. Saddle geometry. Recall u0 and U from ( 34), and set
u∗ = −1 + logλ
4λ . (43)
To determine the signs of the Mellin integrals ( 38), we associate each contour t =λ(T +iu)
with the radius r = ev(u) at which Eλ(t)rit is stationary in T . The decrease Du(T ) of its
logarithmic modulus must remain positive away from T = 0 . We establish this ﬁrst using the
gamma contribution when u∗ ≤ u ≤ U , and then using the positive shell wB when u ≥ U . The
resulting saddle estimates will identify the sign of each integral with the sign of Pj(iu).
Put
η = 1 +u> 0, m = λη
2 , ψ = (log Γ)′, ψ (1) =ψ′.
Take the branch of log Γ on Rez > 0 which is real on the positive axis. On the contour
t =λ(T +iu), the logarithm of Eλ(t)rit is
iλ(T +iu)
2 logπ + log Γ
(
m − iλT
2
)
+λhϵ(T +iu) +iλ(T +iu) logr.
Its derivative with respect to T at T = 0 equals
iλ
( 1
2 logπ − 1
2ψ(m) −
∫∞
0
w(a)a sinh(ua)da + logr
)
.
ThusT = 0 is stationary precisely when r =ev(u), where
v(u) = − 1
2 logπ + 1
2ψ(m) +
∫∞
0
w(a)a sinh(ua)da,
V (u) = v′(u) = λ
4ψ(1)(m) +
∫∞
0
w(a)a2 cosh(ua)da.
(44)
Diﬀerentiating the saddle log-radius gives V (u) = v′(u). Thus V (u) > 0 makes ev(u) increase
with u; the quadratic decrease of the logarithmic modulus at T = 0 is λV (u)T 2/2.
To separate the gamma and shell contributions to this decrease, recall the positive density
µλ,η from ( 37). The standard log-gamma integral [ DLMF, § 5.9], after substituting a = λs/2,
gives
Gλ,η(T ) := log Γ(m −iλT/ 2) − log Γ(m) + iλT
2 ψ(m)
=
∫∞
0
(eiaT − 1 −iaT )µλ,η(a)da, (45)
Dγ(T ) := − ReGλ,η(T ) =
∫∞
0
(1 − cos(aT ))µλ,η(a)da.
In particular, the gamma function in the Mellin envelope always damps the integrand away
from T = 0.
Normalize Eλ(λ(T +iu))riλT byEλ(iλu) and set r =ev(u). The linear contributions cancel
by the saddle equation, and ( 36) gives
Lu(T ) := log Eλ(λ(T +iu))
Eλ(iλu) +iλTv (u)
=Gλ,η(T ) +λ
∫∞
0
w(a) cosh(ua)(cos(aT ) − 1)da
+iλ
∫∞
0
w(a) sinh(ua)(aT − sin(aT ))da, (46)
Du(T ) := − Re Lu(T )
=Dγ(T ) +λ
∫∞
0
w(a) cosh(ua)(1 − cos(aT ))da. (47)
15
===== PAGE 18 =====
Equation (47) isolates the main diﬃculty: ws reducesDu(T ), while wB increases it. We must
prove Du(T ) > 0 for every T ̸= 0 and V (u) > 0 for every u ≥ u∗. The gamma density will
dominate ws on [u∗,U ], whereas wB will dominate ws on [U, ∞ ).
The quadratic and cubic sizes of the phase are measured by
Vγ = 1
λ
∫∞
0
a2µλ,η(a)da = λ
4ψ(1)(m),
M3 = 1
λ
∫∞
0
a3µλ,η(a)da +
∫∞
0
(
|ws(a)|+wB(a)
)
a3 cosh(ua)da.
(48)
HereVγ is the gamma contribution to V (u), and M3 bounds the cubic error after the signed
shell contributions have been replaced by their absolute values.
For later comparisons, write
Ds(T ) = λ
∫A
a0
|ws(a)|cosh(ua)(1 − cos(aT ))da,
DB(T ) = λ
∫B+1
B
wB(a) cosh(ua)(1 − cos(aT ))da,
Vs =
∫A
a0
|ws(a)|a2 cosh(ua)da,
VB =
∫B+1
B
wB(a)a2 cosh(ua)da.
(49)
In particular, Du =Dγ −Ds +DB and V (u) = Vγ −Vs +VB.
Lemma 4.4. There are absolute constants c,C > 0 such that, for every λ > 0, u > −1
satisfying λ(1 +u) ≥ 1, and T ∈ R, the phase and quantities deﬁned in (44)–(48) satisfy
⏐⏐⏐⏐Lu(T ) + λV (u)
2 T 2
⏐⏐⏐⏐≤ CλM3|T |3. (50)
Moreover, writing η = 1 +u,
1
2η ≤ Vγ ≤ C
η, (51)
1
λ
∫∞
0
a3µλ,η(a)da ≤ C
η2, (52)
Dγ(T ) ≥ cλ min
(
T 2
η , |T |
)
(T ∈ R). (53)
Proof. The globally valid Taylor estimates
eix − 1 −ix = −x2
2 +O(|x|3), x − sinx =O(|x|3)
applied to ( 45) and ( 46), and using |sinh(ua)| ≤cosh(ua), give ( 50).
Since m = λη/2 ≥ 1/2, the variance and third-moment bounds are the standard uniform
trigamma and polygamma estimates [ DLMF, §§ 5.9, 5.11, 5.15]; indeed,
Vγ = λ
4ψ(1)(m), 1
λ
∫∞
0
a3µλ,η(a)da = −λ2
8 ψ(2)(m).
To bound Dγ(T ) at every frequency, use 1 −e− x ≤ x in ( 37):
µλ,η(a) ≥ λe− ηa
2a2 .
ForT ̸= 0 , take L = min(η− 1, |T |− 1). On 0< a < L, both e− ηa and (1 − cos(aT ))/(a2T 2) are
bounded below by absolute positive constants. Therefore Dγ(T ) ≥ cλT 2L, which is ( 53); the
case T = 0 is immediate. □
16
===== PAGE 19 =====
The lower endpoint ( 43) ensures that the gamma shape parameter grows throughout the
saddle analysis:
m ≥ λ(1 +u∗)
2 = 1
8 logλ.
Lemma 4.4 controls the gamma contribution and cubic remainder. We next show that, for
u∗ ≤ u ≤ U , the negative shell removes at most a (1 −cϵ)-fraction of the gamma damping, while
wB contributes nonnegative damping.
Lemma 4.5. There is ϵ0 > 0 and an absolute c> 0 such that, for every 0<ϵ<ϵ 0, there are
constants Cϵ,λ ϵ > 0 with the following property. For every λ ≥ λϵ, every u∗ ≤ u ≤ U , and
η = 1 +u,
λ|ws(a)|cosh(ua) ≤ (1 −cϵ)µλ,η(a) (a ∈ [a0,A ]), (54)
Du(T ) ≥ cϵDγ(T ) (T ∈ R), (55)
cϵ
η ≤ V (u) ≤ Cϵ
η , (56)
M3 ≤ Cϵ
η2. (57)
Moreover,λη ≥ (logλ)/4.
Proof. Lemma 4.2 gives ( 54). Integrating that inequality against 1 − cos(aT ) ≥ 0 shows that
the negative shell removes at most a (1 −cϵ)-fraction of the gamma damping. The contribution
of wB is nonnegative. Therefore
Du(T ) ≥ Dγ(T ) − (1 −cϵ)
∫A
a0
(1 − cos(aT ))µλ,η(a)da ≥ cϵDγ(T ),
proving ( 55).
For the curvature, integrating ( 54) against a2/λ and using ( 49) gives Vs ≤ (1 − cϵ)Vγ, and
hence
V (u) = Vγ −Vs +VB ≥ cϵVγ +VB ≥ cϵ
η.
Foru∗ ≤ u ≤ U , the positive-shell variance satisﬁes
VB ≤ (B + 1)2Qe(U − 1)(B+1) =Oϵ(1).
Moreover,λη ≥ (logλ)/4, so ( 51) gives
V (u) ≤ Vγ +VB =Oϵ(η− 1),
because η ≤ 2 +ϵ/2. This proves ( 56).
Similarly, the negative-shell third moment is bounded by the gamma third moment:
∫A
a0
|ws(a)|a3 cosh(ua)da ≤ 1
λ
∫∞
0
a3µλ,η(a)da.
The positive-shell third moment is Oϵ(1). Consequently, ( 52), λη ≥ (logλ)/4, and η ≤ 2 +ϵ/2
give ( 57). □
We have proved positive damping and curvature for u∗ ≤ u ≤ U . When u > U, the factor
cosh(ua) in ( 47) can make ws overwhelm the gamma contribution. Put δ =u − 1. For T ̸= 0 ,
the ratios Ds(T )/(λ min(T 2, 1)) andDB(T )/(λ min(T 2, 1)) have respective sizes at most C0eδA
and at least QeδB . The separation in Lemma 4.2 therefore makes wB dominate ws throughout
u ≥ U .
The interval support [B,B + 1] ofwB prevents frequency resonances: a shell concentrated at
one a would have DB(T ) = 0 wheneveraT ∈ 2πZ, whereas
∫B+1
B
(1 − cos(aT ))da = 1 − sinc(T/ 2) cos((B + 1
2 )T ). (58)
Here sinc(x) = sin(x)/x, with sinc(0) = 1 . Since 1 − |sinc(T/ 2)| ≫ min(T 2, 1), ( 58) is positive
for every T ̸= 0, uniformly at both small and large frequencies.
17
===== PAGE 20 =====
Deﬁne the separation error
ρϵ = (A +a− 1
0 )Q− 1 exp
(
−ϵ
2 (B −A)
)
.
Lemma 4.2 gives ρϵ = O(e− c/ϵ2
) = o(1) as ϵ ↓ 0. The next lemma bounds Ds(T )/DB(T ) by
O(ρϵ), uniformly for u ≥ U and T ̸= 0 ; it also gives the curvature and third-moment bounds
required for the saddle approximation.
Lemma 4.6. There are absolute constants c,C > 0 and ϵ0> 0 such that, for every 0<ϵ<ϵ 0,
there are constants λϵ,C ϵ,c ϵ > 0 with the following property. For every λ ≥ λϵ, every u ≥ U ,
and every T ∈ R, writing δ =u − 1, one has
Ds(T ) ≤ CλC 0eδA min(T 2, 1), (59)
DB(T ) ≥ cλQeδB min(T 2, 1). (60)
Consequently,
Ds(T ) ≤ CρϵDB(T ), (61)
Du(T ) ≥ Dγ(T ) +cDB(T ), (62)
cVB ≤ V (u) ≤ CVB. (63)
The shell variance and third moments obey
cB2QeδB ≤ VB ≤ (B + 1)2Qeδ(B+1), (64)
∫A
a0
|ws(a)|a3 cosh(ua)da ≤ CAρϵVB, (65)
∫B+1
B
wB(a)a3 cosh(ua)da ≤ (B + 1)VB.
In particular,
M3 ≤ CϵV (u), V (u) ≥ cϵ> 0 ( u ≥ U ). (66)
Proof. Foru = 1 +δ, the explicit shell densities satisfy
|ws(a)|cosh(ua) ≪ eδa
a2, w B(a) cosh(ua) ≍ Qeδa.
If |T | ≤1, the bound 1 − cos(aT ) = O(a2T 2) gives
Ds(T ) ≪ λT 2
∫A
a0
eδada ≪ λAeδAT 2.
If |T | ≥1, use 1 − cos(aT ) = O(1):
Ds(T ) ≪ λeδA
∫A
a0
a− 2da ≪ λa− 1
0 eδA.
These two estimates give ( 59). On the positive shell, ( 58) yields
DB(T ) ≫ λQeδB
∫B+1
B
(1 − cos(aT ))da ≫ λQeδB min(T 2, 1).
ForT ̸= 0, division gives ( 61), since
Ds(T )
DB(T ) ≪ C0Q− 1e− δ(B− A) ≤ ρϵ =o(1).
At T = 0 , both damping terms vanish. Comparing their quadratic coeﬃcients in ( 49) gives
Vs = O(ρϵVB). Choose ϵ0 so that the implicit constant times ρϵ is less than 1/2. Then Du =
Dγ −Ds +DB proves (62), and V (u) = Vγ −Vs +VB gives
Vγ +cVB ≤ V (u) ≤ Vγ +VB.
IntegratingwB(a) cosh(ua) ≍ Qeδa against a2 gives ( 64). Since δ ≥ ϵ/2,
VB ≫ B2QeϵB/2 =B2ecϵB ≫ 1, V γ ≪ η− 1 ≪ 1.
18
===== PAGE 21 =====
ThusVγ =O(VB), so the preceding comparison of V (u) with Vγ +VB gives ( 63). Since a ≤ A
on the negative shell, ∫A
a0
|ws(a)|a3 cosh(ua)da ≤ AVs ≪ AρϵVB,
while a ≤ B + 1 bounds the positive-shell third moment by (B + 1)VB. This proves ( 65).
Since η ≥ 2 +ϵ/2, ( 51) and ( 52) bound the gamma third moment by O(Vγ). The shell third
moments are Oϵ(VB), while Vγ = O(VB) and ( 63) gives VB ≍ V (u). Hence M3 = Oϵ(V (u)).
Finally, (64) and ( 63) give V (u) ≫ VB ≫ B2QeϵB/2 =:cϵ> 0, proving ( 66). □
Set T0 = (2(B + 1))− 1.
Lemma 4.6 controls the total damping for u ≥ U . To bound the tails of the saddle integral,
we sharpen that control on three frequency ranges: |T | ≤T0, where Du(T ) is quadratic; T0 ≤
|T | ≤η, where wB supplies a uniform positive ﬂoor; and |T | ≥η, where the gamma contribution
also grows linearly.
Lemma 4.7. There is ϵ0 > 0 and an absolute c> 0 such that, for every 0<ϵ<ϵ 0, there are
constantscϵ,λ ϵ> 0 with the following property. For every λ ≥ λϵ and u ≥ U , set η = 1 +u and
δ =u − 1. Then
Du(T ) ≥ cϵλV (u)T 2 (|T | ≤T0), (67)
Du(T ) ≥ cϵλQeδB (T0 ≤ |T | ≤η), (68)
Du(T ) ≥ cλ|T |+cϵλQeδB (|T | ≥η). (69)
Proof. First suppose that |T | ≤T0. Since |aT | ≤ 1/2 on [B,B + 1], 1 − cos(aT ) ≫ a2T 2, and
therefore
DB(T ) ≫ λVBT 2.
Since η ≥ 2 +ϵ/2 and |T | ≤η, ( 53) and ( 51) also give
Dγ(T ) ≫ λT 2
η ≫ λVγT 2.
Combining these contributions using ( 62) and ( 63) proves ( 67).
Next, if T0 ≤ |T | ≤η, then min(T 2, 1) ≥ T 2
0 . Thus ( 62) and ( 60) give
Du(T ) ≫ λT 2
0QeδB ≫ ϵλQeδB.
This proves ( 68).
Finally, if |T | ≥η, then min(T 2, 1) = 1 and ( 53) gives Dγ(T ) ≫ λ|T |. Adding the positive
shell through ( 62) and ( 60) yields
Du(T ) ≫ λ|T |+λQeδB,
which proves ( 69). □
4.4. Global saddle asymptotics. The damping bounds now determine the exterior signs of
f+,f −,f 0. On each contour, the centered phase is quadratic near T = 0, the factor Pj(T +iu)
is asymptotic to Pj(iu), and the remaining contour is negligible. We establish these claims
separately for the gamma-controlled range u∗ ≤ u ≤ U and the positive-shell-controlled range
u ≥ U .
Lemma 4.8. Fix 0 < ϵ < ϵ0, let λ = d/2, and recall u0,U from (34) and u∗ from (43). For
u> −1 and P ∈ {P+,P −,P 0}, put
Iλ,P (u) =
∫
R
eLu(T )P (T +iu)dT.
Asd → ∞ ,
Iλ,P (u) = P (iu)
√
2π
λV (u)
(
1 +oϵ(1)
)
, (70)
19
===== PAGE 22 =====
uniformly for u ≥ u∗ when P =P+, and uniformly for u ≥ u0 when P =P− or P =P0. More
precisely,
sup
u≥ u∗
⏐⏐⏐⏐⏐
√
λV (u)Iλ,P+(u)√
2πP+(iu) − 1
⏐⏐⏐⏐⏐− → 0,
max
j∈{−,0}
sup
u≥ u0
⏐⏐⏐⏐⏐
√
λV (u)Iλ,Pj (u)√
2πPj(iu) − 1
⏐⏐⏐⏐⏐− → 0.
Proof. The poles of the integrand in ( 38) are t = −i(λ + 2n), n ≥ 0. Hence Lemma 4.3 allows
the contour to be shifted to t = λ(T +iu) whenever u >−1. At r = ev(u), the shifted Mellin
inversion formula is
fj(ev(u)) = λEλ(iλu)
2π e− (1+u)λv(u)Iλ,Pj (u). (71)
The prefactor of Iλ,Pj (u) is positive. By ( 39), P+(iu) > 0 for u >−1, while P− (iu) < 0 and
P0(iu)> 0 for u ≥ u0. Their ﬁxed degrees and uniform lower bounds on those ranges imply
|P (T +iu)|
|P (iu)| ≪ ϵ 1 + |T |3, P (T +iu)
P (iu) = 1 +Oϵ(|T |+ |T |3). (72)
To compare Iλ,P (u) with its Gaussian approximation, choose K → ∞ , and set
T∗ = K√
λV (u).
By ( 50), the phase on |T | ≤T∗ is
Lu(T ) = −λV (u)
2 T 2 +O
(
λM3|T |3
)
.
The approximation is uniform if its central interval shrinks and its cubic error tends to zero:
T∗ =oϵ(1), K3M3√
λV (u)3/2 =oϵ(1).
Under these conditions, ( 72) and the substitution x =
√
λV (u)T give
∫
|T |≤T∗
eLu(T )P (T +iu)dT =P (iu)
√
2π
λV (u)
(
1 +oϵ(1)
)
.
It remains to show that the integral over |T |>T ∗ isoϵ(|P (iu)|/
√
λV (u)). We verify the central
approximation and this tail bound separately on [u∗,U ] and [U, ∞ ).
First suppose u∗ ≤ u ≤ U , and put η = 1 +u, L =λη. Equations ( 56) and ( 57) give
L ≥ 1
4 logλ, V (u) ≍ ϵη− 1, M 3 ≪ ϵη− 2.
Choosing K =L1/12, so that K → ∞ and K3 =o(
√
L), gives
T∗
η ≪ ϵL− 5/12, K3M3√
λV (u)3/2 ≪ ϵL− 1/4.
The damping bounds ( 55) and ( 53) are quadratic for |T | ≤η and linear for |T | ≥η. Conse-
quently,
sup
|T |≤T∗
⏐⏐⏐⏐Lu(T ) + λV (u)
2 T 2
⏐⏐⏐⏐≪ ϵL− 1/4,
√
λV (u)
∫
T∗ ≤|T |≤η
(1 + |T |3)e− Du(T )dT ≪ ϵe− cϵK2
,
√
λV (u)
∫
|T |≥η
(1 + |T |3)e− Du(T )dT ≪ ϵe− cϵL.
Both tail estimates tend to zero uniformly because L ≥ (logλ)/4, proving ( 70) for u∗ ≤ u ≤ U .
20
===== PAGE 23 =====
Now suppose u ≥ U , and write δ =u − 1. By ( 63) and ( 66), the remote shell controls both
the curvature and the third moment:
V (u) ≍ ϵVB ≫ ϵ 1, M 3 ≪ ϵV (u).
TakeK =λ1/12. Then
T∗ ≪ ϵλ− 5/12, K3M3√
λV (u)3/2 ≪ ϵλ− 1/4.
In particular, T∗<T 0 for all suﬃciently large λ. The quadratic bound ( 67) on |T | ≤T0 yields
sup
|T |≤T∗
⏐⏐⏐⏐Lu(T ) + λV (u)
2 T 2
⏐⏐⏐⏐≪ ϵλ− 1/4,
√
λV (u)
∫
T∗ ≤|T |≤T0
(1 + |T |3)e− Du(T )dT ≪ ϵe− cϵK2
.
(73)
ForT0 ≤ |T | ≤η, the variance bound ( 64) and the damping estimate ( 68) give
√
λV (u)
∫
T0≤|T |≤η
(1 + |T |3)e− Du(T )dT
≪ ϵ
√
λ exp
( B + 1
2 δ + 4 log(2 +δ) −cϵλQeBδ
)
=oϵ(1).
(74)
The exponent on the right of ( 74) decreases in δ ≥ ϵ/2, since its derivative is (B + 1)/2 + 4/(2 +
δ) − cϵλBQeBδ < 0 for suﬃciently large λ. At δ = ϵ/2, that exponent is −cϵλ +Oϵ(1). Thus
the middle-frequency contribution tends to zero uniformly even as u → ∞ .
Finally, for |T | ≥η, ( 69) supplies the positive-shell damping and a linear gamma tail, so
√
λV (u)
∫
|T |≥η
(1 + |T |3)e− Du(T )dT ≪ ϵe− cϵλ, (75)
uniformly in δ: as in ( 74), the damping −cϵλQeBδ absorbs the growth of
√
V (u). Equations
(73)– ( 75) prove the saddle formula on every u ≥ U . □
Corollary 4.9. For every ﬁxed 0<ϵ<ϵ 0, there is dϵ such that, for every integer d ≥ dϵ,
f+(r)> 0 ( r ≥ ev(u∗ )),
f− (r)< 0 ( r ≥ ev(u0)),
f0(r)> 0 ( r ≥ ev(u0)).
(76)
Proof. Foru >−1, the prefactor of Iλ,Pj (u) in ( 71) is positive. Hence ( 70) identiﬁes the sign
of fj(ev(u)) with that of Pj(iu). Equations ( 56) and ( 63) give v′(u) = V (u) > 0 on [u∗, ∞ ),
while ( 44) and the positive shell wB give v(u) → ∞ . Thus [u∗, ∞ ) parametrizes every radius
r ≥ ev(u∗ ), and [u0, ∞ ) parametrizes every radius r ≥ ev(u0). The signs in ( 39) now give (76). □
4.5. Positivity and the sharp upper bound. Corollary 4.9 proves the required signs outside
the saddle radii. To ﬁnish the construction, we must also show f+(r)> 0 for 0 ≤ r ≤ r∗ =ev(u∗ ).
Shifting the Mellin contour below O(logλ) gamma poles expresses f+(r)/f+(0) as a truncated
exponential series plus a uniformly negligible remainder.
Lemma 4.10. Fix 0<ϵ<ϵ 0, let λ =d/2, set r∗ =ev(u∗ ), and write h′
1 =
∫∞
0 w(a)a sinhada .
Asd → ∞ ,
sup
0≤ r≤ r∗
⏐⏐⏐⏐eπe2h′
1 r2f+(r)
f+(0) − 1
⏐⏐⏐⏐− → 0.
In particular, f+(r)> 0 on [0,r ∗] for all suﬃciently large d.
Proof. First identify the range on which the truncated exponential series must approximate e− y.
Put
y =πe2h′
1r2, H (u) =
∫∞
0
w(a)a sinh(ua)da, η ∗ = 1 +u∗ = logλ
4λ .
21
===== PAGE 24 =====
The normalized contour height u∗ tends to −1, the normalized height of the ﬁrst gamma pole,
while the gamma shape parameter λ(1 + u∗)/2 = (log λ)/8 still diverges. This choice makes
(70) applicable and keeps y(r∗) logarithmic. Indeed, H is odd and, for ﬁxed ϵ, has bounded
derivative near −1. Consequently
H(u∗) +h′
1 =H(−1 +η∗) −H(−1) = Oϵ(η∗).
By ( 44),
y(r∗) = exp
(
ψ
( λη∗
2
)
+ 2H(u∗) + 2h′
1
)
.
The standard digamma asymptotic [ DLMF, § 5.11] and λη∗/2 = (log λ)/8 therefore give
0 ≤ y ≤ y(r∗) = 1
8 logλ +Oϵ(1). (77)
Since e− y can be as small as a negative power of λ on ( 77), the approximation error must be
controlled relative to e− y.
To recover enough exponential-series coeﬃcients, set
N = ⌈logλ⌉, p =N + 1
2, κ = 1 + 2p
λ.
Sincep =N + 1/2, the contour t =s −i(λ + 2p) lies strictly between consecutive gamma poles.
Furthermore,p ≍ logλ makes the exponential-series tail negligible on ( 77). To justify shifting
to this contour, we verify that the multiplier eλhϵ(t/λ) preserves a uniform exponential decay
margin. Indeed, pA/λ =oϵ(1), so the negative-shell taper satisﬁes
b(a)e2pa/λ ≤ 1 −cϵ (a0 ≤ a ≤ A)
for an absolutec> 0 and all suﬃciently largeλ. For every intermediate contour height 0 ≤ q ≤ κ,
the positive shell contributes nonpositively to Rehϵ(s/λ − iq) − hϵ(iq), and the negative shell
gives
λ
[
Rehϵ(s/λ −iq) −hϵ(iq)
]
≤ (1 −cϵ)λ
2
∫∞
0
1 − cos(as/λ)
a2 da
= (1 −cϵ)π|s|
4 .
Standard gamma asymptotics [ DLMF, § 5.11] supply the complementary factor e− π|s|/4. Hence
the integrand decays like e− cϵ|s| on the vertical sides, permitting the shift in ( 38) to t = s −
i(λ + 2p). This shift crosses exactly the poles t = −i(λ + 2n), 0 ≤ n ≤ N .
Applying the residue formula ( 41) and the origin value ( 42) gives
f+(r)
f+(0) =
N∑
n=0
(−y)n
n! Aλ,n + Rλ,p(r), (78)
Aλ,n =eλ[hϵ(i(1+2n/λ))− hϵ(i)]− 2nh′
1
P+(−i(1 + 2n/λ))
β ,
|Aλ,n − 1| ≪ϵ
n(1 +n)
λ (0 ≤ n ≤ N ). (79)
Indeed, Taylor expansion at u = 1 gives
λ
[
hϵ
(
i
(
1 + 2n
λ
))
−hϵ(i)
]
= 2nh′
1 +Oϵ
(
n2
λ
)
, P+(−i(1 + 2n/λ))
β = 1 +Oϵ
( n
λ
)
,
uniformly for n ≤ N ; here N 2/λ =o(1).
Forr> 0, the remainder Rλ,p(r) in ( 78) is the integral over t =s −i(λ + 2p):
Rλ,p(r) = πλ/2+pr2p
2πf+(0)
∫
R
πis/2Γ(−p −is/2)
·eλhϵ(s/λ− iκ)P+(s/λ −iκ)risds.
22
===== PAGE 25 =====
The gamma reﬂection and product estimates [ DLMF, §§ 5.5, 5.8], together with p ∈ Z + 1
2 , give
the standard bound
|Γ(−p −is/2)| ≪ e− π|s|/4
Γ(1 +p),
λ
[
Rehϵ(s/λ −iκ) −hϵ(iκ)
]
≤ (1 −cϵ)π|s|
4 .
Since P+(s/λ −iκ)/β =Oϵ(1 + |s|3), integration in s now gives
|Rλ,p(r)| ≪ϵ
yp
Γ(1 +p). (80)
Here we used
λ[hϵ(iκ) −hϵ(i)] = 2ph′
1 +Oϵ(p2/λ), (πr2)pe2ph′
1 =yp,
and absorbed p2/λ =o(1). The estimate extends to r = 0 by continuity.
To compare ( 78) with e− y, we bound the coeﬃcient errors Aλ,n − 1, the contour remainder
Rλ,p(r), and the omitted terms ∑
n>N (−y)n/n!. Equations ( 79), ( 80), and ( 77) give
ey
N∑
n=0
yn
n! |Aλ,n − 1| ≪ϵ
(1 +y)2e2y
λ ≪ ϵ
(logλ)2
λ3/4 ,
ey|Rλ,p(r)| ≪ϵ
eyyp
Γ(1 +p),
ey ∑
n>N
yn
n! ≪ eyyN +1
(N + 1)!.
(81)
The ﬁrst estimate follows from ∑
n≥ 0n(1 + n)yn/n! = ( y2 + 2y)ey. For the two tails, put
L = logλ. Since y ≤ L/8 +Oϵ(1) and p =L +O(1), Stirling’s formula [ DLMF, § 5.11] gives
log eyyp
Γ(1 +p) ≤
( 1
8 + 1 − log 8
)
L +Oϵ(logL).
The same estimate holds with p replaced by N + 1. Since 1/8 + 1 − log 8 < 0, both tails are
smaller than the coeﬃcient error in ( 81). Therefore ( 78) yields, uniformly on 0 ≤ r ≤ r∗,
f+(r)
f+(0) =e− y
(
1 +Oϵ
(
(logλ)2
λ3/4
))
> 0 (0 ≤ r ≤ r∗). □ (82)
Proof of Theorem 4.1. Set Rϵ,d = ev(u0). The Fourier identities and origin values follow from
(40) and ( 42). Corollary 4.9 gives the required exterior signs, while ( 82) supplies positivity of
f+ on the remaining interval. Thus
ˆf− =f+> 0, f − (0) = f+(0)> 0,
ˆf0 =f0, f 0(0) = 0, f − (r)< 0<f 0(r) ( r ≥ Rϵ,d).
(83)
For ﬁxed ϵ, the saddle equation ( 44) and the digamma asymptotic [ DLMF, § 5.11] give
lim
d→∞
Rϵ,d√
d
=
√
1 +u0
4π exp
( ∫∞
0
w(a)a sinh(u0a)da
)
. (84)
The two shell contributions in Lemma 4.2 give
∫∞
0
w(a)a sinh(u0a)da = − 1
2 logπ
2 +O(ϵ).
Since u0 → 1, ( 33) and ( 84) give
lim
ϵ↓0
lim
d→∞
Rϵ,d√
d
= 1
π. □ (85)
23
===== PAGE 26 =====
Proof of Theorem 1.1. By ( 83), the dilation Fϵ,d(x) = f− (Rϵ,dx) is admissible and satisﬁes
Fϵ,d(0)/ˆFϵ,d(0) = Rd
ϵ,d by Fourier scaling. Inserting Fϵ,d into ( 3) gives
LPd ≤ vd
2dRd
ϵ,d. (86)
The universal lower bound ( 28), the admissible upper bound ( 86), and ( 85), together with
v1/d
d
√
d →
√
2πe, imply
√e
2π ≤ lim inf
d→∞
LP1/d
d ≤ lim sup
d→∞
LP1/d
d ≤
√
2πe
2π =
√e
2π. □
Proof of Theorem 1.2. The lower bound is Proposition 3.7. For the upper bound, deﬁne gϵ,d,− =
f+ −f− and gϵ,d,+ =f0. Equation ( 40) and Fourier inversion give
ˆgϵ,d,− = −gϵ,d,−, ˆgϵ,d,+ =gϵ,d,+.
By ( 83), both gϵ,d,− andgϵ,d,+ vanish at the origin and are strictly positive outside Rϵ,d; in par-
ticular, neither is zero. The deﬁnition ( 6) therefore gives Aς (d) ≤ Rϵ,d for both signs. Combining
this bound with ( 85) gives
1
π ≤ lim inf
d→∞
Aς (d)√
d
≤ lim sup
d→∞
Aς (d)√
d
≤ lim
ϵ↓0
lim
d→∞
Rϵ,d√
d
= 1
π. □
Appendix A. Comparison of the sign-uncertainty constants
For an anti-self-Fourier radial function g, the central Mellin moment Mg(d/2) vanishes. In-
tegrating the radial tail of g therefore produces a self-Fourier function with a strictly smaller
last-sign radius.
Proposition A.1. Let d ≥ 1, put λ = d/2, and suppose that 0 ̸= g ∈ L1
rad(Rd; R) satisﬁes
ˆg = −g and g(0) = 0 . Deﬁne Tdg(0) = 0 and, for x ̸= 0, set
(Tdg)(x) = λ
2
∫∞
1
tλ− 1g(tx)dt, (87)
whereg denotes its continuous Fourier-inversion representative. Then Tdg is nonzero, continu-
ous, and integrable, with
ˆTdg =Tdg, (Tdg)(0) = 0, ∥Tdg∥1 ≤ 1
2 ∥g∥1.
If r(g)< ∞ , then r(Tdg)<r (g); if g is Schwartz, then so is Tdg. Consequently, the constants
in (6) satisfy
A+(d)< A− (d) ( d ≥ 1).
Proof. Since g = −ˆg ∈ L1, Fourier inversion makes g bounded and continuous. In particular,∫
Rd |g(x)| |x|− λdx< ∞ , by splitting the integral at |x|= 1 . The Mellin–Fourier identity in ( 9)
was established for Schwartz functions, so we ﬁrst verify its central consequence directly for
the integrable eigenfunction g. Set J(t) =
∫
Rdg(x)e− πt|x|2
dx. Gaussian duality and Tonelli’s
theorem give
J(t) = −t− λJ(1/t),
∫∞
0
tλ/2− 1|J(t)|dt ≤ Γ(λ/2)
πλ/2
∫
Rd
|g(x)| |x|− λdx< ∞.
Hence the substitution t ↦→1/t makes
∫∞
0 tλ/2− 1J(t)dt equal to its negative. Gaussian integra-
tion and polar coordinates therefore give the central Mellin cancellation
Mg(λ) =
∫∞
0
g(r)rλ− 1dr = 0. (88)
The integral deﬁning Tdg(x) converges absolutely for x ̸= 0, since g is integrable and sλ− 1 ≪ x
sd− 1 for s ≥ |x|. Tonelli’s theorem and d = 2λ yield ∥Tdg∥1 ≤ (λ/2)∥g∥1
∫∞
1 t− λ− 1dt = ∥g∥1/2,
24
===== PAGE 27 =====
also justifying Fourier transformation under the integral. Fourier scaling and ( 88) give
ˆTdg(ξ) = λ
2
∫∞
1
tλ− d− 1ˆg(ξ/t)dt
= −λ
2
∫1
0
sλ− 1g(sξ)ds
= λ
2
∫∞
1
sλ− 1g(sξ)ds =Tdg(ξ).
(89)
The small-scale representation in ( 89) extends continuously to x = 0 , with value −g(0)/2 = 0 .
Diﬀerentiating the large-scale representation gives (x · ∇+λ)Tdg = −λg/2, so Tdg ̸= 0 . If g
is Schwartz, diﬀerentiating the small-scale representation gives smoothness at the origin, and
diﬀerentiating the large-scale representation gives rapid decay at inﬁnity; thus Tdg is Schwartz.
If R =r(g)< ∞ , then R> 0, since otherwise g ≥ 0 and
∫
g =ˆg(0) = −g(0) = 0 would force
g = 0. Hence g(s) ≥ 0 for s ≥ R, and ( 5) and ( 87) give
(Tdg)(r) = λ
2r− λ
∫∞
r
sλ− 1g(s)ds> 0 ( r ≥ R).
Indeed, equality at any r ≥ R would make both g and ˆg = −g compactly supported, con-
tradicting Fourier analyticity. In particular, Tdg(R) > 0, so continuity gives r(Tdg) < R.
Applying this strict decrease to an attained radial negative-sign extremizer [ CG19, Thm. 1.4]
gives A+(d)< A− (d). □
References
[AJCHLT20] N. Afkhami-Jeddi, H. Cohn, T. Hartman, D. de Laat, and A. Tajdini, High-dimensional sphere
packing and the modular bootstrap , J. High Energy Phys. 12 (2020), article 066, doi:10.1007/
JHEP12(2020)066.
[Ahl79] L. V. Ahlfors, Complex Analysis , 3rd ed., McGraw–Hill, New York, 1979.
[BCK10] J. Bourgain, L. Clozel, and J.-P. Kahane, Principe d’Heisenberg et fonctions positives , Ann. Inst.
Fourier (Grenoble) 60 (2010), 1215–1232, doi:10.5802/aif.2552.
[Coh02] H. Cohn, New upper bounds on sphere packings. II , Geom. Topol. 6 (2002), 329–353, doi:10.2140/
gt.2002.6.329.
[CDG24] H. Cohn, D. Dong, and F. Gonçalves, Sign uncertainty principles and low-degree polynomials , Proc.
Amer. Math. Soc. Ser. B 11 (2024), 224–228, doi:10.1090/bproc/219.
[CE03] H. Cohn and N. Elkies, New upper bounds on sphere packings. I , Ann. of Math. (2) 157 (2003),
689–714, doi:10.4007/annals.2003.157.689.
[CG19] H. Cohn and F. Gonçalves, An optimal uncertainty principle in twelve dimensions via modular
forms, Invent. Math. 217 (2019), 799–831, doi:10.1007/s00222-019-00875-4.
[CKMR V17] H. Cohn, A. Kumar, S. D. Miller, D. Radchenko, and M. S. Viazovska, The sphere packing problem
in dimension 24, Ann. of Math. (2) 185 (2017), 1017–1033, doi:10.4007/annals.2017.185.3.8.
[CKMR V22] H. Cohn, A. Kumar, S. D. Miller, D. Radchenko, and M. S. Viazovska, Universal optimality of
the E8 and Leech lattices and interpolation formulas , Ann. of Math. (2) 196 (2022), 983–1082,
doi:10.4007/annals.2022.196.3.3.
[CZ14] H. Cohn and Y. Zhao, Sphere packing bounds via spherical codes , Duke Math. J. 163 (2014), 1965–
2002, doi:10.1215/00127094-2738857.
[Edw25] R. Edwin, Fourier inequalities and sign uncertainty , preprint, 2025, arXiv:2505.15994.
[GOSR21] F. Gonçalves, D. Oliveira e Silva, and J. P. G. Ramos, On regularity and mass concentration
phenomena for the sign uncertainty principle , J. Geom. Anal. 31 (2021), 6080–6101, doi:10.1007/
s12220-020-00519-7.
[GOSS17] F. Gonçalves, D. Oliveira e Silva, and S. Steinerberger, Hermite polynomials, linear ﬂows on the
torus, and an uncertainty principle for roots , J. Math. Anal. Appl. 451 (2017), 678–711, doi:10.1016/
j.jmaa.2017.02.030.
[Gor00] D. V. Gorbachev, Extremal problem for entire functions of exponential spherical type, connected
with the Levenshtein bound on the sphere packing density in Rn, Izv. Tula State Univ. Ser. Math.
Mech. Inform. 6 (2000), 71–78; in Russian.
[HMR19] T. Hartman, D. Mazáč, and L. Rastelli, Sphere packing and quantum gravity , J. High Energy Phys.
12 (2019), article 048, doi:10.1007/JHEP12(2019)048.
[KL78] G. A. Kabatianskii and V. I. Levenshtein, On bounds for packings on a sphere and in space , Prob-
lems Inform. Transmission 14 (1978), 1–17.
[Lev79] V. I. Levenshtein, On bounds for packings in n-dimensional Euclidean space , Soviet Math. Dokl.
20 (1979), 417–421.
25
===== PAGE 28 =====
[DLMF] F. W. J. Olver et al., eds., NIST Digital Library of Mathematical Functions , Release 1.2.7, National
Institute of Standards and Technology, 2026, dlmf.nist.gov.
[PK01] R. B. Paris and D. Kaminski, Asymptotics and Mellin–Barnes Integrals , Encyclopedia of Mathe-
matics and its Applications, vol. 85, Cambridge University Press, Cambridge, 2001.
[R V19] D. Radchenko and M. S. Viazovska, Fourier interpolation on the real line , Publ. Math. Inst. Hautes
Études Sci. 129 (2019), 51–81, doi:10.1007/s10240-018-0101-z.
[SZ24] N. T. Sardari and M. Zargar, New upper bounds for spherical codes and packings , Math. Ann. 389
(2024), 3653–3703, doi:10.1007/s00208-023-02738-z.
[SW71] E. M. Stein and G. Weiss, Introduction to Fourier Analysis on Euclidean Spaces , Princeton Math-
ematical Series, vol. 32, Princeton University Press, Princeton, 1971.
[Via17] M. S. Viazovska, The sphere packing problem in dimension 8, Ann. of Math. (2) 185 (2017), 991–
1015, doi:10.4007/annals.2017.185.3.7.
[Z24] M. Zargar, Stiefel manifolds and upper bounds for spherical codes and packings , preprint, 2024,
arXiv:2407.10697.
26
===== PAGE 29 =====
Chapter 2
Improved Bounds for Binary and Spherical
Codes
Abstract. We construct two-point linear-programming certiﬁcates that im-
prove the high-dimensional bounds for unrestricted binary and spherical codes.
For every ﬁxed relative distance 0<δ < 1/2, our binary-code bound strictly im-
proves the optimized McEliece–Rodemich–Rumsey–Welch exponent. For every
ﬁxed maximum inner product 0 < s <1, our spherical-code bound strictly im-
proves the optimized Kabatianskii–Levenshtein exponent, including its spherical-
cap optimization. These are the ﬁrst improvements to the respective general high-
dimensional exponents since 1977 and 1978. In the limit s→1, the spherical
construction also recovers the optimal sphere-packing exponent of the Euclidean
Cohn–Elkies linear program, obtained independently in a companion paper.
Contents
1. Introduction
2. The ﬁrst binary bound
3. The optimized binary bound
4. Representation graphs for spherical codes
5. Spherical harmonics and stabilizer representations
6. The spherical transition graph
7. Asymptotic spherical-code bounds
8. Sphere packings
Appendix A. Orthogonal representations and asymptotic dimensions
Appendix B. The spherical-to-Euclidean limit
References
27
===== PAGE 30 =====
1. Introduction
A binary code C⊆{0, 1}n has Hamming distance dH(x,y ), the number of coordinates in
which two words diﬀer; its minimum distance is the smallest such value for distinct codewords.
Let A2(n,d ) denote the largest code size with minimum distance at least d. A spherical code
C⊆Sn− 1 has maximum inner product at most s when⟨x,y⟩≤s for distinct points; let A(n,s )
denote its largest size. For ﬁxed relative distance 0 < δ <1/2 and maximum inner product
0<s< 1, the corresponding asymptotic rates are
R2(δ) = lim sup
n→∞
1
n log2A2(n,⌈δn⌉), R sph(s) = lim sup
n→∞
1
n log2A(n,s ).
The best previous general bounds on these rates are due to McEliece, Rodemich, Rumsey, and
Welch (MRR W) for unrestricted binary codes and to Kabatianskii and Levenshtein for spherical
codes [ MRR W77, KL78]. Both arise from Delsarte’s two-point programs [ Del72, Del73, DGS77].
A Delsarte certiﬁcate is a polynomial F (t) =∑M
j=0fjPj(t) in the Krawtchouk, Hahn, or Gegen-
bauer basis associated with the code space, with P0 = 1 . If f0 > 0, fj≥0 for 1≤j≤M ,
and F (t) ≤0 at every normalized inner product allowed by the distance constraint, then
|C|≤F (1)/f0. Our constructions verify positivity directly through projection Gram factoriza-
tions, without requiring explicit orthogonal-polynomial formulas or a converse characterization
of positive-deﬁnite kernels.
In the classical spectral construction, each retained harmonic space contributes a single vector
associated with a code point [ BN06]. We instead associate a dE-dimensional subspace with each
point x, inside a common D-dimensional ambient space. The subspaces move with the points:
a symmetry carrying x to y carries the subspace at x to the subspace at y. If Px denotes
the corresponding orthogonal projection, the overlap tr(PxPy) is still a scalar function of the
distance. Write s for the largest permitted normalized inner product and Λ for the largest
eigenvalue of the associated weighted transition matrix. If Λ > s, the projection bound ( 50)
gives
|C|≤1−s
Λ−s
D
dE
.
Thus an exponentially large projection rank improves the rate provided Λ remains bounded away
from the threshold s. For binary codes, the transition matrices are tridiagonal; for spherical
codes, the full construction uses weighted graphs with several degree indices.
Bachoc and Vallentin also exploit higher harmonics of the rotations ﬁxing a point [ BV08,
§3]. Their ﬁxed base point yields matrix-valued, three-point semideﬁnite programs. Here the
subspace moves with each code point, giving scalar two-point certiﬁcates whose bounds contain
its dimension through D/dE.
1.1. Binary codes: statement of the result. We ﬁrst recall the classical binary-code bounds
and then state the two constructions needed to improve the fully optimized second MRR W
bound. The whole-cube construction improves the ﬁrst MRR W bound, while the constant-
weight construction handles parameter ranges where optimization over layers gives a stronger
classical bound.
With 0 log2 0 = 0 , deﬁne the binary entropy function H2 and an auxiliary function g on [0, 1]
by
H2(u) =−u log2u−(1−u) log2(1−u), g (v) = H2
(
1−√1−v
2
)
.
The ﬁrst MRR W bound is [ MRR W77]
M1(δ) = H2
(1
2−
√
δ(1−δ)
)
. (1)
In particular, R2(δ)≤M1(δ). To state the whole-cube improvement, introduce normalized
degree parameters 0≤b < a≤1/2. In the ﬁnite construction, a = L/n records the largest
retained Fourier degree, meaning the number of coordinates in a Fourier monomial, and b =k/n
28
===== PAGE 31 =====
records the degree of the Boolean harmonic subspace attached to each code point. The spaces
are constructed in § 2. Set
ΓH(a,b ) = 2(a−b)(1−a−b)√
a(1−a) .
The whole-cube construction gives the tridiagonal matrix ( 20), whose limiting largest eigenvalue
is ΓH(a,b ) by Lemma 2.2 . Its resulting exponent is
κH(δ) = inf
0≤ b<a≤ 1/2
ΓH(a,b)>1− 2δ
(
H2(a)−H2(b)
)
. (2)
HereH2(a) andH2(b) are the dimension exponents of the retained ambient space and attached
harmonic subspace, respectively. Theorem 2.3 proves that, for every 0<δ < 1/2,
R2(δ)≤κH(δ)<M 1(δ).
The second MRR W bound optimizes the classical construction over constant-weight lay-
ers [ MRR W77]. Its scalar parameter τ reparametrizes the polynomial degree: on the classical
spectral boundary, a largest retained degree un corresponds to τ = 2
√
u(1−u). The objective
is
Fδ(τ ) = 1 + g(τ 2)−g(τ 2 + 2δτ + 2δ), 0≤τ≤1−2δ.
The endpoints are
Fδ(1−2δ) = M1(δ), F δ(0) = 1−g(2δ),
and the second MRR W bound is the full optimized exponent
M2(δ) = min
0≤ τ ≤ 1− 2δ
Fδ(τ ). (3)
Thus R2(δ)≤M2(δ)≤min{M1(δ),F δ(0)}. The minimum over all τ can occur in the interior
and be strictly smaller than both endpoint values. Therefore, improving M1 alone need not
improveM2, so we reﬁne the constant-weight construction as well.
A weight-w layer of the binary cube consists of all binary words having exactly w coordinates
equal to 1. Fixing one such word partitions the coordinates into its w-element support and its
(n−w)-element complement. The construction attaches the tensor product of Boolean harmonic
spaces of degrees p andq on these two coordinate sets and retains layer degrees up to L. Write
α = w/n, β = p/n, γ = q/n, and u = L/n for the normalized layer weight, harmonic degrees,
and largest retained layer degree, respectively. § 3 constructs these spaces and an associated
tridiagonal matrix. The parameter ranges are
δ
2 <α< 1
2, 0≤β <α
2, 0≤γ <1−α
2 , (4)
and
β +γ <u< min{α,α−β +γ, 1−α +β−γ}. (5)
The following function determines which parameter choices yield a code bound; its origin is
explained in Lemma 3.5 . Introduce the aﬃne coordinates
z = 1−2u, m = 1−2α, ζ = 1−2β−2γ, ξ = 1−2α + 2β−2γ.
Deﬁne
Λα,β,γ (u) = (ζξ−mz2)2
z2(1−m2)(1−z2) + (z2−ξ2)(ζ 2−z2)
z2(1−m2)
√
1−z2. (6)
Two weight-αn words at Hamming distance δn have normalized layer-distance coordinate 1−
δ/(2α(1−α)); see ( 28). The construction applies when the preceding function exceeds this
coordinate:
Λα,β,γ (u)> 1− δ
2α(1−α). (7)
LetDδ be the set of all (α,β,γ,u ) in the ranges ( 4)–(5) that also satisfy ( 7). The resulting
unrestricted-code exponent from constant-weight (CW) layers is
κCW(δ) = inf
(α,β,γ,u )∈Dδ
{
1−H2(α) +H2(u)−αH2
(β
α
)
−(1−α)H2
( γ
1−α
)}
. (8)
29
===== PAGE 32 =====
The four terms have a direct dimension interpretation. Passing from the whole cube to a weight-
αn layer costs 1−H2(α), since that layer has 2(H2(α)+o(1))n words. The retained ambient space
has dimension 2(H2(u)+o(1))n, while the subspace attached to a code point has dimension
2(αH2(β/α)+(1− α)H2(γ/(1− α))+o(1))n.
Dividing the ambient dimension by this subspace dimension produces the two entropy subtrac-
tions in ( 8). Finally, set
κbin(δ) = min{κH(δ),κ CW(δ)}.
Theorem 1.1. For every ﬁxed 0<δ < 1/2,
R2(δ)≤κbin(δ)<M 2(δ).
The classical MRR W constructions are boundary subfamilies of the enlarged variational prob-
lems: b = 0 recoversM1, and β = γ = 0 recoversFδ. Theorem 2.3 and Proposition 3.7 show
that introducing positive harmonic degrees strictly improves the ﬁrst MRR W bound and the
classical constant-weight objective at every interior optimizing layer.
If the endpoint τ = 1−2δ minimizes ( 3), then M2 = M1 and the whole-cube construction
gives the strict improvement. Otherwise, the constant-weight construction strictly improves a
minimizing layer. Theorem 3.8 combines these cases to prove Theorem 1.1 .
1.2. Spherical codes: statement of the result. Fix a maximum inner product 0 < s <
1. We ﬁrst recall the classical spherical-code bound and its spherical-cap optimization, then
illustrate our improvement using harmonics on the directions orthogonal to a code point. Finally,
we state the full hierarchy; its sphere-packing consequence follows in the next subsection.
Foru≥0, deﬁne the spherical harmonic dimension exponent by
Hsph(u) = (1 + u) log2(1 +u)−u log2u, Hsph(0) = 0. (9)
Indeed, the space of degree- un +o(n) spherical harmonics has dimension 2(Hsph(u)+o(1))n; the
exact formula is recorded in ( 59). Applying the Kabatianskii–Levenshtein bound directly to the
whole sphere gives
A(n,s )≤2(Hsph(a0(s))+o(1))n, a 0(s) = 1
2
(
(1−s2)− 1/2−1
)
.
A stronger classical bound ﬁrst restricts the code to a suﬃciently populated spherical cap and
projects that cap onto a lower-dimensional sphere. Sidelnikov’s spherical-slice inequality replaces
the original inner-product threshold s by a smaller threshold 0≤t≤s, at an exponential cost
1
2 log2((1−t)/(1−s)) [Sid74]. Combining this spherical-cap reduction with the Kabatianskii–
Levenshtein construction gives the optimized classical exponent [ KL78, Thm. 4]
BKL(s) = inf
0≤ t≤ s
{
Hsph(a0(t)) + 1
2 log2
1−t
1−s
}
. (10)
ThusRsph(s)≤BKL(s).
Forx∈Sn− 1, let Ek,x =Hk(x⊥ ) be the space of degree- k spherical harmonics on the unit
sphere in x⊥ . For k = 0 , this is the classical space of constants; for k = 1 , it consists of
linear functions on x⊥ . Every ambient harmonic space Hi(Rn) with i≥k contains a naturally
associated copy of Ek,x; see § 5.2 for the construction.
Retain these copies for k≤i≤L, and write a = L/n, b = k/n, with 0≤b < a. Coordi-
nate multiplication connects consecutive ambient harmonic spaces, giving a tridiagonal matrix
indexed by i =k,...,L . Deﬁne
Γrow(a,b ) = (a−b)(1 +a +b)
(1 + 2a)
√
a(1 +a), Φrow(a,b ) = Hsph(a)−Hsph(b). (11)
This construction gives, whenever 2Γrow(a,b )>s ,
A(n,s )≤2(Φrow(a,b)+o(1))n.
30
===== PAGE 33 =====
Since dimEk,x = 2 (Hsph(b)+o(1))n, the projection rank subtracts Hsph(b) from the ambient expo-
nent Hsph(a). Optimizing over b> 0 strictly improves both the direct Kabatianskii–Levenshtein
bound and, after spherical-cap reduction, its optimized version.
For the full hierarchy, ﬁx an integer r≥0 and choose vectors a = (a1,...,a r+1) and b =
(b1,...,b r) satisfying
a1>b 1>a 2>···>b r >a r+1≥0.
For r = 0 , the chain means simply a1 ≥0. The relevant orthogonal-group representations
are indexed by Young diagrams, and aℓ and bm are their row lengths divided by n. The
hierarchy level r counts the rows of the subspace associated with each code point; the ambient
representation has one additional row. Their representation-theoretic meaning and the resulting
weighted adjacency matrices are developed in §§ 5.3 and 7. Level r = 0 recovers the classical
construction; when r = 1 , setting a2 = 0 gives the harmonics on x⊥ in ( 11). Introduce the
quadratic coordinates and scalar function
A(u) = u(1 +u), q (u) =
√
u(1 +u)
1 + 2u , x ℓ =A(aℓ), y m =A(bm).
For 1≤ℓ,j ≤r + 1 and 1≤m≤r, deﬁne Rℓ, Γr = Γ r(a, b), and Φr = Φ r(a, b) by
Rℓ =
∏r
m=1(xℓ−ym)∏
j̸=ℓ(xℓ−xj) , Γr =
r+1∑
ℓ=1
Rℓq(aℓ), Φr =
r+1∑
ℓ=1
Hsph(aℓ)−
r∑
m=1
Hsph(bm).
The displayed strict inequalities make every Rℓ positive, and Lagrange interpolation gives∑
ℓRℓ = 1 ; see ( 81). The spectral calculation and dimension estimate giving 2Γr and Φr
appear in Lemmas 7.2 and A.1. Empty products and sums take their usual values, so the
deﬁnitions include r = 0.
Theorem 1.2. Fix r ∈Z≥ 0, 0 < s < 1, and nonnegative vectors a = (a1,...,a r+1) and
b = (b1,...,b r) satisfying aℓ>b ℓ>a ℓ+1 for 1≤ℓ≤r. Then
2Γr(a, b)>s =⇒A(n,s )≤2(Φr(a,b)+o(1))n.
Hereo(1)→0 as n→∞with r,s, a, b ﬁxed. Consequently,
Rsph(s)≤inf
r∈Z≥0
inf
a1>b1>···>br>ar+1≥ 0
2Γr(a,b)≥ s
Φr(a, b).
The non-strict constraint 2Γr≥s follows by approximating its equality boundary with pa-
rameters satisfying 2Γr >s . Write κr(s) for the inner inﬁmum in Theorem 1.2 , taken over a, b
at the ﬁxed hierarchy level r, and set κr(0) = 0 . Applying the spherical-cap reduction from ( 10)
gives
κr(s) = inf
0≤ t≤ s
{
κr(t) + 1
2 log2
1−t
1−s
}
.
Consequently,
Rsph(s)≤inf
r≥ 0
κr(s).
Level 0 recovers the classical Kabatianskii–Levenshtein construction [ KL78], so κ0 =BKL by
(10). The one-row construction ( 11) is obtained from level 1 by setting a2 = 0; write κrow for its
spherical-cap-optimized exponent. The full strict hierarchy, including this intermediate one-row
improvement, is proved in Corollary 7.6 .
Corollary 1.3. For every 0<s< 1 and every r≥0,
κr+1(s)<κ r(s), κr+1(s)<κr(s).
Moreover,
Rsph(s)≤inf
r≥ 0
κr(s)<κ1(s)<κrow(s)<κ0(s) = BKL(s).
31
===== PAGE 34 =====
1.3. Sphere-packing consequence. Let ∆n denote the maximal packing density in Rn. For
−1<s< 1, projection from the upper hemisphere gives [ Sid74, KL78, CZ14]
∆n≤
(1−s
2
)n/2
A(n + 1,s ).
Consequently, if A(n,s )≤2(B(s)+o(1))n, then
∆n≤2(B(s)− 1
2 log2
2
1−s +o(1))n.
For spherical codes at a ﬁxed threshold s, passing to a spherical cap can improve the exponent
by replacing s with some t≤s. The packing transfer behaves diﬀerently: the cost of passing to
that cap exactly oﬀsets the change in its geometric packing factor. Indeed, at hierarchy level r,
1
2 log2
2
1−s−1
2 log2
1−t
1−s−κr(t) = 1
2 log2
2
1−t−κr(t).
Thus transferring a cap-improved spherical bound at threshold s gives exactly the packing
exponent obtained by transferring the direct spherical bound at threshold t; see (93). Optimizing
over the hierarchy and the threshold therefore requires no additional cap optimization.
Corollary 1.4. Asn→∞,
∆n≤2− (λ∗+o(1))n, λ ∗ = 1
2 log2
2π
e .
This improves the classical Kabatianskii–Levenshtein sphere-packing exponent [ KL78, Lev79]
and attains the Cohn–Elkies rate conjectured in [ AJCHLT20, Conjs. 3.1–3.2]. The exact hier-
archy limit and the order of the dimension, hierarchy-depth, and small-angle limits are proved
in Theorem 8.3 .
Remark 1.5. Gorbachev and, independently, Cohn and Elkies developed the Euclidean Fourier-
analytic linear program for sphere packing [ Gor00, CE03]; optimizing its auxiliary functions is
called the Cohn–Elkies linear program. The companion paper in Chapter 1 gives an independent,
self-contained determination of its optimal exponent by proving a lower bound for every auxiliary
function satisfying the Cohn–Elkies Fourier-positivity and sign conditions and constructing
matching Euclidean witnesses. If LPn denotes the optimal density bound of that program, its
result is
limn→∞ LP1/n
n =
√e
2π.
Cohn and Zhao’s upper-hemisphere construction also converts our spherical certiﬁcates into fea-
sible Euclidean auxiliary functions [ CZ14, Thm. 3.4 and subsequent discussion]. The subsequent
discussion covers s >1/2, as required in the limit s↑1. § B further identiﬁes the main weight
in the companion paper’s Euclidean construction with the small-angle limit of our spherical
certiﬁcates.
Remark 1.6. The spherical and binary constructions diﬀer in the multiplicities that can arise
when an ambient representation is restricted to a point stabilizer. This distinction is expressed
by Gelfand pairs and strong Gelfand pairs [ Kra76, CST08]. For a compact group G and a
point stabilizer H, the pair (G,H ) is a Gelfand pair when dimC HomH (1,V )≤1 for every
irreducible complex G-representation V . Thus each ambient representation contains at most
one stabilizer-ﬁxed line, as in the classical constructions. The pair is a strong Gelfand pair when
dimC HomH (E,V )≤1 for every irreducible complex H-representationE. This stronger condi-
tion permits nontrivial stabilizer representations while retaining scalar transition coeﬃcients.
The spherical pair (SO(n),SO (n−1)) is strong by the multiplicity-free branching rule
(72) [ GW09, Thms. 8.1.3–8.1.4]. For the Hamming cube and a weight- w layer, the respective
pairs are
(Bn,S n), (Sn,S w×Sn− w), B n ={±1}n ⋊Sn.
Both are Gelfand pairs but need not be strong. For example, the Littlewood–Richardson coef-
ﬁcient c(3,2,1)
(2,1),(2,1) = 2 produces multiplicity two in both restrictions. Nevertheless, the Fourier
32
===== PAGE 35 =====
spaces in § 2.1 and the two-row Johnson spaces in Lemma 3.1 contain the selected stabilizer
types with multiplicity one. Consequently, both binary arguments remain scalar. More general
binary stabilizer types can require matrix-valued transitions, but they are unnecessary for the
all-distance improvement proved here.
Remark 1.7. Our bounds concern unrestricted codes with ﬁxed relative distance or ﬁxed max-
imum inner product in dimensions tending to inﬁnity. Previous spherical constructions in the
same high-dimensional, ﬁxed-angle setting improve the direct Kabatianskii–Levenshtein bound
for some angles. Relative to the classical bound after spherical-cap optimization, however,
those results improve the bound by constant multiplicative factors rather than its exponential
rate [ SZ24, Z24]. Other results address restricted code families, diﬀerent asymptotic regimes,
or speciﬁc dimensions. The Cohn–Elkies bound is sharp in dimensions 8 and 24, where the
E8 and Leech lattice packings are optimal, respectively [ Via17, CKMR V17]. The n-dimensional
kissing number is τn =A(n, 1/2). Already hierarchy level 2 givesτn≤2(0.39661+o(1))n, compared
with the optimized classical exponent 0.400944... . Its values are known exactly in dimensions
3 [SvdW53], 4 [Mus08], 8 [Lev79], and 24 [OS79]. Semideﬁnite programs improve further ﬁnite-
dimensional binary and spherical bounds [ Sch05, BV08]. MacWilliams’s weight-transform iden-
tities and subsequent spectral and higher-order methods apply to the restricted class of linear
codes [Mac63, FT05, CJJ22, LL23, CJJLL26], while another binary-code improvement concerns
the regime d = n/2−Θ(√n), rather than ﬁxed relative distance [ PMP23]. Constructions of
Delsarte dual certiﬁcates, limitations of particular spectral methods, and lower bounds on spher-
ical, Hamming, and constant-weight linear-programming optima provide additional context but
do not exclude the certiﬁcates constructed here [ Sam01, Sam04, NS05, CD25, Sam25].
2. The first binary bound
We ﬁrst improve the ﬁrst MRR W bound at every relative distance by working directly on
the Hamming cube. The construction uses Fourier levels, elementary Boolean addition and
deletion maps, and a symmetric tridiagonal matrix indexed by consecutive Fourier degrees. Its
new feature is that every degree carries a copy of the same higher-dimensional harmonic space.
In this section, the superscript □ identiﬁes whole-cube representation spaces and dimensions.
Later sections use J and S for the Johnson-layer and spherical constructions, respectively.
2.1. F ourier levels and Boolean harmonics. The classical ﬁrst MRR W bound comes from a
symmetric tridiagonal matrix whose indices are Fourier degrees and whose nonzero oﬀ-diagonal
entries connect consecutive degrees. To improve that bound, we attach a larger Boolean har-
monic space to every selected degree. Identify the binary alphabet with {±1}, and write
Xn ={±1}n. The normalized inner product records Hamming distance:
ℓx = x√n, t (x,y ) =⟨ℓx,ℓ y⟩= 1−2dH(x,y )
n .
Give real-valued functions on Xn the uniform-probability inner product. The Fourier characters
χS(x) = ∏
r∈Sxr, indexed by S⊆[n], form an orthonormal basis; write eS = χS for its basis
vectors. Their degree- i subspace is
V □
i = span{eS :|S|=i}, D □
i = dimV □
i =
(
n
i
)
.
At a word x, the classical spectral construction [ BN06, §3.1] uses the unit vector
vi,x =
(
n
i
)− 1/2 ∑
|S|=i
χS(x)eS.
It is unchanged by every symmetry of the cube ﬁxing x. The inner products ⟨vi,x,v i,y⟩are
normalized Krawtchouk polynomials [ Del73, MRR W77], but their explicit formulas will not be
needed: we use the Fourier spaces and their coordinate transitions ( 17)–(18) instead. Multi-
plication by t(x,·) connects only consecutive Fourier levels. On the lines spanned by vi,x, its
33
===== PAGE 36 =====
oﬀ-diagonal coeﬃcient between degrees i and i + 1 is
√
(i + 1)(n−i)/n. Thus the classical
construction is governed by the symmetric tridiagonal matrix with these neighboring-degree
entries.
To replace each ﬁxed line by a larger subspace, introduce the Boolean addition and deletion
operators [ Sri11, Fei12]:
Ue S =
∑
r /∈S
eS∪{r}, De S =
∑
r∈S
eS\{ r}.
These formulas deﬁne U and D on the Fourier basis and extend linearly to ⨁n
i=0V □
i . Since
adding an element to S is equivalent to deleting the same element from the resulting set, their
matrix coeﬃcients satisfy
⟨Ue S,e T⟩=⟨eS,De T⟩.
Consequently,U ∗ =D. Counting additions and deletions in the two possible orders also gives
(DU−UD )|V □
i
= (n−2i)idV □
i
. (12)
For 0≤k≤n/2, deﬁne the degree- k Boolean harmonic space, with V □
− 1 = 0, by
Ek = ker(D :V □
k →V □
k− 1).
Thus a coeﬃcient vector on the k-element subsets belongs to Ek when its coeﬃcients sum to
zero over all subsets containing any speciﬁed (k−1)-element subset. In particular, E0 is the
constant line, and
E1 =
{n∑
r=1
are{r} :
n∑
r=1
ar = 0
}
has dimension n−1. More generally, for 1≤k≤n/2, ( 12) implies
∥Uf∥2 =∥Df∥2 + (n−2k + 2)∥f∥2 (f∈V □
k− 1).
Thus U : V □
k− 1→V □
k is injective, and its adjoint D : V □
k →V □
k− 1 is surjective. Rank–nullity
therefore gives
d□
k = dimEk =
(
n
k
)
−
(
n
k−1
)
,
where
(n
− 1
)
= 0 . For h∈Ek, induction using ( 12) yields the following identities, valid for
1≤r≤n−2k and 0≤r≤n−2k, respectively:
DU rh =r(n−2k−r + 1)U r− 1h, ∥U rh∥2 =r! (n−2k)!
(n−2k−r)!∥h∥2. (13)
The norm formula in ( 13) follows by repeatedly applying U ∗ = D. Consequently, for every
k≤i≤n−k, the normalized addition map
φih = U i− kh√
(i−k)!(n−2k)!/(n−i−k)! (h∈Ek) (14)
has∥φih∥=∥h∥and therefore embeds Ek isometrically into V □
i . If RxeS = χS(x)eS, then
φi,x =Rxφi transports this copy from the all-ones word to x. For k = 0, its image is precisely
the classical ﬁxed line Rvi,x. For k> 0, every retained Fourier level instead carries a copy of the
same d□
k -dimensional space; when k is proportional to n, that dimension grows exponentially.
The coordinate transitions have an elementary explicit form. For neighboring levels, deﬁne
isometric addition and deletion maps by
Ci,i+1eT = 1√i + 1
∑
r∈T
er⊗eT \{ r}, |T|=i + 1, (15)
Ci+1,ieT = 1√n−i
∑
r /∈T
er⊗eT ∪{r}, |T|=i. (16)
Here er is the rth standard basis vector of Rn, Ci,i+1 : V □
i+1→Rn⊗V □
i , and Ci+1,i : V □
i →
Rn⊗V □
i+1. Each map is an isometry: the displayed summands are distinct orthonormal basis
34
===== PAGE 37 =====
tensors, and inputs to the two maps have i + 1 andn−i summands, respectively. At a common
output level V □
i , the deletion map Ci,i+1 is supported on tensors er⊗eS with r /∈S, whereas
the addition map Ci,i− 1 is supported on tensors with r∈S. Their supports are disjoint, so
their ranges are orthogonal. Set
Qi = (i−k + 1)(n−i−k).
Forf∈V □
i and g∈V □
i+1, the deﬁning basis formulas give
C∗
i,i+1(ℓx⊗Rxf ) = RxUf√
n(i + 1), C ∗
i+1,i(ℓx⊗Rxg) = RxDg√
n(n−i).
By ( 13) and ( 14), the normalized Boolean harmonic embeddings satisfy
Uφ ih =
√
Qiφi+1h, Dφ i+1h =
√
Qiφih.
Combining these identities gives
C∗
i,i+1(ℓx⊗φi,xh) =
√
Qi
n(i + 1)φi+1,xh, (17)
C∗
i+1,i(ℓx⊗φi+1,xh) =
√
Qi
n(n−i)φi,xh. (18)
Thus the squared forward and reverse transition coeﬃcients are
pi,i+1 = Qi
n(i + 1), p i+1,i = Qi
n(n−i).
For k = 0 , all outgoing coeﬃcients at each Fourier degree sum to one on the full path. For
k > 0, they generally do not, because coordinate multiplication also reaches representations
outside the selected path. The coeﬃcients of the two orientations of a given edge are likewise
generally unequal, but they satisfy the dimension-weighted balance identity
(
n
i
)
pi,i+1 =
(
n
i + 1
)
pi+1,i. (19)
This identity will convert the directed transitions into a real symmetric matrix, whose largest
eigenvalue controls the code bound.
2.2. The ﬁnite whole-cube bound. We now symmetrize the directed Fourier-degree transi-
tions and combine their largest eigenvector with the Boolean coordinate maps to construct
a scalar positive-deﬁnite kernel. This gives a bound for codes of ﬁxed ﬁnite length. Fix
0≤k < L≤n−k, and select the Fourier levels V □
k ,...,V □
L . Their symmetric transition
matrix JH =JH(n,k,L ) has zero diagonal and oﬀ-diagonal entries
(JH)i,i+1 = (JH)i+1,i =c(k)
i,H := (i−k + 1)(n−i−k)
n
√
(i + 1)(n−i) . (20)
Indeed, ( 19) says that the directed transition matrix is diagonally similar to a symmetric ma-
trix. The resulting symmetric edge weight is the geometric mean of the coeﬃcients in its two
directions:
√pi,i+1pi+1,i = Qi
n
√
(i + 1)(n−i).
Fork = 0,JH is the classical Krawtchouk matrix underlying the ﬁrst MRR W bound [ MRR W77];
its tridiagonal spectral formulation appears in [ BN06, §3.1]. For positive k, JH is still indexed
by consecutive Fourier degrees and connects only neighboring degrees, but every degree carries
a copy of the d□
k -dimensional harmonic space. The resulting weighted path is shown in Figure 1.
Theorem 2.1. Letn,d,k,L be integers with 1≤d≤n and 0≤k<L ≤n−k. Set s = 1−2d/n
and λ =λmax(JH(n,k,L )). If λ>s , then
A2(n,d )≤
(
1−s
d□
k (λ−s)
) L∑
i=k
(
n
i
)
. (21)
35
===== PAGE 38 =====
V □
k
φk,xEk
V □
k+1
φk+1,xEk
V □
i
φi,xEk
V □
i+1
φi+1,xEk
V □
L− 1
φL−1,xEk
V □
L
φL,xEk
c(k)
k,H
···
c(k)
i,H
···
c(k)
L−1,H
Every vertex carries the same harmonic space Ek.
Figure 1. The whole-cube representation path at ﬁxed Boolean harmonic de-
gree k. Each Fourier level contains the isometric copy φi,xEk, and neighboring
levels have symmetric edge weight c(k)
i,H from (20). The classical path corresponds
to the one-dimensional ﬁber E0.
Proof. We ﬁrst construct a positive-deﬁnite projection kernel from the Boolean coordinate maps
and the Perron eigenvector of JH. Let I ={k,...,L }index the vertices of JH(n,k,L ), and put
V =
⨁
i∈I
V □
i , D amb = dimV =
∑
i∈I
D□
i .
Since the oﬀ-diagonal entries in ( 20) are strictly positive, its largest eigenvalue λ =λmax(JH)> 0
has a strictly positive unit eigenvector v = (vi)i∈I . Write
wi =
√
D□
i vi, Z =
∑
i∈I
wi.
The dimension balance ( 19) and JHv =λv imply
∑
i∈I
|i− j|=1
pi,jwi =λwj (j∈I). (22)
For eachj, dividing by λwj therefore turns the incoming weights into a probability distribution
on its retained neighbors. The square roots of these normalized weights are the coeﬃcients in
the coordinate isometry below.
For each wordx∈Xn, combine its copies of the Boolean harmonic space Ek into the isometric
embedding
Ψx :Ek−→V, Ψxh =
⨁
i∈I
√wi
Z φi,xh.
Let Px = Ψ xΨ∗
x be the orthogonal projection onto its image. Thus every Px has rank d□
k , and
its scalar overlap with another projection is
K(x,y ) = tr(PxPy) =∥PxPy∥2
HS≥0, ∥A∥2
HS = tr(A∗A).
As a Hilbert–Schmidt Gram kernel, K is positive deﬁnite. Coordinate permutations and sign
changes transportPx to the projection associated with the transformed word, so K(x,y ) depends
only on dH(x,y ).
Forf =⨁
j∈Ifj∈V, the concrete coordinate maps ( 15) and ( 16) deﬁne an operator between
the corresponding direct sums:
B :V−→Rn⊗V=
⨁
i∈I
(Rn⊗V □
i ),
Bf =
⨁
i∈I
∑
j∈I
|i− j|=1
√
pi,jwi
λwj
Ci,jfj.
For each i, the images of Ci,i− 1 and Ci,i+1 in Rn⊗V □
i are orthogonal: their respective basis
tensors er⊗eS satisfy r∈S and r /∈S. Therefore ( 22) gives
∥Bf∥2 =
∑
j∈I
∥fj∥2
λwj
∑
i∈I
|i− j|=1
pi,jwi =∥f∥2.
36
===== PAGE 39 =====
ThusB is an isometry and B∗B = id V . For a harmonic vector h∈Ek, the explicit contractions
(17) and ( 18) likewise give
B∗(ℓx⊗Ψxh) =
⨁
j∈I
φj,xh√
λwjZ
∑
i∈I
|i− j|=1
pi,jwi =
⨁
j∈I
√
λwj
Z φj,xh.
Consequently,
B∗(ℓx⊗Ψxh) =
√
λ Ψxh. (23)
To expose the positivity needed for the code bound, set
Lx = (ℓx⊗id)Px, G x =BPx, Θx =Lx−
√
λG x.
These are maps from V to Rn⊗V. Their Hilbert–Schmidt pairings are
⟨Lx,L y⟩HS = tr [Px(ℓx⊗id)∗(ℓy⊗id)Py] = t(x,y )K(x,y ),
⟨Gx,G y⟩HS = tr(PxB∗BPy) = tr(PxPy) = K(x,y ).
Since imPx = im Ψx, ( 23) implies
B∗(ℓx⊗id)Px =
√
λP x. (24)
Taking the adjoint of ( 24), and then applying the same identity at y, yields both mixed pairings:
⟨Lx,G y⟩HS = tr [Px(ℓx⊗id)∗BPy] =
√
λK (x,y ),
⟨Gx,L y⟩HS = tr [PxB∗(ℓy⊗id)Py] =
√
λK (x,y ).
Expanding⟨Lx−
√
λG x,L y−
√
λG y⟩HS now gives
⟨Θx, Θy⟩HS =
(
t(x,y )−λ
)
K(x,y ). (25)
In particular, for every s<λ ,
(
t(x,y )−s
)
K(x,y ) = (λ−s)K(x,y ) +⟨Θx, Θy⟩HS.
Both summands are positive-deﬁnite Gram kernels, so (t−s)K is a scalar two-point Delsarte
certiﬁcate.
LetC⊆Xn have minimum Hamming distance at least d, and put NC =|C|. The projection
kernel constructed above satisﬁes K(x,y ) ≥0. Hence (t(x,y )−s)K(x,y ) ≤0 for distinct
x,y∈C, whereas its diagonal value is (1−s)d□
k . Summing ( 25) over C2 gives
(λ−s)

∑
x∈C
Px

2
HS
≤NC(1−s)d□
k.
Since every Px has rank d□
k and Damb =∑L
i=k
(n
i
)
, trace Cauchy–Schwarz gives

∑
x∈C
Px

2
HS
≥N 2
C(d□
k )2
L∑
i=k
(
n
i
).
Combining these estimates proves ( 21). □
2.3. Asymptotic improvement over the ﬁrst MRR W bound. To compare the ﬁnite
bound with M1, take both the harmonic degree and the largest retained Fourier degree pro-
portional to n. The largest eigenvalue of the explicitly deﬁned tridiagonal matrix JH(n,k,L )
determines whether the spectral condition λmax(JH(n,k,L ))> 1−2d/n in Theorem 2.1 holds,
while the dimension of Ek gives the exponential saving. Recall the binary entropy H2, the
asymptotic rate R2, the ﬁrst MRR W exponent M1, and the whole-cube exponent κH from the
introduction. The spectral calculations use the Rayleigh–Ritz principle: for every real symmet-
ric matrix J,
λmax(J) = max
a̸=0
⟨a,Ja⟩
⟨a,a⟩. (26)
37
===== PAGE 40 =====
Lemma 2.2. Suppose 0≤b < a≤1/2, and let kn < Ln ≤⌊n/2⌋satisfy kn/n→b and
Ln/n→a. Then
limn→∞ λmax
(
JH(n,k n,L n)
)
= Γ H(a,b ).
Proof. For a degree i with i/n→x> 0, the neighboring-degree entry of JH(n,k n,L n) satisﬁes
c(kn)
i,H −→gb(x) := (x−b)(1−x−b)√
x(1−x) =
√
x(1−x)−b(1−b)√
x(1−x).
The ﬁnite entries are increasing through the selected degrees. Indeed, put Yi = (i + 1)(n−i)
and Tk =kn(n + 1−kn). Then
nc(kn)
i,H = Yi−Tk√Yi
.
Both Yi and the function Y ↦→(Y−Tk)/
√
Y increase for kn≤i < Ln≤n/2. Consequently,
the largest row sum gives
λmax
(
JH(n,k n,L n)
)
≤2c(kn)
Ln− 1,H−→2gb(a).
Choose integers mn→∞with mn = o(n), and deﬁne a vector supported on the last mn
Fourier degrees by
fLn− mn+r = sin πr
mn + 1 (1≤r≤mn).
Although the entries vary across the full Fourier-degree path, they converge uniformly to gb(a)
on these last mn = o(n) degrees. The restricted matrix therefore becomes a constant-weight
nearest-neighbor adjacency operator. Its ﬁrst discrete sine vector and ( 26) give
λmax
(
JH(n,k n,L n)
)
≥2gb(a) cos π
mn + 1 +o(1).
Takingn→∞and recalling ΓH(a,b ) = 2gb(a) proves the claim. □
Theorem 2.3. For every ﬁxed 0<δ < 1/2,
R2(δ)≤κH(δ)<M 1(δ).
Proof. Fix 0≤b < a≤1/2 with ΓH(a,b ) > 1−2δ, as in ( 2), and take k =⌊bn⌋, L =⌊an⌋,
and dn =⌈δn⌉. The ﬁnite distance threshold is sn = 1−2dn/n→1−2δ. By Lemma 2.2 ,
λmax(JH(n,k,L ))→ΓH(a,b ). Stirling’s formula gives
1
n log2
L∑
i=k
(
n
i
)
=H2(a) +o(1), 1
n log2d□
k =H2(b) +o(1).
Strict feasibility in ( 2) gives λmax(JH(n,k,L ))−sn> 0, bounded away from zero for large n, so
the prefactor in ( 21) stays bounded. Taking logarithmic rates and then the inﬁmum over (a,b )
givesR2(δ)≤κH(δ).
At the classical ﬁxed-line spectral boundary, put a0 = 1
2−
√
δ(1−δ) and b = 0. Then
ΓH(a0, 0) = 2
√
a0(1−a0) = 1−2δ, H 2(a0)−H2(0) = M1(δ).
At this boundary point,
∂aΓH> 0, −∂bΓH
∂aΓH
= 2
1−2a0
.
Thus every c >2/(1−2a0) gives strictly feasible parameter pairs a = a0 +cb for suﬃciently
smallb> 0. The ambient entropy H2(a) increases by Oδ(b), whereas H2(b) = b log2(1/b) +O(b).
The harmonic-space entropy therefore dominates the spectral cost as b↓0, proving κH(δ) <
M1(δ). □
38
===== PAGE 41 =====
3. The optimized binary bound
The ﬁrst MRR W exponent is not always the smallest classical bound. To improve the op-
timized second MRR W exponent M2, we adapt the whole-cube projection argument of Theo-
rem 2.1 to a constant-weight layer and then transfer the resulting estimate back to unrestricted
binary codes. Johnson degrees replace Fourier degrees, and two Boolean harmonic spaces, on
the support and its complement, replace the single whole-cube harmonic space.
3.1. Constant-weight layers and their harmonic spaces. To improve the constant-weight
part of the second MRR W bound, we ﬁrst reduce an unrestricted code to words with a common
weight. Identify such words with their supports, and write Xw =
([n]
w
)
for the weight-w layer.
Let AJ (n,w,d ) be the largest size of a code in Xw with minimum Hamming distance at least
d. A veraging the intersection of an unrestricted binary code with all translates of the weight- w
layer gives the Bassalygo–Elias inequality [ Bas65, MRR W77]:
A2(n,d )≤2n
(n
w
)AJ (n,w,d ). (27)
When w/n →α, its prefactor has exponential rate 1−H2(α). It therefore suﬃces to con-
struct a constant-weight bound that improves the classical Hahn-polynomial construction after
accounting for this reduction.
A base word x∈Xw partitions the coordinates into x and xc, of sizes w and N = n−w,
respectively. Complementation preserves Hamming distance, so we assume 1≤w < n/2; the
middle layer follows by taking w/n→1/2.
Coordinate permutations preserve the layer, and those ﬁxing x separately permute its support
and complement. The distance between two words in the layer is even: half their Hamming
distance is the number of coordinates removed from one support to obtain the other. For
x,y∈Xw, put
r(x,y ) = w−|x∩y|= 1
2dH(x,y ), t (x,y ) = 1−nr (x,y )
wN . (28)
The unit vectors ℓx =
√
n/(wN )(1x−(w/n)1) satisfy⟨ℓx,ℓ y⟩=t(x,y ).
Give functions onXw the uniform-probability inner product. The standard Johnson harmonic
decomposition, indexed by degrees 0≤j≤w, is the constant-weight analogue of the Fourier
decomposition [ Del73]:
RXw =
w⨁
j=0
V J
j , D J
j = dimV J
j =
(
n
j
)
−
(
n
j−1
)
. (29)
As a representation of the coordinate permutation group Sn, the space V J
j is the Specht module
indexed by the two-row partition (n−j,j ) [Del73, Sri11]. In particular, these spaces are pairwise
inequivalent and irreducible. In the classical construction, the permutations ﬁxing x ﬁx a single
line in V J
j , whose overlap kernel is a Hahn polynomial in r(x,y ). Neither its explicit polynomial
formula nor the adjacency eigenvalues will be needed: the argument uses the Johnson harmonic
spaces and the associated Hahn recurrence coeﬃcients ( 35). We replace the ﬁxed line by a
product of Boolean harmonic spaces, one on the support and one on its complement, extending
the degree-k Boolean harmonics of § 2.1. For a ﬁnite set A, identify R(A
p) with real functions
on its p-element subsets. For 0≤p≤|A|/2, let Ep(A) = ker ∂, where ∂ : R(A
p)→R( A
p−1) is
the Boolean lowering map (∂f )(T ) = ∑
a∈A\ Tf (T∪{a}), with R( A
−1) = 0. Thus f is harmonic
precisely when its values sum to zero over the p-subsets extending each (p−1)-subset. Its
harmonic dimension is
dp(|A|) := dimEp(A) =
(
|A|
p
)
−
(
|A|
p−1
)
. (30)
For 0≤p≤w/2 and 0≤q≤N/2, deﬁne the attached harmonic space and its dimension by
Ep,q
x =Ep(x)⊗Eq(xc), d J
p,q =dp(w)dq(N ).
39
===== PAGE 42 =====
Thusp andq are harmonic degrees on the support and its complement, not dimensions. These
Boolean harmonic spaces are the Specht modules indexed by (w−p,p ) and (N−q,q ), respec-
tively [Sri11]. The two-row Littlewood–Richardson restriction rule for Sn↓Sw×SN determines
exactly which Johnson degrees contain their tensor product Ep,q
x , and shows that each such
degree contains it with multiplicity one [ GW09, §9.3.5].
Lemma 3.1. Letn,w,p,q be integers with 1≤w<n/ 2, 0≤p≤w/2, and 0≤q≤(n−w)/2.
Put N = n−w, and ﬁx x∈Xw. The Johnson space V J
j contains a copy of Ep,q
x preserved by
the permutations ﬁxing x precisely when
j− =p +q≤j≤j+ := min{w,w−p +q,N +p−q}. (31)
This copy occurs once, and its isometric embedding φj,x : Ep,q
x →V J
j , commuting with those
permutations, is unique up to sign.
3.2. The associated Hahn tridiagonal matrix. To adapt the projection argument of The-
orem 2.1 to the layer Xw, we need the coordinate transitions between the copies of Ep,q
x in
successive Johnson degrees. These transitions are governed by an associated Hahn recurrence.
For ﬁxed x, let Mx denote multiplication by y↦→t(x,y ). Its action on the Johnson harmonic
spaces satisﬁes the degree-one product rule [ BCV23, (90)]:
MxV J
j ⊆V J
j− 1⊕V J
j ⊕V J
j+1. (32)
Because Mx commutes with all permutations ﬁxing x, Lemma 3.1 reduces its action on the
copies of Ep,q
x to a scalar three-term recurrence. Its coeﬃcients are conveniently expressed using
six standard Hahn-recurrence parameters:
ȷ1 = w
2−p, ȷ 2 = N
2 −q, ȷ = n
2−j, m 0 = n
2−w, Σ = ȷ1 +ȷ2, ∆J =ȷ2−ȷ1. (33)
Hereȷ1,ȷ 2 depend on the two Boolean harmonic degrees, ȷ depends on the Johnson degree, and
m0 depends only on the layer weight. Write
µp,q
j = m0
2
ȷ2(ȷ2 + 1)−ȷ1(ȷ1 + 1)
ȷ(ȷ + 1) ,
νp,q
j =
√
(ȷ2−m2
0)(ȷ2−∆2
J)((Σ + 1)2−ȷ2)
2ȷ
√
(2ȷ−1)(2ȷ + 1) . (34)
Only j−≤j <j+ require νp,q
j . Deﬁne the diagonal and oﬀ-diagonal recurrence coeﬃcients by
bp,q
j =
nµp,q
j −m2
0
wN , c p,q
j =
nνp,q
j
wN . (35)
The numbers bp,q
j andcp,q
j are the associated Hahn recurrence coeﬃcients [ BCV23, (91)–(92)],
with (j1,j 2,j,m ) = ( ȷ2,ȷ 1,ȷ,m 0) and with the operator normalized to act by multiplication
by t(x,·). Their identiﬁcation with Hahn polynomials is classical [ Koo81, §4]. Setting p =
q = 0 recovers the ordinary Hahn recurrence on the stabilizer-ﬁxed lines, while positive p or q
introduces a higher-dimensional harmonic space.
We now ﬁx the embeddings in Lemma 3.1 unambiguously. Suppose j− ≤j+; otherwise
no Johnson harmonic space contains Ep,q
x . Choose a reference support x0 and an isometric
stabilizer-equivariant embedding φj−,x0 :Ep,q
x0 →V J
j− . Write ΠJ
j for orthogonal projection onto
V J
j . For each successive degree, choose the sign of its isometric embedding so that, for every
Y ∈Ep,q
x0 ,
ΠJ
j+1
(
t(x0,·)φj,x0Y
)
=cp,q
j φj+1,x0Y, j −≤j <j+. (36)
The associated Hahn coeﬃcients cp,q
j are positive throughout this range, so this condition deter-
mines each successive sign. For every support x =gx0, transport all the resulting embeddings
byφj,x =gφj,x0g− 1. This deﬁnition is independent of the permutation g: two choices diﬀer by
a permutation ﬁxing x0, and every φj,x0 intertwines their actions.
40
===== PAGE 43 =====
Proposition 3.2. Let n,w,p,q be integers with 1≤w < n/2, 0≤p≤w/2, and 0≤q≤
(n−w)/2. Put N =n−w, and set j− =p +q and j+ = min{w,w−p +q,N +p−q}. Suppose
j−≤j+. For every x∈Xw, Y ∈Ep,q
x , and j−≤j≤j+, the embeddings ﬁxed in (36) satisfy
t(x,·)φj,xY =cp,q
j− 1φj− 1,xY +bp,q
j φj,xY +cp,q
j φj+1,xY, (37)
where the degree- (j−1) term is omitted when j = j− , and the degree- (j + 1) term is omitted
when j =j+. Every retained oﬀ-diagonal coeﬃcient satisﬁes cp,q
j > 0 for j−≤j <j+.
Proof. Let Hx = Sx×Sxc ≤Sn be the stabilizer of the support x; its two factors permute
x and xc, respectively. Multiplication by t(x,·) and each projection ΠJ
i commute with Hx.
Consequently,
ΠJ
i Mxφj,x :Ep,q
x −→V J
i
is Hx-equivariant. By Lemma 3.1 , its image is zero unless j− ≤i≤j+, and otherwise it lies
in the unique copy φi,xEp,q
x . The Johnson product rule ( 32) further restricts i to j−1,j,j + 1.
Since Ep,q
x is the outer tensor product of two absolutely irreducible real Specht modules, every
Hx-equivariant endomorphism of Ep,q
x is a real scalar. Therefore each surviving component is a
scalar multiple of φi,x.
The associated Hahn recurrence and coeﬃcient formulas [ BCV23, (90)–(92)], with the param-
eters and coordinate normalization in ( 33)–(35), give the diagonal scalar bp,q
j and the absolute
valuecp,q
j of the degree- (j + 1) scalar. For j−≤j <j+,
0< max{m0,|∆J|}<ȷ ≤Σ.
Indeed, j≥j− =p +q givesȷ≤Σ, while
n
2−j+ = max{m0,|∆J|}
and j < j+ give the strict lower inequality. Therefore all three radicand factors in ( 34) are
positive, as is its denominator, proving cp,q
j > 0. The orientation ( 36) ﬁxes the degree- (j + 1)
component at x0. Since t(gx0,gy ) = t(x0,y ), transporting the embeddings gives cp,q
j φj+1,x for
everyx.
If j >j− , self-adjointness of Mx and the isometry of the embeddings give, for Y,Z ∈Ep,q
x ,
⟨
φj− 1,xZ, Mxφj,xY
⟩
=
⟨
Mxφj− 1,xZ,φ j,xY
⟩
=cp,q
j− 1⟨Z,Y⟩.
Thus the degree- (j−1) component is cp,q
j− 1φj− 1,xY , proving ( 37). At the lower endpoint, the
formal preceding index j−−1 givesȷ = Σ + 1, making (Σ + 1)2−ȷ2 = 0. At the upper endpoint,
ȷ = max{m0,|∆J|}; hence ȷ2−m2
0 = 0 if j+ = w, and ȷ2−∆2
J = 0 if j+ = w−p +q or
j+ =N +p−q. These are precisely the missing transitions beyond the branching range. When
j− =j+, both oﬀ-diagonal terms are absent. □
Writeb0
j = b0,0
j and c0
j = c0,0
j for the classical ﬁxed-line coeﬃcients. The ﬁxed-line diagonal
satisﬁes b0
0 = 0 and, for 1≤j≤w,
b0
j = m2
0j(n−j + 1)
wNȷ (ȷ + 1) > 0,
and c0
j > 0 for 0≤j <w.
The associated Hahn coeﬃcients describe multiplication by the scalar distance coordinate
t(x,·). The projection construction instead requires isometric maps between Johnson spaces
and their tensor products with the coordinate space W = 1⊥ ⊆Rn. Their normalization is
determined by the ﬁxed-line case of ( 37).
For Johnson degrees i,j in ( 31) with|i−j|≤1, set
rp,q
i,j =
{
bp,q
i , i =j,
cp,q
min{i,j}, |i−j|= 1, r0
i,j =
{
b0
i, i =j,
c0
min{i,j}, |i−j|= 1.
41
===== PAGE 44 =====
Thus rp,q
i,j is the scalar coeﬃcient connecting the copies of Ep,q
x in V J
i and V J
j , whereas r0
i,j is
the corresponding coeﬃcient for the classical ﬁxed lines. Except when i =j = 0, the ﬁxed-line
coeﬃcient is strictly positive.
Lemma 3.3. Let i,j be Johnson degrees in (31) with|i−j|≤1 and (i,j )̸= (0, 0). There is
an Sn-equivariant isometry
Ci,j :V J
j −→W⊗V J
i
whose contraction onto the selected harmonic spaces is
C∗
i,j(ℓx⊗φi,xY ) =√pi,jφj,xY, p i,j =
(rp,q
i,j )2
r0
i,j
√DJ
j
DJ
i
, (38)
for every x∈Xw and Y ∈Ep,q
x . Consequently,
DJ
ipi,j =DJ
jpj,i, √pi,jpj,i =
(rp,q
i,j )2
r0
i,j
. (39)
Proof. Writeσ for uniform probability measure on Xw, and let Ki and Kj be the reproducing
kernels of V J
i and V J
j . Permutations act transitively on Xw, so these kernels have constant
diagonal values Ki(x,x ) = DJ
i and Kj(x,x ) = DJ
j . Hence
zi,x = Ki(x,·)√
DJ
i
, z j,x = Kj(x,·)√
DJ
j
are the unit stabilizer-ﬁxed vectors positive at x. Their ordinary Hahn recurrence, the p =q = 0
case of ( 37), says that
ΠJ
j
(
t(x,·)zi,x
)
=r0
i,jzj,x. (40)
Deﬁne the coordinate-multiplication map by
Mi,j :W⊗V J
i −→V J
j , Mi,j(v⊗f ) = Π J
j
(
⟨v,ℓ ·⟩f
)
.
It commutes with coordinate permutations, so the positive operator Mi,jM∗
i,j on the irreducible
Johnson space V J
j is a scalar multiple of the identity. To identify that scalar, expand the
Hilbert–Schmidt norm in orthonormal bases. The coordinate identity following ( 28), together
with permutation invariance and the ﬁxed-line recurrence ( 40), gives
∥Mi,j∥2
HS =
∫∫
X 2w
t(y,z )Ki(y,z )Kj(y,z )dσ(y)dσ(z)
=
∫
Xw
t(x,y )Ki(x,y )Kj(x,y )dσ(y)
=r0
i,j
√
DJ
iDJ
j.
Taking the trace on the DJ
j -dimensional output space now yields
Mi,jM∗
i,j =mi,jidV J
j
, m i,j =r0
i,j
√DJ
i
DJ
j
.
Let εi,j = 1 when rp,q
i,j ≥0 and εi,j =−1 otherwise. Then
Ci,j = εi,j
√mi,j
M∗
i,j
is an equivariant isometry. By ( 37), its contraction on Ep,q
x is
C∗
i,j(ℓx⊗φi,xY ) =
|rp,q
i,j|
√mi,j
φj,xY.
Squaring this coeﬃcient gives ( 38). Since rp,q
i,j =rp,q
j,i and r0
i,j =r0
j,i, applying the same formula
in the reverse direction proves ( 39). □
42
===== PAGE 45 =====
By Lemma 3.3, the symmetric matrix entry associated with a Johnson transition is the square
of its associated Hahn coeﬃcient divided by the corresponding ordinary Hahn coeﬃcient. For
j− <L ≤j+, retain the consecutive Johnson degrees j−,...,L . Their coordinate-transition ma-
trix is tridiagonal: its oﬀ-diagonal entries connect neighboring Johnson degrees, and a diagonal
entry is allowed at each degree. Write ˆJ = ˆJ(n,w,p,q,L ) for the symmetric matrix
ˆJj,j =ˆbp,q
j :=
{
(bp,q
j )2/b0
j, j ≥1,
0, j = 0, (41)
ˆJj,j+1 = ˆJj+1,j =ˆcp,q
j :=
(cp,q
j )2
c0
j
. (42)
With the Johnson dimensions DJ
j from ( 29), the squared directed contraction coeﬃcients in
Lemma 3.3 are
pj,j+1 =ˆcp,q
j
√DJ
j+1
DJ
j
, p j+1,j =ˆcp,q
j
√DJ
j
DJ
j+1
, p j,j =ˆbp,q
j .
Forp =q = 0, the diagonal and oﬀ-diagonal coeﬃcients sum to one over the complete Johnson-
degree path. For higher harmonic types, or after truncating that path, the retained coeﬃcients
need not have this normalization. Consequently, the Johnson dimensions satisfy
DJ
jpj,j+1 =DJ
j+1pj+1,j. (43)
The geometric means of the forward and reverse coeﬃcients are exactly the oﬀ-diagonal entries
of ˆJ. Since j− < L, the Johnson matrix ˆJ has a positive largest eigenvalue λ = λmax(ˆJ), so
λ>s implies λ> max{s, 0}.
Theorem 3.4. Letn,w,p,q,L,d be integers with 1≤w<n/ 2, 0≤p≤w/2, 0≤q≤(n−w)/2,
and
p +q <L≤min{w,w−p +q,n−w +p−q}.
Supposed is even and 2≤d≤2w. Put
N =n−w, s = 1−nd
2wN, λ =λmax
(ˆJ(n,w,p,q,L )
)
,
where ˆJ is given by (41)–(42). If λ>s , then
AJ (n,w,d )≤1−s
λ−s
L∑
j=p+q
((
n
j
)
−
(
n
j−1
))
((
w
p
)
−
(
w
p−1
))((
N
q
)
−
(
N
q−1
)). (44)
Proof. Let I ={p +q,...,L }, let v = (vj)j∈I be the positive unit Perron eigenvector of the
Johnson matrix ˆJ in ( 41)–(42), and put
ωj =
√
DJ
jvj, Z =
∑
j∈I
ωj.
The Johnson dimension balance ( 43) gives
∑
i∈I
|i− j|≤1
pi,jωi =λωj. (45)
As in the whole-cube identity ( 22), dividing by λωj normalizes the incoming transition weights
to sum to one. Combine the copies of Ep,q
x in the selected Johnson spaces by setting
ΨxY =
⨁
j∈I
√ωj
Z φj,xY, P x = Ψ xΨ∗
x.
These projections have rank dJ
p,q on the ambient space V =⨁
j∈IV J
j .
43
===== PAGE 46 =====
WriteW = 1⊥ ⊆Rn, and let Ci,j : V J
j →W⊗V J
i be the normalized Johnson coordinate
isometries constructed in Lemma 3.3 for (i,j )̸= (0, 0); set C0,0 = 0, consistently with p0,0 = 0.
For ﬁxed i, the nonzero images for distinct j are orthogonal: they are invariant irreducible
subspaces of W⊗V J
i carrying pairwise inequivalent permutation representations V J
j . Their
contraction coeﬃcients on Ep,q
x are√pi,j, by Lemma 3.3 . Deﬁne B :V→W⊗Vby
Bf =
⨁
i∈I
∑
j∈I
|i− j|≤1
√
pi,jωi
λωj
Ci,jfj, f =
⨁
j∈I
fj∈V.
Orthogonality and the Perron identity ( 45) show that B is an isometry and B∗(ℓx⊗ΨxY ) =√
λ ΨxY . Consequently, if Θx = (ℓx⊗id)Px−
√
λBPx, direct expansion gives
⟨Θx, Θy⟩HS =
(
t(x,y )−λ
)
tr(PxPy).
For a constant-weight code C of size NC, the oﬀ-diagonal terms of (t(x,y )−s) tr(PxPy) are
nonpositive, and the diagonal terms equal (1−s)dJ
p,q. Summation and trace Cauchy–Schwarz
therefore give
(λ−s) N 2
C(dJ
p,q)2
∑L
j=p+qDJ
j
≤NC(1−s)dJ
p,q.
Substituting DJ
j =
(n
j
)
−
( n
j− 1
)
and dJ
p,q = dp(w)dq(N ) proves ( 44). The overlap is a scalar
function of Johnson distance because coordinate permutations are transitive on pairs of supports
having the same intersection size. □
3.3. The asymptotic constant-weight bound. The ﬁnite constant-weight certiﬁcate in The-
orem 3.4 bounds a code by the ratio between the total dimensions of the retained Johnson spaces
and the dimension of the attached Boolean harmonic space. We now pass to high-dimensional
limits, estimate its largest eigenvalue, and include the Bassalygo–Elias cost of returning to the
whole cube.
Fix 0 < δ <1/2, and recall the normalized parameters α = w/n, β = p/n, γ = q/n, and
u = L/n from the introduction. They represent the relative layer weight, the two normalized
Boolean harmonic degrees, and the largest retained Johnson degree, respectively. Their ranges
are ( 4)–(5), and ( 6) gives an asymptotic lower bound for the largest eigenvalue of the Johnson
recurrence matrix ˆJ.
Lemma 3.5. Suppose (α,β,γ,u ) satisﬁes (4) and (5), and choose integers with
w
n→α, p
n→β, q
n→γ, L
n→u.
For the Johnson tridiagonal matrix ˆJ(n,w,p,q,L ), one has
lim infn→∞ λmax
(ˆJ(n,w,p,q,L )
)
≥Λα,β,γ (u). (46)
Proof. Let z,m,ζ,ξ be the normalized coordinates preceding ( 6). Uniformly for |j/n−u|→0,
substitution in ( 35) gives
bp,q
j −→m(ζξ−mz2)
z2(1−m2) , b0
j−→m2(1−z2)
z2(1−m2),
cp,q
j −→
√
(z2−m2)(z2−ξ2)(ζ 2−z2)
2z2(1−m2) , c0
j−→(z2−m2)
√
1−z2
2z2(1−m2) .
The strict inequalities in ( 4) and ( 5) keep all denominators bounded away from zero and place
the terminal degree strictly inside the Johnson-degree range ( 31), so j− < L < j+ for large n.
Choose mn→∞with mn =o(n). Then L−mn≥j− and L<j + for large n, so the discrete
sine vector
fL− mn+r = sin πr
mn + 1 (1≤r≤mn)
is supported on Johnson degrees j−≤j≤j+.
44
===== PAGE 47 =====
By ( 41) and ( 42), the diagonal entries on this terminal degree interval converge uniformly to
B = (ζξ−mz2)2
z2(1−m2)(1−z2),
while the neighboring-degree entries converge uniformly to
C = (z2−ξ2)(ζ 2−z2)
2z2(1−m2)
√
1−z2.
The Rayleigh–Ritz principle ( 26) applied to the displayed sine vector gives
λmax(ˆJ)≥B + 2C cos π
mn + 1 +o(1).
Since B + 2C = Λ α,β,γ (u), taking n→∞proves (46). □
Theorem 3.6. Fix 0<δ < 1/2. If (α,β,γ,u )∈Dδ, then
R2(δ)≤1−H2(α) +H2(u)−αH2
(β
α
)
−(1−α)H2
( γ
1−α
)
. (47)
Proof. Choose integers with w/n →α, p/n→β, q/n →γ, and L/n→u, and put dn =
2⌊⌈δn⌉/2⌋. This is the largest even integer not exceeding ⌈δn⌉, so dn/n→δ andA2(n,⌈δn⌉)≤
A2(n,d n). Since α>δ/ 2> 0, the ﬁnite-theorem hypotheses 2≤dn≤2w hold for all suﬃciently
large n. By Lemma 3.5 , the largest eigenvalue of ˆJ(n,w,p,q,L ) has limiting lower bound
Λα,β,γ (u). The dimensions of the retained Johnson spaces telescope to
L∑
j=p+q
((
n
j
)
−
(
n
j−1
))
=
(
n
L
)
−
(
n
p +q−1
)
= 2 nH2(u)+o(n).
Stirling’s formula and ( 30) likewise give
1
n log2dJ
p,q =αH2
(β
α
)
+ (1−α)H2
( γ
1−α
)
+o(1).
The ﬁnite threshold 1−ndn/(2w(n−w)) converges to the right-hand side of ( 7). Thus strict
feasibility and ( 46) bound the prefactor in ( 44). Taking the logarithmic rate of this ﬁnite
Johnson bound and adding the Bassalygo–Elias cost 1−H2(α) from ( 27) proves ( 47). □
Taking the inﬁmum in ( 47) overDδ recovers the constant-weight exponent ( 8) and gives
R2(δ)≤κCW(δ).
3.4. Strict comparison with the classical bound. We now show that the two binary con-
structions together strictly improve the fully optimized classical bound at every relative dis-
tance. Recall the MRR W objective Fδ, its endpoint values M1(δ) and Fδ(0), and its opti-
mized value M2(δ) from ( 1)–(3). In particular, M2(δ)≤M1(δ). We ﬁrst identify the classical
constant-weight objective inside our construction by taking the one-dimensional ﬁxed-line choice
p =q = 0. A higher-dimensional choice then improves every interior minimizer, while the whole-
cube certiﬁcate handles the endpoint with value M1.
We ﬁrst identify the ﬁxed-line specialization β = γ = 0 with the fully optimized classical
objective ( 3). Write A =α(1−α) and U =u(1−u). Then
1−Λα,0,0(u) = A−U
A(1 + 2
√
U )
. (48)
On the spectral boundary, τ = 2
√
U gives
4A =τ 2 + 2δτ + 2δ, 1−H2(α) +H2(u) = 1 + g(τ 2)−g(τ 2 + 2δτ + 2δ).
Equivalently,u = (1−
√
1−τ 2)/2 and α = (1−
√
1−τ 2−2δτ−2δ)/2. Hence 0<τ < 1−2δ
corresponds exactly to 0 < u < α <1/2; moreover, α > δ/2, so the shell-domain conditions
hold. Every boundary point is approached by strictly feasible u′>u , while τ = 0 andτ = 1−2δ
are obtained as u↓0 and α↑1/2, respectively. Consequently,
κCW(δ)≤M2(δ).
45
===== PAGE 48 =====
Proposition 3.7. Fix 0<δ < 1/2, and suppose 0<u<α< 1/2 and
Λα,0,0(u) = 1− δ
2α(1−α).
Then there exist β,γ > 0 and u′ with (α,β,γ,u ′)∈Dδ whose rate in (47) is strictly smaller
than 1−H2(α) +H2(u).
Proof. Put β =γ =ε. By ( 48),
∂uΛα,0,0(u) = (1−2u)
[
1
A(1 + 2
√
U )
+ A−U
A
√
U (1 + 2
√
U )2
]
> 0.
Here A = α(1−α) and U = u(1−u). Smoothness at the interior point shows that replacing
(β,γ ) = (0 , 0) by (ε,ε ) changes the spectral value by O(ε). Thus, for a suﬃciently large
ﬁxed C, the choice uε = u +Cε satisﬁes ( 4)–(7) strictly. The ambient entropy increases by
H2(uε)−H2(u) = O(ε), whereas the two harmonic-space dimensions contribute
αH2
(ε
α
)
+ (1−α)H2
( ε
1−α
)
= 2ε log2
1
ε +O(ε).
This gain dominates O(ε), proving the strict improvement. □
Theorem 3.8. For every ﬁxed 0<δ < 1/2,
κbin(δ) = min{κH(δ),κ CW(δ)}<M 2(δ).
Proof. Suppose ﬁrst that M2(δ)<M 1(δ). The endpoint τ = 1−2δ cannot minimize Fδ, since
its value is M1(δ). At the other endpoint τ = 0 , g(τ 2) = O(τ 2 log(1/τ )) = o(τ ), so F ′
δ(0+) =
−2δg ′(2δ)< 0. Hence every minimizer is interior, and Proposition 3.7 givesκCW(δ)<M 2(δ). If
M2(δ) = M1(δ), Theorem 2.3 instead gives κH(δ)<M 2(δ). In either case, κbin(δ)<M 2(δ). □
4. Representation graphs for spherical codes
The whole-cube construction in § 2 uses the tridiagonal matrix JH in (20), indexed by Fourier
degree. The constant-weight construction in § 3 uses a tridiagonal matrix indexed by Johnson
degree, with oﬀ-diagonal entries ( 42). In each case, coordinate multiplication connects neigh-
boring degrees. The simplest spherical construction similarly uses a tridiagonal matrix indexed
by harmonic degree, coming from the Gegenbauer recurrence ( 65). Stronger spherical construc-
tions, however, require ambient spaces indexed by several integers, with coordinate transitions
in several independent directions.
This section extends the elementary projection argument to an arbitrary ﬁnite connected
weighted graph. The vertices represent rotation-invariant ambient spaces containing a common
moving subspace, and the edges record the action of the distance coordinate. The concrete
spherical ambient and stabilizer spaces are introduced in § 5; their explicit coordinate-transition
weights are computed in § 6.
4.1. The general projection bound. We ﬁrst isolate the projection argument that underlies
both the concrete whole-cube calculation and the more general spherical construction. The
only inputs are moving orthogonal projections and an isometry compatible with the distance
coordinate.
Proposition 4.1. LetX be a set, and associate a unit vector ℓx in a Euclidean space W with
every x∈X. Write t(x,y ) =⟨ℓx,ℓ y⟩, let V be a D-dimensional Hilbert space, and let Px be a
rank-d orthogonal projection on V for every x∈X, where 1≤d≤D. Suppose an isometry
B :V→W⊗Vsatisﬁes, for some Λ≥0, every x∈X, and every u∈imPx,
B∗(ℓx⊗u) =
√
Λu. (49)
If Λ>s , every code C⊆X satisfying t(x,y )≤s at distinct code points obeys
|C|≤1−s
Λ−s
D
d. (50)
46
===== PAGE 49 =====
Proof. It suﬃces to consider ﬁnite codes: an inﬁnite code would contain ﬁnite subcodes of
arbitrarily large cardinality. The projection overlap satisﬁes
K(x,y ) = tr(PxPy) =∥PxPy∥2
HS≥0.
Deﬁne the residual map
Θx = (ℓx⊗id)Px−
√
ΛBPx.
The same Hilbert–Schmidt calculation as in ( 25), usingB∗B = id V and ( 49), gives
⟨Θx, Θy⟩HS = (t(x,y )−Λ)K(x,y ),
(t(x,y )−s)K(x,y ) = (Λ−s)K(x,y ) +⟨Θx, Θy⟩HS. (51)
The left side is nonpositive at distinct code points and equals (1−s)d on the diagonal. Summing
overC2, discarding the nonnegative Gram term, and applying trace Cauchy–Schwarz give
(Λ−s)|C|2d2
D ≤(Λ−s)

∑
x∈C
Px

2
HS
≤|C|(1−s)d.
Rearrangement proves ( 50). □
We now apply Proposition 4.1 to moving subspaces on the sphere. The rotation group and
the subgroup ﬁxing a base point determine which subspaces can be assembled into a projection.
Let n≥3, let X = Sn− 1, and let G =SO(n) be its rotation group. Give W = Rn the usual
rotation action. For x∈X, the unit distance-coordinate vector is ℓx = x, so t(x,y ) = ⟨x,y⟩.
Fix a base point o, and write H for the rotations ﬁxing o. The action of H on o⊥ identiﬁesH
with SO(n−1).
We call an H-representation a stabilizer representation because H = Stab SO(n)(o) is the
subgroup ﬁxing the base point o. All representations below are ﬁnite-dimensional real Hilbert
spaces with orthogonal group actions. For example, H acts trivially on the ﬁxed line Ro, acts by
ordinary rotations on o⊥ , and acts on the degree- k harmonic polynomials Hk(o⊥ ) by rotating
their input vectors. These examples have dimensions 1, n−1, and dimHk(o⊥ ), respectively.
Choose a d-dimensional irreducible stabilizer representation E, and let Ω be a ﬁnite collection
of pairwise inequivalent irreducible ambient G-representationsVλ. We require the restriction of
eachVλ to H to contain exactly one copy of E:
dimR HomH (E,V λ) = 1, D λ = dimVλ.
The one-dimensional intertwiner space determines a unique copy of E in eachVλ. Identify E with
its copy in one ﬁxed ambient representation, and choose isometric embeddings φλ,o :E→Vλ at
the base point. Composing any H-equivariant endomorphism of E with φλ,o produces another
intertwiner. Hence the one-dimensional intertwiner hypothesis also gives EndH (E) = RidE. If
x =go, transport the stabilizer space and all its embeddings simultaneously:
Ex =gE, φ λ,x(gY ) = gφλ,oY (Y ∈E).
These deﬁnitions are independent of the rotation carrying o to x: two such rotations diﬀer by
an element of H, and every φλ,o commutes with H. In particular, a single rotation transports
all embeddings, so their relative signs are preserved.
4.2. Coordinate transitions and their balanced graph. We next deﬁne the spherical tran-
sition graph and its weights. The vertices are the ambient spaces Vλ. If Vν occurs inside W⊗Vλ,
its inclusion gives a possible coordinate transition from λ to ν. Choose an isometric map com-
muting with rotations:
Cλ,ν :Vν−→W⊗Vλ.
For ﬁxed λ, the images associated with distinct ν are orthogonal because they are inequivalent
irreducible subrepresentations of W⊗Vλ. Contracting with the coordinate vector ℓx gives a map
between the two copies of Ex. Since these copies occur with multiplicity one, EndH (E) = RidE,
and the map commutes with the rotations ﬁxing x, it acts by a real scalar cλ,ν:
C∗
λ,ν(ℓx⊗φλ,xY ) = cλ,νφν,xY. (52)
47
===== PAGE 50 =====
Choose the sign of each coordinate map so that cλ,ν ≥0, and write pλ,ν = c2
λ,ν. The graph
retains an edge only when this coeﬃcient is nonzero. Set pλ,ν = 0 when no such inclusion exists
or its contraction coeﬃcient vanishes. Thus occurrence in the tensor product allows a transition,
but the chosen stabilizer representation determines whether its edge is present. Opposite direc-
tions generally have diﬀerent squared coeﬃcients. We require the following dimension-weighted
reciprocity:
Dλpλ,ν =Dνpν,λ. (53)
Thus multiplying each directed weight by the dimension of the source representation makes the
two directions agree. For the spherical transitions, this identity is veriﬁed explicitly in ( 76) and
§A.2. The undirected weighted adjacency matrix J therefore has symmetric edge weights
Jλ,ν =pλ,ν
√
Dλ
Dν
=√pλ,νpν,λ. (54)
Indeed, if T = (pλ,ν) and D = diag(Dλ), dimension balance ( 53) gives the symmetric similarity
transform
J = D1/2TD− 1/2. (55)
Assume that the ﬁnite graph on Ω is connected and has positive edge weights. The Perron–
Frobenius theorem supplies a strictly positive eigenvector of the weighted adjacency matrix J
for the largest eigenvalue Λ = λmax(J).
Theorem 4.2. Let n≥3, let G = SO(n), and let H = Stab G(o)≃SO(n−1) for a base
point o∈Sn− 1. Let E be a d-dimensional irreducible real H-representation, and let Ω consist
of ﬁnitely many pairwise inequivalent irreducible real G-representations Vλ whose coordinate-
transition graph is connected. Suppose dimR HomH (E,V λ) = 1 for each λ∈Ω, and suppose the
coordinate-transition coeﬃcients satisfy (52) and (53). Let J be the weighted adjacency matrix
in (54), and put Λ = λmax(J) and Dλ = dimVλ. If −1<s< 1 and Λ> max{s, 0}, then
A(n,s )≤1−s
d(Λ−s)
∑
λ∈Ω
Dλ. (56)
Proof. Let v be the positive unit Perron eigenvector of J in ( 54), and put wλ =√Dλvλ and
Z = ∑
λwλ. The dimension-weighted reciprocity ( 53) and the eigenvector identity Jv = Λv
give ∑
λ∈Ω
pλ,νwλ =
√
Dν
∑
λ∈Ω
Jν,λvλ = Λwν. (57)
Consequently,pλ,νwλ/(Λwν) sums to one over λ∈Ω for each ﬁxed ν. These Perron-normalized
weights form the probability distributions used in the coordinate isometry below. Thus
ΨxY =
⨁
λ∈Ω
√wλ
Z φλ,xY
is an isometric embedding into V =⨁
λ∈ΩVλ. Set Px = Ψ xΨ∗
x. For h =⨁
ν∈Ωhν∈V, deﬁne
B :V→W⊗Vby
Bh =
⨁
λ∈Ω
∑
ν∈Ω
pλ,ν >0
√pλ,νwλ
Λwν
Cλ,νhν. (58)
Orthogonality of the images of Cλ,ν and ( 57) give
∥Bh∥2 =
∑
ν∈Ω
∥hν∥2
Λwν
∑
λ∈Ω
pλ,νwλ =∥h∥2,
soB is an isometry. Using ( 52) and then ( 57) gives
B∗(ℓx⊗ΨxY ) =
⨁
ν∈Ω
φν,xY√ΛwνZ
∑
λ∈Ω
pλ,νwλ =
⨁
ν∈Ω
√
Λwν
Z φν,xY =
√
Λ ΨxY.
48
===== PAGE 51 =====
Proposition 4.1 , with D =∑
λDλ, proves ( 56). Finally, deﬁne F (x,y ) = (⟨x,y⟩−s) tr(PxPy).
Rotational invariance makes tr(PxPy) a function of ⟨x,y⟩alone. The residual Gram decomposi-
tion (51) makes F positive deﬁnite, and F (x,y )≤0 when⟨x,y⟩≤s. If σ is uniform probability
measure on the sphere, its constant coeﬃcient satisﬁes
f0 =
∫∫
F (x,y )dσ(x)dσ(y)≥(Λ−s)

∫
Pxdσ(x)

2
HS
≥(Λ−s) d2
∑
λ∈ΩDλ
> 0.
ThusF satisﬁes every requirement of a two-point Delsarte certiﬁcate. □
The full coordinate decomposition can also contain edges leading to ambient spaces outside
the selected vertex set Ω. A ﬁnite truncation discards those edges, so the retained transition
weights need not sum to one. This causes no diﬃculty: ( 57) normalizes the Perron-reweighted
coeﬃcients in ( 58), making that operator an isometry. Thus Theorem 4.2 applies to arbitrary
ﬁnite connected truncations, including multidimensional rectangular boxes.
5. Spherical harmonics and stabilizer representations
To apply the moving-subspace bound of Theorem 4.2 to spherical codes, we need a family of
SO(n)-representations, each containing the same representation of the point stabilizer SO(n−1).
We must also identify the coordinate transitions between the ambient representations and the
dimensions of their moving subspaces. This section describes the relevant representations and
works out the one-dimensional construction. The general transition weights are computed in
§6, and their spectral and dimension asymptotics are analyzed in § 7.
Throughout the spherical arguments, assume n≥3. The multi-row construction will impose
the stronger stable-range condition n≥2r + 4. This restriction does not aﬀect the asymptotic
bounds: every hierarchy level r is ﬁxed before n→∞.
The group SO(n) acts transitively on Sn− 1. For a point x, the rotations ﬁxing x act on its
orthogonal complement
x⊥ ={u∈Rn :⟨u,x⟩= 0},
and every rotation of x⊥ extends uniquely to a rotation ﬁxing x. Hence the point stabilizer of
x is naturally identiﬁed with SO(n−1). We call a representation of this point-ﬁxing subgroup
a stabilizer representation. The ﬁxed line Rx, on which every such rotation acts trivially, is the
one-dimensional example; the tangent space x⊥ , on which the same rotations act in the usual
way, is a higher-dimensional example. A rotation carrying x to another point y also carries the
tangent space x⊥ to y⊥ . Thus the stabilizer representations used below move naturally with
the code point.
We ﬁrst recall the classical construction, which retains the one-dimensional stabilizer-ﬁxed
line in each selected space of spherical harmonics. We next replace this line by a space of
degree-k harmonics on x⊥ , obtaining a weighted one-dimensional path. Finally, more general
stabilizer representations yield multidimensional transition graphs and the full hierarchy.
5.1. Spherical harmonics and the classical bound. Classical spherical linear programming
uses harmonic spaces, their stabilizer-ﬁxed lines, and the associated Gegenbauer kernels. The
resulting tridiagonal spectral construction uses one ﬁxed line in each harmonic degree, just as
the classical whole-cube construction uses one ﬁxed line in each Fourier degree in § 2.1.
Equip Sn− 1 with rotation-invariant probability measure. A polynomial on Rn is homoge-
neous of degree m when scaling its argument by c scales its value by cm, and it is harmonic
when its Euclidean Laplacian vanishes. Let V S
m =Hm(Rn) denote the restrictions of these
homogeneous harmonic polynomials to Sn− 1. Rotations act on V S
m by changing the input of a
polynomial. These mutually orthogonal irreducible spaces are the spherical analogues of Fourier
levels [ GW09, §§8.1.1–8.1.2]. For example, V S
0 consists of constant functions, and V S
1 consists
of the linear functions u↦→⟨v,u⟩. The integer m records polynomial degree, not the dimension
of the harmonic space. That dimension is
DS
m = dimV S
m = 2m +n−2
n−2
(
m +n−3
m
)
. (59)
49
===== PAGE 52 =====
Fix x ∈Sn− 1. A function invariant under all rotations ﬁxing x depends only on its ra-
dial coordinate t =⟨x,u⟩. Inside each V S
m, the invariant functions form a one-dimensional
subspace, called the stabilizer-ﬁxed line. Its generator normalized by Pm(1) = 1 is Pm(t) =
C(n− 2)/2
m (t)/C(n− 2)/2
m (1), where Cη
m denotes the degree- m Gegenbauer polynomial. For an or-
thonormal basis Ym,1,...,Y m,DSm of V S
m, deﬁne its reproducing kernel by
KS
m(u,v ) =
DS
m∑
a=1
Ym,a(u)Ym,a(v).
This kernel is independent of the chosen orthonormal basis. The spherical addition formula
identiﬁes it explicitly [ BV08, (4)]:
KS
m(u,v ) = DS
mPm(⟨u,v⟩). (60)
The deﬁning orthonormal-basis sum is positive deﬁnite. Therefore, so is Pm(⟨u,v⟩), and non-
negative Gegenbauer coeﬃcients suﬃce for positive deﬁniteness. (The converse is Schoenberg’s
theorem [ S42] and is not needed here.) Thus, if f = ∑M
m=0fmPm is a polynomial, f0 > 0,
fm≥0, and f (t)≤0 for−1≤t≤s, the spherical linear-programming bound is [ DGS77]
A(n,s )≤f (1)
f0
.
Just as in the Fourier-path construction of § 2.1, the trivial stabilizer representation in V S
m is
therefore the line spanned by Pm(⟨x,·⟩). The Gegenbauer recurrence ( 64) shows that multipli-
cation by u↦→⟨x,u⟩connects this line only to the ﬁxed lines of degrees m−1 andm + 1. Thus
consecutive harmonic degrees form a weighted path, whose tridiagonal matrix gives the classi-
cal spectral certiﬁcate [ BN06, §3.3]. The explicit zonal polynomials identify the classical ﬁxed
lines. The addition formula ( 60) also normalizes the coordinate maps in Lemma 5.1; apart from
this normalization, the new construction uses the harmonic spaces and normalized recurrence
(65)–(66). Lemma 5.2 below calculates the largest-eigenvalue limit of this path; its case k = 0
recovers the direct whole-sphere Kabatianskii–Levenshtein spectral bound [ KL78], before the
additional spherical-cap optimization.
5.2. Harmonics on the tangent sphere. The classical construction associates one stabilizer-
ﬁxed vector with each selected harmonic degree. We replace that vector with a common space Ex
of harmonic polynomials on x⊥ , embedded inside several ambient harmonic spaces V S
i . Consec-
utive ambient degrees are connected by a symmetric tridiagonal matrix, as in the Fourier-degree
construction of § 2. The projection bound Proposition 4.1 then divides by dimEx rather than
by the classical rank 1. For positive harmonic degree, assume n≥4, so the stabilizer represen-
tations used below have real-scalar endomorphisms. We now describe Ex, its embeddings φi,x,
the weighted adjacency matrix Jk,L, and the resulting spherical-code bound.
For a base point x, the unit sphere in its tangent space is
S(x⊥ ) = x⊥∩Sn− 1.
Equip this sphere with its rotation-invariant probability measure. The stabilizer SO(n−1) acts
on it by rotating its tangent directions. For k≥0, let
Ex =Hk(x⊥ ), d S
k = dimEx =
(
n +k−2
k
)
−
(
n +k−4
k−2
)
. (61)
Here and below, a binomial coeﬃcient with negative lower index is zero. Thus Ex consists
of degree-k homogeneous harmonic polynomials on x⊥ , restricted to S(x⊥ ). Equivalently, its
elements are symmetric traceless k-tensors on x⊥ : a symmetric tensor T represents the poly-
nomial ξ↦→T (ξ,...,ξ ), and harmonicity means that contracting any two tensor indices gives
zero. In particular, k is the polynomial degree or tensor order; it is not the dimension dS
k, which
is generally much larger. For k = 0 , Ex is the classical one-dimensional space of constants; for
k = 1 , it is naturally identiﬁed with x⊥ ; and for k = 2 , it consists of traceless quadratic forms
on x⊥ .
50
===== PAGE 53 =====
The tangent harmonic spaces Ex = Hk(x⊥ ) also appear in the matrix-valued kernels of
Bachoc and Vallentin [ BV08, (9), Thms. 3.1–3.2]. There the stabilizer ﬁxes one distinguished
base point, producing kernels in three inner products. Here Ex moves with the code point, and
the overlap of the corresponding moving projections remains a scalar two-point kernel.
To see which ambient harmonic spaces contain Ex, restrict their rotation action from SO(n)
to the subgroup ﬁxing x. The multiplicity-free orthogonal-group branching rule gives [ GW09,
Thms. 8.1.3–8.1.4]
V S
i ↓SO(n− 1)≃
i⨁
k=0
Hk(x⊥ ). (62)
Every summand occurs with multiplicity one, meaning that V S
i contains exactly one subspace
of each indicated harmonic type. In particular, it contains one copy of Ex if i≥k, and none if
i<k . Write φi,x :Ex→V S
i for the isometric embedding of this unique copy.
Everyu∈Sn− 1 away from the poles u =±x has the unique decomposition
u =tx +
√
1−t2ξ, t =⟨x,u⟩, ξ ∈S(x⊥ ).
In these coordinates, every element of the copy of Ex inside V S
i separates into a tangential
harmonic Y of degree k and a radial polynomial of degree i−k:
(φi,xY )(u) = pi− k(t)(1−t2)k/2Y (ξ), (63)
where Y ∈Ex and the radial polynomial pi− k is a scalar multiple of Ck+(n− 2)/2
i− k [BV08, (8),
proof of Thm. 3.2]. Choose this scalar multiple to have positive leading coeﬃcient and to make
φi,x an isometry. These choices ﬁx the signs of all the embeddings, and the expression extends
continuously over the poles. Multiplication by the base-point coordinate t =⟨x,u⟩preserves
the tangential harmonic Y and acts only on its radial polynomial. Set η =k + (n−2)/2. The
standard Gegenbauer identity [ BN06, §3.3]
2(j +η)tCη
j (t) = (j + 1)Cη
j+1(t) + (j + 2η−1)Cη
j− 1(t) (64)
with j = i−k, where Cη
− 1 = 0 , shows that only degrees i + 1 and i−1 occur. Applying the
isometric normalization in ( 63) gives
tφi,x =α(k)
i φi+1,x +β(k)
i φi− 1,x, (65)
with
(
α(k)
i
)2 = (i−k + 1)(i +k +n−2)
(2i +n−2)(2i +n) ,
(
β(k)
i
)2 = (i−k)(i +k +n−3)
(2i +n−4)(2i +n−2). (66)
The recurrence ( 65) describes scalar multiplication by u↦→⟨x,u⟩. To apply the projection
bound Theorem 4.2 , we must instead normalize the vector-valued coordinate maps between
neighboring harmonic degrees. The required normalization is determined by the classical ﬁxed-
line coeﬃcient α(0)
i in ( 66).
Lemma 5.1. Leti≥k, abbreviate Dj =DS
j , and let Πj be the orthogonal projection onto V S
j .
Deﬁne the upward and downward coordinate-multiplication maps by
M ↑
i : Rn⊗V S
i −→V S
i+1, M ↑
i (v⊗f ) = Π i+1
[
⟨v,·⟩f
]
,
M ↓
i : Rn⊗V S
i+1−→V S
i , M ↓
i (v⊗g) = Π i
[
⟨v,·⟩g
]
.
These maps satisfy
M ↑
i (M ↑
i )∗ =m↑
i idV S
i+1
, M ↓
i (M ↓
i )∗ =m↓
i idV S
i
,
where the normalization constants are
m↑
i =α(0)
i
√
Di
Di+1
= i + 1
2i +n, m ↓
i =α(0)
i
√
Di+1
Di
= i +n−2
2i +n−2. (67)
51
===== PAGE 54 =====
Consequently, the coordinate inclusions
C↑
i = (M ↑
i )∗
√
m↑
i
:V S
i+1−→Rn⊗V S
i ,
C↓
i = (M ↓
i )∗
√
m↓
i
:V S
i −→Rn⊗V S
i+1
are isometries, and their contractions onto the tangent-harmonic copies satisfy
(C↑
i )∗(
x⊗φi,xY
)
= α(k)
i√
m↑
i
φi+1,xY,
(C↓
i )∗(
x⊗φi+1,xY
)
= α(k)
i√
m↓
i
φi,xY.
The resulting symmetric edge weight is
Ji,i+1 = (α(k)
i )2
α(0)
i
. (68)
Proof. The addition formula ( 60) identiﬁes the reproducing kernel Kj =KS
j ofV S
j asKj(u,v ) =
DjPj(⟨u,v⟩). Thus its unit stabilizer-ﬁxed vector at x is zj,x = Kj(x,·)/
√
Dj. Write tx(u) =
⟨x,u⟩. Expanding the Hilbert–Schmidt norm in orthonormal bases and using rotation invariance
gives
∥M ↑
i∥2
HS =
∫∫
(Sn−1)2
⟨u,v⟩Ki(u,v )Ki+1(u,v )dσ(u)dσ(v)
=
√
DiDi+1⟨txzi,x,z i+1,x⟩=α(0)
i
√
DiDi+1.
The ﬁnal equality is the recurrence ( 65) for k = 0 . For every standard basis vector er∈Rn,
self-adjointness of coordinate multiplication gives
⟨M ↑
i (er⊗f ),g⟩=⟨f,M ↓
i (er⊗g)⟩.
Summing over r shows that the two coordinate maps have the same Hilbert–Schmidt norm.
Moreover,M ↑
i (M ↑
i )∗ andM ↓
i (M ↓
i )∗ commute with rotations. Since their target harmonic spaces
are irreducible, they are scalar operators. Taking traces identiﬁes their respective scalar factors
as α(0)
i
√
Di/Di+1 and α(0)
i
√
Di+1/Di. Substituting ( 59) and ( 66) with k = 0 yields ( 67). The
stated contractions follow directly from ( 65); in the downward direction, β(k)
i+1 = α(k)
i . Their
squared coeﬃcients and dimension-weighted reciprocity satisfy
pi,i+1 = (α(k)
i )2
m↑
i
, p i+1,i = (α(k)
i )2
m↓
i
, D ipi,i+1 =Di+1pi+1,i. (69)
Since m↑
im↓
i = (α(0)
i )2, the symmetric edge weight √pi,i+1pi+1,i is ( 68). □
Fix k<L , and retain the unique copy of Ex in each of V S
k,...,V S
L . The resulting transition
graph is the one-dimensional path
V S
k ←→V S
k+1←→···←→V S
L. (70)
The vertices record ambient harmonic degree; they do not record dimensions of subspaces.
Substituting ( 66) into ( 68) gives the symmetric weight of the edge V S
i ↔V S
i+1:
c(k)
i = (i−k + 1)(i +k +n−2)√
(i + 1)(i +n−2)(2i +n−2)(2i +n). (71)
Let Jk,L be the weighted adjacency matrix of the harmonic-degree path: its diagonal entries
vanish and its (i,i + 1) entry is c(k)
i . Write λk,L =λmax(Jk,L). The positive Perron eigenvector
52
===== PAGE 55 =====
of Jk,L, as in Theorem 4.2 , speciﬁes how to combine the copies of Ex into a single rank- dS
k
projection inside V S
k ⊕···⊕V S
L . Theorem 4.2 therefore gives
A(n,s )≤ 1−s
dS
k(λk,L−s)
L∑
i=k
DS
i if λk,L >s.
Here∑L
i=kDS
i is the dimension of the ambient direct sum, while dS
k, given in ( 61), is the rank of
the moving projection. For k = 0, this rank is 1, recovering the classical ﬁxed-line construction.
Whenk grows proportionally to n,dS
k grows exponentially and its logarithm is subtracted from
the code exponent. This gain over the classical ﬁxed-line construction comes from a scalar
two-point Delsarte certiﬁcate, even though the moving subspaces have dimension greater than
one.
The next lemma identiﬁes the spectral limit of this one-dimensional harmonic-degree path,
including the classical Kabatianskii–Levenshtein case k = 0.
Lemma 5.2. Fix 0≤b<a , and suppose k/n→b and L/n→a. Then
λk,L−→2Γrow(a,b ) = 2(a−b)(1 +a +b)
(1 + 2a)
√
a(1 +a).
Proof. Uniformly for i/n in a compact subinterval of (0,∞), the edge weight ( 71) converges to
Γrow(u,b ) = u(u + 1)−b(b + 1)
(1 + 2u)
√
u(u + 1).
This function increases on u≥b: its ﬁrst summand
√
u(u + 1)/(1 + 2u) increases, while b(b +
1)/((1+2u)
√
u(u + 1)) decreases. If b> 0, this convergence is uniform over the entire harmonic-
degree path, so its largest edge weight converges to Γrow(a,b ). If b = 0 , the same conclusion
follows by ﬁrst restricting to i≥εn. The omitted edges satisfy
0≤c(k)
i ≤c(0)
i =
√
(i + 1)(i +n−2)
(2i +n−2)(2i +n)≤
√
i + 1
n−2,
because (i−k + 1)(i +k +n−2) = ( i + 1)(i +n−2)−k(k +n−3). Letting ε↓0 proves
the claim at b = 0 as well. The maximum row sum therefore gives lim supλk,L≤2Γrow(a,b ).
For mn→∞with mn = o(n), the edge weights on the last mn vertices converge uniformly
to Γrow(a,b ). Applying ( 26) to the ﬁrst discrete sine vector on that terminal path gives the
matching lower bound. □
When b = 0 , the limiting eigenvalue is 2q(a), and the classical feasibility boundary 2q(a) =
s gives a = a0(s) from the introduction and the direct whole-sphere exponent Hsph(a0(s)).
Applying the additional spherical-cap optimization gives instead the classical exponent BKL(s)
in ( 10). Positive b gives the tangent-harmonic spectral quantity in ( 11).
The harmonic-degree path ( 70) uses only ambient spaces of scalar spherical harmonics. Scalar
multiplication by the base-point coordinate connects just the neighboring degrees i−1 andi + 1,
as in ( 65). The moving-subspace construction also allows other ambient representations, how-
ever: its rotation-equivariant coordinate maps take values in Rn⊗V S
i , followed by contraction
with the base-point coordinate as in ( 52). This vector-valued tensor product contains one more
irreducible representation besides the two neighboring harmonic spaces.
For integersi≥j≥0, let V(i,j) denote the irreducible orthogonal-group tensor representation
whose Young diagram has two rows of lengths i and j; its precise highest-weight description is
given in § 5.3. A zero second row gives V(i,0) = V S
i . For i≥1 and n≥6, tensoring with the
standard representation Rn gives [ Kra18, (B.2)]
Rn⊗V(i,0)≃V(i+1,0)⊕V(i− 1,0)⊕V(i,1).
The ﬁrst two summands correspond to the neighboring harmonic degrees already present in ( 65).
The third, V(i,1), has row lengths i and 1; it is an ambient tensor representation rather than a
space of scalar functions on the sphere. For i≥k≥1, the restriction of V(i,1) still contains the
53
===== PAGE 56 =====
stabilizer representation Ex. Allowing all the additional spaces V(i,j) containing Ex gives the
vertex set
{(i,j ) : i≥k≥j≥0}.
The graph on vertices (i,j ) now has edges changing either i or j; the harmonic-degree path is
the boundary j = 0. The positive Perron eigenvector of the two-dimensional weighted adjacency
matrix again assembles a moving projection of rank dS
k. Since SO(n) is transitive on ordered
pairs with a prescribed inner product, the overlap of two such projections depends only on ⟨x,y⟩.
Consequently, the enlarged graph still produces a scalar two-point Delsarte certiﬁcate.
5.3. The multi-row hierarchy . The degree-k tangent-harmonic subspace consists of symmet-
ric tracelessk-tensors onx⊥ . This subspace supports both the one-dimensional harmonic-degree
path and its enlargement to the two-dimensional graph on (i,j ). Higher-dimensional transition
graphs arise by allowing more general orthogonal-group tensor representations.
Fix a hierarchy level r≥0 and assume n≥2r + 4. Since r remains ﬁxed as n→∞, this di-
mension restriction is automatic. The irreducible orthogonal-group tensor representations used
here correspond to Young diagrams: arrays of boxes whose row lengths form a weakly decreas-
ing sequence of nonnegative integers. This sequence, completed by zero entries as necessary,
is the dominant highest weight of the representation. For example, the one-row diagram (k)
corresponds to symmetric traceless k-tensors; additional rows describe other tensor symmetries.
We use ambient SO(n)-representations corresponding to Young diagrams with at most r + 1
rows and stabilizer SO(n−1)-representations corresponding to diagrams with at most r rows.
Under n≥2r + 4, their remaining highest-weight coordinates vanish, so none reaches the ﬁnal
available orthogonal-group weight coordinate. This avoids the exceptional splitting that can
occur outside the stable range. The hierarchy level counts these rows, not the dimension of a
representation or the number of graph vertices.
Fix an irreducible SO(n−1)-representationEµ with highest weight
µ = (µ1,...,µ r, 0,... ), µ 1≥···≥µr≥0.
Thusr bounds the number of nonzero stabilizer rows. An ambient representation Vλ of SO(n)
has highest weight
λ = (λ1,...,λ r+1, 0,... ), λ 1≥···≥λr+1≥0.
The orthogonal-group branching rule [ GW09, Thms. 8.1.3–8.1.4] says that restricting Vλ from
SO(n) toSO(n−1) containsEµ exactly when every stabilizer row length lies between the two
adjacent ambient row lengths:
λ1≥µ1≥λ2≥···≥µr≥λr+1≥0. (72)
The harmonic decomposition ( 62) is its specialization to one-row ambient representations. Every
such copy occurs with multiplicity one. Thus, after choosing µ, the interlacing inequalities
identify the ambient representations that contain the selected stabilizer type. These ambient
weights λ will be the vertices of the transition graph. The stabilizer weight µ remains ﬁxed
throughout that graph: only λ varies from vertex to vertex. When taking the high-dimensional
limit, the initial choice of µ may depend on n, but it is still ﬁxed within each individual graph.
The standardSO(n) representation Rn has highest weight (1, 0,..., 0). Tensoring Vλ with Rn
adds or removes one box from its Young diagram, and hence increases or decreases a single row
length by one [ Kra18, (B.2)]. In odd dimensions, a potential unchanged-weight term is absent
under the zero-tail assumption, as explained in § A.2. The transition graph therefore joins λ to
λ±eℓ, where eℓ is the ℓth coordinate vector, provided the resulting row lengths remain weakly
decreasing and satisfy ( 72) for the same ﬁxed µ. Thus the graph is the nearest-neighbor lattice
graph on the ambient weights inside the interlacing region. When r = 0 , it is the classical
one-dimensional path of spherical harmonic degrees. When µ = (k), it is the two-dimensional
region i≥k≥j≥0. Generally, r stabilizer rows permit r + 1 ambient coordinates and hence
an (r + 1)-dimensional transition graph.
The representation-theoretic inputs are the orthogonal-group branching condition ( 72) and
Weyl’s dimension formula ( 111) [ GW09, §7.1.2 and §§8.1.1–8.1.2], together with the explicit
54
===== PAGE 57 =====
coordinate-multiplication coeﬃcients in Kravchuk’s conventions [ Kra18, §§2.1–2.3 and App. B].
Kravchuk’s Spin(n) formulas apply unchanged to integral tensor representations of SO(n). § A.2,
speciﬁcally ( 109) and ( 110), reduces the odd- and even-dimensional formulas to the common
transition weights used below. § A.3 records the dimensions of Vλ and Eµ in ( 111) and their
uniform exponential rates in Lemma A.1 .
6. The spherical transition graph
§5.3 described which ambient representations Vλ contain a chosen stabilizer representation
Eµ and which pairs of ambient representations are connected by coordinate multiplication. To
obtain a spherical-code bound, we must determine the strength of each coordinate transition.
We ﬁrst give the directed squared coeﬃcients, then combine opposite directions into a symmetric
weighted adjacency matrix JΩ. The largest eigenvalue of JΩ and the dimensions of Vλ and Eµ
determine the ﬁnite-dimensional projection bound in Theorem 4.2 .
Fix r≥0 and n≥2r + 4. Choose a stabilizer representation Eµ with highest weight µ =
(µ1,...,µ r, 0,... ). The highest weights λ = (λ1,...,λ r+1, 0,... ) of the ambient representations
containingEµ satisfy ( 72), and each ambient representation contains exactly one copy of Eµ.
Coordinate multiplication can increase or decrease one row length λℓ. The resulting coeﬃ-
cients take a uniform form in odd and even dimensions after adding the standard orthogonal-
group oﬀsets to the row lengths. For 1≤ℓ≤r + 1 and 1≤m≤r, set
ˆλℓ =λℓ + n
2−ℓ, ˆµm =µm + n−1
2 −m, ρ n,r = n
2−r−1. (73)
Writeeℓ for the ℓth coordinate vector. The scalar cℓ,± (λ;µ) describes multiplication by the base-
point coordinate between the copies of Eµ inVλ andVλ± eℓ, in the sense of ( 52). Deﬁne its squared
magnitude by pℓ,± (λ;µ) =|cℓ,± (λ;µ)|2. If the target row lengths are not weakly decreasing or
fail ( 72), there is no target representation containing Eµ, and its transition coeﬃcient is zero.
On the full graph of ambient weights containing the ﬁxed stabilizer representation Eµ, these
squared coeﬃcients sum to one at each vertex, as in ( 75). They may therefore be viewed as
transition probabilities on that full graph, but this probabilistic interpretation is not needed
for the code bound. Indeed, the construction retains a ﬁnite vertex set Ω and omits every edge
leaving Ω, so the remaining coeﬃcients generally sum to less than one. What the construction
uses is the dimension-weighted reciprocity ( 76), which extends ( 69) and allows the ﬁnite directed
transition matrix to be symmetrized. The positive Perron eigenvector of the resulting symmetric
weighted adjacency matrix is then reweighted as in ( 57) to produce the moving projections.
Proposition 6.1. Fix r ≥0, n≥2r + 4 , and ambient and stabilizer highest weights λ,µ
satisfying (72). If 1≤ℓ≤r + 1 andλ±eℓ is a dominant weight still satisfying (72), its directed
squared coordinate coeﬃcient is
pℓ,± (λ;µ) =
(ˆλℓ±ρn,r)
r∏
m=1
(
(ˆλℓ±1
2 )2−ˆµ2
m
)
2ˆλℓ
r+1∏
q=1
q̸=ℓ
(ˆλ2
ℓ−ˆλ2
q)
. (74)
With the zero convention above, the full transition graph satisﬁes
r+1∑
ℓ=1
(
pℓ,+(λ;µ) +pℓ,− (λ;µ)
)
= 1, (75)
and, for every graph edge λ↔λ +eℓ,
dimVλpℓ,+(λ;µ) = dim Vλ+eℓpℓ,− (λ +eℓ;µ). (76)
Proof. The coeﬃcients come from coordinate multiplication between the multiplicity-free sta-
bilizer copies. Kravchuk gives separate odd- and even-dimensional expressions for these coeﬃ-
cients [Kra18, (B.12)–(B.13)]. § A.2 identiﬁes their normalization and records the corresponding
55
===== PAGE 58 =====
squared coeﬃcients in ( 109) and ( 110). In both expressions, factors belonging to zero highest-
weight coordinates cancel, leaving the common formula ( 74). The same appendix also explains
why the apparent odd-dimensional self-loop is absent.
ForY ∈Eµ, the base-point coordinate ℓx is ﬁxed by the stabilizer. Therefore ℓx⊗φλ,xY has
stabilizer type Eµ, and its orthogonal projections onto the ambient irreducible summands have
squared norms pℓ,± (λ;µ)∥Y∥2. Orthogonality of these summands and ∥ℓx∥= 1 give
∥Y∥2 =∥ℓx⊗φλ,xY∥2 =
r+1∑
ℓ=1
(
pℓ,+(λ;µ) +pℓ,− (λ;µ)
)
∥Y∥2,
proving (75) on the full graph. Finally, applying the exact Weyl dimension formula ( 111) to the
two endpoints of an existing edge gives ( 76); the calculation appears at the end of § A.2. □
Now choose a ﬁnite connected set Ω of ambient weights satisfying ( 72), and retain only edges
whose two endpoints belong to Ω. Although the two directed weights on an edge generally diﬀer,
(76) says that each agrees after multiplication by the dimension of its source representation.
Thus ( 55) converts the directed coeﬃcient matrix into a symmetric weighted adjacency matrix
JΩ. The edge weight of JΩ is the geometric mean of the forward and reverse squared coeﬃcients:
Jλ,λ+eℓ =
√
pℓ,+(λ;µ)pℓ,− (λ +eℓ;µ), (77)
with every other entry zero. Write dµ = dimEµ for the rank of the moving projection, Dλ =
dimVλ for each ambient representation dimension, and ΛΩ =λmax(JΩ) for the largest eigenvalue
of the ﬁnite weighted adjacency matrix. Theorem 4.2, applied with G =SO(n),H =SO(n−1),
and W = Rn, produces a scalar positive-deﬁnite kernel depending only on the inner product
and gives the following bound.
Theorem 6.2. Fix−1<s< 1, r≥0, n≥2r + 4, a stabilizer representation Eµ, and a ﬁnite
connected set Ω of ambient weights satisfying (72). If ΛΩ> max{s, 0}, then
A(n,s )≤ 1−s
dµ(ΛΩ−s)
∑
λ∈Ω
Dλ. (78)
6.1. The two-row graph. To make the general graph concrete, return to the degree- k tangent
harmonics Eµ = Hk(x⊥ ), whose stabilizer weight is the single row µ = ( k). An ambient
representation may now have two rows λ = (i,j ). By ( 72), it contains Eµ exactly when i≥k≥
j≥0. Thus the vertices form a two-dimensional region: the one-dimensional harmonic-degree
path is the boundary j = 0, and j >0 supplies the ambient representations omitted from that
boundary. The resulting lattice strip is shown in Figure 2 .
The two possible coordinate directions join (i,j ) to (i±1,j ) or to (i,j±1), respectively, and
(74) gives the four directed squared coeﬃcients
pi,+ = (i−k + 1)(i +k +n−2)(i +n−3)
(i−j + 1)(i +j +n−3)(2i +n−2), p i,− = (i−k)(i +k +n−3)(i + 1)
(i−j + 1)(i +j +n−3)(2i +n−2),
pj,+ = (k−j)(j +k +n−3)(j +n−4)
(i−j + 1)(i +j +n−3)(2j +n−4), pj,− = j(k−j + 1)(j +k +n−4)
(i−j + 1)(i +j +n−3)(2j +n−4).
(79)
The factorsi−k,k−j, andj in (79) make the corresponding transitions vanish at the boundaries
i = k, j = k, and j = 0 , respectively. At j = 0 , pi,+ and pi,− describe the one-dimensional
harmonic-degree path, whereas
pj,+(i, 0) = k(k +n−3)
(i + 1)(i +n−3)
is positive precisely when k > 0. This edge from (i, 0) to (i, 1) is absent from the classical
ﬁxed-line construction. Retaining vertices with j > 0 incorporates such additional edges into
λmax(JΩ) while leaving the stabilizer dimension dS
k unchanged.
56
===== PAGE 59 =====
(I, J )
j
i
0
1
J
k
k k + 1 k + 2 I I + 1
ﬁxed stabilizer weight µ = (k)
one-row subgraph j = 0
Figure 2. The spherical two-row representation graph for a ﬁxed stabilizer
weight µ = (k). Ambient vertices (i,j ) satisfy i≥k≥j≥0; horizontal and
vertical edges change i and j, respectively. Their directed squared weights are
given in ( 79), and ( 77) converts opposite directions into symmetric edge weights.
The blue boundary is the one-row subgraph. The dashed box marks a lattice
region near an upper corner. For any large ﬁxed box size, its edge weights become
asymptotically constant as n→∞, and a product of discrete sine waves bounds
the largest eigenvalue from below. Letting the box size increase gives Lemma 7.2.
The ambient dimension needed in ( 78) is obtained by specializing the exact Weyl formula
(111) in § A.3 to λ = (i,j ):
Di,j = (2i +n−2)(2j +n−4)(i−j + 1)(i +j +n−3)
(n−2)(n−4)(i + 1)(i +n−3)
(
i +n−3
i
)(
j +n−5
j
)
.
The identityDi,jpi,+(i,j ) = Di+1,jpi,− (i+1,j ) and its j-direction analogue give ( 76); restricting
to j = 0 recovers (71).
7. Asymptotic spherical-code bounds
We now evaluate the ﬁnite spherical-code bound ( 78) as the dimension tends to inﬁnity. The
spectral constraint involves ΛΩ =λmax(JΩ), while the exponent in the bound is determined by
∑
λ∈Ω dimVλ
dimEµ
.
We keep the number r of stabilizer rows ﬁxed, let the row lengths of Eµ and Vλ grow propor-
tionally to n, and compute both the spectral constraint and the dimension-ratio exponent from
the limiting coordinates.
Fix r≥0 before taking n→∞. Suppose the ambient and stabilizer row lengths satisfy
λℓ/n→aℓ and µm/n→bm, respectively. We require strict separation between successive
ambient and stabilizer rows, while allowing the ﬁnal ambient row to vanish:
a1>b 1>a 2>···>b r >a r+1≥0. (80)
For r = 0 , this condition means simply a1 ≥0. Two scalar functions describe the limiting
edge weights of JΩ. The quadratic change of variables A(u) = u(1 +u) converts shifted highest-
weight diﬀerences into diﬀerences of nonnegative real numbers. The function q(u) is the limiting
symmetric edge weight in the classical level-zero harmonic path at degree un +o(n). Put
A(u) = u(1 +u), q (u) =
√
u(1 +u)
1 + 2u .
Writexℓ =A(aℓ) and ym =A(bm). Since A is strictly increasing, the interlacing inequalities
(80) give x1 >y 1 >x 2 >···>y r >x r+1≥0. The residues Rℓ associated with the interlacing
57
===== PAGE 60 =====
nodes xℓ,y m, the resulting weighted edge strength Γr, and the ambient-to-stabilizer dimension
exponent Φr are
Rℓ(a, b) =
r∏
m=1
(xℓ−ym)
r+1∏
q=1
q̸=ℓ
(xℓ−xq)
, Γr(a, b) =
r+1∑
ℓ=1
Rℓ(a, b)q(aℓ),
Φr(a, b) =
r+1∑
ℓ=1
Hsph(aℓ)−
r∑
m=1
Hsph(bm).
(81)
The Rℓ are the residues of ∏
m(z−ym)/∏
ℓ(z−xℓ). The strict interlacing in ( 80) makes every
residue positive, and comparison at z =∞gives∑r+1
ℓ=1Rℓ = 1. The next subsection constructs
ﬁnite weighted adjacency matrices JΩn satisfyingλmax(JΩn)≥2Γr +o(1). The same subsection
shows that the normalized logarithm of the dimension ratio in ( 78) converges to Φr.
7.1. Spectral and dimension asymptotics. The spectral estimate is local, even though
transition weights vary across the full ambient-weight graph. Keep the stabilizer weight µ ﬁxed
and consider a lattice box of side mn near an ambient weight λ∗
n, where mn→∞, mn =o(n),
and λ∗
n/n→a. Every vertex of this box has the same limiting normalized ambient weight a.
Consequently, the edge weights freeze to constants depending only on their coordinate direction:
wℓ =Rℓ(a, b)q(aℓ), (Jlocf )(v) =
∑
ℓ
wℓ
(
f (v +eℓ) +f (v−eℓ)
)
.
Here f is zero outside the box. Thus 2∑
ℓwℓI−Jloc is the usual weighted Dirichlet lattice
Laplacian, whose ﬁrst eigenvector is a product of discrete sine vectors.
We ﬁrst calculate the limiting edge weights in Lemma 7.1 ; the local sine test function then
yields the eigenvalue lower bound in Lemma 7.2 . Finally, Lemma A.1 in § A.3 determines the
exponential ratio of ambient to stabilizer dimensions.
Lemma 7.1. Fix r≥0. Suppose (80) holds, λℓ/n→aℓ, and µm/n→bm. For every existing
coordinate transition,
pℓ,± (λ;µ)−→Rℓ(2aℓ + 1±1)
2(1 + 2aℓ) . (82)
Consequently,
Jλ,λ+eℓ−→Rℓq(aℓ). (83)
Both limits hold uniformly whenever
max
ℓ
⏐⏐⏐⏐
λℓ
n −aℓ
⏐⏐⏐⏐+ max
1≤ m≤ r
⏐⏐⏐⏐
µm
n −bm
⏐⏐⏐⏐=o(1).
The second maximum is understood as zero when r = 0.
Proof. Substitute ( 73) into ( 74) and use (u + 1
2 )2−(v + 1
2 )2 =A(u)−A(v). The quadratic and
linear factors give ( 82); the balanced geometric mean of the forward and reverse coeﬃcients
gives ( 83). The strict interlacing in ( 80) keeps all limiting denominator diﬀerences nonzero,
so the rational formulas converge uniformly on shrinking neighborhoods of the prescribed row
lengths. □
Choose integral stabilizer row lengths µm = bmn +o(n) and upper ambient row lengths
Nℓ,n = aℓn +o(n), taking Nr+1,n = 0 if ar+1 = 0 . Let Ωn consist of the ambient weights
satisfying the interlacing inequalities ( 72) and
µℓ≤λℓ≤Nℓ,n (1≤ℓ≤r), 0≤λr+1≤Nr+1,n.
Its upper corner is λ∗
n = (N1,n,...,N r+1,n).
Lemma 7.2. The weighted adjacency matrix of the ﬁnite ambient-weight set Ωn satisﬁes
lim infn→∞ λmax(JΩn)≥2Γr(a, b). (84)
58
===== PAGE 61 =====
Proof. Choose mn→∞with mn = o(n). Strict interlacing allows every positive coordinate
of λ∗
n to decrease independently by 0, 1,...,m n−1 while remaining inside Ωn; a zero last
coordinate stays ﬁxed. The resulting vertices form a rectangular box with mn vertices in each
active coordinate direction. Since each side length is o(n), Lemma 7.1 shows that all edges in
the ℓth coordinate direction have weight Rℓq(aℓ) +o(1), uniformly throughout the box.
On a one-dimensional path with mn vertices and constant edge weight w, the ﬁrst sine vector
has Rayleigh quotient 2w cos(π/(mn + 1)). Taking the product of these sine vectors over the
coordinate directions therefore gives
2
r+1∑
ℓ=1
Rℓq(aℓ) cos π
mn + 1 +o(1).
The Rayleigh–Ritz principle ( 26) now proves ( 84). If ar+1 = 0 , the rectangular box has no
direction corresponding to the last ambient coordinate, but the omitted contribution Rr+1q(0)
also vanishes. Hence the same lower bound holds when ar+1 = 0. □
The dimension calculation is separate from the spectral estimate. At the upper corner λ =λ∗
n,
Lemma A.1 gives the exponential growth rates of the ambient representation and the stabilizer
representation:
1
n log2 dimVλ =
r+1∑
ℓ=1
Hsph(aℓ) +o(1), 1
n log2 dimEµ =
r∑
m=1
Hsph(bm) +o(1). (85)
FixA> maxℓaℓ. For all suﬃciently large n, every λ∈Ωn satisﬁesλℓ≤Nℓ,n≤An. Since Hsph
is increasing, Lemma A.1 therefore gives uniformly on Ωn
1
n log2 dimVλ =
r+1∑
ℓ=1
Hsph
(λℓ
n
)
+Or,A
(log(n + 2)
n
)
≤
r+1∑
ℓ=1
Hsph
(Nℓ,n
n
)
+Or,A
(log(n + 2)
n
)
.
Thus the upper corner λ∗
n maximizes the ambient dimension exponent, with uniform error
Or,A(log(n + 2)/n). There are only O(nr+1) ambient weights in Ωn, so ∑
λ∈Ωn dimVλ diﬀers
from the largest ambient dimension by a subexponential factor:
1
n log2
∑
λ∈Ωn
dimVλ =
r+1∑
ℓ=1
Hsph(aℓ) +o(1). (86)
Proof of Theorem 1.2. First suppose
2Γr(a, b)>s,
so Lemma 7.2 implies that ΛΩn−s stays uniformly positive. Hence the prefactor in ( 78) is
bounded, while ( 85) and ( 86) give dimension-ratio exponent Φr. Consequently,
A(n,s )≤2(Φr(a,b)+o(1))n.
The estimate extends to the feasibility boundary 2Γr =s >0. For c >0, deﬁne the scaling
map Sc(u) = A− 1(cA(u)). Replacing each aℓ,b m by Sc(aℓ),S c(bm) multiplies all quadratic
coordinates by c, preserving interlacing and the residues Rℓ. If c > 1, strict monotonicity of
q increases Γr. Taking c↓1 therefore approximates each tuple satisfying 2Γr = s by strictly
interlacing tuples with 2Γr >s whose dimension exponents converge to Φr. Taking the inﬁmum
over the tuples satisfying ( 80) and 2Γr≥s, and then over all ﬁnite hierarchy levels, proves the
second assertion of Theorem 1.2 . □
Deﬁne
κr(s) = inf
a1>b1>···>br>ar+1≥ 0
2Γr(a,b)≥ s
Φr(a, b), κ ∞ (s) = inf
r≥ 0
κr(s).
The quantityκr(s) is the best exponent obtained directly on the whole sphere at hierarchy level r.
By Theorem 1.2 , approximating tuples with 2Γr =s by tuples with 2Γr >s bounds the whole-
sphere code exponent by κr(s). For any error tolerance, choose a ﬁnite level approximating
59
===== PAGE 62 =====
κ∞ (s) and keep that level ﬁxed as n→∞. Thus
lim sup
n→∞
1
n log2A(n,s )≤κ∞ (s).
In particular, the hierarchy depth is ﬁxed before the dimension limit. We can further improve
a ﬁxed-angle bound by the spherical-cap reduction recalled in ( 10): restrict to a suﬃciently
populated spherical cap and project to a lower-dimensional sphere with inner-product threshold
0≤t≤s. The spherical-slice inequality of Sidelnikov and Kabatianskii–Levenshtein [ Sid74,
KL78], recalled in ( 10), charges the exponential cost 1
2 log2((1−t)/(1−s)) for restricting to the
cap and projecting to the smaller sphere. Applying this inequality at each ﬁxed hierarchy level
gives
κr(s) = inf
0≤ t≤ s
{
κr(t) + 1
2 log2
1−t
1−s
}
, κ∞ (s) = inf
r≥ 0
κr(s), (87)
where κr(0) = 0 . Consequently,
lim sup
n→∞
1
n log2A(n,s )≤κ∞ (s).
Thusκr is the exponent obtained directly on the whole sphere, and κr includes the additional
optimization over spherical caps.
7.2. Strict improvement at every hierarchy level. The direct and spherical-cap-optimized
exponents κr(s) and κr(s) are nonincreasing in r, since a level- r tuple is recovered as a limit
of level- (r + 1) tuples. We prove that both decrease strictly at every 0 < s <1. The ﬁrst
comparisons isolate the intermediate harmonic-degree path ( 70): replacing the classical ﬁxed
line by the moving stabilizer space Hk(x⊥ ) gives one strict improvement, and allowing a second
ambient highest-weight coordinate gives another. Extending this argument to all hierarchy
levels requires controlling minimizing sequences whose coordinates escape to inﬁnity.
Forr = 0 , Γ0(a) = q(a) and Φ0(a) = Hsph(a); the spectral boundary 2q(a0(s)) = s recov-
ers the direct whole-sphere Kabatianskii–Levenshtein exponent Hsph(a0(s)). The intermediate
one-row construction is the restriction a2 = 0 of level 1. By ( 11), its spectral quantity is
Γ1((a, 0),b ) = Γ row(a,b ), and its dimension exponent is Hsph(a)−Hsph(b). The optimized one-
row rate is
κrow(s) = inf
a>b>0
2Γrow(a,b)≥ s
(
Hsph(a)−Hsph(b)
)
, (88)
and its cap-optimized exponent κrow is obtained by replacing κr with κrow in ( 87).
Two perturbations drive the strict improvements. Opening a zero terminal ambient coordi-
nate increases the spectral quantity and decreases the dimension exponent at the same level;
once that coordinate is positive, appending a stabilizer row gives the same improvements one
level higher.
Proposition 7.3. Fix 0 < s <1 and r≥0, and let a = (a1,...,a r+1) and b = (b1,...,b r)
satisfy
a1>b 1>a 2>···>b r >a r+1≥0, 2Γr(a, b)≥s.
Forr = 0, the interlacing condition reduces to a1≥0.
(1) If r≥1 and ar+1 = 0, there are strictly interlacing vectors a′∈Rr+1 and b′∈Rr with
a′
r+1> 0 such that
2Γr(a′, b′)> 2Γr(a, b)≥s, Φr(a′, b′)< Φr(a, b).
(2) If ar+1 > 0, there are strictly interlacing vectors a′∈Rr+2 and b′∈Rr+1 with a′
r+2 =
0<b ′
r+1<a ′
r+1 such that
2Γr+1(a′, b′)> 2Γr(a, b)≥s, Φr+1(a′, b′)< Φr(a, b).
60
===== PAGE 63 =====
Proof. Write Γ = Γ r(a, b), Φ = Φ r(a, b), and work in the quadratic coordinates xℓ,y m. For the
ﬁrst assertion, choose t> 0 small and open the zero terminal coordinate by setting
˜a =
(
a1,...,a r,A− 1(t2)
)
, Γopen = Γ r(˜a, b), Φopen = Φ r(˜a, b).
Expanding ( 81) gives
Γopen = Γ +
∏
mym∏
ℓ≤ rxℓ
t +O(t2), Φopen = Φ +O(t2 log(1/t)).
Replacing the zero terminal ambient coordinate by ˜ar+1 = A− 1(t2) therefore increases the
spectral quantity to ﬁrst order, while its direct contribution to the dimension exponent is smaller.
To turn this spare spectral gain into a strict reduction of the exponent, rescale all quadratic
coordinates simultaneously using Sc. Its entropy derivative is
d
d logc Hsph(Sc(u))
⏐⏐⏐⏐
c=1
=ψ(u) := u(1 +u)
1 + 2u log2
1 +u
u , ψ (0) := 0.
With v = 1 + 2u, strict monotonicity follows from
4(log 2)dψ
dv = (1 +v− 2) logv + 1
v−1−2
v > 0.
Hence the strict interlacing in ( 80) gives ∑
ℓψ(aℓ)−∑
mψ(bm)> 0. For suﬃciently small ﬁxed
η > 0, put c = 1−ηt, a′
ℓ = Sc(˜aℓ), and b′
m = Sc(bm). This common contraction preserves a
positive spectral gain of order t while decreasing the dimension exponent by order t, proving
the ﬁrst assertion.
For the second assertion, choose 0< ε < ar+1, and append a new stabilizer row and a zero
ambient row:
˜a = (a1,...,a r+1, 0), ˜b = (b1,...,b r,ε ), e =A(ε).
Each existing interpolation weight becomes Rnew
ℓ = Rℓ(1−e/xℓ), while the new zero node
contributes nothing to the spectral quantity. Write Γapp = Γ r+1(˜a,˜b) and Φapp = Φ r+1(˜a,˜b).
Then
Γapp = Γ−e
∑
ℓ
Rℓq(aℓ)
xℓ
, Φapp = Φ−Hsph(ε).
Put
DΓ =
∑
ℓ
Rℓq(aℓ)
2(1 + 4xℓ) > 0, L =
∑
ℓ
Rℓq(aℓ)
xℓ
.
Under a common expansion of all quadratic coordinates, the logarithmic derivative of the orig-
inal spectral quantity Γ is DΓ. For ﬁxed θ > 0, choosing logc = (L/DΓ +θ)e and setting
a′
ℓ =Sc(˜aℓ), b′
m =Sc(˜bm) more than restores the spectral loss eL, at dimension-exponent cost
O(e). Since e = O(ε) and Hsph(ε) = ε log2(1/ε) +O(ε), the expanded level- (r + 1) tuple has
spectral quantity larger than Γ and dimension exponent smaller than Φ. □
At level 1, these perturbations separate the classical construction, its one-row reﬁnement,
and the complete level-one construction; the same calculation supplies a boundary estimate for
the general argument.
Lemma 7.4. For every ﬁxed 0<s< 1,
κ1(s)<κ row(s)<κ 0(s), κ1(s)<κrow(s)<κ0(s) = BKL(s).
Proof. Since increasing b decreases the one-row objective Hsph(a)−Hsph(b) in (88), the optimum
overb for ﬁxed a>a 0(s) lies on the spectral boundary b =Bs(a), where
Bs(a) =
√
1 + 4a(1 +a)−2s(1 + 2a)
√
a(1 +a)−1
2 .
Ata =a0(s)+δ,Bs(a) = 1
2
√
1−s2δ+Os(δ2). Since Hsph(u) = u log2(1/u)+O(u), the boundary
objective is smaller than Hsph(a0(s)) for suﬃciently small δ >0. Thus κrow(s)<κ 0(s).
61
===== PAGE 64 =====
As a→∞, the boundary objective tends to −1
2 log2(1−s), which is larger than Hsph(a0(s)).
Indeed, set t = s/(1 +
√
1−s2)∈(0, 1). Since s = 2t/(1 + t2) and a0(s) = t2/(1−t2), the
diﬀerence, multiplied by log 2, is
log(1 +t) + 1
2 log(1 +t2)−2t2
1−t2 log 1
t.
The last term is smaller than t, since log(1/t)< (t− 1−t)/2. The ﬁrst two terms are larger than
t: their diﬀerence from t vanishes at zero and has derivative t2(1−t)/((1 +t)(1 +t2))> 0. Thus
the one-variable minimization over a attains its inﬁmum at a ﬁnite interior point.
Applying the ﬁrst part of Proposition 7.3 to the minimizing level-one tuple
(
(a, 0), (Bs(a))
)
givesκ1(s)<κ row(s).
To justify optimization over spherical caps, put G(t,a ) = Hsph(a)−Hsph(Bt(a)) fora≥a0(t).
This function is continuous, including at a = a0(t), where G(t,a 0(t)) = κ0(t). The explicit
formula for Bt(a) givesBt(a)/a→√1−t, locally uniformly for 0<t< 1. Hence
G(t,a )−→−1
2 log2(1−t) ( a→∞),
with the same local uniformity. The strict improvement over Hsph(a0(t)) and the larger limiting
objective as a→∞therefore restrict all minimizing a to a common bounded interval [a0(t),A ]
for t in a suﬃciently small neighborhood of any ﬁxed t0∈(0, 1). Parameterizing that interval
by a = a0(t) + u(A−a0(t)), 0≤u≤1, expresses κrow(t) as the minimum of a continuous
function on a ﬁxed compact interval. Thus κrow is continuous on (0, 1). Since
0≤κrow(t)≤κ0(t) = O
(
t2 log(1/t)
)
(t↓0),
it extends continuously to t = 0 with value zero. The classical and one-row spherical-cap
objectives are consequently continuous on the compact interval [0,s ] and attain their minima.
Neither minimum occurs at t = 0, since the slice cost decreases by t/(2 log 2) +O(t2), whereas
both code exponents increase by at most O(t2 log(1/t)). Applying κrow(t)<κ 0(t) and κ1(t)<
κrow(t) at the minimizing thresholds for the classical and one-row spherical-cap objectives gives
the two cap-optimized inequalities. □
The ﬁrst-level comparison above uses an attained one-row optimizer. At higher levels, Propo-
sition 7.3 improves each ﬁxed tuple, but this does not by itself give a strict inequality between
optimized exponents: an ambient coordinate and its interlacing stabilizer coordinate can diverge
together while their entropy diﬀerence remains bounded. The next lemma identiﬁes precisely
these noncompact limits.
Lemma 7.5. Fix r ≥0, and consider a sequence of strictly interlacing level- r tuples with
bounded exponents Φr. After passing to a subsequence, there are 0≤j≤r, a strictly interlacing
level-j tuple (a, b), and 0<c ≤1 such that
Φr−→Φj(a, b)−log2c, 1−2Γr−→c2(
1−2Γj(a, b)
)
.
If c< 1, then j <r. Conversely, this limiting datum is approximable at level j + 1 when c< 1
and at level j when c = 1.
Proof. Putf (x) = Hsph(A− 1(x)). This increasing function satisﬁes f (x) = 1
2 log2x+log2e+o(1)
asx→∞. In the quadratic coordinates from ( 81), the exponent is a sum of nonnegative terms:
Φr =f (xr+1) +
r∑
i=1
(
f (xi)−f (yi)
)
.
Thusxr+1 stays bounded, and every divergent xi has a divergent paired yi withyi/xi bounded
away from zero. After extracting a subsequence, the divergent pairs are i = 1,...,k , and
yi
xi
−→αi∈(0, 1], c 2 =
k∏
i=1
αi.
62
===== PAGE 65 =====
Take limits of the remaining ﬁnite coordinates and cancel coincident numerator and denominator
factors in the rational Stieltjes transform
m(z) =
∏r
i=1(z−yi)
∏r+1
i=1 (z−xi) =
r+1∑
i=1
Ri
z−xi
.
Weak interlacing leaves a strictly interlacing level- j tuple with j≤r−k, and m(z)→c2mj(z)
for z <0. Consequently, on the compactiﬁed half-line, the residue measures converge to
∑
i
Riδxi−→c2∑
i
R(j)
i δx(j)
i
+ (1−c2)δ∞ .
Since q(A− 1(x))→1/2 as x→∞, integrating this function gives the asserted limit of Γr. The
asymptotic formula for f gives the corresponding limit of Φr. If c< 1, at least one pair diverges,
so j <r.
Conversely, for c < 1, prepend the quadratic coordinates x = M and y = c2M to the
level-j tuple and let M→∞. If c = 1 , no additional pair is required. Further levels can be
added without changing the limit by appending a stabilizer coordinate tending to zero and a
zero ambient coordinate; a zero terminal coordinate can ﬁrst be opened by an arbitrarily small
amount. At a positive spectral feasibility boundary, slightly decrease c whenc< 1; when c = 1,
apply the common scaling Sd withd↓1. Either perturbation makes the approximations strictly
feasible without changing their limiting exponent. □
The compactiﬁcation parameter c records precisely the spherical-cap cost. Indeed, if t =
2Γj(a, b) and s = 1 −c2(1−t), then −log2c = 1
2 log2((1−t)/(1−s)), exactly the cost in
(87). The local perturbations can therefore be applied to the ﬁnite residual tuple to prove strict
improvement of the optimized exponents at every level.
Corollary 7.6. For every r≥0 and 0<s< 1,
κr+1(s)<κ r(s), κr+1(s)<κr(s).
At level 1, moreover, κ1(s)<κ row(s)<κ 0(s) and κ1(s)<κrow(s)<κ0(s) = BKL(s).
Proof. Appending vanishing rows shows that 0≤κr(t)≤κ0(t). A minimizing sequence for κr(s)
therefore has bounded exponent. Apply Lemma 7.5 to obtain a level-j tuple and 0<c ≤1 with
κr(s) = Φ j−log2c, c 2(1−2Γj)≤1−s.
If its terminal ambient coordinate vanishes and j≥1, the ﬁrst part of Proposition 7.3 , applied
at the threshold 2Γj > 0, decreases Φj and increases Γj. Retaining c, the resulting datum is
approximable at level at most r, contradicting minimality. If j = 0 and the ambient coordinate
vanishes, then Γj = 0, so feasibility gives
Φj−log2c≥−1
2 log2(1−s)>κ 0(s)≥κr(s),
where the strict middle inequality was proved in the proof of Lemma 7.4 . Hence the terminal
ambient coordinate is positive.
The second part of Proposition 7.3 now produces a level- (j + 1) tuple with strictly smaller
exponent and strictly larger spectral quantity. Retain the factor c. If c = 1 , this datum is
approximable at level j + 1≤r + 1; if c< 1, it is approximable at level j + 2≤r + 1. Its strict
spectral margin persists under approximation, proving κr+1(s)<κ r(s).
The same compactiﬁcation shows that κr is lower semicontinuous on (0, 1): if sn→s, nearly
minimizing tuples have uniformly bounded exponents, and their limiting datum is feasible at s
and approximable at level at most r. At zero, 0≤κr(t)≤κ0(t)→0. Therefore the inﬁmum
deﬁning κr(s) is attained on [0,s ]. It is not attained at zero: as t↓0,
κr(t)≤κ0(t) = O
(
t2 log(1/t)
)
, 1
2 log2(1−t) =−t
2 log 2 +O(t2).
Evaluating the ﬁrst strict inequality at the positive minimizing threshold proves κr+1(s)<κr(s).
The ﬁrst-level comparisons are Lemma 7.4 . □
63
===== PAGE 66 =====
8. Sphere packings
We now convert the spherical hierarchy into an upper bound for the maximal Euclidean
sphere-packing density ∆n. The upper-hemisphere comparison ( 89) bounds ∆n by the product
of a spherical-code size and an explicit spherical-cap volume factor. Unlike the coding problem,
where the separation threshold s is ﬁxed, the packing comparison allows us to optimize over s.
The resulting packing exponent balances the spherical-code exponent against the spherical-cap
volume exponent.
8.1. F rom spherical codes to sphere packings. We combine the upper-hemisphere compar-
ison ( 89) with the ﬁnite-level spherical-code bounds and show that spherical-cap optimization
does not further improve the angle-optimized packing exponent.
For−1 < s < 1, Sidelnikov’s upper-hemisphere inequality [ Sid74], in the normalization
of [ CZ14, (2.1)], states that
∆n≤
(1−s
2
)n/2
A(n + 1,s ). (89)
The factor ((1−s)/2)n/2 is the geometric cost of the upper-hemisphere comparison. Thus any
spherical-code exponent A(n,s )≤2(B(s)+o(1))n gives
∆n≤2(B(s)− 1
2 log2
2
1−s +o(1))n. (90)
At hierarchy levelr, deﬁne the positive sphere-packing decay exponent γr obtained by optimizing
(90):
γr = sup
0<s<1
(1
2 log2
2
1−s−κr(s)
)
= sup
a1>b1>···>br>ar+1≥ 0
(1
2 log2
2
1−2Γr(a, b)−Φr(a, b)
)
.
(91)
For a ﬁxed parameter tuple (a, b) satisfying ( 80), the packing objective 1
2 log2(2/(1−s))−
Φr(a, b) increases with s up to the feasibility boundary s = 2Γ r(a, b). Substitution at that
boundary gives the second formula in ( 91).
For each ﬁxed s, we may ﬁrst choose a spherical-cap threshold 0≤t≤s and use the cap-
optimized spherical-code exponent κ∞ (s) deﬁned in ( 87). Substituting the resulting estimate
A(n + 1,s )≤2(κ∞ (s)+o(1))n into the upper-hemisphere inequality ( 89), and then optimizing the
resulting packing decay exponent over s, gives
γ∞ = sup
0<s<1
(1
2 log2
2
1−s−κ∞ (s)
)
. (92)
The spherical-cap reduction does not improve the angle-optimized packing bound. Indeed,
changing the inner-product threshold from s tot incurs the spherical-slice exponent 1
2 log2((1−
t)/(1−s)), which cancels the change in the upper-hemisphere volume exponent:
1
2 log2
2
1−s−1
2 log2
1−t
1−s = 1
2 log2
2
1−t.
Consequently, substituting ( 87) into ( 92) gives
γ∞ = sup
0<t<1
(1
2 log2
2
1−t−κ∞ (t)
)
= sup
r≥ 0
γr.
(93)
Every level-r tuple satisfying ( 80) can be approximated at level r + 1 by appending br+1 = ε
and ar+2 = 0 ; if ar+1 = 0 , ﬁrst replace it by a suﬃciently small positive number. Taking ε↓0
gives γr+1≥γr. Therefore γ∞ = sup rγr = lim r→∞ γr. Thus spherical-cap reduction improves
ﬁxed-angle code bounds but does not improve the fully angle-optimized packing exponent γ∞ .
In particular,
∆n≤2− (γ∞ +o(1))n.
64
===== PAGE 67 =====
8.2. A relative-entropy upper bound. A relative-entropy identity, stated precisely in ( 99),
bounds every ﬁnite-level packing exponent by a common limiting threshold. The candidate
threshold is
λ∗ = 1
2 log2
2π
e . (94)
Throughout the following argument, log is natural and DKL denotes relative entropy.
To bound every ﬁnite hierarchy level by λ∗, we encode the interlacing quadratic coordinates
xℓ =A(aℓ) and ym =A(bm) by the union of [0,x r+1] and the intervals [ym,x m]. The Stieltjes
transformK of the indicator of that union simultaneously records the spectral quantity Γr and
the dimension exponent Φr. Tilting an explicit reference probability measure by e− K identiﬁes
the gap between λ∗ and the packing objective with a nonnegative relative entropy.
Proposition 8.1. Fix r≥0 and a parameter tuple satisfying (80), and set xℓ =A(aℓ), ym =
A(bm), and c = 1/4. Since the positive residues Rℓ sum to one and 0≤2q(aℓ)< 1, put
Z = 1−2Γr(a, b)> 0.
Deﬁne the interlacing indicator ξ, the associated Stieltjes transform K, two reference measures
ρ,ν , and the tilted measure ρK, with all measures supported on 0<t<c :
ξ(u) = 1[0,xr+1](u) +
r∑
m=1
1[ym,xm](u), (95)
K(t) =
∫∞
0
ξ(u)
t +udu, (96)
ρ(dt) = dt
π
√
t(c−t), ν (dt) = dt√c−t, (97)
ρK(dt) = Z− 1e− K(t)ρ(dt). (98)
The measures ρ, ν, and ρK all have total mass one, and
λ∗−
(1
2 log2
2
1−2Γr(a, b)−Φr(a, b)
)
= DKL(ν∥ρK)
2 log 2 . (99)
In particular, γr≤λ∗ for every r≥0.
Proof. The interpolation weights Rℓ from ( 81) form a probability distribution on the poles
xℓ. The rational Stieltjes transform m(z) of that distribution has the equivalent product and
partial-fraction representations
m(z) =
r∏
m=1
(z−ym)
r+1∏
ℓ=1
(z−xℓ)
=
r+1∑
ℓ=1
Rℓ
z−xℓ
.
Integrating ( 95) on each interlacing interval and then taking partial fractions gives
K(t) = log t +xr+1
t +
r∑
m=1
logt +xm
t +ym
,
e− K(t) = t
t +xr+1
r∏
m=1
t +ym
t +xm
=t
r+1∑
ℓ=1
Rℓ
t +xℓ
.
(100)
Puth(x) = (log 2) Hsph(A− 1(x)). Integrating h′on [0,x r+1] and the interlacing intervals [ym,x m]
gives
(log 2)Φr =
∫∞
0
h′(u)ξ(u)du. (101)
Both reference measures ρ and ν have mass one because c = 1/4. Diﬀerentiating h(x) =
(log 2)Hsph(A− 1(x)) gives
h′(x) = 1
1 + 2a log 1 +a
a , a =A− 1(x).
65
===== PAGE 68 =====
The substitutions t =c sin2θ and t =c(1−v2), respectively, give
2q
(
A− 1(x)
)
=
√ x
x +c =
∫c
0
x
x +tρ(dt), 2h′(x) =
∫c
0
ν(dt)
x +t.
By ( 100), ( 101), and Tonelli’s theorem,
Z =
∫c
0
e− K(t)ρ(dt), 2(log 2)Φr =
∫c
0
K(t)ν(dt). (102)
The ﬁrst identity in ( 102) normalizes ρK. Dividing the two reference densities and applying the
same substitution t =c(1−v2) gives
dν
dρ (t) = π
√
t,
∫c
0
logtν (dt) =−2.
Consequently,
DKL(ν∥ρK) =
∫c
0
(
logdν
dρ (t) +K(t) + logZ
)
ν(dt) = log π−1 + 2(log 2)Φr + logZ.
Rearrangement and ( 94) give ( 99). Nonnegativity of relative entropy and ( 91) give γr≤λ∗. □
Corollary 8.2. For every r≥0,
γr <γ r+1<λ ∗.
Proof. Set c = 1/4, and for 0≤x< ∞deﬁne
I(x) =
∫c
0
t
t +xρ(dt), f x(t) = t
(t +x)I(x), ρ x =fxρ.
Include the endpoints by setting f0 = 1 andf∞ (t) = 2t/c. The second identity in ( 100) expresses
ρK as a probability mixture of at most r + 1 measures ρx. Conversely, a mixture with distinct
ﬁnite nodes xi and positive weights αi is obtained by choosing
Ri = αi/I(xi)∑
jαj/I(xj).
The zeros of ∑
iRi/(z−xi) strictly interlace its poles, giving a level- r tuple after approximation
or the addition of vanishing rows. Nodes at inﬁnity are obtained by approximation.
The bounds c
4(c/2 +x)≤I(x)≤c
c +x, t
c≤fx(t)≤4
show that relative entropy is continuous on the compact space of mixtures of at most r + 1
nodes in [0,∞]. Indeed, |logt|is integrable against ν. Consequently, Proposition 8.1 gives, with
xi∈[0,∞],
γr =λ∗− 1
2 log 2 min
g=
∑r+1
i=1 αifxi
αi≥ 0,
∑
i αi=1
DKL(ν∥gρ).
Writeh =dν/dρ =π
√
t. The probability measure η(dx) = I(x)x− 1/2dx on (0,∞) satisﬁes
∫∞
0
fx(t)η(dx) =
∫∞
0
t
t +x
dx√x =π
√
t =h(t).
No ﬁnite mixture g equals h: if it contains a positive atom at zero, then g(0) > 0; otherwise,
g(t) = O(t) ast↓0, whereas h(t) = π
√
t. Thus the minimum relative entropy is positive, giving
γr <λ ∗.
Let g minimize the relative entropy at level r, and put A(x) =
∫c
0 fx(t)g(t)− 1ν(dt). Then
∫∞
0
A(x)η(dx) =
∫c
0
h(t)2
g(t) ρ(dt)> 1,
66
===== PAGE 69 =====
where strictness follows from Cauchy–Schwarz and g̸=h. Hence A(x)> 1 for some ﬁnite x> 0
distinct from the existing mixture nodes. Since fx/g≤c/(xI(x)), diﬀerentiation under the
integral is justiﬁed. For gε = (1−ε)g +εfx,
d
dεDKL(ν∥gερ)
⏐⏐⏐⏐
ε=0
= 1−A(x)< 0.
This level- (r + 1) mixture has smaller relative entropy, proving γr+1>γ r. □
8.3. A sharp Chebyshev construction. Corollary 8.2 shows that the ﬁnite-level exponents
increase strictly while remaining below λ∗. To show that their limit equals this threshold, we
form interlacing parameter tuples from Chebyshev roots and critical points. The resulting
sphere-packing bound agrees with the full-space companion in Chapter 1, but is obtained here
entirely from spherical certiﬁcates.
Theorem 8.3. The spherical hierarchy attains the threshold
limr→∞ γr =γ∞ =λ∗ = 1
2 log2
2π
e .
Consequently,
∆n≤2− (λ∗+o(1))n. (103)
Proof. By Corollary 8.2 , every ﬁnite-level exponent satisﬁes γr < λ∗. To obtain matching
exponents from below, ﬁx R >0, set N =r + 1, and choose the roots and critical points of a
Chebyshev polynomial shifted from [−1, 1] to [0,R ]. The roots and critical points, for 1≤ℓ≤N
and 1≤m<N , respectively, are
xℓ = R
2
(
1 + cos (2ℓ−1)π
2N
)
, y m = R
2
(
1 + cosmπ
N
)
. (104)
The roots xℓ and the critical points ym strictly interlace. If QN is the monic shifted Chebyshev
polynomial with roots x1,...,x N , then Q′
N has roots y1,...,y N − 1. The logarithmic derivative
of QN therefore gives
N − 1∏
m=1
(z−ym)
N∏
ℓ=1
(z−xℓ)
= Q′
N (z)
NQ N (z) = 1
N
N∑
ℓ=1
1
z−xℓ
.
Comparing this partial-fraction expansion with the residues in ( 81) shows that every interpo-
lation weight is Rℓ = 1/N. Put aℓ =A− 1(xℓ) and bm =A− 1(ym). For t >0, the interlacing
indicator ξN and its Stieltjes transform KN are
ξN (u) = 1[0,xN ](u) +
N − 1∑
m=1
1[ym,xm](u), K N (t) =
∫R
0
ξN (u)
t +u du.
By ( 102),
ZN = 1−2ΓN − 1(a, b) = 1−1
N
N∑
ℓ=1
√
xℓ
xℓ + 1/4
=
∫1/4
0
e− KN (t) dt
π
√
t(1/4−t).
Under u = R
2 (1 + cosθ), the critical points and the endpoints θ = 0,π divide (0,π ) into the
N equal intervals ((m−1)π/N,mπ/N ). Each interval contains one root at its midpoint, and
ξN selects exactly half of the interval. The change of variables contributes the Jacobian R
2 sinθ.
A veraging against continuous test functions and then using their density in L1(0,R ) gives weak-*
convergence in L∞ (0,R ). Explicitly,
lim
N →∞
∫R
0
f (u)ξN (u)du = 1
2
∫R
0
f (u)du for every f∈L1(0,R ).
67
===== PAGE 70 =====
Sinceh′(u) = O(log(1/u)) asu↓0, both h′andu↦→(t +u)− 1 belong to L1(0,R ) for every ﬁxed
t> 0. Therefore, ( 96) and ( 101) give
KN (t)−→1
2 logt +R
t , (105)
(log 2)ΦN − 1−→1
2h(R).
Since 0≤e− KN≤1, dominated convergence gives
ZN−→ZR =
∫1/4
0
√
t
t +Rρ(dt) = 2
π arcsin 1√
4R + 1. (106)
TakingN→∞with R ﬁxed gives
lim infr→∞ γr≥log(2/ZR)−h(R)
2 log 2 . (107)
As R→∞,
ZR = 1 +o(1)
π
√
R
, h (R) = 1
2 logR + 1 +o(1),
so the right side of ( 107) tends to λ∗. Together with the ﬁxed-level upper bound and ( 93), this
proves the threshold identity.
Forε > 0, choose successively R, a ﬁnite r, and s < 2Γr whose packing exponent exceeds
λ∗−ε. Keep these parameters ﬁxed. Then Theorem 1.2 and ( 89) give
lim sup
n→∞
1
n log2 ∆n≤−λ∗ +ε.
Takingn→∞before ε↓0 proves (103). □
Appendix A. Orthogonal representations and asymptotic dimensions
The spherical arguments in §§ 6 and 7 require two representation-theoretic inputs. The
coordinate-transition formulas give Proposition 6.1 and the ﬁnite spherical-code bound in The-
orem 6.2 . The uniform representation-dimension estimates give ( 85) and ( 86), which enter the
proof of the main spherical bound in Theorem 1.2 .
The spherical transition graph has vertices given by ambient SO(n)-representations contain-
ing a ﬁxed representation of the point stabilizer SO(n−1), and its edges come from multiplica-
tion by a coordinate. The ambient and stabilizer spaces are described in § 5.3. § A.1 identiﬁes the
possible vertices and edges, and § A.2 derives the common transition formula ( 74), its full-graph
normalization ( 75), and its dimension-weighted balance ( 76). These are the three conclusions
of Proposition 6.1 . Finally, § A.3 gives the exact Weyl dimensions and proves the uniform esti-
mates in Lemma A.1 , which determine the dimension ratio in ( 78). Throughout, the number
of nonzero highest-weight coordinates stays ﬁxed as n increases.
For the standard orthogonal-group conventions and formulas, see Kravchuk [ Kra18, §§2.1–
2.3 and App. B]. There, (2.18)–(2.21) give multiplicity-free restriction; (B.2) and its boundary
correction give the tensor product; (B.3)–(B.4) specify shifted weights; (B.5)–(B.6) give Weyl
dimensions; and (B.11)–(B.13) give coordinate-multiplication coeﬃcients. Source equation num-
bers below refer to this citation.
A.1. Stable tensor conventions. The vertices of the spherical graph are determined by the
orthogonal-group restriction rule ( 72); its possible edges are determined by tensoring with the
standard representation. We ﬁrst record the labeling and tensor conventions needed for both in-
puts. As in § 5.3, the ambient rotation group is SO(n), and the stabilizer of a point of the sphere
isSO(n−1). We call representations of SO(n) ambient representations and representations of
its point-ﬁxing subgroup stabilizer representations.
Fix r≥0 and n≥2r + 4, and retain ambient representations with at most r + 1 nonzero
rows and stabilizer representations with at most r nonzero rows. The remaining highest-weight
coordinates, called the zero tails, all vanish. Because at least one such coordinate remains, these
68
===== PAGE 71 =====
representations avoid the exceptional splitting that can occur when a Young diagram reaches
the ﬁnal orthogonal-group weight coordinate. In this stable range, their irreducible tensor
representations are indexed by dominant integral highest weights: weakly decreasing sequences
of nonnegative integers whose nonzero entries are the row lengths of the corresponding Young
diagram. Write the ambient and stabilizer weights, respectively, as
λ = (λ1,...,λ r+1, 0,... ), µ = (µ1,...,µ r, 0,... ).
The restriction of the ambient representation Vλ to SO(n−1) contains the stabilizer repre-
sentationEµ exactly when their row lengths interlace as in ( 72):
λ1≥µ1≥λ2≥···≥µr≥λr+1≥0.
Each such stabilizer representation occurs with multiplicity one. The rotation-equivariant co-
ordinate maps in ( 52) are obtained by tensoring with the standard SO(n) representation Rn,
of highest weight (1, 0,..., 0). The tensor-product formula (B.2) therefore gives the possible
coordinate transitions λ↔λ±eℓ, provided the target weight remains dominant and still inter-
laces µ. Although the odd-dimensional tensor-product formula initially appears to contain an
additional same-weight term, its zero-tail boundary correction removes that term. Hence these
transitions are precisely the edges of the graph in § 6.
A.2. Cancellation of the parity-dependent factors. §A.1 identiﬁes the possible directed
edges λ→λ±eℓ. Their squared coordinate coeﬃcients are the quantities pℓ,± =|cℓ,±|2 in
Proposition 6.1 , normalized by the unit base-point coordinate and the isometric embeddings in
(52). Kravchuk’s (B.12) and (B.13) give these coeﬃcients separately for odd and even ambient
dimensions. Factors belonging to zero highest-weight coordinates cancel in both expressions,
yielding the common formula ( 74). Parseval then gives ( 75), and the Weyl dimension formula
gives (76). As explained in § 5.3, the Spin(n) formulas apply unchanged to integral SO(n) tensor
representations.
In Kravchuk’s notation, the highest weights mn, mn− 1, and mn(±ℓ) correspond to λ,µ, and
λ±eℓ, respectively. Kravchuk’s coordinate-multiplication formulas use shifted weights, obtained
by adding the conventional dimension-dependent oﬀsets to the highest-weight coordinates. In
the notation of ( 73), put
Lℓ =λℓ + n
2−ℓ, M m =µm + n−1
2 −m, ρ n,r = n
2−r−1. (108)
The variables xd,j in (B.3)–(B.4) satisfy
n = 2N + 1 n = 2N
xn,ℓ Lℓ−1
2 Lℓ
xn− 1,m Mm Mm−1
2.
To interpret Kravchuk’s coordinate coeﬃcients, the multiplicity-free branching formulas (2.18)–
(2.21), applied successively along SO(n)⊃SO(n−1)⊃···⊃SO(2) give the orthonormal
Gelfand–Tsetlin basis: its basis vectors are indexed by a sequence of interlacing highest weights,
one for each group in the chain. Choose SO(n−1) to ﬁx the coordinate line Re1. The symbol
•in (B.11)–(B.13) selects this ﬁxed one-dimensional summand in Rn↓SO(n− 1)= Re1⊕e⊥
1 .
The squared coeﬃcient for this ﬁxed summand is exactly the directed transition weight pℓ,±
associated with ( 52); no additional coordinate normalization is required.
First suppose the ambient dimension is odd, n = 2N + 1. Write L =Lℓ for the shifted active
coordinate in ( 108). Squaring the odd-dimensional coordinate coeﬃcient (B.12) gives
pℓ,± =
N∏
m=1
(
(L±1
2 )2−M 2
m
)
2L(L±1
2 )
N∏
q=1
q̸=ℓ
(L2−L2
q)
. (109)
69
===== PAGE 72 =====
PutA =N−r−1, so ρn,r =A + 1
2 . For r + 1≤m≤N andr + 2≤q≤N , the zero tail gives
Mm =N−m, L q =N + 1
2−q.
The trailing numerator and denominator factors cancel as
∏N
m=r+1
(
(L±1
2 )2−M 2
m
)
(L±1
2 )∏N
q=r+2(L2−L2q) =L±
(
A + 1
2
)
=L±ρn,r.
Empty products are 1. Substitution into ( 109) leaves only numerator indices m ≤r and
denominator indices q≤r + 1.
The odd-dimensional Pieri formula in (B.2) appears to contain a copy of Vλ itself. However,
its boundary correction applies because N≥r + 2 and the ﬁnal highest-weight coordinate λN is
zero. Decreasing that zero coordinate gives a reﬂected weight representing the same SO(2N + 1)
representation; the correction subtracts the repeated term. Consequently,
HomSO(2N +1)
(
Vλ, R2N +1⊗Vλ
)
= 0.
Hence coordinate multiplication has no transition from Vλ back to itself. On the zero-tail
boundary λN = 0 , the coeﬃcient in (B.11) has the indeterminate form 0/0, so the remaining
transitions must be determined from the corrected tensor decomposition.
Now suppose the ambient dimension is even, n = 2N , and again write L =Lℓ. Squaring the
even-dimensional coordinate coeﬃcient (B.13) gives
pℓ,± =
N − 1∏
m=1
(
(L±1
2 )2−M 2
m
)
2
N∏
q=1
q̸=ℓ
(L2−L2
q)
. (110)
Put A =N−r−2, so ρn,r =A + 1. For r + 1≤m≤N−1 and r + 2≤q≤N , the zero tail
gives
Mm =N−1
2−m, L q =N−q.
The numerator factors for Mm and the denominator factors for Lq cancel according to
∏N − 1
m=r+1
(
(L±1
2 )2−M 2
m
)
∏N
q=r+2(L2−L2q) = L±(A + 1)
L = L±ρn,r
L .
Substitution into ( 110) shows that both parities give
pℓ,± =
(Lℓ±ρn,r)
r∏
m=1
(
(Lℓ±1
2 )2−M 2
m
)
2Lℓ
r+1∏
q=1
q̸=ℓ
(L2
ℓ−L2
q)
.
The common odd- and even-dimensional expression is ( 74). If the row lengths of λ±eℓ are not
weakly decreasing or fail ( 72), there is no target representation containing Eµ, and the transition
probability is zero. Applying Parseval to the orthogonal irreducible projections of ℓx⊗φλ,xY ,
whose squared norm is ∥Y∥2, gives the full-graph normalization ( 75). On every existing edge,
(111) gives
Dn(λ +eℓ)
Dn(λ) = pℓ,+(λ;µ)
pℓ,− (λ +eℓ;µ).
Equivalently,Dn(λ)pℓ,+(λ;µ) = Dn(λ +eℓ)pℓ,− (λ +eℓ;µ). Thus weighting each transition by
the dimension of its source makes the forward and reverse directions equal. This is ( 76), and
hence veriﬁes the reciprocity assumption ( 53) used to construct the symmetric spherical graph.
70
===== PAGE 73 =====
A.3. W eyl dimensions. The transition calculation gives the spectral constraint in Proposi-
tion 6.1 , but the spherical-code bound ( 78) also contains the ratio between the total ambient
dimension and the dimension of the common stabilizer space. We record exact formulas for
both dimensions and establish the uniform exponential estimates stated in Lemma A.1 .
WriteDn(λ) = dim Vλ. For a dominant integral highest weight λ with at most r + 1 nonzero
rows, Weyl’s dimension formula [ GW09, §7.1.2] simpliﬁes to
Dn(λ) =
r+1∏
i=1
2λi +n−2i
n−2i
(λi +n−i−r−2)!
(n−i−r−2)!
(r + 1−i)!
(λi +r + 1−i)!
×
∏
1≤ i<j≤ r+1
(λi−λj +j−i)(λi +λj +n−i−j)
(j−i)(n−i−j) .
(111)
Formula (111) is the zero-tail specialization of (B.5)–(B.6). If r≥1, substituting (n,λ,r )↦→
(n−1,µ,r −1) gives the stabilizer dimension dimEµ. If r = 0, the stabilizer representation is
trivial and has dimension 1, and we write Dn− 1(0) = 1 . The corresponding exponential rates
are expressed using the spherical entropy Hsph deﬁned in ( 9).
Lemma A.1. Fix r≥0 and A <∞, and assume n≥2r + 4. Uniformly over dominant
integral ambient weights λ = (λ1,...,λ r+1, 0,... ) and stabilizer weights µ = (µ1,...,µ r, 0,... )
with 0≤λi,µ j≤An,
1
n log2Dn(λ) =
r+1∑
i=1
Hsph
(λi
n
)
+Or,A
(log(n + 2)
n
)
,
1
n log2Dn− 1(µ) =
r∑
j=1
Hsph
(µj
n
)
+Or,A
(log(n + 2)
n
)
.
In particular, if λi/n→ai and µj/n→bj, the dimension exponents converge to ∑
i Hsph(ai)
and∑
j Hsph(bj), respectively.
Proof. Apply uniform Stirling to the ﬁnitely many factorials in ( 111). Dominance bounds every
active diﬀerence between 1 and Or,A(n), so all remaining factors contribute Or,A(log(n + 2)),
including on chamber walls and at zero rows. For r≥1, the stabilizer estimate follows identically
in dimension n−1; for r = 0, it is the identity log2 dimE0 = 0. □
Appendix B. The spherical-to-Euclidean limit
The companion paper in Chapter 1 analyzes the Cohn–Elkies sphere-packing linear program
directly in Euclidean space, proving both a universal bound for its Fourier-positive auxiliary
functions satisfying the required normalization and sign conditions and a matching construc-
tion. Neither argument requires the spherical hierarchy developed here. Nevertheless, the two
approaches share more than their ﬁnal exponent: several objects in the Euclidean construction
arise naturally when the inner-product threshold s of our spherical certiﬁcates tends to 1.
Cohn and Zhao’s upper-hemisphere construction gives the correspondence between spherical
certiﬁcates and Euclidean Cohn–Elkies auxiliary functions [ CZ14, Thm. 3.4 and subsequent dis-
cussion]. We recall the resulting change of scale, then identify the probability measure governing
the optimal spherical hierarchy with the limiting measure in the companion’s Euclidean argu-
ment. The limiting spherical potential also recovers the principal weight in its Mellin-transform
construction. The companion uses a second, smaller weight to control its Fourier estimates;
that additional correction has no spherical counterpart here.
B.1. The upper-hemisphere correspondence. Letgs(t) be a positive-deﬁnite spherical cer-
tiﬁcate on Sd, nonpositive for t≤s, and let gs,0 > 0 be its constant Gegenbauer coeﬃcient.
Set
Ls =
√
2
1−s, π (u) =
(
u,
√
1−|u|2)
(|u|< 1).
71
===== PAGE 74 =====
For a nonzero nonnegative radial cutoﬀ supported in the radius- Ls ball, η∈C∞
c (Bd
Ls), the
Cohn–Zhao upper-hemisphere construction [ CZ14, Thm. 3.4 and subsequent discussion] gives
the Euclidean function
fs(x) =
∫
Rd
η(z + 2x)η(z)gs
(
⟨π((z + 2x)/Ls),π (z/Ls)⟩
)
dz.
The integrand is zero unless both arguments of η belong to its support. Rotational invariance
makesfs a radial Schwartz function, and positive deﬁniteness of gs gives ˆfs≥0. If |x|≥1, the
spherical inner product in the integrand is at most 1−2|x|2/L2
s≤s, so fs(x)≤0. Thus fs is a
Euclidean Cohn–Elkies auxiliary function. Centering a Gram factorization of gs gives
fs(0) = gs(1)∥η∥2
2, ˆfs(0)≥2− dgs,0∥η∥2
1.
Taking cutoﬀs approaching the indicator of Bd
Ls therefore gives [ CZ14, Thm. 3.4 and subsequent
discussion]
LPd≤
(1−s
2
)d/2gs(1)
gs,0
.
In particular, Ls→∞as s↑1, giving the Euclidean scaling used below.
B.2. The limiting hyperbolic measure. The spherical and Euclidean optimality arguments
each single out a probability measure. To compare them, we ﬁrst describe how the spherical
measure arises from the interlacing Chebyshev construction in the proof of Theorem 8.3 . Fix
T > 0, and let x1,...,x N and y1,...,y N − 1 be, respectively, the roots and critical points of
the shifted Chebyshev polynomial on [0,T ], as in ( 104). These two sets of nodes interlace.
The indicator ξN selects the alternating intervals between them, and its Stieltjes transform KN
converts those intervals into the exponential tilt of the reference probability measure ρ(dt) =
dt/(π
√
t(1/4−t)) on (0, 1/4):
ξN (v) = 1[0,xN ](v) +
N − 1∑
m=1
1[ym,xm](v),
KN (t) =
∫T
0
ξN (v)
t +v dv, ZN =
∫1/4
0
e− KN (t)ρ(dt).
Here t∈(0, 1/4) is the spectral variable on which ρ is supported, ZN normalizes the tilted
measure in ( 98), and the hierarchy level is N−1. Keeping T ﬁxed and letting N→∞, ( 105)
and ( 106) give
KT (t) = 1
2 logt +T
t , Z T = 2
π arcsin 1√
4T + 1.
The limiting feasible inner-product threshold is sT = 1−ZT , so
1−sT∼1
π
√
T
, L T =
√
2
1−sT
∼
√
2πT 1/4.
In particular, increasing T realizes the small-angle limit sT↑1.
The reference probability measures ρ and ν were introduced in ( 97). The relative entropy of
ν from the tilted measure controls the gap to the optimal packing exponent in ( 99). To identify
ν with the Euclidean limiting measure, change from the bounded spectral variable t∈(0, 1/4)
to the unbounded hyperbolic coordinate a> 0 deﬁned by
t = 1
4 sech2a. (112)
Under this change of variables, the reference and target measures in ( 97) are
ρ(dt) = 2
π sechada, ν (dt) = sech 2ada. (113)
The tilted probability measure ρKT from ( 98) then has density
ρKT (da) = 2
πZT
secha√
1 + 4T cosh2a
da−→sech2ada.
72
===== PAGE 75 =====
The convergence holds in total variation by dominated convergence and πZT
√
T→1.
The Euclidean lower-bound argument in Chapter 1, Section 3.1 obtains its corresponding
probability measure from the Poisson kernel of a complex strip. If u∈R denotes the rescaled
Mellin frequency, the limiting measure is
p(u)du = π
4 sech2
(πu
2
)
du, u ∈R.
The pushforward of p(u)du under a =π|u|/2 is exactly sech2ada . Thus the target probability
measure in the spherical relative-entropy bound and the measure in the Euclidean lower bound
coincide in hyperbolic coordinates. The hyperbolic densities in ( 113) also give
dν
dρ (a) = π
2 secha, D KL(ν∥ρ) = log π−1,
since
∫∞
0 sech2a log coshada = 1−log 2.
B.3. The limiting Mellin weight. The common probability measure identiﬁes the spherical
and Euclidean optimality arguments at the distributional level. We now give a stronger cor-
respondence: the limiting spherical potential determines the principal weight in the Euclidean
construction in Chapter 1, Section 4.1.
For a radial proﬁle g(r), its Mellin transform is Mg(ζ) =
∫∞
0 g(r)rζ− 1dr. In dimension d, put
λ =d/2 and Xg(τ ) = Mg(λ−iτ ). On this symmetry line, the Mellin–Fourier identity is given
in Chapter 1, Section 2.2:
Xˆg(τ ) = mλ(τ )Xg(−τ ), m λ(τ ) = πiτ Γ((λ−iτ )/2)
Γ((λ +iτ )/2).
The common envelope in the companion construction is
Eλ(τ ) = πiτ /2Γ
(λ−iτ
2
)
exp (λhϵ(τ/λ )).
Ifhϵ is even, then mλ(τ )Eλ(−τ ) = Eλ(τ ), so the modiﬁcation by hϵ preserves Fourier reﬂection;
see Chapter 1, Section 4.1. It is assembled from oscillations cos(az), where z =τ/λ and a> 0
is an oscillation scale, not a spatial radius. The oscillation weight occupies two disjoint intervals
of scales: its principal negative interval determines the sharp packing exponent, whereas a
smaller positive interval controls the global Fourier estimates. Only the negative interval has a
counterpart in the limiting spherical potential.
Under the hyperbolic change of variables ( 112), the potential KT diverges by an additive
constant as T→∞. Subtract this constant:
˜KT (a) = KT
(1
4 sech2a
)
−1
2 log(4T ) = 1
2 log
(
cosh2a + 1
4T
)
.
It follows that
˜KT (a)−→K∞ (a) = log cosha, e − K∞ (a) = secha. (114)
More precisely, the Euclidean construction modiﬁes the logarithm of its Mellin proﬁle by the
even function
hϵ(z) =
∫∞
0
wϵ(a)
(
cos(az)−1
)
da.
Here the rescaled frequency z may be complex. Fix suﬃciently small ϵ> 0, and put
Iϵ = [ϵ2, log(1/ϵ)], b ϵ(a) = 1−2ϵ(1 +a).
The principal negative part of the oscillation weight is
wϵ,− (a) =−bϵ(a)e− 2a
2a2 cosha 1Iϵ(a).
The companion supplements this negative part with an exponentially smaller positive correction
on a distant scale interval. That correction controls its global Fourier estimates without aﬀecting
the limiting radius; see Chapter 1, Sections 4.1–4.2.
73
===== PAGE 76 =====
To recover the negative weightwϵ,− from the spherical potential, deﬁne the ﬁnite-cutoﬀ weight
wϵ,T (a) =−bϵ(a)e− 2a
2a2 e−˜KT (a)1Iϵ(a).
For each ﬁxed ϵ> 0, ( 114) gives wϵ,T→wϵ,− uniformly on Iϵ. Thus the principal weight of the
full-space construction is an exponential tilt of the limiting spherical Stieltjes potential.
As ϵ↓0, the intervals Iϵ increase to (0,∞), and bϵ(a)→1 at each ﬁxed a > 0. Thus the
principal negative weight converges pointwise to w∗(a) =−e− 2a− K∞ (a)/(2a2), and its limiting
Mellin modiﬁcation is
h∗(z) = 1
2
∫∞
0
e− 2a− K∞ (a)
a2
(
1−cos(az)
)
da.
The integral converges locally uniformly on {z ∈C : |Imz|< 3}. At the limiting radius-
determining parameter u = 1, the contribution of w∗ to the logarithm of the radius is
∫∞
0
w∗(a)a sinhada =−1
2
∫∞
0
e− 2a tanha
a da. (115)
The expansion
e− 2a tanha =
∞∑
j=0
e− (4j+2)a(1−e− 2a)2
has nonnegative summands, so Tonelli’s theorem permits termwise integration. For u,v > 0,
the elementary integral identity
∫∞
0
e− ua−e− va
a da = log v
u
then gives Wallis’s product:
∫∞
0
e− 2a tanha
a da = log
∞∏
j=0
(2j + 2)2
(2j + 1)(2j + 3) = log π
2.
The companion’s Fourier-pair theorem in Chapter 1, Theorem 4.1 constructs radial Schwartz
functions f−,f + and an exterior radius Rϵ,d such that ˆf− = f+ > 0, f− (0) = f+(0) > 0, and
f− (x)< 0 whenever|x|≥Rϵ,d. In its radius formula, the principal negative weight contributes
(115), whereas the positive correction vanishes in the limit. Consequently,
lim
ϵ↓0
lim
d→∞
Rϵ,d√
d
= 1√
2π exp
(
−1
2 logπ
2
)
= 1
π.
Ifvd denotes the volume of the unit ball in Rd, then v1/d
d ∼
√
2πe/d. Thus we recover the same
Cohn–Elkies density rate as ( 103):
lim
ϵ↓0
lim
d→∞
v1/d
d
Rϵ,d
2 =
√e
2π = 2 − λ∗.
Thus the spherical construction recovers both the target probability measure and the principal
oscillation weight in the companion’s optimal full-space construction. This identiﬁes limiting
objects, without asserting that ﬁnite-dimensional spherical certiﬁcates converge to a particular
Euclidean auxiliary function. The order of limits also matters: the dimension ﬁrst tends to
inﬁnity at ﬁxed hierarchy level, the hierarchy level then increases at ﬁxed T , and ﬁnally T→∞
forces sT ↑1. If the last two limits are taken jointly, choosing N/
√
T → ∞retains every
ﬁxed neighborhood of the zero endpoint of the interlacing interval, since the smallest shifted
Chebyshev node satisﬁes
xN = T
2
(
1−cos π
2N
)
∼π2T
16N 2−→0.
74
===== PAGE 77 =====
References
[AJCHLT20] N. Afkhami-Jeddi, H. Cohn, T. Hartman, D. de Laat, and A. Tajdini, High-dimensional sphere
packing and the modular bootstrap , J. High Energy Phys. 12 (2020), article 066, doi:10.1007/
JHEP12(2020)066.
[BV08] C. Bachoc and F. Vallentin, New upper bounds for kissing numbers from semideﬁnite programming ,
J. Amer. Math. Soc. 21 (2008), 909–924, doi:10.1090/S0894-0347-07-00589-9.
[BN06] A. Barg and D. Nogin, Spectral approach to linear programming bounds on codes , Problems Inform.
Transmission 42 (2006), 77–89, doi:10.1134/S0032946006020025.
[Bas65] L. A. Bassalygo, New upper bounds for error correcting codes , Problems Inform. Transmission 1
(1965), no. 4, 32–35.
[BCV23] P.-A. Bernard, N. Crampé, and L. Vinet, Entanglement of free fermions on Johnson graphs , J.
Math. Phys. 64 (2023), no. 6, article 061903, doi:10.1063/5.0099879.
[CST08] T. Ceccherini-Silberstein, F. Scarabotti, and F. Tolli, Harmonic Analysis on Finite Groups: Repre-
sentation Theory, Gelfand Pairs and Markov Chains , Cambridge Studies in Advanced Mathematics,
vol. 108, Cambridge University Press, Cambridge, 2008, doi:10.1017/CBO9780511619823.
[CD25] A. Chailloux and T. Debris-Alazard, New solutions to Delsarte’s dual linear programs , IEEE Trans.
Inform. Theory 71 (2025), no. 1, 297–316, doi:10.1109/TIT.2024.3476974.
[CE03] H. Cohn and N. Elkies, New upper bounds on sphere packings. I , Ann. of Math. (2) 157 (2003),
689–714, doi:10.4007/annals.2003.157.689.
[CKMR V17] H. Cohn, A. Kumar, S. D. Miller, D. Radchenko, and M. S. Viazovska, The sphere packing problem
in dimension 24, Ann. of Math. (2) 185 (2017), 1017–1033, doi:10.4007/annals.2017.185.3.8.
[CZ14] H. Cohn and Y. Zhao, Sphere packing bounds via spherical codes , Duke Math. J. 163 (2014), 1965–
2002, doi:10.1215/00127094-2738857.
[CJJ22] L. N. Coregliano, F. G. Jeronimo, and C. Jones, A complete linear programming hierarchy for
linear codes, in 13th Innovations in Theoretical Computer Science Conference , LIPIcs 215 (2022),
article 51, 51:1–51:22, doi:10.4230/LIPIcs.ITCS.2022.51.
[CJJLL26] L. N. Coregliano, F. G. Jeronimo, C. Jones, N. Linial, and E. Loyfer, Higher-order Delsarte
dual LPs: lifting, constructions and completeness , in 17th Innovations in Theoretical Com-
puter Science Conference (ITCS 2026) , LIPIcs 362 (2026), article 44, 44:1–44:22, doi:10.4230/
LIPIcs.ITCS.2026.44.
[Del72] P. Delsarte, Bounds for unrestricted codes, by linear programming , Philips Res. Rep. 27 (1972),
272–289.
[Del73] P. Delsarte, An algebraic approach to the association schemes of coding theory , Philips Res. Rep.
Suppl. 10 (1973), vi+97 pp.
[DGS77] P. Delsarte, J. M. Goethals, and J. J. Seidel, Spherical codes and designs , Geom. Dedicata 6 (1977),
363–388, doi:10.1007/BF03187604.
[Fei12] P. Feinsilver, Representations of sl(2) in the Boolean lattice, and the Hamming and Johnson
schemes, Inﬁn. Dimens. Anal. Quantum Probab. Relat. Top. 15 (2012), no. 3, article 1250019,
doi:10.1142/S0219025712500191.
[FT05] J. Friedman and J.-P. Tillich, Generalized Alon–Boppana theorems and error-correcting codes, SIAM
J. Discrete Math. 19 (2005), 700–718, doi:10.1137/S0895480102408353.
[GW09] R. Goodman and N. R. Wallach, Symmetry, Representations, and Invariants , Graduate Texts in
Mathematics, vol. 255, Springer, New York, 2009, doi:10.1007/978-0-387-79852-3.
[Gor00] D. V. Gorbachev, Extremal problem for entire functions of exponential spherical type, connected
with the Levenshtein bound on the sphere packing density in Rn, Izv. Tula State Univ. Ser. Math.
Mech. Inform. 6 (2000), 71–78; in Russian.
[KL78] G. A. Kabatianskii and V. I. Levenshtein, On bounds for packings on a sphere and in space , Prob-
lems Inform. Transmission 14 (1978), 1–17.
[Koo81] T. H. Koornwinder, Clebsch–Gordan coeﬃcients for SU(2) and Hahn polynomials , Nieuw Arch.
Wisk. (3) 29 (1981), 140–155.
[Kra76] M. Krämer, Multiplicity free subgroups of compact connected Lie groups , Arch. Math. (Basel) 27
(1976), 28–36, doi:10.1007/BF01224637.
[Kra18] P. Kravchuk, Casimir recursion relations for general conformal blocks , J. High Energy Phys. 2018,
no. 2, article 011, doi:10.1007/JHEP02(2018)011.
[Lev79] V. I. Levenshtein, On bounds for packings in n-dimensional Euclidean space , Soviet Math. Dokl.
20 (1979), 417–421.
[LL23] E. Loyfer and N. Linial, New LP-based upper bounds in the rate-vs.-distance problem for binary lin-
ear codes, IEEE Trans. Inform. Theory 69 (2023), no. 5, 2886–2899, doi:10.1109/TIT.2023.3236660.
[Mac63] J. MacWilliams, A theorem on the distribution of weights in a systematic code , Bell Syst. Tech. J.
42 (1963), 79–94, doi:10.1002/j.1538-7305.1963.tb04003.x.
[MRR W77] R. J. McEliece, E. R. Rodemich, H. C. Rumsey, Jr., and L. R. Welch, New upper bounds on the
rate of a code via the Delsarte–MacWilliams inequalities , IEEE Trans. Inform. Theory 23 (1977),
157–166, doi:10.1109/TIT.1977.1055688.
75
===== PAGE 78 =====
[Mus08] O. R. Musin, The kissing number in four dimensions , Ann. of Math. (2) 168 (2008), 1–32,
doi:10.4007/annals.2008.168.1.
[NS05] M. Navon and A. Samorodnitsky, On Delsarte’s linear programming bounds for binary codes , in
46th Annual IEEE Symposium on Foundations of Computer Science (FOCS 2005) , 2005, 327–336,
doi:10.1109/SFCS.2005.55.
[OS79] A. M. Odlyzko and N. J. A. Sloane, New bounds on the number of unit spheres that can touch
a unit sphere in n dimensions, J. Combin. Theory Ser. A 26 (1979), 210–214, doi:10.1016/0097-
3165(79)90074-8.
[PMP23] J. C.-J. Pang, H. Mahdavifar, and S. S. Pradhan, New bounds on the size of binary codes with
large minimum distance , IEEE J. Sel. Areas Inform. Theory 4 (2023), 219–231, doi:10.1109/
JSAIT.2023.3295836.
[Sam01] A. Samorodnitsky, On the optimum of Delsarte’s linear program , J. Combin. Theory Ser. A 96
(2001), 261–287, doi:10.1006/jcta.2001.3176.
[Sam04] A. Samorodnitsky, On linear programming bounds for spherical codes and designs , Discrete Comput.
Geom. 31 (2004), 385–394, doi:10.1007/s00454-003-2858-0.
[Sam25] A. Samorodnitsky, On the diﬃculty to beat the ﬁrst linear programming bound for binary codes ,
IEEE Trans. Inform. Theory 71 (2025), no. 4, 2383–2388, doi:10.1109/TIT.2024.3504268.
[SZ24] N. T. Sardari and M. Zargar, New upper bounds for spherical codes and packings , Math. Ann. 389
(2024), 3653–3703, doi:10.1007/s00208-023-02738-z.
[S42] I. J. Schoenberg, Positive deﬁnite functions on spheres , Duke Math. J. 9 (1942), 96–108,
doi:10.1215/S0012-7094-42-00908-6.
[Sch05] A. Schrijver, New code upper bounds from the Terwilliger algebra and semideﬁnite programming ,
IEEE Trans. Inform. Theory 51 (2005), 2859–2866, doi:10.1109/TIT.2005.851748.
[SvdW53] K. Schütte and B. L. van der Waerden, Das Problem der dreizehn Kugeln , Math. Ann. 125 (1953),
325–334, doi:10.1007/BF01343127.
[Sid74] V. M. Sidel’nikov, New bounds for densest packing of spheres in n-dimensional Euclidean space ,
Math. USSR-Sb. 24 (1974), no. 1, 147–157, doi:10.1070/SM1974v024n01ABEH001911.
[Sri11] M. K. Srinivasan, Symmetric chains, Gelfand–Tsetlin chains, and the Terwilliger algebra of the
binary Hamming scheme , J. Algebraic Combin. 34 (2011), 301–322, doi:10.1007/s10801-010-0272-
2.
[Via17] M. S. Viazovska, The sphere packing problem in dimension 8, Ann. of Math. (2) 185 (2017), 991–
1015, doi:10.4007/annals.2017.185.3.7.
[Z24] M. Zargar, Stiefel manifolds and upper bounds for spherical codes and packings , 2024, arXiv:
2407.10697.
76
===== PAGE 79 =====
Chapter 3
A Counterexample to the Soﬁcity Conjecture
Abstract. A countable group is soﬁc if ﬁnite pieces of its multiplication table can
be faithfully approximated by permutations of ﬁnite sets. We prove that the unit
group LF2(1, 2)× of the binary Leavitt algebra is not soﬁc, disproving the soﬁcity
conjecture. The proof starts from Kun’s expander decomposition for property- (T )
groups and the Kun–Thom centralizer obstruction. A general expander-matching
argument recovers a single expanding component from a union of expanders. El-
ementary groups over the Leavitt algebra then force Thompson’s group V to be
locally embeddable into ﬁnite groups, a contradiction.
Contents
1. Introduction
2. An expander-matching criterion
3. The binary Leavitt conﬁguration
References
77
===== PAGE 80 =====
1. Introduction
A countable group is soﬁc if every ﬁnite portion of its multiplication table can be approximated
by permutations of a ﬁnite set: multiplication must hold at almost every point, and every noniden-
tity element must move almost every point. Gromov introduced this approximation property in
his work on symbolic dynamics [ Gro99]; Weiss subsequently named soﬁc groups and asked whether
a nonsoﬁc group exists [ Wei00, p. 351]. The question became known as the soﬁcity conjecture: is
every countable group soﬁc [ Pes08, Open Question 3.8]?
Let F2 be the ﬁeld with two elements. The noncommutative binary Leavitt algebra [ Lea62] is
R = LF2(1, 2) = F2⟨s0, s1, t0, t1 |tisj = δij, s 0t0 + s1t1 = 1⟩. (1)
For example, t0s0 = 1, whereas s0t0 is a proper idempotent. Write R× for its group of invertible
elements: x ∈ R× means that some y ∈ R satisﬁes xy = yx = 1. Since R is ﬁnitely generated over
the ﬁnite ﬁeld F2, both R and R× are countable.
Theorem 1.1. The unit group LF2(1, 2)× is not soﬁc.
Related work
Earlier work gave several conditional routes to nonsoﬁc groups. Bowen and Burton showed that
ﬂexible permutation stability of PSLd(Z) for some d ≥ 5 would produce such a group [ BB20].
Gohla and Thom showed that suitable central extensions of p-adic lattices would be nonsoﬁc
under a permutation-stability hypothesis; Chapman, Dikstein, and Lubotzky gave an algebraic and
combinatorial treatment of this implication [ GT24, CDL24]. Theorem 1.1 requires no unproved
stability hypothesis.
The Aldous–Lyons conjecture asked whether every unimodular random rooted network is a lo-
cal weak limit of ﬁnite networks [ AL07, Question 10.1]. It was disproved in companion papers by
Bowen, Chapman, Lubotzky, and Vidick and by Bowen, Chapman, and Vidick [ BCL V24, BCV25].
Their tour-de-force argument combines subgroup tests with a reﬁnement of the compression tech-
niques behind the breakthrough MIP∗ = RE of Ji, Natarajan, Vidick, Wright, and Yuen, which
also disproved Connes’s embedding conjecture [ JNVWY20]. The second companion paper also
gives another proof that Connes’s embedding conjecture is false [ BCV25]. To explain the relation-
ship with soﬁcity, let Fd be a free group of ﬁnite rank d ≥ 2. An invariant random subgroup of Fd
is a conjugation-invariant probability distribution on its subgroups. It is co-soﬁc if it is a weak
limit of the stabilizer distributions associated with uniformly chosen points of ﬁnite Fd-sets. The
Aldous–Lyons conjecture was equivalent to the assertion that, for every ﬁnite rank d ≥ 2, every
invariant random subgroup of Fd is co-soﬁc [ Gel18, Section 6].
The soﬁcity conjecture is precisely the restriction of this assertion to invariant random subgroups
concentrated on a single normal subgroup. Indeed, if N ◁ Fd and δN denotes the point mass at N ,
then
Fd/N is soﬁc ⇐ ⇒ δN is a co-soﬁc invariant random subgroup of Fd;
see [ Gel18, Section 6, Proposition 6.1]. Every ﬁnitely generated group is a quotient of some Fd,
and soﬁcity is detected on ﬁnitely generated subgroups. Therefore, the soﬁcity conjecture asks
exactly whether every such δN is co-soﬁc.
Our proof constructs a ﬁnitely generated nonsoﬁc subgroup G ≤ R× . For any surjection Fd ↠ G,
its kernel N therefore gives a non-co-soﬁc point mass δN . Equivalently, the generator-marked
Cayley diagram of G is a deterministic unimodular network that is not a local weak limit of ﬁnite
networks with the same markings. This makes no assertion about the underlying unmarked Cayley
graph. In contrast, a general non-co-soﬁc invariant random subgroup need not be supported on a
normal subgroup and therefore need not produce a nonsoﬁc quotient.
The original motivation for soﬁcity was Gottschalk’s surjunctivity conjecture. A group H is
surjunctive if, for every ﬁnite alphabet A, every injective H-equivariant continuous map AH → AH
is surjective. Gromov and Weiss proved that every soﬁc group is surjunctive [ Gro99, Wei00].
Bowen and Chapman constructed a surjunctive non-co-soﬁc invariant random subgroup [ BC25],
but their example is not concentrated on a normal subgroup and therefore does not produce
a surjunctive nonsoﬁc group. We do not know whether R× is surjunctive. A positive answer
78
===== PAGE 81 =====
would produce a surjunctive nonsoﬁc group, while a negative answer would disprove Gottschalk’s
conjecture. Since surjunctivity passes to subgroups [ Wei00, Lemma 1.1], a positive answer would
also establish surjunctivity of the copy V ≤ R× constructed below.
A group is hyperlinear if ﬁnite pieces of its multiplication table admit asymptotically faith-
ful models by ﬁnite-dimensional unitary matrices in normalized Hilbert–Schmidt distance. The
conjecture that every discrete group is hyperlinear, known as Connes’s embedding conjecture
for groups, remains a major open problem [ Pes08, Open Question 3.9]: no nonhyperlinear dis-
crete group is known. For permutations σ, τ of n points, their permutation matrices satisfy
∥Pσ − Pτ ∥2
2,n = 2 dH(σ, τ), where ∥ · ∥2,n is the normalized Hilbert–Schmidt norm and dH is nor-
malized Hamming distance. Thus every soﬁc group is hyperlinear [ Pes08, Theorem 3.3], but
Theorem 1.1 does not determine whether LF2(1, 2)× is hyperlinear. Hyperlinearity is equiva-
lent to Connes embeddability of the group von Neumann algebra [ Pes08, Theorem 8.5]. Al-
though MIP∗ = RE disproved Connes’s embedding conjecture for general von Neumann alge-
bras [ JNVWY20], it does not produce a nonembeddable group von Neumann algebra.
The corresponding approximation problem for the unnormalized Frobenius norm has a diﬀerent
answer. De Chiﬀre, Glebsky, Lubotzky, and Thom [ DCGLT20] constructed central extensions of
arithmetic lattices that are not approximable by ﬁnite-dimensional unitaries in this norm. Be-
cause hyperlinearity uses the normalized Hilbert–Schmidt norm, their examples do not produce a
nonhyperlinear group.
There are also conditional approaches to nonhyperlinear groups. Dogon showed that ﬂexible
Hilbert–Schmidt stability of certain property- (T ) groups would make nonsplit central extensions
nonhyperlinear; his examples include extensions of Sp2g(Z) with g ≥ 2 [Dog23]. Dogon and
Vigdorovich showed that if SL2(Z[1/p]) is ﬂexibly Hilbert–Schmidt stable for some prime p, then
a ﬁnite central extension of that group is nonhyperlinear [ DV26]. Both stability hypotheses remain
open.
Two further conjectures hold for soﬁc groups. Lück’s determinant conjecture asserts that the
modiﬁed Fuglede–Kadison determinant of every matrix over Z[H] is at least one [ ES05]. The
algebraic eigenvalue conjecture asserts that every eigenvalue of such a matrix acting on ℓ2(H)n
is an algebraic integer [ Tho08]. Neither is settled for R× . Manzoor constructed an invariant
random subgroup satisfying the determinant conjecture that is not co-hyperlinear [ Man25], but
this does not determine the conjecture for R× . The Kervaire–Laudenbach conjecture asks whether
every one-variable equation with coeﬃcients in a group and nonzero total exponent of the variable
has a solution in some larger group. It holds for every hyperlinear group [ NT22, Theorem 1.3].
Consequently, it would hold for R× if that group were hyperlinear, whereas its failure would exhibit
a nonhyperlinear group.
Kaplansky’s direct-ﬁniteness conjecture asks whether ab = 1 in a group algebra always implies
ba = 1. The superﬁcially similar relation t0s0 = 1 ̸= s0t0 does not disprove this conjecture: neither
s0 nor t0 belongs to R× , so their relation holds in R, not in F2[R× ]. For every group H, the rings
Z[H] and k[H] for ﬁelds k of characteristic zero are already stably ﬁnite [ BFF24, Theorem 3.4 and
Corollary 3.5]. Thus only positive-characteristic ﬁelds remain open for R× . If R× were surjunctive,
then k[R× ] would be stably ﬁnite for every ﬁeld [ BFF24, Corollary 3.25].
Binary self-similarity
The deﬁning relations of R can be written as rectangular-matrix identities:
S =
[
s0 s1
]
, T =
[t0
t1
]
, ST = 1, T S = I2.
Thus S : R2 → R and T : R → R2 are inverse right R-module maps, and
R ∼= R2 as right R-modules.
This is an isomorphism of modules, not of unital rings.
The same relations connect the Leavitt algebra with Thompson’s group. The Cuntz algebra O2
is generated by two isometries and their adjoints subject to the same formal relations as si, ti. It
is the universal C∗-completion of the complex Leavitt ∗-algebra LC(1, 2); our algebra R has the
same relations in characteristic two. Replacing initial binary words realizes Thompson’s group V
79
===== PAGE 82 =====
both in the unitary group of O2 [HO17, Section 4] and in the unit group of the binary Leavitt
algebra over any ﬁeld [ BS16, Section 2.2].
For a ﬁnite binary word a, let [a] denote the cylinder consisting of inﬁnite binary strings begin-
ning with a. A complete preﬁx code is a ﬁnite set of pairwise preﬁx-incomparable words whose
cylinders partition all inﬁnite binary strings. Repeatedly splitting a cylinder into its two children
produces complete preﬁx codes with any prescribed number n ≥ 1 of words. After ordering its n
words, every such code E determines a unital ring isomorphism
ΘE : Mn(R) ∼− − →R. (2)
Write ELn(R) for the subgroup of GLn(R) generated by the elementary matrices In + rEij, where
i ̸= j and r ∈ R. Its image
ELE(R) := Θ E(ELn(R)) ≤ R×
is the same elementary group realized inside R× through the binary preﬁx decomposition. Since
R is a ﬁnitely generated ring, the Ershov–Jaikin-Zapirain theorem gives these elementary groups
property (T ) when n ≥ 3 [EJ10, Theorem 1.1]. For the speciﬁc nine-word code D constructed in
Equation (14) , put
G := EL D(R) = Θ D(EL9(R)) ≤ R× .
Hence G ∼= EL9(R). The number nine is useful for the later preﬁx construction; the matrix
isomorphism (2) holds in every rank. Because soﬁcity passes to subgroups, it suﬃces to prove that
G is not soﬁc. In fact, the stronger identity G = R× is independently known [ KT26, Corollary 4.4],
but the proof does not require it.
Proof overview
A family of ﬁnite graphs of uniformly bounded degree is an expander family if there exists γ > 0
such that, in every graph, each vertex set U containing at most half the vertices has at least γ|U |
edges to its complement. Given permutations modeling a ﬁnite generating set, their generator
graph joins each point of the model set to its image under each generator. Kazhdan’s property (T )
is a uniform spectral-gap condition on unitary representations. Kun’s theorem says that the gener-
ator graph of a soﬁc approximation to a property- (T ) group becomes a disjoint union of uniformly
expanding graphs after changing a proportion of edges that tends to zero along the approxima-
tion [ Kun19, Theorem 1]. The expansion constant is uniform, but the number of components can
grow without bound: taking increasingly many disjoint copies preserves a soﬁc approximation.
The Kun–Thom obstruction requires a stronger hypothesis: if K has property (T ), J is ﬁnitely
generated, and a soﬁc approximation of K × J has a single uniformly expanding K-generator graph
on the whole approximation set, then J is locally embeddable into ﬁnite groups , or LEF [ KT19,
Theorem 1.1]. This means that every ﬁnite portion of the multiplication table of J embeds exactly
into a ﬁnite group.
The single-expander hypothesis in the Kun–Thom theorem cannot be replaced by an arbitrary
union of expanders: a commuting group may move between components without being LEF. For
example, set
Λ = SL 3(Z), B = BS(2, 3) = ⟨a, b |ab2a− 1 = b3⟩.
The group Λ has property (T ) and is residually ﬁnite, hence soﬁc. The group B is ﬁnitely presented
and soﬁc but not residually ﬁnite [ Pes08, Example 4.6]; hence it is not LEF [ VG97, Theorem 2.2].
Nevertheless, Λ× B is soﬁc [ ES06, Theorem 1(1)]. Thus the expanding Λ-components alone cannot
force their commuting group B to be LEF.
Proposition 2.3 bridges this gap without assuming that Kun’s decomposition has only one
component. It is a general group-theoretic criterion; the Leavitt algebra enters later, when we
construct an example satisfying its hypotheses. Suppose that G and its subgroup Γ ≤ G both
have property (T ), and that
G = ⟨Γ, t1, . . . , tm⟩, t iΓt− 1
i ≤ Γ (1 ≤ i ≤ m).
Suppose further that a ﬁnitely generated subgroup J ≤ G satisﬁes
[Γ, J] = 1 , Γ ∩ J = {1}, t 1J t− 1
1 ≤ Γ.
80
===== PAGE 83 =====
Thus Γ × J embeds in G, and the same conjugation moves both commuting factors inside Γ:
t1(Γ × J)t− 1
1 = (t1Γt− 1
1 ) × (t1J t− 1
1 ) ≤ Γ.
This additional nesting is absent from the direct-product example above. Under these assumptions,
Proposition 2.3 proves that soﬁcity of G would force J to be LEF.
To prove this implication, suppose that G has a soﬁc approximation on a ﬁnite set Y . Apply
Kun’s theorem separately to the generator graphs for Γ and G, obtaining two generally diﬀerent
partitions of Y into expanding components. Call their respective parts Γ-components and G-
components. For each i, let pi be the permutation approximating ti. Since tiΓt− 1
i ≤ Γ, expansion
implies that, apart from components containing o(|Y |) vertices altogether, each transported com-
ponent pi(C) lies almost entirely inside some Γ-component D. Diﬀerent transported components
may, however, initially select the same D.
For z ∈ Y , let C(z) be its Γ-component and deﬁne M (z) = |C(z)|. If A is a G-component, let
mA be a median of the values M (z) for z ∈ A, and deﬁne
f (z) = M (z)
M (z) + mA
, z ∈ A.
The inclusions tiΓt− 1
i ≤ Γ imply that f is almost nondecreasing along each pi, while the Γ-
generators almost preserve f . Since every generator acts by a permutation, the total increase of f
equals its total decrease. Expansion of the G-components therefore forces f to remain close to its
median 1/2 outside o(|Y |) vertices. It follows that a transported component pi(C) and its target
D have approximately the same size. Since pi(C) already lies almost entirely in D, it occupies
more than half of D. Distinct transported components are disjoint and therefore cannot select the
same target.
For i = 1 , this injective matching makes every ﬁxed Γ-word preserve the transported compo-
nents p1(C) at almost every vertex. Since t1J t− 1
1 ≤ Γ, each J-generator is the conjugate by t− 1
1 of
an element of Γ. Conjugating the component-preservation statement by p− 1
1 therefore shows that
the J-generators preserve the original Γ-components at almost every vertex. The Γ-generators
already preserve these components. We can consequently select one original expanding compo-
nent on which the required multiplication, commutation, and distinctness tests all hold outside a
negligible set. Restrict the Γ- and J-generator actions to that component, complete their partial
permutations, discard a negligible set to restore uniform expansion, and complete the permutations
once more. The result is a soﬁc approximation of Γ × J on a single expander, so the Kun–Thom
theorem implies that J is LEF.
It remains to realize the hypotheses of Proposition 2.3 inside the concrete group G = EL D(R).
In Section 3 , we verify that G has property (T ), construct a property- (T ) subgroup Γ ≤ G, two
units u, v ∈ G, and a subgroup J ≤ G, and prove that
G = ⟨Γ, u, v⟩, u Γu− 1, v Γv− 1 ≤ Γ,
Γ × J ≤ G, uJ u − 1 ≤ Γ, J ∼= V.
Here Γ acts inside the cylinder [0], whereas J ∼= V acts inside the disjoint cylinder [1000]; conjuga-
tion by u moves J into the cylinder [0001] ⊆ [0]. Thompson’s group V is ﬁnitely presented, inﬁnite,
and simple [ CFP96], so it is not LEF [ VG97, Theorem 2.2]. If G were soﬁc, Proposition 2.3 applied
with t1 = u and t2 = v would nevertheless force J to be LEF. This contradiction proves that G,
and hence R× , is not soﬁc.
2. An expander-matching criterion
We ﬁrst isolate the part of the proof that does not depend on the binary Leavitt algebra.
Its purpose is to turn a soﬁc approximation consisting of many expanding components into an
approximation of a commuting direct product on one expanding component.
For a nonempty ﬁnite set Y , write
dH(p, q) = |{z ∈ Y : pz ̸= qz}|
|Y | (p, q ∈ Sym(Y )).
81
===== PAGE 84 =====
A soﬁc approximation of a countable group H consists of maps pn : H → Sym(Yn) satisfying
pn(1) = 1 , d H
(
pn(gh), pn(g)pn(h)
)
− → 0, d H
(
pn(g), 1
)
− → 1 ( g ̸= 1).
Here the multiplication condition holds for every g, h ∈ H. By taking disjoint copies, we may
assume that |Yn| → ∞ .
A group J is locally embeddable into ﬁnite groups , or LEF, if, for every ﬁnite F ⊆ J, there are
a ﬁnite group B and an injection ϕ : F → B such that
ϕ(xy) = ϕ(x)ϕ(y) ( x, y, xy ∈ F ).
Thus the multiplication table of F embeds exactly, although the ﬁnite group B may depend on
F .
For a graph L and U ⊆ V (L), let ∂LU be the set of edges joining U to V (L) \ U . If C is a
connected component of L, we also write ∂CU for the boundary of U ⊆ C in the induced graph on
C. Parallel edges are counted with multiplicity, while loops contribute nothing. Edge symmetric
diﬀerences are likewise counted with multiplicity. We call C a γ-expander if
|∂CU | ≥γ min{|U |, |C \U |} (U ⊆ C). (3)
Throughout this section, a ﬁnite symmetric generating set S = S− 1 ⊆ H includes the identity.
Normalize inverse labels to be inverse permutations, with the identity label acting exactly as
the identity. The corresponding S-labelled generator graph has vertex set Yn and an arc from
z to pn(s)z for every s ∈ S. Pair inverse arcs to obtain an undirected multigraph; ﬁxed points,
including the identity label, give loops. Parallel edges retain their multiplicities. All such graphs
have uniformly bounded degree. Adding identity loops does not change their edge boundaries, but
makes the associated random walk lazy, as in Kun’s property- (T ) argument.
The two external inputs diﬀer in a crucial respect: Kun’s theorem produces possibly many
expanders; the Kun–Thom theorem requires one expander on the entire approximation set.
Theorem 2.1 (Kun’s expander decomposition) . Let H be an inﬁnite ﬁnitely generated group with
property (T ), let S = S− 1 ⊆ H be a ﬁnite generating set containing 1, and let pn : H → Sym(Yn)
be a soﬁc approximation with |Yn| → ∞ . Write Xn for its S-generator multigraph. There are a
constant γ > 0 and unlabelled, uniformly bounded-degree multigraphs Ln on the same vertex sets
such that
|E(Xn)△ E(Ln)|= o(|Yn|)
and every connected component of Ln is a γ-expander.
This is the expander-decomposition conclusion of [ Kun19, Theorem 1], stated with the identity-
inclusive generator and multigraph conventions used in its property- (T ) argument. If a graph
convention suppresses identity loops, adjoin the same identity loop at every vertex of both graphs;
this changes neither their boundaries nor their edge symmetric diﬀerence. The reference graphs
are unlabelled: their edges need not retain the original generator labels, and decompositions for
diﬀerent generating families need not be compatible.
Theorem 2.2 (Kun–Thom’s expander-centralizer theorem) . Let K be a group with property (T ),
let J be a ﬁnitely generated group, and ﬁx a ﬁnite symmetric generating set SK ⊆ K of K
containing 1. Suppose that K × J has a soﬁc approximation pn : K × J → Sym(Yn). Write XK,n
for its SK-generator multigraph, and suppose that, for some λ > 0,
|∂XK,nU | ≥λ min{|U |, |Yn \U |} (U ⊆ Yn)
for every n. Then J is LEF.
We use the permutation-multigraph version of [ KT19, Theorem 1.1 and Section 4]; its boundary
counts repeated edges with multiplicity.
Proposition 2.3. Let Γ ≤ G be inﬁnite ﬁnitely generated groups with property (T ). Suppose that
G = ⟨Γ, t1, . . . , tm⟩, t iΓt− 1
i ≤ Γ (1 ≤ i ≤ m), m ≥ 1.
If a ﬁnitely generated subgroup J ≤ G satisﬁes
[Γ, J] = 1 , Γ ∩ J = {1}, t 1J t− 1
1 ≤ Γ,
82
===== PAGE 85 =====
then soﬁcity of G implies that J is LEF.
Proof. Assume that G is soﬁc, and ﬁx one approximation pn : G → Sym(Yn). By disjoint ampliﬁ-
cation, arrange that
N = |Yn| − → ∞ .
All o(N ) estimates refer to this same approximation. For readability, write pg = pn(g) and suppress
n from the graphs and partitions.
The hypotheses identify ΓJ with Γ × J and imply t1(ΓJ)t− 1
1 ≤ Γ. Our goal is to extract a soﬁc
approximation of Γ × J whose Γ-generator graph is one expander. We ﬁrst compare the expander
decompositions for Γ and G, then show that J almost preserves the Γ-components. Finally, we
select one such component and repair the restricted generator actions.
Step 1: Locate a dominant original component inside each transported component.
Choose a ﬁnite symmetric generating set SΓ for Γ containing 1. Adjoin the distinct nonidentity
elements among t± 1
i to obtain a symmetric generating set SG for G. For every inverse pair added in
this way, choose one of the original ti as its positive representative. Thus each positive nonidentity
G-generator either belongs to Γ or is one of the given compressing elements. Normalize inverse
labels to be inverse permutations and nonidentity involutive labels to be exact involutions, allowing
their o(N ) ﬁxed points; this changes only o(N ) vertices [ ES06, Lemma 2.1].
Apply Theorem 2.1 ﬁrst to the restricted soﬁc approximation of Γ, using SΓ, and then to the
soﬁc approximation of G, using SG. Denote the resulting reference graphs, component partitions,
and expansion constants by
reference graph connected components expansion constant
LΓ Q γΓ > 0
LG A γG > 0.
We call members of Q original components and members of A ambient components. Both partitions
concern the same vertex set, but neither is assumed to reﬁne the other. Each reference graph diﬀers
from its corresponding generator graph in o(N ) edges. Since LΓ has no edges between original
components, an SΓ-generator crosses between them on only o(N ) vertices. If w = s1 · · ·sr is a
ﬁxed Γ-word, write pw = ps1 · · ·psr . The same crossing estimate then holds for pw.
Set τi = pti. Transport the vertices and edges of LΓ through τi, obtaining
Ii = τiLΓ, Pi = {τiC : C ∈ Q}.
Each member of Pi is a γΓ-expanding connected component of Ii. Apart from o(N ) edited edges,
the edges of Ii follow the permutations τipsτ − 1
i , s ∈ SΓ. Approximate multiplicativity identiﬁes
each such permutation, outside o(N ) vertices, with a ﬁxed Γ-word representing tist− 1
i . Since these
words almost preserve the original components, we obtain
#{Ii-edges joining diﬀerent members of Q} = o(N ) (1 ≤ i ≤ m). (4)
For P ∈ P i, choose Q(P ) ∈ Q maximizing |P ∩ Q(P )|, and deﬁne its unmatched mass by
L(P ) = |P | − |P ∩ Q(P )|.
Partition P into the sets P ∩ Q, Q ∈ Q. If the largest part has more than half the vertices, apply
expansion to all other parts, whose total size is L(P ). Otherwise, every part has at most half the
vertices, so apply expansion to all of them. Each edge between diﬀerent parts is counted at most
twice, giving
γΓL(P ) ≤ 2#{Ii[P ]-edges joining diﬀerent members of Q}.
Together with ( 4), this gives ∑
P ∈P i L(P ) = o(N ). Choose ηn ↓ 0 suﬃciently slowly that, simulta-
neously for every i, ∑
P ∈P i
L(P )>ηn|P |
|P |= o(N ). (5)
For each i, all but o(N ) vertices belong to components of Pi whose unmatched mass is at most ηn
times their size. It remains to rule out several transported components selecting the same original
component.
83
===== PAGE 86 =====
Step 2: Use a bounded median normalization to compare component sizes.
For each vertex z, let C(z) ∈ Q be its original component and set
M (z) = |C(z)|.
Suppose that P = τiC satisﬁes L(P ) ≤ ηn|P |. For every z ∈ C with τiz ∈ P ∩ Q(P ),
M (τiz) = |Q(P )| ≥(1 − ηn)|P |= (1 − ηn)M (z).
By ( 5), the discarded components and the unmatched portions of the remaining components
occupy o(N ) vertices. Consequently,
M (τiz) ≥ (1 − ηn)M (z) outside o(N ) vertices (1 ≤ i ≤ m). (6)
For each s ∈ SΓ, we likewise have M (psz) = M (z) outside o(N ) vertices.
The values of M need not be uniformly bounded, so these exceptional sets cannot control its
total variation. For each ambient component A ∈ A, let mA > 0 be a median of the vertex-indexed
multiset (
M (z) : z ∈ A
)
.
Thus at least half of these values are at most mA, and at least half are at least mA. In particular,
an original component C contributes |C ∩ A|copies of |C|. Deﬁne
f (z) = M (z)
M (z) + mA
, z ∈ A.
Then 0 < f < 1, and 1/2 is a median of f on every A.
Every G-generator crosses between components of LG on only o(N ) vertices. On each remaining
generator arc, both endpoints use the same normalizing median mA. For s ∈ SΓ, this gives
f (psz) = f (z) outside o(N ) vertices. For a positive compressing generator ti, use ( 6) and
(1 − η)x
(1 − η)x + a ≥ x
x + a − η (x, a > 0, 0 ≤ η < 1).
Thus every positive G-generator s satisﬁes
f (psz) ≥ f (z) − ηn outside o(N ) vertices.
Because ps is a permutation, ∑
z∈Yn
(
f (psz) − f (z)
)
= 0.
The total decrease of f is at most ηnN + o(N ) = o(N ): the inequality above controls the nonex-
ceptional vertices, and 0 < f < 1 controls the exceptional ones. Since the displayed sum is zero,
the total increase equals the total decrease. Hence
∑
z∈Yn
|f (psz) − f (z)|= o(N ).
The same estimate holds for inverse generators. Summing over SG, and noting that changing one
edge aﬀects the total variation by at most one, therefore gives
∑
{z,w}∈E(LG)
|f (z) − f (w)|= o(N ). (7)
Expansion now forces f to concentrate near its median 1/2. Fix A ∈ A . The ﬁnite coarea
identity says that
∫ 1
0
⏐⏐∂A{z ∈ A : f (z) > t}
⏐⏐dt =
∑
{z,w}∈E(LG[A])
|f (z) − f (w)|.
Indeed, an edge {z, w} crosses the displayed level set precisely for levels between f (z) and f (w).
For 0 < t < 1/2, the set {z ∈ A : f (z) ≤ t} contains at most |A|/2 vertices; for 1/2 < t < 1,
the same holds for {z ∈ A : f (z) > t }. Apply ( 3) to these sublevel and superlevel sets, use that
complementary sets have the same boundary, and split the coarea integral at 1/2. This yields
γG
∑
z∈A
⏐⏐⏐f (z) − 1
2
⏐⏐⏐≤
∑
{z,w}∈E(LG[A])
|f (z) − f (w)|.
84
===== PAGE 87 =====
Summing over A and using ( 7), we obtain
∑
z∈Yn
⏐⏐⏐f (z) − 1
2
⏐⏐⏐= o(N ).
Choose δn ↓ 0 suﬃciently slowly that
En =
{
z :
⏐⏐⏐f (z) − 1
2
⏐⏐⏐> δ n
}
satisﬁes |En|= o(N ).
Since
M (z) = mA
f (z)
1 − f (z) (z ∈ A),
any z, w ∈ A \En satisfy
ρ− 1
n ≤ M (w)
M (z) ≤ ρn, ρ n =
( 1 + 2δn
1 − 2δn
) 2
− → 1. (8)
We have therefore shown that the sizes of original components meeting the same set A \En diﬀer
by a factor tending uniformly to one.
Step 3: Match the ﬁrst transported partition almost bijectively.
All ti were needed to control the full G-generator graph. To show that J preserves the original
components, however, we need only the ﬁrst transport. Set
τ = τ1, P = P1.
Retain a component P = τ C ∈ P precisely when
L(P ) ≤ ηn|P |
and there exists z ∈ C such that
τ z ∈ P ∩ Q(P ), z, τ z / ∈ En, z, τ z belong to the same A ∈ A. (9)
The last condition means that both vertices have the same median mA.
The vertices for which τ crosses between ambient components form a set
Hn = {z : z and τ z belong to diﬀerent members of A}
of size o(N ). Indeed, t1 is a ﬁxed word in SG, and each generator crosses A on only o(N ) vertices.
If P satisﬁes the loss bound but has no vertex as in ( 9), then
τ − 1(
P ∩ Q(P )
)
⊆ Hn ∪ En ∪ τ − 1(En).
The sets τ − 1(P ∩ Q(P )) are disjoint as P varies, and each has at least (1− ηn)|P |vertices when the
loss bound holds. Thus the components satisfying the loss bound but having no witness contribute
only o(N ) vertices. The components failing the loss bound contribute another o(N ) vertices by
(5). Therefore all nonretained components together contain o(N ) vertices.
For a retained P , choose z as in ( 9). Then
M (z) = |C|= |P |, M (τ z) = |Q(P )|.
The size comparison ( 8) gives
ρ− 1
n |P | ≤ |Q(P )| ≤ρn|P |.
Since at most ηn|P |vertices of P lie outside Q(P ), it follows that
|P △ Q(P )| ≤(ρn − 1 + 2ηn)|P |= o(|P |).
In particular, for all suﬃciently large n,
|P ∩ Q(P )|> 1
2 |Q(P )|.
Distinct transported components are disjoint, so they cannot both occupy a strict majority of
the same original component. Therefore P ↦→ Q(P ) is injective on retained components. The
nonretained components and unmatched portions of retained components together contain o(N )
vertices, so the matched intersections cover N − o(N ) vertices.
Fix a Γ-word w. Discard vertices outside the matched intersections, vertices whose pw-images lie
outside those intersections, and vertices for which pw crosses between original components. Each
85
===== PAGE 88 =====
discarded set has size o(N ). For every remaining vertex z, the vertices z and pwz lie in matched
intersections belonging to the same original component. Injectivity of the matching therefore puts
them in the same transported component. Thus
#{z : z and pwz lie in diﬀerent members of P} = o(N ). (10)
For each j ∈ J, choose a ﬁxed Γ-word wj representing t1jt− 1
1 , and put
qj = τ − 1pwj τ.
Approximate multiplicativity shows that qj agrees with pj outside o(N ) vertices. Moreover, τ qjz =
pwj τ z, and the transported component containing τ z is τ C(z). Hence z and qjz belong to the
same original component exactly when τ z and pwj τ z belong to the same transported component.
Applying ( 10) to wj therefore gives
#{z : C(qjz) ̸= C(z)} = o(N ). (11)
Thus, for every ﬁxed generator of either Γ or J, its approximating permutation preserves the
original-component partition outside o(N ) vertices. It remains to select one original component
and turn the restricted actions into an expanding approximation of Γ × J.
Step 4: Select one component carrying all required word tests.
Choose ﬁnite symmetric generating sets
TΓ = SΓ, T J ⊆ J \ {1}, T = TΓ ∪ TJ .
Thus 1 ∈ TΓ ⊆ T ; its generator permutation is the identity. The set TJ may be empty when J is
trivial. For s ∈ TΓ, deﬁne
qs = ps.
For j ∈ TJ , use the permutation qj constructed in Step 3. Normalize inverse labels and make
involutive J-labels exact by replacing all cycles of length greater than two with ﬁxed points.
These changes aﬀect o(N ) vertices and can alter any ﬁxed word test at only o(N ) starting vertices.
Since [Γ, J] = 1 and Γ ∩ J = {1}, multiplication identiﬁes Γ × J with its subgroup of G, and the
permutations qt satisfy its ﬁxed equality and distinctness tests outside o(N ) vertices.
For z ∈ Yn, recall that C(z) is its original component. Deﬁne the set of generator exits by
Cn = {z : C(qtz) ̸= C(z) for some t ∈ T }.
Every Γ-generator preserves the original components outside o(N ) vertices, while ( 11) applies to
every J-generator. Hence |Cn|= o(N ). Let ∆n consist of vertices incident to the edge-multiset
diﬀerence between the Γ-generator graph and LΓ. Then |∆n|= o(N ).
For ℓ ≥ 0, let Wℓ be the ﬁnite set of formal words in the alphabet T of length at most ℓ, including
the empty word. Diﬀerent formal words may represent the same group element. For w ∈ Wℓ, write
qw for the corresponding product of permutations and w ∈ Γ× J for the represented group element.
Words representing the same element should have the same endpoint, whereas words representing
distinct elements should have distinct endpoints. The vertices where either requirement fails form
Fn,ℓ =
⋃
w,w′∈Wℓ
w=w′
{z : qwz ̸= qw′z}
∪
⋃
w,w′∈Wℓ
w̸=w′
{z : qwz = qw′z}.
For ℓ ≥ 1, collect all exceptional vertices in the explicitly deﬁned set
Bn,ℓ = ∆ n ∪ Fn,ℓ ∪
⋃
w∈Wℓ− 1
q− 1
w (Cn).
The last term records word paths for which some generator step crosses between original compo-
nents. For each ﬁxed ℓ, we have |Bn,ℓ|= o(N ). Choose ℓn → ∞ suﬃciently slowly that
en = |Bn,ℓn|
N − → 0, B n = Bn,ℓn.
86
===== PAGE 89 =====
A veraging over all original components with weights |Q|yields a component Qn ∈ Q satisfying
|Qn ∩ Bn| ≤en|Qn| (12)
for every n. For each element of the word-metric ball in Γ, with generating set TΓ and radius
⌊ℓn/2⌋, choose a formal word of that length or shorter representing it. At any z ∈ Qn \Bn, the
exit tests keep every such word path inside Qn, and the distinctness tests give diﬀerent endpoints
for diﬀerent elements. Evaluating the chosen words at z therefore injects the entire word-metric
ball into Qn. Since Γ is inﬁnite, we have
|Qn| − → ∞ .
Step 5: Complete the partial actions and remove the additive expansion error.
We ﬁrst restrict the generator actions to the selected component and complete them to permu-
tations. The resulting generator graph is close to an expander but may fail to expand on very
small sets. Removing a small exceptional set and completing the restricted permutations a second
time will produce one uniformly expanding generator graph.
Set P = Qn, now an original component rather than a transported component. For one repre-
sentative of every nonidentity inverse pair in T , restrict qt to its internal arcs:
At = {z ∈ P : qtz ∈ P }, q t : At − → qt(At).
The omitted sets P \ At and P \ qt(At) have the same cardinality. Choose a bijection between
them to extend this partial bijection to a permutation ˆqt ∈ Sym(P ). For an involution, the missing
domain equals the missing range, and we complete it by ﬁxed points. Use ˆq− 1
t for the inverse label
and ˆq1 = id P for the identity label. Because
P \At ⊆ Cn ∩ P ⊆ Bn ∩ P,
(12) shows that only O(en|P |) values are changed. Every word path of length at most ℓn starting
in P \ Bn remains in P , so its equality, commutation, and distinctness tests are preserved. To
obtain maps on the whole group, choose once and for all a formal representative word wg for every
g ∈ Γ × J, with w1 empty and wt = t for every nonidentity t ∈ T , and set
ˆpn(g) = ˆqwg ∈ Sym(Qn).
For ﬁxed g, h, the equality tests compare wgh with the concatenation wgwh, and the distinctness
tests compare wg with the empty word when g ̸= 1 . Since ℓn → ∞ , these tests eventually apply,
and their exceptional proportions tend to zero. Therefore ˆpn is a soﬁc approximation of Γ × J on
Qn.
Let I0 be the TΓ-generator multigraph of ˆpn. Since ∆n ∪ Cn ⊆ Bn,
|E(I0)△ E(LΓ[P ])|= O|SΓ|(en|P |).
Here LΓ[P ] is precisely the original γΓ-expanding component on P . Consequently, for some an → 0,
|∂I0X| ≥γΓ min{|X|, |P \X|} −an|P | (X ⊆ P ). (13)
The additive error does not control small sets, so the current graph need not yet be an expander.
Fix 0 < λ < γ Γ. If there is a nonempty Bcut ⊆ P with
|Bcut| ≤ |P |
2 , |∂I0Bcut|< λ|Bcut|,
choose such a set of maximum cardinality; otherwise, set Bcut = ∅. Equation ( 13) implies
|Bcut| ≤ an
γΓ − λ |P |= o(|P |).
Put Z = P \ Bcut. We claim that, for all suﬃciently large n, the induced graph I0[Z] is a
λ-expander.
Let X ⊆ Z satisfy 0 < |X| ≤ |Z|/2. If |X|+ |Bcut| ≤ |P |/2, maximality of Bcut gives
λ(|X|+ |Bcut|) ≤ |∂I0(X ∪ Bcut)| ≤ |∂I0[Z]X|+ |∂I0Bcut|.
87
===== PAGE 90 =====
It follows that |∂I0[Z]X| ≥λ|X|. Otherwise,
|X|> |P |
2 − |Bcut|.
If d bounds the degrees of I0, ( 13) yields
|∂I0[Z]X| ≥γΓ|X| −an|P | −d|Bcut| ≥λ|X|
for all suﬃciently large n, because |Bcut|= o(|P |) and |X|= ( 1
2 − o(1))|P |. If Bcut is empty, the
same conclusion is immediate from its deﬁning maximality condition. This proves the claim.
The permutations ˆqt still act on P , not on Z. Restrict each one to
ˆqt : {z ∈ Z : ˆqtz ∈ Z} − → ˆqt
(
{z ∈ Z : ˆqtz ∈ Z}
)
.
The omitted domain and range inside Z again have equal cardinality, so extend this partial bijec-
tion to a permutation of Z. Again use ﬁxed points for an involution and inverse permutations for
inverse labels. The resulting ˜qt ∈ Sym(Z) diﬀers from the restriction of ˆqt on at most
|Bcut|= o(|P |) = o(|Z|)
vertices per generator. Every internal Γ-edge of I0[Z] is retained. Thus the Γ-generator multigraph
of (˜qt)t∈T contains I0[Z] as a spanning submultigraph. The additional completion edges cannot
decrease any edge boundary, so this generator graph is a λ-expander on the whole of Z.
For each ﬁxed word w, compare its path under the permutations ˆqt on P with its path under ˜qt
on Z. These paths can ﬁrst diﬀer only when a preﬁx encounters a repaired generator value. Since
each preﬁx acts by a permutation,
⏐⏐{z ∈ Z : ˜qwz ̸= ˆqwz}
⏐⏐≤ |w| |Bcut|.
Thus every ﬁxed equality, distinctness, and commutation test still fails on only o(|Z|) vertices. As
|Z|= (1 − o(1))|P | − → ∞ ,
the maps g ↦→ ˜qwg give a soﬁc approximation of Γ × J whose Γ-generator graph is one uniform
expander. Theorem 2.2 implies that J is LEF. □
3. The binary Leavitt configuration
We apply Proposition 2.3 inside the unit group of the noncommutative binary Leavitt algebra
R from ( 1). Its binary preﬁx structure supplies the contracting conjugations and the commuting
copy of Thompson’s group, while the Ershov–Jaikin-Zapirain theorem supplies property (T ) for
the elementary groups used in the construction. We construct these groups and then verify the
hypotheses of Proposition 2.3.
3.1. Preﬁx codes and elementary groups. Let W be the F2-vector space with one basis vector
eω for every inﬁnite binary string ω ∈ {0, 1}N. The formulas
sieω = eiω, t iejω = δijeω
satisfy the deﬁning relations of R. Thus si preﬁxes a string by i, whereas ti deletes that preﬁx
when present and otherwise gives zero. The operators sk
0 are distinct, so R is inﬁnite.
For a ﬁnite binary word a = i1 · · ·ir, set
sa = si1 · · ·sir , t a = tir · · ·ti1, e a = sata.
For the empty word, both products are 1. The cylinder [a] consists of the inﬁnite binary strings
beginning with a. A preﬁx code E = ( a1, . . . , aq) is a list of words none of which is a preﬁx of
another. It is complete if the cylinders [ai] partition all inﬁnite binary strings. Write eE = ∑
i eai.
The preﬁx-code identities
taisaj = δij, (saitaj )(sak tal) = δjk saital
follow from the incomparability of its words. Moreover, the Leavitt relation gives
ea = sa(s0t0 + s1t1)ta = ea0 + ea1.
88
===== PAGE 91 =====
Every ﬁnite complete preﬁx code is obtained from the one-word code consisting of the empty word
by repeatedly replacing a word a with its children a0, a1. The displayed identity therefore shows
that eE = 1 whenever E is complete. The preﬁx-code identities also give a ring isomorphism
ΘE : Mq(R) ∼− − →eEReE, (rij) ↦− →
∑
i,j
sairijtaj .
Its inverse sends x ∈ eEReE to (taixsaj )i,j. If E is complete, this identiﬁes Mq(R) with R.
Otherwise, a unit h in the corner extends to a unit of R as h + 1 − eE, acting identically outside
the cylinders in E.
In particular, deﬁne the elementary preﬁx group
ELE(R) =
⟨
1 + sair taj : i ̸= j, r ∈ R
⟩
≤ R× .
Indeed, the corner-unit extension satisﬁes
(1 − eE) + ΘE(Iq + rEij) = 1 + sair taj (i ̸= j),
so ELE(R) is the copy of ELq(R) acting identically outside the cylinders of E. We call its displayed
generators elementary E-roots.
Take the three preﬁx blocks
α = (000, 001, 01),
β = (1000, 1001, 101),
ν = (1100, 1101, 111),
D = (α1, α2, α3, β1, β2, β3, ν1, ν2, ν3).
(14)
Their cylinders partition [0], [10], and [11], respectively. Therefore D is a complete nine-leaf code,
whereas α covers only [0]. Set
G = EL D(R) ∼= EL9(R), Γ = EL α(R) ∼= EL3(R).
Since eα = e0, these identiﬁcations give
Γ =
{
1 − e0 + Θα(A) : A ∈ EL3(R)
}
=
{
ΘD(diag(A, I6)) : A ∈ EL3(R)
}
.
Thus the corner action is extended by the identity on the six complementary leaves, and every
elementary α-root is also a D-root. Consequently,
Γ ≤ G ≤ R× .
Both groups are inﬁnite: for distinct code leaves, the map
r ↦− →1 + sair taj
embeds the inﬁnite additive group of R into their corresponding elementary root subgroup.
The ring R is generated by {1, s0, s1, t0, t1}. For xij(r) = Iq + rEij, the identities
xij(r + r′) = xij(r)xij(r′), [xij(r), xjk (r′)] = xik(rr′) ( i, j, k distinct)
show that the elementary roots with these ﬁve coeﬃcients generate ELq(R) whenever q ≥ 3.
Thus G and Γ are ﬁnitely generated. Both have property (T ) by the Ershov–Jaikin-Zapirain
theorem [ EJ10, Theorem 1.1].
3.2. Copies of Thompson’s group. To deﬁne Thompson’s group V [CFP96], take two complete
preﬁx codes
E = (a1, . . . , aq), E ′= (b1, . . . , bq),
together with a bijection ai ↦→bi. Every inﬁnite binary string has a unique expression aiω, where
ai ∈ E and ω is its remaining inﬁnite tail. The corresponding preﬁx replacement acts by
g(aiω) = biω.
Thus it replaces the initial word ai by bi and leaves the inﬁnite tail unchanged. Since E′ is also
complete, this map is a bijection; its inverse replaces each bi by ai. Thompson’s group V consists
of all such preﬁx replacements.
For example, the complete codes
E = (0, 10, 11), E ′= (10, 0, 11)
89
===== PAGE 92 =====
give the replacement
g(0ω) = 10 ω, g (10ω) = 0 ω, g (11ω) = 11 ω.
It exchanges the cylinders [0] and [10] while ﬁxing [11].
We next realize V inside G, together with smaller copies inside Γ. In the standard Leavitt-
algebra realization [ BS16, Section 2.2], a preﬁx-replacement table g : E → E′ gives the element
Ug =
∑
a∈E
sg(a)ta, U g− 1 =
∑
a∈E
satg(a).
Because both codes are complete, the preﬁx-code identities give
UgUg− 1 = Ug− 1Ug = 1.
To see that this construction depends only on the represented preﬁx replacement, observe that
sbta = sb0ta0 + sb1ta1.
Thus replacing one table entry a ↦→b by the two entries a0 ↦→b0 and a1 ↦→b1 does not change Ug.
Any two tables representing the same preﬁx replacement have a common reﬁnement. Likewise,
given two replacements g and h, reﬁne the range code of g and the domain code of h until they
agree. The preﬁx-code identities then give
UhUg = Uh◦g, U id = 1.
Hence g ↦→Ug is a well-deﬁned homomorphism. Moreover, Ug sends eaω to eg(a)ω. Distinct preﬁx
replacements act diﬀerently on some basis vector, so their units are distinct. We therefore obtain a
faithful copy V ≤ R× . For a binary word l, write Vl ∼= V for the copy acting by preﬁx replacements
inside [l] and ﬁxing its complement. Its tables can be chosen to leave every complementary cylinder
unchanged, so
g − 1 ∈ elRel (g ∈ Vl). (15)
Lemma 3.1. We have V ≤ G. If l extends one of the three words αi, then Vl ≤ Γ.
Proof. For incomparable words ρ, σ, the unit
τρ,σ = 1 + eρ + eσ + sρtσ + sσtρ
exchanges the cylinders [ρ] and [σ] and ﬁxes their complement. These cylinder swaps generate
V [BQ17, Theorem 1.1].
Fix any preﬁx code E = ( a1, . . . , aq) with q ≥ 2. Suppose ﬁrst that ρ = aiw and σ = ajw′
extend diﬀerent leaves of this code. Then
P = sρtσ = sai(swtw′)taj , Q = sσtρ = saj (sw′tw)tai
make 1 + P and 1 + Q elementary E-roots. Since the coeﬃcient ﬁeld has characteristic two,
τρ,σ = (1 + P )(1 + Q)(1 + P ) ∈ ELE(R).
If instead both words extend the same leaf ai, choose a diﬀerent leaf aj. The transposition identity
τρ,σ = τρ,aj τσ,aj τρ,aj
again puts τρ,σ in ELE(R).
For the complete code D, choose k large enough that every ρw and σw, w ∈ {0, 1}k, extends a
leaf of D. Then
τρ,σ =
∏
w∈{0,1}k
τρw,σw ∈ ELD(R).
Hence V ≤ G. If l extends αi, the same-leaf argument with E = α puts every cylinder swap
supported on [l] in Γ, proving Vl ≤ Γ. □
90
===== PAGE 93 =====
3.3. T wo contractions and a commuting obstruction. We construct two preﬁx replacements
that send Γ into the same subgroup and together recover G. The three preﬁxes ζ = (100, 101, 11)
partition [1]. Deﬁne u, v ∈ V ≤ G by the tables
αi βi νi
u αi0 αi1 ζi
v αi0 ζi αi1
(1 ≤ i ≤ 3). (16)
Each column lists a source preﬁx, and an entry b below a source preﬁx a means that the replacement
sends aω to bω. The notation αi0 and αi1 means appending the indicated bit. In either row, the
six target cylinders [αi0], [αi1] partition [0], and the three cylinders [ζi] partition [1]. Thus both
rows are complete preﬁx replacements.
Both u and v send [αi] to [αi0]. Their other preﬁx images are
u([βi]) = [ αi1], u ([νi]) = [ ζi], v ([βi]) = [ ζi], v ([νi]) = [ αi1].
Deﬁne the obstruction group on the ﬁrst leaf of the β-block:
J = Vβ1 = V1000 ≤ G.
The group Γ acts only on [0], whereas J acts only on the disjoint cylinder [1000]. Figure 1 displays
these two supports inside the nine-leaf code.
000
α1
001
α2
01
α3
1000
β1
1001
β2
101
β3
1100
ν1
1101
ν2
111
ν3
0 1
Γ acts on [0]
J = Vβ1 = V1000
Figure 1. The nine-leaf preﬁx code. The blue, teal, and ochre blocks partition
[0], [10], and [11], respectively. The group Γ acts only on the blue block, while J
acts only on the violet leaf β1 in the teal block. Their supports are disjoint.
To verify the direct-product structure algebraically, the incomparability of 0 and 1000 gives
e0e1000 = e1000e0 = 0.
Every g ∈ Γ satisﬁes g − 1 ∈ e0Re0, while ( 15) gives j − 1 ∈ e1000Re1000 for every j ∈ J.
Orthogonality therefore implies
(g − 1)(j − 1) = ( j − 1)(g − 1) = 0 .
Thus g and j commute. Moreover, if g = j, then their common diﬀerence from 1 belongs to both
orthogonal corners and is therefore zero. Hence
[Γ, J] = 1 , Γ ∩ J = {1}, Γ × J ≤ G.
Thompson’s group V is ﬁnitely presented, inﬁnite, and simple [ CFP96]. Every ﬁnitely presented
LEF group is residually ﬁnite [ VG97, Theorem 2.2], whereas an inﬁnite simple group has no
nontrivial ﬁnite quotient. Thus J ∼= V is ﬁnitely generated but not LEF.
Proposition 3.2. The preﬁx replacements in (16) satisfy
uΓu− 1 = vΓv− 1 = EL (α10,α20,α30)(R) ≤ Γ, uJ u − 1 = V0001 ≤ Γ (17)
and
G = ⟨Γ, u, v⟩. (18)
91
===== PAGE 94 =====
Proof. For g = u, v, conjugating an elementary α-root gives
g(1 + sαir tαj )g− 1 = 1 + sαi0r tαj 0, i ̸= j, r ∈ R.
Thus both conjugates equal EL(α10,α20,α30)(R). This elementary preﬁx group lies in Γ, since
sαi0r tαj 0 = sαi(s0rt0)tαj .
Moreover, u sends β1 = 1000 to α11 = 0001 , so
uJ u− 1 = V0001 ≤ Γ
by Lemma 3.1. This proves ( 17).
To recover G, partition its six α- and β-leaves into three two-leaf blocks
Ci = {αi, βi} (1 ≤ i ≤ 3).
Set
Xi = sαit0 + sβit1, Y j = s0tαj + s1tβj .
The inverse preﬁx table for u gives
u− 1(1 + sαir tαj )u = 1 + XirYj (i ̸= j).
Write ℓi,0 = αi and ℓi,1 = βi. Given a matrix B = (bpq) ∈ M2(R), take
r =
∑
p,q∈{0,1}
spbpqtq.
Since tprsq = bpq, we obtain
XirYj =
∑
p,q∈{0,1}
sℓi,pbpqtℓj,q .
Taking a matrix with one nonzero entry produces every elementary root whose source and target lie
in diﬀerent blocks Ci and Cj. For any three distinct code leaves a, b, c, the elementary commutator
identity
[1 + sar tc, 1 + sctb] = 1 + sar tb
also supplies the roots between two leaves in the same block: choose c in any diﬀerent block, so
that both roots on the left join distinct blocks. Consequently,
EL(α,β)(R) ≤ ⟨Γ, u⟩.
The same argument with v and the three blocks {αi, νi} gives
EL(α,ν)(R) ≤ ⟨Γ, v⟩.
It remains to connect a β-leaf to a ν-leaf. For any such leaves a, b, choose an α-leaf c. Both
factors on the left-hand side of
[1 + sar tc, 1 + sctb] = 1 + sar tb
belong to the six-leaf groups just obtained. Interchanging a and b also gives the reverse elementary
root. Thus ⟨Γ, u, v⟩contains every elementary D-root, proving ( 18). □
Proof of Theorem 1.1. Proposition 3.2 shows that Γ ≤ G, J = V1000, t1 = u, and t2 = v satisfy
the hypotheses of Proposition 2.3. If G were soﬁc, Proposition 2.3 would make J LEF, which it
is not. Therefore G is not soﬁc. Since G ≤ R× and soﬁcity passes to subgroups, R× is not soﬁc
either. □
Acknowledgments. We thank Henry Bradford, Michael Chapman, Alon Dogon, and Francesco
Fournier-Facio for helpful comments on the manuscript.
92
===== PAGE 95 =====
References
[AL07] D. Aldous and R. Lyons, Processes on unimodular random networks , Electron. J. Probab. 12 (2007), 1454–
1508, arXiv:math/0603062.
[BQ17] C. Bleak and M. Quick, The inﬁnite simple group V of Richard J. Thompson: presentations by permutations ,
Groups Geom. Dyn. 11 (2017), 1401–1436, arXiv:1511.02123.
[BB20] L. Bowen and P. Burton, Flexible stability and nonsoﬁcity , Trans. Amer. Math. Soc. 373 (2020), 4469–4481,
doi:10.1090/tran/8047.
[BC25] L. Bowen and M. Chapman, Surjunctivity does not characterize cosoﬁcity of invariant random subgroups ,
preprint, 2025, arXiv:2511.06586.
[BCL V24] L. Bowen, M. Chapman, A. Lubotzky, and T. Vidick, The Aldous–Lyons conjecture I: Subgroup tests ,
preprint, 2024, arXiv:2408.00110.
[BCV25] L. Bowen, M. Chapman, and T. Vidick, The Aldous–Lyons conjecture II: Undecidability , preprint, 2025,
arXiv:2501.00173.
[BFF24] H. Bradford and F. Fournier-Facio, Hopﬁan wreath products and the stable ﬁniteness conjecture , Math. Z.
308 (2024), article no. 58, doi:10.1007/s00209-024-03589-3.
[BS16] N. Brownlowe and A. P. W. Sørensen, L2,Z ⊗ L2,Z does not embed in L2,Z, J. Algebra 456 (2016), 1–22,
doi:10.1016/j.jalgebra.2016.01.040.
[CFP96] J. W. Cannon, W. J. Floyd, and W. R. Parry, Introductory notes on Richard Thompson ’s groups , Enseign.
Math. (2) 42 (1996), no. 3–4, 215–256, available online.
[CDL24] M. Chapman, Y. Dikstein, and A. Lubotzky, Conditional non-soﬁcity of p-adic Deligne extensions: On a
theorem of Gohla and Thom , preprint, 2024, arXiv:2410.02913.
[DCGLT20] M. De Chiﬀre, L. Glebsky, A. Lubotzky, and A. Thom, Stability, cohomology vanishing, and nonapprox-
imable groups , Forum Math. Sigma 8 (2020), article no. e18, doi:10.1017/fms.2020.5.
[Dog23] A. Dogon, Flexible Hilbert–Schmidt stability versus hyperlinearity for property (T ) groups, Math. Z. 305
(2023), article no. 58, doi:10.1007/s00209-023-03387-3.
[DV26] A. Dogon and I. Vigdorovich, Hyperlinearity, stability and asymptotic spectral gap of higher rank lattices ,
preprint, 2026, arXiv:2506.20843v2.
[ES05] G. Elek and E. Szabó, Hyperlinearity, essentially free actions and L2-invariants: The soﬁc property , Math.
Ann. 332 (2005), 421–441, arXiv:math/0408400.
[ES06] G. Elek and E. Szabó, On soﬁc groups , J. Group Theory 9 (2006), 161–171, arXiv:math/0305352.
[EJ10] M. Ershov and A. Jaikin-Zapirain, Property (T ) for noncommutative universal lattices , Invent. Math. 179
(2010), 303–347, arXiv:0809.4095.
[Gel18] T. Gelander, A view on invariant random subgroups and lattices , in Proceedings of the International Con-
gress of Mathematicians—Rio de Janeiro 2018 , vol. II, World Scientiﬁc, 2018, 1339–1362, arXiv:1807.06979.
[GT24] L. Gohla and A. Thom, High-dimensional expansion and soﬁcity of groups , preprint, 2024, arXiv:2403.09582.
[Gro99] M. Gromov, Endomorphisms of symbolic algebraic varieties , J. Eur. Math. Soc. 1 (1999), 109–197.
[HO17] U. Haagerup and K. K. Olesen, Non-inner amenability of the Thompson groups T and V , J. Funct. Anal.
272 (2017), 4838–4852, doi:10.1016/j.jfa.2017.02.003.
[JNVWY20] Z. Ji, A. Natarajan, T. Vidick, J. Wright, and H. Yuen, MIP∗ = RE, preprint, 2020, arXiv:2001.04383.
[KT26] H. V. Khanh and V. H. Thanh, Matrix generators for the unit groups of LK (1, d), preprint, 2026,
arXiv:2607.10351.
[Kun19] G. Kun, On soﬁc approximations of property (T ) groups, preprint, 2019, arXiv:1606.04471v5.
[KT19] G. Kun and A. Thom, Inapproximability of actions and Kazhdan ’s property (T ),
preprint, 2019, arXiv:1901.03963.
[Lea62] W. G. Leavitt, The module type of a ring , Trans. Amer. Math. Soc. 103 (1962), 113–130, doi:10.1090/S0002-
9947-1962-0132764-X.
[Man25] A. Manzoor, Invariant random subgroups, soﬁcity, and Lück’s determinant conjecture , preprint, 2025,
arXiv:2508.15154.
[NT22] M. Nitsche and A. Thom, Universal solvability of group equations , J. Group Theory 25 (2022), 1–10,
arXiv:1811.07737.
[Pes08] V. G. Pestov, Hyperlinear and soﬁc groups: A brief guide , Bull. Symbolic Logic 14 (2008), 449–480,
arXiv:0804.3968.
[Tho08] A. Thom, Soﬁc groups and diophantine approximation , Comm. Pure Appl. Math. 61 (2008), 1155–1171,
arXiv:math/0701294.
[VG97] A. M. Vershik and E. I. Gordon, Groups that are locally embeddable in the class of ﬁnite groups , Algebra i
Analiz 9 (1997), no. 1, 71–97; English transl., St. Petersburg Math. J. 9 (1998), 49–67, Math-Net.Ru aa751.
[Wei00] B. Weiss, Soﬁc groups and dynamical systems , Sankhy¯ a Ser. A62 (2000), 350–359.
93
===== PAGE 96 =====
Chapter 4
A Counterexample to Connes’s Rigidity
Conjecture
Abstract. Connes conjectured that the group von Neumann algebra of an ICC
group with Kazhdan’s property (T ) determines the group up to isomorphism. We
disprove the conjecture by constructing a countably inﬁnite family of pairwise
nonisomorphic, mutually commensurable, ﬁnitely generated ICC property- (T )
groups with isomorphic group von Neumann algebras. The construction exploits
the fact that L∞ ( ˆA, m ˆA) depends on the underlying probability space, not on
the group law: binary carry produces diﬀerent compact abelian group structures
with the same Haar measure and group action. Our examples also answer Popa’s
ﬁnite-to-one question in the negative and attain his countability bound.
Contents
1. Introduction
2. Group factors, property (T ), and Fourier duality
3. A torsion-free property- (T ) acting group
4. The binary-carry construction
5. ICC, property (T ), and the basic counterexample
6. An inﬁnite ﬁber of the group-factor functor
References
94
===== PAGE 97 =====
1. Introduction
For a countable discrete group G, write L(G) for its group von Neumann algebra. A group
is ICC if it is inﬁnite and every nonidentity conjugacy class is inﬁnite; in this case, L(G) is a
II1 factor. Connes’s rigidity conjecture asks whether the group factor of an ICC property- (T )
group determines the group. It grew out of his foundational rigidity theorem [ Con80], goes
back to his Kingston proceedings article [ Con82], and appears explicitly as Problem 1 in his
1994 monograph [ Con94, Chapter 5, Appendix B, Problem 1, p. 551], where the group factor is
denoted by R(G).
Conjecture 1.1 (Connes). Let G and H be countable ICC groups with property (T ). If L(G) ∼=
L(H), then G ∼= H.
Theorem 1.2 (Main result) . There exist ﬁnitely generated ICC groups with property (T ),
Λ, Γ0, Γ1, Γ2, . . . ,
that are pairwise nonisomorphic and satisfy
L(Γn) ∼= L(Λ) ( n ≥ 0).
Moreover, for every n ≥ 0, the group Γn contains a subgroup isomorphic to Γ0 of index 24n. In
particular, the groups (Γn)n≥ 0 are mutually commensurable.
Consequences and context. As recorded in Corollary 5.10, the pair Λ, Γ0 already disproves
Connes’s conjecture. To establish this two-group result, it suﬃces to verify the ICC property and
property (T ) for Λ: both then transfer to Γ0 through the common group factor. The full family
in Theorem 1.2 additionally requires an intrinsic invariant to distinguish the groups Γn, and gives
a stronger negative result: even the ﬁnite-to-one weakening fails. In his Madrid ICM address,
Popa proved that the group-factor functor on ICC property- (T ) groups is at most countable-to-
one [ Pop07, Section 4, pp. 457–458]; an alternative proof appears in [ IPV13, Proposition 3.5].
He subsequently asked whether its ﬁbers must in fact be ﬁnite [ Pop13, p. 9]. Since L(Λ) has
countably inﬁnitely many pairwise nonisomorphic ICC property- (T ) group realizations, the
answer is negative and Popa’s countability bound is sharp.
The amenable case gives the opposite extreme: by Connes’s celebrated classiﬁcation theo-
rem for injective factors [ Con76], every amenable ICC group has the same group factor, the
hyperﬁnite II1 factor. Property (T ) [Kaz67] was expected to prevent this collapse.
The conjecture also belongs to the broader theory of W ∗-superrigidity. A countable group
G is W ∗-superrigid if L(G) ∼= L(H) implies G ∼= H for every countable group H. Fur-
man’s orbit-equivalence rigidity theorem provided an earlier analogue for probability-measure-
preserving actions of higher-rank lattices [ Fur99]. Popa introduced and developed deforma-
tion/rigidity theory, beginning with foundational work on Bernoulli shifts and rigid Cartan
inclusions [ Pop06a, Pop06b]. For suitable malleable actions of rigid groups, his strong-rigidity
theorems [ Pop06c, Pop06d] recover the acting group and its probability-space action from the
crossed product: a group-measure-space analogue of Connes’s conjecture. Ioana subsequently
proved W ∗-superrigidity for Bernoulli actions of ICC property- (T ) groups [ Ioa11]; this deter-
mines the action from its crossed product and does not assert rigidity of the bare group factor.
For accounts of the theory, see Popa’s ICM address [ Pop07] and the later surveys [ Vae10, Ioa18].
The ﬁrst W ∗-superrigid groups were constructed in [ IPV13]; the ﬁrst examples with property
(T ) followed in [ CIOS23]. Thus some ICC property- (T ) groups are indeed determined by their
group factors; what Theorem 1.2 disproves is that property (T ) alone guarantees this conclusion,
even up to ﬁnite ambiguity.
Inﬁnite ﬁbers were already known outside the property- (T ) setting. Indeed, as shown in
[IPV13, Theorem 1.2], for every nontrivial ﬁnite abelian group H0 and every n ≥ 3, there are
inﬁnitely many pairwise nonisomorphic groups H satisfying
L(H) ∼= L
(
H0 ≀PSLn(Z)
)
.
95
===== PAGE 98 =====
The ordinary wreath product on the right does not have property (T ). The new feature of
Theorem 1.2 is an inﬁnite ﬁber entirely within the ICC property- (T ) class, precisely the class
to which the countability bound applies.
Proof outline. For a countable abelian K-module A, Fourier transform gives
L(A o K) ∼= L∞ ( ˆA, m ˆA) o K.
The crossed product remembers the Haar probability space and its K-action, but need not
remember the compact group law on ˆA. Our strategy is therefore to put diﬀerent K-invariant
compact abelian group structures on a single probability space, and then to recover their diﬀer-
ences from the dual discrete groups.
Section 3 constructs a torsion-free ICC property- (T ) group
K = ker
(
SL4(Z[t])
g(t)↦→g(0) mod 3
− − − − − − − − − − − →SL4(F3)
)
surjecting onto SL4(F2[t]). For V = F2[t]4, the divided-square module
B = span F2{v ⊗ v : v ∈ V }, D = V ⊕ B,
supplies the common compact K-space ˆD = X × Y , where X = V ∗ and Y = B∗.
The elementary model for the construction is the four-point probability space F2
2. Coordi-
natewise addition gives the Klein four-group, whereas
(x, y) ⋄(x′, y′) = ( x + x′, y + y′+ xx′)
gives Z/4Z; both have the same uniform Haar measure. Section 4 globalizes this binary carry
to a compact group C0 with the same measured K-action as X × Y . Writing
Λ = D o K, Γ0 = ˆC0 o K,
Fourier transform identiﬁes L(Γ0) ∼= L(Λ), while order-four torsion distinguishes the two groups.
Section 5 proves that Λ is ICC and has property (T ). The ICC assertion follows from an
inﬁnite-orbit calculation. For property (T ), transitivity on primitive vectors and a quadratic
Boolean support bound give a uniform spectral estimate for the semidirect product. Both
properties then transfer to Γ0 through the common group factor.
Finally, Section 6 shifts the carry by n coeﬃcient positions in each of the four directions,
producing compact groups Cn with the same measured K-action. Their duals give
Γn = ˆCn o K, L (Γn) ∼= L(Λ).
Pontryagin duality embeds Γ0 in Γn with index 24n. The ﬁnite-orbit part of the intrinsic
quotient En[2]/2En, where En = ˆCn, also has order 24n, recovering n from the abstract group
and proving that the resulting family is pairwise nonisomorphic.
2. Group factors, property (T ), and Fourier duality
2.1. Group von Neumann algebras. Let G be a countable discrete group, and write U (H)
for the unitary group of a Hilbert space H. The left regular representation of G is
λG : G − → U (ℓ2(G)), λ G(g)δh = δgh.
The group von Neumann algebra of G and its canonical trace are
L(G) = λG(G)′′, τ G(x) = ⟨xδ1, δ1⟩.
For a ﬁnite sum x = ∑
g agλG(g), one has τG(x) = a1. A von Neumann algebra is a factor
if its center is C1; an inﬁnite-dimensional factor admitting a faithful normal tracial state is a
II1 factor. The group G is ICC if every nonidentity element has an inﬁnite conjugacy class.
For inﬁnite G, the group-factor criterion asserts that L(G) is a II1 factor if and only if G is
ICC [ MN43].
96
===== PAGE 99 =====
2.2. Property (T ). Let G be a countable discrete group and let π : G → U (H) be a unitary
representation. It has almost invariant unit vectors if, for every ﬁnite F ⊆ G and ε > 0, there
is a unit vector ξ ∈ H such that
max
g∈F
∥π(g)ξ − ξ∥ < ε.
The group G has property (T ) if every unitary representation with almost invariant unit vectors
has a nonzero invariant vector. Property (T ) passes to quotients and is preserved under passage
to ﬁnite-index subgroups and ﬁnite-index extensions. Every countable discrete property- (T )
group is ﬁnitely generated; see [ BHV08].
For a subgroup A ≤ G, the pair (G, A) has relative property (T ) if every unitary representation
of G with almost invariant unit vectors has a nonzero A-invariant vector. If A ◁ G, relative
property (T ) for (G, A), together with property (T ) for G/A, implies property (T ) for G.
Lemma 2.1. Let G and H be countable discrete groups such that L(G) ∼= L(H). If H is ICC
and has property (T ), then G is ICC and has property (T ).
Proof. Since H is ICC, L(H), and therefore L(G), is a II1 factor. The group-factor criterion
shows that G is ICC. By the Connes–Jones characterization [ CJ85], an ICC group has property
(T ) if and only if its group factor does. Applying this equivalence ﬁrst to H and then to G
proves the assertion. □
2.3. Pontryagin duality and crossed products. The algebra L∞ ( ˆA, m ˆA) depends only on
the Haar probability space of ˆA, not on its compact group law. Once the measure and the
K-action are ﬁxed, so is the crossed product.
Put T = {z ∈ C : |z|= 1}. For a locally compact abelian group A, write
ˆA = Hom cont(A, T)
for its Pontryagin dual, equipped with the compact-open topology. When A is countable and
discrete, ˆA is compact; denote its normalized Haar measure by m ˆA and its trivial character by 1.
If a countable discrete group K acts on A by automorphisms, the induced actions on characters
and functions are
(k ·χ)(a) = χ(k− 1 ·a), α k(f )(χ) = f (k− 1 ·χ).
The semidirect product A o K has multiplication (a, k)(b, h) = ( a + k ·b, kh). The corresponding
crossed product L∞ ( ˆA, m ˆA)oK is generated, in its standard representation, by L∞ ( ˆA, m ˆA) and
unitaries (vk)k∈K satisfying
vkf v∗
k = αk(f ), v kvl = vkl.
Under
ℓ2(A o K) ∼= ℓ2(A) ⊗ ℓ2(K),
Fourier transform in the A-coordinate identiﬁes the group unitaries of A with multiplication by
χ ↦→χ(a), and those of K with the unitaries implementing the dual action. Hence
L(A o K) ∼= L∞ ( ˆA, m ˆA) o K. (2.1)
In particular, let A′ be another countable discrete abelian K-module. A measurable bijection
modulo null sets θ : ˆA → ˆA′is measure-preserving and K-equivariant when
θ∗m ˆA = m ˆA′, θ (k ·χ) = k ·θ(χ) for every k ∈ K and almost every χ.
Then f ↦→f ◦θ− 1, together with the identity on the implementing unitaries, gives
L(A o K) ∼= L(A′o K).
No compatibility between the group laws on ˆA and ˆA′is required; this is the mechanism under-
lying our construction.
97
===== PAGE 100 =====
3. A torsion-free property- (T ) acting group
We need a torsion-free ICC property- (T ) group that surjects onto SL4(F2[t]). A congruence
condition at the diﬀerent prime 3 will provide torsion-freeness without losing the characteristic- 2
action. Deﬁne
K = ker
(
SL4(Z[t])
g(t)↦→g(0) mod 3
− − − − − − − − − − − →SL4(F3)
)
.
Set
R = F2[t], Q = SL 4(R).
The groups K and Q are countable.
For a commutative ring S, let
ELn(S) =
⟨
I + f Eij : f ∈ S, i ̸= j
⟩
≤ SLn(S),
where Eij is the (i, j)-matrix unit. Thus ELn(S) is the elementary linear group . Since Z is
a regular ring of Krull dimension 1 and SK1(Z) = 0 , the elementary generation theorem for
polynomial rings [ Sus77, Corollary 6.6] gives
ELn(Z[t]) = SL n(Z[t]) ( n ≥ 3).
Property (T ) for elementary linear groups over ﬁnitely generated unital rings [ EJ10, Theo-
rem 1.1] therefore gives property (T ) for SL4(Z[t]).
Proposition 3.1. The group K has property (T ).
Proof. Evaluation at t = 0 followed by reduction modulo 3 has ﬁnite image. Thus K has ﬁnite
index in SL4(Z[t]) and inherits property (T ). □
We use the following level- 3 congruence lemma [ Min87].
Lemma 3.2. For every d ≥ 2, the group
ker
(
SLd(Z) − → SLd(F3)
)
is torsion-free.
Proof. If the displayed group contains a nonidentity torsion element, it contains one of prime
order p. Write this element as
A = I + 3rB,
where r ≥ 1 is maximal, so B ̸≡0 (mod 3) . If p ̸= 3, then
I = Ap ≡ I + p3rB (mod 3 r+1),
contradicting B ̸≡0 (mod 3) . If p = 3, then
0 = A3 − I
3r+1 = B + 3rB2 + 32r− 1B3.
Reduction modulo 3 again gives B ≡ 0 (mod 3) , a contradiction. □
Lemma 3.3. The group K is torsion-free and ICC. Reduction modulo 2 gives a surjection
π2 : K ↠ Q.
Proof. For torsion-freeness, suppose g(t) ∈ K satisﬁes g(t)m = I for some m ≥ 1. Its constant
term g(0) is a torsion element of ker(SL4(Z) → SL4(F3)), so Lemma 3.2 gives g(0) = I. If g ̸= I,
let r ≥ 1 be its ﬁrst nonzero t-adic degree:
g(t) = I + trA(t), A (0) ̸= 0.
Since Z is an integral domain,
g(t)m ≡ I + mtrA(0) ̸≡I (mod tr+1),
contradicting gm = I.
For the ICC property, let
uij(f ) = I + 3f Eij ∈ K (i ̸= j, f ∈ Z[t]).
98
===== PAGE 101 =====
A matrix commuting with every Eij is scalar, and every scalar element of SL4(Z[t]) has ﬁnite
order. Thus, for a nonidentity g ∈ K, torsion-freeness provides i ̸= j such that
[Eij, g] = Eijg − gEij
is nonzero. If uij(f ) and uij(h) produce the same conjugate of g, then g commutes with uij(f − h),
and hence
3(f − h)[Eij, g] = 0 .
As Z[t] is an integral domain and [Eij, g] ̸= 0, we must have f = h. Varying f therefore produces
inﬁnitely many conjugates.
Finally, reduction modulo 2 gives
uij(f ) ↦− →I + ¯f Eij.
Every elementary matrix over R arises in this way. Since R is Euclidean, these matrices generate
Q = SL 4(R), proving that π2 is onto. □
Remark 3.4. Although the module and orbit calculations factor through Q, this group cannot
replace K:
u = I + E12 + E23 ∈ Q, u 2 = I + E13 ̸= I, u 4 = I,
so Q has an element of order 4. Torsion-freeness of K, by contrast, ensures that Λ has no
element of order 4, since D has exponent 2; this distinguishes Λ from Γ0 in Proposition 4.3. It
also identiﬁes En as the torsion subgroup of Γn, the intrinsic starting point for recovering n in
Proposition 6.9.
4. The binary-carry construction
The distinction between a measured space and its group law already appears on the four-point
set F2 × F2. Consider
(x, y) + (x′, y′) = ( x + x′, y + y′),
(x, y) ⋄(x′, y′) = ( x + x′, y + y′+ xx′),
with all coordinates on the right computed in F2. The ﬁrst law gives the Klein four-group; for
the second,
(x, y) ↦− →˜x + 2˜y (mod 4)
is an isomorphism with Z/4Z, where tildes denote representatives in {0, 1}. Both laws never-
theless have the same uniform Haar probability measure. Their diﬀerence is the binary carry
xx′.
We globalize this carry K-equivariantly. The resulting compact abelian group C0 admits a
K-equivariant, measure-preserving homeomorphism from X × Y = ˆD, but its group law is not
the coordinatewise one. Its Pontryagin dual E0 will deﬁne Γ0.
4.1. The common linear and quadratic modules. Let V = R4, let e1, . . . , e4 be its standard
basis, and put
e = e1, b (v) = v ⊗ F2 v.
Deﬁne
B = span F2{b(v) : v ∈ V } ⊆ V ⊗ F2 V, D = V ⊕ B.
The tensor product is over F2, not over R.
Let K act on V through π2 : K ↠ SL4(R). Its diagonal action on V ⊗ F2 V preserves B, since
k ·b(v) = b(k ·v),
and therefore acts on D. These are countable discrete F2-vector spaces, so D has exponent 2
and
0 − → V
v↦→(v,0)
− − − − − →D
(v,w)↦→w
− − − − − − →B − → 0
is a split K-equivariant exact sequence.
The polarization of b is bilinear:
b(u + v) − b(u) − b(v) = u ⊗ v + v ⊗ u.
99
===== PAGE 102 =====
For an ordered F2-basis (ui)i≥ 1 of V , a basis of B is
ui ⊗ ui, u i ⊗ uj + uj ⊗ ui (i < j ).
Indeed, if v = ∑
i xiui, then
b(v) =
∑
i
xi(ui ⊗ ui) +
∑
i<j
xixj(ui ⊗ uj + uj ⊗ ui).
Conversely,
ui ⊗ uj + uj ⊗ ui = b(ui + uj) + b(ui) + b(uj),
and linear independence follows from the tensor-product basis (ui ⊗ uj)i,j. These are precisely
the tensors ﬁxed by interchanging the two factors; thus
B = (V ⊗ F2 V )S2 = Γ 2
F2(V ),
the divided square of V . Crucially, this is the invariant subspace, not the ordinary symmetric-
square quotient
Sym2
F2(V ) = ( V ⊗ F2 V )S2.
Indeed, the canonical map from invariants to coinvariants kills every oﬀ-diagonal basis element
ui ⊗ uj + uj ⊗ ui.
For q ∈ B∗ = Hom F2(B, F2), the displayed expansion gives
q(b(v)) =
∑
i
xiq(ui ⊗ ui) +
∑
i<j
xixjq(ui ⊗ uj + uj ⊗ ui).
Thus B∗ parametrizes the Boolean quadratic functions on V with zero constant term: diagonal
coordinates supply the linear terms, and oﬀ-diagonal coordinates the quadratic terms. In par-
ticular, for every ﬁnite J ⊆ N, the restriction of v ↦→q(b(v)) to spanF2{uj : j ∈ J} is a Boolean
polynomial of degree at most 2.
Via
(ℓ, q) ↦− →
[
(v, w) ↦→(− 1)ℓ(v)+q(w)]
,
Pontryagin duality identiﬁes
ˆD = X × Y, X = V ∗ = Hom F2(V, F2), Y = B∗ = Hom F2(B, F2).
With their pointwise-convergence topologies, X and Y are compact products of copies of F2.
Thus ˆD = X × Y has coordinatewise addition and Haar probability measure
m = mX ⊗ mY .
The dual actions are
(k ·ℓ)(v) = ℓ(k− 1 ·v), (k ·q)(w) = q(k− 1 ·w).
4.2. The carry group. For a ∈ F2, let ˜a ∈ {0, 1} ⊂ Z denote its standard representative. For
(ℓ, q) ∈ X × Y , deﬁne Fℓ,q : V → Z/4Z by
Fℓ,q(v) = ˜ℓ(v) + 2 ^q(b(v)) (mod 4) ,
and set
C0 = {Fℓ,q : (ℓ, q) ∈ X × Y } ⊆ (Z/4Z)V .
Equip (Z/4Z)V with the product topology and C0 with the subspace topology. The K-action
is
(k ·F )(v) = F (k− 1 ·v).
It preserves C0, since k ·Fℓ,q = Fk·ℓ,k·q.
For s, s′∈ F2, the standard lifts satisfy the binary-carry identity
˜s + ˜s′= ^s + s′+ 2˜s ˜s′ (mod 4) .
For ℓ, ℓ′∈ X, set
rℓ,ℓ′ = (ℓ ⊗ ℓ′)|B ∈ Y.
100
===== PAGE 103 =====
Here (ℓ ⊗ ℓ′)(u ⊗ v) = ℓ(u)ℓ′(v). Since
rℓ,ℓ′(b(v)) = ℓ(v)ℓ′(v),
and the elements b(v) span B, the map (ℓ, ℓ′) ↦→rℓ,ℓ′ is symmetric, bilinear, and normalized:
rℓ,0 = r0,ℓ = 0. Bilinearity gives the cocycle identity
rℓ,ℓ′ + rℓ+ℓ′,ℓ′′= rℓ′,ℓ′′+ rℓ,ℓ′+ℓ′′.
Evaluation at any w ∈ B uses only ﬁnitely many coordinates of ℓ and ℓ′, so r is continuous for
the pointwise topologies. It is therefore a continuous, symmetric, normalized, K-equivariant
Y -valued 2-cocycle on X. Applying the binary-carry identity at each v ∈ V gives
Fℓ,q + Fℓ′,q′ = Fℓ+ℓ′, q+q′+rℓ,ℓ′. (4.2)
Thus C0 contains 0 and is closed under addition. Since the ambient group has exponent 4, every
F ∈ C0 has inverse − F = 3F ∈ C0; hence C0 is a subgroup.
Reduction modulo 2 recovers ℓ from Fℓ,q, and the remaining values q(b(v)) recover q, since
the b(v) span B. Hence (ℓ, q) ↦→Fℓ,q is a bijection under which pointwise addition becomes
(ℓ, q) ⋆0 (ℓ′, q′) =
(
ℓ + ℓ′, q + q′+ rℓ,ℓ′
)
.
Proposition 4.1. The set C0 is a compact subgroup of (Z/4Z)V . The map
Φ0 : X × Y − → C0, Φ0(ℓ, q) = Fℓ,q,
is a K-equivariant homeomorphism that identiﬁes the Haar measure of C0 with m. It is a
topological group isomorphism for ⋆0, but not for coordinatewise addition on X × Y = ˆD.
Proof. Each coordinate of Φ0 is continuous, and the preceding recovery argument shows that Φ0
is bijective. It is therefore a homeomorphism from the compact space X × Y onto its image in the
Hausdorﬀ group (Z/4Z)V ; in particular, C0 is compact and closed. The identity b(k ·v) = k ·b(v)
gives K-equivariance.
Under Φ0, translation by Fℓ′,q′ is the triangular map
(ℓ, q) ↦− →
(
ℓ + ℓ′, q + q′+ rℓ,ℓ′
)
.
This map preserves m: its ﬁrst coordinate is translation in X, and each ﬁber map is translation
in Y . Consequently, (Φ0)∗m is the Haar measure of C0.
Equation ( 4.2) identiﬁes Φ0 as a topological group isomorphism for ⋆0. It cannot be a
homomorphism for coordinatewise addition: if ℓ(e) = 1 , then rℓ,ℓ(b(e)) = 1 and Fℓ,0(e) = 1 .
Thus Fℓ,0 has order 4, whereas X × Y with coordinatewise addition has exponent 2. □
4.3. Dualizing the carry extension. The binary carry is invisible to the measured K-space
but survives Pontryagin duality as a nonsplit extension. Let E0 = ˆC0, written additively and
equipped with the dual K-action, so that biduality identiﬁes C0 canonically with ˆE0. For v ∈ V ,
deﬁne
ε(0)
v ∈ E0, ε (0)
v (F ) = iF (v),
where i = √ − 1. Since V is countable, C0 is compact metrizable and E0 is countable. Moreover,
4ε(0)
e = 0 , and any ℓ ∈ X with ℓ(e) = 1 gives ε(0)
e (Fℓ,0) = i. Thus ε(0)
e has order 4, exhibiting
the obstruction to splitting.
Lemma 4.2. There are K-equivariant exact sequences
0 − → Y − → ˆD = X × Y − → X − → 0,
0 − → Y
ȷ0
− − →C0
ρ0
− − →X − → 0,
whose Pontryagin duals are
0 − → V − → D = V ⊕ B − → B − → 0,
0 − → V ι0
− − →E0
σ0
− − − →B − → 0.
101
===== PAGE 104 =====
The sequences involving ˆD and D split K-equivariantly. The sequence involving E0 does not
split even as an extension of abelian groups; equivalently, the map ρ0 admits no continuous
homomorphic section. The maps for the carry extension satisfy
ȷ0(q) = F0,q, ρ 0(Fℓ,q) = ℓ, ι 0(v)(Fℓ,q) = ( − 1)ℓ(v).
The map σ0 is characterized by
η(F0,q) = ( − 1)q(σ0(η)) (η ∈ E0, q ∈ Y ),
and
2ε(0)
v = ι0(v), σ 0(ε(0)
v ) = b(v).
Proof. The sequences for ˆD and D split by their direct-sum decompositions. For the carry
sequence, ( 4.2) shows that ȷ0 and ρ0 are continuous homomorphisms with
ker ρ0 = {F0,q : q ∈ Y } = ȷ0(Y ).
Since ρ0(Fℓ,0) = ℓ, the sequence is exact; all its maps are K-equivariant. Pontryagin duality
gives the stated discrete extension, with σ0 obtained by restricting a character to ȷ0(Y ) and
using ˆY = B. For evaluation characters,
ε(0)
v (F0,q) = i2q(b(v)) = (− 1)q(b(v)),
so σ0(ε(0)
v ) = b(v). Since the b(v) span B, these characters also give surjectivity of σ0.
If σ0(η) = 0 , then η factors through C0/ȷ0(Y ) ∼= X; since ˆX = V , it equals ι0(v) for a unique
v ∈ V . Finally,
(
ε(0)
v (Fℓ,q)
) 2 = (− 1)Fℓ,q(v) = (− 1)ℓ(v),
which gives 2ε(0)
v = ι0(v).
If the discrete sequence split, then E0 ∼= V ⊕ B would have exponent 2, contradicting the
order-four element ε(0)
e . By Pontryagin duality, ρ0 therefore admits no continuous homomorphic
section. □
Deﬁne
Γ0 = E0 o K, Λ = D o K.
The common measured K-action identiﬁes the group factors; the order-four carry distin-
guishes the groups.
Proposition 4.3. There is an isomorphism
L(Γ0) ∼= L(Λ),
but Γ0 ̸∼= Λ.
Proof. Equation ( 2.1) and Proposition 4.1 give
L(Γ0) ∼= L∞ (C0, m) o K
∼= L∞ (X × Y, m) o K ∼= L(Λ).
Since K is torsion-free, every ﬁnite-order element of Λ = D oK lies in D, which has exponent
2. But ε(0)
e ∈ E0 ⊂ Γ0 has order 4. Hence Γ0 ̸∼= Λ. □
5. ICC, property (T ), and the basic counterexample
The goal of this section is the two-group counterexample of Corollary 5.10. Proposition 4.3
already shows that Γ0 and Λ are nonisomorphic but have isomorphic group von Neumann
algebras. By Lemma 2.1, it therefore suﬃces to prove that Λ is ICC and has property (T ).
These two properties reduce, respectively, to inﬁnite orbits on D and a uniform spectral estimate
on ˆD = X × Y .
102
===== PAGE 105 =====
5.1. The ICC property.
Lemma 5.1. Let an ICC group H act by automorphisms on an abelian group A. If every
nonzero element of A has an inﬁnite H-orbit, then A o H is ICC.
Proof. If h ̸= 1 , the conjugacy class of (a, h) maps onto the inﬁnite conjugacy class of h in H.
If h = 1 and a ̸= 0, then
(0, k)(a, 1)(0, k)− 1 = (k ·a, 1) ( k ∈ H).
The latter conjugacy class is inﬁnite because the H-orbit of a is inﬁnite. □
Since D = V ⊕ B, Lemma 5.1 reduces the ICC assertion to the following orbit calculation,
which will also distinguish the groups in Section 6.
Lemma 5.2. Every nonzero element of V ⊕ B has an inﬁnite Q-orbit.
Proof. Elementary transvections give inﬁnite orbits on V ; on its tensor square, specialization
in one tensor variable distinguishes the same transvections.
For v ∈ V \ {0}, choose j with vj ̸= 0 and i ̸= j. The transvections
gn = I + tnEij ∈ Q (n ≥ 1), g nv = v + tnvjei
give pairwise distinct vectors.
For B ⊆ V ⊗ F2 V , introduce separate variables for the tensor factors:
S = F2[t1, t2], V ⊗ F2 V ∼= (R ⊗ F2 R)16 ∼= S16, t 1 = t ⊗ 1, t 2 = 1 ⊗ t,
so g ∈ Q acts as g(t1) ⊗ g(t2). Given w ∈ S16 \ {0}, remove its largest common power of t2:
w = ta
2w0, w 0(t1, 0) ̸= 0.
Write
w0(t1, 0) =
4∑
j=1
ej ⊗ wj, w j ∈ F2[t1]4.
Choose j with wj ̸= 0 and i ̸= j, and set
z = (Eij ⊗ I)w0(t1, 0) ̸= 0, h r = I + trEij ∈ Q (r ≥ 1).
If hrw = hsw, cancel ta
2 and specialize t2 = 0. Since hr(0) = I in the second tensor factor, this
gives
(tr
1 + ts
1)z = 0.
As F2[t1]16 is torsion-free and z ̸= 0 , we obtain r = s. Every nonzero element of B therefore
has an inﬁnite orbit. Finally, for (v, w) ∈ V ⊕ B, use the equivariant projection to V if v ̸= 0 ,
and the preceding argument if v = 0 and w ̸= 0. □
Proposition 5.3. The group Λ is ICC.
Proof. Lemma 5.2 and the surjection K ↠ Q show that every nonzero element of D has an
inﬁnite K-orbit. Since K is ICC by Lemma 3.3, Lemma 5.1 shows that Λ = D o K is ICC. □
5.2. A spectral criterion for property (T ). The extension
1 − → D − → Λ − → K − → 1
has a property- (T ) quotient by Proposition 3.1. By the extension principle in Subsection 2.2,
it therefore suﬃces to prove relative property (T ) for (Λ, D). The following spectral criterion
combines these two steps: an invariant spectral measure satisfying a uniform detection estimate
must have an atom at the trivial character.
If π : A o H → U (H) is a unitary representation with A abelian, the joint spectral theorem
gives a unique projection-valued measure P on ˆA such that
π(a) =
∫
ˆA
χ(a) dP (χ) ( a ∈ A).
Its covariance relation is
π(h)P (U )π(h)− 1 = P (h ·U )
103
===== PAGE 106 =====
for every Borel set U ⊆ ˆA and h ∈ H.
An H-ﬁxed unit vector therefore induces an H-invariant scalar spectral probability measure,
and P ({1}) projects onto the A-ﬁxed subspace. The criterion is a spectral form of the relative-
property-(T ) criterion in [ CT11].
Lemma 5.4. Let a countable property-(T ) group H act by automorphisms on a countable abelian
group A. Suppose there are a ﬁnite set J ⊆ A and c > 0 such that every H-invariant Borel
probability measure µ on ˆA satisﬁes
∑
a∈J
∫
ˆA
|χ(a) − 1|2 dµ(χ) ≥ c
(
1 − µ({1})
)
. (5.1)
Then A o H has property (T ).
Proof. Suppose A o H does not have property (T ). Choose a unitary representation π with
asymptotically invariant unit vectors (ξn) but no nonzero invariant vector. For a Kazhdan pair
(F, κ) of H, let PH project onto HH . The Kazhdan estimate on (HH )⊥ gives
∥ξn − PH ξn∥ ≤ κ− 1 max
h∈F
∥π(h)ξn − ξn∥ − → 0.
Hence, after discarding ﬁnitely many terms,
ηn = PH ξn
∥PH ξn∥
are H-invariant and satisfy ∥ηn − ξn∥ → 0.
Let P be the spectral measure of π|A and deﬁne
µn(U ) = ⟨P (U )ηn, ηn⟩.
Covariance makes µn H-invariant. For every a ∈ J,
∥π(a)ηn − ηn∥ ≤ 2∥ηn − ξn∥+ ∥π(a)ξn − ξn∥ − → 0,
and hence ∫
ˆA
|χ(a) − 1|2 dµn(χ) = ∥π(a)ηn − ηn∥2 − → 0.
As J is ﬁnite, ( 5.1) forces µn({1}) → 1. Thus P ({1})ηn ̸= 0 for large n. This vector is A-ﬁxed
by deﬁnition of P ({1}), and H-ﬁxed by covariance, since the trivial character is H-ﬁxed. It is
therefore A o H-invariant, a contradiction. □
5.3. A quadratic Boolean estimate. Let F2 be the ﬁeld with two elements. For m ≥ 2,
every function p : Fm
2 → F2 has a unique multilinear polynomial representative; let deg p denote
its degree and supp(p) = {x ∈ Fm
2 : p(x) ̸= 0}.
Lemma 5.5. Let m ≥ 2. If a nonzero polynomial function p : Fm
2 → F2 has degree at most 2,
then
|supp(p)| ≥2m− 2.
Equivalently, p is nonzero on at least one quarter of the Boolean cube.
Proof. The assertion is immediate for m = 2. For m ≥ 3, write
p(x′, xm) = p0(x′) + xmp1(x′),
where deg p0 ≤ 2 and deg p1 ≤ 1. If p1 = 0, then p0 ̸= 0; induction gives
|supp(p)|= 2|supp(p0)| ≥2 ·2(m− 1)− 2 = 2 m− 2.
Suppose that p1 ̸= 0. A nonzero aﬃne-linear function on Fm− 1
2 is nonzero on at least 2m− 2 points:
it is either the constant function 1, or its two ﬁbers have equal size. For every x′ ∈ supp(p1),
exactly one of p(x′, 0) and p(x′, 1) is nonzero. Therefore
|supp(p)| ≥ |supp(p1)| ≥2m− 2. □
104
===== PAGE 107 =====
5.4. A uniform evaluation estimate. The spectral estimate comes from one K-orbit: tran-
sitivity makes detection at e equivalent to detection at any primitive vector, while Lemma 5.5
ensures that every nontrivial character is detected by many such vectors.
A vector v = (v1, . . . , v4) ∈ R4 is primitive if its coordinates generate the unit ideal. Let
P = {v ∈ R4 : (v1, v2, v3, v4) = R}.
For N ≥ 1, put
RN = span F2{1, t, . . . , tN − 1}, V N = R4
N .
Lemma 5.6. The action of K on P is transitive, and
|P ∩VN |= 7 ·24N − 3 + 1.
Equivalently,
|P ∩VN |
|VN | = 7
8 + 2− 4N .
Proof. Since π2 : K ↠ SL4(R) is onto, the K-orbits on V are the SL4(R)-orbits. As R is
Euclidean, elementary row reduction takes any primitive vector to e = (1 , 0, 0, 0), proving
transitivity.
Write PN = |P ∩VN |, with P0 = 0 . Partitioning VN \ {0} by the monic greatest common
divisor of the four coordinates gives
24N − 1 =
N − 1∑
d=0
2dPN − d.
Subtract twice the corresponding identity for N − 1:
PN = (2 4N − 1) − 2(24N − 4 − 1) = 7 ·24N − 3 + 1. □
For z = (ℓ, q) ∈ X × Y , deﬁne
z[v] = ( ℓ(v), q(b(v))) ∈ F2
2.
We say that v detects z if z[v] ̸= (0 , 0). The two bits are evaluated separately by (v, 0) and
(0, b(v)) in D = V ⊕ B; adding them in F2 would allow cancellation.
Lemma 5.7. If µ is a K-invariant probability measure on X × Y , then
µ{z : z[e] ̸= (0, 0)} ≥ 1
7
(
1 − µ({(0, 0)})
)
. (5.3)
Proof. By K-invariance, detection has the same probability at every primitive vector. Indeed,
set
pµ = µ{z : z[e] ̸= (0, 0)}.
Then
(k ·z)[k ·v] = z[v] = ⇒ µ{z : z[v] ̸= (0, 0)} = pµ (v ∈ P ).
Suppose z = (ℓ, q) is detected by some v ∈ VN . At least one of
v ↦− →ℓ(v), v ↦− →q(b(v))
is a nonzero Boolean polynomial on VN ∼= F4N
2 . The ﬁrst is linear and the second has degree at
most 2, since b(v) = v ⊗ v and q is linear. Lemma 5.5 therefore gives at least 24N − 2 detecting
vectors. By Lemma 5.6, exactly
|VN | − |P ∩VN |= 2 4N − 3 − 1
of them can be nonprimitive, so at least 24N − 3 + 1 primitive vectors detect z. Write
UN = {z : z[v] ̸= (0, 0) for some v ∈ VN }.
Integrating the pointwise count and using |P ∩VN |= 7 ·24N − 3 + 1 yields
pµ|P ∩VN | ≥(24N − 3 + 1)µ(UN ) ≥ 1
7 |P ∩VN |µ(UN ).
105
===== PAGE 108 =====
Since V = ⋃
N VN and the b(v) span B, the sets UN increase to (X × Y ) \ {(0, 0)}. Divide by
|P ∩VN |and let N → ∞ to obtain ( 5.3). □
Remark 5.8. The bound 1/7 = (1 /4 − 1/8)/(7/8) comes from restricting detection to primitive
vectors: a nonzero Boolean polynomial of degree at most 2 detects at least 1/4 of the cube,
while the nonprimitive vectors have asymptotic density 1/8.
More generally, in rank j ≥ 3, the nonprimitive vectors have asymptotic density 21− j. The
same argument gives the bound
cj = 1/4 − 21− j
1 − 21− j = 2j− 3 − 1
2j− 1 − 1 .
It is positive exactly when j ≥ 4, with c4 = 1 /7. Thus 4 is the smallest rank for which this
argument yields a spectral gap.
Proposition 5.9. The group Λ has property (T ).
Proof. Let µ be a K-invariant Borel probability measure on ˆD = X × Y , and choose
d1 = (e, 0), d 2 = (0, b(e)).
Writing 1S for the indicator of a set S, a character z = (ℓ, q) ∈ ˆD = X × Y satisﬁes
|z(d1) − 1|2 + |z(d2) − 1|2 ≥ 4 1{z[e]̸=(0,0)}.
After integration, Lemma 5.7 gives
2∑
j=1
∫
ˆD
|χ(dj) − 1|2 dµ(χ) ≥ 4
7
(
1 − µ({1})
)
.
Thus ( 5.1) holds with (A, H, J, c) = ( D, K, {d1, d2}, 4/7), proving property (T ) for Λ. □
These rigidity results and the common group factor now give the promised two-group coun-
terexample.
5.5. The basic counterexample.
Corollary 5.10 (Two-group counterexample). The groups Λ and Γ0 are nonisomorphic ICC
property-(T ) groups with isomorphic group von Neumann algebras.
Proof. Proposition 4.3 shows that the groups are nonisomorphic and that their group von Neu-
mann algebras are isomorphic. Propositions 5.3 and 5.9 show that Λ is ICC and has property
(T ). Applying Lemma 2.1 to the factor isomorphism gives the same properties for Γ0. □
6. An infinite fiber of the group-factor functor
To extend Corollary 5.10 to a countably inﬁnite ﬁber, we keep the measured K-space X × Y
ﬁxed and apply the same binary carry after shifting each of the four coordinate sequences
by n. The common measured action identiﬁes the resulting group factors; an intrinsic ﬁnite-
orbit invariant recovers the 4n carry-free coordinates. The groups Γn will also be pairwise
commensurable.
6.1. Pulling back the carry. For n ≥ 0, deﬁne
Tn : X − → X, (Tnℓ)(v) = ℓ(tnv).
The R-linearity of the K-action makes Tn continuous and K-equivariant. It is surjective: for
λ ∈ X, extend the functional tnv ↦→λ(v) on tnV to V . Its kernel is
Zn = {ℓ ∈ X : ℓ|tnV = 0} ∼= HomF2(V /tnV, F2), |Zn|= 2 4n.
For ℓ, ℓ′∈ X, put
cn(ℓ, ℓ′) = rTnℓ,Tnℓ′ ∈ Y.
Equip X × Y with the operation
(ℓ, q) ⋆n (ℓ′, q′) =
(
ℓ + ℓ′, q + q′+ cn(ℓ, ℓ′)
)
. (6.3)
106
===== PAGE 109 =====
To see the original four-point carry inside this formula, write
xi,j = ℓ(tjei), y i,j = q
(
b(tjei)
)
(1 ≤ i ≤ 4, j ≥ 0).
Since
cn(ℓ, ℓ′)
(
b(tjei)
)
= xi,j+nx′
i,j+n,
the diagonal coordinate pair (xi,j+n, yi,j) adds by
(x, y) ⋄(x′, y′) = ( x + x′, y + y′+ xx′).
This is exactly the Z/4Z carry from Section 4. The ﬁrst n coordinates xi,0, . . . , xi,n− 1 in each
of the four directions never enter the carry.
For n = 0, Proposition 4.1 identiﬁes this coordinate model with the function-space group C0
of Section 4 via Φ0(ℓ, q) = Fℓ,q. We use this as a standing identiﬁcation. For every n ≥ 0, write
Cn for X × Y equipped with ⋆n.
Lemma 6.1. For every n ≥ 0, the operation ⋆n makes Cn a compact abelian group with Haar
probability measure m. The group K acts by continuous automorphisms through the coordinate
action
k ·(ℓ, q) = ( k ·ℓ, k ·q),
which is independent of n.
Proof. The pulled-back carry cn is continuous, symmetric, bilinear, and K-equivariant. Its
cocycle identity makes ( 6.3) associative; symmetry makes it commutative. The identity and
inverse are (0, 0) and (ℓ, q + cn(ℓ, ℓ)), respectively. Thus Cn is a compact abelian group and the
coordinate K-action is by continuous automorphisms.
Translation by (ℓ′, q′) has the form
(ℓ, q) ↦− →
(
ℓ + ℓ′, q + q′+ cn(ℓ, ℓ′)
)
.
It translates X and then translates each Y -ﬁber. Hence it preserves m, which is therefore the
Haar measure of every Cn. □
At this point the measured K-space, and therefore the resulting group factor, no longer
depends on n. We must now recover the shifted carry from the compact group structure. Two
maps isolate its eﬀects: ρn describes the carry extension, while pn identiﬁes the 4n carry-free
coordinates.
Deﬁne
ρn : Cn − → X, ρ n(ℓ, q) = ℓ,
pn : Cn − → C0, p n(ℓ, q) = ( Tnℓ, q).
The ﬁrst map exhibits Cn as an extension of X by Y . Since cn(ℓ, ℓ′) = rTnℓ,Tnℓ′, the second is a
surjective, continuous K-equivariant homomorphism with
ker pn = Zn × {0}.
Thus pn forgets exactly the 4n carry-free bits. Its dual will give the ﬁnite-index inclusion in
Theorem 1.2.
A continuous linear section of Tn gives a noncanonical isomorphism of compact abelian groups
Cn ∼= C0 × (Z/2Z)4n.
For n > 0, this splitting is not K-equivariant: the carry-free coordinates cannot be separated
from the tail as K-modules. Subsection 6.5 shows that their K-action recovers n.
To recover the group structure forgotten by the common measure, set
En = ˆCn, Γn = En o K.
Under the standing identiﬁcation via Φ0, E0 and Γ0 agree with the groups deﬁned in Section 4.
To describe the extension dual to ρn, deﬁne, for v ∈ V ,
ιn(v)(ℓ, q) = ( − 1)ℓ(v).
107
===== PAGE 110 =====
For η ∈ En, deﬁne σn(η) ∈ B by
η(0, q) = ( − 1)q(σn(η)) (q ∈ Y ).
This uniquely determines σn(η), since restriction to {0} × Y is a character of Y and ˆY = B.
The next lemma makes the shifted carry visible on the dual side: every En retains the original
order-four elements, and their doubles record the shift tn.
Lemma 6.2. For every n ≥ 0, the group En is countable and ﬁts into the K-equivariant exact
sequence
0 − → V ιn
− − →En
σn
− − − →B − → 0. (6.7)
For v ∈ V , deﬁne
ε(n)
v = ε(0)
v ◦pn ∈ En.
Then
σn(ε(n)
v ) = b(v), 2ε(n)
v = ιn(tnv). (6.8)
In particular, ε(n)
e has order 4.
Proof. Pontryagin duality applied to the exact sequence of compact abelian K-groups
0 − → Y
q↦→(0,q)
− − − − − →Cn
ρn
− − − →X − → 0
gives ( 6.7); metrizability of Cn gives countability of En. The two formulas in ( 6.8) follow from
ε(n)
v (0, q) = ε(0)
v (F0,q) = ( − 1)q(b(v)),
(
ε(n)
v (ℓ, q)
) 2 = (− 1)(Tnℓ)(v) = (− 1)ℓ(tnv).
Since tne ̸= 0 and ιn is injective, ε(n)
e has order 4. □
The essential point is the factor tn in ( 6.8): the lift of b(v) doubles to ιn(tnv). Thus n
records where the carry begins. Subsection 6.5 will recover the 4n carry-free coordinates from
the ﬁnite-orbit part of En[2]/2En.
6.2. The common group factor. The compact group law depends on n, but the measured
K-space does not. Fourier transform therefore gives the same crossed product throughout the
family.
Proposition 6.3. For every n ≥ 0, there is an isomorphism
L(Γn) ∼= L(Λ).
Proof. By Lemma 6.1, the identity (Cn, m) → (X × Y, m) is a K-equivariant isomorphism of
probability spaces. Equation ( 2.1) therefore gives
L(Γn) ∼= L∞ (Cn, m) o K
∼= L∞ (X × Y, m) o K ∼= L(Λ). □
6.3. ICC and property (T ). Both rigidity properties transfer along the common group factor.
Proposition 6.4. For every n ≥ 0, the group Γn is ICC and has property (T ).
Proof. Propositions 5.3 and 5.9 show that Λ is ICC and has property (T ). Proposition 6.3
identiﬁes L(Γn) with L(Λ). The conclusion now follows from Lemma 2.1. □
108
===== PAGE 111 =====
6.4. Finite-index embeddings and commensurability.
Proposition 6.5 (Finite-index embeddings). For every n ≥ 0, the group Γn contains a subgroup
isomorphic to Γ0 of index 24n. Consequently, the groups (Γn)n≥ 0 are mutually commensurable.
Proof. Dualizing
0 − → Zn × {0} − → Cn
pn
− − − →C0 − → 0
gives a K-equivariant exact sequence
0 − → E0
p∗
n
− − − →En
resZn
− − − − →ˆZn − → 0, p ∗
n(η) = η ◦pn.
Here resZn(η) is the character ℓ ↦→η(ℓ, 0) of Zn. Hence p∗
n(E0) o K ∼= Γ0 is a subgroup of Γn
of index
|ˆZn|= |Zn|= 2 4n.
Since every Γn contains a ﬁnite-index copy of Γ0, the groups are mutually commensurable. □
6.5. Pairwise nonisomorphism. The parameter n is detected by the ﬁnite orbits on an in-
trinsic 2-torsion quotient. By ( 6.3), doubling in Cn is
2(ℓ, q) =
(
0, cn(ℓ, ℓ)
)
.
Hence Cn and En have exponent dividing 4. Since K is torsion-free, the torsion elements of
Γn = En o K form the characteristic abelian subgroup
Tor(Γn) = En.
For an abelian group A, write
A[2] = {a ∈ A : 2a = 0}, 2A = {2a : a ∈ A}.
Since 4En = 0, conjugation induces an intrinsic action of Γn/En on En[2]/2En. Deﬁne
i(Γn) =
⏐⏐{a ∈ En[2]/2En : |(Γn/En) ·a|< ∞}
⏐⏐.
Because En = Tor(Γn), this is an invariant of the abstract group. We will prove
i(Γn) = |V /tnV |= 2 4n,
so its ﬁrst two values are 1 and 16. The calculation proceeds through the doubling map on En,
with ιn and σn as in ( 6.7).
Lemma 6.6. There is a unique K-equivariant surjective F2-linear map
d : B − → V, d (b(v)) = v.
Proof. Fix an ordered F2-basis (ui)i≥ 1 of V . Using the corresponding basis for B from Subsec-
tion 4.1, deﬁne d by
ui ⊗ ui ↦− →ui, u i ⊗ uj + uj ⊗ ui ↦− →0 ( i < j ).
The expansion of b(v) gives d(b(v)) = v. Since the elements b(v) span B, this identity implies
surjectivity, uniqueness, and K-equivariance: d(k ·b(v)) = k ·v = k ·d(b(v)). □
Lemma 6.7. For every n ≥ 0 and η ∈ En,
2η = ιn
(
tnd(σn(η))
)
. (6.10)
Consequently,
2En = ιn(tnV ) and En[2] = σ− 1
n (ker d). (6.11)
Proof. Both sides of ( 6.10) are homomorphisms in η. By ( 6.8), they agree on ε(n)
v ; they both
vanish on ιn(V ). These elements generate En, since their images under σn span B and ker σn =
ιn(V ). This proves the identity.
Surjectivity of d and σn gives 2En = ιn(tnV ). Since multiplication by tn on V and ιn are
injective, ( 6.10) also gives En[2] = σ− 1
n (ker d). □
109
===== PAGE 112 =====
Now set
An = En[2]/2En.
For its ﬁnite-orbit subgroup, write
Aﬁn
n = {a ∈ An : K ·a is ﬁnite }.
Lemma 6.8. For every n ≥ 0, there is a K-equivariant exact sequence
0 − → V /tnV − → An − → ker d − → 0. (6.13)
The maps are
v + tnV ↦− →ιn(v) + 2En, η + 2En ↦− →σn(η).
Under the resulting identiﬁcation of V /tnV with its image in An,
Aﬁn
n = V /tnV, |Aﬁn
n |= 2 4n.
Proof. By ( 6.11), restriction of σn gives the exact sequence
0 − → V ιn
− − →En[2] σn
− − − →ker d − → 0.
Quotienting by 2En = ιn(tnV ) gives ( 6.13).
Every element of V /tnV has ﬁnite orbit. Conversely, if a ∈ An has nonzero image in ker d,
that image has inﬁnite K-orbit by Lemma 5.2 and K ↠ Q. Equivariance forces a to have
inﬁnite orbit as well. Thus Aﬁn
n = V /tnV , which has order 24n because V /tnV ∼= (R/(tn))4. □
Proposition 6.9. The groups (Γn)n≥ 0 are pairwise nonisomorphic.
Proof. An isomorphism Γn ∼= Γm preserves the characteristic torsion subgroup and hence in-
duces an isomorphism An ∼= Am intertwining the quotient-group actions. It therefore identiﬁes
their ﬁnite-orbit subgroups. Lemma 6.8 gives
24n = |Aﬁn
n |= |Aﬁn
m |= 2 4m,
so n = m. □
Proof of Theorem 1.2. Propositions 6.3 and 6.9 show that the Γn are pairwise nonisomorphic
and have group factors isomorphic to L(Λ). By Lemma 6.2, every Γn contains an element of
order 4, whereas Λ has none by Proposition 4.3. Thus Λ ̸∼= Γn for every n.
Propositions 5.3, 5.9, and 6.4 give the ICC and property- (T ) assertions. Since the groups are
countable, property (T ) also implies ﬁnite generation. Finally, Proposition 6.5 realizes Γ0 as a
subgroup of Γn of index 24n, so the Γn are mutually commensurable. □
Acknowledgments. We thank Sorin Popa for valuable comments on the historical context, the
countability theorem, and the ﬁnite-to-one question, and François Charles and Cyril Houdayer
for careful readings and helpful suggestions.
During the preparation of this manuscript, we learned of independent and concurrent work
by Shuoxing Zhou also establishing a counterexample to Connes’s rigidity conjecture, developed
in part with the assistance of GPT-5.6 Sol.
References
[BHV08] B. Bekka, P. de la Harpe, and A. Valette, Kazhdan ’s Property (T), New Mathematical Monographs 11,
Cambridge University Press, 2008.
[CIOS23] I. Chifan, A. Ioana, D. Osin, and B. Sun, Wreath-like products of groups and their von Neumann
algebras I: W ∗-superrigidity, Ann. of Math. (2) 198 (2023), no. 3, 1261–1303.
[Con76] A. Connes, Classiﬁcation of injective factors. Cases II1, II∞ , IIIλ, λ ̸= 1, Ann. of Math. (2) 104 (1976),
no. 1, 73–115.
[Con80] A. Connes, A factor of type II1 with countable fundamental group , J. Operator Theory 4 (1980), no. 1,
151–153.
[Con82] A. Connes, Classiﬁcation des facteurs , in Operator Algebras and Applications, Part 2 (Kingston, Ont.,
1980), Proc. Sympos. Pure Math. 38, American Mathematical Society, Providence, R.I., 1982, 43–109,
doi:10.1090/pspum/038.2/679497.
[Con94] A. Connes, Noncommutative Geometry, Academic Press, San Diego, 1994.
110
===== PAGE 113 =====
[CJ85] A. Connes and V. F. R. Jones, Property T for von Neumann algebras , Bull. London Math. Soc. 17
(1985), no. 1, 57–62.
[CT11] Y. Cornulier and R. Tessera, A characterization of relative Kazhdan property T for semidirect products
with abelian groups , Ergodic Theory Dynam. Systems 31 (2011), no. 3, 793–805.
[EJ10] M. Ershov and A. Jaikin-Zapirain, Property (T) for noncommutative universal lattices , Invent. Math.
179 (2010), no. 2, 303–347.
[Fur99] A. Furman, Orbit equivalence rigidity , Ann. of Math. (2) 150 (1999), no. 3, 1083–1108, Annals of
Mathematics.
[Ioa11] A. Ioana, W ∗-superrigidity for Bernoulli actions of property (T ) groups, J. Amer. Math. Soc. 24 (2011),
no. 4, 1175–1226, doi:10.1090/S0894-0347-2011-00706-6.
[Ioa18] A. Ioana, Rigidity for von Neumann algebras , in Proceedings of the International Congress of Mathe-
maticians 2018 , Vol. III, World Scientiﬁc, 2018, 1639–1672.
[IPV13] A. Ioana, S. Popa, and S. Vaes, A class of superrigid group von Neumann algebras , Ann. of Math. (2)
178 (2013), no. 1, 231–286.
[Kaz67] D. A. Kazhdan, Connection of the dual space of a group with the structure of its closed subgroups ,
Funct. Anal. Appl. 1 (1967), no. 1, 63–65.
[Min87] H. Minkowski, Ueber den arithmetischen Begriﬀ der Aequivalenz und über die endlichen Gruppen lin-
earer ganzzahliger Substitutionen , J. Reine Angew. Math. 100 (1887), 449–458.
[MN43] F. J. Murray and J. von Neumann, On rings of operators. IV , Ann. of Math. (2) 44 (1943), 716–808.
[Pop06a] S. Popa, Some rigidity results for non-commutative Bernoulli shifts , J. Funct. Anal. 230 (2006), no. 2,
273–328.
[Pop06b] S. Popa, On a class of type II1 factors with Betti numbers invariants , Ann. of Math. (2) 163 (2006),
no. 3, 809–899.
[Pop06c] S. Popa, Strong rigidity of II1 factors arising from malleable actions of w-rigid groups, I , Invent. Math.
165 (2006), no. 2, 369–408.
[Pop06d] S. Popa, Strong rigidity of II1 factors arising from malleable actions of w-rigid groups, II , Invent. Math.
165 (2006), no. 2, 409–451.
[Pop07] S. Popa, Deformation and rigidity for group actions and von Neumann algebras , in Proceedings of
the International Congress of Mathematicians (Madrid, 2006) , Vol. I, European Mathematical Society,
Zürich, 2007, 445–477, doi:10.4171/022-1/18.
[Pop13] S. Popa, Some open problems in W ∗-rigidity, problem list, Paris, June 2013, https://www.math.ucla.
edu/~popa/ProblemsJune2013.pdf.
[Sus77] A. A. Suslin, On the structure of the special linear group over polynomial rings , Math. USSR-Izv. 11
(1977), no. 2, 221–238.
[Vae10] S. Vaes, Rigidity for von Neumann algebras and their invariants , in Proceedings of the International
Congress of Mathematicians (Hyderabad, India, 2010) , Vol. III, Hindustan Book Agency, 2010, 1624–
1650, arXiv:1008.3610.
111
===== PAGE 114 =====
Chapter 5
Circuit and Formula Lower Bounds for the
Permanent
Abstract. We study the exact symbolic computation of the n×n permanent
over C by arithmetic circuits and formulas. We prove two lower bounds.
•Division-free circuits with unrestricted reuse of intermediate values require
Ω(n2 log log n) arithmetic gates.
•Arithmetic formulas require Ω(n4/ log n) variable-labeled leaves, even when
division is allowed provided all denominators are nonzero rational functions.
The proof of the circuit lower bound constructs an aﬀine specialization whose
gradient vanishes on a suﬀiciently low-dimensional set, then combines simulta-
neous differentiation with a geometric degree bound. The formula lower bound
proof identifies many algebraically independent coeﬀicients associated with a
short matching of matrix entries and adds the resulting requirements over entry-
disjoint matchings. We also explain how both arguments use properties of the
permanent and do not directly imply a similar result for the determinant.
Contents
1. Introduction
2. Overview of the circuit lower bound
3. Overview of the formula lower bounds
4. A geometric circuit bound
5. Critical loci of minor sums
6. An aﬀine specialization of the permanent
7. Circuit parameters and the lower bound
8. Coeﬀicient transcendence degree
9. Independent coeﬀicients from a matching
10. Formula lower bounds with and without division
11. Comparison with the determinant
12. Related work
References
112
===== PAGE 115 =====
1. Introduction
Fix an integer n≥1, and let X = (xij)i,j∈[n] be an n×n matrix of algebraically independent
variables over C, where [j] ={1, . . . , j }. The permanent of X is the polynomial
pern(X) =
∑
σ∈Sn
n∏
i=1
xi,σ(i).
Here Sn is the set of permutations of [n]. Thus a monomial of pern chooses exactly one entry
from each row and each column; equivalently, it records a perfect matching in the complete
bipartite graph on the row and column indices. The closely related determinant is
detn (X) =
∑
σ∈Sn
sgn(σ)
n∏
i=1
xi,σ(i),
which differs from the permanent only through the signs of its monomials. Nevertheless, the
determinant has polynomial-size arithmetic circuits [ Ber84], whereas the permanent is complete
for Valiant’s class VNP [Val79a]. Understanding whether the permanent admits polynomial-
sized algebraic circuits is the central problem in algebraic complexity theory [ BCS97, SY10].
Throughout, “compute” means compute the polynomial exactly as a formal expression over
C, not merely evaluate it on a particular input matrix. An arithmetic circuit is a finite directed
acyclic graph with input gates labeled by individual variables or arbitrary complex constants,
binary internal gates labeled by +,−, or ×, and one designated output gate. Intermediate
values may be reused arbitrarily: a gate can feed its output to any number of later gates.
The circuit is division-free, and its size is the number of arithmetic gates; input gates are not
counted. We write C(f ) for the minimum size of a circuit whose output is the polynomial f .
There are no restrictions on depth, intermediate degrees, fan-out, or cancellations.
An arithmetic formula has the same kinds of inputs and binary arithmetic gates, but its
underlying computation is a rooted tree. Consequently, two uses of the same intermediate
polynomial must be computed by separate subformulas. For a formula Φ, let L(Φ) be its
total number of leaves, let Lvar(Φ) count only the leaves labeled by variables, with repeated
occurrences counted separately, and let G(Φ) be its number of internal arithmetic gates. A
formula with division additionally permits ÷gates and is interpreted in the rational-function
field C(xij : i, j∈[n]). Such a formula is valid if every denominator is a nonzero element of
this field. Its final output is required to equal the polynomial being computed; in particular,
intermediate rational functions need not themselves be polynomials.
The permanent depends on all N = n2 matrix variables, giving the elementary Ω(N ) circuit
lower bound. The classical division-free formula lower bounds for the permanent and determi-
nant are Ω(n3) [KS14, §3.2, Thm. 5]; for the determinant, Kalorkoti’s cubic lower bound holds
even when division is allowed [ Kal85]. Our first result improves the unrestricted, division-free
circuit lower bound specifically for the permanent.
Theorem 1.1. For every n≥216,
(1.1) C(pern)≥n2
144
(
log2 log2 n−3
)
.
In particular, C(pern) = Ω( n2 log log n) and C(pern)/n 2−→∞.
The next result concerns the more restrictive formula model. Its primary measure is the
number of variable occurrences, which also lower-bounds the total number of leaves and vertices.
Theorem 1.2. If n≥32 and a division-free arithmetic formula Φ computes pern, then
Lvar(Φ)≥ n4
128 log2 n , G (Φ)≥ n4
256 log2 n .
The variable-leaf bound also holds for the total numbers of leaves and vertices.
The same asymptotic variable-occurrence bound remains true when a formula may use valid
divisions; the explicit constants change.
113
===== PAGE 116 =====
Theorem 1.3. If n≥32 and a valid arithmetic formula Φ with division computes pern, then
Lvar(Φ)≥ n4
192 log2 n , G (Φ)≥ n4
384 log2 n .
Again, the variable-leaf bound holds for the total numbers of leaves and vertices.
In terms of the N = n2 input variables, the circuit bound is Ω(N log log N ), and both for-
mula bounds are Ω(N 2/ log N ). The circuit and formula results use different arguments: circuits
permit eﬀicient simultaneous computation of first derivatives because intermediate values can
be reused, whereas the formula bounds charge algebraically independent coeﬀicients to dis-
tinct occurrences of selected input variables. The permanent-specific inputs required by these
arguments are not available for the determinant; § 11 identifies both obstructions.
2. Overview of the circuit lower bound
Our circuit lower bound combines a geometric measure of polynomial complexity with a
permanent-specific construction. The measure applies to a homogeneous polynomial whose
gradient vanishes on a suﬀiciently small set; the construction realizes such a polynomial by
fixing and identifying inputs of pern. We describe both components, illustrate the necessary
cancellation on a four-by-four permanent, and give complete proofs in § 4–§7.
Stage 1: Many solutions force many multiplication gates. Consider the homogeneous
polynomial
H(z1, . . . , z k) = 1
d
k∑
i=1
zd
i , ∇H(z) = ( zd− 1
1 , . . . , z d− 1
k ), d ≥2.
For a target whose coordinates are all nonzero, the gradient has (d−1)k distinct preimages. If
aﬀine operations are free, a circuit using q multiplication gates describes the same fiber by q
quadratic gate equations and k aﬀine output equations. Bézout’s inequality bounds its number
of isolated solutions by 2q. Reverse-mode differentiation computes the gradient of a size- L
circuit with at most 3L multiplications [ BS83]. Consequently,
(d−1)k≤23L, L ≥k log2(d−1)
3 .
Section 4 supplies the full gate-equation and reverse-mode differentiation arguments.
The advantage of this argument is that it does not require the coordinates of the gradient to
be individual powers. The same solution count holds for any homogeneous map F : Ck→Ck
of degree d−1 whose only zero is the origin: its generic fiber consists of (d−1)k points. This
extension, proved in Lem. 4.1, is what allows the degree argument to apply to a polynomial
obtained from the permanent.
Stage 2: A small critical locus produces the required gradient map. Let P ∈
C[x1, . . . , x m] be a homogeneous polynomial of degree d. Its critical locus is
Crit(P ) ={x∈Cm : ∂P/∂x 1 =···= ∂P/∂x m = 0}.
Its dimension measures the number of freely varying coordinates in the common zero set; its
codimension is m−dim Crit(P ). In particular, a critical locus of codimension at least k is small
enough for a generic k-dimensional linear subspace to meet it only at the origin.
Choose a linear injection W : Ck→Cm whose image is such a subspace. Then ∇P (W u)̸= 0
whenever u̸= 0. A second generic linear map A : Cm→Ck preserves this nonvanishing on the
entire family of gradient directions. Therefore
F (u) = A∇P (W u)
is a homogeneous degree- (d−1) map from Ck to itself with F − 1(0) ={0}. Lem. 4.2 justifies the
two generic choices. Linear maps cost no multiplications, so combining slicing, reverse-mode
differentiation, and the preceding Bézout bound gives
L≥k log2(d−1)
3
114
===== PAGE 117 =====
for any circuit computing P . Proposition 4.3 records the same implication when P is a nonzero
scalar multiple of an aﬀine specialization of pern: replacing the permanent’s inputs by aﬀine
linear forms transfers its circuit to P without adding multiplication gates.
To obtain a superquadratic lower bound, it therefore suﬀices to construct a degree- d special-
ization with d growing with n and with k = Θ(n2). A direct application to the full permanent
does not supply the needed codimension. The remaining stages construct a different specializa-
tion whose critical locus can be controlled.
Stage 3: Control the critical locus of a sum of subpermanents. For a t×s matrix
X = (xia) and 3≤d≤min{t, s}, define
Mt,s,d(X) =
∑
I⊆ [t], J⊆ [s]
|I|=|J|=d
per(XI,J ).
Thus Mt,s,d sums the weights of all size- d matchings between t row vertices and s column
vertices. It is homogeneous of degree d in ts variables.
For each nonempty subset B⊆[t], introduce the power sum
pB(X) =
s∑
a=1
∏
i∈B
xia.
There are 2t−1 such quantities, shared by every column. To differentiate Mt,s,d with respect to
xia, first insist that row i is matched to column a. The remaining d−1 rows must be matched
injectively to columns other than a. Inclusion–exclusion on partitions expresses this injectivity
requirement as a polynomial in the pB(X) and the entries of column a.
Section 5 uses these derivative equations together with the first d−2 elementary symmetric
functions of each column. Once the 2t−1 shared power sums and these s(d−2) additional
quantities are specified, the critical-point equations leave only finitely many possibilities for
the column entries. Algebraically, those equations reduce every (d−1)st power of a column
coordinate to expressions of lower column degree. Repeated reduction makes the coordinate
algebra finite over the ring generated by the specified quantities. This yields the dimension
bound
dim Crit(Mt,s,d)≤2t−1 + s(d−2).
If b copies occupy disjoint variable blocks and receive nonzero scalar weights, their critical loci
form a Cartesian product. Corollary 5.2 therefore bounds the resulting dimension by
b
(
2t−1 + s(d−2)
)
.
Stage 4: Realize the desired block polynomial inside the permanent. Partition r = bt
rows into blocks R1, . . . , R b of size t, and let X be an r×s matrix of variables. We want the
polynomial
P (X) =
b∑
h=1
λhMt,s,d(XRh,[s]), λ h̸= 0,
so that the preceding critical-locus estimate applies. The challenge is to realize this specific sum
as one permanent, rather than as a separate sum of circuits.
A four-by-four cancellation example. The required block-selective cancellation is already visible
in
per


u v 1 1
w z 1 1
p q 2 −2
r s 2 −2

=−8(uz + vw) + 2(ps + qr).
Expand according to the two rows assigned to the first two columns. If both chosen rows belong
to the upper block, their variable contribution is per ( u vw z ) = uz + vw, while the complementary
constant block has permanent
per
(2 −2
2 −2
)
=−8.
115
===== PAGE 118 =====
If both chosen rows belong to the lower block, the variable contribution is ps + qr, and the
complementary constant block has permanent
per
(1 1
1 1
)
= 2.
If one chosen row comes from each block, the complementary constant block likewise contains
one row of each type, and its permanent vanishes:
per
(1 1
2 −2
)
=−2 + 2 = 0 .
Thus every mixed-block contribution cancels, leaving precisely the two within-block permanents.
The example has degree d = 2 , so log2(d−1) = 0 and it cannot itself produce a useful circuit
lower bound. Its purpose is to exhibit the cancellation that the general construction must
reproduce at a larger degree.
The general specialization. Lemma 6.1 constructs a constant r×(r−d) matrix U for which
B(X) =
(X U
1 0
)
is square of size r + s−d; the bottom-left all-ones block has s−d rows. Every nonzero term
of per(B(X)) chooses exactly d entries from X. The contribution of a chosen set of d variable
rows is controlled by a complementary permanent of U .
The columns of U are chosen using dth roots of unity. In commuting square-zero variables
z1, . . . , z r, write yh =∑
i∈Rh zi. For h≥2, set Y = y1 +···+ yh− 1, and let ζ be a primitive dth
root of unity. The corresponding root-of-unity product has the form
d− 1∏
j=0
(Y + 2ζjyh) = Y d + (−1)d+12dyd
h.
Combining these factors across the blocks forces every contributing set of d variable rows to lie
entirely inside a single Rh; choices meeting several blocks cancel. All surviving block weights
are nonzero. Thus per(B(X)) is a nonzero scalar multiple of P (X). Section 6 proves the
construction and computes its nonzero block weights.
Stage 5: Choose the degree and count the surviving variables. Section 7 takes
d =
⌊log2 n
4
⌋
, t = 4d, b =
⌊n
2t
⌋
, r = bt, s = n−r + d.
Then B(X) has size n and X contains m = rs = Θ( n2) independent variables. The choice
t≤log2 n keeps 2t at most n, while d = t/ 4 keeps the columnwise contribution bs(d−2) below
m/ 4. The full critical-locus bound is therefore smaller than m/ 2, permitting a slice of dimension
k =⌊m/ 4⌋= Θ(n2). Stage 2 now gives
C(pern)≥k log2(d−1)
3 = Ω(n2 log log n).
The quantitative bookkeeping in Proposition 7.1 gives the explicit constant in Theorem 1.1.
3. Overview of the formula lower bounds
The formula bounds exploit the fact that a formula is a tree: unlike a circuit, it cannot
reuse a computation in several places. Our strategy identifies many small, disjoint groups of
matrix entries whose influence on the permanent is individually rich. Each group forces many
occurrences of its variables in any formula, and disjointness allows us to add these requirements.
We first describe the measure of influence, then the matching construction that makes the
measure large, and finally the packing and the extension to division.
116
===== PAGE 119 =====
Stage 1: Measuring information in a group of variables. Let Y be a nonempty set of variables of
a polynomial f∈C[Y, Z], where Z denotes all remaining variables. Expanding in the variables
of Y gives
f =
∑
α∈NY
cα(Z)Y α, c α(Z)∈C[Z].
We measure how much independent information these coeﬀicients contain by
tdY (f ) = trdeg C C
(
cα(Z) : α∈NY)
.
Here polynomials c1, . . . , c r ∈C[Z] are algebraically independent if no nonzero polynomial
H ∈C[T1, . . . , T r] satisfies H(c1, . . . , c r) = 0 . For example, independent variables z1, z2 are
algebraically independent, whereas z1, z2
1 are dependent because T2−T 2
1 vanishes after sub-
stituting these two polynomials. The transcendence degree above is the maximum number of
algebraically independent coeﬀicient polynomials. It counts independent parameters, not merely
the number of distinct or linearly independent coeﬀicients.
For a formula Φ, let tY (Φ) be the number of leaves labeled by variables from Y , counting
repeated occurrences. Section 8 proves that every division-free formula computing f satisfies
(3.1) tdY (f )≤4tY (Φ)−2≤4tY (Φ), t Y (Φ)≥1.
The reason is that any subformula containing no Y -variable computes a polynomial in Z. Along
a path where only one child contains a Y -variable, the other child therefore modifies the marked
computation by an aﬀine map u↦→Au + B, with A, B∈C[Z]. An entire such path remains
a single aﬀine map. Only a gate with two Y -containing children combines genuinely different
marked computations. The tree connecting tY (Φ) marked leaves has at most tY (Φ)−1 such
branching gates, and each gate introduces at most four coeﬀicient parameters; the final aﬀine
map contributes two more. Consequently, all coeﬀicients of f belong to a field generated by at
most 4tY (Φ)−2 quantities. This step turns algebraic independence into a direct lower bound
on variable occurrences.
Stage 2: Obtaining quadratically many independent coeﬀicients from a logarithmic-size match-
ing. A matching Y in the n×n variable matrix X is a set of entries with no repeated row or
column. Set
ℓ =⌈log2 n⌉, k = 2ℓ, m = n−k,
and choose a matching of k entries. For n≥32, we have m≥n/ 2, so m2 = Ω(n2) even though
|Y|= O(log n). After permuting rows and columns, suppose that the marked variables are
Y ={yi = xii : i∈[k]}. Since the permanent is multilinear, its expansion takes the particularly
simple form
pern(X) =
∑
S⊆ [k]
cS(X\Y )
∏
i∈S
yi.
The coeﬀicient cS sums the permutation terms using exactly the marked diagonal entries indexed
by S. Equivalently, delete their rows and columns and set every other marked entry to zero.
The key assertion, proved in Section 9, is
(3.2) tdY (pern)≥m2.
To see what must be shown, divide the k marked indices into two sets E and F of size ℓ. For
each pair 0≤α, β < m , let P (α)⊆E and Q(β)⊆F encode the binary digits of α and β,
respectively, and set
S(α, β) = [ k]\
(
P (α)∪Q(β)
)
.
Because m≤2ℓ, these choices specify m2 distinct coeﬀicients cS(α,β). Separate the marked and
unmarked row and column indices by writing
X =
(D U
V W
)
, W = (wab)a,b∈[m].
117
===== PAGE 120 =====
Here D uses the k internal indices, W uses the m external indices, and U, V connect the two
groups. We establish algebraic independence by showing that the square Jacobian
(∂cS(α,β)
∂wab
)
(α,β),(a,b)
is invertible at one explicit assignment of the unmarked variables. The characteristic-zero
Jacobian criterion then proves ( 3.2).
The assignment uses distinct complex numbers p1, . . . , p m and, independently, distinct com-
plex numbers q1, . . . , q m. Set the internal off-diagonal entries to zero and every wab to one. If
eu∈E and fv∈F correspond to binary positions u, v∈{0, . . . , ℓ −1}, assign
Ueu,b = p2u
b , U fv,b = 1, V a,eu = 1, V a,fv = q2v
a
to the internal-to-external and external-to-internal entries, respectively. The derivative with
respect to wab fixes the external matching edge (a, b). Because all other external entries are
one, the remaining weighted choices separate into an external column choice depending only on
pb and an external row choice depending only on qa. More precisely, the evaluated Jacobian has
entries
Lα,β gα(pb)hβ(qa), L α,β̸= 0,
where gα and hβ are univariate polynomials of exact degrees α and β, respectively. Thus
the p-evaluation and q-evaluation matrices are Vandermonde matrices multiplied by invertible
triangular change-of-basis matrices. Their Kronecker product, and hence the whole Jacobian,
is invertible. The 5×5 example at the beginning of Section 9 illustrates this row–column
separation before the general construction.
Stage 3: Packing matchings and summing their costs. One matching now forces at least m2/ 4
occurrences of its k variables by ( 3.1) and ( 3.2). To obtain the full formula bound, Section 10
partitions many of the n2 matrix entries into pairwise entry-disjoint matchings of size k. Index
rows and columns by {0, . . . , n −1}and, for 0≤τ < n and 0≤j <⌊n/k ⌋, define
Yτ,j =
{
xjk+r, (jk+r+τ) mod n : 0≤r < k
}
.
Each Yτ,j is a matching. The row determines j, while the column-minus-row difference modulo
n determines τ, so no matrix entry belongs to two of these matchings. Their number is
ν = n
⌊n
k
⌋
≥n2
2k .
Since their variable sets are disjoint, each variable-labeled leaf is charged at most once. Therefore
Lvar(Φ)≥
∑
τ,j
tYτ,j (Φ)≥νm2
4 = Ω
(
n4
log n
)
.
Keeping the explicit inequalities m≥n/ 2 and k≤4 log2 n gives the constant in Theorem 1.2.
The passage to internal-gate bounds uses only the binary-tree identity G(Φ) = L(Φ)−1.
Stage 4: Allowing valid division. The matching construction and its Jacobian concern the per-
manent itself, so they remain unchanged when the formula contains division gates. Only the
occurrence-charging statement requires a new argument. Put R = C(Z), the field of rational
functions in the unmarked variables. Along a path with one marked child, an unmarked child
now computes an element of R, and all four arithmetic operations transform the marked value
by a fractional linear map
u↦−→au + b
cu + d , a, b, c, d ∈R.
Validity ensures that the actual denominator is nonzero as a rational function. After dividing
the representing matrix by one of its nonzero entries, the map is described by at most three
parameters; the matrix is not required to be invertible. A gate combining two marked sub-
formulas therefore contributes at most six parameters, and the final map contributes at most
three. This places the output in K(Y ) for a subfield K ⊆R generated over C by at most
6tY (Φ)−3 elements.
118
===== PAGE 121 =====
There is one additional subtlety: membership in K(Y ) alone does not immediately say that
the coeﬀicients of the output belong to K. However, the output is also the polynomial pern∈
R[Y ], and the elementary field-intersection identity
K(Y )∩R[Y ] = K[Y ]
recovers precisely that conclusion. Consequently, Section 10 establishes
tdY (pern)≤6tY (Φ)−3 < 6tY (Φ).
Applying this inequality to the same ν disjoint matchings gives
Lvar(Φ)≥νm2
6 = Ω
(
n4
log n
)
,
with the explicit constant of Theorem 1.3. The Jacobian specialization is applied only to
polynomial coeﬀicients of the permanent: a formula denominator need not remain nonzero at
that numerical assignment.
4. A geometric circuit bound
Our goal in this section is to convert a geometric property of a homogeneous polynomial into
an arithmetic circuit lower bound. For a polynomial P∈C[x1, . . . , x m], its gradient and critical
locus are
∇P (x) =
( ∂P
∂x1
(x), . . . , ∂P
∂xm
(x)
)
, Crit(P ) ={x∈Cm :∇P (x) = 0}.
The critical locus is an aﬀine algebraic set: it consists of the common solutions to finitely
many polynomial equations. Its dimension is, informally, the largest number of algebraically
independent parameters that can vary on one of its components; its codimension in Cm is
m−dim Crit(P ). We will show that when P has degree d and its critical locus has codimension
at least k, computing P requires at least k log2(d−1)/ 3 multiplication gates. The bound then
transfers to the permanent whenever P is an aﬀine specialization of it.
The argument has three components. First, we bound the complexity of a homogeneous
square polynomial map whose only zero is the origin. Second, we obtain such a map from the
gradient of P by restricting its input to a suitable k-dimensional linear subspace and taking k
linear combinations of its outputs. Finally, we use reverse-mode differentiation to compute this
restricted gradient from a circuit for P .
Throughout the section, we use the multiplicative-complexity model : aﬀine combinations of
inputs and previously computed results are free, while each binary multiplication costs one.
Since an ordinary size- L arithmetic circuit contains at most L multiplication gates, its multi-
plicative complexity is at most L. Treating aﬀine operations as free will also let us perform
linear changes of variables and linear combinations of outputs without affecting our bounds.
The first lemma formalizes the gradient warm-up in § 2. Its hypothesis that the origin is the
only common zero forces a generic fiber of a homogeneous degree- e polynomial map to have
ek solutions. Conversely, a circuit using q multiplications can describe the same solutions with
only q quadratic equations, which have at most 2q isolated solutions.
Lemma 4.1. Let F = ( F1, . . . , F k) : Ck→Ck have homogeneous coordinates of a common
degree e≥1. If F − 1(0) ={0}and a circuit in this model computes all Fi using q multiplications,
then ek≤2q.
Proof. We first count the solutions of F (u) = a for a suitably chosen target a = ( a1, . . . , a k).
Introducing one additional variable z, homogenize these equations to obtain
(4.1) Fi(u)−aize = 0, i ∈[k],
in projective space Pk. A point of Pk is a nonzero vector (u1, . . . , u k, z) considered up to
multiplication by a nonzero scalar. Points with z̸= 0 can be normalized to z = 1 and are
exactly the usual aﬀine solutions of F (u) = a. The remaining points, with z = 0 , are the
potential solutions “at infinity. ”
119
===== PAGE 122 =====
There are no such solutions at infinity: if [u1 : ···: uk : 0] satisfied ( 4.1), then u ̸= 0
and F (u) = 0 , contradicting the hypothesis. Moreover, every positive-dimensional projective
algebraic set intersects every projective hyperplane. Thus a positive-dimensional common zero
set of ( 4.1) would intersect the hyperplane z = 0, which we have just ruled out. The intersection
is therefore zero-dimensional. Projective Bézout now says that the total number of its points,
counted with their algebraic multiplicities, is the product of the k defining degrees:
e·e···e
k factors
= ek.
Since there are no points at infinity, this is also the number of aﬀine solutions counted with
multiplicity.
To obtain ek distinct solutions, rather than merely ek solutions counted with multiplicity, we
verify that a generic target a has a reduced fiber. Put
R = C[u1, . . . , u k], B = C[F1, . . . , F k]⊆R.
Because the origin is the only common zero of the Fi, the Nullstellensatz gives
(u1, . . . , u k)h⊆(F1, . . . , F k)
for some integer h. In particular, every monomial of total degree at least h belongs to the
ideal generated by the Fi. Since that ideal is homogeneous, a monomial of degree j≥h can
be written as a sum of terms FiGi, with each nonzero Gi homogeneous of degree j−e < j .
Repeating this reduction expresses every element of R as a B-linear combination of the finitely
many monomials of total degree less than h. Thus R is a finite B-module.
A finite ring extension preserves Krull dimension, so dim B = dim R = k. Since B is gener-
ated by the k elements F1, . . . , F k, this dimension equality also shows that these elements are
algebraically independent. Consequently, B∼= C[y1, . . . , y k], and the original map F : Ck→Ck
is a finite dominant morphism: finiteness gives finite fibers, and dominance means that the
image is dense in the target. Characteristic zero rules out inseparability, so generic smoothness
supplies a nonempty open set of targets a whose fibers are reduced, meaning that every solution
has multiplicity one [ Har77, Ch. III, Cor. 10.7]. Choose such an a. Its fiber consists of exactly
ek distinct points by the preceding Bézout count.
We next describe the same fiber using the multiplication gates of the circuit. Order those gates
topologically and introduce a new variable vj for the output of the jth gate. Because additions,
subtractions, and scalar operations are free, its two inputs are aﬀine functions Aj(u, v<j) and
Bj(u, v<j) of the original inputs and the preceding multiplication outputs. Its gate equation is
therefore
vj = Aj(u, v<j)Bj(u, v<j), j ∈[q].
Similarly, each circuit output is an aﬀine function Hi(u, v), so requiring that the output equal
a adds the equations
Hi(u, v) = ai, i ∈[k].
We have obtained q equations of degree at most two and k equations of degree at most one in
the q + k unknowns (u, v). For every u, the gate equations determine the vj successively and
uniquely. Thus solutions of the complete system correspond bijectively to the ek points of the
selected fiber. The aﬀine Bézout inequality [ Hei83] bounds the number of isolated solutions by
the product of the equation degrees, which is at most 2q. Hence ek≤2q. □
We now explain how to produce the kind of square polynomial map required by Lem. 4.1
from a gradient. The gradient of a degree- d homogeneous polynomial has degree d−1, but it has
m outputs and may vanish on a positive-dimensional critical locus. The next lemma removes
these obstacles in two steps: restrict the input to a k-dimensional subspace that avoids nonzero
critical points, and then project the m gradient coordinates down to k without introducing a
new zero.
Lemma 4.2. Let P ∈C[x1, . . . , x m] be homogeneous of degree d≥2, and let δ≥0 satisfy
dim Crit(P )≤δ. If 1≤k < m and k + δ≤m, there are linear maps W : Ck→Cm and
120
===== PAGE 123 =====
A : Cm→Ck, with W injective, such that the homogeneous map F (u) = A∇P (W u) has degree
d−1 and F − 1(0) ={0}.
Proof. Since P is homogeneous and d≥2, all coordinates of ∇P are homogeneous of degree
d−1≥1. In particular, Crit(P ) is a cone: if x is critical, so is every scalar multiple of x. Its
nonzero points can consequently be viewed as directions in projective space:
P Crit(P ) ={[x]∈Pm− 1 : x∈Crit(P )\{0}}.
Removing the scalar parameter decreases dimension by one, so this projectivized critical locus
has dimension at most δ−1. If Crit(P ) ={0}, its projectivization is empty and the avoidance
condition below is automatic.
We use the standard projective avoidance principle: if an algebraic subset of PN has dimension
at most r, then a generic projective l-plane misses that subset whenever l + r < N . One way to
see the dimension count is to consider pairs consisting of a point in the subset and an l-plane
containing that point. For a fixed point, the condition that an l-plane contain it has codimension
N−l in the space of all l-planes. Allowing the point to vary introduces at most r parameters,
so the planes meeting the subset still form a proper exceptional set whenever r < N−l [Har77,
Ch. I].
Apply this principle first in Pm− 1 with l = k−1 and r = δ−1. The hypothesis k + δ≤m
gives
(k−1) + (δ−1) < m−1,
so some projective (k−1)-plane avoids P Crit(P ). Such a plane is the projectivization of a
k-dimensional linear subspace of Cm. Choose an injective linear map W : Ck→Cm whose
image is that subspace. A voidance means exactly that
∇P (W u)̸= 0 for every u̸= 0.
At this point the gradient has no nonzero zero on the restricted input space, but it still has
m output coordinates. Homogeneity and the displayed nonvanishing let us associate to every
nonzero u the projective direction of its gradient:
[u]↦−→[∇P (W u)].
This is a well-defined morphism Pk− 1→Pm− 1: replacing u by cu multiplies the gradient by
cd− 1 and therefore does not change its projective direction. Its image is a projective algebraic
set of dimension at most k−1.
Apply the avoidance principle again, now to this image and to projective planes of dimension
m−k−1. The required inequality is
(m−k−1) + (k−1) = m−2 < m−1.
Hence there is an (m−k)-dimensional linear subspace K⊆Cm whose projectivization does
not meet any gradient direction. Choose a rank- k linear map A : Cm→Ck with kernel K. If
A∇P (W u) = 0 for some u̸= 0, then the nonzero vector ∇P (W u) belongs to K, contradicting
the choice of K. Therefore
F (u) = A∇P (W u) = ⇒ F − 1(0) ={0}.
Its coordinates remain homogeneous of degree d−1, as required. □
Combining the preceding lemmas now gives a circuit criterion in terms of the codimension of
the critical locus. The only additional ingredient is that all first derivatives of a circuit output
can be computed together with only a constant-factor increase in the number of multiplication
gates.
Proposition 4.3. Suppose a homogeneous polynomial P of degree d≥2 in m variables is a
nonzero scalar multiple of an aﬀine specialization of pern. If dim Crit(P )≤m−k for some
1≤k < m , then every arithmetic circuit of size L computing pern satisfies
(4.2) k log2(d−1)≤3L.
121
===== PAGE 124 =====
Proof. Start with a size- L circuit for pern. Since P is a nonzero scalar multiple of an aﬀine
specialization, substituting aﬀine linear forms for the input entries and applying the scalar factor
produces a circuit for P . These operations are free in the multiplicative-complexity model, so
the resulting circuit has at most L multiplication gates.
The Baur–Strassen differentiation theorem [ BS83, Thm. 2] computes all m first derivatives of
P simultaneously with at most three times as many multiplication gates. To see why the factor
is three in this model, evaluate the original circuit in topological order, retaining the output
of each multiplication gate. In the reverse traversal, the adjoint ¯v of an intermediate value v
records the derivative of the final output with respect to v. If a forward gate computes v = ab,
the chain rule gives the updates
¯a←¯a + ¯vb, ¯b←¯b + ¯va.
The forward product uses one multiplication, and these two updates use at most two more;
additions and scalar operations remain free. Thus all of ∇P can be computed with at most 3L
multiplications, regardless of the number m of derivatives.
Apply Lem. 4.2 with δ = m−k. Its hypothesis is satisfied because dim Crit(P )≤m−k and
k + (m−k) = m. We obtain linear maps W and A for which
F (u) = A∇P (W u)
is a homogeneous degree- (d−1) map Ck→Ck whose only zero is the origin. Precomposing
the gradient circuit with W and taking the output combinations prescribed by A cost no mul-
tiplications. Therefore F is computable with at most 3L multiplication gates, and Lem. 4.1
gives
(d−1)k≤23L.
Taking base-two logarithms proves ( 4.2). □
5. Critical loci of minor sums
The circuit bound from Prop. 4.3 becomes useful when we find a degree- d polynomial in
many variables whose critical locus has comparatively small dimension. This section supplies
the necessary estimate for a polynomial that sums all size- d matchings between t rows and s
columns. The following section will realize several disjoint copies of this polynomial as an aﬀine
specialization of the permanent.
Let X = (xia) be a t×s matrix of variables, and suppose 1≤d≤min{t, s}. Define
(5.1) Mt,s,d(X) =
∑
I⊆ [t]
|I|=d
∑
J⊆ [s]
|J|=d
per(XI,J ).
Every term of per(XI,J ) chooses a bijection from I to J. Equivalently, Mt,s,d is the sum of
the weights ∏
j∈I xj,φ(j) over all d-element row sets I and all injections φ : I ↪→[s]. Thus its
monomials correspond precisely to matchings of d row–column pairs.
To describe the critical-point equations, for every nonempty B⊆[t] introduce
pB(X) =
s∑
a=1
∏
j∈B
xja.
For example, p{j} is the sum of row j, while p{j,j′} records the sum of products obtained by
assigning both rows to the same column. There are ρ = 2 t−1 such quantities. We will first treat
them as freely chosen parameters and then impose their actual values pB(X). This enlargement
can only increase the dimension being estimated, but makes the critical-point equations uniform
from column to column.
The basic idea is especially transparent for d = 2 . Fix a column a, write uj = xja, and
abbreviate pj = p{j}(X). A matching counted by ∂Mt,s,2/∂x ia already uses the pair (i, a); its
other pair may use any row j̸= i and any column other than a. Therefore
∂Mt,s,2
∂xia
=
∑
j̸=i
(pj−uj).
122
===== PAGE 125 =====
At a critical point, put vj = pj−uj. Subtracting the equations for two different values of i
shows that all vj are equal. Each equation then reads (t−1)vj = 0. Since t≥2 and the ground
field has characteristic zero, every vj vanishes. Thus, once the row sums pj have been fixed, the
entire column (u1, . . . , u t) is determined.
For d≥3, the power sums alone do not determine a column. We will additionally retain
its first d−2 elementary symmetric functions and prove that these data leave only finitely
many possibilities. Counting the 2t−1 shared power-sum parameters and the d−2 additional
parameters for each of the s columns gives the desired bound.
Proposition 5.1. If 3≤d≤min{t, s}, then
(5.2) dim Crit(Mt,s,d)≤2t−1 + s(d−2).
Proof. Put q = d−1, so q≥2 and q < t . The argument has three stages. First, we rewrite
every first derivative using the power-sum parameters and one column of X. Next, we identify
the highest-degree part of the resulting equations. Finally, we use that highest-degree part to
show that, once q−1 = d−2 symmetric functions per column are fixed, all the remaining
column coordinates admit only finitely many possibilities.
Fix a row i and a column a. Differentiating a matching monomial with respect to xia keeps
precisely those matchings that use the pair (i, a). Removing that pair leaves a q-element set of
other rows, injected into the columns other than a. Consequently,
∂Mt,s,d
∂xia
(X) =
∑
I⊆ [t]\{ i}
|I|=q
∑
φ:I↪→ [s]\{ a}
∏
j∈I
xj,φ(j).
The obstacle is the injectivity requirement: independently summing over a column for each row
would also count assignments in which several rows choose the same column. Inclusion–exclusion
over these collisions gives a convenient expression in terms of the pB.
For a finite set I, let Π(I) be its set of partitions into nonempty blocks. For π∈Π(I), define
µ(π) =
∏
B∈π
(−1)|B|−1(|B|−1)!.
Here µ(π) is the usual Möbius coeﬀicient for the partition lattice. Temporarily regard all pB as
independent parameters, and for a column vector u = (u1, . . . , u t) define
(5.3) Qi(u; p) =
∑
I⊆ [t]\{ i}
|I|=q
∑
π∈Π(I)
µ(π)
∏
B∈π

pB−
∏
j∈B
uj

.
To verify the inclusion–exclusion explicitly, specialize to u = X•a = (x1a, . . . , x ta) and p = p(X).
For any nonempty block B,
pB(X)−
∏
j∈B
xja =
∑
c̸=a
∏
j∈B
xjc.
The product of these expressions over B∈π counts all maps φ : I→[s]\{a}that are constant
on every block of π, with the matching weight∏
j∈I xj,φ(j). For a fixed map φ, its total coeﬀicient
in the partition sum is therefore
∑
π∈Π(I)
π refines the fiber partition of φ
µ(π).
This coeﬀicient factors over the nonempty fibers C of φ. The factor for a fiber C is
∑
π∈Π(C)
∏
B∈π
(−1)|B|−1(|B|−1)! =
∑
σ∈SC
sgn(σ).
Indeed, a permutation with cycle blocks B contributes the displayed sign, and there are (|B|−1)!
cycles on each fixed block B. The sum of permutation signs is 1 when|C|= 1 and 0 when
123
===== PAGE 126 =====
|C| ≥2. Hence precisely the maps with singleton fibers—that is, the injections—survive.
Summing over I proves
(5.4) ∂Mt,s,d
∂xia
(X) = Qi(X•a; p(X)).
We next identify the part of Qi having highest degree in the column variables u, while treating
every pB as a coeﬀicient of degree zero. For a fixed q-element set I, the only way to obtain
column degree q is to take −∏
j∈B uj from every block factor in ( 5.3). Thus the coeﬀicient of∏
j∈I uj in degree q is
(−1)q ∑
π∈Π(I)
∏
B∈π
(|B|−1)! = (−1)qq!.
For the equality, specify the cycle blocks of a permutation of I; each prescribed block B can
be arranged into a cycle in (|B|−1)! ways. Summing over partitions therefore counts all q!
permutations. Put α = (−1)qq!, and write ej(u) for the jth elementary symmetric polynomial
in u1, . . . , u t, with e0(u) = 1 . Summing the degree- q monomials over all I⊆[t]\{i}gives
(5.5) Qi(u; p) = αeq(u1, . . . , ˆui, . . . , u t) + Ri(u; p), degu Ri≤q−1.
Here the hat means that coordinate ui is omitted. In particular, although the lower-degree
remainder can depend on the shared parameters pB, the highest-degree part has a simple sym-
metric form independent of those parameters.
We now convert this structure into the promised parameter count. Introduce independent
coordinates pB and a separate column vector u(a) = ( u(a)
1 , . . . , u (a)
t ) for every a∈[s]. The
equations Qi(u(a); p) = 0 define an aﬀine set whose coordinate ring is
A = C[pB, u(a)
i ]
/(
Qi(u(a); p) : 1≤i≤t, 1≤a≤s
)
.
This is the incidence construction: its points record one common collection of power-sum pa-
rameters together with s columns satisfying the corresponding critical-point equations. A true
critical point of Mt,s,d gives such a point by taking u(a) = X•a and pB = pB(X). We allow
additional incidence points for which the pB need not equal these actual power sums, since an
upper bound for the larger set also bounds the critical locus.
In addition to the ρ power-sum parameters, retain the first q−1 elementary symmetric func-
tions of each column. To keep these parameters formally independent, introduce the polynomial
ring
B = C[pB, za,j : ∅̸= B⊆[t], 1≤a≤s, 1≤j < q ]
and map it into A by sending each pB to its namesake and each za,j to ej(u(a)). Equivalently,
this map makes A into a B-algebra. The map need not be injective: any relations among the
actual parameter values can only decrease the final dimension.
Our remaining task is to prove that A is generated by finitely many elements as a module
overB. Fix one column, suppress its index, and put κ = t−q > 0. Two elementary symmetric-
polynomial identities give
eq(u1, . . . , ˆui, . . . , u t) =
q∑
j=0
(−ui)q− jej(u),
t∑
i=1
eq(u1, . . . , ˆui, . . . , u t) = κeq(u).
For the first identity, expand ∏
h̸=i(1 + uhz) =∏
h(1 + uhz)/ (1 + uiz) and compare coeﬀicients
of zq. For the second, each squarefree monomial of degree q occurs once for each of the t−q = κ
omitted coordinates outside its support.
The incidence equations and ( 5.5) say that αeq(u1, . . . , ˆui, . . . , u t) + Ri(u; p) = 0 for every i.
Summing these equations and using the second elementary symmetric identity gives
καeq(u) +
t∑
h=1
Rh(u; p) = 0 .
This eliminates the only elementary symmetric function eq(u) not already recorded among the
base parameters za,j. Insert the first symmetric identity into the ith incidence equation, replace
124
===== PAGE 127 =====
ej(u) by za,j for 1≤j < q , and eliminate eq(u) using the summed equation. Since α(−1)q = q!,
the resulting equality in A is
(5.6) κq!uq
i =−κα
q− 1∑
j=1
(−ui)q− jza,j−κRi(u; p) +
t∑
h=1
Rh(u; p).
Treating the pB and za,j as base coeﬀicients, every term on the right has degree at most q−1 in
the coordinates of the chosen column. Because κ > 0 and the ground field has characteristic zero,
the leading coeﬀicient κq! is invertible. Therefore ( 5.6) replaces uq
i by a B-linear combination
of monomials of strictly smaller total column degree.
Apply this replacement whenever any coordinate exponent is at least q. Each replacement
decreases total degree in the corresponding column, so the process terminates. Repeating it for
all s columns shows that the finitely many monomials
s∏
a=1
t∏
i=1
(u(a)
i )ra,i , 0≤ra,i < q,
generateA as a B-module. In particular, fixing all the parameters pB and za,j leaves a finite-
dimensional coordinate algebra for the possible columns; this is the algebraic form of the claimed
finite-choice property.
A finite algebra cannot have larger Krull dimension than its parameter ring: if the map
B→Ahas kernel K, thenA is finite overB/K , and the standard dimension theorem for finite
algebras gives dimA = dim(B/K )≤dimB [Eis95]. Since B is a polynomial ring in ρ + s(q−1)
independent parameters, we obtain
dimA≤dimB = ρ + s(q−1);
Finally, to return from the enlarged incidence set to the actual critical locus, ( 5.4) induces
a surjection from A onto C[X]/ (∂Mt,s,d/∂x ia : i, a) by sending pB to pB(X) and u(a)
i to xia.
The map is surjective because the images of the u(a)
i are all the matrix variables. Passing to
a quotient cannot increase Krull dimension, and the dimension of an aﬀine common-zero set
equals the Krull dimension of its coordinate ring. Hence
dim Crit(Mt,s,d)≤dimA≤ρ + s(q−1) = 2 t−1 + s(d−2),
which proves ( 5.2). □
The circuit application requires several copies of this polynomial on disjoint sets of variables.
Because their critical-point equations involve separate variable blocks, the individual dimension
bounds add.
Corollary 5.2. Suppose 3≤d≤min{t, s}, let X (1), . . . , X (b) be disjoint t×s variable blocks,
and let λ1, . . . , λ b∈C× . Then
P (X) =
b∑
h=1
λhMt,s,d(X (h)) = ⇒ dim Crit(P )≤b
(
2t−1 + s(d−2)
)
.
Proof. For a variable in block X (h), the corresponding derivative of P is λh times the derivative
of Mt,s,d(X (h)). Since λh̸= 0, this derivative vanishes exactly when the corresponding derivative
of the block polynomial vanishes. Different blocks share no variables, and therefore
Crit(P ) =
b∏
h=1
Crit(Mt,s,d(X (h))).
Dimensions add under products of complex aﬀine algebraic sets. Applying Prop. 5.1 to each
factor gives the stated bound. □
125
===== PAGE 128 =====
6. An affine specialization of the permanent
Corollary 5.2 bounds the critical locus of a sum of minor-sum polynomials supported on
disjoint row blocks. To apply Prop. 4.3, however, we must first realize such a sum as a spe-
cialization of one permanent. Our immediate objective is therefore to construct a matrix of
constants whose permanent minors cancel whenever the omitted rows come from several dif-
ferent blocks, but remain nonzero when all the omitted rows come from one block. Appending
these constant columns to a matrix of variables will then produce exactly the blockwise minor
sums from the preceding section.
Let b, t, s≥1, partition [r] into b disjoint blocks R1, . . . , R b of size t, where r = bt, and
suppose that 1≤d≤min{t, s}. For T⊆[r], let 1T∈Cr denote the vector that is 1 on T and
0 elsewhere. Choose a primitive dth root of unity ζ, and set
θ = (−1)d+12d.
The following two families of constant columns form a matrix U∈Cr× (r− d):
•for each h∈[b], take t−d copies of 1Rh;
•for each h = 2, . . . , b and j = 0, . . . , d −1, take 1R1∪···∪Rh− 1 + 2ζj1Rh.
The first family contributes b(t−d) columns and the second contributes (b−1)d columns, for
a total of b(t−d) + (b−1)d = bt−d = r−d. If t = d, the first family is empty; if b = 1 , the
second family is empty.
Lemma 6.1. There are λ1, . . . , λ b∈C× such that ∑
h λhMt,s,d(XRh,[s]) is, up to a nonzero
scalar, an aﬀine specialization of perr+s− d. More precisely, for the block matrix
B(X) =
(X U
1 0
)
, X = (xia)i∈[r], a∈[s],
where the lower-left block is the (s−d)×s all-ones matrix and the lower-right block is the
(s−d)×(r−d) zero matrix, one has
(6.1) per(B(X)) = c
b∑
h=1
λhMt,s,d(XRh,[s]), c = (s−d)!(t−d)!(t!)b− 1̸= 0.
Proof. First observe why minors of U determine the desired specialization. The matrix B(X)
has r + s−d rows and columns. Because its lower-right block is zero, each of its s−d lower rows
must be matched to one of the first s columns in every nonzero permanent term. This leaves
exactly d of those columns to be matched to upper rows. Let J⊆[s] be those d columns and
I⊆[r] the d upper rows matched to them. The remaining r−d upper rows must be matched
to the r−d columns of U . Finally, the remaining lower-left submatrix is an (s−d)×(s−d)
all-ones matrix, whose permanent is (s−d)!. Summing over I and J consequently gives
(6.2) per(B(X)) = ( s−d)!
∑
I⊆ [r], J⊆ [s]
|I|=|J|=d
per(UI c,[r− d]) per(XI,J ).
It remains to show that the constant coeﬀicient per(UI c,[r− d]) vanishes unless I is contained in
one row block, and to compute its value in the remaining cases.
To keep track of these minors, introduce the commutative square-zero algebra
S = C[z1, . . . , z r]/ (z2
1, . . . , z 2
r ).
Its monomials zK = ∏
i∈K zi, indexed by subsets K⊆[r], form a vector-space basis: a term
containing any zi twice vanishes. Consequently, if A is an r×q matrix and|K|= q, expansion
of its column forms gives
(6.3) [zK]
q∏
j=1
( r∑
i=1
Aijzi
)
= per( AK,[q]).
Indeed, each surviving contribution chooses a distinct row for each column, and the contributions
producing zK are precisely the bijections between the q columns and the rows in K. When q = 0,
126
===== PAGE 129 =====
both the empty product and the permanent of the empty matrix are 1. Thus the minors of U
are encoded by a single product of its column forms.
For each block, put
yh =
∑
i∈Rh
zi.
Because the variables commute and have square zero,
(6.4) yj
h = j!
∑
K⊆ Rh
|K|=j
zK (0≤j≤t), y t+1
h = 0.
In particular, yt
h = t!∏
i∈Rh zi: the power yt
h saturates the entire block, so multiplying it by any
additional zi with i∈Rh gives zero.
The column form of 1Rh is yh. If Yh− 1 = y1 +···+ yh− 1, the column form of 1R1∪···∪Rh− 1 +
2ζj1Rh is Yh− 1 + 2ζjyh. The ordinary factorization ∏d− 1
j=0(A + ζjB) = Ad−(−B)d, applied in
the commutative algebra S, therefore gives
d− 1∏
j=0
(Yh− 1 + 2ζjyh) = Y d
h− 1 + θyd
h.
All mixed powers of Yh− 1 and yh have canceled. Multiplying over both families of columns now
yields
(6.5)
r− d∏
j=1
( r∑
i=1
Uijzi
)
=
( b∏
h=1
yt− d
h
) b∏
h=2
(
Y d
h− 1 + θyd
h
)
.
For example, when b = 2, the product of all column forms of U is
yt− d
1 yt− d
2 (yd
1 + θyd
2) = yt
1yt− d
2 + θyt− d
1 yt
2.
In the first term all rows of R1 appear and exactly d rows of R2 are omitted; in the second, the
roles of the blocks are reversed. In particular, no term can omit rows from both blocks. Taking
t = s = d = 2 gives θ =−4 and recovers the 4×4 cancellation in § 2.
We next verify that the same block-selection property persists for any number of blocks. For
1≤h≤b, let
Ch =


h∏
g=1
yt− d
g


h∏
g=2
(
Y d
g− 1 + θyd
g
)
.
We claim that there are coeﬀicients λ(h)
i such that
Ch =
h∑
i=1
λ(h)
i yt− d
i
∏
g∈[h]
g̸=i
yt
g.
For h = 1, this is the identity C1 = yt− d
1 , with λ(1)
1 = 1. Suppose the identity holds for h blocks.
By definition,
Ch+1 = Chyt− d
h+1
(
Y d
h + θyd
h+1
)
.
The term containing θyd
h+1 saturates the new block and multiplies each previous coeﬀicient by
θ. In the term containing Y d
h , every old block other than Ri is already saturated in the ith
summand. Therefore all mixed terms in Y d
h = ( y1 +···+ yh)d vanish after multiplication by
that summand, and the only surviving term is yd
i . Hence


h∑
i=1
λ(h)
i yt− d
i
∏
g∈[h]
g̸=i
yt
g

Y d
h =
( h∑
i=1
λ(h)
i
) h∏
g=1
yt
g.
127
===== PAGE 130 =====
It follows that the coeﬀicients satisfy
λ(h+1)
i = θλ(h)
i (1≤i≤h), λ (h+1)
h+1 =
h∑
i=1
λ(h)
i .
If Sh = ∑h
i=1 λ(h)
i , then S1 = 1 and Sh+1 = (1 + θ)Sh, so Sh = (1 + θ)h− 1. Consequently, at
h = b the coeﬀicients are
λ1 = θb− 1, λ h = θb− h(1 + θ)h− 2 (2≤h≤b).
They are all nonzero: θ̸= 0 and|θ|= 2 d > 1 imply 1 + θ̸= 0 . Combining the induction with
(6.5) proves
(6.6)
r− d∏
j=1
( r∑
i=1
Uijzi
)
=
b∑
h=1
λhyt− d
h
∏
g̸=h
yt
g,
the promised expression in which exactly one row block is unsaturated.
Finally, let I ⊆[r] have size d. By ( 6.3), the coeﬀicient of zI c on the left of ( 6.6) is
per(UI c,[r− d]). On the right, the hth summand saturates every block except Rh. Thus it
contributes to zI c only if I⊆Rh. When this occurs, ( 6.4) gives a factor (t−d)! from yt− d
h and
a factor t! from each of the other b−1 blocks. Therefore
per(UI c,[r− d]) =
{
λh(t−d)!(t!)b− 1, I ⊆Rh,
0, I meets more than one block .
Substituting this identity into ( 6.2) and grouping the surviving terms by their block Rh gives
per(B(X)) = ( s−d)!(t−d)!(t!)b− 1
b∑
h=1
λh
∑
I⊆ Rh, J⊆ [s]
|I|=|J|=d
per(XI,J ).
The inner sum is Mt,s,d(XRh,[s]), and the factorial prefactor is nonzero over C. This proves ( 6.1)
and realizes the blockwise polynomial needed for Cor. 5.2 as a specialization of one permanent.
□
7. Circuit parameters and the lower bound
We now assemble the geometric gradient bound, the critical-locus estimate, and the block-
selective specialization to prove Thm. 1.1. There are two quantitative requirements. First, the
specialization must retain m = Θ( n2) genuinely variable matrix entries. Second, its critical
locus must have dimension bounded away from m, so that a linear slice of dimension k = Θ(m)
avoids every nonzero critical point. Once these requirements hold, Prop. 4.3 supplies a lower
bound proportional to k log2(d−1).
The critical-locus bound from Cor. 5.2 has two costs per row block: 2t−1 global power-sum
parameters and s(d−2) column parameters. Setting t = 4 d makes the second cost less than
one quarter of the ts variables in each block. We will separately require 2t−1≤ts/ 4, so the
first cost also consumes at most one quarter. Choosing d on the order of log n will make these
requirements compatible while preserving the logarithmic gain in the gradient bound.
Fix d≥3, and introduce the parameters
(7.1) t = 4d, b =
⌊n
2t
⌋
, r = bt, s = n−r + d, m = rs, k =
⌊m
4
⌋
.
Here t is the number of rows in each block, b is the number of blocks, and r = bt is the total
number of variable rows. Taking b =⌊n/ (2t)⌋places r near n/ 2, leaving roughly n/ 2 variable
columns. More precisely, the choice s = n−r + d makes the square matrix B(X) of Lem. 6.1
have exactly
r + s−d = n
rows and columns. Its variable upper-left block is an r×s matrix, so m = rs counts its variable
entries. Finally, k =⌊m/ 4⌋is the dimension of the gradient slice to which Prop. 4.3 will be
applied.
128
===== PAGE 131 =====
If n≥6t, then b≥1 and s≥n/ 2. In particular, d≤t and d≤s, so all hypotheses needed
to construct the degree- d specialization in Lem. 6.1 hold. The next proposition isolates the
remaining numerical condition before we choose the degree as a function of n.
Proposition 7.1. Let n, d be positive integers, and define t, b, r, s, m, k by (7.1). Suppose
(7.2) d≥3, n ≥6t, 4(2t−1)≤ts.
Then every arithmetic circuit of size L computing pern satisfies
(7.3) L≥n2 log2(d−1)
144 .
Proof. Let ρ = 2 t−1, and let
P (X) =
b∑
h=1
λhMt,s,d(XRh,[s])
be the weighted block polynomial from ( 6.1). Lem. 6.1 makes P a nonzero scalar multiple of
an aﬀine specialization of pern, so it has precisely the form required by Prop. 4.3. Since all λh
are nonzero and the row blocks involve disjoint variables, Cor. 5.2 gives
dim Crit(P )≤D := b
(
ρ + s(d−2)
)
.
We estimate the two summands of D separately. The scale condition 4ρ≤ts gives
bρ≤bts
4 = m
4 .
For the column-parameter contribution, the choice t = 4d gives
bs(d−2) < bsd = bts
4 = m
4 .
Consequently,
dim Crit(P )≤D < m
2 .
Since k =⌊m/ 4⌋ ≤m/ 4, we have k + D < m , and in particular k + D ≤m. Thus a k-
dimensional linear slice can avoid the nonzero critical locus, as required in Lem. 4.2. Applying
Prop. 4.3 to this specialization gives
(7.4) k log2(d−1)≤3L.
It remains to express the slice dimension k in terms of the original matrix size n. From the
definition of b,
n
2−t≤r = t
⌊n
2t
⌋
≤n
2 .
The hypothesis n≥6t implies n/ 2−t≥n/ 3. Therefore
n
3≤r≤n
2 , s = n−r + d≥n
2 , m = rs≥n2
6 .
In particular m≥8, and the floor in the definition of k loses at most a factor of two:
k =
⌊m
4
⌋
≥m
8 ≥n2
48 .
Equivalently, n2≤48k. Substituting this estimate into ( 7.4) yields
L≥k log2(d−1)
3 ≥n2 log2(d−1)
144 ,
as claimed. □
129
===== PAGE 132 =====
Proof of Thm. 1.1. The fixed-degree bound becomes strongest when d grows while 24d remains
small enough to satisfy the scale condition. For n≥216, put
ℓ = log 2 n, d =
⌊ℓ
4
⌋
, t = 4d.
Then ℓ≥16, so d≥4 and t≤ℓ. The inequality n≥6t follows from n≥216 and t≤log2 n.
As in the proposition, r≤n/ 2 and s≥n/ 2. Moreover, 2t≤2ℓ = n, while d≥4 gives ds≥n.
Therefore
2t−1 < n≤ds, 4(2t−1)≤4ds = ts.
Thus all three hypotheses of ( 7.2) hold.
Finally, ℓ≥16 ensures
d−1 =
⌊ℓ
4
⌋
−1≥ℓ
4−2≥ℓ
8 .
Taking logarithms gives
log2(d−1)≥log2 ℓ−3 = log 2 log2 n−3.
Substitution into ( 7.3) proves ( 1.1). The factor log2 log2 n−3 grows without bound, so the
resulting circuit lower bound is superquadratic. □
8. Coefficient transcendence degree
We now turn from circuits to formulas. The first task is to define a complexity measure
that records how much independent information a polynomial carries in the coeﬀicients asso-
ciated with a selected set of variables. We then show that, for any division-free formula, this
information is controlled by the number of occurrences of those variables. The next section
will exhibit a matching of O(log n) matrix entries for which the permanent has Ω(n2) indepen-
dent coeﬀicients. The formula lower bound will follow by applying the present section to many
entry-disjoint matchings and adding their occurrence requirements.
LetX be a finite set of variables, let ∅̸= Y ⊆X, and put Z =X\ Y . We call Y the
selected variables and Z the remaining variables. To expose the information associated with Y ,
regard a polynomial in all the variables as a polynomial in Y whose coeﬀicients are themselves
polynomials in Z. Thus every f∈C[X ] = C[Z][Y ] has a unique expansion
f =
∑
α∈NY
fαY α, f α∈C[Z], Y α =
∏
y∈Y
yα(y).
Although the index set NY is infinite, only finitely many fα are nonzero. The multi-index 0
denotes the all-zero exponent vector, so f0 is obtained by setting every variable of Y to zero.
Counting distinct coeﬀicient polynomials would overestimate the information they contain:
several coeﬀicients can satisfy polynomial relations. Instead, we count the maximum number
that are algebraically independent. Recall that polynomials c1, . . . , c r∈C[Z] are algebraically
independent over C if
Q(c1, . . . , c r)̸= 0 for every nonzero Q∈C[T1, . . . , T r].
For example, if Y ={y}and f = yz1 + z2, the two coeﬀicients z1, z2 are algebraically indepen-
dent. In contrast, for f = yz 2 + z, the coeﬀicients c0 = z and c1 = z2 satisfy c1−c2
0 = 0 , and
therefore carry only one algebraically independent parameter.
Define its coeﬀicient transcendence degree by
tdY (f ) = trdeg C C
(
fα : α∈NY)
.
Here C(Z) denotes the rational-function field in the remaining variables, and C(fα : α∈NY )
is the smallest subfield containing C and all the coeﬀicient polynomials. In particular, the
field includes the constant-in- Y coeﬀicient f0. Its transcendence degree is precisely the largest
number of algebraically independent coeﬀicients in the expansion. Passing to the field generated
by the coeﬀicients does not assume that they are rational rather than polynomial: it simply lets
us measure how many independent parameters generate all of them. In the examples above,
the coeﬀicient transcendence degrees are two and one, respectively.
130
===== PAGE 133 =====
For a formula Φ, let tY (Φ) denote the number of leaves labeled by variables in Y , counted
with multiplicity. Thus two leaves carrying the same variable contribute two occurrences. Our
goal is to bound tdY (f ) in terms of tY (Φ), independently of the number or complexity of the
subformulas involving only Z. The coeﬀicient-transcendence method is standard [ KS14, §3.2.1,
Lem. 7]; the following proof supplies the explicit constant needed here.
Lemma 8.1. If a division-free formula Φ computes f∈C[X ] and t = tY (Φ)≥1, then
tdY (f )≤4t−2≤4t.
Proof. Mark a vertex of the formula exactly when its subformula has a descendant leaf labeled
by a variable in Y . The marked vertices form the portion of the formula connecting the t
selected leaves to the root. A marked gate can have either one or two marked children. The
two cases play different roles: a gate with one marked child merely changes an aﬀine wrapper
around the selected-variable computation, while a gate with two marked children combines two
such computations and can introduce new parameters.
First suppose a marked gate has exactly one marked child, whose output is u. The other child
contains no selected-variable leaf and hence computes some polynomial h∈C[Z]. According to
the gate operation and the order of its inputs, the output is one of
u + h, u −h, h −u, hu.
Each expression has the form Au + B with A, B∈C[Z]. Moreover, a whole path of such gates
can be absorbed into a single aﬀine map, since
A2(A1u + B1) + B2 = (A2A1)u + (A2B1 + B2).
Thus an arbitrarily long path with only one marked child at each gate does not require a new
independent parameter at every gate.
We formalize this observation by induction. For every marked subformula with s≥1 selected-
variable leaves, we claim that its output admits a representation
(8.1) Ag + B, A, B ∈C[Z], g ∈C(Γ)[Y ], |Γ|≤4s−4,
for some finite Γ⊆C(Z). The outer coeﬀicients A, B are not yet counted in Γ; they will be
charged when the corresponding marked computation meets another one, or at the root. At a
marked leaf labeled by y∈Y , choose
g = y, A = 1, B = 0, Γ = ∅.
This gives the claim for s = 1.
If a marked gate has only one marked child, compose its aﬀine map with the outer aﬀine map
already supplied for that child. The resulting slope and intercept still belong to C[Z], the inner
polynomial g is unchanged, and no new element is added to Γ.
It remains to consider a gate with two marked children. Suppose they have s1, s2 ≥1
selected-variable leaves and, by induction, their respective outputs are
A1g1 + B1 and A2g2 + B2, g i∈C(Γi)[Y ], |Γi|≤4si−4.
Adjoin the four outer coeﬀicients and set
Γ = Γ 1∪Γ2∪{A1, B1, A2, B2}⊆C(Z).
Both child outputs now belong to C(Γ)[Y ]. Applying the gate operation +,−, or ×therefore
produces another polynomial g∈C(Γ)[Y ]. Represent the resulting output with the identity
outer map, namely A = 1 and B = 0. Since s = s1 + s2, the parameter count is
|Γ|≤(4s1−4) + (4s2−4) + 4 = 4 s−4.
This completes the induction. Equivalently, the marked part of a binary formula has t−1 genuine
branching points; each can be charged at most four parameters, regardless of the lengths of the
intervening one-child paths.
Apply ( 8.1) to the root, which is marked because t≥1. Its output is f = Ag + B with
|Γ|≤4t−4. Adjoin the final slope and intercept by taking
Γ′= Γ∪{A, B}⊆C(Z).
131
===== PAGE 134 =====
Then|Γ′|≤4t−2 and f∈C(Γ′)[Y ], so every coeﬀicient fα belongs to C(Γ′). A field generated by
r elements has transcendence degree at most r, whether or not those generators are algebraically
independent. Therefore
tdY (f )≤trdegC C(Γ′)≤|Γ′|≤4t−2,
as claimed. □
To apply this upper bound to the permanent, we also need a practical way to certify that
a large family of its coeﬀicients is algebraically independent. The characteristic-zero Jacobian
criterion supplies exactly that test. Given coeﬀicient polynomials c1, . . . , c r∈C[Z], form the
matrix
J(c1, . . . , c r) =
(∂ci
∂z
)
i∈[r], z∈Z
.
Its rank is computed over the rational-function field C(Z). The Jacobian criterion states that
trdegC C(c1, . . . , c r) = rank C(Z) J(c1, . . . , c r)
in characteristic zero [ BMS11, Thm. 6]. Consequently, to prove that r coeﬀicients are alge-
braically independent, it is enough to identify r remaining variables and show that the cor-
responding square Jacobian minor is a nonzero polynomial. It is enough in turn to find one
specialization of those and the other remaining variables where this minor evaluates to a nonzero
complex number. The next section constructs precisely such a specialization for r = Ω(n2) co-
eﬀicients associated with one short matching.
9. Independent coefficients from a matching
A matching is a set of matrix entries with no repeated row or column. Our goal in this
section is to prove that, for a matching Y of only O(log n) entries, the expansion of pern in
the variables of Y contains Ω(n2) algebraically independent coeﬀicients. Combined with the
coeﬀicient bound from Lem. 8.1, this will force every division-free formula for the permanent
to contain Ω(n2) occurrences of the variables in each such matching; an analogous coeﬀicient
bound later treats formulas with division. The remaining step, packing many entry-disjoint
matchings, is deferred to § 10.
The independence proof has two conceptual ingredients. First, split the marked matching
into two equal parts, one encoding external column choices and the other encoding external row
choices. Second, specialize the unmarked entries so that the Jacobian of selected coeﬀicients
separates into independent row and column evaluation matrices. We begin with a small instance
that displays this separation without the binary-index bookkeeping needed in general.
9.1. A five-by-five warm-up. Choose distinct p1, p2, p3 ∈C and, independently, distinct
q1, q2, q3∈C, and consider
B =


ye 0 p1 p2 p3
0 yf 1 1 1
1 q1 w11 w12 w13
1 q2 w21 w22 w23
1 q3 w31 w32 w33


.
The matching here consists of the two diagonal variables ye, yf . Call their rows and columns
internal, and call the remaining three rows and columns external. Since the permanent is
multilinear, its expansion in the marked variables is
per(B) = cef yeyf + cf yf + ceye + c∅.
Thus cef , cf , ce, c∅ collect the permutation terms using both marked diagonal entries, only yf ,
only ye, or neither, respectively. They are polynomials in the external block entries wab.
Differentiating a coeﬀicient with respect to wab keeps precisely the permutation terms that
match external row a to external column b. Set
Gb =
∑
j̸=b
pj, H a =
∑
i̸=a
qi,
132
===== PAGE 135 =====
and, only after taking the derivative, evaluate all wij at 1. Counting the remaining matchings
gives
∂cef
∂wab
= 2, ∂cf
∂wab
= 2Gb, ∂ce
∂wab
= 2Ha, ∂c∅
∂wab
= GbHa.
Each count can be seen directly:
•For cef , both internal rows and columns are already matched. After the derivative fixes
(a, b), the other two external rows can match the other two external columns in 2! = 2
ways.
•For cf , the f -row uses its marked diagonal entry. The e-row must use an external column
j̸= b, with weight pj, giving Gb. The internal e-column can receive either external row
other than a, giving the additional factor 2.
•For ce, the roles are reversed: the f -row can use either remaining external column, while
the external row i̸= a matched to the f -column contributes qi. The result is 2Ha.
•For c∅, neither internal diagonal is used. The external column used by the e-row con-
tributes Gb, and the external row matched to the f -column contributes Ha. These
choices are independent, and all remaining matches are forced.
Restricting to the four external variables w11, w12, w21, w22 yields the Jacobian
diag(2, 2, 2, 1)


1 1 1 1
G1 G2 G1 G2
H1 H1 H2 H2
G1H1 G2H1 G1H2 G2H2

.
The second factor is the Kronecker product VH⊗VG of the two-point Vandermonde matrices
VH =
(
1 1
H1 H2
)
and VG =
(
1 1
G1 G2
)
. The row choice and column choice are independent, so these
two evaluation factors separate. Since G2−G1 = p1−p2 and H2−H1 = q1−q2, their Kronecker
product has determinant (p1−p2)2(q1−q2)2̸= 0. The diagonal prefactor is also invertible, so
the four coeﬀicients are algebraically independent. The characteristic-zero Jacobian criterion
recalled in § 8 justifies this final implication: a nonzero Jacobian minor at even one specialization
certifies independence before specialization.
The example identifies the general plan. We will replace the single e-index and f -index by ℓ
indices of each type. Subsets of these indices encode external column and row choices in binary,
and the resulting two evaluation matrices become m×m Vandermonde-type matrices. Their
Kronecker product then certifies the independence of m2 coeﬀicients.
9.2. The parameters and the chosen coeﬀicient family . Fix n≥32 and introduce the
formula parameters
(9.1) ℓ =⌈log2 n⌉, k = 2ℓ, m = n−k.
These parameters satisfy k≤n/ 2, m≥k + 1, and m≤2ℓ. Indeed, n > 4ℓ when ℓ = 5 , and
when ℓ≥6 one has n≥2ℓ− 1 + 1≥4ℓ+ 1. Here k is the number of marked entries and m is the
number of unmarked rows and columns left after those entries are placed on the diagonal. The
inequality m≤2ℓ means that ℓ bits suﬀice to index each of the m external rows or columns;
the inequality m≥k + 1 ensures that there are enough external indices for every injection that
appears below.
Lemma 9.1. If Y is a matching of k entries of X, then tdY (pern)≥m2.
Proof. We first identify m2 coeﬀicients indexed by a pair (α, β)∈{0, . . . , m −1}2. We then
specialize the unmarked entries, count the derivatives of those coeﬀicients with respect to the
m2 external-block entries, and show that the resulting Jacobian is invertible. The counting
separates external column choices from external row choices, exactly as in the 5×5 example.
Step 1: Coeﬀicients of marked diagonal entries. By permuting rows and columns, suppose Y =
{y1, . . . , y k}, where yi = xii. For S⊆[k], let cS denote the coeﬀicient of ∏
i∈S yi. Multilinearity
133
===== PAGE 136 =====
gives
(9.2) cS =
(∏
i∈S
∂
∂yi
)
pern(X)
⏐⏐⏐⏐⏐
y1=···=yk=0
.
Indeed, differentiating once with respect to each yi for i∈S selects the permutation terms that
use those marked diagonal entries. Setting all marked variables to zero then discards terms
using any additional marked entry. Equivalently, cS is the permanent of the matrix obtained by
deleting the rows and columns indexed by S and setting the remaining marked diagonal entries
to zero.
Step 2: Separate internal and external choices. Partition the marked indices as [k] = E⊔F ,
where E ={e0, . . . , e ℓ− 1}and F ={f0, . . . , f ℓ− 1}. Call these k rows and columns internal, index
the m external rows and columns by [m], and write X =
(D U
V W
)
, where D is k×k, U is k×m,
V is m×k, and W = ( wab) is m×m. Thus U matches internal rows to external columns, V
matches external rows to internal columns, and W matches external rows to external columns.
Choose distinct p1, . . . , p m ∈C and, independently, distinct q1, . . . , q m. For i̸= j in [k],
0≤u, v < ℓ, and a, b∈[m], specialize the unmarked variables by
Dij = 0, wab = 1,(9.3)
Ueu,b = p2u
b , Ufv,b = 1,
Va,eu = 1, Va,fv = q2v
a .(9.4)
Denote this specialization by ξ; derivatives are taken before evaluation at ξ. The e-indices
carry powers of pb when an internal row chooses external column b, whereas the f -indices carry
powers of qa when external row a chooses an internal column. All other internal–external edges
have weight 1. The powers 2u and 2v ensure that subsets of E and F encode integers without
colliding.
For 0≤α, β < m , let P (α)⊆E and Q(β)⊆F record the 1-digits of the ℓ-digit binary
expansions of α and β, with digit 0 least significant. Set T (α, β) = P (α)∪Q(β) and S(α, β) =
[k]\ T (α, β). Since m≤2ℓ, these definitions yield m2 coeﬀicients cS(α,β) of distinct marked
monomials. The complement in the definition of S is important: the indices in S have already
been matched through their marked diagonal entries, while the indices in T remain present in
the coeﬀicient permanent and must be matched through the unmarked blocks.
Our immediate goal is to show that these m2 coeﬀicients have an invertible Jacobian with
respect to the m2 variables wab. Consider the square matrix
J(α,β),(a,b) = ∂cS(α,β)
∂wab
⏐⏐⏐⏐
ξ
.
Once det J̸= 0 has been established, the Jacobian criterion immediately gives the conclusion
of the lemma. We first derive a combinatorial expression for each entry of J.
Step 3: Count the surviving permutation terms. Fix α, β, a, b, and abbreviate P = P (α),
Q = Q(β), T = P∪Q, and r =|T|. Because r≤k≤m−1, differentiation fixes external row a
to external column b and leaves precisely the internal rows and columns indexed by T . There
are m−1 external rows and m−1 external columns still available. At ξ, the internal block
on T is zero: its off-diagonal entries are zero by ( 9.3), and its marked diagonal entries were set
to zero in ( 9.2). Therefore no remaining internal row can match an internal column. Instead,
every internal row must match an external column, and every internal column must receive an
external row.
The first set of choices is an injection ρ : T ↪→[m]\{b}, assigning a distinct external column
to each internal row. The second is an injection θ : T ↪→[m]\{a}, assigning a distinct external
row to each internal column. They are independent because ρ selects columns and θ selects rows.
The m−1−r external rows and columns not used by these injections can then be matched in
(m−1−r)! ways, each of weight 1, since W specializes to the all-ones matrix. Hence
J(α,β),(a,b) = (m−1−r)!
∑
ρ:T ↪→ [m]\{ b}
∏
i∈T
Ui,ρ(i)
∑
θ:T ↪→ [m]\{ a}
∏
j∈T
Vθ(j),j.(9.5)
134
===== PAGE 137 =====
This is the general counterpart of the four elementary matching counts in the warm-up. To see
the row–column separation in a form that proves invertibility, we now express each injection
sum as the evaluation of a univariate polynomial.
Step 4: Encode forbidden-column choices by univariate polynomials. For P ⊆E, let DP =∑
eu∈P 2u and HP =∑
ρ:P ↪→ [m]
∏
eu∈P p2u
ρ(eu). Here HP is the total weight of injections into all
m external columns; in particular, H∅ = 1. Define gP∈C[z] recursively by
(9.6) g∅(z) = 1 , g P (z) = HP−
∑
eu∈P
z2u
gP \{ eu}(z) for P̸= ∅.
To interpret this recursion, fix b. An injection from P into [m] either avoids b or maps exactly
one index eu∈P to b. In the latter case, the remaining indices form an injection from P\{eu}
that avoids b, and the chosen index contributes p2u
b . Consequently, subtracting all injections
that use b from the unrestricted sum HP gives precisely the recursion ( 9.6) evaluated at z = pb.
Induction on|P|therefore yields
(9.7) gP (pb) =
∑
ρ:P ↪→ [m]\{ b}
∏
eu∈P
p2u
ρ(eu), deg gP = DP , [zDP ]gP (z) = (−1)|P ||P|!.
For completeness, the degree and leading coeﬀicient follow from the same induction. For P̸= ∅,
HP is constant, whereas each term z2u
gP \{ eu}(z) in ( 9.6) has degree DP and leading coeﬀicient
(−1)|P |−1(|P|−1)!. The preceding minus sign and the |P|choices of eu give the claimed
coeﬀicient (−1)|P ||P|!. In particular, g{e0}(z) = ∑
b pb−z, recovering the first factor in the
example. These leading coeﬀicients are nonzero because the ground field has characteristic
zero.
The row-side construction is identical. For Q⊆F , put
DQ =
∑
fv∈Q
2v, K Q =
∑
θ:Q↪→ [m]
∏
fv∈Q
q2v
θ(fv),
and recursively define
h∅(z) = 1 , h Q(z) = KQ−
∑
fv∈Q
z2v
hQ\{ fv}(z) for Q̸= ∅.
Partitioning row injections according to whether they use the forbidden row a proves
(9.8) hQ(qa) =
∑
θ:Q↪→ [m]\{ a}
∏
fv∈Q
q2v
θ(fv), deg hQ = DQ, [zDQ]hQ(z) = (−1)|Q||Q|!.
At this point the nontrivial weighted choices have been isolated: gP (pb) records the P -indices
that choose external columns, and hQ(qa) records the Q-indices that choose external rows. It
remains to account for indices whose edge weights are 1 and then prove that the resulting
evaluation matrices have full rank.
Step 5: Factor the Jacobian entries. Write (M )s = M (M−1)···(M−s + 1) and (M )0 = 1 .
In the first sum of ( 9.5), choose the images of P first. Their total weight is gP (pb) by ( 9.7).
Because every index in Q has U -weight one, each such injection has exactly (m−1−|P|)|Q|
extensions to the labeled indices in Q: there are m−1−|P|available external columns for
the first index, one fewer for the next, and so on. Similarly, in the second sum first choose the
images of Q. Their total weight is hQ(qa), and each choice has (m−1−|Q|)|P | extensions to
the indices in P , all with V -weight one.
Substituting these two counts into ( 9.5) separates the column parameter pb from the row
parameter qa:
J(α,β),(a,b) = LP,Q gP (pb)hQ(qa),(9.9)
LP,Q = (m−1−|P|−|Q|)!(m−1−|P|)|Q|(m−1−|Q|)|P |̸= 0.(9.10)
All factors are nonzero because |P|+|Q|≤m−1; in particular, every falling factorial counts
injections that actually exist. The scalar LP,Q depends on the selected coeﬀicient, but not on
the external row a or column b.
135
===== PAGE 138 =====
Step 6: Apply two Vandermonde matrices. Since DP (α) = α and DQ(β) = β, the evaluation
matrices Ap = ( gP (α)(pb))b,α and Aq = ( hQ(β)(qa))a,β are invertible. Indeed, ( 9.7) shows that
the polynomials
gP (0)(z), gP (1)(z), . . . , g P (m− 1)(z)
have respective degrees 0, 1, . . . , m −1 and nonzero leading coeﬀicients. Their coeﬀicient matrix
in the monomial basis 1, z, . . . , z m− 1 is therefore triangular with nonzero diagonal. Evaluating
at the distinct points p1, . . . , p m multiplies this coeﬀicient matrix by the Vandermonde matrix
(pj
b)b∈[m], 0≤ j<m, which is invertible because the pb are distinct. Thus Ap is invertible. The same
argument, using ( 9.8) and the distinct qa, proves that Aq is invertible.
After permuting columns, the matrix
(
gP (α)(pb)hQ(β)(qa)
)
(α,β),(a,b) is AT
p⊗AT
q and is therefore
invertible. By ( 9.9), J differs from it only by the nonzero row scalars ( 9.10). Hence det J̸=
0. The m2 selected coeﬀicients are consequently algebraically independent by the Jacobian
criterion, giving tdY (pern)≥m2. □
10. Formula lower bounds with and without division
We have established the two local ingredients needed for a formula lower bound. For a match-
ing Y of k = O(log n) matrix entries, Lem. 9.1 produces m2 = Ω(n2) algebraically independent
Y -coeﬀicients of pern. If the formula has no division, Lem. 8.1 charges those coeﬀicients to
occurrences of the variables in Y . Our first task is to select many matchings for which the re-
sulting occurrence charges do not overlap. We then extend the charging argument to formulas
with division by showing that rational operations along a path with only one marked child at
each gate contribute only a constant number of field parameters.
10.1. Packing matchings and the division-free bound. Throughout this section, k =
2⌈log2 n⌉and m = n−k are the parameters from ( 9.1). The useful notion of disjointness
concerns matrix entries, not their rows and columns: two matchings may use the same row or
the same column, as long as they never contain the same variable xij. This weaker condition is
exactly what prevents a variable-labeled leaf from being charged to two different matchings.
Proof of Thm. 1.2. Index the rows and columns by {0, . . . , n −1}. For a cyclic offset 0≤τ < n
and a row-block index 0≤j <⌊n/k ⌋, define
Yτ,j ={xjk+r, (jk+r+τ) mod n : 0≤r < k}.
Each Yτ,j is a matching: its k row indices are distinct, and adding the fixed offset τ modulo
n sends them to k distinct column indices. Moreover, any entry in one of these matchings
determines its parameters uniquely. Its row index i determines j =⌊i/k ⌋, and its column-
minus-row difference modulo n determines τ. Thus the matchings are pairwise entry-disjoint
even though different matchings can share rows and columns.
There are n choices of τ and⌊n/k ⌋choices of j, so their total number is
(10.1) ν = n
⌊n
k
⌋
≥n2
2k ,
where the inequality follows from k≤n/ 2 and⌊x⌋≥x/ 2 for x≥2.
Every matrix variable must occur at least once in Φ: otherwise its output would be inde-
pendent of that variable, whereas ∂ pern /∂x ij is the nonzero permanent of the complementary
(n−1)×(n−1) submatrix. In particular, tY (Φ)≥1 for every selected matching Y , so Lem. 8.1
applies. Together with Lem. 9.1, it gives the per-matching requirement
m2≤tdY (pern)≤4tY (Φ).
In words, a matching containing only k = O(log n) distinct variables must account for at least
m2/ 4 = Ω( n2) variable-labeled leaves, counted with repetition.
Because the matchings are entry-disjoint, a leaf labeled by xij contributes to at most one
of the numbers tY (Φ). Consequently, ∑
Y tY (Φ) ≤Lvar(Φ). Summing the preceding local
136
===== PAGE 139 =====
requirement, and then using ( 10.1), m≥n/ 2, and k≤4 log2 n, gives
Lvar(Φ)≥
∑
Y
tY (Φ)≥νm2
4 ≥n2m2
8k
≥n4
32k≥ n4
128 log2 n .
The total leaf and vertex counts are at least the number Lvar(Φ) of variable-labeled leaves.
Finally, a rooted binary formula with L(Φ) leaves has exactly G(Φ) = L(Φ)−1 internal gates.
Since the permanent is nonconstant and n≥32, L(Φ)≥2, and hence G(Φ)≥L(Φ)/ 2≥
Lvar(Φ)/ 2. This gives the stated gate bound as well. □
10.2. Allowing division: recovering a coeﬀicient field. To extend the argument, fix a
nonempty set Y of marked variables, let Z contain all remaining variables, and put R = C(Z).
A formula with division is evaluated symbolically in the rational-function field
C(Y, Z) = R(Y ).
Validity means that the denominator at each division gate is a nonzero element of this field;
it does not require the denominator to be nonzero after every numerical specialization of Z.
In particular, the point used in ( 9.3)–(9.4) to prove algebraic independence might make some
denominator of the formula vanish. This causes no problem: that point is applied only to the
polynomial coeﬀicients of pern, not to the rational formula or any of its gates.
The new diﬀiculty is that a division formula may represent its output using rational expres-
sions in the marked variables. Merely placing the output in a small rational-function field K(Y )
does not immediately say that its polynomial coeﬀicients belong to K. The next elementary
observation supplies precisely that missing implication.
Lemma 10.1. For fields K⊆E and a finite set Y of indeterminates, K(Y )∩E[Y ] = K[Y ]
inside E(Y ).
Proof. The inclusion K[Y ]⊆K(Y )∩E[Y ] is immediate. Conversely, suppose f∈K(Y )∩E[Y ].
Membership in K(Y ) gives polynomials P, Q∈K[Y ] with Q̸= 0 and
Qf = P in E[Y ].
To compare the coeﬀicients in E with those in K, regard E as a K-vector space. Extend a basis
of its one-dimensional subspace K⊆E to a basis of E, and let π : E→K be the associated
K-linear projection. Thus π fixes every element of K. Apply π coeﬀicientwise to polynomials
in E[Y ], writing π∗ for the resulting map.
Although π need not preserve products of arbitrary elements of E, its K-linearity ensures
that it commutes with multiplication by the polynomial Q∈K[Y ]. Therefore
Qπ∗(f ) = π∗(Qf ) = π∗(P ) = P.
Subtracting from Qf = P gives Q(f−π∗(f )) = 0 . Since E[Y ] is an integral domain and Q̸= 0,
we conclude that f = π∗(f )∈K[Y ], as required. □
It remains to find a small field K containing the rational parameters that genuinely influence
the marked variables. As in the division-free argument, mark each vertex whose subformula
contains a Y -labeled leaf. A maximal path of gates with only one marked child can contain
many unmarked computations, but all of its influence is captured by one fractional linear trans-
formation. The essential count is therefore charged at gates where two marked subformulas
meet.
Lemma 10.2. Suppose that a valid formula with division computes a polynomial f∈C[Y, Z]
and contains t≥1 leaves labeled by variables in Y . Then tdY (f )≤6t−3 < 6t.
Proof. Put R = C(Z), and mark precisely those vertices having at least one Y -labeled descen-
dant. At a gate with one marked child, the other child has no marked leaves and therefore
137
===== PAGE 140 =====
computes a rational function h∈R. If the marked child computes u∈R(Y ), the possible
outputs are
u + h, u −h, h −u, hu, u/h, h/u,
where validity requires h̸= 0 for u/h and u̸= 0 for h/u . Every such operation has the fractional
linear form
u↦−→au + b
cu + d , M =
(a b
c d
)
∈R2× 2.
For example, the transformations u + h, hu, u/h , and h/u are represented, respectively, by
(1 h
0 1
)
,
(h 0
0 1
)
,
(1 0
0 h
)
,
(0 h
1 0
)
.
It is important not to require these matrices to be invertible. When h = 0, multiplication by h
is a valid constant-zero operation represented by the singular, but nonzero, second matrix.
Composition of fractional linear transformations corresponds to multiplication of their rep-
resenting matrices. Moreover, although singular matrices are allowed, the composite matrix
for a valid marked path cannot become the zero matrix. To see this, suppose that the current
marked value is
uj = aju0 + bj
cju0 + dj
, c ju0 + dj̸= 0,
and the next unary marked gate applies u↦→(au + b)/ (cu + d). The denominator represented
by the composite matrix is
c(aju0 + bj) + d(cju0 + dj) = ( cju0 + dj)(cuj + d)̸= 0 in R(Y ).
The first factor is nonzero by the inductive representation, and the second is nonzero because the
gate is valid. In particular, the composite matrix has a nonzero entry. Dividing all four entries
by any one nonzero entry leaves the represented rational function unchanged and normalizes
that entry to 1. Such a normalized matrix is therefore described by at most three elements of
R, even when it is singular.
We now prove the following more precise invariant by induction on a marked subformula with
s≥1 marked leaves: its output can be written as
ag + b
cg + d , g ∈C(Γ)(Y ), Γ⊆R, |Γ|≤6s−6,
for some matrix over R, with cg + d̸= 0 in R(Y ). The outer matrix is deliberately not counted
in Γ until the subformula meets another marked subformula or reaches the root.
For a marked leaf labeled by y∈Y , take g = y, Γ = ∅, and the identity matrix. If the
root gate of the subformula has only one marked child, compose its fractional linear transfor-
mation with the child’s outer matrix. The preceding validity argument shows that the resulting
denominator remains nonzero, and no new element needs to be added to Γ.
Suppose instead that the gate has two marked children with s1, s2≥1 marked leaves. Nor-
malize each child’s outer matrix and adjoin its at most three nontrivial entries to the union of
the two existing parameter sets. If Γ denotes the resulting set, both child outputs belong to the
single field C(Γ)(Y ). Apply the gate operation to these two outputs, use the resulting rational
function as the new inner function g, and take the identity as the new outer matrix. When
the operation is division, the divisor is nonzero in R(Y ) by validity, hence also nonzero in the
subfield C(Γ)(Y ); thus the new inner function is well-defined. Finally, because s = s1 + s2, the
parameter count is at most
(6s1−6) + (6s2−6) + 6 = 6( s1 + s2)−6.
This completes the induction.
At the formula root, the invariant gives at most 6t−6 parameters for the inner function.
Normalize the final outer matrix and adjoin its at most three remaining entries. We obtain a
set Γ′⊆R satisfying
|Γ′|≤(6t−6) + 3 = 6 t−3
138
===== PAGE 141 =====
such that the complete formula output belongs to K(Y ), where K = C(Γ′)⊆R. On the other
hand, the hypothesis that the output is a polynomial gives f ∈C[Y, Z]⊆R[Y ]. Applying
Lem. 10.1 with E = R therefore yields
f∈K(Y )∩R[Y ] = K[Y ].
Thus every coeﬀicient of f as a polynomial in Y belongs to the same field K. Since a field
generated by|Γ′|elements has transcendence degree at most |Γ′|,
tdY (f )≤trdegC K≤|Γ′|≤6t−3 < 6t.
This is the desired division-formula analogue of Lem. 8.1. □
10.3. Completing the lower bound with division. The coeﬀicient-independence construc-
tion is a property of the permanent itself and therefore remains unchanged when the formula is
allowed to use division. Only its translation into a lower bound on marked occurrences changes,
from a factor of 4 to a factor of 6.
Proof of Thm. 1.3. Use the same parameters ( 9.1) and the same ν pairwise entry-disjoint match-
ings constructed in ( 10.1). If some matching Y contributes no variable-labeled leaf, every gate
of the formula belongs to the rational-function field C(X\Y ). Its output would then be inde-
pendent of all variables in Y , contradicting its equality to pern. Therefore tY (Φ)≥1 for every
selected matching, as required to apply Lem. 10.2.
For each matching, Lem. 9.1 and Lem. 10.2 now give
m2≤tdY (pern)≤6tY (Φ)−3 < 6tY (Φ).
As before, entry-disjointness guarantees that no variable-labeled leaf is charged twice. Summing
over all ν matchings, and using m≥n/ 2 and k≤4 log2 n, yields
Lvar(Φ)≥
∑
Y
tY (Φ)≥νm2
6 ≥n2m2
12k
≥n4
48k≥ n4
192 log2 n .
Finally, allowing division changes the allowed labels of internal gates but does not change the
fact that the formula is a rooted binary tree. Consequently, L(Φ)≥Lvar(Φ) and G(Φ) =
L(Φ)−1 ≥L(Φ)/ 2, giving the remaining leaf, vertex, and gate bounds exactly as in the
division-free case. □
11. Comparison with the determinant
For the generic determinant, the known unrestricted formula bounds are Ω(n3) and nO(log n).
The lower bound holds even with division [ Kal85], while the upper bound follows by unfolding
the polynomial-size, O(log2 n)-depth circuits of [ Ber84]. It is therefore natural to ask whether
either of our permanent arguments also improves the corresponding determinant bound. We
show that the answer is negative for two separate reasons. On the formula side, the coeﬀicients
associated with a small set of determinant entries satisfy many algebraic relations. On the
circuit side, every homogeneous specialization of the determinant has a critical locus that is too
large for our geometric certificate to give a superquadratic bound.
11.1. Coeﬀicient independence and a cubic formula ceiling. The formula argument re-
quires many algebraically independent coeﬀicients for small, entry-disjoint sets of variables.
Recall that tdY (f ) counts the maximum number of algebraically independent coeﬀicients ob-
tained by expanding f in the variables of Y ; those coeﬀicients are polynomials in the remaining
variables. For the permanent, a matching of only O(log n) entries contributes Ω(n2) independent
coeﬀicients. We first explain why this crucial feature fails for the determinant.
139
===== PAGE 142 =====
Let Y be a matching of k < n entries of a generic n×n matrix X. Permuting rows and
columns moves its marked entries to the first k diagonal positions. Separate the corresponding
rows and columns from the others, and write
X =
(diag(Y ) + D0 U
V W
)
, δ = det W, S = D0−U W− 1V.
Here diag(Y ) is the k×k diagonal matrix of marked variables, D0 contains the unmarked entries
of the same block and has zero diagonal, and U, V, W also contain only unmarked variables.
The complementary block W is a generic (n−k)×(n−k) matrix, so its determinant δ is
a nonzero polynomial. Consequently, W is invertible over the rational-function field of the
unmarked variables: its entries need not be invertible as polynomials, but W − 1 = adj(W )/δ is
a well-defined matrix of rational functions. The Schur complement identity then gives
det X = δdet
(
diag(Y ) + S
)
.
Although the right-hand side uses rational functions to describe the coeﬀicients, the identity
holds in the rational-function field, and its left-hand side is still the original polynomial.
To read off an individual coeﬀicient, let T⊆[k]. In the determinant expansion, selecting yi
for every i∈T fixes those rows and columns to their diagonal positions. The remaining rows
and columns therefore contribute the principal minor on [k]\T :
[ ∏
i∈T
yi
]
det X = δdet S[k]\ T,[k]\ T ,
where the determinant of an empty matrix is 1. Thus every Y -coeﬀicient belongs to the field
generated by the single element δ and the k2 entries of S. A field generated by k2 + 1 elements
has transcendence degree at most k2 + 1, and hence
tdY (det X)≤k2 + 1.
Consequently, matchings of size O(log n) yield at most O(log2 n) independent coeﬀicients for
the determinant, whereas § 9 produces Ω(n2) independent coeﬀicients for the permanent. The
determinant’s Schur complement compresses a potentially exponential family of coeﬀicients into
only O(k2) parameters.
One might try to recover a stronger formula lower bound by choosing marked entries that
are not a matching. The same obstruction still applies. Suppose Y is any nonempty set of k
marked entries, where 1≤k < n . Its occupied row set and occupied column set each have
size at most k; enlarge the smaller set, if necessary, so both have a common size s≤k. After
permuting rows and columns, all marked entries lie in the upper-left s×s block, which we write
as B(Y ) + D0. Here B(Y ) contains the marked variables and vanishes in the other positions,
while D0 contains the unmarked entries. Because s < n , the complementary block W is again
generically invertible. The Schur complement expresses every Y -coeﬀicient in the field generated
by δ = det W and the s2 entries of D0−U W− 1V . Therefore tdY (det X)≤s2 + 1≤nk. For
the last inequality, s≤k < n implies s2 + 1≤k2 + 1≤nk. If k≥n, we instead use the trivial
bound tdY (det X)≤n2≤nk: there are only n2 matrix variables in total.
We have therefore proved tdY (det X)≤n|Y|for every nonempty block Y . If Y1, . . . , Y q are
pairwise entry-disjoint, then their total size is at most n2, and summing the individual bounds
gives
(11.1)
q∑
j=1
tdYj (det X)≤n
q∑
j=1
|Yj|≤n3.
Thus summing blockwise coeﬀicient transcendence degrees cannot give a supercubic determinant
formula lower bound, regardless of how the entry-disjoint blocks are chosen.
11.2. F ull matchings recover the cubic determinant bound. The cubic ceiling is not
merely an upper limit on what this method might prove: using full matchings, the same method
actually recovers a cubic lower bound. Let Y consist of all n diagonal entries, and write
X = diag(Y ) + A, a ii = 0.
140
===== PAGE 143 =====
Expanding as above, the Y -coeﬀicients are exactly the principal minors of the zero-diagonal
matrix A; a principal minor indexed by I⊆[n] is det AI,I .
The first question is how many of these principal minors can be algebraically independent.
If D is an invertible diagonal matrix, then
(DAD− 1)I,I = DI,I AI,I D− 1
I,I ,
so diagonal conjugation leaves every principal minor unchanged. On the generic open set where
a1i ̸= 0 for i > 1, choose λi = a1i and D = diag(1 , λ2, . . . , λ n). The matrix B = DAD− 1
satisfies b1i = 1 for every i > 1. Conversely, A = D− 1BD, so the original off-diagonal entries
are birationally equivalent to the n−1 nonzero parameters λi together with the remaining
normalized entries of B. The latter entries are therefore algebraically independent, and their
number is
n(n−1)−(n−1) = ( n−1)2
because the normalization fixes precisely the n−1 first-row entries. In particular, all principal
minors belong to the rational-function field generated by these (n−1)2 normalized entries. That
field has transcendence degree (n−1)2, giving the corresponding upper bound.
For the matching lower bound, it is enough to recover all normalized entries up to algebraic
ambiguity from the principal minors. Continue to write A for the normalized matrix, and set
ti = ai1 for i > 1. For distinct i, j > 1, its principal minors of sizes two and three are
det A{1,i},{1,i} =−ti,
det A{i,j},{i,j} =−aijaji,
det A{1,i,j},{1,i,j} = aijtj + ajiti.
Thus the field generated by the principal minors contains ti, the product pij = aijaji, and the
linear combination qij = aijtj + ajiti. Multiplying the last identity by aij gives
tja2
ij−qijaij + pijti = 0.
Its leading coeﬀicient tj is a nonzero rational function, so aij is algebraic of degree at most two
over the field of principal minors; the same argument applies to aji. Every normalized entry is
consequently algebraic over that field. Algebraic extensions preserve transcendence degree, so
the upper bound established by normalization is attained:
tdY (det X) = ( n−1)2.
Now let Φ be a formula computing det X, and partition all n2 entries into the n cyclic full
matchings
Yτ ={xi,(i+τ) mod n : 0≤i < n}, 0≤τ < n,
where rows and columns are indexed by {0, . . . , n −1}. Each matching has coeﬀicient tran-
scendence degree (n−1)2 by the preceding argument, since row and column permutations only
relabel the entries. If the formula is division-free, Lem. 8.1 gives (n−1)2≤4tYτ (Φ)−2. If it
permits valid division, Lem. 10.2 instead gives (n−1)2≤6tYτ (Φ)−3. Summing over the n
disjoint matchings therefore yields
Lvar(Φ)≥n((n−1)2 + 2)
4 , L var(Φ)≥n((n−1)2 + 3)
6
without division and with valid division. Thus the cubic ceiling in ( 11.1) is attained up to a
constant factor.
11.3. Critical loci obstruct the geometric circuit argument. The circuit proof needs an
aﬀine specialization with many active variables, reasonably high degree, and a critical locus of
large codimension. We first inspect the determinant analogue of the specialization used for the
permanent, and then show that the obstruction persists for every homogeneous determinant
specialization.
141
===== PAGE 144 =====
Replacing the permanent by the determinant in the example from § 2 gives
det


u v 1 1
w z 1 1
p q 2 −2
r s 2 −2

= 4
(
(u−w)(q−s)−(v−z)(p−r)
)
,
a single 2×2 determinant rather than a sum of independent block permanents. The cancellations
have compressed all the variable dependence into a much smaller matrix.
More generally, suppose 2 ≤d ≤min{r, s}, and let X, U, V have respective sizes r×s,
r×(r−d), and (s−d)×s, with U, V constant. The block matrix
(X U
V 0
)
is square of size r + s−d. If U fails to have full column rank, its last r−d columns are linearly
dependent. If V fails to have full row rank, its last s−d rows are linearly dependent. In either
case the determinant is identically zero.
Suppose therefore that U and V have their full respective ranks. Choose a full-row-rank d×r
matrix A whose rows span the left kernel of U , so AU = 0. Likewise, choose a full-column-rank
s×d matrix C whose columns span the kernel of V , so V C = 0 . Constant changes of basis
separating these kernels from complementary subspaces give
det
(X U
V 0
)
= c det(AXC ),
where c̸= 0 depends only on the constant basis changes. In other words, the original deter-
minant retains only the induced map from the d-dimensional kernel of V to the d-dimensional
quotient by the image of U .
The linear map X↦→AXC is surjective onto the space of d×d matrices. Indeed, full row rank
provides a right inverse A′with AA′= Id, while full column rank provides a left inverse C′with
C′C = Id; for any d×d matrix H, taking X = A′HC ′ gives AXC = H. The first derivatives
of a determinant are its (d−1)×(d−1) cofactors. They vanish simultaneously precisely when
the matrix has rank at most d−2. The space of d×d matrices of rank at most r has dimension
r(2d−r): a rank- r factorization has two d×r factors, with r2 parameters accounting for their
common change of basis. Taking r = d−2, its codimension in the d2-dimensional matrix space
is
d2−(d−2)(d + 2) =
(
d−(d−2)
) 2 = 4.
IfL(X) = AXC , the chain rule gives d(det◦L)X =L∗(d detL(X)). Surjectivity of L makes its
dualL∗ injective, so the critical locus is exactly the inverse image of the smaller determinant’s
critical locus. Moreover, choosing a complementary subspace to kerL identifies the domain
with kerL⊕Cd× d. Under this identification, an inverse image is a product with kerL, which
preserves codimension. The specialized determinant therefore also has critical-locus codimension
4. Thus this block construction cannot provide the Θ(n2) critical-locus codimension that drove
the permanent circuit bound.
Importantly, changing the specialization does not resolve the problem. Let n ≥5, and
obtain P by substituting aﬀine linear forms into detn. Suppose that the resulting polynomial is
homogeneous of degree d > 2. For a homogeneous polynomial of degree d, Euler’s identity says
dP (x) =
∑
i
xi
∂P
∂xi
(x).
Because the ground field has characteristic zero, every critical point of P also satisfies P (x) = 0 .
Consequently, Crit(P ) is exactly the singular locus of the hypersurface defined by P = 0.
Recall that the determinantal complexity dc(P ) is the smallest size of a matrix of aﬀine
linear forms having determinant P . Since P itself is an aﬀine specialization of detn, the original
specialization provides such a representation of size n; therefore dc(P )≤n. If codim Crit(P ) >
4, then [ ABV17, Thm. 1.2] implies codim Crit(P ) + 1 ≤dc(P )≤n: the singular locus of a
142
===== PAGE 145 =====
polynomial with a small determinantal representation cannot have arbitrarily large codimension.
Otherwise, codim Crit(P )≤4≤n−1. In either case,
codim Crit(P )≤n−1.
Finally, the slicing parameter k in Lem. 4.2 cannot exceed the critical-locus codimension: its
hypothesis is precisely dim Crit(P )≤m−k, where m is the number of variables of P . Therefore
k≤n−1. Also d≤n, since substituting aﬀine linear forms into a degree- n determinant cannot
increase its degree. The largest circuit lower bound obtainable from ( 4.2) is consequently
k log2(d−1)
3 ≤(n−1) log2(n−1)
3 .
For d = 2 , the certificate is zero because log2(d−1) = 0 . Even for larger degrees, it is only
O(n log n). This is below the elementary n2−1 gate lower bound: the determinant depends on
all n2 individual input variables, and combining n2 distinct inputs into one output with binary
arithmetic gates requires at least n2−1 gates. Thus this method, in its present form, cannot
establish a superquadratic determinant lower bound.
12. Related work
The two lower bounds interact with several bodies of work that use similar words for sub-
stantially different computational models and complexity measures. We first distinguish those
models and recall their established bounds. We then place the geometric circuit proof, the
coeﬀicient-independence formula proof, and the restricted-depth literature in their respective
contexts. In particular, a lower bound for representing a polynomial as a determinant, a lower
bound for general arithmetic circuits, and a lower bound for formulas are logically different
statements.
12.1. Historical bounds and computational models. The modern complexity-theoretic
comparison between permanent and determinant begins with two distinct results of Valiant.
His algebraic completeness theorem makes the permanent complete for VNP over fields of char-
acteristic different from two [ Val79a]. Here completeness concerns families of polynomials and
arithmetic projections: variables of one polynomial are replaced by variables or field constants
to obtain another polynomial. His separate counting-complexity theorem proves that evaluating
the permanent of a zero–one matrix is #P-complete [ Val79b]. The two results motivate related
questions, but one concerns symbolic arithmetic computation and the other a Boolean counting
problem. In characteristic two, the determinant and permanent coincide, so even the distinction
between the two polynomials depends on the ground field.
Several surveys describe this broader landscape. Bürgisser–Clausen–Shokrollahi [ BCS97],
Shpilka–Yehudayoff [SY10], and Kayal–Saptharishi [ KS14] introduce algebraic complexity and
arithmetic lower-bound methods. Bürgisser surveys algebraic completeness classes [ Bür24];
Chen–Kayal–Wigderson survey partial-derivative techniques [ CKW11]; and Bürgisser, Lands-
berg, Manivel, and Weyman [ BLMW11], together with Bläser and Ikenmeyer [ BI25], discuss
geometric complexity theory.
It is important to distinguish three models. An unrestricted arithmetic circuit may reuse any
previously computed intermediate value. A formula is a circuit whose underlying graph is a tree,
so every reuse must instead be recomputed. A determinantal representation of f is an expression
f = det(A) for a matrix A of aﬀine linear forms; its minimum matrix dimension is the determi-
nantal complexity dc(f ). The determinant is complete, under polynomial-size projections, for al-
gebraic branching programs, or equivalently weakly skew circuits. It is not known to be complete
for unrestricted polynomial-size arithmetic circuits [ MP08]. Consequently, a superpolynomial
lower bound on dc(pern) separates the permanent from the branching-program/weakly-skew
model but does not by itself establish VP̸= VNP for general circuits.
There is nevertheless a weaker connection to the general-circuit model. Valiant’s determinant
simulation, together with circuit balancing, transforms a polynomial-size general circuit into a
143
===== PAGE 146 =====
quasipolynomial-size determinantal representation [ Val79a, VSBR83, BI25]. A superquasipoly-
nomial lower bound on determinantal complexity would therefore rule out polynomial-size gen-
eral circuits, whereas a merely superpolynomial determinantal bound would not. The distinc-
tion matters for Thm. 1.1: its lower bound concerns the number of gates in an unrestricted
division-free circuit directly, not the dimension of a determinantal representation.
Write N = n2 for the number of entries of an n×n matrix. Before the present result, the
general-circuit lower bound known specifically for either detn or pern was only Ω(n2) = Ω( N ).
The classical Ω(N log d) lower bounds of Strassen and Baur–Strassen apply to other explicit
degree-d polynomial families, such as sums of powers; they do not assert the same bound for
either matrix polynomial [ Str73a, BS83, KS14]. Thm. 1.1 instead establishes the permanent-
specific bound Ω(N log log N ) for division-free circuits. It neither proves such a bound for the
determinant nor treats circuits with division.
For upper bounds, the determinant has polynomial-size division-free circuits [ Ber84]. Balanc-
ing and unfolding suitable circuits gives determinant formulas of size nO(log n) [Hya79, VSBR83].
For the permanent, Ryser’s inclusion–exclusion identity yields exponential-size circuits and, if
intermediate computations cannot be shared, formulas of size O(n22n) [Rys63].
For unrestricted division-free formulas, the previous lower bounds for both matrix polynomi-
als were Ω(n3) = Ω( N 3/ 2) [Kal85, KS14]. Kalorkoti’s determinant lower bound even permits
rational formulas with valid division [ Kal85]; his published result should not be interpreted
as the corresponding division-formula theorem for the permanent. Thms. 1.2 and 1.3 raise
the permanent-specific bounds to Ω(n4/ log n) = Ω( N 2/ log N ) without division and with valid
division, respectively. This comparison is specific to the permanent: for a different explicit
polynomial, Chatterjee–Kumar–She–Volk prove an Ω(N 2) unrestricted formula lower bound for
a suitable elementary symmetric polynomial [ CKSV22]. Raz’s nΩ(log n) bounds for the determi-
nant and permanent are numerically stronger but concern syntactically multilinear formulas, a
restricted model rather than the general formulas considered here [ Raz09].
12.2. Determinantal representations and geometric lower bounds. The permanent-
versus-determinant problem is often stated in terms of determinantal representations: how
large must a matrix of aﬀine linear forms be if its determinant is pern? Early work of von zur
Gathen and Cai studied versions of this projection problem [ vzG87, Cai90]. Mignon–Ressayre
proved
dc(pern)≥n2
2
over characteristic zero by comparing Hessians at suitable points [ MR04]. Cai–Chen–Li extend a
quadratic bound to fields of characteristic different from two [ CCL10]; in the opposite direction,
Grenet gives determinantal representations of size 2n−1 [Gre12].
There are also geometric variants in which the permanent is allowed to arise as a limit of
determinantal representations. Landsberg–Manivel–Ressayre obtain quadratic lower bounds
for this border determinantal complexity using dual varieties [ LMR13]. Mulmuley–Sohoni place
determinantal representation and orbit-closure questions in the representation-theoretic frame-
work of geometric complexity theory [ MS01]. All these results measure the dimension of a
determinant representation, or its border analogue. They are not lower bounds on the number
of gates in an arbitrary arithmetic circuit, and therefore should not be confused with prior
superquadratic general-circuit bounds.
The geometric quantity relevant to the present paper is more elementary to describe. If P is
a polynomial in m variables, its critical locus Crit(P ) is the set where all first partial derivatives
vanish; its codimension in the ambient aﬀine space Cm is m−dim Crit(P ). The singular locus of
the hypersurface P = 0 additionally requires P = 0 ; its codimension here is likewise measured
in Cm, not inside the hypersurface. For a homogeneous polynomial of positive degree over C,
Euler’s identity implies that the derivative equations already force P = 0 , so these two loci
agree.
These loci have several antecedents in algebraic complexity. Alper–Bogart–Velasco lower-
bound determinantal complexity using the codimension of the singular locus and determine
144
===== PAGE 147 =====
the exact determinantal complexity of the 3×3 permanent [ ABV17]. Chatterjee–Kumar–
She–Volk use the common zero set of first derivatives for quadratic branching-program and
formula lower bounds [ CKSV22], while Gesmundo–Ghosal–Ikenmeyer–Lysikov relate singular-
locus codimension to homogeneous branching-program complexity [ GGIL22].
Our use of the same geometric object is different. We first obtain a homogeneous polyno-
mial P by replacing entries of the permanent matrix with aﬀine linear forms. We then prove
that Crit(P ) has large codimension, choose a linear subspace avoiding its nonzero points, and
apply a degree bound to the restricted gradient map. The resulting lower bound concerns the
original unrestricted circuit directly; at no point do we identify circuit size with determinantal
complexity.
The singular-locus theorem of Alper–Bogart–Velasco also makes the determinant obstruction
transparent. Suppose n≥5, substitute aﬀine linear forms into detn, and assume the resulting
polynomial P is homogeneous of degree at least three. The specialization supplies an n×n
determinantal representation, so dc(P )≤n. If codim Crit(P ) > 4, the singular-locus theorem in
[ABV17] gives codim Crit(P ) + 1≤dc(P )≤n. If the codimension is at most 4, the assumption
n≥5 already bounds it by n−1. Consequently, in either case,
codim Crit(P )≤n−1.
Thus a determinant specialization cannot supply the Θ(n2) critical-locus codimension needed by
the present circuit argument. Section 11 explains the implication, including the low-codimension
case, in detail.
A related literature studies the polynomial ideals generated by subpermanents. Lauben-
bacher and Swanson investigate permanental ideals [ LS00]. Efremenko, Landsberg, Schenck,
and Weyman study minimal free resolutions of such ideals motivated by geometric complexity
theory [ ELSW18a]. Boralevi, Carlini, Michałek, and Ventura give codimension bounds for per-
manental varieties [ BCMV25]. In particular, their results imply that, for n≥6, the critical
locus of the full permanent satisfies
6≤codim Crit(pern)≤2n.
The upper bound shows why applying our gradient argument directly to pern cannot work:
its critical-locus codimension is only O(n), rather than the Θ(n2) required in Prop. 4.3. The
specially constructed aﬀine specialization is therefore essential. There is also an important
distinction between the ideals themselves. The cited permanental ideal papers usually generate
an ideal from a collection of individual subpermanents, whereas § 5 studies the first derivatives of
a single sum of subpermanents. These families of equations need not define the same geometric
object.
12.3. Differentiation, degree bounds, and the aﬀine specialization. Proposition 4.3
combines two classical ideas: eﬀicient simultaneous differentiation and a degree bound for
polynomial maps. Strassen used Bézout-type degree arguments to lower-bound the simulta-
neous computation of powers and elementary symmetric functions [ Str73a]. Baur–Strassen
then showed that a straight-line program computing one polynomial f can be augmented to
compute f and all its first partial derivatives with only constant-factor overhead [ BS83]. The
history and many applications of partial-derivative techniques are surveyed by Chen–Kayal–
Wigderson [ CKW11]; the Nisan–Wigderson partial-derivative method is another important,
model-dependent development [ NW97].
The special polynomial
f (x1, . . . , x k) = d− 1
k∑
i=1
xd
i
makes the degree argument particularly transparent. Its gradient is (xd− 1
1 , . . . , x d− 1
k ), and setting
these outputs equal to generic nonzero constants gives (d−1)k distinct solutions. Computing the
same outputs with q multiplications produces a system containing q quadratic multiplication-
gate equations. Bézout’s inequality bounds the number of isolated solutions of that system
by 2q. Consequently (d−1)k ≤2q, yielding q = Ω( k log d). This argument works because
the chosen gradient has an isolated common zero and a large generic fiber. Neither fact is an
145
===== PAGE 148 =====
automatic consequence of the degree and number of variables of an arbitrary polynomial, so
the classical Ω(k log d) conclusion cannot simply be substituted for a permanent or determinant
lower bound.
The exact differentiation overhead also depends on the cost model. Proposition 4.3 counts
nonscalar multiplications and treats aﬀine operations as free. For an original product gate, one
forward multiplication and at most two reverse-mode multiplications suﬀice, giving the factor
three used there. The full Baur–Strassen theorem also accounts for additions, scalar operations,
and divisions; it does not justify the unqualified statement that a circuit with s total gates
always has a gradient circuit with at most 3s total gates [ BS83]. Furthermore, reverse-mode
differentiation reuses intermediate values, an operation available to circuits but not to formulas.
Ramya–Shastri exhibit multi-output formula and planar-circuit separations demonstrating that
the analogous constant-overhead claim fails in those restricted models [ RS26]. This is why the
formula argument needs its separate coeﬀicient-transcendence measure.
The remaining ingredients of the circuit proof likewise have classical precedents. A multipli-
cation gate can be represented by a quadratic equation for its output; aﬀine Bézout bounds
the number of isolated common solutions; a generic linear slice avoids a suﬀiciently low-
dimensional critical locus; and the degree of the resulting finite gradient map counts a generic
fiber [ Str73a, BS83, Hei83, KS14]. The challenge specific to the permanent is to construct a
specialization for which these standard tools apply simultaneously: the specialized polynomial
must have degree d≍log n, retain Θ(n2) variables, and have critical-locus codimension Θ(n2).
The first ingredient in that construction is the minor-sum polynomial Mt,s,d of ( 5.1). Its
monomials encode size- d matchings between the rows and columns of a t×s matrix; summing
the corresponding products is equivalent to summing all d×d permanental minors. To analyze
its derivatives, § 5 rewrites sums over injective assignments of rows to columns in terms of
the power sums pB. This is Möbius inversion on the partition lattice: each partition records
which rows were assigned the same column, and its Möbius coeﬀicient corrects the resulting
overcount. The general incidence-algebra framework originates with Rota [ Rot64]; the specific
permanental expansion is the rectangular Binet–Minc identity [ Min79]. Forbes also uses this
identity for characteristic-independent set-multilinearization [ For24].
The second ingredient is realizing an appropriate sum of these minor-sum polynomials as
a single specialization of a larger permanent. Friedland–Levy already realize the sum of all
d×d permanental minors as a larger permanent by adjoining all-ones and zero blocks [ FL06].
Lemma 6.1 refines that completion: it selects constant columns using roots of unity so that
the d upper rows not assigned to those constant columns all belong to a single row block. The
surviving terms therefore split into the separate block polynomials whose critical loci can be
bounded independently.
The square-zero algebra used to verify this cancellation has its own precedents. Feinsilver–
McSorley use commuting square-zero “zeon” variables whose induced matrix coeﬀicients are per-
manents [FM11]; Butera–Pernici use commuting Grassmann-even nilpotent variables to encode
sums of permanental minors and bipartite matchings [ BP15]. Signed and Fourier/root-of-unity
coeﬀicient filters likewise occur in Ryser’s and Glynn’s permanent identities and in Aaronson–
Hance’s generalized Glynn estimator [ Rys63, Gly10, AH14]. These precedents supply the un-
derlying square-zero and cancellation ideas, but not the particular simultaneous block-selective
specialization of Lem. 6.1. For the determinant, complementary maximal minors instead satisfy
Plücker relations, obstructing the same block-supported pattern. The construction therefore
uses a structural difference between permanents and determinants rather than merely replacing
unsigned terms with signed ones.
12.4. F ormula methods, coeﬀicient independence, and division. The formula argument
adapts a block-counting principle introduced in a different computational setting. Nečiporuk
partitioned the variables of a Boolean function and lower-bounded formula size by adding the
information required by the individual blocks [ Nec66]. Kalorkoti translated this general idea to
rational arithmetic formulas using algebraic independence of coeﬀicient families [ Kal85]. The
exposition in [ KS14, §3.2] describes the corresponding arithmetic measure explicitly.
146
===== PAGE 149 =====
Concretely, choose a block Y of variables of a polynomial f and expand f as a polynomial in Y .
Its coeﬀicients are polynomials in the remaining variables. The coeﬀicient transcendence degree
tdY (f ) counts the maximum number of those coeﬀicients that are algebraically independent:
no nonzero polynomial relation with complex coeﬀicients holds among the chosen coeﬀicient
polynomials. A formula with few occurrences of variables from Y can introduce only few
independent coeﬀicients. If the variable blocks are disjoint, their occurrence requirements can
be added without counting any formula leaf twice. Applying this principle to n entry-disjoint
full diagonals of a matrix gives the classical Ω(n3) division-free formula bounds for both the
permanent and determinant.
An especially close antecedent for the choice of blocks is work of Hrubeš–Joglekar [ HJ25].
Their proof also selects a matching of Θ(log n) matrix entries, exploits a specialization of the
permanent on that matching, packs Θ(n2/ log n) pairwise entry-disjoint matchings, and adds the
resulting occurrence requirements. In the model of read-bounded determinantal representations,
they obtain an Ω(n5/ 2/ log n) lower bound on variable-containing matrix entries and rule out
read-o(√n/ log n) representations. The present argument uses the same matching-and-packing
architecture in a different model. It proves that each short matching already produces Ω(n2)
algebraically independent coeﬀicient polynomials, and charges this quantity directly to leaves
of an unrestricted arithmetic formula.
The new independence witness can be understood through the Jacobian criterion. Over
characteristic zero, coeﬀicient polynomials are algebraically independent when an appropri-
ate Jacobian matrix has full rank. Lem. 9.1 specializes the unmarked matrix entries so that
this Jacobian factors into two Vandermonde evaluation matrices, one associated with an ex-
ternal row and the other with an external column. Their Kronecker product has full rank,
certifying Ω(n2) independent coeﬀicients for a matching of only O(log n) entries. Algebraic in-
dependence and the Jacobian criterion also play central roles in identity testing and restricted-
model lower bounds [ BMS11]. In particular, Agrawal–Saha–Saptharishi–Saxena use Jacobian
and transcendence-degree methods to lower-bound all immanants, including the permanent
and determinant, in bounded-occurrence and bounded-transcendence-depth models [ ASSS16].
Boralevi–Carlini–Michałek–Ventura also study algebraic independence of selected subperma-
nents [ BCMV25], but their coeﬀicient families and geometric objectives differ from those in
Lem. 9.1.
This block-based method has a nearly matching intrinsic ceiling. For an N -variate multilinear
polynomial and a block Y , its coeﬀicient contribution satisfies
tdY (f )≤min{2|Y |, N−|Y|}.
Indeed, multilinearity gives at most 2|Y |coeﬀicient polynomials, while those coeﬀicients involve
only the N−|Y|remaining variables. Summing this contribution over a partition of the variables
gives at most O(N 2/ log N ) in the usual Nečiporuk–Kalorkoti framework; see [ CKSV22]. Hence
the permanent bound Ω(N 2/ log N ) essentially saturates this particular framework. The Ω(N 2)
lower bound for an elementary symmetric polynomial in [ CKSV22] uses different methods.
The determinant illustrates why choosing very short matchings is specific to the permanent.
The Schur-complement calculation in §11 shows that a matching Y of k entries has tdY (det X)≤
k2+1. For k = Θ(log n), this gives only O(log2 n) independent coeﬀicients, rather than the Ω(n2)
supplied by Lem. 9.1 for the permanent. Relations among the relevant principal minors are
studied explicitly by Lin–Sturmfels [ LinS09]. The same section proves that even arbitrary entry-
disjoint blocks cannot make this coeﬀicient-summing method yield a supercubic determinant
formula bound.
Finally, allowing division requires care about the computational model. Strassen’s division-
elimination theorem often replaces a circuit with division by a division-free circuit computing
the same polynomial, but the cost depends on its degree [ Str73b]. This transformation does
not preserve the sharp formula-size or variable-occurrence estimates needed here. Kalorkoti
instead analyzes rational formulas directly [ Kal85], an approach followed by Lem. 10.2. Along
a formula path containing only one marked child at each gate, the marked value is transformed
by a fractional linear map u↦→(au + b)/ (cu + d). Such maps require only a bounded number of
147
===== PAGE 150 =====
parameters from the field of unmarked variables; at branching gates, the parameters contributed
by the two marked children are added. A field-intersection argument then shows that when the
final output is a polynomial, its coeﬀicients belong to the resulting parameter field. Formula
validity requires denominators to be nonzero as rational functions; it does not require those
denominators to remain nonzero at the later Jacobian specialization, which is applied only to
the polynomial coeﬀicients.
12.5. Lower bounds in restricted arithmetic models. Many stronger-looking lower bounds
impose structural restrictions on the computation rather than on the target polynomial. In a
monotone computation over a semiring, subtraction and cancellation are unavailable. Jerrum–
Snir obtain exponential lower bounds for monotone computations of the permanent [ JS82];
these arguments do not apply here because our circuits and formulas allow arbitrary complex
constants and cancellation.
At every multiplication gate of a syntactically multilinear computation, the two input sub-
computations use disjoint sets of variables. Consequently every intermediate polynomial is
multilinear, a stronger requirement than multilinearity of the final output alone. For this re-
stricted formula model, Raz proves nΩ(log n) lower bounds for both the determinant and perma-
nent [ Raz09]. Raz–Yehudayoff prove exponential lower bounds for constant-depth multilinear
circuits [ RY09]. Although the determinant and permanent are themselves multilinear, a gen-
eral circuit or formula computing one of them may pass through nonmultilinear intermediate
polynomials; the restricted bounds therefore do not transfer to the unrestricted models of this
paper.
Another important restriction is circuit depth. A depth-three ΣΠΣ circuit expresses a poly-
nomial as a sum of products of aﬀine linear forms. Over characteristic zero, Shpilka–Wigderson
use partial derivatives on low-codimension aﬀine subspaces to obtain nearly quadratic depth-
three determinant bounds in the number N = n2 of matrix variables [ SW01]. Over fixed finite
fields, Grigoriev–Karpinski obtain exponential depth-three lower bounds for the determinant;
Grigoriev–Razborov and the exposition in [ KS14, §7] give corresponding results and variants
for the permanent [ GK98, GR00]. Those arguments exploit finite-field evaluation and are not
characteristic-zero general-circuit arguments. In characteristic two, the determinant and per-
manent again coincide.
The distinction between homogeneous and nonhomogeneous circuits is also essential. In a ho-
mogeneous circuit, intermediate gates respect the degree grading; a nonhomogeneous circuit may
create terms of different degrees and cancel them later. For homogeneous depth-three circuits,
exponential lower bounds hold for both the determinant and permanent [ NW97]. Neverthe-
less, over Q the determinant has nonhomogeneous depth-three circuits of size exp(O(√n log n))
[GKKS16]. Thus a homogeneous lower bound does not automatically extend to a general circuit
of the same depth.
Several complexity measures yield additional restricted-model bounds. Nisan–Wigderson use
the dimension of a space of partial derivatives [ NW97]; Jacobian and algebraic-independence
methods apply to bounded-occurrence and related models [ ASSS16]; and shifted partial deriva-
tives yield bounds in homogeneous, low-depth, or bounded-bottom-fan-in settings [ GKKS14].
In particular, such methods give exp(Ω(√n)) lower bounds for homogeneous depth-four circuits
of bottom fan-in O(√n) computing either the n×n determinant or the n×n permanent.
The fact that many of these measures treat the two polynomials alike is itself supported by
barrier results. Efremenko–Landsberg–Schenck–Weyman show that shifted partial derivatives
cannot separate the padded permanent from the determinant in the relevant orbit-closure regime
[ELSW18b]; Gesmundo–Landsberg identify related limitations for unpadded derivative spaces
[GL19]. In a different geometric complexity theory setting, Bürgisser–Ikenmeyer–Panova prove
a barrier for representation-theoretic “occurrence obstructions” [ BIP19]. These results help
explain why a large derivative-based measure often proves a lower bound for both matrix poly-
nomials in a restricted model, rather than a permanent-versus-determinant separation. With
a different symmetry restriction, Dawar–Wilsenach do obtain an exponential permanent lower
bound while retaining polynomial-size determinant circuits [ DW25]. This is a genuine separa-
tion inside that restricted symmetric model, not a lower bound for unrestricted circuits.
148
===== PAGE 151 =====
Depth-reduction theorems explain why shallow circuits nevertheless attract sustained at-
tention. Agrawal–Vinay reduce general arithmetic circuits to depth four [ A V08], and Gupta–
Kamath–Kayal–Saptharishi obtain a “chasm at depth three” over characteristic zero [ GKKS16].
These simulations increase circuit size superpolynomially at the relevant degrees, so an arbi-
trary lower bound for the resulting shallow model does not immediately yield a comparable
unrestricted-circuit lower bound.
Recent constant-depth lower bounds extend beyond the early homogeneous and quadratic
depth-three results. Limaye–Srinivasan–Tavenas prove superpolynomial lower bounds for gen-
eral, possibly nonhomogeneous constant-depth circuits computing iterated matrix multiplication
over characteristic zero or suﬀiciently large characteristic [ LST25]; Forbes extends the conclu-
sion to every field [ For24]. Iterated matrix multiplication is a polynomial-size projection of
both the determinant and permanent: its source–sink path polynomial can be represented by a
cycle-cover matrix with self-loops, with the determinant differing only by a uniform sign. Since
substituting variables and constants preserves constant depth, a small constant-depth circuit
for either matrix polynomial would produce one for the projected iterated matrix multiplication
polynomial. Thus these results also give superpolynomial constant-depth lower bounds for both
matrix families.
More precisely, over characteristic zero, the depth-three consequence is at least nΩ(√ log n)
for each n×n matrix polynomial [ LST25]. Over every field, one obtains in particular the
depth-three bound
exp
(
Ω
(
(log n)3/ 2
√log log n
))
[For24]. Bhargav–Dutta–Saxena improve the constant-depth parameters and identify a bar-
rier for the associated measure [ BDS24]. None of these results conflicts with polynomial-size
unrestricted-depth determinant circuits, and none distinguishes the permanent from the deter-
minant in the constant-depth model under discussion.
References
[AH14] S. Aaronson and T. Hance, Generalizing and derandomizing Gurvits’s approximation algorithm for
the permanent , Quantum Inf. Comput. 14 (2014), nos. 7–8, 541–559, doi:10.26421/QIC14.7-8-1.
[ASSS16] M. Agrawal, C. Saha, R. Saptharishi, and N. Saxena, Jacobian hits circuits: Hitting sets, lower
bounds for depth- D occur-k formulas and depth- 3 transcendence degree-k circuits, SIAM J. Comput.
45 (2016), no. 4, 1533–1562, doi:10.1137/130910725.
[A V08] M. Agrawal and V. Vinay, Arithmetic circuits: A chasm at depth four , in 49th Annual IEEE Sym-
posium on Foundations of Computer Science , IEEE, 2008, 67–75, doi:10.1109/FOCS.2008.32.
[ABV17] J. Alper, T. Bogart, and M. Velasco, A lower bound for the determinantal complexity of a hypersur-
face, Found. Comput. Math. 17 (2017), no. 3, 829–836, doi:10.1007/s10208-015-9300-x.
[BS83] W. Baur and V. Strassen, The complexity of partial derivatives , Theoret. Comput. Sci. 22 (1983),
no. 3, 317–330, doi:10.1016/0304-3975(83)90110-X.
[BMS11] M. Beecken, J. Mittmann, and N. Saxena, Algebraic independence and blackbox identity testing , in
Automata, Languages and Programming, Part II , L. Aceto, M. Henzinger, and J. Sgall, eds., Lecture
Notes in Comput. Sci. 6756, Springer, 2011, 137–148, doi:10.1007/978-3-642-22012-8_10.
[Ber84] S. J. Berkowitz, On computing the determinant in small parallel time using a small number of
processors, Inform. Process. Lett. 18 (1984), no. 3, 147–150, doi:10.1016/0020-0190(84)90018-8.
[BDS24] C. S. Bhargav, S. Dutta, and N. Saxena, Improved lower bound, and proof barrier, for constant depth
algebraic circuits, ACM Trans. Comput. Theory 16 (2024), no. 4, Art. 23, 1–22, doi:10.1145/3689957.
[BI25] M. Bläser and C. Ikenmeyer, Introduction to geometric complexity theory , Theory Comput. Libr.,
Grad. Surv. 10 (2025), 1–166, doi:10.4086/toc.gs.2025.010.
[BCMV25] A. Boralevi, E. Carlini, M. Michałek, and E. Ventura, On the codimension of permanental varieties ,
Adv. Math. 461 (2025), Art. 110079, doi:10.1016/j.aim.2024.110079.
[Bür24] P. Bürgisser, Completeness classes in algebraic complexity theory , 2024, arXiv:2406.06217.
[BCS97] P. Bürgisser, M. Clausen, and M. A. Shokrollahi, Algebraic Complexity Theory , Grundlehren Math.
Wiss. 315, Springer, Berlin, 1997, doi:10.1007/978-3-662-03338-8.
[BIP19] P. Bürgisser, C. Ikenmeyer, and G. Panova, No occurrence obstructions in geometric complexity
theory, J. Amer. Math. Soc. 32 (2019), no. 1, 163–193, doi:10.1090/jams/908.
[BLMW11] P. Bürgisser, J. M. Landsberg, L. Manivel, and J. Weyman, An overview of mathematical issues
arising in the geometric complexity theory approach to VP ̸= VNP , SIAM J. Comput. 40 (2011),
no. 4, 1179–1209, doi:10.1137/090765328.
149
===== PAGE 152 =====
[BP15] P. Butera and M. Pernici, Sums of permanental minors using Grassmann algebra , Int. J. Graph
Theory Appl. 1 (2015), no. 2, 83–96, arXiv:1406.5337.
[Cai90] J.-Y. Cai, A note on the determinant and permanent problem , Inform. Comput. 84 (1990), no. 1,
119–127, doi:10.1016/0890-5401(90)90036-H.
[CCL10] J.-Y. Cai, X. Chen, and D. Li, Quadratic lower bound for permanent vs. determinant in any charac-
teristic, Comput. Complexity 19 (2010), no. 1, 37–56, doi:10.1007/s00037-009-0284-2.
[CKSV22] P. Chatterjee, M. Kumar, A. She, and B. L. Volk, Quadratic lower bounds for algebraic branching
programs and formulas, Comput. Complexity 31 (2022), no. 2, Art. 8, doi:10.1007/s00037-022-00223-
8.
[CKW11] X. Chen, N. Kayal, and A. Wigderson, Partial derivatives in arithmetic complexity and beyond ,
Found. Trends Theor. Comput. Sci. 6 (2011), nos. 1–2, 1–138, doi:10.1561/0400000043.
[DW25] A. Dawar and G. Wilsenach, Symmetric arithmetic circuits , Theory Comput. 21 (2025), no. 14,
1–32, doi:10.4086/toc.2025.v021a014.
[ELSW18a] K. Efremenko, J. M. Landsberg, H. Schenck, and J. Weyman, On minimal free resolutions
of sub-permanents and other ideals arising in complexity theory , J. Algebra 503 (2018), 8–20,
doi:10.1016/j.jalgebra.2018.01.021.
[ELSW18b] K. Efremenko, J. M. Landsberg, H. Schenck, and J. Weyman, The method of shifted partial deriva-
tives cannot separate the permanent from the determinant , Math. Comp. 87 (2018), 2037–2045,
doi:10.1090/mcom/3284.
[Eis95] D. Eisenbud, Commutative Algebra with a View Toward Algebraic Geometry , Grad. Texts in Math.
150, Springer, New York, 1995, doi:10.1007/978-1-4612-5350-1.
[FM11] P. Feinsilver and J. McSorley, Zeons, permanents, the Johnson scheme, and generalized derangements ,
Int. J. Combin. 2011 (2011), Art. 539030, doi:10.1155/2011/539030.
[For24] M. A. Forbes, Low-depth algebraic circuit lower bounds over any field , in 39th Computational
Complexity Conference , Leibniz Int. Proc. Inform. 300, Schloss Dagstuhl, 2024, 31:1–31:16,
doi:10.4230/LIPIcs.CCC.2024.31.
[FL06] S. Friedland and D. Levy, A polynomial-time approximation algorithm for the number of k-matchings
in bipartite graphs, in Mathematical Papers in Honour of Eduardo Marques de Sá , Textos Mat. Sér. B
39, Univ. Coimbra, Coimbra, 2006, 61–67, arXiv:cs/0607135.
[GGIL22] F. Gesmundo, P. Ghosal, C. Ikenmeyer, and V. Lysikov, Degree-restricted strength decompositions
and algebraic branching programs , in 42nd IARCS Annual Conference on Foundations of Software
Technology and Theoretical Computer Science , Leibniz Int. Proc. Inform. 250, Schloss Dagstuhl,
2022, 20:1–20:15, doi:10.4230/LIPIcs.FSTTCS.2022.20.
[GL19] F. Gesmundo and J. M. Landsberg, Explicit polynomial sequences with maximal spaces of par-
tial derivatives and a question of K. Mulmuley , Theory Comput. 15 (2019), no. 3, 1–24,
doi:10.4086/toc.2019.v015a003.
[Gly10] D. G. Glynn, The permanent of a square matrix , European J. Combin. 31 (2010), no. 7, 1887–1891,
doi:10.1016/j.ejc.2010.01.010.
[Gre12] B. Grenet, An upper bound for the permanent versus determinant problem , manuscript, 2012, author’s
manuscript.
[GK98] D. Grigoriev and M. Karpinski, An exponential lower bound for depth 3 arithmetic circuits , in
Proceedings of the Thirtieth Annual ACM Symposium on Theory of Computing , ACM, 1998, 577–
582, doi:10.1145/276698.276872.
[GR00] D. Grigoriev and A. A. Razborov, Exponential lower bounds for depth 3 arithmetic circuits in algebras
of functions over finite fields , Appl. Algebra Engrg. Comm. Comput. 10 (2000), no. 6, 465–487,
doi:10.1007/s002009900021.
[GKKS14] A. Gupta, P. Kamath, N. Kayal, and R. Saptharishi, Approaching the chasm at depth four , J. ACM
61 (2014), no. 6, Art. 33, 1–16, doi:10.1145/2629541.
[GKKS16] A. Gupta, P. Kamath, N. Kayal, and R. Saptharishi, Arithmetic circuits: A chasm at depth 3, SIAM
J. Comput. 45 (2016), no. 3, 1064–1079, doi:10.1137/140957123.
[Har77] R. Hartshorne, Algebraic Geometry , Grad. Texts in Math. 52, Springer, New York, 1977,
doi:10.1007/978-1-4757-3849-0.
[Hei83] J. Heintz, Definability and fast quantifier elimination in algebraically closed fields , Theoret. Comput.
Sci. 24 (1983), no. 3, 239–277, doi:10.1016/0304-3975(83)90002-6; corrigendum, 39 (1985), no. 2–3,
343, doi:10.1016/0304-3975(85)90150-1.
[HJ25] P. Hrubeš and P. S. Joglekar, On read- k projections of the determinant , in 42nd International
Symposium on Theoretical Aspects of Computer Science , Leibniz Int. Proc. Inform. 327, Schloss
Dagstuhl, 2025, 53:1–53:7, doi:10.4230/LIPIcs.STACS.2025.53.
[Hya79] L. Hyafil, On the parallel evaluation of multivariate polynomials , SIAM J. Comput. 8 (1979), no. 2,
120–123, doi:10.1137/0208010.
[JS82] M. Jerrum and M. Snir, Some exact complexity results for straight-line computations over semirings ,
J. ACM 29 (1982), no. 3, 874–897, doi:10.1145/322326.322341.
[Kal85] K. A. Kalorkoti, A lower bound for the formula size of rational functions , SIAM J. Comput. 14
(1985), no. 3, 678–687, doi:10.1137/0214050.
150
===== PAGE 153 =====
[KS14] N. Kayal and R. Saptharishi, A selection of lower bounds for arithmetic circuits , in Perspectives in
Computational Complexity , M. Agrawal and V. Arvind, eds., Progr. Comput. Sci. Appl. Logic 26,
Birkhäuser, Cham, 2014, 77–115, doi:10.1007/978-3-319-05446-9_5.
[LMR13] J. M. Landsberg, L. Manivel, and N. Ressayre, Hypersurfaces with degenerate duals and the geometric
complexity theory program, Comment. Math. Helv. 88 (2013), no. 2, 469–484, doi:10.4171/CMH/292.
[LS00] R. Laubenbacher and I. Swanson, Permanental ideals , J. Symbolic Comput. 30 (2000), no. 2, 195–
205, doi:10.1006/jsco.2000.0363.
[LST25] N. Limaye, S. Srinivasan, and S. Tavenas, Superpolynomial lower bounds against low-depth algebraic
circuits, J. ACM 72 (2025), no. 4, Art. 26, 1–35, doi:10.1145/3734215.
[LinS09] S. Lin and B. Sturmfels, Polynomial relations among principal minors of a 4 × 4-matrix, J. Algebra
322 (2009), no. 11, 4121–4131, doi:10.1016/j.jalgebra.2009.06.026.
[MP08] G. Malod and N. Portier, Characterizing Valiant’s algebraic complexity classes , J. Complexity 24
(2008), no. 1, 16–38, doi:10.1016/j.jco.2006.09.006.
[MR04] T. Mignon and N. Ressayre, A quadratic bound for the determinant and permanent problem , Int.
Math. Res. Not. 2004 (2004), no. 79, 4241–4253, doi:10.1155/S1073792804142566.
[Min79] H. Minc, Evaluation of permanents , Proc. Edinburgh Math. Soc. (2) 22 (1979), no. 1, 27–32,
doi:10.1017/S0013091500027760.
[MS01] K. D. Mulmuley and M. Sohoni, Geometric complexity theory I: An approach to the P vs. NP and
related problems, SIAM J. Comput. 31 (2001), no. 2, 496–526, doi:10.1137/S009753970038715X.
[Nec66] É. I. Nechiporuk, On a Boolean function , Dokl. Akad. Nauk SSSR 169 (1966), no. 4, 765–766;
English transl., Soviet Math. Dokl. 7 (1966), 999–1000, Math-Net.Ru:dan32449.
[NW97] N. Nisan and A. Wigderson, Lower bounds on arithmetic circuits via partial derivatives , Comput.
Complexity 6 (1996/97), no. 3, 217–234, doi:10.1007/BF01294256.
[RS26] C. Ramya and P. Shastri, Lower bounds for planar arithmetic circuits , ACM Trans. Comput. The-
ory 18 (2026), no. 1, Art. 9, 1–23, doi:10.1145/3778858; conference version, 15th Innovations in
Theoretical Computer Science Conference , Leibniz Int. Proc. Inform. 287, Schloss Dagstuhl, 2024,
91:1–91:22, doi:10.4230/LIPIcs.ITCS.2024.91.
[Raz09] R. Raz, Multi-linear formulas for permanent and determinant are of super-polynomial size , J. ACM
56 (2009), no. 2, Art. 8, 1–17, doi:10.1145/1502793.1502797.
[RY09] R. Raz and A. Yehudayoff, Lower bounds and separations for constant depth multilinear circuits ,
Comput. Complexity 18 (2009), no. 2, 171–207, doi:10.1007/s00037-009-0270-8.
[Rot64] G.-C. Rota, On the foundations of combinatorial theory I: Theory of Möbius functions , Z. Wahrschein-
lichkeitstheorie Verw. Gebiete 2 (1964), 340–368, doi:10.1007/BF00531932.
[Rys63] H. J. Ryser, Combinatorial Mathematics , Carus Math. Monogr. 14, Mathematical Association of
America, 1963.
[SW01] A. Shpilka and A. Wigderson, Depth-3 arithmetic circuits over fields of characteristic zero , Comput.
Complexity 10 (2001), no. 1, 1–27, doi:10.1007/PL00001609.
[SY10] A. Shpilka and A. Yehudayoff, Arithmetic circuits: A survey of recent results and open questions ,
Found. Trends Theor. Comput. Sci. 5 (2010), no. 3–4, 207–388, doi:10.1561/0400000039.
[Str73a] V. Strassen, Die Berechnungskomplexität von elementarsymmetrischen Funktionen und von Interpo-
lationskoeﬀizienten, Numer. Math. 20 (1973), 238–251, doi:10.1007/BF01436566.
[Str73b] V. Strassen, Vermeidung von Divisionen , J. Reine Angew. Math. 264 (1973), 184–202, Eu-
DML:151394.
[Val79a] L. G. Valiant, Completeness classes in algebra , in Proceedings of the Eleventh Annual ACM Sympo-
sium on Theory of Computing , ACM, 1979, 249–261, doi:10.1145/800135.804419.
[Val79b] L. G. Valiant, The complexity of computing the permanent , Theoret. Comput. Sci. 8 (1979), no. 2,
189–201, doi:10.1016/0304-3975(79)90044-6.
[VSBR83] L. G. Valiant, S. Skyum, S. Berkowitz, and C. Rackoff, Fast parallel computation of polynomials
using few processors , SIAM J. Comput. 12 (1983), no. 4, 641–644, doi:10.1137/0212043.
[vzG87] J. von zur Gathen, Permanent and determinant , Linear Algebra Appl. 96 (1987), 87–100,
doi:10.1016/0024-3795(87)90337-5.
151
===== PAGE 154 =====
Chapter 6
Exponential Parallel Repetition
for All Two-Player Entangled Games
Abstract. In a two-player entangled gameG, a referee sends a question to each
of two noncommunicating players, receives their answers, and decides whether
they win. The players may share an arbitrary entangled quantum state, and the
supremum of their winning probabilities is the entangled value ω∗(G). In the
repeated game G⊗n, the referee plays n independent copies and accepts only if
the players win every copy.
Raz’s celebrated classical parallel repetition theorem (STOC 1995) shows
that, for classical players, the repeated value decreases exponentially whenever
the original value is less than one. Whether the same holds for arbitrary en-
tangled games has been a longstanding open problem. We resolve this quan-
tum analogue aﬃrmatively: for every ﬁnite two-player, one-round game G with
ω∗(G) = 1 −ε< 1 and answer alphabets A,B ,
ω∗(G⊗n) ≤ exp
(
−cqs
ε13
ε + log(|A||B|)n
)
, n ≥ 1,
for a universal constant cqs> 0.
Previously, Yuen (ICALP 2016) proved polynomial decay for arbitrary entan-
gled games, and Bavarian, Vidick, and Yuen (STOC 2017) proved exponential
decay for anchored games obtained by modifying the original game. Our proof
builds on Yuen’s conditioning and dependency-breaking framework. Its main
new ingredient is a postselection-stable quantum sampleability estimate that
avoids an inverse dependence on the probability of the conditioning event.
Contents
1. Introduction
2. Preliminaries
3. Proof of the parallel repetition theorem
4. Proof of the postselected sampleability lemma
A. Deferred auxiliary proofs
References
152
===== PAGE 155 =====
1 Introduction
Parallel repetition is a basic method for reducing the error of multiprover interactive proofs.
Starting from a game that dishonest players cannot always win, the veriﬁer plays many inde-
pendent copies and accepts only if every copy is won. The fundamental question is whether
requiring simultaneous success makes the players’ winning probability exponentially small.
In more detail, a ﬁnite two-player, one-round game is speciﬁed by G = (X,Y,A,B,µ,V ).
A referee samples a pair of questions (x,y ) ∼ µ, sends x to Alice and y to Bob, and receives
answersa ∈A andb ∈B. The players win if V (x,y,a,b ) = 1 . They may agree on a strategy and
share randomness before the game, but they cannot communicate after receiving their questions.
The maximum winning probability of such a strategy is the classical value ω(G).
In the parallel repetition G⊗n, the referee independently samples n question pairs and ac-
cepts precisely when the players win all n coordinates. The coordinates are independent in
the referee’s experiment, but Alice’s answer to a coordinate can depend on all her questions,
and similarly for Bob. Consequently, the winning probability of an arbitrary repeated-game
strategy need not factor across coordinates. Nevertheless, Raz’s parallel repetition theorem
shows that every ﬁnite classical game with ω(G) < 1 satisﬁes ω(G⊗n) ≤ exp(−cGn) for some
cG > 0 depending on the game [ Raz98]. Holenstein later gave an information-theoretic proof
and improved the quantitative dependence on the soundness gap [ Hol09].
In the quantum setting, an entangled game has exactly the same questions, answers, and ac-
ceptance rule, but the players are additionally allowed to share a bipartite quantum state before
receiving their questions. Alice measures her part of this state according to x, Bob measures
his part according to y, and their classical outcomes determine their answers. Their optimal
winning probability, taken over arbitrary ﬁnite-dimensional shared states and local measure-
ments, is the entangled value ω∗(G). In G⊗n, each player may perform one joint measurement
depending on their entire question tuple. Playing the coordinates independently shows only
that
ω∗(G⊗n) ≥ ω∗(G)n;
the diﬃculty is to prove a matching exponential upper bound for unrestricted entangled strate-
gies.
The general quantum analogue of Raz’s theorem was explicitly noted as open by
2004 [ CHTW04, footnote 2]. In its basic qualitative form, the question is:
(Quantum Parallel Repetition Conjecture) For every ﬁnite two-player entangled
game G with ω∗(G)< 1, is there a constant cG> 0 such that
ω∗(G⊗n) ≤ exp(−cG ·n) for every n ≥ 1 ?
Exponential repetition was subsequently proved for several important classes of games, but
the question for arbitrary games remained open. The strongest general theorem, due to Yuen,
established polynomial rather than exponential decay [ Yue16].
1.1 Our result
We give an aﬃrmative answer to the quantum parallel repetition question for every ﬁnite two-
player, one-round entangled game.
Theorem 1.1 (Quantum parallel repetition theorem for two-player games) . There exists a
universal constant cqs> 0 such that the following holds. Let G = (X,Y,A,B,µ,V ) be any ﬁnite
two-player, one-round entangled game with nonempty answer alphabets, and put
ε = 1 −ω∗(G)> 0, ℓ = log(|A||B|).
153
===== PAGE 156 =====
Then, for every integer n ≥ 1,
ω∗(G⊗n) ≤ exp
(
−cqs
ε13
ε + log(|A||B|)n
)
(n ≥ 1).
The exponent 13 is not claimed to be optimal. It arises from the quantitative loss in a
standard quantum correlated-sampling lemma [ DSV15, Lemma 17]. The central point is that
the decay is exponential for every ﬁnite entangled game.
1.2 Previous work
Classical parallel repetition. Raz proved exponential parallel repetition for all ﬁnite clas-
sical two-player, one-round games [ Raz98]. Holenstein subsequently introduced an information-
theoretic approach based on correlated sampling and obtained the bound [ Hol09, Theorem 2.5]
ω(G⊗n) ≤ exp
(
−Ω
(
ε3n
1 + log(|A||B|)
))
, ε = 1 −ω(G).
The dependence on the soundness gap can be improved for certain structured games [ Rao11],
while Raz’s counterexample shows that the strongest possible linear-gap bound does not hold
for all games [ Raz11].
Entangled games with additional structure. Perfect parallel repetition holds for quan-
tum XOR games [ CSUU08], and exponential repetition has been established for entangled
unique games [ KRT10], projection games [ DSV15], and free games, where the players’ questions
are independently distributed [ JPY14, CS15]. Other bounds apply to games with strictly pos-
itive Cartesian question support but can depend on the minimum question probability [ CS14].
These results do not resolve the question for arbitrary predicates and correlated question distri-
butions.
General games. For unrestricted entangled games, Yuen proved [ Yue16, Theorem 1] that if
ω∗(G) = 1 −ε, then, for n ≥ 2,
ω∗(G⊗n) ≤ csG logn
ε17n1/4 ,
where c is universal and sG is the bit-length of the answer alphabet. This theorem already
applies to arbitrary question distributions and unchanged games; the remaining gap is that its
decay is polynomial rather than exponential.
Bavarian, Vidick, and Yuen obtained exponential ampliﬁcation by transforming the original
game into an anchored game [ BVY17]. Earlier work of Kempe and Vidick also obtained general-
game ampliﬁcation by introducing additional consistency or dummy questions [ KV11]. These
results are useful for hardness ampliﬁcation, but a repetition theorem for a modiﬁed game does
not imply one for the original game.
Our proof follows the general conditioning and sampleability framework of Yuen [ Yue16,
Section 3.2], which itself builds on Holenstein’s classical correlated sampling [ Hol09, Lemma 5.2
and Corollary 5.3] and the quantum correlated-sampling lemma of Dinur, Steurer, and
Vidick [ DSV15, Lemma 17]. The new ingredient is a quantum sampleability estimate that
remains eﬀective even when the conditioning event has exponentially small probability.
2 Preliminaries
We ﬁrst ﬁx probability and operator notation, then formally deﬁne ﬁnite one-round entangled
games and their standard parallel repetition. Standard ﬁnite-dimensional quantum background
appears in [ Wat18, Chapters 2 and 3] and [ NC10].
154
===== PAGE 157 =====
2.1 Notation and probability conventions
All logarithms are natural. For n ≥ 1, write [n] = {1,...,n }. If S ⊆ [n] andxn is a tuple, write
xS = (xj)j∈S, and similarly for yS,aS,bS. Empty products equal one.
Named probability distributions are written in calligraphic font. In particular, P denotes an
original experiment, Q its conditioned distribution, and JA, JB locally generated distributions.
The referee’s question distribution retains the conventional symbol µ; Roman Ea
x,F b
y denote
measurement operators, not probability distributions.
For probability distributions D, E on a ﬁnite set, relative entropy and total variation are
D(D∥E) =
∑
u
D(u) log D(u)
E(u),
dTV(D, E) = 1
2
∑
u
|D(u) − E (u)|.
The conventions 0 log 0 = 0 and D(D∥E) = + ∞ when supp D ̸⊆supp E are understood. With
natural logarithms, Pinsker’s inequality reads
dTV(D, E) ≤
√
1
2D(D∥E).
Probabilities and expectations under a speciﬁed distribution are written P and E. Conditioning
is used only when the conditioned event has strictly positive probability.
For a ﬁnite-dimensional Hilbert space H, |ψ⟩denotes a vector, F † the adjoint of an operator,
and F ⪰ 0 positive semideﬁniteness. A positive contraction satisﬁes 0 ⪯ F ⪯ I. A positive-
operator-valued measure (POVM) is a ﬁnite family of positive semideﬁnite operators summing
to the identity.
2.2 Finite one-round two-player entangled games
The referee samples one possibly correlated question pair and sends one question to each player.
Entanglement can correlate the answers, but the players cannot communicate after receiving
their questions.
Deﬁnition 2.1 (Finite one-round two-player entangled game) . A game is a tuple
G = (X,Y,A,B,µ,V ), V :X ×Y ×A ×B − → {0, 1},
where the question and answer sets are ﬁnite, both answer alphabets A,B are nonempty, and µ
is an arbitrary probability distribution on X ×Y . A ﬁnite-dimensional tensor-product strategy
consists of ﬁnite local Hilbert spaces HA, HB, a unit vector ψ ∈ HA ⊗ HB, and local POVMs
Ea
x ⪰ 0,
∑
a∈A
Ea
x =IHA, F b
y ⪰ 0,
∑
b∈B
Fb
y =IHB.
Its winning probability is
ω∗(G;ψ,E,F ) =
∑
x,y
µ(x,y )
∑
a,b
V (x,y,a,b ) ⟨ψ|Ea
x ⊗Fb
y |ψ⟩.
The entangled value is the supremum
ω∗(G) = sup
HA,HB ﬁnite
ψ,E,F
ω∗(G;ψ,E,F ).
No uniform bound on the local dimensions and no attaining strategy are assumed.
155
===== PAGE 158 =====
Deﬁne the question marginals
µX (x) =
∑
y
µ(x,y ), µ Y (y) =
∑
x
µ(x,y ).
A question with zero marginal probability can be deleted without changing either game value.
On the resulting positive-marginal question sets, write
µ(x |y) = µ(x,y )
µY (y), µ (y |x) = µ(x,y )
µX (x).
These expressions are evaluated only where their denominators are positive. The actual question-
pair support is
Eµ = {(x,y ) ∈X ×Y :µ(x,y )> 0};
it need not equal X ×Y and need not be connected.
The tensor product expresses locality, not independence of the players’ answers. In particu-
lar, writing ρAB = |ψ⟩ ⟨ψ|, the actual Born probabilities are
P(a,b |x,y ) = Tr
(
ρAB(Ea
x ⊗Fb
y )
)
.
The state is prepared before either question is received.
2.3 Standard parallel repetition
Deﬁnition 2.2 (Standard parallel repetition) . Forn ≥ 1, the repeated game G⊗n samples
(xn,yn) ∼ µ⊗n,
sends xn to Alice and yn to Bob, permits arbitrary ﬁnite-dimensional joint local POVMs
{Ean
xn :an ∈An}, {Fbn
yn :bn ∈Bn},
and accepts according to
V ⊗n(xn,yn,an,bn) =
n∏
i=1
V (xi,yi,ai,bi).
Write vn = ω∗(G⊗n). Thus a strategy wins the repeated game exactly when it wins every
original coordinate.
ForS ⊆ [n], write
µS(xS,yS) =
∏
j∈S
µ(xj,yj), µ S
X (xS) =
∏
j∈S
µX (xj), µ S
Y (yS) =
∏
j∈S
µY (yj).
These products express independence between distinct game coordinates, not independence
between the two questions of one coordinate.
Although the sampled question pairs are independent between coordinates, Alice’s ith an-
swer may depend on all of xn, and Bob’s ith answer may depend on all of yn. In particular,
ω∗(G⊗n) ≥ ω∗(G)n
is a lower bound obtained from independent strategies, not an upper bound on unrestricted
joint strategies. For a repeated strategy, write ρ(n)
AB =
⏐⏐⏐ψ(n)
⟩⣨
ψ(n)
⏐⏐⏐for its preshared density
operator.
The resulting precise game deﬁnitions are those used in Theorem 1.1, which was stated in
the introduction.
156
===== PAGE 159 =====
3 Proof of the parallel repetition theorem
We prove Theorem 1.1 by contradiction. Suppose that a strategy for G⊗n wins all n coordi-
nates simultaneously with probability exceeding the claimed exponential bound. Lemma 3.1
selects a small core D such that, conditional on winning every coordinate in D, a uniformly
chosen remaining coordinate wins with high probability. Lemma 3.2 represents this conditioned
coordinate by an ideal shared state and local measurements.
This ideal experiment is not yet a legal single-game strategy: the conditioned question
distribution may diﬀer from µ, its history is not supplied to the players, and its state depends
jointly on their separate questions. The central Lemma 3.3 produces locally generated histories
and locally describable states that approximate the ideal experiment. Lemmas 3.4 and 3.5
then use classical and quantum correlated sampling to synchronize those histories and prepare
the state, and Lemma 3.6 converts them into an actual strategy for G. Finally, Section 3.5
chooses the parameters so that this strategy wins with probability greater than ω∗(G), giving
the contradiction.
This section mainly follows the conditioning-and-rounding template of Yuen [ Yue16, Sec-
tion 3.2]. The new ingredient is Lemma 3.3, whose proof is deferred to Section 4.
3.1 The contradiction and the conditioning lemma
Fix an actual ﬁnite-dimensional strategy for G⊗n. Its shared state is |ψ⟩, its local measurements
are {Ean
xn }an∈An and {Fbn
yn }bn∈Bn. Write (Xn,Y n,An,Bn) for the random question-and-answer
word generated by this strategy; its distribution is
P(xn,yn,an,bn) = µ⊗n(xn,yn) ⟨ψ|Ean
xn ⊗Fbn
yn |ψ⟩.
WriteWi for the event that coordinate i is won and set
WD =
⋂
j∈D
Wj, ϑ = P(W[n]).
The letter ϑ always denotes the all-coordinate success probability; the letter r below denotes a
classical history.
Lemma 3.1 (Quantitative greedy conditioning) . Supposeϑ> 0, let 0<δ < 1, and assume
log(1/ϑ)
δ <n.
There exists D ⊊ [n] such that
|D| ≤ log(1/ϑ)
δ ,
P(WD) ≥ ϑ,
1
n − |D|
∑
i∈[n]\ D
P(Wi |WD) ≥ 1 −δ.
The proof appears in Appendix A.2. Recall the conditioning parameters from the proof
overview: p is the probability of winning every coordinate in D, q is the average conditional
winning probability on a remaining coordinate, and η is the information cost per remaining
coordinate. For the set D supplied by Lemma 3.1, these are
m =n − |D|, p = P(WD),
q = 1
m
∑
i∈[n]\ D
P(Wi |WD), η = log(1/p) + |D|log(|A||B|)
m . (1)
157
===== PAGE 160 =====
We will explicitly choose the parameters in Section 3.5, where the bounds on |D|and p from
Lemma 3.1 will give 0 ≤ η ≤ 1; see ( 17). We will also deﬁne a universal rounding constant
Bqs ≥ 1 in ( 11). With these choices, the operational goal is the following implication:
0 ≤ η ≤ 1 = ⇒ ω∗(G) ≥ q −Bqsη1/12.
Lemma 3.6 proves this implication by constructing a genuine single-game strategy. Its left-hand
side is computed in the conditioned repeated-game experiment; its right-hand side concerns an
actual single-game strategy receiving fresh questions from µ. Thus it suﬃces to make q close to
one and η small; the probability p itself need not approach one.
3.2 The ideal conditioned single-game strategy
Fix D ⊊ [n] with p = P(WD)> 0. To extract one instance of G, we keep one coordinate i /∈D
live: its questions Xi,Yi are withheld from the history and will serve as the referee’s single-game
questions. The history reveals both core questions XD,YD, so the core winning event WD can
be checked once the core answers are recorded. At every other coordinate it reveals at least one
of the two questions. This breaks the correlation between the remaining unrevealed Alice and
Bob question strings, while randomized reveal orders later make the live question a uniformly
chosen martingale increment. Section 4 constructs those orders and their distribution explicitly.
To help construct their single-game strategy, Alice and Bob use ﬁnite-valued public random-
ness λ ∈ Λ, independent of the game questions, to sample a uniformly random live coordinate
i ∈ [n] \D and revealed-coordinate sets CX,CY ⊆ [n] for their respective questions. These sets
satisfy
D ⊆ CX ∩CY, C X ∪CY = [n] \ {i}. (2)
The ﬁrst condition records both questions on D; the second withholds both live questions Xi,Yi
and reveals at least one question at every other coordinate. In particular, this second condition
is what makes the question factorization below possible.
The conditioned history . Let Z denote the random pair of answer words produced on D,
taking values in AD ×BD. Deﬁne the revealed-question history and full history by
T = (λ,XCX,YCY ), Z ∈AD ×BD, R = (T,Z ).
Because T contains λ, conditioning on T = t automatically ﬁxes both reveal sets CX,CY .
Continue to denote the augmented distribution on Λ ×Xn ×Yn ×An ×Bn by P, and write
Q = P( · |WD).
The history R is an analytical variable, not information supplied to either player. Since R con-
tainsλ, a realized history r determines its live coordinate i; we nevertheless display i explicitly
to identify the extracted coordinate. Deﬁne the posterior tuple distribution by
Q(i,r,x,y ) = P(R =r,Xi =x,Yi =y |WD).
Here (i,r,x,y ) denotes realized values, while R,Xi,Yi denote random variables; the four tuple
entries need not be independent.
Why the unrevealed questions factor. We now see why the coverage property in ( 2)
matters. Once (T,Xi,Yi) is ﬁxed, the still-random Alice questions occur only on [n] \(CX ∪ {i}),
while the still-random Bob questions occur only on [n] \(CY ∪ {i}). Their intersection is empty
precisely because CX ∪CY = [n]\{i}. Therefore no unrevealed pair (Xj,Yj) ∼ µ remains jointly
158
===== PAGE 161 =====
sampled. Independence of the original question pairs across coordinates then gives the prior
factorization
P(Xn =xn,Y n =yn |T =t,Xi =x,Yi =y)
= P(Xn =xn |T =t,Xi =x) P(Yn =yn |T =t,Yi =y). (3)
This factorization holds under the prior P, not under the conditioned distribution Q.
Local eﬀects and the ideal conditioned state. Fix a realized history r = (t,z ), where t
is a realized value of T and z = (aD,bD) ∈ AD × BD is a realized value of Z. The marginal
repeated-game POVM eﬀects for these recorded answers are
EaD
xn =
∑
˜an∈An
˜aD=aD
E˜an
xn,
FbD
yn =
∑
˜bn∈Bn
˜bD=bD
F
˜bn
yn.
Thus EaD
xn is the eﬀect of Alice producing the particular answer word aD on D, regardless of
her answers elsewhere; FbD
yn has the analogous meaning for Bob. A verage these eﬀects over each
player’s unrevealed questions to obtain the eﬀective local eﬀects
Hr,x = E[EaD
X n |T =t,Xi =x],
Kr,y = E
[
FbD
Y n |T =t,Yi =y
]
.
ThusHr,x andKr,y are the local eﬀective eﬀects for the ﬁxed answer words aD,bD. The question
factorization ( 3) gives the exact probability of observing those answer words:
pr(x,y ) := P(Z =z |T =t,Xi =x,Yi =y)
= ⟨ψ|Hr,x ⊗Kr,y |ψ⟩. (4)
A POVM eﬀect speciﬁes an outcome probability but does not uniquely determine the operator
representing its conditional state-update branch. To specify the branch, choose one common
cross operator, or puriﬁcation,
Γ(F ) : H − → H ⊗ A , 0 ⪯ F ⪯ I,
satisfying
Γ(F )†Γ(F ) = F. (5)
Equation ( 5) says that the cross operator preserves the exact Born probability of its eﬀect.
Deﬁnition 4.2 constructs a common ﬁnite-dimensional resolvent puriﬁcation, and Lemma 4.3
supplies its operator-entropy estimate.
The resulting conditioned branch and its normalized state are
ϕr,x,y = (Γ(Hr,x) ⊗ Γ(Kr,y)) |ψ⟩, Ψr,x,y = ϕr,x,y
∥ϕr,x,y∥.
By ( 5) and ( 4),
∥ϕr,x,y∥2 =pr(x,y ).
Therefore Ψr,x,y is well deﬁned on every branch of positive Q-probability. This state is only
ideal: its deﬁnition uses the full history r and both live questions (x,y ), whereas Alice and Bob
separately know only their own questions. Lemma 3.3 will replace it by nearby states described
using separate local information.
159
===== PAGE 162 =====
There are two separate questions about the ideal branch. First, if Alice and Bob were
handed Ψr,x,y, could they reproduce the original strategy’s answers at coordinate i? Second,
can they approximately obtain this state from their own questions? The next lemma answers
only the ﬁrst question. The substantially harder Lemma 3.3 answers the second.
Lemma 3.2 (The ideal state exactly simulates the remaining coordinate) . Fix (i,r,x,y ) such
that Q(i,r,x,y ) > 0. If Alice and Bob share the ideal state Ψr,x,y, there are local POVMs
{˜Ma
r,x}a∈A and {˜Nb
r,y}b∈B, determined by (r,x ) and (r,y ), respectively, such that
⟨Ψr,x,y|˜Ma
r,x ⊗ ˜Nb
r,y |Ψr,x,y⟩= Q(Ai =a,Bi =b |R =r,Xi =x,Yi =y).
The proof and the corresponding answer-reﬁnement operators appear in Appendix A.1.
Why the ideal state wins with probability q. By Lemma 3.2, measuring Ψr,x,y produces
exactly the original strategy’s answers at coordinate i, conditioned on the history and live
questions. Its winning probability on this branch is therefore
Q(Wi |R =r,Xi =x,Yi =y).
A verage over (i,R,X i,Yi) ∼ Q . Since i is uniform in [n] \D and independent of the original
experiment, the law of total expectation gives
E(i,r,x,y)∼Q [Q(Wi |R =r,Xi =x,Yi =y)] = 1
m
∑
j∈[n]\ D
P(Wj |WD) = q.
This is an ideal analytical success probability: it does not assume that the players can sample
Q, obtain the history, or prepare the question-dependent state.
Sampling histories from separate questions. The ideal experiment is not yet a legal
single-game strategy: under Q, its questions may be biased by conditioning, its history is not
given to either player, and Ψr,x,y depends jointly on both questions. Instead, consider the
following actual experiment.
The referee draws (x,y ) ∼ µ, and the players use shared randomness to choose a uniform
i ∈ [n] \D. Alice sees x but not y, so she samples a history from the conditional distribution of
R given her own question:
rA ∼ Q (R |i,Xi =x).
Similarly, Bob sees y but not x, and samples
rB ∼ Q (R |i,Yi =y).
These histories need not agree automatically. They will be coupled by classical correlated
sampling using the players’ shared randomness.
Let JA denote the distribution generated when Alice samples a history using her own ques-
tion, and let JB denote the analogous distribution generated by Bob. Their respective tuple
distributions are
JA(i,r,x,y ) = 1
mµ(x,y )Q(r |i,Xi =x),
JB(i,r,x,y ) = 1
mµ(x,y )Q(r |i,Yi =y).
(6)
Both retain the original question distribution µ.
160
===== PAGE 163 =====
Locally describable candidate states. Even when rA = rB = r, the target Ψr,x,y still
depends on both questions. To obtain states that Alice and Bob can describe separately, average
the corresponding eﬀects over the other player’s unknown question:
¯Hr,y =
∑
x′
µ(x′|y)Hr,x′, ¯Kr,x =
∑
y′
µ(y′|x)Kr,y′.
Here ¯Hr,y is Bob’s estimate of Alice’s eﬀect, using his question y, while ¯Kr,x is Alice’s estimate
of Bob’s eﬀect, using her question x. Collect the exact branch and its two locally describable
alternatives:
ϕr,x,y = (Γ(Hr,x) ⊗ Γ(Kr,y)) |ψ⟩,
ϕA
r,x = (Γ(Hr,x) ⊗ Γ( ¯Kr,x)) |ψ⟩,
ϕB
r,y = (Γ( ¯Hr,y) ⊗ Γ(Kr,y)) |ψ⟩.
(7)
Let
ΨA
r,x = ϕA
r,xϕAr,x

, ΨB
r,y = ϕB
r,yϕBr,y

.
Alice can specify the entire bipartite state ΨA
r,x from (r,x ), while Bob can specify ΨB
r,y from
(r,y ).
The attempt to mimic the ideal experiment therefore requires two guarantees: the locally
generated histories must agree and remain close in distribution to Q, and both locally described
states must approximate Ψr,x,y. The next lemma provides exactly these guarantees.
3.3 The central state-alignment and history-sampleability lemma
The following lemma contains the new technical estimates. Its ﬁrst conclusion says that the
ideal conditioned state admits two nearby descriptions, one available to each player. Its second
says that both players can approximately sample the same conditioned history despite receiving
fresh questions from µ. The complete proof is deferred to Section 4.
Recall that (i,r,x,y ) ∼ Q denotes a tuple drawn from the conditioned distribution; although
r already determines i, the coordinate is displayed explicitly.
Lemma 3.3 (Postselected state alignment and history sampleability) . For every ﬁnite repeated-
game strategy and every D ⊊ [n] with p = P(WD)> 0, use the parameters, history, states, and
locally generated distributions deﬁned above. Then
E(i,r,x,y)∼Q
Ψr,x,y − ΨA
r,x

2
≤ 8η,
E(i,r,x,y)∼Q
Ψr,x,y − ΨB
r,y

2
≤ 8η,
(8)
Moreover, with
κ =
√
3
2η,
one has dTV(Q, JA), dTV(Q, JB) ≤ κ. There exists ﬁnite shared randomness such that, on
(x,y ) ∼ µ, Alice and Bob sample a common uniform i ∈ [n] \D and histories rA,rB with
respective tuple distributions JA, JB, satisfying
P(rA ̸=rB) ≤ 4κ. (9)
The state inequalities are averages under the posterior distribution: for example, the ﬁrst
states that when the repeated experiment is conditioned on WD, the ideal state is typically
close to the state described by Alice. They are not pointwise claims about every history. The
total-variation bounds compare the ideal posterior with histories that Alice or Bob can actually
generate using their own question. Finite classical correlated sampling then gives ( 9).
161
===== PAGE 164 =====
3.4 Constructing the actual single-game strategy
On fresh referee questions (x,y ) ∼ µ, the desired strategy has three operational steps. First,
Alice and Bob use shared randomness to produce approximately matching histories rA,rB.
Second, they use their local descriptions ΨA
rA,x and ΨB
rB,y to approximately prepare the ideal
state Ψr,x,y. Finally, they apply the local coordinate measurements from Lemma 3.2. We ﬁrst
state the two standard sampling tools and then give the full strategy and its error analysis.
Classical sampling is the familiar Holenstein construction [ Hol09, Lemma 5.2 and Corol-
lary 5.3]; a direct proof using ﬁnite shared randomness appears in Appendix A.7. The quantum
input is the state-preparation theorem of Dinur, Steurer, and Vidick [ DSV15, Lemma 17], which
applies to arbitrary bipartite states.
Lemma 3.4 (Exact ﬁnite classical correlated sampling) . Let F be a ﬁnite family of probability
distributions on a ﬁnite set R. There exists one ﬁnite shared random variable and, for each
D ∈ F , an output RD having exactly distribution D, such that
P(RD ̸=RE ) ≤ 2 dTV(D, E) ( D, E ∈ F ). (10)
Apply the lemma to the ﬁnite family
{Q(R |i,Xi =x), Q(R |i,Yi =y)}i,x,y.
After sharing a uniform i, Alice uses her actual question x and Bob his actual question y.
A veraging (10) against µ(x,y ) gives
P(rA ̸=rB) ≤ 2 dTV(JA, JB)
≤ 2
(
dTV(JA, Q) + dTV(Q, JB)
)
≤ 4κ,
which proves the ﬁnite-shared-randomness guarantee in Lemma 3.3.
Lemma 3.5 (Quantum correlated sampling) . There exists a universal Kqs ≥ 1 with the follow-
ing property. Given d ≥ 1 and 0 < α≤ 1, there exist a ﬁnite d′≥ 1 and assignments of local
unitaries
σA ↦− →U (σA), σ B ↦− →V (σB)
on Cdd′
, indexed by unit vectors in Cd ⊗ Cd, such that, simultaneously for every pair σA,σB of
such unit vectors,
(
U (σA) ⊗V (σB)
)
|Edd′⟩ − |σA⟩ |Ed′⟩
≤ Kqs max
{
α1/12, ∥σA −σB∥1/6}
.
Here the ﬁnite embezzlement state is
|Eb⟩=


b∑
j=1
1
j


− 1/2 b∑
j=1
1√j |j⟩ |j⟩.
The initial state |Edd′⟩and catalyst dimension d′ depend on d,α , not on σA,σB.
This is precisely the quantum correlated-sampling lemma of Dinur, Steurer, and
Vidick [ DSV15, Lemma 17].
Rounding into a legal single-game strategy . Set the following universal constants:
U∗ =Kqs(1 + 21/6) + 2, B qs = (5 + 2U∗)
√
3
2 + 2Kqs321/12 + 2
√
8. (11)
162
===== PAGE 165 =====
Lemma 3.6 (Postselection-stable ﬁnite-dimensional rounding) . In the setting of Lemma 3.3,
suppose 0 ≤ η ≤ 1. For every 0 < α≤ 1, there is an actual ﬁnite-dimensional tensor-product
strategySα for the unchanged game G. On questions (x,y ) ∼ µ, the strategy ﬁrst uses classical
correlated sampling to generate approximately matching histories, then uses quantum correlated
sampling to prepare the state associated with that history, and ﬁnally applies the coordinate
measurements of Lemma 3.2. Its winning probability satisﬁes
win(Sα) ≥ q −Bqsη1/12 − 2Kqsα1/12. (12)
The questions of this strategy have distribution µ, and its shared state is prepared before either
question is received. In particular,
ω∗(G) ≥ q −Bqsη1/12. (13)
Proof. First, synchronize the history. Classical correlated sampling provides ﬁnite shared ran-
domnessh, including a uniform coordinate i, from which Alice computes rA =rA(h,x ) and Bob
computes rB =rB(h,y ). By Lemma 3.3,
dTV(Q, JA), dTV(Q, JB) ≤ κ, P(rA ̸=rB) ≤ 4κ, κ ≤
√
3
2η. (14)
Next, prepare the ideal state. Pad all candidate states to a common ﬁnite dimension d, and
apply quantum correlated sampling once, obtaining d′and local unitaries U,V . If ν(h) denotes
the distribution of the classical shared randomness, the question-independent shared state is
|Ω⟩=
( ∑
h
√
ν(h) |h⟩A |h⟩B
)
⊗ |Edd′⟩. (15)
For analysis, ﬁx a branch on which rA =rB =r. Alice knows (r,x ), Bob knows (r,y ), and they
applyU (ΨA
r,x) andV (ΨB
r,y), respectively. Quantum correlated sampling requires these candidate
states to be close. Since both approximate the same ideal state,
E(i,r,x,y)∼Q
ΨA
r,x − ΨB
r,y

2
≤ 2E(i,r,x,y)∼Q
ΨA
r,x − Ψr,x,y

2
+ 2E(i,r,x,y)∼Q
Ψr,x,y − ΨB
r,y

2
≤ 32η.
Quantum correlated sampling therefore approximately prepares ΨA
r,x, which is itself close to
Ψr,x,y. The resulting average state-preparation error is O(α1/12 +η1/12).
Finally, measure the extracted coordinate. Alice and Bob apply the measurements from
Lemma 3.2. On the ideal state their average winning probability is q; closeness of the prepared
state changes this probability by O(α1/12 + η1/12). Mismatching histories and the change
from Q to the actual question distribution cost O(κ) = O(√η). The precise calculation in
Appendix A.8 gives ( 12). Taking the supremum over the ﬁnite-dimensional strategies Sα and
letting α → 0+ yields ( 13).
3.5 The ﬁnal contradiction and exponential bound
We now prove Theorem 1.1, including its explicit distribution-uniform rate and the prefactor 1.
Set
cqs = 1
8(4Bqs)12 > 0. (16)
Proof of Theorem 1.1. First suppose the game satisﬁes ω∗(G) = 0 . From any ﬁnite-dimensional
strategy for G⊗n, the players can construct a single-game strategy by choosing a coordinate and
presampling all other question pairs from µ using ﬁnite shared randomness. They insert their
163
===== PAGE 166 =====
actual referee questions in the chosen coordinate, run the original repeated local measurements,
and return that coordinate’s answers. Every all-coordinate win is a win of the resulting single-
game strategy. Hence
ω∗(G⊗n) ≤ ω∗(G) = 0 ( n ≥ 1),
and the assertion holds.
Suppose, therefore, that 0<ε< 1, and write
ℓ = log(|A||B|), γ =cqs
ε13
ε +ℓ, δ = ε
4.
Fix an arbitrary n ≥ 1. If the desired conclusion fails at this n, then
ω∗(G⊗n)>e −γn.
The deﬁnition of the supremum therefore gives an actual ﬁnite-dimensional repeated strategy
with
ϑ = P(W[n])>e −γn.
There is no assumption that the repeated value is attained. Since Bqs ≥ 1,
γ = ε
8(ε +ℓ)
(
ε
4Bqs
) 12
≤ ε
8 = δ
2.
Thus the hypothesis of Lemma 3.1 is satisﬁed, and it supplies D ⊊ [n] with
|D|< γn
δ ≤ n
2, m> n
2, p ≥ ϑ, q ≥ 1 − ε
4.
In particular,
log(1/p)<γn, |D|ℓ< 4γnℓ
ε .
Using m>n/ 2 and ( 16), we get
η = log(1/p) + |D|ℓ
m
< 2γ
(
1 + 4ℓ
ε
)
= ε12
4(4Bqs)12
ε + 4ℓ
ε +ℓ
≤
(
ε
4Bqs
) 12
≤ 1. (17)
Choose the strictly positive ﬁnite-catalyst accuracy
α =
(
ε
16Kqs
) 12
∈ (0, 1].
Lemma 3.6 now produces an actual single-game ﬁnite-dimensional strategy with
win(Sα) ≥ q −Bqsη1/12 − 2Kqsα1/12
> 1 − ε
4 − ε
4 − ε
8 = 1 − 5ε
8 > 1 −ε =ω∗(G),
164
===== PAGE 167 =====
contradicting the deﬁnition of ω∗(G). Therefore ω∗(G⊗n) ≤ e−γn for this arbitrary n. As n ≥ 1
was arbitrary,
ω∗(G⊗n) ≤ exp
(
− 1
8(4Bqs)12
ε13
ε + log(|A||B|)n
)
(n ≥ 1).
Every question conditional above was used only on positive µ-support. Neither a minimum
positive question probability nor a connected-support or component-dependent reduction enters
the proof. Both the classical ﬂag and the catalyst in ( 15) are ﬁnite for each ﬁxed strategy and
eachα> 0. The rate is consequently independent of the question distribution, its support, the
question-alphabet sizes, and the entanglement dimension.
4 Proof of the postselected sampleability lemma
This section proves Lemma 3.3.
Reminder of Lemma 3.3 (Postselected state alignment and history sampleability) . For every
ﬁnite repeated-game strategy and every D ⊊ [n] withp = P(WD)> 0, let the histories, branches,
and distributions be deﬁned by (1)–(7) and (6). Then
E(i,r,x,y)∼Q
Ψr,x,y − ΨA
r,x

2
≤ 8η,
E(i,r,x,y)∼Q
Ψr,x,y − ΨB
r,y

2
≤ 8η,
Furthermore, with
κ =
√
3
2η,
one has
dTV(Q, JA) ≤ κ, dTV(Q, JB) ≤ κ.
There exists a ﬁnite shared random variable such that, on (x,y ) ∼ µ, the players sample a
common uniform i ∈ [n]\D and locally generated histories rA,rB with respective tuple marginals
JA, JB and
P(rA ̸=rB) ≤ 4κ.
Recall notations. Fix the repeated-game strategy and D ⊊ [n] with p = P(WD) > 0.
Throughout this section write
M = [n] \D, m = |M |, τ = log(1/p), s = |D|log(|A||B|), η = τ +s
m .
HereWD is the event that every core coordinate in D is won, and Q = P( · |WD) is its posterior.
Proof roadmap. We begin by understanding what the state diﬀerence in ( 8) actually mea-
sures. Public randomness λ picks a live coordinate i and speciﬁes which questions have already
been revealed. The resulting history is
r = (t,z ), t = (λ,XCX,YCY ), z = (aD,bD).
Thusr records the core questions XD,YD and answers aD,bD, but neither live question Xi,Yi.
Suppose now that Xi = x and Yi = y. The eﬀects Hr,x and Kr,y describe Alice’s and Bob’s
165
===== PAGE 168 =====
recorded core answers aD,bD, respectively. Alice knows x, but not y, so from her point of view
Bob’s eﬀect Kr,y must instead be averaged:
¯Kr,x = EYi∼µ(·|x)Kr,Yi.
Write |ψ⟩ for the original shared state and Γ for a common puriﬁcation. The ideal branch
conditioned on both live questions (x,y ) and the branch determined by Alice’s information
(r,x ) are, respectively,
ϕr,x,y =
(
Γ(Hr,x) ⊗ Γ(Kr,y)
)
|ψ⟩, ϕ A
r,x =
(
Γ(Hr,x) ⊗ Γ( ¯Kr,x)
)
|ψ⟩.
The only diﬀerence is that the ﬁrst branch sees Bob’s actual question Yi =y, while the second
does not. The quantity ϕr,x,y −ϕA
r,x is therefore precisely the change caused by revealing Yi. Its
normalized counterpart is the ﬁrst state diﬀerence in ( 8).
A single reveal can have a large eﬀect, so there is no reason for revealing Yi in isolation
to have a small cost. Instead, imagine keeping Alice’s relevant questions ﬁxed and gradually
uncovering Bob’s remaining questions, one at a time, in a random order πX . Somewhere along
the way we encounter the live coordinate i. Because the order is random, the number kX of
questions revealed before i is uniform. Let U be everything ﬁxed before this process begins.
After the ﬁrst j questions have been uncovered, our current prediction for Bob’s core-answer
eﬀect FbD
Y n is
Gj = E
[
FbD
Y n
⏐⏐⏐⏐U,Yπ≤ j
X
]
.
As more questions are exposed, these predictions form a Doob martingale under the prior P.
Immediately before the live step kX , the question Yi is still unknown; immediately afterwards,
it has been revealed. We therefore have
GkX = ¯Kr,Xi, G kX +1 =Kr,Yi, ϕ r,Xi,Yi −ϕA
r,Xi = Γ(Hr,Xi) ⊗
(
Γ(GkX +1) − Γ(GkX )
)
|ψ⟩.
This is the central reduction: the state diﬀerence we care about is exactly one randomly chosen
increment of a much longer reveal process. A particular increment might be large, but a
uniformly random one can be controlled by the total information budget.
The martingale above tracks eﬀects. To control the resulting change in quantum states, we
must also choose the puriﬁcation Γ. One obvious choice would be Γ(F ) = F 1/2, which already
preserves Born probabilities, that is, Γ(F )†Γ(F ) = F . Instead, we use the resolvent puriﬁcation
from Deﬁnition 4.2, which preserves the same Born probabilities. Its additional beneﬁt is the
entropy-control property in Lemma 4.3: with H1(v) = −v logv and H1(0) = 0 ,
EF
[ (
Γ(F ) − Γ( ¯F )
) †(
Γ(F ) − Γ( ¯F )
) ]
⪯ H1( ¯F ) − EFH1(F ), ¯F = EFF.
The meaning is that the expected squared diﬀerence between a random eﬀect F and its average
¯F , after applying Γ, is bounded by the decrease in operator entropy when ¯F is reﬁned to F .
Apply this at every step of the reveal martingale (Gj)N
j=0. The successive entropy decreases
telescope, so their total, weighted by Alice’s ﬁxed eﬀect H and the shared state, is at most the
entropy of the initial branch probability:
N − 1∑
j=0
E
Γ(H) ⊗
(
Γ(Gj+1) − Γ(Gj)
)
|ψ⟩
2 ≤ H1(p0), p 0 = ⟨ψ|H ⊗G0 |ψ⟩.
Lemma 4.4 therefore bounds a uniformly random step k by its 1/N share of the total:
E
Γ(H) ⊗
(
Γ(Gk+1) − Γ(Gk)
)
|ψ⟩
2 ≤ H1(p0)
N .
166
===== PAGE 169 =====
For a ﬁxed core-answer word z, the initial branch probability is p0 = pz(U ) = P(Z = z |U ).
Lemma 4.5 shows that the total entropy of the accepted words is at most p(τ +s) on average.
Intuitively, acceptance has total probability p, and recording its core-answer word contributes
at most s additional units of entropy.
Lemma 4.6 applies the random-step estimate to the two live-question reveals. Write P 0 for
the prior distribution of public randomness and questions. The Alice- and Bob-reveal costs are
IA = E(i,t,x,y)∼P 0
∑
z:WD(t,z)
ϕr,x,y −ϕB
r,y

2
,
IB = E(i,t,x,y)∼P 0
∑
z:WD(t,z)
ϕr,x,y −ϕA
r,x

2
.
Herer = (t,z ), and the sums range over accepted core-answer words. The vectors ϕr,x,y,ϕA
r,x,ϕB
r,y
are unnormalized branches, so IA andIB measure their unnormalized squared diﬀerences. The
reverse description selects a block of N candidate live coordinates with size bias 2N/m, while
its uniform reveal step contributes 1/N. These factors cancel, so Lemma 4.6 bounds both costs
by
IA, IB ≤ 2
mp(τ +s).
Lemma 4.7 then converts these unnormalized branch diﬀerences into the normalized-state dif-
ferences that we actually want to bound:
E(i,r,x,y)∼Q
Ψr,x,y − ΨA
r,x

2
≤ 4
pIB ≤ 8η,
E(i,r,x,y)∼Q
Ψr,x,y − ΨB
r,y

2
≤ 4
pIA ≤ 8η.
This proves both desired state bounds in ( 8) without any inverse-postselection loss. What re-
mains, the history-matching guarantee ( 9), is purely classical: Lemma 4.8 supplies the standard
conditioning budget, and Lemma 4.9 combines it with the relative-entropy chain rule, Pinsker’s
inequality, and classical correlated sampling.
4.1 Setting up the revealed history and its martingale
The forward history . Choose i uniformly in M and partition M \ {i} fairly into LX ⊔
LY . Choose independent uniform random permutations πX,−i of LX and πY,−i of LY . The
subscript −i indicates that these permutations exclude the live coordinate i. Independently
choose uniform cuts
kX ∈ {0,..., |LX |}, k Y ∈ {0,..., |LY |}.
This is a symmetric random-reveal variant of the dependency-breaking construction in Holen-
stein’s classical embedding argument [ Hol09, Section 3]. The random permutations and cuts
kX,kY allow the live question to be identiﬁed later with a uniformly random increment of a
reveal martingale.
The public randomness and revealed-coordinate sets are
λ = (i,LX,LY,πX,−i,πY,−i,kX,kY ),
CX =D ∪LX ∪π≤kY
Y,−i,
CY =D ∪LY ∪π≤kX
X,−i.
Thus Alice’s questions XLX and Xπ≤ kY
Y,− i
are revealed, as are Bob’s questions YLY and Yπ≤ kX
X,− i
.
This is precisely the public randomness λ introduced in Section 3.2; in particular,
T = (λ,XCX,YCY ), C X ∪CY = [n] \ {i}.
167
===== PAGE 170 =====
Write P 0 for the marginal retaining the independent public randomness and questions but
discarding all answers: P 0(λ,xn,yn) = P(λ)∏n
j=1µ(xj,yj). Its induced marginal on (i,T,X i,Yi)
is denoted by P 0(i,t,x,y ). Both core-question tuples XD,YD are revealed, neither live question
Xi,Yi is revealed, and every other coordinate reveals at least one question. Therefore the
unrevealed Alice and Bob index sets are disjoint, and the product prior P gives exactly ( 3).
This is independence under P, not under the posterior Q.
The branches to be compared. Forz = (aD,bD) and r = (t,z ), recall
Hr,x = E[EaD
X n |T =t,Xi =x],
Kr,y = E
[
FbD
Y n |T =t,Yi =y
]
.
Prior conditional independence identiﬁes the joint branch probability pr(x,y ) with the notation
already introduced in Section 3:
pr(x,y ) = ⟨ψ|Hr,x ⊗Kr,y |ψ⟩= ∥ϕr,x,y∥2.
A veraging over the other player’s unknown live question gives
¯Hr,y =
∑
x′
µ(x′|y)Hr,x′, ¯Kr,x =
∑
y′
µ(y′|x)Kr,y′.
Consequently,
ϕr,x,y =
(
Γ(Hr,x) ⊗ Γ(Kr,y)
)
|ψ⟩,
ϕA
r,x =
(
Γ(Hr,x) ⊗ Γ( ¯Kr,x)
)
|ψ⟩,
ϕB
r,y =
(
Γ( ¯Hr,y) ⊗ Γ(Kr,y)
)
|ψ⟩.
If Q(i,t,z,x,y )> 0, then µ(x,y )> 0 and pr(x,y )> 0. Moreover,
¯Hr,y ⪰ µ(x |y)Hr,x, ¯Kr,x ⪰ µ(y |x)Kr,y,
so ϕA
r,x

2
≥ µ(y |x)pr(x,y )> 0,
ϕB
r,y

2
≥ µ(x |y)pr(x,y )> 0.
Thus all normalized states used on positive-posterior branches (i,t,z,x,y ) exist. Since t records
the core questions XD,YD, the pair (t,z ) determines whether WD occurs, that is, whether every
core coordinate in D is won. Summing the accepted branch probabilities therefore gives
∑
i,t,x,y,z
P 0(i,t,x,y ) 1WD (t,z )pr(x,y ) = p.
This exact branch massp is the factor that will cancel when the unnormalized costs are converted
into normalized-state distances.
The random live-coordinate martingale. Only three features of the reveal construction
enter the proof: the live question is a uniform martingale step, its block is sampled with the
appropriate size bias, and the neighboring eﬀects are exactly the local eﬀects we wish to compare.
Lemma 4.1 (Random live-coordinate martingales) . The forward history admits the following
equivalent reverse descriptions.
For the Alice-reveal direction, sample a partition M =LX ⊔L+
Y with
P(LX,L +
Y ) = 2 −m 2|L+
Y |
m .
168
===== PAGE 171 =====
A uniform order πY of L+
Y and an independent uniform cut kY ∈ {0,..., |L+
Y | −1} determine
i =πY [kY + 1]. With
U = (XD,YD,XLX,YL+
Y
,Yπ≤ kX
X,− i
), (21)
the eﬀects
Fj = E
[
EaD
X n |U,Xπ≤ j
Y
]
, 0 ≤ j ≤ |L+
Y |,
K = E
[
FbD
Y n |U
]
(22)
form a prior martingale with ﬁxed Bob eﬀect K, and
FkY = ¯Hr,Yi, F kY +1 =Hr,Xi, K =Kr,Yi. (23)
For the Bob-reveal direction, sample M = L+
X ⊔LY with probability 2−m2|L+
X |/m, take a
uniform order πX of L+
X , and let i =πX [kX + 1] for a uniform cut kX . With
U = (XD,YD,XL+
X
,YLY,Xπ≤ kY
Y,− i
),
the eﬀects
Gj = E
[
FbD
Y n |U,Yπ≤ j
X
]
, 0 ≤ j ≤ |L+
X |,
form a prior martingale with ﬁxed Alice eﬀect Hr,Xi, and
GkX = ¯Kr,Xi, G kX +1 =Kr,Yi.
The live increments are therefore exactly the Alice- and Bob-reveal branch diﬀerences. Ap-
pendix A.3 veriﬁes the reverse distribution and these martingale properties.
4.2 Resolvent puriﬁcation and one-step entropy control
We now make precise the puriﬁcation Γ used in the roadmap. The ordinary square-root choice
Γ(F ) = F 1/2 preserves Born probabilities; the resolvent puriﬁcation below does the same while
also yielding a useful one-step entropy estimate.
Deﬁnition 4.2 (Resolvent puriﬁcation) . Let S be the collection of all possible values of
Hr,x,Kr,y, ¯Hr,y, ¯Kr,x and the martingale eﬀects Fj,Gj in Lemma 4.1. The question, answer,
and public-randomness alphabets are ﬁnite, so S is ﬁnite. Let Σ be the union of the positive
eigenvalues of the operators in S. Set
gσ(u) = σ
σ +u, A0 = span{gσ :σ ∈ Σ} ⊆L2((0, ∞ ),du ), A = A0 ⊕ C |0⟩.
The auxiliary space A is ﬁnite dimensional, with dim A ≤ |Σ|+ 1. For each eﬀect F , deﬁne
[Γ(F )v](u) = F (F +uI)− 1v, Γ(F ) : H − → H ⊗ A .
V eriﬁcation of the Born-probability property . For every positive eigenvalue σ,
∫∞
0
( σ
σ +u
) 2
du =σ,
so spectral calculus gives
Γ(F )†Γ(F ) = F, (24)
including for singular F .
169
===== PAGE 172 =====
The entropy-control property . Revealing one question replaces an averaged eﬀect ¯F by a
more informative eﬀect F . The key beneﬁt of the resolvent puriﬁcation is that the resulting
squared movement is bounded by the corresponding decrease in operator entropy.
Lemma 4.3 (One-step puriﬁed variation is controlled by entropy) . LetF be a ﬁnitely supported
random positive contraction taking values in S, and suppose that ¯F = EFF also belongs to S.
Recall
H1(v) = −v logv (0<v ≤ 1), H 1(0) = 0,
and deﬁne H1(F ) by functional calculus. Then
EF
[ (
Γ(F ) − Γ( ¯F )
) †(
Γ(F ) − Γ( ¯F )
) ]
⪯ H1( ¯F ) − EFH1(F ). (25)
For positive deﬁnite eﬀects, the entropy gap is the expected operator Bregman divergence in-
troduced by Petz [ Pet07]; closely related resolvent-based estimates were studied by Kim [ Kim14].
A direct proof, also covering singular eﬀects, appears in Appendix A.4.
4.3 A puriﬁed martingale has a small random increment
The one-step estimate becomes useful because its entropy terms telescope over an entire reveal
martingale. This is the quantum counterpart of the classical relative-entropy chain rule.
Lemma 4.4 (Puriﬁed martingale increments) . Let F0,...,F N be a ﬁnite positive-contraction
martingale, where N ≥ 1, F0 is deterministic, and
E[Fj+1 |F0,...,F j] = Fj.
Fix a positive contraction K on Bob’s space and a shared unit vector |ψ⟩. Let k be uniform in
{0,...,N − 1}, independently of the martingale, and write
p0 = ⟨ψ|F0 ⊗K |ψ⟩.
Recall
H1(v) = −v logv (0<v ≤ 1), H 1(0) = 0.
Then
Ek,F
(
Γ(Fk+1) − Γ(Fk)
)
⊗ Γ(K) |ψ⟩
2 ≤ H1(p0)
N . (26)
The same conclusion holds conditionally when previously revealed information ﬁxes F0 and K.
Proof. Absorb Bob’s ﬁxed eﬀect into the positive operator
ρK = TrB
[
(I ⊗K1/2) |ψ⟩ ⟨ψ|(I ⊗K1/2)
]
.
For every operator C on Alice’s space,
Tr(ρKC) = ⟨ψ|C ⊗K |ψ⟩, TrρK = ⟨ψ|I ⊗K |ψ⟩ ≤ 1. (27)
In particular, p0 = Tr(ρKF0).
Write
∆j = Γ(Fj+1) − Γ(Fj), Fj =σ(F0,...,F j).
Conditional on Fj, apply Lemma 4.3 with F = Fj+1 and ¯F = Fj. The martingale identity
E[Fj+1 | Fj] = Fj gives
E[∆†
j∆j | Fj] ⪯ H1(Fj) − E[H1(Fj+1) | Fj].
170
===== PAGE 173 =====
Moreover, (24) and ( 27) give
∥∆j ⊗ Γ(K) |ψ⟩∥2 = Tr(ρK∆†
j∆j).
Taking expectations, tracing against ρK, and summing over j makes the intermediate entropies
cancel:
N − 1∑
j=0
E ∥∆j ⊗ Γ(K) |ψ⟩∥2 ≤ Tr
[
ρK
(
H1(F0) − EH1(FN )
)]
≤ Tr(ρKH1(F0)). (28)
For the last inequality use H1(FN ) ⪰ 0.
Diagonalize F0 = ∑
aσa |va⟩ ⟨va|and put wa = ⟨va|ρK |va⟩. Since ∑
awa = Tr ρK ≤ 1,
append an eigenvalue 0 with weight 1 − TrρK. Concavity of H1 then gives
Tr(ρKH1(F0)) =
∑
a
waH1(σa) ≤ H1
( ∑
a
waσa
)
=H1(p0).
Finally, the uniform cut k selects one of the N increments independently, so its expected squared
movement is the sum in ( 28) divided by N . This proves ( 26).
4.4 From reveal costs to normalized state alignment
Our goal is the pair of normalized-state estimates in ( 8). On every positive-posterior branch,
the exact posterior weight is
Q(i,t,z,x,y ) = P 0(i,t,x,y ) 1WD (t,z ) ∥ϕr,x,y∥2
p . (29)
For nonzero vectors u,v , 
u
∥u∥ − v
∥v∥

2
≤ 4 ∥u −v∥2
∥u∥2 .
Takingu = ϕr,x,y and v = ϕB
r,y, the factor ∥u∥2 in ( 29) cancels the denominator above. Thus
the desired normalized estimate reduces to the following unnormalized Alice-reveal cost:
IA = E(i,t,x,y)∼P 0
∑
z:
1WD (t,z)=1

(
Γ(Hr,x) − Γ( ¯Hr,y)
)
⊗ Γ(Kr,y) |ψ⟩

2
= E(i,t,x,y)∼P 0
∑
z:
1WD (t,z)=1
ϕr,x,y −ϕB
r,y

2
.
It is an Alice-reveal cost because the operator that changes is Alice’s eﬀect Hr,x; it compares
the ideal branch ϕr,x,y with Bob’s surrogate ϕB
r,y. It is unnormalized because neither branch
vector is divided by its norm and the expectation is under the prior P 0. Deﬁne the symmetric
Bob-reveal cost by
IB = E(i,t,x,y)∼P 0
∑
z:
1WD (t,z)=1
ϕr,x,y −ϕA
r,x

2
.
The two target estimates are therefore bounded by
E(i,r,x,y)∼Q
Ψr,x,y − ΨB
r,y

2
≤ 4
pIA,
E(i,r,x,y)∼Q
Ψr,x,y − ΨA
r,x

2
≤ 4
pIB.
(30)
It remains to show that each unnormalized cost is at most 2p(τ +s)/m.
171
===== PAGE 174 =====
Lemma 4.5 (Accepted-word entropy budget) . For any background information U containing
XD,YD, let
pW (U ) = P(WD |U ), p z(U ) = P(Z =z |U ).
The accepted answer words z satisfy
∑
z:
1WD (U,z)=1
H1(pz(U )) ≤ H1(pW (U )) +pW (U )s, (31)
and consequently
EU ∼P 0
∑
z:
1WD (U,z)=1
H1(pz(U )) ≤ p(τ +s). (32)
The proof is deferred to Appendix A.5.
Lemma 4.6 (Probability-weighted quantum alignment) . The two reveal costs satisfy
IA, IB ≤ 2p(τ +s)
m .
Proof. Use the Alice-reveal martingale already constructed in ( 22). Conditional on its back-
ground U , the accepted answer word z has prior probability
pz(U ) = P(Z =z |U ) = ⟨ψ|F0 ⊗K |ψ⟩.
Its live cut kY is uniform in {0,..., |L+
Y | −1}, so Lemma 4.4, applied with N = |L+
Y |andk =kY ,
gives
E
[ (
Γ(FkY +1) − Γ(FkY )
)
⊗ Γ(K) |ψ⟩
2⏐⏐⏐U
]
≤ H1(pz(U ))
|L+
Y | .
By (23), the vector on the left is exactly ϕr,Xi,Yi −ϕB
r,Yi. Fix a partition M =LX ⊔L+
Y , and write
EU for averaging over its remaining public randomness and background questions. Because U
containsXD,YD, accepted words are already determined before the random cut. Summing the
preceding bound over those words gives
EU
∑
z:WD(U,z)
H1(pz(U ))
|L+
Y | ≤ p(τ +s)
|L+
Y | ,
where ( 32) applies for each ﬁxed partition because the public randomness is independent of the
game. Finally, average over the size-biased partitions:
IA ≤
∑
LX ⊔L+
Y =M
|L+
Y |>0
2−m 2|L+
Y |
m 
probability of the partition
p(τ +s)
|L+
Y |
= 2p(τ +s)
m
∑
LX ⊔L+
Y =M
|L+
Y |>0
2−m ≤ 2p(τ +s)
m .
The last sum is at most one because 2−m is the probability of a fair partition and only the
nonemptyL+
Y blocks occur.
For IB, use the symmetric Bob-reveal martingale (Gj)j constructed above. Alice’s eﬀect
Hr,Xi remains ﬁxed while Bob’s questions Yπ≤ j
X
are revealed, and its partition has size bias
2|L+
X |/m. The same martingale estimate and size-bias cancellation give IB ≤ 2p(τ +s)/m.
172
===== PAGE 175 =====
Passing to normalized states. We now convert the unnormalized reveal-cost bounds into
the normalized-state alignment required by Lemma 3.3.
Lemma 4.7 (Postselection-stable normalized alignment) . The ideal conditioned state and its
locally describable alternatives satisfy
E(i,r,x,y)∼Q
Ψr,x,y − ΨA
r,x

2
≤ 8η, E(i,r,x,y)∼Q
Ψr,x,y − ΨB
r,y

2
≤ 8η.
Proof. On tuples of zero posterior probability, any undeﬁned normalized state may be completed
by a ﬁxed arbitrary unit vector; such defaults do not contribute to a posterior expectation.
Combining the reduction ( 30) with Lemma 4.6 gives both bounds:
4
pIA, 4
pIB ≤ 8(τ +s)
m = 8η.
Thus the p retained in the unnormalized entropy budget cancels the 1/p in the posterior, with
no inverse-postselection loss.
4.5 Classical history generation and correlated sampling
The remaining task is classical: Alice and Bob must generate nearly matching histories rA,rB
using their respective live questions Xi,Yi. We collect the conditioning budget and its sampling
consequence together to separate this standard argument from the quantum state alignment.
Lemma 4.8 (Conditioning and answer-history entropy) . Conditioning on WD has exact
relative-entropy cost
D(P( · |WD)∥P) = log(1/p) = τ. (33)
Recalls = |D|log(|A||B|). The answer-word alphabet Z =AD ×BD has log |Z|=s; for every
revealed question tuple U and additional question block YC,
D(QU,YC,Z ∥ PU,YC ⊗ Unif Z ) ≤ τ +s. (34)
Proof. The Radon–Nikodym derivative of Q with respect to P is 1WD/p, which gives ( 33). Data
processing bounds the relative-entropy cost of every question marginal by τ . Conditionally on
those questions, the divergence of Z from the uniform distribution on Z is at most log |Z|=s.
The chain rule gives ( 34).
Lemma 4.9 (Locally generated histories approximate the posterior) . The locally generated
history distributions satisfy
D(Q∥JA), D(Q∥JB) ≤ 3τ + 2s
m , dTV(Q, JA), dTV(Q, JB) ≤ κ.
Classical correlated sampling produces histories rA,rB with respective tuple distributions JA, JB
such that
P(rA ̸=rB) ≤ 4κ. (35)
The proof uses only the preceding conditioning budget, the classical relative-entropy chain
rule, Pinsker’s inequality, and Lemma 3.4; it is deferred to Appendix A.6.
Conclusion. Lemma 4.7 proves the two state inequalities in Lemma 3.3, and Lemma 4.9 gives
its total-variation and matching-history conclusions. Together they complete the proof.
173
===== PAGE 176 =====
A Deferred auxiliary proofs
A.1 Ideal-state extraction and local measurement reﬁnements
Forr = (t,z ), z = (aD,bD), deﬁne the answer-reﬁnement operators
Ha
r,x = EX n∼P ( ·|T =t,Xi=x)[EaD,ai=a
X n ],
Kb
r,y = EY n∼P ( ·|T =t,Yi=y)
[
FbD,bi=b
Y n
]
.
These are positive contractions satisfying
∑
a∈A
Ha
r,x =Hr,x,
∑
b∈B
Kb
r,y =Kr,y.
Lemma A.1 (Singular-safe local POVM reﬁnement) . Let 0 ⪯ F ⪯ I and let {Fa :a ∈A} be
positive operators satisfying ∑
aFa =F . There is a genuine POVM {Ma
F :a ∈A} on the ﬁnite
puriﬁed space such that
Γ(F )†Ma
F Γ(F ) = Fa (a ∈A). (36)
Proof. Use the inverse square root F [− 1/2] on supp(F ), extended by zero on kerF , and put
UF = Γ(F )F [− 1/2].
By ( 5), UF is an isometry on supp(F ). Choose a default a0 ∈A and set
Ma
F =UFF [− 1/2]FaF [− 1/2]U †
F + 1{a=a0}(I −UFU †
F ).
Since 0 ⪯ Fa ⪯ F , each Fa is supported on supp(F ). The displayed operators are positive and
sum to the identity on the entire ﬁnite puriﬁed space. Finally U †
F Γ(F ) = F 1/2, and Γ(F ) has
image in imUF . These identities prove ( 36), including when F has a nontrivial kernel.
Proof of Lemma 3.2. Apply Lemma A.1 to {Ha
r,x}a∈A and {Kb
r,y}b∈B, obtaining local POVMs
{˜Ma
r,x}a∈A and {˜Nb
r,y}b∈B. The reﬁnement identities and ∥ϕr,x,y∥2 =pr(x,y ) give
⟨Ψr,x,y|˜Ma
r,x ⊗ ˜Nb
r,y |Ψr,x,y⟩= ⟨ψ|Ha
r,x ⊗Kb
r,y |ψ⟩
pr(x,y ) .
Prior conditional independence identiﬁes the numerator with the probability of the recorded his-
tory answers together with (Ai,Bi) = (a,b ); the denominator is the probability of the recorded
history answers. Their ratio is therefore Q(Ai = a,Bi = b |R = r,Xi = x,Yi = y), as
claimed.
A.2 The conditioning lemma recalled and proved
Reminder of Lemma 3.1 (Quantitative greedy conditioning) . Supposeϑ> 0, let 0<δ < 1,
and assume
log(1/ϑ)
δ <n.
There exists D ⊊ [n] such that
|D| ≤ log(1/ϑ)
δ ,
P(WD) ≥ ϑ,
1
n − |D|
∑
i∈[n]\ D
P(Wi |WD) ≥ 1 −δ.
174
===== PAGE 177 =====
Proof of Lemma 3.1. Start with D = ∅. If
1
n − |D|
∑
i/∈D
P(Wi |WD)>δ,
choose an i /∈D whose individual conditional failure is larger than δ, and replace D byD ∪ {i}.
Every conditional probability is well deﬁned, since
W[n] ⊆ WD, P(WD) ≥ ϑ> 0.
Each addition strictly decreases the mass by a factor smaller than 1 −δ:
P(WD∪{i}) = P(WD)P(Wi |WD)< (1 −δ)P(WD).
Consequently, after k ≥ 1 additions,
ϑ ≤ P(WD)< (1 −δ)k, k< log(1/ϑ)
− log(1 −δ) ≤ log(1/ϑ)
δ .
The assumed strict inequality prevents all n coordinates from being added. Therefore the
process stops at a proper set. The stopping condition is exactly the asserted average-success
inequality; containment of the all-win event gives the claimed mass. If the process makes no
additions, the same conclusions hold with D = ∅.
A.3 Random live-coordinate reveal martingales
Proof of Lemma 4.1. Consider ﬁrst the Alice-reveal direction and write N = |L+
Y |. In the
forward experiment, choose i uniformly in M , partition the other m − 1 coordinates fairly, and
choose the two orders and cuts uniformly. The probability of a particular outcome is
21−m
m |LX |!(|LX |+ 1)(N − 1)!N.
In the reverse experiment, ﬁrst choose M =LX ⊔L+
Y with probability 2−m2N/m. Then choose
a uniform order πY of L+
Y , a uniform cut kY ∈ {0,...,N − 1}, and set
i =πY [kY + 1], L Y =L+
Y \ {i}.
Deleting i from πY recoversπY,−i. Finally, choose πX,−i and kX as in the forward experiment.
The resulting outcome again has probability
2−m 2N
m
size-biased partition
1
N !
1
N
1
|LX |!
1
|LX |+ 1 = 21−m
m |LX |!(|LX |+ 1)(N − 1)!N.
The reverse construction therefore preserves the exact history distribution while making the live
cut kY uniform.
Fix the partition, its orders, kX , and the background U from ( 21). Given U , the remaining
questionsXj,j ∈L+
Y , are independent with distributions µ(· |Yj). Therefore the tower property
gives
E[Fj+1 |U,Xπ≤ j
Y
] = Fj,
so (Fj)N
j=0 is a positive-contraction martingale. Bob’s eﬀect K is ﬁxed because all questions
on which it depends have already been included in U . At the live cut, averaging over Xi
gives FkY = ¯Hr,Yi, revealing Xi gives FkY +1 = Hr,Xi, and the ﬁxed eﬀect is K = Kr,Yi. This
proves (23).
Interchanging Alice and Bob gives the second construction. Its partition has probability
2−m2|L+
X |/m; the uniform cut kX selects the live question from L+
X , while Alice’s eﬀect remains
ﬁxed. The same conditional-independence and tower arguments give the martingale (Gj)j and
the two stated eﬀects at its live cut.
175
===== PAGE 178 =====
A.4 Resolvent puriﬁcation and its entropy estimate
For positive deﬁnite eﬀects, let f (v) = v logv and H1(v) = −v logv. The associated operator
Bregman divergence is
Df (F, ¯F ) = f (F ) −f ( ¯F ) −Df ( ¯F )[F − ¯F ].
When ¯F = EFF , averaging cancels the derivative term and identiﬁes the expected divergence
with the entropy gap:
EFDf (F, ¯F ) = H1( ¯F ) − EFH1(F ).
Proof of Lemma 4.3. Foru> 0, abbreviate
RF = (F +uI)− 1, R ¯F = ( ¯F +uI)− 1, J =F − ¯F.
The pointwise diﬀerence between the two resolvent puriﬁcations is
Lu =F (F +uI)− 1 − ¯F ( ¯F +uI)− 1 =uRFJR ¯F =uR ¯FJRF.
Since uR2
F ⪯ RF ,
L2
u =u2R ¯FJR 2
FJR ¯F ⪯ uR ¯FJRFJR ¯F.
The second-order resolvent identity gives
RF −R ¯F +R ¯FJR ¯F =R ¯FJRFJR ¯F.
Taking expectations and using EFJ = 0, we obtain
EFL2
u ⪯ u
(
EFRF −R ¯F
)
.
For every positive semideﬁnite C,
∫T
0
u(C +uI)− 1du =TI −C log(C +TI ) +C logC.
Integrate the preceding operator inequality, cancel the TI terms, and let T → ∞ . The remaining
large-T terms vanish because log(F +TI ) = (log T )I + log(I +F/T ) and EFF = ¯F . Therefore
∫∞
0
EFL2
udu ⪯ EF [F logF ] − ¯F log ¯F =H1( ¯F ) − EFH1(F ).
The integral on the left is precisely the left side of ( 25).
A.5 Probability-weighted accepted-answer entropy
Proof of Lemma 4.5. Fix background information U containingXD,YD. The accepted answer
words have total probability pW (U ) and their number is at most
|Z|= |A||D||B||D|=es.
Applying the log-sum inequality to their probabilities pz(U ) gives
∑
z:
1WD (U,z)=1
H1(pz(U )) ≤ H1(pW (U )) +pW (U )s,
which is ( 31). Since EU ∼P 0pW (U ) = p and H1 is concave,
EU ∼P 0H1(pW (U )) ≤ H1(p) = pτ.
A veraging (31) therefore gives ( 32).
176
===== PAGE 179 =====
A.6 Classical sampleability of the revealed history
Proof of Lemma 4.9. Recall the two locally generated tuple distributions
JA(i,r,x,y ) = 1
mµ(x,y )Q(r |i,Xi =x), JB(i,r,x,y ) = 1
mµ(x,y )Q(r |i,Yi =y).
The live coordinate i remains uniform under Q, so the relative-entropy chain rule gives
D(Q∥JA) = Ei∼ Unif(M )D(QXi|i∥µX )
+ E(i,r,x,y)∼QD
(
QYi|i,Xi,T,Z
µ( · |Xi)
)
.
(40)
The product prior and ( 33) imply
∑
i∈M
D(QXi∥µX ) ≤ D(QXM ∥µ⊗m
X ) ≤ τ,
so the ﬁrst term of ( 40) is at most τ/m .
For the second term use the Bob-reveal reverse construction from Section 4. Fix a partition
M =L+
X ⊔LY , its orders, the LY cut, and the background
U = (XD,YD,XL+
X
,YLY,Xπ≤ kY
Y,− i
), |L+
X |> 0.
Equation ( 34) specializes to
D
(
QU,YL+
X
,Z
PU,YL+
X
⊗ Unif Z
)
≤ τ +s.
Under the reference distribution, conditionally on U , the variables Yj,j ∈L+
X , are independent
with distributions µ(· |Xj). Apply the chain rule in the order πX and discard its nonnegative
initial term:
|L+
X |∑
j=1
EQD
(
QYπX [j]|U,Z,Yπ<j
X
µ( · |XπX [j])
)
≤ τ +s.
The live cut is uniform over these |L+
X |positions. Its conditioning data are precisely (i,T,X i,Z ),
while the reverse partition has weight 2|L+
X |/m. These factors cancel, giving
E(i,r,x,y)∼QD
(
QYi|i,Xi,T,Z
µ( · |Xi)
)
≤ 2(τ +s)
m .
Consequently,
D(Q∥JA) ≤ 3τ + 2s
m .
Interchanging Alice and Bob gives the same bound for JB. Pinsker’s inequality and η =
(τ +s)/m imply
dTV(Q, JA), dTV(Q, JB) ≤
√
3τ + 2s
2m ≤
√
3
2η =κ.
Finally, apply Lemma 3.4 to the ﬁnite family
{Q(R |i,Xi =x), Q(R |i,Yi =y)}i,x,y,
including arbitrary ﬁxed defaults for zero posterior marginals. Use public randomness to choose
the uniform coordinate i and perform the correlated sampling. The resulting histories have exact
tuple distributions JA, JB, and
P(rA ̸=rB) ≤ 2 dTV(JA, JB) ≤ 2
(
dTV(JA, Q) + dTV(Q, JB)
)
≤ 4κ.
This proves ( 35).
177
===== PAGE 180 =====
A.7 Proof of ﬁnite classical correlated sampling
Proof of Lemma 3.4. Temporarily generate shared independent proposals
(Zj,Uj)j≥ 1, Z j ∼ Unif(R), U j ∼ Unif[0, 1].
The procedure indexed by D outputs the ﬁrst Zj for which Uj ≤ D (Zj). Each proposal is
accepted with probability 1/|R|, and the output has exactly distribution D. For D, E, inspect
the ﬁrst proposal accepted by either procedure. The probability that it is accepted by only one
of them is ∑
z |D(z) − E (z)|∑
z max{D(z), E(z)} = 2 dTV(D, E)
1 + dTV(D, E) ≤ 2 dTV(D, E).
When the ﬁrst proposal is accepted by both, their outputs agree; thus this also bounds their
eventual disagreement. Since F is ﬁnite, all procedures terminate simultaneously almost surely.
Their joint output vector belongs to the ﬁnite set RF . Use that vector itself as the ﬁnite
shared random variable, and let each player read the component indexed by the locally speciﬁed
distribution. This preserves the exact marginals and all the disagreement bounds without using
an inﬁnite randomness register.
A.8 Quantitative details for the single-game rounding
We ﬁnish the error calculation deferred from Lemma 3.6. On a matching valid branch (i,r,x,y ),
Lemma 3.5 with
σA = ΨA
r,x, σ B = ΨB
r,y
bounds the distance from Alice’s candidate state. A further triangle inequality bounds the
distance from the ideal state by
e(i,r,x,y ) = Kqs
(
α1/12 +
ΨA
r,x − ΨB
r,y

1/6)
+
ΨA
r,x − Ψr,x,y
.
Set e = U∗ outside the support of Q. Since unit vectors have distance at most 2, one has
0 ≤ e ≤ U∗.
The state alignment in Lemma 3.3 and Jensen’s inequality give
E(i,r,x,y)∼Q
ΨA
r,x − ΨB
r,y

1/6
≤
(
E(i,r,x,y)∼Q
ΨA
r,x − ΨB
r,y

2) 1/12
≤ (32η)1/12.
Similarly, E(i,r,x,y)∼Q
ΨA
r,x − Ψr,x,y
≤ √ 8η. Consequently,
E(i,r,x,y)∼Qe(i,r,x,y ) ≤ Kqs
(
α1/12 + (32η)1/12)
+
√
8η.
Let w(i,r,x,y ) be the ideal branch winning probability, and set w = 0 outside the support
of Q. Then 0 ≤ w ≤ 1, E(i,r,x,y)∼Qw(i,r,x,y ) = q, and ( 14) implies
E(i,r,x,y)∼J Aw(i,r,x,y ) ≥ q −κ, E(i,r,x,y)∼J Ae(i,r,x,y ) ≤ E(i,r,x,y)∼Qe(i,r,x,y ) +U∗κ.
Histories disagree with probability at most 4κ. On a matching branch, replacing the ideal
state by one at distance e changes any measurement probability by at most 2e. Therefore the
strategy ( 15) satisﬁes
win(Sα) ≥ q − 5κ − 2
(
E(i,r,x,y)∼Qe(i,r,x,y ) +U∗κ
)
≥ q − (5 + 2U∗)κ − 2Kqsα1/12 − 2Kqs(32η)1/12 − 2
√
8η.
Finally, 0 ≤ η ≤ 1 gives
κ ≤
√
3
2η1/12, √η ≤ η1/12.
Using the constants in ( 11) proves ( 12) with exactly the stated universal constant Bqs.
178
===== PAGE 181 =====
References
[BVY17] M. Bavarian, T. Vidick, and H. Yuen. Hardness ampliﬁcation for entangled games via
anchoring. In Proceedings of the 49th ACM Symposium on Theory of Computing , pages
303–316, 2017. doi:10.1145/3055399.3055433. Revised full version, Anchored parallel
repetition for nonlocal games : https://arxiv.org/abs/1509.07466v2.
[CS14] A. Chailloux and G. Scarpa. Parallel repetition of entangled games with exponential
decay via the superposed information cost. In ICALP 2014 , Lecture Notes in Computer
Science 8572, pages 296–307, 2014. doi:10.1007/978-3-662-43948-7_25; corrected full
version: https://arxiv.org/abs/1310.7787v3.
[CS15] A. Chailloux and G. Scarpa. Parallel repetition of free entangled games: simpliﬁcation
and improvements. arXiv:1410.4397v2, 2015 (ﬁrst version 2014).
https://arxiv.org/abs/1410.4397v2.
[CHTW04] R. Cleve, P. Høyer, B. Toner, and J. Watrous. Consequences and limits of nonlocal
strategies. In Proceedings of the 19th IEEE Conference on Computational Complexity ,
pages 236–249, 2004. doi:10.1109/CCC.2004.1313847;
https://arxiv.org/abs/quant-ph/0404076v1.
[CSUU08] R. Cleve, W. Slofstra, F. Unger, and S. Upadhyay. Perfect parallel repetition theorem for
quantum XOR proof systems. Computational Complexity 17:282–299, 2008.
doi:10.1007/s00037-008-0250-4.
[DSV15] I. Dinur, D. Steurer, and T. Vidick. A parallel repetition theorem for entangled projection
games. Computational Complexity 24(2):201–254, 2015. doi:10.1007/s00037-015-0098-3.
Full arXiv version, including Lemma 17: arXiv:1310.4113v2.
[FMZ25] H. Fu, K. Mastel, and X. Zhang. Succinct perfect zero-knowledge for MIP∗.
arXiv:2503.04517v2, 2025. https://arxiv.org/abs/2503.04517v2.
[Hol09] T. Holenstein. Parallel repetition: Simpliﬁcation and the no-signaling case. Theory of
Computing 5:141–172, 2009. doi:10.4086/toc.2009.v005a008.
[JPY14] R. Jain, A. Pereszlényi, and P. Yao. A parallel repetition theorem for entangled two-player
one-round games under product distributions. In Proceedings of the 29th IEEE Conference
on Computational Complexity , pages 209–216, 2014. doi:10.1109/CCC.2014.29.
[KRT10] J. Kempe, O. Regev, and B. Toner. Unique games with entangled provers are easy. SIAM
Journal on Computing 39(7):3207–3229, 2010. doi:10.1137/090772885.
[KV11] J. Kempe and T. Vidick. Parallel repetition of entangled games. In Proceedings of the
43rd ACM Symposium on Theory of Computing , pages 353–362, 2011.
doi:10.1145/1993636.1993684.
[Kim14] I. H. Kim. Modulus of convexity for operator convex functions. Journal of Mathematical
Physics 55:082201, 2014. doi:10.1063/1.4890292; https://arxiv.org/abs/1310.0746v3.
[Lin25] J. Lin. MIPco = coRE. arXiv:2510.07162, 2025. https://arxiv.org/abs/2510.07162.
[NC10] M. A. Nielsen and I. L. Chuang. Quantum Computation and Quantum Information . 10th
Anniversary Edition, Cambridge University Press, 2010.
[Pet07] D. Petz. Bregman divergence as relative operator entropy. Acta Mathematica Hungarica
116:127–131, 2007. doi:10.1007/s10474-007-6014-9.
[Rao11] A. Rao. Parallel repetition in projection games and a concentration bound. SIAM Journal
on Computing 40(6):1871–1891, 2011. doi:10.1137/080734042.
[Raz98] R. Raz. A parallel repetition theorem. SIAM Journal on Computing 27(3):763–803, 1998.
doi:10.1137/S0097539795280895.
[Raz11] R. Raz. A counterexample to strong parallel repetition. SIAM Journal on Computing
40(3):771–777, 2011. doi:10.1137/090747270.
[Wat18] J. Watrous. The Theory of Quantum Information . Cambridge University Press, 2018.
doi:10.1017/9781316848142.
179
===== PAGE 182 =====
[Yue16] H. Yuen. A parallel repetition theorem for all entangled games. In 43rd International
Colloquium on Automata, Languages, and Programming , LIPIcs 55, article 77, 2016.
doi:10.4230/LIPIcs.ICALP.2016.77. Full version: https://arxiv.org/abs/1604.04340.
180
===== PAGE 183 =====
Chapter 7
n1/400-Hardness of the
Euclidean Closest Vector Problem
Abstract. We study the hardness of approximating the Euclidean closest
vector problem within a ﬁxed polynomial in the lattice dimension. We
present a deterministic polynomial-time many-one reduction from 3SAT to
GapCVP(2)
n1/400, where n is the rank of a lattice given by an explicit square
integer basis. The construction uses Reed–Solomon power-sum constraints
over a characteristic-two ﬁeld to encode assignments and their satisfying
restrictions to individual clauses. It converts the resulting binary aﬃne system
into an integer lattice by coordinatewise reduction modulo two. Completeness
follows from polynomial interpolation. For soundness, a low-weight binary
solution gives small sets of selected ﬁeld values. Reconstruction from their
power sums produces separable root sets over a rational function ﬁeld;
additional power-sum constraints recover the Boolean clause assignments
through valuations, and the clause equations identify a root compatible with
every clause. The same construction yields approximation factors n1/200 for
binary nearest codeword and syndrome decoding and n1/(200p) for closest
vector in every ﬁxed rational ℓp norm, p ≥ 1. The result is a direct reduction
from 3SAT and therefore does not invoke the PCP theorem or assume the
Projection Games Conjecture.
Contents
1. Introduction
2. Preliminaries
3. Encoding Boolean assignments by Reed–Solomon codes
4. Algebraic reconstruction of bounded polynomial-moment families
5. Soundness of the nearest-codeword reduction
6. Transfer to CVP and complexity
7. Further consequences
References
181
===== PAGE 184 =====
1 Introduction
Given a full-rank integer lattice and a target, the closest vector problem (CVP) asks for a
lattice point of minimum Euclidean distance to the target. The computational complexity
of CVP depends on how closely one seeks to approximate this minimum. Writing n for the
lattice rank, we study approximation factors that grow as a ﬁxed polynomial in n.
1.1 The closest vector problem and main result
To formulate the closest vector problem precisely, we ﬁrst describe the lattice generated by
an integer basis and the distance from a target to that lattice.
For a nonsingular integer matrix B ∈ Zn×n, the lattice L(B) generated by the columns of
B is
L(B) = BZn = {Bz : z ∈ Zn}.
The Euclidean distance from a target t ∈ Qn to the lattice L(B) is
dist2(t, L(B)) = min
z∈Zn
∥t − Bz∥2.
For an approximation factor γ(n) ≥ 1, deﬁne the approximate closest vector problem
GapCVP(2)
γ as follows. An instance consists of a nonsingular integer lattice basis B ∈ Zn×n,
a target t ∈ Qn, and a positive rational radius r ∈ Q>0, all encoded in binary. The task is to
distinguish between the following two cases:
YES : dist 2(t, L(B)) ≤ r,
NO : dist 2(t, L(B)) > γ (n)r.
An algorithm must return the indicated answer whenever one of these conditions holds. If
r < dist2(t, L(B)) ≤ γ(n)r, either answer is allowed.
CVP is a central computational problem in the geometry of numbers, with connections
to computational number theory, integer optimization, and cryptography. The lattice-basis
reduction algorithm of Lenstra, Lenstra, and Lovász led to applications in polynomial factor-
ization [ LLL82], and Babai used reduced bases to approximate nearest lattice points, with
applications to integer programming [ Bab86].
The importance of lattice problems extends to public-key and post-quantum cryptography.
Ajtai established a foundational connection between worst-case lattice problems and average-
case computational hardness [ Ajt96]; Goldreich, Goldwasser, and Halevi proposed public-key
encryption and signatures based on lattice-reduction problems [ GGH97]; and Regev intro-
duced learning with errors and related its hardness to worst-case lattice problems [ Reg09].
The practical signiﬁcance of this line of work is reﬂected in the standardization of lattice-based
key encapsulation and digital signatures by the National Institute of Standards and Technol-
ogy [ NIST24a, NIST24b]. These cryptographic applications rely on appropriate structured
or average-case assumptions, rather than directly on the worst-case NP-hardness of CVP.
Nonetheless, they reinforce the importance of determining which approximation regimes for
fundamental lattice problems remain computationally intractable.
Theorem 1 (Main theorem) . There is a deterministic polynomial-time mapping that assigns
to each 3SAT formula φ a nonsingular matrix B ∈ Zn×n, a target t ∈ Zn, and a radius
r ∈ Q>0 such that
φ satisﬁable =⇒ dist2(t, L(B)) ≤ r,
φ unsatisﬁable =⇒ dist2(t, L(B)) > n 1/400r.
Consequently, GapCVP(2)
n1/400 is NP-hard under deterministic polynomial-time many-one re-
ductions.
182
===== PAGE 185 =====
The reduction uses no randomized step, gap-producing PCP, or Projection Games Con-
jecture.
Two related binary coding problems also play a central role. Write F2 for the ﬁeld with
two elements. A binary linear code C ≤ Fn
2 is a linear subspace, and a generator matrix for C
has rows spanning that subspace. For a binary word z, write wt(z) for its Hamming weight ,
the number of nonzero coordinates. Given C and a received word u ∈ Fn
2 , the nearest-codeword
problem asks for the minimum Hamming distance
dH (u, C) = min
c∈C
wt(u − c).
Its promise version receives a generator for C, the word u, and an integer radius R > 0. The
equivalent syndrome-decoding problem receives a binary parity-check matrix H, a syndrome
b, and the same radius, and asks for
min{wt(x) : x ∈ Fn
2 , Hx = b}.
Here H is a parity-check matrix for C = ker F2 H. If b = Hu, the solutions of Hx = b form
the aﬃne coset u + C, so the two objectives agree. For approximation factor γ(n), the YES
threshold is R, and the strict NO threshold is γ(n)R; here n denotes the code block length.
The reduction also establishes approximation hardness within n1/200 for nearest codeword
and syndrome decoding. For every ﬁxed rational p ≥ 1, replacing the Euclidean norm with
the ℓp norm gives a closest-vector factor n1/(200p); setting p = 2 recovers the main Euclidean
exponent. Let N denote the input-size parameter and let q denote the size of the ﬁnite ﬁeld
used in the construction. The ﬁeld size and lattice dimension satisfy
q = Θ(N 200), n ≤ 40N 401,
so the construction has large, but ﬁxed-polynomial, output and bit complexity.
1.2 Proof overview
The reduction factors through binary nearest codeword:
3SAT − →binary nearest codeword − →Euclidean CVP .
The ﬁrst arrow represents our main technical contribution; the second is the standard
dimension-preserving reduction from binary nearest codeword to Euclidean CVP. We now
explain the ﬁrst arrow, the reduction from 3SAT to binary nearest codeword.
Let the input formula have m variables and clauses C1, . . . , Cℓ. Choose a characteristic-two
ﬁeld K = Fq, distinct anchors a1, . . . , am ∈ K, and the evaluation set
P = K \ {a1, . . . , am}.
An assignment σ ∈ {0, 1}m determines the unique interpolation polynomial Qσ ∈ K[X] satis-
fying
deg Qσ < m, Q σ(ai) = σi.
For every p ∈ P and w ∈ K, introduce a binary coordinate x0,p,w. The intended encoding of
Qσ is
x0,p,w = 1 ⇐ ⇒ w = Qσ(p).
For a clause C, let IC be the indices of its variables, and let BC ⊆ { 0, 1}IC be the set of
assignments satisfying C. For every β ∈ B C, introduce another array of binary coordinates
x(C,β),p,w. If σ satisﬁes C, the intended assignment is
x(C,β),p,w = 1 ⇐ ⇒ β = σ|IC and w = Qσ(p).
183
===== PAGE 186 =====
Call these binary arrays evaluation tables : the global table has index τ = 0 , and the clause
tables have indices τ = ( C, β). Such an index τ is called the table type . For any type, deﬁne
its support at p by
Sτ (p) = {w ∈ K : xτ,p,w = 1}.
For the intended assignment, the support of table 0 and each selected clause table is {Qσ(p)};
all other supports are empty. Writing M for the total number of binary coordinates, the proof
proceeds as follows.
(i) Encoding and completeness (Section 3). Impose low-degree constraints on the ordinary
and shifted moments
µτ,j (p) =
∑
w∈Sτ (p)
wj, η τ,i,j (p) =
∑
w∈Sτ (p)
( w − βi
p − ai
) j
,
where the shifted moment is deﬁned for a table indexed by τ = ( C, β) and a variable
i appearing in C. Since p /∈ { a1, . . . , am}, its denominator is nonzero. Require the
moments to be low-degree polynomial evaluations, the support of table 0 to have odd
size, and the tables for each clause to reproduce the indicators of table 0 modulo two.
These conditions give a binary aﬃne system Hx = b. For a satisfying assignment σ,
the indicator assignment deﬁned above gives a solution of weight
R = (ℓ + 1)|P |,
as proved in Lemma 8.
(ii) Algebraic reconstruction (Section 4). Lemma 10 treats a family of bounded sets whose
power sums are low-degree polynomials. It reconstructs one separable polynomial over
the rational function ﬁeld K(X); its roots, in a ﬁnite separable extension, have exactly
those prescribed power sums. This statement is proved independently of the reduction
from 3SAT to binary nearest codeword.
(iii) Nearest-codeword soundness (Section 5). A low-weight solution of Hx = b yields
bounded support sets Sτ (p) after discarding a small number of evaluation points sep-
arately for each type. For each table τ , Lemma 10 produces a root set Rτ ; thus R0
corresponds to table 0, and R(C,β) corresponds to the table indexed by (C, β). Lemma 12
recovers the clause-assignment bit βi from roots in R(C,β). Lemma 13 associates each
α ∈ R 0 with a satisfying assignment β for each clause C such that α ∈ R (C,β). These
assignments agree on shared variables, giving Proposition 14: a suﬃciently low-weight
solution implies that the original formula is satisﬁable.
(iv) Transfer to CVP (Sections 2 and 6). Lemma 7 converts Hx = b into an integer lattice
ΛH and a target u with
dist2(u, ΛH )2 = min
x∈FM
2
Hx=b
wt(x).
Consequently, the binary approximation factor M 1/200 becomes the Euclidean factor
n1/400, where the lattice rank is n = M . Section 6 combines completeness, soundness,
and this standard reduction to prove Theorem 1.
(v) Further consequences (Section 7). Corollaries 15 and 16 give the corresponding hardness
results for binary decoding and for closest vector in each ﬁxed ﬁnite rational norm.
184
===== PAGE 187 =====
1.3 Background and related work
Hardness of approximating closest vector. The complexity-theoretic study of CVP
begins with the NP-hardness of its exact version, proved by van Emde Boas [ vEB81]. Arora,
Babai, Stern, and Sweedyk extended this line of work to approximation, establishing hard-
ness within every ﬁxed constant for problems involving lattices, codes, and systems of linear
equations [ ABSS97]. Dinur, Kindler, and Safra subsequently obtained an almost-polynomial
hardness factor for CVP [ DKS98], reﬁned in the journal version by Dinur, Kindler, Raz, and
Safra [ DKRS03]. In particular, the latter work proves NP-hardness of Euclidean CVP within
na/ log log n for some absolute a > 0.
Although this factor grows faster than every ﬁxed power of log n, its exponent tends to zero.
Consequently, it does not establish hardness within nc for any ﬁxed c > 0.
Complexity-theoretic limits and conditional results. The signiﬁcance of strengthen-
ing the approximation factor becomes clear from upper bounds in a nearby regime. Gol-
dreich and Goldwasser established interactive upper bounds for lattice approximation prob-
lems [ GG00], and Aharonov and Regev proved that, for some absolute constant C > 0,
GapCVP(2)
C√n ∈ NP ∩ coNP.
Thus, NP-hardness at the square-root scale would imply NP = coNP [AR05]. Between the
exponent 1/400 established here and this square-root barrier, it remains open to determine
the largest c ∈ [1/400, 1/2) for which GapCVP(2)
nc is NP-hard.
Moshkovitz [ Mos15, Section 5.1] and Mukhopadhyay [ Muk22] obtain ﬁxed-polynomial
lattice inapproximability conditional on the Projection Games Conjecture. Such conditional
conclusions diﬀer from the unconditional, deterministic reduction from ordinary 3SAT in
Theorem 1.
Coding problems and PCP-free reductions. The coding-theoretic problems used in our
reduction have a related but distinct history. Berlekamp, McEliece, and van Tilborg proved
the intractability of syndrome decoding [ BMVT78], while Vardy established the hardness of
computing the minimum distance of a linear code [ Var97]. Syndrome decoding and nearest
codeword concern an aﬃne coset, whereas minimum distance concerns nonzero vectors in a
linear subspace. Hardness for either formulation therefore does not automatically provide an
approximation gap for the other.
Bhattiprolu, Guruswami, and Ren gave deterministic, PCP-free reductions establishing
NP-hardness of approximating nearest codeword and minimum distance within any ﬁxed
constant factor over each ﬁxed ﬁnite ﬁeld [ BGR25]. Almost-polynomial coding gaps in that
work require the stronger assumption that NP has no quasipolynomial-time algorithms. The
broader work of Bhattiprolu, Guruswami, Lee, and Ren also studies sparse vectors in real
subspaces and lattices, with randomized reductions in those settings [ BGLR25]. These results
do not yield a deterministic nδ-factor hardness result for Euclidean CVP with any ﬁxed δ > 0.
Algebraic reconstruction and lattice lifts. The reduction in this paper uses the
polynomial-evaluation codes introduced by Reed and Solomon [ RS60]. The associated
reconstruction step is related to recovering algebraic information from unordered evalua-
tions and to Reed–Solomon list recovery [ Sud97, ALRS98, GS99, GR06]. The power-sum
Hankel systems also have antecedents in Massey’s shift-register decoding and in subsequent
key-equation methods [ Mas69, RR00, ZGA11]. The structural conclusion needed here diﬀers
185
===== PAGE 188 =====
from a conventional list-decoding output: it produces a complete set of algebraic roots, which
need not be rational functions, rather than only a list of low-degree codewords.
Bennett and Peikert likewise combine Reed–Solomon codes with an integer lattice lift, but
in a randomized hardness reduction for the shortest vector problem. That work also discusses
the obstacles to derandomizing the reduction [ BP23].
Fine-grained hardness. Recent work also examines how quickly approximate lattice prob-
lems can be solved. Aggarwal, Gupta, Morolia, and Zhang establish deterministic ETH-based
lower bounds for constant-factor CVP in every ﬁnite ℓp norm [ AGMZ26]. Huang, Ko, and
Wang study related classical and quantum ﬁne-grained reductions for constant-factor CVP
and Max-Cut [ HKW26]. These results address running-time lower bounds at constant approx-
imation factors rather than unconditional NP-hardness at a ﬁxed polynomial approximation
factor.
2 Preliminaries
We recall ﬁnite-ﬁeld evaluations, valuations, and the standard dimension-preserving reduction
from binary decoding to CVP.
2.1 Finite-ﬁeld evaluations
Let K = Fq, let P ⊆ K, and let D be a nonnegative integer with D < |P |. Deﬁne
RS(P, D) =
{(
f (p)
)
p∈P : f ∈ K[X], deg f ≤ D
}
.
Since a nonzero polynomial of degree at most D has at most D roots, every codeword has
a unique interpolating polynomial. An element of the evaluation code is a codeword, and
a parity check is a linear equation satisﬁed by every codeword. A membership test is an
explicit K-linear system: form the evaluation matrix of 1, X, . . . , XD, compute parity checks
by Gaussian elimination, and require each parity check to vanish. After ﬁxing a basis of K
over F2, each such equation becomes a ﬁnite list of binary-linear equations.
2.2 Valuations
A valuation records orders of vanishing and poles at a speciﬁed point.
Rational functions and orders of vanishing. Let K be a ﬁeld. Its rational function ﬁeld
in the indeterminate X is
F = K(X) =
{g(X)
h(X) : g, h ∈ K[X], h ̸= 0
}
.
Fix a ∈ K and write ℓa = X − a. A rational function cannot always be evaluated at a: for
example, 1/ℓa has a pole there. Nevertheless, it has a well-deﬁned order of vanishing at a.
For a nonzero polynomial g ∈ K[X], let ordℓa(g) be the largest integer m ≥ 0 such that
ℓm
a divides g. Equivalently,
g = ℓm
a g0, g 0(a) ̸= 0.
For nonzero rational functions, deﬁne
ordℓa
( g
h
)
= ord ℓa(g) − ordℓa(h), ordℓa(0) = + ∞.
186
===== PAGE 189 =====
Unique factorization in K[X] shows that the deﬁnition does not depend on the chosen repre-
sentation of g/h. Positive orders correspond to zeros, negative orders to poles, and order zero
to functions that are nonzero and regular at a. In particular,
ordℓa(ℓ3
a) = 3 , ordℓa(1/ℓa) = −1, ordℓa(c) = 0 ( c ∈ K∗).
V aluations and their basic properties. An additive, rational-valued valuation on a ﬁeld
E is a function
v : E − →Q ∪ {+∞}
such that, for all x, y ∈ E,
v(x) = + ∞ ⇐ ⇒ x = 0,
v(xy) = v(x) + v(y),
v(x + y) ≥ min{v(x), v(y)}.
The third property is the ultrametric inequality. Multiplicativity gives
v(1) = v(−1) = 0 , v (−x) = v(x), v (xj) = jv(x) ( x ̸= 0, j ≥ 0).
Since ℓa = X − a, the two notations ordℓa = ord X−a denote the same integer-valued valuation
on F .
The ultrametric inequality prevents a uniquely minimum-valuation summand from being
canceled.
Lemma 2 (Minimum-valuation principle). Let v be a valuation on E. If v(x) ̸= v(y), then
v(x + y) = min {v(x), v(y)}.
More generally, if r ≥ 2, x1, . . . , xr ∈ E∗, and exactly one xj has minimum valuation, then
v
( r∑
i=1
xi
)
= v(xj).
In particular, such a sum cannot be zero.
Proof. Suppose v(x) < v (y). The ultrametric inequality gives v(x+y) ≥ v(x). If the inequality
were strict, applying the same property to x = (x + y) − y would give
v(x) ≥ min{v(x + y), v(y)} > v (x),
a contradiction. For the general statement, put y = ∑
i̸=j xi. Repeated applications of the
ultrametric inequality give
v(y) ≥ min
i̸=j
v(xi) > v (xj),
so the two-term statement applies to xj + y.
Separable polynomials and splitting ﬁelds. Let G(Y ) ∈ F [Y ] be a nonzero polynomial.
A splitting ﬁeld of G is an extension E/F in which G factors into linear polynomials and which
is generated over F by those roots. The polynomial G is separable if its roots in a splitting
ﬁeld are distinct. Equivalently,
gcd
(
G, dG
dY
)
= 1.
The derivative criterion is especially useful in positive characteristic. For example, if char F =
2, then
d
dY (Y 2 − c) = 0 ,
and Y 2 − c has a repeated root in any splitting ﬁeld.
187
===== PAGE 190 =====
Lemma 3 (Common separable splitting ﬁeld) . Let G1, . . . , Gr ∈ F [Y ] be separable polynomi-
als. There is a single ﬁnite separable extension E/F in which all Gi split into linear factors.
Proof. Take a splitting ﬁeld E of the product G1 · · · Gr. It is generated by ﬁnitely many roots,
so E/F is ﬁnite. Every generating root belongs to a separable polynomial Gi and is therefore
separable over F . A ﬁnite extension generated by separable elements is separable, proving
the claim. The product need not itself have distinct roots: diﬀerent Gi may share a root.
Extending a valuation. Let E/F be a ﬁnite separable extension. An extension of ordℓa
to E is a valuation va satisfying
va(f ) = ord ℓa(f ) ( f ∈ F ∗), v a(ℓa) = 1 .
Such an extension need not be integer-valued. For example, if u ∈ E satisﬁes ue = ℓa, then
e va(u) = va(ue) = va(ℓa) = 1 , v a(u) = 1
e .
The appearance of fractional orders is called ramiﬁcation.
Lemma 4 (Existence and normalization of extended valuations) . Let K be a ﬁeld, F = K(X),
a ∈ K, and E/F a ﬁnite separable extension. There exists a valuation
va : E − →Q ∪ {+∞}
whose restriction to F is ordX−a. Moreover, for some positive integer e, its values on E∗ lie
in 1
e Z.
Proof. An element z ∈ E is integral over K[X] if it satisﬁes a monic polynomial with coeﬃ-
cients in K[X]. The set of all such elements,
A = {z ∈ E : z is integral over K[X]},
is the integral closure of K[X] in E. Because E/F is ﬁnite and separable, A is a ﬁnite K[X]-
module and a Dedekind domain. The lying-over property provides a nonzero prime ideal
p ⊆ A above (ℓa), that is,
p ∩ K[X] = ( ℓa).
Localizing at p means allowing denominators outside p:
Ap =
{x
s : x ∈ A, s ∈ A \ p
}
.
The localization of a Dedekind domain at a nonzero prime is a discrete valuation ring . In
particular, its maximal ideal is generated by one element t, called a uniformizer, and every
z ∈ E∗ has a unique expression
z = tnw, n ∈ Z, w ∈ A∗
p.
Here A∗
p denotes the units of the local ring. Deﬁne ordp(z) = n and put
e = ord p(ℓa) > 0, v a(z) = ordp(z)
e , v a(0) = + ∞.
The integer e is the ramiﬁcation index. If g ∈ K[X] \ {0}, write
g = ℓm
a g0, g 0(a) ̸= 0.
Since p ∩ K[X] = ( ℓa), we have g0 /∈ p, so g0 is a unit in Ap. It follows that
ordp(g) = em, v a(g) = m = ord ℓa(g).
Applying the same identity to numerators and denominators shows that va(f ) = ord ℓa(f ) for
every f ∈ F ∗. Finally, ordp(E∗) = Z, so va(E∗) = 1
e Z.
188
===== PAGE 191 =====
V aluation rings and congruence. For a valuation va on E, its valuation ring and maximal
ideal are
Ova = {z ∈ E : va(z) ≥ 0}, mva = {z ∈ E : va(z) > 0}.
The quotient
κ(va) = Ova/mva
is the residue ﬁeld . Reduction modulo mva generalizes evaluation at a: if f ∈ K[X], then
f (X) − f (a) ∈ ℓaK[X], v a
(
f (X) − f (a)
)
≥ 1,
so f (X) and f (a) have the same residue. Since va(c) = 0 for every c ∈ K∗, distinct elements
of K remain distinct in κ(va).
Lemma 5 (Uniqueness of a constant residue) . Let va extend ordX−a to E. For α ∈ E and
b, c ∈ K, if
va(α − b) > 0, v a(α − c) > 0,
then b = c. The same conclusion holds if both lower bounds are replaced by 1.
Proof. If b ̸= c, then b − c ∈ K∗, and therefore va(b − c) = 0 . On the other hand, the
ultrametric inequality gives
va(b − c) = va
(
(α − c) − (α − b)
)
≥ min{va(α − c), va(α − b)} > 0,
a contradiction.
2.3 From binary nearest codeword to CVP
A binary aﬃne decoding instance speciﬁes a matrix and a prescribed right-hand side, called
its syndrome:
H ∈ Fr×M
2 , b ∈ Fr
2,
and the aﬃne system
Hx = b, x ∈ FM
2 ,
where all matrix operations are over F2. The system is consistent if there exists at least one
x ∈ FM
2 satisfying Hx = b; equivalently,
b ∈ imF2 H, or, equivalently, rankF2 H = rank F2[H | b].
It is inconsistent if no such solution exists. Gaussian elimination tests consistency and, in the
consistent case, computes a particular solution in polynomial time. For a consistent system,
the associated minimum-weight aﬃne solution problem asks for a solution having the fewest
nonzero coordinates:
W (H, b) = min
x∈FM
2
Hx=b
wt(x).
Here wt(x), the Hamming weight of x, is the number of its nonzero coordinates. Minimizing
this weight is the standard binary syndrome-decoding problem [BMVT78, ABSS97].
The associated binary nearest-codeword problem is obtained from the homogeneous code
C = kerF2 H,
and a particular solution u ∈ FM
2 of Hu = b identiﬁes the entire solution set:
{x ∈ FM
2 : Hx = b} = u + C.
189
===== PAGE 192 =====
Since subtraction and addition agree in characteristic two,
W (H, b) = min
c∈C
wt(u − c) = dH (u, C),
where dH (u, C) is the Hamming distance from u to the nearest codeword of C. Conversely,
given a binary code C, a parity-check matrix H for C, and a received word u, set
b = Hu.
Then nearest-codeword decoding is exactly minimum-weight decoding of Hx = b. Gaussian
elimination converts between generator and parity-check representations in polynomial time.
A closest-vector instance speciﬁes a nonsingular integer basis B ∈ ZM ×M , the lattice
L(B) = BZM ,
and a target u ∈ ZM . Its Euclidean objective is
dist2(u, L(B)) = min
z∈ZM
∥u − Bz∥2.
The reduction from nearest codeword to closest vector is standard. Feige and Micciancio
and Regev use the corresponding coding-to-lattice connection in their hardness results with
preprocessing; Alekhnovich, Khot, Kindler, and Vishnoi explicitly apply the resulting square-
root conversion of approximation factors [ FM04, Reg04, AKKV11].
The homogeneous code and its integer lift. The homogeneous system associated with
H deﬁnes the binary linear code already introduced above:
C = kerF2 H = {c ∈ FM
2 : Hc = 0}.
The matrix H is a parity-check matrix for C; its rows need not be linearly independent.
Rank–nullity gives
k0 = dim F2 C = M − rankF2 H.
Let
ρ : ZM − →FM
2 , ρ (z) = z mod 2 ,
be coordinatewise reduction modulo two. The inverse image of the homogeneous code is
ΛH = ρ−1(C) = {z ∈ ZM : H(z mod 2) = 0 }.
This inverse-image lattice is classical [ LS71]. Bennett and Peikert likewise combine the corre-
sponding coding-to-lattice lift with Reed–Solomon codes in their randomized shortest-vector
reduction [ BP23]. We call ΛH the parity-lift lattice of H.
For c ∈ C , let ˜c ∈ {0, 1}M denote its integer lift. Then
ΛH =
⋃
c∈C
( ˜c + 2ZM)
, 2ZM ⊆ ΛH ⊆ ZM .
Because C is an additive subgroup of FM
2 , its inverse image ΛH is an additive subgroup of
ZM . Since it contains 2ZM , it is a full-rank integer lattice in RM .
190
===== PAGE 193 =====
An explicit lattice basis. A closest-vector instance requires an integer basis, not merely a
membership condition. Gaussian elimination puts C into systematic form : after a permutation
of the M coordinates, there are k0 free information coordinates f ∈ Fk0
2 , and the remaining
coordinates are determined by a binary matrix
Psys ∈ F(M −k0)×k0
2 .
In these coordinates,
C = {(f, Psysf ) : f ∈ Fk0
2 }.
Here Psys is the parity-coordinate matrix : it gives the dependent parity coordinates as a
function of the free information coordinates. Write
˜Psys ∈ {0, 1}(M −k0)×k0
for its entrywise integer lift.
These free and parity coordinates give the following explicit lattice basis.
Lemma 6 (Explicit parity-lift lattice basis) . In systematic coordinate order, ΛH has integer
basis
BH =
(
Ik0 0
˜Psys 2IM −k0
)
. (1)
In particular,
ΛH = BH ZM , | det BH | = 2 M −k0 = 2 rankF2 H .
The basis and the coordinate permutation can be computed in polynomial time from H.
Proof. In systematic coordinates, write
z = (f, g), f ∈ Zk0, g ∈ ZM −k0.
The deﬁnition of ΛH gives
z ∈ ΛH ⇐ ⇒ g ≡ ˜Psysf (mod 2)
⇐ ⇒ g = ˜Psysf + 2w for some w ∈ ZM −k0
⇐ ⇒ z = BH
(
f
w
)
.
Thus ΛH = BH ZM . The determinant follows from the block-triangular form. Gaussian
elimination computes Psys and the permutation; the inverse permutation restores the basis to
the original coordinate order.
The aﬃne system becomes a lattice coset. When Hx = b is consistent, Gaussian
elimination provides a particular solution
u ∈ {0, 1}M , Hu = b over F2.
Every binary solution diﬀers from u by a codeword:
{x ∈ FM
2 : Hx = b} = (u mod 2) + C.
Likewise, the integer vectors having syndrome b form the lattice coset
{z ∈ ZM : H(z mod 2) = b} = u + ΛH .
Thus the natural candidate for the closest-vector instance is the integer basis BH and target
u. The following lemma gives their exact distance relation.
191
===== PAGE 194 =====
Lemma 7 (Standard nearest-codeword-to-CVP reduction) . Let H ∈ Fr×M
2 and b ∈ Fr
2,
and suppose Hx = b is consistent. In deterministic polynomial time, one can construct a
nonsingular matrix
BH ∈ ZM ×M
and a target
u ∈ {0, 1}M
such that
dist2(u, L(BH ))2 = W (H, b).
More generally, for every real p ≥ 1, the same basis and target satisfy
min
λ∈L(BH )
∥u − λ∥p
p = W (H, b).
The lattice rank is exactly M .
Proof. Use Gaussian elimination over F2 to compute a particular solution u of Hu = b, a
systematic form of kerF2 H, and the basis BH from Lemma 6. Restore the original coordinate
order after constructing the basis. This takes polynomial time, and
L(BH ) = Λ H .
Let λ ∈ L(BH ) and put
x = (u − λ) mod 2 .
Since H(λ mod 2) = 0 , we have Hx = b. Each nonzero coordinate of x comes from an odd
integer coordinate of u − λ, whose absolute value is at least one. Therefore
∥u − λ∥p
p =
M∑
j=1
|uj − λj|p ≥ wt(x) ≥ W (H, b).
Conversely, let x be any binary solution of Hx = b and let ˜x ∈ { 0, 1}M be its integer lift.
Then
H
(
(u −˜x) mod 2
)
= b − b = 0,
so u −˜x ∈ ΛH . Choosing λ = u −˜x gives
∥u − λ∥p
p = ∥˜x∥p
p = wt(x).
Taking minima over binary solutions proves the ℓp identity. Substituting p = 2 gives
dist2(u, L(BH ))2 = W (H, b).
Since BH is a nonsingular M × M integer matrix, the lattice rank is M .
Consequently, a binary weight gap
W (H, b) ≤ R versus W (H, b) > ΓR
becomes the closest-vector gap
min
λ∈ΛH
∥u − λ∥p ≤ R1/p versus min
λ∈ΛH
∥u − λ∥p > Γ1/pR1/p.
For p = 2, the approximation factor is
√
Γ. These are real-valued distance thresholds, which
need not themselves be rational. The reduction also requires a particular solution u, and
therefore applies only to consistent aﬃne systems.
192
===== PAGE 195 =====
For example, take
H =
(
1 1 1
)
, b = 1.
The homogeneous code and its parity-lift lattice are
C = {000, 011, 101, 110},
ΛH = {z ∈ Z3 : z1 + z2 + z3 ≡ 0 (mod 2) }.
Here k0 = 2, and a systematic-form matrix and lattice basis are
Psys =
(
1 1
)
, B H =


1 0 0
0 1 0
1 1 2

.
Choose u = (1 , 0, 0). The binary solutions of Hx = 1 are the odd-parity vectors, and their
minimum weight is one. Correspondingly,
dist2(u, ΛH ) = 1 .
3 Encoding Boolean assignments by Reed–Solomon codes
Let φ be a 3SAT formula of encoding length s. The purpose of this section is to encode
its Boolean assignments and clause constraints in a binary aﬃne system whose structure is
controlled by Reed–Solomon codes.
A single interpolation polynomial ﬁrst records the Boolean assignment. Binary indicators
then encode its values at the evaluation points, and clause-indexed copies of those indicators
represent possible satisfying local assignments. Low-degree moment constraints tie these
tables together without leaving the binary aﬃne setting.
Delete tautological clauses and repeated occurrences of a literal. A formula containing
an empty clause is trivially unsatisﬁable, whereas one with no remaining clauses is trivially
satisﬁable; handle these cases separately. Otherwise delete unused variables. Write
v1, . . . , vm and C1, . . . , Cℓ
for the remaining variables and clauses, where m, ℓ ≥ 1. Write [m] := {1, . . . , m} for the set
of variable indices.
3.1 Assignments as interpolation polynomials
Let
K = Fq
be a characteristic-two ﬁeld large enough to contain distinct elements
a1, . . . , am ∈ K.
We call ai the anchor of the Boolean variable vi. Identify the Boolean values 0 and 1 with
the corresponding elements of K.
A Boolean assignment
σ = (σ1, . . . , σm) ∈ {0, 1}m
determines a unique interpolation polynomial
Qσ ∈ K[X], deg Qσ ≤ m − 1, Q σ(ai) = σi (1 ≤ i ≤ m).
193
===== PAGE 196 =====
Explicitly, Lagrange interpolation gives
Qσ(X) =
m∑
i=1
σi
∏
1≤h≤m
h̸=i
X − ah
ai − ah
.
All denominators are nonzero because the anchors are distinct. Conversely, any polynomial
of degree at most m − 1 taking values in {0, 1} at the anchors recovers a Boolean assignment
by evaluation.
Let
P = K \ {a1, . . . , am}
be the set of non-anchor evaluation points. The vector
(
Qσ(p)
)
p∈P ∈ RS(P, m − 1)
is a Reed–Solomon encoding of the assignment polynomial. Excluding the anchors ensures
that
p − ai ̸= 0 ( p ∈ P, 1 ≤ i ≤ m),
so these diﬀerences can be used as denominators. We write
d = m
for a convenient upper bound on the degree of an assignment polynomial.
Encode each polynomial evaluation by one binary coordinate for each ﬁeld value: the
coordinate for the actual value is one and all others are zero. This one-hot array is the global
evaluation table .
3.2 Clause assignments and evaluation tables
For each clause, introduce one additional evaluation table for each of its satisfying local
assignments.
For each clause C, let
IC ⊆ [m]
be the indices of the variables occurring in C, and deﬁne
BC = {β ∈ {0, 1}IC : β satisﬁes C}.
Thus BC consists of all satisfying local assignments to the variables in C. Since a clause has
at most three variables,
|IC| ≤ 3, |BC| ≤ 8.
If a global assignment σ satisﬁes C, then its restriction
σ|IC ∈ B C
selects one satisfying local assignment.
Index the global table and all clause-indexed copies by
Θ = {0} ∪ {(C, β) : C a clause , β ∈ B C}.
We call an element of this index set a table type . Type 0 represents the global assignment
polynomial. A type (C, β) represents a candidate local assignment for clause C and is called
a clause subtype .
194
===== PAGE 197 =====
For a satisfying assignment σ, declare the global type 0 and, for each clause C, the clause
subtype (C, σ|IC ) to be active. Every other clause subtype is inactive. An active table records
the one-hot evaluations of the assignment polynomial; an inactive table is identically zero.
For every table type, evaluation point, and candidate ﬁeld value,
τ ∈ Θ, p ∈ P, w ∈ K,
introduce a binary indicator
xτ,p,w ∈ F2.
For a ﬁxed type τ and point p, the coordinates
(
xτ,p,w
)
w∈K
form the evaluation ﬁber at p. For a satisfying assignment, a ﬁber of an active type is an
active ﬁber ; it has exactly one nonzero indicator, namely
xτ,p,Qσ(p) = 1.
A general binary table can also have ﬁbers containing several nonzero coordinates.
3.3 Reed–Solomon moment constraints
For each evaluation ﬁber, record the power sums of its selected ﬁeld values.
Fix a moment budget T ≥ 0 and assume
dT < |P |.
For 0 ≤ j ≤ T , use the convention w0 = 1 , including when w = 0 . Deﬁne the ordinary
moments
µτ,j (p) =
∑
w∈K
xτ,p,w wj.
If a ﬁber is supported only at w = Qσ(p), then
µτ,j (p) = Qσ(p)j.
As p varies, these are evaluations of the polynomial
Qσ(X)j, deg Qσ(X)j ≤ (m − 1)j ≤ d j.
Therefore the ordinary moments should form a Reed–Solomon codeword of degree at most d j.
For a clause-indexed table, also form shifted power sums by subtracting each prescribed
local Boolean value and dividing by the corresponding nonzero anchor diﬀerence.
For a clause type τ = (C, β) and an index i ∈ IC, deﬁne the shifted moments
η(C,β),i,j(p) =
∑
w∈K
x(C,β),p,w
( w − βi
p − ai
) j
.
The denominator is nonzero because p ∈ P . If βi = σi, then
Qσ(ai) = βi,
and the factor theorem yields
Qσ(X) − βi
X − ai
∈ K[X].
195
===== PAGE 198 =====
When m ≥ 2, this quotient has degree at most m − 2; when m = 1, it is zero. Thus an active
clause ﬁber has shifted moments
η(C,β),i,j(p) =
( Qσ(p) − βi
p − ai
) j
,
which form a Reed–Solomon codeword of degree at most (d − 1)j.
Impose the following four groups of constraints:
(C1) For every p ∈ P , ∑
w∈K
x0,p,w = 1 in F2.
Thus every global ﬁber has odd parity.
(C2) For every clause C, p ∈ P , and w ∈ K,
x0,p,w =
∑
β∈BC
x(C,β),p,w in F2.
Thus the local ﬁbers for C reproduce the global ﬁber modulo two.
(C3) For every τ ∈ Θ and 0 ≤ j ≤ T ,
(
µτ,j (p)
)
p∈P ∈ RS(P, d j).
(C4) For every τ = (C, β), i ∈ IC, and 0 ≤ j ≤ T ,
(
ητ,i,j (p)
)
p∈P ∈ RS(P, (d − 1)j).
In particular, condition (C4) uniquely determines the shifted-moment interpolation polynomial
ητ,i,j (X) ∈ K[X], deg ητ,i,j ≤ (d − 1)j,
ητ,i,j (p) =
∑
w∈K
xτ,p,w
( w − βi
p − ai
) j
(p ∈ P ). (2)
Uniqueness follows from (d − 1)j < |P |.
Although the moments involve powers of ﬁeld elements, their unknowns are the binary
indicators xτ,p,w ; every ﬁeld element multiplying an indicator is a known coeﬃcient. Moreover,
by Section 2, membership in a Reed–Solomon code is given by linear parity checks over K.
Expanding these checks in an F2-basis of K, all four families together form an explicit binary
aﬃne system
Hx = b over F2. (3)
3.4 Completeness of the encoding
The one-hot graph of a satisfying assignment, together with the clause copies indexed by its
satisfying local restrictions, has the following completeness guarantee.
Lemma 8 (Satisfying assignments give low-weight binary solutions) . If φ is satisﬁable, sys-
tem (3) has a binary solution of Hamming weight
R = (ℓ + 1)|P |.
196
===== PAGE 199 =====
Proof. Let
σ = (σ1, . . . , σm) ∈ {0, 1}m
be a satisfying assignment and let Qσ be its interpolation polynomial. For each p ∈ P , set
x0,p,Qσ(p) = 1
and set all other coordinates of the global ﬁber to zero. For each clause C, select its satisfying
restriction
β = σ|IC ∈ B C.
Set
x(C,β),p,Qσ(p) = 1 ( p ∈ P )
and set all other clause-type coordinates to zero.
Each global ﬁber has exactly one nonzero coordinate, so condition (C1) holds. For each
clause, exactly one subtype reproduces the global ﬁber, proving condition (C2). The ordinary
moments of an active type are
Qσ(p)j,
and those of an inactive type are zero. Since
deg Qσ(X)j ≤ (m − 1)j ≤ d j,
condition (C3) follows. For an active subtype and i ∈ IC, the shifted moments are the
evaluations of ( Qσ(X) − σi
X − ai
) j
.
The quotient has degree at most m − 2 when m ≥ 2 and is zero when m = 1. Its powers there-
fore satisfy condition (C4); at j = 0 , the active shifted moment is the constant one. Finally,
there are exactly ℓ + 1 active coordinates at each evaluation point: one global coordinate and
one coordinate for each clause. Hence
wt(x) = ( ℓ + 1)|P | = R.
3.5 Parameter choices and encoding size
Fix the parameters and bound the size of the resulting binary aﬃne system. Let
N = 100 + s + m + ℓ, d = m, K = N 4, T = N 30, c = 1/400.
Choose the least integer e satisfying
2e ≥ N 200,
and deﬁne
q = 2 e, N 200 ≤ q < 2N 200, K = Fq.
This ﬁeld can be constructed deterministically. Enumerate the monic binary polynomials of
degree
e = O(log N )
and apply the standard polynomial-time irreducibility test until an irreducible polynomial is
found. Even exhaustive enumeration costs at most
2e = N O(1).
197
===== PAGE 200 =====
Since q ≥ N 200 > m, distinct anchors a1, . . . , am ∈ K exist. Their complement satisﬁes
|P | = q − m, dT ≤ N 31 < q − m = |P |,
so every Reed–Solomon degree bound above is strictly smaller than the number of evaluation
points.
The type count is bounded by
|Θ| = 1 +
∑
C
|BC| ≤ 1 + 8ℓ.
There is one binary indicator for each triple (τ, p, w), so the dimension of the aﬃne system is
M = |Θ| |P | q ≤ (1 + 8ℓ)q2 ≤ 40N 401. (4)
Each K-linear Reed–Solomon parity check becomes
e = [K : F2]
binary equations, and each code membership condition requires at most |P | ﬁeld-valued
checks. Furthermore, ∑
C
|BC| |IC| ≤ 3(|Θ| − 1).
Therefore, conditions (C1) through (C4) produce at most
|P | + ℓ|P |q + 4|Θ|(T + 1)|P |e = O(N 401) (5)
binary equations. Here
|Θ| ≤ 9N, |P | < q < 2N 200, T = N 30, e = O(log N ).
Together, (4) and ( 5) show that the dense binary encoding of H has at most
O(N 802)
bits. In particular, the complete aﬃne system is constructible in deterministic polynomial
time.
4 Algebraic reconstruction of bounded polynomial-moment
families
We isolate the following algebraic inverse problem: when do bounded, unordered sets whose
power sums agree with low-degree polynomials admit a single global description? We show
that these power sums are also the power sums of the roots of a single polynomial, indepen-
dently of Boolean assignments, clauses, and binary aﬃne systems.
4.1 Bounded moment families and algebraic root sets
Let K be a ﬁnite ﬁeld and P ⊆ K a set of evaluation points. At each p ∈ P , we are given an
unordered set S(p) ⊆ K, forming the family
S = (S(p))p∈P .
The set S(p) is called the ﬁber at p. There is no prescribed correspondence between the
elements at diﬀerent points, and the sizes of the sets may vary.
198
===== PAGE 201 =====
Each set must have at most K elements, and its power sums up to a moment budget T
must agree with low-degree polynomials, even though its individual elements need not vary
polynomially with p. To formulate this condition, write
mj(p) :=
∑
w∈S(p)
wj
for the j-th moment of S(p), using the convention w0 = 1 even when w = 0 . In particular,
m0(p) is |S(p)| interpreted in K; in characteristic two, it records the parity of the set size,
rather than its integer value. The following deﬁnition makes the two regularity conditions
precise.
Deﬁnition 9 (Bounded polynomial-moment family) . Let d, K ∈ Z≥1, let T ∈ Z≥0 satisfy
dT < |P |. A family S = (S(p))p∈P is a (d, T, K)-bounded polynomial-moment family if it has
the following two properties:
(M1) Uniformly bounded sets. Every pointwise set has at most K elements:
|S(p)| ≤ K (p ∈ P ).
(M2) Low-degree polynomial moments. For every 0 ≤ j ≤ T , there is a polynomial
µj(X) ∈ K[X], deg µj ≤ d j,
satisfying
µj(p) = mj(p) ( p ∈ P ).
The polynomials µ0, . . . , µT are called the moment polynomials of the family.
Since d j≤ dT < |P |, the polynomial in condition (M2) is unique: two degree-at-most- d j
polynomials agreeing on P must coincide. Condition (M1) holds at every point indexing the
family and permits empty sets.
The global structure to be extracted. To see the kind of global structure we seek, ﬁrst
consider K low-degree polynomials
q1(X), . . . , qK(X) ∈ K[X], deg qt ≤ d.
Suppose that their evaluations are pairwise distinct at every p ∈ P , and deﬁne
S(p) = {q1(p), . . . , qK(p)}.
Then the moment polynomials are simply
µj(X) =
K∑
t=1
qt(X)j, deg µj ≤ d j.
In particular, evaluating µj at p gives the j-th moment of S(p). The entire family is explained
by the single polynomial
G(Y ) =
K∏
t=1
(
Y − qt(X)
)
∈ K[X][Y ].
Its roots are the global polynomials q1(X), . . . , qK(X); at each p, evaluating its coeﬃcients
recovers the polynomial whose roots are the elements of S(p).
199
===== PAGE 202 =====
Unlike this example, a bounded polynomial-moment family need not arise from globally
labeled polynomials qt. Nevertheless, its moment polynomials still yield an analogous global
description. Set
F = K(X), h = max
p∈P
|S(p)| ≤ K.
The desired global description consists of a monic separable polynomial
G(Y ) ∈ F [Y ], degY G = h.
Its distinct roots should form, in a ﬁnite separable extension E/F , the root set
R = {α ∈ E : G(α) = 0 }, |R| = h,
whose power sums reproduce the original moment polynomials:
∑
α∈R
αj = µj(X) (0 ≤ j ≤ T ).
The roots play the role of q1(X), . . . , qK(X) in the example, but may be algebraic rather than
polynomial or rational functions. Moreover, wherever |S(p)| = h, evaluating the coeﬃcients
of G at p recovers the monic polynomial whose roots are exactly the elements of S(p).
Encoding a pointwise set without labeling it. Recovering a polynomial from its mo-
ment sequence follows a classical method of Massey [ Mas69]. Here the moments additionally
depend on the evaluation point.
The natural polynomial associated with a particular set S(p) is
∏
w∈S(p)
(Y − w) ∈ K[Y ].
This product is monic, has degree |S(p)|, and vanishes precisely at the elements of S(p). Its
coeﬃcients are symmetric functions of those elements: they do not change when the elements
are reordered. Consequently, no ordering or labeling is required. If S(p) = ∅, the empty
product is 1.
To explain how the moments determine this product, suppose that h > 0 and consider a
point satisfying |S(p)| = h. Write
∏
w∈S(p)
(Y − w) = Y h +
h−1∑
l=0
gp,lY l, g p,l ∈ K.
Since the product vanishes at every w ∈ S(p), multiplying by wi and summing gives
0 =
∑
w∈S(p)
wi
(
wh +
h−1∑
l=0
gp,lwl
)
= mi+h(p) +
h−1∑
l=0
gp,lmi+l(p) (0 ≤ i < h ).
Thus the coeﬃcients gp,l satisfy a linear system whose entries are the moments. The coeﬃcient
matrix is a Hankel matrix: its entries depend only on the sum of their row and column indices.
Here it is (
mi+l(p)
)
0≤i,l<h.
Because S(p) consists of h distinct elements, this matrix factors as a Vandermonde matrix
times its transpose. The Vandermonde matrix lists successive powers of those distinct elements
and is therefore invertible. Hence the moments determine the entire product polynomial,
without identifying any individual element.
200
===== PAGE 203 =====
Constructing one global polynomial. The pointwise Hankel systems are linked by a
simple observation: each entry mj(p) is the evaluation of the same moment polynomial µj(X).
Consequently, all the pointwise Hankel matrices arise by specializing one polynomial matrix,
(
µi+l(X)
)
0≤i,l<h.
Solve one linear system with X left as an indeterminate:
h−1∑
l=0
µi+l(X)cl(X) = −µi+h(X) (0 ≤ i < h ).
At any point where |S(p)| = h, the polynomial matrix specializes to the invertible pointwise
Hankel matrix. Its determinant is therefore not identically zero. Hence the global system has
a unique solution over the rational function ﬁeld F = K(X). Division by the determinant
may be necessary, which explains why its solutions need not belong to K[X].
The coeﬃcient functions obtained from this one system deﬁne a single monic polynomial
G(Y ) = Y h +
h−1∑
l=0
cl(X)Y l ∈ F [Y ].
At a point p where |S(p)| = h, the pointwise matrix is invertible. Cramer’s rule expresses
the rational coeﬃcients cl(X) using the determinant of the global matrix as a common denom-
inator. At p, that denominator becomes the nonzero determinant of the pointwise matrix, so
the coeﬃcients can be evaluated. Their evaluations solve the original pointwise system, and
uniqueness therefore gives
evp(G)(Y ) := Y h +
h−1∑
l=0
cl(p)Y l =
∏
w∈S(p)
(Y − w).
Thus one global polynomial recovers the maximum-size pointwise sets.
Why the roots may require an extension. Although G has coeﬃcients in F = K(X),
it need not split over F . Its individual roots therefore need not be rational functions of X.
Instead, pass to a splitting ﬁeld E/F and write
R = {α ∈ E : G(α) = 0 }.
These roots are nevertheless algebraic functions of X. Indeed, if D(X) ∈ K[X] is a nonzero
common denominator of the coeﬃcients of G, then
˜G(X, Y ) := D(X)G(Y ) ∈ K[X, Y ], ˜G(X, α) = 0 ( α ∈ R).
Thus each root satisﬁes a polynomial equation over K[X], even though it need not belong to
K(X).
4.2 The algebraic reconstruction lemma
The following lemma gives the precise reconstruction statement.
Lemma 10 (Algebraic reconstruction of bounded polynomial moments) . Let K be a ﬁnite
ﬁeld, let P ⊆ K, and let
S = (S(p))p∈P , S (p) ⊆ K,
201
===== PAGE 204 =====
be a (d, T, K)-bounded polynomial-moment family with moment polynomials µ0, . . . , µT ∈
K[X]. In other words, assume that
deg µj ≤ d j, µ j(p) =
∑
w∈S(p)
wj (p ∈ P, 0 ≤ j ≤ T ),
and
|S(p)| ≤ K (p ∈ P ).
Put F = K(X), and suppose that
T ≥ 2K − 1, |P | − dK(K − 1) > 2dK2T.
Deﬁne the maximum ﬁber size
h := max
p∈P
|S(p)| ≤ K
and its Hankel determinant
∆h(X) :=



1, h = 0,
det
(
µi+j(X)
)
0≤i,j<h, h > 0.
Then ∆h ̸= 0, and there exist a monic separable polynomial
G(Y ) = Y h +
h−1∑
l=0
clY l ∈ F [Y ],
and a ﬁnite separable splitting ﬁeld E/F of G. Write
R = {α1, . . . , αh} = {α ∈ E : G(α) = 0 },
so that these objects have the following properties:
(i) Moment identities. For every 0 ≤ j ≤ T ,
µj(X) =
∑
α∈R
αj. (6)
(ii) Maximum-size ﬁbers. For every p ∈ P ,
∆h(p) ̸= 0 ⇐ ⇒ | S(p)| = h.
In particular,
#{p ∈ P : |S(p)| = h} ≥ | P | − dh(h − 1).
(iii) Coeﬃcients and discriminant. The polynomial ∆h is nonzero and satisﬁes
deg ∆h ≤ dh(h − 1).
If h > 0, the coeﬃcients c0, . . . , ch−1 ∈ F are the unique solution of
h−1∑
l=0
µi+l(X)cl = −µi+h(X) (0 ≤ i < h ). (7)
For every 0 ≤ l < h , there is an nl ∈ K[X] such that
cl = nl
∆h
, deg nl ≤ d(h2 − l) ≤ dh2.
Furthermore,
∆h =
∏
1≤r<s≤h
(αs − αr)2. (8)
202
===== PAGE 205 =====
(iv) Specialization. For every p ∈ P satisfying |S(p)| = h, one has ∆h(p) ̸= 0 . Thus the
coeﬃcientwise specialization
evp(G)(Y ) := Y h +
h−1∑
l=0
cl(p)Y l ∈ K[Y ]
is deﬁned and satisﬁes
evp(G)(Y ) =
∏
w∈S(p)
(Y − w). (9)
When h = 0 , the empty-sum and empty-product conventions give G = 1 , R = ∅, ∆0 = 1 ,
and µj = 0 for every 0 ≤ j ≤ T . The conclusions hold in every characteristic, including
characteristic two.
Proof. If h = 0, then S(p) = ∅ for every p ∈ P . Consequently µj vanishes at all |P | evaluation
points. Since
deg µj ≤ dT < |P | (0 ≤ j ≤ T ),
the polynomial root bound gives µj = 0 for every j. Taking G = 1, E = F , and R = ∅ proves
all the conclusions.
Suppose henceforth that h > 0. Since 2h − 2 ≤ 2K − 2 ≤ T , all moments in ∆h are
deﬁned. Expansion of its determinant and the inequalities deg µi+j ≤ d(i + j) give
deg ∆h ≤ dh(h − 1). (10)
At any point with
S(p) = {w1, . . . , wh},
the moment identities give
(
µi+j(p)
)
0≤i,j<h = VpV T
p , (Vp)i,s = wi
s.
Since the ws are distinct, Vp is an invertible Vandermonde matrix, and therefore
∆h(p) = det( Vp)2 =
∏
1≤s<t≤h
(wt − ws)2 ̸= 0. (11)
Because h is the maximum ﬁber size, at least one such point exists. Hence ∆h is a nonzero
polynomial.
At every point with |S(p)| < h, the size- h moment matrix factors as
(
µi+j(p)
)
0≤i,j<h = WpW T
p , (Wp)i,w = wi (0 ≤ i < h, w ∈ S(p)).
The matrix Wp has fewer than h columns, so its product has rank less than h, and ∆h(p) = 0 .
By ( 10), the nonzero polynomial ∆h has at most dh(h − 1) zeros. Since every ﬁber has size
at most h, it follows that
#{p ∈ P : |S(p)| = h} ≥ | P | − dh(h − 1) ≥ |P | − dK(K − 1) > 2dK2T. (12)
Since ∆h ̸= 0, the Hankel system ( 7) has a unique solution over F . For that solution, set
G(Y ) = Y h +
h−1∑
l=0
clY l.
203
===== PAGE 206 =====
Cramer’s rule gives a common denominator ∆h. Replacing column l by (µi+h)0≤i<h gives a
numerator of degree at most
d
(
h(h − 1) + h − l
)
= d(h2 − l) ≤ dh2.
Fix any point satisfying
S(p) = {w1, . . . , wh}.
Equation ( 11) gives ∆h(p) ̸= 0 , so the coeﬃcients cl have no poles at p. Specializing ( 7)
therefore gives, for 0 ≤ i < h ,
0 = µi+h(p) +
h−1∑
l=0
µi+l(p)cl(p)
=
h∑
s=1
wi
s
(
wh
s +
h−1∑
l=0
cl(p)wl
s
)
=
h∑
s=1
wi
s evp(G)(ws).
Equivalently,
Vp


evp(G)(w1)
...
evp(G)(wh)

= 0.
Since Vp is invertible, every ws is a root of evp(G)(Y ). Both sides of ( 9) are monic of degree
h, so the claimed specialization follows.
Let α1, . . . , αh be the roots of G in a splitting ﬁeld, initially listed with multiplicity.
Newton’s identities express their j-th power sum as a polynomial
Pj(c0, . . . , ch−1)
of total degree at most j. For j > h , use the recurrence given by the monic equation G(αs) = 0 .
Crucially, this direction of Newton’s identities computes power sums from coeﬃcients without
dividing by j; it remains valid in characteristic two. For 1 ≤ j ≤ T , the expression
∆j
h
(
µj − Pj(c0, . . . , ch−1)
)
is a polynomial of degree at most
2dh2j ≤ 2dK2T.
By ( 9), it vanishes at every point with |S(p)| = h. There are strictly more than 2dK2T such
points by ( 12), so the polynomial is identically zero. Consequently,
µj(X) =
h∑
s=1
αj
s (1 ≤ j ≤ T ).
For j = 0, the polynomial µ0 is constant. At any point with |S(p)| = h, it equals
µ0(p) = h · 1 =
h∑
s=1
α0
s in K,
which proves the remaining moment identity without mistaking parity for integer cardinality.
Since 2h − 2 ≤ T , the root moment identities give
∆h = det
(
VαV T
α
)
= det(Vα)2, (Vα)i,s = αi
s.
As ∆h ̸= 0 , the roots α1, . . . , αh are distinct. Therefore G is separable and its root set R
satisﬁes both ( 6) and ( 8).
204
===== PAGE 207 =====
Relation to Reed–Solomon list reconstruction and recovery . Ar, Lipton, Rubinfeld,
and Sudan studied reconstruction of several algebraic functions from unordered, mixed evalua-
tions [ALRS98]. Reed–Solomon list recovery has the same pointwise input—small sets S(p)—
but usually seeks all low-degree polynomials f ∈ K[X] satisfying f (p) ∈ S(p) at suﬃciently
many points [ Sud97, GS99, GR06]. Generalized key-equation and block-Hankel methods give
a further technical connection [ RR00, ZGA11]. Recent work sharpens the achievable agree-
ment and output-list bounds [ GST23, GLSTW24, LS25], and power sums have also appeared
in Reed–Solomon decoding and lattice hardness [ GGG18, BP23].
The additional hypothesis here is that the power sums of the entire pointwise sets are
low-degree polynomials. For h > 0, the reconstruction produces the bivariate interpolation
polynomial
Q(X, Y ) := ∆ h(X)G(Y ) = ∆ h(X)Y h +
h−1∑
l=0
nl(X)Y l ∈ K[X, Y ].
At a maximum-size point, Q vanishes on S(p) by specialization. At a smaller point, the
Hankel matrix and each of its column replacements factor through a Vandermonde matrix
with fewer than h columns, so ∆h(p) and every nl(p) vanish. Hence
Q(p, w) = 0 ( p ∈ P, w ∈ S(p)).
Moreover, for every f ∈ K[X] of degree at most d, the coeﬃcient bounds give
degX Q(X, f(X)) ≤ dh2.
Therefore, if f (p) ∈ S(p) at more than dh2 points, the polynomial root bound gives G(f ) =
0. Thus every such list-recovery candidate is one of at most h rational roots of G. The
reconstruction also retains its possibly nonrational algebraic roots, together with the exact
whole-ﬁber moment and specialization identities that remain valid in characteristic two.
5 Soundness of the nearest-codeword reduction
We now return to the binary aﬃne system ( 3). Recall that its coordinate xτ,p,w indicates
whether the ﬁeld element w is selected at evaluation point p in the table indexed by τ . The
index τ = 0 denotes the global table, while τ = (C, β) denotes the table for a satisfying local
assignment β ∈ B C to clause C.
We prove that a suﬃciently low-weight binary solution determines a satisfying Boolean
assignment.
5.1 Pointwise support sets of a low-weight solution
A support set consists of the ﬁeld values with nonzero indicators at one evaluation point.
Suppose that a binary solution x ∈ FM
2 satisﬁes
Hx = b, wt(x) ≤ 4M 1/200R, R = (ℓ + 1)|P |.
For each τ ∈ Θ and p ∈ P , deﬁne
Sτ (p) = {w ∈ K : xτ,p,w = 1}.
Every nonzero coordinate of x contributes to exactly one set Sτ (p). Therefore
∑
τ ∈Θ
∑
p∈P
|Sτ (p)| = wt(x) ≤ 4M 1/200R.
205
===== PAGE 208 =====
For each table index, retain the evaluation points with bounded support sets:
Pτ := {p ∈ P : |Sτ (p)| ≤ K}, K = N 4.
This restriction aﬀects only the analysis: the aﬃne system and all ordinary-moment, shifted-
moment, and clause constraints remain indexed by the original evaluation set P . Markov’s
inequality bounds the number of discarded evaluation points:
|P \ Pτ | = #{p ∈ P : |Sτ (p)| > K }
≤ 1
K
∑
p∈P
|Sτ (p)|
≤ 4M 1/200R
N 4
≤ 4 · 401/200qN −199/200 < q
20 (N ≥ 100).
Here we used M ≤ 40N 401 and R ≤ N q. In particular, every type retains a large evaluation
set:
|Pτ | > |P | − q
20 (τ ∈ Θ). (13)
The parameter choices also give
|P | − q
20 − N 9 > q/ 2, q/ 2 > 2N 39. (14)
These estimates use |P | = q − m, m ≤ N , and q ≥ N 200. The sets Pτ may diﬀer; no common
retained evaluation set is required.
5.2 Applying the algebraic reconstruction lemma
Fix τ ∈ Θ. The ordinary-moment constraints apply to its support sets on the full evaluation
set. Condition (C3) says that, for every 0 ≤ j ≤ T , the vector

∑
w∈Sτ (p)
wj


p∈P
belongs to RS(P, d j). Consequently there is a unique polynomial
µτ,j (X) ∈ K[X], deg µτ,j ≤ d j,
satisfying
µτ,j (p) =
∑
w∈Sτ (p)
wj (p ∈ P ).
These polynomials come from the original constraints on P . Restricting the evaluation set
does not change them. For each table, deﬁne the family of support sets
Sτ := (Sτ (p))p∈Pτ .
Since Pτ ⊆ P , the same polynomials satisfy
µτ,j (p) =
∑
w∈Sτ (p)
wj (p ∈ Pτ ),
which veriﬁes condition (M2). By the deﬁnition of Pτ ,
|Sτ (p)| ≤ K (p ∈ Pτ ),
206
===== PAGE 209 =====
which veriﬁes condition (M1).
The parameters of Section 3 give
T = N 30 ≥ 2N 4 − 1 = 2 K − 1,
and ( 13) and ( 14) give
|Pτ | − dK(K − 1) > |P | − q
20 − N 9
> q/ 2
> 2N 39
≥ 2dK2T.
In particular,
dT ≤ N 31 < q/ 2 < |Pτ |.
Thus Sτ is a (d, T, K)-bounded polynomial-moment family on Pτ , and it satisﬁes every hy-
pothesis of Lemma 10.
Apply that lemma separately to each Sτ . It gives a separable monic polynomial
Gτ (Y ) ∈ F [Y ], h τ = max
p∈Pτ
|Sτ (p)| = deg Y Gτ ≤ K, F = K(X).
Lemma 3 supplies one ﬁnite separable extension E/F in which all of these polynomials split.
Write
Rτ = {α ∈ E : Gτ (α) = 0 }.
In particular, R0 corresponds to the table indexed by 0, and R(C,β) corresponds to the table
indexed by (C, β). Each root set consists of hτ distinct elements. The ordinary moment
polynomials of the original pointwise sets are exactly the power sums of these roots:
µτ,j (X) =
∑
α∈Rτ
αj (τ ∈ Θ, 0 ≤ j ≤ T ). (15)
The polynomials µτ,j are deﬁned on P ; only the application of Lemma 10 uses Pτ .
The global parity constraint and the zeroth root-moment identity imply the following.
Corollary 11. The root set R0 of the global type is nonempty.
Proof. Condition (C1) gives µ0,0 = 1. Equation ( 15) with j = 0 therefore gives
1 =
∑
α∈R0
1 = |R0| · 1 in K.
Thus |R0| is odd, and in particular R0 ̸= ∅.
5.3 Valuative recovery of local assignments
For the table indexed by τ = ( C, β), the bit βi is speciﬁed for each i ∈ IC. The anchor ai
lies outside P . For roots algebraic over K(X), ﬁx a valuation above X − ai for each variable,
using the same valuation across all clause tables containing that variable.
Lemma 12 (Local valuation extraction) . Let τ = ( C, β), i ∈ IC, and let E/F be the com-
mon ﬁnite separable splitting ﬁeld ﬁxed in the preceding subsection. Fix once and for all an
extension vi of ordX−ai to E. For every α ∈ R τ ,
vi(α − βi) ≥ 1. (16)
207
===== PAGE 210 =====
Proof. Write ℓi = X − ai, set h = hτ , and enumerate the distinct roots as α1, . . . , αh. There
is nothing to prove if h = 0. For h > 0, abbreviate the Hankel determinant of this particular
type by
∆h(X) = det
(
µτ,r+s(X)
)
0≤r,s<h.
Recall from ( 2) that ητ,i,j (X) is the unique polynomial of degree at most (d − 1)j satisfying
ητ,i,j (p) =
∑
w∈Sτ (p)
( w − βi
p − ai
) j
(p ∈ P ).
The pointwise binomial identity and uniqueness of Reed–Solomon interpolation imply, for
0 ≤ j ≤ T ,
ℓj
i ητ,i,j (X) =
j∑
l=0
(
j
l
)
(−βi)j−lµτ,l(X). (17)
Both sides have degree at most d j < |P | and agree on all p ∈ P , so this is an identity in K[X],
not merely an agreement on the sampled grid.
Put
ys = αs − βi
ℓi
.
Combining ( 17) with ( 15) gives
h∑
s=1
yj
s = ητ,i,j (X) (0 ≤ j ≤ T ). (18)
In particular, each displayed power sum has nonnegative vi-valuation.
Write
Gτ (Y ) = Y h +
∑
l<h
clY l, D 0 = dh2 + h.
Lemma 10 gives vi(cl) ≥ −dh2. The ys are the roots of
ℓ−h
i Gτ (ℓiY + βi) = Y h +
∑
l<h
blY l,
where bh = 1 and, for 0 ≤ l < h ,
bl = ℓl−h
i
[(
h
l
)
βh−l
i +
h−1∑
k′=l
ck′
(
k′
l
)
βk′−l
i
]
, v i(bl) ≥ −D0.
If ys = 0, then vi(ys) = + ∞, and the desired conclusion already holds for that root. Otherwise
write ts = vi(ys) ∈ Q. Since vi(bl) ≥ −D0 for l < h , the monic equation implies
ts ≥ −D0. (19)
Indeed, if ts < −D0, then yh
s would be the unique minimum-valuation term of the equation.
If ts < 0, the minimum of
vi(bl) + lts (0 ≤ l ≤ h, b l ̸= 0)
must be attained by at least two indices. Thus there exist 0 ≤ l < k ′ ≤ h with bl, bk′ ∈ F ×
and
(k′ − l)ts = vi(bl) − vi(bk′) ∈ Z.
Consequently
ts < 0 = ⇒ ts ≤ −1/h. (20)
208
===== PAGE 211 =====
Let V = (yj
s)0≤j<h, 1≤s≤h. By ( 8),
(det V )2 = ℓ−h(h−1)
i ∆h.
Since ∆h ∈ K[X] \ {0},
0 ≤ vi(∆h) = ord X−ai(∆h) ≤ deg ∆h ≤ dh(h − 1).
Thus V is invertible and
2vi(det V ) = vi(∆h) − h(h − 1), v i(det V ) ≤ 1
2 (d − 1)h(h − 1) ≤ dh2.
By ( 19), each entry of V has valuation at least −hD0, and every cofactor has valuation at
least −h2D0. Therefore
vi
(
(V −1)s,j
)
≥ −Uh, U h = h2D0 + dh2 + 1 ≤ 4N 17. (21)
Choose
z = hUh + 1.
The required moments exist since
z + h − 1 ≤ 5N 21 < T = N 30.
Equation ( 18) gives
V


yz
1
...
yz
h

=


ητ,i,z
ητ,i,z +1
...
ητ,i,z +h−1


.
The right-hand vector has nonnegative valuation. By ( 21),
vi(yz
s ) ≥ −Uh (1 ≤ s ≤ h).
If ts < 0, however, ( 20) gives
vi(yz
s ) = zts ≤ − hUh + 1
h < −Uh,
a contradiction. Therefore vi(ys) ≥ 0 for every root, which is precisely ( 16).
5.4 Clause matching
For each clause C, the sets R(C,β) indexed by β ∈ B C are called its clause subtype root
sets. The clause constraint expresses every indicator of the table indexed by 0 as the sum
modulo two of the corresponding indicators of the tables indexed by (C, β). Together with
the root-moment identities, this gives the following matching property.
Lemma 13 (Parity matching of clause roots) . For each clause C, every α ∈ R 0 belongs to
R(C,β) for at least one β ∈ B C.
Proof. The pointwise clause constraint and Reed–Solomon interpolation give, for 0 ≤ j ≤ T ,
µ0,j(X) =
∑
β∈BC
µ(C,β),j(X).
209
===== PAGE 212 =====
Substitute the reconstructed moments from ( 15) and move the right-hand side to the left.
Since char K = 2, ∑
α∈R0
αj +
∑
β∈BC
∑
α∈R(C,β)
αj = 0.
Let WC be the set of distinct roots occurring an odd number of times in these sets. Then
∑
α∈WC
αj = 0 (0 ≤ j ≤ T ), |WC| ≤ (1 + |BC|)K ≤ 9K < T + 1.
If WC ̸= ∅, the ﬁrst |WC| equations form an invertible Vandermonde matrix applied to the
all-ones vector, an impossibility. Thus WC = ∅. A root appearing once in R0 must therefore
occur at least once among the clause subtype root sets.
5.5 Completing the soundness proof
Fix α ∈ R 0. For each clause C, this element belongs to some R(C,β); the resulting satisfying
assignments agree on shared variables.
Proposition 14 (Binary nearest-codeword soundness) . If the aﬃne system (3) has a binary
solution x satisfying
wt(x) ≤ 4M 1/200R, R = (ℓ + 1)|P |,
then φ is satisﬁable.
Proof. Fix such a binary solution. As veriﬁed above, its restricted support families satisfy
Deﬁnition 9 and the numerical hypotheses of Lemma 10. Apply the reconstruction lemma
separately to each family and take the common splitting ﬁeld E. By Corollary 11, choose one
α ∈ R 0. For every clause C, Lemma 13 supplies a satisfying local tuple β(C) with
α ∈ R (C,β(C)).
Fix an index i appearing in two clauses C, C′. Apply the same valuation vi on the common
splitting ﬁeld in both applications of Lemma 12. This gives
vi
(
α − β(C)i
)
≥ 1, v i
(
α − β(C′)i
)
≥ 1.
If the two bits diﬀered, the ultrametric inequality would imply
vi(1) = vi
(
β(C)i − β(C′)i
)
≥ 1,
contradicting vi(1) = 0 . All locally selected tuples therefore agree on shared variables. Since
unused variables were discarded, they assemble into one global Boolean assignment; each
clause is satisﬁed by construction.
Together with Lemma 8, this soundness implication completes the binary nearest-codeword
gap:
φ satisﬁable =⇒ W (H, b) ≤ R,
and, whenever Hx = b is consistent,
φ unsatisﬁable =⇒ W (H, b) > 4M 1/200R.
It remains to transfer this binary gap to CVP using Lemma 7.
210
===== PAGE 213 =====
6 Transfer to CVP and complexity
First handle the formula-preprocessing cases from the start of the construction. If no clauses
remain, return (B, t, r) = ((1) , (0), 1), a one-dimensional YES instance. If an empty clause
remains, return
B = (2), t = (1), r = 1
2 .
This one-dimensional instance has distance 1, hence is a strict NO instance because 1cr = 1/2.
For every other formula, construct the explicit aﬃne system ( 3). Gaussian elimination
over F2 tests whether the aﬃne system is consistent; it does not decide whether the input
formula is satisﬁable.
If the aﬃne system is inconsistent, return the same one-dimensional NO instance. By
Lemma 8, inconsistency cannot occur for a satisﬁable formula.
On the consistent branch, ﬁnd any u ∈ {0, 1}M solving Hu = b. The parity-lift lattice has
the square basis ( 1), with the inverse coordinate permutation restoring the original order. Its
squared distance to this target equals the minimum binary weight. Output
(B, t, r) =
(
BH , u, ⌈
√
(ℓ + 1)|P |⌉
)
.
On this branch its dimension is n = M , its basis is nonsingular, and its target and radius are
binary-encoded integers. Furthermore,
dist2(u, L(BH )) = min
v∈u−ΛH
∥v∥2.
For a satisﬁable formula, Lemmas 8 and 7 give
dist2(u, L(BH )) ≤
√
R ≤ r.
For an unsatisﬁable formula, suppose for contradiction that
dist2(u, L(BH )) ≤ M cr.
Since c = 1/400, Lemma 7 gives
W (H, b) = dist 2(u, L(BH ))2 ≤ M 1/200r2 ≤ 4M 1/200R,
where r = ⌈
√
R⌉ implies r2 ≤ 4R. Proposition 14 would then make φ satisﬁable, a contradic-
tion. Therefore
dist2(u, L(BH )) > M cr.
The inequality is strict, as required by the promise deﬁnition.
The ﬁnite ﬁeld has extension degree e = O(log N ), and its deterministic construction
uses N O(1) bit operations. Equations ( 4) and ( 5) bound both dimensions of H by O(N 401).
Consequently, the dense binary system and the square output basis each have O(N 802) bits.
Field arithmetic, Reed–Solomon parity checks, consistency testing, and basis construction are
deterministic polynomial-time operations.
7 Further consequences
The same binary aﬃne gap gives coding-theoretic and ﬁxed-ﬁnite-norm consequences. In each
statement, n denotes the output block length or lattice rank.
Recall the binary nearest-codeword and syndrome-decoding promise problems deﬁned in
Section 1.1.
211
===== PAGE 214 =====
Corollary 15 (Hardness of binary nearest codeword and syndrome decoding) . Binary nearest
codeword and binary syndrome decoding are NP-hard to approximate within n1/200 under
deterministic polynomial-time many-one reductions.
Proof. First suppose that ( 3) is consistent, compute a binary solution u, and put
C = kerF2 H, d H (u, C) = min {wt(x) : x ∈ Fn
2 , Hx = b}.
Use the integer radius R = ( ℓ + 1)|P |. Completeness follows directly from Lemma 8. Con-
versely, if a binary solution satisﬁes
wt(x) ≤ n1/200R,
then, since n = M , it also satisﬁes
wt(x) ≤ 4M 1/200R.
Proposition 14 therefore implies that φ is satisﬁable. Consequently an unsatisﬁable formula
gives the strict NO promise
dH (u, C) > n 1/200R.
Gaussian elimination computes either a generator for C or an independent parity-check matrix,
with at most O(n2) output bits. For an inconsistent aﬃne system, output the ﬁxed binary
code {00}, target 11, and radius 1: its distance 2 is strictly greater than 21/200. By Lemma 8,
this branch is never reached by a satisﬁable formula. The same system and radius give the
equivalent syndrome-decoding formulation.
For a ﬁxed rational p ≥ 1, deﬁne
distp(t, L) = min
z∈L
∥t − z∥p.
The norm parameter p is ﬁxed independently of the input; the lattice basis, target, and
threshold constitute the promise instance.
For a parity-lift lattice, raising this distance to the norm exponent gives the minimum
binary Hamming weight.
Corollary 16 (Hardness for ﬁxed ﬁnite rational norms) . Fix a rational p ≥ 1. There is a
deterministic polynomial-time many-one reduction from 3SAT to the full-rank ℓp closest-vector
promise problem with approximation factor
n1/(200p).
The lattice basis is square and integral, and the target and radius have polynomial-size exact
rational encodings.
Proof. Write p = a/b in lowest terms and set the ﬁxed integer A = ⌈4p⌉. For R = (ℓ + 1)|P |,
compute
jp = min{j ∈ Z≥0 : ja ≥ AaRb}, r p = jp
A .
Fixed-degree integer exponentiation and binary search compute this radius in deterministic
polynomial time. Moreover,
R1/p ≤ rp ≤ (1 + 1/A)R1/p, r p
p ≤ ep/AR ≤ e1/4R < 2R.
212
===== PAGE 215 =====
For a consistent system, apply Lemma 7 to obtain the same integral square basis BH and
binary target u, now equipped with the ℓp norm and radius rp. If φ is satisﬁable, completeness
and the exact ℓp distance identity give
distp(u, L(BH ))p = W (H, b) ≤ R ≤ rp
p.
For soundness, suppose that
distp(u, L(BH )) ≤ n1/(200p)rp.
Lemma 7 then yields
W (H, b) = dist p(u, L(BH ))p ≤ n1/200rp
p < 2n1/200R ≤ 4n1/200R.
Since n = M , Proposition 14 would imply that φ is satisﬁable. Thus an unsatisﬁable input
satisﬁes the strict promise
distp(u, L(BH )) > n 1/(200p)rp.
On an inconsistent system, the one-dimensional ﬁxed output (B, t, r) = ((2) , (1), 1/2) has ℓp
distance 1 > 1/2 for every ﬁnite p, and is a strict NO instance.
References
[AGMZ26] D. Aggarwal, R. Gupta, A. Morolia, and C. Zhang. Mind the gap? Not for
SVP hardness under ETH! In 53rd International Colloquium on Automata,
Languages, and Programming , volume 374 of Leibniz International Proceedings
in Informatics , pages 8:1–8:24, 2026. doi:10.4230/LIPIcs.ICALP.2026.8.
[AR05] D. Aharonov and O. Regev. Lattice problems in NP ∩ coNP. Journal of the
ACM, 52(5):749–765, 2005. doi:10.1145/1089023.1089025.
[Ajt96] M. Ajtai. Generating hard instances of lattice problems. In Proceedings of the
Twenty-Eighth Annual ACM Symposium on Theory of Computing , pages
99–108, 1996. doi:10.1145/237814.237838.
[AKKV11] M. Alekhnovich, S. Khot, G. Kindler, and N. K. Vishnoi. Hardness of
approximating the closest vector problem with pre-processing. Computational
Complexity, 20(4):741–753, 2011. doi:10.1007/s00037-011-0031-3.
[ALRS98] S. Ar, R. J. Lipton, R. Rubinfeld, and M. Sudan. Reconstructing algebraic
functions from mixed data. SIAM Journal on Computing , 28(2):487–510, 1998.
doi:10.1137/S0097539796297577.
[ABSS97] S. Arora, L. Babai, J. Stern, and Z. Sweedyk. The hardness of approximate
optima in lattices, codes, and systems of linear equations. Journal of Computer
and System Sciences , 54(2):317–331, 1997. doi:10.1006/jcss.1997.1472.
[Bab86] L. Babai. On Lovász’ lattice reduction and the nearest lattice point problem.
Combinatorica, 6(1):1–13, 1986. doi:10.1007/BF02579403.
[BP23] H. Bennett and C. Peikert. Hardness of the (approximate) shortest vector
problem: A simple proof via Reed–Solomon codes. In Approximation,
Randomization, and Combinatorial Optimization. Algorithms and Techniques
(APPROX/RANDOM 2023) , volume 275 of Leibniz International Proceedings
in Informatics , pages 37:1–37:20, 2023.
doi:10.4230/LIPIcs.APPROX/RANDOM.2023.37.
213
===== PAGE 216 =====
[BMVT78] E. R. Berlekamp, R. J. McEliece, and H. C. A. van Tilborg. On the inherent
intractability of certain coding problems. IEEE Transactions on Information
Theory, 24(3):384–386, 1978. doi:10.1109/TIT.1978.1055873.
[BGLR25] V. Bhattiprolu, V. Guruswami, E. Lee, and X. Ren. Inapproximability of
ﬁnding sparse vectors in codes, subspaces, and lattices. In Proceedings of the
66th IEEE Annual Symposium on Foundations of Computer Science , pages
1295–1303, 2025. doi:10.1109/FOCS63196.2025.00068.
[BGR25] V. Bhattiprolu, V. Guruswami, and X. Ren. PCP-free APX-hardness of
nearest codeword and minimum distance. Electronic Colloquium on
Computational Complexity , Report TR25-029, 2025.
https://eccc.weizmann.ac.il/report/2025/029/. Subsequently incorporated
into [ BGLR25].
[DKRS03] I. Dinur, G. Kindler, R. Raz, and S. Safra. Approximating CVP to within
almost-polynomial factors is NP-hard. Combinatorica, 23(2):205–243, 2003.
doi:10.1007/s00493-003-0019-y.
[DKS98] I. Dinur, G. Kindler, and S. Safra. Approximating-CVP to within
almost-polynomial factors is NP-hard. In Proceedings of the 39th Annual
Symposium on Foundations of Computer Science , pages 99–111, 1998.
doi:10.1109/SFCS.1998.743433.
[FM04] U. Feige and D. Micciancio. The inapproximability of lattice and coding
problems with preprocessing. J. Comput. Syst. Sci. , 69(1):45–67, 2004.
doi:10.1016/j.jcss.2004.01.002.
[GGG18] V. Gandikota, B. Ghazi, and E. Grigorescu. NP-hardness of Reed–Solomon
decoding, and the Prouhet–Tarry–Escott problem. SIAM Journal on
Computing, 47(4):1547–1584, 2018. doi:10.1137/16M110349X.
[GST23] E. Goldberg, C. Shangguan, and I. Tamo. List-decoding and list-recovery of
Reed–Solomon codes beyond the Johnson radius for every rate. IEEE
Transactions on Information Theory , 69(4):2261–2268, 2023.
doi:10.1109/TIT.2022.3222877.
[GG00] O. Goldreich and S. Goldwasser. On the limits of nonapproximability of lattice
problems. Journal of Computer and System Sciences , 60(3):540–563, 2000.
doi:10.1006/jcss.1999.1686.
[GGH97] O. Goldreich, S. Goldwasser, and S. Halevi. Public-key cryptosystems from
lattice reduction problems. In Advances in Cryptology—CRYPTO ’97 , volume
1294 of Lecture Notes in Computer Science , pages 112–131. Springer, 1997.
doi:10.1007/BFb0052231.
[GLSTW24] Z. Guo, R. Li, C. Shangguan, I. Tamo, and M. Wootters. Improved
list-decodability and list-recoverability of Reed–Solomon codes via tree
packings. SIAM Journal on Computing , 53(2):389–430, 2024.
doi:10.1137/21M1463707.
[GR06] V. Guruswami and A. Rudra. Limits to list decoding Reed–Solomon codes.
IEEE Transactions on Information Theory , 52(8):3642–3649, 2006.
doi:10.1109/TIT.2006.878164.
214
===== PAGE 217 =====
[GS99] V. Guruswami and M. Sudan. Improved decoding of Reed–Solomon and
algebraic-geometry codes. IEEE Transactions on Information Theory ,
45(6):1757–1767, 1999. doi:10.1109/18.782097.
[HKW26] J. A. Huang, Y. K. Ko, and C. Wang. On the (classical and quantum)
ﬁne-grained complexity of approximate CVP and max-cut. In 53rd
International Colloquium on Automata, Languages, and Programming , volume
374 of Leibniz International Proceedings in Informatics , pages 111:1–111:17,
2026. doi:10.4230/LIPIcs.ICALP.2026.111.
[LS71] J. Leech and N. J. A. Sloane. Sphere packings and error-correcting codes.
Canadian Journal of Mathematics , 23(4):718–745, 1971.
doi:10.4153/CJM-1971-081-3.
[LLL82] A. K. Lenstra, H. W. Lenstra, Jr., and L. Lovász. Factoring polynomials with
rational coeﬃcients. Mathematische Annalen , 261(4):515–534, 1982.
doi:10.1007/BF01457454.
[LS25] R. Li and N. Shagrithaya. Near-optimal list-recovery of linear code families. In
Approximation, Randomization, and Combinatorial Optimization. Algorithms
and Techniques (APPROX/RANDOM 2025) , volume 353 of Leibniz
International Proceedings in Informatics , pages 53:1–53:14, 2025.
doi:10.4230/LIPIcs.APPROX/RANDOM.2025.53.
[Mas69] J. L. Massey. Shift-register synthesis and BCH decoding. IEEE Transactions
on Information Theory , 15(1):122–127, 1969. doi:10.1109/TIT.1969.1054260.
[Mos15] D. Moshkovitz. The projection games conjecture and the NP-hardness of
ln n-approximating set-cover. Theory of Computing , 11(7):221–235, 2015.
doi:10.4086/toc.2015.v011a007. See Section 5.1.
[Muk22] P. Mukhopadhyay. The projection games conjecture and the hardness of
approximation of super-SAT and related problems. Journal of Computer and
System Sciences , 123:186–201, 2022. doi:10.1016/j.jcss.2021.09.002.
[NIST24a] National Institute of Standards and Technology. Module-lattice-based
key-encapsulation mechanism standard. Federal Information Processing
Standards Publication 203 , 2024. doi:10.6028/NIST.FIPS.203.
[NIST24b] National Institute of Standards and Technology. Module-lattice-based digital
signature standard. Federal Information Processing Standards Publication 204 ,
2024. doi:10.6028/NIST.FIPS.204.
[RS60] I. S. Reed and G. Solomon. Polynomial codes over certain ﬁnite ﬁelds. Journal
of the Society for Industrial and Applied Mathematics , 8(2):300–304, 1960.
doi:10.1137/0108018.
[Reg04] O. Regev. Improved inapproximability of lattice and coding problems with
preprocessing. IEEE Transactions on Information Theory , 50(9):2031–2037,
2004. doi:10.1109/TIT.2004.833350.
[Reg09] O. Regev. On lattices, learning with errors, random linear codes, and
cryptography. Journal of the ACM , 56(6):34:1–34:40, 2009.
doi:10.1145/1568318.1568324.
215
===== PAGE 218 =====
[RR00] R. M. Roth and G. Ruckenstein. Eﬃcient decoding of Reed–Solomon codes
beyond half the minimum distance. IEEE Transactions on Information
Theory, 46(1):246–257, 2000. doi:10.1109/18.817522.
[Sud97] M. Sudan. Decoding of Reed Solomon codes beyond the error-correction bound.
Journal of Complexity , 13(1):180–193, 1997. doi:10.1006/jcom.1997.0439.
[vEB81] P. van Emde Boas. Another NP-complete partition problem and the
complexity of computing short vectors in a lattice. Technical Report
MI-UvA-81-04, Mathematical Institute, University of Amsterdam, 1981.
https://staﬀ.fnwi.uva.nl/p.vanemdeboas/vectors/mi8104c.html.
[Var97] A. Vardy. The intractability of computing the minimum distance of a code.
IEEE Transactions on Information Theory , 43(6):1757–1766, 1997.
doi:10.1109/18.641542.
[ZGA11] A. Zeh, C. Gentner, and D. Augot. An interpolation procedure for list decoding
Reed–Solomon codes based on generalized key equations. IEEE Transactions
on Information Theory , 57(9):5946–5959, 2011. doi:10.1109/TIT.2011.2162160.
216
===== PAGE 219 =====
Chapter 8
The Sharp Inequality in Ehrhart’s Volume
Conjecture
Abstract. We prove the sharp bound that an n-dimensional convex body
whose barycenter is its unique interior lattice point has volume at most (n +
1)n/n!.
Contents
1. Introduction
2. The real potential and lattice Bergman spaces
3. Vanishing orders and the lower slope
4. Bergman convexity and the upper slope
References
217
===== PAGE 220 =====
1. Introduction
Ehrhart asked whether, among convex bodies whose barycenter is their only interior lattice
point, the centered simplex maximizes volume [ Ehr64]. Let ∆n = conv{0,e 1,...,e n} and write
vol for ordinary Euclidean volume. The precise inequality is the following.
Theorem 1.1. Let K ⊂ Rn be a full-dimensional compact convex body with barycenter 0. If
int(K) ∩ Zn = {0}, then
vol(K) ≤ (n + 1)n
n! . (1)
The bound is sharp: the simplex (n + 1)∆n − (1,..., 1) has barycenter 0, contains no other
interior lattice point, and has volume (n + 1)n/n!. The equality reﬁnement predicts that every
extremizer is a unimodular image of this simplex under an integer linear map of determinant
± 1 [NP14, Conj. 1.1]. We do not determine whether these are the only equality cases.
Previous work. Ehrhart proved the conjecture for planar convex bodies and for simplices in
every dimension [ Ehr55, Ehr79]. For arbitrary centered bodies, Milman–Pajor symmetrization
and Minkowski’s theorem give vol(K) ≤ 4n, as observed by Henk, Henze, and Hernández
Cifre [MP00, HHH16]. Using thin-shell estimates, Huang, Slomka, Tkocz, and Vritsiou improved
this to vol(K) ≤ 4ne−c√n for a universal c > 0 [HSTV22, Prop. 6.2]. Campos, van Hintum,
Morris, and Tiba subsequently obtained vol(K) ≤ 4n exp(−cn/(logn)8) using bounds for the
isotropic constant [ CHMT24]. Combining their argument with Klartag and Lehec’s solution of
Bourgain’s slicing problem gives vol(K) ≤ 4ne−cn for a universal c> 0 [CHMT24, KL25].
The conjecture is also known for certain classes of convex bodies. Berman and Berndtsson
connect the sharp bound with the anticanonical volume of Kähler–Einstein toric varieties [ BB17].
Their analytic argument combines Bergman convexity and a Moser–Trudinger inequality with
a Green function at a torus-ﬁxed point. In particular, it proves the conjecture for centered
rational polytopes with facet presentation
P =
{
y : ⟨ℓF,y ⟩ ≥ −aF for every facet F
}
, ℓ F ∈ Zn, 0<a F ≤ 1,
where eachℓF is primitive, meaning that its coordinates have no common factor [ BB17, Cor. 1.4].
They also establish the sharp bound for bodies in the positive orthant with barycenter (1,..., 1)
and record Klartag’s direct derivation from Grünbaum’s barycentric half-space inequality [ BB17,
Thm. 1.5 and Rem. 3.2]; see [ Gru60]. The displayed facet conditions also give an aﬃne reduction
to the orthant case. Write
Q∗ = {u : ⟨u,y ⟩ ≤ 1 for every y ∈Q}
for the polar of a convex body Q containing 0. Nill and Paﬀenholz extend this argument to
convex bodies in the polar of a lattice polytope and classify the equality cases [ NP14, Thm. 1.4].
Their hypothesis does not cover every centered rational polytope with unique interior lattice
point 0: they give the example
P0 = conv
{
± (3/2, 1/4), ± (3/2, 5/4)
}
, P ∗
0 ∩ Z2 = {0, ± (1, − 2)},
so P ∗
0 contains no full-dimensional lattice polygon.
Idea of the proof. By a theorem of Berman and Berndtsson [ BB13, Thm. 1.1], there is a
smooth convex potential ϕ whose gradient transports e−ϕ(x)dx to Lebesgue measure on K;
Cordero-Erausquin and Klartag also studied this transport problem [ CK15]. On X = ( C∗)n,
regard ϕ as a function of the logarithmic radii:
ϕ(z) = ϕ
(
log |z1|2,..., log |zn|2)
.
Let dν = dxdθ , where xi = log |zi|2 and dθ is normalized angular measure. The space Hk
of holomorphic functions on X that are square-integrable with weight e−kϕdν has Laurent
monomial basis
Hk = span{zm :m ∈ Zn ∩ int(kK )}, dim Hk = #(Zn ∩ int(kK )).
The unique-interior-lattice-point hypothesis is therefore exactly the assertion H1 = C.
218
===== PAGE 221 =====
At higher levels, ﬁx p = (1,..., 1). Every monomial equals 1 at p, so choose an orthonormal
basis (sa) adapted to vanishing order at p. Vanishing to order j forces all Taylor coeﬃcients
of degree less than j to vanish, imposing at most
( n+j− 1
n
)
linear conditions. Write qa for the
order of sa, truncated at cKk, where cK = (n! vol(K))1/n, and form the ﬁnite-level potentials
uk
t =k− 1 log∑
a |sa|2etqa. Their regularized limit is a ray of potentials , a one-parameter family
(ψt)t≥ 0 with ψ0 =ϕ and bounded ψt − ϕ for each t.
Introduce the normalized partition function and its logarithm:
Z(t) = 1
vol(K)
∫
X
e−ψtdν, L (t) = − logZ(t).
Since H1 = C, the weighted holomorphic space associated with ψt still consists only of constants,
so its Bergman kernel equals 1/(vol(K)Z(t)). Berndtsson’s positivity theorem makes L con-
vex [ Ber06], as in the one-dimensional Bergman mechanism of Berman and Berndtsson [ BB17,
Thm. 2.3]. Counting the vanishing conditions gives the lower bound on its initial slope. A
separate local Schwarz estimate uses the decay of functions vanishing at p to bound ψt from
above on a ball of radius proportional to e−t/2; the volume of that ball gives the upper bound.
Together, these arguments yield
n
n + 1cK ≤ L′
+(0) ≤ n. (2)
Their comparison gives cK ≤ n + 1, proving ( 1).
Fujita previously used the same point ﬁltration and vanishing-order count to obtain a sharp
volume bound in Fano geometry [ Fuj18, Thms. 2.3 and 5.1]. Related constructions include
ﬁltrations of Laurent polynomials in graded Ehrhart theory [ RR24, Cav26], toric and ﬁltered
Bergman kernels [ Zel09, PS14], and rays from ﬁltered linear series [ BC11, R W14].
2. The real potential and lattice Bergman spaces
We ﬁrst construct the transport potential, identify lattice points with an orthogonal basis
of holomorphic monomials, and establish the convergence needed to pass from those ﬁnite-
dimensional spaces to a limiting potential.
Let hK(x) = sup y∈K⟨y,x ⟩ be the support function of K. Since its barycenter is 0, the
existence theorem of Berman and Berndtsson [ BB13, Thm. 1.1] gives a smooth strictly convex
potentialϕ : Rn → R whose gradient transports its associated log-concave measure to Lebesgue
measure on K:
(∇ϕ)#
(
e−ϕ(x)dx
)
= 1K(y)dy, |ϕ(x) − hK(x)| ≤C. (3)
Moreover, ∇ϕ is a diﬀeomorphism onto int(K), so the transport identity is equivalent to
∇ϕ(Rn) = int(K), detD2ϕ =e−ϕ.
In particular, the transported measure has exactly the volume of K:∫
Rn
e−ϕ(x)dx =
∫
Rn
detD2ϕ(x)dx = vol(K). (4)
To expose the lattice, attach independent angular coordinates to the original real variables.
Writedθ for the Haar probability measure on (S1)n, so that
X = (C∗)n, z i =exi/2+iθi, dν =dxdθ.
Letdλ denote Euclidean Lebesgue measure on Cn. The change to logarithmic coordinates gives
dν(z) = π−n
n∏
i=1
|zi|− 2dλ(z). (5)
Here x ∈ Rn is unrestricted; in particular, the |zi|need not be bounded or bounded away from
0. Whenever ϕ is evaluated on X, it denotes the pullback
ϕ(z) = ϕ
(
log |z1|2,..., log |zn|2)
.
219
===== PAGE 222 =====
Since the angular variables have total mass one, ( 4) becomes
∫
X
e−ϕdν = vol(K), dµ = e−ϕ
vol(K)dν. (6)
Write O(X) for the space of holomorphic functions on X. For any real weight b on X, its
weighted holomorphic space and Bergman kernel are
H(b) =
{
f ∈ O (X) :
∫
X
|f |2e−bdν <∞
}
,
Bb(z) = sup
f ∈H(b)\{0}
|f (z)|2
∫
X
|f |2e−bdν
.
(7)
Fork ≥ 1, specialize to b =kϕ:
Hk = H(kϕ), ∥s∥2
k =
∫
X
|s|2e−kϕdν.
The point of the complex torus is that its holomorphic Laurent monomials are indexed by Zn.
By ( 3), zm has ﬁnite weighted norm exactly when m/k ∈ int(K): only then does its integrand
decay exponentially in every direction. Since K is bounded, there are only ﬁnitely many such
exponents.
Lemma 2.1. The monomials zm, with m ∈ Zn ∩ int(kK ), form an orthogonal basis of Hk. In
particular, Hk is ﬁnite-dimensional; writing dk = dim Hk, one has
dk = #
(
Zn ∩ int(kK )
)
, dk
kn − → vol(K), H1 = C. (8)
More generally, H(b) = C whenever b − ϕ is bounded on X.
Proof. Foru =m/k, integration over θ ∈ (S1)n gives
∥zm∥2
k =Ik(u) :=
∫
Rn
ek(⟨u,x⟩−ϕ(x))dx. (9)
If u ∈ int(K), there is δ >0 for which hK(x) − ⟨u,x ⟩ ≥ δ|x|. Thus ( 3) implies Ik(u) < ∞ . If
u /∈ int(K), take a supporting direction v ̸= 0 with ⟨u,v ⟩ ≥ hK(v). On a tube of ﬁxed radius
about the ray R≥ 0v, ⟨u,x ⟩ −ϕ(x) is bounded below, so Ik(u) = ∞ . For the Laurent expansion
s =∑
m∈Zncmzm, Parseval’s identity for the integral over θ and Tonelli’s theorem give
∥s∥2
k =
∑
m∈Zn
|cm|2Ik(m/k),
with zero terms omitted. Hence an integrable s has nonzero coeﬃcients only for m ∈ Zn ∩
int(kK ). This set is ﬁnite because K is bounded, proving both the basis statement and ﬁnite-
dimensionality. The lattice-counting limit follows from the fact that ∂K has measure zero. At
k = 1 , the only admissible exponent is 0. Finally, a bounded change of weight does not aﬀect
integrability, so H(b) = H(ϕ) = C wheneverb − ϕ is bounded. □
We next approximate the probability measure dµ = e−ϕdν/ vol(K) using the lattice mono-
mials. By Lemma 2.1 and ( 9), an orthonormal basis of Hk is given explicitly by
sm(z) = zm
√
Ik(m/k), m ∈ Zn ∩ int(kK ).
Deﬁne the Bergman kernel Bk and the associated probability measure µk by
Bk(z) = Bkϕ(z) =
∑
m∈Zn∩int(kK)
|sm(z)|2 =
∑
m∈Zn∩int(kK)
|zm|2
Ik(m/k),
dµk = Bke−kϕ
dk
dν.
(10)
The kernel Bk is independent of the orthonormal basis, so we may later replace the monomials
by a basis adapted to vanishing at a point without changing Bk orµk. The next lemma supplies
220
===== PAGE 223 =====
the two convergence statements needed for the limiting construction. The logarithmic kernels
recoverϕ, so the limiting deformation starts at the original transport potential; convergence of
µk in total variation transfers averaged vanishing orders to the limiting measure µ. All limits
in the next lemma are as k → ∞ , and ok(1) denotes an error tending to zero in that limit.
Whenever uniformity is asserted, it is on the speciﬁed compact set.
Lemma 2.2. There exists C >0 such that, for every k ≥ 2 and every z ∈X,
1
k logBk(z) ≤ ϕ(z) +C logk
k . (11)
Moreover, as k → ∞ ,
1
k logBk − → ϕ locally uniformly on X, ∥µk − µ∥TV − → 0.
Proof. PutA = maxy∈K |y|. Since ∇ϕ(Rn) ⊂ K, the function ϕ isA-Lipschitz on all of Rn. For
x ∈ Rn, u ∈K, and |v − x|< 1/k, it follows that
⟨u,v ⟩ −ϕ(v) ≥ ⟨u,x ⟩ −ϕ(x) − 2A
k .
Integrating ( 9) over this real ball gives
Ik(u) ≥ ωnk−nek(⟨u,x⟩−ϕ(x))− 2A,
where ωn is the volume of the unit ball in Rn. For z ∈X with xi = log |zi|2 and u =m/k, we
have |zm|2 =ek⟨u,x⟩. Therefore ( 10) gives
Bk(z) ≤ e2A
ωn
kndkekϕ(z) ≤ Ck 2nekϕ(z),
where the last inequality follows from dk/kn → vol(K). Taking logarithms proves ( 11).
To obtain both remaining conclusions from a single estimate, introduce the unnormalized
densities
ρk =k−nBke−kϕ, ρ =e−ϕ, ρ kdν = dk
kndµk, ρdν = vol(K)dµ.
If x = (log |z1|2,..., log |zn|2), the monomial formula ( 10) gives
ρk(x) = 1
kn
∑
m∈Zn∩int(kK)
ek(⟨m/k,x⟩−ϕ(x))
Ik(m/k) .
For ﬁxed x, the summands with m/k within O(k− 1/2) of ∇ϕ(x) already suﬃce for both
convergence statements. We approximate those summands by a Gaussian.
WriteH =D2ϕ and deﬁne the Legendre transform
ϕ∗(u) = sup
x∈Rn
(
⟨u,x ⟩ −ϕ(x)
)
.
Foru ∈ int(K), the exponent in ( 9) has its unique maximum at xu = (∇ϕ)− 1(u), with Hessian
−H(xu). The multivariate Laplace estimate therefore gives
Ik(u) = ekϕ∗(u) (2π/k)n/2
√
detH(xu) (1 +ok(1)). (12)
The error is uniform on every compact S ⊂ int(K). Indeed, with δS = dist(S,∂K )> 0,
hK(x) − ⟨u,x ⟩ ≥δS|x| (u ∈S).
Together with ( 3), this controls the tails uniformly; the xu remain in a compact set where D2ϕ
is uniformly positive deﬁnite.
Fix R > 0, put y = ∇ϕ(x), and retain only the monomials with |m/k − y| ≤ R/
√
k. For
u =m/k and q =
√
k(u − y), Taylor’s formula gives
k
(
ϕ∗(u) +ϕ(x) − ⟨u,x ⟩
)
= 1
2 ⟨H(x)− 1q,q ⟩+ok(1),
221
===== PAGE 224 =====
uniformly for |q| ≤ R and x in any ﬁxed compact subset of Rn. Substituting ( 12) into the
monomial sum for ρk now gives a Gaussian Riemann sum:
ρk(x) ≥ FR(x) +ok(1),
FR(x) =
√
detH(x)
(2π)n/2
∫
|q|≤R
e−⟨H(x)− 1q,q⟩/2dq, (13)
again locally uniformly in x.
This one estimate gives both desired limits. On any compact Q ⊂ Rn, FR has a strictly
positive minimum. Together with the global upper bound already proved, this gives constants
bQ,C > 0 such that
bQ ≤ ρk(x) ≤ Ckn (x ∈Q, k suﬃciently large ).
Consequently,
1
k logBk(z) − ϕ(z) = n logk + logρk(x)
k − − − →
k→∞
0
uniformly for x ∈Q, proving local uniform convergence.
For the measures, let R → ∞ in ( 13). The full Gaussian integral equals (2π)n/2√
detH(x),
so detH =e−ϕ gives
lim inf
k→∞
ρk(x) ≥ detH(x) = ρ(x).
On the other hand, ( 8) and ( 6) give the exact mass limit
∫
X
ρkdν = dk
kn − − − →
k→∞
vol(K) =
∫
X
ρdν. (14)
Since 0 ≤ min(ρk,ρ ) ≤ ρ and min(ρk,ρ ) → ρ pointwise, dominated convergence and ( 14) give
∥ρk − ρ∥L1(dν) =
∫
X
ρkdν +
∫
X
ρdν − 2
∫
X
min(ρk,ρ )dν − − − →
k→∞
0.
Since dk/kn → vol(K) as k → ∞ , normalizing these densities proves ∥µk − µ∥TV → 0. □
3. V anishing orders and the lower slope
We ﬁrst count the vanishing orders forced by the dimensions of Hk. We then realize that
count as the initial slope of a limiting family of potentials.
Fix p = (1,..., 1) ∈X. For a nonzero holomorphic function s, expand around p as
s(p +ζ) =
∑
α∈Zn
≥ 0
cαζα, ordp(s) = min
{
|α|:cα ̸= 0
}
, |α|=α1 + · · ·+αn.
Thus ordp(s) ≥ j means that all Taylor coeﬃcients of total degree less than j vanish; set
ordp(0) = ∞ . Filter Hk by these conditions:
Fj
k = {s ∈ Hk : ordp(s) ≥ j}, Hk =F 0
k ⊇ F 1
k ⊇ F 2
k ⊇ · · ·.
The number of Taylor coeﬃcients of degree less than j controls the codimension of Fj
k .
Lemma 3.1. For every j,k ≥ 1,
dk − dimFj
k ≤
(
n +j − 1
n
)
. (15)
Proof. Taking the Taylor polynomial of total degree less than j deﬁnes a linear map on Hk with
kernelFj
k and target of dimension
( n+j− 1
n
)
. □
Since Hk is ﬁnite-dimensional and a holomorphic function vanishing to every order is zero,
Fj
k = 0 for all suﬃciently large j. For each j, choose an orthonormal basis of Fj
k ∩(Fj+1
k )⊥ , where
orthogonality is taken in Hk. Combining these bases gives an orthonormal basis s1,...,s dk of
Hk. Writing ja = ordp(sa), it satisﬁes
Fj
k = span{sa :ja ≥ j}, dimFj
k = #{a :ja ≥ j}. (16)
222
===== PAGE 225 =====
Replacing the monomial basis by this adapted basis does not change Bk or µk.
For ﬁxed s> 0 and j = ⌊sk⌋, the lattice count ( 8) and the vanishing estimate ( 15) give
dimF ⌊sk⌋
k
kn ≥ vol(K) − sn
n! +ok(1).
The leading-order lower bound is positive exactly when s<c K = (n! vol(K))1/n, so we truncate
the vanishing orders at this scale:
Nk = ⌊cKk⌋, q a = min{ja,Nk}.
For a real parameter t, multiply the squared contribution of a basis element with truncated
order qa byetqa. The resulting potential and its initial slope are
uk
t (z) = 1
k log
dk∑
a=1
|sa(z)|2etqa, g k(z) =
∑
aqa|sa(z)|2
kBk(z) .
Thusuk
0 =k− 1 logBk andgk = ∂tuk
t
⏐⏐⏐
t=0
; at eachz,gk(z) is the average ofqa/k with probabilities
|sa(z)|2/Bk(z). In particular,
0 ≤ gk ≤ cK, |uk
t − uk
0| ≤cK|t|. (17)
The average of gk underµk records exactly the truncated vanishing orders. Since the adapted
basis is orthonormal, ( 16) gives
∫
X
gkdµk = 1
kdk
dk∑
a=1
qa = 1
kdk
Nk∑
j=1
dimFj
k ≥ Nkdk −
( n+Nk
n+1
)
kdk
.
The inequality follows from ( 15) and ∑Nk
j=1
( n+j− 1
n
)
=
( n+Nk
n+1
)
. By ( 8), its large- k limit is the
same sharp integral as in Fujita’s point-ﬁltration argument [ Fuj18, proof of Thm. 5.1]:
lim inf
k→∞
∫
X
gkdµk ≥ 1
vol(K)
∫cK
0
(
vol(K) − sn
n!
)
ds = n
n + 1cK. (18)
The bound ( 18) involves a diﬀerent potential uk
t and initial slope gk at each level k. We now
construct a single, k-independent family of potentials ψt withψ0 =ϕ, then transfer this bound
to its initial slope g = ˙ψ0+. The construction uses the complex analogue of convexity.
Recall that a function a : D → [−∞ , ∞ ) on a domain D ⊂ CN is plurisubharmonic if it
is upper semicontinuous and its restriction to every complex aﬃne line satisﬁes the submean
inequality
a(w) ≤ 1
2π
∫2π
0
a
(
w +reiθv
)
dθ
for every w ∈D,v ∈ CN , and r> 0 for which the closed complex disk {w +ζv : |ζ| ≤r} lies in
D. When a is twice diﬀerentiable, this is equivalent to positive semideﬁniteness of its complex
Hessian
(
∂2a/∂wi∂wj
) N
i,j=1.
Fort = log |τ |2, put
Uk(z,τ ) = uk
t (z) = 1
k log
dk∑
a=1
|sa(z)τqa|2.
This function is plurisubharmonic on X × C∗: it is k− 1 times the logarithm of the squared
norm of a holomorphic vector. By Lemma 2.2 and ( 17), the functions Uk are locally uniformly
bounded above. Their regularized tail envelopes therefore deﬁne a plurisubharmonic limit:
Ψm = usc (z,τ )
(
sup
k≥m
Uk(z,τ )
)
, Ψ = limm→∞ Ψm, ψ t(z) = Ψ(z,et/2). (19)
Here uscf (z,τ ) = lim sup (z′,τ ′)→ (z,τ )f (z′,τ ′) denotes upper-semicontinuous regularization in
both variables. For a compact neighborhood Q ofz, set ϵm(Q) = supk≥m supQ |uk
0 −ϕ| → 0. By
(17), for z′ ∈ Q and k ≥ m, |Uk(z′,τ ) − ϕ(z′)| ≤ϵm(Q) +cK|log |τ |2|. Taking the regularized
223
===== PAGE 226 =====
supremum at (z, 1) gives |Ψm(z, 1) −ϕ(z)| ≤ϵm(Q) and therefore ψ0 =ϕ. For t ≥ 0, taking the
same regularized limit in uk
0 ≤ uk
t ≤ uk
0 +cKt gives
ψ0 =ϕ, ϕ ≤ ψt ≤ ϕ +cKt (t ≥ 0). (20)
Since a radial plurisubharmonic function is convex in its logarithmic radius, t ↦→ψt(z) is convex.
Deﬁne its initial right-hand velocity by
g(z) := ˙ψ0+(z) := lim
t↓0
ψt(z) − ϕ(z)
t . (21)
In particular, 0 ≤ g ≤ cK.
The envelope construction immediately gives lim supk→∞ uk
t ≤ ψt. Convexity now relates the
ﬁnite-level velocities gk to the limiting velocity g: for every ﬁxed t> 0,
gk(z) ≤ uk
t (z) − uk
0(z)
t .
Since uk
0 → ϕ locally uniformly, taking upper limits in this inequality and then letting t ↓ 0
gives lim supk→∞ gk ≤ g. Moreover, 0 ≤ gk ≤ cK. Total-variation convergence of µk to µ and
reverse Fatou therefore give
lim sup
k→∞
gk ≤ g, lim sup
k→∞
∫
X
gkdµk ≤
∫
X
gdµ. (22)
Proposition 3.2. ForcK = (n! vol(K))1/n, the initial velocity (21) satisﬁes
∫
X
gdµ ≥ n
n + 1cK.
Proof. Combine the ﬁnite-level estimate ( 18) with the limiting comparison ( 22). □
4. Bergman convexity and the upper slope
It remains to turn the limiting potential into a convex logarithmic partition function and
control its growth near the point p. A function is pluriharmonic if both it and its negative are
plurisubharmonic; adding such a function preserves plurisubharmonicity. In particular, log |zi|2
is pluriharmonic where zi ̸= 0.
On D = ( C∗)n × {τ ∈ C : |τ |> 1}, Berndtsson’s positivity theorem says that the logarithm
of the Bergman kernel associated with any plurisubharmonic weight and Euclidean measure is
itself plurisubharmonic [ Ber06, Thm. 1.1]. The same conclusion holds for the kernels ( 7) deﬁned
using dν: if b is plurisubharmonic on D, then
(z,τ ) ↦− →logBbτ (z), b τ (z) = b(z,τ ), (23)
is plurisubharmonic. Indeed, by ( 5), the Euclidean weight a(z,τ ) = b(z,τ ) +∑n
i=1 log |zi|2 +
n logπ satisﬁes e−adλ =e−bdν. The added logarithms are pluriharmonic, so a is plurisubhar-
monic whenever b is. More generally, Berndtsson’s theorem holds on any pseudoconvex domain.
We now turn the ray into the one-dimensional convex function required by ( 2). Set
Z(t) = 1
vol(K)
∫
X
e−ψtdν, L (t) = − logZ(t), t ≥ 0.
In particular, Z(0) = 1 and L(0) = 0 . In general, if 1 = f0,f 1,...,f r is a basis of a weighted
holomorphic space, its Gram matrix and Bergman kernel are
Gij(t) =
∫
X
fifje−ψtdν, B ψt(z) = v(z)∗G(t)− 1v(z), v (z) = (f0(z),...,f r(z))T.
The unnormalized partition function is G00(t), so positivity of logBψt does not generally imply
convexity of − logG00(t). The unique-interior-lattice-point hypothesis is what reduces G(t) to
a 1 × 1 matrix and identiﬁes these two quantities.
Lemma 4.1. The function L is ﬁnite and convex, and
L′
+(0) =
∫
X
gdµ. (24)
224
===== PAGE 227 =====
Proof. By ( 20), ψt − ϕ is bounded for each t ≥ 0, so Lemma 2.1 gives H(ψt) = C. Taking
the supremum over constant functions in ( 7) therefore identiﬁes the Bergman kernel with the
partition function:
Bψt(z) =
( ∫
X
e−ψtdν
) − 1
= eL(t)
vol(K).
Apply ( 23) to the plurisubharmonic weight b(z,τ ) = Ψ( z,τ ). It follows that logBψt(z) =
L(log |τ |2) − log vol(K) is plurisubharmonic. A radial subharmonic function is convex in its
logarithmic radius, so L is convex on (0, ∞ ); ( 20) extends the convexity continuously to 0.
Finally, ( 20) and the deﬁnition of g give (1 − e− (ψt−ϕ))/t → g pointwise as t ↓ 0, with the
quotient bounded between 0 and cK. Dominated convergence and ( 6) therefore give
1 − Z(t)
t =
∫
X
1 − e− (ψt−ϕ)
t dµ − →
∫
X
gdµ.
Since Z(t) → 1 and L = − logZ, this proves ( 24). □
To bound the other side of the initial slope, it suﬃces to look near the point p where the
ﬁltration was deﬁned. High vanishing order cancels the exponential ﬁltration weight on a ball
whose radius decreases like e−t/2.
Lemma 4.2.
L(t) ≤ nt (t ≥ 0). (25)
Proof. Choose a branch of the coordinates ζi = log zi near p, so that p corresponds to ζ = 0
and dν = π−ndλ(ζ). Let B2r be the Euclidean ball of radius 2r in these coordinates and put
Mr = supB2rϕ. For s ∈ Hk with ∥s∥k = 1 , the submean inequality on B2r bounds s on Br
byCrekMr/2. If s vanishes to order j at p, applying the one-variable Schwarz estimate on each
complex line through 0 improves this to
|s(ζ)| ≤CrekMr/2
( |ζ|
r
) j
(|ζ|<r ).
If |ζ|<re −t/2, then qa ≤ ja gives (|ζ|/r)2jaetqa ≤ 1. Thus uk
t (ζ) ≤ Mr +k− 1 log(C2
rdk) on the
open joint region |ζ| |τ |< r, |τ |> 1. The bound therefore survives the upper-semicontinuous
regularization in ( 19). Since dk = O(kn), taking the regularized tail limit gives ψt ≤ Mr on
Bre− t/2, whose dν-volume is π−nλ(Br)e−nt = cre−nt, where cr > 0. Consequently, for some
constantD independent of t,
Z(t) ≥ cr
vol(K)e−Mr−nt, L (t) ≤ nt +D.
For 0<t<T , convexity and L(0) = 0 now give
L(t)
t ≤ L(T )
T ≤ n + D
T.
Letting T → ∞ proves (25). □
Together, Proposition 3.2 and Lemmas 4.1 and 4.2 give ( 2), proving Theorem 1.1.
References
[BB13] R. J. Berman and B. Berndtsson, Real Monge–Ampère equations and Kähler–Ricci solitons on toric
log Fano varieties , Ann. Fac. Sci. Toulouse Math. (6) 22 (2013), 649–711.
[BB17] R. J. Berman and B. Berndtsson, The volume of Kähler–Einstein Fano varieties and convex bodies , J.
Reine Angew. Math. 723 (2017), 127–152.
[Ber06] B. Berndtsson, Subharmonicity properties of the Bergman kernel and some other functions associated
to pseudoconvex domains , Ann. Inst. Fourier (Grenoble) 56 (2006), 1633–1662.
[BC11] S. Boucksom and H. Chen, Okounkov bodies of ﬁltered linear series , Compos. Math. 147 (2011),
1205–1229.
[CHMT24] M. Campos, P. van Hintum, R. Morris, and M. Tiba, Towards Hadwiger’s conjecture via Bourgain
slicing, Int. Math. Res. Not. IMRN 2024 (2024), no. 10, 8282–8295, doi:10.1093/imrn/rnad198.
[Cav26] I. Cavey, Graded Ehrhart theory and toric geometry , Proc. Amer. Math. Soc. 154 (2026), 1859–1866.
[CK15] D. Cordero-Erausquin and B. Klartag, Moment measures, J. Funct. Anal. 268 (2015), 3834–3866.
225
===== PAGE 228 =====
[Ehr55] E. Ehrhart, Une généralisation du théorème de Minkowski , C. R. Acad. Sci. Paris 240 (1955), 483–485.
[Ehr64] E. Ehrhart, Une généralisation probable du théorème fondamental de Minkowski , C. R. Acad. Sci. Paris
258 (1964), 4885–4887.
[Ehr79] E. Ehrhart, Volume réticulaire critique d’un simplexe , J. Reine Angew. Math. 305 (1979), 218–220.
[Fuj18] K. Fujita, Optimal bounds for the volumes of Kähler–Einstein Fano manifolds , Amer. J. Math. 140
(2018), 391–414.
[Gru60] B. Grünbaum, Partitions of mass-distributions and of convex bodies by hyperplanes , Paciﬁc J. Math.
10 (1960), 1257–1261.
[HHH16] M. Henk, M. Henze, and M. A. Hernández Cifre, Variations of Minkowski’s theorem on successive
minima, Forum Math. 28 (2016), 311–325, doi:10.1515/forum-2014-0093.
[HSTV22] H. Huang, B. A. Slomka, T. Tkocz, and B.-H. Vritsiou, Improved bounds for Hadwiger’s covering
problem via thin-shell estimates , J. Eur. Math. Soc. 24 (2022), 1431–1448.
[KL25] B. Klartag and J. Lehec, Aﬃrmative resolution of Bourgain ’s slicing problem using Guan ’s bound ,
Geom. Funct. Anal. 35 (2025), 1147–1168, doi:10.1007/s00039-025-00718-w.
[MP00] V. D. Milman and A. Pajor, Entropy and asymptotic geometry of non-symmetric convex bodies , Adv.
Math. 152 (2000), 314–335.
[NP14] B. Nill and A. Paﬀenholz, On the equality case in Ehrhart’s volume conjecture , Adv. Geom. 14 (2014),
579–586.
[PS14] F. T. Pokorny and M. Singer, Toric partial density functions and stability of toric varieties , Math.
Ann. 358 (2014), 879–923.
[RR24] V. Reiner and B. Rhoades, Harmonics and graded Ehrhart theory , J. Combin. Algebra, to appear;
arXiv:2407.06511.
[R W14] J. Ross and D. Witt Nyström, Analytic test conﬁgurations and geodesic rays , J. Symplectic Geom. 12
(2014), 125–169.
[Zel09] S. Zelditch, Bernstein polynomials, Bergman kernels and toric Kähler varieties , J. Symplectic Geom.
7 (2009), 51–76.
226
===== PAGE 229 =====
Chapter 9
Super-exponential lower bounds for
R(3, . . . ,3)
Abstract. Let Rk(3) = R(3, . . . ,3
k
) denote the multicolor Ramsey number
for k colors, that is, the least N for which every k-coloring of the edges of KN
contains a monochromatic triangle. We prove that there exists an absolute
constant c > 0 such that, for every integer k ≥ 2,
Rk(3) ≥
(
ck1/3
log k
) k
.
Together with the classical factorial upper bound, this establishes Rk(3) =
kΘ(k). In particular, the Shannon capacity of graphs with independence num-
ber 2 is unbounded.
Contents
1. Introduction
2. Saturated matrices, coordinate covers, and palettes
3. Recursive triangle-free colorings
References
227
===== PAGE 230 =====
1. Introduction
Write
Rk(3) = R(3, . . . ,3
k
)
for the least integer N such that every coloring of E(KN ) with k colors contains a monochro-
matic triangle. Via the standard product construction
Rk+ℓ(3) − 1 ≥
(
Rk(3) − 1
)(
Rℓ(3) − 1
)
and Fekete’s lemma, the limit
L = lim
k→∞
Rk(3)1/k (1)
exists in [1, ∞].
Previous lower bounds were obtained by tensoring small triangle-free colorings and by
constructions from sum-free partitions [ GG55, Chu73, CG83, Exo94, FS00]. After a series
of improvements, the best known lower bound before this work was
Rk(3) ≥ 380k/5 − O(1)
[ACPPRT21, Blo183]. On the upper-bound side, reﬁnements [ Whi73, Wan97, XXC02,
Blo183, Rad] of the standard monochromatic-neighborhood recurrence led to constant-factor
improvements of the upper bound. The current record is
Rk(3) ≤
(
e − 1
6
)
k! + 1 ( k ≥ 4). (2)
The question whether Rk(3) grows superexponentially was recorded by Graham, Roth-
schild, and Spencer [ GRS90, p. 146]. The connection between the multicolor Ramsey problem
and Shannon capacity appears implicitly in work of Erdős, McEliece, and Taylor [ EMT71]
and was made explicit by Alon and Orlitsky [ AO95, §2.1], who also raised the analogous
question for R(c, . . . , c) with ﬁxed c. The gap between these exponential lower bounds and
factorial upper bounds was later highlighted explicitly by Conlon, Fox, and Sudakov [ CFS15,
§2.1]; see also [ CG83, Rad]. For the broader interaction between structure and randomness,
see Gowers [Gow00]. Erdős oﬀered $250 for determining the value of ( 1) and $100 for deciding
whether it is ﬁnite [ CG83, Blo183, CG].
Theorem 1.1. There exists an absolute constant c > 0 such that, for every integer k ≥ 2,
R(3, . . . ,3
k
) = Rk(3) ≥
(
ck1/3
log k
) k
. (3)
Together with (2), this gives
k(1/3−o(1))k ≤ Rk(3) ≤ k(1+o(1))k, R k(3) = kΘ(k).
In particular,
lim
k→∞
Rk(3)1/k = +∞. (4)
The Ramsey–Shannon correspondence [ EMT71, AO95] also gives an equivalent formula-
tion of ( 4). For a graph G, write
Θ(G) = sup
m≥1
α
(
G⊠m) 1/m
for its Shannon capacity, where α(G) is the independence number and ⊠ denotes the strong
graph product. Given a triangle-free k-coloring of KN , let Hi be the graph of color i and set
G = H1 ∨ · · · ∨ Hk,
where ∨ denotes the complete join. Then α(G) = 2 , and the N diagonal words form an
independent set in G⊠k. Thus Θ(G) ≥ N 1/k. Taking N = Rk(3) − 1 and applying ( 4),
228
===== PAGE 231 =====
we obtain graphs with independence number 2 and arbitrarily large Shannon capacity. In
particular, Shannon capacity cannot be bounded above by any function of the independence
number.
1.1. Proof outline. The argument adapts the random-matrix and coordinate-covering in-
gredients of Alon, Ben-Eliezer, Shangguan, and Tamo [ ABST20, Lemmas 3.4 and 4.1]. Their
saturated-matrix argument in turn builds on work of Chakraborty, Radhakrishnan, Raghu-
nathan, and Sasatte on zero-error list decoding [ CRRS06]. We give direct proofs of the
matrix and two-sided coordinate-covering statements without the hat-guessing terminology.
The saturated-matrix construction is not new; its application to R(3, . . . ,3) is.
Fix a stage parameter H. A union bound produces an H-colored s × H m matrix, where
m ≍ H log H and s ≍ H 2 log2 H, such that among any m+1 columns some row contains every
color. This property yields maps f, g : [ H]s → [H]s, ﬁxed once for the entire construction,
such that for every x, y ∈ [H]s there is a d ∈ [s] with
xd =
(
f (y)
)
d or yd =
(
g(x)
)
d.
We construct an edge-coloring recursively while maintaining the stronger invariant that, at
stage j, each color graph is properly (j + 1)-colorable. Divide the vertices into blocks indexed
by palettes P ⊆ [jt] of size t = s⌈log H⌉. The palette P records the colors missing from its
block; all other colors are active. Inside that block, place a copy of the preceding coloring
with colors relabeled by [jt] \ P . Each active color then has a proper internal vertex labeling
in [j]. A maximal packing provides many palettes while ensuring that distinct palettes diﬀer
in at least s colors in each direction.
For blocks P < Q , choose colors a1, . . . , as ∈ Q \ P and b1, . . . , bs ∈ P \ Q. The internal
labels of u ∈ VP in the ad and of v ∈ VQ in the bd form words x(u), y(v) ∈ [H]s. Apply
the ﬁxed coordinate cover to these words: if xd(u) =
(
f (y(v))
)
d, color uv with ad; otherwise
color it with a bd for which yd(v) =
(
g(x(u))
)
d. Every cross-edge color is therefore active
at exactly one endpoint block and missing at the other. Crucially, the proper label at the
active endpoint is determined by the opposite endpoint.
This last property excludes triangles on two blocks: two edges of the same color from one
outside vertex into an active block force the same internal label, so the edge between their
endpoints cannot have that color. If the color is missing from the block, there is no internal
edge of that color in the ﬁrst place. A triangle on three blocks would require a color to belong
to each of P △Q, Q△R, and P △R: by symmetry, if c ∈ P , the ﬁrst two memberships give
c /∈ Q and c ∈ R, contradicting the third. Finally, label each active block using its proper
internal labels and each missing block with the new label j + 1. Since every cross edge of
a ﬁxed color joins an active block to a missing block, these labels properly color its entire
color graph and propagate the inductive invariant.
Multiplying the sizes of the packed palette families over the H stages gives a triangle-free
coloring with kH ≍ H 3 log3 H colors and at least (c0H)kH vertices. Rounding down to the
nearest such color count changes only the absolute constant. Since H ≫ k1/3/ log k, this
proves (3) for all suﬃciently large k; decreasing the constant covers the remaining k ≥ 2.
All logarithms are natural, [r] = {1, . . . , r}, and [0] is empty. We do not optimize the
absolute constants.
2. Saturated matrices, coordinate covers, and palettes
We ﬁrst show that, in a thin, wide matrix randomly colored with H colors, every suﬃciently
large set of columns contains a row in which all H colors appear. This is the saturated-
matrix construction of [ ABST20, Lemma 3.4], whose underlying family was studied earlier
in [ CRRS06].
Lemma 2.1. Let H ≥ 2, and deﬁne
m = ⌈2H log H⌉, s = m(m + 1) + 1. (5)
229
===== PAGE 232 =====
There is a matrix
A = (Ar,z)r∈[s], z ∈[H]m with Ar,z ∈ [H]
such that, for every T ⊆ [H]m with |T | = m + 1, some row r ∈ [s] satisﬁes
{Ar,z : z ∈ T } = [H]. (6)
Proof. Choose all entries independently and uniformly from [H]. For a ﬁxed set T of m + 1
columns, a given row fails ( 6) only if one of the H symbols is absent. Hence
P
(
{Ar,z : z ∈ T } ̸= [H]
)
≤ H
(
1 − 1
H
) m+1
< H exp
(
− m
H
)
≤ 1
H .
Independence bounds the probability that all s rows fail for this T by H −s. Since there are
at most
(H m
m+1
)
≤ H m(m+1) choices of T , a second union bound gives a total failure probability
at most
H m(m+1)−s = H −1 < 1.
Thus one matrix works simultaneously for all sets of m + 1 columns. □
The next lemma converts this matrix property into a two-sided coordinate cover. One
function handles all but a small exceptional set of words; the other handles the remaining
words by assigning them distinct coordinates. The construction adapts [ ABST20, Lemma 4.1]
to the present symmetric formulation.
Lemma 2.2 (Two-sided coordinate cover) . For H, m, s as in (5), there are ﬁxed maps
f, g : [H]s − →[H]s
such that, for every x, y ∈ [H]s,
∃d ∈ [s] : xd =
(
f (y)
)
d or yd =
(
g(x)
)
d. (7)
Proof. Fix a matrix A from Lemma 2.1 . Write ¯x = (x1, . . . , xm), and set
(
g(x)
)
r = Ar,¯x (r ∈ [s]). (8)
For y ∈ [H]s, let
Ey = {z ∈ [H]m : Ar,z ̸= yr for every r ∈ [s]}. (9)
Then |Ey| ≤ m. Otherwise take m + 1 members of Ey. The matrix property gives a row
containing every symbol on those columns and, in particular, a column z for which Ar,z = yr
for some r, contrary to ( 9).
Enumerate Ey in a ﬁxed order as z(1), . . . , z(ρ), where ρ ≤ m, and deﬁne
(
f (y)
)
d =
{
z(d)
d , 1 ≤ d ≤ ρ,
1, ρ < d ≤ s.
The ﬁrst case makes sense because d ≤ ρ ≤ m. If ¯x /∈ Ey, then ( 9) and ( 8) give some d ∈ [s]
such that
yd = Ad,¯x =
(
g(x)
)
d.
If instead ¯x ∈ Ey, then ¯x = z(d) for some d ≤ ρ, and
xd = z(d)
d =
(
f (y)
)
d.
In either case, ( 7) follows. □
We next pack the palettes that will specify the colors missing from each block. Fix H ≥ 3,
use the parameters of ( 5), and put
t = s⌈log H⌉, M j = jt (0 ≤ j ≤ H). (10)
In particular, t ≥ 2s. At stage j, a palette is a member of
([Mj ]
t
)
. A block with palette P
will omit exactly the colors in P .
230
===== PAGE 233 =====
Lemma 2.3 (Separated palettes) . For every 1 ≤ j ≤ H, there is a family
Pj ⊆
(
[jt]
t
)
such that distinct P, Q ∈ P j satisfy
|P \ Q| = |Q \ P | ≥ s. (11)
Writing Bj = |Pj|, one can arrange that Bj ≥ 1 and
Bj ≥
(jt
t
)
s−1∑
d=0
(
t
d
)(
(j − 1)t
d
) ≥ jt
s
(
e2j⌈log H⌉2) s . (12)
Proof. Take a maximal family satisfying ( 11). Every t-subset of [jt] then lies at diﬀerence
less than s from at least one selected palette. Counting these covering balls gives the ﬁrst
inequality in ( 12). Since t = s⌈log H⌉ ≥ 2s, the estimates
(
jt
t
)
≥ jt,
s−1∑
d=0
(
t
d
)(
(j − 1)t
d
)
≤ s
(
t
s
)(
jt
s
)
,
(
N
r
)
≤
(eN
r
) r
immediately give the second inequality in ( 12). A maximal family is nonempty, so Bj ≥ 1. □
3. Recursive triangle-free colorings
For an edge-coloring κ, write Γκ(c) for the spanning graph whose edges are those of color
c. We construct colorings for which every Γκ(c) has a short proper vertex coloring. This
stronger invariant is what makes a triangle-free recursion possible.
Proposition 3.1 (Recursive coloring) . Fix H ≥ 3, let t and Mj be as in (10), and, for
1 ≤ r ≤ H, let Pr be a palette family provided by Lemma 2.3 . Write Br = |Pr|. For each
0 ≤ j ≤ H, there is a coloring
κj : E(Knj ) − →[Mj], n j =
j∏
r=1
Br,
with the following properties:
(1) κj contains no monochromatic triangle;
(2) for each c ∈ [Mj],
χ
(
Γκj (c)
)
≤ j + 1.
Proof. Fix once and for all the maps f, g : [ H]s → [H]s provided by Lemma 2.2 ; the same
pair will be used at every stage and for every pair of blocks. For j = 0 , take the edgeless
graph on one vertex. Suppose the statement holds at stage j − 1, and order Pj once and for
all.
Internal edges and labels. For every P ∈ P j, take a block VP of nj−1 vertices. Since
|[Mj] \ P | = (j − 1)t = Mj−1,
place a copy of κj−1 on VP , relabeling its color set bijectively by [Mj] \ P . A color c is active
on VP if c /∈ P and missing if c ∈ P . For each active c, the inductive invariant supplies a
proper coloring
ℓP
c : VP − →[j]
of the internal graph of color c. In particular,
κj(uu′) = c =⇒ ℓP
c (u) ̸= ℓP
c (u′) ( u, u′ ∈ VP ). (13)
Cross edges. For each ordered pair P < Q , ﬁx distinct colors
a1, . . . , as ∈ Q \ P, b 1, . . . , bs ∈ P \ Q,
231
===== PAGE 234 =====
which is possible by Lemma 2.3 . The ad are active on VP and missing on VQ; the bd have
the opposite status. For u ∈ VP and v ∈ VQ, form
x(u) =
(
ℓP
ad(u)
) s
d=1, y (v) =
(
ℓQ
bd(v)
) s
d=1.
These belong to [H]s because j ≤ H.
If xd(u) =
(
f (y(v))
)
d for some d, assign uv the color ad for the least such d. Otherwise
Lemma 2.2 supplies a d with yd(v) =
(
g(x(u))
)
d; assign uv the color bd for the least such d.
In particular,
κj(uv) ∈ P △ Q. (14)
More importantly, the label at the active endpoint is determined by the opposite endpoint:
κj(uv) = ad =⇒ ℓP
ad(u) =
(
f (y(v))
)
d, (15)
κj(uv) = bd =⇒ ℓQ
bd(v) =
(
g(x(u))
)
d. (16)
Triangles in one or two blocks. A triangle inside one block is not monochromatic by induction.
Suppose next that u, u′ ∈ VP and v ∈ VQ, with κj(uv) = κj(u′v) = c. If c ∈ P , the color is
missing internally on VP , so κj(uu′) ̸= c.
If instead c /∈ P , it is active on VP . When P < Q , the distinctness of the ad gives a unique
d with c = ad, and ( 15) yields
ℓP
c (u) =
(
f (y(v))
)
d = ℓP
c (u′).
When Q < P , the distinctness of the relevant bd and ( 16) give exactly the same conclusion.
Now ( 13) shows that the internal edge uu′ cannot have color c.
Triangles in three blocks. Suppose a triangle of color c meets three distinct blocks VP , VQ, VR.
By ( 14),
c ∈ P △Q, c ∈ Q△R, c ∈ P △R.
By symmetry, suppose c ∈ P . The ﬁrst inclusion gives c /∈ Q, and the second then gives
c ∈ R. But this contradicts c ∈ P △R. The coloring is therefore triangle-free.
The next proper-coloring invariant. For a ﬁxed c ∈ [Mj], deﬁne
Lc(v) =
{
ℓP
c (v), v ∈ VP , c /∈ P,
j + 1, v ∈ VP , c ∈ P.
Inside an active block, Lc properly colors the c-edges; inside a missing block, there are no
c-edges. By ( 14), every cross edge of color c joins an active block to a missing block. Its
endpoints therefore receive labels in [j] and {j + 1}, respectively. Thus Lc is a proper (j + 1)-
coloring of Γκj (c). Finally, the Bj blocks each have nj−1 vertices, proving nj = Bjnj−1 and
completing the induction. □
Proof of Theorem 1.1. By decreasing c, it suﬃces to prove ( 3) for suﬃciently large k. For
H ≥ 3, write
m(H) = ⌈2H log H⌉, s (H) = m(H)
(
m(H) + 1
)
+ 1, k H = Hs(H)⌈log H⌉.
These special color counts satisfy kH ≍ H 3 log3 H and kH+1/kH = 1 + O(1/ log H). If
kH ≤ k < k H+1, monotonicity therefore shows that a bound RkH (3) ≥ (c0H)kH implies
Rk(3) ≥ (c1H)k for another absolute constant c1 > 0: the factor kH /k = 1 − O(1/ log H)
changes log(c0H) by only an additive constant. Moreover, k < k H+1 = O(H 3 log3 H) implies
H ≫ k1/3/ log k. Hence, after decreasing c again, it suﬃces to consider
k = kH = Hs⌈log H⌉
for suﬃciently large H, where s = s(H).
232
===== PAGE 235 =====
At stage H, Proposition 3.1 produces a triangle-free k-coloring on∏H
j=1 Bj vertices. Recall
that t = s⌈log H⌉, s = O(H 2 log2 H), k ≍ H 3 log3 H, and log(H!) ≥ H log H − H. Multi-
plying ( 12) therefore gives, for suﬃciently large k and a suﬃciently small absolute constant
c > 0,
Rk(3) ≥ (H!)t−s
sH(
e2⌈log H⌉2) sH ≥
(
ck1/3
log k
) k
.
This proves ( 3). Since k1/3/ log k → ∞, ( 4) follows. □
References
[ACPPRT21] R. Ageron, P. Casteras, T. Pellerin, Y. Portella, A. Rimmel, and J. Tomasik, New lower bounds
for Schur and weak Schur numbers , 2021, arXiv:2112.03175.
[ABST20] N. Alon, O. Ben-Eliezer, C. Shangguan, and I. Tamo, The hat guessing number of graphs ,
J. Combin. Theory Ser. B 144 (2020), 119–149, doi:10.1016/j.jctb.2020.01.003; see also
arXiv:1812.09752.
[AO95] N. Alon and A. Orlitsky, Repeated communication and Ramsey graphs , IEEE Trans. Inform.
Theory 41 (1995), 1276–1289.
[Blo183] T. F. Bloom, Erdős problem #183 , https://www.erdosproblems.com/183; see also https://
www.erdosproblems.com/latex/183.
[CRRS06] S. Chakraborty, J. Radhakrishnan, N. Raghunathan, and P. Sasatte, Zero error list-decoding
capacity of the q/(q − 1) channel, in Foundations of Software Technology and Theoretical Com-
puter Science , Lecture Notes in Comput. Sci. 4337, Springer, 2006, 129–138.
[Chu73] F. R. K. Chung, On the Ramsey numbers N (3, 3, . . . ,3; 2), Discrete Math. 5 (1973), 317–321,
doi:10.1016/0012-365X(73)90125-8.
[CG] F. Chung and R. Graham, Multi-color Ramsey number for triangles , in Erdős Problems, https:
//mathweb.ucsd.edu/~erdosproblems/erdos/newproblems/MulticolorR3.html.
[CG83] F. R. K. Chung and C. M. Grinstead, A survey of bounds for classical Ramsey numbers , J.
Graph Theory 7 (1983), 25–37, doi:10.1002/jgt.3190070105.
[CFS15] D. Conlon, J. Fox, and B. Sudakov, Recent developments in graph Ramsey theory , in Surveys in
Combinatorics 2015 , London Math. Soc. Lecture Note Ser. 424, Cambridge University Press,
2015, arXiv:1501.02474.
[EMT71] P. Erdős, R. J. McEliece, and H. Taylor, Ramsey bounds for graph products , Paciﬁc J. Math.
37 (1971), 45–46.
[Exo94] G. Exoo, A lower bound for Schur numbers and multicolor Ramsey numbers , Electron. J. Com-
bin. 1 (1994), R8.
[FS00] H. Fredricksen and M. M. Sweet, Symmetric sum-free partitions and lower bounds for Schur
numbers, Electron. J. Combin. 7 (2000), R32.
[Gow00] W. T. Gowers, Rough structure and classiﬁcation , Geom. Funct. Anal., Special Volume, Part I
(2000), 79–117; reprinted in Visions in Mathematics , Birkhäuser, 2010, doi:10.1007/978-3-0346-
0422-2_4.
[GRS90] R. L. Graham, B. L. Rothschild, and J. H. Spencer, Ramsey Theory, 2nd ed., Wiley-Interscience,
1990.
[GG55] R. E. Greenwood and A. M. Gleason, Combinatorial relations and chromatic graphs , Canad. J.
Math. 7 (1955), 1–7, doi:10.4153/CJM-1955-001-4.
[Rad] S. P. Radziszowski, Small Ramsey numbers , Electron. J. Combin., Dynamic Survey DS1, https:
//www.combinatorics.org/ojs/index.php/eljc/article/view/DS1.
[Wan97] H. Wan, Upper bounds for Ramsey numbers R(3, 3, . . . ,3) and Schur numbers , J. Graph Theory
26 (1997), 119–122.
[Whi73] E. G. Whitehead, Jr., The Ramsey number N (3, 3, 3, 3; 2), Discrete Math. 4 (1973), 389–396.
[XXC02] X.-D. Xu, Z. Xie, and Z. Chen, Upper bounds for Ramsey numbers Rn(3) and Schur numbers ,
Math. Econ. 19 (2002), 81–84.
233
===== PAGE 236 =====
Chapter 10
Counterexamples to the Compactness and
Degeneracy Conjectures for Extremal
Numbers
Abstract. We give two complementary counterexamples in extremal graph the-
ory. First, we construct a ﬁnite family F of connected bipartite graphs, each
containing a cycle, for which
ex(n, F ) = O
(
n4/ 3−1/ 48)
but ex(n, F ) = Ω
(
n4/ 3)
(F ∈ F ).
This disproves the Erdős–Simonovits compactness conjecture. Second, we con-
struct a ﬁxed connected bipartite 2-degenerate graph H and ﬁxed constants
c, ε > 0 such that
ex(n, H) ≥ c n3/ 2+ε for all suﬃciently large n.
This disproves a conjecture of Erdős on extremal numbers of r-degenerate graphs.
Contents
1. Introduction
2. The forbidden graphs for compactness
3. Proof of the upper bound in Theorem 1.1
4. The generalized-quadrangle witnesses
5. A binary entropy inequality
6. The layered graph and the parameter thresholds
7. A sampled Hamming-ball graph
8. Excluding the forbidden graph
References
234
===== PAGE 237 =====
1. Introduction
We disprove the compactness conjecture of Erdős and Simonovits and a degeneracy conjec-
ture of Erdős in extremal graph theory. The compactness conjecture [ ES82, Wig] asks whether
forbidding a ﬁnite family of graphs, each containing a cycle, can reduce the extremal number
by more than a constant factor compared with forbidding any individual member. The degen-
eracy conjecture [ Erd67] predicts that every bipartite r-degenerate graph has extremal number
O(n2−1/r ), which we disprove even when r = 2.
Throughout, all graphs are ﬁnite, simple, and undirected, and implicit constants may depend
on ﬁxed forbidden graphs or families. For a graph G, let V (G) and E(G) denote its vertex and
edge sets, respectively. Given a family F of graphs, we say G is F -free if it contains no member
of F as a subgraph. The extremal number of F is
ex(n, F ) := max
{
|E(G)| : |V (G)| = n, G is F -free
}
.
For a single graph H, we abbreviate ex(n, {H}) to ex(n, H).
1.1. The compactness conjecture. Erdős and Simonovits conjectured that the extremal
number of a ﬁnite family of graphs is, up to a constant factor, the extremal number of one of its
members [ES82, FS13, Con26, Blo575]. The original formulation admits simple counterexamples
[Wig]. For example, the folklore family {K1, 2, 2K2} [Blo180] satisﬁes, for n ≥ 4,
ex(n, {K1, 2, 2K2}) = 1 , ex(n, K1, 2) = ⌊n/ 2⌋, ex(n, 2K2) = n − 1.
The corrected form of the conjecture (see [ Wig]) asks: for every ﬁnite nonempty family of graphs
F , all of whose members contain cycles, do there exist F ∈ F and C > 0 such that
ex(n, F ) ≤ C ex(n, F ) for all suﬃciently large n? (1)
Conlon, Mulrenin, and Pohoata [ CMP26] recently disproved a conjecture of Verstraëte [ Ver16,
Conj. VIII], a stronger host-graph analog of compactness for even cycles, but their examples
do not resolve the compactness conjecture itself. We disprove this conjecture even when every
member of F is connected and bipartite.
Theorem 1.1 (Failure of compactness) . There exists a ﬁnite nonempty family F of connected
bipartite graphs, every member of which contains a cycle, such that, for ε = 1/ 48,
ex(n, F ) = O
(
n4/ 3−ε)
and ex(n, F ) = Ω
(
n4/ 3)
(F ∈ F ). (2)
In particular, no member of F satisﬁes (1).
1.2. The degeneracy conjecture. A graph H is r-degenerate if every nonempty subgraph of
H has a vertex of degree at most r. Erdős [ Erd67, Erd97, Blo146] conjectured that every ﬁxed
bipartite r-degenerate graph H satisﬁes
ex(n, H) = O
(
n2−1/r )
. (3)
Alon, Krivelevich, and Sudakov proved the weaker general estimate ex(n, H) = O
(
n2−1/ (4r))
for
bipartite r-degenerate graphs [ AKS03, Thm. 3.5].
The conjecture is known in several cases: when one bipartition class has maximum degree at
most r [Fur91, AKS03]; for r-degenerate blow-ups of trees [ GJN22]; and, when r = 2, for grids
[BJST23] and certain critical 2-degenerate graphs [ DGL25].
A related conjecture of Erdős [ Erd81, Blo113] asserts that a bipartite graph H is 2-degenerate
if and only if ex(n, H) = O(n3/ 2). Janzer [ Jan23] disproved the reverse implication by con-
structing, for every η > 0, a 3-regular bipartite graph H with ex(n, H) = O(n4/ 3+η). Janzer’s
construction does not address the forward implication, which is the r = 2 case of ( 3).
We disprove Erdős’s degeneracy conjecture by constructing a counterexample for r = 2 ,
thereby also refuting the forward implication of the related conjecture.
Theorem 1.2 (Failure of the 2-degenerate bound) . There exist a ﬁxed connected bipartite 2-
degenerate graph H and constants c, ε > 0 such that
ex(n, H) ≥ c n3/ 2+ε
235
===== PAGE 238 =====
for all suﬃciently large n.
1.3. Proof strategy. For the compactness conjecture, we select F to consist of C4, C6, and
certain admissible quotients of two ﬁxed templates built from subdivided complete bipartite
graphs, in analogy with the rooted-power construction of Bukh and Conlon [ BC18]. We count
short paths in a graph avoiding this family to obtain the upper bound ex(n, F ) = O(n21/ 16).
For each individual forbidden graph F ∈ F , we obtain the lower bound ex(n, F ) = Ω( n4/ 3) from
the incidence graph of a generalized quadrangle, allowing the characteristic of the underlying
ﬁeld to depend on the forbidden graph. We develop this counterexample in Sections 2 to 4.
For the degeneracy conjecture, we construct H in layers, adjoining a vertex for every pair of
vertices in the preceding layer. This construction is related to the complete degenerate graphs
of Grzesik, Janzer, and Nagy [ GJN22]. To obtain a lower bound on ex(n, H), we independently
retain vertices of a bipartite graph deﬁned by Hamming distance. An embedding of H would
increase a bounded entropy potential by a ﬁxed amount at each layer, which is impossible
after suﬃciently many layers. A second-moment argument shows that the sampled graph has
Ω(n3/ 2+ε) edges, and padding extends the construction to every suﬃciently large order. We
develop this counterexample in Sections 5 to 8.
2. The forbidden graphs for compactness
The compactness family arises from two properly 2-colored bipartite templates.
Deﬁnition 2.1 (Subdivisions). For k ∈ {2, 3}, form Sk from K3,k by replacing each edge with
a two-edge path; therefore |V (S2)| = 11 and |V (S3)| = 15. Call the three original vertices bases,
the other k original vertices centers, and the inserted vertices subdivision vertices.
Deﬁnition 2.2 (Admissible identiﬁcations) . Let T be a properly two-colored graph with dis-
tinguished subgraphs T1, T2. An equivalence relation ≈ on V (T ) is admissible if
(1) v ≈ w implies that v and w have the same color; and
(2) for i ∈ {1, 2} and v, w ∈ V (Ti), v ≈ w implies v = w.
Write T / ≈ for the simple graph whose vertices are the equivalence classes and in which [v][w]
is an edge whenever some representatives are adjacent in T . Repeated edges are suppressed.
The ﬁrst condition keeps T / ≈ bipartite and prevents loops. The second ensures that the
maps Ti → T / ≈ are injective.
Deﬁnition 2.3 (The ﬁrst template) . Form J0 from two copies of S2 with base triples {x, y, z}
and {x′, y, z} by identifying y, z, keeping all other vertices distinct, and adjoining a color-one
vertex λ adjacent to x, x′. Thus, |V (J0)| = 21 . Let J consist of the uncolored admissible
quotients J0/ ≈ satisfying x ̸≈ x′. This condition preserves all four distinguished bases; λ may
be identiﬁed whenever admissibility permits.
Deﬁnition 2.4 (The second template) . Let K0 be obtained from disjoint copies S(1)
3 , S(2)
3 of S3
by reversing the coloring on S(2)
3 and adding an edge d1d2 between speciﬁed centers of the two
copies. Thus, |V (K0)| = 30. Let K consist of the uncolored graphs K0/ ≈, where ≈ is admissible
for S(1)
3 , S(2)
3 .
The two templates are shown in Figure 1 .
Deﬁnition 2.5 (The forbidden family) . Let
F := {C4, C6} ∪ J ∪ K . (4)
As each member of J contains S2 and each member of K contains S3, every graph in F
contains a cycle.
236
===== PAGE 239 =====
J0
x x′
y
z
c1
c2
c′
1
c′
2
λ
K0
S(1)
3 S(2)
3
u1
u2
u3
c1
d1
c3
c′
1
d2
c′
3
u′
1
u′
2
u′
3
Figure 1. The graphs J0 and K0.
3. Proof of the upper bound in Theorem 1.1
Throughout this section, B is a bipartite graph containing no C4 or C6, and S is either side
of the bipartition of B. Let RS be the auxiliary common-neighbor graph on S, deﬁned by
uv ∈ E(RS) ⇐ ⇒ u ̸= v and NB(u) ∩ NB(v) ̸= ∅.
The graph RS records pairs joined by length-two paths in B, which are central to the forbidden
conﬁgurations.
For distinct u, v ∈ S, write u ∼ v when uv ∈ E(RS), and call u, v related or unrelated
according as they are adjacent or nonadjacent in RS. Call a set of vertices RS-independent if
no pair is adjacent in RS. For an RS-independent triple T ⊆ S, put
L(T ) := {c ∈ S : c ∼ t for all t ∈ T } and r(T ) := |L(T )|.
Lemma 3.1 (Common-neighbor geometry) . The following assertions hold:
(1) Every related pair has a unique common neighbor. If three distinct members of S are
pairwise related, the three pairs have the same common neighbor.
(2) If T ⊆ S is an RS-independent triple, then L(T ) is RS-independent and disjoint from T .
If r(T ) ≥ k, for k ∈ {2, 3}, then B contains a copy of Sk with base set T . Conversely, the
bases of any such copy form an RS-independent triple with at least k common centers.
(3) If u, v ∈ S are distinct and unrelated, then any two distinct vertices related to both u
and v are unrelated. Equivalently, the set
Zuv = {w ∈ S : w ∼ u, w ∼ v}
is RS-independent.
Proof. A related pair has a unique common neighbor, since two would form a C4. For three
pairwise related vertices, their common neighbors either all coincide or form a C6. This proves
(1).
If u ̸∼ v and w, w′ ∈ Zuv were related, (1) would make their common neighbor adjacent to
both u and v, a contradiction. This proves (3).
For distinct u, v ∈ T , we have L(T ) ⊆ Zuv. Thus, (3) makes L(T ) independent, while
irreﬂexivity gives L(T ) ∩ T = ∅. If r(T ) ≥ k, the unique common neighbors of the 3k pairs
between T and any k centers in L(T ) are distinct: a repetition would relate two bases or two
237
===== PAGE 240 =====
centers. This forms a copy of Sk. Conversely, (1) forces related bases in such a copy to share a
subdivision vertex at every center, a contradiction. Thus, its bases are independent and its k
centers belong to L(T ), proving (2). □
Lemma 3.2 (Non-backtracking four-edge-walk count) . If δ(B) ≥ d ≥ 2, then, for every u ∈ S,
∑
v∈S\{u}
v̸∼u
|Zuv| ≥ d(d − 1)3. (5)
Proof. There are at least d(d − 1)3 non-backtracking walks u, a, w, b, v. Since B has girth at
least eight, each satisﬁes v ̸= u and v ̸∼ u; otherwise it closes to a cycle of length at most six.
By Lemma 3.1 (1), these walks correspond bijectively to pairs (v, w) with v ̸= u, v ̸∼ u, and
w ∈ Zuv. Counting these pairs proves ( 5). □
Lemma 3.3 (Minimum-degree reduction) . Let G be an n-vertex graph without C4 or C6, and
put m = |E(G)| > 0. There is a nonempty bipartite subgraph B of order N ≤ n and minimum
degree d such that
m ≤ 2nd and ∆(B)(d − 1)2 ≤ N.
Proof. A maximum cut yields a bipartite subgraph with at least m/ 2 edges. Deleting vertices
of degree < m/ (2n) cannot exhaust it, since fewer than m/ 2 edges would be removed. Thus,
the remainder B satisﬁes d = δ(B) ≥ m/ (2n), and hence m ≤ 2nd.
Since B has girth at least eight, the radius-three neighborhood of a maximum-degree vertex
is a tree. Its third level contains at least ∆(B)(d − 1)2 vertices, so ∆(B)(d − 1)2 ≤ N . □
The main estimate uses the two forbidden families in complementary ways. Excluding J
bounds the number of vertices that fail to be centers of a subdivided K3, 3, while excluding K
forces every edge to meet one of these vertices.
Proposition 3.4 (Key counting estimate) . For the family F in (4),
ex(n, F ) = O(n21/ 16) = O(n4/ 3−1/ 48).
Proof. Let G be an n-vertex F -free graph. We may assume m := |E(G)| ≥ Cn21/ 16, where
C ≥ 1 is suﬃciently large. Let B be the bipartite subgraph supplied by Lemma 3.3 , with order
N ≤ n and minimum degree d. Put
d ≥ m
2n ≫ CN 5/ 16, p = d(d − 1)3, R = p
2N .
Fix a bipartition class S and u ∈ S, and write tuv = |Zuv|. Lemma 3.1 shows that Cu :=∑
v̸=u
v̸∼u
( tuv
3
)
counts the copies of S2 with center u. By discrete convexity of binomial coeﬃcients,
we have
Cu ≥ N
( N −1∑
v̸=u
v̸∼u
tuv
3
)
≫ d12
N 2 ,
where Lemma 3.2 gives∑
v̸=u
v̸∼u
tuv ≥ d(d − 1)3.
We use the exclusion of J to bound the number of possible base triples. For an unrelated
pair y, z ∈ S, let
Ayz :=
{
x ∈ S \ {y, z} : {x, y, z} is independent in RS, r ({x, y, z}) ≥ 2
}
.
This is the set of possible third bases for copies of S2 whose other bases are y, z. If two distinct
vertices of Ayz were related, their witnessing copies of S2, together with their common neighbor,
would produce a member of J . Thus, Ayz is RS-independent; its vertices therefore have pairwise
disjoint neighborhoods, and |Ayz | ≤ N/d .
Writing TS for the set of independent triples in S with at least two common centers, we obtain
|TS| = 1
3
∑
{y,z }⊆S
y̸∼z
|Ayz | ≤ N
3d
(
N
2
)
≤ N 3
6d . (6)
238
===== PAGE 241 =====
Let U ⊆ V (B) be the set of vertices that are not centers of any copy of S3. For every
bipartition class S and every u ∈ S, we have
Cu =
∑
T ∈TS
u∈L(T )
(
r(T ) − 1
)
.
Indeed, for each triple T with u ∈ L(T ), choosing another center v ∈ L(T ) \ {u} determines
a copy of S2 with base triple T and centers u, v; conversely, every copy counted by Cu arises
uniquely in this way.
If u ∈ U ∩ S and u ∈ L(T ), then necessarily r(T ) = 2 : otherwise, u together with two other
members of L(T ) would be the centers of a copy of S3, by Lemma 3.1 . Therefore, additionally
using ( 6), we have
|U ∩ S| d12
N 2 ≪
∑
u∈U ∩S
Cu ≤ 2|TS| ≪ N 3
d .
Summing over the two bipartition classes gives
|U | ≪ N 5
d13 . (7)
We claim that U is a vertex cover of B. Otherwise, there would be an edge uv ∈ E(B) with
u, v / ∈ U . Choose a copy of S3 having u as a center and a copy of S3 having v as a center.
Together with the edge uv, these copies form an admissible quotient of K0, and hence give a
member of K, contrary to the choice of B. Thus, every edge of B meets U .
By Lemma 3.3 we have ∆(B) ≪ N
d2 . Since U is a vertex cover, ( 7) implies
N d ≤ 2e(B) ≤ 2|U |∆(B) ≪ N 6
d15 .
Therefore d16 ≪ N 5, which is a contradiction provided that C ≥ 1 is a suﬃciently large
constant. □
4. The generalized-quadrangle witnesses
We now proceed to the lower bound side of Theorem 1.1 . Since the required constructions
already appear in the literature (e.g. [ PT09] and [ BHKT18]), we keep the proof brief.
Let q be a prime power, let V = F4
q, and ﬁx a nondegenerate alternating bilinear form
⟨·, ·⟩ : V × V − →Fq.
The symplectic generalized quadrangle W (q) has point and line classes
P = {P ≤ V : dim P = 1} and M = {M ≤ V : dim M = 2, ⟨M, M ⟩ = 0},
with incidence given by containment. Let
Iq := I(W (q))
denote its bipartite incidence graph: its vertex set is P ⊔ M, and P ∈ P is adjacent to M ∈ M
precisely when P ⊆ M . This is the standard symplectic construction of W (q); see [ PT09, §3.2.1]
and [ BHKT18, §4].
The quadrangle has order (q, q): every point lies on q + 1 lines, every line contains q + 1
points, and
|P| = |M| = (q + 1)(q2 + 1).
Its incidence graph has girth eight [ PT09, §1.1, §1.2.1, and §3.1.1]. Consequently,
nq = 2(q + 1)(q2 + 1), e q = (q + 1)2(q2 + 1) ≥ 2−4/ 3n4/ 3
q . (8)
For S ∈ {P , M}, retain the common-neighbor graph RS, the sets L(T ), and the quantities
r(T ) from the preceding section, with B = Iq. Explicitly, for distinct vertices in the same
bipartition class,
P ∼ P ′ ⇐ ⇒ ⟨ P, P ′⟩ = 0 ( P, P ′ ∈ P ),
239
===== PAGE 242 =====
and
M ∼ M ′ ⇐ ⇒ M ∩ M ′ ̸= {0} (M, M ′ ∈ M).
We will also use two classical facts. The dual generalized quadrangle W (q)D is isomorphic to
the parabolic quadrangle Q(4, q), and W (q) is self-dual when q is even [ PT09, §3.2.1]; see also
[BHKT18, §4].
Deﬁnition 4.1 (Local patterns) . A J-pattern in S consists of independent triples {x, y, z} and
{x′, y, z}, each with at least two common centers, such that x ∼ x′. An S3-pattern in S is an
RS-independent triple with at least three common centers.
A member of J forces a J-pattern in one bipartition class, while a member of K forces an
S3-pattern in both bipartition classes.
Proposition 4.2 (Quadrangle witnesses) . For even q, Iq is J -free; for odd q, it is K-free. In
either case, it contains no C4 or C6.
Proof. Let y, z ∈ P be noncollinear, and put U = y + z. Since y and z are not orthogonal,
U is a nondegenerate two-dimensional subspace of V . Their common centers are precisely the
projective points of U ⊥. If a third point x has at least two common centers with y, z, then x is
orthogonal to two distinct projective points of U ⊥, and therefore to all of U ⊥. Hence,
x ⊆ (U ⊥)⊥ = U.
Any two distinct projective points of the nondegenerate symplectic plane U are nonorthogonal.
Therefore, any two possible third bases are unrelated, and P contains no J-pattern.
If q is even, the self-duality of W (q) [PT09, §3.2.1] gives the same conclusion for M. Thus,
neither bipartition class contains a J-pattern, and Iq is J -free.
If q is odd, identify M with the point class of the dual quadrangle Q(4, q). Every triad in
Q(4, q) has either zero or two centers [ BHKT18, Proposition 4.5]; see also [ PT09, §1.3.6(iii) and
§3.3.1]. Consequently, M contains no S3-pattern, and therefore Iq is K-free.
Finally, the girth-eight property excludes C4 and C6. □
Proposition 4.3 (Individual lower bounds) . For every F ∈ F ,
ex(n, F ) = Ω( n4/ 3).
Proof. If F ∈ { C4, C6} ∪ J , take q = 2 j; if F ∈ K , take q = 3 j. In either case, Proposition 4.2
makes Iq F -free. For t ∈ {2, 3},
ntq = 2(tq + 1)(t2q2 + 1) ≤ t3nq.
Choose the largest admissible q for which nq ≤ n. The displayed inequality gives nq ≫ n.
Padding Iq with isolated vertices preserves F -freeness, since F is connected and contains an
edge. Hence, ( 8) gives
ex(n, F ) ≥ eq ≫ n4/ 3. □
Proof of Theorem 1.1. The family in ( 4) is ﬁnite and nonempty, and each of its members is
connected, bipartite, and contains a cycle. Propositions 3.4 and 4.3 give ( 2); in particular, ( 1)
cannot hold for any F ∈ F . □
5. A binary entropy inequality
We now proceed to the proof of Theorem 1.2. The graph H consists of layers L1, L2, . . . , with
every vertex in Li having two parents in Li−1. The host graph is a variant of the Hamming cube
in which points at most a ﬁxed linear distance apart are adjacent. This construction naturally
leads to the entropy inequalities considered in this section.
All logarithms and entropies are to base two. Write
h(x) := −x log2 x − (1 − x) log2(1 − x), h (0) = h(1) = 0 ,
and put
κ := 3
2 − 3
4 log2 3.
240
===== PAGE 243 =====
The following inequality converts a bound on the average disagreement between a child and
its parents into a bound on its conditional entropy.
Lemma 5.1 (Independent-parent entropy). Let X, Y be independent Bernoulli variables with
common parameter q, and let Z be any jointly distributed binary variable. Write
v = P(Z = 1), d = P(X ̸= Z) + P(Y ̸= Z)
2 .
Then
H(Z | X, Y ) ≤ κ + (log2 3)d + h(v) − h(q)
2 . (9)
Proof. For a probability vector (r0, r1) and nonnegative numbers t0, t1, the Gibbs inequality
gives
−
∑
z∈{0, 1}
rz log2 rz +
∑
z∈{0, 1}
rz log2 tz ≤ log2(t0 + t1). (10)
Indeed, after writing T = t0 + t1, the diﬀerence between the right-hand and left-hand sides is
∑
z∈{0, 1}
rz log2
( rz
tz/T
)
≥ 0.
Put
c(x, y, z) = 1x̸=z + 1y̸=z
2 , π z = P(Z = z).
For ﬁxed x, y, apply ( 10) with
rz = P(Z = z | X = x, Y = y), t z = √πz 3−c(x,y,z ).
A veraging overX, Y gives
H(Z | X, Y ) − h(v)
2 − (log2 3)d ≤ E log2
( 1∑
z=0
√πz 3−c(X,Y,z )
)
. (11)
It remains to bound the right-hand side. Set
a =
√
1 − v, b = √v, u = 2q − 1,
so that a2+b2 = 1. The three possible types for {X, Y }, namely 00, 11, and 01, have probabilities
α0 = (1 − u)2
4 , α 1 = (1 + u)2
4 , α ∗ = 1 − u2
2 ,
and give respective expressions
t0 = a + b
3 , t 1 = a
3 + b, t ∗ = a + b√
3 .
Thus, after adding h(q)/ 2, the right-hand side of ( 11) becomes
F = 1
2 h(q) + α0 log2 t0 + α1 log2 t1 + α∗ log2 t∗.
Since
log2 t ≤ log2 λ + (log2 e)
( t
λ − 1
)
(t, λ > 0),
we have
log2
(
a + b
3
)
≤ log2
( 4
3
√
2
)
+ (log2 e)
(
3
√
2
4
(
a + b
3
)
− 1
)
,
log2
( a
3 + b
)
≤ log2
( 4
3
√
2
)
+ (log2 e)
(
3
√
2
4
( a
3 + b
)
− 1
)
,
log2
( a + b√
3
)
≤ log2
( √
2
3
)
+ (log2 e)
( a + b√
2 − 1
)
.
241
===== PAGE 244 =====
Multiplying these inequalities by
α0 = (1 − u)2
4 , α 1 = (1 + u)2
4 , α ∗ = 1 − u2
2 ,
respectively, and summing, gives
α0 log2
(
a + b
3
)
+ α1 log2
( a
3 + b
)
+ α∗ log2
( a + b√
3
)
≤ 1 − 3
4 log2 3 + u2
4 log2
4
3
+ (log2 e)
( (2 − u)a + (2 + u)b
2
√
2 − 1
)
≤ 1 − 3
4 log2 3 + u2
4 log2
4
3 + (log2 e)


√
1 + u2
4 − 1

,
where the ﬁnal inequality follows from Cauchy–Schwarz and a2 + b2 = 1.
Therefore
F ≤ 1
2 h
( 1 + u
2
)
+ 1 − 3
4 log2 3 + u2
4 log2
4
3 + (log2 e)


√
1 + u2
4 − 1

. (12)
A direct optimization shows that the right-hand side of ( 12) is maximized at u = 0 , where it
equals κ. Together with ( 11), this proves ( 9). □
In the layered construction, the two parents are sampled without replacement. The resulting
error vanishes as the layer size tends to inﬁnity.
Lemma 5.2 (Without-replacement correction) . Let L ≥ 4, let x1, . . . , x L ∈ {0, 1}, and sample
an ordered pair of distinct indices uniformly. Let X, Y be the corresponding bits, and let Z have
any conditional binary law given X, Y . Put
q = 1
L
L∑
a=1
xa, v = P(Z = 1), d = P(X ̸= Z) + P(Y ̸= Z)
2 .
Then
H(Z | X, Y ) ≤ κ + (log2 3)d + h(v) − h(q)
2 + η(L),
where
η(L) = O
( log2 L
L
)
= o(1)
uniformly over all choices of the bits and the conditional law of Z.
Proof. Couple sampling with and without replacement so that
P
(
(X, Y ) ̸= (X ′, Y ′)
)
≤ 1
L ,
where X ′, Y ′ are independent Bernoulli variables with parameter q. Give Z′, conditionally on
X ′, Y ′, the same conditional law used to deﬁne Z. Then
⏐⏐H(Z | X, Y ) − H(Z′ | X ′, Y ′)
⏐⏐≤ 1
L ,
while
|d − d′| ≤ 1
L , |v − v′| ≤ 1
L , |h(v) − h(v′)| ≤ h(1/L ).
Now apply Lemma 5.1 to (X ′, Y ′, Z′). □
242
===== PAGE 245 =====
6. The layered graph and the parameter thresholds
The construction depends on a Hamming radius τ ∈ (0, 1/ 2) and a sampling exponent β ∈
(0, 1). Deﬁne
A(τ) := κ + τ log2 3, C (τ) := 2h(τ) − 1.
The threshold A(τ) controls exclusion of the layered graph, while C(τ) controls whether the
sampled host has more than n3/ 2 edges.
For now, assume that
A(τ) < β < C (τ). (13)
We verify at the end that such parameters exist.
Choose
0 < δ < β − A(τ)
4 .
Since η(L) = o(1) and
( L
2
)
≍ L2, ﬁx L0 ≥ 4 suﬃciently large that, for every L ≥ L0,
η(L) < δ, L + 3 log2
((
L
2
)
+ 1
)
− δ
(
L
2
)
< −1. (14)
Then choose an integer s ≥ 2 such that
2s
(
β − A(τ) − 2δ
)
> 1. (15)
Take disjoint layers V0, . . . , V s with
|V0| = L0, V i =
(
Vi−1
2
)
(1 ≤ i ≤ s).
Join each vertex {a, b} ∈ Vi to its two parents a, b ∈ Vi−1, and let H be the resulting graph.
Writing
Li = |Vi|,
we have
Li =
(
Li−1
2
)
≥ Li−1 ≥ L0.
F act 6.1. The graph H is connected, bipartite, and 2-degenerate.
7. A sampled Hamming-ball graph
For m ≥ 1, put
U = {0, 1}m, Q = 2 m, p = 2 −βm, k = ⌊τ m⌋.
Take two disjoint copies UL, UR of U , joining vertices on opposite sides whenever their Hamming
distance is at most k. Independently retain each vertex with probability p, and write Gm for
the induced subgraph.
For a parent array
u = (ua)L
a=1 ∈ U L
and a child array
z = (z{a,b }){a,b }∈([L]
2 ) ∈ U M , M =
(
L
2
)
,
choose a uniformly random parent pair and orient it using an independent fair coin. In coordi-
nate j, denote the resulting parent and child bits by Xj, Yj, Zj, and deﬁne
E(u, z) := 1
m
m∑
j=1
H(Zj | Xj, Yj).
An array of conditional entropy E has at most 2mM E+O(m log2 M ) realizations, while requiring
its M children to survive sampling costs 2−βmM . Since M ≍ L2, this dominates the 2mL possible
parent arrays whenever E < β .
243
===== PAGE 246 =====
Lemma 7.1 (Exclusion of low-entropy arrays) . With probability at least 1 − 2s 2−m, simulta-
neously on both host sides and at every transition, there is no parent array of length Li−1 and
pairwise distinct retained child array of length Li satisfying
E(u, z) ≤ β − δ. (16)
Proof. Fix a host side, a transition, and a parent array. Write
L = Li−1, M = Li =
(
L
2
)
.
For each coordinate j, partition the parent pairs according to their bit types
G = {00, 11, 01},
where 01 includes both orientations of a mixed pair. Let Ng,j be the size of group g, and let
bg,j count its children having jth bit equal to one. Then
H(Zj | Xj, Yj) =
∑
g∈G
Ng,j
M h
(
bg,j
Ng,j
)
.
There are at most (M + 1) 3m possible proﬁles (bg,j )g,j . For a ﬁxed proﬁle, the number of
child arrays, allowing repeated words, is
m∏
j=1
∏
g∈G
(
Ng,j
bg,j
)
≤ 2mM E(u, z),
by the estimate (
N
r
)
≤ 2N h(r/N ).
Therefore, at most
(M + 1)3m2mM (β−δ)
child arrays satisfy ( 16).
For pairwise distinct children, the probability that they are all retained is
pM = 2 −βmM .
There are QL = 2 mL possible parent arrays, so ( 14) gives
P(a bad retained array ) ≤ QL(M + 1)3m2mM (β−δ)pM
= 2 m[L+3 log2(M +1)−δM]
≤ 2−m.
Take a union bound over both host sides and all s transitions. □
8. Excluding the forbidden graph
Proposition 8.1 (Exclusion of the layered graph) . With probability 1 − o(1), the sampled graph
Gm is H-free.
Proof. Assume the event in Lemma 7.1 , and suppose that
ι: H ↪→ Gm
is an embedding. Since H is connected and bipartite, consecutive layers occupy opposite sides
of the host.
For the parent and child arrays at transition i, write
Ei = E(ui, zi).
The children are distinct and retained, so Lemma 7.1 gives
Ei > β − δ. (17)
244
===== PAGE 247 =====
Deﬁne the entropy potential of layer i by
Φi = 1
m
m∑
j=1
h

1
Li
∑
z∈ι(Vi)
z(j)

.
Since binary entropy belongs to [0, 1],
0 ≤ Φi ≤ 1.
At transition i, let
dj = P(Xj ̸= Zj) + P(Yj ̸= Zj)
2 .
Every child is adjacent to both parents, and therefore
1
m
m∑
j=1
dj = 1
2mLi
∑
{a,b }∈(Vi−1
2 )
(
dist(ua, z{a,b }) + dist(ub, z{a,b })
)
≤ k
m ≤ τ.
Applying Lemma 5.2 in each coordinate and averaging gives
Ei ≤ A(τ) + Φi − Φi−1
2 + η(Li−1). (18)
Combining ( 17), ( 18), and ( 14), we obtain
Φi − Φi−1 > 2
(
β − A(τ) − 2δ
)
.
Hence, ( 15) gives
Φs − Φ0 > 2s
(
β − A(τ) − 2δ
)
> 1,
contradicting 0 ≤ Φi ≤ 1. Therefore,
P(H ⊆ Gm) ≤ 2s 2−m = o(1). □
Proof of Theorem 1.2. Continue assuming ( 13); the existence of suitable parameters will be
checked at the end.
Put
Dm =
⌊τ m⌋∑
j=0
(
m
j
)
.
The standard Hamming-ball estimate gives
Dm = 2 (h(τ)+o(1))m.
For
Wm = |V (Gm)|, e m = e(Gm),
we have
EWm = 2pQ, Var(Wm) ≤ 2pQ,
and
Eem = p2QDm, Var(em) ≤ p2QDm + 2p3QD2
m.
Since β < C (τ) < 1,
pQ = 2 (1−β)m − → ∞
and
p2QDm = 2 (1+h(τ)−2β+o(1))m − → ∞.
Consequently,
Wm ≤ 3pQ, e m ≥ 1
2 p2QDm
with probability 1 − o(1).
Combining these estimates with Proposition 8.1 , and padding with isolated vertices, gives
ex(Nm, H) ≥ 1
2 p2QDm, N m =
⌈
3 · 2(1−β)m
⌉
.
245
===== PAGE 248 =====
Moreover,
1 + h(τ) − 2β
1 − β = 3
2 + 2h(τ) − 1 − β
2(1 − β)
= 3
2 + C(τ) − β
2(1 − β) > 3
2 .
Therefore, for any ﬁxed
0 < ε < C(τ) − β
2(1 − β) , (19)
we have
ex(Nm, H) ≥ N 3/ 2+ε
m
for all suﬃciently large m.
Since 21−β < 2,
Nm+1 ≤ 2Nm.
Thus, for every suﬃciently large n, there is an m such that
Nm ≤ n < N m+1 ≤ 2Nm.
Padding once more gives
ex(n, H) ≥ ex(Nm, H) ≥ 2−3/ 2−εn3/ 2+ε.
It remains to verify that the parameter window ( 13) is nonempty. Its width is
f (τ) = C(τ) − A(τ) = 2 h(τ) − 1 − κ − τ log2 3.
Since
f ′(τ) = 2 log 2
( 1 − τ
τ
)
− log2 3,
the strictly concave function f is maximized at
τ = 1
1 +
√
3 .
Set r =
√
3. At this value of τ,
2h(τ) − τ log2 3 = 2 log 2
(
1 + 1
r
)
,
while
κ = 1
2 + 1
2 log2(1 + r2) − 3
2 log2 r.
Hence,
f (τ) = 1
2 log2
(
(1 + r)4
8r(1 + r2)
)
= 1
2 log2
(
1 + (r − 1)4
8r(1 + r2)
)
> 0.
We may therefore choose any
A(τ) < β < C (τ),
and subsequently any ε satisfying ( 19). The remaining assertions follow from Fact 6.1 . □
246
===== PAGE 249 =====
References
[AKS03] N. Alon, M. Krivelevich, and B. Sudakov, Turán numbers of bipartite graphs and related
Ramsey-type questions , Combin. Probab. Comput. 12 (2003), 477–494, https://doi.org/10.1017/
S0963548303005741.
[BHKT18] D. Bartoli, T. Héger, G. Kiss, and M. Takáts, On the metric dimension of aﬃne planes, biaﬃne
planes and generalized quadrangles , Australas. J. Combin. 72 (2018), 226–248, https://ajc.maths.
uq.edu.au/pdf/72/ajc_v72_p226.pdf.
[Blo113] T. F. Bloom, Erdős problem #113 , https://www.erdosproblems.com/113.
[Blo146] T. F. Bloom, Erdős problem #146 , https://www.erdosproblems.com/146.
[Blo180] T. F. Bloom, Erdős problem #180 , https://www.erdosproblems.com/180.
[Blo575] T. F. Bloom, Erdős problem #575 , https://www.erdosproblems.com/575.
[BJST23] D. Bradač, O. Janzer, B. Sudakov, and I. Tomon, The Turán number of the grid , Bull. Lond. Math.
Soc. 55 (2023), 194–204, https://doi.org/10.1112/blms.12721.
[BC18] B. Bukh and D. Conlon, Rational exponents in extremal graph theory , J. Eur. Math. Soc. 20 (2018),
1747–1757, https://doi.org/10.4171/JEMS/798.
[Con26] D. Conlon, Combinatorial theorems relative to sparse sets , manuscript, 2026; to appear in the Pro-
ceedings of the International Congress of Basic Science, available online.
[CMP26] D. Conlon, E. Mulrenin, and C. Pohoata, Two counterexamples to a conjecture about even cycles ,
2026, arXiv:2603.24515.
[DGL25] Z. Dong, J. Gao, and H. Liu, Bipartite Turán problems via graph gluing , Bull. Lond. Math. Soc. 57
(2025), 3783–3796, https://doi.org/10.1112/blms.70243.
[Erd67] P. Erdős, Some recent results on extremal problems in graph theory , in Theory of Graphs (International
Symposium, Rome, 1966), Gordon and Breach, New York, 1967, 117–123.
[Erd81] P. Erdős, Problems and results in graph theory , in The Theory and Applications of Graphs (Kalamazoo,
1980), Wiley, New York, 1981, 331–341, https://www.renyi.hu/~p_erdos/1981-20.pdf.
[Erd97] P. Erdős, Some of my favorite problems and results , in The Mathematics of Paul Erdős, I , Algorithms
Combin. 13, Springer, Berlin, 1997, 47–67, https://doi.org/10.1007/978-3-642-60408-9_3 .
[ES82] P. Erdős and M. Simonovits, Compactness results in extremal graph theory , Combinatorica 2 (1982),
275–288, https://doi.org/10.1007/BF02579234.
[Fur91] Z. Füredi, On a Turán type problem of Erdős , Combinatorica 11 (1991), 75–79, https://doi.org/10.
1007/BF01375476.
[FS13] Z. Füredi and M. Simonovits, The history of degenerate (bipartite) extremal graph problems ,
in Erdős Centennial , Bolyai Soc. Math. Stud. 25 (2013), 169–264, https://doi.org/10.1007/
978-3-642-39286-3_7 .
[GJN22] A. Grzesik, O. Janzer, and Z. L. Nagy, The Turán number of blow-ups of trees , J. Combin. Theory
Ser. B 156 (2022), 299–309, https://doi.org/10.1016/j.jctb.2022.05.004.
[Jan23] O. Janzer, Disproof of a conjecture of Erdős and Simonovits on the Turán number of graphs with
minimum degree 3 , Int. Math. Res. Not. 2023 (2023), 8478–8494, https://doi.org/10.1093/imrn/
rnac076.
[PT09] S. E. Payne and J. A. Thas, Finite Generalized Quadrangles , 2nd ed., EMS Series of Lectures in
Mathematics 9, European Mathematical Society, 2009, https://doi.org/10.4171/066.
[Ver16] J. Verstraëte, Extremal problems for cycles in graphs , in Recent Trends in Combinatorics , IMA Vol.
Math. Appl. 159, Springer, Cham, 2016, 83–116, https://doi.org/10.1007/978-3-319-24298-9_4 .
[Wig] Y. Wigderson, The Erdős–Simonovits compactness conjecture needs more assumptions , https://
ywigderson.math.ethz.ch/math/static/Compactness.pdf.
247