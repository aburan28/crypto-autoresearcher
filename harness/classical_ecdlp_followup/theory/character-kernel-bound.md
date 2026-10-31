# A coarse fifth-character bound for a single doubling/translation step

25 October 2026. Data-free mathematical follow-up selected after the pilot. This note supplies a proof map for one fixed feature; it changes no frozen experiment, threshold, decoder or recorded result. It is same-session work, not independent review or a novelty claim. No scientific measurements were run for this note.

The conclusion is a population bound on the five nonzero fifth-residue classes of two public coordinates. With bounded cofactor parameter h, the joint distribution conditioned on both coordinates being finite and nonzero approaches uniform product at order p^(-1/2), and its conditional entropy deficit is O(1/p). The explicit constants below are deliberately loose. Exceptional coordinate symbols require a separate correction. This is not an ECDLP lower bound.

## Assumptions and statement

Let p>3 be prime, with p=1 modulo 5, and let

`E/Fp: y^2 = x^3 + A*x + B`

be nonsingular. Initially assume B is nonzero. Let h>=1 be an integer prime to p, let N=#E(Fp), and suppose H=[h]E(Fp) has order r. In the intended experiment r is prime and H=<P>; the argument itself only needs the stated image and a rational point P in H. Write

`T_b(X) = [2]X + [b]P`, for b in {0,1}.

Fix a multiplicative character chi:Fp* -> mu_5 of exact order five. Such a character exists because 5 divides p-1. Fix a primitive complex fifth root zeta and define labels by chi(x)=zeta^U, with U in {0,...,4}. The Fourier exponents below use this cyclic labeling. The implementation's value x^((p-1)/5), including its sorted numerical labels, is the same five-class partition up to a permutation; entropy and cell-probability conclusions are invariant under that relabeling. Logs and entropies below are in bits. Conditioning on G_b in displayed character and entropy expressions always means conditioning on the event G_b=1, rather than averaging over its two indicator values.

For X uniform in H, let G_b be the event that x(X) and x(T_b(X)) are both finite and nonzero. Define q_b=Pr(G_b) and epsilon_b=1-q_b. When q_b>0, let (U,V) be the pair of fifth-character labels conditioned on G_b. Set

`Gamma_h(p) = (60*h^2 + 2)*sqrt(p) + 75*h^2`,

`eta_b = min(1, Gamma_h(p)/(N*q_b))`.

Then epsilon_b<=min(1,15/r), and, for every (a,c) in {0,...,4}^2 other than (0,0),

`| E[ chi(x(X))^a * chi(x(T_b(X)))^c | G_b ] | <= eta_b`.       (1)

Consequently, with p_uv=Pr(U=u,V=v | G_b),

`|p_uv - 1/25| <= 24*eta_b/25`,                              (2)

`|p_u - 1/5| <= 4*eta_b/5`,                                 (3)

and the same marginal bound holds for V. In particular,

`|p_uv - p_u*p_v| <= (32*eta_b + 16*eta_b^2)/25`.             (4)

The information and conditional entropy bounds are

`I(U;V | G_b) <= 24*eta_b^2/ln(2)`,

`0 <= log2(5) - H(V | U,G_b) <= 24*eta_b^2/ln(2)`.            (5)

Use the trivial alphabet-size bound whenever these expressions are larger. If h is bounded, q_b stays bounded away from zero, and p grows, (2)--(4) are O(h^2/sqrt(p)) and (5) is O(h^4/p). Calling the latter O(1/p) requires bounded h. No numerical usefulness at the toy sizes follows from this loose bound.

## Geometric non-fifth-power certificate

Work first over the algebraic closure of Fp. This is necessary: a single geometric valuation obstructs a geometric fifth power even when its point is not rational. The rational function x on E has its only pole at O, of order two, and its zero support has at most two points. For B!=0 the two zeros are (0,+sqrt(B)) and (0,-sqrt(B)), each simple. Thus its zero/pole support S has at most three geometric points.

For a,c in {0,...,4}, not both zero, consider

`F_(a,c,b)(X) = x(X)^a * x(T_b(X))^c`.

These functions are not fifth powers, even up to multiplication by a nonzero constant. A valuation of a fifth power has order divisible by five, whereas the following cases exhibit an order that is not divisible by five.

