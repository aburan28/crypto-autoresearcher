# TASK-20260913-0188bf — task report

- **Role:** coordinator subagent (knowledge curation + one decision record)
- **Goal / batch:** `GOAL-SEMBIN-fcb7a2` / `BATCH-efea59`
- **Branch:** `cursor/semaev-2015-audit-program-5b8b`
- **Objective:** read the two newly frozen Nagao preprints that Nagao 2015/984
  leans on — ePrint 2013/549 (`[11]`, source of its Lemma 3 and Lemma 5) and
  ePrint 2013/548 (`[10]`, credited with the disjoint factor base) — and record
  what they establish and what they do not.
- **Runs executed:** none. No experiment was launched and no measurement taken.
- **Commits made:** none. Every archival commit is the top-level session's.

## Files written

| path | what it is |
|---|---|
| `inputs/NAGAO-2013-549/source_record.yaml` | `SRC-NAGAO-2013-549` freeze record |
| `inputs/NAGAO-2013-548/source_record.yaml` | `SRC-NAGAO-2013-548` freeze record |
| `knowledge/literature/KN-LIT-c5dceb.md` | read record, ePrint 2013/549 |
| `knowledge/literature/KN-LIT-ebd657.md` | read record, ePrint 2013/548 |
| `knowledge/open-problems/KN-OPEN-7f0511.md` | open problem opened by the reading |
| `ledger/decisions/DEC-20260913-8d19e5.yaml` | the Coordinator decision |
| this file | task report |

Nothing else was touched. `KN-LIT-71b758`, `H-SEMBIN-c59e50`,
`IDEA-20260913-352163`, every goal record, `knowledge/sources.json` and
`knowledge/SOURCES.md` are unmodified (`git status` confirms: the only changes
under `knowledge/` are the three new untracked files).

## Integrity checks performed before reading

- **Hashes.** Both PDFs and both `paper_fulltext.md` files were recomputed with
  `sha256sum` and agree with the `.sha256` sidecars **and** with the `sha256`
  fields in each `provenance.json`. No disagreement, so no STOP condition.
- **Page counts — a correction.** Both `provenance.json` files record
  `"pages": 2`. Counted with `pdfminer`'s `PDFPage.get_pages`, the frozen PDFs
  have **9 pages** (2013/549) and **6 pages** (2013/548); the extractions are
  30,634 and 18,123 bytes. Two independent packages carrying the same wrong
  value points at a systematic defect in whatever wrote the field, not two
  typos. The receipts are immutable and were **not** edited; the discrepancy is
  recorded in each new `source_record.yaml` under
  `provenance.recorded_page_count_disagrees_with_pdf`. The hashes in the same
  files are correct. **This also corrects the task brief, which inherited "2
  pages each" from those receipts** — the papers are substantially longer than
  the brief assumed.
- **Anchors.** All page anchors below are PDF pages of the frozen files, mapped
  by per-page `pdfminer` extraction. Every statement quoted was re-read in the
  PDF, because 2013/549's extraction interleaves overset vector arrows with the
  displayed formulas.

## The four questions

### 1. Lemma 3 — what 2013/549 proves, and in which direction

**The statement is there and it is proved.** 2015/984's Lemma 3 is 2013/549's
**Lemma 2, page 4**, modulo renaming (`G`/`D` for `f`/`deg F`):

> Let `G_1, ..., G_N ∈ F_p[X_1, .., X_N]` be local polynomials and put
> `F := Σ G_i · (X_i^p − X_i)` and `D := deg F`. So, there are some local
> polynomials `G'_1, ..., G'_N` satisfying `F := Σ_{i=1}^N G'_i · (X_i^p − X_i)`
> and `deg G'_i <= D − p` (`i = 1, ..., N`).

The proof occupies **pages 4–5** and is a descent on the leading monomial: fix a
degree-compatible monomial order, let `ψ(G)` be the largest `LM(G_i X_i^p)` over
representing tuples and `NUM(G)` the number of indices attaining it; if
`NUM(G) = 1` the bound falls out of `deg ψ(G) = D`, and if `NUM(G) > 1` with
`deg ψ(G) > D` an explicit `G^new` with `ψ(G^new) < ψ(G)` is constructed, the
lemma following by induction on `ψ(G)` (well-founded, monomial orders being
well-orders). **Said plainly, because the brief asked for it in both directions:
2013/549 does prove the statement 2015/984 says it proves.**

