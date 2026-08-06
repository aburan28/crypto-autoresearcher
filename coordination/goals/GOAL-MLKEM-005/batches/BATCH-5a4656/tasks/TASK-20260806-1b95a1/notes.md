# Working notes — TASK-20260806-1b95a1 (Red Team review of BATCH-5a4656)

Independent session. Reviewed the Coordinator-committed snapshot at
`8a121df975c8665b7b7a62436b228822d4fe9545` on `claude/mlkem-campaign-005`
(parent `da16e6d3d4274304fcf4f3a42f81d63bab88ca4a`). No working-tree-only
artifact treated as evidence. Nothing here changes any `EV-MLKEM-*` or `KN-*`
status (rule 12 unmet/unwaived). No git commit run by me.

## 0. Reading order

`ledger/goals/GOAL-MLKEM-005.yaml` → `ledger/evidence/EV-MLKEM-d146a5.yaml` →
`ledger/decisions/DEC-20260805-4823db.yaml` → BATCH-5a4656 `dispatch_queue.json`
(all four handoffs + `coordinator_amendment`) → all four task directories →
`archives/TASK-20260806-6c5a4b/snapshot_receipt.json` → BATCH-a51f91
`TASK-20260805-49acd8` (prior red team, `is_C3_unmeetable_by_this_design`).

## 1. The lineage anomaly (found while orienting, not asked for by name in the
mandate, but decisive for the C1/C2/C3 read)

`ledger/goals/GOAL-MLKEM-005.yaml`'s own `batch_log` — as committed on THIS
SAME branch — shows `current_batch_id: BATCH-a44d08`, `previous_batch_id:
BATCH-f19c37`, and a `batch_log` sequence `BATCH-a51f91 → BATCH-436ddd →
BATCH-f19c37`. **`BATCH-5a4656` appears nowhere in that sequence.**

`git log --oneline claude/mlkem-campaign-005` (chronological, top = newest):

```
5c445c9ea coordination: bind TASK-20260806-6c5a4b snapshot receipt
8a121df97 snapshot: BATCH-5a4656 all four producers (TASK-20260806-6c5a4b)   <- REVIEWED HERE
da16e6d3d coordination: mark BATCH-5a4656 producers completed; ...
a582a7991 coordination: GOAL-MLKEM-005 BATCH-5a4656 — repair C3's instrument...
0c02c832b Merge pull request #190 ... (unrelated goal)
0702b38c0 Merge pull request #191 ... (unrelated goal)
...
a2fdca0ed research: GOAL-MLKEM-005 BATCH-a44d08 opened — k != d/2 leads (DEC-20260806-14ac13)
e1611a9b0 coordination: close BATCH-f19c37 queue ...
dbed00b80 research: TASK-20260806-f16f53 ledger archive — EV-MLKEM-94c773, DEC-20260806-14ac13 (refine)
a517e013b research: TASK-20260806-2e602d snapshot of both BATCH-f19c37 producers
a2d0eba67 research: GOAL-MLKEM-005 BATCH-f19c37 opened — executes DEC-20260806-00deff
e56712289 research: DEC-20260806-00deff supersedes DEC-20260805-4823db on two points
426afbd57 research: BATCH-436ddd ledger archive — EV-MLKEM-94f036, DEC-20260806-8c33bf (refine)
c9a7794fa research: GOAL-MLKEM-005 BATCH-436ddd opened (DEC-20260805-4823db)
08b6de8f9 ledger: TASK-20260805-d23bf0 archive of BATCH-a51f91; goal stays active
7983a474b snapshot: BATCH-a51f91 all four producers
096b9256b coordination: GOAL-MLKEM-005 BATCH-a51f91 — four tasks ...
```

