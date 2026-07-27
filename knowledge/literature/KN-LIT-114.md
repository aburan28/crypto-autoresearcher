---
id: KN-LIT-114
type: literature
title: 'NTRU Fatigue: How Stretched is Overstretched?'
authors: [Ducas Leo, van Woerden Wessel]
year: 2021
venue: ASIACRYPT 2021 (ePrint 2021/999)
identifiers:
  eprint: iacr:2021/999
  doi: null
  url: https://eprint.iacr.org/2021/999
tags: [ntru, overstretched-ntru, fatigue-point, dense-sublattice, dsd, bkz, concrete-security, instance-validity, structure, lattice]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
Locates the NTRU fatigue point -- the modulus q at which NTRU lattices stop
behaving like LWE lattices of the same parameters and become substantially
easier -- both asymptotically and concretely, and explains the mechanism that
the earlier impossibility argument (KN-LIT-113) could not.

## Key claims (as reported)
- Asymptotic fatigue point for ternary NTRU narrowed from Kirchner-Fouque's
  `q <= n^(2.783+o(1))` to `q = n^(2.484+o(1))`.
- Concrete fatigue point settled at `q ~ 0.004 * n^2.484`, enabling precise
  hardness predictions inside the overstretched regime rather than only a
  boundary.
- The analysis explains the mechanism behind the phenomenon -- how lattice
  reduction actually recovers secret-key information via the dense sublattice --
  which the authors note the prior impossibility argument did not.
- Predictions are backed by extensive experiments.

## Relevance to this program
This is the entry that turns "overstretched NTRU" from folklore into a checkable
precondition, and it is why KN-TECH-045 treats the fatigue point as an
instance-validity gate rather than an attack. Its structural role in the lattice
corpus mirrors Pohlig-Hellman's role in the ECDLP corpus (KN-TECH-030): a
condition on the instance that, if unchecked, manufactures an apparent
algorithmic advantage that is really an artifact of parameter choice. Any
internal experiment that measures reduction behaviour on an NTRU-shaped lattice
must state its q relative to `0.004 * n^2.484` for the measurement to mean
anything.

The arc KN-LIT-112 -> KN-LIT-113 -> KN-LIT-114 is also the corpus's best case
study in mechanism versus effect: a real effect, first explained by the wrong
mechanism (subfields), then bounded by an argument that gave no mechanism, then
finally explained and tightened by a factor visible in the exponent.

## Not verified here
The ePrint abstract was fetched and read. The asymptotic derivation, the
concrete constant 0.004, and the supporting experiments were not reproduced.
The result is stated for ternary NTRU with the standard secret distribution;
its extension to other secret distributions was not checked.
