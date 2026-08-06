---
id: KN-OPEN-028
type: open_problem
title: What is the corrected cost of the nrd-PIP route against HAWK, now that Heuristic 4 has failed and 1-3 are verified?
tags: [hawk, module-lip, lattice-isomorphism-problem, nrd-pip, principal-ideal-problem, quaternion, lenstra-silverberg, super-polynomial, fractional-ideals, heuristic, retracted-claim, pqc, open, lattice]
confidence: read
status: closed_all_questions_answered
all_questions_closed: 2026-08-05
q1_closure: >-
  Q1 CLOSED (derivation + paper-body confirmation, 2026-08-05). Case C:
  algorithm samples bounded-norm β (‖β‖ < O(n^{13/2})) → bounded denominator
  O_F-ideals → density of "easy" principal ideals → 0 as bound grows →
  super-polynomial runtime. No sub-exponential advantage over brute force
  established. See EV-HAWK-c99848 / DEC-20260805-ed4cd3.
supersedes: KN-OPEN-027
q2_closure: >-
  Q2 CLOSED: The re-randomization idea (conjugate G by U to get distinct nrd-PIP
  instances) SURVIVES. The mechanism is valid; what failed is Heuristic 4's
  density estimate. The algorithm just needs super-polynomial guesses. (From
  paper Section 4 and 30/06 update, EV-HAWK-21edba / DEC-20260805-a62164)
q3_closure: >-
  Q3 CLOSED: KN-OPEN-024 unaffected. Paper Section 12 confirms the attack does
  not break the quaternion nrd-PIP. The reduction from module-LIP to nrd-PIP
  ([8], Eurocrypt 2025) remains valid. (From paper Section 12, EV-HAWK-21edba)
source_refs: [KN-LIT-7674, KN-LIT-7670, KN-LIT-7592, KN-LIT-7673, KN-LIT-7648, KN-LIT-7671, KN-OPEN-024, KN-OPEN-027, KN-TECH-081, EV-HAWK-001, EV-HAWK-c99848]
added: 2026-08-02
updated: 2026-08-05
superseded_by: null
---

> **Supersedes [[KN-OPEN-027]]**, which was written against an incomplete reading of
> `iacr:2026/1318` and asked "do the heuristics hold?" as an open question. **That
> question is now substantially answered by the paper's own 30/06 update**, which
> `KN-OPEN-027` did not have because this program had recorded the abstract as
> truncated when it never was. See [[KN-LIT-7674]] and
> `ledger/corrections/CORR-20260802-008.yaml`.

## What is now settled

From the complete 30/06 update, transcribed verbatim in [[KN-LIT-7674]]:

- **Heuristics 1–3: independently experimentally verified.** The authors say so.
- **Heuristic 4: failed.** It "is insufficient to conclude that the main algorithm
  runs in polynomial time, and in fact the main algorithm appears to run in
  **super-polynomial time**."
- **The cause is named and arithmetic**: the count of ideals of norm `q'` in `O_F`
  omitted **fractional** ideals, "of which there are many."

`KN-OPEN-027`'s question 1 ("do the heuristics hold?") is therefore closed in a
specific and unusual shape: **three of four hold and are checked; the fourth is
wrong, and its wrongness is understood.** That is a much more informative position
than "unverified."

## What is open now

**(Q1) What is the corrected cost?** "Appears to run in super-polynomial time" is a
direction, not a bound. The corrected ideal count is a concrete arithmetic quantity —
fractional ideals of norm `q'` in `O_F` — so a corrected complexity is derivable in
principle. Nobody in this corpus has derived it. **Is the route super-polynomial but
sub-exponential, or does it degrade to something with no advantage at all?** That
difference decides whether the nrd-PIP route remains interesting.

**(Q2) Does the re-randomisation idea survive its cost correction?** The mechanism —
conjugate the public Gram matrix by short unimodular `U` until the attached nrd-PIP
instance is "unusually easy," then solve *that* — is independent of the miscount. It
is a search over instance *representations* rather than over solutions, and
`docs/inventor-protocol.md` asks generators to look for exactly that move. **The
instance-density question is what Heuristic 4 was about**, so Q2 and Q1 are the same
quantity seen from two sides.

**(Q3) What does this leave for [[KN-OPEN-024]]?** That entry asked whether rank-1
quaternion-order PIP inherits the tractability shown for `M_g(O)`, `g ≥ 2`, and named
the module-LIP → nrd-PIP reduction as the cheapest thing to check. The reduction is
real and was used offensively; what failed is the *density estimate downstream of it*,
not the reduction. **`KN-OPEN-024` is therefore unaffected in its core and should not
be read as weakened by this correction.**

## Why it matters

HAWK's Round-3 tweak deadline is **2026-08-14**. The live attack surface is now:

| Route | Status |
|---|---|
| Straznickas–Weis ([[KN-LIT-7592]]) | **Unconditional**, exponential `2^{(n/2+1)+o(n)}` — halves the oracle dimension |
| nrd-PIP / Guessing Game ([[KN-LIT-7674]]) | Heuristics 1–3 verified, **Heuristic 4 failed**, cost now super-polynomial and underived |
| Definite/indefinite LIP ([[KN-LIT-7648]]) | Breaks DEFI; **reports HAWK unaffected** |
| Complexity ceiling ([[KN-LIT-7671]]) | SLIP ∈ AM ∩ coAM — provably not as hard as SVP absent a PH collapse |

**None of these is a break of HAWK, and this entry asserts none.**

## What would resolve it

1. **Read the body of `iacr:2026/1318`.** Still not obtained — the ePrint PDF is
   Cloudflare-gated, and as of 2026-08-02 the paper is confirmed **not on arXiv**
   (four queries including an author search returned nothing). Q1 is not answerable
   from the abstract.
2. Derive the corrected count independently: fractional ideals of norm `q'` in `O_F`
   is a standard algebraic-number-theory quantity, and the corrected exponent may
   follow without the paper.
3. Only then revisit Q2 and Q3.

## Not verified here

Everything is relayed from the `iacr:2026/1318` abstract and its 30/06 update,
retrieved 2026-08-02; **the body has not been read**. This program has verified no
heuristic, derived no corrected cost, and run no HAWK experiment. **No assessment of
HAWK's security is made in either direction.** The "independently experimentally
verified" claim for Heuristics 1–3 is the authors' own report and was not checked
against whoever performed that verification. **Does not bear on the ECDLP.**
