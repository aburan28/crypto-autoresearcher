---
id: KN-TECH-013
type: technique
title: Tensor-network / tensor-train contraction for counting and solving
tags: [tensor-network, tensor-train, contraction, treewidth, bond-rank, counting, semaev, ecdlp]
confidence: reported
complexity: contraction cost exp(treewidth) or ~ tree * chi^{O(1)} * d for bond rank chi; exact contraction == dense elimination
applicability: counting/enumerating solutions of a recursively-structured algebraic system by reading it as a contractible tensor network
source_refs: [KN-LIT-032, KN-LIT-033, KN-LIT-034]
added: 2026-07-22
superseded_by: null
---

## Method
Read a structured system as a tensor network -- indices are variables, tensors
are the local constraints/relations, bonds are eliminated variables -- and
contract it. Two levers control cost:
- **Structure**: contraction cost is exponential in the network's treewidth
  (Markov-Shi, KN-LIT-033); low-treewidth/tree networks contract cheaply.
- **Rank truncation**: represent intermediate tensors in tensor-train / hierarchical
  form (Oseledets, KN-LIT-032) and truncate to bond rank chi, trading recall for
  cost. Counting/enumeration by (conditional) contraction (Kourtis et al.,
  KN-LIT-034).

## Complexity indicator
The recursive Semaev definition S_m = Res_y(S_k, S_{m-k+2}) is a *tree* tensor
network whose bonds are eliminated variables. Exact contraction equals the dense
composed-resultant cost (the program's measured ~1.979 exponent). Rank-chi
contraction costs ~ tree * chi^{O(1)} * d, so the method wins iff the bond rank
chi needed for recall >= 0.99 grows with exponent < 1 in the per-variable degree
d = 2^{m-2}. Bond rank, not degree, is the new invariant (KN-OPEN-007).

## Program usage
The mechanism of RQ-TTN-001 / EXP-TTN-001. Every emitted tuple is verified
exactly by direct Semaev evaluation, so truncation can only lose recall, never
precision. The measurable is the bond-rank growth law chi(m, log q).

## Applicability limits
Over F_p there is NO SVD norm, so "low rank" must mean exact rank-revealing
factorization / border rank, not singular-value truncation -- and recall must be
measured empirically. Likely obstruction: resultant tensors generically have
maximal (full) border rank, so chi explodes like d^{Theta(m)} and the method
degenerates to dense elimination with overhead. In that case the experiment still
yields a measured rank-growth law -- a negative-theory contribution. The program's
own TTN experiment reported a scoped negative.
