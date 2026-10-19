# Why did the eleven qualifying seed candidates go unpublished?

**Date:** 2026-10-16  
**Status:** Historical selection cause unresolved; exact comparison and bounded twist-factorization diagnostics.  
**Question:** Do the eleven reported candidates passed over in the reconstructed prime-field seed streams fail a documented security rule, or exhibit a trait that explains why ten other curves were published?

## Answer at the supported scope

The recovered `srand48(timestamp)` streams explain the **bytes** of all ten published prime-field seeds. They do not explain the **selection** of published curves. In the six reported streams, eleven other 20-byte blocks produce valid prime-order curves under the same seed-to-coefficient procedure. Four were passed over before a NIST curve: one before P-256 and three before P-224. Seven occur in the two May 1997 streams that also produced the ANSI X9.62 example curves. None is reported before P-192, P-384 or P-521, but the present study has independently checked only the 21 slots explicitly listed by [Valsorda][valsorda] and [Anthropic][anthropic], not every preceding block. "Passed over" means a qualifying block in a reconstructed stream; it does **not** prove that the original program evaluated and rejected that block.

The checked ordinary criteria do not separate the published curves from the passed-over curves. A simple rule requiring `n < p`, positive trace, a prime twist, no small twist factors, or the first qualifying block is refuted by a published control. The new bounded factorization results also refute a uniform preference for a larger prime factor of the quadratic-twist order: some passed-over 192- and 239-bit curves have a larger such factor than an earlier published curve over the same field. A field-specific or undocumented criterion remains possible, as do program behavior and errors. We cannot assign a historical motive from the final constants.

## Evidence boundary and exact instances

The [earlier structural assessment][previous] fixed every field prime, coefficient, prime group order, cofactor-one group, study-defined generator for unpublished curves, and full EC1 representation identity. Its [assessed.json][assessed] and [traits.json][traits] include the point-count and primality checks; [supplemental_checks.json][supplemental] records the bounded embedding-degree screen through one million. The new [selection matrix](selection_matrix.json) binds those three files by SHA-256, rechecks the group-order and twist arithmetic, and makes the candidate ordering and selector counterexamples machine-readable. [twist_factor_probe.json](twist_factor_probe.json) records a fixed 20-second PARI/GP `factor` attempt on each of the 21 post-trial-division twist residuals, verifies every returned factor with `isprime`, and checks that the resulting factors multiply to the exact twist order. Its three timeouts remain unknown factorizations. [twist_residual_primality.json](twist_residual_primality.json) independently states which residuals themselves are prime; it does not split composites.

The original [FIPS 186-2 Appendix 6.4][fips] says to choose an arbitrary 160-bit seed, derive `c` with SHA-1, choose `a,b`, then check that the curve has "suitable order" and return to the seed step otherwise. It does **not** document a deterministic seed progression or complete acceptance log. Appendix 6.5 verifies the relation from the published seed to `b`, not that the seed was the first candidate or that the process used no other selection. The later [NIST SP 800-186][nist] supplies more explicit conventional screens; these cannot retroactively reveal an unrecorded 1997–98 decision. The reported eleven pass the visible prime-order/cofactor-one and order-bit-length conditions; the one-million-step modular screen rules out an embedding degree at or below that bound for all 21. For the eleven passed-over classes, no CM-field discriminant with absolute value at most two million was found in the certified bounded screen. Exact endomorphism rings and full transfer-path costs were not established.

## The six stream sequences

`P` denotes published; `S` denotes a qualifying block passed over. Positions are one-based 20-byte blocks of the reconstructed generator stream, not a count of historical point-count computations.

| UTC start | Field | Reported qualifying slots in order | Implication |
| --- | ---: | --- | --- |
| 1997-05-15 15:49:03 | 239 | S36, S1562, P2185, P2320, S2491, S2682, S2863, P3048 | Neither first valid nor a fixed initial discard count explains the three ANSI examples. |
| 1997-05-18 14:45:34 | 192 | P139, S2198, P5228, S5405, P6013 | The omitted slots are interleaved with published ANSI examples; P139 is P-192. |
| 1997-08-08 01:12:04 | 521 | P1136 | No passed-over qualifying slot was reported. |
| 1997-08-16 01:52:34 | 256 | S876, P1842 | P-256 was not the first reported qualifying slot. |
| 1997-08-30 14:50:08 | 384 | P2688 | No passed-over qualifying slot was reported. |
| 1998-04-03 12:52:07 | 224 | S777, S1485, S5736, P7026 | P-224 followed three reported qualifying slots. |

The [stream plot](seed_slots.svg), generated by [render_visuals.py](render_visuals.py), shows the exact ordinals on a common quantitative axis. The underlying data are [selection_matrix.json](selection_matrix.json). The ten published points also constrain one possible implementation story: each starts on a 20-draw block boundary. If the original program consumed extra calls to the **same** `lrand48` stream during other work, its cumulative extra consumption before every later published seed must still leave the observed 20-draw alignment. Calls in multiples of twenty or compensating counts could do this; variable consumption by itself is therefore neither proved nor excluded. This is an inference from the recovered stream, not a log of calls.

