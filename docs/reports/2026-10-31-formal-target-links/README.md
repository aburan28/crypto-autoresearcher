# Formal target source links at main `e03417c`

This is a navigation inventory of the 91 tracked `formal/targets/*.yaml` specs at commit `e03417ca2831c6000f100e55b5cb4185b0421072`. The [machine-readable rows](links.json) bind each target, declared source, and Lean module to SHA-256 hashes of exact Git blobs. Generate them with:

```sh
python3 tools/formal_target_source_inventory.py e03417ca2831c6000f100e55b5cb4185b0421072 docs/reports/2026-10-31-formal-target-links/links.json
```

The [diagram](links.svg) and [PDF](links.pdf) show the pointer categories. They count target specs, not distinct scientific claims or verified experiments.

| Link observed in target or its declared source | Targets | Distinct IDs | Meaning |
| --- | ---: | ---: | --- |
| Declared source lives under `experiments/EXP-*` | 8 | 2 direct experiment directories | Direct file path |
| Declared source lives under a `RUN-*` directory | 0 | 0 | No target points directly at a run directory |
| Standalone `EXP-*` ID occurs in declared source bytes | 17 | 6 | Lexical mention, all six IDs have tracked experiment directories |
| Standalone `RUN-*` ID occurs in declared source bytes | 11 | 5 | Lexical mention; three IDs match `RUN-*` directories |
| All target specs | 91 | 32 distinct declared source files | Other sources include research notes and reports |

The categories overlap. The two `RUN-FROB-91ee9c-*` IDs without matching `RUN-*` directory names are recorded in `TASK-*` run directories: `TASK-20260914-7119f2/manifest.yaml` and `TASK-20260921-51bc02/manifest.yaml`. A separate exact-tree manifest inspection found the declared IDs matched their YAML manifests; this inventory does not replay those runs or validate all manifest artifacts.

A prior scratch lexical pass reported eight distinct `EXP-*` strings. Two were substrings of `AMD-EXP-BINSTD-8bdf86-20261003-ell89` amendment IDs in `knowledge/findings/KN-FIND-48f0ae.md`. Requiring a standalone ID boundary yields six. The 91 target/source/module rows at this head are byte-identical to the earlier `ad91212179e737d829076ca593d608261590ba89` inventory.

Every target names a tracked source and Lean module, and this script checks those Git blobs. It does not elaborate a theorem, audit axioms, compare the theorem statement to the source claim, validate a measurement, or establish that a run executed. `source_status: PROVED` is source metadata, not this review's verdict. Those checks require named Lean receipts and independent source and execution reviews. No proof-coverage percentage follows from this inventory; the claim denominator is still being constructed across all three repositories.