So: **two separate batches — `BATCH-436ddd` and `BATCH-5a4656` — were both
opened to execute the identical `next_actions` block of
`DEC-20260805-4823db`** (`c9a7794fa`'s own commit message literally reads
"BATCH-436ddd opened (DEC-20260805-4823db)"; `BATCH-5a4656`'s own
`prediction_frozen.json.repairs` field reads "per DEC-20260805-4823db
next_actions[0]"). `BATCH-436ddd` iterated forward through **two** Coordinator
supersession decisions (`DEC-20260806-00deff`, then `DEC-20260806-14ac13`)
into `BATCH-f19c37` and then `BATCH-a44d08` — which was **already opened**
(commit `a2fdca0ed`) **before** `BATCH-5a4656` was even opened (`a582a7991`),
on this same branch. `BATCH-5a4656`'s task cards (`read_scope` for
`TASK-20260806-b51ac8`, `-4810e2`, `-3b0337`, `-9918cd`) cite only
`ledger/goals/GOAL-MLKEM-005.yaml`, `EV-MLKEM-d146a5.yaml`,
`DEC-20260805-4823db.yaml` and `BATCH-a51f91` paths. **None of the four cards,
nor the dispatch queue's own objective/coordinator_amendment text, cites
`EV-MLKEM-94f036`, `EV-MLKEM-94c773`, `DEC-20260806-00deff`, or
`DEC-20260806-14ac13`.**

Why this matters: those uncited, chronologically-earlier-committed records
found *specific, severe, named defects* in exactly the design `BATCH-5a4656`
executes — see §2 below. `BATCH-5a4656` is not a fresh, independent design; it
is the *original, unamended* Batch-2 design, run again without the repairs its
own sibling lineage already made and without addressing the standing
amendments (`AM-3`, `AM-4`) that lineage's Coordinator decision imposed on any
successor in this goal.

## 2. P3 in `BATCH-f19c37` vs P3 in `BATCH-5a4656` — same object, different
statistic, same underlying defect

Read `coordination/goals/GOAL-MLKEM-005/batches/BATCH-f19c37/tasks/TASK-20260806-0617ed/predicate_report.md`
and `.../reviews/TASK-20260806-ca8dc7/p3_attack.py` in full.

`f19c37`'s "P3" is `V(Q) = sum_a (P_aa - beta/d)^2`, a **deterministic**,
zero-draw scalar of the projector `P = QQ^T`. Its own §6(a): "A frame that is
a coordinate selector has `P_aa in {0,1}`, so `V = beta(1-beta/d)` exactly.
**The graded family at `t = 0` is that frame.**" `DEC-20260806-14ac13`'s
rationale, verbatim: "P3 returns its maximum possible DEPARTURE on Z^d... An
ambient isometry ... assigns the same lattice DEPARTURE (z = +465.48),
ANOMALY_BELOW_NULL (z = -17.98) ... and AGREEMENT (z = -0.50). **P3 IS REFUSED
AS AN ADJUDICATOR.**" `AM-4` (same decision) REQUIRES any coordinate-alignment
adjudicator to be shown invariant under ambient isometry, row permutation, and
unimodular change of basis, and REFUSES any predicate whose verdict changes
under those transformations "regardless of how well it separates."
`p3_attack.py` §D demonstrates this directly and reproducibly: rotating the
SAME lattice by an orthogonal `H` flips the verdict from DEPARTURE to
ANOMALY_BELOW_NULL to AGREEMENT.

`BATCH-5a4656`'s B2-A "P3" (`prediction_frozen.json` `P3` block) is a
**different** statistic — `mean(ratio_2em10[t=0]) - mean(ratio_2em10[t=1])`,
estimated from `2^20` CBD draws, tested at `>=4 SE-of-difference` — but its
`t=0` arm is constructed from **the identical object**: `E_S`, "a `d x beta`
matrix whose columns are beta distinct standard basis vectors ... selected by
a random permutation" (`prediction_frozen.json` `graded_family.definition`).
This is verbatim the "coordinate selector" object `f19c37`'s report names as
the extreme point where `V = beta(1-beta/d)` is attained *exactly, for any
d,beta, with zero draws* — i.e. a presentation artifact, not a lattice
property. B2-A's headline "P3 PASSES in all four cells by 46.8-73.2 SE" is,
to leading order, restating that the same deterministic extreme differs from
Haar — which per §2.1(c) of `f19c37`'s report is *exactly* the quantity
`ratio_2em10` is a noisy `2^20`-draw estimator of (`Var(e^T P e) = 2 beta +
(mu4-3)(V + beta^2/d)`, the only frame-dependent term being `V`). B2-A's
`prediction_frozen.json` even re-derives this identical mechanism
independently in its own `P3.direction_predicted_in_advance` field, citing
`RT-20260806-d008e0` (the BATCH-a51f91 red team) as the source of the idea —
but never checks it against the LATER finding (same author lineage, later
batch) that this exact extreme is a presentation artifact.

