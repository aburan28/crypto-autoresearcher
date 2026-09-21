---
id: KN-LIT-112
type: literature
title: 'A subfield lattice attack on overstretched NTRU assumptions: Cryptanalysis of some FHE and Graded Encoding Schemes'
authors: [Albrecht Martin, Bai Shi, Ducas Leo]
year: 2016
venue: CRYPTO 2016 (ePrint 2016/127)
identifiers:
  eprint: iacr:2016/127
  doi: null
  url: https://eprint.iacr.org/2016/127
tags: [ntru, overstretched-ntru, subfield-attack, norm, fhe, multilinear-maps, ideal-lattice, structure, lattice]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
Resurrects and generalises the subfield attack on NTRU: norm the public key
`h` down to a subfield, solve an easier lattice problem there, and lift the
solution back to a short vector in the full NTRU lattice. The idea was sketched
by Gentry and Szydlo in 2002 (attributed also to Jonsson, Nguyen and Stern) but
abandoned because it fails for small moduli and hence for NTRUEncrypt. The
paper shows it succeeds decisively for large moduli -- the *overstretched*
regime -- and breaks schemes that live there.

## Key claims (as reported)
- For sufficiently large modulus q the subfield attack applies and
  asymptotically outperforms other known attacks.
- Asymptotic security claims of the bootstrappable FHE schemes LTV and YASHE,
  which rely on a mildly overstretched NTRU assumption, are invalidated: the
  attack runs in `2^O(lambda / log^(1/3) lambda)` against a claimed
  `2^Theta(lambda)`.
- Against GGH-like multilinear maps the attack can run in polynomial time
  without encodings of zero or the zero-testing parameter, with an additional
  quantum step needed to recover secret parameters exactly.
- Reported experiment: running LLL in dimension 512 produced vectors that would
  otherwise have required BKZ with block size 130 in dimension 8192.
- The paper discusses the condition on q that guarantees full immunity.

## Relevance to this program
The canonical demonstration that *algebraic structure introduced for efficiency
can be load-bearing for security*, and that a parameter regime chosen for a
downstream application (large q for FHE noise growth) can silently leave the
regime where the hardness assumption was studied. The program's ECDLP work has
the same shape whenever it considers curve families with extra structure. Note
the sequel: Kirchner-Fouque (KN-LIT-113) showed the algebraic detour was
unnecessary and plain lattice reduction already does as well, and Ducas-van
Woerden (KN-LIT-114) explained why -- a three-paper arc worth reading as a unit
on how a mechanism's *explanation* can be wrong while its *effect* is real.

## Not verified here
The ePrint abstract was fetched and read. The asymptotic complexity claims, the
LLL experiment, and the immunity condition on q were not reproduced or
re-derived, and the exact definition of "overstretched" used by this paper was
not extracted from the full text.
