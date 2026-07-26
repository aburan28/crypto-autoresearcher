---
id: KN-LIT-6300
type: literature
title: "Robuster Combiners for Oblivious Transfer"
authors:
  - "Remo Meier"
  - "Bartosz Przydatek"
  - "Jürg Wullschleger"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, mpc, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A (k; n)-robust combiner for a primitive F takes as input n candidate implementations of F and constructs an implementation of F, which is secure assuming that at least k of the input candidates are secure. Such constructions provide robustness against insecure implementations and wrong assumptions underlying the candidate schemes.

## Key claims (as reported)
- In a recent work Harnik et al.
- (Eurocrypt 2005) have proposed a (2; 3)-robust combiner for oblivious transfer (OT), and have shown that (1; 2)-robust OT-combiners of a certain type are impossible.
- In this paper we propose new, generalized notions of combiners for two-party primitives, which capture the fact that in many two-party protocols the security of one of the parties is unconditional, or is based on an assumption independent of the assumption underlying the security of the other party.
- This fine-grained approach results in OT-combiners strictly stronger than the constructions known before.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/43920403 (1).pdf`
- `downloads/43920403 (2).pdf`
- `downloads/43920403 (3).pdf`
- `downloads/43920403.pdf`
