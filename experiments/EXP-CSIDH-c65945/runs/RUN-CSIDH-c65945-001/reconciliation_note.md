# Reconciliation note / exact-agreement statement

Per specification.yaml required_artifacts[2]: "A reconciliation note if the
two sources disagree ..., or an explicit 'exact agreement' statement if they
do not."

**EXPLICIT EXACT AGREEMENT STATEMENT:** The two independently obtained
citations for CSIDH-512's class-group order N —

1. Beullens, Kleinjung, Vercauteren, "CSI-FiSh..." (IACR ePrint 2019/498),
   Section 3, p.8 (paper text, retrieved live this run); and
2. The CSI-FiSh reference implementation's own `classgroup_data/class number`
   file (https://github.com/KULeuven-COSIC/CSI-FiSh, retrieved live this run)

agree EXACTLY:

```
N = 254652442229484275177030186010639202161620514305486423592570860975597611726191
```

No disagreement occurred; no reconciliation was required. Per
invalidation_rules[0], had the two values disagreed and the discrepancy been
unresolvable within budget, this run would have been reported INVALID for
the applicability conclusion rather than proceeding — that condition did not
arise.
