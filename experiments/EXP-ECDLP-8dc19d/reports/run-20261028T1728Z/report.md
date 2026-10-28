# Fixed-circuit transfer observations

EXP-ECDLP-8dc19d / RUN-ECDLP-994f70 / H-ECDLP-e1270c / GOAL-ECDLP-e70832

Observations only; scientific interpretation and status changes require a separate evidence review.

Operational status: completed; independent arithmetic/coverage check: True; retained verifier errors: 0.

Observed curve fixtures: 40; retained per-curve/arm metric rows: 440. Registered arms: 11.

The fixed recipes are (alpha,beta)=(1,-4),(-2,-1), a=1,2,3,5, with four fresh blinded trials per public target. Conversion x=a*b^-1*x' mod r is publicly checked. BSGS runs once per target; the uniform-candidate control makes four attempts. Identity is excluded from primary success rates.

Source and protocol byte bindings are listed on separate lines in the reproduction section below; full bindings also remain in report-inputs.json.

## Complete arm counts

Totals below are labelled sums of retained per-curve records, not a pooled statistical inference. Unique IDs are distinct within curve/arm; successes are attempt events.

| Arm | Observed / planned attempts | Verified events | Unique target IDs | Zero-success domains | Unverified domains |
|---|---|---|---|---|---|
| circuit1.a1 | 10032 / 10032 | 7 | 7 | 39 | 0 |
| circuit1.a2 | 10032 / 10032 | 62 | 53 | 38 | 0 |
| circuit1.a3 | 10032 / 10032 | 3 | 3 | 37 | 0 |
| circuit1.a5 | 10032 / 10032 | 4 | 4 | 39 | 0 |
| circuit2.a1 | 10032 / 10032 | 53 | 29 | 36 | 0 |
| circuit2.a2 | 10032 / 10032 | 3 | 3 | 38 | 0 |
| circuit2.a3 | 10032 / 10032 | 27 | 24 | 37 | 0 |
| circuit2.a5 | 10032 / 10032 | 67 | 58 | 37 | 0 |
| uniform_candidate | 10032 / 10032 | 33 | 32 | 29 | 0 |
| bsgs_reference | 2508 / 2508 | 2508 | 2508 | 0 | 0 |
| aa_circuit1_a1 | 10032 / 10032 | 7 | 7 | 39 | 0 |

The full per-curve/arm table is `per-curve-arm.csv`, including every reported status, unresolved/unattempted count, registered Wilson interval, undefined ratio and first-success prefix. No zero-success domain is removed.

## Cost definitions and full vectors

Registered, explicitly modeled cold retry: S + mean(online)/q. Observed batch work per success event: (S + sum online)/s. These are copied as exact numerator/denominator values; s=0 remains undefined. Online prefixes through first success retain all four trials for targets without a success; one-time setup is separate.

`operation-vectors.csv` retains setup, all online phases, full diagnostics and prefix counter families. `common-work.json` retains cohort generation, proposal rejection, certification and input-validation work. `validator-controls.json` retains independent validator work. Total vectors and their phase breakdowns overlap and must not be added together. Group-call graphs show only the registered solver group-call component, never an overall priced machine cost; common preprocessing is shown separately rather than silently erased.

## Observed fixture scope

