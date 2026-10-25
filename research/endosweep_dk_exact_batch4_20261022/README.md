# Exact CM discriminants of 7 more standardized curves (batch 4)

**Question.**  Batches 1 to 3
([`../endosweep_dk_exact_20261016`](../endosweep_dk_exact_20261016/README.md),
[`../endosweep_dk_exact_batch2_20261016`](../endosweep_dk_exact_batch2_20261016/README.md),
[`../endosweep_dk_exact_batch3_20261017`](../endosweep_dk_exact_batch3_20261017/README.md))
recorded the exact CM field discriminant `D_K`, the conductor `f` and the least
non-scalar endomorphism degree for the 27 curves whose `4q − t²` the factoring
driver had split completely by its third frozen snapshot (03:22Z on
2026-10-17).  The driver kept running.  Which further curves did it finish by a
fourth frozen snapshot, and what are their exact `D_K`, `f` and degree bound?

The answer is seven curves: nums/numsp384d1, other/Curve41417,
nums/ed-510-mont, nums/numsp512d1, other/M-511, other/E-521 and
arkworks/ed_on_mnt4_753.  This directory is batch 1's computation applied to
them, by the same scripts, run exactly as batch 3 ran them.

## Method

Everything up to the factoring driver is batch 1's, unchanged: the 10 s
screen, its survey records, the driver and its job list.  Batch 1's README,
"Method" steps 1 and 2, describes them.  The driver itself was edited during
the run; see "Provenance" below.

1. **A fourth frozen snapshot** of the driver state,
   [`provenance/driver_state.snapshot4.json`](provenance/driver_state.snapshot4.json),
   was taken at 03:26Z on 2026-10-22, while ECM at B1 = 3·10^6 was running on
   the five composites still open.  The driver's event log up to that moment is
   [`provenance/driver_events.snapshot4.log`](provenance/driver_events.snapshot4.log).
   * Its first 85 lines are byte-identical to batch 3's
     `driver_events.snapshot3.log`.
   * Snapshot 4 has the same 43 composites as snapshot 3, and every
     snapshot-3 entry that was complete is unchanged in snapshot 4.
   * Exactly seven entries went from open to complete between the snapshots.
     Those seven are this batch.
2. **The survey records** of the seven curves are copied verbatim, in survey
   order, from the 10 s screen's output (`survey.jsonl`, 155 records) into
   [`provenance/survey_selected.jsonl`](provenance/survey_selected.jsonl).
3. **Certificates.**  Batch 1's
   [`make_factorizations.py`](../endosweep_dk_exact_20261016/make_factorizations.py)
   writes [`factorizations.jsonl`](factorizations.jsonl), run with `--dir`
   (this directory), `--snapshot provenance/driver_state.snapshot4.json` and
   `--exclude-certified` three times (the `factorizations.jsonl` of batches 1,
   2 and 3).
   * It joins the survey's small primes to the primes of the composite `C`.
   * It reconstructs `found_by` per factor by replaying the snapshot's split
     log against the order in which the driver appended the primes.
   * Every factor is proved prime with PARI `isprime`, and the factors must
     multiply back to `4q − t²` exactly.
4. **Results.**  Batch 1's
   [`build_dk_exact.py`](../endosweep_dk_exact_20261016/build_dk_exact.py),
   run with `--dir` and the same three `--exclude-certified`, writes
   [`dk_exact.json`](dk_exact.json) and [`dk_exact.md`](dk_exact.md).
   * Each curve is reloaded from the std-curves checkout (ed_on_mnt4_753 from
     `research/endosweep_curves_20261006`) and re-verified (`n` prime, `h·n` in
     the Hasse interval, a point killed by `h·n`).
   * `t = q + 1 − h·n` and `N = 4q − t²` are recomputed from the curve
     parameters; `D_K` and `f` come from `nist.exact_discriminant` and are
     re-checked (`t² − 4q = D_K·f²`, `D_K ≡ 0, 1 (mod 4)`, fundamentality).
   * The degree is `(|D_K| + (D_K mod 2))/4`.
   * Where std-curves records `cm_disc` or `conductor`, both are compared.  It
     records neither for any of the seven.

**Changes to the batch-1 scripts.**  Two were data lines, two were not.

* `make_factorizations.py` maps each ECM B1 to its driver tier, and had no
  entry for B1 = 3·10^6 (tier 5), which found the last factors of ed-510-mont
  and M-511.  One entry was added: `"3000000": 5`.
