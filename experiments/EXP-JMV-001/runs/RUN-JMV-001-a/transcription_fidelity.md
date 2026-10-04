# Transcription-fidelity control results (C1b-RESULT) — RUN-JMV-001-a

**STATUS: SCOUTING-CLASS CONTROL RESULT, RE-DERIVED FROM SCRATCH BY THIS RUN,
NOT A FIGURE-1 FINDING.** Per `specification.yaml` control `C1b-RESULT` and
its `coordinator_ruling_on_class_and_gate`: this section reports defects
measured IN OUR OWN TRANSCRIPTION ARTIFACT, as the reason the artifact
cannot be trusted pending the separate C1 review. It is not routed to any
erratum gate as an independent claim, and this run does NOT conclude that
arXiv:math/0411378v3 itself is wrong.

## K-163: internal inconsistency, both readings

Re-derived independently in this run (`run_conductor_audit.py`, cross-checked
by `verify_certificates.py`):

1. **Compositeness.** Under the reading "P(c_pi) is the largest prime
   factor," the printed value `86110311` is COMPOSITE:
   `86110311 = 3 * 7 * 367 * 11173`. A composite number cannot be a prime
   factor of anything. This certificate (`certificates/K-163_composite_P.json`)
   requires NO curve data, NO conductor theory, and NO NIST constants —
   it is refutable from the printed table alone.

2. **Product mismatch.** Under the reading "c_pi is the product of the
   listed factors times P(c_pi)," the printed product
   `45641 * 82153 * 56498081 * 86110311 = 18,241,789,221,316,136,032,457,943`
   exceeds the curve-derived `c_pi = 1,824,026,374,634,505,274,957,943` by a
   factor of exactly 10 (ratio computed: 10.000836..., i.e. approximately
   10x — the certificate records the exact ratio, not a rounded one).
   This certificate (`certificates/K-163_product_mismatch.json`) DOES depend
   on curve data and on CTRL-ORDER-KOBLITZ / CTRL-CM-KOBLITZ passing (both
   pass in this run, per `controls.json`).

3. **Single-digit repair hypothesis.** Replacing the printed `86110311` with
   `8610311` (a single inserted digit removed) gives:
   `45641 * 82153 * 8610311 * 56498081 = 1,824,026,374,634,505,274,957,943`
   — this run confirms this equals the independently-derived `c_pi` for
   K-163 EXACTLY (`raw.json`, `koblitz_rows.K-163.c_pi`). The repaired
   product identity HOLDS. However, the maximality reading would STILL fail
   under the repaired digits, because `8610311 < 56498081`, and `56498081`
   is already listed on the same row as one of the other (non-P) factors.

All three statements above are reported separately, per specification.yaml's
`C1b-RESULT` requirement that they not be merged.

## Interpretation, per the Coordinator's own binding ruling

Per `specification.yaml`'s `coordinator_ruling_on_class_and_gate`: the K-163
inconsistency has an identified, strictly more probable proximate cause
INTERNAL to this program's own artifact — a one-digit edit repairs the row
to exact product consistency, which is the signature of an OCR or retype
error in what we hold, not evidence of a published error. K-163's primary
status is therefore a measured defect in THIS PROGRAM'S TRANSCRIPTION, and
its correct destination is this file and the future C1 review packet, where
it functions as the reason the paste cannot yet be trusted — it is NOT
routed to any erratum gate as an independent finding about the paper.

## Additional fidelity gap found and recorded this run (not previously
## isolated by the scouting script)

The held transcription (`figure1_transcription.md`, this run) contains **no
transcribed Figure-1 numeric value at all** for P-192, P-384, or P-521 —
distinct from P-224, which is explicitly confirmed absent as a row. This is
a genuine completeness gap in what this program holds (not merely a
computation gap): three of the ten curves_attempted rows have no held Figure
1 content to check the recomputed arithmetic against. This is reported here
as a C1b-relevant fact about row completeness, not as any claim about the
paper: the paper may well report values for these rows that this program
simply never transcribed. See `analysis.md` "Reported specification gaps"
for how this run handles the resulting verdict, and see the handoff's
`constraints` on frozen-protocol discipline for why this is reported rather
than patched.

## What this control result does NOT establish

- It does not establish that arXiv:math/0411378v3 prints `86110311` (the
  as-held value) or `8610311` (the value that would repair the row). Only
  the source paper, read by the C1 reviewer, can settle which.
- It does not raise or lower confidence in the P-256 finding (P-256_mod9
  certificate) by transfer: per the Coordinator's ruling, there is no
  cross-block transfer of transcription confidence between the K-block and
  the P-block, and K-163's OWN defect if anything argues the opposite
  direction for confidence in the paste generally, per the ruling's point
  (c): "Under a demonstrated nonzero defect rate, attributing any remaining
  discrepancy to the paper rather than to the paste is unjustified."
- It is not a KN-LIT erratum and no CORR- record is emitted for it, per
  `invalidation_rules`.
