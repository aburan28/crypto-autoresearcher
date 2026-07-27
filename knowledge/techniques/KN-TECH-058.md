---
id: KN-TECH-058
type: technique
title: McEliece and Niederreiter trapdoors - the binary Goppa instantiation
tags: [code-based, mceliece, niederreiter, goppa, kem, trapdoor, pqc, key-size, implementation, constant-time]
confidence: reported
complexity: keygen/encap/decap polynomial; public key size Theta(k(n-k)) bits generic, ~10^5-10^6 bytes at deployed parameters; ciphertext ~10^2 bytes in Niederreiter form
applicability: Classic McEliece and every binary-Goppa variant; the reference point against which structured-key variants trade size for risk
source_refs: [KN-LIT-7564, KN-LIT-7565, KN-LIT-7573, KN-LIT-2607, KN-LIT-4873, KN-LIT-3946, KN-LIT-4874, KN-LIT-6187, KN-LIT-4915, KN-LIT-4912, KN-LIT-6614]
added: 2026-07-27
superseded_by: null
---

## The construction
Pick a binary Goppa code with a secret support and Goppa polynomial; it corrects
`t` errors and has an efficient algebraic decoder. Publish a scrambled
description of it. An attacker who cannot recognize the code must decode
generically (KN-TECH-057); the holder of the support and polynomial decodes in
polynomial time.

Two dual forms:

- **McEliece (primal, KN-LIT-7564).** Public key `G' = SGP`. Ciphertext
  `c = mG' + e`. Ciphertext is a full codeword.
- **Niederreiter (dual, KN-LIT-7565).** Public key `H' = SHP` (systematic form,
  so only the non-identity part is stored). Message is encoded *as* a
  fixed-weight error vector; ciphertext is its syndrome -- short.

Modern deployments use the Niederreiter form with a systematic public key, plus
an implicit-rejection CCA2 conversion (KN-LIT-7573).

## Why binary Goppa specifically
Goppa codes are the one family from the 1978 proposal that has survived. The
reason is negative rather than positive: they resist the structural attacks that
killed every more transparent alternative (KN-TECH-059). There is no reduction
showing scrambled Goppa matrices are indistinguishable from random -- the
assumption is empirical, and the known distinguisher for *high-rate* Goppa codes
(KN-LIT-2395) is the standing reason not to treat it as settled (KN-OPEN-021).

## The key-size problem, and the trade that follows
An unstructured public key costs `Theta(k(n-k))` bits. At category-5 parameters
that is around a megabyte (KN-LIT-7573). Every attempt to fix this adds
structure -- quasi-cyclic, quasi-dyadic, automorphism-induced (KN-LIT-6187),
LDPC/MDPC (KN-TECH-060) -- and every added structure is a new attack surface.
The corpus records both ends: KN-LIT-2395 and KN-LIT-2383 break compact-key and
special-polynomial variants algebraically; BIKE and HQC survive with quasi-cyclic
structure but pay with a decoding failure rate instead.

**The general shape is worth stating plainly**, because it recurs outside
code-based crypto: efficiency gained by adding algebraic structure to a hard
instance is efficiency borrowed against the structural-attack surface, and the
loan is called in unpredictably. Compare the overstretched-NTRU fatigue point
(KN-TECH-045) on the lattice side.

## Implementation
Constant-time implementation is a solved but delicate problem: the decoder's
control flow is naturally secret-dependent. KN-LIT-4873 (McBits) is the
reference for fast constant-time code-based primitives; KN-LIT-3946 covers
hardware key generation, which is the expensive operation. Physical attacks are
live: KN-LIT-4912 (laser fault injection on Classic McEliece) and KN-LIT-6614
(side-channel-assisted ISD against the reference hardware implementation) both
recover plaintext or key material without touching the mathematical assumption.
KN-LIT-4874 reports resistance to quantum Fourier sampling, closing one specific
quantum structural route.

## Applicability limits
Nothing here has been implemented or measured in this program. Size figures are
as reported in KN-LIT-7573 and were not recomputed. The claim that binary Goppa
"resists" structural attacks is a statement about the absence of a published
break at deployed parameters, not a proof, and KN-OPEN-021 states precisely what
remains open.