1. If c=0, then a!=0 and ord_O(F)=-2a, which is not divisible by five.
2. If c!=0 and b=0, multiplication by two is étale of degree four. The poles of x([2]X) are exactly the four points of E[2], with order two at each. At any nonzero point of E[2], the coordinate x is finite, and B!=0 ensures x!=0. There is therefore no zero or pole from x(X)^a at that point, and ord(F)=-2c.
3. If c!=0 and b=1, the poles of x([2]X+P) are the four distinct geometric solutions of [2]X=-P, again with order two. A four-element set cannot be contained in S, whose size is at most three. At a pole outside S the valuation is exactly -2c. This covers all rational P, including special coincidences between other poles and zeros; cancellation elsewhere cannot cancel this witness.

All uses of four distinct preimages require p!=2. There is no assumption that these preimages are Fp-rational. The B!=0 restriction is sufficient, not a hidden exceptional attack class: if B=0 and the curve is nonsingular, A!=0, and two of the three nonzero two-torsion points still have nonzero x. Choosing one of those gives case 2. The support bound remains at most three, so the same proof actually extends to B=0. We do not need that extension for the stated main assumption.

Now pull back by multiplication by h:

`f = F_(a,c,b) o [h]`.

The map [h] is étale and has degree h^2 because p does not divide h. At any preimage of a witness point the valuation of f is unchanged: the ramification index is one. Thus f still has a valuation prime to five. It is not enough merely to say that F was not a fifth power; preservation under pullback uses étaleness here.

The union of the zero/pole supports of x and x o T_b has at most 3+4*3=15 geometric points. Its pullback by [h] has at most 15h^2 points. Cancellation in F can reduce this support; it cannot increase it or remove the witness already established.

## Connected Kummer covers and their genus

This section derives the cover conditions rather than assuming a character-sum theorem with unchecked hypotheses. Let K=overline(Fp)(E), choose a root z of z^5=f, and extend a witness valuation v with n=ord_v(f) prime to five to a normalized valuation w of K(z). If e is its ramification index, then

`5*w(z) = e*n`.

Therefore 5 divides e. But e<= [K(z):K] <=5, so both e and the field degree equal five. In particular Z^5-f is irreducible over K. Since p!=5, this is a separable extension. It gives a geometrically integral degree-five cover; its smooth projective normalization exists over Fp. The algebraic closure contains mu_5, so the geometric extension is cyclic.

At any geometric base point with ord(f) not divisible by five the same calculation gives ramification index five. If ord(f)=5n, write f=s^(5n)*u for a local parameter s and a unit u. After replacing z by z/s^n, the local equation is z^5=u. Here z and the derivative 5z^4 are units, so this algebra is étale. Its normalization has no ramification at that point. This checks that the only ramification is the stated full ramification, and it is tame.

Let m be the number of geometric base points where ord(f) is not divisible by five. We have m<=15h^2. Tame Riemann--Hurwitz, with genus-one base, gives

`2*g_C - 2 = 5*(2*1-2) + 4*m`,

so

`g_C = 1 + 2*m <= 1 + 30*h^2`.                              (6)

The same statements hold for every twist C_t given by z^5=t*f, with t in Fp*. Twisting changes no geometric valuation and becomes an isomorphism after adjoining a fifth root of t. Thus all five twist classes are geometrically integral, have the same genus, and qualify for Hasse--Weil. No genus estimate based on the singular plane equation is being substituted for the normalization.

## A five-twist derivation of the character bound

Let D be the subset of E(Fp) lying over the union of the two original zero/pole supports under [h], let d=#D<=15h^2, and let Omega=E(Fp) minus D. This possibly excludes more points than the divisor support of f when cancellation occurs; excluding them consistently makes every character evaluation below well-defined.

For j=1,...,4, put

`S_j = sum_(Y in Omega) chi(f(Y))^j`.

Choose five representatives t for Fp*/(Fp*)^5. For each Y in Omega, the number of rational z satisfying z^5=t*f(Y) is

`1 + sum_(j=1..4) chi(t)^j * chi(f(Y))^j`.

