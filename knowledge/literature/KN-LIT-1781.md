---
id: KN-LIT-1781
type: literature
title: "On the Formal Verification of Authenticated Encryption of the MQTT Protocol"
authors:
  - "Varsha Jarali"
  - "Shashi Kant Pandey"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1020"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1020"
tags: [ecdsa, elliptic-curve, lattice, protocol, signature, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Message Queuing Telemetry Transport (MQTT) protocol is highly preferable for Internet of Things (IoT) environments due to its lightweight architecture, but routing sensitive medical data through a central broker introduces severe privacy risks if the broker is untrusted or compromised. To address this, we propose secure MQTT, a high performance end to end encrypted (E2EE) protocol tailored for constrained devices that renders the broker completely blind to message payloads and incapable of man in the middle (MitM) attacks.

## Key claims (as reported)
- Our design utilizes a nested AES-GCM encryption architecture that strictly separates linklevel routing metadata from application layer confidentiality.
- To establish these secure channels efficiently, MQTT integrates MQTT v5.0 enhanced authentication key exchange mechanism via a challenge response embedding one time Broker Nonce into the Schnorr digital signatures version of HMQV key exchange protocol.
- This provide authenticated end to end session key derivation, that requires only a negligible computational increase over basic ECDH.
- The security of this proposed model has been rigorously proven using the ProVerif cryptographic verifier under the Dolev-Yao threat model, offering a highly secure, low overhead solution for modern IoT networks.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1020.pdf`
