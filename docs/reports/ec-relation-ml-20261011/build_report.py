#!/usr/bin/env python3
"""Derived explanation of two frozen software pilots and earlier run records."""
import csv
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

os.environ.setdefault("MPLCONFIGDIR","/tmp/ec-relation-ml-matplotlib")
os.environ.setdefault("XDG_CACHE_HOME","/tmp/ec-relation-ml-cache")
Path(os.environ["XDG_CACHE_HOME"]).mkdir(parents=True,exist_ok=True)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import typst

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"tasks/ec_relation_ml"))
from audit import audit
from run import verify
from derive_batch import main as derive_batch


def read(path):
    return json.loads(path.read_text())


def save(name,value):
    with (OUT/name).open("x") as stream:
        json.dump(value,stream,indent=2,allow_nan=False)
        stream.write("\n")


def load(profile,name):
    path = ROOT/"tasks/ec_relation_ml/examples"/name
    manifest = read(path/"manifest.json")
    cases = read(path/"cases.json")
    exact = read(path/"exact_evaluation.json")
    result = read(path/"evaluation.json")
    labels = [json.loads(line) for line in (path/"labels.jsonl").read_text().splitlines()]
    verification = verify(path)
    save(name+"-verification.json",verification)
    stats = {"profile":profile,"path":path.relative_to(ROOT).as_posix(),
             "source_commit":manifest["config"]["git_commit"],"cases":len(cases),"jobs":len(labels),
             "field_blocks":len({c["curve"]["p"] for c in cases}),
             "unique_curves":len({c["curve_uid"] for c in cases}),
             "subgroup_bits_range":[min(c["curve"]["n"].bit_length() for c in cases),max(c["curve"]["n"].bit_length() for c in cases)],
             "field_prime_range":[min(c["curve"]["p"] for c in cases),max(c["curve"]["p"] for c in cases)],
             "completed_jobs":sum(r["status"]=="completed" for r in labels),
             "censored_jobs":sum(r["status"]=="timed_out" for r in labels),
             "no_decomposition_cases":sum(not v["roots"] for v in exact.values()),
             "overhead_seconds":manifest["overhead_seconds"],
             "max_child_rss_bytes":max(r.get("peak_rss_bytes",0) for r in labels),
             "full_cost_learning_target":"per-action subprocess wall time (PAR-2 if censored)",
             "verified_relation_rank_sum":sum(v["relations"]["independent_rank"] for v in exact.values()),
             "bsgs_verified_recoveries":len(exact),"splits":{}}
    for split in ("train","validation","test"):
        cs = [c for c in cases if c["split"]==split]
        known = sum(c["target"][0]==c["curve"]["g"][0] for c in cs)
        recovered = sum(exact[c["id"]]["relations"]["target_recoveries"] for c in cs)
        stats["splits"][split] = {"cases":len(cs),"fields":len({c["curve"]["p"] for c in cs}),
                                  "initially_known_G_or_minus_G":known,
                                  "total_verified_recoveries":recovered,
                                  "new_target_recoveries_from_relations":recovered-known,
                                  "unidentified_targets":len(cs)-recovered,
                                  "independent_relation_rank_sum":sum(exact[c["id"]]["relations"]["independent_rank"] for c in cs)}
    return stats,cases,labels,result,exact