Let R_t count rational points of the smooth projective C_t over D. Since a degree-five finite map has at most five geometric points in a fibre, 0<=R_t<=5d. Every rational point on C_t maps to a rational base point. Hence

`#C_t(Fp) = |Omega| + sum_(j=1..4) chi(t)^j*S_j + R_t`.

Fourier inversion over the five twist classes isolates S_j. The common |Omega| cancels, and so does p+1. Hasse--Weil and (6) therefore give the safe bound

`|S_j| <= (1/5)*sum_t |#C_t(Fp)-(p+1)| + (1/5)*sum_t R_t`

`       <= 2*g_C*sqrt(p) + 5*d`

`       <= (60*h^2+2)*sqrt(p) + 75*h^2 = Gamma_h(p)`.          (7)

The boundary term 5d is intentionally not sharpened. This derivation avoids invoking an unread specialized multiplicative-character theorem, and its cost is a large constant.

The finite group homomorphism [h]:E(Fp)->H has equal rational fibre sizes N/r. Consequently, for every function g on H,

`(1/N)*sum_(Y in E(Fp)) g([h]Y) = (1/r)*sum_(X in H) g(X)`.

Apply this identity with the summand zero off G_b and equal to the character monomial on G_b. The left-hand sum is S_1/N for f=F_(a,c,b) o [h]. There are at most 15 bad rational points already on H, so epsilon_b<=15/r. Dividing (7) by N*q_b proves (1). Neither the construction nor this argument needs the discrete logarithm of a sampled point. The prime-order assumption is not being used as a substitute for the equal-fibre argument.

## From character moments to entropy

Let zeta be a primitive complex fifth root of unity and set

`m_ac = E[zeta^(a*U+c*V) | G_b]`.

Here m_00=1, and all other 24 coefficients have magnitude at most eta_b by (1). Finite Fourier inversion gives

`p_uv = (1/25)*sum_(a,c=0..4) m_ac*zeta^(-a*u-c*v)`.

Taking absolute values proves (2). Marginalizing retains the four nontrivial coefficients with c=0, giving (3). Expanding p_u*p_v around 1/25 gives

`|p_u*p_v-1/25| <= 8*eta_b/25 + 16*eta_b^2/25`,

which with (2) proves (4).

For the stronger entropy scaling, use Parseval instead of a linear continuity bound. If U_25 denotes uniform product on the 25 pairs, then

`chi_square(p || U_25) = 25*sum_(u,v)(p_uv-1/25)^2`

`                         = sum_((a,c)!=(0,0)) |m_ac|^2`

`                         <= 24*eta_b^2`.

The elementary inequality ln(t)<=t-1 gives D_KL(p||U_25)<=chi_square(p||U_25)/ln(2). The usual finite-sum identities, with all distributions conditioned on G_b, are

`D_KL(p_UV || U_25) = I(U;V) + D_KL(p_U||U_5) + D_KL(p_V||U_5)`,

`log2(5)-H(V|U) = D_KL(p_UV||U_25)-D_KL(p_U||U_5)`.

Nonnegativity of the subtracted/divided terms proves (5). These bounds need no lower bound on individual cell probabilities because the reference distribution is uniform and strictly positive.

For a bulk kernel defined using this jointly conditioned law, one can also obtain a row bound when eta_b<1/4. The Fourier expansion of p_uv-p_u/5 retains twenty terms and gives magnitude at most 4*eta_b/5. Since p_u>=(1-4*eta_b)/5,

`|Pr(V=v|U=u,G_b)-1/5| <= 4*eta_b/(1-4*eta_b)`.

Its Dobrushin coefficient is at most min(1,20*eta_b/(1-4*eta_b)). This concerns the conditioned five-class channel. It does not bound the maximum row distance of the experiment's full alphabet, nor does conditioning on future nonexceptional output produce the same kernel as retaining all seven symbols.

## Identity and zero symbols cannot be silently discarded

Let U_full,V_full be the full feature with separate symbols for O and finite x=0, in addition to the five nonzero residue classes. The good event G_b is determined by the pair (U_full,V_full). Its complement has mass epsilon_b<=15/r. The entropy chain rule gives exactly

`H(V_full|U_full) = H(G_b|U_full)`

