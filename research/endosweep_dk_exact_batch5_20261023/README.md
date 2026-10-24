# Exact CM discriminant of gost512 (batch 5), and the four composites still open

**Question.**  Batches 1 to 4
([`../endosweep_dk_exact_20261016`](../endosweep_dk_exact_20261016/README.md),
[`../endosweep_dk_exact_batch2_20261016`](../endosweep_dk_exact_batch2_20261016/README.md),
[`../endosweep_dk_exact_batch3_20261017`](../endosweep_dk_exact_batch3_20261017/README.md),
[`../endosweep_dk_exact_batch4_20261022`](../endosweep_dk_exact_batch4_20261022/README.md))
recorded the exact CM field discriminant `D_K`, the conductor `f` and the least
non-scalar endomorphism degree for the 34 curves whose `4q − t²` was split
completely by the fourth frozen driver snapshot (03:26Z on 2026-10-22).  This
directory answers two questions:

* **Part A.** Which curve was completed by the fifth frozen snapshot, and what
  are its exact `D_K`, `f` and degree bound?
* **Part B.** For the four `4q − t²` still open, what is known and how much
  ECM has been spent on them?

**Answers.**

* **Part A.** One curve was completed: gost/gost512.  Its `4q − t²` is
  `19870558523 · p71 · p74`, so `f = 1` and `D_K = −(4q − t²)` (155 digits,
  log2 |D_K| = 512.00).  **The last split, of the 144-digit cofactor into p71
  and p74, was not found by this project.**  It was fetched from FactorDB
  (see "Provenance").
* **Part B.** Four curves are still open:

  | curve | open cofactor |
  |:--|--:|
  | nums/ed-511-mers | C133 |
  | nums/w-510-mont | C146 |
  | nums/ed-512-mont | C151 |
  | brainpool/brainpoolP512r1 | C152 |

  Each has had all ECM tiers up to B1 = 3·10^6, and 1500 or 1600 of the 4480
  curves at B1 = 11·10^6.  FactorDB lists all four as composite with no known
  factor.

## Part A: method

This is batch 4's process, by the same scripts, run as batch 4 ran them.

1. **A fifth frozen snapshot** of the driver state,
   [`provenance/driver_state.snapshot5.json`](provenance/driver_state.snapshot5.json),
   was taken at 00:12Z on 2026-10-23.
   * By then the driver had stopped ECM and was running CADO-NFS on
     ed-511-mers' C133.  The live `state.json` was byte-identical to the
     snapshot when it was copied.
   * The event log up to that moment is
     [`provenance/driver_events.snapshot5.log`](provenance/driver_events.snapshot5.log).
     Its first 121 lines are byte-identical to batch 4's
     `driver_events.snapshot4.log`.
   * Snapshot 5 has the same 43 composites as snapshot 4.  Every snapshot-4
     entry that was complete is unchanged in snapshot 5.
   * Exactly one entry went from open to complete between the two snapshots:
     gost/gost512.
2. **The survey record** of gost512 is copied verbatim from the 10 s screen's
   `survey.jsonl` into
   [`provenance/survey_selected.jsonl`](provenance/survey_selected.jsonl).  The
   survey found no small prime: its composite is the whole 155-digit `4q − t²`.
3. **Certificates.**  Batch 1's
   [`make_factorizations.py`](../endosweep_dk_exact_20261016/make_factorizations.py)
   writes [`factorizations.jsonl`](factorizations.jsonl).
   * It runs with `--snapshot provenance/driver_state.snapshot5.json` and
     `--exclude-certified` four times, once for each earlier batch.
   * `found_by` is replayed from the snapshot's split log.
   * Every factor is proved prime by PARI `isprime`, and the factors must
     multiply back to `4q − t²`.