**Directions of every inequality found.** All upper bounds, and none of them is
`d_F <= d'_F`:

- Lemma 2, p. 4 — the rewritten **coefficients**: `deg G'_i <= D − p` (at `p = 2`,
  `D − 2`).
- Proposition 1, p. 7 — the first fall degree: `<= (p−1)dα + 1`.
- Lemma 1, p. 3 — the Gröbner cost: `<= O(N^{D_ff·C+O(1)})`.

**`d_F <= d'_F` is not in 2013/549, in either direction.** It cannot be:
2013/549 predates the true/fake split and uses one notion, its Definition 1
(p. 3, Petit-style, no field-equation reduction). The split is 2015/984's
Definitions 5 and 6, and the inequality is **2015/984's Lemma 4 — printed with
no proof at all**.

So, to the brief's exact question: **the fake-degree substitution rests on
2013/549 for the load-bearing *ingredient* of the direction that matters, not for
the assembled inequality and not merely for a sharper statement it does not
need.** Converting "the excess vanishes mod `S_fe`" into "the excess is a
degree-controlled combination of field equations" is precisely the step
`d_F <= d'_F` needs, and that step is Lemma 2. The chain is:

> 2013/549 Lemma 2 (**proved**) → 2015/984 Lemma 3 (borrowed) → 2015/984 Lemma 4
> `d_F <= d'_F` (**asserted, unproved**) → the substitution.

**"Complicated and not constructive" reconciled.** The proof is complete and
constructive in the logical sense. The non-constructivity is a *different* fact
and 2013/549 states it itself, p. 5, immediately after Lemma 2: "when
`deg f ~ exp(n^{1/3+O(1)})`, computation of such `G'_i` is very difficult and its
complexity (using direct computation) seems to be exponential of `n`, although
computation of `wd(f)` is subexponential." That is about **producing witnesses**,
not about existence — so it does not bite on an instrument that needs only the
bound.

**Two blemishes, both notational.** (i) The case `NUM(G) > 1` with
`deg ψ(G) <= D` is not spelled out; it is immediate but absent from the printed
analysis. (ii) Step 1) prints `X_{I_1}^p | G_{I_i}` — divisibility of the whole
polynomial — where only `X_{I_1}^p | LT(G_{I_i})` follows and only that is used,
so the printed claim is stronger than both what holds and what is needed. The
notation sentence also prints `LT` as `LM`.

### 2. The revision note

2013/549 p. 1 carries **two** unintegrated notes, both already folded into the
one frozen version.

**"Revise 6 NOV"** states the failure outright — "the solution of the equations
system `{[m_0 F]#_i = 0} ∪ S_fe` must equals to `{[F]#_i = 0} ∪ S_fe`. However,
it is not true" — and repairs it by taking `τ` outside the base subspace and
replacing the monomial multiplier `m_0 = Π X_i^{p^α−1−E_i}` by the **polynomial**
`Π (X_i − τ)^{p^α−1−E_i}` ("(not monomial but polynomial)"), asserting "we have
this property and all lemmas still hold."

What it does to the first-fall-degree machinery:

- **The repair is in the body.** p. 6 defines `m_0 := Π (X_i − τ)^{p^α−1−E_i}`
  and Lemma 6 (p. 6) is exactly the solution-set equality the monomial version
  lacked. The frozen text *is* the repaired version.
- **It does not touch the lemma 2015/984 cites.** Lemma 2 is in Section 2, is
  about the field-equation ideal alone, and mentions neither `m_0`, nor `τ`, nor
  Section 3. What the repair touches is Section 3's weight bookkeeping, where
  Lemmas 7–8 must range over `Mon(m_0)` rather than a single monomial — which, as
  printed on p. 6, they do.
- **"All lemmas still hold" is the author's assertion and was not checked here.**