def main():
    loaded = [load("quick","pilot-20261011"),load("standard","standard-20261011")]
    quick,standard = [v[0] for v in loaded]
    derive_batch()
    batch = read(OUT/"batch-relations-derived.json")["results"]["standard-20261011"]["splits"]["test"]
    data_audit = audit(ROOT)
    save("archived-data-audit.json",data_audit)
    save("pilot-summary.json",{"pilots":[quick,standard],"provenance":"Derived arithmetic from retained engineering pilots; software replays passed.",
                               "scientific_review_performed":False,"confidence_intervals":"Not estimated: fixed engineering pilot, no preregistered security inference."})
    with (OUT/"curve-identities.csv").open("x",newline="") as stream:
        writer = csv.writer(stream,lineterminator="\n")
        writer.writerow(["profile","case_id","split","curve_uid","curve_id","p","A","B","n","h","Gx","Gy","Qx","Qy"])
        for stats,cases,_,_,_ in loaded:
            for c in cases:
                ec = c["curve"]
                writer.writerow([stats["profile"],c["id"],c["split"],c["curve_uid"],c["curve_id"],
                                 ec["p"],ec["a"],ec["b"],ec["n"],ec["h"],*ec["g"],*c["target"]])
    previous = []
    paths = ["experiments/EXP-ECDLP-5184f7/runs/RUN-ECDLP-07aad1/analysis/summary.json",
             "experiments/EXP-ECDLP-5184f7/runs/RUN-ECDLP-d0e449/analysis/summary.json"]
    wide,nist = [read(ROOT/p) for p in paths]
    previous.append(("Solinas toy family",wide["primary_result"]))
    previous.extend((name,nist["cases"][name]["primary"]) for name in ("P-192","P-224"))
    save("source-bindings.json",{"git_base":"84cbcbdab26e436e9a88eb01d03453e74426c68e",
            "inputs":{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
            "archived_csv_sha256":data_audit["source_sha256"],
            "software_manifests":{stats["path"]:hashlib.sha256((ROOT/stats["path"]/"manifest.json").read_bytes()).hexdigest() for stats,*_ in loaded}})
    snapshots = OUT/"source-records"
    snapshots.mkdir(exist_ok=False)
    source_paths = ["knowledge/literature/KN-LIT-001.md","knowledge/literature/KN-LIT-d8e1b9.md",
                    "knowledge/literature/KN-LIT-1940.md","knowledge/frontiers/ecdlp/index-calculus/KR-IC-5a43e5.yaml",
                    "knowledge/frontiers/ecdlp/index-calculus/KR-IC-5931ee.yaml"]
    source_meta = []
    for p in source_paths:
        content = subprocess.check_output(["git","show","84cbcbdab26e436e9a88eb01d03453e74426c68e:"+p],cwd=ROOT)
        (snapshots/Path(p).name).write_bytes(content)
        source_meta.append({"path":p,"git_commit":"84cbcbdab26e436e9a88eb01d03453e74426c68e",
                            "sha256":hashlib.sha256(content).hexdigest(),"provenance":"internal retrieved record; primary paper not read in this round"})
    save("source-records.json",source_meta)
    save("graph-inventory.json",{"checked":["knowledge/frontiers/ecdlp/README.md",
        "knowledge/frontiers/ecdlp/index-calculus/KR-IC-5a43e5.yaml",
        "knowledge/frontiers/ecdlp/index-calculus/KR-IC-5931ee.yaml",
        "experiments/EXP-ECDLP-4c6a09/reports/point-relations-20261011T0407Z/relation-pipeline.svg",
        "experiments/EXP-ECDLP-4c6a09/reports/random-fields-20261011T0523Z/sampling-pipeline.svg",
        "experiments/EXP-ECDLP-5184f7/runs/RUN-ECDLP-d0e449/report/report.md"],
        "canonical_changes":[],"reason":"Engineering bridge and exploratory data audit add no supported mathematical mechanism or sealed measured bound. Historical evidence and graphs stay immutable."})
    subprocess.run(["dot","-Tsvg",str(OUT/"workflow.dot"),"-o",str(OUT/"workflow.svg")],check=True)
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9,"svg.fonttype":"none","svg.hashsalt":"ec-relation-ml-20261011"})
    stats,cases,labels,result,exact = loaded[1]
    test = result["test"]
    names = ["fixed","train_best_fixed","uniform_seeded","ridge","bandit"]
    readable = ["Fixed 0","Best fixed\n(training)","Random\n(seed 0)","Ridge","Bandit"]
    values = [test["methods"][name]["mean_action_process_or_par2_seconds"] for name in names]
    fig,ax = plt.subplots(figsize=(8.2,3.3))
    ax.bar(range(len(names)),values,color=["#b0bac0"]*3+["#287d94","#b87535"],width=.65)
    by_id = {c["id"]:c for c in cases}
    rows = {(r["case_id"],r["action"]):r for r in labels}
    for x,name in enumerate(names):
        action_map = dict(zip(test["case_ids"],test["methods"][name]["actions"]))
        clusters = {}
        for case_id,a in action_map.items():
            clusters.setdefault(by_id[case_id]["curve"]["p"],[]).append(rows[case_id,a]["cost_seconds"])
        ys = [sum(v)/len(v) for _,v in sorted(clusters.items())]
        ax.scatter(np.linspace(x-.17,x+.17,len(ys)),ys,s=12,color="#22323d",alpha=.6)
        ax.text(x,max(values)*1.06,f"{values[x]:.3f}",ha="center",fontsize=9)
    ax.set_xticks(range(len(names)),readable)
    ax.set_ylabel("Mean action process / PAR-2 time (seconds)")
    ax.set_ylim(0,max(max(values)*1.2,ax.get_ylim()[1]))
    ax.set_title(f"Standard software pilot: {test['cases']} test cases in {test['independent_field_blocks']} held-out fields")
    ax.spines[["top","right"]].set_visible(False)
    fig.text(.5,.015,"Dots: per-field means, not confidence intervals. One run/fit; startup included. Source: standard-20261011.",ha="center",fontsize=8)
    fig.tight_layout(rect=(0,.05,1,1))
    fig.savefig(OUT/"solver-costs.svg")
    plt.close(fig)
    fig,axes = plt.subplots(1,2,figsize=(8.2,3.2),gridspec_kw={"width_ratios":[1.35,1]})
    for i,stats in enumerate((quick,standard)):
        s = stats["splits"]["test"]
        parts = [s["initially_known_G_or_minus_G"],s["new_target_recoveries_from_relations"],s["unidentified_targets"]]
        left = 0
        for value,color,label in zip(parts,("#b6c2c8","#287d94","#d2a171"),("Known G or -G","Newly identified","Unidentified")):
            axes[0].barh(i,value,left=left,color=color,label=label if i==0 else None)
            if value:axes[0].text(left+value/2,i,str(value),ha="center",va="center",fontsize=8)
            left += value
    axes[0].set_yticks([0,1],["Quick test","Standard test"])
    axes[0].set_xlabel("Targets (count); same outcome for all completed solvers")
    axes[0].legend(loc="upper center",bbox_to_anchor=(.5,-.24),ncol=3,fontsize=7)
    ranks = [s["splits"]["test"]["independent_relation_rank_sum"] for s in (quick,standard)]
    new = [s["splits"]["test"]["new_target_recoveries_from_relations"] for s in (quick,standard)]
    axes[1].bar([-.15,.85],ranks,.3,label="Sum of per-target ranks",color="#287d94")
    axes[1].bar([.15,1.15],new,.3,label="New target logs",color="#b87535")
    axes[1].set_xticks([0,1],["Quick","Standard"])
    axes[1].set_ylabel("Count on test cases")
    axes[1].legend(fontsize=6)
    for ax in axes:ax.spines[["top","right"]].set_visible(False)
    fig.suptitle("Rank, already-known targets and new recovery are separate quantities",fontsize=10)
    fig.text(.5,.005,"Exact finite fixture counts; no population CI. Sources: pilot-20261011 and standard-20261011.",ha="center",fontsize=7)
    fig.tight_layout(rect=(0,.09,1,.95))
    fig.savefig(OUT/"relations-and-recovery.svg")
    plt.close(fig)
    metrics = "\n".join(f"| {label.replace(chr(10),' ')} | {value:.3f} | {test['methods'][name]['delivered_independent_rank_sum']} | {test['methods'][name]['verified_target_recoveries']} |" for label,value,name in zip(readable,values,names))
    old_rows = "\n".join(f"| {name} | {r['estimate']:.4f} | [{r['CI99_9'][0]:.4f}, {r['CI99_9'][1]:.4f}] |" for name,r in previous)
    rows = "\n".join(f"| {s['profile']} | {s['field_blocks']} | {s['cases']} | {s['jobs']} | {s['completed_jobs']} | {s['censored_jobs']} |" for s in (quick,standard))
    tq,ts = quick["splits"]["test"],standard["splits"]["test"]
    total_wall = quick["overhead_seconds"]["pilot_wall_total"]+standard["overhead_seconds"]["pilot_wall_total"]
    md = f'''# ML-assisted EC relation research flow

2026-10-11 UTC. Status: **implemented and measured engineering pilot**; exact
software replays passed. No independent scientific review, sealed bound,
hypothesis promotion, or new cryptographic-size resistance result.

## What changed

ML now chooses an algebra solver for an actual elliptic-curve decomposition
problem. Its output passes an exact point-relation checker and modular rank
evaluator. This replaces a vague pattern search with a measurable question:
does guidance yield additional target-identifying relations or lower full cost
on fields and curves excluded from training?

The first bridge uses the existing ridge and one-step contextual-bandit
selector from `tasks/polynomial_solver_ml`. It solves bounded S3 systems,
lifts their roots to points, verifies the signed group equation, removes
dependent information, and checks whether the target scalar is uniquely
identified. Learned choices among four solvers are implemented; learned lifts,
factor bases, endomorphisms and other relation generators are **proposed
extensions**. Existing `tools/rl_isogeny_search.py` is another ML search tool,
but its structural scores are not used as a substitute for verified recovery.

[Workflow diagram](workflow.svg) · [editable source](workflow.dot) ·
[runnable task](../../../tasks/ec_relation_ml/README.md) ·
[frozen pilot and proposed confirmation design](../../../tasks/ec_relation_ml/PROTOCOL.md)

![Implemented flow and proposed extensions](workflow.svg)

## Measured pilot results

Both profiles were fixed before execution. Source commit:
`{standard['source_commit']}`. All **{quick['jobs']+standard['jobs']} solver
jobs** were retained and every completed output matched separate exhaustive
evaluation of the original polynomial equations plus exact relation checks.
The 13 mathematical/data-boundary tests passed. Positive and constant-reward
learning controls passed; shuffled labels were replayed as a diagnostic.

| Profile | Independent finite fields | Cases | Jobs | Completed | Censored |
|---|---:|---:|---:|---:|---:|
{rows}

Quick test: **{tq['cases']} targets in {tq['fields']} held-out fields**,
{tq['independent_relation_rank_sum']} independent relation rows,
{tq['total_verified_recoveries']} verified target logs. Of those,
{tq['initially_known_G_or_minus_G']} were already known G/-G and
**{tq['new_target_recoveries_from_relations']} were newly identified**.
Standard test: **{ts['cases']} targets in {ts['fields']} held-out fields**,
{ts['independent_relation_rank_sum']} independent rows,
{ts['total_verified_recoveries']} total verified target logs,
{ts['initially_known_G_or_minus_G']} initially known and
**{ts['new_target_recoveries_from_relations']} newly identified**;
{ts['unidentified_targets']} remain unidentified by this decomposition set.

These ranks are sums of per-target matrix ranks. Targets on one curve share
seed logs; a sum need not be the rank of a single combined batch matrix.
`batch-relations-derived.json` separately deduplicates the combined equations
per exact curve and verifies recovery against both points and the BSGS output.
This is post-hoc exact accounting of the measured root sets, with no new fits
or solver trials and no full batch-cost claim. On the standard test, the sum
of joint per-curve ranks is **{batch['joint_rank']}**, and shared information
newly identifies **{batch['newly_identified_targets']}** targets (plus
{batch['initially_known_targets']} initially known). This reuse applies to
all solvers and is not a learned discovery.

All completed solvers solve the same equations, so they deliver the same
relation information. **ML discovered no additional relations in this pilot.**
Its learned decisions concern solver cost. Exact generic BSGS recovered all
{standard['cases']} standard targets; the relational method need not do so.

| Standard test selector | Mean full action process/PAR-2 cost (s) | Independent rank sum | Total verified target logs |
|---|---:|---:|---:|
{metrics}

![Solver costs and per-field dispersion](solver-costs.svg)

Numbers are one frozen software run, not evidence of a learned mathematical
weakness. The four test-field quick pilot was too small for security inference;
the standard pilot also supplies no preregistered confidence interval. Dots
show observed per-field means, not confidence intervals. Timings include fresh
Python/NumPy/SymPy startup, which dominates these tiny jobs and varies with host
activity. Quick label collection overlapped read-only Git corpus retrieval and
sparse-checkout materialization. Its largest slow child took 1.620 s of process
time but only 0.0294 s inside the timed solver. These observations are retained.
No timing difference is a security finding. The warm-parent BSGS check is a
correctness comparator, not a paired process-timing race.

The quick and standard pilots took **{total_wall:.1f} s together**, including
all {quick['jobs']+standard['jobs']} acquired action labels and control fits.
Standard offline label acquisition took
{standard['overhead_seconds']['complete_offline_label_acquisition']:.3f} s;
fit-and-select took
{standard['overhead_seconds']['fit_and_select_both_learners']:.3f} s. All
generation, oracle, fitting, feature, inference and verification times are in
`pilot-summary.json` and the immutable pilot manifests. A one-off attack must
charge label acquisition and fitting; selected-action times alone are not that
full cost. Largest recorded child RSS: {standard['max_child_rss_bytes']:,} bytes.
Fields span primes {standard['field_prime_range'][0]}–{standard['field_prime_range'][1]};
subgroups span {standard['subgroup_bits_range'][0]}–{standard['subgroup_bits_range'][1]} bits.
Root extraction enumerates the small field grid and cannot scale to P-192/P-224.

![Independent information and target recovery](relations-and-recovery.svg)

## Theory in plain language — derived explanation

For Q = [q]G, a valid equation between public points becomes a linear equation
between their unknown logs. On the checked example
E/F17: y²=x³+2x+2, n=19, h=1, G=(5,1), let P=[5]G and Q=[7]G.
The relation 2P-Q=3G gives **2u-q=3 modulo 19**. It has rank one and two unknowns;
it does not identify q. Add P=5G, or u=5: now rank is two and q=7 is uniquely
identified and verifies against Q. Predicting “a relation probably exists” is
not enough; the exact equation and its information gain must survive checking.

The summation polynomial encodes whether x-coordinates can belong to points
whose signed sum is zero. The implemented equation is

`S3(x,y,z) = (x-y)^2 z^2 - 2((x+y)(xy+A)+2B)z + (xy-A)^2 - 4B(x+y)`.

Fix z=x(Q) and constrain x,y to public factor-base x coordinates. Solve, find
base-field y coordinates, choose signs and verify P1+P2=Q. A polynomial root
alone does not verify a usable point relation. Duplicate roots, P and -P, and
scaled/dependent equations do not provide extra rank. An explicit known map
must transport witnesses back to the original curve before it can contribute
information there; this pilot does not automatically discover such maps.

Three different ranks matter. **Unit rank** counts independent multiplicative
units in a number field. **Mordell–Weil rank** counts independent infinite-order
EC points over that number field. **Relation-matrix rank modulo n** counts
independent constraints between finite-subgroup logs. ML prediction of one of
these ranks is not scalar recovery. A higher lift rank can enlarge a point
supply while discovery and combinations consume more work. The earlier
RUN-ECDLP-6d910b found rank gains on selected lifts but no advantage over its
declared BSGS comparison; its exact lift preprocessing was excluded from primary
group-call counts. A new candidate must price that work too.

## What the archived data can and cannot train

The retrospective audit of RUN-ECDLP-9e6cc1 reads {data_audit['rows']} cohorts:
{data_audit['distinct_source_number_fields']} source number fields, but only
{data_audit['distinct_exact_curve_uids']} distinct finite curves over
{data_audit['distinct_finite_prime_fields']} primes. The nominal
{data_audit['nominal_repeated_target_attempts']} attempts reuse target batches;
they are not that many independent challenges. Requiring both a source-field
and finite-curve holdout links all {data_audit['rows']} rows into one connected
component. A random row split would test memory of these reused objects.

These earlier data are suitable for exploratory audits and mechanism proposals.
They have already been inspected and cannot now become fresh confirmation.
Holding out new finite fields under a fixed lift template and holding out wholly
new source fields/templates are separate questions. P-192 and P-224 are two
fixed primes; a family classifier could identify constants or sparse binary
encodings without learning anything about their discrete logs.

For context, the prior controlled generic-attack comparisons remain unchanged:

| Earlier scope | Structured/random normalized rho cost | Marginal 99.9% interval |
|---|---:|---|
{old_rows}

These interval estimates are conditional on their recorded sampling/matching.
The Solinas study uses toy fields; P-192/P-224 use full fields with small
16–20-bit subgroups. They did not detect greater generic resistance in those
scopes and do not decide cryptographic-size resistance or eliminate rare
nonlinear structure. ML can guide discovery of a different, verifiable
mechanism; it cannot make these earlier null comparisons into a security proof.

## Next confirmation study — proposed

Use learned guidance to prioritize low-height lifts, factor bases, candidate
relations and solver policies, with exact witnesses and incremental target
identification as feedback. Compare against random proposals, simple public
heuristics, best fixed policies, matched random primes/number fields/seed points
and identical-target generic BSGS/rho. Retain all failed, censored and unavailable
map cases. Prevent seed regeneration of hidden answers: evaluator-held fresh
challenge entropy is revealed only after predictions/checkpoint hashes are fixed.

Target at least 512 independent matched blocks per eligible toy-size stratum,
four independent curves and four random-prime/four random-number-field controls
per structured draw where the eligible population and maps permit. For a fixed
P-192/P-224 field, a block is a new curve/control pairing, not a new structured
prime. Use discovery variance and a frozen practical effect to set power and
final confirmation counts before opening those labels. There is no assumption
that more target rows manufacture independent fields.

Reserve two-sided **99.9667% intervals per family for three primary families**
to obtain 99.9% joint nominal coverage by Bonferroni. Additional primary sizes
or objectives need further correction. Resample independent matched blocks,
charge all acquisition/training/search/verification/memory costs, and freeze
missingness, multiplicity, stopping and any amortization assumptions. New
samples improve precision; a higher confidence level alone widens intervals.
A reproducible signal needs mathematical explanation and independent review
before any larger-group security implication.

## Sources, exact identities and remaining limits

All benchmark curve parameters, generators, subgroups and full EC1 UIDs are in
[curve-identities.csv](curve-identities.csv) and the public `cases.json` files.
The illustrative F17 equation is checked by the 13-test suite, including all
nonzero subgroup point pairs, alias/dependency checks and rank-without-recovery.
Software verification replays producer arithmetic and an independent root
oracle; it is not independent scientific review or authentication of timing.

Provenance is internal/retrieved for the repository sources: prior run IDs
RUN-ECDLP-6d910b, RUN-ECDLP-9e6cc1, RUN-ECDLP-07aad1 and RUN-ECDLP-d0e449;
exact input SHA bindings are in `source-bindings.json`. The knowledge MCP was
not available; bounded repository searches and exact source reads were used.
Copied KN-LIT/KR records under `source-records/` are unchanged snapshots, with
their original verification limits retained. Semaev summation-polynomial
decomposition is established prior art (KN-LIT-001/KR-IC-5a43e5); the curated
record for naive prime-field IC reports a conditional negative result
(KN-LIT-d8e1b9/KR-IC-5931ee). The primary papers were not read in this round;
no claim of novelty or new impossibility is made. KN-LIT-1940 is an internal
abstract-level pointer about twist-class redundancy, not evidence of ECDLP
recovery. The warning motivates a separate transport/template holdout.

`graph-inventory.json` records historical study diagrams and canonical frontier
sources checked. There is no supported frontier change; only these new derived
views are added. Results do not alter any official hypothesis status. Ready PR
tracking files accompany the change; actual publication requires working GitHub
authentication and is reported separately, without fabricating a PR number.
'''
    (OUT/"report.md").write_text(md)
    escape = lambda s: str(s).replace("\\","\\\\").replace("_","\\_").replace("#","\\#").replace("[","\\[").replace("]","\\]").replace("$","\\$")
    def table(rows,columns):
        return '#table(columns: ('+columns+'), inset: 4pt, '+',\n'.join('['+escape(v)+']' for row in rows for v in row)+')'
    measured_rows = [("Pilot","Fields / cases","Jobs / censored","Test new logs")]+[(s["profile"],f"{s['field_blocks']} / {s['cases']}",f"{s['jobs']} / {s['censored_jobs']}",f"{s['splits']['test']['new_target_recoveries_from_relations']} / {s['splits']['test']['cases']}") for s in (quick,standard)]
    comparison_rows = [("Selector","Process/PAR-2 mean (s)","Rank / total target logs")]+[(label.replace("\n"," "),f"{value:.3f}",f"{test['methods'][name]['delivered_independent_rank_sum']} / {test['methods'][name]['verified_target_recoveries']}") for label,value,name in zip(readable,values,names)]
    previous_rows = [("Prior scope","Ratio","Marginal 99.9% interval")]+[(name,f"{r['estimate']:.4f}",f"[{r['CI99_9'][0]:.4f}, {r['CI99_9'][1]:.4f}]") for name,r in previous]
    ty = f'''#set page(paper: "a4", margin: 17mm, footer: context [#align(center)[#counter(page).display()]])
#set text(font: "DejaVu Sans", size: 9.5pt)
#set par(leading: .5em)
= ML-assisted EC relation research flow
2026-10-11 · measured engineering pilots · source {standard['source_commit'][:12]}

The runnable bridge uses ML to choose an algebra solver, checks exact EC point
relations, removes dependent rows and verifies any uniquely identified scalar.
It implements a discovery/evaluation flow. It establishes no cryptographic-size
resistance result or new attack mechanism.

{table(measured_rows,'1fr, 1.8fr, 1.5fr, 1.5fr')}

Every completed action agreed with separate exhaustive evaluation of the original
equations and exact point checks. All {quick['jobs']+standard['jobs']} jobs were retained;
the 13 mathematical/leakage tests and software replays passed. The standard test
has {ts['cases']} targets in {ts['fields']} unseen finite fields.

{table(comparison_rows,'1.8fr, 1.8fr, 1.9fr')}

#image("solver-costs.svg", width: 100%)

All completed solvers deliver the same information: a sum of {ts['independent_relation_rank_sum']}
per-target independent ranks and {ts['total_verified_recoveries']} total target logs,
including {ts['initially_known_G_or_minus_G']} already-known G/-G targets.
Only {ts['new_target_recoveries_from_relations']} are newly identified. ML found no
additional relations here. Exact BSGS recovered all {standard['cases']} standard targets.
Warm-parent BSGS timing is not a paired process benchmark. Post-hoc shared-batch
accounting gives a sum of {batch['joint_rank']} joint per-curve ranks and
{batch['newly_identified_targets']} newly identified test targets. These differ
from per-target sums; all solvers supply the same pool. No full batch-cost claim.

Timings include fresh process startup; dots are field means, not intervals.
These are one-run software observations, with no preregistered statistical
security inference. Sources: immutable pilot manifests, labels and evaluation JSON.

#pagebreak()
= Why rank is not recovery
Let $Q = q G$ and $P = u G$. On the checked toy curve
$E / F_17: y^2 = x^3 + 2x + 2$, subgroup order 19, cofactor 1, $G = (5,1)$,
take $P = 5G$ and $Q = 7G$. The point equation $2P-Q=3G$ gives
$2u-q=3$ modulo 19. Rank one with two unknowns leaves q undetermined.
Add $P=5G$: rank becomes two, and q=7 is unique and verifies against Q.

Unit rank counts number-field multiplicative units. Mordell–Weil rank counts
independent infinite-order EC points over that field. Modular relation rank
counts constraints between finite-subgroup logs. Predicting one of these ranks
does not recover a scalar. Extra seeds can add rank while leaving q unknown.

#image("workflow.svg", width: 100%)

Solid boxes are implemented. Dashed extensions/confirmation are proposed.
Training feedback uses training fields only. Scalar truth and post-solve outcomes
are excluded from features. S3 roots must lift to subgroup points with signs
that verify P1+P2=Q. Duplicate, negated and dependent information adds no rank.
Known maps need explicit transport to the original curve before their relations
can be counted there; map discovery is outside this pilot.

#pagebreak()
= Controls, costs and data independence
#image("relations-and-recovery.svg", width: 100%)

The archived number-field data have 104 cohorts from 24 source fields but only
six finite curves over three primes. The 1,664 nominal attempts reuse targets.
A simultaneous source-field and finite-curve holdout connects all 104 rows.
Random row splitting would test reuse. The archive is exploratory, not fresh
confirmation. Source: RUN-ECDLP-9e6cc1 and archived-data-audit.json.

Held-out finite fields under a fixed lift and wholly unseen lift templates are
separate generalization questions. P-192 and P-224 are fixed fields: recognizing
their constants or sparse binary encodings is not evidence about their logs.

Controls: fixed action, best training fixed action, uniform policy, shuffled
action labels, planted learnable and constant-reward cases; exact original-root
and signed-point checks; point aliases, false relations and field/curve leakage;
exact generic BSGS on the same targets. There is no speedup acceptance gate.

The pilots took {total_wall:.1f} seconds in total. Standard acquisition cost
was {standard['overhead_seconds']['complete_offline_label_acquisition']:.2f} seconds;
fit and selection took {standard['overhead_seconds']['fit_and_select_both_learners']:.3f} seconds.
Full overhead and memory are retained in the manifests. A one-off attack must
charge acquisition and fitting, not just a chosen solve. Subgroups here are
{standard['subgroup_bits_range'][0]}–{standard['subgroup_bits_range'][1]} bits; grid root extraction does not scale.
Quick timing overlapped Git reads/checkout. One 1.620-second process spent only
0.0294 seconds in its timed solver. No such timing difference is a security finding.

Next scientific confirmation (proposed): fresh evaluator-held challenges,
checkpoint/predictions locked before truth release, matched random-prime and
random-number-field/seed controls, identical-target BSGS/rho, and full cost.
Target at least 512 independent eligible matched blocks per size stratum with
four curves and four controls of each type where available. Fixed P fields use
new curve/control pairings. Estimate power and freeze final counts before
opening confirmation labels. More reused target rows do not create new fields.

For three primary families, reserve 99.9667% intervals each for 99.9% joint
nominal coverage; additional primary tests require more correction. Resample
independent matched blocks, predeclare missingness/stopping/amortization, and
seek an independently reviewed mechanism. Higher confidence alone widens intervals.

#pagebreak()
= Prior evidence and limits
The earlier generic-resistance results remain unchanged:

{table(previous_rows,'1.8fr, 1fr, 2.5fr')}

Source runs: RUN-ECDLP-07aad1 (Solinas toy fields) and RUN-ECDLP-d0e449
(full P-192/P-224 fields, 16–20-bit subgroups). The intervals are conditional
on their frozen sampling/matching. These comparisons did not detect greater
generic resistance in those scopes. Cryptographic-size ECDLP remains unresolved;
localized or different structural mechanisms require different tests.

RUN-ECDLP-6d910b measured rank gains for selected lifts but no advantage over
its declared BSGS comparison. Exact lift preprocessing was excluded from its
primary group-call totals. New learned candidates must charge that work.

All exact benchmark curve/subgroup/generator/target identities are in
curve-identities.csv and the public cases.json files. Primary source:
{escape('tasks/ec_relation_ml/PROTOCOL.md')} and immutable examples/{escape('standard-20261011')}.
Software verification replays exact roots, signed relations, ranks, recovery,
fits and controls. It does not independently authenticate timings or constitute
independent scientific review. No sealed bound or official status changes.

Prior-art records were read from the repository because the knowledge MCP was
unavailable. KN-LIT-001/KR-IC-5a43e5 describe established summation-polynomial
decomposition. KN-LIT-d8e1b9/KR-IC-5931ee relay a negative result for naive
prime-field index calculus under statistical assumptions. KN-LIT-1940 is an
abstract-level pointer about twist-class redundancy. Primary papers were not
read in this round; no novelty or new impossibility follows from these pointers.
Unchanged record snapshots and hashes are in source-records/ and source-records.json.

The historical report diagrams and canonical frontier records were checked;
graph-inventory.json explains why no supported graph/frontier changes. The new
diagram is an engineering workflow, not a proven mathematical mechanism.

Artifacts: report.md; workflow.dot/svg; solver-costs.svg;
relations-and-recovery.svg; pilot-summary.json; archived-data-audit.json;
curve-identities.csv; source-bindings.json; both software verification receipts.
Publication is tracked separately and requires authenticated GitHub access.
'''
    (OUT/"report.typ").write_text(ty)
    for path in OUT.glob("*.svg"):
        path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines())+"\n")
    typst.compile(str(OUT/"report.typ"),output=str(OUT/"report.pdf"),root=str(OUT))
    save("render-environment.json",{"python":sys.version,"versions":{n:importlib.metadata.version(n) for n in ("matplotlib","numpy","sympy","typst")},"graphviz":subprocess.check_output(["dot","-V"],stderr=subprocess.STDOUT,text=True).strip()})
    print(json.dumps({"pdf":str(OUT/"report.pdf"),"pilots":[quick,standard]},indent=2))


if __name__=="__main__":
    main()
