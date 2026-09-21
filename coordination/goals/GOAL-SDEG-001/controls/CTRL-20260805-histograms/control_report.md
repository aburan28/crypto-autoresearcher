# CTRL-20260805-histograms — cheapest-control execution, partial

Authorised by `DEC-20260805-cc2b32` `next_actions[2]`, which states this control
needs no ladder authorisation. Executed by the dispatching session, 2026-08-05.
**No experiment was approved and none ran.** `EXP-SDEG-f7faa8` remains
`review_required` / `approved_by: null`. Claim tier `toy`.

## What was asked, and what was possible

The control as specified was: rebuild the n=12 systems at seeds 2 and 2026 from
the hash-pinned `src/semaev_tree.py`, recording system hash and per-degree column
histograms at D=5 and D=6.

**The rebuild half is UNRUN, and that is an infrastructure outcome, never
mathematical evidence (AGENTS.md rule 5).** `src/semaev_tree.py` imports
`sage.all` (`GF`, `EllipticCurve`, `BooleanPolynomialRing`, `PolynomialRing`).
Sage is absent from this environment: `import sage` fails, no `sage` binary,
`apt-cache policy sagemath` reports no candidate, and `pip install
sagemath-standard` fails to build. `tools/sage_free_estimator/shim/sage/` does
**not** help — it is scoped to the lattice-estimator's 27 elementary math names
and provides none of the algebraic constructors this builder needs.

A reimplementation was deliberately **not** attempted. The control's purpose is
builder identity; a reimplementation cannot distinguish "the two lineages used
different builders" from "my reimplementation differs from both", which is the
exact failure `tools/sage_free_estimator/README.md` records this campaign losing
three batches to.

**The artifact half was run and is productive.** `experiments/EXP-SIG-008/work/n1_ms.json`
is a committed artifact holding the descended boolean system itself — `n: 12`,
`seed: 2`, `nb: 24`, 24 equations, each a list of integer **bitmasks over the 24
variables**. Monomial degree is `popcount`; boolean monomial product is bitwise
OR. The Macaulay column set is therefore reconstructible by pure combinatorics
with no Sage at all.

## Reconstruction method

For each equation `f_i` of degree `d_i` (measured: 12 equations of degree 2, 12
of degree 3) and each multiplier monomial `m` with `deg(m) ≤ D − d_i`, the row
`f_i·m` has support `{mask | m : mask ∈ supp(f_i)}` restricted to
`popcount ≤ D`. Columns are the union of all row supports. Full monomial count is
`N(24,D) = Σ_{k≤D} C(24,k)`.

## Result — every D=6 structural number reproduces exactly

| D | nrows | ncols | deleted | committed nrows | committed ncols | committed deleted |
|---|---|---|---|---|---|---|
| 6 | **183,312** | **174,033** | **16,018** | 183,312 ✓ | 174,033 ✓ | 16,018 ✓ |
| 5 | **31,512** | 46,694 | 8,761 | 31,512 ✓ | — | — |

`N(24,6) = 190,051` and `190,051 − 174,033 = 16,018` exactly. Per-degree column
histograms:

```
D=6:  {0:1, 1:24, 2:276, 3:2024, 4:10626, 5:42504, 6:118578}   u_k = {6: 16018}
D=5:  {0:1, 1:24, 2:276, 3:2024, 4:10626, 5:33743}             u_k = {5:  8761}
```

`hist[5]` rising 33,743 → 42,504 between D=5 and D=6 is expected and not a
defect: at D=6 there are more multipliers, so more degree-5 monomials are hit.

## Findings

### C-1. Blocking defect B3 is DISCHARGED at D=6 and localised at D=5

`u_k = 0 for k < D` is now **verified by independent reconstruction at D=6**
(`u_4 = u_5 = 0`, all mass at `u_6 = 16,018`). At D=5 this reconstruction also
gives `u_4 = 0`, with `u_5 = 8,761`.

That **conflicts with the committed BATCH-003 `RT-CTRLB.md` histogram
`{5: 8736, 4: 2}`** (⇒ deleted 8,738, ncols 46,717) which the Validator cited as
falsifying the blanket claim, and with the other reported pair 46,709 / 8,746.
All three partition `N(24,5) = 55,455` consistently and differ only in how many
degree-5 monomials are present: 33,743 (here) / 33,758 / 33,766.

