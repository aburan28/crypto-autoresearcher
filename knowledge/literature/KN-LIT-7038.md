---
id: KN-LIT-7038
type: literature
title: "The Power of Proofs-of-Possession: Securing Multiparty Signatures against Rogue-Key Attacks"
authors:
  - "Thomas Ristenpart"
  - "Scott Yilek"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, rsa, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Multiparty signature protocols need protection against roguekey attacks, made possible whenever an adversary can choose its public key(s) arbitrarily. For many schemes, provable security has only been established under the knowledge of secret key (KOSK) assumption where the adversary is required to reveal the secret keys it utilizes.

## Key claims (as reported)
- In practice, certifying authorities rarely require the strong proofs of knowledge of secret keys required to substantiate the KOSK assumption.
- Instead, proofs of possession (POPs) are required and can be as simple as just a signature over the certificate request message.
- We propose a general registered key model, within which we can model both the KOSK assumption and in-use POP protocols.
- We show that simple POP protocols yield provable security of Boldyreva’s multisignature scheme [11], the LOSSW multisignature scheme [28], and a 2-user ring signature scheme due to Bender, Katz, and Morselli [10].

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/45150228 (1).pdf`
- `downloads/45150228 (2).pdf`
- `downloads/45150228 (3).pdf`
- `downloads/45150228.pdf`
