---
id: KN-LIT-b58682
type: literature
title: "A Riddle Wrapped in an Enigma"
authors:
  - "Neal Koblitz"
  - "Alfred J. Menezes"
year: 2015
venue: "IACR ePrint 2015/1018 (dated 20 October 2015, updated 19 May 2018); also reported as published in IEEE Security & Privacy 14(6), 2016, not verified here"
identifiers:
  eprint: "2015/1018"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2015/1018"
tags: [nist-curves, seed-manipulation, verifiably-random, weak-curve-class, nsa, suite-b, dual-ec, post-quantum, standardization, ecdlp]
confidence: reported
citation_verified: web
added: "2026-10-01"
superseded_by: null
---

## Contribution

Abstract (verbatim): "In August 2015 the U.S. National Security Agency
(NSA) released a major policy statement on the need for post-quantum
cryptography (PQC). This announcement will be a great stimulus to the
development, standardization, and commercialization of new quantum-safe
algorithms. However, certain peculiarities in the wording and timing of the
statement have puzzled many people and given rise to much speculation
concerning the NSA, elliptic curve cryptography (ECC), and quantum-safe
cryptography. Our purpose is to attempt to evaluate some of the theories
that have been proposed."

Sections (read from the ePrint PDF): 1 Introduction; 2 History: The NSA and
ECC; 3 Can the NSA Break ECC?; 4 Does the NSA Know Something the Outside
World Doesn't about Quantum Computers?; 5 Theories about the NSA's Motives.

## Key claims (read directly; Section 3 is the one this program uses)

- **The NIST curve seeds.** The ANSI X9F1 committee asked for randomly
  generated curves to avoid as-yet-unknown special-class weaknesses; an NSA
  representative supplied them around 1997 with coefficients derived by
  passing a seed through SHA-1, so that "it would be infeasible for anyone
  to first select a curve with very special properties, and then find a seed
  which yields that curve." The paper states that no new class of weak
  prime-field curves has been found since 1997 and no weakness in the NIST
  curves has been found.
- **The density argument against a planted weak class.** Over a fixed
  256-bit prime there are about `2^257` isomorphism classes, of which at
  least a fraction `2^-8` have prime order. If the NSA had known a weak
  sub-class of relative density `2^-40`, it could have found one by trying
  about `2^48` seeds, but that class would contain about `2^209` curves,
  and the authors judge it "highly unlikely that such a large family of weak
  elliptic curves would have escaped detection by the cryptographic research
  community from 1997 to the present." They call the planted-seed scenario
  "highly implausible."
- **Remark 1 (Bernstein-Lange, 2017 personal communication, added in the
  2018 revision).** A different search needs only about `2^61` weak
  prime-order curves over the P-256 field: generate curves from hash
  outputs, look for a collision of prime group orders between hash-derived
  curves and known-weak curves (about `2^70` curves to count, with
  mod-`N` group-order sieving as a speed-up), then random-walk in the shared
  isogeny class until the curves collide. The authors record this as a
  criticism of their density argument.
- Dual EC DRBG is discussed as the one documented NSA back door, with the
  observation that its design let the back door be used by the NSA alone;
  the paper notes that no way to insert a back door into DSA or ECDSA has
  been found in two decades.
- Sections 4 and 5 argue, from the Snowden documents and the size of the
  NSA's quantum program, that the NSA does not have a near-term quantum
  computer and weigh several explanations for the 2015 announcement; they
  are outside this program's scope and are not summarized further.

## Relevance to this program

Primary source for the detectability discussion in `KN-TECH-031027`
(seed-manipulation meta-trapdoor): it supplies the quantitative version of
"a secret weak class of usable density would have to exist," and Remark 1
is the sharper collision-plus-isogeny-walk variant that lowers the required
class size from `2^209` to about `2^61`. Both numbers are exactly what
`KN-OPEN-cc1988` (non-isogeny-invariant prime-field weakness) would have to
beat for a planted prime-field trapdoor to be deployable, so this paper is
the cost side of that open problem's condition (3). It is also the
program's clearest statement that, as of 2018, no prime-field weak class
beyond anomalous and low-embedding-degree curves is publicly known.
