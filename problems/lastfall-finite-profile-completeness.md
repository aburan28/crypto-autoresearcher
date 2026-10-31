# Last fall degree needs a finite-profile completion certificate

- **Status:** `open`
- **Kind:** proof gap and implementation gap
- **Affected work:** [LastFall target](../formal/targets/lastfall-is-max-degree-fall.yaml), [research note](../research/THM_FALLDEG_INVARIANTS1.md), [independent review](../docs/reports/2026-10-31-lastfall-fidelity/synthesis.md), `IDEA-20260916-4b7c1e`
- **Next action owner:** Coordinator to select a concrete measured system and protocol
- **Last updated:** 2026-10-31

## Problem

A finite Macaulay rank profile cannot yet establish the global last fall degree `d_F`: the measured rows have not been bound to the iterative closure spaces `V_{F,i}`, and no certificate excludes falls beyond the measured cutoff. This blocks promoting a finite observed maximum to an exact invariant or a dashboard claim.

## Evidence and uncertainty

- **Observed:** The [blind review](../docs/reports/2026-10-31-lastfall-fidelity/blind/report.md) derives two systems `G_N` and `H_N` with identical `V_i` and ranks through any cutoff `B<N`, including an observed fall at degree 2, but with `d_(G_N)=2` and `d_(H_N)=N`. Its one-pass matrix control also shows that generator multiples alone can miss the iterative closure. These are mathematical controls, not measured experiment receipts.
- **Named historical candidate:** The [R35a publication and certificate replay](../docs/reports/2026-10-31-r35a-readback/README.md) matches all public assets to tracked hashes and freshly passes the pinned independent checker. It establishes `1 not in W_4` and a codimension lower bound of 5,287. Its receipt's `d_ref_exact` remains null. The dated correction forbids treating the dual certificate as exact dimension equality; unsatisfiability and the separate upper-bound steps have not been replayed in this audit.
- **Derived or proved:** The conditional greatest-fall theorem applies to the global set of all degree falls, given finite `d_F` and an existing fall. A witnessed fall at `D` gives `d_F>=D` under those hypotheses; a finite prefix alone does not give equality.
- **Suspected explanation:** No concrete experiment is adjudicated here. Whether its implementation computes full `V_i` or has an independent cutoff is unknown.
- **Missing capability:** A row-space equality checker for the selected concrete matrices and a proof or independently checked certificate that all later degrees have no new falls.
- **What this evidence does not establish:** It does not invalidate the conditional Lean theorem, any uninspected run, or a lower bound from an exact witnessed fall.

## What would unblock it

- [ ] Bind one named experiment's input, field, generators, term order, matrix construction, raw rows, and checker hashes to an independently replayable receipt; verify each reported row space equals the iteratively closed `V_{F,i}` at every reported degree.
- [ ] Supply a proved cutoff/completion lemma or checkable finite certificate for that exact system showing no falls after its measured maximum. Check a later-fall negative control such as `H_N` with `N` beyond the initial cutoff.

Meeting both conditions would support an exact `d_F` claim for that system. It would not transfer to other systems or establish an ECDLP performance result.

## Next discriminating step

- **Action or proof obligation:** For the archived R35a input, independently check unsatisfiability and the two restricted degree-4 refutations, then audit the Boolean-to-polynomial closure bridge against Definition 1.5 before an exact `d_F` claim is promoted.
- **Inputs and controls:** Preserve the run's original input and receipt; compare its row spaces to an independent closure implementation on tractable degrees, with the `G_N/H_N` later-fall control.
- **Execution limits and stop condition:** Read-only receipt and source audit first. Any new computation needs its frozen protocol, resource admission, and $25/day Spot budget; stop an exactness claim at the first missing row or cutoff witness.
- **Outcomes and next actions:** A row-space mismatch requires a source correction and rerun; equality without cutoff supports observed lower bounds only; both gates passing permits scoped exact-invariant review; missing raw data leaves the run unverified.
- **Recheck trigger:** A selected run with complete raw rows or a proved cutoff bound.

## Resolution and history

- 2026-10-31: Opened from the independent LastFall review; no actual rank run was promoted.
- 2026-10-31: Selected R35a as a concrete historical candidate; verified public custody bytes and freshly replayed the pinned dual-certificate checker under a bounded, exclusive host slot. The separate unsatisfiability and upper-bound steps remain unverified here. Unresolved.
