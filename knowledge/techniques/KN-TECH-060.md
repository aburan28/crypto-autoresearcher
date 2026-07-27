---
id: KN-TECH-060
type: technique
title: QC-MDPC schemes and decoding-failure (reaction) attacks
tags: [code-based, qc-mdpc, bike, hqc, decoding-failure, dfr, reaction-attack, weak-keys, bit-flipping, ind-cca, extrapolation, cryptanalysis]
confidence: reported
complexity: attack cost is dominated by the number of decapsulation queries needed to observe enough failures; scales as ~1/DFR, so security requires DFR below the security level
applicability: BIKE, HQC, LEDA-family, and any scheme whose decryption can fail with key-dependent probability
source_refs: [KN-LIT-7574, KN-LIT-2085, KN-LIT-3735, KN-LIT-2141, KN-LIT-5730, KN-LIT-1963, KN-LIT-6056, KN-LIT-6708, KN-LIT-6365, KN-LIT-7575]
added: 2026-07-27
superseded_by: null
---

## The trade
Quasi-cyclic MDPC codes shrink the public key from ~10^6 bytes to ~10^3 by making
the parity-check matrix quasi-cyclic and moderate-density. The price: decoding is
iterative (bit-flipping, and refinements such as Black-Gray-Flip) and **fails
with nonzero probability**. That failure probability is the attack surface.

## The GJS reaction attack
KN-LIT-2085 (Guo-Johansson-Stankovski, ASIACRYPT 2016) is the defining result.
The decoding failure probability depends on the secret key -- specifically on the
key's *distance spectrum*, the multiset of distances between its nonzero
positions. An attacker who can observe whether decapsulation succeeded, over many
chosen ciphertexts, reconstructs the distance spectrum and then the key.

Two properties make this important beyond its own scheme:

1. **It defeats a CCA proof.** The schemes attacked carried IND-CCA proofs. The
   proofs were not wrong; their model simply did not include decoding failure.
   A security proof bounds only what its model represents.
2. **It needs only a reaction.** Success/failure is enough -- no plaintext, no
   timing, no fault. Any observable correlated with failure is sufficient.

Related and subsequent: KN-LIT-3735 (weak-key classes and key recovery in BIKE),
KN-LIT-5730 (partial key exposure), KN-LIT-2141 (a decryption-failure attack
against HQC), KN-LIT-6365 (side-channel-assisted variants via an LDPC framework).

## The extrapolation problem
IND-CCA therefore requires DFR below the security level -- for category 1, on the
order of `2^{-128}`. **No such rate can be measured.** Simulation reaches perhaps
`2^{-30}` before the compute cost is prohibitive; the claim at `2^{-128}` is an
extrapolation from a fitted model of the decoder's error behaviour, and the
existence of weak-key classes (KN-LIT-3735) and error floors means the tail is
not guaranteed to follow the fitted body.

This is a security claim resting on curve-fitting far outside the measured range
— exactly the failure mode KN-TECH-052 exists to police in this program's own
work. When the program evaluates any DFR-style claim, its own rules apply: state
the model, state the measured range, state the extrapolation factor, and do not
present the extrapolated value with the confidence of a measured one.
KN-OPEN-022 records what would actually settle it.

NIST's round-4 reasoning tracks this directly: HQC was preferred over BIKE on
maturity of the security analysis, with the decoding-failure story the
distinguishing issue (KN-LIT-7575).

## Cross-domain note
This is the code-based counterpart of KN-TECH-048 (decryption-failure attacks and
failure boosting against lattice KEMs). The mechanisms differ -- key-dependent
decoder behaviour versus noise-distribution tails -- but the shape is identical:
a rare, key-correlated failure event, amplified by chosen ciphertexts, defeating
a CCA proof whose model omitted it. Two independent instances of the same
epistemic failure is a strong argument for treating "the model omits a rare
event" as a standing review question rather than a scheme-specific one.

## Applicability limits
No DFR was measured or decoder implemented in this program. All attack costs and
failure rates are `reported`. The `~1/DFR` query scaling is the shape given in
secondary summaries, not a bound checked here.
