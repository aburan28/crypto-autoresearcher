# The rule's comparison at baseline v3: results

**What this is.** The single-target comparison that the plan owes at every
new baseline (`research/notes/index-calculus/IC_TOOL_PROGRAM.md` §5),
run at v3, main's `995ea207`, under [`PROTOCOL.md`](PROTOCOL.md):
- one unseen public point a process, the index calculus against Pollard
  rho on that same point, online and cold;
- at ledger §23's six sizes, with §23's 64 targets and four A/A repeats a
  size;
- each row read against §23's.

It ran on 2026-10-06 from 08:29 to 09:42 UTC, on the host of R07's runs:
`Intel(R) Xeon(R) Processor @ 2.10GHz`, kernel build `6.18.44-fc-v70`,
the programme's reference class ([`runs/host.json`](runs/host.json)).

**The verdict is §23's.** Online, the index calculus is faster than rho on
the same point at all six sizes. Cold, with its reusable set-up, rho is
faster at all six. By AGENTS.md §2 the method is not faster than rho.

## What ran, and what it checked

- **408 rows, 408 checked.** Each size ran its 64 targets once (`R1`) and
  four of them again (`R2`, the A/A). Every row passes the repository's
  `vs_rho` claim check (`claims/summary.json`).
- **Every process was clean.** None was contended, none failed, and none
  was retried.
- **Every logarithm is §23's.** At every size, all 68 rows recovered the
  logarithms §23's rows did, for both arms, on the same targets.
- **The pin held:** v3's outputs on `T01` at each size equal §23's
  ([`runs/pin/`](runs/pin/)).
