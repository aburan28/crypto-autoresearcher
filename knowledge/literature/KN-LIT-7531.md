---
id: KN-LIT-7531
type: literature
title: "XPX: Generalized Tweakable Even-Mansour with Improved Security Guarantees"
authors:
  - "Bart Mennink"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present XPX, a tweakable blockcipher based on a single permutation P . On input of a tweak (t11 , t12 , t21 , t22 ) ∈ T and a message m, it outputs ciphertext c = P (m⊕∆1 )⊕∆2 , where ∆1 = t11 k ⊕t12 P (k) and ∆2 = t21 k ⊕ t22 P (k).

## Key claims (as reported)
- Here, the tweak space T is required to satisfy a certain set of trivial conditions (such as (0, 0, 0, 0) 6∈ T ).
- We prove that XPX with any such tweak space is a strong tweakable pseudorandom permutation.
- Next, we consider the security of XPX under related-key attacks, where the adversary can freely select a key-deriving function upon every evaluation.
- We prove that XPX achieves various levels of related-key security, depending on the set of key-deriving functions and the properties of T .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98140061 (1).pdf`
- `downloads/98140061.pdf`