* `build_dk_exact.py`'s `SOURCES` table had no entry for Curve41417, M-511 or
  E-521.  Three lines were added: M-511 and E-521 as Aranha-Barreto-Pereira-
  Ricardini, ePrint 2013/647 (the source std-curves gives), and Curve41417 as
  Bernstein-Chuengsatiansup-Lange, CHES 2014 (std-curves cites the
  cr.yp.to/talks/2013.09.16 slides).
* **A code change, not a data line:** `lean/gen_dk_exact_lean.py` assumed at
  least one curve with a small `D_K` (every earlier batch had one).  With none
  it wrote `() ∧` into the statement of `exact_discriminants`, which does not
  compile.  The change, guarded by `if small`, leaves out that conjunct and its
  `decide`, and words the docstring "Moreover, on all 7 curves …".  When a
  batch has a small `D_K` the output is unchanged.
* **A code change, not a data line:** `report/plot_dk.py` wrote "Not shown: ."
  under the graph when no curve was left out.  The note is now written only
  when a curve is left out; otherwise the text is unchanged.

Batches 1, 2 and 3 were regenerated with the edited scripts, by the commands
in their READMEs:

* `factorizations.jsonl`, `dk_exact.json` and `dk_exact.md` of all three, and
  `DkExact.lean`, `DkExactBatch2.lean` and `DkExactBatch3.lean`, came out
  byte-identical (`git status` clean; `sha256sum -c SHA256SUMS` passes in all
  three directories).
* Their `report/dk_exact.svg`, redrawn into a scratch directory, matched the
  committed files except for the `<dc:date>` line and matplotlib's per-run
  random clip-path and marker ids, which match one-to-one.  The committed
  graphs, `report.typ` and `report.pdf` of batches 1 to 3 were not touched.

## Results

| curve | p bits | 4q−t² digits | factorisation of 4q−t² | f | D_K | log2 \|D_K\| | least non-scalar degree | already public? |
|:--|--:|--:|:--|--:|:--|--:|--:|:--|
| nums/numsp384d1 | 384 | 117 | p50 · p67 | 1 | −(117 digits) | 385.99 | 2^383.99 | (not checked against literature) |
| other/Curve41417 | 414 | 125 | 2² · 3607 · p53 · p69 | 2 | −(125 digits) | 413.21 | 2^411.21 | (not checked against literature) |
| nums/ed-510-mont | 510 | 154 | 2² · 154799 · p40 · p109 | 2 | −(154 digits) | 509.23 | 2^507.23 | (not checked against literature) |
| other/M-511 | 511 | 155 | 2⁴ · 7 · p14 · p39 · p101 | 2 | −(154 digits) | 510.54 | 2^508.54 | (not checked against literature) |
| nums/numsp512d1 | 512 | 155 | 29 · 43 · p33 · p119 | 1 | −(155 digits) | 513.84 | 2^511.84 | (not checked against literature) |
| other/E-521 | 521 | 158 | 2² · 47 · 23658857317 · p34 · p53 · p59 | 2 | −(157 digits) | 520.90 | 2^518.90 | (not checked against literature) |
| arkworks/ed_on_mnt4_753 | 753 | 228 | 2⁵ · 751 · p21 · p25 · p30 · p149 | 2 | −(227 digits) | 752.82 | 2^750.82 | (not checked against literature) |

* `pN` is an N-digit prime.  [`dk_exact.json`](dk_exact.json) has every number
  in full, including `t`, `n`, `h`, the squarefree part `s` and `D_K`.
* `D_K = −s` (`s ≡ 3 mod 4`) on five curves; `D_K = −4s` on M-511 and
  ed_on_mnt4_753.
* The degree column is `(|D_K| + (D_K mod 2))/4`.  It is a lower bound for the
  degree of every endomorphism outside `Z`, whichever order between `Z[π]`
  and `O_K` `End(E)` is.
* [`dk_exact.md`](dk_exact.md) gives the same table with `t` and `s`, and
  names the method that found each factor.

**Already public?**  std-curves records no `cm_disc` and no `conductor` for
any of the seven, so none of these `D_K` values was checked against
literature.  Their sources may publish them, as may FactorDB: the NUMS paper (ePrint 2014/130) for numsp384d1, numsp512d1 and
ed-510-mont; ePrint 2013/647 for M-511 and E-521; the Curve41417 paper; and
arkworks for ed_on_mnt4_753.

## Findings