**"Revise 9/8"** — "Lemma 9 of the first version of this manuscript is false and I
delete the content of §4 and related footnote" — leaves a matching scar: **there
is no Lemma 10 anywhere**; Lemma 9 (p. 7) is followed directly by Lemma 11
(p. 7). This touches the *other* borrowed lemma: **2015/984's Lemma 5 is this
paper's current Lemma 9 (p. 7)**, the same number the author declares false in
the first version. The current Lemma 9 is proved in two lines by bilinearity and
there is no reason to doubt it; whether the retracted statement is the same
statement **cannot be settled from the frozen bytes**, since the first version is
not frozen.

**Is the repaired version the one 2015/984 cites?** Not settleable from these
bytes — a strong inference only. The landing page records the last revision as
2013-11-05 with none later, the served `last-modified` matches, and 2015/984 was
received 2015-10-12, nearly two years after; its reference [11] is a bare URL
with no version or date. So these bytes are the only version ePrint was *serving*
when 2015/984 was written. That is a claim about availability, not about what the
author had in hand.

### 3. The priority question

**Yes, the construction is in the frozen bytes — Section 7, pages 4–5.** Fix a
basis `[w_1..w_n]` of `F_{p^n}/F_p` and `n_1 + ... + n_d ≈ ng`; put
`B'_i := {Σ_j x_{i,j} w_j | x_{i,j} ∈ F_p}`; take `r_1, ..., r_d ∈ F_{p^n}` and
set `B_i := {P − ∞ ∈ Jac(C/F_{p^n}) | P ∈ C(F_{p^n}), ∃x ∈ B'_i such that
x(P) = x + r_i}`. **Footnote 3, p. 5** gives the disjointness recipe: "Take
`r_{i+1} ∈ F_{p^n} \ ∪_{j=1}^i B'_j` and disjoint decomposed factor is
constracted." The yield accounting is stated in full on p. 5, both halves of the
trade: "`B_i`'s are essentially disjoint, `|B_i| ≈ p^{n_i}` ... **From the
disjointness, it is improved that the term of `1/d!` in the probability is
omitted.** (Remark that it is needed to compute gaussian elimination of `d`-times
size matrix in the last step.)" (The summation limit in `B'_i` prints as `n_j` in
both PDF and extraction — an apparent typo for `n_i`, recorded rather than
silently corrected.)

**Elliptic case: by specialisation only, and the paper never specialises it.**
Section 2 (p. 1) fixes a plane curve of small genus `g`; Section 7 is written for
`Jac(C/F_{p^n})` with `P − ∞` throughout, which at `g = 1` is the standard
identification. "Elliptic curve" appears in Section 7 only in its *attribution*
paragraph. Proposition 5's proof takes `d = ng`, `n_i = 1`, which at `g = 1` is
the same many-summands/constant-coset shape 2015/984 uses at `p = 2`.

**The paper does not claim the construction, and says so twice.** p. 4 credits
Diem [2] (2009, "Diem-variant") and then Matsuo: "In 2005 or 2006, soon after the
Semaev's formula is discoverd, Matsuo also found the simmilar and more general way
of taking decomposed factor ... it it not presented and only the researchers
around him knows this." p. 5: "Here, we propose the way of taking decomposed
factor of Jacobian of the curve, which is **the generalization of Matsuo's
decomposed factor**."

