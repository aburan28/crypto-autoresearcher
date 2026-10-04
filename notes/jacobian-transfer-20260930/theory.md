---
title: "Koblitz Jacobian transfers: a scoped dimension obstruction"
record_kind: unreviewed_theory_note
added: "2026-09-30"
independent_review: false
research_state_transition: false
dlp_runs: 0
---

# Koblitz Jacobian transfers: a scoped dimension obstruction

This develops the public curve-security assessment in
`docs/jacobian-transfer-assessment-20260930.md`. It is a proposed derivation
with exact arithmetic diagnostics, not a promoted finding, formal proof
certificate, goal closure, transfer construction, or DLP benchmark.

## Scope and result

Let E/F_2 be either standard binary Koblitz curve

    y^2 + x*y = x^3 + a*x^2 + 1,  a in {0,1}.

Its Frobenius polynomial is T^2 - mu*T + 2 with mu=(-1)^(1-a).
Let n be one of 31, 53, 83, 131 and put

    W = Res_(F_(2^n)/F_2)(E),
    A = ker(Tr: W -> E).

Proposed scoped result: A is F_2-simple of dimension n-1. An algebraic
F_2-homomorphism from W into a Jacobian J_C/F_2 that preserves an odd
prime-order subgroup G of E(F_(2^n)) must therefore have genus(C) >= n-1.
The analogous dimension constraint applies when a Jacobian maps into W
with an image carrying G.

For n=131 this gives genus >=130. The result is about homomorphisms of
abelian varieties over F_2. It does not apply to an arbitrary homomorphism
between finite groups that does not extend to such a geometric map.

## Published structural input

Claus Diem and Niko Naumann, *On the Structure of Weil Restrictions of
Abelian Varieties*, Theorem 4 and Corollary 21, describe the cyclic
decomposition and simplicity criterion in terms of the CM field's
intersection with a cyclotomic field. These parts of the full text were
retrieved and read in this session:
https://arxiv.org/html/math/0504359v2 (provenance: retrieved).
The application to the selected Koblitz parameters below is this note's
derivation. It is not claimed as a novel theorem.

For the finite-field homomorphism/isogeny framework, Kedlaya's Chapter 7,
Theorems 7.1.3-7.1.4, was read:
https://kskedlaya.org/weil-cohom/chapter-7.html (provenance: retrieved).
Existence of an isogeny supplies no efficient explicit map by itself.

## Derivation

1. Both curves are ordinary. Their rational endomorphism algebra is
   K_0=Q(sqrt(-7)), since mu^2-8=-7. For ordinary elliptic curves over
   finite fields, geometric endomorphisms commute with Frobenius and
   are already defined over the base field.

2. W is isogenous over F_2 to E times A. The kernel of trace is connected:
   after extension to F_(2^n), trace is the sum map E^n -> E, whose
   kernel is E^(n-1). Thus dim(A)=n-1.

3. Let alpha,beta be the roots of T^2-mu*T+2 and
   s_0=2, s_1=mu, s_j=mu*s_(j-1)-2*s_(j-2).
   The cyclic Frobenius action gives

       P_W(T)=T^(2n)-s_n*T^n+2^n,
       P_A(T)=P_W(T)/(T^2-mu*T+2).

   For prime n, the roots of P_A are alpha*zeta_n^i and beta*zeta_n^i
   for i=1,...,n-1. This is the primitive cyclotomic component.

4. K_0 and Q(zeta_n) have trivial intersection for these primes. For
   n=31,83,131 the unique quadratic cyclotomic subfield is Q(sqrt(-n));
   for n=53 it is Q(sqrt(53)). None is Q(sqrt(-7)). Therefore the
   published simplicity criterion applies to A.

   An independent algebraic explanation of irreducibility is also
   available. For lambda=alpha*zeta_n, lambda^n=alpha^n generates K_0:
   alpha^n cannot equal beta^n, since alpha/beta is not a root of unity.
   Indeed, alpha/beta + beta/alpha = -3/2; a rational algebraic integer
   would be an integer. Hence Q(lambda) contains both alpha and zeta_n,
   and has degree 2*(n-1). Its degree equals deg(P_A), so P_A is
   irreducible over Q. A proper abelian subvariety would contribute a
   proper Frobenius-polynomial factor, which is impossible.

