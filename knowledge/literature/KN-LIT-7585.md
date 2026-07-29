---
id: KN-LIT-7585
type: literature
title: 'ZKPoSP: Post-Quantum Zero-Knowledge Proofs for Hierarchical Deterministic Wallets'
authors:
  - "Vincenzo Botta"
  - "Michal Pospieszalski"
  - "Emanuele Ragnoli"
  - "Justus Ranvier"
year: 2026
venue: 'Cryptology ePrint Archive, Paper 2026/1508'
identifiers:
  eprint: iacr:2026/1508
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/1508
tags: [shor, ecdlp, migration, post-quantum, zk-proof, nizk, hd-wallet, bip32, ed25519, secp256k1, harvest-now-decrypt-later, applied]
confidence: reported
citation_verified: web
added: "2026-07-27"
superseded_by: null
---

## Contribution
Proposes keeping existing elliptic-curve blockchain address formats unchanged while
replacing the classical signing step with a NIZK proof of knowledge of the *seed*
underlying the address, so that security against quantum adversaries reduces to hash
hardness and NIZK soundness rather than to the ECDLP. Extends the single-level
observation of Baldimtsi et al. (that EdDSA's deterministic seed-to-key map makes the seed
a valid zero-knowledge witness for the public key) to the full hierarchical deterministic
wallet setting.

## Key claims (as reported)
- Motivation stated explicitly: a quantum computer running **Shor's algorithm recovers any
  elliptic-curve private key from the corresponding public key**, threatening every
  production wallet under BIP32/BIP44/SLIP-10.
- QBIP32: a new derivation scheme built on a keyed function HASH768 (instantiated with
  KMAC256) producing signing scalar, explicit quantum-safe witness, and chain code in one
  call — defined for **any** prime-order elliptic curve group with a fixed generator
  (secp256k1, Ed25519, future curves), unlike BIP32-Ed25519 which has no cross-curve
  analogue.
- ZKPoSP splits the proof into a derivation proof (once per key pair) and a signing proof
  (once per message), making per-message proving cost **constant in derivation depth**.
- Characterises exactly when the derivation proof can cover only the last derivation step:
  the criterion is the existence of a private value bound to the seed by a one-way
  function and not recoverable from the public key. Met by **hardened** keys, not by
  non-hardened keys (true across BIP32 secp256k1, SLIP-10/Ed25519, BIP32-Ed25519, QBIP32).
- Post-Q-day variant: once networks reject non-post-quantum signatures, the leaf scalar
  moves to the public statement, removing all EC scalar multiplications from the proof
  circuit.
- Implementation in Rust on RISC Zero; signing proving time ~12–13 s constant,
  verification ~9–10 ms constant across variants and depths.
- Post-quantum security is stated as **conjectured**, not proved.

## Relevance to this program
Recorded as an applied-consequence entry: it is what the downstream world does when it
takes the ECDLP's quantum breakability as settled. Its research value here is narrow but
real — it is a concrete instance of a *migration path that does not require the hard
problem to survive*, which is a different response to a broken assumption than parameter
growth.

- `KN-TECH-037` (quantum ECDLP resource estimation, Shor circuits for elliptic curves) is
  the technique entry in scope. This paper **consumes** that result and adds nothing to
  it: no resource estimate, no circuit, no new analysis of Shor's cost for `E(F_p)`.
- The abstract's framing — citing Google's Willow processor as having "substantially
  narrowed the timeline to cryptographically relevant quantum computers" — is a
  *motivational* claim of the kind this program does not accept without a resource
  estimate tied to a specific curve and error model. It is recorded as reported, and
  should not be cited as evidence about quantum timelines. `KN-TECH-037` remains the only
  entry the program should reason from on that question.

**Does not bear on the classical ECDLP.** Nothing here concerns the `sqrt(p)` barrier, the
index-calculus line, or any classical algorithm.

## Not verified here
Full paper not read; all claims relayed from the official ePrint abstract retrieved from
eprint.iacr.org on 2026-07-27 (hence `confidence: reported`). ePrint history: received
2026-07-23, approved 2026-07-25. Not peer-reviewed or formally published as of this entry;
no DOI on the ePrint page. Category: PROTOCOLS. Note the author list includes an
organisational affiliation ("AmericanFortress") in the ePrint author-display field; the
four individual authors above are taken from the paper's own BibTeX record.

NOT verified here: the EUF-CMA proof; the hardened/non-hardened criterion and its claimed
universality across BIP32/SLIP-10/QBIP32; the security of HASH768/KMAC256 as instantiated;
the RISC Zero benchmarks, their hardware, and whether ~12–13 s signing is viable in the
deployment settings claimed; and the conjectured post-quantum security, which by the
authors' own statement is not proved. The Baldimtsi et al. attribution was not checked.
**No claim about quantum timelines should be drawn from this entry.**