**The retraction lands elsewhere.** The p. 1 note — "Proposition 3 is not true and
this thechnique can not be used. So, we re-write §4" — hits the equation-system
machinery, not Section 7; `B_i = B'_i + r_i` and the `1/d!` count do not use
Proposition 3. It does degrade what Section 7 sits on ("the number of the
equations is quite large"). Three further defects: a statement numbered
Proposition 3 is **still printed** (p. 3, §5) and cannot be identified without the
first version; **Proposition 5's proof cites "Proposition ??" twice**, so the two
propositions the paper's only complexity claim depends on are unnamed; and
footnote 2 (p. 3) declares an unrepaired projective-vs-affine gap.

**A scope point.** Proposition 5 (p. 5) is restricted to `log p = O((ng)^2)` — the
**large-characteristic** Diem regime — while 2015/984's Theorem 1 is
small-characteristic with `F_{2^n}` as headline. The coset construction is shared;
the conclusion drawn from it here is not.

**Status, in one sentence I would defend to a reviewer:**

> A disjoint coset-shifted factor base with the `1/d!` yield removal stated
> explicitly is present in the frozen last revision of Nagao ePrint 2013/548 at
> Section 7 (pages 4–5, footnote 3), covering the elliptic case only by
> specialisation at `g = 1`, and that paper itself credits the idea to Diem (2009)
> and to Matsuo (2005/2006, unpublished) rather than claiming it — so the
> construction is older than this program's mechanism lane assumed and is not
> Nagao's either, while *who re-discovered what* remains unsettled here because
> two earlier revisions of 2013/548 are not frozen, ePrint 2014/806 has not been
> opened by this task, and the Matsuo attribution is unverifiable in principle.

**What the bytes cannot do:** date Section 7 (two earlier revisions exist, neither
frozen, ePrint serves only the latest); say anything about 2014/806's content
(not frozen, not opened, and not to be characterised from memory); confirm or
refute the Matsuo attribution. **What would settle it:** freeze and read 2014/806,
turning one author's assertion into a comparison of two read texts. If §7's date
becomes load-bearing, an earlier revision must be recovered from outside ePrint
and its absence recorded as an impediment rather than inferred past.

### 4. What each paper changes for this program

**For `EXP-SEMBIN-4fa22c`** (in design; **no record exists at that identifier** —
`experiments/EXP-SEMBIN-4fa22c` is absent and the ID appears only in
`coordination/bus/messages/MSG-20260913-67d64f.yaml`, so it is deliberately not a
decision target):

- The existence half of the Lemma 3 dependency is **discharged** — the statement
  is proved at 2013/549 Lemma 2, p. 4.
- The non-constructivity is about witness computation, and the instrument
  computes no witnesses, so **it does not bite**.
- The assembled inequality `d_F <= d'_F` still rests on 2015/984's **unproved**
  Lemma 4.
- **The consequence the contract should state explicitly:** a measured
  `d'_F > 4` **refutes** 2015/984's Proposition 5 regardless of Lemma 4, because
  Proposition 5 asserts an upper bound and a violated upper bound is violated. A
  measured `d'_F <= 4` **confirms** it only *through* Lemma 4. The instrument is
  therefore a **one-directional refuter** until Lemma 4 is proved or checked at
  the tested parameters, and a success criterion symmetric in the two directions
  overstates what a rank computation can deliver.

**For `H-SEMBIN-c59e50`'s novelty language** (untouched; another session is
reviewing it):

- Calling the `m!`-removing device "a PUBLISHED device: Galbraith-Gebregiyorgis
  2014/806 section 4.2" is accurate as *where this program read it* and properly
  provenanced (`KN-LIT-439`, `TASK-20260913-6519c9`). As a **priority** statement
  it is too narrow: the construction and its `1/d!` accounting are in the frozen
  2013/548 bytes, which point further back to Diem and Matsuo.
- The reading **does not** trigger that record's own novelty-downgrade condition,
  which requires prior work already composing a typed factor base with an
  auxiliary-variable presentation *and deriving the degree consequence*. §7
  composes the coset family with a Weil-descent system in the
  large-characteristic regime and derives a bound of the form `<= Const_1^d` — no
  first-fall-degree consequence, nothing about a chained presentation. So the
  indicated change is an **attribution correction, not a novelty downgrade**.
- Separately, and sharpened rather than created by this reading: the mechanism
  block's sentence "removal (i) has never been composed with a presentation whose
  solve is CLAIMED polynomial" reads as false against 2015/984's own Section 7 —
  a paper already read as `KN-LIT-71b758`, so this is not new evidence. The
  distinction that survives is real and narrow (2015/984 descends a *single*
  summation polynomial, not Semaev's chained-`S_3` system with auxiliary partial
  sums), and the language should name the presentation explicitly or a reviewer
  will read it as wrong.

## Lemma 3 dependency: **partially discharged**

- **Discharged:** the statement exists and is proved in a frozen, read source
  (2013/549 Lemma 2, p. 4; proof pp. 4–5), and the "complicated and not
  constructive" label is about witness cost and does not bear on a bound-only
  instrument.
