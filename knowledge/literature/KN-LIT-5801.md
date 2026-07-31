---
id: KN-LIT-5801
type: literature
title: "Post-Quantum Anonymous One-Sided Authenticated Key Exchange without Random Oracles"
authors:
  - "Ren Ishibashi"
  - "Kazuki Yoneyama"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, isogeny, lattice, pqc, protocol, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Authenticated Key Exchange (AKE) is a cryptographic protocol to share a common session key among multiple parties. Usually, PKI-based AKE schemes are designed to guarantee secrecy of the session key and mutual authentication.

## Key claims (as reported)
- However, in practice, there are many cases where mutual authentication is undesirable such as in anonymous networks like Tor and Riffle, or difficult to achieve due to the certificate management at the user level such as the Internet.
- Goldberg et al. formulated a model of anonymous one-sided AKE which guarantees the anonymity of the client by allowing only the client to authenticate the server, and proposed a concrete scheme.
- However, existing anonymous one-sided AKE schemes are only known to be secure in the random oracle model.
- In this paper, we propose generic constructions of anonymous one-sided AKE in the random oracle model and in the standard model, respectively.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/131770035 (1).pdf`
- `downloads/131770035.pdf`
