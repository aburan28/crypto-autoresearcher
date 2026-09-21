# Experiment Contract: Principalized Auxiliary Kani Lattice

Date: 2026-07-29

## Hypothesis

For each type-`(1,delta)` Gram matrix `H`, choose a primitive lift `v`
of its modular kernel and a unimodular matrix `U=[w,v]`. In the new
multiplicity coordinates the polarization kernel is the second copy of
`E[delta]`. Quotient a cyclic line in that copy by a cyclic
degree-`delta` Tate map

```text
M_delta=diag(delta,1).
```

The resulting rank-four quotient matrix

```text
Pi_H=diag(I_2,M_delta)*(U^(-1) tensor I_2)
```

should transform `H tensor J` into an integral unimodular alternating
form

```text
Omega_H'=Pi_H^(-T)*(H tensor J)*Pi_H^(-1).
```

If the auxiliary ideal inclusion `A` maps the selected source
polarization line to the target line, then

```text
Abar=Pi_O*(A tensor I_2)*Pi_a^(-1)
```

should be integral and satisfy

```text
Abar^T Omega_O' Abar=S Omega_a'.
```

Conjugating the full typed Kani block by the four principalization maps
should produce an integral dimension-four Kani lattice with principal
source and target forms and unchanged Smith type.

## Status

EXACT PRINCIPALIZED-LATTICE HYPOTHESIS /
NO ABELIAN-SURFACE QUOTIENT OR THETA EVALUATION

## Inputs

Read all passing rows from:

```text
experiments/ecdlp_isogeny/p1243_auxiliary_lattice_kani_result.json
```

## Metrics

- primitive lifts and unimodular alignment matrices;
- integral quotient matrices and complementary factorizations;
- integral principal alternating forms;
- determinant-one and full-rank checks;
- integral descended auxiliary and secret-action matrices;
- descended similitude identities;
- integral conjugated Kani block;
- determinant and Smith form;
- exact agreement with direct block conjugation.

## Positive Controls

All five families pass, including all four integer-two-square failures.

## Negative Controls

- Use a vector outside the Gram kernel and reject integrality or
  principal polarization.
- Mutate the cyclic quotient degree and reject unimodularity.
- Mutate `Abar` and reject the auxiliary similitude.
- Mutate the secret degree and reject the Kani identity.

## Success Criterion

All integral, principal, similitude, determinant, Smith, and conjugation
gates pass and all mutations reject.

Passing proves an exact Tate-lattice principalization. It does not
construct the corresponding polarized abelian-surface quotients, prove
their field of definition, or implement theta evaluation.

## Reproduction Command

```bash
python3 -B experiments/ecdlp_isogeny/p1243_auxiliary_principalized_lattice.py
```

