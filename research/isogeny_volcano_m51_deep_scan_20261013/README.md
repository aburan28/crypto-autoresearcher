# m=51 deep conductor endpoint discovery

This directory preserves the completed discovery-only scan for new
`f_E=271*120871=32756041` bottom representatives and their certified
degree-271 ascending parents at `f_E=120871` in the ordinary Koblitz isogeny
class over `GF(2^51)`. It records observations, not a weakness verdict or a
performance claim.

## Scope and execution

| Requirement | Executed evidence | Status |
| --- | --- | --- |
| Exhaust the frozen rank interval | All 256 shards covered `[0, 3,600,000,000)`; `fixed_range_exhausted=true` | Verified complete |
| Retain and classify every sieve hit | 42 aggregate rows; 42 classification records | Verified complete |
| Certify bottom/parent endpoints | 42/42 have status `CERTIFIED_BOTTOM_PARENT` | Verified complete |
| Freeze the first 32 eligible distinct parent orbits | 32 distinct parent and 32 distinct bottom orbits selected | Verified complete |
| Preserve failures and prohibit backfill | Zero admitted failures and zero blocking failures; no backfill | Verified complete |
| Serialize an evaluator, dual, or transfer | Not required by this discovery protocol and not done | Not implemented by design |

The admitted run started at `2026-10-13T11:18:05.217452Z`, finished at
`2026-10-13T12:46:06.160844Z`, and records 5,280.943 seconds elapsed. It was
not resumed. All 21 frozen controls passed before the scientific shards were
accepted.

## Observed endpoint facts

Across all 42 certificates, the following fields are uniform:

- field and model: `GF(2^51)` with modulus `x^51+x^6+x^3+x+1`, curves
  `E_b: y^2+xy=x^3+b`;
- curve order: `N=2,251,799,852,369,764`;
- `D_K=-7`, `f_pi=32,756,041=271*120871`;
- source/bottom: `f_E=32,756,041`, Frobenius orbit size 51;
- target/parent: `f_E=120,871`, Frobenius orbit size 51;
- edge: degree 271, separable, defined over `GF(2^51)`, and ascending;
- certificate status: `CERTIFIED_BOTTOM_PARENT`.

The deterministic selection rule retained the first bottom child for each of
the first 32 eligible distinct parent orbits in global-index order. The 32nd
selected global rank, and therefore the frozen cutoff, is
`2,531,725,702`. The selected set has no admitted or blocking failure. The
excluded feasibility-pilot parent family contributed no scientific selection.

The planning model expected 52.5384 eligible hits, conditional on the frozen
modeled-PRP exchangeability assumption; 42 were observed. That comparison is a
descriptive sampling diagnostic. It is not an ECDLP measurement.

## Browse the evidence

- [`results/hits.csv`](results/hits.csv): all 42 aggregate sieve hits.
- [`results/records.jsonl`](results/records.jsonl): all 42 classifier records.
- [`results/pairs.jsonl`](results/pairs.jsonl): all 42 certified endpoint pairs.
- [`results/selection.json`](results/selection.json): final validated selection.
- [`results/selected-pairs.csv`](results/selected-pairs.csv): compact table of
  the first 32 frozen pairs.
- [`results/controls.json`](results/controls.json): 21/21 frozen control
  outcomes.
- [`run1.tar.zst`](run1.tar.zst): complete deterministic sealed run archive;
  see [`ARCHIVE.md`](ARCHIVE.md).

The [cumulative-yield graph](discovery-yield.svg) is drawn directly from all
42 rows in `results/hits.csv`; its editable source is
[`plot_discovery.py`](plot_discovery.py). The
[conductor-lattice diagram](conductor-lattice.svg) distinguishes the two
certified degree-271 edges from the unsupplied degree-120871 lattice
adjacencies; its editable source is
[`conductor-lattice.dot`](conductor-lattice.dot). The current printable report
is [`report.pdf`](report.pdf), built from [`report.md`](report.md).

Rebuild the derived views from this directory with:

```sh
python3 -I -S -B plot_discovery.py
dot -Tsvg conductor-lattice.dot -o conductor-lattice.svg
inkscape discovery-yield.svg --export-type=png --export-filename=discovery-yield.png --export-width=2400
inkscape conductor-lattice.svg --export-type=png --export-filename=conductor-lattice.png --export-width=2400
pandoc report.md --from=gfm --pdf-engine=xelatex -o report.pdf
```

## Claim boundary

Every scientific certificate explicitly records:

```text
map_evaluator_serialized=0
dual_serialized=0
transfer_claim_permitted=0
```

Accordingly, this run establishes endpoint-native conductor and edge facts in
the exact scan scope. It does **not** establish an executable map evaluator or
dual, subgroup transport or recovery, an ECDLP speedup, a conductor-caused
hardness difference, a weak representative, or weakness of any source curve.
The complete archive contains the per-pair certificates needed for later
replay; the compact copies deliberately do not detach those certificates from
their sealed context.
