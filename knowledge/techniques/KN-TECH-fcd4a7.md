---
id: KN-TECH-fcd4a7
type: technique
title: >-
  Hidden-SNFS trapdoor through a low embedding degree -- a visibly pairing-friendly curve over a prime of secretly special form, so that the MOV-transferred DLP in F_{p^k} falls to the special number field sieve
tags: [trapdoor, hidden-snfs, snfs, nfs, mov, embedding-degree, pairing-friendly, gordon, finite-field-dlp, ecdlp]
confidence: reported
complexity: >-
  holder runs SNFS in F_{p^k} at L_{p^k}(1/3, (32/9)^{1/3} ~ 1.526); outsider runs GNFS at L_{p^k}(1/3, (64/9)^{1/3} ~ 1.923); the gap is what makes a size that outsiders consider safe feasible for the holder (a 1024-bit hidden-SNFS DLP was computed in about two months of core time by Fried-Gaudry-Heninger-Thome, KN-LIT-7635)
applicability: >-
  curves whose embedding degree k is small enough that the field F_{p^k} is in SNFS range; requires the generator to choose p with a hidden low-degree polynomial representation with small coefficients; detection of the hidden form is believed hard (Gordon)
source_refs: [KN-LIT-7635, KN-LIT-2089, KN-LIT-086, KN-TECH-6ead00]
added: 2026-09-30
superseded_by: null
---

## Construction

1. Choose a polynomial `f` of small degree `d` (6 to 8 in practice) with small
   coefficients and an integer `m` such that `p = f(m)` is prime. Such `p`
   admits an SNFS polynomial pair, which is what makes the sieve cheap.
   Gordon (CRYPTO 1992, "Designing and detecting trapdoors for discrete log
   cryptosystems"; not yet a KN-LIT entry) showed how to make this look like a
   random prime.
2. Build a curve `E/F_p` with a small embedding degree `k` (supersingular for
   `k <= 6`, or a pairing-friendly family for larger `k`).
3. Publish `(p, E, P)`. The small `k` is visible; users accept it because they
   believe `F_{p^k}` is out of NFS range at the chosen size.
4. To solve a DLP on `E`, apply the MOV / Frey-Rueck transfer to `F_{p^k}^*`
   and run SNFS with the secret polynomial. Individual logs after the one-time
   linear-algebra phase are cheap.

## Evidence that it is practical

KN-LIT-7635 (Fried, Gaudry, Heninger, Thome 2017) computed a discrete
logarithm modulo a 1024-bit prime of hidden SNFS form, at a size then widely
deployed for finite-field Diffie-Hellman, and reported that distinguishing
such a prime from a random one is not feasible with known methods. The ECTD
briefing calls this the "parameter-level trapdoor gold standard": ordinary-
looking public parameters, a hidden algebraic representation, private
precomputation, cheap individual logs, and no obvious detector.

## Detectability

The embedding degree is public and computable, so the *transfer* is not
hidden. What is hidden is the special form of `p`. Gordon's analysis and the
2017 computation both treat recovery of `(f, m)` from `p` as infeasible in
general (it is a small-coefficient polynomial reconstruction problem with no
known efficient algorithm at these sizes).

## Applicability limits

- Only curves with small `k` are exposed; ordinary random curves have
  `k ~ n` (KN-LIT-086) and the transfer is useless.
- The hidden-SNFS advantage is a constant in the `L(1/3)` exponent, so the
  window is a range of field sizes, not an asymptotic break.
- Pairing-based deployments choose `p` by construction (Barreto-Naehrig,
  BLS12 families are themselves polynomial-form primes), so for those the
  "hidden" form is public and the relevant question is the plain SNFS/TNFS
  security level, not a trapdoor.

## Relevance

The clearest existing template for a trapdoor on `F_p` parameters: a public,
detectable *transfer* combined with a hidden *solver advantage* in the target
group. GOAL-ECTD-001's search for a prime-field isogeny trapdoor is looking
for the same separation with an isogeny in the place of the MOV map.
