# P1542 R1 independent pairing lift-return audit

## Status and claim boundary

- Record type: independent theorem-only audit
- Root hypothesis: `ECDLP-IDEA-008`
- Candidate: `P1542`
- Claim: `CLM-P1542-PARTIAL-PAIRING-LIFT-RETURN-CYCLE`
- Evidence scale: exact Frobenius-eigenspace, FAPI, rational-map, degree,
  Fourier-support, and cost statements; no experiment
- Contract state: no contract was drafted, approved, revised, or executed
- Breakthrough claim: none
- Disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_GO__ORDINARY_ENDOMORPHISM_EIGENLINE_GATE_RECONSTRUCTED__TORUS_RETURN_M_OVER_5D_AND_SYMMETRIC_TRACE_GATES_RECONSTRUCTED__LIFT_AND_RETURN_ARE_FAPI_1_AND_FAPI_2__REVISED_SATOH_MAKES_MILLER_INVERSION_POLYNOMIAL_BUT_DOES_NOT_SUPPLY_PRESCRIBED_IMAGE_EI__SHIFTED_RETURN_HAS_OMEGA_N_FOURIER_SUPPORT__PAIRING_EXTENSION_AND_WHOLE_CYCLE_COSTS_UNSUPPLIED__COMPACT_EI_OR_AUXILIARY_BRANCH_UNCLASSIFIED__INCONCLUSIVE`

The producer's ordinary eigenline, torus-to-elliptic, `M<=5d`, complete-trace,
and whole-cycle statements reconstruct. Independent review sharpens the finite-group
interface: the missing cross-line lift and source return are exactly the two directions
of fixed-argument pairing inversion (FAPI). Their graphs are compact and membership is
easy to verify, but solving the unique fibers is the operation.

The literature review also corrects an important possible overstatement. Satoh's
majorly revised 2025 preprint gives polynomial-time Miller inversion for the reduced
Tate pairing at every embedding degree greater than one. Miller inversion must not be
recorded as an unconditional degree-`N` obstruction. The remaining FAPI step is the
selection of a final-exponent preimage in the Miller image of the prescribed source
domain, together with both inversion directions and all extension-field costs. No
audited artifact supplies that operation.

P1542 is therefore terminal inconclusive within the named classes. This is not a lower
bound against every compact modular circuit, exponentiation-inversion algorithm, or
auxiliary-variety correspondence.

## Hash-bound inputs

- `ideas/ECDLP-IDEA-008_partial_pairing_return_cycle_hypothesis.md`:
  `0566ffabe87b88f3c92500dbeeee3ebe6a6a561c482ca1eaa40e48226d403142`
- `ideas/artifacts/ECDLP-IDEA-008/p1542_pairing_lift_return_geometry_gate.md`:
  `0fc5bc2796aab3f2a1daab8d3ec40b769b472f8c023cda2716677532bb2b7897`
- `ideas/artifacts/ECDLP-IDEA-003/correspondence_spec.md`:
  `7ad6ee0d5a038dbb086eb32d65e40cda79cba20bf2288c0bee473e9e96c2fc0f`
- `ideas/artifacts/ECDLP-IDEA-003/p1530_r1_r2_independent_audit.md`:
  `e7dfae990f357da7d1f3f8503c06d6334323d925244d3803f2a002888081c402`
- `ideas/artifacts/ECDLP-IDEA-006/p1540_r1_independent_audit.md`:
  `8032be2d3a645ac64c046783191cc9c634715518eb18e4702acf66e077223d45`
- `ledger/H-ISO-001.yaml`:
  `dd4253ed30194fc390506894194349ecb6b62ae0f9052d27ff00f2ef293df59b`
- `ledger/EV-ISO-001.yaml`:
  `1ba53e3c49d1fcb1b0cfea1af2508839a32b2140241f145081d25cbf689db581`

## Ordinary Frobenius-eigenline reconstruction

Let `E/F_p` be ordinary and let `G_1=<P> subset E(F_p)` have prime order
`N!=p`. Let `pi` be geometric Frobenius. When its two roots on `E[N]` are
distinct,

```text
E[N]=V_1 direct_sum V_p,
pi|V_1=1,
pi|V_p=p mod N,
G_1=V_1.
```

The geometric endomorphism algebra of an ordinary elliptic curve is an imaginary
quadratic field and is commutative. Every geometric endomorphism `u` commutes with
`pi`, so for `R in V_1`,

```text
pi(u(R))=u(pi(R))=u(R).
```

Thus `u(R)` remains in `V_1`. A same-curve ordinary endomorphism cannot transport
the rational line to the independent `V_p` direction required by a nondegenerate
pairing. This reconstructs the producer gate.

The statement is deliberately scoped. It does not classify an isogeny or
correspondence through another abelian variety, an algorithm defined only on the
finite torsion set, merged Frobenius eigenvalues, or a low-embedding-degree special
family. Each such route must still provide the scalar-compatible map and its complete
cost.

## Exact FAPI normal form

Let `G_2=<T>` be an independent order-`N` pairing line and let

```text
e:G_1 x G_2 -> mu_N
```

be nondegenerate. Put `zeta=e(P,T)`. The two fixed-argument maps

```text
Phi_1:G_1 -> mu_N,  R |-> e(R,T),
Phi_2:G_2 -> mu_N,  S |-> e(P,S)
```

are group isomorphisms. For `R=[a]P` and `S=[b]T`,

```text
Phi_1(R)=zeta^a,
Phi_2(S)=zeta^b.
```

In the standard terminology:

- `Phi_2^(-1)` is FAPI-1, with the first pairing argument fixed;
- `Phi_1^(-1)` is FAPI-2, with the second pairing argument fixed.

The scalar-compatible lift required by P1542 is exactly

```text
L(R)=Phi_2^(-1)(Phi_1(R)),
L([a]P)=[a]T.
```

Given both inverses, the outward-and-back product is

```text
B(R,S)=Phi_1^(-1)(e(R,L(S))),
B([a]P,[b]P)=[a*b]P.
```

This is the direct P1542 cycle. It is also the standard reduction showing that both
FAPI directions yield computational Diffie-Hellman. It does not prove FAPI equivalent
to a DLP, and the audit does not make that stronger claim.

The graph of each inverse is compact:

```text
Gamma_1={(z,S):e(P,S)=z},
Gamma_2={(z,R):e(R,T)=z}.
```

Nondegeneracy gives one output in the named cyclic line for every `z in mu_N`, and
one pairing verifies a proposed output. Compact graph definition and easy verification
do not locate the unique point. A correspondence-membership certificate is therefore
not a return algorithm.

One inversion direction alone does not supply the claimed nonlinear cycle. Target
multiplication followed by `Phi_1^(-1)` only reproduces source addition. The lift and
return directions, or a mechanism with exactly the same two scalar effects, must both
be charged.

## Rational and explicit-degree return gates

Over an algebraic closure, a torus is rational and has trivial Albanese variety. Every
rational map from a connected torus to an elliptic curve is therefore constant. This
reconstructs the producer's exclusion of a global rational extension

```text
rho:T dashrightarrow E
```

of a pairing return.

The finite subgroup `mu_N` is not Zariski dense in a fixed instance, so its abstract
inverse is not contradicted by this theorem. It must fail to extend rationally, use
instance-dependent high complexity, or leave this geometric class.

For the explicit finite-domain screen, suppose on `M` distinct target values the
returned coordinates on

```text
E:y^2=x^3+a*x+b
```

are

```text
x=A(z)/B(z),
y=C(z)/D(z)
```

with all four polynomial degrees at most `d` and nonzero denominators. Clearing the
curve equation gives

```text
H=C^2*B^3-A^3*D^2-a*A*B^2*D^2-b*B^3*D^2,
deg(H)<=5*d.
```

If `M>5d`, then `H=0`. The formulas define a rational torus-to-`E` map and are
constant. Hence every nonconstant formula in this class satisfies

```text
d>=ceil(M/5).
```

This is a degree lower bound, not an arithmetic-circuit lower bound. Repeated squaring,
modular reduction by `z^N-1`, division, and branching can represent high-degree maps
succinctly.

## Shifted Fourier-support screen

The strongest explicit compact-circuit screen available from P1540 concerns sparse
character expansions. Choose a public `R_0 in E(F_(p^2))` outside `-G_1`; this is a
constant-degree extension and makes every point `R_0+[c]P`, `c in Z/NZ`, finite.
Define

```text
s_c=x(R_0+[c]P).
```

Over a field containing `mu_N`, there is a unique polynomial modulo `Z^N-1`,

```text
X_(R_0)(Z)=sum_(j=0)^(N-1) a_j*Z^j,
X_(R_0)(zeta^c)=s_c.
```

Let `t` be the number of nonzero `a_j`. The periodic sequence is a sum of `t`
characters, so it has a constant-coefficient recurrence of order at most `t`, with
characteristic polynomial

```text
prod_(a_j!=0) (U-zeta^j).
```

The independently audited translated-pole theorem applied to the full finite block of
length `N` gives

```text
t>=ceil((N-2)/3).
```

Thus a shifted source return cannot be an `o(N)`-term expanded Fourier sum or sparse
polynomial in the pairing character. Subtracting public `R_0` converts its point output
to `[c]P` in constant group work.

This is prior-art-aligned rather than a novelty claim. Satoh proved stronger coefficient
nonvanishing for a positive proportion of ordinary Verheul-homomorphism instances.
The present all-instance lower bound is weaker and shifted. Neither result excludes a
small straight-line program, a sparse high-degree rational expression whose inversion
densifies its Fourier expansion, a nonlinear state machine, or an implicit root/branch
solver.

## Pairing-inversion literature correction

Pairing computation separates a Miller value from a final exponentiation. Kim and
Cheon formalize the corresponding inversion tasks:

1. exponentiation inversion (EI), which must select a final-exponent root lying in the
   Miller image of the prescribed source domain; and
2. Miller inversion (MI), which recovers a point from that raw Miller value.

Taking an arbitrary algebraic root can be polynomial time, yet be useless because it
misses the small source domain. Their corrected EI is the intersection

```text
{y:y^d=z} intersection {f_(s,A)(R):R in prescribed G_i}.
```

The revised 2025 version of Satoh's preprint proves MI algorithms for reduced Tate
pairings at every embedding degree `k>1`:

```text
even k: deterministic O((k*log p)^3) bit operations,
odd  k: probabilistic O(k^6*(log p)^3) average bit operations.
```

This invalidates the older route description that treated solving an explicit
degree-about-`N` Miller equation as the enduring hard core. The Satoh algorithm starts
from a raw Miller value. P1542 starts from a reduced pairing target and therefore still
owes the prescribed-image EI step. It also owes the opposite FAPI direction and cannot
reuse an arbitrary point from an extended Tate domain when the cycle requires the named
prime-order eigenline.

Satoh's 2008 closed-form Weil-pairing inversion and his interpolation papers are prior
art for explicit inverse descriptions. A closed formula is not by itself a
polylogarithmic evaluation algorithm. In the supersingular embedding-degree-two case,
Satoh's 2013 coordinate inversion constructs a polynomial of degree about `p/2` and
explicitly records the method as infeasible at cryptographic size. The current audit
therefore neither dismisses the closed formulas nor promotes them as an efficient FAPI.

The corrected survivor is precise: a target-independent algorithm that performs the
prescribed-image EI for both FAPI directions, or bypasses EI and MI together, while
returning the required source-line points and paying the full extension cost. No such
algorithm is present in the hypothesis or cited sources.

## Embedding-degree and representation cost

Let

```text
k=ord_N(p)=N^(kappa+o(1)).
```

A primitive `N`th root has minimal field `F_(p^k)`. In the ordinary materialized
extension-field model, one target element occupies `Theta(k)` base-field words and a
pairing touches extension state of that scale. Thus the direct representation has

```text
time exponent at least kappa,
memory exponent at least kappa.
```

The specific revised Satoh MI route has exponents `3*kappa` for even `k` and
`6*kappa` for odd `k`, ignoring polylogarithmic factors. These are costs of that
algorithm, not lower bounds on all MI circuits. A compressed torus representation must
state its dimension, multiplication, pairing-output, EI, decompression, and returned
point costs; an unknown exponent is not a free compressed representation.

When `k=N^(o(1))`, low-embedding-degree families and direct finite-field DLP are the
MOV/Frey-Ruck controls. They may be weak curves, but they are special-family transfer
evidence, not a generic ordinary-prime lift-and-return construction. When `k` is large,
materializing the pairing target can itself exceed the P1542 cap. An auxiliary
small-embedding environment would be mechanism-new only after a scalar-compatible map
from the original generic curve and a rational source return are constructed.

## Correspondence and branch reconstruction

Let a finite correspondence be represented generically by

```text
q:C -> T,
psi:C -> E.
```

The complete group sum of `psi` over a generic fiber of `q`, with multiplicities, is a
rational map `T dashrightarrow E`. It is constant by the torus gate. Norms, complete
deck sums, and symmetric branch aggregation therefore cannot return the target scalar.

A useful nonsymmetric branch must solve a FAPI fiber, not merely name the compact graph.
It must publish:

1. target-independent equations and every extension field;
2. a public branch predicate and complete certificate;
3. the accepted target set and full-cycle success probability;
4. direct output in the required cyclic eigenline;
5. every branch, ramification, rejection, and failed-attempt cost; and
6. proof that the two directions compose to `[a*b]P` without a source or target DLP.

An auxiliary abelian variety or nonsymmetric cover remains outside the no-go theorem.
No audited object meets this interface.

## Whole-cycle cost reconstruction

Retain the producer's notation and add the explicit target-representation exponent
`sigma`. Let setup cost `N^c`; calibration use `N^gamma` samples of per-sample cost
`N^r_0` and algebra exponent `omega_cal`; one complete fixed scalar-power circuit cost
`N^r`; its success probability be `N^(-Delta)`; return state be `N^s`; final ambiguity
be `N^v`; and `D=N^alpha` be the Cheon divisor. Then

```text
lambda=max(c,sigma,gamma+r_0,omega_cal*gamma,r+Delta,
           alpha/2,(1-alpha)/2,v),
