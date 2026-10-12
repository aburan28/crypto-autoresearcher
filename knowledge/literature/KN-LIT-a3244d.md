---
id: KN-LIT-a3244d
type: literature
title: >-
  The Dark Side of "Black-Box" Cryptography, or: Should We Trust Capstone?
authors:
  - "Adam Young"
  - "Moti Yung"
year: 1996
venue: "Advances in Cryptology -- CRYPTO '96, LNCS 1109, pp. 89-103"
identifiers:
  eprint: null
  doi: "10.1007/3-540-68697-5_8"
  arxiv: null
  url: "https://link.springer.com/chapter/10.1007/3-540-68697-5_8"
tags: [kleptography, setup, young-yung, subverted-implementation, key-generation, subliminal-channel, escrow, rsa, elgamal, dsa]
confidence: reported
citation_verified: web
added: "2026-10-01"
superseded_by: null
---

## Contribution

Introduces the **SETUP** (Secretly Embedded Trapdoor with Universal
Protection): a mechanism embedded in a black-box cryptographic device or
library that lets the manufacturer recover the user's secret from the
device's ordinary output, undetectably, while the embedded trapdoor is
itself protected against other attackers and against reverse engineering
(the attacker's own public key is inside the device, so only the attacker's
private key opens the leak).

Abstract, verbatim from the publisher page: "The use of cryptographic
devices as 'black boxes', namely trusting their internal designs, has been
suggested and in fact Capstone technology is offered as a next generation
hardware-protected escrow encryption technology. Software cryptographic
servers and programs are being offered as well, for use as library
functions, as cryptography gets more and more prevalent in computing
environments. The question we address in this paper is how the usage of
cryptography as a black box exposes users to various threats and attacks
that are undetectable in a black-box environment. We present the SETUP
(Secretly Embedded Trapdoor with Universal Protection) mechanism, which can
be embedded in a cryptographic black-box device. It enables an attacker (the
manufacturer) to get the user's secret (from some stage of the output
process of the device) in an unnoticeable fashion, yet protects against
attacks by others and against reverse engineering (thus, maintaining the
relative advantage of the actual attacker). We also show how the SETUP can,
in fact, be employed for the design of 'auto-escrowing key' systems. We
present embeddings of SETUPs in RSA, El-Gamal, DSA, and private key systems
(Kerberos). We implemented an RSA key-generation based SETUP that performs
favorably when compared to PGP, a readily available RSA implementation. We
also relate message-based SETUPs and subliminal channel attacks. Finally,
we reflect on the potential implications of 'trust management' in the
context of the design and production of cryptosystems."

## Key claims (as reported)

- SETUPs are given for RSA key generation, ElGamal, DSA and Kerberos; the
  RSA one was implemented and benchmarked against PGP.
- The leak is through the normal output (keys, signatures), not a side
  channel, and is indistinguishable from honest output to anyone without
  the attacker's private key.

## Relevance to this program

Primary source, with its sequel `KN-LIT-9d845c`, for `KN-TECH-257dbc`
(kleptographic SETUPs in elliptic-curve key and nonce generation). It is the
origin of the "attacker public key inside the implementation" row of the
hiding-criterion table in `KN-TECH-6ead00`, and the historical reason the
taxonomy includes implementation-level backdoors at all: most deployed "ECC
backdoors" have been of this kind rather than mathematical.
