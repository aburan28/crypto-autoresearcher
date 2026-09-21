---
id: KN-FIND-e22186
type: internal_finding
title: "Simon 2026's DCP erasure technique has no currently-citable general-N extension applicable to CSIDH-512's actual class-group order -- premise (i) of the CSIDH DCP-route chain fails on current literature"
tags:
- csidh
- dihedral-hsp
- dcp-route
- kuperberg
- literature-audit
- crypto-scale
confidence: reported
internal_refs:
- H-CSIDH-3eaede
- EV-QALG-1b3395
- DEC-20260906-29caf8
proof_status: derivation
proof_refs:
- experiments/EXP-CSIDH-c65945/runs/RUN-CSIDH-c65945-001/applicability_audit.md
- coordination/goals/GOAL-QALG-001/reviews/RUN-CSIDH-c65945-001-redteam/report.yaml
added: '2026-09-06'
superseded_by: null
---

## Artifacts

- `experiments/EXP-CSIDH-c65945/` -- frozen specification, `amendments/v1.yaml`
  (resulting_version 2), `runs/RUN-CSIDH-c65945-001/`.
- `ledger/decisions/DEC-20260906-b60887.yaml` (dispatch authorization),
  `DEC-20260906-29caf8.yaml` (evidence-review decision closing this record).
- Independent review: `coordination/goals/GOAL-QALG-001/reviews/RUN-CSIDH-c65945-001-validation/report.yaml`
  (REVISE, on citation-precision/timing points -- see `CORR-20260906-4c1b57`)
  and `.../RUN-CSIDH-c65945-001-redteam/report.yaml` (SUSTAINED).

## The finding

Simon 2026 (KN-LIT-e204ab, an unverified, self-labelled "[Preliminary Draft]")
proposes a polynomial-time quantum DCP algorithm, proved in its own text only
for dihedral group order `N = 2^n`. `H-CSIDH-3eaede` (`IDEA-20260813-e6d55d`)
asked whether this construction, specialized to the zero-noise limit, is a
legitimate instantiation of Simon's own stated theorem when applied to
CSIDH-512's actual class-group order -- which is not a power of 2.

**It is not, under the current, fully-searched literature.** CSIDH-512's
exact class-group order was independently re-derived from CSI-FiSh
(Beullens-Kleinjung-Vercauteren, IACR eprint 2019/498) and cross-verified:

```
N = 3 x 37 x 1407181 x 51593604295295867744293584889
      x 31599414504681995853008278745587832204909
  = 254652442229484275177030186010639202161620514305486423592570860975597611726191
```

(258 bits, `log2(N) = 257.1369928597118`, matching the paper's own stated
"approximately 2^257.136"). No sentence in Simon 2026's own text, or in any
of its cited predecessors (Regev 2004, Kuperberg 2005, Ettinger-Hoyer) --
all four read in full by three independent sessions -- names a technique,
with a page/lemma citation, extending Simon's `N=2^n`-restricted proof
(Section 2.2, Theorem/Proof) to this actual, non-power-of-2 `N`, with that
technique's own preconditions checked.

**The most serious constructive attempt to overturn this failed on
structural grounds, not merely an absent citation.** Kuperberg 2005 (a
cited predecessor) does supply a citable general-N technique for his own,
different dihedral-HSP algorithm: a CRT decomposition `N = 2^a M` plus an
automorphism relabeling (Section 5, Algorithm 2), with a stated
complexity-preservation claim. An independent red-team review tested
directly whether this technique is algorithm-agnostic -- i.e., whether it
could be composed onto Simon's construction regardless of the "different
construction" label -- and found it cannot, for two independent reasons:
(1) **computational-model mismatch**: Kuperberg's algorithms are all stated
`Input: an oracle f: D_N -> S`, and his CRT trick works by re-querying a
twisted oracle at each of `ceil(log2 N)` steps; Simon's construction is
explicitly *sample*-based (a pre-supplied stream of possibly-faulty states),
with no oracle to compose an automorphism onto. (2) **no odd-modulus
recovery analog**: even granting the relabeling step is portable, Kuperberg's
construction still needs a digit-recovery procedure for the `M`-component,
supplied only by re-invoking his own sieve; no source anywhere defines an
analogous recursion compatible with Simon's binary-digit, fault-tolerant
erasure machinery (Lemmas 1-4). A third, independent instance of the same
CRT technique was found in Childs-Jao-Soukharev 2014's own Appendix
(Algorithm 8 / Theorem A.1) -- built entirely on Kuperberg-style sieve
subroutines, reinforcing rather than weakening this separation.

A proves-too-much control applied the same strict operative test, unchanged,
to Kuperberg's own Theorem 1.1 (also first proved only for `N=2^n`) and
correctly returned the opposite outcome (applicable), since Kuperberg's own
paper supplies the citable patch for his own construction -- confirming the
test discriminates "patched in the same paper" from "never patched anywhere
in the citable record," rather than blanket-rejecting every `N=2^n`-first
proof.

## Independence and robustness

Independently reproduced by two fully separate review sessions, each
re-fetching all four (plus, beyond the required scope, two additional)
primary sources live rather than trusting the executor's transcriptions,
with byte-identical downloaded file sizes and byte-verbatim citation
confirmation at the cited page/section locations. Class-group-order
arithmetic was independently re-verified via four separate primality-testing
implementations (sympy, from-scratch Miller-Rabin/Fermat, GNU `factor`,
OpenSSL) with zero disagreement, and a third-party, differently-authored,
peer-reviewed citation (Peikert 2019/725, EUROCRYPT 2020) was independently
located that states the identical class-group order.

## Why this is a barrier finding and not a proof of impossibility, and what it is not

**This is a citation-existence finding, not a mathematical-impossibility
proof.** Both independent reviews explicitly and repeatedly warn against
collapsing "no currently-citable reduction exists" into "no reduction is
mathematically possible" -- any future citation, restatement, or synthesis
of this finding must preserve that distinction.

**What is NOT established:**
1. **Premise (ii)** of `H-CSIDH-3eaede` (the crossover-order/cost-model
   question against Kuperberg's sieve) remains untested and, given premise
   (i)'s negative outcome and the hypothesis's own conditional (AND)
   structure, is moot for this specific hypothesis chain.
2. **Mathematical impossibility** of any general-N extension of Simon's
   technique is not shown -- only that none is currently citable.
3. **Simon 2026's Lemma 3** and the rest of the paper's correctness are
   untouched.
4. **CSIDH's security** is not addressed in any way; no attack, speedup, or
   security-margin claim is made.

**The sharpest open question this finding narrows to** (per the red-team's
own `next_concrete_action`): does any published or citable dihedral/abelian-HSP
construction define a fault-tolerant, noise-resistant recovery procedure for
an odd-modulus component -- a genuine noise-tolerant analog of Kuperberg's/CJS's
CRT patch, rather than the error-free sieve version both currently supply? A
"no" would close this lane on a sharper, more defensible obstruction than "no
citation found"; a "yes" would be the most direct route to reopening premise
(i).

## Promotion-gate status

`DEC-20260906-29caf8` records `reject_scoped` for `H-CSIDH-3eaede`'s premise
(i) chain at evidence strength `strong` (two independent adversarial reviews,
each re-fetching every primary source live, zero discrepancy, a survived
constructive falsification attempt). Per CLAUDE.md's knowledge-promotion
gate, a `reject_scoped` decision at `strong` strength promotes this finding
rather than stating `not_warranted`.
