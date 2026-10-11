---
id: KN-LIT-9d845c
type: literature
title: "Kleptography: Using Cryptography Against Cryptography"
authors:
  - "Adam Young"
  - "Moti Yung"
year: 1997
venue: "Advances in Cryptology -- EUROCRYPT '97, LNCS 1233, pp. 62-74"
identifiers:
  eprint: null
  doi: "10.1007/3-540-69053-0_6"
  arxiv: null
  url: "https://link.springer.com/chapter/10.1007/3-540-69053-0_6"
tags: [kleptography, setup, young-yung, subverted-implementation, diffie-hellman, discrete-log, key-leak, forward-secrecy, rsa]
confidence: reported
citation_verified: web
added: "2026-10-01"
superseded_by: null
---

## Contribution

Abstract (verbatim from the publisher page): "The notion of a Secretly
Embedded Trapdoor with Universal Protection (SETUP) has been recently
introduced. In this paper we extend the study of stealing information
securely and subliminally from black-box cryptosystems. The SETUP mechanisms
presented here, in contrast with previous ones, leak secret key information
without using an explicit subliminal channel. This extends this area of
threats, which we call 'kleptography'."

This is the paper that names the field. Its technical advance over
`KN-LIT-a3244d` is a SETUP for **Diffie-Hellman** (and a strengthened one
for RSA) in which the leak needs no subliminal channel: the device derives
the next secret exponent from a Diffie-Hellman value shared with the
attacker's embedded public key, so the attacker recovers it from the public
exchange value alone. The paper uses the discrete logarithm as its one-way
function, embeds public-key cryptography in the device, and applies
"probabilistic bias removal" so the leaked values are uniformly
distributed, which also gives the attacker forward secrecy with respect to
the device's past outputs.

## Key claims (as reported)

- Discrete-log based SETUP for Diffie-Hellman key exchange that leaks the
  user's secret exponent through the public value, undetectably under the
  hardness of the DLP / DDH in the group.
- A strengthened RSA SETUP relative to the 1996 construction.

Not verified here: the exact leak schedule (which exchange leaks which
exponent) and the bias-removal construction. Read the full text before
citing those details.

## Relevance to this program

With `KN-LIT-a3244d`, the primary source for `KN-TECH-257dbc`. The
Diffie-Hellman SETUP is the direct ancestor of the elliptic-curve key-pair
and ECDSA-nonce SETUPs that entry describes, and of the Dual EC point-
relation trapdoor (`KN-TECH-a7e9a8`): in all of them the secret is a
discrete-log relation to a fixed attacker point, so an ECDLP advance would
be a *detection* tool here rather than an attack. `KN-LIT-2923`
("Cliptography") is the systematic defence.
