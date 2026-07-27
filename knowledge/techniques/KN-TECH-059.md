---
id: KN-TECH-059
type: technique
title: Structural key-recovery attacks on algebraic code trapdoors
tags: [code-based, structural-attack, key-recovery, distinguisher, filtration, code-equivalence, support-splitting, groebner, reed-solomon, goppa, cryptanalysis]
confidence: reported
complexity: polynomial time on broken families (GRS, Reed-Muller, several compact-key variants); no attack at deployed binary-Goppa parameters
applicability: screening any code-based proposal that buys efficiency with algebraic structure; assessing key-security (as opposed to message-security) claims
source_refs: [KN-LIT-7569, KN-LIT-7570, KN-LIT-2395, KN-LIT-2383, KN-LIT-2127, KN-LIT-5792, KN-LIT-7518, KN-LIT-7519, KN-LIT-3281, KN-LIT-2452, KN-LIT-1894]
added: 2026-07-27
superseded_by: null
---

## The second assumption
A code-based scheme has two independent security legs (KN-LIT-7564): decoding
hardness, and indistinguishability of the published code from a random one.
Structural attacks go after the second. They recover the secret code description
and then decode legitimately -- generic decoding hardness (KN-TECH-057) is never
engaged, so its exponent is irrelevant to whether the scheme stands.

Keeping these separate is the discipline this entry exists to enforce. "SD is
NP-complete" is not an answer to a structural attack, and a new ISD record is not
evidence about key security.

## The techniques
**Direct algebraic recovery.** Solve for the secret support and multipliers from
the public matrix. This is what breaks GRS codes in polynomial time
(KN-LIT-7569) and, with more work, several compact-key variants via Groebner
methods on the resulting system (KN-LIT-2395, KN-LIT-2383). Recent work recasts
the problem in terms of quadratic forms (KN-LIT-2127). The Groebner machinery
here is the same the program already tracks for ECDLP (KN-TECH-004, KN-TECH-011)
and MQ (KN-TECH-053) -- the solving-degree question transfers even though the
target does not.

**Distinguishers and filtration.** Find an invariant separating the public code
from a random one -- typically anomalous dimension of a square or shortened code
-- then bootstrap it into recovery by peeling off a filtration of subcodes. This
is how Wild McEliece over quadratic extensions falls (KN-LIT-5792, against
KN-LIT-7518 and KN-LIT-7519), and it is the technique behind the high-rate Goppa
distinguisher (KN-LIT-2395) that keeps KN-OPEN-021 open.

**Code equivalence.** If the secret is only a permutation of a known code, the
support splitting algorithm recovers it in time polynomial in length and
exponential in hull dimension (KN-LIT-7570). Note the dual use: the same
hull-dimension dependence makes code equivalence a usable *hardness* assumption
for signatures, not only an attack.

## Track record
Broken families include generalized Reed-Solomon (KN-LIT-7569), Reed-Muller
(KN-LIT-3281), several quasi-cyclic/quasi-dyadic compact-key variants
(KN-LIT-2395), Goppa polynomials of special form (KN-LIT-2383), and Wild
McEliece over quadratic extensions (KN-LIT-5792). The rank-metric branch has its
own algebraic-attack line (KN-LIT-2452, KN-LIT-1894). Unbroken at deployed
parameters: plain binary Goppa (KN-LIT-7573), and the quasi-cyclic MDPC/HQC
family -- whose exposure is decoding failures instead (KN-TECH-060).

## Use as a screen
The transferable rule, and the reason this entry belongs in a corpus whose main
subject is elsewhere: **when a proposal makes a hard instance cheaper by giving
it algebraic structure, the structure is a hypothesis to attack, not a free
optimization.** Ask what invariant the added structure creates, and whether that
invariant is computable from public data. The Idea Generator should apply this to
any proposal that introduces structured instances -- the ECDLP side has already
retired several representation-exploiting families on essentially this ground.

## Applicability limits
All attacks here are `reported`; none was reproduced in this program. "Unbroken"
means no published break known to this corpus as of the `added` date, at the
parameters cited -- it is not a security proof and carries no forward guarantee.