4. **Results.**  Batch 1's
   [`build_dk_exact.py`](../endosweep_dk_exact_20261016/build_dk_exact.py)
   writes [`dk_exact.json`](dk_exact.json) and [`dk_exact.md`](dk_exact.md).
   * The curve is reloaded from std-curves and verified again.
   * `t = q + 1 − h·n` and `N = 4q − t²` are recomputed from the curve
     parameters.
   * `D_K` and `f` come from `nist.exact_discriminant` and are checked again.
   * std-curves records no `cm_disc` and no `conductor` for gost512, so `D_K`
     was not checked against literature.

**Changes to the batch-1 scripts.**  One was a data line and three were not.
Each was rerun on batches 1 to 4 afterwards (see the end of this section).

* **Data line:** `build_dk_exact.py`'s `SOURCES` table mapped every `gost/…`
  curve to "TC26 GOST R 34.10-2012 parameter set C", which is wrong for
  gost512.  One line was added: `gost/gost512` is GOST R 34.10-2001, RFC 5832,
  which is the source std-curves gives.
* **Code change:** `make_factorizations.py`'s `method()` had no case for the
  split-log line the driver writes for the FactorDB split,
  `FactorDB (fetched 2026-10-22T23:04:32.541251Z): 144-digit -> 71 x 74`, and
  stopped there.
  * A three-line branch maps it to
    `FactorDB (external; finder not recorded; fetched <timestamp>)`.
  * It does not attribute the split to ECM or CADO.
  * No earlier log contains such a line.
* **Code change:** `lean/gen_dk_exact_lean.py` wrote "The 1 curves" and "on all
  1 curves" for a one-curve batch.  Both phrases now use the singular when
  there is exactly one curve.  Otherwise the text is unchanged.
* **Code change:** `report/plot_dk.py` wrote "n = 1 curves" under the graph.
  It now uses the singular for one curve and is otherwise unchanged.
* The generator needed no other change: a one-element `dkCerts` with
  `rcases hc with rfl` compiles.

Batches 1 to 4 were regenerated with the edited scripts, by the commands in
their READMEs:

* Their `factorizations.jsonl`, `dk_exact.json` and `dk_exact.md`, and
  `DkExact.lean` and `DkExactBatch2.lean` to `DkExactBatch4.lean`, came out
  byte-identical (`git status` clean, and `sha256sum -c SHA256SUMS` passes in
  all four directories).
* Their `report/dk_exact.svg` was redrawn into a scratch directory.  It matched
  the committed file once the `<dc:date>` line was removed and matplotlib's
  per-run random element ids were mapped one-to-one.
* The committed records of batches 1 to 4 were not touched.

## Part A: result

| curve | p bits | 4q−t² digits | factorisation of 4q−t² | f | D_K | log2 \|D_K\| | least non-scalar degree | already public? |
|:--|--:|--:|:--|--:|:--|--:|--:|:--|
| gost/gost512 | 511 | 155 | 19870558523 · p71 · p74 | 1 | −(155 digits) | 512.00 (511.998) | 2^510.00 | (not checked against literature) |

* For the recorded integers, `h = 1`, and `4q − t²` is squarefree with
  `4q − t² ≡ 3 (mod 4)`. Thus `D_K = −s = t² − 4q` and `f = 1`.
  Identifying this discriminant with the endomorphism ring of the named
  curve requires that `q` is its prime field size, `t` is its actual
  Frobenius trace, and the listed large factors are prime. Under those
  hypotheses and the standard ordinary-curve order theorem, `End(E) = O_K`.
  The Lean target below does not prove that curve-model bridge or primality.
* The gap `log2(4q) − log2 |D_K|` is 0.11 bits.
* `|D_K| ≥ 2^511`, and the abstract quadratic-order model has minimum
  non-scalar norm at least 2^509 (Lean, below). Applying this as an
  endomorphism degree bound for the named curve needs the curve-model bridge.
* [`dk_exact.json`](dk_exact.json) has every number in full.

**Who found the factors** (from [`dk_exact.md`](dk_exact.md)):

