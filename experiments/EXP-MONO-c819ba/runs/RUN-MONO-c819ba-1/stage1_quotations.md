# Stage-1 verbatim quotations (EXP-MONO-c819ba)

## KN-FIND-007

path: knowledge/findings/KN-FIND-007.md
obtained: True

### quote_mean_formula

Let `G` be a finite abelian group of order `N` and `D ⊆ G \ {0}` a factor base of `B` distinct elements. For `m ≥ 1` and `r ∈ G`, let `c_D(r)` be the number of size-`m` multisets from `D` summing to `r`. Then

```
sum over r in G of c_D(r)  =  binomial(B + m - 1, m)
```

exactly, because every size-`m` multiset sums to exactly one target. Hence the mean per-target decomposition yield is

```
E_r[c_D(r)] = binomial(B + m - 1, m) / N
```

for **every** base of size `B`, independently of how `D` is chosen.

### convention_finding

KN-FIND-007's conservation mean is C(B+m-1,m)/N, the UNORDERED-MULTISET mean (c_D(r) counts multisets, i.e. unordered selections with repetition), NOT literally F^m/N (the ORDERED-tuple mean this contract's (I1) proves). These are NOT related by a single, m-independent multiplicative convention factor: C(B+m-1,m) = B(B+1)...(B+m-1)/m! differs from B^m/m! by lower-order terms in B that do not vanish for finite B (they agree only asymptotically as B -> infinity with m fixed). H-MONO-663fb4 mechanism step (4) already anticipated exactly this gap, calling F^m/N 'the ordered-convention ANALOGUE' of KN-FIND-007's multiset mean, not asserting equality, and pre-committing to report both conventions at every cell for this reason.

### stage1_disposition