**This is the central objection (O3 below).** It does not mean B2-A's numbers
are wrong — they were independently spot-checked against `results.json` and
reproduce exactly (see §5). It means "the instrument is sensitive," B2-A's own
headline framing, is not established free of the concern the program's own
(uncited) sibling batch raised about the *identical construction* one rung
over.

## 3. Does P3/P4/P5 passing actually license reading P1/P2 as informative?
(the sharpest, cheapest check — O2)

P1/P2 is the ONLY test that reads the real (BKZ-reduced) arm; it compares the
real arm's own empirical quantile ratio against the *theoretical Beta CDF*
(not against the Haar arm). P3 compares two wholly synthetic arms (`t=0`
coordinate selector vs `t=1` Haar) against *each other*. These are different
decision rules with different comparators. Showing P3 has "dynamic range"
does not show P1/P2 has power — DF-1 (`EV-MLKEM-d146a5`) already established
that a sensitivity demonstration must manipulate the object the null removes;
the stronger, unstated requirement is that it must exercise the SAME decision
rule used on the real evidence.

Cheapest check, using only numbers already committed in this batch's own
`report.md` §7 (unreduced-arm `ratio_2em10`, at zero new compute): apply P1's
own frozen rule (`|ratio - 1| <= 0.05` at `2^-10`) to the unreduced arm, which
the report itself calls "a real, non-forced departure from Beta":

| cell | unreduced ratio_2em10 | \|dev\| | P1 tol (0.05) | P1 would say |
|---|---|---|---|---|
| d100_b30 | 1.03784 | 0.03784 | 0.05 | **PASS (missed)** |
| d100_b40 | 1.05540 | 0.05540 | 0.05 | FAIL (caught) |
| d140_b30 | 1.02326 | 0.02326 | 0.05 | **PASS (missed)** |
| d140_b40 | 1.02943 | 0.02943 | 0.05 | **PASS (missed)** |

**3 of 4 cells: P1's own frozen threshold would score a known, real,
non-forced Beta departure as a PASS.** This is not a hypothetical — it is
computed directly from numbers B2-A's own `report.md` §7 already prints. It
demonstrates that P1's detection floor is coarser than the very departure
this batch's own additional arms exhibit, independent of anything P3/P4/P5
show. The real arm's "PASS" therefore cannot be distinguished, by this
instrument, from "the real arm has a departure of this order and P1 cannot
see it" — which is precisely the caveat B2-A's own §6 states in prose
("P1/P2 cannot ... tell 'the real arm obeys Beta' apart from 'the real arm's
departure ... is too small for this decision rule to see'") without drawing
the C3 consequence.

## 4. B2-B lane (a): the SSH rekey check (O4)

`census.json` row R20 quotes only: "generating an ephemeral key exchange
keypair for ECDH and ML-KEM per connection is REQUIRED by this
specification." No committed artifact in this campaign quotes anything about
SSH transport-layer re-keying (RFC 4253 §9, `SSH_MSG_KEXINIT` re-exchange
within an existing connection, which does not terminate/restart the
"connection"). I fetched the primary source directly (WebFetch,
`https://www.ietf.org/archive/id/draft-ietf-sshm-mlkem-hybrid-kex-10.txt`,
this session) and asked specifically whether the fresh-keypair requirement is
stated to apply per rekey event or only at initial connection setup. Result:
the document does **not** address re-keying at all; "per connection" is the
only granularity stated. R21 (IKEv2)'s own quoted text is more precise —
"for each ML-KEM **key exchange**" — and IKEv2 rekeys (`CREATE_CHILD_SA`) are
themselves key-exchange events, so R21's wording is more robust to this
concern than R20's. This does not overturn `M=1` for either row (rekeying is
near-certainly intended to use fresh key material, since that is rekeying's
entire cryptographic purpose) — but B2-B's stated certainty ("EXACTLY 0, not
merely 'may be'") for R20 specifically outruns what the cited text supports.

