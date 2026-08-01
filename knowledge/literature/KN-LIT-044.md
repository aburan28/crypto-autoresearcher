---
id: KN-LIT-044
type: literature
title: The Insecurity of (EC)DSA with Partially Known Nonces (Nguyen-Shparlinski)
authors: [Nguyen Phong Q., Shparlinski Igor E.]
year: 2003
venue: J. Cryptology 15(3):151-176 (DSA, 2002); Des. Codes Cryptogr. 30(2):201-217 (ECDSA, 2003)
identifiers:
  eprint: null
  doi: 10.1023/A:1025436905711
  url: https://link.springer.com/article/10.1023/A:1025436905711
tags: [ecdsa, dsa, nonce-leakage, hidden-number-problem, hnp, lattice, key-recovery, ecdlp-adjacent, cryptanalysis]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Turns the Hidden Number Problem (KN-LIT-043) into concrete secret-key recovery
for (EC)DSA when a few bits of each per-signature nonce k leak. The partial-nonce
information is reduced to the HNP over the group order and solved with lattice
basis reduction (LLL/BKZ). Two companion papers: DSA (J. Cryptology 15(3):151-176,
2002, doi:10.1007/s00145-002-0021-3) and ECDSA (Des. Codes Cryptogr.
30(2):201-217, 2003, doi:10.1023/A:1025436905711).

## Key claims (as reported)
- ~sqrt(log q) leaked MSBs/LSBs over ~log-many signatures suffice to recover the
  key in polynomial time (down to log log q with subexponential time, or ~2 bits
  with an ideal lattice-reduction oracle).
- Provable under a reasonable hash assumption (improving on the earlier heuristic
  Howgrave-Graham-Smart treatment, KN-LIT-045); ECDSA results validated
  experimentally on real curve parameters.

## Relevance to this program
The single most direct lattice/ECDLP intersection: a lattice attack that breaks
EC discrete-log-based signatures (ECDSA) via nonce leakage. CRITICAL scoping: it
recovers the key from SIDE-CHANNEL / partial-nonce information, NOT by solving the
plain ECDLP -- the attack lives entirely in the leakage model (KN-OPEN-011). This
is the canonical reason side-channel nonce protection matters for EC signatures,
and why the program's ECDLP hardness claims are orthogonal to (not contradicted
by) these breaks.

## Not verified here
Full papers not read; the leakage thresholds and provable-vs-heuristic status
relayed from the abstracts (hence confidence: reported). Fields for both DSA and
ECDSA versions confirmed against Springer/DBLP records via search, not by
fetching the primary pages.
