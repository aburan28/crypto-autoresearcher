# Recipient-mechanism composition — BATCH-d92210

This zero-run design/search round attempted two materially different recipient mechanisms for the objective of a novel EndRing-based PKE with QPT/QROM security and a NIST Category 5 target. Neither candidate is a complete PKE and neither proceeds to implementation or parameter selection.

## Method

The frozen methodology was: propose at most two mechanisms, package each against O1–O6, review independent joints J1–J6, then copy the sole-owner verdicts without voting. Novelty, quantum security, and Category 5 are separate gates. The round used zero scientific, implementation, formalizer, benchmark, and parameter-selection runs.

The composed joint vector is:

| Joint | Verdict | Narrow scope |
|---|---|---|
| J1 | breaks | M1 is inconclusive; M2 does not require a recipient secret. |
| J2 | inconclusive | Operation changes exist, but novelty is unverified. |
| J3 | inconclusive | Neither exact-law simulator is complete. |
| J4 | breaks | Neither attacker-to-complete-EndRing reduction is typed. |
| J5 | breaks | M1 lacks a QPT theorem; M2 has a passive public recovery. |
| J6 | inconclusive | Complete costs and a Category-5 case are unavailable. |

## Candidate M1: LABELLED-NORM-HOM-LIFT

The public sender forms `a=m+Mr`, the cyclic kernel `K_a=<P+[a]Q>`, and the endpoint ciphertext `j(E/K_a)`. The proposed recipient would use a complete evaluable basis of `End(E)` to construct `Hom(E,C)`, enumerate all norm-`L` maps, and recover the unique residue modulo `M`.

That recipient algorithm is only a name. The packet does not supply a polynomial, distribution-matched key sampler; a complete Hom lift; a complete norm enumeration; or a bound showing endpoint fibers contain one message residue. Its exact finite reference decoder publicly enumerates every `a` in `[0,L)`, so polynomial-size `L` gives no asymmetry. Most importantly, no successful QPT message distinguisher is converted into a complete evaluable EndRing basis.

All O1–O6 remain open. This is a useful construction gap, not a PKE or an impossibility result.

## Candidate M2: simultaneous full-module conjugation

The sender samples `S`, publishes `X=SUS^-1` and `Y=SVS^-1`, and masks the message using a hash of the normalized projective class of `S`. Because `U,V` generate `M_2(F_ell)`, the public equations `XT=TU` and `YT=TV` have solution space exactly `F_ell S`. Public Gaussian elimination therefore recovers the same normalized value used in the mask.

Conditional actual-message correctness is established for accepted keys, but it is public correctness: one ordinary hash query and no decryption query recover the message, with advantage `1/2` for distinct challenge messages. O4 is contradicted for this exact syntax. An integral lift cannot repair a pad already determined by public finite matrices.

This rejects the submitted construction, not every module-based or EndRing-based design.

## Objective status and next boundary

No reviewed candidate establishes novelty, a complete PKE, QPT/QROM security, a correct-direction reduction to complete EndRing, or Category 5. No parameters were selected and no concrete attack-resource lower bound was measured.

The next admissible idea would need a materially new sender/recipient relation that simultaneously:

1. lets the public sender compute encryption without the ring;
2. gives the complete ring holder an exact polynomial-time operation unavailable from public finite data or a smaller witness;
3. proves actual-message correctness over the exact key/ciphertext law; and
4. reduces a QPT attacker in the correct direction to recovery of a complete evaluable saturated endomorphism ring, with explicit losses and resources.

This batch authorizes no automatic successor. Its result is the preserved pair of negative/inconclusive attempts and the narrowed interface obligations.

## Review-procedure boundary

The frozen independence checker exited 1 with eight diagnostics: two reports omit `review_attestation.task_id`; their four owned joints and the blind rederivation are not mechanically recognized; J7 belongs to the later documentation review. That failure is preserved and is not described as a pass. It is an administrative limitation, not a replacement for or reversal of the sourced mathematical verdicts.

The authoritative machine-readable composition is [composition.yaml](composition.yaml). Source reviews are `TASK-20261013-962e06`, `TASK-20261013-235da3`, and `TASK-20261013-0e9c61`, frozen by `TASK-20261013-b65fe8` under `EV-SSI-235d01` and `DEC-20261013-b60218`.