`  + (1-epsilon_b)*H(V|U,G_b=1)`

`  + epsilon_b*H(V_full|U_full,G_b=0)`.

It follows, with h2 the binary entropy, that

`|H(V_full|U_full)-H(V|U,G_b=1)| <= h2(epsilon_b) + epsilon_b*log2(7)`.

Also

`I(U_full;V_full) <= h2(epsilon_b)`

`  + (1-epsilon_b)*I(U;V|G_b=1) + epsilon_b*log2(7)`.

Thus an unconditional entropy statement needs at least this explicit rare-event allowance under the present proof. In the common N=hr regime with bounded h, the crude allowance is O(log(p)/p), rather than O(1/p). Removing that logarithm would require an additional calculation; it is not supplied here.

The rare rows also matter for worst-case contraction. For example, conditioning the input on O pins the exact next point to [b]P. Such a row can be deterministic even though it occurs with probability 1/r. A small average information gap does not force the full maximum-row Dobrushin coefficient to be small. Population bulk decorrelation, learned smoothed rows and floating numerical contraction diagnostics are separate objects.

## A separate ceiling from the decoder's target interface

This elementary counting statement does not use the character bound. Fix a target index and condition on public preprocessing, training samples, random/tie seeds and offset points R_1,...,R_m, collectively W. Assume W is independent of a uniform scalar k in {0,...,r-1}. In particular, choosing the offset seeds from a target ordinal is allowed when that ordinal was assigned independently of k. No independence between the R_i themselves is needed for this lemma.

Suppose the scalar candidate list before verification can depend on Q=[k]P only through the signature

`s(Q) = (phi(Q+[2^ell]R_1),...,phi(Q+[2^ell]R_m))`,

where phi has at most d possible labels. Let every such list contain at most B distinct canonical scalars. Arbitrary preprocessing independent of Q is allowed, and all prefix calculations from P,R_i and proposed scalar bits are allowed. The candidate's success after its post-hoc full-point verification then satisfies

`Pr(success | W) <= min(1, B*d^m/r)`.                       (8)

To prove this, partition the r possible scalars by their signatures. There are at most d^m nonempty parts. For any fixed signature s, the algorithm produces one fixed list L_s after conditioning on W. At most B of the scalars in that part belong to L_s. The union of all successful scalars therefore has size at most B*d^m; divide by r. The full point equation [k_candidate]P=Q certifies which guesses succeeded but cannot add guesses to a list already formed. Averaging over W proves the same unconditional bound. Randomized preprocessing is included by conditioning on all of its independent coins.

The source inspection supporting application to the present interface is specific and limited. In `src/decoder.cpp`, inspected 25 October 2026, `make_views` derives view seeds from fixture/feature seeds and target ordinal, samples R, and makes the four shifted targets. `search` receives the start and terminal feature labels; its exact-prefix context contains R and an advance function using only doubling and the public P. `emit_target` constructs the list before comparing each candidate's full point with Q. The `run` membership-validation predicate accepts every valid subgroup target, so its boolean outcome distinguishes no scalar within the intended valid-target population. Operation counters, logged shifted coordinates and validation arithmetic are not used as search inputs in these inspected call boundaries. This is a source-interface check, not an OS blindness claim or a formal audit of the full toolchain.

For either the model-prefix or exact-public-prefix configuration, the current per-feature alphabet has d<=8, m=4 and beam budget B<=8. Thus (8) is at most min(1,32768/r). The bound is vacuous at the current toy subgroup sizes, including 12-bit r. With fixed d,m,B it prevents a constant limiting recovery rate as r grows in this restricted interface. It is not a lower bound for algorithms that can use more information from Q. For the constant feature, d=1 and the actual list is independent of k, so a list of exactly n distinct guesses has success probability exactly n/r; this equals B/r when n=B.

Equation (8) is per specified feature, prefix mode and beam configuration. Combining configurations requires counting the combined signature and the total guesses; applying the single-configuration bound to an aggregate success count would be unjustified. The uniform-target assertion is a population probability model: it is not a statement that one fixed public target manifest remains random after all of its generation inputs are fixed. No extra randomness or independence is inferred merely from the use of a reproducible PRNG.