1. **Seven more curves have an exact `D_K`.**
   * `|D_K|` ranges from 2^385.99 (numsp384d1) to 2^752.82 (ed_on_mnt4_753),
     so every non-scalar endomorphism has degree at least 2^383.
   * The gap `log2(4q) − log2 |D_K|` is 0.01 bits on numsp384d1 and 0.16 on
     numsp512d1 (`f = 1`, `h = 1`), and 2.0 to 2.79 bits on the five curves
     with `f = 2`, of which 2 bits are `log2 f²`.
   * Lean proves the arithmetic of `|D_K| ≥ 2^385` and degree `≥ 2^383` on all
     seven (below).
2. **The conductors.**  `f = 1` on numsp384d1 and numsp512d1 (prime-order
   Weierstrass curves); `f = 2` on the other five (cofactor 4 or 8).
3. **Who found the factors.**  The per-factor list is in
   [`dk_exact.md`](dk_exact.md), reconstructed from the snapshot-4 split log.
   * Three curves were finished by CADO-NFS 3.0.0 (git
     `692ecb7e62f0f3bdab88ee44cc60b8ded0ea1a1b`, run as `nice -n 5 python3
     cado-nfs.py C -t 4 -w WORKDIR`).  The time in `dk_exact.md` is the one the
     driver logged, which is that of the last (resumed) run only:

     | curve | composite | split | logged wall | first start → split (event log) |
     |:--|--:|:--|--:|:--|
     | E-521 | C112 | p53 · p59 | 1179 s | 01:13:25Z → 03:30:12Z (8207 s; failed rc = 1 at 02:22:37Z, resumed 03:10:33Z) |
     | numsp384d1 | C117 | p50 · p67 | 4994 s | 03:30:13Z → 06:33:54Z (11021 s; resumed 05:10:40Z; an earlier attempt failed at 02:22:37Z) |
     | Curve41417 | C121 | p53 · p69 | 1463 s | 06:33:55Z → 11:36:02Z (18127 s; resumed 07:10:49Z, 09:10:58Z, 11:11:09Z, 11:11:39Z) |
   * Four curves were finished by GMP-ECM 7.0.5; the raw factor of each is in
     the event log:

     | curve | composite | factor found | B1 (driver tier) | event log |
     |:--|--:|:--|:--|:--|
     | ed_on_mnt4_753 | C179 | p30 (cofactor p149) | 10^6 (4) | 12:32:02Z |
     | numsp512d1 | C152 | p33 (cofactor p119) | 10^6 (4) | 12:38:20Z |
     | ed-510-mont | C149 | p40 (cofactor p109) | 3·10^6 (5) | 15:51:50Z |
     | M-511 | C139 | p39 (cofactor p101) | 3·10^6 (5) | 16:05:18Z |
   * Earlier ECM tiers found M-511's p14 (B1 = 11000), E-521's 23658857317
     (B1 = 11000) and p34 (B1 = 250000), and ed_on_mnt4_753's p21
     (B1 = 50000) and p25 (B1 = 250000); these lines predate snapshot 3.
     Every other factor came from the survey's `PARI factor(N, 2^32)`.
   * The times are those of one run on a shared 4-core machine. They are not
     measurements of how hard any number is.
4. **Excluded:**
   * P-256, P-384, P-521 and Curve25519 (`../endosweep_nist_20261006`) and the
     27 curves of batches 1 to 3 are complete in snapshot 4 too.  They are not
     repeated.
   * 5 snapshot-4 entries still have an open composite: w-510-mont (C146),
     ed-512-mont (C151), brainpoolP512r1 (C152), ed-511-mers (C133) and gost512
     (C144).

## Provenance

What the files here show about the run, checked against them:

* **The crash of 2026-10-17, about 11:36Z.**  The event log has no line for
  the crash itself.  After Curve41417's CADO split (11:36:02Z) it shows the
  ECM tier B1 = 10^6 starting on 9 composites at 11:36:05Z, and then the same
  tier starting again on the same 9 composites at 12:29:03Z, with no factor
  logged in between.  The driver's console output (not copied here) ends the
  11:36 run with a traceback in which `split()` calls `isprime()` from inside
  the ECM thread pool (`ex.map(one, todo)`) and cypari2 raises
  `SignalError: Segmentation fault`.
