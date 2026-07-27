---
id: KN-LIT-7565
type: literature
title: Knapsack-type cryptosystems and algebraic coding theory
authors: [Niederreiter Harald]
year: 1986
venue: Problems of Control and Information Theory, 15(2):159-166
identifiers:
  eprint: null
  doi: null
  url: null
tags: [code-based, niederreiter, syndrome-decoding, goppa, pqc, foundational, trapdoor]
confidence: reported
citation_verified: web
added: 2026-07-27
superseded_by: null
---

## Contribution
Introduces the dual ("syndrome") form of the code-based trapdoor: the public key
is a scrambled parity-check matrix rather than a generator matrix, the plaintext
is encoded as a low-weight error vector, and the ciphertext is its syndrome.
This is the form used by every modern code-based KEM, because the ciphertext is
a syndrome (short) rather than a full codeword (long).

## Key claims (as reported)
- The syndrome form is equivalent in security to the generator form when
  instantiated with the same code family.
- The original proposal also suggested generalized Reed-Solomon codes, which was
  broken by KN-LIT-7569; the binary Goppa instantiation was not.

## Relevance to this program
The Niederreiter form is what Classic McEliece actually ships (KN-LIT-7573), so
any cost or parameter statement about "McEliece" in a modern context is normally
a statement about this construction. Recorded in KN-TECH-058. The
GRS-instantiation break is the canonical warning that the two security
assumptions of KN-LIT-7564 are independent: the same generic decoding hardness
sat behind both the broken and the surviving variant.

## Not verified here
Primary source not fetched (the journal is not open-access-indexed in the search
path used). Author, title, venue, volume/pages, and year confirmed via search
against secondary bibliographic records. The security-equivalence claim is
relayed, not checked.
