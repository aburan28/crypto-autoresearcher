# R-LWE / M-LWE lane — staging, 2026-08-06 (**revision 2**)

**Nothing in this directory is a ledger record.** These are drafts produced by a
top-level session at the user's request. Per AGENTS.md rule 1 only the
Coordinator mints research questions, approves experiments, or changes
hypothesis status; per rule 7 nothing is official until it is committed through
a verified ledger archive.

> ## ⚠ Revision 1 was pressure-tested and did not survive intact
>
> 11 independent agents checked 7 claim clusters by exact computation and
> screened 3 prior-art lanes. **All 7 came back partially wrong.** The structural
> algebra held — several parts are *stronger* than revision 1 argued — but every
> headline number a downstream Executor would have acted on was wrong, and two
> were wrong in the direction that inverts the conclusion.
>
> **Read `rlwe-pressure-test-report.md` before trusting anything here.** All
> blocking corrections are applied to the drafts in this directory; the report
> lists 39 numbered edits, of which the 12 blocking ones are done.
>
> Three things that must not be lost:
> 1. **The κ-surface is two-dimensional `(κ, β_c)`.** Revision 1's one-parameter
>    form omitted the cost of *producing* `c` and reports that subring descent
>    **beats** the primal attack at FHE parameters. It was a false-positive
>    generator aimed at deployed parameter sets.
> 2. **ML-KEM sits 0.205 bits BELOW the concrete NTRU fatigue point**
>    (`0.004·n^2.484`), not 8 bits above. Revision 1's scoping claim was wrong
>    *and* was a rule-4 violation.
> 3. **M8 was closed for a false reason** and is reopened. Its closure argument
>    dropped the shortness constraint on `s` and, if true, would have implied
>    `m = 1` R-LWE is trivially broken.
>
> **Correction to this program's recorded network status:** eprint HTML and
> `/search` return **HTTP 200**; only PDFs 403 behind Cloudflare. The
> **WebSearch/WebFetch tools are hard-broken** with a model-availability error —
> not a network block. Earlier "eprint unreachable" verdicts across this program
> (including in RQ-FHE-001) may be misattributed tool failures and are worth
> re-testing.

## Contents

| file | what it is |
|---|---|
| `PORTFOLIO.md` | the substance: nine mechanisms, ranked, with ceilings and kill-tests |
| `RQ-RLWE-be8f64.draft.yaml` | question — overstretched R-LWE / dense-submodule transfer |
| `RQ-RLWE-fe4e1f.draft.yaml` | question — weak instances over `a`, and the smoothing instrument |
| `RQ-RLWE-912fdb.draft.yaml` | question — the κ-curve and the Arora–Ge rank deficit |
| `GOAL-RLWE-001.draft.yaml` | goal — measure whether DSD fires for R-LWE (NTRU positive control) |
| `GOAL-RLWE-002.draft.yaml` | goal — weak-instance tail + decidable weak-parameter test |
| `GOAL-RLWE-003.draft.yaml` | goal — κ-curve + Arora–Ge; **cheapest, schedule first** |
| `proposals.draft.yaml` | nine idea records (M1–M9), one of which is closed on arrival |

## Identifiers

All IDs were allocated with `tools/allocate_id.py` and verified free on
2026-08-06. `GOAL-*` has no enforced pattern in `validate_ledger.ID_PATTERNS`,
so `GOAL-RLWE-001/002/003` follow the existing `GOAL-MLKEM-00N` convention.
**Re-check every ID with `--check` before minting** — this directory has sat
uncommitted and another worktree may have claimed one.

## How to promote

1. Coordinator reviews `PORTFOLIO.md` and decides which lanes open.
2. `--check` the IDs, then copy the accepted drafts to `ledger/questions/`,
   `ledger/goals/`, `ledger/proposals/` (splitting `proposals.draft.yaml` into
   one file per idea), dropping the `# STAGING DRAFT` headers.
3. `python3 tools/validate_ledger.py` before committing.
4. `/coordinate-research-goal` on the goal that opens first.

## Scheduling, if only one thing runs

**`GOAL-RLWE-003`, M9 (Arora–Ge).** Its prediction is already *confirmed and
upgraded to a proof*: Galois acts as a signed permutation, the symmetric support
`[−B,B]` absorbs the sign, so conjugation returns the same polynomials — rank
increase exactly 0 from four independent sources, including short-multiplier
equations the first draft never considered. What remains is bookkeeping: fix
three numbers (`2^41.05` not `2^44`; **1536** equations not 768, since ML-KEM's
secret is CBD-bounded too; ML-KEM-512 is `η₁ = 3` ⟹ degree 7), and the
"deficit exactly `n`" sentence is already deleted. Closest thing here to a
finished result.

**`GOAL-RLWE-001` still does not start with code**, but its gate is now one
question rather than a reading list. FPS (2022/1203) and DvW (2021/999) are read
in full text from local disk; FPS turns out to *support* the goal rather than
collide with it. The live gate: **is Karenin–Kirshanova 2024/844 arbitrary-rank
or rank-2 only?** Its PDF is 403-blocked, so this needs an out-of-band copy or
the AfricaCrypt proceedings. Second question in the same gate: how does this
object differ from Ducas–Loyer 2025/1694's dense-sublattice *no-go*?

**Do not run `GOAL-RLWE-003`'s κ lane in its revision-1 form.** See the warning
above.

## Relationship to existing records

- **RQ-MLKEM-001** (mechanism search) — GOAL-MLKEM-001 closed at budget with no
  mechanism found. This lane differs in target: R-LWE/M-LWE as *problems*, not
  FIPS 203 as a scheme. Overlap should be declared, not avoided.
- **KN-OPEN-012 / KN-OPEN-026** — the umbrella questions this lane serves.
  M1 and M9 are new answers to KN-OPEN-012; the κ-curve is the KN-OPEN-019
  method applied to structured lattices.
- **KN-OPEN-016 / GOAL-MLKEM-004** — binding gate on the dual endpoint of the
  κ-curve. Do not build a ring-native dual attack on a score model this program
  has evidence to distrust.
- **GOAL-HAWK-001 / KN-OPEN-028** — same rank-2 module object (see the
  organizing claim in `PORTFOLIO.md`). Heuristic 4's failure is the most
  informative datum available for M7; coordinate, do not duplicate.
- **RQ-FHE-001** — M1's payoff regime overlaps its parameter sets. Coordinate.
- **KN-LIT-114 / KN-LIT-112** — the NTRU fatigue and subfield-attack entries M1
  builds on; both are already in the corpus.