* **The bad state.**  The state saved at that point is kept as
  [`provenance/driver_state.precrashfix.json`](provenance/driver_state.precrashfix.json).
  In it, exactly two of the 43 entries do not multiply back to their
  composite: numsp512d1 and ed_on_mnt4_753.  Each is marked complete
  (`open == []`) and its log already ends with the split of the interrupted
  run (`ECM B1=1000000: 152-digit -> 33 x 119` and `179-digit -> 30 x 149`),
  but neither part of that split is in `primes`: numsp512d1 has no primes at
  all, and ed_on_mnt4_753 has only its p21 and p25.  So both the ECM factor
  and its cofactor were missing, and the product was not `N`.
* **The restoration.**  In snapshot 4 both entries are their snapshot-3 entry
  (same `primes` prefix, same log prefix) plus that one ECM split, and their
  log list equals the bad state's.  The event log shows the driver finding
  both factors again after the 12:29:03Z restart, each with a `raw factor`
  line before the `found` line:
  `arkworks/ed_on_mnt4_753: ECM B1=1000000 raw factor 587822677040096842506003367703 of C179`
  (12:32:02Z) and
  `nums/numsp512d1: ECM B1=1000000 raw factor 636022186443411851910975284226071 of C152`
  (12:38:20Z).  Both raw factors are in this batch's certificates.  The files
  do not themselves record that the restore was done from snapshot 3; that is
  the operator's account, and it is consistent with everything above.
* **The fix.**  The driver now running (not copied here) keeps PARI and all
  state changes in the main thread (the threads only run the `ecm`
  subprocess), logs the raw factor before splitting, and `save()` asserts that
  every entry multiplies back to its composite before writing.  The event log
  shows another restart of the B1 = 3·10^6 tier at 14:29:28Z, after the
  driver file was edited again; no factor of this batch depends on what that
  edit changed (ed-510-mont's and M-511's factors are re-proved below like all
  others).
* **The idle period.**  The event log has no line between 2026-10-17T18:04:20Z
  (a progress line) and 2026-10-22T02:42:24Z, when the B1 = 3·10^6 tier
  restarts on the 5 remaining composites.  By the operator's account the
  driver was idle from about 18:29Z (the log cannot show the exact time).  The last factor of this batch was logged at 16:05:18Z on
  2026-10-17, so the gap affects none of them.
* **None of this is relied on.**  Every factor of the seven certificates is
  re-proved prime by PARI `isprime` here, and the factors must multiply back
  exactly to `4q − t²` recomputed from the curve parameters, or the scripts
  stop.  `tests/test_endosweep_dk_exact_batch4.py` re-checks the crash and
  restoration facts above from the three state files and the log.
* The snapshot, the log and the bad state are copies of `state.snapshot4.json`,
  `events.snapshot4.log` and `state.precrashfix.json` from the driver's working
  directory; the live state file was not read.

## Scope

* These are exact integer facts about `t² − 4q`, plus the standard theory
  that `End(E)` is an order of `Q(√D_K)` containing `Z[π]`, whose non-scalar
  elements have norm at least `(|D_K| + (D_K mod 2))/4`.
* No attack, speed-up or weakness is claimed.  A large `|D_K|` rules out a
  small-degree endomorphism and nothing else.
* Primality is PARI `isprime`, which is a proof.  Lean re-proves only the
  factors below 10^8 (below).

## Files

| file | what |
|:--|:--|
| `factorizations.jsonl` | the 7 complete factorisation certificates of `4q − t²`, in batch 1's schema (`found_by` a per-factor list, `seconds` null) |
| `dk_exact.json` | per curve: `p`, `n`, `h`, `t`, `4q − t²`, factorisation, `found_by`, squarefree part, `f`, `D_K`, log2, least non-scalar degree, source, std-curves check; and the 31 excluded curves with the file that certifies each |
| `dk_exact.md` | the generated table, with who found each factor |
| `provenance/` | the fourth frozen driver snapshot, its event log, the bad pre-fix state, and the seven survey records |
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
B4=research/endosweep_dk_exact_batch4_20261022
# The certificates, from the copied survey records and the fourth frozen snapshot:
nice -n 10 python3 $B1/make_factorizations.py STD_CURVES_CHECKOUT research/endosweep_curves_20261006 \
    --dir $B4 --snapshot provenance/driver_state.snapshot4.json \
    --exclude-certified $B1/factorizations.jsonl --exclude-certified $B2/factorizations.jsonl \
    --exclude-certified $B3/factorizations.jsonl
