---
id: KN-LIT-1325
type: literature
title: "A Compact Post-quantum Strong Designated Verifier Signature Scheme from Isogenies"
authors:
  - "Farzin Renan"
year: 2025
venue: "arXiv preprint"
identifiers:
  eprint: "iacr:2025/1335"
  doi: null
  arxiv: "2507.14893"
  url: "https://arxiv.org/abs/2507.14893"
tags: [class-group, dlp, elliptic-curve, factoring, isogeny, lattice, number-theory, pairing, pqc, provable-security, quantum, signature, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Digital signatures are fundamental cryptographic tools that provide authentication and integrity in digital communications. However, privacy-sensitive applications—such as e-voting and digital cash—require more restrictive verification models to ensure confidentiality and control.

## Key claims (as reported)
- Strong Designated Verifier Signature (SDVS) schemes address this need by enabling the signer to designate a specific verifier, ensuring that only this party can validate the signature.
- Existing SDVS constructions are primarily based on number-theoretic assumptions and are therefore vulnerable to quantum attacks.
- Although post-quantum alternatives—particularly those based on lattices—have been proposed, they often entail large key and signature sizes.
- In this work, we present CSI-SDVS, a novel isogeny-based SDVS scheme that offers a compact, quantum-resistant alternative to existing SDVS constructions.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-1335.pdf`
- `downloads/2507.14893v3.pdf`
