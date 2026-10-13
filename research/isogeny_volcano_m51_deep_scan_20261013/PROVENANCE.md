# Provenance and development evidence

This file identifies inherited arithmetic, historical scripts, runtime
artifacts, and pre-freeze tests. `FROZEN.sha256`, created only after review,
binds the final local files byte-for-byte.

## Audited C lineage

The field representation and low-level carry-less arithmetic were taken from
the frozen m=51 rho study at commit
`929ccbcfce` (full object available from Git):

- `research/isogeny_volcano_m51_rho_20261013/rho.c`, SHA256
  `f86cf62f8c0bf6ea9bb35e5358e0aec99f995db5779b0cf179d1b896d7cb9327`;
- `research/isogeny_volcano_m51_rho_20261013/params.h`, SHA256
  `cb3790db6122996da89b260a6bd57301b02f5f96760fe80caacb795b3bef18b2`.

The candidate-sieve structure was informed by the historical m=41 search at
commit `9669c616`:

- `research/isogeny_volcano_rho_m41_20261006/search.c`, SHA256
  `b4f71d229c2daa918061d01c2c0b1a0704bae3cc79391539df614023582786e1`.

The indexed modeled PRP, strict parser, write-once output, mock lane, and
reference-vector mode are new for this study. `test_sieve_reference.py` is an
independent arithmetic oracle rather than a copy of the C x-only ladder.

## Historical GP lineage

The two files under `upstream/` are byte-exact copies from commit
`f0bdf9f739462766a9060532c59f9bfed69d00b1`:

- `second_level/lvl_check.gp` -> `upstream/lvl_check.gp`, SHA256
  `08ce9353a53c88710df716f0a3569bf12fcb6952ca8975df9b6b253d7c9b48b9`;
- `second_level/vert_down.gp` -> `upstream/vert_down.gp`, SHA256
  `d356605443edde74b52851124fafbc387c8354aef631655e646c572d81c797de`.

Additional historical sources used in the design were:

- `m51_m53/cm51_120871.gp`, SHA256
  `00c3f3b0780de8ce42e097bff078ca0d45abf53c145afc3c2e378141865c76f6`;
- `m51_m53/floor51_271_cm.txt`, SHA256
  `a73ef01d0cb78be9f1c3df131c5598eae394541ce85a55fab5b33efaeca8d91b`.

`floor271_orbits.csv` is a normalized 16-orbit table derived from the latter,
not a byte-exact copy. Its required SHA256 is
`bb4b64d5e8d53b323cd7493af435c738198b90b0ba8696316bb36e8709150fbe`.
`classify_recover.gp` is a new fail-closed batch classifier derived from the
historical torsion and Velu methods; it adds positive source and target
certificates, Frobenius-stable-kernel checks, pilot-fiber exclusion, and
control-only replay modes.

## GP runtime

The canonical container content ID is
`sha256:7436527cbf48e6e00a4b574c31725a90d5802160fb817a8f6bd94128d95a3cd4`.
It is built from
`debian:bookworm-slim@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587`
with Debian `pari-gp=2.15.2-1`.

For the host execution route, `/usr/bin/gp-2.15` was extracted byte-for-byte
from that image and independently compared with the in-image binary. Its
SHA256 is
`35b1fc1911407f5e893f5ab6b683ac660d164d5d84223b1d38645ebc96d43379`.
Because this executable dynamically links host libraries, `run_scan.py`
records raw `ldd` output and the resolved path, size, and SHA256 of every
shared object. Raw `ldd` text is retained in `host.json`, while resume and
phase fingerprints deliberately use the stable resolved paths and hashes and
exclude ASLR load addresses. Selected certificates remain eligible for a later replay in
the canonical container; the present harness does not claim that such a
second-implementation replay has already occurred for future scan hits. The
admitted runner rejects `--gp-image`: terminating the Docker CLI cannot prove
that the daemon-side container stopped, so the extracted binary is the only
long-run route and has no daemon-side container lifecycle. The Linux runner
is a required child subreaper; it terminates and reaps the full child PGID
before a bounded pipe drain even when the pipeline leader exits first, which
closes the corresponding host-process zombie/mutation path. GP is invoked with
`-f` under a minimal recorded environment, excluding user `gprc`, preload,
and library-path inputs. Python runner/children use `-I -S -B`.

## Key generation record

At `2026-10-13T08:55:02Z`, before any admitted outcome, the command
`openssl rand -hex 32` was run exactly once under OpenSSL 3.5.7 (9 Jun 2026)
and exited 0. It produced
`10456676ccd2e6bd1497bc8de889944eff4f72ebe81da37fbedb0a95b36853c6`.
The frozen counter-0 derivation produced
`c6ac26c5f692baa74a02c14f38de8e93bfe40c2d2ecbdcf7231ac6e79049d7b2`;
the inverse image of zero is 1,143,900,985,707,342, outside the scan range.
No key retry occurred for any other reason.

## Excluded feasibility pilot

The development pilot used raw `b=675235026289400`, bottom orbit minimum
`99224513745505`, and recovered parent orbit minimum `7746411922983`. It is
not scientific data. Normal mode excludes the entire 272-child parent fiber.
Control mode alone replays this exact child/parent, and its status is
incompatible with scientific selection.

## Pre-freeze development checks

The following checks were run without an admitted scientific scan:

- warning-clean C build and built-in self-test;
- a statically linked scanner and independent ELF-header rejection of dynamic
  interpreter/dependency segments;
- stricter C11/pedantic/UBSan self-test during implementation;
- twelve independent Python-vs-C GF/inversion/affine-scalar differential
  cases with both sieve outcomes, malformed-input tests, and O_EXCL tests;
- a GP-free end-to-end harness-contract test proving that a bound
  per-candidate `GP_ERROR` reaches the admitted no-backfill invalid path and
  that forged sieve/crater/f=271/pilot/direct-parent/certified benign labels
  are rejected by both validation layers, that orphan payload evidence or a
  changed GP driver is rejected, and that leader-exit descendants holding
  pipes are killed and reaped within a fixed bound;
- PRP derivation/vectors/inverse/zero-preimage checks, including under
  `PYTHONOPTIMIZE=2`, reduced-width exhaustive bijection, and self-test-key
  diagnostics;
- GP parser and exact negative labels;
- a latest 21-control batch under the pinned extracted GP binary, including
  all sixteen `f=271` exclusions and the three positive torsion/ascent/rank
  controls; it exited successfully in approximately 22 seconds; and
- Python compilation and JSON parsing checks.

Temporary development outputs live outside the repository and are not study
results. No command traversed the fixed 3.6-billion scientific rank range.
