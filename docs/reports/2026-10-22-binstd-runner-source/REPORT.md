# BINSTD runner source restoration with prior toy replay

The current main checkout at `13eb217678653267553dcbfa9601f2564f63706b`
contains the original BINSTD runner. It accepts neither `--ells`,
`--artifact-tag` nor `--seed`, although the archived ell89 and ell89r1
Stage-1 commands use those options. This patch restores the exact runner
bytes from the second historical snapshot to the live
`implementation/run.py`. It changes no archived run, result, protocol,
decision, field helper or checker.

## Source custody

The [source custody checker](check_custody.py) reads both snapshot commits
and the two archived `environment.json` source maps. The ell89 snapshot
`8efed7dea288e827a4889aec8b768180b6b55e02` contains runner SHA-256
`7efcf8e6bbfcf00b3846f2283bc1c9f2a850f7f23acc98297d3ac238d0dbfd12`,
matching `RUN-BINSTD-43abd4`. The ell89r1 snapshot
`c39a3d5e4cc750a837d6339d2ff28f3209c67619` contains
`17a3175a30b229154f16087f85907845336dfac616a1f2f46c9f43223789c7bb`,
matching `RUN-BINSTD-a2a24c`. `gf2.py` and `check.py` match both
environments and already matched current main. The current runner now
matches the latter archived source exactly. The
[custody receipt](custody.json) records all hashes.

The ell89 source introduced the additive ell={8,9} panel and
factor-kernel construction. The ell89r1 source added seed selection
for the second panel. Restoring the latter makes both archived CLI
forms available. The [editable graph](source.dot), [SVG](source.svg),
[PNG](source.png), [figure PDF](source-figure.pdf) and [report PDF](report.pdf)
show this source progression.

## Checks

The [independent algebra check](check_algebra.py) uses SymPy over
GF(2) to confirm that `t^17+t^3+1` is irreducible and that
`x^17+1` factors into irreducibles with degrees 1,8,8. It checks the
runner's admissible dimensions `{0,1,8,9,16,17}`, its actual
Frobenius-closed kernel bases of dimensions 8 and 9, and the absence
of constructed bases at 3 and 4. Sampled curve points satisfy the
binary curve equation; small samples check group associativity and
the optimized three-point membership against brute-force triples.
The [algebra receipt](algebra.json) gives exact sample counts and
source hash.

The complete-tree ledger validator still exits 1 on this branch:
141 unsuppressed errors in 39 paths, byte-for-byte the same log as
main `13eb21767865`. The [validation receipt](validation.json) and
[log](validator.log) bind that unchanged gate; this source patch does
not repair unrelated archived records.

The earlier [source-pinned replay](../2026-10-22-binstd-ell89-replay/report.md)
already extracted the historical source and ran both Stage-1 panels
in temporary directories. Its [receipt](../2026-10-22-binstd-ell89-replay/receipt.json)
records byte-for-byte matches for both frozen yield matrices,
dimension tables and result notes, with independent bounded
arithmetic controls. This source restoration makes the latest
historical implementation available on the live branch; it does
not repeat the completed full-panel replay or alter frozen artifacts.

## Limits

The restored code and earlier replay concern only the toy n=17,
ell={8,9}, 40-target exhaustive m=3 pin. The repository's historical
`check.py` checks result shape and status but does not independently
validate per-target relations. The sample algebra tests and earlier
same-code deterministic replay do not prove the empirical yield in
Lean, certify statistical independence, establish a speedup or make
any deployed-curve security claim. Existing evidence and decisions
retain their original scopes.
The prior replay inspected the canonical performance dashboard and
found no speedup or attack-cost row to update. Restoring source does
not change a measured value or that dashboard reading.
