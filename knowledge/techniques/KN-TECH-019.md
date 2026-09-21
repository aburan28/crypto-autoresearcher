---
id: KN-TECH-019
type: technique
title: Hidden Number Problem and lattice attacks on (EC)DSA nonces
tags: [hidden-number-problem, hnp, ecdsa, dsa, nonce-leakage, lattice, cvp, key-recovery, ecdlp-adjacent]
confidence: established
complexity: polynomial time given ~sqrt(log q) leaked nonce bits over O(log q) signatures; reduces to CVP/SVP solved by LLL/BKZ
applicability: key recovery for discrete-log signatures (DSA/ECDSA/Schnorr) under partial per-signature nonce leakage; NOT plain ECDLP
source_refs: [KN-LIT-043, KN-LIT-044, KN-LIT-045]
added: 2026-07-23
superseded_by: null
---

## Method
Each (EC)DSA signature gives a linear relation k = s^{-1}(H(m) + r*d) mod q
between the nonce k and the secret d. If a few bits of each k leak, the unknown
part of k is small, and many signatures yield an instance of the Hidden Number
Problem (KN-LIT-043): recover d given approximate multiples of it mod q. Building
a lattice from the signature relations, the secret is a short/close vector found
by lattice reduction (LLL/BKZ, KN-TECH-020) -- a CVP/SVP solve.

## Complexity / applicability
Roughly sqrt(log q) leaked MSBs/LSBs over O(log q) signatures suffice for
polynomial-time recovery (Nguyen-Shparlinski, KN-LIT-044); fewer bits cost more
(subexponential, or ~2 bits with an ideal reduction oracle). Also drives attacks
on biased/repeated nonces (a repeated nonce breaks ECDSA outright with 2
signatures, a degenerate case).

## Relevance to this program
The canonical practical lattice/ECDLP intersection and the main reason to record
lattice methods in an ECDLP corpus. CRITICAL boundary: this recovers the key from
SIDE-CHANNEL / partial-nonce information, NOT by solving the plain ECDLP. The
program's ECDLP-hardness claims are orthogonal to these breaks -- a fielded ECDSA
key can fall to nonce leakage while the underlying ECDLP stays hard (KN-OPEN-011).

## Applicability limits
Requires an actual leakage/bias source (implementation flaw, side channel); on
uniformly random, fully secret nonces the HNP instance is underdetermined and the
attack does not apply. It is a statement about signature-scheme + implementation
security, not about the hardness of the group's discrete log.
