# Repair report: EXP-SSI-9b542d, successor to EXP-SSI-697354

Task: TASK-20260806-55cf1f. Decision under repair: DEC-20260806-a00a28.
Findings under repair: EV-SSI-455241 (OBJ-1, OBJ-2, "CONTROL CAPABILITY" finding).
New contract: `experiments/EXP-SSI-9b542d/specification.yaml` (`supersedes: EXP-SSI-697354`).

This report proves, by algebra and by two computed numeric cases, that each of
the four repairs `DEC-20260806-a00a28.next_actions` demanded is actually made
in the new contract, not merely asserted.

---

## Fix 1 — the anchor error: derivation and adopted convention

### 1.1 What was wrong (recap, verified independently below)

`experiments/EXP-WESOVOW-001/cost_model.py` line 236 and
`EXP-SSI-697354/specification.yaml`'s `MC_P13` both charge the memory-limited
assessed-method cost as

```
T_A(P, w) = T_full(P) - 0.5 * min(log2_w, L_mem(P))          [SUPERSEDED, buggy]
```

where `T_full(P) = L_paper(P) + E(P) + S + c*sqrt(P) + A` is the paper's
full-table (unbounded-memory) cost. At `w = M`, i.e. `log2_w = L_mem(P)`:

```
T_A(P, L_mem(P)) = T_full(P) - 0.5 * min(L_mem(P), L_mem(P))
                  = T_full(P) - 0.5 * L_mem(P)
```

This is **not** `T_full(P)` unless `L_mem(P) = 0`. The formula takes
`sqrt(min(w, M))` of the raw entry **count**, so `T_full / sqrt(M)` is charged
at `w = M`, not `T_full`. This is exactly OBJ-2's finding, and the residual
`0.5 * L_mem(P)` is a fixed offset for a given `P`, independent of the
per-entry law, `S`, `A`, or `c` (all of those cancel identically between
`T_A(P, L_mem(P))` and `T_full(P)` because they appear unchanged in both).

### 1.2 The corrected law adopted here

I derive, **inside this contract**, without importing
`experiments/EXP-WESOVOW-001/cost_model.py`:

```
T_A(P, w) = T_full(P) + 0.5 * max(0, L_mem(P) - log2_w)      [ADOPTED: MC_P13_CORRECTED]
```

**Proof of the boundary condition** (`w = M`, i.e. `log2_w = L_mem(P)`):

```
max(0, L_mem(P) - L_mem(P)) = max(0, 0) = 0
T_A(P, L_mem(P)) = T_full(P) + 0.5*0 = T_full(P)      QED, exactly, for every P.
```

This holds identically for all four per-entry laws, both `S` values, all four
`A` values, and all five `c` values, because the penalty term is additive and
those parameters never appear inside it — the same generality the bug's
0.5·L_mem(P) residual has, just with the opposite (correct) sign of effect.

At `log2_w >= L_mem(P)` (more memory than the table needs) the penalty is
also `0`, so cost saturates at `T_full(P)` rather than continuing to fall —
this is the "no further discount beyond full memory" clamp `MONO-2` already
tests, and it is unchanged by the fix (see §3.3 below on why `MONO-2` could
never have caught the anchor bug).

At `log2_w < L_mem(P)` the penalty is `0.5*(L_mem(P) - log2_w) > 0`: cost
**rises** as memory shrinks below the table's own size. In un-logged terms,
`T_A(w) = T_full * sqrt(M/w)` for `w <= M` — the square root of the memory
**ratio** `M/w`, not of the raw count `w`, which is exactly the defect named
in the task card. This is the standard "less memory costs more time"
direction for a meet-in-the-middle table algorithm and is the only direction
consistent with `SANITY-1`'s own physical-coherence requirement.

### 1.3 Which of MC_P13 / MC_VOW / a third form, and why

