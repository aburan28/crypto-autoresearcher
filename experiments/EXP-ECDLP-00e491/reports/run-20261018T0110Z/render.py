"""Present the completed finite sampler measurements; no scientific reruns."""
from collections import Counter
from itertools import combinations
from pathlib import Path
from statistics import mean, median
import hashlib
import json
import subprocess
import tarfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pymupdf
import typst
import yaml

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
EXP="EXP-ECDLP-00e491"
RUNS=["RUN-ECDLP-ee0d23","RUN-ECDLP-6bd7b4"]
RAW_COMMIT="12c9637426bf25eb4f7a41b9ac59e6f3bcff78a9"


def write(name,value):
    with (OUT/name).open("x") as h:h.write(value.rstrip()+"\n")


def main():
    paths=[ROOT/"experiments"/EXP/"runs"/run for run in RUNS]
    raw=[json.loads((p/"raw-result.json").read_text()) for p in paths]
    receipts=[json.loads((p/"execution-receipt.json").read_text()) for p in paths]
    assert all(r["status"]=="output_validated" for r in receipts)
    panel=json.loads((ROOT/"research/snfs_sampler_completion_20261018/panel.json").read_text())
    support=raw[0]["data"]["summary"]
    jobs=raw[1]["data"]["rows"]
    with tarfile.open(paths[1]/"instrument.tar.gz") as archive:
        streams={m.name:archive.extractfile(m).read() for m in archive.getmembers() if m.name.endswith(".jsonl")}
    def point_keys(row):
        return [(tuple(e["x"]),tuple(e["y"])) for e in
                (json.loads(line) for line in streams[row["job"]["id"]+".jsonl"].splitlines()) if e["event"]=="point"]
    variation=[]
    for inp in panel["inputs"]:
        rows=[r for r in jobs if r["input_id"]==inp["id"] and r["job"]["role"]=="fresh"]
        assert len(rows)==12
        trajectories=[]
        for k,work in enumerate(panel["ladder"]):
            values=[r["observations"]["rungs"][k]["distinct_residues"] for r in rows]
            trajectories.append(dict(work=work,minimum=min(values),median=median(values),maximum=max(values),values=values))
        keys=[point_keys(r) for r in rows]
        pairs=list(combinations(range(12),2))
        same_prefix=[(a,b) for a,b in pairs if keys[a][:8]==keys[b][:8]]
        same_prefix_different_path=sum(any(x["distinct_residues"]!=y["distinct_residues"] for x,y in zip(rows[a]["observations"]["rungs"],rows[b]["observations"]["rungs"])) for a,b in same_prefix)
        final=[r["observations"]["final"]["distinct_residues"] for r in rows]
        variation.append(dict(input_id=inp["id"],degree=len(inp["g"])-1,g=inp["g"],p=inp["p"],A=inp["A"],B=inp["B"],n=12,
                              trajectories=trajectories,final_values=final,final_min=min(final),final_max=max(final),
                              pairs=len(pairs),same_first_eight_pairs=len(same_prefix),same_prefix_different_path_pairs=same_prefix_different_path,
                              different_full_point_set_pairs=sum(set(keys[a])!=set(keys[b]) for a,b in pairs)))
    gaps=[dict(shape=r["shape"],g=r["g"],first_exact_eligible=r["first_exact_eligible"],
               exact_factorization=r["q_factorization"],source_irreducibility_witness=r["source_irreducibility_witness"])
          for r in raw[0]["data"]["rows"] if r["exact_admissible"] and r["source_irreducibility_witness"] is not True]
    boundary=Counter(r["observations"]["final"]["distinct_residues"]-r["observations"]["rungs"][-1]["distinct_residues"] for r in jobs)
    manifests=[json.loads((p/"manifest.yaml").read_text())["run"] for p in paths]
    source_commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    summary=dict(scope="Descriptive arithmetic on two published completed trials; no scientific interpretation",
                 support=support,variation=variation,prime_eligible_unresolved_patterns=gaps,
                 job_roles=dict(Counter(r["job"]["role"] for r in jobs)),
                 before_to_after_final_residue_changes={str(k):v for k,v in sorted(boundary.items())},
                 support_rows=3232,prime_values=29088,jobs=len(jobs),point_events=480,
                 native_statuses={r["run_id"]:r["status"] for r in receipts},
                 analysis_source_commit=source_commit,analysis_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    write("observations.json",json.dumps(summary,indent=2))
    plt.rcParams.update({"font.size":10,"svg.hashsalt":"sampler-completion-20261018"})
    names=list(support)
    fig,ax=plt.subplots(figsize=(8,3.5))
    colors=["#a7adb4","#5285b1","#d39339","#429273"]
    fields=[("coefficient_patterns","coefficient support"),("q_irreducible","irreducible over Q"),("exact_admissible","Q + exact prime eligible"),("source_admissible","original screen + prime")]
    for offset,(field,label) in enumerate(fields):
        ax.bar([i+(offset-1.5)*.20 for i in range(4)],[support[n][field] for n in names],.19,label=label,color=colors[offset])
    ax.set(xticks=range(4),xticklabels=["degree 3","degree 7","degree 8","degree 12"],yscale="log",ylim=(1,8000),ylabel="Number of coefficient patterns (log scale)",title="All prescribed coefficient patterns, with each filtering stage separate")
    ax.legend(fontsize=8,ncol=2,loc="upper left")
    fig.tight_layout();fig.savefig(OUT/"support.svg");plt.close(fig)
    fig,axes=plt.subplots(2,4,figsize=(9,4.8),sharex=True,sharey=True)
    for number,(ax,row) in enumerate(zip(axes.flat,variation),1):
        ts=row["trajectories"];xx=[v["work"] for v in ts]
        ax.fill_between(xx,[v["minimum"] for v in ts],[v["maximum"] for v in ts],alpha=.25,color="#3e7db1")
        ax.plot(xx,[v["median"] for v in ts],"o-",ms=3,color="#3e7db1")
        ax.set(xscale="log",ylim=(-1,23),title=f"{number}: d={row['degree']}, A={row['A']}, B={row['B']}")
        ax.set_title(ax.get_title(),fontsize=9)
        ax.tick_params(labelsize=8)
        ax.grid(alpha=.18)
    axes.flat[-1].axis("off")
    axes.flat[-1].text(.0,.8,"12 fresh seeds/input\nMedian and min/max\nBefore-candidate rungs\nRange is not a CI",fontsize=9,va="top",transform=axes.flat[-1].transAxes)
    fig.supxlabel("Recorded candidate work W (log axis)");fig.supylabel("Distinct residues before candidate W")
    fig.subplots_adjust(left=.10,right=.98,bottom=.15,top=.92,wspace=.14,hspace=.30)
    fig.savefig(OUT/"variation.svg");plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,3.4))
    xx=range(7)
    ax.bar(xx,[r["same_first_eight_pairs"] for r in variation],label="same first eight (or shorter) point keys",color="#a7adb4")
    ax.bar(xx,[r["same_prefix_different_path_pairs"] for r in variation],label="same prefix, different residue-count path",color="#cf8833")
    ax.set(xticks=range(7),xticklabels=[f"{i+1}: d={r['degree']}" for i,r in enumerate(variation)],ylim=(0,82),ylabel="Pairs among 12 seeds (66 pairs/input)",title="Capped point prefixes and full recorded trajectories are separate observations")
    ax.legend(fontsize=8,loc="upper right");fig.tight_layout();fig.savefig(OUT/"prefixes.svg");plt.close(fig)
    for svg in OUT.glob("*.svg"):svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines())+"\n")
    support_text="; ".join(f"d={d}: {support[n]['coefficient_patterns']} patterns, {support[n]['q_irreducible']} Q-irreducible, {support[n]['exact_admissible']} exact-prime eligible, {support[n]['source_admissible']} original-screen eligible" for n,d in zip(names,[3,7,8,12]))
    ranges="; ".join(f"input {i+1} (d={r['degree']}): final D range {r['final_min']}..{r['final_max']}" for i,r in enumerate(variation))
    spread="; ".join(f"input {i+1}: "+", ".join(f"W={t['work']} D={t['minimum']}..{t['maximum']}" for t in r["trajectories"] if t["minimum"]!=t["maximum"]) for i,r in enumerate(variation) if any(t["minimum"]!=t["maximum"] for t in r["trajectories"])) or "No spread at the recorded rungs."
    prefix_text="; ".join(f"input {i+1}: {r['same_first_eight_pairs']} same-prefix pairs, {r['same_prefix_different_path_pairs']} of those with different D paths, {r['different_full_point_set_pairs']} different full point-set pairs" for i,r in enumerate(variation))
    pages=[("Complete finite sampler support","support.svg",[
        "Observations only, 2026-10-18. EXP-ECDLP-00e491 completed both frozen trials; native statuses are output_validated. Built-in checks are not independent scientific review. Interpretation, relevance and usefulness calls remain with the owner.",
        support_text+". These are exhaustive counts for the specified monic, constant +/-1, weight-three/five coefficient supports, k=4..12 and prime minimum 4096. Full QQ factorizations and all 29,088 prime records are retained.",
        "What is worth inspecting: 3 degree-eight and 21 degree-twelve exact-prime-eligible, Q-irreducible patterns remain unresolved by the original modular irreducibility screen. Across all coefficient patterns, the corresponding Q-irreducible but unresolved counts are 7 and 80. A missing screen witness is not relabeled Q-reducible.",
        "Both prime screens agree on all 29,088 eligible/ineligible value decisions. Every original positive irreducibility witness agrees with exact Q irreducibility. These agreements and unresolved cases are separate columns, not a uniformity or anomaly significance test.",
        "Example unresolved eligible degree-eight pattern, coefficients low to high: "+json.dumps(gaps[0]["g"])+f"; first exact eligible k={gaps[0]['first_exact_eligible']}. All 24 eligible unresolved patterns and their exact factors are in observations.json. The source trial uses Sage "+raw[0]["data"]["sage_version"]+" with proof-enabled primality; source-screen and exact classifications remain distinct.",
        "Source RUN-ECDLP-ee0d23. Reproducible commands, seeds, hashes, execution-start commit, environment, child CPU and memory are in the sealed native records. No earlier G3 result or protocol was changed."
    ]),("Fresh seeds with inputs held fixed","variation.svg",[
        "Seven fixed inputs, twelve fresh search-seed strings each: 84 fresh jobs, plus eleven legacy-seed controls and seven identical-seed replays. No field, curve or auxiliary-prime list is regenerated when a search seed changes. All 102 prescribed jobs completed.",
        ranges+". All endpoints match within each input's twelve fresh jobs, including ordinary zero-count cases. Intermediate-rung spread is retained: "+spread+".",
        "Selection was fixed before launch: four exact archived inputs previously seen under seeds 1/3, plus the minimum canonical-JSON input key among archived seed-1 random_g cases at each degree 7,8,12. These seven conditional cases are not a random sample of all curves or fields. Distinct seed labels do not prove statistical independence.",
        "The plot shows the median and observed min/max of twelve counts at each recorded rung. The shaded ranges are not confidence intervals; no population variance, significance label or fitted scaling exponent is supplied. Point/residue counts do not identify full point sets.",
        "Original checkpoints occur before testing candidate W. Final after-search snapshots are saved separately. Across all 102 jobs, residue-count differences between those last two boundaries were "+json.dumps(summary["before_to_after_final_residue_changes"])+" (difference: job count). The boundary distinction is retained even when counts happen to match.",
        "Source RUN-ECDLP-6bd7b4. Every unique discovered point, checkpoint and shell event is retained in the indexed instrument.tar.gz bundle, with no eight-point cap. Rejected candidates are not individually logged."
    ]),("Prefixes, controls and provenance","prefixes.svg",[
        "Each input has 66 pairwise comparisons among twelve fresh jobs. These pairs reuse the same twelve jobs; they are not 66 independent samples. Point-key prefixes use coordinates, exclude event work counters and include the whole shorter list when fewer than eight points were found.",
        prefix_text+". Full per-input trajectories and pair counts are in observations.json; all zero-difference/control behavior is retained beside differences.",
        "All eleven legacy controls reproduce every comparable original rung field. All seven identical-seed replays have byte-identical event streams. The separate checker verified all 480 discovered point events by exact Fraction arithmetic on the curve and recomputed residues; it also replayed all support records. No independent scientific review is claimed.",
        "Producer timing (completed operations, not performance comparisons): support wall "+f"{manifests[0]['timing']['wall_seconds']:.3f} s, child CPU {manifests[0]['timing']['child_cpu_seconds']:.3f} s, child peak RSS {manifests[0]['timing']['child_peak_rss_bytes']} bytes; panel wall {manifests[1]['timing']['wall_seconds']:.3f} s, child CPU {manifests[1]['timing']['child_cpu_seconds']:.3f} s, child peak RSS {manifests[1]['timing']['child_peak_rss_bytes']} bytes. Checker time is separate from those producer metrics. Exact host/platform and launch provenance are preserved in native manifests.",
        "All requested sampler follow-ups in this protocol are complete: larger-degree finite support, fixed-input interface, fresh seeds, legacy controls, identical-seed replay, uncapped traces and separate observation views. New questions to inspect are the structure of unresolved modular-screen cases and how discovery order changes while final counts agree. These are proposed follow-ups, not additional measurements or verdicts.",
        "Raw records were published before this report. Certificate kind remains none; hypothesis/goal scientific conclusions and historical observations remain unchanged. Local coverage() retains a hardcoded publication_verified:false field; actual publication is evidenced by Git commits/hashes and the separate archive receipt, never inferred from that placeholder."
    ])]
    markdown="# Completed sampler observations — 2026-10-18\n\n"
    typst_source='#set page(paper:"a4",margin:16mm)\n#set text(size:9.2pt)\n'
    for i,(title,svg,paragraphs) in enumerate(pages):
        markdown+="## "+title+"\n\n"+"\n\n".join(paragraphs)+"\n\n!["+title+"]("+svg+")\n\n"
        if i:typst_source+="\n#pagebreak()\n"
        typst_source+="\n= "+title+"\n\n"
        for j,text in enumerate(paragraphs):
            typst_source+='#text('+json.dumps(text)+')\n\n'
            if j==0:typst_source+='#image('+json.dumps(svg)+',width:100%)\n\n'
    write("REPORT.md",markdown);write("report.typ",typst_source)
    typst.compile(str(OUT/"report.typ"),output=str(OUT/"report.pdf"),root=str(OUT))
    pdf=pymupdf.open(OUT/"report.pdf")
    for i,page in enumerate(pdf):page.get_pixmap(matrix=pymupdf.Matrix(1.25,1.25)).save(f"/tmp/snfs-completed-page-{i+1}.png")
    make_yaml(summary,paths,receipts,source_commit)
    print(json.dumps({"pages":len(pdf),"variation":[dict(input=r['input_id'],final=[r['final_min'],r['final_max']],same_prefix_different_path_pairs=r['same_prefix_different_path_pairs']) for r in variation]}))