| factor | found by | where it is recorded |
|:--|:--|:--|
| 19870558523 | GMP-ECM 7.0.5, B1 = 11000 (driver tier 1), on the C155 | event log 2026-10-16T20:34:13Z; split log `ECM B1=11000: 155-digit -> 11 x 144` |
| p71, p74 | **FactorDB (external; finder not recorded)** | see "Provenance" |

**Already public?**  FactorDB already held the complete factorisation of the
C144, so these factors were public before this record.  Whether `D_K` itself
is published anywhere was not checked.

## Part A: provenance of the FactorDB split

* **Our ECM did not find it.**  Up to the fetch, the driver had run these
  curves on the C144 without a factor:
  * every tier through B1 = 3·10^6, the last being all 2400 curves at
    B1 = 3·10^6 (`ecm_done = 5`, `ecm_curves["4"] = 2400`);
  * 1200 of 4480 curves at B1 = 11·10^6 (`ecm_curves["5"] = 1200`, the
    log's last progress line `gost/gost512 1200/4480` at 22:35:46Z).

  CADO-NFS was never run on it.
* **The fetch.**
  [`provenance/gost512_factordb.json`](provenance/gost512_factordb.json) is
  the operator's record of the fetch:
  * the composite;
  * the two factors;
  * `"source": "factordb.com"` and `factordb_id` 1100000009030548498;
  * `"fetched": "2026-10-22T23:04:32.541251Z"`.
* **What the driver logged.**  At 23:04:46Z it wrote:
  `gost/gost512: C144 found fully factored on FactorDB (id 1100000009030548498) as 71 x 74; product and PARI isprime verified locally`.
  The snapshot's split log for gost512 ends with
  `FactorDB (fetched 2026-10-22T23:04:32.541251Z): 144-digit -> 71 x 74`.
* **Who found it is unknown.**  FactorDB does not record, in what was fetched,
  who found the split or how.  `found_by` says exactly that.
* **None of this is relied on for correctness.**  Both primes are re-proved
  here by PARI `isprime`.  The certificate multiplies back to `4q − t²`,
  recomputed from the std-curves parameters.  The test checks the snapshot
  entry against the fetched record.

## Part B: the four composites still open

[`open_composites.md`](open_composites.md) and
[`open_composites.json`](open_composites.json) are written by
[`open_composites.py`](open_composites.py), a new script for this part.  For
each open curve it does the following:

* It reloads the curve with batch 1's loader and recomputes `t` and
  `4q − t²`.
* It joins the survey's small primes
  ([`provenance/survey_open.jsonl`](provenance/survey_open.jsonl), copied
  verbatim) to the primes the driver found.  Their `found_by` comes from batch
  1's `method()`.
* It proves every known prime with PARI `isprime` and checks that the
  cofactor is composite.
* It requires `known primes × cofactor = 4q − t²`.

No `D_K`, `f` or degree is stated for these four.  The existing scripts state
no bound for an incomplete factorisation, and none is added here.

| curve | 4q−t² digits | known primes (proved) | open cofactor | FactorDB (2026-10-23 ≈00:33Z) |
|:--|--:|:--|--:|:--|
| nums/ed-511-mers | 155 | 2² · 11 · 282668334925509580163 (p21) | C133 | C (composite, no factor known) |
| nums/w-510-mont | 155 | 247993621 | C146 | C |
| nums/ed-512-mont | 155 | 2² · 6857 | C151 | C |
| brainpool/brainpoolP512r1 | 155 | 557 | C152 | C |

* The small primes come from the survey's `PARI factor(N, 2^32)`.
* The p21 of ed-511-mers was found by GMP-ECM at B1 = 11000 on the C153.
* The cofactors are written out in full in `open_composites.md`.
* **FactorDB status:** each cofactor was queried once, at
  `https://factordb.com/api?query=<N>`, at 00:33:32Z to 00:33:35Z on
  2026-10-23.  The responses are in
  [`provenance/factordb_status_20261023.json`](provenance/factordb_status_20261023.json).
  All four came back status `C` with only the number itself as factor.
  Querying FactorDB can add an unknown number to its database, so these
  queries may themselves have created entries.

**ECM effort per open cofactor** (GMP-ECM 7.0.5, `ecm -q -one -c CURVES B1`,
default B2), from the snapshot's `ecm_done` / `ecm_curves`:

| curve | B1 = 11e3 | 5e4 | 2.5e5 | 1e6 | 3e6 | 11e6 (of 4480) |
|:--|--:|--:|--:|--:|--:|--:|
| nums/ed-511-mers (C133) | ≤ 90, not recorded | 240 | 500 | 900 | 2400 | 1600 |
| nums/w-510-mont (C146) | 90 | 240 | 500 | 900 | 2400 | 1500 |
| nums/ed-512-mont (C151) | 90 | 240 | 500 | 900 | 2400 | 1500 |
| brainpool/brainpoolP512r1 (C152) | 90 | 240 | 500 | 900 | 2400 | 1500 |

What these counts rest on:

* **B1 = 3·10^6 and 11·10^6.** These counts are the snapshot's
  `ecm_curves`.  The driver adds to them per completed 50-curve chunk
  ([`provenance/driver.snapshot5.py`](provenance/driver.snapshot5.py), the
  driver file as it stood at snapshot 5).  Curves in a chunk interrupted by a
  restart are not counted.
* **Last logged progress at 11·10^6.**  The log's last progress line
  (22:35:46Z) reads 1450 for three curves and 1500 for ed-511-mers.  The saved
  counts are 50 curves further on for those three and 100 for ed-511-mers.
  The driver saves every finished chunk but logs a progress line only after a
  whole round of chunks.  The chunks finished after 22:35:46Z (around the
  22:51:07Z restart) and before the driver moved to CADO-NFS at 23:05Z were
  therefore saved without a log line.
* **B1 ≤ 10^6.** These tiers are recorded only as completed (`ecm_done = 5`
  covers tiers 1 to 5).  The counts shown are the tiers' nominal sizes, not
  logged counts.  In the driver version that ran them (batch 1's
  `provenance/driver.py`), a tier was one `ecm -c CURVES` call per composite,
  marked done only when the call returned.  So a tier marked complete had at
  least its nominal count, and any run cut short by a restart adds uncounted
  curves.
* **ed-511-mers at B1 = 11000.**  Its C133 was created at B1 = 11000, when ECM
  found the p21 on the C153.  The curves it received at that B1 are the ones
  run on the C153 before the find.  Their number is not recorded (at most 90),
  and they are counted as 0 below.

**What this rules out.**  GMP-ECM's own table of expected curves per factor
size, printed by `ecm -v` for each B1 at the driver's default B2, is kept in
[`provenance/gmp_ecm_expected_curves.txt`](provenance/gmp_ecm_expected_curves.txt).
Dividing the curves run by those numbers and summing over the tiers gives the
following:

| factor size | Σ curves / expected (C146, C151, C152) | ed-511-mers C133 | approx. chance missed, exp(−Σ) |
|--:|--:|--:|:--|
| 35 digits | 18.2 | 18.9 | < 10^−7 |
| 40 digits | 2.87 | 3.00 | ≈ 5–6 % |
| 45 digits | 0.40 | 0.42 | ≈ 66–67 % |
| 50 digits | 0.05 | 0.05 | ≈ 95 % |

In standard terms:

* A factor of up to about 35 digits would almost surely have been found.
* Most 40-digit factors would very likely have been found.
* 45-digit coverage is well under one expected find (the "t45" level is less
  than half done).
* 50 digits and above are essentially untested.

`exp(−Σ)` is the usual idealised model.  It treats GMP-ECM's expected-curve
figures as exact and the curves as independent.  It is an approximation, not a
measured probability, and it says nothing about whether a factor of that size
exists.

**What is running, and what is not feasible here.**

* ed-511-mers' C133 has been on CADO-NFS since 2026-10-22T23:05:07Z (event
  log, last line), and was still running when this was written.  No result
  from it is used here.