| Curve ID | Panel | Field p | Order r | Public targets | Stratum |
|---|---|---|---|---|---|
| transfer-small-r17-000-4df84a4178b0 | exact | 19 | 17 | 16 | small-r17 |
| transfer-small-r17-001-7843c37524fd | exact | 23 | 17 | 16 | small-r17 |
| transfer-small-r29-000-15eaead10ee0 | exact | 31 | 29 | 28 | small-r29 |
| transfer-small-r29-001-da5ccaa2d316 | exact | 31 | 29 | 28 | small-r29 |
| transfer-small-r61-000-6cda0b6db679 | exact | 47 | 61 | 60 | small-r61 |
| transfer-small-r61-001-c4500ab805e0 | exact | 67 | 61 | 60 | small-r61 |
| transfer-small-r127-000-0872ff3d540e | exact | 139 | 127 | 126 | small-r127 |
| transfer-small-r127-001-9e1032a8b55f | exact | 107 | 127 | 126 | small-r127 |
| transfer-sampled-r10-000-d9a310bd040c | sampled | 907 | 919 | 64 | sampled-r10 |
| transfer-sampled-r10-001-f359b10a2617 | sampled | 971 | 929 | 64 | sampled-r10 |
| transfer-sampled-r10-002-686faa35a67d | sampled | 859 | 839 | 64 | sampled-r10 |
| transfer-sampled-r10-003-4957592e1bbd | sampled | 967 | 1009 | 64 | sampled-r10 |
| transfer-sampled-r10-004-60ef2ea293e8 | sampled | 599 | 613 | 64 | sampled-r10 |
| transfer-sampled-r10-005-04f2c6f1555a | sampled | 971 | 1009 | 64 | sampled-r10 |
| transfer-sampled-r10-006-fcaa2afd257e | sampled | 827 | 859 | 64 | sampled-r10 |
| transfer-sampled-r10-007-edda0c186f8e | sampled | 967 | 919 | 64 | sampled-r10 |
| transfer-sampled-r10-008-1ee6b66f0a9b | sampled | 883 | 857 | 64 | sampled-r10 |
| transfer-sampled-r10-009-799c4a6eb035 | sampled | 547 | 557 | 64 | sampled-r10 |
| transfer-sampled-r10-010-7ae0956fd72d | sampled | 823 | 877 | 64 | sampled-r10 |
| transfer-sampled-r10-011-cccdb8bcb95e | sampled | 739 | 769 | 64 | sampled-r10 |
| transfer-sampled-r10-012-9a2a49101bf0 | sampled | 863 | 853 | 64 | sampled-r10 |
| transfer-sampled-r10-013-4d20b519be02 | sampled | 587 | 631 | 64 | sampled-r10 |
| transfer-sampled-r10-014-4f4ac4fe3943 | sampled | 599 | 641 | 64 | sampled-r10 |
| transfer-sampled-r10-015-280d9f011c6b | sampled | 619 | 601 | 64 | sampled-r10 |
| transfer-sampled-r13-000-80b0110183d1 | sampled | 6079 | 6011 | 64 | sampled-r13 |
| transfer-sampled-r13-001-d1752e10c21d | sampled | 6679 | 6823 | 64 | sampled-r13 |
| transfer-sampled-r13-002-a8c6042a4de5 | sampled | 7151 | 7307 | 64 | sampled-r13 |
| transfer-sampled-r13-003-e6e0c99da9f8 | sampled | 7219 | 7243 | 64 | sampled-r13 |
| transfer-sampled-r13-004-2961b0b70374 | sampled | 7243 | 7229 | 64 | sampled-r13 |
| transfer-sampled-r13-005-1006b5c5b0ba | sampled | 4943 | 4909 | 64 | sampled-r13 |
| transfer-sampled-r13-006-3df950d9375a | sampled | 5519 | 5573 | 64 | sampled-r13 |
| transfer-sampled-r13-007-e0bce6311232 | sampled | 5387 | 5471 | 64 | sampled-r13 |
| transfer-sampled-r13-008-ea632dab6270 | sampled | 6791 | 6679 | 64 | sampled-r13 |
| transfer-sampled-r13-009-69671b548816 | sampled | 8059 | 8167 | 64 | sampled-r13 |
| transfer-sampled-r13-010-ca7d167aef66 | sampled | 6899 | 6971 | 64 | sampled-r13 |
| transfer-sampled-r13-011-184afa48d1ae | sampled | 6659 | 6761 | 64 | sampled-r13 |
| transfer-sampled-r13-012-50bb448686c6 | sampled | 6947 | 6967 | 64 | sampled-r13 |
| transfer-sampled-r13-013-b39885cf6559 | sampled | 5839 | 5783 | 64 | sampled-r13 |
| transfer-sampled-r13-014-0728a16d698f | sampled | 4231 | 4261 | 64 | sampled-r13 |
| transfer-sampled-r13-015-ef69229f8e71 | sampled | 5507 | 5431 | 64 | sampled-r13 |

## Controls, coverage and limits

Frozen stream coverage: `{"attempts": {"complete": true, "expected": 102828, "missing": 0, "observed": 102828}, "diagnostics": {"complete": true, "expected": 3744, "missing": 0, "observed": 3744}, "setups": {"complete": true, "expected": 440, "missing": 0, "observed": 440}}`.

