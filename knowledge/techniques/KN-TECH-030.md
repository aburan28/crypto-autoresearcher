---
id: KN-TECH-030
type: technique
title: Pohlig-Hellman reduction and prime-order-subgroup hygiene
tags: [pohlig-hellman, group-order, smooth-order, subgroup, crt, generic, baseline, instance-validity, ecdlp, hygiene]
confidence: established
complexity: O(sum_i e_i * (log n + sqrt(p_i))) group operations for n = prod p_i^{e_i}; dominated by the largest prime factor
applicability: any finite cyclic group whose order is known and factorable; always applicable, so it defines the effective problem size
source_refs: [KN-LIT-082, KN-TECH-001, KN-TECH-005]
added: 2026-07-24
superseded_by: null
---

## Method
Given #E(F_p) = n = prod p_i^{e_i}, project the instance into each subgroup of
order p_i^{e_i}, solve there (by e_i successive solves in a group of order
p_i, each a square-root problem), and recombine by the Chinese Remainder
Theorem. The cost is dominated by sqrt(p_max) where p_max is the largest prime
factor of n. Consequently the *only* quantity that determines ECDLP difficulty
in the generic model is the size of the largest prime-order subgroup, not the
size of the field or of the full group.

## Why it is a precondition, not an attack
Pohlig-Hellman is not a route to beating rho; it is the reduction that fixes
what "the instance" is. Three obligations follow for this program:

1. **Baseline arithmetic.** The rho cost 0.886*sqrt(n) (KN-TECH-006) must use
   n = the prime subgroup order, not #E(F_p). On a curve with cofactor h, using
   #E overstates the baseline by sqrt(h) -- a factor of ~2.8 at the common
   cofactor 8, which is large enough to manufacture an apparent advantage.
2. **Instance validity.** Any curve the harness generates for measurement must
   have its group order factored and its largest prime factor recorded. A
   speedup measured on a smooth-order curve is Pohlig-Hellman, not a mechanism.
   This is cheap at toy scale and must not be skipped there, because accidental
   smoothness is far more likely at 16-32 bits than at 256.
3. **Claim scoping.** A result stated as "solved an n-bit ECDLP" is meaningless
   without the prime subgroup order; evidence records should carry the factored
   order, following the practice in the published records (KN-LIT-095 quotes
   its prime n explicitly).

## Applicability limits
The reduction needs the group order, which for a curve over F_p means running
a point-counting algorithm (SEA) or using a standardized curve with published
order. It gives no advantage when n is prime -- which is the designed case for
every cryptographic curve, and the case this program targets. It says nothing
about non-generic structure: an anomalous or small-embedding-degree curve of
prime order is still broken (KN-TECH-032, KN-TECH-033) despite Pohlig-Hellman
offering nothing there.

## Verified vs reported
The reduction and its cost are textbook and proven in KN-LIT-082 (confidence:
established). The specific numeric consequences stated above -- the sqrt(h)
mis-charge, the toy-scale smoothness concern -- are this program's own
reasoning applied to its baseline convention, not claims from the source, and
have not been measured against the program's own runs.