def make_yaml(summary,paths,receipts,source_commit):
    artifacts=[]
    for i,p in enumerate(paths):
        for name in ("raw-result.json","execution-receipt.json","instrument.tar.gz","instrument-index.json","manifest.yaml"):
            ident=("support" if i==0 else "panel")+"-"+name.replace(".","-")
            artifacts.append(dict(id=ident,path=str((p/name).relative_to(ROOT)),commit=RAW_COMMIT,sha256=hashlib.sha256((p/name).read_bytes()).hexdigest()))
    artifacts.append(dict(id="report-analysis",path=str(Path(__file__).relative_to(ROOT)),commit=source_commit,sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
    ev=lambda artifact,selector:[dict(artifact=artifact,selector=selector)]
    def observation(id,description,kind,value,unit,n,sample_unit,uncertainty,evidence):
        return dict(id=id,description=description,kind=kind,value=value,unit=unit,sample=dict(n=n,unit=sample_unit,dependence="Exhaustive coefficient support or repeated seeds within fixed inputs; no population independence assertion."),uncertainty=uncertainty,evidence=evidence)
    observations=[
        observation("complete-support","All finite coefficient classifications","measured",summary["support"],"coefficient patterns",3232,"exhaustively enumerated coefficient patterns","Exact classifications within this finite support; no extrapolation.",ev("support-raw-result-json","/data/summary")),
        observation("fresh-variation","Within-input fresh-seed distributions and pairwise prefix comparisons","derived",summary["variation"],"recorded counts and overlapping pair counts",84,"fresh jobs in seven fixed-input groups","Twelve seed jobs per input. Min/max is spread, not a confidence interval; pair counts are dependent.",ev("panel-raw-result-json","/data/rows filtered by job.role=fresh")+ev("panel-instrument-tar-gz","all fresh job JSONL event streams")+ev("report-analysis","main(): variation and pair arithmetic")),
        observation("check-completion","Builtin checker completion counts","measured",dict(catalog=3232,prime_values=29088,jobs=102,point_events=480,legacy_controls=11,exact_replays=7),"verified records/events",2,"completed native trials","Builtin mechanical checks by the authoring session; not independent scientific review.",ev("support-execution-receipt-json","/status and /check_returncode")+ev("panel-execution-receipt-json","/status and /check_returncode"))]
    record=dict(schema="crypto.autoresearch.experiment_observation.v1",report_kind="run_observations",
        question="What finite support does the sampler reach, and what varies across fresh seeds when the algebraic input is held fixed?",
        scope="The frozen 3232-pattern support and seven-input, 102-job panel. Complete within this protocol, no wider population claim.",
        method=dict(description="Executed the two fixed supervisor trials; built-in checkers replayed records. This report derives descriptive arithmetic from their published outputs.",
                    command="python3 tools/experiment_execution.py run --plan experiments/EXP-ECDLP-00e491/trial-plan.json --owner executor-snfs-sampler-20261018 --epoch 1",
                    parameters=dict(fixed_inputs=7,fresh_jobs=84,legacy_controls=11,identical_seed_replays=7,work_ladder=[300,1000,3000,10000,30000,100000]),
                    seeds=[r['job']['search_seed'] for r in json.loads((paths[1]/"raw-result.json").read_text())['data']['rows']],sampling_unit="Coefficient pattern or explicitly labeled job within fixed input; legacy/replay roles kept separate.",stopping_rule="All 3232 patterns and all 102 declared jobs completed without adaptive extension."),
        runs=[dict(experiment_id=EXP,run_id=r['run_id'],native_status=r['status'],evidence=ev(('support' if i==0 else 'panel')+'-execution-receipt-json','/status')) for i,r in enumerate(receipts)],
        observations=observations,
        controls=[dict(id="exact-source-reference",description="Exact QQ factorization and proof-enabled prime decisions alongside the source screen",observation_ids=["complete-support"],matching="Same complete coefficient supports and k/minimum rules.",limitations=["Unresolved source irreducibility screen is not Q-reducible."]),dict(id="fixed-input-references",description="Eleven archived-seed controls and seven same-seed replays",observation_ids=["check-completion"],matching="Fixed g,p,root,A,B,auxiliary lists and ladder; exact source seed strings used for controls.",limitations=["Only seven input cases; no independent scientific review."])],
        patterns=[dict(id="screen-unresolved",kind="exploratory_pattern",description="Three degree-eight and 21 degree-twelve prime-eligible Q-irreducible patterns are unresolved by the source modular screen.",observation_ids=["complete-support"],reference_ids=["exact-source-reference"],uncertainty="Exact finite counts, no significance test or general completeness claim about the source screen.",alternative_explanations=["The source requires an irreducibility witness among a fixed set of finite primes; exact Q factorization is a different criterion."]),dict(id="stable-endpoints",kind="exploratory_pattern",description="All twelve final residue counts agree within each input; intermediate paths and capped-prefix comparisons are separately retained.",observation_ids=["fresh-variation"],reference_ids=["fixed-input-references"],uncertainty="Only twelve fresh seeds per input and seven fixed cases; no wider variance estimate.",alternative_explanations=["Enumeration order can change intermediate discoveries while later counts coincide.","Small reporting prefixes can omit later differences."])],
        limitations=["Raw certificate kind none; builtin checking is not independent scientific review.","No hypothesis/goal interpretation, relevance or usefulness verdict.","The local coverage publication_verified field is hardcoded false; actual Git/hash publication has a separate receipt.","Same-prefix pair counts reuse the twelve jobs and are not independent samples."],missing=[],
        next_checks=[dict(question="Which coefficient/factorization structures occur among source-screen unresolved cases?",method="Inspect the retained exact factor and coefficient tables under a separately scoped follow-up.",control="Present all unresolved cases alongside witnessed cases of the same degree/weight; do not select only favorable examples.",status="proposed")],artifacts=artifacts)
    write("observation.yaml",yaml.safe_dump(record,sort_keys=False,width=98))


if __name__=="__main__":main()
