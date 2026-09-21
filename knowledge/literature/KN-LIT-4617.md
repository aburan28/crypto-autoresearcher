---
id: KN-LIT-4617
type: literature
title: "KyberSlash: Exploiting secret-dependent division timings in Kyber implementations"
authors:
  - "Daniel J. Bernstein∗"
  - "Karthikeyan Bhargavan"
  - "Shivam Bhasin ¶ ∗∗"
  - "Anupam Chattopadhyay ∥ ∗∗"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, implementation, pairing, pqc, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents KyberSlash1 and KyberSlash2 – two timing vulnerabilities in several implementations (including the official reference code) of the Kyber Post-Quantum Key Encapsulation Mechanism, currently undergoing standardization as ML-KEM. We demonstrate the exploitability of both KyberSlash1 and KyberSlash2 on two popular platforms: the Raspberry Pi 2 (Arm Cortex-A7) and the Arm Cortex-M4 microprocessor.

## Key claims (as reported)
- Kyber secret keys are reliably recovered within minutes for KyberSlash2 and a few hours for KyberSlash1.
- We responsibly disclosed these vulnerabilities to maintainers of various libraries and they have swiftly been patched.
- We present two approaches for detecting and avoiding similar vulnerabilities.
- First, we patch the dynamic analysis tool Valgrind to allow detection of variable-time instructions operating on secret data, and apply it to more than 1000 implementations of cryptographic primitives in SUPERCOP.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/kyberslash-20240628.pdf`
- `downloads/kyberslash-20250115.pdf`
