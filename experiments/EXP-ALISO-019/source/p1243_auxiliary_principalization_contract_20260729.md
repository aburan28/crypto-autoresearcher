# Experiment Contract: Auxiliary Principalization Lines

Date: 2026-07-29

## Hypothesis

For every auxiliary-lattice Kani family with prime polarization type
`(1,delta)`:

1. `ker(H_a mod delta)` and `ker(H_O mod delta)` are one-dimensional
   multiplicity lines;
2. after tensoring with `E[delta]`, each polarization kernel is a
   two-dimensional symplectic space with exactly `delta+1` maximal
   isotropic lines;
3. the ideal inclusion `A` maps the source multiplicity kernel
   isomorphically to the target multiplicity kernel;
4. the cyclic degree-`D` Tate action is invertible and permutes the
   `delta+1` principalization lines;
5. the `A` and `eta` transports commute on the full four-dimensional
   torsion module.

This shows that compatible principalization requires at most
`delta+1` target-line candidates, rather than an exponential action
guess.

## Status

EXACT FINITE-MODULE PREFLIGHT / NO POLARIZED QUOTIENT CONSTRUCTION /
NO THETA IMPLEMENTATION

## Inputs

Read all passing rows from:

```text
experiments/ecdlp_isogeny/p1243_auxiliary_lattice_kani_result.json
```

## Metrics

- modular ranks and kernel dimensions of both Gram matrices;
- explicit kernel generators;
- nonzero scalar relating `A*v_a` and `v_O`;
- line count `delta+1`;
- invertibility of the degree-`D` Tate action;
- bijectivity of its projective-line action;
- exact tensor commutation;
- source and target line-image hashes.

## Positive Controls

All five families pass, including all four integer-two-square failures.

## Negative Controls

- Mutate `A` and reject preservation of the Gram kernel.
- Make the Tate action singular modulo `delta` and reject line
  bijectivity.
- Mutate one target line and reject the transported-line equality.

## Success Criterion

Every exact kernel, bijection, and commutation gate passes and all
mutations reject.

Passing does not prove the existence, field cost, or evaluation cost of
the corresponding abelian-surface quotients.

## Reproduction Command

```bash
python3 -B experiments/ecdlp_isogeny/p1243_auxiliary_principalization.py
```

