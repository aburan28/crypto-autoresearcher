---
id: KN-LIT-3640
type: literature
title: "Efficient Two-Party Secure Computation on Committed Inputs"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, mpc, provable-security, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present an efficient construction of Yao’s “garbled circuits” protocol for securely computing any two-party circuit on committed inputs. The protocol is secure in a universally composable way in the presence of malicious adversaries under the decisional composite residuosity (DCR) and strong RSA assumptions, in the common reference string model.

## Key claims (as reported)
- The protocol requires a constant number of rounds (four-five in the standard model, two-three in the random oracle model, depending on whether both parties receive the output), O(|C|) modular exponentiations per player, and a bandwidth of O(|C|) group elements, where |C| is the size of the computed circuit.
- Our technical tools are of independent interest.
- We propose a homomorphic, semantically secure variant of the Camenisch-Shoup verifiable cryptosystem, which uses shorter keys, is unambiguous (it is infeasible to generate two keys which successfully decrypt the same ciphertext), and allows efficient proofs that a committed plaintext is encrypted under a committed key.
- Our second tool is a practical four-round (two-round in ROM) protocol for committed oblivious transfer on strings (string-COT) secure against malicious participants.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/45150097 (1).pdf`
- `downloads/45150097 (2).pdf`
- `downloads/45150097 (3).pdf`
- `downloads/45150097.pdf`
