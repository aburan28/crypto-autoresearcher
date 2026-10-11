---
id: KN-OPEN-3c8f51
type: open_problem
title: >-
  What produces, and how far in n does it persist, the degree-4 Macaulay
  refutation of most unsatisfiable m = 2 S_3 descents on Semaev's diagonal?
tags: [semaev, summation-polynomial, s3, weil-descent, characteristic-two, macaulay, xl,
  degree-of-regularity, first-fall-degree, solving-degree, unsatisfiability-certificate,
  proposition-s, certbin, open, ecdlp]
confidence: unverified
status: open
source_refs: [EV-CERTBIN-6c3e0a, DEC-20260923-f25b97, EXP-CERTBIN-4e92d7, RUN-CERTBIN-3b7e05,
  H-CERTBIN-a73f1c, RQ-CERTBIN-836ce2, KN-OPEN-d218ec, KN-LIT-fa346d, KN-LIT-7604, KN-TECH-b18366]
added: 2026-09-23
superseded_by: null
---

## Statement

### The observation (preliminary)

The observation comes from one run on one curve (EV-CERTBIN-6c3e0a O-10, O-11). The setting is n = 17 (F_2[t]/(t^17+t^3+1)), m = 2, l = 9 (V = {deg < 9}), which lies on Semaev's diagonal k = ceil(n/m), with one random ordinary curve (h = 4). The D = 4 multilinear Macaulay matrix of the Weil-descended S_3 system, with field equations, has the constant in its row space for:

- **324 of 386 (0.839, CP95 [0.799, 0.875])** unsatisfiable subgroup-target attempts;
- 0 of 386 of the same attempts at D = 3;
- 0 of 115-138 in same-support random affine and random-F_2 null systems at D = 4;
- no satisfiable instance in any family (sound by Proposition S).

For uniform x_R the rate is 0.845 on x(2E), 0.60 on x(E) \ x(2E) and 0.66 on the twist. Nine sampled refutations were certified by an explicit combination sum lambda_i mu_i f_{k_i} = 1, using code independent of the run.

The one S_3-specific ingredient exhibited so far is a linear consequence: sum_k Tr(t^k/x_R^2) f_k = v_0 + v_9 + Tr(B/x_R^2). It holds on every curve-algebra instance and fails on every null instance. It does not explain degree 4: with one linear equation the semi-regular series (1+z)^17/(1+z^2)^16 still gives D_reg = 5.

### What is open

- **(A) Mechanism.** Which structure of S_3 in characteristic 2 produces a degree-4 refutation for most unsatisfiable targets, when the semi-regular model predicts 5? Why does membership of x_R in x(2E) modulate the rate?
- **(B) Persistence in n.** Along the diagonal (n = 19, 23, ...), does the D = 4 refutation rate stay near 0.84, or decay toward the nulls' 0?
- **(C) The remainder.** Is the 16% "not reached at D <= 4" a genuine D* > 4, or an artifact of the plain Macaulay closure, which does not reuse degree-fallen polynomials the way F4 does? This is KN-OPEN-d218ec gap (B) at a shared cell.

## Why it matters here

A sound one-bit unsatisfiability filter needs no learned trace. The trace-replay premise that motivated EXP-CERTBIN-4e92d7 failed at this cell, and this filter is the part of that premise's "divergence as signal" that survived.

It is worthless at m = 2, where root-finding (2^l per attempt) decides satisfiability outright. It could matter only at m >= 3 or in the chained regime, where enumeration costs 2^{(m-1)l} and the rate is unmeasured.

Separately, a stable low refutation degree on the diagonal bears on the same surface as Semaev's Assumption 1 (KN-OPEN-d218ec). It is a Macaulay-closure datum, not an F4 step degree.

## Resolution criterion

1. **RC-1 (zero new sampling).** Run a D = 5 and an iterated-D4 / mutant-XL closure on the 62 archived "not reached" unsatisfiable instances of RUN-CERTBIN-3b7e05, plus 62 archived satisfiable controls. Verify every certificate with independent code. This answers (C) at n = 17.
2. **n = 19 cell.** At l = 10, D = 4, on about 400 subgroup targets with same-support nulls and the x(2E) split, measure the rate against n. This answers (B) at its first step.
3. **An exact account for (A).** Either an explicit degree-4 identity derived from S_3's structure, or a proof that none exists generically, together with an explanation of the x(2E) modulation.
4. **Replicate on further curves.** At least one h = 2 curve and a random-V replicate, before any rate is quoted as characteristic of the family.

## What must NOT be said in the meantime

- **Not** "S_3 systems are refuted at degree 4". This is one curve, one n and one closure definition.
- **Not** evidence for or against Semaev's Assumption 1. This cell lies on its diagonal, so the observation is the assumption's content at work, not a test of it. It is also Macaulay closure, not F4 step degree.
- **Not** a relation-search speedup at any size. At m = 2 root-finding dominates, and at m >= 3 nothing is measured.
- **Supportable instead:** at n = 17, m = 2, l = 9 and one curve, a degree-4 Macaulay refutation was found for 84% of unsatisfiable subgroup-target attempts, and for 0% of the same-support nulls. The result is sound by theorem and sample-certified.

## Related open surface

- **KN-OPEN-d218ec.** Its gaps (A) and (B), and its resolution item 4 ("prefer certificates to completion"), share this cell's diagonal and its definitional question.
- **KN-LIT-7604 (Kosters-Yeo, reported).** Its low first fall degree via a group morphism is consistent with the exhibited linear consequence. That consistency is not verified.