* The C146, C151 and C152 are beyond practical NFS on this 4-core machine.
  For comparison, the largest CADO-NFS split in this run was a C121, which
  took about 5 hours of wall time across several resumed runs (batch 4).
* Only more ECM, or an external result, is in reach for those three.

The graph [`report/ecm_effort.svg`](report/ecm_effort.svg) has two panels:
(a) the curves per B1 tier on each open cofactor, and (b) the same effort in
units of expected curves against factor size.

## Scope

* Part A certifies integer facts about `t² − 4q`. Conditional on the named
  curve having prime field size `q` and actual Frobenius trace `t`, and on
  the listed large factors being prime, standard ordinary-curve theory
  identifies `End(E)` as an order containing `Z[π]`. With `f = 1`, that order
  is maximal. This curve-model identification is not Lean-certified here.
* Part B records effort and status.  It makes no claim that any cofactor has
  no small factor, beyond the approximate model above.
* No attack, speed-up or weakness is claimed.  A large `|D_K|` rules out a
  small-degree endomorphism and nothing else.
* Primality is PARI `isprime`, which is a proof.  Lean proves no factor of
  gost512 prime, because all three are above 10^8.

## Files

| file | what |
|:--|:--|
| `factorizations.jsonl` | the complete factorisation certificate of gost512's `4q − t²`, in batch 1's schema |
| `dk_exact.json`, `dk_exact.md` | the result for gost512, with who found each factor, and the 38 excluded curves |
| `open_composites.py` | writes `open_composites.json` / `.md`, and with `--plot` the graph `report/ecm_effort.svg` |
| `open_composites.json`, `open_composites.md` | the four open `4q − t²`: known primes, cofactor in full, ECM effort, coverage, FactorDB status |
| `provenance/driver_state.snapshot5.json`, `driver_events.snapshot5.log` | the fifth frozen driver state and its event log |
| `provenance/driver.snapshot5.py` | the driver file as it stood at snapshot 5 (last modified 2026-10-22T08:42:59Z) |
| `provenance/gost512_factordb.json` | the FactorDB record of the C144's split, as fetched |
| `provenance/survey_selected.jsonl`, `survey_open.jsonl` | survey records of gost512 and of the four open curves |
| `provenance/factordb_status_20261023.json` | FactorDB's responses for the four open cofactors |
| `provenance/gmp_ecm_expected_curves.txt` | GMP-ECM 7.0.5's expected-curve table per B1 (`ecm -v`) |
| `report/` | `report.typ`, `dk_exact.svg`, `ecm_effort.svg`, `report.pdf` |
| `SHA256SUMS` | hashes of the data files |

