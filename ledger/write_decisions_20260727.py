#!/usr/bin/env python3
"""Write DEC-20260727-001..004 decision records for the completion wave."""
import os

DECS = [
    dict(
        id="DEC-20260727-001",
        context="EXP-SIG-007 n=21 seed-1 D5 rank cell: measurement COMPLETE",
        decision="experiment_completed_evidence_admitted",
        target_ids=["EXP-SIG-007", "H-SIG-001"],
        rationale=[
            "Full n=21 seed-1 D5 staircase measured to completion: rank = 265,950 vs sr_pred = 268,674 (778,394 cols, 76 carries, every unit checkpointed and sha256-verified; carries git-blob mirrored at refs/mirror/EXP-SIG-007-n21-s1).",
            "FINAL numbers independently re-derived from s1_vectors.pkl (dense m4ri): deficit_5 = 2,724; extra_5 = 2,725; residual_5 = 1,318. Closure anchors re-derived and PASS: rank(K5) = 10,373, A3_5 = 800, A4_5 = 1,407; consistency identities hold (extra_5 = deficit_5 + 1).",
            "Two-partition control: C-forward direction PASSED (re-derived 265,950 exactly across the 389,197 split; the 947-pivot burst reproduced at grid-shifted coordinates [449,197,454,197) — burst tied to column identity, not processing order). C-reverse at 490,000/778,394 checkpointed, rank already 265,950; completion pending (EV records control status explicitly).",
            "Telemetry on record: saturation onset col 454,000; dead plateau [364,000,449,000); single burst unit [449,000,454,000) k=947; 324,394-column fully dependent tail; 65 k=0 units.",
            "AGENTS rule 5 honored: two exFAT payload sweeps and one reboot interrupted the cell; zero mathematical loss (state rebuilt from carries with sum(npiv) proofs; rebuilt checkpoints cross-verified).",
        ],
        evidence_refs=[
            "ledger/EV-SIG-007.yaml",
            "experiments/EXP-SIG-007/analysis.md",
            "experiments/EXP-SIG-007/work/n21_s1/rank5/state.json",
            "refs/mirror/EXP-SIG-007-n21-s1",
        ],
        limitations=[
            "C-reverse control direction incomplete (63%, checkpointed); rank claim rests on the completed measurement + C-forward PASS + independent re-derivation until it finishes.",
            "Toy-scale boolean-family evidence (rule 7); not a crypto-scale claim.",
        ],
        next_actions=[
            "Finish C-reverse fires (resume automation_707000ac with control_rev input).",
            "Feed deficit_5(21) = 2,724 and residual_5(21) = 1,318 into the growth-law series (GPS-3).",
        ],
    ),
    dict(
        id="DEC-20260727-002",
        context="EXP-SIG-008 n=12 D6 cell: all three gates FINAL",
        decision="experiment_completed_evidence_admitted",
        target_ids=["EXP-SIG-008", "H-SIG-001"],
        rationale=[
            "GATE 1 FINAL: column-matched (N1) null at n=12 D6 ranks 149,410 vs sr_pred 156,520 (deficit 7,110, extra_6 = 7,110) — the column-matched D6 null baseline is INVALID at n=12; the failure shape is a below-freeze collapse in the top sextic columns, not variety saturation.",
            "GATE 2 FINAL: sem D6 rank 138,570 (deficit_6 = 17,950, extra_6 = 17,982, residual_6 = 2,722 vs A5 closure 15,260; closure ranks A3_6 = 1,515, A4_6 = 3,559, rankK6 = 26,760 all valid). The sem defect exceeds the null's by 10,840.",
            "GATE 3 FINAL: support-induced share of the sem-D5 deficit at n=12 = 0/1,321 = 0.0% (N1 null exactly semiregular at D3/D4/D5) — the n=9 40.6% confound is size-dependent and vanishes; the 1,321 D5 deficit is entirely genuine.",
            "Interpretation held pending EXP-GPS-002: gate-1 invalidity was later EXPLAINED as column-set-dependent support censoring (see DEC-20260727-003); residual_6 admissibility resolved there.",
            "Artifacts survived two worktree destructions via git-object preservation (branches exp-sig-008-artifacts, coordinator merge e32afbc).",
        ],
        evidence_refs=[
            "ledger/EV-SIG-008.yaml",
            "experiments/EXP-SIG-008/RESULTS.md",
        ],
        limitations=[
            "All numbers at n=12 seed 2, toy scale (rule 7).",
        ],
        next_actions=[
            "None for this experiment; the D6 baseline repair path runs through EXP-GPS-002 receipts.",
        ],
    ),
    dict(
        id="DEC-20260727-003",
        context="EXP-GPS-002: freeze-minus-one support-syzygy law (GPS-2) decisive test",
        decision="hypothesis_supported_scoped",
        target_ids=["GPS-2", "H-SIG-001"],
        rationale=[
            "P1 DECISIVE PASS: the FULL-support (old/T11-style, 100% of C(24,<=6) = 190,051 cols) null at n=12 D6 seed 2 ranks EXACTLY sr_pred = 156,520 (deficit 0, kernel 26,792, rankK6 = 26,792 == kernel, extra_6 = 0; determinism control: kill-redo of a staircase unit produced identical k = 14,761).",
            "Consequence: the EXP-SIG-008 column-matched null collapse (149,410, deficit 7,110) is COLUMN-SET-DEPENDENT — induced by the N1 censoring pattern (16,018 missing degree-6 columns), not an intrinsic below-freeze failure of semi-regularity. The freeze theory's validity below freeze stands; at D = freeze−1, support censoring induces syzygies in generic systems on the censored support.",
            "The D6 baseline is therefore REPAIRABLE: genuine D6 cascade content at n=12 = sem-minus-null excess 10,840 (= 17,950 − 7,110), with the 7,110 now accounted as support-induced. The residual_6 = 2,722 value becomes interpretable against the validated full-support baseline.",
            "P2 DECIDED: n=9 N1 D5 seed 2 extra = 368 (not 369): the exact integer is seed-dependent by 1 (369/369 at seed 1); magnitude stable (support-induced share 40.5% vs 40.6% of sem's 909 deficit). New on record: sem n=9 D5 rankK = 935, extra = 910, N1 |V| = 0 at seed 2.",
            "Scope: supported for the tested family at n in {9,12} at the freeze−1 degree; the general law (any n, rate band [0.23, 0.90] per missing top-slice column) remains open — bracket cell n=15 (D6 clean / D7 defective) is the named confirmation.",
        ],
        evidence_refs=[
            "ledger/EV-GPS-002.yaml",
            "experiments/EXP-GPS-002/analysis.md",
            "experiments/EXP-SIG-008/RESULTS.md",
        ],
        limitations=[
            "Seed-dependence of the exact extra at n=9 means the law is quantitative in magnitude, not exact integer, across seeds.",
            "Which support property of the censoring pattern sets the rate (7,110 at N1-D6 vs 368 at N1-D5) is unexplained — flagged open.",
        ],
        next_actions=[
            "Run the n=15 bracket confirmation (D6 column-matched null clean, D7 defective) when a compute window opens (gated; ~30 invocations).",
            "Use the repaired baseline: future D6 cascade claims must decompose sem deficit into support-induced (null-measurable) + genuine (sem-minus-null) shares.",
        ],
    ),
    dict(
        id="DEC-20260727-004",
        context="EXP-GPS-001: GPS-1 composition-class stratification + GPS-4 stage-1 nesting probe (forensics)",
        decision="hypothesis_falsified_as_stated_reformulated",
        target_ids=["GPS-1", "GPS-4"],
        rationale=[
            "GPS-1 P1 FALSIFIED as stated: the 947 burst pivots form a contiguous all-pivot window [452,824, 453,770) spread over 9 composition classes (top class 294/947 = 31.0%) — block composition is the wrong stratification variable.",
            "REFORMULATED on measured structure: ALL 947 burst pivots carry u-degree exactly 1, and all u>=2 unit classes (plus u=1 class (1,1,0,3)) contributed zero pivots — a coarser u-degree-typed stratification fits exactly. GPS-1 survives as the u-degree stratification hypothesis (predictions to be re-stated before further work).",
            "GPS-1 P2 NOT DECIDABLE from existing artifacts (dead plateau is not a union of whole classes; whole-class rates need live-unit profiling, ~3 h, resume command on file).",
            "GPS-4 P1 NOT SCORED (infrastructure: no surviving n=12 D6 kernel basis; S9 F5-image closure exceeded the 240 s cap — hypothesis untouched; resume path recorded).",
            "Rule-8 corrections on record: (i) 70 pure-u quartics missing -> quintic shell starts at col 124,244 (not 124,314); 654,150 quintic columns (not 654,080); (ii) ALL 20,349 pure-u quintics (5,0,0,0) missing — the a9 missing set is NOT confined to balanced compositions; (iii) the burst is a contiguous window, not a yield spike.",
        ],
        evidence_refs=[
            "ledger/EV-GPS-001.yaml",
            "experiments/EXP-GPS-001/analysis.md",
        ],
        limitations=[
            "Forensics only at n=21 seed 1 for GPS-1; the u-degree reformulation is unfitted.",
        ],
        next_actions=[
            "Re-state GPS-1 as u-degree stratification with predictions before new spend (idea-generator).",
            "GPS-4 P1 resume: kernel regeneration via carry back-reduction (4-5 invocations) + F5 position-list closure (1 invocation).",
        ],
    ),
]

TEMPLATE = """coordinator_decision:
  id: {id}
  context: "{context}"
  decision: {decision}
  target_ids: [{targets}]
  rationale:
{rationale}
  evidence_refs: [{refs}]
  limitations:
{limitations}
  next_actions:
{next_actions}
  decided_by: coordinator
  decided_at: "2026-07-27"
"""

def q(items, indent):
    return "\n".join('%s- "%s"' % (" " * indent, s.replace('"', "'")) for s in items)

os.makedirs("ledger", exist_ok=True)
for d in DECS:
    path = os.path.join("ledger", d["id"] + ".yaml")
    with open(path, "w") as f:
        f.write(TEMPLATE.format(
            id=d["id"], context=d["context"], decision=d["decision"],
            targets=", ".join(d["target_ids"]),
            rationale=q(d["rationale"], 4),
            refs=", ".join(d["evidence_refs"]),
            limitations=q(d["limitations"], 4),
            next_actions=q(d["next_actions"], 4),
        ))
    print("wrote", path)
