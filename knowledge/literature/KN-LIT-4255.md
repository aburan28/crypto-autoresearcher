---
id: KN-LIT-4255
type: literature
title: "How Risky is the Random-Oracle Model?"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, elliptic-curve, hash, provable-security, rsa, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
RSA-FDH and many other schemes secure in the RandomOracle Model (ROM) require a hash function with output size larger than standard sizes. We show that the random-oracle instantiations proposed in the literature for such cases are weaker than a random oracle, including the proposals by Bellare and Rogaway from 1993 and 1996, and the ones implicit in IEEE P1363 and PKCS standards: for instance, we obtain a 267 preimage attack on BR93 for 1024-bit digests.

## Key claims (as reported)
- Next, we study the security impact of hash function defects for ROM signatures.
- As an extreme case, we note that any hash collision would suffice to disclose the master key in the ID-based cryptosystem by Boneh et al. from FOCS ’07, and the secret key in the Rabin-Williams signature for which Bernstein proved tight security at EUROCRYPT ’08.
- Interestingly, for both of these schemes, a slight modification can prevent these attacks, while preserving the ROM security result.
- We give evidence that in the case of RSA and Rabin/Rabin-Williams, an appropriate PSS padding is more robust than all other paddings known.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/56770440 (1).pdf`
- `downloads/56770440 (2).pdf`
- `downloads/56770440 (3).pdf`
- `downloads/56770440.pdf`
