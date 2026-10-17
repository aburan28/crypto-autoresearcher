# Exact CM discriminants of 3 more standardized curves (batch 3)

**Question.**  Batches 1 and 2
([`../endosweep_dk_exact_20261016`](../endosweep_dk_exact_20261016/README.md),
[`../endosweep_dk_exact_batch2_20261016`](../endosweep_dk_exact_batch2_20261016/README.md))
recorded the exact CM field discriminant `D_K`, the conductor `f` and the least
non-scalar endomorphism degree for the 24 curves whose `4q − t²` the factoring
driver had split completely by its second frozen snapshot (22:56Z on
2026-10-16).  The driver kept running.  Which further curves did it finish by a
third frozen snapshot, and what are their exact `D_K`, `f` and degree bound?

The answer is three curves: nums/numsp384t1, arkworks/bw6_761 and other/E-382.
This directory is batch 1's computation applied to them, by the same scripts,
run exactly as batch 2 ran them.

## Method

Everything up to the factoring driver is batch 1's, unchanged: the 10 s
screen, its survey records, the driver and its job list.  Batch 1's README,
"Method" steps 1 and 2, describes them.  `survey.py` and `jobs.json` are not
copied here; they are byte-identical (`cmp`) to
[`../endosweep_dk_exact_20261016/provenance/`](../endosweep_dk_exact_20261016/provenance/).
The driver itself was edited during the run; see "Provenance" below.

1. **A third frozen snapshot** of the driver state,
   [`provenance/driver_state.snapshot3.json`](provenance/driver_state.snapshot3.json),
   was taken at 03:22Z on 2026-10-17.  CADO-NFS was then running on E-521's
   C112.  The driver's event log up to that moment is
   [`provenance/driver_events.snapshot3.log`](provenance/driver_events.snapshot3.log).
   * Its first 67 lines are byte-identical to batch 2's
     `driver_events.snapshot2.log`.
   * Snapshot 3 has the same 43 composites as snapshot 2, and every
     snapshot-2 entry that was complete is unchanged in snapshot 3.
   * Exactly three entries went from open to complete between the snapshots.
     Those three are this batch.
2. **The survey records** of the three curves are copied verbatim from the
   10 s screen's output (`survey.jsonl`, 155 records) into
   [`provenance/survey_selected.jsonl`](provenance/survey_selected.jsonl).
3. **Certificates.**  Batch 1's
   [`make_factorizations.py`](../endosweep_dk_exact_20261016/make_factorizations.py)
   writes [`factorizations.jsonl`](factorizations.jsonl), run with `--dir`
   (this directory), `--snapshot provenance/driver_state.snapshot3.json` and
   `--exclude-certified` twice (batch 1's and batch 2's `factorizations.jsonl`).
   * It takes every complete snapshot entry except the four NIST curves and
     the 24 of batches 1 and 2.
   * It joins the survey's small primes to the primes of the composite `C`.
     On bw6_761 the survey left `C²` (a `D = −3` curve), and the exponent is
     recovered by division.
   * It reconstructs `found_by` per factor by replaying the snapshot's split
     log against the order in which the driver appended the primes.
   * Every factor is proved prime with PARI `isprime`, and the factors must
     multiply back to `4q − t²` exactly.
4. **Results.**  Batch 1's
   [`build_dk_exact.py`](../endosweep_dk_exact_20261016/build_dk_exact.py),
   run with `--dir` and the same two `--exclude-certified`, writes
   [`dk_exact.json`](dk_exact.json) and [`dk_exact.md`](dk_exact.md).
   * Each curve is reloaded from the std-curves checkout (the arkworks curves
     from `research/endosweep_curves_20261006`) and re-verified (`n` prime,
     `h·n` in the Hasse interval, a point killed by `h·n`).
   * `t = q + 1 − h·n` and `N = 4q − t²` are recomputed from the curve
     parameters.
   * `D_K` and `f` come from `nist.exact_discriminant`.  Then `t² − 4q =
     D_K·f²`, `D_K ≡ 0, 1 (mod 4)` and fundamentality are re-checked.
   * The degree is `quadorder.min_nonscalar_degree(D_K) = (|D_K| + (D_K mod
     2))/4`.
   * Where std-curves records `cm_disc` or `conductor`, both are compared.  It
     records neither for any of the three.

