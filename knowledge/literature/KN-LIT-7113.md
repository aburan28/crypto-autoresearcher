---
id: KN-LIT-7113
type: literature
title: "Threshold Password-Authenticated Key Exchange"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, protocol, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
) Philip MacKenzie1 , Thomas Shrimpton2 , and Markus Jakobsson3 1 Bell Laboratories Lucent Technologies Murray Hill, NJ 07974 USA philmac@lucent.com 2 Dept. of Electrical and Computer Engineering UC Davis Davis, CA 95616 USA teshrim@ucdavis.edu 3 RSA Laboratories RSA Security, Inc. Bedford, MA 01730 USA mjakobsson@rsasecurity.com Abstract.

## Key claims (as reported)
- In most password-authenticated key exchange systems there is a single server storing password verification data.
- To provide some resilience against server compromise, this data typically takes the form of a one-way function of the password (and possibly a salt, or other public values), rather than the password itself.
- However, if the server is compromised, this password verification data can be used to perform an offline dictionary attack on the user’s password.
- In this paper we propose an efficient password-authenticated key exchange system involving a set of servers, in which a certain threshold of servers must participate in the authentication of a user, and in which the compromise of any fewer than that threshold of servers does not allow an attacker to perform an offline dictionary attack.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/24420387 (1).pdf`
- `downloads/24420387 (2).pdf`
- `downloads/24420387.pdf`
