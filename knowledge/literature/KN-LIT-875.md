---
id: KN-LIT-875
type: literature
title: "Group Signatures and More from Isogenies and Lattices:"
authors: []
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/1366"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/1366"
tags: [isogeny, lattice, pqc, sidh-csidh, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct an efficient dynamic group signature (or more generally an accountable ring signature) from isogeny and lattice assumptions. Our group signature is based on a simple generic construction that can be instantiated by cryptographically hard group actions such as the CSIDH group action or an MLWE-based group action.

## Key claims (as reported)
- The signature is of size O(log N ), where N is the number of users in the group.
- Our idea builds on the recent efficient OR-proof by Beullens, Katsumata, and Pintore (Asiacrypt’20), where we efficiently add a proof of valid ciphertext to their OR-proof and further show that the resulting non-interactive zero-knowledge proof system is online extractable.
- Our group signatures satisfy more ideal security properties compared to previously known constructions, while simultaneously having an attractive signature size.
- The signature size of our isogeny-based construction is an order of magnitude smaller than all previously known post-quantum group signatures (e.g., 6.6 KB for 64 members).

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/132760233 (1).pdf`
- `downloads/132760233.pdf`
- `downloads/2021-1366.pdf`
