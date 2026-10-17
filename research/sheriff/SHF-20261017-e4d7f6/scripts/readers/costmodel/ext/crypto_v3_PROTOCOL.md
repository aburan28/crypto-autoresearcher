# The rule's comparison at baseline v3

**Declared in R07's results pull request, before any run below.** R07's
protocol
([`../../rounds/R07-main-head/PROTOCOL.md`](../../rounds/R07-main-head/PROTOCOL.md))
says that if R07 accepts v3, the rule's comparison runs at v3 under rule
v2's protocol with v3's binary, declared here as `rule/v3`.

**Rule v2 never ran.** It was declared for v2
([`../v2/PROTOCOL.md`](../v2/PROTOCOL.md)). R07 moved the programme to
main's head first, so rule v2 stays on record unrun, superseded by this
comparison.

**Everything rule v2 declared holds here, except the rows under "What
changes".** That covers:
- §23's sizes, rows, arms, retries and stop rule;
- the claims and the reading, and the inadmissible list;
- the native tools (`icprog rule`, `isolated_bench`);
- `icprog`'s oracle as the replay's checker;
- the pin against §23's `T01-R1`, and each row's logarithms checked
  against §23's row;
- the reference check against the strong rho;
- the accounting, class and non-claims.

## Question

IC_TOOL_PROGRAM.md asks, at every new baseline, for the rule's
comparison: one unseen public point, the index calculus against Pollard
rho on that same point, online and cold. It runs at §23's six sizes with
64 targets, as §23 did, and it moves the scoreboard's §23 row.

**v3 is the baseline R07 made:** main's `995ea207`, binary
`9c3320390d74ae48b74382d2ec3f8b4b5b1585e5e8aa2448c0d78369807a26b4`.

## What changes from rule v2

- **The binary** is v3's: the one R07 measured, built from
  `995ea2071cc7453877a503d30eb561ae82cddab9`. It does not embed its commit,
  so the runner is given it (`--ic-commit`), as R07's runner was.
- **The arms' sources are still §23's list.** Main changed five of them
  after v2 (`koblitz_index_calculus.rs`, `koblitz_fast.rs`,
  `semaev_decomp.rs`, `ic_measurement.rs` and `ic_boundary.rs`) and
  added no file the arms run. The candidate IDs are new, as they should
  be.
- **The strong rho is v3's own.** `koblitz_rho_fixture` is built from the
  same commit (binary `36ba84d5…`). Main changed the walk under it after N3 (#1334, #1360:
  `koblitz_strong_rho.rs`, width-generic), so its per-step cost is
  measured afresh. The example itself gained only a `peak_rss_bytes`
  field in its report.
- **What each size is read against:** §23's measurement of the same
  figure, under the key `s23_then_v3`.
- **The host** is this container, kernel build `6.18.44-fc-v70`, the
  host of R07's runs. Its manifest is `runs/host.json`.

## Cost, as an estimate

v3's set-up is 1.05–1.54 times faster than v2's at the top sizes (R07's
diagnostic; R07's own figures supersede it), so the 408 rows take under
an hour. The reference check's 48 walks take minutes.

## Commands

    icprog rule all --comparison v3 --ic <v3 ic> --ic-commit 995ea2071cc7453877a503d30eb561ae82cddab9 --isolate <isolated_bench>
    icprog rule reference --comparison v3 --fixture <koblitz_rho_fixture> --fixture-commit 995ea2071cc7453877a503d30eb561ae82cddab9 --isolate <isolated_bench>
    icprog rule claims --comparison v3
    icprog rule analyse --comparison v3 > research/ic_tool_program/rule/v3/analysis.json