Allowing d, m or B to grow, reading richer functions of Q, or making additional target-dependent observations changes the interface and can escape this fixed-parameter ceiling. More target-independent training alone cannot change the number of signatures, although it can change which B guesses are selected in each part. The lemma therefore does not imply a lower bound on the amount of training needed, and establishes no ECDLP lower bound.

## Scope and outstanding obligations

This argument supports a narrow possible explanation for weak fifth-residue unary channels. It supplies no direction to retune the frozen decoder. It does not close the existing probabilistic propagation lead.

* It treats one fixed order-five multiplicative-character partition of x and one public map X->[2]X+[b]P. It does not treat x modulo 7, an arbitrary public x hash, an alphabet growing with p, or algorithms using full coordinates.
* It bounds the uniform subgroup population. Finite-sample kernel estimation, pseudocount effects, calibrated log loss and dependence from a particular pseudorandom sampler require their own analysis.
* A nearly uninformative one-step population channel does not establish an exact coarse Markov process after conditioning on a prefix history, an endpoint, or several offset views. It supplies no posterior bound for either the model-prefix or exact-public-prefix beam decoder.
* The scale experiment's pair statistic H(phi(X+Y)|phi(X),phi(Y)), for independent X,Y, lives on E times E. It is not this unary character sum. Its matched-null entropy gap is not bounded by (5) without a separate argument matching its probability model.
* No sample-size requirement such as N_train=Omega(r) follows from an upper bound on a signal. An information-theoretic testing lower bound would need specified alternative distributions, divergences, observations, dependence assumptions and a minimax or prior model. Upper-bounding a bias alone does not supply those hypotheses.
* No generic-group restriction, classical ECDLP complexity lower bound, scalar-bit unpredictability theorem or novel algorithm is established. The elementary divisor application may already be standard; this note is not a priority search.

The mathematical dependencies are standard and explicit: the multiplication maps' degree and étaleness; smooth projective normalization of a separable one-variable function field over a perfect field; local valuation/étale facts; tame Riemann--Hurwitz; Hasse--Weil; and finite Fourier/entropy identities. The divisors, connectedness, ramification count, genus bound, five-twist extraction, subgroup normalization and entropy estimates are derived above. No specialized character-sum result is asserted on the strength of an inaccessible source. This is an ordinary mathematical derivation using those external theorems, not a formal proof-assistant certificate.

## Sources and reading depth

Retrieved 25 October 2026. These are first-party reference texts; the historical original proofs of Weil's theorem were not audited here. No source is quoted at length.

1. [The Stacks Project, Lemma 39.9.8, tag 0BFG](https://stacks.math.columbia.edu/tag/0BFG). Read the statement and proof: multiplication by d on a dimension-g abelian variety is finite locally free of degree d^(2g). For E this gives degree h^2, and for doubling degree four.
2. [The Stacks Project, Lemma 39.9.9, tag 0BFH](https://stacks.math.columbia.edu/tag/0BFH). Read the statement and proof: multiplication by d is étale exactly when d is invertible in the ground field. This checks both pullback preservation and distinct geometric doubling preimages.
3. [The Stacks Project, Section 53.12, tag 0C1B](https://stacks.math.columbia.edu/tag/0C1B). Read the formula and tame-ramification discussion, including Lemma 53.12.4's criterion. The different contributes e-1 in the tame case. Here all nontrivial ramification indices are five and p!=5, so the displayed genus computation uses the applicable tame formula.
4. [John Voight, *Curves over finite fields with many points: an introduction*](https://jvoight.github.io/articles/pointscurves-moscow.pdf), dated 5 May 2005, Section 2.1, Theorem 2.1 and Corollary 2.2, printed pages 3--4. Read the smooth/geometrically integral projective-curve scope and the zeta-root statement |alpha_i|=sqrt(q), which gives |#C(Fp)-(p+1)|<=2g*sqrt(p). This is an author-hosted survey statement of the standard theorem, not a claim to have checked Weil's original proof. Its cover hypotheses were checked above before using it.

No campaign output, target truth labels or measured entropy values enter any constant or assumption in this note. Selection after the pilot is disclosed; there is no retrospective claim that this derivation preregistered a quantitative result for the follow-up.
