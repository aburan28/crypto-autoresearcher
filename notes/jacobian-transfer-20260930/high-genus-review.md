---
title: "High-genus Jacobian review: existence, computation, and secrecy"
record_kind: draft_literature_and_mathematical_review
added: "2026-09-30"
reviewed_commit: "6ee050827103049fb7bec95e61e315d95e7ccbbe"
canonical_review: false
research_state_transition: false
dlp_runs: 0
map_constructions: 0
---

# High-genus Jacobian review

The scoped dimension obstruction survives this review. Abstract existence of a
Jacobian having the required abelian factor is supported by a published general
theorem. Neither a practical subgroup transfer nor a computational advantage
for the selected Koblitz families follows. Public recoverability of any useful
alternative correspondence remains a separate, unresolved question.

This addendum reviews the draft at the commit above without replacing its
historical contents. `independent-review.md` records an independent agent's
mathematical check, including procedural limits. This is not a canonical
claim-changing review, validated finding, or goal closure.

## Model and scope

An isogeny preserves dimension. Thus an elliptic curve cannot be isogenous to
an entire high-genus Jacobian. The model assessed here is a secret isogeny
between elliptic curves over F_(2^n), followed by a separate descent or
correspondence involving a Jacobian over F_2. A map into a higher-dimensional
Jacobian need not be an isogeny onto that entire Jacobian.

The original derivation concerns the two standard binary Koblitz families,
mu in {-1,+1}, and n in {31,53,83,131}. It constrains homomorphisms of abelian
varieties defined over F_2. It does not constrain every abstract finite-group
homomorphism, every curve family, or maps over other fields. No exact challenge
curve UID or subgroup was introduced by this review.

## Claims after review

| Question | Supported result | Remaining boundary |
| --- | --- | --- |
| Must a subgroup-carrying Jacobian be large? | g >= n-1 in this geometric setting | A necessary condition, not a construction |
| Can g=n-1 occur for mu=+1? | No: the forced counts are 4 over F_2 and 2 over F_4 | Larger Jacobians can have additional factors |
| Can g=n-1 be hyperelliptic for mu=-1? | No: the forced F_4 count is 2, but a hyperelliptic curve over F_2 has at least 3 F_4 points | Does not exclude nonhyperelliptic Jacobians at that dimension |
| Does some Jacobian have A as an isogeny factor? | Yes, by general finite-field Jacobian-covering existence results | Does not fix genus near n-1, special model, efficient evaluation, or the chosen subgroup |
| Is the destination DLP substantially easier here? | Unestablished | No destination curve, usable map, or matched total-cost comparison |
| Can a useful advantage remain hidden? | Unestablished separately | Public class invariants persist; specific endpoints or paths need not be determined by them |

For n=131, a general destination requires g>=130, with g=130 excluded for
mu=+1. A hyperelliptic destination requires g>=131 for both signs. These lower
bounds do not assert existence at genus 130 or 131.

## Two arguments made explicit

For the reverse map f:J_C->W, set B=im(f). Its Frobenius polynomial divides
P_W=P_E*P_A. Since P_A is irreducible and has degree 2(n-1), dim(B)<n-1
forces B to be zero or isogenous to E. Such a B has 1, 2, or 4 F_2-rational
points, so B(F_2) cannot contain an odd-prime-order subgroup. This proves the
reverse dimension bound without assuming surjectivity on rational points or
an actual direct product decomposition of W(F_2).

If E'/F_(2^n) is isogenous to E but does not descend to F_2, define
W'=Res(E'). Restriction of scalars gives W'~W. Let A' be its large simple
isotypic subvariety, with elliptic quotient Q=W'/A'~E. Since Q(F_2) has 2 or
4 points, every odd-prime-order subgroup of W'(F_2) lies in A'(F_2). This
does not require a trace map from W' to an elliptic curve E'/F_2. An actual
secret isogeny's restriction to the chosen subgroup still needs a kernel
check; a shared Weil polynomial alone is insufficient.

## Exact-dimension hyperelliptic obstruction

This refinement was proposed by the root agent during review and checked by
the independent agent; it was not a blinded rederivation by that agent.

For a smooth projective geometrically connected hyperelliptic C/F_2 of genus
at least 2, the unique hyperelliptic involution descends, and its genus-zero
quotient is P^1 over the finite field. Each of the three F_2-rational points of
P^1 has a fiber that is an effective divisor of degree 2. Its support contains
a closed point of degree 1 or 2, hence an F_4-rational point. Distinct fibers
have disjoint support. Consequently #C(F_4)>=3. Wild ramification can change
multiplicity, not this lower bound.

