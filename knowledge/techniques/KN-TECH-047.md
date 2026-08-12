---
id: KN-TECH-047
type: technique
title: Integrating hints - lattice attacks with side information
tags: [hints, side-information, side-channel, primal-attack, sparsification, projection, decryption-failure, security-loss, leakage-budget, cross-domain, lattice]
confidence: reported
complexity: modifies the primal attack's lattice and success condition; cost is the resulting reduced block size, with security loss measured in bits as a function of hint count and quality
applicability: any lattice instance where partial information about the secret or error is available - side-channel leakage, decryption failures, or constraints imposed by the scheme itself
source_refs: [KN-LIT-118, KN-TECH-038, KN-TECH-019, KN-LIT-043, KN-OPEN-011, KN-OPEN-015]
added: 2026-07-24
superseded_by: null
---

## Method
Rather than treating leakage qualitatively, fold it into the lattice before
reduction. KN-LIT-118 generalises the primal attack (KN-TECH-038) to accept
"hints" about the secret or error and integrate them progressively, using
sparsification of the lattice, projection onto or intersection with hyperplanes,
and modification of the secret's distribution. The final lattice reduction then
runs on a smaller or better-conditioned instance, and the framework predicts the
resulting cost, so the leakage can be priced in bits rather than described.

The framework's scope is wider than side channels: the same machinery covers
information from decryption failures (KN-TECH-048) and structural constraints
imposed by particular schemes.

## Why this matters to a program working on both curves and lattices
This is the point where the program's two focus areas use the same instrument
in opposite directions.

- **On elliptic curves**, partial nonce leakage is turned into a hidden number
  problem and solved *with* lattice reduction (KN-TECH-019, KN-LIT-043). The
  lattice is the attacker's tool; the curve is the target.
- **On lattices**, partial secret leakage is folded into the lattice instance
  itself and consumed by reduction. The lattice is the target.

Both are instances of the theme the program has already isolated: auxiliary
information changes the complexity driver (KN-OPEN-015). The practical
consequence is a shared discipline -- a leakage claim in either domain is
incomplete without the quantity of leakage, the model that produced it, and the
resulting cost, and the framework here is what makes that quantification
possible on the lattice side. It is also the right tool for the defensive
leakage-budget work in the repository's ML-KEM line, where a soft-oracle budget
is only meaningful if leakage can be priced.

## Applicability limits
Predicted costs inherit every caveat of the primal attack: a GSA-based success
condition (KN-TECH-041), a cost convention (KN-TECH-040), and validation only in
dimensions far below deployed parameters. The framework assumes hints of
specific forms (perfect, modular, approximate); leakage that does not fit those
forms is not covered. Reported end-to-end applications are single-trace attacks
on specific implementations, so a security loss computed here is a statement
about an implementation and its leakage model, not about the scheme.

## Verified vs reported
The hint-integration techniques, the framework's stated scope, the Sage toolkit,
and the Frodo application are reported from KN-LIT-118's abstract; nothing was
run or reproduced. The cross-domain framing against the program's HNP work is
this program's own synthesis and is not a claim from the source.