- **The reference check is admissible at every size.** The comparison's
  rho must be no slower per step than the strong walk
  (`koblitz_rho_fixture strong`, v3's own build) on the same public
  targets. It runs at 0.50–0.62 times the strong walk's time a step
  ([`runs/reference/`](runs/reference/)).

## Results

Each figure is v3's, with §23's beside it. **Online speedup** is mean rho
online over mean index-calculus online, with a 95% bootstrap interval over
the 64 targets. **Cold** is set-up plus online, index calculus over rho,
so above 1 rho is faster. **Break-even** is the number of targets at
which one set-up and their descents cost as much as as many one-target
rho runs.

| curve | `log₂ r` | online speedup [95%] | §23 | cold, IC over rho [95%] | §23 | break-even | §23 |
|:--|--:|:--|--:|:--|--:|--:|--:|
| `icv1-f2m47-t22705043-f4e44623` | 36.6 | **10.2×** [8.1, 13.1] | 9.77× | **5.23×** [4.80, 5.72] | 4.95× | 7.4 | 7 |
| `icv1-f2m57-tm747311035-c1f545af` | 38.0 | **16.3×** [13.0, 20.8] | 13.5× | **6.12×** [5.66, 6.67] | 1.98× | 8.8 | 15 |
| `icv1-f2m41-tm2308219-7f48b14a` | 39.0 | **10.9×** [8.6, 14.2] | 9.38× | **7.66×** [6.90, 8.61] | 8.04× | 9.2 | 10 |
| `icv1-f2m53-tm56619371-dac20a85` | 44.3 | **21.5×** [16.9, 27.6] | 17.5× | **13.2×** [11.8, 15.0] | 14.7× | 14.4 | 16 |
| `icv1-f2m59-tm943548413-98844ecc` | 44.5 | **26.5×** [20.5, 34.5] | 16.9× | **12.0×** [10.6, 13.9] | 15.7× | 13.0 | 18 |
| `icv1-f2m61-t158598901-ab42b6c5` | 47.2 | **14.8×** [11.3, 19.8] | 8.84× | **21.0×** [18.6, 23.8] | 31.6× | 22.8 | 37 |

- **Rho priced at the canonical step,** the conservative reading, makes
  the online speedup 4.55–13.3× (§23: 4.34–9.37×).
- **Against Bernstein and Lange's trade-off,** a model of a generic walk
  given the same set-up as precomputation, the index calculus's online
  cost is 1.42–3.52 times that walk's (§23: 2.0–8.0×).
- **Every target's online speedup is above 1,** at every size.
- **In the progress chart's direction,** index calculus over rho, the
  online cost is 0.038–0.098 of rho's, the reciprocals of the speedups
  above: 0.0377 [0.0290, 0.0487] at `2^44.5`, the closest size.
- **The A/A:** a target's second process over its first reads 0.63–1.60
  in online speedup. The online interval is short and noisy, which is why
  only the 64-target means are read.

## Reading

- **Online, the index calculus gains on rho at every size:** 10.2–26.5×
  against §23's 8.8–17.5×. Its online interval, the target's descent and
  its lookups, gained more since §23 than rho's walk did.
- **Cold, the gap narrows at the three largest sizes:** from 14.7, 15.7
  and 31.6× to 13.2, 12.0 and 21.0×. The set-up there is what R05's filter
  and main's two-fold reduction (#1242) made cheaper (R07).
- **At `2^38.0` the cold ratio rises, from 1.98 to 6.12×.** That is not a
  regression of the method.
  - §23's figure was low because both arms paid a 48–58 ms curve
    construction, longer than rho's walk. §23 itself read 6.3–32.5×
    without it.
  - R03 (v1) made that construction 1.28 ms, so rho's cold time there is
    now its walk.
- **At `2^36.6` and `2^39.0` the cold ratio barely moves,** 4.95 → 5.23
  and 8.04 → 7.66×: both arms gained there.
- **The gap to rho still grows with the size.** Fitted over the six
  sizes, the cold ratio grows as `r^0.18` [0.14, 0.21]. §23's fit,
  `r^0.30`, included the construction-bound point at `2^38.0`, so the two
  exponents are not like for like.
- **`S` is not compared with §23's.** The analysis reports each figure's
  `S` in its own process's unit, its batched addition (`unit_ns`).
  - That unit is 2.3–3.2 times cheaper at v3: 9.0–11.1 ns in v3's
    processes against 24–36 ns in §23's, at the same sizes.
  - So v3's set-up reads 9.4–24.9 in its unit against §23's 4.2–15.1,
    while its wall time fell.
  - The plan quotes `S` across baselines in v0's unit (§5). The ratios
    above need no unit.

**Class: accounting.** No algorithm changed in the comparison itself. It
re-measures the rule at the newest baseline, so the scoreboard's §23
figures move to v3's, with §23's kept beside them.

## Files

| file | what it is |
|:--|:--|
| [`PROTOCOL.md`](PROTOCOL.md) | the declaration, before any run (#1414) |
| [`analysis.json`](analysis.json) | every figure above: `icprog rule analyse --comparison v3` |
| `runs/` | the host manifest, the pin, each target's processes (report, isolation record, stderr), the reference check's walks, and the run's logs |
| `claims/` | each row's `vs_rho` claim and its independent replay; `claims/summary.json` counts the checker's verdicts |
| `manifests/` | the candidate, workload and rho manifests the claims cite |

The claims point at their runs by path, so the tree is committed as it
ran, with one exception. The pin's six reports were written under each
size's old directory stem. They are committed under their curves' slugs,
as AGENTS.md §11 requires of new files, with their contents unchanged;
nothing reads them by name, and `icprog rule pin` now writes the slug.
`tests/icprog.rs` checks that `icprog rule analyse --comparison v3`
writes [`analysis.json`](analysis.json) again, byte for byte.

**The commands that ran,** from the protocol, with v3's `ic` and the
strong rho fixture built from `995ea2071cc7453877a503d30eb561ae82cddab9`
(binaries `9c332039…` and `36ba84d5…`):

    icprog rule all --comparison v3 --ic <v3 ic> --ic-commit 995ea2071cc7453877a503d30eb561ae82cddab9 --isolate <isolated_bench>
    icprog rule reference --comparison v3 --fixture <koblitz_rho_fixture> --fixture-commit 995ea2071cc7453877a503d30eb561ae82cddab9 --isolate <isolated_bench>
    icprog rule claims --comparison v3
    icprog rule analyse --comparison v3 > research/ic_tool_program/rule/v3/analysis.json
