# EXP-SGCP-EMBED-002 V16 Revision Response

## Reviewed boundary

V16 responds to the three fresh exact-commit reviews of
`8adba3ad4ddf7055cc098831dff2a33e1e469810` and coordinator decision
`DEC-SGCP-EMBED-002-015`. Theory, accounting, and red team all issued
`REVISE before launch-plan design`. No V15 review authorized a generated row,
canonical matrix, runner, launch plan, execution, or budget increase.

## Finding disposition

| V15 finding | V16 disposition |
|---|---|
| Exactly two leading POSIX separators remain a distinct `//` anchor, falsifying the blanket repeated-separator alias claim | Public admission and the private descriptor walker now reject `Path.anchor == "//"` before absolute normalization. The contract distinguishes internal repeated separators, the exact double anchor, and the host behavior for three or more leading separators. |
| The internal alias control did not cover the leading anchor or the full lexical boundary | The same focused method is now table-driven over dot, internal double separators, absolute in-root paths, three-leading separators, exact leading `//`, explicit `..`, the development root, and an ordinary outside path. Existing production symlink-parent controls remain separate because the standalone parser is not a filesystem-race oracle. |
| Post-publication status attribution was checked through the normalized path rather than the raw alias | Production and standalone status now receive every admitted raw alias after publication and must attribute the exact winning publication identifier. |
| Handoff, active ledger, revision-response next action, and test-log next action described already completed V15 validation and commit work as pending | V15 is preserved as a reviewed scoped negative. The live handoff, ledger, and V16 documents record completed validation and route only to fresh exact-commit review. |
| The contract title still said version 14 | The title now says version 16 and is covered by a current-state consistency check against specification, ledger, source, and verifier versions. |
| “Repository-wide suite” overstated `unittest discover` collection | The evidence section is named `Repository-wide unittest-discover suite`. It reports only the 225 collected unittest methods and explicitly excludes the 27 module-level pytest-style tests unless a separate pytest run is recorded. |

The reviewers found no mathematical, containment, accounting, inventory, or
zero-budget defect. V16 changes path-policy precision, controls, and governance
records only.

## Exact POSIX path policy

For the controlled POSIX runtime:

- ordinary `.` components and internal repeated separators are normalized
  aliases;
- exactly two leading separators form the distinct `//` anchor and are rejected;
- three or more leading separators collapse to the ordinary `/` anchor under
  `pathlib` and `abspath`, then undergo the same root containment test;
- explicit `..` is rejected before normalization;
- the development root itself and every normalized outside-root destination are
  rejected;
- an absolute in-root destination follows the ordinary containment rule.

The private descriptor walker independently repeats the anchor,
parent-traversal, root, and containment checks before opening the normalized
parent chain no-follow.

## Control scope

The standalone parser now applies the same lexical anchor, parent-traversal,
root, and containment policy before receipt validation. It remains independent
of production status and canonicalization helpers, and it remains outside the
descriptor-race theorem. Symlinked-parent rejection is therefore asserted by
the production writer, status, and descriptor traversal controls.

The focused alias method publishes through a raw spelling containing both
`./` and an internal `//`, then reuses that same spelling for production and
standalone accepted-state attribution.

## Test-scope boundary

The broad recorded command is:

```bash
python3 -B -m unittest discover -s tests -v
```

It is a repository-wide unittest-discover pass, not an all-framework claim.
Twenty-seven module-level pytest-style functions are outside that command and
remain unexecuted unless separately recorded.

## Claim and budget boundary

The curve grid, predicates, compiler, ordering digest, graph, cap schedule,
five-field objective, family gate, and completed operation vector
`480/112/336/218/4218` are unchanged.

No relation yield, rank, linear algebra, target descent, fixed-curve
preprocessing crossover, rho improvement, fitted exponent, deployment result,
or ECDLP break is established. V16 remains `HYPOTHESIS`, `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

No generated V16 curve-family density row, canonical matrix, runner, launch
plan, or run is authorized. `maximum_runs=0`.

## Next action

Obtain fresh independent read-only theory, accounting, and red-team reviews of
the exact commit containing this response. Even three scoped `GO` decisions
could authorize only a separate hash-complete launch-plan design, not
execution.
