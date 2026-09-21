# Pre-implementation benchmark review v1

## Handoff: subset-norm accounting audit

### Claim or task

Audit Tier A, Tier B, one-instance, comparator, and generic-preprocessing gates.

### Status

`OPEN`: `REVISE`; `NO-GO` for implementation.

The `o(B^2)` online and `B^2.5=n^0.5` one-instance boundaries are correct.
The original Tier A had no advice cap, Tier B did not constrain peak offline
workspace asymptotically, and the root operator dimensions remain unknown.

### Assumptions

- `N2=Theta(B^2)` and `N3=Theta(B^3)` are measured hypotheses, not identities.
- Relation probability is measured on uniform targets.
- Rank yield is conditional on current matrix rank.
- A relation oracle is not an arbitrary-target DLP algorithm.

### Evidence so far

The corrected tiers are:

```text
Tier A: S_total=O(B^3), T_online=o(B^2), TargetLive=o(B^2)
Tier B: S_total=o(B^3), PeakWorkspace_pre=o(B^3),
        T_online=o(B^2), TargetLive=o(B^2)
one instance: advice, writes, construction, peak workspace,
              actual relation batch, linear algebra, and descent=o(B^2.5).
```

A finite `0.8x` ratio does not prove Tier B; the empirical advice and workspace
upper slopes must be below 3. Explicit D3 can pass Tier A but fails the
one-instance gate.

The generic `S*T^2` theorem accepts generic-group oracle queries and
arbitrary-target DLP success. It does not accept coordinate field operations,
memory traffic, relation probability, or multi-target batch sharing.

### Failure modes

- Arbitrary high advice trivializes the Tier A online gate.
- Peak preprocessing materializes and discards D3 while persistent advice is
  reported as compressed.
- Explicit D3 terminal lift is omitted from Tier B advice.
- Equal-advice BSGS or constructive generic preprocessing omits one side's
  preprocessing.
- A one-target average is extrapolated to relation collection.

### Next concrete action

Fill root modules, specialization, displacement rank, storage, query work,
child restriction, and terminal lift; then repeat the zero-run accounting review.

### Artifact paths

- `contract.md`
- `object-dimension-ledger.md`
- `notes/ecdlp_relation_preprocessing_accounting_20260718.md`

## Coordinator response

Tier A is now capped at actual `O(B^3)` advice; Tier B includes subcubic peak
workspace and slope gates; the one-instance boundary includes advice writes and
the confidence-sized relation batch. Comparator and generic-theorem formulas are
explicit. The `REVISE` and implementation `NO-GO` remain because the root
operator and all of its dimensions are undefined.
