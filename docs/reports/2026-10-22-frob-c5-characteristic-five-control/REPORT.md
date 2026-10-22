# FROB C5 characteristic-five countercontrol

## Scope and result

This is a mathematical negative control requested by the [C5 model-bridge
problem](../../../problems/frob-c5-factor-kernel-and-model-bridge.md). The
archived EXP-FROB-91ee9c core cells use base characteristics 11, 13, and 19;
the control asks what fails if the same coprime-factor argument is transferred
to characteristic five. No scientific trial was rerun.

At exact source commit `203cff284eff59a81e8a98a4ff5fac0459d63790`,
[CharacteristicFive.lean](../../../formal/CryptoResearch/FrobTrace/CharacteristicFive.lean)
proves over `ZMod 5` that

1. `X^5 - 1 = (X - 1)^5`;
2. `X^4 + X^3 + X^2 + X + 1 = (X - 1)^4`; and
3. `X^5 - 1` is not squarefree, by exhibiting the nonunit square divisor
   `(X - 1)^2`.

The source SHA-256 is
`d5d58d51838558d8d02fbeebd30b23318cace7680335bcfe1bd69a0f5b3cdf4f`.
The frozen [formal target](../../../formal/targets/frob-c5-characteristic-five-control.yaml)
has SHA-256
`146abf35f8e0fe438f0f0f34e0b16019b574dac3b77c96f738276f1de14addb9`.
The exact-source [verification receipt](proof-verification.json) has SHA-256
`e38fd8092a9f06c68e4a3962fe9835387984636724af85ce30b4917586663c7d`.
On pinned Lean 4.35.0-rc1, its 8,971-job workspace build and 3,092-job
target build passed. The forbidden-construct scan found none; the target
axiom audit passed; the workspace audit found 588 theorem declarations using
standard axioms only. Independent semantic review remains pending.

## Why this is the right negative control

The q=11, 13, and 19 factor-kernel argument uses distinct irreducible factors
of the nontrivial fifth cyclotomic polynomial and their coprime kernels.
Characteristic five collapses those factors to powers of `X - 1`, as the
[proof diagram](proof.svg) shows. Thus the coprime-factor CRT step cannot be
copied unchanged to that characteristic. This is a boundary on the proof
method, not a counterexample to the recorded q=11/13/19 identities.

The [archived specification](../../../experiments/EXP-FROB-91ee9c/specification.yaml)
contains no q=5 core cell. The theorem does not identify the archived
`F_q[z]/(g)` basis or executable Frobenius matrix with a Lean field, recover
historical C3/C4 sample identities, finish C8, or establish an ECDLP
performance improvement. The separate [factor-kernel PR
#2475](https://github.com/aburan28/crypto-autoresearcher/pull/2475) carries
the q=11/13/19 mathematical proof and source-bound matrix replay; its
historical model bridge and independent review remain open.

## Graphs and next check

The editable [DOT](proof.dot), [SVG](proof.svg), [PNG](proof.png),
[figure PDF](proof-figure.pdf), and [report PDF](report.pdf) render the new
boundary. The C5 factor-proof diagram is checked separately in PR #2475.
No run value, performance graph, or dashboard row changed because this task
made no measurement. The next proof obligation is a checked link from each
archived quotient modulus and Frobenius matrix to the Lean field model, with
source custody and independent semantic/code review.
