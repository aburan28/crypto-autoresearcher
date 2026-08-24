---
id: KN-TECH-14efa5
type: technique
title: Obtaining a working Sage, fpylll and G6K in a wheels-only container - the exact routes, and the two link-level fixes
tags: [tooling, environment, sage, passagemath, fpylll, g6k, sieve, bkz, lattice, reproducibility, harness, infrastructure]
complexity: "Not an algorithm. Installation cost only: passagemath-standard 10.8.7 installs from binary wheels in roughly 3 minutes; g6k 0.1.2 compiles from source in roughly 8 minutes given the two fixes below. Measured on the container described in `environment_verified_on`"
applicability: "Any harness that needs real Sage, real lattice reduction, or a real sieve in a container with no root package installs, no conda, and no working `sagemath-standard` source build. Supersedes the belief - held by GOAL-MLKEM-003 across twelve batches - that these are unobtainable in such an environment"
confidence: verified_by_execution
source_refs: [KN-OPEN-016, KN-TECH-038, KN-TECH-039, KN-TECH-040, EV-MLKEM-af61e7, DEC-20260803-64b55b]
added: 2026-08-03
superseded_by: null
---

## Why this entry exists

`GOAL-MLKEM-003` was blocked on lattice tooling **three times** — G6K in BATCH-003
and BATCH-005, Sage throughout — and closed at budget on 2026-08-03 without ever
measuring a sieve. Its closing decision `DEC-20260803-64b55b` names the successor's
instrument as unavailable. Within an hour of that commit, all three components were
obtained and verified functional in the same container.

The blocker was never that these packages cannot run here. It was that each failed
route was read as evidence about the environment rather than about the route. Three
failures were treated as a searched space; the space was not searched.

**This entry is infrastructure, not a research finding.** It establishes no fact about
ML-KEM, no cost, and no security claim. It records how to obtain instruments.

## The three routes, including the ones that fail

### Sage — `passagemath-standard`, not `sagemath-standard`

Routes that FAIL, all reproduced twice:

| route | failure |
|---|---|
| system binary | no `sage` on PATH |
| `apt-get install sagemath` | `Candidate: (none)` |
| `pip install sagemath-standard` | cypari2 build: `cannot find an installation of PARI/GP: make sure that the 'gp' program is in your $PATH` |
| conda | not present |

The route that WORKS:

```sh
python3 -m venv /tmp/sagevenv
/tmp/sagevenv/bin/pip install --no-cache-dir passagemath-standard   # 10.8.7, binary wheels
```

`sage.all` imports; the full name surface used by the lattice-estimator works.
**passagemath is a redistribution/fork of the Sage source, not upstream sagemath.**
Numbers agreeing under it are implementation agreement across arithmetic backends —
see "What this does not buy" below.

Discriminator against a Sage *shim*: `PowerSeriesRing` works under passagemath and
raises under the `tools/sage_free_estimator` shim. Checking `sage.__version__` is not
enough — a shim on `PYTHONPATH` will shadow the real package, and
`/tmp/sagevenv/bin/python` was observed resolving `sage.all` to the shim when the shim
was on the path. **Verify from inside the interpreter** that the shim directory is not
on `sys.path`.

### fpylll — arrives free with passagemath, with one broken default

`fpylll 0.6.4` is installed as a passagemath dependency. `LLL`, `GSO`, `BKZ` and
`fpylll.algorithms.bkz2.BKZReduction` all work.

**Broken default:** `BKZ.DEFAULT_STRATEGY` points at the wheel's build-time path
`/project/local/share/fplll/strategies/default.json`, which does not exist in the
wheel. `BKZ.EasyParam(...)` and any `BKZ.Param(strategies=BKZ.DEFAULT_STRATEGY)` fail
with `RuntimeError: Cannot open strategies file.`

Fix — build pruning-free strategies in-process:

```python
from fpylll import BKZ
from fpylll.fplll.bkz_param import Strategy
strategies = [Strategy(b) for b in range(41)]
param = BKZ.Param(block_size=30, strategies=strategies,
                  max_loops=4, flags=BKZ.MAX_LOOPS)
```

Verified: dim 60 qary q=3329, BKZ-30 x4 loops, `||b0||` 160.4 -> 130.3 in 0.3s.

**fpylll ships no sieve.** `fpylll.algorithms` is `babai`, `bkz`, `bkz2`,
`simple_bkz`, `simple_dbkz` — all enumeration. There is no `GaussSieve` and no
`Siever`. A harness that needs sieve behaviour is not served by fpylll alone; that was
the state this entry's campaign closed in.

