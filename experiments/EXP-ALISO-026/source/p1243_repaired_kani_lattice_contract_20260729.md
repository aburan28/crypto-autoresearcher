# Experiment Contract: Repaired Dimension-Four Kani Lattice

Date: 2026-07-29

## Hypothesis

For every arithmetic parity-repair fixture, let

```text
D=c*m*d,
n=n_1*m,
n^2-D=x^2+y^2.
```

Model the action of a cyclic degree-`D` isogeny on a symplectic Tate
basis by

```text
M=diag(D,1), dual(M)=diag(1,D).
```

Let

```text
A=[[x,y],[-y,x]],  A^T A=(n^2-D)I_2.
```

The orientation-free dimension-four Kani block on the rank-eight product
Tate module is

```text
F = [[A tensor I_2,       I_2 tensor dual(M)],
     [I_2 tensor M,      -A^T tensor I_2    ]].
```

It should satisfy

```text
F^dagger F=n^2 I_8,
F^T Omega F=n^2 Omega,
det(F)=n^8,
Smith(F)=diag(1,1,1,1,n^2,n^2,n^2,n^2).
```

This checks the exact polarized lattice interface, including the case
where `v_ell(D)=v_ell(m)+1>v_ell(n)` at repair primes.

## Status

RESTRICTED LATTICE THEOREM / EXACT COMPUTATIONAL CHECK /
NO ABELIAN-VARIETY ISOGENY

## Inputs

Use every passing family from

```text
experiments/ecdlp_isogeny/p1243_parity_repaired_kani_probe_result.json.
```

## Metrics

- exact norm identity;
- symplectic adjoint identity;
- polarization similitude;
- determinant;
- Smith normal form;
- `gcd(D,n)` and kernel size of `M mod n`;
- repair-prime valuations of `D`, `n`, and `n^2`;
- absence of any inverse of `D mod n`.

## Positive controls

- Every registered repaired family has the expected Smith form.
- The extra repair valuation satisfies
  `v_ell(D)=v_ell(m)+1<=2v_ell(m)=v_ell(n^2)`.
- The modeled action on `E[n]` has kernel size `m`.

## Negative controls

- Incrementing one entry of `A` rejects the polarization identity.
- Replacing `D` by `D+1` while retaining `A` rejects the norm identity.
- Requiring `D` invertible modulo `n` must fail on every nontrivial
  repaired case.

## Success criterion

All exact identities and Smith forms pass and all mutations are rejected.

## Falsification criterion

Any wrong invariant rejects the repaired Kani lattice interface.
Passing does not construct either half of the higher-dimensional isogeny,
prove smooth-modulus density, or measure field-operation costs.

## Reproduction command

```bash
python3 -B experiments/ecdlp_isogeny/p1243_repaired_kani_lattice.py
```