5. The trace of an odd prime-order subgroup G lands in E(F_2), whose
   order is 3-mu, either 2 or 4. Thus Tr(G)=0 and G lies in A(F_2).
   A map preserving G must restrict nontrivially to A. Its kernel has
   zero-dimensional identity component because A is F_2-simple, so its
   image has dimension n-1. A Jacobian containing that image has genus
   at least n-1. For a map in the other direction, its image must contain
   the large simple component to carry G, giving the same dimension bound.

6. Replacing E over F_(2^n) by an F_(2^n)-isogenous curve leaves the
   Frobenius polynomial of its Weil restriction unchanged. Its only
   simple component capable of carrying an odd prime-order rational
   subgroup is still the dimension-(n-1) component: the remaining
   elliptic component has 2 or 4 F_2-rational points. Concealing an
   isogeny changes neither this public isogeny-class invariant nor the
   dimension requirement.

## A further Jacobian condition

If genus(C)=n-1 exactly and A maps nontrivially to J_C, then J_C is
F_2-isogenous to A. For n>2 the first two power traces of W vanish,
so those of A are -s_1 and -s_2. Consequently such a curve would have

    #C(F_2) = 3+mu,
    #C(F_4) = 5+s_2 = 2.

For mu=+1 this gives 4 points over F_2 but only 2 over F_4, contrary
to inclusion of the rational-point sets. Thus genus n-1 is excluded
in this sign case; the scoped algebraic-transfer bound becomes genus >=n.
For mu=-1 both counts are 2; passing this condition establishes no
Jacobian existence. Larger Jacobians may have other isogeny components,
and their additional traces prevent this particular contradiction.

## Arithmetic checks and controls

`check_tracezero.py` uses only Python's standard library. The output
`arithmetic.json` retains full integer coefficients and their hashes.
The execution was:

    python3 theory-work/check_tracezero.py > theory-work/arithmetic.json

After checkout of this note's repository directory, the equivalent command is:

    python3 notes/jacobian-transfer-20260930/check_tracezero.py > /tmp/tracezero.json

Checks performed: exact polynomial quotients, multiplication of primitive
blocks, P_A(1)*#E(F_2)=#E(F_(2^n)), nonzero coefficient of alpha in alpha^n,
and explicit factor multiplication for the exceptional n=7 control.
The program does not factor the large polynomials or prove the dimension
theorem mechanically; the simple dimensions are applications of the
published theorem, explicitly labelled as such in the output.

| Extension degree n | Dimensions of non-base simple components | Interpretation |
| --- | --- | --- |
| 7 | 3, 3 | Exceptional control: Q(sqrt(-7)) is cyclotomic here; explicit degree-6 factors multiply to P_A |
| 31 | 30 | Prime-degree Koblitz analogue |
| 51 | 2, 16, 32 | Composite-degree control; component carrying a particular subgroup must be identified separately |
| 53 | 52 | Prime-degree analogue |
| 83 | 82 | Higher-fidelity checkpoint |
| 131 | 130 | Challenge-scale family-level constraint |

Both signs mu=-1 and mu=+1 were checked at all six degrees (12 cases).
No exact ECC2K-130 curve UID or challenge subgroup was loaded. The note
covers both standard families, and any later challenge-specific artifact
must bind the exact curve UID and subgroup rather than infer them from n.

## What this resolves and leaves open

The derivation supplies a public obstruction to small-genus F_2 algebraic
transfers for these prime-degree Koblitz families. A hidden isogeny does
not erase that obstruction. It supplies no secrecy bound for an explicit
correspondence, and it does not exclude a high-genus destination.

High genus alone does not prove that the destination DLP is harder.
Jacobian existence, a compatible polarization, actual map evaluation,
and a measured computational advantage are separate questions.

Next mathematical checks, in order:

- Obtain independent review of the map scope, subgroup location, and the
  simplicity application before promoting a finding or closing any lane.
- Check which isogeny classes in the permitted dimension can contain
  Jacobians, using polarization and point-count constraints.
- Keep existence evidence separate from an explicit efficient map and
  from any total-cost claim. Do not infer secrecy from unsuccessful search.

No canonical experiment or goal was started or closed. This is a draft
theory artifact with a reproducible arithmetic diagnostic; no trapdoor
was constructed and no discrete logarithm was computed.