Legacy known-fixture controls: `true`. Fresh cohort schedule/exclusions: `true`. Full small-curve cocycle pairs checked: 41960.

The same-shape odd/anchor null functions are validator-only context. Their fixed source rule and supplied outcomes are retained in validator-controls.json, without new algorithm rows or padded attempts. The null deliberately lacks coordinate covariance; no tail or familywise inference is introduced here.

These are recorded observations and registered descriptive calculations, not an evidence-review verdict. The two circuits and public multipliers were fixed before the fresh cohort. Every failed, undefined, empty-interval, unresolved and unattempted outcome remains visible. Public inputs contain no scalar labels.

A success event is one independently checked attempt. Four repetitions can recover the same target more than once; unique target-ID recovery is a separate quantity. A/A is a repeated control, not a new candidate or independent baseline. The working BSGS reference executes once per target and is not padded to four tries.

Per-curve Wilson intervals are the registered random-blinding descriptions copied from the census. Fresh public nonce and domain-separated SHA256 rejection draws supply the stated sampling model; trace consistency does not prove randomness or fresh execution. Heterogeneous curves are not pooled into a new binomial inference. A zero-success sample does not prove a zero population probability.

Cold retry estimates S+mean(C)/q and observed batch work (S+sum(C))/success-events are different quantities. Neither is work per unique target, a measured runtime, or an arbitrary weighted machine-cost total. Undefined zero-success ratios remain undefined. All four failed attempts contribute to the first-success prefix for a target with no success; setup remains separate.

Group, coordinate-field, scalar-field, RNG, lookup and other operation families are retained without a common price. Cohort generation, rejected proposals, certification, common input validation, diagnostic and validator work remain separate. Source counter execution is not independently replayed; all clocks are unqualified. The exact small all-r diagnostic is validator-only and never gates a primary attempt.

Canonical research graphs were checked by scope: this descriptive report changes no scientific status or verified global theorem edge. The figures below are fresh derived views of the retained records.

## Recorded per-curve comparisons

\clearpage

### q-panel-1

![RUN-ECDLP-994f70: q including all registered arms](q-panel-1.png){width=95%}

\clearpage

### q-panel-2

![RUN-ECDLP-994f70: q including all registered arms](q-panel-2.png){width=95%}

\clearpage

### q-panel-3

![RUN-ECDLP-994f70: q including all registered arms](q-panel-3.png){width=95%}

\clearpage

### q-panel-4

![RUN-ECDLP-994f70: q including all registered arms](q-panel-4.png){width=95%}

\clearpage

### cold_group_work-panel-1

![RUN-ECDLP-994f70: cold_group_work including all registered arms](cold_group_work-panel-1.png){width=95%}

\clearpage

### cold_group_work-panel-2

![RUN-ECDLP-994f70: cold_group_work including all registered arms](cold_group_work-panel-2.png){width=95%}

\clearpage

### cold_group_work-panel-3

![RUN-ECDLP-994f70: cold_group_work including all registered arms](cold_group_work-panel-3.png){width=95%}

\clearpage

### cold_group_work-panel-4

![RUN-ECDLP-994f70: cold_group_work including all registered arms](cold_group_work-panel-4.png){width=95%}

\clearpage

## Reproduction and immutable inputs

The postrun directory retains the exact verifier invocation, independent report, census, original export and file-check receipts. This renderer imports no candidate, generator or verifier code. All input byte bindings are listed in `report-inputs.json`; the renderer source is included alongside the report. Historical absolute paths are provenance and are restored or explicitly rebased during artifact hydration, never rewritten inside an earlier run record.

Source revision:

```text
3af20095591932b16c0cd33461650962ec0c98fe
```

Official protocol:

```text
fa961d179668d86e1dfcdc393d80c60e4f6a6f3ac541b9015f6011beba050c71
```

Standalone compute plan:

```text
4d57a58cdf2fd6f3f748b8ac5b7adb9011ad99db4a37314cd3c459caed529fcc
```

Source manifest:

```text
5dbfd6260333fac95d6cb181795aee2e70331779a3a1ee9be89f92788cbf3d71
```