This does NOT trigger the Stage-1 stop condition, because that condition asks whether the mean is 'the ordered mean F^m/N under any reasonable convention' -- and this contract's own Stage 0 gate proves (I1) mean_R N_m(R) = F^m/N as an EXACT identity for the ORDERED convention, independent of and prior to reading KN-FIND-007. KN-FIND-007 is a DIFFERENT, self-consistent conservation identity for the MULTISET convention (C(B+m-1,m)/N), not a contradiction of (I1); the two are related but not identical, exactly as mechanism step (4) flagged. The identification of N_m with 'the relation event' therefore stands for the ORDERED convention this contract's (I1)/(I2)/(I3) are stated in, and the multiset convention reported at every cell (N_m(R)/m!, this contract's declared combinatorial factor) is an approximation to KN-FIND-007's exact multiset count that becomes exact only when no repeated-element m-tuple sums to the same target -- a discrepancy reported as a finding, not silently reconciled.


## KN-FIND-d4f820

path: knowledge/findings/KN-FIND-d4f820.md
obtained: True

### quote

The constant C = max|hat{1_F}(k)| / sqrt(B) (full k-range DFT):

| p | C (mean) | log2(p) |
|---|---------|---------|
| 1009 | 3.0 | 10.0 |
| 4001 | 3.5 | 11.9 |
| 9001 | 3.7 | 13.1 |
| 50021 | 3.84 | 15.6 |

**Best fit: C(p) ~ p^{0.055}** (very slow power law, consistent with O((log p)^{0.5}) or O(log log p)).

### alpha_value

0.055 (mean C over random curves, small-x factor base, full-range DFT)


## KN-FIND-4c9e71

path: knowledge/findings/KN-FIND-4c9e71.md
obtained: True

### quote

Adversarial maximum of C = max_k |hat{1_F}(k)| / sqrt(B) across all tested random curves:

| p | n measurements | max C | mean C |
|---|---|---|---|
| 1009 | 152 | 3.90 | 2.99 |
| 4001 | 26 | 3.87 | 3.47 |
| 9001 | 12 | 4.11 | 3.63 |

**The adversarial maximum is BOUNDED ~ 4 and NOT growing significantly with p.**
No counter-example to H-PSEUDO found in 190+ measurements.

## CORRECTION (BATCH-107)

At p=50021: max C = 5.182 (6 measurements), consistent with p^{0.079} scaling (prediction: 5.31). The adversarial max DOES grow with p, following the same C ~ p^{0.079} as the mean. Earlier claim of "O(1) max C" was premature (too narrow p range: 1009..9001 spans only 9x).

**Revised finding**: BOTH mean C AND adversarial max C scale as ~ p^{0.079}.

### alpha_value

0.079 (adversarial-max C, AFTER the BATCH-107 self-correction superseding the record's own earlier, in-document 'O(1) max C' claim)


## DEC-20260804-0a4bc2

path: ledger/decisions/DEC-20260804-0a4bc2.yaml
obtained: True

### quote

H-PSEUDO-83817b REVISED: The empirical evidence now supports the STRONGER form: C = O(1) (constant, not growing with p), not just C = O(p^{0.079}).

Evidence:
- Mean C ~ p^{0.079} (from BATCH-073..079 random curve measurements)
- Adversarial max C ~ 4 across p=1009..9001 (this batch + BATCH-104)
- The adversarial max is NOT growing with p (3.90 -> 3.87 -> 4.11)

H-PSEUDO with C <= 5 (universal constant) is STRONGLY empirically supported.

### max_c_verdict

O(1), constant ~4, dated 2026-08-04, batch 105/104 data only (p up to 9001).


## DEC-20260804-4f3a3b

path: ledger/decisions/DEC-20260804-4f3a3b.yaml
obtained: True

### quote

KN-FIND-4c9e71 promoted. H-PSEUDO-83817b updated: predictions now state adversarial max C ~ O(1) ~= 4 (revised from C ~ p^{0.079}).

THE CENTRAL REMAINING QUESTION: does the adversarial max C stay bounded at p=50021? ... This measurement would discriminate.

### max_c_verdict

Same as DEC-20260804-0a4bc2 (O(1)/~4), BUT this decision explicitly flags the p=50021 measurement as the discriminating test still to be run -- and KN-FIND-4c9e71's OWN 'CORRECTION (BATCH-107)' section (quoted above) reports that test came back at max C=5.182, consistent with GROWTH (p^0.079), superseding the O(1) verdict this decision records. Both DEC-20260804-0a4bc2 and DEC-20260804-4f3a3b therefore record a verdict (O(1)) that the promoted finding's own later correction (still within the same KN-FIND-4c9e71 record) reverses; neither decision record itself was updated to reflect the correction. Reported as-is, not resolved, per this contract's Stage-1 scope.


## DEC-20260804-53c89f

path: ledger/decisions/DEC-20260804-53c89f.yaml
obtained: True

### quote

CORRECTED EMPIRICAL DESCRIPTION: |hat{1_F}(k)| ~ sqrt(B) * p^{0.079} (not sqrt(N) * constant as previously hypothesized in BATCH-080). This means C = max|hat|/sqrt(B) ~ p^{0.079} is genuine p-growth, not a B_frac normalization artifact.

### max_c_verdict

'genuine p-growth' (p^{0.079}), directly contradicting DEC-20260804-0a4bc2 and DEC-20260804-4f3a3b's 'C = O(1)' verdict recorded the SAME DAY (2026-08-04). This is the two-way max-C disagreement H-MONO-663fb4 mechanism step (7) reports and does not resolve.


## DEC-20260804-f320c2

path: ledger/decisions/DEC-20260804-f320c2.yaml
obtained: True

### quote

BGS spectral gap direction: CLOSED with named obstruction (abelian spectral gap obstruction: E(F_p) ≅ Z/N is cyclic abelian, BGS requires non-abelian; even if a spectral gap existed, birthday collision threshold is orthogonal to mixing time).

### spectral_gap_scope_note

This record closes the Cay(Z/N,S) spectral-gap ROUTE for |S|=O(1) generating sets, on the abelian-group obstruction; it does not itself state the |S|=O(1) scope boundary in those words (that paraphrase in H-MONO-663fb4 mechanism step (7), attributed to this record as '(R2) closes the spectral-gap route for Cay(Z/N,S) at |S|=O(1)', is a reasonable reading of the abelian_spectral_gap_obstruction clause but is NOT a verbatim phrase in this record -- the record's own words are quoted above in full for independent judgement).


