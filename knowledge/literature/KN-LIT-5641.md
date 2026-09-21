---
id: KN-LIT-5641
type: literature
title: "OpenSSLNTRU: Faster post-quantum TLS key exchange"
authors:
  - "Daniel J. Bernstein"
  - "Billy Bob Brumley"
  - "Ming-Shing Chen"
  - "Nicola Tuveri"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, implementation, lattice, pqc, protocol, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Google’s CECPQ1 experiment in 2016 integrated a post-quantum key-exchange algorithm, newhope1024, into TLS 1.2. The Google-Cloudflare CECPQ2 experiment in 2019 integrated a more efficient key-exchange algorithm, ntruhrss701, into TLS 1.3.

## Key claims (as reported)
- This paper revisits the choices made in CECPQ2, and shows how to achieve higher performance for post-quantum key exchange in TLS 1.3 using a higher-security algorithm, sntrup761.
- Previous work had indicated that ntruhrss701 key generation was much faster than sntrup761 key generation, but this paper makes sntrup761 key generation much faster by generating a batch of keys at once.
- Batch key generation is invisible at the TLS protocol layer, but raises software-engineering questions regarding the difficulty of integrating batch key exchange into existing TLS libraries and applications.
- This paper shows that careful choices of software layers make it easy to integrate fast post-quantum software, including batch key exchange, into TLS with minor changes to TLS libraries and no changes to applications.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/opensslntru-20211006.pdf`