## Regenerating

From the repository root, with `STD_CURVES_CHECKOUT` J08nY/std-curves at commit
`77fe6e3585ca2c2225b59d7df24b7c775437276f`:

```sh
B1=research/endosweep_dk_exact_20261016
B2=research/endosweep_dk_exact_batch2_20261016
B3=research/endosweep_dk_exact_batch3_20261017
B4=research/endosweep_dk_exact_batch4_20261022
B5=research/endosweep_dk_exact_batch5_20261023
EX="--exclude-certified $B1/factorizations.jsonl --exclude-certified $B2/factorizations.jsonl \
    --exclude-certified $B3/factorizations.jsonl --exclude-certified $B4/factorizations.jsonl"
# Part A: the certificate, from the copied survey record and the fifth frozen snapshot:
nice -n 10 python3 $B1/make_factorizations.py STD_CURVES_CHECKOUT research/endosweep_curves_20261006 \
    --dir $B5 --snapshot provenance/driver_state.snapshot5.json $EX
# The result:
nice -n 10 python3 $B1/build_dk_exact.py STD_CURVES_CHECKOUT research/endosweep_curves_20261006 \
    --dir $B5 $EX
# The Lean file:
python3 $B1/lean/gen_dk_exact_lean.py . --dir $B5 --module DkExactBatch5 \
    --target formal/targets/endosweep-dk-exact-batch5-discriminants.yaml
# Part B (PARI for the proofs; matplotlib for the graph):
nice -n 10 python3 $B5/open_composites.py STD_CURVES_CHECKOUT research/endosweep_curves_20261006
python3 $B5/open_composites.py --plot
# The graphs and the PDF (matplotlib and the typst wheel):
python3 $B1/report/plot_dk.py $B5/report
python3 -c "import typst; typst.compile('$B5/report/report.typ', \
    output='$B5/report/report.pdf', root='$B5')"
# Provenance that is not regenerated: the ECM table (stop each run once the table is printed)
echo N | ecm -v -c 1 B1        # for B1 in 11000 50000 250000 1000000 3000000 11000000
# Checks:
(cd $B5 && sha256sum -c SHA256SUMS)
python3 -m pytest -q tests/test_endosweep_dk_exact_batch5.py
```

