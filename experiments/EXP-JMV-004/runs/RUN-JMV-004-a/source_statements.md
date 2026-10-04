# source_statements.md — RUN-JMV-004-a

## UNCHECKED-AGAINST-SOURCE BANNER (read this first)

**None of the statements below have been checked against arXiv:math/0411378v3.**
No copy of that paper exists anywhere in this repository's `inputs/` corpus
(confirmed this session, matching the handoff's `inputs_note` and
specification.yaml control C1's `status_at_approval`: "NOT SATISFIED. No
agent in this program has read arXiv:math/0411378v3."). Everything
transcribed here is held, as-is, from two prior-session artifacts already in
this repository:

1. `experiments/EXP-JMV-004/cost_model.py`'s module docstring (scouting
   implementation, moved in under DEC-20260726-001 per its own header).
2. `research/JMV004_branch_a_scouting_20260726.md` (the scouting write-up).

Neither of those two artifacts is itself the paper. Both carry their own
"scouting, not evidence" banners. specification.yaml's own
`theorem_transcription_artifact` field is explicit that this two-file
transcription **is** "an object under test on equal footing with the model" —
not a verified source. Per specification.yaml control C1, a single-character
error in a transcribed constant, exponent, or normalization here would flip
the sign of `log(k/c)`, which is the headline quantity of this run. The C1
review (a digit-level check against the actual paper, by a reviewer who did
NOT produce this transcription) is a separate, later, not-yet-dispatched
task. **C1 STATUS: PENDING** for every statement below, and for everything
derived from them anywhere in this run's other artifacts.

---

## Theorem 1.1 (as held)

> `m = (log q)^(2+delta)` — "m = p(log q)" for some polynomial p.

Verbatim source text (from `cost_model.py` docstring, line 12):
```
m       = (log q)^(2+delta)                       [Thm 1.1, m = p(log q)]
```
And from the research note (`research/JMV004_branch_a_scouting_20260726.md`,
"What was computed"):
```
m = (log q)^(2+δ)                             Thm 1.1
```

**What is and is not held**: the held transcription gives the *specific*
polynomial family `(log q)^(2+delta)` used throughout this run's model, and
attributes to Theorem 1.1 only the weaker existential claim that *some*
polynomial `p(log q)` suffices ("m = p(log q)"). The research note makes this
explicit: "Any `δ > 0` is asymptotically valid — the theorem only asserts
*some* polynomial `p(x)`." The specific family `(log q)^(2+delta)` swept in
this run is therefore a modelling choice consistent with, but not identical
to, the literal content attributed to Theorem 1.1. Statement number: Thm 1.1.
No section/equation number beyond "Thm 1.1" is held in either source file.

---

## Corollary 1.2 — NOT HELD VERBATIM (protocol deviation, reported per stopping_rules)

Neither held source file transcribes Corollary 1.2 as an equation-level
statement. Both reference it only narratively:

- `cost_model.py` docstring, line 4: "Converts Corollary 1.2 (polylog(q)
  ORACLE QUERIES) into field operations, and compares against Pollard rho at
  sqrt(n)."
- `research/JMV004_branch_a_scouting_20260726.md`, line 14: "Corollary 1.2
  gives `polylog(q)` **oracle queries**."

Per specification.yaml's stopping_rules ("If any of the four required source
statements cannot be archived verbatim as held, STOP and report an
infrastructure defect rather than paraphrasing. A paraphrased theorem cannot
be digit-level checked."): **this statement is reported as a completeness
gap in the held transcription artifact, not paraphrased or fabricated to
fill it.** The two phrases above ("polylog(q) oracle queries") are the
complete verbatim text available in this repository for Corollary 1.2; no
normalization, exponent, or equation form for it is held anywhere in the
corpus. This gap does not block the model/grid computation in this run,
which draws only on the Theorem 1.1 m-formula, the Sec 4.3 k-approximation,
Lemma 4.1's bound, and Proposition 3.1's walk-length inequality (all held
below) — but it means Corollary 1.2's own precise statement has never been
digit-checked in this program at all, and this run's `analysis.md`/
`cost_model.md` make no claim purporting to reproduce Corollary 1.2's
statement itself, only the four quantities named above. This gap is flagged
for the Coordinator and the (separate) C1 reviewer as a candidate repair
target for the held transcription artifact.

---

## Section 4.3 — split-prime generator count (as held)

Verbatim source text (`cost_model.py` docstring, line 13):
```
k       = lambda_triv ~ #{split p <= m} ~ pi(m)/2 [Sec 4.3]
```
And (`research/...md`, "What was computed"):
```
k = λ_triv ≈ #{split p ≤ m} ≈ π(m)/2          §4.3
```
Statement number: Sec 4.3 (no equation number held). This is the PRIMARY
degree convention adopted in this run's model (split primes contribute one
generator each, hence the `/2` factor relative to `pi(m)`, the count of all
primes `<= m`). The ALTERNATE degree convention (`k = pi(m)`, no `/2`,
"each split prime contributes 2 generators") is computed side by side for
condition E2 sensitivity only; see `cost_model.md` for the written
reconciliation and `constants_table.csv` for its provenance note. Neither
form is held with an explicit equation number beyond "Sec 4.3"; the `/2`
factor's precise derivation (e.g., whether it comes from a stated formula in
the source or is descriptive shorthand) is UNCHECKED-AGAINST-SOURCE.

