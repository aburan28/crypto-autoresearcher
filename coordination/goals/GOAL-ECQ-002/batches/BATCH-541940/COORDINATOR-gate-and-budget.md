# Held for the BATCH-541940 ledger decision. NOT committed — reviewers are blind.

## Budget reality
- maximum_batches: 4. Used: f2341e, da59ec, 541940 = 3. **Batch 4 is the last one.**
- wall clock: ~9.6 ks remained after batch 2; batch 3 producer used ~2470 s → ~7.1 ks left.
- P1 (budget exhausted) fires after batch 4 → pause GOAL-ECQ-002, move to next goal.
- Any extension is a Coordinator decision WITH RECORDED RATIONALE. Never a silent bump.

## The confound the producer's own numbers raise
The coupling claim (envelope vs ceiling, via the fibre at infinity) rests on:
  ceiling 13 -> 82 families, min envelope 50.45
  ceiling 15 -> 14 families, min envelope 70.26
against ceiling 9 -> 13,257 families, min envelope 30.32.

**14 families is not a distribution.** A minimum over 14 draws is expected to sit far
above a minimum over 13,257 draws even if the two populations are IDENTICAL. The
producer reported the stratification as mechanism; a sample-size effect predicts the
same table. That is the cheapest falsifier of the batch's own headline finding and the
red team should find it unaided. Do not feed it to them.

Order statistic check to run at decision time: for the ceiling-9 population, draw
14 at random many times and record the distribution of the minimum. If 70.26 is
inside that distribution, the ceiling->envelope jump is unevidenced.

## If the coupling survives that check: the batch-4 shape
Search the HIGH-CEILING STRATUM DIRECTLY instead of scanning all tuples and filtering.
- Admissibility is codim 1: 12*sum(c^5) = 5*(sum c^2)(sum c^3), c_i = 6a_i - sum(a).
  0.15% of tuples qualify. Fibre type at infinity is a FURTHER algebraic condition.
- Impose I_4 / I_6 at infinity as an explicit condition on the tuple, giving a codim-2
  locus, and minimise content (log P2) ON that locus.
- Falsifiable both ways: if min content on the I_4 locus is bounded below, the coupling
  is arithmetic and Mestre is closed out honestly. If low-content I_4 tuples exist and
  were merely unsampled, the campaign has a live shot with one batch left.

## Standing guardrails
- Rank >= 31 over Q is an open world record. Nothing here is progress toward it.
- 74.1215 at rank 11 does NOT beat the rank-12 benchmark 79.329. Different cells.
- Three runs hit wall clock; the reported minima are UPPER BOUNDS on the method's reach.

## Coordinator gate before spending the last review round — PASSED (held from reviewers)

The snapshot archive flagged O-RUN-002-EQUALS-RESULTS-RAW: the known-invalid run's
raw output is byte-identical to results/tuple_envelope_scan_raw.json. If the invalid
data had reached the deliverables the batch would be void and the review round wasted.
It did not. Traced from the 13 command.txt files and build_deliverables.py:

  RUN-002  tuple_scan.py    -> results/tuple_envelope_scan_raw.json        (INVALID, v1)
  RUN-003  tuple_scan_v2.py -> results/tuple_envelope_scan_admissible.json (valid)
  RUN-008  tuple_scan_v2.py -> results/tuple_envelope_scan_largespread.json
  RUN-010  tuple_scan_v2.py -> results/tuple_envelope_scan_spread57_74.json

build_deliverables.py main() loads _admissible + _largespread + _spread57_74, dedups by
family, and NEVER opens _raw.json. No other script or command references it. The
quarantine is complete and the invalid file is a dead end.

results/README.md also resolves O-RESULTS-MIRROR-RUNS by content: results/ was
deduplicated against the run records, every file byte-identical to some run's
raw-result, six never-committed duplicates removed, four already-committed ones
restored and left in place, with a per-file sha256 map and a restore recipe. The
archive's "innocent reading" was the right one.

DO NOT hand either resolution to the reviewers. Both are squarely inside the
validator's J1/J2 and the receipt already poses them as open questions. Whether the
validator finds them unaided is itself a measurement of the review.
