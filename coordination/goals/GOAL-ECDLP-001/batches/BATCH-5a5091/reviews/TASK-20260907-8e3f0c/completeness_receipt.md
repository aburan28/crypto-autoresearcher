# TASK-20260907-8e3f0c — completeness of the later eight-prime decay-fit protocol

Recorded: 2026-09-07. Role: coordinator. Goal: GOAL-ECDLP-001. Experiment: EXP-ECDLP-5cad48.

## Object checked

The later eight-prime decay-fit protocol named in `DEC-20260907-5d9375` as the recorded `next_action`. Two texts:

1. The existing stub `fit_of_a` in `experiments/EXP-ECDLP-5cad48/amendments/v1_stage2_protocol.yaml`.
2. The new later protocol `experiments/EXP-ECDLP-5cad48/amendments/v1_stage2_fit_protocol.yaml`.

This receipt does not authorize the fit. It does not classify W. It does not fit a.

## Stub verdict: incomplete

The `fit_of_a` block in `v1_stage2_protocol.yaml` is a pointer, not a protocol. Missing items:

- cartesian package (cells, M, arms, n, G, first-curve-only, eight-prime rule)
- negative-W_jack rule (do not take log of a negative jackknife W as the primary response)
- H2 fail threshold and exclusion rule
- null-subtraction formula W_rel = W_plugin(arm) - W_plugin(sha)
- H3-gated smallest-resolvable-effect formula (not a peek at H3 bias numbers)
- log-log specification log W_plugin = c + a log M + b log p, constrained Weil b = -1/2, leave-one-prime-out
- eight-prime representation-after-exclusions rule
- producer classification prohibition (SMALL_W_or_LARGE_W false, fit_of_a false)
- later classification rule recorded as later, not applied
- refuse-until-authorized clause
- proof_search_map
- certificate kind none
- CS proxy disclosure (no measured G in Stage 2 raw)

Filing the stub as the protocol would have been incomplete work.

## New protocol verdict: complete enough to file, not authorized

`v1_stage2_fit_protocol.yaml` names the missing items. Predecessor SHA of `v1_stage2_h3_authorized.yaml` is `72c815160bbd013372a14dbf31c417a1ae60179fdb7ac7042021c4e85f9b2fab`. Execution authorized is false. Classification authorized is false.

The H3 gate is a formula. This receipt did not read H3 bias numbers to set the 0.25 scale. A passing H3 gate on two primes at n = 10^7 does not prove n = 10^6 is adequate on the six larger primes. The protocol discloses that.

## What this receipt does not do

- Does not authorize RUN-ECDLP-5cad48-S2FIT.
- Does not classify W.
- Does not fit a.
- Does not authorize Stage 5 of EXP-ECDLP-a98ea9.
- Does not change H-ECDLP-07c7c6.

Cited: DEC-20260907-5d9375, DEC-20260907-ddfbce, DEC-20260907-e187e3, H-ECDLP-2ade73, EXP-ECDLP-5cad48, IDEA-20260904-f7d47d.
