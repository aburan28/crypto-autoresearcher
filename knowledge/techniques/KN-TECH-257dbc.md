---
id: KN-TECH-257dbc
type: technique
title: >-
  Kleptographic SETUPs in elliptic-curve key and nonce generation (Young-Yung) -- an implementation that leaks the private key through ordinary-looking public values encrypted to the attacker
tags: [trapdoor, kleptography, setup, young-yung, subverted-implementation, nonce-leak, ecdsa, key-generation, cliptography, protocol-level, ecdlp]
confidence: reported
complexity: >-
  attacker with the embedded secret recovers the victim's key from one or two public values with one ECDH computation; outsider sees keys and signatures that are statistically indistinguishable from honest ones (under DDH on the curve) and would need the ECDLP to detect the leak
applicability: >-
  any black-box implementation the attacker controls (hardware tokens, closed-source libraries, firmware); defeated by deterministic, verifiable key generation and by the "cliptographic" countermeasures of KN-LIT-2923
source_refs: [KN-LIT-2923, KN-TECH-a7e9a8, KN-TECH-6ead00]
added: 2026-09-30
superseded_by: null
---

## Mechanism (Young and Yung, CRYPTO 1996 "The dark side of black-box cryptography" and EUROCRYPT 1997 "Kleptography: using cryptography against cryptography"; not yet KN-LIT entries)

A **SETUP** (Secretly Embedded Trapdoor with Universal Protection) is a
modified key-generation algorithm containing the attacker's public key `Y`.
Two canonical elliptic-curve instances:

1. **Key-pair SETUP.** The first key pair `(x_1, x_1 P)` is honest. The
   second is derived as `x_2 = H(x_1 * Y)`: the attacker, seeing `x_1 P` on
   the wire, computes `x_1 Y = y * (x_1 P)` with their own secret `y` and
   recovers `x_2`. To everyone else `x_2 P` is a random point.
2. **Nonce SETUP in ECDSA.** The signing nonce is `k = H(x * Y)` or a
   function of a previous nonce and `Y`; the attacker recovers `k` from the
   public data and then the signing key from one signature, since ECDSA is
   linear in `k`.

Indistinguishability from honest output follows from DDH on the curve, so
the subversion is undetectable by black-box testing. KN-LIT-2923
("Cliptography") is the systematic defence: split key generation between
components and re-randomize outputs so that no single component can embed a
channel.

## Why it is listed

It is not an ECDLP trapdoor: the curve and the DLP are untouched. It is
listed because it is the mechanism behind most deployed "ECC backdoors" and
because its secret, like Dual EC's (KN-TECH-a7e9a8), is a discrete-log
relation to a fixed attacker point: recovering the attacker's `y` from `Y`
would expose every victim, so an ECDLP advance is a detection tool here.

## Detectability

Black-box: none (DDH). White-box: the embedded `Y` and the hash call are
visible in source or firmware, which is why reproducible builds and open
implementations are the standard mitigation.

## Applicability limits

Requires the attacker to control the implementation. It says nothing about
the hardness of any mathematical problem and provides no research lead for
GOAL-ECTD-001; it is included so that the taxonomy (KN-TECH-6ead00) is
complete about what "backdoored ECC" has meant in practice.
