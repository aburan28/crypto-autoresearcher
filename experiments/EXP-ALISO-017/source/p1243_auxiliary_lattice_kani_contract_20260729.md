# Experiment Contract: Auxiliary-Lattice Kani Compression

Date: 2026-07-29

## Candidate

Use a small imaginary quadratic order on the rank-two multiplicity
lattice, not as an orientation of either elliptic curve.

For a cyclic isogeny of degree `D_eta`, a smooth modulus `n`, and

```text
S=n^2-D_eta>0,
```

find a negative fundamental discriminant `Delta_aux=-delta`, coprime to
`n*D_eta`, in which every prime dividing `S` splits. A root of the
auxiliary order polynomial modulo `S` gives an invertible ideal

```text
a=(S, omega-r)
```

of norm `S`. On integral bases, inclusion `a -> O` is a matrix `A` and
the normalized norm forms have Gram matrices `H_a,H_O` satisfying

```text
A^T H_O A=S H_a,
det(H_a)=det(H_O)=delta.
```

The typed Kani block on the two-copy multiplicity modules should then
have abelian dimension four even when `S` is not a sum of two integer
squares.

## Hypothesis

For the registered non-coprime Kani fixtures, the exact rank-eight Tate
matrix

```text
F = [[A tensor I_2,          I_2 tensor dual(M)],
     [I_2 tensor M,         -A^dagger tensor I_2]]
```

with `M=diag(D_eta,1)` satisfies

```text
F^T Omega_out F=n^2 Omega_in,
det(F)=n^8,
Smith(F)=diag(1,1,1,1,n^2,n^2,n^2,n^2).
```

Here

```text
Omega_in = diag(H_a tensor J,H_O tensor J),
Omega_out= diag(H_O tensor J,H_a tensor J).
```

Both Gram matrices should have Smith type `(1,delta)`. This is the exact
nonprincipal-polarization lattice gate needed before attempting
principalization and geometric evaluation.

## Status

HYPOTHESIS / EXACT LATTICE PREFLIGHT / NO PRINCIPALIZATION THEOREM /
NO ABELIAN-VARIETY ISOGENY

## Parameters

Use the five arithmetic families from

```text
experiments/ecdlp_isogeny/p1243_parity_repaired_kani_probe_result.json
```

but remove the parity repair:

```text
D_eta=m*d,  n=n_1*m,  S=n^2-D_eta.
```

Search prime `delta == 7 mod 8` in increasing order, with
`gcd(delta,n*D_eta*S)=1`, until every prime divisor of `S` splits in
discriminant `-delta`.

## Metrics

- auxiliary discriminant and search trials;
- splitting at every prime power of `S`;
- exact ideal norm and inclusion determinant;
- integral normalized Gram matrices;
- Gram determinants and Smith forms;
- ideal adjoint integrality and both adjoint identities;
- typed polarization similitude;
- determinant and Smith form of the Kani block;
- local kernel sizes at primes dividing `n`;
- comparison with the integer two-square gate.

## Positive Controls

- At least one registered family has `S` not a sum of two integer
  squares but passes the auxiliary-lattice gate.
- Every accepted auxiliary discriminant is prime fundamental, coprime, and
  split at all required primes.
- Every Kani block has the target Smith form.

## Negative Controls

- Increment one entry of `A` and reject the ideal similitude.
- Increment one entry of `H_a` and reject the typed polarization
  identity.
- Replace `D_eta` by `D_eta+1` and reject the Kani norm identity.
- Force an inert auxiliary discriminant and reject ideal construction.

## Success Criterion

All exact lattice identities and Smith forms pass on all five families,
at least one integer-two-square failure is rescued, and every effective
mutation is rejected.

Passing does not prove that type-`(1,delta)` polarizations can be
principalized functorially with only polynomial-in-`delta` overhead. It
does not construct or evaluate a dimension-four isogeny.

## Falsification Criterion

Any registered family has no searched small splitting discriminant, a
nonintegral adjoint, wrong restricted-kernel Smith type, or failed
polarization identity.

## Reproduction Command

```bash
python3 -B experiments/ecdlp_isogeny/p1243_auxiliary_lattice_kani.py
```
