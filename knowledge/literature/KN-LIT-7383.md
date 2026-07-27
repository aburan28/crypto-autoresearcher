---
id: KN-LIT-7383
type: literature
title: "Universal Designated-Verifier Signatures"
authors:
  - "Ron Steinfeld"
  - "Laurence Bull"
  - "Huaxiong Wang"
  - "Josef Pieprzyk"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Motivated by privacy issues associated with dissemination of signed digital certificates, we define a new type of signature scheme called a ‘Universal Designated-Verifier Signature’ (UDVS). A UDVS scheme can function as a standard publicly-verifiable digital signature but has additional functionality which allows any holder of a signature (not necessarily the signer) to designate the signature to any desired designatedverifier (using the verifier’s public key).

## Key claims (as reported)
- Given the designated-signature, the designated-verifier can verify that the message was signed by the signer, but is unable to convince anyone else of this fact.
- We propose an efficient deterministic UDVS scheme constructed using any bilinear group-pair.
- Our UDVS scheme functions as a standard Boneh-Lynn-Shacham (BLS) signature when no verifier-designation is performed, and is therefore compatible with the key-generation, signing and verifying algorithms of the BLS scheme.
- We prove that our UDVS scheme is secure in the sense of our unforgeability and privacy notions for UDVS schemes, under the Bilinear Diffie-Hellman (BDH) assumption for the underlying group-pair, in the random-oracle model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/UDVS_asia03_final_1 (1).pdf`
- `downloads/UDVS_asia03_final_1 (2).pdf`
- `downloads/UDVS_asia03_final_1.pdf`
