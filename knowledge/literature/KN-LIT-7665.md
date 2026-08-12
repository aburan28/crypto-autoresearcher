---
id: KN-LIT-7665
type: literature
title: "What Happens When integrating Modulus Switching and Lossy Source Coding: A New Dual Attack Variant on LWE"
authors:
  - "Yechen Li"
  - "Qunxiong Zheng"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/1400"
identifiers:
  eprint: "iacr:2026/1400"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1400"
tags: [dual-attack, dual-sieve-fft, lwe, kyber, ml-kem, modulus-switching, lossy-source-coding, concrete-security, cost-model, memory, multi-target]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
A new variant of the **dual-sieve-FFT attack** on LWE integrating **modulus switching**
with **lossy source coding**, following the MATZOV and Carrier et al. improvements.

The stated technical effect: the enumeration size in the FFT step falls from
`q^{n_fft}` to `p^{k_fft}` with `p < q` and `k_fft < n_fft`, lowering both FFT and
decoding cost.

## Key claims (as reported)
- Applied to **KYBER**, the variant achieves better **total** complexity than using
  lossy source coding alone — but the authors state the improvement is **modest**.
- Decoding cost reduced by **1–6 bits** and FFT cost by **2–7 bits** in most parameter
  settings.
- The authors situate the value correctly: these reductions "are practically meaningful
  in scenarios where **memory usage or multi-target attacks** are of concern" — i.e. the
  win is on a resource axis other than raw time.

## Relevance to this program
Two reasons, one narrow and one that generalizes.

**Narrow:** a 2026 increment to [[KN-TECH-039]] (the dual attack and the dual-sieve
dispute) and a data point for [[KN-OPEN-016]], which asks what the dual attack actually
costs once its heuristics are repaired. Companion paper to [[KN-LIT-7664]] by the same
authors — that one fixes the *analysis*, this one improves the *attack*.

**General, and the reason it is worth an entry at all:** this is an unusually
well-behaved example of **reporting a gain on the axis where it actually falls**. The
headline is not "we broke Kyber" or even "we improved the attack"; it is that total
complexity improves *modestly* while the **FFT and decoding cost components** improve
by 2–7 and 1–6 bits, and that this matters specifically under **memory pressure or in
multi-target settings**.

`KN-TECH-035` requires exactly that discipline of this program — charge memory, wiring
and communication, and say which axis a claimed improvement moves. A paper that
volunteers "the time improvement is modest but the memory-side components move" is a
model of the form, and is cited here for that as much as for the numbers.

**Does not bear on the ECDLP**, and **is not a break of Kyber** — a few bits off two
cost components of one attack variant is not a security-level change, and this entry
asserts none.

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/1400,
retrieved 2026-08-01 (hence `confidence: reported`). Citation checked against the
ePrint record: title, two authors, report number, year 2026.

NOT verified here: the integration of modulus switching with lossy source coding; the
`q^{n_fft} → p^{k_fft}` enumeration reduction; the 1–6 and 2–7 bit figures or the cost
model they are computed in; the claimed total-complexity improvement over lossy-source-
coding-only; and the attributions to MATZOV and Carrier et al. **No ML-KEM parameter
set is reassessed by this program.**
