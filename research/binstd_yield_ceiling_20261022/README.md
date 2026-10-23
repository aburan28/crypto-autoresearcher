# BINSTD toy yield ceiling: conditional Lean check

This note records a machine check of the arithmetic used in
`KN-FIND-48f0ae`. The source claim is the finding at commit
`3bed4d891777a15a44ecd577958c99279483696b`. The proof source and task
spec are committed at `b775b3f6ee613c1f5f7f44ee48abe79d09bd0f18`.

## Statement and scope

`CryptoResearch.Binstd.YieldCeiling.saturated_open_below_band` states that,
for natural-number counts, `targets > 0`, `openHits = targets`, and
`tauHits <= targets` imply `4*tauHits < 5*openHits`. On matched targets this
is the strict failure of the frozen `R_tau >= 1.25*R_open` prediction. The
same Lean file also instantiates the archived `(tauHits, openHits)` pairs
`(16,40)`, `(40,40)`, `(20,40)`, and `(40,40)`.

The hypotheses expose the empirical inputs. Lean does not establish that
the archived runner produced those counts, that its elliptic-curve arithmetic
is correct, or that the result transfers to another field, solver, or attack.
The finding therefore retains `confidence: reported` and
`proof_status: empirical_only` for the experimental result.

## Exact verification

The write-once [verification receipt](verification.json) has SHA-256
`685af9aa6a53633f7698930df6398237ba06c7eaca5348cc29f99df8bb0e013c`.
It pins the theorem file to
`c76fc9b90a315285ac0d4e9913938f46131605575e5868ed90600773479463de`,
the task spec to
`27137822c177c837e8dca5325faa4ef1730df5bf4a9d9a1d417f4003afc997b8`,
and records Lean `4.35.0-rc1` with the checked-in Mathlib manifest.

The pinned Mathlib cache decompressed 8,857 files. A direct module build
passed (3,092 jobs); the complete project build passed (3,142 jobs). The
project axiom audit checked 480 theorems and found only the allowed standard
axioms. The exact-target verifier returned `machine_verified`, with no
forbidden constructs, a passed build, and passed project and target axiom
audits. The receipt explicitly marks independent semantic review as pending.

Reproduce with the checked-in `formal/lean-toolchain` and
`formal/lake-manifest.json`:

```bash
cd formal
lake exe cache get
lake build
lake env lean AxiomAudit.lean
cd ..
python3 -m orchestration.formal.cli verify \
  --task-file formal/targets/binstd-yield-ceiling.yaml \
  --artifact-out /tmp/binstd-yield-ceiling-new-receipt.json
```

The verifier refuses to overwrite a receipt; choose a fresh output path.
The command requires Python 3.11 or newer and PyYAML. The formal result does
not change any measured performance, leaderboard row, or dashboard.
