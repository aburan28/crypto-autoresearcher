---
id: KN-OPEN-027
type: open_problem
title: Is HAWK's module-LIP assumption reachable through nrd-PIP, and do the four heuristics hold?
tags: [hawk, module-lip, lattice-isomorphism-problem, nrd-pip, principal-ideal-problem, quaternion, lenstra-silverberg, heuristic, unverified-heuristic, pqc, concrete-security, open, lattice]
confidence: reported
status: open
source_refs: [KN-LIT-7670, KN-LIT-7647, KN-LIT-7648, KN-LIT-7671, KN-LIT-7641, KN-OPEN-024, KN-TECH-081]
added: 2026-08-01
superseded_by: KN-OPEN-028
---

> **Superseded 2026-08-02 by [[KN-OPEN-028]].** This entry asks "do the heuristics
> hold?" as an open question. It is substantially answered by the paper's own 30/06
> update, which this entry did not have because the abstract had been recorded as
> truncated when it never was: **Heuristics 1-3 are independently experimentally
> verified and Heuristic 4 failed**, making the algorithm super-polynomial. Body left
> unedited per the immutability rule; cite KN-OPEN-028. See
> `ledger/corrections/CORR-20260802-008.yaml`.

## Statement

[[KN-LIT-7670]] (Nelson, Limbrey, Ling, Mendelsohn) describes a **classical algorithm
claimed to recover the HAWK secret key in probabilistic polynomial time under four
number-theoretic heuristics**, routed through the Eurocrypt 2025 reduction from HAWK's
rank-2 **module-LIP** instances to **nrd-PIP**. The method re-randomises the nrd-PIP
instance — conjugating the public Gram matrix by short unimodular `U` — until an
instance appears that the **Lenstra–Silverberg** subfield approach solves.

The authors state they **do not claim HAWK is broken**, having not verified the
heuristics experimentally, and a **30/06 update acknowledges that Heuristic 4 is
insufficient** for the stated running-time conclusion (the retrieved abstract is
truncated mid-sentence there).

So the question is live and precisely three-part:

**(Q1) Do the heuristics hold?** Specifically the one the authors conceded, and whether
a repair exists. This is the authors' own stated next step.

**(Q2) Is the "unusually easy instance" density real?** The algorithm needs a
non-negligible proportion of re-randomised `G'` to yield nrd-PIP instances the subfield
approach solves. That density is a number, and it is the load-bearing quantity.

**(Q3) Does this settle [[KN-OPEN-024]]?** That entry asked whether rank-1
quaternion-order PIP inherits the tractability [[KN-LIT-7641]] showed for `M_g(O)`,
`g ≥ 2`, and named verifying the module-LIP → nrd-PIP reduction as the cheapest first
move. **This paper is that reduction being used offensively** — so `KN-OPEN-024`'s
question 2 (the *stage* question: find a generator versus find a short one) now has a
concrete algorithm attached rather than only an assumption.

## Why it matters

- **HAWK is a NIST-round lattice signature.** A heuristic polynomial-time key-recovery
  route, even an unverified one with a conceded gap, is a material fact about its
  assumption's standing.
- **The same small author group is on both sides.** Nelson and Mendelsohn wrote
  [[KN-LIT-7647]] (SoliloQuat), which **assumes** SG-PIP in quaternion orders is hard;
  Cong Ling wrote [[KN-LIT-7648]], which broke DEFI's LIP instantiation and reported
  HAWK **unaffected** by that route. A single group proposing on an assumption and
  attacking it is a signal about how unsettled the assumption is — not about anyone's
  good faith.
- **Two independent attack routes and one complexity ceiling now converge on LIP.**
  [[KN-LIT-7648]] (genus/spinor-genus collapse), this one (nrd-PIP + subfield), and
  [[KN-LIT-7671]] (SLIP lies in AM ∩ coAM, so it is provably *not* as hard as SVP unless
  the polynomial hierarchy collapses). Any program proposal reaching for a LIP-style
  hardness baseline must read all three first.

## Current state (as reported)

- The algorithm exists on paper; **no implementation is reported**, and the authors say
  verification is future work.
- **Heuristic 4 is publicly conceded insufficient** for the running-time claim. The
  precise scope of that concession is **not recorded in this corpus**, because the
  retrieved abstract is truncated inside the sentence stating it.
- HAWK is **not** claimed broken by its own authors, and is **not** claimed broken here.
- [[KN-LIT-7648]] separately reports HAWK unaffected by the definite/indefinite LIP
  techniques that broke DEFIv2 — a different route, also unverified by this program.

## What would resolve it

1. **Read the current version of ePrint 2026/1318 directly.** This is not optional and
   not substitutable by any record here: the claim is heuristic-dependent with a live
   public correction, and an abstract-level record is structurally insufficient for it.
   Anything downstream of this entry must start there.
2. Extract and state the four heuristics individually, with the 30/06 concession's exact
   scope, and record which are standard and which are novel to this paper.
3. Watch for third-party analysis or an implementation. The Apon and Saarinen
   discussions the update references suggest the community is already on it.
4. Only then revisit [[KN-OPEN-024]] with whatever the outcome implies for rank-1
   quaternion-order PIP.

## Not verified here

**No assessment of HAWK's security is made, in either direction.** This program has not
read the paper, not checked any heuristic, not evaluated the instance density, and not
verified the Eurocrypt 2025 reduction the algorithm depends on — which is itself relayed
second-hand through [[KN-LIT-7647]] and is not an entry in this corpus. The 30/06
acknowledgement is recorded as truncated rather than completed by inference. **Does not
bear on the ECDLP.**