## 5. Spot-checks against committed artifacts (no fabrication found this
round)

- `results.json` `P5_falsifier_adjudication`: `d100` ratio 0.8925753827199299
  (pred 0.8017837257372731, rel. discrepancy 0.1132...), `d140` ratio
  0.8902550943598917 (pred 0.8257228238721946, rel. discrepancy 0.0781...).
  Matches `report.md` §5 and the Coordinator's snapshot commit message and
  `snapshot_receipt.json.producer_headlines` exactly (0.8926/0.8903 vs
  0.8018/0.8257, 11.3%/7.8%).
- `results.json` per-cell `P3_sensitivity.shift_in_units_of_SE`: 46.816,
  73.146, 52.940, 53.990 — matches report.md table and commit message
  "46.8-73.2 SE" exactly. `met_directional`/`met_two_sided` both `true` in
  all four cells (my first query used a wrong key name and returned `None`;
  corrected and confirmed `true`/`true`).
- `results.json` per-cell `P4_gaussian_null_of_null` deviations: 0.7329,
  0.8788, 0.0603, 0.5170 SE — matches report.md ("largest deviation 0.88 SE")
  and commit message exactly.
- `results.json` per-cell `verdict_on_the_real_arm`: P1/P2 both `pass: true`
  in all four cells — matches report.md §6 table exactly.
- B2-B `bound.md` §4 figures (0.27416443652415257 / 0.2803876000294535 /
  0.28009177919327805 bits/block; "3 of 40" / "2 of 40" / "3 of 40" anomalous
  intervals) cross-checked directly against
  `BATCH-a51f91/tasks/TASK-20260805-9672b3/verification.json` `V7_...` and
  `V5_...` blocks — reproduce exactly.
- Coordinator commit message (`8a121df9`) and `snapshot_receipt.json`
  `producer_headlines`: every quoted P3/P4/P5/f'' figure checked above traces
  to the producer's own committed file, with the qualifiers the producers
  used ("direction-consistent", "magnitude ... off"). **No fabricated number
  found in this commit**, unlike the immediately preceding batch's CE-1
  defect the commit message itself references as precedent. This is recorded
  as a positive finding, not assumed.

## 6. Graded family validity (mandate item 1)

`Q_t = QR(sqrt(1-t) E_S + sqrt(t) G)`, `G` column-normalized post D-1 fix.
For any `t in (0,1)` where the combined matrix has full column rank (true
almost surely for continuous `G`), QR gives a valid `d x beta` matrix with
orthonormal columns — a proper rank-beta projector. Verified the D-1
"unaffected" claim algebraically: QR is invariant under independent positive
per-column rescaling of ITS INPUT; at `t=0` the input is `E_S` alone
(`G` term vanishes when `sqrt(t)=0`, independent of any G-normalization); at
`t=1` the input is `G` alone, and `QR(G) = QR(G_normalized)` exactly by the
same invariance (normalizing columns is itself a positive per-column
rescaling of `G`). So `t=0` and `t=1` — the only two points P1-P5 read — are
provably unaffected by D-1, exactly as claimed. **Confirmed correct, not
disputed.** Objection is narrower (O6, minor): interior points `0<t<1` have
no principled statistical interpretation (an artifact of this particular
"normalize-then-add-then-QR" parametrization, not a canonical distribution on
the Grassmannian such as a matrix-variate Bingham/von-Mises-Fisher family), so
"strictly monotone non-increasing across 6 gaps" is a fact about this ad hoc
construction's geometry more than a validated statement about a
physically-meaningful "degree of coordinate alignment."

## 7. Not pursued further (budget)

- Did not re-run `measure.py` myself (no BKZ budget claimed by this review;
  spot-checks above are against already-committed `results.json`/
  `verification.json` values only).
- Did not attempt to construct an AM-4-admissible replacement statistic —
  `DEC-20260806-14ac13` already names this open (its `next_actions[3]`).
- Did not re-derive B2-D's hash-instability finding; it is self-reported
  and disclosed honestly, not disputed here.