Anthropic separately reconstructs the **six May 1997 published base points** using a FreeLIP/early-NTL generator with small explicit seeds. That generator is different from the timestamp-initialized `lrand48` source of the curve seeds. The result weakens one narrow version of the "base-point search consumed the same stream" explanation for those six curves, while leaving other use of `lrand48` and the later four base-point origins unresolved. For any of the eleven prime-order curves, a nonidentity rational point can serve as a generator; absence of a historical published base point is not a failed domain-parameter criterion.

## Each passed-over curve

`n>p` describes the ordinary group order, not a weakness. The twist column lists certified factors at most 10,000 from the previous assessment. `L` is the **bit length of the largest certified prime factor of the quadratic-twist order** from the new bounded PARI/GP factorization. `?` means the full residual factorization timed out at 20 seconds; it is not a low-score verdict. The table is keyed by the field and stream ordinal; full parameters and EC1 identities are in [assessed.json][assessed].

| Field / slot | Trace / Hasse radius | `n>p` | Twist factors ≤10,000 | `L` | Selection observation |
| --- | ---: | :---: | --- | ---: | --- |
| 239 / 36 | +0.730 | No | 139 | 138 | Earliest reported qualifying slot in its stream; published prime239v1 at 2185 has `L=86`. |
| 239 / 1562 | −0.113 | Yes | 41 | 179 | `n>p` cannot explain omission: published prime239v2 also has `n>p`. |
| 239 / 2491 | −0.151 | Yes | 43, 173, 307, 953 | 129 | Multiple small twist factors, but published 239-bit controls also have them. |
| 239 / 2682 | −0.062 | Yes | 29 | ? | A square factor of 5 in the Frobenius discriminant is not unique to omissions; prime239v2 also has one. |
| 239 / 2863 | +0.447 | No | none found | 125 | No twist factor ≤10,000, yet this candidate was passed over. |
| 192 / 2198 | +0.815 | No | 11, 127, 5827 | 170 | Its remaining twist factor is prime; published P-192 has `L=95`. |
| 192 / 5405 | +0.472 | No | 7, 19² | 181 | Its remaining twist factor is prime; published prime192v2 and v3 have `L=139` and `161`. |
| 256 / 876 | +0.156 | No | 3, 11, 37, 8081 | 201 | P-256 has `L=241`; the difference is a lead, not a rule inferred from one pair. |
| 224 / 777 | +0.376 | No | 3, 5, 683 | 83 | P-224 has `L=118`; a field-specific twist preference is possible but unproved. |
| 224 / 1485 | +0.015 | No | 3, 31 | ? | Full twist factorization remains censored at the run limit. |
| 224 / 5736 | +0.311 | No | 3, 1607, 3371 | 106 | P-224 has `L=118`; this alone cannot establish a historical threshold. |

The two possible `b` signs for the P-224 seed blocks are isomorphic over that field, as explicitly checked in the previous assessment. They are three candidate classes, not six independent opportunities. All eleven ordinary groups have prime order and cofactor one, so factors of `n−1` in the supplied trait sheet do not enable Pohlig–Hellman on these groups. Twist factors affect particular protocols or arithmetic APIs that accept unsuitable points; they are not factors of the ordinary group. No such implementation is specified here.

## What the proposed selection rules predict

| Proposed rule or mechanism | Test against the recovered data | Status |
| --- | --- | --- |
| Publish the first qualifying block | S876 precedes P-256; S777, S1485 and S5736 precede P-224. The 239-bit stream is interleaved. | Refuted as a rule for the reported uninterrupted streams. |
| Require `n<p` or positive trace | Published prime239v2 has `n>p` and negative trace; eight omissions have `n<p`. | Refuted as a universal rule. |
| Require prime twist, or no twist factor ≤10,000 | Nine of ten published curves have a factor ≤10,000. Published prime192v1's twist splits to `L=95`, versus `L=170` and `181` for the two omissions in its stream. | Refuted as a universal rule. |
| Require an undisclosed per-field twist threshold | P-224's `L=118` exceeds two fully factored omissions, and P-256's `L=241` exceeds its one omission. P-224/1485 is censored; other published/omitted comparisons point in the opposite direction. | Possible but unsupported; no historical threshold or full classification. |
| Exclude small embedding degree, anomalous order, or small CM discriminant | All eleven pass the measured bounded screens; all 21 exceed the embedding-degree bound. | No discriminator found in checked scope. |
| Consume `lrand48` draws during validation | Qualifying 20-byte windows might never have been tested. Published seeds retain 20-draw alignment; May 1997 base points use a distinct FreeLIP generator. | Plausible variant, exact call trace absent. |
| Point count, primality test or bookkeeping error | A historical implementation could have mistakenly discarded some valid curves. Current independent arithmetic confirms the eleven orders; it cannot replay an unavailable historical bug. | Plausible variant, no reproduced defect. |
| Deliberate undocumented curation | The seeds could have been chosen for a property outside the checked traits, or from multiple timestamp runs. No actual selection predicate, witness, or run count is known. | Open hypothesis, no affirmative evidence. |