# The results:
nice -n 10 python3 $B1/build_dk_exact.py STD_CURVES_CHECKOUT research/endosweep_curves_20261006 \
    --dir $B4 --exclude-certified $B1/factorizations.jsonl --exclude-certified $B2/factorizations.jsonl \
    --exclude-certified $B3/factorizations.jsonl
# The Lean file:
python3 $B1/lean/gen_dk_exact_lean.py . --dir $B4 --module DkExactBatch4 \
    --target formal/targets/endosweep-dk-exact-batch4-discriminants.yaml
# The graph and the PDF (matplotlib and the typst wheel):
python3 $B1/report/plot_dk.py $B4/report
python3 -c "import typst; typst.compile('$B4/report/report.typ', \
    output='$B4/report/report.pdf', root='$B4')"
# Checks:
(cd $B4 && sha256sum -c SHA256SUMS)
python3 -m pytest -q tests/test_endosweep_dk_exact_batch4.py
```

## Lean verification

`formal/CryptoResearch/Endosweep/DkExactBatch4.lean` is generated by batch
1's `lean/gen_dk_exact_lean.py` with `--module DkExactBatch4`, after the
no-small-`D_K` change described under "Method".

* **What it imports and reuses.** It imports `CryptoResearch.Endosweep.DkExact`
  and reuses its `DkCert`, `DkCert.Statement` and `DkCert.statement_of_holds`,
  and through them NistCertificates' `FactoredCert`, `noDivBelow` and its 10^8
  threshold.  It defines none of them again and has only data and proofs.
  It is core Lean, with no Mathlib.
* **Its target.** The frozen target spec is
  `formal/targets/endosweep-dk-exact-batch4-discriminants.yaml`
  (`TASK-20261022-ff60b1`).  The id was checked for collisions in the whole
  tree at `HEAD`, and in `formal/targets` and `coordination` on every remote
  branch tip.
* **Its namespace** is `CryptoResearch.Endosweep.DkExactBatch4`.

Per curve, `<curve>_holds` is closed arithmetic checked by `decide +kernel`.
`<curve>_certificate : <curve>.Statement` states the same propositions as in
batches 1 to 3:

* `q + 1 − t = h·n`, and `t² − 4q = D_K·f²`;
* the factorisation multiplies back;
* the squarefree part and the construction of `D_K` from it;
* `IsDisc D_K`, and the recorded degree;
* `2^L ≤ |D_K| < 2^(L+1)`, and the degree is at least `2^(L−2)`;
* if the listed factors above 10^8 are prime, `D_K` is fundamental.

The theorems are `nums_numsp384d1_certificate`,
`other_Curve41417_certificate`, `nums_ed_510_mont_certificate`,
`other_M_511_certificate`, `nums_numsp512d1_certificate`,
`other_E_521_certificate` and `arkworks_ed_on_mnt4_753_certificate`.

**`DkExactBatch4.exact_discriminants`** collects all seven certificates, plus,
on all seven, `|D_K| ≥ 2^385` and `min_nonscalar_degree(D_K) ≥ 2^383`.

**The primality hypothesis.** As in `DkExact`, the factors above 10^8 are an
explicit hypothesis: Lean does not prove them prime. PARI `isprime` proved
them.  Factors below 10^8 (3607, 154799, 7, 29, 43, 47, 751) are proved prime
in Lean by trial division.

**Not certified:**

* the primality of `p` and `n`;
* that `t` is the trace of Frobenius of the named curve;
* any elliptic-curve fact;
* which order `End(E)` is.

**Checked locally** with Lean 4 (`leanprover/lean4:v4.35.0-rc1`,
`formal/lean-toolchain`), using `lean -o` on `Discriminant.lean`,
`NistCertificates.lean`, `DkExact.lean`, `DkExactBatch2.lean`,
`DkExactBatch3.lean` and `DkExactBatch4.lean` in order:

* all six compile;
* `#print axioms` gives `[propext, Classical.choice, Quot.sound]` on
  `exact_discriminants`, on the seven certificates and on
  `DkExact.DkCert.statement_of_holds`;
* the file has no `sorry`, `admit`, `axiom`, `unsafe` or `native_decide`.

**Negative controls.** Two edited copies were compiled, and the kernel
rejected both: `decide` proved `arkworks_ed_on_mnt4_753.Holds` and
`other_E_521.Holds` false.

* In the first, one digit of ed_on_mnt4_753's p30 was changed in its factor
  list.
* In the second, one digit of E-521's `n` was changed.