- **Still open:** (i) `d_F <= d'_F`, the inequality actually relied on, is not in
  2013/549 in either direction — it is 2015/984's Lemma 4, printed without proof;
  (ii) this was a Coordinator *read* for presence and structure, not an
  independent adversarial review, and it found two notational defects and one
  unspelled case; (iii) nothing connects either definition to the recombination
  version `D_ff^max` that the author himself calls credible and cannot establish
  for descent systems.

## What surprised me, and what bears on claims elsewhere

1. **Nagao says on the record that the first fall degree assumption has
   counterexamples, and that his systems are deliberately outside the genericity
   hypothesis under which it is assumed.** 2013/549 p. 3: "This assumption has
   some counter examples and Petit et al. assume that the polynomials
   `f_1, ..., f_l` are general polynomials. However, if `f_1, ..., f_l` are
   randomly chosen, the value of `D_ff` seems to be very large. In our situation,
   we treat only the cases that `D_ff ~ max_i deg f_i` and so, `f_1, ..., f_l`
   cannot be randomly chosen." This is the author of the polynomial-time claim, in
   the paper that claim cites.

2. **He names the definition under which the assumption is plausible and says he
   cannot discharge it.** Same page: for any invertible `M` he sets
   `(f^{(M)}_i) := M(f_i)`, defines `D_ff(M)`, puts `D_ff := max_M D_ff(M)`, notes
   the assumption "seems to be true" for it — then: "However, by using this new
   assumption, **I can not prove that the equations system coming from Weil descent
   have low first fall degree in strict way and it remains a future work**."
   `D_ff^max >= D_ff` by construction, so the credible version is the *harder*
   condition, and it is the one relevant to an algorithm because F4 recombines
   generators. This is the reason `KN-OPEN-7f0511` was written.

3. **2013/549's Assumption 1 carries a `+ O(1)` that 2015/984's drops.** Here
   (p. 3): "Upper bound of the degree ... of F4 algorithm is `D_ff + O(1)`", with
   Lemma 1 charging `O(N^{D_ff·C+O(1)})`. 2015/984 reads "`<= d_F`" and charges
   `O(N^{d_F w})`. Invisible against a subexponential target; **not** invisible
   against a claim that names an exponent — under the cited predecessor's version
   `O(n^{8w+1})` becomes `O(n^{8w+1+O(1)})` with the `O(1)` unquantified. The
   claim stays polynomial; **the exponent is not determined by the assumption as
   2013/549 states it**, and every concrete cost this program derives from `8w+1`
   inherits that. Cheapest item in this report: a disclosure, not a research
   result.

4. **The pair isolates exactly what is new in 2015/984.** 2013/549 reaches
   *subexponential* ECDLP/JACDLP under the first fall degree assumption; 2015/984
   reaches *polynomial* from the same assumption; the difference is the 2013/548
   §7 construction. That makes 2015/984's **unproved Proposition 5** — the
   affine-invariance step — the only new mathematical content between the two
   conclusions, which strengthens the case for the audit target this program
   already picked.

5. **The two 2013 papers corroborate nothing about each other.** Received the
   same day (2013-09-04), both self-described joint work with Matsuo and Takagi
   under a single-author ePrint entry, both PDFs titled "(Draft)", both carrying a
   "6 Nov" note retracting a numbered result, each citing the other.

## Why `KN-OPEN-7f0511` was written rather than skipped

The brief made it optional and warned against filling a slot. It is written
because item 2 above is an **author-declared open problem sitting directly under
a published polynomial-time claim**, and because the reading leaves four
inequivalent quantities in this corpus all called "the first fall degree"
(2013/549 Definition 1; `D_ff^max`; 2015/984 `d_F`; 2015/984 `d'_F`), with the
instrument able to measure only the fourth. Checked for overlap against
`KN-OPEN-d218ec`, which is the nearest: that record asks *where* Semaev's
Assumption 1 fails in `(n, m, t, k)` and whether Semaev's `d_F4` is the quantity
`GOAL-DREG-001` measures. Neither `D_ff^max` nor the true/fake split nor the
`+O(1)` exponent question appears in it — `D_ff^max` is not in Semaev's paper at
all. The two records meet at one point (both are partly settled by running several
degree definitions against one instance family), which is recorded in each so an
experiment serving one is designed to serve the other; neither subsumes the other.