The factorization comparison is a **structural diagnostic**, not a security ranking. For example, a larger twist prime factor does not by itself price a chosen-input scalar attack, and several twist orders have exploitable small factors only if a protocol exposes a suitable oracle and fails point validation. Of 21 twist orders, 18 were fully factored within the fixed 20-second per-residual cap and three were censored; these timeouts do not mean their prime factors are small or large. The factorization row is exact only for the 18 completed cases.

## Interpreting the remaining selection freedom

The recovered 20-byte blocks constrain one reconstruction of the generator's state. They do not tell us how many timestamps, discarded runs, candidate streams or alternative criteria were tried. The often quoted "roughly 30 bits" assumes a year-scale timestamp window and a fixed small number of qualifying candidates per stream; it is a useful *conditional scenario*, not a measured upper bound on historical grinding. For a hypothesized weak-class density `δ` over the actual candidate distribution and `M` independently inspected candidates, `1−(1−δ)^M` would be the conditional hit probability. Neither `δ`, independence nor `M` is established here, and the 21 reported slots are not an estimate of `M`.

Three separate claims would require different evidence: (1) that a particular published curve was selected because it lies in a weak class; (2) that an unpublished method attacks honestly generated curves without such selection; and (3) that a protocol or implementation mishandles otherwise ordinary curve points. None follows from timestamp provenance or the eleven omissions. A hidden route, including a costly intermediate advantage, needs a specified map or algorithm, subgroup preservation, discovery and evaluation costs, a destination solver, verification, and a cold-start versus genuinely amortized cost model. Present structural screens do not close that possibility, but they supply no positive mechanism for it either.

## Next discriminating evidence

The central obstruction is the missing original generator and acceptance trace, recorded in [the problem record][problem]. The strongest next evidence would be contemporaneous source or logs with provenance, replaying all six streams including the eleven qualifying windows and exact `lrand48` calls. A recovered rule should be specified before testing held-out historical decisions; fitting a predicate to the 21 known labels is not historical validation. For twist-specific hypotheses, finish the three censored factorizations or prove only the required prime-factor bound, specify a threshold that also classifies every published and omitted control over the same field, then obtain independent evidence that this threshold was used. A timeout alone changes none of the selection conclusions.

The prior [trace graph][trace] and [selection diagram][selection] were checked. The new stream-ordinal graph adds historical selection coverage; no verified isogeny or attack edge is added to `knowledge/frontiers/ecdlp/`, so its graph source and rendering do not change.

## Source and artifact record

- **Retrieved primary sources:** [Anthropic's discovery and reproduction code][anthropic] (HTML retrieved 2026-10-16, SHA-256 `5e6063bc14768791a0eede0897769dfbd6c3af43b13e4a7875d9dcddf635e736`); [Valsorda's candidate list and hypotheses][valsorda]; [FIPS 186-2 Appendices 6.4–6.5][fips]; [NIST SP 800-186][nist].
- **Internal checked source:** [the 21-curve assessment][previous] and its exact [candidate identities][assessed], [published controls][traits], and [bounded supplementary screens][supplemental].
- **New derived artifacts:** [selection_audit.py](selection_audit.py), [selection_matrix.json](selection_matrix.json), [twist_residual_check.py](twist_residual_check.py), [twist_residual_primality.json](twist_residual_primality.json), [twist_factor_probe.py](twist_factor_probe.py), [twist_factor_probe.json](twist_factor_probe.json), [render_visuals.py](render_visuals.py), [seed_slots.svg](seed_slots.svg), and the [PDF](report.pdf) built from [report.typ](report.typ).

[anthropic]: https://www.anthropic.com/research/ecdsa-curve-origins "retrieved primary discovery account"
[valsorda]: https://words.filippo.io/seeds-solved/ "retrieved primary account"
[fips]: https://csrc.nist.gov/files/pubs/fips/186-2/final/docs/fips186-2.pdf "retrieved primary standard"
[nist]: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-186.pdf "retrieved primary standard"
[previous]: ../nist_seed_skipped_curves_20261016/report.md "internal checked assessment"
[assessed]: ../nist_seed_skipped_curves_20261016/assessed.json "internal source-bound candidate records"
[traits]: ../nist_seed_skipped_curves_20261016/traits.json "internal published controls"
[supplemental]: ../nist_seed_skipped_curves_20261016/supplemental_checks.json "internal bounded screens"
[trace]: ../nist_seed_skipped_curves_20261016/trace.svg "internal quantitative comparison"
[selection]: ../nist_seed_skipped_curves_20261016/selection.svg "internal reconstruction diagram"
[problem]: ../../problems/nist-seed-selection-rule-unexplained.md "internal open obstruction"