If J_C~A and g=n-1, the original exact Frobenius calculation gives
#C(F_4)=2, for both signs. Such a C cannot be hyperelliptic. For mu=-1 this
adds a restriction beyond the earlier point-inclusion test; it supplies no
general nonhyperelliptic exclusion. The basic hyperelliptic quotient facts
were checked in Howe's ANTS XVI slides, page labelled 2 (retrieved).

## Existence is not an algorithmic advantage

Bruce and Li's finite-field covering theorem supplies a smooth curve whose
Jacobian maps dominantly onto the polarized abelian variety A. Up to isogeny,
A is therefore a Jacobian factor. The simple-variety theorem statement in
Li's slides also applies here. This resolves abstract factor existence, not
existence of a curve at the lower genus bound. The statements used do not
provide a hyperelliptic model or certify an efficiently evaluated injection
of the selected prime-order subgroup.

Velichka, Jacobson, and Stein study even-characteristic high-genus
hyperelliptic Jacobians. Their cited Enge--Gaudry asymptotic assumes known
Jacobian order and g/log(q)->infinity, with a subexponential bound expressed
in q^g. Those assumptions and the required curve representation cannot be
imported from the general Jacobian-covering theorem. At a fixed parameter,
an asymptotic bound is not a runtime estimate.

Other curve families can admit other index-calculus methods. Failure to meet
this particular hyperelliptic algorithm's hypotheses would not prove that
the destination DLP is hard.

There is a conditional asymptotic opportunity: if an efficiently accessible
family satisfies a suitable subexponential method's hypotheses with q=2 and
g=O(n), its logarithmic work bound of order sqrt(n*log(n)) can beat the
linear-in-n exponent of generic rho for a subgroup of size approximately 2^n.
This is a comparison of asymptotic forms, not evidence that this family of
destinations exists. The general covering theorem supplies no genus-O(n)
guarantee for the A considered here, and no finite runtime is inferred.

For a larger J_C~A*B, costs must use the actual curve genus and presentation.
The target subgroup's size does not justify treating the entire destination
as a genus-(n-1) Jacobian. No matched timing or memory measurement was obtained.
The baseline must include the public Koblitz/Frobenius structure. A comparison
would have to account for map evaluation, preprocessing, destination DLP work,
and verification, with amortization stated explicitly.

## Secrecy assessed separately

The simple-factor dimension and the point-count obstruction are public
isogeny-class information. A secret elliptic isogeny does not hide or change
them. These invariants do not determine every correspondence or secret path,
so their visibility is not a reconstruction theorem.

Jao--Miller--Venkatesan establish GRH-conditional random DLP reducibility
with restrictions on endomorphism rings. This limits a claim of an isolated
easy curve within the covered families; it does not recover every secret
isogeny or settle arbitrary Jacobian correspondences. A public observer only
needs some comparably useful route, rather than the original secret route.
No public-reconstruction lower bound or scoped search timing was produced.

Thus neither easier DLP nor hidden access to that advantage has been
established for these Koblitz classes. Neither question is closed by the
genus bound or the existence theorem.

## Sources and validation

- Diem--Naumann, *On the Structure of Weil Restrictions of Abelian Varieties*,
  Theorem 4, Corollary 21, and restriction-of-scalars functor:
  https://arxiv.org/html/math/0504359v2 (retrieved full text).
- Bruce--Li, *Effective Bounds on the Dimensions of Jacobians Covering
  Abelian Varieties*: https://arxiv.org/abs/1804.11015 (retrieved abstract);
  Li's author slides, theorem statements on pages labelled 6 and 8:
  https://www.math.wustl.edu/~wanlin/covering%20abelian%20varieties.pdf
  (retrieved). The full paper's proof was not inspected in this review.
- Howe, *Enumerating hyperelliptic curves over finite fields in quasilinear
  time*, ANTS XVI, page labelled 2:
  https://antsmath.org/ANTSXVI/slides/Howe.pdf (retrieved).
- Velichka--Jacobson--Stein, *Computing Discrete Logarithms in the Jacobian
  of High-Genus Hyperelliptic Curves over Even Characteristic Finite Fields*,
  Sections 1--2: https://eprint.iacr.org/2011/098.pdf (retrieved full text).
- Jao--Miller--Venkatesan, *Do All Elliptic Curves of the Same Order Have
  the Same Difficulty of Discrete Log?*:
  https://arxiv.org/abs/math/0411378 (retrieved abstract).
- Original theory and exact arithmetic: the reviewed commit named above
  (internal). The independent report records its rerun of all 12 cases.

No large-polynomial factorization, map construction, DLP computation,
challenge-specific result, or canonical state transition was performed.
