---
id: KN-OPEN-007
type: open_problem
title: Do the bond tensors of the recursive Semaev resultant tree admit low-rank factorizations over F_p, with the recall-0.99 bond rank growing with exponent < 1 in the per-variable degree?
tags: [tensor-network, tensor-train, bond-rank, semaev, resultant, border-rank, finite-field, open]
confidence: reported
status: open
source_refs: [KN-LIT-032, KN-LIT-033, KN-TECH-013]
added: 2026-07-22
superseded_by: null
---

## Statement
Reading the recursive Semaev resultant tree S_m = Res_y(S_k, S_{m-k+2}) as a
tree tensor network over F_p (bonds = eliminated variables), do the intermediate
bond tensors have low exact/border rank? Concretely: does the bond rank chi
needed for contraction-based solution counting to reach recall >= 0.99 grow with
exponent < 1 in the per-variable degree d = 2^{m-2} -- beating the ~1.979 dense
composed-resultant exponent -- or are the bond ranks generically full, so
rank-truncated contraction degenerates to dense elimination?

## Current state (as reported)
Tensor-train / tensor-network contraction and the treewidth cost model
(KN-LIT-032, KN-LIT-033, KN-TECH-013) are standard, and counting-as-contraction
is established for #CSP (KN-LIT-034). But bond ranks of *resultant recursion*
tensors -- generic or Semaev -- have not been measured. The program's tensor-train
candidate (RQ-TTN-001, H-TTN-001, EXP-TTN-001) implemented exact-F_p
rank-revealing contraction at toy scale and reported a SCOPED NEGATIVE (bond
ranks near full; no sub-exponential chi). By rule 6 that closes only the tested
scope; the asymptotic bond-rank growth law remains open.

## Why it matters here
It converts the dense-resultant degree obstruction (measured exponent ~1.979,
KN-OPEN-002) into a measurable *rank-growth* question with an exact stopping
criterion (recall vs chi). A sub-exponential chi(m) would change the complexity
driver of point-decomposition counting; a full-rank result is a clean negative
theory (border-rank lower bound on resultant tensors). Over F_p the truncation
must be exact rank-revealing, not SVD, so the measurement is well-defined but
norm-free -- a caveat any claim here must respect.

## Reconciliation note, 2026-10-18 (appended; the entry above is unchanged)

Register status stays `open`. The tensor-train results are a toy-scale scoped negative (m <= 6, p <= 1009) and this entry says the asymptotic bond-rank law remains open.

Premise check: the request that prompted this note cited DEC-20260722-003..006 as the proving decisions. They are not: DEC-20260722-003 targets GOAL-MLKEM-001/IDEA-20260722-001, -004 and -005 target GOAL-ECDLP-001 BATCH-002 task handling, and no DEC-20260722-006 exists. The records that do bear on this problem are below.

- EV-TTN-001 (H-TTN-001, `weakens`, preliminary, m <= 5) and EV-TTN-002 (`strengthens`, preliminary, m = 6 only).
- H-TTN-806b84 `proposed`; H-ECDLP-0fd4b9 `supported` also cites this entry (DEC-20261003-c6641c); neither resolves the growth law.
- DEC-20260804-139a86 records "H-TTN-001 rejected_scoped (earlier campaign)"; no decision record with that disposition was located in `ledger/decisions/` by hypothesis id in this pass, so that line is unverified here.

Decision request: `coordination/remediation/DECISION-REQUEST-20261018-ic-integrity.md`, item R-3.
