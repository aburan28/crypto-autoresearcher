---
id: KN-LIT-3387
type: literature
title: "Design and analysis of a distributed ECDSA signing service"
authors:
  - "Jens Groth"
  - "Victor Shoup"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, ecdsa, hash, mpc, pairing, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present and analyze a new protocol that provides a distributed ECDSA signing service, with the following properties: • it works in an asynchronous communication model; • it works with n parties with up to f < n/3 Byzantine corruptions; • it provides guaranteed output delivery; • it provides a very efficient, non-interactive online signing phase; • it supports additive key derivation according to the BIP32 standard. While there has been a flurry of recent research on distributed ECDSA signing protocols, none of these newly designed protocols provides guaranteed output delivery over an asynchronous communication network; moreover, the performance of our protocol (in terms of asymptotic communication and computational complexity) meets or beats the performance of any of these other protocols.

## Key claims (as reported)
- This service is being implemented and integrated into the architecture of the Internet Computer, enabling smart contracts running on the Internet Computer to securely hold and spend Bitcoin and other cryptocurrencies.
- Along the way, we present some results of independent interest: • a new asynchronous verifiable secret sharing (AVSS) scheme that is simple and efficient; • a new scheme for multi-recipient encryption that is simple and efficient.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/tecdsa.pdf`