**One change to the batch-1 scripts.**  `build_dk_exact.py` names where each
curve comes from in a `SOURCES` table, and it had no entry for E-382, so the
builder stopped with a `KeyError`.  One line was added:
`"other/E-382": "Aranha-Barreto-Pereira-Ricardini, ePrint 2013/647"` (the
source std-curves gives).  Nothing else changed.  Batches 1 and 2 were then
regenerated with the edited scripts, by the commands in their READMEs:

* `factorizations.jsonl`, `dk_exact.json` and `dk_exact.md` of both, and
  `formal/CryptoResearch/Endosweep/DkExact.lean` and `DkExactBatch2.lean`,
  came out byte-identical (`git status` clean, and `sha256sum -c SHA256SUMS`
  passes in both directories).
* Their `report/dk_exact.svg`, redrawn into a scratch directory, matched the
  committed files except for the `<dc:date>` line and matplotlib's per-run
  random clip-path and marker ids, which match one-to-one.  The committed
  graphs, `report.typ` and `report.pdf` of batches 1 and 2 were not touched.

## Results

| curve | p bits | 4q−t² digits | factorisation of 4q−t² | f | D_K | log2 \|D_K\| | least non-scalar degree | already public? |
|:--|--:|--:|:--|--:|:--|--:|--:|:--|
| other/E-382 (= other/Curve67254) | 382 | 116 | 2² · 5 · 11 · 48109 · p41 · p69 | 2 | −(115 digits) | 381.19 | 2^379.19 | (not checked against literature) |
| nums/numsp384t1 | 384 | 117 | 2² · 5 · 13 · 29 · 18911 · 32957 · p34 · p71 | 2 | −(116 digits) | 383.97 | 2^381.97 | (not checked against literature) |
| arkworks/bw6_761 | 761 | 230 | 2² · 3 · 11² · 13827131² · p35² · p72² | 115 digits | −3 | 1.58 | 1 | `D = −3` by construction (not checked against literature) |

* `pN` is an N-digit prime.  [`dk_exact.json`](dk_exact.json) has every number
  in full, including `t`, `n`, `h`, the squarefree part `s` and `D_K`.
* On all three, `s ≡ 3 (mod 4)` and `D_K = −s`.
* The degree column is `(|D_K| + (D_K mod 2))/4`.  It is a lower bound for the
  degree of every endomorphism outside `Z`, whichever order between `Z[π]`
  and `O_K` `End(E)` is.
* [`dk_exact.md`](dk_exact.md) gives the same table with `t` and `s`, and
  names the method that found each factor.

**Already public?**  std-curves records no `cm_disc` and no `conductor` for
any of the three, so none of these `D_K` values was checked against
literature.  Their sources may publish them, as may FactorDB:

* E-382: Aranha, Barreto, Pereira, Ricardini, "A note on high-security
  general-purpose elliptic curves", ePrint 2013/647;
* numsp384t1: the NUMS paper (ePrint 2014/130) and draft-black-numscurves;
* bw6_761: the BW6-761 construction (El Housni and Guillevic) and arkworks.

On bw6_761, `D_K = −3` holds by construction (BW6 curves have `j = 0`), and
only the factorisation of the conductor is new here.

## Findings

1. **Three more curves have an exact `D_K`.**
   * On E-382 and numsp384t1, `|D_K|` is 2^381.19 and 2^383.97.
   * The gap `log2(4q) − log2 |D_K|` is 2.81 bits on E-382 and 2.03 on
     numsp384t1; 2 of those bits are `log2 f² = log2 4` on each.
   * So the least non-scalar endomorphism degree on these two is at least
     2^379.19, and neither has a small-degree endomorphism beyond the
     integers.
   * Lean proves the arithmetic of `|D_K| ≥ 2^381` and degree `≥ 2^379` on
     them (below).