## Lean verification

`formal/CryptoResearch/Endosweep/DkExactBatch5.lean` is generated by batch 1's
`lean/gen_dk_exact_lean.py` with `--module DkExactBatch5`, after the
singular-wording change described under "Part A: method".

* **What it imports and reuses.** It imports `CryptoResearch.Endosweep.DkExact`
  and reuses `DkCert`, `DkCert.Statement` and `DkCert.statement_of_holds`.
  Through them it reuses NistCertificates' `FactoredCert` and `noDivBelow`.  It
  is core Lean, with no Mathlib.
* **Its target.** The frozen target spec is
  `formal/targets/endosweep-dk-exact-batch5-discriminants.yaml`
  (`TASK-20261023-6fca5a`).  The id was checked for collisions:
  * in the whole tree at `HEAD`;
  * in every blob under `formal/targets` and `coordination` on all 1415
    remote branch tips.  No `TASK-20261023-*` id existed there.
* **Its namespace** is `CryptoResearch.Endosweep.DkExactBatch5`.

The theorems:

* `gost_gost512_holds` is closed arithmetic checked by `decide +kernel`.
* `gost_gost512_certificate : gost_gost512.Statement` states the same
  propositions as in batches 1 to 4:
  * `q + 1 − t = h·n` and `t² − 4q = D_K·f²`;
  * the factorisation multiplies back;
  * the squarefree part and the construction of `D_K` from it;
  * `IsDisc D_K` and the recorded degree;
  * `2^511 ≤ |D_K| < 2^512`, and the degree is at least `2^509`;
  * if the listed factors above 10^8 are prime, `D_K` is fundamental.
* **`DkExactBatch5.exact_discriminants`** collects it, together with
  `|D_K| ≥ 2^511` and `min_nonscalar_degree(D_K) ≥ 2^509`.

**The primality hypothesis.**  All three factors (19870558523, p71 and p74) are
above 10^8, so all three are in `largePrimes`.  Fundamentality of `D_K` is
conditional on their primality.  PARI `isprime` proved them; Lean did not.

**Not certified:**

* the primality of `p` and `n`;
* that `t` is the trace of Frobenius of gost512;
* any elliptic-curve fact.

**Checked locally** with Lean 4 (`leanprover/lean4:v4.35.0-rc1`,
`formal/lean-toolchain`), using `lean -o` in order on `Discriminant.lean`,
`NistCertificates.lean`, `DkExact.lean` and `DkExactBatch2.lean` to
`DkExactBatch5.lean`:

* all seven compile;
* `#print axioms` gives `[propext, Classical.choice, Quot.sound]` on
  `exact_discriminants`, on `gost_gost512_certificate` and on
  `DkExact.DkCert.statement_of_holds`, and no axioms on `gost_gost512_holds`;
* the file has no `sorry`, `admit`, `axiom`, `unsafe` or `native_decide`.

**Negative controls.**  Two edited copies were compiled, and the kernel
rejected both: `decide` proved `gost_gost512.Holds` false.

* In the first, the last digit of the p71 was changed.
* In the second, the last digit of `n` was changed.
