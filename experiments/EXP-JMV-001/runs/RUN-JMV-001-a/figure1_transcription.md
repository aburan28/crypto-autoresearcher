# Figure 1 transcription artifact, archived verbatim as held — RUN-JMV-001-a

## UNCHECKED-AGAINST-SOURCE BANNER

**THIS TRANSCRIPTION HAS NOT BEEN CHECKED AGAINST arXiv:math/0411378v3.**
No agent in this program has read the source paper; it is not in the corpus.
This file archives the transcription exactly as this program currently holds
it (verbatim, not tidied or reconstructed, per specification.yaml's stopping
rule: "Reconstructing or tidying the artifact destroys the object under
test"). Control C1 (an independent reviewer who did NOT produce this
transcription checking it against the source) has NOT been satisfied by this
task and is explicitly out of this task's scope (control C1b implementation
of C1). No conclusion about arXiv:math/0411378v3 itself may be drawn from
this file or from this run.

## Provenance

The complete held transcription of Figure 1's numeric content exists ONLY as
a plain-text paste embedded in two files in this program:

1. `research/JMV2005_experiment_suite_20260726.md`, Section 2 and Section 2b
   (prose transcription with inline numeric values).
2. `experiments/EXP-JMV-001/cpi_audit.py` (the same numeric values, encoded
   as Python literals in the `KOBLITZ` dict and referenced in comments for
   the prime rows).

There is no separate, cleaner source file, and no copy of the paper's actual
PDF/Figure-1 image exists anywhere in `inputs/` (verified this session by
inspecting the `inputs/` directory tree and finding no JMV/0411378 entry).
The two files above ARE the complete `figure1_transcription_artifact`
referenced by `specification.yaml`'s `inputs.figure1_transcription_artifact`
field. This file reproduces their numeric content verbatim, without
reformatting the reported values, and adds no new digits or corrections.

## Complete row inventory, AS HELD (row count, labels, printed order)

The held transcription's row inventory is exactly the ten rows in
`specification.yaml`'s `inputs.curves_attempted`, in the order given there,
**PLUS the explicit fact that P-224 is confirmed absent as a row**:

1. P-192
2. P-224 — **CONFIRMED ABSENT.** Section 2 of the research note states
   explicitly: "Meanwhile P-224, which is *absent* from Figure 1, does
   satisfy `9 | (-d_π)`, hence `3 | c_π`." This is a positive claim about the
   paste's row inventory (an absence we hold as confirmed), not a gap in what
   we hold.
3. P-256
4. P-384
5. P-521
6. K-163
7. K-233
8. K-283
9. K-409
10. K-571

**Seven further rows exist in Figure 1 as originally scoped (version 1) but
are explicitly out of this experiment's `curves_attempted` scope and are not
reported with any result of any sign, per `invalidation_rules`:**
B-163, B-233, B-283, B-409, B-571, IPSec-3rdOG-F2^155, IPSec-4thOG-F2^185.

## Row-by-row numeric content, AS HELD (verbatim)

**P-192, P-384, P-521: NO NUMERIC FIGURE-1 VALUE IS TRANSCRIBED ANYWHERE IN
THE HELD ARTIFACT.** Neither `research/JMV2005_experiment_suite_20260726.md`
nor `cpi_audit.py` states any `c_pi` or `P(c_pi)` value for these three rows.
This is recorded here exactly as found — it is a genuine gap in what this
program holds, not a confirmed absence like P-224's. See "Spec gap" note in
`analysis.md`.

**P-224: confirmed absent from Figure 1** (see row inventory above). No
numeric value is held for it because, per the held transcription, no row
exists for it.

**P-256** (`research/JMV2005_experiment_suite_20260726.md` Sec. 2, verbatim):

> Figure 1 lists **`c_π = 3`, `P(c_π) = 3` for P-256**.

Column semantics as held for this row: `P(c_pi)` is read as "the (claimed)
largest prime factor of `c_pi`"; for P-256 the paste states `c_pi` itself
equals the single value 3 (i.e. no separate list of smaller factors is
pasted for this row — the reading taken is that `c_pi = P(c_pi) = 3` for
this row, a fully "complete" one-factor case, though note this row's
Figure-1 check is NOT run through the three-part CTRL-FIG1-ROWCHECK rubric
by this run because it carries no *listed-factors × P(c_pi)* product to
check — only a single claimed value for `c_pi` itself. See `analysis.md` for
how this is handled.)

**K-163** (`cpi_audit.py` `KOBLITZ` dict, verbatim Python literal, and
`research/...md` Sec. 2b table):

```
listed_factors = [45641, 82153, 56498081]
P(c_pi) as printed = 86110311
```
Verbatim table row (Sec. 2b): `K-163 | 45641·82153·56498081·P, P = 86110311`

Column semantics as held: `c_pi = (product of listed_factors) * P(c_pi)`,
and `P(c_pi)` is claimed to be the LARGEST of the full factor list
(listed_factors ∪ {P(c_pi)}).

**K-233** (verbatim):

```
listed_factors = [5610641, 85310626991]
P(c_pi) as printed = 150532234816721999
```
Verbatim table row (Sec. 2b): `K-233 | 5610641·85310626991·P, P = 150532234816721999`

**K-283** (verbatim):

```
listed_factors = [1697, 162254089]
P(c_pi) as printed = 1779143207551652584836995286271
```
Verbatim table row (Sec. 2b): `K-283 | 1697·162254089·P, P = 1779143207551652584836995286271`

**K-409** (verbatim — INCOMPLETE as held):

```
listed_factors = [21262439877311, 22431439539154506863]
P(c_pi) as printed = NONE ("line-wrapped into unusability", per cpi_audit.py
                      and research/...md Sec. 2b: "K-409/K-571 do not (their
                      P(c_π) values are line-wrapped into unusability)")
```

**K-571** (verbatim — INCOMPLETE as held):

```
listed_factors = [3952463]
P(c_pi) as printed = NONE (same reason as K-409)
```

## What this transcription does NOT claim

This file archives numeric content and its held provenance only. It makes no
statement about whether this content matches arXiv:math/0411378v3. Any
apparent gap or inconsistency identified in `analysis.md` and
`transcription_fidelity.md` is reported as a property of THIS ARTIFACT AS
HELD, pending the separate C1 review by a reviewer who did not produce this
transcription.