**So there are three mutually inconsistent D5 column readings in this lineage,
and an independent reconstruction from the committed seed-2 system agrees with
none of them — while agreeing exactly with every D=6 number.** The D5
inconsistency is real, is now sharply localised, and is not explained by this
control. It does not touch G5, whose outcome the Validator showed is invariant
under all these histograms.

### C-2. The provenance objection against G1 is RETIRED — the anchor has a committed receipt

`EV-SIG-008`'s `artifact_absence_statement`, carried into `EXP-SDEG-f7faa8` and
into the Red Team's OBJ-3 and this session's own PR text, says no claim in it is
bound to a reproducible receipt and that 7,110 survives only via transcript and
the unreachable branch `d1d36dd`. **That is wrong on the committed tree.**
`experiments/EXP-SIG-008/` contains:

- `work/null_rank6/state.json` — `tag: null_n12_s2`, `nrows: 183312`,
  `ncols: 174033`, `next_col: 174033`, `rank_acc: 149410`, `done: true`,
  `secs_total: 1182.6`, 22 carry files each with a distinct `sha256`.
- `runs/RUN-EXP-SIG-008-n/raw.json` — `seed: 2`, `status: completed_valid`,
  `sr_pred: 156520`, `rank: 149410`, `deficit: 7110`, `extra: 7110`.
- `runs/RUN-EXP-SIG-008-n/stdout.txt` — `rank6 null: completed_valid
  rank_acc=149410 cols=174033/174033 work=1183s`.

Integrity checks run here, all passing:

- 11 units, **contiguous** `0 → 174,033`, covering `ncols` exactly once;
- `Σ(unit k) = 149,410` = reported `rank_acc`;
- `Σ(carry npiv) = 149,410` — a **second, independent decomposition** agreeing;
- 22 distinct carry `sha256` values.

The Red Team flagged this same `raw.json` as uncited (its NON-BLOCKING OBJ),
which was correct; the stronger statement is that the receipt exists, is
internally consistent under two independent pivot decompositions, and reproduces
`nrows`/`ncols` that this control derived independently from the system itself.

### C-3. `EXP-SIG-008/summary.json` contradicts its own completed run

`summary.json` records `gate1_null_D6_baseline.status:
censored_budget_checkpointed` with `checkpoint.next_col: 138000`,
`rank_acc: 124719`, `fraction: 0.793`, `cumulative_prefix_shortfall: 13281`. The
`state.json` in the same experiment directory records `next_col: 174033`,
`rank_acc: 149410`, `done: true`, and the unit trajectory passes straight through
138,000 (`rank_acc` 124,719 at that boundary, matching the summary exactly)
before continuing to completion. **`summary.json` is a stale mid-run snapshot
that was never refreshed**, and its `censored` status is contradicted by the
completed state beside it. It also carries `dirty_tree: true`.

Anyone reading `summary.json` alone would conclude the D6 null baseline was never
finished. That is how the provenance in C-2 came to be mis-stated in both
directions.

## What this does NOT establish

- **Builder identity is UNRESOLVED.** Only seed 2 (the SIG lineage) has a
  committed system artifact here. Nothing in this control touches seed 2026, so
  the two unreconciled n=12 readings (174,033/16,018 vs 174,035/16,016) remain
  unexplained and `HEUR-BF-1` remains untestable on that pair.
- **`EXP-SDEG-f7faa8` is not approved and is not repaired.** Blocking defects
  B1, B2, B4, B5 are untouched; B3 is discharged at D=6 only.
- **Nothing about the D6 mechanism.** The 7,110 deficit is still unexplained; Φ
  is still refuted for the whole partial-sum lattice by `DEC-20260805-cc2b32`.
- **No transfer.** Boolean systems are not prime-field systems; `KN-OPEN-002`
  untouched, no exponent moved, `sota_delta` zero, Pollard rho remains the ECDLP
  baseline.

## Reproduction

Pure Python 3, no dependencies beyond the standard library, seconds to run.
Input: `experiments/EXP-SIG-008/work/n1_ms.json` (committed). Method as stated
above; `int.bit_count` for degree, bitwise OR for monomial product,
`itertools.combinations` over the 24 variables for multipliers.
