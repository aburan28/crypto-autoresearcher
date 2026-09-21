---
id: KN-LIT-6425
type: literature
title: "Secure Computation from One-Way Noisy Communication, or:"
authors:
  - "Anti-Correlation via Anti-Concentration"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Can a sender encode a pair of messages (m0 , m1 ) jointly, and send their encoding over (say) a binary erasure channel, so that the receiver can decode exactly one of the two messages and the sender does not know which one? (Crypto 2015) showed that this is information-theoretically impossible.

## Key claims (as reported)
- We show how to circumvent this impossibility by assuming that the receiver is computationally bounded, settling for an inversepolynomial security error (which is provably necessary), and relying on ideal obfuscation.
- Our solution creates a computational anti-correlation between the events of receiving m0 and receiving m1 by exploiting the anti-concentration of the binomial distribution.
- The ideal obfuscation primitive in our construction can either be directly realized using (stateless) tamper-proof hardware, yielding an unconditional result, or heuristically instantiated in the plain model using existing indistinguishability obfuscation schemes.
- As a corollary, we get similar feasibility results for general secure computation of sender-receiver functionalities by leveraging the completeness of the above random oblivious transfer functionality.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12826188 (1).pdf`
- `downloads/12826188.pdf`
