# Four-level m=51 rho archive

The scientific execution is preserved as a deterministic compressed tar
archive. The frozen pre-run files in this directory remain byte-identical to
commit `1a3bdfb1b940a5affaa6a49f992d785d9d0e1568`; all post-run material is
additive.

## Artifact identities

| artifact | bytes | SHA-256 |
|---|---:|---|
| `run1.tar.zst` | 2,185,115 | `d8d334f8f4e4b14ef2f05066d6230fb2d082fb869342355d92e161fdd019059e` |
| `analysis.json` | 1,100,453 | `14f7fee5513bfc936df2d56b39b4877017f262fbf1aedf8ee0d8845f17accb72` |
| `run_manifest.json` | 3,629 | `82982751a94431552930bfcae0e23c3e4941c41f3e3dafa33cae6dd372cdf970` |
| `setup_robustness_decision.json` | 1,021 | `e9dbf3de0c69850e1ba9657a558a8a0650ade8b313d5aae756e7eca6d261a4c5` |
| `four-level-diagnostics.svg` | 12,683 | `5ceb05e3c6e1ff462dacec0244b880b799218b3eaf33915eb83bcc02781d58fa` |
| `four-level-diagnostics.png` | 206,456 | `677a1794b22ec3be972bfe6cad57d3a1bb44660a07c3c20781de6c6d6eb2a1c2` |
| `report.pdf` | 279,374 | `381e00009fdc13fb193dd5318c8a126fcdf3315b1a64d27a84059432db1fb2a8` |

The archive's root `MANIFEST.sha256` has SHA-256
`4f1cc09059d4f61f698e3633f358324aaa26368a3e475a7ebdfb5f2ff9f179cd`
and lists 139 regular files. Its primary tree manifest has SHA-256
`ba1d08f8a1552659cf454ca2fae7a946f235310ad45b9618584a319419521fe7`.
The primary records have SHA-256
`ebe8e47e1b124cdb8d1e329dfe6859c79223a73cefc90091ee926afde9f514eb`
and contain 20,480 data rows. The in-run primary analysis has SHA-256
`0e2ba4cb34da60e17e77ae9bc587dec788f254766e9c695d1e9ca217436a759c`.

## Verification

From this directory:

```sh
sha256sum -c FROZEN.sha256
sha256sum -c RESULTS.sha256
sha256sum run1.tar.zst analysis.json run_manifest.json setup_robustness_decision.json

audit_dir=$(mktemp -d /tmp/m51-deep-rho-archive.XXXXXX)
tar --zstd -xf run1.tar.zst -C "$audit_dir"
(
  cd "$audit_dir"
  sha256sum -c MANIFEST.sha256
  cd primary
  sha256sum -c MANIFEST.sha256
)
```

The archived tree was extracted independently at
`/tmp/m51-rho-archive-audit-1a3bdfb1`; byte-for-byte comparison with the
restored sealed live tree passed, both manifests passed, and no `__pycache__`
entry was present in the archive.

The four CSV views are deterministically derived from the copied analysis and
the archived `primary/records.csv` using only the standard library:

```sh
python3 -I -S -B derive_summaries.py \
  --analysis analysis.json \
  --records "$audit_dir/primary/records.csv" \
  --output-dir .

python3 -I -S -B plot_results.py \
  --contrasts contrast-summary.csv \
  --aa aa-summary.csv \
  --analysis analysis.json \
  --out four-level-diagnostics.svg

XDG_CONFIG_HOME=/tmp/m51-inkscape-config \
XDG_CACHE_HOME=/tmp/m51-inkscape-cache \
inkscape four-level-diagnostics.svg --export-type=png \
  --export-filename=four-level-diagnostics.png --export-width=1550

SOURCE_DATE_EPOCH=1791897118 TZ=UTC \
XDG_CONFIG_HOME=/tmp/m51-pandoc-config \
XDG_CACHE_HOME=/tmp/m51-pandoc-cache \
pandoc RESULTS.md --from=gfm --pdf-engine=pdflatex \
  -V geometry:margin=0.7in -V colorlinks=true \
  -V linkcolor=blue -V urlcolor=blue \
  -V 'header-includes=\pdftrailerid{}' -o report.pdf
```

`RESULTS.md` is the report source. All three rendered PDF pages were opened and
inspected after generation; the graph, gate warning, tables, hashes, and claim
boundary were legible.

`REPLICATION_SIZING.md` is an additive, provisional planning note for a fresh
run. It is neither part of the sealed archive nor authority to release the
current run's withheld labels.

## Relocation limitation

Manifest verification and byte comparison are relocation-safe. A direct rerun
of the frozen analyzer against the archive extracted at a different absolute
path is not: the attempted relocated replay stopped at
`RNG cross-language execution differs: 0` because recorded execution receipts
bind the original absolute run path. This is a replay-packaging limitation,
not a changed scientific record and not evidence for or against any curve
effect. The original-path analysis completed, and an independent statistical
recomputation reproduced its reported quantities exactly. No frozen analyzer
was edited to bypass the receipt binding.

## Immutability boundary

`run1.tar.zst` is the archived sealed run. `analysis.json`, the CSV files, the
figure, and this report are additive views. Corrections must be new additive
records; neither the archive nor the 16 paths covered by `FROZEN.sha256` may be
rewritten.