### G6K — builds from PyPI given two fixes

`g6k 0.1.2` is on PyPI. Two failures in sequence, each with a one-line fix:

**1. Build isolation hides Cython.**

```
ModuleNotFoundError: No module named 'Cython'
```

The isolated build env lacks Cython even though the venv has 3.2.9. Fix:
`pip install --no-build-isolation g6k`.

**2. The link finds no `libgmp`.**

After that, every sieve kernel compiles — `bgj1_sieve.o`, `bdgl_sieve.o`,
`hk3_sieve.o`, `fht_lsh.o`, `control.o`, `sieving.o` — and only the final link fails:

```
/usr/bin/ld: cannot find -lgmp: No such file or directory
```

`libgmp.so.10` IS present at `/usr/lib/x86_64-linux-gnu/libgmp.so.10`; only the
`-dev` symlink `libgmp.so` is missing, and `libgmp-dev` needs a root install. No root
is required — provide the symlink yourself:

```sh
mkdir -p "$SCRATCH/gmplink"
ln -sf /usr/lib/x86_64-linux-gnu/libgmp.so.10 "$SCRATCH/gmplink/libgmp.so"
export LIBRARY_PATH="$SCRATCH/gmplink:$LIBRARY_PATH" LDFLAGS="-L$SCRATCH/gmplink"
/tmp/sagevenv/bin/pip install --no-build-isolation g6k
```

Result: `Successfully installed g6k-0.1.2`, exposing all five kernels —
`gauss_sieve`, `bgj1_sieve`, `bdgl_sieve`, `hk3_sieve`, `nv_sieve` — plus
`g6k.algorithms.{pump, workout, bkz, ducas18}`.

**Construction gotcha:** `Siever(GSO.Mat(A))` raises
`ValueError: Siever requires UinvT enabled`. Pass the `IntegerMatrix` directly and let
G6K build the GSO: `g = Siever(A)`, then read `g.M`.

## Verification actually run

Every claim above was executed, not inferred.

```
fpylll 0.6.4   dim 60 qary q=3329, BKZ-30 x4:  ||b0|| 160.4 -> 130.3   (0.3s)
g6k    0.1.2   dim 50 qary q=3329, gauss_sieve: db 4075 vectors        (0.94s)
```

The 4075-vector database is the object that matters: it is a population of
**sieve-produced vectors**, which is what a score-distribution measurement needs and
what no batch of `GOAL-MLKEM-003` could produce.

## What this does not buy

- **No ML-KEM result of any kind.** No break, no security proof, no FIPS 203
  parameter set affected or cleared, no cost claim.
- **Not upstream Sage.** passagemath 10.8.7 is a redistribution; upstream sagemath
  10.9 (which computed `RUN-MLKEM-015-001`) remains unobtainable here. Agreement
  under passagemath is *implementation* agreement — a second arithmetic backend
  running the same estimator source. It buys reproducibility, not independence of the
  cost model.
- **It does not reopen `GOAL-MLKEM-003`.** That goal closed on the merits of its
  evidence, not on tooling: its completion criterion 1 asks for calibration by
  measured sieve behaviour that the campaign never performed, and criterion 2 failed
  because uncharged assumptions were shown present. Availability of an instrument
  today does not retroactively satisfy either. What it changes is the **successor's**
  viability.
- **These are install facts, not benchmarks.** The two timings are single runs at toy
  dimensions on one container, recorded to show the code executes.

## Consequence for the successor

`KN-OPEN-016`'s actual question — does the dual-sieve attack work as costed — was
recorded in `DEC-20260803-64b55b` as needing "the score distribution of sieve-produced
dual vectors MEASURED", on "a different instrument". That instrument now exists in
this environment and is verified functional. The successor's opening task is no longer
"obtain a sieve"; it is to measure with one.

## The transferable lesson

Three install failures were read as "the environment cannot do this" and became a
standing blocker across twelve batches and two campaigns' worth of budget. Each
failure was informative about **one route** and about nothing else. The correct
handling of a negative install result is the one `AGENTS.md` rule 5 already
prescribes for infrastructure failure: record the exact command and output, and do
NOT convert it into a claim about what is possible.

A concrete discipline that would have caught this: before recording a tool as
unobtainable, name the routes not yet tried. Here they were "a redistribution of the
package under a different name", "the same build without isolation", and "supply the
missing dev symlink yourself" — all cheap, and all found only after the campaign
that needed them had closed.
