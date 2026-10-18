"""Present pinned sampler arithmetic and archived trajectories; no searches."""
from pathlib import Path
import argparse
import csv
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pymupdf
import typst
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CODE = "a6a1d9173e4cf8cea1d7f3855f41c1be22f6695d"
DATA = "c7ad97ec55d4e5c83848589c777c973cdee15bf5"


def write(path, text):
    with path.open("x") as handle:
        handle.write(text)


def main(out):
    out.mkdir()
    read = lambda name: json.loads((HERE / "data" / name).read_text())
    summary = read("summary.json")
    support, draws = read("sampler-support.json"), read("draw-multiplicities.json")
    groups, weights = read("within-input-groups.json"), read("weighting-views.json")
    trajectories = list(csv.DictReader((HERE / "data/within-input-trajectories.csv").open()))
    shapes = [r["shape"] for r in support]
    plt.rcParams.update({"font.size":10, "svg.hashsalt":"snfs-sampler-variation-20261018"})
    fig, ax = plt.subplots(figsize=(8,3.6))
    colors = ["#326ba8", "#c88027", "#429276"]
    for offset, seed in enumerate((1,2,3)):
        ys = [next(r["distinct_g"] for r in draws if r["shape"] == shape and r["seed"] == seed) for shape in shapes]
        xs = [i+(offset-1)*.25 for i in range(4)]
        ax.bar(xs, ys, .23, color=colors[offset], label=f"seed {seed}")
        for x,y in zip(xs,ys):
            ax.text(x,y+.3,str(y),ha="center",fontsize=9)
    ax.axhline(20,color="#555555",ls="--",lw=1,label="20 accepted draws per seed/shape")
    ax.set(xticks=range(4),xticklabels=shapes,ylim=(0,23),ylabel="Distinct coefficient vectors observed",
           title="Same accepted draw count; different observed support occupancy")
    ax.legend(ncol=2,loc="lower right",fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "support-occupancy.svg")
    plt.close(fig)

    fig, axes = plt.subplots(2,2,figsize=(8,5),sharex=True,sharey=True)
    for ax, group in zip(axes.flat, groups):
        for seed, marker, style, color in ((1,"o","-",colors[0]),(3,"x","--",colors[1])):
            rows = [r for r in trajectories if r["input_id"] == group["input_id"] and int(r["seed"]) == seed]
            ax.plot([int(r["work"]) for r in rows],[int(r["distinct_residues"]) for r in rows],
                    marker=marker,ms=6,ls=style,lw=1.3,color=color,label=f"seed {seed}")
        ax.set(xscale="log",ylim=(-1,23),title=f"p={group['p']}; A={group['A']}, B={group['B']}")
        ax.grid(alpha=.2)
    for ax in axes[:,0]:
        ax.set_ylabel("Distinct residues D(W)")
    for ax in axes[-1,:]:
        ax.set_xlabel("Recorded candidate-work rung W (log axis)")
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc="lower center",ncol=2)
    fig.tight_layout(rect=(0,.06,1,1))
    fig.savefig(out / "within-input-trajectories.svg")
    plt.close(fig)

    fig,ax=plt.subplots(figsize=(8,3.7))
    dweights=[r for r in weights if r["metric"] == "final_distinct_residues"]
    for offset,(field,label) in enumerate((("row_weighted_mean","saved rows"),
                                          ("seed_input_grouped_mean","seed/input groups"),
                                          ("input_grouped_mean","algebraic inputs"))):
        xs=[i+(offset-1)*.25 for i in range(4)]
        ax.bar(xs,[r[field] for r in dweights],.23,label=label,color=colors[offset])
    ax.set(xticks=range(4),xticklabels=shapes,ylabel="Mean final distinct residues D(100,000)",
           title="Three descriptive weighting definitions on the same archived rows")
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(out / "weighting-views.svg")
    plt.close(fig)
    for svg in out.glob("*.svg"):
        svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines())+"\n")

    table1="\n".join(f"| {r['shape']} | {r['coefficient_patterns']} | {r['observed_distinct_g']} | {r['admissible_support_count'] if r['admissible_support_count'] is not None else 'not computed'} |" for r in support)
    table2="\n".join(f"| {r['shape']} | {r['row_weighted_mean']:.6f} | {r['seed_input_grouped_mean']:.6f} | {r['input_grouped_mean']:.6f} | {r['rows']}/{r['seed_inputs']}/{r['inputs']} |" for r in dweights)
    gamma_rows=[r for r in weights if r["metric"] == "gamma"]
    gamma_table="\n".join(f"| {r['shape']} | {r['row_values_present']}/{r['rows']} | {r['seed_input_values_present']}/{r['seed_inputs']} | {r['input_values_present']}/{r['inputs']} |" for r in gamma_rows)
    pages=[
        ("Sampler support and accepted-draw multiplicity", "support-occupancy.svg", [
            "2026-10-18: descriptive reanalysis of saved data and an exact finite coefficient/prime reference. No fresh field/curve point search ran. Interpretation stays with the owner.",
            "Source EXP-ECDLP-4c6a09 / RUN-ECDLP-e89532 has 1,395 rows, grouped into 279 contiguous five-curve field blocks. Its random-g arm has 240 accepted field draws and 1,200 curve rows: 20 draws for each shape/seed, across seeds 1, 2 and 3. Rejected attempts and the raw RNG draw stream were not saved.",
            "Coefficient support: 2^(w-1) times binomial(d-1,w-2), before filters. Enumerating the coefficient vectors gives 8, 24, 560 and 2,640 patterns for degrees 3, 7, 8 and 12. Their observed unions across seeds contain 5, 10, 55 and 60 polynomials. Higher-degree admissible support is not classified here.",
            "Exact cubic reference: all eight monic weight-three cubics have no rational root (the only candidates are +1 and -1), hence are irreducible over Q. Exhaustive trial division of all 72 values at k=4..12 leaves five polynomials with an eligible prime >=2^12. Every one occurs in each archived seed, and every recorded cubic prime/k matches that polynomial's first eligible value. The independent modular irreducibility-screen outcomes are not enumerated; observed acceptance establishes acceptance of these five.",
            "For cubic seeds 1, 2, 3, accepted-draw multiplicities are respectively [1,2,5,5,7], [2,3,4,4,7] and [1,2,3,4,10] after sorting. Seven-degree unique counts are 10,10,7; degree eight 20,19,20; degree twelve 20,20,20. These are accepted-draw occupancies, not uniformity tests or estimates of rejected-draw probabilities.",
            "Native status remains invalid_output, attributed by the receipt to the legacy manifest format. Producer and built-in checker codes are both zero. All original rows, statuses and weighting remain unchanged. Sources and exact hashes are in observation.yaml and data/summary.json."
        ]),
        ("Within-input variation across two saved seeds", "within-input-trajectories.svg", [
            "Four exact algebraic inputs occur under both saved seeds 1 and 3. Identity is (g,p,reduction root,A,B), not number-field isomorphism. Pick the first saved row per input/seed for plotting, while retaining every repeated row index. There are eight representative attempts and 48 recorded rung rows.",
            "The two g are [-1,0,1,1] at p=33791 and [1,1,0,1] at p=32801, both with reduction root 32. Each occurs with (A,B)=(-17,9) and (-7,11). Auxiliary-prime lists match within each input; torsion bounds also match (2 for the first displayed input and 1 for the others). These are incidental overlaps, not a deliberately balanced replication panel.",
            "What is worth inspecting: at W=3,000, the (-17,9) curve has D=6 versus 4 for p=33791, and D=14 versus 10 for p=32801. At W=100,000 the paired counts match at 10 and 20. The other two inputs match at every saved rung, ending at 2 and 0. No claim of equal full point sets follows from equal residue counts.",
            "All four paired inputs have identical saved sample-point lists. Those lists are capped at eight points: identical prefixes do not establish identical trajectories or full search outputs. Two actual trajectories differ despite identical saved sample lists and equal final counts.",
            "The source seeds coefficient-shell enumeration with the search seed and degree. Curves/fields are generated upstream using the same top-level seed. Thus changing a CLI seed generally changes inputs as well as search order; the four incidental overlaps allow only this small conditional comparison. No population-level variance or confidence interval is estimated.",
            "Source RUN-ECDLP-e89532; selectors and every raw row index are in data/within-input-groups.json and data/within-input-trajectories.csv. Straight segments connect recorded rungs; no interpolation model or unrecorded measurements are asserted."
        ]),
        ("Row weighting and input weighting", "weighting-views.svg", [
            "Three views retain the same archived random-g rows: mean over rows; mean over seed/input groups after averaging repeats within a group; and mean over algebraic inputs after equal weighting of their observed seeds. They answer different descriptive questions. None replaces the original estimator.",
            "Mean D(100,000), row / seed-input / input: degree 3 = 7.140000 / 7.391892 / 7.357143; degree 7 = 1.383333 / 1.455224 / 1.455224; degree 8 = 0.883333 / 0.891525 / 0.891525; degree 12 = 0.416667 / 0.416667 / 0.416667. Group counts respectively are 300/74/70, 300/134/134, 300/295/295 and 300/300/300.",
            "Gamma summaries and all missing-value counts remain in data/weighting-views.json. Defined row counts are 217/300, 129/300, 93/300 and 40/300. Defined input counts are 54/70, 62/134, 93/295 and 40/300. Missing gamma is not zero and is not silently included in a mean. No uncertainty interval is supplied for these descriptive weighting comparisons.",
            "Checks: mechanical replay by this authoring session checks 72 cubic evaluations by a separate divisor scan, four supports by ternary enumeration, twelve draw strata, 48 trajectory rows and eight weighting rows. This is not independent scientific review. Analysis took approximately 0.11 wall seconds on Python 3.12.14; the exact observed timings/host are in data/summary.json, not performance comparisons.",
            "Next proposed check: prepare a fixed-input interface with field, curve, auxiliary configuration and search seed recorded separately; use unique inputs with fresh per-input seed strings and persist more than capped sample prefixes. Keep original coupled-seed data alongside the future panel. The current launcher has no fixed-input CLI, and no such new replicas ran in this session.",
            "Canonical graphs, hypothesis/goal statuses, existing frozen protocols and run outputs are unchanged. No scientific verdict is issued. Source EXP-ECDLP-4c6a09 / RUN-ECDLP-e89532; native invalid_output and separate zero process codes are retained."
        ])]
    md="# Sampler support and within-input variation — 2026-10-18\n\n"
    for title,svg,paragraphs in pages:
        md+="## "+title+"\n\n"+"\n\n".join(paragraphs)+"\n\n!["+title+"]("+svg+")\n\n"
        if svg=="support-occupancy.svg":
            md+="| Shape | Pre-filter coefficient support | Observed union | Exact admissible support |\n| --- | ---: | ---: | ---: |\n"+table1+"\n\n"
        if svg=="weighting-views.svg":
            md+="| Shape | Row mean D | Seed/input mean D | Input mean D | Rows/seed-inputs/inputs |\n| --- | ---: | ---: | ---: | --- |\n"+table2+"\n\n"
            md+="| Shape | Defined gamma rows | Defined seed/input gamma | Defined input gamma |\n| --- | ---: | ---: | ---: |\n"+gamma_table+"\n\n"
    write(out/"REPORT.md",md)
    source='#set page(paper:"a4",margin:17mm)\n#set text(size:9.5pt)\n'
    for i,(title,svg,paragraphs) in enumerate(pages):
        if i: source+='\n#pagebreak()\n'
        source+='\n= '+title+'\n\n'
        for j,p in enumerate(paragraphs):
            source+='#text('+json.dumps(p)+')\n\n'
            if j==0: source+='#image('+json.dumps(svg)+',width:100%)\n\n'
    write(out/"report.typ",source)
    typst.compile(str(out/"report.typ"),output=str(out/"report.pdf"),root=str(out))
    pdf=pymupdf.open(out/"report.pdf")
    for i,page in enumerate(pdf):
        page.get_pixmap(matrix=pymupdf.Matrix(1.25,1.25)).save(f"/tmp/snfs-sampler-page-{i+1}.png")
    make_yaml(out,support,draws,groups,weights,summary)
    print(json.dumps({"pages":len(pdf),"pdf":str(out/"report.pdf")}))


