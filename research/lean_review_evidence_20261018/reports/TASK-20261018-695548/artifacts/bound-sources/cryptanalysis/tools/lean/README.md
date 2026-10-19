# Lean proof gate

The gate implementation is copied from `tools/lean/` in [aburan28/crypto](https://github.com/aburan28/crypto/tree/main/tools/lean), which is the source of truth. Change the implementation there first and copy it here. The [2026-10-18 retrospective](../../research/lean_retrospective_20261018/README.md) adds this repository's first research Lake project; CI discovers and checks it in addition to the gate self-test.

`proof-gate.sh` checks every Lean target in the repository. CI runs it through
[`lean-proof-gate.yml`](../../.github/workflows/lean-proof-gate.yml): on any
change to a `.lean` file, lakefile, toolchain or manifest, on pushes to `main`,
and weekly.

| target | how it is checked |
|:--|:--|
| Lake project (directory with `lakefile.toml` / `lakefile.lean`) | `lake exe cache get` if it uses Mathlib, then `lake build` plus each tracked proof source as an explicit Lake source target, then an audit of every module the project built |
| standalone `.lean` file outside any Lake project | `lean -o` against the core library under its directory's `lean-toolchain`, then an audit of that module |

The audit, [`AuditAxioms.lean`](AuditAxioms.lean), imports the modules and
collects each theorem's **transitive** axioms. Only `propext`,
`Classical.choice` and `Quot.sound` are accepted. A grep cannot do this
check, because a `sorry` or axiom can be several imports away.

| outcome | meaning |
|:--|:--|
| `ok` | kernel-checked on the standard foundations |
| `TRUST` | closed by `native_decide` (the compiler is trusted, not only the kernel), and listed in [`trusted-native.txt`](trusted-native.txt) with the reason and where the study records that decision |
| `FAIL` | `sorryAx`, an unlisted `native_decide`, or any other axiom |

A target also fails when it doesn't build, when its build log reports
`declaration uses 'sorry'`, or when it contains no theorems. A gate that
audits nothing must not pass. A failure to fetch the Mathlib cache exits 3. It
is an infrastructure failure and never evidence about a proof.

```sh
tools/lean/proof-gate.sh --list                  # what would be checked
tools/lean/proof-gate.sh                         # check everything
tools/lean/proof-gate.sh research/<study>/lean   # one target
tools/lean/proof-gate.sh --out receipts          # keep build and audit logs
```

## Self-test

[`selftest/run.sh`](selftest/run.sh) runs the gate on known fixtures:
`selftest/pass/` must pass (`Good.lean` is plain kernel proofs,
`Trusted.lean` is a listed `native_decide`), and `selftest/fail/` must fail
(a transitive `sorry`, a user axiom, an unlisted `native_decide`, a file with
no theorems, a build error). CI runs it on every trigger, so the gate stays
exercised even in a repository with no Lean proofs yet. `LEAN_GATE_TRUSTED`
points the gate at another trust manifest. The self-test uses its own one.

## What passing does not mean

The gate shows that each theorem is proved from the standard foundations. It
does **not** show that the Lean statement is the report's theorem. That
fidelity check (quantifiers, hypotheses, the bridge to the real objects) is
still a review of the proof against the report.

## Adding to `trusted-native.txt`

Only add an entry when the study itself records the decision to trust the
compiler, for example a registered replay. Never add one for a theorem a
report or paper states as proved. Prefer `decide` or `decide +kernel` when
they finish in reasonable time.

The gate rejects tracked project sources omitted by default targets. Declare
each source as a Lake module; an unknown source target fails with
`FAIL_build_source`. `sources.log` records the inventory. Nested projects are
checked separately; Lake configuration and gate code/fixtures under
`tools/lean` or `tools/selftest` are explicit exclusions. Untracked files
are outside repository discovery. The self-test exercises omitted, configured
positive and configured negative project modules. A green default build alone
is insufficient.