## Verification outputs

```
$ python3 tools/validate_ledger.py 2>&1 | grep -E "8d19e5|c5dceb|ebd657|7f0511"
(empty — grep exit 1, no matches)
```

Full run: exit 1 with **20 errors, none on any path this task wrote**
(`grep -E "NAGAO-2013|c5dceb|ebd657|7f0511|8d19e5"` over the full output returns
nothing). The 20 are pre-existing: `review_plan` gaps in three handoffs
(`TASK-20260910-6d6bd3`, `TASK-20260910-c8cb36`, `TASK-20260913-9863af`) and
missing manifest fields in two `EXP-AES-14352a` runs.

```
$ python3 tools/build_source_index.py --check 2>&1 | tail -20
stale: knowledge/SOURCES.md, knowledge/sources.json; run tools/build_source_index.py
exit=1
```

**This is the pass signal, not a failure.** `--check` builds the whole index in
memory and only then compares; reaching a staleness verdict means both new
`source_record.yaml` files parsed and were consumed without error. The staleness
is exactly the two new source records, which this task is instructed not to write
into the index — `git status knowledge/` confirms `SOURCES.md` and `sources.json`
are untouched, the only changes being the three new untracked knowledge files.
The top-level session runs the tool in write mode as part of the ledger archive.

```
$ python3 tools/allocate_id.py --audit 2>&1 | tail -5
  DEC-20260722-001         ledger/DEC-20260722-001.yaml, ledger/decisions/DEC-20260722-001.yaml
  DEC-20260722-002         ledger/DEC-20260722-002.yaml, ledger/decisions/DEC-20260722-002.yaml
  DEC-20260722-003         ledger/DEC-20260722-003.yaml, ledger/decisions/DEC-20260722-003.yaml
  DEC-20260722-004         ledger/DEC-20260722-004.yaml, ledger/decisions/DEC-20260722-004.yaml
  DEC-20260722-005         ledger/DEC-20260722-005.yaml, ledger/decisions/DEC-20260722-005.yaml
  TASK-20260903-087076     ledger/archives/TASK-20260903-087076.yaml, ledger/handoffs/TASK-20260903-087076.yaml
```

21,737 record files scanned. **None of `DEC-20260913-8d19e5`, `KN-LIT-c5dceb`,
`KN-LIT-ebd657` or `KN-OPEN-7f0511` appears in either the malformed set or the
doubly-occupied set.** The listed duplicates are legacy root-level ledger
records and one archived handoff, all pre-existing; all four new identifiers were
confirmed well-formed and free with `--check` before authoring.

## Archive request for the top-level Coordinator

- **Snapshot commit:** `inputs/NAGAO-2013-549/source_record.yaml`,
  `inputs/NAGAO-2013-548/source_record.yaml`, this report.
- **Ledger commit:** `knowledge/literature/KN-LIT-c5dceb.md`,
  `knowledge/literature/KN-LIT-ebd657.md`,
  `knowledge/open-problems/KN-OPEN-7f0511.md`,
  `ledger/decisions/DEC-20260913-8d19e5.yaml`, plus a regenerated
  `knowledge/INDEX.md`.
- Run `tools/build_source_index.py` in write mode to refresh
  `knowledge/SOURCES.md` and `knowledge/sources.json`, left untouched here by
  instruction and now stale by exactly the two new source records.
- `DEC-20260913-8d19e5.next_actions` carries the follow-ups: freeze and read
  ePrint 2014/806 (the action that settles the priority question), an independent
  `review-adversarial` pass on 2013/549 Lemma 2 and on whether 2015/984's Lemma 4
  follows from it, the refuter-asymmetry finding for the `EXP-SEMBIN-4fa22c`
  contract, an agent-bus pointer to the session holding `H-SEMBIN-c59e50`, and
  the `+O(1)` exponent disclosure.