def make_yaml(out,support,draws,groups,weights,summary):
    ev=lambda artifact,selector:{"artifact":artifact,"selector":selector}
    descriptions=[
        ("support","Coefficient support and observed polynomial union",support,"coefficient vectors",4,"shape strata","Exact coefficient counts; only cubic admissible support is fully classified.","support-data"),
        ("draws","Accepted draws and distinct g by shape/seed",[{k:r[k] for k in ("shape","seed","accepted_draws","distinct_g")} for r in draws],"accepted field draws",240,"accepted random-g field draws","Rejected draws are unavailable; these are occupancy counts, not a uniformity test.","draw-data"),
        ("trajectories","Exact inputs observed under two saved seeds",groups,"matched algebraic input",4,"incidental cross-seed input groups","Only four incidental overlaps, each with seeds 1 and 3; no population variance estimate.","group-data"),
        ("weights","Three weighting views including missing-gamma denominators",weights,"descriptive mean of recorded metrics",1200,"random-g saved curve rows","Group counts and defined-value denominators differ; no confidence interval is estimated.","weight-data")]
    observations=[]
    for ident,description,value,unit,n,sample_unit,uncertainty,artifact in descriptions:
        observations.append(dict(id=ident,description=description,kind="derived",value=value,unit=unit,
                                 sample=dict(n=n,unit=sample_unit,dependence="Repeated draws, shared seeds and reused curve generator keys; counts are not independent field/curve replicates."),
                                 uncertainty=uncertainty,evidence=[ev(artifact,"whole file"),ev("raw","/cells"),ev("analysis","main() and associated arithmetic functions")]))
    observations.append(dict(id="process-codes",description="Literal native process codes",kind="measured",
                             value=dict(returncode=summary["producer_returncode"],check_returncode=summary["checker_returncode"]),
                             unit="exit code",sample=None,uncertainty="Process codes are separate from native status.",evidence=[ev("receipt","/returncode and /check_returncode")]))
    missing=[dict(field=f"/observations/0/value/{i}/admissible_support_count",reason="Higher-degree admissible support was not classified.") for i in (1,2,3)]
    missing.append(dict(field="/observations/4/sample",reason="Not applicable: literal process receipt fields."))
    # Undefined derived means are allowed only with explicit missing reasons.
    for i,row in enumerate(weights):
        for k,v in row.items():
            if v is None: missing.append(dict(field=f"/observations/3/value/{i}/{k}",reason="No defined metric values in this group."))
    artifacts=[]
    paths=[("raw",summary["sources"][0]["path"],CODE),("receipt",summary["sources"][1]["path"],CODE),
           ("producer",summary["sources"][2]["path"],CODE),("search",summary["sources"][3]["path"],CODE),
           ("rng",summary["sources"][4]["path"],CODE),
           ("analysis",str(HERE.relative_to(ROOT)/"analyze.py"),CODE)]
    for ident,name in (("support-data","sampler-support.json"),("draw-data","draw-multiplicities.json"),
                       ("group-data","within-input-groups.json"),("weight-data","weighting-views.json"),
                       ("catalog","cubic-catalog.json"),("trajectories-data","within-input-trajectories.csv")):
        paths.append((ident,str(HERE.relative_to(ROOT)/"data"/name),DATA))
    for ident,path,commit in paths:
        artifacts.append(dict(id=ident,path=path,commit=commit,sha256=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()))
    record=dict(schema="crypto.autoresearch.experiment_observation.v1",report_kind="reanalysis",
                question="Which polynomial inputs can the sampler reach, how often are they reused, and what varies within an identical input?",
                scope="Archived G3 rows and exact bounded coefficient/cubic-prime arithmetic; no new point search or independent scientific review.",
                method=dict(description="Group saved rows, enumerate coefficient support and evaluate all eight cubic patterns at k=4..12 by trial division. Seeds below are archived source seeds, not fresh replicas.",
                            command="python3 research/snfs_sampler_variation_20261018/analyze.py --out research/snfs_sampler_variation_20261018/data",
                            parameters=dict(kmin=4,kmax=12,minimum_prime=4096,source_work_ladder=[300,1000,3000,10000,30000,100000]),
                            seeds=[1,2,3],sampling_unit="Accepted field draws, curve rows and incidental fixed-input seed pairs; kept distinct.",
                            stopping_rule="All 1,395 saved rows; four coefficient supports; 72 cubic evaluations; no new random samples."),
                runs=[dict(experiment_id="EXP-ECDLP-4c6a09",run_id="RUN-ECDLP-e89532",native_status=summary["native_status"],evidence=[ev("receipt","/status and /detail")])],
                observations=observations,
                controls=[dict(id="cubic-reference",description="Exact cubic rational-root/prime reference",observation_ids=["support"],matching="Same coefficient constraints, k range and minimum prime as source; every eligible cubic is also accepted in saved rows.",limitations=["The source modular irreducibility test is not replayed; higher degrees have only pre-filter counts here."]),
                          dict(id="paired-inputs",description="Seeds 1 and 3 at an identical algebraic input",observation_ids=["trajectories"],matching="Same g,p,root,A,B, auxiliary-prime list and torsion bound within each group.",limitations=["Incidental overlaps; two seeds each; sample-point lists capped at eight; final counts do not identify full point sets."])],
                patterns=[dict(id="cubic-occupancy",kind="exploratory_pattern",description="Each 20-draw cubic stratum revisits exactly the five admissible coefficient patterns.",observation_ids=["draws"],reference_ids=["cubic-reference"],uncertainty="Descriptive finite support and three saved strata, without a sampler uniformity test.",alternative_explanations=["The small admissible support and replacement sampling explain why repeated fields can occur; rejected draws were not recorded."]),
                          dict(id="trajectory-prefix",kind="exploratory_pattern",description="Two paired trajectories differ at W=3,000 despite equal final counts and identical capped sample lists.",observation_ids=["trajectories"],reference_ids=["paired-inputs"],uncertainty="Four matched inputs and two seeds each; no estimate beyond these saved paths.",alternative_explanations=["Seed-dependent enumeration order can change intermediate discoveries even when later counts agree.","The eight-point reporting cap can hide later differences in the saved sample lists."])],
                limitations=["Original run status and row weighting are preserved.","Row grouping uses literal coefficients, not field-isomorphism classes.","No fresh fixed-input replicas ran: the current CLI couples generation and search seeds.","No scientific interpretation, relevance or usefulness verdict is recorded."],
                missing=missing,
                next_checks=[dict(question="What changes under fresh search seeds when all algebraic inputs are fixed?",method="Prepare a versioned fixed-input replay interface; freeze separate input and search-seed records and retain full per-rung traces.",control="Same explicit inputs and work ladder; compare coupled and per-input seed schedules without overwriting old outputs.",status="proposed")],artifacts=artifacts)
    write(out/"observation.yaml",yaml.safe_dump(record,sort_keys=False,width=96))


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    main(args.out)
