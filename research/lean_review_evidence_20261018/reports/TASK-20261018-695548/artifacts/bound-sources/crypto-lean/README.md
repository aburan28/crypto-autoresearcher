# CryptoLean

A shared Lean 4 library for
[aburan28/crypto](https://github.com/aburan28/crypto),
[aburan28/cryptanalysis](https://github.com/aburan28/cryptanalysis) and
[aburan28/crypto-autoresearcher](https://github.com/aburan28/crypto-autoresearcher):
faithful definitions of the objects our proofs are about, and the proof gate
that checks them. The design and migration plan are in [docs/DESIGN.md](docs/DESIGN.md).

**Pinned:** Lean `v4.35.0`, Mathlib `cfc55fc` (2026-10-15). Every consumer
must build on the same toolchain (Lake requires it).

## Layers

| library | imports | contents |
|:--|:--|:--|
| `CryptoLeanCore` | Std only | `iterate` and return times; the N83 state-count bounds (`pairStates`, `squareStates`, `requestedEntries`, with proofs that the source files' two spellings agree); `GF(2)[t]` on `Nat` bit patterns (kernel-reducible, no `native_decide` needed); SplitMix64 |
| `CryptoLean` | Mathlib | short Weierstrass models and their generic, quartic and sextic twists; torsion fixing; cyclic and finite-field subfield twist tests; conductor arithmetic; Semaev's S₃ and its roots `x(R±F)` |
| `CryptoLean.Bridge` | both | proofs that a `Core` computation means the Mathlib object (so far: `iterate` equals `f^[n]`, `Returns` iff `Function.IsPeriodicPt`) |

Everything in `CryptoLean` was promoted from proofs that already passed in
`aburan28/crypto`. Each file's first line names its source.

## Using it

In the consumer's `lakefile.toml`:

```toml
[[require]]
name = "CryptoLean"
git = "https://github.com/aburan28/crypto-lean"
rev = "v0.1.0"
```

Then `lake update CryptoLean`, commit `lake-manifest.json`, and set
`lean-toolchain` to this repository's.

## Proof gate

`tools/proof-gate.sh` builds every Lean target of the repository it is run in
and audits each theorem's transitive axioms with `tools/AuditAxioms.lean`.
Only `propext`, `Classical.choice` and `Quot.sound` pass. `sorryAx`, an
unlisted `native_decide` and user axioms fail. So does a target with no
theorems. Consumers run the pinned copy from their repository root:

```sh
.lake/packages/CryptoLean/tools/proof-gate.sh
```

For a Lake project the gate also builds each tracked proof source explicitly,
using its source-path target, before auditing the built modules. A source
omitted by default targets must be declared as a Lake module; an unknown target
fails with `FAIL_build_source`. Nested projects are checked separately. Lake
configuration, the gate auditor and deliberate gate fixtures under `tools/lean`
or `tools/selftest` are outside the proof inventory. The receipt's `sources.log`
records that inventory. Untracked files are not covered by repository discovery.

A deliberate `native_decide` goes in the consumer's
`tools/lean/trusted-native.txt` with its reason, and is reported as `TRUST`.
`tools/selftest/run.sh` checks the gate itself: every fixture must pass or
fail *for the expected reason*, so a broken audit cannot pass the self-test.
Project controls include an omitted false proof and configured positive and
negative modules, independently of the default root's successful build.

Passing the gate shows that a theorem is proved from the standard foundations.
It does not show that the theorem is the claim a report makes. That still
needs review.

## Not yet in v0.1.0

- the `Bridge` theorem relating `GF2Poly.mod` to `Polynomial (ZMod 2)`
  reduction;
- the group-level `PointIsogeny` and the generic-group model on Mathlib `Group`;
- autoresearcher's Semaev symmetrization and fall-degree material;
- the `@[report_theorem]` attribute (design phase 4).
