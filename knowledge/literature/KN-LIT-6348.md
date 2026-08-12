---
id: KN-LIT-6348
type: literature
title: "RSA–OAEP is Secure under the RSA Assumption"
authors:
  - "Eiichiro Fujisaki"
  - "Tatsuaki Okamoto"
  - "David Pointcheval"
  - "Jacques Stern"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Recently Victor Shoup noted that there is a gap in the widely-believed security result of OAEP against adaptive chosen-ciphertext attacks. Moreover, he showed that, presumably, OAEP cannot be proven secure from the one-wayness of the underlying trapdoor permutation.

## Key claims (as reported)
- This paper establishes another result on the security of OAEP.
- It proves that OAEP offers semantic security against adaptive chosenciphertext attacks, in the random oracle model, under the partial-domain one-wayness of the underlying permutation.
- Therefore, this uses a formally stronger assumption.
- Nevertheless, since partial-domain one-wayness of the RSA function is equivalent to its (full-domain) one-wayness, it follows that the security of RSA–OAEP can actually be proven under the sole RSA assumption, although the reduction is not tight.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/21390259 (1).pdf`
- `downloads/21390259 (2).pdf`
- `downloads/21390259.pdf`