2. **The conductors.**
   * `f = 2` on E-382 and numsp384t1, both Edwards-form curves with `h = 4`.
     E-382's duplicate in the corpus, other/Curve67254, has the same `p`,
     `j`, `n` and `h` (the builder's duplicate key), so it is the same curve
     up to isomorphism, with the same `t`.
   * On bw6_761, `f` has 115 digits: `4q − t² = 3·f²`.
3. **Who found each factor.**  The per-factor list is in
   [`dk_exact.md`](dk_exact.md); it is reconstructed from the snapshot-3 split
   log.
   * CADO-NFS 3.0.0 (git `692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b`, run as
     `nice -n 5 python3 cado-nfs.py C -t 4 -w WORKDIR`) made the one split on
     each of the three, in wall-clock time:

     | curve | composite | split | wall | event log |
     |:--|--:|:--|--:|:--|
     | numsp384t1 | C104 | p34 · p71 | 2138 s | 22:55:42Z → 23:31:20Z |
     | bw6_761 | C106 (squared in `4q − t²`) | p35 · p72 | 2845 s | 23:31:20Z → 00:18:45Z |
     | E-382 | C109 | p41 · p69 | 3059 s | 00:22:26Z → 01:13:25Z |
   * On E-382 the log shows CADO-NFS starting at 00:18:45Z and starting again
     at 00:22:26Z, resuming from CADO's `c110.parameters_snapshot.0`.  The log
     does not say why.  The 3059 s is the resumed run only; the first start
     to the split is 3280 s.
   * No ECM tier found a factor of these three composites.  Every other
     factor came from the survey's `PARI factor(N, 2^32)`.
   * The wall times are those of one run on a shared 4-core machine. They
     are not measurements of how hard any number is.
4. **Excluded:**
   * P-256, P-384, P-521 and Curve25519, certified in
     `../endosweep_nist_20261006`, and the 24 curves of batches 1 and 2 are
     complete in snapshot 3 too.  They are not repeated.
   * 12 snapshot-3 entries still had an open composite, so they are not in
     this directory: numsp384d1, Curve41417, w-510-mont, ed-510-mont,
     ed-512-mont, brainpoolP512r1, numsp512d1, ed-511-mers, M-511, gost512,
     E-521 (CADO-NFS running on its C112) and ed_on_mnt4_753.

## Provenance

* The driver's state file was briefly truncated on disk at about 02:22Z on
  2026-10-17, when the disk filled.  It was rewritten from the driver's
  in-memory state before snapshot 3 was taken.  Nothing here relies on that
  file being right: every factor of the three certificates is re-proved prime
  by PARI `isprime` here, and the factors must multiply back exactly to
  `4q − t²` recomputed from the curve parameters, or the script stops.
* At 02:22:37Z the log shows CADO-NFS failing (rc = 1) on E-521's C112,
  numsp384d1's C117 and Curve41417's C121.  None of those is in this batch.
* The driver script was edited at about 03:05Z and restarted at 03:10Z (the
  last two log lines).  The edit made `save()` fsync the state and re-read it
  before replacing the old file, and made the driver delete a CADO work
  directory after a successful split.  The open entries in snapshot 3 carry a
  new `ecm_done` field.  The three splits of this batch, and the split-log
  lines they are reconstructed from, predate the edit.
* The snapshot and log are copies of `state.snapshot3.json` and
  `events.snapshot3.log`, taken from the driver's working directory; the live
  state file was not read.

## Scope

* These are exact integer facts about `t² − 4q`, plus the standard theory
  that `End(E)` is an order of `Q(√D_K)` containing `Z[π]`, whose
  non-scalar elements have norm at least `(|D_K| + (D_K mod 2))/4`.
* No attack, speed-up or weakness is claimed.  A large `|D_K|` rules out a
  small-degree endomorphism and nothing else.  On bw6_761 `D_K = −3` is the
  known `j = 0` CM.
* Primality is PARI `isprime`, which is a proof.  Lean re-proves only the
  factors below 10^8 (below).

## Files

| file | what |
|:--|:--|
| `factorizations.jsonl` | the 3 complete factorisation certificates of `4q − t²`, in batch 1's schema (`found_by` a per-factor list, `seconds` null) |
| `dk_exact.json` | per curve: `p`, `n`, `h`, `t`, `4q − t²`, factorisation, `found_by`, squarefree part, `f`, `D_K`, log2, least non-scalar degree, source, std-curves check; and the 28 excluded curves with the file that certifies each |
| `dk_exact.md` | the generated table, with who found each factor |
| `provenance/` | the third frozen driver snapshot, its event log, and the three survey records |
| `report/` | `report.typ`, the graph `dk_exact.svg` (drawn by batch 1's `plot_dk.py`) and `report.pdf` |
| `SHA256SUMS` | hashes of the data files |

The scripts are batch 1's, in
[`../endosweep_dk_exact_20261016/`](../endosweep_dk_exact_20261016/).

## Regenerating

From the repository root, with `STD_CURVES_CHECKOUT` J08nY/std-curves at commit
`77fe6e3585ca2c2225b59d7df24b7c775437276f`:

```sh
B1=research/endosweep_dk_exact_20261016
B2=research/endosweep_dk_exact_batch2_20261016
B3=research/endosweep_dk_exact_batch3_20261017
# The certificates, from the copied survey records and the third frozen snapshot:
nice -n 10 python3 $B1/make_factorizations.py STD_CURVES_CHECKOUT research/endosweep_curves_20261006 \
    --dir $B3 --snapshot provenance/driver_state.snapshot3.json \
    --exclude-certified $B1/factorizations.jsonl --exclude-certified $B2/factorizations.jsonl
# The results:
nice -n 10 python3 $B1/build_dk_exact.py STD_CURVES_CHECKOUT research/endosweep_curves_20261006 \
    --dir $B3 --exclude-certified $B1/factorizations.jsonl --exclude-certified $B2/factorizations.jsonl
# The Lean file:
python3 $B1/lean/gen_dk_exact_lean.py . --dir $B3 --module DkExactBatch3 \
    --target formal/targets/endosweep-dk-exact-batch3-discriminants.yaml
# The graph and the PDF (matplotlib and the typst wheel):
python3 $B1/report/plot_dk.py $B3/report
python3 -c "import typst; typst.compile('$B3/report/report.typ', \
    output='$B3/report/report.pdf', root='$B3')"
# Checks:
(cd $B3 && sha256sum -c SHA256SUMS)
python3 -m pytest -q tests/test_endosweep_dk_exact_batch3.py
```

## Lean verification

`formal/CryptoResearch/Endosweep/DkExactBatch3.lean` is generated by batch
1's `lean/gen_dk_exact_lean.py` with `--module DkExactBatch3`.  The generator
was not changed for this batch.

* **What it imports and reuses.** It imports `CryptoResearch.Endosweep.DkExact`
  and reuses its `DkCert`, `DkCert.Statement` and `DkCert.statement_of_holds`,
  and through them NistCertificates' `FactoredCert`, `noDivBelow` and its 10^8
  threshold.  It defines none of them again and has only data and proofs.
  It is core Lean, with no Mathlib.
* **Its target.** The frozen target spec is
  `formal/targets/endosweep-dk-exact-batch3-discriminants.yaml`
  (`TASK-20261017-9c045d`).  The id was checked for collisions in the whole tree at
  `HEAD`, and in `formal/targets` and `coordination` on every remote branch
  tip.
* **Its namespace** is `CryptoResearch.Endosweep.DkExactBatch3`.

Per curve, `<curve>_holds` is closed arithmetic checked by `decide +kernel`.
`<curve>_certificate : <curve>.Statement` states the same propositions as in
batches 1 and 2:

* `q + 1 − t = h·n`, and `t² − 4q = D_K·f²`;
* the factorisation multiplies back;
* the squarefree part and the construction of `D_K` from it;
* `IsDisc D_K`, and the recorded degree;
* `2^L ≤ |D_K| < 2^(L+1)`, and the degree is at least `2^(L−2)`;
* if the listed factors above 10^8 are prime, `D_K` is fundamental.

The theorems are `other_E_382_certificate`, `nums_numsp384t1_certificate`
and `arkworks_bw6_761_certificate`.

**`DkExactBatch3.exact_discriminants`** collects all three certificates, plus:

* `D_K = −3` on bw6_761;
* on E-382 and numsp384t1, `|D_K| ≥ 2^381` and
  `min_nonscalar_degree(D_K) ≥ 2^379`.

**The primality hypothesis.** As in `DkExact`, the factors above 10^8 are an
explicit hypothesis: Lean does not prove them prime. PARI `isprime` proved
them.  Factors below 10^8 are proved prime in Lean by trial division.

**Not certified:**

* the primality of `p` and `n`;
* that `t` is the trace of Frobenius of the named curve;
* any elliptic-curve fact;
* which order `End(E)` is.

**Checked locally** with Lean 4 (`leanprover/lean4:v4.35.0-rc1`,
`formal/lean-toolchain`), using `lean -o` on `Discriminant.lean`,
`NistCertificates.lean`, `DkExact.lean`, `DkExactBatch2.lean` and
`DkExactBatch3.lean` in order:

* all five compile;
* `#print axioms` gives `[propext, Classical.choice, Quot.sound]` on
  `exact_discriminants`, on the three certificates and on
  `DkExact.DkCert.statement_of_holds`;
* the file has no `sorry`, `admit`, `axiom`, `unsafe` or `native_decide`.

**Negative controls.** Two edited copies were compiled, and the kernel
rejected both: `decide` proved `other_E_382.Holds` and
`arkworks_bw6_761.Holds` false.

* In the first, one digit of E-382's p41 was changed in its factor list.
* In the second, one digit of bw6_761's `n` was changed.
