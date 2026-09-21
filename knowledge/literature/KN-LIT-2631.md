---
id: KN-LIT-2631
type: literature
title: "Authenticated Key Exchange and Key Encapsulation in the Standard Model"
authors:
  - "Tatsuaki Okamoto"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, protocol, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper introduces a new paradigm to realize various types of cryptographic primitives such as authenticated key exchange and key encapsulation in the standard model under three standard assumptions: the decisional DiffieHellman (DDH) assumption, target collision resistant (TCR) hash functions and pseudo-random functions (PRFs). We propose the first (PKI-based) two-pass authenticated key exchange (AKE) protocol that is comparably as efficient as the existing most efficient protocols like MQV and that is secure in the standard model (under these standard assumptions), while the existing efficient two-pass AKE protocols such as HMQV, NAXOS and CMQV are secure in the random oracle model.

## Key claims (as reported)
- Our protocol is shown to be secure in the (currently) strongest security definition, the extended Canetti-Krawczyk (eCK) security definition introduced by LaMacchia, Lauter and Mityagin.
- This paper also proposes a CCA-secure key encapsulation mechanism (KEM) under these assumptions, which is almost as efficient as the Kurosawa-Desmedt KEM.
- This scheme is also secure in a stronger security notion, the chosen public-key and ciphertext attack (CPCA) security.
- The proposed schemes in this paper are redundancy-free (or validity-check-free) and the implication is that combining them with redundancy-free symmetric encryption (DEM) will yield redundancy-free (e.g., MAC-free) CCA-secure hybrid encryption.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/48330477 (1).pdf`
- `downloads/48330477 (2).pdf`
- `downloads/48330477 (3).pdf`
- `downloads/48330477.pdf`