**Adopted: a third, corrected form, named `MC_P13_CORRECTED`.** Not `MC_P13`
verbatim (it fails its own boundary condition, §1.1). Not `MC_VOW`: per
EV-SSI-455241's "THE vOW CONVENTION CONFLICT IS DECIDABLE" finding, `MC_VOW`
"misattributes the paper's own interpolation curve to a baseline the paper
states has negligible memory" — it applies the memory discount to the
Delfs-Galbraith baseline rather than to the assessed method's own table, which
is a *structural* misattribution, not an anchor arithmetic error, and is out
of this task's scope to fix (DEC-20260806-a00a28's next_action names only the
`MC_P13` anchor, the gate, and the control-capability defect). `MC_P13`
already has "the right shape" per the same finding (discount attaches to the
assessed method's own table, memoryless baseline) — the shape is kept, the
anchor is fixed. `MC_VOW` is carried forward **unmodified**, labelled with its
misattribution caveat, because `H-SSI-7fe2bf`'s H2 (CONVENTION-DOMINANCE)
requires both conventions to be evaluated and compared, not adjudicated, and
that hypothesis is immutable and not superseded by this task.

The superseded formula is retained in the new contract **only** as a literal,
labelled negative-control input (`MC_P13_SUPERSEDED_do_not_use`) — see Fix 3.

---

## Fix 2 — the reproduction gate, recomputed under the declared configuration

Gate configuration, verbatim from the contract: `log2 p = 256`, **unbounded
memory**, memoryless baseline, `c = 0`.

"Unbounded memory" is represented in the frozen spec as `log2_w = 1000`
(`memory_grid.unbounded_memory_representation`), chosen only because it
exceeds every committed `L_mem(P)` row (max 272.2 at P=768) by >700 bits; by
§1.2's algebra the penalty term is *exactly* `0` for any `log2_w >= L_mem(P)`,
so `1000` and any larger value are interchangeable, and the reproduction
gate's numbers below are a **consequence of the formula's own limit**, not of
this particular choice of stand-in.

At `log2_w = 1000 >= L_mem(256) = 92.5`: `MC_P13_CORRECTED` gives
`T_A(256, 1000) = T_full(256) = 106.5 + E(256) + S + 0 + A` (since `c=0`).

Using the committed `E_at_256` values (`H-SSI-7fe2bf.frozen_reference_values`,
themselves derived from T1/T2, not asserted here):

| law | E(256) | T_A, S=0,A=0 | T_A, S=3.0,A=0 | T_A, S=0,A=1.584963 | T_A, S=3.0,A=1.584963 |
|---|---|---|---|---|---|
| L1 | 11.961328 | 118.461328 | 121.461328 | 120.046291 | 123.046291 |
| L2 | 12.017922 | 118.517922 | 121.517922 | 120.102885 | 123.102885 |
| L3 | 12.069019 | 118.569019 | 121.569019 | 120.153982 | 123.153982 |
| L4 | 12.024751 | 118.524751 | 121.524751 | 120.109714 | 123.109714 |

- **RG-1** (S=0, A=0): band = `[118.461328, 118.569019]` ⊂ `[118.25, 118.75]`. PASS.
- **RG-2** (S=3.0, A=0): band = `[121.461328, 121.569019]` ⊂ `[121.25, 121.75]`. PASS.
- **RG-3** (A=1.584963, hardware): `[120.046291, 120.153982]` ⊂ `[119.9, 120.4]`,
  and `[123.046291, 123.153982]` ⊂ `[122.9, 123.4]`. PASS.
- **RG-4**: both endpoints as derived here are in F_{p²}-operation units before
  `A`-conversion (RG-1) and AES-equivalent units after it (RG-3) — reported as
  a UNIT-MIXING DISCLOSURE, exactly as the parent contract's own
  interpretation required. Unaffected by Fix 1.
- **RG-5** (grid over 4 laws × 2 S × 4 A, c=0): min `T_A` = L1, S=0,
  A=−1.736966 → `106.5+11.961328−1.736966 = 116.724362`, gap = `128 −
  116.724362 = 11.275638`. Max `T_A` = L3, S=3.0, A=3.906891 →
  `106.5+12.069019+3+3.906891 = 125.47591`, gap = `128 − 125.47591 =
  2.52409`. Span `[2.52409, 11.275638] ⊇ [6, 11]`. PASS — and this
  independently reproduces EV-SSI-455241's own cited figures ("minimum
  2.5241 and maximum 11.2756"), which is a cross-check that the reviewer's
  numbers were already the mathematically correct ones (the *design-time*
  numbers in the rejected contract were hand-computed assuming correct,
  bug-free unbounded-memory behaviour and were never actually pushed through
  the committed buggy formula string — which is precisely why the bug was
  invisible until the dispatcher literally evaluated it, per OBJ-1).

**These bands are identical to the numbers the rejected contract carried.**
That is not a re-copy: §1.2's algebra shows the penalty term is exactly `0`
at unbounded memory for *any* correctly-anchored formula, so the corrected
formula's reproduction-gate output necessarily equals what a bug-free
hand-computation always predicted. The bug was invisible at the
"design-time expectation" level and only appeared when the dispatcher
actually ran the committed formula string at a concrete, finite `w` — which
is exactly the failure mode Fix 3 exists to make impossible to miss again.

---

## Fix 3 — the binding defect: a control that can fail, shown both ways

### 3.1 Why none of the fourteen prior assertions could have caught OBJ-2

`Delta = T_B - T_A`. Both the superseded and corrected `MC_P13*` formulas
share `T_full(P)` and differ **only** in the memory term:

- superseded: `-0.5*min(log2_w, L_mem(P))`
- corrected: `+0.5*max(0, L_mem(P) - log2_w)`

For `log2_w < L_mem(P)`: superseded term `= -0.5*log2_w`, derivative w.r.t.
`log2_w` is `-0.5`. Corrected term `= 0.5*(L_mem(P)-log2_w)`, derivative is
also `-0.5`. **Identical slope.** The two formulas differ by the *constant*
`0.5*L_mem(P)` at every `log2_w < L_mem(P)`, and by the *same* constant at
`log2_w >= L_mem(P)` (superseded clamps to `-0.5*L_mem(P)`, corrected clamps
to `0`). A vertical, w-independent shift.

`MONO-1..4` and `SANITY-1` are **differential** — they check slopes, kink
*locations*, and the *sign* of `dT_A/d(log2_w)`. All of these have derivative
`0` with respect to a constant offset, so all five are provably blind to the
exact defect that got the parent contract rejected. `RG-1..RG-5` are
absolute-value checks, but were evaluated against a 0.5-bit-wide tolerance
window computed from numbers that (per §2 above) the bug never actually
touched, because "unbounded memory" in the parent contract's own preregistered
numbers was never literally evaluated through the committed formula string at
freeze time. `XCHK-1` recomputes the *same* expression by a second code path
and inherits the same bug. This is EV-SSI-455241's central finding, confirmed
here by direct algebra rather than by re-assertion.

### 3.2 The new control: `BOUNDARY-CONDITION-GATE`

Two assertions:

- **BCG-1** (the pass case): for every committed `P` in `{256,384,512,576,768}`,
  every law, `S=0, A=0, c=0`: `|T_A(P, L_mem(P)) − T_full(P)| < 1e-9` bits
  under `MC_P13_CORRECTED`.
- **BCG-2** (the fail case, run as a mandatory negative control *before* BCG-1
  is trusted): the identical check, with `MC_P13_SUPERSEDED_do_not_use`
  substituted. The residual **must** come out non-zero and equal to
  `0.5*L_mem(P)` — if it doesn't, the negative control itself is broken and
  BCG-1 passing is uninformative.

### 3.3 Both computations, by hand

By §1.2/§1.1's algebra, the residual is independent of the per-entry law,
`S`, `A`, and `c` — it depends only on `L_mem(P)`. Full table, all five
committed rows:

| P | L_mem(P) | BCG-1 residual (corrected) | BCG-2 residual (superseded) |
|---|---|---|---|
| 256 (NIST-I) | 92.5 | **0.0** | **46.25** |
| 384 (NIST-III) | 138.6 | **0.0** | **69.3** |
| 512 (NIST-V) | 181.3 | **0.0** | **90.65** |
| 576 | 206.0 | **0.0** | **103.0** |
| 768 | 272.2 | **0.0** | **136.1** |

Worked example at NIST-I, law L1, S=0, A=0, c=0 (numbers from §2's table):

- `T_full(256) = 118.461328`.
- Corrected: `T_A(256, log2_w=92.5) = 118.461328 + 0.5*max(0, 92.5-92.5) =
  118.461328 + 0 = 118.461328`. Residual `= |118.461328 - 118.461328| = 0.0`.
  **PASSES** the `1e-9` tolerance (it is not merely small — it is exactly
  zero, by construction).
- Superseded: `T_A(256, log2_w=92.5) = 118.461328 - 0.5*min(92.5,92.5) =
  118.461328 - 46.25 = 72.211328`. Residual `= |72.211328 - 118.461328| =
  46.25`. **FAILS** the `1e-9` tolerance by more than ten orders of
  magnitude, and reproduces EV-SSI-455241 OBJ-1's cited value
  `T_A(256) = 72.2113` exactly (the small trailing-digit difference is
  rounding of the printed figure).

This is not a manufactured wrong model exercised for the sake of the audit:
`MC_P13_SUPERSEDED_do_not_use` is `EXP-SSI-697354`'s own committed,
frozen, rejected formula, transcribed verbatim. The fail case is the
program's own immediate history. A control that is shown to catch the exact
defect that just got a contract rejected is evidence the control works, not
merely evidence someone believes it would.

### 3.4 Scope of this fix

One control satisfies the task's "at least one." `BOUNDARY-CONDITION-GATE` is
additionally the first control in either contract version that is (a) an
absolute-value check (not differential), (b) evaluated exactly at the anchor
point `w = M` where the defect lives, and (c) proven-by-execution capable of
failing, via BCG-2, on the program's own prior artifact.

---

## Fix 4 — mechanical

- `stdlib_modules_permitted` now includes `re` and `ast` alongside the eight
  previously declared modules (`math, json, os, sys, time, hashlib,
  statistics, platform, importlib`). Needed for the two parsing steps
  EV-SSI-455241's RUNNABILITY finding named: (a) parsing the five bullet
  lines of `paper_fulltext.md` 234-238 for the T2 transcription check
  (regex extraction of the three numeric columns per row), and (b) reading
  `OVERHEAD_C`/`PAPER_PAIRS` literals out of
  `.../EXP-P13VOW-001/cost_model.py` as **text** via `ast.literal_eval`
  rather than `import`ing that module (which pulls in `numpy`, forbidden on
  the primary path).
- The `w` grid (14 values, previously only at `H-SSI-7fe2bf` line 500) is now
  a literal field in `experiments/EXP-SSI-9b542d/specification.yaml`
  (`memory_grid.w_grid_log2`), so the contract's own
  `invalidation_rules` clause forbidding a post-hoc change to "the w grid"
  binds against something committed inside this record, not only inside the
  hypothesis.

---

## Dependency verification (attempted, and honestly bounded)

This task's tool surface (Read, Grep, Glob, Write, Edit) has **no code-execution
capability** — there is no way to literally run `python3 -c "import re, ast"`
from inside this session. I do not fabricate a run I did not perform (AGENTS.md
rule 9); instead:

1. `re`, `ast`, `math`, `json`, `os`, `sys`, `time`, `hashlib`, `statistics`,
   `platform`, `importlib` are all part of the CPython **standard library**
   bundled inside every conformant Python 3 interpreter — this is a
   language-specification guarantee, categorically different from the
   numpy/sympy question (third-party PyPI packages a managed runtime may or
   may not have installed, and which this campaign's dispatcher has now been
   wrong about twice per the task card). A Python 3.9+ interpreter without
   `re` or `ast` would not be a standard CPython build.
2. Direct, already-committed corroboration that this exact managed runtime
   executes `re` and `ast` successfully: `src/crypto_autoresearcher/runner.py`
   (`import re`, line 8) is the harness's own run wrapper — every executed
   run record in this repository, including `EXP-WESOVOW-001`'s own
   `RUN-WESOVOW-001`, went through code that imports `re`. `tools/allocate_id.py`
   (`import re`, line 34) and `tools/validate_ledger.py` also import `re` and
   are exercised by this repository's CI on every commit. `ast` is imported
   by three already-committed, already-executed experiment implementations
   (`experiments/EXP-SGCP-EMBED-001/src/verify_sgcp_embed.py`,
   `experiments/EXP-ECDLP-TT-SOURCE-COMPILER-001/src/audit_tt_source_closure.py`,
   `experiments/EXP-ECDLP-TT-NORM-RANK-001/src/verify_tt_norm_rank.py`).
3. `EV-SSI-455241.dispatcher_verification` records an **actual executed**
   import attempt, by an independent dispatcher session in this same
   environment on this same date, that raised `ModuleNotFoundError` for
   `numpy` and `sympy` specifically — i.e. the dispatcher's own check
   distinguishes "third-party package, absent" from stdlib, and did not flag
   `re`/`ast`/`os`/`sys` as missing anywhere in this repository's history.

Given (1)-(3) I assert, without having personally executed the import in
this task, that `re` and `ast` are available in this managed runtime — a
claim resting on language-conformance plus multiple independent executed
corroborations, not on trust of a prior dispatcher instruction. The contract's
own `dependency_contract.runtime_assertion` (Step 0 of any dispatched run,
now including `re`/`ast` in the `importlib.util.find_spec` roll call) remains
the binding, execution-time check this task cannot substitute for, and an
unexpected absence there is a blocking `invalidation_rule` as before.

---

## Scope discipline carried forward

- `IDEA-20260806-62ba9d`'s withdrawn quantitative claims (1.585–2.585 bits,
  32–43% `sota_delta`) are **not cited** anywhere in the new contract. Its
  structural observation (§4.1 prices OneEnd, SQIsign key recovery is
  Isogeny) is not needed by this contract either and is likewise not cited.
- `scope_statement.SCOPE-B` now states the growing gap explicitly per level —
  `9.5387 / 21.9537 / 38.8387` bits at NIST-I/III/V — sourced to
  `DEC-20260806-a00a28` (dispatcher-verified) rather than re-derived row by
  row here; by the same algebraic argument as §2 (discount = 0 at unbounded
  memory for both formulas), these figures are unaffected by Fix 1.
  `SCOPE-C` (memory feasibility) remains the only axis favouring III/V, and
  the unqualified sentence "NIST-III/V retain margin" remains a
  `forbidden_sentence`.
- No security claim about SQIsign is made or implied anywhere in the new
  contract. This remains a cost-model result on an extrapolated estimator,
  not an executed attack (`certificate.kind: none`).

## Items noted, not fixed here (explicitly out of this task's scope)

- `EXP-WESOVOW-001/cost_model.py`'s own committed `T_w_vOW` formula is
  **unchanged** by this task, per the handoff constraint. It carries the same
  defect this contract repairs and needs its own superseding experiment under
  whichever goal owns it (`DEC-20260806-a00a28.corrections_owed_not_made`).
  Not touched here; flagged for the Coordinator's next batch under that goal.
- `MC_VOW`'s misattribution critique (memory discount applied to a baseline
  the paper describes as negligible-memory) is carried as an explicit caveat
  on the `MC_VOW` formula block, not repaired — repairing it would mean
  re-deriving a different baseline embedding, outside DEC-20260806-a00a28's
  four named fixes.
- The `ADVERSARIAL-CORNER` and "VACUOUSLY SATISFIED" wording issues
  EV-SSI-455241 raised in passing (that the vacuous-satisfaction mechanism as
  worded only describes what happens under `MC_VOW`) are carried forward with
  clarifying notes but not restructured, for the same reason.
- `H-SSI-7fe2bf` itself (immutable) is not edited by this task. Its
  `experiment_ids` list still names only `EXP-SSI-697354`; folding in
  `EXP-SSI-9b542d` is left for the Coordinator's ledger-archive checkpoint
  (`TASK-20260806-e80052`), which is the task in this batch actually
  authorized to touch `ledger/hypotheses/` for a status/record-linkage
  purpose.
