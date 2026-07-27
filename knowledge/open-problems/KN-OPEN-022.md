---
id: KN-OPEN-022
type: open_problem
title: Can a QC-MDPC decoding failure rate at 2^-128 be established rather than extrapolated?
tags: [code-based, bike, qc-mdpc, dfr, decoding-failure, ind-cca, extrapolation, error-floor, weak-keys, cost-model, open]
confidence: reported
status: open
source_refs: [KN-TECH-060, KN-TECH-052, KN-LIT-7574, KN-LIT-2085, KN-LIT-3735, KN-LIT-1963, KN-LIT-7575, KN-TECH-048]
added: 2026-07-27
superseded_by: null
---

## Statement
IND-CCA security for a QC-MDPC KEM requires the decoding failure rate to sit
below the security level -- of order `2^{-128}` at category 1 -- because
failures leak the key (KN-TECH-060, KN-LIT-2085). **No such rate is
measurable.** Simulation reaches perhaps `2^{-30}` before compute cost becomes
prohibitive. The deployed claim is a fitted model evaluated roughly a hundred
orders of magnitude outside its measured range.

**Can that gap be closed by anything other than extrapolation** -- a proof, a
provably-bounded decoder, or a construction whose security does not depend on
the tail?

## Current state (as reported)
- **The claim is an extrapolation.** BIKE's DFR argument fits a model to
  simulable rates and extends it (KN-LIT-7574). This corpus has not verified the
  model's form or its stated confidence.
- **The tail is known not to be uniform.** KN-LIT-3735 reports weak-key classes:
  key-dependent regions where failure behaviour departs from the aggregate. Error
  floors are the general phenomenon -- iterative decoders often have a tail that
  does not follow the waterfall region's trend, which is precisely the region the
  extrapolation must get right.
- **Decoder design is still moving.** BGF and successors changed DFR behaviour;
  KN-LIT-1963 reports learned/unfolded decoders for QC-MDPC. A DFR claim is
  attached to a specific decoder, and re-tuning the decoder invalidates it.
- **NIST treated this as the deciding issue** in preferring HQC over BIKE
  (KN-LIT-7575). HQC's advantage is that its failure analysis is more tractable,
  not that it has no failures.

## Why it matters here
This is an external, high-stakes instance of the exact epistemic failure mode
this program built machinery to prevent. KN-TECH-052 governs fitting and
extrapolating cost exponents from bounded experiments; AGENTS.md rule 4 forbids
presenting toy-scale evidence as crypto-scale. A DFR claim at `2^{-128}` fitted
from data at `2^{-30}` is the largest extrapolation factor either rule has ever
been pointed at.

The program has a clear obligation here and it is a modest one: **do not let a
code-based DFR figure enter this corpus as a measured quantity.** Any future
entry citing a DFR must state the measured range, the model, and the
extrapolation factor. That obligation holds whether or not the underlying claim
turns out to be correct.

The parallel to KN-TECH-048 is worth keeping in view: lattice KEMs face the same
structure -- rare key-correlated failures amplified by chosen ciphertexts -- with
a different mechanism. Two independent instances suggest the right target is the
general question, not either scheme.

## What would close it
- **A provable DFR bound.** A decoder with an analyzable failure probability, even
  a loose one, would replace extrapolation with a bound. This is the outcome the
  field wants and has not achieved.
- **A characterization of the error floor.** Establishing whether QC-MDPC
  bit-flipping decoders have a floor above `2^{-128}`, and where, would settle the
  question empirically-plus-analytically without needing to reach the rate.
- **Structural avoidance.** A CCA transform whose security does not depend on the
  DFR at all -- the cleanest fix, and the reason HQC's different failure structure
  was preferred.

A cheaper diagnostic first step, well within this program's competence: take the
published DFR model, fit it to the *measured* range only, and report the width of
the prediction interval at `2^{-128}`. If that interval is unbounded in practice,
that fact is itself worth recording, and it requires no new cryptanalysis. Not
attempted here.
