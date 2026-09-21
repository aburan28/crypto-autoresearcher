# Experiment Contract: Four-Line Principalized Kani Descent

Date: 2026-07-29

## Hypothesis

Let `A` be the auxiliary ideal inclusion, `A^dagger` its adjoint, and
let `M` be an arbitrary integral rank-two Tate matrix of determinant
`D`, with dual

```text
M^vee = D M^(-1).
```

Choose a line `L` in the polarization kernel of the source
type-`(1,delta)` surface.  Use the four principalization lines

```text
E_0,H_a: L,       E_0,H_O: L,
E_1,H_a: M(L),    E_1,H_O: M(L).
```

Then all four blocks

```text
A, M, M^vee, A^dagger
```

descend integrally, and their descended Kani block is an
`n^2`-similitude between principal alternating lattices with the
required Smith type.

## Null Hypothesis

The earlier diagonal-action verifier only passed because it implicitly
fixed an eigenline.  For a non-diagonal `M`, one or more descended
blocks becomes nonintegral, the Kani polarization identity fails, or
the Smith type changes.

## Status

EXACT TATE-LATTICE HYPOTHESIS /
NO ABELIAN-SURFACE QUOTIENT OR THETA EVALUATION

## Inputs

Use every passing family from

```text
experiments/ecdlp_isogeny/p1243_auxiliary_lattice_kani_result.json
```

For each family test three deterministic non-diagonal matrices

```text
M = L_s diag(D,1) R_t
```

with `L_s,R_t` unimodular, and three source lines.

## Metrics

- determinant and dual identities for `M`;
- integral unimodular principal forms for all four quotients;
- integral descent of `A`, `M`, `M^vee`, and `A^dagger`;
- exact descended Kani polarization identity;
- determinant and Smith form;
- exact agreement with direct four-way conjugation.

## Positive Controls

Every family and every non-diagonal action/line pair passes all exact
gates.

## Negative Controls

- Replace `M(L)` by a different target line and reject integral descent
  of `M`.
- Use a different target line for the `H_O` copy and reject descent of
  `A^dagger` or `M^vee`.
- Mutate one entry of the descended Kani block and reject the
  polarization identity.

## Success Criterion

All exact gates pass for all rows and all mutations reject.

Passing proves the four-line compatibility on the tested Tate
lattices.  It does not construct geometric quotient surfaces, theta
structures, fields of definition, or an end-to-end recovery.

## Reproduction Command

```bash
python3 -B experiments/ecdlp_isogeny/p1243_auxiliary_four_line_descent.py
```
