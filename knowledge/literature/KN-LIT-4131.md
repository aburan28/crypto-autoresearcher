---
id: KN-LIT-4131
type: literature
title: "Group Action Key Encapsulation and Non-Interactive Key Exchange in the QROM Julien Duman , Dominik Hartmann , Eike Kiltz"
authors:
  - "Sabrina Kunzweiler"
  - "Jonas Lehmann"
  - "Doreen Riepel"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, finite-field, isogeny, lattice, pqc, protocol, provable-security, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In the context of quantum-resistant cryptography, cryptographic group actions offer an abstraction of isogeny-based cryptography in the Commutative Supersingular Isogeny Diffie-Hellman (CSIDH) setting. In this work, we revisit the security of two previously proposed natural protocols: the Group Action Hashed ElGamal key encapsulation mechanism (GA-HEG KEM) and the Group Action Hashed DiffieHellman non-interactive key-exchange (GA-HDH NIKE) protocol.

## Key claims (as reported)
- The latter protocol has already been considered to be used in practical protocols such as Post-Quantum WireGuard (S&P ’21) and OPTLS (CCS ’20).
- We prove that active security of the two protocols in the Quantum Random Oracle Model (QROM) inherently relies on very strong variants of the Group Action Strong CDH problem, where the adversary is given arbitrary quantum access to a DDH oracle.
- That is, quantum accessible Strong CDH assumptions are not only sufficient but also necessary to prove active security of the GA-HEG KEM and the GA-HDH NIKE protocols.
- Furthermore, we propose variants of the protocols with QROM security from the classical Strong CDH assumption, i.e., CDH with classical access to the DDH oracle.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910357 (1).pdf`
- `downloads/137910357.pdf`
