# Exact experiment ID pointers in formal targets, 2026-10-27

This is a syntactic inventory of `crypto-autoresearcher` at commit
`351c9c021c7be044ade54dc7e352b33d3a772244` (`main` when scanned). It
does not review any theorem or experiment. The question is narrow: which
existing `EXP-*` directory IDs occur as exact tokens in a registered formal
target YAML file, its declared text source, or its Lean theorem source?

## Method and source

`tools/formal_pointer_inventory.py` reads the immutable Git tree, enumerates
top-level experiment directories with tracked files, and reads each registered
YAML target and its named sources through `git cat-file --batch`. It accepts
an `EXP-*` token only if that exact ID exists as an experiment directory in
the same tree. The 1 MB text-source limit skipped **zero** sources in this
scan. It writes the deterministic [inventory](inventory.json), including
every ID, target, witness path and source-tree hash. The editable
[plot source](plot.py) renders the [SVG](coverage.svg) and the same figure in
the [PDF report](report.pdf).

Reproduce against the frozen commit with:

```sh
python3 tools/formal_pointer_inventory.py \
  --repo . \
  --revision 351c9c021c7be044ade54dc7e352b33d3a772244 \
  --out /tmp/formal-pointer-inventory.json
```

## Observations

| Counted object | Total | With an exact existing experiment ID pointer | Remaining without an exact pointer |
| --- | ---: | ---: | ---: |
| Experiment directories | 2,784 | 5 (0.180%) | 2,779 |
| Registered formal targets | 87 | 17 (19.5%) | 70 |

The five linked IDs are `EXP-BINSTD-8bdf86`, `EXP-FROB-91ee9c`,
`EXP-FROB-b8cf21`, `EXP-GFPN-05ff43`, and `EXP-NCP-001`. The last is a
legacy short-suffix ID named in `research/THM_COMMUTATOR_KERNEL1.md`, the
declared source for three NCP formal targets. The earlier local pointer
diagnostic counted four IDs; this scan records the NCP source references
explicitly. A pointer does not show that any NCP theorem proves the
experiment's full claim.

The [figure](coverage.svg) uses exact proportional widths for both bars.
The experiment-linked segment is a thin sliver because 5/2,784 is small.
No uncertainty interval applies to these deterministic Git-tree counts;
the uncertainty is semantic and outside this inventory.

## Interpretation and limits

The inventory makes the claim-to-target linkage backlog visible. It does
**not** count validated experiments: a target can compile while its
statement is narrower than its cited run, and a target can be relevant
without spelling the experiment ID in the scanned text. The scan does not
check Lean declarations, axioms, source bridges, run digests, independent
replay, matched costs, or security/performance conclusions. It covers this
one repository's committed `main` only, not `crypto`, `cryptanalysis`, open
PR heads, or uncommitted work. No official research status changes here.

Next, each high-impact historical claim needs an exact source/run pointer,
a statement-to-claim review, a pinned Lean build and axiom audit, independent
review, and the experiment's own execution/cost checks. Public dashboard
publication remains subject to current-head GitHub checks.
