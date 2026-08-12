# Experiment Contract: EXP-ECDLP-TT-SAMPLED-REPLICATION-001

## Hypothesis

The p16267 sampled typed-TT locator signal is reproducible on two independently
generated ordinary 14-bit prime-field curves under the same family, budget,
held-out, rank, and matched-rho protocol.

## Null hypothesis

The 64/100 signal is fixture-specific: one or both fresh curves fail exact
support, held-out coverage, or quotient rank at every sub-full budget, or the
cost reduction disappears after fresh curve construction and matched rho are
charged.

## Parameters

- seeds: `271828`, `161803`;
- generated curves: one 14-bit curve per seed using the committed typed-five-EC
  generator, occupancy lambda `0.5`, and 32 held-out candidates;
- families: `random_x`, `source_prf_x`, `x_interval`, `rational_union`;
- suffix budgets: `8,16,32,64,full`;
- candidate: the same adaptive cut-3 sampled locator and source-sum cache;
- baselines: independently materialized typed D4 support and harness Pollard-rho
  on every public relation/held-out target.

## Controls and gates

- full `B^2` replay must be exact;
- every candidate witness must verify directly;
- held-out expected witnesses and projected support must be exact at any
  accepted sub-full budget;
- quotient rank is reported per family, preserving rank-deficient controls;
- the verifier regenerates both fresh fixtures from their seeds and reruns
  direct rho certificate checks.
- fixture serialization recursively excludes runner wall-time metadata so
  regeneration hashes bind mathematical inputs rather than incidental timing.

## Success criterion

Both fresh curves must contain at least one sub-full budget that passes support,
held-out, witness, and rank gates with reduced predicted entries and charged
source/reconstruction work. A one-curve or one-family signal is not sufficient.

## Falsification criterion

Either fresh curve fails the full control, or neither curve has an accepted
sub-full budget after all declared costs and matched rho are included.

## Boundary

This is medium toy-scale evidence about a fixed-curve representation lead. It
does not claim a generic ECDLP break, exponent improvement, deployed-key
recovery, or superiority to rho at cryptographic size.
