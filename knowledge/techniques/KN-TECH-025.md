---
id: KN-TECH-025
type: technique
title: SIDH/SIKE key exchange and the torsion-point-image structure
tags: [sidh, sike, key-exchange, torsion-points, auxiliary-information, isogeny, broken, adjacent]
confidence: established
complexity: broken - classical polynomial-time key recovery (Robert, all cases); pre-break generic isogeny cost was ~O(p^{1/4})
applicability: two-party key exchange by commuting secret isogenies over F_{p^2}, publishing torsion-basis images
source_refs: [KN-LIT-062, KN-LIT-064, KN-LIT-076]
added: 2026-07-23
superseded_by: null
---

## Method
In SIDH, Alice and Bob each pick a secret cyclic subgroup (of order 2^a resp.
3^b), quotient by it to get a secret isogeny phi over F_{p^2}, and exchange the
IMAGE CURVE plus the IMAGES OF THE OTHER PARTY'S TORSION BASIS under their secret
isogeny. Those auxiliary images let each party re-quotient on the other's curve to
reach a common j-invariant. SIKE (KN-LIT-064) is the FO-transformed CCA KEM.

## Why the torsion images are the flaw
Publishing phi(P), phi(Q) for a known basis P,Q of the (coprime-order) torsion is
extra structure absent from the general isogeny problem. Petit (KN-LIT-077) showed
in 2017 this weakens unbalanced parameters; GPST (KN-LIT-076) showed adaptive
misuse breaks static keys; in 2022 it enabled full polynomial-time key recovery
(KN-TECH-026). The degrees are also unbalanced and known, which the attacks need.

## Relevance to this program
The clearest modern case of the program's central theme: AUXILIARY INFORMATION
collapsing a conjectured-hard problem (KN-OPEN-015). Methodologically identical in
spirit to the program's ECDLP "does published structure lower the complexity
driver?" questions (KN-OPEN-005). Adjacent to the ECDLP mission (supersingular
isogeny setting).

## Applicability limits
The break is SPECIFIC to schemes that reveal torsion-point images at known,
unbalanced degrees (SIDH, SIKE, Seta, B-SIDH). Schemes that reveal no torsion
images -- CGL (KN-TECH-024), CSIDH (KN-TECH-027), SQIsign (KN-TECH-028) -- are
untouched. This is a statement about the protocol's leaked structure, not about
generic isogeny hardness.
