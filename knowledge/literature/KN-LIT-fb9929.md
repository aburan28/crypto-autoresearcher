---
id: KN-LIT-fb9929
type: literature
title: "Low-Latency Elliptic Curve Scalar Multiplication"
authors:
  - "Joppe W. Bos"
year: null
venue: "manuscript (author's page, draft)"
identifiers:
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, scalar-multiplication, parallel, gpu, ecdlp, baseline]
confidence: reported
citation_verified: read
added: "2026-08-07"
superseded_by: null
---

## Contribution
Presents a low-latency algorithm for elliptic-curve scalar multiplication
for parallel computer architectures (GPU implementation on the NVIDIA GTX 500
family), built on side-channel-analysis approaches. A standardized curve over
a 224-bit prime field (112-bit security level) computes one scalar
multiplication in 1.9 ms.

## Key claims (as reported)
- 1.9 ms scalar multiplication on the NVIDIA GTX 500 family for a 224-bit
  curve.
- Methods and implementation considerations apply to any parallel 32-bit
  architecture; the approach is latency-oriented rather than throughput-
  oriented.
- Not a constant-time claim; it is a fast parallel arithmetic result.

## Relevance
- Demonstrates the practical cost of the arithmetic inside an ECDLP baseline
  when parallel hardware is available. Useful as a cost-modeling data point
  for the baseline/allowed-arithmetic discussions in the program.

## Not verified here
- Benchmarks relayed from the draft; not reproduced. Authorship inferred from
  the manuscript header (Joppe W. Bos).