---

## Lemma 4.1 — eigenvalue bound and its normalization (as held)

Verbatim source text (`cost_model.py` docstring, line 14):
```
c       = C * m^(1/2) * log|mD|,  |D| <= 4q       [Lemma 4.1]
```
And (`research/...md`, "What was computed"):
```
c = C · m^(1/2) · log|mD|,  |D| ≤ 4q          Lemma 4.1
```
Statement number: Lemma 4.1. Normalization/constant provenance, verbatim
from `cost_model.py`'s "CRITICAL HONESTY NOTES" (lines 18-21):
```
1. C is the implied constant of Lemma 4.1. The paper says only that it is
   absolute, it never states a value. Pinning it needs the Bach-Sorenson
   explicit constants (JMV ref [2]). It is NOT assumed to be 1 here - it is
   SWEPT, and the threshold behaviour in C is the reported output.
```
And from the research note (line 26): "`C` is Lemma 4.1's implied constant.
The paper states only that it is absolute and never gives a value; pinning
it needs the Bach–Sorenson constants (ref [2])." This is why `C` is swept
over `{0.5, 1, 2, 4, 8}` in this run rather than pinned to a single value —
per specification.yaml's stopping_rules, "If a needed explicit constant has
no traceable citation, STOP for that cell and record it as
not_computable_without_citation. Do not proceed with an invented or assumed
value." A single numeric `C` is NOT_COMPUTABLE_WITHOUT_CITATION from this
program's corpus (the Bach-Sorenson explicit-constant paper, JMV ref [2], is
not held anywhere in `inputs/`); `C` is therefore swept, not invented or
fixed to 1. `|D| <= 4q` is used AS EQUALITY (`|D| = 4q`) in this run's
`c`, the conservative (largest-`c`, most-anti-positive-sign) reading of the
stated bound — see `constants_table.csv` for the disclosure that this choice
biases against, never toward, a positive-sign ("non-vacuous separation")
finding.

---

## Proposition 3.1 — walk-length inequality (as held)

Verbatim source text (`cost_model.py` docstring, line 15):
```
r       >= log(2h/|S|^(1/2)) / log(k/c)           [Prop 3.1]
```
And (`research/...md`, "What was computed"):
```
r ≥ log(2h/|S|^(1/2)) / log(k/c)              Prop 3.1
```
plus the held order-of-magnitude note for `h` (`cost_model.py` docstring,
line 16; research note line 22):
```
h       ~ sqrt(|D|) ~ sqrt(q)                     [class number, order of magnitude]
```
Statement number: Prop 3.1. `|S|` (the target-set size inside the logarithm)
is not itself given a numeric value in the held transcription; this run's
implementation introduces a DECLARED (not paper-sourced) parameter `eps`
with `|S| = eps * h`, `eps = 0.5` by default with sensitivity checked at
`{0.1, 0.5, 0.9}` — flagged explicitly in `constants_table.csv` as
`NOT_COMPUTABLE_WITHOUT_CITATION` for a specific value, and disclosed as
having NO effect on the sign of `log(k/c)` (it enters `r` only, inside a
logarithm), which is the headline quantity this run reports.

---

## Per-step cost models (as held, supporting specification.yaml method item 4)

Verbatim (`cost_model.py` docstring, lines 27-33):
```
4. Three per-step cost models are reported, because JMV's 2005 figure is not
   the only one available today:
     phi_l     O(l^3)      JMV Sec 4.1, via modular polynomials (Galbraith)
     velu      O(l)        plain Velu, given a kernel point
     sqrt_velu O(l^(1/2))  Bernstein-De Feo-Leroux-Smith 2020
   Which model holds is an assumption about available algorithms, and the
   feasibility verdict depends on it. That dependence is the finding, not a
   detail to be optimized away.
```
Only `phi_l O(l^3)` (JMV Sec 4.1) is attributed to the JMV paper itself;
`velu` and `sqrt_velu` are held as citations to later, separate literature
(plain Velu's formulas; Bernstein-De Feo-Leroux-Smith 2020), reported as
OPTIMISTIC/CAVEATED alternates per the research note's "load-bearing caveat"
(a random split prime generally lacks rational `l`-torsion over the base
field in this ordinary-curve setting, so a kernel point is not cheaply
available — `velu`/`sqrt_velu` assume it is). specification.yaml's own
method item 4 requires modelling "the typical-l and the best-case-l=2
variants and report both," which this run's `phi_l` row satisfies as the
PRIMARY/APPLICABLE variant; `velu`/`sqrt_velu` are reported in addition,
strictly more disclosure than the frozen method requires, never as the
headline figure.

---

## Precomputation term (as held, supporting specification.yaml method item 5 / condition E4)

specification.yaml's own method item 5 (frozen contract text, not a
paper-external source but the binding contract itself): "At the m the
theorem's generator set forces at cryptographic q, Phi_l has on the order of
l^2 coefficients and is not storable. A cost that silently assumes free
precomputation is not a cost." This run's `phi_l_storage_coeffs_order` field
(`compute_grid.py`, evaluated at the typical `l ~ Theta(m)` per cell)
implements this order-of-magnitude coefficient count directly from the
frozen contract's own text; see `cost_model.md` for the full E4 statement.

---

*End of held transcription. Every statement above is UNCHECKED-AGAINST-SOURCE.
C1 STATUS: PENDING.*
