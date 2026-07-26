---
id: KN-LIT-3348
type: literature
title: "Curious case of Rowhammer: Flipping Secret Exponent Bits using Timing Analysis"
authors:
  - "Sarani Bhattacharya"
  - "Debdeep Mukhopadhyay"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, provable-security, rsa, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Rowhammer attacks have exposed a serious vulnerability in modern DRAM chips to induce bit flips in data which is stored in memory. In this paper, we develop a methodology to combine timing analysis to perform the hammering in a controlled manner to create bit flips in cryptographic keys which are stored in memory.

## Key claims (as reported)
- The attack would require only user level privilege for Linux kernel versions before 4.0 and is unaware of the memory location of the key.
- An intelligent combination of timing Prime + Probe attack and row-buffer collision is shown to induce bit flip faults in a 1024 bit RSA key on modern processors using realistic number of hammering attempts.
- This demonstrates the feasibility of fault analysis of ciphers using purely software means on commercial x86 architectures, which to the best of our knowledge has not been reported earlier.
- The attack is also relevant for the newest Linux kernel in a Cross-VM environment where the VMs having root privilege are not denied to access the pagemap.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98130221 (1).pdf`
- `downloads/98130221.pdf`
