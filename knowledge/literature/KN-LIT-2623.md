---
id: KN-LIT-2623
type: literature
title: "Attribute-Based Signatures for Unbounded Languages from Standard Assumptions"
authors:
  - "Yusuke Sakai"
  - "Shuichi Katsumata"
  - "Nuttapong Attrapadung"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Attribute-based signature (ABS) schemes are advanced signature schemes that simultaneously provide fine-grained authentication while protecting privacy of the signer. Previously known expressive ABS schemes support either the class of deterministic finite automata and circuits from standard assumptions or Turing machines from the existence of indistinguishability obfuscations.

## Key claims (as reported)
- In this paper, we propose the first ABS scheme for a very general policy class, all deterministic Turing machines, from a standard assumption, namely, the Symmetric External Diffie-Hellman (SXDH) assumption.
- We also propose the first ABS scheme that allows nondeterministic finite automata (NFA) to be used as policies.
- Although the expressiveness of NFAs are more restricted than Turing machines, this is the first scheme that supports nondeterministic computations as policies.
- Our main idea lies in abstracting ABS constructions and presenting the concept of history of computations; this allows a signer to prove possession of a policy that accepts the string associated to a message in zero-knowledge while also hiding the policy, regardless of the computational model being used.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11272203 (1).pdf`
- `downloads/11272203.pdf`