mu=max(s,sigma,gamma,alpha/2,(1-alpha)/2).
```

The terms `r,s,Delta` include both FAPI directions, EI, MI, pairing evaluation,
extension arithmetic, domain tests, branch search, and every failed full circuit. A
per-gate acceptance fraction is not `Delta`. If `Theta(log N)` gates have independent
constant acceptance below one, their joint acceptance contributes a nonzero exponent.

Cheon's quarter-exponent term near `alpha=1/2` starts only after a correct
`[x^D]P` has been returned. A pairing value, raw Miller preimage, branch-membership
certificate, or injected auxiliary point is not that output. No current route supplies
numbers with `lambda,mu<=0.45`.

## Named route screens

- Same-curve ordinary distortion maps fail the reconstructed Frobenius gate.
- Direct Weil/Tate/Ate return is the named FAPI problem. Revised Satoh MI removes one
  subproblem but does not supply prescribed-domain EI in both directions.
- Global rational and low-degree univariate returns fail the constant-map and
  `M<=5d` gates.
- Expanded sparse character or polynomial returns have linear Fourier support.
- Complete cover traces are constant; a selected branch must solve the FAPI fiber.
- Semaev systems, resultants, Groebner bases, FFE, and generic root finders are backend
  controls unless they construct the prescribed EI branch, output the exact source
  point, and pass the complete exponent rectangle.
- A target-field DLP solves FAPI but is charged as the direct MOV/Frey-Ruck control.
- A source rho/BSGS inversion has exponent one half and misses the promotion cap.
- Closed formulas, toy supersingular distortion maps, and oracle-labeled return tables
  validate identities or plumbing only.

## Literature boundary

1. Steven Galbraith, Florian Hess, and Frederik Vercauteren, *Aspects of Pairing
   Inversion*, <https://eprint.iacr.org/2007/256.pdf>. This supplies the FAPI
   definitions, unique-fiber interface, cross-group homomorphism, and two-direction CDH
   reduction.
2. Sungwook Kim and Jung Hee Cheon, *Fixed Argument Pairing Inversion on Elliptic
   Curves*, <https://eprint.iacr.org/2012/657.pdf>. This supplies the EI/MI split and
   the prescribed-domain intersection correction.
3. Takakazu Satoh, *Miller Inversion is Easy for the Reduced Tate Pairing of Embedding
   Degree Greater than one*, <https://eprint.iacr.org/2019/385>. The 2025 revision
   supplies polynomial-time MI for every `k>1`; it does not take a reduced pairing
   target as the raw Miller-value input.
4. Takakazu Satoh, *Closed formulae for the Weil pairing inversion*,
   <https://doi.org/10.1016/j.ffa.2007.12.003>. This is the explicit closed-form
   prior-art control.
5. Takakazu Satoh, *On Polynomial Interpolations Related to Verheul Homomorphisms*,
   <https://doi.org/10.1112/S1461157000001224>. This is the inverse-coordinate degree
   and coefficient-support prior-art boundary.
6. Takakazu Satoh, *On a Relation between the Ate Pairing and the Weil Pairing for
   Supersingular Elliptic Curves*, <https://eprint.iacr.org/2013/532.pdf>. This gives
   the degree-about-`p/2`, explicitly infeasible supersingular coordinate-inversion
   control.
7. J. S. Milne, *Abelian Varieties*,
   <https://www.jmilne.org/math/CourseNotes/AV.pdf>. This supplies the rational-map and
   Albanese boundary.
8. Andreas Enge, *Bilinear Pairings on Elliptic Curves*,
   <https://arxiv.org/abs/1301.5520>. This supplies the eigenspace, pairing, and
   distortion-map background.

No source or audited artifact supplies the two prescribed-domain FAPI inverses with a
generic ordinary scalar-compatible lift, complete source return, and sub-rho costs.
Novelty of such a future operation remains unverified.

## Independent decision

The P1542 review trigger is satisfied within its stated scope:

- the ordinary eigenline, torus rational-map, `M<=5d`, symmetric-trace, and
  whole-cycle gates reconstruct;
- the lift and return are identified exactly as FAPI-1 and FAPI-2, and their compact
  graph does not solve either unique fiber;
- the revised Satoh result corrects MI from a presumed hard degree-`N` root problem to
  a polynomial-time subroutine, leaving prescribed-domain EI as the explicit survivor;
- shifted inverse coordinates have `Omega(N)` Fourier support, without implying a
  general circuit lower bound;
- embedding degree, materialized target state, both inversion directions, and failed
  full cycles are included in the cost interface; and
- no compact EI, selected auxiliary branch, or complete lift-and-return path passes
  `lambda,mu<=0.45`.

P1542 is terminal inconclusive. IDEA-008 remains open only for a mechanism-new compact
prescribed-image EI or auxiliary correspondence outside the audited classes. No
contract, pairing fixture, extension-field campaign, FAPI implementation, return table,
or Cheon run is authorized by this receipt.

## Exactly one next action

Rerank outside same-curve ordinary distortion maps, global rational returns, explicit
low-degree interpolation, expanded Fourier/character returns, symmetric cover traces,
direct pairing inversion, and prior scalar-orbit families. Admit one successor only if
it names a mechanism-distinct source construction with a complete direct scalar-recovery
path and sub-rho cost gate.
